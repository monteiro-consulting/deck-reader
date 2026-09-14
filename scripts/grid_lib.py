#!/usr/bin/env python3
"""Shared helpers: load a grid by stage, apply the business-model block, load the benchmarks.

Standard library only.

    load_grid(path_or_stage)      -> dict. "preseed" / "seed" / "series_a" / "series_b" /
                                     "series_c" (and the spellings in STAGES) resolve to
                                     scripts/grids/<stage>.json.
    stage_key(stage)              -> "preseed" | "seed" | "series_a" | "series_b" | "series_c",
                                     from any accepted spelling or from a grid's "stage" field.
                                     Series C covers every later round: "series D", "growth
                                     round" and the profiler's "series-c-or-later" route to it.
    model_key(profile)            -> the model whose block applies. The profile's model_type when
                                     a file scripts/grids/models/<model>.json exists, else "saas".
    load_model(model)             -> the model block (dict) or None.
    effective_grid(grid, profile) -> a copy of the stage grid with the model block applied, in
                                     this order: remove, reweight, add, documents. Every script
                                     that walks the questions, or the required documents, must
                                     use this, so that a marketplace deck is scored on the
                                     marketplace questions and gated on the marketplace documents.
    load_benchmarks(model, stage) -> the benchmarks to display for that model and stage: the
                                     model's own list, plus the stage-generic entries of saas.json
                                     (marked all_models) when the model is not saas. Never scored.
    all_questions(grid)           -> [(block, question), ...] in grid order.

A model block (scripts/grids/models/<model>.json) has, per stage, four verbs, applied in order:
    remove    ["C4", ...]                       question ids of the stage grid taken out
    reweight  {"blocks": {"B": 0}, "questions": {"B2": 1}}
                                                new weight for a block, or for one question
    add       [{"block": "B", "questions": [...]},
               {"block": {"id": "Q", "name": {...}, "weight": 2}, "questions": [...]}]
                                                questions appended to an existing block (they
                                                take its weight), or to a block the model brings
    documents {"remove": ["crm_pipeline"], "add": [{"id": ..., "name": {...},
               "requirement": {...}, "min_months": 12, "min_count": null}]}
                                                required documents of the stage's first gate
                                                (grid["annex_gate"]["required_documents"]) taken
                                                out by id, or appended with the same shape as the
                                                grid entries. Only for a stage whose grid carries
                                                a document list (series A, series B, series C);
                                                an error otherwise.
The stage grid is never edited on disk; the pre-seed grid has no model section and is untouched.
The document list is the same for every deck of one stage and one model: the model block
adjusts it, the deck never does.
"""
import copy
import json
import os
import re

GRIDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grids")
MODELS_DIR = os.path.join(GRIDS_DIR, "models")
BENCHMARKS_DIR = os.path.join(GRIDS_DIR, "benchmarks")
DEFAULT_MODEL = "saas"

STAGES = {
    "pre-seed": "preseed", "preseed": "preseed", "pre seed": "preseed",
    "seed": "seed",
    "series a": "series_a", "series-a": "series_a", "series_a": "series_a", "seriesa": "series_a",
    "série a": "series_a", "serie a": "series_a", "série-a": "series_a", "serie-a": "series_a",
    "series b": "series_b", "series-b": "series_b", "series_b": "series_b", "seriesb": "series_b",
    "série b": "series_b", "serie b": "series_b", "série-b": "series_b", "serie-b": "series_b",
    # Series C covers the series C and every later round: D, E, F, growth rounds.
    "series c": "series_c", "series-c": "series_c", "series_c": "series_c", "seriesc": "series_c",
    "série c": "series_c", "serie c": "series_c", "série-c": "series_c", "serie-c": "series_c",
    "series-c-or-later": "series_c",
    "series d": "series_c", "series-d": "series_c", "série d": "series_c", "serie d": "series_c",
    "series e": "series_c", "series-e": "series_c", "série e": "series_c", "serie e": "series_c",
    "series f": "series_c", "series-f": "series_c", "série f": "series_c", "serie f": "series_c",
    "growth round": "series_c", "growth-round": "series_c", "growth": "series_c",
}


class GridError(Exception):
    pass


def _norm(s):
    s = str(s or "").strip().lower()
    return re.sub(r"\s+", " ", s)


def stage_key(stage):
    """Accept a stage spelling ("Series A", "série A", "seed") or a grid dict."""
    if isinstance(stage, dict):
        stage = stage.get("stage", "")
    key = STAGES.get(_norm(stage))
    if key is None:
        raise GridError(f"no grid for stage {stage!r}; known: {sorted(set(STAGES.values()))}")
    return key


def grid_path(stage_or_path):
    if os.path.isfile(str(stage_or_path)):
        return stage_or_path
    try:
        key = stage_key(stage_or_path)
    except GridError as e:
        raise SystemExit(str(e))
    return os.path.join(GRIDS_DIR, f"{key}.json")


def load_grid(stage_or_path):
    with open(grid_path(stage_or_path), encoding="utf-8") as f:
        return json.load(f)


def known_models():
    if not os.path.isdir(MODELS_DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(MODELS_DIR) if f.endswith(".json"))


def model_key(profile=None):
    m = _norm((profile or {}).get("model_type", ""))
    return m if m and m in known_models() else DEFAULT_MODEL


def load_model(model):
    path = os.path.join(MODELS_DIR, f"{model}.json")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_benchmarks(model, stage):
    """The benchmarks of one model at one stage, plus the stage-generic ones of saas.json."""
    skey = stage_key(stage)
    out = []
    seen = set()

    def take(name, generic_only):
        path = os.path.join(BENCHMARKS_DIR, f"{name}.json")
        if not os.path.isfile(path):
            return
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        for b in (doc.get("stages") or {}).get(skey) or []:
            if generic_only and not b.get("all_models"):
                continue
            if b.get("id") in seen:
                continue
            seen.add(b.get("id"))
            out.append(dict(b, model=name))

    take(model, False)
    if model != DEFAULT_MODEL:
        take(DEFAULT_MODEL, True)
    return out


def _find_block(grid, block_id):
    for b in grid["blocks"]:
        if b["id"] == block_id:
            return b
    return None


def _question_index(grid):
    return {q["id"]: (b, q) for b in grid["blocks"] for q in b["questions"]}


def _required_documents(grid):
    """The document list of the first gate, or None when the stage grid has none."""
    gate = grid.get("annex_gate")
    if not isinstance(gate, dict) or "required_documents" not in gate:
        return None
    return gate["required_documents"]


def _apply_documents(g, ops, model):
    """The documents verb: remove required documents by id, add entries with the grid shape."""
    docs = _required_documents(g)
    removed, added = [], []
    if not ops:
        return {"removed": removed, "added": added}
    if docs is None:
        raise GridError(f"model {model!r}: a documents verb for stage {g['stage']!r}, whose grid has no required_documents")
    for did in ops.get("remove") or []:
        if did not in {d["id"] for d in docs}:
            raise GridError(f"model {model!r}: cannot remove document {did!r}, not in the {g['stage']} list")
        docs[:] = [d for d in docs if d["id"] != did]
        removed.append(did)
    for entry in ops.get("add") or []:
        for key in ("id", "name", "requirement"):
            if key not in entry:
                raise GridError(f"model {model!r}: added document without {key!r}")
        if entry["id"] in {d["id"] for d in docs}:
            raise GridError(f"model {model!r}: document id {entry['id']!r} already exists in the {g['stage']} list")
        doc = {"id": entry["id"], "name": entry["name"], "requirement": entry["requirement"], "min_months": entry.get("min_months")}
        if entry.get("min_count") is not None:
            doc["min_count"] = entry["min_count"]
        docs.append(copy.deepcopy(doc))
        added.append(entry["id"])
    return {"removed": removed, "added": added}


def apply_model_block(grid, ops, model=""):
    """Apply one stage section of a model block to a copy of the grid: remove, reweight, add, documents."""
    g = copy.deepcopy(grid)
    ops = ops or {}
    removed, reweighted, added = [], {"blocks": {}, "questions": {}}, []

    # 1. remove
    for qid in ops.get("remove") or []:
        idx = _question_index(g)
        if qid not in idx:
            raise GridError(f"model {model!r}: cannot remove {qid!r}, not in the {g['stage']} grid")
        block, _ = idx[qid]
        block["questions"] = [q for q in block["questions"] if q["id"] != qid]
        removed.append(qid)

    # 2. reweight
    rw = ops.get("reweight") or {}
    for bid, weight in (rw.get("blocks") or {}).items():
        block = _find_block(g, bid)
        if block is None:
            raise GridError(f"model {model!r}: cannot reweight block {bid!r}, not in the {g['stage']} grid")
        block["weight"] = weight
        reweighted["blocks"][bid] = weight
    idx = _question_index(g)
    for qid, weight in (rw.get("questions") or {}).items():
        if qid not in idx:
            raise GridError(f"model {model!r}: cannot reweight {qid!r}, not in the {g['stage']} grid")
        idx[qid][1]["weight"] = weight
        reweighted["questions"][qid] = weight

    # 3. add
    for entry in ops.get("add") or []:
        spec = entry.get("block")
        if isinstance(spec, dict):
            if _find_block(g, spec["id"]) is not None:
                raise GridError(f"model {model!r}: block {spec['id']!r} already exists in the {g['stage']} grid")
            block = {"id": spec["id"], "name": spec["name"], "weight": spec["weight"], "questions": [], "from_model": model}
            g["blocks"].append(block)
        else:
            block = _find_block(g, spec)
            if block is None:
                raise GridError(f"model {model!r}: cannot add to block {spec!r}, not in the {g['stage']} grid")
        existing = {q["id"] for _, q in all_questions(g)}
        for q in entry.get("questions") or []:
            if q["id"] in existing:
                raise GridError(f"model {model!r}: question id {q['id']!r} already exists")
            block["questions"].append(copy.deepcopy(q))
            existing.add(q["id"])
            added.append(q["id"])

    # 4. documents (the first gate's list, only where the stage grid has one)
    documents = _apply_documents(g, ops.get("documents"), model)

    g["model_block"] = {"model": model, "removed": removed, "reweighted": reweighted, "added": added, "documents": documents}
    return g


def effective_grid(grid, profile=None):
    model = model_key(profile)
    block = load_model(model) or {}
    try:
        skey = stage_key(grid)
    except GridError:
        skey = ""
    ops = (block.get("stages") or {}).get(skey) or {}
    g = apply_model_block(grid, ops, model)
    mb = g["model_block"]
    changed = bool(mb["removed"] or mb["added"] or mb["reweighted"]["blocks"] or mb["reweighted"]["questions"]
                   or mb["documents"]["removed"] or mb["documents"]["added"])
    g["applied_model"] = model
    g["applied_model_questions"] = model if changed else ""
    return g


def all_questions(grid):
    return [(b, q) for b in grid["blocks"] for q in b["questions"]]


def required_documents(grid):
    """The required documents of a grid's first gate, [] when the stage has none.

    Pass an effective grid (effective_grid) to get the list of the stage and the model."""
    return list(_required_documents(grid) or [])

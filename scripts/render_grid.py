#!/usr/bin/env python3
"""Write the effective grid of one stage and one business model as a single markdown document.

Standard library only. Nothing is scored, nothing is judged: this is the grid an investor reads
in one piece, "the SaaS series A grid", with the model block already applied (questions and,
where the stage has a first gate, the required document list) and the benchmarks listed with
their sources.

Usage:
    render_grid.py <stage> <model> [--lang en|fr] [--out grid.md]

    render_grid.py series_a saas
    render_grid.py series_b biotech --lang fr
    render_grid.py seed marketplace --lang fr --out seed-marketplace.fr.md

<stage> accepts preseed, seed, series_a, series_b, series_c (and the spellings grid_lib knows:
"series A", "série B", "series D", "growth round").
<model> is one of the files in scripts/grids/models/ (saas, marketplace, consumer, ecommerce,
hardware, fintech, biotech); an unknown model falls back to saas, as the profiler does.
"""
import argparse
import sys

from grid_lib import (GridError, apply_model_block, known_models, load_benchmarks, load_grid,
                      load_model, required_documents, stage_key)

T = {
    "en": {
        "title": "Grid: {stage}, {model}",
        "intro": "One grid per stage, one block per business model. This document is the stage grid with the model block applied, as the scripts use it. Completeness is computed by code from the weights below; benchmarks are displayed next to the figures and never scored.",
        "stage": "Stage", "model": "Model", "grid_version": "Grid version", "model_version": "Model block version",
        "model_block": "What the model block does to the stage grid",
        "removed": "Removed questions", "reweighted_blocks": "Reweighted blocks", "reweighted_questions": "Reweighted questions", "added": "Added questions",
        "documents_removed": "Removed documents", "documents_added": "Added documents",
        "documents": "Required documents (first gate)",
        "documents_note": "The list of the stage and the model block: every document below must be present and cover the minimum, or the reading stops with the request email. The model block adjusts the list; the deck never does.",
        "document_id": "Id", "document_name": "Document", "requirement": "Requirement", "minimum": "Minimum",
        "min_months": "{n} months", "min_count": "{n} items",
        "none": "none", "principle": "Model principle", "sources": "Model sources",
        "blocks": "Blocks and questions", "weight": "weight", "from_model": "block brought by the model",
        "question": "Question", "found_if": "Found if", "note": "Note", "proof": "proof", "claim_types": "claim types",
        "computation": "The computation", "block": "Block", "share": "Approximate share of the score",
        "computation_note": "Per question: 0, 1 or 2 points times the block weight (or the question's own weight). Per block: points over the maximum. Global: mean of the blocks weighted by their weight. A block of weight 0 is for information only. A question with weight 0 in B2C is marked as such.",
        "b2c": "weight {w} in B2C", "own_weight": "own weight {w}", "info_only": "for information, weight 0",
        "benchmarks": "Benchmarks, shown next to the figures, never scored",
        "benchmarks_note": "Each benchmark has a value, a source and a date. An empty value means no dated source was found; it is left empty rather than invented.",
        "metric": "Metric", "value": "Value", "source": "Source", "date": "Date", "no_value": "(no dated source)",
        "no_benchmarks": "No benchmark file for this model and stage.",
    },
    "fr": {
        "title": "Grille : {stage}, {model}",
        "intro": "Une grille par stade, un bloc par modèle économique. Ce document est la grille du stade avec le bloc de modèle appliqué, telle que les scripts l'utilisent. La complétude est calculée par le code depuis les poids ci-dessous ; les repères sont affichés à côté des chiffres et jamais notés.",
        "stage": "Stade", "model": "Modèle", "grid_version": "Version de la grille", "model_version": "Version du bloc de modèle",
        "model_block": "Ce que le bloc de modèle fait à la grille du stade",
        "removed": "Questions retirées", "reweighted_blocks": "Blocs repondérés", "reweighted_questions": "Questions repondérées", "added": "Questions ajoutées",
        "documents_removed": "Documents retirés", "documents_added": "Documents ajoutés",
        "documents": "Documents requis (première porte)",
        "documents_note": "La liste du stade et du bloc de modèle : chaque document ci-dessous doit être présent et couvrir le minimum, sinon la lecture s'arrête avec l'email de demande. Le bloc de modèle ajuste la liste ; le deck ne le fait jamais.",
        "document_id": "Id", "document_name": "Document", "requirement": "Exigence", "minimum": "Minimum",
        "min_months": "{n} mois", "min_count": "{n} éléments",
        "none": "aucune", "principle": "Principe du modèle", "sources": "Sources du modèle",
        "blocks": "Blocs et questions", "weight": "poids", "from_model": "bloc apporté par le modèle",
        "question": "Question", "found_if": "Trouvée si", "note": "Note", "proof": "preuve", "claim_types": "types d'affirmation",
        "computation": "Le calcul", "block": "Bloc", "share": "Part approximative du score",
        "computation_note": "Par question : 0, 1 ou 2 points multipliés par le poids du bloc (ou le poids propre à la question). Par bloc : points sur le maximum. Global : moyenne des blocs pondérée par leur poids. Un bloc à poids 0 est posé pour information. Une question à poids 0 en B2C est marquée comme telle.",
        "b2c": "poids {w} en B2C", "own_weight": "poids propre {w}", "info_only": "pour information, poids 0",
        "benchmarks": "Repères, affichés à côté des chiffres, jamais notés",
        "benchmarks_note": "Chaque repère a une valeur, une source et une date. Une valeur vide signifie qu'aucune source datée n'a été trouvée ; elle reste vide plutôt qu'inventée.",
        "metric": "Repère", "value": "Valeur", "source": "Source", "date": "Date", "no_value": "(pas de source datée)",
        "no_benchmarks": "Pas de fichier de repères pour ce modèle et ce stade.",
    },
}

STAGE_NAMES = {"preseed": {"en": "pre-seed", "fr": "pre-seed"}, "seed": {"en": "seed", "fr": "seed"},
               "series_a": {"en": "series A", "fr": "série A"}, "series_b": {"en": "series B", "fr": "série B"},
               "series_c": {"en": "series C", "fr": "série C"}}


def pick(d, lang):
    if isinstance(d, dict):
        return d.get(lang) or d.get("en") or next(iter(d.values()), "")
    return d or ""


def cell(x):
    return str(x or "").replace("|", "\\|").replace("\n", " ").strip()


def render(stage, model, lang="en"):
    t = T.get(lang, T["en"])
    skey = stage_key(stage)
    grid = load_grid(skey)
    if model not in known_models():
        model = "saas"
    block = load_model(model) or {}
    ops = (block.get("stages") or {}).get(skey) or {}
    g = apply_model_block(grid, ops, model)
    mb = g["model_block"]
    stage_name = STAGE_NAMES[skey][lang if lang in ("en", "fr") else "en"]
    model_name = pick(block.get("name"), lang) or model

    lines = [f"# {t['title'].format(stage=stage_name, model=model_name)}", "", t["intro"], ""]
    lines.append(f"**{t['stage']}**: {stage_name} · **{t['model']}**: {model_name} · **{t['grid_version']}**: {grid['version']} · **{t['model_version']}**: {block.get('version', '—')}")
    lines.append("")
    if block.get("principle"):
        lines += [f"## {t['principle']}", "", pick(block["principle"], lang), ""]
    lines += [f"## {t['model_block']}", ""]
    lines.append(f"- **{t['removed']}**: {', '.join(mb['removed']) or t['none']}")
    rb = mb["reweighted"]["blocks"]
    rq = mb["reweighted"]["questions"]
    lines.append(f"- **{t['reweighted_blocks']}**: {', '.join(f'{k} → {v}' for k, v in rb.items()) or t['none']}")
    lines.append(f"- **{t['reweighted_questions']}**: {', '.join(f'{k} → {v}' for k, v in rq.items()) or t['none']}")
    lines.append(f"- **{t['added']}**: {', '.join(mb['added']) or t['none']}")
    documents = required_documents(g)
    if documents or mb["documents"]["removed"] or mb["documents"]["added"]:
        lines.append(f"- **{t['documents_removed']}**: {', '.join(mb['documents']['removed']) or t['none']}")
        lines.append(f"- **{t['documents_added']}**: {', '.join(mb['documents']['added']) or t['none']}")
    lines.append("")
    if block.get("sources"):
        lines += [f"## {t['sources']}", ""]
        for s in block["sources"]:
            lines.append(f"- [{cell(s.get('title'))}]({s.get('url')}) · {s.get('date') or '—'}")
        lines.append("")

    if documents:
        lines += [f"## {t['documents']}", "", t["documents_note"], "",
                  f"| {t['document_id']} | {t['document_name']} | {t['requirement']} | {t['minimum']} |", "|---|---|---|---|"]
        for d in documents:
            minimum = []
            if d.get("min_months"):
                minimum.append(t["min_months"].format(n=d["min_months"]))
            if d.get("min_count"):
                minimum.append(t["min_count"].format(n=d["min_count"]))
            lines.append(f"| {d['id']} | {cell(pick(d.get('name'), lang))} | {cell(pick(d.get('requirement'), lang))} | {', '.join(minimum) or '—'} |")
        lines.append("")

    lines += [f"## {t['blocks']}", ""]
    for b in g["blocks"]:
        title = f"### {b['id']}. {pick(b['name'], lang)}, {t['weight']} {b['weight']}"
        if b["weight"] == 0:
            title += f" ({t['info_only']})"
        if b.get("from_model"):
            title += f" ({t['from_model']})"
        lines += [title, "", f"| # | {t['question']} | {t['found_if']} | {t['note']} |", "|---|---|---|---|"]
        for q in b["questions"]:
            notes = []
            if q.get("requires_proof"):
                notes.append(f"*{t['proof']}*")
            if q.get("note"):
                notes.append(cell(q["note"]))
            if "weight" in q:
                notes.append(t["own_weight"].format(w=q["weight"]))
            if "weight_if_b2c" in q:
                notes.append(t["b2c"].format(w=q["weight_if_b2c"]))
            if q.get("claim_types"):
                notes.append(f"{t['claim_types']}: {', '.join(q['claim_types'])}")
            lines.append(f"| {q['id']} | {cell(pick(q['question'], lang))} | {cell(q.get('found_if'))} | {' · '.join(notes)} |")
        lines.append("")

    lines += [f"## {t['computation']}", "", t["computation_note"], "", f"| {t['block']} | {t['weight']} | {t['share']} |", "|---|---|---|"]
    total = sum(b["weight"] for b in g["blocks"])
    for b in g["blocks"]:
        share = f"{round(100.0 * b['weight'] / total)} %" if total and b["weight"] else "—"
        lines.append(f"| {b['id']}. {pick(b['name'], lang)} | {b['weight']} | {share} |")
    lines.append("")

    benchmarks = load_benchmarks(model, skey)
    lines += [f"## {t['benchmarks']}", "", t["benchmarks_note"], ""]
    if not benchmarks:
        lines += [t["no_benchmarks"], ""]
    else:
        lines += [f"| # | {t['metric']} | {t['value']} | {t['source']} | {t['date']} |", "|---|---|---|---|---|"]
        for bm in benchmarks:
            src = cell(bm.get("source")) or "—"
            if bm.get("url"):
                src = f"[{src}]({bm['url']})"
            value = cell(bm.get("value")) or t["no_value"]
            if bm.get("note"):
                value += f" {cell(bm['note'])}"
            lines.append(f"| {', '.join(bm.get('question_ids') or [])} | {cell(pick(bm.get('metric'), lang))} | {value} | {src} | {bm.get('date') or '—'} |")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage")
    ap.add_argument("model")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    try:
        text = render(args.stage, args.model, args.lang)
    except GridError as e:
        print(f"render_grid.py: {e}", file=sys.stderr)
        return 2
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(args.out)
    else:
        sys.stdout.buffer.write(text.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Consolidate one or more independent checker passes into the final answers.

Standard library only. No model is involved.

Usage:
    consolidate.py --pass DIR1 [--pass DIR2 --pass DIR3] --out FINAL_DIR

Each pass directory holds block-A.json ... block-F.json as written by the checkers and
finalised by verify_quotes.py. The output directory receives the same six files.

Rule, per question
    value    = median of the pass values on the scale absent < partial < found.
               Three passes: the majority when there is one (1,2,2 -> 2; 1,1,2 -> 1),
               the middle value otherwise (0,1,2 -> 1). One pass: that pass.
               Two passes that disagree: the stricter one.
    stable   = all passes gave the same value.
    passes   = the list of pass values, in order, kept for the report.
    evidence, missing, call_question = taken from the first pass whose value equals the
               consolidated value, so the quote shown always supports the value shown.
    quote_invalid = true when the chosen pass had its quote rejected (its value is absent).
    claim_ids, capped, downgraded, downgraded_by = carried over from the chosen pass (seed).
"""
import argparse
import glob
import json
import os
import sys

ORDER = {"absent": 0, "partial": 1, "found": 2}
NAMES = {v: k for k, v in ORDER.items()}


class ConsolidateError(Exception):
    pass


def median_value(values):
    if not values:
        raise ConsolidateError("no values")
    ranks = sorted(ORDER[v] for v in values)
    n = len(ranks)
    if n % 2 == 1:
        return NAMES[ranks[n // 2]]
    # Even count: the stricter of the two middle values (lower rank).
    return NAMES[ranks[n // 2 - 1]]


def consolidate_answers(passes):
    """passes: list (one per pass) of lists of answer dicts. Returns the consolidated list."""
    by_pass = []
    for i, answers in enumerate(passes, start=1):
        m = {}
        for a in answers:
            if a.get("value") not in ORDER:
                raise ConsolidateError(f"pass {i}: unknown value {a.get('value')!r} for {a.get('question_id')}")
            m[a["question_id"]] = a
        by_pass.append(m)
    ids = list(by_pass[0].keys())
    for i, m in enumerate(by_pass[1:], start=2):
        if set(m) != set(ids):
            raise ConsolidateError(f"pass {i} does not answer the same questions as pass 1")

    merged = []
    for qid in ids:
        values = [m[qid]["value"] for m in by_pass]
        value = median_value(values)
        source = next(m[qid] for m in by_pass if m[qid]["value"] == value)
        out = {
            "question_id": qid,
            "value": value,
            "evidence": [] if value == "absent" else list(source.get("evidence") or []),
            "missing": source.get("missing", ""),
            "call_question": source.get("call_question", ""),
            "passes": values,
            "stable": len(set(values)) == 1,
        }
        if source.get("quote_invalid"):
            out["quote_invalid"] = True
        # Seed markers set by apply_proof_cap.py travel with the chosen pass.
        for key in ("claim_ids", "capped", "downgraded", "downgraded_by"):
            if key in source:
                out[key] = source[key]
        merged.append(out)
    return merged


def _load_dir(path):
    blocks = {}
    for p in sorted(glob.glob(os.path.join(path, "block-?.json"))):
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        blocks[data["block"]] = data.get("answers", [])
    if not blocks:
        raise ConsolidateError(f"no block-?.json in {path}")
    return blocks


def run(pass_dirs, out_dir):
    loaded = [_load_dir(d) for d in pass_dirs]
    block_ids = sorted(loaded[0])
    os.makedirs(out_dir, exist_ok=True)
    unstable = []
    for b in block_ids:
        merged = consolidate_answers([lp.get(b, []) for lp in loaded])
        unstable.extend(a["question_id"] for a in merged if not a["stable"])
        with open(os.path.join(out_dir, f"block-{b}.json"), "w", encoding="utf-8") as f:
            json.dump({"block": b, "passes": len(pass_dirs), "answers": merged}, f, ensure_ascii=False, indent=2)
    summary = {"passes": len(pass_dirs), "unstable": unstable, "out": out_dir}
    with open(os.path.join(out_dir, "consolidation.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pass", dest="passes", action="append", required=True, help="a pass directory; repeat")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    try:
        summary = run(args.passes, args.out)
    except ConsolidateError as e:
        print(f"consolidate.py: {e}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

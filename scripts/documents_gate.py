#!/usr/bin/env python3
"""The stop decisions a model must never take, for every stage whose grid carries a required
document list (series A, series B and series C). Standard library only. --grid takes series_a,
series_b or series_c.

Usage:
    documents_gate.py required  --grid series_a [--profile profile.json] --out required.json
    documents_gate.py documents --grid series_a [--profile profile.json] --annexes annexes.json
                                --classification annex-types.json --out gate.json [--invalid invalid.json]
    documents_gate.py contradictions --grid series_a --claims claims.final.json --review review.json
                                     --out gate.json --out-claims claims.reviewed.json

required   writes the document list (id, name, requirement, min_months, min_count) for the
           annex-classifier agent, which sees the list and never the gate rule.

documents  (grid["annex_gate"]["required_documents"], model block applied)
    The list is the one of the stage and of the business model: the stage grid carries the
    base list, the model block adjusts it with its documents verb (grid_lib.effective_grid), the
    deck never does. Without --profile the default model (saas) applies, as everywhere else.
    The annex-classifier agent says, for each readable annex, which required document it is,
    with a verbatim quote from the annex and the months it covers. This script checks the quote
    against the annex text (a classification with a quote that is not there is ignored), then
    walks the required list:
        stop_missing_documents   at least one document is absent, or covers fewer months than
                                 min_months, or fewer items than min_count. The gate lists them
                                 for the founder email, document by document.
        continue                 every document is there.
    No coverage threshold: the list is the gate. What the annexes do not cover after matching is
    listed in the report, and never stops the reading.

contradictions
    Same rule as seed (seed_gate.contradictions_gate): every blatant claim went to the reviewer;
    with an honest explanation it becomes to_probe, without one the reading stops.
"""
import argparse
import json
import sys

from claims_lib import load_json, save_json
from grid_lib import effective_grid, load_grid, required_documents
from seed_gate import contradictions_gate
from verify_quotes import quote_on_page


def _annex_text(annexes_doc):
    return {a["id"]: [p.get("text", "") for p in a.get("pages", [])] for a in annexes_doc.get("annexes", []) if a.get("kind") != "unsupported"}


def documents_gate(annexes_doc, classification_doc, grid):
    """Walk the required documents of `grid` (pass the effective grid for the model's list)."""
    required = required_documents(grid)
    texts = _annex_text(annexes_doc)
    invalid = []
    by_type = {}
    for item in (classification_doc or {}).get("annexes", []):
        aid, dtype = item.get("annex_id"), item.get("type")
        reason = None
        if aid not in texts:
            reason = "unknown_or_unreadable_annex"
        elif dtype not in {d["id"] for d in required}:
            reason = "unknown_document_type" if dtype != "other" else None
        elif not item.get("quote") or not any(quote_on_page(item["quote"], t) for t in texts[aid]):
            reason = "quote_not_in_annex"
        if reason:
            invalid.append({"annex_id": aid, "type": dtype, "reason": reason})
            continue
        if dtype == "other":
            continue
        by_type.setdefault(dtype, []).append(item)

    present, missing = [], []
    for d in required:
        items = by_type.get(d["id"], [])
        if not items:
            missing.append({"document": d["id"], "name": d["name"], "requirement": d["requirement"], "reason": "absent"})
            continue
        months = max((int(i.get("months_covered") or 0) for i in items), default=0)
        count = sum(int(i.get("items_covered") or 1) for i in items)
        if d.get("min_months") and months < int(d["min_months"]):
            missing.append({"document": d["id"], "name": d["name"], "requirement": d["requirement"],
                            "reason": f"covers {months} month(s), {d['min_months']} required", "annex_ids": [i["annex_id"] for i in items]})
            continue
        if d.get("min_count") and count < int(d["min_count"]):
            missing.append({"document": d["id"], "name": d["name"], "requirement": d["requirement"],
                            "reason": f"{count} item(s), {d['min_count']} required", "annex_ids": [i["annex_id"] for i in items]})
            continue
        present.append({"document": d["id"], "annex_ids": [i["annex_id"] for i in items], "months_covered": months})

    return {
        "gate": "documents",
        "decision": "stop_missing_documents" if missing else "continue",
        "readable_annexes": len(texts),
        "model": grid.get("applied_model") or grid.get("model_block", {}).get("model") or "",
        "required": [d["id"] for d in required],
        "present": present,
        "to_request": missing,
    }, invalid


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("gate", choices=["required", "documents", "contradictions"])
    ap.add_argument("--grid", required=True)
    ap.add_argument("--profile", default=None, help="profile.json; picks the model block whose documents verb adjusts the list (default: saas)")
    ap.add_argument("--annexes", default=None)
    ap.add_argument("--classification", default=None)
    ap.add_argument("--claims", default=None)
    ap.add_argument("--review", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--out-claims", default=None)
    ap.add_argument("--invalid", default=None)
    args = ap.parse_args(argv)
    profile = load_json(args.profile) if args.profile else {}
    grid = effective_grid(load_grid(args.grid), profile)
    if args.gate == "required":
        required = required_documents(grid)
        save_json(args.out, {"stage": grid["stage"], "model": grid["applied_model"], "required": required})
        print(json.dumps({"out": args.out, "model": grid["applied_model"], "required": [d["id"] for d in required]}))
        return 0
    if args.gate == "documents":
        if not args.annexes:
            print("documents_gate.py: --annexes is required for the documents gate", file=sys.stderr)
            return 2
        classification = load_json(args.classification) if args.classification else {"annexes": []}
        result, invalid = documents_gate(load_json(args.annexes), classification, grid)
        if args.invalid:
            save_json(args.invalid, invalid)
        result["invalid_classifications"] = len(invalid)
    else:
        if not args.claims:
            print("documents_gate.py: --claims is required for the contradictions gate", file=sys.stderr)
            return 2
        claims_doc = load_json(args.claims)
        review_doc = load_json(args.review) if args.review else {"reviews": []}
        result, claims_doc = contradictions_gate(claims_doc, review_doc)
        if args.out_claims:
            save_json(args.out_claims, claims_doc)
    save_json(args.out, result)
    summary = {k: v for k, v in result.items() if k not in ("to_request", "present")}
    summary["to_request"] = [m["document"] for m in result.get("to_request", [])] if args.gate == "documents" else len(result.get("to_request", []))
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

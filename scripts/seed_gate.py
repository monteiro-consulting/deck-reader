#!/usr/bin/env python3
"""The two decisions of the seed reading that a model must never take. Standard library only.

Usage:
    seed_gate.py annexes --grid seed --claims claims.annex.json --annexes annexes.json --out gate.json
    seed_gate.py contradictions --grid seed --claims claims.final.json --review review.json
                                --out gate.json --out-claims claims.reviewed.json

annexes  (grid["annex_gate"])
    stop_no_annexes      no readable annex was given. Generic email, no web, no grid.
    stop_insufficient    among the key claim types the deck makes (revenue, customers,
                         retention), fewer than min_key_coverage are covered by at least one
                         proven claim. Precise email, no web, no grid.
    continue             enough is covered. What is still not covered is listed for the email.
    A deck that makes no key claim at all continues: there is nothing to prove, the grid will
    show the absences.

contradictions (grid["gaps"])
    Every blatant claim went to the reviewer, whose only job was to find an honest explanation
    (a different date, a different definition, a stale source, a namesake). With an explanation
    the claim is lowered to to_probe and becomes a question for the call. Without one, with
    the sources on both sides, the reading stops: stop_contradiction. The stop erases nothing.
"""
import argparse
import json
import sys

from claims_lib import load_json, save_json
from grid_lib import load_grid


def annex_gate(claims_doc, annexes_doc, grid):
    rule = grid.get("annex_gate") or {}
    key_types = list(rule.get("key_claim_types") or [])
    min_cov = float(rule.get("min_key_coverage", 0.5))
    claims = claims_doc.get("claims", [])
    readable = int(annexes_doc.get("readable_count", 0))
    to_request = [c for c in claims if c.get("check") in ("annex", "both") and c.get("annex_status") == "not_covered"]
    present = sorted({c["type"] for c in claims if c.get("type") in key_types})
    covered = sorted({c["type"] for c in claims if c.get("type") in key_types and c.get("annex_status") == "proven"})
    coverage = (len(covered) / len(present)) if present else None
    if readable == 0:
        decision = "stop_no_annexes"
    elif present and coverage < min_cov:
        decision = "stop_insufficient"
    else:
        decision = "continue"
    return {
        "gate": "annexes",
        "decision": decision,
        "readable_annexes": readable,
        "key_types_present": present,
        "key_types_covered": covered,
        "key_coverage": None if coverage is None else round(coverage, 2),
        "min_key_coverage": min_cov,
        "to_request": [{"id": c["id"], "page": c["page"], "statement": c.get("statement", ""), "proof": c.get("proof", ""), "type": c.get("type")} for c in to_request],
    }


def contradictions_gate(claims_doc, review_doc):
    reviews = {r.get("claim_id"): r for r in (review_doc or {}).get("reviews", [])}
    stopping, explained = [], []
    for c in claims_doc.get("claims", []):
        if c.get("status") != "blatant":
            continue
        r = reviews.get(c["id"]) or {}
        c["review"] = {"explanation_found": bool(r.get("explanation_found")), "explanation": r.get("explanation", ""), "sources": list(r.get("sources") or [])}
        if c["review"]["explanation_found"] and c["review"]["explanation"].strip():
            c["status"] = "to_probe"
            c["lowered_by_review"] = True
            explained.append(c["id"])
        else:
            stopping.append(c["id"])
    claims_doc["blatant_ids"] = stopping
    return {
        "gate": "contradictions",
        "decision": "stop_contradiction" if stopping else "continue",
        "stopping": stopping,
        "lowered_to_probe": explained,
    }, claims_doc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("gate", choices=["annexes", "contradictions"])
    ap.add_argument("--grid", required=True)
    ap.add_argument("--claims", required=True)
    ap.add_argument("--annexes", default=None)
    ap.add_argument("--review", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--out-claims", default=None)
    args = ap.parse_args(argv)
    grid = load_grid(args.grid)
    claims_doc = load_json(args.claims)
    if args.gate == "annexes":
        if not args.annexes:
            print("seed_gate.py: --annexes is required for the annexes gate", file=sys.stderr)
            return 2
        result = annex_gate(claims_doc, load_json(args.annexes), grid)
    else:
        review_doc = load_json(args.review) if args.review else {"reviews": []}
        result, claims_doc = contradictions_gate(claims_doc, review_doc)
        if args.out_claims:
            save_json(args.out_claims, claims_doc)
    save_json(args.out, result)
    summary = {k: v for k, v in result.items() if k != "to_request"}
    summary["to_request"] = len(result.get("to_request", []))
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

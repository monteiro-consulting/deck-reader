#!/usr/bin/env python3
"""Validate the claims extracted from a seed deck and attach their check mode. Standard library only.

Usage:
    check_claims.py --grid seed --claims claims.json --pages pages.json --out claims.verified.json
                    [--invalid invalid.json] [--finalize]

Each claim must have a unique id, a page that exists, and a quote that appears verbatim on
that page (same matching rule as verify_quotes.py). Its type must be one of grid["claim_types"];
an unknown type becomes "other". The script adds:
    check   annex / web / both / none, from the grid
    proof   the document that would back it, from the grid (used for the founder email)

Invalid claims are listed in --invalid and the exit code is 1, unless --finalize, in which
case they are simply dropped from the output. Nobody rewrites a claim by hand.
"""
import argparse
import json
import sys

from claims_lib import claim_check_mode, claim_proof_text, load_json, save_json, to_number
from grid_lib import load_grid
from verify_quotes import quote_on_page

MAX_QUOTE = 300


def check(claims_doc, pages_doc, grid):
    page_text = {int(p["number"]): p.get("text", "") for p in pages_doc.get("pages", [])}
    known_types = set((grid.get("claim_types") or {}).keys())
    valid, invalid, seen = [], [], set()
    for c in claims_doc.get("claims", []):
        cid = c.get("id")
        reason = None
        try:
            page = int(c.get("page"))
        except (TypeError, ValueError):
            page = None
        quote = (c.get("quote") or "").strip()
        if not cid or cid in seen:
            reason = "missing_or_duplicate_id"
        elif page not in page_text:
            reason = "page_out_of_range"
        elif not quote:
            reason = "no_quote"
        elif len(quote) > MAX_QUOTE:
            reason = "quote_too_long"
        elif not quote_on_page(quote, page_text[page]):
            reason = "quote_not_on_page"
        elif not (c.get("statement") or "").strip():
            reason = "no_statement"
        if reason:
            invalid.append({"id": cid, "reason": reason, "page": c.get("page"), "quote": quote})
            continue
        seen.add(cid)
        out = dict(c)
        out["page"] = page
        out["quote"] = quote
        if out.get("type") not in known_types:
            out["type"] = "other"
        out["value"] = to_number(out.get("value"))
        out["check"] = claim_check_mode(out, grid)
        out["proof"] = claim_proof_text(out, grid)
        valid.append(out)
    return valid, invalid


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", required=True)
    ap.add_argument("--claims", required=True)
    ap.add_argument("--pages", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--invalid", default=None)
    ap.add_argument("--finalize", action="store_true")
    args = ap.parse_args(argv)
    grid = load_grid(args.grid)
    valid, invalid = check(load_json(args.claims), load_json(args.pages), grid)
    save_json(args.out, {"stage": grid["stage"], "claim_count": len(valid), "claims": valid})
    if args.invalid:
        save_json(args.invalid, invalid)
    by_check = {}
    for c in valid:
        by_check[c["check"]] = by_check.get(c["check"], 0) + 1
    print(json.dumps({"valid": len(valid), "invalid": len(invalid), "by_check": by_check,
                      "invalid_ids": [i["id"] for i in invalid]}, ensure_ascii=False))
    if invalid and not args.finalize:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

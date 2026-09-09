#!/usr/bin/env python3
"""Verify the annex matcher's output and classify each annex-checked claim. Standard library only.

Usage:
    verify_matches.py --grid seed --claims claims.verified.json --matches matches.json
                      --annexes annexes.json --out claims.annex.json [--invalid invalid.json] [--finalize]

The matcher gives, per claim, a status (proven / contradicted / not_covered), quotes from the
annexes, and the figure it found there. This script:
    - rejects a match whose quote is not on the cited annex page (same rule as verify_quotes.py);
    - for numeric claims, recomputes the gap between the deck figure and the annex figure with
      the thresholds in grid["gaps"] and sets the status from that, whatever the matcher said:
          minor    -> proven (gap noted)
          to_probe -> to_probe
          blatant  -> blatant
    - a "contradicted" without figures on both sides is blatant (a fact that is not there);
    - a claim with no match, or an invalid match after --finalize, is not_covered.

Output: the claims file with annex_status, annex_evidence, annex_value, gap_class, gap_ratio.
Invalid matches are listed in --invalid; exit 1 unless --finalize.
"""
import argparse
import json
import sys

from claims_lib import classify_gap, load_json, save_json, to_number
from grid_lib import load_grid
from verify_quotes import quote_on_page

MATCHER_STATUSES = {"proven", "contradicted", "not_covered"}
MAX_EVIDENCE = 3


def _annex_pages(annexes_doc):
    out = {}
    for a in annexes_doc.get("annexes", []):
        out[a["id"]] = {int(p["number"]): p.get("text", "") for p in a.get("pages", [])}
    return out


def verify(claims_doc, matches_doc, annexes_doc, grid):
    pages = _annex_pages(annexes_doc)
    by_claim = {}
    invalid = []
    for m in matches_doc.get("matches", []):
        cid = m.get("claim_id")
        status = m.get("status")
        evidence = m.get("evidence") or []
        reason = None
        if status not in MATCHER_STATUSES:
            reason = "unknown_status"
        elif status == "not_covered" and evidence:
            reason = "not_covered_with_evidence"
        elif status != "not_covered" and not evidence:
            reason = "no_evidence"
        elif len(evidence) > MAX_EVIDENCE:
            reason = "too_many_evidence_items"
        else:
            for ev in evidence:
                aid = ev.get("annex_id")
                try:
                    page = int(ev.get("page"))
                except (TypeError, ValueError):
                    reason = "page_missing"
                    break
                if aid not in pages or page not in pages[aid]:
                    reason = "annex_page_out_of_range"
                    break
                if not quote_on_page(ev.get("quote", ""), pages[aid][page]):
                    reason = "quote_not_in_annex"
                    break
        if reason:
            invalid.append({"claim_id": cid, "reason": reason, "evidence": evidence})
            continue
        by_claim[cid] = m

    claims = []
    for c in claims_doc.get("claims", []):
        out = dict(c)
        if c.get("check") not in ("annex", "both"):
            claims.append(out)
            continue
        m = by_claim.get(c["id"])
        if m is None:
            out["annex_status"] = "not_covered"
            out["annex_evidence"] = []
            if any(i["claim_id"] == c["id"] for i in invalid):
                out["annex_match_invalid"] = True
            claims.append(out)
            continue
        status = m["status"]
        found_value = to_number(m.get("found_value"))
        out["annex_evidence"] = list(m.get("evidence") or [])
        out["annex_value"] = found_value
        out["annex_note"] = m.get("note", "")
        gap_class, ratio = classify_gap(c.get("value"), found_value, grid)
        out["gap_class"] = gap_class
        out["gap_ratio"] = ratio
        if status == "not_covered":
            out["annex_status"] = "not_covered"
        elif gap_class == "minor":
            out["annex_status"] = "proven"
        elif gap_class in ("to_probe", "blatant"):
            out["annex_status"] = gap_class
        elif status == "proven":
            out["annex_status"] = "proven"
        else:  # contradicted without two figures: the fact is not there
            out["annex_status"] = "blatant"
        claims.append(out)
    return claims, invalid


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", required=True)
    ap.add_argument("--claims", required=True)
    ap.add_argument("--matches", required=True)
    ap.add_argument("--annexes", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--invalid", default=None)
    ap.add_argument("--finalize", action="store_true")
    args = ap.parse_args(argv)
    grid = load_grid(args.grid)
    claims_doc = load_json(args.claims)
    claims, invalid = verify(claims_doc, load_json(args.matches), load_json(args.annexes), grid)
    claims_doc["claims"] = claims
    save_json(args.out, claims_doc)
    if args.invalid:
        save_json(args.invalid, invalid)
    counts = {}
    for c in claims:
        s = c.get("annex_status")
        if s:
            counts[s] = counts.get(s, 0) + 1
    print(json.dumps({"annex_status": counts, "invalid": len(invalid), "invalid_ids": [i["claim_id"] for i in invalid]}, ensure_ascii=False))
    if invalid and not args.finalize:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Enforce the web verification rules and compute each claim's final status. Standard library only.

Usage:
    verify_web.py --grid seed --claims claims.annex.json --web web.json --out claims.final.json
    verify_web.py --grid seed --claims claims.annex.json --out claims.final.json   (no web step run)

The web verifier gives, per web-checked claim: status (confirmed / contradicted / unverifiable),
the searches it ran, sources for and against (url, title, quote), and the figure it found.
This script does not trust the status. It applies grid["web"]:
    - confirmed needs at least min_independent_sources sources FOR on distinct domains;
    - contradicted needs at least that many AGAINST on distinct domains;
    - anything short of that is unverifiable, which is a valid state;
    - numeric claims are re-classified by the gap thresholds (grid["gaps"]):
          minor -> confirmed, to_probe -> to_probe, blatant -> blatant;
    - a non-numeric contradiction that meets the source rule is blatant.

Then, per claim, status = the worst of annex_status and web_status (claims_lib.worst):
proven / confirmed < not_covered / unverifiable < to_probe < blatant. Claims with check
"none" get status "not_checked". The output also lists the blatant claims for the reviewer.
"""
import argparse
import json
import sys

from claims_lib import classify_gap, distinct_domains, load_json, save_json, to_number, worst
from grid_lib import load_grid

WEB_STATUSES = {"confirmed", "contradicted", "unverifiable"}


def apply_web(claims, web_doc, grid):
    rule = grid.get("web") or {}
    need = int(rule.get("min_independent_sources", 2))
    results = {r.get("claim_id"): r for r in (web_doc or {}).get("results", [])}
    out = []
    for c in claims:
        item = dict(c)
        if c.get("check") in ("web", "both"):
            r = results.get(c["id"])
            if r is None:
                item["web_status"] = "unverifiable"
                item["web_for"], item["web_against"], item["web_searches"] = [], [], []
                item["web_note"] = "no web result"
            else:
                status = r.get("status") if r.get("status") in WEB_STATUSES else "unverifiable"
                for_src = list(r.get("for") or [])
                against = list(r.get("against") or [])
                n_for = len(distinct_domains(for_src))
                n_against = len(distinct_domains(against))
                found_value = to_number(r.get("found_value"))
                gap_class, ratio = classify_gap(c.get("value"), found_value, grid)
                item["web_for"], item["web_against"] = for_src, against
                item["web_searches"] = list(r.get("searches") or [])
                item["web_value"] = found_value
                item["web_note"] = r.get("note", "")
                item["web_domains_for"], item["web_domains_against"] = n_for, n_against
                if gap_class is not None and (n_for >= need or n_against >= need):
                    item["gap_class"], item["gap_ratio"] = gap_class, ratio
                    web_status = "confirmed" if gap_class == "minor" else gap_class
                elif status == "confirmed" and n_for >= need:
                    web_status = "confirmed"
                elif status == "contradicted" and n_against >= need:
                    web_status = "blatant"
                else:
                    web_status = "unverifiable"
                    if status != "unverifiable":
                        item["web_note"] = (item["web_note"] + " " if item["web_note"] else "") + \
                            f"downgraded to unverifiable: {status} needs {need} independent domains (for={n_for}, against={n_against})"
                item["web_status"] = web_status
        out.append(item)
    return out


def finalize(claims):
    for c in claims:
        if c.get("check") == "none":
            c["status"] = "not_checked"
        else:
            c["status"] = worst(c.get("annex_status"), c.get("web_status")) or "not_covered"
    return claims


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", required=True)
    ap.add_argument("--claims", required=True)
    ap.add_argument("--web", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    grid = load_grid(args.grid)
    doc = load_json(args.claims)
    web_doc = load_json(args.web) if args.web else None
    claims = apply_web(doc.get("claims", []), web_doc, grid)
    claims = finalize(claims)
    doc["claims"] = claims
    doc["blatant_ids"] = [c["id"] for c in claims if c.get("status") == "blatant"]
    save_json(args.out, doc)
    counts = {}
    for c in claims:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    print(json.dumps({"status": counts, "blatant_ids": doc["blatant_ids"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Write the list of claim types of a grid, with a one-line meaning each, for the claim extractor.

Usage:
    claim_types.py --grid seed --out types.json

The extractor sees the type names and meanings only, never the check mode or the proof text.
"""
import argparse
import json
import sys

from grid_lib import load_grid

MEANING = {
    "revenue": "revenue, MRR, ARR, GMV, margin, or any money the company earned",
    "customers": "number of paying customers, accounts, seats, or first payment dates",
    "retention": "retention, cohorts, recurring usage, repeat rate, engagement over time",
    "churn": "customers lost, churn rate, reasons for leaving",
    "acquisition": "acquisition channels, cost per customer, conversion, sales cycle length",
    "pricing": "the price actually paid by customers",
    "runway": "monthly burn, cash, months of runway",
    "cap_table": "equity split, full-time status of founders, ownership",
    "named_customer": "a customer, pilot or partner named in the deck",
    "competitor": "a named competitor, or the statement that there is none",
    "founder": "a founder's or hire's past role, employer, achievement, degree",
    "funding": "a past round, grant, investor name or amount",
    "why_now": "a regulation, event or technology shift, with its date",
    "market": "a market size figure and its basis",
    "other": "a checkable fact that fits none of the above",
}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    grid = load_grid(args.grid)
    types = [{"type": t, "meaning": MEANING.get(t, "")} for t in (grid.get("claim_types") or {})]
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"stage": grid["stage"], "types": types}, f, ensure_ascii=False, indent=2)
    print(f"{args.out}: {len(types)} type(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Write the questions of ONE grid block to a file, so a block checker sees only its block.

Usage:
    grid_block.py --grid GRID --block A --out block-A.questions.json [--only A2,A4] [--profile profile.json]

--grid    a stage name (preseed, seed) or a path to a grid JSON.
--profile adds the model-specific questions (e.g. marketplace) to their block.
--only    restricts the file to the listed question ids (used for retries after a quote rejection).
The block weight and the B2C rule are deliberately left out: the checker does not score.
For questions marked requires_proof, the checker is told so and which claim types apply.
"""
import argparse
import json
import sys

from grid_lib import effective_grid, load_grid


def block_questions(grid, block_id, only=None):
    for block in grid["blocks"]:
        if block["id"] == block_id:
            questions = []
            for q in block["questions"]:
                if only and q["id"] not in only:
                    continue
                item = {
                    "id": q["id"],
                    "question": q["question"]["en"],
                    "found_if": q["found_if"],
                    "note": q.get("note", ""),
                }
                if q.get("requires_proof"):
                    item["requires_proof"] = True
                if q.get("claim_types"):
                    item["claim_types"] = list(q["claim_types"])
                questions.append(item)
            return {"block": block_id, "block_name": block["name"]["en"], "stage": grid["stage"], "questions": questions}
    raise SystemExit(f"unknown block {block_id}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", required=True, help="stage name or path")
    ap.add_argument("--block", required=True)
    ap.add_argument("--profile", default=None)
    ap.add_argument("--only", default=None, help="comma-separated question ids")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    grid = load_grid(args.grid)
    profile = None
    if args.profile:
        with open(args.profile, encoding="utf-8") as f:
            profile = json.load(f)
    grid = effective_grid(grid, profile)
    only = set(x.strip() for x in args.only.split(",")) if args.only else None
    data = block_questions(grid, args.block.upper(), only)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{args.out}: {len(data['questions'])} question(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Write the questions of ONE grid block to a file, so a block checker sees only its block.

Usage:
    grid_block.py --block A --out block-A.questions.json [--only A2,A4] [--grid grid.json]

--only restricts the file to the listed question ids (used for retries after a quote rejection).
The block weight and the B2C rule are deliberately left out: the checker does not score.
"""
import argparse
import json
import os
import sys


def block_questions(grid, block_id, only=None):
    for block in grid["blocks"]:
        if block["id"] == block_id:
            questions = []
            for q in block["questions"]:
                if only and q["id"] not in only:
                    continue
                questions.append({
                    "id": q["id"],
                    "question": q["question"]["en"],
                    "found_if": q["found_if"],
                    "note": q.get("note", ""),
                })
            return {"block": block_id, "block_name": block["name"]["en"], "questions": questions}
    raise SystemExit(f"unknown block {block_id}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "grid.json"))
    ap.add_argument("--block", required=True)
    ap.add_argument("--only", default=None, help="comma-separated question ids")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    with open(args.grid, encoding="utf-8") as f:
        grid = json.load(f)
    only = set(x.strip() for x in args.only.split(",")) if args.only else None
    data = block_questions(grid, args.block.upper(), only)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{args.out}: {len(data['questions'])} question(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

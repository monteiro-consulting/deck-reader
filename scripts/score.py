#!/usr/bin/env python3
"""Compute deck completeness from the 24 validated answers and the grid weights.

Standard library only. No model sees or computes this score.

Usage:
    score.py --grid grid.json --answers-dir DIR --profile profile.json --out score.json

Rules (fixed with the grid, see grid.md "The computation"):
    per question   points = value(0/1/2) x weight (block weight, or the question's own weight)
    per block      percent = points / max, max = sum of 2 x weight over counted questions
    global         mean of block percents weighted by block weight
    C3 (weight 0)  not counted
    F3             not_assessable and not counted when F1 or F2 is not "found"
    B3             weight 1 instead of the block weight when the profile says B2C
    red block      percent strictly below the grid threshold (50)
    call questions absent or partial questions in blocks of weight 3

"Score" always means "deck completeness", never the quality of the company.
"""
import argparse
import glob
import json
import os
import sys


class ScoreError(Exception):
    pass


def _round(x):
    return round(x + 1e-9, 2)


def compute(grid, answers, profile):
    scale = grid["scale"]
    by_id = {}
    for a in answers:
        qid = a.get("question_id")
        if qid in by_id:
            raise ScoreError(f"duplicate answer for {qid}")
        by_id[qid] = a

    is_b2c = str(profile.get("customer_type", "")).upper() == "B2C"
    threshold = grid.get("red_block_threshold_percent", 50)
    call_weight = grid.get("call_question_block_weight", 3)

    questions_out = []
    blocks_out = []
    red_flags = []
    call_question_ids = []

    for block in grid["blocks"]:
        block_points = 0
        block_max = 0
        for q in block["questions"]:
            qid = q["id"]
            if qid not in by_id:
                raise ScoreError(f"missing answer for {qid}")
            ans = by_id[qid]
            value = ans.get("value")
            if value not in scale:
                raise ScoreError(f"unknown value {value!r} for {qid}")

            weight = q.get("weight", block["weight"])
            if is_b2c and "weight_if_b2c" in q:
                weight = q["weight_if_b2c"]

            status = "counted"
            counted = weight > 0
            if not counted:
                status = "information_only"
            for dep in q.get("requires_found", []):
                if by_id.get(dep, {}).get("value") != "found":
                    status = "not_assessable"
                    counted = False
                    break

            points = scale[value] * weight if counted else 0
            q_max = 2 * weight if counted else 0
            block_points += points
            block_max += q_max

            if q.get("red_flag_if_absent") and value == "absent":
                red_flags.append(qid)
            if block["weight"] >= call_weight and value in ("partial", "absent") and status != "not_assessable":
                call_question_ids.append(qid)

            questions_out.append({
                "question_id": qid,
                "block": block["id"],
                "value": value,
                "weight": weight,
                "points": points,
                "max": q_max,
                "counted": counted,
                "status": status,
                "quote_invalid": bool(ans.get("quote_invalid", False)),
            })

        percent = _round(100.0 * block_points / block_max) if block_max else 0.0
        blocks_out.append({
            "id": block["id"],
            "name": block["name"],
            "weight": block["weight"],
            "points": block_points,
            "max": block_max,
            "percent": percent,
            "red": percent < threshold,
        })

    total_weight = sum(b["weight"] for b in blocks_out)
    global_percent = _round(sum(b["percent"] * b["weight"] for b in blocks_out) / total_weight) if total_weight else 0.0

    passes = max((len(a.get("passes") or [1]) for a in answers), default=1)
    unstable = [a["question_id"] for a in answers if a.get("passes") and not a.get("stable", True)]
    conf = grid.get("confirmation") or {}
    lo = conf.get("trigger_min_percent")
    hi = conf.get("trigger_max_percent")
    confirmation_due = passes == 1 and bool(conf) and (lo is None or global_percent >= lo) and (hi is None or global_percent <= hi)

    return {
        "passes": passes,
        "unstable": unstable,
        "confirmation_due": confirmation_due,
        "extra_passes": conf.get("extra_passes", 0),
        "meaning": "deck completeness, not company quality",
        "stage": grid["stage"],
        "grid_version": grid["version"],
        "customer_type": profile.get("customer_type"),
        "global_percent": global_percent,
        "blocks": blocks_out,
        "questions": questions_out,
        "red_blocks": [b["id"] for b in blocks_out if b["red"]],
        "red_flags": red_flags,
        "call_question_ids": call_question_ids,
    }


def load_answers(answers_dir):
    answers = []
    for path in sorted(glob.glob(os.path.join(answers_dir, "block-*.json"))):
        with open(path, encoding="utf-8") as f:
            answers.extend(json.load(f).get("answers", []))
    return answers


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "grid.json"))
    ap.add_argument("--answers-dir", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    with open(args.grid, encoding="utf-8") as f:
        grid = json.load(f)
    with open(args.profile, encoding="utf-8") as f:
        profile = json.load(f)
    answers = load_answers(args.answers_dir)
    try:
        result = compute(grid, answers, profile)
    except ScoreError as e:
        print(f"score.py: {e}", file=sys.stderr)
        return 2
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps({"global_percent": result["global_percent"],
                      "blocks": {b["id"]: b["percent"] for b in result["blocks"]},
                      "red_blocks": result["red_blocks"],
                      "passes": result["passes"],
                      "unstable": result["unstable"],
                      "confirmation_due": result["confirmation_due"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

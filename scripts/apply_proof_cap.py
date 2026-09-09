#!/usr/bin/env python3
"""Apply the seed proof rule to one checker pass. Standard library only.

Usage:
    apply_proof_cap.py --grid seed --profile profile.json --answers-dir PASS_DIR --claims claims.final.json

Rules (grid["proof"]):
    - A question marked requires_proof whose value is "found" keeps it only if the answer
      cites, in claim_ids, at least one claim whose status is proven or confirmed. Otherwise the
      value becomes grid["proof"]["cap_value"] (partial) and the answer is marked capped.
    - An answer citing a claim whose status is to_probe is lowered by one step
      (found -> partial, partial -> absent) and marked downgraded, with the claim id. One gap,
      one step: the cap is not applied on top of the lowering.
    - Blatant claims never reach this script: the reading stopped before.
The block files are rewritten in place. Nobody edits a value by hand.
"""
import argparse
import glob
import json
import os
import sys

from claims_lib import OK_STATUSES, load_json, save_json
from grid_lib import all_questions, effective_grid, load_grid

STEP_DOWN = {"found": "partial", "partial": "absent", "absent": "absent"}


def apply(answers, questions_by_id, claims_by_id, grid):
    cap_value = (grid.get("proof") or {}).get("cap_value", "partial")
    changed = []
    for a in answers:
        q = questions_by_id.get(a.get("question_id"))
        if q is None:
            continue
        ids = [i for i in (a.get("claim_ids") or []) if i in claims_by_id]
        a["claim_ids"] = ids
        statuses = [claims_by_id[i].get("status") for i in ids]
        probes = [i for i in ids if claims_by_id[i].get("status") == "to_probe"]
        if probes and a.get("value") != "absent":
            # One gap, one step down. The cap is not applied on top of it.
            a["value"] = STEP_DOWN[a["value"]]
            a["downgraded"] = True
            a["downgraded_by"] = probes
            changed.append((a["question_id"], "downgraded"))
        elif q.get("requires_proof") and a.get("value") == "found" and not any(s in OK_STATUSES for s in statuses):
            a["value"] = cap_value
            a["capped"] = True
            changed.append((a["question_id"], "capped"))
    return changed


def run(grid_name, profile_path, answers_dir, claims_path):
    profile = load_json(profile_path)
    grid = effective_grid(load_grid(grid_name), profile)
    questions_by_id = {q["id"]: q for _, q in all_questions(grid)}
    claims_by_id = {c["id"]: c for c in load_json(claims_path).get("claims", [])}
    all_changed = []
    for path in sorted(glob.glob(os.path.join(answers_dir, "block-?.json"))):
        data = load_json(path)
        changed = apply(data.get("answers", []), questions_by_id, claims_by_id, grid)
        if changed:
            save_json(path, data)
        all_changed.extend(changed)
    return all_changed


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--answers-dir", required=True)
    ap.add_argument("--claims", required=True)
    args = ap.parse_args(argv)
    changed = run(args.grid, args.profile, args.answers_dir, args.claims)
    print(json.dumps({"capped": [q for q, k in changed if k == "capped"], "downgraded": [q for q, k in changed if k == "downgraded"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

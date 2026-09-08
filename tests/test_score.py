"""Tests for scripts/score.py: deck completeness from the 24 answers and the grid weights."""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import score  # noqa: E402

with open(os.path.join(HERE, "..", "scripts", "grid.json"), encoding="utf-8") as f:
    GRID = json.load(f)

ALL_IDS = [q["id"] for b in GRID["blocks"] for q in b["questions"]]


def answers(values):
    """values: dict question_id -> found/partial/absent; missing ids default to absent."""
    return [{"question_id": qid, "value": values.get(qid, "absent"), "evidence": [], "missing": "", "call_question": f"ask about {qid}"}
            for qid in ALL_IDS]


def profile(customer_type="B2B"):
    return {"customer_type": customer_type, "stage": "pre-seed"}


class ScoreTest(unittest.TestCase):
    def test_all_found_gives_100_everywhere(self):
        s = score.compute(GRID, answers({q: "found" for q in ALL_IDS}), profile())
        for b in s["blocks"]:
            self.assertEqual(b["percent"], 100)
        self.assertEqual(s["global_percent"], 100)
        self.assertEqual(s["red_blocks"], [])

    def test_all_absent_gives_zero_and_six_red_blocks(self):
        s = score.compute(GRID, answers({}), profile())
        self.assertEqual(s["global_percent"], 0)
        self.assertEqual(s["red_blocks"], ["A", "B", "C", "D", "E", "F"])

    def test_points_are_value_times_block_weight(self):
        s = score.compute(GRID, answers({"A1": "found", "A2": "partial"}), profile())
        by_id = {q["question_id"]: q for q in s["questions"]}
        self.assertEqual(by_id["A1"]["points"], 6)   # 2 x 3
        self.assertEqual(by_id["A2"]["points"], 3)   # 1 x 3
        self.assertEqual(by_id["A3"]["points"], 0)
        block_a = next(b for b in s["blocks"] if b["id"] == "A")
        self.assertEqual(block_a["max"], 24)         # 4 questions x 2 x 3
        self.assertEqual(block_a["percent"], 37.5)

    def test_c3_weight_zero_is_excluded_from_block_max(self):
        s = score.compute(GRID, answers({"C1": "found", "C2": "found", "C3": "found"}), profile())
        block_c = next(b for b in s["blocks"] if b["id"] == "C")
        self.assertEqual(block_c["max"], 4)          # C1 + C2 only, weight 1
        self.assertEqual(block_c["percent"], 100)
        by_id = {q["question_id"]: q for q in s["questions"]}
        self.assertEqual(by_id["C3"]["counted"], False)

    def test_b3_weight_drops_to_1_when_b2c(self):
        vals = {"B3": "found"}
        b2b = score.compute(GRID, answers(vals), profile("B2B"))
        b2c = score.compute(GRID, answers(vals), profile("B2C"))
        self.assertEqual(next(q for q in b2b["questions"] if q["question_id"] == "B3")["weight"], 3)
        self.assertEqual(next(q for q in b2c["questions"] if q["question_id"] == "B3")["weight"], 1)
        self.assertEqual(next(b for b in b2c["blocks"] if b["id"] == "B")["max"], 26)  # 4x6 + 1x2

    def test_f3_not_assessable_when_f1_or_f2_not_found(self):
        s = score.compute(GRID, answers({"F1": "found", "F2": "partial", "F3": "found"}), profile())
        f3 = next(q for q in s["questions"] if q["question_id"] == "F3")
        self.assertEqual(f3["status"], "not_assessable")
        self.assertFalse(f3["counted"])
        block_f = next(b for b in s["blocks"] if b["id"] == "F")
        self.assertEqual(block_f["max"], 12)         # F1, F2, F4 x 2 x 2

    def test_f3_counted_when_f1_and_f2_found(self):
        s = score.compute(GRID, answers({"F1": "found", "F2": "found", "F3": "partial"}), profile())
        f3 = next(q for q in s["questions"] if q["question_id"] == "F3")
        self.assertTrue(f3["counted"])
        self.assertEqual(f3["points"], 2)

    def test_global_is_weighted_mean_of_block_percents(self):
        # Block A fully found, everything else absent: 100 x 3 / 14 = 21.43
        s = score.compute(GRID, answers({"A1": "found", "A2": "found", "A3": "found", "A4": "found"}), profile())
        self.assertAlmostEqual(s["global_percent"], 21.43, places=2)

    def test_red_block_threshold_is_strictly_below_50(self):
        # E: E1 partial, E2 found, E5 found = 5/10 = 50% -> not red
        s = score.compute(GRID, answers({"E1": "partial", "E2": "found", "E5": "found"}), profile())
        self.assertNotIn("E", s["red_blocks"])
        s2 = score.compute(GRID, answers({"E2": "found", "E5": "found"}), profile())
        self.assertIn("E", s2["red_blocks"])

    def test_red_flags_list_absent_flagged_questions(self):
        s = score.compute(GRID, answers({"A4": "partial"}), profile())
        self.assertNotIn("A4", s["red_flags"])
        self.assertIn("B4", s["red_flags"])
        self.assertIn("F2", s["red_flags"])

    def test_call_questions_are_absent_or_partial_in_weight_3_blocks(self):
        s = score.compute(GRID, answers({"A1": "found", "A2": "partial", "D1": "absent", "F1": "absent"}), profile())
        self.assertIn("A2", s["call_question_ids"])
        self.assertIn("A3", s["call_question_ids"])
        self.assertNotIn("A1", s["call_question_ids"])
        self.assertNotIn("D1", s["call_question_ids"])  # weight 2 block
        self.assertNotIn("F1", s["call_question_ids"])  # weight 2 block

    def test_missing_answer_raises(self):
        with self.assertRaises(score.ScoreError):
            score.compute(GRID, answers({})[:-1], profile())

    def test_unknown_value_raises(self):
        bad = answers({})
        bad[0]["value"] = "maybe"
        with self.assertRaises(score.ScoreError):
            score.compute(GRID, bad, profile())


if __name__ == "__main__":
    unittest.main()

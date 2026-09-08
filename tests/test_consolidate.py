"""Tests for scripts/consolidate.py: median of independent passes, per question."""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import consolidate  # noqa: E402


def ans(qid, value, page=1, quote="q", missing="m", call="c", **extra):
    a = {"question_id": qid, "value": value,
         "evidence": [] if value == "absent" else [{"page": page, "quote": quote}],
         "missing": missing, "call_question": call}
    a.update(extra)
    return a


class MedianTest(unittest.TestCase):
    def test_majority_wins(self):
        self.assertEqual(consolidate.median_value(["partial", "found", "found"]), "found")
        self.assertEqual(consolidate.median_value(["partial", "partial", "found"]), "partial")
        self.assertEqual(consolidate.median_value(["absent", "absent", "found"]), "absent")

    def test_three_different_values_give_the_middle_one(self):
        self.assertEqual(consolidate.median_value(["absent", "partial", "found"]), "partial")

    def test_single_pass_is_itself(self):
        self.assertEqual(consolidate.median_value(["found"]), "found")

    def test_two_passes_disagreeing_take_the_stricter(self):
        self.assertEqual(consolidate.median_value(["found", "partial"]), "partial")
        self.assertEqual(consolidate.median_value(["partial", "absent"]), "absent")


class ConsolidateTest(unittest.TestCase):
    def test_unanimous_is_stable_and_keeps_first_pass_fields(self):
        merged = consolidate.consolidate_answers([
            [ans("A1", "found", quote="first")],
            [ans("A1", "found", quote="second")],
            [ans("A1", "found", quote="third")],
        ])
        a = merged[0]
        self.assertEqual(a["value"], "found")
        self.assertTrue(a["stable"])
        self.assertEqual(a["passes"], ["found", "found", "found"])
        self.assertEqual(a["evidence"][0]["quote"], "first")

    def test_split_takes_median_and_fields_from_a_matching_pass(self):
        merged = consolidate.consolidate_answers([
            [ans("A2", "found", quote="f1", missing="")],
            [ans("A2", "partial", quote="p2", missing="gap2")],
            [ans("A2", "partial", quote="p3", missing="gap3")],
        ])
        a = merged[0]
        self.assertEqual(a["value"], "partial")
        self.assertFalse(a["stable"])
        self.assertEqual(a["passes"], ["found", "partial", "partial"])
        self.assertEqual(a["evidence"][0]["quote"], "p2")
        self.assertEqual(a["missing"], "gap2")

    def test_absent_median_has_no_evidence(self):
        merged = consolidate.consolidate_answers([
            [ans("B4", "absent")], [ans("B4", "partial")], [ans("B4", "absent")],
        ])
        self.assertEqual(merged[0]["value"], "absent")
        self.assertEqual(merged[0]["evidence"], [])

    def test_quote_invalid_pass_counts_as_absent_vote(self):
        merged = consolidate.consolidate_answers([
            [ans("E5", "absent", quote_invalid=True)],
            [ans("E5", "found")],
            [ans("E5", "absent", quote_invalid=True)],
        ])
        self.assertEqual(merged[0]["value"], "absent")
        self.assertTrue(merged[0]["quote_invalid"])

    def test_missing_question_in_a_pass_raises(self):
        with self.assertRaises(consolidate.ConsolidateError):
            consolidate.consolidate_answers([[ans("A1", "found")], []])

    def test_run_writes_final_block_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirs = []
            for i, val in enumerate(["found", "partial", "found"], start=1):
                d = os.path.join(tmp, f"pass-{i}")
                os.makedirs(d)
                with open(os.path.join(d, "block-A.json"), "w", encoding="utf-8") as f:
                    json.dump({"block": "A", "answers": [ans("A1", val)]}, f)
                dirs.append(d)
            out = os.path.join(tmp, "final")
            summary = consolidate.run(dirs, out)
            with open(os.path.join(out, "block-A.json"), encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["answers"][0]["value"], "found")
            self.assertEqual(summary["passes"], 3)
            self.assertEqual(summary["unstable"], ["A1"])


if __name__ == "__main__":
    unittest.main()

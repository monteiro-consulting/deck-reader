"""Tests for scripts/verify_quotes.py.

The key property: a quote that is not on the cited page is rejected.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import verify_quotes  # noqa: E402

PAGES = {
    "source": "pdf",
    "reliable": True,
    "pages": [
        {"number": 1, "text": "GANTRIX\nProcurement follow-up for small industrial firms"},
        {"number": 2, "text": "We interviewed 14 purchasing managers between March and\nJune 2026. One said: “I spend my Fridays chasing suppliers.”"},
    ],
}


def answer(qid, value, evidence, **extra):
    base = {
        "question_id": qid,
        "value": value,
        "evidence": evidence,
        "missing": "",
        "call_question": "",
    }
    base.update(extra)
    return base


class VerifyQuotesTest(unittest.TestCase):
    def check(self, answers):
        return verify_quotes.check_answers(answers, PAGES)

    def test_quote_present_on_cited_page_is_valid(self):
        invalid = self.check([answer("A4", "partial", [{"page": 2, "quote": "We interviewed 14 purchasing managers"}])])
        self.assertEqual(invalid, [])

    def test_quote_absent_from_page_is_rejected(self):
        invalid = self.check([answer("A4", "found", [{"page": 2, "quote": "We interviewed 40 purchasing managers"}])])
        self.assertEqual(len(invalid), 1)
        self.assertEqual(invalid[0]["question_id"], "A4")
        self.assertEqual(invalid[0]["reason"], "quote_not_on_page")

    def test_quote_on_another_page_is_rejected(self):
        invalid = self.check([answer("A4", "found", [{"page": 1, "quote": "We interviewed 14 purchasing managers"}])])
        self.assertEqual(len(invalid), 1)
        self.assertEqual(invalid[0]["reason"], "quote_not_on_page")

    def test_page_out_of_range_is_rejected(self):
        invalid = self.check([answer("A1", "found", [{"page": 9, "quote": "GANTRIX"}])])
        self.assertEqual(invalid[0]["reason"], "page_out_of_range")

    def test_found_without_evidence_is_rejected(self):
        invalid = self.check([answer("A1", "found", [])])
        self.assertEqual(invalid[0]["reason"], "no_evidence")

    def test_absent_with_evidence_is_rejected(self):
        invalid = self.check([answer("A1", "absent", [{"page": 1, "quote": "GANTRIX"}])])
        self.assertEqual(invalid[0]["reason"], "absent_with_evidence")

    def test_absent_without_evidence_is_valid(self):
        self.assertEqual(self.check([answer("B4", "absent", [])]), [])

    def test_line_breaks_and_curly_quotes_are_tolerated(self):
        # The model may straighten quotes and join lines; that is still verbatim.
        invalid = self.check([answer("A4", "found", [{"page": 2, "quote": 'between March and June 2026. One said: "I spend my Fridays'}])])
        self.assertEqual(invalid, [])

    def test_paraphrase_is_rejected(self):
        invalid = self.check([answer("A4", "found", [{"page": 2, "quote": "14 interviews with purchasing managers"}])])
        self.assertEqual(invalid[0]["reason"], "quote_not_on_page")

    def test_more_than_three_evidence_items_is_rejected(self):
        ev = [{"page": 1, "quote": "GANTRIX"}] * 4
        invalid = self.check([answer("A1", "found", ev)])
        self.assertEqual(invalid[0]["reason"], "too_many_evidence_items")

    def test_finalize_marks_invalid_answers_absent_with_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            block_path = os.path.join(tmp, "block-A.json")
            with open(block_path, "w", encoding="utf-8") as f:
                json.dump({"block": "A", "answers": [
                    answer("A1", "found", [{"page": 1, "quote": "GANTRIX"}]),
                    answer("A4", "found", [{"page": 2, "quote": "not on the page at all"}]),
                ]}, f)
            pages_path = os.path.join(tmp, "pages.json")
            with open(pages_path, "w", encoding="utf-8") as f:
                json.dump(PAGES, f)
            invalid = verify_quotes.run(tmp, pages_path, finalize=True)
            self.assertEqual([i["question_id"] for i in invalid], ["A4"])
            with open(block_path, encoding="utf-8") as f:
                data = json.load(f)
            by_id = {a["question_id"]: a for a in data["answers"]}
            self.assertEqual(by_id["A4"]["value"], "absent")
            self.assertEqual(by_id["A4"]["evidence"], [])
            self.assertTrue(by_id["A4"]["quote_invalid"])
            self.assertEqual(by_id["A1"]["value"], "found")
            self.assertFalse(by_id["A1"].get("quote_invalid", False))


if __name__ == "__main__":
    unittest.main()

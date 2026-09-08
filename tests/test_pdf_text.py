"""Tests for scripts/pdf_text.py against the generated fixture."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
sys.path.insert(0, os.path.join(HERE, "..", "fixtures"))

import pdf_text  # noqa: E402
import make_fixture  # noqa: E402


class PdfTextTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = pdf_text.extract(make_fixture.build_pdf(make_fixture.PAGES))

    def test_page_count(self):
        self.assertEqual(self.result["page_count"], 12)
        self.assertTrue(self.result["reliable"])

    def test_pages_are_in_order(self):
        self.assertIn("GANTRIX", self.result["pages"][0]["text"])
        self.assertIn("Who already invested", self.result["pages"][11]["text"])

    def test_phrase_is_on_the_right_page(self):
        p4 = self.result["pages"][3]["text"]
        self.assertIn("We interviewed 14 purchasing managers", p4)
        self.assertNotIn("We interviewed 14 purchasing managers", self.result["pages"][2]["text"])

    def test_wrapped_lines_are_matchable_by_verify_quotes(self):
        import verify_quotes
        p2 = self.result["pages"][1]["text"]
        self.assertTrue(verify_quotes.quote_on_page(
            "chase supplier confirmations by email, one order at a time", p2))

    def test_not_a_pdf_is_empty(self):
        r = pdf_text.extract(b"hello")
        self.assertEqual(r["page_count"], 0)
        self.assertFalse(r["reliable"])


if __name__ == "__main__":
    unittest.main()

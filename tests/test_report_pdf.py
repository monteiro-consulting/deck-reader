"""Tests for scripts/report_pdf.py: the markdown reading rendered as a PDF, checked by round-trip
through the plugin's own text extractor (pdf_text.py), so the PDF says what the markdown says."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import pdf_text  # noqa: E402
import report_pdf  # noqa: E402

FIXTURE = os.path.join(HERE, "..", "fixtures", "preseed-deck.reading.md")


def extract_all(data):
    doc = pdf_text.extract(data)
    return doc, "\n".join(p["text"] for p in doc["pages"])


class RenderFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FIXTURE, encoding="utf-8") as f:
            cls.md = f.read()
        cls.pdf = report_pdf.render(cls.md, "preseed-deck.reading.md")
        cls.doc, cls.text = extract_all(cls.pdf)

    def test_is_a_pdf_with_several_pages(self):
        self.assertTrue(self.pdf.startswith(b"%PDF-1.4"))
        self.assertTrue(self.pdf.rstrip().endswith(b"%%EOF"))
        self.assertGreaterEqual(self.doc["page_count"], 3)
        self.assertTrue(self.doc["reliable"])

    def test_headings_and_reading_survive(self):
        for needle in ("Fiche du deck", "Complétude du deck", "Questions pour l'appel", "Question par question",
                       "Lena et Marc travaillent-ils", "68.9"):
            self.assertIn(needle, self.text, needle)

    def test_no_emoji_glyph_but_status_words_kept(self):
        self.assertNotIn("\U0001F7E2", self.text)
        self.assertIn("trouvée", self.text)
        self.assertIn("absente", self.text)

    def test_page_numbers_in_footer(self):
        self.assertIn(f"1 / {self.doc['page_count']}", self.doc["pages"][0]["text"])


class Inline(unittest.TestCase):
    def test_bold_code_and_links_are_flattened(self):
        r = report_pdf.runs("a **b** `c` [d](http://x) e")
        self.assertEqual([(t.strip(), s) for t, s in r if t.strip()], [("a", "r"), ("b", "b"), ("c", "c"), ("d", "r"), ("e", "r")])

    def test_bar_cells(self):
        self.assertTrue(report_pdf._is_bar("`██████████████░░░░░░`"))
        self.assertAlmostEqual(report_pdf._bar_ratio("`██████████████░░░░░░`"), 0.7)
        self.assertFalse(report_pdf._is_bar("87.5 %"))

    def test_wrap_never_exceeds_width(self):
        lines = report_pdf.wrap_runs(report_pdf.runs("mot " * 60), 10, 200)
        for line in lines:
            self.assertLessEqual(sum(report_pdf.text_w(t, s, 10) for t, s in line), 200 + 1e-6)

    def test_render_handles_every_block_kind(self):
        md = "# T\n\n> quote\n\n- a\n- b\n\n---\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n```\ncode\n```\n\ntext\n"
        _, text = extract_all(report_pdf.render(md, "t"))
        for needle in ("T", "quote", "a", "code", "text", "1", "2"):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()

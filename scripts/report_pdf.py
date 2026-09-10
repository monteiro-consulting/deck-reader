#!/usr/bin/env python3
"""Render the markdown reading (report.py output) as a PDF, next to it. Standard library only.

Usage:
    report_pdf.py deck.reading.md                    -> deck.reading.pdf
    report_pdf.py deck.reading.md --out other.pdf

What is rendered: headings, paragraphs, bullets, blockquotes, horizontal rules, tables (the
completeness bars are drawn as bars), fenced code blocks (the email draft) and the inline
**bold** / `code` runs. Links keep their text. Emoji have no glyph in the standard PDF fonts:
the status words next to them (found / partial / absent) carry the meaning, so they are dropped.

Nothing is inferred and nothing is added: the PDF says exactly what the markdown says.
"""
import argparse
import os
import re
import sys
import textwrap
import zlib

PAGE_W, PAGE_H = 595, 842            # A4, points
MARGIN = 50
BODY_W = PAGE_W - 2 * MARGIN
BODY, LEADING = 10.5, 14.5
FOOT_LINE = "deck-reader"

# Fonts of the standard 14, no embedding needed. Encoding WinAnsi = cp1252.
FONTS = {"r": "Helvetica", "b": "Helvetica-Bold", "i": "Helvetica-Oblique", "c": "Courier"}
FONT_KEYS = {"r": "/F1", "b": "/F2", "i": "/F3", "c": "/F4"}

# Approximate Helvetica advance widths (per 1 pt of font size), by character class. Good
# enough to wrap with a small safety margin; Courier is fixed at 0.6.
_NARROW = set("iljtfrI.,:;'!|()[]{}/\\ ")
_WIDE = set("mwMW@%")
_UPPER = set("ABCDEFGHJKLNOPQRSTUVXYZ")


def char_w(ch, style):
    if style == "c":
        return 0.6
    if ch in _NARROW:
        return 0.3
    if ch in _WIDE:
        return 0.85
    if ch in _UPPER or ch in "0123456789":
        return 0.62
    if ch.isupper():
        return 0.66
    return 0.54 if style != "b" else 0.57


def text_w(s, style, size):
    return sum(char_w(c, style) for c in s) * size


# ---------------------------------------------------------------- text clean-up

_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]")
_REPL = {"—": "-", "–": "-", "…": "...", "→": "->", "←": "<-", "⚠": "!", "•": "\x95", "≤": "<=", "≥": ">=", "×": "x", " ": " ", " ": " "}


def clean(s):
    s = _EMOJI.sub("", s)
    for a, b in _REPL.items():
        s = s.replace(a, b)
    s = re.sub(r"  +", " ", s)
    return s.strip()


def esc(s):
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def enc(s):
    return esc(s).encode("cp1252", errors="replace").decode("cp1252")


# ---------------------------------------------------------------- inline markdown

_INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def runs(text, base="r"):
    """Split a line into (text, style) runs. Bold and code nest nowhere: kept flat on purpose."""
    out = []
    for part in _INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            out.append((part[2:-2], "b"))
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            out.append((part[1:-1], "c"))
        elif part.startswith("["):
            out.append((re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", part), base))
        else:
            out.append((part, base))
    return out


def wrap_runs(run_list, size, width):
    """Word-wrap styled runs into lines of [(word_or_space, style)], measuring per style."""
    words = []
    for text, style in run_list:
        for i, tok in enumerate(re.split(r"(\s+)", text)):
            if tok:
                words.append((tok, style))
    lines, cur, cur_w = [], [], 0.0
    for tok, style in words:
        w = text_w(tok, style, size)
        if tok.isspace():
            if cur:
                cur.append((" ", style))
                cur_w += text_w(" ", style, size)
            continue
        if cur and cur_w + w > width:
            while cur and cur[-1][0] == " ":
                cur.pop()
            lines.append(cur)
            cur, cur_w = [], 0.0
        # a single token wider than the line is cut hard
        while w > width and len(tok) > 1:
            n = max(1, int(len(tok) * width / w) - 1)
            lines.append([(tok[:n], style)])
            tok = tok[n:]
            w = text_w(tok, style, size)
        cur.append((tok, style))
        cur_w += w
    if cur:
        lines.append(cur)
    return lines or [[]]


# ---------------------------------------------------------------- page builder

class Doc:
    def __init__(self):
        self.pages = []      # list of op lists (str)
        self.ops = None
        self.y = 0
        self.new_page()

    def new_page(self):
        self.ops = []
        self.pages.append(self.ops)
        self.y = PAGE_H - MARGIN

    def need(self, h):
        if self.y - h < MARGIN + 20:
            self.new_page()

    def text(self, x, y, line, size):
        """line: list of (text, style)."""
        parts = ["BT"]
        cur = None
        parts.append(f"1 0 0 1 {x:.1f} {y:.1f} Tm")
        for tok, style in line:
            if style != cur:
                parts.append(f"{FONT_KEYS[style]} {size} Tf")
                cur = style
            parts.append(f"({enc(tok)}) Tj")
        parts.append("ET")
        self.ops.append(" ".join(parts))

    def rect(self, x, y, w, h, gray):
        self.ops.append(f"{gray:.2f} g {x:.1f} {y:.1f} {w:.1f} {h:.1f} re f 0 g")

    def hline(self, x, y, w, gray=0.75, lw=0.5):
        self.ops.append(f"{gray:.2f} G {lw} w {x:.1f} {y:.1f} m {x + w:.1f} {y:.1f} l S 0 G")

    # -- blocks
    def paragraph(self, text, size=BODY, style="r", indent=0, width=None, leading=None, gap=6):
        width = width or (BODY_W - indent)
        leading = leading or (size * 1.38)
        lines = wrap_runs(runs(clean(text), style), size, width)
        self.need(leading * min(len(lines), 2))
        for line in lines:
            self.need(leading)
            self.y -= leading
            self.text(MARGIN + indent, self.y, line, size)
        self.y -= gap

    def heading(self, text, level):
        size = {1: 19, 2: 14.5, 3: 12}.get(level, 11.5)
        self.need(size * 3.2)
        self.y -= {1: 6, 2: 16, 3: 10}.get(level, 8)
        lines = wrap_runs(runs(clean(text), "b"), size, BODY_W)
        for line in lines:
            self.y -= size * 1.25
            self.text(MARGIN, self.y, line, size)
        if level == 1:
            self.y -= 6
            self.hline(MARGIN, self.y, BODY_W, gray=0.2, lw=0.8)
        self.y -= 8 if level > 1 else 12

    def bullet(self, text):
        lead = BODY * 1.38
        self.need(lead * 2)
        top = self.y
        page = self.ops
        self.paragraph(text, indent=14, gap=3)
        # the bullet glyph, on the first line of the item, drawn on the page where it started
        page.append(f"BT /F1 {BODY} Tf 1 0 0 1 {MARGIN + 2:.1f} {top - lead:.1f} Tm ({enc(chr(0x2022))}) Tj ET")

    def quote(self, text):
        top = self.y
        self.paragraph(text, style="i", indent=14, gap=4, size=BODY - 0.5)
        self.ops.append(f"0.6 G 1.2 w {MARGIN + 4:.1f} {top - 2:.1f} m {MARGIN + 4:.1f} {self.y + 4:.1f} l S 0 G")

    def rule(self):
        self.need(14)
        self.y -= 7
        self.hline(MARGIN, self.y, BODY_W)
        self.y -= 7

    def code(self, lines):
        size, lead = 8.5, 11
        cols = int(BODY_W / (0.6 * size)) - 4
        wrapped = []
        for ln in lines:
            ln = clean(ln) or ""
            wrapped += textwrap.wrap(ln, cols, replace_whitespace=False, drop_whitespace=False) or [""]
        self.need(lead * min(len(wrapped), 3) + 12)
        i = 0
        while i < len(wrapped):
            avail = int((self.y - MARGIN - 20) / lead)
            if avail < 2:
                self.new_page()
                avail = int((self.y - MARGIN - 20) / lead)
            chunk = wrapped[i:i + avail]
            h = lead * len(chunk) + 10
            self.rect(MARGIN, self.y - h, BODY_W, h, 0.94)
            yy = self.y - 5
            for ln in chunk:
                yy -= lead
                self.text(MARGIN + 8, yy + 2, [(ln, "c")], size)
            self.y -= h
            i += avail
        self.y -= 8

    def table(self, rows):
        """rows: list of list of cell strings; first row = header."""
        size, lead, pad = 8.8, 11.2, 4
        ncol = max(len(r) for r in rows)
        rows = [r + [""] * (ncol - len(r)) for r in rows]
        cells = [[runs(clean(c), "b" if ri == 0 else "r") for c in r] for ri, r in enumerate(rows)]
        bar_col = {ci for ci in range(ncol) if any(_is_bar(rows[ri][ci]) for ri in range(1, len(rows)))}
        natural = []
        for ci in range(ncol):
            if ci in bar_col:
                natural.append(110)
                continue
            m = 0
            for r in cells:
                m = max(m, sum(text_w(t, s, size) for t, s in r[ci]))
            natural.append(max(30, min(m + 2 * pad + 3, BODY_W * 0.45)))
        total = sum(natural)
        widths = list(natural)
        if total > BODY_W:
            # shrink the widest columns first, never below 48 pt
            flex = [w for w in natural if w > 60]
            scale = (BODY_W - (total - sum(flex))) / sum(flex) if flex else 1
            widths = [max(48, w * scale) if w > 60 else w for w in natural]
            # the shrink can leave the table a little wider than the body; clamp the widest column
            over = sum(widths) - BODY_W
            if over > 0:
                k = widths.index(max(widths))
                widths[k] = max(48, widths[k] - over)
        else:
            # give the spare room to the widest column
            widths[natural.index(max(natural))] += BODY_W - total
        # lay out rows
        for ri, r in enumerate(cells):
            lines_per_cell = []
            for ci in range(ncol):
                if ci in bar_col and ri > 0 and _is_bar(rows[ri][ci]):
                    lines_per_cell.append(None)
                else:
                    lines_per_cell.append(wrap_runs(r[ci], size, widths[ci] - 2 * pad))
            h = max(len(l) if l else 1 for l in lines_per_cell) * lead + 2 * pad
            if self.y - h < MARGIN + 20:
                self.new_page()
                if ri > 0:
                    self._table_row(cells[0], [wrap_runs(c, size, widths[ci] - 2 * pad) for ci, c in enumerate(cells[0])], widths, size, lead, pad, header=True)
            self._table_row(r, lines_per_cell, widths, size, lead, pad, header=(ri == 0), raw=rows[ri])
        self.y -= 10

    def _table_row(self, r, lines_per_cell, widths, size, lead, pad, header=False, raw=None):
        h = max(len(l) if l else 1 for l in lines_per_cell) * lead + 2 * pad
        if header:
            self.rect(MARGIN, self.y - h, BODY_W, h, 0.92)
        x = MARGIN
        for ci, lines in enumerate(lines_per_cell):
            if lines is None:
                fill = _bar_ratio(raw[ci])
                bw = widths[ci] - 2 * pad
                by = self.y - pad - lead + 3
                self.rect(x + pad, by, bw, 6, 0.85)
                self.rect(x + pad, by, bw * fill, 6, 0.25)
            else:
                yy = self.y - pad
                for line in lines:
                    yy -= lead
                    self.text(x + pad, yy + 3, line, size)
            x += widths[ci]
        self.y -= h
        self.hline(MARGIN, self.y, BODY_W, gray=0.8)

    # -- output
    def build(self, title):
        total = len(self.pages)
        objs = []

        def add(o):
            objs.append(o)
            return len(objs)

        catalog = add(None)
        pages_id = add(None)
        font_ids = {k: add(f"<< /Type /Font /Subtype /Type1 /BaseFont /{v} /Encoding /WinAnsiEncoding >>".encode()) for k, v in FONTS.items()}
        res = b"/Resources << /Font << " + b" ".join(f"{FONT_KEYS[k]} {font_ids[k]} 0 R".encode() for k in FONTS) + b" >> >>"
        page_ids = []
        for i, ops in enumerate(self.pages, start=1):
            foot = f"BT /F1 8 Tf 1 0 0 1 {MARGIN} 30 Tm ({enc(FOOT_LINE + ' - ' + title)}) Tj ET BT /F1 8 Tf 1 0 0 1 {PAGE_W - MARGIN - 30} 30 Tm ({i} / {total}) Tj ET"
            raw = ("\n".join(ops) + "\n" + foot).encode("cp1252", errors="replace")
            data = zlib.compress(raw)
            sid = add(b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(data) + data + b"\nendstream")
            page_ids.append(add(b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %d %d] " % (pages_id, PAGE_W, PAGE_H) + res + b" /Contents %d 0 R >>" % sid))
        objs[pages_id - 1] = b"<< /Type /Pages /Kids [" + b" ".join(b"%d 0 R" % p for p in page_ids) + b"] /Count %d >>" % len(page_ids)
        objs[catalog - 1] = b"<< /Type /Catalog /Pages %d 0 R >>" % pages_id
        info = add(b"<< /Producer (deck-reader report_pdf.py) /Title (" + enc(title).encode("cp1252", errors="replace") + b") >>")
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = []
        for num, o in enumerate(objs, start=1):
            offsets.append(len(out))
            out += b"%d 0 obj\n" % num + o + b"\nendobj\n"
        xref = len(out)
        out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
        for off in offsets:
            out += b"%010d 00000 n \n" % off
        out += b"trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, catalog, info, xref)
        return bytes(out)


def _is_bar(cell):
    c = cell.strip().strip("`")
    return bool(c) and set(c) <= {"█", "░"}


def _bar_ratio(cell):
    c = cell.strip().strip("`")
    return c.count("█") / max(1, len(c))


# ---------------------------------------------------------------- markdown walk

def render(md, title=""):
    doc = Doc()
    lines = md.splitlines()
    i, n = 0, len(lines)
    para = []

    def flush():
        if para:
            doc.paragraph(" ".join(para))
            para.clear()

    while i < n:
        ln = lines[i]
        s = ln.strip()
        if s.startswith("```"):
            flush()
            block = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            doc.code(block)
        elif s.startswith("#"):
            flush()
            level = len(s) - len(s.lstrip("#"))
            doc.heading(s[level:].strip(), level)
        elif s.startswith("|"):
            flush()
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                row = lines[i].strip().strip("|")
                cells = [c.strip() for c in re.split(r"(?<!\\)\|", row)]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                    rows.append(cells)
                i += 1
            if rows:
                doc.table(rows)
            continue
        elif s.startswith(">"):
            flush()
            q = []
            while i < n and lines[i].strip().startswith(">"):
                q.append(lines[i].strip()[1:].strip())
                i += 1
            text = " ".join(x for x in q if x) if not any(x == "" for x in q) else None
            if text is None:
                # blank quote lines separate quote paragraphs
                buf = []
                for x in q + [""]:
                    if x:
                        buf.append(x)
                    elif buf:
                        doc.quote(" ".join(buf))
                        buf = []
            else:
                doc.quote(text)
            continue
        elif re.match(r"^[-*]\s+", s):
            flush()
            doc.bullet(re.sub(r"^[-*]\s+", "", s))
        elif re.fullmatch(r"-{3,}|\*{3,}", s):
            flush()
            doc.rule()
        elif not s:
            flush()
        else:
            para.append(s)
        i += 1
    flush()
    return doc.build(title)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("markdown", help="the .reading.md written by report.py")
    ap.add_argument("--out", help="output path; default: same name with .pdf")
    args = ap.parse_args(argv)
    src = args.markdown
    out = args.out or (src[:-3] if src.lower().endswith(".md") else src) + ".pdf"
    with open(src, encoding="utf-8") as f:
        md = f.read()
    title = os.path.basename(src)
    with open(out, "wb") as f:
        f.write(render(md, title))
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

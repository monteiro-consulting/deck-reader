#!/usr/bin/env python3
"""Generate fixtures/preseed-deck.pdf, a 12-page FICTIONAL pre-seed deck.

Standard library only (a minimal PDF writer, Helvetica, WinAnsi, Flate streams).
Every name, figure and person is invented. The deck has deliberate gaps so that the
reader has something to find missing. Expected grid outcome is listed at the bottom.

Run:  python fixtures/make_preseed_fixture.py
"""
import os
import textwrap
import zlib

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preseed-deck.pdf")

FOOTER = "FICTIONAL DECK - generated for testing deck-reader. All names, figures and people are invented."

# Each page: (title, [paragraphs]). Empty string = blank line.
PAGES = [
    ("GANTRIX", [
        "Procurement follow-up for small industrial firms.",
        "",
        "Pre-seed round - September 2026",
        "",
        "Lena Vartan, CEO - Marc Delorme, CTO",
        "contact: fictional@example.com",
    ]),
    ("The problem", [
        "Purchasing managers in industrial SMEs (50 to 200 employees) chase supplier confirmations by email, "
        "one order at a time.",
        "",
        "From our field notes: a purchasing manager spends about 6 hours a week on supplier follow-ups. "
        "This is our estimate from the interviews, not a measured figure.",
        "",
        "When a confirmation is missed, the production line waits. One plant told us a late delivery "
        "stopped a line for two days in April 2026.",
    ]),
    ("How they cope today", [
        "Today they use Excel and email threads. Every order has its own tab, updated by hand on Friday afternoons.",
        "",
        "Two of the companies we met use a shared Google Sheet. None of them uses a dedicated tool: "
        "the ERP modules they own are, in their words, too heavy for this.",
    ]),
    ("What we learned", [
        "We interviewed 14 purchasing managers between March and June 2026, in the Lyon and Nantes areas.",
        "",
        "All 14 chase confirmations by hand. 11 of them said they would try a tool that reads their emails for them.",
        "",
        "Interview notes are available on request.",
    ]),
    ("The product", [
        "Gantrix is a web app that reads supplier emails and updates the order status automatically.",
        "",
        "Current state: a clickable prototype built in Figma, tested with 3 purchasing managers in June 2026. "
        "The email parsing engine is not built yet.",
    ]),
    ("Traction", [
        "Waiting list: 38 companies signed up on our landing page since May 2026.",
        "",
        "Letters of intent signed by Ferrolux SAS and Metalpro Ouest.",
        "",
        "One paid pilot: Ferrolux SAS pays 200 EUR per month since July 2026 for a manual version of the service "
        "(we update their sheet by hand).",
        "",
        "Since March 2026 we have: run 14 interviews, built the Figma prototype, signed 2 letters of intent, "
        "started 1 paid pilot.",
    ]),
    ("Business model", [
        "Pricing: 150 EUR per month per site. This price comes from our spreadsheet model and has not been "
        "tested with prospects yet.",
        "",
        "The purchasing manager uses the tool; the plant director signs the subscription. "
        "In the 14 companies we met, the director was always involved in software purchases above 100 EUR per month.",
    ]),
    ("Market", [
        "Procurement software for industrial SMEs is a 40 billion dollar market worldwide, according to an analyst report.",
        "",
        "Why now: since 2025 the EU e-invoicing mandate forces suppliers to send structured documents, "
        "which makes the emails machine-readable for the first time.",
    ]),
    ("Team", [
        "Lena Vartan, CEO. 8 years as purchasing manager at Forgeval Industries (fictional group, 180 employees), "
        "where she led a team of 6 buyers. She lived the problem every week.",
        "",
        "Marc Delorme, CTO. Ex-BigTech engineer.",
        "",
        "Roles: product and sales discovery (Lena), tech (Marc). Sales: no one yet. "
        "We plan to hire a first sales person after the round.",
    ]),
    ("The ask", [
        "We are raising 400,000 EUR in this pre-seed round.",
        "",
        "Use of funds: 60% product (email parsing engine, 2 developers), 25% first sales hire, 15% operations.",
    ]),
    ("Next milestone", [
        "Goal before the seed round: 20 paying customers within 12 months of closing.",
        "",
        "At the current plan, 400,000 EUR covers 14 months of spending, which leaves 2 months of margin "
        "after the 12-month goal.",
    ]),
    ("Who already invested", [
        "Founders: 30,000 EUR of their own money, invested in January 2026.",
        "",
        "Regional innovation grant: 25,000 EUR, received in May 2026.",
        "",
        "No business angel so far.",
    ]),
]

# Expected outcome when the grid is applied (for observations, not used by the code):
# A1 found (p2)  A2 partial (p2, estimate, no source)  A3 found (p3)  A4 partial (p4: number, no verbatim quote)
# B1 partial (p5, Figma mockup)  B2 found (p6)  B3 found (p6)  B4 absent  B5 found (p6)
# C1 partial (p7, spreadsheet price)  C2 found (p7)  C3 absent (info only)
# D1 absent (p8, top-down 40bn)  D2 found (p8)  D3 absent
# E1 partial (p9: Lena verifiable, Marc "ex-BigTech")  E2 found (p9)  E3 absent  E4 absent  E5 found (p9)
# F1 found (p10)  F2 found (p11)  F3 found (p11)  F4 found (p12)


def esc(s):
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def content_stream(title, paragraphs, page_no, total):
    lines = ["BT", "/F2 22 Tf", "50 780 Td", f"({esc(title)}) Tj", "ET"]
    lines += ["BT", "/F1 12 Tf", "16 TL", "50 740 Td"]
    for para in paragraphs:
        if not para:
            lines.append("T*")
            continue
        for wrapped in textwrap.wrap(para, 85):
            lines.append(f"({esc(wrapped)}) Tj T*")
    lines += ["ET"]
    lines += ["BT", "/F1 8 Tf", "50 40 Td", f"({esc(FOOTER)}) Tj", "ET"]
    lines += ["BT", "/F1 9 Tf", "520 40 Td", f"({page_no} / {total}) Tj", "ET"]
    return "\n".join(lines).encode("cp1252")


def build_pdf(pages):
    objects = []  # list of bytes, index+1 = object number

    def add(obj):
        objects.append(obj)
        return len(objects)

    catalog_id = add(None)  # placeholder 1
    pages_id = add(None)    # placeholder 2
    font_regular = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    font_bold = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")

    page_ids = []
    total = len(pages)
    for i, (title, paragraphs) in enumerate(pages, start=1):
        raw = content_stream(title, paragraphs, i, total)
        data = zlib.compress(raw)
        stream_id = add(b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(data) + data + b"\nendstream")
        page_obj = (
            b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 %d 0 R /F2 %d 0 R >> >> /Contents %d 0 R >>"
            % (pages_id, font_regular, font_bold, stream_id)
        )
        page_ids.append(add(page_obj))

    kids = b" ".join(b"%d 0 R" % pid for pid in page_ids)
    objects[pages_id - 1] = b"<< /Type /Pages /Kids [%s] /Count %d >>" % (kids, len(page_ids))
    objects[catalog_id - 1] = b"<< /Type /Catalog /Pages %d 0 R >>" % pages_id

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for num, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % num + obj + b"\nendobj\n"
    xref_pos = len(out)
    out += b"xref\n0 %d\n" % (len(objects) + 1)
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, catalog_id, xref_pos)
    return bytes(out)


if __name__ == "__main__":
    pdf = build_pdf(PAGES)
    with open(OUT, "wb") as f:
        f.write(pdf)
    print(f"wrote {OUT} ({len(pdf)} bytes, {len(PAGES)} pages)")

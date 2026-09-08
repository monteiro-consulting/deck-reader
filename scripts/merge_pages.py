#!/usr/bin/env python3
"""Build pages.json, the single page reference given to the checkers and the quote verifier.

Usage:
    merge_pages.py --pdf-text pdf-text.json --transcription transcription.json --out pages.json

Rule
    The "text" of each page is the PDF text layer (pdf_text.py) when extraction is reliable,
    otherwise the model transcription. Titles, figures and claims always come from the
    transcription. The chosen source is recorded in "reference_source" and printed in the
    report header. Quotes are verified against "text" only, so a checker can only cite what
    is in the reference text.
"""
import argparse
import json
import sys


def merge(pdf_text, transcription):
    use_pdf = bool(pdf_text and pdf_text.get("reliable"))
    t_pages = {int(p["number"]): p for p in (transcription or {}).get("pages", [])}
    p_pages = {int(p["number"]): p for p in (pdf_text or {}).get("pages", [])}
    numbers = sorted(set(t_pages) | set(p_pages))
    pages = []
    for n in numbers:
        t = t_pages.get(n, {})
        p = p_pages.get(n, {})
        text = p.get("text", "") if use_pdf else t.get("text", "")
        if not text.strip():
            # A blank page in the chosen source: keep the other source so the page is not lost.
            text = t.get("text", "") if use_pdf else p.get("text", "")
        pages.append({
            "number": n,
            "title": t.get("title", ""),
            "text": text,
            "figures": t.get("figures", []),
            "claims": t.get("claims", []),
        })
    return {
        "reference_source": "pdf" if use_pdf else "transcription",
        "deck_language": (transcription or {}).get("deck_language", ""),
        "page_count": len(pages),
        "warnings": (pdf_text or {}).get("warnings", []),
        "pages": pages,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf-text", required=True)
    ap.add_argument("--transcription", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    with open(args.pdf_text, encoding="utf-8") as f:
        pdf_text = json.load(f)
    with open(args.transcription, encoding="utf-8") as f:
        transcription = json.load(f)
    result = merge(pdf_text, transcription)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in result.items() if k != "pages"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Verify that every quote cited by the block checkers exists verbatim on the cited page.

Standard library only. No model is involved.

Usage:
    verify_quotes.py --answers-dir DIR --pages PAGES.json [--out invalid.json] [--finalize]

Inputs
    DIR          contains block-A.json ... block-F.json, each {"block": "A", "answers": [...]}
    PAGES.json   {"pages": [{"number": 1, "text": "..."}, ...]}
                 produced by pdf_text.py (preferred) or by the page transcriber (fallback)

Outputs
    invalid.json: list of rejected answers with a reason. Exit code 1 if any, unless --finalize.
    --finalize rewrites the block files: each invalid answer becomes "absent", evidence [],
    quote_invalid true. Use it after the retries are exhausted.

Matching rule
    Text is normalised on both sides (Unicode NFKC, straight quotes, plain hyphens, collapsed
    whitespace, case folded) and the quote must appear as a contiguous substring of the page.
    A second pass ignores all whitespace, to tolerate line breaks inside words that PDF
    extraction sometimes produces. Nothing looser than that: a paraphrase is rejected.
"""
import argparse
import glob
import json
import os
import re
import sys
import unicodedata

MAX_EVIDENCE = 3
VALUES = {"found", "partial", "absent"}

_QUOTE_MAP = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "«": '"', "»": '"', "‹": "'", "›": "'",
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "―": "-", "−": "-",
    " ": " ", " ": " ", " ": " ", " ": " ",
    "­": "", "​": "", "﻿": "",
    "…": "...",
}
_TRANS = str.maketrans(_QUOTE_MAP)


def normalize(text):
    text = unicodedata.normalize("NFKC", text or "")
    text = text.translate(_TRANS)
    text = re.sub(r"\s+", " ", text)
    return text.strip().casefold()


def quote_on_page(quote, page_text):
    q = normalize(quote)
    p = normalize(page_text)
    if not q:
        return False
    if q in p:
        return True
    # Tolerate line breaks that split words during extraction.
    return q.replace(" ", "") in p.replace(" ", "")


def _page_map(pages):
    return {int(p["number"]): p.get("text", "") for p in pages.get("pages", [])}


def check_answers(answers, pages):
    """Return the list of invalid answers: [{question_id, reason, page, quote}]."""
    page_text = _page_map(pages)
    invalid = []

    def reject(ans, reason, page=None, quote=None):
        invalid.append({"question_id": ans.get("question_id"), "reason": reason, "page": page, "quote": quote})

    for ans in answers:
        value = ans.get("value")
        evidence = ans.get("evidence") or []
        if value not in VALUES:
            reject(ans, "unknown_value")
            continue
        if value == "absent":
            if evidence:
                reject(ans, "absent_with_evidence")
            continue
        if not evidence:
            reject(ans, "no_evidence")
            continue
        if len(evidence) > MAX_EVIDENCE:
            reject(ans, "too_many_evidence_items")
            continue
        for ev in evidence:
            page = ev.get("page")
            quote = ev.get("quote", "")
            try:
                page = int(page)
            except (TypeError, ValueError):
                reject(ans, "page_missing", page, quote)
                break
            if page not in page_text:
                reject(ans, "page_out_of_range", page, quote)
                break
            if not quote_on_page(quote, page_text[page]):
                reject(ans, "quote_not_on_page", page, quote)
                break
    return invalid


def load_blocks(answers_dir):
    blocks = {}
    for path in sorted(glob.glob(os.path.join(answers_dir, "block-*.json"))):
        with open(path, encoding="utf-8") as f:
            blocks[path] = json.load(f)
    return blocks


def run(answers_dir, pages_path, out_path=None, finalize=False):
    with open(pages_path, encoding="utf-8") as f:
        pages = json.load(f)
    blocks = load_blocks(answers_dir)
    if not blocks:
        raise SystemExit(f"no block-*.json found in {answers_dir}")

    all_invalid = []
    for path, data in blocks.items():
        invalid = check_answers(data.get("answers", []), pages)
        for item in invalid:
            item["block"] = data.get("block")
            item["file"] = os.path.basename(path)
        all_invalid.extend(invalid)
        if finalize and invalid:
            bad_ids = {i["question_id"] for i in invalid}
            for ans in data["answers"]:
                if ans.get("question_id") in bad_ids:
                    ans["value"] = "absent"
                    ans["evidence"] = []
                    ans["quote_invalid"] = True
                    if not ans.get("missing"):
                        ans["missing"] = "The cited quote could not be verified on the cited page after retries."
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(all_invalid, f, ensure_ascii=False, indent=2)
    return all_invalid


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--answers-dir", required=True)
    ap.add_argument("--pages", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--finalize", action="store_true")
    args = ap.parse_args(argv)

    invalid = run(args.answers_dir, args.pages, args.out, args.finalize)
    print(json.dumps(invalid, ensure_ascii=False, indent=2))
    if invalid and not args.finalize:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Read the annexes given with a seed deck into one JSON, page by page. Standard library only.

Usage:
    annex_text.py --out annexes.json [FILE ...]

Accepted: .pdf (text layer, via pdf_text.py), .csv, .tsv, .txt, .md, .json, .xlsx (cells
joined by tabs, one "page" per sheet). Anything else is listed with kind "unsupported" and no
text. Long text files are cut into pages of PAGE_LINES lines so that a quote can be located.

Output:
    {"annex_count": 2,
     "annexes": [{"id": "X1", "file": "revenue.csv", "kind": "csv", "warnings": [],
                  "pages": [{"number": 1, "text": "..."}]}]}

The "text" of each page is the only thing the annex matcher may quote, and the only thing
verify_matches.py checks quotes against.
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

import pdf_text

PAGE_LINES = 80
TEXT_KINDS = {".csv": "csv", ".tsv": "csv", ".txt": "txt", ".md": "md", ".json": "json"}
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _paginate(lines):
    pages = []
    for i in range(0, max(len(lines), 1), PAGE_LINES):
        chunk = lines[i:i + PAGE_LINES]
        pages.append({"number": len(pages) + 1, "text": "\n".join(chunk)})
    return pages


def _read_text_file(path):
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _csv_lines(text):
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(io.StringIO(text), dialect))
    return ["\t".join(cell.strip() for cell in row) for row in rows]


def _col_index(ref):
    letters = re.match(r"[A-Z]+", ref or "")
    if not letters:
        return 0
    n = 0
    for ch in letters.group(0):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _xlsx_sheets(path):
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
        names = {}
        if "xl/workbook.xml" in z.namelist():
            wb = ET.fromstring(z.read("xl/workbook.xml"))
            sheets_el = wb.find("m:sheets", NS)
            for i, s in enumerate(list(sheets_el) if sheets_el is not None else [], start=1):
                names[i] = s.get("name", f"sheet{i}")
        sheets = []
        i = 1
        while f"xl/worksheets/sheet{i}.xml" in z.namelist():
            root = ET.fromstring(z.read(f"xl/worksheets/sheet{i}.xml"))
            lines = []
            for row in root.iter("{%s}row" % NS["m"]):
                cells = {}
                for c in row.findall("m:c", NS):
                    v = c.find("m:v", NS)
                    t = c.get("t")
                    if t == "s" and v is not None:
                        val = shared[int(v.text)] if v.text and v.text.isdigit() and int(v.text) < len(shared) else ""
                    elif t == "inlineStr":
                        val = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
                    else:
                        val = v.text if v is not None and v.text is not None else ""
                    cells[_col_index(c.get("r"))] = val
                if cells:
                    width = max(cells) + 1
                    lines.append("\t".join(cells.get(k, "") for k in range(width)))
            sheets.append((names.get(i, f"sheet{i}"), lines))
            i += 1
    return sheets


def read_annex(path, annex_id):
    ext = os.path.splitext(path)[1].lower()
    item = {"id": annex_id, "file": os.path.basename(path), "path": os.path.abspath(path), "kind": "", "warnings": [], "pages": []}
    try:
        if ext == ".pdf":
            with open(path, "rb") as f:
                data = f.read()
            res = pdf_text.extract(data)
            item["kind"] = "pdf"
            item["warnings"] = list(res.get("warnings", []))
            if not res.get("reliable"):
                item["warnings"].append("pdf text layer unreliable; quotes may not be found")
            item["pages"] = [{"number": p["number"], "text": p.get("text", "")} for p in res.get("pages", [])]
        elif ext in TEXT_KINDS:
            text = _read_text_file(path)
            item["kind"] = TEXT_KINDS[ext]
            lines = _csv_lines(text) if item["kind"] == "csv" else text.splitlines()
            item["pages"] = _paginate(lines)
        elif ext == ".xlsx":
            item["kind"] = "xlsx"
            for n, (name, lines) in enumerate(_xlsx_sheets(path), start=1):
                item["pages"].append({"number": n, "sheet": name, "text": "\n".join(lines)})
        else:
            item["kind"] = "unsupported"
            item["warnings"].append(f"unsupported extension {ext or '(none)'}")
    except Exception as e:  # a broken annex must not stop the reading
        item["kind"] = item["kind"] or "error"
        item["warnings"].append(f"could not read: {e}")
        item["pages"] = []
    item["chars"] = sum(len(p.get("text", "")) for p in item["pages"])
    return item


def read_all(paths):
    annexes = [read_annex(p, f"X{i}") for i, p in enumerate(paths, start=1)]
    readable = [a for a in annexes if a["chars"] > 0]
    return {"annex_count": len(annexes), "readable_count": len(readable), "annexes": annexes}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    missing = [p for p in args.files if not os.path.isfile(p)]
    if missing:
        print(f"annex_text.py: not found: {', '.join(missing)}", file=sys.stderr)
        return 2
    result = read_all(args.files)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps({"annex_count": result["annex_count"], "readable_count": result["readable_count"],
                      "annexes": [{"id": a["id"], "file": a["file"], "kind": a["kind"], "pages": len(a["pages"]), "chars": a["chars"]} for a in result["annexes"]]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

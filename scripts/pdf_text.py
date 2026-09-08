#!/usr/bin/env python3
"""Extract the raw text of each PDF page without any model. Standard library only.

Usage:
    pdf_text.py DECK.pdf --out pdf-text.json

Output:
    {"source": "pdf", "reliable": true|false, "page_count": N, "warnings": [...],
     "pages": [{"number": 1, "text": "..."}, ...]}

This is the ground truth used by verify_quotes.py. It handles the common cases of
text-based decks: Flate-compressed content streams, object streams, simple fonts with
WinAnsi/standard encodings, and composite fonts carrying a ToUnicode CMap (Canva, Google
Slides, Keynote, PowerPoint exports). It does not handle scanned decks (images only),
fonts without a ToUnicode map, or exotic filters. When the result looks unreliable the
"reliable" flag is false and the orchestrator falls back to the model transcription.
"""
import argparse
import json
import re
import sys
import zlib

MIN_CHARS_PER_PAGE = 20  # below this average, extraction is declared unreliable

OBJ_RE = re.compile(rb"(?<![0-9])(\d+)\s+(\d+)\s+obj\b")
REF_RE = re.compile(rb"(\d+)\s+(\d+)\s+R\b")


class PdfError(Exception):
    pass


# ---------------------------------------------------------------- low-level object model

def _find_dict_end(data, start):
    """Return the index just after the dictionary starting at data[start:] ('<<')."""
    depth = 0
    i = start
    n = len(data)
    while i < n:
        if data.startswith(b"<<", i):
            depth += 1
            i += 2
        elif data.startswith(b">>", i):
            depth -= 1
            i += 2
            if depth == 0:
                return i
        elif data[i:i + 1] == b"(":
            i = _skip_string(data, i)
        elif data[i:i + 1] == b"%":
            j = data.find(b"\n", i)
            i = n if j < 0 else j + 1
        else:
            i += 1
    return n


def _skip_string(data, i):
    depth = 0
    n = len(data)
    while i < n:
        c = data[i:i + 1]
        if c == b"\\":
            i += 2
            continue
        if c == b"(":
            depth += 1
        elif c == b")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


class Obj:
    __slots__ = ("raw", "dict", "stream")

    def __init__(self, raw, dictionary, stream):
        self.raw = raw
        self.dict = dictionary
        self.stream = stream


def _parse_object_body(body):
    """Split an object body into (dict bytes or None, stream bytes or None)."""
    body = body.strip()
    dictionary = None
    stream = None
    if body.startswith(b"<<"):
        end = _find_dict_end(body, 0)
        dictionary = body[:end]
        rest = body[end:]
        m = re.match(rb"\s*stream\r?\n", rest)
        if m:
            stream = rest[m.end():]
            length = _dict_int(dictionary, b"Length")
            if length is not None and length <= len(stream):
                candidate = stream[:length]
                if re.match(rb"\s*endstream", stream[length:]):
                    stream = candidate
                else:
                    stream = _cut_endstream(stream)
            else:
                stream = _cut_endstream(stream)
    return dictionary, stream


def _cut_endstream(stream):
    j = stream.rfind(b"endstream")
    if j < 0:
        return stream
    return stream[:j].rstrip(b"\r\n")


def _dict_int(dictionary, key):
    m = re.search(rb"/" + key + rb"\s+(\d+)(?!\s+\d+\s+R)", dictionary or b"")
    return int(m.group(1)) if m else None


def _dict_ref(dictionary, key):
    m = re.search(rb"/" + key + rb"\s+(\d+)\s+(\d+)\s+R", dictionary or b"")
    return int(m.group(1)) if m else None


def _dict_name(dictionary, key):
    m = re.search(rb"/" + key + rb"\s*/([^\s/\[\]<>()]+)", dictionary or b"")
    return m.group(1).decode("latin-1") if m else None


def _dict_value(dictionary, key):
    """Return the raw bytes of the value for key (ref, name, array or nested dict)."""
    m = re.search(rb"/" + key + rb"(?=[\s/\[<(])", dictionary or b"")
    if not m:
        return None
    i = m.end()
    data = dictionary
    while i < len(data) and data[i:i + 1].isspace():
        i += 1
    if data.startswith(b"<<", i):
        return data[i:_find_dict_end(data, i)]
    if data[i:i + 1] == b"[":
        depth = 0
        j = i
        while j < len(data):
            if data[j:j + 1] == b"[":
                depth += 1
            elif data[j:j + 1] == b"]":
                depth -= 1
                if depth == 0:
                    return data[i:j + 1]
            j += 1
        return data[i:]
    m2 = re.match(rb"(\d+\s+\d+\s+R|/[^\s/\[\]<>()]+|[^\s/\[\]<>()]+)", data[i:])
    return m2.group(1) if m2 else None


def _decode_stream(dictionary, stream, warnings):
    filt = _dict_value(dictionary, b"Filter")
    if filt is None:
        return stream
    names = re.findall(rb"/([A-Za-z0-9]+)", filt)
    data = stream
    for name in names:
        if name == b"FlateDecode":
            try:
                data = zlib.decompress(data)
            except zlib.error:
                try:
                    data = zlib.decompressobj().decompress(data)
                except zlib.error:
                    warnings.append("flate_decode_failed")
                    return b""
        elif name in (b"ASCIIHexDecode",):
            hexdata = re.sub(rb"[^0-9A-Fa-f]", b"", data.split(b">")[0])
            data = bytes.fromhex(hexdata.decode("ascii"))
        else:
            warnings.append(f"unsupported_filter:{name.decode('latin-1')}")
            return b""
    return data


class Pdf:
    def __init__(self, data):
        self.data = data
        self.objects = {}
        self.warnings = []
        self._scan_objects()
        self._expand_object_streams()

    def _scan_objects(self):
        positions = [(m.start(), int(m.group(1))) for m in OBJ_RE.finditer(self.data)]
        for idx, (pos, num) in enumerate(positions):
            end = positions[idx + 1][0] if idx + 1 < len(positions) else len(self.data)
            body = self.data[pos:end]
            body = body[body.find(b"obj") + 3:]
            j = body.rfind(b"endobj")
            if j >= 0:
                body = body[:j]
            dictionary, stream = _parse_object_body(body)
            # Later definitions win (incremental updates append new versions).
            self.objects[num] = Obj(body, dictionary, stream)

    def _expand_object_streams(self):
        for num in list(self.objects):
            obj = self.objects[num]
            if obj.dict and _dict_name(obj.dict, b"Type") == "ObjStm" and obj.stream is not None:
                raw = _decode_stream(obj.dict, obj.stream, self.warnings)
                if not raw:
                    continue
                n = _dict_int(obj.dict, b"N") or 0
                first = _dict_int(obj.dict, b"First") or 0
                header = raw[:first].split()
                pairs = [(int(header[i]), int(header[i + 1])) for i in range(0, min(len(header), 2 * n), 2)]
                for k, (onum, off) in enumerate(pairs):
                    start = first + off
                    end = first + pairs[k + 1][1] if k + 1 < len(pairs) else len(raw)
                    body = raw[start:end]
                    if onum not in self.objects:
                        dictionary, stream = _parse_object_body(body)
                        self.objects[onum] = Obj(body, dictionary, stream)

    def get(self, num):
        return self.objects.get(num)

    def resolve(self, value):
        """If value is a reference, return the referenced object's raw body/dict; else value."""
        if value is None:
            return None
        m = re.fullmatch(rb"\s*(\d+)\s+\d+\s+R\s*", value)
        if m:
            obj = self.get(int(m.group(1)))
            if obj is None:
                return None
            return obj.dict if obj.dict is not None else obj.raw.strip()
        return value

    # ------------------------------------------------------------ page tree

    def page_objects(self):
        root = None
        trailer_root = re.findall(rb"/Root\s+(\d+)\s+\d+\s+R", self.data)
        if trailer_root:
            root = self.get(int(trailer_root[-1]))
        if root is None:
            for obj in self.objects.values():
                if obj.dict and _dict_name(obj.dict, b"Type") == "Catalog":
                    root = obj
                    break
        pages = []
        if root is not None:
            pages_ref = _dict_ref(root.dict, b"Pages")
            if pages_ref is not None:
                self._walk_pages(pages_ref, pages, set())
        if not pages:
            self.warnings.append("page_tree_not_found")
            for num in sorted(self.objects):
                obj = self.objects[num]
                if obj.dict and _dict_name(obj.dict, b"Type") == "Page":
                    pages.append(num)
        return pages

    def _walk_pages(self, num, out, seen):
        if num in seen:
            return
        seen.add(num)
        obj = self.get(num)
        if obj is None or obj.dict is None:
            return
        t = _dict_name(obj.dict, b"Type")
        if t == "Page":
            out.append(num)
            return
        kids = _dict_value(obj.dict, b"Kids")
        if kids:
            for m in REF_RE.finditer(kids):
                self._walk_pages(int(m.group(1)), out, seen)

    def inherited(self, num, key):
        seen = set()
        while num is not None and num not in seen:
            seen.add(num)
            obj = self.get(num)
            if obj is None or obj.dict is None:
                return None
            val = _dict_value(obj.dict, key)
            if val is not None:
                return val
            num = _dict_ref(obj.dict, b"Parent")
        return None

    # ------------------------------------------------------------ fonts

    def fonts_for_page(self, num):
        """Map resource name (e.g. 'F1') -> decoder callable(bytes) -> str."""
        resources = self.resolve(self.inherited(num, b"Resources"))
        fonts = {}
        if not resources:
            return fonts
        font_dict = self.resolve(_dict_value(resources, b"Font"))
        if not font_dict:
            return fonts
        inner = font_dict[2:-2] if font_dict.startswith(b"<<") else font_dict
        for m in re.finditer(rb"/([^\s/\[\]<>()]+)\s+(\d+)\s+\d+\s+R", inner):
            name = m.group(1).decode("latin-1")
            fonts[name] = self._font_decoder(int(m.group(2)))
        for m in re.finditer(rb"/([^\s/\[\]<>()]+)\s+(<<.*?>>)", inner, re.S):
            name = m.group(1).decode("latin-1")
            if name not in fonts:
                fonts[name] = self._decoder_from_dict(m.group(2))
        return fonts

    def _font_decoder(self, num):
        obj = self.get(num)
        if obj is None or obj.dict is None:
            return _simple_decoder("cp1252", 1)
        return self._decoder_from_dict(obj.dict)

    def _decoder_from_dict(self, fdict):
        tu_ref = _dict_ref(fdict, b"ToUnicode")
        if tu_ref is not None:
            tu = self.get(tu_ref)
            if tu is not None and tu.stream is not None:
                cmap = _decode_stream(tu.dict, tu.stream, self.warnings)
                mapping, code_len = _parse_cmap(cmap)
                if mapping:
                    return _cmap_decoder(mapping, code_len)
        subtype = _dict_name(fdict, b"Subtype")
        if subtype == "Type0":
            self.warnings.append("type0_font_without_tounicode")
            return _simple_decoder("utf-16-be", 2)
        enc = _dict_value(fdict, b"Encoding")
        enc_name = None
        if enc:
            resolved = self.resolve(enc)
            if resolved and resolved.startswith(b"<<"):
                enc_name = _dict_name(resolved, b"BaseEncoding")
            elif resolved:
                enc_name = resolved.decode("latin-1").strip("/ ")
        if enc_name == "MacRomanEncoding":
            return _simple_decoder("mac_roman", 1)
        return _simple_decoder("cp1252", 1)


def _simple_decoder(codec, code_len):
    def decode(raw):
        try:
            return raw.decode(codec, errors="replace")
        except LookupError:
            return raw.decode("latin-1", errors="replace")
    decode.code_len = code_len
    return decode


def _cmap_decoder(mapping, code_len):
    def decode(raw):
        out = []
        i = 0
        while i < len(raw):
            chunk = raw[i:i + code_len]
            code = int.from_bytes(chunk, "big")
            if code in mapping:
                out.append(mapping[code])
            elif code_len == 1:
                out.append(chunk.decode("cp1252", errors="replace"))
            else:
                out.append("�")
            i += code_len
        return "".join(out)
    decode.code_len = code_len
    return decode


def _parse_cmap(cmap):
    """Parse a ToUnicode CMap into {code: str}. Returns (mapping, code byte length)."""
    mapping = {}
    code_len = 1
    m = re.search(rb"begincodespacerange(.*?)endcodespacerange", cmap, re.S)
    if m:
        hexes = re.findall(rb"<([0-9A-Fa-f]+)>", m.group(1))
        if hexes:
            code_len = max(1, len(hexes[0]) // 2)

    def uni(hexstr):
        b = bytes.fromhex(hexstr.decode("ascii"))
        if len(b) % 2:
            b = b"\x00" + b
        return b.decode("utf-16-be", errors="replace")

    for block in re.findall(rb"beginbfchar(.*?)endbfchar", cmap, re.S):
        for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
            code_len = max(code_len, len(src) // 2)
            mapping[int(src, 16)] = uni(dst)
    for block in re.findall(rb"beginbfrange(.*?)endbfrange", cmap, re.S):
        for lo, hi, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
            code_len = max(code_len, len(lo) // 2)
            lo_i, hi_i = int(lo, 16), int(hi, 16)
            base = uni(dst)
            if hi_i - lo_i > 65535:
                continue
            for k, code in enumerate(range(lo_i, hi_i + 1)):
                if base:
                    mapping[code] = base[:-1] + chr(ord(base[-1]) + k)
        for lo, hi, arr in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*\[(.*?)\]", block, re.S):
            code_len = max(code_len, len(lo) // 2)
            dsts = re.findall(rb"<([0-9A-Fa-f]+)>", arr)
            for k, dst in enumerate(dsts):
                mapping[int(lo, 16) + k] = uni(dst)
    return mapping, code_len


# ---------------------------------------------------------------- content stream

_ESCAPES = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f",
            b"(": b"(", b")": b")", b"\\": b"\\"}


def _unescape(raw):
    out = bytearray()
    i = 0
    n = len(raw)
    while i < n:
        c = raw[i:i + 1]
        if c == b"\\" and i + 1 < n:
            nxt = raw[i + 1:i + 2]
            if nxt in _ESCAPES:
                out += _ESCAPES[nxt]
                i += 2
            elif nxt.isdigit():
                j = i + 1
                while j < n and j < i + 4 and raw[j:j + 1].isdigit():
                    j += 1
                out.append(int(raw[i + 1:j], 8) & 0xFF)
                i = j
            elif nxt in (b"\n", b"\r"):
                i += 2
                if nxt == b"\r" and raw[i:i + 1] == b"\n":
                    i += 1
            else:
                out += nxt
                i += 2
        else:
            out += c
            i += 1
    return bytes(out)


def _tokenize(content):
    """Yield ('str', bytes) | ('num', float) | ('name', str) | ('op', str) | ('arr_open'/'arr_close', None)."""
    i = 0
    n = len(content)
    while i < n:
        c = content[i:i + 1]
        if c.isspace():
            i += 1
        elif c == b"%":
            j = content.find(b"\n", i)
            i = n if j < 0 else j + 1
        elif c == b"(":
            j = _skip_string(content, i)
            yield ("str", _unescape(content[i + 1:j - 1]))
            i = j
        elif c == b"<":
            if content.startswith(b"<<", i):
                j = _find_dict_end(content, i)
                i = j
            else:
                j = content.find(b">", i)
                if j < 0:
                    j = n
                hexdata = re.sub(rb"[^0-9A-Fa-f]", b"", content[i + 1:j])
                if len(hexdata) % 2:
                    hexdata += b"0"
                yield ("str", bytes.fromhex(hexdata.decode("ascii")))
                i = j + 1
        elif c == b"[":
            yield ("arr_open", None)
            i += 1
        elif c == b"]":
            yield ("arr_close", None)
            i += 1
        elif c == b"/":
            m = re.match(rb"/([^\s/\[\]<>()%]*)", content[i:])
            yield ("name", m.group(1).decode("latin-1"))
            i += m.end()
        elif c == b"{" or c == b"}":
            i += 1
        else:
            m = re.match(rb"[+-]?(\d+\.?\d*|\.\d+)", content[i:])
            if m:
                yield ("num", float(m.group(0)))
                i += m.end()
            else:
                m = re.match(rb"[^\s\[\]<>()/%{}]+", content[i:])
                if not m:
                    i += 1
                    continue
                yield ("op", m.group(0).decode("latin-1"))
                i += m.end()


def extract_page_text(content, fonts):
    """Walk a content stream and return the text with line breaks at text-position changes."""
    out = []
    operands = []
    array = None
    decoder = _simple_decoder("cp1252", 1)
    font_size = 1.0
    last_y = None

    def emit(text):
        out.append(text)

    for kind, value in _tokenize(content):
        if kind == "arr_open":
            array = []
            continue
        if kind == "arr_close":
            operands.append(("arr", array))
            array = None
            continue
        if array is not None:
            array.append((kind, value))
            continue
        if kind != "op":
            operands.append((kind, value))
            continue

        op = value
        if op == "Tf":
            names = [v for k, v in operands if k == "name"]
            nums = [v for k, v in operands if k == "num"]
            if names:
                decoder = fonts.get(names[-1], decoder)
            if nums:
                font_size = nums[-1] or 1.0
        elif op in ("Tj", "'", '"'):
            if op != "Tj":
                emit("\n")
            strs = [v for k, v in operands if k == "str"]
            if strs:
                emit(decoder(strs[-1]))
        elif op == "TJ":
            for k, v in operands:
                if k == "arr":
                    for ik, iv in v:
                        if ik == "str":
                            emit(decoder(iv))
                        elif ik == "num" and iv < -180:
                            emit(" ")
        elif op == "T*":
            emit("\n")
        elif op in ("Td", "TD"):
            nums = [v for k, v in operands if k == "num"]
            if len(nums) >= 2:
                if abs(nums[1]) > 0.01:
                    emit("\n")
                elif nums[0] > 0.01:
                    emit(" ")
        elif op == "Tm":
            nums = [v for k, v in operands if k == "num"]
            if len(nums) >= 6:
                y = nums[5]
                if last_y is None or abs(y - last_y) > 0.01 * max(font_size, 1):
                    emit("\n")
                else:
                    emit(" ")
                last_y = y
        elif op == "ET":
            emit("\n")
        operands = []

    text = "".join(out)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract(data):
    pdf = Pdf(data)
    pages = []
    for idx, num in enumerate(pdf.page_objects(), start=1):
        obj = pdf.get(num)
        contents = _dict_value(obj.dict, b"Contents") if obj and obj.dict else None
        streams = []
        if contents:
            refs = [int(m.group(1)) for m in REF_RE.finditer(contents)]
            for r in refs:
                cobj = pdf.get(r)
                if cobj is not None and cobj.stream is not None:
                    streams.append(_decode_stream(cobj.dict, cobj.stream, pdf.warnings))
        content = b"\n".join(streams)
        fonts = pdf.fonts_for_page(num)
        text = extract_page_text(content, fonts) if content else ""
        pages.append({"number": idx, "text": text})

    total_chars = sum(len(p["text"]) for p in pages)
    replacement_ratio = (sum(p["text"].count("�") for p in pages) / total_chars) if total_chars else 1.0
    reliable = bool(pages) and total_chars / len(pages) >= MIN_CHARS_PER_PAGE and replacement_ratio < 0.02 \
        and not any(w.startswith("unsupported_filter") or w == "type0_font_without_tounicode" for w in pdf.warnings)
    return {
        "source": "pdf",
        "reliable": reliable,
        "page_count": len(pages),
        "warnings": sorted(set(pdf.warnings)),
        "pages": pages,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    with open(args.pdf, "rb") as f:
        data = f.read()
    if not data.startswith(b"%PDF"):
        print("pdf_text.py: not a PDF file", file=sys.stderr)
        return 2
    result = extract(data)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in result.items() if k != "pages"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

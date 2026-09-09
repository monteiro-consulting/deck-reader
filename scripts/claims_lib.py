#!/usr/bin/env python3
"""Shared helpers for the seed claim pipeline. Standard library only.

A claim is one verifiable statement the deck makes, with its page and verbatim quote:

    {"id": "K01", "page": 6, "quote": "...", "type": "revenue",
     "statement": "MRR of 12,000 EUR in August 2026", "value": 12000, "unit": "EUR/month",
     "date": "2026-08"}

Statuses, from best to worst, as set by code after verification:

    proven        an annex backs it (gap minor or none)
    confirmed     the web backs it with enough independent sources
    not_covered   no annex covers it (annex check)
    unverifiable  the web could not settle it (web check); a valid state, never "probably false"
    to_probe      a gap that has a plausible explanation; becomes a question for the call
    blatant       a gap that cannot be reconciled, or a fact that does not exist; stops the reading
                  unless the reviewer finds an honest explanation

classify_gap(deck_value, found_value, grid) applies the thresholds written in grid["gaps"].
"""
import json
from urllib.parse import urlparse

SEVERITY = {"proven": 0, "confirmed": 0, "not_covered": 1, "unverifiable": 1, "to_probe": 2, "blatant": 3}
OK_STATUSES = {"proven", "confirmed"}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def to_number(x):
    if x is None or isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(" ", "").replace(" ", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def classify_gap(deck_value, found_value, grid):
    """Return (gap_class, ratio). gap_class in minor / to_probe / blatant, or None when not numeric."""
    d = to_number(deck_value)
    f = to_number(found_value)
    if d is None or f is None:
        return None, None
    ratio = abs(d - f) / max(abs(f), 1.0)
    gaps = grid.get("gaps") or {}
    if ratio <= float(gaps.get("minor_max_ratio", 0.25)):
        return "minor", round(ratio, 4)
    if ratio <= float(gaps.get("probe_max_ratio", 1.0)):
        return "to_probe", round(ratio, 4)
    return "blatant", round(ratio, 4)


def domain_of(url):
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


def distinct_domains(sources):
    return {domain_of(s.get("url", "")) for s in (sources or []) if domain_of(s.get("url", ""))}


def worst(*statuses):
    statuses = [s for s in statuses if s]
    if not statuses:
        return None
    return max(statuses, key=lambda s: SEVERITY.get(s, 1))


def claim_check_mode(claim, grid):
    types = grid.get("claim_types") or {}
    return (types.get(claim.get("type")) or types.get("other") or {}).get("check", "none")


def claim_proof_text(claim, grid):
    types = grid.get("claim_types") or {}
    return (types.get(claim.get("type")) or {}).get("proof", "")

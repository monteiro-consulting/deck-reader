#!/usr/bin/env python3
"""Assemble the final markdown report from the answers, the score and the writer's reading.

Standard library only. No model is involved: this script only lays out what it is given.

Usage:
    report.py --deck DECK.pdf --profile profile.json --answers-dir DIR --score score.json
              --reading reading.md --pages pages.json --lang fr --out DECK.preseed-reading.md
    report.py --deck DECK.pdf --profile profile.json --lang fr --out ... --abort-reason "..."

--lang selects the labels. Shipped: en, fr. Any other code falls back to English labels;
the writer's prose (reading.md) is in whatever language the orchestrator requested.
The grid question wording follows the same rule (grid.json carries en and fr).
"""
import argparse
import datetime as dt
import json
import os
import sys

LABELS = {
    "en": {
        "title": "Deck completeness reading",
        "stage": "Stage",
        "grid_version": "Grid version",
        "read_on": "Read on",
        "reference": "Quotes verified against",
        "reference_pdf": "PDF text layer",
        "reference_transcription": "model transcription (PDF text layer unusable)",
        "disclaimer": "This report measures the completeness of the deck against the pre-seed grid: whether the deck answers the questions an investor will ask. It does not measure the quality of the company. It contains no verdict, no rating and no investment recommendation.",
        "image_note": "Text that only appears inside images (charts, screenshots) is not in the PDF text layer and cannot be cited; it is treated as absent.",
        "profile": "Deck profile",
        "sector": "Sector",
        "business_model": "Business model",
        "customer_type": "Customer type",
        "announced_stage": "Announced stage",
        "deck_language": "Deck language",
        "pages": "Pages",
        "completeness": "Deck completeness",
        "block": "Block",
        "weight": "weight",
        "global": "Global (weighted)",
        "red_blocks": "Red blocks (below {threshold} %)",
        "no_red_blocks": "No red block.",
        "red_flags": "Stage red signals (absent)",
        "reading": "Reading",
        "by_question": "Question by question",
        "question": "Question",
        "value": "Value",
        "page": "Page",
        "quote": "Quote",
        "missing": "Missing",
        "to_ask": "To ask",
        "found": "found",
        "partial": "partial",
        "absent": "absent",
        "not_assessable": "not assessable",
        "information_only": "for information",
        "quote_rejected": "quote rejected by verification",
        "passes_one": "Checker passes: 1 (completeness outside the confirmation band {threshold} %)",
        "passes_many": "Checker passes: {n} (confirmation triggered, completeness within {threshold} %; each value is the median of the passes)",
        "unstable": "unstable",
        "unstable_note": "Unstable questions (passes disagreed)",
        "abort_title": "Deck not read",
        "abort_reason": "Reason",
        "abort_body": "This reader only applies the pre-seed grid. It does not score a deck of another stage, because the questions and weights would not fit. No completeness score was computed.",
        "page_abbrev": "p.",
    },
    "fr": {
        "title": "Lecture de complétude du deck",
        "stage": "Stade",
        "grid_version": "Version de la grille",
        "read_on": "Lu le",
        "reference": "Extraits vérifiés contre",
        "reference_pdf": "la couche texte du PDF",
        "reference_transcription": "la transcription par le modèle (couche texte du PDF inutilisable)",
        "disclaimer": "Ce rapport mesure la complétude du deck au regard de la grille pre-seed : le deck répond-il aux questions qu'un investisseur va poser. Il ne mesure pas la qualité de l'entreprise. Il ne contient ni verdict, ni note, ni recommandation d'investissement.",
        "image_note": "Le texte qui n'apparaît que dans des images (graphiques, captures) n'est pas dans la couche texte du PDF et ne peut pas être cité ; il est traité comme absent.",
        "profile": "Fiche du deck",
        "sector": "Secteur",
        "business_model": "Modèle économique",
        "customer_type": "Type de client",
        "announced_stage": "Stade annoncé",
        "deck_language": "Langue du deck",
        "pages": "Pages",
        "completeness": "Complétude du deck",
        "block": "Bloc",
        "weight": "poids",
        "global": "Global (pondéré)",
        "red_blocks": "Blocs rouges (sous {threshold} %)",
        "no_red_blocks": "Aucun bloc rouge.",
        "red_flags": "Signaux rouges du stade (absents)",
        "reading": "Lecture",
        "by_question": "Question par question",
        "question": "Question",
        "value": "Valeur",
        "page": "Page",
        "quote": "Extrait",
        "missing": "Manque",
        "to_ask": "À demander",
        "found": "trouvée",
        "partial": "partielle",
        "absent": "absente",
        "not_assessable": "non évaluable",
        "information_only": "pour information",
        "quote_rejected": "extrait rejeté à la vérification",
        "passes_one": "Passes de vérification : 1 (complétude hors de la bande de confirmation {threshold} %)",
        "passes_many": "Passes de vérification : {n} (confirmation déclenchée, complétude dans la bande {threshold} % ; chaque valeur est la médiane des passes)",
        "unstable": "instable",
        "unstable_note": "Questions instables (les passes ont divergé)",
        "abort_title": "Deck non lu",
        "abort_reason": "Raison",
        "abort_body": "Ce lecteur n'applique que la grille pre-seed. Il ne note pas un deck d'un autre stade, parce que les questions et les poids ne conviendraient pas. Aucun score de complétude n'a été calculé.",
        "page_abbrev": "p.",
    },
}

SYMBOL = {"found": "🟢", "partial": "🟠", "absent": "🔴", "not_assessable": "⚪", "information_only": "⚪"}
BAR_WIDTH = 20


def L(lang):
    return LABELS.get(lang, LABELS["en"])


def bar(percent):
    filled = int(round(percent / 100 * BAR_WIDTH))
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def md_cell(text):
    return str(text or "").replace("|", "\\|").replace("\n", " ").strip()


def pick(d, lang):
    if isinstance(d, dict):
        return d.get(lang) or d.get("en") or next(iter(d.values()), "")
    return d or ""


def evidence_str(profile, key, lab):
    ev = (profile.get("evidence") or {}).get(key) or []
    parts = []
    for e in ev[:2]:
        if e.get("page") is not None and e.get("quote"):
            parts.append(f'{lab["page_abbrev"]} {e["page"]}: "{e["quote"]}"')
    return " · ".join(parts)


def header(lab, deck, grid, date, reference_source):
    lines = [f"# {lab['title']}: {os.path.basename(deck)}", ""]
    meta = [f"**{lab['stage']}**: {grid['stage']}", f"**{lab['grid_version']}**: {grid['version']}", f"**{lab['read_on']}**: {date}"]
    if reference_source:
        ref = lab["reference_pdf"] if reference_source == "pdf" else lab["reference_transcription"]
        meta.append(f"**{lab['reference']}**: {ref}")
    lines.append(" · ".join(meta))
    lines.append("")
    lines.append(f"> {lab['disclaimer']}")
    if reference_source == "pdf":
        lines.append(">")
        lines.append(f"> {lab['image_note']}")
    lines.append("")
    return lines


def profile_section(lab, profile):
    lines = [f"## {lab['profile']}", ""]
    for key in ("sector", "business_model", "customer_type", "announced_stage", "deck_language"):
        val = profile.get(key, "")
        ev = evidence_str(profile, key, lab)
        line = f"- **{lab[key]}**: {val}"
        if ev:
            line += f" ({ev})"
        lines.append(line)
    if profile.get("page_count"):
        lines.append(f"- **{lab['pages']}**: {profile['page_count']}")
    lines.append("")
    return lines


def completeness_section(lab, grid, score, lang):
    threshold = grid.get("red_block_threshold_percent", 50)
    lines = [f"## {lab['completeness']}", "", f"| {lab['block']} | | % |", "|---|---|---:|"]
    for b in score["blocks"]:
        name = f"{b['id']}. {pick(b['name'], lang)} ({lab['weight']} {b['weight']})"
        lines.append(f"| {name} | `{bar(b['percent'])}` | {fmt_pct(b['percent'])} |")
    lines.append(f"| **{lab['global']}** | `{bar(score['global_percent'])}` | **{fmt_pct(score['global_percent'])}** |")
    lines.append("")
    if score["red_blocks"]:
        names = ", ".join(f"{b['id']}. {pick(b['name'], lang)}" for b in score["blocks"] if b["id"] in score["red_blocks"])
        lines.append(f"**{lab['red_blocks'].format(threshold=threshold)}**: {names}")
    else:
        lines.append(lab["no_red_blocks"])
    if score.get("red_flags"):
        lines.append("")
        lines.append(f"**{lab['red_flags']}**: {', '.join(score['red_flags'])}")
    conf = grid.get("confirmation") or {}
    n_passes = score.get("passes", 1)
    if conf:
        lines.append("")
        key = "passes_many" if n_passes > 1 else "passes_one"
        lo, hi = conf.get("trigger_min_percent"), conf.get("trigger_max_percent")
        band = f"{lo}-{hi}" if lo is not None and hi is not None else (f">= {lo}" if lo is not None else f"<= {hi}")
        lines.append(lab[key].format(n=n_passes, threshold=band))
        if score.get("unstable"):
            lines.append("")
            lines.append(f"**{lab['unstable_note']}**: {', '.join(score['unstable'])}")
    lines.append("")
    return lines


def fmt_pct(x):
    return f"{int(x)} %" if float(x).is_integer() else f"{x:.1f} %"


def reading_section(lab, reading_text):
    lines = [f"## {lab['reading']}", ""]
    lines.append(reading_text.strip())
    lines.append("")
    return lines


def questions_section(lab, grid, score, answers, lang):
    by_id = {a["question_id"]: a for a in answers}
    sq = {q["question_id"]: q for q in score["questions"]}
    lines = [f"## {lab['by_question']}", ""]
    for block in grid["blocks"]:
        sb = next(b for b in score["blocks"] if b["id"] == block["id"])
        lines.append(f"### {block['id']}. {pick(block['name'], lang)} — {lab['weight']} {block['weight']} — {fmt_pct(sb['percent'])}")
        lines.append("")
        lines.append(f"| # | {lab['question']} | {lab['value']} | {lab['page']} | {lab['quote']} |")
        lines.append("|---|---|---|---|---|")
        details = []
        for q in block["questions"]:
            qid = q["id"]
            a = by_id.get(qid, {})
            s = sq.get(qid, {})
            status = s.get("status", "counted")
            value = a.get("value", "absent")
            if status in ("not_assessable", "information_only"):
                label = f"{SYMBOL[status]} {lab[status]}"
                if status == "information_only":
                    label += f" ({lab[value]})"
            else:
                label = f"{SYMBOL.get(value, '')} {lab.get(value, value)}"
            if a.get("quote_invalid"):
                label += f" ({lab['quote_rejected']})"
            if a.get("passes") and not a.get("stable", True):
                readings = ", ".join(lab.get(v, v) for v in a["passes"])
                label += f" ⚠ {lab['unstable']} ({readings})"
            evidence = a.get("evidence") or []
            pages = ", ".join(dict.fromkeys(str(e.get("page")) for e in evidence)) if evidence else "—"
            quotes = " / ".join(f'"{md_cell(e.get("quote"))}"' for e in evidence) if evidence else "—"
            lines.append(f"| {qid} | {md_cell(pick(q['question'], lang))} | {label} | {pages} | {quotes} |")
            if value in ("partial", "absent") and status != "not_assessable":
                d = []
                if a.get("missing"):
                    d.append(f"**{lab['missing']}**: {a['missing'].strip()}")
                if a.get("call_question"):
                    d.append(f"**{lab['to_ask']}**: {a['call_question'].strip()}")
                if d:
                    details.append(f"- **{qid}** — " + " ".join(d))
        lines.append("")
        if details:
            lines.extend(details)
            lines.append("")
    return lines


def abort_report(lab, deck, grid, profile, date, reason):
    lines = header(lab, deck, grid, date, None)
    lines += [f"## {lab['abort_title']}", "", f"**{lab['abort_reason']}**: {reason}", "", lab["abort_body"], ""]
    lines += profile_section(lab, profile)
    return "\n".join(lines)


def full_report(lab, deck, grid, profile, answers, score, reading, pages_meta, date, lang):
    reference_source = (pages_meta or {}).get("reference_source", "")
    lines = header(lab, deck, grid, date, reference_source)
    lines += profile_section(lab, profile)
    lines += completeness_section(lab, grid, score, lang)
    lines += reading_section(lab, reading)
    lines += questions_section(lab, grid, score, answers, lang)
    return "\n".join(lines)


def load_answers(answers_dir):
    import glob
    answers = []
    for path in sorted(glob.glob(os.path.join(answers_dir, "block-*.json"))):
        with open(path, encoding="utf-8") as f:
            answers.extend(json.load(f).get("answers", []))
    return answers


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "grid.json"))
    ap.add_argument("--deck", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--answers-dir")
    ap.add_argument("--score")
    ap.add_argument("--reading")
    ap.add_argument("--pages", help="pages.json, for the reference_source header line")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--abort-reason", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    lab = L(args.lang)
    with open(args.grid, encoding="utf-8") as f:
        grid = json.load(f)
    with open(args.profile, encoding="utf-8") as f:
        profile = json.load(f)

    if args.abort_reason:
        text = abort_report(lab, args.deck, grid, profile, args.date, args.abort_reason)
    else:
        for name in ("answers_dir", "score", "reading"):
            if not getattr(args, name):
                print(f"report.py: --{name.replace('_', '-')} is required unless --abort-reason is given", file=sys.stderr)
                return 2
        with open(args.score, encoding="utf-8") as f:
            score = json.load(f)
        with open(args.reading, encoding="utf-8") as f:
            reading = f.read()
        pages_meta = None
        if args.pages:
            with open(args.pages, encoding="utf-8") as f:
                pages_meta = json.load(f)
        answers = load_answers(args.answers_dir)
        text = full_report(lab, args.deck, grid, profile, answers, score, reading, pages_meta, args.date, args.lang)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

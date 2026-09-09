#!/usr/bin/env python3
"""Assemble the final markdown report from the answers, the score and the writer's reading.

Standard library only. No model is involved: this script only lays out what it is given.

Usage (full report, any stage):
    report.py --grid seed --deck DECK.pdf --profile profile.json --answers-dir DIR --score score.json
              --reading reading.md --pages pages.json --lang fr --out DECK.reading.md
              [--claims claims.final.json --annexes annexes.json --gate gate.json --email email.md]

Usage (reading stopped):
    report.py --grid seed --deck DECK.pdf --profile profile.json --lang fr --out ...
              --abort-kind stage|no_annexes|insufficient_annexes|contradiction --abort-reason "..."
              [--claims ... --annexes ... --gate ... --email ...]

--grid is a stage name (preseed, seed) or a path. --lang selects the labels. Shipped: en, fr.
Any other code falls back to English labels; the writer's prose (reading.md) is in whatever
language the orchestrator requested. Grid question wording follows the same rule.
"""
import argparse
import datetime as dt
import glob
import json
import os
import sys

from grid_lib import effective_grid, load_grid

LABELS = {
    "en": {
        "title": "Deck completeness reading",
        "stage": "Stage",
        "grid_version": "Grid version",
        "read_on": "Read on",
        "reference": "Quotes verified against",
        "reference_pdf": "PDF text layer",
        "reference_transcription": "model transcription (PDF text layer unusable)",
        "disclaimer_preseed": "This report measures the completeness of the deck against the pre-seed grid: whether the deck answers the questions an investor will ask. It does not measure the quality of the company. It contains no verdict, no rating and no investment recommendation.",
        "disclaimer_seed": "This report measures the completeness of the deck against the seed grid, and whether what the deck states holds up against the annexes provided and public sources. It does not measure the quality of the company. It contains no verdict, no rating and no investment recommendation. A figure the deck states without a document behind it cannot score higher than partial.",
        "image_note": "Text that only appears inside images (charts, screenshots) is not in the PDF text layer and cannot be cited; it is treated as absent.",
        "profile": "Deck profile",
        "sector": "Sector",
        "business_model": "Business model",
        "model_type": "Model type",
        "customer_type": "Customer type",
        "announced_stage": "Announced stage",
        "deck_language": "Deck language",
        "pages": "Pages",
        "model_questions": "Model-specific questions applied",
        "annexes": "Annexes",
        "no_annexes": "No annex was provided.",
        "annex_line": "{id}: {file} ({kind}, {pages} page(s))",
        "completeness": "Deck completeness",
        "block": "Block",
        "weight": "weight",
        "global": "Global (weighted)",
        "red_blocks": "Red blocks (below {threshold} %)",
        "no_red_blocks": "No red block.",
        "red_flags": "Stage red signals (absent)",
        "reading": "Reading",
        "claims": "What the deck states, and what backs it",
        "claim": "Statement",
        "type": "Type",
        "status": "Status",
        "backing": "Backing",
        "st_proven": "proven by annex",
        "st_confirmed": "confirmed on the web",
        "st_not_covered": "no document covers it",
        "st_unverifiable": "unverifiable",
        "st_to_probe": "gap to probe in the call",
        "st_blatant": "contradicted",
        "st_not_checked": "not checked",
        "gap": "gap {ratio} % ({klass})",
        "deck_says": "deck",
        "found_says": "found",
        "contradictions": "Gaps to probe in the call",
        "no_contradictions": "No gap between the deck and the documents or public sources reached the probing threshold.",
        "contradiction_line": "- **{id}** (p. {page}) - {statement}. {detail}",
        "reviewer_explanation": "Possible explanation found by review",
        "to_request": "Documents still to request",
        "nothing_to_request": "Every annex-checked statement is covered.",
        "email_draft": "Email draft",
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
        "capped": "capped: figure without proof",
        "downgraded": "lowered: cites a gap to probe ({ids})",
        "passes_one": "Checker passes: 1 (completeness outside the confirmation band {threshold} %)",
        "passes_many": "Checker passes: {n} (confirmation triggered, completeness within {threshold} %; each value is the median of the passes)",
        "unstable": "unstable",
        "unstable_note": "Unstable questions (passes disagreed)",
        "abort_title": "Reading stopped",
        "abort_reason": "Reason",
        "abort_stage": "This grid only applies to the stage it was written for. A deck of another stage is not scored with it, because the questions and weights would not fit. No completeness score was computed.",
        "abort_no_annexes": "The deck came without any supporting document. At seed, a figure without a document behind it cannot be read as proven, so the reading stops here. No web check, no grid, no score. The email draft below asks the founder for the documents.",
        "abort_insufficient_annexes": "The documents provided do not cover enough of the key figures the deck states (revenue, customers, retention). The reading stops here, before any web check or scoring. The email draft below lists, statement by statement, what would be needed.",
        "abort_contradiction": "At least one statement of the deck is contradicted by the documents or by public sources, beyond what a different date, definition or source could explain, after a second independent review looked for such an explanation. The reading stops here and shows the sources on both sides. This is not a verdict on the company: the investor sees the evidence and decides. Everything read so far is kept below.",
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
        "disclaimer_preseed": "Ce rapport mesure la complétude du deck au regard de la grille pre-seed : le deck répond-il aux questions qu'un investisseur va poser. Il ne mesure pas la qualité de l'entreprise. Il ne contient ni verdict, ni note, ni recommandation d'investissement.",
        "disclaimer_seed": "Ce rapport mesure la complétude du deck au regard de la grille seed, et si ce que le deck affirme tient face aux annexes fournies et aux sources publiques. Il ne mesure pas la qualité de l'entreprise. Il ne contient ni verdict, ni note, ni recommandation d'investissement. Un chiffre avancé sans document derrière ne peut pas dépasser « partielle ».",
        "image_note": "Le texte qui n'apparaît que dans des images (graphiques, captures) n'est pas dans la couche texte du PDF et ne peut pas être cité ; il est traité comme absent.",
        "profile": "Fiche du deck",
        "sector": "Secteur",
        "business_model": "Modèle économique",
        "model_type": "Type de modèle",
        "customer_type": "Type de client",
        "announced_stage": "Stade annoncé",
        "deck_language": "Langue du deck",
        "pages": "Pages",
        "model_questions": "Questions propres au modèle appliquées",
        "annexes": "Annexes",
        "no_annexes": "Aucune annexe fournie.",
        "annex_line": "{id} : {file} ({kind}, {pages} page(s))",
        "completeness": "Complétude du deck",
        "block": "Bloc",
        "weight": "poids",
        "global": "Global (pondéré)",
        "red_blocks": "Blocs rouges (sous {threshold} %)",
        "no_red_blocks": "Aucun bloc rouge.",
        "red_flags": "Signaux rouges du stade (absents)",
        "reading": "Lecture",
        "claims": "Ce que le deck affirme, et ce qui l'appuie",
        "claim": "Affirmation",
        "type": "Type",
        "status": "Statut",
        "backing": "Appui",
        "st_proven": "prouvée par annexe",
        "st_confirmed": "confirmée sur le web",
        "st_not_covered": "aucun document ne la couvre",
        "st_unverifiable": "invérifiable",
        "st_to_probe": "écart à creuser en call",
        "st_blatant": "contredite",
        "st_not_checked": "non vérifiée",
        "gap": "écart {ratio} % ({klass})",
        "deck_says": "deck",
        "found_says": "trouvé",
        "contradictions": "Écarts à creuser en call",
        "no_contradictions": "Aucun écart entre le deck et les documents ou les sources publiques n'atteint le seuil à creuser.",
        "contradiction_line": "- **{id}** (p. {page}) - {statement}. {detail}",
        "reviewer_explanation": "Explication possible trouvée à la relecture",
        "to_request": "Documents encore à demander",
        "nothing_to_request": "Toutes les affirmations vérifiables par annexe sont couvertes.",
        "email_draft": "Brouillon d'email",
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
        "capped": "plafonnée : chiffre sans preuve",
        "downgraded": "abaissée : cite un écart à creuser ({ids})",
        "passes_one": "Passes de vérification : 1 (complétude hors de la bande de confirmation {threshold} %)",
        "passes_many": "Passes de vérification : {n} (confirmation déclenchée, complétude dans la bande {threshold} % ; chaque valeur est la médiane des passes)",
        "unstable": "instable",
        "unstable_note": "Questions instables (les passes ont divergé)",
        "abort_title": "Lecture interrompue",
        "abort_reason": "Raison",
        "abort_stage": "Cette grille ne s'applique qu'au stade pour lequel elle est écrite. Un deck d'un autre stade n'est pas noté avec, parce que les questions et les poids ne conviendraient pas. Aucun score de complétude n'a été calculé.",
        "abort_no_annexes": "Le deck est arrivé sans aucune pièce justificative. Au seed, un chiffre sans document derrière ne peut pas être lu comme prouvé, donc la lecture s'arrête ici. Pas de vérification web, pas de grille, pas de score. Le brouillon d'email ci-dessous demande les documents au fondateur.",
        "abort_insufficient_annexes": "Les documents fournis ne couvrent pas assez des chiffres clés que le deck avance (revenus, clients, rétention). La lecture s'arrête ici, avant toute vérification web et tout score. Le brouillon d'email ci-dessous liste, affirmation par affirmation, ce qu'il faudrait.",
        "abort_contradiction": "Au moins une affirmation du deck est contredite par les documents ou par des sources publiques, au-delà de ce qu'une date, une définition ou une source différente pourrait expliquer, après qu'une seconde relecture indépendante a cherché une telle explication. La lecture s'arrête ici et montre les sources des deux côtés. Ce n'est pas un verdict sur l'entreprise : l'investisseur voit les preuves et décide. Tout ce qui a été lu est conservé ci-dessous.",
        "page_abbrev": "p.",
    },
}

SYMBOL = {"found": "🟢", "partial": "🟠", "absent": "🔴", "not_assessable": "⚪", "information_only": "⚪"}
CLAIM_SYMBOL = {"proven": "🟢", "confirmed": "🟢", "not_covered": "⚪", "unverifiable": "⚪", "to_probe": "🟠", "blatant": "🔴", "not_checked": "⚪"}
BAR_WIDTH = 20


def L(lang):
    return LABELS.get(lang, LABELS["en"])


def bar(percent):
    filled = int(round(percent / 100 * BAR_WIDTH))
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def md_cell(text):
    return str(text or "").replace("|", "\\|").replace("\n", " ").replace("\t", " ").strip()


def fmt_num(x):
    if x is None:
        return "?"
    try:
        f = float(x)
    except (TypeError, ValueError):
        return str(x)
    return str(int(f)) if f.is_integer() else f"{f:g}"


def pick(d, lang):
    if isinstance(d, dict):
        return d.get(lang) or d.get("en") or next(iter(d.values()), "")
    return d or ""


def fmt_pct(x):
    return f"{int(x)} %" if float(x).is_integer() else f"{x:.1f} %"


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
    key = "disclaimer_seed" if grid["stage"] == "seed" else "disclaimer_preseed"
    lines.append(f"> {lab[key]}")
    if reference_source == "pdf":
        lines.append(">")
        lines.append(f"> {lab['image_note']}")
    lines.append("")
    return lines


def profile_section(lab, profile, grid, annexes):
    lines = [f"## {lab['profile']}", ""]
    keys = ["sector", "business_model", "model_type", "customer_type", "announced_stage", "deck_language"]
    for key in keys:
        val = profile.get(key, "")
        if key == "model_type" and not val:
            continue
        ev = evidence_str(profile, key, lab)
        line = f"- **{lab[key]}**: {val}"
        if ev:
            line += f" ({ev})"
        lines.append(line)
    if profile.get("page_count"):
        lines.append(f"- **{lab['pages']}**: {profile['page_count']}")
    if grid.get("applied_model_questions"):
        lines.append(f"- **{lab['model_questions']}**: {grid['applied_model_questions']}")
    if grid["stage"] == "seed":
        items = (annexes or {}).get("annexes") or []
        if items:
            lines.append(f"- **{lab['annexes']}**: " + "; ".join(lab["annex_line"].format(id=a["id"], file=a["file"], kind=a["kind"], pages=len(a.get("pages", []))) for a in items))
        else:
            lines.append(f"- **{lab['annexes']}**: {lab['no_annexes']}")
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


def reading_section(lab, reading_text):
    return [f"## {lab['reading']}", "", reading_text.strip(), ""]


def _backing(lab, c):
    parts = []
    for e in (c.get("annex_evidence") or [])[:2]:
        parts.append(f'{e.get("annex_id")} {lab["page_abbrev"]} {e.get("page")}: "{md_cell(e.get("quote"))}"')
    for e in (c.get("web_for") or [])[:2]:
        parts.append(f'[{md_cell(e.get("title") or e.get("url"))}]({e.get("url")})')
    for e in (c.get("web_against") or [])[:2]:
        parts.append(f'✗ [{md_cell(e.get("title") or e.get("url"))}]({e.get("url")})')
    if c.get("gap_class") and c.get("gap_ratio") is not None:
        found = c.get("annex_value") if c.get("annex_value") is not None else c.get("web_value")
        parts.append(lab["gap"].format(ratio=round(c["gap_ratio"] * 100), klass=c["gap_class"]) + f" · {lab['deck_says']} {fmt_num(c.get('value'))} / {lab['found_says']} {fmt_num(found)}")
    return " · ".join(parts) if parts else "—"


def claims_section(lab, claims_doc):
    claims = (claims_doc or {}).get("claims") or []
    if not claims:
        return []
    lines = [f"## {lab['claims']}", "", f"| # | {lab['page']} | {lab['claim']} | {lab['type']} | {lab['status']} | {lab['backing']} |", "|---|---|---|---|---|---|"]
    for c in claims:
        st = c.get("status") or "not_checked"
        label = f"{CLAIM_SYMBOL.get(st, '')} {lab.get('st_' + st, st)}"
        lines.append(f"| {c['id']} | {c.get('page')} | {md_cell(c.get('statement'))} | {c.get('type')} | {label} | {_backing(lab, c)} |")
    lines.append("")
    return lines


def contradictions_section(lab, claims_doc):
    claims = [c for c in ((claims_doc or {}).get("claims") or []) if c.get("status") in ("to_probe", "blatant")]
    lines = [f"## {lab['contradictions']}", ""]
    if not claims:
        lines += [lab["no_contradictions"], ""]
        return lines
    for c in claims:
        detail = _backing(lab, c)
        review = c.get("review") or {}
        if review.get("explanation"):
            detail += f" **{lab['reviewer_explanation']}**: {md_cell(review['explanation'])}"
        lines.append(lab["contradiction_line"].format(id=c["id"], page=c.get("page"), statement=md_cell(c.get("statement")), detail=detail))
    lines.append("")
    return lines


def to_request_section(lab, gate, email_text):
    lines = [f"## {lab['to_request']}", ""]
    items = (gate or {}).get("to_request") or []
    if not items:
        lines += [lab["nothing_to_request"], ""]
    else:
        for it in items:
            lines.append(f"- **{it['id']}** ({lab['page_abbrev']} {it.get('page')}) {md_cell(it.get('statement'))} → {it.get('proof') or '-'}")
        lines.append("")
    if email_text:
        lines += [f"### {lab['email_draft']}", "", "```", email_text.strip(), "```", ""]
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
            if a.get("capped"):
                label += f" ({lab['capped']})"
            if a.get("downgraded"):
                label += f" ({lab['downgraded'].format(ids=', '.join(a.get('downgraded_by') or []))})"
            if a.get("passes") and not a.get("stable", True):
                readings = ", ".join(lab.get(v, v) for v in a["passes"])
                label += f" ⚠ {lab['unstable']} ({readings})"
            evidence = a.get("evidence") or []
            pages = ", ".join(dict.fromkeys(str(e.get("page")) for e in evidence)) if evidence else "—"
            quotes = " / ".join(f'"{md_cell(e.get("quote"))}"' for e in evidence) if evidence else "—"
            if a.get("claim_ids"):
                quotes += " · " + ", ".join(a["claim_ids"])
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


def abort_report(lab, deck, grid, profile, date, kind, reason, annexes, claims_doc, gate, email_text, pages_meta):
    reference_source = (pages_meta or {}).get("reference_source", "")
    lines = header(lab, deck, grid, date, reference_source or None)
    lines += [f"## {lab['abort_title']}", "", f"**{lab['abort_reason']}**: {reason}", "", lab[f"abort_{kind}"], ""]
    lines += profile_section(lab, profile, grid, annexes)
    if kind == "contradiction":
        lines += contradictions_section(lab, claims_doc)
    if kind in ("no_annexes", "insufficient_annexes", "contradiction"):
        lines += to_request_section(lab, gate, email_text)
    if kind in ("insufficient_annexes", "contradiction"):
        lines += claims_section(lab, claims_doc)
    return "\n".join(lines)


def full_report(lab, deck, grid, profile, answers, score, reading, pages_meta, date, lang, annexes, claims_doc, gate, email_text):
    reference_source = (pages_meta or {}).get("reference_source", "")
    lines = header(lab, deck, grid, date, reference_source)
    lines += profile_section(lab, profile, grid, annexes)
    lines += completeness_section(lab, grid, score, lang)
    lines += reading_section(lab, reading)
    if grid["stage"] == "seed":
        lines += contradictions_section(lab, claims_doc)
        lines += to_request_section(lab, gate, email_text)
        lines += claims_section(lab, claims_doc)
    lines += questions_section(lab, grid, score, answers, lang)
    return "\n".join(lines)


def load_answers(answers_dir):
    answers = []
    for path in sorted(glob.glob(os.path.join(answers_dir, "block-*.json"))):
        with open(path, encoding="utf-8") as f:
            answers.extend(json.load(f).get("answers", []))
    return answers


def _load(path):
    if not path:
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grid", required=True, help="stage name or path")
    ap.add_argument("--deck", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--answers-dir")
    ap.add_argument("--score")
    ap.add_argument("--reading")
    ap.add_argument("--pages", help="pages.json, for the reference_source header line")
    ap.add_argument("--annexes", help="annexes.json (seed)")
    ap.add_argument("--claims", help="claims.final.json or claims.annex.json (seed)")
    ap.add_argument("--gate", help="gate.json from seed_gate.py annexes (seed)")
    ap.add_argument("--email", help="founder email draft (seed)")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--abort-kind", default=None, choices=["stage", "no_annexes", "insufficient_annexes", "contradiction"])
    ap.add_argument("--abort-reason", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    lab = L(args.lang)
    profile = _load(args.profile)
    grid = effective_grid(load_grid(args.grid), profile)
    annexes, claims_doc, gate, pages_meta = _load(args.annexes), _load(args.claims), _load(args.gate), _load(args.pages)
    email_text = None
    if args.email and os.path.isfile(args.email):
        with open(args.email, encoding="utf-8") as f:
            email_text = f.read()

    if args.abort_kind or args.abort_reason:
        kind = args.abort_kind or "stage"
        text = abort_report(lab, args.deck, grid, profile, args.date, kind, args.abort_reason or kind, annexes, claims_doc, gate, email_text, pages_meta)
    else:
        for name in ("answers_dir", "score", "reading"):
            if not getattr(args, name):
                print(f"report.py: --{name.replace('_', '-')} is required unless --abort-kind is given", file=sys.stderr)
                return 2
        score = _load(args.score)
        with open(args.reading, encoding="utf-8") as f:
            reading = f.read()
        answers = load_answers(args.answers_dir)
        text = full_report(lab, args.deck, grid, profile, answers, score, reading, pages_meta, args.date, args.lang, annexes, claims_doc, gate, email_text)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

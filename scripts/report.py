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

--grid is a stage name (preseed, seed, series_a, series_b, series_c, series_d) or a path. --lang selects the labels. Shipped: en, fr.
Any other code falls back to English labels; the writer's prose (reading.md) is in whatever
language the orchestrator requested. Grid question wording follows the same rule.
"""
import argparse
import datetime as dt
import glob
import json
import os
import sys

from claims_lib import to_number
from grid_lib import GridError, effective_grid, load_benchmarks, load_grid, stage_key

STAGES_WITH_ANNEXES = ("seed", "series-a", "series-b", "series-c", "series-d")

# How a grid is named in the disclaimer of a stage that carries a required document list. Any
# stage whose grid has annex_gate.required_documents uses disclaimer_documents with this name;
# a new stage needs one row here, not a new disclaimer.
GRID_NAMES = {
    "series-a": {"en": "series A grid", "fr": "grille série A"},
    "series-b": {"en": "series B grid", "fr": "grille série B"},
    "series-c": {"en": "series C grid", "fr": "grille série C"},
    "series-d": {"en": "series D grid", "fr": "grille série D"},
}

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
        "disclaimer_documents": "This report measures the completeness of the deck against the {grid}, and whether what the deck states holds up against the required documents of its stage and business model and public sources. It does not measure the quality of the company. It contains no verdict, no rating and no investment recommendation. A figure the deck states without a document behind it cannot score higher than partial. Benchmarks are shown next to the figures with their source and date; they never enter the score.",
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
        "abort_missing_documents": "At this stage every deck is read with the same list of documents for its stage and business model. At least one is missing or incomplete, so the reading stops here, before any claim, web check or scoring. The email draft below lists them, document by document.",
        "documents_required": "Required documents (stage and model list)",
        "documents_all_present": "Every document of the list is present.",
        "doc_line": "- **{name}**: {requirement} ({reason})",
        "doc_present": "present",
        "benchmark": "Benchmark",
        "benchmarks": "Benchmarks shown, never scored",
        "benchmarks_note": "Orders of magnitude for the model and the stage, each with its source and date. They are displayed next to the deck figures and never enter the completeness score. An empty value means no dated source was found.",
        "benchmark_none": "no dated source",
        "information_only_block": "for information, weight 0",
        "page_abbrev": "p.",
        "plan_vs_actual": "Plan against actual, quarter by quarter",
        "plan_vs_actual_note": "The plan read in the board pack of each quarter and the actual read in the P&L, from the claims of the deck matched in the documents. The gap is computed by code, (actual - plan) / |plan|. Empty cells stay empty. Displayed, never scored.",
        "plan_vs_actual_none": "No plan against actual figure was stated in the deck and matched in the documents.",
        "quarter": "Quarter",
        "metric": "Metric",
        "plan": "Plan (board pack)",
        "actual": "Actual (P&L)",
        "gap_pct": "Gap",
        "pva_summary": "{metric}: average gap {avg} over {n} quarter(s)",
        "pva_missed": ", {k} quarter(s) missed",
        "pva_band": ", {k} within ±{b} %",
        "pva_beyond": ", {k} beyond ±{b} %",
        "preference_stack": "The preference stack, as the terms state it",
        "preference_stack_note": "Every round, secondary sale, tender offer and debt line the deck states, one row each, with the figure stated, the status set by code and the backing found in the cap table, the terms or the press. Nothing is summed, nothing is valued. Displayed, never scored.",
        "preference_stack_none": "No round, preference, secondary sale or debt line was stated in the deck.",
        "round_or_instrument": "Round or instrument",
        "figure": "Figure",
        "ipo_comparables": "The company next to the last IPOs of its category",
        "ipo_comparables_note": "The comparables the deck names, with the figure their IPO filing states, next to the deck's own latest figure for the same metric when a proven or confirmed claim gives one. Facts side by side; no multiple, no valuation, no ranking. Displayed, never scored.",
        "ipo_comparables_none": "No IPO filing of the category was cited by the deck with a metric at IPO.",
        "comparable": "Comparable",
        "at_ipo": "At IPO (filing)",
        "deck_figure": "Deck",
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
        "disclaimer_documents": "Ce rapport mesure la complétude du deck au regard de la {grid}, et si ce que le deck affirme tient face aux documents obligatoires de son stade et de son modèle économique et aux sources publiques. Il ne mesure pas la qualité de l'entreprise. Il ne contient ni verdict, ni note, ni recommandation d'investissement. Un chiffre avancé sans document derrière ne peut pas dépasser « partielle ». Les repères sont affichés à côté des chiffres avec leur source et leur date ; ils n'entrent jamais dans le score.",
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
        "abort_missing_documents": "À ce stade, chaque deck est lu avec la même liste de documents pour son stade et son modèle économique. Au moins un manque ou est incomplet, donc la lecture s'arrête ici, avant toute affirmation, vérification web ou score. Le brouillon d'email ci-dessous les liste, document par document.",
        "documents_required": "Documents obligatoires (liste du stade et du modèle)",
        "documents_all_present": "Tous les documents de la liste sont présents.",
        "doc_line": "- **{name}** : {requirement} ({reason})",
        "doc_present": "présent",
        "benchmark": "Repère",
        "benchmarks": "Repères affichés, jamais notés",
        "benchmarks_note": "Ordres de grandeur pour le modèle et le stade, chacun avec sa source et sa date. Ils sont affichés à côté des chiffres du deck et n'entrent jamais dans le score de complétude. Une valeur vide signifie qu'aucune source datée n'a été trouvée.",
        "benchmark_none": "pas de source datée",
        "information_only_block": "pour information, poids 0",
        "page_abbrev": "p.",
        "plan_vs_actual": "Plan contre réalisé, trimestre par trimestre",
        "plan_vs_actual_note": "Le plan lu dans le board pack de chaque trimestre et le réalisé lu dans le P&L, à partir des affirmations du deck retrouvées dans les documents. L'écart est calculé par le code, (réalisé - plan) / |plan|. Les cases vides restent vides. Affiché, jamais noté.",
        "plan_vs_actual_none": "Aucun chiffre de plan contre réalisé n'est avancé par le deck et retrouvé dans les documents.",
        "quarter": "Trimestre",
        "metric": "Indicateur",
        "plan": "Plan (board pack)",
        "actual": "Réalisé (P&L)",
        "gap_pct": "Écart",
        "pva_summary": "{metric} : écart moyen {avg} sur {n} trimestre(s)",
        "pva_missed": ", {k} trimestre(s) manqué(s)",
        "pva_band": ", {k} à moins de ±{b} %",
        "pva_beyond": ", {k} au-delà de ±{b} %",
        "preference_stack": "La pile de préférences, telle que les termes l'énoncent",
        "preference_stack_note": "Chaque tour, cession secondaire, offre de rachat et ligne de dette que le deck avance, une ligne chacun, avec le chiffre avancé, le statut fixé par le code et l'appui trouvé dans la table de capitalisation, les termes ou la presse. Rien n'est additionné, rien n'est valorisé. Affiché, jamais noté.",
        "preference_stack_none": "Aucun tour, préférence, cession secondaire ou ligne de dette n'est avancé par le deck.",
        "round_or_instrument": "Tour ou instrument",
        "figure": "Chiffre",
        "ipo_comparables": "L'entreprise à côté des dernières introductions en bourse de sa catégorie",
        "ipo_comparables_note": "Les comparables que le deck nomme, avec le chiffre que leur prospectus d'introduction énonce, à côté du dernier chiffre du deck pour le même indicateur quand une affirmation prouvée ou confirmée en donne un. Des faits côte à côte ; ni multiple, ni valorisation, ni classement. Affiché, jamais noté.",
        "ipo_comparables_none": "Aucun prospectus d'introduction de la catégorie n'est cité par le deck avec un indicateur à l'introduction.",
        "comparable": "Comparable",
        "at_ipo": "À l'introduction (prospectus)",
        "deck_figure": "Deck",
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


def disclaimer(lab, grid):
    """The disclaimer of the stage: pre-seed, seed, or the one of a stage with a document list, named after its grid."""
    stage = grid.get("stage", "")
    if stage == "pre-seed":
        return lab["disclaimer_preseed"]
    if stage == "seed":
        return lab["disclaimer_seed"]
    if isinstance(grid.get("annex_gate"), dict) and "required_documents" in grid["annex_gate"]:
        lang = "fr" if lab is LABELS["fr"] else "en"
        name = GRID_NAMES.get(stage, {}).get(lang) or f"{stage} grid"
        return lab["disclaimer_documents"].format(grid=name)
    return lab["disclaimer_preseed"]


def header(lab, deck, grid, date, reference_source):
    lines = [f"# {lab['title']}: {os.path.basename(deck)}", ""]
    meta = [f"**{lab['stage']}**: {grid['stage']}", f"**{lab['grid_version']}**: {grid['version']}", f"**{lab['read_on']}**: {date}"]
    if reference_source:
        ref = lab["reference_pdf"] if reference_source == "pdf" else lab["reference_transcription"]
        meta.append(f"**{lab['reference']}**: {ref}")
    lines.append(" · ".join(meta))
    lines.append("")
    lines.append(f"> {disclaimer(lab, grid)}")
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
    if grid["stage"] in STAGES_WITH_ANNEXES:
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
        if b.get("information_only"):
            name = f"{b['id']}. {pick(b['name'], lang)} ({lab['information_only_block']})"
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


def _bench_cell(lab, items):
    parts = []
    for b in items:
        value = b.get("value") or lab["benchmark_none"]
        tail = ", ".join(x for x in (b.get("source") or "", b.get("date") or "") if x)
        parts.append(f"{value} ({tail})" if tail else value)
    return " · ".join(parts) if parts else "—"


def benchmarks_for_question(benchmarks, qid):
    return [b for b in (benchmarks or []) if qid in (b.get("question_ids") or [])]


def benchmarks_for_claim(benchmarks, claim_type):
    return [b for b in (benchmarks or []) if claim_type in (b.get("claim_types") or [])]


def claims_section(lab, claims_doc, benchmarks=None):
    claims = (claims_doc or {}).get("claims") or []
    if not claims:
        return []
    with_bench = bool(benchmarks)
    head = f"| # | {lab['page']} | {lab['claim']} | {lab['type']} | {lab['status']} | {lab['backing']} |"
    sep = "|---|---|---|---|---|---|"
    if with_bench:
        head += f" {lab['benchmark']} |"
        sep += "---|"
    lines = [f"## {lab['claims']}", "", head, sep]
    for c in claims:
        st = c.get("status") or "not_checked"
        label = f"{CLAIM_SYMBOL.get(st, '')} {lab.get('st_' + st, st)}"
        row = f"| {c['id']} | {c.get('page')} | {md_cell(c.get('statement'))} | {c.get('type')} | {label} | {_backing(lab, c)} |"
        if with_bench:
            items = benchmarks_for_claim(benchmarks, c.get("type")) if c.get("value") is not None else []
            row += f" {md_cell(_bench_cell(lab, items)) if items else '—'} |"
        lines.append(row)
    lines.append("")
    return lines


def benchmarks_section(lab, benchmarks, lang):
    if not benchmarks:
        return []
    lines = [f"## {lab['benchmarks']}", "", lab["benchmarks_note"], "", f"| {lab['question']} | {lab['benchmark']} | | |", "|---|---|---|---|"]
    for b in benchmarks:
        metric = pick(b.get("metric"), lang)
        value = b.get("value") or lab["benchmark_none"]
        src = md_cell(b.get("source")) or "—"
        if b.get("url"):
            src = f"[{src}]({b['url']})"
        note = f" {md_cell(b['note'])}" if b.get("note") else ""
        lines.append(f"| {', '.join(b.get('question_ids') or [])} · {md_cell(metric)} | {md_cell(value)}{note} | {src} | {b.get('date') or '—'} |")
    lines.append("")
    return lines


def _gap_percent(plan, actual):
    if plan is None or actual is None or plan == 0:
        return None
    return 100.0 * (actual - plan) / abs(plan)


def plan_vs_actual_section(lab, grid, claims_doc, lang):
    """The plan vs actual table of a grid that asks for one (grid["report"]["plan_vs_actual"]).

    Layout only: the plan and the actual come from the matched claims (plan_value from the board
    pack, actual_value from the P&L), the gap is computed here, nothing is scored."""
    spec = (grid.get("report") or {}).get("plan_vs_actual")
    if not spec:
        return []
    metrics = spec.get("metrics") or []
    order = {m["id"]: i for i, m in enumerate(metrics)}
    by_key = {}
    for c in (claims_doc or {}).get("claims") or []:
        if c.get("type") != spec.get("claim_type", "plan_vs_actual") or c.get("metric") not in order or not c.get("period"):
            continue
        key = (str(c["period"]), c["metric"])
        complete = c.get("plan_value") is not None and c.get("actual_value") is not None
        if key not in by_key or (complete and by_key[key].get("plan_value") is None):
            by_key[key] = c
    lines = [f"## {lab['plan_vs_actual']}", "", lab["plan_vs_actual_note"], ""]
    if not by_key:
        return lines + [lab["plan_vs_actual_none"], ""]
    periods = sorted({p for p, _ in by_key})[-int(spec.get("quarters") or 8):]
    bands = sorted(float(b) for b in (spec.get("bands_percent") or []))
    lines += [f"| {lab['quarter']} | {lab['metric']} | {lab['plan']} | {lab['actual']} | {lab['gap_pct']} | # |", "|---|---|---:|---:|---:|---|"]
    stats = {m["id"]: {"gaps": [], "missed": 0} for m in metrics}
    for p in periods:
        for m in metrics:
            c = by_key.get((p, m["id"]))
            if c is None:
                continue
            plan, actual = to_number(c.get("plan_value")), to_number(c.get("actual_value"))
            gap = _gap_percent(plan, actual)
            if gap is not None:
                stats[m["id"]]["gaps"].append(gap)
                if (m.get("missed_if") == "below" and actual < plan) or (m.get("missed_if") == "above" and actual > plan):
                    stats[m["id"]]["missed"] += 1
            plan_s = fmt_num(plan) if plan is not None else "—"
            actual_s = fmt_num(actual) if actual is not None else "—"
            gap_s = f"{gap:+.1f} %" if gap is not None else "—"
            lines.append(f"| {p} | {md_cell(pick(m.get('name'), lang))} | {plan_s} | {actual_s} | {gap_s} | {c.get('id')} |")
    lines.append("")
    for m in metrics:
        gaps = stats[m["id"]]["gaps"]
        if not gaps:
            continue
        line = "- " + lab["pva_summary"].format(metric=pick(m.get("name"), lang), avg=f"{sum(gaps) / len(gaps):+.1f} %", n=len(gaps))
        if m.get("missed_if"):
            line += lab["pva_missed"].format(k=stats[m["id"]]["missed"])
        # The distribution of the quarters by absolute gap (series D): within each band, then
        # beyond the widest one. Counted, never judged.
        for b in bands:
            line += lab["pva_band"].format(k=sum(1 for g in gaps if abs(g) <= b), b=fmt_num(b))
        if bands:
            line += lab["pva_beyond"].format(k=sum(1 for g in gaps if abs(g) > bands[-1]), b=fmt_num(bands[-1]))
        lines.append(line)
    lines.append("")
    return lines


def preference_stack_section(lab, grid, claims_doc, lang):
    """The preference stack of a grid that asks for one (grid["report"]["preference_stack"]).

    Layout only: one row per claim of the listed types, the round or instrument, the figure the
    deck states, the status set by code and the backing. Nothing summed, nothing valued."""
    spec = (grid.get("report") or {}).get("preference_stack")
    if not spec:
        return []
    types = set(spec.get("claim_types") or [])
    rows = [c for c in ((claims_doc or {}).get("claims") or []) if c.get("type") in types]
    lines = [f"## {lab['preference_stack']}", "", lab["preference_stack_note"], ""]
    if not rows:
        return lines + [lab["preference_stack_none"], ""]
    lines += [f"| # | {lab['round_or_instrument']} | {lab['type']} | {lab['claim']} | {lab['figure']} | {lab['status']} | {lab['backing']} |", "|---|---|---|---|---:|---|---|"]
    for c in rows:
        st = c.get("status") or "not_checked"
        label = f"{CLAIM_SYMBOL.get(st, '')} {lab.get('st_' + st, st)}"
        round_name = md_cell(c.get("round")) or "—"
        figure = fmt_num(c.get("value")) if c.get("value") is not None else "—"
        lines.append(f"| {c['id']} | {round_name} | {c.get('type')} | {md_cell(c.get('statement'))} | {figure} | {label} | {_backing(lab, c)} |")
    lines.append("")
    return lines


def ipo_comparables_section(lab, grid, claims_doc, lang):
    """The IPO comparables table of a grid that asks for one (grid["report"]["ipo_comparables"]).

    Layout only: every claim of the claim type that names a comparable and a metric, with the
    figure its filing states at IPO, and next to it the deck's own latest figure for the same
    metric, from the last proven or confirmed claim of the matching type. No multiple, no
    valuation, no ranking."""
    spec = (grid.get("report") or {}).get("ipo_comparables")
    if not spec:
        return []
    metrics = {m["id"]: m for m in (spec.get("metrics") or [])}
    claims = (claims_doc or {}).get("claims") or []
    rows = [c for c in claims if c.get("type") == spec.get("claim_type", "exit_comparable") and c.get("comparable") and c.get("metric") in metrics]
    lines = [f"## {lab['ipo_comparables']}", "", lab["ipo_comparables_note"], ""]
    if not rows:
        return lines + [lab["ipo_comparables_none"], ""]
    deck_figure = {}
    for c in claims:
        if c.get("status") in ("proven", "confirmed") and c.get("value") is not None:
            deck_figure[c.get("type")] = c  # the last one in claim order wins
    lines += [f"| {lab['comparable']} | {lab['metric']} | {lab['at_ipo']} | {lab['deck_figure']} | {lab['status']} | # |", "|---|---|---:|---:|---|---|"]
    for c in rows:
        m = metrics[c["metric"]]
        st = c.get("status") or "not_checked"
        label = f"{CLAIM_SYMBOL.get(st, '')} {lab.get('st_' + st, st)}"
        own = deck_figure.get(m.get("deck_claim_type"))
        own_s = f"{fmt_num(own.get('value'))} ({own['id']})" if own else "—"
        at_ipo = fmt_num(c.get("value")) if c.get("value") is not None else "—"
        lines.append(f"| {md_cell(c.get('comparable'))} | {md_cell(pick(m.get('name'), lang))} | {at_ipo} | {own_s} | {label} | {c.get('id')} |")
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


def to_request_section(lab, gate, email_text, lang="en"):
    lines = [f"## {lab['to_request']}", ""]
    items = (gate or {}).get("to_request") or []
    if (gate or {}).get("gate") == "documents":
        lines[0] = f"## {lab['documents_required']}"
        for p in (gate or {}).get("present") or []:
            lines.append(f"- {p['document']}: {lab['doc_present']} ({', '.join(p.get('annex_ids') or [])})")
        if not items:
            lines += [lab["documents_all_present"], ""]
        else:
            for it in items:
                name = pick(it.get("name"), lang) or it.get("document", "?")
                req = pick(it.get("requirement"), lang)
                lines.append(lab["doc_line"].format(name=md_cell(name), requirement=md_cell(req), reason=md_cell(it.get("reason", ""))))
            lines.append("")
    elif not items:
        lines += [lab["nothing_to_request"], ""]
    else:
        for it in items:
            lines.append(f"- **{it['id']}** ({lab['page_abbrev']} {it.get('page')}) {md_cell(it.get('statement'))} → {it.get('proof') or '-'}")
        lines.append("")
    if email_text:
        lines += [f"### {lab['email_draft']}", "", "```", email_text.strip(), "```", ""]
    return lines


def questions_section(lab, grid, score, answers, lang, benchmarks=None):
    by_id = {a["question_id"]: a for a in answers}
    sq = {q["question_id"]: q for q in score["questions"]}
    with_bench = bool(benchmarks)
    lines = [f"## {lab['by_question']}", ""]
    for block in grid["blocks"]:
        sb = next(b for b in score["blocks"] if b["id"] == block["id"])
        lines.append(f"### {block['id']}. {pick(block['name'], lang)} — {lab['weight']} {block['weight']} — {fmt_pct(sb['percent'])}")
        lines.append("")
        head = f"| # | {lab['question']} | {lab['value']} | {lab['page']} | {lab['quote']} |"
        sep = "|---|---|---|---|---|"
        if with_bench:
            head += f" {lab['benchmark']} |"
            sep += "---|"
        lines.append(head)
        lines.append(sep)
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
            row = f"| {qid} | {md_cell(pick(q['question'], lang))} | {label} | {pages} | {quotes} |"
            if with_bench:
                items = benchmarks_for_question(benchmarks, qid)
                row += f" {md_cell(_bench_cell(lab, items)) if items else '—'} |"
            lines.append(row)
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


def grid_benchmarks(grid):
    """The benchmarks to display for this effective grid: model and stage. Empty at pre-seed."""
    try:
        return load_benchmarks(grid.get("applied_model") or "saas", stage_key(grid))
    except GridError:
        return []


def abort_report(lab, deck, grid, profile, date, kind, reason, annexes, claims_doc, gate, email_text, pages_meta, lang="en"):
    reference_source = (pages_meta or {}).get("reference_source", "")
    lines = header(lab, deck, grid, date, reference_source or None)
    lines += [f"## {lab['abort_title']}", "", f"**{lab['abort_reason']}**: {reason}", "", lab[f"abort_{kind}"], ""]
    lines += profile_section(lab, profile, grid, annexes)
    if kind == "contradiction":
        lines += contradictions_section(lab, claims_doc)
    if kind in ("no_annexes", "insufficient_annexes", "contradiction", "missing_documents"):
        lines += to_request_section(lab, gate, email_text, lang)
    if kind in ("insufficient_annexes", "contradiction"):
        lines += claims_section(lab, claims_doc, grid_benchmarks(grid))
    return "\n".join(lines)


def full_report(lab, deck, grid, profile, answers, score, reading, pages_meta, date, lang, annexes, claims_doc, gate, email_text):
    reference_source = (pages_meta or {}).get("reference_source", "")
    benchmarks = grid_benchmarks(grid)
    lines = header(lab, deck, grid, date, reference_source)
    lines += profile_section(lab, profile, grid, annexes)
    lines += completeness_section(lab, grid, score, lang)
    lines += reading_section(lab, reading)
    if grid["stage"] in STAGES_WITH_ANNEXES:
        lines += contradictions_section(lab, claims_doc)
        lines += to_request_section(lab, gate, email_text, lang)
        lines += claims_section(lab, claims_doc, benchmarks)
        lines += plan_vs_actual_section(lab, grid, claims_doc, lang)
        lines += preference_stack_section(lab, grid, claims_doc, lang)
        lines += ipo_comparables_section(lab, grid, claims_doc, lang)
    lines += questions_section(lab, grid, score, answers, lang, benchmarks)
    lines += benchmarks_section(lab, benchmarks, lang)
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
    ap.add_argument("--gate", help="gate.json from seed_gate.py annexes (seed) or documents_gate.py documents (stages with a required document list)")
    ap.add_argument("--email", help="founder email draft (seed)")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--abort-kind", default=None, choices=["stage", "no_annexes", "insufficient_annexes", "contradiction", "missing_documents"])
    ap.add_argument("--abort-reason", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-pdf", action="store_true", help="skip the PDF rendered next to --out")
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
        text = abort_report(lab, args.deck, grid, profile, args.date, kind, args.abort_reason or kind, annexes, claims_doc, gate, email_text, pages_meta, args.lang)
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
    if not args.no_pdf:
        # The same reading as a PDF, next to the markdown: nothing added, nothing inferred.
        import report_pdf
        pdf_path = (args.out[:-3] if args.out.lower().endswith(".md") else args.out) + ".pdf"
        with open(pdf_path, "wb") as f:
            f.write(report_pdf.render(text, os.path.basename(args.out)))
        print(pdf_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

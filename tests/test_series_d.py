"""Tests for the series D grid: routing (series D and every later round; series C now alone), readable copy, documents gate (twelve documents, stage and model list), founder email, score, proof cap, report with the plan vs actual distribution, the preference stack and the IPO comparables."""
import json
import os
import re
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import apply_proof_cap  # noqa: E402
import claim_types  # noqa: E402
import documents_gate  # noqa: E402
import founder_email  # noqa: E402
import grid_lib  # noqa: E402
import report  # noqa: E402
import score  # noqa: E402

GRID = grid_lib.load_grid("series_d")
REQUIRED = [d["id"] for d in GRID["annex_gate"]["required_documents"]]
NEW_TYPES = ("backlog", "round_price", "round_purpose", "acquired_company", "management_letter", "close_cycle")
MD_PATH = os.path.join(HERE, "..", "skills", "deck-reader", "grids", "series_d.md")


def dump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


def annex(aid, text, kind="csv"):
    return {"id": aid, "file": f"{aid}.{kind}", "kind": kind, "pages": [{"number": 1, "text": text}]}


ANNEXES = {"annex_count": 12, "readable_count": 12, "annexes": [
    annex("X1", "Month\tProduct\tGeography\tRevenue\tCOGS\tS&M\tR&D\tG&A\tNet burn\tFCF\n2021-09\tCore\tFR\t100\t20\t40\t30\t10\t-10\t-12"),
    annex("X2", "INDEPENDENT AUDITOR'S REPORT\nOpinion\nPrepared under IFRS\nCash flow statement for the year ended 31 December 2025", "pdf"),
    annex("X3", "Segment\tAcquisition year\tCohort\tM0\tM12\tM48"),
    annex("X4", "Deal\tStage\tProbability\tAmount\tOwner\tSegment\tProduct\tGeography\tLost reason\tCompetitor"),
    annex("X5", "Rep\tStart date\tQuota\tQ1 attainment\tQ2 attainment\tLeft on"),
    annex("X6", "Contract\tMonth\tList price\tNet price\tDiscount\tStart date\tEnd date\tTerm"),
    annex("X7", "Holder\tShares\tRound\tPrice\tPost-money\tLiquidation preference\tParticipating\tRatchet\tIPO ratchet\tDebt facility"),
    annex("X8", "Model 2026-2029\tBase case\tCash with round, no further round\tZero-burn scenario", "xlsx"),
    annex("X9", "MASTER SUBSCRIPTION AGREEMENT between Gantrix and Ferrolux SAS", "pdf"),
    annex("X10", "Board meeting Q2 2026\tIssued 2026-07-19\tBudget\tActual\tVariance", "pdf"),
    annex("X11", "Month\tSales\tR&D\tG&A\tTotal headcount\tExecutive\tStart date\tEnd date"),
    annex("X12", "MANAGEMENT LETTER\nTo the Audit Committee\nControl deficiencies identified during the audit of the year ended 31 December 2025", "pdf"),
]}


def classification(**overrides):
    base = {
        "X1": {"type": "pnl_60m", "quote": "Month\tProduct\tGeography", "months_covered": 60},
        "X2": {"type": "accounts_audited_3y", "quote": "INDEPENDENT AUDITOR'S REPORT", "months_covered": None, "items_covered": 3},
        "X3": {"type": "cohorts_48m", "quote": "Segment\tAcquisition year", "months_covered": 49},
        "X4": {"type": "crm_pipeline", "quote": "Deal\tStage\tProbability", "months_covered": None},
        "X5": {"type": "sales_roster", "quote": "Rep\tStart date\tQuota", "months_covered": 24},
        "X6": {"type": "billing_export_36m", "quote": "List price\tNet price\tDiscount", "months_covered": 36},
        "X7": {"type": "cap_table_terms", "quote": "Liquidation preference\tParticipating", "months_covered": None},
        "X8": {"type": "model_3y", "quote": "Zero-burn scenario", "months_covered": 36},
        "X9": {"type": "top20_contracts", "quote": "MASTER SUBSCRIPTION AGREEMENT", "months_covered": None, "items_covered": 20},
        "X10": {"type": "board_pack_12q", "quote": "Board meeting Q2 2026", "months_covered": None, "items_covered": 12},
        "X11": {"type": "org_chart", "quote": "Total headcount", "months_covered": 48},
        "X12": {"type": "management_letters_3y", "quote": "MANAGEMENT LETTER", "months_covered": None, "items_covered": 3},
    }
    for k, v in overrides.items():
        if v is None:
            base.pop(k)
        else:
            base[k].update(v)
    return {"annexes": [dict(annex_id=k, **v) for k, v in base.items()]}


class RoutingTest(unittest.TestCase):
    def test_series_d_and_every_later_round_route_to_series_d(self):
        for s in ("series D", "Series D", "série D", "serie D", "series-d", "série-d", "series_d", "seriesd", "SERIES D",
                  "series E", "Série F", "growth round", "Growth Round", "growth-round", "growth", "pre-IPO", "pre ipo", "late stage",
                  "series-d-or-later"):
            self.assertEqual(grid_lib.stage_key(s), "series_d", s)
            self.assertEqual(grid_lib.load_grid(s)["stage"], "series-d", s)
        self.assertEqual(grid_lib.stage_key(GRID), "series_d")

    def test_series_c_now_covers_series_c_only(self):
        for s in ("series C", "série C", "series-c", "series-c-or-later"):
            self.assertEqual(grid_lib.stage_key(s), "series_c", s)
        self.assertEqual(grid_lib.load_grid("series C")["stage"], "series-c")
        for s in ("other", "not_stated", ""):
            with self.assertRaises(grid_lib.GridError):
                grid_lib.stage_key(s)

    def test_profiler_value_is_the_one_routed(self):
        with open(os.path.join(HERE, "..", "agents", "deck-profiler.md"), encoding="utf-8") as f:
            profiler = re.sub(r"\s+", " ", f.read())
        self.assertIn("`series-d-or-later`", profiler)
        self.assertIn("`series-c`", profiler)
        self.assertNotIn("series-c-or-later", profiler)
        self.assertIn("series D grid", profiler)
        with open(os.path.join(HERE, "..", "skills", "deck-reader", "SKILL.md"), encoding="utf-8") as f:
            skill = f.read()
        self.assertIn("`series-d-or-later`", skill)
        self.assertIn("GRID=series_d", skill)
        self.assertIn("GRID=series_c", skill)

    def test_grid_shape_inherits_series_c(self):
        seed = grid_lib.load_grid("seed")
        series_c = grid_lib.load_grid("series_c")
        for key in ("scale", "red_block_threshold_percent", "call_question_block_weight", "confirmation", "proof", "annex_gate", "gaps", "web", "claim_types", "report", "blocks"):
            self.assertIn(key, GRID, key)
        self.assertEqual(GRID["version"], "2026-09-14")
        self.assertEqual(GRID["scale"], seed["scale"])
        self.assertEqual(GRID["red_block_threshold_percent"], 50)
        self.assertEqual(GRID["call_question_block_weight"], 3)
        self.assertEqual(GRID["confirmation"], series_c["confirmation"])
        self.assertEqual(GRID["proof"], series_c["proof"])
        for k in ("minor_max_ratio", "probe_max_ratio"):
            self.assertEqual(GRID["gaps"][k], seed["gaps"][k], k)
        self.assertEqual(GRID["web"]["min_independent_sources"], 2)
        self.assertEqual(REQUIRED, ["pnl_60m", "accounts_audited_3y", "cohorts_48m", "crm_pipeline", "sales_roster", "billing_export_36m",
                                    "cap_table_terms", "model_3y", "top20_contracts", "board_pack_12q", "org_chart", "management_letters_3y"])
        docs = {d["id"]: d for d in GRID["annex_gate"]["required_documents"]}
        self.assertEqual(docs["pnl_60m"]["min_months"], 60)
        self.assertEqual(docs["accounts_audited_3y"]["min_count"], 3)
        self.assertEqual(docs["cohorts_48m"]["min_months"], 48)
        self.assertEqual(docs["billing_export_36m"]["min_months"], 36)
        self.assertEqual(docs["board_pack_12q"]["min_count"], 12)
        self.assertEqual(docs["org_chart"]["min_months"], 48)
        self.assertEqual(docs["management_letters_3y"]["min_count"], 3)
        self.assertIsNone(docs["management_letters_3y"]["min_months"])
        for d in docs.values():
            for lang in ("en", "fr"):
                self.assertTrue(d["name"].get(lang) and d["requirement"].get(lang), f"{d['id']}: missing {lang} label")
        # Every series C claim type survives, the series D ones are added, each with its proof rule.
        for t in series_c["claim_types"]:
            self.assertIn(t, GRID["claim_types"], t)
        for t in NEW_TYPES:
            self.assertIn(t, GRID["claim_types"], t)
            self.assertIn(t, claim_types.MEANING, t)
            self.assertIn(GRID["claim_types"][t]["check"], ("annex", "web", "both"), t)
            self.assertTrue(GRID["claim_types"][t]["proof"], t)
        for t in series_c["web"]["claim_types"]:
            self.assertIn(t, GRID["web"]["claim_types"], t)
        for t in ("round_price", "acquired_company"):
            self.assertIn(t, GRID["web"]["claim_types"], t)
        for t in GRID["web"]["claim_types"]:
            self.assertIn(GRID["claim_types"][t]["check"], ("web", "both"), t)
        for word in ("Infogreffe", "Wayback Machine", "tender offers", "acquired or listed", "S-1", "prospectus"):
            self.assertIn(word, GRID["web"]["rule"], word)
        qs = {q["id"]: q for _, q in grid_lib.all_questions(GRID)}
        self.assertEqual(sorted(q for q, x in qs.items() if x.get("red_flag_if_absent")), ["B4", "D1", "E2", "G1", "H2", "H3"])
        self.assertEqual(sorted(q for q, x in qs.items() if "weight_if_b2c" in x), ["C5"])
        self.assertEqual(qs["D1"]["claim_types"], ["plan_vs_actual"])
        self.assertEqual(qs["H3"]["claim_types"][0], "round_purpose")
        self.assertNotIn("D6", qs)  # the deals without a founder are no longer asked at series D
        self.assertIn("F3", qs)  # the win rate trend moved to market and competition
        self.assertIn("F4", qs)  # and so did pricing power
        for qid, q in qs.items():
            for t in q.get("claim_types") or []:
                self.assertIn(t, GRID["claim_types"], f"{qid} cites unknown type {t}")
        pva = GRID["report"]["plan_vs_actual"]
        self.assertEqual(pva["claim_type"], "plan_vs_actual")
        self.assertEqual(pva["quarters"], 12)
        self.assertEqual(pva["bands_percent"], [5, 10])
        self.assertEqual([m["id"] for m in pva["metrics"]], ["arr", "net_new_arr", "net_burn", "headcount"])
        self.assertEqual(GRID["report"]["preference_stack"]["claim_types"], ["liquidation_preference", "funding", "secondary_or_debt", "debt_terms", "round_price"])
        ipo = GRID["report"]["ipo_comparables"]
        self.assertEqual(ipo["claim_type"], "exit_comparable")
        self.assertEqual([m["id"] for m in ipo["metrics"]], ["arr_growth", "fcf_margin", "nrr", "gross_margin", "backlog"])
        for m in ipo["metrics"]:
            self.assertIn(m["deck_claim_type"], GRID["claim_types"], m["id"])

    def test_claim_types_cli_lists_the_new_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "types.json")
            self.assertEqual(claim_types.main(["--grid", "growth round", "--out", out]), 0)
            with open(out, encoding="utf-8") as f:
                doc = json.load(f)
            self.assertEqual(doc["stage"], "series-d")
            names = {t["type"]: t["meaning"] for t in doc["types"]}
            for t in NEW_TYPES:
                self.assertTrue(names.get(t), t)


class ReadableCopyTest(unittest.TestCase):
    """series_d.json and series_d.md say strictly the same thing."""

    @classmethod
    def setUpClass(cls):
        with open(MD_PATH, encoding="utf-8") as f:
            cls.md = f.read()
        cls.rows = {}
        for line in cls.md.splitlines():
            m = re.match(r"^\| ([A-I]\d) \| (.*)$", line)
            if m:
                cls.rows[m.group(1)] = line

    def test_version_and_progression(self):
        self.assertIn(f"**Grid version: {GRID['version']}.", self.md)
        flat = re.sub(r"\s+", " ", self.md)
        for q in ("what does the deck not say?", "does what the deck says hold up?", "does the machine repeat?",
                  "does the machine hold at scale, without the founders?", "does the machine hold without new money, and keep its place?",
                  "is the machine ready to change hands, and why this round?"):
            self.assertIn(q, flat, q)
        for title in ("## What changes from series C", "## How the series D reading works", "## Where the grid comes from"):
            self.assertIn(title, self.md)

    def test_blocks_weights_and_questions_are_identical(self):
        for b in GRID["blocks"]:
            self.assertIn(f"### Block {b['id']}. {b['name']['en']}, weight {b['weight']}", self.md, b["id"])
        ids = [q["id"] for _, q in grid_lib.all_questions(GRID)]
        self.assertEqual(sorted(self.rows), sorted(ids))
        for _, q in grid_lib.all_questions(GRID):
            row = self.rows[q["id"]]
            self.assertIn(f"| {q['id']} | {q['question']['en']} | {q['found_if'].rstrip('.')} |", row, q["id"])
            self.assertEqual("*proof*" in row, bool(q.get("requires_proof")), q["id"])
            self.assertEqual("Weight 0 in B2C" in row, "weight_if_b2c" in q, q["id"])
            if q.get("red_flag_if_absent"):
                self.assertRegex(row.lower(), r"absent = (red|the deck hides churn\. red)", q["id"])

    def test_documents_and_shares_are_identical(self):
        total = sum(b["weight"] for b in GRID["blocks"])
        for b in GRID["blocks"]:
            self.assertIn(f"| {b['id']}. {b['name']['en']} | {b['weight']} | {round(100 * b['weight'] / total)} % |", self.md, b["id"])
        for d in GRID["annex_gate"]["required_documents"]:
            line = next((l for l in self.md.splitlines() if l.startswith(f"| `{d['id']}` |")), None)
            self.assertIsNotNone(line, d["id"])
            if d.get("min_months"):
                self.assertIn(f"{d['min_months'] // 12} years" if d["id"] == "model_3y" else f"{d['min_months']} months", line, d["id"])
            if d.get("min_count"):
                self.assertIn(str(d["min_count"]), line, d["id"])

    def test_red_signals_listed(self):
        for s in ("More than two quarters beyond 10 % of plan in the last two years", "A round whose reason is not in the deck",
                  "A model that needs another round when the deck says this is the last", "A price at or below the last post-money that the deck does not say",
                  "An IPO ratchet in the terms", "Acquired ARR that shrank since closing", "A material weakness in a management letter",
                  "A document of the list missing"):
            self.assertIn(f"- {s}", self.md, s)


class DocumentsGateTest(unittest.TestCase):
    def test_all_present_continues(self):
        g, invalid = documents_gate.documents_gate(ANNEXES, classification(), GRID)
        self.assertEqual(invalid, [])
        self.assertEqual(g["decision"], "continue")
        self.assertEqual([p["document"] for p in g["present"]], REQUIRED)

    def test_missing_management_letters_stop_and_write_the_email(self):
        g, _ = documents_gate.documents_gate(ANNEXES, classification(X12=None), GRID)
        self.assertEqual(g["decision"], "stop_missing_documents")
        self.assertEqual([m["document"] for m in g["to_request"]], ["management_letters_3y"])
        t = founder_email.draft("documents", "deck.pdf", "fr", g["to_request"])
        self.assertIn("Lettres de recommandations de l'auditeur, trois derniers exercices", t)
        self.assertIn("(absent)", t)

    def test_too_short_documents_stop(self):
        g, _ = documents_gate.documents_gate(ANNEXES, classification(X1={"months_covered": 48}, X10={"items_covered": 8}, X12={"items_covered": 2}), GRID)
        self.assertEqual(g["decision"], "stop_missing_documents")
        self.assertEqual([m["document"] for m in g["to_request"]], ["pnl_60m", "board_pack_12q", "management_letters_3y"])
        self.assertIn("48 month(s), 60 required", g["to_request"][0]["reason"])
        self.assertIn("8 item(s), 12 required", g["to_request"][1]["reason"])
        self.assertIn("2 item(s), 3 required", g["to_request"][2]["reason"])
        t = founder_email.draft("documents", "deck.pdf", "en", g["to_request"])
        self.assertIn("- Board decks or minutes with budget vs actual, last twelve quarters:", t)
        self.assertIn("covers 48 month(s), 60 required", t)

    def test_no_annex_at_all_lists_the_twelve(self):
        g, _ = documents_gate.documents_gate({"annex_count": 0, "readable_count": 0, "annexes": []}, {"annexes": []}, GRID)
        self.assertEqual([m["document"] for m in g["to_request"]], REQUIRED)
        self.assertEqual(len(REQUIRED), 12)

    def test_consumer_list_is_adjusted_by_the_model_block(self):
        g = grid_lib.effective_grid(GRID, {"model_type": "consumer"})
        gate, invalid = documents_gate.documents_gate(ANNEXES, classification(X4=None, X5=None, X9=None), g)
        self.assertEqual(invalid, [])
        for did in ("crm_pipeline", "sales_roster", "top20_contracts"):
            self.assertNotIn(did, gate["required"])
        self.assertIn("management_letters_3y", gate["required"])
        self.assertEqual(gate["model"], "consumer")
        self.assertEqual([m["document"] for m in gate["to_request"]], ["product_analytics_48m"])

    def test_biotech_list_through_the_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile, req = os.path.join(tmp, "profile.json"), os.path.join(tmp, "required.json")
            dump(profile, {"model_type": "biotech", "announced_stage": "series-d-or-later"})
            self.assertEqual(documents_gate.main(["required", "--grid", "series-d-or-later", "--profile", profile, "--out", req]), 0)
            with open(req, encoding="utf-8") as f:
                doc = json.load(f)
            self.assertEqual(doc["stage"], "series-d")
            self.assertEqual([d["id"] for d in doc["required"]],
                             ["pnl_60m", "accounts_audited_3y", "cap_table_terms", "model_3y", "board_pack_12q", "org_chart", "management_letters_3y", "clinical_dossier", "ip_schedule"])


class ScoreTest(unittest.TestCase):
    def answers(self, grid, value="found", **overrides):
        out = []
        for _, q in grid_lib.all_questions(grid):
            v = overrides.get(q["id"], value)
            out.append({"question_id": q["id"], "value": v, "evidence": [] if v == "absent" else [{"page": 3, "quote": "q"}], "missing": "", "call_question": "ask"})
        return out

    def test_block_weights_and_shares(self):
        weights = {b["id"]: b["weight"] for b in GRID["blocks"]}
        self.assertEqual(weights, {"A": 1, "B": 2, "C": 3, "D": 3, "E": 2, "F": 2, "G": 2, "H": 2, "I": 1})
        names = [b["name"]["en"] for b in GRID["blocks"]]
        self.assertEqual(names[2], "Profitable growth")
        self.assertEqual(names[3], "Predictability and exit readiness")
        self.assertEqual(names[7], "The round and the exit")
        total = sum(weights.values())
        self.assertEqual({k: round(100 * w / total) for k, w in weights.items()}, {"A": 6, "B": 11, "C": 17, "D": 17, "E": 11, "F": 11, "G": 11, "H": 11, "I": 6})
        self.assertEqual(round(100 * (weights["C"] + weights["D"]) / total), 33)
        self.assertEqual(len(grid_lib.all_questions(GRID)), 48)
        g = grid_lib.effective_grid(GRID, {"model_type": "saas", "customer_type": "B2B"})
        s = score.compute(g, self.answers(g), {"customer_type": "B2B"})
        self.assertEqual(s["global_percent"], 100)
        # Only block D partial: 5 questions of 10 points, 50 % of D, 17 % of the global weight lost by half.
        s = score.compute(g, self.answers(g, **{q: "partial" for q in ("D1", "D2", "D3", "D4", "D5")}), {"customer_type": "B2B"})
        self.assertEqual(next(b for b in s["blocks"] if b["id"] == "D")["percent"], 50)
        self.assertEqual(s["global_percent"], round(100 - 50 * 3 / 18, 2))
        self.assertEqual(sorted(s["call_question_ids"]), ["D1", "D2", "D3", "D4", "D5"])

    def test_red_flags_in_b2b_and_b2c(self):
        g = grid_lib.effective_grid(GRID, {"model_type": "saas", "customer_type": "B2B"})
        s = score.compute(g, self.answers(g, "absent"), {"customer_type": "B2B"})
        self.assertEqual(sorted(s["red_flags"]), ["B4", "D1", "E2", "G1", "H2", "H3"])
        s = score.compute(g, self.answers(g, "absent"), {"customer_type": "B2C"})
        by_id = {q["question_id"]: q for q in s["questions"]}
        self.assertFalse(by_id["C5"]["counted"])
        self.assertEqual(by_id["C5"]["status"], "information_only")
        self.assertEqual(sorted(s["red_flags"]), ["B4", "D1", "E2", "G1", "H2", "H3"])  # no red signal depends on B2B at series D

    def test_red_signal_off_on_a_block_reweighted_to_zero(self):
        g = grid_lib.effective_grid(GRID, {"model_type": "biotech"})
        s = score.compute(g, self.answers(g, "absent"), {"customer_type": "B2B", "model_type": "biotech"})
        by_id = {q["question_id"]: q for q in s["questions"]}
        for qid in ("B4", "D1", "E2"):
            self.assertEqual(by_id[qid]["status"], "information_only", qid)
            self.assertNotIn(qid, s["red_flags"], qid)
        self.assertEqual(sorted(s["red_flags"]), ["G1", "H2", "H3"])


class ProofCapTest(unittest.TestCase):
    def test_proof_questions_without_a_proven_claim_are_capped_by_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            prof, cp = os.path.join(tmp, "profile.json"), os.path.join(tmp, "claims.json")
            dump(prof, {"model_type": "saas", "customer_type": "B2B", "announced_stage": "series-d-or-later"})
            dump(cp, {"claims": [{"id": "K01", "type": "plan_vs_actual", "status": "proven"},
                                 {"id": "K02", "type": "management_letter", "status": "not_covered"},
                                 {"id": "K03", "type": "backlog", "status": "unverifiable"},
                                 {"id": "K04", "type": "round_price", "status": "to_probe"}]})
            dump(os.path.join(tmp, "block-D.json"), {"block": "D", "answers": [
                {"question_id": "D1", "value": "found", "evidence": [{"page": 1, "quote": "q"}], "claim_ids": ["K01"]},
                {"question_id": "D2", "value": "found", "evidence": [{"page": 1, "quote": "q"}], "claim_ids": ["K02"]},
                {"question_id": "D3", "value": "found", "evidence": [{"page": 1, "quote": "q"}], "claim_ids": []}]})
            dump(os.path.join(tmp, "block-B.json"), {"block": "B", "answers": [{"question_id": "B7", "value": "found", "evidence": [{"page": 1, "quote": "q"}], "claim_ids": ["K03"]}]})
            dump(os.path.join(tmp, "block-H.json"), {"block": "H", "answers": [
                {"question_id": "H1", "value": "found", "evidence": [{"page": 1, "quote": "q"}], "claim_ids": []},
                {"question_id": "H4", "value": "found", "evidence": [{"page": 1, "quote": "q"}], "claim_ids": ["K04"]}]})
            changed = dict(apply_proof_cap.run("series E", prof, tmp, cp))
            self.assertEqual(changed, {"D2": "capped", "D3": "capped", "B7": "capped", "H4": "downgraded"})
            with open(os.path.join(tmp, "block-H.json"), encoding="utf-8") as f:
                values = {a["question_id"]: a["value"] for a in json.load(f)["answers"]}
            self.assertEqual(values, {"H1": "found", "H4": "partial"})  # H1 needs no proof; H4 lowered one step


class ReportTest(unittest.TestCase):
    PROFILE = {"model_type": "saas", "customer_type": "B2B", "announced_stage": "series-d-or-later", "sector": "s", "business_model": "b", "deck_language": "en", "page_count": 3, "evidence": {}}

    def claims(self):
        out = []
        # Twelve quarters of ARR plan vs actual: gaps -3, +1, -12, 0, -6, +4, -15, +2, -1, -8, +1, -2 (%).
        gaps = [-3, 1, -12, 0, -6, 4, -15, 2, -1, -8, 1, -2]
        for i, gap in enumerate(gaps):
            period = f"{2023 + (i + 2) // 4}-Q{(i + 2) % 4 + 1}"
            plan = 100
            out.append({"id": f"K{10 + i}", "page": 5, "quote": "q", "type": "plan_vs_actual", "statement": f"ARR {period}", "value": plan + gap,
                        "metric": "arr", "period": period, "plan_value": plan, "actual_value": plan + gap, "status": "proven"})
        out.append({"id": "K30", "page": 6, "quote": "q", "type": "plan_vs_actual", "statement": "headcount", "value": 410, "metric": "headcount", "period": "2026-Q2",
                    "plan_value": 400, "actual_value": None, "status": "not_covered"})
        out.append({"id": "K01", "page": 3, "quote": "q", "type": "fcf_margin", "statement": "FCF margin -8 %", "value": -8, "status": "proven"})
        out.append({"id": "K02", "page": 3, "quote": "q", "type": "nrr", "statement": "NRR 118 %", "value": 118, "status": "proven"})
        out.append({"id": "K03", "page": 8, "quote": "q", "type": "liquidation_preference", "statement": "Series C: 1x non-participating", "value": 1, "round": "Series C", "status": "proven"})
        out.append({"id": "K04", "page": 8, "quote": "q", "type": "funding", "statement": "Series C: 60M USD", "value": 60000000, "round": "Series C", "status": "proven"})
        out.append({"id": "K05", "page": 8, "quote": "q", "type": "debt_terms", "statement": "Venture debt 15M USD, 2025", "value": 15000000, "round": "Venture debt 2025", "status": "not_covered"})
        out.append({"id": "K06", "page": 8, "quote": "q", "type": "round_price", "statement": "Series C post-money 400M USD", "value": 400000000, "round": "Series C", "status": "proven"})
        out.append({"id": "K07", "page": 11, "quote": "q", "type": "exit_comparable", "statement": "Comparable Ltd: NRR 124 % at IPO", "value": 124,
                    "comparable": "Comparable Ltd", "metric": "nrr", "status": "confirmed"})
        out.append({"id": "K08", "page": 11, "quote": "q", "type": "exit_comparable", "statement": "Comparable Ltd: FCF margin -20 % at IPO", "value": -20,
                    "comparable": "Comparable Ltd", "metric": "fcf_margin", "status": "confirmed"})
        out.append({"id": "K09", "page": 11, "quote": "q", "type": "exit_comparable", "statement": "Comparable Ltd: gross margin 74 % at IPO", "value": 74,
                    "comparable": "Comparable Ltd", "metric": "gross_margin", "status": "unverifiable"})
        out.append({"id": "K40", "page": 11, "quote": "q", "type": "exit_comparable", "statement": "Acquirer Corp bought a peer", "value": None, "status": "confirmed"})
        return {"claims": out}

    def test_full_report_lays_out_the_three_series_d_tables(self):
        g = grid_lib.effective_grid(GRID, self.PROFILE)
        answers = ScoreTest().answers(g)
        s = score.compute(g, answers, self.PROFILE)
        gate, _ = documents_gate.documents_gate(ANNEXES, classification(), GRID)
        text = report.full_report(report.L("en"), "deck.pdf", g, self.PROFILE, answers, s, "### reading", {"reference_source": "pdf"}, "2026-09-14", "en", ANNEXES, self.claims(), gate, None)
        self.assertIn("series D grid", text)
        self.assertIn("**Stage**: series-d", text)
        self.assertIn("- management_letters_3y: present (X12)", text)
        # Plan vs actual: twelve quarters kept, the distribution counted by band.
        self.assertIn("## Plan against actual, quarter by quarter", text)
        rows = [l for l in text.splitlines() if l.startswith("| 20") and "| ARR |" in l]
        self.assertEqual(len(rows), 12)
        self.assertIn("| 2025-Q1 | ARR | 100 | 85 | -15.0 % | K16 |", text)
        self.assertIn("| 2026-Q2 | Headcount | 400 | — | — | K30 |", text)
        # Gaps -3, 1, -12, 0, -6, 4, -15, 2, -1, -8, 1, -2: average -3.2 %, 7 quarters under plan, 8 within 5 %, 10 within 10 %, 2 beyond.
        self.assertIn("- ARR: average gap -3.2 % over 12 quarter(s), 7 quarter(s) missed, 8 within ±5 %, 10 within ±10 %, 2 beyond ±10 %", text)
        # The preference stack: one row per round or instrument, as the terms state it.
        self.assertIn("## The preference stack, as the terms state it", text)
        self.assertIn("| K03 | Series C | liquidation_preference | Series C: 1x non-participating | 1 |", text)
        self.assertIn("| K05 | Venture debt 2025 | debt_terms | Venture debt 15M USD, 2025 | 15000000 |", text)
        self.assertIn("| K06 | Series C | round_price |", text)
        self.assertNotIn("| K07 | ", text.split("## The preference stack")[1].split("## The company next to")[0])
        # The IPO comparables: the filing figure next to the deck's own proven figure for the same metric.
        self.assertIn("## The company next to the last IPOs of its category", text)
        self.assertIn("| Comparable Ltd | Net revenue retention | 124 | 118 (K02) |", text)
        self.assertIn("| Comparable Ltd | Free cash flow margin | -20 | -8 (K01) |", text)
        self.assertIn("| Comparable Ltd | Gross margin | 74 | — |", text)  # no proven gross margin claim in the deck
        self.assertNotIn("Acquirer Corp", text.split("## The company next to")[1].split("## Question by question")[0])
        # Order: claims, then the three tables, then the questions; nothing in them is scored.
        self.assertLess(text.index("## What the deck states"), text.index("## Plan against actual"))
        self.assertLess(text.index("## Plan against actual"), text.index("## The preference stack"))
        self.assertLess(text.index("## The preference stack"), text.index("## The company next to"))
        self.assertLess(text.index("## The company next to"), text.index("## Question by question"))
        for bid in "ABCDEFGHI":
            self.assertIn(f"| {bid}. ", text)
        fr = report.full_report(report.L("fr"), "deck.pdf", g, self.PROFILE, answers, s, "### lecture", {"reference_source": "pdf"}, "2026-09-14", "fr", ANNEXES, self.claims(), gate, None)
        self.assertIn("grille série D", fr)
        self.assertIn("- ARR : écart moyen -3.2 % sur 12 trimestre(s), 7 trimestre(s) manqué(s), 8 à moins de ±5 %, 10 à moins de ±10 %, 2 au-delà de ±10 %", fr)
        self.assertIn("## La pile de préférences, telle que les termes l'énoncent", fr)
        self.assertIn("## L'entreprise à côté des dernières introductions en bourse de sa catégorie", fr)
        self.assertIn("| Comparable Ltd | Rétention nette du revenu | 124 | 118 (K02) |", fr)

    def test_tables_say_when_empty_and_stay_off_other_stages(self):
        g = grid_lib.effective_grid(GRID, self.PROFILE)
        empty = {"claims": []}
        self.assertIn("No round, preference, secondary sale or debt line was stated in the deck.", report.preference_stack_section(report.L("en"), g, empty, "en"))
        self.assertIn("No IPO filing of the category was cited by the deck with a metric at IPO.", report.ipo_comparables_section(report.L("en"), g, empty, "en"))
        c = grid_lib.load_grid("series_c")
        self.assertEqual(report.preference_stack_section(report.L("en"), c, self.claims(), "en"), [])
        self.assertEqual(report.ipo_comparables_section(report.L("en"), c, self.claims(), "en"), [])
        # The series C table has no bands: its summary line is unchanged.
        lines = report.plan_vs_actual_section(report.L("en"), c, self.claims(), "en")
        summary = next(l for l in lines if l.startswith("- ARR:"))
        self.assertNotIn("within", summary)
        self.assertEqual(len([l for l in lines if l.startswith("| 20") and "| ARR |" in l]), 8)

    def test_report_cli_abort_on_missing_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile, ann, gate_path, out = (os.path.join(tmp, n) for n in ("profile.json", "annexes.json", "gate.json", "deck.reading.md"))
            dump(profile, {"model_type": "saas", "customer_type": "B2B", "announced_stage": "series-d-or-later", "evidence": {}})
            dump(ann, ANNEXES)
            gate, _ = documents_gate.documents_gate(ANNEXES, classification(X12=None), GRID)
            dump(gate_path, gate)
            self.assertEqual(report.main(["--grid", "series-d-or-later", "--deck", "deck.pdf", "--profile", profile, "--annexes", ann, "--gate", gate_path,
                                          "--lang", "fr", "--out", out, "--no-pdf", "--abort-kind", "missing_documents", "--abort-reason", "management_letters_3y"]), 0)
            with open(out, encoding="utf-8") as f:
                text = f.read()
            self.assertIn("grille série D", text)
            self.assertIn("Lettres de recommandations de l'auditeur", text)
            self.assertIn("Lecture interrompue", text)
            self.assertNotIn("Plan contre réalisé", text)
            self.assertNotIn("pile de préférences", text)


if __name__ == "__main__":
    unittest.main()

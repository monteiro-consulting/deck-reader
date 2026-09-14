"""Tests for the series C grid: routing (series C and every later round), readable copy, documents gate (eleven documents, stage and model list), founder email, score, proof cap, report with the plan vs actual table."""
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

GRID = grid_lib.load_grid("series_c")
REQUIRED = [d["id"] for d in GRID["annex_gate"]["required_documents"]]
NEW_TYPES = ("plan_vs_actual", "net_price", "discount_rate", "fcf_margin", "zero_burn_growth", "product_share", "geo_share",
             "liquidation_preference", "debt_terms", "audit_opinion", "controls_certification", "competitor_funding", "exit_comparable")
MD_PATH = os.path.join(HERE, "..", "skills", "deck-reader", "grids", "series_c.md")


def dump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


def annex(aid, text, kind="csv"):
    return {"id": aid, "file": f"{aid}.{kind}", "kind": kind, "pages": [{"number": 1, "text": text}]}


ANNEXES = {"annex_count": 11, "readable_count": 11, "annexes": [
    annex("X1", "Month\tProduct\tGeography\tRevenue\tCOGS\tS&M\tR&D\tG&A\tNet burn\n2022-09\tCore\tFR\t100\t20\t40\t30\t10\t-10"),
    annex("X2", "INDEPENDENT AUDITOR'S REPORT\nOpinion\nCash flow statement for the year ended 31 December 2025", "pdf"),
    annex("X3", "Segment\tAcquisition year\tCohort\tM0\tM12\tM36"),
    annex("X4", "Deal\tStage\tProbability\tAmount\tOwner\tSegment\tProduct\tGeography\tLost reason\tCompetitor"),
    annex("X5", "Rep\tStart date\tQuota\tQ1 attainment\tQ2 attainment\tLeft on"),
    annex("X6", "Contract\tMonth\tList price\tNet price\tDiscount"),
    annex("X7", "Holder\tShares\tRound\tLiquidation preference\tParticipating\tRatchet\tDebt facility"),
    annex("X8", "Model 2026-2029\tBase case\tZero-burn scenario\tCash", "xlsx"),
    annex("X9", "MASTER SUBSCRIPTION AGREEMENT between Gantrix and Ferrolux SAS", "pdf"),
    annex("X10", "Board meeting Q2 2026\tBudget\tActual\tVariance", "pdf"),
    annex("X11", "Month\tSales\tR&D\tG&A\tTotal headcount\tExecutive\tStart date\tEnd date"),
]}


def classification(**overrides):
    base = {
        "X1": {"type": "pnl_48m", "quote": "Month\tProduct\tGeography", "months_covered": 48},
        "X2": {"type": "accounts_audited_3y", "quote": "INDEPENDENT AUDITOR'S REPORT", "months_covered": None, "items_covered": 3},
        "X3": {"type": "cohorts_36m", "quote": "Segment\tAcquisition year", "months_covered": 37},
        "X4": {"type": "crm_pipeline", "quote": "Deal\tStage\tProbability", "months_covered": None},
        "X5": {"type": "sales_roster", "quote": "Rep\tStart date\tQuota", "months_covered": 24},
        "X6": {"type": "billing_export_24m", "quote": "List price\tNet price\tDiscount", "months_covered": 24},
        "X7": {"type": "cap_table_terms", "quote": "Liquidation preference\tParticipating", "months_covered": None},
        "X8": {"type": "model_3y", "quote": "Zero-burn scenario", "months_covered": 36},
        "X9": {"type": "top20_contracts", "quote": "MASTER SUBSCRIPTION AGREEMENT", "months_covered": None, "items_covered": 20},
        "X10": {"type": "board_pack_8q", "quote": "Board meeting Q2 2026", "months_covered": None, "items_covered": 8},
        "X11": {"type": "org_chart", "quote": "Total headcount", "months_covered": 36},
    }
    for k, v in overrides.items():
        if v is None:
            base.pop(k)
        else:
            base[k].update(v)
    return {"annexes": [dict(annex_id=k, **v) for k, v in base.items()]}


class RoutingTest(unittest.TestCase):
    def test_series_c_routes_to_series_c_and_later_rounds_no_longer_do(self):
        for s in ("series C", "Series C", "série C", "serie C", "series-c", "série-c", "series_c", "seriesc", "SERIES C", "series-c-or-later"):
            self.assertEqual(grid_lib.stage_key(s), "series_c", s)
            self.assertEqual(grid_lib.load_grid(s)["stage"], "series-c", s)
        self.assertEqual(grid_lib.stage_key(GRID), "series_c")
        self.assertEqual(grid_lib.stage_key("series B"), "series_b")
        # Since the series D grid exists, series D and every later round route to it, not here.
        for s in ("series D", "Série D", "series E", "growth round", "Growth Round", "growth-round", "series-d-or-later"):
            self.assertEqual(grid_lib.stage_key(s), "series_d", s)
        for s in ("other", "not_stated", ""):
            with self.assertRaises(grid_lib.GridError):
                grid_lib.stage_key(s)

    def test_profiler_value_is_the_one_routed(self):
        with open(os.path.join(HERE, "..", "agents", "deck-profiler.md"), encoding="utf-8") as f:
            profiler = re.sub(r"\s+", " ", f.read())
        self.assertIn("`series-c`", profiler)
        self.assertIn("series C grid", profiler)
        with open(os.path.join(HERE, "..", "skills", "deck-reader", "SKILL.md"), encoding="utf-8") as f:
            skill = f.read()
        self.assertIn("`series-c`", skill)
        self.assertIn("GRID=series_c", skill)

    def test_grid_shape_inherits_series_b(self):
        seed = grid_lib.load_grid("seed")
        series_b = grid_lib.load_grid("series_b")
        for key in ("scale", "red_block_threshold_percent", "call_question_block_weight", "confirmation", "proof", "annex_gate", "gaps", "web", "claim_types", "report", "blocks"):
            self.assertIn(key, GRID, key)
        self.assertEqual(GRID["version"], "2026-09-14")
        self.assertEqual(GRID["scale"], seed["scale"])
        self.assertEqual(GRID["red_block_threshold_percent"], 50)
        self.assertEqual(GRID["call_question_block_weight"], 3)
        self.assertEqual(GRID["confirmation"], series_b["confirmation"])
        self.assertEqual(GRID["proof"], series_b["proof"])
        for k in ("minor_max_ratio", "probe_max_ratio"):
            self.assertEqual(GRID["gaps"][k], seed["gaps"][k], k)
        self.assertEqual(GRID["web"]["min_independent_sources"], 2)
        self.assertEqual(REQUIRED, ["pnl_48m", "accounts_audited_3y", "cohorts_36m", "crm_pipeline", "sales_roster", "billing_export_24m",
                                    "cap_table_terms", "model_3y", "top20_contracts", "board_pack_8q", "org_chart"])
        docs = {d["id"]: d for d in GRID["annex_gate"]["required_documents"]}
        self.assertEqual(docs["pnl_48m"]["min_months"], 48)
        self.assertEqual(docs["accounts_audited_3y"]["min_count"], 3)
        self.assertEqual(docs["cohorts_36m"]["min_months"], 36)
        self.assertEqual(docs["sales_roster"]["min_months"], 24)
        self.assertEqual(docs["billing_export_24m"]["min_months"], 24)
        self.assertIsNone(docs["cap_table_terms"]["min_months"])
        self.assertEqual(docs["model_3y"]["min_months"], 36)
        self.assertEqual(docs["top20_contracts"]["min_count"], 20)
        self.assertEqual(docs["board_pack_8q"]["min_count"], 8)
        self.assertEqual(docs["org_chart"]["min_months"], 36)
        for d in docs.values():
            for lang in ("en", "fr"):
                self.assertTrue(d["name"].get(lang) and d["requirement"].get(lang), f"{d['id']}: missing {lang} label")
        # Every series B claim type survives, the series C ones are added, each with its proof rule.
        for t in series_b["claim_types"]:
            self.assertIn(t, GRID["claim_types"], t)
        for t in NEW_TYPES:
            self.assertIn(t, GRID["claim_types"], t)
            self.assertIn(t, claim_types.MEANING, t)
            self.assertIn(GRID["claim_types"][t]["check"], ("annex", "web", "both"), t)
            self.assertTrue(GRID["claim_types"][t]["proof"], t)
        for t in series_b["web"]["claim_types"]:
            self.assertIn(t, GRID["web"]["claim_types"], t)
        for t in ("audit_opinion", "controls_certification", "competitor_funding", "exit_comparable", "net_price", "debt_terms"):
            self.assertIn(t, GRID["web"]["claim_types"], t)
        for t in GRID["web"]["claim_types"]:
            self.assertIn(GRID["claim_types"][t]["check"], ("web", "both"), t)
        for word in ("Infogreffe", "Companies House", "Handelsregister", "Wayback Machine", "G2", "Capterra", "litigation", "security incidents", "since the series B", "listed comparables"):
            self.assertIn(word, GRID["web"]["rule"], word)
        qs = {q["id"]: q for _, q in grid_lib.all_questions(GRID)}
        self.assertEqual(sorted(q for q, x in qs.items() if x.get("red_flag_if_absent")), ["B4", "D1", "D6", "E2", "G1", "H2"])
        self.assertEqual(sorted(q for q, x in qs.items() if "weight_if_b2c" in x), ["C5", "D6"])
        self.assertEqual(qs["D1"]["claim_types"], ["plan_vs_actual"])
        for qid, q in qs.items():
            for t in q.get("claim_types") or []:
                self.assertIn(t, GRID["claim_types"], f"{qid} cites unknown type {t}")
        pva = GRID["report"]["plan_vs_actual"]
        self.assertEqual(pva["claim_type"], "plan_vs_actual")
        self.assertEqual(pva["quarters"], 8)
        self.assertEqual([m["id"] for m in pva["metrics"]], ["arr", "net_new_arr", "net_burn", "headcount"])

    def test_claim_types_cli_lists_the_new_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "types.json")
            self.assertEqual(claim_types.main(["--grid", "series_c", "--out", out]), 0)
            with open(out, encoding="utf-8") as f:
                doc = json.load(f)
            self.assertEqual(doc["stage"], "series-c")
            names = {t["type"]: t["meaning"] for t in doc["types"]}
            for t in NEW_TYPES:
                self.assertTrue(names.get(t), t)


class ReadableCopyTest(unittest.TestCase):
    """series_c.json and series_c.md say strictly the same thing."""

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
                  "does the machine hold at scale, without the founders?", "does the machine hold without new money, and keep its place?"):
            self.assertIn(q, flat, q)
        for title in ("## What changes from series B", "## How the series C reading works", "## Where the grid comes from"):
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
        for s in ("Growth that slows faster than burn falls", "A plan missed two years in a row", "Discounts that rise",
                  "Older cohorts below younger ones", "A participating preference or a ratchet absent from the deck",
                  "Audited accounts with a qualified opinion", "A document of the list missing"):
            self.assertIn(f"- {s}", self.md, s)


class DocumentsGateTest(unittest.TestCase):
    def test_all_present_continues(self):
        g, invalid = documents_gate.documents_gate(ANNEXES, classification(), GRID)
        self.assertEqual(invalid, [])
        self.assertEqual(g["decision"], "continue")
        self.assertEqual([p["document"] for p in g["present"]], REQUIRED)

    def test_one_missing_document_stops_and_writes_the_email(self):
        g, _ = documents_gate.documents_gate(ANNEXES, classification(X6=None), GRID)
        self.assertEqual(g["decision"], "stop_missing_documents")
        self.assertEqual([m["document"] for m in g["to_request"]], ["billing_export_24m"])
        t = founder_email.draft("documents", "deck.pdf", "fr", g["to_request"])
        self.assertIn("Export de facturation avec prix liste, prix net et remise sur 24 mois", t)
        self.assertIn("(absent)", t)

    def test_too_short_documents_stop(self):
        g, _ = documents_gate.documents_gate(ANNEXES, classification(X1={"months_covered": 36}, X2={"items_covered": 2}, X10={"items_covered": 4}), GRID)
        self.assertEqual(g["decision"], "stop_missing_documents")
        self.assertEqual([m["document"] for m in g["to_request"]], ["pnl_48m", "accounts_audited_3y", "board_pack_8q"])
        self.assertIn("36 month(s), 48 required", g["to_request"][0]["reason"])
        self.assertIn("2 item(s), 3 required", g["to_request"][1]["reason"])
        self.assertIn("4 item(s), 8 required", g["to_request"][2]["reason"])
        t = founder_email.draft("documents", "deck.pdf", "en", g["to_request"])
        self.assertIn("- Audited annual accounts with the auditor's opinion, last three fiscal years:", t)
        self.assertIn("covers 36 month(s), 48 required", t)

    def test_no_annex_at_all_lists_the_eleven(self):
        g, _ = documents_gate.documents_gate({"annex_count": 0, "readable_count": 0, "annexes": []}, {"annexes": []}, GRID)
        self.assertEqual([m["document"] for m in g["to_request"]], REQUIRED)

    def test_consumer_list_is_adjusted_by_the_model_block(self):
        g = grid_lib.effective_grid(GRID, {"model_type": "consumer"})
        gate, invalid = documents_gate.documents_gate(ANNEXES, classification(X4=None, X5=None, X9=None), g)
        self.assertEqual(invalid, [])
        for did in ("crm_pipeline", "sales_roster", "top20_contracts"):
            self.assertNotIn(did, gate["required"])
        self.assertEqual(gate["model"], "consumer")
        self.assertEqual([m["document"] for m in gate["to_request"]], ["product_analytics_36m"])
        annexes = dict(ANNEXES, annexes=ANNEXES["annexes"] + [annex("X12", "Month\tMAU\tDAU\tDAU/MAU\tOrganic share\tPaid CAC by country")])
        cl = classification(X4=None, X5=None, X9=None)
        cl["annexes"].append({"annex_id": "X12", "type": "product_analytics_36m", "quote": "Month\tMAU\tDAU", "months_covered": 24})
        gate, _ = documents_gate.documents_gate(annexes, cl, g)
        self.assertIn("24 month(s), 36 required", gate["to_request"][0]["reason"])
        cl["annexes"][-1]["months_covered"] = 36
        gate, _ = documents_gate.documents_gate(annexes, cl, g)
        self.assertEqual(gate["decision"], "continue")

    def test_biotech_list_drops_cohorts_and_billing_through_the_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile, req = os.path.join(tmp, "profile.json"), os.path.join(tmp, "required.json")
            dump(profile, {"model_type": "biotech", "announced_stage": "series-c"})
            self.assertEqual(documents_gate.main(["required", "--grid", "series-c", "--profile", profile, "--out", req]), 0)
            with open(req, encoding="utf-8") as f:
                doc = json.load(f)
            self.assertEqual(doc["stage"], "series-c")
            self.assertEqual([d["id"] for d in doc["required"]],
                             ["pnl_48m", "accounts_audited_3y", "cap_table_terms", "model_3y", "board_pack_8q", "org_chart", "clinical_dossier", "ip_schedule"])


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
        self.assertEqual([b["name"]["en"] for b in GRID["blocks"]][3], "Position and durability")
        self.assertEqual([b["name"]["en"] for b in GRID["blocks"]][7], "Money and exit")
        total = sum(weights.values())
        self.assertEqual({k: round(100 * w / total) for k, w in weights.items()}, {"A": 6, "B": 11, "C": 17, "D": 17, "E": 11, "F": 11, "G": 11, "H": 11, "I": 6})
        self.assertEqual(round(100 * (weights["C"] + weights["D"]) / total), 33)
        self.assertEqual(len(grid_lib.all_questions(GRID)), 45)
        g = grid_lib.effective_grid(GRID, {"model_type": "saas", "customer_type": "B2B"})
        s = score.compute(g, self.answers(g), {"customer_type": "B2B"})
        self.assertEqual(s["global_percent"], 100)
        # Only block D partial: 6 questions of 12 points, 50 % of D, 17 % of the global weight lost by half.
        s = score.compute(g, self.answers(g, **{q: "partial" for q in ("D1", "D2", "D3", "D4", "D5", "D6")}), {"customer_type": "B2B"})
        self.assertEqual(next(b for b in s["blocks"] if b["id"] == "D")["percent"], 50)
        self.assertEqual(s["global_percent"], round(100 - 50 * 3 / 18, 2))
        self.assertEqual(sorted(s["call_question_ids"]), ["D1", "D2", "D3", "D4", "D5", "D6"])

    def test_b2b_red_flags_and_b2c_weight_zero(self):
        g = grid_lib.effective_grid(GRID, {"model_type": "saas", "customer_type": "B2B"})
        s = score.compute(g, self.answers(g, "absent"), {"customer_type": "B2B"})
        self.assertEqual(sorted(s["red_flags"]), ["B4", "D1", "D6", "E2", "G1", "H2"])
        s = score.compute(g, self.answers(g, "absent"), {"customer_type": "B2C"})
        by_id = {q["question_id"]: q for q in s["questions"]}
        for qid in ("C5", "D6"):
            self.assertFalse(by_id[qid]["counted"], qid)
            self.assertEqual(by_id[qid]["status"], "information_only", qid)
        # A question at weight 0 never raises a red signal: D6 drops out in B2C.
        self.assertEqual(sorted(s["red_flags"]), ["B4", "D1", "E2", "G1", "H2"])

    def test_red_signal_off_on_a_block_reweighted_to_zero(self):
        g = grid_lib.effective_grid(GRID, {"model_type": "biotech"})
        s = score.compute(g, self.answers(g, "absent"), {"customer_type": "B2B", "model_type": "biotech"})
        by_id = {q["question_id"]: q for q in s["questions"]}
        for qid in ("B4", "D1", "E2"):
            self.assertEqual(by_id[qid]["status"], "information_only", qid)
            self.assertNotIn(qid, s["red_flags"], qid)
        self.assertEqual(sorted(s["red_flags"]), ["G1", "H2"])


class ProofCapTest(unittest.TestCase):
    def test_proof_questions_without_a_proven_claim_are_capped_by_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            prof, cp = os.path.join(tmp, "profile.json"), os.path.join(tmp, "claims.json")
            dump(prof, {"model_type": "saas", "customer_type": "B2B", "announced_stage": "series-c"})
            dump(cp, {"claims": [{"id": "K01", "type": "plan_vs_actual", "status": "proven"},
                                 {"id": "K02", "type": "discount_rate", "status": "not_covered"},
                                 {"id": "K03", "type": "fcf_margin", "status": "unverifiable"},
                                 {"id": "K04", "type": "liquidation_preference", "status": "to_probe"}]})
            ans = [{"question_id": "D1", "value": "found", "evidence": [{"page": 1, "quote": "q"}], "claim_ids": ["K01"]},
                   {"question_id": "D2", "value": "found", "evidence": [{"page": 1, "quote": "q"}], "claim_ids": ["K02"]},
                   {"question_id": "D3", "value": "found", "evidence": [{"page": 1, "quote": "q"}], "claim_ids": []}]
            dump(os.path.join(tmp, "block-D.json"), {"block": "D", "answers": ans})
            dump(os.path.join(tmp, "block-C.json"), {"block": "C", "answers": [{"question_id": "C6", "value": "found", "evidence": [{"page": 1, "quote": "q"}], "claim_ids": ["K03"]}]})
            dump(os.path.join(tmp, "block-H.json"), {"block": "H", "answers": [
                {"question_id": "H1", "value": "found", "evidence": [{"page": 1, "quote": "q"}], "claim_ids": []},
                {"question_id": "H4", "value": "found", "evidence": [{"page": 1, "quote": "q"}], "claim_ids": ["K04"]}]})
            changed = dict(apply_proof_cap.run("série C", prof, tmp, cp))
            self.assertEqual(changed, {"D2": "capped", "D3": "capped", "C6": "capped", "H4": "downgraded"})
            with open(os.path.join(tmp, "block-D.json"), encoding="utf-8") as f:
                values = {a["question_id"]: a["value"] for a in json.load(f)["answers"]}
            self.assertEqual(values, {"D1": "found", "D2": "partial", "D3": "partial"})
            with open(os.path.join(tmp, "block-H.json"), encoding="utf-8") as f:
                values = {a["question_id"]: a["value"] for a in json.load(f)["answers"]}
            self.assertEqual(values, {"H1": "found", "H4": "partial"})  # H1 needs no proof; H4 lowered one step


class ReportTest(unittest.TestCase):
    PROFILE = {"model_type": "saas", "customer_type": "B2B", "announced_stage": "series-c", "sector": "s", "business_model": "b", "deck_language": "en", "page_count": 3, "evidence": {}}

    def claims(self):
        pva = []
        n = 10
        for i, (period, plan, actual) in enumerate([("2024-Q3", 100, 95), ("2024-Q4", 110, 112), ("2025-Q1", 120, 108), ("2025-Q2", 130, 130)]):
            pva.append({"id": f"K{n + i}", "page": 5, "quote": "q", "type": "plan_vs_actual", "statement": f"ARR {period}", "value": actual,
                        "metric": "arr", "period": period, "plan_value": plan, "actual_value": actual, "status": "proven"})
        pva.append({"id": "K20", "page": 6, "quote": "q", "type": "plan_vs_actual", "statement": "burn Q2", "value": 9, "metric": "net_burn", "period": "2025-Q2",
                    "plan_value": 8, "actual_value": 9, "status": "proven"})
        pva.append({"id": "K21", "page": 6, "quote": "q", "type": "plan_vs_actual", "statement": "headcount Q2", "value": 210, "metric": "headcount", "period": "2025-Q2",
                    "plan_value": 200, "actual_value": None, "status": "not_covered"})
        pva.append({"id": "K01", "page": 3, "quote": "q", "type": "fcf_margin", "statement": "FCF margin -20 %", "value": -20, "status": "proven"})
        return {"claims": pva}

    def test_full_report_lays_out_the_plan_vs_actual_table(self):
        g = grid_lib.effective_grid(GRID, self.PROFILE)
        answers = ScoreTest().answers(g)
        s = score.compute(g, answers, self.PROFILE)
        gate, _ = documents_gate.documents_gate(ANNEXES, classification(), GRID)
        text = report.full_report(report.L("en"), "deck.pdf", g, self.PROFILE, answers, s, "### reading", {"reference_source": "pdf"}, "2026-09-14", "en", ANNEXES, self.claims(), gate, None)
        self.assertIn("series C grid", text)
        self.assertIn("**Stage**: series-c", text)
        self.assertIn("- board_pack_8q: present (X10)", text)
        self.assertIn("## Plan against actual, quarter by quarter", text)
        self.assertIn("| Quarter | Metric | Plan (board pack) | Actual (P&L) | Gap | # |", text)
        self.assertIn("| 2024-Q3 | ARR | 100 | 95 | -5.0 % | K10 |", text)
        self.assertIn("| 2025-Q1 | ARR | 120 | 108 | -10.0 % | K12 |", text)
        self.assertIn("| 2025-Q2 | Net burn | 8 | 9 | +12.5 % | K20 |", text)
        self.assertIn("| 2025-Q2 | Headcount | 200 | — | — | K21 |", text)  # empty cells stay empty
        # ARR gaps -5, +1.8, -10, 0: average -3.3 %, two quarters under plan; net burn one quarter above plan.
        self.assertIn("- ARR: average gap -3.3 % over 4 quarter(s), 2 quarter(s) missed", text)
        self.assertIn("- Net burn: average gap +12.5 % over 1 quarter(s), 1 quarter(s) missed", text)
        self.assertNotIn("- Headcount: average gap", text)
        # The table comes after the claims and before the questions, and nothing in it is scored.
        self.assertLess(text.index("## What the deck states"), text.index("## Plan against actual"))
        self.assertLess(text.index("## Plan against actual"), text.index("## Question by question"))
        self.assertIn("57 %", text)  # Bessemer, 100M USD ARR and above, next to B3
        for bid in "ABCDEFGHI":
            self.assertIn(f"| {bid}. ", text)
        fr = report.full_report(report.L("fr"), "deck.pdf", g, self.PROFILE, answers, s, "### lecture", {"reference_source": "pdf"}, "2026-09-14", "fr", ANNEXES, self.claims(), gate, None)
        self.assertIn("grille série C", fr)
        self.assertIn("## Plan contre réalisé, trimestre par trimestre", fr)
        self.assertIn("| 2025-Q2 | Burn net | 8 | 9 | +12.5 % | K20 |", fr)
        self.assertIn("- ARR : écart moyen -3.3 % sur 4 trimestre(s), 2 trimestre(s) manqué(s)", fr)

    def test_table_keeps_the_last_eight_quarters_and_says_when_empty(self):
        g = grid_lib.effective_grid(GRID, self.PROFILE)
        claims = {"claims": [{"id": f"K{i:02d}", "type": "plan_vs_actual", "metric": "net_new_arr", "period": f"{2023 + (i - 1) // 4}-Q{(i - 1) % 4 + 1}",
                              "plan_value": 10, "actual_value": 10, "status": "proven"} for i in range(1, 11)]}
        lines = report.plan_vs_actual_section(report.L("en"), g, claims, "en")
        rows = [l for l in lines if l.startswith("| 20")]
        self.assertEqual(len(rows), 8)
        self.assertTrue(rows[0].startswith("| 2023-Q3 |"))
        self.assertTrue(rows[-1].startswith("| 2025-Q2 |"))
        self.assertIn("- Net new ARR: average gap +0.0 % over 8 quarter(s), 0 quarter(s) missed", lines)
        empty = report.plan_vs_actual_section(report.L("en"), g, {"claims": []}, "en")
        self.assertIn("No plan against actual figure was stated in the deck and matched in the documents.", empty)
        # Stages without the table in their grid get nothing.
        self.assertEqual(report.plan_vs_actual_section(report.L("en"), grid_lib.load_grid("series_b"), claims, "en"), [])

    def test_report_cli_abort_on_missing_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile, ann, gate_path, out = (os.path.join(tmp, n) for n in ("profile.json", "annexes.json", "gate.json", "deck.reading.md"))
            dump(profile, {"model_type": "fintech", "customer_type": "B2B", "announced_stage": "series-c", "evidence": {}})
            dump(ann, ANNEXES)
            gate, _ = documents_gate.documents_gate(ANNEXES, classification(), grid_lib.effective_grid(GRID, {"model_type": "fintech"}))
            dump(gate_path, gate)
            self.assertEqual(report.main(["--grid", "series-c", "--deck", "deck.pdf", "--profile", profile, "--annexes", ann, "--gate", gate_path,
                                          "--lang", "fr", "--out", out, "--no-pdf", "--abort-kind", "missing_documents", "--abort-reason", "licence, risk_book_48m"]), 0)
            with open(out, encoding="utf-8") as f:
                text = f.read()
            self.assertIn("grille série C", text)
            self.assertIn("Livre de risque sur 48 mois", text)
            self.assertIn("Lecture interrompue", text)
            self.assertNotIn("Plan contre réalisé", text)


if __name__ == "__main__":
    unittest.main()

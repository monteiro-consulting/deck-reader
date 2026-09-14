"""Tests for the series B grid: routing, readable copy, documents gate (ten documents, stage and model list), founder email, score, report."""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import claim_types  # noqa: E402
import founder_email  # noqa: E402
import grid_lib  # noqa: E402
import report  # noqa: E402
import score  # noqa: E402
import documents_gate  # noqa: E402

GRID = grid_lib.load_grid("series_b")
REQUIRED = [d["id"] for d in GRID["annex_gate"]["required_documents"]]
NEW_TYPES = ("rule_of_40", "magic_number", "quota_attainment", "rep_ramp", "second_engine", "exec_team", "exec_departure",
             "headcount", "attrition", "board", "breakeven", "audited_figure", "win_rate", "secondary_or_debt", "expansion", "employee_reviews")


def dump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


def annex(aid, text, kind="csv"):
    return {"id": aid, "file": f"{aid}.{kind}", "kind": kind, "pages": [{"number": 1, "text": text}]}


ANNEXES = {"annex_count": 10, "readable_count": 10, "annexes": [
    annex("X1", "Month\tRevenue\tCOGS\tS&M\tR&D\tG&A\tNet burn\n2023-09\t100\t20\t40\t30\t10\t-10"),
    annex("X2", "INDEPENDENT AUDITOR'S REPORT\nBalance sheet as at 31 December 2025\nIncome statement", "pdf"),
    annex("X3", "Segment\tCohort\tM0\tM1\tM2\tM24"),
    annex("X4", "Deal\tStage\tProbability\tAmount\tOwner\tSegment\tFirst contact\tSigned\tLost reason\tCompetitor"),
    annex("X5", "Rep\tStart date\tQuota\tQ1 attainment\tQ2 attainment\tLeft on"),
    annex("X6", "Holder\tShares\tPercent\tOption pool\tUnallocated"),
    annex("X7", "Model 2026-2029\tRevenue by segment\tExpenses by function\tCash\tHires\tBreakeven", "xlsx"),
    annex("X8", "MASTER SUBSCRIPTION AGREEMENT between Gantrix and Ferrolux SAS", "pdf"),
    annex("X9", "Board meeting Q3 2026\tAttendees\tMinutes", "pdf"),
    annex("X10", "Month\tSales\tR&D\tG&A\tTotal headcount\tExecutive\tStart date\tEnd date"),
]}


def classification(**overrides):
    base = {
        "X1": {"type": "pnl_36m", "quote": "Month\tRevenue\tCOGS", "months_covered": 36},
        "X2": {"type": "accounts_audited", "quote": "INDEPENDENT AUDITOR'S REPORT", "months_covered": None, "items_covered": 2},
        "X3": {"type": "cohorts_24m", "quote": "Segment\tCohort\tM0", "months_covered": 25},
        "X4": {"type": "crm_pipeline", "quote": "Deal\tStage\tProbability", "months_covered": None},
        "X5": {"type": "sales_roster", "quote": "Rep\tStart date\tQuota", "months_covered": 12},
        "X6": {"type": "cap_table", "quote": "Holder\tShares", "months_covered": None},
        "X7": {"type": "model_3y", "quote": "Model 2026-2029", "months_covered": 36},
        "X8": {"type": "top20_contracts", "quote": "MASTER SUBSCRIPTION AGREEMENT", "months_covered": None, "items_covered": 20},
        "X9": {"type": "board_pack_4q", "quote": "Board meeting Q3 2026", "months_covered": None, "items_covered": 4},
        "X10": {"type": "org_chart", "quote": "Total headcount", "months_covered": 24},
    }
    for k, v in overrides.items():
        if v is None:
            base.pop(k)
        else:
            base[k].update(v)
    return {"annexes": [dict(annex_id=k, **v) for k, v in base.items()]}


class RoutingTest(unittest.TestCase):
    def test_stage_spellings_route_to_series_b(self):
        for s in ("series B", "Series B", "série B", "serie B", "series-b", "série-b", "serie-b", "series_b", "seriesb", "SERIES B"):
            self.assertEqual(grid_lib.stage_key(s), "series_b", s)
            self.assertEqual(grid_lib.load_grid(s)["stage"], "series-b", s)
        self.assertEqual(grid_lib.stage_key(GRID), "series_b")
        self.assertEqual(grid_lib.stage_key("series A"), "series_a")
        with self.assertRaises(grid_lib.GridError):
            grid_lib.stage_key("series C")
        with self.assertRaises(grid_lib.GridError):
            grid_lib.stage_key("série C")

    def test_grid_shape_matches_seed_schema(self):
        seed = grid_lib.load_grid("seed")
        series_a = grid_lib.load_grid("series_a")
        for key in ("scale", "red_block_threshold_percent", "call_question_block_weight", "confirmation", "proof", "annex_gate", "gaps", "web", "claim_types", "blocks"):
            self.assertIn(key, GRID, key)
        self.assertEqual(GRID["version"], "2026-09-14")
        self.assertEqual(GRID["scale"], seed["scale"])
        self.assertEqual(GRID["confirmation"], series_a["confirmation"])
        self.assertEqual(GRID["proof"], series_a["proof"])
        for k in ("minor_max_ratio", "probe_max_ratio"):
            self.assertEqual(GRID["gaps"][k], seed["gaps"][k], k)
        self.assertEqual(GRID["web"]["min_independent_sources"], seed["web"]["min_independent_sources"])
        self.assertEqual(REQUIRED, ["pnl_36m", "accounts_audited", "cohorts_24m", "crm_pipeline", "sales_roster", "cap_table", "model_3y", "top20_contracts", "board_pack_4q", "org_chart"])
        docs = {d["id"]: d for d in GRID["annex_gate"]["required_documents"]}
        self.assertEqual(docs["pnl_36m"]["min_months"], 36)
        self.assertEqual(docs["accounts_audited"]["min_count"], 2)
        self.assertEqual(docs["cohorts_24m"]["min_months"], 24)
        self.assertEqual(docs["sales_roster"]["min_months"], 12)
        self.assertEqual(docs["model_3y"]["min_months"], 36)
        self.assertEqual(docs["top20_contracts"]["min_count"], 20)
        self.assertEqual(docs["board_pack_4q"]["min_count"], 4)
        self.assertEqual(docs["org_chart"]["min_months"], 24)
        for d in docs.values():
            for lang in ("en", "fr"):
                self.assertTrue(d["name"].get(lang) and d["requirement"].get(lang), f"{d['id']}: missing {lang} label")
        # Every series A claim type survives, the series B ones are added, every one has a meaning.
        for t in series_a["claim_types"]:
            self.assertIn(t, GRID["claim_types"], t)
        for t in NEW_TYPES:
            self.assertIn(t, GRID["claim_types"], t)
            self.assertIn(t, claim_types.MEANING, t)
            self.assertTrue(GRID["claim_types"][t]["check"] in ("annex", "web", "both"), t)
        for t in ("exec_team", "exec_departure", "headcount", "secondary_or_debt", "expansion", "employee_reviews"):
            self.assertIn(t, GRID["web"]["claim_types"], t)
        for t in series_a["web"]["claim_types"]:
            self.assertIn(t, GRID["web"]["claim_types"], t)
        weights = {b["id"]: b["weight"] for b in GRID["blocks"]}
        self.assertEqual(weights, {"A": 1, "B": 2, "C": 3, "D": 3, "E": 2, "F": 2, "G": 2, "H": 2, "I": 1})
        qs = {q["id"]: q for _, q in grid_lib.all_questions(GRID)}
        self.assertEqual(sorted(q for q, x in qs.items() if x.get("red_flag_if_absent")), ["B4", "D4", "D6", "E2", "G1", "H2"])
        self.assertEqual(sorted(q for q, x in qs.items() if "weight_if_b2c" in x), ["C5", "C6", "D4", "D5", "D6"])
        for q in ("C5", "C6", "D4", "D5", "D6"):
            self.assertEqual(qs[q]["weight_if_b2c"], 0)
        # Every claim type cited by a question exists in the grid.
        for qid, q in qs.items():
            for t in q.get("claim_types") or []:
                self.assertIn(t, GRID["claim_types"], f"{qid} cites unknown type {t}")

    def test_readable_grid_matches_json(self):
        with open(os.path.join(HERE, "..", "skills", "deck-reader", "grids", "series_b.md"), encoding="utf-8") as f:
            md = f.read()
        for _, q in grid_lib.all_questions(GRID):
            self.assertIn(f"| {q['id']} |", md, f"{q['id']} missing from series_b.md")
        self.assertIn(GRID["version"], md)
        for d in REQUIRED:
            self.assertIn(d, md)

    def test_claim_types_cli_lists_the_new_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "types.json")
            self.assertEqual(claim_types.main(["--grid", "series_b", "--out", out]), 0)
            with open(out, encoding="utf-8") as f:
                doc = json.load(f)
            self.assertEqual(doc["stage"], "series-b")
            names = {t["type"]: t["meaning"] for t in doc["types"]}
            for t in NEW_TYPES:
                self.assertTrue(names.get(t), t)


class DocumentsGateTest(unittest.TestCase):
    def test_all_present_continues(self):
        g, invalid = documents_gate.documents_gate(ANNEXES, classification(), GRID)
        self.assertEqual(invalid, [])
        self.assertEqual(g["decision"], "continue")
        self.assertEqual([p["document"] for p in g["present"]], REQUIRED)
        self.assertEqual(g["to_request"], [])

    def test_one_missing_document_stops_and_lists_it(self):
        g, _ = documents_gate.documents_gate(ANNEXES, classification(X9=None), GRID)
        self.assertEqual(g["decision"], "stop_missing_documents")
        self.assertEqual([m["document"] for m in g["to_request"]], ["board_pack_4q"])
        self.assertEqual(g["to_request"][0]["reason"], "absent")

    def test_too_few_months_stops(self):
        g, _ = documents_gate.documents_gate(ANNEXES, classification(X1={"months_covered": 24}), GRID)
        self.assertEqual(g["decision"], "stop_missing_documents")
        self.assertEqual(g["to_request"][0]["document"], "pnl_36m")
        self.assertIn("24 month(s), 36 required", g["to_request"][0]["reason"])

    def test_one_fiscal_year_of_accounts_stops(self):
        g, _ = documents_gate.documents_gate(ANNEXES, classification(X2={"items_covered": 1}), GRID)
        self.assertEqual(g["decision"], "stop_missing_documents")
        self.assertEqual(g["to_request"][0]["document"], "accounts_audited")
        self.assertIn("1 item(s), 2 required", g["to_request"][0]["reason"])

    def test_too_few_contracts_and_board_decks_stop(self):
        g, _ = documents_gate.documents_gate(ANNEXES, classification(X8={"items_covered": 12}, X9={"items_covered": 3}), GRID)
        self.assertEqual([m["document"] for m in g["to_request"]], ["top20_contracts", "board_pack_4q"])
        self.assertIn("12 item(s), 20 required", g["to_request"][0]["reason"])
        self.assertIn("3 item(s), 4 required", g["to_request"][1]["reason"])

    def test_no_annex_at_all_lists_the_ten(self):
        g, _ = documents_gate.documents_gate({"annex_count": 0, "readable_count": 0, "annexes": []}, {"annexes": []}, GRID)
        self.assertEqual(g["decision"], "stop_missing_documents")
        self.assertEqual([m["document"] for m in g["to_request"]], REQUIRED)

    def test_consumer_list_drops_sales_documents_and_requires_product_analytics(self):
        g = grid_lib.effective_grid(GRID, {"model_type": "consumer"})
        gate, invalid = documents_gate.documents_gate(ANNEXES, classification(X4=None, X5=None, X8=None), g)
        self.assertEqual(invalid, [])
        for did in ("crm_pipeline", "sales_roster", "top20_contracts"):
            self.assertNotIn(did, gate["required"])
        self.assertIn("product_analytics_24m", gate["required"])
        self.assertEqual(gate["model"], "consumer")
        self.assertEqual(gate["decision"], "stop_missing_documents")
        self.assertEqual([m["document"] for m in gate["to_request"]], ["product_analytics_24m"])
        # A classification into a document the model removed is invalid, not silently accepted.
        gate, invalid = documents_gate.documents_gate(ANNEXES, classification(), g)
        self.assertEqual(sorted(i["type"] for i in invalid), ["crm_pipeline", "sales_roster", "top20_contracts"])
        # With the analytics export the consumer list is complete.
        annexes = dict(ANNEXES, annexes=ANNEXES["annexes"] + [annex("X11", "Month\tMAU\tDAU\tDAU/MAU\tD30 retention\tOrganic share")])
        cl = classification(X4=None, X5=None, X8=None)
        cl["annexes"].append({"annex_id": "X11", "type": "product_analytics_24m", "quote": "Month\tMAU\tDAU", "months_covered": 24})
        gate, _ = documents_gate.documents_gate(annexes, cl, g)
        self.assertEqual(gate["decision"], "continue")
        self.assertEqual([p["document"] for p in gate["present"]],
                         ["pnl_36m", "accounts_audited", "cohorts_24m", "cap_table", "model_3y", "board_pack_4q", "org_chart", "product_analytics_24m"])
        # Twelve months of analytics are not enough at series B.
        cl["annexes"][-1]["months_covered"] = 12
        gate, _ = documents_gate.documents_gate(annexes, cl, g)
        self.assertEqual(gate["decision"], "stop_missing_documents")
        self.assertIn("12 month(s), 24 required", gate["to_request"][0]["reason"])

    def test_cli_required_and_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = os.path.join(tmp, "profile.json")
            dump(profile, {"model_type": "saas", "customer_type": "B2B"})
            req = os.path.join(tmp, "required.json")
            self.assertEqual(documents_gate.main(["required", "--grid", "series_b", "--profile", profile, "--out", req]), 0)
            with open(req, encoding="utf-8") as f:
                doc = json.load(f)
            self.assertEqual([d["id"] for d in doc["required"]], REQUIRED)
            self.assertEqual(doc["stage"], "series-b")
            self.assertEqual(doc["model"], "saas")
            ann, cl, out = (os.path.join(tmp, n) for n in ("annexes.json", "cl.json", "gate.json"))
            dump(ann, ANNEXES)
            dump(cl, classification(X10=None))
            self.assertEqual(documents_gate.main(["documents", "--grid", "series_b", "--profile", profile, "--annexes", ann, "--classification", cl, "--out", out]), 0)
            with open(out, encoding="utf-8") as f:
                g = json.load(f)
            self.assertEqual(g["decision"], "stop_missing_documents")
            self.assertEqual([m["document"] for m in g["to_request"]], ["org_chart"])
            dump(profile, {"model_type": "biotech"})
            self.assertEqual(documents_gate.main(["required", "--grid", "series_b", "--profile", profile, "--out", req]), 0)
            with open(req, encoding="utf-8") as f:
                ids = [d["id"] for d in json.load(f)["required"]]
            self.assertEqual(ids, ["pnl_36m", "accounts_audited", "cap_table", "model_3y", "board_pack_4q", "org_chart", "clinical_dossier", "ip_schedule"])


class FounderEmailTest(unittest.TestCase):
    def test_documents_email_lists_each_missing_document(self):
        g, _ = documents_gate.documents_gate(ANNEXES, classification(X2=None, X5={"months_covered": 6}), GRID)
        t = founder_email.draft("documents", "deck.pdf", "fr", g["to_request"])
        self.assertIn("Comptes annuels audités ou revus, deux derniers exercices", t)
        self.assertIn("Effectif commercial avec l'atteinte des quotas sur 12 mois", t)
        self.assertIn("covers 6 month(s), 12 required", t)
        self.assertIn("n'envoie rien", t)
        t = founder_email.draft("documents", "deck.pdf", "en", g["to_request"])
        self.assertIn("- Audited or reviewed annual accounts, last two fiscal years: Balance sheet, income statement", t)
        self.assertIn("(absent)", t)


class ScoreAndReportTest(unittest.TestCase):
    def answers(self, grid, value="found"):
        return [{"question_id": q, "value": value, "evidence": [] if value == "absent" else [{"page": 3, "quote": "q"}], "missing": "", "call_question": "ask"}
                for q in (x["id"] for _, x in grid_lib.all_questions(grid))]

    def test_b2c_zeroes_the_sales_questions_and_their_red_flags(self):
        g = grid_lib.effective_grid(GRID, {"model_type": "saas", "customer_type": "B2C"})
        s = score.compute(g, self.answers(g, "absent"), {"customer_type": "B2C", "model_type": "saas"})
        by_id = {q["question_id"]: q for q in s["questions"]}
        for qid in ("C5", "C6", "D4", "D5", "D6"):
            self.assertFalse(by_id[qid]["counted"], qid)
            self.assertEqual(by_id[qid]["status"], "information_only", qid)
        self.assertTrue(by_id["C4"]["counted"])
        # A question at weight 0 never raises a red flag: D4 and D6 drop out of the list in B2C.
        self.assertEqual(sorted(s["red_flags"]), ["B4", "E2", "G1", "H2"])
        self.assertEqual(sorted(s["red_blocks"]), ["A", "B", "C", "D", "E", "F", "G", "H", "I"])
        # Blocks of weight 3 feed the call questions; the information-only questions do not.
        self.assertIn("C4", s["call_question_ids"])
        self.assertIn("D1", s["call_question_ids"])

    def test_b2b_keeps_every_red_flag(self):
        g = grid_lib.effective_grid(GRID, {"model_type": "saas", "customer_type": "B2B"})
        s = score.compute(g, self.answers(g, "absent"), {"customer_type": "B2B", "model_type": "saas"})
        self.assertEqual(sorted(s["red_flags"]), ["B4", "D4", "D6", "E2", "G1", "H2"])
        s = score.compute(g, self.answers(g, "found"), {"customer_type": "B2B", "model_type": "saas"})
        self.assertEqual(s["red_flags"], [])
        self.assertEqual(s["global_percent"], 100)

    def test_full_report_shows_series_b_grid_and_benchmarks(self):
        profile = {"model_type": "saas", "customer_type": "B2B", "announced_stage": "series-b", "sector": "s", "business_model": "b", "deck_language": "en", "page_count": 3, "evidence": {}}
        g = grid_lib.effective_grid(GRID, profile)
        answers = self.answers(g)
        s = score.compute(g, answers, profile)
        claims = {"claims": [{"id": "K01", "page": 3, "quote": "q", "type": "nrr", "statement": "NRR 118 %", "value": 118, "status": "proven"},
                             {"id": "K02", "page": 4, "quote": "q", "type": "magic_number", "statement": "magic number 0.9", "value": 0.9, "status": "proven"},
                             {"id": "K03", "page": 5, "quote": "q", "type": "exec_team", "statement": "x is CFO", "value": None, "status": "confirmed"}]}
        gate, _ = documents_gate.documents_gate(ANNEXES, classification(), GRID)
        lab = report.L("en")
        text = report.full_report(lab, "deck.pdf", g, profile, answers, s, "### reading", {"reference_source": "pdf"}, "2026-09-14", "en", ANNEXES, claims, gate, None)
        self.assertIn("series B grid", text)
        self.assertNotIn("series A grid", text)
        self.assertIn("**Stage**: series-b", text)
        self.assertIn("Every document of the list is present.", text)
        self.assertIn("- board_pack_4q: present (X9)", text)
        self.assertIn("| Benchmark |", text)
        self.assertIn("Benchmarks shown, never scored", text)
        self.assertIn("110 to 120 %", text)  # NRR next to K01 (ICONIQ)
        self.assertIn("2021-09-21", text)  # Bessemer
        self.assertIn("0.7x", text)  # magic number next to K02 (Scale VP)
        self.assertIn("2010-04-20", text)
        # The executive claim carries no figure: no benchmark next to it.
        row = next(l for l in text.splitlines() if l.startswith("| K03 |"))
        self.assertTrue(row.endswith("| — |"))
        # Nine blocks in the completeness table.
        for bid in "ABCDEFGHI":
            self.assertIn(f"| {bid}. ", text)
        fr = report.full_report(report.L("fr"), "deck.pdf", g, profile, answers, s, "### lecture", {"reference_source": "pdf"}, "2026-09-14", "fr", ANNEXES, claims, gate, None)
        self.assertIn("grille série B", fr)
        self.assertIn("Tous les documents de la liste sont présents.", fr)

    def test_abort_report_missing_documents_in_french(self):
        profile = {"model_type": "saas", "customer_type": "B2B", "announced_stage": "series-b", "evidence": {}}
        g = grid_lib.effective_grid(GRID, profile)
        gate, _ = documents_gate.documents_gate(ANNEXES, classification(X9=None), GRID)
        email = founder_email.draft("documents", "deck.pdf", "fr", gate["to_request"])
        text = report.abort_report(report.L("fr"), "deck.pdf", g, profile, "2026-09-14", "missing_documents", "board_pack_4q missing", ANNEXES, None, gate, email, {"reference_source": "pdf"}, "fr")
        self.assertIn("Lecture interrompue", text)
        self.assertIn("grille série B", text)
        self.assertIn("Supports ou comptes rendus de board, quatre derniers trimestres", text)
        self.assertIn("pnl_36m: présent", text)
        self.assertIn("accounts_audited: présent", text)
        self.assertIn("Brouillon d'email", text)
        self.assertIn("(absent)", text)

    def test_report_cli_end_to_end_abort(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile, ann, gate_path, out = (os.path.join(tmp, n) for n in ("profile.json", "annexes.json", "gate.json", "deck.reading.md"))
            dump(profile, {"model_type": "hardware", "customer_type": "B2B", "announced_stage": "series-b", "evidence": {}})
            dump(ann, ANNEXES)
            gate, _ = documents_gate.documents_gate(ANNEXES, classification(), grid_lib.effective_grid(GRID, {"model_type": "hardware"}))
            dump(gate_path, gate)
            self.assertEqual(report.main(["--grid", "series_b", "--deck", "deck.pdf", "--profile", profile, "--annexes", ann, "--gate", gate_path,
                                          "--lang", "en", "--out", out, "--no-pdf", "--abort-kind", "missing_documents", "--abort-reason", "bom_and_suppliers, inventory_24m missing"]), 0)
            with open(out, encoding="utf-8") as f:
                text = f.read()
            self.assertIn("series B grid", text)
            self.assertIn("Bill of materials and supplier terms", text)
            self.assertIn("Inventory, warranty claims and returns over 24 months", text)
            self.assertIn("**Model-specific questions applied**: hardware", text)


if __name__ == "__main__":
    unittest.main()

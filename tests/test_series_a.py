"""Tests for the series A grid: routing, readable copy, documents gate, founder email, report."""
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
import series_a_gate  # noqa: E402

GRID = grid_lib.load_grid("series_a")
REQUIRED = [d["id"] for d in GRID["annex_gate"]["required_documents"]]


def annex(aid, text, kind="csv"):
    return {"id": aid, "file": f"{aid}.{kind}", "kind": kind, "pages": [{"number": 1, "text": text}]}


ANNEXES = {"annex_count": 6, "readable_count": 6, "annexes": [
    annex("X1", "Month\tRevenue\tCOGS\tOpex\tNet burn\n2024-09\t100\t20\t80\t-10"),
    annex("X2", "Cohort\tM0\tM1\tM2\tM12"),
    annex("X3", "Deal\tStage\tProbability\tAmount\tOwner\tFirst contact\tSigned"),
    annex("X4", "Holder\tShares\tPercent\tOption pool"),
    annex("X5", "Model 2026-2029\tRevenue\tExpenses\tCash\tHires", "xlsx"),
    annex("X6", "MASTER SUBSCRIPTION AGREEMENT between Gantrix and Ferrolux SAS", "pdf"),
]}


def classification(**overrides):
    base = {
        "X1": {"type": "pnl_24m", "quote": "Month\tRevenue\tCOGS", "months_covered": 24},
        "X2": {"type": "cohorts_12m", "quote": "Cohort\tM0\tM1", "months_covered": 13},
        "X3": {"type": "crm_pipeline", "quote": "Deal\tStage\tProbability", "months_covered": None},
        "X4": {"type": "cap_table", "quote": "Holder\tShares", "months_covered": None},
        "X5": {"type": "model_3y", "quote": "Model 2026-2029", "months_covered": 36},
        "X6": {"type": "top10_contracts", "quote": "MASTER SUBSCRIPTION AGREEMENT", "months_covered": None, "items_covered": 10},
    }
    for k, v in overrides.items():
        if v is None:
            base.pop(k)
        else:
            base[k].update(v)
    return {"annexes": [dict(annex_id=k, **v) for k, v in base.items()]}


class RoutingTest(unittest.TestCase):
    def test_stage_spellings_route_to_series_a(self):
        for s in ("series A", "Series A", "série A", "series-a", "series_a", "serie a", "SERIES A"):
            self.assertEqual(grid_lib.stage_key(s), "series_a", s)
            self.assertEqual(grid_lib.load_grid(s)["stage"], "series-a", s)
        self.assertEqual(grid_lib.stage_key(GRID), "series_a")
        self.assertEqual(grid_lib.stage_key("pre-seed"), "preseed")
        with self.assertRaises(grid_lib.GridError):
            grid_lib.stage_key("series B")

    def test_grid_shape_matches_seed_schema(self):
        seed = grid_lib.load_grid("seed")
        for key in ("scale", "confirmation", "proof", "annex_gate", "gaps", "web", "claim_types", "blocks"):
            self.assertIn(key, GRID, key)
        self.assertEqual(GRID["scale"], seed["scale"])
        for k in ("minor_max_ratio", "probe_max_ratio"):
            self.assertEqual(GRID["gaps"][k], seed["gaps"][k], k)
        self.assertEqual(GRID["web"]["min_independent_sources"], seed["web"]["min_independent_sources"])
        self.assertEqual(REQUIRED, ["pnl_24m", "cohorts_12m", "crm_pipeline", "cap_table", "model_3y", "top10_contracts"])
        for t in ("nrr", "pipeline", "sales_cycle", "gross_margin", "concentration", "burn_multiple", "founder_sales", "key_hire", "reviews", "job_posts"):
            self.assertIn(t, GRID["claim_types"], t)
            self.assertIn(t, claim_types.MEANING, t)
        weights = {b["id"]: b["weight"] for b in GRID["blocks"]}
        self.assertEqual(weights["C"], 3)
        self.assertEqual(weights["D"], 3)
        self.assertEqual(weights["B"], 2)

    def test_readable_grid_matches_json(self):
        with open(os.path.join(HERE, "..", "skills", "deck-reader", "grids", "series_a.md"), encoding="utf-8") as f:
            md = f.read()
        for _, q in grid_lib.all_questions(GRID):
            self.assertIn(f"| {q['id']} |", md, f"{q['id']} missing from series_a.md")
        self.assertIn(GRID["version"], md)
        for d in REQUIRED:
            self.assertIn(d, md)


class DocumentsGateTest(unittest.TestCase):
    def test_all_present_continues(self):
        g, invalid = series_a_gate.documents_gate(ANNEXES, classification(), GRID)
        self.assertEqual(invalid, [])
        self.assertEqual(g["decision"], "continue")
        self.assertEqual([p["document"] for p in g["present"]], REQUIRED)
        self.assertEqual(g["to_request"], [])

    def test_one_missing_document_stops_and_lists_it(self):
        g, _ = series_a_gate.documents_gate(ANNEXES, classification(X4=None), GRID)
        self.assertEqual(g["decision"], "stop_missing_documents")
        self.assertEqual([m["document"] for m in g["to_request"]], ["cap_table"])
        self.assertEqual(g["to_request"][0]["reason"], "absent")

    def test_too_few_months_stops(self):
        g, _ = series_a_gate.documents_gate(ANNEXES, classification(X1={"months_covered": 18}), GRID)
        self.assertEqual(g["decision"], "stop_missing_documents")
        self.assertEqual(g["to_request"][0]["document"], "pnl_24m")
        self.assertIn("18 month(s), 24 required", g["to_request"][0]["reason"])

    def test_too_few_contracts_stops(self):
        g, _ = series_a_gate.documents_gate(ANNEXES, classification(X6={"items_covered": 7}), GRID)
        self.assertEqual(g["decision"], "stop_missing_documents")
        self.assertIn("7 item(s), 10 required", g["to_request"][0]["reason"])

    def test_quote_not_in_annex_is_invalid_and_document_missing(self):
        g, invalid = series_a_gate.documents_gate(ANNEXES, classification(X2={"quote": "not there"}), GRID)
        self.assertEqual(invalid[0]["reason"], "quote_not_in_annex")
        self.assertEqual([m["document"] for m in g["to_request"]], ["cohorts_12m"])

    def test_no_annex_at_all_lists_the_six(self):
        g, _ = series_a_gate.documents_gate({"annex_count": 0, "readable_count": 0, "annexes": []}, {"annexes": []}, GRID)
        self.assertEqual(g["decision"], "stop_missing_documents")
        self.assertEqual([m["document"] for m in g["to_request"]], REQUIRED)

    def test_other_type_is_ignored_not_invalid(self):
        cl = classification()
        cl["annexes"].append({"annex_id": "X1", "type": "other", "quote": "", "months_covered": None})
        g, invalid = series_a_gate.documents_gate(ANNEXES, cl, GRID)
        self.assertEqual(invalid, [])
        self.assertEqual(g["decision"], "continue")

    def test_cli_required_and_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            req = os.path.join(tmp, "required.json")
            self.assertEqual(series_a_gate.main(["required", "--grid", "series_a", "--out", req]), 0)
            with open(req, encoding="utf-8") as f:
                self.assertEqual([d["id"] for d in json.load(f)["required"]], REQUIRED)
            ann, cl, out = (os.path.join(tmp, n) for n in ("annexes.json", "cl.json", "gate.json"))
            json.dump(ANNEXES, open(ann, "w", encoding="utf-8"))
            json.dump(classification(X5=None), open(cl, "w", encoding="utf-8"))
            self.assertEqual(series_a_gate.main(["documents", "--grid", "series_a", "--annexes", ann, "--classification", cl, "--out", out]), 0)
            with open(out, encoding="utf-8") as f:
                self.assertEqual(json.load(f)["decision"], "stop_missing_documents")


class FounderEmailTest(unittest.TestCase):
    def test_documents_email_lists_each_missing_document(self):
        g, _ = series_a_gate.documents_gate(ANNEXES, classification(X4=None, X1={"months_covered": 12}), GRID)
        t = founder_email.draft("documents", "deck.pdf", "fr", g["to_request"])
        self.assertIn("P&L mensuel sur 24 mois", t)
        self.assertIn("covers 12 month(s), 24 required", t)
        self.assertIn("Table de capitalisation", t)
        self.assertIn("n'envoie rien", t)
        t = founder_email.draft("documents", "deck.pdf", "en", g["to_request"])
        self.assertIn("- Cap table: Every holder with its share", t)


class ScoreAndReportTest(unittest.TestCase):
    def answers(self, grid, value="found"):
        return [{"question_id": q, "value": value, "evidence": [] if value == "absent" else [{"page": 3, "quote": "q"}], "missing": "", "call_question": "ask"}
                for q in (x["id"] for _, x in grid_lib.all_questions(grid))]

    def test_c3_is_zero_in_b2c_and_red_flags(self):
        g = grid_lib.effective_grid(GRID, {"model_type": "saas", "customer_type": "B2C"})
        s = score.compute(g, self.answers(g, "absent"), {"customer_type": "B2C", "model_type": "saas"})
        self.assertFalse(next(q for q in s["questions"] if q["question_id"] == "C3")["counted"])
        self.assertEqual(sorted(s["red_flags"]), ["B4", "C6", "D2", "F2", "G2"])
        self.assertEqual(sorted(s["red_blocks"]), ["A", "B", "C", "D", "E", "F", "G", "H"])

    def test_full_report_shows_benchmarks_next_to_figures(self):
        profile = {"model_type": "saas", "customer_type": "B2B", "announced_stage": "series-a", "sector": "s", "business_model": "b", "deck_language": "en", "page_count": 3, "evidence": {}}
        g = grid_lib.effective_grid(GRID, profile)
        answers = self.answers(g)
        s = score.compute(g, answers, profile)
        claims = {"claims": [{"id": "K01", "page": 3, "quote": "q", "type": "nrr", "statement": "NRR 118 %", "value": 118, "status": "proven"},
                             {"id": "K02", "page": 4, "quote": "q", "type": "founder", "statement": "x", "value": None, "status": "confirmed"}]}
        gate, _ = series_a_gate.documents_gate(ANNEXES, classification(), GRID)
        lab = report.L("en")
        text = report.full_report(lab, "deck.pdf", g, profile, answers, s, "### reading", {"reference_source": "pdf"}, "2026-09-13", "en", ANNEXES, claims, gate, None)
        self.assertIn("series A grid", text)
        self.assertIn("Every document of the fixed list is present.", text)
        self.assertIn("| Benchmark |", text)
        self.assertIn("110 to 120 percent competitive".replace(" percent", " %"), text)  # NRR next to K01
        self.assertIn("Benchmarks shown, never scored", text)
        self.assertIn("2026-03-31", text)
        # The founder claim carries no figure: no benchmark next to it.
        row = next(l for l in text.splitlines() if l.startswith("| K02 |"))
        self.assertTrue(row.endswith("| — |"))

    def test_abort_report_missing_documents(self):
        profile = {"model_type": "saas", "customer_type": "B2B", "announced_stage": "series-a", "evidence": {}}
        g = grid_lib.effective_grid(GRID, profile)
        gate, _ = series_a_gate.documents_gate(ANNEXES, classification(X3=None), GRID)
        email = founder_email.draft("documents", "deck.pdf", "en", gate["to_request"])
        text = report.abort_report(report.L("fr"), "deck.pdf", g, profile, "2026-09-13", "missing_documents", "crm_pipeline missing", ANNEXES, None, gate, email, {"reference_source": "pdf"}, "fr")
        self.assertIn("Lecture interrompue", text)
        self.assertIn("Export CRM avec pipeline pondéré", text)
        self.assertIn("pnl_24m: présent", text)
        self.assertIn("Brouillon d'email", text)

    def test_preseed_report_has_no_benchmark_column(self):
        pre = grid_lib.effective_grid(grid_lib.load_grid("preseed"), {"customer_type": "B2B"})
        answers = self.answers(pre)
        s = score.compute(pre, answers, {"customer_type": "B2B"})
        text = report.full_report(report.L("en"), "deck.pdf", pre, {"customer_type": "B2B", "evidence": {}}, answers, s, "r", {"reference_source": "pdf"}, "2026-09-13", "en", None, None, None, None)
        self.assertNotIn("| Benchmark |", text)
        self.assertNotIn("Benchmarks shown", text)


if __name__ == "__main__":
    unittest.main()

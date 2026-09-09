"""Tests for the seed pipeline scripts: claims, annexes, gates, web rules, proof cap, email."""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
sys.path.insert(0, os.path.join(HERE, "..", "fixtures"))

import annex_text  # noqa: E402
import apply_proof_cap  # noqa: E402
import check_claims  # noqa: E402
import claims_lib  # noqa: E402
import founder_email  # noqa: E402
import grid_lib  # noqa: E402
import score  # noqa: E402
import seed_gate  # noqa: E402
import verify_matches  # noqa: E402
import verify_web  # noqa: E402

GRID = grid_lib.load_grid("seed")

PAGES = {"pages": [
    {"number": 1, "text": "GANTRIX\nSeed round - September 2026"},
    {"number": 6, "text": "42 paying customers as of August 2026, first payment in November 2025.\nMRR: 8,200 EUR in June 2026, 9,900 EUR in July 2026, 12,100 EUR in August 2026."},
    {"number": 9, "text": "Marc Delorme, CTO. 6 years at Datadog as a staff engineer."},
]}


def claim(cid, page, quote, ctype, value=None, statement="s"):
    return {"id": cid, "page": page, "quote": quote, "type": ctype, "statement": statement, "value": value, "unit": "", "date": ""}


CLAIMS_RAW = {"claims": [
    claim("K01", 6, "42 paying customers as of August 2026", "customers", 42, "42 paying customers in August 2026"),
    claim("K02", 6, "12,100 EUR in August 2026", "revenue", 12100, "MRR 12,100 EUR in August 2026"),
    claim("K03", 9, "6 years at Datadog as a staff engineer", "founder", None, "Marc Delorme, staff engineer at Datadog for 6 years"),
]}

ANNEXES = {"annex_count": 1, "readable_count": 1, "annexes": [
    {"id": "X1", "file": "revenue.csv", "kind": "csv", "pages": [{"number": 1, "text": "month\tmrr_eur\tpaying_customers\n2026-08\t12100\t38"}]},
]}


class GapTest(unittest.TestCase):
    def test_minor_to_probe_blatant_thresholds(self):
        self.assertEqual(claims_lib.classify_gap(42, 38, GRID)[0], "minor")      # 10.5 %
        self.assertEqual(claims_lib.classify_gap(60, 38, GRID)[0], "to_probe")   # 58 %
        self.assertEqual(claims_lib.classify_gap(100, 38, GRID)[0], "blatant")   # 163 %
        self.assertEqual(claims_lib.classify_gap(None, 38, GRID), (None, None))
        self.assertEqual(claims_lib.classify_gap("12,100", 12100, GRID)[0], "minor")

    def test_worst_status_order(self):
        self.assertEqual(claims_lib.worst("proven", "unverifiable"), "unverifiable")
        self.assertEqual(claims_lib.worst("confirmed", "to_probe"), "to_probe")
        self.assertEqual(claims_lib.worst("blatant", "proven"), "blatant")
        self.assertIsNone(claims_lib.worst(None, None))

    def test_distinct_domains_ignores_www_and_duplicates(self):
        srcs = [{"url": "https://www.a.com/x"}, {"url": "https://a.com/y"}, {"url": "https://b.org/"}]
        self.assertEqual(claims_lib.distinct_domains(srcs), {"a.com", "b.org"})


class CheckClaimsTest(unittest.TestCase):
    def test_valid_claims_get_check_and_proof(self):
        valid, invalid = check_claims.check(CLAIMS_RAW, PAGES, GRID)
        self.assertEqual(invalid, [])
        by_id = {c["id"]: c for c in valid}
        self.assertEqual(by_id["K01"]["check"], "annex")
        self.assertEqual(by_id["K03"]["check"], "web")
        self.assertIn("Stripe", by_id["K02"]["proof"])

    def test_quote_not_on_page_and_unknown_type(self):
        raw = {"claims": [claim("K01", 6, "99 paying customers", "customers", 99),
                          claim("K02", 6, "42 paying customers", "unicorns", 42)]}
        valid, invalid = check_claims.check(raw, PAGES, GRID)
        self.assertEqual([i["id"] for i in invalid], ["K01"])
        self.assertEqual(invalid[0]["reason"], "quote_not_on_page")
        self.assertEqual(valid[0]["type"], "other")
        self.assertEqual(valid[0]["check"], "none")

    def test_duplicate_id_rejected(self):
        raw = {"claims": [claim("K01", 6, "42 paying customers", "customers", 42), claim("K01", 6, "42 paying customers", "customers", 42)]}
        valid, invalid = check_claims.check(raw, PAGES, GRID)
        self.assertEqual(len(valid), 1)
        self.assertEqual(invalid[0]["reason"], "missing_or_duplicate_id")


class VerifyMatchesTest(unittest.TestCase):
    def setUp(self):
        self.claims_doc = {"claims": check_claims.check(CLAIMS_RAW, PAGES, GRID)[0]}

    def test_minor_gap_is_proven_and_exact_is_proven(self):
        matches = {"matches": [
            {"claim_id": "K01", "status": "contradicted", "evidence": [{"annex_id": "X1", "page": 1, "quote": "2026-08\t12100\t38"}], "found_value": 38},
            {"claim_id": "K02", "status": "proven", "evidence": [{"annex_id": "X1", "page": 1, "quote": "2026-08\t12100"}], "found_value": 12100},
        ]}
        claims, invalid = verify_matches.verify(self.claims_doc, matches, ANNEXES, GRID)
        self.assertEqual(invalid, [])
        by_id = {c["id"]: c for c in claims}
        self.assertEqual(by_id["K01"]["annex_status"], "proven")  # 10 % gap: the code overrides the matcher
        self.assertEqual(by_id["K01"]["gap_class"], "minor")
        self.assertEqual(by_id["K02"]["annex_status"], "proven")
        self.assertNotIn("annex_status", by_id["K03"])  # web claim untouched

    def test_big_gap_is_blatant_and_missing_match_is_not_covered(self):
        matches = {"matches": [
            {"claim_id": "K01", "status": "proven", "evidence": [{"annex_id": "X1", "page": 1, "quote": "2026-08\t12100\t38"}], "found_value": 12},
        ]}
        claims, _ = verify_matches.verify(self.claims_doc, matches, ANNEXES, GRID)
        by_id = {c["id"]: c for c in claims}
        self.assertEqual(by_id["K01"]["annex_status"], "blatant")   # deck 42 vs 12, even if the matcher said proven
        self.assertEqual(by_id["K02"]["annex_status"], "not_covered")

    def test_quote_not_in_annex_is_invalid_then_not_covered(self):
        matches = {"matches": [{"claim_id": "K02", "status": "proven", "evidence": [{"annex_id": "X1", "page": 1, "quote": "not there"}], "found_value": 12100}]}
        claims, invalid = verify_matches.verify(self.claims_doc, matches, ANNEXES, GRID)
        self.assertEqual(invalid[0]["reason"], "quote_not_in_annex")
        by_id = {c["id"]: c for c in claims}
        self.assertEqual(by_id["K02"]["annex_status"], "not_covered")
        self.assertTrue(by_id["K02"]["annex_match_invalid"])

    def test_contradicted_without_figures_is_blatant(self):
        matches = {"matches": [{"claim_id": "K01", "status": "contradicted", "evidence": [{"annex_id": "X1", "page": 1, "quote": "paying_customers"}], "found_value": None}]}
        claims, _ = verify_matches.verify(self.claims_doc, matches, ANNEXES, GRID)
        self.assertEqual(next(c for c in claims if c["id"] == "K01")["annex_status"], "blatant")


class AnnexGateTest(unittest.TestCase):
    def doc(self, statuses):
        claims = check_claims.check(CLAIMS_RAW, PAGES, GRID)[0]
        for c in claims:
            if c["id"] in statuses:
                c["annex_status"] = statuses[c["id"]]
        return {"claims": claims}

    def test_no_annex_stops(self):
        g = seed_gate.annex_gate(self.doc({"K01": "not_covered", "K02": "not_covered"}), {"readable_count": 0}, GRID)
        self.assertEqual(g["decision"], "stop_no_annexes")

    def test_insufficient_coverage_stops_and_lists_requests(self):
        g = seed_gate.annex_gate(self.doc({"K01": "not_covered", "K02": "not_covered"}), {"readable_count": 1}, GRID)
        self.assertEqual(g["decision"], "stop_insufficient")
        self.assertEqual(g["key_coverage"], 0)
        self.assertEqual([r["id"] for r in g["to_request"]], ["K01", "K02"])

    def test_half_coverage_continues_with_leftovers(self):
        g = seed_gate.annex_gate(self.doc({"K01": "proven", "K02": "not_covered"}), {"readable_count": 1}, GRID)
        self.assertEqual(g["decision"], "continue")
        self.assertEqual(g["key_coverage"], 0.5)
        self.assertEqual([r["id"] for r in g["to_request"]], ["K02"])

    def test_no_key_claim_continues(self):
        doc = {"claims": [dict(claim("K09", 9, "q", "founder"), check="web")]}
        g = seed_gate.annex_gate(doc, {"readable_count": 1}, GRID)
        self.assertEqual(g["decision"], "continue")
        self.assertIsNone(g["key_coverage"])


class VerifyWebTest(unittest.TestCase):
    def claims(self):
        cl = check_claims.check(CLAIMS_RAW, PAGES, GRID)[0]
        for c in cl:
            if c["check"] == "annex":
                c["annex_status"] = "proven"
        return cl

    def test_one_domain_is_unverifiable(self):
        web = {"results": [{"claim_id": "K03", "status": "confirmed", "for": [{"url": "https://linkedin.com/in/x", "quote": "q"}], "against": []}]}
        out = verify_web.finalize(verify_web.apply_web(self.claims(), web, GRID))
        k3 = next(c for c in out if c["id"] == "K03")
        self.assertEqual(k3["web_status"], "unverifiable")
        self.assertEqual(k3["status"], "unverifiable")
        self.assertIn("downgraded", k3["web_note"])

    def test_two_domains_confirm_and_contradict(self):
        srcs = [{"url": "https://linkedin.com/in/x", "quote": "q"}, {"url": "https://conf.org/s", "quote": "q"}]
        web = {"results": [{"claim_id": "K03", "status": "confirmed", "for": srcs, "against": []}]}
        out = verify_web.finalize(verify_web.apply_web(self.claims(), web, GRID))
        self.assertEqual(next(c for c in out if c["id"] == "K03")["status"], "confirmed")
        web = {"results": [{"claim_id": "K03", "status": "contradicted", "for": [], "against": srcs}]}
        out = verify_web.finalize(verify_web.apply_web(self.claims(), web, GRID))
        self.assertEqual(next(c for c in out if c["id"] == "K03")["status"], "blatant")

    def test_no_result_is_unverifiable_and_annex_claims_keep_status(self):
        out = verify_web.finalize(verify_web.apply_web(self.claims(), None, GRID))
        by_id = {c["id"]: c for c in out}
        self.assertEqual(by_id["K03"]["status"], "unverifiable")
        self.assertEqual(by_id["K01"]["status"], "proven")


class ContradictionsGateTest(unittest.TestCase):
    def test_explanation_lowers_to_probe_else_stops(self):
        doc = {"claims": [dict(claim("K01", 6, "q", "customers", 42), status="blatant"), dict(claim("K02", 6, "q", "revenue", 12100), status="blatant"), dict(claim("K03", 9, "q", "founder"), status="confirmed")]}
        review = {"reviews": [{"claim_id": "K01", "explanation_found": True, "explanation": "Different period.", "sources": []},
                              {"claim_id": "K02", "explanation_found": False, "explanation": "", "sources": []}]}
        g, out = seed_gate.contradictions_gate(doc, review)
        self.assertEqual(g["decision"], "stop_contradiction")
        self.assertEqual(g["stopping"], ["K02"])
        self.assertEqual(g["lowered_to_probe"], ["K01"])
        by_id = {c["id"]: c for c in out["claims"]}
        self.assertEqual(by_id["K01"]["status"], "to_probe")
        self.assertEqual(by_id["K02"]["status"], "blatant")

    def test_empty_explanation_does_not_count(self):
        doc = {"claims": [dict(claim("K01", 6, "q", "customers", 42), status="blatant")]}
        g, _ = seed_gate.contradictions_gate(doc, {"reviews": [{"claim_id": "K01", "explanation_found": True, "explanation": "  "}]})
        self.assertEqual(g["decision"], "stop_contradiction")


class ProofCapTest(unittest.TestCase):
    def run_cap(self, answers, claim_statuses):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "block-B.json"), "w", encoding="utf-8") as f:
                json.dump({"block": "B", "answers": answers}, f)
            prof = os.path.join(tmp, "profile.json")
            with open(prof, "w", encoding="utf-8") as f:
                json.dump({"customer_type": "B2B", "model_type": "saas"}, f)
            cp = os.path.join(tmp, "claims.json")
            with open(cp, "w", encoding="utf-8") as f:
                json.dump({"claims": [{"id": k, "status": v} for k, v in claim_statuses.items()]}, f)
            changed = apply_proof_cap.run("seed", prof, tmp, cp)
            with open(os.path.join(tmp, "block-B.json"), encoding="utf-8") as f:
                return changed, {a["question_id"]: a for a in json.load(f)["answers"]}

    def ans(self, qid, value, ids):
        return {"question_id": qid, "value": value, "evidence": [{"page": 6, "quote": "q"}], "claim_ids": ids, "missing": "", "call_question": ""}

    def test_found_without_proven_claim_is_capped(self):
        changed, by_id = self.run_cap([self.ans("B2", "found", ["K02"])], {"K02": "not_covered"})
        self.assertEqual(by_id["B2"]["value"], "partial")
        self.assertTrue(by_id["B2"]["capped"])
        self.assertIn(("B2", "capped"), changed)

    def test_found_with_proven_claim_stays(self):
        _, by_id = self.run_cap([self.ans("B2", "found", ["K02"])], {"K02": "proven"})
        self.assertEqual(by_id["B2"]["value"], "found")
        self.assertNotIn("capped", by_id["B2"])

    def test_found_with_no_claim_ids_is_capped(self):
        _, by_id = self.run_cap([self.ans("B1", "found", [])], {})
        self.assertEqual(by_id["B1"]["value"], "partial")

    def test_to_probe_lowers_one_step(self):
        _, by_id = self.run_cap([self.ans("B1", "found", ["K01"]), self.ans("B5", "partial", ["K01"])], {"K01": "to_probe"})
        self.assertEqual(by_id["B1"]["value"], "partial")  # one gap, one step: found -> partial, no cap on top
        self.assertEqual(by_id["B5"]["value"], "absent")
        self.assertEqual(by_id["B5"]["downgraded_by"], ["K01"])

    def test_question_without_proof_rule_untouched(self):
        _, by_id = self.run_cap([self.ans("B4", "found", ["K05"]), {"question_id": "A2", "value": "found", "evidence": [], "claim_ids": [], "missing": "", "call_question": ""}], {"K05": "confirmed"})
        self.assertEqual(by_id["B4"]["value"], "found")


class SeedScoreTest(unittest.TestCase):
    def test_marketplace_questions_are_added_and_scored(self):
        g = grid_lib.effective_grid(GRID, {"model_type": "marketplace"})
        ids = [q["id"] for _, q in grid_lib.all_questions(g)]
        self.assertIn("M1", ids)
        self.assertEqual(g["applied_model_questions"], "marketplace")
        answers = [{"question_id": q, "value": "found", "evidence": [], "missing": "", "call_question": ""} for q in ids]
        s = score.compute(g, answers, {"customer_type": "B2B", "model_type": "marketplace"})
        self.assertEqual(s["global_percent"], 100)
        block_b = next(b for b in s["blocks"] if b["id"] == "B")
        self.assertEqual(block_b["max"], 10 * 2 * 3)  # 6 + 4 questions

    def test_saas_has_no_model_questions_and_c4_is_zero_in_b2c(self):
        g = grid_lib.effective_grid(GRID, {"model_type": "saas", "customer_type": "B2C"})
        ids = [q["id"] for _, q in grid_lib.all_questions(g)]
        self.assertNotIn("M1", ids)
        answers = [{"question_id": q, "value": "absent", "evidence": [], "missing": "", "call_question": ""} for q in ids]
        s = score.compute(g, answers, {"customer_type": "B2C", "model_type": "saas"})
        c4 = next(q for q in s["questions"] if q["question_id"] == "C4")
        self.assertFalse(c4["counted"])
        self.assertEqual(sorted(s["red_blocks"]), ["A", "B", "C", "D", "E", "F", "G"])

    def test_readable_grid_matches_json(self):
        with open(os.path.join(HERE, "..", "skills", "deck-reader", "grids", "seed.md"), encoding="utf-8") as f:
            md = f.read()
        for _, q in grid_lib.all_questions(GRID):
            self.assertIn(f"| {q['id']} |", md, f"{q['id']} missing from seed.md")
        self.assertIn(GRID["version"], md)


class AnnexTextTest(unittest.TestCase):
    def test_csv_and_xlsx_and_unsupported(self):
        import zipfile
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = os.path.join(tmp, "rev.csv")
            with open(csv_path, "w", encoding="utf-8") as f:
                f.write("month,mrr_eur\n2026-08,12100\n")
            xlsx_path = os.path.join(tmp, "cap.xlsx")
            with zipfile.ZipFile(xlsx_path, "w") as z:
                z.writestr("xl/workbook.xml", '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets><sheet name="Cap" sheetId="1"/></sheets></workbook>')
                z.writestr("xl/sharedStrings.xml", '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>Lena</t></si></sst>')
                z.writestr("xl/worksheets/sheet1.xml", '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1"><v>45</v></c></row></sheetData></worksheet>')
            other = os.path.join(tmp, "x.bin")
            open(other, "wb").write(b"\x00")
            res = annex_text.read_all([csv_path, xlsx_path, other])
            self.assertEqual(res["annex_count"], 3)
            self.assertEqual(res["readable_count"], 2)
            self.assertIn("2026-08\t12100", res["annexes"][0]["pages"][0]["text"])
            self.assertEqual(res["annexes"][1]["pages"][0]["text"], "Lena\t45")
            self.assertEqual(res["annexes"][2]["kind"], "unsupported")

    def test_seed_fixture_pdf_and_csv_are_readable(self):
        import make_seed_fixture
        import pdf_text
        res = pdf_text.extract(make_seed_fixture.base.build_pdf(make_seed_fixture.PAGES))
        self.assertEqual(res["page_count"], 14)
        self.assertIn("42 paying customers", res["pages"][4]["text"])


class FounderEmailTest(unittest.TestCase):
    def test_none_has_no_list_and_missing_lists_items(self):
        t = founder_email.draft("none", "x/deck.pdf", "fr")
        self.assertIn("deck.pdf", t)
        self.assertNotIn("Page ", t)
        t = founder_email.draft("missing", "deck.pdf", "en", [{"page": 6, "statement": "MRR 12,100 EUR", "proof": "revenue export"}])
        self.assertIn("- Page 6: \"MRR 12,100 EUR\". Document expected: revenue export.", t)
        self.assertIn("sends nothing", t)


if __name__ == "__main__":
    unittest.main()

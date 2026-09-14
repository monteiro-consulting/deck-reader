"""Tests for the business-model blocks: the four verbs, the seed + marketplace non-regression,
the default model, the pre-seed grid left untouched, the readable copies, and render_grid."""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import grid_lib  # noqa: E402
import render_grid  # noqa: E402
import score  # noqa: E402

SEED = grid_lib.load_grid("seed")
SERIES_A = grid_lib.load_grid("series_a")
SERIES_B = grid_lib.load_grid("series_b")
SERIES_C = grid_lib.load_grid("series_c")
SERIES_D = grid_lib.load_grid("series_d")
PRESEED = grid_lib.load_grid("preseed")
STAGES_WITH_DOCUMENTS = (SERIES_A, SERIES_B, SERIES_C, SERIES_D)
MODELS_MD = os.path.join(HERE, "..", "skills", "deck-reader", "grids", "models")


def ids(grid):
    return [q["id"] for _, q in grid_lib.all_questions(grid)]


def block(grid, bid):
    return next(b for b in grid["blocks"] if b["id"] == bid)


def doc_ids(grid):
    return [d["id"] for d in grid_lib.required_documents(grid)]


DOC = {"id": "t_doc", "name": {"en": "T", "fr": "T"}, "requirement": {"en": "t.", "fr": "t."}, "min_months": 6}


class VerbTest(unittest.TestCase):
    def test_remove_takes_a_question_out_by_id(self):
        g = grid_lib.apply_model_block(SEED, {"remove": ["C4"]}, "t")
        self.assertNotIn("C4", ids(g))
        self.assertEqual(len(block(g, "C")["questions"]), 3)
        self.assertEqual(g["model_block"]["removed"], ["C4"])
        self.assertIn("C4", ids(SEED))  # the stage grid on disk is untouched

    def test_remove_unknown_id_is_an_error(self):
        with self.assertRaises(grid_lib.GridError):
            grid_lib.apply_model_block(SEED, {"remove": ["Z9"]}, "t")

    def test_reweight_block_and_question(self):
        g = grid_lib.apply_model_block(SEED, {"reweight": {"blocks": {"B": 0, "C": 6}, "questions": {"A1": 1}}}, "t")
        self.assertEqual(block(g, "B")["weight"], 0)
        self.assertEqual(block(g, "C")["weight"], 6)
        a1 = next(q for _, q in grid_lib.all_questions(g) if q["id"] == "A1")
        self.assertEqual(a1["weight"], 1)
        self.assertEqual(g["model_block"]["reweighted"], {"blocks": {"B": 0, "C": 6}, "questions": {"A1": 1}})
        with self.assertRaises(grid_lib.GridError):
            grid_lib.apply_model_block(SEED, {"reweight": {"blocks": {"Z": 1}}}, "t")

    def test_add_to_existing_block_and_to_a_new_block(self):
        q = {"id": "T1", "question": {"en": "t?", "fr": "t ?"}, "found_if": "x", "note": ""}
        g = grid_lib.apply_model_block(SEED, {"add": [
            {"block": "B", "questions": [q]},
            {"block": {"id": "Z", "name": {"en": "Z", "fr": "Z"}, "weight": 2}, "questions": [dict(q, id="Z1")]},
        ]}, "t")
        self.assertEqual(block(g, "B")["questions"][-1]["id"], "T1")
        z = block(g, "Z")
        self.assertEqual(z["weight"], 2)
        self.assertEqual(z["from_model"], "t")
        self.assertEqual([x["id"] for x in z["questions"]], ["Z1"])
        self.assertEqual(g["model_block"]["added"], ["T1", "Z1"])
        with self.assertRaises(grid_lib.GridError):
            grid_lib.apply_model_block(SEED, {"add": [{"block": "B", "questions": [dict(q, id="B1")]}]}, "t")
        with self.assertRaises(grid_lib.GridError):
            grid_lib.apply_model_block(SEED, {"add": [{"block": "Z", "questions": [q]}]}, "t")

    def test_order_is_remove_then_reweight_then_add(self):
        # Reweighting a question that was removed must fail: remove runs first.
        with self.assertRaises(grid_lib.GridError):
            grid_lib.apply_model_block(SEED, {"remove": ["C4"], "reweight": {"questions": {"C4": 1}}}, "t")
        # Adding to a block reweighted to 0 keeps the block weight 0: add runs last.
        q = {"id": "T1", "question": {"en": "t?"}, "found_if": "x", "note": ""}
        g = grid_lib.apply_model_block(SEED, {"reweight": {"blocks": {"B": 0}}, "add": [{"block": "B", "questions": [q]}]}, "t")
        self.assertEqual(block(g, "B")["weight"], 0)
        self.assertIn("T1", ids(g))


class DocumentsVerbTest(unittest.TestCase):
    BASE = ["pnl_24m", "cohorts_12m", "crm_pipeline", "cap_table", "model_3y", "top10_contracts"]

    def test_remove_takes_a_document_out_by_id(self):
        g = grid_lib.apply_model_block(SERIES_A, {"documents": {"remove": ["crm_pipeline"]}}, "t")
        self.assertEqual(doc_ids(g), [d for d in self.BASE if d != "crm_pipeline"])
        self.assertEqual(g["model_block"]["documents"], {"removed": ["crm_pipeline"], "added": []})
        self.assertEqual(doc_ids(SERIES_A), self.BASE)  # the stage grid on disk is untouched
        self.assertEqual(g["blocks"], SERIES_A["blocks"])

    def test_add_appends_an_entry_with_the_grid_shape(self):
        g = grid_lib.apply_model_block(SERIES_A, {"documents": {"add": [DOC, dict(DOC, id="t_set", min_months=None, min_count=3)]}}, "t")
        self.assertEqual(doc_ids(g), self.BASE + ["t_doc", "t_set"])
        added = grid_lib.required_documents(g)[-2:]
        self.assertEqual(added[0], DOC)
        self.assertEqual(added[1]["min_count"], 3)
        self.assertIsNone(added[1]["min_months"])
        self.assertNotIn("min_count", added[0])
        self.assertEqual(g["model_block"]["documents"], {"removed": [], "added": ["t_doc", "t_set"]})

    def test_unknown_id_and_duplicate_id_are_errors(self):
        with self.assertRaises(grid_lib.GridError):
            grid_lib.apply_model_block(SERIES_A, {"documents": {"remove": ["nope"]}}, "t")
        with self.assertRaises(grid_lib.GridError):
            grid_lib.apply_model_block(SERIES_A, {"documents": {"add": [dict(DOC, id="cap_table")]}}, "t")
        with self.assertRaises(grid_lib.GridError):
            grid_lib.apply_model_block(SERIES_A, {"documents": {"add": [DOC, DOC]}}, "t")
        with self.assertRaises(grid_lib.GridError):
            grid_lib.apply_model_block(SERIES_A, {"documents": {"add": [{"id": "x", "name": {"en": "x"}}]}}, "t")

    def test_documents_on_a_stage_without_a_list_is_an_error(self):
        for stage in (SEED, PRESEED):
            with self.assertRaises(grid_lib.GridError):
                grid_lib.apply_model_block(stage, {"documents": {"remove": ["pnl_24m"]}}, "t")
            with self.assertRaises(grid_lib.GridError):
                grid_lib.apply_model_block(stage, {"documents": {"add": [DOC]}}, "t")
            g = grid_lib.apply_model_block(stage, {"documents": {}}, "t")  # an empty verb is not an error
            self.assertEqual(g["model_block"]["documents"], {"removed": [], "added": []})
            self.assertEqual(grid_lib.required_documents(g), [])

    def test_documents_run_after_the_question_verbs(self):
        q = {"id": "T1", "question": {"en": "t?"}, "found_if": "x", "note": ""}
        ops = {"remove": ["C3"], "reweight": {"blocks": {"B": 0}}, "add": [{"block": "B", "questions": [q]}],
               "documents": {"remove": ["crm_pipeline"], "add": [DOC]}}
        g = grid_lib.apply_model_block(SERIES_A, ops, "t")
        self.assertIn("T1", ids(g))
        self.assertNotIn("C3", ids(g))
        self.assertEqual(doc_ids(g), [d for d in self.BASE if d != "crm_pipeline"] + ["t_doc"])
        # A question verb that fails stops the block before the documents verb runs.
        with self.assertRaises(grid_lib.GridError):
            grid_lib.apply_model_block(SERIES_A, {"remove": ["Z9"], "documents": {"remove": ["crm_pipeline"]}}, "t")
        mb = g["model_block"]
        self.assertEqual(set(mb), {"model", "removed", "reweighted", "added", "documents"})

    def test_documents_change_alone_counts_as_applied_model_questions(self):
        fake = {"model": "docsonly", "version": "t", "name": {"en": "d"}, "stages": {"series_a": {"documents": {"remove": ["crm_pipeline"]}}}}
        known, load = grid_lib.known_models, grid_lib.load_model
        grid_lib.known_models = lambda: known() + ["docsonly"]
        grid_lib.load_model = lambda m: fake if m == "docsonly" else load(m)
        try:
            g = grid_lib.effective_grid(SERIES_A, {"model_type": "docsonly"})
            self.assertEqual(g["applied_model_questions"], "docsonly")
            self.assertEqual(g["blocks"], SERIES_A["blocks"])
            self.assertNotIn("crm_pipeline", doc_ids(g))
            s = grid_lib.effective_grid(SEED, {"model_type": "docsonly"})  # no seed section: untouched
            self.assertEqual(s["applied_model_questions"], "")
        finally:
            grid_lib.known_models, grid_lib.load_model = known, load


class AssemblyTest(unittest.TestCase):
    def test_seed_plus_marketplace_is_exactly_the_previous_seed_grid(self):
        with open(os.path.join(HERE, "fixtures", "seed-marketplace-effective.json"), encoding="utf-8") as f:
            expected = json.load(f)
        got = grid_lib.effective_grid(SEED, {"model_type": "marketplace"})
        self.assertEqual(got["blocks"], expected["blocks"])
        self.assertEqual(got["applied_model_questions"], expected["applied_model_questions"])
        self.assertEqual(ids(got), ids(expected))
        for key in ("scale", "proof", "annex_gate", "gaps", "web", "claim_types", "confirmation"):
            self.assertEqual(got[key], expected[key], key)

    def test_saas_is_the_default_and_changes_nothing(self):
        for profile in ({}, {"model_type": "saas"}, {"model_type": "unknown"}, {"model_type": "other"}, {"model_type": "spacetech"}):
            g = grid_lib.effective_grid(SEED, profile)
            self.assertEqual(g["applied_model"], "saas", profile)
            self.assertEqual(g["applied_model_questions"], "")
            self.assertEqual(g["blocks"], SEED["blocks"])

    def test_preseed_is_untouched_by_every_model(self):
        for m in grid_lib.known_models():
            g = grid_lib.effective_grid(PRESEED, {"model_type": m})
            self.assertEqual(g["blocks"], PRESEED["blocks"], m)
            self.assertEqual(g["applied_model_questions"], "", m)

    def test_every_model_assembles_at_seed_series_a_and_series_b(self):
        for m in grid_lib.known_models():
            model = grid_lib.load_model(m)
            self.assertEqual(set(model["stages"]), {"seed", "series_a", "series_b", "series_c", "series_d"}, m)
            self.assertEqual(model["version"], "2026-09-14", m)
            for stage in (SEED, SERIES_A, SERIES_B, SERIES_C, SERIES_D):
                g = grid_lib.effective_grid(stage, {"model_type": m})
                self.assertEqual(len(ids(g)), len(set(ids(g))), f"{m} {stage['stage']}: duplicate ids")
                self.assertEqual(g["applied_model"], m)
            for stage in STAGES_WITH_DOCUMENTS:
                g = grid_lib.effective_grid(stage, {"model_type": m})
                # Every claim type a model question cites exists in the stage grid (the seed grid
                # predates the series A types and is not held to this).
                for _, q in grid_lib.all_questions(g):
                    for t in q.get("claim_types") or []:
                        self.assertIn(t, stage["claim_types"], f"{m} {stage['stage']} {q['id']}: unknown claim type {t}")
                docs = grid_lib.required_documents(g)
                self.assertTrue(docs, f"{m}: empty document list at {stage['stage']}")
                self.assertEqual(len(doc_ids(g)), len(set(doc_ids(g))), f"{m} {stage['stage']}: duplicate document ids")
                for d in docs:
                    for key in ("id", "name", "requirement", "min_months"):
                        self.assertIn(key, d, f"{m} {d.get('id')}: missing {key}")
                    for lang in ("en", "fr"):
                        self.assertTrue(d["name"].get(lang) and d["requirement"].get(lang), f"{m} {d['id']}: missing {lang} label")
            self.assertEqual(grid_lib.required_documents(grid_lib.effective_grid(SEED, {"model_type": m})), [])

    def test_document_lists_per_model_at_series_a(self):
        base = ["pnl_24m", "cohorts_12m", "crm_pipeline", "cap_table", "model_3y", "top10_contracts"]
        lists = {m: doc_ids(grid_lib.effective_grid(SERIES_A, {"model_type": m})) for m in grid_lib.known_models()}
        self.assertEqual(lists["saas"], base)
        self.assertEqual(lists["marketplace"], base + ["gmv_24m"])
        self.assertEqual(lists["consumer"], ["pnl_24m", "cohorts_12m", "cap_table", "model_3y", "product_analytics_12m"])
        self.assertNotIn("crm_pipeline", lists["consumer"])
        self.assertEqual(lists["ecommerce"], ["pnl_24m", "cohorts_12m", "cap_table", "model_3y", "orders_export_24m"])
        self.assertEqual(lists["hardware"], base + ["bom_and_suppliers"])
        self.assertEqual(lists["fintech"], base + ["licence", "risk_book_24m"])
        self.assertEqual(lists["biotech"], ["pnl_24m", "cap_table", "model_3y", "clinical_dossier", "ip_schedule"])
        bio = {d["id"]: d for d in grid_lib.required_documents(grid_lib.effective_grid(SERIES_A, {"model_type": "biotech"}))}
        self.assertIsNone(bio["clinical_dossier"]["min_months"])
        cons = {d["id"]: d for d in grid_lib.required_documents(grid_lib.effective_grid(SERIES_A, {"model_type": "consumer"}))}
        self.assertEqual(cons["product_analytics_12m"]["min_months"], 12)
        self.assertEqual(grid_lib.effective_grid(SERIES_A, {"model_type": "saas"})["model_block"]["documents"], {"removed": [], "added": []})

    def test_document_lists_per_model_at_series_b(self):
        base = ["pnl_36m", "accounts_audited", "cohorts_24m", "crm_pipeline", "sales_roster", "cap_table", "model_3y", "top20_contracts", "board_pack_4q", "org_chart"]
        no_sales = ["pnl_36m", "accounts_audited", "cohorts_24m", "cap_table", "model_3y", "board_pack_4q", "org_chart"]
        lists = {m: doc_ids(grid_lib.effective_grid(SERIES_B, {"model_type": m})) for m in grid_lib.known_models()}
        self.assertEqual(lists["saas"], base)
        self.assertEqual(lists["marketplace"], base + ["gmv_36m"])
        self.assertEqual(lists["consumer"], no_sales + ["product_analytics_24m"])
        self.assertEqual(lists["ecommerce"], no_sales + ["orders_export_36m"])
        self.assertEqual(lists["hardware"], base + ["bom_and_suppliers", "inventory_24m"])
        self.assertEqual(lists["fintech"], base + ["licence", "risk_book_36m"])
        self.assertEqual(lists["biotech"], ["pnl_36m", "accounts_audited", "cap_table", "model_3y", "board_pack_4q", "org_chart", "clinical_dossier", "ip_schedule"])
        docs = {m: {d["id"]: d for d in grid_lib.required_documents(grid_lib.effective_grid(SERIES_B, {"model_type": m}))} for m in lists}
        self.assertEqual(docs["marketplace"]["gmv_36m"]["min_months"], 36)
        self.assertEqual(docs["consumer"]["product_analytics_24m"]["min_months"], 24)
        self.assertEqual(docs["ecommerce"]["orders_export_36m"]["min_months"], 36)
        self.assertIsNone(docs["hardware"]["bom_and_suppliers"]["min_months"])
        self.assertEqual(docs["hardware"]["inventory_24m"]["min_months"], 24)
        self.assertEqual(docs["fintech"]["risk_book_36m"]["min_months"], 36)
        self.assertIsNone(docs["biotech"]["clinical_dossier"]["min_months"])
        self.assertEqual(docs["saas"]["accounts_audited"]["min_count"], 2)
        self.assertEqual(grid_lib.effective_grid(SERIES_B, {"model_type": "saas"})["model_block"]["documents"], {"removed": [], "added": []})
        self.assertEqual(grid_lib.effective_grid(SERIES_B, {"model_type": "saas"})["applied_model_questions"], "")

    def test_document_lists_per_model_at_series_c(self):
        base = ["pnl_48m", "accounts_audited_3y", "cohorts_36m", "crm_pipeline", "sales_roster", "billing_export_24m",
                "cap_table_terms", "model_3y", "top20_contracts", "board_pack_8q", "org_chart"]
        no_sales = ["pnl_48m", "accounts_audited_3y", "cohorts_36m", "billing_export_24m", "cap_table_terms", "model_3y", "board_pack_8q", "org_chart"]
        lists = {m: doc_ids(grid_lib.effective_grid(SERIES_C, {"model_type": m})) for m in grid_lib.known_models()}
        self.assertEqual(lists["saas"], base)
        self.assertEqual(lists["marketplace"], base + ["gmv_48m"])
        self.assertEqual(lists["consumer"], no_sales + ["product_analytics_36m"])
        self.assertEqual(lists["ecommerce"], no_sales + ["orders_export_48m"])
        self.assertEqual(lists["hardware"], base + ["bom_and_suppliers", "inventory_36m"])
        self.assertEqual(lists["fintech"], base + ["licence", "risk_book_48m"])
        self.assertEqual(lists["biotech"], ["pnl_48m", "accounts_audited_3y", "cap_table_terms", "model_3y", "board_pack_8q", "org_chart", "clinical_dossier", "ip_schedule"])
        docs = {m: {d["id"]: d for d in grid_lib.required_documents(grid_lib.effective_grid(SERIES_C, {"model_type": m}))} for m in lists}
        self.assertEqual(docs["marketplace"]["gmv_48m"]["min_months"], 48)
        self.assertEqual(docs["consumer"]["product_analytics_36m"]["min_months"], 36)
        self.assertEqual(docs["ecommerce"]["orders_export_48m"]["min_months"], 48)
        self.assertEqual(docs["hardware"]["inventory_36m"]["min_months"], 36)
        self.assertEqual(docs["fintech"]["risk_book_48m"]["min_months"], 48)
        self.assertEqual(docs["saas"]["accounts_audited_3y"]["min_count"], 3)
        self.assertEqual(docs["saas"]["board_pack_8q"]["min_count"], 8)
        self.assertEqual(grid_lib.effective_grid(SERIES_C, {"model_type": "saas"})["applied_model_questions"], "")

    def test_document_lists_per_model_at_series_d(self):
        base = ["pnl_60m", "accounts_audited_3y", "cohorts_48m", "crm_pipeline", "sales_roster", "billing_export_36m",
                "cap_table_terms", "model_3y", "top20_contracts", "board_pack_12q", "org_chart", "management_letters_3y"]
        no_sales = ["pnl_60m", "accounts_audited_3y", "cohorts_48m", "billing_export_36m", "cap_table_terms", "model_3y",
                    "board_pack_12q", "org_chart", "management_letters_3y"]
        lists = {m: doc_ids(grid_lib.effective_grid(SERIES_D, {"model_type": m})) for m in grid_lib.known_models()}
        self.assertEqual(lists["saas"], base)
        self.assertEqual(lists["marketplace"], base + ["gmv_60m"])
        self.assertEqual(lists["consumer"], no_sales + ["product_analytics_48m"])
        self.assertEqual(lists["ecommerce"], no_sales + ["orders_export_60m"])
        self.assertEqual(lists["hardware"], base + ["bom_and_suppliers", "inventory_48m"])
        self.assertEqual(lists["fintech"], base + ["licence", "risk_book_60m"])
        self.assertEqual(lists["biotech"], ["pnl_60m", "accounts_audited_3y", "cap_table_terms", "model_3y", "board_pack_12q", "org_chart",
                                            "management_letters_3y", "clinical_dossier", "ip_schedule"])
        docs = {m: {d["id"]: d for d in grid_lib.required_documents(grid_lib.effective_grid(SERIES_D, {"model_type": m}))} for m in lists}
        self.assertEqual(docs["marketplace"]["gmv_60m"]["min_months"], 60)
        self.assertEqual(docs["consumer"]["product_analytics_48m"]["min_months"], 48)
        self.assertEqual(docs["ecommerce"]["orders_export_60m"]["min_months"], 60)
        self.assertIsNone(docs["hardware"]["bom_and_suppliers"]["min_months"])
        self.assertEqual(docs["hardware"]["inventory_48m"]["min_months"], 48)
        self.assertIsNone(docs["fintech"]["licence"]["min_months"])
        self.assertEqual(docs["fintech"]["risk_book_60m"]["min_months"], 60)
        self.assertIsNone(docs["biotech"]["clinical_dossier"]["min_months"])
        self.assertIsNone(docs["biotech"]["ip_schedule"]["min_months"])
        self.assertEqual(docs["saas"]["accounts_audited_3y"]["min_count"], 3)
        self.assertEqual(docs["saas"]["board_pack_12q"]["min_count"], 12)
        self.assertEqual(docs["saas"]["management_letters_3y"]["min_count"], 3)
        self.assertEqual(grid_lib.effective_grid(SERIES_D, {"model_type": "saas"})["model_block"]["documents"], {"removed": [], "added": []})
        self.assertEqual(grid_lib.effective_grid(SERIES_D, {"model_type": "saas"})["applied_model_questions"], "")

    def test_examples_from_the_spec_at_series_d(self):
        cons = grid_lib.effective_grid(SERIES_D, {"model_type": "consumer"})
        for qid in ("B2", "C5", "F3"):
            self.assertNotIn(qid, ids(cons), qid)
        self.assertTrue({"N1", "N2", "N3"} <= set(ids(cons)))
        self.assertEqual([q["id"] for q in block(cons, "D")["questions"]], ["D1", "D2", "D3", "D4", "D5"])
        self.assertEqual(next(q for _, q in grid_lib.all_questions(cons) if q["id"] == "B1")["weight"], 1)
        bio = grid_lib.effective_grid(SERIES_D, {"model_type": "biotech"})
        for bid in ("B", "D", "E"):
            self.assertEqual(block(bio, bid)["weight"], 0, bid)
        self.assertEqual(block(bio, "C")["weight"], 1)
        self.assertEqual(block(bio, "R")["weight"], 3)
        self.assertEqual([q["id"] for q in block(bio, "R")["questions"]], ["R1", "R2", "R3"])
        self.assertIn("since the series C", next(q for _, q in grid_lib.all_questions(bio) if q["id"] == "R1")["question"]["en"])
        for qid in ("C5", "F3", "F4"):
            self.assertNotIn(qid, ids(bio), qid)
        self.assertIn("D1", ids(bio))
        hw = grid_lib.effective_grid(SERIES_D, {"model_type": "hardware"})
        self.assertEqual(block(hw, "C")["weight"], 6)
        self.assertEqual(block(hw, "C")["weight"], 2 * block(SERIES_D, "C")["weight"])
        self.assertTrue({"P1", "P2", "P3"} <= set(ids(hw)))
        eco = grid_lib.effective_grid(SERIES_D, {"model_type": "ecommerce"})
        self.assertTrue({"O1", "O2"} <= {q["id"] for q in block(eco, "C")["questions"]})
        self.assertIn("O3", [q["id"] for q in block(eco, "E")["questions"]])
        self.assertIn("F4", ids(eco))  # pricing power stays: the billing export is on the list
        for qid in ("C5", "F3"):
            self.assertNotIn(qid, ids(eco), qid)
        fin = grid_lib.effective_grid(SERIES_D, {"model_type": "fintech"})
        self.assertEqual(block(fin, "Q")["weight"], 2)
        self.assertEqual([q["id"] for q in block(fin, "Q")["questions"]], ["Q1", "Q2", "Q3", "Q4"])
        self.assertIn("over 60 months", next(q for _, q in grid_lib.all_questions(fin) if q["id"] == "Q4")["question"]["en"])
        mkt = grid_lib.effective_grid(SERIES_D, {"model_type": "marketplace"})
        self.assertEqual([q["id"] for q in block(mkt, "B")["questions"]][-4:], ["M1", "M2", "M3", "M4"])
        self.assertIn("over 60 months", next(q for _, q in grid_lib.all_questions(mkt) if q["id"] == "M1")["question"]["en"])
        self.assertEqual(ids(grid_lib.effective_grid(SERIES_D, {"model_type": "saas"})), ids(SERIES_D))

    def test_examples_from_the_spec_at_series_c(self):
        cons = grid_lib.effective_grid(SERIES_C, {"model_type": "consumer"})
        for qid in ("B2", "C5", "D3", "D6"):
            self.assertNotIn(qid, ids(cons), qid)
        self.assertEqual([q["id"] for q in block(cons, "D")["questions"]], ["D1", "D2", "D4", "D5"])
        self.assertEqual(next(q for _, q in grid_lib.all_questions(cons) if q["id"] == "B1")["weight"], 1)
        bio = grid_lib.effective_grid(SERIES_C, {"model_type": "biotech"})
        for bid in ("B", "D", "E"):
            self.assertEqual(block(bio, bid)["weight"], 0, bid)
        self.assertEqual(block(bio, "C")["weight"], 1)
        self.assertEqual(block(bio, "R")["weight"], 3)
        for qid in ("C5", "D2", "D3", "D6"):
            self.assertNotIn(qid, ids(bio), qid)
        hw = grid_lib.effective_grid(SERIES_C, {"model_type": "hardware"})
        self.assertEqual(block(hw, "C")["weight"], 2 * block(SERIES_C, "C")["weight"])
        eco = grid_lib.effective_grid(SERIES_C, {"model_type": "ecommerce"})
        self.assertIn("O3", [q["id"] for q in block(eco, "E")["questions"]])
        self.assertIn("D2", ids(eco))
        fin = grid_lib.effective_grid(SERIES_C, {"model_type": "fintech"})
        self.assertEqual([q["id"] for q in block(fin, "Q")["questions"]], ["Q1", "Q2", "Q3", "Q4"])
        mkt = grid_lib.effective_grid(SERIES_C, {"model_type": "marketplace"})
        self.assertEqual([q["id"] for q in block(mkt, "B")["questions"]][-4:], ["M1", "M2", "M3", "M4"])
        self.assertEqual(ids(grid_lib.effective_grid(SERIES_C, {"model_type": "saas"})), ids(SERIES_C))

    def test_examples_from_the_spec_at_series_b(self):
        cons = grid_lib.effective_grid(SERIES_B, {"model_type": "consumer"})
        for qid in ("B2", "C5", "C6", "D4", "D5", "D6"):
            self.assertNotIn(qid, ids(cons), qid)
        self.assertTrue({"N1", "N2", "N3"} <= set(ids(cons)))
        self.assertEqual(next(q for _, q in grid_lib.all_questions(cons) if q["id"] == "B1")["weight"], 1)
        self.assertEqual([q["id"] for q in block(cons, "D")["questions"]], ["D1", "D2", "D3"])
        bio = grid_lib.effective_grid(SERIES_B, {"model_type": "biotech"})
        self.assertEqual(block(bio, "R")["weight"], 3)
        self.assertEqual([q["id"] for q in block(bio, "R")["questions"]], ["R1", "R2", "R3"])
        for bid in ("B", "D", "E"):
            self.assertEqual(block(bio, bid)["weight"], 0, bid)
        self.assertEqual(block(bio, "C")["weight"], 1)
        for qid in ("C5", "C6", "D4", "D5", "D6"):
            self.assertNotIn(qid, ids(bio), qid)
        hw = grid_lib.effective_grid(SERIES_B, {"model_type": "hardware"})
        self.assertEqual(block(hw, "C")["weight"], 6)
        self.assertEqual(block(hw, "C")["weight"], 2 * block(SERIES_B, "C")["weight"])
        self.assertTrue({"P1", "P2", "P3"} <= set(ids(hw)))
        eco = grid_lib.effective_grid(SERIES_B, {"model_type": "ecommerce"})
        self.assertTrue({"O1", "O2", "O3"} <= set(ids(eco)))
        self.assertIn("O3", [q["id"] for q in block(eco, "E")["questions"]])
        self.assertIn("C2", ids(eco))  # the series B design keeps the generic CAC payback
        for qid in ("C5", "C6", "D4", "D5", "D6"):
            self.assertNotIn(qid, ids(eco), qid)
        fin = grid_lib.effective_grid(SERIES_B, {"model_type": "fintech"})
        self.assertEqual(block(fin, "Q")["weight"], 2)
        self.assertEqual([q["id"] for q in block(fin, "Q")["questions"]], ["Q1", "Q2", "Q3", "Q4"])
        mkt = grid_lib.effective_grid(SERIES_B, {"model_type": "marketplace"})
        self.assertEqual([q["id"] for q in block(mkt, "B")["questions"]][-4:], ["M1", "M2", "M3", "M4"])
        self.assertEqual(ids(grid_lib.effective_grid(SERIES_B, {"model_type": "saas"})), ids(SERIES_B))

    def test_examples_from_the_spec(self):
        bio = grid_lib.effective_grid(SEED, {"model_type": "biotech"})
        self.assertEqual(block(bio, "B")["weight"], 0)
        self.assertEqual([q["id"] for q in block(bio, "R")["questions"]], ["R1", "R2", "R3"])
        hw = grid_lib.effective_grid(SEED, {"model_type": "hardware"})
        self.assertEqual(block(hw, "C")["weight"], 2 * block(SEED, "C")["weight"])
        self.assertTrue({"P1", "P2", "P3"} <= set(ids(hw)))
        cons = grid_lib.effective_grid(SEED, {"model_type": "consumer"})
        self.assertTrue({"N1", "N2", "N3"} <= set(ids(cons)))
        self.assertEqual(next(q for _, q in grid_lib.all_questions(cons) if q["id"] == "B2")["weight"], 1)
        eco = grid_lib.effective_grid(SERIES_A, {"model_type": "ecommerce"})
        self.assertTrue({"O1", "O2", "O3"} <= set(ids(eco)))
        self.assertNotIn("C2", ids(eco))
        fin = grid_lib.effective_grid(SERIES_A, {"model_type": "fintech"})
        self.assertEqual(block(fin, "Q")["weight"], 2)

    def test_weight_zero_block_is_information_only_in_the_score(self):
        g = grid_lib.effective_grid(SEED, {"model_type": "biotech"})
        answers = [{"question_id": q, "value": "absent", "evidence": [], "missing": "", "call_question": ""} for q in ids(g)]
        s = score.compute(g, answers, {"customer_type": "B2B", "model_type": "biotech"})
        b = next(x for x in s["blocks"] if x["id"] == "B")
        self.assertTrue(b["information_only"])
        self.assertFalse(b["red"])
        self.assertNotIn("B", s["red_blocks"])
        self.assertIn("R", s["red_blocks"])
        self.assertEqual(s["global_percent"], 0)
        # Series B biotech: B, D and E are information only, and their red flags (B4, E2) do not fire.
        g = grid_lib.effective_grid(SERIES_B, {"model_type": "biotech"})
        answers = [{"question_id": q, "value": "absent", "evidence": [], "missing": "", "call_question": ""} for q in ids(g)]
        s = score.compute(g, answers, {"customer_type": "B2B", "model_type": "biotech"})
        for bid in ("B", "D", "E"):
            self.assertNotIn(bid, s["red_blocks"], bid)
        self.assertIn("R", s["red_blocks"])
        self.assertEqual(sorted(s["red_flags"]), ["G1", "H2"])
        # Series C biotech: the same; D1 (plan vs actual) is asked for information and does not fire either.
        g = grid_lib.effective_grid(SERIES_C, {"model_type": "biotech"})
        answers = [{"question_id": q, "value": "absent", "evidence": [], "missing": "", "call_question": ""} for q in ids(g)]
        s = score.compute(g, answers, {"customer_type": "B2B", "model_type": "biotech"})
        for bid in ("B", "D", "E"):
            self.assertNotIn(bid, s["red_blocks"], bid)
        self.assertEqual(sorted(s["red_flags"]), ["G1", "H2"])
        # Series D biotech: B, D and E are information only (B4, D1, E2 do not fire); the round's reason (H3) does.
        g = grid_lib.effective_grid(SERIES_D, {"model_type": "biotech"})
        answers = [{"question_id": q, "value": "absent", "evidence": [], "missing": "", "call_question": ""} for q in ids(g)]
        s = score.compute(g, answers, {"customer_type": "B2B", "model_type": "biotech"})
        for bid in ("B", "D", "E"):
            self.assertNotIn(bid, s["red_blocks"], bid)
        self.assertIn("R", s["red_blocks"])
        self.assertEqual(sorted(s["red_flags"]), ["G1", "H2", "H3"])


class BenchmarkTest(unittest.TestCase):
    def test_every_benchmark_has_source_and_date_or_is_empty(self):
        for m in grid_lib.known_models():
            for stage in ("seed", "series_a", "series_b", "series_c", "series_d"):
                bms = grid_lib.load_benchmarks(m, stage)
                self.assertTrue(bms, f"{m} {stage}: no benchmark list")
                for b in bms:
                    if b.get("value"):
                        self.assertTrue(b.get("source"), f"{b['id']}: value without source")
                        if stage in ("series_b", "series_c", "series_d"):  # the series B, C and D guardrail: a value needs a dated source
                            self.assertTrue(b.get("date"), f"{b['id']}: value without a date")
                    if b.get("date"):
                        self.assertTrue(b.get("source"), f"{b['id']}: date without source")
                    if not b.get("value"):
                        self.assertTrue(b.get("note"), f"{b['id']}: empty value without a note")
                    self.assertTrue(b.get("question_ids") or b.get("claim_types"), b["id"])

    def test_series_b_benchmarks_point_at_series_b_questions(self):
        for m in grid_lib.known_models():
            g = grid_lib.effective_grid(SERIES_B, {"model_type": m})
            known = set(ids(g))
            for b in grid_lib.load_benchmarks(m, "series_b"):
                for qid in b.get("question_ids") or []:
                    self.assertIn(qid, known, f"{m}: benchmark {b['id']} points at {qid}, not in the series B {m} grid")
                for t in b.get("claim_types") or []:
                    self.assertIn(t, SERIES_B["claim_types"], f"{b['id']}: unknown claim type {t}")
        saas = {b["id"]: b for b in grid_lib.load_benchmarks("saas", "series_b")}
        for empty in ("saas-b-quota-attainment", "saas-b-rep-ramp", "all-b-round-size"):
            self.assertEqual(saas[empty]["value"], "", empty)
        self.assertEqual(saas["saas-b-rule-of-40-feld"]["date"], "2015-02-03")
        self.assertEqual(saas["saas-b-magic-number-scale-2010"]["date"], "2010-04-20")

    def test_series_c_benchmarks_point_at_series_c_questions(self):
        for m in grid_lib.known_models():
            g = grid_lib.effective_grid(SERIES_C, {"model_type": m})
            known = set(ids(g))
            for b in grid_lib.load_benchmarks(m, "series_c"):
                for qid in b.get("question_ids") or []:
                    self.assertIn(qid, known, f"{m}: benchmark {b['id']} points at {qid}, not in the series C {m} grid")
                for t in b.get("claim_types") or []:
                    self.assertIn(t, SERIES_C["claim_types"], f"{b['id']}: unknown claim type {t}")
        saas = {b["id"]: b for b in grid_lib.load_benchmarks("saas", "series_c")}
        self.assertIn("57 %", saas["saas-c-growth-bessemer"]["value"])  # 100M USD ARR and above
        self.assertEqual(saas["saas-c-fcf-margin-bessemer"]["date"], "2021-09-21")
        for empty in ("saas-c-plan-attainment", "saas-c-discount-trend", "saas-c-zero-burn-growth", "saas-c-growth-fcf-iconiq-high-alpha", "all-c-round-size", "all-c-exit-comparables"):
            self.assertEqual(saas[empty]["value"], "", empty)
        self.assertIn("all-c-exit-comparables", {b["id"] for b in grid_lib.load_benchmarks("fintech", "series_c")})

    def test_series_d_benchmarks_point_at_series_d_questions(self):
        for m in grid_lib.known_models():
            g = grid_lib.effective_grid(SERIES_D, {"model_type": m})
            known = set(ids(g))
            for b in grid_lib.load_benchmarks(m, "series_d"):
                self.assertNotIn("-c-", b["id"], f"{m}: series C id {b['id']} in the series D list")
                for qid in b.get("question_ids") or []:
                    self.assertIn(qid, known, f"{m}: benchmark {b['id']} points at {qid}, not in the series D {m} grid")
                for t in b.get("claim_types") or []:
                    self.assertIn(t, SERIES_D["claim_types"], f"{b['id']}: unknown claim type {t}")
        saas = {b["id"]: b for b in grid_lib.load_benchmarks("saas", "series_d")}
        # The series C values are shown again, identical, with their sources and dates.
        c = {b["id"]: b for b in grid_lib.load_benchmarks("saas", "series_c")}
        for cid, cb in c.items():
            if cid in ("all-c-round-size", "saas-c-plan-attainment", "all-c-exit-comparables"):
                continue  # replaced at series D by all-d-round-size, saas-d-forecast-accuracy and all-d-ipo-comparables
            db = saas[cid.replace("-c-", "-d-", 1)]
            for key in ("value", "source", "url", "date"):
                self.assertEqual(db[key], cb[key], f"{cid}: {key} differs at series D")
        self.assertIn("57 %", saas["saas-d-growth-bessemer"]["value"])
        self.assertEqual(saas["saas-d-fcf-margin-bessemer"]["date"], "2021-09-21")
        # The series C question ids that moved: D2 (discounts) to F4, D3 (win rate) to F3, D4 to D3, H5 to H6.
        self.assertEqual(saas["saas-d-discount-trend"]["question_ids"], ["F4"])
        self.assertEqual(saas["saas-d-win-rate"]["question_ids"], ["F3", "F2"])
        self.assertEqual(saas["saas-d-product-share"]["question_ids"], ["D3"])
        self.assertEqual(saas["saas-d-geo-share"]["question_ids"], ["D5"])
        self.assertEqual(saas["all-d-ipo-comparables"]["question_ids"], ["H6"])
        self.assertEqual(saas["saas-d-forecast-accuracy"]["question_ids"], ["D1", "H2"])
        for dup in ("saas-d-plan-attainment", "all-d-exit-comparables"):  # replaced by the two entries above
            self.assertNotIn(dup, saas, dup)
        for empty in ("saas-d-forecast-accuracy", "saas-d-backlog", "saas-d-close-cycle", "saas-d-round-price", "all-d-round-size", "all-d-ipo-comparables",
                      "saas-d-forecast-accuracy", "saas-d-discount-trend", "saas-d-zero-burn-growth", "all-d-ipo-comparables"):
            self.assertEqual(saas[empty]["value"], "", empty)
            self.assertTrue(saas[empty]["note"], empty)
        self.assertNotIn("all-c-round-size", saas)
        self.assertNotIn("all-d-round-size".replace("-d-", "-c-"), saas)
        generic = {b["id"] for b in grid_lib.load_benchmarks("biotech", "series_d")}
        for gid in ("all-d-burn-multiple-sacks", "all-d-round-size", "all-d-ipo-comparables"):
            self.assertIn(gid, generic, gid)
        self.assertNotIn("saas-d-growth-bessemer", generic)

    def test_generic_saas_benchmarks_are_shown_for_other_models(self):
        ids_hw = {b["id"] for b in grid_lib.load_benchmarks("hardware", "series_a")}
        self.assertIn("all-a-burn-multiple-sacks", ids_hw)
        self.assertNotIn("saas-a-arr", ids_hw)
        ids_hw_b = {b["id"] for b in grid_lib.load_benchmarks("hardware", "series_b")}
        self.assertIn("all-b-burn-multiple-sacks", ids_hw_b)
        self.assertIn("all-b-efficiency-score", ids_hw_b)
        self.assertNotIn("saas-b-growth-bessemer", ids_hw_b)
        self.assertEqual(grid_lib.load_benchmarks("saas", "preseed"), [])


class ReadableCopyTest(unittest.TestCase):
    def test_model_md_lists_added_ids_removed_ids_and_version(self):
        for m in grid_lib.known_models():
            doc = grid_lib.load_model(m)
            with open(os.path.join(MODELS_MD, f"{m}.md"), encoding="utf-8") as f:
                md = f.read()
            self.assertIn(doc["version"], md, m)
            for stage, ops in doc["stages"].items():
                for entry in ops.get("add") or []:
                    for q in entry["questions"]:
                        self.assertIn(f"| {q['id']} |", md, f"{m}: {q['id']} missing from {m}.md")
                for qid in ops.get("remove") or []:
                    self.assertIn(qid, md, f"{m}: removed {qid} not mentioned in {m}.md")
                docs = ops.get("documents") or {}
                for did in docs.get("remove") or []:
                    self.assertIn(did, md, f"{m}: removed document {did} not mentioned in {m}.md")
                for d in docs.get("add") or []:
                    self.assertIn(f"| {d['id']} |", md, f"{m}: added document {d['id']} missing from {m}.md")
                    self.assertIn(d["name"]["en"], md, f"{m}: name of {d['id']} missing from {m}.md")


class RenderGridTest(unittest.TestCase):
    def test_renders_every_stage_and_model_in_both_languages(self):
        for stage in ("seed", "series_a", "series_b", "series_c", "series_d"):
            for m in grid_lib.known_models():
                for lang in ("en", "fr"):
                    text = render_grid.render(stage, m, lang)
                    g = grid_lib.effective_grid(grid_lib.load_grid(stage), {"model_type": m})
                    for qid in ids(g):
                        self.assertIn(f"| {qid} |", text, f"{stage} {m} {lang}: {qid}")
        text = render_grid.render("series A", "saas")
        self.assertIn("Benchmarks", text)
        self.assertIn("2026-03-31", text)
        text = render_grid.render("série B", "saas", "fr")
        self.assertIn("# Grille : série B, SaaS", text)
        self.assertIn("| pnl_36m | P&L mensuel sur 36 mois |", text)
        self.assertIn("2 éléments", text)
        self.assertIn("2015-02-03", text)

    def test_series_b_render_lists_the_model_documents(self):
        text = render_grid.render("series_b", "biotech")
        self.assertIn("# Grid: series B, Biotech", text)
        self.assertIn("**Removed questions**: C5, C6, D4, D5, D6", text)
        self.assertIn("**Reweighted blocks**: B → 0, D → 0, E → 0, C → 1", text)
        self.assertIn("**Removed documents**: cohorts_24m, crm_pipeline, sales_roster, top20_contracts", text)
        self.assertIn("**Added documents**: clinical_dossier, ip_schedule", text)
        self.assertIn("### R. Science and regulation, weight 3 (block brought by the model)", text)
        self.assertNotIn("| sales_roster |", text)
        self.assertIn("| accounts_audited |", text)

    def test_series_c_render_lists_the_model_documents(self):
        text = render_grid.render("series_c", "biotech")  # "growth round" now routes to series D
        self.assertIn("# Grid: series C, Biotech", text)
        self.assertIn("**Removed questions**: C5, D2, D3, D6", text)
        self.assertIn("**Removed documents**: cohorts_36m, crm_pipeline, sales_roster, billing_export_24m, top20_contracts", text)
        self.assertIn("| accounts_audited_3y |", text)
        self.assertIn("3 items", text)
        fr = render_grid.render("série C", "saas", "fr")
        self.assertIn("# Grille : série C, SaaS", fr)
        self.assertIn("| board_pack_8q |", fr)
        self.assertIn("8 éléments", fr)
        self.assertIn("### D. Position et durabilité, poids 3", fr)

    def test_series_d_render_lists_the_model_documents(self):
        text = render_grid.render("growth round", "biotech")  # series D covers every later round
        self.assertIn("# Grid: series D, Biotech", text)
        self.assertIn("**Removed questions**: C5, F3, F4", text)
        self.assertIn("**Reweighted blocks**: B → 0, D → 0, E → 0, C → 1", text)
        self.assertIn("**Removed documents**: cohorts_48m, crm_pipeline, sales_roster, billing_export_36m, top20_contracts", text)
        self.assertIn("**Added documents**: clinical_dossier, ip_schedule", text)
        self.assertIn("| management_letters_3y |", text)
        self.assertIn("| board_pack_12q |", text)
        self.assertIn("12 items", text)
        self.assertIn("since the series C", text)
        self.assertNotIn("| billing_export_36m |", text)
        self.assertIn("| H1 | Series D round size |", text)
        self.assertIn("| H6 | IPO filings of the category |", text)
        fr = render_grid.render("série D", "saas", "fr")
        self.assertIn("# Grille : série D, SaaS", fr)
        self.assertIn("| pnl_60m |", fr)
        self.assertIn("| management_letters_3y |", fr)
        self.assertIn("12 éléments", fr)

    def test_unknown_model_falls_back_to_saas(self):
        self.assertIn("SaaS", render_grid.render("seed", "spacetech"))

    def test_series_a_render_lists_the_model_documents(self):
        text = render_grid.render("series_a", "consumer")
        self.assertIn("## Required documents (first gate)", text)
        self.assertIn("| product_analytics_12m |", text)
        self.assertIn("Product analytics export over 12 months", text)
        self.assertNotIn("| crm_pipeline |", text)
        self.assertNotIn("| top10_contracts |", text)
        self.assertIn("**Removed documents**: crm_pipeline, top10_contracts", text)
        self.assertIn("**Added documents**: product_analytics_12m", text)
        fr = render_grid.render("series_a", "hardware", "fr")
        self.assertIn("## Documents requis (première porte)", fr)
        self.assertIn("| bom_and_suppliers | Nomenclature et conditions fournisseurs |", fr)
        self.assertIn("| pnl_24m | P&L mensuel sur 24 mois |", fr)
        self.assertIn("| top10_contracts |", fr)
        self.assertIn("10 éléments", fr)
        # Seed has no document list: no section, no summary lines.
        seed = render_grid.render("seed", "consumer")
        self.assertNotIn("Required documents", seed)
        self.assertNotIn("Removed documents", seed)


if __name__ == "__main__":
    unittest.main()

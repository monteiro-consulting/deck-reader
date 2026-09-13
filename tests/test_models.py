"""Tests for the business-model blocks: the three verbs, the seed + marketplace non-regression,
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
PRESEED = grid_lib.load_grid("preseed")
MODELS_MD = os.path.join(HERE, "..", "skills", "deck-reader", "grids", "models")


def ids(grid):
    return [q["id"] for _, q in grid_lib.all_questions(grid)]


def block(grid, bid):
    return next(b for b in grid["blocks"] if b["id"] == bid)


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

    def test_every_model_assembles_at_seed_and_series_a(self):
        for m in grid_lib.known_models():
            for stage in (SEED, SERIES_A):
                g = grid_lib.effective_grid(stage, {"model_type": m})
                self.assertEqual(len(ids(g)), len(set(ids(g))), f"{m} {stage['stage']}: duplicate ids")
                self.assertEqual(g["applied_model"], m)

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


class BenchmarkTest(unittest.TestCase):
    def test_every_benchmark_has_source_and_date_or_is_empty(self):
        for m in grid_lib.known_models():
            for stage in ("seed", "series_a"):
                for b in grid_lib.load_benchmarks(m, stage):
                    if b.get("value"):
                        self.assertTrue(b.get("source"), f"{b['id']}: value without source")
                    if b.get("date"):
                        self.assertTrue(b.get("source"), f"{b['id']}: date without source")
                    self.assertTrue(b.get("question_ids") or b.get("claim_types"), b["id"])

    def test_generic_saas_benchmarks_are_shown_for_other_models(self):
        ids_hw = {b["id"] for b in grid_lib.load_benchmarks("hardware", "series_a")}
        self.assertIn("all-a-burn-multiple-sacks", ids_hw)
        self.assertNotIn("saas-a-arr", ids_hw)
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


class RenderGridTest(unittest.TestCase):
    def test_renders_every_stage_and_model_in_both_languages(self):
        for stage in ("seed", "series_a"):
            for m in grid_lib.known_models():
                for lang in ("en", "fr"):
                    text = render_grid.render(stage, m, lang)
                    g = grid_lib.effective_grid(grid_lib.load_grid(stage), {"model_type": m})
                    for qid in ids(g):
                        self.assertIn(f"| {qid} |", text, f"{stage} {m} {lang}: {qid}")
        text = render_grid.render("series A", "saas")
        self.assertIn("Benchmarks", text)
        self.assertIn("2026-03-31", text)

    def test_unknown_model_falls_back_to_saas(self):
        self.assertIn("SaaS", render_grid.render("seed", "spacetech"))


if __name__ == "__main__":
    unittest.main()

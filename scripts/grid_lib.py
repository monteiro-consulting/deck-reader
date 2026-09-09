#!/usr/bin/env python3
"""Shared helpers: load a grid by stage and build the effective grid for one deck.

Standard library only.

    load_grid(path_or_stage)      -> dict. "preseed" / "seed" resolve to scripts/grids/<stage>.json.
    effective_grid(grid, profile) -> a copy of the grid where the model-specific questions
                                     (grid["model_questions"][profile["model_type"]]) are appended
                                     to their block. Every script that walks the questions must
                                     use this, so that a marketplace deck is scored on the
                                     marketplace questions too.
    all_questions(grid)           -> [(block, question), ...] in grid order.
"""
import copy
import json
import os

GRIDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grids")
STAGES = {"pre-seed": "preseed", "preseed": "preseed", "seed": "seed"}


def grid_path(stage_or_path):
    if os.path.isfile(stage_or_path):
        return stage_or_path
    key = STAGES.get(str(stage_or_path).lower())
    if key is None:
        raise SystemExit(f"no grid for stage {stage_or_path!r}; known: {sorted(set(STAGES.values()))}")
    return os.path.join(GRIDS_DIR, f"{key}.json")


def load_grid(stage_or_path):
    with open(grid_path(stage_or_path), encoding="utf-8") as f:
        return json.load(f)


def effective_grid(grid, profile=None):
    g = copy.deepcopy(grid)
    model = str((profile or {}).get("model_type", "")).lower()
    extra = (g.get("model_questions") or {}).get(model)
    if extra:
        for block in g["blocks"]:
            if block["id"] == extra["block"]:
                block["questions"] = list(block["questions"]) + list(extra["questions"])
                break
    g["applied_model_questions"] = model if extra else ""
    return g


def all_questions(grid):
    return [(b, q) for b in grid["blocks"] for q in b["questions"]]

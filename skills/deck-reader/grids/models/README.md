# Model blocks

One block per business model, never one grid per sector. Each file here is the readable copy of
`scripts/grids/models/<model>.json`; both must stay identical (a test checks the question ids
and the version). The benchmarks of each model live in `scripts/grids/benchmarks/<model>.json`
and are displayed next to the deck figures, never scored.

A model block is applied to the stage grid by `grid_lib.effective_grid` in four verbs, in this
order:

| Verb | What it does |
|---|---|
| **remove** | Takes questions of the stage grid out, by id |
| **reweight** | Changes the weight of a block, or of one question. A block at weight 0 is asked for information and never counts nor turns red |
| **add** | Appends questions to a block of the stage grid, with the block weight, or to a block the model brings (with its own id, name and weight) |
| **documents** | Adjusts the required document list of the stage's first gate (`annex_gate.required_documents`, series A, series B, series C and series D): `remove` takes documents out by id, `add` appends entries with the same shape as the grid's (`id`, `name`, `requirement`, `min_months`, optional `min_count`). Only for a stage whose grid carries a list; an error otherwise. The list is the same for every deck of one stage and one model: the block adjusts it, the deck never does |

The profile detects the model. No model detected, or a model without a file, means `saas`.
The pre-seed grid has no model section and is untouched; seed has no document list. Each model
file carries one section per stage: `seed`, `series_a`, `series_b`, `series_c`, `series_d`.

`scripts/render_grid.py <stage> <model> [--lang fr]` writes the effective grid in one piece.

| Model | File |
|---|---|
| SaaS (default) | [saas.md](saas.md) |
| Marketplace | [marketplace.md](marketplace.md) |
| Consumer | [consumer.md](consumer.md) |
| E-commerce and D2C | [ecommerce.md](ecommerce.md) |
| Hardware | [hardware.md](hardware.md) |
| Fintech | [fintech.md](fintech.md) |
| Biotech | [biotech.md](biotech.md) |

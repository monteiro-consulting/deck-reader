# deck-reader

A Claude Code plugin that reads a pitch deck and writes, next to the PDF, a report of what the
deck answers and what it does not, with the grid of the stage the deck announces and the block
of its business model.

- **Pre-seed**: completeness. Per grid question, found / partial / absent with the page and the
  verbatim quote; six completeness bars; the questions to ask the founder; what the deck does
  not say.
- **Seed**: completeness, plus verification. Every figure and fact the deck states is listed,
  looked up in the annexes the founder sent, then, for what a document cannot settle, checked on
  the public web with sources on both sides. A figure with no document behind it cannot score
  higher than partial. What is missing goes into a draft email to the founder. What is
  contradicted goes through a second independent review before the reading stops.
- **Series A**: the same engine, another question: does the machine repeat? A list of required
  documents, the same for every deck of one stage and one business model (the base list, written
  for SaaS: monthly P&L over 24 months, cohorts over 12 months or more, CRM export with weighted
  pipeline, cap table, three-year financial model, contracts of the top 10 customers; the model
  block adjusts it, a consumer app drops the CRM and the contracts for a product analytics
  export, a hardware company adds its bill of materials); a missing one stops the reading with
  the request email. Unit economics and net
  retention are the heaviest blocks. New claim types (NRR, weighted pipeline, sales cycle by
  segment, gross margin against the P&L, top 10 concentration, burn multiple, deals closed
  without a founder, key hires) and a wider web check (public reviews, open job posts, press of
  previous rounds, key hires on LinkedIn). Benchmarks for the model and the stage are shown next
  to every figure, with source and date, and never enter the score.
- **Series B**: the same engine, another question: does the machine hold at scale, without the
  founders? Ten required documents for SaaS, over 36 months where series A asked 24 (monthly
  P&L, audited accounts, cohorts by segment, CRM with win/loss, sales roster with quota
  attainment, cap table, three-year model, top 20 contracts, board pack, org chart; the model
  block adjusts the list). Efficient growth and repeatability are the heaviest blocks: a second
  engine with its own economics, quota attainment, rep ramp, deals closed by reps hired in the
  year, a burn multiple that falls as ARR rises. New claim types (Rule of 40, magic number,
  quota attainment, rep ramp, second engine, executive team and departures, headcount, board,
  breakeven, audited figures, win rate, secondary or debt, expansion) and a wider web check
  (every executive on LinkedIn, headcount trend, employee reviews, job posts by country,
  registries for subsidiaries, press of every round).
- **Series C**: the same engine, another
  question: does the machine hold without new money, and keep its place? The central proof is
  the past of the deck: the plan of the last eight quarters in the board packs against the
  actual in the P&L, laid out quarter by quarter in the report (ARR, net new ARR, net burn,
  headcount; the gap computed by code). Eleven required documents for SaaS, over 48 months
  (monthly P&L by product and geography, audited accounts over three years with the opinion,
  cohorts by segment and acquisition year, CRM with win/loss, sales roster, billing export with
  list and net price, cap table with the terms of every round and debt, three-year model with a
  zero-burn scenario, top 20 contracts, board pack of eight quarters, org chart; the model block
  adjusts the list). Efficient growth and position and durability are the heaviest blocks: free
  cash flow margin, growth at zero burn, plan against actual, pricing power, win rate trend,
  products and countries after the first with their own economics. New claim types (plan vs
  actual, net price, discount rate, FCF margin, zero-burn growth, product and geographic share,
  liquidation preference, debt terms, audit opinion, controls certification, competitor funding,
  exit comparables) and a wider web check (accounts filed at the registry, pricing page history
  on the Wayback Machine, review trend, litigation and security incidents, competitors' rounds,
  listed comparables). Never a valuation.
- **Series D and every later round** (series E, growth rounds, pre-IPO): the same engine,
  another question: is the machine ready to change hands, and why this round? The central proof
  is the dispersion of the forecasts: the plan of the last twelve quarters in the board packs
  against the actual in the P&L, laid out quarter by quarter in the report and counted by band
  (within 5 %, within 10 %, beyond), because a public market punishes the miss, not the average.
  Twelve required documents for SaaS, over 60 months (monthly P&L by product and geography,
  audited accounts over three years with the opinion and the standard, cohorts over 48 months,
  CRM with win/loss, sales roster, billing export with contract start and end dates, cap table
  with the terms of every round and this round's term sheet if signed, three-year model with the
  cash line of this round, top 20 contracts, board pack of twelve quarters with the issue dates,
  org chart, the auditor's management letters over three years; the model block adjusts the
  list). Profitable growth and predictability and exit readiness are the heaviest blocks: plan
  against actual by band, the accounting standard, the days to close and the management letter
  findings, a second act with its own economics, acquisitions with their ARR at closing against
  today, breakeven within the cash of this round. New claim types (backlog, round price, round
  purpose, acquired company, management letter, close cycle) and a wider web check (the press
  of every previous round for its price, the press and the registry of every acquisition,
  tender offers and secondary sales made public, competitors acquired or listed since the
  series C, the last IPO filings of the category). The preference stack and the company next
  to the last IPOs of its category are laid out as facts, never a valuation.

It never says whether to invest. It says what to ask, and what did not hold up.

**One grid per stage, one block per business model, one engine.** The deck's announced stage
picks the grid (`scripts/grids/preseed.json`, `seed.json`, `series_a.json`, `series_b.json`, `series_c.json`, `series_d.json`; series D covers every later round). The detected
business model picks the model block (`scripts/grids/models/<model>.json`: saas, marketplace,
consumer, ecommerce, hardware, fintech, biotech; no model detected means saas), applied to the
stage grid in four verbs: remove, reweight, add, documents. A deck of a stage with no grid is
refused with a one-line explanation. Never one grid for all, never one grid per sector.

## Usage

```
/deck-reader path/to/deck.pdf
/deck-reader path/to/deck.pdf --annex revenue.csv --annex cohorts.xlsx --annex model.pdf
/deck-reader path/to/deck.pdf --annex pnl.xlsx --annex cohorts.csv --annex crm.csv --annex cap-table.xlsx --annex model.xlsx --annex contracts.pdf
```

Output: `path/to/deck.reading.md` and the same reading as `path/to/deck.reading.pdf`, and at
seed, series A, series B, series C and series D, when documents are missing, `path/to/deck.founder-email.md`. Add
`--keep-work` to keep the intermediate files in a temporary folder for inspection. Annexes:
`.pdf`, `.csv`, `.tsv`, `.xlsx`, `.txt`, `.md`, `.json`.

To read a grid in one piece, model block applied and benchmarks listed:

```bash
python scripts/render_grid.py series_a saas
python scripts/render_grid.py series_b biotech --lang fr
python scripts/render_grid.py series_c fintech
python scripts/render_grid.py series_d saas
python scripts/render_grid.py seed marketplace --lang fr --out seed-marketplace.md
```

The plugin itself is in English. The report is written in the user's language (labels shipped
for English and French; other languages get English labels and prose in the user's language).
Quotes from the deck and the annexes are never translated.

## How it works

Isolated steps, so that a model never fills a gap with something it saw elsewhere, and code
takes every decision that must not go through a model.

### Every stage

| Step | What happens | Who |
|---|---|---|
| 1. Read | PDF text layer extracted by code; pages transcribed by a model into raw JSON | `pdf_text.py`, `page-transcriber` |
| 2. Profile and route | Sector, model type, B2B or B2C, announced stage, each with a quote. The stage picks the grid, the model type picks the model block; no grid, stop | `deck-profiler`, `grid_lib.py` |
| 5. Grid | One checker per block in parallel, each sees only its own questions. One question at a time. Every quote is verified by code against the cited page; rejected quotes are retried twice, then marked absent | `block-checker` × blocks, `verify_quotes.py` |
| 5c. Confirmation | If the first-pass completeness is between 65 % and 80 %, two more independent passes; each question takes the median | `consolidate.py` |
| 7. Reading, report | Completeness computed by code from the weights; the writer sees only the answers, never the deck nor the score | `score.py`, `report-writer`, `report.py` |

### Seed, between the profile and the grid

| Step | What happens | Who |
|---|---|---|
| 3S. Claims | Every verifiable statement of the deck: figures, named customers, competitors, founders, past funding, "why now". Page and quote each, verified by code | `annex_text.py`, `claim-extractor`, `check_claims.py` |
| 4S. Proof in the annexes | Each claim looked up in the documents; the gap between the deck figure and the annex figure is classified by code (minor ≤ 25 %, to probe ≤ ×2, blatant above). First gate: no annex, stop with a generic email; key figures less than half covered, stop with a precise email; otherwise continue | `annex-matcher`, `verify_matches.py`, `seed_gate.py`, `founder_email.py` |
| 5S. Web | Only for what a document cannot settle. Searched for and against; at least two independent domains to conclude; otherwise unverifiable. The only agent on the web | `web-verifier`, `verify_web.py` |
| 6S. Double check | Every blatant contradiction goes to a second reviewer whose only job is to find an honest explanation (date, definition, scope, unit, stale source, homonym). With one, the claim becomes a question for the call. Without one, the second gate stops the reading and shows the sources on both sides | `contradiction-reviewer`, `seed_gate.py` |
| 5. Grid, with proof | Checkers cite the claims they rely on. A figure without a proven or confirmed claim is capped at partial; an answer citing a gap to probe is lowered one step. Code, not the checker | `apply_proof_cap.py` |

### Series A, series B, series C and series D, between the profile and the grid

| Step | What happens | Who |
|---|---|---|
| 3A. Documents | Each annex sorted into one of the required documents of the stage and model with a verbatim quote and the months or items covered; the quote is checked by code. First gate: the list is the one of the stage grid (six documents for SaaS at series A, ten at series B, eleven at series C, twelve at series D) adjusted by the model block, never by the deck; a document missing, or covering fewer months or items than required, stops the reading with the request email. No coverage threshold | `annex_text.py`, `annex-classifier`, `documents_gate.py`, `founder_email.py` |
| 4A. Claims and proof | As at seed, with the series A, series B, series C or series D claim types. At series C and series D a plan vs actual claim is looked up twice, the plan in the board pack and the actual in the P&L. At series D a management letter finding is read in the management letters, a close cycle in the issue dates of the board packs, a backlog in the contract dates of the billing export, the price of a round and its preference in the terms, the cash line of the round in the model. A figure the deck attributes to the audited accounts is looked up there, not in the P&L. Claims the documents do not cover are listed, never a stop. No leftovers email: the document list replaces it | `claim-extractor`, `check_claims.py`, `annex-matcher`, `verify_matches.py` |
| 5S, 6S | As at seed, with public reviews, open job posts, the press of previous rounds and the LinkedIn profile of each announced key hire added to the web scope; at series B also every executive on LinkedIn, the headcount trend and departures, employee reviews, job posts by country, registries for announced subsidiaries, the press of every round; at series C also the accounts filed at the company registry against the audited ones, the pricing page history on the Wayback Machine, the review trend over 24 months, litigation and security incidents made public, the rounds of competitors since the series B, listed comparables; at series D also the press of every previous round for its announced price, the press and the registry of every acquisition, tender offers and secondary sales made public, the competitors acquired or listed since the series C, the last IPO filings of the category | `web-verifier`, `verify_web.py`, `contradiction-reviewer`, `documents_gate.py` |
| 7. Report | Benchmarks for the model and the stage shown next to each figure, with source and date. Displayed, never scored. At series C, the plan against actual table, quarter by quarter, laid out by code. At series D, the same over twelve quarters with the distribution by band (within ±5 %, ±10 %, beyond), the preference stack as a table, and the company next to the last IPOs of its category, all laid out by code, nothing summed or valued | `report.py`, `scripts/grids/benchmarks/` |

The gate decisions, the gap thresholds, the document list, the source rule, the model blocks and
the benchmarks live in `scripts/grids/`, readable by all, corrected at each post-mortem. They are
not hidden in a prompt.

## Model blocks

`scripts/grids/models/<model>.json`, readable copy in `skills/deck-reader/grids/models/`. Per
stage, four verbs applied in this order by `grid_lib.effective_grid`:

| Verb | Effect |
|---|---|
| `remove` | question ids of the stage grid taken out |
| `reweight` | new weight for a block or a question; a block at weight 0 is for information, never counts, never red |
| `add` | questions appended to a block of the stage grid, with its weight, or to a block the model brings |
| `documents` | the required document list of the first gate (`annex_gate.required_documents`, series A, series B, series C and series D) adjusted: `remove` by document id, `add` with entries of the grid's shape (`id`, `name`, `requirement`, `min_months`, optional `min_count`). Only where the stage grid has a list; an error otherwise |

Examples: biotech puts traction at weight 0 and adds milestones, IP and regulatory path;
hardware adds margin at 1,000 / 10,000 / 100,000 units, bill of materials and MOQs, and doubles
economics; consumer adds DAU/MAU, flattening cohorts and organic share, and lowers revenue;
ecommerce adds contribution margin per order after shipping and returns, CAC by channel and
60-day repeat; fintech adds licence, cost of compliance, credit or fraud risk. Marketplace at
seed is exactly the previous grid (a test checks it). The pre-seed grid has no model section.

At series A the base document list is written for SaaS. The model block adjusts it: marketplace
adds the monthly GMV by side; consumer and ecommerce drop the CRM export and the top 10
contracts for a product analytics export or an orders export; hardware adds the bill of
materials and supplier terms; fintech adds the licence and the risk book; biotech drops the
cohorts, the CRM and the contracts for the clinical data package and the patent schedule. The
deck never adjusts the list.

At series B the same blocks apply to the ten-document list, 36 months where series A asked 24:
marketplace adds the monthly GMV by side over 36 months; consumer and ecommerce drop the CRM
export, the sales roster and the top 20 contracts for a product analytics export over 24 months
or an orders export over 36 months, and drop the magic number, the pipeline and the sales-team
questions; hardware adds the inventory and warranty history to the bill of materials; fintech
adds a fourth question, losses on the book over 36 months, and the risk book over 36 months;
biotech puts traction, repeatability and net retention at weight 0 and drops the cohorts as well.

At series C the list has eleven documents over 48 months: marketplace adds the monthly GMV by
side over 48 months; consumer and ecommerce drop the CRM export, the sales roster and the top 20
contracts for a product analytics export over 36 months or an orders export over 48 months, and
drop the magic number, the win rate trend and the deals without a founder; hardware adds the
inventory and warranty history over 36 months to the bill of materials; fintech adds licences
per country and the risk book over 48 months; biotech puts traction, position and durability and
net retention at weight 0, drops pricing power, and drops the cohorts and the billing export as
well.

At series D the list has twelve documents over 60 months: marketplace adds the monthly GMV by
side over 60 months; consumer and ecommerce drop the CRM export, the sales roster and the top 20
contracts for a product analytics export over 48 months or an orders export over 60 months, and
drop the magic number and the win rate trend (consumer also drops the ACV by segment and lowers
the ARR weight); hardware adds the inventory and warranty history over 48 months to the bill of
materials and doubles profitable growth; fintech adds licences per country and the risk book
over 60 months; biotech puts traction, predictability and exit readiness and net retention at
weight 0, drops the magic number, the win rate trend and pricing power, and drops the cohorts
and the billing export as well.

Benchmarks are per model and per stage in `scripts/grids/benchmarks/<model>.json`, each with
value, source and date. An entry with no dated source is left empty, on purpose.

## Layout

```
.claude-plugin/plugin.json
skills/deck-reader/SKILL.md            the orchestrator, routes by stage
skills/deck-reader/grids/preseed.md    the pre-seed grid, readable
skills/deck-reader/grids/seed.md       the seed grid, readable, with gates and thresholds
skills/deck-reader/grids/series_a.md   the series A grid, readable, with the document list
skills/deck-reader/grids/series_b.md   the series B grid, readable, with the ten-document list
skills/deck-reader/grids/series_c.md   the series C grid, readable, with the eleven-document list
skills/deck-reader/grids/series_d.md   the series D grid (and every later round), readable, with the twelve-document list
skills/deck-reader/grids/models/       one readable model block per business model
agents/page-transcriber.md             sonnet, every stage
agents/deck-profiler.md                sonnet, every stage
agents/block-checker.md                sonnet, one per block, every stage
agents/report-writer.md                opus, every stage
agents/claim-extractor.md              sonnet, seed, series A, series B, series C and series D
agents/annex-matcher.md                sonnet, seed, series A, series B, series C and series D
agents/annex-classifier.md             sonnet, series A, series B, series C and series D: which required document of the stage and model is each annex
agents/web-verifier.md                 sonnet, seed, series A, series B, series C and series D, the only agent on the web
agents/contradiction-reviewer.md       opus, seed, series A, series B, series C and series D
scripts/grids/preseed.json             grid as data
scripts/grids/seed.json                grid as data, plus claim types, gates, thresholds
scripts/grids/series_a.json            grid as data, plus the base document list of the first gate
scripts/grids/series_b.json            grid as data, plus the base ten-document list and the series B claim types
scripts/grids/series_c.json            grid as data, plus the base eleven-document list, the series C claim types and the plan vs actual table
scripts/grids/series_d.json            grid as data, plus the base twelve-document list, the series D claim types, the plan vs actual table by band, the preference stack and the IPO comparables
scripts/grids/models/<model>.json      model blocks: remove, reweight, add, documents, per stage
scripts/grids/benchmarks/<model>.json  benchmarks per model and stage, value, source, date
scripts/grid_lib.py                    grid by stage, model block assembly, benchmarks
scripts/render_grid.py                 the effective grid of a stage and a model as one markdown
scripts/pdf_text.py                    PDF text per page, stdlib only
scripts/merge_pages.py                 page reference for checkers and verifier
scripts/annex_text.py                  annexes to pages (pdf, csv, xlsx, txt, md, json)
scripts/claim_types.py                 claim types for the extractor
scripts/check_claims.py                claim quotes exist on the cited page
scripts/verify_matches.py              annex quotes exist; gaps classified; annex status
scripts/verify_web.py                  source rule enforced; final status per claim
scripts/seed_gate.py                   the two seed stop decisions
scripts/documents_gate.py              the stop decisions of the stages with a document list (series A, series B, series C, series D): documents of the stage and model, contradictions
scripts/founder_email.py               the email draft (never sent by the tool)
scripts/grid_block.py                  one block's questions
scripts/verify_quotes.py               quote exists verbatim on the cited page
scripts/apply_proof_cap.py             cap and lowering by proof status
scripts/consolidate.py                 median of independent passes, per question
scripts/score.py                       completeness from values and weights
scripts/report.py                      final markdown, every stage, both languages, benchmarks, the series C and series D plan vs actual table, the series D preference stack and IPO comparables
scripts/report_pdf.py                  the same reading as a PDF, stdlib only, no font embedded
scripts/claims_lib.py                  shared claim helpers
fixtures/preseed-deck.pdf              12-page fictional pre-seed deck with deliberate gaps
fixtures/preseed-deck.reading.md       its reading, markdown; .reading.pdf = the same, rendered
fixtures/seed-deck.pdf                 14-page fictional seed deck
fixtures/seed-annex-revenue.csv        its revenue export (one minor gap on purpose)
fixtures/seed-annex-cohorts.csv        its cohort table
fixtures/make_preseed_fixture.py       regenerates the pre-seed deck
fixtures/make_seed_fixture.py          regenerates the seed deck and annexes
tests/                                 unittest, stdlib only
tests/fixtures/seed-marketplace-effective.json   the seed + marketplace grid before the model blocks, for the non-regression test
```

Python 3.9+, standard library only. Nothing leaves the local disk except the web verifier's
searches, which carry the claim text and never the deck or the annexes.

## Tests

```bash
python -m unittest discover -s tests
```

## Guardrails

- "Score" means deck completeness. Never quality, potential or investment score.
- No inference: a figure that is not on a page is absent.
- A value without a page and a verbatim quote is invalid and rejected by code. So is a claim, an
  annex match, an annex classification or a web source without one.
- A red block produces a question, not a judgement. A contradiction produces the sources on
  both sides, a review, and a question or a stop, never a verdict.
- The tool can only stop on something false, never on something imprecise. At series A,
  series B, series C and series D it also stops on a missing document, which is a fact about the file set, not about
  the company.
- A benchmark is displayed next to the figure with its source and date. It never enters the
  score, and one without a dated source stays empty.
- The tool never sends the founder email.
- Nothing persists outside the report (markdown and PDF) and the email draft unless `--keep-work` is given.

## Known limits

- Quotes are verified against the PDF text layer. Text that exists only inside images (charts,
  screenshots) cannot be cited and is treated as absent. When the text layer is unusable
  (scanned deck), the model transcription becomes the reference and the report header says so.
  The same applies to annex PDFs.
- Checker values are not perfectly stable between runs on borderline questions; the
  confirmation passes exist for this reason, inside the 65-80 % band.
- The web check depends on what is public. A customer with no public trace is unverifiable, not
  contradicted; the report says so and the call clears it up.
- The gap thresholds, the document minimums (24, 12, 36 months, 10 contracts at series A; 36,
  24, 12 months, 2 fiscal years, 20 contracts, 4 quarters at series B; 48, 36, 24 months, 3 fiscal years, 20 contracts, 8 quarters at series C; 60, 48, 36, 24 months, 3 fiscal years, 3 management letters, 20 contracts, 12 quarters at series D) and the model weights are
  a first setting. They will be corrected at the first post-mortems, in the grid files, in the
  open.
- Several benchmarks have no dated source yet (sales cycle by segment, pipeline coverage, share
  of deals closed without a founder, quota attainment, rep ramp, win rate, series B round size,
  BOM and MOQ, fintech loss rates, biotech IP and phase durations; at series C plan attainment, discount trend, zero-burn growth,
  shares of ARR from second products and from abroad, series C round size, growth and FCF margin
  above 50M USD ARR in the 2024-2025 reports; at series D forecast accuracy by band, backlog and
  multi-year share, days to close, the price against the last round, series D round size, and
  the figures of the category's IPOs, read per deck from the filings and never as a generic
  figure). They are listed empty rather
  than invented.
- The grid cannot tell a founder who presents poorly from a founder who did nothing. That is the
  call's job.

# deck-reader

A Claude Code plugin that reads a pitch deck and writes, next to the PDF, a report of what the
deck answers and what it does not, with the grid of the stage the deck announces.

- **Pre-seed**: completeness. Per grid question, found / partial / absent with the page and the
  verbatim quote; six completeness bars; the questions to ask the founder; what the deck does
  not say.
- **Seed**: completeness, plus verification. Every figure and fact the deck states is listed,
  looked up in the annexes the founder sent, then, for what a document cannot settle, checked on
  the public web with sources on both sides. A figure with no document behind it cannot score
  higher than partial. What is missing goes into a draft email to the founder. What is
  contradicted goes through a second independent review before the reading stops.

It never says whether to invest. It says what to ask, and what did not hold up.

**One grid per stage, one engine.** The deck's announced stage picks the grid
(`scripts/grids/preseed.json`, `scripts/grids/seed.json`). A deck of a stage with no grid is
refused with a one-line explanation. Never one grid for all.

## Usage

```
/deck-reader path/to/deck.pdf
/deck-reader path/to/deck.pdf --annex revenue.csv --annex cohorts.xlsx --annex model.pdf
```

Output: `path/to/deck.reading.md`, and at seed, when documents are missing,
`path/to/deck.founder-email.md`. Add `--keep-work` to keep the intermediate files in a
temporary folder for inspection. Annexes: `.pdf`, `.csv`, `.tsv`, `.xlsx`, `.txt`, `.md`, `.json`.

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
| 2. Profile and route | Sector, model type, B2B or B2C, announced stage, each with a quote. The stage picks the grid; no grid, stop | `deck-profiler` |
| 5. Grid | One checker per block in parallel, each sees only its own questions. One question at a time. Every quote is verified by code against the cited page; rejected quotes are retried twice, then marked absent | `block-checker` × blocks, `verify_quotes.py` |
| 5c. Confirmation | If the first-pass completeness is between 65 % and 80 %, two more independent passes; each question takes the median | `consolidate.py` |
| 7. Reading, report | Completeness computed by code from the weights; the writer sees only the answers, never the deck nor the score | `score.py`, `report-writer`, `report.py` |

### Seed only, between the profile and the grid

| Step | What happens | Who |
|---|---|---|
| 3S. Claims | Every verifiable statement of the deck: figures, named customers, competitors, founders, past funding, "why now". Page and quote each, verified by code | `annex_text.py`, `claim-extractor`, `check_claims.py` |
| 4S. Proof in the annexes | Each claim looked up in the documents; the gap between the deck figure and the annex figure is classified by code (minor ≤ 25 %, to probe ≤ ×2, blatant above). First gate: no annex, stop with a generic email; key figures less than half covered, stop with a precise email; otherwise continue | `annex-matcher`, `verify_matches.py`, `seed_gate.py`, `founder_email.py` |
| 5S. Web | Only for what a document cannot settle. Searched for and against; at least two independent domains to conclude; otherwise unverifiable. The only agent on the web | `web-verifier`, `verify_web.py` |
| 6S. Double check | Every blatant contradiction goes to a second reviewer whose only job is to find an honest explanation (date, definition, scope, unit, stale source, homonym). With one, the claim becomes a question for the call. Without one, the second gate stops the reading and shows the sources on both sides | `contradiction-reviewer`, `seed_gate.py` |
| 5. Grid, with proof | Checkers cite the claims they rely on. A figure without a proven or confirmed claim is capped at partial; an answer citing a gap to probe is lowered one step. Code, not the checker | `apply_proof_cap.py` |

The gate decisions, the gap thresholds, the coverage threshold and the source rule live in
`scripts/grids/seed.json`, readable by all, corrected at each post-mortem. They are not hidden
in a prompt.

## Layout

```
.claude-plugin/plugin.json
skills/deck-reader/SKILL.md            the orchestrator, routes by stage
skills/deck-reader/grids/preseed.md    the pre-seed grid, readable
skills/deck-reader/grids/seed.md       the seed grid, readable, with gates and thresholds
agents/page-transcriber.md             sonnet, every stage
agents/deck-profiler.md                sonnet, every stage
agents/block-checker.md                sonnet, one per block, every stage
agents/report-writer.md                opus, every stage
agents/claim-extractor.md              sonnet, seed
agents/annex-matcher.md                sonnet, seed
agents/web-verifier.md                 sonnet, seed, the only agent on the web
agents/contradiction-reviewer.md       opus, seed
scripts/grids/preseed.json             grid as data
scripts/grids/seed.json                grid as data, plus claim types, gates, thresholds
scripts/grid_lib.py                    grid by stage, model-specific questions
scripts/pdf_text.py                    PDF text per page, stdlib only
scripts/merge_pages.py                 page reference for checkers and verifier
scripts/annex_text.py                  annexes to pages (pdf, csv, xlsx, txt, md, json)
scripts/claim_types.py                 claim types for the extractor
scripts/check_claims.py                claim quotes exist on the cited page
scripts/verify_matches.py              annex quotes exist; gaps classified; annex status
scripts/verify_web.py                  source rule enforced; final status per claim
scripts/seed_gate.py                   the two stop decisions
scripts/founder_email.py               the email draft (never sent by the tool)
scripts/grid_block.py                  one block's questions
scripts/verify_quotes.py               quote exists verbatim on the cited page
scripts/apply_proof_cap.py             cap and lowering by proof status
scripts/consolidate.py                 median of independent passes, per question
scripts/score.py                       completeness from values and weights
scripts/report.py                      final markdown, both stages, both languages
scripts/claims_lib.py                  shared claim helpers
fixtures/preseed-deck.pdf              12-page fictional pre-seed deck with deliberate gaps
fixtures/seed-deck.pdf                 14-page fictional seed deck
fixtures/seed-annex-revenue.csv        its revenue export (one minor gap on purpose)
fixtures/seed-annex-cohorts.csv        its cohort table
fixtures/make_preseed_fixture.py       regenerates the pre-seed deck
fixtures/make_seed_fixture.py          regenerates the seed deck and annexes
tests/                                 unittest, stdlib only
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
  annex match or a web source without one.
- A red block produces a question, not a judgement. A contradiction produces the sources on
  both sides, a review, and a question or a stop, never a verdict.
- The tool can only stop on something false, never on something imprecise.
- The tool never sends the founder email.
- Nothing persists outside the report and the email draft unless `--keep-work` is given.

## Known limits

- Quotes are verified against the PDF text layer. Text that exists only inside images (charts,
  screenshots) cannot be cited and is treated as absent. When the text layer is unusable
  (scanned deck), the model transcription becomes the reference and the report header says so.
  The same applies to annex PDFs.
- Checker values are not perfectly stable between runs on borderline questions; the
  confirmation passes exist for this reason, inside the 65-80 % band.
- The web check depends on what is public. A customer with no public trace is unverifiable, not
  contradicted; the report says so and the call clears it up.
- The gap thresholds are a first setting. They will be corrected at the first post-mortems, in
  the grid file, in the open.
- The grid cannot tell a founder who presents poorly from a founder who did nothing. That is the
  call's job.

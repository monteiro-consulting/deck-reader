# preseed-deck-reader

A Claude Code plugin that reads a **pre-seed** pitch deck and writes, next to the PDF, a report of
what the deck answers and what it does not: per grid question, found / partial / absent with the
page and the verbatim quote; six completeness bars; the questions to ask the founder; what the
deck does not say.

It never says whether to invest. It says what to ask.

**Pre-seed only.** A deck is scored according to its stage, and this reader carries the pre-seed
grid and weights. A seed or series A deck is refused with a one-line explanation. One reader per
stage, never one grid for all.

## Usage

```
/preseed-deck-reader path/to/deck.pdf
```

Output: `path/to/deck.preseed-reading.md`. Add `--keep-work` to keep the intermediate files in a
temporary folder for inspection.

The plugin itself is in English. The report is written in the user's language (labels shipped for
English and French; other languages get English labels and prose in the user's language). Quotes
from the deck are never translated.

## How it works

Four isolated steps, so that the model never fills a gap with something it saw elsewhere.

| Step | What happens | Who |
|---|---|---|
| 1. Read | PDF text layer extracted by code; pages transcribed by a model into raw JSON | `pdf_text.py`, `preseed-page-transcriber` |
| 2. Profile | Sector, business model, B2B or B2C, announced stage, each with a quote. Not pre-seed: stop | `preseed-deck-profiler` |
| 3. Grid | Six checkers in parallel, one per block, each sees only its own questions. One question at a time. Every quote is verified by code against the cited page; rejected quotes are retried twice, then marked absent | `preseed-block-checker` × 6, `verify_quotes.py` |
| 3b. Confirmation | If the first-pass completeness is at or above 65 %, two more independent checker passes run and each question takes the median of the three values (1,2,2 gives 2; 1,1,2 gives 1). Disagreements are marked unstable in the report | `consolidate.py`, `preseed-block-checker` × 12 |
| 4. Reading | Completeness computed by code from the weights; the writer sees only the 24 answers, never the deck nor the score | `score.py`, `preseed-report-writer`, `report.py` |

The grid (24 questions, 6 blocks, weights) is fixed: [`skills/preseed-deck-reader/grid.md`](skills/preseed-deck-reader/grid.md)
is the readable version, [`scripts/grid.json`](scripts/grid.json) the one the scripts use. They must
stay identical. Weights are not hidden in a prompt.

## Layout

```
.claude-plugin/plugin.json
skills/preseed-deck-reader/SKILL.md    the orchestrator
skills/preseed-deck-reader/grid.md     the fixed pre-seed grid
agents/preseed-page-transcriber.md     sonnet
agents/preseed-deck-profiler.md        sonnet
agents/preseed-block-checker.md        sonnet, six in parallel
agents/preseed-report-writer.md        opus
scripts/grid.json                      grid as data
scripts/pdf_text.py                    PDF text per page, stdlib only
scripts/merge_pages.py                 page reference for checkers and verifier
scripts/grid_block.py                  one block's questions
scripts/verify_quotes.py               quote exists verbatim on the cited page
scripts/consolidate.py                 median of independent passes, per question
scripts/score.py                       completeness from values and weights
scripts/report.py                      final markdown
fixtures/fictional-preseed-deck.pdf    12-page fictional deck with deliberate gaps
fixtures/make_fixture.py               regenerates it
tests/                                 unittest, stdlib only
```

Python 3.9+, standard library only. Nothing leaves the local disk.

## Tests

```bash
python -m unittest discover -s tests
```

## Guardrails

- "Score" means deck completeness. Never quality, potential or investment score.
- No inference: a figure that is not on a page is absent.
- A value without a page and a verbatim quote is invalid and rejected by code.
- A red block produces a question, not a judgement.
- Nothing persists outside the report unless `--keep-work` is given.

## Known limits

- Quotes are verified against the PDF text layer. Text that exists only inside images (charts,
  screenshots) cannot be cited and is treated as absent. When the text layer is unusable
  (scanned deck), the model transcription becomes the reference and the report header says so.
- Checker values are not perfectly stable between runs on borderline questions. On the fixture,
  two consecutive runs disagreed on 4 of 24 questions (A2, C1, D3, E2), always between adjacent
  values (found/partial or partial/absent), never on the quotes. The quotes are verified by
  code; the values are a model's reading of a fixed criterion. The confirmation passes exist for
  this reason: above the threshold, three independent readings vote and the report shows where
  they disagreed. Below it, the single pass stands and this variance is not measured.
- The confirmation threshold and the number of extra passes live in `scripts/grid.json` under
  `confirmation`. They are about deck completeness, never about the company.
- The grid cannot tell a founder who presents poorly from a founder who did nothing. That is the
  call's job.

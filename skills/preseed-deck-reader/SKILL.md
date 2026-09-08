---
name: preseed-deck-reader
description: Use when the user runs /preseed-deck-reader with a path to a PRE-SEED pitch deck PDF and wants the deck-completeness report written next to it. Pre-seed only. Never a verdict.
argument-hint: path/to/deck.pdf [--keep-work]
disable-model-invocation: true
---

# Pre-seed deck reader

You orchestrate. You read nothing yourself, you judge nothing yourself, you compute nothing
yourself. Each step gets only what it needs; scripts do everything that must not go through a
model. The word "score" always means "deck completeness", never the quality of the company.

Scripts live in `${CLAUDE_PLUGIN_ROOT}/scripts/`. Agents are the plugin's own
(`preseed-deck-reader:<agent-name>`). Run scripts with `python`.

## 0. Setup

1. `DECK` = the path in `$ARGUMENTS` (strip `--keep-work` if present). If the file does not
   exist or is not a `.pdf`, say so and stop.
2. `WORK` = a fresh temporary directory:
   `python -c "import tempfile;print(tempfile.mkdtemp(prefix='preseed-deck-reader-'))"`.
3. `LANG` = the language for the report: the language the user writes in, or the default
   language set by their instructions, else `en`. ISO 639-1 code. Labels exist for `en` and `fr`;
   any other code gets English labels and the writer's prose in `LANG`.
4. `OUT` = `<same folder as DECK>/<deck file name without .pdf>.preseed-reading.md`.

## 1. Read

1. `python ${CLAUDE_PLUGIN_ROOT}/scripts/pdf_text.py DECK --out WORK/pdf-text.json`
   Note `page_count` and `reliable` from its output line.
2. Launch **one** `preseed-deck-reader:preseed-page-transcriber` agent with:
   `pdf_path=DECK`, `page_count=<from step 1>`, `output_path=WORK/transcription.json`.
3. `python ${CLAUDE_PLUGIN_ROOT}/scripts/merge_pages.py --pdf-text WORK/pdf-text.json --transcription WORK/transcription.json --out WORK/pages.json`
   From here on, `WORK/pages.json` is the only page reference anyone sees.

## 2. Profile

1. Launch **one** `preseed-deck-reader:preseed-deck-profiler` agent with:
   `pages_path=WORK/pages.json`, `output_path=WORK/profile.json`.
2. Read `announced_stage` in `WORK/profile.json`.
   - `pre-seed`: continue.
   - anything else (`seed`, `series-a`, `series-b-or-later`, `other`, `not_stated`): run
     `python ${CLAUDE_PLUGIN_ROOT}/scripts/report.py --deck DECK --profile WORK/profile.json --lang LANG --out OUT --abort-reason "<announced stage and the quote>"`,
     tell the user the deck announces that stage (or none) and that this reader only applies
     the pre-seed grid, give the path of the minimal report, go to step 5. No score, no answers.

## 3. Grid

### 3a. One checker pass into a directory `P`

This procedure is used for `P = WORK/pass-1`, and again for `WORK/pass-2` and `WORK/pass-3`
when step 3c asks for confirmation. Each pass is independent: same inputs, fresh agents, no
access to any other pass.

1. For each block `X` in A B C D E F (once, shared by all passes):
   `python ${CLAUDE_PLUGIN_ROOT}/scripts/grid_block.py --block X --out WORK/block-X.questions.json`
2. Launch the **six** `preseed-deck-reader:preseed-block-checker` agents **in one message**, one
   per block, each with: `pages_path=WORK/pages.json`, `profile_path=WORK/profile.json`,
   `questions_path=WORK/block-X.questions.json`, `output_path=P/block-X.json`,
   `output_language=LANG`.
   Never give a checker another block's questions, the grid file, or any other checker's output.
3. `python ${CLAUDE_PLUGIN_ROOT}/scripts/verify_quotes.py --answers-dir P --pages WORK/pages.json --out P/invalid.json`
4. If `P/invalid.json` is not empty, retry, **at most twice** per pass:
   - group the invalid entries by block;
   - for each block: `grid_block.py --block X --only <ids> --out P/block-X.retry.questions.json`,
     relaunch that block's checker with `questions_path=P/block-X.retry.questions.json`,
     `output_path=P/block-X.retry.json`, `output_language=LANG`, and
     `retry_reason=<the rejected quotes and reasons from invalid.json>`;
   - merge: replace, inside `P/block-X.json`, the answers whose ids are in the retry file with
     the retry answers (a short `python -c` is fine; do not edit values yourself);
   - run `verify_quotes.py` again.
5. After the second retry, or when no retry is needed:
   `python ${CLAUDE_PLUGIN_ROOT}/scripts/verify_quotes.py --answers-dir P --pages WORK/pages.json --out P/invalid.json --finalize`
   Remaining invalid answers become `absent` with `quote_invalid: true`. Nobody overrides that.

### 3b. First pass

Run 3a with `P = WORK/pass-1`, then:
`python ${CLAUDE_PLUGIN_ROOT}/scripts/score.py --answers-dir WORK/pass-1 --profile WORK/profile.json --out WORK/pass-1/score.json`
Read `confirmation_due` and `extra_passes` from its output line.

### 3c. Confirmation passes

- `confirmation_due` is `false`: `python ${CLAUDE_PLUGIN_ROOT}/scripts/consolidate.py --pass WORK/pass-1 --out WORK/final`
- `confirmation_due` is `true`: run 3a for `P = WORK/pass-2` and `P = WORK/pass-3` (launch all
  twelve checkers in one message if you can), then
  `python ${CLAUDE_PLUGIN_ROOT}/scripts/consolidate.py --pass WORK/pass-1 --pass WORK/pass-2 --pass WORK/pass-3 --out WORK/final`
  The script takes, per question, the median of the three values and marks disagreements as
  unstable. You do not pick values yourself.

The threshold and the number of extra passes live in `grid.json` under `confirmation`. They
concern the completeness of the deck, never the company.

## 4. Score, reading, report

1. `python ${CLAUDE_PLUGIN_ROOT}/scripts/score.py --answers-dir WORK/final --profile WORK/profile.json --out WORK/score.json`
   Do not read the percentages aloud to any agent. Only the `red_blocks` list goes to the writer.
2. Launch **one** `preseed-deck-reader:preseed-report-writer` agent with:
   `answers_dir=WORK/final`, `grid_path=${CLAUDE_PLUGIN_ROOT}/scripts/grid.json`,
   `red_blocks=<list from score.json>`, `output_language=LANG`, `output_path=WORK/reading.md`.
   The writer never receives DECK, pages.json, transcription.json, score.json or the pass
   directories.
3. `python ${CLAUDE_PLUGIN_ROOT}/scripts/report.py --deck DECK --profile WORK/profile.json --answers-dir WORK/final --score WORK/score.json --reading WORK/reading.md --pages WORK/pages.json --lang LANG --out OUT`

## 5. Finish

1. Unless `--keep-work` was given, delete `WORK`. Nothing persists outside `OUT`.
2. Tell the user, in their language: the report path, the six block percentages and the global
   as printed by `score.py`, the red blocks, the number of passes and the unstable questions,
   and how many quotes were rejected. Nothing else. No opinion on the company, no "looks
   strong", no "I would pass".

## Rules you never bend

- You do not answer a grid question yourself, not even an obvious one. Only a checker does.
- You do not edit a checker's value, quote or gap. Only `verify_quotes.py --finalize` and
  `consolidate.py` change a value, by rules written in their docstrings.
- Nothing leaves the local disk. No web, no upload, no external tool.
- A deck that does not announce pre-seed is not scored. No exception "because it looks like
  pre-seed".
- If any script exits with an error, show the error and stop. Do not improvise its output.

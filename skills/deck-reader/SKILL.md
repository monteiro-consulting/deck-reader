---
name: deck-reader
description: Use when the user runs /deck-reader with a path to a pitch deck PDF (and, at seed, the annexes the founder sent) and wants the deck-completeness report written next to it. One grid per stage (pre-seed, seed); the deck's announced stage picks the grid. Never a verdict.
argument-hint: path/to/deck.pdf [--annex file ...] [--keep-work]
disable-model-invocation: true
---

# Deck reader

You orchestrate. You read nothing yourself, you judge nothing yourself, you compute nothing
yourself. Each step gets only what it needs; scripts do everything that must not go through a
model. The word "score" always means "deck completeness", never the quality of the company.

Scripts live in `${CLAUDE_PLUGIN_ROOT}/scripts/`. Agents are the plugin's own
(`deck-reader:<agent-name>`). Run scripts with `python`. `--grid` takes a stage name
(`preseed`, `seed`); the grids are in `scripts/grids/`.

## 0. Setup

1. `DECK` = the first `.pdf` path in `$ARGUMENTS`. `ANNEXES` = every path given after `--annex`
   (repeatable). Strip `--keep-work`. If DECK does not exist or is not a `.pdf`, say so and stop.
   An annex that does not exist: say so and stop.
2. `WORK` = a fresh temporary directory:
   `python -c "import tempfile;print(tempfile.mkdtemp(prefix='deck-reader-'))"`.
3. `LANG` = the language for the report: the language the user writes in, or the default
   language set by their instructions, else `en`. ISO 639-1 code. Labels exist for `en` and `fr`;
   any other code gets English labels and the writers' prose in `LANG`.
4. `OUT` = `<same folder as DECK>/<deck file name without .pdf>.reading.md`.
   `EMAIL` = `<same folder as DECK>/<deck file name without .pdf>.founder-email.md`.

## 1. Read (every stage)

1. `python ${CLAUDE_PLUGIN_ROOT}/scripts/pdf_text.py DECK --out WORK/pdf-text.json`
   Note `page_count` and `reliable` from its output line.
2. Launch **one** `deck-reader:page-transcriber` agent with:
   `pdf_path=DECK`, `page_count=<from step 1>`, `output_path=WORK/transcription.json`.
3. `python ${CLAUDE_PLUGIN_ROOT}/scripts/merge_pages.py --pdf-text WORK/pdf-text.json --transcription WORK/transcription.json --out WORK/pages.json`
   From here on, `WORK/pages.json` is the only page reference anyone sees.

## 2. Profile and route (every stage)

1. Launch **one** `deck-reader:deck-profiler` agent with:
   `pages_path=WORK/pages.json`, `output_path=WORK/profile.json`.
2. Read `announced_stage` in `WORK/profile.json` and set `GRID`:
   - `pre-seed` → `GRID=preseed`, continue at **3P**. Annexes, if any, are ignored and you say so.
   - `seed` → `GRID=seed`, continue at **3S**.
   - anything else (`series-a`, `series-b-or-later`, `other`, `not_stated`): run
     `python ${CLAUDE_PLUGIN_ROOT}/scripts/report.py --grid preseed --deck DECK --profile WORK/profile.json --pages WORK/pages.json --lang LANG --out OUT --abort-kind stage --abort-reason "<announced stage and the quote>"`,
     tell the user the deck announces that stage (or none) and that no grid exists for it, give
     the path of the minimal report, go to step 9. No score, no answers.

## 3P. Pre-seed: grid

Run the checker procedure of section 5 with `GRID=preseed` and no `claims_path`, then go to
section 7.

## 3S. Seed: annexes and claims

1. `python ${CLAUDE_PLUGIN_ROOT}/scripts/annex_text.py --out WORK/annexes.json ANNEXES...`
   (run it even with no annex: it writes `annex_count: 0`). Note `readable_count`.
2. `python ${CLAUDE_PLUGIN_ROOT}/scripts/claim_types.py --grid seed --out WORK/types.json`
3. Launch **one** `deck-reader:claim-extractor` agent with:
   `pages_path=WORK/pages.json`, `types_path=WORK/types.json`, `output_path=WORK/claims.json`.
4. `python ${CLAUDE_PLUGIN_ROOT}/scripts/check_claims.py --grid seed --claims WORK/claims.json --pages WORK/pages.json --out WORK/claims.verified.json --invalid WORK/claims.invalid.json`
   If the exit code is 1, relaunch the extractor **once** with `retry_reason=<the invalid list>`
   and `output_path=WORK/claims.retry.json`, merge the retried claims into `WORK/claims.json`
   by id (a short `python -c`; do not edit a claim yourself), then run `check_claims.py` again
   with `--finalize`. Invalid claims are dropped by the script.

## 4S. Seed: proof in the annexes, first gate

1. If `readable_count` is 0, skip to step 3 below (nothing to match).
2. Launch **one** `deck-reader:annex-matcher` agent with:
   `claims_path=WORK/claims.verified.json`, `annexes_path=WORK/annexes.json`,
   `output_path=WORK/matches.json`.
   Then `python ${CLAUDE_PLUGIN_ROOT}/scripts/verify_matches.py --grid seed --claims WORK/claims.verified.json --matches WORK/matches.json --annexes WORK/annexes.json --out WORK/claims.annex.json --invalid WORK/matches.invalid.json`
   Exit code 1: relaunch the matcher **once** with `retry_reason=<the invalid list>` for those
   claims only, merge by `claim_id` into `WORK/matches.json`, run again with `--finalize`.
   With no annex: `python ${CLAUDE_PLUGIN_ROOT}/scripts/verify_matches.py --grid seed --claims WORK/claims.verified.json --matches <an empty {"matches": []} file> --annexes WORK/annexes.json --out WORK/claims.annex.json --finalize`
3. `python ${CLAUDE_PLUGIN_ROOT}/scripts/seed_gate.py annexes --grid seed --claims WORK/claims.annex.json --annexes WORK/annexes.json --out WORK/gate.json`
   Read `decision`:
   - `stop_no_annexes`:
     `python ${CLAUDE_PLUGIN_ROOT}/scripts/founder_email.py --kind none --deck DECK --lang LANG --out EMAIL`
     then `report.py --grid seed --deck DECK --profile WORK/profile.json --pages WORK/pages.json --annexes WORK/annexes.json --claims WORK/claims.annex.json --gate WORK/gate.json --email EMAIL --lang LANG --out OUT --abort-kind no_annexes --abort-reason "no annex provided"`.
     Tell the user the deck came without annexes, that the reading stops there, and where the
     report and the email draft are. **No web check, no grid.** Go to step 9.
   - `stop_insufficient`:
     `python ${CLAUDE_PLUGIN_ROOT}/scripts/founder_email.py --kind missing --deck DECK --lang LANG --gate WORK/gate.json --out EMAIL`
     then `report.py` as above with `--abort-kind insufficient_annexes --abort-reason "<key_types_covered> of <key_types_present> covered"`.
     Tell the user which key figures are not covered and where the email draft is. Go to step 9.
   - `continue`: if `to_request` is not empty,
     `python ${CLAUDE_PLUGIN_ROOT}/scripts/founder_email.py --kind leftovers --deck DECK --lang LANG --gate WORK/gate.json --out EMAIL`
     (the reading goes on; the email lists what is still missing). Continue.

## 5S. Seed: web check

1. Launch **one** `deck-reader:web-verifier` agent with:
   `claims_path=WORK/claims.annex.json`, `profile_path=WORK/profile.json`,
   `output_path=WORK/web.json`, `min_sources=<grid web.min_independent_sources, 2>`.
   It is the only agent allowed on the web, and only on the claims whose `check` is `web` or `both`.
2. `python ${CLAUDE_PLUGIN_ROOT}/scripts/verify_web.py --grid seed --claims WORK/claims.annex.json --web WORK/web.json --out WORK/claims.final.json`
   Read `blatant_ids`.

## 6S. Seed: double check, second gate

1. If `blatant_ids` is empty: `python ${CLAUDE_PLUGIN_ROOT}/scripts/seed_gate.py contradictions --grid seed --claims WORK/claims.final.json --out WORK/gate2.json --out-claims WORK/claims.reviewed.json`
   and continue with `CLAIMS=WORK/claims.reviewed.json`.
2. Otherwise launch **one** `deck-reader:contradiction-reviewer` agent with:
   `claims_path=WORK/claims.final.json`, `annexes_path=WORK/annexes.json`,
   `pages_path=WORK/pages.json`, `output_path=WORK/review.json`.
   Then `python ${CLAUDE_PLUGIN_ROOT}/scripts/seed_gate.py contradictions --grid seed --claims WORK/claims.final.json --review WORK/review.json --out WORK/gate2.json --out-claims WORK/claims.reviewed.json`
   Read `decision`:
   - `stop_contradiction`: `report.py --grid seed --deck DECK --profile WORK/profile.json --pages WORK/pages.json --annexes WORK/annexes.json --claims WORK/claims.reviewed.json --gate WORK/gate.json --email EMAIL --lang LANG --out OUT --abort-kind contradiction --abort-reason "<the stopping claim ids and their statements>"`.
     Tell the user which statements are contradicted, that the sources on both sides are in the
     report, and that this is not a verdict. Go to step 9.
   - `continue`: `CLAIMS=WORK/claims.reviewed.json`. The lowered claims will become questions.
3. Run the checker procedure of section 5 with `GRID=seed` and `claims_path=CLAIMS`, then go
   to section 7.

## 5. Checker procedure (every stage)

### 5a. One checker pass into a directory `P`

Used for `P = WORK/pass-1`, and again for `WORK/pass-2` and `WORK/pass-3` when 5c asks for
confirmation. Each pass is independent: same inputs, fresh agents, no access to any other pass.

1. `BLOCKS` = the block ids of the grid (`python -c "import json,sys;print(' '.join(b['id'] for b in json.load(open(sys.argv[1]))['blocks']))" ${CLAUDE_PLUGIN_ROOT}/scripts/grids/GRID.json`).
   For each block `X` (once, shared by all passes):
   `python ${CLAUDE_PLUGIN_ROOT}/scripts/grid_block.py --grid GRID --profile WORK/profile.json --block X --out WORK/block-X.questions.json`
2. Launch the `deck-reader:block-checker` agents **in one message**, one per block, each with:
   `pages_path=WORK/pages.json`, `profile_path=WORK/profile.json`,
   `questions_path=WORK/block-X.questions.json`, `output_path=P/block-X.json`,
   `output_language=LANG`, and at seed `claims_path=CLAIMS`.
   Never give a checker another block's questions, the grid file, or any other checker's output.
3. `python ${CLAUDE_PLUGIN_ROOT}/scripts/verify_quotes.py --answers-dir P --pages WORK/pages.json --out P/invalid.json`
4. If `P/invalid.json` is not empty, retry, **at most twice** per pass:
   - group the invalid entries by block;
   - for each block: `grid_block.py --grid GRID --profile WORK/profile.json --block X --only <ids> --out P/block-X.retry.questions.json`,
     relaunch that block's checker with `questions_path=P/block-X.retry.questions.json`,
     `output_path=P/block-X.retry.json`, `output_language=LANG`, the same `claims_path`, and
     `retry_reason=<the rejected quotes and reasons from invalid.json>`;
   - merge: replace, inside `P/block-X.json`, the answers whose ids are in the retry file with
     the retry answers (a short `python -c` is fine; do not edit values yourself);
   - run `verify_quotes.py` again.
5. After the second retry, or when no retry is needed:
   `python ${CLAUDE_PLUGIN_ROOT}/scripts/verify_quotes.py --answers-dir P --pages WORK/pages.json --out P/invalid.json --finalize`
   Remaining invalid answers become `absent` with `quote_invalid: true`. Nobody overrides that.
6. Seed only: `python ${CLAUDE_PLUGIN_ROOT}/scripts/apply_proof_cap.py --grid seed --profile WORK/profile.json --answers-dir P --claims CLAIMS`
   A figure without a proven or confirmed claim behind it is capped at partial; an answer
   citing a claim left to probe is lowered one step. The script does it, not you.

### 5b. First pass

Run 5a with `P = WORK/pass-1`, then:
`python ${CLAUDE_PLUGIN_ROOT}/scripts/score.py --grid GRID --answers-dir WORK/pass-1 --profile WORK/profile.json --out WORK/pass-1/score.json`
Read `confirmation_due` and `extra_passes` from its output line.

### 5c. Confirmation passes

- `confirmation_due` is `false`: `python ${CLAUDE_PLUGIN_ROOT}/scripts/consolidate.py --pass WORK/pass-1 --out WORK/final`
- `confirmation_due` is `true`: run 5a for `P = WORK/pass-2` and `P = WORK/pass-3` (launch all
  the checkers in one message if you can), then
  `python ${CLAUDE_PLUGIN_ROOT}/scripts/consolidate.py --pass WORK/pass-1 --pass WORK/pass-2 --pass WORK/pass-3 --out WORK/final`
  The script takes, per question, the median of the three values and marks disagreements as
  unstable. You do not pick values yourself.

## 7. Score, reading, report (every stage)

1. `python ${CLAUDE_PLUGIN_ROOT}/scripts/score.py --grid GRID --answers-dir WORK/final --profile WORK/profile.json --out WORK/score.json`
   Do not read the percentages aloud to any agent. Only the `red_blocks` list goes to the writer.
2. Launch **one** `deck-reader:report-writer` agent with:
   `answers_dir=WORK/final`, `grid_path=${CLAUDE_PLUGIN_ROOT}/scripts/grids/GRID.json`,
   `red_blocks=<list from score.json>`, `output_language=LANG`, `output_path=WORK/reading.md`,
   and at seed `claims_path=CLAIMS`.
   The writer never receives DECK, pages.json, transcription.json, score.json, the annexes or
   the pass directories.
3. Pre-seed: `python ${CLAUDE_PLUGIN_ROOT}/scripts/report.py --grid preseed --deck DECK --profile WORK/profile.json --answers-dir WORK/final --score WORK/score.json --reading WORK/reading.md --pages WORK/pages.json --lang LANG --out OUT`
   Seed: the same with `--grid seed --annexes WORK/annexes.json --claims CLAIMS --gate WORK/gate.json --email EMAIL`.

## 9. Finish

1. Unless `--keep-work` was given, delete `WORK`. Nothing persists outside `OUT` and, at seed
   when something is missing, `EMAIL`.
2. Tell the user, in their language: the report path; the stage and grid used; the block
   percentages and the global as printed by `score.py`; the red blocks; the number of passes and
   the unstable questions; how many quotes were rejected; at seed, how many claims were proven,
   confirmed, not covered, unverifiable, to probe, and whether an email draft was written and
   where. Nothing else. No opinion on the company, no "looks strong", no "I would pass". If the
   reading stopped, say at which gate and why, in one sentence, and that the investor decides.

## Rules you never bend

- You do not answer a grid question yourself, not even an obvious one. Only a checker does.
- You do not extract, match, verify or review a claim yourself. Only the agents of sections 3S
  to 6S do, and only the scripts set a claim's status.
- You do not edit a checker's value, quote or gap. Only `verify_quotes.py --finalize`,
  `apply_proof_cap.py` and `consolidate.py` change a value, by rules written in their docstrings.
- The only agent that touches the web is `web-verifier` (and `contradiction-reviewer` to re-check
  a source). Everything else stays on the local disk. No upload, ever.
- The tool never sends the email. It writes a draft; the user decides.
- A deck is read with the grid of the stage it announces. No exception "because it looks like
  seed". No grid for the stage: no score.
- If any script exits with an error, show the error and stop. Do not improvise its output.

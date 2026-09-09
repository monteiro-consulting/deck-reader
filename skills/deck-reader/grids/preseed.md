# The pre-seed grid

**Grid version: 2026-09-08. Stage covered: pre-seed only.**

This file is a fixed copy of the grid. It does not change at run time. The machine-readable
version used by the scripts is `scripts/grids/preseed.json`; both must stay identical.

**A deck is scored according to its stage.** This grid only scores pre-seed decks, with
questions and weights made for pre-seed. A seed deck is not scored with it: it would excuse
absences a seed company cannot afford. One grid per stage, never one grid for all; the deck's
announced stage picks the grid (`seed.md` for seed). No grid for the announced stage: the tool
stops and says so.

**What the grid measures**: the completeness of the deck, that is, how well it answers the
questions an investor will ask. It does not measure the quality of the company. A complete deck
can describe a bad company, and a founder who made a poor deck is not a founder who did nothing.
The call decides; the grid prepares the call.

**What the grid never produces**: a recommendation to invest or not, a decision threshold, a
rating of the company.

---

## The pre-seed principle

There are almost no figures. We judge **evidence of learning**: what the founder did, tested,
learned and abandoned.

Red signals of the stage:

- No user interviews
- No invalidated hypothesis
- Part-time founders without explanation
- No "we did", only "we will"

---

## The scale

Each question receives exactly one of three values, with the deck page and the verbatim quote
that justifies it.

| Value | Points | Meaning |
|---|---|---|
| **Found** | 2 | The deck answers, with a verifiable element: a figure, a name, a quote, a screenshot |
| **Partial** | 1 | The deck touches the subject but without a verifiable element, or vaguely |
| **Absent** | 0 | The deck does not mention it. No inference: if it is not on a page, it is absent |

---

## Blocks and questions

A weight of 0 means the question is asked for information but does not count in the score.

### Block A. Problem and field, weight 3

| # | Question | Found if | Note |
|---|---|---|---|
| A1 | Who suffers from the problem, precisely? | A nameable profile: "purchasing manager in an industrial SME of 50 to 200 people", not "companies" | |
| A2 | How much does the problem cost this person today? | A cost in time, money or risk, with a source or a testimony | Partial accepted if the order of magnitude is argued |
| A3 | How does this person cope today without the product? | The real competitor is named, including Excel, an intern or "we do nothing" | A deck that says "no competitor" is partial at best |
| A4 | How many users did the founder interview, and what do they say? | A number and at least one verbatim quote | **The central question of the stage.** Absent = main red signal |

### Block B. Evidence, weight 3

| # | Question | Found if | Note |
|---|---|---|---|
| B1 | Does the product exist? | Three levels to distinguish: nothing, mockup, prototype used by real people. Found only at the third | Mockup = partial |
| B2 | What weak signals of interest? | A quantified waiting list, named letters of intent, pilots under way, first payments even tiny | A first payment of 50 euros is worth more than a waiting list of 2,000 emails |
| B3 | Named customers or pilots? | Names of companies or people, not blurry logos or "large accounts" | Weight reduced to 1 if the sector is B2C |
| B4 | What was tested and abandoned? | A pivot, an invalidated hypothesis, a removed feature, with what triggered it | A deck with nothing abandoned is a deck without field work. Absent = red |
| B5 | What has the team done in the last six months? | Past, dated actions, not intentions | Count the "we did" against the "we will". Absent = red |

### Block C. Economics, weight 1

| # | Question | Found if | Note |
|---|---|---|---|
| C1 | What price, and tested on whom? | A price and the proof that it was offered to real prospects, with their reaction | A price out of a spreadsheet = partial |
| C2 | Who pays, and is it the same person as the one who suffers? | The payer is identified, and the gap with the user is explained if there is one | Frequent in B2B: the user is not the decision-maker |
| C3 | Margin, acquisition cost, retention? | A sourced figure | **Weight 0.** Asked for information, almost always absent at this stage and that is not a signal |

### Block D. Market and timing, weight 2

| # | Question | Found if | Note |
|---|---|---|---|
| D1 | Market size computed bottom-up? | Number of possible customers multiplied by a price, with visible assumptions | A Gartner figure or "a 40 billion market" = absent, not partial |
| D2 | Why now? | A recent, named change: regulation, technology, behaviour, a cost that dropped | Absent = the deck does not say why this does not exist already |
| D3 | Why is it not already done by an incumbent? | A structural reason, not "they are slow" | |

### Block E. Team, weight 3

The heaviest block of the stage. What cannot be read in a deck is the subject of the call.

| # | Question | Found if | Note |
|---|---|---|---|
| E1 | Who did what, concretely, before? | Verifiable achievements, not titles. "Built X used by Y people" | "Ex-Google" without role or result = partial |
| E2 | What link between the founders and the problem? | They lived it, or they spent identifiable time with those who live it | |
| E3 | Full-time or not? | Stated explicitly for each founder | Not stated = absent. Part-time explained and dated = partial |
| E4 | Equity split between founders? | Percentages are given, or the deck says they are available | A very unbalanced split or a founder who left with shares is a question for the call, not a verdict |
| E5 | Do the skills cover product, tech and sales? | Each founder is tied to a role, and any gap is named with a plan | A named gap is worth more than a hidden gap |

### Block F. Money and next step, weight 2

| # | Question | Found if | Note |
|---|---|---|---|
| F1 | How much is asked, and what for? | An amount and a breakdown, even rough | |
| F2 | What proof must the company obtain before the next round? | A measurable, dated goal: "20 paying customers within 12 months" | **The question that replaces runway.** Absent = the money has no purpose |
| F3 | Does the amount allow reaching that proof? | The link between F1 and F2 is made, with a duration | Only assessed if F1 and F2 are found |
| F4 | Who already put money in? | Names or categories (founders, relatives, business angels, grant), amounts | Founders who put nothing in themselves: a question for the call |

---

## The computation

1. **Per question**: 0, 1 or 2 points, multiplied by the block weight (or by the question's own
   weight when one is given).
2. **Per block**: points obtained divided by the maximum possible, as a percentage.
3. **Global**: average of the blocks weighted by their weight.

Weights summary:

| Block | Weight | Approximate share of the score |
|---|---|---|
| A. Problem and field | 3 | 21 % |
| B. Evidence | 3 | 21 % |
| C. Economics | 1 | 7 % |
| D. Market and timing | 2 | 14 % |
| E. Team | 3 | 21 % |
| F. Money and next step | 2 | 14 % |

The global figure is the least useful of the seven. The six bars say where to dig.

Implementation rules, fixed with the grid:

- A question with weight 0 (C3) is excluded from the block maximum.
- F3 is `not_assessable` and excluded from the block maximum when F1 or F2 is not found.
- B3 counts with weight 1 instead of the block weight when the profile says B2C.
- A block is **red** when its completeness is below 50 %.
- **Confirmation passes.** A model's reading of a criterion is not perfectly stable between
  runs on borderline questions. When the first-pass deck completeness is between 65 % and 80 %
  inclusive, two more independent checker passes are run and each question
  takes the median of the three values: 1,2,2 gives 2; 1,1,2 gives 1; 0,1,2 gives 1. Questions
  whose passes disagree are marked unstable in the report, with the three readings. Outside that
  band, below 65 % or above 80 %, the single pass stands. The threshold is about the completeness of the deck, never
  about the company.

---

## What the tool outputs

For each deck:

- **Six bars** of completeness, one per block, and the global.
- **Per question**: the value, the page, the verbatim quote. Nothing else.
- **Questions for the call**: each absent or partial question of a weight-3 block becomes a
  question to ask the founder, worded as such. Example: "The deck does not say who is full-time.
  To ask."
- **The three main gaps**, ranked by weight.
- **What the deck does not say**, one sentence per red block.

What it does not output: a rating of the company, a verdict, a threshold, a comparison with other
decks.

---

## Guardrails

- The score is called "deck completeness". Never "quality", "potential" or "investment score".
- No inference. A figure that is not on a page is absent, not "probably around".
- Each value cites a page and a quote. A value without a page is invalid.
- The weights live in this file, readable by all, and are corrected at each post-mortem. They are
  not hidden in a prompt.
- A red block produces a question, not a judgement.

---

## What the grid cannot do

- Tell a founder who presents poorly from a founder who did nothing.
- Read what can only be read in a call: how an objection is answered, honesty about what does not
  work, speed of reasoning.
- Predict anything. Each score is dated and kept. At 18 months we look at what the companies
  became, and publish the result, flattering or not.

---

## Revisions

| Date | Change | Triggered by |
|---|---|---|
| 2026-09-08 | First version: concept, workflow, pre-seed grid | Design of the deck reader |

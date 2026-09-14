# The series A grid

**Grid version: 2026-09-13. Stage covered: series A only.**

This file is a fixed copy of the grid. It does not change at run time. The machine-readable
version used by the scripts is `scripts/grids/series_a.json`; both must stay identical.

**A deck is scored according to its stage.** Same engine as the seed grid, another question.
Seed asks "does what the deck says hold up?". Series A asks "**does the machine repeat?**": does
the next customer cost the same, bring the same, and sign without the founder in the room.

**What the grid measures**: the completeness of the deck, and whether its statements are backed
by the required documents of the stage and model and by public sources. It does not measure the quality of the
company. No verdict, no threshold, no rating.

---

## What changes from seed

| | Seed | Series A |
|---|---|---|
| What is judged | Evidence of use: who pays, who comes back | Evidence of repetition: the next customer costs the same, brings the same, signs without the founder |
| Input | The deck, plus optional annexes | The deck, plus **the required documents of the stage and model**: the base list (monthly P&L over 24 months, cohorts over 12 months or more, CRM export with weighted pipeline, cap table, three-year financial model, contracts of the top 10 customers) adjusted by the model block |
| First gate | No annex, or key figures less than half covered | **Fixed list.** A missing document stops the reading and produces the email draft. No coverage threshold |
| Heaviest blocks | Traction, economics (weight 3) | **Unit economics, net retention (weight 3).** Raw traction drops to 2 |
| Claim types | Revenue, customers, retention, churn, acquisition, pricing, runway, cap table, named customers, competitors, founders, funding, why now, market | The same, plus **NRR, weighted pipeline, sales cycle by segment, gross margin confirmed against the P&L, top 10 concentration, burn multiple, share of deals closed without a founder, key hires** |
| Web check | Named customers, competitors, founders, funding, why now, market | The same, plus **public reviews** (G2, Capterra or the sector's equivalent), **open job posts**, **press of previous rounds**, and the LinkedIn profile of every announced key hire |
| Extra output | The leftovers email for what is not covered | **The list of documents to request** replaces the leftovers email. **Series A benchmarks** are shown next to every figure |

---

## The series A principle

There are one or two years of figures. Whether someone pays and comes back is no longer the
question. The question is whether the machine repeats: does the next customer cost the same as
the last one, bring the same, and sign without a founder in the room.

Red signals of the stage:

- An ARR without the 24 monthly points behind it
- No net retention, or a gross retention without the reasons customers left
- A pipeline that is not weighted, or that does not cover next year's plan
- Every deal closed by a founder
- A key hire announced on a slide and absent from LinkedIn
- A document of the required list missing

---

## How the series A reading works

1. **Read.** The PDF page by page; the annexes read separately (`annex_text.py`).
2. **Profile.** Sector, model type (SaaS, marketplace, consumer, e-commerce, hardware, fintech,
   biotech), B2B or B2C, announced stage. The stage picks the grid, the model picks the model
   block. No model detected means SaaS.
3. **Documents, first gate.** An agent sorts each annex into one of the required documents of
   the stage and model, with a verbatim quote and the months covered (`annex-classifier`); the
   code checks the quote and compares with the list, the base list below adjusted by the model
   block's `documents` verb (`documents_gate.py documents --profile`):
   - a document missing, or covering fewer months than required: stop, email draft document by
     document, no claims, no web, no grid;
   - every document present: continue.
4. **Claims.** Every verifiable statement of the deck, one line each with page and quote
   (`claim-extractor`, checked by `check_claims.py`). The seed types plus the series A types.
5. **Proof in the documents.** Each claim looked up in the required documents (`annex-matcher`,
   checked and classified by `verify_matches.py`). Same gap thresholds as seed. What is not
   covered is listed in the report; it never stops the reading.
6. **Web check**, only now, and only on what a document cannot settle: the seed scope, plus
   public reviews, open job posts, the press of previous rounds, and the LinkedIn profile of
   each announced key hire (`web-verifier`, rules enforced by `verify_web.py`). Searched both for
   and against; at least two independent domains to conclude; otherwise unverifiable.
7. **Double check.** As at seed: every blatant contradiction goes to an independent reviewer
   whose only job is to find an honest explanation (`contradiction-reviewer`). Without one, the
   second gate stops the reading and shows the sources on both sides.
8. **Grid**, on the deck and the proofs. A figure without a proven or confirmed claim behind it
   is capped at partial by code (`apply_proof_cap.py`); an answer citing a gap to probe is
   lowered one step.
9. **Report.** Eight bars, the reading, the gaps to probe, the documents to request with the
   email draft, the claims table with the benchmark next to each figure, question by question.

---

## The scale

Found 2, partial 1, absent 0, each with the deck page and the verbatim quote. Same scale as
pre-seed and seed. Same rule as seed: a question marked *proof* cannot be found from the deck
alone.

---

## Blocks and questions

"Proof expected" is the document, among the required ones, that backs the answer.

### Block A. Problem and customer, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| A1 | Which segment buys, and do the last ten customers match it? | A nameable profile (size, role, sector), and the last ten signed customers fit it, checked against the contracts | Top 10 contracts | *proof*. A segment that changes with every customer is not a repeatable machine |
| A2 | Why do they buy, and why do they renew, in their own words? | A customer quote for the purchase and one for the renewal, or a documented use case with both | The deck suffices | |
| A3 | What was tried and dropped since the seed? | A segment, channel or feature abandoned since the seed round, dated, with what triggered it | The deck suffices | Nothing dropped since seed = partial at best |

### Block B. Traction, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| B1 | ARR today, and the monthly curve over 24 months? | An ARR figure and the monthly revenue points over 24 months, matching the P&L | Monthly P&L | *proof*. A growth percentage without its starting point = absent |
| B2 | How many paying customers, and the average contract value by segment? | A customer count and an ACV per segment, backed by the contracts or the P&L | Contracts, P&L | *proof* |
| B3 | Year-over-year growth, with the starting point? | Two dated ARR points twelve months apart and the ratio | Monthly P&L | *proof*. Benchmark shown next to the figure, never in the score |
| B4 | Do the named customers exist, pay, and use the product? | Confirmed outside the deck: a contract in the annexes, and a website, LinkedIn page or public review | Contracts, web | *proof*. **Still the central question.** Absent = red |
| B5 | How much of ARR do the top ten customers make? | A share of ARR for the top ten customers, confirmed against the contracts or the P&L | Contracts, P&L | *proof*. A single customer above 40 % of ARR is a question for the call, not a verdict |
| B6 | Where do customers come from, channel by channel? | Each channel with its share of new ARR, from the CRM export | CRM export | *proof*. All from one channel = partial |

### Block C. Unit economics, weight 3

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| C1 | Gross margin, confirmed against the P&L? | A gross margin with what is included in cost of revenue, and the same figure in the P&L | Monthly P&L | *proof*. A margin that excludes hosting or support = partial |
| C2 | Customer acquisition cost by channel, and payback? | A CAC per channel with the method, and the months to recover it | CRM export, P&L | *proof* |
| C3 | Sales cycle by segment? | An average duration from first contact to signature, per segment, from the CRM export | CRM export | *proof*. B2B only, weight 0 in B2C |
| C4 | Burn multiple? | Net burn divided by net new ARR over the last twelve months, both figures from the P&L | Monthly P&L | *proof*. Benchmark shown next to the figure (Sacks, Bessemer), never in the score |
| C5 | Weighted pipeline, and how much of next year's plan does it cover? | A pipeline by stage with probabilities, its weighted total, and the ratio to the plan | CRM export, financial model | *proof*. An unweighted pipeline = partial |
| C6 | What share of deals closed without a founder? | A share of signed deals whose owner in the CRM is not a founder | CRM export | *proof*. **The question that separates series A from seed.** Absent = red |

### Block D. Net retention, weight 3

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| D1 | Net revenue retention over twelve months? | An NRR over a twelve-month window with the definition used, recomputable from the cohorts | Cohorts | *proof*. Benchmark shown next to the figure, never in the score |
| D2 | Gross retention and logo churn, with the reasons? | A gross revenue retention or logo churn figure, and a reason per lost customer | Cohorts, P&L | *proof*. Absent = the deck hides churn. Red |
| D3 | Do the cohorts flatten, over twelve months or more? | Cohort curves of at least twelve months, with the month where they flatten | Cohorts | *proof* |
| D4 | Which customers expanded, and why? | Named customers or a share of ARR from expansion, with the trigger (seats, modules, price) | Cohorts, contracts | *proof* |

### Block E. Market and competition, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| E1 | Market size computed bottom-up with the observed ACV? | Possible customers in the segment multiplied by the ACV actually signed, with visible assumptions | The deck, assumptions visible | An analyst figure = absent |
| E2 | Who are the competitors, where do they win, and who was lost to them? | Named competitors, one point where each wins, and deals lost to them | Web, CRM export | Omitted competitors become a contradiction |
| E3 | Why now, and why still? | A recent, named, verifiable change, and why the window is still open two years later | Web | |

### Block F. Team, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| F1 | Who did what before, verifiably? | Named achievements, confirmed on LinkedIn or elsewhere | Web: LinkedIn | *proof*. A title without a result = partial |
| F2 | Do the announced key hires exist? | Each key hire named in the deck (VP Sales, VP Engineering...) found on LinkedIn with that role at the company | Web: LinkedIn | *proof*. A VP Sales on a slide who is not on LinkedIn is a contradiction. Absent = red |
| F3 | Do the open job posts match the plan? | Public job posts that correspond to the hiring plan of the round | Web: careers page, LinkedIn jobs | *proof*. No open post while the deck plans ten hires: a question for the call |
| F4 | Who owns what, and is everyone full-time? | Founders, investors, employees and option pool shares from the cap table, and full-time status per founder | Cap table | *proof* |

### Block G. Money and next step, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| G1 | How much is asked, and what for, hire by hire? | An amount and a breakdown by function with the hiring plan | The deck suffices | |
| G2 | What figures must be reached for series B? | A measurable, dated goal: ARR, NRR, burn multiple | The deck suffices | Absent = the money has no purpose. Red |
| G3 | Runway and burn on the three-year model? | Monthly burn, cash, and the months of runway, consistent with the financial model | Financial model, P&L | *proof* |
| G4 | Previous rounds: amounts, investors, and do they follow on? | Amounts and investors for each round, in the cap table and the press, and whether existing investors follow on | Cap table, web: press | *proof*. The press of previous rounds is checked on the web |

### Block H. References, weight 1

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| H1 | Customers we can call, including one that left? | Names and a way to contact them, including at least one lost customer | The deck suffices | |
| H2 | Former colleagues, investors or key hires we can call? | Same | The deck suffices | Asked to prepare the call, not to judge the deck |

---

## The business-model block

The profile detects the model; no model detected means SaaS. The model block lives in its own
file (`scripts/grids/models/<model>.json`, readable copy in `grids/models/<model>.md`) and is
applied to this grid by `grid_lib.effective_grid` in four verbs, in this order: **remove**
questions of the stage grid (by id), **reweight** blocks or questions, **add** questions to a
block with the block weight, or in a block the model brings, **documents** to adjust the
required document list of the first gate (remove by id, add entries of the same shape). One
block per business model, never one grid per sector.

| Model | What the block does to the series A grid |
|---|---|
| SaaS (default) | Nothing. The grid and the document list are written for it. Benchmarks only |
| Marketplace | Adds M1 to M5 to block B: GMV, take rate and net revenue over 24 months, match rate by market, concentration of both sides, both sides coming back, GMV retention by cohort. Documents: adds the monthly GMV by side over 24 months |
| Consumer | Adds DAU/MAU, flattening cohorts and organic share to block B; removes the ACV by segment and the sales cycle; ARR (B1) drops to weight 1. Documents: drops the CRM export and the top 10 contracts, adds the product analytics export over 12 months |
| E-commerce | Adds contribution margin per order and CAC by channel with payback to block C, 60-day repeat rate by cohort to block D; removes the generic CAC and the sales cycle. Documents: drops the CRM export and the top 10 contracts, adds the orders export over 24 months |
| Hardware | Adds margin by volume (1,000 / 10,000 / 100,000 units), bill of materials and MOQs to block C; doubles the weight of unit economics. Documents: adds the bill of materials and supplier terms |
| Fintech | Adds a block Q, weight 2: licence or agreement, cost of compliance, credit or fraud risk. Documents: adds the licence or regulator correspondence and the risk book over 24 months |
| Biotech | Traction and net retention to weight 0, unit economics to 1; removes the sales cycle; adds a block R, weight 3: milestones, IP, regulatory path. Documents: drops the cohorts, the CRM export and the top 10 contracts, adds the clinical data package and the patent schedule |

`scripts/render_grid.py <stage> <model>` writes the effective grid, model block applied and
benchmarks listed, as one markdown document.

---

## The computation

Same as seed: points times the block weight, percentage per block, weighted mean. A block of
weight 0 is for information: it never counts in the global and is never red.

| Block | Weight | Approximate share of the score |
|---|---|---|
| A. Problem and customer | 2 | 12 % |
| B. Traction | 2 | 12 % |
| C. Unit economics | 3 | 18 % |
| D. Net retention | 3 | 18 % |
| E. Market and competition | 2 | 12 % |
| F. Team | 2 | 12 % |
| G. Money and next step | 2 | 12 % |
| H. References | 1 | 6 % |

Unit economics and net retention make 35 % of the score. At seed, traction and economics made
40 %. The shares move with the model block.

Implementation rules, fixed with the grid:

- C3 counts with weight 0 when the profile says B2C.
- A question marked *proof* whose value is found without a proven or confirmed claim cited is
  capped at partial by `apply_proof_cap.py`. An answer citing a claim left to probe is lowered
  one step.
- A block is **red** when its completeness is below 50 % and its weight is above 0.
- **Confirmation passes**, as at seed: between 65 % and 80 % inclusive, three independent
  checker passes and the median per question.

### Gap thresholds

Those of seed: minor at 25 %, to probe up to a factor of 2, blatant above. Ratio =
|deck − found| / max(|found|, 1). A non-numeric contradiction (a named customer that does not
exist, a key hire not on LinkedIn) is blatant by default and goes to the review like the others.

### Documents gate

The list is fixed and lives in the grid file. No coverage threshold.

| Document | Must contain | Minimum |
|---|---|---|
| `pnl_24m` Monthly P&L | Revenue, cost of revenue, operating expenses and net burn, month by month | 24 months |
| `cohorts_12m` Cohorts | Revenue and logo retention by monthly acquisition cohort | 12 months |
| `crm_pipeline` CRM export | Every deal with its stage, probability, amount, owner, first contact and signature dates | weighted pipeline |
| `cap_table` Cap table | Every holder with its share, the option pool, the past rounds | |
| `model_3y` Financial model | Revenue, expenses, cash and hires, month by month | 36 months |
| `top10_contracts` Top 10 contracts | The signed contract of each of the ten largest customers by ARR | 10 contracts |

A document missing, or covering fewer months than the minimum, stops the reading with the email
draft. The classification of each annex is made by an agent with a verbatim quote, checked by
code; the decision is the code's.

### Web rule

At least 2 sources on distinct domains, after searching both for and against. Two domains of
the same owner count as one. Silence is unverifiable, not contradicted. Web-checked at series A:
named customers, competitors, founders, past funding (with the press of previous rounds),
"why now", market bases, key hires (LinkedIn), open job posts, public reviews. Revenue, NRR and
pipeline are never "checked on the web".

---

## What the tool outputs

- **Eight bars** of completeness, one per block, and the global.
- **Per question**: the value, the page, the verbatim quote, the claims cited, whether the
  value was capped or lowered, and the benchmark for the model and stage next to it.
- **The reading**: the three main gaps, the questions for the call, what the deck does not say,
  what did not hold up.
- **Gaps to probe**: each claim left to probe, with both sides and the reviewer's explanation.
- **The documents to request**: the list of the stage and model, document by document, with the email draft.
  This replaces the seed leftovers email. The tool writes the draft; the user sends it, or not.
- **The claims table**: every statement, its status, what backs it, and the benchmark next to
  each figure, with source and date.

What it does not output: a rating of the company, a verdict, a threshold, a valuation.

---

## Guardrails

Those of seed, without exception, plus:

- A benchmark is an order of magnitude displayed next to the deck figure, never a criterion of
  the grid. It lives in its own file, per model and stage, with its value, source and date. A
  benchmark without a dated source stays empty.
- The document list is the same for every series A deck of one business model: the base list
  of this grid, adjusted by the model block (`skills/deck-reader/grids/models/<model>.md`,
  "Series A: documents"). The tool does not adapt it to the deck, does not shorten it, does not
  ask for more.

---

## Where the grid comes from

- **Y Combinator's Series A guide** (February 2020, announced on
  [Hacker News](https://news.ycombinator.com/item?id=22424854), guide at
  `blog.ycombinator.com/ycs-series-a-guide/`), which states that there are no cut-and-dry
  revenue or traction requirements for a series A, and its
  [Series A diligence checklist](https://www.ycombinator.com/library/3h-series-a-diligence-checklist),
  which inspires the fixed document list. No numeric benchmark is taken from it.
- **Point Nine's open-source deal memo**
  ([Medium, 2017-11-06](https://medium.com/point-nine-news/what-do-we-base-our-investment-decisions-on-open-source-deal-memo-template-2b50ee82324)):
  nine sections, with traction read through cohorts and pipeline, acquisition with its costs,
  and reference calls. Source of the pipeline question (C5) and of block H.
- **Bessemer's LifeLock memo** ([bvp.com/memos/lifelock](https://www.bvp.com/memos/lifelock),
  2006-09-25, a 4.5M USD series A): monthly churn, CAC channel by channel and conversion rates
  read figure by figure. The model for CAC by channel (C2) and churn reasons (D2).
- **CRV's series A metrics**
  ([Series A Metrics VCs Expect in 2026](https://www.crv.com/content/series-a-metrics-vcs-expect), 2026-03-31;
  [Startup KPIs VCs Track](https://www.crv.com/content/key-performance-indicators), 2026-07-16;
  [SaaS Churn Rate Benchmarks](https://www.crv.com/content/saas-churn-rate), 2026-06-19):
  ARR, NRR, GRR, burn multiple, CAC payback, customer concentration. The main source of the
  SaaS series A benchmarks.
- **a16z's 16 startup metrics** ([2015-08-21](https://a16z.com/16-startup-metrics/)) for the
  definitions: bookings against revenue, ARR, gross against net churn, paid against blended
  CAC, net burn. And [a16z Growth's guide to growth metrics](https://a16z.com/introducing-a16z-growths-guide-to-growth-metrics/)
  (2022-12-14) for NDR, GDR, magic number and burn multiple.
- **The burn multiple** ([David Sacks, 2020-04-23](https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200)):
  net burn over net new ARR, and its bands.
- **Bessemer's Efficiency Score** ([State of the Cloud 2019](https://www.bvp.com/atlas/state-of-the-cloud-2019),
  2019-02-06): net new ARR over net burn, good, better, best under 30M USD ARR. And
  [Scaling to $100 Million](https://www.bvp.com/atlas/scaling-to-100-million) (2021-09-21) for
  growth, net retention, gross margin and CAC payback by ARR bucket.
- **Initialized** ([The Metrics You Need To Raise a Series A](https://blog.initialized.com/2021/06/the-metrics-you-need-to-raise-a-series-a/),
  2021-06-29) for the benchmarks by model: SaaS, D2C, marketplace.

None of these sources reads the deck, cites the page, or checks that a VP Sales exists. That is
what the tool does.

---

## Revisions

| Date | Change | Triggered by |
|---|---|---|
| 2026-09-13 | First version: series A grid, fixed document list, new claim types, wider web check, benchmarks per model and stage, model blocks in three verbs | Research on existing series A grids |
| 2026-09-14 | The document list becomes the one of the stage and the model: the model blocks gain a fourth verb, documents (remove, add), and the gate reads the effective grid (`documents_gate.py --profile`). Grid unchanged | A consumer app has no CRM pipeline, a biotech no cohorts, a hardware company a BOM to show |

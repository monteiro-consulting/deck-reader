# The series B grid

**Grid version: 2026-09-14. Stage covered: series B only.**

This file is a fixed copy of the grid. It does not change at run time. The machine-readable
version used by the scripts is `scripts/grids/series_b.json`; both must stay identical.

**A deck is scored according to its stage.** Same engine as the pre-seed, seed and series A
grids, another question. Pre-seed asks "what does the deck not say?". Seed asks "does what the
deck says hold up?". Series A asks "does the machine repeat?". Series B asks "**does the machine
hold at scale, without the founders?**": does a second engine (a segment, a geography, a product
or a channel opened after the series A) reproduce the economics of the first, does a sales team
hired in the last twelve months carry the number, does the company run without a founder in the
room, and does growth get cheaper rather than dearer as it grows?

**What the grid measures**: the completeness of the deck, and whether its statements are backed
by the required documents of the stage and model and by public sources. It does not measure the
quality of the company. No verdict, no threshold, no rating.

---

## What changes from series A

| | Series A | Series B |
|---|---|---|
| What is judged | Evidence of repetition: the next customer costs the same, brings the same, signs without the founder | Evidence of scale: a second engine reproduces the first, a sales team hired in the year carries the number, the company runs without a founder, growth gets cheaper |
| Input | The deck, plus a required list of documents, per stage and model (six for SaaS) | The deck, plus **a required list of ten documents** for SaaS, over 36 months where series A asked 24: monthly P&L, audited accounts, cohorts by segment, CRM with win/loss, sales roster with quota attainment, cap table, three-year model, top 20 contracts, board pack, org chart. The model block adjusts the list |
| First gate | A missing document stops the reading | Same mechanism. **Audited accounts and the sales roster are new** |
| Heaviest blocks | Unit economics, net retention (weight 3) | **Efficient growth, repeatability (weight 3).** Net retention drops to 2 |
| Claims verified | The seed types, plus NRR, pipeline, sales cycle, gross margin, concentration, burn multiple, deals without a founder, key hires | The same, plus: **Rule of 40, magic number, quota attainment, rep ramp, second-engine ARR and economics, executive team, executive departures, headcount and attrition, board, breakeven, figures attributed to audited accounts, win rate, secondary or debt, geographic expansion** |
| Web check | Named customers, competitors, founders, funding, "why now", market, reviews, job posts, press of rounds, announced key hires | The same, plus: **the LinkedIn profile of every executive**, LinkedIn headcount trend and departures, **employee reviews** (Glassdoor or the local equivalent), job posts by country against the geographic plan, company registries for announced subsidiaries, the press of every previous round |
| Extra output | The list of documents to request, benchmarks next to every figure | The same. **The second engine's economics side by side with the first's** |

---

## The series B principle

There are three years of figures, a sales team, an executive team, a board. Whether the machine
repeats is no longer the question. The question is whether it holds at scale and without the
founders: a second engine with the same economics as the first, reps hired this year who make
quota, deals that close with no founder on the call, and a burn multiple that falls as ARR rises.

Red signals of the stage:

- Growth bought with a rising burn multiple
- A second segment or geography announced without its own unit economics
- No quota attainment, or every rep under quota
- An executive on a slide who is not on LinkedIn, or who left within the year
- No audited or reviewed accounts
- A document of the list missing

---

## How the series B reading works

1. **Read.** The PDF page by page; the annexes read separately (`annex_text.py`).
2. **Profile.** Sector, model type (SaaS, marketplace, consumer, e-commerce, hardware, fintech,
   biotech), B2B or B2C, announced stage. The stage picks the grid, the model picks the model
   block. No model detected means SaaS. No grid for the stage, the tool stops and says so.
3. **Documents, first gate.** The code builds the required list: the base list of the stage,
   written for SaaS, adjusted by the model block with `remove` and `add`
   (`documents_gate.py required --grid series_b --profile`). An agent sorts each annex into one
   of the expected documents, with a quote that proves it and the number of months covered
   (`annex-classifier`); the code checks the quote, then compares with the list
   (`documents_gate.py documents`):
   - a document missing, or covering fewer months than required: stop, email draft document by
     document, no claims, no web, no grid;
   - every document present: continue.
4. **Claims.** Every verifiable statement of the deck, one line each with page and quote
   (`claim-extractor`, checked by `check_claims.py`). The seed and series A types plus the series
   B ones: Rule of 40, magic number, quota attainment, rep ramp, second-engine ARR and economics,
   executive team, executive departures, headcount and attrition, board, breakeven, figures
   attributed to audited accounts, win rate, secondary or debt, geographic expansion.
5. **Proof in the documents.** Each claim looked up in the required documents (`annex-matcher`,
   checked and classified by `verify_matches.py`). A figure the deck attributes to the audited
   accounts is looked up in the audited accounts, not in the P&L. Same gap thresholds as seed.
   What is not covered is listed in the report; it never stops the reading.
6. **Web check**, only now, and only on what a document cannot settle: the series A scope, plus
   the LinkedIn profile of every executive, the LinkedIn headcount trend and the departures,
   employee reviews, job posts by country, company registries for announced subsidiaries, and
   the press of every previous round (`web-verifier`, rules enforced by `verify_web.py`).
   Searched both for and against; at least two independent domains to conclude; otherwise
   unverifiable. An ARR is never checked on the internet.
7. **Double check.** As at seed: every blatant contradiction goes to an independent reviewer
   whose only job is to find an honest explanation (`contradiction-reviewer`). Without one, the
   second gate stops the reading and shows the sources on both sides.
8. **Grid**, on the deck and the proofs. A figure without a proven or confirmed claim behind it
   is capped at partial by code (`apply_proof_cap.py`); an answer citing a gap to probe is
   lowered one step.
9. **Report.** Nine bars, the reading, the gaps to probe, the documents still to request with
   the email draft, the claims table with the benchmark next to each figure, the two engines side
   by side, question by question.

The score is computed by the code. The model never sees it. The tool never sends the email.

---

## The scale

Found 2, partial 1, absent 0, each with the deck page and the verbatim quote. Same scale as
pre-seed, seed and series A. Same rule as seed: a question marked *proof* cannot be found from
the deck alone.

---

## Blocks and questions

"Proof expected" is the document, among the required list, that backs the answer.

### Block A. Problem and customer, weight 1

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| A1 | Which segments are served, and do the last twenty customers match them? | A nameable profile (size, role, sector) per segment, and the last twenty signed contracts fit one of them | Top 20 contracts | *proof*. A customer that fits no segment is a question for the call |
| A2 | Why do they buy, and why do they renew, per segment, in their own words? | A purchase quote and a renewal quote per segment, or a documented use case with both | The deck suffices | One segment quoted for all = partial |
| A3 | What was tried and dropped since the series A? | A segment, geography, product or channel abandoned since the series A round, dated, with what triggered it | The deck suffices | Nothing dropped in two years = partial at best |

### Block B. Traction, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| B1 | ARR today, and the monthly curve over 36 months? | An ARR and the monthly points over 36 months, matching the P&L and the audited accounts | Monthly P&L, audited accounts | *proof*. A growth percentage without its starting point = absent |
| B2 | How many paying customers, and the average contract value by segment? | A customer count and an ACV per segment, backed by the contracts or the P&L | Contracts, P&L | *proof* |
| B3 | Year-over-year growth for each of the last two years, with the starting points? | Three dated ARR points twelve months apart and the two ratios | Monthly P&L | *proof*. Benchmark shown next to the figure, never in the score |
| B4 | Do the named customers exist, pay, and use the product? | Confirmed outside the deck: a contract in the annexes, and a website, LinkedIn page or public review | Contracts, web | *proof*. **Still the central question.** Absent = red |
| B5 | How much of ARR do the top twenty customers make? | A share of ARR for the top twenty, confirmed against the contracts or the P&L | Contracts, P&L | *proof*. A single customer above 20 % of ARR is a question for the call, not a verdict |
| B6 | New ARR by channel and by segment? | Each channel and each segment with its share of new ARR over twelve months, from the CRM export | CRM export | *proof*. All from one channel = partial |

### Block C. Efficient growth, weight 3

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| C1 | Gross margin, confirmed against the audited accounts? | A gross margin with what is included in cost of revenue, and the same figure in the audited accounts | Audited accounts, P&L | *proof*. A margin that excludes hosting, support or implementation = partial |
| C2 | CAC payback by channel and by segment, and its trend over 24 months? | A payback in months per channel and per segment, with the method, and its curve over 24 months | CRM export, P&L | *proof*. A single blended figure = partial |
| C3 | Burn multiple over the last twelve months, and over the twelve before? | Net burn divided by net new ARR for both windows, from the P&L, and the direction of the change | Monthly P&L | *proof*. **A multiple that rises with ARR is a red signal of the stage.** Benchmark shown next to the figure (Sacks, Bessemer), never in the score |
| C4 | Rule of 40? | Revenue growth plus operating margin over the last twelve months, both from the P&L | Monthly P&L | *proof*. Benchmark shown next to the figure, never in the score |
| C5 | Sales efficiency: magic number? | Net new ARR of the quarter over the previous quarter's sales and marketing spend, over the last four quarters | Monthly P&L | *proof*. B2B only. Weight 0 in B2C |
| C6 | Weighted pipeline coverage of next year's plan, by segment? | A pipeline by stage with probabilities, its weighted total per segment, and the ratio to the plan of each segment | CRM export, financial model | *proof*. B2B only. Weight 0 in B2C. An unweighted pipeline = partial |
| C7 | The breakeven month in the model, and the cash needed to reach it? | A month where net burn turns positive in the three-year model, with the cumulative cash to get there, or the explicit statement that none is planned | Financial model | *proof*. A model with no breakeven and no statement = absent |

### Block D. Repeatability, weight 3

The block that separates series B from series A.

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| D1 | What is the second engine, and what does it weigh? | A segment, geography, product or channel opened after the series A, named, with its own ARR and its start date, in the P&L by segment | Monthly P&L, CRM export | *proof*. No engine opened since the series A = absent |
| D2 | Do its unit economics match the first engine's? | CAC payback, gross margin and NRR of the second engine next to the same three of the first, from the same documents | Cohorts by segment, P&L, CRM export | *proof*. **A second engine without its own economics = partial at best.** Shown side by side in the report |
| D3 | What share of new ARR comes from engines opened after the series A? | The share of net new ARR over the last twelve months that comes from those engines, from the CRM | CRM export, P&L | *proof* |
| D4 | Quota attainment? | The share of reps at or above quota, by quarter, over twelve months | Sales roster | *proof*. B2B only. Weight 0 in B2C. **Absent = red.** Every rep under quota is a question for the call |
| D5 | Ramp time of a rep hired in the last twelve months? | The months from start date to full quota for the reps hired in the year, from the roster, and how many are ramped | Sales roster | *proof*. B2B only. Weight 0 in B2C. No rep hired in the year = partial |
| D6 | What share of deals closed without a founder, and by reps hired in the year? | The share of signed deals whose owner in the CRM is not a founder, and the share owned by reps whose start date is within twelve months | CRM export, sales roster | *proof*. B2B only. Weight 0 in B2C. **Absent = red** |

### Block E. Net retention, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| E1 | Net revenue retention over twelve months, by segment? | An NRR per segment over a twelve-month window with the definition used, recomputable from the cohorts | Cohorts by segment | *proof*. Benchmark shown next to the figure, never in the score |
| E2 | Gross retention and logo churn, with the reasons? | A gross revenue retention and a logo churn figure, and a reason per lost customer | Cohorts, CRM win/loss | *proof*. Absent = the deck hides churn. Red |
| E3 | Do the cohorts flatten at 24 months, in each segment? | Cohort curves of at least 24 months per segment, with the month where they flatten | Cohorts by segment | *proof*. A segment whose cohorts do not flatten is a question for the call |
| E4 | Expansion: what share of new ARR comes from existing customers, and why? | A share of net new ARR from expansion, with the trigger (seats, modules, price, second product) | Cohorts, contracts | *proof* |

### Block F. Market and competition, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| F1 | Market size computed bottom-up with the ACV by segment, and the share already taken? | Possible customers per segment multiplied by the ACV signed in that segment, with visible assumptions, and the current ARR as a share of it | The deck, assumptions visible | An analyst figure = absent |
| F2 | Who are the competitors, and what is the win rate against each? | Named competitors, and a win rate against each from the CRM win/loss | CRM win/loss, web | *proof*. Web check: omitted competitors become a contradiction |
| F3 | Why now, and why still? | A recent, named, verifiable change, why the window is still open two years after the series A, and what a well-funded entrant would need | Web | |

### Block G. Leadership and organisation, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| G1 | Does the executive team exist? | CFO, CRO or VP Sales, CTO or VP Engineering, CPO: each named in the deck and found on LinkedIn with that role at the company | Org chart, web: LinkedIn | *proof*. An executive on a slide who is not on LinkedIn is a contradiction. **Absent = red** |
| G2 | Which executives left in the last 24 months, and why? | Each departure from the executive team with its date and a reason, matching the org chart and LinkedIn | Org chart, web: LinkedIn | *proof*. A departure found on LinkedIn and not in the deck is a contradiction |
| G3 | Headcount by function over 24 months, and regretted attrition? | Headcount per function month by month, matching the P&L by function, and the share of departures the company did not want | Org chart, P&L | *proof*. Headcount that does not match the P&L is a gap to probe |
| G4 | The board: members, independents, cadence? | The board members with their affiliation, the independent seats, and the meeting dates of the last four quarters | Board pack | *proof* |
| G5 | Do the open job posts match the hiring plan, by function and by country? | Public job posts that correspond to the hiring plan of the round, function by function and country by country | Financial model, web: careers page, LinkedIn jobs | *proof*. A country in the plan with no post: a question for the call |
| G6 | Who owns what? | Founders, investors, employees, option pool and what is left to grant, from the cap table | Cap table | *proof* |

### Block H. Money and next step, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| H1 | How much is asked, and what for, by function and by engine? | An amount and a breakdown by function and by engine (segment, geography, product, channel) | The deck suffices | |
| H2 | What figures must be reached for the series C, or for profitability? | A measurable, dated goal: ARR, NRR, burn multiple, or the breakeven month | The deck suffices | Absent = the money has no purpose. Red |
| H3 | Runway and burn on the three-year model, with the breakeven if planned? | Monthly burn, cash and months of runway, consistent with the financial model, and the breakeven month if there is one | Financial model, P&L | *proof* |
| H4 | Previous rounds, investors, follow-on, and any secondary or venture debt? | Amounts and investors for each round, in the cap table and the press, whether existing investors follow on, and any secondary sale or debt with its terms | Cap table, web: press | *proof*. A secondary or a debt line absent from the deck and present in the cap table is a contradiction |

### Block I. References, weight 1

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| I1 | Customers we can call, including one that left and one in the second engine? | Names and a way to contact them, including at least one lost customer and one customer of the second engine | The deck suffices | |
| I2 | Executives, board members, and one executive who left, we can call? | Same | The deck suffices | Asked to prepare the call, not to judge the deck |

---

## The business-model block

The profile detects the model; no model detected means SaaS. The model block lives in its own
file (`scripts/grids/models/<model>.json`, readable copy in `grids/models/<model>.md`) and is
applied to this grid by `grid_lib.effective_grid` in four verbs, in this order: **remove**
questions of the stage grid (by id), **reweight** blocks or questions, **add** questions to a
block with the block weight, or in a block the model brings, **documents** to adjust the
required document list of the first gate (remove by id, add entries of the same shape). One
block per business model, never one grid per sector. The deck never adjusts the list.

| Model | What the block does to the series B grid | What it does to the document list |
|---|---|---|
| SaaS (default) | Nothing. The grid is written for it. Benchmarks only | Nothing. The base list is written for it |
| Marketplace | Adds M1 to M4 to block B: GMV and take rate over 36 months, both sides coming back, concentration of the top twenty sellers and buyers, GMV retention by cohort and by side | Adds `gmv_36m`: monthly GMV, take rate, active supply and demand, 36 months |
| Consumer | Adds N1 to N3 to block B: DAU over MAU, flattening cohorts (day 7 to day 30), organic share. Removes the ACV by segment (B2), the magic number (C5), the pipeline (C6) and the sales-team questions (D4, D5, D6). Lowers the ARR weight (B1) to 1 | Removes `crm_pipeline`, `sales_roster`, `top20_contracts`. Adds `product_analytics_24m`: MAU, DAU over MAU, retention cohorts, organic share, 24 months |
| E-commerce | Adds O1 and O2 to block C: contribution margin per order after shipping and returns, CAC by channel (paid and blended) with payback. Adds O3 to block E: 60-day repeat rate. Removes the magic number (C5), the pipeline (C6) and the sales-team questions (D4, D5, D6) | Removes `crm_pipeline`, `sales_roster`, `top20_contracts`. Adds `orders_export_36m`: orders with revenue, cost of goods, shipping, returns, marketing by channel, 36 months |
| Hardware | Adds P1 to P3 to block C: margin by volume (1,000, 10,000, 100,000 units) and realized in the audited accounts, bill of materials (BOM) with unit cost and its 36-month curve, minimum order quantities (MOQ), inventory and warranty. Doubles the weight of efficient growth (C to 6) | Adds `bom_and_suppliers`: BOM with unit cost, supplier contracts with MOQ and terms. Adds `inventory_24m`: inventory, warranty claims and returns by month, 24 months |
| Fintech | Adds a block Q, weight 2: licence or agreement (Q1), cost of compliance (Q2), credit or fraud risk (Q3), losses on the book over 36 months (Q4) | Adds `licence`: licence or agreement or regulator correspondence, compliance cost lines. Adds `risk_book_36m`: loan, transaction or policy book with losses, defaults, fraud, chargebacks, 36 months |
| Biotech | Traction (B), repeatability (D) and net retention (E) to weight 0, efficient growth (C) to 1. Removes the sales-team questions (D4, D5, D6) and the two sales-efficiency questions (C5, C6). Adds a block R, weight 3: preclinical or clinical milestones reached, intellectual property, regulatory path | Removes `cohorts_24m`, `crm_pipeline`, `sales_roster`, `top20_contracts`. Adds `clinical_dossier`: protocols, results, regulator correspondence per milestone. Adds `ip_schedule`: patent filings, status, jurisdictions, ownership |

`scripts/render_grid.py series_b <model>` writes the effective grid, model block applied and
benchmarks listed, as one markdown document.

---

## The computation

Same as seed: points times the block weight, percentage per block, weighted mean. A block of
weight 0 is asked for information: it never counts in the global and is never red.

| Block | Weight | Approximate share of the score |
|---|---|---|
| A. Problem and customer | 1 | 6 % |
| B. Traction | 2 | 11 % |
| C. Efficient growth | 3 | 17 % |
| D. Repeatability | 3 | 17 % |
| E. Net retention | 2 | 11 % |
| F. Market and competition | 2 | 11 % |
| G. Leadership and organisation | 2 | 11 % |
| H. Money and next step | 2 | 11 % |
| I. References | 1 | 6 % |

Efficient growth and repeatability make 33 % of the score. At series A, unit economics and net
retention made 35 %. The shares move with the model block.

Implementation rules, fixed with the grid:

- C5, C6, D4, D5 and D6 count with weight 0 when the profile says B2C. A question at weight 0
  is asked for information: it never raises a red signal (`score.py`), so a B2C deck's red
  signals are B4, E2, G1 and H2.
- A question marked *proof* whose value is found without a proven or confirmed claim cited is
  capped at partial by `apply_proof_cap.py`. An answer citing a claim left to probe is lowered
  one step.
- A block is **red** when its completeness is below 50 % and its weight is above 0.
- **Confirmation passes**, as at seed: between 65 % and 80 % inclusive, three independent
  checker passes and the median per question.

### Gap thresholds

Those of seed: minor at 25 %, to probe up to a factor of 2, blatant above. Ratio =
|deck − found| / max(|found|, 1). A non-numeric contradiction (a named customer that does not
exist, an executive not on LinkedIn) is blatant by default and goes to the review like the others.

### Documents gate

The list is per stage and model, no coverage threshold. The base list below is written for
SaaS; the model block adjusts it with `remove` and `add`, as in the table above. The minimum
number of months lives in the grid file, readable, corrected at each post-mortem.

| id | Document | What it must contain | Minimum |
|---|---|---|---|
| `pnl_36m` | Monthly P&L | Revenue, cost of revenue, operating expenses by function (sales and marketing, R&D, G&A), net burn, month by month | 36 months |
| `accounts_audited` | Audited or reviewed annual accounts | Balance sheet, income statement and the auditor's or reviewer's report, for each of the last two fiscal years | 2 years |
| `cohorts_24m` | Cohorts by segment | Revenue and logo retention by monthly acquisition cohort, split by segment | 24 months |
| `crm_pipeline` | CRM export with weighted pipeline and win/loss | Every deal with stage, probability, amount, owner, segment, first contact and signature dates; lost deals with the reason and the competitor | weighted pipeline |
| `sales_roster` | Sales team roster with quota attainment | Each rep with start date, quota, attainment by quarter, and departures | 12 months |
| `cap_table` | Cap table | Every holder with its share, the option pool and what is left to grant, the past rounds | |
| `model_3y` | Three-year financial model | Revenue by segment, expenses by function, cash, hires, month by month, and the breakeven month if planned | 3 years |
| `top20_contracts` | Contracts of the top 20 customers | The signed contract of each of the twenty largest customers by ARR | 20 contracts |
| `board_pack_4q` | Board decks or minutes | The board deck or the minutes of each of the last four quarters | 4 quarters |
| `org_chart` | Org chart and headcount history | Headcount by function month by month, start and end dates, and the executive team with start dates | 24 months |

A document missing, or covering fewer months than the minimum, stops the reading with the email
draft. The classification of each annex is made by an agent with a verbatim quote, checked by
code; the decision is the code's.

### Web rule

At least 2 sources on distinct domains, after searching both for and against. Two domains of
the same owner count as one. Silence is unverifiable, not contradicted. Web-checked at series B:
named customers, competitors, founders, past funding (with the press of every previous round),
"why now", market bases, key hires and every executive (LinkedIn), executive departures,
headcount trend, open job posts by function and by country, public reviews, employee reviews
(Glassdoor or the local equivalent), secondary or debt (press), announced subsidiaries
(registries). Revenue, NRR, pipeline, quota attainment and burn multiple are never "checked on
the web".

---

## What the tool outputs

- **Nine bars** of completeness, one per block, and the global.
- **Per question**: the value, the page, the verbatim quote, the claims cited, whether the
  value was capped or lowered, and the benchmark for the model and stage next to it, with source
  and date.
- **The claims**: each one proven, confirmed, not covered, unverifiable, to probe or
  contradicted, with the source, and the benchmark next to each figure.
- **The two engines side by side**: CAC payback, gross margin, NRR of the first engine and of
  the second, each with its document. Empty cells stay empty.
- **The contradictions**: the gaps to probe, with both sides and the explanation found at review.
- **The documents to request**: the list of the stage and model, document by document, with the
  email draft. The tool writes the draft; the user sends it, or not.
- **The questions for the call**: every absent or partial question of a weight-3 block, plus
  every contradiction.

What it does not output: a rating of the company, a verdict, a threshold, a valuation.

---

## Guardrails

Those of seed, without exception, plus two:

- A benchmark is an order of magnitude displayed next to the deck figure, never a criterion of
  the grid. It lives in its own file, per model and per stage
  (`scripts/grids/benchmarks/<model>.json`, `stages.series_b`), with its value, its source and
  its date. A benchmark without a dated source stays empty.
- The document list is the same for every deck of the same stage and business model. The model
  block adjusts it, in the model's own file (`skills/deck-reader/grids/models/<model>.md`,
  "Series B: documents"); the tool never adapts it to a deck, never shortens it, never asks for
  more.

---

## Benchmarks

Shown next to the figures, never scored. SaaS at series B: ARR growth, net retention, gross
margin and free cash flow margin by ARR bucket, 10 to 25, 25 to 50 and 50 to 100M USD
(Bessemer, Scaling to $100 Million, 2021-09-21); CAC payback around 20 months for private SaaS
(CRV, 2026-07-16; Bessemer gives no figure above 10M USD ARR); Rule of 40 as growth plus profit
(Brad Feld, 2015-02-03) and as ARR growth plus FCF margin (ICONIQ, 2025); magic number above 1x
compelling, under 0.5x a model not yet found (Scale VP, 2010-04-20), 0.7x long-term median
(Scale VP, 2020-09-11), net magic number above 1.0x in the top quartile (ICONIQ, 2025); net
dollar retention settling at 110 to 120 % (ICONIQ, 2025) and public SaaS at 110 % (High Alpha,
2024); burn multiple bands and trajectory (Sacks, 2020-04-23); efficiency score under 30M USD
ARR (Bessemer, 2019-02-06). a16z Growth's guide (2022-12-14) names the metric set without a
figure on the page. Quota attainment, rep ramp, win rate and the series B round size: no dated
source, left empty.

---

## Where the grid comes from

- **Bessemer's Scaling to $100 Million** ([bvp.com/atlas/scaling-to-100-million](https://www.bvp.com/atlas/scaling-to-100-million),
  2021-09-21): growth, net retention, gross margin and CAC payback by ARR bucket. The main source
  of the SaaS series B benchmarks, and the reason B3 asks for two years of growth rather than one.
- **The burn multiple** ([David Sacks, 2020-04-23](https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200)):
  net burn over net new ARR, its bands, and the expectation that it improves after each round.
  C3 asks for it twice, twelve months apart, for that reason.
- **Bessemer's Efficiency Score** ([State of the Cloud 2019](https://www.bvp.com/atlas/state-of-the-cloud-2019),
  2019-02-06): net new ARR over net burn, best band above 1.5x under 30M USD ARR. Shown next to
  C3 as the inverse reading of the same figures.
- **The Rule of 40** ([Brad Feld, 2015-02-03](https://feld.com/archives/2015/02/rule-40-healthy-saas-company/)):
  growth rate plus profit margin should add up to 40 %. The definition used in C4.
- **The magic number** (Scale Venture Partners, [Magic Number Math](https://www.scalevp.com/insights/magic-number-math/),
  Rory O'Driscoll, 2010-04-20, and [A History of the Magic Number](https://www.scalevp.com/blog/saas-metrics-a-history-of-the-magic-number),
  Dale Chang, 2020-09-11): the definition and the benchmark of C5.
- **a16z Growth's guide to growth metrics** ([a16z.com](https://a16z.com/introducing-a16z-growths-guide-to-growth-metrics/),
  2022-12-14): ARR growth, Rule of 40, gross margin, free cash flow margin and CAC payback as the
  growth-stage set. The reason block C reads growth and margin together rather than growth alone.
- **The 2024 SaaS Benchmarks Report** (High Alpha, continuing OpenView,
  [highalpha.com/saas-benchmarks/2024](https://www.highalpha.com/saas-benchmarks/2024), 2024
  edition, over 800 companies): net dollar retention at 110 %, growth by ARR bucket. It gives no
  quota attainment or rep ramp figure; those benchmarks stay empty.
- **ICONIQ Growth's State of Software 2025** ([iconiq.com](https://www.iconiq.com/growth/reports/2025-state-of-software))
  and its [Enterprise Five](https://www.iconiq.com/growth/reports/the-iconiq-enterprise-five):
  the net magic number, net dollar retention at 110 to 120 %, Rule of 40 as growth plus free
  cash flow margin. The net variant of C5, and the NRR order of magnitude of E1.

None of them reads the deck, cites the page, or checks that a CFO exists. That is what the tool
does.

---

## Revisions

| Date | Change | Triggered by |
|---|---|---|
| 2026-09-14 | First version: series B grid, document list per stage and model (ten documents for SaaS), repeatability block, executive team and organisation checks, new claim types, wider web check, series B benchmarks | Series B grid; the model block now adjusts the document list |

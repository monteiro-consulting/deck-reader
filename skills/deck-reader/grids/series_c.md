# The series C grid

**Grid version: 2026-09-14. Stage covered: series C and every later round (series D, growth rounds).**

This file is a fixed copy of the grid. It does not change at run time. The machine-readable
version used by the scripts is `scripts/grids/series_c.json`; both must stay identical.

**A deck is scored according to its stage.** Same engine as the pre-seed, seed, series A and
series B grids, another question. Pre-seed asks "what does the deck not say?". Seed asks "does
what the deck says hold up?". Series A asks "does the machine repeat?". Series B asks "does the
machine hold at scale, without the founders?". Series C asks "**does the machine hold without
new money, and keep its place?**": did the company do what its series B deck promised, quarter
after quarter, does it grow with less cash every year and could it grow with none, do its prices
hold against the competitors that raised since, and do the products and the countries added
after the first reproduce its economics?

**What the grid measures**: the completeness of the deck, and whether its statements are backed
by the required documents of the stage and model and by public sources. It does not measure the
quality of the company. No verdict, no threshold, no rating, no valuation.

---

## What changes from series B

| | Series B | Series C |
|---|---|---|
| What is judged | Evidence of scale: a second engine reproduces the first, a sales team hired in the year carries the number, the company runs without a founder, growth gets cheaper | Evidence of durability: **the plan of the series B met quarter after quarter**, growth that holds as burn falls and a model that says what happens at zero burn, prices that hold, a position kept against funded entrants, products and countries after the first with their own economics |
| Central proof | The deck against the documents | **The past of the deck**: the series B deck promised figures (its H2); the board packs of eight quarters give the plan, the P&L gives the actual |
| Input | The deck, plus a required list of ten documents for SaaS, over 36 months | The deck, plus **a required list of eleven documents** for SaaS, over 48 months: monthly P&L by product and geography, audited accounts over three years with the opinion, cohorts by segment and acquisition year, CRM with win/loss, sales roster, **billing export with list and net price**, **cap table with the terms of every round and debt**, three-year model **with a zero-burn scenario**, top 20 contracts, **board pack of eight quarters with budget vs actual**, org chart. The model block adjusts the list |
| First gate | A missing document stops the reading | Same mechanism. **The billing export and the terms of the rounds are new**; audited accounts go to three years, the board pack to eight quarters |
| Heaviest blocks | Efficient growth, repeatability (weight 3) | **Efficient growth, position and durability (weight 3).** Repeatability gives way to position and durability |
| Claims verified | The series A types, plus Rule of 40, magic number, quota attainment, rep ramp, second engine, executive team and departures, headcount and attrition, board, breakeven, audited figures, win rate, secondary or debt, expansion | The same, plus: **plan vs actual, net price, discount rate, free cash flow margin, zero-burn growth, product share, geographic share, liquidation preference, debt terms, audit opinion, controls certification, competitor funding, exit comparables** |
| Web check | The series A scope, plus every executive on LinkedIn, headcount trend and departures, employee reviews, job posts by country, registries for subsidiaries, press of every round | The same, plus: **the accounts filed at the company registry** (Infogreffe, Companies House, Handelsregister...) against the audited accounts, **the pricing page history on the Wayback Machine**, the trend of G2 and Capterra reviews over 24 months, litigation and security incidents made public, **the rounds raised by competitors since the series B**, listed comparables for the benchmarks |
| Extra output | The two engines side by side | The same, plus **the plan vs actual table, quarter by quarter**: ARR, net new ARR, net burn, headcount; plan from the board pack, actual from the P&L, gap in percent |

---

## The series C principle

There are four years of figures, audited accounts, a board that has approved budgets for two
years. What the company says it will do is no longer the question: the board packs say what it
said and the P&L says what it did. The question is whether the machine holds without the next
round, whether it keeps its prices and its win rate as funded entrants arrive, and whether what
was added after the first product and the first country pays for itself.

Red signals of the stage:

- Growth that slows faster than burn falls
- A plan missed two years in a row
- Discounts that rise
- Older cohorts below younger ones
- A participating preference or a ratchet absent from the deck and present in the terms
- Audited accounts with a qualified opinion
- A document of the list missing

---

## How the series C reading works

1. **Read.** The PDF page by page; the annexes read separately (`annex_text.py`).
2. **Profile.** Sector, model type (SaaS, marketplace, consumer, e-commerce, hardware, fintech,
   biotech), B2B or B2C, announced stage. The stage picks the grid: "series C", "série C",
   "series D", "growth round" and every later round route to this grid (`series-c-or-later`).
   The model picks the model block. No model detected means SaaS.
3. **Documents, first gate.** The code builds the required list: the base list of the stage,
   written for SaaS, adjusted by the model block with `remove` and `add`
   (`documents_gate.py required --grid series_c --profile`). An agent sorts each annex into one
   of the expected documents, with a quote that proves it and the months or items covered
   (`annex-classifier`); the code checks the quote, then compares with the list
   (`documents_gate.py documents`):
   - a document missing, or covering fewer months or items than required: stop, email draft
     document by document, no claims, no web, no grid;
   - every document present: continue.
4. **Claims.** Every verifiable statement of the deck, one line each with page and quote
   (`claim-extractor`, checked by `check_claims.py`). The series B types plus the series C ones:
   plan vs actual (with its metric and quarter), net price, discount rate, free cash flow
   margin, zero-burn growth, product share, geographic share, liquidation preference, debt
   terms, audit opinion, controls certification, competitor funding, exit comparables.
5. **Proof in the documents.** Each claim looked up in the required documents (`annex-matcher`,
   checked and classified by `verify_matches.py`). **The central proof is the past of the deck**:
   a plan vs actual claim is looked up twice, the plan in the board pack of its quarter, the
   actual in the P&L. A figure the deck attributes to the audited accounts is looked up there;
   an audit opinion is read in the auditor's report; a price in the billing export; a preference
   in the terms. Same gap thresholds as seed. What is not covered is listed in the report; it
   never stops the reading.
6. **Web check**, only now, and only on what a document cannot settle: the series B scope, plus
   the accounts filed at the company registry compared with the audited accounts, the history of
   the pricing page on the Wayback Machine, the trend of public reviews over 24 months,
   litigation and security incidents made public, the rounds raised by competitors since the
   series B, and listed comparables (`web-verifier`, rules enforced by `verify_web.py`). Searched
   both for and against; at least two independent domains to conclude; otherwise unverifiable.
   An ARR is never checked on the internet.
7. **Double check.** As at seed: every blatant contradiction goes to an independent reviewer
   whose only job is to find an honest explanation (`contradiction-reviewer`). Without one, the
   second gate stops the reading and shows the sources on both sides.
8. **Grid**, on the deck and the proofs. A figure without a proven or confirmed claim behind it
   is capped at partial by code (`apply_proof_cap.py`); an answer citing a gap to probe is
   lowered one step.
9. **Report.** Nine bars, the reading, the gaps to probe, the documents still to request with
   the email draft, the claims table with the benchmark next to each figure, **the plan vs
   actual table quarter by quarter** next to the two engines side by side, question by question.

The score is computed by the code. The model never sees it. The tool never sends the email.

---

## The scale

Found 2, partial 1, absent 0, each with the deck page and the verbatim quote. Same scale as
pre-seed, seed, series A and series B. Same rule as seed: a question marked *proof* cannot be
found from the deck alone.

---

## Blocks and questions

"Proof expected" is the document, among the required list, that backs the answer.

### Block A. Problem and customer, weight 1

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| A1 | Which segments are served, and do the last twenty customers match them? | A nameable profile (size, role, sector) per segment, and the last twenty signed contracts fit one of them | Top 20 contracts | *proof*. A customer that fits no segment is a question for the call |
| A2 | Why do they buy, and why do they renew, per segment, in their own words? | A purchase quote and a renewal quote per segment, or a documented use case with both | The deck suffices | One segment quoted for all = partial |
| A3 | What was dropped since the series B? | A segment, geography, product or channel abandoned since the series B round, dated, with what triggered it | The deck suffices | Nothing dropped since the series B = partial at best |

### Block B. Traction, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| B1 | ARR today, and the monthly curve over 48 months? | An ARR and the monthly points over 48 months, matching the P&L and the audited accounts | Monthly P&L, audited accounts | *proof*. A growth percentage without its starting point = absent |
| B2 | How many paying customers, and the average contract value by segment? | A customer count and an ACV per segment, backed by the contracts or the P&L | Contracts, P&L | *proof* |
| B3 | Year-over-year growth for each of the last three years, with the starting points? | Four dated ARR points twelve months apart and the three ratios | Monthly P&L | *proof*. Benchmark shown next to the figure, never in the score |
| B4 | Do the named customers exist, pay, and use the product? | Confirmed outside the deck: a contract in the annexes, and a website, LinkedIn page or public review | Contracts, web | *proof*. **Still the central question.** Absent = red |
| B5 | How much of ARR do the top twenty customers make, and how has that share moved over 24 months? | A share of ARR for the top twenty today and 24 months ago, confirmed against the contracts or the P&L | Contracts, P&L | *proof*. A single customer above 20 % of ARR is a question for the call, not a verdict |
| B6 | New ARR by channel, segment, product and geography? | Each channel, segment, product and geography with its share of new ARR over twelve months, from the CRM export and the P&L | CRM export, P&L by product and geography | *proof*. All from one channel or one product = partial |

### Block C. Efficient growth, weight 3

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| C1 | Gross margin, confirmed against the audited accounts? | A gross margin with what is included in cost of revenue, and the same figure in the audited accounts | Audited accounts, P&L | *proof*. A margin that excludes hosting, support or implementation = partial |
| C2 | CAC payback by channel and by segment, and its trend over 24 months? | A payback in months per channel and per segment, with the method, and its curve over 24 months | CRM export, P&L | *proof*. A single blended figure = partial |
| C3 | Burn multiple over three twelve-month windows? | Net burn divided by net new ARR for each of the last three twelve-month windows, from the P&L, and the direction of the change | Monthly P&L | *proof*. **Growth that slows faster than burn falls is a red signal of the stage.** Benchmark shown next to the figure (Sacks), never in the score |
| C4 | Rule of 40, two years in a row? | Revenue growth plus free cash flow or operating margin for each of the last two fiscal years, from the P&L and the audited accounts | Monthly P&L, audited accounts | *proof*. One year only = partial. Benchmark shown next to the figure, never in the score |
| C5 | Sales efficiency: magic number? | Net new ARR of the quarter over the previous quarter's sales and marketing spend, over the last four quarters | Monthly P&L | *proof*. B2B only. Weight 0 in B2C |
| C6 | Free cash flow margin over 24 months, and its direction? | Free cash flow over revenue, quarter by quarter over 24 months, from the P&L and the cash flow statements of the audited accounts | Monthly P&L, audited accounts | *proof*. A margin without its direction = partial. Benchmark shown next to the figure, never in the score |
| C7 | What growth does the model forecast at zero burn? | A scenario of the three-year model where spending is frozen at the level the cash on hand allows, with the ARR growth it forecasts year by year | Financial model | *proof*. A model without a zero-burn scenario = absent. The scenario is read, never judged |
| C8 | Breakeven: reached, with its date in the accounts, or dated in the model? | The period where net burn turned positive, in the audited accounts or the P&L, or the month where it does in the three-year model with the cumulative cash to get there | Audited accounts, P&L, financial model | *proof*. Neither reached nor dated = absent |

### Block D. Position and durability, weight 3

The block that separates series C from series B. It replaces repeatability.

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| D1 | Plan against actual over eight quarters: the average gap, and how many quarters were missed? | For each of the last eight quarters, the plan of the board pack and the actual of the P&L for ARR, net new ARR, net burn and headcount, the average gap and the number of quarters missed | Board packs, monthly P&L | *proof*. **The central proof of the stage.** **A plan missed two years in a row is a red signal of the stage.** Absent = red. Laid out quarter by quarter in the report |
| D2 | Pricing power: net price against list price per contract, and the trend of discounts over 24 months? | The list price and the net price of each contract, and the average discount month by month over 24 months, from the billing export | Billing export | *proof*. **Discounts that rise are a red signal of the stage** |
| D3 | Win rate against each competitor, and its trend over 24 months? | Deals won and lost against each named competitor, quarter by quarter over 24 months, from the CRM win/loss | CRM win/loss | *proof*. A win rate without its trend = partial |
| D4 | What share of ARR do the products after the first make, and with what economics next to the first? | The ARR of each product after the first as a share of total ARR, with its gross margin and new ARR next to those of the first product, from the P&L by product | P&L by product | *proof*. A second product without its own economics = partial at best |
| D5 | What share of ARR comes from outside the home country, and with what economics? | The ARR outside the home country as a share of total ARR, by country or region, with its gross margin and new ARR, from the P&L by geography | P&L by geography | *proof*. A geography without its own economics = partial at best |
| D6 | What share of deals is signed without a founder, and by reps with more than twelve months in the company? | The share of signed deals whose owner in the CRM is not a founder, and the share owned by reps whose start date is more than twelve months old | CRM export, sales roster | *proof*. B2B only. Weight 0 in B2C. **Absent = red** |

### Block E. Net retention, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| E1 | Net revenue retention by segment and by cohort vintage? | An NRR per segment and per acquisition year over a twelve-month window, with the definition used, recomputable from the cohorts | Cohorts by segment and acquisition year | *proof*. **Older cohorts below younger ones are a red signal of the stage** and a question for the call. Benchmark shown next to the figure, never in the score |
| E2 | Gross retention and logo churn, with the reasons? | A gross revenue retention and a logo churn figure, and a reason per lost customer | Cohorts, CRM win/loss | *proof*. Absent = the deck hides churn. Red |
| E3 | Do the cohorts flatten at 36 months, in each segment? | Cohort curves of at least 36 months per segment, with the month where they flatten | Cohorts by segment | *proof*. A segment whose cohorts do not flatten is a question for the call |
| E4 | Expansion: what share of new ARR comes from existing customers, and what triggers it? | A share of net new ARR from expansion, with the trigger (seats, modules, price, second product) | Cohorts, contracts, P&L by product | *proof* |

### Block F. Market and competition, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| F1 | Market size computed bottom-up with the ACV by segment, and the share already taken? | Possible customers per segment multiplied by the ACV signed in that segment, with visible assumptions, and the current ARR as a share of it | The deck, assumptions visible | An analyst figure = absent |
| F2 | Who are the competitors, and what is the win rate against each? | Named competitors, the same names in the CRM win/loss with a win rate against each | CRM win/loss, web | *proof*. Web check: omitted competitors become a contradiction |
| F3 | Which entrants have raised money since the series B? | The competitors that raised a round since the series B, with the amount and the date, and what the deck says about them | Web: press of competitors' rounds | *proof*. A funded entrant the deck does not name is a contradiction |
| F4 | Why now, and why still? | A recent, named, verifiable change, why the window is still open after the series B, and what a well-funded entrant would need | Web | |

### Block G. Leadership and organisation, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| G1 | Does the executive team exist, and has the CFO already run audited accounts? | CFO, CRO or VP Sales, CTO or VP Engineering, CPO: each named in the deck and found on LinkedIn with that role at the company, and a CFO who has already held audited accounts, here or before | Org chart, web: LinkedIn | *proof*. An executive on a slide who is not on LinkedIn is a contradiction. **Absent = red** |
| G2 | Which executives left in the last 24 months, and why? | Each departure from the executive team with its date and a reason, matching the org chart and LinkedIn | Org chart, web: LinkedIn | *proof*. A departure found on LinkedIn and not in the deck is a contradiction |
| G3 | Headcount by function over 36 months, and regretted attrition? | Headcount per function month by month over 36 months, matching the P&L by function, and the share of departures the company did not want | Org chart, P&L | *proof*. Headcount that does not match the P&L is a gap to probe |
| G4 | The board: members, independents, cadence? | The board members with their affiliation, the independent seats, and the meeting dates of the last eight quarters | Board pack | *proof* |
| G5 | Controls: three fiscal years audited without qualification, and SOC 2 or ISO 27001? | An unqualified auditor's opinion on each of the last three fiscal years, and, for a B2B company, a SOC 2 report or an ISO 27001 certificate with its date and scope | Audited accounts, web: registry, trust page | *proof*. **Accounts with a qualified opinion are a red signal of the stage.** In B2C the certification is not asked: three unqualified opinions = found |
| G6 | Do the open job posts match the hiring plan, by function and by country? | Public job posts that correspond to the hiring plan of the round, function by function and country by country | Financial model, web: careers page, LinkedIn jobs | *proof*. A country in the plan with no post: a question for the call |
| G7 | Who owns what? | Founders, investors, employees, option pool and what is left to grant, from the cap table | Cap table | *proof* |

### Block H. Money and exit, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| H1 | How much is asked, and what for, by function, product and geography? | An amount and a breakdown by function, by product and by geography | The deck suffices | |
| H2 | Were the goals of the series B reached? | The goals the series B round set (ARR, NRR, burn multiple, breakeven month), each with what was reached and when, from the board packs and the P&L | Board packs, P&L | *proof*. The series B deck promised them. **Absent = red.** Shown next to the plan vs actual table |
| H3 | Runway and burn on the three-year model? | Monthly burn, cash and months of runway, consistent with the financial model, with and without the round | Financial model, P&L | *proof* |
| H4 | Previous rounds, the stack of liquidation preferences, secondary sales, and debt with its terms? | Amounts and investors for each round, the preference of each (multiple, participation, seniority, ratchets), any secondary sale, and every debt line with its terms, from the cap table and the terms | Cap table with terms, web: press, registry | *proof*. **A participating preference or a ratchet absent from the deck and present in the terms is a contradiction** |
| H5 | Which exit path, in facts only? | Named acquirers with a public trace of interest in the category, or listed comparables with their filings | Web: filings, press of acquisitions | *proof*. Facts only, shown as benchmarks. Never a valuation, never a multiple applied to the company |

### Block I. References, weight 1

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| I1 | Customers we can call, including one that left, one of the second product and one outside the home country? | Names and a way to contact them, including at least one lost customer, one customer of a product after the first, and one outside the home country | The deck suffices | |
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

| Model | What the block does to the series C grid | What it does to the document list |
|---|---|---|
| SaaS (default) | Nothing. The grid is written for it. Benchmarks only | Nothing. The base list is written for it |
| Marketplace | Adds M1 to M4 to block B: GMV and take rate over 48 months, both sides coming back, concentration of the top twenty sellers and buyers and its trend, GMV retention by cohort vintage and by side | Adds `gmv_48m`: monthly GMV, take rate, active supply and demand, 48 months |
| Consumer | Adds N1 to N3 to block B: DAU over MAU over 48 months, older cohorts next to newer ones, organic share and paid CAC by country. Removes the ACV by segment (B2), the magic number (C5), the win rate trend (D3) and the deals without a founder (D6). Lowers the ARR weight (B1) to 1 | Removes `crm_pipeline`, `sales_roster`, `top20_contracts`. Adds `product_analytics_36m`: MAU, DAU over MAU, retention cohorts, organic share, 36 months |
| E-commerce | Adds O1 and O2 to block C: contribution margin per order after shipping and returns over 48 months, CAC by channel and country with payback. Adds O3 to block E: 60-day repeat rate by cohort vintage. Removes the magic number (C5), the win rate trend (D3) and the deals without a founder (D6) | Removes `crm_pipeline`, `sales_roster`, `top20_contracts`. Adds `orders_export_48m`: orders with revenue, cost of goods, shipping, returns, discounts, marketing by channel, 48 months |
| Hardware | Adds P1 to P3 to block C: margin by volume and realized in three years of audited accounts, bill of materials with its 48-month curve, MOQ, inventory and warranty. Doubles the weight of efficient growth (C to 6) | Adds `bom_and_suppliers`: BOM with unit cost, supplier contracts with MOQ and terms. Adds `inventory_36m`: inventory, warranty claims and returns by month, 36 months |
| Fintech | Adds a block Q, weight 2: licences by country (Q1), cost of compliance against three years of audited accounts (Q2), credit or fraud risk (Q3), losses on the book over 48 months by vintage (Q4) | Adds `licence`: licences or agreements per country, regulator correspondence, compliance cost lines. Adds `risk_book_48m`: loan, transaction or policy book with losses, defaults, fraud, chargebacks, 48 months |
| Biotech | Traction (B), position and durability (D) and net retention (E) to weight 0, efficient growth (C) to 1. Removes the magic number (C5), pricing power (D2), the win rate trend (D3) and the deals without a founder (D6). Adds a block R, weight 3: clinical milestones reached since the series B, intellectual property, regulatory path and what the round funds up to | Removes `cohorts_36m`, `crm_pipeline`, `sales_roster`, `billing_export_24m`, `top20_contracts`. Adds `clinical_dossier`: protocols, results, regulator correspondence per milestone. Adds `ip_schedule`: patent filings, status, jurisdictions, ownership |

`scripts/render_grid.py series_c <model>` writes the effective grid, model block applied and
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
| D. Position and durability | 3 | 17 % |
| E. Net retention | 2 | 11 % |
| F. Market and competition | 2 | 11 % |
| G. Leadership and organisation | 2 | 11 % |
| H. Money and exit | 2 | 11 % |
| I. References | 1 | 6 % |

Efficient growth and position and durability make 33 % of the score, as efficient growth and
repeatability did at series B. The shares move with the model block.

Implementation rules, fixed with the grid:

- C5 and D6 count with weight 0 when the profile says B2C. A question at weight 0 is asked for
  information: it never raises a red signal (`score.py`), so a B2C deck's red signals are B4,
  D1, E2, G1 and H2.
- A question marked *proof* whose value is found without a proven or confirmed claim cited is
  capped at partial by `apply_proof_cap.py`. An answer citing a claim left to probe is lowered
  one step.
- A block is **red** when its completeness is below 50 % and its weight is above 0.
- **Confirmation passes**, as at seed: between 65 % and 80 % inclusive, three independent
  checker passes and the median per question.
- **The plan vs actual table** is laid out by `report.py` from the claims of type
  `plan_vs_actual` that carry a metric and a quarter: plan from the board pack, actual from the
  P&L, gap = (actual − plan) / |plan|, the last eight quarters. Per metric, the average gap and
  the quarters missed (ARR and net new ARR below plan, net burn above plan; headcount shows its
  gap without a count). Empty cells stay empty. Displayed, never scored.

### Gap thresholds

Those of seed: minor at 25 %, to probe up to a factor of 2, blatant above. Ratio =
|deck − found| / max(|found|, 1). A non-numeric contradiction (a named customer that does not
exist, a participating preference in the terms that the deck does not state) is blatant by
default and goes to the review like the others.

### Documents gate

The list is per stage and model, no coverage threshold. The base list below is written for
SaaS; the model block adjusts it with `remove` and `add`, as in the table above. The minimum
number of months lives in the grid file, readable, corrected at each post-mortem.

| id | Document | What it must contain | Minimum |
|---|---|---|---|
| `pnl_48m` | Monthly P&L by product and by geography | Revenue and cost of revenue by product and by geography, operating expenses by function, net burn, month by month | 48 months |
| `accounts_audited_3y` | Audited annual accounts with the auditor's opinion | Balance sheet, income statement, cash flow statement and the auditor's report with its opinion, for each of the last three fiscal years | 3 years |
| `cohorts_36m` | Cohorts by segment and by acquisition year | Revenue and logo retention by acquisition cohort, split by segment and by acquisition year | 36 months |
| `crm_pipeline` | CRM export with weighted pipeline, owner, and win/loss with competitor | Every deal with stage, probability, amount, owner, segment, product, geography, first contact and signature dates; lost deals with the reason and the competitor | weighted pipeline |
| `sales_roster` | Sales roster with quota attainment | Each rep with start date, quota, attainment by quarter, and departures | 24 months |
| `billing_export_24m` | Billing export | Every contract with its list price, net price and discount, month by month | 24 months |
| `cap_table_terms` | Cap table with the terms of every round and any debt agreement | Every holder with its share and the option pool; for every round the liquidation preference, participation, ratchets and secondary sales; every debt agreement with its terms | |
| `model_3y` | Three-year financial model with a zero-burn scenario | Revenue by product and geography, expenses by function, cash, hires, month by month, the breakeven month if planned, and a scenario with spending frozen at the level the cash on hand allows | 3 years |
| `top20_contracts` | Signed contracts of the top 20 customers | The signed contract of each of the twenty largest customers by ARR | 20 contracts |
| `board_pack_8q` | Board decks or minutes with budget vs actual | The board deck or the minutes of each of the last eight quarters, with the budget or plan of the quarter next to the actual | 8 quarters |
| `org_chart` | Org chart and headcount history | Headcount by function month by month, start and end dates, and the executive team with start dates | 36 months |

A document missing, or covering fewer months or items than the minimum, stops the reading with
the email draft. The classification of each annex is made by an agent with a verbatim quote,
checked by code; the decision is the code's.

### Web rule

At least 2 sources on distinct domains, after searching both for and against. Two domains of
the same owner count as one. Silence is unverifiable, not contradicted. Web-checked at series C:
everything checked at series B, plus the annual accounts filed at the company registry
(Infogreffe, Companies House, Handelsregister or the local registry) compared with the audited
accounts, the history of the public pricing page on the Wayback Machine against the list prices
of the billing export, the trend of public reviews (G2, Capterra) over 24 months, litigation and
security incidents made public, the rounds raised by competitors since the series B, and listed
comparables or named acquirers for the benchmarks. Revenue, NRR, plan vs actual, discounts, free
cash flow and preferences are never "checked on the web".

---

## What the tool outputs

- **Nine bars** of completeness, one per block, and the global.
- **Per question**: the value, the page, the verbatim quote, the claims cited, whether the
  value was capped or lowered, and the benchmark for the model and stage next to it, with source
  and date.
- **The claims**: each one proven, confirmed, not covered, unverifiable, to probe or
  contradicted, with the source, and the benchmark next to each figure.
- **The plan vs actual table, quarter by quarter**: ARR, net new ARR, net burn and headcount;
  the plan from the board pack, the actual from the P&L, the gap in percent computed by code,
  the average gap and the quarters missed per metric. Empty cells stay empty.
- **The two engines side by side**, as at series B.
- **The contradictions**: the gaps to probe, with both sides and the explanation found at review.
- **The documents to request**: the list of the stage and model, document by document, with the
  email draft. The tool writes the draft; the user sends it, or not.
- **The questions for the call**: every absent or partial question of a weight-3 block, plus
  every contradiction.

What it does not output: a rating of the company, a verdict, a threshold, a valuation. Listed
comparables and named acquirers are shown as facts next to H5, never turned into a price.

---

## Guardrails

Those of seed, without exception, plus three:

- A benchmark is an order of magnitude displayed next to the deck figure, never a criterion of
  the grid. It lives in its own file, per model and per stage
  (`scripts/grids/benchmarks/<model>.json`, `stages.series_c`), with its value, its source and
  its date. A benchmark without a dated source stays empty.
- The document list is the same for every deck of the same stage and business model. The model
  block adjusts it, in the model's own file (`skills/deck-reader/grids/models/<model>.md`,
  "Series C: documents"); the tool never adapts it to a deck, never shortens it, never asks for
  more.
- This is a triage that prepares the call, not a due diligence. The zero-burn scenario, the
  preference stack and the exit path are read as written in the documents; the tool never
  recomputes a model, never values a preference, never prices an exit.

---

## Benchmarks

Shown next to the figures, never scored. SaaS at series C: ARR growth, net retention, gross
margin and free cash flow margin at 50 to 100M USD ARR and above 100M USD ARR (Bessemer,
Scaling to $100 Million, 2021-09-21: growth 60 % average at both, medians 60 % and 57 %; FCF
margin -37 %+ and -35 %+, top performers -25 %+ and -20 %+); Rule of 40 as growth plus profit,
written for companies with at least 50M USD of revenue (Brad Feld, 2015-02-03) and as ARR growth
plus FCF margin (ICONIQ, 2025); net dollar retention settling at 110 to 120 % (ICONIQ, 2025),
public SaaS at 110 % (High Alpha, 2024); burn multiple bands and trajectory (Sacks, 2020-04-23);
magic number (Scale VP, 2010-04-20 and 2020-09-11). ICONIQ 2025 and High Alpha 2024 give no
growth or FCF figure by ARR bucket above 50M USD on their pages: not shown. Plan attainment,
discount trend, win rate trend, zero-burn growth, share of ARR from second products or from
abroad, series C round size, and exit comparables (read per deck by the web check, never as a
generic figure): no dated source, left empty.

---

## Where the grid comes from

- **Bessemer's Scaling to $100 Million** ([bvp.com/atlas/scaling-to-100-million](https://www.bvp.com/atlas/scaling-to-100-million),
  2021-09-21): growth, net retention, gross margin and free cash flow margin at 50 to 100M USD
  and above 100M USD ARR. The main source of the SaaS series C benchmarks, and the reason C6
  reads the free cash flow margin with its direction rather than growth alone.
- **The burn multiple** ([David Sacks, 2020-04-23](https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200)):
  net burn over net new ARR, its bands, and the expectation that it improves after each round.
  C3 asks for three windows so that the direction can be read against growth.
- **The Rule of 40** ([Brad Feld, 2015-02-03](https://feld.com/archives/2015/02/rule-40-healthy-saas-company/)):
  growth rate plus profit margin should add up to 40 %, written for SaaS companies with at least
  50M USD of revenue. C4 asks for it two years in a row.
- **The magic number** (Scale Venture Partners, [Magic Number Math](https://www.scalevp.com/insights/magic-number-math/),
  2010-04-20, and [A History of the Magic Number](https://www.scalevp.com/blog/saas-metrics-a-history-of-the-magic-number),
  2020-09-11): the definition and the benchmark of C5, unchanged from series B.
- **The 2024 SaaS Benchmarks Report** (High Alpha, continuing OpenView,
  [highalpha.com/saas-benchmarks/2024](https://www.highalpha.com/saas-benchmarks/2024), 2024
  edition): net dollar retention of public SaaS at 110 %. No figure by ARR bucket above 50M USD
  on the page.
- **ICONIQ Growth's State of Software 2025** ([iconiq.com](https://www.iconiq.com/growth/reports/2025-state-of-software))
  and its [Enterprise Five](https://www.iconiq.com/growth/reports/the-iconiq-enterprise-five),
  2025: net dollar retention at 110 to 120 %, Rule of 40 as ARR growth plus free cash flow
  margin and the most reliable predictor of valuation. No figure by ARR band above 50M USD on
  the pages.

None of them reads the board packs of eight quarters, compares the filed accounts with the
audited ones, or finds the ratchet the deck does not mention. That is what the tool does.

---

## Revisions

| Date | Change | Triggered by |
|---|---|---|
| 2026-09-14 | First version: series C grid for series C and every later round, eleven documents for SaaS over 48 months, position and durability block, plan vs actual over eight quarters in the report, new claim types, wider web check, series C benchmarks | Series C grid; `series-c-or-later` now routes to a grid |

# The series D grid

**Grid version: 2026-09-14. Stage covered: series D and every later round (series E, growth rounds, pre-IPO).**

This file is a fixed copy of the grid. It does not change at run time. The machine-readable
version used by the scripts is `scripts/grids/series_d.json`; both must stay identical.

**A deck is scored according to its stage.** Same engine as the pre-seed, seed, series A,
series B and series C grids, another question. Pre-seed asks "what does the deck not say?".
Seed asks "does what the deck says hold up?". Series A asks "does the machine repeat?". Series B
asks "does the machine hold at scale, without the founders?". Series C asks "does the machine
hold without new money, and keep its place?". Series D asks "**is the machine ready to change
hands, and why this round?**": does the company hit the quarters it forecasts, the way a public
market or an acquirer will demand, are its accounts and controls ready for that scrutiny, is a
second act carrying growth as the first product matures, and why does this round exist at all:
what does it precede, at what price against the last one, under what preference stack, and is
it the last private one?

**What the grid measures**: the completeness of the deck, and whether its statements are backed
by the required documents of the stage and model and by public sources. It does not measure the
quality of the company. No verdict, no threshold, no rating, no valuation.

---

## What changes from series C

| | Series C | Series D |
|---|---|---|
| What is judged | Evidence of durability: the plan of the series B met quarter after quarter, growth that holds as burn falls, prices that hold, a position kept against funded entrants, products and countries after the first with their own economics | Evidence of readiness to change hands: **the forecasts hit at guidance level, quarter after quarter**, accounts and controls that stand public scrutiny, a second act that carries growth, acquisitions that kept their ARR, and **a round with a stated reason**, a stated price against the last round, a preference stack read in the terms, and a model that says whether another round is needed |
| Central proof | The past of the deck: the series B plan against the actual, eight quarters | **The dispersion of the forecasts**: twelve quarters of plan against actual, counted by band (within 5 %, within 10 %, beyond), because a public market punishes the miss, not the average |
| Input | The deck, plus a required list of eleven documents for SaaS, over 48 months | The deck, plus **a required list of twelve documents** for SaaS, over 60 months: monthly P&L by product and geography, audited accounts over three years with the opinion and the standard, cohorts over 48 months, CRM with win/loss, sales roster, **billing export with contract start and end dates**, **cap table with the terms of every round and this round's term sheet if signed**, three-year model **with the cash line of this round**, top 20 contracts, **board pack of twelve quarters with the issue dates**, org chart over 48 months, **the auditor's management letters over three years**. The model block adjusts the list |
| First gate | A missing document stops the reading | Same mechanism. **The management letters are new**; the board pack goes to twelve quarters, the billing export carries the contract dates |
| Heaviest blocks | Efficient growth, position and durability (weight 3) | **Profitable growth, predictability and exit readiness (weight 3).** Position and durability gives way to predictability and exit readiness; pricing power and the win rate trend move to market and competition |
| Claims verified | The series B types, plus plan vs actual, net price, discount rate, free cash flow margin, zero-burn growth, product share, geographic share, liquidation preference, debt terms, audit opinion, controls certification, competitor funding, exit comparables | The same, plus: **backlog, round price, round purpose, acquired company, management letter, close cycle** |
| Web check | The series B scope, plus the accounts filed at the registry, the pricing page history, the review trend, litigation and incidents, competitors' rounds, listed comparables | The same, plus: **the press of every previous round for its price**, the press and the registry for every acquisition, tender offers and secondary sales made public, the competitors acquired or listed since the series C, **the last IPO filings of the category** (S-1, F-1, prospectus) for the comparables |
| Extra output | The plan vs actual table over eight quarters | The same over twelve quarters **with the distribution by band**, plus **the preference stack as a table** and **the company next to the last IPOs of its category**: growth, free cash flow margin, net retention, gross margin, backlog, as the filings state them at IPO. Facts, never a price |

---

## The series D principle

There are five years of figures, three audited years, twelve board packs. Whether the machine
holds is no longer the question either: the series C answered it. The question is what happens
when the company belongs to someone else, a public market, an acquirer, a buyout fund, and
whether the round on the table is a step towards that or a way to avoid it. Two things say so.
The board packs say how often the company misses what it forecast, and by how much. The terms
say at what price and under what stack the money came in, and the model says whether more will
be needed. A series D deck that does not say why the round exists is itself the signal.

Red signals of the stage:

- More than two quarters beyond 10 % of plan in the last two years
- A round whose reason is not in the deck
- A model that needs another round when the deck says this is the last
- A price at or below the last post-money that the deck does not say
- An IPO ratchet in the terms
- Acquired ARR that shrank since closing
- A material weakness in a management letter
- A document of the list missing

---

## How the series D reading works

1. **Read.** The PDF page by page; the annexes read separately (`annex_text.py`).
2. **Profile.** Sector, model type (SaaS, marketplace, consumer, e-commerce, hardware, fintech,
   biotech), B2B or B2C, announced stage. The stage picks the grid: "series D", "série D",
   "series E", "growth round", "pre-IPO" and every later round route to this grid
   (`series-d-or-later`); "series C" routes to the series C grid. The model picks the model
   block. No model detected means SaaS.
3. **Documents, first gate.** The code builds the required list: the base list of the stage,
   written for SaaS, adjusted by the model block with `remove` and `add`
   (`documents_gate.py required --grid series_d --profile`). An agent sorts each annex into one
   of the expected documents, with a quote that proves it and the months or items covered
   (`annex-classifier`); the code checks the quote, then compares with the list
   (`documents_gate.py documents`):
   - a document missing, or covering fewer months or items than required: stop, email draft
     document by document, no claims, no web, no grid;
   - every document present: continue.
4. **Claims.** Every verifiable statement of the deck, one line each with page and quote
   (`claim-extractor`, checked by `check_claims.py`). The series C types plus the series D ones:
   backlog, round price, round purpose, acquired company, management letter, close cycle. A
   plan vs actual claim carries its metric and quarter; an exit comparable read in an IPO filing
   carries the comparable's name and the metric; a preference carries its round.
5. **Proof in the documents.** Each claim looked up in the required documents (`annex-matcher`,
   checked and classified by `verify_matches.py`). **The central proof is the dispersion of the
   forecasts**: a plan vs actual claim is looked up twice, the plan in the board pack of its
   quarter, the actual in the P&L, over twelve quarters. A management letter finding is read in
   the letter; a close cycle in the issue dates of the board packs; a backlog in the contract
   dates of the billing export; the price of a round and its preference in the terms; the cash
   line of the round in the model. Same gap thresholds as seed. What is not covered is listed in
   the report; it never stops the reading.
6. **Web check**, only now, and only on what a document cannot settle: the series C scope, plus
   the press of every previous round for its price, the press and the registry for every
   acquisition, tender offers and secondary sales made public, the competitors acquired or
   listed since the series C, and the last IPO filings of the category for the comparables
   (`web-verifier`, rules enforced by `verify_web.py`). Searched both for and against; at least
   two independent domains to conclude; otherwise unverifiable. An ARR is never checked on the
   internet.
7. **Double check.** As at seed: every blatant contradiction goes to an independent reviewer
   whose only job is to find an honest explanation (`contradiction-reviewer`). Without one, the
   second gate stops the reading and shows the sources on both sides.
8. **Grid**, on the deck and the proofs. A figure without a proven or confirmed claim behind it
   is capped at partial by code (`apply_proof_cap.py`); an answer citing a gap to probe is
   lowered one step.
9. **Report.** Nine bars, the reading, the gaps to probe, the documents still to request with
   the email draft, the claims table with the benchmark next to each figure, **the plan vs
   actual table over twelve quarters with the distribution by band**, **the preference stack**,
   **the company next to the last IPOs of its category**, question by question.

The score is computed by the code. The model never sees it. The tool never sends the email.

---

## The scale

Found 2, partial 1, absent 0, each with the deck page and the verbatim quote. Same scale as
pre-seed, seed, series A, series B and series C. Same rule as seed: a question marked *proof*
cannot be found from the deck alone.

---

## Blocks and questions

"Proof expected" is the document, among the required list, that backs the answer.

### Block A. Problem and customer, weight 1

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| A1 | Which segments are served, and do the last twenty customers match them? | A nameable profile (size, role, sector) per segment, and the last twenty signed contracts fit one of them | Top 20 contracts | *proof*. A customer that fits no segment is a question for the call |
| A2 | Why do they buy, and why do they renew, per segment, in their own words? | A purchase quote and a renewal quote per segment, or a documented use case with both | The deck suffices | One segment quoted for all = partial |
| A3 | What was dropped since the series C? | A segment, geography, product, channel or acquisition abandoned since the series C round, dated, with what triggered it | The deck suffices | Nothing dropped since the series C = partial at best |

### Block B. Traction, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| B1 | ARR today, and the monthly curve over 60 months? | An ARR and the monthly points over 60 months, matching the P&L and the audited accounts | Monthly P&L, audited accounts | *proof*. A growth percentage without its starting point = absent |
| B2 | How many paying customers, and the average contract value by segment? | A customer count and an ACV per segment, backed by the contracts or the P&L | Contracts, P&L | *proof* |
| B3 | Year-over-year growth for each of the last four years, with the starting points? | Five dated ARR points twelve months apart and the four ratios | Monthly P&L | *proof*. Benchmark shown next to the figure, never in the score |
| B4 | Do the named customers exist, pay, and use the product? | Confirmed outside the deck: a contract in the annexes, and a website, LinkedIn page or public review | Contracts, web | *proof*. **Still the central question.** Absent = red |
| B5 | How much of ARR do the top twenty customers make, and how has that share moved over 36 months? | A share of ARR for the top twenty today and 36 months ago, confirmed against the contracts or the P&L | Contracts, P&L | *proof*. A single customer above 20 % of ARR is a question for the call, not a verdict |
| B6 | New ARR by channel, segment, product and geography? | Each channel, segment, product and geography with its share of new ARR over twelve months, from the CRM export and the P&L | CRM export, P&L by product and geography | *proof*. All from one channel or one product = partial |
| B7 | Backlog: contracted revenue not yet recognised, and the share of ARR under multi-year contracts? | The remaining value of signed contracts not yet recognised (RPO) and the share of ARR under contracts of two years or more, from the start and end dates of the billing export and the top 20 contracts | Billing export with contract dates, top 20 contracts | *proof*. A backlog without the contract end dates behind it = partial. Benchmark shown next to the figure, never in the score |

### Block C. Profitable growth, weight 3

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| C1 | Gross margin, confirmed against the audited accounts? | A gross margin with what is included in cost of revenue, and the same figure in the audited accounts | Audited accounts, P&L | *proof*. A margin that excludes hosting, support or implementation = partial |
| C2 | CAC payback by channel and by segment, and its trend over 36 months? | A payback in months per channel and per segment, with the method, and its curve over 36 months | CRM export, P&L | *proof*. A single blended figure = partial |
| C3 | Burn multiple over three twelve-month windows, or the quarter it stopped applying? | Net burn divided by net new ARR for each of the last three twelve-month windows, from the P&L, and the direction of the change; or the quarter where net burn turned positive, after which the multiple no longer applies | Monthly P&L | *proof*. **Growth that slows faster than burn falls is a red signal of the stage.** Benchmark shown next to the figure (Sacks), never in the score |
| C4 | Rule of 40, three years in a row? | Revenue growth plus free cash flow or operating margin for each of the last three fiscal years, from the P&L and the audited accounts | Monthly P&L, audited accounts | *proof*. Fewer than three years = partial. Benchmark shown next to the figure, never in the score |
| C5 | Sales efficiency: magic number? | Net new ARR of the quarter over the previous quarter's sales and marketing spend, over the last four quarters | Monthly P&L | *proof*. B2B only. Weight 0 in B2C |
| C6 | Free cash flow margin over 36 months, and its direction? | Free cash flow over revenue, quarter by quarter over 36 months, from the P&L and the cash flow statements of the audited accounts | Monthly P&L, audited accounts | *proof*. A margin without its direction = partial. Benchmark shown next to the figure, never in the score |
| C7 | What growth does the model forecast at zero burn? | A scenario of the three-year model where spending is frozen at the level the cash on hand allows, with the ARR growth it forecasts year by year | Financial model | *proof*. A model without a zero-burn scenario = absent. The scenario is read, never judged |
| C8 | Breakeven: reached, with its date in the accounts, or dated in the model within the cash of this round? | The period where free cash flow turned positive, in the audited accounts or the P&L, or the month where it does in the three-year model with the cumulative cash to get there and the model's cash line staying above zero to that month with this round and no further one | Audited accounts, P&L, financial model | *proof*. Neither reached nor dated within the cash of the round = absent. The model is read, never recomputed |

### Block D. Predictability and exit readiness, weight 3

The block that separates series D from series C. It replaces position and durability.

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| D1 | Plan against actual over twelve quarters: how many quarters within 5 %, within 10 %, and beyond? | For each of the last twelve quarters, the plan of the board pack and the actual of the P&L for ARR, net new ARR, net burn and headcount, and per metric the number of quarters within 5 %, within 10 % and beyond 10 % of plan | Board packs, monthly P&L | *proof*. **The central proof of the stage**: a public market punishes a missed quarter, and the board packs say how often the company misses. **More than two quarters beyond 10 % of plan in the last two years is a red signal of the stage.** Absent = red. Laid out quarter by quarter in the report, with the distribution |
| D2 | Reporting: under which standard are the accounts audited, how many days to close a quarter, and what did the auditor's management letters report? | The accounting standard of the audited accounts (IFRS, US GAAP or the local GAAP) in the auditor's report, the days between quarter end and the issue of the board pack of that quarter over the last eight quarters, and each control deficiency or material weakness of the last three management letters, or the statement that there was none | Audited accounts, management letters, board packs | *proof*. **A material weakness in a management letter is a red signal of the stage.** A close cycle without its dates = partial |
| D3 | Second act: what share of net new ARR comes from products launched in the last 36 months, and with what economics next to the first? | The share of net new ARR over twelve months from the products launched in the last 36 months, with the gross margin and the net revenue retention of each next to those of the first product, from the P&L by product and the cohorts | P&L by product, cohorts | *proof*. A second act without its own economics = partial at best. No product launched in 36 months = absent |
| D4 | Acquisitions since the series C: ARR at closing against today, and the team retained? | For each company acquired since the series C, the date, the consideration, the ARR at closing and today from the P&L by product, and the share of its team still in the org chart; or the statement that none was made, matching the cap table and the registry | P&L by product, org chart, cap table, web: press, registry | *proof*. **Acquired ARR that shrank since closing is a red signal of the stage.** An acquisition absent from the deck and present in the cap table or the registry is a contradiction |
| D5 | What share of ARR comes from outside the home country, and with what economics? | The ARR outside the home country as a share of total ARR, by country or region, with its gross margin and new ARR, from the P&L by geography | P&L by geography | *proof*. A geography without its own economics = partial at best |

### Block E. Net retention, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| E1 | Net revenue retention by segment and by cohort vintage? | An NRR per segment and per acquisition year over a twelve-month window, with the definition used, recomputable from the cohorts | Cohorts by segment and acquisition year | *proof*. **Older cohorts below younger ones are a red signal of the stage** and a question for the call. Benchmark shown next to the figure, never in the score |
| E2 | Gross retention and logo churn, with the reasons? | A gross revenue retention and a logo churn figure, and a reason per lost customer | Cohorts, CRM win/loss | *proof*. Absent = the deck hides churn. Red |
| E3 | Do the cohorts flatten at 48 months, in each segment? | Cohort curves of at least 48 months per segment, with the month where they flatten | Cohorts by segment | *proof*. A segment whose cohorts do not flatten is a question for the call |
| E4 | Expansion: what share of new ARR comes from existing customers, and what triggers it? | A share of net new ARR from expansion, with the trigger (seats, modules, price, second product) | Cohorts, contracts, P&L by product | *proof* |

### Block F. Market and competition, weight 2

Pricing power and the win rate trend come here from the series C block D.

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| F1 | Market size computed bottom-up with the ACV by segment, and the share already taken? | Possible customers per segment multiplied by the ACV signed in that segment, with visible assumptions, and the current ARR as a share of it | The deck, assumptions visible | An analyst figure = absent |
| F2 | Who are the competitors, and what is the win rate against each? | Named competitors, the same names in the CRM win/loss with a win rate against each | CRM win/loss, web | *proof*. Web check: omitted competitors become a contradiction |
| F3 | Win rate against each competitor, and its trend over 36 months? | Deals won and lost against each named competitor, quarter by quarter over 36 months, from the CRM win/loss | CRM win/loss | *proof*. A win rate without its trend = partial |
| F4 | Pricing power: net price against list price per contract, and the trend of discounts over 36 months? | The list price and the net price of each contract, and the average discount month by month over 36 months, from the billing export | Billing export | *proof*. **Discounts that rise are a red signal of the stage** |
| F5 | Which entrants have raised money since the series C, and which competitors were acquired or listed? | The competitors that raised a round since the series C, with the amount and the date, the competitors acquired or listed since, with the acquirer or the market, and what the deck says about them | Web: press of competitors' rounds, acquisitions and listings | *proof*. Web check: the press of competitors' rounds, acquisitions and listings. A funded entrant or an acquisition the deck does not name is a contradiction |
| F6 | Why now, and why still? | A recent, named, verifiable change, why the window is still open after the series C, and what a well-funded entrant or an incumbent would need | Web | |

### Block G. Leadership and organisation, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| G1 | Does the executive team exist, and has the CFO already taken a company through an IPO, a sale or public reporting? | CFO, CRO or VP Sales, CTO or VP Engineering, CPO, and a general counsel or head of legal: each named in the deck and found on LinkedIn with that role at the company, and a CFO who has already held audited accounts and been through an IPO, a sale or a public-company finance role, here or before | Org chart, web: LinkedIn | *proof*. An executive on a slide who is not on LinkedIn is a contradiction. **Absent = red** |
| G2 | Which executives left in the last 24 months, and why? | Each departure from the executive team with its date and a reason, matching the org chart and LinkedIn | Org chart, web: LinkedIn | *proof*. A departure found on LinkedIn and not in the deck is a contradiction |
| G3 | Headcount by function over 48 months, and regretted attrition? | Headcount per function month by month over 48 months, matching the P&L by function, and the share of departures the company did not want | Org chart, P&L | *proof*. Headcount that does not match the P&L is a gap to probe |
| G4 | The board: members, independents, committees, cadence? | The board members with their affiliation, the independent seats, the audit and compensation committees if any with their members, and the meeting dates of the last twelve quarters | Board packs | *proof* |
| G5 | Controls: three fiscal years audited without qualification, and SOC 2 Type II or ISO 27001? | An unqualified auditor's opinion on each of the last three fiscal years, and, for a B2B company, a SOC 2 Type II report or an ISO 27001 certificate with its date and scope | Audited accounts, web: registry, trust page | *proof*. **Accounts with a qualified opinion are a red signal of the stage.** In B2C the certification is not asked: three unqualified opinions = found |
| G6 | Do the open job posts match the hiring plan, by function and by country? | Public job posts that correspond to the hiring plan of the round, function by function and country by country | Financial model, web: careers page, LinkedIn jobs | *proof*. A country in the plan with no post: a question for the call |
| G7 | Who owns what? | Founders, investors, employees, option pool and what is left to grant, from the cap table | Cap table | *proof* |

### Block H. The round and the exit, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| H1 | How much is asked, and what for, by function, product, geography and acquisition? | An amount and a breakdown by function, by product, by geography and, when acquisitions are planned, by acquisition | The deck suffices | |
| H2 | Were the goals of the series C reached? | The goals the series C round set (ARR, NRR, free cash flow margin, breakeven month), each with what was reached and when, from the board packs and the P&L | Board packs, P&L | *proof*. The series C deck promised them. **Absent = red.** Shown next to the plan vs actual table |
| H3 | Why this round: what does it precede, and is it the last private one? | What the deck says the round leads to (profitability, an IPO window, an acquisition programme, a sale), and the three-year model's cash line staying above zero to that point with this round and no further one, or the explicit statement that another round is planned, with its date | Financial model, board packs | *proof*. **A round whose reason is not in the deck is a red signal of the stage.** A model that needs another round when the deck says this is the last is a contradiction. **Absent = red** |
| H4 | At what price, against the last round? | The pre-money of this round as the deck states it, and the post-money of the series C from the cap table with the terms, side by side | Cap table with terms, web: press of the series C | *proof*. **A price at or below the last post-money that the deck does not say is a contradiction.** The two figures are laid out, never judged |
| H5 | The preference stack: every round with its multiple, participation, seniority and ratchets, secondary sales, and debt with its terms? | For each round, the amount, the investors, the preference multiple, participation, seniority and any ratchet, including an IPO ratchet in the terms of this round; every secondary sale or tender offer with its amount; every debt line with its terms; from the cap table and the terms | Cap table with terms, web: press, registry | *proof*. **A participating preference, a ratchet or an IPO ratchet absent from the deck and present in the terms is a contradiction.** Laid out as a table in the report, never valued |
| H6 | Which exit path, in facts only, next to the last IPOs of the category? | Named acquirers with a public trace of interest in the category, or the last IPOs of the category with their filings, and the growth, free cash flow margin, net retention, gross margin and backlog those filings state at IPO | Web: IPO filings, press of acquisitions | *proof*. Facts only, laid out next to the IPO filings of the category. Never a valuation, never a multiple applied to the company |

### Block I. References, weight 1

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| I1 | Customers we can call, including one that left, one of a product launched in the last 36 months, one outside the home country, and one of an acquired company? | Names and a way to contact them, including at least one lost customer, one customer of a product launched in the last 36 months, one outside the home country, and, when an acquisition was made, one customer of the acquired company | The deck suffices | |
| I2 | Executives, board members, one executive who left, and the audit partner, we can call? | Same, plus the audit partner who signed the last opinion | The deck suffices | Asked to prepare the call, not to judge the deck |

---

## The business-model block

The profile detects the model; no model detected means SaaS. The model block lives in its own
file (`scripts/grids/models/<model>.json`, readable copy in `grids/models/<model>.md`) and is
applied to this grid by `grid_lib.effective_grid` in four verbs, in this order: **remove**
questions of the stage grid (by id), **reweight** blocks or questions, **add** questions to a
block with the block weight, or in a block the model brings, **documents** to adjust the
required document list of the first gate (remove by id, add entries of the same shape). One
block per business model, never one grid per sector. The deck never adjusts the list.

| Model | What the block does to the series D grid | What it does to the document list |
|---|---|---|
| SaaS (default) | Nothing. The grid is written for it. Benchmarks only | Nothing. The base list is written for it |
| Marketplace | Adds M1 to M4 to block B: GMV and take rate over 60 months, both sides coming back by market and vintage, concentration of the top twenty sellers and buyers and its trend over 36 months, GMV retention by cohort vintage and by side | Adds `gmv_60m`: monthly GMV, take rate, active supply and demand, 60 months |
| Consumer | Adds N1 to N3 to block B: DAU over MAU over 60 months, older cohorts next to newer ones over 48 months, organic share and paid CAC by country over 36 months. Removes the ACV by segment (B2), the magic number (C5) and the win rate trend (F3). Lowers the ARR weight (B1) to 1 | Removes `crm_pipeline`, `sales_roster`, `top20_contracts`. Adds `product_analytics_48m`: MAU, DAU over MAU, retention cohorts, organic share, paid CAC by country, 48 months |
| E-commerce | Adds O1 and O2 to block C: contribution margin per order after shipping and returns over 60 months, CAC by channel and country with payback. Adds O3 to block E: 60-day repeat rate by cohort vintage over 48 months. Removes the magic number (C5) and the win rate trend (F3) | Removes `crm_pipeline`, `sales_roster`, `top20_contracts`. Adds `orders_export_60m`: orders with revenue, cost of goods, shipping, returns, discounts, marketing by channel and country, 60 months |
| Hardware | Adds P1 to P3 to block C: margin by volume and realized in three years of audited accounts, bill of materials with its 60-month curve, MOQ, inventory and warranty over 48 months. Doubles the weight of profitable growth (C to 6) | Adds `bom_and_suppliers`: BOM with unit cost, supplier contracts with MOQ and terms. Adds `inventory_48m`: inventory, warranty claims and returns by month, 48 months |
| Fintech | Adds a block Q, weight 2: licences by country (Q1), cost of compliance against three years of audited accounts (Q2), credit or fraud risk (Q3), losses on the book over 60 months by vintage (Q4) | Adds `licence`: licences or agreements per country, regulator correspondence, compliance cost lines. Adds `risk_book_60m`: loan, transaction or policy book with losses, defaults, fraud, chargebacks, 60 months |
| Biotech | Traction (B), predictability and exit readiness (D) and net retention (E) to weight 0, profitable growth (C) to 1. Removes the magic number (C5), the win rate trend (F3) and pricing power (F4). Adds a block R, weight 3: clinical milestones reached since the series C next to what the series C funded, intellectual property, regulatory path and what the round funds up to | Removes `cohorts_48m`, `crm_pipeline`, `sales_roster`, `billing_export_36m`, `top20_contracts`. Adds `clinical_dossier`: protocols, results, regulator correspondence per milestone. Adds `ip_schedule`: patent filings, status, jurisdictions, ownership |

`scripts/render_grid.py series_d <model>` writes the effective grid, model block applied and
benchmarks listed, as one markdown document.

---

## The computation

Same as seed: points times the block weight, percentage per block, weighted mean. A block of
weight 0 is asked for information: it never counts in the global and is never red.

| Block | Weight | Approximate share of the score |
|---|---|---|
| A. Problem and customer | 1 | 6 % |
| B. Traction | 2 | 11 % |
| C. Profitable growth | 3 | 17 % |
| D. Predictability and exit readiness | 3 | 17 % |
| E. Net retention | 2 | 11 % |
| F. Market and competition | 2 | 11 % |
| G. Leadership and organisation | 2 | 11 % |
| H. The round and the exit | 2 | 11 % |
| I. References | 1 | 6 % |

Profitable growth and predictability and exit readiness make 33 % of the score, as efficient
growth and position and durability did at series C. The shares move with the model block.

Implementation rules, fixed with the grid:

- C5 counts with weight 0 when the profile says B2C. A question at weight 0 is asked for
  information: it never raises a red signal (`score.py`). The red signals of the stage are B4,
  D1, E2, G1, H2 and H3; a B2C deck has the same six.
- A question marked *proof* whose value is found without a proven or confirmed claim cited is
  capped at partial by `apply_proof_cap.py`. An answer citing a claim left to probe is lowered
  one step.
- A block is **red** when its completeness is below 50 % and its weight is above 0.
- **Confirmation passes**, as at seed: between 65 % and 80 % inclusive, three independent
  checker passes and the median per question.
- **The plan vs actual table** is laid out by `report.py` from the claims of type
  `plan_vs_actual` that carry a metric and a quarter: plan from the board pack, actual from the
  P&L, gap = (actual − plan) / |plan|, the last twelve quarters. Per metric, the average gap,
  the quarters missed (ARR and net new ARR below plan, net burn above plan; headcount shows its
  gap without a count), and **the distribution**: quarters within ±5 %, within ±10 %, beyond
  ±10 %. Empty cells stay empty. Displayed, never scored.
- **The preference stack** is laid out by `report.py` from the claims of types
  `liquidation_preference`, `funding`, `secondary_or_debt`, `debt_terms` and `round_price`, one
  row each with the round or instrument, the figure the deck states, the status set by code and
  the backing. Nothing is summed, nothing is valued.
- **The IPO comparables** are laid out by `report.py` from the claims of type `exit_comparable`
  that carry a `comparable` and a `metric` (ARR growth, free cash flow margin, net revenue
  retention, gross margin, backlog): the figure the filing states at IPO, and next to it the
  deck's own latest figure for the same metric from the last proven or confirmed claim of the
  matching type. Facts side by side; no multiple, no valuation, no ranking.

### Gap thresholds

Those of seed: minor at 25 %, to probe up to a factor of 2, blatant above. Ratio =
|deck − found| / max(|found|, 1). A non-numeric contradiction (a named customer that does not
exist, a participating preference or an IPO ratchet in the terms that the deck does not state,
an acquisition in the cap table that the deck does not state) is blatant by default and goes to
the review like the others.

### Documents gate

The list is per stage and model, no coverage threshold. The base list below is written for
SaaS; the model block adjusts it with `remove` and `add`, as in the table above. The minimum
number of months lives in the grid file, readable, corrected at each post-mortem.

| id | Document | What it must contain | Minimum |
|---|---|---|---|
| `pnl_60m` | Monthly P&L by product and by geography | Revenue and cost of revenue by product and by geography, operating expenses by function, net burn and free cash flow, month by month | 60 months |
| `accounts_audited_3y` | Audited annual accounts with the auditor's opinion and the accounting standard | Balance sheet, income statement, cash flow statement and the auditor's report with its opinion and the accounting standard applied, for each of the last three fiscal years | 3 years |
| `cohorts_48m` | Cohorts by segment and by acquisition year | Revenue and logo retention by acquisition cohort, split by segment and by acquisition year | 48 months |
| `crm_pipeline` | CRM export with weighted pipeline, owner, and win/loss with competitor | Every deal with stage, probability, amount, owner, segment, product, geography, first contact and signature dates; lost deals with the reason and the competitor | weighted pipeline |
| `sales_roster` | Sales roster with quota attainment | Each rep with start date, quota, attainment by quarter, and departures | 24 months |
| `billing_export_36m` | Billing export with contract dates | Every contract with its list price, net price and discount month by month, and its start date, end date and term | 36 months |
| `cap_table_terms` | Cap table with the terms of every round, this round's term sheet if signed, and any debt agreement | Every holder with its share and the option pool; for every round closed the price, the liquidation preference, participation, seniority, ratchets and secondary sales or tender offers; the term sheet of this round when one is signed; every debt agreement with its terms | |
| `model_3y` | Three-year financial model with the cash line of this round and a zero-burn scenario | Revenue by product and geography, expenses by function, cash, hires, month by month, the breakeven month if planned, the cash line with this round and without a further one, and a scenario with spending frozen at the level the cash on hand allows | 3 years |
| `top20_contracts` | Signed contracts of the top 20 customers | The signed contract of each of the twenty largest customers by ARR | 20 contracts |
| `board_pack_12q` | Board decks or minutes with budget vs actual | The board deck or the minutes of each of the last twelve quarters, with the budget or plan of the quarter next to the actual, and the date each was issued | 12 quarters |
| `org_chart` | Org chart and headcount history | Headcount by function month by month, start and end dates, and the executive team with start dates | 48 months |
| `management_letters_3y` | Auditor's management letters | The auditor's letter to management or to the audit committee for each of the last three fiscal years, with every control deficiency, significant deficiency or material weakness reported, or the statement that none was | 3 letters |

A document missing, or covering fewer months or items than the minimum, stops the reading with
the email draft. The classification of each annex is made by an agent with a verbatim quote,
checked by code; the decision is the code's.

### Web rule

At least 2 sources on distinct domains, after searching both for and against. Two domains of
the same owner count as one. Silence is unverifiable, not contradicted. Web-checked at series D:
everything checked at series C (the annual accounts filed at the company registry, Infogreffe,
Companies House, Handelsregister or the local registry, compared with the audited accounts; the
history of the public pricing page on the Wayback Machine; the trend of public reviews, G2,
Capterra, over 24 months; litigation and security incidents made public; the rounds raised by
competitors), plus the press of every previous round for its announced price, the press and the
registry for every acquisition made or announced, tender offers and secondary sales made public,
the competitors acquired or listed since the series C, and the last IPO filings of the category
(S-1, F-1 or prospectus) for the comparables. Revenue, NRR, plan vs actual, discounts, free cash
flow, backlog, preferences and management letters are never "checked on the web".

---

## What the tool outputs

- **Nine bars** of completeness, one per block, and the global.
- **Per question**: the value, the page, the verbatim quote, the claims cited, whether the
  value was capped or lowered, and the benchmark for the model and stage next to it, with source
  and date.
- **The claims**: each one proven, confirmed, not covered, unverifiable, to probe or
  contradicted, with the source, and the benchmark next to each figure.
- **The plan vs actual table over twelve quarters**: ARR, net new ARR, net burn and headcount;
  the plan from the board pack, the actual from the P&L, the gap in percent computed by code,
  the average gap, the quarters missed and the distribution by band per metric. Empty cells
  stay empty.
- **The preference stack**: every round, secondary sale, tender offer and debt line the deck
  states, one row each, with the figure, the status and the backing. Nothing summed, nothing
  valued.
- **The company next to the last IPOs of its category**: growth, free cash flow margin, net
  retention, gross margin and backlog as the filings state them at IPO, next to the deck's own
  figure for the same metric. Facts, never a price.
- **The contradictions**: the gaps to probe, with both sides and the explanation found at review.
- **The documents to request**: the list of the stage and model, document by document, with the
  email draft. The tool writes the draft; the user sends it, or not.
- **The questions for the call**: every absent or partial question of a weight-3 block, plus
  every contradiction.

What it does not output: a rating of the company, a verdict, a threshold, a valuation. Listed
comparables, IPO filings and named acquirers are shown as facts next to H6, never turned into a
price; a preference stack is shown as the terms state it, never valued.

---

## Guardrails

Those of seed, without exception, plus three:

- A benchmark is an order of magnitude displayed next to the deck figure, never a criterion of
  the grid. It lives in its own file, per model and per stage
  (`scripts/grids/benchmarks/<model>.json`, `stages.series_d`), with its value, its source and
  its date. A benchmark without a dated source stays empty.
- The document list is the same for every deck of the same stage and business model. The model
  block adjusts it, in the model's own file (`skills/deck-reader/grids/models/<model>.md`,
  "Series D: documents"); the tool never adapts it to a deck, never shortens it, never asks for
  more.
- This is a triage that prepares the call, not a due diligence. The cash line of the round, the
  preference stack, the price against the last round and the IPO comparables are read as
  written in the documents and the filings; the tool never recomputes a model, never values a
  preference, never prices a round, never prices an exit.

---

## Benchmarks

Shown next to the figures, never scored. SaaS at series D: the series C set again, none of it
being specific to a later round: ARR growth, net retention, gross margin and free cash flow
margin above 100M USD ARR (Bessemer, Scaling to $100 Million, 2021-09-21); Rule of 40 as growth
plus profit, written for companies with at least 50M USD of revenue (Brad Feld, 2015-02-03) and
as ARR growth plus FCF margin (ICONIQ, 2025); net dollar retention settling at 110 to 120 %
(ICONIQ, 2025), public SaaS at 110 % (High Alpha, 2024); burn multiple bands and trajectory
(Sacks, 2020-04-23); magic number (Scale VP, 2010-04-20 and 2020-09-11). Forecast accuracy by
band, backlog and multi-year share, days to close, management letter findings, the price of a
series D against the series C, series D round size, and the figures of the category's IPOs
(read per deck from the filings, never as a generic figure): no dated source, left empty.

---

## Where the grid comes from

- **The series C grid** (`series_c.md`): the engine, the document gate, the claims, the web
  check, the plan vs actual table. Series D keeps all of it and asks the next question.
- **Bessemer's Scaling to $100 Million** ([bvp.com/atlas/scaling-to-100-million](https://www.bvp.com/atlas/scaling-to-100-million),
  2021-09-21): growth, net retention, gross margin and free cash flow margin above 100M USD ARR,
  the last bucket the page gives, and the reason the series D benchmarks are the series C ones.
- **The Rule of 40** ([Brad Feld, 2015-02-03](https://feld.com/archives/2015/02/rule-40-healthy-saas-company/)):
  growth plus profit, written for SaaS companies with at least 50M USD of revenue. C4 asks for
  it three years in a row, the three audited years.
- **The burn multiple** ([David Sacks, 2020-04-23](https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200)):
  net burn over net new ARR, and the expectation that it improves after each round. C3 keeps
  the three windows and adds the quarter where the multiple stops applying.
- **ICONIQ Growth's State of Software 2025** ([iconiq.com](https://www.iconiq.com/growth/reports/2025-state-of-software))
  and its [Enterprise Five](https://www.iconiq.com/growth/reports/the-iconiq-enterprise-five),
  2025: Rule of 40 as ARR growth plus free cash flow margin, the most reliable predictor of
  valuation. The reason block C reads free cash flow over 36 months with its direction.
- **The 2024 SaaS Benchmarks Report** (High Alpha, continuing OpenView,
  [highalpha.com/saas-benchmarks/2024](https://www.highalpha.com/saas-benchmarks/2024)): net
  dollar retention of public SaaS at 110 %.

Forecast accuracy by band, backlog, days to close, management letter findings and the price
against the last round have no dated benchmark: the grid asks for them because a public market
or an acquirer will, not because a report gives a median. The figures of the category's IPOs
are read per deck from the filings by the web check, never taken from a generic table.

None of them reads twelve board packs to count the missed quarters, reads the management
letters, or finds the IPO ratchet the deck does not mention. That is what the tool does.

---

## Revisions

| Date | Change | Triggered by |
|---|---|---|
| 2026-09-14 | First version: series D grid for series D and every later round, twelve documents for SaaS over 60 months with the auditor's management letters, predictability and exit readiness block, plan vs actual over twelve quarters with the distribution by band, the preference stack and the IPO comparables in the report, six new claim types, wider web check | Series D grid; series C now covers series C only |

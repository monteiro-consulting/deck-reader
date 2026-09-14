# Model block: Fintech

**Block version: 2026-09-14.** Readable copy of `scripts/grids/models/fintech.json`.

Money moves through the product, so a regulator, a partner bank and a loss rate sit between the
company and its revenue. The questions follow Qubit Capital's fintech due diligence checklist
and Mercury's stage-based metrics: licence or agreement, cost of compliance, credit or fraud
risk. They form the model's own block, weight 2.

| Stage | Remove | Reweight | Add | Documents |
|---|---|---|---|---|
| Seed | none | none | block Q (weight 2): Q1 to Q3 | none (no list at seed) |
| Series A | none | none | block Q (weight 2): Q1 to Q3 | add licence, risk_book_24m |
| Series B | none | none | block Q (weight 2): Q1 to Q4 | add licence, risk_book_36m |
| Series C | none | none | block Q (weight 2): Q1 to Q4 | add licence, risk_book_48m |
| Series D | none | none | block Q (weight 2): Q1 to Q4 | add licence, risk_book_60m |

## Seed: block Q. Licence and risk, weight 2 (brought by the model)

| # | Question | Found if | Note |
|---|---|---|---|
| Q1 | Which licence or agreement, held directly or through a partner, since when? | The licence or the regulated partner named, the regulator, and the date obtained or the date applied for | A licence 'in progress' without a filing date = partial |
| Q2 | What does compliance cost? | A monthly or annual compliance cost (people, tools, audits) as a share of expenses | *proof*. Benchmark shown next to the figure |
| Q3 | Credit or fraud losses, and how they are measured? | A loss rate or fraud rate over a period, with the denominator and the method | *proof*. A 'low' loss rate without a figure = absent |

## Series A: block Q. Licence and risk, weight 2 (brought by the model)

| # | Question | Found if | Note |
|---|---|---|---|
| Q1 | Which licence or agreement, held directly or through a partner, in which countries, since when? | The licence or the regulated partner named per country, the regulator, and the date obtained; the partner contract in the annexes | *proof*. A licence 'in progress' without a filing date = partial |
| Q2 | What does compliance cost, confirmed against the P&L? | A monthly compliance cost (people, tools, audits) as a share of expenses, and the same lines in the P&L | *proof*. Benchmark shown next to the figure |
| Q3 | Credit or fraud losses over twelve months, and how they are measured? | A loss rate or fraud rate over twelve months, by cohort, with the denominator and the method | *proof*. A 'low' loss rate without a figure = absent |

## Series A: documents (first gate)

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| licence | Licence, agreement or regulator correspondence | The licence or agreement held, or the regulator's correspondence on the application, and the compliance cost lines of the P&L. | — |
| risk_book_24m | Risk book over 24 months | Loan, transaction or policy book with losses, defaults, fraud and chargebacks, month by month. | 24 months |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_a.json`) with the changes above; the deck never adjusts it.

## Series B: block Q. Licence and risk, weight 2 (brought by the model)

| # | Question | Found if | Note |
|---|---|---|---|
| Q1 | Which licence or agreement, held directly or through a partner, in which countries, since when? | The licence or the regulated partner named per country, the regulator, and the date obtained; the licence or the partner contract in the annexes | *proof*. A licence 'in progress' without a filing date = partial |
| Q2 | What does compliance cost, confirmed against the P&L and the audited accounts? | A monthly compliance cost (people, tools, audits) as a share of expenses, and the same lines in the P&L and the audited accounts | *proof*. Benchmark shown next to the figure |
| Q3 | Credit or fraud risk: how is it underwritten and measured? | The underwriting or fraud rules, the denominator and the method of the loss rate, and who bears the loss (the company, a partner, an insurer) | *proof*. A 'low' risk without a method = absent |
| Q4 | Losses on the book over 36 months, by cohort? | Losses, defaults, fraud and chargebacks month by month over 36 months, by cohort, from the risk book | *proof*. A single annual loss rate = partial |

## Series B: documents (first gate)

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| licence | Licence, agreement or regulator correspondence | The licence or agreement held, or the regulator's correspondence on the application, and the compliance cost lines of the P&L. | — |
| risk_book_36m | Risk book over 36 months | Loan, transaction or policy book with losses, defaults, fraud and chargebacks, month by month. | 36 months |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_b.json`) with the changes above; the deck never adjusts it.

## Series C: block Q. Licence and risk, weight 2 (brought by the model)

| # | Question | Found if | Note |
|---|---|---|---|
| Q1 | Which licences or agreements, held directly or through a partner, in each country served, since when? | The licence or the regulated partner named for each country in the P&L by geography, the regulator, and the date obtained; the licences or the partner contracts in the annexes | *proof*. A country served without its licence or partner = partial |
| Q2 | What does compliance cost, confirmed against the P&L and three years of audited accounts? | A monthly compliance cost (people, tools, audits) as a share of expenses, and the same lines in the P&L and in each of the last three fiscal years of audited accounts | *proof*. Benchmark shown next to the figure |
| Q3 | Credit or fraud risk: how is it underwritten and measured? | The underwriting or fraud rules, the denominator and the method of the loss rate, and who bears the loss (the company, a partner, an insurer) | *proof*. A 'low' risk without a method = absent |
| Q4 | Losses on the book over 48 months, by vintage? | Losses, defaults, fraud and chargebacks month by month over 48 months, by vintage, from the risk book | *proof*. A single annual loss rate = partial. Older vintages worse than newer ones are a question for the call |

## Series C: documents (first gate)

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| licence | Licences, agreements or regulator correspondence | The licence or agreement held in each country served, or the regulator's correspondence on the application, and the compliance cost lines of the P&L. | — |
| risk_book_48m | Risk book over 48 months | Loan, transaction or policy book with losses, defaults, fraud and chargebacks, by vintage, month by month. | 48 months |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_c.json`) with the changes above; the deck never adjusts it.

## Series D: block Q. Licence and risk, weight 2 (brought by the model)

| # | Question | Found if | Note |
|---|---|---|---|
| Q1 | Which licences or agreements, held directly or through a partner, in each country served, since when? | The licence or the regulated partner named for each country in the P&L by geography, the regulator, and the date obtained; the licences or the partner contracts in the annexes | *proof*. A country served without its licence or partner = partial |
| Q2 | What does compliance cost, confirmed against the P&L and three years of audited accounts? | A monthly compliance cost (people, tools, audits) as a share of expenses, and the same lines in the P&L and in each of the last three fiscal years of audited accounts | *proof*. Benchmark shown next to the figure |
| Q3 | Credit or fraud risk: how is it underwritten and measured? | The underwriting or fraud rules, the denominator and the method of the loss rate, and who bears the loss (the company, a partner, an insurer) | *proof*. A 'low' risk without a method = absent |
| Q4 | Losses on the book over 60 months, by vintage? | Losses, defaults, fraud and chargebacks month by month over 60 months, by vintage, from the risk book | *proof*. A single annual loss rate = partial. Older vintages worse than newer ones are a question for the call |

## Series D: documents (first gate)

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| licence | Licences, agreements or regulator correspondence | The licence or agreement held in each country served, or the regulator's correspondence on the application, and the compliance cost lines of the P&L. | — |
| risk_book_60m | Risk book over 60 months | Loan, transaction or policy book with losses, defaults, fraud and chargebacks, by vintage, month by month. | 60 months |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_d.json`) with the changes above; the deck never adjusts it.

## Benchmarks (displayed, never scored)

Seed-stage fintech median net burn 120,000 USD per month, roughly 42 % above SaaS peers,
largely due to compliance and licensing (Qubit, 2026-01-02, citing icanpitch). 60 % of fintech
companies paid at least 250,000 USD in compliance fines in the past year (Qubit, 2025-12-11).
Credit or fraud loss rate, and compliance cost as a share of expenses at series A: no dated
source, left empty. Series B: the compliance fines figure (Qubit, 2025-12-11) is shown again;
compliance cost as a share of expenses and losses on the book have no dated source and stay
empty.

Series C: the compliance fines figure (Qubit, 2025-12-11) is shown again; compliance cost as a
share of expenses and losses on the book have no dated source and stay empty.

Series D: the compliance fines figure (Qubit, 2025-12-11) is shown again; compliance cost as a
share of expenses and losses on the book have no dated source and stay empty.

## Sources

- [Qubit Capital, Fintech Due Diligence Checklist](https://qubit.capital/blog/fintech-due-diligence-checklist), 2025-12-11
- [Qubit Capital, How Do Fintech Founders Manage Capital in 2026?](https://qubit.capital/blog/how-to-manage-fintech-capital-requirements), 2026-01-02
- [Mercury, Stage-based startup metrics that impact valuation](https://mercury.com/blog/stage-based-startup-metrics-valuation), 2026-01-12

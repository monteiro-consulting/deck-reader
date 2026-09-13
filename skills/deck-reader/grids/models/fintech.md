# Model block: Fintech

**Block version: 2026-09-13.** Readable copy of `scripts/grids/models/fintech.json`.

Money moves through the product, so a regulator, a partner bank and a loss rate sit between the
company and its revenue. The questions follow Qubit Capital's fintech due diligence checklist
and Mercury's stage-based metrics: licence or agreement, cost of compliance, credit or fraud
risk. They form the model's own block, weight 2.

| Stage | Remove | Reweight | Add |
|---|---|---|---|
| Seed | none | none | block Q (weight 2): Q1 to Q3 |
| Series A | none | none | block Q (weight 2): Q1 to Q3 |

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

## Benchmarks (displayed, never scored)

Seed-stage fintech median net burn 120,000 USD per month, roughly 42 % above SaaS peers,
largely due to compliance and licensing (Qubit, 2026-01-02, citing icanpitch). 60 % of fintech
companies paid at least 250,000 USD in compliance fines in the past year (Qubit, 2025-12-11).
Credit or fraud loss rate, and compliance cost as a share of expenses at series A: no dated
source, left empty.

## Sources

- [Qubit Capital, Fintech Due Diligence Checklist](https://qubit.capital/blog/fintech-due-diligence-checklist), 2025-12-11
- [Qubit Capital, How Do Fintech Founders Manage Capital in 2026?](https://qubit.capital/blog/how-to-manage-fintech-capital-requirements), 2026-01-02
- [Mercury, Stage-based startup metrics that impact valuation](https://mercury.com/blog/stage-based-startup-metrics-valuation), 2026-01-12

# Model block: SaaS

**Block version: 2026-09-14.** Readable copy of `scripts/grids/models/saas.json`.

The default model. The stage grids are written for it: no question is added, removed or
reweighted at seed, series A, series B or series C. Only the benchmarks apply
(`scripts/grids/benchmarks/saas.json`), displayed next to the deck figures, never in the score.

| Stage | Remove | Reweight | Add | Documents |
|---|---|---|---|---|
| Seed | none | none | none | none (no list at seed) |
| Series A | none | none | none | base list, unchanged |
| Series B | none | none | none | base list, unchanged |
| Series C | none | none | none | base list, unchanged |

## Series A: documents (first gate)

The document list is the base one of the series A grid: monthly P&L over 24 months, cohorts over 12 months or more, CRM export with weighted pipeline, cap table, three-year financial model, contracts of the top 10 customers. Nothing removed, nothing added.

## Series B: documents (first gate)

The document list is the base one of the series B grid: monthly P&L over 36 months, audited accounts for the last two fiscal years, cohorts by segment over 24 months, CRM export with weighted pipeline and win/loss, sales roster with quota attainment over 12 months, cap table, three-year financial model, contracts of the top 20 customers, board decks or minutes of the last four quarters, org chart and headcount history over 24 months. Nothing removed, nothing added.

## Series C: documents (first gate)

The document list is the base one of the series C grid: monthly P&L by product and by geography over 48 months, audited accounts with the auditor's opinion for the last three fiscal years, cohorts by segment and by acquisition year over 36 months, CRM export with weighted pipeline and win/loss, sales roster over 24 months, billing export with list and net price over 24 months, cap table with the terms of every round and any debt agreement, three-year financial model with a zero-burn scenario, contracts of the top 20 customers, board decks or minutes with budget vs actual for the last eight quarters, org chart and headcount history over 36 months. Nothing removed, nothing added.

## Benchmarks (displayed, never scored)

Seed: retention curve flattening from week 8, monthly logo churn 3 to 5 % below 1M USD ARR,
NRR median near 100 % (CRV, 2026); burn multiple above 3 read as high, 18 months of runway
(Mercury, 2026-01-12); LTV above 3x CAC and CAC recovered in under 12 months (Skok, undated).
Gross margin and sales cycle: no dated seed source, left empty.

Series A: ARR 2 to 5M USD, NRR 100 / 110-120 / 120+ %, burn multiple below 2 (CRV, 2026-03-31);
GRR high 80s to low 90s, CAC payback about 20 months, LTV:CAC 3:1 floor, one customer at 40 %
of ARR flagged (CRV, 2026-07-16); annual revenue churn median 12.5 % (CRV, 2026-06-19); growth
2 to 3x, gross margin 70 %+, LTV:CAC 4 to 6x (Initialized, 2021-06-29); growth 200 %, net
retention 140 %, gross margin 70 %, CAC payback 15 months at 1-10M USD ARR (Bessemer,
2021-09-21); burn multiple bands (Sacks, 2020-04-23); efficiency score good / better / best
(Bessemer, 2019-02-06); runway 9 to 12+ months, round about 20M USD (Burkland, 2026-07-21).
Sales cycle by segment, pipeline coverage, share of deals closed without a founder: no dated
source, left empty.

Series B: ARR growth 115 % / 95 % / 60 % average (medians 87 / 77 / 60 %), net retention
105-125 % (medians 117 / 120 / 120 %), gross margin 70 / 65 / 65 %, FCF margin medians -75 /
-62 / -37 % at 10-25 / 25-50 / 50-100M USD ARR (Bessemer, 2021-09-21); CAC payback around 20
months for private SaaS (CRV, 2026-07-16); Rule of 40 as growth plus profit (Feld, 2015-02-03)
and as ARR growth plus FCF margin (ICONIQ, 2025); magic number above 1x compelling, under 0.5x
not yet a model (Scale VP, 2010-04-20), 0.7x long-term median (Scale VP, 2020-09-11), net magic
number above 1.0x in the top quartile (ICONIQ, 2025); NDR 110-120 % (ICONIQ, 2025), public SaaS
110 % (High Alpha, 2024); burn multiple bands and trajectory (Sacks, 2020-04-23); efficiency
score (Bessemer, 2019-02-06). Quota attainment, rep ramp, win rate, series B round size: no
dated source, left empty.

Series C: ARR growth 60 % average at 50-100M and at 100M+ USD ARR (medians 60 and 57 %), net
retention median 120 % at both, gross margin median 70 %, FCF margin medians -37 and -35 %
(Bessemer, 2021-09-21); CAC payback around 20 months for private SaaS (CRV, 2026-07-16); Rule
of 40 (Feld, 2015-02-03; ICONIQ, 2025); NDR 110-120 % (ICONIQ, 2025), public SaaS 110 % (High
Alpha, 2024); magic number (Scale VP, 2010-04-20 and 2020-09-11); burn multiple bands and
trajectory (Sacks, 2020-04-23). Growth and FCF margin above 50M USD ARR on the ICONIQ 2025 and
High Alpha 2024 pages, plan attainment, discount trend, win rate trend, zero-burn growth, shares
of ARR from second products and from abroad, series C round size, exit comparables: no dated
source, left empty.

## Sources

- [CRV, Series A Metrics VCs Expect in 2026](https://www.crv.com/content/series-a-metrics-vcs-expect), 2026-03-31
- [Bessemer, Scaling to $100 Million](https://www.bvp.com/atlas/scaling-to-100-million), 2021-09-21
- [Initialized, The Metrics You Need To Raise a Series A](https://blog.initialized.com/2021/06/the-metrics-you-need-to-raise-a-series-a/), 2021-06-29
- [Brad Feld, The Rule of 40% For a Healthy SaaS Company](https://feld.com/archives/2015/02/rule-40-healthy-saas-company/), 2015-02-03
- [Scale Venture Partners, Magic Number Math](https://www.scalevp.com/insights/magic-number-math/), 2010-04-20, and [A History of the Magic Number](https://www.scalevp.com/blog/saas-metrics-a-history-of-the-magic-number), 2020-09-11
- [ICONIQ Growth, State of Software 2025](https://www.iconiq.com/growth/reports/2025-state-of-software) and [The ICONIQ Enterprise Five](https://www.iconiq.com/growth/reports/the-iconiq-enterprise-five), 2025
- [High Alpha, 2024 SaaS Benchmarks Report](https://www.highalpha.com/saas-benchmarks/2024), 2024

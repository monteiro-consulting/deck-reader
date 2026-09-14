# Model block: Marketplace

**Block version: 2026-09-14.** Readable copy of `scripts/grids/models/marketplace.json`.

The company matches supply and demand and takes a share of transactions. Revenue is the take
rate on GMV, and both sides must come back. The questions follow a16z's 13 marketplace metrics
and are appended to the traction block with its weight.

| Stage | Remove | Reweight | Add | Documents |
|---|---|---|---|---|
| Seed | none | none | M1 to M4 in block B | none (no list at seed) |
| Series A | none | none | M1 to M5 in block B | add gmv_24m |
| Series B | none | none | M1 to M4 in block B | add gmv_36m |
| Series C | none | none | M1 to M4 in block B | add gmv_48m |
| Series D | none | none | M1 to M4 in block B | add gmv_60m |

## Seed: added to block B (weight 3)

| # | Question | Found if | Note |
|---|---|---|---|
| M1 | Gross merchandise value and take rate? | Both figures, and the net revenue that follows from them | *proof*. From a16z's marketplace metrics |
| M2 | Match rate and time to match? | Share of requests served, and the delay | *proof* |
| M3 | Concentration? | Share of volume made by the top 10 sellers or buyers | *proof* |
| M4 | Do both sides come back? | Retention figures for supply and demand, separately | *proof* |

## Series A: added to block B (weight 2)

| # | Question | Found if | Note |
|---|---|---|---|
| M1 | Gross merchandise value, take rate, and the net revenue over 24 months? | GMV and take rate, and the monthly net revenue over 24 months that follows from them, matching the P&L | *proof*. Benchmark shown next to the figure |
| M2 | Match rate and time to match, by market? | Share of requests served and the delay, for the oldest market and the newest | *proof*. Older markets should match faster |
| M3 | Concentration of supply and demand? | Share of GMV made by the top 10 sellers and by the top 10 buyers, separately | *proof* |
| M4 | Do both sides come back? | Retention cohorts for supply and for demand, separately, over twelve months or more | *proof* |
| M5 | GMV retention by cohort? | The share of each cohort's spend retained month after month, supply and demand separately | *proof*. From a16z's GMV retention note |

## Series A: documents (first gate)

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| gmv_24m | Monthly GMV by side over 24 months | GMV, take rate, and active supply and demand counts, month by month. | 24 months |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_a.json`) with the changes above; the deck never adjusts it.

## Series B: added to block B (weight 2)

| # | Question | Found if | Note |
|---|---|---|---|
| M1 | Gross merchandise value and take rate over 36 months, and the net revenue that follows? | Monthly GMV and take rate over 36 months, and the net revenue that follows from them, matching the P&L and the audited accounts | *proof*. From a16z's marketplace metrics. Benchmark shown next to the figure |
| M2 | Do both sides come back, market by market? | Retention cohorts for supply and for demand, separately, over 24 months or more, for the oldest market and the newest | *proof*. One side retained and not the other = partial |
| M3 | Concentration of the top twenty sellers and the top twenty buyers? | Share of GMV made by the top twenty sellers and by the top twenty buyers, separately, confirmed against the GMV export | *proof* |
| M4 | GMV retention by cohort and by side? | The share of each cohort's spend retained month after month, supply and demand separately, over 24 months or more | *proof*. From a16z's GMV retention note. Benchmark shown next to the figure |

## Series B: documents (first gate)

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| gmv_36m | Monthly GMV by side over 36 months | GMV, take rate, and active supply and demand counts, month by month. | 36 months |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_b.json`) with the changes above; the deck never adjusts it.

## Series C: added to block B (weight 2)

| # | Question | Found if | Note |
|---|---|---|---|
| M1 | Gross merchandise value and take rate over 48 months, and the net revenue that follows? | Monthly GMV and take rate over 48 months, and the net revenue that follows from them, matching the P&L and three years of audited accounts | *proof*. From a16z's marketplace metrics. Benchmark shown next to the figure |
| M2 | Do both sides come back, market by market and cohort vintage by cohort vintage? | Retention cohorts for supply and for demand, separately, over 36 months or more, by market and by acquisition year | *proof*. One side retained and not the other = partial. Older cohorts below newer ones are a question for the call |
| M3 | Concentration of the top twenty sellers and the top twenty buyers, and its trend over 24 months? | Share of GMV made by the top twenty sellers and by the top twenty buyers, separately, today and 24 months ago, confirmed against the GMV export | *proof* |
| M4 | GMV retention by cohort vintage and by side? | The share of each cohort's spend retained month after month, supply and demand separately, over 36 months or more, by acquisition year | *proof*. From a16z's GMV retention note. Benchmark shown next to the figure |

## Series C: documents (first gate)

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| gmv_48m | Monthly GMV by side over 48 months | GMV, take rate, and active supply and demand counts, by market, month by month. | 48 months |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_c.json`) with the changes above; the deck never adjusts it.

## Series D: added to block B (weight 2)

| # | Question | Found if | Note |
|---|---|---|---|
| M1 | Gross merchandise value and take rate over 60 months, and the net revenue that follows? | Monthly GMV and take rate over 60 months, and the net revenue that follows from them, matching the P&L and three years of audited accounts | *proof*. From a16z's marketplace metrics. Benchmark shown next to the figure |
| M2 | Do both sides come back, market by market and cohort vintage by cohort vintage? | Retention cohorts for supply and for demand, separately, over 48 months or more, by market and by acquisition year | *proof*. One side retained and not the other = partial. Older cohorts below newer ones are a question for the call |
| M3 | Concentration of the top twenty sellers and the top twenty buyers, and its trend over 36 months? | Share of GMV made by the top twenty sellers and by the top twenty buyers, separately, today and 36 months ago, confirmed against the GMV export | *proof* |
| M4 | GMV retention by cohort vintage and by side? | The share of each cohort's spend retained month after month, supply and demand separately, over 48 months or more, by acquisition year | *proof*. From a16z's GMV retention note. Benchmark shown next to the figure |

## Series D: documents (first gate)

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| gmv_60m | Monthly GMV by side over 60 months | GMV, take rate, and active supply and demand counts, by market, month by month. | 60 months |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_d.json`) with the changes above; the deck never adjusts it.

## Benchmarks (displayed, never scored)

Supply-side GMV retention: average 80 to 95 % in the first three months, plateau around 45 to
50 % by month 12, best-in-class at or above 100 % (a16z, 2022-04-28). Series A: net revenue
run-rate 2M USD+, GMV 5 to 7M USD+, take rate 10 to 30 %, GMV growth 5x, gross margin 50 to
60 % (Initialized, 2021-06-29). Match rate, time to match and concentration: a16z defines the
metrics without thresholds (2020-02-21); left empty. Seed take rate: no dated source, left empty.
Series B: the GMV retention curve (a16z, 2022-04-28) and the concentration definition (a16z,
2020-02-21) are shown again; take rate and GMV growth at series B have no dated source and stay
empty. The stage-generic benchmarks of the SaaS file (burn multiple, efficiency score) are
shown as well.

Series C: the GMV retention curve (a16z, 2022-04-28) and the concentration definition (a16z,
2020-02-21) are shown again; take rate and GMV growth at series C have no dated source and stay
empty. The stage-generic benchmarks of the SaaS file (burn multiple, exit comparables) are shown
as well.

Series D: the GMV retention curve (a16z, 2022-04-28) and the concentration definition (a16z,
2020-02-21) are shown again; take rate and GMV growth at series D have no dated source and stay
empty. The stage-generic benchmarks of the SaaS file (burn multiple, round size, exit comparables
and the IPO filings of the category) are shown as well.

## Sources

- [a16z, 13 Metrics for Marketplace Companies](https://a16z.com/13-metrics-for-marketplace-companies/), 2020-02-21
- [a16z, GMV Retention: The Marketplace Metric Most Ignore](https://a16z.com/gmv-retention-the-marketplace-metric-most-ignore/), 2022-04-28
- [Initialized, The Metrics You Need To Raise a Series A](https://blog.initialized.com/2021/06/the-metrics-you-need-to-raise-a-series-a/), 2021-06-29

# Model block: Marketplace

**Block version: 2026-09-13.** Readable copy of `scripts/grids/models/marketplace.json`.

The company matches supply and demand and takes a share of transactions. Revenue is the take
rate on GMV, and both sides must come back. The questions follow a16z's 13 marketplace metrics
and are appended to the traction block with its weight.

| Stage | Remove | Reweight | Add |
|---|---|---|---|
| Seed | none | none | M1 to M4 in block B |
| Series A | none | none | M1 to M5 in block B |

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

## Benchmarks (displayed, never scored)

Supply-side GMV retention: average 80 to 95 % in the first three months, plateau around 45 to
50 % by month 12, best-in-class at or above 100 % (a16z, 2022-04-28). Series A: net revenue
run-rate 2M USD+, GMV 5 to 7M USD+, take rate 10 to 30 %, GMV growth 5x, gross margin 50 to
60 % (Initialized, 2021-06-29). Match rate, time to match and concentration: a16z defines the
metrics without thresholds (2020-02-21); left empty. Seed take rate: no dated source, left empty.

## Sources

- [a16z, 13 Metrics for Marketplace Companies](https://a16z.com/13-metrics-for-marketplace-companies/), 2020-02-21
- [a16z, GMV Retention: The Marketplace Metric Most Ignore](https://a16z.com/gmv-retention-the-marketplace-metric-most-ignore/), 2022-04-28
- [Initialized, The Metrics You Need To Raise a Series A](https://blog.initialized.com/2021/06/the-metrics-you-need-to-raise-a-series-a/), 2021-06-29

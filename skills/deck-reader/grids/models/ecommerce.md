# Model block: E-commerce and D2C

**Block version: 2026-09-13.** Readable copy of `scripts/grids/models/ecommerce.json`.

Physical goods sold online. The order is the unit: what is left after goods, shipping, returns
and marketing, and whether the customer orders again. The questions follow Daasity's ten D2C
metrics and Fairview's D2C unit economics; the generic CAC and the sales cycle are replaced.

| Stage | Remove | Reweight | Add |
|---|---|---|---|
| Seed | C4 (sales cycle) | none | O1, O2 in block C; O3 in block B |
| Series A | C2 (generic CAC), C3 (sales cycle) | none | O1, O2 in block C; O3 in block D |

## Seed

Added to block C (weight 3):

| # | Question | Found if | Note |
|---|---|---|---|
| O1 | Contribution margin per order, after shipping and returns? | Net sales per order minus goods, shipping, payment fees, returns and refunds, with each line visible | *proof*. A gross margin that stops at the goods = partial |
| O2 | Customer acquisition cost by channel? | A CAC per channel, paid and blended, with the spend and the orders behind it | *proof*. A blended CAC alone = partial |

Added to block B (weight 3):

| # | Question | Found if | Note |
|---|---|---|---|
| O3 | What share of customers order again within 60 days? | A 60-day repeat purchase rate by acquisition cohort | *proof*. Benchmark shown next to the figure |

## Series A

Added to block C (weight 3):

| # | Question | Found if | Note |
|---|---|---|---|
| O1 | Contribution margin per order, after shipping and returns, over 24 months? | Net sales per order minus goods, shipping, payment fees, returns and refunds, month by month, matching the P&L | *proof*. A gross margin that stops at the goods = partial |
| O2 | Customer acquisition cost by channel, paid and blended, and payback? | A CAC per channel, paid and blended, the spend and the orders behind it, and the months of contribution margin needed to recover it | *proof*. A blended CAC alone = partial |

Added to block D (weight 3):

| # | Question | Found if | Note |
|---|---|---|---|
| O3 | What share of customers order again within 60 days, cohort by cohort? | A 60-day repeat purchase rate by monthly acquisition cohort over twelve months or more | *proof*. Benchmark shown next to the figure |

## Benchmarks (displayed, never scored)

Contribution margin median 22 % in 2025, down from 35 % in 2021; 60-day repeat rate strong
20 to 35 %, average 10 to 20 %, weak below 10 %; return rate apparel 20 to 35 %, consumables
2 to 6 %; paid CAC 15 to 40 USD for consumables; returning-customer ROAS 3 to 8x (Fairview,
2026). LTV/CAC 4:1 healthy, 6:1 or 7:1 may mean underinvestment (Daasity, 2022-03-30). Series
A: revenue 500K to 2M USD, growth 2 to 3x, AOV 150 to 300 USD+, gross margin 25 % minimum and
above 50 % good, LTV/CAC above 3x (Initialized, 2021-06-29). CAC payback in months: no dated
source confirmed on the page, left empty.

## Sources

- [Daasity, 10 Metrics D2C Investors Care About the Most](https://www.daasity.com/post/10-metrics-d2c-investors-care-about-the-most), 2022-03-30
- [Fairview, D2C Metrics 2026: CAC, LTV, ROAS & Contribution Margin](https://getfairview.com/d2c-metrics), 2026
- [Initialized, The Metrics You Need To Raise a Series A (D2C section)](https://blog.initialized.com/2021/06/the-metrics-you-need-to-raise-a-series-a/), 2021-06-29

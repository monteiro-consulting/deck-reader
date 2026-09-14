# Model block: E-commerce and D2C

**Block version: 2026-09-14.** Readable copy of `scripts/grids/models/ecommerce.json`.

Physical goods sold online. The order is the unit: what is left after goods, shipping, returns
and marketing, and whether the customer orders again. The questions follow Daasity's ten D2C
metrics and Fairview's D2C unit economics; the generic CAC and the sales cycle are replaced.

| Stage | Remove | Reweight | Add | Documents |
|---|---|---|---|---|
| Seed | C4 (sales cycle) | none | O1, O2 in block C; O3 in block B | none (no list at seed) |
| Series A | C2 (generic CAC), C3 (sales cycle) | none | O1, O2 in block C; O3 in block D | remove crm_pipeline, top10_contracts; add orders_export_24m |
| Series B | C5 (magic number), C6 (pipeline), D4, D5, D6 (sales team) | none | O1, O2 in block C; O3 in block E | remove crm_pipeline, sales_roster, top20_contracts; add orders_export_36m |

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

## Series A: documents (first gate)

Removed from the base list: `crm_pipeline` (CRM export with weighted pipeline), `top10_contracts` (Contracts of the top 10 customers).

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| orders_export_24m | Orders export over 24 months | Every order with revenue, cost of goods, shipping, returns, and marketing spend by channel, month by month. | 24 months |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_a.json`) with the changes above; the deck never adjusts it.

## Series B

Added to block C (weight 3):

| # | Question | Found if | Note |
|---|---|---|---|
| O1 | Contribution margin per order, after shipping and returns, over 36 months? | Net sales per order minus goods, shipping, payment fees, returns and refunds, month by month over 36 months, matching the P&L and the audited accounts | *proof*. A gross margin that stops at the goods = partial |
| O2 | Customer acquisition cost by channel, paid and blended, and its payback? | A CAC per channel, paid and blended, the spend and the orders behind it, and the months of contribution margin needed to recover it, from the orders export | *proof*. A blended CAC alone = partial |

Added to block E (weight 2):

| # | Question | Found if | Note |
|---|---|---|---|
| O3 | What share of customers order again within 60 days, cohort by cohort? | A 60-day repeat purchase rate by monthly acquisition cohort over 24 months or more | *proof*. Benchmark shown next to the figure |

The generic CAC payback question (C2) stays at series B, as the series B design says: O2 reads
the CAC per order from the orders export, C2 reads the payback by channel and by segment and its
trend from the P&L.

## Series B: documents (first gate)

Removed from the base list: `crm_pipeline` (CRM export with weighted pipeline and win/loss), `sales_roster` (Sales team roster with quota attainment), `top20_contracts` (Contracts of the top 20 customers).

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| orders_export_36m | Orders export over 36 months | Every order with revenue, cost of goods, shipping, returns, and marketing spend by channel, month by month. | 36 months |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_b.json`) with the changes above; the deck never adjusts it.

## Benchmarks (displayed, never scored)

Contribution margin median 22 % in 2025, down from 35 % in 2021; 60-day repeat rate strong
20 to 35 %, average 10 to 20 %, weak below 10 %; return rate apparel 20 to 35 %, consumables
2 to 6 %; paid CAC 15 to 40 USD for consumables; returning-customer ROAS 3 to 8x (Fairview,
2026). LTV/CAC 4:1 healthy, 6:1 or 7:1 may mean underinvestment (Daasity, 2022-03-30). Series
A: revenue 500K to 2M USD, growth 2 to 3x, AOV 150 to 300 USD+, gross margin 25 % minimum and
above 50 % good, LTV/CAC above 3x (Initialized, 2021-06-29). CAC payback in months: no dated
source confirmed on the page, left empty. Series B: the Fairview (2026) and Daasity (2022-03-30)
figures are shown again, none being stage-specific; revenue, growth and CAC payback at series B
have no dated source and stay empty.

## Sources

- [Daasity, 10 Metrics D2C Investors Care About the Most](https://www.daasity.com/post/10-metrics-d2c-investors-care-about-the-most), 2022-03-30
- [Fairview, D2C Metrics 2026: CAC, LTV, ROAS & Contribution Margin](https://getfairview.com/d2c-metrics), 2026
- [Initialized, The Metrics You Need To Raise a Series A (D2C section)](https://blog.initialized.com/2021/06/the-metrics-you-need-to-raise-a-series-a/), 2021-06-29

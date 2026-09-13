# Model block: Consumer

**Block version: 2026-09-13.** Readable copy of `scripts/grids/models/consumer.json`.

Many users, small or no payments, growth carried by habit and word of mouth. The evidence is
engagement and cohort retention, not revenue. The questions follow a16z's consumer benchmarks
and Andrew Chen's magic metrics; revenue questions lose weight, the sales cycle disappears.

| Stage | Remove | Reweight | Add |
|---|---|---|---|
| Seed | C4 (sales cycle) | B2 (monthly revenue) to weight 1 | N1 to N3 in block B |
| Series A | B2 (ACV by segment), C3 (sales cycle) | B1 (ARR) to weight 1 | N1 to N3 in block B |

## Seed: added to block B (weight 3)

| # | Question | Found if | Note |
|---|---|---|---|
| N1 | Daily active users over monthly active users? | Both counts with the definition of 'active', and the ratio, from an analytics export | *proof*. Benchmark shown next to the figure |
| N2 | Do the cohort curves flatten? | Day 1, 7 and 30 retention by cohort, with the day where the curve flattens | *proof*. A curve that still falls at day 30 = partial |
| N3 | What share of new users is organic? | The share of new users from organic, referral or word of mouth, with the method | *proof*. All paid = partial |

## Series A: added to block B (weight 2)

| # | Question | Found if | Note |
|---|---|---|---|
| N1 | Daily active users over monthly active users, over 24 months? | Both counts with the definition of 'active', and the monthly ratio over 24 months, from an analytics export | *proof*. Benchmark shown next to the figure |
| N2 | Do the cohort curves flatten, and do newer cohorts do better? | Day 1, 7 and 30 retention by monthly cohort over twelve months or more, with the day where the curves flatten | *proof*. A curve that still falls at day 30 = partial |
| N3 | What share of new users is organic, and what is the paid CAC? | The share of new users from organic, referral or word of mouth, and the cost per paid user, with the method | *proof*. All paid = partial |

## Benchmarks (displayed, never scored)

Social apps (a16z, 2023-03-03): DAU/MAU ok 25 / good 40 / great 50 %+; day 1/7/30 retention
ok 50/35/20, good 60/40/25, great 70/50/30 %; week 1/4 ok 40/20, good 55/30, great 75/50 %;
monthly growth ok 20 / good 35 / great 50 %; organic 80 to 90 %+ of growth; the curve flattens
between day 7 and 14. Consumer in general (Andrew Chen, 2019-10-15): DAU/MAU above 50 %, day
1/7/30 above 60/30/15 %, above 60 % organic, actives over registered above 25 %, subscription
annual retention above 65 %, above 4x annual growth. Paid CAC: no dated source, left empty.

## Sources

- [a16z (Bryan Kim), Do You Have Lightning In a Bottle? How to Benchmark Your Social App](https://a16z.com/do-you-have-lightning-in-a-bottle-how-to-benchmark-your-social-app/), 2023-03-03
- [Andrew Chen (a16z), magic metrics indicating a startup probably has product/market fit](https://x.com/andrewchen/status/1184170125525577728), 2019-10-15
- [a16z, 16 Startup Metrics](https://a16z.com/16-startup-metrics/), 2015-08-21

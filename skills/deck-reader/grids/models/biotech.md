# Model block: Biotech

**Block version: 2026-09-13.** Readable copy of `scripts/grids/models/biotech.json`.

No customer, no revenue, no retention for years: the evidence is scientific and regulatory
progress. The questions follow Mercury's guide to biotech investors: milestones reached,
intellectual property, regulatory path. Traction and retention are asked for information only
(weight 0), unit economics drops to 1, the sales cycle disappears, and the model's own block
counts 3.

| Stage | Remove | Reweight | Add |
|---|---|---|---|
| Seed | C4 (sales cycle) | block B to 0, block C to 1 | block R (weight 3): R1 to R3 |
| Series A | C3 (sales cycle) | blocks B and D to 0, block C to 1 | block R (weight 3): R1 to R3 |

## Seed: block R. Science and regulation, weight 3 (brought by the model)

| # | Question | Found if | Note |
|---|---|---|---|
| R1 | Which preclinical or clinical milestones were reached, when? | Each milestone named (in vitro, in vivo, tox, IND or CTA filing, phase) with its date and the data behind it | A milestone 'expected' is not a milestone reached |
| R2 | What intellectual property, filed or granted, and who owns it? | Patent numbers or filing dates, the owner (company, university, licence), and the licence terms if any | 'Patent pending' without a filing date = partial |
| R3 | Which regulatory path, and what is the next step with its date? | The agency and route named (FDA, EMA; IND, 510(k), CE...), the designations obtained, and the next filing with its date | |

## Series A: block R. Science and regulation, weight 3 (brought by the model)

| # | Question | Found if | Note |
|---|---|---|---|
| R1 | Which preclinical or clinical milestones were reached since the seed, when, with what data? | Each milestone named (tox, IND or CTA filing, phase 1 readout...) with its date and the data behind it | A milestone 'expected' is not a milestone reached |
| R2 | What intellectual property, filed or granted, in which territories, and who owns it? | Patent numbers or filing dates per territory, the owner (company, university, licence), and the licence terms if any | 'Patent pending' without a filing date = partial |
| R3 | Which regulatory path, which designations, and what does this round fund up to? | The agency and route named, the designations obtained, and the milestone the round funds, with its date, consistent with the financial model | |

## Benchmarks (displayed, never scored)

Biotech has no revenue benchmark. What is shown is what investors read instead: preclinical
validation, regulatory filings, clinical trial data, manufacturing readiness, commercial
approvals; runway planned to the next development milestone (Mercury, 2026-08-25), qualitative.
Patent coverage and clinical phase durations: no source from the required list, left empty.

## Sources

- [Mercury, A guide to the top biotech and life sciences VC firms for startups](https://mercury.com/blog/top-biotech-life-sciences-vc-firms), 2026-08-25
- [Mercury, Stage-based startup metrics that impact valuation](https://mercury.com/blog/stage-based-startup-metrics-valuation), 2026-01-12

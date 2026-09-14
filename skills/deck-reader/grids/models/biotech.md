# Model block: Biotech

**Block version: 2026-09-14.** Readable copy of `scripts/grids/models/biotech.json`.

No customer, no revenue, no retention for years: the evidence is scientific and regulatory
progress. The questions follow Mercury's guide to biotech investors: milestones reached,
intellectual property, regulatory path. Traction and retention are asked for information only
(weight 0), unit economics drops to 1, the sales cycle disappears, and the model's own block
counts 3.

| Stage | Remove | Reweight | Add | Documents |
|---|---|---|---|---|
| Seed | C4 (sales cycle) | block B to 0, block C to 1 | block R (weight 3): R1 to R3 | none (no list at seed) |
| Series A | C3 (sales cycle) | blocks B and D to 0, block C to 1 | block R (weight 3): R1 to R3 | remove cohorts_12m, crm_pipeline, top10_contracts; add clinical_dossier, ip_schedule |
| Series B | C5 (magic number), C6 (pipeline), D4, D5, D6 (sales team) | blocks B, D and E to 0, block C to 1 | block R (weight 3): R1 to R3 | remove cohorts_24m, crm_pipeline, sales_roster, top20_contracts; add clinical_dossier, ip_schedule |
| Series C | C5 (magic number), D2 (pricing power), D3 (win rate trend), D6 (deals without a founder) | blocks B, D and E to 0, block C to 1 | block R (weight 3): R1 to R3 | remove cohorts_36m, crm_pipeline, sales_roster, billing_export_24m, top20_contracts; add clinical_dossier, ip_schedule |

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

## Series A: documents (first gate)

Removed from the base list: `cohorts_12m` (Cohorts over 12 months or more), `crm_pipeline` (CRM export with weighted pipeline), `top10_contracts` (Contracts of the top 10 customers).

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| clinical_dossier | Preclinical or clinical data package | Protocols, results and the regulator's correspondence (FDA, EMA or equivalent) for each milestone the deck claims. | — |
| ip_schedule | Patent schedule | Every patent filing with its status, jurisdictions, and who owns it. | — |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_a.json`) with the changes above; the deck never adjusts it.

## Series B: block R. Science and regulation, weight 3 (brought by the model)

| # | Question | Found if | Note |
|---|---|---|---|
| R1 | Which preclinical or clinical milestones were reached since the series A, when, with what data? | Each milestone named (phase 1 or 2 readout, pivotal study start, regulator meeting...) with its date and the data behind it, in the clinical data package | *proof*. A milestone 'expected' is not a milestone reached |
| R2 | What intellectual property, filed or granted, in which territories, and who owns it? | Patent numbers or filing dates per territory, the owner (company, university, licence), and the licence terms if any, in the patent schedule | *proof*. 'Patent pending' without a filing date = partial |
| R3 | Which regulatory path, which designations, and what does this round fund up to? | The agency and route named, the designations obtained, and the milestone the round funds, with its date, consistent with the financial model | *proof* |

At series B the block also removes the magic number (C5) and the pipeline coverage (C6): with no
sales team and no revenue plan to cover, both would be answered "absent" for information only
and add nothing the repeatability block does not already ask for at weight 0.

## Series B: documents (first gate)

Removed from the base list: `cohorts_24m` (Cohorts by segment over 24 months or more), `crm_pipeline` (CRM export with weighted pipeline and win/loss), `sales_roster` (Sales team roster with quota attainment), `top20_contracts` (Contracts of the top 20 customers).

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| clinical_dossier | Preclinical or clinical data package | Protocols, results and the regulator's correspondence (FDA, EMA or equivalent) for each milestone the deck claims. | — |
| ip_schedule | Patent schedule | Every patent filing with its status, jurisdictions, and who owns it. | — |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_b.json`) with the changes above; the deck never adjusts it.

## Series C: block R. Science and regulation, weight 3 (brought by the model)

| # | Question | Found if | Note |
|---|---|---|---|
| R1 | Which clinical milestones were reached since the series B, when, with what data? | Each milestone named (phase 2 or 3 readout, pivotal study, filing, regulator meeting...) with its date and the data behind it, in the clinical data package, next to the milestones the series B round was meant to fund | *proof*. A milestone 'expected' is not a milestone reached |
| R2 | What intellectual property, filed or granted, in which territories, and who owns it? | Patent numbers or filing dates per territory, the owner (company, university, licence), and the licence terms if any, in the patent schedule | *proof*. 'Patent pending' without a filing date = partial |
| R3 | Which regulatory path, which designations, and what does this round fund up to? | The agency and route named, the designations obtained, and the milestone the round funds, with its date, consistent with the financial model | *proof* |

At series C the block also removes pricing power (D2), the win rate trend (D3) and the deals
signed without a founder (D6): with no billing export, no CRM and no sales team on the list, they
would be answered "absent" for information only. Position and durability stays at weight 0, for
information: the plan against actual of the board packs (D1) is still asked, and R1 reads the
same promise against the milestones.

## Series C: documents (first gate)

Removed from the base list: `cohorts_36m` (Cohorts by segment and by acquisition year over 36 months or more), `crm_pipeline` (CRM export with weighted pipeline, owner, and win/loss with competitor), `sales_roster` (Sales roster with quota attainment over 24 months), `billing_export_24m` (Billing export with list price, net price and discount over 24 months), `top20_contracts` (Signed contracts of the top 20 customers).

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| clinical_dossier | Preclinical or clinical data package | Protocols, results and the regulator's correspondence (FDA, EMA or equivalent) for each milestone the deck claims. | — |
| ip_schedule | Patent schedule | Every patent filing with its status, jurisdictions, and who owns it. | — |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_c.json`) with the changes above; the deck never adjusts it.

## Benchmarks (displayed, never scored)

Biotech has no revenue benchmark. What is shown is what investors read instead: preclinical
validation, regulatory filings, clinical trial data, manufacturing readiness, commercial
approvals; runway planned to the next development milestone (Mercury, 2026-08-25), qualitative.
Patent coverage and clinical phase durations: no source from the required list, left empty.
The same Mercury reading is shown at series B, next to R1, R3, H3 and C7.

Series C: the same Mercury reading is shown again, next to R1, R3, H3 and C8; patent coverage
and clinical phase durations stay empty.

## Sources

- [Mercury, A guide to the top biotech and life sciences VC firms for startups](https://mercury.com/blog/top-biotech-life-sciences-vc-firms), 2026-08-25
- [Mercury, Stage-based startup metrics that impact valuation](https://mercury.com/blog/stage-based-startup-metrics-valuation), 2026-01-12

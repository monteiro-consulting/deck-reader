# Model block: Hardware

**Block version: 2026-09-13.** Readable copy of `scripts/grids/models/hardware.json`.

A physical product that must be built, shipped and supported. Margin depends on volume, and
volume depends on suppliers. The questions follow SeriesOps' note on hardware gross margin: the
deck must show the margin at 1,000, 10,000 and 100,000 units, the bill of materials, and the
minimum order quantities. The economics block counts double.

| Stage | Remove | Reweight | Add |
|---|---|---|---|
| Seed | none | block C to weight 6 | P1 to P3 in block C |
| Series A | none | block C to weight 6 | P1 to P3 in block C |

## Seed: added to block C (weight 6)

| # | Question | Found if | Note |
|---|---|---|---|
| P1 | Gross margin at 1,000, 10,000 and 100,000 units? | A margin per unit at each of the three volumes, with the cost lines that change between them | *proof*. A single margin figure without volume = partial |
| P2 | Bill of materials with the cost per unit? | The main components with their unit cost, and the total landed cost per unit | *proof*. A total without the lines = partial |
| P3 | Minimum order quantities and supplier terms? | The MOQ of the critical components or of the contract manufacturer, and the payment terms | *proof* |

## Series A: added to block C (weight 6)

| # | Question | Found if | Note |
|---|---|---|---|
| P1 | Gross margin at 1,000, 10,000 and 100,000 units, and the margin actually realized in the P&L? | A margin per unit at each of the three volumes, and the realized margin over the last twelve months in the P&L | *proof*. A single margin figure without volume = partial |
| P2 | Bill of materials with the cost per unit, and how it moved over 24 months? | The main components with their unit cost, the total landed cost per unit, and its curve over 24 months | *proof*. A total without the lines = partial |
| P3 | Minimum order quantities, supplier terms, and the inventory they impose? | The MOQ of the critical components or of the contract manufacturer, the payment terms, and the inventory in the financial model | *proof* |

## Benchmarks (displayed, never scored)

Public comparables only: Cisco about 65 %, Garmin about 58 %, Sonos mid-40s, Apple hardware
about 37 %, GoPro mid-30s, Dell low 20s; margins become critical at series B, not at seed; the
model should show 1,000 versus 10,000 versus 100,000 units (SeriesOps, 2026-01-17). BOM share
of price and typical MOQs: no dated source, left empty. The stage-generic benchmarks of the SaaS
file (burn multiple, runway, round size) are shown as well.

## Sources

- [SeriesOps, Gross Margin for Hardware Startups: What's Actually Good at Seed Stage?](https://seriesops.com/insights/gross-margin-hardware-startups), 2026-01-17
- [Burkland, How Investors Evaluate Series A Startups in 2026](https://burklandassociates.com/2026/07/21/how-investors-evaluate-series-a-startups-in-2026/), 2026-07-21

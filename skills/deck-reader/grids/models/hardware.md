# Model block: Hardware

**Block version: 2026-09-14.** Readable copy of `scripts/grids/models/hardware.json`.

A physical product that must be built, shipped and supported. Margin depends on volume, and
volume depends on suppliers. The questions follow SeriesOps' note on hardware gross margin: the
deck must show the margin at 1,000, 10,000 and 100,000 units, the bill of materials, and the
minimum order quantities. The economics block counts double.

| Stage | Remove | Reweight | Add | Documents |
|---|---|---|---|---|
| Seed | none | block C to weight 6 | P1 to P3 in block C | none (no list at seed) |
| Series A | none | block C to weight 6 | P1 to P3 in block C | add bom_and_suppliers |
| Series B | none | block C to weight 6 | P1 to P3 in block C | add bom_and_suppliers, inventory_24m |
| Series C | none | block C to weight 6 | P1 to P3 in block C | add bom_and_suppliers, inventory_36m |

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

## Series A: documents (first gate)

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| bom_and_suppliers | Bill of materials and supplier terms | The BOM with the unit cost per component and the landed cost per unit, and the supplier contracts or quotes with minimum order quantities and payment terms. | — |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_a.json`) with the changes above; the deck never adjusts it.

## Series B: added to block C (weight 6)

| # | Question | Found if | Note |
|---|---|---|---|
| P1 | Gross margin at 1,000, 10,000 and 100,000 units, and the margin realized in the audited accounts? | A margin per unit at each of the three volumes, and the realized margin of each of the last two fiscal years in the audited accounts | *proof*. A single margin figure without volume = partial |
| P2 | Bill of materials with the cost per unit, and its curve over 36 months? | The main components with their unit cost, the total landed cost per unit, and its curve over 36 months | *proof*. A total without the lines = partial |
| P3 | Minimum order quantities, supplier terms, inventory and warranty? | The MOQ of the critical components or of the contract manufacturer, the payment terms, the inventory month by month, and the warranty claims and returns by month | *proof*. Inventory or warranty missing = partial |

## Series B: documents (first gate)

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| bom_and_suppliers | Bill of materials and supplier terms | The BOM with the unit cost per component and the landed cost per unit, and the supplier contracts or quotes with minimum order quantities and payment terms. | — |
| inventory_24m | Inventory, warranty claims and returns over 24 months | Inventory, warranty claims and returns, month by month. | 24 months |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_b.json`) with the changes above; the deck never adjusts it.

## Series C: added to block C (weight 6)

| # | Question | Found if | Note |
|---|---|---|---|
| P1 | Gross margin at 1,000, 10,000 and 100,000 units, and the margin realized in three years of audited accounts? | A margin per unit at each of the three volumes, and the realized margin of each of the last three fiscal years in the audited accounts | *proof*. A single margin figure without volume = partial |
| P2 | Bill of materials with the cost per unit, and its curve over 48 months? | The main components with their unit cost, the total landed cost per unit, and its curve over 48 months | *proof*. A total without the lines = partial |
| P3 | Minimum order quantities, supplier terms, inventory and warranty over 36 months? | The MOQ of the critical components or of the contract manufacturer, the payment terms, the inventory month by month, and the warranty claims and returns by month over 36 months | *proof*. Inventory or warranty missing = partial |

## Series C: documents (first gate)

| Id | Document | Requirement | Minimum |
|---|---|---|---|
| bom_and_suppliers | Bill of materials and supplier terms | The BOM with the unit cost per component and the landed cost per unit, and the supplier contracts or quotes with minimum order quantities and payment terms. | — |
| inventory_36m | Inventory, warranty claims and returns over 36 months | Inventory, warranty claims and returns, month by month. | 36 months |

The document list of the first gate is the one of the stage grid (`scripts/grids/series_c.json`) with the changes above; the deck never adjusts it.

## Benchmarks (displayed, never scored)

Public comparables only: Cisco about 65 %, Garmin about 58 %, Sonos mid-40s, Apple hardware
about 37 %, GoPro mid-30s, Dell low 20s; margins become critical at series B, not at seed; the
model should show 1,000 versus 10,000 versus 100,000 units (SeriesOps, 2026-01-17). BOM share
of price and typical MOQs: no dated source, left empty. The stage-generic benchmarks of the SaaS
file (burn multiple, runway, round size) are shown as well. Series B: the same SeriesOps
comparables, whose note that margins become critical at series B is the point; BOM, MOQ,
inventory months and warranty rates have no dated source and stay empty.

Series C: the same SeriesOps public comparables and volume tiers (2026-01-17); BOM, MOQ,
inventory months and warranty rates have no dated source and stay empty.

## Sources

- [SeriesOps, Gross Margin for Hardware Startups: What's Actually Good at Seed Stage?](https://seriesops.com/insights/gross-margin-hardware-startups), 2026-01-17
- [Burkland, How Investors Evaluate Series A Startups in 2026](https://burklandassociates.com/2026/07/21/how-investors-evaluate-series-a-startups-in-2026/), 2026-07-21

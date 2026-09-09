#!/usr/bin/env python3
"""Generate the FICTIONAL seed fixture: a 14-page deck and two annexes.

    fixtures/seed-deck.pdf              the deck, with figures on pages 6, 7, 10, 12
    fixtures/seed-annex-revenue.csv     monthly revenue export that backs most figures
    fixtures/seed-annex-cohorts.csv     cohort retention table

Every name, figure and person is invented. The deck states one figure the export does not
match (customer count: deck 42, export 38, a 10 % gap, minor) and one figure with no annex at
all (CAC), so that the seed pipeline has something to prove, something to note and something to
request. Standard library only; reuses the PDF writer of make_preseed_fixture.py.

Run:  python fixtures/make_seed_fixture.py
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_preseed_fixture as base  # noqa: E402

OUT_PDF = os.path.join(HERE, "seed-deck.pdf")
OUT_REVENUE = os.path.join(HERE, "seed-annex-revenue.csv")
OUT_COHORTS = os.path.join(HERE, "seed-annex-cohorts.csv")

PAGES = [
    ("GANTRIX", [
        "Procurement follow-up for small industrial firms.",
        "",
        "Seed round - September 2026",
        "",
        "Lena Vartan, CEO - Marc Delorme, CTO - Sofia Reyes, Head of Sales",
        "contact: fictional@example.com",
    ]),
    ("The customer", [
        "Purchasing managers in industrial SMEs (50 to 200 employees). The plant director signs the subscription.",
        "",
        "From a customer, Ferrolux SAS, April 2026: \"We stopped chasing suppliers on Fridays. The tool does it.\"",
    ]),
    ("What changed since pre-seed", [
        "In January 2026 we dropped the manual service and shipped the email parsing engine.",
        "",
        "We abandoned the per-user pricing tested in Q4 2025: buyers wanted one price per site.",
    ]),
    ("The product", [
        "Gantrix reads supplier emails and updates the order status automatically. Live since February 2026.",
    ]),
    ("Traction", [
        "42 paying customers as of August 2026, first payment in November 2025.",
        "",
        "MRR: 8,200 EUR in June 2026, 9,900 EUR in July 2026, 12,100 EUR in August 2026.",
        "",
        "Named customers: Ferrolux SAS, Metalpro Ouest, Bricard Fonderie, Atelier Vion.",
    ]),
    ("Retention", [
        "Monthly logo churn: 2.1% on average over the last six months.",
        "",
        "Week-8 retention of the February cohort: 84%, flat since week 6.",
        "",
        "Customers lost since launch: 4, three of them plants that closed their purchasing desk.",
    ]),
    ("Economics", [
        "Price: 150 EUR per month per site, paid by 42 customers.",
        "",
        "Customer acquisition cost: 900 EUR, computed on the 18 customers signed in Q2 2026 (sales salary plus events).",
        "",
        "Gross margin per customer: 81%.",
        "",
        "Sales cycle: 34 days on average from first call to first payment.",
    ]),
    ("Acquisition", [
        "Channels: 55% outbound by our sales lead, 30% referrals from existing customers, 15% trade shows.",
    ]),
    ("Market", [
        "Bottom-up: 24,000 industrial SMEs in France with a purchasing desk, times 150 EUR per month, is 43 million EUR per year.",
        "",
        "Competitors: Procurio (stronger ERP integrations) and Suppli (cheaper, no email parsing).",
        "",
        "Why now: since 2025 the EU e-invoicing mandate forces suppliers to send structured documents.",
    ]),
    ("Team", [
        "Lena Vartan, CEO. 8 years as purchasing manager at Forgeval Industries, led a team of 6 buyers.",
        "",
        "Marc Delorme, CTO. 6 years at Datadog as a staff engineer.",
        "",
        "Sofia Reyes, Head of Sales, hired March 2026. Previously 5 years at Suppli.",
        "",
        "Both founders full-time since January 2026. Equity: Lena 45%, Marc 45%, option pool 10%.",
        "",
        "Missing for series A: a VP Marketing. Hiring planned for Q1 2027.",
    ]),
    ("The ask", [
        "We are raising 1,500,000 EUR in this seed round.",
        "",
        "Use of funds: 50% sales team, 30% product, 20% operations.",
    ]),
    ("Next milestones", [
        "Goal before series A: 150 paying customers and 45,000 EUR MRR by September 2027.",
        "",
        "Monthly burn: 70,000 EUR. Runway with this round: 21 months.",
    ]),
    ("Who already invested", [
        "Pre-seed, January 2026: 400,000 EUR from Lyon Angels and two business angels. Lyon Angels follows on in this round.",
    ]),
    ("References", [
        "Customers available for a call: Ferrolux SAS (plant director), Metalpro Ouest (purchasing manager).",
        "",
        "Former colleagues and pre-seed investors available on request.",
    ]),
]

REVENUE_ROWS = [
    ("month", "mrr_eur", "paying_customers", "new_customers", "churned_customers"),
    ("2025-11", "600", "4", "4", "0"),
    ("2025-12", "1500", "10", "6", "0"),
    ("2026-01", "2400", "16", "6", "0"),
    ("2026-02", "3300", "22", "7", "1"),
    ("2026-03", "4650", "31", "9", "0"),
    ("2026-04", "5550", "37", "7", "1"),
    ("2026-05", "6450", "43", "7", "1"),
    ("2026-06", "8200", "40", "0", "3"),
    ("2026-07", "9900", "39", "0", "1"),
    ("2026-08", "12100", "38", "0", "1"),
]

COHORT_ROWS = [
    ("cohort", "week_0", "week_2", "week_4", "week_6", "week_8"),
    ("2026-02", "100", "93", "88", "84", "84"),
    ("2026-03", "100", "95", "90", "87", "86"),
    ("2026-04", "100", "91", "86", "83", "82"),
]


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


if __name__ == "__main__":
    pdf = base.build_pdf(PAGES)
    with open(OUT_PDF, "wb") as f:
        f.write(pdf)
    write_csv(OUT_REVENUE, REVENUE_ROWS)
    write_csv(OUT_COHORTS, COHORT_ROWS)
    print(f"wrote {OUT_PDF} ({len(pdf)} bytes, {len(PAGES)} pages), {OUT_REVENUE}, {OUT_COHORTS}")

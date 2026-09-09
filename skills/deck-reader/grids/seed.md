# The seed grid

**Grid version: 2026-09-09. Stage covered: seed only.**

This file is a fixed copy of the grid. It does not change at run time. The machine-readable
version used by the scripts is `scripts/grids/seed.json`; both must stay identical.

**A deck is scored according to its stage.** Same engine as the pre-seed grid, another question.
Pre-seed asks "what does the deck not say?". Seed asks "does what the deck says hold up?".

**What the grid measures**: the completeness of the deck, and whether its statements are backed
by the documents the founder sent and by public sources. It does not measure the quality of the
company. No verdict, no threshold, no rating.

---

## What changes from pre-seed

| | Pre-seed | Seed |
|---|---|---|
| What is judged | Evidence of learning | Evidence of use: who pays, who comes back |
| Input | The deck alone | The deck, plus the annexes: revenue export, cohorts, financial model, cap table |
| What the tool does | Completeness: does the deck answer? | Completeness, then verification: do the statements hold against the annexes and the web? |
| Extra output | | The gaps to probe in the call, and a draft email for the missing documents |
| Heaviest blocks | Team, field | Traction, economics |

---

## The seed principle

There are first figures. We judge whether someone pays, whether someone comes back, and whether
what the deck states survives a check.

Red signals of the stage:

- No retention figure
- Customers "in discussion", none paying
- A growth percentage without its starting point
- A statement contradicted by an annex or by the web
- Churn appears nowhere

---

## How the seed reading works

1. **Read.** The PDF page by page; the annexes read separately (`annex_text.py`).
2. **Profile.** Sector, model type (SaaS, marketplace, other), B2B or B2C, announced stage.
3. **Claims.** Every verifiable statement of the deck, one line each with page and quote
   (`claim-extractor`, checked by `check_claims.py`).
4. **Proof in the annexes.** Each claim looked up in the documents (`annex-matcher`, checked and
   classified by `verify_matches.py`). Then the first gate (`seed_gate.py annexes`):
   - no annex: stop, generic email to the founder, no web, no grid;
   - the key figures (revenue, customers, retention) less than half covered: stop, precise email;
   - otherwise continue, and list what is still missing for the email.
5. **Web check**, only now, and only on what a document cannot settle: named customers,
   competitors, founders, past funding, "why now" (`web-verifier`, rules enforced by
   `verify_web.py`). For every claim, searched both for and against; at least two independent
   domains to conclude; otherwise unverifiable, which is a valid state.
6. **Double check.** Every blatant contradiction goes to a second, independent reviewer whose
   only job is to find an honest explanation: date, definition, scope, unit, stale source,
   homonym (`contradiction-reviewer`). With an explanation, the claim becomes a question for the
   call. Without one, the second gate stops the reading and shows the sources on both sides.
7. **Grid**, on the deck and the proofs. A figure without a proven or confirmed claim behind it
   is capped at partial by code (`apply_proof_cap.py`); an answer citing a gap to probe is
   lowered one step.
8. **Report.** Seven bars, the reading, the gaps to probe, the documents still to request with
   the email draft, the claims table, question by question.

---

## The scale

Each question receives exactly one of three values, with the deck page and the verbatim quote
that justifies it.

| Value | Points | Meaning |
|---|---|---|
| **Found** | 2 | The deck answers, with a verifiable element, and for a figure, a proven or confirmed claim behind it |
| **Partial** | 1 | The deck touches the subject without a verifiable element, or vaguely, or states a figure no document backs |
| **Absent** | 0 | The deck does not mention it. No inference: if it is not on a page, it is absent |

**Seed rule**: a question marked *proof* cannot be found from the deck alone.

---

## Blocks and questions

"Proof expected" is the document that would back the answer; it is what the founder email asks
for when the claim is not covered.

### Block A. Problem and customer, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| A1 | Who is the paying customer, precisely? | A nameable profile, and at least one real customer that matches it | Customer list | |
| A2 | Why do they buy, in their own words? | A customer quote or a documented use case | Testimonial, customer call | |
| A3 | What changed since the start? | A pivot or an invalidated hypothesis, dated | The deck suffices | Nothing abandoned in two years = partial at best |

### Block B. Traction, weight 3

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| B1 | How many paying customers, since when? | A number and a first payment date, backed by an annex or the web | Stripe export or invoices | *proof* |
| B2 | Monthly revenue and its curve? | An MRR or equivalent over at least 3 months, with the data points | Stripe export | *proof*. A growth percentage without the starting point = absent |
| B3 | Do customers come back? | A retention figure: cohorts, churn, recurring usage | Cohorts, analytics | *proof*. A cohort that flattens after week 8 is the signal seed funds look for |
| B4 | Do the named customers exist and really use the product? | Confirmed outside the deck: website, LinkedIn, public testimonial, or an annex | Web | *proof*. **The central question of the stage.** Absent = red |
| B5 | How many customers lost, and why? | A figure and a reason | Export, cohorts | *proof*. Absent = the deck hides churn. Red |
| B6 | Where do customers come from? | A named channel with its share, and the share of organic | Analytics, CRM | *proof*. All paid = partial |

### Block C. Economics, weight 3

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| C1 | What price, paid by whom, since when? | A price actually collected | Stripe export | *proof*. A price list without a payment = partial |
| C2 | Customer acquisition cost? | A figure with the method, even on 10 customers | Marketing spend, CRM | *proof*. Benchmark shown with the caveat "small sample" |
| C3 | Gross margin per customer? | A figure. Estimated without a basis = partial | P&L, financial model | *proof* |
| C4 | Sales cycle? | An average duration from first contact to payment | CRM | *proof*. B2B only, weight 0 in B2C |

### Block D. Market and competition, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| D1 | Market size computed bottom-up? | Possible customers multiplied by the observed price, with visible assumptions | The deck, assumptions visible | An analyst figure = absent |
| D2 | Who are the competitors, and where are they better? | Named, with one point where they win | Web: omitted competitors | Omitted competitors become a contradiction |
| D3 | Why now? | A recent, named, verifiable change | Web | |

### Block E. Team, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| E1 | Who did what before, verifiably? | Named achievements, confirmed on LinkedIn or elsewhere | Web: LinkedIn | *proof*. A title without a result = partial |
| E2 | Who was hired since, and for what? | Names and roles | LinkedIn | Absent = the previous money did not go into the team |
| E3 | Full-time, and equity split? | Stated for each founder | Cap table | |
| E4 | Who is missing to reach series A? | A named gap with a hiring plan | The deck suffices | A named gap is worth more than a hidden gap |

### Block F. Money and next step, weight 2

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| F1 | How much is asked, and what for? | An amount and a breakdown | The deck suffices | |
| F2 | What figures must be reached for series A? | A measurable, dated goal: MRR, customers, retention | The deck suffices | Absent = the money has no purpose. Red |
| F3 | How many months of runway? | A monthly burn and a duration | Financial model, bank statement | *proof*. 12 to 18 months with named milestones is what funds expect |
| F4 | Who already invested, and do they follow on? | Names, amounts, whether existing investors follow on | Cap table, web | Existing investors who do not follow on: a question for the call |

### Block G. References, weight 1

| # | Question | Found if | Proof expected | Note |
|---|---|---|---|---|
| G1 | Customers we can call? | Names and a way to contact them, or the deck says they are available | The deck suffices | |
| G2 | Former colleagues or investors we can call? | Same | The deck suffices | Asked to prepare the call, not to judge the deck |

---

## Questions added by business model

The profile detects the model. These questions are appended to block B with the block weight.

**Marketplace** (from a16z's 13 marketplace metrics):

| # | Question | Found if |
|---|---|---|
| M1 | Gross merchandise value and take rate? | Both figures, and the net revenue that follows from them |
| M2 | Match rate and time to match? | Share of requests served, and the delay |
| M3 | Concentration? | Share of volume made by the top 10 sellers or buyers |
| M4 | Do both sides come back? | Retention figures for supply and demand, separately |

**SaaS**: no extra question, the grid is written for it.

---

## The computation

1. **Per question**: 0, 1 or 2 points, multiplied by the block weight (or by the question's own
   weight when one is given).
2. **Per block**: points obtained divided by the maximum possible, as a percentage.
3. **Global**: average of the blocks weighted by their weight.

| Block | Weight | Approximate share of the score |
|---|---|---|
| A. Problem and customer | 2 | 13 % |
| B. Traction | 3 | 20 % |
| C. Economics | 3 | 20 % |
| D. Market and competition | 2 | 13 % |
| E. Team | 2 | 13 % |
| F. Money and next step | 2 | 13 % |
| G. References | 1 | 7 % |

Traction and economics make 40 % of the score. At pre-seed, team and field made 42 %.

Implementation rules, fixed with the grid:

- C4 counts with weight 0 when the profile says B2C.
- A question marked *proof* whose value is found without a proven or confirmed claim cited is
  capped at partial by `apply_proof_cap.py`. An answer citing a claim left to probe is lowered
  one step.
- A block is **red** when its completeness is below 50 %.
- **Confirmation passes**, as in pre-seed: between 65 % and 80 % inclusive, three independent
  checker passes and the median per question.

### Gap thresholds

A gap between a deck figure and the figure found in an annex or on the web is classified by
code, never by a model. Ratio = |deck − found| / max(|found|, 1).

| Class | Ratio | What happens |
|---|---|---|
| minor | ≤ 25 % | Noted. The claim is proven or confirmed. No penalty |
| to probe | ≤ 100 % (a factor of 2) | Becomes a question for the call; the questions citing it are lowered one step |
| blatant | above, or the fact does not exist | Second independent review; without an honest explanation, the reading stops |

A non-numeric contradiction (a named customer that does not exist, a founder who never worked
there) is blatant by default, and goes to the review like the others.

### Annex gate

- No readable annex: stop. Generic email: "the deck arrived without supporting documents".
- Key claim types the deck makes (revenue, customers, retention) covered by a proven claim in a
  proportion below 50 %: stop, precise email listing each uncovered statement with the document
  expected.
- Otherwise continue; the uncovered statements go into the report and into a leftovers email.
- A deck that makes no key claim at all continues: the grid will show the absences.

### Web rule

A claim is confirmed or contradicted on the web only with at least 2 sources on distinct
domains, after searching both for and against. Two domains of the same owner count as one.
Silence is unverifiable, not contradicted. Only named customers, competitors, founders, past
funding, "why now" and market bases are web-checked; revenue is never "checked on the web".

---

## What the tool outputs

- **Seven bars** of completeness, one per block, and the global.
- **Per question**: the value, the page, the verbatim quote, the claims cited, and whether the
  value was capped or lowered.
- **The reading**: the three main gaps, the questions for the call, what the deck does not say,
  and what did not hold up.
- **Gaps to probe**: each claim left to probe, with both sides and the reviewer's explanation.
- **Documents still to request**, with the email draft. The tool writes the draft; the user
  sends it, or not.
- **The claims table**: every statement, its status and what backs it, sources on both sides.

What it does not output: a rating of the company, a verdict, a threshold, a valuation.

---

## Guardrails

Those of pre-seed, plus:

- A verification without a source is rejected by code. "Unverifiable" is a valid answer;
  "probably false" is not.
- The tool can only stop on something false, never on something imprecise. Every stop is
  preceded by an independent review that looked for an honest explanation, and shows it.
- A stop erases nothing: everything read so far stays in the report, and the investor decides.
- The thresholds (gaps, coverage, sources) live in this file and in the JSON, readable by all,
  and are corrected at each post-mortem. They are not hidden in a prompt.
- The tool never sends the email.

---

## Where the grid comes from

Compared with what exists for seed: Point Nine's open-source deal memo (nine sections, including
references), the eight dimensions seed funds weigh in a three-minute read (market, traction,
business model ahead of team), CRV's seed KPIs (cohorts, week-8 retention, organic referrals),
a16z's 13 marketplace metrics, and Payne's scorecard weights for business angels. None of these
sources reads the deck or cites the page. That is what the tool does.

---

## Revisions

| Date | Change | Triggered by |
|---|---|---|
| 2026-09-09 | First version: seed grid, claims and verification, model questions, gates and thresholds | Research on existing seed grids |

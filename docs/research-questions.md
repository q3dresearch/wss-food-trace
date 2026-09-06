# What this archive is for

Written before the repo was published, because the previous version of it was
built first and questioned afterwards: a working capture, parser, chart and
README, for a source nobody had yet asked a question of. The rule that came out
of it — **probe the shape, write the questions down, try to answer them, and
only then decide what to build** — is why this file exists at all.

## The spine

Every substance in the food supply passed through a **gate**: an approval, a
notification, or a self-determination nobody was told about. Human food and
animal feed share that gate — same agency, same instruments, same failure
modes. Crop production does not; it is a market, not a gate.

So this repo is **the regulatory gate on the food supply**, not "food" in
general. That is what makes petitions, consultations and not-GRAS
determinations one archive instead of three unrelated ones.

## The questions

Status is honest about what the archive can do **today**, not what it will do.

| # | question | needs | status |
| --- | --- | --- | --- |
| 1 | How long from first filing to market, and is it lengthening? | queue over years + `reference/final-rules.csv` | **accruing** — but see *the gate moved*, below |
| 2 | What share enters by notification vs petition vs silent self-determination? | — | **unanswerable** — the third category is invisible by construction |
| 3 | What is queued right now that most people do not know is coming? | one capture | **answerable now** |
| 4 | Who petitions to *remove* an additive, and does it work? | queue over years + not-GRAS list | **accruing** |
| 5 | How long between a revocation petition and any regulatory action? | queue + rules join | **accruing** |
| 6 | When a substance is removed, what replaces it — and was the replacement scrutinised? | a substitution join we do not have | **blocked** |
| 7 | What is withdrawn before a decision, and does it return? | `reference/gras-notices.csv` | **answered** — 16.8% withdrawn; of the 70 linked to a resubmission, 93% later cleared |
| 8 | Do withdrawn substances appear in food anyway? | — | **out of scope** — a GRAS determination needs no notice at all, so this data cannot see it. See NRDC below |
| 9 | What is animal feed innovation actually for? | `reference/agras-notices.csv` | **answered** — 37% of notices exist to extract more from existing feed, not to add anything new |
| 10 | Does animal clear at a lower rate than human? | both GRAS references | **answered** — [chart](../examples/charts/animal-vs-human.svg) |
| 11 | Is antibiotic use in feed falling? | FDA annual antimicrobial sales | **no verified source yet** |
| 12 | Does an EU ban predict a US revocation petition? | an EU register | **no verified source yet** |

**Eleven of twelve need the queue observed over time.** That is why this repo
captures rather than analyses, and why it was not worth publishing on day one.

## What the join already shows

The petition number links the queue to the rules, and 91% of the 609 rules
carry one. The first thing it surfaced:

> **FAP 9M4697** — ionizing radiation, Food Irradiation Coalition. FDA issued a
> final rule for **part** of it in August 2008 (fresh iceberg lettuce and
> spinach, 21 CFR 179.26). The **same petition** is still held in abeyance in
> 2026 for the remainder — refrigerated, frozen or dried meat, poultry, fruit
> and vegetables.

A partial grant with the rest waiting eighteen years. Neither half of the
record shows it alone.

## Answered already: the gate moved, it did not close

![The gate did not close](../examples/charts/the-gate-moved.svg)

Counting granted petitions alone, food additive rulemaking looks like collapse
— 546 rules between 1990 and 2026, only 82 of them after 2005. Rules per decade
run 61 · 383 · 94 · 46 · 23.

**That reading is wrong, and the reason is a mechanism rather than a trend.**
54% of those rules are food-contact substances, and food-contact petitions
granted per year run 26, 29, 39, 23, 30, 41, 26 through 2000 — then **2, 0, 0,
0**. A cliff, not a slope.

The 1997 FDA Modernization Act created a **notification** route for
food-contact substances. From 2000 they used it: **1,636 notifications became
effective against 293 food-contact petitions granted** in the same window,
running about 70 a year where petitions never exceeded ~40.

Meanwhile the lanes that stayed on the petition route behave differently from
each other:

| kind | 1975–89 | 1990–97 | 1998–05 | 2006–15 | 2016–26 |
| --- | --- | --- | --- | --- | --- |
| food contact | 38 | 186 | 99 | 2 | 6 |
| food additive | 5 | 47 | 54 | 16 | 10 |
| **colour** | 0 | 15 | 14 | 17 | **22** |

**Food additive rules genuinely declined. Colour additive rules rose.** Neither
is visible if you read the total.

The lesson generalises past this dataset: **a series that ends abruptly is more
often a route change than a behaviour change.** Look for where the traffic
went before concluding it stopped.

## Answered: animal ingredients clear at two thirds the human rate

![The same instrument, two very different gates](../examples/charts/animal-vs-human.svg)

**55.8% of closed animal GRAS notices cleared, against 81.2% of human ones.**
The withdrawal gap — 37.2% against 17.3% — is about 3.8 standard errors on 86
closed animal notices, so it is real. The rejection gap runs the same way but
rests on 6 events, and is quoted as "6 of 86" rather than as a multiple.

None of that explains *why*. A lower pass rate is equally consistent with
stricter review, weaker submissions, or a thinner evidence base. FDA announced
in August 2024 that it was evaluating both animal programmes.

## On question 8, and why it is not answerable here

A GRAS determination requires **no notice to FDA at all**. A company may
withdraw a notice when FDA asks a hard question and continue marketing the
substance under its own determination, and nothing in these inventories would
record it — a substance that never files never appears.

That is not a gap in the capture; it is a property of the statute. It has been
documented from the outside: NRDC's 2014 report [*Generally Recognized as
Secret*](https://www.nrdc.org/resources/generally-recognized-secret-chemicals-added-food-united-states)
identified 275 chemicals from 56 companies apparently sold on undisclosed
determinations, including substances withdrawn more than once that stayed on
sale.

**So do not read a withdrawal here as a substance leaving the food supply.**

## Answered: the enforcement list and the notification system barely overlap

Joining the captured not-GRAS list against the GRAS notice inventory:

> **19 of the 20 substances FDA has declared *not* GRAS never filed a notice at
> all.**

The single exception is **Ginkgo biloba** — GRN 36, filed by Vancol Industries,
**withdrawn in April 2000**, and later determined not GRAS post-market. The
whole arc in one row. Everything else on that list — CBD, delta-8-THC, kava,
tianeptine, muscimol, betel nut, tara flour — arrived without ever using the
notification route.

This does not answer question 8, which stays unanswerable. But it is the
visible shadow of it: **the gate is being routed around, and the enforcement
list is where that becomes measurable.**

*Method, because a loose one gives the wrong answer here.* Matching requires
verbatim containment of the full substance name or one of FDA's listed aliases,
minimum 8 characters. A first attempt using shared word tokens reported **9 of
20**, of which eight were false — it matched melatonin to *N-acetyl-D-neuraminic
acid* on "acetyl", and tara flour to *protein preparation from animal blood* on
"protein". The conservative matcher will still miss anything filed under a
chemical synonym FDA does not list.

## Answered: the gate is a long tail, not a concentrated industry

![Who files](../examples/charts/who-files.svg)

**503 of 745 human-food notifiers filed exactly once**, and the ten most
frequent account for only 12% of all notices. Novozymes leads with 32 of 1,336.

That cuts against one specific critique: whatever is wrong with the GRAS route,
*"a few big companies use it repeatedly"* is not the description. The animal
side is smaller and slightly more concentrated, but the same shape.

**It does not mean the tail is disposable.** Filing once almost certainly means
having one novel ingredient — a company that develops a single new culture
notifies once and never needs to again. The data supports the boring reading:

| notifier files | n | cleared | withdrawn | rejected |
| --- | --- | --- | --- | --- |
| exactly once | 484 | **81.4%** | 16.5% | 2.1% |
| 2–3 times | 402 | 75.1% | 23.1% | 1.7% |
| 4–9 times | 264 | 84.5% | 14.4% | 1.1% |
| 10+ times | 151 | **90.7%** | 9.3% | 0.0% |
| all | 1,301 | 81.2% | 17.3% | 1.5% |

One-time filers clear at the same rate as everyone else, and they arrive
steadily — between 27% and 49% of each year's closures for twenty-five years,
with no clustering. Shell filings would fail more often and would bunch around
whatever incentive created them. Neither happens.

The real gradient is experience: **90.7% for the most frequent filers, with a
zero rejection rate.** Novozymes has filed 32 times and knows what FDA wants.

**A null result, recorded so nobody re-runs it:** filing history does not
predict animal GRAS outcome. One-time filers cleared 52.6%, repeat filers
56.7%, on n=19 and n=67. There is nothing there.

## Questions this raised

Added because the archive suggested them, not because they were planned.

| # | question | needs |
| --- | --- | --- |
| 13 | Is AFIC recruiting firms the formal route never saw? Seven of nine consultations come from companies with no AGRN notice ever. **Weak** — AFIC only launched in 2024, so "never filed before" is the expected state, not a signal. Barely a question until there are more than nine consultations. | AFIC over time |
| 14 | Does the enforcement list keep growing from a population the notification system cannot see? 19 of 20 says yes, but 20 is a small list. | the not-GRAS capture, over years |

## Sources, and why each is filed where it is

| source | rows | filing | why |
| --- | --- | --- | --- |
| `fda.additives.petitions` | 32 open | **capture** | resolved petitions leave the page; grants survive as rules, abandonments leave nothing |
| `fda.animalfeed.consultations` (AFIC) | 9 | **capture** | explicitly an *interim* programme — the page plausibly disappears with it |
| `fda.additives.notgras` | 20 | **capture** | the list is retained but carries **no dates**; only an archive can say *when* a substance was added |
| `reference/final-rules.csv` | 609, to 1975 | **reference** | self-archiving. Cited, not captured — but it is the join target |
| `reference/fcn-notifications.csv` | 1,760, to 2000 | **reference** | the route food-contact substances moved to; without it the rules series is unreadable |
| `reference/gras-notices.csv` | 1,336 | **reference** | human GRAS notices, retained in full including withdrawals |
| `reference/agras-notices.csv` | 94 | **reference** | animal GRAS notices, AGRN 1–94 contiguous |

## A trap that nearly cost a wrong verdict

The FDA app paginates by default and **does not say so**. `set=FinalRules`
returns 51 rows back to 2014 and reads exactly like a rolling window — the
blurb even claims coverage "since 1994", which made the gap look like evidence
of deletion. Adding `showAll=true` returns **609 rows back to 1975**.

The same test run against `set=FAP-CAP` returns 32 either way, which is what
confirms that one genuinely is only the open queue.

> **Before declaring a source perishable, look for a pagination parameter.**
> Two sources on the same host, identical in appearance, opposite verdicts.

## Not yet verified

Questions 11 and 12 have **no confirmed source**. Candidate URLs for FDA's
annual antimicrobial sales report and an EU novel-food register were guessed
and returned 404. They stay listed as open questions rather than as a plan.

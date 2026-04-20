# Reference: site-audit

Operation-specific details for the `unfairgaps site-audit` operation. Read this AFTER the shared 4-phase protocol in `../SKILL.md`.

## Core question for this operation

**Is this site selling into a REAL unfairgap or a manufactured one?**

A company can have sharp copy and pretty screenshots while targeting a pain that doesn't recur at scale. Conversely, a boring-looking company can be plugged into a $10B/yr unfairgap. The site's claims mean nothing without corroboration from the enforcement/court/cost-evidence data.

Three questions per claim:
1. Does this pain actually show up in the data? (If no → EXAGGERATED or NO_EVIDENCE)
2. Is the pain systemic (≥3 events, ≥2 companies)? (If no → their TAM is anecdotal)
3. What pains are they MISSING that the data clearly shows?

## Input parsing

- `url` (required): website to audit

## Phase 1 — Site scrape + business model extraction

Fetch the site with WebFetch. If HTTP 403 / timeout / empty:
- Try WebFetch via `site:<domain>` search
- Try about page, pricing page, blog landing
- If all fail, emit `## Scrape failure` and stop — don't fabricate.

Emit as `### SITE MODEL`:

```yaml
url: "<input>"
domain: "<derived>"
language_detected: "<primary language>"
market_inferred: "<country; reasoning>"
what_you_sell: "<1 sentence>"
problem_you_claim_to_solve: "<1 sentence, from hero + features>"
pricing_visible: "<yes/no; tier details if shown>"
customer_segments_claimed: [<2-5; who PAYS>]

claimed_pains:
  - id: cp_001
    pain: "<1 sentence>"
    specificity: "HIGH | MEDIUM | LOW"
    evidence_on_site: "<case study / testimonial / stat / nothing>"
    quote: "<verbatim <=150 char>"
  - id: cp_002
    ...
```

**Geo caveat:** some sites are geo-routed (e.g., procore.com → Singapore from non-US IP). If detected market looks wrong based on company origin, flag it and force the correct market inference OR note coverage limitation.

## Phase 2 — Query split (verification + discovery)

For each claimed pain, 1-2 verification queries: does the pain exist in enforcement/court data?

Plus **discovery queries (4-5)**: what OTHER pains does data show for this segment that the site ignores?

Plus aggregator hunt (1).

Total queries: 8-12. Emit with column `claim_linked: cp_00X | DISCOVERY`.

## Phase 3 — Evidence card additions

Add fields to shared schema:
```yaml
linked_claim: "cp_00X" | "discovery"
verdict_contribution: "confirms | contradicts | partial | tangential"
```

## Phase 3.5 — Claims vs reality synthesis

For each `cp_XXX` claimed pain, assign a verdict:

```yaml
- claim_id: cp_001
  claim: "<restate>"
  verdict: "CONFIRMED | EXAGGERATED | UNDERSTATED | NO_EVIDENCE"
  corroborating_events: [ev_XXX, ev_YYY]
  reasoning: "<1-2 sentences>"
```

**Verdict rules:**
- **CONFIRMED** — ≥2 events in ledger directly corroborate, ≥2 companies
- **UNDERSTATED** — events show the pain is bigger than the site claims. Annotate with $ delta.
- **EXAGGERATED** — events exist but site inflates (wrong magnitude, scope, or who-suffers)
- **NO_EVIDENCE** — ledger doesn't corroborate

Separately emit `missed_unfairgaps` — systemic gaps (per shared Phase 3.5 rules) that the site does NOT address:

```yaml
- missed_id: mu_001
  unfairgap_hypothesis: "<plain language>"
  status: "CONFIRMED_SYSTEMIC | EMERGING_PATTERN"
  evidence: [ev_ZZZ, ev_WWW, ev_VVV]
  why_the_site_should_care: "<why their segment/product line should address this>"
```

**Drop-rule:** claimed pains that can't be assigned one of the 4 verdicts = skill failure.

## Phase 4 — Report format

```
# Site Audit: {domain}
Generated: {date}
Skill version: 0.5.0

## Overall assessment: {EVIDENCE_BASED | MIXED | MOSTLY_FLUFF | MISPOSITIONED}
One sentence explaining the verdict.

## Site positioning
- What they sell: {what_you_sell}
- Target segments: {list}
- Market inferred: {country + reasoning}

## Claims vs Reality
| claim_id | claim | verdict | evidence | $ delta if UNDERSTATED |
|---|---|---|---|---|

### Per-claim detail
For each claim: verdict + corroborating ev_ links + reasoning.

## Missed Unfairgaps (what the data shows that they don't address)
For each mu_XXX with status, evidence list, and reframing.

## Recommended positioning changes
- If EVIDENCE_BASED: lean into specific events with $ amounts
- If MIXED: which claims to double down on; which to cut
- If MOSTLY_FLUFF: reconsider fundamentally
- If MISPOSITIONED: data-backed opportunity is mu_XXX, not what they pitch

## Run manifest
queries, fetches, ledger size, claim counts by verdict
```

Save as `audit-{domain}-{YYYY-MM-DD}.md`.

## Hard rules specific to site-audit

1. CONFIRMED ≥2 events minimum; UNDERSTATED requires $ delta annotation.
2. At least 1 MISSED UNFAIRGAP attempted; if truly none found, say so in `coverage_caveats`.
3. Overall `MOSTLY_FLUFF` is a real valid outcome. Do not soften.
4. Geo-mismatch flagged explicitly if the detected market doesn't match the company's origin.

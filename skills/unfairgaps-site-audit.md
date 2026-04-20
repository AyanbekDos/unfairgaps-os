---
name: unfairgaps-site-audit
description: Audit a website's pain claims vs reality using court filings and enforcement data. Dual mode - native Claude Code or delegates to run.py if PERPLEXITY_API_KEY set.
version: 0.4.0-proto
---

# THE ONE THING TO REMEMBER

**We audit whether this site is selling into a REAL unfairgap or a manufactured one.**

A company can have sharp copy and pretty screenshots while targeting a pain that doesn't recur at scale. Conversely, a boring-looking company can be plugged into a $10B/yr unfairgap. The site's claims mean nothing without corroboration from the enforcement / court / cost-evidence data.

Three questions per claim:
1. Does this pain actually show up in the data? (If no → EXAGGERATED or NO_EVIDENCE)
2. Is the pain systemic (≥3 events, ≥2 companies)? (If no → their TAM is anecdotal)
3. What pains are they MISSING that the data clearly shows?

## Input contract

- `url` (required): Website to audit

## Execution mode selection

If `PERPLEXITY_API_KEY` set and user didn't request native: delegate to `python run.py site-audit --url "X"`. Otherwise native flow.

## Native flow — 4-phase protocol

### Phase 1 — Site scrape + business model extraction (≤400 tokens)

Fetch the site with WebFetch. If HTTP 403 / timeout / empty:
- Try WebFetch on `site:<domain>` via search
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
customer_segments_claimed: [<2-5; who PAYS, not who reads>]

claimed_pains:
  - id: cp_001
    pain: "<1 sentence>"
    specificity: "HIGH | MEDIUM | LOW"   # HIGH = names $ amounts or specific regulation; LOW = vague
    evidence_on_site: "<case study / testimonial / stat / nothing>"
    quote: "<verbatim ≤150 char quote from the site>"
  - id: cp_002
    ...
```

### Phase 2 — Candidate pool (verification + discovery)

For each claimed pain, 1-2 verification queries: does the pain exist in enforcement/court data? Specifically with the named industry + segment + regulatory pattern the site mentions.

Plus **discovery queries** (4-5): what OTHER pains does data show for this segment that the site ignores?

Plus aggregator hunt (1): curated lists of events in this segment's pain class.

Total queries: 8-12 depending on # of claimed pains.

Emit `### CANDIDATE POOL` same schema as industry-scan. Add column `claim_linked: cp_00X | DISCOVERY`.

### Phase 3 — Evidence ledger

Top 8-12 global-ranked fetches. Compress to cards. Each card has additional field:

```yaml
linked_claim: "cp_00X" | "discovery"
verdict_contribution: "confirms | contradicts | partial | tangential"
```

### Phase 3.5 — Claims vs reality synthesis

For each `cp_XXX` claimed pain, assign a verdict based on ledger evidence:

```yaml
- claim_id: cp_001
  claim: "<restate>"
  verdict: "CONFIRMED | EXAGGERATED | UNDERSTATED | NO_EVIDENCE"
  corroborating_events: [ev_XXX, ev_YYY]
  reasoning: "<1-2 sentences>"
```

**Verdict rules:**
- **CONFIRMED** — ≥2 events in ledger directly corroborate the claimed pain, across ≥2 companies. (Same bar as unfairgap EMERGING/CONFIRMED.)
- **UNDERSTATED** — events show the pain is bigger / more frequent / more costly than the site claims. Annotate with $ delta.
- **EXAGGERATED** — events exist but site is inflating (wrong $ magnitude, wrong scope, wrong who-suffers).
- **NO_EVIDENCE** — ledger doesn't corroborate. Either search missed it or the pain is manufactured.

Separately, emit `missed_unfairgaps`:

```yaml
- missed_id: mu_001
  unfairgap_hypothesis: "<plain language>"
  status: "CONFIRMED_SYSTEMIC | EMERGING_PATTERN"   # same rules as industry-scan Phase 3.5
  evidence: [ev_ZZZ, ev_WWW, ev_VVV]
  why_the_site_should_care: "<why their segment/product line should address this>"
```

Drop-rule: claimed pains that don't slot into CONFIRMED/UNDERSTATED/EXAGGERATED/NO_EVIDENCE = skill failure.

### Phase 4 — Final report

```
# Site Audit: {domain}
Generated: {date}
Skill version: 0.4.0-proto

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
For each claim with verdict + corroborating ev_ links + reasoning.

## Missed Unfairgaps (what the data shows that they don't address)
For each mu_XXX with status, evidence list, and reframing for the site.

## Recommended positioning changes
- If EVIDENCE_BASED: leaning into specific events with $ amounts
- If MIXED: which claims to double down on, which to cut
- If MOSTLY_FLUFF: this is not an unfairgap-plug, reconsider fundamentally
- If MISPOSITIONED: their data-based opportunity is actually mu_XXX, not what they pitch

## Run manifest
<queries, fetches, ledger size, claim counts by verdict>
```

Save as `audit-{domain}-{YYYY-MM-DD}.md`.

## Hard rules

1. CONFIRMED ≥2 events minimum; UNDERSTATED requires comparable $ delta annotation.
2. At least 1 MISSED UNFAIRGAP attempted; if truly none found, say so in `coverage_caveats` — don't fake a missed opp.
3. No verdict on claims with <1 event unless explicitly NO_EVIDENCE.
4. Overall `MOSTLY_FLUFF` is a real valid outcome — do not soften it.
5. Fetch cap 14. PDF-via-cache + blocked-primary-source workarounds same as industry-scan.

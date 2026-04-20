---
name: unfairgaps-customer-pains
description: Find your customers' documented pain points - unfairgap-style, grounded in court filings and enforcement data per segment. Dual mode - native Claude Code or delegates to run.py if PERPLEXITY_API_KEY set.
version: 0.4.0-proto
---

# THE ONE THING TO REMEMBER

**We find unfairgaps in YOUR CUSTOMERS' regulatory exposure — not yours.**

Your customers are companies that spend money to fix pains they already know about (their own). Your leverage is knowing what's hitting THEIR customers in court / regulatory data that they can then pitch as a solution.

We find **B2B2C unfairgaps**: systemic pains in your customers' customer segments, grounded in enforcement evidence. These become the exact hooks your customers need to sell their product.

## Input contract

- `url` (required): User's website

## Execution mode selection

If `PERPLEXITY_API_KEY` set and user didn't request native: delegate to `python run.py customer-pains --url "X"`. Otherwise native flow.

## Native flow — 4-phase protocol

### Phase 1 — Site scrape + customer-segment extraction (≤400 tokens)

Fetch the site. Same fallback chain as site-audit if primary fails.

Emit `### SITE MODEL`:

```yaml
url: "<input>"
what_you_sell: "<1 sentence>"
who_you_sell_to: "<1 sentence; role + industry + company-size context>"
market_inferred: "<country + reasoning>"
your_customer_segments:
  - seg_id: seg_001
    name: "<specific segment>"
    industry: "<industry>"
    size_tier: "<SMB | mid-market | enterprise>"
    pays_for: "<what they pay your customer for; why they have budget>"
    their_customers: "<WHO in turn pays them — these are the B2B2C population we search>"
  - seg_id: seg_002
    ...
```

**Critical distinction:**
- **Your customer segments** = who you sell to
- **Their customers** = who they sell to / serve; this is where we hunt for unfairgaps
- If the site sells B2C directly, then "their customers" = the buying persona, and we search for pains affecting them.

### Phase 2 — Per-segment candidate pools

For each `seg_00X`, run 6-8 queries hunting enforcement/verdict data affecting the `their_customers` population. Query categories same as industry-scan (regulatory/legal/verdicts/aggregators).

**Crucial:** queries must target THEIR CUSTOMERS' pains, not the segment's own operational pains. E.g., if your customer is a compliance-SaaS vendor serving restaurants, search for pains that RESTAURANT OWNERS suffer — fines, lawsuits, insurance increases — not for pains the SaaS vendor suffers.

Total queries: 8-12 per segment, capped at 16 across all segments if the idea has multiple.

Emit `### CANDIDATE POOL` with column `segment_id`.

### Phase 3 — Evidence ledger per segment

Fetch top 10-14 global-ranked (not per-segment-local). Cards linked to `seg_id` via `linked_segment` field.

### Phase 3.5 — Per-segment unfairgap detection (the product)

For each segment, run the industry-scan Phase 3.5 pattern-detection logic: group events into unfairgaps with status CONFIRMED_SYSTEMIC / EMERGING / ANECDOTAL.

**Then, crucially, translate each unfairgap into a sales-angle for your customer:**

```yaml
- unfairgap_id: ug_seg_001_001
  status: CONFIRMED_SYSTEMIC
  hypothesis: "<plain language>"
  corroborating_events: [ev_XXX, ev_YYY, ev_ZZZ]
  the_unfairgap: "<systemic regulatory hole>"
  your_customers_solution_angle: "<how YOUR CUSTOMER'S product plugs this gap, in exactly the way they would pitch it to their prospect>"
  prospect_message_sketch: "<1-2 sentences your customer can literally paste into outbound>"
  evidence_hook: "<specific $ fact + ev_ id they cite>"
  target_prospect_profile: "<role + company type + why they're vulnerable>"
```

**Status rules same as industry-scan.** ≥3 events for CONFIRMED; 2 events = EMERGING; 1 = ANECDOTAL (appendix).

### Phase 4 — Final report

```
# Customer Pain Report: {domain}
Generated: {date}
Skill version: 0.4.0-proto

## What you sell
{what_you_sell}

## Your customer segments ({N})

### Segment 1: {name}
Industry: ... | Size: ... | Their customers: ...

**Confirmed unfairgaps affecting their customers:**

**UG_1.1: {hypothesis}**
- Status: CONFIRMED_SYSTEMIC ({N} events)
- Evidence: <table ev_id | event | $ | source>
- Solution angle for your customer: {sales-angle}
- **Pitch template for outbound:** "{prospect_message_sketch}"
- Target prospect profile: {role + context}

**UG_1.2: ...**

### Segment 2: {name}
...

## Cross-segment unfairgaps
Any unfairgap that appears in 2+ of your customer segments = horizontal opportunity (biggest leverage).

## Anecdotal signals (not pitch-ready yet)
Single-event findings. Not wedges.

## Recommended next steps
- Top 3 unfairgaps by prospect-pitch-readiness
- Which segment has richest unfairgap density
- Which unfairgap is EMERGING and worth watching for 1 more event

## Run manifest
<queries per segment, fetches, ledger size, unfairgap counts>
```

Save as `pains-{domain}-{YYYY-MM-DD}.md`.

## Hard rules

1. Unfairgaps are found in YOUR CUSTOMERS' CUSTOMERS' data — if the queries drift to "your customer's operational pain" that's a failure.
2. Every pitch template references a specific `ev_` with $ + source URL — no generic outbound suggestions.
3. CONFIRMED_SYSTEMIC requires ≥3 events across ≥2 companies, same as industry-scan.
4. If a segment yields only ANECDOTAL findings, say so — don't pad.
5. Fetch cap 14 shared across all segments. PDF-via-cache + blocked-primary workarounds same as industry-scan.

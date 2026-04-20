---
name: unfairgaps-validate-idea
description: Validate a business idea against real court filings, regulatory fines, and enforcement data. Dual mode - native Claude Code WebSearch+WebFetch OR delegates to run.py if PERPLEXITY_API_KEY set.
version: 0.4.0-proto
---

# THE ONE THING TO REMEMBER

**We are not checking if SOMEONE was harmed. We are checking if the idea targets a SYSTEMIC regulatory gap that recurs across a POPULATION of companies.**

A single $50M fine proves nothing. Three similar events across three companies across two jurisdictions proves an unfairgap. Your job is to find corroboration or reject the idea honestly.

A "VALIDATED" verdict without 3+ corroborating events is a lie we can't afford.

## Input contract

Parse user request:
- `idea` (required): Business idea description, even if vague
- `country` (required): ISO 2-letter. If missing, infer from language or ask.

## Execution mode selection

Check if `PERPLEXITY_API_KEY` is set:
- **If set AND** user didn't say "use claude code" / "no api": delegate to `python run.py validate-idea --idea "X" --country YY` and stop.
- **Otherwise**: native flow below.

## Native flow — 4-phase protocol

### Phase 1 — Idea decomposition + hypothesis (≤400 tokens)

Emit as `### IDEA DECOMPOSITION`:

```yaml
idea_raw: "<user input verbatim>"
decomposed:
  product: "<what they want to build/sell, 1 sentence>"
  industry: "<primary industry, specific>"
  target_pain: "<the specific pain the product claims to solve>"
  target_customer: "<role + company size + context>"
  core_hypothesis: "People in [X] lose money because of [Y] and would pay [Z] for [W]"
assumptions_to_test:
  - a1: "<1st assumption that must be true>"
  - a2: "<2nd>"
  - a3: "<3rd>"
  - a4: "<4th; usually about purchase intent/budget>"
success_criteria:
  validated: "≥3 corroborating pain events across ≥2 companies, AND existing-solution landscape is weak or incumbent-failed"
  weak: "<3 events OR solution landscape is saturated"
```

### Phase 2 — Candidate pool (6-8 SUPPORTING + 4-6 CHALLENGING queries)

**SUPPORTING queries** (does the pain exist across a population?):
- 2 regulatory-fine queries (agency + specific pain + year)
- 2 legal/verdict queries (lawsuits, settlements, class actions naming the pain)
- 1 aggregator hunt (curated lists of events in this pain class)
- 1 industry-report quantification (total $ / company count / trend)

**CHALLENGING queries** (why would this idea fail?):
- 2 existing-solutions queries (who is already solving this?)
- 1 market-saturation query ("X is a crowded space", competitor funding)
- 1 counter-evidence ("why does Y not work", regulator/industry pushback)
- 0-2 follow-ups with event-markers if first pass is weak

Same rules as industry-scan: native language, financial keywords, year range, `.gov`/court bias for supporting queries, VC-blog and competitor-landscape bias for challenging.

Emit `### CANDIDATE POOL` table: url | domain_class | title | query_type (SUPPORT/CHALLENGE) | score

### Phase 3 — Evidence ledger (compressed cards)

Fetch top 8-12 global-ranked URLs (not per-query). Compress each fetch into a ≤150-token card. Event schema same as industry-scan, plus field `validation_side: SUPPORTING|CHALLENGING`.

**Mandatory:** the ledger must contain both sides. If all CHALLENGING queries yielded zero useful data, run 2 more targeted CHALLENGING queries before proceeding — no idea is truly unchallenged.

Event-key dedup same as industry-scan.

### Phase 3.5 — Unfairgap fit check (the actual validation logic)

Assess the idea against what the ledger shows:

```yaml
unfairgap_fit:
  pain_is_systemic: true | false | weak
  pain_events_count: N
  pain_events_list: [ev_XXX, ev_YYY, ...]
  pain_cross_company: <how many distinct defendant/sanctioned companies>
  pain_cross_jurisdiction: <federal+N states, or N countries>
  pain_is_repeating: "incidents per year trend — growing|stable|declining|unclear"

solution_landscape:
  existing_solutions_found: [<list named>]
  solution_adequacy: "strong|mediocre|weak|absent"
  funding_signal: "well-funded incumbents | early-stage only | empty"
  reason_incumbents_fail: "<if applicable; e.g., 'focused on enterprise, SMB underserved'>"

timing:
  regulatory_trend: "enforcement-increasing|decreasing|stable|rolling-back (may create vacuum)"
  recent_precedent_cases: [<list>]
  market_window_signal: "<6mo|6-18mo|18mo+|unclear>"

final_verdict:
  status: "VALIDATED | PROMISING | WEAK | NO_EVIDENCE | SATURATED"
  reasoning: "<2-3 sentences grounded in the ledger; cite ev_ ids>"
```

**Status rules:**
- **VALIDATED** — pain is systemic (≥3 events, ≥2 companies, ≥2 jurisdictions), solution_adequacy is weak|absent, timing signal is enforcement-increasing or vacuum-creating
- **PROMISING** — 2 of the 3 validation conditions met; missing one is recoverable with more research
- **WEAK** — ≥1 condition fails; document what's missing
- **NO_EVIDENCE** — <2 ledger events support the pain
- **SATURATED** — pain confirmed but solution_adequacy is strong (multiple well-funded incumbents covering target segment)

**Do not promote WEAK to VALIDATED with clever framing. If the ledger doesn't support it, tell the user to pivot.**

### Phase 4 — Final report

Emit only after Phase 3.5 reaches a status.

```
# Idea Validation: {short product name}
Generated: {date}
Skill version: 0.4.0-proto

## Verdict: {STATUS}
{1-sentence reasoning}

## Why this verdict
### Supporting evidence
<table: ev_id | pain | $ | source_url | evidence_quality>

### Challenging evidence (the risks)
<table: ev_id | competitor/counter | link_type | quote>

## Unfairgap fit (the systematic view)
- Pain is systemic across {N} companies in {N} jurisdictions? {yes/no, grounded}
- Solution landscape adequacy: {weak/mediocre/strong}
- Timing signal: {increasing/vacuum/stable/declining}

## What would change the verdict
- If VALIDATED → WEAK: <what evidence would downgrade>
- If WEAK → VALIDATED: <what evidence would upgrade; how to go collect it>

## Recommended next steps (status-specific)
- **VALIDATED**: 2-3 concrete first customer-discovery moves (not "build the MVP")
- **PROMISING**: what gap to close first; who to interview
- **WEAK**: pivot suggestions with evidence grounding
- **NO_EVIDENCE**: the problem might not be real; consider talking to 10 prospects with an open problem interview before trying again
- **SATURATED**: which segment/geography/vertical might be underserved by current incumbents

## Run manifest
<queries, fetches, ledger size, status counts>
```

Save as `validation-{short-idea-slug}-{YYYY-MM-DD}.md`.

## Hard rules

1. `VALIDATED` without ≥3 events across ≥2 companies = skill failure.
2. Challenging queries mandatory. No "unchallenged idea" reports.
3. Primary-source ratio target 50%+ for the evidence supporting VALIDATED status.
4. Native-language queries mandatory for non-English countries.
5. PDF-via-cache workflow (Read tool on cached path) same as industry-scan.
6. Fetch cap 14.

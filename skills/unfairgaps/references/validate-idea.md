# Reference: validate-idea

Operation-specific details for the `unfairgaps validate-idea` operation. Read this AFTER the shared 4-phase protocol in `../SKILL.md`.

## Input parsing

- `idea` (required): business idea description, even if vague
- `country` (required): ISO 2-letter. If missing, infer from language or ask.

## Phase 1 — Idea decomposition schema

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
  validated: ">=3 corroborating events across >=2 companies AND >=2 jurisdictions; solution landscape weak; timing signal enforcement-increasing or regulatory-vacuum"
  weak: "<3 events OR solution landscape saturated"
```

## Phase 2 — Query split (SUPPORTING + CHALLENGING)

Instead of the pure evidence-gathering mix, split queries:

**SUPPORTING queries (6-8)** — does the pain exist across a population?
- 2 regulatory fines (agency + specific pain + year)
- 2 legal/verdict queries
- 1 aggregator hunt
- 1 industry report quantification (total $ / company count / trend)

**CHALLENGING queries (4-6)** — why would this idea fail?
- 2 existing-solutions queries (who is already solving this?)
- 1 market-saturation query
- 1 counter-evidence ("why does Y not work", regulator/industry pushback)
- 0-2 follow-ups with event-markers if first pass is thin

**CHALLENGING queries are MANDATORY.** No "unchallenged idea" verdict.

Emit candidate pool with `validation_side: SUPPORTING | CHALLENGING` column.

## Phase 3 — Evidence card addition

Add field to the shared card schema:
```yaml
validation_side: SUPPORTING | CHALLENGING
```

The ledger must contain both sides. If all CHALLENGING queries yielded zero useful data, run 2 more targeted CHALLENGING queries before proceeding.

## Phase 3.5 — Unfairgap fit check (the actual validation logic)

Instead of generic unfairgap detection, emit a structured fit assessment:

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
  solution_adequacy: "strong | mediocre | weak | absent"
  funding_signal: "well-funded incumbents | early-stage only | empty"
  reason_incumbents_fail: "<if applicable>"

timing:
  regulatory_trend: "enforcement-increasing | decreasing | stable | rolling-back (may create vacuum)"
  recent_precedent_cases: [<list>]
  market_window_signal: "<6mo | 6-18mo | 18mo+ | unclear>"

final_verdict:
  status: "VALIDATED | PROMISING | WEAK | NO_EVIDENCE | SATURATED"
  reasoning: "<2-3 sentences grounded in the ledger; cite ev_ ids>"
```

**Verdict rules:**
- **VALIDATED** — pain is systemic (≥3 events, ≥2 companies, ≥2 jurisdictions), solution_adequacy is `weak` or `absent`, timing is `enforcement-increasing` or `rolling-back-creates-vacuum`
- **PROMISING** — 2 of the 3 conditions met; missing one is recoverable with more research
- **WEAK** — ≥1 condition fails; document what's missing
- **NO_EVIDENCE** — <2 ledger events support the pain
- **SATURATED** — pain confirmed but solution_adequacy is `strong` (multiple well-funded incumbents)

**Do not promote WEAK to VALIDATED with clever framing.** If the ledger doesn't support it, tell the user to pivot.

## Phase 4 — Report format

```
# Idea Validation: {short product name}
Generated: {date}
Skill version: 0.5.0

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
- **NO_EVIDENCE**: consider 10 open problem interviews before trying again
- **SATURATED**: which segment/geography/vertical might be underserved

## Run manifest
queries (SUPPORTING + CHALLENGING counts), fetches, ledger size, status counts
```

Save as `validation-{short-idea-slug}-{YYYY-MM-DD}.md`.

## Hard rules specific to validate-idea

1. `VALIDATED` without ≥3 events across ≥2 companies = skill failure.
2. CHALLENGING queries mandatory. No "unchallenged idea" reports.
3. Primary-source ratio target 50%+ for evidence supporting VALIDATED.

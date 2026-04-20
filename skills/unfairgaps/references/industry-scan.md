# Reference: industry-scan

Operation-specific details for the `unfairgaps industry-scan` operation. Read this AFTER the shared 4-phase protocol in `../SKILL.md`.

## Input parsing

From the user request extract:
- `industry` (required): free-text ("construction", "healthcare", "logistics", "engineered stone fabrication"). Ask if missing.
- `country` (required): ISO 2-letter (US, DE, KZ, RU, UK, FR, BR, ...). Ask if missing.

## Phase 1 — Research plan schema

```yaml
industry: <input>
country_code: <input>
country_name: <full>
primary_languages: [<language codes for web content>]
jurisdictions: [<federal/regional bodies; for US: federal + relevant states; for EU: member-state + EU-level>]
regulatory_bodies: [<3-6 names>]
court_systems: [<2-4 names/URLs>]
expected_pain_hypotheses: [<3-5 short guesses BEFORE searching; these will be tested>]
stop_condition: ">=6 unique canonical events with primary-source evidence OR Phase 3 ledger saturated"
fetch_budget: 14
```

## Phase 2 — Query emphasis

Standard 10-14 query mix from shared protocol. Additional lesson for industry-scan:
- Match one query explicitly to each of the 3-5 pain hypotheses from Phase 1, so you can empirically confirm or refute each hypothesis in the ledger.

## Phase 3 — Evidence card additions

Use the shared card schema. No additional fields for this operation.

## Phase 3.5 — Unfairgap pattern detection

Use shared status rules. Target 3-5 CONFIRMED_SYSTEMIC unfairgaps per run.

## Phase 4 — Report format

```
# UnfairGap Report: {industry} in {country_name}
Generated: {date}
Skill version: 0.5.0

## Summary
<2-3 sentences: what systemic gaps exist, NOT a catalog of fines>

## Unfairgaps found

### UnfairGap 1: {plain-language name of the hole}
- **Status:** CONFIRMED_SYSTEMIC / EMERGING_PATTERN
- **Why it exists:** {the regulatory or market mechanism producing pain}
- **Evidence across ledger:** ev_XXX, ev_YYY, ev_ZZZ ({N} events, ${X}-${Y} range)
- **Product sketch:** {what plugs the hole}
- **Who pays:** {the NOT-YET-SANCTIONED peers of companies in ev_*}
- **Why now:** {urgency trigger}
- **Biggest risk:** {what kills the wedge}

### UnfairGap 2: ...

## Anecdotal signals
Single-event findings; honest "this is one case, not a wedge yet."

## Evidence ledger reference
Compact table: id | event_key | financial_impact | source_class | url | linked_unfairgap

## Coverage caveats
- Primary-source ratio: {X}% (target 60%)
- Missing case classes: [...]
- EMERGING_PATTERN unfairgaps that might upgrade with 1-2 more fetches: [...]

## Run manifest
queries, candidates_pooled, fetched, dedup_merges, skipped_junk, follow_ups_used, events_final, primary_source_ratio, coverage_gaps
```

Save as `report-{industry}-{country_code}-{YYYY-MM-DD}.md` in the current working directory. Also save a run manifest as `manifest-{industry}-{country_code}-{YYYY-MM-DD}.json` with the raw ledger + search/fetch trace for debugging.

## Good-run example

Input: `construction in US`

Expected output shape:
- 26+ events across 14 fetches
- 5 CONFIRMED_SYSTEMIC unfairgaps (e.g., training-evidence-chain for 8-figure verdicts; silica exposure monitoring; pre-commit builder solvency; multi-tier sub payroll compliance; SVEP procurement verification)
- 55-65% primary-source ratio
- 3-4 anecdotal signals

## Sparse-run example (expected failure mode)

Input: `logistics in Turkmenistan`

Expected output shape:
- 3-7 events, 2 EMERGING_PATTERN max
- Honest `coverage_gap` note at top
- No padding, no CONFIRMED claims
- "Insufficient public enforcement data accessible via web search in this jurisdiction" conclusion

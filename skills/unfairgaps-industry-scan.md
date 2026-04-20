---
name: unfairgaps-industry-scan
description: Find documented business pain points in any industry using public enforcement data (court filings, regulatory fines, industry reports). Dual mode - runs natively in Claude Code via WebSearch+WebFetch, or delegates to run.py if PERPLEXITY_API_KEY is set.
version: 0.4.0-proto
---

# THE ONE THING TO REMEMBER

**We are not finding customers to sell to. We are finding UNFAIRGAPS — systemic holes in a regulatory regime where a good product can plug the leak for EVERYONE who hasn't been caught yet.**

A $72M jury verdict is interesting only if it exposes a systemic gap (e.g., "no evidence chain for training compliance"), not because Walker Engineering specifically got hit.

**A good event corroborates a SYSTEMIC PATTERN.** A great ledger groups events into 3-5 confirmed systemic patterns, each with a clear answer to:
- Who will pay to avoid ending up in this data?
- What product could plug this hole?
- Why now — what's changing in enforcement/technology/market that makes this urgent?

An event with no corroboration in the ledger is **anecdotal** — report it separately, do not pretend it's a wedge.

# UnfairGaps Industry Scan

Find REAL business pain points in a specified `industry x country` from primary-source public data: court records, regulatory actions, enforcement fines, industry reports. Output a structured report with source-grounded evidence.

## Input contract

Parse user request into:
- `industry` (required): free-text (e.g., "construction", "healthcare", "logistics"). Ask if missing.
- `country` (required): ISO 2-letter (US, DE, KZ, RU, UK, FR, BR, ...). Ask if missing.

## Execution mode selection

Before doing anything: check if `PERPLEXITY_API_KEY` is set in env.

- **If set AND** user didn't explicitly say "use claude code" or "no api": **delegate to `python run.py industry-scan --industry "X" --country YY`** and return its output. Stop here.
- **Otherwise**: run the native Claude Code flow below.

The native flow uses WebSearch + WebFetch. No Perplexity needed.

## Native flow — MANDATORY 4-phase protocol

This is not a guideline. Skip or reorder phases and the output becomes untrustworthy. Every phase produces a visible artifact. Do not write the final report before Phase 4.

---

### Phase 1 — Research plan (≤400 tokens)

Emit a compact research plan as a markdown code-block titled `### RESEARCH PLAN`. Fields:

```yaml
industry: <input>
country_code: <input>
country_name: <full>
primary_languages: [<language codes for web content in that country>]
jurisdictions: [<federal/regional bodies that matter; for US → federal + relevant states; for EU → member-state + EU-level>]
regulatory_bodies: [<3-6 names>]
court_systems: [<2-4 names/URLs>]
expected_pain_hypotheses: [<3-5 short guesses BEFORE searching; these will be tested>]
stop_condition: >=6 unique canonical events with primary-source evidence OR Phase 3 ledger saturated
fetch_budget: 12 (hard cap, follow-ups count)
```

---

### Phase 2 — Candidate pool (≤600 tokens)

Run **10-14 WebSearch queries**. Compose them across **7 categories** (v0.3 — expanded after US/KZ fixture runs showed 8 queries missed major case types):

- 2 REGULATORY FINES (agency name + fine/penalty/enforcement + year)
- 2 LEGAL CASES (lawsuits, settlements, court cases)
- 2 JURY VERDICTS (**new in v0.3**: "verdict million {industry} 2024 2025" — 8-figure jury awards were missed in v0.2 runs)
- 2 REPEAT VIOLATOR / SVEP (**new in v0.3**: for US, include "SVEP {industry}", "repeat violator"; for other countries: equivalent "multiple-violation" or "рецидив нарушений")
- 1 BANKRUPTCY / CHAPTER 7 (**new in v0.3**: "{industry} contractor Chapter 7 bankruptcy 2024 2025" for US; "банкротство застройщик" for RU/KZ)
- 1 AGGREGATOR HUNT (**new in v0.3**: search for aggregator blogs / lists — "biggest OSHA fines {year}", "top construction lawsuits {year}", "Taproot OSHA fines" — these sites pre-curate primary-source lists)
- 1 INDUSTRY COST (reports, losses, financial impact)
- 1 SPECIFIC INCIDENT (single high-$ event with known name)
- 0-2 EVENT-MARKER FOLLOW-UPS (after initial pool, if >30% of results are norms/penalty-tables rather than events, run targeted queries using **action verbs**: "fined", "sentenced", "settled", "оштрафована", "приговор", "verurteilt")

**Query rules:**
- Include industry verbatim
- Include at least one financial keyword: `lawsuit, fine, penalty, settlement, million, cost, loss, verdict, Chapter 7` (or native-language equivalent)
- Include year range: `2024 2025 2026`
- **Queries MUST be in the primary language(s) from the research plan.** English-only searches for non-English countries produce fake "no evidence" conclusions.
- At least 2 queries target `.gov` / regulator / court-system sources explicitly
- **v0.3 lesson (from KZ fixture run):** if the first pass returns penalty tables / code articles rather than named-party events, that's a diagnostic signal — immediately compose follow-ups with action-verb markers instead of spending budget on more fetches from the norm-heavy pool.

Collect results into a candidate table:

```
### CANDIDATE POOL
| # | url | domain_class | title (≤80c) | query_source | score |
|---|-----|--------------|--------------|--------------|-------|
```

**domain_class** (assign each URL):
- `primary_gov` — .gov, federal/state regulator, court docket
- `primary_court` — court opinion databases, official dockets
- `quasi_primary` — regulator press release, enforcement database mirror
- `aggregator_primary` (**new in v0.3**) — curated lists of primary-source events (Taproot OSHA fines, JDSupra regulatory trackers, CourtListener top verdicts). These are secondary but list MANY primary events efficiently; fetch one of them and you get 10-15 named-party events in one page.
- `secondary_trade` — industry trade press with named case/$ (Insurance Journal, Construction Dive, ENR, law-firm-published case analyses that name the defendant)
- `secondary_news` — major news outlets with named case/$
- `tertiary_blog` — law-firm marketing blogs (no case names), consulting opinion, LinkedIn
- `junk` — SEO content, vendor marketing, norm/penalty tables without events

**score** (0-10):
- +4 if primary_gov or primary_court
- +3.5 if aggregator_primary (**new in v0.3** — high-leverage: one fetch yields many events)
- +3 if quasi_primary
- +2 if secondary_trade and names a specific case/amount
- +1 if secondary_news and names a specific case/amount
- 0 if tertiary_blog
- drop junk
- **Drop norm/penalty tables** — adilet.zan.kz-style pages listing penalty amounts WITHOUT a named party/incident provide zero events. They look relevant in search results but always waste fetch budget.

Pool size should be 20-40 candidates. Dedupe by URL before scoring.

---

### Phase 3 — Evidence ledger (the critical step)

Fetch the **top 8-10 candidates by global score** (NOT top 2-3 per query). Do not fetch junk or tertiary unless everything else is exhausted.

**For each fetched page, IMMEDIATELY write a compact evidence card (≤150 tokens)** and append to the ledger below. Do not keep raw page text in context — compress then discard.

```
### EVIDENCE LEDGER
```

Evidence card format (one card = one event, not one page):

```yaml
- id: ev_001
  event_key: "<authority>|<action_type>|<date>|<actor>|<docket_or_id>"   # for dedup
  pain: "<1-2 sentences, what went wrong and who lost money>"
  actor: "<company/role that suffers or was sanctioned>"
  jurisdiction: "<federal|state name|country|EU-level>"
  evidence_type: "court_record|regulatory_fine|industry_report|news"
  source_class: "<primary_gov|primary_court|quasi_primary|secondary_trade|secondary_news>"
  financial_impact: "<exact amount + currency, or null>"
  date: "<YYYY-MM or YYYY>"
  language: "<en|ru|kk|de|...>"
  pinpoint_citation:
    url: "<full URL>"
    locator: "<page N, section X, paragraph P — or quoted selector>"
    quote: "<≤200 char verbatim excerpt proving the claim>"
  evidence_quality: "hard|soft"
  notes: "<optional — contradicts ev_XXX, or corroborates, or coverage_gap>"
```

**Compression rule:** if you can't fit a card in ~150 tokens, the card is too vague. Either sharpen it or drop it.

**Event-level dedup:** before appending, check if `event_key` matches an existing card. If yes — merge `pinpoint_citation` into a `corroborating_urls: []` list on the existing card, don't create a duplicate.

**Follow-up fetches (max 4):** after initial 8-10 fetches, if the ledger has <6 hard events OR a pain-hypothesis from Phase 1 has zero evidence, do up to 4 targeted follow-up fetches from the candidate pool.

**Hard stop:** 12 fetches total. If still under 6 events, emit a `coverage_gap` note and proceed to Phase 4 — do NOT fabricate breadth.

---

### Phase 3.5 — Pattern detection (unfairgap synthesis) — NEW in v0.4

**This is the product of the skill. Without this step, the ledger is just a curated news digest.**

Read through the Evidence Ledger from Phase 3 and group events into **unfairgap hypotheses** — candidate systemic regulatory holes that recur across multiple cases.

For each candidate pattern, emit an `UNFAIRGAP` entry:

```yaml
- unfairgap_id: ug_001
  hypothesis: "<1 sentence: the systemic hole in plain language>"
  status: "CONFIRMED_SYSTEMIC" | "EMERGING_PATTERN" | "ANECDOTAL"   # see rules below
  corroborating_events: [ev_XXX, ev_YYY, ev_ZZZ]
  event_count: N
  scale_signal: "<$ range across events; sum if meaningful>"
  regulatory_source: "<which regulator(s) enforce this; which statutes>"
  product_sketch:
    what: "<concrete product, 1-2 sentences>"
    who_pays: "<specific buyer persona — NOT the sanctioned companies, their NOT-YET-SANCTIONED peers>"
    why_now: "<what makes this urgent in 2024-2026 specifically — new rule, new enforcement trend, new technology unlock>"
    what_kills_it: "<biggest risk to the wedge — usually: regulator changes posture, incumbents bundle it, or pain doesn't actually reach buyer consciousness>"
  coverage_caveats: "<what we don't know that would change the call>"
```

**Status rules (non-negotiable):**
- `CONFIRMED_SYSTEMIC` — 3+ events from the ledger corroborate the same gap, AND at least 1 is a primary/quasi-primary source, AND events span 2+ companies or 2+ jurisdictions (or 1 company 3+ times = pattern of regulator behavior)
- `EMERGING_PATTERN` — 2 events corroborating, or 3+ events but all from tertiary/blog/single-source
- `ANECDOTAL` — 1 event only, OR a big-$ event that can't generalize (unique regulatory context, bespoke facts)

**Do not promote ANECDOTAL to CONFIRMED with clever arguments. If the data isn't there, say so.**

**Drop-rule:** events in the ledger that don't slot into any unfairgap pattern do not appear in Phase 4 pain topics. They go into an "Anecdotal signals" appendix only.

**Target:** 3-5 CONFIRMED_SYSTEMIC unfairgaps per industry×country run. If you have 0-2, the run didn't find enough pattern — say so in the report, don't pad.

### Phase 4 — Final report

Emit ONLY after Phase 3.5 has produced at least 2 CONFIRMED_SYSTEMIC or EMERGING_PATTERN unfairgaps. Synthesize from unfairgaps + cards, not from raw fetch memory.

**Quality gates before writing the report:**
- At least 60% of events are `primary_gov | primary_court | quasi_primary` source_class (target ratio). If below → add `## Coverage caveats` section explicitly.
- At most 25% of events are `secondary_news`. If above → prune or mark as corroborating, not primary.
- Cluster events into 3-8 pain topics by semantic similarity. One event belongs to one topic.

Report structure (markdown):

```
# UnfairGap Report: {industry} in {country_name}
Generated: {date}
Skill version: 0.4.0-proto

## Summary
<2-3 sentences: what systemic gaps exist, NOT a catalog of fines>

## Unfairgaps found (the product)

### UnfairGap 1: <plain-language name of the hole>
- **Status:** CONFIRMED_SYSTEMIC / EMERGING_PATTERN
- **Why it exists:** <the regulatory or market mechanism that keeps producing pain>
- **Evidence across ledger:** ev_XXX, ev_YYY, ev_ZZZ (<N> events, $X-$Y range)
- **Product sketch:** <what plugs the hole>
- **Who pays:** <the NOT-YET-SANCTIONED peers of companies in ev_*>
- **Why now:** <urgency trigger>
- **Biggest risk:** <what kills the wedge>

### UnfairGap 2: ...

## Anecdotal signals (single-event, not yet a pattern)
<Short list. Honest "this is one case, not a wedge yet."></  Do not dress these up as opportunities.>

## Evidence ledger reference
<Compact table: id | event_key | financial_impact | source_class | url | linked_unfairgap>

## Coverage caveats
- Primary-source ratio: X% (target 60%)
- Missing case classes: [...]
- Unfairgaps at EMERGING_PATTERN that might upgrade to CONFIRMED with 1-2 more fetches

## Run manifest
<queries, fetches, dedupe decisions, unfairgap status counts>
```

**Writing the report, hard rule:** every unfairgap has an event list ≥3 (CONFIRMED) or ≥2 (EMERGING). If you're writing an unfairgap with 1 event, you're violating the skill — move it to Anecdotal signals.

Save the final report to `report-{industry}-{country_code}-{YYYY-MM-DD}.md` in the current working directory. Also save the run manifest as `manifest-{industry}-{country_code}-{YYYY-MM-DD}.json` with the raw ledger + search/fetch trace for debugging.

---

## Hard rules (violations = wrong output)

1. **Do not write the final report before Phase 3 is complete.** The ledger exists as a persistent artifact; if context pressure hits, re-read the ledger from prior output rather than synthesizing from memory.
2. **Do not fabricate source quotas.** If a jurisdiction genuinely has 1 primary source, report 1 primary source and flag `coverage_gap`. Padding with unrelated US cases = failure mode.
3. **Native-language queries are mandatory** for non-English countries. English-only = fake "no evidence".
4. **Do not exceed 14 fetches** (v0.3: was 12; raised after validation runs showed budget was the bottleneck, not context). If budget exhausted and ledger thin, ship what you have with caveats.
5. **Do not synthesize from raw fetched page text.** Compress each fetch into a card immediately, then drop raw text.
6. **Every finding needs `pinpoint_citation` with url + locator + quote.** URL-only is not a citation.
7. **v0.3: PDF handling.** If WebFetch on a government/court PDF returns "cannot parse binary content," the PDF is cached to tool-results/. Use Read tool on the returned cache path — this extracts full document content. Treat this as the canonical PDF workflow; do NOT give up on primary-source PDFs just because WebFetch complains.
8. **v0.3: Blocked-primary-source handling.** Some regulator domains (osha.gov, dir.ca.gov) return HTTP 403 or timeout on direct WebFetch. When this happens: (a) search for `aggregator_primary` sites that cite the same release verbatim; (b) preserve the **canonical event_key** so evidence from the aggregator can be merged with the primary source when it becomes reachable later. Do NOT drop the event.
9. **v0.3: Cover these case-classes for US** (gap analysis vs Perplexity-mode): jury verdicts ≥ $10M, OSHA SVEP enrollees, Chapter 7 contractor bankruptcies, wage-theft citations from state Labor Commissioners. If your ledger has zero events from any of these classes after Phase 3, your queries missed a category — run a follow-up.

## Example — good run (for calibration)

User: `scan construction in Germany`

- Plan: languages=[de, en], bodies=[BG BAU, Gewerbeaufsicht, StatBA], courts=[Bundesarbeitsgericht, Landesgerichte]
- Queries mix German legal/regulatory + 2 English for international trade/industry
- Pool: 28 candidates, 15 kept after junk drop
- Fetch: 9 initial + 3 follow-ups = 12 total
- Ledger: 8 events, 5 primary_gov, 2 court_record, 1 industry_report, 2 dedup merges
- Report: 4 pain topics, coverage_gap flagged for "payment delays" (only industry survey, no court records found within budget)

## Example — sparse run (expected failure mode)

User: `scan logistics in Turkmenistan`

- Plan: language=[ru, tk], limited regulators
- Queries: 8 composed, 6 return thin results
- Pool: 12 candidates, 7 kept
- Fetch: 7 + 0 follow-ups (pool exhausted) = 7 total
- Ledger: 3 events, 2 quasi_primary, 1 secondary_news
- Report: 2 pain topics, strong `coverage_gap` caveat at top, honest "insufficient primary data" conclusion

Both runs are valid. The second is not a bug — it's an honest signal that the jurisdiction lacks public enforcement data accessible via web search.

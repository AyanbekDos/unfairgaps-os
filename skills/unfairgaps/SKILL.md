---
name: unfairgaps
description: Find documented UNFAIRGAPS — systemic regulatory holes where a product can plug the leak — using court filings, regulatory fines, and enforcement data. Four operations in one methodology - industry-scan, validate-idea, site-audit, customer-pains. Dual mode - native Claude Code (WebSearch+WebFetch) or delegates to run.py if PERPLEXITY_API_KEY is set.
version: 0.5.0
---

# THE ONE THING TO REMEMBER

**We are not finding customers to sell to. We are finding UNFAIRGAPS — systemic holes in a regulatory regime where a good product can plug the leak for EVERYONE who hasn't been caught yet.**

A $72M jury verdict is interesting only if it exposes a systemic gap (e.g., "no evidence chain for training compliance"), not because one company got hit.

**A good event corroborates a SYSTEMIC PATTERN.** A great report groups events into 3-5 confirmed systemic patterns, each with a clear answer to:
- Who will pay to avoid ending up in this data?
- What product could plug this hole?
- Why now — what's changing in enforcement/technology/market that makes this urgent?

An event with no corroboration in the ledger is **anecdotal** — report it separately, do not pretend it's a wedge.

---

# One methodology, four operations

All four operations share the same 4-phase protocol (below). Only the input, the query taxonomy, and the final-report shape differ. Parse the user's intent into one of these operations, then load the matching op-specific reference from `references/` for that operation's details.

| Operation | Input | Output | Reference |
|---|---|---|---|
| **industry-scan** | industry + country | Pain report: 3-5 CONFIRMED unfairgaps in that industry × country, each with product sketch | [industry-scan.md](references/industry-scan.md) |
| **validate-idea** | business idea + country | VALIDATED / PROMISING / WEAK / NO_EVIDENCE / SATURATED verdict grounded in enforcement data | [validate-idea.md](references/validate-idea.md) |
| **site-audit** | URL | Claims-vs-reality audit: per-claim verdicts + missed unfairgaps the site ignores | [site-audit.md](references/site-audit.md) |
| **customer-pains** | URL | B2B2C unfairgaps affecting YOUR customers' customers, with pitch templates for outbound | [customer-pains.md](references/customer-pains.md) |

**How to pick the operation from user input:**
- "scan X in Y" / "find pains in <industry> <country>" → industry-scan
- "validate <idea>" / "is <idea> real pain" / "should I build <X>" → validate-idea
- "audit <url>" / "check claims on <url>" / "is <url> real or fluff" → site-audit
- "find pains for <url>'s customers" / "customer pains <url>" / "outbound angles for <url>" → customer-pains

If the user's request is ambiguous, ask which operation they want. Do not guess.

---

# Execution mode selection (shared)

Before running any operation:

- **If `PERPLEXITY_API_KEY` is set in env AND** user didn't explicitly say "use claude code" / "no api" / "native":
  - Delegate to `python run.py <operation> <args>` (the CLI path; faster, deterministic, scriptable). Stop here.
- **Otherwise**: run the native flow below using Claude Code's WebSearch + WebFetch.

The native flow uses 0 API keys — entirely free via your Claude Code / Cursor / Codex subscription.

---

# Native flow — shared 4-phase protocol

This protocol is mandatory for all four operations. Skip or reorder phases and the output becomes untrustworthy. Every phase produces a visible artifact. Do not synthesize the final report before Phase 4.

## Phase 1 — Research plan (≤400 tokens)

Produce a compact plan BEFORE searching. See the op-specific reference for its exact schema. Generally includes:

- The input interpreted into a structured form
- Primary languages for retrieval (e.g., `[en]` for US, `[ru, kk]` for KZ, `[de, en]` for DE)
- Regulatory bodies, court systems, jurisdictions in scope
- 3-5 pain hypotheses BEFORE searching (to be tested)
- Stop condition (minimum evidence threshold for a valid result)
- Fetch budget (hard cap)

## Phase 2 — Candidate pool (10-14 WebSearch queries)

Compose queries across these categories (expanded in v0.3 after empirical gap-analysis vs Perplexity):

- 2 REGULATORY FINES (agency + specific pain + year)
- 2 LEGAL CASES (lawsuits, settlements, class actions)
- 2 JURY VERDICTS (8-figure + jury awards, "verdict million {industry} 2024 2025")
- 2 REPEAT VIOLATOR / SVEP (for US: "SVEP {industry}", "repeat violator"; other countries: equivalent)
- 1 BANKRUPTCY / CHAPTER 7 ("{industry} contractor Chapter 7 bankruptcy 2024 2025")
- 1 AGGREGATOR HUNT ("biggest OSHA fines {year}", "top {industry} lawsuits {year}" — aggregator sites pre-curate primary-source lists)
- 1 INDUSTRY COST (reports, losses, financial impact)
- 1 SPECIFIC INCIDENT (single high-$ event with known name)
- 0-2 EVENT-MARKER FOLLOW-UPS (if >30% of first-pass results are norms/penalty-tables, compose follow-ups with action verbs: "fined", "sentenced", "settled", "оштрафована", "приговор", etc.)

**Query rules:**
- Include the target noun verbatim (industry / segment / pain / whatever the op focuses on)
- Include at least one financial keyword (lawsuit, fine, penalty, settlement, million, cost, loss, verdict, Chapter 7 — or native-language equivalent)
- Include year range `2024 2025 2026`
- **Native-language queries are mandatory** for non-English countries. English-only = fake "no evidence".
- At least 2 queries target `.gov` / regulator / court-system sources explicitly
- **v0.3 lesson:** if the first pass returns penalty tables / code articles rather than named-party events, that's a diagnostic signal — immediately compose follow-ups with action-verb markers.

Emit candidate pool as a table, scored by `domain_class`:

- `primary_gov` (+4) — .gov, federal/state regulator, court docket
- `primary_court` (+4) — court opinion databases, official dockets
- `aggregator_primary` (+3.5) — curated lists of primary-source events (Taproot OSHA fines, JDSupra, CourtListener top verdicts — one fetch yields 10-15 named events)
- `quasi_primary` (+3) — regulator press releases, enforcement DB mirrors
- `secondary_trade` (+2) — industry trade press with named case/$ (Insurance Journal, Construction Dive, ENR, law-firm analyses naming defendants)
- `secondary_news` (+1) — major news outlets with named case/$
- `tertiary_blog` (0) — law-firm marketing blogs, consulting opinion, LinkedIn
- **drop `junk`** — SEO content, vendor marketing, norm/penalty tables without events

Pool should be 20-60 candidates. Dedupe by URL before scoring.

## Phase 3 — Evidence ledger (the critical step)

Fetch the **top 8-12 candidates by global score** (NOT top-N per query). Budget caps at 14 total fetches including follow-ups.

**For each fetched page, IMMEDIATELY write a compact evidence card (≤150 tokens)** and append to the ledger. Do not keep raw page text in context — compress then discard.

Card schema (shared; op-specific references may add fields):

```yaml
- id: ev_XXX
  event_key: "<authority>|<action_type>|<date>|<actor>|<docket_or_id>"   # event-level canonical key for dedup
  pain: "<1-2 sentences, what went wrong and who lost money>"
  actor: "<company/role sanctioned or suffering>"
  jurisdiction: "<federal | state name | country | EU-level>"
  evidence_type: "court_record | regulatory_fine | industry_report | news"
  source_class: "primary_gov | primary_court | aggregator_primary | quasi_primary | secondary_trade | secondary_news"
  financial_impact: "<exact amount + currency, or null>"
  date: "<YYYY-MM or YYYY>"
  language: "<en | ru | de | ...>"
  pinpoint_citation:
    url: "<full URL>"
    locator: "<page N, section X, paragraph P — or quoted selector>"
    quote: "<≤200 char verbatim excerpt proving the claim>"
  evidence_quality: "hard | soft"
  notes: "<optional — contradicts ev_XXX, corroborates, or coverage_gap>"
```

**Event-level dedup:** before appending, check if `event_key` matches an existing card. If yes, merge `pinpoint_citation` into `corroborating_urls: []` on the existing card. Don't create duplicates.

**Follow-up fetches (max 4 of the 14 cap):** after initial 8-10 fetches, if the ledger has <6 hard events OR a pain-hypothesis from Phase 1 has zero evidence, do up to 4 targeted follow-up fetches.

**Hard stop at 14 fetches.** If still thin, emit `coverage_gap` notes and proceed to Phase 4 — do NOT fabricate breadth.

## Phase 3.5 — Unfairgap pattern detection (THE PRODUCT)

Read through the Evidence Ledger and group events into candidate **unfairgap hypotheses** — systemic regulatory holes that recur across multiple cases.

For each candidate pattern, emit an `UNFAIRGAP` entry:

```yaml
- unfairgap_id: ug_XXX
  hypothesis: "<1 sentence: the systemic hole in plain language>"
  status: "CONFIRMED_SYSTEMIC | EMERGING_PATTERN | ANECDOTAL"
  corroborating_events: [ev_XXX, ev_YYY, ev_ZZZ]
  event_count: N
  scale_signal: "<$ range across events; sum if meaningful>"
  regulatory_source: "<which regulator(s); which statutes>"
  product_sketch:
    what: "<concrete product, 1-2 sentences>"
    who_pays: "<specific buyer persona — NOT the sanctioned companies, their NOT-YET-SANCTIONED peers>"
    why_now: "<what makes this urgent in 2024-2026 specifically>"
    what_kills_it: "<biggest risk to the wedge>"
  coverage_caveats: "<what we don't know that would change the call>"
```

**Status rules (non-negotiable):**
- **CONFIRMED_SYSTEMIC** — 3+ events corroborate the same gap, AND at least 1 is primary / quasi-primary / aggregator-primary source, AND events span 2+ companies or 2+ jurisdictions (or 1 company 3+ times = pattern of regulator behavior)
- **EMERGING_PATTERN** — 2 events corroborating, or 3+ events but all tertiary/blog/single-source
- **ANECDOTAL** — 1 event only, OR a big-$ event that cannot generalize

**Do not promote ANECDOTAL to CONFIRMED with clever arguments.** If the data isn't there, say so.

**Drop-rule:** events that don't slot into any unfairgap pattern don't appear in Phase 4 main topics. They go to an "Anecdotal signals" appendix only.

**Target:** 3-5 CONFIRMED_SYSTEMIC unfairgaps per run. If you have 0-2, the run didn't find a pattern — say so in the report, don't pad.

## Phase 4 — Final report

Op-specific (see reference). General shape:
- Summary (data-grounded, 2-3 sentences — NOT a catalog of fines)
- Unfairgaps found (CONFIRMED + EMERGING, each with product sketch)
- Anecdotal signals (single-event appendix, honest)
- Evidence ledger reference
- Coverage caveats (what you don't know)
- Run manifest (queries, fetches, dedup decisions, counts)

Save under an op-specific filename (see reference).

---

# Hard rules (apply to all operations)

1. **Do not write the final report before Phase 3.5 is complete.** The ledger and unfairgap entries are persistent artifacts.
2. **Do not fabricate source quotas.** If a jurisdiction genuinely has 1 primary source, report 1 primary source and flag `coverage_gap`. Padding with unrelated cases = failure.
3. **Native-language queries mandatory** for non-English countries.
4. **Do not exceed 14 fetches.** If exhausted and ledger thin, ship with caveats.
5. **Do not synthesize from raw fetched page text.** Compress each fetch into a card immediately; drop raw text.
6. **Every finding needs `pinpoint_citation` with url + locator + quote.** URL-only is not a citation.
7. **PDF handling:** If WebFetch on a .gov/court PDF returns "cannot parse binary content," the PDF is cached to the tool-results path returned. Use Read tool on that cache path — it extracts full document content. Treat as canonical PDF workflow.
8. **Blocked primary sources:** Some regulator domains (osha.gov, dir.ca.gov) return HTTP 403 or timeout on direct WebFetch. When this happens: (a) search for `aggregator_primary` sites that cite the same release verbatim; (b) preserve the canonical `event_key` so evidence from the aggregator merges with the primary when reachable later. Do NOT drop the event.
9. **CONFIRMED_SYSTEMIC requires ≥3 events + ≥2 companies.** Non-negotiable. 1-event "opportunity" in the main section = skill failure.

---

# Then — load the op-specific reference

Once you've determined which of the 4 operations the user wants and you've briefed yourself on the shared protocol above, **read the matching reference** for input-parsing, query-category specifics, reference-card-schema additions, and the final-report format:

- `references/industry-scan.md`
- `references/validate-idea.md`
- `references/site-audit.md`
- `references/customer-pains.md`

Each reference is small (<150 lines) — read the one that applies, then execute.

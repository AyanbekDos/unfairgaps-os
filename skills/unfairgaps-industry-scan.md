---
name: unfairgaps-industry-scan
description: Find documented business pain points in any industry using court filings, regulatory fines, and enforcement data
---

# UnfairGaps Industry Scan

You are running the UnfairGaps Industry Scan pipeline. This finds REAL business pain points from public enforcement data - court filings, regulatory fines, documented financial losses.

## Input

Parse the user's request to extract:
- **industry** (required): The industry to scan (e.g., "construction", "logistics", "healthcare")
- **country** (required): ISO 2-letter code (e.g., US, DE, KZ). If not specified, ask.

## Pipeline Steps

Run these steps IN ORDER. Each step feeds into the next.

### Step 1: Country Context

Before anything else, determine for the target country:
1. Primary language for internet content
2. Top 3-5 regulatory agencies for this industry
3. Publicly accessible court/legal databases
4. Key industry publications
5. Local currency and format

Use this context in ALL subsequent steps.

### Step 2: Compose Search Queries

Create exactly 8 search queries mixing 4 categories:
- **LEGAL** (2): "[industry] lawsuit settlement [year]" targeting the country's court system
- **REGULATORY** (2): "[industry] [local agency] fine penalty enforcement"
- **INDUSTRY COST** (2): "[industry] industry report financial loss cost [year]"
- **SPECIFIC INCIDENT** (2): "[industry] [problem type] cost damage penalty"

Rules:
- Include industry name verbatim
- Include financial keywords (lawsuit, fine, penalty, settlement, million, cost, loss)
- Include year range: 2024 2025 2026
- Compose in the PRIMARY LANGUAGE of the target country
- Target government/regulatory sources for at least 2 queries

### Step 3: Web Search

Use Perplexity Sonar (or any web search tool) to execute each query. For each result, collect:
- The full text response
- All citation URLs

### Step 4: Extract Evidence

From all search results, extract EVERY finding that involves money lost, fines paid, or costs incurred:

For each finding:
- **problem**: 2-3 sentence description a non-expert would understand
- **financial_impact**: EXACT amount from the text (copy, don't estimate). Null if none.
- **evidence_type**: court_record | regulatory_fine | industry_report | news
- **source_url**: Matching citation URL
- **who_suffers**: Specific role/business type that loses money
- **evidence_quality**: "hard" (specific case + amount) | "soft" (survey, estimate, trend)

Skip findings that are too vague or have no supporting data.

### Step 5: Cluster into Pain Topics

Group findings by semantic similarity into Pain Topics. Each cluster gets a clear 5-10 word name. A finding belongs to exactly one cluster.

### Step 6: Generate Opportunities

For each pain topic, generate:
- **Problem**: What's happening (with $ amounts)
- **Who suffers**: Specific roles/companies
- **Solution gap**: What's missing in the market
- **Business model**: How to monetize
- **Quick validation**: First step to test this
- **Why now**: What changed recently

### Step 7: Format Report

Compile everything into a clean markdown report:
- Summary (2-3 sentences)
- Key Findings (top 3-5 with $ amounts)
- Detailed Analysis (organized by pain topics)
- Evidence Sources table
- Confidence Assessment
- Next Steps (3-5 actionable recommendations)

## Output

Save the report as `report-{industry}-{country}-{date}.md` and display it to the user.

## Example

User: "Find pain points in construction in Germany"

Output: A report with documented construction violations from BG BAU, Gewerbeaufsicht fines, court settlements - all with specific amounts in EUR and source URLs.

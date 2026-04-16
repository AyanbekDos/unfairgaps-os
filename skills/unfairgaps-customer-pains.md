---
name: unfairgaps-customer-pains
description: Find your customers' documented pain points from court filings and enforcement data
---

# UnfairGaps Customer Pain Finder

You are running the UnfairGaps Customer Pain Finder pipeline. This discovers what your customers are ACTUALLY losing money on - documented in court records, regulatory fines, and enforcement actions.

## Input

Parse the user's request to extract:
- **url** (required): The user's website URL

## Pipeline Steps

### Step 1: Scrape the Website

Get clean text content (try Scrapling -> HTTP fetch -> web search fallback). Keep first 5000 chars.

### Step 2: Analyze Business Model

Determine:
- **what_you_sell**: One sentence
- **problem_you_solve**: One sentence
- **market**: ISO country code (auto-detect from site content)
- **segments**: 2-5 customer segments who PAY for this product

IMPORTANT: Segments = people/businesses who PAY MONEY, not topics the website shows data about.

### Step 3: Scan Each Segment

FOR EACH customer segment:

**3a. Compose 8 Search Queries:**
Mix across 4 categories (LEGAL, REGULATORY, INDUSTRY COST, SPECIFIC INCIDENT).
All queries must:
- Include segment name verbatim
- Include financial keywords
- Target the detected country's regulatory agencies
- Be in the primary language of the country

**3b. Execute Web Searches:**
Run each query through Sonar/web search. Collect text + citations.

**3c. Extract Evidence:**
Pull every finding with: problem, financial_impact, evidence_type, source_url, who_suffers, evidence_quality.

### Step 4: Filter by Relevance

Score each finding 0.0-1.0 for relevance to the user's product:
- 0.8-1.0: Directly related to what the product solves
- 0.5-0.8: Related to the industry/segment
- 0.0-0.5: Tangentially related or irrelevant

Keep findings with score >= 0.5.

### Step 5: Cluster into Pain Topics

Group relevant findings by semantic similarity. Each cluster = one pain topic.

### Step 6: Generate Opportunities

For each pain topic:
- **Deduplicate evidence** within the topic
- **Generate 1 opportunity per unique evidence piece**
- Include: problem description, who suffers, financial impact, source URL
- **Layman hook**: One sentence a non-expert would understand ("Your customers are paying $X because...")

### Step 7: Format Report

Report includes:
- Site overview (product, segments, market)
- Per-segment findings summary
- Top pain topics with evidence
- Opportunities ranked by financial impact
- Evidence sources table
- Recommended next steps (how to act on these findings)

## Output

Save as `pains-{domain}-{date}.md` and display to the user.

## Example

User: "Find pain points for customers of https://my-saas.com"

Output: 3 customer segments identified. 47 findings across 12 pain topics. Top opportunity: "Restaurant owners in your target segment are paying $4.2B/year in FDA violations - your compliance module directly addresses this."

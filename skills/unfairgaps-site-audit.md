---
name: unfairgaps-site-audit
description: Audit a website's pain claims vs reality using court filings and enforcement data
---

# UnfairGaps Site Pain Audit

You are running the UnfairGaps Site Pain Audit pipeline. This checks whether a company is solving REAL problems or selling vitamins.

## Input

Parse the user's request to extract:
- **url** (required): The website URL to audit

## Pipeline Steps

### Step 1: Scrape the Website

Get the website's text content. Try in order:
1. Scrapling (if available): `Fetcher().get(url)` then `StealthFetcher().fetch(url)`
2. Direct HTTP fetch + HTML tag stripping
3. Web search as fallback: "analyze this website: {url}"

Keep first 5000 chars of clean text.

### Step 2: Analyze Business Model

From the website content, determine:
- **what_you_sell**: One sentence
- **problem_you_solve**: One sentence
- **market**: ISO country code (detect from domain, language, currency, addresses)
- **segments**: 2-5 customer segments who PAY for this product

### Step 3: Extract Claimed Pains

Find every pain point the company CLAIMS to address. Look in:
- Hero section, headlines
- "Problems we solve" sections
- Feature descriptions (each feature implies a problem)
- Testimonials, case studies
- FAQ, pricing page

For each claim, extract: claimed_pain, claimed_solution, evidence_on_site, specificity (HIGH/MEDIUM/LOW), quote.

### Step 4: Reality Check Queries

For each claimed pain, compose search queries to VERIFY if it's real:
- **Verification queries** (4): Search for actual court filings, fines, losses matching the claimed pain
- **Discovery queries** (4): Search for REAL pains in the industry that the site DOESN'T mention

### Step 5: Search + Extract Evidence

Execute queries, extract findings with amounts and sources.

### Step 6: Match Claims vs Reality

For each claimed pain, assign a verdict:
- **CONFIRMED**: Real evidence supports this claim (with $ amounts)
- **EXAGGERATED**: Some truth but overstated
- **NO_EVIDENCE**: Could not find supporting data
- **UNDERSTATED**: The real problem is BIGGER than they claim

Also list any MISSED PAINS: real documented problems in the industry that the site doesn't address.

### Step 7: Format Report

Report includes:
- Site overview (what they sell, to whom)
- Claims vs Reality table (claim | verdict | evidence)
- Confirmed pains with source URLs
- Exaggerated/unverified claims
- Missed opportunities (real pains they don't address)
- Overall assessment: EVIDENCE_BASED / MIXED / MOSTLY_FLUFF

## Output

Save as `audit-{domain}-{date}.md` and display to the user.

## Example

User: "Audit https://competitor.com"

Output: 6 claimed pains found. 3 CONFIRMED (with court records), 2 NO_EVIDENCE, 1 EXAGGERATED. Plus 4 missed pains worth $50M+ annually that they don't address.

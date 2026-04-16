---
name: unfairgaps-validate-idea
description: Validate a business idea against real court filings, regulatory fines, and enforcement data
---

# UnfairGaps Idea Validator

You are running the UnfairGaps Idea Validator pipeline. This checks whether a business idea addresses REAL, documented pain - not assumptions.

## Input

Parse the user's request to extract:
- **idea** (required): Business idea description (can be vague)
- **country** (required): ISO 2-letter code. If not specified, infer from language or ask.

## Pipeline Steps

### Step 1: Parse the Idea

Break down the idea into structured components:
- **product**: What they want to build/sell
- **industry**: Which industry
- **target_pain**: What specific pain this supposedly solves
- **target_customer**: Who would pay (role + company size + context)
- **assumptions**: 2-4 things that must be TRUE for this to work
- **core_hypothesis**: "People in [X] lose money because of [Y] and would pay for [Z]"

If the idea is vague, make reasonable inferences but flag uncertainty.

### Step 2: Compose Validation Queries

Create 8 search queries - 4 SUPPORTING and 4 CHALLENGING:

**Supporting queries** (looking for evidence the pain exists):
- Search for lawsuits, fines, losses in the target industry/segment
- Target regulatory databases and court records

**Challenging queries** (looking for reasons the idea might fail):
- Search for existing solutions, competitors
- Search for counter-evidence (is this pain actually being solved already?)

Compose in the primary language of the target country.

### Step 3: Web Search

Execute all 8 queries using web search. Collect text and citations.

### Step 4: Extract Evidence

From all results, extract every relevant finding with:
- problem, financial_impact, evidence_type, source_url, who_suffers, evidence_quality

### Step 5: Score Validation

Evaluate across 4 dimensions (each 0-10):

1. **Pain Evidence** (0-10): How much documented financial loss exists?
2. **Market Size** (0-10): How widespread is this pain?
3. **Solution Gap** (0-10): Are existing solutions adequate?
4. **Timing** (0-10): Is this getting worse? Recent regulatory changes?

**Final Verdict**:
- **VALIDATED** (avg >= 7): Strong evidence of real, underserved pain
- **PROMISING** (avg 5-7): Evidence exists but gaps in data
- **WEAK** (avg 3-5): Limited evidence, high risk
- **NO_EVIDENCE** (avg < 3): Could not find supporting data
- **SATURATED** (Solution Gap < 3): Pain is real but well-served

### Step 6: Format Report

Report includes:
- Verdict (prominent, top of report)
- Score breakdown with reasoning
- Supporting evidence (with $ amounts and source URLs)
- Challenging evidence (competitors, counter-arguments)
- Risk factors
- Recommended next steps based on verdict

## Output

Save as `validation-{date}.md` and display to the user.

## Example

User: "Validate SaaS for restaurant health code compliance in US"

Output: VALIDATED (7.5/10) - 4,000+ FDA violations/year averaging $15K per fine, existing solutions are manual checklists, post-COVID regulatory enforcement up 30%.

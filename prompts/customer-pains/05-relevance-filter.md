# Step 5: Relevance Filter

Pipeline: Customer Pains
Input: All findings + user profile (what_you_sell)

## System Prompt

```
You evaluate whether a product/service can help solve specific customer problems. Return only valid JSON.
```

## User Prompt

```
PRODUCT: {what_you_sell}
PROBLEM WE SOLVE: {problem_you_solve}

FINDINGS:
{findings_list}

Score each finding 0.0-1.0 for relevance to this product:
- 0.8+ = product directly addresses this problem
- 0.5-0.7 = tangentially related, worth knowing
- Below 0.5 = not relevant, exclude

Return JSON array: [{"index": 0, "score": 0.85, "reason": "one sentence"}]
Only include findings with score >= 0.4.
```

Format for findings_list:
```
[0] [{segment}] {problem} ({financial_impact})
[1] [{segment}] {problem} ({financial_impact})
```

## Parameters
- Model: Claude (via Perplexity Agent API)
- Max tokens: 2000
- Temperature: 0.2

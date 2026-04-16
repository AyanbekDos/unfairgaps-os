# Topic Clusterer

Used in: Pipeline 1 (Industry Scan), Pipeline 4 (Customer Pains)

## System Prompt

```
You group business problem findings into semantic clusters (Pain Topics).

Rules:
- Findings about the SAME underlying problem go into the SAME cluster
- Each cluster gets a short, clear topic name (5-10 words)
- A finding can only belong to ONE cluster
- Don't over-cluster: if two findings are only loosely related, keep them separate
- Don't under-cluster: if 3 findings are clearly about "workforce shortage", group them
- Write topic names in the same language as the findings

Return ONLY valid JSON:
[{"topic": "Short topic name", "finding_indices": [0, 3, 7]}]
```

## User Prompt

```
Group these findings into Pain Topics:

{FINDINGS_LIST}
```

Format for FINDINGS_LIST:
```
[0] {problem} | {financial_impact} | {segment}
[1] {problem} | {financial_impact} | {segment}
...
```

## Parameters
- Model: Claude (via Perplexity Agent API)
- Max tokens: 1000
- Temperature: 0.3

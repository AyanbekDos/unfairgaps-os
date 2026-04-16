# Country Context Block

Inserted into every prompt that needs country-awareness.

```
## COUNTRY CONTEXT
The user is researching the {COUNTRY_CODE} ({COUNTRY_NAME}) market.

Before proceeding, determine:
1. What is the PRIMARY LANGUAGE of internet content in {COUNTRY_NAME}?
2. What REGULATORY AGENCIES oversee this industry in {COUNTRY_NAME}? (List top 3-5 with full names)
3. What COURT/LEGAL databases are publicly accessible in {COUNTRY_NAME}?
4. What INDUSTRY PUBLICATIONS cover this sector in {COUNTRY_NAME}?
5. What CURRENCY is used? What format for large amounts?

Apply this context to all search queries, analysis, and output:
- Compose search queries in the appropriate language
- Reference country-specific regulatory bodies (NOT US agencies unless country=US)
- Use local currency for financial figures
- Cite country-specific legal databases and court systems
- Write final output in the primary language of {COUNTRY_NAME}
```

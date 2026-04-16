# UnfairGaps

> Find real business pain points from public enforcement data. Court filings, regulatory fines, documented financial losses - not AI guesswork.

<!-- TODO: GIF demo here -->

**Already validated by real people:**
- [659 upvotes on r/Entrepreneur](https://www.reddit.com/r/Entrepreneur/comments/1qc0cwd/) - "I scraped 48,000 court filings to stop guessing business ideas"
- [237 comments on r/SideProject](https://www.reddit.com/r/SideProject/comments/1qurbh2/) - people requested pain reports for their industries in the comments
- [102 upvotes on r/Logistics](https://www.reddit.com/r/logistics/) - trucking industry pain analysis

The methodology works. Now it's open source.

## What is this?

Every SEC fine, EPA violation, OSHA citation, and court filing is a business screaming **"I NEED A SOLUTION."** UnfairGaps finds these screams automatically.

4 pipelines. Works in any country. One API key. 5 minutes to first result.

## The 4 Pipelines

| Pipeline | Input | Output | Use case |
|----------|-------|--------|----------|
| **Industry Scan** | Industry + Country | Pain points + business opportunities | "What problems exist in construction in Germany?" |
| **Idea Validator** | Business idea + Country | Verdict: VALIDATED / WEAK / NO_EVIDENCE / SATURATED | "Does my SaaS idea have real pain behind it?" |
| **Site Pain Audit** | URL | Claims vs reality report | "Is this competitor solving real problems or selling vitamins?" |
| **Customer Pain Finder** | URL | Your customers' documented pain points | "What are my customers actually losing money on?" |

## How it works

Each pipeline is a chain of AI prompts that:

1. **Compose targeted search queries** - Claude determines the right regulatory agencies, court systems, and search language for your country
2. **Search the web** - Sonar finds lawsuits, fines, enforcement actions, industry reports
3. **Extract evidence** - Claude pulls structured findings: who, what, how much, source URL
4. **Analyze & report** - Clustering, deduplication, scoring, opportunity generation

All prompts are in `prompts/` - fully transparent, fully customizable.

## Quick Start

### Requirements

- Python 3.10+ (for scrapling)
- A Perplexity API key

### Get your free API key

Perplexity gives **$5/month free API credits** to every account. That's enough for ~20-30 full pipeline runs.

1. Go to [perplexity.ai/settings/api](https://perplexity.ai/settings/api)
2. Create an API key
3. You're done. No credit card needed.

### Install

```bash
git clone https://github.com/AyanbekDos/unfairgaps-os.git
cd unfairgaps-os
pip install scrapling
cp .env.example .env
# Edit .env and paste your PERPLEXITY_API_KEY
```

### Run

```bash
# Find pain points in an industry
python run.py industry-scan --industry "construction" --country US

# Validate a business idea
python run.py validate-idea --idea "SaaS for restaurant health code compliance" --country US

# Audit a website's pain claims
python run.py site-audit --url "https://example.com"

# Find your customers' pain points
python run.py customer-pains --url "https://your-site.com"
```

### Use as AI Agent Skill

Works with Claude Code, Cursor, Windsurf, Cline, or any AI coding assistant:

```bash
# Copy skill files to your AI agent's skills directory
cp skills/*.md ~/.claude/skills/  # for Claude Code
```

Then just ask your AI assistant:
```
/unfairgaps-industry-scan construction in Kazakhstan
/unfairgaps-validate-idea "SaaS for restaurant compliance" in Germany
/unfairgaps-site-audit https://competitor.com
/unfairgaps-customer-pains https://my-site.com
```

### Use prompts manually

Every prompt is in `prompts/` as plain markdown. Copy-paste into ChatGPT, Claude, or any LLM:

1. Open the pipeline folder (e.g., `prompts/industry-scan/`)
2. Follow steps 01, 02, 03... in order
3. Feed output of each step as input to the next

No code required. Works with any LLM that can search the web.

## Country Support

UnfairGaps works worldwide. When you specify a country, Claude automatically determines:

- Regulatory agencies (OSHA in US, Роструд in Russia, BG BAU in Germany...)
- Court systems and legal databases
- Search language
- Local currency
- Industry-specific regulations

Tested with: US, DE, KZ, RU, UK, BR, IN, AU, and more.

## Project Structure

```
unfairgaps/
  README.md
  .env.example          # Just one key: PERPLEXITY_API_KEY
  run.py                # CLI entry point
  prompts/
    shared/             # Reusable across all pipelines
      country-context.md
      site-analyzer.md
      sonar-search.md
      evidence-extractor.md
      topic-clusterer.md
      report-formatter.md
    industry-scan/      # Pipeline 1
      01-query-architect.md
      05-opportunity-writer.md
    idea-validator/     # Pipeline 2
      01-idea-parser.md
      02-validation-query-architect.md
      05-validation-scorer.md
    site-audit/         # Pipeline 3
      02-claimed-pain-extractor.md
      03-reality-check-query-architect.md
      06-pain-solution-matcher.md
    customer-pains/     # Pipeline 4
      02-query-architect.md
      05-relevance-filter.md
      07-opportunity-generator.md
  skills/               # AI agent skill files
    unfairgaps-industry-scan.md
    unfairgaps-validate-idea.md
    unfairgaps-site-audit.md
    unfairgaps-customer-pains.md
```

## How is this different from ChatGPT?

| | ChatGPT / Claude | UnfairGaps |
|---|---|---|
| Source | "I think there might be problems..." | SEC filing #2024-03847, $2.3M fine |
| Evidence | Opinions and general knowledge | Court records, regulatory actions, documented losses |
| Structure | Free-form chat | 4 specialized pipelines with defined outputs |
| Verification | Trust the AI | Every finding has a source URL |
| Country-aware | Sometimes | Always - regulatory agencies, language, courts |

## The Philosophy

**Annoyances vs Liabilities.**

Most "market research" finds annoyances. UnfairGaps finds liabilities - places where businesses are **legally required** to lose money. If a company is paying a fine or settling a lawsuit, they aren't looking for a nice-to-have tool. They're looking for a tourniquet.

## Data Sources

UnfairGaps searches across:
- **Court records** - lawsuits, settlements, class actions
- **SEC EDGAR** - securities enforcement actions
- **EPA ECHO** - environmental violations and fines
- **OSHA** - workplace safety citations
- **CFPB** - consumer complaints (14M+ records)
- **openFDA** - product recalls and enforcement
- **Country-specific** - local regulatory databases based on your market

All public data. No scraping private databases. No paywalls.

## Cost

With Perplexity's free $5/month:
- ~4-5 full Industry Scans
- ~5-6 Idea Validations
- ~3-4 Site Audits
- ~2-3 Customer Pain Finder runs

One pipeline run costs roughly $0.50-1.50 depending on complexity.

## Contributing

PRs welcome. Especially:
- New country-specific regulatory source adapters
- Pipeline improvements and prompt refinements
- Translations of documentation
- Bug reports and test results

## License

MIT

## Star History

<!-- TODO: Add star history badge -->

---

Built by [@AyanbekDos](https://github.com/AyanbekDos). If this helped you find a real business opportunity, I'd love to hear about it.

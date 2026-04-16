# UnfairGaps

> AI is replacing engineers. The safest career move? Find a boring niche that Big Tech will never touch. This tool finds those niches.

<!-- TODO: GIF demo here -->

## The Story

I spent 2 years building tools nobody wanted. Every time it was the same: I'd get excited about a "clever" idea, spend months building it, and discover that nobody cared enough to pay. I was solving annoyances, not real problems.

Then I had a realization: **stop brainstorming ideas. Start reading court filings.** If a company is paying a fine or settling a lawsuit, they aren't looking for a "nice-to-have" tool. They're looking for a tourniquet.

So I burned $5K in API credits and built AI pipelines that scan enforcement data automatically. I found things like:
- Solar installers losing **$12K per rejected warranty claim** because field techs forget to geotag photos
- E-commerce stores settling **4,000+ ADA lawsuits/year** at $20-50K each
- Apparel brands writing off **$1-3M/year** on returns from assembly defects

I posted the results on Reddit:
- [659 upvotes on r/Entrepreneur](https://www.reddit.com/r/Entrepreneur/comments/1qc0cwd/) - "I scraped 48,000 court filings to stop guessing business ideas"
- [237 comments on r/SideProject](https://www.reddit.com/r/SideProject/comments/1qurbh2/) - people begged me to scan their industries
- [102 upvotes on r/Logistics](https://www.reddit.com/r/logistics/) - trucking pain analysis

One user took my research and is now building a company around a gap I found.

I tried to turn this into a SaaS. 200 visitors, 19 signups, 0 purchases. The methodology is valuable but one-time - once you have the report, you don't come back. My target audience is developers, and developers will always just build it themselves if you show them the approach.

**So I'm done chasing Product-Market Fit. Here's everything I built.** 4 pipelines, 17 prompts, a Python CLI, and AI agent skills. Free. MIT license. Take it, improve it, build a boring profitable business with it.

## Why This Matters Right Now

Every week another headline: "Google cuts 12K engineers." "Meta lays off entire ML team." "Startup replaces 60% of engineering with AI."

The standard advice is "build a side project." But build what?

The most profitable software businesses solve painfully boring problems for industries that never make TechCrunch:
- Plumbing contractors paying **$50K/year in OSHA fines**
- Solar installers losing **$12K per rejected warranty claim** because a field tech forgot to geotag a photo
- Restaurant owners settling **ADA lawsuits for $20-50K** each

AI can't replace you if your customers are plumbing contractors who barely use email. **The boring niches are where the money is.** This tool finds them.

## The 4 Pipelines

| Pipeline | Input | Output | Use case |
|----------|-------|--------|----------|
| **Industry Scan** | Industry + Country | Pain points + business opportunities | "What problems exist in construction in Germany?" |
| **Idea Validator** | Business idea + Country | Verdict: VALIDATED / WEAK / NO_EVIDENCE / SATURATED | "Does my SaaS idea have real pain behind it?" |
| **Site Pain Audit** | URL | Claims vs reality report | "Is this competitor solving real problems or selling vitamins?" |
| **Customer Pain Finder** | URL | Your customers' documented pain points | "What are my customers actually losing money on?" |

## The Philosophy

**Annoyances vs Liabilities.**

Most "market research" finds annoyances. UnfairGaps finds liabilities - places where businesses are **legally required** to lose money. If a company is paying a fine or settling a lawsuit, they aren't looking for a nice-to-have tool. They're looking for a tourniquet.

## How It Works

Each pipeline is a chain of AI prompts that:

1. **Compose targeted search queries** - Claude determines the right regulatory agencies, court systems, and search language for your country
2. **Search the web** - Sonar finds lawsuits, fines, enforcement actions, industry reports
3. **Extract evidence** - Claude pulls structured findings: who, what, how much, source URL
4. **Analyze & report** - Clustering, deduplication, scoring, opportunity generation

All prompts are in `prompts/` - fully transparent, fully customizable.

## Quick Start

### Requirements

- Python 3.10+
- A Perplexity API key

### Get your free API key

Perplexity gives **$5/month free API credits** to every account. That's enough for ~20 full pipeline runs. No credit card needed.

1. Go to [perplexity.ai/settings/api](https://perplexity.ai/settings/api)
2. Create an API key
3. Done.

### Install

```bash
git clone https://github.com/AyanbekDos/unfairgaps-os.git
cd unfairgaps-os
pip install scrapling httpx
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

Works worldwide. When you specify a country, Claude automatically determines:

- Regulatory agencies (OSHA in US, BG BAU in Germany, GASK in Kazakhstan...)
- Court systems and legal databases
- Search language
- Local currency
- Industry-specific regulations

Tested with: US, DE, KZ, RU, UK, BR, IN, AU, and more.

## How is this different from ChatGPT?

| | ChatGPT / Claude | UnfairGaps |
|---|---|---|
| Source | "I think there might be problems..." | SEC filing #2024-03847, $2.3M fine |
| Evidence | Opinions and general knowledge | Court records, regulatory actions, documented losses |
| Structure | Free-form chat | 4 specialized pipelines with defined outputs |
| Verification | Trust the AI | Every finding has a source URL |
| Country-aware | Sometimes | Always - regulatory agencies, language, courts |

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

## Project Structure

```
unfairgaps-os/
  README.md
  .env.example          # Just one key: PERPLEXITY_API_KEY
  run.py                # CLI entry point
  prompts/
    shared/             # Reusable across all pipelines
    industry-scan/      # Pipeline 1: Find industry pain points
    idea-validator/     # Pipeline 2: Validate business ideas
    site-audit/         # Pipeline 3: Claims vs reality
    customer-pains/     # Pipeline 4: Your customers' pain points
  skills/               # AI agent skill files (Claude Code, Cursor, etc.)
```

## Help Wanted

I'm not a professional programmer. I built this because I needed it. Here's where I need help:

- **Direct database connectors** - Right now we search through Perplexity. Building direct connectors to PACER, SEC EDGAR, EPA ECHO, and OSHA databases would make results 10x more reliable and faster.
- **Prompt engineering** - The 17 prompts work, but they're not perfect. I'd love prompt engineers to tear them apart.
- **Python improvements** - The CLI runs but it's not elegant. Any Pythonista who wants to refactor - please do.
- **Country adapters** - Every country has its own regulatory databases. I know US and Kazakhstan well. Help me add yours.
- **Bug reports** - Run it on your industry and tell me what breaks.

## License

MIT

---

Built by [@AyanbekDos](https://github.com/AyanbekDos) from Kazakhstan. 4 months of work, open-sourced because the world needs more people building boring, profitable businesses instead of chasing the next AI wrapper.

If this helped you find a real business opportunity, I'd love to hear about it.

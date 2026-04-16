# Site Analyzer

Used in: Pipeline 3 (Site Audit), Pipeline 4 (Customer Pains)

## Method

3-step cascade to get site content:
1. **Scrapling** (best quality) - `pip install scrapling` - adaptive parsing, anti-bot bypass, handles Cloudflare/JS-rendered sites. Uses `Fetcher` for static sites, `StealthFetcher` if blocked.
2. **Direct fetch** + HTML strip (fallback) - no dependency needed, plain HTTP
3. **Sonar search** (last resort) - "analyze this website: {url}"

Then Claude analyzes the content.

## Scraping Code (Python)

```python
from scrapling import Fetcher, StealthFetcher

def scrape_site(url: str) -> str:
    """Get clean text content from URL. Cascade: Scrapling -> fetch -> Sonar."""
    try:
        # Try fast fetcher first
        page = Fetcher().get(url, timeout=10)
        text = page.get_all_text(ignore_tags=('script', 'style', 'nav', 'footer'))
        if len(text) > 200:
            return text[:5000]
    except Exception:
        pass

    try:
        # Try stealth fetcher (handles Cloudflare, JS rendering)
        page = StealthFetcher().fetch(url, timeout=15)
        text = page.get_all_text(ignore_tags=('script', 'style', 'nav', 'footer'))
        if len(text) > 200:
            return text[:5000]
    except Exception:
        pass

    # Fallback to Sonar search (see sonar-search.md)
    return None  # caller should use Sonar fallback
```

## System Prompt (Claude analysis step)

```
You are a business analyst. Given the text content of a company's website, figure out what they SELL and WHO PAYS for it.

## MARKET DETECTION
Analyze the website content and determine which COUNTRY/MARKET the business primarily operates in.
Look for clues: domain TLD (.ru, .kz, .de), language of content, currency symbols, phone numbers, addresses, regulatory mentions.
If unclear, default to "us".

## CRITICAL: HOW TO IDENTIFY SEGMENTS
Segments = the people or businesses who PAY MONEY for this product. NOT:
- Industries or topics the website displays data ABOUT
- Categories of content shown on the website
- End users of the customers

EXAMPLE - CORRECT:
Website mentions "4400 problems across construction, logistics, healthcare"
- what_you_sell: "Weekly pain intelligence reports"
- segments: ["Startup founders", "B2B sales teams"] - who PAYS
- NOT: ["Contractors", "Logistics operators"] - what DATA is about

## OUTPUT LANGUAGE
Write ALL text fields in the PRIMARY LANGUAGE of the detected market.

## RULES
- 2-5 segments, ordered by who is MOST LIKELY to pay
- Be specific: "Early-stage SaaS founders" not just "Founders"
- Look at pricing page, CTAs, and marketing copy to determine who the buyer is

Return ONLY valid JSON:
{
  "what_you_sell": "One sentence",
  "problem_you_solve": "One sentence",
  "market": "ISO 2-letter country code",
  "segments": [
    {"name": "Short segment name", "description": "One sentence"}
  ]
}
```

## User Prompt

```
WEBSITE URL: {url}

WEBSITE CONTENT:
{scraped_content (max 4000 chars)}
```

## Parameters
- Model: Claude (via Perplexity Agent API)
- Max tokens: 1000
- Temperature: 0.3

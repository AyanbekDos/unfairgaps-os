#!/usr/bin/env python3
"""UnfairGaps CLI - Find real business pain points from public enforcement data."""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from datetime import date

import httpx

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY") or ""
AGENT_URL = "https://api.perplexity.ai/v1/agent"
SONAR_URL = "https://api.perplexity.ai/chat/completions"
PROMPTS_DIR = Path(__file__).parent / "prompts"

CLAUDE_MODEL = "anthropic/claude-sonnet-4-6"
SONAR_MODEL = "sonar-reasoning-pro"

COUNTRY_NAMES = {
    "US": "United States", "DE": "Germany", "KZ": "Kazakhstan", "RU": "Russia",
    "UK": "United Kingdom", "BR": "Brazil", "IN": "India", "AU": "Australia",
    "CA": "Canada", "FR": "France", "JP": "Japan", "CN": "China",
    "KR": "South Korea", "MX": "Mexico", "TR": "Turkey", "SA": "Saudi Arabia",
    "AE": "UAE", "NG": "Nigeria", "ZA": "South Africa", "ID": "Indonesia",
    "PH": "Philippines", "VN": "Vietnam", "TH": "Thailand", "PL": "Poland",
    "IT": "Italy", "ES": "Spain", "NL": "Netherlands", "SE": "Sweden",
    "NO": "Norway", "FI": "Finland", "DK": "Denmark", "IL": "Israel",
    "SG": "Singapore", "MY": "Malaysia", "AR": "Argentina", "CL": "Chile",
    "CO": "Colombia", "PE": "Peru", "EG": "Egypt", "PK": "Pakistan",
    "BD": "Bangladesh", "UA": "Ukraine", "CZ": "Czech Republic", "AT": "Austria",
    "CH": "Switzerland", "BE": "Belgium", "PT": "Portugal", "GR": "Greece",
    "RO": "Romania", "HU": "Hungary", "IE": "Ireland", "NZ": "New Zealand",
    "UZ": "Uzbekistan", "GE": "Georgia", "AM": "Armenia", "AZ": "Azerbaijan",
    "BY": "Belarus", "KG": "Kyrgyzstan", "TJ": "Tajikistan", "TM": "Turkmenistan",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_prompt(path: str, block_index: int = 0) -> str:
    """Load a prompt markdown file and extract the system prompt code block.

    Finds the code block after '## System Prompt' header, or falls back to
    the block_index-th code block.
    """
    full = (PROMPTS_DIR / path).read_text()

    # Try to find the block right after "## System Prompt"
    marker = "## System Prompt"
    pos = full.find(marker)
    if pos != -1:
        after = full[pos:]
        blocks = after.split("```")
        if len(blocks) >= 3:
            block = blocks[1].strip()
            # Strip language identifier (e.g., "python", "json")
            if block.split("\n")[0].strip().isalpha():
                block = block[block.index("\n") + 1:]
            return block.strip()

    # Fallback: take nth code block
    blocks = full.split("```")
    idx = block_index * 2 + 1  # code blocks are at odd indices
    if idx < len(blocks):
        block = blocks[idx].strip()
        if block.split("\n")[0].strip().isalpha():
            block = block[block.index("\n") + 1:]
        return block.strip()
    return full


def country_context(code: str) -> str:
    """Build country context block."""
    name = COUNTRY_NAMES.get(code.upper(), code)
    tpl = (PROMPTS_DIR / "shared/country-context.md").read_text()
    # Extract template between ``` markers
    blocks = tpl.split("```")
    ctx = blocks[1] if len(blocks) >= 3 else tpl
    return ctx.replace("{COUNTRY_CODE}", code.upper()).replace("{COUNTRY_NAME}", name)


def call_claude(system: str, user: str, max_tokens: int = 2000, temp: float = 0.3) -> str:
    """Call Claude via Perplexity Agent API."""
    r = httpx.post(
        AGENT_URL,
        headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"},
        json={"model": CLAUDE_MODEL, "instructions": system, "input": user,
              "max_output_tokens": max_tokens, "temperature": temp},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()

    def extract_text(obj):
        """Recursively extract text from Agent API response."""
        if isinstance(obj, str):
            return obj
        if isinstance(obj, list):
            return "\n".join(extract_text(item) for item in obj)
        if isinstance(obj, dict):
            # {text: "...", type: "output_text"}
            if "text" in obj and obj.get("type") == "output_text":
                return obj["text"]
            # {content: [...]}
            if "content" in obj:
                return extract_text(obj["content"])
            # {output: ...}
            if "output" in obj:
                return extract_text(obj["output"])
            # {choices: [{message: {content: "..."}}]}
            if "choices" in obj:
                return obj["choices"][0]["message"]["content"]
        return str(obj)

    return extract_text(data)


def call_sonar(system: str, user: str, max_tokens: int = 3000) -> dict:
    """Call Sonar via Perplexity Chat Completions. Returns {text, citations}."""
    r = httpx.post(
        SONAR_URL,
        headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"},
        json={"model": SONAR_MODEL, "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ], "max_tokens": max_tokens, "return_citations": True},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    text = data["choices"][0]["message"]["content"]
    citations = data.get("citations", [])
    return {"text": text, "citations": citations}


def scrape_site(url: str) -> str | None:
    """Get clean text from URL. Cascade: Scrapling -> raw fetch -> None."""
    try:
        from scrapling import Fetcher, StealthFetcher
        try:
            page = Fetcher().get(url, timeout=10)
            text = page.get_all_text(ignore_tags=("script", "style", "nav", "footer"))
            if len(text) > 200:
                return text[:5000]
        except Exception:
            pass
        try:
            page = StealthFetcher().fetch(url, timeout=15)
            text = page.get_all_text(ignore_tags=("script", "style", "nav", "footer"))
            if len(text) > 200:
                return text[:5000]
        except Exception:
            pass
    except ImportError:
        pass

    # Fallback: raw HTTP
    try:
        import re
        r = httpx.get(url, timeout=10, follow_redirects=True)
        html = r.text
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
        html = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", html).strip()
        if len(text) > 200:
            return text[:5000]
    except Exception:
        pass

    return None


def parse_json(text):
    """Try to extract JSON from LLM response."""
    if isinstance(text, (list, dict)):
        return text
    text = text.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        # Try to find JSON array or object in text
        for start_char, end_char in [("[", "]"), ("{", "}")]:
            s = text.find(start_char)
            e = text.rfind(end_char)
            if s != -1 and e != -1:
                try:
                    return json.loads(text[s:e + 1])
                except json.JSONDecodeError:
                    continue
        # Try to fix truncated JSON array by closing it
        s = text.find("[")
        if s != -1:
            truncated = text[s:]
            # Find last complete object
            last_brace = truncated.rfind("}")
            if last_brace != -1:
                try:
                    return json.loads(truncated[:last_brace + 1] + "]")
                except json.JSONDecodeError:
                    pass
        return None


def step(name: str, detail: str = ""):
    """Print a step indicator."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    if detail:
        print(f"  {detail}")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Pipeline 1: Industry Scan
# ---------------------------------------------------------------------------

def pipeline_industry_scan(industry: str, country: str):
    country = country.upper()
    country_name = COUNTRY_NAMES.get(country, country)
    ctx = country_context(country)

    # Step 1: Query Architect
    step("Step 1/5: Composing search queries", f"{industry} in {country_name}")
    sys_prompt = load_prompt("industry-scan/01-query-architect.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{COUNTRY_NAME}", country_name)
    user_prompt = f"INDUSTRY: {industry}\nCOUNTRY: {country} ({country_name})\nDATE: {date.today()}\n\nBefore writing queries, reason through:\n1. Which government agencies regulate \"{industry}\" in {country_name}?\n2. What are the 3 most expensive problems in \"{industry}\" in {country_name}?\n3. What specific incidents generate court records or enforcement actions?\n4. What would a journalist or lawyer search to find these cases?"
    queries_raw = call_claude(sys_prompt, user_prompt, max_tokens=800, temp=0.4)
    queries = parse_json(queries_raw)
    if not queries:
        print("ERROR: Failed to parse queries. Raw output:")
        print(queries_raw)
        return
    print(f"  Generated {len(queries)} search queries")
    for i, q in enumerate(queries):
        print(f"  [{i+1}] {q}")

    # Step 2: Sonar search (parallel batches of 3)
    step("Step 2/5: Searching the web", f"{len(queries)} queries via Sonar")
    sys_prompt = load_prompt("shared/sonar-search.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{COUNTRY_NAME}", country_name)
    all_text = []
    all_citations = []
    for i in range(0, len(queries), 3):
        batch = queries[i:i+3]
        for q in batch:
            print(f"  Searching: {q[:60]}...")
            result = call_sonar(sys_prompt, q)
            all_text.append(result["text"])
            all_citations.extend(result["citations"])
        if i + 3 < len(queries):
            time.sleep(1)  # Rate limiting between batches

    combined_text = "\n\n---\n\n".join(all_text)
    citations_str = "\n".join(f"[{i}] {c}" for i, c in enumerate(all_citations))
    print(f"  Found {len(all_citations)} citations")

    # Step 3: Evidence Extractor
    step("Step 3/5: Extracting evidence")
    sys_prompt = load_prompt("shared/evidence-extractor.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{CITATIONS}", citations_str)
    findings_raw = call_claude(sys_prompt, f"RESEARCH TEXT TO ANALYZE:\n\n{combined_text}", max_tokens=4000, temp=0.2)
    findings = parse_json(findings_raw)
    if not findings:
        print("ERROR: Failed to parse findings. Raw output:")
        print(findings_raw[:500])
        return
    print(f"  Extracted {len(findings)} findings")

    # Step 4: Topic Clusterer
    step("Step 4/5: Clustering findings")
    sys_prompt = load_prompt("shared/topic-clusterer.md")
    findings_list = "\n".join(f"[{i}] {f.get('problem', '')} | {f.get('financial_impact', 'N/A')} | {f.get('who_suffers', 'N/A')}" for i, f in enumerate(findings))
    clusters_raw = call_claude(sys_prompt, f"Group these findings into Pain Topics:\n\n{findings_list}", max_tokens=1000, temp=0.3)
    clusters = parse_json(clusters_raw)
    if not clusters:
        print("WARNING: Clustering failed, using flat list")
        clusters = [{"topic": industry, "finding_indices": list(range(len(findings)))}]
    print(f"  Found {len(clusters)} pain topics")
    for c in clusters:
        print(f"  - {c['topic']} ({len(c.get('finding_indices', []))} findings)")

    # Step 5: Opportunity Writer + Report
    step("Step 5/5: Generating opportunities and report")
    sys_prompt_opp = load_prompt("industry-scan/05-opportunity-writer.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{COUNTRY_NAME}", country_name)
    # Build clustered data for opportunity writer
    topics_data = []
    for c in clusters:
        topic_findings = [findings[i] for i in c.get("finding_indices", []) if i < len(findings)]
        topics_data.append({"topic": c["topic"], "findings": topic_findings})

    opportunities_raw = call_claude(sys_prompt_opp, f"PAIN TOPICS AND FINDINGS:\n{json.dumps(topics_data, ensure_ascii=False, indent=2)}", max_tokens=2000, temp=0.4)

    # Final report
    sys_prompt_report = load_prompt("shared/report-formatter.md")
    report_input = f"INDUSTRY: {industry}\nCOUNTRY: {country_name}\n\nFINDINGS:\n{json.dumps(findings, ensure_ascii=False, indent=2)}\n\nCLUSTERS:\n{json.dumps(clusters, ensure_ascii=False, indent=2)}\n\nOPPORTUNITIES:\n{opportunities_raw}"
    report = call_claude(sys_prompt_report, report_input, max_tokens=2500, temp=0.3)

    # Save
    output_file = f"report-{industry.lower().replace(' ', '-')}-{country.lower()}-{date.today()}.md"
    Path(output_file).write_text(report)
    print(f"\n  Report saved to: {output_file}")
    print(f"\n{report}")


# ---------------------------------------------------------------------------
# Pipeline 2: Idea Validator
# ---------------------------------------------------------------------------

def pipeline_validate_idea(idea: str, country: str):
    country = country.upper()
    country_name = COUNTRY_NAMES.get(country, country)
    ctx = country_context(country)

    # Step 1: Idea Parser
    step("Step 1/5: Parsing your idea")
    sys_prompt = load_prompt("idea-validator/01-idea-parser.md")
    parsed_raw = call_claude(sys_prompt, f"BUSINESS IDEA:\n{idea}\n\nCOUNTRY (if specified): {country}", max_tokens=800, temp=0.3)
    parsed = parse_json(parsed_raw)
    if not parsed:
        print("ERROR: Failed to parse idea. Raw:")
        print(parsed_raw)
        return
    print(f"  Product: {parsed.get('product', '?')}")
    print(f"  Industry: {parsed.get('industry', '?')}")
    print(f"  Target pain: {parsed.get('target_pain', '?')}")
    print(f"  Hypothesis: {parsed.get('core_hypothesis', '?')}")

    # Step 2: Validation Query Architect
    step("Step 2/5: Composing validation queries")
    sys_prompt = load_prompt("idea-validator/02-validation-query-architect.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{COUNTRY_NAME}", country_name)
    queries_raw = call_claude(sys_prompt, f"PARSED IDEA:\n{json.dumps(parsed, ensure_ascii=False, indent=2)}\nCOUNTRY: {country} ({country_name})\nDATE: {date.today()}", max_tokens=800, temp=0.4)
    queries = parse_json(queries_raw)
    if not queries:
        print("ERROR: Failed to parse queries")
        return
    # Flatten if returned as dict with supporting/challenging keys
    if isinstance(queries, dict):
        flat = []
        for v in queries.values():
            if isinstance(v, list):
                flat.extend(v)
        queries = flat
    print(f"  Generated {len(queries)} queries (supporting + challenging)")

    # Step 3: Sonar search
    step("Step 3/5: Searching for evidence")
    sys_prompt = load_prompt("shared/sonar-search.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{COUNTRY_NAME}", country_name)
    all_text = []
    all_citations = []
    for i, q in enumerate(queries):
        if not isinstance(q, str):
            continue
        print(f"  [{i+1}/{len(queries)}] {q[:60]}...")
        result = call_sonar(sys_prompt, q)
        all_text.append(result["text"])
        all_citations.extend(result["citations"])
        if (i + 1) % 3 == 0 and i + 1 < len(queries):
            time.sleep(1)

    combined_text = "\n\n---\n\n".join(all_text)
    citations_str = "\n".join(f"[{i}] {c}" for i, c in enumerate(all_citations))

    # Step 4: Evidence Extractor
    step("Step 4/5: Extracting evidence")
    sys_prompt = load_prompt("shared/evidence-extractor.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{CITATIONS}", citations_str)
    findings_raw = call_claude(sys_prompt, f"RESEARCH TEXT TO ANALYZE:\n\n{combined_text}", max_tokens=4000, temp=0.2)
    findings = parse_json(findings_raw)
    if not findings:
        findings = []
    print(f"  Extracted {len(findings)} findings")

    # Step 5: Validation Scorer
    step("Step 5/5: Scoring validation")
    sys_prompt = load_prompt("idea-validator/05-validation-scorer.md").replace("{COUNTRY_CONTEXT}", ctx)
    scorer_input = f"ORIGINAL IDEA:\n{json.dumps(parsed, ensure_ascii=False, indent=2)}\n\nEVIDENCE FOUND:\n{json.dumps(findings, ensure_ascii=False, indent=2)}"
    verdict_raw = call_claude(sys_prompt, scorer_input, max_tokens=1500, temp=0.2)

    # Report
    sys_prompt_report = load_prompt("shared/report-formatter.md")
    report_input = f"IDEA VALIDATION REPORT\n\nIDEA: {idea}\nCOUNTRY: {country_name}\n\nPARSED:\n{json.dumps(parsed, ensure_ascii=False, indent=2)}\n\nEVIDENCE:\n{json.dumps(findings, ensure_ascii=False, indent=2)}\n\nVERDICT:\n{verdict_raw}"
    report = call_claude(sys_prompt_report, report_input, max_tokens=2500, temp=0.3)

    output_file = f"validation-{date.today()}.md"
    Path(output_file).write_text(report)
    print(f"\n  Report saved to: {output_file}")
    print(f"\n{report}")


# ---------------------------------------------------------------------------
# Pipeline 3: Site Pain Audit
# ---------------------------------------------------------------------------

def pipeline_site_audit(url: str):
    # Step 1: Scrape + Analyze site
    step("Step 1/6: Scraping website", url)
    content = scrape_site(url)
    if not content:
        print("  Scrapling/fetch failed, falling back to Sonar...")
        result = call_sonar("Analyze this website and describe what they sell, who their customers are, and what problems they claim to solve.", f"Analyze: {url}")
        content = result["text"]
    print(f"  Got {len(content)} chars of content")

    # Step 2: Site Analyzer - detect market + segments
    step("Step 2/6: Analyzing business model")
    sys_prompt = load_prompt("shared/site-analyzer.md")
    site_analysis_raw = call_claude(sys_prompt, f"WEBSITE URL: {url}\n\nWEBSITE CONTENT:\n{content[:4000]}", max_tokens=1000, temp=0.3)
    site_analysis = parse_json(site_analysis_raw)
    if not site_analysis:
        print("ERROR: Failed to analyze site")
        return
    market = site_analysis.get("market", "US")
    country_name = COUNTRY_NAMES.get(market.upper(), market)
    ctx = country_context(market)
    print(f"  Product: {site_analysis.get('what_you_sell', '?')}")
    print(f"  Market: {country_name}")

    # Step 3: Claimed Pain Extractor
    step("Step 3/6: Extracting claimed pains")
    sys_prompt = load_prompt("site-audit/02-claimed-pain-extractor.md")
    claims_raw = call_claude(sys_prompt, f"WEBSITE URL: {url}\nSITE ANALYSIS: {site_analysis.get('what_you_sell', '')}, {site_analysis.get('problem_you_solve', '')}\n\nWEBSITE CONTENT:\n{content[:4000]}", max_tokens=1500, temp=0.2)
    claims = parse_json(claims_raw)
    if not claims:
        print("ERROR: Failed to extract claims")
        return
    if isinstance(claims, list):
        claimed_pains = claims
        marketing_quality = "?"
    else:
        claimed_pains = claims.get("claimed_pains", [])
        marketing_quality = claims.get("overall_marketing_quality", "?")
    print(f"  Found {len(claimed_pains)} claimed pains")
    print(f"  Marketing quality: {marketing_quality}")

    # Step 4: Reality Check Query Architect
    step("Step 4/6: Composing reality-check queries")
    sys_prompt = load_prompt("site-audit/03-reality-check-query-architect.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{COUNTRY_NAME}", country_name)
    queries_raw = call_claude(sys_prompt, f"CLAIMED PAINS:\n{json.dumps(claimed_pains, ensure_ascii=False, indent=2)}\nCOUNTRY: {market} ({country_name})\nDATE: {date.today()}", max_tokens=800, temp=0.4)
    queries = parse_json(queries_raw)
    if not queries:
        print("ERROR: Failed to generate queries")
        return
    print(f"  Generated {len(queries)} verification queries")

    # Step 5: Sonar search + Evidence extraction
    step("Step 5/6: Searching for real evidence")
    sys_prompt_sonar = load_prompt("shared/sonar-search.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{COUNTRY_NAME}", country_name)
    all_text = []
    all_citations = []
    for i, q in enumerate(queries):
        print(f"  [{i+1}/{len(queries)}] {q[:60]}...")
        result = call_sonar(sys_prompt_sonar, q)
        all_text.append(result["text"])
        all_citations.extend(result["citations"])
        if (i + 1) % 3 == 0 and i + 1 < len(queries):
            time.sleep(1)

    combined_text = "\n\n---\n\n".join(all_text)
    citations_str = "\n".join(f"[{i}] {c}" for i, c in enumerate(all_citations))

    sys_prompt_extract = load_prompt("shared/evidence-extractor.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{CITATIONS}", citations_str)
    findings_raw = call_claude(sys_prompt_extract, f"RESEARCH TEXT TO ANALYZE:\n\n{combined_text}", max_tokens=2000, temp=0.2)
    findings = parse_json(findings_raw) or []
    print(f"  Extracted {len(findings)} real-world findings")

    # Step 6: Pain-Solution Matcher
    step("Step 6/6: Matching claims vs reality")
    sys_prompt = load_prompt("site-audit/06-pain-solution-matcher.md").replace("{COUNTRY_CONTEXT}", ctx)
    matcher_input = f"SITE: {url}\nPRODUCT: {site_analysis.get('what_you_sell', '')}\n\nCLAIMED PAINS:\n{json.dumps(claimed_pains, ensure_ascii=False, indent=2)}\n\nREAL EVIDENCE:\n{json.dumps(findings, ensure_ascii=False, indent=2)}"
    verdict_raw = call_claude(sys_prompt, matcher_input, max_tokens=2000, temp=0.2)

    # Report
    sys_prompt_report = load_prompt("shared/report-formatter.md")
    report_input = f"SITE PAIN AUDIT: {url}\nCOUNTRY: {country_name}\n\nSITE ANALYSIS:\n{json.dumps(site_analysis, ensure_ascii=False, indent=2)}\n\nCLAIMS:\n{json.dumps(claims, ensure_ascii=False, indent=2)}\n\nEVIDENCE:\n{json.dumps(findings, ensure_ascii=False, indent=2)}\n\nVERDICT:\n{verdict_raw}"
    report = call_claude(sys_prompt_report, report_input, max_tokens=2500, temp=0.3)

    output_file = f"audit-{url.split('//')[1].split('/')[0].replace('.', '-')}-{date.today()}.md"
    Path(output_file).write_text(report)
    print(f"\n  Report saved to: {output_file}")
    print(f"\n{report}")


# ---------------------------------------------------------------------------
# Pipeline 4: Customer Pain Finder
# ---------------------------------------------------------------------------

def pipeline_customer_pains(url: str):
    # Step 1: Scrape + Analyze site
    step("Step 1/7: Scraping website", url)
    content = scrape_site(url)
    if not content:
        print("  Scrapling/fetch failed, falling back to Sonar...")
        result = call_sonar("Analyze this website and describe what they sell, who their customers are.", f"Analyze: {url}")
        content = result["text"]
    print(f"  Got {len(content)} chars of content")

    # Step 2: Site Analyzer
    step("Step 2/7: Analyzing business model")
    sys_prompt = load_prompt("shared/site-analyzer.md")
    site_analysis_raw = call_claude(sys_prompt, f"WEBSITE URL: {url}\n\nWEBSITE CONTENT:\n{content[:4000]}", max_tokens=1000, temp=0.3)
    site_analysis = parse_json(site_analysis_raw)
    if not site_analysis:
        print("ERROR: Failed to analyze site")
        return
    market = site_analysis.get("market", "US")
    country_name = COUNTRY_NAMES.get(market.upper(), market)
    ctx = country_context(market)
    segments = site_analysis.get("segments", [])
    print(f"  Product: {site_analysis.get('what_you_sell', '?')}")
    print(f"  Market: {country_name}")
    print(f"  Segments: {len(segments)}")
    for s in segments:
        print(f"    - {s.get('name', '?')}: {s.get('description', '')}")

    all_findings = []

    # Step 3: Query Architect + Sonar search PER SEGMENT
    for seg_idx, segment in enumerate(segments):
        step(f"Step 3/7: Scanning segment {seg_idx+1}/{len(segments)}", segment.get("name", "?"))

        sys_prompt = load_prompt("customer-pains/02-query-architect.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{COUNTRY_NAME}", country_name)
        user_prompt = f"PRODUCT: {site_analysis.get('what_you_sell', '')}\nPROBLEM IT SOLVES: {site_analysis.get('problem_you_solve', '')}\nCUSTOMER SEGMENT: {segment.get('name', '')} - {segment.get('description', '')}\nCOUNTRY: {market} ({country_name})\nDATE: {date.today()}\n\nBefore writing queries, reason through:\n1. Which government agencies regulate \"{segment.get('name', '')}\" in {country_name}?\n2. What are the 3 most expensive problems \"{segment.get('name', '')}\" faces?\n3. What specific incidents generate court records or enforcement actions?\n4. What would a journalist or lawyer search to find these cases?"
        queries_raw = call_claude(sys_prompt, user_prompt, max_tokens=800, temp=0.4)
        queries = parse_json(queries_raw) or []
        print(f"  {len(queries)} queries for {segment.get('name', '?')}")

        # Sonar search
        sys_prompt_sonar = load_prompt("shared/sonar-search.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{COUNTRY_NAME}", country_name)
        seg_text = []
        seg_citations = []
        for i, q in enumerate(queries):
            print(f"    [{i+1}/{len(queries)}] {q[:55]}...")
            result = call_sonar(sys_prompt_sonar, q)
            seg_text.append(result["text"])
            seg_citations.extend(result["citations"])
            if (i + 1) % 3 == 0 and i + 1 < len(queries):
                time.sleep(1)

        # Extract evidence
        combined = "\n\n---\n\n".join(seg_text)
        cit_str = "\n".join(f"[{i}] {c}" for i, c in enumerate(seg_citations))
        sys_prompt_extract = load_prompt("shared/evidence-extractor.md").replace("{COUNTRY_CONTEXT}", ctx).replace("{CITATIONS}", cit_str)
        findings_raw = call_claude(sys_prompt_extract, f"RESEARCH TEXT TO ANALYZE:\n\n{combined}", max_tokens=2000, temp=0.2)
        findings = parse_json(findings_raw) or []
        for f in findings:
            f["segment"] = segment.get("name", "Unknown")
        all_findings.extend(findings)
        print(f"  Extracted {len(findings)} findings for {segment.get('name', '?')}")

    print(f"\n  Total findings across all segments: {len(all_findings)}")

    # Step 4: Relevance Filter
    step("Step 5/7: Filtering by relevance")
    sys_prompt = load_prompt("customer-pains/05-relevance-filter.md")
    filter_input = f"PRODUCT: {site_analysis.get('what_you_sell', '')}\nPROBLEM YOU SOLVE: {site_analysis.get('problem_you_solve', '')}\n\nFINDINGS:\n{json.dumps(all_findings, ensure_ascii=False, indent=2)}"
    filtered_raw = call_claude(sys_prompt, filter_input, max_tokens=2000, temp=0.2)
    filtered = parse_json(filtered_raw)
    if filtered:
        # Filter to relevance >= 0.5
        if isinstance(filtered, list):
            relevant = [f for f in filtered if f.get("relevance_score", 0) >= 0.5]
        else:
            relevant = all_findings
    else:
        relevant = all_findings
    print(f"  {len(relevant)} relevant findings (score >= 0.5)")

    # Step 5: Topic Clusterer
    step("Step 6/7: Clustering findings")
    sys_prompt = load_prompt("shared/topic-clusterer.md")
    findings_list = "\n".join(f"[{i}] {f.get('problem', '')} | {f.get('financial_impact', 'N/A')} | {f.get('segment', 'N/A')}" for i, f in enumerate(relevant))
    clusters_raw = call_claude(sys_prompt, f"Group these findings into Pain Topics:\n\n{findings_list}", max_tokens=1000, temp=0.3)
    clusters = parse_json(clusters_raw) or [{"topic": "All findings", "finding_indices": list(range(len(relevant)))}]
    print(f"  Found {len(clusters)} pain topics")

    # Step 6: Opportunity Generator
    step("Step 7/7: Generating opportunities")
    sys_prompt = load_prompt("customer-pains/07-opportunity-generator.md").replace("{COUNTRY_CONTEXT}", ctx)
    topics_data = []
    for c in clusters:
        topic_findings = [relevant[i] for i in c.get("finding_indices", []) if i < len(relevant)]
        topics_data.append({"topic": c["topic"], "findings": topic_findings})

    opps_raw = call_claude(sys_prompt, f"PRODUCT: {site_analysis.get('what_you_sell', '')}\nSEGMENTS: {json.dumps(segments, ensure_ascii=False)}\n\nPAIN TOPICS:\n{json.dumps(topics_data, ensure_ascii=False, indent=2)}", max_tokens=2000, temp=0.4)

    # Report
    sys_prompt_report = load_prompt("shared/report-formatter.md")
    report_input = f"CUSTOMER PAIN REPORT FOR: {url}\nCOUNTRY: {country_name}\n\nSITE ANALYSIS:\n{json.dumps(site_analysis, ensure_ascii=False, indent=2)}\n\nFINDINGS ({len(relevant)} relevant):\n{json.dumps(relevant, ensure_ascii=False, indent=2)}\n\nCLUSTERS:\n{json.dumps(clusters, ensure_ascii=False, indent=2)}\n\nOPPORTUNITIES:\n{opps_raw}"
    report = call_claude(sys_prompt_report, report_input, max_tokens=2500, temp=0.3)

    output_file = f"pains-{url.split('//')[1].split('/')[0].replace('.', '-')}-{date.today()}.md"
    Path(output_file).write_text(report)
    print(f"\n  Report saved to: {output_file}")
    print(f"\n{report}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    # Load .env if present
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

    global PERPLEXITY_API_KEY
    PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")

    parser = argparse.ArgumentParser(
        description="UnfairGaps - Find real business pain points from public enforcement data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python run.py industry-scan --industry "construction" --country US
  python run.py validate-idea --idea "SaaS for restaurant compliance" --country DE
  python run.py site-audit --url https://example.com
  python run.py customer-pains --url https://your-site.com
""",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # industry-scan
    p1 = sub.add_parser("industry-scan", help="Find pain points in an industry")
    p1.add_argument("--industry", required=True, help="Industry to scan (e.g., 'construction')")
    p1.add_argument("--country", required=True, help="ISO 2-letter country code (e.g., US, DE, KZ)")

    # validate-idea
    p2 = sub.add_parser("validate-idea", help="Validate a business idea against real evidence")
    p2.add_argument("--idea", required=True, help="Business idea description")
    p2.add_argument("--country", required=True, help="ISO 2-letter country code")

    # site-audit
    p3 = sub.add_parser("site-audit", help="Audit a website's pain claims vs reality")
    p3.add_argument("--url", required=True, help="Website URL to audit")

    # customer-pains
    p4 = sub.add_parser("customer-pains", help="Find your customers' documented pain points")
    p4.add_argument("--url", required=True, help="Your website URL")

    args = parser.parse_args()

    if not PERPLEXITY_API_KEY:
        print("ERROR: PERPLEXITY_API_KEY not set.")
        print("Get your free key at: https://perplexity.ai/settings/api")
        print("Then: cp .env.example .env && edit .env")
        sys.exit(1)

    print(r"""
 _   _        __       _       ____
| | | |_ __  / _| __ _(_)_ __ / ___| __ _ _ __  ___
| | | | '_ \| |_ / _` | | '__| |  _ / _` | '_ \/ __|
| |_| | | | |  _| (_| | | |  | |_| | (_| | |_) \__ \
 \___/|_| |_|_|  \__,_|_|_|   \____|\__,_| .__/|___/
                                          |_|
    Find real pain. Build real solutions.
    """)

    if args.command == "industry-scan":
        pipeline_industry_scan(args.industry, args.country)
    elif args.command == "validate-idea":
        pipeline_validate_idea(args.idea, args.country)
    elif args.command == "site-audit":
        pipeline_site_audit(args.url)
    elif args.command == "customer-pains":
        pipeline_customer_pains(args.url)


if __name__ == "__main__":
    main()

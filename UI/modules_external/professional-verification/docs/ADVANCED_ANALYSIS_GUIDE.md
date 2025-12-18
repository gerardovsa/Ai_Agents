# Advanced Professional Verification Guide
**AI-Powered Deep Analysis Tools**

---

## Overview

This module now includes **49 total verification tools** across 4 categories:

1. **Professional Verification** (35 tools) - Core identity/credential checks
2. **Image Verification** (8 tools) - Reverse image search and AI face detection
3. **Web Scraping** (10 tools) - Website metadata and infrastructure analysis
4. **Advanced Analysis** (6 NEW tools) - AI content analysis, traffic, backlinks, government claims

---

## New Advanced Analysis Tools

### 1. `analyze_content_with_ai`
**AI-powered content authenticity assessment**

**What it does:**
- Analyzes website text using Claude/GPT-4
- Detects AI-generated filler vs genuine business content
- Scores content authenticity (0-100)
- Identifies buzzwords, vague claims, lack of specifics
- Assesses writing quality and technical depth

**Use when:**
- Website looks professionally designed but content seems generic
- Claims sound too good to be true
- Need to distinguish real expertise from marketing fluff

**Red flags detected:**
- ❌ Generic AI buzzwords: "leverage", "synergy", "cutting-edge", "revolutionize"
- ❌ Filler phrases: "we believe", "committed to excellence", "passionate about"
- ❌ Lack of specific dates, numbers, names, locations
- ❌ Repetitive patterns characteristic of AI writing

**Legitimacy indicators:**
- ✅ Specific claims with data points
- ✅ Technical depth and expertise demonstrated
- ✅ Realistic expectations (not overpromising)
- ✅ Named individuals, dates, project details

**Example output:**
```json
{
  "authenticity_score": 35,
  "ai_generated_probability": 78,
  "ai_buzzwords_count": 12,
  "has_specific_dates": false,
  "assessment": "AI-generated"
}
```

---

### 2. `estimate_web_traffic`
**FREE traffic and popularity estimation**

**What it does:**
- Checks Tranco Top 1M ranking (global popularity list)
- Analyzes Certificate Transparency logs (SSL activity indicator)
- Tests global DNS propagation (Google/Cloudflare/OpenDNS)
- Provides social media search URLs for manual verification
- Returns traffic tier and 0-100 score

**Data sources (all FREE):**
- **Tranco List**: If domain is in Top 1M, shows exact rank
- **Certificate Transparency**: Number of SSL certificates = activity level
- **Global DNS**: Reachability from major DNS providers
- **Social Search**: Twitter, Reddit, LinkedIn mention URLs

**Use when:**
- Suspicious of newly created domains
- Need to verify claimed popularity or reach
- Assessing if site has actual visitors vs shell site

**Traffic tiers:**
- **Very High**: Top 10K sites (rank < 10,000)
- **High**: Top 100K sites (rank < 100,000)  
- **Medium**: Top 500K sites (rank < 500,000)
- **Low-Medium**: Top 1M sites (rank < 1,000,000)
- **Low**: Outside Top 1M (likely minimal traffic)

**Example output:**
```json
{
  "estimated_traffic_tier": "Low (Outside Top 1M)",
  "traffic_score": 12.5,
  "tranco": {
    "rank": null,
    "in_top_million": false
  },
  "certificate_transparency": {
    "total_certificates": 2,
    "subdomains_detected": 1,
    "activity_indicator": "Low"
  }
}
```

**Interpretation:**
- ISB.ECO might not be in Top 1M (biodiversity nonprofits are niche)
- SCA Technology definitely won't be (too new, suspicious)
- COMPARE: Legitimate tech companies often have Top 100K ranking

---

### 3. `analyze_backlinks`
**Domain authority and citation analysis**

**What it does:**
- Searches Common Crawl (massive web index of 250B+ pages)
- Counts Internet Archive historical snapshots
- Checks Wikipedia mentions and citations
- Finds GitHub code references to domain
- Provides Google Scholar search URL
- Calculates domain authority score (0-100)

**Data sources (all FREE):**
- **Common Crawl**: Free web index, shows if domain is widely linked
- **Internet Archive**: Historical snapshots (more = longer credibility)
- **Wikipedia**: Citations in articles (VERY high authority indicator)
- **GitHub**: Code repos referencing domain (developer trust)
- **Google Scholar**: Academic citations

**Use when:**
- Verifying domain credibility and reputation
- Checking if other legitimate sites link to this domain
- Assessing long-term online presence

**Authority scoring:**
- **High (70-100)**: Common Crawl indexed + 50+ Archive snapshots + Wikipedia mentions
- **Medium (40-69)**: Some web presence, moderate archival depth
- **Low (0-39)**: Minimal external references, no authority signals

**Red flags:**
- ❌ Zero Common Crawl pages (not linked by other sites)
- ❌ No Web Archive snapshots (no historical presence)
- ❌ Zero Wikipedia mentions (no authoritative citations)
- ❌ No GitHub references (developers don't trust it)

**Example output:**
```json
{
  "domain_authority_score": 75,
  "authority_tier": "High",
  "common_crawl": {
    "pages_indexed": 127,
    "crawl_frequency": "Regular"
  },
  "web_archive": {
    "total_snapshots": 83,
    "archival_depth": "Deep"
  },
  "wikipedia": {
    "mentions": 3,
    "authority_indicator": "Medium"
  }
}
```

---

### 4. `verify_government_claims`
**Official government database verification**

**What it does:**
- Searches official government contract/funding databases
- Provides direct API search results where available
- Returns verification URLs for manual checking
- Covers USA, Australia, UK, EU, Colombia databases

**Data sources (all OFFICIAL & FREE):**

**USA:**
- **USASpending.gov API**: ALL federal spending (contracts, grants, loans)
- **SAM.gov**: System for Award Management (registered vendors)

**Australia:**
- **AusTender**: Government procurement and contracts
- **ABR**: Australian Business Register (ABN verification)

**UK:**
- **Contracts Finder**: UK government contracts database

**EU:**
- **TED**: Tenders Electronic Daily (EU public procurement)

**Colombia:**
- **RUES**: Registro Único Empresarial y Social
- **CCB**: Cámara de Comercio (NIT verification)

**Use when:**
- Company claims government funding, grants, or contracts
- Verifying partnership with government agencies
- Checking claimed government certifications

**CRITICAL INSIGHT:**
Government spending is PUBLIC RECORD. If a company claims "$2M DOD grant" but NOTHING appears in USASpending.gov = **100% FRAUD**.

**Example output:**
```json
{
  "organization": "SCA Technology",
  "claim": "AI company with government contracts",
  "verification_sources": {
    "usaspending": {
      "found": false,
      "contracts": [],
      "search_url": "https://www.usaspending.gov/search/?hash=SCA%20Technology"
    },
    "sam_gov": {
      "search_url": "https://sam.gov/search?keywords=SCA%20Technology"
    }
  }
}
```

---

### 5. `analyze_business_registries`
**Legal entity verification**

**What it does:**
- Searches global and country-specific business registries
- Verifies company legal existence and registration
- Checks registration numbers (ABN, NIT, etc.)
- Provides API endpoints where available

**Data sources:**

**Global:**
- **OpenCorporates**: 200M+ companies worldwide (500 free API calls/month)

**USA:**
- State Secretary of State databases (varies by state)

**Australia:**
- **ASIC**: Australian Securities & Investments Commission
- **ABN Lookup**: Australian Business Number verification (FREE)

**UK:**
- **Companies House**: Official UK company registry (FREE API available)

**Colombia:**
- **RUES**: National business registry
- **CCB**: Chamber of Commerce (NIT lookup)

**Use when:**
- Verifying company is legally registered
- Checking company age, directors, status
- Validating registration numbers

**CRITICAL INSIGHT:**
Every legitimate business is registered with government authorities. If a company claims to exist but ISN'T in official registries = **SHELL COMPANY or FRAUD**.

**Example output:**
```json
{
  "company_name": "Institute of Sustainable Biodiversity",
  "country": "AU",
  "registries": {
    "asic": {
      "search_url": "https://connectonline.asic.gov.au/...",
      "note": "Australian Securities & Investments Commission"
    },
    "abn_lookup": {
      "search_url": "https://abr.business.gov.au/ABN/View?abn=...",
      "note": "Australian Business Number lookup"
    },
    "opencorporates": {
      "search_url": "https://opencorporates.com/companies?q=Institute+Sustainable+Biodiversity",
      "api_url": "https://api.opencorporates.com/...",
      "note": "Free tier: 500 requests/month"
    }
  }
}
```

---

### 6. `calculate_digital_presence_score`
**Comprehensive digital footprint assessment**

**What it does:**
- Analyzes presence across 7 major categories
- Provides search URLs for 30+ platforms
- Calculates overall presence score (0-100)
- Identifies gaps in digital footprint

**Categories analyzed:**

**1. Website Quality**
- Domain age, content quality, SEO, security, speed

**2. Social Media**
- Facebook, Twitter, LinkedIn, Instagram, YouTube

**3. Professional Networks**
- GitHub, StackOverflow, Medium, Dev.to

**4. Content Marketing**
- Blog posts, news coverage, press releases

**5. Community Engagement**
- Reddit, HackerNews, ProductHunt

**6. Technical Presence**
- GitHub repos, Docker Hub, npm packages, PyPI

**7. Media Coverage**
- Wikipedia, Crunchbase, news articles

**Use when:**
- Need comprehensive legitimacy assessment
- Verifying claimed online presence
- Comparing real companies vs shell companies

**CRITICAL INSIGHT:**
Legitimate businesses have BROAD digital presence across MULTIPLE platforms. Shell/scam companies exist ONLY on their website.

**Red flags:**
- ❌ Website exists but NO social media profiles
- ❌ No LinkedIn company page (every real business has one)
- ❌ Zero GitHub presence for "tech company"
- ❌ No news coverage or press releases
- ❌ Not in Crunchbase (startups are listed there)
- ❌ No Wikipedia page for "established organization"

**Example output:**
```json
{
  "total_score": 45,
  "assessment": {
    "tier": "Fair",
    "recommendation": "Manual verification required - check all presence URLs"
  },
  "presence_components": {
    "social_media": {
      "facebook": "https://www.facebook.com/search/...",
      "linkedin": "https://www.linkedin.com/search/..."
    },
    "professional": {
      "github": "https://github.com/search?q=...",
      "stackoverflow": "https://stackoverflow.com/search?q=..."
    },
    "technical": {
      "github_repos": "https://github.com/search?q=...",
      "docker_hub": "https://hub.docker.com/search?q=..."
    }
  }
}
```

---

## Complete Workflow Example

**Scenario:** Verify Gregory Dutton @ SCA Technology requesting database access

### Step 1: Basic Infrastructure (existing tools)
```python
# Domain age check
check_domain_age('scatechnology.ai')
# Result: 168 days (5.6 months) - RED FLAG

# SSL certificate
check_ssl_certificate('scatechnology.ai')
# Result: Valid but recent (Let's Encrypt)

# Website structure
analyze_website_structure('scatechnology.ai')
# Result: No sitemap, no robots.txt - POOR SEO
```

### Step 2: Advanced Analysis (NEW tools)
```python
# 1. AI Content Analysis
content = scrape_website_content('scatechnology.ai')['content']
analyze_content_with_ai(content['full_text'], 'scatechnology.ai')
# Result: 78% AI-generated probability - RED FLAG

# 2. Web Traffic
estimate_web_traffic('scatechnology.ai')
# Result: Not in Top 1M, 2 SSL certs, Low activity - RED FLAG

# 3. Backlinks & Authority
analyze_backlinks('scatechnology.ai')
# Result: Domain authority 15/100, no Wikipedia mentions - RED FLAG

# 4. Government Claims (if they claim gov contracts)
verify_government_claims('SCA Technology', 'government contracts', 'US')
# Check: USASpending.gov search URL
# Result: No contracts found - FRAUD if claimed

# 5. Business Registry
analyze_business_registries('SCA Technology', 'US')
# Check: OpenCorporates, state registries
# Result: Not found = SHELL COMPANY

# 6. Digital Presence
calculate_digital_presence_score('scatechnology.ai', 'SCA Technology')
# Result: 25/100 - Only website exists, no social media, no GitHub
# MAJOR RED FLAG for "AI company"
```

### Step 3: Comparison with Claimed Organization (ISB)
```python
# Repeat all checks for isb.eco
# ISB Results:
# - Domain age: 809 days (2.2 years) ✅
# - AI content: 35% probability (more authentic) ✅
# - Traffic: Better metrics (though still niche) ✅
# - Backlinks: Domain authority 55/100 ✅
# - Business registry: Found in Australian registries ✅
# - Digital presence: 60/100 (legitimate footprint) ✅
```

### Step 4: Final Decision
```
ASSESSMENT:
- SCA Technology: FRAUDULENT (6/6 red flags)
- ISB: LIKELY LEGITIMATE (6/6 green flags)
- Gregory Dutton: IDENTITY CONFUSION
  - Real person at ISB being impersonated? OR
  - Same person running legitimate + fraudulent orgs? OR
  - Complete identity theft?

RECOMMENDATION:
✅ DENY: SCA Technology access (100% confidence)
⚠️  VERIFY: Gregory Dutton identity at ISB before granting access
   - Video call with government ID
   - Employment confirmation from ISB
   - LinkedIn profile reverse image search
   - Phone verification (+61 461 357 358)
```

---

## API Keys & Configuration

### Required Environment Variables

**For AI Content Analysis:**
```bash
# Anthropic Claude (preferred)
ANTHROPIC_API_KEY=sk-ant-...

# OR OpenAI GPT-4 (fallback)
OPENAI_API_KEY=sk-...
```

**For Government Verification:**
No API keys required - uses public databases and search URLs

**For Business Registries:**
```bash
# Optional - UK Companies House API
COMPANIES_HOUSE_API_KEY=...  # Free at https://developer.company-information.service.gov.uk/

# Optional - OpenCorporates API  
OPENCORPORATES_API_KEY=...  # Free tier: 500 requests/month
```

### Fallback Behavior

If AI API keys not available:
- `analyze_content_with_ai()` falls back to **rule-based analysis**
- Still detects AI buzzwords, filler phrases, lack of specifics
- Scores authenticity based on pattern matching
- Not as sophisticated but still useful

All other tools work without any API keys (100% FREE sources).

---

## Libraries Required

**Already installed:**
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `dnspython` - DNS queries
- `python-whois` - Domain registration info

**New requirements:**
```bash
# For AI content analysis (optional but recommended)
pip install anthropic  # Claude API
# OR
pip install openai     # GPT-4 API
```

---

## Best Practices

### 1. Progressive Verification
Start with fast/free checks, escalate to deeper analysis:

**Level 1 - Quick Checks (< 30 seconds):**
- Domain age
- SSL certificate
- DNS records
- Website structure

**Level 2 - Medium Analysis (1-2 minutes):**
- Web traffic estimation
- Backlink analysis
- AI content analysis

**Level 3 - Deep Verification (5-10 minutes):**
- Government claim verification (manual URL checking)
- Business registry searches
- Digital presence assessment
- Social media manual verification

### 2. AI Content Analysis Tips
- Extract at least 500-1000 chars of content for accurate analysis
- Include homepage text, about page, service descriptions
- Compare AI scores across multiple pages for consistency
- Use rule-based fallback if AI API quota exhausted

### 3. Traffic Analysis Interpretation
- **Tranco rank < 100K**: Significant traffic, likely legitimate
- **Tranco rank 100K-500K**: Moderate traffic, niche businesses
- **Tranco rank 500K-1M**: Low traffic, small businesses/blogs
- **Not in Top 1M**: Very low traffic, new sites, or shell sites
- **Certificate count > 10**: Active site with subdomains
- **Global DNS 3/3**: Well-configured infrastructure

### 4. Backlink Scoring Guide
- **Authority 70-100**: Established domain with citations
- **Authority 40-69**: Moderate presence, some backlinks
- **Authority 0-39**: Minimal presence, likely new or suspicious
- **Wikipedia mentions**: VERY strong legitimacy indicator
- **GitHub references**: Shows developer trust (for tech companies)

### 5. Government Claims - VERIFY EVERYTHING
- **NEVER take claims at face value**
- Always check official databases (USASpending, AusTender, etc.)
- Look for press releases on official .gov sites
- Google News search for coverage of funding/contracts
- If claimed but not found = FRAUD (government spending is public)

### 6. Business Registry Checks
- OpenCorporates search FIRST (fastest global search)
- Then country-specific registries for details
- Registration number = instant verification (ABN, NIT, etc.)
- Check company status (Active vs Dissolved)
- Verify directors/officers match claimed individuals

### 7. Digital Presence Red Flags
For "tech companies":
- ❌ No GitHub organization
- ❌ No LinkedIn company page
- ❌ No employee LinkedIn profiles
- ❌ No npm/PyPI packages
- ❌ No StackOverflow mentions

For "established organizations":
- ❌ No Wikipedia page
- ❌ No Crunchbase listing
- ❌ No news coverage
- ❌ No social media presence
- ❌ Website is ONLY online presence

---

## Testing

Run comprehensive test suite:
```bash
cd UI/modules_external/professional-verification/TESTS
python test_advanced_analysis.py
```

Tests include:
1. AI content analysis (ISB vs SCA Technology)
2. Web traffic estimation
3. Backlink and authority analysis
4. Government claim verification
5. Business registry searches
6. Digital presence scoring

Expected output shows side-by-side comparison of legitimate vs suspicious domains.

---

## Summary: Why These Tools Matter

**Previous verification (35 tools):**
- ✅ Domain age, SSL, DNS, email validation
- ✅ Profile image reverse search
- ✅ Website metadata extraction
- ❌ **Could not assess CONTENT quality**
- ❌ **Could not verify TRAFFIC/popularity**
- ❌ **Could not check BACKLINKS/authority**
- ❌ **Could not verify GOVERNMENT claims**
- ❌ **Could not check BUSINESS registration**
- ❌ **Could not assess DIGITAL footprint**

**Now (49 tools total):**
- ✅ Everything above PLUS:
- ✅ **AI analysis of content authenticity**
- ✅ **Traffic and popularity metrics**
- ✅ **Backlink and domain authority**
- ✅ **Government database verification**
- ✅ **Business registry confirmation**
- ✅ **Comprehensive digital presence**

**Result:** Near-complete verification capability rivaling commercial solutions, **100% using FREE tools and APIs**.

---

## Cost Comparison

**Commercial Solutions:**
- Recorded Future: $50K-$100K/year
- LexisNexis: $25K-$75K/year
- Thomson Reuters Clear: $15K-$40K/year
- ZoomInfo: $15K-$30K/year

**This Module:**
- **Core tools**: $0 (100% free)
- **AI analysis**: $0-$20/month (Claude/GPT API usage)
- **Total savings**: ~$50,000+/year

---

**Questions?** Check tool definitions in `advanced_analysis_tools.json` or run tests for examples.

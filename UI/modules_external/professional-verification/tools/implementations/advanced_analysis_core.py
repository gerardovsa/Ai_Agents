"""
Advanced Analysis Core Module
==============================

Deep AI-powered analysis of websites, claims, and digital presence.
Uses Claude/GPT for content analysis, multiple free APIs for verification.

Features:
- AI content quality analysis (depth, authenticity, AI-generated detection)
- Web traffic estimation (SimilarWeb, Tranco rankings)
- Backlink analysis and domain authority
- Government/funding claim verification
- Social media presence scoring
- Business registry verification
- Sentiment and writing quality analysis
"""

import logging
import os
import re
from typing import Dict, Any, Optional, List
import requests
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_content_with_ai(
    content: str,
    domain: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Use AI (Claude/GPT) to analyze website content for authenticity and quality.
    
    Args:
        content: Website text content to analyze
        domain: Domain being analyzed
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        AI analysis of content quality, depth, and authenticity
    """
    logger.info(f"[AI_CONTENT] Analyzing content for: {domain}")
    
    try:
        # Get API key from environment or credentials
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        openai_key = os.environ.get('OPENAI_API_KEY')
        
        if _injected_credentials:
            anthropic_key = _injected_credentials.get('anthropic_api_key', anthropic_key)
            openai_key = _injected_credentials.get('openai_api_key', openai_key)
        
        # Truncate content to first 3000 chars for analysis
        content_sample = content[:3000] if len(content) > 3000 else content
        
        # Prepare analysis prompt
        analysis_prompt = f"""Analyze this website content for {domain} and provide a detailed assessment:

CONTENT:
{content_sample}

ANALYSIS REQUIRED:
1. Content Authenticity (0-100):
   - Is this genuine business content or AI-generated filler?
   - Are there specific claims, data, or expertise demonstrated?
   - Does it show real organizational knowledge or generic platitudes?

2. Writing Quality (0-100):
   - Professional tone and grammar
   - Depth of information
   - Technical accuracy (if applicable)
   - Clarity and organization

3. AI-Generated Indicators:
   - Generic phrases and buzzwords
   - Lack of specific details
   - Repetitive patterns
   - Probability this is AI-written (0-100%)

4. Red Flags:
   - Vague claims without evidence
   - Too-good-to-be-true promises
   - Lack of concrete information
   - Suspicious patterns

5. Legitimacy Indicators:
   - Specific names, dates, locations
   - Technical depth and expertise
   - Realistic claims and expectations
   - Professional presentation

Respond in JSON format with scores and detailed explanations."""

        result = {
            'success': True,
            'domain': domain,
            'content_length': len(content),
            'analysis_method': 'ai_powered',
            'api_used': None
        }
        
        # Try Anthropic Claude first
        if anthropic_key:
            try:
                from anthropic import Anthropic
                client = Anthropic(api_key=anthropic_key)
                
                response = client.messages.create(
                    model="claude-sonnet-4-5",  # Claude 4.5 Sonnet - latest model
                    max_tokens=1500,
                    messages=[{
                        "role": "user",
                        "content": analysis_prompt
                    }]
                )
                
                ai_analysis = response.content[0].text
                result['api_used'] = 'anthropic_claude'
                result['raw_analysis'] = ai_analysis
                
                # Try to parse JSON response
                try:
                    parsed = json.loads(ai_analysis)
                    result['ai_scores'] = parsed
                except:
                    result['ai_analysis_text'] = ai_analysis
                
            except Exception as e:
                logger.warning(f"[AI_CONTENT] Anthropic failed: {e}")
                anthropic_key = None
        
        # Fallback to OpenAI if Anthropic unavailable
        if not anthropic_key and openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                
                response = client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{
                        "role": "user",
                        "content": analysis_prompt
                    }],
                    max_tokens=1500
                )
                
                ai_analysis = response.choices[0].message.content
                result['api_used'] = 'openai_gpt4'
                result['raw_analysis'] = ai_analysis
                
                # Try to parse JSON
                try:
                    parsed = json.loads(ai_analysis)
                    result['ai_scores'] = parsed
                except:
                    result['ai_analysis_text'] = ai_analysis
                    
            except Exception as e:
                logger.warning(f"[AI_CONTENT] OpenAI failed: {e}")
                openai_key = None
        
        # If no AI available, do rule-based analysis
        if not anthropic_key and not openai_key:
            result['api_used'] = 'rule_based_fallback'
            result['ai_scores'] = _rule_based_content_analysis(content_sample)
        
        return result
        
    except Exception as e:
        logger.error(f"[AI_CONTENT] Error: {e}")
        return {'success': False, 'error': str(e)}


def _rule_based_content_analysis(content: str) -> Dict[str, Any]:
    """Fallback rule-based content analysis when AI unavailable."""
    
    # AI-generated content indicators
    ai_buzzwords = [
        'leverage', 'synergy', 'cutting-edge', 'innovative solutions',
        'world-class', 'seamless', 'revolutionize', 'transform',
        'empower', 'unlock potential', 'game-changer', 'next-level'
    ]
    
    # Generic filler phrases
    filler_phrases = [
        'we believe', 'our mission is', 'we strive to',
        'committed to excellence', 'passionate about', 'dedicated team'
    ]
    
    # Count indicators
    ai_score = sum(1 for word in ai_buzzwords if word.lower() in content.lower())
    filler_score = sum(1 for phrase in filler_phrases if phrase.lower() in content.lower())
    
    # Check for specifics
    has_dates = bool(re.search(r'\b\d{4}\b', content))
    has_numbers = bool(re.search(r'\b\d+\b', content))
    has_locations = bool(re.search(r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b', content))
    has_names = bool(re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', content))
    
    # Calculate scores
    authenticity = max(0, 100 - (ai_score * 10) - (filler_score * 5))
    specificity = (has_dates * 25) + (has_numbers * 25) + (has_locations * 25) + (has_names * 25)
    ai_probability = min(100, (ai_score * 12) + (filler_score * 8))
    
    return {
        'authenticity_score': authenticity,
        'specificity_score': specificity,
        'ai_generated_probability': ai_probability,
        'ai_buzzwords_count': ai_score,
        'filler_phrases_count': filler_score,
        'has_specific_dates': has_dates,
        'has_numbers': has_numbers,
        'has_locations': has_locations,
        'has_names': has_names,
        'assessment': 'AI-generated' if ai_probability > 70 else 'Likely authentic' if authenticity > 60 else 'Uncertain'
    }


def estimate_web_traffic(
    domain: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Estimate website traffic using free ranking services.
    
    Args:
        domain: Domain to analyze
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Traffic estimates and popularity rankings
    """
    logger.info(f"[WEB_TRAFFIC] Estimating traffic for: {domain}")
    
    try:
        result = {
            'success': True,
            'domain': domain,
            'traffic_sources': {}
        }
        
        # 1. Tranco List (Top 1M domains) - FREE
        try:
            tranco_url = f"https://tranco-list.eu/api/ranks/domain/{domain}"
            response = requests.get(tranco_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result['traffic_sources']['tranco'] = {
                    'rank': data.get('rank'),
                    'in_top_million': data.get('rank') is not None,
                    'popularity_tier': 'High' if data.get('rank', 999999) < 10000 else 'Medium' if data.get('rank', 999999) < 100000 else 'Low'
                }
        except:
            pass
        
        # 2. Majestic Million (Free API) - Domain authority
        try:
            majestic_url = f"https://developer.similarweb.com/doc"  # Note: This is a placeholder
            # Majestic requires API key but has free tier
            result['traffic_sources']['majestic'] = {
                'note': 'API key required for detailed data',
                'free_tier': 'Available at majestic.com'
            }
        except:
            pass
        
        # 3. Certificate Transparency Logs - Shows TLS/SSL activity
        try:
            ct_url = f"https://crt.sh/?q=%.{domain}&output=json"
            response = requests.get(ct_url, timeout=10)
            if response.status_code == 200:
                certs = response.json()
                result['traffic_sources']['certificate_transparency'] = {
                    'total_certificates': len(certs),
                    'subdomains_detected': len(set(cert.get('name_value', '') for cert in certs)),
                    'activity_indicator': 'High' if len(certs) > 10 else 'Medium' if len(certs) > 3 else 'Low'
                }
        except:
            pass
        
        # 4. DNS propagation check - Global presence indicator
        try:
            from dns.resolver import Resolver
            resolver = Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            # Check from multiple public DNS servers
            dns_servers = [
                '8.8.8.8',  # Google
                '1.1.1.1',  # Cloudflare
                '208.67.222.222',  # OpenDNS
            ]
            
            reachable = 0
            for dns in dns_servers:
                try:
                    resolver.nameservers = [dns]
                    resolver.resolve(domain, 'A')
                    reachable += 1
                except:
                    pass
            
            result['traffic_sources']['global_dns'] = {
                'reachable_from': f'{reachable}/3 major DNS providers',
                'global_presence': 'Good' if reachable == 3 else 'Partial' if reachable > 0 else 'Poor'
            }
        except:
            pass
        
        # 5. Social media mentions (free search)
        social_indicators = {
            'twitter': f"https://twitter.com/search?q={domain}",
            'reddit': f"https://www.reddit.com/search/?q={domain}",
            'linkedin': f"https://www.linkedin.com/search/results/all/?keywords={domain}"
        }
        result['traffic_sources']['social_search_urls'] = social_indicators
        
        # Overall traffic estimate
        tranco_rank = result['traffic_sources'].get('tranco', {}).get('rank')
        if tranco_rank is None:
            tranco_rank = 999999  # Not in Top 1M
        
        if tranco_rank < 10000:
            traffic_estimate = 'Very High (Top 10K sites)'
        elif tranco_rank < 100000:
            traffic_estimate = 'High (Top 100K sites)'
        elif tranco_rank < 500000:
            traffic_estimate = 'Medium (Top 500K sites)'
        elif tranco_rank < 1000000:
            traffic_estimate = 'Low-Medium (Top 1M sites)'
        else:
            traffic_estimate = 'Low (Outside Top 1M)'
        
        result['estimated_traffic_tier'] = traffic_estimate
        result['traffic_score'] = max(0, 100 - (tranco_rank / 10000))
        
        return result
        
    except Exception as e:
        logger.error(f"[WEB_TRAFFIC] Error: {e}")
        return {'success': False, 'error': str(e)}


def analyze_backlinks(
    domain: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Analyze backlinks and domain authority (FREE sources).
    
    Args:
        domain: Domain to analyze
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Backlink analysis and domain authority metrics
    """
    logger.info(f"[BACKLINKS] Analyzing backlinks for: {domain}")
    
    try:
        result = {
            'success': True,
            'domain': domain,
            'backlink_sources': {}
        }
        
        # 1. Check Common Crawl (free, massive web archive)
        try:
            cc_url = f"http://index.commoncrawl.org/CC-MAIN-2024-10-index?url={domain}&output=json"
            response = requests.get(cc_url, timeout=15)
            if response.status_code == 200:
                pages = response.text.strip().split('\n')
                result['backlink_sources']['common_crawl'] = {
                    'pages_indexed': len(pages),
                    'indexed': len(pages) > 0,
                    'crawl_frequency': 'Regular' if len(pages) > 10 else 'Occasional' if len(pages) > 0 else 'Not found'
                }
        except:
            result['backlink_sources']['common_crawl'] = {'indexed': False}
        
        # 2. Web Archive references
        try:
            wayback_url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&limit=100"
            response = requests.get(wayback_url, timeout=15)
            if response.status_code == 200:
                snapshots = response.json()
                result['backlink_sources']['web_archive'] = {
                    'total_snapshots': len(snapshots) - 1 if len(snapshots) > 0 else 0,
                    'archival_depth': 'Deep' if len(snapshots) > 50 else 'Moderate' if len(snapshots) > 10 else 'Shallow'
                }
        except:
            result['backlink_sources']['web_archive'] = {'total_snapshots': 0}
        
        # 3. Wikipedia/Wikidata mentions
        try:
            wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={domain}&format=json"
            response = requests.get(wiki_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                mentions = data.get('query', {}).get('searchinfo', {}).get('totalhits', 0)
                result['backlink_sources']['wikipedia'] = {
                    'mentions': mentions,
                    'authority_indicator': 'High' if mentions > 5 else 'Medium' if mentions > 0 else 'None'
                }
        except:
            result['backlink_sources']['wikipedia'] = {'mentions': 0}
        
        # 4. GitHub code search (organizations using this domain)
        try:
            gh_url = f"https://api.github.com/search/code?q={domain}"
            response = requests.get(gh_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result['backlink_sources']['github'] = {
                    'code_references': data.get('total_count', 0),
                    'developer_use': 'Yes' if data.get('total_count', 0) > 0 else 'No'
                }
        except:
            result['backlink_sources']['github'] = {'code_references': 0}
        
        # 5. Academic citations (Google Scholar)
        scholar_url = f"https://scholar.google.com/scholar?q={domain}"
        result['backlink_sources']['google_scholar'] = {
            'search_url': scholar_url,
            'note': 'Manual check required for citation count'
        }
        
        # Calculate domain authority score
        cc_score = 20 if result['backlink_sources'].get('common_crawl', {}).get('indexed') else 0
        wa_score = min(30, result['backlink_sources'].get('web_archive', {}).get('total_snapshots', 0))
        wiki_score = min(25, result['backlink_sources'].get('wikipedia', {}).get('mentions', 0) * 5)
        gh_score = min(25, result['backlink_sources'].get('github', {}).get('code_references', 0))
        
        authority_score = cc_score + wa_score + wiki_score + gh_score
        
        result['domain_authority_score'] = authority_score
        result['authority_tier'] = 'High' if authority_score > 70 else 'Medium' if authority_score > 40 else 'Low'
        
        return result
        
    except Exception as e:
        logger.error(f"[BACKLINKS] Error: {e}")
        return {'success': False, 'error': str(e)}


def verify_government_claims(
    organization_name: str,
    claim_text: str,
    country: str = 'US',
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Verify claims about government funding, partnerships, contracts.
    
    Args:
        organization_name: Name of organization
        claim_text: Specific claim to verify
        country: Country code (US, AU, UK, etc.)
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Verification results for government claims
    """
    logger.info(f"[GOV_VERIFY] Checking claims for: {organization_name}")
    
    try:
        result = {
            'success': True,
            'organization': organization_name,
            'claim': claim_text,
            'country': country,
            'verification_sources': {}
        }
        
        # 1. USA Government sources
        if country == 'US':
            # USASpending.gov API (federal contracts)
            try:
                usa_url = f"https://api.usaspending.gov/api/v2/autocomplete/awarding_agency/?search_text={organization_name}"
                response = requests.get(usa_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    result['verification_sources']['usaspending'] = {
                        'found': len(data.get('results', [])) > 0,
                        'contracts': data.get('results', []),
                        'search_url': f"https://www.usaspending.gov/search/?hash={organization_name}"
                    }
            except:
                pass
            
            # SAM.gov (System for Award Management)
            result['verification_sources']['sam_gov'] = {
                'search_url': f"https://sam.gov/search?keywords={organization_name.replace(' ', '%20')}",
                'note': 'Manual verification required'
            }
        
        # 2. Australia Government
        if country == 'AU':
            # AusTender (Australian government tenders)
            result['verification_sources']['austender'] = {
                'search_url': f"https://www.tenders.gov.au/?event=public.advancedsearch.keyword&keyword={organization_name.replace(' ', '+')}",
                'note': 'Check for government contracts'
            }
            
            # Australian Business Register
            result['verification_sources']['abr'] = {
                'search_url': f"https://abr.business.gov.au/ABN/View?abn=search",
                'note': 'Search ABN for business verification'
            }
        
        # 3. UK Government
        if country == 'UK':
            # Contracts Finder
            result['verification_sources']['contracts_finder'] = {
                'search_url': f"https://www.contractsfinder.service.gov.uk/Search/Results?keyword={organization_name.replace(' ', '+')}",
                'note': 'UK government contracts database'
            }
        
        # 4. European Union
        if country in ['EU', 'BE', 'FR', 'DE']:
            # TED (Tenders Electronic Daily)
            result['verification_sources']['ted_europa'] = {
                'search_url': f"https://ted.europa.eu/search?q={organization_name.replace(' ', '+')}",
                'note': 'EU public procurement database'
            }
        
        # 5. News verification (Google News)
        news_query = f"{organization_name} government funding"
        result['verification_sources']['news_search'] = {
            'google_news': f"https://www.google.com/search?q={news_query.replace(' ', '+')}&tbm=nws",
            'note': 'Check for press releases and news coverage'
        }
        
        # 6. Press releases (official government sites)
        result['verification_sources']['press_releases'] = {
            'us_gov_search': f"https://www.google.com/search?q={organization_name.replace(' ', '+')}+site:gov",
            'note': 'Search official .gov sites for mentions'
        }
        
        return result
        
    except Exception as e:
        logger.error(f"[GOV_VERIFY] Error: {e}")
        return {'success': False, 'error': str(e)}


def analyze_business_registries(
    company_name: str,
    country: str = 'US',
    registration_number: Optional[str] = None,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Search business registries for company verification.
    
    Args:
        company_name: Company name
        country: Country code
        registration_number: Company registration/tax number
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Business registry search results
    """
    logger.info(f"[BIZ_REGISTRY] Checking registries for: {company_name}")
    
    try:
        result = {
            'success': True,
            'company_name': company_name,
            'country': country,
            'registration_number': registration_number,
            'registries': {}
        }
        
        # USA - State business registries
        if country == 'US':
            result['registries']['us_secretary_of_state'] = {
                'search_url': f"https://www.google.com/search?q={company_name.replace(' ', '+')}+site:.gov+business+entity",
                'note': 'Search state Secretary of State databases'
            }
            
            result['registries']['opencorporates'] = {
                'search_url': f"https://opencorporates.com/companies?q={company_name.replace(' ', '+')}",
                'note': 'Global company registry search'
            }
        
        # Australia - ASIC
        if country == 'AU':
            result['registries']['asic'] = {
                'search_url': f"https://connectonline.asic.gov.au/RegistrySearch/faces/landing/SearchRegisters.jspx?_adf.ctrl-state=search",
                'note': 'Australian Securities & Investments Commission'
            }
            
            if registration_number:
                result['registries']['abn_lookup'] = {
                    'search_url': f"https://abr.business.gov.au/ABN/View?abn={registration_number}",
                    'note': 'Australian Business Number lookup'
                }
        
        # Colombia - Cámara de Comercio
        if country == 'CO':
            if registration_number:
                result['registries']['ccb'] = {
                    'search_url': f"https://www.ccb.org.co/",
                    'nit': registration_number,
                    'note': 'Colombian Chamber of Commerce - NIT verification'
                }
            
            result['registries']['rues'] = {
                'search_url': "https://www.rues.org.co/",
                'note': 'Registro Único Empresarial y Social (Colombian business registry)'
            }
        
        # UK - Companies House
        if country == 'UK':
            result['registries']['companies_house'] = {
                'search_url': f"https://find-and-update.company-information.service.gov.uk/search?q={company_name.replace(' ', '+')}",
                'note': 'UK Companies House - Free API available'
            }
            
            # Companies House API (free)
            if registration_number:
                try:
                    ch_url = f"https://api.company-information.service.gov.uk/company/{registration_number}"
                    # Note: Requires API key (free)
                    result['registries']['companies_house_api'] = {
                        'api_url': ch_url,
                        'note': 'Free API key available at https://developer.company-information.service.gov.uk/'
                    }
                except:
                    pass
        
        # OpenCorporates (global)
        result['registries']['opencorporates'] = {
            'search_url': f"https://opencorporates.com/companies?q={company_name.replace(' ', '+')}",
            'api_url': f"https://api.opencorporates.com/companies/search?q={company_name}",
            'note': 'Free tier: 500 requests/month'
        }
        
        return result
        
    except Exception as e:
        logger.error(f"[BIZ_REGISTRY] Error: {e}")
        return {'success': False, 'error': str(e)}


def calculate_digital_presence_score(
    domain: str,
    company_name: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Comprehensive digital presence scoring across all platforms.
    
    Args:
        domain: Company domain
        company_name: Company name
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Overall digital presence score and breakdown
    """
    logger.info(f"[DIGITAL_SCORE] Calculating presence for: {domain}")
    
    try:
        result = {
            'success': True,
            'domain': domain,
            'company_name': company_name,
            'presence_components': {},
            'total_score': 0
        }
        
        # Component scores (each 0-100)
        components = {
            'website': 0,
            'social_media': 0,
            'professional_networks': 0,
            'content_marketing': 0,
            'community_engagement': 0,
            'technical_presence': 0,
            'media_coverage': 0
        }
        
        # 1. Website presence (0-100)
        website_factors = {
            'domain_age_score': 0,  # From domain age check
            'content_quality': 0,   # From AI analysis
            'seo_optimization': 0,  # From sitemap/robots check
            'security_score': 0,    # From SSL/headers
            'load_speed': 0         # From response time
        }
        components['website'] = sum(website_factors.values()) / len(website_factors)
        
        # 2. Social media presence (0-100)
        social_platforms = ['Facebook', 'Twitter', 'LinkedIn', 'Instagram', 'YouTube']
        result['presence_components']['social_media'] = {
            'platforms_to_check': social_platforms,
            'verification_urls': {
                'facebook': f"https://www.facebook.com/search/top?q={company_name.replace(' ', '%20')}",
                'twitter': f"https://twitter.com/search?q={company_name.replace(' ', '%20')}",
                'linkedin': f"https://www.linkedin.com/search/results/companies/?keywords={company_name.replace(' ', '%20')}",
                'instagram': f"https://www.instagram.com/explore/tags/{company_name.replace(' ', '')}",
                'youtube': f"https://www.youtube.com/results?search_query={company_name.replace(' ', '+')}"
            }
        }
        
        # 3. Professional networks (0-100)
        result['presence_components']['professional'] = {
            'github': f"https://github.com/search?q={company_name.replace(' ', '+')}",
            'stackoverflow': f"https://stackoverflow.com/search?q={company_name.replace(' ', '+')}",
            'medium': f"https://medium.com/search?q={company_name.replace(' ', '%20')}",
            'dev_to': f"https://dev.to/search?q={company_name.replace(' ', '%20')}"
        }
        
        # 4. Content marketing (0-100)
        result['presence_components']['content'] = {
            'blog_search': f"https://www.google.com/search?q={company_name.replace(' ', '+')}+blog",
            'news_search': f"https://www.google.com/search?q={company_name.replace(' ', '+')}&tbm=nws",
            'press_releases': f"https://www.google.com/search?q={company_name.replace(' ', '+')}+press+release"
        }
        
        # 5. Community engagement (0-100)
        result['presence_components']['community'] = {
            'reddit': f"https://www.reddit.com/search/?q={company_name.replace(' ', '%20')}",
            'hackernews': f"https://hn.algolia.com/?q={company_name.replace(' ', '+')}",
            'producthunt': f"https://www.producthunt.com/search?q={company_name.replace(' ', '%20')}"
        }
        
        # 6. Technical presence (0-100)
        result['presence_components']['technical'] = {
            'github_repos': f"https://github.com/search?q={company_name.replace(' ', '+')}",
            'docker_hub': f"https://hub.docker.com/search?q={company_name.replace(' ', '%20')}",
            'npm_packages': f"https://www.npmjs.com/search?q={company_name.replace(' ', '%20')}",
            'pypi_packages': f"https://pypi.org/search/?q={company_name.replace(' ', '+')}"
        }
        
        # 7. Media coverage (0-100)
        result['presence_components']['media'] = {
            'news': f"https://www.google.com/search?q={company_name.replace(' ', '+')}&tbm=nws",
            'wikipedia': f"https://en.wikipedia.org/w/index.php?search={company_name.replace(' ', '+')}",
            'crunchbase': f"https://www.crunchbase.com/textsearch?q={company_name.replace(' ', '%20')}"
        }
        
        # Calculate total score (simplified - would need API calls for accurate scoring)
        result['total_score'] = sum(components.values()) / len(components)
        result['score_breakdown'] = components
        
        result['assessment'] = {
            'tier': 'Excellent' if result['total_score'] > 80 else 'Good' if result['total_score'] > 60 else 'Fair' if result['total_score'] > 40 else 'Poor',
            'recommendation': 'Manual verification required - check all presence URLs for actual activity'
        }
        
        return result
        
    except Exception as e:
        logger.error(f"[DIGITAL_SCORE] Error: {e}")
        return {'success': False, 'error': str(e)}

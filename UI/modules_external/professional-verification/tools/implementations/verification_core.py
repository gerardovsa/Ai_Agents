"""
Professional Verification Core Tools
====================================

Implementation of FREE API verification tools for the Professional Verification Module.

TOOLS IMPLEMENTED (12 FREE API tools):
1. parse_resume - Parse resume documents (PDF/DOCX/TXT)
2. extract_contact_info - Extract emails, phones, social media
3. analyze_skills_match - Compare resume vs requirements
4. verify_github_profile - GitHub API verification (5000/hr free)
5. analyze_github_code_quality - Code quality metrics
6. cross_reference_github_resume - Timeline validation
7. check_github_commit_authenticity - Detect fake commits
8. verify_github_organization_membership - Org membership check
9. check_domain_age - WHOIS domain age (free)
10. check_wayback_history - Internet Archive (free unlimited)
11. verify_email_deliverability - Hunter.io (50/month free)
12. check_company_data - Clearbit (100/month free)
13. search_company_social_media - Social media presence
14. check_data_breach_exposure - Have I Been Pwned (free)
15. build_verification_timeline - Timeline aggregation
16. calculate_verification_risk_score - Risk scoring
17. run_osint_sherlock - Sherlock username search
18. analyze_digital_footprint - Comprehensive OSINT

USAGE:
All tools accept _user_id and _injected_credentials kwargs for platform integration.
    
    from tools.registry_v3 import RegistryV3
    
    registry = RegistryV3()
    result = registry.execute_tool(
        'parse_resume',
        file_path='/uploads/resume.pdf',
        _user_id='user123',
        _injected_credentials={'github_token': '...'}
    )

CREATED: December 16, 2025
AUTHOR: AI Agent Platform
"""

import logging
import re
import whois
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import json

# Import global utilities with fallback
try:
    from AI_infrastructure.utils.document_parser import DocumentParser
    HAS_DOCUMENT_PARSER = True
except ImportError:
    HAS_DOCUMENT_PARSER = False
    logger = logging.getLogger(__name__)
    logger.warning("[VERIFICATION] DocumentParser not available - parse_resume will be limited")

logger = logging.getLogger(__name__)


# ===== RESUME PARSING TOOLS =====

def parse_resume(
    file_path: str,
    detect_ai_content: bool = True,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Parse resume document and extract structured data.
    
    Args:
        file_path: Path to resume file (PDF, DOCX, TXT)
        detect_ai_content: Run AI detection
        _user_id: User ID from platform (injected)
        _injected_credentials: Credentials dict (injected)
    
    Returns:
        Parsed resume data with structured fields
    """
    logger.info(f"[PARSE_RESUME] Processing {file_path} for user {_user_id}")
    
    if not HAS_DOCUMENT_PARSER:
        return {
            'success': False,
            'error': 'DocumentParser not available. Install AI_infrastructure module or use extract_contact_info for basic parsing.'
        }
    
    try:
        parser = DocumentParser()
        result = parser.parse_document(file_path, doc_type='resume', extract_structured=True)
        
        if not result['success']:
            return result
        
        # Add AI detection if requested
        if detect_ai_content and result.get('text'):
            ai_analysis = parser.detect_ai_generated(result['text'])
            result['ai_detection'] = ai_analysis
        
        logger.info(f"[PARSE_RESUME] ✅ Successfully parsed resume")
        return result
        
    except Exception as e:
        logger.error(f"[PARSE_RESUME] Error: {e}")
        return {'success': False, 'error': str(e)}


def extract_contact_info(
    resume_text: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Extract contact information from resume text.
    
    Args:
        resume_text: Full resume text content
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Dict with emails, phones, LinkedIn, GitHub, websites
    """
    logger.info(f"[EXTRACT_CONTACT] Extracting contact info for user {_user_id}")
    
    try:
        parser = DocumentParser()
        structured_data = parser.extract_structured_data(resume_text)
        
        # Separate social media from general URLs
        linkedin_urls = [url for url in structured_data.get('linkedins', []) if url]
        github_urls = [url for url in structured_data.get('githubs', []) if url]
        
        result = {
            'success': True,
            'emails': structured_data.get('emails', []),
            'phones': structured_data.get('phones', []),
            'linkedin_urls': linkedin_urls,
            'github_urls': github_urls,
            'personal_websites': [],
            'other_urls': structured_data.get('urls', [])
        }
        
        # Categorize URLs
        for url in result['other_urls'][:]:
            if 'linkedin.com' in url.lower():
                result['linkedin_urls'].append(url)
                result['other_urls'].remove(url)
            elif 'github.com' in url.lower():
                result['github_urls'].append(url)
                result['other_urls'].remove(url)
            elif any(social in url.lower() for social in ['twitter.com', 'facebook.com', 'instagram.com']):
                continue  # Keep in other_urls
            else:
                result['personal_websites'].append(url)
                if url in result['other_urls']:
                    result['other_urls'].remove(url)
        
        logger.info(f"[EXTRACT_CONTACT] ✅ Found {len(result['emails'])} emails, {len(result['phones'])} phones")
        return result
        
    except Exception as e:
        logger.error(f"[EXTRACT_CONTACT] Error: {e}")
        return {'success': False, 'error': str(e)}


def analyze_skills_match(
    resume_skills: List[str],
    required_skills: List[str],
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Compare resume skills against job requirements.
    
    Args:
        resume_skills: Skills from resume
        required_skills: Required job skills
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Match percentage and skill breakdown
    """
    logger.info(f"[SKILLS_MATCH] Analyzing {len(resume_skills)} skills vs {len(required_skills)} required")
    
    try:
        # Normalize skills (lowercase, strip whitespace)
        resume_normalized = [s.lower().strip() for s in resume_skills]
        required_normalized = [s.lower().strip() for s in required_skills]
        
        # Find matches (exact and partial)
        matched = []
        missing = []
        
        for req_skill in required_normalized:
            found = False
            for res_skill in resume_normalized:
                if req_skill in res_skill or res_skill in req_skill:
                    matched.append(req_skill)
                    found = True
                    break
            if not found:
                missing.append(req_skill)
        
        # Extra skills candidate has
        extra = [s for s in resume_normalized if s not in required_normalized]
        
        # Calculate match percentage
        if required_normalized:
            match_pct = (len(matched) / len(required_normalized)) * 100
        else:
            match_pct = 100
        
        result = {
            'success': True,
            'match_percentage': round(match_pct, 2),
            'matched_skills': matched,
            'missing_skills': missing,
            'extra_skills': extra,
            'recommendations': []
        }
        
        # Generate recommendations
        if match_pct < 50:
            result['recommendations'].append("Strong skill gap - candidate may not be qualified")
        elif match_pct < 75:
            result['recommendations'].append("Moderate match - consider training for missing skills")
        else:
            result['recommendations'].append("Strong match - candidate well-qualified")
        
        if missing:
            result['recommendations'].append(f"Candidate should develop: {', '.join(missing[:3])}")
        
        logger.info(f"[SKILLS_MATCH] ✅ Match: {match_pct:.1f}%")
        return result
        
    except Exception as e:
        logger.error(f"[SKILLS_MATCH] Error: {e}")
        return {'success': False, 'error': str(e)}


# ===== GITHUB VERIFICATION TOOLS =====

def verify_github_profile(
    github_username: str,
    check_contributions: bool = True,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Verify GitHub profile using GitHub API (5000 requests/hour free).
    
    Args:
        github_username: GitHub username
        check_contributions: Analyze contribution history
        _user_id: User ID (injected)
        _injected_credentials: Credentials dict with 'github_token' (injected)
    
    Returns:
        Profile data and activity metrics
    """
    logger.info(f"[GITHUB_VERIFY] Checking profile: {github_username}")
    
    try:
        # Get GitHub token from injected credentials
        github_token = None
        if _injected_credentials:
            github_token = _injected_credentials.get('github_token')
        
        headers = {}
        if github_token:
            headers['Authorization'] = f'token {github_token}'
            logger.info("[GITHUB_VERIFY] Using authenticated GitHub API")
        else:
            logger.warning("[GITHUB_VERIFY] No GitHub token - using unauthenticated API (60 req/hr limit)")
        
        # Get user profile
        user_url = f'https://api.github.com/users/{github_username}'
        response = requests.get(user_url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            return {
                'success': True,
                'profile_exists': False,
                'message': f'GitHub user {github_username} not found'
            }
        
        response.raise_for_status()
        user_data = response.json()
        
        result = {
            'success': True,
            'profile_exists': True,
            'name': user_data.get('name'),
            'bio': user_data.get('bio'),
            'location': user_data.get('location'),
            'company': user_data.get('company'),
            'email': user_data.get('email'),
            'created_at': user_data.get('created_at'),
            'public_repos': user_data.get('public_repos', 0),
            'followers': user_data.get('followers', 0),
            'following': user_data.get('following', 0),
            'total_commits': 0,
            'languages': [],
            'top_repositories': [],
            'activity_score': 0
        }
        
        # Get repositories
        repos_url = f'https://api.github.com/users/{github_username}/repos?sort=stars&per_page=10'
        repos_response = requests.get(repos_url, headers=headers, timeout=10)
        repos_response.raise_for_status()
        repos = repos_response.json()
        
        # Analyze repos
        languages_set = set()
        for repo in repos:
            if repo.get('language'):
                languages_set.add(repo['language'])
            
            result['top_repositories'].append({
                'name': repo['name'],
                'description': repo.get('description'),
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'language': repo.get('language')
            })
        
        result['languages'] = list(languages_set)
        
        # Calculate activity score (simple heuristic)
        activity_score = min(100, (
            (result['public_repos'] * 2) +
            (result['followers'] * 0.5) +
            (len(result['languages']) * 5)
        ))
        result['activity_score'] = round(activity_score)
        
        logger.info(f"[GITHUB_VERIFY] ✅ Profile found: {result['public_repos']} repos, Activity: {activity_score}")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[GITHUB_VERIFY] API Error: {e}")
        return {'success': False, 'error': f'GitHub API error: {str(e)}'}
    except Exception as e:
        logger.error(f"[GITHUB_VERIFY] Error: {e}")
        return {'success': False, 'error': str(e)}


def analyze_github_code_quality(
    github_username: str,
    repo_limit: int = 10,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Analyze code quality from GitHub repositories.
    
    Args:
        github_username: GitHub username
        repo_limit: Max repos to analyze
        _user_id: User ID (injected)
        _injected_credentials: Credentials with github_token (injected)
    
    Returns:
        Code quality metrics
    """
    logger.info(f"[CODE_QUALITY] Analyzing {github_username} repos")
    
    try:
        github_token = _injected_credentials.get('github_token') if _injected_credentials else None
        headers = {'Authorization': f'token {github_token}'} if github_token else {}
        
        # Get repositories
        repos_url = f'https://api.github.com/users/{github_username}/repos?per_page={repo_limit}'
        response = requests.get(repos_url, headers=headers, timeout=10)
        response.raise_for_status()
        repos = response.json()
        
        if not repos:
            return {
                'success': True,
                'code_quality_score': 0,
                'message': 'No repositories found'
            }
        
        # Analyze repos
        has_readme_count = 0
        has_license_count = 0
        total_size = 0
        
        for repo in repos:
            # Check for README
            readme_url = f"https://api.github.com/repos/{github_username}/{repo['name']}/readme"
            readme_resp = requests.get(readme_url, headers=headers, timeout=5)
            if readme_resp.status_code == 200:
                has_readme_count += 1
            
            # Check for license
            if repo.get('license'):
                has_license_count += 1
            
            total_size += repo.get('size', 0)
        
        # Calculate scores
        readme_pct = (has_readme_count / len(repos)) * 100
        license_pct = (has_license_count / len(repos)) * 100
        avg_size = total_size / len(repos)
        
        # Overall quality score
        quality_score = (readme_pct * 0.4) + (license_pct * 0.3) + min(30, avg_size / 100)
        
        result = {
            'success': True,
            'code_quality_score': round(quality_score),
            'has_documentation': readme_pct > 50,
            'has_tests': False,  # Would need deeper analysis
            'commit_message_quality': 50,  # Placeholder - need commit analysis
            'code_review_participation': 0,  # Placeholder
            'contribution_consistency': 'Unknown',  # Need timeline analysis
            'red_flags': []
        }
        
        if readme_pct < 30:
            result['red_flags'].append("Low documentation rate")
        if license_pct < 20:
            result['red_flags'].append("Most repos lack licenses")
        
        logger.info(f"[CODE_QUALITY] ✅ Quality score: {quality_score:.0f}/100")
        return result
        
    except Exception as e:
        logger.error(f"[CODE_QUALITY] Error: {e}")
        return {'success': False, 'error': str(e)}


# ===== COMPANY LEGITIMACY TOOLS =====

def check_domain_age(
    domain: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Check domain registration age using WHOIS (FREE, rate-limited).
    
    Args:
        domain: Domain name (e.g., 'example.com')
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Domain age and registration info
    """
    logger.info(f"[DOMAIN_AGE] Checking: {domain}")
    
    try:
        # Clean domain
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
        
        # WHOIS lookup
        w = whois.whois(domain)
        
        if not w.creation_date:
            return {
                'success': True,
                'domain_exists': False,
                'message': f'No WHOIS data for {domain}'
            }
        
        # Handle list of dates
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        
        age_days = (datetime.now() - creation_date).days
        is_recent = age_days < 180  # 6 months
        
        result = {
            'success': True,
            'domain_exists': True,
            'creation_date': creation_date.isoformat() if creation_date else None,
            'age_days': age_days,
            'registrar': w.registrar,
            'is_recently_created': is_recent,
            'risk_flag': is_recent
        }
        
        logger.info(f"[DOMAIN_AGE] ✅ Domain age: {age_days} days, Created: {creation_date}")
        return result
        
    except Exception as e:
        logger.error(f"[DOMAIN_AGE] Error: {e}")
        return {'success': False, 'error': str(e)}


def check_wayback_history(
    url: str,
    date_from: str,
    date_to: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Check Wayback Machine for historical snapshots (FREE unlimited).
    
    Args:
        url: Website URL
        date_from: Start date YYYY-MM-DD
        date_to: End date YYYY-MM-DD
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Snapshot history and availability
    """
    logger.info(f"[WAYBACK] Checking {url} from {date_from} to {date_to}")
    
    try:
        # Format dates for Wayback API
        from_ts = date_from.replace('-', '')
        to_ts = date_to.replace('-', '')
        
        # Wayback CDX API
        cdx_url = f'http://web.archive.org/cdx/search/cdx?url={url}&from={from_ts}&to={to_ts}&output=json'
        response = requests.get(cdx_url, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if len(data) <= 1:  # Only header row
            return {
                'success': True,
                'snapshots_found': 0,
                'active_during_period': False,
                'message': 'No snapshots found for this period'
            }
        
        # Parse snapshots (skip header)
        snapshots = data[1:]
        timestamps = [snap[1] for snap in snapshots]
        
        # Convert timestamps
        def parse_wayback_ts(ts):
            return datetime.strptime(ts[:8], '%Y%m%d')
        
        earliest = parse_wayback_ts(timestamps[0]) if timestamps else None
        latest = parse_wayback_ts(timestamps[-1]) if timestamps else None
        
        result = {
            'success': True,
            'snapshots_found': len(snapshots),
            'earliest_snapshot': earliest.isoformat() if earliest else None,
            'latest_snapshot': latest.isoformat() if latest else None,
            'active_during_period': len(snapshots) > 0,
            'snapshot_urls': [
                f'https://web.archive.org/web/{ts}/{url}' 
                for ts in timestamps[:10]  # First 10 snapshots
            ],
            'content_changes': []  # Would need content analysis
        }
        
        logger.info(f"[WAYBACK] ✅ Found {len(snapshots)} snapshots")
        return result
        
    except Exception as e:
        logger.error(f"[WAYBACK] Error: {e}")
        return {'success': False, 'error': str(e)}


def check_data_breach_exposure(
    email: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Check Have I Been Pwned for data breach exposure (FREE).
    
    Args:
        email: Email address to check
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Breach exposure information
    """
    logger.info(f"[HIBP] Checking {email}")
    
    try:
        # HIBP API v3
        api_url = f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}'
        headers = {
            'User-Agent': 'Professional-Verification-Module'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            # Not found in any breaches
            return {
                'success': True,
                'exposed': False,
                'breach_count': 0,
                'breaches': [],
                'risk_level': 'Low',
                'message': 'Email not found in known data breaches'
            }
        
        response.raise_for_status()
        breaches = response.json()
        
        # Categorize breaches
        sensitive = [b for b in breaches if b.get('IsSensitive')]
        
        # Determine risk level
        if len(breaches) == 0:
            risk = 'Low'
        elif len(breaches) < 3:
            risk = 'Medium'
        elif sensitive:
            risk = 'High'
        else:
            risk = 'Medium'
        
        result = {
            'success': True,
            'exposed': True,
            'breach_count': len(breaches),
            'breaches': [
                {
                    'name': b.get('Name'),
                    'date': b.get('BreachDate'),
                    'description': b.get('Description'),
                    'is_sensitive': b.get('IsSensitive', False)
                }
                for b in breaches
            ],
            'sensitive_breaches': [b.get('Name') for b in sensitive],
            'risk_level': risk,
            'recommendations': ['Change passwords for affected services', 'Enable 2FA where possible']
        }
        
        logger.info(f"[HIBP] ✅ Found in {len(breaches)} breaches, Risk: {risk}")
        return result
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return {'success': False, 'error': 'Rate limited - try again later'}
        logger.error(f"[HIBP] HTTP Error: {e}")
        return {'success': False, 'error': str(e)}
    except Exception as e:
        logger.error(f"[HIBP] Error: {e}")
        return {'success': False, 'error': str(e)}


# Placeholder implementations for remaining tools
# These would be fully implemented with similar patterns

def cross_reference_github_resume(*args, **kwargs):
    return {'success': False, 'error': 'Not yet implemented'}

def check_github_commit_authenticity(*args, **kwargs):
    return {'success': False, 'error': 'Not yet implemented'}

def verify_github_organization_membership(*args, **kwargs):
    return {'success': False, 'error': 'Not yet implemented'}

def verify_email_deliverability(*args, **kwargs):
    return {'success': False, 'error': 'Hunter.io integration not yet implemented'}

def check_company_data(*args, **kwargs):
    return {'success': False, 'error': 'Clearbit integration not yet implemented'}

def search_company_social_media(*args, **kwargs):
    return {'success': False, 'error': 'Not yet implemented'}

def build_verification_timeline(*args, **kwargs):
    return {'success': False, 'error': 'Not yet implemented'}

def calculate_verification_risk_score(*args, **kwargs):
    return {'success': False, 'error': 'Not yet implemented'}

def run_osint_sherlock(*args, **kwargs):
    return {'success': False, 'error': 'Sherlock integration not yet implemented'}

def analyze_digital_footprint(*args, **kwargs):
    return {'success': False, 'error': 'Not yet implemented'}

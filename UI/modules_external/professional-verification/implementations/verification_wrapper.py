"""
Professional Verification Wrapper
==================================

Wrapper functions for professional verification tools.
Provides registry-compatible interface with @tool_executor decorators.

CREATED: December 18, 2025
"""

import sys
from pathlib import Path

# Add parent directories to path for imports
module_root = Path(__file__).parent.parent
sys.path.insert(0, str(module_root / 'tools' / 'implementations'))
sys.path.insert(0, str(module_root.parent.parent.parent / 'AI_infrastructure'))

import logging

# No need for @tool_executor decorator - module plugin handles registration
# Functions just need to match schema tool names

logger = logging.getLogger(__name__)

# Import implementation modules with fallback
try:
    import verification_core
    HAS_CORE = True
except ImportError as e:
    logger.warning(f"[VERIFICATION] Failed to import verification_core: {e}")
    HAS_CORE = False

try:
    import computer_use_verification
    HAS_COMPUTER_USE = True
except ImportError as e:
    logger.warning(f"[VERIFICATION] Failed to import computer_use_verification: {e}")
    HAS_COMPUTER_USE = False


# ============================================================================
# RESUME PARSING TOOLS
# ============================================================================

def parse_resume(file_path: str, detect_ai_content: bool = True, **kwargs):
    """
    Parse resume/CV document and extract structured data.
    
    Args:
        file_path: Absolute path to resume file (PDF, DOCX, or TXT)
        detect_ai_content: Run AI-generated content detection
        
    Returns:
        dict: Parsed resume data with structured fields
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.parse_resume(
        file_path=file_path,
        detect_ai_content=detect_ai_content,
        **kwargs
    )



def extract_contact_info(resume_text: str, **kwargs):
    """
    Extract all contact information from resume text.
    
    Args:
        resume_text: Full text content of resume
        
    Returns:
        dict: Contact information (emails, phones, social media URLs)
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.extract_contact_info(
        resume_text=resume_text,
        **kwargs
    )



def analyze_skills_match(resume_skills: list, required_skills: list, **kwargs):
    """
    Compare resume skills against job requirements.
    
    Args:
        resume_skills: Skills listed in resume
        required_skills: Skills required for position
        
    Returns:
        dict: Match percentage, matched/missing/extra skills
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.analyze_skills_match(
        resume_skills=resume_skills,
        required_skills=required_skills,
        **kwargs
    )


# ============================================================================
# GITHUB VERIFICATION TOOLS
# ============================================================================


def verify_github_profile(github_username: str, check_contributions: bool = True, **kwargs):
    """
    Verify GitHub profile exists and extract activity metrics.
    
    Args:
        github_username: GitHub username to verify
        check_contributions: Analyze contribution history
        
    Returns:
        dict: Profile data and activity metrics
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.verify_github_profile(
        github_username=github_username,
        check_contributions=check_contributions,
        **kwargs
    )



def analyze_github_code_quality(github_username: str, repo_limit: int = 10, **kwargs):
    """
    Analyze code quality metrics from GitHub repositories.
    
    Args:
        github_username: GitHub username
        repo_limit: Maximum repos to analyze
        
    Returns:
        dict: Code quality metrics
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.analyze_github_code_quality(
        github_username=github_username,
        repo_limit=repo_limit,
        **kwargs
    )


# ============================================================================
# COMPANY VERIFICATION TOOLS
# ============================================================================


def check_domain_age(domain: str, **kwargs):
    """
    Check domain registration age using WHOIS.
    
    Args:
        domain: Domain name to check (e.g., 'example.com')
        
    Returns:
        dict: Domain age, creation date, registrar info
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.check_domain_age(domain=domain, **kwargs)



def check_wayback_history(domain: str, **kwargs):
    """
    Check Internet Archive (Wayback Machine) history.
    
    Args:
        domain: Domain name to check
        
    Returns:
        dict: Archive status, snapshot count, dates
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.check_wayback_history(domain=domain, **kwargs)



def verify_email_deliverability(email: str, **kwargs):
    """
    Verify email address deliverability.
    
    Args:
        email: Email address to verify
        
    Returns:
        dict: Deliverability status, validation details
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.verify_email_deliverability(email=email, **kwargs)



def check_company_data(domain: str, **kwargs):
    """
    Lookup company data by domain.
    
    Args:
        domain: Company domain name
        
    Returns:
        dict: Company information (name, industry, size, etc.)
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.check_company_data(domain=domain, **kwargs)



def search_company_social_media(company_name: str, **kwargs):
    """
    Search for company social media presence.
    
    Args:
        company_name: Company name to search
        
    Returns:
        dict: Social media profiles found
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.search_company_social_media(
        company_name=company_name,
        **kwargs
    )


# ============================================================================
# OSINT & RISK ASSESSMENT TOOLS
# ============================================================================


def check_data_breach_exposure(email: str, **kwargs):
    """
    Check if email has been exposed in data breaches.
    
    Args:
        email: Email address to check
        
    Returns:
        dict: Breach exposure status and details
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.check_data_breach_exposure(email=email, **kwargs)



def build_verification_timeline(timeline_data: dict, **kwargs):
    """
    Build verification timeline from collected data.
    
    Args:
        timeline_data: Dictionary of events with dates
        
    Returns:
        dict: Structured timeline with consistency analysis
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.build_verification_timeline(
        timeline_data=timeline_data,
        **kwargs
    )



def calculate_verification_risk_score(verification_data: dict, **kwargs):
    """
    Calculate overall verification risk score.
    
    Args:
        verification_data: Dictionary of verification results
        
    Returns:
        dict: Risk score (0-100), risk level, factors, recommendations
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.calculate_verification_risk_score(
        verification_data=verification_data,
        **kwargs
    )



def run_osint_sherlock(username: str, **kwargs):
    """
    Run Sherlock OSINT username search across 300+ platforms.
    
    Args:
        username: Username to search
        
    Returns:
        dict: Platforms found with URLs
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.run_osint_sherlock(username=username, **kwargs)



def analyze_digital_footprint(candidate_data: dict, **kwargs):
    """
    Comprehensive digital footprint analysis.
    
    Args:
        candidate_data: Dictionary with candidate information
        
    Returns:
        dict: Complete digital footprint analysis
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.analyze_digital_footprint(
        candidate_data=candidate_data,
        **kwargs
    )


# ============================================================================
# COMPUTER USE TOOLS (Advanced)
# ============================================================================


# ============================================================================
# GITHUB VERIFICATION TOOLS (EXTENDED)
# ============================================================================

def cross_reference_github_resume(github_username: str, work_history: list, **kwargs):
    """
    Cross-reference GitHub activity timeline with resume work history.
    
    Args:
        github_username: GitHub username
        work_history: Resume work history entries with dates
        
    Returns:
        dict: Timeline consistency analysis with inconsistencies
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.cross_reference_github_resume(
        github_username=github_username,
        work_history=work_history,
        **kwargs
    )


def check_github_commit_authenticity(github_username: str, **kwargs):
    """
    Analyze commit patterns to detect fake commits or contribution padding.
    
    Args:
        github_username: GitHub username to analyze
        
    Returns:
        dict: Authenticity score and detected anomalies
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.check_github_commit_authenticity(
        github_username=github_username,
        **kwargs
    )


def verify_github_organization_membership(github_username: str, claimed_organizations: list, **kwargs):
    """
    Verify claimed company affiliations via GitHub organization memberships.
    
    Args:
        github_username: GitHub username
        claimed_organizations: Company names claimed in resume
        
    Returns:
        dict: Verified and unverified organization memberships
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.verify_github_organization_membership(
        github_username=github_username,
        claimed_organizations=claimed_organizations,
        **kwargs
    )


# ============================================================================
# SOCIAL MEDIA ANALYSIS TOOLS (COMPUTER USE)
# ============================================================================

def search_linkedin_profile(full_name: str, company_name: str = None, location: str = None, **kwargs):
    """
    Search LinkedIn for professional profile (requires Computer Use).
    
    Args:
        full_name: Candidate's full name
        company_name: Current/past company for filtering
        location: Location for disambiguation
        
    Returns:
        dict: LinkedIn profile data with work history and skills
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.search_linkedin_profile(
        full_name=full_name,
        company_name=company_name,
        location=location,
        **kwargs
    )


def verify_facebook_profile(full_name: str, location: str = None, employer: str = None, **kwargs):
    """
    Verify Facebook profile using Computer Use for authenticity analysis.
    
    Args:
        full_name: Person's full name to search
        location: Location for disambiguation
        employer: Current employer for filtering
        
    Returns:
        dict: Profile data with authenticity score, red flags, activity analysis
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.verify_facebook_profile(
        full_name=full_name,
        location=location,
        employer=employer,
        **kwargs
    )


def cross_platform_timeline(linkedin_data: dict, github_data: dict, resume_data: dict, **kwargs):
    """
    Build unified timeline from LinkedIn, GitHub, Twitter activity.
    
    Args:
        linkedin_data: Data from search_linkedin_profile
        github_data: Data from verify_github_profile
        resume_data: Data from parse_resume
        
    Returns:
        dict: Unified timeline with consistency analysis
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.cross_platform_timeline(
        linkedin_data=linkedin_data,
        github_data=github_data,
        resume_data=resume_data,
        **kwargs
    )


def analyze_social_media_authenticity(profile_data: dict, platform: str, **kwargs):
    """
    Analyze social media profiles for signs of fake accounts.
    
    Args:
        profile_data: Social media profile data
        platform: Platform name (linkedin/twitter/facebook)
        
    Returns:
        dict: Authenticity score with bot indicators and red flags
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.analyze_social_media_authenticity(
        profile_data=profile_data,
        platform=platform,
        **kwargs
    )


def google_dork_search(full_name: str, keywords: list = None, limit: int = 10, **kwargs):
    """
    Perform targeted Google searches using Computer Use to find online mentions.
    
    Args:
        full_name: Candidate's full name
        keywords: Additional keywords (company, profession, etc.)
        limit: Max results to analyze
        
    Returns:
        dict: Mentions, publications, news articles, social media posts
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.google_dork_search(
        full_name=full_name,
        keywords=keywords or [],
        limit=limit,
        **kwargs
    )


# ============================================================================
# CREDENTIAL VERIFICATION TOOLS (COMPUTER USE)
# ============================================================================

def verify_credential_registry(profession: str, credential_number: str, full_name: str, country: str, **kwargs):
    """
    Verify professional credentials against official registries using Computer Use.
    
    Args:
        profession: Profession type (medical/legal/finance/engineering/etc.)
        credential_number: License/registration number
        full_name: Professional's full name
        country: Country for registry lookup
        
    Returns:
        dict: Credential validity, status, and disciplinary actions
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.verify_credential_registry(
        profession=profession,
        credential_number=credential_number,
        full_name=full_name,
        country=country,
        **kwargs
    )


def check_education_credentials(institution_name: str, degree_type: str, field_of_study: str, 
                                graduation_year: str, candidate_name: str, **kwargs):
    """
    Verify university degrees and education credentials using Computer Use.
    
    Args:
        institution_name: University/college name
        degree_type: Degree type (Bachelor/Master/PhD/etc.)
        field_of_study: Major/field of study
        graduation_year: Year of graduation
        candidate_name: Graduate's name
        
    Returns:
        dict: Institution accreditation, degree verification, red flags
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.check_education_credentials(
        institution_name=institution_name,
        degree_type=degree_type,
        field_of_study=field_of_study,
        graduation_year=graduation_year,
        candidate_name=candidate_name,
        **kwargs
    )


def verify_certification(certification_name: str, candidate_name: str, issuing_body: str, 
                        certification_number: str = None, **kwargs):
    """
    Verify professional certifications against issuing body databases using Computer Use.
    
    Args:
        certification_name: Certification name (e.g., 'AWS Solutions Architect', 'CPA')
        candidate_name: Certificate holder's name
        issuing_body: Organization that issued certification
        certification_number: Certificate number/ID if available
        
    Returns:
        dict: Certification validity, status, and expiry dates
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.verify_certification(
        certification_name=certification_name,
        candidate_name=candidate_name,
        issuing_body=issuing_body,
        certification_number=certification_number,
        **kwargs
    )


# ============================================================================
# CRIMINAL BACKGROUND CHECK TOOLS
# ============================================================================

def check_criminal_records_public(full_name: str, date_of_birth: str, state_province: str, country: str, **kwargs):
    """
    Search public criminal records databases using Computer Use.
    
    Args:
        full_name: Full legal name of person
        date_of_birth: Date of birth (YYYY-MM-DD) for disambiguation
        state_province: State/Province for targeted search
        country: Country (USA/Australia/UK/Canada)
        
    Returns:
        dict: Criminal records, sex offender registry, pending cases, risk level
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.check_criminal_records_public(
        full_name=full_name,
        date_of_birth=date_of_birth,
        state_province=state_province,
        country=country,
        **kwargs
    )


def check_court_records(full_name: str, state_province: str, country: str, case_type: str = "both", **kwargs):
    """
    Search public court records for civil and criminal cases using Computer Use.
    
    Args:
        full_name: Full legal name
        state_province: State/Province jurisdiction
        country: Country for court system
        case_type: criminal/civil/both
        
    Returns:
        dict: Criminal cases, civil cases, judgments, active litigation
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.check_court_records(
        full_name=full_name,
        state_province=state_province,
        country=country,
        case_type=case_type,
        **kwargs
    )


def check_sex_offender_registry(full_name: str, state_province: str, country: str, **kwargs):
    """
    Check national and state sex offender registries (FREE).
    
    Args:
        full_name: Full legal name
        state_province: State/Province to search
        country: Country (USA/Australia/UK)
        
    Returns:
        dict: Registry check results with risk level (Clear/Critical)
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.check_sex_offender_registry(
        full_name=full_name,
        state_province=state_province,
        country=country,
        **kwargs
    )


def check_professional_sanctions(full_name: str, profession: str, state_province: str, 
                                 country: str, license_number: str = None, **kwargs):
    """
    Check for professional sanctions and disciplinary actions using Computer Use.
    
    Args:
        full_name: Professional's full name
        profession: Profession (medical/legal/finance/engineering/etc.)
        state_province: State/Province of license
        country: Country
        license_number: License number if known
        
    Returns:
        dict: Sanctions, disciplinary actions, license status, ethics violations
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.check_professional_sanctions(
        full_name=full_name,
        profession=profession,
        state_province=state_province,
        country=country,
        license_number=license_number,
        **kwargs
    )


def check_bankruptcy_records(full_name: str, state_province: str, country: str, **kwargs):
    """
    Search federal and state bankruptcy court records using Computer Use.
    
    Args:
        full_name: Full legal name
        state_province: State/Province
        country: Country
        
    Returns:
        dict: Bankruptcy filings, discharge status, debt amounts, creditors
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.check_bankruptcy_records(
        full_name=full_name,
        state_province=state_province,
        country=country,
        **kwargs
    )


def check_terrorist_watchlist(full_name: str, date_of_birth: str, nationality: str, **kwargs):
    """
    Check international terrorist watchlists and sanctions lists (FREE).
    
    Args:
        full_name: Full legal name
        date_of_birth: Date of birth (YYYY-MM-DD)
        nationality: Country of citizenship
        
    Returns:
        dict: Watchlist matches, sanction lists (OFAC/UN/EU/Interpol), PEP status
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.check_terrorist_watchlist(
        full_name=full_name,
        date_of_birth=date_of_birth,
        nationality=nationality,
        **kwargs
    )


def check_interpol_red_notices(full_name: str, nationality: str = None, **kwargs):
    """
    Check Interpol Red Notices database for international arrest warrants (FREE).
    
    Args:
        full_name: Full legal name
        nationality: Nationality if known
        
    Returns:
        dict: Red notice status, charges, issuing country, warrant status
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.check_interpol_red_notices(
        full_name=full_name,
        nationality=nationality,
        **kwargs
    )


def verify_identity_documents(document_image_path: str, document_type: str, 
                              expected_name: str, expected_dob: str, **kwargs):
    """
    Verify identity documents using Computer Use with OCR and authentication.
    
    Args:
        document_image_path: Path to document image file
        document_type: passport/drivers_license/national_id
        expected_name: Expected name for cross-check
        expected_dob: Expected date of birth (YYYY-MM-DD)
        
    Returns:
        dict: Document validity, extracted data, forgery indicators, confidence score
    """
    if not HAS_COMPUTER_USE:
        return {
            'success': False,
            'error': 'Computer Use verification not available. Requires Anthropic API + Docker.'
        }
    
    return computer_use_verification.verify_identity_documents(
        document_image_path=document_image_path,
        document_type=document_type,
        expected_name=expected_name,
        expected_dob=expected_dob,
        **kwargs
    )


def comprehensive_background_check(full_name: str, date_of_birth: str, state_province: str, 
                                  country: str, profession: str = None, check_level: str = "standard", **kwargs):
    """
    Run comprehensive background check combining all criminal/financial/identity checks.
    
    Args:
        full_name: Full legal name
        date_of_birth: Date of birth (YYYY-MM-DD)
        state_province: State/Province of residence
        country: Country
        profession: Profession for targeted checks
        check_level: basic/standard/comprehensive
        
    Returns:
        dict: Overall risk score, all check results, red flags, comprehensive report
    """
    if not HAS_CORE:
        return {'success': False, 'error': 'verification_core module not available'}
    
    return verification_core.comprehensive_background_check(
        full_name=full_name,
        date_of_birth=date_of_birth,
        state_province=state_province,
        country=country,
        profession=profession,
        check_level=check_level,
        **kwargs
    )


logger.info("[VERIFICATION] Wrapper module loaded - 34 tools registered")

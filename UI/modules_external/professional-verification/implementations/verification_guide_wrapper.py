"""
Professional Verification Guide Wrapper
========================================

Provides comprehensive guides and instructions for using the professional verification module.

CREATED: December 18, 2025
"""

import logging

logger = logging.getLogger(__name__)


def professional_verification_guide(topic: str = "overview", **kwargs):
    """
    Get comprehensive guide for professional verification workflows.
    
    Args:
        topic: Guide topic (overview, quickstart, workflows, etc.)
        
    Returns:
        dict: Guide content with instructions and examples
    """
    
    guides = {
        "overview": _get_overview_guide(),
        "quickstart": _get_quickstart_guide(),
        "workflows": _get_workflows_guide(),
        "resume_verification": _get_resume_verification_guide(),
        "github_verification": _get_github_verification_guide(),
        "company_verification": _get_company_verification_guide(),
        "criminal_checks": _get_criminal_checks_guide(),
        "credential_verification": _get_credential_verification_guide(),
        "risk_assessment": _get_risk_assessment_guide(),
        "legal_compliance": _get_legal_compliance_guide(),
        "industry_specific": _get_industry_specific_guide(),
        "all_tools": _get_all_tools_guide()
    }
    
    if topic not in guides:
        return {
            'success': False,
            'error': f'Invalid topic. Available: {", ".join(guides.keys())}'
        }
    
    guide_data = guides[topic]
    
    return {
        'success': True,
        'topic': topic,
        'guide_content': guide_data['content'],
        'related_tools': guide_data.get('related_tools', []),
        'next_steps': guide_data.get('next_steps', []),
        'examples': guide_data.get('examples', [])
    }


def _get_overview_guide():
    """Overview of the professional verification module."""
    return {
        'content': """
# Professional Verification Module - Overview

## What This Module Does

The Professional Verification Module provides **34 tools** for comprehensive background checking and credential verification across ANY profession. It combines resume analysis, online presence verification, company legitimacy checks, professional credential validation, and criminal background screening.

## Core Capabilities

### 1. Resume & Skills Analysis (3 tools)
- Parse resumes (PDF, DOCX, TXT) with AI detection
- Extract contact information (emails, phones, social media)
- Match candidate skills against job requirements

### 2. GitHub Verification (6 tools)
- Verify GitHub profiles and activity
- Analyze code quality and contribution patterns
- Detect fake commits or contribution padding
- Cross-reference GitHub history with resume claims
- Verify organization memberships

### 3. Company Legitimacy (5 tools)
- Check domain age and registration (WHOIS)
- Search historical website snapshots (Wayback Machine)
- Verify email deliverability
- Fetch company data (employee count, industry)
- Search social media presence

### 4. Social Media & OSINT (4 tools)
- LinkedIn profile search and extraction
- Cross-platform timeline analysis
- Detect fake social media accounts
- Advanced Google search (Google Dorking)

### 5. Professional Credentials (3 tools)
- Verify professional licenses (Medical, Legal, Finance, Engineering)
- Check university degrees and accreditation
- Validate professional certifications (AWS, CPA, etc.)

### 6. Criminal Background Checks (9 tools)
- Public criminal records search
- Court records (civil and criminal)
- Sex offender registry checks
- Professional sanctions and disciplinary actions
- Bankruptcy records
- Terrorist watchlist screening
- Interpol Red Notices
- Identity document verification
- Comprehensive background check (all-in-one)

### 7. Analysis & Reporting (5 tools)
- Data breach exposure checks
- Build unified verification timeline
- Calculate overall risk score (0-100)
- Username search across 300+ platforms (Sherlock)
- Comprehensive digital footprint analysis

## When to Use This Module

**ALWAYS USE for:**
- Pre-employment screening (any role, any industry)
- Contractor/vendor vetting
- Partner/investor due diligence
- Tenant screening
- Board member appointments
- Volunteer background checks (especially for vulnerable populations)

**CRITICAL FOR:**
- Healthcare workers (MANDATORY sex offender checks)
- Education sector (MANDATORY sex offender checks)
- Finance/Banking (MANDATORY terrorist watchlist checks for AML)
- Government/Defense (comprehensive security clearance)
- Childcare providers (multiple criminal checks required)

## How to Use This Module

### Step 1: Call the Guide
```python
professional_verification_guide(topic='quickstart')
```

### Step 2: Follow the Workflow
Each guide provides:
- Which tools to call in what order
- How to interpret results
- Risk assessment criteria
- Legal compliance requirements
- Next action recommendations

### Step 3: Execute Verification
Use the tools in sequence following the industry-specific workflow.

## AI Agent Instructions

**CRITICAL: Read tool results carefully and provide INTERPRETATION**

When using verification tools:

1. **Execute the tool** - Get actual data
2. **Analyze the results** - Don't just show raw data
3. **Assess the risk** - Explain what findings mean
4. **Provide recommendations** - Clear next steps

**Example BAD response:**
"Tool returned: criminal_records: 2, sex_offender_registry: false"

**Example GOOD response:**
"âš ï¸ **2 criminal records found:**
- 2018: Misdemeanor DUI (7 years ago, single incident)
- 2023: Traffic violation (minor)

âœ… **Sex offender registry: CLEAR**

**Risk Assessment:** LOW
- Older DUI is concerning but isolated incident
- No pattern of criminal behavior
- Not disqualifying for non-driving roles
- May require discussion for roles involving company vehicles

**Recommendation:** 
- Proceed with interview
- Discuss DUI if role involves driving
- Consider role-specific risk tolerance"

## Tool Categories by Credential Requirement

**FREE Tools (No API keys needed):**
- Resume parsing
- Contact extraction
- Skills matching
- Domain age checks
- Wayback Machine searches
- Data breach checks
- Sex offender registry
- Terrorist watchlist
- Interpol notices
- OSINT tools

**Requires GitHub Token:**
- GitHub profile verification
- Code quality analysis
- Commit authenticity checks

**Requires API Keys:**
- Email deliverability (Hunter.io - FREE tier: 50/month)
- Company data (Clearbit - FREE tier: 100/month)

**Requires Computer Use (Anthropic API + Docker):**
- Criminal records search
- Court records
- LinkedIn search
- Professional sanctions
- Bankruptcy records
- Credential registry verification
- Education verification
- Certification verification
- Identity document verification

## Quick Reference

**For Resume Screening:**
→ Call: `professional_verification_guide(topic='resume_verification')`

**For Tech Roles:**
→ Call: `professional_verification_guide(topic='github_verification')`

**For Criminal Checks:**
→ Call: `professional_verification_guide(topic='criminal_checks')`

**For Healthcare/Education:**
→ Call: `professional_verification_guide(topic='industry_specific')`

## Next Steps

1. Review quickstart guide: `professional_verification_guide(topic='quickstart')`
2. Understand risk assessment: `professional_verification_guide(topic='risk_assessment')`
3. Learn legal requirements: `professional_verification_guide(topic='legal_compliance')`
4. See all tools: `professional_verification_guide(topic='all_tools')`
""",
        'related_tools': [
            'professional_verification_guide',
            'comprehensive_background_check',
            'calculate_verification_risk_score'
        ],
        'next_steps': [
            'Call professional_verification_guide(topic="quickstart") for 5-minute workflow',
            'Call professional_verification_guide(topic="industry_specific") for role-specific guidance',
            'Review legal requirements with topic="legal_compliance"'
        ],
        'examples': []
    }


def _get_quickstart_guide():
    """5-minute quickstart workflow."""
    return {
        'content': """
# Professional Verification - 5-Minute Quickstart

## Workflow for Standard Pre-Employment Screening

### STEP 1: Resume Analysis (1 minute)
```python
# Parse resume
resume_data = parse_resume(
    file_path='/uploads/john_doe_resume.pdf',
    detect_ai_content=True
)

# Extract contact info
contacts = extract_contact_info(
    resume_text=resume_data['raw_text']
)

# Match skills
skills_match = analyze_skills_match(
    resume_skills=resume_data['skills'],
    required_skills=['Python', 'SQL', 'AWS', 'Docker']
)
```

**What to look for:**
- âœ… AI detection score < 30% (likely human-written)
- âœ… Skills match > 60% (meets minimum requirements)
- âš ï¸ AI score > 70% = AI-generated resume (discuss with candidate)
- 🚨 Skills match < 40% = underqualified

### STEP 2: Company Verification (1 minute)
```python
# Check current employer legitimacy
domain_check = check_domain_age(
    domain='currentcompany.com'
)

wayback_check = check_wayback_history(
    url='https://currentcompany.com',
    date_from='2020-01-01',
    date_to='2025-12-18'
)
```

**What to look for:**
- âœ… Domain age > 2 years (established company)
- âœ… Wayback snapshots during employment period (company existed)
- âš ï¸ Domain < 6 months old (new/potentially fake company)
- 🚨 No Wayback snapshots during claimed employment = RED FLAG

### STEP 3: Online Presence Check (1 minute)
```python
# GitHub for tech roles
github_profile = verify_github_profile(
    github_username='johndoe',
    check_contributions=True
)

# LinkedIn search (Computer Use)
linkedin_data = search_linkedin_profile(
    full_name='John Doe',
    company_name='CurrentCo',
    location='San Francisco'
)
```

**What to look for:**
- âœ… GitHub activity matches resume dates
- âœ… LinkedIn history consistent with resume
- âš ï¸ No online presence = investigate further
- 🚨 Conflicting dates between platforms = RED FLAG

### STEP 4: Criminal Checks (2 minutes)
```python
# Sex offender registry (MANDATORY for education/healthcare)
sex_offender = check_sex_offender_registry(
    full_name='John Doe',
    state_province='California',
    country='USA'
)

# Criminal records
criminal_records = check_criminal_records_public(
    full_name='John Doe',
    date_of_birth='1985-03-15',
    state_province='California',
    country='USA'
)

# Terrorist watchlist (MANDATORY for finance/government)
watchlist = check_terrorist_watchlist(
    full_name='John Doe',
    date_of_birth='1985-03-15',
    nationality='USA'
)
```

**What to look for:**
- âœ… All checks clear = proceed
- 🚨 Sex offender registry hit = AUTOMATIC DISQUALIFICATION
- 🚨 Terrorist watchlist hit = AUTOMATIC DISQUALIFICATION
- âš ï¸ Old criminal records = assess based on role (see risk assessment guide)

### STEP 5: Calculate Risk Score
```python
risk_score = calculate_verification_risk_score(
    verification_results={
        'resume': resume_data,
        'contacts': contacts,
        'skills': skills_match,
        'domain': domain_check,
        'wayback': wayback_check,
        'github': github_profile,
        'linkedin': linkedin_data,
        'sex_offender': sex_offender,
        'criminal': criminal_records,
        'watchlist': watchlist
    }
)
```

**Risk Score Interpretation:**
- **0-20 (Clear):** âœ… Proceed with hiring
- **21-40 (Low):** âš ï¸ Minor issues, discuss with candidate
- **41-60 (Medium):** âš ï¸ Enhanced verification needed
- **61-80 (High):** 🚨 Likely disqualification
- **81-100 (Critical):** 🚨 Automatic disqualification

## AI Agent Response Template

```markdown
# Background Verification Report: [Candidate Name]

## âœ… CLEARED CHECKS (X/10)
- Resume analysis: No AI content detected
- Skills match: 75% match with requirements
- Company verification: ABC Corp domain established 2015
- GitHub profile: Active with quality contributions
- Sex offender registry: CLEAR
- Terrorist watchlist: CLEAR

## âš ï¸ ISSUES FOUND (X items)
1. **Criminal Record - Misdemeanor (2020)**
   - Charge: Public intoxication
   - Status: Dismissed
   - Risk: LOW (minor, old, dismissed)

2. **Employment Gap**
   - Gap: 6 months (Jan-Jun 2022)
   - LinkedIn shows "Career break"
   - Risk: LOW (explained on profile)

## 🚨 RED FLAGS (X items)
(None found)

## OVERALL RISK SCORE: 25/100 (LOW)

**Risk Level:** Low  
**Recommendation:** âœ… Proceed to interview  
**Conditions:** 
- Discuss 2020 incident if role-sensitive
- Verify career break explanation

**Next Steps:**
1. Schedule interview
2. Reference check with previous employer
3. Final decision after interview
```

## Common Patterns

**Tech Candidate:**
1. Resume + GitHub + LinkedIn
2. Skills match
3. Criminal checks
4. Risk assessment

**Healthcare Worker:**
1. Resume + credentials
2. **MANDATORY:** Sex offender check
3. Professional sanctions check
4. License verification
5. Criminal checks
6. Risk assessment

**Finance Role:**
1. Resume + LinkedIn
2. **MANDATORY:** Terrorist watchlist
3. Bankruptcy check
4. Criminal checks
5. Professional sanctions (if CPA/CFA)
6. Risk assessment

**General Office:**
1. Resume analysis
2. Company verification
3. Basic criminal checks
4. Risk assessment
""",
        'related_tools': [
            'parse_resume',
            'check_sex_offender_registry',
            'check_criminal_records_public',
            'calculate_verification_risk_score'
        ],
        'next_steps': [
            'Execute workflow for your specific industry',
            'Review risk_assessment guide for scoring criteria',
            'Check legal_compliance guide for FCRA/GDPR requirements'
        ],
        'examples': [
            {
                'scenario': 'Tech startup hiring software engineer',
                'tools': ['parse_resume', 'verify_github_profile', 'check_criminal_records_public'],
                'outcome': 'Risk score 18 - CLEAR to hire'
            }
        ]
    }


def _get_criminal_checks_guide():
    """Detailed criminal background check guide."""
    return {
        'content': """
# Criminal Background Checks - Complete Guide

## 9 Criminal Check Tools Available

### 1. check_sex_offender_registry (FREE) - MANDATORY FOR SOME ROLES

**When to use:**
- âœ… MANDATORY for education sector
- âœ… MANDATORY for healthcare (working with vulnerable adults)
- âœ… MANDATORY for childcare providers
- âœ… MANDATORY for elder care facilities
- âœ… MANDATORY for coaching/youth programs

**How to interpret:**
- `found_on_registry: false` âœ… CLEAR - Proceed
- `found_on_registry: true` 🚨 CRITICAL - AUTOMATIC DISQUALIFICATION

**No exceptions policy:**
Anyone on sex offender registry is automatically disqualified for roles involving:
- Children (any age)
- Vulnerable adults
- Healthcare settings
- Educational institutions

**AI Agent Response Example:**
```markdown
âœ… **Sex Offender Registry: CLEAR**
Candidate not found on national or California state registries.
Safe to proceed with roles involving vulnerable populations.
```

OR

```markdown
🚨 **CRITICAL: Sex Offender Registry HIT**
Candidate found on registry with offense date 2015.
**AUTOMATIC DISQUALIFICATION** for this role.
Cannot proceed with hiring process.
Legal requirement: Cannot employ in education/childcare/healthcare settings.
```

### 2. check_criminal_records_public (Computer Use)

**What it searches:**
- Federal criminal records (PACER)
- State criminal records (50 states)
- County court records
- Pending cases
- Conviction history

**How to interpret:**
```python
result = {
    'records_found': True,
    'criminal_records': [
        {
            'date': '2018-05-12',
            'charge': 'DUI',
            'disposition': 'Convicted',
            'sentence': 'Probation 12 months (completed)'
        }
    ],
    'risk_level': 'Low'
}
```

**Risk Assessment Matrix:**

| Offense Type | < 1 year | 1-3 years | 3-7 years | > 7 years | Risk Level |
|--------------|----------|-----------|-----------|-----------|------------|
| Violent crime | 🚨 High | 🚨 High | âš ï¸ Medium | âš ï¸ Medium | Case-by-case |
| Sex offense | 🚨 Critical | 🚨 Critical | 🚨 Critical | 🚨 Critical | Disqualify |
| Theft/Fraud | 🚨 High | âš ï¸ Medium | âš ï¸ Low | âœ… Low | Role-dependent |
| Drug offense | âš ï¸ Medium | âš ï¸ Low | âœ… Low | âœ… Clear | Usually OK |
| DUI | âš ï¸ Medium | âš ï¸ Low | âœ… Low | âœ… Clear | Driving roles only |
| Misdemeanor | âš ï¸ Low | âœ… Low | âœ… Clear | âœ… Clear | Usually OK |

**AI Agent Response Template:**
```markdown
âš ï¸ **Criminal Record Found: 1 offense**

**Offense:** DUI (Driving Under Influence)  
**Date:** May 12, 2018 (7 years ago)  
**Disposition:** Convicted  
**Sentence:** 12 months probation (completed)  
**Subsequent offenses:** None  

**Risk Assessment:** LOW
- Single isolated incident
- Occurred 7 years ago
- Probation successfully completed
- No pattern of criminal behavior
- Not role-disqualifying for office positions

**Recommendations:**
âœ… Proceed with interview
âœ… Discuss incident if role involves company vehicle operation
âš ï¸ May require additional review for driving-intensive roles
âœ… Generally acceptable for non-driving positions
```

### 3. check_terrorist_watchlist (FREE) - MANDATORY FOR FINANCE/GOVERNMENT

**When to use:**
- âœ… MANDATORY for banking/finance (AML compliance)
- âœ… MANDATORY for government positions
- âœ… MANDATORY for defense contractors
- âœ… MANDATORY for aviation security
- âœ… Recommended for any sensitive role

**What it checks:**
- OFAC (Office of Foreign Assets Control)
- UN Sanctions Lists
- EU Sanctions Lists
- Interpol Watchlists
- PEP (Politically Exposed Person) status

**How to interpret:**
```python
result = {
    'found_on_watchlist': False,
    'pep_status': True,  # Family member of politician
    'risk_level': 'Medium'
}
```

**Risk Matrix:**
- `found_on_watchlist: true` 🚨 CRITICAL - CANNOT PROCEED (legal prohibition)
- `pep_status: true` âš ï¸ MEDIUM - Enhanced due diligence required
- `both false` âœ… CLEAR - Proceed normally

**AI Agent Response for PEP:**
```markdown
âš ï¸ **Politically Exposed Person (PEP) Identified**

**Status:** Family member of state legislator (California)  
**Watchlist:** CLEAR (not on any sanctions lists)  

**Risk Assessment:** MEDIUM (Enhanced Due Diligence Required)

**Legal Requirements (AML Compliance):**
1. Enhanced background verification required
2. Source of wealth documentation needed
3. Ongoing monitoring for duration of employment
4. Report to compliance officer
5. Senior management approval for hire

**Recommendation:**
âœ… Can proceed with hiring IF:
- Enhanced DD completed
- Source of wealth verified
- Compliance officer approves
- Ongoing monitoring established

⚠️ Additional compliance costs: ~$500-1000/year for monitoring
```

### 4. check_court_records (Computer Use)

**Use for:**
- Civil lawsuits
- Financial judgments/liens
- Ongoing litigation
- Legal history beyond criminal

**Key for roles involving:**
- Financial responsibilities
- Fiduciary duties
- Contract management
- Legal compliance

### 5. check_professional_sanctions (Computer Use)

**Critical for licensed professionals:**
- Medical doctors, nurses (state medical boards)
- Lawyers (bar associations)
- CPAs, CFAs (financial licensing boards)
- Engineers (PE licenses)
- Real estate agents
- Pharmacists, psychologists

**What it finds:**
- Formal complaints
- License suspensions/revocations
- Malpractice claims
- Ethics violations
- Disciplinary actions

**Automatic disqualifiers:**
- Active license suspension
- License revocation
- Pending serious ethics charges

### 6. check_bankruptcy_records (Computer Use)

**When to check:**
- Finance positions
- Accounting roles
- Executive management
- Fiduciary responsibilities
- Roles with financial access

**How to interpret:**
- Recent bankruptcy (< 2 years) âš ï¸ HIGH risk for financial roles
- Old bankruptcy (> 7 years) âœ… LOW risk
- Multiple bankruptcies 🚨 HIGH risk pattern
- No bankruptcy âœ… CLEAR

### 7. check_interpol_red_notices (FREE)

**For international hires:**
- Active Red Notice 🚨 CRITICAL - International arrest warrant
- No Red Notice âœ… CLEAR

### 8. verify_identity_documents (Computer Use)

**Use for:**
- Remote hires
- International candidates
- Identity verification
- Forgery detection

### 9. comprehensive_background_check (All-in-One)

**Best for:**
- Senior positions
- Sensitive roles
- Complete screening
- Time-constrained checks

**Combines all checks above into single execution with unified risk score.**

## AI Agent Instructions for Criminal Checks

### Rule 1: ALWAYS Interpret, Don't Just Report

**BAD:**
"Criminal check returned 1 record."

**GOOD:**
"Criminal record found: 2018 DUI (7 years ago, completed probation). Risk: LOW for office roles. Not disqualifying."

### Rule 2: Use Risk Matrix Above

Don't guess - follow the matrix for consistent risk assessment.

### Rule 3: Provide Clear Recommendations

Every criminal check result must include:
1. What was found (be specific)
2. Risk level with justification
3. Whether it's disqualifying
4. Role-specific considerations
5. Next steps (proceed/investigate/disqualify)

### Rule 4: Flag MANDATORY Checks

If user hasn't requested sex offender check for education/healthcare role:
"âš ï¸ WARNING: This is an education role. Sex offender registry check is MANDATORY by law. Should I run it?"

### Rule 5: Explain Legal Requirements

When watchlist/PEP found in finance:
"âš ï¸ AML Compliance Required: Enhanced due diligence mandatory under Bank Secrecy Act..."

## Legal Compliance Notes

**FCRA (USA):**
- Written authorization required
- Adverse action notice if rejected
- Must provide copy of report
- Dispute resolution process

**GDPR (EU):**
- Data minimization
- Purpose limitation  
- Right to erasure
- Consent required

**State Laws:**
- Ban-the-box laws (delay criminal check)
- Look-back periods (7-10 years max)
- Offense restrictions (can't use for certain crimes)
""",
        'related_tools': [
            'check_sex_offender_registry',
            'check_criminal_records_public',
            'check_terrorist_watchlist',
            'check_professional_sanctions',
            'comprehensive_background_check'
        ],
        'next_steps': [
            'Review industry_specific guide for your sector',
            'Check legal_compliance guide for jurisdiction',
            'Use comprehensive_background_check for complete screening'
        ]
    }


def _get_risk_assessment_guide():
    """Risk scoring and decision-making framework."""
    return {
        'content': """
# Risk Assessment Framework

## Overall Risk Score Calculation (0-100 Scale)

### Score Interpretation

| Score Range | Risk Level | Decision | Action Required |
|-------------|------------|----------|-----------------|
| 0-20 | **Clear** | âœ… PROCEED | Standard hiring process |
| 21-40 | **Low** | âš ï¸ DISCUSS | Review issues with candidate |
| 41-60 | **Medium** | âš ï¸ ENHANCED | Additional verification needed |
| 61-80 | **High** | 🚨 LIKELY REJECT | Strong justification to proceed |
| 81-100 | **Critical** | 🚨 REJECT | Automatic disqualification |

### Scoring Components

```
Total Risk Score = (weighted average of):

1. Resume Issues (20%)
   - AI-generated content: +15 points
   - Skills mismatch (< 40%): +10 points
   - Missing contact info: +5 points

2. Company Verification (15%)
   - Fake company detected: +20 points
   - New domain (< 6 months): +15 points
   - No wayback history during employment: +15 points
   - Legitimate company: 0 points

3. Online Presence (15%)
   - Conflicting timelines: +15 points
   - No digital footprint: +10 points
   - Fake social media: +15 points
   - Consistent presence: 0 points

4. Criminal History (30%) - HIGHEST WEIGHT
   - Sex offender registry: +100 points (auto-critical)
   - Terrorist watchlist: +100 points (auto-critical)
   - Violent crime (< 3 years): +40 points
   - Violent crime (> 7 years): +15 points
   - Theft/Fraud (< 3 years): +30 points
   - Theft/Fraud (> 7 years): +10 points
   - DUI (< 3 years): +20 points
   - DUI (> 7 years): +5 points
   - Multiple offenses: +20 points per additional

5. Professional Credentials (10%)
   - License suspended/revoked: +50 points
   - Disciplinary actions: +25 points
   - Unverifiable credentials: +15 points
   - Valid credentials: 0 points

6. Financial Issues (10%)
   - Recent bankruptcy (< 2 years): +25 points
   - Multiple bankruptcies: +40 points
   - Old bankruptcy (> 7 years): +5 points
   - Clean financial history: 0 points
```

### Example Calculations

**Example 1: Clean Candidate**
```
Resume: 0 (no issues)
Company: 0 (legitimate)
Online: 0 (consistent)
Criminal: 0 (clear)
Credentials: 0 (valid)
Financial: 0 (clean)
─────────────────
Total: 0/100 (CLEAR)
Decision: âœ… Proceed with hiring
```

**Example 2: Minor Issues**
```
Resume: 5 (minor formatting)
Company: 0 (legitimate)
Online: 10 (no LinkedIn found)
Criminal: 5 (old DUI, 8 years ago)
Credentials: 0 (valid)
Financial: 0 (clean)
─────────────────
Total: 20/100 (CLEAR)
Decision: âœ… Proceed, discuss LinkedIn absence
```

**Example 3: Moderate Concerns**
```
Resume: 15 (AI content detected)
Company: 15 (new company, 4 months old)
Online: 15 (conflicting LinkedIn dates)
Criminal: 10 (misdemeanor, 5 years ago)
Credentials: 0 (valid)
Financial: 0 (clean)
─────────────────
Total: 55/100 (MEDIUM)
Decision: âš ï¸ Enhanced verification required
Actions: Verify employment, discuss timeline gaps
```

**Example 4: High Risk**
```
Resume: 10 (skills mismatch)
Company: 20 (fake company detected)
Online: 15 (no digital footprint)
Criminal: 30 (theft conviction, 2 years ago)
Credentials: 15 (unverifiable degree)
Financial: 0 (clean)
─────────────────
Total: 90/100 (CRITICAL)
Decision: 🚨 REJECT - Multiple red flags
```

## Role-Specific Risk Tolerance

### High-Security Roles (Finance, Government, Defense)
**Acceptable Risk: 0-20 only**
- Zero tolerance for criminal history
- Full credentials required
- Enhanced background check mandatory

### Healthcare (Working with Vulnerable Populations)
**Acceptable Risk: 0-30**
- MUST pass sex offender check
- Professional license verification required
- Some non-violent history acceptable

### General Office/Tech Roles
**Acceptable Risk: 0-50**
- Minor criminal history acceptable
- Focus on skill match and company verification
- Old offenses (> 7 years) typically OK

### Manual Labor/Warehouse
**Acceptable Risk: 0-60**
- Higher tolerance for old offenses
- Focus on work ethic and reliability
- Criminal history less critical (role-dependent)

## AI Agent Response Template

```markdown
# Risk Assessment: [Candidate Name]

## Risk Score: XX/100
**Risk Level:** [Clear/Low/Medium/High/Critical]  
**Decision:** [Proceed/Review/Enhanced/Reject]

### Score Breakdown

**Resume Analysis: X points**
- [Issue or âœ… No issues]

**Company Verification: X points**
- [Issue or âœ… Legitimate company]

**Online Presence: X points**
- [Issue or âœ… Consistent profiles]

**Criminal History: X points** (Highest Weight)
- [Details or âœ… No criminal history]

**Professional Credentials: X points**
- [Issue or âœ… Valid credentials]

**Financial History: X points**
- [Issue or âœ… Clean history]

### Red Flags (Priority Order)
1. [Most critical issue]
2. [Next critical issue]
...

### Mitigating Factors
- [Positive findings that reduce risk]
- [Explanations that contextualize issues]

### Role-Specific Considerations
**Position:** [Job Title]  
**Acceptable Risk Level:** 0-XX  
**This Candidate:** XX/100  
**Status:** [Within/Exceeds] acceptable range

## Final Recommendation

**Decision:** [âœ… Proceed / âš ï¸ Conditional / 🚨 Reject]

**Justification:**
[Clear explanation of decision based on risk score, role requirements, and specific findings]

**Conditions (if applicable):**
1. [Required condition 1]
2. [Required condition 2]

**Next Steps:**
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]
```

## Common Decision Scenarios

### Scenario 1: Old Criminal Record
**Finding:** DUI from 2015 (10 years ago), no other offenses  
**Score Impact:** +5 points  
**Decision:** âœ… Proceed for non-driving roles

### Scenario 2: Employment Gap
**Finding:** 12-month gap in 2022  
**LinkedIn:** Shows "Career sabbatical"  
**Score Impact:** +5 points (explained)  
**Decision:** âœ… Proceed, verify during interview

### Scenario 3: Fake Company
**Finding:** Company domain 2 months old, no wayback history  
**Resume Claims:** Employed 2020-2024  
**Score Impact:** +35 points  
**Decision:** 🚨 High risk, investigate thoroughly

### Scenario 4: License Suspension
**Finding:** Medical license suspended 2023 for 6 months (now reinstated)  
**Score Impact:** +25-50 points depending on reason  
**Decision:** âš ï¸ Role-dependent, review suspension cause

## When to Override Risk Score

**Higher Risk Acceptable:**
- Candidate explained issues transparently
- Evidence of rehabilitation
- References strongly vouch for character
- Skills are exceptionally rare/valuable

**Lower Risk Still Concerning:**
- Pattern of dishonesty (even minor)
- Evasive about issues
- Multiple small red flags accumulating
- Role requires high trust
""",
        'related_tools': [
            'calculate_verification_risk_score',
            'comprehensive_background_check'
        ],
        'next_steps': [
            'Use calculate_verification_risk_score() for automated scoring',
            'Review legal_compliance for FCRA adverse action requirements',
            'Check industry_specific for role-based risk tolerance'
        ]
    }


def _get_all_tools_guide():
    """Complete reference of all 34 tools."""
    return {
        'content': """
# Complete Tool Reference - 34 Tools

## Resume Parsing & Analysis (3 tools)

### parse_resume
Parse resume/CV documents (PDF, DOCX, TXT) and extract structured data.
- **Features:** Name, contact info, skills, education, experience, certifications, AI content detection
- **Cost:** FREE
- **Returns:** Structured resume data with AI detection score

### extract_contact_info
Extract all contact information from resume text using regex patterns.
- **Features:** Emails, phones, LinkedIn, GitHub, personal websites
- **Cost:** FREE
- **Returns:** Categorized contact information

### analyze_skills_match
Compare resume skills against job requirements and calculate match percentage.
- **Features:** Matched skills, missing skills, bonus skills, recommendations
- **Cost:** FREE
- **Returns:** Match percentage (0-100%) with detailed breakdown

## GitHub Verification (6 tools)

### verify_github_profile
Verify GitHub profile and extract activity metrics.
- **Requirements:** GitHub token (FREE tier: 5000 requests/hour)
- **Features:** Profile data, contribution history, languages, repositories
- **Returns:** Activity score (0-100) with detailed metrics

### analyze_github_code_quality
Analyze code quality metrics from GitHub repositories.
- **Requirements:** GitHub token
- **Features:** Documentation, tests, commit messages, code reviews
- **Returns:** Quality score (0-100) with red flags

### cross_reference_github_resume
Cross-reference GitHub activity timeline with resume work history.
- **Requirements:** GitHub token
- **Features:** Timeline consistency check, gap detection
- **Returns:** Inconsistencies, suspicious gaps, risk score

### check_github_commit_authenticity
Analyze commit patterns to detect fake commits or contribution padding.
- **Requirements:** GitHub token
- **Features:** Bulk import detection, time anomalies, padding detection
- **Returns:** Authenticity score (0-100) with evidence

### verify_github_organization_membership
Verify claimed company affiliations via GitHub organization memberships.
- **Requirements:** GitHub token
- **Features:** Org membership verification, repository contributions
- **Returns:** Verified vs unverified claims

## Company Legitimacy (5 tools)

### check_domain_age
Check domain registration age using WHOIS lookup.
- **Cost:** FREE (rate-limited)
- **Features:** Creation date, age in days, registrar, risk flag
- **Returns:** Domain age and legitimacy indicators

### check_wayback_history
Check Internet Archive for historical website snapshots.
- **Cost:** FREE (unlimited)
- **Features:** Historical snapshots, content changes, existence verification
- **Returns:** Snapshots found during claimed employment period

### verify_email_deliverability
Verify email address exists and is deliverable.
- **Requirements:** Hunter.io API key (FREE tier: 50/month)
- **Features:** MX records, mailbox existence, disposable email detection
- **Returns:** Deliverability score (0-100)

### check_company_data
Fetch company information from Clearbit API.
- **Requirements:** Clearbit API key (FREE tier: 100/month)
- **Features:** Employee count, industry, location, social profiles
- **Returns:** Complete company profile

### search_company_social_media
Search for company presence on social media platforms.
- **Cost:** FREE
- **Features:** LinkedIn, Twitter, Facebook presence
- **Returns:** Social presence score (0-100)

## Social Media & OSINT (4 tools + Computer Use)

### search_linkedin_profile
Search LinkedIn for professional profile using Computer Use.
- **Requirements:** Computer Use (Anthropic API + Docker)
- **Features:** Work history, skills, endorsements, connections
- **Returns:** Complete profile data with screenshot evidence

### cross_platform_timeline
Build unified timeline from LinkedIn, GitHub, Twitter, resume.
- **Requirements:** Computer Use for LinkedIn
- **Features:** Consistency check, conflicting data detection, gap analysis
- **Returns:** Unified timeline with inconsistencies

### analyze_social_media_authenticity
Analyze social media profiles for signs of fake accounts.
- **Requirements:** Computer Use
- **Features:** Account age, engagement rate, bot indicators
- **Returns:** Authenticity score (0-100) with verdict

### google_dork_search
Perform advanced Google searches using Computer Use.
- **Requirements:** Computer Use
- **Features:** Publications, news articles, forum posts, mentions
- **Returns:** Online mentions with URLs and screenshots

## Professional Credentials (3 tools + Computer Use)

### verify_credential_registry
Verify professional credentials against official registries.
- **Requirements:** Computer Use
- **Supports:** Medical, Legal, Finance, Engineering, Nursing, Psychology, etc.
- **Returns:** Credential status, disciplinary actions, license validity

### check_education_credentials
Verify university degrees and education credentials.
- **Requirements:** Computer Use
- **Features:** Institution accreditation, diploma mill detection
- **Returns:** Verification confidence score

### verify_certification
Verify professional certifications (AWS, CPA, CFA, etc.).
- **Requirements:** Computer Use
- **Features:** Certification validity, expiry dates, issuing body verification
- **Returns:** Certification status with evidence

## Criminal Background Checks (9 tools)

### check_sex_offender_registry
Check national and state sex offender registries (USA, Australia, UK).
- **Cost:** FREE
- **MANDATORY FOR:** Education, healthcare, childcare, elder care
- **Returns:** Registry status (Clear/Critical)

### check_criminal_records_public
Search public criminal records databases using Computer Use.
- **Requirements:** Computer Use
- **Searches:** Court records, convictions, pending cases
- **Returns:** Criminal history with risk level

### check_court_records
Search federal, state, and county court systems.
- **Requirements:** Computer Use
- **Searches:** Criminal and civil cases, judgments, liens
- **Returns:** Complete case history

### check_terrorist_watchlist
Check international terrorist watchlists and sanctions lists.
- **Cost:** FREE
- **MANDATORY FOR:** Finance (AML), government, defense, aviation
- **Searches:** OFAC, UN, EU, Interpol, PEP lists
- **Returns:** Watchlist status, PEP status, risk level

### check_interpol_red_notices
Check Interpol Red Notices database for international arrest warrants.
- **Cost:** FREE
- **Returns:** Red notice status, charges, issuing country

### check_professional_sanctions
Check for professional disciplinary actions and sanctions.
- **Requirements:** Computer Use
- **Searches:** Medical boards, bar associations, CPA boards, etc.
- **Returns:** Sanctions, license status, malpractice claims

### check_bankruptcy_records
Search federal and state bankruptcy court records.
- **Requirements:** Computer Use
- **Searches:** Chapter 7, 11, 13 filings
- **Returns:** Bankruptcy history with financial risk score

### verify_identity_documents
Verify identity documents using OCR and authentication.
- **Requirements:** Computer Use
- **Supports:** Passports, driver's licenses, national IDs
- **Returns:** Document validity, forgery indicators, confidence score

### comprehensive_background_check
Run complete background check combining all checks above.
- **Requirements:** Computer Use for some checks
- **Levels:** Basic, Standard, Comprehensive
- **Returns:** Overall risk score (0-100), complete report, recommendations

## Analysis & Reporting (5 tools)

### check_data_breach_exposure
Check if email has been exposed in data breaches (Have I Been Pwned).
- **Cost:** FREE (unlimited)
- **Returns:** Breach count, breach details, risk level

### build_verification_timeline
Aggregate all verification data into chronological timeline.
- **Cost:** FREE
- **Features:** Gap detection, overlap detection, inconsistency identification
- **Returns:** Unified timeline with consistency score

### calculate_verification_risk_score
Calculate overall risk score (0-100) based on all verification findings.
- **Cost:** FREE
- **Returns:** Risk score, risk level, red flags, recommendations, comprehensive report

### run_osint_sherlock
Run Sherlock tool to find social media accounts across 300+ platforms.
- **Requirements:** Sherlock installed
- **Returns:** Platform matches, profile URLs

### analyze_digital_footprint
Comprehensive digital footprint analysis combining all OSINT data.
- **Cost:** FREE
- **Returns:** Footprint size, online presence map, privacy score, risk indicators

## Documentation (1 tool)

### professional_verification_guide
Get comprehensive guides and instructions (this tool!).
- **Topics:** overview, quickstart, workflows, criminal_checks, risk_assessment, legal_compliance, industry_specific, all_tools
- **Returns:** Formatted guide with examples and next steps
""",
        'related_tools': ['professional_verification_guide'],
        'next_steps': [
            'Review quickstart guide for workflows',
            'Check industry_specific for your sector',
            'Use comprehensive_background_check for complete screening'
        ]
    }


def _get_workflows_guide():
    """Common verification workflows by scenario."""
    return {'content': '', 'related_tools': [], 'next_steps': []}

def _get_resume_verification_guide():
    """Resume analysis workflow."""
    return {'content': '', 'related_tools': [], 'next_steps': []}

def _get_github_verification_guide():
    """GitHub verification workflow."""
    return {'content': '', 'related_tools': [], 'next_steps': []}

def _get_company_verification_guide():
    """Company legitimacy checking workflow."""
    return {'content': '', 'related_tools': [], 'next_steps': []}

def _get_credential_verification_guide():
    """Professional credential verification workflow."""
    return {'content': '', 'related_tools': [], 'next_steps': []}

def _get_legal_compliance_guide():
    """FCRA, GDPR, and legal compliance guide."""
    return {'content': '', 'related_tools': [], 'next_steps': []}

def _get_industry_specific_guide():
    """Industry-specific verification requirements."""
    return {'content': '', 'related_tools': [], 'next_steps': []}


logger.info("[VERIFICATION GUIDE] Guide wrapper module loaded")

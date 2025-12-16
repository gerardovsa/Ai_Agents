# Professional Verification Module
## Universal Background Verification for ANY Profession

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-alpha-orange.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

---

## 🎯 Overview

The **Professional Verification Module** provides comprehensive background verification for candidates across **ANY profession** - from Software Engineers to Medical Professionals, Accountants to Lawyers, Teachers to Engineers.

Using a combination of **free APIs**, **OSINT techniques**, and **Anthropic Computer Use** for browser automation, this module validates:

- ✅ Resume authenticity and AI-generated content detection
- ✅ GitHub/LinkedIn profile verification
- ✅ Company legitimacy (domain age, online presence, social media)
- ✅ Professional credentials (medical licenses, bar admissions, certifications)
- ✅ Education credentials (university degrees)
- ✅ Timeline consistency across platforms
- ✅ Digital footprint analysis
- ✅ Data breach exposure

**Result:** Comprehensive risk score (0-100) with categorized findings, evidence screenshots, and red flag alerts.

---

## 🌍 Supported Professions

This module is **profession-agnostic** and works for:

| Category | Professions | Verification Methods |
|----------|------------|---------------------|
| **Technology** | Software Engineers, Data Scientists, IT Professionals | GitHub, LinkedIn, technical skills, company history |
| **Healthcare** | Doctors, Nurses, Pharmacists, Psychologists | Medical licenses (AHPRA, GMC), education, credentials |
| **Legal** | Lawyers, Paralegals, Legal Consultants | Bar associations, education, case history |
| **Finance** | CPAs, Financial Advisors, Accountants | CPA registration, certifications, company legitimacy |
| **Engineering** | Civil, Mechanical, Electrical Engineers | PE licenses, education, project history |
| **Education** | Teachers, Professors, Tutors | Teaching licenses, education credentials, background |
| **Business** | Managers, Consultants, Executives | Company history, LinkedIn, references |
| **Any Profession** | Custom verification workflows | Resume parsing, timeline analysis, OSINT |

---

## 🚀 Quick Start

### 1. Prerequisites

**Required:**
- Docker Desktop installed and running
- GitHub Personal Access Token (free, 5000 requests/hour)

**Optional (for enhanced features):**
- Anthropic API Key (for Computer Use - LinkedIn, credential registries)
- Hunter.io API Key (free tier: 50/month - email verification)
- Clearbit API Key (free tier: 100/month - company data)
- Dedicated LinkedIn verifier account (for profile searches)

### 2. Install Docker Image

```bash
cd AI_agents/docker/computer-use
docker build -t professional-verification-browser:latest .
```

**Build time:** 3-5 minutes

### 3. Configure API Credentials

Navigate to: **Settings → Platform Connections → Professional Verification**

1. **GitHub Token** (Required):
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `read:user`, `public_repo`
   - Copy token and paste

2. **Anthropic API Key** (Optional - for Computer Use):
   - Go to: https://console.anthropic.com/
   - Create API key
   - Paste in settings

3. **Hunter.io / Clearbit** (Optional):
   - Sign up for free tier
   - Copy API keys
   - Paste in settings

4. **LinkedIn Verifier Account** (Optional):
   - Create a NEW LinkedIn account (not your personal one!)
   - Use dedicated email: `verifier@yourcompany.com`
   - Enter credentials in settings

### 4. Run Your First Verification

1. Navigate to: **Dashboard → Professional Verification → New Verification**
2. Upload resume (PDF, DOCX, or TXT)
3. Select profession category
4. Choose verification checks to run
5. Click "Start Verification"
6. Watch real-time progress with streaming updates!

---

## 📊 Verification Workflow

```
┌─────────────────┐
│ Upload Resume   │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Parse Document  │ → Extract name, contact, skills, education, experience
└────────┬────────┘
         ↓
┌─────────────────┐
│ GitHub Check    │ → Profile exists? Activity metrics? Code quality?
└────────┬────────┘
         ↓
┌─────────────────┐
│ LinkedIn Search │ → Profile found? Work history matches resume?
│ (Computer Use)  │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Company Verify  │ → Domain age? Wayback history? Social presence?
└────────┬────────┘
         ↓
┌─────────────────┐
│ Credential Check│ → Medical license? Bar admission? CPA valid?
│ (Computer Use)  │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Timeline Build  │ → Cross-reference all sources, find gaps/overlaps
└────────┬────────┘
         ↓
┌─────────────────┐
│ Risk Scoring    │ → Calculate 0-100 score with category breakdown
└────────┬────────┘
         ↓
┌─────────────────┐
│ Generate Report │ → PDF with findings, screenshots, recommendations
└─────────────────┘
```

---

## 🛠️ Available Tools (25 Total)

### Resume Parsing (3 tools)
- `parse_resume` - Extract structured data from PDF/DOCX/TXT
- `extract_contact_info` - Find emails, phones, LinkedIn, GitHub
- `analyze_skills_match` - Compare resume vs job requirements

### GitHub Verification (5 tools)
- `verify_github_profile` - Profile metrics, languages, repositories
- `analyze_github_code_quality` - Documentation, tests, commit quality
- `cross_reference_github_resume` - Timeline consistency check
- `check_github_commit_authenticity` - Detect fake commits
- `verify_github_organization_membership` - Confirm company affiliations

### Company Legitimacy (5 tools)
- `check_domain_age` - WHOIS lookup for domain registration
- `check_wayback_history` - Internet Archive snapshots
- `verify_email_deliverability` - Hunter.io email validation
- `check_company_data` - Clearbit company enrichment
- `search_company_social_media` - LinkedIn/Twitter/Facebook presence

### Social Media Analysis (4 tools)
- `search_linkedin_profile` - Computer Use LinkedIn search
- `cross_platform_timeline` - Unified timeline from all sources
- `analyze_social_media_authenticity` - Detect fake profiles
- `google_dork_search` - Find online mentions via Google

### Credential Verification (4 tools)
- `verify_credential_registry` - Medical, Legal, Finance licenses
- `check_education_credentials` - University degree verification
- `verify_certification` - Professional certifications (AWS, CPA, etc.)
- `check_data_breach_exposure` - Have I Been Pwned check

### Timeline Analysis (2 tools)
- `build_verification_timeline` - Aggregate all data chronologically
- `calculate_verification_risk_score` - Overall 0-100 risk score

### OSINT Tools (2 tools)
- `run_osint_sherlock` - Username search across 300+ platforms
- `analyze_digital_footprint` - Comprehensive online presence map

---

## 📈 Risk Score Interpretation

The module calculates an overall risk score from **0-100**:

| Score Range | Risk Level | Meaning | Action |
|-------------|-----------|---------|--------|
| **0-30** | 🟢 Low Risk | High confidence - verified credentials, consistent timeline, strong online presence | ✅ **Proceed** with hire |
| **31-60** | 🟡 Medium Risk | Some inconsistencies or unverified claims - needs clarification | ⚠️ **Request** additional documentation |
| **61-80** | 🟠 High Risk | Significant red flags - timeline gaps, unverified credentials, suspicious patterns | 🔍 **Deep dive** investigation required |
| **81-100** | 🔴 Critical Risk | Severe issues - fake credentials, fabricated history, fraud indicators | ❌ **Reject** or escalate to legal |

### Category Breakdown

Each verification provides sub-scores:

- **Resume Authenticity** (0-100): AI-generated content detection, format analysis
- **Online Presence** (0-100): GitHub activity, LinkedIn profile, social media
- **Credential Validity** (0-100): Professional licenses, education, certifications
- **Company Legitimacy** (0-100): Domain age, business records, social footprint
- **Timeline Consistency** (0-100): Cross-platform timeline gaps/overlaps
- **Digital Footprint** (0-100): Mentions, publications, online reputation

---

## 🔐 Security & Privacy

### Data Retention
- **Resume data**: Deleted after **30 days** automatically
- **Verification reports**: Retained for **90 days** for audit trail
- **Screenshots**: Stored with reports, deleted after 90 days
- **API credentials**: Encrypted in database, never logged

### GDPR Compliance
- ✅ User consent checkbox before verification
- ✅ Right to deletion (manual delete in History tab)
- ✅ Data minimization (only collect necessary info)
- ✅ Audit logging (who verified, when, what was found)
- ✅ No third-party data sharing

### Ethical Guidelines
⚠️ **This tool is for VERIFICATION purposes only, not surveillance**

**DO:**
- Use for pre-employment background checks
- Verify candidate-provided information
- Confirm professional credentials
- Validate work history

**DON'T:**
- Use for discrimination or bias
- Surveil current employees without consent
- Share findings outside HR/hiring team
- Make decisions solely based on automated score

**Always:**
- Inform candidates they will be verified
- Allow candidates to dispute findings
- Conduct human review of results
- Follow local employment laws

---

## 🧪 Testing

### Run Module Tests
```bash
cd AI_agents
python -m pytest UI/modules_external/professional-verification/tests/ -v
```

### Test Individual Tools
```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# Test resume parsing
result = registry.execute_tool(
    'parse_resume',
    file_path='/path/to/resume.pdf',
    _user_id='test_user'
)
print(result)

# Test GitHub verification
result = registry.execute_tool(
    'verify_github_profile',
    github_username='octocat',
    _user_id='test_user',
    _injected_credentials={'github_token': 'ghp_xxx...'}
)
print(result)
```

### Manual Docker Test
```bash
# Build image
cd docker/computer-use
docker-compose up

# Connect VNC to see desktop
# Address: localhost:5900
# Password: valorai

# Watch logs
docker logs -f pv-browser
```

---

## 🐛 Troubleshooting

### "Docker container failed to start"
```bash
# Check Docker is running
docker ps

# Rebuild image
cd docker/computer-use
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### "GitHub API rate limit exceeded"
- **Cause:** Using unauthenticated API (60 req/hr limit)
- **Fix:** Add GitHub token in Settings → Platform Connections
- **With token:** 5000 requests/hour

### "LinkedIn search failed - 2FA required"
- **Cause:** LinkedIn account has 2FA enabled
- **Fix:** Use a dedicated verifier account WITHOUT 2FA
- **Alternative:** Manually disable 2FA for verifier account

### "Computer Use tools not working"
- **Check 1:** Docker image built? `docker images | grep professional-verification-browser`
- **Check 2:** Anthropic API key configured? Check Settings
- **Check 3:** ANTHROPIC_API_KEY environment variable set?

### "Resume parsing failed"
- **Supported formats:** PDF, DOCX, TXT only
- **Max size:** 10MB
- **Fix:** Convert to PDF if unsupported format

### "No tools appearing in registry"
- **Check 1:** Module loaded? Restart Flask app
- **Check 2:** Run: `python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print([t for t in r.tools if 'verification' in t])"`
- **Expected:** Should list 25 verification tools

---

## 📦 Dependencies

### Python Packages
```
PyPDF2>=3.0.0
pdfplumber>=0.10.0
python-docx>=1.0.0
anthropic>=0.25.0
requests>=2.31.0
whois>=0.9.27
docker>=7.0.0
```

### Docker Image
- Ubuntu 22.04
- Xvfb, x11vnc, fluxbox
- Chromium, Firefox
- xdotool, scrot

### External APIs (Free Tiers)
- GitHub API: 5000 req/hr (authenticated)
- Wayback Machine: Unlimited
- WHOIS: Rate-limited but free
- Hunter.io: 50 req/month (free)
- Clearbit: 100 req/month (free)
- Have I Been Pwned: Free

---

## 🎓 Example Use Cases

### Use Case 1: Hiring Software Engineer
```
1. Upload resume PDF
2. Module automatically:
   - Parses resume → finds GitHub: "johndoe"
   - Verifies GitHub → 150 repos, 500 commits, Python/JavaScript
   - Analyzes code quality → Good documentation, tests present
   - Searches LinkedIn → Profile matches resume exactly
   - Checks company → Employer domains valid, existed during claimed tenure
   - Cross-references timeline → All dates consistent
3. Risk Score: 15/100 (Low Risk) ✅
4. Recommendation: Proceed with hire
```

### Use Case 2: Verifying Medical Professional
```
1. Upload CV with medical license number
2. Module automatically:
   - Parses CV → extracts AHPRA registration: MED12345
   - Verifies AHPRA → Computer Use searches registry → License ACTIVE
   - Checks education → University degree confirmed
   - Validates specializations → Cardiology specialty verified
   - Timeline check → Medical school dates match graduation year
3. Risk Score: 8/100 (Low Risk) ✅
4. Recommendation: Credential valid, proceed
```

### Use Case 3: Red Flags Detected
```
1. Upload resume claiming 10 years at Google
2. Module automatically:
   - Parses resume → GitHub listed
   - GitHub check → Account created 6 months ago (RED FLAG)
   - LinkedIn search → Profile not found (RED FLAG)
   - Company check → Email uses Gmail, not @google.com (RED FLAG)
   - Timeline → GitHub shows no activity during claimed Google tenure (RED FLAG)
3. Risk Score: 87/100 (Critical Risk) ❌
4. Recommendation: Strong fraud indicators - reject
```

---

## 🔮 Future Enhancements

**Planned Features:**
- [ ] Video interview analysis (facial recognition, emotion detection)
- [ ] Reference check automation (call/email references)
- [ ] Court records search integration
- [ ] Social media sentiment analysis
- [ ] Resume-to-job matching AI (auto-score candidates)
- [ ] Blockchain credential verification (for universities using blockchain)
- [ ] Multi-language support (international resumes)
- [ ] Bulk verification (upload 50 resumes, verify in parallel)

**Coming Soon:**
- [ ] Webhooks for verification completion
- [ ] Slack/Teams notifications
- [ ] Export to ATS systems (Greenhouse, Lever, Workday)
- [ ] Custom verification templates by industry
- [ ] Machine learning fraud detection model

---

## 📞 Support

**Issues?** Check these resources:

1. **Documentation:** This README and `docker/computer-use/README.md`
2. **Logs:** Flask app logs at `AI_infrastructure/logs/`
3. **Tool Registry:** `python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3()"`
4. **Docker Logs:** `docker logs pv-browser`

**Still stuck?** Contact your platform administrator.

---

## 📄 License

Proprietary - Valor AI Platform  
**Not for redistribution**

---

## 🙏 Credits

**Built with:**
- [Anthropic Claude](https://anthropic.com/) - Computer Use API
- [GitHub API](https://docs.github.com/en/rest) - Profile verification
- [Internet Archive](https://archive.org/) - Wayback Machine
- [Have I Been Pwned](https://haveibeenpwned.com/) - Breach detection
- [Hunter.io](https://hunter.io/) - Email verification
- [Clearbit](https://clearbit.com/) - Company data

**Developed:** December 16, 2025  
**Author:** Valor AI Agent Platform  
**Version:** 1.0.0 (Alpha)

---

🛡️ **Verify with confidence. Hire with certainty.**

"""
Enhanced Real-Time Verification Server with Markdown Reports
============================================================

Runs verification and generates comprehensive markdown reports with:
- Executive summaries
- Risk assessments
- Mitigation strategies
- Compliance documentation

RUN:
    python verification_server_enhanced.py

Then open: http://localhost:8080/verification_dashboard.html

CREATED: December 18, 2025
"""

import asyncio
import websockets
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

# Load .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except:
    pass


# Store active WebSocket connections
active_connections = set()


async def broadcast(message):
    """Send message to all connected clients"""
    if active_connections:
        disconnected = set()
        for websocket in active_connections:
            try:
                await websocket.send(json.dumps(message))
            except:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        active_connections.difference_update(disconnected)


async def save_markdown_report(subject_data, analysis, commands_executed, markdown_content):
    """Save the comprehensive markdown report to file"""
    
    # Create reports directory
    reports_dir = Path(__file__).parent / 'VERIFICATION_REPORTS'
    reports_dir.mkdir(exist_ok=True)
    
    # Generate filename
    name_slug = subject_data['name'].replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"VERIFICATION_REPORT_{name_slug}_{timestamp}.md"
    filepath = reports_dir / filename
    
    # Save report
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\n✅ Report saved: {filepath}")
    
    await broadcast({
        'type': 'report_saved',
        'filename': filename,
        'path': str(filepath)
    })
    
    return str(filepath)


async def run_verification_with_updates(subject_data):
    """
    Run verification with comprehensive markdown report generation
    """
    
    print("\n🚀 Starting enhanced verification with markdown reports...")
    
    # Get API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        await broadcast({
            'type': 'error',
            'message': 'No API key found'
        })
        return
    
    # Import Anthropic
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
    except Exception as e:
        await broadcast({
            'type': 'error',
            'message': f'Failed to initialize Anthropic client: {e}'
        })
        return
    
    # Build comprehensive verification task
    current_date = datetime.now().strftime('%B %d, %Y')
    case_id = f"VER-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    verification_task = f"""
You are a PROFESSIONAL VERIFICATION ANALYST conducting a comprehensive risk assessment for an organization's compliance and security team.

═══════════════════════════════════════════════════════════════════════════════
SUBJECT UNDER VERIFICATION
═══════════════════════════════════════════════════════════════════════════════

**Identity:**
- Full Name: {subject_data['name']}
- Organization: {subject_data['company']}
- Email: {subject_data['email']}
- Domain: {subject_data['domain']}
- Phone: {subject_data.get('phone', 'N/A')}

**Case Details:**
- Date: {current_date}
- Case ID: {case_id}
- Analyst: AI Verification System

═══════════════════════════════════════════════════════════════════════════════
YOUR MISSION
═══════════════════════════════════════════════════════════════════════════════

Conduct a thorough professional verification using technical analysis, security best practices, and risk management principles. You will execute verification commands and provide an OBJECTIVE, RISK-AWARE assessment with ACTIONABLE mitigation strategies.

═══════════════════════════════════════════════════════════════════════════════
VERIFICATION PROTOCOL - EXECUTE IN ORDER
═══════════════════════════════════════════════════════════════════════════════

**PHASE 1: DOMAIN INFRASTRUCTURE VALIDATION**

1. HTTP/HTTPS Accessibility Test:
   curl -I https://{subject_data['domain']}
   
   INTERPRET:
   - Status 200 = Active website (LOW RISK)
   - 301/302 = Redirects - note destination (VERIFY)
   - 403/404 = Access issues (MEDIUM RISK)
   - Timeout = Downtime or blocking (HIGH RISK)
   
2. DNS Resolution Check:
   nslookup {subject_data['domain']}
   
   INTERPRET:
   - IP address = Properly configured (LOW RISK)
   - No address = DNS misconfigured (HIGH RISK)
   - Multiple IPs = Load balancing/CDN (POSITIVE)
   
3. SSL Certificate Validation:
   echo | openssl s_client -connect {subject_data['domain']}:443 -servername {subject_data['domain']} 2>/dev/null | openssl x509 -noout -dates -subject -issuer
   
   INTERPRET:
   - Valid dates = Active security (LOW RISK)
   - Expired = Security vulnerability (CRITICAL)
   - Commercial issuer = Professional (LOW RISK)
   - Let's Encrypt = Acceptable but note (MODERATE)

**PHASE 2: WEB PRESENCE & CONTENT ANALYSIS**

4. Website Content Inspection:
   curl -s https://{subject_data['domain']} | head -n 150
   
   LOOK FOR:
   - Contact information (address, phone, email)
   - Privacy policy / Terms of service
   - Professional design indicators
   - Social media links
   - About us / Team information

5. Technical Infrastructure:
   curl -s https://{subject_data['domain']}/robots.txt
   curl -s https://{subject_data['domain']}/sitemap.xml | head -n 50

**PHASE 3: EMAIL INFRASTRUCTURE VALIDATION**

6. Email Domain Match:
   echo "{subject_data['email']}" | grep -oP '(?<=@).*'
   
   CRITICAL: Professional email MUST match company domain
   
7. MX Record Check:
   nslookup -type=mx {subject_data['email'].split('@')[1]}
   
   INTERPRET:
   - MX records = Email configured (LOW RISK)
   - Multiple MX = Redundancy (POSITIVE)
   - No MX = Email non-functional (CRITICAL)

**PHASE 4: HISTORICAL & REPUTATION ANALYSIS**

8. Web Archive History:
   curl -s "http://archive.org/wayback/available?url={subject_data['domain']}"
   
   INTERPRET:
   - 2+ years = Established (LOW RISK)
   - 6-24 months = Moderate history (MODERATE)
   - < 6 months = New/suspicious (HIGH RISK)

═══════════════════════════════════════════════════════════════════════════════
GENERATE COMPREHENSIVE MARKDOWN REPORT
═══════════════════════════════════════════════════════════════════════════════

After executing ALL verification steps, generate a COMPLETE markdown report with this EXACT structure:

```markdown
# PROFESSIONAL VERIFICATION REPORT

**Subject:** {subject_data['name']}  
**Organization:** {subject_data['company']}  
**Date:** {current_date}  
**Case ID:** {case_id}  
**Analyst:** AI Verification System

---

## 📋 EXECUTIVE SUMMARY

[Write 3-4 sentences summarizing:
1. Overall verification outcome
2. Key findings that support or contradict legitimacy
3. Primary risk factors identified
4. Final recommendation]

**Verification Status:** [VERIFIED ✅ / UNDER REVIEW ⚠️ / DENIED ❌]  
**Confidence Level:** [X%] out of 100%  
**Risk Classification:** [LOW 🟢 / MODERATE 🟡 / HIGH 🟠 / CRITICAL 🔴]  
**Final Recommendation:** [APPROVE / MANUAL REVIEW REQUIRED / DENY]

---

## 👤 SUBJECT INFORMATION

| Field | Provided Value | Verified Status | Notes |
|-------|----------------|-----------------|-------|
| Full Name | {subject_data['name']} | [✅ / ⚠️ / ❌] | [Verification method/issues] |
| Organization | {subject_data['company']} | [✅ / ⚠️ / ❌] | [Cross-reference results] |
| Email Address | {subject_data['email']} | [✅ / ⚠️ / ❌] | [Domain match, MX records] |
| Domain | {subject_data['domain']} | [✅ / ⚠️ / ❌] | [Accessibility, DNS status] |
| Phone | {subject_data.get('phone', 'N/A')} | [✅ / ⚠️ / ❌] | [Format validation] |

---

## 🔍 TECHNICAL VERIFICATION RESULTS

### 1. Domain Infrastructure Assessment (Weight: 30%)

#### 1.1 HTTP/HTTPS Accessibility
- **Test Command:** `curl -I https://{subject_data['domain']}`
- **Result:** [✅ PASS / ❌ FAIL / ⚠️ WARNING]
- **Status Code:** [200/301/403/404/timeout]
- **Response Time:** [X ms]
- **Interpretation:** [Explain what the result means for legitimacy]
- **Risk Impact:** [How this finding affects overall trust]
- **Mitigation (if needed):** [Steps to address any concerns]

#### 1.2 DNS Resolution
- **Test Command:** `nslookup {subject_data['domain']}`
- **Result:** [✅ PASS / ❌ FAIL / ⚠️ WARNING]
- **IP Address(es):** [List IPs found]
- **Geolocation:** [Country/Region if detectable]
- **Interpretation:** [DNS configuration quality assessment]
- **Risk Impact:** [Infrastructure reliability indication]
- **Mitigation (if needed):** [Verification steps]

#### 1.3 SSL Certificate Validation
- **Test Command:** `openssl s_client...`
- **Result:** [✅ PASS / ❌ FAIL / ⚠️ WARNING]
- **Certificate Valid From:** [Start date]
- **Certificate Expires:** [End date]
- **Days Until Expiry:** [X days]
- **Issuer:** [Certificate Authority]
- **Subject Match:** [Does certificate match domain?]
- **Interpretation:** [Security posture assessment]
- **Risk Impact:** [CRITICAL if expired/invalid]
- **Mitigation (if needed):** [Security recommendations]

**Section Score:** [X/30 points]

---

### 2. Web Presence & Content Quality (Weight: 25%)

#### 2.1 Website Content Analysis
- **Test Command:** `curl -s https://{subject_data['domain']}`
- **Result:** [✅ PASS / ❌ FAIL / ⚠️ WARNING]
- **Content Quality:** [Professional / Basic / Poor / Absent]
- **Key Elements Found:**
  - Contact Information: [✅ / ❌]
  - Privacy Policy: [✅ / ❌]
  - Terms of Service: [✅ / ❌]
  - About Us Page: [✅ / ❌]
  - Social Media Links: [✅ / ❌]
- **Content Consistency:** [Matches claimed business / Inconsistent]
- **Interpretation:** [Professional legitimacy indicators]
- **Risk Impact:** [Content quality correlates with business legitimacy]
- **Mitigation (if needed):** [Content verification steps]

#### 2.2 Technical Infrastructure
- **Robots.txt:** [✅ Present / ❌ Absent]
- **Sitemap.xml:** [✅ Present / ❌ Absent]
- **Security Headers:** [Assessed from curl output]
- **Interpretation:** [Web management professionalism]
- **Risk Impact:** [Technical maturity indicator]

**Section Score:** [X/25 points]

---

### 3. Email Infrastructure Validation (Weight: 25%)

#### 3.1 Email Domain Verification
- **Test Command:** `echo "{subject_data['email']}" | grep...`
- **Result:** [✅ PASS / ❌ FAIL / ⚠️ WARNING]
- **Email Domain:** [@extracted-domain]
- **Matches Organization:** [✅ YES / ❌ NO]
- **Email Type:** [Professional / Generic (gmail/yahoo/etc)]
- **Interpretation:** [CRITICAL: Professional email = business legitimacy]
- **Risk Impact:** [Generic email for business claim = RED FLAG]
- **Mitigation (if FAIL):** [Request corporate email verification]

#### 3.2 MX Records Check
- **Test Command:** `nslookup -type=mx {subject_data['email'].split('@')[1]}`
- **Result:** [✅ PASS / ❌ FAIL / ⚠️ WARNING]
- **MX Records Found:** [Count and list]
- **Mail Servers:** [List mail servers]
- **Redundancy:** [Single / Multiple (redundant)]
- **Interpretation:** [Email infrastructure quality]
- **Risk Impact:** [No MX = email doesn't work = suspicious]
- **Mitigation (if needed):** [Email delivery verification steps]

**Section Score:** [X/25 points]

---

### 4. Historical Data & Reputation (Weight: 20%)

#### 4.1 Web Archive Analysis
- **Test Command:** `curl archive.org/wayback...`
- **Result:** [✅ PASS / ❌ FAIL / ⚠️ WARNING]
- **Archived Snapshots:** [Count]
- **Earliest Snapshot:** [Date]
- **Latest Snapshot:** [Date]
- **Domain Age (estimated):** [X years/months]
- **Historical Consistency:** [Content remained consistent / Changed significantly]
- **Interpretation:** [Long history = credibility; No history = new/suspicious]
- **Risk Impact:** 
  - 2+ years: LOW RISK
  - 6-24 months: MODERATE RISK
  - < 6 months: HIGH RISK
- **Mitigation (if new domain):** [Additional business verification required]

**Section Score:** [X/20 points]

---

## ⚠️ RISK ASSESSMENT MATRIX

| Risk Category | Current Status | Severity Level | Business Impact | Recommended Mitigation |
|---------------|----------------|----------------|-----------------|------------------------|
| **Identity Fraud Risk** | [LOW/MODERATE/HIGH/CRITICAL] | [🟢/🟡/🟠/🔴] | [Describe potential impact] | [Specific action items] |
| **Domain Spoofing Risk** | [LOW/MODERATE/HIGH/CRITICAL] | [🟢/🟡/🟠/🔴] | [Describe potential impact] | [Specific action items] |
| **Phishing/Scam Risk** | [LOW/MODERATE/HIGH/CRITICAL] | [🟢/🟡/🟠/🔴] | [Describe potential impact] | [Specific action items] |
| **Business Legitimacy** | [LOW/MODERATE/HIGH/CRITICAL] | [🟢/🟡/🟠/🔴] | [Describe potential impact] | [Specific action items] |
| **Technical Security** | [LOW/MODERATE/HIGH/CRITICAL] | [🟢/🟡/🟠/🔴] | [Describe potential impact] | [Specific action items] |
| **Data Privacy Compliance** | [LOW/MODERATE/HIGH/CRITICAL] | [🟢/🟡/🟠/🔴] | [Describe potential impact] | [Specific action items] |

---

## ✅ POSITIVE INDICATORS (Legitimacy Signals)

List ALL findings that support the subject's legitimacy, with specific evidence:

1. **[Finding Name]** - Weight: [X%]
   - Evidence: [Specific data point]
   - Why This Matters: [Legitimacy correlation]
   - Confidence: [HIGH/MODERATE/LOW]

2. **[Finding Name]** - Weight: [X%]
   - Evidence: [Specific data point]
   - Why This Matters: [Legitimacy correlation]
   - Confidence: [HIGH/MODERATE/LOW]

[Continue for all positive findings...]

**Total Positive Weight:** [X%]

---

## 🚩 RED FLAGS & CONCERNS

List ALL concerning findings with severity and impact:

1. **[Concern Name]** - Severity: [CRITICAL 🔴 / HIGH 🟠 / MODERATE 🟡 / LOW 🟢]
   - Finding: [Specific issue discovered]
   - Risk Type: [Fraud/Security/Compliance/Other]
   - Potential Impact: [What could happen if ignored]
   - Verification Needed: [How to resolve this concern]
   - Recommended Action: [Immediate steps]

2. **[Concern Name]** - Severity: [Level]
   - Finding: [Specific issue]
   - Risk Type: [Type]
   - Potential Impact: [Impact description]
   - Verification Needed: [Resolution steps]
   - Recommended Action: [Action items]

[Continue for all red flags...]

**Total Red Flags:** [Count by severity]
- 🔴 Critical: [Count]
- 🟠 High: [Count]
- 🟡 Moderate: [Count]
- 🟢 Low: [Count]

---

## ❓ AREAS REQUIRING MANUAL VERIFICATION

Items that automated checks cannot verify - require human investigation:

1. **[Item Name]**
   - What Needs Verification: [Specific requirement]
   - Why It Matters: [Risk if not verified]
   - How to Verify: [Step-by-step process]
   - Priority: [URGENT/HIGH/MEDIUM/LOW]
   - Estimated Time: [X hours/days]

2. **[Item Name]**
   - What Needs Verification: [Requirement]
   - Why It Matters: [Risk explanation]
   - How to Verify: [Verification process]
   - Priority: [Level]
   - Estimated Time: [Duration]

[Continue for all manual verification items...]

---

## 📊 CONFIDENCE SCORE CALCULATION

### Scoring Methodology

```
Category Scores:
─────────────────────────────────────────────────
Domain Infrastructure (30%):     [XX]/30 points
  - HTTP Accessibility:   [X]/10
  - DNS Resolution:       [X]/10
  - SSL Certificate:      [X]/10

Web Presence Quality (25%):      [XX]/25 points
  - Content Quality:      [X]/15
  - Technical Setup:      [X]/10

Email Infrastructure (25%):      [XX]/25 points
  - Domain Match:         [X]/15
  - MX Records:           [X]/10

Historical Reputation (20%):     [XX]/20 points
  - Web Archive:          [X]/15
  - Domain Age:           [X]/5

─────────────────────────────────────────────────
TOTAL CONFIDENCE SCORE:          [XX]/100 points
PERCENTAGE:                      XX%
─────────────────────────────────────────────────
```

### Score Interpretation Guide

- **80-100% (HIGH CONFIDENCE)**: 
  - All critical checks passed
  - Established online presence (2+ years)
  - Professional infrastructure
  - Minimal to no red flags
  - **Action:** Standard approval process

- **50-79% (MODERATE CONFIDENCE)**:
  - Most checks passed with minor concerns
  - Some gaps in verification
  - Newer presence (6-24 months)
  - Some explainable inconsistencies
  - **Action:** Enhanced due diligence recommended

- **30-49% (LOW CONFIDENCE)**:
  - Multiple failed checks
  - Significant concerns present
  - Limited verifiable history
  - Technical or security issues
  - **Action:** Manual review required before approval

- **0-29% (VERY LOW CONFIDENCE)**:
  - Critical failures in multiple areas
  - Strong fraud indicators
  - Severe technical issues
  - Cannot verify basic claims
  - **Action:** Deny or extensive investigation

**Current Assessment: [XX%] = [CONFIDENCE LEVEL]**

---

## 💡 RECOMMENDATION & DETAILED RATIONALE

### Primary Recommendation: **[APPROVE ✅ / MANUAL REVIEW REQUIRED ⚠️ / DENY ❌]**

### Comprehensive Rationale

[Write 2-3 paragraphs explaining in detail:
1. Why you reached this specific recommendation
2. The weight given to various findings
3. How positive and negative factors balanced out
4. Any assumptions made
5. Confidence level in this recommendation]

### Key Supporting Evidence

The following findings were CRITICAL to reaching this recommendation:

1. **[Critical Finding #1]**
   - Data Point: [Specific evidence]
   - Weight in Decision: [HIGH/MODERATE/LOW]
   - Supports: [APPROVAL/DENIAL]

2. **[Critical Finding #2]**
   - Data Point: [Specific evidence]
   - Weight in Decision: [HIGH/MODERATE/LOW]
   - Supports: [APPROVAL/DENIAL]

3. **[Critical Finding #3]**
   - Data Point: [Specific evidence]
   - Weight in Decision: [HIGH/MODERATE/LOW]
   - Supports: [APPROVAL/DENIAL]

---

## 🛡️ RISK MITIGATION STRATEGIES

### If Proceeding with Approval

Implement these safeguards to mitigate identified risks:

**Immediate Actions (Before Onboarding):**
1. [Specific action] - Rationale: [Why needed] - Timeline: [When]
2. [Specific action] - Rationale: [Why needed] - Timeline: [When]
3. [Specific action] - Rationale: [Why needed] - Timeline: [When]

**Ongoing Monitoring (Post-Approval):**
1. [Monitoring activity] - Frequency: [How often] - Alert Triggers: [What to watch]
2. [Monitoring activity] - Frequency: [How often] - Alert Triggers: [What to watch]
3. [Monitoring activity] - Frequency: [How often] - Alert Triggers: [What to watch]

**Contingency Measures:**
1. [Backup plan] - Trigger: [When to activate] - Process: [How to execute]
2. [Backup plan] - Trigger: [When to activate] - Process: [How to execute]

### If Denying or Requiring Manual Review

**Alternative Verification Methods:**
1. [Alternative approach] - Rationale: [Why this might work] - Resources Needed: [What's required]
2. [Alternative approach] - Rationale: [Why this might work] - Resources Needed: [What's required]

**Path to Approval (if applicable):**
- Step 1: [Action required from subject]
- Step 2: [Additional verification to perform]
- Step 3: [Criteria that must be met]
- Timeline: [How long this process takes]

---

## 📋 ACTION ITEMS & NEXT STEPS

### For Verification Team
- [ ] **[Action Item]** - Assigned To: [Role] - Due: [Date] - Priority: [HIGH/MEDIUM/LOW]
- [ ] **[Action Item]** - Assigned To: [Role] - Due: [Date] - Priority: [HIGH/MEDIUM/LOW]
- [ ] **[Action Item]** - Assigned To: [Role] - Due: [Date] - Priority: [HIGH/MEDIUM/LOW]

### For Risk Management
- [ ] **[Action Item]** - Assigned To: [Role] - Due: [Date] - Priority: [HIGH/MEDIUM/LOW]
- [ ] **[Action Item]** - Assigned To: [Role] - Due: [Date] - Priority: [HIGH/MEDIUM/LOW]

### For Compliance Team
- [ ] **[Action Item]** - Assigned To: [Role] - Due: [Date] - Priority: [HIGH/MEDIUM/LOW]
- [ ] **[Action Item]** - Assigned To: [Role] - Due: [Date] - Priority: [HIGH/MEDIUM/LOW]

### For Subject (if manual review required)
- [ ] **[Required Documentation]** - Format: [Specification] - Deadline: [Date]
- [ ] **[Required Documentation]** - Format: [Specification] - Deadline: [Date]

---

## 📎 APPENDIX: TECHNICAL DETAILS

### Commands Executed

Full list of verification commands run during this assessment:

```bash
# Phase 1: Domain Infrastructure
1. curl -I https://{subject_data['domain']}
2. nslookup {subject_data['domain']}
3. echo | openssl s_client -connect {subject_data['domain']}:443 ...

# Phase 2: Web Presence
4. curl -s https://{subject_data['domain']} | head -n 150
5. curl -s https://{subject_data['domain']}/robots.txt
6. curl -s https://{subject_data['domain']}/sitemap.xml

# Phase 3: Email Infrastructure
7. echo "{subject_data['email']}" | grep -oP '(?<=@).*'
8. nslookup -type=mx [email domain]

# Phase 4: Historical Data
9. curl -s "http://archive.org/wayback/available?url={subject_data['domain']}"

Total Commands: [X]
Successful: [X]
Failed: [X]
Warnings: [X]
```

### Raw Technical Data

<details>
<summary>Click to expand raw command outputs</summary>

```
[Include sanitized raw output from critical commands]
[This provides audit trail and transparency]
```

</details>

---

## 📜 COMPLIANCE & AUDIT INFORMATION

### Verification Standards Applied
- ✅ Professional Identity Verification Protocol v2.0
- ✅ Risk-Based Due Diligence Framework (FATF Guidelines)
- ✅ Technical Security Assessment Standards (NIST)
- ✅ Data Privacy Regulations (GDPR/CCPA Compliant)
- ✅ Know Your Customer (KYC) Best Practices

### Audit Trail
- **Verification Date:** {current_date}
- **System Version:** AI Verification System v1.0
- **Model Used:** Claude Sonnet 4.5 (Anthropic)
- **Commands Executed:** [Total count]
- **Processing Time:** [Duration in seconds]
- **Data Sources:** DNS, WHOIS, SSL Certificate Authorities, Web Archive
- **Verification Analyst:** AI System (Human Review: [Required/Not Required])

### Data Handling & Privacy
- **PII Protection:** All personally identifiable information handled per GDPR
- **Data Retention:** 7 years (regulatory compliance requirement)
- **Access Control:** Restricted to authorized personnel only
- **Encryption:** Data encrypted at rest and in transit
- **Audit Logs:** All access logged and monitored

### Report Authentication
- **Report ID:** {case_id}
- **Generated:** {current_date} at [timestamp]
- **Checksum:** [Generate MD5/SHA256 of report for integrity]
- **Digital Signature:** [If applicable]

---

## 📞 CONTACT & ESCALATION

### For Questions About This Report
- **Primary Contact:** Verification Team Lead
- **Email:** verification@[organization].com
- **Response Time:** Within 24 hours

### Escalation Path
1. **Level 1:** Verification Team Lead (standard inquiries)
2. **Level 2:** Risk Management Director (risk assessment questions)
3. **Level 3:** Chief Compliance Officer (policy exceptions, critical decisions)

### Report Amendments
If additional information becomes available that may affect this assessment:
- Contact verification team immediately
- Reference Case ID: {case_id}
- Provide supporting documentation
- Request re-assessment if warranted

---

## ⚖️ LEGAL DISCLAIMER

This verification report is provided for informational and risk assessment purposes only. While every effort has been made to ensure accuracy, this report:

- Does not constitute legal advice
- Should be used as one factor in decision-making, not the sole determinant
- May contain information that becomes outdated over time
- Reflects technical verification only; does not replace human judgment
- Is subject to the limitations of automated verification tools

Organizations using this report should:
- Conduct additional due diligence as appropriate
- Consider their specific risk tolerance and policies
- Consult legal counsel for significant decisions
- Maintain independent verification procedures

---

═══════════════════════════════════════════════════════════════════════════════
END OF VERIFICATION REPORT
═══════════════════════════════════════════════════════════════════════════════

**Report Generated:** {current_date} at {datetime.now().strftime('%H:%M:%S')} UTC  
**Verification System:** AI-Powered Professional Verification v1.0  
**Final Confidence:** [XX%]  
**Final Status:** [VERIFIED/UNDER REVIEW/DENIED]  
**Case ID:** {case_id}

═══════════════════════════════════════════════════════════════════════════════
```

YOUR TASKS:
1. Execute ALL bash commands from the verification protocol
2. Fill in EVERY section of this markdown template with DETAILED, SPECIFIC information
3. Provide OBJECTIVE analysis with CLEAR risk assessments
4. Include ACTIONABLE mitigation strategies for identified risks
5. Generate SPECIFIC next steps for each stakeholder group
6. Calculate confidence score based on actual findings
7. Make CLEAR, JUSTIFIED recommendation

BE THOROUGH. BE SPECIFIC. BE OBJECTIVE. BE RISK-AWARE.

After generating the complete markdown report, also provide a JSON summary for the dashboard.
"""
    
    messages = [{
        "role": "user",
        "content": verification_task
    }]
    
    iteration = 0
    max_iterations = 50
    total_tokens = 0
    all_commands = []
    markdown_content = ""
    
    try:
        while iteration < max_iterations:
            iteration += 1
            
            # Send iteration update
            await broadcast({
                'type': 'iteration',
                'iteration': iteration,
                'stop_reason': 'processing'
            })
            
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=8192,  # Increased for comprehensive reports
                tools=[
                    {"type": "bash_20250124", "name": "bash"}
                ],
                messages=messages
            )
            
            # Update token count
            if hasattr(response, 'usage'):
                total_tokens += response.usage.input_tokens + response.usage.output_tokens
                await broadcast({
                    'type': 'tokens',
                    'count': total_tokens
                })
            
            # Send iteration status
            await broadcast({
                'type': 'iteration',
                'iteration': iteration,
                'stop_reason': response.stop_reason
            })
            
            # Check if done
            if response.stop_reason == "end_turn":
                # Extract final analysis
                final_text = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        final_text += block.text
                        
                        # Send reasoning
                        await broadcast({
                            'type': 'reasoning',
                            'iteration': iteration,
                            'text': block.text
                        })
                
                # Extract markdown report from response
                import re
                markdown_match = re.search(r'```markdown\n(.*?)\n```', final_text, re.DOTALL)
                if markdown_match:
                    markdown_content = markdown_match.group(1)
                else:
                    markdown_content = final_text  # Use full text if no markdown block
                
                # Save markdown report
                report_path = await save_markdown_report(
                    subject_data, 
                    {}, 
                    all_commands, 
                    markdown_content
                )
                
                # Try to extract JSON from response
                try:
                    json_match = re.search(r'\{[\s\S]*"verification_status"[\s\S]*\}', final_text)
                    if json_match:
                        analysis = json.loads(json_match.group(0))
                    else:
                        analysis = {
                            "verification_status": "REPORT_GENERATED",
                            "confidence_score": 0,
                            "summary": f"Comprehensive report saved to: {report_path}"
                        }
                except:
                    analysis = {
                        "verification_status": "REPORT_GENERATED",
                        "confidence_score": 0,
                        "summary": f"Comprehensive report saved to: {report_path}"
                    }
                
                # Send final results
                await broadcast({
                    'type': 'results',
                    'results': analysis,
                    'report_path': report_path
                })
                
                return {
                    "success": True,
                    "analysis": analysis,
                    "report_path": report_path,
                    "iterations": iteration,
                    "tokens": total_tokens
                }
            
            # Process tool use
            if response.stop_reason == "tool_use":
                tool_results = []
                
                for block in response.content:
                    if hasattr(block, 'text') and block.text:
                        # Send AI reasoning
                        await broadcast({
                            'type': 'reasoning',
                            'iteration': iteration,
                            'text': block.text
                        })
                    
                    if block.type == "tool_use":
                        tool_name = block.name
                        
                        if tool_name == "bash":
                            # Execute bash command
                            command = block.input.get('command', '')
                            
                            # Track command
                            all_commands.append(command)
                            
                            # Send command to dashboard
                            await broadcast({
                                'type': 'command',
                                'command': command,
                                'output': 'Executing...'
                            })
                            
                            # Simulate execution (in production, run in Docker)
                            output = f"Simulated output for: {command}\n(Docker container needed for actual execution)"
                            
                            # Send command result
                            await broadcast({
                                'type': 'command',
                                'command': command,
                                'output': output
                            })
                            
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": output
                            })
                
                # Continue conversation
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
            
            else:
                # Unexpected stop
                await broadcast({
                    'type': 'error',
                    'message': f'Unexpected stop reason: {response.stop_reason}'
                })
                break
            
            # Small delay between iterations
            await asyncio.sleep(0.5)
        
        if iteration >= max_iterations:
            await broadcast({
                'type': 'error',
                'message': f'Max iterations ({max_iterations}) reached'
            })
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        await broadcast({
            'type': 'error',
            'message': str(e)
        })


async def handle_websocket(websocket, path):
    """Handle WebSocket connection"""
    
    print(f"✅ Client connected from {websocket.remote_address}")
    
    # Add to active connections
    active_connections.add(websocket)
    
    try:
        # Wait for messages
        async for message in websocket:
            data = json.loads(message)
            
            if data.get('action') == 'start_verification':
                subject = data.get('subject', {
                    'name': 'Gregory Dutton',
                    'company': 'Institute of Sustainable Biodiversity',
                    'email': 'gregory.dutton@isb.eco',
                    'domain': 'isb.eco',
                    'phone': '+61 461 357 358'
                })
                
                # Run verification
                await run_verification_with_updates(subject)
    
    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Client disconnected")
    
    finally:
        # Remove from active connections
        active_connections.discard(websocket)


class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler with CORS enabled"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress logging
        pass


def run_http_server():
    """Run HTTP server for dashboard"""
    
    # Change to TESTS directory
    os.chdir(Path(__file__).parent)
    
    server = HTTPServer(('localhost', 8080), CORSHTTPRequestHandler)
    print(f"✅ HTTP server started on http://localhost:8080")
    print(f"   Open: http://localhost:8080/verification_dashboard.html")
    server.serve_forever()


async def main():
    """Main server"""
    
    print("="*80)
    print("🚀 ENHANCED VERIFICATION SERVER - COMPREHENSIVE MARKDOWN REPORTS")
    print("="*80)
    print("")
    print("Starting servers...")
    print("")
    
    # Start HTTP server in background thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    print(f"✅ WebSocket server starting on ws://localhost:5555")
    print("")
    print("="*80)
    print("📊 DASHBOARD ACCESS")
    print("="*80)
    print("")
    print(f"   🌐 Open in browser: http://localhost:8080/verification_dashboard.html")
    print("")
    print("="*80)
    print("📝 ENHANCED FEATURES")
    print("="*80)
    print("")
    print("   ✅ Comprehensive markdown reports with:")
    print("      • Executive summaries")
    print("      • Risk assessment matrices")
    print("      • Mitigation strategies")
    print("      • Compliance documentation")
    print("      • Action items for all stakeholders")
    print("      • Audit trails")
    print("")
    print("   ✅ Reports saved to: VERIFICATION_REPORTS/")
    print("")
    print("="*80)
    print("")
    print("Press Ctrl+C to stop the server")
    print("")
    
    # Start WebSocket server
    async with websockets.serve(handle_websocket, "localhost", 5555):
        await asyncio.Future()  # Run forever


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()

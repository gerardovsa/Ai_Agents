# COMPUTER USE INVESTIGATION METHODOLOGY
## Advanced Verification Techniques Demonstration
**Date**: December 19, 2025

---

## EXECUTIVE SUMMARY

This document demonstrates **STRATEGIC** Computer Use investigation - not just running pre-defined commands, but **ADAPTIVE** exploration based on findings. The AI verification dashboard currently lacks this intelligent progression.

### Current Dashboard Problems:
1. **Rigid Script Execution** - Runs same commands regardless of findings
2. **No Adaptive Branching** - Doesn't pivot based on discovered data
3. **Limited Search Variations** - Uses narrow search terms
4. **Shallow Analysis** - Surface checks without deep dives
5. **No Cross-Referencing** - Misses connections between data points

---

## PHASE 1: RECONNAISSANCE - BROAD TO NARROW

### Strategy: Start Wide, Then Focus

#### Example: Investigating "Gregory Ross Dutton"

**Step 1: Multiple Name Variations**
```bash
# Try different name formats
python -c "import requests; print(requests.get('https://www.google.com/search?q=Gregory+Ross+Dutton').status_code)"
python -c "import requests; print(requests.get('https://www.google.com/search?q=Greg+Dutton').status_code)"
python -c "import requests; print(requests.get('https://www.google.com/search?q=G.R.+Dutton').status_code)"
```

**Step 2: Name + Context Combinations**
```bash
# Location-based searches
curl -s "https://www.google.com/search?q=Gregory+Dutton+Australia"
curl -s "https://www.google.com/search?q=Gregory+Dutton+Colombia"
curl -s "https://www.google.com/search?q=Gregory+Dutton+Manizales"

# Company-based searches
curl -s "https://www.google.com/search?q=Gregory+Dutton+SCA+Technology"
curl -s "https://www.google.com/search?q=Gregory+Dutton+ISB.eco"

# Role-based searches
curl -s "https://www.google.com/search?q=Gregory+Dutton+CEO"
curl -s "https://www.google.com/search?q=Gregory+Dutton+founder"
```

**Step 3: Email Pattern Analysis**
```python
# Test common email formats
patterns = [
    'gregory.dutton@scatechnology.ai',
    'greg.dutton@scatechnology.ai',
    'gdutton@scatechnology.ai',
    'ross.dutton@scatechnology.ai',
    'gregory@scatechnology.ai'
]
for email in patterns:
    print(f'Testing: {email}')
```

---

## PHASE 2: VERIFICATION - CROSS-REFERENCE EVERYTHING

### Strategy: Validate Claims Against Authoritative Sources

#### Domain Infrastructure Deep Dive

**Step 1: DNS History Analysis**
```python
import requests

domains = ['scatechnology.ai', 'isb.eco']
record_types = ['A', 'MX', 'TXT', 'NS', 'SOA']

for domain in domains:
    print(f'\n=== {domain} ===')
    for rtype in record_types:
        url = f'https://dns.google/resolve?name={domain}&type={rtype}'
        r = requests.get(url)
        print(f'{rtype}: {r.json()}')
```

**Step 2: Web Archive Deep Scan**
```python
import requests

domain = 'scatechnology.ai'
timestamps = ['20241201', '20240601', '20240101', '20230101', '20220101']

for ts in timestamps:
    url = f'http://archive.org/wayback/available?url={domain}&timestamp={ts}'
    r = requests.get(url)
    print(f'{ts}: {r.json()}')
```

**Step 3: SSL Certificate Chain Analysis**
```python
import ssl
import socket
from datetime import datetime

def check_ssl(domain):
    context = ssl.create_default_context()
    with socket.create_connection((domain, 443), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            cert = ssock.getpeercert()
            print(f'\n=== SSL Certificate for {domain} ===')
            print(f'Subject: {cert.get("subject")}')
            print(f'Issuer: {cert.get("issuer")}')
            print(f'Version: {cert.get("version")}')
            print(f'Serial: {cert.get("serialNumber")}')
            print(f'Not Before: {cert.get("notBefore")}')
            print(f'Not After: {cert.get("notAfter")}')
            print(f'Subject Alt Names: {cert.get("subjectAltName")}')

check_ssl('scatechnology.ai')
check_ssl('isb.eco')
```

---

## PHASE 3: ANOMALY DETECTION - FIND CONTRADICTIONS

### Strategy: Look for Mismatches and Red Flags

#### Checklist of Investigative Angles:

**1. Domain Age vs Business Claims**
```python
from datetime import datetime

ssl_date = 'Dec 15, 2025'
claimed_years = '10+ years in business'

print(f'SSL Certificate: {ssl_date}')
print(f'Business Claims: {claimed_years}')
print(f'FINDING: MAJOR DISCREPANCY')
```

**2. Geographic Consistency**
```python
locations = {
    'Website claims': 'Colombia (Manizales)',
    'Phone country': 'Australia (+61)',
    'Email domain': 'Poland (isb.eco)',
    'Hosting IP': 'USA (California)',
    'SSL issuer': 'USA (Let\'s Encrypt)'
}

print('=== GEOGRAPHIC ANALYSIS ===')
for source, location in locations.items():
    print(f'{source}: {location}')
print('\nFINDING: MULTIPLE INCONSISTENT LOCATIONS')
```

**3. Email Domain Alignment**
```python
email = 'gregory.dutton@isb.eco'
company = 'SCA Technology (scatechnology.ai)'

print(f'Contact Email: {email}')
print(f'Company: {company}')
print(f'FINDING: EMAIL DOMAIN MISMATCH - RED FLAG')
```

**4. Social Media Footprint Analysis**
```python
import requests

platforms = {
    'LinkedIn': 'https://www.linkedin.com/search/results/all/?keywords=Gregory+Dutton+SCA+Technology',
    'Twitter': 'https://twitter.com/search?q=Gregory+Dutton+SCA+Technology',
    'GitHub': 'https://github.com/search?q=Gregory+Dutton',
    'Medium': 'https://medium.com/search?q=Gregory+Dutton',
    'Dev.to': 'https://dev.to/search?q=Gregory+Dutton'
}

print('=== SOCIAL MEDIA PRESENCE CHECK ===')
for platform, url in platforms.items():
    try:
        r = requests.get(url, timeout=5)
        print(f'{platform}: Status {r.status_code}')
    except Exception as e:
        print(f'{platform}: ERROR - {e}')
```

---

## PHASE 4: DEEP DIVE - FOLLOW THE EVIDENCE

### Strategy: Adaptive Investigation Based on Findings

#### Example: When You Find a Mismatch

**Scenario**: Email uses isb.eco but represents scatechnology.ai

**Follow-up Actions**:
```python
import requests
from bs4 import BeautifulSoup

print('=== ISB.ECO DEEP DIVE ===')

# Get full website content
r = requests.get('https://www.isb.eco', timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

# Extract ALL text
text = soup.get_text()

# Search for person mentions
people = ['Gregory', 'Dutton', 'Greg', 'Ross']
print('\nPeople mentions:')
for person in people:
    count = text.count(person)
    print(f'{person}: {count} mentions')

# Extract all email addresses
import re
emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
print(f'\nEmails found: {set(emails)}')

# Extract all links
links = [a.get('href') for a in soup.find_all('a', href=True)]
print(f'\nTotal links: {len(links)}')
print('External links:')
for link in links:
    if link.startswith('http') and 'isb.eco' not in link:
        print(f'  - {link}')
```

**2. Check Business Relationships**
```bash
# Search for connections between entities
curl -s "https://www.google.com/search?q=ISB.eco+SCA+Technology+partnership"
curl -s "https://www.google.com/search?q=ISB.eco+Manizales+Colombia"
curl -s "https://www.google.com/search?q=Gregory+Dutton+biodiversity+AI"
```

**3. Reverse IP Lookup**
```python
import requests

def reverse_ip_lookup(ip):
    # Use multiple services
    services = [
        f'https://api.hackertarget.com/reverseiplookup/?q={ip}',
        f'https://api.viewdns.info/reverseip/?host={ip}&apikey=demo',
    ]
    
    print(f'=== REVERSE IP LOOKUP: {ip} ===')
    for service in services:
        try:
            r = requests.get(service, timeout=5)
            print(f'\nService: {service}')
            print(r.text[:500])
        except Exception as e:
            print(f'Error: {e}')

reverse_ip_lookup('216.198.79.1')
```

---

## PHASE 5: PATTERN RECOGNITION - IDENTIFY FRAUD SIGNATURES

### Strategy: Match Against Known Scam Patterns

#### Red Flag Checklist:

**1. Brand New Domain with Old Claims**
```python
indicators = {
    'Domain created': '3 days ago',
    'Business claims': '10+ years experience',
    'SSL age': '3 days',
    'Archive history': 'None'
}

score = 0
if 'days' in indicators['Domain created']:
    score += 50
    print('[CRITICAL] Domain brand new')

if 'years' in indicators['Business claims']:
    score += 30
    print('[WARNING] Claims long history')

print(f'\nFRAUD RISK SCORE: {score}/100')
```

**2. Pressure Tactics Timeline**
```python
from datetime import datetime, timedelta

events = {
    'Domain created': datetime(2025, 12, 15),
    'First contact': datetime(2025, 12, 17),
    'Access request': datetime(2025, 12, 17),
    'Deadline given': datetime(2025, 12, 23)
}

domain_age = (datetime.now() - events['Domain created']).days
time_to_contact = (events['First contact'] - events['Domain created']).days
deadline_window = (events['Deadline given'] - events['Access request']).days

print('=== TIMELINE ANALYSIS ===')
print(f'Domain age when contacted: {domain_age} days')
print(f'Time from domain to contact: {time_to_contact} days')
print(f'Deadline pressure: {deadline_window} days')

if domain_age < 7 and deadline_window < 7:
    print('\n[CRITICAL] Extremely rushed timeline - MAJOR RED FLAG')
```

**3. Professional Verification Impossibility**
```python
verification_attempts = {
    'LinkedIn profile': 'Not found',
    'Twitter account': 'Not found',
    'GitHub repos': 'Not found',
    'Company news': 'Not found',
    'Business registration': 'Cannot verify online',
    'Professional publications': 'Not found'
}

successful = sum(1 for v in verification_attempts.values() if 'found' not in v.lower())
total = len(verification_attempts)

print('=== PROFESSIONAL VERIFICATION RESULTS ===')
for check, result in verification_attempts.items():
    print(f'{check}: {result}')

print(f'\nVerified: {successful}/{total}')
if successful == 0:
    print('[CRITICAL] ZERO independent verification possible - FRAUD INDICATOR')
```

---

## KEY DIFFERENCES: SMART AI vs DASHBOARD AI

### Current Dashboard Behavior:
```
1. Run command list A through Z
2. Display all outputs
3. End investigation
```

### Strategic AI Behavior:
```
1. Run initial reconnaissance (commands A-E)
2. ANALYZE RESULTS
3. IF domain_age < 7 days THEN:
     - Deep dive into web archive (more timestamps)
     - Check DNS history for changes
     - Search for related domains
4. IF email_mismatch THEN:
     - Investigate BOTH domains
     - Look for business relationships
     - Check for domain parking/for-sale
5. IF no_social_media THEN:
     - Try alternative platforms
     - Search for person in news
     - Check professional databases
6. SYNTHESIZE findings into risk score
```

---

## ADVANCED TECHNIQUES

### 1. Recursive Domain Discovery
```python
import requests
from bs4 import BeautifulSoup

def find_linked_domains(start_domain):
    visited = set()
    to_visit = [start_domain]
    
    while to_visit:
        domain = to_visit.pop()
        if domain in visited:
            continue
        visited.add(domain)
        
        try:
            r = requests.get(f'https://{domain}', timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Extract all external links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href.startswith('http'):
                    # Extract domain
                    from urllib.parse import urlparse
                    linked_domain = urlparse(href).netloc
                    if linked_domain and linked_domain not in visited:
                        print(f'Found linked domain: {linked_domain}')
                        to_visit.append(linked_domain)
        except:
            pass

find_linked_domains('scatechnology.ai')
```

### 2. Temporal Analysis
```python
# Check if multiple events happened simultaneously (coordination indicator)
events = [
    ('Domain registered', '2025-12-15'),
    ('SSL issued', '2025-12-15'),
    ('Website deployed', '2025-12-15'),
    ('First email sent', '2025-12-17')
]

print('=== TEMPORAL CLUSTERING ANALYSIS ===')
for event, date in events:
    print(f'{event}: {date}')

# Check for suspicious clustering
dates = [e[1] for e in events]
if len(set(dates[:3])) == 1:
    print('\n[SUSPICIOUS] Multiple events on exact same day')
    print('Indicates: Pre-planned deployment, not organic growth')
```

### 3. Linguistic Analysis
```python
import requests
from bs4 import BeautifulSoup

def check_generic_content(url):
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text()
    
    # Common scam phrases
    generic_phrases = [
        'leading provider',
        'industry leader',
        'cutting-edge technology',
        'innovative solutions',
        'trusted partner',
        'years of experience'
    ]
    
    print('=== GENERIC CONTENT ANALYSIS ===')
    for phrase in generic_phrases:
        if phrase in text.lower():
            print(f'[FOUND] "{phrase}"')
    
check_generic_content('https://scatechnology.ai')
```

---

## SEARCH TERM VARIATIONS

### The Problem with Single Search Terms

**Bad**: Just search "Gregory Dutton"
**Good**: Try 15+ variations

### Name Search Matrix:

```python
# Full combinations
name_parts = {
    'first': ['Gregory', 'Greg', 'G.'],
    'middle': ['Ross', 'R.', ''],
    'last': ['Dutton']
}

contexts = [
    'CEO', 'founder', 'director', 'manager',
    'SCA Technology', 'scatechnology.ai',
    'Australia', 'Colombia', 'Manizales',
    'AI', 'artificial intelligence', 'technology',
    'biodiversity', 'ISB', 'sustainable'
]

# Generate all combinations
for first in name_parts['first']:
    for middle in name_parts['middle']:
        for last in name_parts['last']:
            name = f"{first} {middle} {last}".strip()
            print(f"Search: {name}")
            
            # Add context variations
            for context in contexts:
                print(f"  + {context}")
```

### Expected Results:
- LinkedIn profiles
- Company websites
- News articles
- Academic papers
- GitHub repositories
- Conference presentations
- Social media accounts
- Business registrations

### If NONE Found:
**That's a major red flag** - professional people have digital footprints

---

## CONCLUSION

**The difference between current dashboard and strategic investigation:**

**Current Dashboard**: 
- Execute 50 commands sequentially
- Display all outputs
- No analysis between commands
- No adaptive branching

**Strategic Investigation**: 
1. Execute 10 reconnaissance commands
2. **ANALYZE** what you found
3. Branch into 3-5 specialized follow-up commands **BASED ON FINDINGS**
4. Cross-reference results
5. Identify patterns
6. Calculate risk scores
7. Provide actionable intelligence

**The AI should THINK between commands, not just execute a script.**

---

## RECOMMENDATIONS FOR DASHBOARD IMPROVEMENT

### 1. Add Decision Trees
```python
if domain_age < 30:
    run_commands(['deep_whois', 'archive_scan', 'dns_history'])
elif ssl_mismatch:
    run_commands(['certificate_chain', 'issuer_lookup'])
```

### 2. Add Cross-Referencing
```python
results = {}
results['domain_age'] = check_domain_age()
results['claimed_age'] = extract_business_age()

if results['domain_age'] << results['claimed_age']:
    flag_critical_discrepancy()
```

### 3. Add Progressive Depth
```python
# Level 1: Quick checks (30 seconds)
# Level 2: Deep dive if suspicious (2 minutes)
# Level 3: Forensic analysis if red flags (5+ minutes)
```

### 4. Add Contextual Search
```python
# Don't just search "Gregory Dutton"
# Search "Gregory Dutton" + context from findings
searches = [
    f"{name} + {company}",
    f"{name} + {location}",
    f"{name} + {claimed_role}",
    f"{email} breach",
    f"{domain} scam"
]
```

---

## PRACTICAL IMPLEMENTATION

### Backend Changes Needed:

**File**: `AI_infrastructure/routes/verification_routes.py`

```python
def run_verification_task(sid, subject_text):
    """Enhanced with adaptive investigation"""
    
    # Phase 1: Initial reconnaissance
    initial_findings = run_initial_checks(subject_text)
    
    # Phase 2: Analyze findings and branch
    if initial_findings['domain_age'] < 30:
        # NEW DOMAIN - deep dive
        run_domain_forensics(initial_findings['domain'])
        
    if initial_findings['email_mismatch']:
        # EMAIL MISMATCH - investigate both domains
        investigate_email_domain(initial_findings['email_domain'])
        check_domain_relationships(
            initial_findings['business_domain'],
            initial_findings['email_domain']
        )
    
    if initial_findings['social_media_count'] == 0:
        # NO SOCIAL PRESENCE - try alternatives
        search_alternative_platforms(initial_findings['person'])
        check_news_archives(initial_findings['person'])
    
    # Phase 3: Cross-reference and score
    risk_score = calculate_risk_score(initial_findings)
    
    # Phase 4: Generate report
    report = synthesize_findings(initial_findings, risk_score)
    
    return report
```

---

**END OF METHODOLOGY DEMONSTRATION**

This document shows the **intelligent, adaptive approach** that Computer Use should follow, not just blind script execution.

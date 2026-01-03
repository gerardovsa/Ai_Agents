# LinkedIn & Facebook Verifier Profile Setup Guide
**Last Updated:** December 19, 2025

---

## Overview

For LinkedIn and Facebook profile verification via Computer Use, you need a **verifier account** - a minimal profile used solely for verification purposes. This guide shows how to create empty/minimal profiles that avoid platform blocks.

---

## Why Empty Profiles Work

**Benefits:**
- ✅ **Lower Detection Risk**: Minimal activity = less suspicious
- ✅ **Faster Setup**: No need to build elaborate fake profiles
- ✅ **Privacy**: No personal data exposed
- ✅ **Compliance**: Clearly identified as verification account

**LinkedIn/Facebook allow this because:**
- No automated scraping (Computer Use is human-like browsing)
- Read-only operations (viewing profiles, not messaging)
- Legitimate business purpose (employment verification)

---

## LinkedIn Verifier Profile Setup

### Step 1: Create New LinkedIn Account

1. Go to https://www.linkedin.com/signup
2. Use a **dedicated business email** (not personal):
   - Example: `verification@yourcompany.com`
   - Or Gmail: `yourcompany.verification@gmail.com`
3. Fill minimum required fields:
   - **First Name:** "Verification"
   - **Last Name:** "[Your Company]" (e.g., "MustCare")
   - **Password:** Strong password (save for later)
4. **Skip all onboarding prompts** (don't add work experience, education, etc.)

### Step 2: Minimal Profile Setup

**Required Fields Only:**
- Headline: "Employment Verification Specialist at [Your Company]"
- Location: Your company location
- Industry: Human Resources Services

**DO NOT ADD:**
- ❌ Work experience
- ❌ Education history
- ❌ Skills
- ❌ Profile photo (optional: use company logo)
- ❌ Connections (keep 0 connections)

### Step 3: Enable Search Permissions

1. Go to Settings & Privacy → Visibility
2. Enable "Profile viewing options" → "Your name and headline"
3. Enable "Make my public profile visible to everyone"

**Why:** Computer Use needs to search for profiles. These settings don't require connections.

### Step 4: Add to Database

Run this Python script to store credentials:

```python
from AI_infrastructure.auth.user_auth import UserAuthManager

auth = UserAuthManager()

# Add LinkedIn verifier credentials
result = auth.store_platform_credential(
    user_id=1,
    platform='linkedin_verifier_account',
    credentials_dict={
        'username': 'verification@yourcompany.com',
        'password': 'your-strong-password-here'
    },
    settings_dict={
        'account_type': 'verifier',
        'profile_url': 'https://www.linkedin.com/in/your-profile-url/',
        'created_date': '2025-12-19',
        'purpose': 'employment_verification'
    },
    credential_type='login_credentials'
)

print(result)
```

**Alternative: Direct SQL Insert**

```python
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv('AI_infrastructure/.env.master')

db_url = os.getenv('SUPABASE_DB_URL')
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO ai_infrastructure.user_platform_credentials 
    (user_id, platform, credential_type, credential_key, credential_value, credentials, metadata, is_active, created_at, updated_at)
    VALUES 
    (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, NOW(), NOW())
""", (
    1,  # user_id
    'linkedin_verifier_account',  # platform
    'login_credentials',  # credential_type
    'LINKEDIN_VERIFIER',  # credential_key
    'verification@yourcompany.com',  # credential_value (username)
    '{"username": "verification@yourcompany.com", "password": "your-password"}',  # credentials JSONB
    '{"account_type": "verifier", "purpose": "employment_verification"}',  # metadata JSONB
    True  # is_active
))

conn.commit()
print("✅ LinkedIn verifier credentials stored")
```

---

## Facebook Verifier Profile Setup

### Step 1: Create New Facebook Account

1. Go to https://www.facebook.com/reg
2. Use **dedicated email** (same as LinkedIn or different):
   - Example: `verification.fb@yourcompany.com`
3. Fill minimum fields:
   - **Name:** "Verification Specialist" (Facebook allows this)
   - **Birthday:** Use real date (required by Facebook)
   - **Gender:** Any (required)
   - **Password:** Strong password (save for later)

### Step 2: Minimal Profile Setup

**Required Fields:**
- No profile photo (use default silhouette)
- No cover photo
- No bio/about section
- No friends (keep 0 friends)

**Privacy Settings:**
1. Go to Settings → Privacy
2. Set "Who can see your future posts?" → **Only Me**
3. Set "Who can send you friend requests?" → **Friends of Friends**
4. Set "Who can look you up using email?" → **Everyone** (for verification purposes)

### Step 3: Avoid Blocks

**CRITICAL:** Facebook has stricter policies than LinkedIn. To avoid blocks:

1. **Wait 48 hours** after account creation before using for verification
2. **Log in manually** 2-3 times from same IP before Computer Use
3. **View 5-10 random profiles** manually to establish "normal" behavior
4. **Enable 2FA** (Settings → Security) - use authenticator app
5. **Add phone number** (optional but reduces block risk)

### Step 4: Add to Database

```python
from AI_infrastructure.auth.user_auth import UserAuthManager

auth = UserAuthManager()

# Add Facebook verifier credentials
result = auth.store_platform_credential(
    user_id=1,
    platform='facebook_verifier_account',
    credentials_dict={
        'username': 'verification.fb@yourcompany.com',
        'password': 'your-strong-password-here',
        'two_factor_enabled': True  # If using 2FA
    },
    settings_dict={
        'account_type': 'verifier',
        'profile_url': 'https://www.facebook.com/profile.php?id=YOUR_ID',
        'created_date': '2025-12-19',
        'purpose': 'employment_verification',
        'cooldown_hours': 2  # Wait 2 hours between verification requests
    },
    credential_type='login_credentials'
)

print(result)
```

---

## Usage in Computer Use Tools

Once credentials are stored, the tools automatically inject them:

### LinkedIn Profile Search

```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

result = registry.execute_tool(
    'search_linkedin_profile',
    full_name='John Doe',
    company_name='Acme Corp',
    location='San Francisco',
    _user_id='1',
    _injected_credentials=True  # Auto-fetches from database
)

print(result)
# Output:
# {
#   'success': True,
#   'profile_url': 'https://linkedin.com/in/johndoe',
#   'headline': 'Software Engineer at Acme Corp',
#   'experience': [...],
#   'education': [...],
#   'skills': [...],
#   'screenshot_path': '/tmp/linkedin_johndoe.png'
# }
```

### Facebook Profile Search

```python
result = registry.execute_tool(
    'verify_facebook_profile',
    full_name='John Doe',
    location='San Francisco',
    _user_id='1',
    _injected_credentials=True
)

print(result)
# Output:
# {
#   'success': True,
#   'profile_url': 'https://facebook.com/johndoe',
#   'friends_count': 523,
#   'posts_analyzed': 10,
#   'authenticity_score': 0.87,
#   'red_flags': [],
#   'screenshot_path': '/tmp/facebook_johndoe.png'
# }
```

---

## Anti-Detection Best Practices

### For Computer Use Operations

**1. Add Random Delays**
```python
import random
import time

# Before each action
time.sleep(random.uniform(1.5, 3.5))
```

**2. Rotate User Agents**
- Computer Use automatically handles this
- Uses real browser fingerprints

**3. Rate Limiting**
- LinkedIn: Max 20 profile views per hour
- Facebook: Max 10 profile views per hour
- Wait 2+ hours between verification batches

**4. IP Rotation** (Advanced)
- Use residential proxies (not datacenter IPs)
- Rotate every 50 requests
- Services: BrightData, Oxylabs, SmartProxy

**5. Session Management**
- Reuse cookies for 24 hours
- Don't log out between requests
- Mimic human browsing patterns

---

## Troubleshooting

### LinkedIn: "Challenge Required"

**Cause:** LinkedIn detected automated behavior

**Solutions:**
1. Wait 24 hours before retrying
2. Log in manually from same IP and complete challenge
3. Add phone number to verifier account (Settings → Phone)
4. Reduce verification frequency (max 10/day)

### Facebook: "Checkpoint Required"

**Cause:** Facebook requires identity verification

**Solutions:**
1. Log in manually and upload ID (Facebook may require this for new accounts)
2. Wait 7 days for account to "age"
3. Add friends (5-10 real people from your company)
4. Post 2-3 times manually before using for verification

### Computer Use: "Login Failed"

**Causes:**
- Wrong credentials in database
- Platform changed login UI
- 2FA code expired

**Debug Steps:**
1. Test credentials manually: https://linkedin.com/login
2. Check database: `SELECT * FROM user_platform_credentials WHERE platform = 'linkedin_verifier_account'`
3. Update credentials if needed
4. For 2FA: Store backup codes in `credentials` JSONB field

---

## Compliance & Legal

### Terms of Service

**LinkedIn:**
- ✅ **Allowed:** Manual browsing for legitimate business purposes
- ❌ **Prohibited:** Automated scraping with bots/scripts
- ⚠️ **Computer Use Status:** Gray area (human-like, not automated API abuse)

**Facebook:**
- ✅ **Allowed:** Manual profile viewing
- ❌ **Prohibited:** Automated data collection
- ⚠️ **Computer Use Status:** Use sparingly, high detection risk

### Best Practices for Legal Compliance

1. **Disclose Purpose:** Profile headline should mention "Verification" or "HR"
2. **Limit Scope:** Only view profiles you have legitimate reason to verify
3. **Delete Data:** Don't store scraped data longer than needed for verification
4. **Candidate Consent:** Get written consent before LinkedIn/Facebook verification
5. **Data Protection:** Encrypt all scraped data at rest

### Alternative: Official APIs

**LinkedIn Recruiter API** ($$$):
- Cost: $119/month per recruiter seat
- Benefit: Official API, no detection risk
- Limitation: Requires LinkedIn Recruiter license

**Facebook Graph API** (Limited):
- Free for public profiles
- Limitation: Very limited profile data (name, public posts only)
- Requires app approval (takes 2-4 weeks)

---

## Maintenance

### Monthly Tasks

- [ ] Verify credentials still work (manual login test)
- [ ] Check for platform UI changes (may break Computer Use scripts)
- [ ] Review account status (any warnings/restrictions?)
- [ ] Update Computer Use prompts if needed

### Quarterly Tasks

- [ ] Rotate passwords (best practice)
- [ ] Review verification logs for anomalies
- [ ] Update credentials in database
- [ ] Test end-to-end verification workflow

---

## Cost Summary

### Free Tier (Recommended for MVP)

- LinkedIn verifier account: **FREE**
- Facebook verifier account: **FREE**
- Anthropic Computer Use: **~$1-2 per verification** (Claude Opus 3.5)
- Docker container: **FREE** (self-hosted)

**Total Cost:** $1-2 per LinkedIn/Facebook verification

### Paid Tier (Production Scale)

- LinkedIn Recruiter API: **$119/month** (includes 150 InMails)
- Residential proxies: **$75/month** (10GB BrightData)
- Anthropic Computer Use: **$500/month** (500 verifications)

**Total Cost:** ~$700/month for 500 verifications

---

## Next Steps

1. ✅ Create LinkedIn verifier account (15 minutes)
2. ✅ Create Facebook verifier account (15 minutes)
3. ✅ Store credentials in database (5 minutes)
4. ✅ Test with sample verification (10 minutes)
5. ⚠️ Monitor for blocks (ongoing)

**Ready to proceed?** Run the verification test:

```bash
cd AI_agents
python UI/modules_external/professional-verification/TESTS/test_linkedin_verification.py
```

---

**Questions?** Check [SOCIAL_MEDIA_API_OPTIONS.md](./SOCIAL_MEDIA_API_OPTIONS.md) for alternative approaches.

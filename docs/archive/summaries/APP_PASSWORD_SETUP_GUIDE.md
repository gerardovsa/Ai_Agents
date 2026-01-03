# Gmail App Password Setup Guide
**Date:** October 27, 2025

## 🔐 How to Generate Gmail App Passwords

You need to generate **App Passwords** for each of your 5 Gmail accounts. Here's the step-by-step process:

---

## 📋 Prerequisites (MUST DO FIRST)

### **Step 0: Enable 2-Factor Authentication**

For EACH Gmail account, you must enable 2-Step Verification:

1. Go to: https://myaccount.google.com/security
2. Log in with the account
3. Find "2-Step Verification" section
4. Click "Get Started" or "Turn On"
5. Follow the wizard (phone verification, backup codes, etc.)

**⚠️ YOU CANNOT CREATE APP PASSWORDS WITHOUT 2FA ENABLED!**

---

## 🔑 Generate App Passwords (Do for Each Account)

### **Account 1: Personal Gmail** 
**Email:** `gpoli1982@gmail.com`

1. **Log in** to Google Account: https://myaccount.google.com
2. Go to **Security**: https://myaccount.google.com/security
3. Scroll to "2-Step Verification" → Click it
4. Scroll down to "App passwords" → Click it
   - *If you don't see "App passwords", 2FA is not enabled - go back to Step 0*
5. Click **"Select app"** → Choose **"Mail"**
6. Click **"Select device"** → Choose **"Other (Custom name)"**
7. Enter name: `AI Agent Platform`
8. Click **"Generate"**
9. **COPY THE 16-CHARACTER PASSWORD** (e.g., `abcd efgh ijkl mnop`)
   - ⚠️ Remove spaces when copying: `abcdefghijklmnop`

**Update in `.env.master`:**
```bash
PERSONAL_EMAIL_APP_PASSWORD=abcdefghijklmnop
```

---

### **Account 2: Work Email**
**Email:** `gerardo@vetsuccessacademy.com`

**Follow the same steps as Account 1:**
1. Log in to this account
2. Go to https://myaccount.google.com/security
3. 2-Step Verification → App passwords
4. Generate new password named "AI Agent Platform"
5. Copy the 16-character code

**Update in `.env.master`:**
```bash
WORK_EMAIL_APP_PASSWORD=your-new-16-char-code
```

---

### **Account 3: MiniVet Gerardo**
**Email:** `gerardo@minivetguide.com`

**Same process:**
1. Log in to this account
2. https://myaccount.google.com/security
3. App passwords → Generate
4. Name: "AI Agent Platform"
5. Copy code

**Update in `.env.master`:**
```bash
GERARDO_MVG_PASSWORD=your-new-16-char-code
```

---

### **Account 4: MiniVet Main**
**Email:** `minivetguide@gmail.com`

**Same process:**
1. Log in to this account
2. https://myaccount.google.com/security
3. App passwords → Generate
4. Name: "AI Agent Platform"
5. Copy code

**Update in `.env.master`:**
```bash
MVG_EMAIL_PASSWORD=your-new-16-char-code
```

---

### **Account 5: MiniVet Marketing**
**Email:** `marketing@minivetguide.com`

**Same process:**
1. Log in to this account
2. https://myaccount.google.com/security
3. App passwords → Generate
4. Name: "AI Agent Platform"
5. Copy code

**Update in `.env.master`:**
```bash
MVG_MARKETING_PASSWORD=your-new-16-char-code
```

---

## 📝 After Generating All Passwords

### **Your `.env.master` should look like:**

```bash
# Personal Gmail
PERSONAL_EMAIL=gpoli1982@gmail.com
PERSONAL_EMAIL_APP_PASSWORD=abcdefghijklmnop  # ← Your 16-char code

# Work Email
WORK_EMAIL=gerardo@vetsuccessacademy.com
WORK_EMAIL_APP_PASSWORD=pqrstuvwxyzabcde  # ← Your 16-char code

# MiniVet Gerardo
GERARDO_MVG_EMAIL=gerardo@minivetguide.com
GERARDO_MVG_PASSWORD=fghijklmnopqrstu  # ← Your 16-char code

# MiniVet Main
MVG_EMAIL=minivetguide@gmail.com
MVG_EMAIL_PASSWORD=vwxyzabcdefghijk  # ← Your 16-char code

# MiniVet Marketing
MVG_MARKETING_EMAIL=marketing@minivetguide.com
MVG_MARKETING_PASSWORD=lmnopqrstuvwxyza  # ← Your 16-char code
```

---

## ✅ Test Each Account

After updating passwords, test EACH account individually:

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python test_each_account.py
```

This will test each account one at a time and tell you which ones work and which need fixing.

---

## 🔍 Troubleshooting

### **"App passwords" option not showing**
- **Cause:** 2-Factor Authentication not enabled
- **Fix:** Go to https://myaccount.google.com/security → Enable 2-Step Verification first

### **"Invalid credentials" error**
- **Cause:** Wrong app password or spaces in password
- **Fix:** Copy password again, remove ALL spaces, update `.env.master`

### **"Less secure app access" message**
- **Cause:** Old Gmail security setting (deprecated)
- **Fix:** Ignore this - use App Passwords instead (requires 2FA)

### **Still not working after updating**
- **Check:** Password copied correctly (no spaces, no quotes)
- **Check:** Right password in right variable in `.env.master`
- **Check:** Saved `.env.master` file after editing
- **Restart:** Close and reopen terminal/Python to reload environment

---

## 📊 Progress Checklist

- [ ] **Account 1:** `gpoli1982@gmail.com` - 2FA enabled, app password generated
- [ ] **Account 2:** `gerardo@vetsuccessacademy.com` - 2FA enabled, app password generated
- [ ] **Account 3:** `gerardo@minivetguide.com` - 2FA enabled, app password generated
- [ ] **Account 4:** `minivetguide@gmail.com` - 2FA enabled, app password generated
- [ ] **Account 5:** `marketing@minivetguide.com` - 2FA enabled, app password generated
- [ ] **Updated** `.env.master` with all 5 app passwords
- [ ] **Tested** with `python test_each_account.py`
- [ ] **All accounts** sending emails successfully

---

## 🎯 Quick Links

- **Google Account Security:** https://myaccount.google.com/security
- **App Passwords Direct:** https://myaccount.google.com/apppasswords
- **2FA Setup:** https://myaccount.google.com/signinoptions/two-step-verification

---

**Estimated Time:** 5 minutes per account = 25 minutes total

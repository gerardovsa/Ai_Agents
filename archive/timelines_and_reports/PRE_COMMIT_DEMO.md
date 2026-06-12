# Pre-Commit Review Agent Demo

This demo shows the Pre-Commit Review Agent in action with real examples.

## 🎬 Demo Scenarios

### Scenario 1: Blocking Hardcoded API Key (CRITICAL)

**Create test file with hardcoded API key:**
```powershell
cd "c:\Users\gpoli\GIT\AI_agents"

# Create file with security issue
@"
# Test file with hardcoded API key
ANTHROPIC_API_KEY = "sk-ant-api03-abc123defgh456ijklmn789opqrst012uvwxyz345"

def test_function():
    return ANTHROPIC_API_KEY
"@ | Out-File -FilePath test_security_issue.py -Encoding utf8

# Stage the file
git add test_security_issue.py

# Try to commit (will be BLOCKED)
git commit -m "feat: add test feature"
```

**Expected Result:**
```
╔════════════════════════════════════════╗
║   PRE-COMMIT REVIEW AGENT             ║
╚════════════════════════════════════════╝

🔒 Phase 1/2: Security & Secrets Scanning...
📁 Scanning 1 staged files...

════════════════════════════════════════════════
🔒 SECURITY SCAN REPORT
════════════════════════════════════════════════

📊 Summary:
  Files scanned: 1
  Secrets found: 1
  Vulnerabilities: 0
  Overall severity: CRITICAL

🔐 Secrets Detected (1):

  🔴 ANTHROPIC_API_KEY
     File: test_security_issue.py:2
     Value: sk-ant-api03-abc123defgh...
     Fix: Move to environment variables or .env.master

❌ COMMIT BLOCKED: Critical security issues must be fixed!
   Fix the issues above and try again.

╔════════════════════════════════════════╗
║   ❌ PRE-COMMIT CHECKS FAILED         ║
╚════════════════════════════════════════╝
```

**Fix the issue:**
```powershell
# Create proper version
@"
# Test file with proper API key usage
from config import get_api_key_enhanced

def test_function():
    # ✅ Correct: Import from config
    api_key = get_api_key_enhanced('ANTHROPIC_API_KEY')
    return api_key
"@ | Out-File -FilePath test_security_issue.py -Encoding utf8

# Stage the fixed version
git add test_security_issue.py

# Commit now succeeds
git commit -m "feat: add test feature with secure API key handling"
```

**Cleanup:**
```powershell
git rm test_security_issue.py
git commit -m "chore: remove demo file"
```

---

### Scenario 2: Warning About SQL Injection (HIGH)

**Create file with SQL injection vulnerability:**
```powershell
@"
# SQL injection example
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    
    # ❌ VULNERABLE: String concatenation
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    
    return cursor.fetchone()
"@ | Out-File -FilePath test_sql.py -Encoding utf8

git add test_sql.py
git commit -m "feat: add user lookup function"
```

**Expected Result:**
```
⚠️  Vulnerabilities Detected (1):

  🔴 SQL_INJECTION
     File: test_sql.py:8
     Code: query = f"SELECT * FROM users WHERE id = {user_id}"
     Description: Possible SQL injection via string concatenation
     Fix: Use parameterized queries or prepared statements

❌ COMMIT BLOCKED: Critical security issues must be fixed!
```

**Fix:**
```powershell
@"
# Secure SQL example
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    
    # ✅ SECURE: Parameterized query
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    
    return cursor.fetchone()
"@ | Out-File -FilePath test_sql.py -Encoding utf8

git add test_sql.py
git commit -m "feat: add secure user lookup function"
```

**Cleanup:**
```powershell
git rm test_sql.py
git commit -m "chore: remove demo file"
```

---

### Scenario 3: Invalid Commit Message Format

**Try commit with invalid message:**
```powershell
# Create simple test file
echo "# Test file" | Out-File -FilePath test_msg.py -Encoding utf8
git add test_msg.py

# Try commit with bad format
git commit -m "Added new feature"
```

**Expected Result:**
```
╔════════════════════════════════════════╗
║   COMMIT MESSAGE VALIDATOR            ║
╚════════════════════════════════════════╝

════════════════════════════════════════════════
📝 COMMIT MESSAGE VALIDATION
════════════════════════════════════════════════

❌ ERRORS:

  Commit message must follow conventional commits format:
    type(scope): description
    Valid types: feat, fix, docs, style, refactor, perf, test, chore, build, ci
    Example: feat(auth): add Google OAuth integration

❌ Commit message validation failed!
   Fix the errors above and try again.
```

**Fix:**
```powershell
# Use correct format
git commit -m "feat(demo): add test feature for demonstration"

# Or with scope
git commit -m "feat(testing): add test file"
```

**Cleanup:**
```powershell
git rm test_msg.py
git commit -m "chore: remove demo file"
```

---

### Scenario 4: Large File Warning

**Create large file:**
```powershell
# Create 6MB file (triggers warning)
$content = "x" * 6000000
$content | Out-File -FilePath large_test.txt -Encoding utf8

git add large_test.txt
git commit -m "feat: add large test file"
```

**Expected Result:**
```
✨ Phase 2/2: Code Quality & Standards...

🟡 WARNING Issues (1):

  File Size: Large file: 6.0MB
     File: large_test.txt
     Fix: Consider refactoring or splitting

⚠️  9 warnings found
   Continue with commit? (y/N):
```

**Cleanup:**
```powershell
rm large_test.txt
git reset HEAD large_test.txt
```

---

### Scenario 5: Success - Everything Passes

**Create clean test file:**
```powershell
@"
"""
Test module for demonstration purposes.

This module shows proper code structure with:
- Module docstring
- Function docstrings
- Secure coding practices
"""

from config import get_api_key_enhanced


def get_anthropic_client():
    """
    Initialize Anthropic client with secure API key.
    
    Returns:
        Anthropic client instance
    """
    api_key = get_api_key_enhanced('ANTHROPIC_API_KEY')
    return api_key


def execute_secure_query(user_id):
    """
    Execute secure database query with parameterization.
    
    Args:
        user_id: ID of user to query
        
    Returns:
        User data dictionary
    """
    # Parameterized query prevents SQL injection
    query = "SELECT * FROM users WHERE id = %s"
    # ... execute query safely
    return {}
"@ | Out-File -FilePath test_clean.py -Encoding utf8

git add test_clean.py
git commit -m "feat(demo): add clean example module"
```

**Expected Result:**
```
╔════════════════════════════════════════╗
║   PRE-COMMIT REVIEW AGENT             ║
╚════════════════════════════════════════╝

🔒 Phase 1/2: Security & Secrets Scanning...
📁 Scanning 1 staged files...
✅ No security issues detected!

✨ Phase 2/2: Code Quality & Standards...
📁 Checking 1 staged files...
✅ No quality issues detected!

╔════════════════════════════════════════╗
║   ✅ ALL PRE-COMMIT CHECKS PASSED     ║
╚════════════════════════════════════════╝

╔════════════════════════════════════════╗
║   COMMIT MESSAGE VALIDATOR            ║
╚════════════════════════════════════════╝

✅ Commit message is valid!

✅ Commit message validated

[your-branch abc1234] feat(demo): add clean example module
 1 file changed, 35 insertions(+)
 create mode 100644 test_clean.py
```

**Cleanup:**
```powershell
git rm test_clean.py
git commit -m "chore: remove demo file"
```

---

## 🎓 Learning Points

### What Gets Blocked (CRITICAL)
1. ✅ Hardcoded API keys (Anthropic, OpenAI, DeepSeek, AWS, Google)
2. ✅ SQL injection vulnerabilities (string concatenation in queries)
3. ✅ Database credentials in code
4. ✅ Files larger than 10MB
5. ✅ Invalid commit message format

### What Gets Warned (HIGH)
1. ⚠️ XSS vulnerabilities (unsafe HTML rendering)
2. ⚠️ Hardcoded passwords
3. ⚠️ Private keys in code
4. ⚠️ Files larger than 5MB
5. ⚠️ Long lines (>120 characters)

### Best Practices Demonstrated
1. ✅ Import API keys from config.py using `get_api_key_enhanced()`
2. ✅ Use parameterized SQL queries with `%s` placeholders
3. ✅ Include module and function docstrings
4. ✅ Follow conventional commit format: `type(scope): description`
5. ✅ Keep files under 5MB

---

## 🚀 Try It Yourself

Run through all scenarios to see the agent in action:

```powershell
# Navigate to project
cd "c:\Users\gpoli\GIT\AI_agents"

# Run each scenario above in order
# Observe the different behaviors:
#   - Critical issues block commits
#   - High severity requires confirmation
#   - Warnings are informational
#   - Clean code passes immediately
```

---

## 📚 Next Steps

After completing the demo:
1. Read `PRE_COMMIT_REVIEW_QUICK_START.md` for daily usage
2. Review `PRE_COMMIT_REVIEW_COMPLETE.md` for full documentation
3. Share with team members
4. Customize rules in `scripts/pre_commit/` if needed

---

**Version:** 1.0.0  
**Last Updated:** November 30, 2025

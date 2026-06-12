# Pre-Commit Review Agent - Complete Guide

## 🎯 Overview

The **Pre-Commit Review Agent** is an automated code review system that runs before every Git commit to ensure code quality, security, and compliance with project standards. It prevents problematic code from entering the repository.

## 📋 What Gets Checked

### Phase 1: Security & Secrets Scanning (CRITICAL - Blocks Commit)
- ✅ **Hardcoded API Keys**: Detects Anthropic, OpenAI, DeepSeek, Google, AWS, Stripe keys
- ✅ **Secrets**: Finds passwords, JWT secrets, database URLs, private keys
- ✅ **SQL Injection**: Identifies unsafe SQL query construction
- ✅ **XSS Vulnerabilities**: Detects unsafe HTML rendering
- ✅ **Hardcoded Credentials**: Finds database connection strings with credentials

**Severity Levels:**
- 🔴 **CRITICAL**: Blocks commit immediately (hardcoded API keys, SQL injection)
- 🟡 **HIGH**: Requires confirmation to proceed (XSS, credential clusters)
- 🟠 **MEDIUM**: Warning only (potential issues)

### Phase 2: Code Quality & Standards (ERROR - Blocks Commit)
- ✅ **File Size**: Flags files >5MB, blocks >10MB
- ✅ **Line Length**: Warns about lines >120 characters
- ✅ **Imports**: Detects wildcard imports and potentially unused imports
- ✅ **Documentation**: Checks for missing docstrings in public APIs
- ✅ **Python Quality**: Runs pylint if available

### Phase 3: Commit Message Validation (WARNING - Can Override)
- ✅ **Conventional Commits**: Enforces `type(scope): description` format
- ✅ **Valid Types**: feat, fix, docs, style, refactor, perf, test, chore, build, ci
- ✅ **Length Limits**: Subject ≤72 chars, body ≤80 chars per line
- ✅ **Breaking Changes**: Requires BREAKING CHANGE footer with explanation

## 🚀 Installation

### Quick Setup (Automated)

```powershell
cd "c:\Users\gpoli\GIT\AI_agents"

# Make hooks executable (Git Bash)
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/commit-msg

# Or use PowerShell to create executable wrappers
# (Already done - pre-commit.ps1 exists)
```

### Manual Setup

The hooks are already installed in `.git/hooks/`:
- `pre-commit` - Python script that runs security + quality checks
- `commit-msg` - Python script that validates commit messages
- `pre-commit.ps1` - PowerShell wrapper (for Windows)

### Verify Installation

```powershell
# Test pre-commit hook
python .git/hooks/pre-commit

# Test commit-msg hook
echo "test: sample commit message" > test_commit.txt
python .git/hooks/commit-msg test_commit.txt
rm test_commit.txt
```

## 📖 Usage

### Normal Workflow (Hooks Run Automatically)

```powershell
# Stage your changes
git add .

# Commit (hooks run automatically)
git commit -m "feat(auth): add Google OAuth integration"

# If checks fail, fix issues and try again
# If checks pass, commit proceeds
```

### Example Output

**✅ Successful Commit:**
```
╔════════════════════════════════════════╗
║   PRE-COMMIT REVIEW AGENT             ║
╚════════════════════════════════════════╝

🔒 Phase 1/2: Security & Secrets Scanning...
📁 Scanning 5 staged files...
✅ No security issues detected!

✨ Phase 2/2: Code Quality & Standards...
📁 Checking 5 staged files...
✅ No quality issues detected!

╔════════════════════════════════════════╗
║   ✅ ALL PRE-COMMIT CHECKS PASSED     ║
╚════════════════════════════════════════╝

╔════════════════════════════════════════╗
║   COMMIT MESSAGE VALIDATOR            ║
╚════════════════════════════════════════╝

✅ Commit message is valid!
```

**❌ Failed Commit (Critical Issues):**
```
╔════════════════════════════════════════╗
║   PRE-COMMIT REVIEW AGENT             ║
╚════════════════════════════════════════╝

🔒 Phase 1/2: Security & Secrets Scanning...
📁 Scanning 3 staged files...

════════════════════════════════════════════════
🔒 SECURITY SCAN REPORT
════════════════════════════════════════════════

📊 Summary:
  Files scanned: 3
  Secrets found: 2
  Vulnerabilities: 1
  Overall severity: CRITICAL

🔐 Secrets Detected (2):

  🔴 ANTHROPIC_API_KEY
     File: config.py:45
     Value: sk-ant-api03-abc123...
     Fix: Move to environment variables or .env.master

  🔴 DATABASE_URL
     File: db_config.py:12
     Value: postgres://user:pass@...
     Fix: Move to environment variables or .env.master

❌ COMMIT BLOCKED: Critical security issues must be fixed!
   Fix the issues above and try again.

╔════════════════════════════════════════╗
║   ❌ PRE-COMMIT CHECKS FAILED         ║
╚════════════════════════════════════════╝
```

## 🔧 Bypassing Hooks (Emergency Only)

If you need to bypass the hooks (NOT recommended):

```powershell
# Skip pre-commit and commit-msg hooks
git commit --no-verify -m "emergency fix"

# Only use this for genuine emergencies!
```

## 📝 Commit Message Format

### Valid Examples

✅ **Feature:**
```
feat(auth): add Google OAuth integration

- Implement OAuth flow using google-auth-manager
- Add credential storage to oauth_tokens table
- Update frontend login component
```

✅ **Bug Fix:**
```
fix(threads): prevent duplicate thread creation

Fixed race condition in ThreadManager that caused duplicate
threads when rapidly clicking create button.
```

✅ **Breaking Change:**
```
feat(api)!: update user authentication endpoint

BREAKING CHANGE: The /api/auth/login endpoint now requires
email verification. Update all clients to use the new
/api/auth/login-verified endpoint for backward compatibility.
```

### Invalid Examples

❌ **Too vague:**
```
updated stuff
```

❌ **Wrong format:**
```
Added new feature for authentication
```

❌ **Subject too long:**
```
feat(auth): add Google OAuth integration with complete user profile sync and automatic credential refresh
```

## 🛠️ Configuration

### Adjusting Severity Levels

Edit `scripts/pre_commit/pre_commit_security_scanner.py`:

```python
# Make SQL injection warnings instead of errors
if not is_parameterized:
    self.vulnerabilities.append({
        'type': 'SQL_INJECTION',
        'severity': 'HIGH',  # Changed from 'CRITICAL'
        # ...
    })
```

### Adding Custom Patterns

Edit `scripts/pre_commit/pre_commit_security_scanner.py`:

```python
secret_patterns = {
    # Add your custom pattern
    'CUSTOM_API_KEY': r'custom-key-[a-zA-Z0-9]{32}',
    # ...
}
```

### Disabling Specific Checks

Comment out checks you don't want:

```python
def scan_all(self):
    """Run all security checks"""
    self.scan_secrets()
    # self.scan_sql_injection()  # Disabled
    self.scan_xss_vulnerabilities()
    # ...
```

## 🔍 Troubleshooting

### Hook Not Running

**Problem:** Commit proceeds without running checks

**Solution:**
```powershell
# Check if hooks are executable
ls -la .git/hooks/

# Make executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/commit-msg

# Or use PowerShell wrapper
# The pre-commit.ps1 file should work automatically
```

### Python Import Errors

**Problem:** `ModuleNotFoundError: No module named 'pre_commit_security_scanner'`

**Solution:**
```powershell
# Ensure scripts are in correct location
ls scripts/pre_commit/

# Should show:
# - pre_commit_security_scanner.py
# - code_quality_checker.py
# - commit_message_validator.py
```

### False Positives

**Problem:** Hook flags legitimate code as security issue

**Solution:**
1. Check if it's a placeholder/example (add to exclusion list)
2. Move sensitive data to `.env.master` or `config.py`
3. Add inline comment to suppress: `# nosec`
4. Bypass for this commit only: `git commit --no-verify` (not recommended)

## 📊 What Gets Blocked

### CRITICAL (Always Blocks)
- Hardcoded API keys (Anthropic, OpenAI, DeepSeek, etc.)
- SQL injection vulnerabilities
- Hardcoded database credentials
- Files >10MB

### HIGH (Requires Confirmation)
- XSS vulnerabilities
- Hardcoded passwords
- Private keys in code

### WARNING (Non-blocking)
- Long lines (>120 chars)
- Missing docstrings
- Unused imports
- Files >5MB
- Commit message format issues

## 🎯 Best Practices

### Before Committing

1. ✅ **Review your changes**: `git diff --staged`
2. ✅ **Run checks manually**: `python scripts/pre_commit/pre_commit_security_scanner.py`
3. ✅ **Write good commit message**: Follow conventional commits format
4. ✅ **Fix issues proactively**: Don't wait for hooks to catch them

### When Adding Secrets

```powershell
# ✅ DO: Use environment variables
from config import get_api_key_enhanced
api_key = get_api_key_enhanced('ANTHROPIC_API_KEY')

# ❌ DON'T: Hardcode in files
api_key = "sk-ant-api03-abc123..."  # WILL BE BLOCKED
```

### When Writing SQL

```python
# ✅ DO: Use parameterized queries
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ❌ DON'T: Use string concatenation
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # WILL BE BLOCKED
```

## 📚 Related Documentation

- `.github/prompts/Pre-Commit Review Agent.prompt.md` - Full agent prompt
- `scripts/pre_commit/` - All pre-commit scripts
- `.git/hooks/` - Git hook implementations

## 🚨 Emergency Procedures

### Critical Production Issue (Need to bypass)

```powershell
# 1. Document reason
echo "EMERGENCY BYPASS: Production auth server down" > EMERGENCY.txt

# 2. Commit with bypass
git commit --no-verify -m "fix: emergency auth server hotfix"

# 3. Create follow-up task to fix properly
git commit -m "chore: add TODO for proper auth fix"
```

### Rollback Bad Commit

```powershell
# Undo last commit (keep changes staged)
git reset --soft HEAD~1

# Fix issues
# ... make corrections ...

# Re-commit (hooks will run again)
git commit -m "fix: corrected security issues"
```

## 📈 Success Metrics

After enabling pre-commit hooks, you should see:
- ✅ **Zero hardcoded secrets** in committed code
- ✅ **Consistent commit message format** across team
- ✅ **Reduced code review time** (basic issues caught early)
- ✅ **Fewer security vulnerabilities** in production

## 🤝 Team Adoption

### Onboarding New Developers

1. Share this guide: `PRE_COMMIT_REVIEW_COMPLETE.md`
2. Have them test hooks: `git commit -m "test: verify hooks work"`
3. Review first few commits together
4. Adjust configuration based on team feedback

### Common Questions

**Q: Can I disable hooks locally?**
A: Yes, but not recommended. Use `git commit --no-verify` sparingly.

**Q: What if hooks are too strict?**
A: Adjust severity levels in scanner scripts or discuss with team.

**Q: Do hooks run on merge commits?**
A: Yes, pre-commit runs but commit-msg is skipped for merges.

---

**Last Updated:** November 30, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

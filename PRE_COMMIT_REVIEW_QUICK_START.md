# Pre-Commit Review Agent - Quick Start

## 🚀 5-Minute Setup

### Step 1: Verify Installation
```powershell
cd "c:\Users\gpoli\GIT\AI_agents"

# Check hooks exist
ls .git/hooks/ | Select-String "pre-commit|commit-msg"
```

**Expected output:**
```
pre-commit
pre-commit.ps1
commit-msg
```

### Step 2: Make Hooks Executable (Windows)
```powershell
# Already done! PowerShell wrapper (pre-commit.ps1) handles execution
# No additional setup needed on Windows
```

### Step 3: Test the Hooks
```powershell
# Create test file with intentional issue
echo "api_key = 'sk-ant-api03-test123456789'" > test_security.py
git add test_security.py

# Try to commit (should be BLOCKED)
git commit -m "test: security check"

# Clean up
git reset HEAD test_security.py
rm test_security.py
```

**Expected:** Commit blocked with security warning about hardcoded API key ✅

### Step 4: Test Valid Commit
```powershell
# Create safe test file
echo "# Safe test file" > test_safe.py
git add test_safe.py

# Commit with valid message
git commit -m "test: verify hooks work correctly"

# Clean up
git rm test_safe.py
git commit -m "chore: remove test file"
```

**Expected:** Commit succeeds ✅

## 📝 Commit Message Cheat Sheet

### Format
```
type(scope): short description

Optional longer description explaining the change.

BREAKING CHANGE: explanation (if applicable)
```

### Valid Types
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style (formatting, no logic change)
- `refactor` - Code restructuring
- `perf` - Performance improvement
- `test` - Adding/updating tests
- `chore` - Maintenance tasks
- `build` - Build system changes
- `ci` - CI/CD changes

### Examples

✅ **Simple feature:**
```
feat(auth): add Google OAuth support
```

✅ **Bug fix with scope:**
```
fix(threads): prevent duplicate thread creation
```

✅ **Documentation:**
```
docs(readme): update installation instructions
```

✅ **Breaking change:**
```
feat(api)!: change authentication endpoint

BREAKING CHANGE: /api/auth/login now requires email verification
```

## 🔒 What Gets Checked

### CRITICAL (Blocks Commit)
- 🔴 Hardcoded API keys (Anthropic, OpenAI, DeepSeek, AWS, Google)
- 🔴 SQL injection vulnerabilities
- 🔴 Database credentials in code
- 🔴 Files larger than 10MB

### HIGH (Asks for Confirmation)
- 🟡 XSS vulnerabilities
- 🟡 Hardcoded passwords
- 🟡 Private keys

### WARNING (Non-blocking)
- 🟠 Long lines (>120 characters)
- 🟠 Missing docstrings
- 🟠 Unused imports

## 🛠️ Common Issues & Fixes

### Issue: "API key detected in config.py"
**Fix:** This is expected - config.py is excluded from checks
```python
# ✅ Correct: Import from config
from config import get_api_key_enhanced
api_key = get_api_key_enhanced('ANTHROPIC_API_KEY')

# ❌ Wrong: Hardcode in other files
api_key = "sk-ant-..."  # BLOCKED
```

### Issue: "SQL injection detected"
**Fix:** Use parameterized queries
```python
# ✅ Correct: Parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ❌ Wrong: String concatenation
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # BLOCKED
```

### Issue: "Commit message format invalid"
**Fix:** Use conventional commits format
```bash
# ✅ Correct format
git commit -m "feat(module): add new feature"

# ❌ Wrong format
git commit -m "Added new feature"  # BLOCKED
```

### Issue: "File too large"
**Fix:** Use Git LFS or split file
```powershell
# For large files, use Git LFS
git lfs install
git lfs track "*.large"
git add .gitattributes
git add large_file.large
git commit -m "feat: add large file via LFS"
```

## 🚨 Emergency Bypass (Use Sparingly)

If you absolutely must bypass the hooks:

```powershell
# Skip ALL hooks
git commit --no-verify -m "fix: emergency production hotfix"

# ⚠️ WARNING: Only use for genuine emergencies!
# Create follow-up ticket to fix properly
```

## 📊 Quick Test Checklist

Before committing, verify:
- [ ] No hardcoded API keys or secrets
- [ ] SQL queries use parameterized statements
- [ ] HTML rendering is sanitized (no XSS)
- [ ] Files are <5MB (preferably)
- [ ] Commit message follows `type(scope): description` format
- [ ] Public functions have docstrings

## 🎯 Daily Workflow

```powershell
# 1. Make changes
code AI_infrastructure/routes/my_feature.py

# 2. Stage changes
git add AI_infrastructure/routes/my_feature.py

# 3. Commit (hooks run automatically)
git commit -m "feat(routes): add my new feature"

# 4. If hooks fail, fix and retry
# - Read error messages
# - Fix the issues
# - Try commit again

# 5. Push when ready
git push origin your-branch
```

## 📚 Full Documentation

For complete details, see: `PRE_COMMIT_REVIEW_COMPLETE.md`

## 🤝 Getting Help

If hooks are blocking legitimate code:
1. Read the error message carefully
2. Check `PRE_COMMIT_REVIEW_COMPLETE.md` troubleshooting section
3. Adjust configuration in `scripts/pre_commit/` if needed
4. Ask team for guidance

---

**Quick Links:**
- Full Guide: `PRE_COMMIT_REVIEW_COMPLETE.md`
- Scripts: `scripts/pre_commit/`
- Hooks: `.git/hooks/`
- Agent Prompt: `.github/prompts/Pre-Commit Review Agent.prompt.md`

**Version:** 1.0.0  
**Last Updated:** November 30, 2025

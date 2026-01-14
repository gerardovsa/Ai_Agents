# Pre-Commit Scripts

This folder contains the core Python scripts that power the Pre-Commit Review Agent.

## 📁 Files

### Core Scanners

**`pre_commit_security_scanner.py`** (Main Security Scanner)
- Detects hardcoded API keys (Anthropic, OpenAI, DeepSeek, AWS, Google, Stripe, etc.)
- Finds secrets (passwords, JWT secrets, database URLs, private keys)
- Identifies SQL injection vulnerabilities
- Detects XSS vulnerabilities
- Scans for hardcoded database credentials
- Exit codes:
  - `0` = No issues or low severity
  - `1` = Critical or high severity issues found

**`code_quality_checker.py`** (Code Quality Scanner)
- Checks Python code quality with pylint (if available)
- Flags excessively large files (>5MB warning, >10MB error)
- Detects long lines (>120 characters)
- Identifies problematic imports (wildcards, unused)
- Checks for missing documentation (docstrings)
- Exit codes:
  - `0` = No errors
  - `1` = Quality errors found

**`commit_message_validator.py`** (Commit Message Validator)
- Enforces Conventional Commits format: `type(scope): description`
- Validates commit types: feat, fix, docs, style, refactor, perf, test, chore, build, ci
- Checks subject line length (≤72 chars)
- Validates body format and line length (≤80 chars)
- Requires BREAKING CHANGE footer for breaking changes
- Exit codes:
  - `0` = Valid commit message
  - `1` = Invalid commit message

## 🔧 Usage

### Manual Execution

```powershell
cd "c:\Users\gpoli\GIT\AI_agents"

# Run security scanner on staged files
python scripts/pre_commit/pre_commit_security_scanner.py

# Run quality checker on staged files
python scripts/pre_commit/code_quality_checker.py

# Validate commit message
echo "feat(auth): add OAuth support" > test_msg.txt
python scripts/pre_commit/commit_message_validator.py test_msg.txt
rm test_msg.txt
```

### Automatic Execution

These scripts run automatically via Git hooks:
- `.git/hooks/pre-commit` calls security scanner and quality checker
- `.git/hooks/commit-msg` calls commit message validator

## 📊 Output Format

### Security Scanner Output

```
════════════════════════════════════════════════
🔒 SECURITY SCAN REPORT
════════════════════════════════════════════════

📊 Summary:
  Files scanned: 5
  Secrets found: 1
  Vulnerabilities: 0
  Overall severity: CRITICAL

🔐 Secrets Detected (1):

  🔴 ANTHROPIC_API_KEY
     File: test.py:45
     Value: sk-ant-api03-abc123...
     Fix: Move to environment variables or .env.master
```

### Quality Checker Output

```
════════════════════════════════════════════════
✨ CODE QUALITY REPORT
════════════════════════════════════════════════

📊 Summary:
  Files checked: 8
  Total issues: 3
  Errors: 0
  Warnings: 3
  Info: 0

🟡 WARNING Issues (3):

  Line Length: Line too long: 125 characters (max 120)
     File: routes/agent_routes.py
     Line: 456
     Fix: Break into multiple lines
```

### Commit Message Validator Output

```
════════════════════════════════════════════════
📝 COMMIT MESSAGE VALIDATION
════════════════════════════════════════════════

✅ Commit message is valid!
```

## 🎨 Customization

### Adding New Secret Patterns

Edit `pre_commit_security_scanner.py`:

```python
secret_patterns = {
    # Add your pattern
    'MY_CUSTOM_KEY': r'mykey-[a-zA-Z0-9]{32}',
    # ...
}
```

### Adjusting Severity Levels

Edit any scanner to change severity:

```python
self.issues.append({
    'severity': 'WARNING',  # Change from 'ERROR'
    # ...
})
```

### Disabling Specific Checks

Comment out checks you don't need:

```python
def scan_all(self):
    self.scan_secrets()
    # self.scan_sql_injection()  # Disabled
    self.scan_xss_vulnerabilities()
```

## 🔍 Testing

Test individual scanners:

```powershell
# Test security scanner with test file
echo "api_key = 'sk-ant-test123'" > test.py
git add test.py
python scripts/pre_commit/pre_commit_security_scanner.py
git reset HEAD test.py
rm test.py

# Test quality checker with large file
# (create a file >120 chars per line)

# Test commit message validator
echo "invalid commit message" > test_msg.txt
python scripts/pre_commit/commit_message_validator.py test_msg.txt
rm test_msg.txt
```

## 📚 Dependencies

**Required:**
- Python 3.8+
- Git

**Optional (for enhanced features):**
- `pylint` - For Python code quality analysis
- `radon` - For complexity analysis

Install optional dependencies:
```powershell
pip install pylint radon
```

## 🔗 Integration

These scripts are called by Git hooks:
- `.git/hooks/pre-commit` - Python hook calling security + quality scanners
- `.git/hooks/commit-msg` - Python hook calling message validator
- `.git/hooks/pre-commit.ps1` - PowerShell wrapper (Windows)

## 📖 Documentation

- `PRE_COMMIT_REVIEW_COMPLETE.md` - Full user guide
- `PRE_COMMIT_REVIEW_QUICK_START.md` - Quick start guide
- `.github/prompts/Pre-Commit Review Agent.prompt.md` - AI agent prompt

## 🐛 Troubleshooting

### Scripts Not Found

Ensure you're in the project root:
```powershell
cd "c:\Users\gpoli\GIT\AI_agents"
```

### Import Errors

Scripts add themselves to Python path automatically, but if issues persist:
```powershell
$env:PYTHONPATH = "scripts/pre_commit;$env:PYTHONPATH"
```

### Hooks Not Running

Hooks must be executable (handled by PowerShell wrapper on Windows):
```bash
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/commit-msg
```

## 🚀 Performance

- **Security scanner**: ~100-200ms per file
- **Quality checker**: ~50-100ms per file
- **Message validator**: <10ms

Total pre-commit time for typical commit (5 files): **1-2 seconds**

## 🔐 Security

These scripts:
- ✅ Only read files, never modify
- ✅ Don't send data over network
- ✅ Don't store sensitive information
- ✅ Run locally on your machine

## 📝 Maintenance

To update scanners:
1. Edit the relevant Python file
2. Test manually: `python scripts/pre_commit/<scanner>.py`
3. Test via commit: `git commit -m "test: verify changes"`
4. Update documentation if behavior changes

---

**Version:** 1.0.0  
**Last Updated:** November 30, 2025  
**Maintained By:** AI Agents Team

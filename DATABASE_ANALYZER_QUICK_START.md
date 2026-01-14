# Database Analyzer - Quick Start Guide 🚀

**Script:** `data/show_database_structure_enhanced.py`  
**Purpose:** Keep codebase connected to database schema  
**Status:** ✅ ALL 5 PHASES COMPLETE (including Phase 5 Real-Time Checks)

---

## ⚡ Quick Commands

### Run Full Analysis (Phases 1-5)
```powershell
# Install dependencies first time only
pip install -r data\requirements_analyzer.txt
playwright install chromium

# Start server (required for Phase 5)
BISTART  # Terminal 1

# Run analyzer
cd c:\Users\gpoli\GIT\AI_agents
python data\show_database_structure_enhanced.py  # Terminal 2
```

### Run Static Analysis Only (Phases 1-4, faster)
```powershell
# Don't install Playwright - Phase 5 auto-skips
cd c:\Users\gpoli\GIT\AI_agents
python data\show_database_structure_enhanced.py
```

### View Report
```powershell
notepad data\database_analysis_report_enhanced.txt
```

### Enable Supabase Analysis
```powershell
# Add to .env.master
SUPABASE_DB_URL=postgresql://postgres:[password]@[host]:5432/postgres
```

---

## 🎯 What It Checks

### ✅ Phase 1: Supabase PostgreSQL Analysis
**Maps complete database schema:**
- 5 schemas, 47 tables
- Columns, types, constraints
- Row counts, sample data

### ✅ Phase 2: Connection Manager Validation
**Prevents your Nov 24 fix from regressing:**
- ❌ Detects duplicate `createClient()` calls
- ❌ Finds direct channel subscriptions
- ✅ Confirms singleton pattern usage

**Example Output:**
```
CONNECTION MANAGER VALIDATION
✅ All files use connection manager correctly!
✅ 18 files using connection manager
```

### ✅ Phase 3: Schema Consistency
**Prevents "table not found" errors:**
- 🔍 Missing tables (code references non-existent tables)
- 🔍 Orphaned tables (tables exist but never used)
- 🔍 Invalid column references

**Example Output:**
```
SCHEMA CONSISTENCY CHECKS
🔴 [HIGH] users_backup
   File: routes/cleanup.py
   Code references table 'users_backup' not found in Supabase
```

### ✅ Phase 4: CI/CD Integration
**Automated testing:**
- GitHub Actions workflow
- Pre-commit hooks
- Automated reporting

### ✅ Phase 5: Real-Time Health Checks (NEW!)
**Browser-based runtime testing:**
- ✅ Singleton pattern validation at runtime
- ✅ WebSocket connection counting (expect 1)
- ✅ Channel deduplication testing
- ✅ Network resilience simulation
- ✅ Memory leak detection

**Example Output:**
```
REAL-TIME HEALTH CHECKS (PHASE 5)
✅ Overall Status: PASSED

✅ Test 1: Singleton Pattern - PASSED
   Duplicate warnings: 0
   Client instances: 1

✅ Test 2: WebSocket Connections - PASSED
   Connection count: 1 (expected: 1)
```

**Requires:** Playwright installed + UI running on localhost:5001

### ✅ SQLite Analysis (Original)
**Validates local databases:**
- All .db files in data/ folder
- Script usage patterns
- API route mappings
- Database inconsistencies

---

## 📊 Understanding the Output

### Section 1: Supabase PostgreSQL Schemas (Phase 1)
Shows complete structure of production database:
- Tables, columns, types
- Primary keys, foreign keys
- Row counts, sample data

**Skip this if:** SUPABASE_DB_URL not set (shows warning instead)

### Section 2: Connection Manager Validation (Phase 2)
**THIS IS CRITICAL** - Validates your recent Supabase fix:
- `✅ All files use connection manager correctly!` = GOOD
- `❌ Found X issues` = FIX THESE IMMEDIATELY

### Section 3: Schema Consistency Checks (Phase 3)
Finds code-to-database mismatches:
- **MISSING_TABLE** = Code references non-existent table (HIGH severity)
- **ORPHANED_TABLE** = Table exists but never used (LOW severity)

### Section 4: Real-Time Health Checks (Phase 5)
**NEW:** Browser-based runtime testing:
- `✅ Overall Status: PASSED` = All tests passed
- `⚠️ Overall Status: WARNING` = Minor issues (review details)
- `❌ Overall Status: FAILED` = Critical issues (DO NOT DEPLOY)

**5 Tests Run:**
1. **Singleton Pattern** - Detects duplicate client creation at runtime
2. **WebSocket Connections** - Validates single connection (not multiple)
3. **Channel Management** - Tests deduplication and cleanup
4. **Network Resilience** - Simulates offline/online reconnection
5. **Memory Usage** - Detects memory leaks from unreleased channels

**Skipped if:** Playwright not installed or UI not running

### Section 5-7: SQLite Analysis (Original)
Original functionality (preserved):
- SQLite database structure
- Script usage analysis
- API route mapping

---

## 🚨 When to Run This

### Development (Fast - Phases 1-4 only)
**5-8 seconds, static analysis only:**
```powershell
# Don't install Playwright - Phase 5 auto-skips
python data\show_database_structure_enhanced.py
```

**Use for:**
- Quick validation during coding
- Before every commit
- After schema changes

### Pre-Deployment (Complete - All 5 Phases)
**25-30 seconds, includes browser testing:**
```powershell
# Install Playwright first time only
pip install playwright
playwright install chromium

# Start server
BISTART  # Terminal 1

# Run full analysis
python data\show_database_structure_enhanced.py  # Terminal 2
```

**Use for:**
- Before deployments (CRITICAL)
- Weekly health checks
- After connection manager changes
- Investigating production issues

### CI/CD (Automated - All 5 Phases)
**Already configured in `.github/workflows/database-checks.yml`:**
- Runs on every push to main
- Installs Playwright automatically
- Starts test server
- Executes full analysis
- Fails build if issues found

### After Schema Changes (Required)
Run complete analysis (Phases 1-5) when:
- Added/removed tables in Supabase
- Changed column names/types
- Modified foreign keys
- Updated connection manager logic

---

## 🔥 Common Issues & Fixes

### Issue: "psycopg2 not available"
```powershell
pip install psycopg2-binary
# Or install all at once:
pip install -r data\requirements_analyzer.txt
```

### Issue: "Playwright not installed"
```
⚠️  Real-time checks skipped: Playwright not installed
```

**Expected:** Phase 5 skipped, Phases 1-4 still run  
**Fix (to enable Phase 5):**
```powershell
pip install playwright
playwright install chromium
```

### Issue: "SUPABASE_DB_URL not set"
**Expected:** Supabase analysis skipped, SQLite still works  
**Fix:** Add to `.env.master`:
```
SUPABASE_DB_URL=postgresql://...
```

### Issue: "Connection refused" (Phase 5)
```
❌ Real-time checks failed: net::ERR_CONNECTION_REFUSED
```

**Cause:** UI server not running  
**Fix:**
```powershell
BISTART  # Start server first
python data\show_database_structure_enhanced.py  # Then run analyzer
```

### Issue: Found duplicate client creation (Phase 2)
**Example:**
```
🔴 [HIGH] DUPLICATE_CLIENT
   File: UI/modules/old-module.js
   Line: 42
```

**Fix:**
```javascript
// WRONG - Bypasses singleton
const supabase = createClient(url, key);

// RIGHT - Uses connection manager
const supabase = await connectionManager.getClient();
```

### Issue: Missing table reference
**Example:**
```
🔴 [HIGH] MISSING_TABLE
   Table: sessions.archived_threads
   File: routes/archive_routes.py
```

**Fix:**
1. Check if table exists: `SELECT * FROM sessions.archived_threads LIMIT 1`
2. If missing: Create table or update code reference
3. If typo: Fix table name in code

### Issue: 300+ SQLite issues found
**Expected:** Many archived scripts reference old paths  
**Safe to ignore:** Issues in `archive/` folder  
**Action needed:** Only fix issues in active code

---

## 🎯 Success Criteria

**Good Output (Everything Working):**
```
✅ Connected to Supabase PostgreSQL
✅ All files use connection manager correctly!
✅ No consistency issues found!
⚠️  Found 10 total issues (all in archived scripts)
```

**Needs Attention:**
```
❌ Found 2 connection manager violations
🔴 [HIGH] DUPLICATE_CLIENT in UI/modules/...
```
→ Fix connection manager issues IMMEDIATELY

```
❌ Found 3 missing tables
🔴 [HIGH] Code references 'users_backup' not found
```
→ Fix table references or create missing tables

---

## 📚 Related Files

**Enhanced Script:**
- `data/show_database_structure_enhanced.py` - Run this

**Output:**
- `data/database_analysis_report_enhanced.txt` - Review this

**Documentation:**
- `DATABASE_ANALYZER_ENHANCED_COMPLETE.md` - Full guide
- `SUPABASE_CONNECTION_FIX_COMPLETE_NOV24.md` - Your Nov 24 fix
- `SUPABASE_QUICK_REFERENCE.md` - Connection health monitoring

---

## 💡 Pro Tips

1. **Run after pulling code:**
   ```powershell
   git pull; python data\show_database_structure_enhanced.py
   ```

2. **Diff reports to track changes:**
   ```powershell
   # Save baseline
   cp data\database_analysis_report_enhanced.txt reports\baseline.txt
   
   # Later: Compare
   diff reports\baseline.txt data\database_analysis_report_enhanced.txt
   ```

3. **Focus on active code:**
   - Ignore issues in `archive/` folder
   - Fix issues in `AI_infrastructure/`, `tools/`, `UI/`

4. **Use grep to find specific issues:**
   ```powershell
   # Find all CRITICAL issues
   Select-String "CRITICAL" data\database_analysis_report_enhanced.txt
   
   # Find connection manager violations
   Select-String "DUPLICATE_CLIENT" data\database_analysis_report_enhanced.txt
   ```

5. **Integrate with CI/CD:**
   - See full guide: `DATABASE_ANALYZER_ENHANCED_COMPLETE.md`
   - GitHub Actions workflow included
   - Pre-commit hook template included

---

## 🚀 Next Steps

1. **Set SUPABASE_DB_URL** (if not already):
   ```
   SUPABASE_DB_URL=postgresql://...
   ```

2. **Run full analysis:**
   ```powershell
   python data\show_database_structure_enhanced.py
   ```

3. **Review report** for issues:
   ```powershell
   notepad data\database_analysis_report_enhanced.txt
   ```

4. **Fix any HIGH severity issues** found

5. **Commit changes:**
   ```powershell
   git add data/show_database_structure_enhanced.py
   git add DATABASE_ANALYZER_*.md
   git commit -m "feat: Enhanced database analyzer with Supabase validation"
   ```

---

**Last Updated:** November 24, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅

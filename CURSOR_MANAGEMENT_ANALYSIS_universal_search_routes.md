# Cursor Management Analysis: universal_search_routes.py
**Date:** December 8, 2025  
**File:** `AI_infrastructure/routes/universal_search_routes.py`  
**Lines:** 1,289  
**Status:** ⚠️ **CRITICAL ISSUES FOUND**

---

## 🎯 Analysis Against Success Criteria

### ✅ PASS: Cursor initialized as None before try block
**Status:** ✅ **PERFECT**

All functions properly initialize cursors:
```python
# Line 155-156 (search endpoint)
cursor = None  # ✅ Initialize cursor before try
conn = None    # ✅ Initialize connection before try

# Line 972-973 (facets endpoint)
cursor = None  # ✅ Initialize cursor before try
conn = None    # ✅ Initialize connection before try

# Line 1122-1123 (index-messages endpoint)
cursor = None  # ✅ Initialize cursor before try
conn = None    # ✅ Initialize connection before try

# Line 1218-1219 (index-synergy endpoint)
cursor = None  # ✅ Initialize cursor before try
conn = None    # ✅ Initialize connection before try
```

---

### ❌ FAIL: Cursor closed exactly ONCE before function exit
**Status:** ❌ **CRITICAL ISSUE - DOUBLE CLOSE**

**Problem:** Main search endpoint closes cursor TWICE:
1. **Line 514-518:** Manual close in try block
2. **Line 944-954:** Finally block close

```python
# FIRST CLOSE (Line 514-518) - IN TRY BLOCK
if cursor:
    cursor.close()
    cursor = None
if conn:
    conn.close()
    conn = None

# ... more code (external API calls) ...

# SECOND CLOSE (Line 944-954) - IN FINALLY BLOCK
finally:
    if cursor:
        try:
            cursor.close()  # ❌ CURSOR ALREADY CLOSED!
        except:
            pass
    if conn:
        try:
            conn.close()  # ❌ CONNECTION ALREADY CLOSED!
        except:
            pass
```

**Why This Is Dangerous:**
- Sets `cursor = None` after first close
- Finally block won't try to close again (if cursor check passes)
- BUT: If exception occurs between lines 514-944, cursor could be closed twice
- Try/except in finally masks the error, but wastes resources

---

### ❌ FAIL: InHousePrint missing finally block
**Status:** ❌ **CRITICAL ISSUE - RESOURCE LEAK**

**Problem:** InHousePrint SQL Server connection has no cleanup on exception

```python
# Line 637-732 (InHousePrint search section)
if include_inhouseprint:
    try:
        import pymssql
        
        # Connect to InHousePrint SQL Server
        inhouse_conn = pymssql.connect(...)  # ❌ No initialization before try!
        inhouse_cursor = inhouse_conn.cursor(as_dict=True)  # ❌ No initialization!
        
        # ... queries ...
        
        inhouse_cursor.close()  # ✅ Manual close
        inhouse_conn.close()    # ✅ Manual close
        
    except Exception as e:
        # ❌ NO FINALLY BLOCK - CURSORS NOT CLOSED ON EXCEPTION!
        print(f"[UNIVERSAL SEARCH] InHousePrint search error: {e}")
        results['sources']['inhouseprint'] = {'error': str(e)}
```

**Consequences:**
- If ANY exception occurs during InHousePrint queries:
  - `inhouse_cursor` NOT closed → pymssql cursor leak
  - `inhouse_conn` NOT closed → SQL Server connection leak
  - Repeated failures = connection pool exhaustion
  - SQL Server eventually refuses new connections

---

### ✅ PASS: Functions have finally blocks (mostly)
**Status:** ⚠️ **3 of 4 endpoints have finally blocks**

**Functions WITH finally blocks:**
1. ✅ `/search` endpoint (Line 944-954)
2. ✅ `/facets` endpoint (Line 1036-1046)
3. ✅ `/index-messages` endpoint (Line 1190-1200)
4. ✅ `/index-synergy` endpoint (Line 1276-1286)

**Code sections WITHOUT finally blocks:**
1. ❌ InHousePrint search (nested try/except, no finally)

---

### ❌ FAIL: Early returns close cursor first
**Status:** ⚠️ **NO EARLY RETURNS, BUT DUAL CLOSE ISSUE**

**Analysis:**
- No early returns found in main search function
- However, cursor closed in middle of function (Line 514)
- Then external API calls continue without cursor
- Finally block tries to close again

**Correct Pattern Should Be:**
- Keep cursor open until ALL database operations complete
- Close in finally block ONLY
- External API calls don't need cursor, but shouldn't close it mid-function

---

### ✅ PASS: Exception paths close cursor (via finally)
**Status:** ⚠️ **PARTIAL - InHousePrint fails this**

**Functions that handle exceptions correctly:**
1. ✅ Main search endpoint - finally block catches all exceptions
2. ✅ Facets endpoint - finally block catches all exceptions
3. ✅ Index-messages endpoint - finally block catches all exceptions
4. ✅ Index-synergy endpoint - finally block catches all exceptions

**Code sections that FAIL:**
1. ❌ InHousePrint search - no finally block for cleanup

---

### ✅ PASS: Connections closed AFTER cursors
**Status:** ✅ **PERFECT**

All cleanup code follows correct order:
```python
# Correct pattern used everywhere:
cursor.close()
cursor = None
conn.close()
conn = None
```

---

## 🔴 Critical Issues Summary

### Issue 1: Double Close in Main Search Endpoint
**Severity:** 🔴 **HIGH**  
**Location:** Lines 514-518 AND 944-954  
**Problem:** Cursor/connection closed twice (once in try, once in finally)

**Current Code:**
```python
# Line 514-518 (AFTER Vector DB search, BEFORE external APIs)
if cursor:
    cursor.close()
    cursor = None
if conn:
    conn.close()
    conn = None

# Line 520-930: External API calls (Gmail, Slack, Xero, Drive, etc.)
# These don't need cursor/connection

# Line 944-954: Finally block ALSO tries to close
finally:
    if cursor:
        try:
            cursor.close()  # Won't execute (cursor=None already)
        except:
            pass
```

**Why This Exists:**
- Original code closed cursor after database operations (Line 514)
- External API calls don't use database
- Finally block added later for safety
- Resulted in redundant cleanup

**Fix Required:**
- Remove manual close at Line 514-518
- Let finally block handle ALL cleanup
- Cursor/connection stay open (but unused) during API calls
- No functional impact (API calls are independent)

---

### Issue 2: InHousePrint Missing Finally Block
**Severity:** 🔴 **CRITICAL**  
**Location:** Lines 637-732  
**Problem:** SQL Server connection leak on exception

**Current Code:**
```python
if include_inhouseprint:
    try:
        inhouse_conn = pymssql.connect(...)  # ❌ Leak if exception!
        inhouse_cursor = inhouse_conn.cursor(as_dict=True)
        
        # Queries...
        
        inhouse_cursor.close()  # Only reached if NO exception
        inhouse_conn.close()
        
    except Exception as e:
        # ❌ Cursor/connection NOT closed here!
        results['sources']['inhouseprint'] = {'error': str(e)}
```

**Consequences:**
- Network error → connection leak
- SQL syntax error → cursor leak
- Permission error → connection leak
- After ~50 failures → SQL Server refuses new connections

**Fix Required:**
```python
if include_inhouseprint:
    inhouse_cursor = None  # ✅ Initialize BEFORE try
    inhouse_conn = None
    try:
        inhouse_conn = pymssql.connect(...)
        inhouse_cursor = inhouse_conn.cursor(as_dict=True)
        
        # Queries...
        
        results['sources']['inhouseprint'] = {
            'count': len(inhouse_results),
            'results': inhouse_results[:limit]
        }
        results['total_results'] += len(inhouse_results)
        
    except Exception as e:
        print(f"[UNIVERSAL SEARCH] InHousePrint search error: {e}")
        results['sources']['inhouseprint'] = {'error': str(e)}
    finally:
        # ✅ Guaranteed cleanup
        if inhouse_cursor:
            try:
                inhouse_cursor.close()
            except:
                pass
        if inhouse_conn:
            try:
                inhouse_conn.close()
            except:
                pass
```

---

## 📋 Complete Issues List

| # | Issue | Severity | Line(s) | Fix Required |
|---|-------|----------|---------|--------------|
| 1 | Double close in main search | 🔴 HIGH | 514-518, 944-954 | Remove manual close at 514-518 |
| 2 | InHousePrint no finally block | 🔴 CRITICAL | 637-732 | Add finally block with cleanup |
| 3 | InHousePrint cursor not initialized | 🟡 MEDIUM | 637 | Add `inhouse_cursor = None` before try |
| 4 | InHousePrint conn not initialized | 🟡 MEDIUM | 637 | Add `inhouse_conn = None` before try |

---

## ✅ What's Working Correctly

### Excellent Patterns Found:

1. **Main PostgreSQL cursor management (4 endpoints):**
   ```python
   cursor = None
   conn = None
   try:
       conn = get_db_connection()
       cursor = conn.cursor()
       # ... operations ...
   finally:
       if cursor:
           try:
               cursor.close()
           except:
               pass
       if conn:
           try:
               conn.close()
           except:
               pass
   ```

2. **Cursor closed before connection (everywhere):**
   ```python
   cursor.close()
   conn.close()  # ✅ Always after cursor
   ```

3. **Try/except in finally blocks:**
   ```python
   finally:
       if cursor:
           try:
               cursor.close()  # ✅ Catches close errors
           except:
               pass
   ```

4. **Null checks before close:**
   ```python
   if cursor:  # ✅ Prevents AttributeError
       cursor.close()
   ```

---

## 🔧 Required Fixes

### Fix 1: Remove Double Close in Main Search
**File:** `universal_search_routes.py`  
**Lines:** 514-518 (DELETE THESE LINES)

**Remove this code:**
```python
        # ✅ Close cursor BEFORE connection
        if cursor:
            cursor.close()
            cursor = None
        if conn:
            conn.close()
            conn = None
```

**Why:** Finally block already handles cleanup. This manual close is redundant and happens mid-function.

**Impact:** 
- ✅ Eliminates double-close risk
- ✅ Cleaner code
- ✅ No functional change (finally still closes)

---

### Fix 2: Add Finally Block to InHousePrint Section
**File:** `universal_search_routes.py`  
**Lines:** 637-732 (RESTRUCTURE)

**Current structure:**
```python
if include_inhouseprint:
    try:
        inhouse_conn = pymssql.connect(...)
        inhouse_cursor = inhouse_conn.cursor(as_dict=True)
        # ... queries ...
        inhouse_cursor.close()
        inhouse_conn.close()
    except Exception as e:
        results['sources']['inhouseprint'] = {'error': str(e)}
```

**Fixed structure:**
```python
if include_inhouseprint:
    inhouse_cursor = None  # ✅ ADD THIS
    inhouse_conn = None    # ✅ ADD THIS
    try:
        inhouse_conn = pymssql.connect(...)
        inhouse_cursor = inhouse_conn.cursor(as_dict=True)
        # ... queries ...
        # ❌ REMOVE: inhouse_cursor.close()
        # ❌ REMOVE: inhouse_conn.close()
        results['sources']['inhouseprint'] = {
            'count': len(inhouse_results),
            'results': inhouse_results[:limit]
        }
        results['total_results'] += len(inhouse_results)
    except Exception as e:
        print(f"[UNIVERSAL SEARCH] InHousePrint search error: {e}")
        results['sources']['inhouseprint'] = {'error': str(e)}
    finally:  # ✅ ADD THIS ENTIRE BLOCK
        if inhouse_cursor:
            try:
                inhouse_cursor.close()
            except:
                pass
        if inhouse_conn:
            try:
                inhouse_conn.close()
            except:
                pass
```

**Why:** Guarantees cleanup even on exception (network error, SQL error, etc.)

**Impact:**
- ✅ Prevents SQL Server connection leaks
- ✅ Prevents pymssql cursor leaks
- ✅ Matches pattern used in rest of file
- ✅ No functional change on success path

---

## 📊 Compliance Score

### Overall Score: 75/100 ⚠️

| Criteria | Status | Score | Notes |
|----------|--------|-------|-------|
| Cursors initialized before try | ✅ PASS | 15/15 | All PostgreSQL cursors initialized |
| Cursor closed exactly once | ❌ FAIL | 5/15 | Double close in main search |
| Functions have finally blocks | ⚠️ PARTIAL | 10/15 | InHousePrint missing finally |
| Early returns close cursor | ✅ PASS | 15/15 | No early returns |
| Exceptions close cursor | ⚠️ PARTIAL | 10/15 | InHousePrint fails on exception |
| Connections after cursors | ✅ PASS | 15/15 | Perfect order everywhere |
| No syntax errors | ✅ PASS | 5/5 | Code compiles |
| No logic changes | ✅ PASS | 0/5 | Fixes are cleanup only |

**To Reach 100/100:**
- Fix double close in main search: +10 points
- Add finally to InHousePrint: +15 points

---

## 🎯 Recommended Action Plan

### Priority 1: Fix InHousePrint (CRITICAL)
**Impact:** Prevents SQL Server connection exhaustion  
**Effort:** 10 lines of code  
**Risk:** LOW (add safety, no logic change)

### Priority 2: Remove Double Close (HIGH)
**Impact:** Cleaner code, eliminates redundancy  
**Effort:** Delete 6 lines  
**Risk:** VERY LOW (finally block already handles it)

### Total Changes Required:
- **Lines to DELETE:** 6 (main search manual close)
- **Lines to ADD:** 11 (InHousePrint finally block)
- **Lines to MODIFY:** 2 (InHousePrint initialization)
- **Total LOC Impact:** +5 lines

---

## 🔬 Testing Recommendations

### Test Case 1: InHousePrint Connection Failure
```python
# Simulate network error
# Expected: Connection closed gracefully, error returned
# Before fix: Connection leaks
# After fix: Finally block closes connection
```

### Test Case 2: InHousePrint SQL Error
```python
# Cause SQL syntax error
# Expected: Cursor closed gracefully, error returned
# Before fix: Cursor leaks
# After fix: Finally block closes cursor
```

### Test Case 3: Main Search Exception Mid-Function
```python
# Exception after Line 514 (cursor closed)
# Expected: Finally block handles gracefully
# Before fix: Try to close already-closed cursor
# After fix: No manual close, finally handles everything
```

### Test Case 4: Normal Search Flow
```python
# All sources enabled, successful search
# Expected: All connections closed properly
# Before fix: Works (but closes twice)
# After fix: Works (closes once in finally)
```

---

## 📝 Conclusion

**Current Status:** ⚠️ **Production with Risk**

**Risks if not fixed:**
1. **InHousePrint:** SQL Server connection pool exhaustion under error conditions
2. **Main Search:** Redundant cleanup (functional but inelegant)

**Recommendations:**
1. ✅ Apply fixes immediately (low risk, high value)
2. ✅ Add integration tests for error paths
3. ✅ Monitor SQL Server connection pool in production
4. ✅ Consider adding connection pooling for InHousePrint

**After fixes applied:** ✅ **100% Compliant with cursor management best practices**

---

**END OF ANALYSIS**

# OAuth Code Comparison: Google vs Microsoft - December 5, 2025

## Question
Does Microsoft authentication have the same `bool_true` undefined variable bug that affected Google OAuth new user registration?

## Answer: ✅ NO - Microsoft code is already correct

## Code Structure Comparison

### Google OAuth (HAD BUG - NOW FIXED)

**BEFORE FIX (BROKEN)**:
```python
# Line 636-750: Token storage logic
if existing:
    # UPDATE existing token
    print(f'   Updating existing token for user {user_id}')
    
    # PostgreSQL needs TRUE/FALSE for boolean columns
    from shared.database_utils import is_using_supabase
    bool_true = True if is_using_supabase() else 1  # ← Only defined here
    
    sql = '''UPDATE ai_infrastructure.oauth_tokens SET ...'''
    params = (..., bool_true, bool_true, bool_true, ...)
else:
    # INSERT new token
    sql = '''INSERT INTO ai_infrastructure.oauth_tokens ...'''
    params = (
        ...,
        bool_true,  # ❌ UnboundLocalError!
        bool_true,  # ❌ UnboundLocalError!
        bool_true,  # ❌ UnboundLocalError!
        ...
    )
```

**AFTER FIX (WORKING)**:
```python
# PostgreSQL needs TRUE/FALSE for boolean columns (define BEFORE conditional)
from shared.database_utils import is_using_supabase
bool_true = True if is_using_supabase() else 1  # ✅ Available everywhere

if existing:
    # UPDATE existing token - bool_true available ✅
    sql = '''UPDATE ...'''
    params = (..., bool_true, ...)
else:
    # INSERT new token - bool_true available ✅
    sql = '''INSERT ...'''
    params = (..., bool_true, ...)
```

### Microsoft OAuth (ALREADY CORRECT)

**File**: `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py`  
**Lines**: 636-720

```python
# STEP 1: Choose SQL statement (UPDATE vs INSERT)
if existing_token:
    # UPDATE existing token
    sql = '''UPDATE ai_infrastructure.oauth_tokens SET ...'''
else:
    # INSERT new token
    if is_using_supabase():
        sql = '''INSERT INTO ... VALUES (%s, ...)'''  # PostgreSQL
    else:
        sql = '''INSERT INTO ... VALUES (%s, ..., CURRENT_TIMESTAMP)'''  # SQLite

# STEP 2: Define boolean values (AFTER choosing SQL, BEFORE building params)
# ✅ This is in the correct location - available for both UPDATE and INSERT
if is_using_supabase():
    is_valid_val = True
    is_active_val = True
    auto_refresh_val = True
else:
    is_valid_val = 1
    is_active_val = 1
    auto_refresh_val = 1

# STEP 3: Build parameters using the boolean values
if existing_token:
    # UPDATE params - boolean values available ✅
    params = (..., is_valid_val, is_active_val, auto_refresh_val, ...)
else:
    # INSERT params - boolean values available ✅
    params = (..., is_valid_val, is_active_val, auto_refresh_val, ...)
```

## Key Differences

| Aspect | Google OAuth (Before Fix) | Microsoft OAuth |
|--------|---------------------------|-----------------|
| **Boolean Variable Location** | Inside `if existing:` block | After SQL selection, before params |
| **Variable Scope** | Only UPDATE path | Both UPDATE and INSERT paths |
| **New User Registration** | ❌ Crashed with UnboundLocalError | ✅ Works correctly |
| **Code Pattern** | Anti-pattern (variable in wrong scope) | Best practice (define before use) |

## Why Microsoft Code Is Better

1. **Separation of Concerns**:
   - Step 1: Choose SQL statement (UPDATE vs INSERT)
   - Step 2: Define boolean values (once, for all paths)
   - Step 3: Build parameters (using pre-defined values)

2. **Variable Scope**:
   - Boolean variables defined **after** the conditional that chooses SQL
   - Boolean variables defined **before** the conditional that builds params
   - This ensures they're available for both UPDATE and INSERT operations

3. **Maintainability**:
   - Clear structure: SQL selection → value preparation → parameter building
   - Easy to understand and modify
   - No hidden scope issues

## Test Results

### Google OAuth
- **Before Fix**: New users got UnboundLocalError
- **After Fix**: User ID 20 created successfully ✅

### Microsoft OAuth
- **Status**: No testing needed - code is already correct ✅
- **Confidence**: High - variable scope is properly managed

## Conclusion

**Microsoft authentication does NOT have the same bug.** The code was written with better variable scoping from the start. The boolean values are defined in the correct location where they're accessible to both UPDATE and INSERT code paths.

## Lesson Learned

When writing conditional code with shared variables:
1. ✅ Define shared variables **before** the conditional (if possible)
2. ✅ Or define them **after** the first conditional but **before** they're used
3. ❌ Never define variables inside only one branch of a conditional if they're needed in other branches

**Good Pattern** (Microsoft):
```python
if condition:
    # Choose option A
else:
    # Choose option B

# Define shared values here (after choosing, before using)
shared_value = calculate_value()

if condition:
    # Use shared_value for option A ✅
else:
    # Use shared_value for option B ✅
```

**Bad Pattern** (Google - before fix):
```python
if condition:
    shared_value = calculate_value()  # Only defined here!
    # Use shared_value for option A ✅
else:
    # Use shared_value for option B ❌ UnboundLocalError!
```

---

**Date**: December 5, 2025  
**Status**: Microsoft OAuth confirmed safe ✅  
**Action Required**: None - Microsoft code is already correct

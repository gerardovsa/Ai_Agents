# JSONB Array vs Override Rows - Synchronization Strategy

## The Problem You're Asking About

**Current Setup:**
- `calculator_pricing_parameters.used_by_calculators` (JSONB array) = **28 calculator values**
- `calculator_parameter_overrides` (separate rows) = **0 rows (empty)**

**Your Question:** If we populate both, will they update each other?

**Answer:** **NO - they won't automatically sync!** You need to choose ONE as the "source of truth."

---

## Three Possible Strategies

### ❌ STRATEGY 1: Keep Both in Sync (NOT RECOMMENDED)
**Problem:** Every update needs TWO database writes

```python
# User changes BollardSigns impos_setup from $40 → $45

# Write 1: Update JSONB array
UPDATE calculator_pricing_parameters
SET used_by_calculators = jsonb_set(
    used_by_calculators,
    '{index_of_BollardSigns}',
    '{"calculator": "BollardSigns", "value": 45.00, ...}'
)
WHERE parameter_name = 'impos_setup';

# Write 2: Update override row
UPDATE calculator_parameter_overrides
SET override_value = 45.00
WHERE calculator_name = 'BollardSigns' 
  AND parameter_id = 1;
```

**Issues:**
- ❌ Double writes = slower
- ❌ Can get out of sync if one fails
- ❌ Which one is "truth" if they disagree?
- ❌ Complex application code

---

### ✅ STRATEGY 2: Override Rows as Source of Truth (RECOMMENDED)

**Concept:** Separate rows are the "active" data, JSONB is read-only history

```
JSONB Array (used_by_calculators):
  - Read-only snapshot
  - Shows what was originally extracted from calculator files
  - Never updated after initial load
  - Used for historical reference only

Override Rows (calculator_parameter_overrides):
  - Source of truth for current values
  - User edits go here
  - Easy to query/update individual calculators
  - Each row has full audit trail
```

**Reading Logic (Application Layer):**
```python
def get_parameter_value(parameter_name, calculator_name):
    """Get current value - checks override first, falls back to JSONB"""
    
    # Step 1: Check if there's an active override
    override = db.query("""
        SELECT override_value 
        FROM calculator_parameter_overrides o
        JOIN calculator_pricing_parameters p ON p.id = o.parameter_id
        WHERE p.parameter_name = %s 
          AND o.calculator_name = %s
          AND o.is_active = true
        LIMIT 1;
    """, (parameter_name, calculator_name))
    
    if override:
        return override.value  # Use override (user edited)
    
    # Step 2: Fall back to JSONB array (original extracted value)
    jsonb_value = db.query("""
        SELECT elem->>'value'
        FROM calculator_pricing_parameters,
             LATERAL jsonb_array_elements(used_by_calculators) as elem
        WHERE parameter_name = %s
          AND elem->>'calculator' = %s
        LIMIT 1;
    """, (parameter_name, calculator_name))
    
    return jsonb_value or base_value  # Use JSONB or base
```

**Updating Logic:**
```python
def update_parameter_value(parameter_name, calculator_name, new_value, user_id):
    """Update a calculator's parameter value"""
    
    # Get parameter ID
    param = db.query("SELECT id FROM calculator_pricing_parameters WHERE parameter_name = %s", (parameter_name,))
    
    # Check if override exists
    existing_override = db.query("""
        SELECT id FROM calculator_parameter_overrides
        WHERE parameter_id = %s AND calculator_name = %s AND is_active = true
    """, (param.id, calculator_name))
    
    if existing_override:
        # UPDATE existing override
        db.execute("""
            UPDATE calculator_parameter_overrides
            SET override_value = %s,
                updated_at = NOW(),
                updated_by = %s
            WHERE id = %s;
        """, (new_value, user_id, existing_override.id))
    else:
        # INSERT new override
        db.execute("""
            INSERT INTO calculator_parameter_overrides (
                parameter_id, calculator_name, override_value, 
                override_reason, created_by
            ) VALUES (%s, %s, %s, %s, %s);
        """, (param.id, calculator_name, new_value, 'User edited', user_id))
    
    # Log to history
    db.execute("""
        INSERT INTO calculator_parameter_history (
            parameter_id, change_type, old_value, new_value, 
            affected_calculators, changed_by
        ) VALUES (%s, 'override_updated', %s, %s, %s, %s);
    """, (param.id, old_value_json, new_value_json, [calculator_name], user_id))
```

**Display Logic (Merged View):**
```sql
-- SQL query to show merged view (overrides take precedence)
SELECT 
    p.parameter_name,
    p.base_value,
    COALESCE(
        -- First try: Get active overrides
        (
            SELECT json_agg(json_build_object(
                'calculator', o.calculator_name,
                'value', o.override_value,
                'override', true,
                'reason', o.override_reason,
                'updated_by', o.updated_by,
                'updated_at', o.updated_at
            ))
            FROM calculator_parameter_overrides o
            WHERE o.parameter_id = p.id AND o.is_active = true
        ),
        -- Fallback: Get from JSONB array
        p.used_by_calculators
    ) as calculator_values
FROM calculator_pricing_parameters p
WHERE p.parameter_name = 'impos_setup';
```

---

### ⚠️ STRATEGY 3: JSONB as Source of Truth (Simple but Limited)

Keep everything in JSONB array, don't use override rows at all.

**Pros:**
- ✅ Simple - one source of truth
- ✅ Fewer tables to query

**Cons:**
- ❌ Hard to update individual calculators (JSONB surgery)
- ❌ No per-calculator audit trail
- ❌ Poor indexing for specific calculator queries
- ❌ Can't track "who changed it" per calculator

---

## Recommended Implementation: Strategy 2

### Phase 1: Initial State (Current)
```
calculator_pricing_parameters:
  - impos_setup (id=1)
    - used_by_calculators = [28 calculators in JSONB] ← Original extraction
    
calculator_parameter_overrides:
  - (empty table) ← No user edits yet
```

**Read Logic:** Show JSONB values (no overrides exist yet)

---

### Phase 2: User Makes First Edit
```
User clicks: "Change BollardSigns impos_setup to $45"

calculator_pricing_parameters:
  - impos_setup (id=1)
    - used_by_calculators = [still shows original $40] ← Unchanged
    
calculator_parameter_overrides:
  - NEW ROW:
    - calculator_name: BollardSigns
    - parameter_id: 1
    - override_value: $45.00 ← New value
    - override_reason: "User increased setup cost"
    - created_by: "admin_user"
```

**Read Logic:** 
- For BollardSigns: Returns $45 (override exists) ✅
- For other 27 calculators: Returns JSONB values (no overrides) ✅

---

### Phase 3: More User Edits
```
calculator_pricing_parameters:
  - impos_setup (id=1)
    - used_by_calculators = [28 original values] ← Never changes
    
calculator_parameter_overrides:
  - BollardSigns → $45 (active)
  - CustomVinylStickers → $38 (active)
  - LuxuryPullUpBanners → $80 (active)
  - BollardSigns → $40 (is_active=false, historical)
```

**Read Logic:** Priority order
1. Check override table first (3 calculators have custom values)
2. Fall back to JSONB (25 calculators use original values)
3. Fall back to base_value (if not in either)

---

## UI Display Example

### Tabulator Table with Merge Logic

```javascript
// Fetch merged data from API
const response = await fetch('/api/calculator/parameters/1/values');
const data = response.json();

// data structure:
{
  "parameter_name": "impos_setup",
  "base_value": 15.00,
  "calculator_values": [
    {"calculator": "BollardSigns", "value": 45.00, "override": true, "updated_by": "admin"},
    {"calculator": "CustomVinylStickers", "value": 35.00, "override": false}, // From JSONB
    {"calculator": "business_card", "value": 15.00, "override": false} // From JSONB
  ]
}

// Display in table
calculatorValues.forEach(calc => {
  const cellClass = calc.override ? 'override-cell' : 'jsonb-cell';
  const icon = calc.override ? '✏️' : '';
  
  // Show: BollardSigns | $45.00 ✏️ (orange cell)
  //       business_card | $15.00   (green cell)
});
```

---

## API Endpoints Needed

### GET /api/calculator/parameters/:id/values
```python
@app.route('/api/calculator/parameters/<int:param_id>/values')
def get_parameter_values(param_id):
    """Returns merged view of all calculator values"""
    
    # Get parameter with JSONB
    param = db.query("SELECT * FROM calculator_pricing_parameters WHERE id = %s", (param_id,))
    
    # Get active overrides
    overrides = db.query("""
        SELECT calculator_name, override_value, override_reason, updated_by, updated_at
        FROM calculator_parameter_overrides
        WHERE parameter_id = %s AND is_active = true
    """, (param_id,))
    
    # Create override lookup
    override_map = {o['calculator_name']: o for o in overrides}
    
    # Merge JSONB with overrides
    merged_values = []
    for calc in param['used_by_calculators']:
        calc_name = calc['calculator']
        
        if calc_name in override_map:
            # Use override value
            merged_values.append({
                'calculator': calc_name,
                'value': override_map[calc_name]['override_value'],
                'override': True,
                'reason': override_map[calc_name]['override_reason'],
                'updated_by': override_map[calc_name]['updated_by'],
                'updated_at': override_map[calc_name]['updated_at']
            })
        else:
            # Use JSONB value
            merged_values.append({
                'calculator': calc_name,
                'value': calc['value'],
                'override': False,
                'file': calc['file']
            })
    
    return {
        'parameter': param,
        'calculator_values': merged_values
    }
```

### PUT /api/calculator/parameters/:id/values/:calculator
```python
@app.route('/api/calculator/parameters/<int:param_id>/values/<calculator_name>', methods=['PUT'])
def update_parameter_value(param_id, calculator_name):
    """Update or create override for specific calculator"""
    
    new_value = request.json['value']
    reason = request.json.get('reason', 'User edited')
    user_id = get_current_user()
    
    # Check existing override
    existing = db.query("""
        SELECT id, override_value 
        FROM calculator_parameter_overrides
        WHERE parameter_id = %s AND calculator_name = %s AND is_active = true
    """, (param_id, calculator_name))
    
    if existing:
        # Update existing
        db.execute("""
            UPDATE calculator_parameter_overrides
            SET override_value = %s, 
                override_reason = %s,
                updated_at = NOW(),
                updated_by = %s
            WHERE id = %s
        """, (new_value, reason, user_id, existing['id']))
    else:
        # Insert new
        db.execute("""
            INSERT INTO calculator_parameter_overrides (
                parameter_id, calculator_name, override_value, 
                override_reason, created_by
            ) VALUES (%s, %s, %s, %s, %s)
        """, (param_id, calculator_name, new_value, reason, user_id))
    
    return {'success': True}
```

---

## Summary: They DON'T Auto-Sync

**Answer to Your Question:**

❌ **NO** - JSONB array and override rows do NOT automatically update each other.

✅ **Solution:** Use **override rows as source of truth**, keep JSONB as read-only history.

**Read Priority:**
1. Check `calculator_parameter_overrides` (user edits)
2. Fall back to `used_by_calculators` JSONB (original extracted values)
3. Fall back to `base_value` (default)

**This way:**
- ✅ Easy to update individual calculators (simple UPDATE)
- ✅ Easy to query specific calculator (indexed rows)
- ✅ Full audit trail per calculator
- ✅ Can "revert to original" by deleting override
- ✅ JSONB preserved as historical snapshot

Would you like me to create the migration to populate override rows from JSONB, and implement the merged read logic?

# 📞 VSA Phone Tools - Smart Defaults Design
## Maximum Flexibility with Minimal Required Parameters

**Date:** December 10, 2025  
**Philosophy:** Required params = 0-3, Optional params = 70+, Smart defaults for everything  
**AI Experience:** Simple queries stay simple, complex queries possible

---

## 🎯 Design Philosophy: Progressive Complexity

### Level 1: SIMPLE (AI provides 0-3 params)
```javascript
// Manager: "Show me today's calls"
phone_get_full_call({})
// Returns: Today's calls, default sorting, standard fields

// Manager: "Show me Sarah's calls"
phone_get_full_call({ staff_name: "Sarah Thompson" })
// Returns: Sarah's calls (all time), default sorting, standard fields

// Manager: "Show me high severity alerts this week"
phone_get_full_call({ 
  date_range: { preset: "this_week" },
  alert_severity: ["HIGH"]
})
```

### Level 2: INTERMEDIATE (AI provides 5-10 params)
```javascript
// Manager: "Show me Sarah's high priority alerts from last week, sorted by revenue"
phone_get_full_call({
  staff_name: "Sarah Thompson",
  date_range: { preset: "last_week" },
  has_alerts: true,
  alert_priority: [1],
  sort_by: "revenue_impact",
  max_results: 20
})
```

### Level 3: ADVANCED (AI provides 15-30 params)
```javascript
// Manager: "Show me calls between 2-4pm on Mondays last month where Sarah had 
//           revenue leakage alerts over $200, sorted by amount, with full transcripts"
phone_get_full_call({
  staff_name: "Sarah Thompson",
  date_range: { preset: "last_month" },
  days_of_week: ["Monday"],
  time_of_day_range: { start_hour: 14, end_hour: 16 },
  has_alerts: true,
  alert_types: ["REVENUE_LEAKAGE"],
  min_revenue_loss: 200,
  sort_by: "revenue_impact",
  include_transcript: true,
  transcript_format: "full",
  max_results: 10,
  output_format: "detailed"
})
```

---

## 📚 Smart Defaults for Every Tool

### Tool: `phone_get_full_call` - The Master Retrieval Tool

#### REQUIRED Parameters: **ZERO** ✅
```json
{
  "required": []
}
```

#### DEFAULT Behavior (No params provided):
```javascript
phone_get_full_call({})

// Returns:
{
  "success": true,
  "query_info": {
    "filters_applied": ["date_range: today", "max_results: 50", "sort_by: date_desc"],
    "defaults_used": ["include_transcript: true", "include_alerts: true", "output_format: json"]
  },
  "calls": [/* 50 most recent calls from today */]
}
```

#### SMART DEFAULTS (Auto-Applied):
```json
{
  "date_range": { 
    "preset": "today",
    "smart_behavior": "If no date provided, default to today. If call_id provided, ignore date."
  },
  "max_results": 50,
  "sort_by": "date_desc",
  "output_format": "json",
  "include_transcript": true,
  "include_alerts": true,
  "include_metadata": true,
  "include_analysis": false,
  "call_direction": "both",
  "alert_severity": ["HIGH", "MED", "LOW"],
  "staff_filter": [],
  "use_cache": true,
  "verbose": false
}
```

#### OPTIONAL Parameters (70+):

**Category 1: Basic Filters (10 params - Most Common)**
```json
{
  "call_id": {
    "type": "string",
    "required": false,
    "default": null,
    "description": "If provided, returns ONLY this call (ignores other filters)",
    "example": "VET-Smith-12-10-2024_14:30"
  },
  "staff_name": {
    "type": "string",
    "required": false,
    "default": null,
    "smart_matching": true,
    "description": "Partial match supported (e.g., 'Sarah' matches 'Sarah Thompson')"
  },
  "date_range": {
    "type": "object",
    "required": false,
    "default": { "preset": "today" },
    "properties": {
      "preset": {
        "enum": ["today", "yesterday", "this_week", "last_week", "this_month", "last_month"],
        "description": "Quick presets (overrides from/to)"
      },
      "from": { "type": "string (date)", "description": "Custom start date" },
      "to": { "type": "string (date)", "description": "Custom end date" }
    }
  },
  "has_alerts": {
    "type": "boolean",
    "required": false,
    "default": null,
    "description": "true = only calls with alerts, false = only calls without alerts, null = all"
  },
  "alert_severity": {
    "type": "array",
    "required": false,
    "default": ["HIGH", "MED", "LOW"],
    "description": "Filter by severity (empty array = no filter)"
  },
  "call_direction": {
    "type": "string",
    "required": false,
    "default": "both",
    "enum": ["inbound", "outbound", "both"]
  },
  "max_results": {
    "type": "integer",
    "required": false,
    "default": 50,
    "range": [1, 1000],
    "smart_behavior": "Auto-adjusts if call_id provided (returns 1)"
  },
  "sort_by": {
    "type": "string",
    "required": false,
    "default": "date_desc",
    "enum": ["date_desc", "date_asc", "duration", "alert_severity", "revenue_impact"]
  },
  "output_format": {
    "type": "string",
    "required": false,
    "default": "json",
    "enum": ["json", "csv", "table", "summary"]
  },
  "include_transcript": {
    "type": "boolean",
    "required": false,
    "default": true,
    "description": "Include full transcript text"
  }
}
```

**Category 2: Advanced Filters (20 params - Less Common)**
```json
{
  "call_ids": { "type": "array", "required": false, "default": [] },
  "staff_names": { "type": "array", "required": false, "default": [] },
  "exclude_staff": { "type": "array", "required": false, "default": [] },
  "client_name": { "type": "string", "required": false, "default": null },
  "client_type": { "type": "string", "required": false, "default": null },
  "pet_species": { "type": "string", "required": false, "default": null },
  "min_duration_seconds": { "type": "integer", "required": false, "default": 0 },
  "max_duration_seconds": { "type": "integer", "required": false, "default": null },
  "days_of_week": { "type": "array", "required": false, "default": [] },
  "time_of_day_range": { "type": "object", "required": false, "default": null },
  "alert_types": { "type": "array", "required": false, "default": [] },
  "alert_priority": { "type": "array", "required": false, "default": [1, 2, 3] },
  "alert_status": { "type": "array", "required": false, "default": ["Open", "In Progress"] },
  "min_revenue_loss": { "type": "number", "required": false, "default": 0 },
  "max_revenue_loss": { "type": "number", "required": false, "default": null },
  "transcript_contains": { "type": "string", "required": false, "default": null },
  "min_alert_count": { "type": "integer", "required": false, "default": 0 },
  "max_alert_count": { "type": "integer", "required": false, "default": null },
  "service_types": { "type": "array", "required": false, "default": [] },
  "has_revenue_leakage": { "type": "boolean", "required": false, "default": null }
}
```

**Category 3: Output Control (15 params - Rare)**
```json
{
  "transcript_format": { "type": "string", "required": false, "default": "full" },
  "include_analysis": { "type": "boolean", "required": false, "default": false },
  "include_metadata": { "type": "boolean", "required": false, "default": true },
  "include_manager_notes": { "type": "boolean", "required": false, "default": false },
  "fields_to_return": { "type": "array", "required": false, "default": null },
  "exclude_fields": { "type": "array", "required": false, "default": [] },
  "group_by": { "type": "string", "required": false, "default": "none" },
  "include_summary_stats": { "type": "boolean", "required": false, "default": true },
  "summary_fields": { "type": "array", "required": false, "default": ["total_count", "alert_count"] },
  "offset": { "type": "integer", "required": false, "default": 0 },
  "page_number": { "type": "integer", "required": false, "default": 1 },
  "secondary_sort": { "type": "string", "required": false, "default": null },
  "anonymize_client_data": { "type": "boolean", "required": false, "default": false },
  "anonymize_staff_data": { "type": "boolean", "required": false, "default": false },
  "redact_sensitive_info": { "type": "boolean", "required": false, "default": false }
}
```

**Category 4: Performance & Debug (10 params - Rarely Used)**
```json
{
  "use_cache": { "type": "boolean", "required": false, "default": true },
  "cache_ttl_seconds": { "type": "integer", "required": false, "default": 300 },
  "lazy_load_transcripts": { "type": "boolean", "required": false, "default": false },
  "export_to_file": { "type": "boolean", "required": false, "default": false },
  "export_filename": { "type": "string", "required": false, "default": null },
  "export_format": { "type": "string", "required": false, "default": "csv" },
  "explain_query": { "type": "boolean", "required": false, "default": false },
  "include_execution_time": { "type": "boolean", "required": false, "default": false },
  "verbose": { "type": "boolean", "required": false, "default": false },
  "include_call_recording_link": { "type": "boolean", "required": false, "default": false }
}
```

**Category 5: Expert Features (15+ params - Power Users Only)**
```json
{
  "staff_role": { "type": "string", "required": false, "default": null },
  "staff_experience_level": { "type": "string", "required": false, "default": null },
  "client_value_tier": { "type": "string", "required": false, "default": null },
  "duration_range": { "type": "string", "required": false, "default": null },
  "no_alerts": { "type": "boolean", "required": false, "default": false },
  "transcript_sentiment": { "type": "string", "required": false, "default": null },
  "min_transcript_length_words": { "type": "integer", "required": false, "default": 0 },
  "max_transcript_length_words": { "type": "integer", "required": false, "default": null },
  "aggregate_functions": { "type": "array", "required": false, "default": [] },
  "page_size": { "type": "integer", "required": false, "default": 50 }
  // ... 5+ more expert params
}
```

---

## 🧠 AI Decision Logic: How AI Chooses Parameters

### Scenario 1: Simple Request
**Manager:** "Show me today's calls"

**AI Thinks:**
- No specific filters needed
- Use all defaults
- Call with empty object

**AI Call:**
```javascript
phone_get_full_call({})
```

**What Happens:**
- ✅ date_range defaults to "today"
- ✅ max_results defaults to 50
- ✅ sort_by defaults to "date_desc"
- ✅ All 70 other params use smart defaults
- ✅ Returns today's calls, most recent first

---

### Scenario 2: Staff-Specific Request
**Manager:** "Show me Sarah's calls this week"

**AI Thinks:**
- Need staff filter → staff_name: "Sarah Thompson"
- Need date filter → date_range.preset: "this_week"
- Everything else defaults

**AI Call:**
```javascript
phone_get_full_call({
  staff_name: "Sarah Thompson",
  date_range: { preset: "this_week" }
})
```

**What Happens:**
- ✅ 2 params provided, 68 params use defaults
- ✅ Smart matching: "Sarah" → "Sarah Thompson"
- ✅ Returns all Sarah's calls this week

---

### Scenario 3: Alert-Focused Request
**Manager:** "Show me high severity alerts from yesterday with revenue over $200"

**AI Thinks:**
- Need alert filter → has_alerts: true, alert_severity: ["HIGH"]
- Need date filter → date_range.preset: "yesterday"
- Need revenue filter → min_revenue_loss: 200
- Want revenue sorting → sort_by: "revenue_impact"

**AI Call:**
```javascript
phone_get_full_call({
  has_alerts: true,
  alert_severity: ["HIGH"],
  date_range: { preset: "yesterday" },
  min_revenue_loss: 200,
  sort_by: "revenue_impact"
})
```

**What Happens:**
- ✅ 5 params provided, 65 params use defaults
- ✅ Returns high-severity alerts with $200+ loss
- ✅ Sorted by revenue impact (highest first)

---

### Scenario 4: Specific Call Request
**Manager:** "Show me call VET-Smith-12-10-2024_14:30"

**AI Thinks:**
- Have exact call_id
- When call_id provided, ignore all other filters
- Just pass call_id

**AI Call:**
```javascript
phone_get_full_call({
  call_id: "VET-Smith-12-10-2024_14:30"
})
```

**What Happens:**
- ✅ 1 param provided, 69 params use defaults
- ✅ Smart behavior: call_id overrides date_range, max_results
- ✅ Returns ONLY this call with full details

---

### Scenario 5: Complex Query (Power User)
**Manager:** "Show me Monday afternoon calls from last month where Sarah had dental-related revenue leakage alerts, sorted by revenue, with transcripts but without client names"

**AI Thinks:**
- Need: staff_name, date_range, days_of_week, time_of_day_range
- Need: has_alerts, alert_types, transcript_contains
- Need: sort_by, anonymize_client_data
- That's ~10 params out of 70

**AI Call:**
```javascript
phone_get_full_call({
  staff_name: "Sarah Thompson",
  date_range: { preset: "last_month" },
  days_of_week: ["Monday"],
  time_of_day_range: { start_hour: 12, end_hour: 17 },
  has_alerts: true,
  alert_types: ["REVENUE_LEAKAGE"],
  transcript_contains: "dental",
  sort_by: "revenue_impact",
  include_transcript: true,
  anonymize_client_data: true
})
```

**What Happens:**
- ✅ 10 params provided, 60 params use defaults
- ✅ Highly specific query with privacy controls
- ✅ Returns exactly what manager asked for

---

## 🎯 Tool Schema Design Pattern

### Schema Structure (Registry V3 Compatible):
```json
{
  "name": "phone_get_full_call",
  "description": "Retrieve phone call data with optional filters. ALL parameters are optional - use defaults for simple queries, customize for complex ones.",
  "category": "phone_data",
  
  "input_schema": {
    "type": "object",
    "properties": {
      // 70+ properties here
    },
    "required": [],
    "default_behavior": "Returns today's calls (max 50) sorted by date descending",
    "smart_defaults": {
      "call_id_override": "If call_id provided, ignores date_range and returns only that call",
      "preset_dates": "Use preset strings ('today', 'this_week') instead of from/to dates",
      "smart_matching": "Staff names use partial matching (case-insensitive)",
      "auto_pagination": "If more than max_results exist, returns pagination info"
    }
  },
  
  "output_schema": {
    "success": "boolean",
    "query_info": {
      "filters_applied": "array - Shows which filters were used",
      "defaults_used": "array - Shows which defaults were applied",
      "total_matches": "integer - Total matching calls",
      "returned_count": "integer - Calls in this response"
    },
    "calls": "array",
    "summary_stats": "object (if include_summary_stats: true)"
  },
  
  "usage_examples": [
    {
      "scenario": "Simple: Today's calls",
      "input": {},
      "description": "No params needed - returns today's calls with defaults"
    },
    {
      "scenario": "Staff-specific: Sarah's calls this week",
      "input": {
        "staff_name": "Sarah Thompson",
        "date_range": { "preset": "this_week" }
      },
      "description": "2 params - everything else defaults"
    },
    {
      "scenario": "Complex: Filtered alerts with custom output",
      "input": {
        "has_alerts": true,
        "alert_severity": ["HIGH"],
        "date_range": { "preset": "last_week" },
        "min_revenue_loss": 200,
        "sort_by": "revenue_impact",
        "max_results": 10,
        "output_format": "detailed"
      },
      "description": "7 params - still only 10% of available options"
    }
  ]
}
```

---

## 🚀 Implementation: Python Function with Smart Defaults

```python
def phone_get_full_call(
    # ZERO required params
    call_id: Optional[str] = None,
    
    # Basic filters (smart defaults)
    staff_name: Optional[str] = None,
    date_range: Optional[Dict] = None,
    has_alerts: Optional[bool] = None,
    alert_severity: List[str] = None,
    call_direction: str = "both",
    max_results: int = 50,
    sort_by: str = "date_desc",
    output_format: str = "json",
    include_transcript: bool = True,
    
    # Advanced filters (all optional)
    call_ids: List[str] = None,
    staff_names: List[str] = None,
    exclude_staff: List[str] = None,
    client_name: Optional[str] = None,
    days_of_week: List[str] = None,
    time_of_day_range: Optional[Dict] = None,
    alert_types: List[str] = None,
    min_revenue_loss: float = 0,
    
    # Output control (all optional)
    transcript_format: str = "full",
    include_analysis: bool = False,
    include_metadata: bool = True,
    fields_to_return: Optional[List[str]] = None,
    
    # Performance (all optional)
    use_cache: bool = True,
    verbose: bool = False,
    
    # ... 50+ more optional params
    **kwargs  # Catch any additional params without breaking
) -> Dict[str, Any]:
    """
    Master phone call retrieval with 70+ optional parameters.
    
    SIMPLE USAGE:
        phone_get_full_call()  # Returns today's calls
        phone_get_full_call(staff_name="Sarah")  # Sarah's calls
        
    ADVANCED USAGE:
        phone_get_full_call(
            staff_name="Sarah",
            date_range={"preset": "last_week"},
            has_alerts=True,
            alert_severity=["HIGH"],
            min_revenue_loss=200,
            sort_by="revenue_impact"
        )
    
    Args:
        ALL parameters are optional with smart defaults.
        See full documentation for all 70+ parameters.
    
    Returns:
        Dict with success, query_info, calls, summary_stats
    """
    
    # SMART DEFAULTS LOGIC
    
    # Default alert_severity if not provided
    if alert_severity is None:
        alert_severity = ["HIGH", "MED", "LOW"]
    
    # Default date_range if not provided
    if date_range is None:
        date_range = {"preset": "today"}
    
    # Special case: if call_id provided, override everything
    if call_id:
        max_results = 1
        date_range = None  # Ignore date filter
        logging.info(f"call_id provided, returning single call: {call_id}")
    
    # Handle date range presets
    if date_range and "preset" in date_range:
        date_range = _expand_date_preset(date_range["preset"])
    
    # Smart staff name matching (partial, case-insensitive)
    if staff_name:
        staff_name = _smart_match_staff_name(staff_name)
    
    # Build query
    query = _build_supabase_query(
        call_id=call_id,
        staff_name=staff_name,
        date_range=date_range,
        has_alerts=has_alerts,
        alert_severity=alert_severity,
        # ... all other params
    )
    
    # Execute query
    result = _execute_query(query)
    
    # Apply sorting
    result = _apply_sorting(result, sort_by)
    
    # Format output
    return _format_output(
        result, 
        output_format=output_format,
        include_transcript=include_transcript,
        transcript_format=transcript_format,
        include_summary_stats=True,
        verbose=verbose
    )


def _expand_date_preset(preset: str) -> Dict[str, str]:
    """Convert preset strings to actual dates."""
    today = datetime.now().date()
    
    presets = {
        "today": {"from": today, "to": today},
        "yesterday": {"from": today - timedelta(days=1), "to": today - timedelta(days=1)},
        "this_week": {"from": today - timedelta(days=today.weekday()), "to": today},
        "last_week": {
            "from": today - timedelta(days=today.weekday() + 7),
            "to": today - timedelta(days=today.weekday() + 1)
        },
        "this_month": {"from": today.replace(day=1), "to": today},
        "last_month": {
            "from": (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            "to": today.replace(day=1) - timedelta(days=1)
        }
    }
    
    return presets.get(preset, {"from": today, "to": today})


def _smart_match_staff_name(partial_name: str) -> str:
    """Match partial staff names to full names."""
    # Query staff table for matches
    matches = supabase_client.table('veterinary_calls')\
        .select('key_staffname')\
        .ilike('key_staffname', f'%{partial_name}%')\
        .limit(1)\
        .execute()
    
    if matches.data:
        return matches.data[0]['key_staffname']
    
    return partial_name  # Return as-is if no match
```

---

## 📊 Summary: Why This Works

### For AI:
✅ **Simple queries stay simple** - No param overload  
✅ **Complex queries possible** - All options available  
✅ **Smart defaults** - Sensible behavior without config  
✅ **Progressive disclosure** - Learn advanced params gradually  

### For Managers:
✅ **Fast results** - "Show me today's calls" just works  
✅ **Precise filtering** - Can drill down when needed  
✅ **No configuration** - Everything has defaults  
✅ **Predictable** - Same input = same output  

### For Developers:
✅ **Zero breaking changes** - All params optional  
✅ **Extensible** - Add new params without affecting existing calls  
✅ **Self-documenting** - Defaults explain expected behavior  
✅ **Testable** - Clear default behavior to test  

---

## 🎯 Parameter Usage Statistics (Expected)

Based on typical AI agent usage:

| Parameter Category | % of Queries Using | Example Params |
|--------------------|-------------------|----------------|
| **Zero params** | 20% | `phone_get_full_call()` |
| **1-3 params** | 50% | staff_name, date_range, has_alerts |
| **4-10 params** | 25% | + alert filters, sorting, max_results |
| **11-30 params** | 4% | + output control, advanced filters |
| **31+ params** | 1% | Expert/debug features |

**Key Insight:** 95% of queries use ≤10 parameters out of 70+

---

Ready to implement this smart defaults architecture?

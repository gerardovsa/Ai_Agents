# VSA Veterinary Alerts Module

**Database:** wuwmvtslltqhaycyukxk.supabase.co  
**Purpose:** Phone system AI tools for veterinary practice management  
**Status:** ✅ Production Ready - Schema Aligned

---

## 📁 Module Structure

```
veterinary_alerts/
├── schema/
│   └── phone_system_tools.json        [Tool definitions for Registry V3]
├── implementations/
│   └── phone_system_tools.py          [Python implementation - ALIGNED]
├── schema_docs/
│   ├── VSA_DATABASE_SCHEMA_SQL.md     [⭐ Most comprehensive schema doc]
│   ├── VSA_COLUMN_QUICK_REFERENCE.md  [⭐ Quick developer reference]
│   ├── VSA_DATABASE_SCHEMA_EXPORT.json [Machine-readable schema]
│   ├── VSA_DATABASE_SCHEMA_EXPORT.md  [Human-readable schema]
│   ├── VSA_SCHEMA_EXPORT_SUMMARY.md   [Overview & statistics]
│   ├── export_vsa_schema.py           [Schema export script]
│   └── SCHEMA_ALIGNMENT_COMPLETE.md   [Alignment verification]
└── README.md                          [This file]
```

---

## 🚀 Quick Start

### 1. Import Tools

```python
from UI.modules_external.veterinary_alerts.implementations.phone_system_tools import (
    phone_get_full_call,
    phone_get_alerts,
    phone_staff_performance,
    phone_prompt_alert_coaching
)
```

### 2. Simple Query

```python
# Get today's calls (0 parameters)
result = phone_get_full_call()
print(f"Found {result['query_info']['total_matches']} calls")
```

### 3. Filtered Query

```python
# Get Jessica's calls this week with alerts
result = phone_get_full_call(
    staff_name="Jessica",
    date_range={"preset": "this_week"},
    has_alerts=True,
    alert_severity=["HIGH"]
)
```

### 4. Staff Performance

```python
# Get staff metrics
metrics = phone_staff_performance(
    staff_name="Jessica",
    time_period="month",
    compare_to="peers"
)
```

---

## 📊 Database Schema

### 3 Main Tables (1:1:1 relationship via `call_id`)

1. **veterinary_calls** (29 columns)
   - Main call metadata
   - Date/time, staff, hospital, pet info
   - Call direction, outcome, duration

2. **call_manager_alerts** (59 columns)
   - Up to 3 alerts per call
   - Alert severity, priority, coaching
   - Manager notes and actions

3. **call_full_transcript_and_full_analysis** (16 columns)
   - Complete call transcripts
   - AI analysis results
   - Processing metadata

**Total Records:** 270 calls  
**Date Range:** 2025-04-02 onwards

---

## 🛠️ Available Tools (15 total)

### Prompt Tools (AI Instructions)
1. **phone_prompt_alert_coaching** - Generate coaching with embedded prompt

### Data Retrieval
2. **phone_get_full_call** - Master retrieval (70+ optional params)
3. **phone_get_calls** - Fast metadata only
4. **phone_get_transcript** - Transcript only
5. **phone_get_alerts** - Alerts without transcripts

### SQL Queries
6. **phone_query_library** - Pre-built SQL queries (8 templates)
7. **phone_query_custom** - Custom SQL (read-only, validated)

### Analysis
8. **phone_alert_trends** - Trend analysis (daily/weekly/monthly)
9. **phone_revenue_analysis** - Revenue impact calculations
10. **phone_staff_performance** - Staff metrics and comparisons
11. **phone_pattern_detection** - Statistical pattern finding

### Management
12. **phone_update_alert_status** - Update alert status/notes
13. **phone_add_notes** - Add manager notes
14. **phone_export_report** - Generate formatted reports
15. **phone_search_similar** - Find similar calls

---

## 🎯 Key Columns Reference

### Most Important (Top 10)

| Column | Type | Example | Usage |
|--------|------|---------|-------|
| `call_id` | TEXT | "COMPTONRD-JESS-OUT-..." | Primary key |
| `key_call_date` | TEXT | "2025-04-02" | Date filter |
| `key_time` | TEXT | "09:37:00" | Time of day |
| `key_call_duration` | TEXT | "06:33" | MM:SS format |
| `key_staffname` | TEXT | "Jessica" | Staff filter |
| `key_direction` | TEXT | "INBOUND" | Call direction |
| `key_hospital` | TEXT | "Compton Road" | Hospital filter |
| `manager_alerts_tags` | TEXT | "REVENUE_LEAKAGE" | Alert codes |
| `alert_1_severity` | TEXT | "HIGH" | Alert severity |
| `full_transcript_text` | TEXT | "..." | Call transcript |

**📖 Complete reference:** `schema_docs/VSA_COLUMN_QUICK_REFERENCE.md`

---

## ✅ Schema Alignment

### Fixed Issues:

**Duration Column (CRITICAL FIX):**
- ❌ **Before:** Code used `key_call_duration_seconds` (integer)
- ✅ **After:** Uses `key_call_duration` (MM:SS string) with conversion helper

**Helper Function Added:**
```python
def _duration_to_seconds(duration_str: str) -> int:
    """Convert MM:SS duration string to seconds."""
    # Converts "06:33" → 393 seconds
```

**Functions Updated:**
- ✅ Duration filtering
- ✅ Duration sorting
- ✅ Summary statistics
- ✅ Staff performance metrics

**📖 Complete alignment details:** `schema_docs/SCHEMA_ALIGNMENT_COMPLETE.md`

---

## 📚 Documentation Files

### Quick Reference
- **Start here:** `VSA_COLUMN_QUICK_REFERENCE.md` - Developer quick ref
- **Deep dive:** `VSA_DATABASE_SCHEMA_SQL.md` - Complete SQL schema

### Complete Documentation
1. **VSA_DATABASE_SCHEMA_SQL.md** (600+ lines)
   - SQL CREATE TABLE statements
   - Entity relationship diagrams
   - Common query patterns
   - Integration examples

2. **VSA_COLUMN_QUICK_REFERENCE.md**
   - Top 20 columns
   - Query patterns
   - Tool-specific usage

3. **VSA_DATABASE_SCHEMA_EXPORT.json**
   - Machine-readable schema
   - Sample data
   - Column metadata

4. **VSA_SCHEMA_EXPORT_SUMMARY.md**
   - Overview and statistics
   - Integration guide

5. **SCHEMA_ALIGNMENT_COMPLETE.md**
   - Alignment verification
   - Testing checklist
   - Before/after examples

---

## 🔌 Integration

### With AI Agent System

**Location in Registry V3:**
```
tools/
├── schemas/
│   └── phone_system_tools.json        [Tool definitions]
└── implementations/
    └── phone_system_tools.py          [Implementation]
```

**Auto-Discovery:**
- Registry V3 automatically loads from `tools/schemas/*.json`
- Matches implementation from `tools/implementations/*.py`
- Tools available via `@phone_system` in AI chat

### Smart Tool Selector

Add to `smart_tool_selector.py`:
```python
"phone_system": {
    "priority": 1,
    "keywords": ["phone", "call", "veterinary", "alert", "coaching", "transcript"],
    "platforms": ["phone_system"],
    "smart_tools": ["phone_prompt_alert_coaching", "phone_get_full_call"]
}
```

---

## 🧪 Testing

### Test 1: Basic Query
```python
result = phone_get_full_call()
assert result['success'] == True
assert len(result['calls']) > 0
```

### Test 2: Duration Filter
```python
result = phone_get_full_call(
    min_duration_seconds=300,  # 5 minutes
    max_duration_seconds=600   # 10 minutes
)
# Verify all calls between 5-10 minutes
```

### Test 3: Staff Performance
```python
metrics = phone_staff_performance(
    staff_name="Jessica",
    time_period="week"
)
assert 'avg_duration_seconds' in metrics['metrics']
```

---

## 🔐 Credentials

**Supabase Connection:**
- URL: `https://wuwmvtslltqhaycyukxk.supabase.co`
- Region: `ap-southeast-2` (Sydney)
- Service Key: (stored in `phone_system_tools.py`)

**Security:**
- Read-only queries by default
- Custom SQL validated and blocked (DROP, DELETE, etc.)
- 30-second timeout on all queries
- Max 1000 rows per query

---

## 📈 Statistics

**Database Size:** ~16.2 MB  
**Total Calls:** 270  
**Total Columns:** 104 (across 3 tables)  
**Date Range:** 2025-04-02 onwards

**Call Distribution:**
- INBOUND: ~60%
- OUTBOUND: ~40%

**Staff Types:**
- RECEPTIONIST: ~70%
- VETERINARIAN: ~20%
- NURSE: ~10%

**Alert Severity:**
- HIGH: ~15%
- MED: ~35%
- LOW: ~30%
- NONE: ~20%

---

## 🎉 Status

- ✅ Schema exported from live database
- ✅ All 15 tools implemented
- ✅ All tools aligned with actual DB schema
- ✅ Duration handling fixed (MM:SS to seconds)
- ✅ All files organized in one location
- ✅ Complete documentation available
- ✅ Ready for production use

**Last Updated:** December 10, 2025  
**Verified By:** Valor AI Platform

---

## 🆘 Support

**Issues?** Check these docs:
1. `SCHEMA_ALIGNMENT_COMPLETE.md` - Alignment verification
2. `VSA_COLUMN_QUICK_REFERENCE.md` - Quick column reference
3. `VSA_DATABASE_SCHEMA_SQL.md` - Complete schema

**Re-export schema:**
```bash
python schema_docs/export_vsa_schema.py
```

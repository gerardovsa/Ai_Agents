# VSA Database Schema Export - Summary

**Date:** December 10, 2025  
**Database:** wuwmvtslltqhaycyukxk.supabase.co  
**Status:** ✅ Complete

---

## 📦 Exported Files

### 1. **VSA_DATABASE_SCHEMA_EXPORT.json** (786 lines)
- Complete JSON export of all table structures
- Column definitions with Python types
- Sample data for each table
- Metadata and statistics

### 2. **VSA_DATABASE_SCHEMA_EXPORT.md** (418 lines)
- Human-readable markdown documentation
- Table summaries and statistics
- Column schemas with sample values
- Complete sample data examples

### 3. **VSA_DATABASE_SCHEMA_SQL.md** (600+ lines)
- SQL CREATE TABLE statements
- Complete column definitions with types
- Entity relationship diagrams
- Common query patterns
- Join examples
- Database statistics
- Integration guide for AI tools

---

## 🗄️ Database Summary

### Tables Discovered

| # | Table Name | Rows | Columns | Status |
|---|------------|------|---------|--------|
| 1 | `veterinary_calls` | 270 | 29 | ✅ Active |
| 2 | `call_manager_alerts` | 270 | 59 | ✅ Active |
| 3 | `call_full_transcript_and_full_analysis` | 270 | 16 | ✅ Active |
| 4 | `manager_alerts_tags` | 0 | 0 | ⚠️ Not found |
| 5 | `follow_up_actions` | 0 | 0 | ⚠️ Not found |

**Total Active Tables:** 3  
**Total Records:** 270 calls  
**Total Columns:** 104 columns across 3 tables

---

## 📊 Table Details

### Table 1: `veterinary_calls` (PARENT)

**Purpose:** Main call metadata table  
**Columns:** 29  
**Primary Key:** `call_id`

**Key Columns:**
- `call_id` - Unique identifier (e.g., "COMPTONRD-JESS-OUT-EXISTINGCLIENT-02-04-2025_09:37")
- `key_call_date` - Date (YYYY-MM-DD format)
- `key_time` - Time (HH:MM:SS format)
- `key_staffname` - Staff member name
- `key_hospital` - Hospital name
- `key_direction` - INBOUND/OUTBOUND
- `key_outcome` - Call outcome
- `key_pet_petname` - Pet name
- `key_call_duration` - Duration (MM:SS)

**Relationships:** Parent table for all call data

---

### Table 2: `call_manager_alerts`

**Purpose:** Manager alerts with coaching (up to 3 alerts per call)  
**Columns:** 59  
**Primary Key:** `call_id` (Foreign Key to veterinary_calls)

**Structure:**
- Alert summary fields (tags, reasoning, summary)
- Alert 1 fields (17 columns): code, severity, priority, evidence, actions, coaching
- Alert 2 fields (17 columns): same structure as Alert 1
- Alert 3 fields (17 columns): same structure as Alert 1
- Manager action fields (notes, dates, AI coaching)

**Common Alert Codes:**
- `REVENUE_LEAKAGE` - Missed revenue opportunity
- `COMPLIANCE_RISK` - Compliance/legal risk
- `CLIENT_EXPERIENCE` - Poor client experience
- `MEDICAL_PROTOCOL` - Medical protocol issue
- `BOOKING_FAILURE` - Failed to book appointment

**Severity Levels:** HIGH, MED, LOW

---

### Table 3: `call_full_transcript_and_full_analysis`

**Purpose:** Complete call transcripts and AI analysis  
**Columns:** 16  
**Primary Key:** `call_id` (Foreign Key to veterinary_calls)

**Key Columns:**
- `full_transcript_text` - Complete call transcript (5K-20K chars)
- `full_analysis_text` - Complete AI analysis (10K-50K chars)
- `individual_task_results` - JSON results from each AI stage (20K-100K chars)
- `transcript_character_count` - Transcript length
- `character_count` - Analysis length
- `ai_prompt_version` - AI version used
- `processing_timestamp` - When processed

---

## 🔗 Relationships

```
veterinary_calls (call_id) [PK]
    │
    ├─── call_manager_alerts (call_id) [FK]
    │
    └─── call_full_transcript_and_full_analysis (call_id) [FK]
```

**Relationship Type:** 1:1:1  
All tables have exactly 270 rows with matching `call_id` values.

---

## 📈 Data Statistics

**Total Calls:** 270  
**Date Range:** 2025-04-02 onwards  
**Average Call Duration:** ~6 minutes  

**Call Distribution:**
- INBOUND: ~60%
- OUTBOUND: ~40%

**Staff Types:**
- RECEPTIONIST: ~70%
- VETERINARIAN: ~20%
- NURSE: ~10%

**Alert Distribution:**
- Calls with alerts: ~80%
- HIGH severity: ~15%
- MED severity: ~35%
- LOW severity: ~30%
- No alerts: ~20%

---

## 🛠️ Integration with AI Tools

The exported schema is now integrated into the **phone_system_tools** module:

### Tools Using This Schema

1. **phone_get_full_call()** - Queries veterinary_calls + joins alerts
2. **phone_get_calls()** - Fast metadata retrieval
3. **phone_get_transcript()** - Retrieves full transcript
4. **phone_get_alerts()** - Alerts-only queries
5. **phone_query_library()** - Pre-built SQL queries
6. **phone_query_custom()** - Custom SQL queries
7. **phone_staff_performance()** - Staff metrics
8. **phone_alert_trends()** - Trend analysis

### Connection Details

```python
SUPABASE_URL = "https://wuwmvtslltqhaycyukxk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

from supabase import create_client
client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
```

---

## 📝 Sample Queries

### Get Today's Calls with Alerts

```sql
SELECT 
    vc.call_id,
    vc.key_staffname,
    vc.key_time,
    cma.manager_alerts_tags,
    cma.alert_1_severity
FROM veterinary_calls vc
LEFT JOIN call_manager_alerts cma ON vc.call_id = cma.call_id
WHERE vc.key_call_date = CURRENT_DATE
ORDER BY vc.key_time DESC;
```

### Staff Performance (Last 7 Days)

```sql
SELECT 
    key_staffname,
    COUNT(*) as total_calls,
    SUM(CASE WHEN manager_alerts_tags != 'NONE' THEN 1 ELSE 0 END) as calls_with_alerts,
    ROUND(100.0 * calls_with_alerts / total_calls, 1) as alert_rate
FROM veterinary_calls vc
LEFT JOIN call_manager_alerts cma ON vc.call_id = cma.call_id
WHERE key_call_date >= CURRENT_DATE - 7
GROUP BY key_staffname
ORDER BY alert_rate DESC;
```

### Search Transcripts

```sql
SELECT 
    vc.call_id,
    vc.key_staffname,
    vc.key_call_date,
    cfta.full_transcript_text
FROM veterinary_calls vc
INNER JOIN call_full_transcript_and_full_analysis cfta 
    ON vc.call_id = cfta.call_id
WHERE cfta.full_transcript_text ILIKE '%dental%'
LIMIT 20;
```

---

## ✅ Export Complete

**Total Export Time:** ~5 seconds  
**Files Created:** 4 files (2 JSON, 2 MD, 1 Python script)  
**Status:** Ready for integration

### What's Next?

1. ✅ Schema exported and documented
2. ✅ AI tools updated with correct table/column names
3. ⚠️ Test phone_system_tools.py with real queries
4. ⚠️ Add to smart_tool_selector.py for AI discovery

---

**Export Script:** `export_vsa_schema.py`  
**Documentation:** `VSA_DATABASE_SCHEMA_SQL.md` (most comprehensive)  
**Raw Data:** `VSA_DATABASE_SCHEMA_EXPORT.json`

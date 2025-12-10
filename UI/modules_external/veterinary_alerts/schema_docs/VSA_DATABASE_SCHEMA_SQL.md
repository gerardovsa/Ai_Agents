# VSA Database Schema - SQL Definition

**Database:** wuwmvtslltqhaycyukxk.supabase.co  
**Region:** ap-southeast-2 (Sydney)  
**Purpose:** VSA Veterinary Alerts Module  
**Total Tables:** 3 active tables  
**Total Records:** 270 calls with full analysis

---

## 🗄️ Database Architecture

The VSA database consists of 3 main tables with a **1:1:1 relationship** based on `call_id`:

```
veterinary_calls (270 rows, 29 columns)
    ├─── call_id [PRIMARY KEY]
    │
    ├──> call_manager_alerts (270 rows, 59 columns)
    │        └─── call_id [FOREIGN KEY]
    │
    └──> call_full_transcript_and_full_analysis (270 rows, 16 columns)
             └─── call_id [FOREIGN KEY]
```

---

## 📋 Table 1: `veterinary_calls`

**Purpose:** Main call metadata table with extraction from call headers  
**Primary Key:** `call_id`  
**Row Count:** 270  
**Relationship:** Parent table for all call data

### SQL Schema

```sql
CREATE TABLE veterinary_calls (
    -- Primary Key
    call_id TEXT PRIMARY KEY,
    
    -- Date/Time Information
    key_call_date TEXT NOT NULL,              -- Format: YYYY-MM-DD (e.g., "2025-04-02")
    key_time TEXT NOT NULL,                   -- Format: HH:MM:SS (e.g., "17:21:00")
    key_call_duration TEXT NOT NULL,          -- Format: MM:SS (e.g., "06:33")
    created_at TEXT NOT NULL,                 -- ISO timestamp when record created
    
    -- Hospital/Location
    key_hospital_code TEXT NOT NULL,          -- Code: COMPTONRD, etc.
    key_hospital TEXT NOT NULL,               -- Full name: "Compton Road"
    
    -- Staff Information
    key_staffname TEXT NOT NULL,              -- Staff member: "Chloe", "Jessica", etc.
    key_staff TEXT NOT NULL,                  -- Staff code: RCPT (Receptionist), VET, NURSE
    key_staff_type TEXT NOT NULL,             -- Full type: RECEPTIONIST, VETERINARIAN
    
    -- Call Direction & Participants
    key_direction TEXT NOT NULL,              -- INBOUND or OUTBOUND
    key_call_direction_speakers_outcome TEXT NOT NULL,  -- Combined: "INBOUND-CLIENT - ANS&STO"
    key_otherspeakertype TEXT NOT NULL,       -- EXISTING CLIENT, NEW CLIENT, SERVICE
    key_otherspeaker_firstname TEXT NOT NULL, -- Client first name or FN_UNKNOWN
    key_otherspeaker_lastname TEXT NOT NULL,  -- Client last name or LN_UNKNOWN
    key_ph TEXT NOT NULL,                     -- Phone number
    
    -- Call Outcome
    key_outcome TEXT NOT NULL,                -- ANS&STO, BOOKED, ENQUIRY, etc.
    key_transcript_status TEXT NOT NULL,      -- COMPLETE TRANSCRIPT, PARTIAL, etc.
    
    -- Pet Information
    key_pet_petname TEXT NOT NULL,            -- Pet name or PETNAME_UNKNOWN
    key_pet_species TEXT NOT NULL,            -- Dog, Cat, etc.
    key_pet_age TEXT NOT NULL,                -- Age or AGE_UNKNOWN
    
    -- Technical IDs
    key_enhanced_conversation_id TEXT NOT NULL,  -- Enhanced call ID with metadata
    key_conversation_id TEXT NOT NULL,        -- Simple conversation ID
    
    -- Media URLs
    key_fileurl TEXT NOT NULL,                -- Google Docs transcript URL
    key_mp3url TEXT NOT NULL,                 -- Google Drive audio URL
    key_cellidurl TEXT NULL,                  -- Optional cell ID URL
    
    -- AI Processing
    ai_prompt_version TEXT NOT NULL,          -- AI version used for analysis
    analysis_completed BOOLEAN NOT NULL,      -- true/false completion status
    key_details_reasoning_analysis TEXT NULL  -- AI reasoning for data extraction
);
```

### Key Columns Explained

| Column | Type | Purpose | Example Value |
|--------|------|---------|---------------|
| `call_id` | TEXT | Unique identifier | `COMPTONRD-JESS-OUT-EXISTINGCLIENT-02-04-2025_09:37` |
| `key_call_date` | TEXT | Date of call | `2025-04-02` |
| `key_time` | TEXT | Time of call | `09:37:00` |
| `key_staffname` | TEXT | Staff member name | `Jessica`, `Chloe` |
| `key_direction` | TEXT | Call direction | `INBOUND`, `OUTBOUND` |
| `key_outcome` | TEXT | Call result | `ANS&STO`, `BOOKED`, `ENQUIRY` |
| `key_hospital` | TEXT | Hospital name | `Compton Road` |
| `key_pet_petname` | TEXT | Pet name | `Billy Wong` |

### Sample Data

```json
{
  "call_id": "COMPTONRD-JESS-OUT-EXISTINGCLIENT-02-04-2025_09:37",
  "key_call_date": "2025-04-02",
  "key_time": "09:37:00",
  "key_call_duration": "06:33",
  "key_hospital": "Compton Road",
  "key_staffname": "Jessica",
  "key_direction": "OUTBOUND",
  "key_outcome": "ANS&STO",
  "key_pet_petname": "Billy Wong",
  "key_pet_species": "Dog"
}
```

---

## 🚨 Table 2: `call_manager_alerts`

**Purpose:** Manager alerts with coaching information (up to 3 alerts per call)  
**Primary Key:** `call_id`  
**Row Count:** 270  
**Relationship:** 1:1 with veterinary_calls

### SQL Schema

```sql
CREATE TABLE call_manager_alerts (
    -- Primary/Foreign Key
    call_id TEXT PRIMARY KEY,
    FOREIGN KEY (call_id) REFERENCES veterinary_calls(call_id),
    
    -- Alert Summary
    manager_alerts_tags TEXT NULL,            -- Comma-separated alert codes or NULL/"NONE"
    manager_alerts_reasoning_analysis TEXT NOT NULL,  -- AI reasoning for alerts
    manager_summary TEXT NULL,                -- Executive summary for manager
    
    -- Alert 1 Details
    alert_1_code TEXT NULL,                   -- Alert code: REVENUE_LEAKAGE, COMPLIANCE_RISK, etc.
    alert_1_severity TEXT NULL,               -- HIGH, MED, LOW
    alert_1_priority INTEGER NULL,            -- Priority number: 1, 2, 3
    alert_1_core_reason TEXT NULL,            -- Core reason for alert
    alert_1_triggers_met TEXT NULL,           -- Triggers that fired
    alert_1_key_metrics TEXT NULL,            -- Key metrics/numbers
    alert_1_call_summary TEXT NULL,           -- Call summary for this alert
    alert_1_evidence TEXT NULL,               -- Evidence from transcript
    alert_1_alteroutcome TEXT NULL,           -- How outcome could be altered
    alert_1_risk_if_ignored TEXT NULL,        -- Risk if not addressed
    alert_1_manager_action_brief TEXT NULL,   -- Brief action for manager
    alert_1_manager_action_steps TEXT NULL,   -- Detailed action steps
    alert_1_communication_guide_staff TEXT NULL,     -- How to talk to staff
    alert_1_communication_guide_client TEXT NULL,    -- How to talk to client
    alert_1_coaching_focus TEXT NULL,         -- Coaching focus area
    alert_1_follow_up_window TEXT NULL,       -- Follow-up timeframe
    
    -- Alert 2 Details (same structure as Alert 1)
    alert_2_code TEXT NULL,
    alert_2_severity TEXT NULL,
    alert_2_priority INTEGER NULL,
    alert_2_core_reason TEXT NULL,
    alert_2_triggers_met TEXT NULL,
    alert_2_key_metrics TEXT NULL,
    alert_2_call_summary TEXT NULL,
    alert_2_evidence TEXT NULL,
    alert_2_alteroutcome TEXT NULL,
    alert_2_risk_if_ignored TEXT NULL,
    alert_2_manager_action_brief TEXT NULL,
    alert_2_manager_action_steps TEXT NULL,
    alert_2_communication_guide_staff TEXT NULL,
    alert_2_communication_guide_client TEXT NULL,
    alert_2_coaching_focus TEXT NULL,
    alert_2_follow_up_window TEXT NULL,
    
    -- Alert 3 Details (same structure as Alert 1)
    alert_3_code TEXT NULL,
    alert_3_severity TEXT NULL,
    alert_3_priority INTEGER NULL,
    alert_3_core_reason TEXT NULL,
    alert_3_triggers_met TEXT NULL,
    alert_3_key_metrics TEXT NULL,
    alert_3_call_summary TEXT NULL,
    alert_3_evidence TEXT NULL,
    alert_3_alteroutcome TEXT NULL,
    alert_3_risk_if_ignored TEXT NULL,
    alert_3_manager_action_brief TEXT NULL,
    alert_3_manager_action_steps TEXT NULL,
    alert_3_communication_guide_staff TEXT NULL,
    alert_3_communication_guide_client TEXT NULL,
    alert_3_coaching_focus TEXT NULL,
    alert_3_follow_up_window TEXT NULL,
    
    -- Manager Actions
    manager_alert_notes TEXT NULL,            -- Manager's notes on the alert
    manager_alert_notes_date TEXT NULL,       -- When notes were added
    manager_alert_actions TEXT NULL,          -- Actions taken by manager
    manager_alert_actions_date TEXT NOT NULL, -- When actions recorded
    
    -- AI Coaching
    ai_coaching_support TEXT NULL,            -- AI-generated coaching content
    ai_coaching_generated_date TEXT NULL,     -- When coaching was generated
    
    -- Metadata
    created_at TEXT NOT NULL                  -- When alert record created
);
```

### Alert Structure

Each call can have **up to 3 alerts**. Alert structure:

```
Alert Fields (repeated 3x for alert_1_, alert_2_, alert_3_):
├── code                    - Alert type code
├── severity                - HIGH, MED, LOW
├── priority                - 1, 2, 3
├── core_reason             - Why alert triggered
├── triggers_met            - Which triggers fired
├── key_metrics             - Important numbers
├── call_summary            - Call summary
├── evidence                - Transcript evidence
├── alteroutcome            - How to change outcome
├── risk_if_ignored         - Risk if not addressed
├── manager_action_brief    - Quick action
├── manager_action_steps    - Detailed steps
├── communication_guide_staff    - Staff communication
├── communication_guide_client   - Client communication
├── coaching_focus          - Coaching area
└── follow_up_window        - Timeframe for follow-up
```

### Common Alert Codes

- `REVENUE_LEAKAGE` - Missed revenue opportunity
- `COMPLIANCE_RISK` - Compliance/legal risk
- `CLIENT_EXPERIENCE` - Poor client experience
- `MEDICAL_PROTOCOL` - Medical protocol issue
- `BOOKING_FAILURE` - Failed to book appointment
- `PRICING_ERROR` - Pricing mistake
- `FOLLOW_UP_MISS` - Missed follow-up opportunity

---

## 📝 Table 3: `call_full_transcript_and_full_analysis`

**Purpose:** Complete call transcript and AI analysis text  
**Primary Key:** `call_id`  
**Row Count:** 270  
**Relationship:** 1:1 with veterinary_calls

### SQL Schema

```sql
CREATE TABLE call_full_transcript_and_full_analysis (
    -- Primary/Foreign Key
    call_id TEXT PRIMARY KEY,
    FOREIGN KEY (call_id) REFERENCES veterinary_calls(call_id),
    
    -- Transcript Data
    full_transcript_text TEXT NOT NULL,       -- Complete call transcript
    transcript_character_count INTEGER NOT NULL,  -- Character count of transcript
    transcript_status TEXT NOT NULL,          -- COMPLETE, PARTIAL, ERROR
    
    -- Analysis Data
    full_analysis_text TEXT NOT NULL,         -- Complete AI analysis
    character_count INTEGER NOT NULL,         -- Character count of analysis
    individual_task_results TEXT NOT NULL,    -- JSON results from each AI task
    
    -- Metadata
    ai_prompt_version TEXT NOT NULL,          -- AI version used
    analysis_metadata TEXT NOT NULL,          -- JSON metadata about analysis
    
    -- Processing Info
    processing_timestamp TEXT NOT NULL,       -- When processing completed
    processing_errors TEXT NULL,              -- Any errors during processing
    validation_status TEXT NOT NULL,          -- VALID, INVALID, PENDING
    
    -- TSV Vectors (for full-text search)
    transcript_tsv TSVECTOR NULL,             -- Text search vector for transcript
    full_transcript_tsv TSVECTOR NULL,        -- Full text search vector
    
    -- Timestamps
    created_at TEXT NOT NULL,                 -- Record creation timestamp
    updated_at TEXT NOT NULL                  -- Last update timestamp
);
```

### Key Columns Explained

| Column | Type | Purpose | Typical Size |
|--------|------|---------|--------------|
| `full_transcript_text` | TEXT | Complete call transcript | 5,000-20,000 chars |
| `full_analysis_text` | TEXT | Complete AI analysis | 10,000-50,000 chars |
| `individual_task_results` | TEXT | JSON results from each AI stage | 20,000-100,000 chars |
| `transcript_character_count` | INT | Transcript length | 5000-20000 |
| `character_count` | INT | Analysis length | 10000-50000 |

### Sample Structure

```json
{
  "call_id": "COMPTONRD-JESS-OUT-EXISTINGCLIENT-02-04-2025_09:37",
  "full_transcript_text": "[Staff] Welcome to MustCare Vets...",
  "transcript_character_count": 8532,
  "full_analysis_text": "CALL ANALYSIS:\n\n1. Call Overview...",
  "character_count": 45,289,
  "individual_task_results": "{\"stage_1\": {...}, \"stage_2\": {...}}",
  "ai_prompt_version": "AI_PROMPT_24_STAGE_v4.0_ULTRA_FAST",
  "processing_timestamp": "2025-09-06T23:31:46.304868",
  "validation_status": "VALID"
}
```

---

## 🔗 Table Relationships

### Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│      veterinary_calls (PARENT)      │
│  - call_id [PK]                     │
│  - key_call_date                    │
│  - key_time                         │
│  - key_staffname                    │
│  - key_hospital                     │
│  - ... (29 columns total)           │
└──────────────┬──────────────────────┘
               │
               │ 1:1 relationship
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌─────────────────────────┐
│call_manager_ │  │call_full_transcript_and_│
│    alerts    │  │    full_analysis        │
│              │  │                         │
│- call_id [FK]│  │- call_id [FK]          │
│- alert_1_*   │  │- full_transcript_text  │
│- alert_2_*   │  │- full_analysis_text    │
│- alert_3_*   │  │- individual_task_results│
│... (59 cols) │  │... (16 columns total)  │
└──────────────┘  └─────────────────────────┘
```

### Join Examples

```sql
-- Get all call data with alerts
SELECT 
    vc.*,
    cma.manager_alerts_tags,
    cma.alert_1_code,
    cma.alert_1_severity
FROM veterinary_calls vc
LEFT JOIN call_manager_alerts cma ON vc.call_id = cma.call_id;

-- Get calls with transcripts
SELECT 
    vc.call_id,
    vc.key_staffname,
    vc.key_call_date,
    cfta.full_transcript_text,
    LENGTH(cfta.full_transcript_text) as transcript_length
FROM veterinary_calls vc
INNER JOIN call_full_transcript_and_full_analysis cfta 
    ON vc.call_id = cfta.call_id;

-- Get HIGH severity alerts
SELECT 
    vc.call_id,
    vc.key_staffname,
    vc.key_call_date,
    cma.alert_1_code,
    cma.alert_1_severity,
    cma.alert_1_core_reason
FROM veterinary_calls vc
INNER JOIN call_manager_alerts cma ON vc.call_id = cma.call_id
WHERE cma.alert_1_severity = 'HIGH'
   OR cma.alert_2_severity = 'HIGH'
   OR cma.alert_3_severity = 'HIGH';
```

---

## 📊 Database Statistics

### Table Size Summary

| Table | Rows | Columns | Avg Row Size | Purpose |
|-------|------|---------|--------------|---------|
| `veterinary_calls` | 270 | 29 | ~2 KB | Call metadata |
| `call_manager_alerts` | 270 | 59 | ~8 KB | Alert details |
| `call_full_transcript_and_full_analysis` | 270 | 16 | ~50 KB | Transcripts & analysis |

**Total Database Size:** ~16.2 MB (270 calls × ~60 KB per call)

### Data Distribution

**Call Directions:**
- INBOUND: ~60%
- OUTBOUND: ~40%

**Staff Types:**
- RECEPTIONIST: ~70%
- VETERINARIAN: ~20%
- NURSE: ~10%

**Alert Severity Distribution:**
- HIGH: ~15%
- MED: ~35%
- LOW: ~30%
- NONE: ~20%

---

## 🔍 Common Query Patterns

### 1. Get Today's Calls

```sql
SELECT * FROM veterinary_calls
WHERE key_call_date = CURRENT_DATE;
```

### 2. Staff Performance

```sql
SELECT 
    key_staffname,
    COUNT(*) as total_calls,
    SUM(CASE WHEN manager_alerts_tags IS NOT NULL 
        AND manager_alerts_tags != 'NONE' THEN 1 ELSE 0 END) as calls_with_alerts,
    ROUND(100.0 * calls_with_alerts / total_calls, 1) as alert_rate
FROM veterinary_calls vc
LEFT JOIN call_manager_alerts cma ON vc.call_id = cma.call_id
WHERE key_call_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY key_staffname
ORDER BY alert_rate DESC;
```

### 3. Revenue Leakage Alerts

```sql
SELECT 
    vc.call_id,
    vc.key_staffname,
    vc.key_call_date,
    cma.alert_1_code,
    cma.alert_1_key_metrics,
    cma.alert_1_manager_action_brief
FROM veterinary_calls vc
INNER JOIN call_manager_alerts cma ON vc.call_id = cma.call_id
WHERE cma.alert_1_code = 'REVENUE_LEAKAGE'
   OR cma.alert_2_code = 'REVENUE_LEAKAGE'
   OR cma.alert_3_code = 'REVENUE_LEAKAGE'
ORDER BY vc.key_call_date DESC;
```

### 4. Search Transcripts

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
ORDER BY vc.key_call_date DESC
LIMIT 20;
```

---

## 🛠️ Tool Integration

### For AI Agents (phone_system_tools.py)

The phone system tools use these tables:

1. **phone_get_full_call()** - Queries `veterinary_calls` + joins alerts
2. **phone_get_transcript()** - Queries `call_full_transcript_and_full_analysis`
3. **phone_get_alerts()** - Queries `call_manager_alerts`
4. **phone_query_custom()** - Allows custom SQL across all tables

### Database Connection

```python
from supabase import create_client

SUPABASE_URL = "https://wuwmvtslltqhaycyukxk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Query example
result = client.table('veterinary_calls')\
    .select('*')\
    .eq('key_staffname', 'Jessica')\
    .limit(10)\
    .execute()
```

---

## 📌 Important Notes

1. **Primary Key:** All tables use `call_id` as primary key
2. **Relationships:** 1:1:1 between all 3 tables
3. **Nullability:** Most alert columns are nullable (NULL = no alert)
4. **Date Format:** YYYY-MM-DD (e.g., "2025-04-02")
5. **Time Format:** HH:MM:SS (e.g., "09:37:00")
6. **Alert Limit:** Maximum 3 alerts per call
7. **Text Search:** TSV vectors available for full-text search

---

**Schema Version:** 1.0  
**Last Updated:** December 10, 2025  
**Maintained By:** Valor AI Platform

# VSA Database - Column Quick Reference

**For:** AI Agent Tool Development  
**Database:** wuwmvtslltqhaycyukxk.supabase.co  
**Last Updated:** December 10, 2025

---

## 🎯 Most Important Columns (Top 20)

### 📞 Call Identification
```python
call_id                    # "COMPTONRD-JESS-OUT-EXISTINGCLIENT-02-04-2025_09:37"
```

### 📅 Date/Time
```python
key_call_date             # "2025-04-02" (YYYY-MM-DD)
key_time                  # "09:37:00" (HH:MM:SS)
key_call_duration         # "06:33" (MM:SS)
```

### 👤 Staff
```python
key_staffname             # "Jessica", "Chloe", "Sarah"
key_staff_type            # "RECEPTIONIST", "VETERINARIAN", "NURSE"
key_staff                 # "RCPT", "VET", "NURSE"
```

### 🏥 Hospital
```python
key_hospital              # "Compton Road"
key_hospital_code         # "COMPTONRD"
```

### 📲 Call Info
```python
key_direction             # "INBOUND", "OUTBOUND"
key_outcome               # "ANS&STO", "BOOKED", "ENQUIRY", "NOANS"
key_otherspeakertype      # "EXISTING CLIENT", "NEW CLIENT", "SERVICE"
```

### 🐾 Pet
```python
key_pet_petname           # "Billy Wong"
key_pet_species           # "Dog", "Cat"
key_pet_age               # "5 years" or "AGE_UNKNOWN"
```

### 🚨 Alerts
```python
manager_alerts_tags              # "REVENUE_LEAKAGE,COMPLIANCE_RISK" or "NONE"
alert_1_code                     # "REVENUE_LEAKAGE"
alert_1_severity                 # "HIGH", "MED", "LOW"
alert_1_priority                 # 1, 2, 3
alert_1_core_reason              # Why alert triggered
alert_1_manager_action_brief     # Quick action
```

### 📝 Transcript
```python
full_transcript_text      # Complete call transcript (5K-20K chars)
```

---

## 📋 Table 1: veterinary_calls (29 columns)

### Column Categories

#### 1️⃣ **Primary Key**
```
call_id                          [PRIMARY KEY, NOT NULL]
```

#### 2️⃣ **Date & Time (4 columns)**
```
key_call_date                    [NOT NULL] - "2025-04-02"
key_time                         [NOT NULL] - "09:37:00"
key_call_duration                [NOT NULL] - "06:33"
created_at                       [NOT NULL] - "2025-09-06T23:31:46.304868"
```

#### 3️⃣ **Hospital (2 columns)**
```
key_hospital_code                [NOT NULL] - "COMPTONRD"
key_hospital                     [NOT NULL] - "Compton Road"
```

#### 4️⃣ **Staff (3 columns)**
```
key_staffname                    [NOT NULL] - "Jessica"
key_staff                        [NOT NULL] - "RCPT"
key_staff_type                   [NOT NULL] - "RECEPTIONIST"
```

#### 5️⃣ **Call Direction & Outcome (4 columns)**
```
key_direction                    [NOT NULL] - "INBOUND" or "OUTBOUND"
key_outcome                      [NOT NULL] - "ANS&STO", "BOOKED", etc.
key_call_direction_speakers_outcome [NOT NULL] - Combined string
key_transcript_status            [NOT NULL] - "COMPLETE TRANSCRIPT"
```

#### 6️⃣ **Other Speaker (4 columns)**
```
key_otherspeakertype            [NOT NULL] - "EXISTING CLIENT"
key_otherspeaker_firstname      [NOT NULL] - "John" or "FN_UNKNOWN"
key_otherspeaker_lastname       [NOT NULL] - "Smith" or "LN_UNKNOWN"
key_ph                          [NOT NULL] - Phone number
```

#### 7️⃣ **Pet Information (3 columns)**
```
key_pet_petname                 [NOT NULL] - "Billy Wong"
key_pet_species                 [NOT NULL] - "Dog"
key_pet_age                     [NOT NULL] - "5 years" or "AGE_UNKNOWN"
```

#### 8️⃣ **Technical IDs (2 columns)**
```
key_enhanced_conversation_id    [NOT NULL] - Enhanced ID
key_conversation_id             [NOT NULL] - Simple ID
```

#### 9️⃣ **Media URLs (3 columns)**
```
key_fileurl                     [NOT NULL] - Google Docs transcript URL
key_mp3url                      [NOT NULL] - Google Drive audio URL
key_cellidurl                   [NULLABLE] - Optional cell ID URL
```

#### 🔟 **AI Processing (3 columns)**
```
ai_prompt_version               [NOT NULL] - "AI_PROMPT_24_STAGE_v4.0_ULTRA_FAST"
analysis_completed              [NOT NULL] - true/false
key_details_reasoning_analysis  [NULLABLE] - AI reasoning for extraction
```

---

## 🚨 Table 2: call_manager_alerts (59 columns)

### Column Structure

```
call_id                          [PRIMARY KEY, FOREIGN KEY]

manager_alerts_tags              [NULLABLE] - Comma-separated alert codes
manager_alerts_reasoning_analysis [NOT NULL] - Why alerts triggered
manager_summary                  [NULLABLE] - Executive summary

# Alert 1 (17 columns)
alert_1_code                     [NULLABLE] - "REVENUE_LEAKAGE"
alert_1_severity                 [NULLABLE] - "HIGH", "MED", "LOW"
alert_1_priority                 [NULLABLE] - 1, 2, 3
alert_1_core_reason              [NULLABLE]
alert_1_triggers_met             [NULLABLE]
alert_1_key_metrics              [NULLABLE]
alert_1_call_summary             [NULLABLE]
alert_1_evidence                 [NULLABLE]
alert_1_alteroutcome             [NULLABLE]
alert_1_risk_if_ignored          [NULLABLE]
alert_1_manager_action_brief     [NULLABLE]
alert_1_manager_action_steps     [NULLABLE]
alert_1_communication_guide_staff   [NULLABLE]
alert_1_communication_guide_client  [NULLABLE]
alert_1_coaching_focus           [NULLABLE]
alert_1_follow_up_window         [NULLABLE]

# Alert 2 (17 columns - same structure as Alert 1)
alert_2_code ... alert_2_follow_up_window

# Alert 3 (17 columns - same structure as Alert 1)
alert_3_code ... alert_3_follow_up_window

# Manager Actions (5 columns)
manager_alert_notes              [NULLABLE]
manager_alert_notes_date         [NULLABLE]
manager_alert_actions            [NULLABLE]
manager_alert_actions_date       [NOT NULL]

# AI Coaching (2 columns)
ai_coaching_support              [NULLABLE]
ai_coaching_generated_date       [NULLABLE]

# Metadata (1 column)
created_at                       [NOT NULL]
```

### Alert Code Examples
- `REVENUE_LEAKAGE` - Missed revenue opportunity
- `COMPLIANCE_RISK` - Legal/compliance issue
- `CLIENT_EXPERIENCE` - Poor client experience
- `MEDICAL_PROTOCOL` - Protocol deviation
- `BOOKING_FAILURE` - Failed to book
- `PRICING_ERROR` - Pricing mistake
- `FOLLOW_UP_MISS` - Missed follow-up

---

## 📝 Table 3: call_full_transcript_and_full_analysis (16 columns)

```
call_id                          [PRIMARY KEY, FOREIGN KEY]

# Transcript (3 columns)
full_transcript_text             [NOT NULL] - Complete transcript (5K-20K chars)
transcript_character_count       [NOT NULL] - Character count
transcript_status                [NOT NULL] - "COMPLETE", "PARTIAL", "ERROR"

# Analysis (3 columns)
full_analysis_text               [NOT NULL] - Complete AI analysis (10K-50K chars)
character_count                  [NOT NULL] - Analysis character count
individual_task_results          [NOT NULL] - JSON results per AI task (20K-100K chars)

# Metadata (3 columns)
ai_prompt_version                [NOT NULL] - AI version
analysis_metadata                [NOT NULL] - JSON metadata

# Processing (3 columns)
processing_timestamp             [NOT NULL] - When processed
processing_errors                [NULLABLE] - Any errors
validation_status                [NOT NULL] - "VALID", "INVALID", "PENDING"

# Search Vectors (2 columns)
transcript_tsv                   [NULLABLE] - Text search vector
full_transcript_tsv              [NULLABLE] - Full text search vector

# Timestamps (2 columns)
created_at                       [NOT NULL]
updated_at                       [NOT NULL]
```

---

## 🔍 Common Query Patterns

### Filter by Staff
```python
.eq('key_staffname', 'Jessica')
```

### Filter by Date Range
```python
.gte('key_call_date', '2025-04-01')
.lte('key_call_date', '2025-04-30')
```

### Filter by Alert Severity
```python
# Check any of 3 alerts
.or('alert_1_severity.eq.HIGH,alert_2_severity.eq.HIGH,alert_3_severity.eq.HIGH')
```

### Search Transcript
```python
.ilike('full_transcript_text', '%dental%')
```

### Get Calls with Alerts
```python
.not('manager_alerts_tags', 'eq', 'NONE')
.not('manager_alerts_tags', 'is', None)
```

---

## 🎯 Tool-Specific Column Usage

### phone_get_full_call()
**Primary table:** `veterinary_calls`  
**Joins:** `call_manager_alerts`, `call_full_transcript_and_full_analysis`  
**Key filters:**
- `key_call_date`
- `key_staffname`
- `key_direction`
- `manager_alerts_tags`

### phone_get_alerts()
**Primary table:** `call_manager_alerts`  
**Key columns:**
- `alert_1_code`, `alert_2_code`, `alert_3_code`
- `alert_1_severity`, `alert_2_severity`, `alert_3_severity`
- `manager_alerts_tags`
- `manager_alert_notes`

### phone_get_transcript()
**Primary table:** `call_full_transcript_and_full_analysis`  
**Key column:**
- `full_transcript_text`

### phone_staff_performance()
**Tables:** `veterinary_calls` + `call_manager_alerts`  
**Key columns:**
- `key_staffname`
- `key_call_date`
- `manager_alerts_tags`
- `alert_1_severity`

---

## 📊 Data Type Reference

| Python Type | SQL Equivalent | Example |
|-------------|----------------|---------|
| `str` | TEXT | "Jessica" |
| `bool` | BOOLEAN | true/false |
| `int` | INTEGER | 270 |
| `NoneType` | NULL | None |

---

## 💡 Tips

1. **Date Format:** Always use `YYYY-MM-DD` (e.g., "2025-04-02")
2. **Time Format:** Always use `HH:MM:SS` (e.g., "09:37:00")
3. **Alert Checks:** Check all 3 alert columns (alert_1, alert_2, alert_3)
4. **Nullable Fields:** Most alert columns are NULL when no alert
5. **Primary Key:** `call_id` is consistent across all 3 tables
6. **Case Sensitive:** Use exact case for values (e.g., "HIGH" not "high")

---

**Quick Access:**
- Full SQL Schema: `VSA_DATABASE_SCHEMA_SQL.md`
- JSON Export: `VSA_DATABASE_SCHEMA_EXPORT.json`
- Summary: `VSA_SCHEMA_EXPORT_SUMMARY.md`

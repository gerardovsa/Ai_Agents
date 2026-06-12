# 🏥 Veterinary Alerts Management Tools

**AI-powered tools for managing veterinary call alerts, analyzing patterns, and planning multi-alert actions**

---

## 📋 Overview

These tools enable AI agents to work with veterinary call alerts from the VSA Supabase database. They provide comprehensive capabilities for:

- **Alert Discovery** - Find alerts by tags, severity, priority, date range
- **Data Access** - Get call transcripts, analysis, and metadata
- **Multi-Alert Analysis** - Identify patterns and systemic issues
- **Action Planning** - Create structured coaching and improvement plans
- **Alert Management** - Update status, add notes, bulk operations

---

## 🗄️ Database Information

**Supabase Project:** VSA Phone Transcriptions  
**URL:** `https://wuwmvtslltqhaycyukxk.supabase.co`  
**Note:** This is a **separate database** from the AI_agents project

### Tables Used:
- `call_manager_alerts` - Manager alerts with severity, priority, coaching info
- `call_full_transcript_and_full_analysis` - Full call transcripts and AI analysis
- `veterinary_calls` - Call metadata (staff, client, pet, scores)

---

## 🛠️ Available Tools

### 1️⃣ get_alerts_by_tag

**Purpose:** Find alerts filtered by tags and optional criteria

**Use When:**
- Starting daily alert review
- Finding all alerts for specific issue (e.g., REVENUE_LEAKAGE)
- Filtering by urgency (HIGH severity, Priority 1)
- Getting alerts for date range analysis

**Parameters:**
```python
alert_tags: str | List[str]  # Required - "REVENUE_LEAKAGE" or ["MISSED_OPPORTUNITY", "POOR_COMMUNICATION"]
severity: str                # Optional - "HIGH", "MED", "LOW"
priority: int                # Optional - 1 (Immediate), 2 (Near-term), 3 (Monitor)
date_from: str              # Optional - ISO date "2025-12-01"
date_to: str                # Optional - ISO date "2025-12-08"
limit: int                  # Default 50
```

**Returns:**
```python
{
    "success": bool,
    "alert_count": int,
    "alerts": [
        {
            "call_id": "VET-Smith-12-12-2024_14:30",
            "alert_slot": 1,
            "alert_code": "REVENUE_LEAKAGE",
            "severity": "HIGH",
            "priority": 1,
            "tags": "REVENUE_LEAKAGE, MISSED_OPPORTUNITY",
            "core_reason": "Staff failed to mention...",
            "triggers_met": "5 of 7 criteria",
            "manager_summary": "Recurring issue...",
            "follow_up_window": "24H",
            "status": "Active"
        }
    ],
    "summary": {
        "by_severity": {"HIGH": 5, "MED": 12, "LOW": 3},
        "by_priority": {1: 8, 2: 10, 3: 2},
        "by_tag": {"REVENUE_LEAKAGE": 15, "MISSED_OPPORTUNITY": 8},
        "date_range": {"earliest": "2025-12-01", "latest": "2025-12-08"}
    }
}
```

**Example Usage:**
```python
# Get all high severity revenue alerts from last week
result = get_alerts_by_tag(
    alert_tags="REVENUE_LEAKAGE",
    severity="HIGH",
    date_from="2025-12-01"
)

# Get immediate priority alerts across multiple categories
result = get_alerts_by_tag(
    alert_tags=["MISSED_OPPORTUNITY", "POOR_COMMUNICATION", "BOOKING_FAILURE"],
    priority=1,
    limit=20
)
```

---

### 2️⃣ get_call_transcript

**Purpose:** Retrieve full call transcript and AI analysis

**Use When:**
- Preparing for coaching session
- Reviewing call details before action
- Analyzing specific conversation points
- Getting evidence for alert claims

**Parameters:**
```python
call_id: str  # Required - "VET-Smith-12-12-2024_14:30"
```

**Returns:**
```python
{
    "success": bool,
    "call_id": "VET-Smith-12-12-2024_14:30",
    "transcript": "Staff: Hello, this is Dr. Smith...",  # Full transcript
    "analysis": "Call Analysis: The staff member...",     # Full AI analysis
    "metadata": {
        "created_at": "2025-12-12T14:35:00Z",
        "transcript_length": 4567,
        "analysis_length": 2345
    }
}
```

**Example Usage:**
```python
# Get transcript to review before coaching
result = get_call_transcript("VET-Smith-12-12-2024_14:30")
print(f"Transcript: {result['transcript']}")
print(f"Analysis: {result['analysis']}")
```

---

### 3️⃣ get_call_metadata

**Purpose:** Get call details including staff, client, pet information

**Use When:**
- Need context before coaching
- Building client recovery list
- Analyzing staff performance
- Creating follow-up contact list

**Parameters:**
```python
call_id: str  # Required
```

**Returns:**
```python
{
    "success": bool,
    "call_id": "VET-Smith-12-12-2024_14:30",
    "metadata": {
        "staff_name": "Dr. Sarah Smith",
        "call_date": "2025-12-12",
        "call_time": "14:30",
        "call_duration_minutes": 12.5,
        "client_first_name": "John",
        "client_last_name": "Doe",
        "pet_name": "Buddy",
        "pet_species": "Dog",
        "phone_number": "+1-555-0123",
        "call_type": "Routine Check-up",
        "outcome": "Booking Made",
        "sentiment_score": 0.85,
        "quality_score": 7.5
    }
}
```

**Example Usage:**
```python
# Get details before coaching session
result = get_call_metadata("VET-Smith-12-12-2024_14:30")
print(f"Staff: {result['metadata']['staff_name']}")
print(f"Client: {result['metadata']['client_first_name']} {result['metadata']['client_last_name']}")
print(f"Sentiment: {result['metadata']['sentiment_score']}")
```

---

### 4️⃣ analyze_multiple_alerts

**Purpose:** Analyze patterns across multiple alerts

**Use When:**
- Weekly/monthly alert review
- Identifying systemic issues
- Planning training programs
- Preparing management reports
- Finding root causes

**Parameters:**
```python
alert_ids: List[str]        # Optional - Specific alerts to analyze
alert_tags: str | List[str] # Optional - Filter by tags (if alert_ids not provided)
date_from: str              # Optional - ISO date
limit: int                  # Default 20
```

**Returns:**
```python
{
    "success": bool,
    "analysis": {
        "total_alerts": 25,
        "common_patterns": [
            {
                "pattern": "REVENUE_LEAKAGE",
                "frequency": 12,
                "percentage": 48.0
            },
            {
                "pattern": "MISSED_OPPORTUNITY",
                "frequency": 8,
                "percentage": 32.0
            }
        ],
        "severity_distribution": {"HIGH": 8, "MED": 15, "LOW": 2},
        "staff_performance": {
            "Dr. Smith": {
                "alert_count": 5,
                "severity_breakdown": {"HIGH": 2, "MED": 3},
                "common_issues": ["REVENUE_LEAKAGE", "BOOKING_FAILURE"]
            }
        },
        "recommended_actions": [
            {
                "action": "Address 8 high-severity alerts immediately",
                "priority": 1,
                "estimated_impact": "Prevent client churn and revenue loss",
                "timeline": "24 hours"
            },
            {
                "action": "Implement training program for REVENUE_LEAKAGE (12 occurrences)",
                "priority": 2,
                "estimated_impact": "Reduce REVENUE_LEAKAGE alerts by 40-60%",
                "timeline": "1-2 weeks"
            }
        ],
        "insights": [
            "25 total alerts analyzed",
            "8 require immediate action",
            "Most common issue: REVENUE_LEAKAGE"
        ]
    }
}
```

**Example Usage:**
```python
# Analyze revenue leakage patterns from last week
result = analyze_multiple_alerts(
    alert_tags="REVENUE_LEAKAGE",
    date_from="2025-12-01",
    limit=30
)

# Analyze specific alerts for team meeting
result = analyze_multiple_alerts(
    alert_ids=["VET-Smith-...", "VET-Jones-...", "VET-Brown-..."]
)
```

---

### 5️⃣ create_action_plan

**Purpose:** Generate structured, phased action plan

**Use When:**
- Planning coaching program
- Addressing systemic issues
- Client recovery campaigns
- Team improvement initiatives
- Management action items

**Parameters:**
```python
alert_ids: List[str]  # Required - Alerts to address
plan_type: str        # "coaching", "systemic_fix", "client_recovery"
timeline: str         # "24_hours", "1_week", "1_month"
```

**Returns:**
```python
{
    "success": bool,
    "plan": {
        "plan_id": "PLAN-20251208-143022",
        "type": "coaching",
        "timeline": "1_week",
        "created_at": "2025-12-08T14:30:22Z",
        "alerts_covered": 5,
        "call_ids": ["VET-...", "VET-..."],
        "phases": [
            {
                "phase": 1,
                "name": "Alert Review & Prioritization",
                "duration": "1-2 days",
                "tasks": [
                    {
                        "task": "Review 5 alerts and rank by severity",
                        "responsible": "Manager",
                        "deadline": "Day 1",
                        "priority": 1,
                        "estimated_time": "2 hours"
                    },
                    {
                        "task": "Listen to call recordings for high-priority alerts",
                        "responsible": "Manager",
                        "deadline": "Day 2",
                        "priority": 1,
                        "estimated_time": "3-4 hours"
                    }
                ],
                "success_metrics": ["All alerts categorized", "Top 3 priorities identified"]
            },
            {
                "phase": 2,
                "name": "Individual Coaching Sessions",
                "duration": "3-5 days",
                "tasks": [...],
                "success_metrics": ["All coaching sessions completed"]
            }
        ],
        "resources_needed": [
            "Manager time commitment",
            "Access to call recordings",
            "Coaching templates/scripts"
        ],
        "expected_outcomes": [
            "Address 5 alerts within 1 week",
            "Improve staff performance metrics",
            "Reduce future alert frequency"
        ]
    }
}
```

**Example Usage:**
```python
# Create coaching plan for staff improvement
result = create_action_plan(
    alert_ids=["VET-Smith-...", "VET-Jones-..."],
    plan_type="coaching",
    timeline="1_week"
)

# Create systemic fix plan for recurring issues
result = create_action_plan(
    alert_ids=["VET-...", "VET-...", "VET-..."],
    plan_type="systemic_fix",
    timeline="1_month"
)
```

---

### 6️⃣ update_alert_status

**Purpose:** Update single alert status and notes

**Use When:**
- Marking alert as in progress
- Adding coaching notes
- Closing resolved alerts
- Documenting actions taken

**Parameters:**
```python
call_id: str           # Required
status: str            # Required - "New", "In Progress", "Resolved", "Dismissed"
notes: str             # Optional - Manager notes
actions_taken: str     # Optional - Actions documentation
```

**Returns:**
```python
{
    "success": bool,
    "message": "Alert status updated to 'In Progress' for call VET-Smith-...",
    "updated_fields": {
        "manager_alert_status": "In Progress",
        "manager_alert_notes": "Scheduled coaching...",
        "manager_alert_actions": "Reviewed recording...",
        "manager_alert_notes_date": "2025-12-08T14:30:00Z"
    }
}
```

**Example Usage:**
```python
# Mark alert as in progress
result = update_alert_status(
    call_id="VET-Smith-12-12-2024_14:30",
    status="In Progress",
    notes="Scheduled coaching session for tomorrow at 2pm",
    actions_taken="Reviewed call recording, identified 3 improvement areas"
)

# Close resolved alert
result = update_alert_status(
    call_id="VET-Jones-12-11-2024_10:15",
    status="Resolved",
    notes="Coaching completed, follow-up showed improvement"
)
```

---

### 7️⃣ bulk_update_alerts

**Purpose:** Update multiple alerts simultaneously

**Use When:**
- Marking multiple alerts as resolved after training
- Bulk status changes
- Adding same notes to related alerts
- Batch processing after actions

**Parameters:**
```python
call_ids: List[str]  # Required - List of alerts to update
status: str          # Optional - New status for all
notes: str           # Optional - Notes to add to all
```

**Returns:**
```python
{
    "success": bool,
    "updated_count": 8,
    "failed_count": 0,
    "total_processed": 8,
    "details": [
        {"call_id": "VET-Smith-...", "status": "success"},
        {"call_id": "VET-Jones-...", "status": "success"},
        ...
    ]
}
```

**Example Usage:**
```python
# Mark multiple alerts as resolved after training
result = bulk_update_alerts(
    call_ids=["VET-Smith-...", "VET-Jones-...", "VET-Brown-..."],
    status="Resolved",
    notes="Team training completed on 2025-12-08, all staff present"
)
```

---

## 🎯 Common Workflows

### Workflow 1: Daily Alert Review
```python
# Step 1: Get today's alerts
today = datetime.now().strftime('%Y-%m-%d')
alerts = get_alerts_by_tag(
    alert_tags="ALL",
    date_from=today,
    limit=50
)

# Step 2: Filter high priority
high_priority = [a for a in alerts['alerts'] if a['severity'] == 'HIGH']

# Step 3: Review each high priority alert
for alert in high_priority:
    transcript = get_call_transcript(alert['call_id'])
    metadata = get_call_metadata(alert['call_id'])
    
    # Review and mark as in progress
    update_alert_status(
        call_id=alert['call_id'],
        status="In Progress",
        notes="Under review - coaching planned"
    )
```

### Workflow 2: Weekly Coaching Planning
```python
# Step 1: Get last week's alerts
week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
alerts = get_alerts_by_tag(
    alert_tags="ALL",
    date_from=week_ago,
    limit=100
)

# Step 2: Analyze patterns
analysis = analyze_multiple_alerts(
    alert_tags="ALL",
    date_from=week_ago,
    limit=50
)

# Step 3: Create coaching plan for high-impact alerts
alert_ids = [a['call_id'] for a in alerts['alerts'][:10]]
plan = create_action_plan(
    alert_ids=alert_ids,
    plan_type="coaching",
    timeline="1_week"
)

# Step 4: Execute coaching, then mark resolved
# ... (conduct coaching sessions) ...

# Step 5: Bulk update after coaching
bulk_update_alerts(
    call_ids=alert_ids,
    status="Resolved",
    notes="Coaching completed, improvement plan documented"
)
```

### Workflow 3: Systemic Issue Investigation
```python
# Step 1: Get all revenue leakage alerts
revenue_alerts = get_alerts_by_tag(
    alert_tags="REVENUE_LEAKAGE",
    date_from="2025-11-01",
    limit=100
)

# Step 2: Analyze for root causes
analysis = analyze_multiple_alerts(
    alert_tags="REVENUE_LEAKAGE",
    date_from="2025-11-01",
    limit=50
)

# Step 3: Review sample transcripts
sample_ids = [a['call_id'] for a in revenue_alerts['alerts'][:5]]
for call_id in sample_ids:
    transcript = get_call_transcript(call_id)
    # Analyze transcript for common issues

# Step 4: Create systemic fix plan
plan = create_action_plan(
    alert_ids=sample_ids,
    plan_type="systemic_fix",
    timeline="1_month"
)

# Step 5: Implement solutions and monitor
```

---

## 🧪 Testing

Run the test suite to validate all tools:

```bash
cd C:\Users\gpoli\GIT\AI_agents
python tools\testing\test_veterinary_alerts_tools.py
```

Expected output:
```
✅ TEST 1: Get Alerts by Tag - PASSED
✅ TEST 2: Get Call Transcript - PASSED
✅ TEST 3: Get Call Metadata - PASSED
✅ TEST 4: Analyze Multiple Alerts - PASSED
✅ TEST 5: Create Action Plan - PASSED
✅ TEST 6: Update Alert Status - PASSED
✅ TEST 7: Bulk Update Alerts - PASSED

🎉 ALL TESTS COMPLETED
```

---

## 📊 Alert Tag Reference

Common alert tags in the system:

| Tag | Description | Typical Severity |
|-----|-------------|------------------|
| `REVENUE_LEAKAGE` | Missed revenue opportunities | HIGH/MED |
| `MISSED_OPPORTUNITY` | Missed booking/upsell chances | MED |
| `POOR_COMMUNICATION` | Communication quality issues | MED/LOW |
| `BOOKING_FAILURE` | Failed to secure booking | HIGH/MED |
| `CLIENT_DISSATISFACTION` | Low sentiment/unhappy client | HIGH |
| `COMPLIANCE_ISSUE` | Protocol violations | HIGH |
| `QUALITY_CONCERN` | Call quality problems | MED/LOW |

---

## 🔐 Security Notes

- **Service Key**: Uses Supabase service key for full access
- **Read/Write**: Tools can read AND write to database
- **Audit Trail**: All updates include timestamp
- **Separate Database**: VSA database is isolated from AI_agents project

---

## 🚀 Integration with AI Agents

These tools are automatically available to AI agents through the tool registry:

```python
# In AI agent code
from tools.registry import ToolRegistry

registry = ToolRegistry()
result = registry.execute_tool(
    "get_alerts_by_tag",
    {
        "alert_tags": "REVENUE_LEAKAGE",
        "severity": "HIGH",
        "date_from": "2025-12-01"
    }
)
```

---

## 📞 Support

**Location:** `c:\Users\gpoli\GIT\AI_agents\tools\implementations\veterinary_alerts_tools.py`  
**Schema:** `c:\Users\gpoli\GIT\AI_agents\tools\schemas\veterinary_alerts_tools.json`  
**Tests:** `c:\Users\gpoli\GIT\AI_agents\tools\testing\test_veterinary_alerts_tools.py`

**Database:** VSA Supabase (`wuwmvtslltqhaycyukxk`)

---

## ✅ Summary

**7 Tools Available:**
1. ✅ `get_alerts_by_tag` - Find and filter alerts
2. ✅ `get_call_transcript` - Access full transcripts
3. ✅ `get_call_metadata` - Get call details
4. ✅ `analyze_multiple_alerts` - Pattern analysis
5. ✅ `create_action_plan` - Generate plans
6. ✅ `update_alert_status` - Single alert updates
7. ✅ `bulk_update_alerts` - Batch operations

**Ready for AI agent use! 🎉**

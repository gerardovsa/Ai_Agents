# 🤖 AI Agent Quick Reference - Veterinary Alerts Tools

## 🚀 Quick Start (Copy & Paste)

```python
from tools.implementations.veterinary_alerts_tools import (
    get_alerts_by_tag,
    get_call_transcript,
    get_call_metadata,
    analyze_multiple_alerts,
    create_action_plan,
    update_alert_status,
    bulk_update_alerts
)
```

---

## 📋 Most Common Commands

### Get Today's High Priority Alerts
```python
from datetime import datetime

result = get_alerts_by_tag(
    alert_tags="ALL",
    severity="HIGH",
    date_from=datetime.now().strftime('%Y-%m-%d'),
    limit=20
)

print(f"Found {result['alert_count']} high-priority alerts")
for alert in result['alerts']:
    print(f"- {alert['call_id']}: {alert['core_reason'][:50]}...")
```

### Get Revenue Leakage Alerts
```python
result = get_alerts_by_tag(
    alert_tags="REVENUE_LEAKAGE",
    priority=1,  # Immediate action needed
    date_from="2025-12-01"
)
```

### Get Call Details for Coaching
```python
call_id = "VET-Smith-12-12-2024_14:30"

# Get transcript
transcript_result = get_call_transcript(call_id)
transcript = transcript_result['transcript']

# Get metadata
meta_result = get_call_metadata(call_id)
staff = meta_result['metadata']['staff_name']
client = meta_result['metadata']['client_first_name']
```

### Analyze This Week's Patterns
```python
from datetime import datetime, timedelta

week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

analysis = analyze_multiple_alerts(
    alert_tags="ALL",
    date_from=week_ago,
    limit=50
)

print(f"Total alerts: {analysis['analysis']['total_alerts']}")
print(f"Top patterns: {analysis['analysis']['common_patterns']}")
print(f"Recommendations: {analysis['analysis']['recommended_actions']}")
```

### Create Coaching Plan
```python
# Step 1: Get alerts to address
alerts = get_alerts_by_tag(
    alert_tags="POOR_COMMUNICATION",
    severity="HIGH",
    limit=10
)

# Step 2: Extract call IDs
alert_ids = [alert['call_id'] for alert in alerts['alerts'][:5]]

# Step 3: Create plan
plan = create_action_plan(
    alert_ids=alert_ids,
    plan_type="coaching",
    timeline="1_week"
)

print(f"Plan ID: {plan['plan']['plan_id']}")
print(f"Phases: {len(plan['plan']['phases'])}")
for phase in plan['plan']['phases']:
    print(f"Phase {phase['phase']}: {phase['name']} ({phase['duration']})")
```

### Mark Alert as In Progress
```python
update_alert_status(
    call_id="VET-Smith-12-12-2024_14:30",
    status="In Progress",
    notes="Coaching session scheduled for tomorrow 2pm",
    actions_taken="Reviewed call recording, identified 3 improvement areas"
)
```

### Bulk Resolve After Training
```python
alert_ids = ["VET-...", "VET-...", "VET-..."]

bulk_update_alerts(
    call_ids=alert_ids,
    status="Resolved",
    notes="Team training completed on 2025-12-08"
)
```

---

## 🎯 Decision Tree

```
START
  │
  ├─ Need to find alerts?
  │   └─ Use: get_alerts_by_tag(alert_tags="...", severity="...", ...)
  │
  ├─ Need call details?
  │   ├─ Want transcript? → get_call_transcript(call_id)
  │   └─ Want metadata? → get_call_metadata(call_id)
  │
  ├─ Need to understand patterns?
  │   └─ Use: analyze_multiple_alerts(alert_tags="...", date_from="...")
  │
  ├─ Need to plan actions?
  │   └─ Use: create_action_plan(alert_ids=[...], plan_type="coaching")
  │
  └─ Need to update alerts?
      ├─ Single? → update_alert_status(call_id, status, notes)
      └─ Multiple? → bulk_update_alerts(call_ids=[...], status, notes)
```

---

## 🏷️ Alert Tags to Use

```python
# High Priority
"REVENUE_LEAKAGE"          # Missed revenue opportunities
"CLIENT_DISSATISFACTION"   # Unhappy clients
"COMPLIANCE_ISSUE"         # Protocol violations
"BOOKING_FAILURE"          # Failed bookings

# Medium Priority  
"MISSED_OPPORTUNITY"       # Missed upsell/booking chances
"POOR_COMMUNICATION"       # Communication quality
"QUALITY_CONCERN"          # Call quality issues

# Filter by multiple tags
alert_tags=["REVENUE_LEAKAGE", "MISSED_OPPORTUNITY", "BOOKING_FAILURE"]
```

---

## ⚡ Status Values

```python
"New"          # Alert just created
"In Progress"  # Manager reviewing/acting
"Resolved"     # Issue addressed
"Dismissed"    # Not relevant/duplicate
```

---

## 📊 Priority Levels

```python
1  # Immediate - needs action within 24 hours
2  # Near-term - needs action within 1 week
3  # Monitor - needs attention but not urgent
```

---

## 🔍 Severity Levels

```python
"HIGH"  # Critical issue, high impact
"MED"   # Moderate issue, medium impact
"LOW"   # Minor issue, low impact
```

---

## 🎭 Plan Types

```python
"coaching"        # Individual staff coaching plan
"systemic_fix"    # Process/protocol improvement plan
"client_recovery" # Client outreach and remediation plan
```

---

## ⏱️ Timeline Options

```python
"24_hours"  # Emergency response
"1_week"    # Standard response
"1_month"   # Long-term improvement
```

---

## 🔄 Typical Workflow

### Daily Alert Management
```python
# Morning: Get today's alerts
alerts = get_alerts_by_tag(alert_tags="ALL", date_from="today", severity="HIGH")

# Review each high-priority alert
for alert in alerts['alerts']:
    transcript = get_call_transcript(alert['call_id'])
    metadata = get_call_metadata(alert['call_id'])
    
    # Mark as in progress
    update_alert_status(
        call_id=alert['call_id'],
        status="In Progress",
        notes="Under review"
    )

# End of day: Close resolved alerts
resolved_ids = [...]  # Alerts you addressed
bulk_update_alerts(call_ids=resolved_ids, status="Resolved")
```

### Weekly Coaching Planning
```python
# Monday: Analyze last week
week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
analysis = analyze_multiple_alerts(date_from=week_ago, limit=50)

# Tuesday: Create coaching plan
alert_ids = [...]  # Top 10 alerts from analysis
plan = create_action_plan(alert_ids=alert_ids, plan_type="coaching", timeline="1_week")

# Throughout week: Execute coaching sessions

# Friday: Mark completed
bulk_update_alerts(call_ids=alert_ids, status="Resolved", notes="Coaching completed")
```

### Monthly Pattern Analysis
```python
# Get all alerts from last month
month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
alerts = get_alerts_by_tag(alert_tags="ALL", date_from=month_ago, limit=200)

# Analyze patterns
analysis = analyze_multiple_alerts(date_from=month_ago, limit=100)

# Identify systemic issues
if analysis['analysis']['recommended_actions']:
    # Create systemic fix plan
    plan = create_action_plan(
        alert_ids=[...],  # Representative samples
        plan_type="systemic_fix",
        timeline="1_month"
    )
```

---

## 💡 Pro Tips

### 1. Always Check Success
```python
result = get_alerts_by_tag(...)
if result['success']:
    # Use result['alerts']
else:
    # Handle error: result['error']
```

### 2. Use Summaries
```python
result = get_alerts_by_tag(...)
summary = result['summary']
print(f"HIGH: {summary['by_severity']['HIGH']}")
print(f"Immediate: {summary['by_priority'][1]}")
```

### 3. Filter Progressively
```python
# Start broad
all_alerts = get_alerts_by_tag(alert_tags="ALL", date_from=week_ago)

# Then filter in code
high_severity = [a for a in all_alerts['alerts'] if a['severity'] == 'HIGH']
immediate = [a for a in high_severity if a['priority'] == 1]
```

### 4. Combine Data Sources
```python
# Get alert
alert = get_alerts_by_tag(alert_tags="REVENUE_LEAKAGE", limit=1)['alerts'][0]

# Get transcript for context
transcript = get_call_transcript(alert['call_id'])

# Get metadata for coaching prep
metadata = get_call_metadata(alert['call_id'])

# Now you have complete picture
```

### 5. Use Bulk Operations
```python
# Instead of:
for call_id in call_ids:
    update_alert_status(call_id, "Resolved", "Done")

# Do this:
bulk_update_alerts(call_ids, "Resolved", "Done")
```

---

## ❌ Common Errors

### No alerts found
```python
result = get_alerts_by_tag(alert_tags="TYPO_TAG", ...)
# result['alert_count'] == 0
# Check: alert tag spelling, date range, database has data
```

### Call ID not found
```python
result = get_call_transcript("WRONG-ID")
# result['success'] == False
# Check: call_id format (VET-Name-DD-MM-YYYY_HH:MM)
```

### Empty analysis
```python
result = analyze_multiple_alerts(alert_ids=[])
# result['analysis']['total_alerts'] == 0
# Check: provide alert_ids or alert_tags
```

---

## 📚 Full Documentation

See: `VETERINARY_ALERTS_TOOLS_README.md` (complete guide)  
See: `VETERINARY_ALERTS_IMPLEMENTATION_COMPLETE.md` (implementation details)

---

## 🎉 You're Ready!

**7 tools available, all tested, all working!**

Start with:
```python
from tools.implementations.veterinary_alerts_tools import get_alerts_by_tag

result = get_alerts_by_tag(alert_tags="ALL", date_from="2025-12-01")
print(f"Found {result['alert_count']} alerts")
```

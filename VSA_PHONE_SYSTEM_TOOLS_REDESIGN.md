# 📞 VSA Phone System AI Tools - Prompt-Centric Redesign
## Veterinary Call Analysis Tools with Embedded Prompts

**Date:** December 10, 2025  
**Philosophy:** Each tool = **AI Prompt + Context + SQL Queries**  
**Naming:** `phone_[category]_[action]` makes it crystal clear this is phone system data

---

## 🎯 Design Philosophy

### OLD Naming (Confusing)
```
vsa_generate_coaching          ← What does "vsa" mean to AI?
vsa_get_full_call_context      ← Is this VSA-specific or general?
vsa_query_alerts_sql           ← Unclear what database
```

### NEW Naming (Clear)
```
phone_prompt_alert_coaching     ← "I'm a PROMPT for coaching on PHONE alerts"
phone_get_full_call            ← "I get PHONE call data"
phone_query_library            ← "I'm a library of PHONE queries"
phone_alert_trends             ← "I analyze PHONE alert trends"
```

### Benefits
✅ **AI knows it's phone system data** (not email, chat, etc.)  
✅ **"prompt" tools signal: "I have specific instructions to follow"**  
✅ **Variable-driven** (date range, staff filter, call direction)  
✅ **SQL query libraries** (pre-built queries AI can trigger)

---

## 📚 Complete Tool Library (20 Tools)

### Category 1: AI Prompt Tools (Specialized Instructions)

#### Tool 1: `phone_prompt_alert_coaching` 🔴 **PRIMARY COACHING**
**Purpose:** Generate coaching document with embedded veterinary-specific prompt  
**What Makes It Special:** Contains the full coaching prompt + context builder

```json
{
  "name": "phone_prompt_alert_coaching",
  "description": "Generate personalized veterinary staff coaching using specialized prompt. Analyzes phone call transcript and creates constructive feedback document with specific examples, action items, and practice scenarios.",
  "category": "phone_prompts",
  "embedded_prompt": "Built-in veterinary coaching expert persona",
  "input_schema": {
    "type": "object",
    "properties": {
      "call_id": {
        "type": "string",
        "description": "Call ID to coach on",
        "required": true,
        "example": "VET-Smith-12-10-2024_14:30"
      },
      "alert_type": {
        "type": "string",
        "description": "Alert code that triggered coaching need",
        "enum": ["REVENUE_LEAKAGE", "MISSED_OPPORTUNITY", "POOR_COMMUNICATION", "BOOKING_FAILURE"],
        "required": true
      },
      "coaching_focus": {
        "type": "string",
        "description": "Specific skill area to focus on",
        "examples": [
          "Dental upselling",
          "Active listening",
          "Appointment booking",
          "Client rapport",
          "Follow-up scheduling"
        ],
        "required": false
      },
      "staff_name": {
        "type": "string",
        "description": "Staff member to coach",
        "required": true
      },
      "include_role_play": {
        "type": "boolean",
        "description": "Include practice scenario based on this call",
        "default": true
      },
      "tone": {
        "type": "string",
        "enum": ["constructive", "direct", "encouraging"],
        "description": "Coaching tone to use",
        "default": "constructive"
      }
    },
    "required": ["call_id", "alert_type", "staff_name"]
  },
  "embedded_prompt_structure": {
    "persona": "Expert veterinary practice coach with 15+ years experience",
    "sections_generated": [
      "1. Call Overview (what happened)",
      "2. What Went Well (positive reinforcement)",
      "3. Opportunity for Growth (specific to alert)",
      "4. Coaching Tips (actionable advice)",
      "5. Practice Scenario (30-second role-play)",
      "6. Follow-up Plan (short/long term goals)",
      "7. Encouragement (motivational close)"
    ],
    "output_format": "Markdown with sections, bullet points, and quotes from transcript"
  },
  "sql_queries_triggered": [
    "Get full transcript from call_full_transcript_and_full_analysis",
    "Get alert details from call_manager_alerts",
    "Get call metadata from veterinary_calls",
    "Get staff previous alerts for context"
  ]
}
```

---

#### Tool 2: `phone_prompt_prioritization` 🔴 **ALERT TRIAGE**
**Purpose:** AI analyzes alerts and prioritizes them with embedded decision logic

```json
{
  "name": "phone_prompt_prioritization",
  "description": "Analyze phone alerts and prioritize them using embedded AI decision framework. Considers severity, revenue impact, urgency, and staff performance to create action-ranked list.",
  "category": "phone_prompts",
  "embedded_prompt": "Priority decision framework with scoring algorithm",
  "input_schema": {
    "type": "object",
    "properties": {
      "date_range": {
        "type": "object",
        "properties": {
          "from": "string (date)",
          "to": "string (date)"
        },
        "description": "Date range to analyze",
        "default": "Today"
      },
      "staff_filter": {
        "type": "array",
        "items": "string",
        "description": "Filter by specific staff members (empty = all)",
        "default": []
      },
      "alert_types": {
        "type": "array",
        "items": "string",
        "description": "Filter by alert types (empty = all)",
        "default": []
      },
      "prioritization_factors": {
        "type": "object",
        "properties": {
          "revenue_weight": { "type": "number", "default": 0.4 },
          "severity_weight": { "type": "number", "default": 0.3 },
          "urgency_weight": { "type": "number", "default": 0.2 },
          "frequency_weight": { "type": "number", "default": 0.1 }
        }
      },
      "max_results": {
        "type": "integer",
        "description": "Number of top priority alerts to return",
        "default": 10
      }
    }
  },
  "embedded_prompt_structure": {
    "decision_framework": [
      "1. Calculate revenue impact score (0-100)",
      "2. Calculate severity score (HIGH=100, MED=60, LOW=30)",
      "3. Calculate urgency score based on follow_up_window",
      "4. Calculate frequency score (repeat offender = higher)",
      "5. Weighted total score",
      "6. Rank and return top N"
    ],
    "output": {
      "prioritized_list": "Array of alerts sorted by score",
      "recommended_actions": "What to do first, second, third",
      "time_estimate": "Estimated time to address each",
      "reasoning": "Why each alert ranked where it is"
    }
  }
}
```

---

#### Tool 3: `phone_prompt_staff_analysis`
**Purpose:** Comprehensive staff performance analysis with coaching recommendations

```json
{
  "name": "phone_prompt_staff_analysis",
  "description": "Deep analysis of staff member's phone performance using embedded analytical framework. Identifies patterns, strengths, weaknesses, and generates development plan.",
  "category": "phone_prompts",
  "input_schema": {
    "staff_name": "string (required)",
    "time_period": "string (week|month|quarter) default: month",
    "comparison_mode": "string (peer|self|none) - compare to peers or previous period",
    "include_coaching_plan": "boolean (default: true)"
  },
  "embedded_prompt_structure": {
    "analysis_sections": [
      "1. Performance Overview (calls, alerts, conversion rates)",
      "2. Strengths Analysis (what they do well)",
      "3. Opportunity Areas (specific improvements needed)",
      "4. Pattern Detection (recurring issues)",
      "5. Peer Comparison (if enabled)",
      "6. Coaching Recommendations (3-5 actionable items)",
      "7. 30-Day Development Plan"
    ],
    "metrics_calculated": [
      "Alert rate (alerts/total_calls)",
      "Revenue leakage rate",
      "Booking success rate",
      "Average call duration",
      "Client satisfaction indicators"
    ]
  },
  "sql_queries_triggered": [
    "Staff call history query",
    "Staff alert breakdown query",
    "Peer comparison query",
    "Trend analysis query"
  ]
}
```

---

#### Tool 4: `phone_prompt_revenue_recovery`
**Purpose:** Actionable plan to recover lost revenue from alerts

```json
{
  "name": "phone_prompt_revenue_recovery",
  "description": "Generate revenue recovery action plan from phone alerts. AI analyzes missed opportunities and creates specific steps to recapture revenue.",
  "category": "phone_prompts",
  "input_schema": {
    "alert_ids": "array of call_ids (required)",
    "recovery_window": "string (1_week|2_weeks|1_month) - timeframe to act",
    "include_client_scripts": "boolean - generate client callback scripts"
  },
  "embedded_prompt_structure": {
    "recovery_plan_sections": [
      "1. Total Revenue at Risk ($)",
      "2. Recoverable Amount (realistic %)",
      "3. Client Callback Priority List",
      "4. Callback Scripts (word-for-word)",
      "5. Upsell Approach per Client",
      "6. Timeline (day-by-day actions)",
      "7. Success Tracking Metrics"
    ]
  }
}
```

---

#### Tool 5: `phone_prompt_trend_analysis`
**Purpose:** Identify patterns and trends across phone calls/alerts

```json
{
  "name": "phone_prompt_trend_analysis",
  "description": "Analyze phone system trends using embedded pattern detection framework. Identifies emerging issues, seasonal patterns, and systemic problems.",
  "category": "phone_prompts",
  "input_schema": {
    "analysis_type": "string (daily|weekly|monthly|custom)",
    "date_range": "object {from, to}",
    "focus_area": "string (staff|alerts|revenue|client_satisfaction)",
    "include_predictions": "boolean - forecast next period"
  },
  "embedded_prompt_structure": {
    "trend_analysis": [
      "1. Volume Trends (calls/alerts over time)",
      "2. Category Trends (which alert types increasing/decreasing)",
      "3. Staff Trends (who's improving/declining)",
      "4. Revenue Trends ($ lost over time)",
      "5. Pattern Detection (day-of-week, time-of-day)",
      "6. Predictions (next 30 days forecast)",
      "7. Recommended Actions"
    ]
  }
}
```

---

### Category 2: Phone Data Retrieval Tools (Variable-Driven)

#### Tool 6: `phone_get_full_call` 🔴 **MASTER RETRIEVAL**
**Purpose:** Get complete call data with full variable control

```json
{
  "name": "phone_get_full_call",
  "description": "Retrieve complete phone call data with transcript, analysis, alerts, and metadata. Highly variable-driven for precise filtering.",
  "category": "phone_data",
  "input_schema": {
    "type": "object",
    "properties": {
      "call_id": {
        "type": "string",
        "description": "Specific call ID (if known)",
        "required": false,
        "example": "VET-Smith-12-10-2024_14:30"
      },
      "date_range": {
        "type": "object",
        "properties": {
          "from": { "type": "string", "format": "date" },
          "to": { "type": "string", "format": "date" }
        },
        "description": "Date range to search",
        "default": "Today"
      },
      "staff_name": {
        "type": "string",
        "description": "Filter by staff member",
        "example": "Sarah Thompson"
      },
      "client_name": {
        "type": "string",
        "description": "Filter by client name"
      },
      "call_direction": {
        "type": "string",
        "enum": ["inbound", "outbound", "both"],
        "description": "Call direction filter",
        "default": "both"
      },
      "has_alerts": {
        "type": "boolean",
        "description": "Only return calls with alerts",
        "default": false
      },
      "alert_severity": {
        "type": "string",
        "enum": ["HIGH", "MED", "LOW", "ALL"],
        "description": "Filter by alert severity",
        "default": "ALL"
      },
      "min_duration_seconds": {
        "type": "integer",
        "description": "Minimum call duration",
        "default": 0
      },
      "max_duration_seconds": {
        "type": "integer",
        "description": "Maximum call duration"
      },
      "include_transcript": {
        "type": "boolean",
        "description": "Include full transcript text",
        "default": true
      },
      "include_analysis": {
        "type": "boolean",
        "description": "Include AI analysis",
        "default": true
      },
      "max_results": {
        "type": "integer",
        "description": "Maximum number of calls to return",
        "default": 50,
        "maximum": 500
      },
      "sort_by": {
        "type": "string",
        "enum": ["date_desc", "date_asc", "duration", "alert_severity"],
        "default": "date_desc"
      }
    }
  },
  "output_schema": {
    "success": true,
    "total_matches": 127,
    "returned_count": 50,
    "calls": [
      {
        "call_id": "string",
        "metadata": { /* full metadata */ },
        "transcript": { /* full transcript */ },
        "analysis": { /* AI analysis */ },
        "alerts": [ /* array of alerts */ ]
      }
    ]
  }
}
```

---

#### Tool 7: `phone_get_calls`
**Purpose:** Simplified call retrieval (no transcript/analysis, just metadata)

```json
{
  "name": "phone_get_calls",
  "description": "Get phone call metadata ONLY (no transcript/analysis). Fast for listing/filtering large numbers of calls.",
  "category": "phone_data",
  "input_schema": {
    "date_range": "object {from, to}",
    "staff_name": "string (optional)",
    "client_name": "string (optional)",
    "call_direction": "string (inbound|outbound|both)",
    "has_alerts": "boolean",
    "max_results": "integer (default: 100)",
    "fields_to_return": {
      "type": "array",
      "description": "Specific fields to return (reduces payload)",
      "items": "string",
      "examples": ["call_id", "call_date", "staff_name", "duration", "alert_count"]
    }
  }
}
```

---

#### Tool 8: `phone_get_transcript`
**Purpose:** Get ONLY transcript (no alerts/metadata)

```json
{
  "name": "phone_get_transcript",
  "description": "Retrieve just the call transcript text. Use when you only need conversation content.",
  "input_schema": {
    "call_id": "string (required)",
    "format": "string (full|summary|timestamped) default: full",
    "include_speaker_labels": "boolean (default: true)"
  }
}
```

---

#### Tool 9: `phone_get_alerts`
**Purpose:** Get alert data without full call context

```json
{
  "name": "phone_get_alerts",
  "description": "Get phone call alerts without loading full transcripts. Fast for alert analysis.",
  "input_schema": {
    "date_range": "object {from, to}",
    "staff_name": "string (optional)",
    "alert_types": "array (optional) - filter by alert codes",
    "severity": "string (HIGH|MED|LOW|ALL)",
    "priority": "integer (1|2|3|ALL)",
    "status": "string (Open|In Progress|Completed|ALL)",
    "max_results": "integer (default: 100)"
  },
  "output_schema": {
    "alerts": [
      {
        "call_id": "string",
        "alert_slot": 1,
        "alert_code": "REVENUE_LEAKAGE",
        "severity": "HIGH",
        "core_reason": "string",
        "estimated_revenue_loss": "$300",
        "staff_name": "Sarah Thompson",
        "created_at": "2025-12-10T14:30:00Z"
      }
    ],
    "summary": {
      "total_count": 45,
      "by_severity": { "HIGH": 12, "MED": 23, "LOW": 10 },
      "total_revenue_at_risk": "$8,400"
    }
  }
}
```

---

### Category 3: Phone Analysis Tools

#### Tool 10: `phone_alert_trends`
**Purpose:** Pre-built trend analysis (no prompt, just data)

```json
{
  "name": "phone_alert_trends",
  "description": "Get phone alert trend data (daily/weekly/monthly aggregations). Returns data for charting/analysis.",
  "category": "phone_analysis",
  "input_schema": {
    "trend_type": "string (daily|weekly|monthly)",
    "date_range": "object {from, to}",
    "group_by": "string (staff|alert_type|severity|day_of_week)",
    "include_comparison": "boolean - compare to previous period"
  },
  "output_schema": {
    "trend_data": [
      { "date": "2025-12-01", "count": 15, "revenue_loss": 4200 },
      { "date": "2025-12-02", "count": 12, "revenue_loss": 3600 }
    ],
    "comparison": {
      "current_period": { "total": 127, "avg_per_day": 18 },
      "previous_period": { "total": 98, "avg_per_day": 14 },
      "change_percent": "+29.6%"
    }
  }
}
```

---

#### Tool 11: `phone_revenue_analysis`
**Purpose:** Revenue impact calculations

```json
{
  "name": "phone_revenue_analysis",
  "description": "Calculate revenue impact from phone alerts. Provides $ estimates for missed opportunities.",
  "input_schema": {
    "call_ids": "array of strings (optional)",
    "date_range": "object (optional)",
    "breakdown_by": "string (service_type|staff|alert_type)"
  },
  "output_schema": {
    "total_revenue_loss": 8400,
    "recoverable_amount": 3360,
    "recovery_percentage": 40,
    "breakdown": {
      "Dental cleanings": { "lost": 4200, "count": 14, "avg_per_missed": 300 },
      "Follow-up appointments": { "lost": 2800, "count": 7, "avg_per_missed": 400 }
    }
  }
}
```

---

#### Tool 12: `phone_staff_performance`
**Purpose:** Staff metrics (no prompt, just data)

```json
{
  "name": "phone_staff_performance",
  "description": "Get staff performance metrics from phone calls. Returns data only, no AI analysis.",
  "input_schema": {
    "staff_name": "string (required)",
    "time_period": "string (week|month|quarter)",
    "compare_to": "string (peers|previous_period|none)",
    "metrics_to_include": {
      "type": "array",
      "items": "string",
      "examples": ["alert_rate", "call_count", "avg_duration", "booking_rate"]
    }
  }
}
```

---

#### Tool 13: `phone_pattern_detection`
**Purpose:** Automated pattern finding

```json
{
  "name": "phone_pattern_detection",
  "description": "Detect patterns in phone calls/alerts using ML algorithms. Finds recurring issues, time patterns, correlations.",
  "input_schema": {
    "date_range": "object {from, to}",
    "pattern_types": {
      "type": "array",
      "items": "string",
      "enum": [
        "time_of_day",
        "day_of_week",
        "staff_correlations",
        "alert_sequences",
        "client_patterns",
        "seasonal_trends"
      ]
    },
    "min_confidence": "number (0-1) - minimum pattern confidence to report"
  },
  "output_schema": {
    "patterns_found": [
      {
        "pattern_type": "time_of_day",
        "description": "REVENUE_LEAKAGE alerts 3x higher between 2-4pm",
        "confidence": 0.87,
        "sample_size": 156,
        "recommendation": "Schedule dental training during 1-2pm"
      }
    ]
  }
}
```

---

### Category 4: Phone Query Library (SQL Templates)

#### Tool 14: `phone_query_library` 🔴 **SQL POWERHOUSE**
**Purpose:** Library of pre-built SQL queries AI can execute

```json
{
  "name": "phone_query_library",
  "description": "Execute pre-built SQL queries against phone system database. Contains 50+ optimized queries for common analysis tasks.",
  "category": "phone_queries",
  "security": {
    "read_only": true,
    "allowed_tables": [
      "veterinary_calls",
      "call_manager_alerts",
      "call_full_transcript_and_full_analysis"
    ]
  },
  "input_schema": {
    "query_id": {
      "type": "string",
      "description": "Pre-built query to execute",
      "enum": [
        "top_staff_by_alerts",
        "revenue_loss_by_day",
        "alert_frequency_by_hour",
        "repeat_client_issues",
        "staff_improvement_tracking",
        "alert_correlation_analysis",
        "booking_success_rates",
        "call_duration_analysis",
        "pet_species_alert_patterns",
        /* ... 40+ more queries */
      ],
      "required": true
    },
    "parameters": {
      "type": "object",
      "description": "Dynamic parameters for query",
      "examples": {
        "date_from": "2025-12-01",
        "date_to": "2025-12-10",
        "staff_name": "Sarah Thompson",
        "limit": 20
      }
    },
    "format": {
      "type": "string",
      "enum": ["json", "csv", "table"],
      "default": "json"
    }
  },
  "query_library": {
    "top_staff_by_alerts": {
      "description": "Show staff ranked by alert rate",
      "sql": "SELECT key_staffname, COUNT(DISTINCT call_id) as calls, COUNT(DISTINCT CASE WHEN manager_alerts_tags != 'NONE' THEN call_id END) as alerts, ROUND(100.0 * alerts / calls, 1) as alert_rate FROM veterinary_calls WHERE key_call_date >= {{date_from}} GROUP BY key_staffname ORDER BY alert_rate DESC LIMIT {{limit}}",
      "parameters": ["date_from", "limit"],
      "typical_use": "Manager asks 'who has the most alerts?'"
    },
    "revenue_loss_by_day": {
      "description": "Daily revenue loss breakdown",
      "sql": "SELECT DATE(created_at) as date, COUNT(*) as alert_count, SUM(CASE WHEN alert_1_code = 'REVENUE_LEAKAGE' THEN 1 ELSE 0 END) as revenue_leakage_count FROM call_manager_alerts WHERE created_at >= {{date_from}} GROUP BY date ORDER BY date",
      "parameters": ["date_from"],
      "typical_use": "Trend analysis of revenue loss over time"
    },
    /* ... 48+ more pre-built queries ... */
  }
}
```

---

#### Tool 15: `phone_query_custom`
**Purpose:** Execute custom SQL (with safety)

```json
{
  "name": "phone_query_custom",
  "description": "Execute custom SQL query on phone database. AI can construct complex queries for unique analysis needs.",
  "category": "phone_queries",
  "security": {
    "read_only": true,
    "query_validation": "Blocks DROP, DELETE, UPDATE, INSERT, ALTER",
    "timeout_seconds": 30,
    "max_rows": 1000
  },
  "input_schema": {
    "sql": "string (required) - SQL query to execute",
    "parameters": "object (optional) - parameterized values",
    "explain_query": "boolean - return query execution plan"
  }
}
```

---

### Category 5: Phone Management Tools

#### Tool 16: `phone_update_alert_status`
```json
{
  "name": "phone_update_alert_status",
  "description": "Update phone alert status/notes/actions",
  "input_schema": {
    "call_id": "string (required)",
    "status": "string (Open|In Progress|Completed|Ignored)",
    "notes": "string (optional)",
    "actions": "string (optional)"
  }
}
```

#### Tool 17: `phone_add_notes`
```json
{
  "name": "phone_add_notes",
  "description": "Add manager notes to phone call",
  "input_schema": {
    "call_id": "string (required)",
    "notes": "string (required)",
    "mode": "string (append|replace)"
  }
}
```

#### Tool 18: `phone_export_report`
```json
{
  "name": "phone_export_report",
  "description": "Generate formatted report from phone data",
  "input_schema": {
    "report_type": "string (daily|weekly|staff|alert_summary)",
    "date_range": "object {from, to}",
    "format": "string (pdf|csv|excel|html)",
    "email_to": "string (optional)",
    "include_charts": "boolean"
  }
}
```

#### Tool 19: `phone_schedule_follow_up`
```json
{
  "name": "phone_schedule_follow_up",
  "description": "Create follow-up task from phone alert",
  "input_schema": {
    "call_id": "string (required)",
    "follow_up_type": "string (coaching|client_callback|process_review)",
    "due_date": "string (date)",
    "assigned_to": "string",
    "notes": "string"
  }
}
```

#### Tool 20: `phone_search_similar`
```json
{
  "name": "phone_search_similar",
  "description": "Find similar phone calls/alerts (pattern matching)",
  "input_schema": {
    "reference_call_id": "string (required)",
    "similarity_criteria": ["staff", "alert_type", "keywords", "duration"],
    "date_range_days": "integer (default: 30)",
    "max_results": "integer (default: 10)"
  }
}
```

---

## 🎯 How AI Discovers and Uses Tools

### Scenario 1: Manager Asks for Coaching

**Manager:** "Generate coaching for Sarah's call VET-Smith-12-10-2024_14:30"

**AI Thinks:**
1. "I need coaching... let me check tool names"
2. Sees: `phone_prompt_alert_coaching` ← "PROMPT" tells me this has coaching instructions
3. Reads tool description: "Generate personalized veterinary staff coaching using specialized prompt"
4. Calls tool with: `{call_id: "...", staff_name: "Sarah Thompson", alert_type: "REVENUE_LEAKAGE"}`

**Tool Executes:**
1. Fetches full call context (transcript, alerts, metadata)
2. Loads embedded coaching prompt
3. Calls Claude with structured prompt
4. Returns formatted coaching document

---

### Scenario 2: Manager Asks About Trends

**Manager:** "What are the alert trends this month?"

**AI Thinks:**
1. "Trends... let me look for trend tools"
2. Sees two options:
   - `phone_alert_trends` ← Data only (fast)
   - `phone_prompt_trend_analysis` ← AI analysis with predictions
3. Manager didn't ask for predictions, so use data tool first
4. Calls: `phone_alert_trends` with `{trend_type: "daily", date_range: {from: "2025-12-01", to: "2025-12-10"}}`

**If Manager Follows Up:** "What does this mean? What should I do?"

**AI Then:**
1. Now use prompt tool: `phone_prompt_trend_analysis`
2. Pass trend data to embedded analysis prompt
3. Get AI-generated insights + recommendations

---

### Scenario 3: Manager Asks Complex Question

**Manager:** "Which staff member has the worst alert rate on Mondays between 2-4pm?"

**AI Thinks:**
1. "This needs custom SQL... `phone_query_library` or `phone_query_custom`?"
2. Check if pre-built query exists in library
3. No exact match, so use `phone_query_custom`
4. Construct SQL:
```sql
SELECT 
    key_staffname,
    COUNT(*) as monday_2_4pm_calls,
    COUNT(CASE WHEN manager_alerts_tags != 'NONE' THEN 1 END) as alerts,
    ROUND(100.0 * alerts / calls, 1) as alert_rate
FROM veterinary_calls vc
LEFT JOIN call_manager_alerts cma ON vc.call_id = cma.call_id
WHERE EXTRACT(DOW FROM key_call_date) = 1  -- Monday
  AND EXTRACT(HOUR FROM key_time::time) BETWEEN 14 AND 16
  AND key_call_date >= '2025-11-01'
GROUP BY key_staffname
HAVING COUNT(*) >= 5  -- Minimum sample size
ORDER BY alert_rate DESC
LIMIT 10;
```

---

## 📦 Registry Integration

### Schema File: `phone_system_tools.json`

```json
{
  "platform": "phone_system",
  "version": "2.0.0",
  "description": "Veterinary phone call analysis tools with embedded AI prompts and SQL query library",
  "database": {
    "provider": "Supabase",
    "url": "https://wuwmvtslltqhaycyukxk.supabase.co",
    "tables": [
      "veterinary_calls",
      "call_manager_alerts",
      "call_full_transcript_and_full_analysis"
    ]
  },
  "tool_categories": {
    "phone_prompts": {
      "description": "AI prompt tools with embedded instructions",
      "count": 5,
      "tools": [
        "phone_prompt_alert_coaching",
        "phone_prompt_prioritization",
        "phone_prompt_staff_analysis",
        "phone_prompt_revenue_recovery",
        "phone_prompt_trend_analysis"
      ]
    },
    "phone_data": {
      "description": "Data retrieval tools (variable-driven)",
      "count": 4,
      "tools": [
        "phone_get_full_call",
        "phone_get_calls",
        "phone_get_transcript",
        "phone_get_alerts"
      ]
    },
    "phone_analysis": {
      "description": "Analysis tools (data output, no prompts)",
      "count": 4,
      "tools": [
        "phone_alert_trends",
        "phone_revenue_analysis",
        "phone_staff_performance",
        "phone_pattern_detection"
      ]
    },
    "phone_queries": {
      "description": "SQL query tools (library + custom)",
      "count": 2,
      "tools": [
        "phone_query_library",
        "phone_query_custom"
      ]
    },
    "phone_management": {
      "description": "Management actions (update, export, schedule)",
      "count": 5,
      "tools": [
        "phone_update_alert_status",
        "phone_add_notes",
        "phone_export_report",
        "phone_schedule_follow_up",
        "phone_search_similar"
      ]
    }
  },
  "tools": [
    /* All 20 tool definitions */
  ]
}
```

---

## 🎨 Smart Tool Selector Integration

### Add to `smart_tool_selector.py`

```python
"phone_system": {
    "priority": 1,
    "keywords": [
        "phone", "call", "veterinary", "alert", "coaching", 
        "transcript", "staff", "revenue", "client", "pet",
        "dental", "booking", "communication", "performance"
    ],
    "platforms": ["phone_system"],
    "smart_tools": [
        "phone_prompt_alert_coaching",
        "phone_get_full_call",
        "phone_query_library"
    ],
    "typical_queries": [
        "Generate coaching for...",
        "Show me alerts from...",
        "Which staff has most...",
        "What's the revenue impact...",
        "Find calls where..."
    ]
}
```

---

## 💡 Additional Tool Ideas

### Tool 21: `phone_prompt_client_callback_script`
**Purpose:** Generate callback script for revenue recovery
- Input: Call ID + missed opportunity
- Output: Word-for-word script to recover sale

### Tool 22: `phone_prompt_training_needs`
**Purpose:** Identify training gaps across team
- Analyzes all alerts for patterns
- Recommends specific training modules

### Tool 23: `phone_alert_prediction`
**Purpose:** Predict which future calls likely to have alerts
- ML model based on historical patterns
- Proactive coaching recommendations

### Tool 24: `phone_benchmark_comparison`
**Purpose:** Compare practice to industry benchmarks
- Alert rates vs averages
- Revenue capture vs best practices

### Tool 25: `phone_client_sentiment`
**Purpose:** Analyze client sentiment from transcripts
- Positive/negative language detection
- Risk flagging for client retention

---

## 🚀 Implementation Priority

### Phase 1 (Week 1): Core Prompt Tools
1. `phone_prompt_alert_coaching` ← Extract from Python dashboard
2. `phone_get_full_call` ← Master data retrieval
3. `phone_query_library` ← 10 most common SQL queries

### Phase 2 (Week 2): Data & Analysis
4. `phone_get_alerts`
5. `phone_alert_trends`
6. `phone_revenue_analysis`
7. `phone_staff_performance`

### Phase 3 (Week 3): Advanced Prompts
8. `phone_prompt_prioritization`
9. `phone_prompt_staff_analysis`
10. `phone_prompt_trend_analysis`

### Phase 4 (Week 4): Management Tools
11. `phone_update_alert_status`
12. `phone_add_notes`
13. `phone_export_report`
14. Remaining tools

---

## 📊 Tool Usage Examples

### Example 1: Complete Coaching Workflow

```javascript
// Manager drags alert card to AI chat

// AI automatically calls:
1. phone_get_full_call({
     call_id: "VET-Smith-12-10-2024_14:30",
     include_transcript: true,
     include_analysis: true
   })
   
// Manager: "Generate coaching for Sarah"

2. phone_prompt_alert_coaching({
     call_id: "VET-Smith-12-10-2024_14:30",
     alert_type: "REVENUE_LEAKAGE",
     staff_name: "Sarah Thompson",
     coaching_focus: "Dental upselling"
   })
   
// Manager: "Save my notes that we discussed this"

3. phone_add_notes({
     call_id: "VET-Smith-12-10-2024_14:30",
     notes: "Discussed dental opportunity. Sarah will practice with Mike tomorrow."
   })
```

### Example 2: Revenue Analysis

```javascript
// Manager: "How much money did we lose this week?"

1. phone_revenue_analysis({
     date_range: {from: "2025-12-04", to: "2025-12-10"},
     breakdown_by: "service_type"
   })
   // Returns: $8,400 lost, $3,360 recoverable

// Manager: "Create a recovery plan"

2. phone_prompt_revenue_recovery({
     date_range: {from: "2025-12-04", to: "2025-12-10"},
     recovery_window: "1_week",
     include_client_scripts: true
   })
   // Returns: Prioritized callback list + scripts
```

---

## 🎯 Key Benefits of This Redesign

### 1. **Clear Naming**
✅ `phone_` prefix = phone system data  
✅ `_prompt_` = has embedded AI instructions  
✅ `_query_` = SQL operations  
✅ `_get_` = data retrieval  

### 2. **Variable-Driven**
✅ Date range filters  
✅ Staff filters  
✅ Call direction filters  
✅ Result limits  
✅ Field selection  

### 3. **Embedded Prompts**
✅ Coaching prompt extracted  
✅ Analysis frameworks built-in  
✅ Decision logic embedded  
✅ Consistent output structure  

### 4. **SQL Power**
✅ 50+ pre-built queries  
✅ Custom query capability  
✅ Safety constraints  
✅ Optimized performance  

### 5. **Scalable**
✅ Easy to add new prompts  
✅ Easy to add new queries  
✅ Modular tool categories  
✅ Registry auto-discovery  

---

Would you like me to start implementing Phase 1 with these tool designs?
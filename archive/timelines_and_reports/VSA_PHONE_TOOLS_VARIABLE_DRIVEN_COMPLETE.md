# 📞 VSA Phone System Tools - Complete Variable-Driven Architecture
## Every Tool Has Full Variable Control

**Date:** December 10, 2025  
**Philosophy:** Maximum flexibility through comprehensive variable parameters  
**Design:** No hardcoded values, AI can control everything

---

## 🎯 Variable-Driven Design Principles

### Universal Variables (Available in ALL Tools)
```json
{
  "date_range": {
    "from": "string (date) - Start date",
    "to": "string (date) - End date",
    "presets": ["today", "yesterday", "this_week", "last_week", "this_month", "last_month", "last_7_days", "last_30_days", "custom"]
  },
  "staff_filter": {
    "type": "array|string",
    "options": ["specific_names", "all", "exclude_list"],
    "examples": ["Sarah Thompson", "Mike Chen", "Emily Rodriguez"]
  },
  "max_results": {
    "type": "integer",
    "default": 50,
    "range": [1, 1000],
    "description": "Limit number of results returned"
  },
  "sort_by": {
    "type": "string",
    "options": ["date_desc", "date_asc", "severity", "priority", "duration", "alert_count", "revenue_impact"],
    "default": "date_desc"
  },
  "output_format": {
    "type": "string",
    "options": ["json", "csv", "table", "summary", "detailed"],
    "default": "json"
  }
}
```

---

## 📚 Complete Tool Library with Full Variables

### Category 1: AI Prompt Tools (Specialized Instructions)

#### Tool 1: `phone_prompt_alert_coaching` 🔴
**Complete Variable Control:**

```json
{
  "name": "phone_prompt_alert_coaching",
  "description": "Generate personalized coaching with full variable control over content, tone, format, and delivery",
  "category": "phone_prompts",
  "input_schema": {
    "type": "object",
    "properties": {
      
      // REQUIRED VARIABLES
      "call_id": {
        "type": "string",
        "required": true,
        "description": "Call ID to coach on",
        "example": "VET-Smith-12-10-2024_14:30"
      },
      "staff_name": {
        "type": "string",
        "required": true,
        "description": "Staff member to coach"
      },
      "alert_type": {
        "type": "string",
        "required": true,
        "enum": [
          "REVENUE_LEAKAGE",
          "MISSED_OPPORTUNITY", 
          "POOR_COMMUNICATION",
          "BOOKING_FAILURE",
          "CLIENT_DISSATISFACTION",
          "FOLLOW_UP_MISSING",
          "UPSELL_FAILURE",
          "INFORMATION_GAP",
          "TONE_ISSUE",
          "COMPLIANCE_CONCERN"
        ]
      },
      
      // COACHING FOCUS VARIABLES
      "coaching_focus": {
        "type": "string",
        "required": false,
        "description": "Specific skill area to emphasize",
        "options": [
          "dental_upselling",
          "active_listening",
          "appointment_booking",
          "client_rapport",
          "follow_up_scheduling",
          "objection_handling",
          "value_communication",
          "empathy_development",
          "product_knowledge",
          "closing_techniques"
        ]
      },
      
      // TONE & STYLE VARIABLES
      "coaching_tone": {
        "type": "string",
        "enum": ["constructive", "direct", "encouraging", "developmental", "corrective"],
        "default": "constructive",
        "description": "Overall coaching approach"
      },
      "detail_level": {
        "type": "string",
        "enum": ["brief", "standard", "comprehensive", "executive_summary"],
        "default": "standard",
        "description": "Length and depth of coaching document"
      },
      
      // CONTENT VARIABLES
      "include_transcript_excerpts": {
        "type": "boolean",
        "default": true,
        "description": "Include specific quotes from call"
      },
      "include_role_play": {
        "type": "boolean",
        "default": true,
        "description": "Include practice scenario"
      },
      "include_metrics": {
        "type": "boolean",
        "default": true,
        "description": "Include performance metrics and benchmarks"
      },
      "include_follow_up_plan": {
        "type": "boolean",
        "default": true,
        "description": "Include structured follow-up timeline"
      },
      "include_resources": {
        "type": "boolean",
        "default": false,
        "description": "Include training resources and references"
      },
      
      // COMPARISON VARIABLES
      "compare_to_previous": {
        "type": "boolean",
        "default": false,
        "description": "Compare to staff's previous performance"
      },
      "compare_to_peers": {
        "type": "boolean",
        "default": false,
        "description": "Compare to team average"
      },
      "show_improvement_trends": {
        "type": "boolean",
        "default": false,
        "description": "Show progress over time"
      },
      
      // CONTEXT VARIABLES
      "staff_experience_level": {
        "type": "string",
        "enum": ["new_hire", "junior", "intermediate", "senior", "expert"],
        "required": false,
        "description": "Adjust coaching complexity to experience"
      },
      "previous_coaching_count": {
        "type": "integer",
        "default": 0,
        "description": "Number of previous coaching sessions (affects tone)"
      },
      "is_repeat_issue": {
        "type": "boolean",
        "default": false,
        "description": "Is this the same issue as before?"
      },
      
      // OUTPUT FORMAT VARIABLES
      "output_format": {
        "type": "string",
        "enum": ["markdown", "html", "pdf", "plain_text", "email_ready"],
        "default": "markdown"
      },
      "language": {
        "type": "string",
        "enum": ["en", "es", "fr", "de", "pt"],
        "default": "en",
        "description": "Language for coaching document"
      },
      "max_words": {
        "type": "integer",
        "default": 1500,
        "range": [300, 5000],
        "description": "Maximum word count"
      },
      
      // DELIVERY VARIABLES
      "send_to_email": {
        "type": "string",
        "required": false,
        "description": "Email address to send coaching document"
      },
      "schedule_delivery": {
        "type": "string",
        "format": "datetime",
        "required": false,
        "description": "Schedule delivery for later"
      },
      "cc_manager": {
        "type": "boolean",
        "default": false,
        "description": "Copy manager on delivery"
      },
      
      // PRIVACY VARIABLES
      "anonymize_client": {
        "type": "boolean",
        "default": false,
        "description": "Remove client identifying information"
      },
      "include_call_recording_link": {
        "type": "boolean",
        "default": false,
        "description": "Include link to call recording"
      }
    },
    "required": ["call_id", "staff_name", "alert_type"]
  },
  
  "output_schema": {
    "type": "object",
    "properties": {
      "success": "boolean",
      "coaching_document": {
        "sections": [
          "call_overview",
          "what_went_well",
          "opportunity_for_growth",
          "coaching_tips",
          "practice_scenario",
          "follow_up_plan",
          "encouragement"
        ],
        "word_count": "integer",
        "estimated_review_time": "string (e.g., '5-7 minutes')"
      },
      "metadata": {
        "generated_at": "datetime",
        "coaching_id": "string",
        "ai_model_used": "string",
        "tokens_used": "integer"
      },
      "metrics_included": {
        "staff_alert_rate": "number",
        "peer_comparison": "object",
        "improvement_vs_last_month": "string"
      },
      "delivery_status": {
        "email_sent": "boolean",
        "scheduled_for": "datetime|null",
        "recipients": "array"
      }
    }
  }
}
```

---

#### Tool 2: `phone_prompt_prioritization`
**Complete Variable Control:**

```json
{
  "name": "phone_prompt_prioritization",
  "description": "AI-driven alert prioritization with customizable scoring algorithm",
  "input_schema": {
    
    // DATE & FILTER VARIABLES
    "date_range": {
      "from": "string (date)",
      "to": "string (date)",
      "preset": "string (today|this_week|this_month)"
    },
    "staff_filter": {
      "type": "array",
      "items": "string",
      "description": "Filter by staff (empty = all)"
    },
    "alert_types_filter": {
      "type": "array",
      "items": "string",
      "description": "Filter by alert codes (empty = all)"
    },
    "severity_filter": {
      "type": "array",
      "enum": ["HIGH", "MED", "LOW"],
      "default": ["HIGH", "MED", "LOW"]
    },
    "priority_filter": {
      "type": "array",
      "enum": [1, 2, 3],
      "default": [1, 2, 3]
    },
    "status_filter": {
      "type": "array",
      "enum": ["Open", "In Progress", "Actioned & Completed", "Ignored & No Action"],
      "default": ["Open", "In Progress"]
    },
    
    // SCORING ALGORITHM VARIABLES
    "prioritization_weights": {
      "type": "object",
      "description": "Customize scoring algorithm",
      "properties": {
        "revenue_impact_weight": {
          "type": "number",
          "default": 0.40,
          "range": [0, 1],
          "description": "Weight for $ lost/potential revenue"
        },
        "severity_weight": {
          "type": "number",
          "default": 0.30,
          "range": [0, 1],
          "description": "Weight for alert severity"
        },
        "urgency_weight": {
          "type": "number",
          "default": 0.20,
          "range": [0, 1],
          "description": "Weight for time sensitivity"
        },
        "frequency_weight": {
          "type": "number",
          "default": 0.10,
          "range": [0, 1],
          "description": "Weight for repeat issues"
        }
      }
    },
    
    // URGENCY CALCULATION VARIABLES
    "urgency_factors": {
      "client_callback_window_hours": {
        "type": "integer",
        "default": 24,
        "description": "Hours until callback is too late"
      },
      "follow_up_window_hours": {
        "type": "integer",
        "default": 72,
        "description": "Hours until follow-up window closes"
      },
      "time_decay_factor": {
        "type": "number",
        "default": 0.05,
        "description": "How much urgency increases per hour (0-1)"
      }
    },
    
    // OUTPUT VARIABLES
    "max_results": {
      "type": "integer",
      "default": 10,
      "range": [1, 100],
      "description": "Number of top alerts to return"
    },
    "include_score_breakdown": {
      "type": "boolean",
      "default": true,
      "description": "Show how each score was calculated"
    },
    "include_action_recommendations": {
      "type": "boolean",
      "default": true,
      "description": "AI suggests what to do with each alert"
    },
    "include_time_estimates": {
      "type": "boolean",
      "default": true,
      "description": "Estimate time to address each alert"
    },
    "group_by": {
      "type": "string",
      "enum": ["none", "staff", "alert_type", "urgency_tier"],
      "default": "none",
      "description": "Group prioritized alerts"
    },
    
    // ADVANCED VARIABLES
    "boost_repeat_offenders": {
      "type": "boolean",
      "default": true,
      "description": "Increase priority for staff with multiple alerts"
    },
    "boost_high_value_clients": {
      "type": "boolean",
      "default": false,
      "description": "Increase priority for top clients"
    },
    "penalize_low_recovery_chance": {
      "type": "boolean",
      "default": false,
      "description": "Lower priority if unlikely to recover revenue"
    },
    
    // CONTEXT VARIABLES
    "business_hours_only": {
      "type": "boolean",
      "default": false,
      "description": "Only include alerts during business hours"
    },
    "current_time_consideration": {
      "type": "boolean",
      "default": true,
      "description": "Factor in current time for urgency"
    }
  }
}
```

---

#### Tool 3: `phone_prompt_staff_analysis`
**Complete Variable Control:**

```json
{
  "name": "phone_prompt_staff_analysis",
  "description": "Comprehensive staff performance analysis with full variable control",
  "input_schema": {
    
    // REQUIRED VARIABLES
    "staff_name": {
      "type": "string",
      "required": true
    },
    
    // TIME PERIOD VARIABLES
    "analysis_period": {
      "type": "string",
      "enum": ["week", "month", "quarter", "year", "custom"],
      "default": "month"
    },
    "custom_date_range": {
      "from": "string (date)",
      "to": "string (date)",
      "required_if": "analysis_period === 'custom'"
    },
    
    // COMPARISON VARIABLES
    "comparison_mode": {
      "type": "string",
      "enum": ["peer", "self_previous", "both", "none"],
      "default": "both",
      "description": "Compare to peers or their own previous period"
    },
    "peer_selection": {
      "type": "string",
      "enum": ["all", "same_role", "same_experience_level", "top_performers"],
      "default": "same_role",
      "required_if": "comparison_mode includes 'peer'"
    },
    "previous_period_length": {
      "type": "string",
      "enum": ["same_length", "3_months", "6_months", "year"],
      "default": "same_length",
      "required_if": "comparison_mode includes 'self_previous'"
    },
    
    // METRICS VARIABLES
    "metrics_to_analyze": {
      "type": "array",
      "default": ["all"],
      "options": [
        "call_volume",
        "alert_rate",
        "revenue_impact",
        "booking_success_rate",
        "call_duration",
        "client_satisfaction",
        "upsell_rate",
        "follow_up_completion",
        "communication_quality",
        "product_knowledge"
      ]
    },
    
    // ANALYSIS DEPTH VARIABLES
    "analysis_depth": {
      "type": "string",
      "enum": ["executive_summary", "standard", "deep_dive", "forensic"],
      "default": "standard",
      "description": "How detailed the analysis should be"
    },
    "include_call_examples": {
      "type": "boolean",
      "default": true,
      "description": "Include specific call examples"
    },
    "number_of_examples": {
      "type": "integer",
      "default": 3,
      "range": [1, 10],
      "required_if": "include_call_examples === true"
    },
    "example_selection": {
      "type": "string",
      "enum": ["best", "worst", "mixed", "random"],
      "default": "mixed"
    },
    
    // PATTERN DETECTION VARIABLES
    "detect_patterns": {
      "type": "boolean",
      "default": true,
      "description": "Look for recurring patterns"
    },
    "pattern_types": {
      "type": "array",
      "default": ["all"],
      "options": [
        "time_of_day",
        "day_of_week",
        "call_type",
        "client_demographics",
        "alert_sequences",
        "improvement_trends",
        "decline_trends"
      ]
    },
    "pattern_min_occurrences": {
      "type": "integer",
      "default": 3,
      "description": "Minimum times pattern must occur to report"
    },
    
    // COACHING PLAN VARIABLES
    "include_coaching_plan": {
      "type": "boolean",
      "default": true
    },
    "coaching_plan_timeline": {
      "type": "string",
      "enum": ["1_week", "2_weeks", "30_days", "60_days", "90_days"],
      "default": "30_days",
      "required_if": "include_coaching_plan === true"
    },
    "coaching_focus_areas_limit": {
      "type": "integer",
      "default": 3,
      "range": [1, 5],
      "description": "Number of focus areas in coaching plan"
    },
    "include_training_resources": {
      "type": "boolean",
      "default": false,
      "description": "Link to specific training materials"
    },
    
    // STRENGTHS & WEAKNESSES VARIABLES
    "strengths_to_highlight": {
      "type": "integer",
      "default": 5,
      "range": [1, 10],
      "description": "Number of strengths to highlight"
    },
    "weaknesses_to_address": {
      "type": "integer",
      "default": 3,
      "range": [1, 10],
      "description": "Number of improvement areas"
    },
    "prioritize_by": {
      "type": "string",
      "enum": ["impact", "ease_of_improvement", "frequency", "business_priority"],
      "default": "impact"
    },
    
    // VISUALIZATION VARIABLES
    "include_charts": {
      "type": "boolean",
      "default": true,
      "description": "Include performance charts"
    },
    "chart_types": {
      "type": "array",
      "default": ["trend_line", "comparison_bar"],
      "options": [
        "trend_line",
        "comparison_bar",
        "radar_chart",
        "pie_chart",
        "heat_map"
      ]
    },
    
    // OUTPUT VARIABLES
    "output_format": {
      "type": "string",
      "enum": ["markdown", "html", "pdf", "presentation", "email_ready"],
      "default": "markdown"
    },
    "tone": {
      "type": "string",
      "enum": ["formal", "casual", "motivational", "technical"],
      "default": "motivational"
    },
    "max_pages": {
      "type": "integer",
      "default": 5,
      "range": [2, 20]
    },
    
    // PRIVACY VARIABLES
    "anonymize_peer_data": {
      "type": "boolean",
      "default": true,
      "description": "Don't show names of peers in comparisons"
    },
    "include_sensitive_metrics": {
      "type": "boolean",
      "default": false,
      "description": "Include metrics like salary impact, promotion readiness"
    }
  }
}
```

---

#### Tool 4: `phone_prompt_revenue_recovery`
**Complete Variable Control:**

```json
{
  "name": "phone_prompt_revenue_recovery",
  "description": "Generate actionable revenue recovery plan with full customization",
  "input_schema": {
    
    // INPUT SELECTION VARIABLES
    "input_mode": {
      "type": "string",
      "enum": ["call_ids", "date_range", "alert_query", "staff_member"],
      "required": true,
      "description": "How to select alerts for recovery"
    },
    "call_ids": {
      "type": "array",
      "items": "string",
      "required_if": "input_mode === 'call_ids'"
    },
    "date_range": {
      "from": "string (date)",
      "to": "string (date)",
      "required_if": "input_mode === 'date_range'"
    },
    "staff_filter": {
      "type": "string",
      "required_if": "input_mode === 'staff_member'"
    },
    "alert_types_to_recover": {
      "type": "array",
      "default": ["REVENUE_LEAKAGE", "MISSED_OPPORTUNITY", "UPSELL_FAILURE"],
      "description": "Which alert types to focus on"
    },
    
    // RECOVERY STRATEGY VARIABLES
    "recovery_window": {
      "type": "string",
      "enum": ["24_hours", "3_days", "1_week", "2_weeks", "1_month"],
      "default": "1_week",
      "description": "Timeframe to execute recovery actions"
    },
    "recovery_approach": {
      "type": "string",
      "enum": ["aggressive", "moderate", "gentle", "custom"],
      "default": "moderate",
      "description": "How assertive the recovery approach"
    },
    "prioritize_by": {
      "type": "string",
      "enum": ["highest_revenue", "easiest_wins", "client_relationship", "time_sensitive"],
      "default": "highest_revenue"
    },
    
    // RECOVERY ESTIMATE VARIABLES
    "optimism_level": {
      "type": "string",
      "enum": ["pessimistic", "realistic", "optimistic"],
      "default": "realistic",
      "description": "How to estimate recovery likelihood"
    },
    "recovery_rate_assumptions": {
      "high_value_clients": {
        "type": "number",
        "default": 0.60,
        "range": [0, 1],
        "description": "% of revenue recoverable from top clients"
      },
      "medium_value_clients": {
        "type": "number",
        "default": 0.40,
        "range": [0, 1]
      },
      "low_value_clients": {
        "type": "number",
        "default": 0.20,
        "range": [0, 1]
      },
      "time_decay_per_day": {
        "type": "number",
        "default": 0.05,
        "description": "% less likely to recover per day delayed"
      }
    },
    
    // CLIENT CONTACT VARIABLES
    "include_client_scripts": {
      "type": "boolean",
      "default": true,
      "description": "Generate word-for-word callback scripts"
    },
    "script_style": {
      "type": "string",
      "enum": ["casual", "professional", "empathetic", "value_focused"],
      "default": "professional",
      "required_if": "include_client_scripts === true"
    },
    "script_length": {
      "type": "string",
      "enum": ["30_seconds", "1_minute", "2_minutes", "detailed"],
      "default": "1_minute"
    },
    "include_objection_handling": {
      "type": "boolean",
      "default": true,
      "description": "Include responses to common objections"
    },
    
    // CONTACT METHOD VARIABLES
    "preferred_contact_methods": {
      "type": "array",
      "default": ["phone", "email", "sms"],
      "options": ["phone", "email", "sms", "in_person", "whatsapp"]
    },
    "contact_attempt_sequence": {
      "type": "array",
      "default": [
        {"method": "phone", "timing": "same_day"},
        {"method": "email", "timing": "24_hours"},
        {"method": "sms", "timing": "72_hours"}
      ],
      "description": "Sequence and timing of contact attempts"
    },
    
    // OFFER VARIABLES
    "include_incentives": {
      "type": "boolean",
      "default": true,
      "description": "Include discount/incentive recommendations"
    },
    "max_discount_percentage": {
      "type": "number",
      "default": 10,
      "range": [0, 50],
      "required_if": "include_incentives === true"
    },
    "incentive_types": {
      "type": "array",
      "default": ["first_visit_discount", "bundle_deal"],
      "options": [
        "percentage_discount",
        "dollar_amount_off",
        "free_addon",
        "bundle_deal",
        "loyalty_points",
        "first_visit_discount",
        "referral_bonus"
      ]
    },
    
    // TIMELINE VARIABLES
    "plan_format": {
      "type": "string",
      "enum": ["day_by_day", "prioritized_list", "staff_assigned", "client_grouped"],
      "default": "day_by_day"
    },
    "start_date": {
      "type": "string",
      "format": "date",
      "default": "today"
    },
    "include_deadlines": {
      "type": "boolean",
      "default": true,
      "description": "Set specific deadlines for each action"
    },
    
    // TRACKING VARIABLES
    "include_tracking_sheet": {
      "type": "boolean",
      "default": true,
      "description": "Generate tracking spreadsheet"
    },
    "tracking_metrics": {
      "type": "array",
      "default": ["contacts_made", "appointments_scheduled", "revenue_recovered"],
      "options": [
        "contacts_made",
        "appointments_scheduled",
        "revenue_recovered",
        "conversion_rate",
        "time_spent",
        "objections_encountered"
      ]
    },
    "success_criteria": {
      "type": "object",
      "properties": {
        "target_recovery_percentage": {
          "type": "number",
          "default": 40,
          "description": "% of total revenue to recover"
        },
        "minimum_conversion_rate": {
          "type": "number",
          "default": 0.25,
          "description": "Minimum % of clients who should convert"
        }
      }
    },
    
    // ASSIGNMENT VARIABLES
    "assign_to_staff": {
      "type": "boolean",
      "default": true,
      "description": "Assign specific callbacks to staff members"
    },
    "assignment_logic": {
      "type": "string",
      "enum": ["original_caller", "best_performer", "availability", "workload_balance"],
      "default": "original_caller"
    },
    
    // OUTPUT VARIABLES
    "output_format": {
      "type": "string",
      "enum": ["markdown", "pdf", "excel", "email_ready", "presentation"],
      "default": "markdown"
    },
    "include_executive_summary": {
      "type": "boolean",
      "default": true
    },
    "detail_level": {
      "type": "string",
      "enum": ["summary", "standard", "comprehensive"],
      "default": "standard"
    }
  }
}
```

---

#### Tool 5: `phone_prompt_trend_analysis`
**Complete Variable Control:**

```json
{
  "name": "phone_prompt_trend_analysis",
  "description": "Pattern detection and trend forecasting with full customization",
  "input_schema": {
    
    // TIME PERIOD VARIABLES
    "analysis_period": {
      "type": "string",
      "enum": ["daily", "weekly", "monthly", "quarterly", "custom"],
      "default": "weekly"
    },
    "date_range": {
      "from": "string (date)",
      "to": "string (date)",
      "required": true
    },
    "comparison_periods": {
      "type": "array",
      "default": ["previous_period", "year_ago"],
      "options": [
        "previous_period",
        "year_ago",
        "best_period",
        "worst_period",
        "team_average"
      ]
    },
    
    // FOCUS AREA VARIABLES
    "primary_focus": {
      "type": "string",
      "enum": ["volume_trends", "alert_trends", "revenue_trends", "staff_performance", "client_patterns"],
      "required": true
    },
    "secondary_focuses": {
      "type": "array",
      "items": "string",
      "description": "Additional areas to analyze"
    },
    
    // ALERT TREND VARIABLES
    "alert_categories_to_track": {
      "type": "array",
      "default": ["all"],
      "options": ["REVENUE_LEAKAGE", "MISSED_OPPORTUNITY", "POOR_COMMUNICATION", "etc..."]
    },
    "trend_metrics": {
      "type": "array",
      "default": ["count", "percentage", "revenue_impact"],
      "options": [
        "count",
        "percentage",
        "revenue_impact",
        "severity_distribution",
        "resolution_time",
        "repeat_rate"
      ]
    },
    
    // STAFF TREND VARIABLES
    "staff_filter": {
      "type": "array",
      "items": "string",
      "default": [],
      "description": "Specific staff to analyze (empty = all)"
    },
    "staff_grouping": {
      "type": "string",
      "enum": ["individual", "role", "experience_level", "team"],
      "default": "individual"
    },
    "identify_outliers": {
      "type": "boolean",
      "default": true,
      "description": "Flag staff with unusual trends"
    },
    
    // PATTERN DETECTION VARIABLES
    "pattern_types_to_detect": {
      "type": "array",
      "default": ["all"],
      "options": [
        "time_of_day",
        "day_of_week",
        "seasonal",
        "staff_correlations",
        "alert_sequences",
        "client_behavior",
        "external_factors"
      ]
    },
    "pattern_sensitivity": {
      "type": "string",
      "enum": ["low", "medium", "high"],
      "default": "medium",
      "description": "How strict pattern detection should be"
    },
    "min_pattern_confidence": {
      "type": "number",
      "default": 0.70,
      "range": [0.5, 0.99],
      "description": "Minimum confidence to report pattern"
    },
    "min_sample_size": {
      "type": "integer",
      "default": 10,
      "description": "Minimum occurrences for valid pattern"
    },
    
    // FORECASTING VARIABLES
    "include_predictions": {
      "type": "boolean",
      "default": true,
      "description": "Forecast future trends"
    },
    "prediction_horizon": {
      "type": "string",
      "enum": ["1_week", "2_weeks", "1_month", "3_months", "6_months"],
      "default": "1_month",
      "required_if": "include_predictions === true"
    },
    "prediction_confidence_interval": {
      "type": "number",
      "default": 0.95,
      "options": [0.90, 0.95, 0.99],
      "description": "Statistical confidence level"
    },
    "prediction_method": {
      "type": "string",
      "enum": ["linear_regression", "moving_average", "exponential_smoothing", "ml_model"],
      "default": "exponential_smoothing"
    },
    
    // ANOMALY DETECTION VARIABLES
    "detect_anomalies": {
      "type": "boolean",
      "default": true,
      "description": "Flag unusual spikes/drops"
    },
    "anomaly_threshold": {
      "type": "string",
      "enum": ["conservative", "moderate", "aggressive"],
      "default": "moderate",
      "description": "How sensitive anomaly detection is"
    },
    "anomaly_window": {
      "type": "integer",
      "default": 7,
      "description": "Days to look back for baseline"
    },
    
    // CORRELATION ANALYSIS VARIABLES
    "analyze_correlations": {
      "type": "boolean",
      "default": true,
      "description": "Find relationships between variables"
    },
    "correlation_variables": {
      "type": "array",
      "default": ["alert_type", "time_of_day", "staff", "day_of_week"],
      "options": [
        "alert_type",
        "severity",
        "priority",
        "time_of_day",
        "day_of_week",
        "staff",
        "call_duration",
        "client_type",
        "service_type"
      ]
    },
    "min_correlation_strength": {
      "type": "number",
      "default": 0.50,
      "range": [0.3, 1.0],
      "description": "Minimum correlation coefficient to report"
    },
    
    // VISUALIZATION VARIABLES
    "chart_types": {
      "type": "array",
      "default": ["line", "bar", "heatmap"],
      "options": [
        "line",
        "bar",
        "pie",
        "scatter",
        "heatmap",
        "area",
        "box_plot",
        "candlestick"
      ]
    },
    "chart_style": {
      "type": "string",
      "enum": ["simple", "detailed", "presentation", "print_friendly"],
      "default": "detailed"
    },
    
    // INSIGHT GENERATION VARIABLES
    "insight_focus": {
      "type": "string",
      "enum": ["actionable", "strategic", "diagnostic", "comprehensive"],
      "default": "actionable",
      "description": "Type of insights to generate"
    },
    "max_insights": {
      "type": "integer",
      "default": 10,
      "range": [3, 20],
      "description": "Maximum number of key insights"
    },
    "prioritize_insights_by": {
      "type": "string",
      "enum": ["impact", "urgency", "confidence", "novelty"],
      "default": "impact"
    },
    
    // RECOMMENDATION VARIABLES
    "include_recommendations": {
      "type": "boolean",
      "default": true
    },
    "recommendation_style": {
      "type": "string",
      "enum": ["specific_actions", "strategic_guidance", "questions_to_explore"],
      "default": "specific_actions"
    },
    "recommendation_timeline": {
      "type": "string",
      "enum": ["immediate", "short_term", "long_term", "all"],
      "default": "all"
    },
    
    // OUTPUT VARIABLES
    "output_format": {
      "type": "string",
      "enum": ["markdown", "html", "pdf", "presentation", "dashboard"],
      "default": "markdown"
    },
    "detail_level": {
      "type": "string",
      "enum": ["executive_summary", "standard", "deep_dive"],
      "default": "standard"
    },
    "target_audience": {
      "type": "string",
      "enum": ["executive", "manager", "analyst", "staff"],
      "default": "manager",
      "description": "Adjust language and focus for audience"
    }
  }
}
```

---

### Category 2: Data Retrieval Tools

#### Tool 6: `phone_get_full_call` 🔴
**ULTIMATE Variable Control - Master Retrieval Tool:**

```json
{
  "name": "phone_get_full_call",
  "description": "Maximum flexibility call retrieval - every possible filter and option",
  "input_schema": {
    
    // BASIC FILTERS
    "call_id": { "type": "string", "description": "Specific call ID (if known)" },
    "call_ids": { "type": "array", "items": "string", "description": "Multiple specific calls" },
    
    // DATE & TIME FILTERS
    "date_range": {
      "from": "string (date)",
      "to": "string (date)",
      "preset": "string (today|yesterday|this_week|last_week|this_month|last_month|last_7_days|last_30_days|last_90_days|custom)"
    },
    "time_of_day_range": {
      "start_hour": { "type": "integer", "range": [0, 23] },
      "end_hour": { "type": "integer", "range": [0, 23] },
      "description": "Filter by time of day (e.g., 9am-5pm)"
    },
    "days_of_week": {
      "type": "array",
      "items": { "enum": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] },
      "description": "Filter by specific days"
    },
    
    // STAFF FILTERS
    "staff_name": { "type": "string", "description": "Single staff member" },
    "staff_names": { "type": "array", "items": "string", "description": "Multiple staff" },
    "staff_role": { "type": "string", "options": ["receptionist", "vet", "tech", "manager"] },
    "staff_experience_level": { "type": "string", "enum": ["new_hire", "junior", "intermediate", "senior"] },
    "exclude_staff": { "type": "array", "items": "string", "description": "Exclude specific staff" },
    
    // CLIENT FILTERS
    "client_name": { "type": "string" },
    "client_id": { "type": "string" },
    "client_type": { "type": "string", "enum": ["new", "existing", "vip", "at_risk", "inactive"] },
    "client_value_tier": { "type": "string", "enum": ["high", "medium", "low"] },
    "pet_name": { "type": "string" },
    "pet_species": { "type": "string", "enum": ["dog", "cat", "bird", "exotic", "other"] },
    
    // CALL CHARACTERISTICS FILTERS
    "call_direction": {
      "type": "string",
      "enum": ["inbound", "outbound", "both"],
      "default": "both"
    },
    "min_duration_seconds": { "type": "integer", "default": 0 },
    "max_duration_seconds": { "type": "integer" },
    "duration_range": {
      "type": "string",
      "enum": ["very_short_0_1min", "short_1_3min", "medium_3_10min", "long_10_30min", "very_long_30plus"],
      "description": "Predefined duration ranges"
    },
    
    // ALERT FILTERS
    "has_alerts": {
      "type": "boolean",
      "default": false,
      "description": "Only calls with alerts"
    },
    "no_alerts": {
      "type": "boolean",
      "default": false,
      "description": "Only calls WITHOUT alerts"
    },
    "alert_types": {
      "type": "array",
      "items": "string",
      "description": "Filter by specific alert codes"
    },
    "alert_severity": {
      "type": "array",
      "enum": ["HIGH", "MED", "LOW"],
      "default": ["HIGH", "MED", "LOW"]
    },
    "alert_priority": {
      "type": "array",
      "enum": [1, 2, 3],
      "default": [1, 2, 3]
    },
    "alert_status": {
      "type": "array",
      "enum": ["Open", "In Progress", "Actioned & Completed", "Ignored & No Action"],
      "default": ["Open"]
    },
    "min_alert_count": { "type": "integer", "description": "Minimum alerts per call" },
    "max_alert_count": { "type": "integer", "description": "Maximum alerts per call" },
    
    // REVENUE FILTERS
    "has_revenue_leakage": { "type": "boolean" },
    "min_revenue_loss": { "type": "number", "description": "$ minimum" },
    "max_revenue_loss": { "type": "number", "description": "$ maximum" },
    "service_types": {
      "type": "array",
      "items": "string",
      "description": "Filter by services discussed (dental, surgery, boarding, etc.)"
    },
    
    // TRANSCRIPT FILTERS
    "transcript_contains": {
      "type": "string",
      "description": "Search for keywords/phrases in transcript"
    },
    "transcript_sentiment": {
      "type": "string",
      "enum": ["positive", "neutral", "negative", "mixed"]
    },
    "min_transcript_length_words": { "type": "integer" },
    "max_transcript_length_words": { "type": "integer" },
    
    // CONTENT INCLUSION VARIABLES
    "include_transcript": {
      "type": "boolean",
      "default": true,
      "description": "Include full transcript text"
    },
    "transcript_format": {
      "type": "string",
      "enum": ["full", "summary", "timestamped", "speaker_separated"],
      "default": "full"
    },
    "include_analysis": {
      "type": "boolean",
      "default": true,
      "description": "Include AI analysis"
    },
    "include_alerts": {
      "type": "boolean",
      "default": true,
      "description": "Include alert details"
    },
    "include_metadata": {
      "type": "boolean",
      "default": true,
      "description": "Include call metadata"
    },
    "include_manager_notes": {
      "type": "boolean",
      "default": false,
      "description": "Include manager notes/actions"
    },
    "include_call_recording_link": {
      "type": "boolean",
      "default": false,
      "description": "Include link to recording"
    },
    
    // FIELD SELECTION VARIABLES
    "fields_to_return": {
      "type": "array",
      "items": "string",
      "description": "Specific fields to return (reduces payload)",
      "examples": [
        "call_id",
        "call_date",
        "staff_name",
        "duration",
        "alert_count",
        "transcript",
        "alert_1_type",
        "revenue_loss_estimate"
      ]
    },
    "exclude_fields": {
      "type": "array",
      "items": "string",
      "description": "Fields to exclude from response"
    },
    
    // AGGREGATION VARIABLES
    "group_by": {
      "type": "string",
      "enum": ["none", "staff", "date", "alert_type", "client"],
      "default": "none",
      "description": "Group results"
    },
    "aggregate_functions": {
      "type": "array",
      "items": {
        "field": "string",
        "function": "string (sum|avg|min|max|count)"
      },
      "description": "Calculate aggregates (e.g., total revenue loss)"
    },
    
    // SORTING VARIABLES
    "sort_by": {
      "type": "string",
      "enum": [
        "date_desc",
        "date_asc",
        "duration_desc",
        "duration_asc",
        "alert_severity",
        "alert_count",
        "revenue_impact",
        "staff_name",
        "client_name",
        "random"
      ],
      "default": "date_desc"
    },
    "secondary_sort": {
      "type": "string",
      "description": "Second-level sorting"
    },
    
    // PAGINATION VARIABLES
    "max_results": {
      "type": "integer",
      "default": 50,
      "range": [1, 1000],
      "description": "Maximum number of calls to return"
    },
    "offset": {
      "type": "integer",
      "default": 0,
      "description": "Skip first N results (for pagination)"
    },
    "page_number": {
      "type": "integer",
      "description": "Page number (alternative to offset)"
    },
    "page_size": {
      "type": "integer",
      "default": 50,
      "description": "Results per page"
    },
    
    // PERFORMANCE VARIABLES
    "use_cache": {
      "type": "boolean",
      "default": true,
      "description": "Use cached results if available"
    },
    "cache_ttl_seconds": {
      "type": "integer",
      "default": 300,
      "description": "How long to cache results"
    },
    "lazy_load_transcripts": {
      "type": "boolean",
      "default": false,
      "description": "Don't load transcripts initially (fetch on demand)"
    },
    
    // OUTPUT FORMAT VARIABLES
    "output_format": {
      "type": "string",
      "enum": ["json", "csv", "table", "summary", "detailed", "excel"],
      "default": "json"
    },
    "include_summary_stats": {
      "type": "boolean",
      "default": true,
      "description": "Include summary statistics"
    },
    "summary_fields": {
      "type": "array",
      "default": ["total_count", "alert_count", "total_revenue_loss", "avg_duration"],
      "description": "Which summary stats to include"
    },
    
    // EXPORT VARIABLES
    "export_to_file": {
      "type": "boolean",
      "default": false,
      "description": "Save results to file"
    },
    "export_filename": {
      "type": "string",
      "description": "Filename for export"
    },
    "export_format": {
      "type": "string",
      "enum": ["csv", "excel", "json", "pdf"],
      "default": "csv"
    },
    
    // PRIVACY VARIABLES
    "anonymize_client_data": {
      "type": "boolean",
      "default": false,
      "description": "Remove client identifying info"
    },
    "anonymize_staff_data": {
      "type": "boolean",
      "default": false,
      "description": "Remove staff names"
    },
    "redact_sensitive_info": {
      "type": "boolean",
      "default": false,
      "description": "Redact phone numbers, addresses, payment info"
    },
    
    // DEBUGGING VARIABLES
    "explain_query": {
      "type": "boolean",
      "default": false,
      "description": "Return SQL query explanation"
    },
    "include_execution_time": {
      "type": "boolean",
      "default": false,
      "description": "Show query execution time"
    },
    "verbose": {
      "type": "boolean",
      "default": false,
      "description": "Return detailed processing info"
    }
  },
  
  "output_schema": {
    "success": "boolean",
    "query_info": {
      "total_matches": "integer",
      "returned_count": "integer",
      "filters_applied": "array",
      "execution_time_ms": "number",
      "cache_hit": "boolean"
    },
    "summary_stats": {
      "total_calls": "integer",
      "calls_with_alerts": "integer",
      "total_revenue_loss": "number",
      "avg_duration": "number",
      "by_staff": "object",
      "by_alert_type": "object"
    },
    "calls": [
      {
        "call_id": "string",
        "metadata": "object",
        "transcript": "string|object",
        "analysis": "object",
        "alerts": "array"
      }
    ],
    "pagination": {
      "current_page": "integer",
      "total_pages": "integer",
      "has_next_page": "boolean",
      "has_previous_page": "boolean"
    }
  }
}
```

---

## 🎯 Summary: Why Variable-Driven Design Matters

### Benefits:

1. **AI Flexibility** - AI can adapt queries to exact user needs
2. **No Hardcoding** - Every parameter is adjustable
3. **Progressive Disclosure** - Simple defaults, advanced options available
4. **Composability** - Combine variables for complex queries
5. **User Control** - Users can fine-tune AI behavior
6. **Future-Proof** - Easy to add new variables without breaking existing tools

### Example: Manager asks "Show me Sarah's worst calls this month"

AI can now control:
- ✅ Date range (this month)
- ✅ Staff filter (Sarah)
- ✅ Has alerts (true)
- ✅ Alert severity (HIGH only)
- ✅ Sort by (revenue_impact DESC)
- ✅ Max results (10)
- ✅ Include transcript (true for review)
- ✅ Output format (detailed)

**Result:** Precise, customized query instead of generic result

---

## 🚀 Implementation Notes

### Default Values Strategy:
- **Required params**: Must be provided (call_id, staff_name, etc.)
- **Common params**: Smart defaults (date_range: "today", max_results: 50)
- **Advanced params**: Optional (anonymize, export, caching)

### Progressive Complexity:
```javascript
// SIMPLE: Manager just wants coaching
phone_prompt_alert_coaching({
  call_id: "VET-123",
  staff_name: "Sarah",
  alert_type: "REVENUE_LEAKAGE"
})

// INTERMEDIATE: Manager wants specific style
phone_prompt_alert_coaching({
  call_id: "VET-123",
  staff_name: "Sarah",
  alert_type: "REVENUE_LEAKAGE",
  coaching_tone: "encouraging",
  include_role_play: true
})

// ADVANCED: Manager wants full control
phone_prompt_alert_coaching({
  call_id: "VET-123",
  staff_name: "Sarah",
  alert_type: "REVENUE_LEAKAGE",
  coaching_tone: "encouraging",
  coaching_focus: "dental_upselling",
  detail_level: "comprehensive",
  compare_to_peers: true,
  include_metrics: true,
  include_training_resources: true,
  output_format: "pdf",
  send_to_email: "sarah@clinic.com",
  schedule_delivery: "2025-12-11T09:00:00Z",
  max_words: 2000
})
```

---

Ready to implement Phase 1 with this variable-driven architecture?

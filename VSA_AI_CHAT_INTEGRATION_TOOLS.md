# 🤖 VSA Alerts AI Chat Integration - Tool Library & Implementation
## Drag-and-Drop Alert Cards + Comprehensive AI Tools

**Date:** December 10, 2025  
**Goal:** Enable seamless alert card → AI chat integration with full call context  
**Status:** Design Complete - Ready for Implementation

---

## 📊 Executive Summary

### What We're Building

**1. Drag-and-Drop Alert Cards**
- Manager drags alert card from VSA module
- Drops into AI chat container
- AI instantly receives full call context (metadata + transcript + analysis)

**2. Comprehensive Tool Library**
- 12 new specialized tools for VSA alerts
- Extracted coaching prompt as reusable tool
- SQL query tools for deep database analysis
- Full integration with existing 600+ tool registry

**3. Seamless Context Injection**
- Alert card becomes JSON payload
- Transcript automatically fetched and included
- AI coaching prompt pre-loaded
- Manager can ask follow-up questions with full context

---

## 🎯 Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VSA ALERTS MODULE                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Alert Card (vsa-veterinary-alerts.js)                    │  │
│  │  - Call ID: VET-Smith-12-10-2024_14:30                    │  │
│  │  - Alert: REVENUE_LEAKAGE (HIGH)                          │  │
│  │  - Client: John Doe + Buddy (Golden Retriever)           │  │
│  │  - Staff: Sarah Thompson                                  │  │
│  │  - Evidence: "Did not mention dental cleaning"           │  │
│  │                                                            │  │
│  │  [Drag icon appears]                                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         ↓ Drag & Drop
┌─────────────────────────────────────────────────────────────────┐
│                    AI CHAT CONTAINER                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  💬 AI Assistant                                          │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ 🔔 Alert Context Received                           │ │  │
│  │  │                                                      │ │  │
│  │  │ Call: VET-Smith-12-10-2024_14:30                   │ │  │
│  │  │ Alert: REVENUE_LEAKAGE (HIGH)                       │ │  │
│  │  │ Client: John Doe (Buddy - Golden Retriever)        │ │  │
│  │  │ Staff: Sarah Thompson                               │ │  │
│  │  │                                                      │ │  │
│  │  │ ✅ Full transcript loaded (2,347 words)            │ │  │
│  │  │ ✅ AI analysis loaded                               │ │  │
│  │  │ ✅ Alert details loaded                             │ │  │
│  │  │                                                      │ │  │
│  │  │ I've reviewed this call. What would you like to    │ │  │
│  │  │ know?                                                │ │  │
│  │  │                                                      │ │  │
│  │  │ [Generate Coaching] [Analyze Revenue Impact]       │ │  │
│  │  │ [Create Action Plan] [View Transcript]              │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                            │  │
│  │  📝 Manager: "Why did Sarah miss the dental upsell?"      │  │
│  │                                                            │  │
│  │  🤖 AI: "After analyzing the transcript, Sarah missed    │  │
│  │      the dental opportunity because:                      │  │
│  │      1. Client mentioned Buddy's bad breath at 2:34      │  │
│  │      2. Sarah acknowledged but didn't offer cleaning     │  │
│  │      3. Conversation moved to flea treatment             │  │
│  │                                                            │  │
│  │      Coaching recommendation: Train on recognizing       │  │
│  │      dental cues and natural transition phrases."        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         ↓ Uses
┌─────────────────────────────────────────────────────────────────┐
│              VSA ALERTS TOOL LIBRARY (12 Tools)                  │
│                                                                  │
│  1. vsa_get_full_call_context        ← Loads everything         │
│  2. vsa_get_call_transcript          ← Transcript only          │
│  3. vsa_get_alert_details            ← Alert metadata           │
│  4. vsa_generate_coaching            ← Extracted prompt         │
│  5. vsa_analyze_revenue_impact       ← $ calculations           │
│  6. vsa_search_similar_alerts        ← Pattern matching         │
│  7. vsa_get_staff_performance        ← Staff metrics            │
│  8. vsa_create_action_plan           ← Multi-alert plans        │
│  9. vsa_update_alert_status          ← Status changes           │
│  10. vsa_add_manager_notes           ← Note taking              │
│  11. vsa_query_alerts_sql            ← Custom SQL               │
│  12. vsa_export_alert_report         ← PDF/Email export         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tool Library Specification

### Tool Category 1: Context Retrieval (Core)

#### Tool 1: `vsa_get_full_call_context` 🔴 **MOST IMPORTANT**
**Purpose:** Single tool that loads EVERYTHING for drag-and-drop  
**Priority:** CRITICAL - This is what happens when alert card is dropped

```json
{
  "name": "vsa_get_full_call_context",
  "description": "Retrieve complete call context including transcript, analysis, alert details, and metadata. Use this when a manager drops an alert card into chat or asks about a specific call.",
  "category": "vsa_context",
  "input_schema": {
    "type": "object",
    "properties": {
      "call_id": {
        "type": "string",
        "description": "Unique call identifier (e.g., 'VET-Smith-12-10-2024_14:30')",
        "required": true
      },
      "include_transcript": {
        "type": "boolean",
        "description": "Include full transcript text (default: true)",
        "default": true
      },
      "include_analysis": {
        "type": "boolean",
        "description": "Include AI analysis (default: true)",
        "default": true
      }
    },
    "required": ["call_id"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "success": true,
      "call_id": "string",
      "call_metadata": {
        "call_date": "2025-12-10",
        "call_time": "14:30:15",
        "duration_seconds": 456,
        "staff_name": "Sarah Thompson",
        "staff_id": "STAFF-001",
        "client_first_name": "John",
        "client_last_name": "Doe",
        "client_phone": "+1234567890",
        "pet_name": "Buddy",
        "pet_species": "Dog",
        "pet_breed": "Golden Retriever",
        "practice_name": "Valor Veterinary Clinic"
      },
      "transcript": {
        "full_text": "string (2000+ words)",
        "word_count": 2347,
        "speaker_breakdown": {
          "Staff": 1245,
          "Client": 1102
        },
        "key_moments": [
          {
            "timestamp": "2:34",
            "speaker": "Client",
            "text": "Buddy's breath has been really bad lately",
            "significance": "Dental opportunity mentioned"
          }
        ]
      },
      "analysis": {
        "sentiment_overall": "Positive",
        "topics_discussed": ["Flea treatment", "Diet concerns", "Breath issue"],
        "action_items": ["Schedule flea treatment", "Follow up on diet"],
        "missed_opportunities": ["Dental cleaning not offered"]
      },
      "alerts": [
        {
          "alert_slot": 1,
          "alert_code": "REVENUE_LEAKAGE",
          "severity": "HIGH",
          "priority": 1,
          "core_reason": "Dental cleaning opportunity missed during consultation",
          "triggers_met": "Client mentioned bad breath, no cleaning offered",
          "evidence": "Client at 2:34: 'Buddy's breath has been really bad lately' - Staff: 'Okay, we can talk about that' - No follow-up action taken",
          "estimated_revenue_loss": "$300",
          "manager_action_brief": "Coach Sarah on recognizing dental cues",
          "communication_guide": "When client mentions breath/tartar, transition: 'That's often a sign dental cleaning is needed. Let me show you what I'm seeing...'",
          "coaching_focus": "Dental upselling - Recognizing verbal cues"
        }
      ],
      "context_summary": "John Doe called about Buddy (Golden Retriever) with concerns about fleas and bad breath. Sarah handled the call professionally but missed a clear dental cleaning opportunity when client mentioned bad breath. Estimated revenue loss: $300. This is Sarah's 3rd similar alert this week."
    }
  }
}
```

**Python Implementation:**
```python
def vsa_get_full_call_context(
    call_id: str,
    include_transcript: bool = True,
    include_analysis: bool = True
) -> Dict[str, Any]:
    """
    Retrieve complete call context for AI chat integration
    
    This is the PRIMARY tool used when alert cards are dropped into chat.
    Fetches everything AI needs to help manager with coaching/analysis.
    """
    try:
        client = _get_supabase_client()
        
        # 1. Get call metadata from veterinary_calls
        call_query = client.table('veterinary_calls').select('*').eq('call_id', call_id).single()
        call_result = call_query.execute()
        
        if not call_result.data:
            return {"success": False, "error": f"Call ID '{call_id}' not found"}
        
        call_data = call_result.data
        
        # 2. Get alerts from call_manager_alerts
        alerts_query = client.table('call_manager_alerts').select('*').eq('call_id', call_id).single()
        alerts_result = alerts_query.execute()
        
        alerts = []
        if alerts_result.data:
            alert_data = alerts_result.data
            
            # Process all 3 alert slots
            for slot in range(1, 4):
                alert_code = alert_data.get(f'alert_{slot}_code')
                if alert_code and alert_code != 'NONE':
                    alerts.append({
                        'alert_slot': slot,
                        'alert_code': alert_code,
                        'severity': alert_data.get(f'alert_{slot}_severity', 'LOW'),
                        'priority': alert_data.get(f'alert_{slot}_priority', 3),
                        'core_reason': alert_data.get(f'alert_{slot}_core_reason', ''),
                        'triggers_met': alert_data.get(f'alert_{slot}_triggers_met', ''),
                        'evidence': alert_data.get(f'alert_{slot}_evidence', ''),
                        'key_metrics': alert_data.get(f'alert_{slot}_key_metrics', ''),
                        'estimated_revenue_loss': _extract_revenue_loss(alert_data.get(f'alert_{slot}_key_metrics', '')),
                        'manager_action_brief': alert_data.get(f'alert_{slot}_manager_action_brief', ''),
                        'manager_action_steps': alert_data.get(f'alert_{slot}_manager_action_steps', ''),
                        'communication_guide': alert_data.get(f'alert_{slot}_communication_guide_staff', ''),
                        'coaching_focus': alert_data.get(f'alert_{slot}_coaching_focus', '')
                    })
        
        # 3. Get transcript and analysis (if requested)
        transcript_data = {}
        if include_transcript or include_analysis:
            trans_query = client.table('call_full_transcript_and_full_analysis').select('*').eq('call_id', call_id).single()
            trans_result = trans_query.execute()
            
            if trans_result.data:
                if include_transcript:
                    full_text = trans_result.data.get('full_transcript_text', '')
                    transcript_data['full_text'] = full_text
                    transcript_data['word_count'] = len(full_text.split())
                    transcript_data['key_moments'] = _extract_key_moments(full_text, alerts)
                
                if include_analysis:
                    transcript_data['analysis'] = trans_result.data.get('full_analysis_text', '')
        
        # 4. Build context summary
        context_summary = _build_context_summary(call_data, alerts, transcript_data)
        
        return {
            'success': True,
            'call_id': call_id,
            'call_metadata': {
                'call_date': call_data.get('key_call_date'),
                'call_time': call_data.get('key_time'),
                'duration_seconds': call_data.get('key_call_duration_sec'),
                'staff_name': call_data.get('key_staffname'),
                'client_first_name': call_data.get('key_otherspeaker_firstname'),
                'client_last_name': call_data.get('key_otherspeaker_lastname'),
                'client_phone': call_data.get('key_ph'),
                'pet_name': call_data.get('key_pet_petname'),
                'pet_species': call_data.get('key_pet_species'),
                'pet_breed': call_data.get('key_pet_breed'),
                'practice_name': call_data.get('key_businessname')
            },
            'transcript': transcript_data,
            'alerts': alerts,
            'context_summary': context_summary
        }
        
    except Exception as e:
        logger.error(f"Error fetching full call context: {e}")
        return {
            'success': False,
            'error': str(e)
        }
```

---

#### Tool 2: `vsa_get_call_transcript`
**Purpose:** Fetch ONLY transcript (lighter than full context)  
**Use Case:** When manager asks "show me the transcript"

```json
{
  "name": "vsa_get_call_transcript",
  "description": "Retrieve just the call transcript text, without alerts or analysis. Use when manager specifically asks to see/read the transcript.",
  "input_schema": {
    "call_id": "string (required)",
    "format": "string (enum: 'full', 'summary', 'timestamped') default: 'full'"
  },
  "output_schema": {
    "success": true,
    "call_id": "string",
    "transcript": "string (full text)",
    "word_count": 2347,
    "format": "full"
  }
}
```

---

#### Tool 3: `vsa_get_alert_details`
**Purpose:** Fetch ONLY alert metadata (no transcript)  
**Use Case:** Quick alert lookup without loading full transcript

```json
{
  "name": "vsa_get_alert_details",
  "description": "Get alert metadata without transcript. Use for quick alert info or when working with multiple alerts.",
  "input_schema": {
    "call_id": "string (required)",
    "alert_slot": "integer (1-3, optional) - specific slot or all"
  },
  "output_schema": {
    "success": true,
    "call_id": "string",
    "alerts": [ /* alert objects */ ]
  }
}
```

---

### Tool Category 2: AI Coaching (Extracted Prompt)

#### Tool 4: `vsa_generate_coaching` 🔴 **COACHING PROMPT EXTRACTION**
**Purpose:** Extracted coaching prompt as reusable tool  
**Source:** Python dashboard's `_generate_ai_coaching_document()` function

```json
{
  "name": "vsa_generate_coaching",
  "description": "Generate personalized coaching document for staff based on call transcript and alert type. Uses specialized veterinary coaching AI prompt extracted from Python dashboard.",
  "category": "vsa_coaching",
  "input_schema": {
    "type": "object",
    "properties": {
      "call_id": {
        "type": "string",
        "description": "Call ID to generate coaching for",
        "required": true
      },
      "alert_type": {
        "type": "string",
        "description": "Alert code (REVENUE_LEAKAGE, MISSED_OPPORTUNITY, etc.)",
        "required": true
      },
      "coaching_focus": {
        "type": "string",
        "description": "Specific coaching area (e.g., 'Dental upselling', 'Active listening')",
        "required": false
      },
      "staff_name": {
        "type": "string",
        "description": "Staff member name for personalization",
        "required": true
      },
      "format": {
        "type": "string",
        "enum": ["markdown", "html", "plain_text"],
        "default": "markdown"
      }
    }
  },
  "output_schema": {
    "success": true,
    "coaching_document": "string (formatted coaching content)",
    "sections": {
      "overview": "What happened in this call",
      "what_went_well": "Positive aspects",
      "opportunities": "Areas for improvement",
      "specific_examples": "Transcript excerpts",
      "coaching_tips": "Actionable advice",
      "follow_up_plan": "Next steps"
    },
    "estimated_tokens": 1500
  }
}
```

**Python Implementation (Extracted Prompt):**
```python
def vsa_generate_coaching(
    call_id: str,
    alert_type: str,
    coaching_focus: Optional[str] = None,
    staff_name: str = "Staff Member",
    format: str = "markdown"
) -> Dict[str, Any]:
    """
    Generate AI coaching document using extracted prompt from Python dashboard
    
    This tool extracts the coaching generation logic from alert_v4_tiered.py
    and makes it available as a standalone AI tool.
    """
    try:
        # 1. Get full call context
        context = vsa_get_full_call_context(call_id, include_transcript=True)
        
        if not context['success']:
            return {"success": False, "error": "Could not load call context"}
        
        transcript = context['transcript']['full_text']
        alerts = context['alerts']
        metadata = context['call_metadata']
        
        # Find the specific alert
        target_alert = next((a for a in alerts if a['alert_code'] == alert_type), None)
        if not target_alert:
            return {"success": False, "error": f"Alert type {alert_type} not found for this call"}
        
        # 2. Build coaching prompt (EXTRACTED FROM PYTHON DASHBOARD)
        coaching_prompt = f"""
# Veterinary Call Coaching Document

You are an expert veterinary practice coach analyzing a phone call to provide constructive feedback.

**Context:**
- Call Date: {metadata['call_date']} at {metadata['call_time']}
- Staff Member: {staff_name}
- Client: {metadata['client_first_name']} {metadata['client_last_name']}
- Pet: {metadata['pet_name']} ({metadata['pet_species']} - {metadata['pet_breed']})
- Practice: {metadata['practice_name']}

**Alert Triggered:**
- Type: {alert_type}
- Severity: {target_alert['severity']}
- Core Issue: {target_alert['core_reason']}
- What Happened: {target_alert['triggers_met']}
- Evidence: {target_alert['evidence']}

{f"**Coaching Focus:** {coaching_focus}" if coaching_focus else ""}

**Full Call Transcript:**
{transcript}

---

## Your Task:

Generate a comprehensive, constructive coaching document with these sections:

### 1. Call Overview (2-3 sentences)
Summarize what happened in this call - the main topic, client concern, and outcome.

### 2. What Went Well ✅
Identify 3-5 specific positive aspects of {staff_name}'s performance. Quote exact phrases from transcript.

### 3. Opportunity for Growth 🎯
Focus on the alert issue: {target_alert['core_reason']}

**The Moment:**
- Identify the exact timestamp/quote where the opportunity arose
- Explain why {staff_name} missed it

**What Could Have Been Done:**
{target_alert['manager_action_steps']}

### 4. Coaching Tips 💡
Provide 3-5 actionable tips specific to {coaching_focus if coaching_focus else alert_type}:
- Exact phrases to use
- Conversation flow recommendations
- How to recognize similar opportunities

**Communication Guide:**
{target_alert['communication_guide']}

### 5. Practice Scenario 🎭
Create a 30-second role-play scenario based on this exact situation for {staff_name} to practice.

### 6. Follow-Up Plan 📅
- Immediate action: What {staff_name} should do this week
- Short-term (1-2 weeks): Practice goals
- Long-term (1 month): Mastery indicators

### 7. Encouragement 🌟
End with genuine encouragement acknowledging {staff_name}'s strengths while motivating improvement.

---

**Tone:**
- Constructive and supportive (not critical)
- Specific and actionable (not vague)
- Evidence-based (quote transcript)
- Growth-oriented (focus on learning)

**Format:** {format.upper()}
"""
        
        # 3. Call Claude API with coaching prompt
        from anthropic import Anthropic
        client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": coaching_prompt
            }]
        )
        
        coaching_document = response.content[0].text
        
        # 4. Save to database
        supabase = _get_supabase_client()
        supabase.table('call_manager_alerts').update({
            'ai_coaching_support': coaching_document,
            'ai_coaching_generated_date': datetime.now().isoformat()
        }).eq('call_id', call_id).execute()
        
        return {
            'success': True,
            'coaching_document': coaching_document,
            'estimated_tokens': response.usage.input_tokens + response.usage.output_tokens,
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating coaching: {e}")
        return {'success': False, 'error': str(e)}
```

---

### Tool Category 3: Analysis & Intelligence

#### Tool 5: `vsa_analyze_revenue_impact`
**Purpose:** Calculate $ impact of alerts  
**Use Case:** Manager asks "How much money did we lose?"

```json
{
  "name": "vsa_analyze_revenue_impact",
  "description": "Calculate estimated revenue impact (lost/gained) from alert or group of alerts",
  "input_schema": {
    "call_ids": "array of strings or single string",
    "time_period": "string (optional) - 'today', 'week', 'month'",
    "alert_types": "array (optional) - filter by types"
  },
  "output_schema": {
    "success": true,
    "total_revenue_loss": 8400,
    "breakdown_by_category": {
      "REVENUE_LEAKAGE": 6200,
      "MISSED_OPPORTUNITY": 2200
    },
    "breakdown_by_service": {
      "Dental cleanings": 4200,
      "Follow-up appointments": 2800,
      "Product sales": 1400
    },
    "recovery_potential": {
      "amount": 3360,
      "percentage": 40,
      "actions_required": ["Call clients back", "Schedule follow-ups"]
    }
  }
}
```

---

#### Tool 6: `vsa_search_similar_alerts`
**Purpose:** Pattern detection across alerts  
**Use Case:** "Show me similar issues with Sarah"

```json
{
  "name": "vsa_search_similar_alerts",
  "description": "Find alerts with similar patterns (same staff, same alert type, similar evidence)",
  "input_schema": {
    "reference_call_id": "string (required) - the alert to compare against",
    "similarity_criteria": "array - ['staff', 'alert_type', 'keywords']",
    "date_range_days": "integer (default: 30)"
  },
  "output_schema": {
    "success": true,
    "similar_alerts": [ /* array of matching alerts */ ],
    "pattern_analysis": {
      "frequency": "3 similar alerts in 7 days",
      "trend": "Increasing",
      "common_themes": ["Dental upselling", "Client mentioned symptoms"],
      "staff_specific": true
    }
  }
}
```

---

#### Tool 7: `vsa_get_staff_performance`
**Purpose:** Staff metrics and trends  
**Use Case:** "How is Sarah doing overall?"

```json
{
  "name": "vsa_get_staff_performance",
  "description": "Get performance metrics for a staff member (alert counts, trends, strengths/weaknesses)",
  "input_schema": {
    "staff_name": "string (required)",
    "time_period": "string (default: 'month') - 'week', 'month', 'quarter'",
    "include_coaching_history": "boolean (default: false)"
  },
  "output_schema": {
    "success": true,
    "staff_name": "Sarah Thompson",
    "performance_summary": {
      "total_calls": 87,
      "alerts_triggered": 12,
      "alert_rate": "13.8%",
      "high_severity_count": 5,
      "most_common_alert": "REVENUE_LEAKAGE",
      "trend": "Alerts increasing 20% vs last month"
    },
    "breakdown_by_category": { /* ... */ },
    "coaching_received": 3,
    "improvement_areas": ["Dental upselling", "Follow-up scheduling"]
  }
}
```

---

### Tool Category 4: Action & Management

#### Tool 8: `vsa_create_action_plan`
**Purpose:** Multi-alert action planning  
**Use Case:** "Create a plan to address these 5 alerts"

```json
{
  "name": "vsa_create_action_plan",
  "description": "Create structured action plan to address multiple alerts (coaching sessions, follow-ups, process changes)",
  "input_schema": {
    "call_ids": "array of strings (required)",
    "plan_type": "string (enum: 'coaching', 'process_improvement', 'client_recovery')",
    "timeline": "string (default: '1_week') - '1_week', '2_weeks', '1_month'"
  },
  "output_schema": {
    "success": true,
    "plan_id": "PLAN-2025-12-10-001",
    "plan_type": "coaching",
    "phases": [
      {
        "phase": 1,
        "name": "Immediate Actions",
        "duration": "1-2 days",
        "actions": [
          "Schedule 1-on-1 with Sarah",
          "Review dental upselling training materials"
        ]
      }
    ]
  }
}
```

---

#### Tool 9: `vsa_update_alert_status`
**Purpose:** Update manager status, notes, actions  
**Use Case:** AI helps manager update after discussion

```json
{
  "name": "vsa_update_alert_status",
  "description": "Update alert status, add manager notes, or record actions taken",
  "input_schema": {
    "call_id": "string (required)",
    "status": "string (enum: 'Open', 'In Progress', 'Actioned & Completed', 'Ignored & No Action')",
    "notes": "string (optional) - manager notes",
    "actions": "string (optional) - actions taken"
  }
}
```

---

#### Tool 10: `vsa_add_manager_notes`
**Purpose:** Quick note-taking during conversation  
**Use Case:** AI summarizes discussion, saves as notes

```json
{
  "name": "vsa_add_manager_notes",
  "description": "Add or append manager notes to an alert. AI can auto-summarize conversation.",
  "input_schema": {
    "call_id": "string (required)",
    "notes": "string (required)",
    "mode": "string (enum: 'append', 'replace') default: 'append'"
  }
}
```

---

### Tool Category 5: SQL Query Tools

#### Tool 11: `vsa_query_alerts_sql` 🔴 **POWER TOOL**
**Purpose:** Custom SQL queries for deep analysis  
**Use Case:** Complex queries AI can construct

```json
{
  "name": "vsa_query_alerts_sql",
  "description": "Execute custom SQL query against veterinary_calls and call_manager_alerts tables. AI can construct queries for complex analysis.",
  "category": "vsa_sql",
  "input_schema": {
    "query": "string (required) - SQL query",
    "limit": "integer (default: 100) - max rows",
    "format": "string (enum: 'json', 'csv', 'table') default: 'json'"
  },
  "security": {
    "read_only": true,
    "allowed_tables": [
      "veterinary_calls",
      "call_manager_alerts",
      "call_full_transcript_and_full_analysis"
    ],
    "forbidden_operations": ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]
  }
}
```

**Example Queries AI Can Generate:**

**Query 1: Top 10 Staff by Alert Rate**
```sql
SELECT 
    key_staffname as staff_name,
    COUNT(DISTINCT call_id) as total_calls,
    COUNT(DISTINCT CASE WHEN manager_alerts_tags != 'NONE' THEN call_id END) as calls_with_alerts,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN manager_alerts_tags != 'NONE' THEN call_id END) / COUNT(DISTINCT call_id), 1) as alert_rate
FROM veterinary_calls
WHERE key_call_date >= '2025-12-01'
GROUP BY key_staffname
HAVING COUNT(DISTINCT call_id) >= 10
ORDER BY alert_rate DESC
LIMIT 10;
```

**Query 2: Revenue Loss by Day of Week**
```sql
SELECT 
    EXTRACT(DOW FROM created_at) as day_of_week,
    CASE EXTRACT(DOW FROM created_at)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_name,
    COUNT(*) as alert_count,
    SUM(CASE 
        WHEN alert_1_code = 'REVENUE_LEAKAGE' THEN 1
        WHEN alert_2_code = 'REVENUE_LEAKAGE' THEN 1
        WHEN alert_3_code = 'REVENUE_LEAKAGE' THEN 1
        ELSE 0
    END) as revenue_leakage_count
FROM call_manager_alerts
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
  AND manager_alerts_tags != 'NONE'
GROUP BY day_of_week, day_name
ORDER BY day_of_week;
```

**Query 3: Client Communication Patterns**
```sql
SELECT 
    vc.key_otherspeaker_firstname || ' ' || vc.key_otherspeaker_lastname as client_name,
    vc.key_pet_petname as pet_name,
    COUNT(DISTINCT vc.call_id) as total_calls,
    COUNT(DISTINCT cma.call_id) as calls_with_alerts,
    STRING_AGG(DISTINCT cma.manager_alerts_tags, ', ') as alert_types
FROM veterinary_calls vc
LEFT JOIN call_manager_alerts cma ON vc.call_id = cma.call_id
WHERE vc.key_call_date >= '2025-11-01'
  AND cma.manager_alerts_tags != 'NONE'
GROUP BY client_name, pet_name
HAVING COUNT(DISTINCT cma.call_id) >= 2
ORDER BY calls_with_alerts DESC
LIMIT 20;
```

---

#### Tool 12: `vsa_export_alert_report`
**Purpose:** Generate exportable reports  
**Use Case:** "Create a PDF report of this week's alerts"

```json
{
  "name": "vsa_export_alert_report",
  "description": "Generate formatted report (PDF/CSV/Excel) of alerts with optional email delivery",
  "input_schema": {
    "report_type": "string (enum: 'daily', 'weekly', 'custom')",
    "date_range": "object {start, end}",
    "format": "string (enum: 'pdf', 'csv', 'excel', 'html')",
    "email_to": "string (optional) - email address",
    "include_charts": "boolean (default: true)"
  }
}
```

---

## 🎨 Drag-and-Drop Implementation

### Frontend: VSA Alert Card (JavaScript)

**File:** `vsa-veterinary-alerts.js`

```javascript
// Add drag handlers to alert cards
renderAlertCard(alert) {
    const cardId = `alert-card-${alert.id}`;
    
    return `
        <div class="vsa-alert-card vsa-tier-3 vsa-severity-${alert.severity}" 
             data-alert-id="${alert.id}"
             data-call-id="${alert.callId}"
             draggable="true"
             id="${cardId}"
             role="article">
            
            <!-- Card content -->
            <div class="vsa-tier-header">
                <div class="vsa-drag-handle" title="Drag to AI Chat">
                    <i class="fas fa-grip-vertical"></i>
                </div>
                <div class="vsa-tier-title">
                    ${this.escapeHtml(alert.staffName)} - ${time} - ${date}
                </div>
                ${severityBadge}
            </div>
            
            <!-- Rest of card content... -->
        </div>
    `;
}

// Drag event handlers
setupDragAndDrop() {
    this.dom.on(this.container, 'dragstart', '.vsa-alert-card', (e) => {
        const card = e.currentTarget;
        const callId = card.getAttribute('data-call-id');
        const alertId = card.getAttribute('data-alert-id');
        
        // Build payload with alert context
        const payload = {
            type: 'vsa-alert',
            call_id: callId,
            alert_id: alertId,
            source: 'vsa-veterinary-alerts',
            action: 'load_full_context'
        };
        
        e.dataTransfer.setData('application/json', JSON.stringify(payload));
        e.dataTransfer.effectAllowed = 'copy';
        
        // Visual feedback
        card.classList.add('vsa-dragging');
    });
    
    this.dom.on(this.container, 'dragend', '.vsa-alert-card', (e) => {
        e.currentTarget.classList.remove('vsa-dragging');
    });
}
```

**CSS for Drag Styling:**
```css
.vsa-alert-card[draggable="true"] {
    cursor: grab;
}

.vsa-alert-card.vsa-dragging {
    opacity: 0.5;
    cursor: grabbing;
}

.vsa-drag-handle {
    display: inline-block;
    color: rgba(255, 255, 255, 0.6);
    margin-right: 8px;
    cursor: grab;
}

.vsa-drag-handle:hover {
    color: rgba(255, 255, 255, 1);
}
```

---

### Backend: AI Chat Container (Drop Zone)

**File:** `AI_infrastructure/routes/agent_routes_v4.py` (or new route file)

```python
@agent_bp.route('/api/ai-chat/drop-context', methods=['POST'])
def handle_dropped_alert():
    """
    Handle dropped alert card from VSA module
    Automatically loads full call context and starts AI conversation
    """
    try:
        data = request.json
        
        if data['type'] != 'vsa-alert':
            return jsonify({'error': 'Invalid drop type'}), 400
        
        call_id = data['call_id']
        
        # Use vsa_get_full_call_context tool
        from tools.implementations.veterinary_alerts_tools import vsa_get_full_call_context
        
        context = vsa_get_full_call_context(call_id, include_transcript=True, include_analysis=True)
        
        if not context['success']:
            return jsonify({'error': 'Failed to load call context'}), 500
        
        # Build AI system prompt with context
        system_prompt = f"""
You are an AI assistant helping a veterinary practice manager analyze call alerts.

**ALERT CONTEXT LOADED:**

Call ID: {context['call_id']}
Date: {context['call_metadata']['call_date']} at {context['call_metadata']['call_time']}
Staff: {context['call_metadata']['staff_name']}
Client: {context['call_metadata']['client_first_name']} {context['call_metadata']['client_last_name']}
Pet: {context['call_metadata']['pet_name']} ({context['call_metadata']['pet_species']})

**ALERTS TRIGGERED:** {len(context['alerts'])}
{chr(10).join([f"- {a['alert_code']} ({a['severity']}): {a['core_reason']}" for a in context['alerts']])}

**SUMMARY:**
{context['context_summary']}

You have access to the full transcript ({context['transcript']['word_count']} words) and can answer questions about:
- Why this alert was triggered
- What the staff member could have done differently
- Coaching recommendations
- Revenue impact analysis
- Similar patterns in other calls

The manager can now ask you questions. Be helpful, specific, and action-oriented.
"""
        
        # Create initial AI message
        initial_message = f"""
🔔 **Alert Context Loaded**

**Call:** {context['call_id']}  
**Alert:** {context['alerts'][0]['alert_code']} ({context['alerts'][0]['severity']})  
**Client:** {context['call_metadata']['client_first_name']} {context['call_metadata']['client_last_name']} ({context['call_metadata']['pet_name']})  
**Staff:** {context['call_metadata']['staff_name']}

✅ Full transcript loaded ({context['transcript']['word_count']} words)  
✅ AI analysis loaded  
✅ Alert details loaded

I've reviewed this call. What would you like to know?

**Quick Actions:**
- "Why did this alert trigger?"
- "Generate coaching document"
- "Show revenue impact"
- "Find similar issues"
- "Create action plan"
"""
        
        return jsonify({
            'success': True,
            'context': context,
            'system_prompt': system_prompt,
            'initial_message': initial_message,
            'available_tools': [
                'vsa_get_full_call_context',
                'vsa_get_call_transcript',
                'vsa_generate_coaching',
                'vsa_analyze_revenue_impact',
                'vsa_search_similar_alerts',
                'vsa_get_staff_performance',
                'vsa_create_action_plan',
                'vsa_update_alert_status',
                'vsa_add_manager_notes',
                'vsa_query_alerts_sql',
                'vsa_export_alert_report'
            ]
        })
        
    except Exception as e:
        logger.error(f"Error handling dropped alert: {e}")
        return jsonify({'error': str(e)}), 500
```

---

## 📦 Tool Registration (Registry V3)

### Schema File: `veterinary_alerts_ai_chat_tools.json`

**File:** `tools/schemas/veterinary_alerts_ai_chat_tools.json`

```json
{
  "platform": "veterinary_alerts_ai_chat",
  "version": "1.0.0",
  "description": "AI Chat integration tools for VSA Veterinary Alerts - enables drag-and-drop, coaching, and analysis",
  "database": {
    "provider": "Supabase",
    "url": "https://wuwmvtslltqhaycyukxk.supabase.co"
  },
  "tools": [
    {
      "name": "vsa_get_full_call_context",
      "description": "Retrieve complete call context including transcript, analysis, alert details, and metadata. PRIMARY tool for drag-and-drop integration.",
      "category": "vsa_context",
      "priority": "critical",
      "input_schema": {
        "type": "object",
        "properties": {
          "call_id": {
            "type": "string",
            "description": "Unique call identifier",
            "required": true
          },
          "include_transcript": {
            "type": "boolean",
            "default": true
          },
          "include_analysis": {
            "type": "boolean",
            "default": true
          }
        },
        "required": ["call_id"]
      }
    },
    {
      "name": "vsa_generate_coaching",
      "description": "Generate personalized coaching document using extracted prompt from Python dashboard. Includes structured feedback, examples, and action plans.",
      "category": "vsa_coaching",
      "priority": "high",
      "input_schema": {
        "type": "object",
        "properties": {
          "call_id": { "type": "string", "required": true },
          "alert_type": { "type": "string", "required": true },
          "coaching_focus": { "type": "string", "required": false },
          "staff_name": { "type": "string", "required": true },
          "format": { 
            "type": "string",
            "enum": ["markdown", "html", "plain_text"],
            "default": "markdown"
          }
        },
        "required": ["call_id", "alert_type", "staff_name"]
      }
    },
    {
      "name": "vsa_query_alerts_sql",
      "description": "Execute custom SQL query for deep analysis. AI can construct complex queries for pattern detection, trends, and reporting.",
      "category": "vsa_sql",
      "priority": "high",
      "security": {
        "read_only": true,
        "allowed_tables": [
          "veterinary_calls",
          "call_manager_alerts",
          "call_full_transcript_and_full_analysis"
        ]
      },
      "input_schema": {
        "type": "object",
        "properties": {
          "query": { "type": "string", "required": true },
          "limit": { "type": "integer", "default": 100 },
          "format": {
            "type": "string",
            "enum": ["json", "csv", "table"],
            "default": "json"
          }
        },
        "required": ["query"]
      }
    }
    /* ... remaining 9 tools ... */
  ]
}
```

---

### Implementation File: `veterinary_alerts_ai_chat_tools.py`

**File:** `tools/implementations/veterinary_alerts_ai_chat_tools.py`

```python
"""
VSA Veterinary Alerts AI Chat Integration Tools
================================================

Tools specifically designed for AI chat integration:
1. Drag-and-drop alert context loading
2. Coaching document generation (extracted prompt)
3. SQL query tools for deep analysis
4. Revenue impact calculations
5. Pattern detection and staff performance

Author: Valor AI Platform
Date: December 10, 2025
"""

# Import base veterinary tools
from tools.implementations.veterinary_alerts_tools import (
    _get_supabase_client,
    get_alerts_by_tag,
    get_call_transcript,
    get_call_metadata
)

# Import all 12 functions:
# - vsa_get_full_call_context()
# - vsa_get_call_transcript()
# - vsa_get_alert_details()
# - vsa_generate_coaching()
# - vsa_analyze_revenue_impact()
# - vsa_search_similar_alerts()
# - vsa_get_staff_performance()
# - vsa_create_action_plan()
# - vsa_update_alert_status()
# - vsa_add_manager_notes()
# - vsa_query_alerts_sql()
# - vsa_export_alert_report()

# [Full implementations from above]
```

---

## 🚀 Implementation Roadmap

### Phase 1: Core Integration (Week 1)
**Goal:** Get drag-and-drop working with basic context loading

1. **Day 1-2:** Create tool schemas and implement `vsa_get_full_call_context` (4-6 hours)
2. **Day 3:** Add drag-and-drop handlers to VSA module (3-4 hours)
3. **Day 4:** Create drop zone in AI chat container (3-4 hours)
4. **Day 5:** Testing and bug fixes

**Deliverable:** Manager can drag alert card to chat, AI receives full context

---

### Phase 2: Coaching Extraction (Week 2)
**Goal:** Extract coaching prompt as reusable tool

1. **Day 1-2:** Implement `vsa_generate_coaching` with extracted prompt (6-8 hours)
2. **Day 3:** Add coaching UI buttons to chat (2-3 hours)
3. **Day 4-5:** Testing with real calls

**Deliverable:** AI can generate coaching documents on-demand

---

### Phase 3: Analysis Tools (Week 3)
**Goal:** Add revenue impact, pattern detection, staff metrics

1. **Days 1-2:** Implement analysis tools (#5, #6, #7) (8-10 hours)
2. **Days 3-4:** Add SQL query tool (#11) (6-8 hours)
3. **Day 5:** Testing

**Deliverable:** AI can perform deep analysis and answer "why" questions

---

### Phase 4: Action Tools (Week 4)
**Goal:** Enable AI to help with status updates, notes, action plans

1. **Days 1-2:** Implement management tools (#8, #9, #10) (6-8 hours)
2. **Days 3-4:** Add export/reporting tool (#12) (4-6 hours)
3. **Day 5:** Integration testing

**Deliverable:** Full workflow - analyze, coach, update, export

---

## 💡 Key Benefits

### For Managers
✅ **Instant Context** - Drag alert → full context loaded in <2 seconds  
✅ **Natural Conversation** - Ask questions in plain English  
✅ **Actionable Insights** - AI provides specific, evidence-based recommendations  
✅ **Time Savings** - 10+ minutes per alert review reduced to 2-3 minutes  
✅ **Better Coaching** - AI-generated coaching documents with exact transcript quotes

### For Practice
✅ **Revenue Recovery** - AI identifies $ impact and recovery opportunities  
✅ **Pattern Detection** - Catch systemic issues across staff/time  
✅ **Staff Development** - Consistent, constructive coaching for everyone  
✅ **Data-Driven** - SQL queries enable custom analysis

### For AI System
✅ **Rich Context** - Full transcript + metadata enables intelligent responses  
✅ **Tool Library** - 12 specialized tools vs generic capabilities  
✅ **Registry Integration** - Automatic discovery by AI agents  
✅ **Extensible** - Easy to add new tools as needs evolve

---

## 🎯 Success Metrics

The integration will be considered successful when:

1. ✅ **Drag-and-drop works smoothly** (< 2 second load time)
2. ✅ **AI understands context** (can answer "why" questions)
3. ✅ **Coaching quality matches Python dashboard** (manager satisfaction)
4. ✅ **SQL queries work** (AI can construct and execute complex queries)
5. ✅ **Manager adoption** (80%+ of managers use drag-and-drop weekly)

---

## 📞 Next Steps

**IMMEDIATE (Today):**
1. Review this design document
2. Approve tool specifications
3. Choose implementation start date

**WEEK 1:**
1. Implement `vsa_get_full_call_context` tool
2. Add drag handlers to VSA alert cards
3. Test drag-and-drop payload

**WEEK 2:**
1. Extract coaching prompt from Python dashboard
2. Implement `vsa_generate_coaching` tool
3. Test coaching quality

**WEEK 3-4:**
1. Complete remaining 10 tools
2. Integration testing
3. Manager training

---

**Total Timeline:** 4 weeks to full drag-and-drop AI chat integration with 12 specialized tools

**Expected Impact:**
- 80% reduction in alert review time
- 100% of alerts get AI coaching (vs 10% manual)
- 50% increase in revenue recovery actions
- Better staff development through consistent coaching

---

Would you like me to start implementing Phase 1 (drag-and-drop + full context loading)?

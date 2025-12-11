"""
Veterinary Alerts Management Tools
===================================

AI tools for managing veterinary call alerts, accessing phone call data,
and planning actions across multiple alerts from Supabase database.

These tools connect to the VSA Supabase database (different from AI_agents project)
to access veterinary calls, transcripts, and manager alerts.

Database Tables:
- veterinary_calls: Main call records with metadata
- call_full_transcript_and_full_analysis: Full transcripts and AI analysis
- call_manager_alerts: Manager alerts with severity, priority, and coaching info

Author: Valor AI Platform
Date: December 2025
"""

import os
import sys
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = "https://wuwmvtslltqhaycyukxk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1d212dHNsbHRxaGF5Y3l1a3hrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTIyNDMzNCwiZXhwIjoyMDY2ODAwMzM0fQ.tUJ473GHC139vvH0X6fIgaFtgmLTl-VaUCf9kY6xQj4"


def _get_supabase_client():
    """Get Supabase client for VSA database"""
    try:
        from supabase import create_client, Client
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        return client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise


# ============================================================================
# ALERT DISCOVERY & FILTERING TOOLS
# ============================================================================

def get_alerts_by_tag(
    alert_tags: Union[str, List[str]],
    severity: Optional[str] = None,
    priority: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get veterinary alerts filtered by tag(s) and optional criteria.
    
    Args:
        alert_tags: Single tag or list of tags (e.g., "REVENUE_LEAKAGE" or ["MISSED_OPPORTUNITY", "POOR_COMMUNICATION"])
        severity: Filter by severity ("HIGH", "MED", "LOW")
        priority: Filter by priority (1=Immediate, 2=Near-term, 3=Monitor)
        date_from: ISO date string (e.g., "2025-12-01")
        date_to: ISO date string (e.g., "2025-12-08")
        limit: Maximum number of alerts to return (default 50)
    
    Returns:
        {
            "success": bool,
            "alert_count": int,
            "alerts": [
                {
                    "call_id": str,
                    "alert_slot": int,  # 1, 2, or 3
                    "alert_code": str,
                    "severity": str,
                    "priority": int,
                    "tags": str,
                    "core_reason": str,
                    "triggers_met": str,
                    "manager_summary": str,
                    "created_at": str,
                    "staff_name": str,
                    "client_info": str,
                    "follow_up_window": str
                }
            ],
            "summary": {
                "by_severity": {"HIGH": int, "MED": int, "LOW": int},
                "by_priority": {1: int, 2: int, 3: int},
                "by_tag": {tag: count},
                "date_range": {"earliest": str, "latest": str}
            }
        }
    
    Example:
        # Get all high severity revenue leakage alerts from last week
        result = get_alerts_by_tag(
            alert_tags="REVENUE_LEAKAGE",
            severity="HIGH",
            date_from="2025-12-01"
        )
    """
    try:
        client = _get_supabase_client()
        
        # Build query
        query = client.table('call_manager_alerts').select('*')
        
        # Filter by tags
        if isinstance(alert_tags, str):
            query = query.ilike('manager_alerts_tags', f'%{alert_tags}%')
        else:
            # Multiple tags - use OR condition
            tag_filters = ' | '.join([f'manager_alerts_tags.ilike.%{tag}%' for tag in alert_tags])
            query = query.or_(tag_filters)
        
        # Date filtering
        if date_from:
            query = query.gte('created_at', date_from)
        if date_to:
            query = query.lte('created_at', date_to)
        
        # Exclude NONE tags
        query = query.neq('manager_alerts_tags', 'NONE')
        
        # Limit and order
        query = query.order('created_at', desc=True).limit(limit * 3)  # Account for 3 slots per call
        
        result = query.execute()
        
        if not result.data:
            return {
                "success": True,
                "alert_count": 0,
                "alerts": [],
                "summary": {
                    "by_severity": {},
                    "by_priority": {},
                    "by_tag": {},
                    "date_range": {}
                },
                "message": "No alerts found matching criteria"
            }
        
        # Process alerts (each call can have up to 3 alert slots)
        alerts = []
        severity_counts = {"HIGH": 0, "MED": 0, "LOW": 0}
        priority_counts = {1: 0, 2: 0, 3: 0}
        tag_counts = {}
        dates = []
        
        for row in result.data:
            # Check each alert slot (1, 2, 3)
            for slot in [1, 2, 3]:
                alert_code = row.get(f'alert_{slot}_code')
                if not alert_code:
                    continue
                
                alert_severity = row.get(f'alert_{slot}_severity', 'MED')
                alert_priority = row.get(f'alert_{slot}_priority', 2)
                
                # Apply filters
                if severity and alert_severity != severity:
                    continue
                if priority and alert_priority != priority:
                    continue
                
                # Build alert object
                alert_obj = {
                    "call_id": row.get('call_id'),
                    "alert_slot": slot,
                    "alert_code": alert_code,
                    "severity": alert_severity,
                    "priority": alert_priority,
                    "tags": row.get('manager_alerts_tags'),
                    "core_reason": row.get(f'alert_{slot}_core_reason'),
                    "triggers_met": row.get(f'alert_{slot}_triggers_met'),
                    "key_metrics": row.get(f'alert_{slot}_key_metrics'),
                    "call_summary": row.get(f'alert_{slot}_call_summary'),
                    "evidence": row.get(f'alert_{slot}_evidence'),
                    "risk_if_ignored": row.get(f'alert_{slot}_risk_if_ignored'),
                    "manager_action_brief": row.get(f'alert_{slot}_manager_action_brief'),
                    "manager_action_steps": row.get(f'alert_{slot}_manager_action_steps'),
                    "coaching_focus": row.get(f'alert_{slot}_coaching_focus'),
                    "follow_up_window": row.get(f'alert_{slot}_follow_up_window'),
                    "manager_summary": row.get('manager_summary') or row.get('manager_alerts_summary'),
                    "created_at": row.get('created_at'),
                    "status": row.get(f'alert_{slot}_status', 'Active'),
                    # Manager notes (shared across all alerts for this call)
                    "manager_notes": row.get('manager_alert_notes'),
                    "manager_actions": row.get('manager_alert_actions'),
                    "manager_status": row.get('manager_alert_status')
                }
                
                alerts.append(alert_obj)
                
                # Update counts
                severity_counts[alert_severity] = severity_counts.get(alert_severity, 0) + 1
                priority_counts[alert_priority] = priority_counts.get(alert_priority, 0) + 1
                
                # Count tags
                tags = row.get('manager_alerts_tags', '').split(',')
                for tag in tags:
                    tag = tag.strip()
                    if tag and tag != 'NONE':
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
                dates.append(row.get('created_at'))
        
        # Limit alerts to requested amount
        alerts = alerts[:limit]
        
        # Build summary
        summary = {
            "by_severity": severity_counts,
            "by_priority": priority_counts,
            "by_tag": tag_counts,
            "date_range": {
                "earliest": min(dates) if dates else None,
                "latest": max(dates) if dates else None
            }
        }
        
        return {
            "success": True,
            "alert_count": len(alerts),
            "alerts": alerts,
            "summary": summary,
            "message": f"Found {len(alerts)} alerts matching criteria"
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts by tag: {e}")
        return {
            "success": False,
            "error": str(e),
            "alert_count": 0,
            "alerts": []
        }


def get_call_transcript(call_id: str) -> Dict[str, Any]:
    """
    Get full transcript and AI analysis for a specific call.
    
    Args:
        call_id: Unique call identifier (e.g., "VET-Smith-12-12-2024_14:30")
    
    Returns:
        {
            "success": bool,
            "call_id": str,
            "transcript": str,  # Full call transcript
            "analysis": str,    # Full AI analysis
            "metadata": {
                "created_at": str,
                "transcript_length": int,
                "analysis_length": int
            }
        }
    
    Example:
        result = get_call_transcript("VET-Smith-12-12-2024_14:30")
        print(result["transcript"])
    """
    try:
        client = _get_supabase_client()
        
        result = client.table('call_full_transcript_and_full_analysis') \
            .select('*') \
            .eq('call_id', call_id) \
            .single() \
            .execute()
        
        if not result.data:
            return {
                "success": False,
                "error": f"No transcript found for call_id: {call_id}",
                "call_id": call_id
            }
        
        transcript = result.data.get('full_transcript_text', '')
        analysis = result.data.get('full_analysis_text', '')
        
        return {
            "success": True,
            "call_id": call_id,
            "transcript": transcript,
            "analysis": analysis,
            "metadata": {
                "created_at": result.data.get('created_at'),
                "transcript_length": len(transcript) if transcript else 0,
                "analysis_length": len(analysis) if analysis else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting call transcript: {e}")
        return {
            "success": False,
            "error": str(e),
            "call_id": call_id
        }


def get_call_metadata(call_id: str) -> Dict[str, Any]:
    """
    Get detailed metadata for a veterinary call including staff, client, pet info.
    
    Args:
        call_id: Unique call identifier
    
    Returns:
        {
            "success": bool,
            "call_id": str,
            "metadata": {
                "staff_name": str,
                "call_date": str,
                "call_time": str,
                "call_duration_minutes": float,
                "client_first_name": str,
                "client_last_name": str,
                "pet_name": str,
                "pet_species": str,
                "phone_number": str,
                "call_type": str,
                "outcome": str,
                "sentiment_score": float,
                "quality_score": float
            }
        }
    
    Example:
        result = get_call_metadata("VET-Smith-12-12-2024_14:30")
    """
    try:
        client = _get_supabase_client()
        
        result = client.table('veterinary_calls') \
            .select('*') \
            .eq('call_id', call_id) \
            .single() \
            .execute()
        
        if not result.data:
            return {
                "success": False,
                "error": f"No metadata found for call_id: {call_id}",
                "call_id": call_id
            }
        
        data = result.data
        
        return {
            "success": True,
            "call_id": call_id,
            "metadata": {
                "staff_name": data.get('key_staffname'),
                "call_date": data.get('key_call_date'),
                "call_time": data.get('key_time'),
                "call_duration_minutes": data.get('key_call_duration_minutes'),
                "client_first_name": data.get('key_otherspeaker_firstname'),
                "client_last_name": data.get('key_otherspeaker_lastname'),
                "pet_name": data.get('key_pet_petname'),
                "pet_species": data.get('key_pet_petspecies'),
                "phone_number": data.get('key_ph'),
                "call_type": data.get('key_call_type'),
                "outcome": data.get('key_calloutcome'),
                "sentiment_score": data.get('vsa_sentiment_score'),
                "quality_score": data.get('vsa_quality_score'),
                "booking_offered": data.get('key_booking_offered'),
                "booking_confirmed": data.get('key_booking_confirmed')
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting call metadata: {e}")
        return {
            "success": False,
            "error": str(e),
            "call_id": call_id
        }


# ============================================================================
# MULTI-ALERT ANALYSIS & PLANNING TOOLS
# ============================================================================

def analyze_multiple_alerts(
    alert_ids: List[str] = None,
    alert_tags: Union[str, List[str]] = None,
    date_from: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Analyze multiple alerts to identify patterns and create action plan.
    
    Args:
        alert_ids: List of specific call_ids to analyze (optional)
        alert_tags: Tag(s) to filter by (optional, used if alert_ids not provided)
        date_from: Start date for analysis (ISO format)
        limit: Maximum alerts to analyze
    
    Returns:
        {
            "success": bool,
            "analysis": {
                "total_alerts": int,
                "common_patterns": [
                    {
                        "pattern": str,
                        "frequency": int,
                        "severity_distribution": dict,
                        "affected_staff": [str]
                    }
                ],
                "staff_performance": {
                    staff_name: {
                        "alert_count": int,
                        "severity_breakdown": dict,
                        "common_issues": [str],
                        "recommended_training": [str]
                    }
                },
                "systemic_issues": [
                    {
                        "issue": str,
                        "impact": str,
                        "affected_calls": int,
                        "urgency": str
                    }
                ],
                "recommended_actions": [
                    {
                        "action": str,
                        "priority": int,
                        "estimated_impact": str,
                        "timeline": str
                    }
                ]
            }
        }
    
    Example:
        # Analyze all revenue leakage alerts from last week
        result = analyze_multiple_alerts(
            alert_tags="REVENUE_LEAKAGE",
            date_from="2025-12-01"
        )
    """
    try:
        # Get alerts
        if alert_ids:
            # Fetch specific alerts
            client = _get_supabase_client()
            alerts_data = []
            for call_id in alert_ids[:limit]:
                result = client.table('call_manager_alerts') \
                    .select('*') \
                    .eq('call_id', call_id) \
                    .execute()
                if result.data:
                    alerts_data.extend(result.data)
            
            # Process into alert objects
            alerts = []
            for row in alerts_data:
                for slot in [1, 2, 3]:
                    if row.get(f'alert_{slot}_code'):
                        alerts.append({
                            "call_id": row.get('call_id'),
                            "alert_code": row.get(f'alert_{slot}_code'),
                            "severity": row.get(f'alert_{slot}_severity'),
                            "core_reason": row.get(f'alert_{slot}_core_reason'),
                            "tags": row.get('manager_alerts_tags'),
                            "staff_name": "Unknown"  # Would need to join with veterinary_calls
                        })
        else:
            # Use tag filtering
            result = get_alerts_by_tag(
                alert_tags=alert_tags or "ALL",
                date_from=date_from,
                limit=limit
            )
            if not result["success"]:
                return result
            alerts = result["alerts"]
        
        if not alerts:
            return {
                "success": True,
                "analysis": {
                    "total_alerts": 0,
                    "message": "No alerts to analyze"
                }
            }
        
        # Analyze patterns
        alert_codes = {}
        severity_dist = {"HIGH": 0, "MED": 0, "LOW": 0}
        staff_issues = {}
        
        for alert in alerts:
            code = alert.get("alert_code", "UNKNOWN")
            alert_codes[code] = alert_codes.get(code, 0) + 1
            
            sev = alert.get("severity", "MED")
            severity_dist[sev] = severity_dist.get(sev, 0) + 1
            
            staff = alert.get("staff_name", "Unknown")
            if staff not in staff_issues:
                staff_issues[staff] = {
                    "alert_count": 0,
                    "severity_breakdown": {"HIGH": 0, "MED": 0, "LOW": 0},
                    "common_issues": []
                }
            staff_issues[staff]["alert_count"] += 1
            staff_issues[staff]["severity_breakdown"][sev] += 1
            if code not in staff_issues[staff]["common_issues"]:
                staff_issues[staff]["common_issues"].append(code)
        
        # Identify common patterns
        common_patterns = [
            {
                "pattern": code,
                "frequency": count,
                "percentage": round((count / len(alerts)) * 100, 1)
            }
            for code, count in sorted(alert_codes.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Generate recommendations
        recommendations = []
        
        # High severity alerts need immediate attention
        if severity_dist["HIGH"] > 0:
            recommendations.append({
                "action": f"Address {severity_dist['HIGH']} high-severity alerts immediately",
                "priority": 1,
                "estimated_impact": "Prevent client churn and revenue loss",
                "timeline": "24 hours"
            })
        
        # Pattern-based recommendations
        if alert_codes:
            top_issue = max(alert_codes.items(), key=lambda x: x[1])
            recommendations.append({
                "action": f"Implement training program for {top_issue[0]} ({top_issue[1]} occurrences)",
                "priority": 2,
                "estimated_impact": f"Reduce {top_issue[0]} alerts by 40-60%",
                "timeline": "1-2 weeks"
            })
        
        return {
            "success": True,
            "analysis": {
                "total_alerts": len(alerts),
                "common_patterns": common_patterns,
                "severity_distribution": severity_dist,
                "staff_performance": staff_issues,
                "recommended_actions": recommendations,
                "insights": [
                    f"{len(alerts)} total alerts analyzed",
                    f"{severity_dist['HIGH']} require immediate action",
                    f"Most common issue: {max(alert_codes.items(), key=lambda x: x[1])[0]}" if alert_codes else "N/A"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing multiple alerts: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def create_action_plan(
    alert_ids: List[str],
    plan_type: str = "coaching",
    timeline: str = "1_week"
) -> Dict[str, Any]:
    """
    Create a structured action plan for addressing multiple alerts.
    
    Args:
        alert_ids: List of call_ids to include in plan
        plan_type: Type of plan ("coaching", "systemic_fix", "client_recovery")
        timeline: Execution timeline ("24_hours", "1_week", "1_month")
    
    Returns:
        {
            "success": bool,
            "plan": {
                "plan_id": str,
                "type": str,
                "timeline": str,
                "created_at": str,
                "alerts_covered": int,
                "phases": [
                    {
                        "phase": int,
                        "name": str,
                        "duration": str,
                        "tasks": [
                            {
                                "task": str,
                                "responsible": str,
                                "deadline": str,
                                "priority": int,
                                "estimated_time": str
                            }
                        ],
                        "success_metrics": [str]
                    }
                ],
                "resources_needed": [str],
                "expected_outcomes": [str]
            }
        }
    
    Example:
        # Create coaching plan for specific alerts
        result = create_action_plan(
            alert_ids=["VET-Smith-...", "VET-Jones-..."],
            plan_type="coaching",
            timeline="1_week"
        )
    """
    try:
        # Get alert details
        client = _get_supabase_client()
        alerts = []
        
        for call_id in alert_ids:
            result = client.table('call_manager_alerts') \
                .select('*') \
                .eq('call_id', call_id) \
                .execute()
            if result.data:
                alerts.extend(result.data)
        
        if not alerts:
            return {
                "success": False,
                "error": "No alerts found for provided IDs"
            }
        
        # Generate plan ID
        plan_id = f"PLAN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Build plan based on type
        phases = []
        
        if plan_type == "coaching":
            phases = [
                {
                    "phase": 1,
                    "name": "Alert Review & Prioritization",
                    "duration": "1-2 days",
                    "tasks": [
                        {
                            "task": f"Review {len(alert_ids)} alerts and rank by severity",
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
                    "tasks": [
                        {
                            "task": "Schedule 1-on-1 coaching sessions with affected staff",
                            "responsible": "Manager",
                            "deadline": "Day 3",
                            "priority": 1,
                            "estimated_time": "1 hour"
                        },
                        {
                            "task": "Conduct coaching sessions (30-45 min each)",
                            "responsible": "Manager",
                            "deadline": "Day 5",
                            "priority": 1,
                            "estimated_time": f"{len(alert_ids) * 0.75} hours"
                        }
                    ],
                    "success_metrics": ["All coaching sessions completed", "Action items documented"]
                },
                {
                    "phase": 3,
                    "name": "Follow-up & Validation",
                    "duration": "2-3 days",
                    "tasks": [
                        {
                            "task": "Monitor subsequent calls for improvement",
                            "responsible": "Manager",
                            "deadline": "Day 7",
                            "priority": 2,
                            "estimated_time": "2 hours"
                        },
                        {
                            "task": "Document outcomes and close alerts",
                            "responsible": "Manager",
                            "deadline": "Day 7",
                            "priority": 2,
                            "estimated_time": "1 hour"
                        }
                    ],
                    "success_metrics": ["Improvement validated", "Alerts closed"]
                }
            ]
        elif plan_type == "systemic_fix":
            phases = [
                {
                    "phase": 1,
                    "name": "Root Cause Analysis",
                    "duration": "2-3 days",
                    "tasks": [
                        {
                            "task": "Analyze patterns across all alerts",
                            "responsible": "Management Team",
                            "deadline": "Day 2",
                            "priority": 1,
                            "estimated_time": "3 hours"
                        },
                        {
                            "task": "Identify systemic gaps (process, training, tools)",
                            "responsible": "Management Team",
                            "deadline": "Day 3",
                            "priority": 1,
                            "estimated_time": "2 hours"
                        }
                    ],
                    "success_metrics": ["Root causes identified", "Fix plan drafted"]
                },
                {
                    "phase": 2,
                    "name": "Solution Implementation",
                    "duration": "1-2 weeks",
                    "tasks": [
                        {
                            "task": "Update processes/protocols",
                            "responsible": "Operations Manager",
                            "deadline": "Week 2",
                            "priority": 1,
                            "estimated_time": "5 hours"
                        },
                        {
                            "task": "Conduct team training on new protocols",
                            "responsible": "Manager",
                            "deadline": "Week 2",
                            "priority": 1,
                            "estimated_time": "4 hours"
                        }
                    ],
                    "success_metrics": ["Protocols updated", "Team trained"]
                },
                {
                    "phase": 3,
                    "name": "Monitoring & Adjustment",
                    "duration": "Ongoing",
                    "tasks": [
                        {
                            "task": "Monitor alert trends for 2 weeks",
                            "responsible": "Manager",
                            "deadline": "Week 4",
                            "priority": 2,
                            "estimated_time": "2 hours/week"
                        }
                    ],
                    "success_metrics": ["Alert frequency reduced by 30%+"]
                }
            ]
        elif plan_type == "client_recovery":
            phases = [
                {
                    "phase": 1,
                    "name": "Client Outreach",
                    "duration": "1-2 days",
                    "tasks": [
                        {
                            "task": "Prepare personalized recovery scripts",
                            "responsible": "Manager",
                            "deadline": "Day 1",
                            "priority": 1,
                            "estimated_time": "2 hours"
                        },
                        {
                            "task": "Call affected clients directly",
                            "responsible": "Senior Staff/Manager",
                            "deadline": "Day 2",
                            "priority": 1,
                            "estimated_time": f"{len(alert_ids) * 0.5} hours"
                        }
                    ],
                    "success_metrics": ["All clients contacted", "Issues acknowledged"]
                },
                {
                    "phase": 2,
                    "name": "Service Recovery",
                    "duration": "3-5 days",
                    "tasks": [
                        {
                            "task": "Offer appropriate remediation (discount, free service, etc.)",
                            "responsible": "Manager",
                            "deadline": "Day 3",
                            "priority": 1,
                            "estimated_time": "1 hour"
                        },
                        {
                            "task": "Schedule follow-up appointments",
                            "responsible": "Front Desk",
                            "deadline": "Day 5",
                            "priority": 2,
                            "estimated_time": "2 hours"
                        }
                    ],
                    "success_metrics": ["Recovery offers made", "Client satisfaction restored"]
                }
            ]
        
        # Resources and outcomes
        resources_needed = [
            "Manager time commitment",
            "Access to call recordings",
            "Coaching templates/scripts",
            "Training materials"
        ]
        
        expected_outcomes = [
            f"Address {len(alert_ids)} alerts within {timeline.replace('_', ' ')}",
            "Improve staff performance metrics",
            "Reduce future alert frequency",
            "Enhance client experience"
        ]
        
        return {
            "success": True,
            "plan": {
                "plan_id": plan_id,
                "type": plan_type,
                "timeline": timeline,
                "created_at": datetime.now().isoformat(),
                "alerts_covered": len(alert_ids),
                "call_ids": alert_ids,
                "phases": phases,
                "resources_needed": resources_needed,
                "expected_outcomes": expected_outcomes
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating action plan: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# ALERT MANAGEMENT TOOLS
# ============================================================================

def update_alert_status(
    call_id: str,
    status: str,
    notes: Optional[str] = None,
    actions_taken: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update the status and notes for an alert.
    
    Args:
        call_id: Call identifier
        status: New status ("New", "In Progress", "Resolved", "Dismissed")
        notes: Manager notes about the alert
        actions_taken: Actions taken to address the alert
    
    Returns:
        {
            "success": bool,
            "message": str,
            "updated_fields": dict
        }
    
    Example:
        result = update_alert_status(
            call_id="VET-Smith-12-12-2024_14:30",
            status="In Progress",
            notes="Scheduled coaching session for tomorrow",
            actions_taken="Reviewed call recording, identified 3 improvement areas"
        )
    """
    try:
        client = _get_supabase_client()
        
        update_data = {
            "manager_alert_status": status,
            "manager_alert_notes_date": datetime.now().isoformat()
        }
        
        if notes:
            update_data["manager_alert_notes"] = notes
        
        if actions_taken:
            update_data["manager_alert_actions"] = actions_taken
        
        result = client.table('call_manager_alerts') \
            .update(update_data) \
            .eq('call_id', call_id) \
            .execute()
        
        return {
            "success": True,
            "message": f"Alert status updated to '{status}' for call {call_id}",
            "updated_fields": update_data
        }
        
    except Exception as e:
        logger.error(f"Error updating alert status: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def bulk_update_alerts(
    call_ids: List[str],
    status: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Bulk update multiple alerts at once.
    
    Args:
        call_ids: List of call identifiers
        status: New status to apply to all
        notes: Notes to add to all alerts
    
    Returns:
        {
            "success": bool,
            "updated_count": int,
            "failed_count": int,
            "details": [{"call_id": str, "status": str, "error": str}]
        }
    
    Example:
        result = bulk_update_alerts(
            call_ids=["VET-Smith-...", "VET-Jones-..."],
            status="Resolved",
            notes="Coaching completed, follow-up scheduled"
        )
    """
    try:
        results = []
        updated = 0
        failed = 0
        
        for call_id in call_ids:
            result = update_alert_status(call_id, status, notes)
            if result["success"]:
                updated += 1
                results.append({"call_id": call_id, "status": "success"})
            else:
                failed += 1
                results.append({"call_id": call_id, "status": "failed", "error": result.get("error")})
        
        return {
            "success": True,
            "updated_count": updated,
            "failed_count": failed,
            "total_processed": len(call_ids),
            "details": results
        }
        
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# EXPORT & REGISTRATION
# ============================================================================

# Export all tools for AI agent use
__all__ = [
    'get_alerts_by_tag',
    'get_call_transcript',
    'get_call_metadata',
    'analyze_multiple_alerts',
    'create_action_plan',
    'update_alert_status',
    'bulk_update_alerts'
]


# Tool metadata for registration
TOOLS_METADATA = {
    "platform": "veterinary_alerts",
    "version": "1.0.0",
    "description": "AI tools for managing veterinary call alerts and planning actions",
    "database": "VSA Supabase (wuwmvtslltqhaycyukxk)",
    "tools": [
        {
            "name": "get_alerts_by_tag",
            "category": "alert_discovery",
            "complexity": "medium",
            "estimated_time": "2-5 seconds"
        },
        {
            "name": "get_call_transcript",
            "category": "data_access",
            "complexity": "low",
            "estimated_time": "1-2 seconds"
        },
        {
            "name": "get_call_metadata",
            "category": "data_access",
            "complexity": "low",
            "estimated_time": "1-2 seconds"
        },
        {
            "name": "analyze_multiple_alerts",
            "category": "analysis",
            "complexity": "high",
            "estimated_time": "5-15 seconds"
        },
        {
            "name": "create_action_plan",
            "category": "planning",
            "complexity": "high",
            "estimated_time": "3-8 seconds"
        },
        {
            "name": "update_alert_status",
            "category": "management",
            "complexity": "low",
            "estimated_time": "1-2 seconds"
        },
        {
            "name": "bulk_update_alerts",
            "category": "management",
            "complexity": "medium",
            "estimated_time": "2-10 seconds"
        }
    ]
}

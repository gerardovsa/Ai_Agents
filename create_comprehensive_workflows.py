"""Create 4 comprehensive visual automation workflows"""
import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection
import json
import time

def create_workflows():
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Workflow 1: Morning Email Check & Triage
    workflow1 = {
        "automation_id": f"wf_morning_emails_{int(time.time())}",
        "user_id": 1,
        "title": "Morning Email Check & Triage",
        "slug": f"morning-email-triage-{int(time.time())}",
        "description": "Automatically checks Gmail every morning at 8am, categorizes emails by priority, and creates a summary digest with action items.",
        "category": "email",
        "ui_json": {
            "shapes": [
                {
                    "id": "trigger_1",
                    "type": "trigger",
                    "x": 100,
                    "y": 100,
                    "width": 200,
                    "height": 90,
                    "text": "Schedule Trigger\n8:00 AM Daily",
                    "color": "#10B981"
                },
                {
                    "id": "action_1",
                    "type": "tool",
                    "x": 100,
                    "y": 250,
                    "width": 200,
                    "height": 90,
                    "text": "Get Unread Emails\ngmail_list_messages",
                    "color": "#6B7280"
                },
                {
                    "id": "action_2",
                    "type": "tool",
                    "x": 100,
                    "y": 400,
                    "width": 200,
                    "height": 90,
                    "text": "Analyze with AI\nClassify Priority",
                    "color": "#6B7280"
                },
                {
                    "id": "decision_1",
                    "type": "decision",
                    "x": 100,
                    "y": 550,
                    "width": 200,
                    "height": 90,
                    "text": "Has Urgent Emails?",
                    "color": "#F59E0B"
                },
                {
                    "id": "action_3",
                    "type": "tool",
                    "x": 400,
                    "y": 550,
                    "width": 200,
                    "height": 90,
                    "text": "Send Urgent Alert\nslack_post_message",
                    "color": "#6B7280"
                },
                {
                    "id": "action_4",
                    "type": "tool",
                    "x": 100,
                    "y": 700,
                    "width": 200,
                    "height": 90,
                    "text": "Create Summary\nai_summarize_text",
                    "color": "#6B7280"
                },
                {
                    "id": "output_1",
                    "type": "output",
                    "x": 100,
                    "y": 850,
                    "width": 200,
                    "height": 90,
                    "text": "Send Daily Digest\ngmail_send_email",
                    "color": "#EAB308"
                }
            ],
            "connections": [
                {"from": "trigger_1", "to": "action_1"},
                {"from": "action_1", "to": "action_2"},
                {"from": "action_2", "to": "decision_1"},
                {"from": "decision_1", "to": "action_3", "label": "Yes"},
                {"from": "decision_1", "to": "action_4", "label": "No"},
                {"from": "action_3", "to": "action_4"},
                {"from": "action_4", "to": "output_1"}
            ]
        },
        "execution_json": {
            "trigger": {
                "type": "schedule",
                "schedule_cron": "0 8 * * *",
                "timezone": "Australia/Sydney"
            },
            "actions": [
                {
                    "id": "action_1",
                    "tool": "gmail_list_messages",
                    "parameters": {
                        "max_results": 50,
                        "query": "is:unread"
                    }
                },
                {
                    "id": "action_2",
                    "tool": "ai_analyze_text",
                    "parameters": {
                        "text": "{{action_1.messages}}",
                        "prompt": "Classify these emails by priority (urgent/high/medium/low) and extract action items"
                    }
                },
                {
                    "id": "action_3",
                    "tool": "slack_post_message",
                    "parameters": {
                        "channel": "#alerts",
                        "text": "🚨 You have {{urgent_count}} urgent emails requiring immediate attention"
                    },
                    "condition": "{{action_2.urgent_count}} > 0"
                },
                {
                    "id": "action_4",
                    "tool": "ai_summarize_text",
                    "parameters": {
                        "text": "{{action_2.classified_emails}}",
                        "max_length": 1000
                    }
                },
                {
                    "id": "output_1",
                    "tool": "gmail_send_email",
                    "parameters": {
                        "to": "{{user_email}}",
                        "subject": "Daily Email Digest - {{date}}",
                        "body": "{{action_4.summary}}"
                    }
                }
            ]
        },
        "status": "draft",
        "is_scheduled": False
    }
    
    # Workflow 2: Quote Request Processing with Synergy Session
    workflow2 = {
        "automation_id": f"wf_quote_requests_{int(time.time())}",
        "user_id": 1,
        "title": "Quote Request Email → Synergy Session Builder",
        "slug": f"quote-request-synergy-{int(time.time())}",
        "description": "Scans emails for quote requests, creates Synergy session with each client as a milestone, breaks down tasks, generates internal docs with quote details, creates draft responses.",
        "category": "crm",
        "ui_json": {
            "shapes": [
                {
                    "id": "trigger_1",
                    "type": "trigger",
                    "x": 150,
                    "y": 80,
                    "width": 220,
                    "height": 100,
                    "text": "Email Trigger\nNew Quote Request",
                    "color": "#10B981"
                },
                {
                    "id": "action_1",
                    "type": "tool",
                    "x": 150,
                    "y": 230,
                    "width": 220,
                    "height": 100,
                    "text": "Search Quote Emails\ngmail_search",
                    "color": "#6B7280"
                },
                {
                    "id": "action_2",
                    "type": "tool",
                    "x": 150,
                    "y": 380,
                    "width": 220,
                    "height": 100,
                    "text": "Extract Details\nAI Parse Email",
                    "color": "#6B7280"
                },
                {
                    "id": "decision_1",
                    "type": "decision",
                    "x": 150,
                    "y": 530,
                    "width": 220,
                    "height": 100,
                    "text": "Valid Quote Request?",
                    "color": "#F59E0B"
                },
                {
                    "id": "action_3",
                    "type": "tool",
                    "x": 500,
                    "y": 530,
                    "width": 220,
                    "height": 100,
                    "text": "Create Synergy Session\nsynergy_create_session",
                    "color": "#6B7280"
                },
                {
                    "id": "action_4",
                    "type": "tool",
                    "x": 500,
                    "y": 680,
                    "width": 220,
                    "height": 100,
                    "text": "Add Client Milestone\nsynergy_add_milestone",
                    "color": "#6B7280"
                },
                {
                    "id": "action_5",
                    "type": "tool",
                    "x": 500,
                    "y": 830,
                    "width": 220,
                    "height": 100,
                    "text": "Create Tasks\nsynergy_add_task",
                    "color": "#6B7280"
                },
                {
                    "id": "action_6",
                    "type": "tool",
                    "x": 800,
                    "y": 680,
                    "width": 220,
                    "height": 100,
                    "text": "Create Quote Doc\ngoogle_docs_create",
                    "color": "#6B7280"
                },
                {
                    "id": "action_7",
                    "type": "tool",
                    "x": 800,
                    "y": 830,
                    "width": 220,
                    "height": 100,
                    "text": "Calculate Quote\ncalculate_quote",
                    "color": "#6B7280"
                },
                {
                    "id": "action_8",
                    "type": "tool",
                    "x": 800,
                    "y": 980,
                    "width": 220,
                    "height": 100,
                    "text": "Generate Draft Email\nai_generate_text",
                    "color": "#6B7280"
                },
                {
                    "id": "action_9",
                    "type": "tool",
                    "x": 500,
                    "y": 980,
                    "width": 220,
                    "height": 100,
                    "text": "Attach Docs to Milestone\nsynergy_update_milestone",
                    "color": "#6B7280"
                },
                {
                    "id": "output_1",
                    "type": "output",
                    "x": 500,
                    "y": 1130,
                    "width": 220,
                    "height": 100,
                    "text": "Notify Team\nslack_post_message",
                    "color": "#EAB308"
                }
            ],
            "connections": [
                {"from": "trigger_1", "to": "action_1"},
                {"from": "action_1", "to": "action_2"},
                {"from": "action_2", "to": "decision_1"},
                {"from": "decision_1", "to": "action_3", "label": "Yes"},
                {"from": "action_3", "to": "action_4"},
                {"from": "action_4", "to": "action_5"},
                {"from": "action_4", "to": "action_6"},
                {"from": "action_6", "to": "action_7"},
                {"from": "action_7", "to": "action_8"},
                {"from": "action_5", "to": "action_9"},
                {"from": "action_8", "to": "action_9"},
                {"from": "action_9", "to": "output_1"}
            ]
        },
        "execution_json": {
            "trigger": {
                "type": "event",
                "event_type": "gmail_new_message",
                "filter": "subject:(quote OR quotation OR pricing OR estimate)"
            },
            "actions": [
                {
                    "id": "action_1",
                    "tool": "gmail_search",
                    "parameters": {
                        "query": "subject:(quote OR quotation OR pricing) is:unread newer_than:1d",
                        "max_results": 20
                    }
                },
                {
                    "id": "action_2",
                    "tool": "ai_extract_structured_data",
                    "parameters": {
                        "text": "{{action_1.messages}}",
                        "schema": {
                            "client_name": "string",
                            "client_email": "string",
                            "products": "array",
                            "quantities": "array",
                            "deadline": "date",
                            "special_requirements": "string"
                        }
                    }
                },
                {
                    "id": "action_3",
                    "tool": "synergy_create_session",
                    "parameters": {
                        "title": "Quote Requests - {{date}}",
                        "description": "Processing quote requests from email",
                        "session_type": "quotes"
                    }
                },
                {
                    "id": "action_4",
                    "tool": "synergy_add_milestone",
                    "parameters": {
                        "session_id": "{{action_3.session_id}}",
                        "title": "{{action_2.client_name}} - Quote Request",
                        "description": "Quote for {{action_2.products}}",
                        "due_date": "{{action_2.deadline}}"
                    }
                },
                {
                    "id": "action_5",
                    "tool": "synergy_add_task",
                    "parameters": {
                        "milestone_id": "{{action_4.milestone_id}}",
                        "tasks": [
                            {
                                "title": "Review Client Requirements",
                                "subtasks": [
                                    "Verify product specifications",
                                    "Check quantity requirements",
                                    "Identify special requirements"
                                ]
                            },
                            {
                                "title": "Calculate Pricing",
                                "subtasks": [
                                    "Calculate base cost",
                                    "Apply volume discounts",
                                    "Add shipping costs"
                                ]
                            },
                            {
                                "title": "Prepare Quote Documentation",
                                "subtasks": [
                                    "Create quote spreadsheet",
                                    "Generate PDF quote",
                                    "Draft email response"
                                ]
                            }
                        ]
                    }
                },
                {
                    "id": "action_6",
                    "tool": "google_docs_create",
                    "parameters": {
                        "title": "Quote Details - {{action_2.client_name}}",
                        "content": "Client: {{action_2.client_name}}\nEmail: {{action_2.client_email}}\n\nProducts:\n{{action_2.products}}\n\nQuantities:\n{{action_2.quantities}}\n\nDeadline: {{action_2.deadline}}\n\nSpecial Requirements:\n{{action_2.special_requirements}}"
                    }
                },
                {
                    "id": "action_7",
                    "tool": "calculate_comprehensive_quote",
                    "parameters": {
                        "products": "{{action_2.products}}",
                        "quantities": "{{action_2.quantities}}",
                        "client_type": "standard"
                    }
                },
                {
                    "id": "action_8",
                    "tool": "ai_generate_text",
                    "parameters": {
                        "prompt": "Write a professional quote email for {{action_2.client_name}} with total: ${{action_7.total_price}}",
                        "max_length": 500
                    }
                },
                {
                    "id": "action_9",
                    "tool": "synergy_update_milestone",
                    "parameters": {
                        "milestone_id": "{{action_4.milestone_id}}",
                        "internal_docs": [
                            "{{action_6.doc_url}}",
                            "Quote: ${{action_7.total_price}}",
                            "Draft Email: {{action_8.email_text}}"
                        ]
                    }
                },
                {
                    "id": "output_1",
                    "tool": "slack_post_message",
                    "parameters": {
                        "channel": "#quotes",
                        "text": "✅ New quote request processed for {{action_2.client_name}} - ${{action_7.total_price}}"
                    }
                }
            ]
        },
        "status": "draft",
        "is_scheduled": False
    }
    
    # Workflow 3: Xero Accounts Payable → Synergy Session
    workflow3 = {
        "automation_id": f"wf_xero_payables_{int(time.time())}",
        "user_id": 1,
        "title": "Xero Accounts Payable → Synergy Payment Session",
        "slug": f"xero-payables-synergy-{int(time.time())}",
        "description": "Checks Xero for overdue bills and invoices, creates Synergy session with payment tracking, organizes by supplier/priority, generates payment schedules.",
        "category": "accounting",
        "ui_json": {
            "shapes": [
                {
                    "id": "trigger_1",
                    "type": "trigger",
                    "x": 100,
                    "y": 80,
                    "width": 220,
                    "height": 100,
                    "text": "Schedule Trigger\nWeekly Mon 9am",
                    "color": "#10B981"
                },
                {
                    "id": "action_1",
                    "type": "tool",
                    "x": 100,
                    "y": 230,
                    "width": 220,
                    "height": 100,
                    "text": "Get Xero Bills\nxero_get_bills",
                    "color": "#6B7280"
                },
                {
                    "id": "action_2",
                    "type": "tool",
                    "x": 100,
                    "y": 380,
                    "width": 220,
                    "height": 100,
                    "text": "Filter Overdue\nFilter by Date",
                    "color": "#6B7280"
                },
                {
                    "id": "decision_1",
                    "type": "decision",
                    "x": 100,
                    "y": 530,
                    "width": 220,
                    "height": 100,
                    "text": "Has Overdue Bills?",
                    "color": "#F59E0B"
                },
                {
                    "id": "action_3",
                    "type": "tool",
                    "x": 450,
                    "y": 530,
                    "width": 220,
                    "height": 100,
                    "text": "Create Synergy Session\nsynergy_create_session",
                    "color": "#6B7280"
                },
                {
                    "id": "action_4",
                    "type": "tool",
                    "x": 450,
                    "y": 680,
                    "width": 220,
                    "height": 100,
                    "text": "Group by Supplier\nProcess Each Supplier",
                    "color": "#6B7280"
                },
                {
                    "id": "action_5",
                    "type": "tool",
                    "x": 450,
                    "y": 830,
                    "width": 220,
                    "height": 100,
                    "text": "Add Supplier Milestone\nsynergy_add_milestone",
                    "color": "#6B7280"
                },
                {
                    "id": "action_6",
                    "type": "tool",
                    "x": 750,
                    "y": 680,
                    "width": 220,
                    "height": 100,
                    "text": "Create Payment Tasks\nsynergy_add_task",
                    "color": "#6B7280"
                },
                {
                    "id": "action_7",
                    "type": "tool",
                    "x": 750,
                    "y": 830,
                    "width": 220,
                    "height": 100,
                    "text": "Generate Payment Schedule\ngoogle_sheets_create",
                    "color": "#6B7280"
                },
                {
                    "id": "action_8",
                    "type": "tool",
                    "x": 750,
                    "y": 980,
                    "width": 220,
                    "height": 100,
                    "text": "Calculate Priorities\nAI Prioritization",
                    "color": "#6B7280"
                },
                {
                    "id": "action_9",
                    "type": "tool",
                    "x": 450,
                    "y": 980,
                    "width": 220,
                    "height": 100,
                    "text": "Update Milestone Docs\nsynergy_update_milestone",
                    "color": "#6B7280"
                },
                {
                    "id": "output_1",
                    "type": "output",
                    "x": 450,
                    "y": 1130,
                    "width": 220,
                    "height": 100,
                    "text": "Send Summary Email\ngmail_send_email",
                    "color": "#EAB308"
                }
            ],
            "connections": [
                {"from": "trigger_1", "to": "action_1"},
                {"from": "action_1", "to": "action_2"},
                {"from": "action_2", "to": "decision_1"},
                {"from": "decision_1", "to": "action_3", "label": "Yes"},
                {"from": "action_3", "to": "action_4"},
                {"from": "action_4", "to": "action_5"},
                {"from": "action_4", "to": "action_6"},
                {"from": "action_5", "to": "action_9"},
                {"from": "action_6", "to": "action_7"},
                {"from": "action_7", "to": "action_8"},
                {"from": "action_8", "to": "action_9"},
                {"from": "action_9", "to": "output_1"}
            ]
        },
        "execution_json": {
            "trigger": {
                "type": "schedule",
                "schedule_cron": "0 9 * * 1",
                "timezone": "Australia/Sydney"
            },
            "actions": [
                {
                    "id": "action_1",
                    "tool": "xero_get_bills",
                    "parameters": {
                        "status": "AUTHORISED",
                        "where": "AmountDue > 0"
                    }
                },
                {
                    "id": "action_2",
                    "tool": "filter_overdue_bills",
                    "parameters": {
                        "bills": "{{action_1.bills}}",
                        "date": "{{today}}"
                    }
                },
                {
                    "id": "action_3",
                    "tool": "synergy_create_session",
                    "parameters": {
                        "title": "Accounts Payable Review - {{date}}",
                        "description": "Weekly overdue bills review and payment planning",
                        "session_type": "accounting"
                    }
                },
                {
                    "id": "action_4",
                    "tool": "group_by_supplier",
                    "parameters": {
                        "bills": "{{action_2.overdue_bills}}"
                    }
                },
                {
                    "id": "action_5",
                    "tool": "synergy_add_milestone",
                    "parameters": {
                        "session_id": "{{action_3.session_id}}",
                        "title": "{{supplier_name}} - ${{total_amount}}",
                        "description": "{{bill_count}} overdue bills",
                        "priority": "{{priority_level}}"
                    }
                },
                {
                    "id": "action_6",
                    "tool": "synergy_add_task",
                    "parameters": {
                        "milestone_id": "{{action_5.milestone_id}}",
                        "tasks": [
                            {
                                "title": "Review Bills",
                                "subtasks": [
                                    "Verify invoice accuracy",
                                    "Check payment terms",
                                    "Confirm goods/services received"
                                ]
                            },
                            {
                                "title": "Process Payment",
                                "subtasks": [
                                    "Schedule payment date",
                                    "Prepare payment documentation",
                                    "Get approval if needed"
                                ]
                            },
                            {
                                "title": "Update Records",
                                "subtasks": [
                                    "Mark as paid in Xero",
                                    "Update cash flow forecast",
                                    "File documentation"
                                ]
                            }
                        ]
                    }
                },
                {
                    "id": "action_7",
                    "tool": "google_sheets_create",
                    "parameters": {
                        "title": "Payment Schedule - {{date}}",
                        "headers": ["Supplier", "Invoice", "Amount", "Due Date", "Priority", "Payment Date"],
                        "data": "{{action_4.grouped_bills}}"
                    }
                },
                {
                    "id": "action_8",
                    "tool": "ai_prioritize_payments",
                    "parameters": {
                        "bills": "{{action_2.overdue_bills}}",
                        "criteria": ["days_overdue", "amount", "supplier_importance", "payment_terms"]
                    }
                },
                {
                    "id": "action_9",
                    "tool": "synergy_update_milestone",
                    "parameters": {
                        "milestone_id": "{{action_5.milestone_id}}",
                        "internal_docs": [
                            "Payment Schedule: {{action_7.sheet_url}}",
                            "Priority: {{action_8.priority}}",
                            "Total Amount: ${{total_amount}}",
                            "Due Date: {{earliest_due_date}}"
                        ]
                    }
                },
                {
                    "id": "output_1",
                    "tool": "gmail_send_email",
                    "parameters": {
                        "to": "accounts@company.com",
                        "subject": "Weekly AP Review - {{overdue_count}} Overdue Bills",
                        "body": "Total Overdue: ${{total_overdue}}\n\nSynergy Session: {{action_3.session_url}}\nPayment Schedule: {{action_7.sheet_url}}"
                    }
                }
            ]
        },
        "status": "draft",
        "is_scheduled": False
    }
    
    # Workflow 4: High-Value Client Reactivation Campaign
    workflow4 = {
        "automation_id": f"wf_client_reactivation_{int(time.time())}",
        "user_id": 1,
        "title": "High-Value Client Reactivation - FRED Database Analysis",
        "slug": f"fred-reactivation-campaign-{int(time.time())}",
        "description": "Queries FRED database for high-value clients who haven't ordered but were due to order. AI researches each client, develops personalized reactivation strategy, creates outreach campaigns.",
        "category": "crm",
        "ui_json": {
            "shapes": [
                {
                    "id": "trigger_1",
                    "type": "trigger",
                    "x": 120,
                    "y": 80,
                    "width": 240,
                    "height": 100,
                    "text": "Schedule Trigger\nMonthly 1st 10am",
                    "color": "#10B981"
                },
                {
                    "id": "action_1",
                    "type": "tool",
                    "x": 120,
                    "y": 230,
                    "width": 240,
                    "height": 100,
                    "text": "Query FRED Database\nfred_query_clients",
                    "color": "#6B7280"
                },
                {
                    "id": "action_2",
                    "type": "tool",
                    "x": 120,
                    "y": 380,
                    "width": 240,
                    "height": 100,
                    "text": "Calculate Expected Orders\nAnalyze Order History",
                    "color": "#6B7280"
                },
                {
                    "id": "action_3",
                    "type": "tool",
                    "x": 120,
                    "y": 530,
                    "width": 240,
                    "height": 100,
                    "text": "Filter Inactive Clients\nDue But Not Ordered",
                    "color": "#6B7280"
                },
                {
                    "id": "decision_1",
                    "type": "decision",
                    "x": 120,
                    "y": 680,
                    "width": 240,
                    "height": 100,
                    "text": "Found Inactive Clients?",
                    "color": "#F59E0B"
                },
                {
                    "id": "action_4",
                    "type": "tool",
                    "x": 480,
                    "y": 680,
                    "width": 240,
                    "height": 100,
                    "text": "Create Synergy Session\nsynergy_create_session",
                    "color": "#6B7280"
                },
                {
                    "id": "action_5",
                    "type": "tool",
                    "x": 480,
                    "y": 830,
                    "width": 240,
                    "height": 100,
                    "text": "AI Research Each Client\nweb_search + analyze",
                    "color": "#6B7280"
                },
                {
                    "id": "action_6",
                    "type": "tool",
                    "x": 800,
                    "y": 680,
                    "width": 240,
                    "height": 100,
                    "text": "Add Client Milestone\nsynergy_add_milestone",
                    "color": "#6B7280"
                },
                {
                    "id": "action_7",
                    "type": "tool",
                    "x": 800,
                    "y": 830,
                    "width": 240,
                    "height": 100,
                    "text": "Create Research Doc\ngoogle_docs_create",
                    "color": "#6B7280"
                },
                {
                    "id": "action_8",
                    "type": "tool",
                    "x": 800,
                    "y": 980,
                    "width": 240,
                    "height": 100,
                    "text": "Develop Strategy\nAI Strategy Generator",
                    "color": "#6B7280"
                },
                {
                    "id": "action_9",
                    "type": "tool",
                    "x": 800,
                    "y": 1130,
                    "width": 240,
                    "height": 100,
                    "text": "Generate Email Campaigns\nai_generate_text",
                    "color": "#6B7280"
                },
                {
                    "id": "action_10",
                    "type": "tool",
                    "x": 480,
                    "y": 980,
                    "width": 240,
                    "height": 100,
                    "text": "Create Action Tasks\nsynergy_add_task",
                    "color": "#6B7280"
                },
                {
                    "id": "action_11",
                    "type": "tool",
                    "x": 480,
                    "y": 1130,
                    "width": 240,
                    "height": 100,
                    "text": "Update Milestone\nsynergy_update_milestone",
                    "color": "#6B7280"
                },
                {
                    "id": "output_1",
                    "type": "output",
                    "x": 480,
                    "y": 1280,
                    "width": 240,
                    "height": 100,
                    "text": "Send Team Report\nslack_post_message",
                    "color": "#EAB308"
                }
            ],
            "connections": [
                {"from": "trigger_1", "to": "action_1"},
                {"from": "action_1", "to": "action_2"},
                {"from": "action_2", "to": "action_3"},
                {"from": "action_3", "to": "decision_1"},
                {"from": "decision_1", "to": "action_4", "label": "Yes"},
                {"from": "action_4", "to": "action_5"},
                {"from": "action_5", "to": "action_6"},
                {"from": "action_6", "to": "action_7"},
                {"from": "action_7", "to": "action_8"},
                {"from": "action_8", "to": "action_9"},
                {"from": "action_6", "to": "action_10"},
                {"from": "action_9", "to": "action_11"},
                {"from": "action_10", "to": "action_11"},
                {"from": "action_11", "to": "output_1"}
            ]
        },
        "execution_json": {
            "trigger": {
                "type": "schedule",
                "schedule_cron": "0 10 1 * *",
                "timezone": "Australia/Sydney"
            },
            "actions": [
                {
                    "id": "action_1",
                    "tool": "fred_query_clients",
                    "parameters": {
                        "query": "SELECT * FROM clients WHERE lifetime_value > 10000 ORDER BY last_order_date DESC"
                    }
                },
                {
                    "id": "action_2",
                    "tool": "calculate_expected_orders",
                    "parameters": {
                        "clients": "{{action_1.clients}}",
                        "analysis_period": "90_days"
                    }
                },
                {
                    "id": "action_3",
                    "tool": "filter_inactive_clients",
                    "parameters": {
                        "clients": "{{action_2.analyzed_clients}}",
                        "criteria": {
                            "expected_order": True,
                            "actual_order": False,
                            "days_overdue": "> 30"
                        }
                    }
                },
                {
                    "id": "action_4",
                    "tool": "synergy_create_session",
                    "parameters": {
                        "title": "Client Reactivation Campaign - {{month}} {{year}}",
                        "description": "High-value clients reactivation strategy and outreach",
                        "session_type": "sales"
                    }
                },
                {
                    "id": "action_5",
                    "tool": "ai_research_client",
                    "parameters": {
                        "client": "{{client_data}}",
                        "research_points": [
                            "Recent company news",
                            "Industry trends",
                            "Competitor analysis",
                            "Social media activity",
                            "Business changes"
                        ]
                    }
                },
                {
                    "id": "action_6",
                    "tool": "synergy_add_milestone",
                    "parameters": {
                        "session_id": "{{action_4.session_id}}",
                        "title": "{{client_name}} - ${{lifetime_value}} LTV",
                        "description": "Last order: {{last_order_date}} ({{days_since_order}} days ago)",
                        "priority": "high"
                    }
                },
                {
                    "id": "action_7",
                    "tool": "google_docs_create",
                    "parameters": {
                        "title": "Client Research - {{client_name}}",
                        "content": "Client: {{client_name}}\nLifetime Value: ${{lifetime_value}}\nLast Order: {{last_order_date}}\n\nResearch Findings:\n{{action_5.research}}\n\nOrder History:\n{{order_history}}\n\nPrevious Products:\n{{products_ordered}}"
                    }
                },
                {
                    "id": "action_8",
                    "tool": "ai_develop_reactivation_strategy",
                    "parameters": {
                        "client_data": "{{client_data}}",
                        "research": "{{action_5.research}}",
                        "prompt": "Develop a personalized reactivation strategy considering client history, industry trends, and current needs"
                    }
                },
                {
                    "id": "action_9",
                    "tool": "ai_generate_text",
                    "parameters": {
                        "prompt": "Write 3 personalized email campaigns for {{client_name}} based on strategy: {{action_8.strategy}}",
                        "tone": "professional, personal, value-focused",
                        "length": "medium"
                    }
                },
                {
                    "id": "action_10",
                    "tool": "synergy_add_task",
                    "parameters": {
                        "milestone_id": "{{action_6.milestone_id}}",
                        "tasks": [
                            {
                                "title": "Phase 1: Initial Outreach",
                                "subtasks": [
                                    "Review client research",
                                    "Personalize email template",
                                    "Send initial reconnection email",
                                    "Schedule follow-up"
                                ]
                            },
                            {
                                "title": "Phase 2: Value Demonstration",
                                "subtasks": [
                                    "Send product updates email",
                                    "Share relevant case studies",
                                    "Offer exclusive promotion",
                                    "Request phone call"
                                ]
                            },
                            {
                                "title": "Phase 3: Closing Strategy",
                                "subtasks": [
                                    "Send final outreach email",
                                    "Offer custom quote",
                                    "Personal call from account manager",
                                    "Mark as completed/inactive"
                                ]
                            }
                        ]
                    }
                },
                {
                    "id": "action_11",
                    "tool": "synergy_update_milestone",
                    "parameters": {
                        "milestone_id": "{{action_6.milestone_id}}",
                        "internal_docs": [
                            "Research Document: {{action_7.doc_url}}",
                            "Reactivation Strategy: {{action_8.strategy}}",
                            "Email Campaign 1: {{action_9.email_1}}",
                            "Email Campaign 2: {{action_9.email_2}}",
                            "Email Campaign 3: {{action_9.email_3}}",
                            "Expected Revenue: ${{expected_order_value}}",
                            "Success Probability: {{action_8.success_rate}}%"
                        ]
                    }
                },
                {
                    "id": "output_1",
                    "tool": "slack_post_message",
                    "parameters": {
                        "channel": "#sales",
                        "text": "🎯 Monthly Reactivation Campaign Ready!\n\n{{inactive_count}} high-value clients identified\nTotal potential revenue: ${{total_potential}}\n\nSynergy Session: {{action_4.session_url}}"
                    }
                }
            ]
        },
        "status": "draft",
        "is_scheduled": False
    }
    
    # Insert all workflows
    workflows = [workflow1, workflow2, workflow3, workflow4]
    
    for wf in workflows:
        try:
            cursor.execute("""
                INSERT INTO visual_automations 
                (automation_id, user_id, title, slug, description, category, 
                 ui_json, execution_json, status, is_scheduled)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                wf['automation_id'],
                wf['user_id'],
                wf['title'],
                wf['slug'],
                wf['description'],
                wf['category'],
                json.dumps(wf['ui_json']),
                json.dumps(wf['execution_json']),
                wf['status'],
                wf['is_scheduled']
            ))
            conn.commit()
            print(f"✅ Created: {wf['title']}")
            print(f"   ID: {wf['automation_id']}")
            print(f"   Shapes: {len(wf['ui_json']['shapes'])}")
            print(f"   Connections: {len(wf['ui_json']['connections'])}")
            print()
        except Exception as e:
            print(f"❌ Error creating {wf['title']}: {e}")
            conn.rollback()
    
    conn.close()
    print("\n🎉 All workflows created successfully!")

if __name__ == "__main__":
    create_workflows()

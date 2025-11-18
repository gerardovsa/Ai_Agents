"""
Create 4 Complete Sample Workflows for Visual Automation Canvas
================================================================
Creates robust, fully-formed workflows with proper shapes and connections
Inserts them into Supabase database
"""

import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:5001"

# Workflow 1: Email Processing Automation
workflow_1 = {
    "slug": "email-to-sheets-automation",
    "title": "Email to Sheets Automation",
    "description": "Automatically process incoming emails and log them to Google Sheets with categorization",
    "category": "operations",
    "status": "draft",
    "ui_json": {
        "shapes": [
            {
                "id": 1,
                "type": "trigger",
                "x": 100,
                "y": 100,
                "width": 220,
                "height": 90,
                "label": "New Email Received",
                "color": "#10B981",
                "description": "Trigger: Gmail inbox monitoring"
            },
            {
                "id": 2,
                "type": "tool",
                "x": 400,
                "y": 100,
                "width": 220,
                "height": 90,
                "label": "Parse Email Content",
                "color": "#6B7280",
                "description": "Extract sender, subject, body"
            },
            {
                "id": 3,
                "type": "tool",
                "x": 700,
                "y": 50,
                "width": 220,
                "height": 90,
                "label": "Categorize Email",
                "color": "#3B82F6",
                "description": "AI categorization (urgent/normal/spam)"
            },
            {
                "id": 4,
                "type": "database",
                "x": 1000,
                "y": 100,
                "width": 220,
                "height": 90,
                "label": "Log to Sheets",
                "color": "#EC4899",
                "description": "Append row to Google Sheets"
            },
            {
                "id": 5,
                "type": "tool",
                "x": 700,
                "y": 200,
                "width": 220,
                "height": 90,
                "label": "Send Notification",
                "color": "#F59E0B",
                "description": "Slack notification for urgent emails"
            },
            {
                "id": 6,
                "type": "end",
                "x": 1300,
                "y": 100,
                "width": 160,
                "height": 80,
                "label": "Complete",
                "color": "#EF4444",
                "description": "Workflow finished"
            }
        ],
        "connections": [
            {"id": 1, "from": 1, "to": 2, "label": "email data"},
            {"id": 2, "from": 2, "to": 3, "label": "parsed"},
            {"id": 3, "from": 3, "to": 4, "label": "categorized"},
            {"id": 4, "from": 3, "to": 5, "label": "if urgent"},
            {"id": 5, "from": 4, "to": 6, "label": "logged"},
            {"id": 6, "from": 5, "to": 6, "label": "notified"}
        ]
    }
}

# Workflow 2: Daily Report Generation
workflow_2 = {
    "slug": "daily-sales-report",
    "title": "Daily Sales Report Generator",
    "description": "Automatically compile sales data, generate charts, and email report to management team",
    "category": "sales",
    "status": "draft",
    "ui_json": {
        "shapes": [
            {
                "id": 1,
                "type": "schedule",
                "x": 100,
                "y": 100,
                "width": 220,
                "height": 90,
                "label": "Daily at 9 AM",
                "color": "#3B82F6",
                "description": "Cron: 0 9 * * *"
            },
            {
                "id": 2,
                "type": "database",
                "x": 400,
                "y": 100,
                "width": 220,
                "height": 90,
                "label": "Query Sales DB",
                "color": "#EC4899",
                "description": "Get yesterday's transactions"
            },
            {
                "id": 3,
                "type": "tool",
                "x": 700,
                "y": 100,
                "width": 220,
                "height": 90,
                "label": "Calculate Metrics",
                "color": "#6B7280",
                "description": "Total, average, top products"
            },
            {
                "id": 4,
                "type": "tool",
                "x": 1000,
                "y": 50,
                "width": 220,
                "height": 90,
                "label": "Generate Charts",
                "color": "#8B5CF6",
                "description": "Create bar/pie charts"
            },
            {
                "id": 5,
                "type": "tool",
                "x": 1000,
                "y": 180,
                "width": 220,
                "height": 90,
                "label": "Format Report",
                "color": "#10B981",
                "description": "HTML email template"
            },
            {
                "id": 6,
                "type": "tool",
                "x": 1300,
                "y": 100,
                "width": 220,
                "height": 90,
                "label": "Send Email",
                "color": "#F59E0B",
                "description": "To: management@company.com"
            },
            {
                "id": 7,
                "type": "database",
                "x": 1600,
                "y": 100,
                "width": 220,
                "height": 90,
                "label": "Archive Report",
                "color": "#EC4899",
                "description": "Save to Google Drive"
            },
            {
                "id": 8,
                "type": "end",
                "x": 1900,
                "y": 100,
                "width": 160,
                "height": 80,
                "label": "Complete",
                "color": "#EF4444",
                "description": "Report sent"
            }
        ],
        "connections": [
            {"id": 1, "from": 1, "to": 2, "label": "trigger"},
            {"id": 2, "from": 2, "to": 3, "label": "raw data"},
            {"id": 3, "from": 3, "to": 4, "label": "metrics"},
            {"id": 4, "from": 3, "to": 5, "label": "metrics"},
            {"id": 5, "from": 4, "to": 6, "label": "charts"},
            {"id": 6, "from": 5, "to": 6, "label": "template"},
            {"id": 7, "from": 6, "to": 7, "label": "sent"},
            {"id": 8, "from": 7, "to": 8, "label": "archived"}
        ]
    }
}

# Workflow 3: Customer Onboarding
workflow_3 = {
    "slug": "customer-onboarding-flow",
    "title": "New Customer Onboarding",
    "description": "Automated onboarding sequence with welcome email, account setup, and training materials",
    "category": "customer_service",
    "status": "draft",
    "ui_json": {
        "shapes": [
            {
                "id": 1,
                "type": "trigger",
                "x": 100,
                "y": 150,
                "width": 220,
                "height": 90,
                "label": "New Customer Signup",
                "color": "#10B981",
                "description": "Webhook from CRM"
            },
            {
                "id": 2,
                "type": "database",
                "x": 400,
                "y": 150,
                "width": 220,
                "height": 90,
                "label": "Create User Record",
                "color": "#EC4899",
                "description": "Add to customer database"
            },
            {
                "id": 3,
                "type": "tool",
                "x": 700,
                "y": 50,
                "width": 220,
                "height": 90,
                "label": "Send Welcome Email",
                "color": "#F59E0B",
                "description": "Personalized greeting"
            },
            {
                "id": 4,
                "type": "tool",
                "x": 700,
                "y": 170,
                "width": 220,
                "height": 90,
                "label": "Create Slack Channel",
                "color": "#3B82F6",
                "description": "Dedicated support channel"
            },
            {
                "id": 5,
                "type": "tool",
                "x": 700,
                "y": 290,
                "width": 220,
                "height": 90,
                "label": "Schedule Training",
                "color": "#8B5CF6",
                "description": "Calendar invite for onboarding call"
            },
            {
                "id": 6,
                "type": "wait",
                "x": 1000,
                "y": 150,
                "width": 220,
                "height": 90,
                "label": "Wait 24 Hours",
                "color": "#F59E0B",
                "description": "Delay before follow-up"
            },
            {
                "id": 7,
                "type": "tool",
                "x": 1300,
                "y": 150,
                "width": 220,
                "height": 90,
                "label": "Send Resources",
                "color": "#10B981",
                "description": "Documentation links, videos"
            },
            {
                "id": 8,
                "type": "database",
                "x": 1600,
                "y": 150,
                "width": 220,
                "height": 90,
                "label": "Update CRM Status",
                "color": "#EC4899",
                "description": "Mark as 'onboarding complete'"
            },
            {
                "id": 9,
                "type": "end",
                "x": 1900,
                "y": 150,
                "width": 160,
                "height": 80,
                "label": "Complete",
                "color": "#EF4444",
                "description": "Customer onboarded"
            }
        ],
        "connections": [
            {"id": 1, "from": 1, "to": 2, "label": "customer data"},
            {"id": 2, "from": 2, "to": 3, "label": "user created"},
            {"id": 3, "from": 2, "to": 4, "label": "user created"},
            {"id": 4, "from": 2, "to": 5, "label": "user created"},
            {"id": 5, "from": 3, "to": 6, "label": "email sent"},
            {"id": 6, "from": 4, "to": 6, "label": "channel created"},
            {"id": 7, "from": 5, "to": 6, "label": "training scheduled"},
            {"id": 8, "from": 6, "to": 7, "label": "24h elapsed"},
            {"id": 9, "from": 7, "to": 8, "label": "resources sent"},
            {"id": 10, "from": 8, "to": 9, "label": "status updated"}
        ]
    }
}

# Workflow 4: Invoice Processing
workflow_4 = {
    "slug": "invoice-approval-workflow",
    "title": "Invoice Approval & Payment",
    "description": "Automated invoice processing with approval routing and payment scheduling",
    "category": "finance",
    "status": "draft",
    "ui_json": {
        "shapes": [
            {
                "id": 1,
                "type": "trigger",
                "x": 100,
                "y": 200,
                "width": 220,
                "height": 90,
                "label": "Invoice Received",
                "color": "#10B981",
                "description": "Email attachment or upload"
            },
            {
                "id": 2,
                "type": "tool",
                "x": 400,
                "y": 200,
                "width": 220,
                "height": 90,
                "label": "Extract Data (OCR)",
                "color": "#6B7280",
                "description": "Parse invoice fields"
            },
            {
                "id": 3,
                "type": "database",
                "x": 700,
                "y": 200,
                "width": 220,
                "height": 90,
                "label": "Create Record",
                "color": "#EC4899",
                "description": "Add to accounting system"
            },
            {
                "id": 4,
                "type": "tool",
                "x": 1000,
                "y": 100,
                "width": 220,
                "height": 90,
                "label": "Check Amount",
                "color": "#3B82F6",
                "description": "If > $5000, require approval"
            },
            {
                "id": 5,
                "type": "tool",
                "x": 1300,
                "y": 50,
                "width": 220,
                "height": 90,
                "label": "Request Approval",
                "color": "#F59E0B",
                "description": "Email to finance manager"
            },
            {
                "id": 6,
                "type": "wait",
                "x": 1600,
                "y": 50,
                "width": 220,
                "height": 90,
                "label": "Wait for Approval",
                "color": "#F59E0B",
                "description": "Max 48 hours"
            },
            {
                "id": 7,
                "type": "tool",
                "x": 1300,
                "y": 200,
                "width": 220,
                "height": 90,
                "label": "Auto-Approve",
                "color": "#10B981",
                "description": "Amount < $5000"
            },
            {
                "id": 8,
                "type": "tool",
                "x": 1900,
                "y": 100,
                "width": 220,
                "height": 90,
                "label": "Schedule Payment",
                "color": "#8B5CF6",
                "description": "Add to payment batch"
            },
            {
                "id": 9,
                "type": "database",
                "x": 2200,
                "y": 100,
                "width": 220,
                "height": 90,
                "label": "Update Status",
                "color": "#EC4899",
                "description": "Mark as 'scheduled'"
            },
            {
                "id": 10,
                "type": "tool",
                "x": 1000,
                "y": 320,
                "width": 220,
                "height": 90,
                "label": "Send Rejection",
                "color": "#EF4444",
                "description": "Notify vendor of issue"
            },
            {
                "id": 11,
                "type": "end",
                "x": 2500,
                "y": 100,
                "width": 160,
                "height": 80,
                "label": "Complete",
                "color": "#EF4444",
                "description": "Invoice processed"
            },
            {
                "id": 12,
                "type": "end",
                "x": 1300,
                "y": 320,
                "width": 160,
                "height": 80,
                "label": "Rejected",
                "color": "#EF4444",
                "description": "Invoice rejected"
            }
        ],
        "connections": [
            {"id": 1, "from": 1, "to": 2, "label": "invoice file"},
            {"id": 2, "from": 2, "to": 3, "label": "extracted data"},
            {"id": 3, "from": 3, "to": 4, "label": "record created"},
            {"id": 4, "from": 4, "to": 5, "label": "if > $5000"},
            {"id": 5, "from": 4, "to": 7, "label": "if < $5000"},
            {"id": 6, "from": 5, "to": 6, "label": "approval requested"},
            {"id": 7, "from": 6, "to": 8, "label": "if approved"},
            {"id": 8, "from": 6, "to": 10, "label": "if rejected"},
            {"id": 9, "from": 7, "to": 8, "label": "auto-approved"},
            {"id": 10, "from": 8, "to": 9, "label": "payment scheduled"},
            {"id": 11, "from": 9, "to": 11, "label": "status updated"},
            {"id": 12, "from": 10, "to": 12, "label": "rejection sent"}
        ]
    }
}

def create_workflow(workflow_data):
    """Create workflow via API"""
    try:
        print(f"\nCreating workflow: {workflow_data['title']}")
        print(f"  Slug: {workflow_data['slug']}")
        print(f"  Category: {workflow_data['category']}")
        print(f"  Shapes: {len(workflow_data['ui_json']['shapes'])}")
        print(f"  Connections: {len(workflow_data['ui_json']['connections'])}")
        
        response = requests.post(
            f"{API_BASE_URL}/api/automation/save",
            json=workflow_data,
            headers={
                'Content-Type': 'application/json',
                'X-User-ID': '1'  # Default user
            }
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"  Result: SUCCESS (HTTP {response.status_code})")
            print(f"  ID: {result.get('automation_id', 'N/A')}")
            return True
        else:
            print(f"  Result: FAILED - {response.status_code}")
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"  Result: ERROR - {str(e)}")
        return False

def main():
    """Create all sample workflows"""
    print("=" * 80)
    print("CREATING 4 SAMPLE WORKFLOWS FOR VISUAL AUTOMATION CANVAS")
    print("=" * 80)
    
    workflows = [workflow_1, workflow_2, workflow_3, workflow_4]
    success_count = 0
    
    for workflow in workflows:
        if create_workflow(workflow):
            success_count += 1
    
    print("\n" + "=" * 80)
    print(f"COMPLETE: {success_count}/{len(workflows)} workflows created successfully")
    print("=" * 80)
    
    if success_count == len(workflows):
        print("\nAll workflows ready! Open Visual Automation Canvas and click 'Load' to see them.")
        print("\nWorkflows created:")
        print("  1. Email to Sheets Automation (6 shapes, 6 connections)")
        print("  2. Daily Sales Report Generator (8 shapes, 8 connections)")
        print("  3. New Customer Onboarding (9 shapes, 10 connections)")
        print("  4. Invoice Approval & Payment (12 shapes, 12 connections)")
    else:
        print(f"\nWarning: Only {success_count} workflows created. Check errors above.")

if __name__ == "__main__":
    main()

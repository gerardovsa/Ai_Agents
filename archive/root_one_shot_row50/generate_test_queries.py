"""
Generate 200 Test Queries Based on Available Platforms

Analyzes the tool registry and generates realistic user queries for each platform
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))
sys.path.insert(0, os.path.dirname(__file__))

from tools.registry_v3 import RegistryV3

print("\n" + "="*100)
print(" "*30 + "GENERATING 200 TEST QUERIES")
print("="*100)

# Load registry
registry = RegistryV3()

# Analyze platforms
platforms = {}
for tool_name, tool_data in registry.tools.items():
    platform = tool_data.get('platform', 'unknown')
    if platform not in platforms:
        platforms[platform] = []
    platforms[platform].append(tool_name)

print(f"\nFound {len(platforms)} platforms with {len(registry.tools)} total tools")
print(f"\nPlatforms: {sorted(platforms.keys())}")

# Generate queries for each platform
queries = []

# Gmail queries (46 tools)
gmail_queries = [
    "check my emails",
    "send an email to john@example.com",
    "search for emails from sarah",
    "mark all unread emails as read",
    "create a draft email",
    "archive old emails",
    "delete spam emails",
    "get my inbox messages",
    "reply to the last email",
    "forward this email to the team",
    "create email filter for newsletters",
    "organize my inbox",
    "check for important emails",
    "find emails with attachments",
    "bulk delete promotional emails",
]

# Google Docs queries
google_docs_queries = [
    "create a new document",
    "write a report about Q4 sales",
    "edit my document",
    "share document with team",
    "export document as PDF",
    "add comments to document",
    "format my document with headers",
    "insert table in document",
    "create meeting notes document",
    "write a proposal",
]

# Google Sheets queries
google_sheets_queries = [
    "create a spreadsheet",
    "add data to my spreadsheet",
    "calculate sum of column A",
    "create a budget spreadsheet",
    "import CSV data",
    "format cells in spreadsheet",
    "create pivot table",
    "share spreadsheet with finance team",
    "export spreadsheet to Excel",
    "analyze sales data in sheets",
]

# Google Drive queries
google_drive_queries = [
    "upload a file to drive",
    "search for files in drive",
    "share folder with team",
    "create new folder",
    "download file from drive",
    "organize my drive files",
    "find recent documents",
    "backup my files",
    "move file to folder",
    "delete old files",
]

# Google Calendar queries
google_calendar_queries = [
    "schedule a meeting",
    "create calendar event",
    "check my calendar for tomorrow",
    "find available meeting times",
    "book appointment for next week",
    "set up recurring meeting",
    "add reminder to event",
    "cancel tomorrow's meeting",
    "update meeting time",
    "view this week's schedule",
]

# Google Meet queries
google_meet_queries = [
    "create instant meeting",
    "schedule video call",
    "start team meeting",
    "generate meeting link",
    "set up daily standup",
    "create interview meeting",
    "schedule recurring team sync",
    "get meeting join info",
    "cancel video meeting",
    "update meeting agenda",
]

# Microsoft Outlook queries
microsoft_outlook_queries = [
    "check my outlook inbox",
    "send outlook email",
    "search outlook messages",
    "create outlook folder",
    "flag important emails",
    "schedule outlook meeting",
    "check outlook calendar",
    "create email rule",
    "forward outlook message",
    "mark emails as read",
]

# Microsoft Word queries
microsoft_word_queries = [
    "create word document",
    "edit word file",
    "format document in word",
    "add table to word doc",
    "insert image in document",
    "create letter template",
    "export word to PDF",
    "share word document",
    "review document changes",
    "create report in word",
]

# Microsoft Excel queries
microsoft_excel_queries = [
    "create excel spreadsheet",
    "add formula to excel",
    "create excel chart",
    "filter excel data",
    "sort excel table",
    "import data to excel",
    "create excel template",
    "format excel cells",
    "analyze data in excel",
    "export excel to CSV",
]

# Microsoft Teams queries
microsoft_teams_queries = [
    "send teams message",
    "create teams channel",
    "schedule teams meeting",
    "upload file to teams",
    "search teams chat",
    "start teams call",
    "create teams group",
    "post announcement in teams",
    "share screen in teams",
    "record teams meeting",
]

# Microsoft OneDrive queries
microsoft_onedrive_queries = [
    "upload to onedrive",
    "share onedrive file",
    "create onedrive folder",
    "download from onedrive",
    "sync files to onedrive",
    "search onedrive files",
    "backup to onedrive",
    "organize onedrive folders",
    "restore deleted file",
    "get onedrive link",
]

# Slack queries
slack_queries = [
    "send slack message",
    "create slack channel",
    "post in slack",
    "search slack messages",
    "upload file to slack",
    "set slack status",
    "create slack poll",
    "pin slack message",
    "react to slack message",
    "start slack thread",
]

# Stripe queries
stripe_queries = [
    "create customer in stripe",
    "process payment",
    "create invoice",
    "refund transaction",
    "list stripe customers",
    "create subscription",
    "update payment method",
    "generate payment link",
    "check payment status",
    "create product in stripe",
]

# Automation queries
automation_queries = [
    "create automation workflow",
    "schedule automated task",
    "set up email automation",
    "create recurring workflow",
    "automate data sync",
    "schedule report generation",
    "create backup automation",
    "automate file uploads",
    "set up notification workflow",
    "create approval workflow",
]

# AI/Analysis queries
ai_queries = [
    "summarize this document",
    "analyze sales data",
    "generate report summary",
    "extract key points from text",
    "translate document",
    "check document for errors",
    "compare two documents",
    "create data visualization",
    "analyze trends",
    "generate insights from data",
]

# Task management queries
task_queries = [
    "create task",
    "list my tasks",
    "mark task complete",
    "set task deadline",
    "assign task to team member",
    "prioritize tasks",
    "create project plan",
    "track task progress",
    "add task reminder",
    "update task status",
]

# Cross-platform general queries
general_queries = [
    "help me organize my work",
    "what can you do",
    "show me my schedule",
    "send message to my team",
    "create document for meeting",
    "find file about project",
    "share latest report",
    "backup my important files",
    "check for updates",
    "collaborate with team",
    "manage my calendar",
    "track expenses",
    "create invoice for client",
    "schedule appointment",
    "write email to customer",
    "analyze quarterly results",
    "create presentation slides",
    "upload contract document",
    "search for customer info",
    "generate monthly report",
]

# Combine all queries
all_queries = (
    gmail_queries + google_docs_queries + google_sheets_queries + 
    google_drive_queries + google_calendar_queries + google_meet_queries +
    microsoft_outlook_queries + microsoft_word_queries + microsoft_excel_queries +
    microsoft_teams_queries + microsoft_onedrive_queries + slack_queries +
    stripe_queries + automation_queries + ai_queries + task_queries + general_queries
)

print(f"\nGenerated {len(all_queries)} queries")

# Save to JSON file
output_file = 'test_queries_200.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'total_queries': len(all_queries),
        'platforms': list(platforms.keys()),
        'queries': all_queries
    }, f, indent=2, ensure_ascii=False)

print(f"\n✓ Saved queries to {output_file}")

# Display query breakdown
print("\n" + "="*100)
print(" "*35 + "QUERY BREAKDOWN")
print("="*100)

breakdown = {
    'Gmail': len(gmail_queries),
    'Google Docs': len(google_docs_queries),
    'Google Sheets': len(google_sheets_queries),
    'Google Drive': len(google_drive_queries),
    'Google Calendar': len(google_calendar_queries),
    'Google Meet': len(google_meet_queries),
    'Microsoft Outlook': len(microsoft_outlook_queries),
    'Microsoft Word': len(microsoft_word_queries),
    'Microsoft Excel': len(microsoft_excel_queries),
    'Microsoft Teams': len(microsoft_teams_queries),
    'Microsoft OneDrive': len(microsoft_onedrive_queries),
    'Slack': len(slack_queries),
    'Stripe': len(stripe_queries),
    'Automation': len(automation_queries),
    'AI/Analysis': len(ai_queries),
    'Task Management': len(task_queries),
    'General': len(general_queries),
}

for category, count in sorted(breakdown.items(), key=lambda x: -x[1]):
    print(f"{category:.<40} {count:>3} queries")

print(f"\n{'TOTAL':.<40} {sum(breakdown.values()):>3} queries")

print("\n" + "="*100)
print(" "*40 + "COMPLETE")
print("="*100 + "\n")

"""
Add Email AI Synergy Session Planner prompts to database
from shared.database_utils import convert_sql_placeholders

Creates comprehensive set of prompts for email coordination,
accounts payable, customer support, and team management.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# Database path
root_dir = Path(__file__).parent.parent.parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print("="*80)
print("EMAIL AI SYNERGY SESSION PLANNER - PROMPT LIBRARY SETUP")
print("="*80)

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Timestamp for created_at/updated_at
now = datetime.now().isoformat()

# Define prompts
prompts = [
    # ==================== FULL PROMPTS ====================
    
    {
        'name': 'Email AI Synergy Session Planner',
        'category': 'workflow_automation',
        'type': 'full_prompt',
        'description': 'Master coordinator that transforms emails into actionable Synergy session cards with complete AI agent plans',
        'prompt_text': open(root_dir / 'AI_infrastructure' / 'prompts' / 'email_synergy_coordinator.md', 'r', encoding='utf-8').read(),
        'tags': 'email,synergy,coordinator,automation,workflow,ai_agents',
        'visibility': 'public',
        'source_file': 'AI_infrastructure/prompts/email_synergy_coordinator.md'
    },
    
    {
        'name': 'Accounts Payable Specialist',
        'category': 'finance',
        'type': 'full_prompt',
        'description': 'Expert in processing invoices, verifying against POs, and managing payment workflows',
        'prompt_text': '''You are an Accounts Payable specialist managing invoice processing and payments:

**INVOICE VERIFICATION WORKFLOW:**
1. Extract invoice details: Number, amount, date, supplier, line items
2. Query database for matching PO:
   ```sql
   SELECT po_number, supplier, line_items, total, status
   FROM purchase_orders
   WHERE supplier = ? AND date >= DATE_SUB(NOW(), INTERVAL 90 DAY)
   ORDER BY date DESC
   ```
3. Match invoice to PO: Verify quantities, pricing, terms
4. Check authorization: Amounts >$1000 need manager approval
5. Schedule payment: Enter payment date based on terms
6. Record transaction: Update accounting system

**TOOLS TO USE:**
- execute_sql_query: Query POs and suppliers
- google_sheets_update: Update AP tracking sheet
- stripe_create_payment: Process payments via Stripe
- gmail_send_email: Send remittance advice
- synergy_update_session: Update payment status

**VERIFICATION CHECKLIST:**
☐ Invoice matches PO number
☐ Line items match PO items
☐ Pricing is correct
☐ Quantities verified
☐ Delivery confirmed
☐ Authorization obtained
☐ Payment scheduled
☐ System updated

**SQL QUERIES:**
```sql
-- Find matching PO
SELECT * FROM purchase_orders WHERE supplier = ? AND status = 'approved'

-- Check supplier history
SELECT supplier, AVG(payment_days) as avg_days
FROM invoices 
WHERE supplier = ? 
GROUP BY supplier

-- Update invoice record
INSERT INTO invoices (invoice_num, supplier, amount, due_date, status)
VALUES (?, ?, ?, ?, 'pending')
```

**PAYMENT TERMS:**
- Net 30: Pay within 30 days
- Net 15: Pay within 15 days
- Due on Receipt: Pay immediately
- 2/10 Net 30: 2% discount if paid in 10 days

**ESCALATION:**
- Discrepancies: Report to procurement
- Over $5000: Require director approval
- Overdue: Send reminder to supplier
- Disputes: Create support ticket

**OUTPUT FORMAT:**
✅ Verified: Invoice #[XXX] matches PO #[YYY]
💰 Amount: $[XXX.XX] (incl. GST)
📅 Due: [Date] ([X] days)
✔️ Authorized by: [Name]
⏰ Payment scheduled: [Date]
''',
        'tags': 'accounts_payable,invoice,payment,finance,verification,sql',
        'visibility': 'public',
        'source_file': 'Generated from email_synergy_coordinator.md'
    },
    
    {
        'name': 'Customer Support Specialist',
        'category': 'customer_service',
        'type': 'full_prompt',
        'description': 'Expert in handling customer issues, investigating orders, and coordinating resolutions',
        'prompt_text': '''You are a Customer Support specialist handling issues and coordinating resolutions:

**ISSUE RESOLUTION WORKFLOW:**
1. Extract issue details: Order number, problem description, customer info
2. Investigate order:
   ```sql
   SELECT o.*, c.name, c.email, c.history
   FROM orders o
   JOIN customers c ON o.customer_id = c.id
   WHERE o.order_number = ?
   ```
3. Identify root cause: Check production notes, proofs, specifications
4. Determine resolution: Reprint, refund, discount, or explanation
5. Calculate costs: Use quote calculator for reprints
6. Communicate with customer: Professional, empathetic, solution-focused
7. Track resolution: Update Synergy card with progress

**TOOLS TO USE:**
- execute_sql_query: Query order details and history
- inhouse_calculate_quote: Calculate reprint costs
- gmail_send_email: Customer communication
- synergy_update_session: Track resolution progress
- google_docs_create: Create incident report

**ISSUE CATEGORIES:**

**Quality Issues:**
- Wrong finish (gloss vs matt)
- Wrong size/quantity
- Poor print quality
- Damage in shipping
→ Action: Arrange reprint + pickup

**Delivery Issues:**
- Late delivery
- Wrong address
- Missing items
→ Action: Rush replacement + tracking

**Specification Errors:**
- Customer changed mind
- Proof not reviewed
- Communication breakdown
→ Action: Explain politely, offer discount

**SQL QUERIES:**
```sql
-- Get order details
SELECT o.*, oi.product, oi.specs, oi.quantity
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
WHERE o.order_number = ?

-- Check customer history
SELECT COUNT(*) as total_orders, 
       SUM(total) as lifetime_value,
       COUNT(CASE WHEN status = 'issue' THEN 1 END) as issues
FROM orders
WHERE customer_id = ?

-- Log support ticket
INSERT INTO support_tickets 
(order_id, issue_type, description, priority, status)
VALUES (?, ?, ?, ?, 'open')
```

**COMMUNICATION TEMPLATES:**

**Apology Email:**
```
Subject: We apologize - Order #[XXX] Issue Resolution

Dear [Name],

We sincerely apologize for the issue with your order #[XXX]. 

Issue: [Description]
Resolution: [Action being taken]
Timeline: [When resolved]
Compensation: [Discount/credit offered]

We value your business and will ensure this is resolved promptly.

Best regards,
[Your name]
```

**Resolution Confirmation:**
```
Subject: Resolved - Order #[XXX]

Dear [Name],

Great news! Your issue has been resolved:

✅ [Resolution action completed]
📦 Tracking: [Number]
🎁 Special discount: [XX]% off next order

Thank you for your patience.

Best regards,
[Your name]
```

**ESCALATION RULES:**
- Order value >$1000: Notify manager
- Customer VIP/high-volume: Priority handling
- Repeated issues: Flag quality control
- Unable to resolve: Escalate to director

**METRICS TO TRACK:**
- Resolution time (target: <24 hours)
- Customer satisfaction (CSAT score)
- Reprint costs (minimize)
- Issue recurrence rate
''',
        'tags': 'support,customer_service,issues,resolution,communication,sql',
        'visibility': 'public',
        'source_file': 'Generated from email_synergy_coordinator.md'
    },
    
    {
        'name': 'Team Coordination Specialist',
        'category': 'project_management',
        'type': 'full_prompt',
        'description': 'Expert in coordinating multi-person projects, delegating tasks, and tracking progress',
        'prompt_text': '''You are a Team Coordination specialist managing multi-person projects:

**PROJECT COORDINATION WORKFLOW:**
1. Break down request into deliverables
2. Identify required specialists (Quote AI, Design AI, Email AI, etc.)
3. Create Synergy card with clear task breakdown
4. Assign tasks to AI agents with dependencies
5. Set up communication channels (Teams, Slack)
6. Monitor progress and update stakeholders
7. Handle blockers and escalations

**TOOLS TO USE:**
- synergy_smart_project_tracker: Create coordinated project
- microsoft_teams_create_channel: Set up team communication
- google_docs_create: Create project documentation
- google_calendar_create_event: Schedule milestones
- execute_sql_query: Track resource allocation

**PROJECT TYPES:**

**Marketing Campaigns:**
Components: Print materials + digital + social + web
Specialists: Quote AI, Design AI, Email AI, Web AI
Timeline: 2-4 weeks
Checklist:
  ☐ Print Materials (Quote AI)
  ☐ Email Campaign (Email AI)
  ☐ Social Graphics (Design AI)
  ☐ Landing Page (Web AI)

**Client Onboarding:**
Components: Welcome kit + training + setup + documentation
Specialists: Document AI, Email AI, Support AI
Timeline: 1 week
Checklist:
  ☐ Welcome email (Email AI)
  ☐ Account setup (Support AI)
  ☐ Training materials (Document AI)
  ☐ Follow-up call (Calendar AI)

**Product Launches:**
Components: Materials + marketing + sales + support
Specialists: Quote AI, Design AI, Email AI, Support AI
Timeline: 4-8 weeks
Checklist:
  ☐ Product pricing (Quote AI)
  ☐ Marketing materials (Design AI)
  ☐ Launch campaign (Email AI)
  ☐ Support documentation (Document AI)

**DEPENDENCY MANAGEMENT:**
```javascript
// Define task dependencies
{
  tasks: [
    { id: 1, name: "Calculate quote", agent: "Quote AI", dependencies: [] },
    { id: 2, name: "Design layout", agent: "Design AI", dependencies: [1] },
    { id: 3, name: "Create proposal", agent: "Document AI", dependencies: [1,2] },
    { id: 4, name: "Send to client", agent: "Email AI", dependencies: [3] }
  ]
}
```

**SYNERGY CARD STRUCTURE:**
```json
{
  "title": "Marketing Campaign - Multi-Channel",
  "platforms_involved": ["print", "email", "web", "design"],
  "team_members": ["Quote AI", "Design AI", "Email AI", "Web AI"],
  "milestones": [
    { "name": "Print quote", "date": "Nov 15", "responsible": "Quote AI" },
    { "name": "Designs ready", "date": "Nov 18", "responsible": "Design AI" },
    { "name": "Campaign live", "date": "Nov 22", "responsible": "Email AI" }
  ],
  "communication": {
    "teams_channel": "marketing-campaign-nov",
    "slack_channel": "#project-abc",
    "meeting_schedule": "Daily standup 9am"
  }
}
```

**TEAM COMMUNICATION:**
```
Daily Update Template:
📊 Project: [Name]
✅ Completed: [Tasks]
🔄 In Progress: [Tasks]
⚠️ Blocked: [Issues]
📅 Next: [Upcoming tasks]
👥 Needs: [Resources/help]
```

**SQL QUERIES:**
```sql
-- Track team workload
SELECT ai_agent, COUNT(*) as active_tasks
FROM synergy_sessions
WHERE status IN ('in_progress', 'backlog')
GROUP BY ai_agent

-- Project timeline
SELECT project, MIN(start_date) as start, MAX(due_date) as end
FROM synergy_sessions
WHERE project_id = ?
GROUP BY project

-- Resource allocation
SELECT ai_agent, SUM(estimated_hours) as total_hours
FROM synergy_sessions
WHERE status = 'in_progress'
GROUP BY ai_agent
```

**ESCALATION MATRIX:**
- Behind schedule: Notify project owner
- Resource conflict: Reprioritize tasks
- Blocker >24hrs: Escalate to manager
- Client request change: Update project scope
''',
        'tags': 'coordination,project_management,team,synergy,workflow,delegation',
        'visibility': 'public',
        'source_file': 'Generated from email_synergy_coordinator.md'
    },
    
    # ==================== QUICK ACTIONS ====================
    
    {
        'name': 'Process Today\'s Emails',
        'category': 'workflow_automation',
        'type': 'quick_action',
        'description': 'Scan inbox, categorize emails, and create Synergy cards for each actionable item',
        'prompt_text': '''Process unread emails from last 24 hours:

1. Scan inbox:
   gmail_list_messages(query="is:unread after:yesterday")
   OR
   microsoft_outlook_list_messages(filter="isRead eq false")

2. For each email:
   - Extract: sender, subject, body, category
   - Categorize: client_request, invoice, support, internal
   - Priority: critical/high/medium/low based on keywords

3. Create Synergy cards:
   synergy_smart_project_tracker(
     title="[Category] - [Client] - [Topic]",
     platforms_involved=[detected platforms],
     next_steps=[extracted action items],
     priority=calculated
   )

4. Create documents:
   google_docs_create for each email thread

5. Report summary:
   "Processed [X] emails, created [Y] Synergy cards"
''',
        'tags': 'email,automation,inbox,synergy,quick',
        'visibility': 'public',
        'source_file': 'Generated from email_synergy_coordinator.md'
    },
    
    {
        'name': 'Quick Invoice Processing',
        'category': 'finance',
        'type': 'quick_action',
        'description': 'Verify invoice against PO and schedule payment',
        'prompt_text': '''Process invoice quickly:

1. Extract invoice data from email attachment
2. Query database:
   execute_sql_query("SELECT * FROM purchase_orders WHERE supplier = ?")
3. Verify: Match invoice to PO
4. If verified:
   - Create Synergy card: "AP: Invoice #[XXX]"
   - Schedule payment
   - Update status
5. If discrepancy:
   - Flag for manual review
   - Email procurement team
''',
        'tags': 'invoice,accounts_payable,quick,finance',
        'visibility': 'public',
        'source_file': 'Generated from email_synergy_coordinator.md'
    },
    
    {
        'name': 'Quick Support Response',
        'category': 'customer_service',
        'type': 'quick_action',
        'description': 'Quickly respond to customer support emails with investigation and resolution plan',
        'prompt_text': '''Handle support issue:

1. Get order details:
   execute_sql_query("SELECT * FROM orders WHERE order_number = ?")
2. Assess issue severity
3. Create Synergy card: "Support: Order #[XXX]"
4. If critical:
   - Calculate reprint cost
   - Draft apology email
   - Set priority: HIGH
5. Respond to customer within 1 hour
''',
        'tags': 'support,customer_service,quick,email',
        'visibility': 'public',
        'source_file': 'Generated from email_synergy_coordinator.md'
    },
    
    {
        'name': 'Create Email Action Document',
        'category': 'documentation',
        'type': 'quick_action',
        'description': 'Create comprehensive document from email with summary, thread, and action plan',
        'prompt_text': '''Create action document:

1. Get full email thread:
   gmail_get_message(message_id) or microsoft_outlook_get_message
2. Create document:
   google_docs_create(
     title="[Category] - [Client] - [Topic]",
     content=template with:
       - Executive Summary
       - Full Email Thread
       - Requirements Breakdown
       - Action Plan
       - AI Agent Instructions
   )
3. Store in Drive:
   google_drive_move_file to "Email Actions/[Year]/[Month]"
4. Return document URL
''',
        'tags': 'documentation,email,google_docs,quick',
        'visibility': 'public',
        'source_file': 'Generated from email_synergy_coordinator.md'
    },
    
    {
        'name': 'Check Approaching Deadlines',
        'category': 'monitoring',
        'type': 'quick_action',
        'description': 'Check Synergy cards with deadlines in next 2 days and send alerts',
        'prompt_text': '''Check deadlines:

1. Query Synergy:
   synergy_list_sessions(filter="due_date < DATE_ADD(NOW(), INTERVAL 2 DAY)")
2. For each urgent item:
   - Send alert email to team
   - Update priority to CRITICAL
   - Add note: "Due in [X] days"
3. Generate summary report:
   "[X] items due soon - action required"
''',
        'tags': 'monitoring,deadlines,alerts,quick',
        'visibility': 'public',
        'source_file': 'Generated from email_synergy_coordinator.md'
    }
]

# Insert prompts into database
print(f"\nInserting {len(prompts)} prompts into database...")
print("="*80)

inserted_count = 0
for prompt in prompts:
    try:
        sql, params = convert_sql_placeholders('''
            INSERT INTO prompt_library 
            (user_id, name, category, type, description, prompt_text, tags, visibility, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            1,  # user_id
            prompt['name'],
            prompt['category'],
            prompt['type'],
            prompt['description'],
            prompt['prompt_text'],
            prompt['tags'],
            prompt['visibility'],
            now,
            now
        ))

        cursor.execute(sql, params)
        inserted_count += 1
        print(f"✅ Added: {prompt['name']} ({prompt['type']})")
    except Exception as e:
        print(f"❌ Error adding {prompt['name']}: {e}")

conn.commit()

# Verify insertion
cursor.execute('''
    SELECT category, type, COUNT(*) as count
    FROM prompt_library
    WHERE user_id = 1
    GROUP BY category, type
    ORDER BY category, type
''')

print("\n" + "="*80)
print("DATABASE SUMMARY")
print("="*80)
results = cursor.fetchall()
for row in results:
    print(f"{row[0]:30} | {row[1]:15} | {row[2]:3} prompts")

# Get total count for user 1
cursor.execute('SELECT COUNT(*) FROM prompt_library WHERE user_id = 1')
total = cursor.fetchone()[0]

print("="*80)
print(f"✅ SUCCESS: Added {inserted_count} new prompts")
print(f"📊 Total prompts for user_id=1: {total}")
print("="*80)

conn.close()

print("\n🎉 Email AI Synergy Session Planner prompts installed!")
print("\nThese prompts are now available in your prompt library:")
print("  - Email AI Synergy Session Planner (FULL)")
print("  - Accounts Payable Specialist (FULL)")
print("  - Customer Support Specialist (FULL)")
print("  - Team Coordination Specialist (FULL)")
print("  - Process Today's Emails (QUICK)")
print("  - Quick Invoice Processing (QUICK)")
print("  - Quick Support Response (QUICK)")
print("  - Create Email Action Document (QUICK)")
print("  - Check Approaching Deadlines (QUICK)")
print("\nAccess via: http://localhost:5001/ui → Click ⚡ Prompt Library button")

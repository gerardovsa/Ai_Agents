"""
Add InHouse Print Business-Specific Prompts to Database
from shared.database_utils import convert_sql_placeholders

This script adds comprehensive prompts focused on:
- Daily email coordination with explicit db_get_available_queries() workflow
- Business operations with two-step database access pattern
- All prompts clearly state: Step 1 = discover queries, Step 2 = execute

Created: November 15, 2025
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def get_db_connection():
    """Get database connection"""
    db_path = project_root / 'data' / 'ai_infrastructure.db'
    print(f'Using database: {db_path}')
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def add_prompt(conn, user_id, name, category, prompt_type, description, prompt_text, tags, source):
    """Add a prompt to the database"""
    cursor = conn.cursor()
    
    # Check if prompt already exists
    sql, params = convert_sql_placeholders("SELECT id FROM prompt_library WHERE name = ? AND user_id = ?", (name, user_id))

    cursor.execute(sql, params)
    existing = cursor.fetchone()
    
    if existing:
        print(f"Skipped: '{name}' (already exists)")
        return False
    
    # Insert new prompt
    sql, params = convert_sql_placeholders("""
        INSERT INTO prompt_library 
        (user_id, name, category, type, description, prompt_text, tags, visibility, usage_count, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, name, category, prompt_type, description, prompt_text, 
        tags, 'public', 0,
        datetime.now().isoformat(), datetime.now().isoformat()
    ))
    
    print(f"Added: '{name}' ({prompt_type})")
    return True

def main():
    conn = get_db_connection()
    user_id = 1
    source = "InHouse Print Business Operations v1.0"
    added_count = 0
    
    print("\n" + "="*60)
    print("ADDING INHOUSE PRINT BUSINESS-SPECIFIC PROMPTS")
    print("="*60 + "\n")
    
    # Read the master prompt file we created earlier
    master_prompt_path = project_root / 'AI_infrastructure' / 'prompts' / 'email_synergy_coordinator.md'
    
    if master_prompt_path.exists():
        with open(master_prompt_path, 'r', encoding='utf-8') as f:
            email_coordinator_prompt = f.read()
        
        # Update it to include explicit database workflow
        email_coordinator_prompt = """You are the **Daily Email Coordinator AI** - master orchestrator for InHouse Print.

**CRITICAL: DATABASE ACCESS PATTERN**

The InHouse database uses QueryLibrary with 100+ pre-built queries. You MUST follow this two-step process:

**STEP 1: DISCOVER AVAILABLE QUERIES**
```python
# ALWAYS call this first to see what queries are available
queries = db_get_available_queries()

# Or filter by category
client_queries = db_get_available_queries(category="Client Analysis")
sales_queries = db_get_available_queries(category="Sales & Revenue")
stock_queries = db_get_available_queries(category="Stock Management")
```

**STEP 2: EXECUTE SPECIFIC QUERY**
```python
# Use the query name you discovered in Step 1
result = db_execute_query(
    query_name="client_order_history",
    params={"client_email": "john@example.com"}
)
```

**THERE IS NO DIRECT SQL EXECUTION** - All queries are pre-built and optimized.

**YOUR MISSION:**
Process today's emails, create Synergy session with prioritized checklists, assign AI agents, generate documents.

**WORKFLOW:**

1. **Scan emails:** Use gmail_search_messages(query="after:today")
2. **Categorize:** Quote/Order/Invoice/Support/Vendor/Internal
3. **Create Synergy:** synergy_create_session(name="Daily Operations - {date}")
4. **Verify clients:** db_get_available_queries() then db_execute_query(query_name="client_lookup")
5. **Assign AI agents:** Quote/Support/Invoice/Document AI with detailed instructions
6. **Generate documents:** google_docs_create() for each email
7. **Log activity:** synergy_update_session() with comprehensive notes
8. **Report to user:** Clear summary with top priorities and agent status

**TOOLS:**
- Email: gmail_search_messages, gmail_get_message
- Database Discovery: db_get_available_queries(category="...")
- Database Queries: db_execute_query(query_name="...", params={...})
- Synergy: synergy_create_session, synergy_add_checklist, synergy_update_session
- Documents: google_docs_create
- Financial: xero_get_invoices, xero_get_contacts

**AI AGENT INSTRUCTIONS:**

**Quote AI:** Extract specs, use db_calculate_quote(), check similar orders, present itemized quote
**Support AI:** Find order with db_execute_query(), investigate issue, calculate resolution, draft apology
**Invoice AI:** Match invoice in Xero, check payment history, provide clear instructions
**Document AI:** Create structured summary in Google Docs for every email

**SUCCESS CRITERIA:**
- All emails categorized and prioritized
- Synergy session with complete checklists
- AI agents assigned with instructions
- Documents generated for each email
- User report with actionable items
- Database queries use two-step pattern
"""
    else:
        email_coordinator_prompt = """[Email Coordinator Prompt - See email_synergy_coordinator.md for full version]

**CRITICAL DATABASE WORKFLOW:**
1. db_get_available_queries() - Discover what's available
2. db_execute_query(query_name, params) - Execute specific query

Use this pattern for ALL database access."""
    
    if add_prompt(conn, user_id, 
                 "Daily Email Coordinator - Morning Briefing", 
                 "workflow_automation", 
                 "full_prompt",
                 "Master coordinator for InHouse Print emails. Creates Synergy session, assigns AI agents. Uses db_get_available_queries() then db_execute_query() for database access.",
                 email_coordinator_prompt,
                 "email,synergy,coordination,database,printing",
                 source):
        added_count += 1
    
    # Check-In Prompt
    checkin_prompt = """You are the **Daily Email Coordinator - Check-In Mode**.

**CRITICAL: DATABASE ACCESS PATTERN**
1. db_get_available_queries() - See what queries exist
2. db_execute_query(query_name, params) - Execute the query

**YOUR MISSION:**
Review AI progress, process new emails, update Synergy, report status.

**WORKFLOW:**

1. **Get session:** synergy_get_session(session_name_contains="Daily Operations")
2. **Review progress:** Check completed/in-progress/blocked items
3. **Scan new emails:** gmail_search_messages(query=f"after:{morning_time}")
4. **Process new emails:** Categorize, verify clients (db_get_available_queries then db_execute_query)
5. **Update Synergy:** synergy_add_checklist() for new items
6. **Check alignment:** Priorities, deadlines, blockers
7. **Log activity:** synergy_update_session() with progress notes
8. **Report status:** Clear update with wins, blockers, metrics

**TOOLS:**
- Synergy: synergy_get_session, synergy_add_checklist, synergy_update_session
- Email: gmail_search_messages
- Database: db_get_available_queries(), db_execute_query()
"""
    
    if add_prompt(conn, user_id, 
                 "Daily Email Coordinator - Check-In", 
                 "workflow_automation", 
                 "full_prompt",
                 "Mid-day check-in: review AI progress, process new emails, update Synergy. Uses db_get_available_queries() first.",
                 checkin_prompt,
                 "email,synergy,checkin,progress",
                 source):
        added_count += 1
    
    # Quick Action 1: Single Email Handler
    single_email_prompt = """**Single Email Handler** - Quick processing without Synergy session.

**DATABASE WORKFLOW:**
1. db_get_available_queries(category="Client Analysis")
2. db_execute_query(query_name="client_lookup", params={"email": "..."})

**PROCESS:**
- Get email: gmail_get_message()
- Lookup client: Use two-step database pattern above
- Take action based on type (quote/support/invoice/general)
- Draft response: gmail_create_draft()
- Present to user with client history

**TOOLS:** gmail_get_message, db_get_available_queries, db_execute_query, db_calculate_quote, xero_get_invoices, gmail_create_draft
"""
    
    if add_prompt(conn, user_id, 
                 "Single Email Handler", 
                 "communication", 
                 "quick_action",
                 "Quick single email processing without Synergy. Uses db_get_available_queries() then db_execute_query().",
                 single_email_prompt,
                 "email,quick,single",
                 source):
        added_count += 1
    
    # Quick Action 2: Client History
    client_history_prompt = """**Client History Check** - Full client verification and history.

**DATABASE WORKFLOW:**
1. db_get_available_queries(category="Client Analysis")
2. db_execute_query(query_name="client_lookup", params={...})
3. db_execute_query(query_name="client_order_history", params={...})
4. db_execute_query(query_name="client_preferences", params={...})

**PROCESS:**
- Discover client queries with db_get_available_queries()
- Execute client lookup
- Get order history
- Get product preferences
- Check Xero for financial status
- Search email threads
- Present comprehensive summary

**TOOLS:** db_get_available_queries, db_execute_query, xero_get_contacts, xero_get_invoices, gmail_search_messages
"""
    
    if add_prompt(conn, user_id, 
                 "Client History Check", 
                 "business_operations", 
                 "quick_action",
                 "Comprehensive client verification with order history, preferences, Xero status. Uses db_get_available_queries() to discover client queries.",
                 client_history_prompt,
                 "client,history,xero,verification",
                 source):
        added_count += 1
    
    # Quick Action 3: Search Similar Orders
    similar_orders_prompt = """**Search Similar Orders** - Find if similar product has been done before.

**DATABASE WORKFLOW:**
1. db_get_available_queries() - Find order search queries
2. db_execute_query(query_name="product_search", params={"product": "..."})
3. db_execute_query(query_name="order_by_specs", params={"stock": "...", "finish": "..."})
4. db_execute_query(query_name="pricing_history", params={...})

**PROCESS:**
- User provides: product type, quantity, specs
- Discover order queries with db_get_available_queries()
- Search by product name
- Search by specifications
- Search by quantity range
- Analyze pricing trends
- Generate quote with db_calculate_quote()
- Present findings with recommendations

**TOOLS:** db_get_available_queries, db_execute_query, db_calculate_quote
"""
    
    if add_prompt(conn, user_id, 
                 "Search Similar Orders", 
                 "business_operations", 
                 "quick_action",
                 "Find similar past orders by product/specs/quantity. Uses db_get_available_queries() to discover order search capabilities.",
                 similar_orders_prompt,
                 "orders,search,history,specs",
                 source):
        added_count += 1
    
    # Quick Action 4: Xero AP Summary
    xero_ap_prompt = """**Xero Accounts Payable Summary** - Outstanding bills and payment priorities.

**PROCESS:**
- Get unpaid bills: xero_get_invoices(status="AUTHORISED", invoice_type="ACCPAY")
- Categorize by due date (overdue, this week, next week, future)
- Get recent payments: xero_get_payments(date_from="...")
- Analyze by supplier
- Present summary with recommended actions

**TOOLS:** xero_get_invoices, xero_get_payments, xero_get_contacts
"""
    
    if add_prompt(conn, user_id, 
                 "Xero Accounts Payable Summary", 
                 "finance", 
                 "quick_action",
                 "Quick AP snapshot from Xero: overdue, due this week, by supplier, cash flow impact.",
                 xero_ap_prompt,
                 "xero,finance,payable,bills",
                 source):
        added_count += 1
    
    # Quick Action 5: Business Performance
    business_performance_prompt = """**Business Performance Snapshot** - Quick business health check.

**DATABASE WORKFLOW:**
1. db_get_available_queries() - Discover business intelligence queries
2. db_get_business_summary(months=1) - Or use specific queries:
3. db_execute_query(query_name="revenue_summary", params={...})
4. db_execute_query(query_name="top_clients", params={...})
5. db_execute_query(query_name="product_performance", params={...})

**PROCESS:**
- Get business summary or specific queries
- Top clients analysis
- Pending work (ready to invoice, in production, urgent)
- Product mix analysis
- Cash flow from Xero
- Present KPIs with insights and recommendations

**TOOLS:** db_get_available_queries, db_get_business_summary, db_execute_query, xero_get_invoices
"""
    
    if add_prompt(conn, user_id, 
                 "Business Performance Snapshot", 
                 "business_intelligence", 
                 "quick_action",
                 "Business health check: revenue, clients, pending work, product mix, cash flow, KPIs. Uses db_get_available_queries().",
                 business_performance_prompt,
                 "kpi,performance,revenue,snapshot",
                 source):
        added_count += 1
    
    conn.commit()
    
    # Get totals
    cursor = conn.cursor()
    sql, params = convert_sql_placeholders("SELECT COUNT(*) FROM prompt_library WHERE user_id = ?", (user_id,))

    cursor.execute(sql, params)
    total_prompts = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM prompt_library
        WHERE user_id = ?
        GROUP BY category
        ORDER BY count DESC
    """, (user_id,))

    cursor.execute(sql, params)
    
    categories = cursor.fetchall()
    
    conn.close()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"\nSUCCESS: Added {added_count} new prompts")
    print(f"Total prompts for user_id={user_id}: {total_prompts}")
    print(f"\nPrompts by Category:")
    for category in categories:
        print(f"   - {category[0]}: {category[1]} prompts")
    
    print("\nNEW PROMPTS ADDED:")
    print("   FULL PROMPTS (2):")
    print("   1. Daily Email Coordinator - Morning Briefing")
    print("   2. Daily Email Coordinator - Check-In")
    print("\n   QUICK ACTIONS (5):")
    print("   3. Single Email Handler")
    print("   4. Client History Check")
    print("   5. Search Similar Orders")
    print("   6. Xero Accounts Payable Summary")
    print("   7. Business Performance Snapshot")
    
    print("\nKEY FEATURE:")
    print("   All prompts explicitly state two-step database workflow:")
    print("   1. db_get_available_queries() - Discover available queries")
    print("   2. db_execute_query(query_name, params) - Execute query")
    
    print("\nUSAGE:")
    print("   1. Open http://localhost:5001/ui")
    print("   2. Click lightning bolt button (Prompt Library)")
    print("   3. Select a prompt")
    print("   4. AI will follow the two-step database pattern")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()

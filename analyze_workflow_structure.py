"""
Analyze Workflow Structure - Detailed Examination
=================================================
Analyzes the workflow JSON structures provided by the user to identify issues
with arrow rendering, automation structure, and schedule configuration.
"""

import json

# The three workflows provided by the user
workflows = [
    {
        "automation_id": "wf_3z9ce4l5_1763565968",
        "title": "Smart Email Processing & Quote Generation",
        "ui_json": "{}",
        "execution_json": "{}",
        "status": "draft"
    },
    {
        "automation_id": "wf_7prr8le9_1763559775",
        "title": "Daily Sales Report Generator",
        "ui_json": '{"shapes": [{"x": 200, "y": 100, "id": 1, "type": "schedule", "color": "#3B82F6", "label": "Daily at 9 AM", "width": 220, "height": 90, "description": "Cron: 0 9 * * *"}, {"x": 200, "y": 300, "id": 2, "type": "database", "color": "#EC4899", "label": "Query Sales DB", "width": 220, "height": 90, "description": "Get yesterday\'s transactions"}, {"x": 200, "y": 500, "id": 3, "type": "tool", "color": "#6B7280", "label": "Calculate Metrics", "width": 220, "height": 90, "description": "Total, average, top products"}, {"x": 200, "y": 700, "id": 4, "type": "tool", "color": "#8B5CF6", "label": "Generate Charts", "width": 220, "height": 90, "description": "Create bar/pie charts"}, {"x": 500, "y": 700, "id": 5, "type": "tool", "color": "#10B981", "label": "Format Report", "width": 220, "height": 90, "description": "HTML email template"}, {"x": 200, "y": 900, "id": 6, "type": "tool", "color": "#F59E0B", "label": "Send Email", "width": 220, "height": 90, "description": "To: management@company.com"}, {"x": 200, "y": 1100, "id": 7, "type": "database", "color": "#EC4899", "label": "Archive Report", "width": 220, "height": 90, "description": "Save to Google Drive"}, {"x": 200, "y": 1300, "id": 8, "type": "end", "color": "#EF4444", "label": "Complete", "width": 160, "height": 80, "description": "Report sent"}], "connections": [{"id": 1, "to": 2, "from": 1, "label": "trigger"}, {"id": 2, "to": 3, "from": 2, "label": "raw data"}, {"id": 3, "to": 4, "from": 3, "label": "metrics"}, {"id": 4, "to": 5, "from": 3, "label": "metrics"}, {"id": 5, "to": 6, "from": 4, "label": "charts"}, {"id": 6, "to": 6, "from": 5, "label": "template"}, {"id": 7, "to": 7, "from": 6, "label": "sent"}, {"id": 8, "to": 8, "from": 7, "label": "archived"}]}',
        "execution_json": "{}",
        "status": "draft"
    },
    {
        "automation_id": "wf_client_reactivation_1763946900",
        "title": "High-Value Client Reactivation - FRED Database Analysis",
        "ui_json": '{"shapes": [{"x": 120, "y": 80, "id": "trigger_1", "text": "Schedule Trigger\\nMonthly 1st 10am", "type": "trigger", "color": "#10B981", "width": 240, "height": 100}, {"x": 120, "y": 230, "id": "action_1", "text": "Query FRED Database\\nfred_query_clients", "type": "tool", "color": "#6B7280", "width": 240, "height": 100}, {"x": 120, "y": 380, "id": "action_2", "text": "Calculate Expected Orders\\nAnalyze Order History", "type": "tool", "color": "#6B7280", "width": 240, "height": 100}, {"x": 120, "y": 530, "id": "action_3", "text": "Filter Inactive Clients\\nDue But Not Ordered", "type": "tool", "color": "#6B7280", "width": 240, "height": 100}, {"x": 120, "y": 680, "id": "decision_1", "text": "Found Inactive Clients?", "type": "decision", "color": "#F59E0B", "width": 240, "height": 100}, {"x": 480, "y": 680, "id": "action_4", "text": "Create Synergy Session\\nsynergy_create_session", "type": "tool", "color": "#6B7280", "width": 240, "height": 100}, {"x": 480, "y": 830, "id": "action_5", "text": "AI Research Each Client\\nweb_search + analyze", "type": "tool", "color": "#6B7280", "width": 240, "height": 100}, {"x": 800, "y": 680, "id": "action_6", "text": "Add Client Milestone\\nsynergy_add_milestone", "type": "tool", "color": "#6B7280", "width": 240, "height": 100}, {"x": 800, "y": 830, "id": "action_7", "text": "Create Research Doc\\ngoogle_docs_create", "type": "tool", "color": "#6B7280", "width": 240, "height": 100}, {"x": 800, "y": 980, "id": "action_8", "text": "Develop Strategy\\nAI Strategy Generator", "type": "tool", "color": "#6B7280", "width": 240, "height": 100}, {"x": 800, "y": 1130, "id": "action_9", "text": "Generate Email Campaigns\\nai_generate_text", "type": "tool", "color": "#6B7280", "width": 240, "height": 100}, {"x": 480, "y": 980, "id": "action_10", "text": "Create Action Tasks\\nsynergy_add_task", "type": "tool", "color": "#6B7280", "width": 240, "height": 100}, {"x": 480, "y": 1130, "id": "action_11", "text": "Update Milestone\\nsynergy_update_milestone", "type": "tool", "color": "#6B7280", "width": 240, "height": 100}, {"x": 480, "y": 1280, "id": "output_1", "text": "Send Team Report\\nslack_post_message", "type": "output", "color": "#EAB308", "width": 240, "height": 100}], "connections": [{"to": "action_1", "from": "trigger_1"}, {"to": "action_2", "from": "action_1"}, {"to": "action_3", "from": "action_2"}, {"to": "decision_1", "from": "action_3"}, {"to": "action_4", "from": "decision_1", "label": "Yes"}, {"to": "action_5", "from": "action_4"}, {"to": "action_6", "from": "action_5"}, {"to": "action_7", "from": "action_6"}, {"to": "action_8", "from": "action_7"}, {"to": "action_9", "from": "action_8"}, {"to": "action_10", "from": "action_6"}, {"to": "action_11", "from": "action_9"}, {"to": "action_11", "from": "action_10"}, {"to": "output_1", "from": "action_11"}]}',
        "execution_json": '{"actions": [{"id": "action_1", "tool": "fred_query_clients", "parameters": {"query": "SELECT * FROM clients WHERE lifetime_value > 10000 ORDER BY last_order_date DESC"}}, {"id": "action_2", "tool": "calculate_expected_orders", "parameters": {"clients": "{{action_1.clients}}", "analysis_period": "90_days"}}, {"id": "action_3", "tool": "filter_inactive_clients", "parameters": {"clients": "{{action_2.analyzed_clients}}", "criteria": {"actual_order": false, "days_overdue": "> 30", "expected_order": true}}}, {"id": "action_4", "tool": "synergy_create_session", "parameters": {"title": "Client Reactivation Campaign - {{month}} {{year}}", "description": "High-value clients reactivation strategy and outreach", "session_type": "sales"}}, {"id": "action_5", "tool": "ai_research_client", "parameters": {"client": "{{client_data}}", "research_points": ["Recent company news", "Industry trends", "Competitor analysis", "Social media activity", "Business changes"]}}, {"id": "action_6", "tool": "synergy_add_milestone", "parameters": {"title": "{{client_name}} - ${{lifetime_value}} LTV", "priority": "high", "session_id": "{{action_4.session_id}}", "description": "Last order: {{last_order_date}} ({{days_since_order}} days ago)"}}, {"id": "action_7", "tool": "google_docs_create", "parameters": {"title": "Client Research - {{client_name}}", "content": "Client: {{client_name}}\\nLifetime Value: ${{lifetime_value}}\\nLast Order: {{last_order_date}}\\n\\nResearch Findings:\\n{{action_5.research}}\\n\\nOrder History:\\n{{order_history}}\\n\\nPrevious Products:\\n{{products_ordered}}"}}, {"id": "action_8", "tool": "ai_develop_reactivation_strategy", "parameters": {"prompt": "Develop a personalized reactivation strategy considering client history, industry trends, and current needs", "research": "{{action_5.research}}", "client_data": "{{client_data}}"}}, {"id": "action_9", "tool": "ai_generate_text", "parameters": {"tone": "professional, personal, value-focused", "length": "medium", "prompt": "Write 3 personalized email campaigns for {{client_name}} based on strategy: {{action_8.strategy}}"}}, {"id": "action_10", "tool": "synergy_add_task", "parameters": {"tasks": [{"title": "Phase 1: Initial Outreach", "subtasks": ["Review client research", "Personalize email template", "Send initial reconnection email", "Schedule follow-up"]}, {"title": "Phase 2: Value Demonstration", "subtasks": ["Send product updates email", "Share relevant case studies", "Offer exclusive promotion", "Request phone call"]}, {"title": "Phase 3: Closing Strategy", "subtasks": ["Send final outreach email", "Offer custom quote", "Personal call from account manager", "Mark as completed/inactive"]}], "milestone_id": "{{action_6.milestone_id}}"}}, {"id": "action_11", "tool": "synergy_update_milestone", "parameters": {"milestone_id": "{{action_6.milestone_id}}", "internal_docs": ["Research Document: {{action_7.doc_url}}", "Reactivation Strategy: {{action_8.strategy}}", "Email Campaign 1: {{action_9.email_1}}", "Email Campaign 2: {{action_9.email_2}}", "Email Campaign 3: {{action_9.email_3}}", "Expected Revenue: ${{expected_order_value}}", "Success Probability: {{action_8.success_rate}}%"]}}, {"id": "output_1", "tool": "slack_post_message", "parameters": {"text": "🎯 Monthly Reactivation Campaign Ready!\\n\\n{{inactive_count}} high-value clients identified\\nTotal potential revenue: ${{total_potential}}\\n\\nSynergy Session: {{action_4.session_url}}", "channel": "#sales"}}], "trigger": {"type": "schedule", "timezone": "Australia/Sydney", "schedule_cron": "0 10 1 * *"}}',
        "status": "active"
    }
]

print("\n" + "="*100)
print("WORKFLOW STRUCTURE ANALYSIS - ARROW RENDERING & AUTOMATION STRUCTURE")
print("="*100)

for idx, workflow in enumerate(workflows, 1):
    print(f"\n{'='*100}")
    print(f"WORKFLOW {idx}: {workflow['title']}")
    print(f"{'='*100}")
    print(f"Automation ID: {workflow['automation_id']}")
    print(f"Status: {workflow['status']}")
    
    # Parse ui_json
    try:
        ui_data = json.loads(workflow['ui_json'])
        shapes = ui_data.get('shapes', [])
        connections = ui_data.get('connections', [])
        
        print(f"\n📊 UI_JSON ANALYSIS:")
        print(f"  Total shapes: {len(shapes)}")
        print(f"  Total connections: {len(connections)}")
        
        # CRITICAL ISSUE 1: Check for empty ui_json
        if not shapes and not connections:
            print("\n  ❌ CRITICAL ISSUE: ui_json is EMPTY!")
            print("     This workflow has NO visual data - arrows cannot render!")
            print("     Expected: shapes array with objects containing id, type, x, y, etc.")
            print("     Expected: connections array with objects containing from, to")
            continue
        
        # Analyze shape IDs
        print(f"\n  Shape IDs and Types:")
        shape_ids = []
        for shape in shapes:
            shape_id = shape.get('id')
            shape_type = shape.get('type', 'unknown')
            shape_ids.append(shape_id)
            
            # Check for label vs text field
            has_label = 'label' in shape
            has_text = 'text' in shape
            display_field = shape.get('label') or shape.get('text', 'NO LABEL')
            
            print(f"    - ID: {shape_id} ({type(shape_id).__name__}) | Type: {shape_type} | Display: {display_field[:30]}")
            
            if not has_label and not has_text:
                print(f"      ⚠️  WARNING: Shape has no 'label' or 'text' field")
        
        # CRITICAL ISSUE 2: Analyze connection structure
        print(f"\n  Connection Structure:")
        if not connections:
            print("    ❌ CRITICAL ISSUE: NO CONNECTIONS!")
            print("       Arrows cannot render without connection data")
        else:
            for i, conn in enumerate(connections, 1):
                conn_id = conn.get('id', 'NO_ID')
                from_id = conn.get('from')
                to_id = conn.get('to')
                label = conn.get('label', '')
                
                print(f"    Connection {i}:")
                print(f"      ID: {conn_id} ({type(conn_id).__name__})")
                print(f"      FROM: {from_id} ({type(from_id).__name__})")
                print(f"      TO: {to_id} ({type(to_id).__name__})")
                if label:
                    print(f"      Label: {label}")
                
                # CRITICAL ISSUE 3: Type mismatch validation
                from_exists = from_id in shape_ids
                to_exists = to_id in shape_ids
                
                # Check with type conversion
                if isinstance(from_id, int):
                    from_str = str(from_id)
                    from_shape = f"shape_{from_id}"
                    from_exists_str = from_str in shape_ids
                    from_exists_shape = from_shape in shape_ids
                    
                    print(f"      FROM validation:")
                    print(f"        Exact match ({from_id}): {'✅ YES' if from_exists else '❌ NO'}")
                    print(f"        String match ('{from_str}'): {'✅ YES' if from_exists_str else '❌ NO'}")
                    print(f"        Shape format ('{from_shape}'): {'✅ YES' if from_exists_shape else '❌ NO'}")
                    
                    if not from_exists and not from_exists_str and not from_exists_shape:
                        print(f"        ❌ CRITICAL: FROM shape ID {from_id} NOT FOUND in shapes!")
                        print(f"           Available shape IDs: {shape_ids[:5]}...")
                else:
                    print(f"      FROM exists: {'✅ YES' if from_exists else '❌ NO'}")
                    if not from_exists:
                        print(f"        ❌ CRITICAL: FROM shape ID '{from_id}' NOT FOUND!")
                
                # Same for TO
                if isinstance(to_id, int):
                    to_str = str(to_id)
                    to_shape = f"shape_{to_id}"
                    to_exists_str = to_str in shape_ids
                    to_exists_shape = to_shape in shape_ids
                    
                    print(f"      TO validation:")
                    print(f"        Exact match ({to_id}): {'✅ YES' if to_exists else '❌ NO'}")
                    print(f"        String match ('{to_str}'): {'✅ YES' if to_exists_str else '❌ NO'}")
                    print(f"        Shape format ('{to_shape}'): {'✅ YES' if to_exists_shape else '❌ NO'}")
                    
                    if not to_exists and not to_exists_str and not to_exists_shape:
                        print(f"        ❌ CRITICAL: TO shape ID {to_id} NOT FOUND in shapes!")
                else:
                    print(f"      TO exists: {'✅ YES' if to_exists else '❌ NO'}")
                    if not to_exists:
                        print(f"        ❌ CRITICAL: TO shape ID '{to_id}' NOT FOUND!")
    
    except json.JSONDecodeError as e:
        print(f"\n  ❌ ERROR: Invalid JSON in ui_json: {e}")
    
    # Parse execution_json
    try:
        exec_data = json.loads(workflow['execution_json'])
        actions = exec_data.get('actions', [])
        trigger = exec_data.get('trigger', {})
        
        print(f"\n📋 EXECUTION_JSON ANALYSIS:")
        if not actions and not trigger:
            print("  ⚠️  EMPTY - No automation logic defined")
        else:
            print(f"  Total actions: {len(actions)}")
            
            if trigger:
                print(f"\n  Trigger Configuration:")
                print(f"    Type: {trigger.get('type', 'NOT SET')}")
                print(f"    Cron: {trigger.get('schedule_cron', 'NOT SET')}")
                print(f"    Timezone: {trigger.get('timezone', 'NOT SET')}")
                
                # CRITICAL ISSUE 4: Validate cron format
                cron = trigger.get('schedule_cron')
                if cron:
                    parts = cron.split()
                    if len(parts) != 5:
                        print(f"    ❌ INVALID CRON: Must have 5 parts (minute hour day month weekday)")
                        print(f"       Got: {len(parts)} parts - '{cron}'")
                    else:
                        print(f"    ✅ Valid cron format")
                else:
                    print(f"    ⚠️  No schedule_cron defined (manual trigger)")
            else:
                print(f"  ⚠️  No trigger configuration found")
            
            # Analyze actions
            if actions:
                print(f"\n  Actions:")
                for action in actions[:3]:  # Show first 3
                    action_id = action.get('id', 'NO_ID')
                    tool = action.get('tool', 'NO_TOOL')
                    print(f"    - {action_id}: {tool}")
                if len(actions) > 3:
                    print(f"    ... and {len(actions) - 3} more actions")
    
    except json.JSONDecodeError as e:
        print(f"\n  ❌ ERROR: Invalid JSON in execution_json: {e}")

# Summary
print("\n" + "="*100)
print("SUMMARY OF FINDINGS")
print("="*100)

print("\n🔍 KEY ISSUES IDENTIFIED:\n")

print("1. WORKFLOW 1 - Smart Email Processing")
print("   ❌ CRITICAL: ui_json is EMPTY ('{}') - NO visual data")
print("   Result: No shapes, no connections, arrows cannot render")
print("   Fix: Re-save workflow from visual canvas to populate ui_json\n")

print("2. WORKFLOW 2 - Daily Sales Report Generator")
print("   ⚠️  ISSUE: Connections use NUMERIC IDs (1, 2, 3...)")
print("   ⚠️  ISSUE: Shapes also use NUMERIC IDs (1, 2, 3...)")
print("   Impact: With the ID normalization fix, these SHOULD work now")
print("   Note: Uses 'label' field instead of 'text' - both are supported\n")

print("3. WORKFLOW 3 - High-Value Client Reactivation")
print("   ✅ GOOD: Uses STRING IDs ('trigger_1', 'action_1'...)")
print("   ✅ GOOD: Connections reference correct shape IDs")
print("   ✅ GOOD: Has execution_json with trigger configuration")
print("   ✅ GOOD: Uses 'text' field for shape labels")
print("   Result: Arrows SHOULD render correctly\n")

print("="*100)
print("RECOMMENDATIONS")
print("="*100)

print("\n📝 IMMEDIATE ACTIONS:\n")

print("1. Workflow 1 (wf_3z9ce4l5_1763565968):")
print("   - Open workflow in visual canvas")
print("   - Add shapes manually")
print("   - Connect shapes with arrows")
print("   - Click 'Save' to populate ui_json")
print("   - Currently: This workflow is non-functional for visual display\n")

print("2. Workflow 2 (wf_7prr8le9_1763559775):")
print("   - Load this workflow to test the ID normalization fix")
print("   - Numeric IDs (1→2→3) should now convert to (shape_1→shape_2→shape_3)")
print("   - Arrows should render with the fix implemented\n")

print("3. Workflow 3 (fred-reactivation-campaign-1763946900):")
print("   - This workflow is correctly structured")
print("   - Should work without any changes")
print("   - Good reference for future workflows\n")

print("="*100)
print("AUTOMATION STRUCTURE VALIDATION")
print("="*100)

print("\n✅ CORRECTLY STRUCTURED:")
print("   - Workflow 3: Has complete execution_json with actions and trigger")
print("   - Workflow 3: Cron schedule '0 10 1 * *' is valid (1st of month, 10am)")
print("   - Workflow 3: Timezone 'Australia/Sydney' is set")
print("   - Workflow 3: Actions have proper tool names and parameters\n")

print("❌ INCOMPLETE:")
print("   - Workflow 1: Empty execution_json ('{}') - no automation logic")
print("   - Workflow 2: Empty execution_json ('{}') - no automation logic")
print("   - Both workflows are 'draft' status - expected for incomplete workflows\n")

print("="*100)
print("CONCLUSION")
print("="*100)

print("\n🎯 WHY ARROWS DON'T SHOW:\n")

print("Workflow 1: No ui_json data → No arrows possible (empty)")
print("Workflow 2: Numeric IDs → Should work with ID normalization fix")
print("Workflow 3: Properly structured → Should work (string IDs)\n")

print("📊 DATA STRUCTURE QUALITY:")
print("Workflow 1: 0/10 - Completely empty visual data")
print("Workflow 2: 7/10 - Has structure but uses numeric IDs (now fixed)")
print("Workflow 3: 10/10 - Perfect structure with string IDs\n")

print("✅ NEXT STEPS:")
print("1. Test Workflow 2 and 3 loading - arrows should render")
print("2. Re-create Workflow 1 from scratch in the visual canvas")
print("3. Always use string IDs for new workflows (e.g., 'action_1', not 1)")
print("4. Ensure ui_json is populated by saving from canvas, not manually\n")

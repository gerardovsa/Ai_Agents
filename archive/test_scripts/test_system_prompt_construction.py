"""
Test System Prompt Construction - Export Complete System Prompt
from shared.database_utils import convert_sql_placeholders

This script simulates the complete system prompt construction flow to verify:
1. Base tool usage instructions loaded from .md file
2. UI context prompt added (data_agent_chat)
3. User context block built from user preferences
4. Platform-specific instructions injected conditionally
5. Complete system prompt exported to text file

Tests THREE scenarios:
- Microsoft 365 user
- Google Workspace user
- Local account user (no OAuth)
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def get_user_preferences_from_db(user_id: int):
    """Simulate fetching user preferences from database"""
    import sqlite3
    
    root_dir = Path(__file__).parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    sql, params = convert_sql_placeholders("""
        SELECT 
            nickname, auth_platform,
            communication_style, detail_level, 
            detected_city, detected_country, detected_timezone,
            ai_memories, preferred_tools
        FROM user_preferences
        WHERE user_id = ?
    """, (user_id,))

    
    cursor.execute(sql, params)
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        # Build location string
        city = row['detected_city'] or 'Unknown'
        country = row['detected_country'] or 'Unknown'
        location = f"{city}, {country}"
        
        return {
            'nickname': row['nickname'],
            'auth_platform': row['auth_platform'],
            'communication_style': row['communication_style'],
            'detail_level': row['detail_level'],
            'location': location,
            'timezone': row['detected_timezone'],
            'ai_memories': row['ai_memories'],
            'preferred_tools': row['preferred_tools']
        }
    
    return None


def load_base_tool_usage_instructions():
    """Load base tool usage instructions from .md file"""
    prompt_path = Path(__file__).parent / 'AI_infrastructure' / 'prompts' / 'tool_usage_system_prompt.md'
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_ui_context_prompt(ui_context: str):
    """
    Get UI context-specific prompt (simulating unified_ai_client.py)
    
    NOTE: As of Nov 14, 2025 - UI Context Prompt is DISABLED in unified_ai_client.py
    Returning empty string to match production behavior (line 196)
    """
    # DISABLED - No longer added to system prompt (commented out in unified_ai_client.py)
    return ""


def build_user_context_block(user_prefs: dict, auth_platform: str):
    """Build user context block (simulating agent_routes_v4.py lines 860-900)"""
    
    nickname = user_prefs.get('nickname', 'User')
    location = user_prefs.get('location', 'Unknown Location')
    communication_style = user_prefs.get('communication_style', 'professional')
    detail_level = user_prefs.get('detail_level', 'moderate')
    
    # Parse AI memories
    ai_memories = []
    try:
        memories_json = user_prefs.get('ai_memories', '[]')
        if memories_json:
            ai_memories = json.loads(memories_json)
    except:
        ai_memories = []
    
    # Parse preferred tools
    preferred_tools = []
    try:
        tools_json = user_prefs.get('preferred_tools', '[]')
        if tools_json:
            preferred_tools = json.loads(tools_json)
    except:
        preferred_tools = []
    
    # Build time context
    now = datetime.now()
    day_of_week = now.strftime('%A')
    current_time_str = now.strftime('%I:%M %p %Z')
    month_name = now.strftime('%B')
    season = "Spring"  # Brisbane hemisphere
    
    # Simulate weather (would normally come from IP geolocation)
    temp_c = 27
    temp_f = 81
    weather_condition = "Partly Cloudy"
    
    # Build platform instructions
    if auth_platform == 'microsoft':
        platform_section = "MANDATORY PLATFORM USE: Microsoft 365 Suite"
    elif auth_platform == 'google':
        platform_section = "MANDATORY PLATFORM USE: Google Workspace"
    else:
        platform_section = "MANDATORY PLATFORM USE: None (Local Account)"
    
    user_context_block = f"""═══════════════════════════════════════════════════════════════
USER CONTEXT

User: {nickname}
Location: {location}
Current Time: {day_of_week}, {current_time_str}
Season: {month_name} ({season})
Weather: {temp_c}°C ({temp_f}°F), {weather_condition}

{platform_section}

Additional Preferences (YOU MUST FOLLOW THESE):
- Communication Style: {communication_style}
- Detail Level: {detail_level}"""
    
    # Add preferred tools
    if preferred_tools:
        user_context_block += "\n\nSpecial Instructions (CRITICAL - MUST FOLLOW):"
        for tool_pref in preferred_tools[:5]:  # Max 5
            user_context_block += f"\n- {tool_pref}"
    
    # Add AI memories
    if ai_memories:
        user_context_block += "\n\nKey Memories About This User:"
        for memory in ai_memories[:5]:  # Max 5
            user_context_block += f"\n- {memory}"
    
    user_context_block += "\n═══════════════════════════════════════════════════════════════\n"
    
    return user_context_block


def build_platform_instructions(auth_platform: str):
    """Build platform-specific instructions (simulating agent_routes_v4.py lines 816-900)"""
    
    if auth_platform == 'microsoft':
        return """
YOU MUST USE Microsoft 365 Suite tools ONLY - Do NOT use Google Workspace tools!

**Productivity Suite (Microsoft 365):**
- Email: list_platform_tools("microsoft_outlook")
- Documents: list_platform_tools("microsoft_word")
- Spreadsheets: list_platform_tools("microsoft_excel")
- Presentations: list_platform_tools("microsoft_powerpoint")
- Storage: list_platform_tools("microsoft_onedrive")
- Calendar: list_platform_tools("microsoft_calendar")
- Tasks: list_platform_tools("microsoft_todo")
- Notes: list_platform_tools("microsoft_onenote")
- Team Chat: list_platform_tools("microsoft_teams")
- Forms: list_platform_forms("microsoft_forms")

**Also Available (Platform-Agnostic Tools):**
- Payments: list_platform_tools("stripe")
- Team Chat: list_platform_tools("slack")
- SMS/Phone: list_platform_tools("twilio")
- E-commerce: list_platform_tools("woocommerce")
- Accounting: list_platform_tools("xero")
- Code Repos: list_platform_tools("github")
- Social Media: list_platform_tools("instagram")
- Payments: list_platform_tools("paypal")
- Projects: list_platform_tools("synergy")
- InHouse Print: list_platform_tools("inhouse")

**Discovery Methods:**
- list_platform_tools("microsoft_outlook") - Get all Outlook tools
- search_tools("send email") - Search across all tools
- get_tool_schema("microsoft_outlook_send_email") - Get parameters"""

    elif auth_platform == 'google':
        return """
YOU MUST USE Google Workspace tools ONLY - Do NOT use Microsoft 365 tools!

**Productivity Suite (Google Workspace):**
- Email: list_platform_tools("gmail")
- Documents: list_platform_tools("google_docs")
- Spreadsheets: list_platform_tools("google_sheets")
- Presentations: list_platform_tools("google_slides")
- Storage: list_platform_tools("google_drive")
- Calendar: list_platform_tools("google_calendar")
- Tasks: list_platform_tools("google_tasks")
- Forms: list_platform_tools("google_forms")
- Video Meetings: list_platform_tools("google_meet")
- Analytics: list_platform_tools("google_analytics")

**Also Available (Platform-Agnostic Tools):**
- Payments: list_platform_tools("stripe")
- Team Chat: list_platform_tools("slack")
- SMS/Phone: list_platform_tools("twilio")
- E-commerce: list_platform_tools("woocommerce")
- Accounting: list_platform_tools("xero")
- Code Repos: list_platform_tools("github")
- Social Media: list_platform_tools("instagram")
- Payments: list_platform_tools("paypal")
- Projects: list_platform_tools("synergy")
- InHouse Print: list_platform_tools("inhouse")

**Discovery Methods:**
- list_platform_tools("gmail") - Get all Gmail tools
- search_tools("send email") - Search across all tools
- get_tool_schema("gmail_send_email") - Get parameters"""

    else:
        return """
PLATFORM USE: Auto-detect

User has not connected Google Workspace or Microsoft 365.

**Available Platform-Agnostic Tools:**
- Payments: list_platform_tools("stripe")
- Team Chat: list_platform_tools("slack")
- SMS/Phone: list_platform_tools("twilio")
- E-commerce: list_platform_tools("woocommerce")
- Accounting: list_platform_tools("xero")
- Code Repos: list_platform_tools("github")
- Social Media: list_platform_tools("instagram")
- Payments: list_platform_tools("paypal")
- Projects: list_platform_tools("synergy")
- InHouse Print: list_platform_tools("inhouse")

**NOT Available (Requires OAuth Connection):**
- ❌ Google Workspace tools (Gmail, Docs, Sheets, Drive, Calendar, Forms, Meet)
- ❌ Microsoft 365 tools (Outlook, Word, Excel, OneDrive, Teams, Calendar)

**Discovery Methods:**
- list_platform_tools("stripe") - Get all Stripe tools
- search_tools("payment") - Search across all tools
- get_tool_schema("stripe_create_customer") - Get parameters"""


def construct_system_prompt(user_id: int, ui_context: str = 'data_agent_chat'):
    """
    Construct complete system prompt (simulating full flow)
    
    Steps:
    1. Load base tool usage instructions
    2. Add UI context prompt
    3. Build user context block
    4. Build platform instructions
    5. Inject both into system prompt
    """
    
    print(f"\n{'=' * 80}")
    print(f"🔷 CONSTRUCTING SYSTEM PROMPT FOR USER {user_id}")
    print(f"{'=' * 80}\n")
    
    # STEP 1: Load base tool usage instructions
    print("STEP 1: Loading base tool usage instructions...")
    tool_usage_instructions = load_base_tool_usage_instructions()
    print(f"  ✅ Loaded {len(tool_usage_instructions)} characters")
    
    # STEP 2: Add UI context prompt
    print("\nSTEP 2: Adding UI context prompt (data_agent_chat)...")
    ui_prompt = get_ui_context_prompt(ui_context)
    system_prompt = tool_usage_instructions + "\n\n" + ui_prompt
    print(f"  ✅ Added {len(ui_prompt)} characters")
    
    # STEP 3: Get user preferences
    print(f"\nSTEP 3: Fetching user preferences for user_id={user_id}...")
    user_prefs = get_user_preferences_from_db(user_id)
    if not user_prefs:
        print(f"  ❌ User {user_id} not found in database!")
        return None
    
    auth_platform = user_prefs.get('auth_platform', 'local')
    print(f"  ✅ User: {user_prefs['nickname']}")
    print(f"  ✅ Platform: {auth_platform}")
    print(f"  ✅ Style: {user_prefs['communication_style']}")
    print(f"  ✅ Detail: {user_prefs['detail_level']}")
    
    # STEP 4: Build user context block
    print("\nSTEP 4: Building user context block...")
    user_context_block = build_user_context_block(user_prefs, auth_platform)
    print(f"  ✅ Built {len(user_context_block)} characters")
    
    # STEP 5: Build platform instructions
    print("\nSTEP 5: Building platform-specific instructions...")
    platform_instructions = build_platform_instructions(auth_platform)
    print(f"  ✅ Built {len(platform_instructions)} characters")
    
    # STEP 6: Inject both into system prompt
    print("\nSTEP 6: Injecting user context and platform instructions...")
    
    # Replace {{USER_CONTEXT}} placeholder (if exists, otherwise add at top)
    if '{{USER_CONTEXT}}' in system_prompt:
        system_prompt = system_prompt.replace('{{USER_CONTEXT}}', user_context_block)
        print("  ✅ Replaced {{USER_CONTEXT}} placeholder")
    else:
        # Add at beginning of USER CONTEXT section
        system_prompt = system_prompt.replace(
            '# USER CONTEXT',
            f'# USER CONTEXT\n\n{user_context_block}'
        )
        print("  ✅ Inserted user context at USER CONTEXT section")
    
    # Replace {{PLATFORM_SPECIFIC_INSTRUCTIONS}} placeholder
    if '{{PLATFORM_SPECIFIC_INSTRUCTIONS}}' in system_prompt:
        system_prompt = system_prompt.replace('{{PLATFORM_SPECIFIC_INSTRUCTIONS}}', platform_instructions)
        print("  ✅ Replaced {{PLATFORM_SPECIFIC_INSTRUCTIONS}} placeholder")
    else:
        print("  ⚠️  Warning: {{PLATFORM_SPECIFIC_INSTRUCTIONS}} placeholder not found!")
    
    print(f"\n{'=' * 80}")
    print(f"✅ SYSTEM PROMPT CONSTRUCTION COMPLETE")
    print(f"{'=' * 80}")
    print(f"Total length: {len(system_prompt):,} characters ({len(system_prompt.split())} words)")
    print(f"Estimated tokens: ~{len(system_prompt) // 4:,} tokens")
    
    return system_prompt


def export_system_prompt(system_prompt: str, filename: str):
    """Export system prompt to text file in prompts folder"""
    # Export to AI_infrastructure/core/prompts/ folder
    root_dir = Path(__file__).parent
    prompts_dir = root_dir / 'AI_infrastructure' / 'core' / 'prompts'
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = prompts_dir / filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(system_prompt)
    
    print(f"\n📄 Exported to: {output_path}")
    print(f"   File size: {len(system_prompt):,} bytes")
    
    return output_path


def main():
    """Test system prompt construction for multiple user types"""
    
    print("\n" + "=" * 80)
    print("🧪 SYSTEM PROMPT CONSTRUCTION TEST")
    print("=" * 80)
    print("Testing THREE scenarios:")
    print("  1. User ID 1 - Microsoft 365 user")
    print("  2. User ID 2 - Google Workspace user (if exists)")
    print("  3. User ID 3 - Local account user (if exists)")
    print("=" * 80)
    
    # Test User 1 (Microsoft 365)
    print("\n\n" + "🔷" * 40)
    print("TEST 1: Microsoft 365 User")
    print("🔷" * 40)
    
    system_prompt_ms = construct_system_prompt(user_id=1)
    if system_prompt_ms:
        export_system_prompt(system_prompt_ms, 'system_prompt_microsoft365_user.txt')
    
    # Test User 2 (Google Workspace - if exists)
    print("\n\n" + "🔷" * 40)
    print("TEST 2: Google Workspace User (if exists)")
    print("🔷" * 40)
    
    # First check if user 2 exists
    try:
        user_prefs = get_user_preferences_from_db(2)
        if user_prefs:
            # Update to google for testing
            import sqlite3
            root_dir = Path(__file__).parent
            db_path = root_dir / 'data' / 'ai_infrastructure.db'
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("UPDATE user_preferences SET auth_platform = 'google' WHERE user_id = 2")
            conn.commit()
            conn.close()
            
            system_prompt_google = construct_system_prompt(user_id=2)
            if system_prompt_google:
                export_system_prompt(system_prompt_google, 'system_prompt_google_workspace_user.txt')
        else:
            print("  ⚠️  User ID 2 not found - skipping Google Workspace test")
    except Exception as e:
        print(f"  ⚠️  Error testing user 2: {e}")
    
    # Test User 3 (Local account - if exists)
    print("\n\n" + "🔷" * 40)
    print("TEST 3: Local Account User (if exists)")
    print("🔷" * 40)
    
    try:
        user_prefs = get_user_preferences_from_db(3)
        if user_prefs:
            # Update to local for testing
            import sqlite3
            root_dir = Path(__file__).parent
            db_path = root_dir / 'data' / 'ai_infrastructure.db'
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("UPDATE user_preferences SET auth_platform = 'local' WHERE user_id = 3")
            conn.commit()
            conn.close()
            
            system_prompt_local = construct_system_prompt(user_id=3)
            if system_prompt_local:
                export_system_prompt(system_prompt_local, 'system_prompt_local_account_user.txt')
        else:
            print("  ⚠️  User ID 3 not found - skipping local account test")
    except Exception as e:
        print(f"  ⚠️  Error testing user 3: {e}")
    
    print("\n\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETE!")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - system_prompt_microsoft365_user.txt")
    print("  - system_prompt_google_workspace_user.txt (if user 2 exists)")
    print("  - system_prompt_local_account_user.txt (if user 3 exists)")
    print("\nOpen these files to see the complete system prompt with:")
    print("  ✅ Base tool usage instructions")
    print("  ✅ UI context prompt (data_agent_chat)")
    print("  ✅ User-specific context (nickname, location, weather, etc.)")
    print("  ✅ Platform-specific instructions (only relevant tools)")
    print("  ✅ AI memories and preferred tools")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()

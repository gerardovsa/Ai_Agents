"""
Test script for Outlook conversation fetching fix (Jan 21, 2026)

This script tests the inbox + sentitems dual-fetch strategy for Outlook conversations.
It verifies that both incoming and outgoing messages are captured correctly.
"""

import sys
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'AI_infrastructure'))

print("=" * 80)
print("🧪 Testing Outlook Conversation Fetching Fix")
print("=" * 80)

# Test parameters
TEST_USER_ID = 14  # User ID with Microsoft OAuth credentials (printing@inhouseprint.com.au)
TEST_CONVERSATION_ID = "AAQkADMzNTk5YTZiLWNlZDQtNDJhYy1iMzE2LTczNjAxODM0NTUyMAAQAJr5V7m68UtCrcEvfIPDgt8="

print(f"\n📋 Test Configuration:")
print(f"   User ID: {TEST_USER_ID}")
print(f"   Conversation ID: {TEST_CONVERSATION_ID}")
print(f"   Strategy: Fetch inbox + sentitems, filter by conversationId in Python")

# Import the Outlook wrapper function
try:
    print("\n📦 Importing microsoft_outlook_list_messages...")
    from tools.implementations.microsoft_outlook_tools import microsoft_outlook_list_messages
    print("   ✅ Import successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 1: Fetch messages from INBOX
print("\n" + "=" * 80)
print("📥 STEP 1: Fetching messages from INBOX folder")
print("=" * 80)

try:
    inbox_result = microsoft_outlook_list_messages(
        folder='inbox',
        max_results=500,
        order_by='receivedDateTime desc',
        _user_id=TEST_USER_ID,
        _injected_credentials=True
    )
    
    print(f"\n📊 Inbox Result:")
    print(f"   Success: {inbox_result.get('success', False)}")
    print(f"   Total messages: {len(inbox_result.get('messages', []))}")
    
    inbox_messages = inbox_result.get('messages', [])
    if inbox_messages:
        print(f"\n   Sample inbox message:")
        sample = inbox_messages[0]
        print(f"      Subject: {sample.get('subject', 'N/A')}")
        print(f"      From: {sample.get('from', {}).get('emailAddress', {}).get('address', 'N/A')}")
        print(f"      ConversationId: {sample.get('conversationId', 'N/A')}")
        print(f"      ReceivedDateTime: {sample.get('receivedDateTime', 'N/A')}")
    
except Exception as e:
    print(f"   ❌ Inbox fetch failed: {e}")
    import traceback
    traceback.print_exc()
    inbox_result = {'success': False, 'messages': []}

# Step 2: Fetch messages from SENT ITEMS
print("\n" + "=" * 80)
print("📤 STEP 2: Fetching messages from SENTITEMS folder")
print("=" * 80)

try:
    sentitems_result = microsoft_outlook_list_messages(
        folder='sentitems',
        max_results=500,
        order_by='receivedDateTime desc',
        _user_id=TEST_USER_ID,
        _injected_credentials=True
    )
    
    print(f"\n📊 Sentitems Result:")
    print(f"   Success: {sentitems_result.get('success', False)}")
    print(f"   Total messages: {len(sentitems_result.get('messages', []))}")
    
    sentitems_messages = sentitems_result.get('messages', [])
    if sentitems_messages:
        print(f"\n   Sample sentitems message:")
        sample = sentitems_messages[0]
        print(f"      Subject: {sample.get('subject', 'N/A')}")
        print(f"      From: {sample.get('from', {}).get('emailAddress', {}).get('address', 'N/A')}")
        print(f"      ConversationId: {sample.get('conversationId', 'N/A')}")
        print(f"      ReceivedDateTime: {sample.get('receivedDateTime', 'N/A')}")
    
except Exception as e:
    print(f"   ❌ Sentitems fetch failed: {e}")
    import traceback
    traceback.print_exc()
    sentitems_result = {'success': False, 'messages': []}

# Step 3: Combine and filter by conversationId
print("\n" + "=" * 80)
print("🔗 STEP 3: Combining and filtering by conversationId")
print("=" * 80)

all_messages = []
if inbox_result.get('success'):
    all_messages.extend(inbox_result.get('messages', []))
    print(f"   ✅ Added {len(inbox_result.get('messages', []))} inbox messages")

if sentitems_result.get('success'):
    all_messages.extend(sentitems_result.get('messages', []))
    print(f"   ✅ Added {len(sentitems_result.get('messages', []))} sentitems messages")

print(f"\n📊 Combined Total: {len(all_messages)} messages")

# Filter messages that match the conversationId
conversation_messages = [
    msg for msg in all_messages 
    if msg.get('conversationId') == TEST_CONVERSATION_ID
]

print(f"🔍 Filtered by conversationId '{TEST_CONVERSATION_ID}': {len(conversation_messages)} matching messages")

# Step 4: Sort by receivedDateTime
print("\n" + "=" * 80)
print("📅 STEP 4: Sorting by receivedDateTime (oldest first)")
print("=" * 80)

conversation_messages.sort(key=lambda x: x.get('receivedDateTime', ''))
print(f"   ✅ Sorted {len(conversation_messages)} messages chronologically")

# Display conversation thread
if conversation_messages:
    print("\n" + "=" * 80)
    print("💬 CONVERSATION THREAD (Chronological Order)")
    print("=" * 80)
    
    for i, msg in enumerate(conversation_messages, 1):
        from_addr = msg.get('from', {})
        if isinstance(from_addr, dict):
            from_email = from_addr.get('emailAddress', {}).get('address', 'Unknown')
        else:
            from_email = str(from_addr)
        
        to_recipients = msg.get('toRecipients', [])
        to_email = ''
        if to_recipients and len(to_recipients) > 0:
            to_email = to_recipients[0].get('emailAddress', {}).get('address', '')
        
        print(f"\n📧 Message #{i}:")
        print(f"   Subject: {msg.get('subject', 'No Subject')}")
        print(f"   From: {from_email}")
        print(f"   To: {to_email}")
        print(f"   Date: {msg.get('receivedDateTime', 'N/A')}")
        print(f"   IsRead: {msg.get('isRead', False)}")
        print(f"   ConversationId: {msg.get('conversationId', 'N/A')}")
        print(f"   Snippet: {msg.get('bodyPreview', '')[:100]}...")
else:
    print("\n⚠️  No messages found in conversation")
    print(f"   Possible reasons:")
    print(f"   1. ConversationId not found in inbox or sentitems")
    print(f"   2. User has no messages in this conversation")
    print(f"   3. OAuth credentials missing or expired")

# Summary
print("\n" + "=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)
print(f"✅ Inbox messages fetched: {len(inbox_result.get('messages', []))}")
print(f"✅ Sentitems messages fetched: {len(sentitems_result.get('messages', []))}")
print(f"✅ Combined total: {len(all_messages)}")
print(f"✅ Conversation messages: {len(conversation_messages)}")

if len(conversation_messages) > 0:
    print(f"\n🎉 SUCCESS: Found {len(conversation_messages)} messages in conversation")
    print(f"   Both incoming and outgoing messages captured!")
else:
    print(f"\n⚠️  WARNING: No messages found")
    print(f"   Try a different conversationId or check OAuth credentials")

print("\n" + "=" * 80)

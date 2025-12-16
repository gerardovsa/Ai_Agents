"""
Test Conversation Memory Tools
===============================

Tests the new vector search tools for conversations and Synergy projects.
"""

import json
from tools.implementations.conversation_memory import (
    session_conversation_search,
    session_conversation_get_thread_messages,
    session_conversation_get_message_context,
    synergy_project_search,
    synergy_docs_search
)

print("=" * 70)
print("CONVERSATION MEMORY TOOLS TEST")
print("=" * 70)
print()

# Test 1: Search conversations
print("TEST 1: Search Conversations")
print("-" * 70)
query = "email automation Gmail API"
user_id = 14
print(f"Query: '{query}'")
print(f"User ID: {user_id}")
print()

try:
    result = session_conversation_search(
        query=query,
        user_id=user_id,
        time_filter="all_time",
        search_type="both",
        limit=5
    )
    
    print(f"Success: {result['success']}")
    print(f"Total Results: {result['total_results']}")
    print()
    
    if result['threads']:
        print("MATCHING THREADS:")
        for thread in result['threads']:
            print(f"  Thread ID: {thread['thread_id']}")
            print(f"  Title: {thread['title']}")
            print(f"  Similarity: {thread['similarity_score']}")
            print(f"  Messages: {thread['message_count']}")
            print(f"  Tools Used: {', '.join(thread['tools_used'][:3])}")
            print()
    
    if result['messages']:
        print("MATCHING MESSAGES:")
        for msg in result['messages'][:3]:  # Show first 3
            print(f"  Message ID: {msg['message_id']}")
            print(f"  Thread: {msg['thread_title']}")
            print(f"  Similarity: {msg['similarity_score']}")
            print(f"  Preview: {msg['content_preview'][:100]}...")
            print()
    
    # Test 2: Get full thread if we found one
    if result['threads']:
        thread_id = result['threads'][0]['thread_id']
        print()
        print("=" * 70)
        print(f"TEST 2: Get Thread Messages (Thread {thread_id})")
        print("-" * 70)
        
        thread_result = session_conversation_get_thread_messages(
            thread_id=thread_id,
            user_id=user_id,
            recent_only=True  # Get last 10 messages
        )
        
        if thread_result['success']:
            print(f"Thread: {thread_result['thread']['title']}")
            print(f"Total Messages: {thread_result['thread']['message_count']}")
            print(f"Returned: {len(thread_result['messages'])} messages")
            print(f"Truncated: {thread_result['truncated']}")
            print()
            
            if thread_result['messages']:
                print("RECENT MESSAGES:")
                for msg in thread_result['messages'][:3]:
                    print(f"  [{msg['role']}] at {msg['timestamp']}")
                    if msg.get('tool_calls'):
                        print(f"    Tool: {msg['tool_calls']}")
                    # Show text content
                    content = msg['content']
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                text = item.get('text', '')[:150]
                                print(f"    {text}...")
                                break
                    print()
    
    # Test 3: Get message context if we found a message
    if result['messages']:
        message_id = result['messages'][0]['message_id']
        print()
        print("=" * 70)
        print(f"TEST 3: Get Message Context (Message {message_id})")
        print("-" * 70)
        
        context_result = session_conversation_get_message_context(
            message_id=message_id,
            user_id=user_id,
            context_size=2
        )
        
        if context_result['success']:
            print(f"Thread: {context_result['thread_info']['title']}")
            print(f"Messages Before: {len(context_result['messages_before'])}")
            print(f"Messages After: {len(context_result['messages_after'])}")
            print()
            
            print("CONTEXT FLOW:")
            for msg in context_result['messages_before']:
                print(f"  [{msg['role']}] BEFORE")
            
            print(f"  [{context_result['target_message']['role']}] ⭐ TARGET MESSAGE")
            
            for msg in context_result['messages_after']:
                print(f"  [{msg['role']}] AFTER")
            print()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("TEST 4: Search Synergy Projects")
print("-" * 70)

try:
    synergy_result = synergy_project_search(
        query="custom quote calculator implementation",
        user_id=user_id,
        status_filter="all",
        limit=5
    )
    
    print(f"Success: {synergy_result['success']}")
    print(f"Total Results: {synergy_result['total_results']}")
    print()
    
    if synergy_result['projects']:
        print("MATCHING PROJECTS:")
        for project in synergy_result['projects']:
            print(f"  Session ID: {project['session_id']}")
            print(f"  Title: {project['title']}")
            print(f"  Similarity: {project['similarity_score']}")
            print(f"  Status: {project['status']}")
            print(f"  Priority: {project['priority']}")
            print(f"  Documents: {project['documents_count']}")
            if project['next_steps']:
                print(f"  Next Steps: {project['next_steps'][0] if project['next_steps'] else 'None'}")
            print()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("TEST 5: Search Synergy Documents")
print("-" * 70)

try:
    docs_result = synergy_docs_search(
        query="pricing guidelines vinyl banners",
        user_id=user_id,
        limit=5
    )
    
    print(f"Success: {docs_result['success']}")
    print(f"Total Results: {docs_result['total_results']}")
    print()
    
    if docs_result['documents']:
        print("MATCHING DOCUMENTS:")
        for doc in docs_result['documents']:
            print(f"  Doc ID: {doc['doc_id']}")
            print(f"  Project: {doc['session_title']}")
            print(f"  Title: {doc['title']}")
            print(f"  Similarity: {doc['similarity_score']}")
            print(f"  Type: {doc['doc_type']}")
            print(f"  Preview: {doc['content_preview'][:100]}...")
            print()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("TEST COMPLETE!")
print("=" * 70)

"""
Debug script to investigate 225,237 token explosion
Checks:
1. System prompt base size
2. Prompt library prompt sizes (Data Analyst, etc.)
3. Conversation history size for thread 1768890633197
4. Context injection sizes
"""
import os
import sys
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import execute_query
import tiktoken

# Initialize tokenizer (Claude uses same as GPT-4)
tokenizer = tiktoken.encoding_for_model("gpt-4")

def count_tokens(text: str) -> int:
    """Count tokens in text"""
    return len(tokenizer.encode(text))

def format_size(chars: int, tokens: int) -> str:
    """Format size info"""
    return f"{chars:>8,} chars | {tokens:>8,} tokens"

print("\n" + "="*80)
print("🔍 INVESTIGATING 225,237 TOKEN EXPLOSION")
print("="*80 + "\n")

# ============================================
# 1. CHECK SYSTEM PROMPT BASE SIZE
# ============================================
print("📋 1. CHECKING BASE SYSTEM PROMPT SIZE")
print("-" * 80)

try:
    from AI_infrastructure.core.unified_ai_client import UnifiedAIClient
    
    # Create client instance
    client = UnifiedAIClient()
    base_prompt = client.get_system_prompt('data_agent_chat')
    
    base_chars = len(base_prompt)
    base_tokens = count_tokens(base_prompt)
    
    print(f"Base system prompt: {format_size(base_chars, base_tokens)}")
    print()
except Exception as e:
    print(f"❌ ERROR: {e}\n")

# ============================================
# 2. CHECK PROMPT LIBRARY SIZES
# ============================================
print("📚 2. CHECKING PROMPT LIBRARY PROMPTS")
print("-" * 80)

try:
    # Get all prompts from library
    prompts = execute_query(
        """
        SELECT name, type, LENGTH(prompt_text) as char_count, prompt_text
        FROM ai_infrastructure.prompt_library
        ORDER BY LENGTH(prompt_text) DESC
        LIMIT 20
        """,
        fetch_mode='all'
    )
    
    if prompts:
        print(f"Found {len(prompts)} prompts in library (showing top 20 by size):\n")
        
        for prompt in prompts:
            name = prompt['name']
            ptype = prompt['type']
            char_count = prompt['char_count']
            text = prompt['prompt_text']
            tokens = count_tokens(text)
            
            print(f"  {name:30} [{ptype:15}] {format_size(char_count, tokens)}")
            
            # Check for Data Analyst specifically
            if name == 'Data Analyst':
                print(f"    ⚠️  DATA ANALYST FOUND!")
                print(f"    Preview: {text[:200]}...")
                print()
    else:
        print("  No prompts found in database")
    
    print()
except Exception as e:
    print(f"❌ ERROR: {e}\n")

# ============================================
# 3. CHECK CONVERSATION HISTORY
# ============================================
print("💬 3. CHECKING CONVERSATION HISTORY FOR THREAD 1768890633197")
print("-" * 80)

try:
    # Get thread ID
    thread = execute_query(
        "SELECT id FROM sessions.threads WHERE thread_slug = %s",
        ('1768890633197',),
        fetch_mode='one'
    )
    
    if thread:
        thread_id = thread['id']
        print(f"Thread ID: {thread_id}\n")
        
        # Get message count and sizes
        messages = execute_query(
            """
            SELECT role, LENGTH(content::text) as char_count, content
            FROM sessions.messages
            WHERE thread_id = %s
            ORDER BY created_at ASC
            """,
            (thread_id,),
            fetch_mode='all'
        )
        
        if messages:
            print(f"Found {len(messages)} messages:\n")
            
            total_chars = 0
            total_tokens = 0
            
            for idx, msg in enumerate(messages, 1):
                role = msg['role']
                char_count = msg['char_count']
                content = msg['content']
                
                # Parse JSONB content for token counting
                import json
                if isinstance(content, str):
                    content = json.loads(content)
                
                # Extract text from content blocks
                text = ""
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict):
                            if block.get('type') == 'text':
                                text += block.get('text', '')
                            elif block.get('type') == 'tool_use':
                                text += f"[tool_use: {block.get('name')}]"
                            elif block.get('type') == 'tool_result':
                                text += f"[tool_result: {len(str(block.get('content', '')))} chars]"
                
                tokens = count_tokens(text)
                total_chars += char_count
                total_tokens += tokens
                
                print(f"  [{idx:3}] {role:10} {format_size(char_count, tokens)}")
            
            print(f"\n  TOTAL: {format_size(total_chars, total_tokens)}")
            print(f"  ⚠️  Conversation alone: {total_tokens:,} tokens")
        else:
            print("  No messages found for this thread")
    else:
        print("  Thread not found in database")
    
    print()
except Exception as e:
    print(f"❌ ERROR: {e}\n")

# ============================================
# 4. CHECK CONTEXT INJECTION SIZES
# ============================================
print("🔗 4. CHECKING CONTEXT INJECTION FOR THREAD 1768890633197")
print("-" * 80)

try:
    # Get thread context data
    thread_ctx = execute_query(
        """
        SELECT 
            synergy_card_id,
            workflow_slug, workflow_title,
            automation_slug, automation_title,
            internal_doc_slug, internal_doc_title,
            email_thread_id, email_subject,
            tags
        FROM sessions.threads
        WHERE thread_slug = %s
        """,
        ('1768890633197',),
        fetch_mode='one'
    )
    
    if thread_ctx:
        print("Context linked to thread:\n")
        
        context_estimate = 0
        
        if thread_ctx['synergy_card_id']:
            print(f"  ✅ Synergy card: {thread_ctx['synergy_card_id']}")
            context_estimate += 2000  # Estimate
        
        if thread_ctx['workflow_slug']:
            print(f"  ✅ Workflow: {thread_ctx['workflow_slug']}")
            context_estimate += 1500  # Estimate
        
        if thread_ctx['automation_slug']:
            print(f"  ✅ Automation: {thread_ctx['automation_slug']}")
            context_estimate += 1500  # Estimate
        
        if thread_ctx['internal_doc_slug']:
            print(f"  ✅ Internal doc: {thread_ctx['internal_doc_slug']}")
            context_estimate += 3000  # Estimate
        
        if thread_ctx['email_thread_id']:
            print(f"  ✅ Email thread: {thread_ctx['email_thread_id']}")
            context_estimate += 2000  # Estimate
        
        if thread_ctx['tags']:
            import json
            tags = json.loads(thread_ctx['tags']) if isinstance(thread_ctx['tags'], str) else thread_ctx['tags']
            print(f"  ✅ Tags: {tags}")
            context_estimate += len(tags) * 500  # Estimate per tag
        
        print(f"\n  Estimated context injection: ~{context_estimate:,} tokens")
    else:
        print("  No context data found")
    
    print()
except Exception as e:
    print(f"❌ ERROR: {e}\n")

# ============================================
# 5. ESTIMATE TOTAL
# ============================================
print("📊 5. TOTAL ESTIMATE")
print("-" * 80)

print("""
Token Budget Breakdown (Claude 200K limit):
- Base system prompt: ~15,000 tokens
- User context block: ~500 tokens
- Prompt injection (Data Analyst): ??? tokens (CHECKING THIS)
- Context injection: ~5,000 tokens
- Tool suggestions: ~2,000 tokens
- System prompt continued: ~1,500 tokens
- Conversation history: ??? tokens (CHECKING THIS)
--------------------------------
= TOTAL SENT TO CLAUDE API

⚠️  ERROR RECEIVED: 225,237 tokens (25,237 over limit)
""")

print("="*80 + "\n")

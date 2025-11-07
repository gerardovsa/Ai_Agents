"""
COMPREHENSIVE FIX for streaming_agent_worker.py _build_messages() method
Apply this to AI_infrastructure/core/streaming_agent_worker.py lines 590-760

Fixes 7 critical issues:
1. Thinking block ordering
2. tool_result in assistant messages
3. Orphaned tool_result detection
4. String to block conversion
5. Missing signature field
6. Duplicate consecutive roles
7. Block field validation
"""

def _build_messages(
    self,
    conversation_history: List[Dict],
    user_prompt: str,
    is_first_round: bool
) -> List[Dict]:
    """
    Build messages array for Claude API with comprehensive validation
    
    Args:
        conversation_history: Full conversation history
        user_prompt: Current user prompt (empty for continuation)
        is_first_round: Whether this is the first round
    
    Returns:
        List of messages in Anthropic format
    """
    messages = []
    
    print(f"[StreamingWorker] Validating {len(conversation_history)} messages from history...")
    
    # Add existing conversation with validation
    for idx, msg in enumerate(conversation_history):
        message = {
            'role': msg.get('role'),
            'content': msg.get('content')
        }
        
        # ============================================================
        # STEP 1: NORMALIZE CONTENT TO LIST OF BLOCKS
        # ============================================================
        # Parse string content that might contain serialized blocks
        if isinstance(message.get('content'), str):
            try:
                import json
                parsed = json.loads(message['content'])
                if isinstance(parsed, list):
                    print(f"[StreamingWorker]  Parsed string content to {len(parsed)} blocks for message {idx}")
                    message['content'] = parsed
                else:
                    # JSON but not a list - convert to text block
                    print(f"[StreamingWorker]  Converting JSON to text block for message {idx}")
                    message['content'] = [{'type': 'text', 'text': str(parsed)}]
            except (json.JSONDecodeError, TypeError):
                # Not JSON - wrap in text block (BOTH user and assistant)
                print(f"[StreamingWorker]  Converting plain string to text block for {message['role']} message {idx}")
                message['content'] = [{'type': 'text', 'text': message['content']}]
        
        # Ensure content is always a list
        if not isinstance(message.get('content'), list):
            print(f"[StreamingWorker]  WARNING: Message {idx} content is not a list - wrapping")
            message['content'] = [{'type': 'text', 'text': str(message.get('content', ''))}]
        
        # ============================================================
        # STEP 2: VALIDATE ASSISTANT MESSAGE BLOCKS
        # ============================================================
        if message['role'] == 'assistant':
            valid_blocks = []
            has_thinking = False
            
            for block_idx, block in enumerate(message['content']):
                if not isinstance(block, dict):
                    print(f"[StreamingWorker]  WARNING: Skipping non-dict block {block_idx} in message {idx}")
                    continue
                
                block_type = block.get('type')
                
                # RULE 1: tool_result FORBIDDEN in assistant messages
                if block_type == 'tool_result':
                    print(f"[StreamingWorker]  ERROR: Removing tool_result from assistant message {idx} (API violation)")
                    continue
                
                # RULE 2: Validate thinking blocks
                if block_type in ('thinking', 'redacted_thinking'):
                    if 'thinking' not in block or not isinstance(block.get('thinking'), str):
                        print(f"[StreamingWorker]  WARNING: Invalid thinking block {block_idx} - missing 'thinking' field")
                        continue
                    # RULE 2a: Ensure signature field exists (extended thinking)
                    if 'signature' not in block:
                        print(f"[StreamingWorker]  WARNING: Adding missing 'signature' field to thinking block {block_idx}")
                        block['signature'] = ''
                    has_thinking = True
                
                # RULE 3: Validate text blocks
                elif block_type == 'text':
                    if 'text' not in block or not isinstance(block.get('text'), str):
                        print(f"[StreamingWorker]  WARNING: Invalid text block {block_idx} - missing 'text' field")
                        continue
                
                # RULE 4: Validate tool_use blocks
                elif block_type == 'tool_use':
                    if not all(k in block for k in ['id', 'name', 'input']):
                        print(f"[StreamingWorker]  WARNING: Invalid tool_use block {block_idx} - missing required fields")
                        continue
                
                # Block is valid
                valid_blocks.append(block)
            
            message['content'] = valid_blocks
            
            # Skip if all blocks invalid
            if not message['content']:
                print(f"[StreamingWorker]  WARNING: Skipping message {idx} - all blocks invalid")
                continue
            
            # RULE 5: Reorder - thinking MUST be first if it exists
            if has_thinking:
                first_block_type = message['content'][0].get('type')
                
                print(f"[StreamingWorker] Message {idx} (assistant): {len(message['content'])} blocks")
                print(f"[StreamingWorker]   First block: {first_block_type}")
                print(f"[StreamingWorker]   Has thinking: YES")
                
                if first_block_type not in ('thinking', 'redacted_thinking'):
                    print(f"[StreamingWorker]  CRITICAL FIX: Reordering blocks - moving thinking to first position")
                    
                    # Separate thinking from other blocks
                    thinking_blocks = [b for b in message['content'] if b.get('type') in ('thinking', 'redacted_thinking')]
                    other_blocks = [b for b in message['content'] if b.get('type') not in ('thinking', 'redacted_thinking')]
                    
                    # Reorder: thinking first
                    message['content'] = thinking_blocks + other_blocks
                    print(f"[StreamingWorker]   Reordered: {len(thinking_blocks)} thinking + {len(other_blocks)} other blocks")
                    print(f"[StreamingWorker]   New first block: {message['content'][0].get('type')}")
            else:
                print(f"[StreamingWorker] Message {idx} (assistant): {len(message['content'])} blocks, no thinking")
        
        # ============================================================
        # STEP 3: VALIDATE USER MESSAGE BLOCKS
        # ============================================================
        elif message['role'] == 'user':
            # Find last assistant message with tool_use (look backwards through validated messages)
            has_tool_use_before = False
            for prev_msg in reversed(messages):
                if prev_msg.get('role') == 'assistant':
                    prev_content = prev_msg.get('content', [])
                    has_tool_use_before = any(
                        b.get('type') == 'tool_use' for b in prev_content if isinstance(b, dict)
                    )
                    break  # Found assistant, stop looking
                elif prev_msg.get('role') == 'user':
                    # Another user message before assistant - definitely orphaned
                    break
            
            valid_blocks = []
            for block_idx, block in enumerate(message['content']):
                if not isinstance(block, dict):
                    print(f"[StreamingWorker]  WARNING: Skipping non-dict block {block_idx} in user message {idx}")
                    continue
                
                # RULE 6: Remove orphaned tool_result blocks
                if block.get('type') == 'tool_result' and not has_tool_use_before:
                    print(f"[StreamingWorker]  WARNING: Removing orphaned tool_result from user message {idx}")
                    continue
                
                valid_blocks.append(block)
            
            message['content'] = valid_blocks
            
            # Skip if all blocks removed
            if not message['content']:
                print(f"[StreamingWorker]  WARNING: Skipping message {idx} - all blocks orphaned")
                continue
        
        # ============================================================
        # STEP 4: CHECK FOR DUPLICATE CONSECUTIVE ROLES
        # ============================================================
        if messages and messages[-1].get('role') == message['role']:
            print(f"[StreamingWorker]  WARNING: Duplicate {message['role']} message at index {idx}")
            
            # Merge content blocks instead of creating duplicate role
            if isinstance(messages[-1].get('content'), list) and isinstance(message.get('content'), list):
                print(f"[StreamingWorker]  Merging {len(message['content'])} blocks into previous {message['role']} message")
                messages[-1]['content'].extend(message['content'])
                continue
            else:
                # Can't merge - skip this message
                print(f"[StreamingWorker]  ERROR: Cannot merge messages - skipping message {idx}")
                continue
        
        # ============================================================
        # STEP 5: ADD VALIDATED MESSAGE
        # ============================================================
        messages.append(message)
    
    print(f"[StreamingWorker]  Validated history: {len(messages)} valid messages")
    
    # ============================================================
    # STEP 6: ADD NEW USER PROMPT (FIRST ROUND ONLY)
    # ============================================================
    if user_prompt and is_first_round:
        messages.append({
            'role': 'user',
            'content': user_prompt
        })
    
    # ============================================================
    # STEP 7: PRESERVE ATTACHMENT CONTENT BLOCKS
    # ============================================================
    # User messages may contain arrays of content blocks (text + document/image blocks)
    for msg in messages:
        if msg['role'] == 'user' and isinstance(msg.get('content'), list):
            # Already has content blocks - attachments preserved
            print(f"[StreamingWorker] User message has {len(msg['content'])} content blocks (includes attachments)")
    
    return messages

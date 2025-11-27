"""
Combined Agent Worker - Unified and Fixed
Combines agent_worker.py + streaming_agent_worker.py with all critical fixes

CRITICAL FIXES APPLIED (Nov 7, 2025):
1. ✅ Thinking block ordering (must be first if present)
2. ✅ tool_result blocks removed from assistant messages
3. ✅ Orphaned tool_result detection (backwards search through ALL messages)
4. ✅ String content converted to blocks (both user and assistant)
5. ✅ Signature field validation for thinking blocks
6. ✅ Duplicate consecutive role detection and merging
7. ✅ Block field validation (text.text, tool_use.id, etc.)

UNIFIED EXPORTS:
- run_agent_worker() - Background worker with file support
- run_simple_agent_worker() - Synchronous text-only worker
- agent_worker() - CLI chat worker
- execute_streaming_request() - Multi-round streaming

USAGE:
    from core.combined_agent_worker import run_agent_worker, agent_worker
"""

import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Generator
from queue import Queue
import threading


# ============================================================
# SHARED VALIDATION FUNCTIONS (Used by all workers)
# ============================================================

def validate_and_reorder_assistant_content(content: List[Dict]) -> tuple[List[Dict], List[Dict]]:
    """
    Comprehensive validation and reordering for assistant message content
    
    CRITICAL ANTHROPIC API RULES:
    1. If thinking blocks exist, first block MUST be 'thinking' or 'redacted_thinking'
    2. tool_result blocks are FORBIDDEN in assistant messages (only in user messages)
    3. Thinking blocks must have 'thinking' field (string) and 'signature' field
    4. Text blocks must have 'text' field (string)
    5. tool_use blocks must have 'id', 'name', 'input' fields
    6. CRITICAL: Every tool_use.id MUST have a matching tool_result.tool_use_id in the next user message
    
    Args:
        content: List of content blocks from assistant message
    
    Returns:
        Tuple of (validated_content, extracted_tool_results)
        - validated_content: Assistant blocks (thinking, tool_use, text)
        - extracted_tool_results: tool_result blocks that were incorrectly in assistant message
    
    CRITICAL FIX (Nov 18, 2025):
    - Verify tool_use IDs match tool_result IDs
    - If mismatch detected, return EMPTY to truncate conversation
    - Prevents API error: "tool_use ids were found without tool_result blocks"
    """
    if not isinstance(content, list) or not content:
        return content, []
    
    # STEP 1: Validate and filter blocks, extract tool_result blocks
    validated_blocks = []
    extracted_tool_results = []
    tool_use_ids = []  # Track tool_use IDs for verification
    
    for block in content:
        if not isinstance(block, dict):
            print(f"[Combined Worker] ⚠️ Skipping non-dict block")
            continue
        
        block_type = block.get('type')
        
        # RULE 1: tool_result blocks are FORBIDDEN in assistant messages
        # BUT we need to extract and preserve them for proper conversation structure
        if block_type == 'tool_result':
            print(f"[Combined Worker] ⚠️ Extracting tool_result from assistant message (will be moved to user message)")
            extracted_tool_results.append(block)
            continue
        
        # Track tool_use IDs for verification
        if block_type == 'tool_use':
            tool_use_id = block.get('id')
            if tool_use_id:
                tool_use_ids.append(tool_use_id)
        
        # RULE 2: Validate thinking blocks
        if block_type in ('thinking', 'redacted_thinking'):
            if 'thinking' not in block or not isinstance(block.get('thinking'), str):
                print(f"[Combined Worker] ⚠️ Removing invalid thinking block (missing 'thinking' field)")
                continue
            
            # RULE 2a: Signature field validation (Extended Thinking)
            # NOTE: For old messages without signatures, we OMIT the field entirely
            # (empty string is INVALID per Anthropic API)
            print(f"[Combined Worker] 🔍 Thinking block validation:")
            print(f"  - Has 'signature' key: {'signature' in block}")
            if 'signature' in block:
                sig_value = block['signature']
                sig_preview = str(sig_value)[:20] + '...' if len(str(sig_value)) > 20 else str(sig_value)
                print(f"  - Signature value: {repr(sig_preview)} (type: {type(sig_value).__name__})")
                print(f"  - Is empty string: {sig_value == ''}")
                print(f"  - Is None: {sig_value is None}")
                print(f"  - Is falsy: {not sig_value}")
            
            # If signature exists but is empty string, remove it
            if 'signature' in block and block['signature'] == '':
                print(f"[Combined Worker] ⚠️ Removing invalid empty signature field")
                del block['signature']
                print(f"[Combined Worker] ✅ Signature field removed, block now has keys: {list(block.keys())}")
        
        # RULE 3: Validate text blocks
        elif block_type == 'text':
            if 'text' not in block or not isinstance(block.get('text'), str):
                print(f"[Combined Worker] ⚠️ Removing invalid text block (missing 'text' field)")
                continue
            
            # CRITICAL FIX (Nov 19, 2025): Filter empty text blocks
            # Empty text blocks between tool_use blocks cause API error:
            # "tool_use ids were found without tool_result blocks"
            text_content = block.get('text', '').strip()
            if not text_content:
                print(f"[Combined Worker] ⚠️ Removing empty text block (would break tool_use/tool_result pairing)")
                continue
        
        # RULE 4: Validate tool_use blocks
        elif block_type == 'tool_use':
            if not all(k in block for k in ['id', 'name', 'input']):
                print(f"[Combined Worker] ⚠️ Removing invalid tool_use block (missing required fields)")
                continue
        
        validated_blocks.append(block)
    
    if not validated_blocks:
        # CRITICAL FIX (Nov 22, 2025): Always return tuple of (content, tool_results)
        # When all blocks are invalid, return empty lists for both
        return [], []
    
    # STEP 2: Check if there are any thinking blocks
    has_thinking = any(
        block.get('type') in ('thinking', 'redacted_thinking')
        for block in validated_blocks
    )
    
    # CRITICAL FIX (Nov 12, 2025 - Updated per Anthropic SDK docs):
    # Per official Anthropic documentation:
    # "The Claude API automatically ignores thinking blocks from previous turns"
    # "You do not need to remove previous thinking blocks yourself"
    # "It is only strictly necessary to send back thinking blocks when using tools with extended thinking"
    #
    # IMPORTANT: We should NOT create fake thinking blocks with fake signatures!
    # Signatures are cryptographic and must be generated by Claude, not us.
    # The API will handle missing thinking blocks from previous turns automatically.
    #
    # Therefore: Just return validated blocks as-is. The API will:
    # 1. Strip thinking blocks from previous turns automatically
    # 2. Only require thinking blocks in the CURRENT turn (which Claude generates)
    # 3. Handle conversation history correctly without our intervention
    
    if not has_thinking:
        print(f"[Combined Worker] ℹ️  No thinking blocks in message (this is OK - API handles it)")
    
    # STEP 3: CRITICAL ID VERIFICATION (Nov 18, 2025 FIX)
    # Verify that extracted tool_result IDs match the tool_use IDs
    # This prevents API error: "tool_use ids were found without tool_result blocks"
    if tool_use_ids and extracted_tool_results:
        tool_result_ids = [tr.get('tool_use_id') for tr in extracted_tool_results]
        
        print(f"[Combined Worker]  CRITICAL ID VERIFICATION:")
        print(f"  - tool_use IDs in assistant: {tool_use_ids}")
        print(f"  - tool_result IDs extracted: {tool_result_ids}")
        
        # Check for ID mismatch (tool_use without matching tool_result)
        missing_results = []
        for tool_use_id in tool_use_ids:
            if tool_use_id not in tool_result_ids:
                missing_results.append(tool_use_id)
        
        if missing_results:
            print(f"[Combined Worker] ❌ CRITICAL ERROR: tool_use IDs without matching tool_result:")
            print(f"  - Missing tool_results for: {missing_results}")
            print(f"  - This WILL cause API error: 'tool_use ids were found without tool_result blocks'")
            print(f"[Combined Worker] 🔧 FIX: Returning EMPTY to truncate conversation at this malformed message")
            # Return empty lists - this will cause the message to be skipped
            # and conversation will be truncated to before this malformed message
            return [], []
        
        # Check for extra tool_results (results without matching tool_use)
        extra_results = []
        for tool_result_id in tool_result_ids:
            if tool_result_id not in tool_use_ids:
                extra_results.append(tool_result_id)
        
        if extra_results:
            print(f"[Combined Worker] ⚠️ WARNING: tool_result IDs without matching tool_use:")
            print(f"  - Extra tool_results for: {extra_results}")
            print(f"[Combined Worker] 🔧 FIX: Removing orphaned tool_results")
            # Remove tool_results that don't have matching tool_use
            extracted_tool_results = [tr for tr in extracted_tool_results if tr.get('tool_use_id') in tool_use_ids]
            print(f"  - Kept {len(extracted_tool_results)} matching tool_results")
        
        print(f"[Combined Worker] ✅ ID VERIFICATION PASSED: All tool_use IDs have matching tool_results")
    
    # STEP 4: Check if first block is already thinking
    first_block_type = validated_blocks[0].get('type')
    if first_block_type in ('thinking', 'redacted_thinking'):
        return validated_blocks, extracted_tool_results  # Already correct order
    
    # STEP 5: Reorder: thinking blocks first, then others
    thinking_blocks = [
        b for b in validated_blocks 
        if b.get('type') in ('thinking', 'redacted_thinking')
    ]
    other_blocks = [
        b for b in validated_blocks 
        if b.get('type') not in ('thinking', 'redacted_thinking')
    ]
    
    print(f"[Combined Worker] 🔧 Reordered: {len(thinking_blocks)} thinking + {len(other_blocks)} other blocks")
    return thinking_blocks + other_blocks, extracted_tool_results


def validate_user_content(content: List[Dict], messages: List[Dict]) -> List[Dict]:
    """
    Validate user message content (check for orphaned tool_results)
    
    Args:
        content: List of content blocks from user message
        messages: Previous validated messages (to check for tool_use)
    
    Returns:
        Validated content with orphaned tool_results removed
    """
    if not isinstance(content, list) or not content:
        return content
    
    # Extract tool_result blocks from current message
    tool_result_blocks = [b for b in content if isinstance(b, dict) and b.get('type') == 'tool_result']
    
    # If no tool_result blocks, no validation needed
    if not tool_result_blocks:
        return content
    
    # Look backwards to find tool_use blocks that these tool_results should match
    expected_tool_use_ids = set()
    found_assistant = False
    
    for prev_msg in reversed(messages):
        if prev_msg.get('role') == 'assistant':
            prev_content = prev_msg.get('content', [])
            # Collect all tool_use IDs from this assistant message
            tool_use_ids = [
                b.get('id') for b in prev_content 
                if isinstance(b, dict) and b.get('type') == 'tool_use' and b.get('id')
            ]
            expected_tool_use_ids.update(tool_use_ids)
            found_assistant = True
            break  # Stop at first assistant message
        elif prev_msg.get('role') == 'user':
            # Another user message before assistant - definitely orphaned
            break
    
    # If no assistant message found or no tool_use blocks, tool_results are orphaned
    if not found_assistant or not expected_tool_use_ids:
        print(f"[Combined Worker] ⚠️ Found {len(tool_result_blocks)} tool_result blocks but no prior tool_use blocks")
        print(f"[Combined Worker] 🔧 Converting orphaned tool_result blocks to text blocks (preserving context)")
        
        # CRITICAL FIX (Nov 21, 2025): Don't remove tool_result blocks - convert to text
        # This happens when threads are dragged between agents and tool_results appear as user messages
        validated_blocks = []
        for block in content:
            if not isinstance(block, dict):
                validated_blocks.append(block)
                continue
            
            if block.get('type') == 'tool_result':
                # Convert tool_result to text block
                tool_use_id = block.get('tool_use_id', 'unknown_id')
                result_content = block.get('content', '')
                
                # If content is a list of blocks, extract text
                if isinstance(result_content, list):
                    text_parts = []
                    for c in result_content:
                        if isinstance(c, dict) and c.get('type') == 'text':
                            text_parts.append(c.get('text', ''))
                        elif isinstance(c, str):
                            text_parts.append(c)
                    result_content = '\n'.join(text_parts)
                
                # Create text block with tool context
                text_block = {
                    'type': 'text',
                    'text': f"[Previous Tool Result - ID: {tool_use_id}]\n{result_content}"
                }
                validated_blocks.append(text_block)
                print(f"[Combined Worker]   → Converted tool_result (ID: {tool_use_id}) to text block")
            else:
                validated_blocks.append(block)
        
        return validated_blocks
    
    # Validate each tool_result has a matching tool_use
    validated_blocks = []
    for block in content:
        if not isinstance(block, dict):
            print(f"[Combined Worker] ⚠️ Skipping non-dict block in user message")
            continue
        
        if block.get('type') == 'tool_result':
            tool_use_id = block.get('tool_use_id')
            if tool_use_id in expected_tool_use_ids:
                validated_blocks.append(block)
            else:
                print(f"[Combined Worker] ⚠️ Removing orphaned tool_result (tool_use_id={tool_use_id} not found in previous assistant message)")
        else:
            validated_blocks.append(block)
    
    return validated_blocks


def normalize_content_to_blocks(content: Any, role: str) -> List[Dict]:
    """
    Normalize content to list of blocks format
    
    Handles:
    - Plain strings → [{"type": "text", "text": content}]
    - JSON strings → Parse and validate
    - Already blocks → Return as-is
    
    Args:
        content: Content in any format
        role: Message role (for logging)
    
    Returns:
        List of content blocks
    """
    # Already a list of blocks
    if isinstance(content, list):
        return content
    
    # Plain string
    if isinstance(content, str):
        # Try parsing as JSON first
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                print(f"[Combined Worker] 🔧 Parsed JSON string to {len(parsed)} blocks ({role})")
                return parsed
            else:
                # JSON but not a list - wrap in text block
                print(f"[Combined Worker] 🔧 Converting JSON value to text block ({role})")
                return [{'type': 'text', 'text': str(parsed)}]
        except (json.JSONDecodeError, TypeError):
            # Not JSON - wrap in text block
            print(f"[Combined Worker] 🔧 Converting plain string to text block ({role})")
            return [{'type': 'text', 'text': content}]
    
    # Unknown format - convert to text block
    print(f"[Combined Worker] ⚠️ Unknown content type ({type(content)}) - converting to text ({role})")
    return [{'type': 'text', 'text': str(content)}]


def validate_conversation_history(conversation_history: List[Dict]) -> List[Dict]:
    """
    Comprehensive validation of conversation history
    
    Fixes ALL 7 critical issues:
    1. Thinking block ordering
    2. tool_result in assistant messages
    3. Orphaned tool_results
    4. String to block conversion
    5. Signature field validation
    6. Duplicate consecutive roles
    7. Block field validation
    
    Args:
        conversation_history: Raw conversation history
    
    Returns:
        Validated and fixed conversation history
    """
    messages = []
    
    print(f"[Combined Worker] 🔍 Validating {len(conversation_history)} messages...")
    
    # DEBUG: Log conversation structure BEFORE validation
    for idx, msg in enumerate(conversation_history):
        role = msg.get('role')
        content = msg.get('content', [])
        if isinstance(content, list):
            block_types = [b.get('type') for b in content if isinstance(b, dict)]
            print(f"[Combined Worker]   Message {idx} ({role}): {block_types}")
    
    for idx, msg in enumerate(conversation_history):
        message = {
            'role': msg.get('role'),
            'content': msg.get('content')
        }
        
        # STEP 1: Normalize content to blocks
        message['content'] = normalize_content_to_blocks(message['content'], message['role'])
        
        # STEP 2: Validate based on role
        if message['role'] == 'assistant':
            # Log block types BEFORE validation
            before_types = [b.get('type') for b in message['content'] if isinstance(b, dict)]
            print(f"[Combined Worker] 🔍 Validating assistant message {idx}:")
            print(f"  - Before validation: {before_types}")
            
            # Log signature fields in thinking blocks
            for i, block in enumerate(message['content']):
                if isinstance(block, dict) and block.get('type') == 'thinking':
                    print(f"  - Thinking block {i} before validation:")
                    print(f"    - Keys: {list(block.keys())}")
                    print(f"    - Has signature: {'signature' in block}")
                    if 'signature' in block:
                        sig_preview = str(block['signature'])[:20] + '...' if len(str(block['signature'])) > 20 else str(block['signature'])
                        print(f"    - Signature value: {repr(sig_preview)}")
            
            # CRITICAL: Extract tool_result blocks that don't belong in assistant messages
            message['content'], extracted_tool_results = validate_and_reorder_assistant_content(message['content'])
            
            # Log block types AFTER validation
            after_types = [b.get('type') for b in message['content'] if isinstance(b, dict)]
            print(f"  - After validation: {after_types}")
            
            # Log signature fields in thinking blocks AFTER validation
            for i, block in enumerate(message['content']):
                if isinstance(block, dict) and block.get('type') == 'thinking':
                    print(f"  - Thinking block {i} after validation:")
                    print(f"    - Keys: {list(block.keys())}")
                    print(f"    - Has signature: {'signature' in block}")
                    if 'signature' in block:
                        sig_preview = str(block['signature'])[:20] + '...' if len(str(block['signature'])) > 20 else str(block['signature'])
                        print(f"    - Signature value: {repr(sig_preview)}")
            
            if before_types != after_types:
                print(f"[Combined Worker] 🔧 Message {idx} (assistant) reordered:")
                print(f"    Before: {before_types}")
                print(f"    After:  {after_types}")
            
            # Skip if all blocks were invalid
            if not message['content']:
                print(f"[Combined Worker] ⚠️ Skipping message {idx} - all blocks invalid")
                continue
            
            # CRITICAL FIX (Nov 21, 2025): Skip empty/whitespace-only assistant messages
            # These are often placeholder messages from streaming that got saved incorrectly
            has_real_content = False
            for block in message['content']:
                if isinstance(block, dict):
                    if block.get('type') == 'text':
                        text_content = block.get('text', '').strip()
                        if text_content:
                            has_real_content = True
                            break
                    elif block.get('type') in ('thinking', 'tool_use', 'image'):
                        has_real_content = True
                        break
            
            if not has_real_content:
                print(f"[Combined Worker] 🚫 Skipping message {idx} - assistant message has no real content (only whitespace)")
                continue
            
            # CRITICAL FIX: If we extracted tool_result blocks, insert them as a user message AFTER this assistant
            if extracted_tool_results:
                print(f"[Combined Worker] 🔧 Inserting {len(extracted_tool_results)} extracted tool_result blocks as user message")
                # Add the assistant message first
                messages.append(message)
                # Then add a user message with the extracted tool_results
                messages.append({'role': 'user', 'content': extracted_tool_results})
                continue  # Skip the normal append at the end
        
        elif message['role'] == 'user':
            message['content'] = validate_user_content(message['content'], messages)
            
            # Skip if all blocks were removed
            if not message['content']:
                print(f"[Combined Worker] ⚠️ Skipping message {idx} - all blocks orphaned")
                continue
        
        # STEP 3: Check for duplicate consecutive roles
        if messages and messages[-1].get('role') == message['role']:
            print(f"[Combined Worker] ⚠️ Duplicate {message['role']} message at index {idx}")
            
            # CRITICAL FIX (Nov 21, 2025): NEVER merge assistant messages with tool_use blocks
            # Anthropic requires tool_use to be LAST blocks in assistant message
            if message['role'] == 'assistant':
                prev_content = messages[-1].get('content', [])
                has_tool_use = any(
                    isinstance(b, dict) and b.get('type') == 'tool_use' 
                    for b in prev_content
                )
                
                current_content = message.get('content', [])
                current_has_tool_use = any(
                    isinstance(b, dict) and b.get('type') == 'tool_use'
                    for b in current_content
                )
                
                # If EITHER message has tool_use blocks, DON'T merge
                if has_tool_use or current_has_tool_use:
                    print(f"[Combined Worker] 🚫 Cannot merge assistant messages - tool_use blocks present")
                    print(f"  → Previous message has tool_use: {has_tool_use}")
                    print(f"  → Current message has tool_use: {current_has_tool_use}")
                    # Don't merge - keep as separate messages by skipping to append
                    messages.append(message)
                    continue
            
            # Merge content blocks (safe for text-only messages)
            if isinstance(messages[-1].get('content'), list) and isinstance(message.get('content'), list):
                print(f"[Combined Worker] 🔧 Merging {len(message['content'])} blocks into previous message")
                messages[-1]['content'].extend(message['content'])
                
                # CRITICAL: If merging assistant messages, reorder thinking blocks to first
                if message['role'] == 'assistant':
                    print(f"[Combined Worker] 🔧 Re-validating merged assistant content")
                    merged_content, extracted_tool_results = validate_and_reorder_assistant_content(messages[-1]['content'])
                    messages[-1]['content'] = merged_content
                    
                    # If we extracted tool_results during merge, insert as user message
                    if extracted_tool_results:
                        print(f"[Combined Worker] 🔧 Inserting {len(extracted_tool_results)} extracted tool_result blocks as user message after merge")
                        messages.append({'role': 'user', 'content': extracted_tool_results})
                
                continue
            else:
                print(f"[Combined Worker] ⚠️ Cannot merge - skipping message {idx}")
                continue
        
        # STEP 4: Add validated message
        messages.append(message)
    
    print(f"[Combined Worker] ✅ Validated: {len(messages)} valid messages")
    
    # DEBUG: Log final conversation structure AFTER validation
    print(f"[Combined Worker] 📋 Final conversation structure:")
    for idx, msg in enumerate(messages):
        role = msg.get('role')
        content = msg.get('content', [])
        if isinstance(content, list):
            block_types = [b.get('type') for b in content if isinstance(b, dict)]
            print(f"[Combined Worker]   Message {idx} ({role}): {block_types}")
            
            # Special check: If assistant with tool_use, check next message has tool_result
            if role == 'assistant':
                tool_use_ids = [b.get('id') for b in content if isinstance(b, dict) and b.get('type') == 'tool_use']
                if tool_use_ids:
                    print(f"[Combined Worker]     → {len(tool_use_ids)} tool_use blocks: {tool_use_ids[:3]}{'...' if len(tool_use_ids) > 3 else ''}")
                    
                    # Check if next message is user with tool_result
                    if idx + 1 < len(messages):
                        next_msg = messages[idx + 1]
                        if next_msg.get('role') == 'user':
                            next_content = next_msg.get('content', [])
                            tool_result_ids = [b.get('tool_use_id') for b in next_content if isinstance(b, dict) and b.get('type') == 'tool_result']
                            print(f"[Combined Worker]     → Next user message has {len(tool_result_ids)} tool_result blocks")
                            
                            # Check for missing tool_results
                            missing_ids = set(tool_use_ids) - set(tool_result_ids)
                            if missing_ids:
                                print(f"[Combined Worker]     ⚠️ MISSING tool_result for IDs: {list(missing_ids)[:3]}{'...' if len(missing_ids) > 3 else ''}")
                                print(f"[Combined Worker]     🚨 CRITICAL: Truncating conversation at message {idx} to prevent API error!")
                                print(f"[Combined Worker]     → Orphaned tool_use blocks cannot be sent to Claude")
                                print(f"[Combined Worker]     → Keeping only messages 0-{idx-1} (before the problematic assistant message)")
                                # CRITICAL FIX: Truncate conversation BEFORE the message with orphaned tool_use
                                messages = messages[:idx]
                                print(f"[Combined Worker]     ✅ Truncated to {len(messages)} messages")
                                return messages  # Return immediately with truncated conversation
                        else:
                            print(f"[Combined Worker]     ⚠️ Next message is {next_msg.get('role')}, not user with tool_result!")
                            print(f"[Combined Worker]     🚨 CRITICAL: Truncating conversation at message {idx} to prevent API error!")
                            # Truncate to exclude this assistant message
                            messages = messages[:idx]
                            print(f"[Combined Worker]     ✅ Truncated to {len(messages)} messages")
                            return messages
                    else:
                        print(f"[Combined Worker]     ⚠️ No next message - tool_use blocks are orphaned!")
                        print(f"[Combined Worker]     🚨 CRITICAL: Truncating conversation at message {idx} to prevent API error!")
                        # Truncate to exclude this assistant message
                        messages = messages[:idx]
                        print(f"[Combined Worker]     ✅ Truncated to {len(messages)} messages")
                        return messages
    
    return messages


def ensure_thinking_on_final_assistant(messages: List[Dict], thinking_enabled: bool) -> List[Dict]:
    """
    CRITICAL FIX (Nov 12, 2025 - Anthropic API Requirement):
    
    When thinking is enabled, the API requires that the FINAL assistant message
    in the conversation history starts with a thinking block.
    
    Per Anthropic docs:
    "When `thinking` is enabled, a final `assistant` message must start with a thinking block."
    "During tool use, you must pass thinking blocks back to the API for the last assistant message."
    
    UPDATED (Nov 12, 2025): We now preserve all messages instead of deleting them.
    The presence of the `thinking` parameter in the API call is sufficient for Claude
    to generate thinking blocks in the response, even if prior assistant messages lack them.
    
    Args:
        messages: Validated conversation history
        thinking_enabled: Whether extended thinking is enabled for this request
    
    Returns:
        Conversation history (preserved, no deletions)
    """
    if not thinking_enabled:
        return messages  # No requirement when thinking disabled
    
    if not messages:
        return messages  # Empty conversation
    
    # Find the last assistant message
    last_assistant_idx = None
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get('role') == 'assistant':
            last_assistant_idx = i
            break
    
    if last_assistant_idx is None:
        # No assistant messages in history
        print(f"[Combined Worker] ℹ️  No assistant messages in history (thinking requirement N/A)")
        return messages
    
    last_assistant = messages[last_assistant_idx]
    content = last_assistant.get('content', [])
    
    if not isinstance(content, list):
        print(f"[Combined Worker] ⚠️ Last assistant message has non-list content")
        return messages
    
    # Check if first block is thinking
    has_thinking_first = False
    if content:
        first_block_type = content[0].get('type') if isinstance(content[0], dict) else None
        has_thinking_first = first_block_type in ('thinking', 'redacted_thinking')
    
    if has_thinking_first:
        print(f"[Combined Worker] ✅ Last assistant message (#{last_assistant_idx}) starts with thinking block")
    else:
        # Last assistant message doesn't have thinking blocks - this is OK
        # The API will generate thinking blocks when `thinking` param is present
        print(f"[Combined Worker] ℹ️  Last assistant message (#{last_assistant_idx}) has no thinking blocks (API will generate them)")
        print(f"[Combined Worker]   Content blocks: {[b.get('type') for b in content if isinstance(b, dict)]}")
    
    # Always preserve all messages
    return messages


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text
    
    Uses simple heuristic: ~4 characters per token
    This is a rough approximation but sufficient for pruning decisions
    
    Args:
        text: Text to estimate tokens for
    
    Returns:
        Estimated token count
    """
    if not text:
        return 0
    return len(str(text)) // 4


def truncate_tool_result(result: any, max_tokens: int = 1000) -> tuple[str, int, int]:
    """
    Truncate large tool results to prevent context explosion
    
    Strategy:
    1. Convert result to string
    2. Estimate token count
    3. If over limit, truncate with summary
    4. Return truncated result + token counts (original, final)
    
    Args:
        result: Tool execution result (any type)
        max_tokens: Maximum tokens to keep (default: 1000)
    
    Returns:
        Tuple of (truncated_string, original_tokens, final_tokens)
    """
    result_str = str(result)
    original_tokens = estimate_tokens(result_str)
    
    if original_tokens <= max_tokens:
        return result_str, original_tokens, original_tokens
    
    # Calculate max characters to keep
    max_chars = max_tokens * 4
    
    # Truncate with ellipsis and summary
    truncated = result_str[:max_chars]
    summary = f"\n\n[TRUNCATED: Original {original_tokens} tokens, showing first {max_tokens} tokens. Full result available but not shown to save context.]"
    
    final_result = truncated + summary
    final_tokens = estimate_tokens(final_result)
    
    return final_result, original_tokens, final_tokens


def _inject_session_status(
    tool_result_str: str,
    iteration: int,
    max_iterations: int,
    cumulative_tokens: int,
    conversation_tokens: int,
    tool_name: str = ""
) -> str:
    """
    Inject session status into tool result with context-aware guidance
    
    Provides AI with real-time awareness of:
    - Current iteration round
    - Token usage (tool results + conversation)
    - Percentage of 200K limit used
    - Smart guidance based on usage thresholds
    
    Args:
        tool_result_str: Original tool result string
        iteration: Current iteration number
        max_iterations: Maximum allowed iterations
        cumulative_tokens: Cumulative tool result tokens
        conversation_tokens: Estimated conversation size tokens
        tool_name: Name of tool being executed (for context)
    
    Returns:
        Tool result with session status footer appended
    """
    # Calculate totals and percentages
    total_tokens = cumulative_tokens + conversation_tokens
    token_limit = 200000
    percentage = (total_tokens / token_limit) * 100
    
    # Determine status level and guidance
    if total_tokens < 50000:  # < 25%
        status_emoji = "🟢"
        status_text = "NORMAL"
        guidance = (
            "💡 EARLY STAGE - You have plenty of context space.\n"
            "   → Work freely, explore options, gather information\n"
            "   → No need to optimize yet"
        )
    elif total_tokens < 100000:  # 25-50%
        status_emoji = "🟢"
        status_text = "NORMAL"
        guidance = (
            "💡 COMFORTABLE ZONE - Still plenty of space remaining.\n"
            "   → Continue working normally\n"
            "   → Consider organizing findings if working on large tasks"
        )
    elif total_tokens < 150000:  # 50-75%
        status_emoji = "🟡"
        status_text = "CAUTION"
        guidance = (
            "⚠️  APPROACHING LIMIT - Start optimizing context usage:\n"
            "   → Summarize long results before continuing\n"
            "   → Consider creating Synergy session for important data\n"
            "   → Update user on progress so far\n"
            "   → Focus on completing current task efficiently"
        )
    elif total_tokens < 180000:  # 75-90%
        status_emoji = "🔴"
        status_text = "CRITICAL"
        guidance = (
            "🚨 CRITICAL - Context almost full! Take action NOW:\n"
            "   → CREATE SYNERGY SESSION immediately (use synergy_create_session)\n"
            "   → Move all findings/documents to Synergy cards\n"
            "   → Summarize progress in current response\n"
            "   → Prepare for conversation reset after next response\n"
            "   → Inform user you're approaching limits"
        )
    else:  # 90-100%
        status_emoji = "🔴"
        status_text = "EMERGENCY"
        guidance = (
            "🆘 EMERGENCY - Out of space! Final actions only:\n"
            "   → IMMEDIATELY create Synergy session if not done\n"
            "   → Provide final summary to user NOW\n"
            "   → Document all critical info in Synergy\n"
            "   → This may be your last response before cutoff\n"
            "   → DO NOT start new complex tasks"
        )
    
    # Build status footer
    status_footer = f"""\n
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SESSION STATUS (Round {iteration}/{max_iterations})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tokens Used: {total_tokens:,} / {token_limit:,} ({percentage:.1f}%)
  └─ Tool Results: {cumulative_tokens:,} tokens
  └─ Conversation: {conversation_tokens:,} tokens
Rounds Completed: {iteration}/{max_iterations}
Status: {status_emoji} {status_text}

{guidance}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    return tool_result_str + status_footer


def smart_truncate_tool_result(result: Any, tool_name: str, max_tokens: int = 2000) -> str:
    """
    Context-aware truncation for tool results
    
    TOKEN LIMITS BY INTENT:
    1. META-TOOLS (list_available_platforms, etc.) → NEVER TRUNCATED (tool discovery)
    2. INTENTIONAL reads (read_file, get_document, download) → 60K tokens (240KB)
    3. BULK queries (list, search, get_all) → 2K tokens (8KB)
    4. Single records (get_by_id, find_one) → 10K tokens (40KB)
    5. Unknown tools → 40K tokens (160KB) - Allow larger results
    
    This prevents:
    - Blocking legitimate document reads (user asks "read this 100-page report")
    - Allowing accidental bulk dumps (Xero returns 1000 clients unexpectedly)
    - Truncating tool discovery results (list_platform_tools needs full catalog)
    
    Args:
        result: Tool execution result (any type)
        tool_name: Name of tool (for context-aware limits)
        max_tokens: Default maximum tokens (overridden by tool type)
    
    Returns:
        Truncated result string suitable for Claude API
    """
    # META-TOOLS: NEVER truncate (required for tool discovery and navigation)
    META_TOOLS_NO_TRUNCATE = [
        'list_available_platforms',
        'list_platform_tools',
        'get_tool_schema',
        'search_tools',
        'get_platform_guide',
        'recommend_tools_for_task',
        'get_workflow_steps'
    ]
    
    if tool_name in META_TOOLS_NO_TRUNCATE:
        print(f"[Combined Worker] 🔷 META-TOOL '{tool_name}' - NO TRUNCATION (tool discovery)")
        # Return full result with metadata
        if isinstance(result, str):
            result_str = result
        else:
            try:
                result_str = json.dumps(result, indent=2)
            except:
                result_str = str(result)
        
        estimated_tokens = len(result_str) // 4
        metadata_header = f"[METADATA: {estimated_tokens} tokens, {len(result_str)} bytes, tool={tool_name}, truncated=False, type=META_TOOL]\n\n"
        return metadata_header + result_str
    
    # STEP 1: Determine tool intent and set appropriate limits
    tool_lower = tool_name.lower()
    
    # INTENTIONAL LARGE READS - Allow up to 60K tokens (~240KB)
    # These are explicit user requests for full content (1-3 files typically)
    intentional_read_keywords = [
        'read_file', 'get_file', 'download', 'fetch_document',
        'get_document', 'read_document', 'get_content', 'fetch_content',
        'export', 'get_attachment', 'download_attachment'
    ]
    
    # BULK/LIST OPERATIONS - Strict 2K token limit
    # These often return unexpected volumes
    bulk_query_keywords = [
        'list', 'get_all', 'search', 'query', 'find_all',
        'list_accounts', 'get_contacts', 'get_invoices', 'list_items',
        'get_transactions', 'list_messages', 'get_threads'
    ]
    
    # SINGLE RECORD OPERATIONS - Medium 10K token limit
    # Usually one record but could be complex
    single_record_keywords = [
        'get_by_id', 'find_one', 'get_account', 'get_invoice',
        'get_message', 'get_thread', 'get_contact'
    ]
    
    # Determine limit based on tool type
    if any(keyword in tool_lower for keyword in intentional_read_keywords):
        max_tokens = 60000  # 240KB - Allow full documents (1-3 large files)
        truncate_aggressive = False
        intent = "INTENTIONAL_READ"
    elif any(keyword in tool_lower for keyword in bulk_query_keywords):
        max_tokens = 2000  # 8KB - Strict limit for bulk queries
        truncate_aggressive = True
        intent = "BULK_QUERY"
    elif any(keyword in tool_lower for keyword in single_record_keywords):
        max_tokens = 10000  # 40KB - Medium limit for single records
        truncate_aggressive = False
        intent = "SINGLE_RECORD"
    else:
        max_tokens = 40000  # 160KB - Allow larger results for unknown tools
        truncate_aggressive = False
        intent = "UNKNOWN"
    
    # Convert to string first
    if isinstance(result, str):
        result_str = result
    else:
        try:
            result_str = json.dumps(result, indent=2)
        except:
            result_str = str(result)
    
    # Calculate size (rough: 4 chars = 1 token)
    max_chars = max_tokens * 4
    estimated_tokens = len(result_str) // 4
    
    # If small enough, return as-is WITH TOKEN COUNT
    if len(result_str) <= max_chars:
        # Log successful result (no truncation needed)
        print(f"[Combined Worker] ✅ Tool result within limits:")
        print(f"  Tool: {tool_name}")
        print(f"  Intent: {intent}")
        print(f"  Size: {len(result_str):,} chars (~{estimated_tokens:,} tokens)")
        print(f"  Limit: {max_chars:,} chars (~{max_tokens:,} tokens)")
        print(f"  Status: No truncation needed")
        
        # Add metadata wrapper with token count for AI's awareness
        if isinstance(result, (dict, list)):
            return json.dumps({
                "_metadata": {
                    "estimated_tokens": estimated_tokens,
                    "size_bytes": len(result_str),
                    "tool_name": tool_name,
                    "intent": intent,
                    "truncated": False
                },
                "data": result
            }, indent=2)
        else:
            # For plain text/strings, prepend metadata comment
            metadata_header = f"[METADATA: {estimated_tokens} tokens, {len(result_str)} bytes, tool={tool_name}, truncated=False]\n\n"
            return metadata_header + result_str
    
    # LARGE RESULT - Need to truncate intelligently
    print(f"[Combined Worker] ⚠️  Large tool result detected:")
    print(f"  Tool: {tool_name}")
    print(f"  Intent: {intent}")
    print(f"  Size: {len(result_str):,} chars (~{estimated_tokens:,} tokens)")
    print(f"  Limit: {max_chars:,} chars (~{max_tokens:,} tokens)")
    print(f"  Action: {'Aggressive' if truncate_aggressive else 'Smart'} truncation")
    print(f"  Token reduction: {estimated_tokens:,} → ~{max_tokens:,} tokens ({100 - (max_tokens/estimated_tokens*100):.1f}% reduction)")
    
    # Handle different data types
    if isinstance(result, list):
        # LIST: Show sample + count
        # Aggressive: 10 items, Smart: 50 items, Intentional: 100 items
        if truncate_aggressive:
            page_size = 10
        elif intent == "INTENTIONAL_READ":
            page_size = 100
        else:
            page_size = 50
        
        # Build pagination guidance based on tool
        pagination_help = _get_pagination_guidance(tool_name, len(result))
        
        truncated = {
            "_metadata": {
                "estimated_tokens": len(json.dumps(result[:page_size])) // 4,
                "original_tokens": estimated_tokens,
                "size_bytes": len(result_str),
                "tool_name": tool_name,
                "intent": intent,
                "truncated": True
            },
            "result_type": "list",
            "total_items": len(result),
            "showing_items": min(page_size, len(result)),
            "sample_data": result[:page_size],
            "truncation_note": f"⚠️ Result truncated: Showing {min(page_size, len(result))} of {len(result)} items. Original result was ~{estimated_tokens:,} tokens.",
            "pagination_guidance": pagination_help
        }
        return json.dumps(truncated, indent=2)
    
    elif isinstance(result, dict):
        # DICT: Show structure + sample
        keys = list(result.keys())
        
        # Adjust sample size based on intent
        if truncate_aggressive:
            sample_size = 5
            value_preview = 100
        elif intent == "INTENTIONAL_READ":
            sample_size = 50
            value_preview = 1000
        else:
            sample_size = 20
            value_preview = 300
        
        sample_keys = keys[:sample_size]
        
        truncated = {
            "_metadata": {
                "estimated_tokens": len(json.dumps({k: result[k] for k in sample_keys})) // 4,
                "original_tokens": estimated_tokens,
                "size_bytes": len(result_str),
                "tool_name": tool_name,
                "intent": intent,
                "truncated": True
            },
            "result_type": "dict",
            "total_keys": len(keys),
            "showing_keys": len(sample_keys),
            "keys_list": sample_keys,
            "sample_data": {k: _truncate_value(result[k], value_preview) for k in sample_keys},
            "truncation_note": f"⚠️ Result truncated: Showing {len(sample_keys)} of {len(keys)} keys. Original result was ~{estimated_tokens:,} tokens.",
            "suggestion": "Access specific keys by name to see full values" if len(keys) > sample_size else None
        }
        return json.dumps(truncated, indent=2)
    
    else:
        # TEXT: For intentional reads, keep more content
        if intent == "INTENTIONAL_READ":
            # For document reads, show up to 150KB (better than 200KB to leave room for conversation)
            if len(result_str) > 600000:  # 150K tokens
                half = 300000  # Show 75K chars at start + 75K at end
                truncated = {
                    "result_type": "text",
                    "original_length": len(result_str),
                    "beginning": result_str[:half],
                    "ending": result_str[-half:],
                    "truncation_note": f"⚠️ Document extremely large ({len(result_str):,} chars). Showing beginning and ending sections. Consider processing in chunks.",
                    "tool_name": tool_name
                }
                return json.dumps(truncated, indent=2)
            else:
                # Keep full document if under 150K tokens
                return result_str
        else:
            # For other text, show beginning + ending
            half = max_chars // 2
            truncated = {
                "result_type": "text",
                "original_length": len(result_str),
                "beginning": result_str[:half],
                "ending": result_str[-half:],
                "truncation_note": f"⚠️ Text truncated from {len(result_str):,} to {max_chars:,} chars.",
                "tool_name": tool_name
            }
            return json.dumps(truncated, indent=2)


def _get_pagination_guidance(tool_name: str, total_items: int) -> dict:
    """
    Generate tool-specific pagination guidance
    
    Returns dict with:
    - parameters: List of pagination params the tool supports
    - example: Example usage with pagination
    - recommendation: Specific advice for this result size
    """
    tool_lower = tool_name.lower()
    
    # Common pagination patterns by platform
    if 'gmail' in tool_lower or 'google' in tool_lower:
        return {
            "parameters": ["max_results (default: 10, max: 100)", "page_token (for next page)"],
            "example": f"{tool_name}(max_results=50, page_token='...')",
            "recommendation": f"With {total_items} items, use max_results=100 and iterate with page_token"
        }
    elif 'xero' in tool_lower:
        return {
            "parameters": ["page (1-based)", "if_modified_since (date filter)", "where (filter expression)"],
            "example": f"{tool_name}(page=1, if_modified_since='2024-11-01')",
            "recommendation": f"With {total_items} items, add date filter: if_modified_since='2024-11-01' to reduce results"
        }
    elif 'microsoft' in tool_lower or 'outlook' in tool_lower:
        return {
            "parameters": ["top (page size, default: 10)", "skip (offset)", "filter (OData filter)"],
            "example": f"{tool_name}(top=50, skip=0, filter='receivedDateTime ge 2024-11-01')",
            "recommendation": f"With {total_items} items, use top=100 and filter by date"
        }
    elif 'stripe' in tool_lower:
        return {
            "parameters": ["limit (default: 10, max: 100)", "starting_after (cursor for next page)"],
            "example": f"{tool_name}(limit=100, starting_after='cus_...')",
            "recommendation": f"With {total_items} items, use limit=100 and iterate with starting_after cursor"
        }
    elif 'slack' in tool_lower:
        return {
            "parameters": ["limit (default: 100)", "cursor (for next page)"],
            "example": f"{tool_name}(limit=100, cursor='...')",
            "recommendation": f"With {total_items} items, results should already be paginated"
        }
    else:
        return {
            "parameters": ["Check tool schema with get_tool_schema('" + tool_name + "')"],
            "example": f"Call get_tool_schema('{tool_name}') to see available pagination parameters",
            "recommendation": f"With {total_items} items, look for limit/offset/page parameters in the tool schema"
        }


def _truncate_value(value: Any, max_length: int) -> Any:
    """Helper to truncate individual values"""
    if isinstance(value, str) and len(value) > max_length:
        return value[:max_length] + f"... ({len(value)} chars total)"
    elif isinstance(value, list) and len(value) > 5:
        return value[:5] + [f"... ({len(value)} items total)"]
    elif isinstance(value, dict) and len(value) > 5:
        keys = list(value.keys())[:5]
        return {k: value[k] for k in keys} | {"_truncated": f"{len(value)} keys total"}
    return value


def prune_conversation_for_context_limit(
    messages: List[Dict],
    max_estimated_tokens: int = 180000,
    preserve_first_user: bool = True
) -> List[Dict]:
    """
    Prune conversation history when approaching context limit
    
    Strategy:
    1. Keep the first user message (for original context)
    2. Keep the most recent N messages (current context)
    3. Remove older tool use rounds from the middle
    
    Args:
        messages: Full conversation history
        max_estimated_tokens: Maximum estimated tokens to keep (~180K for safety margin)
        preserve_first_user: Whether to preserve the first user message
    
    Returns:
        Pruned conversation history
    """
    if not messages:
        return messages
    
    # Rough estimation: 1 message ≈ 500 tokens average
    # (assistant with thinking can be 2000+, tool results can be 1000+)
    estimated_tokens_per_message = 800
    max_messages = max_estimated_tokens // estimated_tokens_per_message
    
    # If we're under the limit, no need to prune
    if len(messages) <= max_messages:
        return messages
    
    print(f"[Combined Worker] ⚠️  Conversation pruning needed:")
    print(f"  Current: {len(messages)} messages (~{len(messages) * estimated_tokens_per_message} tokens)")
    print(f"  Target: {max_messages} messages (~{max_estimated_tokens} tokens)")
    
    # Strategy: Keep first + last N messages
    # This preserves original context and recent conversation
    
    if preserve_first_user and messages[0].get('role') == 'user':
        # Keep first user message
        first_message = [messages[0]]
        # Calculate how many recent messages we can keep
        remaining_budget = max_messages - 1
        # Keep the most recent messages
        recent_messages = messages[-remaining_budget:] if remaining_budget > 0 else []
        
        pruned = first_message + recent_messages
        pruned_count = len(messages) - len(pruned)
        
        print(f"[Combined Worker] 🔧 Pruned {pruned_count} messages from middle")
        print(f"  Kept: First message + {len(recent_messages)} recent messages")
        print(f"  Result: {len(pruned)} messages (~{len(pruned) * estimated_tokens_per_message} estimated tokens)")
        
        return pruned
    else:
        # Just keep the most recent messages
        pruned = messages[-max_messages:]
        pruned_count = len(messages) - len(pruned)
        
        print(f"[Combined Worker] 🔧 Pruned {pruned_count} older messages")
        print(f"  Kept: {len(pruned)} recent messages")
        print(f"  Result: ~{len(pruned) * estimated_tokens_per_message} estimated tokens")
        
        return pruned


# ============================================================
# LEGACY HELPER FUNCTIONS (For backward compatibility)
# ============================================================

def strip_thinking_blocks(content: List[Dict]) -> List[Dict]:
    """
    DISABLED (Nov 12, 2025 - Per Anthropic SDK Documentation)
    
    Per official Anthropic docs:
    "The Claude API automatically ignores thinking blocks from previous turns"
    "You do not need to remove previous thinking blocks yourself"
    
    Thinking blocks MUST be preserved when:
    1. Using tools with extended thinking (required for reasoning continuity)
    2. Storing conversation history (for proper context)
    
    The signature field contains encrypted thinking and verifies authenticity.
    We cannot create fake signatures - they must come from Claude's response.
    
    Returns: content unchanged (preserves thinking blocks)
    """
    if not isinstance(content, list):
        return content
    
    # CRITICAL: Return content unchanged - let API handle thinking blocks
    return content


def prepare_content_for_storage(content: List[Dict]) -> List[Dict]:
    """
    UPDATED (Nov 12, 2025): Keep thinking blocks in storage
    
    Keeps: thinking blocks, text blocks, tool_use blocks
    Removes: tool_result blocks (those go in user messages)
    """
    if not isinstance(content, list):
        return content
    
    return [
        block for block in content
        if block.get('type') in ('thinking', 'redacted_thinking', 'text', 'tool_use')
    ]


# Alias for backward compatibility (returns only content, ignores extracted tool_results)
def reorder_assistant_content_blocks(content: List[Dict]) -> List[Dict]:
    """Backward compatibility wrapper - returns only validated content"""
    validated_content, _ = validate_and_reorder_assistant_content(content)
    return validated_content


# ============================================================
# WORKER IMPLEMENTATIONS
# ============================================================

# Add calculator module path to import ToolUseAgent
calculator_module_path = os.path.join(os.path.dirname(__file__), '..', '..', 'UI', 'external', 'modules', 'calculator-module', 'ORIGINAL')
sys.path.insert(0, calculator_module_path)

# Import REAL ToolUseAgent from calculator module (optional)
try:
    from tool_use_agent import ToolUseAgent
    TOOL_USE_AGENT_AVAILABLE = True
    print("[Combined Worker] ToolUseAgent imported - Quote Calculator tools available")
except ImportError:
    TOOL_USE_AGENT_AVAILABLE = False
    print("[Combined Worker] Quote Calculator module not found (optional)")
    
    # Fallback placeholder
    class ToolUseAgent:
        """Placeholder - using registry_v3 tools only"""
        def __init__(self, config_path=None):
            self.tools = []
        def _get_tool_definitions(self):
            return []
        def execute_tool(self, tool_name, tool_input):
            return {"status": "Tool execution via unified_ai_client", "tool": tool_name}


def run_agent_worker(
    agent_id: str,
    prompt: str,
    file_data: List[Dict[str, Any]],
    lock: threading.Lock,
    session_id: str,
    queue: Queue,
    conversation_history: Optional[List[Dict]] = None,
    context: str = 'triple_agent',
    user_id: Optional[int] = None,
    thread_id: Optional[str] = None
):
    """
    Background worker that executes ToolUseAgent (with file support)
    
    Args:
        agent_id: Agent identifier
        prompt: User prompt text
        file_data: List of file dicts with {filename, content_type, data (bytes)}
        lock: threading.Lock for thread safety
        session_id: Session ID
        queue: Queue for SSE events
        conversation_history: Previous conversation (will be validated)
        context: UI context
        user_id: User ID for OAuth credential injection
    """
    if user_id is None:
        user_id = 1
    
    log_prefix = f"[Combined Worker {agent_id}]"
    
    try:
        print("\n\n" + "=" * 100)
        print(f"🚀 NEW REQUEST STARTED - run_agent_worker")
        print("=" * 100)
        print(f"Session: {session_id[:8]}")
        print(f"Agent: {agent_id}")
        print(f"User ID: {user_id}")
        print(f"Files: {len(file_data)}")
        print(f"Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Prompt: {prompt}")
        print("=" * 100 + "\n")
        
        # Validate conversation history (fixes all 7 issues)
        if conversation_history:
            conversation_history = validate_conversation_history(conversation_history)
        
        # Save files to storage and collect metadata
        from utils.file_storage import save_uploaded_file, FileStorageError
        
        file_metadata = []
        content_blocks = []
        
        for file_info in file_data:
            filename = file_info.get('filename', 'unknown')
            content_type = file_info.get('content_type', 'application/octet-stream')
            file_bytes = file_info.get('data', b'')
            
            # Save file to storage and get metadata
            try:
                metadata = save_uploaded_file(
                    file_data=file_bytes,
                    filename=filename,
                    content_type=content_type,
                    user_id=user_id,
                    thread_id=thread_id
                )
                file_metadata.append(metadata)
                print(f"{log_prefix} Saved file: {filename} -> {metadata['server_path']}")
            except FileStorageError as e:
                print(f"{log_prefix} Failed to save file {filename}: {e}")
                queue.put({'type': 'error', 'error': f"Failed to save file: {str(e)}"})
                return
            
            import base64
            encoded_data = base64.b64encode(file_bytes).decode('utf-8')
            
            if content_type == 'application/pdf':
                block_type = 'document'
            elif content_type.startswith('image/'):
                block_type = 'image'
            else:
                block_type = 'document'
            
            content_blocks.append({
                'type': block_type,
                'source': {
                    'type': 'base64',
                    'media_type': content_type,
                    'data': encoded_data
                }
            })
            
            print(f"{log_prefix} Added {block_type} to content: {filename}")
        
        # Add text prompt
        if prompt:
            content_blocks.append({'type': 'text', 'text': prompt})
        elif not content_blocks:
            queue.put({'type': 'error', 'error': 'No prompt or files provided'})
            return
        
        print(f"{log_prefix} Initializing ToolUseAgent...")
        
        def log_callback(log_entry: dict):
            """Stream ToolUseAgent logs to SSE queue"""
            event_type = log_entry.get('type', 'log')
            
            if event_type == 'thinking':
                queue.put({'type': 'thinking', 'content': log_entry.get('content', '')})
            elif event_type == 'tool_use':
                queue.put({'type': 'tool_use', 'tool_name': log_entry.get('tool_name', ''), 'input': log_entry.get('input', {})})
            elif event_type == 'tool_result':
                queue.put({'type': 'tool_result', 'tool_name': log_entry.get('tool_name', ''), 'output': log_entry.get('output', '')})
            elif event_type == 'response':
                queue.put({'type': 'response', 'content': log_entry.get('content', '')})
            elif event_type == 'error':
                queue.put({'type': 'error', 'error': log_entry.get('error', '')})
        
        try:
            config_path = 'config/database-config.json'
            agent = ToolUseAgent(config_path, log_callback=log_callback)
            
            queue.put({'type': 'thinking', 'content': 'Processing with Tool Use API...'})
            
            result = agent.process_request(
                customer_message=prompt,
                max_turns=20,
                conversation_history=conversation_history,
                content_blocks=content_blocks if file_data else None
            )
            
            if result.get('success'):
                final_response = result.get('final_response', '')
                
                queue.put({'type': 'response', 'content': final_response})
                complete_payload = {
                    'type': 'complete',
                    'result': final_response,
                    'session_id': session_id,
                    'tool_calls': result.get('tool_calls', 0),
                    'thinking_tokens': result.get('thinking_tokens', 0),
                    'file_metadata': file_metadata  # Include file metadata for saving
                }
                if thread_id is not None:
                    complete_payload['thread_id'] = thread_id
                queue.put(complete_payload)
                
                print(f"{log_prefix} Complete")
            else:
                error_msg = result.get('error', 'Unknown error')
                queue.put({'type': 'error', 'error': error_msg})
            
            agent.close()
            
        except Exception as e:
            print(f"{log_prefix} ToolUseAgent error: {e}")
            import traceback
            traceback.print_exc()
            queue.put({'type': 'error', 'error': str(e)})
        
    except Exception as e:
        print(f"{log_prefix} Worker error: {e}")
        import traceback
        traceback.print_exc()
        queue.put({'type': 'error', 'error': str(e)})
    
    finally:
        try:
            lock.release()
        except Exception as e:
            print(f"{log_prefix} Lock release error: {e}")


def run_simple_agent_worker(
    agent_id: str,
    prompt: str,
    lock: threading.Lock,
    session_id: str,
    queue: Queue,
    conversation_history: Optional[List[Dict]] = None,
    ai_client = None,
    user_id: int = 1,
    thread_id: Optional[str] = None
):
    """
    Simplified worker for text-only prompts (no files)
    
    USES: Validated conversation history (all 7 fixes applied)
    
    Args:
        agent_id: Agent identifier
        prompt: User prompt text
        lock: threading.Lock
        session_id: Session ID
        queue: Queue for SSE events
        conversation_history: Previous conversation (will be validated)
        ai_client: UnifiedAIClient instance
        user_id: User ID for OAuth credential injection
    """
    log_prefix = f"[Combined Simple {agent_id}]"
    
    try:
        print("\n\n" + "=" * 100)
        print(f"🚀 NEW REQUEST STARTED - run_simple_agent_worker")
        print("=" * 100)
        print(f"Session: {session_id[:8]}")
        print(f"Agent: {agent_id}")
        print(f"User ID: {user_id}")
        print(f"Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Prompt: {prompt}")
        print("=" * 100 + "\n")
        
        if ai_client is None:
            raise ValueError("ai_client is required but not provided")
        
        # Load tools from registry
        from tools import registry_v3
        registry = registry_v3.get_registry()
        
        # Just-in-time schema loading
        conversation_length = len(conversation_history or [])
        
        meta_tool_names = [
            'list_available_platforms',
            'list_platform_tools',
            'get_tool_schema',
            'get_platform_guide',
            'recommend_tools_for_task'
        ]
        
        all_tools_dict = {t['name']: t for t in registry.get_anthropic_tools()}
        tools = [all_tools_dict[name] for name in meta_tool_names if name in all_tools_dict]
        
        print(f"{log_prefix} 🔷 Sending {len(tools)} meta-tools")
        
        # Get system prompt
        prompt_name = 'data_agent_chat'
        system_prompt = ai_client.get_system_prompt(prompt_name)
        
        # Build messages with VALIDATED history
        # CRITICAL FIX: conversation_history ALREADY includes the current user message
        # (added in agent_routes_v4.py line 538), so DON'T append it again!
        messages = []
        if conversation_history:
            print(f"{log_prefix} 🔍 Validating {len(conversation_history)} messages from history...")
            print(f"{log_prefix} Last message role: {conversation_history[-1].get('role') if conversation_history else 'N/A'}")
            print(f"{log_prefix} Last message content: {str(conversation_history[-1].get('content', ''))[:100] if conversation_history else 'N/A'}...")
            
            # CRITICAL: Use comprehensive validation (fixes all 7 issues)
            messages = validate_conversation_history(conversation_history)
            
            # CRITICAL: Ensure last assistant message has thinking blocks (if thinking enabled)
            messages = ensure_thinking_on_final_assistant(messages, thinking_enabled=True)
            
            print(f"{log_prefix} ✅ Validated: {len(messages)} valid messages")
            print(f"{log_prefix} ✅ Current user message ALREADY in history - NOT appending duplicate!")
        else:
            # No history - add current prompt as first message
            messages.append({'role': 'user', 'content': prompt})
            print(f"{log_prefix} ✅ No history - added current prompt as first message")
        
        # CRITICAL FIX (Nov 27, 2025): Strip server tool blocks before sending to API
        # Server-side tool blocks (server_tool_use and their result blocks) cause 400 errors 
        # when replayed because result blocks require tool_use_id references that are removed
        # NOTE: Result blocks are already stored in DB and visible in UI - no data loss
        print(f"{log_prefix} 🧹 Cleaning conversation: Removing server-side tool blocks...")
        try:
            for idx, msg in enumerate(messages):
                if msg.get('role') == 'assistant':
                    content = msg.get('content', [])
                    if isinstance(content, list):
                        original_count = len(content)
                        # Filter out ALL server-side tool blocks (both requests and results)
                        # These blocks are for display only and shouldn't be replayed to API
                        cleaned_content = [
                            block for block in content
                            if not (isinstance(block, dict) and block.get('type') in [
                                'server_tool_use',           # Server tool request
                                'web_search_tool_result',    # Web search result
                                'web_fetch_tool_result'      # Web fetch result
                            ])
                        ]
                        
                        if len(cleaned_content) < original_count:
                            removed = original_count - len(cleaned_content)
                            print(f"{log_prefix}   Message [{idx}]: Removed {removed} server tool blocks")
                            messages[idx]['content'] = cleaned_content
                        
                        # SAFETY CHECK: If ALL blocks were removed, skip this message entirely
                        if len(cleaned_content) == 0:
                            print(f"{log_prefix}   ⚠️ Message [{idx}]: ALL blocks removed - will skip empty message")
        except Exception as cleaning_error:
            # CRITICAL: If cleaning fails, log error but continue with original messages
            # This prevents conversation from stalling due to cleaning logic errors
            print(f"{log_prefix} ⚠️ Error during cleaning: {cleaning_error}")
            print(f"{log_prefix} ⚠️ Continuing with original messages (uncleaned)")
        
        # SAFETY: Remove any assistant messages that became empty after cleaning
        messages = [msg for msg in messages if not (
            msg.get('role') == 'assistant' and 
            isinstance(msg.get('content'), list) and 
            len(msg.get('content', [])) == 0
        )]
        
        # CRITICAL SAFETY CHECK: Ensure we have at least the user message
        if not messages:
            print(f"{log_prefix} ⚠️ All messages removed during cleaning - adding current prompt")
            messages.append({'role': 'user', 'content': prompt})
        
        print(f"{log_prefix} ✅ Final message count after cleaning: {len(messages)} messages")
        
        # Call AI with tools
        response = ai_client.create_message(
            messages=messages,
            provider='anthropic',
            model='claude-sonnet-4-5-20250929',
            max_tokens=16000,
            system=system_prompt,
            tools=tools,
            enable_thinking=True,
            thinking_budget=5000,
            enable_web_search=True,
            enable_web_fetch=True
        )
        
        # Extract response
        response_text = ''
        tool_uses = []
        
        if isinstance(response, dict) and 'content' in response:
            for block in response['content']:
                if block.get('type') == 'thinking':
                    queue.put({'type': 'thinking_block', 'content': block.get('thinking', '')})
                elif block.get('type') == 'text':
                    response_text += block.get('text', '')
                elif block.get('type') == 'tool_use':
                    tool_uses.append(block)
        
        # Tool execution loop (with validation)
        max_tool_iterations = 20
        tool_iteration = 0
        current_response = response
        cumulative_tool_result_tokens = 0
        
        while (tool_uses and current_response.get('stop_reason') == 'tool_use' and 
               tool_iteration < max_tool_iterations):
            
            tool_iteration += 1
            print(f"{log_prefix} 🔧 Tool iteration {tool_iteration}: {len(tool_uses)} tool(s)")
            
            if tool_iteration == 1 and response_text:
                queue.put({'type': 'content_delta', 'text': response_text})
            
            # Execute tools
            tool_results = []
            iteration_token_count = 0
            
            for tool_use in tool_uses:
                tool_name = tool_use.get('name')
                tool_input = tool_use.get('input', {})
                tool_id = tool_use.get('id')
                
                queue.put({'type': 'tool_use', 'tool_name': tool_name, 'tool_input': tool_input})
                
                try:
                    # Execute tool
                    if tool_name in ['get_tool_schema', 'execute_tool']:
                        from tools.implementations.meta_tools import execute_tool as execute_tool_fn, get_tool_schema as get_tool_schema_fn
                        
                        if tool_name == 'execute_tool':
                            result = execute_tool_fn(**tool_input, _user_id=user_id, _injected_credentials=True)
                        else:
                            result = get_tool_schema_fn(**tool_input)
                    else:
                        tool_input_copy = {k: v for k, v in tool_input.items() if k != 'tool_name'}
                        
                        if tool_name.startswith(('google_', 'microsoft_')):
                            result = registry.execute_tool(
                                tool_name=tool_name,
                                _user_id=user_id,
                                _injected_credentials=True,
                                **tool_input_copy
                            )
                        else:
                            result = registry.execute_tool(tool_name=tool_name, **tool_input_copy)
                    
                    # Smart truncation based on tool type (with META-TOOLS exemption)
                    # Use smart_truncate_tool_result which exempts meta-tools from truncation
                    result_str = smart_truncate_tool_result(result, tool_name=tool_name, max_tokens=2000)
                    
                    # Estimate tokens for tracking
                    original_tokens = estimate_tokens(str(result))
                    final_tokens = estimate_tokens(result_str)
                    iteration_token_count += final_tokens
                    
                    # INJECT SESSION STATUS into tool result (Option B)
                    # This gives AI passive awareness of token usage and iteration progress
                    conversation_size_estimate = estimate_tokens(str(conversation_history))
                    result_str = _inject_session_status(
                        tool_result_str=result_str,
                        iteration=tool_iteration,
                        max_iterations=max_tool_iterations,
                        cumulative_tokens=cumulative_tool_result_tokens + iteration_token_count,
                        conversation_tokens=conversation_size_estimate,
                        tool_name=tool_name
                    )
                    # Re-estimate tokens after status injection (adds ~50-100 tokens)
                    final_tokens = estimate_tokens(result_str)
                    
                    # Log tool success with colored formatting (show both original and final if truncated)
                    from utils.logger_config import log_tool_success
                    if original_tokens > final_tokens:
                        print(f"  [TRUNCATED: {original_tokens:,} -> {final_tokens:,} tokens]")
                    log_tool_success(tool_name, final_tokens)
                    
                    queue.put({'type': 'tool_result', 'tool_name': tool_name, 'result': result, 'success': True})
                    
                    tool_results.append({
                        'type': 'tool_result',
                        'tool_use_id': tool_id,
                        'content': result_str  # Use truncated + status-injected version
                    })
                    
                except Exception as tool_error:
                    error_str = f"Error: {str(tool_error)}"
                    error_tokens = estimate_tokens(error_str)
                    iteration_token_count += error_tokens
                    
                    # Log tool failure with colored formatting
                    from utils.logger_config import log_tool_failure
                    log_tool_failure(tool_name, str(tool_error), error_tokens)
                    
                    queue.put({'type': 'tool_result', 'tool_name': tool_name, 'result': str(tool_error), 'success': False})
                    
                    tool_results.append({
                        'type': 'tool_result',
                        'tool_use_id': tool_id,
                        'content': error_str,
                        'is_error': True
                    })
            
            # Log total tokens for this iteration
            cumulative_tool_result_tokens += iteration_token_count
            print(f"{log_prefix} 📊 ITERATION {tool_iteration} TOTAL: {iteration_token_count:,} tokens from {len(tool_results)} tool result(s)")
            print(f"{log_prefix} 📊 CUMULATIVE TOOL RESULTS: {cumulative_tool_result_tokens:,} tokens across {tool_iteration} iteration(s)")
            
            # CRITICAL: Validate assistant content before adding to messages
            content = current_response.get('content', [])
            # validate_and_reorder_assistant_content returns (validated_content, extracted_tool_results)
            validated_content, extracted_tool_results = validate_and_reorder_assistant_content(content)

            # Add validated content to messages
            messages.append({'role': 'assistant', 'content': validated_content})
            
            # CRITICAL FIX (Nov 23, 2025): IMMEDIATELY save assistant message with tool_use to database
            # This prevents orphaned tool_use blocks when errors occur before 'complete' event
            if thread_id:
                print(f"{log_prefix} 💾 IMMEDIATE SAVE: Assistant message with tool_use")
                from routes.agent_routes_v4 import save_message_to_database
                save_success = save_message_to_database(
                    thread_slug=thread_id,
                    role='assistant',
                    content=validated_content,
                    user_id=user_id,
                    model='claude-sonnet-4-5-20250929',
                    metadata={'round': tool_iteration, 'has_tool_use': True}
                )
                if save_success:
                    print(f"{log_prefix} ✅ Assistant message saved immediately")
                else:
                    print(f"{log_prefix} ⚠️ Failed to save assistant message immediately")
            
            # If there are extracted tool_results, insert them as a user message immediately after
            if extracted_tool_results:
                messages.append({'role': 'user', 'content': extracted_tool_results})
            messages.append({'role': 'user', 'content': tool_results})
            
            # CRITICAL FIX (Nov 23, 2025): IMMEDIATELY save tool_result message to database
            # This prevents orphaned tool_use blocks when errors occur
            if thread_id:
                print(f"{log_prefix} 💾 IMMEDIATE SAVE: Tool result message")
                save_success = save_message_to_database(
                    thread_slug=thread_id,
                    role='user',
                    content=tool_results,
                    user_id=user_id,
                    metadata={'round': tool_iteration, 'tool_results': True}
                )
                if save_success:
                    print(f"{log_prefix} ✅ Tool results saved immediately")
                else:
                    print(f"{log_prefix} ⚠️ Failed to save tool results immediately")
            
            # CRITICAL FIX: Re-validate entire message history before next API call
            # This prevents "text block before thinking block" errors from propagating
            print(f"{log_prefix} 🔍 Re-validating entire history before round {tool_iteration + 1}...")
            messages = validate_conversation_history(messages)
            
            # CRITICAL: Ensure last assistant message has thinking blocks (if thinking enabled)
            messages = ensure_thinking_on_final_assistant(messages, thinking_enabled=True)
            
            # Estimate conversation size before API call
            conversation_tokens = 0
            for msg in messages:
                content = msg.get('content', '')
                if isinstance(content, str):
                    conversation_tokens += estimate_tokens(content)
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict):
                            if 'text' in block:
                                conversation_tokens += estimate_tokens(block['text'])
                            elif 'thinking' in block:
                                conversation_tokens += estimate_tokens(block['thinking'])
                            elif 'content' in block:
                                conversation_tokens += estimate_tokens(str(block['content']))
            
            print(f"{log_prefix} ✅ History validated: {len(messages)} messages")
            print(f"{log_prefix} 📊 ESTIMATED CONVERSATION SIZE: {conversation_tokens:,} tokens (~{conversation_tokens/200000*100:.1f}% of 200K limit)")
            
            # Get next response
            current_response = ai_client.create_message(
                messages=messages,
                provider='anthropic',
                model='claude-sonnet-4-5-20250929',
                max_tokens=16000,
                system=system_prompt,
                tools=tools,
                enable_thinking=True,
                thinking_budget=5000,
                enable_web_search=True,
                enable_web_fetch=True
            )
            
            # Extract new tool_uses
            tool_uses = []
            if isinstance(current_response, dict) and 'content' in current_response:
                for block in current_response['content']:
                    if block.get('type') == 'tool_use':
                        tool_uses.append(block)
        
        # Send final response
        if tool_iteration > 0:
            final_text = ''
            final_content = []
            if isinstance(current_response, dict) and 'content' in current_response:
                final_content = current_response['content']
                for block in final_content:
                    if block.get('type') == 'text':
                        final_text += block.get('text', '')
            
            if final_text:
                queue.put({'type': 'content_delta', 'text': final_text})
                response_text += final_text
            
            # CRITICAL FIX (Nov 23, 2025): IMMEDIATELY save final assistant message to database
            if thread_id and final_content:
                print(f"{log_prefix} 💾 IMMEDIATE SAVE: Final assistant message")
                from routes.agent_routes_v4 import save_message_to_database
                validated_final_content, _ = validate_and_reorder_assistant_content(final_content)
                save_success = save_message_to_database(
                    thread_slug=thread_id,
                    role='assistant',
                    content=validated_final_content,
                    user_id=user_id,
                    model='claude-sonnet-4-5-20250929',
                    metadata={'final_response': True, 'rounds': tool_iteration}
                )
                if save_success:
                    print(f"{log_prefix} ✅ Final assistant message saved immediately")
                else:
                    print(f"{log_prefix} ⚠️ Failed to save final assistant message")
        else:
            if response_text:
                queue.put({'type': 'content_delta', 'text': response_text})
            
            # CRITICAL FIX (Nov 23, 2025): IMMEDIATELY save assistant response (no tools used)
            if thread_id and response.get('content'):
                print(f"{log_prefix} 💾 IMMEDIATE SAVE: Assistant message (no tools)")
                from routes.agent_routes_v4 import save_message_to_database
                validated_content, _ = validate_and_reorder_assistant_content(response['content'])
                save_success = save_message_to_database(
                    thread_slug=thread_id,
                    role='assistant',
                    content=validated_content,
                    user_id=user_id,
                    model='claude-sonnet-4-5-20250929',
                    metadata={'direct_response': True}
                )
                if save_success:
                    print(f"{log_prefix} ✅ Assistant message saved immediately")
                else:
                    print(f"{log_prefix} ⚠️ Failed to save assistant message")
        
        complete_payload = {'type': 'complete', 'result': response_text, 'session_id': session_id}
        if thread_id is not None:
            complete_payload['thread_id'] = thread_id
        queue.put(complete_payload)
        
        print(f"{log_prefix} Complete")
        
    except Exception as e:
        print(f"{log_prefix} Error: {e}")
        import traceback
        traceback.print_exc()
        queue.put({'type': 'error', 'error': str(e)})
    
    finally:
        try:
            lock.release()
        except:
            pass


def agent_worker(
    message: str,
    session_id: str,
    user_id: int,
    conversation_history: Optional[List[Dict]] = None,
    ai_client=None,
    attachments: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Synchronous agent worker for CLI chat endpoint
    
    USES: Validated conversation history (all 7 fixes applied)
    
    Args:
        message: User message
        session_id: Session ID
        user_id: User ID for OAuth credential lookup
        conversation_history: Previous messages (will be validated)
        ai_client: UnifiedAIClient instance
        attachments: List of file attachments
    
    Returns:
        Dict with response and tool_calls
    """
    from tools.registry_v3 import get_registry
    
    try:
        print("\n\n" + "=" * 100)
        print(f"🚀 NEW REQUEST STARTED - agent_worker (CLI)")
        print("=" * 100)
        print(f"Session: {session_id[:8]}")
        print(f"User ID: {user_id}")
        print(f"Message: {message[:100]}..." if len(message) > 100 else f"Message: {message}")
        print(f"History: {len(conversation_history) if conversation_history else 0} messages")
        print(f"Attachments: {len(attachments) if attachments else 0}")
        print("=" * 100 + "\n")
        
        registry = get_registry()
        tools = registry.get_anthropic_tools()
        
        # Validate conversation history (fixes all 7 issues)
        if conversation_history is None:
            conversation_history = []
        
        if conversation_history:
            conversation_history = validate_conversation_history(conversation_history)
        
        # Build user message with attachments
        user_message = {'role': 'user'}
        
        if attachments and len(attachments) > 0:
            content_blocks = [{'type': 'text', 'text': message}]
            
            for attachment in attachments:
                content_blocks.append({
                    'type': attachment.get('type', 'document'),
                    'source': {
                        'type': 'base64',
                        'media_type': attachment.get('media_type'),
                        'data': attachment.get('source', {}).get('data')
                    }
                })
            
            user_message['content'] = content_blocks
        else:
            user_message['content'] = message
        
        messages = conversation_history + [user_message]
        
        # Prune conversation if needed to avoid exceeding context limit
        # This prevents "prompt is too long: 231130 tokens > 200000 maximum" errors
        messages = prune_conversation_for_context_limit(
            messages,
            max_estimated_tokens=180000,  # Safety margin below 200K limit
            preserve_first_user=True
        )
        
        # ========================================================================
        # INTELLIGENT TOOL DISCOVERY - Get tool suggestions before AI call
        # ========================================================================
        try:
            from tools.intelligent_discovery import IntelligentToolSuggestion
            
            suggester = IntelligentToolSuggestion(registry)
            
            # Get tool suggestions with platform filtering
            suggested_tools, confidence = suggester.suggest_tools(
                query=message,
                conversation_history=conversation_history,
                user_id=user_id,  # Enable platform filtering
                top_k=10
            )
            
            # Log suggested tools to console
            print("\n" + "="*80)
            print("🎯 [INTELLIGENT TOOL SUGGESTIONS]")
            print("="*80)
            print(f"Query: '{message[:60]}{'...' if len(message) > 60 else ''}'")
            print(f"User ID: {user_id}")
            print(f"Confidence: {confidence:.0%}")
            print(f"\nTop 10 Suggested Tools:")
            print("-"*80)
            
            for i, tool in enumerate(suggested_tools, 1):
                tool_name = tool['tool_name']
                platform = tool['platform']
                final_score = tool['final_score']
                scoring = tool['scoring_breakdown']
                platform_boost = scoring.get('platform_boost', 1.0)
                
                # Format with alignment
                print(f"{i:2d}. {tool_name:<50} "
                      f"platform={platform:<20} "
                      f"score={final_score:6.2f} "
                      f"boost={platform_boost:.1f}x")
            
            print("="*80 + "\n")
            
        except Exception as discovery_error:
            print(f"⚠️ [Tool Discovery] Failed to get suggestions: {discovery_error}")
            # Continue without suggestions - don't block the request
        
        # Build system prompt
        system_prompt = """You are a helpful AI assistant with access to tools.

You can use tools to help the user complete tasks."""
        
        # Call AI
        response = ai_client.create_message(
            messages=messages,
            tools=tools,
            max_tokens=4096,
            model='claude-sonnet-4-5-20250929',
            system=system_prompt
        )
        
        response_text = ''
        tool_calls = []
        content_blocks = response.get('content', [])
        
        # Process response
        for block in content_blocks:
            if block.get('type') == 'text':
                response_text += block.get('text', '')
            elif block.get('type') == 'tool_use':
                tool_name = block.get('name')
                tool_input = block.get('input', {})
                
                try:
                    if 'tool_name' in tool_input:
                        del tool_input['tool_name']
                    
                    if tool_name.startswith(('google_', 'microsoft_')):
                        result = registry.execute_tool(
                            tool_name=tool_name,
                            _user_id=user_id,
                            _injected_credentials=True,
                            **tool_input
                        )
                    else:
                        result = registry.execute_tool(tool_name=tool_name, **tool_input)
                    
                    tool_calls.append({'name': tool_name, 'success': True, 'result': result})
                except Exception as e:
                    tool_calls.append({'name': tool_name, 'success': False, 'error': str(e)})
        
        return {
            'response': response_text,
            'content_blocks': content_blocks,  # Full content with thinking blocks
            'tool_calls': tool_calls,
            'session_id': session_id
        }
        
    except Exception as e:
        print(f"❌ [Combined CLI Worker] Error: {e}")
        import traceback
        traceback.print_exc()
        raise


def execute_streaming_request(
    session_id: str,
    user_prompt: str,
    conversation_history: List[Dict],
    system_prompt: str,
    tools: List[Dict],
    user_id: Optional[int] = None,
    max_rounds: int = 30,
    current_round: int = 1,
    ai_model: str = 'claude-sonnet-4-5-20250929',
    ai_temperature: float = 1.0,
    ai_max_tokens: int = 16000,
    ai_thinking_enabled: bool = True,
    ai_thinking_budget: int = 10000
) -> Generator[Dict[str, Any], None, None]:
    """
    Execute streaming request with multi-round tool use
    
    FULL STREAMING IMPLEMENTATION with all validation fixes applied
    
    Args:
        session_id: Session identifier
        user_prompt: User's message
        conversation_history: Full conversation history (will be validated)
        system_prompt: System prompt for AI
        tools: List of tool definitions
        user_id: User ID for credential injection
        max_rounds: Maximum recursive rounds (safety limit)
        current_round: Current round number
    
    Yields:
        Dict: SSE events with type and data
    """
    log_prefix = f"[Stream Round {current_round}]"
    
    try:
        # Safety check: Prevent infinite loops
        if current_round > max_rounds:
            yield {
                'type': 'error',
                'error': f'Maximum rounds ({max_rounds}) exceeded',
                'session_id': session_id
            }
            return
        
        print("\n\n" + "=" * 100)
        print(f"🚀 NEW REQUEST STARTED - execute_streaming_request (Round {current_round})")
        print("=" * 100)
        print(f"Session: {session_id[:8]}")
        print(f"User ID: {user_id}")
        print(f"Prompt: {user_prompt[:100] if user_prompt else '(continuation)'}")
        print(f"History: {len(conversation_history)} messages")
        print(f"Tools: {len(tools)} available")
        print("=" * 100 + "\n")
        
        # CRITICAL: ALWAYS validate conversation history before API call (all rounds)
        # This ensures thinking blocks are first, even on recursive calls
        if conversation_history:
            print(f"{log_prefix} Validating {len(conversation_history)} messages before Round {current_round}...")
            conversation_history = validate_conversation_history(conversation_history)
            
            # CRITICAL: Ensure last assistant message has thinking blocks (if thinking enabled)
            conversation_history = ensure_thinking_on_final_assistant(conversation_history, thinking_enabled=ai_thinking_enabled)
            
            print(f"{log_prefix} Validation complete: {len(conversation_history)} messages ready")
        
        # Build messages
        messages = conversation_history.copy()
        
        # CRITICAL FIX: Validate that every tool_use has a corresponding tool_result
        # UPDATED (Nov 21, 2025): When thinking is enabled, DON'T remove assistant messages
        # Instead, preserve them to maintain thinking block structure required by Anthropic API
        # This prevents the "messages.5.content.0.type: Expected `thinking` or `redacted_thinking`" error
        for idx, msg in enumerate(messages):
            if msg.get('role') == 'assistant':
                content = msg.get('content', [])
                if isinstance(content, list):
                    tool_use_ids = [b.get('id') for b in content if isinstance(b, dict) and b.get('type') == 'tool_use']
                    
                    if tool_use_ids:
                        # Check if next message is user with matching tool_result blocks
                        if idx + 1 < len(messages):
                            next_msg = messages[idx + 1]
                            if next_msg.get('role') == 'user':
                                next_content = next_msg.get('content', [])
                                tool_result_ids = [b.get('tool_use_id') for b in next_content if isinstance(b, dict) and b.get('type') == 'tool_result']
                                
                                missing_ids = set(tool_use_ids) - set(tool_result_ids)
                                if missing_ids:
                                    # CRITICAL FIX (Nov 21, 2025): ALWAYS remove orphaned tool_use blocks
                                    # Orphaned tool_use ALWAYS causes 400 errors - must fix regardless of thinking mode
                                    print(f"{log_prefix} ❌ ERROR: Assistant message {idx} has tool_use blocks without matching tool_result:")
                                    print(f"{log_prefix}   tool_use IDs: {tool_use_ids}")
                                    print(f"{log_prefix}   tool_result IDs: {tool_result_ids}")
                                    print(f"{log_prefix}   Missing: {list(missing_ids)}")
                                    print(f"{log_prefix} 🔧 FIXING: Truncating conversation at message {idx} (thinking_enabled={ai_thinking_enabled})")
                                    messages = messages[:idx]
                                    break
                            else:
                                # CRITICAL FIX (Nov 21, 2025): ALWAYS fix incorrect message order
                                print(f"{log_prefix} ❌ ERROR: Assistant message {idx} has tool_use but next message is {next_msg.get('role')}, not user!")
                                print(f"{log_prefix} 🔧 FIXING: Truncating conversation at message {idx} (thinking_enabled={ai_thinking_enabled})")
                                messages = messages[:idx]
                                break
                        else:
                            # CRITICAL FIX (Nov 21, 2025): ALWAYS fix missing tool_result message
                            print(f"{log_prefix} ❌ ERROR: Assistant message {idx} has tool_use but no following message!")
                            print(f"{log_prefix} 🔧 FIXING: Truncating conversation at message {idx} (thinking_enabled={ai_thinking_enabled})")
                            messages = messages[:idx]
                            break
        
        # Add user prompt (only on round 1)
        if user_prompt and current_round == 1:
            # CRITICAL FIX (Nov 18, 2025): Check if last message is also user (consecutive roles)
            # If so, merge current prompt with last user message instead of appending
            if messages and messages[-1].get('role') == 'user':
                print(f"{log_prefix} ⚠️  Last message is also 'user' - merging current prompt instead of appending")
                print(f"{log_prefix} 🔧 Original last message content: {str(messages[-1].get('content', ''))[:100]}")
                
                # Get existing content
                existing_content = messages[-1].get('content', '')
                
                # Convert both to block format for consistent handling
                if isinstance(existing_content, str):
                    existing_blocks = [{'type': 'text', 'text': existing_content}]
                elif isinstance(existing_content, list):
                    existing_blocks = existing_content
                else:
                    existing_blocks = []
                
                # Add current prompt as new text block
                existing_blocks.append({'type': 'text', 'text': user_prompt})
                
                # Update the last message
                messages[-1]['content'] = existing_blocks
                
                print(f"{log_prefix} ✅ Merged current prompt into last user message ({len(existing_blocks)} total blocks)")
            else:
                # Normal case: last message is assistant, so we can append user message
                messages.append({'role': 'user', 'content': user_prompt})
                print(f"{log_prefix} ✅ Appended current prompt as new user message")
        
        # CRITICAL: Prune conversation if needed to avoid 413 error
        # This prevents "Request exceeds the maximum size" errors
        print(f"{log_prefix} Checking conversation size before API call...")
        messages = prune_conversation_for_context_limit(
            messages,
            max_estimated_tokens=170000,  # Safety margin below 200K limit
            preserve_first_user=True
        )
        
        # Initialize Anthropic client
        import os
        from anthropic import Anthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            yield {'type': 'error', 'error': 'ANTHROPIC_API_KEY not found'}
            return
        
        client = Anthropic(api_key=api_key, timeout=120.0, max_retries=3)
        
        # Track content blocks and stop reason
        all_content_blocks = []
        stop_reason = None
        tool_uses = []
        
        # Log user AI preferences
        print(f"{log_prefix} AI Settings from User Preferences:")
        print(f"  Model: {ai_model}")
        print(f"  Temperature: {ai_temperature}")
        print(f"  Max Tokens: {ai_max_tokens}")
        print(f"  Extended Thinking: {'Enabled' if ai_thinking_enabled else 'Disabled'}")
        if ai_thinking_enabled:
            print(f"  Thinking Budget: {ai_thinking_budget} tokens")
        
        # Build thinking parameter based on user preference
        thinking_param = {'type': 'enabled', 'budget_tokens': ai_thinking_budget} if ai_thinking_enabled else None
        
        # CRITICAL: When thinking is enabled, temperature MUST be 1.0 (Anthropic API requirement)
        # This overrides user preferences automatically
        final_temperature = 1.0 if ai_thinking_enabled else ai_temperature
        if ai_thinking_enabled and ai_temperature != 1.0:
            print(f"{log_prefix} ⚙️  Temperature overridden: {ai_temperature} → 1.0 (required when thinking enabled)")
        
        # CRITICAL: Final validation before API call (Nov 22, 2025)
        # Double-check that all assistant messages with thinking blocks have thinking as first block
        print(f"{log_prefix} 🔍 FINAL VALIDATION: Checking thinking block order before API call...")
        for idx, msg in enumerate(messages):
            if msg.get('role') == 'assistant':
                content = msg.get('content', [])
                if isinstance(content, list) and content:
                    # Check if message has thinking blocks
                    has_thinking = any(
                        isinstance(b, dict) and b.get('type') in ('thinking', 'redacted_thinking')
                        for b in content
                    )
                    
                    if has_thinking:
                        first_block = content[0]
                        first_type = first_block.get('type') if isinstance(first_block, dict) else 'unknown'
                        
                        if first_type not in ('thinking', 'redacted_thinking'):
                            print(f"{log_prefix} ❌ CRITICAL: Message {idx} has thinking blocks but first block is '{first_type}'")
                            print(f"{log_prefix} 🔧 AUTO-FIX: Reordering blocks to put thinking first...")
                            
                            # Separate blocks by type
                            thinking_blocks = [b for b in content if isinstance(b, dict) and b.get('type') in ('thinking', 'redacted_thinking')]
                            other_blocks = [b for b in content if not (isinstance(b, dict) and b.get('type') in ('thinking', 'redacted_thinking'))]
                            
                            # Reorder: thinking first
                            messages[idx]['content'] = thinking_blocks + other_blocks
                            
                            after_first = messages[idx]['content'][0].get('type') if messages[idx]['content'] else 'empty'
                            print(f"{log_prefix} ✅ Fixed: First block is now '{after_first}'")
        
            # CRITICAL FIX (Nov 27, 2025): Strip server tool blocks before sending to API
            # Server-side tool blocks (server_tool_use and their result blocks) cause 400 errors 
            # when replayed because result blocks require tool_use_id references that are removed
            # NOTE: Result blocks are already stored in DB and visible in UI - no data loss
            print(f"{log_prefix} 🧹 Cleaning conversation: Removing server-side tool blocks...")
            for idx, msg in enumerate(messages):
                if msg.get('role') == 'assistant':
                    content = msg.get('content', [])
                    if isinstance(content, list):
                        original_count = len(content)
                        # Filter out ALL server-side tool blocks (both requests and results)
                        # These blocks are for display only and shouldn't be replayed to API
                        cleaned_content = [
                            block for block in content
                            if not (isinstance(block, dict) and block.get('type') in [
                                'server_tool_use',           # Server tool request
                                'web_search_tool_result',    # Web search result
                                'web_fetch_tool_result'      # Web fetch result
                            ])
                        ]
                        
                        if len(cleaned_content) < original_count:
                            removed = original_count - len(cleaned_content)
                            print(f"{log_prefix}   Message [{idx}]: Removed {removed} server tool blocks")
                            messages[idx]['content'] = cleaned_content        # DEBUG: Log message structure being sent to API
        print(f"{log_prefix} 📋 FINAL MESSAGE STRUCTURE BEING SENT:")
        for idx, msg in enumerate(messages):
            role = msg.get('role')
            content = msg.get('content', [])
            if isinstance(content, list):
                block_types = [b.get('type') if isinstance(b, dict) else 'string' for b in content]
                print(f"  [{idx}] {role}: {block_types}")
            else:
                print(f"  [{idx}] {role}: (string content)")
        
        # Stream response from Claude with USER'S AI PREFERENCES
        stream_params = {
            'model': ai_model,
            'max_tokens': ai_max_tokens,
            'temperature': final_temperature,
            'system': system_prompt,
            'messages': messages,
            'tools': tools,
            'extra_headers': {
                'anthropic-beta': 'web-fetch-2025-09-10,interleaved-thinking-2025-05-14'
            }
        }
        
        # Only add thinking parameter if enabled
        if thinking_param:
            stream_params['thinking'] = thinking_param
            print(f"{log_prefix} 🧠 Interleaved Thinking enabled (allows thinking between tool calls)")
        
        with client.messages.stream(**stream_params) as stream:
            # Process streaming events
            for event in stream:
                if not hasattr(event, 'type'):
                    continue
                
                event_type = event.type
                
                # CONTENT BLOCK START
                if event_type == 'content_block_start':
                    if hasattr(event, 'content_block'):
                        block = event.content_block
                        block_type = block.type
                        index = event.index
                        
                        all_content_blocks.append(block)
                        
                        if block_type == 'thinking':
                            yield {'type': 'thinking', 'content': '', 'block_index': index, 'delta_type': 'start'}
                        elif block_type == 'text':
                            yield {'type': 'content_delta', 'text': '', 'block_index': index, 'delta_type': 'start'}
                        elif block_type == 'tool_use':
                            tool_uses.append({'id': block.id, 'name': block.name, 'input': {}})
                            yield {'type': 'tool_use', 'tool_name': block.name, 'tool_id': block.id, 'tool_input': {}, 'block_index': index}
                
                # CONTENT BLOCK DELTA
                elif event_type == 'content_block_delta':
                    if hasattr(event, 'delta'):
                        delta = event.delta
                        delta_type = delta.type
                        index = event.index
                        
                        if delta_type == 'thinking_delta':
                            yield {'type': 'thinking', 'content': delta.thinking, 'block_index': index, 'delta_type': 'delta'}
                        elif delta_type == 'text_delta':
                            yield {'type': 'content_delta', 'text': delta.text, 'block_index': index, 'delta_type': 'delta'}
            
            # Get final message
            final_message = stream.get_final_message()
            
            if final_message:
                stop_reason = final_message.stop_reason
                all_content_blocks = final_message.content
                
                # Parse tool inputs
                tool_uses = []
                for block in all_content_blocks:
                    if hasattr(block, 'type') and block.type == 'tool_use':
                        tool_uses.append({'id': block.id, 'name': block.name, 'input': block.input})
                        yield {'type': 'tool_input_complete', 'tool_name': block.name, 'tool_id': block.id, 'tool_input': block.input}
        
        # Serialize content blocks
        serialized_content = []
        for block in all_content_blocks:
            if hasattr(block, 'type'):
                if block.type == 'thinking':
                    # Include signature only if it exists and is not empty
                    print(f"[Combined Worker] 🔍 Serializing thinking block:")
                    print(f"  - Has signature attr: {hasattr(block, 'signature')}")
                    if hasattr(block, 'signature'):
                        sig_preview = str(block.signature)[:20] + '...' if len(str(block.signature)) > 20 else str(block.signature)
                        print(f"  - Signature value: {repr(sig_preview)}")
                        print(f"  - Signature is truthy: {bool(block.signature)}")
                    
                    thinking_dict = {'type': 'thinking', 'thinking': block.thinking}
                    if hasattr(block, 'signature') and block.signature:
                        thinking_dict['signature'] = block.signature
                        print(f"  - ✅ Including signature in dict")
                    else:
                        print(f"  - ⚠️ Omitting signature from dict")
                    
                    print(f"  - Final dict keys: {list(thinking_dict.keys())}")
                    serialized_content.append(thinking_dict)
                elif block.type == 'text':
                    # CRITICAL FIX (Nov 27, 2025): Preserve citations from web search/fetch
                    # Citations are embedded in text blocks and must be preserved for UI display
                    text_block = {'type': 'text', 'text': block.text}
                    
                    # Copy citations if present (from web search/fetch)
                    if hasattr(block, 'citations') and block.citations:
                        text_block['citations'] = [
                            {
                                'type': citation.type if hasattr(citation, 'type') else 'web_search_result_location',
                                'url': citation.url if hasattr(citation, 'url') else None,
                                'title': citation.title if hasattr(citation, 'title') else None,
                                'cited_text': citation.cited_text if hasattr(citation, 'cited_text') else None,
                                'encrypted_index': citation.encrypted_index if hasattr(citation, 'encrypted_index') else None
                            }
                            for citation in block.citations
                        ]
                        print(f"{log_prefix} 📚 Preserved {len(block.citations)} citations in text block")
                    
                    serialized_content.append(text_block)
                elif block.type == 'tool_use':
                    serialized_content.append({'type': 'tool_use', 'id': block.id, 'name': block.name, 'input': block.input})
        
        # CRITICAL: Reorder blocks - thinking MUST be first if present (Anthropic API requirement)
        thinking_blocks = [b for b in serialized_content if b.get('type') == 'thinking']
        other_blocks = [b for b in serialized_content if b.get('type') != 'thinking']
        serialized_content = thinking_blocks + other_blocks
        
        print(f"{log_prefix} Serialized {len(serialized_content)} blocks (thinking blocks first: {len(thinking_blocks)})")
        
        # Add assistant response to history (with ALL blocks including thinking)
        conversation_history.append({'role': 'assistant', 'content': serialized_content})
        
        # Execute tools if present
        if tool_uses and stop_reason == 'tool_use':
            from tools.registry_v3 import get_registry
            registry = get_registry()
            
            # CRITICAL: Detect infinite loops (same meta-tool called 3+ times consecutively)
            # BUT allow retries after tool errors (legitimate error recovery)
            if current_round >= 3:
                recent_tools = []
                recent_errors = []
                
                for msg in conversation_history[-6:]:  # Check last 3 rounds (6 messages: assistant + user)
                    if msg.get('role') == 'assistant':
                        content = msg.get('content', [])
                        # Handle both list and string content
                        if isinstance(content, str):
                            try:
                                content = json.loads(content)
                            except:
                                content = []
                        if not isinstance(content, list):
                            content = []
                        
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'tool_use':
                                recent_tools.append(block.get('name'))
                    
                    elif msg.get('role') == 'user':
                        # Check if previous tool call resulted in error
                        content = msg.get('content', [])
                        if isinstance(content, list):
                            for result in content:
                                if isinstance(result, dict) and result.get('is_error'):
                                    recent_errors.append(True)
                                else:
                                    recent_errors.append(False)
                
                # Check if same meta-tool called 3+ times in a row WITH successful results
                # (Don't block if agent is retrying after errors)
                if len(recent_tools) >= 3:
                    meta_tools = ['list_platform_tools', 'list_available_platforms', 'search_tools', 'recommend_tools_for_task']
                    last_three = recent_tools[-3:]
                    
                    # Only block if: same tool 3 times AND at least 2 successful calls (not error recovery)
                    if all(t in meta_tools for t in last_three) and len(set(last_three)) == 1:
                        # Check if this is error recovery (recent errors in tool results)
                        error_recovery_mode = len(recent_errors) > 0 and any(recent_errors[-3:])
                        
                        if not error_recovery_mode:
                            repeated_tool = last_three[0]
                            repeat_count = len([t for t in recent_tools if t == repeated_tool])
                            error_msg = f"""⚠️  INFINITE LOOP DETECTED: You called '{repeated_tool}' {repeat_count} times.

🛑 STOP calling discovery tools repeatedly!

✅ NEXT STEPS:
1. If you found tools → Call get_tool_schema("tool_name") to learn parameters
2. If you have schema → Call execute_tool("tool_name", param1=..., param2=...)
3. Move forward to execution, don't repeat discovery!

Example workflow:
- search_tools("email") → Found gmail_send_email
- get_tool_schema("gmail_send_email") → Got parameters
- execute_tool("gmail_send_email", to="...", subject="...", body="...")

Proceed to the NEXT step now."""
                            print(f"{log_prefix} {error_msg}")
                            yield {'type': 'error', 'error': error_msg, 'session_id': session_id, 'round': current_round}
                            return
                        else:
                            # Allow retry after error - legitimate error recovery
                            print(f"{log_prefix} ♻️  Allowing retry of '{last_three[0]}' (error recovery mode)")
            
            tool_results = []
            for tool_use in tool_uses:
                tool_name = tool_use['name']
                tool_input = tool_use['input'].copy()
                tool_id = tool_use['id']
                
                try:
                    # Handle meta-tools specially
                    if tool_name in ['get_tool_schema', 'execute_tool']:
                        from tools.implementations.meta_tools import execute_tool as execute_tool_fn, get_tool_schema as get_tool_schema_fn
                        
                        if tool_name == 'execute_tool':
                            result = execute_tool_fn(**tool_input, _user_id=user_id, _injected_credentials=True)
                        else:
                            result = get_tool_schema_fn(**tool_input)
                    else:
                        # Regular tools with credential injection
                        if tool_name.startswith(('google_', 'microsoft_')):
                            result = registry.execute_tool(tool_name=tool_name, _user_id=user_id, _injected_credentials=True, **tool_input)
                        else:
                            result = registry.execute_tool(tool_name=tool_name, **tool_input)
                    
                    # Smart truncation for large tool results to avoid 413 errors
                    result_str = smart_truncate_tool_result(result, tool_name=tool_name, max_tokens=2000)
                    tool_results.append({'type': 'tool_result', 'tool_use_id': tool_id, 'content': result_str})
                    yield {'type': 'tool_result', 'tool_name': tool_name, 'tool_id': tool_id, 'result': result_str, 'success': True}
                
                except Exception as e:
                    error_msg = f"Tool execution failed: {str(e)}"
                    tool_results.append({'type': 'tool_result', 'tool_use_id': tool_id, 'content': error_msg, 'is_error': True})
                    yield {'type': 'tool_result', 'tool_name': tool_name, 'tool_id': tool_id, 'result': error_msg, 'success': False, 'error': error_msg}
            
            # Add tool results to history
            conversation_history.append({'role': 'user', 'content': tool_results})
            
            # Recursive call for next round (preserve AI settings)
            yield from execute_streaming_request(
                session_id=session_id,
                user_prompt='',
                conversation_history=conversation_history,
                system_prompt=system_prompt,
                tools=tools,
                user_id=user_id,
                max_rounds=max_rounds,
                current_round=current_round + 1,
                ai_model=ai_model,
                ai_temperature=ai_temperature,
                ai_max_tokens=ai_max_tokens,
                ai_thinking_enabled=ai_thinking_enabled,
                ai_thinking_budget=ai_thinking_budget
            )
        else:
            # Conversation complete
            final_text = ''
            for block in all_content_blocks:
                if hasattr(block, 'type') and block.type == 'text':
                    final_text += block.text
            
            # CRITICAL FIX (Nov 22, 2025): Send conversation_sync BEFORE complete event
            # This ensures frontend has authoritative history before finalizing
            print(f"{log_prefix} 📤 Sending conversation_sync with {len(conversation_history)} messages")
            
            # DEBUG: Log last assistant message structure
            if conversation_history:
                last_msg = conversation_history[-1]
                if last_msg.get('role') == 'assistant':
                    content = last_msg.get('content', [])
                    print(f"{log_prefix} 🔍 Last assistant message has {len(content)} content blocks:")
                    for idx, block in enumerate(content):
                        block_type = block.get('type', 'unknown')
                        if block_type == 'text':
                            text_preview = block.get('text', '')[:50]
                            print(f"{log_prefix}   [{idx}] text: {repr(text_preview)}... (length: {len(block.get('text', ''))})")
                        else:
                            print(f"{log_prefix}   [{idx}] {block_type}")
            
            yield {
                'type': 'conversation_sync',
                'session_id': session_id,
                'conversation_history': conversation_history,
                'message_count': len(conversation_history),
                'round': current_round
            }
            
            # Then send complete event
            print(f"{log_prefix} ✅ Sending complete event")
            yield {
                'type': 'complete', 
                'session_id': session_id, 
                'full_response': final_text, 
                'stop_reason': stop_reason, 
                'total_rounds': current_round,
                'conversation_history': conversation_history  # Keep for backward compatibility
            }
    
    except Exception as e:
        print(f"{log_prefix} ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        yield {'type': 'error', 'error': str(e), 'session_id': session_id, 'round': current_round}

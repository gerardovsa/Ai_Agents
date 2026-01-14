"""
Accurate Token Counting using Anthropic's Official API

FILE: AI_infrastructure/utils/token_counter.py
PURPOSE: Provide exact token counts for Claude conversations before sending to API

EXPORTS:
- count_conversation_tokens(messages, system_prompt, tools, model) -> int
- count_tokens_with_fallback(text) -> int (heuristic fallback)

DEPENDENCIES:
- anthropic - Official Anthropic SDK
- config - API key management

NOTES:
- Uses Anthropic's /messages/count_tokens endpoint
- Returns exact input token counts (matches billing)
- Supports all content types: text, images, PDFs, tools, thinking blocks
- Falls back to heuristic (len // 4) on API errors
- Zero cost to use (pre-flight check, no message creation)

LAST MODIFIED: 2025-11-14 - Initial implementation with token counting API
"""

import anthropic
import os
from typing import List, Dict, Any, Optional


def count_conversation_tokens(
    messages: List[Dict[str, Any]],
    system_prompt: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    model: str = "claude-sonnet-4-5",
    thinking_enabled: bool = False,
    thinking_budget: int = 10000
) -> int:
    """
    Count exact input tokens for a conversation using Anthropic's API
    
    Args:
        messages: List of message dicts with role and content
        system_prompt: Optional system prompt string
        tools: Optional list of tool definitions (for first sampling call)
        model: Claude model to count for (default: claude-sonnet-4-5)
        thinking_enabled: Whether extended thinking is enabled (default: False)
        thinking_budget: Token budget for thinking (default: 10000)
        
    Returns:
        int: Exact input token count from Anthropic's tokenizer
        
    Raises:
        None - Falls back to heuristic on errors
        
    Examples:
        >>> messages = [{"role": "user", "content": "Hello"}]
        >>> count = count_conversation_tokens(messages)
        >>> print(f"Exact tokens: {count}")
        
    Notes:
        - Token count is an estimate; actual usage may differ slightly
        - System-added tokens (optimizations) are not billed
        - Tool tokens only apply to first sampling call
        - Falls back to len(text) // 4 on API errors
    """
    try:
        # Get API key from environment
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Build request parameters
        params = {
            "model": model,
            "messages": messages
        }
        
        if system_prompt:
            params["system"] = system_prompt
        if tools:
            params["tools"] = tools
        
        # CRITICAL FIX (Nov 14, 2025): Add thinking parameter if enabled
        # Without this, API returns 400 error when messages contain thinking blocks
        if thinking_enabled:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget
            }
            
        # Call token counting endpoint
        response = client.messages.count_tokens(**params)
        
        token_count = response.input_tokens
        print(f"[TOKEN COUNT] API returned: {token_count} tokens")
        return token_count
        
    except Exception as e:
        print(f"[TOKEN COUNT] API error: {e}")
        print(f"[TOKEN COUNT] Falling back to heuristic estimator")
        
        # Fallback to heuristic
        total_chars = 0
        for msg in messages:
            content = msg.get('content', '')
            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        if block.get('type') == 'text':
                            total_chars += len(block.get('text', ''))
                        elif block.get('type') == 'thinking':
                            total_chars += len(block.get('thinking', ''))
        
        if system_prompt:
            total_chars += len(system_prompt)
            
        # Heuristic: ~4 chars per token
        estimated = total_chars // 4
        print(f"[TOKEN COUNT] Heuristic estimate: {estimated} tokens")
        return estimated


def count_tokens_with_fallback(text: str) -> int:
    """
    Simple token count for plain text using heuristic
    
    Args:
        text: Plain text string
        
    Returns:
        int: Estimated token count (len // 4)
        
    Notes:
        - Use count_conversation_tokens() for accurate counts
        - This is a fast heuristic for simple text
        - ~4 characters per token average
    """
    return len(text) // 4


def format_token_summary(
    input_tokens: int,
    output_tokens: int = 0,
    limit: int = 200000
) -> Dict[str, Any]:
    """
    Format token counts into summary dict with percentages and status
    
    Args:
        input_tokens: Input token count
        output_tokens: Output token count (optional)
        limit: Token limit for context window (default: 200k)
        
    Returns:
        dict: {
            'total_tokens': int,
            'input_tokens': int,
            'output_tokens': int,
            'percentage': float,
            'status': str (NORMAL/CAUTION/CRITICAL/EMERGENCY),
            'remaining': int
        }
    """
    total = input_tokens + output_tokens
    percentage = (total / limit * 100) if limit > 0 else 0
    remaining = limit - total
    
    # Determine status based on percentage
    if percentage >= 95:
        status = 'EMERGENCY'
    elif percentage >= 80:
        status = 'CRITICAL'
    elif percentage >= 50:
        status = 'CAUTION'
    else:
        status = 'NORMAL'
    
    return {
        'total_tokens': total,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'percentage': round(percentage, 1),
        'status': status,
        'remaining': remaining,
        'limit': limit
    }


# Example usage
if __name__ == "__main__":
    # Test token counting
    test_messages = [
        {"role": "user", "content": "Hello, Claude!"},
        {"role": "assistant", "content": "Hello! How can I help you today?"},
        {"role": "user", "content": "Can you explain token counting?"}
    ]
    
    count = count_conversation_tokens(
        messages=test_messages,
        system_prompt="You are a helpful AI assistant.",
        model="claude-sonnet-4-5"
    )
    
    print(f"\nTest Result: {count} tokens")
    
    summary = format_token_summary(
        input_tokens=count,
        output_tokens=150,
        limit=200000
    )
    
    print(f"Summary: {summary}")

"""
Tool Result Token Limits Configuration

Controls how much data from tool results is kept in conversation history.
Adjust these limits to balance between context preservation and token efficiency.

Token Budget Strategy:
- 200K total context window
- ~20K for system prompt + tools
- ~180K for conversation
- With pruning, keep ~225 messages
- Average 800 tokens per message

Goal: Enable 20-30 rounds of tool use without hitting limits
"""

# ============================================================================
# TOOL RESULT LIMITS (tokens)
# ============================================================================

# Default limit for uncategorized tools
DEFAULT_LIMIT = 2000

# Category-based limits
TOOL_LIMITS = {
    # List/Search operations - moderate limits (users scan results)
    'list': 3000,
    'search': 3000,
    'query': 3000,
    'find': 3000,
    
    # Read operations - larger limits (may need full content)
    'get': 5000,
    'read': 5000,
    'fetch': 5000,
    'retrieve': 5000,
    
    # CRUD operations - small limits (typically just status/ID)
    'create': 1000,
    'update': 1000,
    'delete': 1000,
    'insert': 1000,
    'modify': 1000,
    
    # Special cases - very small limits
    'count': 500,
    'exists': 500,
    'validate': 500,
    'check': 500,
}

# Specific tool overrides (exact tool names)
TOOL_SPECIFIC_LIMITS = {
    # Gmail tools
    'gmail_search_messages': 4000,  # Need to see multiple messages
    'gmail_get_message': 3000,      # Full email content
    'gmail_list_labels': 1000,      # Just label names
    
    # Google Sheets tools
    'google_sheets_get_values': 6000,      # May need many rows
    'google_sheets_batch_get': 8000,       # Multiple ranges
    'google_sheets_create': 1000,          # Just created sheet ID
    
    # Google Docs tools
    'google_docs_get_document': 7000,      # Full document content
    'google_docs_create_document': 1000,   # Just document ID
    
    # Slack tools
    'slack_list_messages': 4000,           # Chat history
    'slack_post_message': 500,             # Just success confirmation
    
    # Stripe tools
    'stripe_list_customers': 3000,         # Customer list
    'stripe_create_customer': 1000,        # Just customer ID
    
    # WooCommerce tools
    'woocommerce_list_products': 4000,     # Product catalog
    'woocommerce_get_product': 2000,       # Single product details
    'woocommerce_create_order': 1000,      # Just order ID
    
    # Calculator tools
    'calculate_business_cards': 2000,      # Quote breakdown
    'calculate_flyers': 2000,              # Quote breakdown
    'calculate_booklets': 2000,            # Quote breakdown
    'get_stock_list': 3000,                # Stock options
}


def get_token_limit_for_tool(tool_name: str) -> int:
    """
    Get the token limit for a specific tool
    
    Priority:
    1. Specific tool name match
    2. Category keyword match
    3. Default limit
    
    Args:
        tool_name: Name of the tool
    
    Returns:
        Maximum tokens to keep from tool result
    """
    # Check specific tool override
    if tool_name in TOOL_SPECIFIC_LIMITS:
        return TOOL_SPECIFIC_LIMITS[tool_name]
    
    # Check category keywords
    tool_lower = tool_name.lower()
    for keyword, limit in TOOL_LIMITS.items():
        if keyword in tool_lower:
            return limit
    
    # Return default
    return DEFAULT_LIMIT


# ============================================================================
# TRUNCATION STRATEGIES
# ============================================================================

def get_truncation_strategy(tool_name: str) -> str:
    """
    Get truncation strategy for a tool
    
    Strategies:
    - 'head': Keep first N tokens (default)
    - 'tail': Keep last N tokens
    - 'smart': Keep first + last (for lists)
    
    Args:
        tool_name: Name of the tool
    
    Returns:
        Truncation strategy name
    """
    tool_lower = tool_name.lower()
    
    # Lists/searches benefit from seeing both start and end
    if any(kw in tool_lower for kw in ['list', 'search', 'query']):
        return 'smart'
    
    # Logs/history benefit from recent items
    if any(kw in tool_lower for kw in ['log', 'history', 'messages']):
        return 'tail'
    
    # Default: keep beginning
    return 'head'


# ============================================================================
# ITERATION LIMITS
# ============================================================================

# Maximum tool iterations before forcing summarization
MAX_ITERATIONS_BEFORE_SUMMARY = 15

# Maximum cumulative tool result tokens before compression
MAX_CUMULATIVE_TOOL_TOKENS = 50000

# Enable/disable auto-truncation
AUTO_TRUNCATE_ENABLED = True

# Log truncation warnings
LOG_TRUNCATION = True

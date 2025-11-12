"""
Test the new colored tool logging
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from utils.logger_config import log_tool_success, log_tool_failure

print("\nTesting colored tool logging:\n")

# Test successful tool calls
print("Successful tool calls:")
log_tool_success('gmail_search_messages', 1234)
log_tool_success('google_sheets_get_values', 5678)
log_tool_success('list_platform_tools', 123)

print("\n")

# Test failed tool calls
print("Failed tool calls:")
log_tool_failure('gmail_send_email', 'Invalid recipient email', 45)
log_tool_failure('stripe_create_customer', 'API key not found', 0)
log_tool_failure('google_docs_create_document', 'Permission denied', 234)

print("\nFormatting test complete!")

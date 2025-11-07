"""
Fix Shopify Module - Add shopify- prefix to all CSS classes and IDs
Prevents CSS/HTML clashing with other modules
"""

import re
from pathlib import Path

# File path
shopify_js_path = Path(r'C:\Users\gpoli\GIT\AI_agents\UI\external\modules\shopify\shopify.js')

# Read file
with open(shopify_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# List of IDs to prefix (excluding those already prefixed with shopify-)
ids_to_fix = [
    'total-orders', 'total-revenue', 'avg-order-value', 'orders-today',
    'orders-over-time-chart', 'revenue-by-product-chart',
    'orders-days-filter', 'orders-status-filter', 'orders-min-value', 
    'apply-orders-filters', 'orders-table-container',
    'customer-segments-chart', 'top-customers-table',
    'top-products-chart', 'products-table',
    'refresh-webhooks', 'webhook-status-chart', 'webhooks-table',
    'shopify-sql-query', 'shopify-execute-query', 'shopify-sql-results'
]

# List of classes to prefix (excluding those already prefixed)
classes_to_fix = [
    'orders-container', 'orders-filters',
    'customers-container', 'charts-row', 'top-customers-section',
    'products-container', 'chart-container', 'products-table-section',
    'webhooks-container', 'webhook-stats', 'webhooks-log-section',
    'sql-viewer-container', 'sql-controls', 'query-examples', 
    'quick-query-btn', 'query-editor', 'sql-results',
    'data-table', 'status-badge', 'loading', 'no-data', 'error',
    'btn', 'btn-primary', 'btn-secondary', 'table-container',
    'query-info', 'table-wrapper', 'results-table', 'error-message',
    'no-results'
]

# Fix getElementById calls
for id_name in ids_to_fix:
    # Skip if already has shopify- prefix
    if id_name.startswith('shopify-'):
        continue
    
    # Replace getElementById('id') → getElementById('shopify-id')
    content = re.sub(
        rf"getElementById\(['\"]({id_name})['\"]\)",
        rf"getElementById('shopify-\1')",
        content
    )
    
    # Replace id="id" → id="shopify-id"
    content = re.sub(
        rf'id=["\']({id_name})["\']',
        rf'id="shopify-\1"',
        content
    )

# Fix className assignments
for class_name in classes_to_fix:
    # Skip if already has shopify- prefix
    if class_name.startswith('shopify-'):
        continue
    
    # Replace className="class" → className="shopify-class"
    content = re.sub(
        rf'className=["\']({class_name})["\']',
        rf'className="shopify-\1"',
        content
    )
    
    # Replace class="class" → class="shopify-class"
    content = re.sub(
        rf'class=["\']({class_name})["\']',
        rf'class="shopify-\1"',
        content
    )
    
    # Replace .querySelector('.class') → .querySelector('.shopify-class')
    content = re.sub(
        rf"querySelector\(['\"]\.({class_name})['\"]\)",
        rf"querySelector('.shopify-\1')",
        content
    )
    
    # Replace .querySelectorAll('.class') → .querySelectorAll('.shopify-class')
    content = re.sub(
        rf"querySelectorAll\(['\"]\.({class_name})['\"]\)",
        rf"querySelectorAll('.shopify-\1')",
        content
    )

# Write updated content
with open(shopify_js_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed shopify.js - Added shopify- prefix to classes and IDs")
print(f"   Fixed {len(ids_to_fix)} ID patterns")
print(f"   Fixed {len(classes_to_fix)} class patterns")
print("\nNext: Update shopify.css to match")

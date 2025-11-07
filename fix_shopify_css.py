"""
Fix Shopify CSS - Add shopify- prefix to match JS changes
"""

import re
from pathlib import Path

# File path
shopify_css_path = Path(r'C:\Users\gpoli\GIT\AI_agents\UI\external\modules\shopify\shopify.css')

# Read file
with open(shopify_css_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Classes that need prefixing
classes_to_fix = [
    'metrics-grid', 'metric-card', 'metric-icon', 'metric-content',
    'period-selector', 'period-btn', 'charts-section', 'chart-container',
    'orders-container', 'orders-filters', 'table-container',
    'data-table', 'status-badge', 
    'customers-container', 'charts-row', 'top-customers-section',
    'products-container', 'products-table-section',
    'webhooks-container', 'webhook-stats', 'webhooks-log-section',
    'sql-viewer-container', 'sql-controls', 'query-examples',
    'quick-query-btn', 'query-editor', 'sql-results',
    'query-info', 'table-wrapper', 'results-table',
    'loading', 'no-data', 'no-results', 'error', 'error-message',
    'btn', 'btn-primary', 'btn-secondary'
]

# Fix CSS selectors
for class_name in classes_to_fix:
    # Skip if already has shopify- prefix
    if class_name.startswith('shopify-'):
        continue
    
    # Replace .class → .shopify-class (at start of selector)
    content = re.sub(
        rf'^\.({class_name})(\s|,|:|\{{)',
        rf'.shopify-\1\2',
        content,
        flags=re.MULTILINE
    )
    
    # Replace space.class → space.shopify-class
    content = re.sub(
        rf'(\s)\.({class_name})(\s|,|:|\{{)',
        rf'\1.shopify-\2\3',
        content
    )

# Also fix status badge variants
status_variants = ['paid', 'success', 'fulfilled', 'pending', 'partial', 'refunded', 'error', 'unfulfilled']
for variant in status_variants:
    content = re.sub(
        rf'\.status-badge\.status-{variant}',
        rf'.shopify-status-badge.shopify-status-{variant}',
        content
    )

# Fix #id selectors
ids_to_fix = [
    'refresh-webhooks', 'shopify-execute-query', 'shopify-sql-query', 
    'shopify-sql-results'
]

for id_name in ids_to_fix:
    if not id_name.startswith('shopify-'):
        content = re.sub(
            rf'#({id_name})(\s|\{{|:)',
            rf'#shopify-\1\2',
            content
        )

# Write updated content
with open(shopify_css_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed shopify.css - Added shopify- prefix to selectors")
print(f"   Fixed {len(classes_to_fix)} class selector patterns")
print(f"   Fixed {len(status_variants)} status badge variants")
print(f"   Fixed {len(ids_to_fix)} ID selectors")

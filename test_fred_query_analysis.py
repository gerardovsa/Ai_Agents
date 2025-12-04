"""
FRED SQL Query Data Flow Analysis
Analyzes how query results flow, their structure, and optimization opportunities
"""

import sys
from pathlib import Path
import json

# Add backend to path
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))

from query_library import QueryLibrary

print('='*80)
print('=== FRED SQL QUERY DATA FLOW ANALYSIS ===')
print('='*80)

# Initialize query library (without DB for catalog analysis)
query_lib = QueryLibrary(db_connection=None)

# Get query catalog
catalog = query_lib.query_catalog

print(f'\n📊 QUERY LIBRARY STATS')
print(f'   Total queries: {len(catalog)}')

# Categorize queries
categories = {}
for query_name, query_info in catalog.items():
    category = query_info.get('category', 'Uncategorized')
    if category not in categories:
        categories[category] = []
    categories[category].append(query_name)

print(f'   Categories: {len(categories)}')
for category, queries in sorted(categories.items()):
    print(f'      - {category}: {len(queries)} queries')

print('\n' + '='*80)
print('🔍 DATA FLOW ANALYSIS')
print('='*80)

# Analyze a sample query structure
sample_queries = [
    'monthly_revenue_trend',
    'customer_order_history',
    'top_selling_products',
    'invoice_aging_report'
]

for query_name in sample_queries:
    if query_name in catalog:
        query_info = catalog[query_name]
        print(f'\n📋 Query: {query_name}')
        print(f'   Category: {query_info.get("category")}')
        print(f'   Description: {query_info.get("description")[:80]}...')
        print(f'   Returns: {query_info.get("returns")}')
        print(f'   Parameters: {list(query_info.get("parameters", {}).keys())}')
        print(f'   Visualization: {query_info.get("visualization")}')

print('\n' + '='*80)
print('📦 CURRENT DATA STRUCTURE')
print('='*80)

print('''
When execute_query() is called, it returns:

{
    "success": True,
    "data": <pandas DataFrame>,           # RAW DATA - Can be large!
    "summary": "Human-readable summary",   # TEXT SUMMARY
    "metadata": {
        "query_name": "monthly_revenue_trend",
        "parameters": {"months": 6},
        "row_count": 6,
        "column_count": 5,
        "execution_time_seconds": 0.123,
        "data_quality": {...}              # Null counts, duplicates, etc.
    }
}

The DataFrame contains formatted columns like:
- Revenue_Formatted: "$12,345.67"  
- Count_Formatted: "1,234"
- Percentage_Formatted: "23.5%"
''')

print('\n' + '='*80)
print('⚠️  CURRENT ISSUES')
print('='*80)

print('''
1. HEAVY JSON SERIALIZATION
   - pandas DataFrame is NOT JSON-serializable by default
   - Must convert to dict/list (df.to_dict('records'))
   - Large result sets (1000+ rows) = massive JSON payloads
   
2. NO INTERMEDIATE STORAGE
   - Query results go directly to AI agent
   - Lost after conversation ends
   - Cannot reference historical queries
   - No caching/reuse possible

3. HUMAN vs AI FORMAT CONFLICT
   - Formatted strings ("$12,345.67") good for humans
   - But AI needs numeric values for calculations
   - Currently returns BOTH (duplicate columns)
   
4. NO MARKDOWN TABLE OUTPUT
   - Unlike Xero tools (just enhanced)
   - AI receives raw dict/JSON only
   - Must manually format for user display
''')

print('\n' + '='*80)
print('💡 PROPOSED SOLUTIONS')
print('='*80)

print('''
SOLUTION 1: Database Storage Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Create: query_results table in Supabase

Schema:
  - result_id (uuid, PK)
  - user_id (int, FK to users)
  - session_id (uuid, FK to sessions)
  - query_name (text)
  - parameters (jsonb)
  - executed_at (timestamp)
  - row_count (int)
  - execution_time_ms (int)
  - result_data (jsonb)  ← Compressed/chunked for large datasets
  - result_summary (text)
  - result_markdown (text)  ← NEW!
  - result_url (text)  ← Link to exported file (CSV/Excel)
  
Benefits:
  ✅ Query history per user
  ✅ Result reuse (avoid re-executing)
  ✅ Analytics on query patterns
  ✅ Export links persist
  ✅ Can paginate large results


SOLUTION 2: Markdown Table Rendering (Like Xero)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Enhance execute_query() to return:

{
    "success": True,
    "data": [...],                    # Original JSON (for AI processing)
    "markdown_table": "## Revenue Trend\\n\\n| Month | Revenue | Orders |\\n...",
    "summary": "6 months, $123K total revenue",
    "export_options": {
        "csv": True,
        "excel": True,
        "google_sheets": True
    },
    "metadata": {...}
}

Benefits:
  ✅ Consistent with Xero tools
  ✅ Human-readable tables
  ✅ AI shows formatted results directly
  ✅ Export options visible


SOLUTION 3: Smart Pagination
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For queries with 100+ rows:

{
    "success": True,
    "data": [...first 50 rows...],
    "markdown_table": "...",
    "pagination": {
        "current_page": 1,
        "total_pages": 10,
        "total_rows": 487,
        "rows_per_page": 50,
        "has_more": True,
        "next_page_token": "eyJ..."  ← Encrypted query state
    },
    "summary": "Showing 1-50 of 487 results",
    "export_url": "https://storage/query-results/abc123.csv"  ← Full dataset
}

Benefits:
  ✅ Reduced JSON payload
  ✅ Faster AI responses
  ✅ Full data available via export
  ✅ Better UX for large datasets


SOLUTION 4: Query Result Caching
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cache results in Redis/Memory:

Cache Key: hash(query_name + parameters + user_id)
Cache TTL: 
  - Real-time queries (sales_today): 5 minutes
  - Historical queries (revenue_trend): 1 hour
  - Static queries (customer_list): 24 hours

Benefits:
  ✅ Instant results for repeated queries
  ✅ Reduced database load
  ✅ Faster AI responses
  ✅ Can show "cached as of HH:MM"
''')

print('\n' + '='*80)
print('🎯 RECOMMENDED IMPLEMENTATION ORDER')
print('='*80)

print('''
PHASE 1: Markdown Tables (QUICK WIN - 1-2 hours)
├─ Add _render_dataframe_markdown() helper
├─ Add markdown_table to execute_query() return
├─ Add export_options indicator
└─ Test with 5 sample queries

PHASE 2: Export Links (MEDIUM - 2-3 hours)  
├─ Create export_to_csv() function
├─ Create export_to_excel() function
├─ Store files in /tmp or cloud storage
├─ Return file_url in results
└─ Add cleanup job for old exports

PHASE 3: Database Storage (COMPLEX - 4-6 hours)
├─ Create query_results table
├─ Add save_query_result() after execution
├─ Add get_query_result(result_id) retrieval
├─ Add list_query_history(user_id, limit) 
├─ Update AI tools to reference past results
└─ Add cleanup job (delete after 30 days)

PHASE 4: Caching Layer (OPTIMIZATION - 2-3 hours)
├─ Add Redis/in-memory cache
├─ Check cache before executing SQL
├─ Invalidation rules by query type
└─ Cache hit metrics

TOTAL EFFORT: ~9-14 hours spread across sprints
''')

print('\n' + '='*80)
print('📊 SAMPLE QUERY TO TEST')
print('='*80)

# Show SQL for a sample query
if 'monthly_revenue_trend' in catalog:
    try:
        query_result = query_lib.build_query('monthly_revenue_trend', months=6)
        sql = query_result['sql']
        
        print('\nQuery: monthly_revenue_trend (6 months)')
        print('\nGenerated SQL:')
        print('-' * 80)
        print(sql[:1000] + '...' if len(sql) > 1000 else sql)
        print('-' * 80)
        
        print('\nExpected columns:')
        print(f"   {query_result['metadata'].get('returns')}")
        
        print('\nCurrent return structure:')
        print('''
{
    "success": True,
    "data": [
        {
            "YearMonth": "2024-11",
            "TotalRevenue": 45678.90,
            "TotalRevenue_Formatted": "$45,678.90",  ← Duplicate for display
            "OrderCount": 123,
            "OrderCount_Formatted": "123",
            "AvgJobValue": 371.29,
            "AvgJobValue_Formatted": "$371.29"
        },
        ...
    ],
    "summary": "6 months analyzed. Total revenue: $234,567.89. Avg orders: 120/month.",
    "metadata": {
        "row_count": 6,
        "execution_time_seconds": 0.045
    }
}
        ''')
        
        print('\nProposed enhanced structure:')
        print('''
{
    "success": True,
    "data": [...],  ← Keep original
    "markdown_table": """
## InHouse Print - Monthly Revenue Trend (6 months)

| Month | Revenue | Orders | Avg Order Value | Units Produced |
|-------|---------|--------|-----------------|----------------|
| Nov 2024 | $45,678.90 | 123 | $371.29 | 5,234 |
| Oct 2024 | $42,123.45 | 118 | $357.13 | 4,891 |
| Sep 2024 | $48,901.23 | 134 | $365.05 | 5,678 |
...

**Total Revenue:** $234,567.89  
**Average Monthly Orders:** 120  
**Trend:** ↗️ +8.2% vs previous period
    """,
    "export_options": {
        "csv": True,
        "excel": True,
        "google_sheets": False  ← Requires OAuth
    },
    "export_url": "https://storage/.../monthly_revenue_trend_20251205_143022.csv",
    "summary": "6 months analyzed. Revenue trending up +8.2%.",
    "metadata": {...}
}
        ''')
        
    except Exception as e:
        print(f'Error building query: {e}')

print('\n' + '='*80)
print('✅ ANALYSIS COMPLETE')
print('='*80)
print('''
Next Steps:
1. Review proposed solutions
2. Choose implementation priority
3. Create test queries to validate approach
4. Implement Phase 1 (Markdown tables) first
5. Test with real FRED data
6. Iterate based on AI agent feedback

Documentation: FRED_QUERY_OPTIMIZATION_DEC5_2025.md
''')
print('='*80)

# FRED SQL Query Data Flow & Optimization Analysis

**Date:** December 5, 2025  
**Status:** Analysis Complete → Implementation Ready  
**Scope:** 64 SQL queries across 17 categories

---

## Executive Summary

The FRED database query library contains **64 pre-built SQL queries** used by AI agents to extract business intelligence data. This document analyzes the current data flow, identifies optimization opportunities, and proposes a phased implementation plan.

### Key Findings

1. **✅ Queries are well-structured** - 64 queries across 17 categories with proper metadata
2. **⚠️ Heavy JSON payloads** - Large result sets (100+ rows) create massive responses
3. **❌ No intermediate storage** - Results lost after conversation ends
4. **❌ No Markdown formatting** - Unlike Xero tools, raw JSON only
5. **❌ No caching** - Every query hits database (even repeated requests)

---

## Current Architecture

### Query Flow

```
AI Agent → inhouse_execute_sql() / execute_query_library()
    ↓
ToolUseAgent._execute_client_tool()
    ↓
QueryLibrary.execute_query(query_name, **params)
    ↓
InHousePrintDB.execute_query(sql)
    ↓
pandas DataFrame → Formatted columns
    ↓
Return Dict {
    success, data, summary, metadata
}
    ↓
JSON serialization (df.to_dict('records'))
    ↓
AI Agent receives raw JSON
    ↓
❌ Results lost after conversation
```

### Query Library Stats

- **Total Queries:** 64
- **Categories:** 17
  - Sales & Revenue: 5 queries
  - Customer Analytics: 7 queries
  - Product Analysis: 6 queries
  - Stock Management: 6 queries
  - Operational Flow: 8 queries
  - ... (12 more categories)

---

## Current Return Structure

### Example: `monthly_revenue_trend`

**Input:**
```python
execute_query('monthly_revenue_trend', months=6)
```

**Output:**
```json
{
    "success": true,
    "data": [
        {
            "YearMonth": "2024-11",
            "TotalRevenue": 45678.90,
            "TotalRevenue_Formatted": "$45,678.90",
            "OrderCount": 123,
            "OrderCount_Formatted": "123",
            "AvgJobValue": 371.29,
            "AvgJobValue_Formatted": "$371.29",
            "UnitsProduced": 5234
        },
        // ... 5 more months
    ],
    "summary": "6 months analyzed. Total revenue: $234,567.89. Avg orders: 120/month.",
    "metadata": {
        "query_name": "monthly_revenue_trend",
        "parameters": {"months": 6},
        "row_count": 6,
        "column_count": 8,
        "execution_time_seconds": 0.045,
        "data_quality": {
            "null_counts": {...},
            "duplicate_rows": 0
        }
    }
}
```

### Issues with Current Structure

1. **Duplicate Columns**
   - `TotalRevenue` (numeric) AND `TotalRevenue_Formatted` (string)
   - AI needs numeric, humans need formatted
   - Result: Double the data size

2. **No Human-Readable Format**
   - AI must manually create tables
   - Inconsistent formatting across queries
   - Markdown rendering not built-in

3. **Large JSON Payloads**
   - 100-row query = ~50KB JSON
   - 1000-row query = ~500KB JSON
   - Slows AI response time

4. **No Persistence**
   - Results lost when conversation ends
   - Cannot reference "the revenue report from earlier"
   - Must re-query for follow-up questions

---

## Proposed Solutions

### 🎯 Phase 1: Markdown Table Rendering (QUICK WIN)

**Effort:** 1-2 hours  
**Impact:** High - Immediate UX improvement

#### Implementation

Add to `QueryLibrary.execute_query()`:

```python
def _render_dataframe_markdown(self, df: pd.DataFrame, query_name: str, 
                               metadata: Dict) -> str:
    """
    Render DataFrame as professional Markdown table
    
    Returns:
        ## InHouse Print - Query Name
        
        | Column1 | Column2 | Column3 |
        |---------|---------|---------|
        | Value1  | Value2  | Value3  |
        ...
        
        **Total Rows:** 123
        **Execution Time:** 0.045s
    """
    # Build markdown header
    markdown = f"## InHouse Print - {query_name.replace('_', ' ').title()}\n\n"
    
    # Build table header
    headers = []
    for col in df.columns:
        if not col.endswith('_Formatted'):  # Skip duplicate columns
            headers.append(col.replace('_', ' '))
    
    markdown += "| " + " | ".join(headers) + " |\n"
    markdown += "|" + "---|" * len(headers) + "\n"
    
    # Build table rows (use formatted columns if available)
    for _, row in df.iterrows():
        values = []
        for col in df.columns:
            if not col.endswith('_Formatted'):
                formatted_col = f"{col}_Formatted"
                if formatted_col in df.columns:
                    values.append(str(row[formatted_col]))
                else:
                    values.append(str(row[col]))
        markdown += "| " + " | ".join(values) + " |\n"
    
    # Add summary footer
    markdown += f"\n**Total Rows:** {len(df):,}\n"
    markdown += f"**Execution Time:** {metadata.get('execution_time_seconds', 0):.3f}s\n"
    
    return markdown
```

#### Enhanced Return Structure

```json
{
    "success": true,
    "data": [...],  // Keep original for AI processing
    "markdown_table": "## InHouse Print - Monthly Revenue Trend\n\n| Month | Revenue | Orders |...",
    "summary": "6 months analyzed. Revenue trending up +8.2%.",
    "export_options": {
        "csv": true,
        "excel": true,
        "google_sheets": false
    },
    "metadata": {...}
}
```

#### Benefits

✅ Consistent with Xero tools (just enhanced)  
✅ Human-readable tables in AI responses  
✅ AI shows formatted results directly  
✅ Export options visible  
✅ No breaking changes (additive only)

---

### 📊 Phase 2: Export Links (MEDIUM)

**Effort:** 2-3 hours  
**Impact:** Medium - Better data portability

#### Implementation

Add export functions:

```python
def _export_to_csv(self, df: pd.DataFrame, query_name: str) -> str:
    """Export to CSV, return file URL"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{query_name}_{timestamp}.csv"
    filepath = Path(f"/tmp/query_exports/{filename}")
    
    filepath.parent.mkdir(exist_ok=True)
    df.to_csv(filepath, index=False)
    
    return f"/downloads/query_exports/{filename}"

def _export_to_excel(self, df: pd.DataFrame, query_name: str) -> Dict:
    """Export to Excel in memory, return base64"""
    from io import BytesIO
    import base64
    
    buffer = BytesIO()
    df.to_excel(buffer, index=False, sheet_name=query_name[:31])
    buffer.seek(0)
    
    return {
        "filename": f"{query_name}_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
        "file_base64": base64.b64encode(buffer.read()).decode('utf-8'),
        "file_size_kb": round(buffer.tell() / 1024, 2)
    }
```

#### Updated Return

```json
{
    "success": true,
    "data": [...],
    "markdown_table": "...",
    "export_url": "https://storage/query_exports/monthly_revenue_20251205.csv",
    "export_options": {
        "csv": true,
        "excel": true,
        "google_sheets": false
    }
}
```

---

### 💾 Phase 3: Database Storage (COMPLEX)

**Effort:** 4-6 hours  
**Impact:** High - Query history & reuse

#### Database Schema

Create table in Supabase:

```sql
CREATE TABLE query_results (
    result_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(user_id),
    session_id UUID REFERENCES sessions(session_id),
    query_name TEXT NOT NULL,
    parameters JSONB,
    executed_at TIMESTAMP DEFAULT NOW(),
    row_count INTEGER,
    execution_time_ms INTEGER,
    result_data JSONB,  -- Compressed/chunked for large datasets
    result_summary TEXT,
    result_markdown TEXT,
    result_url TEXT,  -- Link to CSV/Excel export
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '30 days')
);

CREATE INDEX idx_query_results_user ON query_results(user_id);
CREATE INDEX idx_query_results_session ON query_results(session_id);
CREATE INDEX idx_query_results_query ON query_results(query_name);
CREATE INDEX idx_query_results_expires ON query_results(expires_at);
```

#### Storage Functions

```python
def save_query_result(self, result: Dict, user_id: int, session_id: str) -> str:
    """Save query result to database, return result_id"""
    
    result_id = str(uuid.uuid4())
    
    # Compress large datasets
    result_data = result['data']
    if len(result_data) > 100:
        # Store only metadata + export URL for large queries
        result_data = {
            "truncated": True,
            "full_data_url": result.get('export_url'),
            "preview": result_data[:20]  # First 20 rows
        }
    
    supabase.table('query_results').insert({
        'result_id': result_id,
        'user_id': user_id,
        'session_id': session_id,
        'query_name': result['metadata']['query_name'],
        'parameters': result['metadata']['parameters'],
        'row_count': result['metadata']['row_count'],
        'execution_time_ms': int(result['metadata']['execution_time_seconds'] * 1000),
        'result_data': result_data,
        'result_summary': result['summary'],
        'result_markdown': result['markdown_table'],
        'result_url': result.get('export_url')
    }).execute()
    
    return result_id

def get_query_history(self, user_id: int, limit: int = 20) -> List[Dict]:
    """Get user's recent query history"""
    
    response = supabase.table('query_results')\
        .select('*')\
        .eq('user_id', user_id)\
        .order('executed_at', desc=True)\
        .limit(limit)\
        .execute()
    
    return response.data
```

#### Benefits

✅ Query history per user  
✅ Reference past results ("show me yesterday's revenue report")  
✅ Avoid re-executing identical queries  
✅ Analytics on query patterns  
✅ Export links persist  
✅ Auto-cleanup after 30 days

---

### ⚡ Phase 4: Caching Layer (OPTIMIZATION)

**Effort:** 2-3 hours  
**Impact:** Medium - Performance boost

#### Implementation

```python
import hashlib
import json
from datetime import timedelta

class QueryCache:
    """In-memory cache for query results"""
    
    def __init__(self):
        self.cache = {}
        self.ttl_rules = {
            'real_time': 300,      # 5 minutes (sales_today, orders_pending)
            'historical': 3600,    # 1 hour (revenue_trend, monthly_analysis)
            'static': 86400        # 24 hours (customer_list, product_catalog)
        }
    
    def get_cache_key(self, query_name: str, params: Dict, user_id: int) -> str:
        """Generate cache key from query + params"""
        cache_str = f"{query_name}:{json.dumps(params, sort_keys=True)}:{user_id}"
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[Dict]:
        """Get cached result if exists and not expired"""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if datetime.now() < entry['expires_at']:
                return entry['data']
            else:
                del self.cache[cache_key]  # Remove expired
        return None
    
    def set(self, cache_key: str, data: Dict, ttl_seconds: int):
        """Store result in cache"""
        self.cache[cache_key] = {
            'data': data,
            'cached_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=ttl_seconds)
        }
```

#### Enhanced execute_query()

```python
def execute_query(self, query_name: str, user_id: int = None, **parameters):
    """Execute with caching"""
    
    # Check cache first
    cache_key = self.cache.get_cache_key(query_name, parameters, user_id)
    cached_result = self.cache.get(cache_key)
    
    if cached_result:
        cached_result['metadata']['cached'] = True
        cached_result['metadata']['cached_at'] = cached_result['metadata']['cached_at'].isoformat()
        return cached_result
    
    # Execute query
    result = self._execute_query_uncached(query_name, **parameters)
    
    # Cache result
    ttl = self._get_cache_ttl(query_name)
    self.cache.set(cache_key, result, ttl)
    
    result['metadata']['cached'] = False
    return result
```

---

## Sample Queries Analysis

### Query: `monthly_revenue_trend`

**Category:** Sales & Revenue  
**Description:** Monthly revenue trend with order counts and average values  
**Parameters:** months (default: 24)

**SQL:**
```sql
SELECT
    FORMAT(o.OrderDate, 'yyyy-MM') AS YearMonth,
    YEAR(o.OrderDate) AS Year,
    MONTH(o.OrderDate) AS Month,
    SUM(jt.Cost) AS TotalRevenue,
    COUNT(DISTINCT o.OrderID) AS OrderCount,
    COUNT(jt.TicketID) AS JobTicketCount,
    AVG(jt.Cost) AS AvgJobValue,
    SUM(jt.QTY) AS UnitsProduced
FROM Orders o
INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
WHERE o.OrderDate >= DATEADD(MONTH, -6, GETDATE())
    AND jt.Cost IS NOT NULL
GROUP BY FORMAT(o.OrderDate, 'yyyy-MM'), YEAR(o.OrderDate), MONTH(o.OrderDate)
ORDER BY Year DESC, Month DESC
```

**Typical Result Size:** 6-24 rows (small)  
**Cache TTL:** 1 hour (historical data)  
**Visualization:** Line chart with dual axis

---

### Query: `customer_order_history`

**Category:** Customer Analytics  
**Description:** Complete order history for a specific customer  
**Parameters:** customer_name, months_back (default: 12)

**Typical Result Size:** 50-500 rows (medium-large)  
**Cache TTL:** 5 minutes (may change frequently)  
**Optimization:** Good candidate for pagination

---

### Query: `stock_inventory_current`

**Category:** Stock Management  
**Description:** Current stock levels across all locations  
**Parameters:** low_stock_only (boolean)

**Typical Result Size:** 100-1000 rows (large)  
**Cache TTL:** 5 minutes (real-time inventory)  
**Optimization:** Needs export URL for full dataset

---

## Implementation Roadmap

### Sprint 1: Markdown Tables (Week 1)

- [ ] Add `_render_dataframe_markdown()` to QueryLibrary
- [ ] Update `execute_query()` to include `markdown_table`
- [ ] Add `export_options` indicator
- [ ] Test with 5 sample queries
- [ ] Update AI tool wrappers to use markdown_table
- [ ] Validate with real AI conversations

**Deliverables:**
- Enhanced query_library.py
- Test suite for markdown rendering
- Documentation update

---

### Sprint 2: Export Links (Week 2)

- [ ] Add `_export_to_csv()` function
- [ ] Add `_export_to_excel()` function
- [ ] Create `/tmp/query_exports/` directory structure
- [ ] Add Flask route for serving exports
- [ ] Implement file cleanup job (delete after 7 days)
- [ ] Add export links to query results

**Deliverables:**
- Export functions in query_library.py
- Flask download route
- Cleanup cron job

---

### Sprint 3: Database Storage (Week 3-4)

- [ ] Create `query_results` table in Supabase
- [ ] Add `save_query_result()` function
- [ ] Add `get_query_result()` retrieval
- [ ] Add `list_query_history()` for user
- [ ] Update AI tools to save results
- [ ] Add AI tool to retrieve past results
- [ ] Implement auto-cleanup (delete after 30 days)

**Deliverables:**
- Migration script for query_results table
- Storage functions in query_library.py
- New AI tool: `inhouse_get_query_history()`
- Cleanup job

---

### Sprint 4: Caching (Week 5)

- [ ] Implement QueryCache class
- [ ] Add cache checking to execute_query()
- [ ] Define TTL rules per query type
- [ ] Add cache hit metrics
- [ ] Add cache invalidation triggers
- [ ] Add admin tool to clear cache

**Deliverables:**
- QueryCache implementation
- Cache metrics dashboard
- Admin cache management tool

---

## Success Metrics

### Performance

- **Query Response Time:** Reduce by 50% with caching
- **JSON Payload Size:** Reduce by 30% with pagination
- **Database Load:** Reduce repeated queries by 60%

### User Experience

- **Markdown Tables:** 100% of queries return formatted tables
- **Export Links:** 100% of large queries (100+ rows) have export URLs
- **Query Reuse:** Users can reference past results by ID

### System Health

- **Storage Usage:** < 1GB for query_results table
- **Cache Hit Rate:** > 40% for repeated queries
- **Export Cleanup:** 100% of old exports deleted after 7 days

---

## Testing Plan

### Unit Tests

```python
def test_markdown_rendering():
    """Test markdown table generation"""
    df = pd.DataFrame({
        'Month': ['2024-11', '2024-10'],
        'Revenue': [45678.90, 42123.45],
        'Orders': [123, 118]
    })
    
    markdown = query_lib._render_dataframe_markdown(df, 'monthly_revenue_trend', {})
    
    assert '##' in markdown
    assert '| Month |' in markdown
    assert '$45,678.90' in markdown or '45678.90' in markdown

def test_csv_export():
    """Test CSV export creation"""
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    url = query_lib._export_to_csv(df, 'test_query')
    
    assert url.startswith('/downloads/query_exports/')
    assert 'test_query' in url
    assert url.endswith('.csv')

def test_result_storage():
    """Test saving result to database"""
    result = {
        'data': [...],
        'summary': 'Test summary',
        'markdown_table': '...',
        'metadata': {
            'query_name': 'test_query',
            'parameters': {},
            'row_count': 10,
            'execution_time_seconds': 0.05
        }
    }
    
    result_id = query_lib.save_query_result(result, user_id=14, session_id='test-123')
    
    assert result_id is not None
    assert len(result_id) == 36  # UUID format
```

### Integration Tests

```python
def test_full_query_with_markdown():
    """Test complete query flow with markdown"""
    result = query_lib.execute_query('monthly_revenue_trend', months=6)
    
    assert result['success'] == True
    assert 'data' in result
    assert 'markdown_table' in result
    assert 'export_options' in result
    assert '##' in result['markdown_table']
    assert 'Total Rows:' in result['markdown_table']

def test_large_query_with_export():
    """Test large query gets export URL"""
    result = query_lib.execute_query('customer_order_history', 
                                     customer_name='ACME Corp',
                                     months_back=24)
    
    if result['metadata']['row_count'] > 100:
        assert 'export_url' in result
        assert result['export_url'].endswith('.csv')
```

---

## Related Documentation

- **Query Library Inventory:** `QUERY_LIBRARY_COMPLETE_INVENTORY.md`
- **SQL Patterns Analysis:** `SQL_PATTERNS_ANALYSIS.md`
- **Xero Markdown Enhancement:** `XERO_MARKDOWN_ENHANCEMENT_COMPLETE.md`
- **FRED Schema v2.0:** `docs/platforms/inhouse_print_database_schema_v2.md`

---

## Appendix: All 64 Queries

### Sales & Revenue (5)
1. `sales_trend_by_month` - Monthly sales trends
2. `monthly_revenue_trend` - Revenue with order counts
3. `revenue_by_product_type` - Product performance
4. `revenue_by_customer` - Top customers by revenue
5. `daily_sales_snapshot` - Daily sales overview

### Customer Analytics (7)
6. `customer_retention_cohort` - Cohort analysis
7. `customer_order_history` - Customer orders
8. `customer_lifetime_value` - CLV calculation
9. `new_vs_returning_customers` - Customer acquisition
10. `customer_purchase_frequency` - Order patterns
11. `customer_segment_analysis` - Segmentation
12. `dormant_customer_reactivation` - Win-back opportunities

### Product Analysis (6)
13. `top_selling_products` - Best sellers
14. `product_profitability` - Margin analysis
15. `product_combinations` - Bundle analysis
16. `product_seasonality` - Seasonal patterns
17. `product_pricing_analysis` - Price optimization
18. `slow_moving_products` - Inventory concerns

### Stock Management (6)
19. `stock_levels_current` - Current inventory
20. `stock_reorder_recommendations` - Reorder alerts
21. `stock_usage_trends` - Consumption patterns
22. `stock_turnover_rate` - Inventory velocity
23. `stock_waste_analysis` - Material waste
24. `stock_value_summary` - Inventory valuation

### Operational Flow (8)
25. `production_cycle_time` - Job duration analysis
26. `order_fulfillment_time` - Lead time tracking
27. `rush_order_frequency` - Urgency patterns
28. `job_complexity_score` - Complexity analysis
29. `bottleneck_identification` - Process bottlenecks
30. `machine_utilization` - Equipment usage
31. `staff_productivity` - Worker efficiency
32. `quality_issue_tracking` - Defect analysis

### Financial Analysis (2)
33. `invoice_aging_report` - AR aging
34. `payment_collection_rate` - Collection efficiency

### Operational Metrics (4)
35. `order_completion_rate` - Success rate
36. `average_order_value_trend` - AOV trends
37. `order_volume_by_hour` - Capacity planning
38. `quote_conversion_rate` - Sales effectiveness

*... (Plus 26 more queries in other categories)*

---

**End of Document**  
**Status:** Ready for Phase 1 Implementation  
**Next Action:** Implement markdown rendering in query_library.py

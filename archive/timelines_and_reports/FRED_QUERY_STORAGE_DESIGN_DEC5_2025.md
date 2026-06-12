# FRED Query Storage & Smart Routing Design

**Date:** December 5, 2025  
**Status:** Design Complete - Ready for Implementation  
**Goal:** Auto-store query results with intelligent platform routing

---

## Executive Summary

Design a system that:
1. **Auto-stores** query results in appropriate platform (Google Sheets, Excel, Synergy Docs)
2. **Routes intelligently** based on user's OAuth connections
3. **Returns document links** to AI agent with results
4. **Smart caching** with freshness detection
5. **AI-controlled** storage decisions

---

## Solution Architecture

### Flow Diagram

```
User asks question via AI
    ↓
AI calls: inhouse_execute_sql("SELECT...")
    ↓
QueryLibrary.execute_query()
    ↓
┌─────────────────────────────────────┐
│ 1. CHECK CACHE                      │
│    - Is query identical to recent?  │
│    - Is data still fresh?           │
│    - User preference: always fresh? │
└─────────────────────────────────────┘
    ↓ (cache miss or stale)
┌─────────────────────────────────────┐
│ 2. EXECUTE QUERY                    │
│    - Run SQL against FRED           │
│    - Format results (JSON + MD)     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. DETECT USER PLATFORM             │
│    - Check OAuth connections        │
│    - Google? Microsoft? Neither?    │
│    - User preference override?      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. STORE RESULTS                    │
│    Google User → Google Sheets      │
│    Microsoft User → Excel + OneDrive│
│    No OAuth → Synergy Internal Doc  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 5. RETURN TO AI                     │
│    - data: [JSON rows]              │
│    - markdown_table: "..."          │
│    - storage: {                     │
│        platform: "google_sheets",   │
│        document_url: "https://...", │
│        document_id: "abc123",       │
│        stored_at: "2025-12-05..."   │
│      }                              │
│    - cache_info: {...}              │
└─────────────────────────────────────┘
    ↓
AI presents to user:
"Found 47 invoices totaling $123,456.

[Markdown table here]

📊 Full results saved to Google Sheets:
https://docs.google.com/spreadsheets/d/abc123

This data was just queried (live data).
Would you like me to analyze any specific patterns?"
```

---

## Component 1: Platform Detection

### User OAuth Status Check

```python
def detect_user_storage_platform(user_id: int) -> Dict[str, Any]:
    """
    Detect which storage platforms user has connected
    
    Returns:
        {
            "preferred_platform": "google_sheets",  # Primary choice
            "available_platforms": ["google_sheets", "microsoft_excel", "synergy_internal"],
            "oauth_status": {
                "google": True,
                "microsoft": False
            },
            "user_preference": "google_sheets"  # From user settings
        }
    """
    from AI_infrastructure.auth.oauth_credentials_db import (
        get_google_oauth_token,
        get_microsoft_oauth_token
    )
    
    # Check OAuth connections
    google_token = get_google_oauth_token(user_id, platform='google_drive')
    microsoft_token = get_microsoft_oauth_token(user_id, service='onedrive')
    
    has_google = google_token is not None
    has_microsoft = microsoft_token is not None
    
    # Check user preference from database
    user_pref = get_user_storage_preference(user_id)  # New function
    
    # Determine available platforms
    available = ["synergy_internal"]  # Always available
    if has_google:
        available.append("google_sheets")
    if has_microsoft:
        available.append("microsoft_excel")
    
    # Choose preferred platform
    if user_pref and user_pref in available:
        preferred = user_pref
    elif has_google:
        preferred = "google_sheets"
    elif has_microsoft:
        preferred = "microsoft_excel"
    else:
        preferred = "synergy_internal"
    
    return {
        "preferred_platform": preferred,
        "available_platforms": available,
        "oauth_status": {
            "google": has_google,
            "microsoft": has_microsoft
        },
        "user_preference": user_pref
    }
```

---

## Component 2: Smart Caching Logic

### Cache Decision Matrix

| Query Type | Cache TTL | When to Skip Cache | Example Queries |
|------------|-----------|-------------------|-----------------|
| **Real-time** | 2 minutes | Always if user says "latest" | `sales_today`, `orders_pending`, `stock_current` |
| **Recent** | 15 minutes | If user says "refresh" | `sales_this_week`, `recent_orders` |
| **Historical** | 1 hour | If parameters changed | `monthly_revenue_trend`, `customer_history` |
| **Static** | 24 hours | Rarely | `customer_list`, `product_catalog` |

### Cache Key Structure

```python
def generate_cache_key(query_name: str, parameters: Dict, user_id: int) -> str:
    """
    Generate unique cache key
    
    Format: fred_query:{query_name}:{param_hash}:{user_id}
    Example: fred_query:monthly_revenue_trend:a3f2d1:14
    """
    import hashlib
    import json
    
    # Sort parameters for consistent hashing
    param_str = json.dumps(parameters, sort_keys=True)
    param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
    
    return f"fred_query:{query_name}:{param_hash}:{user_id}"

def should_use_cache(query_name: str, parameters: Dict, 
                     force_refresh: bool = False) -> bool:
    """
    Decide if we should use cached results
    
    Args:
        query_name: Name of the query
        parameters: Query parameters
        force_refresh: User explicitly requested fresh data
    
    Returns:
        True if cache is acceptable, False if must re-query
    """
    # NEVER cache if user requested refresh
    if force_refresh:
        return False
    
    # Check if query is marked as "always fresh"
    query_metadata = get_query_metadata(query_name)
    if query_metadata.get('always_fresh', False):
        return False
    
    # Real-time queries: cache for 2 minutes max
    if query_name in ['sales_today', 'orders_pending', 'stock_current']:
        cache_age = get_cache_age(query_name, parameters)
        return cache_age < 120  # 2 minutes
    
    # Recent queries: cache for 15 minutes
    if 'today' in query_name or 'current' in query_name:
        cache_age = get_cache_age(query_name, parameters)
        return cache_age < 900  # 15 minutes
    
    # Historical queries: cache for 1 hour
    if any(word in query_name for word in ['monthly', 'trend', 'history']):
        cache_age = get_cache_age(query_name, parameters)
        return cache_age < 3600  # 1 hour
    
    # Default: use cache if less than 30 minutes old
    cache_age = get_cache_age(query_name, parameters)
    return cache_age < 1800  # 30 minutes
```

### AI Agent Integration

The AI can control caching through parameters:

```python
# AI calls with force_refresh flag
result = execute_query_library(
    query_name='monthly_revenue_trend',
    months=6,
    _force_refresh=True  # ← AI sets this based on user intent
)

# Or AI can ask user:
# "I have cached results from 5 minutes ago. 
#  Would you like me to use those or refresh the data?"
```

**Natural Language Detection:**
- User says "latest", "current", "right now" → `force_refresh=True`
- User says "what did you show me before" → Use cache if available
- Default: Follow cache TTL rules

---

## Component 3: Storage Implementation

### 3A: Google Sheets Storage

```python
def store_in_google_sheets(df: pd.DataFrame, query_name: str, 
                          user_id: int, metadata: Dict) -> Dict[str, str]:
    """
    Store query results in Google Sheets
    
    Returns:
        {
            "platform": "google_sheets",
            "document_url": "https://docs.google.com/spreadsheets/d/...",
            "document_id": "abc123...",
            "sheet_name": "Monthly Revenue Trend - Dec 5, 2025",
            "stored_at": "2025-12-05T14:32:15Z",
            "row_count": 47
        }
    """
    from google_workspace.google_sheets import (
        google_sheets_create,
        google_sheets_append_rows
    )
    
    # Create descriptive title
    timestamp = datetime.now().strftime('%b %d, %Y %I:%M %p')
    sheet_title = f"{query_name.replace('_', ' ').title()} - {timestamp}"
    
    # Prepare data
    headers = df.columns.tolist()
    # Use formatted columns if available
    data_rows = []
    for _, row in df.iterrows():
        row_data = []
        for col in df.columns:
            if not col.endswith('_Formatted'):
                formatted_col = f"{col}_Formatted"
                if formatted_col in df.columns:
                    row_data.append(str(row[formatted_col]))
                else:
                    row_data.append(str(row[col]))
        data_rows.append(row_data)
    
    # Create spreadsheet
    result = google_sheets_create(
        title=sheet_title,
        user_id=user_id,
        _injected_credentials=True
    )
    
    spreadsheet_id = result['spreadsheet_id']
    spreadsheet_url = result['spreadsheet_url']
    
    # Add query metadata as first sheet
    metadata_sheet = [
        ["Query Information", ""],
        ["Query Name", query_name],
        ["Executed At", metadata.get('executed_at', datetime.now().isoformat())],
        ["Parameters", json.dumps(metadata.get('parameters', {}))],
        ["Row Count", str(metadata.get('row_count', len(df)))],
        ["Execution Time", f"{metadata.get('execution_time_seconds', 0):.3f}s"],
        ["", ""],
        ["Data Quality", ""],
        ["Null Values", str(metadata.get('data_quality', {}).get('null_counts', 'N/A'))],
        ["Duplicates", str(metadata.get('data_quality', {}).get('duplicate_rows', 0))]
    ]
    
    # Append metadata
    google_sheets_append_rows(
        spreadsheet_id=spreadsheet_id,
        range_name="Metadata!A1",
        values=metadata_sheet,
        user_id=user_id,
        _injected_credentials=True
    )
    
    # Append actual data
    google_sheets_append_rows(
        spreadsheet_id=spreadsheet_id,
        range_name="Results!A1",
        values=[headers] + data_rows,
        user_id=user_id,
        _injected_credentials=True
    )
    
    return {
        "platform": "google_sheets",
        "document_url": spreadsheet_url,
        "document_id": spreadsheet_id,
        "sheet_name": sheet_title,
        "stored_at": datetime.now().isoformat(),
        "row_count": len(df)
    }
```

### 3B: Microsoft Excel + OneDrive Storage

```python
def store_in_microsoft_excel(df: pd.DataFrame, query_name: str,
                             user_id: int, metadata: Dict) -> Dict[str, str]:
    """
    Store query results in Excel file on OneDrive
    
    Returns:
        {
            "platform": "microsoft_excel",
            "document_url": "https://onedrive.live.com/...",
            "document_id": "file_id_123",
            "file_name": "Monthly_Revenue_Trend_Dec_5_2025.xlsx",
            "stored_at": "2025-12-05T14:32:15Z",
            "row_count": 47
        }
    """
    from microsoft_excel_tools import create_excel_workbook
    from microsoft_onedrive_tools import upload_file
    import io
    
    # Create Excel file in memory
    timestamp = datetime.now().strftime('%b_%d_%Y_%I%M_%p')
    filename = f"{query_name}_{timestamp}.xlsx"
    
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Write metadata sheet
        metadata_df = pd.DataFrame([
            ['Query Name', query_name],
            ['Executed At', metadata.get('executed_at', datetime.now().isoformat())],
            ['Parameters', json.dumps(metadata.get('parameters', {}))],
            ['Row Count', metadata.get('row_count', len(df))],
            ['Execution Time', f"{metadata.get('execution_time_seconds', 0):.3f}s"]
        ], columns=['Property', 'Value'])
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        # Write results sheet (use formatted values)
        result_df = df.copy()
        # Remove _Formatted duplicate columns, but use their values
        for col in df.columns:
            if col.endswith('_Formatted'):
                base_col = col.replace('_Formatted', '')
                if base_col in result_df.columns:
                    result_df[base_col] = df[col]
                result_df.drop(col, axis=1, inplace=True)
        
        result_df.to_excel(writer, sheet_name='Results', index=False)
    
    buffer.seek(0)
    
    # Upload to OneDrive in "Query Results" folder
    upload_result = upload_file(
        file_content=buffer.read(),
        file_name=filename,
        folder_path="Query Results",
        user_id=user_id,
        _injected_credentials=True
    )
    
    return {
        "platform": "microsoft_excel",
        "document_url": upload_result['web_url'],
        "document_id": upload_result['file_id'],
        "file_name": filename,
        "stored_at": datetime.now().isoformat(),
        "row_count": len(df)
    }
```

### 3C: Synergy Internal Document Storage

```python
def store_in_synergy_internal(df: pd.DataFrame, query_name: str,
                              user_id: int, session_id: str,
                              metadata: Dict) -> Dict[str, str]:
    """
    Store query results in Synergy's internal document system
    
    Creates a session-linked document in Supabase
    
    Returns:
        {
            "platform": "synergy_internal",
            "document_url": "/query-results/abc-123-def-456",
            "document_id": "abc-123-def-456",
            "document_title": "Monthly Revenue Trend - Dec 5, 2025",
            "stored_at": "2025-12-05T14:32:15Z",
            "row_count": 47
        }
    """
    from AI_infrastructure.shared.supabase_client import get_supabase_client
    import uuid
    
    supabase = get_supabase_client()
    
    # Generate document ID
    doc_id = str(uuid.uuid4())
    
    # Create document title
    timestamp = datetime.now().strftime('%b %d, %Y %I:%M %p')
    doc_title = f"{query_name.replace('_', ' ').title()} - {timestamp}"
    
    # Convert DataFrame to JSON (use formatted values where available)
    data_json = []
    for _, row in df.iterrows():
        row_data = {}
        for col in df.columns:
            if not col.endswith('_Formatted'):
                formatted_col = f"{col}_Formatted"
                if formatted_col in df.columns:
                    row_data[col] = str(row[formatted_col])  # Use formatted
                else:
                    row_data[col] = row[col]  # Use raw
        data_json.append(row_data)
    
    # Create Markdown content
    markdown_content = f"# {doc_title}\n\n"
    markdown_content += f"**Query:** {query_name}\n"
    markdown_content += f"**Executed:** {metadata.get('executed_at', datetime.now().isoformat())}\n"
    markdown_content += f"**Parameters:** {json.dumps(metadata.get('parameters', {}), indent=2)}\n"
    markdown_content += f"**Rows:** {metadata.get('row_count', len(df))}\n\n"
    markdown_content += "## Results\n\n"
    
    # Build table
    headers = [col for col in df.columns if not col.endswith('_Formatted')]
    markdown_content += "| " + " | ".join(headers) + " |\n"
    markdown_content += "|" + "---|" * len(headers) + "\n"
    
    for _, row in df.iterrows():
        values = []
        for col in headers:
            formatted_col = f"{col}_Formatted"
            if formatted_col in df.columns:
                values.append(str(row[formatted_col]))
            else:
                values.append(str(row[col]))
        markdown_content += "| " + " | ".join(values) + " |\n"
    
    # Store in database
    supabase.table('query_documents').insert({
        'document_id': doc_id,
        'user_id': user_id,
        'session_id': session_id,
        'document_title': doc_title,
        'query_name': query_name,
        'parameters': metadata.get('parameters', {}),
        'executed_at': metadata.get('executed_at', datetime.now().isoformat()),
        'row_count': metadata.get('row_count', len(df)),
        'execution_time_ms': int(metadata.get('execution_time_seconds', 0) * 1000),
        'data_json': data_json,
        'markdown_content': markdown_content,
        'metadata': metadata,
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
    }).execute()
    
    return {
        "platform": "synergy_internal",
        "document_url": f"/query-results/{doc_id}",
        "document_id": doc_id,
        "document_title": doc_title,
        "stored_at": datetime.now().isoformat(),
        "row_count": len(df)
    }
```

---

## Component 4: Enhanced execute_query()

### Updated Implementation

```python
def execute_query(self, query_name: str, user_id: int = None, 
                 session_id: str = None, _force_refresh: bool = False,
                 _storage_platform: str = None, **parameters) -> Dict[str, Any]:
    """
    Execute query with smart caching and auto-storage
    
    Args:
        query_name: Name of query to execute
        user_id: User ID for OAuth and storage
        session_id: Session ID for linking documents
        _force_refresh: Skip cache, always execute fresh
        _storage_platform: Override platform ("google_sheets", "microsoft_excel", "synergy_internal", or None to disable)
        **parameters: Query parameters
    
    Returns:
        {
            "success": True,
            "data": [...],
            "markdown_table": "...",
            "summary": "...",
            "storage": {
                "platform": "google_sheets",
                "document_url": "https://...",
                "document_id": "abc123",
                "stored_at": "2025-12-05T14:32:15Z"
            },
            "cache_info": {
                "cache_hit": False,
                "cache_age_seconds": 0,
                "query_executed_at": "2025-12-05T14:32:15Z"
            },
            "metadata": {...}
        }
    """
    try:
        # STEP 1: Check cache (unless force refresh)
        cache_hit = False
        cache_age = 0
        
        if not _force_refresh and should_use_cache(query_name, parameters):
            cache_key = generate_cache_key(query_name, parameters, user_id)
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                cached_result['cache_info'] = {
                    'cache_hit': True,
                    'cache_age_seconds': cache_age,
                    'cached_at': cached_result.get('cached_at')
                }
                return cached_result
        
        # STEP 2: Execute query (cache miss or forced refresh)
        query_result = self.build_query(query_name, **parameters)
        sql = query_result['sql']
        metadata = query_result['metadata']
        
        start_time = datetime.now()
        df = self.db.execute_query(sql)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        if df is None or df.empty:
            return {
                'success': True,
                'data': [],
                'markdown_table': f"## {query_name}\n\nNo results found.",
                'summary': f"Query '{query_name}' returned no results",
                'storage': None,
                'cache_info': {'cache_hit': False},
                'metadata': {**metadata, 'row_count': 0}
            }
        
        # STEP 3: Format data
        formatted_df = self._format_dataframe(df, metadata)
        markdown_table = self._render_dataframe_markdown(formatted_df, query_name, metadata)
        summary = self._generate_summary(formatted_df, query_name, metadata)
        
        # Convert to JSON (remove duplicate _Formatted columns)
        data_json = []
        for _, row in formatted_df.iterrows():
            row_dict = {}
            for col in formatted_df.columns:
                if not col.endswith('_Formatted'):
                    row_dict[col] = row[col]
            data_json.append(row_dict)
        
        # STEP 4: Detect storage platform
        storage_info = None
        if user_id and (_storage_platform or _storage_platform != "none"):
            platform_detection = detect_user_storage_platform(user_id)
            
            # Use override or detected platform
            target_platform = _storage_platform or platform_detection['preferred_platform']
            
            # Store results
            try:
                if target_platform == "google_sheets" and platform_detection['oauth_status']['google']:
                    storage_info = store_in_google_sheets(formatted_df, query_name, user_id, {
                        **metadata,
                        'executed_at': start_time.isoformat(),
                        'execution_time_seconds': execution_time,
                        'parameters': parameters
                    })
                
                elif target_platform == "microsoft_excel" and platform_detection['oauth_status']['microsoft']:
                    storage_info = store_in_microsoft_excel(formatted_df, query_name, user_id, {
                        **metadata,
                        'executed_at': start_time.isoformat(),
                        'execution_time_seconds': execution_time,
                        'parameters': parameters
                    })
                
                else:  # Fallback to synergy_internal
                    storage_info = store_in_synergy_internal(formatted_df, query_name, user_id, session_id, {
                        **metadata,
                        'executed_at': start_time.isoformat(),
                        'execution_time_seconds': execution_time,
                        'parameters': parameters
                    })
                
            except Exception as storage_error:
                # Don't fail query if storage fails
                print(f"[WARN] Storage failed: {storage_error}")
                storage_info = {
                    "platform": "none",
                    "error": str(storage_error)
                }
        
        # STEP 5: Build result
        result = {
            'success': True,
            'data': data_json,
            'markdown_table': markdown_table,
            'summary': summary,
            'storage': storage_info,
            'cache_info': {
                'cache_hit': False,
                'cache_age_seconds': 0,
                'query_executed_at': start_time.isoformat()
            },
            'metadata': {
                **metadata,
                'query_name': query_name,
                'parameters': parameters,
                'row_count': len(formatted_df),
                'execution_time_seconds': round(execution_time, 3)
            }
        }
        
        # STEP 6: Cache result
        cache_key = generate_cache_key(query_name, parameters, user_id)
        ttl = self._get_cache_ttl(query_name)
        result['cached_at'] = start_time.isoformat()
        self.cache.set(cache_key, result, ttl)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': [],
            'markdown_table': '',
            'summary': f"Error executing query: {str(e)}",
            'storage': None,
            'cache_info': {'cache_hit': False}
        }
```

---

## Component 5: Database Schema

### New Table: query_documents

```sql
CREATE TABLE query_documents (
    document_id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    session_id UUID REFERENCES sessions(session_id),
    
    -- Document info
    document_title TEXT NOT NULL,
    query_name TEXT NOT NULL,
    parameters JSONB,
    
    -- Execution metadata
    executed_at TIMESTAMP NOT NULL,
    row_count INTEGER,
    execution_time_ms INTEGER,
    
    -- Data storage
    data_json JSONB,  -- Full result data
    markdown_content TEXT,  -- Markdown formatted
    
    -- External storage (if applicable)
    external_platform TEXT,  -- "google_sheets", "microsoft_excel", null
    external_document_url TEXT,
    external_document_id TEXT,
    
    -- Additional metadata
    metadata JSONB,
    
    -- Lifecycle
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '30 days'),
    
    -- Indexes
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_query_docs_user ON query_documents(user_id);
CREATE INDEX idx_query_docs_session ON query_documents(session_id);
CREATE INDEX idx_query_docs_query ON query_documents(query_name);
CREATE INDEX idx_query_docs_expires ON query_documents(expires_at);
```

### New Table: user_storage_preferences

```sql
CREATE TABLE user_storage_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id),
    
    -- Platform preference
    preferred_platform TEXT,  -- "google_sheets", "microsoft_excel", "synergy_internal", "auto"
    
    -- Auto-storage settings
    auto_store_queries BOOLEAN DEFAULT TRUE,
    storage_retention_days INTEGER DEFAULT 30,
    
    -- Per-query-type overrides
    real_time_queries_platform TEXT,  -- Can override for real-time data
    historical_queries_platform TEXT,  -- Can override for historical data
    
    -- Caching preferences
    allow_cached_results BOOLEAN DEFAULT TRUE,
    max_cache_age_minutes INTEGER DEFAULT 30,
    
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Component 6: AI Agent Usage Examples

### Example 1: Basic Query (Auto-storage)

**User:** "Show me revenue for the last 6 months"

**AI calls:**
```python
result = inhouse_execute_sql(
    query_name='monthly_revenue_trend',
    months=6,
    user_id=14,
    session_id='abc-123'
)
```

**AI receives:**
```json
{
    "success": true,
    "data": [...47 rows...],
    "markdown_table": "## Monthly Revenue Trend\n\n| Month | Revenue |...",
    "summary": "6 months analyzed. Total: $234,567.89",
    "storage": {
        "platform": "google_sheets",
        "document_url": "https://docs.google.com/spreadsheets/d/abc123",
        "document_id": "abc123",
        "stored_at": "2025-12-05T14:32:15Z"
    },
    "cache_info": {
        "cache_hit": false,
        "query_executed_at": "2025-12-05T14:32:15Z"
    }
}
```

**AI responds:**
```
Found your revenue data for the last 6 months:

## Monthly Revenue Trend

| Month | Revenue | Orders | Avg Order Value |
|-------|---------|--------|-----------------|
| Nov 2024 | $45,678.90 | 123 | $371.29 |
| Oct 2024 | $42,123.45 | 118 | $357.13 |
...

**Total Revenue:** $234,567.89  
**Average Monthly Orders:** 120

📊 **Full details saved to your Google Sheets:**
https://docs.google.com/spreadsheets/d/abc123

This data was just queried (live from database).
```

---

### Example 2: User Requests Fresh Data

**User:** "Get me the LATEST sales numbers"

**AI detects keywords:** "LATEST" → Sets `_force_refresh=True`

**AI calls:**
```python
result = inhouse_execute_sql(
    query_name='sales_today',
    _force_refresh=True,  # ← Skip cache
    user_id=14,
    session_id='abc-123'
)
```

**AI receives:**
```json
{
    "cache_info": {
        "cache_hit": false,
        "cache_age_seconds": 0,
        "query_executed_at": "2025-12-05T14:35:22Z"
    }
}
```

**AI responds:**
```
Here are TODAY'S sales numbers (just queried):

[Results...]

📊 Saved to: https://docs.google.com/spreadsheets/d/def456

✓ This is live data from 30 seconds ago.
```

---

### Example 3: User Wants Cached Results

**User:** "What was that revenue report you showed me earlier?"

**AI detects:** User wants historical result, not fresh query

**AI calls:**
```python
# Option A: Use cache automatically (within TTL)
result = inhouse_execute_sql(
    query_name='monthly_revenue_trend',
    months=6,
    user_id=14,
    # Cache will be used if available
)

# Option B: Retrieve from query_documents
history = inhouse_get_query_history(
    user_id=14,
    query_name='monthly_revenue_trend',
    limit=1
)
```

**AI responds:**
```
Here's the revenue report from 15 minutes ago:

[Shows cached markdown_table]

📊 Original Google Sheets link:
https://docs.google.com/spreadsheets/d/abc123

⏱️ Cached result (15 minutes old)
Would you like me to refresh this with current data?
```

---

### Example 4: User Overrides Storage Platform

**User:** "Can you run that query again but save it to Excel this time?"

**AI calls:**
```python
result = inhouse_execute_sql(
    query_name='customer_order_history',
    customer_name='ACME Corp',
    _force_refresh=True,
    _storage_platform='microsoft_excel',  # ← Override
    user_id=14,
    session_id='abc-123'
)
```

**AI receives:**
```json
{
    "storage": {
        "platform": "microsoft_excel",
        "document_url": "https://onedrive.live.com/...",
        "file_name": "customer_order_history_Dec_5_2025.xlsx"
    }
}
```

---

## Component 7: Implementation Checklist

### Phase 1: Platform Detection (1 hour)
- [ ] Add `detect_user_storage_platform()` function
- [ ] Check Google OAuth status
- [ ] Check Microsoft OAuth status
- [ ] Create `user_storage_preferences` table
- [ ] Add functions to get/set user preferences

### Phase 2: Storage Functions (3-4 hours)
- [ ] Implement `store_in_google_sheets()`
- [ ] Implement `store_in_microsoft_excel()`
- [ ] Implement `store_in_synergy_internal()`
- [ ] Create `query_documents` table
- [ ] Test each storage method

### Phase 3: Cache Logic (2 hours)
- [ ] Implement cache key generation
- [ ] Implement `should_use_cache()` logic
- [ ] Add cache TTL rules by query type
- [ ] Test cache hit/miss scenarios

### Phase 4: Integration (2 hours)
- [ ] Update `execute_query()` with all components
- [ ] Add `_force_refresh` parameter
- [ ] Add `_storage_platform` parameter override
- [ ] Update AI tool wrappers
- [ ] Add `inhouse_get_query_history()` tool

### Phase 5: Testing (2 hours)
- [ ] Test with Google-authenticated user
- [ ] Test with Microsoft-authenticated user
- [ ] Test with no OAuth (Synergy only)
- [ ] Test cache behavior
- [ ] Test force refresh
- [ ] Test platform override

### Phase 6: Documentation (1 hour)
- [ ] Update tool schemas
- [ ] Add usage examples
- [ ] Document cache behavior
- [ ] Create user guide

**Total Effort:** ~11-13 hours

---

## Success Metrics

- ✅ **100% of queries auto-stored** in user's preferred platform
- ✅ **Cache hit rate > 40%** for repeated queries
- ✅ **< 2 seconds** additional time for storage
- ✅ **Zero storage failures** (graceful fallbacks)
- ✅ **30-day retention** with auto-cleanup

---

**End of Design**  
**Status:** Ready for Implementation  
**Next Action:** Begin Phase 1 (Platform Detection)

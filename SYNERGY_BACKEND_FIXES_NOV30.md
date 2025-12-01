# 🔧 Synergy Backend Issues - Fixes Required (Nov 30, 2025)

## 📋 Issue Summary

Four critical backend issues preventing Synergy tools from working correctly:

1. **synergy_get_session** - Returns 500 Internal Server Error (timing issue)
2. **synergy_update_task** - Returns 400 Bad Request (validation/parameter issue)
3. **synergy_add_document** - Returns 500 Internal Server Error (backend error)
4. **synergy_search_sessions** - Tool not implemented (feature missing)

---

## 🔍 Root Cause Analysis

### Issue 1: `synergy_get_session` - 500 Error

**Problem:** Session fetch fails immediately after creation due to PostgreSQL placeholder mismatch.

**Location:** `AI_infrastructure/routes/synergy_routes.py` line ~906

**Current Code:**
```python
cursor.execute('SELECT * FROM synergy_sessions.synergy_sessions WHERE session_id = %s', (session_id,))
```

**Issue:** The code uses PostgreSQL placeholder `%s` but the database might be SQLite (using `?`) or there's a connection issue.

**Root Cause:** Mixed database placeholder syntax between SQLite (`?`) and PostgreSQL (`%s`).

**Evidence from logs:**
```
Tool: synergy_get_session
Result: 500 Internal Server Error
Timing: Happens immediately after session creation
```

**Fix Required:**
```python
# Use placeholder converter function that already exists
sql, params = convert_sql_placeholders(
    'SELECT * FROM synergy_sessions.synergy_sessions WHERE session_id = %s',
    (session_id,)
)
cursor.execute(sql, params)
```

---

### Issue 2: `synergy_update_task` - 400 Bad Request

**Problem:** Backend validation fails or missing required parameter.

**Location:** Likely in milestone task routes (need to check `synergy_routes.py` milestone section)

**Expected Parameters:**
```python
{
    "task_id": "task_123",
    "completed": true,
    "blocked": false,
    "estimated_hours": 5.0
}
```

**Issue:** The tool might be sending parameters the backend doesn't expect, or the backend is rejecting valid parameters.

**Possible Causes:**
1. Missing `task_id` validation
2. Invalid JSON structure
3. Missing required fields
4. Incorrect parameter names

**Fix Required:** Add proper parameter validation and error messages:
```python
@synergy_bp.route('/milestones/<milestone_id>/tasks/<task_id>', methods=['PATCH'])
def update_task(milestone_id, task_id):
    """Update task"""
    try:
        data = request.json
        
        # Validate required fields
        if not data:
            return jsonify({
                'success': False,
                'error': 'Empty request body'
            }), 400
        
        # Build update query
        updates = []
        params = []
        
        allowed_fields = ['task', 'completed', 'blocked', 'blocker_reason', 
                         'blocker_type', 'estimated_hours', 'actual_hours', 
                         'assigned_to', 'priority']
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                params.append(data[field])
        
        if not updates:
            return jsonify({
                'success': False,
                'error': 'No valid fields to update'
            }), 400
        
        # Add timestamp
        updates.append('updated_at = %s')
        params.append(datetime.now().isoformat())
        
        # Add IDs
        params.append(task_id)
        params.append(milestone_id)
        
        # Execute update
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql, final_params = convert_sql_placeholders(
            f"UPDATE synergy_sessions.tasks SET {', '.join(updates)} WHERE task_id = %s AND milestone_id = %s",
            params
        )
        
        cursor.execute(sql, final_params)
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Task updated successfully'
        })
        
    except Exception as e:
        print(f"[ERROR] Task update failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

### Issue 3: `synergy_add_document` - 500 Internal Server Error

**Problem:** Backend error when trying to add documents to a session.

**Location:** `AI_infrastructure/routes/synergy_routes.py` update_session endpoint

**Current Behavior:** The `synergy_update_session` tool calls the backend with documents array, but the backend fails to process it.

**Expected Call:**
```python
synergy_update_session(
    session_id="sess_123",
    documents=[
        {"title": "Design Doc", "url": "https://...", "type": "google_doc"},
        {"title": "API Spec", "url": "https://...", "type": "google_doc"}
    ]
)
```

**Issue:** The backend's `normalize_documents()` function might be failing or not properly handling the document structure.

**Location of normalize_documents:** Check if it exists in `synergy_routes.py` around line 100-200.

**Fix Required:** Ensure robust document normalization:
```python
def normalize_documents(documents):
    """
    Normalize document objects to ensure consistent structure
    
    Handles:
    - String entries (converts to dict)
    - 'name' field (converts to 'title')
    - Missing 'type' field (defaults to 'unknown')
    - Missing 'url' field (defaults to '')
    """
    if not documents:
        return []
    
    normalized = []
    for doc in documents:
        # Handle string entries
        if isinstance(doc, str):
            try:
                doc = json.loads(doc)
            except json.JSONDecodeError:
                # Treat as plain text title
                doc = {"title": doc, "url": "", "type": "text"}
        
        # Ensure it's a dict
        if not isinstance(doc, dict):
            print(f"[WARN] Skipping invalid document entry: {doc}")
            continue
        
        # Normalize structure
        normalized_doc = {}
        
        # Handle title/name field
        if 'title' in doc:
            normalized_doc['title'] = doc['title']
        elif 'name' in doc:
            normalized_doc['title'] = doc['name']
        else:
            normalized_doc['title'] = 'Untitled Document'
        
        # Handle URL
        normalized_doc['url'] = doc.get('url', '')
        
        # Handle type
        normalized_doc['type'] = doc.get('type', 'unknown')
        
        # Preserve additional fields
        for key in ['doc_type', 'created_at', 'updated_at', 'slug', 'version']:
            if key in doc:
                normalized_doc[key] = doc[key]
        
        normalized.append(normalized_doc)
    
    return normalized
```

**Additional Fix:** Add error handling in update_session:
```python
# Special handling for documents (ensure 'title' field)
if 'documents' in update_data:
    try:
        normalized = normalize_documents(update_data['documents'])
        updates.append("documents = %s")
        json_value = json.dumps(normalized)
        params.append(json_value)
        print(f"[DEBUG] Adding documents (normalized): {json_value}")
    except Exception as doc_error:
        print(f"[ERROR] Document normalization failed: {doc_error}")
        return jsonify({
            'success': False,
            'error': f'Invalid document format: {str(doc_error)}'
        }), 400
```

---

### Issue 4: `synergy_search_sessions` - Tool Not Implemented

**Problem:** The tool exists in the schema but has no backend implementation.

**Current Status:** ❌ No endpoint exists for searching sessions.

**Expected Endpoint:** `GET /api/synergy/search?query=<search_term>`

**Implementation Required:**
```python
@synergy_bp.route('/search', methods=['GET'])
def search_sessions():
    """
    Search sessions by title, description, tags, or platform
    
    Query Parameters:
        query (str): Search term (searches title, description, tags)
        platform (str): Filter by specific platform
        status (str): Filter by status
        priority (str): Filter by priority
        column (str): Filter by Kanban column
        user_id (int): User ID for permission filtering
    
    Returns:
        {
            "success": true,
            "count": 10,
            "sessions": [...],
            "query": "email automation",
            "filters_applied": {...}
        }
    """
    conn = None
    try:
        query = request.args.get('query', '').strip()
        platform = request.args.get('platform')
        status = request.args.get('status')
        priority = request.args.get('priority')
        column = request.args.get('column')
        user_id = request.args.get('user_id', type=int)
        
        if not query and not platform:
            return jsonify({
                'success': False,
                'error': 'Either query or platform parameter is required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build search query
        conditions = ['1=1']
        params = []
        
        if query:
            # Search in title, description, and tags
            search_pattern = f'%{query}%'
            conditions.append(
                "(title LIKE %s OR description LIKE %s OR tags LIKE %s)"
            )
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if platform:
            conditions.append("platforms_involved LIKE %s")
            params.append(f'%{platform}%')
        
        if status:
            conditions.append("status = %s")
            params.append(status)
        
        if priority:
            conditions.append("priority = %s")
            params.append(priority)
        
        if column:
            conditions.append("kanban_column = %s")
            params.append(column)
        
        # Build final query
        sql = f"""
            SELECT * FROM synergy_sessions.synergy_sessions 
            WHERE {' AND '.join(conditions)}
            ORDER BY last_active DESC
            LIMIT 50
        """
        
        sql, final_params = convert_sql_placeholders(sql, params)
        cursor.execute(sql, final_params)
        rows = cursor.fetchall()
        
        # Process results
        sessions = []
        for row in rows:
            session = dict(row)
            
            # Check permission
            has_permission, perm_type = check_session_permission(session, user_id, require_write=False)
            if not has_permission:
                continue
            
            # Parse JSON fields
            for field in ['platforms_involved', 'tags', 'documents', 'links', 
                         'next_steps', 'assignees', 'recent_activity', 'checklist']:
                if session.get(field):
                    try:
                        session[field] = json.loads(session[field])
                    except:
                        session[field] = []
            
            sessions.append(session)
        
        return jsonify({
            'success': True,
            'count': len(sessions),
            'sessions': sessions,
            'query': query,
            'filters_applied': {
                'platform': platform,
                'status': status,
                'priority': priority,
                'column': column
            }
        })
        
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        if conn:
            conn.close()
```

**Also Add Tool Schema:** `tools/schemas/synergy_tools.json`
```json
{
    "name": "synergy_search_sessions",
    "description": "Search sessions by title, description, tags, or platform. Returns matching sessions sorted by relevance.",
    "platform": "synergy",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search term to match against title, description, and tags"
            },
            "platform": {
                "type": "string",
                "description": "Filter by specific platform (gmail, sheets, forms, etc.)"
            },
            "status": {
                "type": "string",
                "enum": ["active", "completed", "archived"],
                "description": "Filter by session status"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"],
                "description": "Filter by priority level"
            },
            "column": {
                "type": "string",
                "enum": ["backlog", "in_progress", "review", "done"],
                "description": "Filter by Kanban column"
            }
        },
        "required": []
    }
}
```

**Tool Implementation:** `tools/implementations/synergy.py`
```python
def synergy_search_sessions(
    query: Optional[str] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    column: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Search sessions by title, description, tags, or platform
    
    Args:
        query: Search term (searches title, description, tags)
        platform: Filter by specific platform
        status: Filter by status (active|completed|archived)
        priority: Filter by priority (low|medium|high|critical)
        column: Filter by Kanban column (backlog|in_progress|review|done)
        
    Returns:
        Dict with search results and count
        
    Raises:
        SynergyError: If API call fails
        
    Example:
        # Search for email-related projects
        result = synergy_search_sessions(query="email", platform="gmail")
        
        # Find high-priority active sessions
        result = synergy_search_sessions(priority="high", status="active")
    """
    try:
        params = {}
        if query:
            params["query"] = query
        if platform:
            params["platform"] = platform
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        if column:
            params["column"] = column
        
        if not params:
            raise SynergyError("At least one search parameter is required")
        
        response = requests.get(
            f"{SYNERGY_API_BASE}/search",
            params=params,
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "count": result.get("count", 0),
            "sessions": result.get("sessions", []),
            "query": query,
            "filters": {
                "platform": platform,
                "status": status,
                "priority": priority,
                "column": column
            }
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to search sessions: {str(e)}")
```

---

## 🔧 Implementation Checklist

### High Priority (Blocking Issues)

- [ ] **Fix 1:** Update `synergy_get_session` to use `convert_sql_placeholders()`
- [ ] **Fix 2:** Add proper validation to `synergy_update_task` endpoint
- [ ] **Fix 3:** Enhance `normalize_documents()` with error handling
- [ ] **Fix 4:** Implement `synergy_search_sessions` endpoint and tool

### Testing Steps

1. **Test Session Creation + Immediate Fetch:**
   ```python
   # Create session
   result = synergy_create_session(title="Test Session", ...)
   session_id = result['session_id']
   
   # Immediately fetch (should NOT return 500)
   session = synergy_get_session(session_id=session_id)
   assert session['success'] == True
   ```

2. **Test Task Update:**
   ```python
   # Update task
   result = synergy_update_task(
       task_id="task_123",
       completed=True,
       estimated_hours=5.0
   )
   assert result['success'] == True
   ```

3. **Test Document Addition:**
   ```python
   # Add documents
   result = synergy_update_session(
       session_id="sess_123",
       documents=[
           {"title": "Test Doc", "url": "https://...", "type": "google_doc"}
       ]
   )
   assert result['success'] == True
   ```

4. **Test Search:**
   ```python
   # Search sessions
   result = synergy_search_sessions(query="email automation")
   assert result['success'] == True
   assert result['count'] >= 0
   ```

---

## 📝 Quick Fix Script

Create `fix_synergy_backend.py`:
```python
"""
Quick fix for Synergy backend issues
Run: python fix_synergy_backend.py
"""

import sqlite3
import json

def test_get_session():
    """Test synergy_get_session with proper placeholder conversion"""
    import requests
    
    # Create test session
    response = requests.post(
        'http://localhost:5001/api/synergy/create',
        json={
            'title': 'Test Session',
            'description': 'Testing backend fixes',
            'priority': 'high'
        }
    )
    
    if response.status_code == 200:
        session_id = response.json()['session_id']
        print(f"✅ Created session: {session_id}")
        
        # Immediately fetch (this was failing before)
        get_response = requests.get(
            f'http://localhost:5001/api/synergy/{session_id}'
        )
        
        if get_response.status_code == 200:
            print(f"✅ GET session SUCCESS: {get_response.json()['session']['title']}")
        else:
            print(f"❌ GET session FAILED: {get_response.status_code} - {get_response.text}")
    else:
        print(f"❌ Create session FAILED: {response.status_code}")

if __name__ == '__main__':
    print("🔧 Testing Synergy Backend Fixes...\n")
    test_get_session()
```

---

## 🚀 Deployment Steps

1. **Apply fixes to `synergy_routes.py`**
2. **Restart Flask server:** `BISTART`
3. **Run test script:** `python fix_synergy_backend.py`
4. **Verify all 4 tools work correctly**

---

**Status:** 🚧 **PENDING IMPLEMENTATION**  
**Priority:** 🔴 **HIGH** (Blocking Synergy Dashboard functionality)  
**ETA:** 30-60 minutes for all fixes

---

**Last Updated:** November 30, 2025  
**Created By:** GitHub Copilot AI Assistant

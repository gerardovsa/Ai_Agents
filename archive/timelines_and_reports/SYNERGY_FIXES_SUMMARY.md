# 🎯 Synergy Backend Issues - Quick Summary (Nov 30, 2025)

## 🚨 4 Critical Issues Identified

### 1️⃣ **synergy_get_session** - 500 Internal Server Error

**Problem:** Session fetch fails immediately after creation  
**Cause:** Mixed SQL placeholder syntax (SQLite `?` vs PostgreSQL `%s`)  
**Location:** `AI_infrastructure/routes/synergy_routes.py` line ~906  

**Quick Fix:**
```python
# BEFORE (broken):
cursor.execute('SELECT * FROM synergy_sessions.synergy_sessions WHERE session_id = %s', (session_id,))

# AFTER (fixed):
sql, params = convert_sql_placeholders(
    'SELECT * FROM synergy_sessions.synergy_sessions WHERE session_id = %s',
    (session_id,)
)
cursor.execute(sql, params)
```

---

### 2️⃣ **synergy_update_task** - 400 Bad Request

**Problem:** Backend rejects task updates  
**Cause:** Missing validation or incorrect parameter handling  
**Location:** Milestone task routes in `synergy_routes.py`  

**Quick Fix:** Add proper validation:
```python
@synergy_bp.route('/milestones/<milestone_id>/tasks/<task_id>', methods=['PATCH'])
def update_task(milestone_id, task_id):
    data = request.json
    
    # Validate required fields
    if not data:
        return jsonify({'success': False, 'error': 'Empty request body'}), 400
    
    # Build update query with allowed fields
    allowed_fields = ['task', 'completed', 'blocked', 'blocker_reason', 
                     'estimated_hours', 'actual_hours', 'assigned_to', 'priority']
    
    updates = []
    params = []
    
    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = %s")
            params.append(data[field])
    
    if not updates:
        return jsonify({'success': False, 'error': 'No valid fields'}), 400
    
    # Execute update with placeholder conversion
    sql, final_params = convert_sql_placeholders(
        f"UPDATE synergy_sessions.tasks SET {', '.join(updates)} WHERE task_id = %s",
        params + [task_id]
    )
    cursor.execute(sql, final_params)
```

---

### 3️⃣ **synergy_add_document** - 500 Internal Server Error

**Problem:** Backend fails to process document additions  
**Cause:** `normalize_documents()` function failing on invalid input  
**Location:** `synergy_routes.py` update_session endpoint  

**Quick Fix:** Enhance normalize_documents:
```python
def normalize_documents(documents):
    """Robust document normalization with error handling"""
    if not documents:
        return []
    
    normalized = []
    for doc in documents:
        # Handle string entries
        if isinstance(doc, str):
            try:
                doc = json.loads(doc)
            except:
                doc = {"title": doc, "url": "", "type": "text"}
        
        if not isinstance(doc, dict):
            continue  # Skip invalid entries
        
        # Normalize structure
        normalized_doc = {
            'title': doc.get('title') or doc.get('name', 'Untitled'),
            'url': doc.get('url', ''),
            'type': doc.get('type', 'unknown')
        }
        
        normalized.append(normalized_doc)
    
    return normalized
```

**Also add error handling in update_session:**
```python
if 'documents' in update_data:
    try:
        normalized = normalize_documents(update_data['documents'])
        updates.append("documents = %s")
        params.append(json.dumps(normalized))
    except Exception as doc_error:
        return jsonify({
            'success': False,
            'error': f'Invalid document format: {str(doc_error)}'
        }), 400
```

---

### 4️⃣ **synergy_search_sessions** - Tool Not Implemented ❌

**Problem:** No backend endpoint exists for searching sessions  
**Status:** Complete feature missing  

**Quick Implementation:**

**Step 1:** Add backend route in `synergy_routes.py`:
```python
@synergy_bp.route('/search', methods=['GET'])
def search_sessions():
    """Search sessions by title, description, tags, or platform"""
    query = request.args.get('query', '').strip()
    platform = request.args.get('platform')
    
    if not query and not platform:
        return jsonify({'success': False, 'error': 'query or platform required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if query:
        search_pattern = f'%{query}%'
        conditions.append("(title LIKE %s OR description LIKE %s OR tags LIKE %s)")
        params.extend([search_pattern, search_pattern, search_pattern])
    
    if platform:
        conditions.append("platforms_involved LIKE %s")
        params.append(f'%{platform}%')
    
    sql = f"""
        SELECT * FROM synergy_sessions.synergy_sessions 
        WHERE {' AND '.join(conditions)}
        ORDER BY last_active DESC
        LIMIT 50
    """
    
    sql, final_params = convert_sql_placeholders(sql, params)
    cursor.execute(sql, final_params)
    rows = cursor.fetchall()
    
    sessions = [dict(row) for row in rows]
    
    return jsonify({
        'success': True,
        'count': len(sessions),
        'sessions': sessions
    })
```

**Step 2:** Add tool implementation in `tools/implementations/synergy.py`:
```python
def synergy_search_sessions(
    query: Optional[str] = None,
    platform: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Search sessions by title, description, tags, or platform
    
    Args:
        query: Search term
        platform: Filter by platform (gmail, sheets, etc.)
        
    Returns:
        Dict with search results
    """
    try:
        params = {}
        if query:
            params["query"] = query
        if platform:
            params["platform"] = platform
        
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
            "sessions": result.get("sessions", [])
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Search failed: {str(e)}")
```

**Step 3:** Add tool schema to `tools/schemas/synergy_tools.json`:
```json
{
    "name": "synergy_search_sessions",
    "description": "Search sessions by title, description, tags, or platform",
    "platform": "synergy",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search term"
            },
            "platform": {
                "type": "string",
                "description": "Filter by platform"
            }
        }
    }
}
```

---

## 🔧 Implementation Priority

**High Priority (30 minutes):**
1. Fix #1 - synergy_get_session (5 min) ✅ Simple placeholder fix
2. Fix #3 - synergy_add_document (10 min) ✅ Enhance normalize_documents
3. Fix #2 - synergy_update_task (15 min) ✅ Add validation

**Medium Priority (20 minutes):**
4. Fix #4 - synergy_search_sessions ✅ Implement new feature

---

## 🧪 Quick Test Script

Create `test_synergy_fixes.py`:
```python
import requests

BASE_URL = 'http://localhost:5001/api/synergy'

def test_all_fixes():
    print("🧪 Testing Synergy Backend Fixes...\n")
    
    # Test 1: Create + Immediate Get
    print("1️⃣ Testing synergy_get_session...")
    create_resp = requests.post(f'{BASE_URL}/create', json={
        'title': 'Test Session',
        'priority': 'high'
    })
    
    if create_resp.status_code == 200:
        session_id = create_resp.json()['session_id']
        
        get_resp = requests.get(f'{BASE_URL}/{session_id}')
        if get_resp.status_code == 200:
            print("   ✅ GET session works!")
        else:
            print(f"   ❌ GET failed: {get_resp.status_code}")
    
    # Test 2: Add Documents
    print("\n2️⃣ Testing synergy_add_document...")
    update_resp = requests.patch(f'{BASE_URL}/{session_id}', json={
        'updates': {
            'documents': [
                {'title': 'Test Doc', 'url': 'https://test.com', 'type': 'google_doc'}
            ]
        }
    })
    
    if update_resp.status_code == 200:
        print("   ✅ Add document works!")
    else:
        print(f"   ❌ Add document failed: {update_resp.status_code}")
    
    # Test 3: Search
    print("\n3️⃣ Testing synergy_search_sessions...")
    search_resp = requests.get(f'{BASE_URL}/search', params={'query': 'test'})
    
    if search_resp.status_code == 200:
        print(f"   ✅ Search works! Found {search_resp.json()['count']} sessions")
    else:
        print(f"   ❌ Search failed: {search_resp.status_code}")

if __name__ == '__main__':
    test_all_fixes()
```

---

## 🚀 Deployment Steps

1. **Apply fixes** to `synergy_routes.py` and `synergy.py`
2. **Restart server:** `BISTART`
3. **Run tests:** `python test_synergy_fixes.py`
4. **Verify** all 4 tools work ✅

---

## 📂 Files to Edit

1. `AI_infrastructure/routes/synergy_routes.py` (fixes 1, 2, 3, 4)
2. `tools/implementations/synergy.py` (fix 4)
3. `tools/schemas/synergy_tools.json` (fix 4)

---

**Status:** 🚧 Ready to implement  
**Time Required:** ~50 minutes total  
**Impact:** Unblocks all Synergy Dashboard functionality

---

**For detailed fixes, see:** `SYNERGY_BACKEND_FIXES_NOV30.md`

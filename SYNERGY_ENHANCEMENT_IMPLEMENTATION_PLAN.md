# Synergy Enhancement Implementation Plan

**Date:** November 8, 2025  
**Status:** 🚧 **READY TO IMPLEMENT**  
**Priority:** P0 - High Impact Feature

---

## 🎯 USER REQUIREMENTS

1. **Enable nested checklists** - Sub-tasks under next steps
2. **Smart tool** - Single tool that creates, adds details, updates, deletes sections
3. **Automatic thread/agent injection** - AI adds its own thread_id and agent_name automatically
4. **Complete CRUD** - Every element in Synergy card manageable via tools

---

## ✅ CURRENT STATE ANALYSIS

### What's Already Working:

1. **✅ UI Nested Checklist Support**
   - Edit modal has sub-checklist UI (lines 22961-22995 in business-ai-platform-v2.html)
   - Sub-checklist styling exists (lines 20842-20934)
   - Save function collects sub-checklists (lines 23077-23092)
   - Data structure supports it: `next_steps` with `sub_checklist` array

2. **✅ Thread/Agent Fields**
   - Database has `thread_ids` and `assigned_agents` columns
   - Backend routes support them (synergy_routes.py)
   - Edit modal has Thread Integration section (lines 7223-7253)
   - Tools accept thread_ids and assigned_agents parameters

3. **✅ Document/Link/Checklist Fixed**
   - Data mismatch bugs fixed (doc.name → doc.title)
   - Filtering corrected (not overly strict)
   - Edit modal, expanded view, popup all show same data

### What's Missing:

1. ❌ **Tool schemas don't support nested checklists**
   - `next_steps` is array of strings, should be array of objects with sub_checklist
   - Tool documentation doesn't explain nested format

2. ❌ **No automatic thread/agent injection**
   - Tools require manual thread_ids parameter
   - No access to current conversation context
   - AI doesn't know its own thread_id or agent_name

3. ❌ **No smart CRUD tool**
   - Separate tools for create/update/delete
   - No "add document without replacing all" pattern
   - No "add checklist item" pattern

---

## 🔧 IMPLEMENTATION PLAN

### Phase 1: Enhanced Tool Schemas (CRITICAL)

**File:** `tools/schemas/synergy_tools.json`

**Changes:**

1. **Update next_steps schema to support nested checklists:**
```json
"next_steps": {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "description": { "type": "string" },
            "due_date": { "type": "string" },
            "completed": { "type": "boolean" },
            "sub_checklist": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "item": { "type": "string" },
                        "completed": { "type": "boolean" }
                    }
                }
            }
        }
    }
}
```

2. **Add _auto_inject_context parameter to ALL Synergy tools:**
```json
"_auto_inject_context": {
    "type": "boolean",
    "description": "AUTOMATIC - Set to true to inject current thread_id and agent_name. Default: true. System will automatically add these to thread_ids and assigned_agents arrays."
}
```

3. **Add new smart CRUD tool:**
```json
{
    "name": "synergy_smart_modify",
    "description": "SMART MODIFIER - Add/remove/update individual elements WITHOUT replacing entire arrays. Use this to:\n- ADD a document without passing all existing docs\n- ADD a checklist item without replacing checklist\n- REMOVE a document by URL\n- UPDATE a next step by index\n- ADD yourself to thread_ids (automatic)\n- ADD your agent name to assigned_agents (automatic)",
    "parameters": {
        "session_id": {"type": "string", "required": true},
        "operation": {
            "type": "string",
            "enum": ["add", "remove", "update", "toggle"],
            "description": "add: Append to array | remove: Delete from array | update: Modify item | toggle: Toggle checklist/step completion"
        },
        "target": {
            "type": "string",
            "enum": ["document", "link", "next_step", "checklist", "tag", "assignee", "thread_id", "agent"],
            "description": "What to modify"
        },
        "data": {
            "type": "object",
            "description": "Item data - format depends on target"
        },
        "index": {
            "type": "integer",
            "description": "For update/remove/toggle operations - which item (0-based)"
        },
        "_auto_inject_context": {
            "type": "boolean",
            "description": "Auto-add current thread_id and agent_name. Default: true"
        }
    }
}
```

---

### Phase 2: Tool Implementation Enhancement

**File:** `tools/implementations/synergy.py`

**Changes:**

1. **Add context injection function:**
```python
def _inject_conversation_context(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inject current thread and agent context from kwargs
    
    Tool executor will inject:
    - _thread_id: Current conversation thread ID
    - _agent_id: Current agent ('1', '2', '3', 'prime', 'secondary')
    - _session_id: Current session ID
    
    Returns: Dict with thread_ids and assigned_agents arrays updated
    """
    result = {}
    
    # Extract injected context
    thread_id = kwargs.get('_thread_id')
    agent_id = kwargs.get('_agent_id', 'unknown')
    session_id = kwargs.get('_session_id')
    
    # Map agent_id to friendly name
    agent_names = {
        '1': 'AI Prime',
        '2': 'AI Secondary',
        '3': 'AI Tertiary',
        'prime': 'AI Prime',
        'secondary': 'AI Secondary',
        'stock_ai': 'Stock AI Agent',
        'data_agent': 'Data Analysis Agent'
    }
    
    agent_name = agent_names.get(agent_id, f'AI Agent {agent_id}')
    
    # Add to result
    if thread_id:
        result['thread_ids'] = [thread_id]
    if agent_name:
        result['assigned_agents'] = [agent_name]
    
    return result
```

2. **Update all tool functions to support auto-injection:**
```python
def synergy_create_session(
    title: str,
    # ... existing parameters ...
    thread_ids: Optional[List[str]] = None,
    assigned_agents: Optional[List[str]] = None,
    _auto_inject_context: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """Create session with optional auto-injection of thread/agent"""
    
    # Auto-inject if enabled
    if _auto_inject_context:
        injected = _inject_conversation_context(kwargs)
        
        # Merge with provided values
        if injected.get('thread_ids'):
            thread_ids = (thread_ids or []) + injected['thread_ids']
        if injected.get('assigned_agents'):
            assigned_agents = (assigned_agents or []) + injected['assigned_agents']
    
    # Continue with normal creation...
```

3. **Implement synergy_smart_modify:**
```python
def synergy_smart_modify(
    session_id: str,
    operation: str,
    target: str,
    data: Optional[Dict[str, Any]] = None,
    index: Optional[int] = None,
    _auto_inject_context: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    SMART CRUD - Modify individual elements without replacing arrays
    
    Operations:
    - add: Append item to array
    - remove: Delete item from array (by index or match)
    - update: Modify item at index
    - toggle: Toggle completion status
    
    Examples:
        # Add document
        synergy_smart_modify(
            session_id="sess_123",
            operation="add",
            target="document",
            data={"title": "New Doc", "url": "https://...", "type": "google_doc"}
        )
        
        # Remove document by index
        synergy_smart_modify(
            session_id="sess_123",
            operation="remove",
            target="document",
            index=2
        )
        
        # Toggle checklist item
        synergy_smart_modify(
            session_id="sess_123",
            operation="toggle",
            target="checklist",
            index=0
        )
        
        # Add nested checklist item to next step
        synergy_smart_modify(
            session_id="sess_123",
            operation="add",
            target="next_step",
            index=1,  # Which next step to add sub-item to
            data={"item": "Sub-task description", "completed": false}
        )
    """
    try:
        # Get current session
        response = requests.get(f"{SYNERGY_API_BASE}/{session_id}", timeout=10)
        response.raise_for_status()
        session = response.json()
        
        # Parse JSON fields
        documents = _parse_json_field(session.get('documents'), [])
        links = _parse_json_field(session.get('links'), [])
        next_steps = _parse_json_field(session.get('next_steps'), [])
        checklist = _parse_json_field(session.get('checklist'), [])
        tags = _parse_json_field(session.get('tags'), [])
        assignees = _parse_json_field(session.get('assignees'), [])
        thread_ids = _parse_json_field(session.get('thread_ids'), [])
        assigned_agents = _parse_json_field(session.get('assigned_agents'), [])
        
        # Auto-inject context if enabled
        if _auto_inject_context and target in ['thread_id', 'agent']:
            injected = _inject_conversation_context(kwargs)
            if target == 'thread_id' and injected.get('thread_ids'):
                data = {'thread_id': injected['thread_ids'][0]}
            elif target == 'agent' and injected.get('assigned_agents'):
                data = {'agent_name': injected['assigned_agents'][0]}
        
        # Build updates based on operation and target
        updates = {}
        
        if operation == "add":
            if target == "document":
                documents.append(data)
                updates['documents'] = documents
            elif target == "link":
                links.append(data)
                updates['links'] = links
            elif target == "next_step":
                # Check if adding sub-item to existing step
                if index is not None and 0 <= index < len(next_steps):
                    step = next_steps[index]
                    if 'sub_checklist' not in step:
                        step['sub_checklist'] = []
                    step['sub_checklist'].append(data)
                else:
                    # Adding new top-level step
                    next_steps.append({
                        'description': data.get('description', ''),
                        'due_date': data.get('due_date'),
                        'completed': data.get('completed', False),
                        'sub_checklist': data.get('sub_checklist', [])
                    })
                updates['next_steps'] = next_steps
            elif target == "checklist":
                checklist.append(data)
                updates['checklist'] = checklist
            elif target == "tag":
                tags.append(data.get('tag', data))
                updates['tags'] = tags
            elif target == "assignee":
                assignees.append(data.get('assignee', data))
                updates['assignees'] = assignees
            elif target == "thread_id":
                thread_id = data.get('thread_id', data)
                if thread_id not in thread_ids:
                    thread_ids.append(thread_id)
                updates['thread_ids'] = thread_ids
            elif target == "agent":
                agent_name = data.get('agent_name', data)
                if agent_name not in assigned_agents:
                    assigned_agents.append(agent_name)
                updates['assigned_agents'] = assigned_agents
        
        elif operation == "remove":
            if index is None:
                raise SynergyError("remove operation requires index parameter")
            
            if target == "document":
                documents.pop(index)
                updates['documents'] = documents
            elif target == "link":
                links.pop(index)
                updates['links'] = links
            elif target == "next_step":
                next_steps.pop(index)
                updates['next_steps'] = next_steps
            elif target == "checklist":
                checklist.pop(index)
                updates['checklist'] = checklist
            elif target == "tag":
                tags.pop(index)
                updates['tags'] = tags
            elif target == "assignee":
                assignees.pop(index)
                updates['assignees'] = assignees
        
        elif operation == "update":
            if index is None:
                raise SynergyError("update operation requires index parameter")
            
            if target == "document":
                documents[index].update(data)
                updates['documents'] = documents
            elif target == "link":
                links[index].update(data)
                updates['links'] = links
            elif target == "next_step":
                next_steps[index].update(data)
                updates['next_steps'] = next_steps
            elif target == "checklist":
                checklist[index].update(data)
                updates['checklist'] = checklist
        
        elif operation == "toggle":
            if index is None:
                raise SynergyError("toggle operation requires index parameter")
            
            if target == "next_step":
                next_steps[index]['completed'] = not next_steps[index].get('completed', False)
                updates['next_steps'] = next_steps
            elif target == "checklist":
                checklist[index]['completed'] = not checklist[index].get('completed', False)
                updates['checklist'] = checklist
        
        # Apply updates
        payload = {"updates": updates}
        response = requests.patch(
            f"{SYNERGY_API_BASE}/{session_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "session_id": session_id,
            "operation": operation,
            "target": target,
            "message": f"✅ {operation.capitalize()}d {target}",
            "session": response.json()
        }
        
    except requests.exceptions.RequestException as e:
        raise SynergyError(f"Failed to modify session: {str(e)}")
```

4. **Add helper function:**
```python
def _parse_json_field(field: Any, default: Any = None) -> Any:
    """Parse JSON field safely"""
    if field is None:
        return default if default is not None else []
    if isinstance(field, str):
        try:
            return json.loads(field)
        except json.JSONDecodeError:
            return default if default is not None else []
    return field
```

---

### Phase 3: Context Injection in Tool Executor

**File:** `AI_infrastructure/core/tool_executor.py`

**Changes:**

1. **Add context extraction in execute_tool:**
```python
def execute_tool(self, tool_name: str, parameters: Dict[str, Any],
                user_id: Optional[int] = None,
                credentials: Optional[Dict[str, Any]] = None,
                stream: bool = False,
                thread_id: Optional[str] = None,  # NEW
                agent_id: Optional[str] = None,   # NEW
                session_id: Optional[str] = None  # NEW
                ) -> Any:
    """Execute tool with credential AND context injection"""
    
    # Existing credential injection
    injected_params = self.inject_credentials(parameters, user_id, credentials)
    
    # NEW: Context injection for Synergy tools
    if tool_name.startswith('synergy_'):
        # Check if auto-injection is enabled (default: true)
        auto_inject = injected_params.get('_auto_inject_context', True)
        
        if auto_inject:
            if thread_id:
                injected_params['_thread_id'] = thread_id
            if agent_id:
                injected_params['_agent_id'] = agent_id
            if session_id:
                injected_params['_session_id'] = session_id
            
            logger.debug(f"Context injected for {tool_name}: thread={thread_id}, agent={agent_id}")
    
    # Continue with execution...
```

---

### Phase 4: Pass Context from Routes

**File:** `AI_infrastructure/routes/agent_routes_v4.py`

**Changes:**

1. **Update run_simple_agent_worker to pass context:**
```python
def run_simple_agent_worker(agent_id, prompt, lock, session_id, queue, conversation, ai_client, user_id):
    """Enhanced worker with context passing"""
    
    try:
        # ... existing code ...
        
        # When executing tools, pass context
        tool_result = executor.execute_tool(
            tool_name=tool_call['name'],
            parameters=tool_call['input'],
            user_id=user_id,
            thread_id=session_id,  # PASS session_id as thread_id
            agent_id=agent_id,     # PASS agent_id
            session_id=session_id  # PASS session_id
        )
        
        # ... rest of code ...
```

---

### Phase 5: Enhanced Expanded Card Display

**File:** `UI/business-ai-platform-v2.html`

**Changes:**

1. **Update renderCardExpanded to show nested checklists:**
```javascript
// Next Steps with sub-checklists
const validSteps = nextSteps.filter(step => 
    step && step.description !== null && step.description !== undefined
);

stepsHTML = `
    <div class="card-section">
        <div class="section-title"><i class="fas fa-tasks"></i> Next Steps ${validSteps.length > 0 ? `(${validSteps.length})` : ''}</div>
        <div class="steps-list">
            ${validSteps.length > 0 ? validSteps.map((step, idx) => `
                <div class="step-item ${step.completed ? 'completed' : ''}">
                    <input type="checkbox" ${step.completed ? 'checked' : ''} 
                           onchange="synergyBoard.toggleStep('${session.session_id}', ${idx})">
                    <span class="step-description">${this.escapeHtml(step.description)}</span>
                    ${step.due_date ? `<span class="step-due">Due: ${new Date(step.due_date).toLocaleDateString()}</span>` : ''}
                    
                    ${step.sub_checklist && step.sub_checklist.length > 0 ? `
                        <div class="sub-checklist-display">
                            ${step.sub_checklist.map((subItem, subIdx) => `
                                <div class="sub-item ${subItem.completed ? 'completed' : ''}">
                                    <i class="fas ${subItem.completed ? 'fa-check-circle' : 'fa-circle'}"></i>
                                    <span>${this.escapeHtml(subItem.item)}</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('') : '<div class="step-item" style="opacity: 0.6; font-style: italic;">No next steps added</div>'}
        </div>
    </div>
`;
```

---

## 📋 TESTING PLAN

### Test 1: Nested Checklist Creation
```python
# Create session with nested checklist
result = synergy_smart_project_tracker(
    title="Test Nested Checklists",
    platforms_involved=["gmail", "sheets"],
    next_steps=[
        {
            "description": "Setup email automation",
            "due_date": "2025-11-15",
            "completed": False,
            "sub_checklist": [
                {"item": "Create template", "completed": False},
                {"item": "Test sending", "completed": False},
                {"item": "Configure triggers", "completed": False}
            ]
        },
        {
            "description": "Create tracking sheet",
            "completed": False,
            "sub_checklist": [
                {"item": "Design columns", "completed": True},
                {"item": "Add formulas", "completed": False}
            ]
        }
    ]
)
```

### Test 2: Auto Thread/Agent Injection
```python
# Create session - should auto-add thread_id and agent_name
result = synergy_create_session(
    title="Test Auto-Injection",
    platforms_involved=["docs"],
    _auto_inject_context=True  # Default
)

# Verify thread_ids and assigned_agents are populated
assert 'thread_ids' in result['session']
assert 'assigned_agents' in result['session']
```

### Test 3: Smart Modify - Add Document
```python
# Add document without replacing all
result = synergy_smart_modify(
    session_id="sess_123",
    operation="add",
    target="document",
    data={
        "title": "New Meeting Notes",
        "url": "https://docs.google.com/document/d/123",
        "type": "google_doc"
    }
)
```

### Test 4: Smart Modify - Add Sub-Checklist Item
```python
# Add sub-item to existing next step
result = synergy_smart_modify(
    session_id="sess_123",
    operation="add",
    target="next_step",
    index=0,  # First next step
    data={"item": "Review with team", "completed": False}
)
```

### Test 5: Smart Modify - Toggle Completion
```python
# Toggle checklist item
result = synergy_smart_modify(
    session_id="sess_123",
    operation="toggle",
    target="checklist",
    index=2
)
```

---

## 🎯 SUCCESS CRITERIA

1. ✅ AI can create sessions with nested sub-checklists
2. ✅ AI automatically adds its thread_id to thread_ids array
3. ✅ AI automatically adds its agent_name to assigned_agents array
4. ✅ AI can add single document without passing all existing docs
5. ✅ AI can add sub-task to existing next step
6. ✅ AI can toggle checklist/step completion
7. ✅ AI can remove items by index
8. ✅ Expanded card view displays nested checklists correctly
9. ✅ Edit modal maintains nested checklist editing
10. ✅ All CRUD operations work via smart tools

---

## 📦 DELIVERABLES

1. **Updated schemas** - `tools/schemas/synergy_tools.json`
2. **Enhanced implementation** - `tools/implementations/synergy.py`
3. **Context injection** - `AI_infrastructure/core/tool_executor.py`
4. **Route updates** - `AI_infrastructure/routes/agent_routes_v4.py`
5. **UI enhancements** - `UI/business-ai-platform-v2.html`
6. **Test suite** - `test_synergy_smart_tools.py`
7. **Documentation** - `SYNERGY_SMART_TOOLS_GUIDE.md`

---

## ⏱️ IMPLEMENTATION TIME

- **Phase 1 (Schemas):** 30 minutes
- **Phase 2 (Tools):** 60 minutes
- **Phase 3 (Executor):** 20 minutes
- **Phase 4 (Routes):** 15 minutes
- **Phase 5 (UI):** 30 minutes
- **Testing:** 45 minutes

**Total:** ~3 hours

---

**Status:** 🚧 READY TO IMPLEMENT  
**Priority:** P0 - High value feature  
**Impact:** Transforms Synergy into intelligent project tracking system with full AI integration

**Next Step:** Begin Phase 1 - Update tool schemas with nested checklist support and auto-injection parameters

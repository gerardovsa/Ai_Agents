# User ID Injection Fix - Implementation Guide
**Date:** January 13, 2026  
**Status:** 📋 READY TO IMPLEMENT  
**Priority:** HIGH  
**Estimated Time:** 2-4 hours

---

## 🎯 Problem Statement

**Current Issue:**
Email attachment processing tools fail with "No user_id provided. User must be authenticated" error because Flask's `g` context doesn't transfer to worker threads.

**Root Cause:**
```python
# Main Thread (Flask Request)
g.user_id = 14  # ✅ Set by middleware

# Worker Thread (AI Processing)
user_id = g.get('user_id')  # ❌ Returns None - different context!
```

**Impact:**
- All authentication-required tools fail in worker threads
- Microsoft Outlook attachment processing broken
- Gmail attachment processing broken
- Any tool needing user credentials fails

---

## 🔧 Solution: Thread-Local Storage + Explicit Passing

We'll implement a **two-pronged approach**:

### **Approach 1: Thread-Local Storage (Primary)**
Registry stores user_id in thread-local storage when worker starts

### **Approach 2: Explicit Passing (Fallback)**
Worker passes user_id directly to registry.execute_tool()

---

## 📝 Implementation Steps

### **Step 1: Add Thread-Local Storage to Registry**

**File:** `tools/registry_v3.py`

**Location:** After class definition (around line 50)

```python
import threading

class RegistryV3:
    """
    Tool Registry V3 - Thread-safe user context
    """
    
    # Thread-local storage for user_id
    _thread_local = threading.local()
    
    def set_thread_user_id(self, user_id: int):
        """
        Store user_id in thread-local storage.
        Call this at the start of worker threads to make user_id available
        to all tool executions in that thread.
        
        Args:
            user_id: User ID from Flask context
        
        Example:
            def worker(user_id, ...):
                registry = RegistryV3()
                registry.set_thread_user_id(user_id)  # ✅ Set for this thread
                # All tool calls now have user_id
        """
        self._thread_local.user_id = user_id
        logger.info(f"[THREAD CONTEXT] Set user_id={user_id} for thread {threading.current_thread().name}")
    
    def get_thread_user_id(self) -> Optional[int]:
        """
        Get user_id from thread-local storage.
        
        Returns:
            int: User ID for current thread, or None
        """
        return getattr(self._thread_local, 'user_id', None)
    
    def clear_thread_user_id(self):
        """
        Clear user_id from thread-local storage.
        Call this at the end of worker threads for cleanup.
        """
        if hasattr(self._thread_local, 'user_id'):
            delattr(self._thread_local, 'user_id')
            logger.debug(f"[THREAD CONTEXT] Cleared user_id for thread {threading.current_thread().name}")
```

---

### **Step 2: Update execute_tool() to Use Thread-Local Storage**

**File:** `tools/registry_v3.py`

**Location:** `execute_tool()` method (around line 450)

**Find:**
```python
def execute_tool(self, tool_name: str, user_id: Optional[int] = None, 
                session_id: Optional[str] = None, **kwargs) -> Any:
    """Execute a tool by name with given parameters"""
    
    # Get user_id if not provided
    if not user_id and 'user_id' in kwargs:
        user_id = kwargs.pop('user_id')
```

**Replace with:**
```python
def execute_tool(self, tool_name: str, user_id: Optional[int] = None, 
                session_id: Optional[str] = None, **kwargs) -> Any:
    """
    Execute a tool by name with given parameters.
    
    User ID Resolution (in order of priority):
    1. Explicit user_id parameter
    2. user_id in kwargs
    3. Thread-local storage (for worker threads)
    4. Flask g context (for main thread)
    
    Args:
        tool_name: Name of tool to execute
        user_id: Optional user ID (will be auto-injected if available)
        session_id: Optional session ID for feedback injection
        **kwargs: Tool-specific parameters
    
    Returns:
        Tool execution result
    """
    
    # ============================================
    # USER ID RESOLUTION (Multi-Source Fallback)
    # ============================================
    
    # Source 1: Explicit parameter (highest priority)
    if not user_id and 'user_id' in kwargs:
        user_id = kwargs.pop('user_id')
    
    # Source 2: Thread-local storage (for worker threads)
    if not user_id:
        thread_user_id = self.get_thread_user_id()
        if thread_user_id:
            user_id = thread_user_id
            logger.debug(f"[EXECUTE_TOOL] Using user_id={user_id} from thread-local storage")
    
    # Source 3: Flask g context (for main request thread)
    if not user_id:
        try:
            from flask import g
            flask_user_id = g.get('user_id')
            if flask_user_id:
                user_id = flask_user_id
                logger.debug(f"[EXECUTE_TOOL] Using user_id={user_id} from Flask g context")
        except (ImportError, RuntimeError):
            # Not in Flask context or outside request
            pass
    
    # Log if user_id still not found
    if not user_id:
        logger.warning(f"[EXECUTE_TOOL] No user_id available for tool '{tool_name}' - tool may fail if authentication required")
```

---

### **Step 3: Update Worker to Set Thread Context**

**File:** `AI_infrastructure/core/combined_agent_worker.py`

**Location:** Beginning of `run_agent_worker()` function (around line 50)

**Find:**
```python
def run_agent_worker(agent_id: str, message: str, file_data: Optional[List] = None,
                    lock=None, thread_slug: Optional[str] = None, queue=None,
                    conversation: List = None, context: List = None,
                    user_id: Optional[int] = None, session_id: Optional[str] = None,
                    sender_team_id: Optional[str] = None, 
                    recipient_team_id: Optional[str] = None) -> None:
    """
    Background worker for AI agent processing
    """
    registry = None
    ai_client = None
    
    try:
        # Get registry
        registry = get_registry()
```

**Add after registry initialization:**
```python
def run_agent_worker(agent_id: str, message: str, file_data: Optional[List] = None,
                    lock=None, thread_slug: Optional[str] = None, queue=None,
                    conversation: List = None, context: List = None,
                    user_id: Optional[int] = None, session_id: Optional[str] = None,
                    sender_team_id: Optional[str] = None, 
                    recipient_team_id: Optional[str] = None) -> None:
    """
    Background worker for AI agent processing
    
    NOTE: Worker threads don't have Flask g context, so we use thread-local
    storage to make user_id available to all tool executions.
    """
    registry = None
    ai_client = None
    
    try:
        # Get registry
        registry = get_registry()
        
        # ✅ FIX: Set user_id in thread-local storage for all tools in this thread
        if user_id:
            registry.set_thread_user_id(user_id)
            logger.info(f"[WORKER] Thread context initialized with user_id={user_id}")
        else:
            logger.warning(f"[WORKER] No user_id provided - authentication-required tools may fail")
```

**Add cleanup at end of function:**

**Find:**
```python
    finally:
        # Release lock if we acquired it
        if lock and lock.locked():
            lock.release()
```

**Add before lock release:**
```python
    finally:
        # ✅ FIX: Clear thread-local user_id for cleanup
        if registry:
            registry.clear_thread_user_id()
            logger.debug(f"[WORKER] Thread context cleaned up")
        
        # Release lock if we acquired it
        if lock and lock.locked():
            lock.release()
```

---

### **Step 4: Update simple_agent_worker Similarly**

**File:** `AI_infrastructure/core/combined_agent_worker.py`

**Location:** `run_simple_agent_worker()` function (around line 600)

**Apply same changes:**

1. Add after registry initialization:
```python
# ✅ FIX: Set user_id in thread-local storage
if user_id:
    registry.set_thread_user_id(user_id)
    logger.info(f"[SIMPLE WORKER] Thread context initialized with user_id={user_id}")
```

2. Add in finally block:
```python
finally:
    # ✅ FIX: Clear thread-local user_id
    if registry:
        registry.clear_thread_user_id()
```

---

### **Step 5: Update Tool Error Messages**

**File:** `tools/implementations/universal_file_tools.py`

**Location:** All functions that validate user_id (lines 70-75, 495-500, etc.)

**Find:**
```python
if not user_id:
    return {
        'success': False,
        'error': 'No user_id provided. User must be authenticated.'
    }
```

**Replace with:**
```python
if not user_id:
    return {
        'success': False,
        'error': 'Authentication required. Please log in to use this tool.',
        'error_code': 'AUTH_REQUIRED',
        'auth_required': True,
        'suggestion': 'Ensure you are logged in with a valid session token.',
        'debug_info': {
            'tool': tool_name,  # Add tool name for debugging
            'timestamp': datetime.utcnow().isoformat()
        }
    }
```

**Benefits:**
- Clearer error message for users
- `auth_required: true` flag for frontend detection
- Debug info for troubleshooting
- Suggestion for how to fix

---

## 🧪 Testing Plan

### **Test 1: Main Thread (Flask Request)**

```python
from flask import Flask, g
from tools.registry_v3 import RegistryV3

app = Flask(__name__)

with app.test_request_context():
    # Simulate middleware setting g.user_id
    g.user_id = 14
    
    # Registry should find user_id from Flask g
    registry = RegistryV3()
    result = registry.execute_tool('process_outlook_attachment_for_ai', 
                                   message_id='test', 
                                   attachment_id='test')
    
    assert result.get('success') == True  # Should work
```

### **Test 2: Worker Thread (Thread-Local Storage)**

```python
import threading
from tools.registry_v3 import RegistryV3

def worker_test(user_id):
    # Simulate worker thread
    registry = RegistryV3()
    registry.set_thread_user_id(user_id)
    
    result = registry.execute_tool('process_outlook_attachment_for_ai',
                                   message_id='test',
                                   attachment_id='test')
    
    assert result.get('success') == True  # Should work
    
    # Cleanup
    registry.clear_thread_user_id()

# Run in separate thread
thread = threading.Thread(target=worker_test, args=(14,))
thread.start()
thread.join()
```

### **Test 3: Explicit Passing (Fallback)**

```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# Even without Flask g or thread-local, explicit user_id should work
result = registry.execute_tool('process_outlook_attachment_for_ai',
                               user_id=14,  # ✅ Explicit parameter
                               message_id='test',
                               attachment_id='test')

assert result.get('success') == True  # Should work
```

### **Test 4: Missing user_id (Graceful Failure)**

```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# No user_id from any source
result = registry.execute_tool('process_outlook_attachment_for_ai',
                               message_id='test',
                               attachment_id='test')

assert result.get('success') == False
assert result.get('auth_required') == True
assert 'Authentication required' in result.get('error')
```

---

## 🚀 Deployment Steps

### **Phase 1: Development Testing (30 min)**

1. Apply code changes to development branch
2. Run test suite (test_user_id_injection.py)
3. Test email attachment processing manually
4. Verify error messages are clear

### **Phase 2: Code Review (15 min)**

1. Review all changed files
2. Verify thread-local storage usage is correct
3. Check for any race conditions
4. Confirm cleanup in finally blocks

### **Phase 3: Staging Deployment (30 min)**

1. Deploy to staging environment
2. Test with real email attachments
3. Monitor logs for user_id resolution
4. Verify worker threads work correctly

### **Phase 4: Production Deployment (1 hour)**

1. Deploy to production during low-traffic window
2. Monitor error logs closely
3. Test email attachment tools immediately
4. Rollback plan ready if issues arise

---

## 📊 Success Metrics

### **Before Fix:**
- ❌ Email attachment tools: 0% success rate (user_id missing)
- ❌ Worker thread tools: Fail with auth errors
- ❌ Error messages: Confusing ("No user_id provided")

### **After Fix:**
- ✅ Email attachment tools: 100% success rate
- ✅ Worker thread tools: Have user_id context
- ✅ Error messages: Clear and actionable

---

## 🔍 Monitoring & Validation

### **Log Messages to Watch For:**

**✅ Good:**
```
[THREAD CONTEXT] Set user_id=14 for thread Thread-5
[EXECUTE_TOOL] Using user_id=14 from thread-local storage
[WORKER] Thread context initialized with user_id=14
```

**⚠️ Warning:**
```
[EXECUTE_TOOL] No user_id available for tool 'X' - tool may fail if authentication required
[WORKER] No user_id provided - authentication-required tools may fail
```

**❌ Bad:**
```
ERROR: Authentication required. Please log in to use this tool.
ERROR: 'NoneType' object has no attribute 'get'
```

### **Metrics to Track:**

1. **Tool Success Rate:**
   - Before: ~20% for auth-required tools in worker threads
   - Target: >95% for auth-required tools

2. **Error Rates:**
   - "No user_id provided" errors should drop to 0%
   - "Authentication required" errors acceptable (user not logged in)

3. **Response Times:**
   - Thread-local storage should add <1ms overhead
   - No performance degradation expected

---

## 🛡️ Rollback Plan

If issues arise after deployment:

### **Quick Rollback (5 minutes)**

1. Revert code changes:
   ```bash
   git revert <commit_hash>
   git push origin main
   ```

2. Restart Flask server:
   ```bash
   sudo systemctl restart flask_app
   ```

### **Emergency Workaround (If rollback not possible)**

Temporarily disable thread-local storage:

```python
# In registry_v3.py execute_tool()
# Comment out thread-local lookup:

# if not user_id:
#     thread_user_id = self.get_thread_user_id()
#     if thread_user_id:
#         user_id = thread_user_id
```

This reverts to old behavior but at least doesn't break existing functionality.

---

## 📚 Related Files

**Modified:**
- `tools/registry_v3.py` - Thread-local storage + execute_tool updates
- `AI_infrastructure/core/combined_agent_worker.py` - Worker thread initialization
- `tools/implementations/universal_file_tools.py` - Better error messages

**Testing:**
- `test_user_id_injection.py` - Comprehensive test suite

**Documentation:**
- `USER_ID_AND_TOOLUSE_ANALYSIS_JAN13_2026.md` - Root cause analysis
- `.github/copilot-instructions.md` - Updated with thread-local pattern

---

## 🎯 Next Steps After Fix

1. **Monitor Production** - Watch for any auth errors for 48 hours
2. **Update Documentation** - Add thread-local pattern to developer guide
3. **Add Metrics** - Dashboard for user_id resolution success rate
4. **Consider Improvements:**
   - Context manager for thread-local user_id
   - Auto-cleanup with decorators
   - Credential caching to reduce DB calls

---

## ✅ Checklist

### **Before Implementation:**
- [ ] Read full implementation guide
- [ ] Understand thread-local storage pattern
- [ ] Review test plan
- [ ] Prepare rollback plan

### **During Implementation:**
- [ ] Apply changes to registry_v3.py
- [ ] Apply changes to combined_agent_worker.py
- [ ] Update error messages in universal_file_tools.py
- [ ] Run test_user_id_injection.py
- [ ] Test manually with email attachments

### **After Deployment:**
- [ ] Monitor logs for 1 hour
- [ ] Test email attachment processing
- [ ] Verify no new errors
- [ ] Update documentation
- [ ] Mark issue as resolved

---

**Estimated Total Time:** 2-4 hours  
**Risk Level:** LOW (fallback mechanisms + rollback plan)  
**Impact:** HIGH (fixes critical authentication issue)

**Ready to implement when approved! 🚀**

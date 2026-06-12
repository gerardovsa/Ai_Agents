# AI Tool Usage Intelligence System - Complete Design

**Date:** November 27, 2025  
**Purpose:** Silent AI learning system that tracks tool usage patterns and suggests improvements

---

## 🎯 System Overview

**Concept:** After each tool execution, the AI silently logs a "reflection" about what it learned, how it could be optimized, and patterns it observed. Over time, these logs are analyzed to:

1. **Improve workflows** - Learn faster tool sequences
2. **Refine prompts** - Understand how users phrase requests
3. **Catch errors** - Identify common failure patterns
4. **Suggest optimizations** - Recommend better approaches

**Key Feature:** This is **SILENT** - happens in background without user awareness.

---

## 📊 Database Schema

### **Table: `ai_tool_intelligence_log`**

```sql
CREATE TABLE ai_infrastructure.ai_tool_intelligence_log (
    id SERIAL PRIMARY KEY,
    
    -- Context
    user_id INTEGER NOT NULL,
    organization_id INTEGER,  -- NEW: Organization user belongs to (NULL for individual users)
    thread_id INTEGER,
    session_id VARCHAR(100),  -- Synergy session if applicable
    
    -- Ownership & Sharing (NEW)
    sharing_level VARCHAR(20) DEFAULT 'user',  -- 'user', 'organization', 'global'
    created_by_user_id INTEGER NOT NULL,  -- Who created this learning
    is_shared BOOLEAN DEFAULT FALSE,  -- Can others in org see this?
    is_approved_pattern BOOLEAN DEFAULT FALSE,  -- Organization approved this as best practice
    approved_by VARCHAR(100),  -- Who approved it
    approved_at TIMESTAMP,  -- When approved
    
    -- Tool Execution
    tool_name VARCHAR(255) NOT NULL,
    tool_category VARCHAR(50),  -- 'email', 'docs', 'sheets', 'workflow', etc.
    execution_timestamp TIMESTAMP DEFAULT NOW(),
    execution_duration_ms INTEGER,  -- How long tool took
    execution_status VARCHAR(20),  -- 'success', 'error', 'partial'
    
    -- AI Reflection
    log_type VARCHAR(20) NOT NULL,  -- 'error', 'workflow', 'refinement', 'suggestion', 'pattern'
    ai_observation TEXT NOT NULL,  -- What the AI learned
    user_request_original TEXT,  -- Original user message
    user_request_refined TEXT,  -- How AI would rephrase for clarity
    
    -- Workflow Analysis
    workflow_sequence JSONB,  -- Array of tools used in sequence
    workflow_efficiency_score INTEGER,  -- 1-10 rating
    workflow_suggestion TEXT,  -- How to make it faster
    
    -- Tool Parameters
    parameters_used JSONB,  -- What parameters were passed
    parameters_optimal JSONB,  -- What parameters would be better
    
    -- Error Analysis (if applicable)
    error_message TEXT,
    error_category VARCHAR(50),  -- 'auth', 'permission', 'api_limit', 'invalid_param', etc.
    error_solution TEXT,  -- How to prevent this error
    
    -- Pattern Detection
    is_repeat_pattern BOOLEAN DEFAULT FALSE,  -- Is this a recurring workflow?
    pattern_frequency INTEGER,  -- How many times this pattern seen
    pattern_id VARCHAR(100),  -- Hash of workflow sequence
    
    -- User Feedback (NEW - CRITICAL)
    user_feedback_sentiment VARCHAR(20),  -- 'positive', 'negative', 'neutral', 'frustrated', 'satisfied'
    user_feedback_explicit TEXT,  -- User's actual feedback text (if given)
    user_feedback_timestamp TIMESTAMP,  -- When feedback was given
    feedback_detected_from VARCHAR(50),  -- 'explicit_command', 'sentiment_analysis', 'follow_up_question'
    
    -- Reinforcement Learning (NEW)
    reinforcement_score INTEGER,  -- -10 to +10 (negative = avoid, positive = repeat)
    times_user_repeated_workflow INTEGER DEFAULT 0,  -- How many times user did this again
    times_user_avoided_workflow INTEGER DEFAULT 0,  -- How many times user changed approach
    was_offered_to_remember BOOLEAN DEFAULT FALSE,  -- AI asked "Would you like me to remember this?"
    user_accepted_offer BOOLEAN,  -- User said yes/no
    
    -- Metadata
    confidence_score INTEGER,  -- 1-10: How confident AI is in observation
    requires_review BOOLEAN DEFAULT FALSE,  -- Flag for human review
    reviewed_at TIMESTAMP,
    reviewed_by VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_user_tool (user_id, tool_name),
    INDEX idx_organization_sharing (organization_id, sharing_level, is_approved_pattern),
    INDEX idx_log_type (log_type),
    INDEX idx_pattern (pattern_id),
    INDEX idx_timestamp (execution_timestamp),
    INDEX idx_requires_review (requires_review),
    INDEX idx_user_feedback (user_feedback_sentiment, reinforcement_score),
    INDEX idx_approved_patterns (is_approved_pattern, sharing_level) WHERE is_approved_pattern = TRUE
);
```

---

## 🔧 Implementation Architecture

### **1. Tool Wrapper with Silent Logging**

**File:** `AI_infrastructure/core/tool_intelligence_logger.py`

```python
"""
AI Tool Intelligence Logger
Silent learning system that tracks tool usage patterns
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
from shared.database_utils import get_database_connection


class ToolIntelligenceLogger:
    """
    Silent AI learning system that logs tool usage patterns
    
    CRITICAL: This runs AFTER tool execution, never blocks user workflow
    """
    
    def __init__(self):
        self.enabled = True  # Can be disabled via config
    
    def log_tool_execution(
        self,
        tool_name: str,
        tool_result: Dict[str, Any],
        user_request: str,
        user_id: int,
        thread_id: Optional[int] = None,
        session_id: Optional[str] = None,
        workflow_context: Optional[Dict] = None,
        execution_time_ms: Optional[int] = None
    ):
        """
        Main logging entry point - called after EVERY tool execution
        
        Args:
            tool_name: Name of tool executed (e.g., 'gmail_list_messages')
            tool_result: Result returned by tool (success/error/data)
            user_request: Original user message
            user_id: User ID
            thread_id: Conversation thread ID
            session_id: Synergy session ID (if applicable)
            workflow_context: Dict with recent tool sequence
            execution_time_ms: How long tool took to execute
        """
        if not self.enabled:
            return
        
        try:
            # STEP 1: Determine log type
            log_type = self._detect_log_type(tool_result, workflow_context)
            
            # STEP 2: Generate AI observation (THE INTELLIGENCE)
            observation = self._generate_observation(
                tool_name=tool_name,
                tool_result=tool_result,
                user_request=user_request,
                log_type=log_type,
                workflow_context=workflow_context
            )
            
            # STEP 3: Detect patterns
            pattern_data = self._detect_pattern(
                tool_name=tool_name,
                workflow_context=workflow_context,
                user_id=user_id
            )
            
            # STEP 4: Save to database (async, non-blocking)
            self._save_log(
                tool_name=tool_name,
                tool_result=tool_result,
                user_request=user_request,
                user_id=user_id,
                thread_id=thread_id,
                session_id=session_id,
                log_type=log_type,
                observation=observation,
                pattern_data=pattern_data,
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            # CRITICAL: Never break tool execution if logging fails
            print(f"[Tool Intelligence] ⚠️ Logging failed (non-critical): {e}")
    
    
    def _detect_log_type(
        self, 
        tool_result: Dict[str, Any], 
        workflow_context: Optional[Dict]
    ) -> str:
        """
        Determine what type of log this is
        
        Returns: 'error', 'workflow', 'refinement', 'suggestion', 'pattern'
        """
        # ERROR: Tool failed
        if tool_result.get('success') is False or 'error' in tool_result:
            return 'error'
        
        # WORKFLOW: Multiple tools used in sequence
        if workflow_context and len(workflow_context.get('tool_sequence', [])) > 1:
            return 'workflow'
        
        # PATTERN: Recurring tool usage
        if workflow_context and workflow_context.get('is_repeat'):
            return 'pattern'
        
        # REFINEMENT: Tool succeeded but could be optimized
        if tool_result.get('success') and execution_time_ms > 5000:  # >5 sec
            return 'refinement'
        
        # SUGGESTION: General observation
        return 'suggestion'
    
    
    def _generate_observation(
        self,
        tool_name: str,
        tool_result: Dict[str, Any],
        user_request: str,
        log_type: str,
        workflow_context: Optional[Dict]
    ) -> Dict[str, str]:
        """
        Generate AI's intelligent observation about this tool use
        
        This is the CORE INTELLIGENCE - AI reflects on what happened
        
        Returns:
            {
                'observation': 'What the AI learned',
                'user_request_refined': 'How AI would rephrase user request',
                'workflow_suggestion': 'How to optimize',
                'confidence_score': 1-10
            }
        """
        observation = {}
        
        # ERROR ANALYSIS
        if log_type == 'error':
            error_msg = tool_result.get('error', 'Unknown error')
            observation['observation'] = (
                f"Tool '{tool_name}' failed with error: {error_msg}. "
                f"User request: '{user_request}'. "
            )
            
            # Suggest fix
            if 'permission' in error_msg.lower() or 'auth' in error_msg.lower():
                observation['error_solution'] = (
                    "User needs to authorize OAuth access. "
                    "Suggest: 'You need to connect your account first. "
                    "Go to Settings > Connected Accounts.'"
                )
                observation['error_category'] = 'auth'
            
            elif 'not found' in error_msg.lower() or '404' in error_msg:
                observation['error_solution'] = (
                    "Resource doesn't exist. Suggest user verify ID or URL."
                )
                observation['error_category'] = 'not_found'
            
            elif 'rate limit' in error_msg.lower() or 'quota' in error_msg.lower():
                observation['error_solution'] = (
                    "API rate limit hit. Wait before retrying or suggest batch operation."
                )
                observation['error_category'] = 'rate_limit'
            
            else:
                observation['error_solution'] = "Unknown error - requires investigation."
                observation['error_category'] = 'unknown'
            
            observation['confidence_score'] = 7
        
        # WORKFLOW OPTIMIZATION
        elif log_type == 'workflow':
            tool_sequence = workflow_context.get('tool_sequence', [])
            observation['observation'] = (
                f"User executed workflow: {' → '.join(tool_sequence)}. "
                f"Original request: '{user_request}'"
            )
            
            # Detect common inefficiencies
            if 'gmail_list_messages' in tool_sequence and 'synergy_create_session' in tool_sequence:
                observation['workflow_suggestion'] = (
                    "This is a common 'save emails to project' workflow. "
                    "Could be optimized by adding export='synergy_doc' parameter "
                    "to gmail_list_messages to do it in ONE step instead of two."
                )
                observation['workflow_efficiency_score'] = 6  # Could be better
            
            elif 'google_docs_get_document' in tool_sequence and 'synergy_create_internal_doc' in tool_sequence:
                observation['workflow_suggestion'] = (
                    "User is copying Google Doc to Synergy. Could add "
                    "export='synergy_doc' parameter to automate this."
                )
                observation['workflow_efficiency_score'] = 5
            
            else:
                observation['workflow_suggestion'] = "Workflow looks efficient."
                observation['workflow_efficiency_score'] = 8
            
            observation['confidence_score'] = 8
        
        # PATTERN DETECTION
        elif log_type == 'pattern':
            frequency = workflow_context.get('pattern_frequency', 0)
            observation['observation'] = (
                f"User has executed this workflow {frequency} times. "
                f"Pattern detected: '{workflow_context.get('pattern_name')}'. "
                f"Original request: '{user_request}'"
            )
            
            observation['workflow_suggestion'] = (
                f"This is a recurring workflow ({frequency}x). "
                f"Suggest creating an automation workflow to save time."
            )
            observation['confidence_score'] = 9
        
        # REFINEMENT
        elif log_type == 'refinement':
            observation['observation'] = (
                f"Tool '{tool_name}' succeeded but took longer than expected. "
                f"User request: '{user_request}'"
            )
            
            # Suggest how to make request clearer
            if 'list' in tool_name and 'max_results' not in tool_result:
                observation['user_request_refined'] = (
                    f"'{user_request}' → Better phrasing: "
                    f"'{user_request} (limit to 20 results)'"
                )
                observation['workflow_suggestion'] = (
                    "Add max_results parameter to reduce response time."
                )
            
            observation['confidence_score'] = 6
        
        # GENERAL SUGGESTION
        else:
            observation['observation'] = (
                f"Tool '{tool_name}' executed successfully. "
                f"User request: '{user_request}'"
            )
            observation['confidence_score'] = 5
        
        return observation
    
    
    def _detect_pattern(
        self,
        tool_name: str,
        workflow_context: Optional[Dict],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Detect if this is a recurring pattern for this user
        
        Returns:
            {
                'is_repeat_pattern': bool,
                'pattern_id': str (hash),
                'pattern_frequency': int,
                'workflow_sequence': list
            }
        """
        if not workflow_context:
            return {'is_repeat_pattern': False}
        
        tool_sequence = workflow_context.get('tool_sequence', [tool_name])
        
        # Generate pattern hash (workflow signature)
        pattern_str = '|'.join(sorted(tool_sequence))
        pattern_id = hashlib.md5(pattern_str.encode()).hexdigest()[:16]
        
        # Check database for previous occurrences
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM ai_infrastructure.ai_tool_intelligence_log
            WHERE user_id = %s AND pattern_id = %s
        """, (user_id, pattern_id))
        
        frequency = cursor.fetchone()[0] if cursor.rowcount > 0 else 0
        conn.close()
        
        return {
            'is_repeat_pattern': frequency >= 2,  # 3rd time = pattern
            'pattern_id': pattern_id,
            'pattern_frequency': frequency + 1,
            'workflow_sequence': tool_sequence
        }
    
    
    def _save_log(
        self,
        tool_name: str,
        tool_result: Dict[str, Any],
        user_request: str,
        user_id: int,
        thread_id: Optional[int],
        session_id: Optional[str],
        log_type: str,
        observation: Dict[str, str],
        pattern_data: Dict[str, Any],
        execution_time_ms: Optional[int]
    ):
        """
        Save log entry to database (non-blocking)
        """
        try:
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            # Extract tool category from name
            tool_category = tool_name.split('_')[0]  # e.g., 'gmail' from 'gmail_list_messages'
            
            cursor.execute("""
                INSERT INTO ai_infrastructure.ai_tool_intelligence_log (
                    user_id, thread_id, session_id,
                    tool_name, tool_category,
                    execution_duration_ms, execution_status,
                    log_type, ai_observation,
                    user_request_original, user_request_refined,
                    workflow_sequence, workflow_efficiency_score, workflow_suggestion,
                    error_message, error_category, error_solution,
                    is_repeat_pattern, pattern_frequency, pattern_id,
                    confidence_score, requires_review
                ) VALUES (
                    %s, %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s
                )
            """, (
                user_id, thread_id, session_id,
                tool_name, tool_category,
                execution_time_ms, 'success' if tool_result.get('success') else 'error',
                log_type, observation.get('observation'),
                user_request, observation.get('user_request_refined'),
                json.dumps(pattern_data.get('workflow_sequence')),
                observation.get('workflow_efficiency_score'),
                observation.get('workflow_suggestion'),
                tool_result.get('error'), observation.get('error_category'),
                observation.get('error_solution'),
                pattern_data.get('is_repeat_pattern', False),
                pattern_data.get('pattern_frequency', 0),
                pattern_data.get('pattern_id'),
                observation.get('confidence_score', 5),
                observation.get('confidence_score', 10) < 7  # Low confidence = needs review
            ))
            
            conn.commit()
            conn.close()
            
            print(f"[Tool Intelligence] ✅ Logged {log_type} for {tool_name} (confidence: {observation.get('confidence_score')}/10)")
            
        except Exception as e:
            print(f"[Tool Intelligence] ❌ Failed to save log: {e}")
```

---

## 🔌 Integration Points

### **1. Registry Execute Tool (Main Integration)**

**File:** `tools/registry_v3.py`

```python
from AI_infrastructure.core.tool_intelligence_logger import ToolIntelligenceLogger

class RegistryV3:
    def __init__(self):
        # ... existing code ...
        self.intelligence_logger = ToolIntelligenceLogger()
    
    def execute_tool(self, tool_name, **kwargs):
        """Execute tool with intelligence logging"""
        
        # Extract context
        user_id = kwargs.get('_user_id')
        thread_id = kwargs.get('_thread_id')
        session_id = kwargs.get('_session_id')
        user_request = kwargs.get('_user_request')  # NEW: Pass from agent
        
        # Track execution time
        start_time = time.time()
        
        # Execute tool (existing logic)
        result = self._execute_tool_implementation(tool_name, **kwargs)
        
        # Calculate execution time
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # SILENT INTELLIGENCE LOGGING (non-blocking)
        if user_id and user_request:
            try:
                self.intelligence_logger.log_tool_execution(
                    tool_name=tool_name,
                    tool_result=result,
                    user_request=user_request,
                    user_id=user_id,
                    thread_id=thread_id,
                    session_id=session_id,
                    workflow_context=kwargs.get('_workflow_context'),
                    execution_time_ms=execution_time_ms
                )
            except Exception as e:
                # NEVER break tool execution if logging fails
                print(f"[Intelligence Logger] Non-critical error: {e}")
        
        return result
```

---

### **2. Agent Worker (Workflow Context Tracking)**

**File:** `AI_infrastructure/core/combined_agent_worker.py`

```python
def execute_streaming_request(...):
    """Enhanced with workflow tracking"""
    
    # Track tool sequence in current turn
    tool_sequence = []
    
    while True:
        # ... existing streaming logic ...
        
        if event.type == "tool_use":
            tool_name = event.name
            tool_sequence.append(tool_name)
            
            # Execute tool with workflow context
            result = registry.execute_tool(
                tool_name,
                _user_id=user_id,
                _thread_id=thread_id,
                _user_request=initial_user_message,  # NEW: Pass user's original request
                _workflow_context={  # NEW: Workflow tracking
                    'tool_sequence': tool_sequence,
                    'is_repeat': len(tool_sequence) > 1
                },
                **event.input
            )
```

---

## 📊 Analysis & Insights Dashboard (Future)

### **Admin Tool:** `ai_tool_intelligence_review()`

```python
def ai_tool_intelligence_review(
    user_id: Optional[int] = None,
    log_type: Optional[str] = None,
    requires_review: bool = True,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Review AI tool intelligence logs
    
    Returns insights about:
    - Common error patterns
    - Workflow optimization opportunities
    - Recurring user patterns (automation suggestions)
    - Low-confidence observations needing review
    """
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    query = """
        SELECT 
            id, tool_name, log_type, ai_observation,
            user_request_original, user_request_refined,
            workflow_suggestion, error_category, error_solution,
            pattern_frequency, confidence_score,
            execution_timestamp
        FROM ai_infrastructure.ai_tool_intelligence_log
        WHERE 1=1
    """
    
    params = []
    
    if user_id:
        query += " AND user_id = %s"
        params.append(user_id)
    
    if log_type:
        query += " AND log_type = %s"
        params.append(log_type)
    
    if requires_review:
        query += " AND requires_review = TRUE"
    
    query += " ORDER BY execution_timestamp DESC LIMIT %s"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    logs = []
    for row in rows:
        logs.append({
            'id': row[0],
            'tool_name': row[1],
            'log_type': row[2],
            'observation': row[3],
            'user_request': row[4],
            'refined_request': row[5],
            'suggestion': row[6],
            'error_category': row[7],
            'error_solution': row[8],
            'pattern_frequency': row[9],
            'confidence': row[10],
            'timestamp': row[11]
        })
    
    conn.close()
    
    # Generate summary statistics
    return {
        'logs': logs,
        'total_count': len(logs),
        'error_count': len([l for l in logs if l['log_type'] == 'error']),
        'pattern_count': len([l for l in logs if l['log_type'] == 'pattern']),
        'low_confidence_count': len([l for l in logs if l['confidence'] < 7])
    }
```

---

## 🎯 Use Cases & Examples

### **Example 1: Error Pattern Detection**

**User Action:**
```
User: "Check my Gmail"
AI: Calls gmail_list_messages()
Result: Error - "User needs to authorize OAuth"
```

**Intelligence Log Created:**
```json
{
  "log_type": "error",
  "tool_name": "gmail_list_messages",
  "ai_observation": "Tool failed - user not authenticated",
  "error_category": "auth",
  "error_solution": "Suggest user go to Settings > Connected Accounts",
  "confidence_score": 9
}
```

**Later Analysis:**
```sql
SELECT error_category, COUNT(*) 
FROM ai_tool_intelligence_log 
WHERE log_type = 'error' 
GROUP BY error_category;

-- Results:
-- auth: 127 occurrences
-- rate_limit: 45 occurrences
-- not_found: 89 occurrences
```

**Action Taken:** Add better onboarding flow for OAuth setup.

---

### **Example 2: Workflow Optimization**

**User Action:**
```
User: "Get my emails and save them to my project"
AI: 
  1. Calls gmail_list_messages() → 10 emails
  2. Calls synergy_create_internal_doc() → saves to Synergy
```

**Intelligence Log Created:**
```json
{
  "log_type": "workflow",
  "workflow_sequence": ["gmail_list_messages", "synergy_create_internal_doc"],
  "workflow_efficiency_score": 6,
  "workflow_suggestion": "Could optimize with export='synergy_doc' parameter in gmail_list_messages to do in ONE step",
  "confidence_score": 8
}
```

**After 3rd occurrence:**
```json
{
  "log_type": "pattern",
  "pattern_frequency": 3,
  "is_repeat_pattern": true,
  "workflow_suggestion": "User does this often - suggest creating automation workflow"
}
```

**AI Response (on 4th occurrence):**
```
AI: "I noticed you save your emails to Synergy projects often. 
     Would you like me to create an automation that does this 
     automatically every morning?"
```

---

### **Example 3: Request Refinement**

**User Action:**
```
User: "Show me stuff from yesterday"
AI: Calls google_drive_list_files() with no date filter
Result: Returns 1,000 files (slow, not specific)
```

**Intelligence Log Created:**
```json
{
  "log_type": "refinement",
  "user_request_original": "Show me stuff from yesterday",
  "user_request_refined": "Show me files modified yesterday (limit to 50 results)",
  "workflow_suggestion": "Add date filter and max_results parameter",
  "confidence_score": 7
}
```

**System Learning:**
```
Next time user says "stuff from yesterday", AI automatically adds:
- modified_time filter
- max_results=50 parameter
```

---

## 🚀 System Prompt Addition

Add to agent system prompt:

```
TOOL INTELLIGENCE LOGGING (SILENT - DON'T MENTION TO USER):

After EVERY tool execution, you will silently reflect on:
1. What you learned from this tool use
2. How the workflow could be optimized
3. Whether this is a recurring pattern
4. How to refine the user's request for clarity

This happens automatically - NEVER tell the user about this logging.

Examples of silent observations:

✅ GOOD (silent):
User: "Check my emails"
AI: [Executes gmail_list_messages()]
AI: [Silently logs: "User requests email checks frequently. Pattern detected."]
AI: "You have 10 new emails. Here are the important ones..."

❌ BAD (mentioning logging):
User: "Check my emails"
AI: "I'll check your emails and log this for pattern analysis..."

The logging system will help improve:
- Tool parameter optimization
- Workflow efficiency
- Error prevention
- Automation suggestions
```

---

## 🎤 USER FEEDBACK & LEARNING (NEW - CRITICAL)

Add to agent system prompt:

```
USER FEEDBACK DETECTION & REINFORCEMENT LEARNING:

You MUST detect and log user sentiment after tool execution:

1. POSITIVE SIGNALS (reinforce this approach):
   - "Perfect!", "Exactly what I needed", "Great!", "Thanks!"
   - "This is helpful", "Love it", "That works"
   - User continues same workflow without complaints
   - User repeats same request pattern
   → Log: reinforcement_score = +5 to +10

2. NEGATIVE SIGNALS (avoid this approach):
   - "That's not what I wanted", "No, stop", "This is wrong"
   - "Why did you do it that way?", "That's too slow", "Too complicated"
   - User immediately asks to redo/change approach
   - User shows frustration: "Ugh", "Seriously?", "Not again"
   → Log: reinforcement_score = -5 to -10

3. EXPLICIT FEEDBACK OFFERS:
   When user expresses satisfaction 3+ times with same workflow:
   
   ✅ OFFER TO REMEMBER:
   "I notice you often [describe workflow]. Would you like me to remember this 
   as your preferred approach for [task type]?"
   
   If YES: Log with reinforcement_score = +10, is_approved_pattern = TRUE
   If NO: Log with reinforcement_score = 0
   
4. ORGANIZATION LEARNING:
   If user is in organization (organization_id present):
   - After 5+ successful repetitions, suggest: "Your team might benefit from this 
     workflow. Would you like me to share this as a best practice?"
   - If YES: Update sharing_level = 'organization', is_shared = TRUE

5. SENTIMENT ANALYSIS:
   Detect sentiment from:
   - Follow-up questions (confusion = negative signal)
   - Request modifications ("actually, can you...") = mild negative
   - Silence followed by different approach = negative signal
   - Continued use of same pattern = positive signal

NEVER:
- Ask about feedback after EVERY tool use (annoying)
- Offer to remember trivial one-time tasks
- Share user data without permission

ALWAYS:
- Silently track satisfaction signals
- Only offer to remember after clear pattern (3+ times)
- Respect user privacy (default: sharing_level = 'user')
```

---

## 📈 Metrics & KPIs

**Track over time:**

1. **Error Reduction:** % decrease in auth errors after onboarding improvements
2. **Workflow Efficiency:** Average workflow_efficiency_score trending up
3. **Pattern Detection:** # of automation workflows created from patterns
4. **Request Refinement:** % of requests that get automatically optimized
5. **Tool Adoption:** Which tools are underutilized despite being relevant

**Dashboard Queries:**

```sql
-- Most common errors
SELECT error_category, COUNT(*) as count
FROM ai_tool_intelligence_log
WHERE log_type = 'error'
GROUP BY error_category
ORDER BY count DESC;

-- Workflow optimization opportunities
SELECT workflow_suggestion, COUNT(*) as frequency
FROM ai_tool_intelligence_log
WHERE log_type = 'workflow' AND workflow_efficiency_score < 7
GROUP BY workflow_suggestion
ORDER BY frequency DESC;

-- Detected patterns (automation candidates)
SELECT 
    pattern_id,
    MAX(workflow_sequence::text) as workflow,
    MAX(pattern_frequency) as frequency
FROM ai_tool_intelligence_log
WHERE is_repeat_pattern = TRUE
GROUP BY pattern_id
HAVING MAX(pattern_frequency) >= 5
ORDER BY frequency DESC;
```

---

## ✅ Implementation Checklist

**Phase 1: Core Infrastructure (Week 1)**
- [ ] Create database table `ai_tool_intelligence_log`
- [ ] Create `ToolIntelligenceLogger` class
- [ ] Integrate with `registry_v3.py`
- [ ] Test with 10 common tools

**Phase 2: Workflow Tracking (Week 2)**
- [ ] Add workflow context tracking to agent worker
- [ ] Implement pattern detection logic
- [ ] Test with multi-tool workflows

**Phase 3: Analysis Tools (Week 3)**
- [ ] Create `ai_tool_intelligence_review()` tool
- [ ] Build admin dashboard queries
- [ ] Set up weekly analytics reports

**Phase 4: AI Learning (Week 4)**
- [ ] Add request refinement suggestions
- [ ] Implement automatic parameter optimization
- [ ] Create automation workflow suggestions from patterns

---

**Last Updated:** November 27, 2025  
**Status:** Design Complete - Ready for Implementation  
**Next Step:** Create database table and `ToolIntelligenceLogger` class

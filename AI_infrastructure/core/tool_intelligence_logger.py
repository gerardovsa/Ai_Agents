"""
AI Tool Intelligence Logger - Silent Learning System

FILE: AI_infrastructure/core/tool_intelligence_logger.py
PURPOSE: Track tool usage patterns and generate AI observations for continuous improvement

CRITICAL: This system is SILENT - it logs reflections after tool execution without
blocking or notifying users. The AI learns from patterns, errors, and workflows over time.

EXPORTS:
- ToolIntelligenceLogger class - Main logging interface

USED BY:
- tools/registry_v3.py - Logs every tool execution
- AI_infrastructure/core/combined_agent_worker.py - Provides workflow context

DEPENDENCIES:
- shared/database_utils.py - PostgreSQL connection pool
- Standard library: hashlib, json, datetime

LAST MODIFIED: 2025-11-27 - Initial implementation of AI intelligence logging system
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from shared.database_utils import get_database_connection


class ToolIntelligenceLogger:
    """
    Silent AI learning system that tracks tool usage patterns
    
    After each tool execution, this logger:
    1. Analyzes what happened (success/error/workflow)
    2. Generates AI observations (what could be improved)
    3. Detects recurring patterns (automation opportunities)
    4. Stores intelligence in database for later analysis
    
    CRITICAL: This runs AFTER tool execution and NEVER blocks user workflow.
    If logging fails, tool execution continues normally.
    """
    
    def __init__(self):
        """Initialize logger with configuration"""
        self.enabled = True  # Can be disabled via environment variable
        self.min_execution_time_slow = 5000  # ms - threshold for "slow" execution
        self.pattern_threshold = 2  # 3rd occurrence triggers pattern detection
    
    
    def log_tool_execution(
        self,
        tool_name: str,
        tool_result: Dict[str, Any],
        user_request: str,
        user_id: int,
        thread_id: Optional[int] = None,
        session_id: Optional[str] = None,
        workflow_context: Optional[Dict] = None,
        execution_time_ms: Optional[int] = None,
        tool_parameters: Optional[Dict] = None
    ):
        """
        Main logging entry point - called after EVERY tool execution
        
        Args:
            tool_name: Name of tool executed (e.g., 'gmail_list_messages')
            tool_result: Result returned by tool (success/error/data)
            user_request: Original user message that triggered this tool
            user_id: User ID executing the tool
            thread_id: Conversation thread ID (optional)
            session_id: Synergy session ID if applicable (optional)
            workflow_context: Dict with recent tool sequence and metadata (optional)
            execution_time_ms: How long tool took to execute in milliseconds (optional)
            tool_parameters: Parameters passed to tool (optional, for optimization analysis)
        
        Returns:
            None (logs silently, never blocks)
        
        Example:
            logger.log_tool_execution(
                tool_name='gmail_list_messages',
                tool_result={'success': True, 'count': 10},
                user_request='Check my emails',
                user_id=14,
                thread_id=42,
                workflow_context={'tool_sequence': ['gmail_list_messages']},
                execution_time_ms=1250
            )
        """
        if not self.enabled:
            return
        
        try:
            # STEP 1: Determine log type based on result and context
            log_type = self._detect_log_type(tool_result, workflow_context, execution_time_ms)
            
            # STEP 2: Generate AI observation (THE CORE INTELLIGENCE)
            observation = self._generate_observation(
                tool_name=tool_name,
                tool_result=tool_result,
                user_request=user_request,
                log_type=log_type,
                workflow_context=workflow_context,
                execution_time_ms=execution_time_ms,
                tool_parameters=tool_parameters
            )
            
            # STEP 3: Detect if this is a recurring pattern
            pattern_data = self._detect_pattern(
                tool_name=tool_name,
                workflow_context=workflow_context,
                user_id=user_id
            )
            
            # STEP 4: Save to database (async/non-blocking)
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
                execution_time_ms=execution_time_ms,
                tool_parameters=tool_parameters
            )
            
        except Exception as e:
            # CRITICAL: Never break tool execution if logging fails
            print(f"[Tool Intelligence] Warning: Logging failed (non-critical): {e}")
    
    
    def _detect_log_type(
        self, 
        tool_result: Dict[str, Any], 
        workflow_context: Optional[Dict],
        execution_time_ms: Optional[int]
    ) -> str:
        """
        Determine what type of intelligence log this should be
        
        Log Types:
        - 'error': Tool execution failed
        - 'workflow': Multiple tools used in sequence (multi-step operation)
        - 'pattern': Recurring workflow detected (3+ times)
        - 'refinement': Tool succeeded but could be optimized
        - 'suggestion': General observation (default)
        
        Args:
            tool_result: Tool execution result dict
            workflow_context: Workflow tracking data
            execution_time_ms: Execution duration
        
        Returns:
            Log type string
        """
        # ERROR: Tool failed completely
        if tool_result.get('success') is False or 'error' in tool_result:
            return 'error'
        
        # PATTERN: Recurring workflow (3+ times seen)
        if workflow_context and workflow_context.get('is_repeat'):
            return 'pattern'
        
        # WORKFLOW: Multiple tools used in sequence
        if workflow_context and len(workflow_context.get('tool_sequence', [])) > 1:
            return 'workflow'
        
        # REFINEMENT: Tool succeeded but took too long or has optimization potential
        if execution_time_ms and execution_time_ms > self.min_execution_time_slow:
            return 'refinement'
        
        # SUGGESTION: General successful execution
        return 'suggestion'
    
    
    def _generate_observation(
        self,
        tool_name: str,
        tool_result: Dict[str, Any],
        user_request: str,
        log_type: str,
        workflow_context: Optional[Dict],
        execution_time_ms: Optional[int],
        tool_parameters: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Generate AI's intelligent observation about this tool use
        
        This is the CORE INTELLIGENCE ENGINE - AI reflects on:
        - What happened during tool execution
        - How it could be optimized
        - Patterns in user behavior
        - Better ways to phrase requests
        
        Args:
            tool_name: Name of executed tool
            tool_result: Tool's return value
            user_request: User's original message
            log_type: Type of log ('error', 'workflow', etc.)
            workflow_context: Workflow tracking data
            execution_time_ms: Execution duration
            tool_parameters: Parameters used
        
        Returns:
            Dict with observation, suggestions, confidence score, etc.
        """
        observation = {
            'observation': '',
            'user_request_refined': None,
            'workflow_suggestion': None,
            'workflow_efficiency_score': None,
            'error_category': None,
            'error_solution': None,
            'confidence_score': 5  # Default: medium confidence
        }
        
        # ============================================================
        # ERROR ANALYSIS
        # ============================================================
        if log_type == 'error':
            error_msg = tool_result.get('error', tool_result.get('message', 'Unknown error'))
            observation['observation'] = (
                f"Tool '{tool_name}' failed. "
                f"Error: {error_msg}. "
                f"User request: '{user_request}'"
            )
            
            # Categorize error and suggest solution
            error_lower = error_msg.lower()
            
            if 'permission' in error_lower or 'auth' in error_lower or 'unauthorized' in error_lower:
                observation['error_category'] = 'auth'
                observation['error_solution'] = (
                    "OAuth authentication required. Suggest: 'You need to connect your account. "
                    "Go to Settings > Connected Accounts to authorize access.'"
                )
                observation['confidence_score'] = 9
            
            elif 'not found' in error_lower or '404' in error_msg:
                observation['error_category'] = 'not_found'
                observation['error_solution'] = (
                    "Resource doesn't exist. Ask user to verify the ID or URL. "
                    "Suggest: 'I couldn't find that resource. Can you verify the ID?'"
                )
                observation['confidence_score'] = 8
            
            elif 'rate limit' in error_lower or 'quota' in error_lower or 'too many requests' in error_lower:
                observation['error_category'] = 'rate_limit'
                observation['error_solution'] = (
                    "API rate limit exceeded. Suggest waiting or using batch operations. "
                    "Suggest: 'API limit reached. I'll try again in a moment.'"
                )
                observation['confidence_score'] = 9
            
            elif 'timeout' in error_lower or 'timed out' in error_lower:
                observation['error_category'] = 'timeout'
                observation['error_solution'] = (
                    "Request took too long. Suggest reducing scope or breaking into smaller requests."
                )
                observation['confidence_score'] = 7
            
            elif 'invalid' in error_lower or 'bad request' in error_lower:
                observation['error_category'] = 'invalid_param'
                observation['error_solution'] = (
                    "Invalid parameter passed. Review tool schema and validate user input."
                )
                observation['confidence_score'] = 6
            
            else:
                observation['error_category'] = 'unknown'
                observation['error_solution'] = (
                    "Unknown error type. Requires investigation. Log error for review."
                )
                observation['confidence_score'] = 4
        
        # ============================================================
        # WORKFLOW OPTIMIZATION ANALYSIS
        # ============================================================
        elif log_type == 'workflow':
            tool_sequence = workflow_context.get('tool_sequence', [])
            observation['observation'] = (
                f"Multi-step workflow executed: {' → '.join(tool_sequence)}. "
                f"User request: '{user_request}'"
            )
            
            # Detect common workflow patterns that could be optimized
            
            # Pattern 1: Get data + Save to Synergy (could use export parameter)
            if any('list' in t or 'get' in t for t in tool_sequence) and any('synergy_create' in t for t in tool_sequence):
                observation['workflow_suggestion'] = (
                    "Common pattern: Fetch data then save to Synergy. "
                    "Could optimize by adding export='synergy_doc' or export='synergy_sheet' "
                    "parameter to the first tool to do in ONE step."
                )
                observation['workflow_efficiency_score'] = 6
                observation['confidence_score'] = 8
            
            # Pattern 2: Get Google Doc + Save to Synergy
            elif 'google_docs_get_document' in tool_sequence and 'synergy_create_internal_doc' in tool_sequence:
                observation['workflow_suggestion'] = (
                    "User copying Google Doc to Synergy. Could add export='synergy_doc' "
                    "to google_docs_get_document to automate."
                )
                observation['workflow_efficiency_score'] = 5
                observation['confidence_score'] = 9
            
            # Pattern 3: Multiple list operations (could batch)
            elif len([t for t in tool_sequence if 'list' in t]) > 2:
                observation['workflow_suggestion'] = (
                    "Multiple list operations. Consider batching or using filters to reduce calls."
                )
                observation['workflow_efficiency_score'] = 6
                observation['confidence_score'] = 6
            
            # Pattern 4: Efficient workflow (no obvious optimizations)
            else:
                observation['workflow_suggestion'] = "Workflow appears efficient - no obvious optimizations."
                observation['workflow_efficiency_score'] = 8
                observation['confidence_score'] = 7
        
        # ============================================================
        # PATTERN DETECTION (Recurring Workflow)
        # ============================================================
        elif log_type == 'pattern':
            frequency = workflow_context.get('pattern_frequency', 0)
            pattern_name = workflow_context.get('pattern_name', 'unnamed workflow')
            
            observation['observation'] = (
                f"RECURRING PATTERN DETECTED: User has executed this workflow {frequency} times. "
                f"Pattern: '{pattern_name}'. "
                f"Original request: '{user_request}'"
            )
            
            observation['workflow_suggestion'] = (
                f"This workflow occurs frequently ({frequency}x). "
                f"Suggest creating an automation workflow to save time. "
                f"Consider: 'Would you like me to automate this task?'"
            )
            observation['confidence_score'] = 9  # High confidence for patterns
        
        # ============================================================
        # REFINEMENT (Successful but could be better)
        # ============================================================
        elif log_type == 'refinement':
            observation['observation'] = (
                f"Tool '{tool_name}' succeeded but performance could improve. "
                f"Execution time: {execution_time_ms}ms (threshold: {self.min_execution_time_slow}ms). "
                f"User request: '{user_request}'"
            )
            
            # Analyze parameters for optimization
            if tool_parameters:
                # Check for missing pagination/limiting
                if 'max_results' not in tool_parameters and 'limit' not in tool_parameters:
                    observation['workflow_suggestion'] = (
                        "Add max_results or limit parameter to reduce response time and data volume."
                    )
                    observation['user_request_refined'] = (
                        f"'{user_request}' → '{user_request} (limit to 20 results)'"
                    )
                    observation['confidence_score'] = 7
                
                # Check for overly broad queries
                elif 'query' not in tool_parameters and 'filter' not in tool_parameters:
                    observation['workflow_suggestion'] = (
                        "Consider adding filters or query parameters to narrow results."
                    )
                    observation['confidence_score'] = 6
            
            else:
                observation['workflow_suggestion'] = "Review tool parameters for optimization opportunities."
                observation['confidence_score'] = 5
        
        # ============================================================
        # GENERAL SUGGESTION (Successful, no issues)
        # ============================================================
        else:
            observation['observation'] = (
                f"Tool '{tool_name}' executed successfully. "
                f"User request: '{user_request}'"
            )
            observation['confidence_score'] = 5  # Medium confidence (not much to learn)
        
        return observation
    
    
    def _detect_pattern(
        self,
        tool_name: str,
        workflow_context: Optional[Dict],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Detect if this is a recurring pattern for this specific user
        
        A pattern is detected when:
        1. Same tool sequence executed 3+ times
        2. Pattern hash matches previous executions
        
        Args:
            tool_name: Name of current tool
            workflow_context: Workflow tracking data
            user_id: User executing the tool
        
        Returns:
            Dict with pattern detection results:
            {
                'is_repeat_pattern': bool,
                'pattern_id': str (hash of workflow),
                'pattern_frequency': int (number of times seen),
                'workflow_sequence': list (tools in sequence),
                'pattern_name': str (human-readable)
            }
        """
        if not workflow_context:
            return {
                'is_repeat_pattern': False,
                'pattern_id': None,
                'pattern_frequency': 0,
                'workflow_sequence': [tool_name]
            }
        
        tool_sequence = workflow_context.get('tool_sequence', [tool_name])
        
        # Generate pattern hash (unique identifier for this workflow)
        # Sort tools to match patterns regardless of conversation order
        pattern_str = '|'.join(sorted(tool_sequence))
        pattern_id = hashlib.md5(pattern_str.encode()).hexdigest()[:16]
        
        # Generate human-readable pattern name
        pattern_name = self._generate_pattern_name(tool_sequence)
        
        try:
            # Check database for previous occurrences of this pattern
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM ai_infrastructure.ai_tool_intelligence_log
                WHERE user_id = %s AND pattern_id = %s
            """, (user_id, pattern_id))
            
            result = cursor.fetchone()
            frequency = result[0] if result else 0
            conn.close()
            
            return {
                'is_repeat_pattern': frequency >= self.pattern_threshold,  # 3rd time = pattern
                'pattern_id': pattern_id,
                'pattern_frequency': frequency + 1,  # +1 for current execution
                'workflow_sequence': tool_sequence,
                'pattern_name': pattern_name
            }
            
        except Exception as e:
            print(f"[Tool Intelligence] Warning: Pattern detection failed: {e}")
            return {
                'is_repeat_pattern': False,
                'pattern_id': pattern_id,
                'pattern_frequency': 1,
                'workflow_sequence': tool_sequence,
                'pattern_name': pattern_name
            }
    
    
    def _generate_pattern_name(self, tool_sequence: List[str]) -> str:
        """
        Generate human-readable name for workflow pattern
        
        Args:
            tool_sequence: List of tool names in workflow
        
        Returns:
            Human-readable pattern name
        
        Examples:
            ['gmail_list_messages', 'synergy_create_internal_doc'] 
            → "Save Emails to Synergy"
            
            ['google_docs_get_document', 'microsoft_word_create_document']
            → "Copy Google Doc to Word"
        """
        if len(tool_sequence) == 1:
            tool = tool_sequence[0]
            # Extract action and platform
            parts = tool.split('_')
            platform = parts[0].replace('google', 'Google').replace('microsoft', 'Microsoft')
            action = ' '.join(parts[1:]).title()
            return f"{platform} {action}"
        
        # Multi-tool pattern - detect common combinations
        seq_str = '|'.join(tool_sequence)
        
        if 'gmail' in seq_str and 'synergy' in seq_str:
            return "Save Emails to Synergy"
        elif 'google_docs' in seq_str and 'synergy' in seq_str:
            return "Copy Google Doc to Synergy"
        elif 'google_sheets' in seq_str and 'synergy' in seq_str:
            return "Import Sheet Data to Synergy"
        elif 'list' in seq_str and 'create' in seq_str:
            return "Fetch and Save Data"
        else:
            return f"{len(tool_sequence)}-Step Workflow"
    
    
    def _save_log(
        self,
        tool_name: str,
        tool_result: Dict[str, Any],
        user_request: str,
        user_id: int,
        thread_id: Optional[int],
        session_id: Optional[str],
        log_type: str,
        observation: Dict[str, Any],
        pattern_data: Dict[str, Any],
        execution_time_ms: Optional[int],
        tool_parameters: Optional[Dict]
    ):
        """
        Save intelligence log entry to database
        
        This is non-blocking and will not raise exceptions to calling code.
        
        Args:
            tool_name: Tool that was executed
            tool_result: Tool's return value
            user_request: User's original message
            user_id: User ID
            thread_id: Thread ID (optional)
            session_id: Synergy session ID (optional)
            log_type: Log type ('error', 'workflow', etc.)
            observation: AI's observation dict
            pattern_data: Pattern detection results
            execution_time_ms: Execution duration
            tool_parameters: Parameters used
        """
        try:
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            # Extract tool category from name (first part before underscore)
            tool_category = tool_name.split('_')[0] if '_' in tool_name else tool_name
            
            # Determine execution status
            execution_status = 'success' if tool_result.get('success', True) else 'error'
            
            # Check if this needs human review (low confidence or critical error)
            requires_review = (
                observation.get('confidence_score', 10) < 7 or 
                (log_type == 'error' and observation.get('error_category') == 'unknown')
            )
            
            cursor.execute("""
                INSERT INTO ai_infrastructure.ai_tool_intelligence_log (
                    user_id, thread_id, session_id,
                    tool_name, tool_category,
                    execution_duration_ms, execution_status,
                    log_type, ai_observation,
                    user_request_original, user_request_refined,
                    workflow_sequence, workflow_efficiency_score, workflow_suggestion,
                    parameters_used,
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
                    %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s
                )
            """, (
                user_id, thread_id, session_id,
                tool_name, tool_category,
                execution_time_ms, execution_status,
                log_type, observation.get('observation'),
                user_request, observation.get('user_request_refined'),
                json.dumps(pattern_data.get('workflow_sequence')),
                observation.get('workflow_efficiency_score'),
                observation.get('workflow_suggestion'),
                json.dumps(tool_parameters) if tool_parameters else None,
                tool_result.get('error'), 
                observation.get('error_category'),
                observation.get('error_solution'),
                pattern_data.get('is_repeat_pattern', False),
                pattern_data.get('pattern_frequency', 0),
                pattern_data.get('pattern_id'),
                observation.get('confidence_score', 5),
                requires_review
            ))
            
            conn.commit()
            conn.close()
            
            # Log success (only visible in server logs, not to user)
            confidence = observation.get('confidence_score', 5)
            print(f"[Tool Intelligence] Logged {log_type} for {tool_name} (confidence: {confidence}/10)")
            
            # If pattern detected, log additional info
            if pattern_data.get('is_repeat_pattern'):
                freq = pattern_data.get('pattern_frequency', 0)
                pattern_name = pattern_data.get('pattern_name', 'unnamed')
                print(f"[Tool Intelligence] PATTERN DETECTED: '{pattern_name}' (frequency: {freq}x)")
            
        except Exception as e:
            # CRITICAL: Never break tool execution if database save fails
            print(f"[Tool Intelligence] Error: Failed to save log (non-critical): {e}")


# ============================================================
# HELPER FUNCTION FOR EASY ACCESS
# ============================================================

# Global singleton instance
_logger_instance = None

def get_tool_intelligence_logger() -> ToolIntelligenceLogger:
    """
    Get singleton instance of ToolIntelligenceLogger
    
    Returns:
        ToolIntelligenceLogger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ToolIntelligenceLogger()
    return _logger_instance

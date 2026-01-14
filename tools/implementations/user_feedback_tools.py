"""
USER FEEDBACK TOOLS - Passive Non-Blocking Feedback
====================================================

FEATURE 2: User Sends Instructions Mid-Execution (NON-BLOCKING)
- User types in textarea and clicks SEND
- Saved to localStorage
- Automatically injected into next tool execution
- AI adjusts behavior without being asked

DIFFERENCE FROM FEATURE 1 (user_interaction_tools):
- Feature 1: AI ASKS user (blocking, modal dialog, required)
- Feature 2: User TELLS AI (non-blocking, small icon, optional)

USE CASE:
User: "Analyze 50 emails"
→ AI calls: show_feedback_area("Processing emails...")
→ Small icon appears (bottom-right)
→ User clicks icon, types: "Focus on legal emails only"
→ User clicks SEND button
→ Saved to localStorage
→ AI continues working...
→ AI calls: gmail_list_messages() (next tool)
→ execute_tool() automatically injects feedback
→ AI sees: "USER SAYS: Focus on legal emails only"
→ AI adjusts behavior
→ Feedback cleared from localStorage

NO FETCH TOOL NEEDED - execute_tool() handles injection automatically!
"""

from typing import Dict, Any


def show_feedback_area(
    message: str = "Working on your request...",
    show_buttons: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Show the user feedback area (non-blocking)
    
    Call this at the start of long operations to show the feedback icon.
    User can optionally provide guidance without blocking AI execution.
    
    Args:
        message: Header text (e.g., "Processing 50 emails...")
        show_buttons: Show Pause/Stop/Explain quick buttons
    
    Returns:
        UI instruction to show feedback icon
    
    Example:
        At start of long task:
        show_feedback_area("Analyzing 50 emails...")
        
        User sees small icon, can click to provide guidance.
        AI continues without waiting.
    """
    return {
        "type": "show_feedback_area",
        "message": message,
        "show_buttons": show_buttons,
        "buttons": ["pause", "stop", "explain"] if show_buttons else []
    }


def hide_feedback_area(**kwargs) -> Dict[str, Any]:
    """
    Hide the user feedback area
    
    Call this when task is complete to hide the feedback icon.
    
    Returns:
        UI instruction to hide feedback icon
    
    Example:
        At end of task:
        hide_feedback_area()
    """
    return {
        "type": "hide_feedback_area",
        "action": "hide"
    }

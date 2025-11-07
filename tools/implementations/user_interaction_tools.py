"""
USER INTERACTION TOOLS v2.0 - UNIFIED Interactive Request System
=================================================================

UNIFIED TOOL: request_user_interaction() replaces 3 separate tools
- Dynamically adapts based on interaction_mode parameter
- Supports auto-submit OR text-insert button behaviors
- Includes control buttons (Pause/Stop/Explain/Continue)
- Clean architecture, single source of truth

NEW FEATURES:
- Text-insert buttons: Click → populates input field (user can edit before sending)
- Control buttons: Pause/Stop/Explain/Continue for long-running operations
- Flexible layouts: buttons_only, buttons_with_input, suggestions_with_input
- Consistent return format across all interaction types

DEPRECATED (but still functional for backward compatibility):
- request_user_confirmation() - Use request_user_interaction(mode="confirmation")
- request_user_choice() - Use request_user_interaction(mode="choice")
- request_user_input() - Use request_user_interaction(mode="input")

Multi-turn conversation preservation maintained across all modes.
"""

from typing import Dict, Any, List, Optional
import json


# ============================================================================
# UNIFIED TOOL - Use This for All Interactions
# ============================================================================

def request_user_interaction(
    message: str,
    interaction_mode: str = "choice",
    options: Optional[List[Dict[str, Any]]] = None,
    allow_custom_input: bool = True,
    button_behavior: str = "submit",
    control_type: Optional[str] = None,
    context: str = "",
    level: str = "medium",
    estimated_tokens: Optional[int] = None,
    estimated_cost_usd: Optional[float] = None,
    is_destructive: bool = False,
    affected_items: Optional[List[str]] = None,
    input_placeholder: str = "Type your response...",
    validation: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    UNIFIED user interaction tool - handles all interaction types in one function
    
    This replaces request_user_confirmation(), request_user_choice(), and 
    request_user_input() with a single, more flexible tool.
    
    Args:
        message: Main message/question to show user (required)
        
        interaction_mode: Type of interaction (default: "choice")
            - "choice": User picks from options
            - "confirmation": Yes/No with cost/risk transparency
            - "input": Free-form text/number input
            - "control": Pause/Stop/Explain/Continue buttons
        
        options: Button options (optional, auto-generated for control mode)
            Format: [
                {
                    "label": "Button Text",
                    "value": "return_value",
                    "description": "What this does",
                    "insert_text": "Text to insert (for text-insert buttons)"
                }
            ]
        
        allow_custom_input: Show text field alongside buttons? (default: True)
        
        button_behavior: How buttons work (default: "submit")
            - "submit": Click → immediately send to AI (instant)
            - "insert": Click → populate input field (user can edit before sending)
        
        control_type: If mode="control", specify type (optional)
            - "pause": Show pause button
            - "stop": Show stop button
            - "explain": Show explain button
            - "continue": Show continue button
            - "all": Show all control buttons (default if control_type not specified)
        
        context: Additional context/explanation (optional)
        level: Risk level - "low", "medium", "high", "critical" (default: "medium")
        estimated_tokens: Token cost estimate (optional)
        estimated_cost_usd: Dollar cost estimate (optional)
        is_destructive: Is this operation destructive/irreversible? (default: False)
        affected_items: List of items affected (optional)
        input_placeholder: Placeholder for text input field
        validation: Input validation rules (for mode="input")
    
    Returns:
        Interaction request dict that frontend detects and renders
    
    Examples:
        # Confirmation with cost transparency
        request_user_interaction(
            message="Should I read the full email with attachments?",
            interaction_mode="confirmation",
            context="Email has 3 PDF attachments (12 MB total)",
            options=[
                {"label": "Read Full Content", "value": "confirm"},
                {"label": "Metadata Only", "value": "metadata"},
                {"label": "Cancel", "value": "cancel"}
            ],
            estimated_tokens=25000,
            estimated_cost_usd=0.075,
            level="high"
        )
        
        # Simple choice
        request_user_interaction(
            message="Which email thread should I analyze?",
            interaction_mode="choice",
            options=[
                {"label": "Contract Review (5 messages)", "value": "thread_1"},
                {"label": "Project Discussion (12 messages)", "value": "thread_2"}
            ]
        )
        
        # Input with suggestions
        request_user_interaction(
            message="Which sender should I search for?",
            interaction_mode="input",
            options=[
                {"label": "john@example.com", "value": "john@example.com"},
                {"label": "jane@example.com", "value": "jane@example.com"}
            ],
            validation={"required": True, "pattern": r"^[^@]+@[^@]+\.[^@]+$"}
        )
        
        # Control buttons (text-insert)
        request_user_interaction(
            message="Long-running operation in progress...",
            interaction_mode="control",
            control_type="all",  # Show all control buttons
            button_behavior="insert"  # Buttons populate input field
        )
        
        # Specific control button
        request_user_interaction(
            message="Analyzing 50 emails...",
            interaction_mode="control",
            control_type="pause",
            button_behavior="insert"
        )
    """
    
    # Auto-generate control buttons if control mode
    if interaction_mode == "control":
        if options is None:
            options = _generate_control_options(control_type or "all")
        button_behavior = "insert"  # Control buttons ALWAYS insert text
    
    # Default options for confirmation mode
    if interaction_mode == "confirmation" and options is None:
        options = [
            {
                "label": "Yes",
                "value": "confirm",
                "description": "Proceed with this operation"
            },
            {
                "label": "No",
                "value": "cancel",
                "description": "Skip this operation"
            }
        ]
    
    # Build unified interaction request
    interaction = {
        "type": "user_interaction_request_v2",  # v2 flag for frontend
        "interaction_mode": interaction_mode,
        "message": message,
        "context": context,
        "options": options or [],
        "allow_custom_input": allow_custom_input,
        "button_behavior": button_behavior,
        "input_placeholder": input_placeholder,
        "level": level,
        "metadata": {
            "estimated_tokens": estimated_tokens,
            "estimated_cost_usd": estimated_cost_usd,
            "is_destructive": is_destructive,
            "affected_items": affected_items or [],
            "validation": validation or {}
        },
        "ui_config": {
            "show_buttons": len(options or []) > 0,
            "show_text_input": allow_custom_input,
            "button_mode": button_behavior,
            "layout": _determine_layout(interaction_mode, options, allow_custom_input)
        }
    }
    
    return interaction


def _generate_control_options(control_type: str) -> List[Dict[str, Any]]:
    """
    Generate button options for control commands
    
    Control buttons use TWO-LAYER system:
    1. insert_text: Visible text in input field (user can edit)
    2. hidden_instructions: Additional context injected to AI (user doesn't see)
    
    When user clicks button and sends, AI receives: insert_text + " " + hidden_instructions + user_edits
    """
    control_configs = {
        "pause": [
            {
                "label": "⏸️ Pause",
                "value": "pause",
                "insert_text": "Pause please",
                "hidden_instructions": "Pause please - Stop current work and call request_user_interaction() with options: [Continue] [Modify Approach] [Explain Progress] [Custom Instructions]. Show what was accomplished so far with resource links.",
                "description": "Pause work and show options"
            }
        ],
        "stop": [
            {
                "label": "⏹️ Stop",
                "value": "stop",
                "insert_text": "Stop please",
                "hidden_instructions": "Stop please - Stop immediately and call request_user_interaction() with options: [Stop and show progress] [Stop and discard work] [Actually continue]. Present all resources created so far with URLs/IDs.",
                "description": "Stop immediately and show progress"
            }
        ],
        "explain": [
            {
                "label": "📊 Explain",
                "value": "explain",
                "insert_text": "Explain your progress",
                "hidden_instructions": "Explain your progress - Provide detailed update including: ✅ Completed actions with links, 🔄 In-progress actions, ⏳ Remaining actions, 🔍 Key discoveries. Then call request_user_interaction() with options: [Explain more about {...}] [Dive deeper into {...}] [Continue current path] [Custom Instructions].",
                "description": "Show detailed progress update with links"
            }
        ],
        "continue": [
            {
                "label": "▶️ Continue",
                "value": "continue",
                "insert_text": "Continue please",
                "hidden_instructions": "Continue please - Resume work from where you paused. Maintain full context and continue with the same plan unless user specified changes.",
                "description": "Resume work from pause"
            }
        ],
        "all": [
            {
                "label": "⏸️ Pause",
                "value": "pause",
                "insert_text": "Pause please",
                "hidden_instructions": "Pause please - Stop current work and call request_user_interaction() with options: [Continue] [Modify Approach] [Explain Progress] [Custom Instructions]. Show what was accomplished so far with resource links.",
                "description": "Pause and show options"
            },
            {
                "label": "⏹️ Stop",
                "value": "stop",
                "insert_text": "Stop please",
                "hidden_instructions": "Stop please - Stop immediately and call request_user_interaction() with options: [Stop and show progress] [Stop and discard work] [Actually continue]. Present all resources created so far with URLs/IDs.",
                "description": "Stop and show progress"
            },
            {
                "label": "📊 Explain",
                "value": "explain",
                "insert_text": "Explain your progress",
                "hidden_instructions": "Explain your progress - Provide detailed update including: ✅ Completed actions with links, 🔄 In-progress actions, ⏳ Remaining actions, 🔍 Key discoveries. Then call request_user_interaction() with options: [Explain more about {...}] [Dive deeper into {...}] [Continue current path] [Custom Instructions].",
                "description": "Detailed update with links"
            },
            {
                "label": "▶️ Continue",
                "value": "continue",
                "insert_text": "Continue please",
                "hidden_instructions": "Continue please - Resume work from where you paused. Maintain full context and continue with the same plan unless user specified changes.",
                "description": "Resume work"
            }
        ]
    }
    
    return control_configs.get(control_type, control_configs["all"])


def _determine_layout(
    interaction_mode: str,
    options: Optional[List[Dict[str, Any]]],
    allow_custom_input: bool
) -> str:
    """Determine UI layout based on interaction configuration"""
    
    has_options = options and len(options) > 0
    
    if interaction_mode == "control":
        return "control_buttons_with_input"
    
    if interaction_mode == "input":
        if has_options:
            return "suggestions_with_input"
        return "input_only"
    
    if interaction_mode == "confirmation":
        if allow_custom_input:
            return "confirmation_with_input"
        return "confirmation_only"
    
    if interaction_mode == "choice":
        if allow_custom_input:
            return "choices_with_input"
        return "choices_only"
    
    # Default
    return "buttons_with_input" if allow_custom_input else "buttons_only"


# ============================================================================
# DEPRECATED TOOLS (Kept for Backward Compatibility)
# ============================================================================
# 
# These tools still work but are deprecated. New code should use
# request_user_interaction() instead.
#
# Migration guide:
#   request_user_confirmation(...) → request_user_interaction(mode="confirmation", ...)
#   request_user_choice(...) → request_user_interaction(mode="choice", ...)
#   request_user_input(...) → request_user_interaction(mode="input", ...)
# ============================================================================


def request_user_confirmation(
    question: str,
    context: str = "",
    options: Optional[List[Dict[str, str]]] = None,
    default_option: Optional[str] = None,
    level: str = "medium",
    estimated_tokens: Optional[int] = None,
    estimated_cost_usd: Optional[float] = None,
    is_destructive: bool = False,
    affected_items: Optional[List[str]] = None,
    allow_custom_input: bool = True,
    input_placeholder: str = "Or type your own response...",
    **kwargs
) -> Dict[str, Any]:
    """
    DEPRECATED: Use request_user_interaction(mode="confirmation") instead
    
    Request user confirmation before proceeding with an operation
    This wrapper maintains backward compatibility.
    """
    return request_user_interaction(
        message=question,
        interaction_mode="confirmation",
        context=context,
        options=options,
        allow_custom_input=allow_custom_input,
        button_behavior="submit",
        level=level,
        estimated_tokens=estimated_tokens,
        estimated_cost_usd=estimated_cost_usd,
        is_destructive=is_destructive,
        affected_items=affected_items,
        input_placeholder=input_placeholder,
        **kwargs
    )


def request_user_choice(
    question: str,
    choices: List[Dict[str, str]],
    context: str = "",
    allow_multiple: bool = False,
    allow_custom: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    DEPRECATED: Use request_user_interaction(mode="choice") instead
    
    Request user to choose from multiple options
    This wrapper maintains backward compatibility.
    """
    return request_user_interaction(
        message=question,
        interaction_mode="choice",
        context=context,
        options=choices,
        allow_custom_input=allow_custom,
        button_behavior="submit",
        **kwargs
    )


def request_user_input(
    prompt: str,
    input_type: str = "text",
    placeholder: Optional[str] = None,
    validation: Optional[Dict[str, Any]] = None,
    suggestions: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    DEPRECATED: Use request_user_interaction(mode="input") instead
    
    Request text/number input from the user
    This wrapper maintains backward compatibility.
    """
    # Convert suggestions to options format
    options = None
    if suggestions:
        options = [{"label": s, "value": s} for s in suggestions]
    
    return request_user_interaction(
        message=prompt,
        interaction_mode="input",
        options=options,
        allow_custom_input=True,
        button_behavior="submit",
        input_placeholder=placeholder or "Type your response...",
        validation=validation,
        **kwargs
    )


# ============================================================================
# NON-BLOCKING TOOLS (Still Active)
# ============================================================================


def inform_user(
    message: str,
    level: str = "info",
    actions: Optional[List[Dict[str, str]]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Inform the user of something important (non-blocking)
    
    Use this to show status updates, warnings, or information without requiring
    user interaction. Unlike confirmation, conversation continues automatically.
    
    Args:
        message: The information to show
        level: Importance level ("info", "success", "warning", "error")
        actions: Optional quick actions the user can take
            Format: [{"label": "View Details", "value": "view_details"}, ...]
    
    Returns:
        An information message
    
    Example:
        inform_user(
            message="Found 5 emails matching your search. Analyzing the most recent one.",
            level="info",
            actions=[
                {"label": "Analyze All", "value": "analyze_all"},
                {"label": "Show List", "value": "show_list"}
            ]
        )
        
        # User sees info banner in chat
        # AI continues automatically (non-blocking)
        # User can click actions if they want to change course
    """
    return {
        "type": "user_information",
        "message": message,
        "level": level,
        "actions": actions or [],
        "blocking": False  # Conversation continues
    }


def suggest_next_actions(
    completed_action: str,
    suggestions: List[Dict[str, str]],
    **kwargs
) -> Dict[str, Any]:
    """
    Suggest follow-up actions after completing a task
    
    Use this at the end of an operation to guide the user on what they can do next.
    
    Args:
        completed_action: What was just completed
        suggestions: List of suggested next actions
            Format: [{"label": "...", "description": "...", "value": "..."}, ...]
    
    Returns:
        A suggestion list
    
    Example:
        suggest_next_actions(
            completed_action="Analyzed contract email",
            suggestions=[
                {
                    "label": "Reply to Email",
                    "description": "Draft a response to the sender",
                    "value": "reply_email"
                },
                {
                    "label": "Schedule Meeting",
                    "description": "Set up a call to discuss the contract",
                    "value": "schedule_meeting"
                },
                {
                    "label": "Create Task",
                    "description": "Add action items to your task list",
                    "value": "create_tasks"
                }
            ]
        )
        
        # User sees: "What would you like to do next?"
        # [Reply to Email] [Schedule Meeting] [Create Task]
    """
    return {
        "type": "next_action_suggestions",
        "completed_action": completed_action,
        "suggestions": suggestions
    }



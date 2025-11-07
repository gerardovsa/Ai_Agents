"""
Google Forms Implementation - Tool Registry Wrappers
====================================================

Wrapper functions for the tool registry to call google_workspace.google_forms functions.
These wrappers handle error formatting, parameter validation, and response formatting
for the AI agent.

Author: Auto-generated
Date: 2025-01-XX
"""

from google_workspace import google_forms
import json
from typing import Dict, Any, List

# ============================================================================
# SMART BUNDLED TOOLS (HIGH PRIORITY)
# ============================================================================

def google_forms_create_complete_form_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_create_complete_form
    
    Creates a complete form with all questions in ONE operation.
    Most efficient method for form creation.
    """
    try:
        # Extract parameters
        title = params.get('title')
        questions = params.get('questions', [])
        description = params.get('description')
        shareable = params.get('shareable', True)
        collect_email = params.get('collect_email', False)
        
        # Validate required parameters
        if not title:
            return {
                "success": False,
                "error": "Parameter 'title' is required"
            }
        
        if not questions or len(questions) == 0:
            return {
                "success": False,
                "error": "Parameter 'questions' must be a non-empty array"
            }
        
        # Call the actual function
        result = google_forms.google_forms_create_complete_form(
            title=title,
            questions=questions,
            description=description,
            shareable=shareable,
            collect_email=collect_email
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Created complete form '{title}' with {result.get('questions_added', 0)} questions"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def google_forms_ai_generate_form_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_ai_generate_form
    
    Generates a form using AI from natural language description.
    """
    try:
        # Extract parameters
        prompt = params.get('prompt')
        form_type = params.get('form_type', 'survey')
        shareable = params.get('shareable', True)
        ai_model = params.get('ai_model', 'gpt-4')
        
        # Validate required parameters
        if not prompt:
            return {
                "success": False,
                "error": "Parameter 'prompt' is required"
            }
        
        # Call the actual function
        result = google_forms.google_forms_ai_generate_form(
            prompt=prompt,
            form_type=form_type,
            shareable=shareable,
            ai_model=ai_model
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"AI-generated form '{result.get('title')}' with {result.get('questions_count', 0)} questions"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "note": "This function requires OPENAI_API_KEY environment variable to be set"
        }


def google_forms_bulk_create_multiple_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_bulk_create_multiple
    
    Creates multiple complete forms at once.
    """
    try:
        # Extract parameters
        forms_configs = params.get('forms_configs', [])
        shareable = params.get('shareable', True)
        
        # Validate required parameters
        if not forms_configs or len(forms_configs) == 0:
            return {
                "success": False,
                "error": "Parameter 'forms_configs' must be a non-empty array"
            }
        
        # Call the actual function
        result = google_forms.google_forms_bulk_create_multiple(
            forms_configs=forms_configs,
            shareable=shareable
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Created {result.get('forms_created', 0)} forms in bulk"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


# ============================================================================
# BASIC FORM OPERATIONS
# ============================================================================

def google_forms_create_form_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_create_form
    
    Creates an empty form. NOTE: Consider using google_forms_create_complete_form instead.
    """
    try:
        title = params.get('title')
        description = params.get('description')
        shareable = params.get('shareable', True)
        
        if not title:
            return {"success": False, "error": "Parameter 'title' is required"}
        
        result = google_forms.google_forms_create_form(
            title=title,
            description=description,
            shareable=shareable
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Created form '{title}'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def google_forms_get_form_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_get_form
    
    Gets form structure and all questions.
    """
    try:
        form_id = params.get('form_id')
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        
        result = google_forms.google_forms_get_form(form_id=form_id)
        
        return {
            "success": True,
            "data": result,
            "message": f"Retrieved form details"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def google_forms_clone_form_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_clone_form
    
    Clones an existing form.
    """
    try:
        form_id = params.get('form_id')
        new_title = params.get('new_title')
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        
        result = google_forms.google_forms_clone_form(
            form_id=form_id,
            new_title=new_title
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Cloned form to '{new_title or result.get('title')}'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def google_forms_delete_form_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_delete_form
    
    Deletes a form permanently.
    """
    try:
        form_id = params.get('form_id')
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        
        result = google_forms.google_forms_delete_form(form_id=form_id)
        
        return {
            "success": True,
            "data": result,
            "message": "Form deleted successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


# ============================================================================
# BULK OPERATIONS
# ============================================================================

def google_forms_batch_add_questions_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_batch_add_questions
    
    Adds multiple questions to a form at once.
    """
    try:
        form_id = params.get('form_id')
        questions_list = params.get('questions_list', [])
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        
        if not questions_list or len(questions_list) == 0:
            return {"success": False, "error": "Parameter 'questions_list' must be a non-empty array"}
        
        result = google_forms.google_forms_batch_add_questions(
            form_id=form_id,
            questions_list=questions_list
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Added {len(questions_list)} questions to form"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


# ============================================================================
# INDIVIDUAL QUESTION OPERATIONS
# ============================================================================

def google_forms_add_text_question_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_add_text_question
    
    Adds a text question. NOTE: Consider using batch_add_questions for multiple questions.
    """
    try:
        form_id = params.get('form_id')
        text = params.get('text')
        paragraph = params.get('paragraph', False)
        required = params.get('required', False)
        index = params.get('index', 0)
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        if not text:
            return {"success": False, "error": "Parameter 'text' is required"}
        
        result = google_forms.google_forms_add_text_question(
            form_id=form_id,
            text=text,
            paragraph=paragraph,
            required=required,
            index=index
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Added text question: '{text}'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def google_forms_add_multiple_choice_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_add_multiple_choice
    
    Adds a multiple choice question.
    """
    try:
        form_id = params.get('form_id')
        text = params.get('text')
        options = params.get('options', [])
        required = params.get('required', False)
        index = params.get('index', 0)
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        if not text:
            return {"success": False, "error": "Parameter 'text' is required"}
        if not options or len(options) == 0:
            return {"success": False, "error": "Parameter 'options' must be a non-empty array"}
        
        result = google_forms.google_forms_add_multiple_choice(
            form_id=form_id,
            text=text,
            options=options,
            required=required,
            index=index
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Added multiple choice question: '{text}'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def google_forms_add_checkbox_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_add_checkbox
    
    Adds a checkbox question (multiple selection).
    """
    try:
        form_id = params.get('form_id')
        text = params.get('text')
        options = params.get('options', [])
        required = params.get('required', False)
        index = params.get('index', 0)
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        if not text:
            return {"success": False, "error": "Parameter 'text' is required"}
        if not options or len(options) == 0:
            return {"success": False, "error": "Parameter 'options' must be a non-empty array"}
        
        result = google_forms.google_forms_add_checkbox(
            form_id=form_id,
            text=text,
            options=options,
            required=required,
            index=index
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Added checkbox question: '{text}'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def google_forms_add_linear_scale_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_add_linear_scale
    
    Adds a linear scale rating question.
    """
    try:
        form_id = params.get('form_id')
        text = params.get('text')
        low_label = params.get('low_label')
        high_label = params.get('high_label')
        low_value = params.get('low_value', 1)
        high_value = params.get('high_value', 5)
        required = params.get('required', False)
        index = params.get('index', 0)
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        if not text:
            return {"success": False, "error": "Parameter 'text' is required"}
        if not low_label:
            return {"success": False, "error": "Parameter 'low_label' is required"}
        if not high_label:
            return {"success": False, "error": "Parameter 'high_label' is required"}
        
        result = google_forms.google_forms_add_linear_scale(
            form_id=form_id,
            text=text,
            low_label=low_label,
            high_label=high_label,
            low_value=low_value,
            high_value=high_value,
            required=required,
            index=index
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Added linear scale question: '{text}'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def google_forms_update_info_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_update_info
    
    Updates form title and description.
    """
    try:
        form_id = params.get('form_id')
        title = params.get('title')
        description = params.get('description')
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        
        result = google_forms.google_forms_update_info(
            form_id=form_id,
            title=title,
            description=description
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Form info updated"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


# ============================================================================
# RESPONSE OPERATIONS
# ============================================================================

def google_forms_get_responses_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_get_responses
    
    Gets all responses from a form.
    """
    try:
        form_id = params.get('form_id')
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        
        result = google_forms.google_forms_get_responses(form_id=form_id)
        
        return {
            "success": True,
            "data": result,
            "message": f"Retrieved {result.get('response_count', 0)} responses"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def google_forms_export_responses_csv_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_export_responses_csv
    
    Exports form responses as CSV.
    """
    try:
        form_id = params.get('form_id')
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        
        result = google_forms.google_forms_export_responses_csv(form_id=form_id)
        
        return {
            "success": True,
            "data": result,
            "message": f"Exported {result.get('response_count', 0)} responses to CSV"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def google_forms_ai_analyze_responses_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_ai_analyze_responses
    
    Analyzes form responses using AI.
    """
    try:
        form_id = params.get('form_id')
        analysis_type = params.get('analysis_type', 'summary')
        ai_model = params.get('ai_model', 'gpt-4')
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        
        result = google_forms.google_forms_ai_analyze_responses(
            form_id=form_id,
            analysis_type=analysis_type,
            ai_model=ai_model
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"AI analysis complete: {analysis_type}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "note": "This function requires OPENAI_API_KEY environment variable to be set"
        }


def google_forms_get_summary_statistics_impl(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for google_forms.google_forms_get_summary_statistics
    
    Gets response statistics and counts.
    """
    try:
        form_id = params.get('form_id')
        
        if not form_id:
            return {"success": False, "error": "Parameter 'form_id' is required"}
        
        result = google_forms.google_forms_get_summary_statistics(form_id=form_id)
        
        return {
            "success": True,
            "data": result,
            "message": "Retrieved summary statistics"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


# ============================================================================
# TOOL REGISTRY MAPPING
# ============================================================================

GOOGLE_FORMS_TOOL_IMPLEMENTATIONS = {
    # Smart bundled tools
    'google_forms_create_complete_form': google_forms_create_complete_form_impl,
    'google_forms_ai_generate_form': google_forms_ai_generate_form_impl,
    'google_forms_bulk_create_multiple': google_forms_bulk_create_multiple_impl,
    
    # Basic operations
    'google_forms_create_form': google_forms_create_form_impl,
    'google_forms_get_form': google_forms_get_form_impl,
    'google_forms_clone_form': google_forms_clone_form_impl,
    'google_forms_delete_form': google_forms_delete_form_impl,
    
    # Bulk operations
    'google_forms_batch_add_questions': google_forms_batch_add_questions_impl,
    
    # Individual question operations
    'google_forms_add_text_question': google_forms_add_text_question_impl,
    'google_forms_add_multiple_choice': google_forms_add_multiple_choice_impl,
    'google_forms_add_checkbox': google_forms_add_checkbox_impl,
    'google_forms_add_linear_scale': google_forms_add_linear_scale_impl,
    'google_forms_update_info': google_forms_update_info_impl,
    
    # Response operations
    'google_forms_get_responses': google_forms_get_responses_impl,
    'google_forms_export_responses_csv': google_forms_export_responses_csv_impl,
    'google_forms_ai_analyze_responses': google_forms_ai_analyze_responses_impl,
    'google_forms_get_summary_statistics': google_forms_get_summary_statistics_impl,
}


def get_google_forms_implementation(tool_name: str):
    """
    Get the implementation function for a given tool name.
    
    Args:
        tool_name: Name of the tool (e.g., 'google_forms_create_complete_form')
    
    Returns:
        Implementation function or None if not found
    """
    return GOOGLE_FORMS_TOOL_IMPLEMENTATIONS.get(tool_name)

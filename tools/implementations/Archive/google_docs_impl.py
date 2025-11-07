"""
Google Docs Tool Implementations
=================================

Wrapper functions for Google Docs SMART bundled tools and basic operations.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from google_workspace import google_docs


# ==================== GOOGLE DOCS SMART BUNDLED TOOLS ====================

def google_docs_ai_smart_generate_document_impl(prompt, tone="professional",
                                                share_with=None, folder_id=None,
                                                include_toc=False):
    """
    🤖 SMART TOOL: AI-powered document generation.
    
    Wrapper for google_docs.google_docs_ai_smart_generate_document()
    """
    try:
        # Validate parameters
        if not prompt or not isinstance(prompt, str):
            return {"success": False, "error": "prompt must be a non-empty string"}
        
        if tone not in ["professional", "casual", "formal", "technical"]:
            return {"success": False, "error": "tone must be: professional, casual, formal, or technical"}
        
        # Call Google Docs function
        result = google_docs.google_docs_ai_smart_generate_document(
            prompt=prompt,
            tone=tone,
            share_with=share_with,
            folder_id=folder_id,
            include_toc=include_toc
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def google_docs_smart_bulk_create_multiple_impl(documents, share_with=None, folder_id=None):
    """
    📚 SMART TOOL: Bulk create multiple Google Docs.
    
    Wrapper for google_docs.google_docs_smart_bulk_create_multiple()
    """
    try:
        # Validate parameters
        if not documents or not isinstance(documents, list):
            return {"success": False, "error": "documents must be a list"}
        
        if len(documents) == 0:
            return {"success": False, "error": "documents list cannot be empty"}
        
        # Validate each document config
        for i, doc in enumerate(documents):
            if not isinstance(doc, dict):
                return {"success": False, "error": f"Document {i+1} must be an object"}
            
            if 'title' not in doc:
                return {"success": False, "error": f"Document {i+1} must have 'title' field"}
            
            if 'markdown_content' not in doc and 'prompt' not in doc:
                return {"success": False, "error": f"Document {i+1} must have either 'markdown_content' or 'prompt' field"}
        
        # Call Google Docs function
        result = google_docs.google_docs_smart_bulk_create_multiple(
            documents=documents,
            share_with=share_with,
            folder_id=folder_id
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ==================== BASIC GOOGLE DOCS TOOLS ====================

def google_docs_smart_create_from_markdown_impl(title, markdown_content, share_with=None, folder_id=None):
    """Create a Google Doc from markdown"""
    try:
        result = google_docs.google_docs_smart_create_from_markdown(title, markdown_content, share_with, folder_id)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def google_docs_smart_update_impl(document_id, markdown_content, insertion_position="end"):
    """Smart update existing Google Doc"""
    try:
        result = google_docs.google_docs_smart_update(document_id, markdown_content, insertion_position)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def google_docs_create_professional_report_with_charts_impl(title, sections_with_data, 
                                                            share_with=None, folder_id=None):
    """Create professional report with charts"""
    try:
        result = google_docs.google_docs_create_professional_report_with_charts(
            title, sections_with_data, share_with, folder_id
        )
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def google_docs_export_pdf_impl(document_id, output_path=None):
    """Export document as PDF"""
    try:
        result = google_docs.google_docs_export_pdf(document_id, output_path)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def google_docs_export_markdown_impl(document_id, output_path=None):
    """Export document as Markdown"""
    try:
        result = google_docs.google_docs_export_markdown(document_id, output_path)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def google_docs_insert_chart_impl(document_id, chart_data, chart_type="column",
                                   chart_options=None, insertion_index=None):
    """Insert chart into document"""
    try:
        result = google_docs.google_docs_insert_chart(
            document_id, chart_data, chart_type, chart_options, insertion_index
        )
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}

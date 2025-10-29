"""
Response Helpers
JSON response formatting for Flask endpoints
"""

from flask import jsonify


def success_response(data=None, message=None, status_code=200):
    """
    Build successful JSON response
    
    Args:
        data: Response data (dict, list, or primitive)
        message: Optional success message
        status_code: HTTP status code (default 200)
    
    Returns:
        Flask JSON response with status code
    """
    response = {
        'success': True
    }
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code


def error_response(error_message, status_code=400, details=None):
    """
    Build error JSON response
    
    Args:
        error_message: Error message string
        status_code: HTTP status code (default 400)
        details: Optional error details (dict)
    
    Returns:
        Flask JSON response with status code
    """
    response = {
        'success': False,
        'error': error_message
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code


def paginated_response(items, page=1, per_page=50, total_items=None):
    """
    Build paginated JSON response
    
    Args:
        items: List of items for current page
        page: Current page number (1-indexed)
        per_page: Items per page
        total_items: Total item count (will calculate if None)
    
    Returns:
        Flask JSON response with pagination metadata
    """
    if total_items is None:
        total_items = len(items)
    
    total_pages = (total_items + per_page - 1) // per_page
    
    response = {
        'success': True,
        'data': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return jsonify(response), 200


def stream_sse_event(event_type, data=None, event_id=None):
    """
    Format SSE event for streaming
    
    Args:
        event_type: Event type (thinking, response, complete, error)
        data: Event data (will be JSON stringified)
        event_id: Optional event ID
    
    Returns:
        SSE-formatted string
    """
    import json
    
    lines = []
    
    if event_id:
        lines.append(f"id: {event_id}")
    
    lines.append(f"event: {event_type}")
    
    if data is not None:
        json_data = json.dumps(data) if not isinstance(data, str) else data
        lines.append(f"data: {json_data}")
    
    lines.append("")  # Empty line to end event
    
    return "\n".join(lines) + "\n"


def list_response(items, total_count=None, message=None):
    """
    Build list response with count
    
    Args:
        items: List of items
        total_count: Total count (will use len(items) if None)
        message: Optional message
    
    Returns:
        Flask JSON response
    """
    if total_count is None:
        total_count = len(items)
    
    response = {
        'success': True,
        'data': items,
        'count': total_count
    }
    
    if message:
        response['message'] = message
    
    return jsonify(response), 200


def created_response(data=None, message="Resource created successfully", resource_id=None):
    """
    Build response for created resource
    
    Args:
        data: Created resource data
        message: Success message
        resource_id: ID of created resource
    
    Returns:
        Flask JSON response with 201 status
    """
    response = {
        'success': True,
        'message': message
    }
    
    if resource_id:
        response['id'] = resource_id
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), 201


def updated_response(data=None, message="Resource updated successfully", updated_count=None):
    """
    Build response for updated resource
    
    Args:
        data: Updated resource data
        message: Success message
        updated_count: Number of records updated
    
    Returns:
        Flask JSON response
    """
    response = {
        'success': True,
        'message': message
    }
    
    if updated_count is not None:
        response['updated_count'] = updated_count
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), 200


def deleted_response(message="Resource deleted successfully", deleted_count=None):
    """
    Build response for deleted resource
    
    Args:
        message: Success message
        deleted_count: Number of records deleted
    
    Returns:
        Flask JSON response
    """
    response = {
        'success': True,
        'message': message
    }
    
    if deleted_count is not None:
        response['deleted_count'] = deleted_count
    
    return jsonify(response), 200


def no_content_response():
    """
    Build 204 No Content response
    
    Returns:
        Empty response with 204 status
    """
    return '', 204


def validation_error_response(errors):
    """
    Build validation error response
    
    Args:
        errors: Validation errors (dict of field: error message)
    
    Returns:
        Flask JSON response with 422 status
    """
    return error_response(
        error_message="Validation failed",
        status_code=422,
        details={'validation_errors': errors}
    )

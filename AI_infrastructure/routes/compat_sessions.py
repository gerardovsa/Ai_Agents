"""
Compatibility layer: legacy /api/sessions/* endpoints
Maps legacy endpoints to the new `/api/kanban` blueprint handlers.
This keeps the UI working without changing browser code.
"""
from flask import Blueprint, request, jsonify, current_app
import requests
import os

compat_bp = Blueprint('compat_sessions', __name__, url_prefix='/api/sessions')

# We'll forward internally to the same Flask app by calling the kanban blueprint
# using Werkzeug test client available via current_app.test_client(). This avoids
# external HTTP calls and preserves request context.

@compat_bp.route('/list', methods=['GET'])
def list_sessions():
    # Forward to /api/kanban/sessions
    with current_app.test_request_context('/api/kanban/sessions', method='GET', query_string=request.query_string):
        resp = current_app.full_dispatch_request()
        return (resp.get_data(), resp.status_code, resp.headers.items())

@compat_bp.route('/create', methods=['POST'])
def create_session():
    with current_app.test_request_context('/api/kanban/sessions', method='POST', data=request.get_data(), headers=request.headers):
        resp = current_app.full_dispatch_request()
        return (resp.get_data(), resp.status_code, resp.headers.items())

@compat_bp.route('/<session_id>', methods=['GET', 'PATCH', 'DELETE'])
def session_proxy(session_id):
    target = f'/api/kanban/sessions/{session_id}'
    method = request.method
    with current_app.test_request_context(target, method=method, data=request.get_data(), headers=request.headers):
        resp = current_app.full_dispatch_request()
        return (resp.get_data(), resp.status_code, resp.headers.items())

@compat_bp.route('/<session_id>/column', methods=['PATCH'])
def session_column(session_id):
    target = f'/api/kanban/sessions/{session_id}'
    with current_app.test_request_context(target, method='PATCH', data=request.get_data(), headers=request.headers):
        resp = current_app.full_dispatch_request()
        return (resp.get_data(), resp.status_code, resp.headers.items())

# Additional legacy endpoints can be added here as thin proxies

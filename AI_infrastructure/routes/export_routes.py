"""
Export Routes - Task 13 (FINAL)
================================
Data export endpoints for conversations, queries, and analytics.

Endpoints:
1. POST /api/export/session - Export conversation to JSON/CSV
2. POST /api/export/query - Export query results to CSV
3. GET /api/export/queries/list - List saved exports

Database: SQLite (stock_data.db) + Chat Manager
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import json
import csv
import io
import os

# Import NEW infrastructure
from utils.database_helpers import execute_sqlite_query
from utils.response_helpers import (
    success_response,
    error_response,
    list_response
)

# Create blueprint
export_bp = Blueprint('export', __name__, url_prefix='/api/export')


@export_bp.route('/session', methods=['POST'])
def export_session():
    """
    POST /api/export/session
    
    Export conversation session to JSON or CSV.
    
    Request Body:
    {
        "session_id": "stock_ai_123456",
        "format": "json",              // "json" or "csv"
        "include_metadata": true
    }
    
    Response:
    {
        "success": true,
        "data": {
            "session_id": "stock_ai_123456",
            "message_count": 15,
            "export_data": "...",
            "format": "json"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400)
        
        session_id = data.get('session_id')
        format_type = data.get('format', 'json')
        include_metadata = data.get('include_metadata', True)
        
        if not session_id:
            return error_response("Missing session_id", 400)
        
        if format_type not in ['json', 'csv']:
            return error_response("Invalid format. Use 'json' or 'csv'", 400)
        
        # TODO: Import ChatHistoryManager and retrieve conversation
        # from core.chat_history_manager import ChatHistoryManager
        # chat_manager = ChatHistoryManager()
        # messages = chat_manager.get_conversation(session_id)
        
        # Mock conversation data for now
        messages = [
            {
                "role": "user",
                "content": "Show me stock levels",
                "timestamp": "2025-10-23T10:30:00",
                "token_count": 5
            },
            {
                "role": "assistant",
                "content": "Here are the current stock levels...",
                "timestamp": "2025-10-23T10:30:15",
                "token_count": 150
            }
        ]
        
        if format_type == 'json':
            # Export as JSON
            export_data = {
                "session_id": session_id,
                "exported_at": datetime.utcnow().isoformat(),
                "message_count": len(messages),
                "messages": messages
            }
            
            if not include_metadata:
                # Remove metadata fields
                for msg in export_data['messages']:
                    msg.pop('token_count', None)
                    msg.pop('timestamp', None)
            
            export_string = json.dumps(export_data, indent=2)
            
            return success_response({
                "session_id": session_id,
                "message_count": len(messages),
                "export_data": export_string,
                "format": "json",
                "size_bytes": len(export_string)
            }, f"Exported {len(messages)} messages to JSON")
        
        else:
            # Export as CSV
            output = io.StringIO()
            
            if messages:
                fieldnames = ['role', 'content', 'timestamp', 'token_count']
                if not include_metadata:
                    fieldnames = ['role', 'content']
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for msg in messages:
                    row = {k: msg.get(k, '') for k in fieldnames}
                    writer.writerow(row)
            
            csv_data = output.getvalue()
            output.close()
            
            return success_response({
                "session_id": session_id,
                "message_count": len(messages),
                "export_data": csv_data,
                "format": "csv",
                "size_bytes": len(csv_data)
            }, f"Exported {len(messages)} messages to CSV")
        
    except Exception as e:
        return error_response(f"Failed to export session: {str(e)}", 500)


@export_bp.route('/query', methods=['POST'])
def export_query():
    """
    POST /api/export/query
    
    Export SQL query results to CSV.
    
    Request Body:
    {
        "query": "SELECT * FROM unified_stocks LIMIT 100",
        "filename": "stock_export.csv",    // Optional
        "include_headers": true
    }
    
    Response:
    {
        "success": true,
        "data": {
            "csv_data": "...",
            "row_count": 100,
            "filename": "stock_export.csv"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400)
        
        query = data.get('query')
        filename = data.get('filename', f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv")
        include_headers = data.get('include_headers', True)
        
        if not query:
            return error_response("Missing query", 400)
        
        # Validate query is SELECT only
        query_upper = query.strip().upper()
        if not query_upper.startswith('SELECT'):
            return error_response("Only SELECT queries are allowed for export", 403)
        
        # Check for write operations
        write_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE']
        if any(keyword in query_upper for keyword in write_keywords):
            return error_response("Write operations not allowed in export queries", 403)
        
        # Stock management is disabled in AI_agents
        return error_response("Stock database export is not available in this deployment", 503)
        
        # Execute query (disabled)
        # results = execute_sqlite_query(db_path, query, [])
        
        if not results:
            return success_response({
                "csv_data": "",
                "row_count": 0,
                "filename": filename
            }, "Query returned no results")
        
        # Generate CSV
        output = io.StringIO()
        
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        
        if include_headers:
            writer.writeheader()
        
        writer.writerows(results)
        
        csv_data = output.getvalue()
        output.close()
        
        return success_response({
            "csv_data": csv_data,
            "row_count": len(results),
            "filename": filename,
            "size_bytes": len(csv_data)
        }, f"Exported {len(results)} rows to CSV")
        
    except Exception as e:
        return error_response(f"Failed to export query: {str(e)}", 500)


@export_bp.route('/queries/list', methods=['GET'])
def list_saved_exports():
    """
    GET /api/export/queries/list
    
    List saved export templates.
    
    Note: This endpoint returns mock data. In a production system,
    export templates would be stored in a database or file system.
    
    Response:
    {
        "success": true,
        "data": [
            {
                "template_id": "stock_levels",
                "name": "Current Stock Levels",
                "query": "SELECT * FROM unified_stocks WHERE is_active = 1",
                "description": "Export all active stock records"
            }
        ]
    }
    """
    try:
        # TODO: Implement actual saved export templates from database
        
        # Mock export templates
        templates = [
            {
                "template_id": "stock_levels",
                "name": "Current Stock Levels",
                "query": "SELECT stock_id, stock_type_name, cost_per_thousand, markup FROM unified_stocks WHERE is_active = 1",
                "description": "Export all active stock records with pricing",
                "created_at": "2025-10-01"
            },
            {
                "template_id": "job_usage",
                "name": "Stock Usage by Job",
                "query": "SELECT e.ticket_id, e.order_date, e.stock_id, u.stock_type_name FROM extracted_jobs e LEFT JOIN unified_stocks u ON e.stock_id = u.stock_id",
                "description": "Export job ticket stock usage data",
                "created_at": "2025-10-05"
            },
            {
                "template_id": "pricing_analysis",
                "name": "Pricing Analysis",
                "query": "SELECT stock_id, cost_per_thousand, markup, (cost_per_thousand * markup) as sell_price FROM unified_stocks ORDER BY cost_per_thousand DESC",
                "description": "Export pricing data for analysis",
                "created_at": "2025-10-10"
            }
        ]
        
        return list_response(templates, len(templates), f"Retrieved {len(templates)} export templates")
        
    except Exception as e:
        return error_response(f"Failed to list exports: {str(e)}", 500)


# Export blueprint
__all__ = ['export_bp']

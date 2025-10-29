"""
VSA AUTOMATION AI AGENT
Advanced AI agent with 25 specialized tools for transcript processing automation

Port: 5300
Framework: Flask + Anthropic Claude 4 Extended Thinking
Features:
- Multi-client database management
- Automated processing workflows
- Google Drive/Sheets/Gmail integration
- Real-time monitoring and notifications
- Batch operations orchestration
"""

from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import anthropic
import os
import sys
import json
import logging
import threading
import queue
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add project paths
sys.path.extend([
    str(Path(__file__).parent),
    str(Path(__file__).parent.parent),
    str(Path(__file__).parent.parent.parent)
])

from SUPABASE.supabase_config import SupabaseConfig
from tools.Database_Data import get_unified_connector

# Import agent tools
from agent_tools import AgentToolRegistry
from multi_client_manager import MultiClientDatabaseManager
from google_integrations import GoogleIntegrations
from notification_manager import NotificationManager
from processing_orchestrator import ProcessingOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    logger.error("❌ ANTHROPIC_API_KEY not found in environment")
    ANTHROPIC_API_KEY = SupabaseConfig.ANTHROPIC_API_KEY

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Global managers
tool_registry = AgentToolRegistry()
client_manager = MultiClientDatabaseManager()
google_integrations = GoogleIntegrations()
notification_manager = NotificationManager()
processing_orchestrator = ProcessingOrchestrator()

# Session storage
agent_sessions: Dict[str, Dict[str, Any]] = {}
conversation_history: Dict[str, List[Dict]] = {}

# ═══════════════════════════════════════════════════════════
# AGENT SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════

def get_or_create_session(session_id: str) -> Dict[str, Any]:
    """Get or create agent session"""
    if session_id not in agent_sessions:
        agent_sessions[session_id] = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'conversation_history': [],
            'active_client': None,
            'extended_thinking': True,
            'tools_used': [],
            'last_activity': datetime.now().isoformat()
        }
        conversation_history[session_id] = []
    
    return agent_sessions[session_id]


def log_agent_activity(session_id: str, activity_type: str, details: Dict):
    """Log agent activity for monitoring"""
    session = get_or_create_session(session_id)
    session['last_activity'] = datetime.now().isoformat()
    
    activity_log = {
        'timestamp': datetime.now().isoformat(),
        'type': activity_type,
        'details': details
    }
    
    if 'activity_log' not in session:
        session['activity_log'] = []
    
    session['activity_log'].append(activity_log)
    
    # Keep only last 100 activities
    if len(session['activity_log']) > 100:
        session['activity_log'] = session['activity_log'][-100:]


# ═══════════════════════════════════════════════════════════
# ANTHROPIC AI AGENT WITH EXTENDED THINKING
# ═══════════════════════════════════════════════════════════

def process_with_extended_thinking(
    user_message: str,
    session_id: str,
    extended_thinking: bool = True
) -> Generator[str, None, None]:
    """Process user request with Claude 4 Extended Thinking"""
    
    session = get_or_create_session(session_id)
    
    # Get conversation history
    history = conversation_history.get(session_id, [])
    
    # Build messages for Claude
    messages = history + [{
        "role": "user",
        "content": user_message
    }]
    
    # Get available tools from registry
    tools = tool_registry.get_claude_tools()
    
    try:
        # Stream response with extended thinking
        with anthropic_client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,
            temperature=0.3,
            thinking={
                "type": "enabled",
                "budget_tokens": 10000
            } if extended_thinking else None,
            tools=tools,
            messages=messages
        ) as stream:
            
            current_text = ""
            current_thinking = ""
            tool_calls = []
            
            for event in stream:
                # Handle different event types
                if event.type == "content_block_start":
                    if hasattr(event.content_block, 'type'):
                        if event.content_block.type == "thinking":
                            yield json.dumps({
                                'type': 'thinking_start',
                                'data': {}
                            }) + '\n'
                        elif event.content_block.type == "text":
                            yield json.dumps({
                                'type': 'text_start',
                                'data': {}
                            }) + '\n'
                
                elif event.type == "content_block_delta":
                    delta = event.delta
                    
                    if hasattr(delta, 'type'):
                        if delta.type == "thinking_delta":
                            # Stream thinking content
                            thinking_text = delta.thinking
                            current_thinking += thinking_text
                            yield json.dumps({
                                'type': 'thinking',
                                'data': {'text': thinking_text}
                            }) + '\n'
                        
                        elif delta.type == "text_delta":
                            # Stream response text
                            text = delta.text
                            current_text += text
                            yield json.dumps({
                                'type': 'text',
                                'data': {'text': text}
                            }) + '\n'
                
                elif event.type == "content_block_stop":
                    if hasattr(event.content_block, 'type'):
                        if event.content_block.type == "thinking":
                            yield json.dumps({
                                'type': 'thinking_complete',
                                'data': {'thinking': current_thinking}
                            }) + '\n'
                            current_thinking = ""
                        elif event.content_block.type == "tool_use":
                            # Tool call detected
                            tool_calls.append({
                                'id': event.content_block.id,
                                'name': event.content_block.name,
                                'input': event.content_block.input
                            })
            
            # Execute tool calls if any
            if tool_calls:
                yield json.dumps({
                    'type': 'tools_detected',
                    'data': {'count': len(tool_calls)}
                }) + '\n'
                
                for tool_call in tool_calls:
                    yield json.dumps({
                        'type': 'tool_start',
                        'data': {
                            'name': tool_call['name'],
                            'input': tool_call['input']
                        }
                    }) + '\n'
                    
                    # Execute tool
                    result = tool_registry.execute_tool(
                        tool_call['name'],
                        tool_call['input'],
                        session_id
                    )
                    
                    yield json.dumps({
                        'type': 'tool_result',
                        'data': {
                            'name': tool_call['name'],
                            'result': result
                        }
                    }) + '\n'
                    
                    # Log tool usage
                    log_agent_activity(session_id, 'tool_execution', {
                        'tool': tool_call['name'],
                        'input': tool_call['input'],
                        'result': result
                    })
            
            # Save conversation
            conversation_history[session_id].append({
                "role": "user",
                "content": user_message
            })
            conversation_history[session_id].append({
                "role": "assistant",
                "content": current_text
            })
            
            yield json.dumps({
                'type': 'complete',
                'data': {'text': current_text}
            }) + '\n'
    
    except Exception as e:
        logger.error(f"Error in AI processing: {e}")
        yield json.dumps({
            'type': 'error',
            'data': {'error': str(e)}
        }) + '\n'


# ═══════════════════════════════════════════════════════════
# API ROUTES - AGENT INTERFACE
# ═══════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Serve AI Agent Dashboard"""
    return render_template('agent_dashboard.html')


@app.route('/api/agent/chat', methods=['POST'])
def agent_chat():
    """Chat with AI agent (streaming)"""
    data = request.json
    session_id = data.get('session_id', 'default')
    user_message = data.get('message', '')
    extended_thinking = data.get('extended_thinking', True)
    
    def generate():
        for chunk in process_with_extended_thinking(user_message, session_id, extended_thinking):
            yield f"data: {chunk}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )


@app.route('/api/agent/session/<session_id>', methods=['GET'])
def get_session(session_id: str):
    """Get agent session details"""
    session = get_or_create_session(session_id)
    return jsonify({
        'success': True,
        'session': session
    })


@app.route('/api/agent/sessions', methods=['GET'])
def get_all_sessions():
    """Get all active agent sessions"""
    return jsonify({
        'success': True,
        'sessions': list(agent_sessions.values())
    })


# ═══════════════════════════════════════════════════════════
# API ROUTES - MULTI-CLIENT MANAGEMENT
# ═══════════════════════════════════════════════════════════

@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Get all configured clients"""
    clients = client_manager.get_all_clients()
    return jsonify({
        'success': True,
        'clients': clients
    })


@app.route('/api/clients/<client_id>', methods=['GET'])
def get_client_detail(client_id: str):
    """Get client database details"""
    client = client_manager.get_client(client_id)
    if client:
        return jsonify({
            'success': True,
            'client': client
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Client not found'
        }), 404


@app.route('/api/clients', methods=['POST'])
def create_client():
    """Add new client configuration"""
    data = request.json
    
    result = client_manager.add_client(
        client_id=data['client_id'],
        client_name=data['client_name'],
        supabase_url=data['supabase_url'],
        supabase_anon_key=data['supabase_anon_key'],
        supabase_service_key=data.get('supabase_service_key'),
        metadata=data.get('metadata', {})
    )
    
    return jsonify(result)


@app.route('/api/clients/<client_id>/test', methods=['POST'])
def test_client_connection(client_id: str):
    """Test client database connection"""
    result = client_manager.test_connection(client_id)
    return jsonify(result)


# ═══════════════════════════════════════════════════════════
# API ROUTES - AUTOMATED PROCESSING
# ═══════════════════════════════════════════════════════════

@app.route('/api/processing/trigger', methods=['POST'])
def trigger_processing():
    """Trigger automated processing workflow"""
    data = request.json
    
    result = processing_orchestrator.trigger_workflow(
        client_id=data.get('client_id'),
        workflow_type=data.get('workflow_type', 'full_pipeline'),
        config=data.get('config', {})
    )
    
    return jsonify(result)


@app.route('/api/processing/status', methods=['GET'])
def get_processing_status():
    """Get processing status across all clients"""
    status = processing_orchestrator.get_global_status()
    return jsonify({
        'success': True,
        'status': status
    })


@app.route('/api/processing/monitor', methods=['GET'])
def monitor_processing():
    """Real-time processing monitoring stream"""
    def generate():
        while True:
            status = processing_orchestrator.get_global_status()
            yield f"data: {json.dumps(status)}\n\n"
            threading.Event().wait(5)  # Update every 5 seconds
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream'
    )


# ═══════════════════════════════════════════════════════════
# API ROUTES - GOOGLE INTEGRATIONS
# ═══════════════════════════════════════════════════════════

@app.route('/api/google/drive/folders', methods=['GET'])
def list_drive_folders():
    """List Google Drive folders"""
    result = google_integrations.list_folders()
    return jsonify(result)


@app.route('/api/google/drive/files/<folder_id>', methods=['GET'])
def list_drive_files(folder_id: str):
    """List files in Google Drive folder"""
    result = google_integrations.list_files(folder_id)
    return jsonify(result)


@app.route('/api/google/drive/import/<file_id>', methods=['POST'])
def import_from_drive(file_id: str):
    """Import transcript from Google Drive file"""
    data = request.json
    client_id = data.get('client_id')
    
    result = google_integrations.import_file_to_client(file_id, client_id)
    return jsonify(result)


@app.route('/api/google/sheets/import', methods=['POST'])
def import_from_sheets():
    """Import from Google Sheets"""
    data = request.json
    
    result = google_integrations.import_from_sheets(
        spreadsheet_id=data['spreadsheet_id'],
        sheet_name=data.get('sheet_name', 'Sheet1'),
        client_id=data.get('client_id')
    )
    
    return jsonify(result)


@app.route('/api/google/gmail/monitor', methods=['POST'])
def setup_gmail_monitoring():
    """Setup Gmail monitoring for incoming transcripts"""
    data = request.json
    
    result = google_integrations.setup_email_monitoring(
        client_id=data['client_id'],
        email_filter=data.get('filter', {}),
        auto_import=data.get('auto_import', False)
    )
    
    return jsonify(result)


# ═══════════════════════════════════════════════════════════
# API ROUTES - NOTIFICATIONS
# ═══════════════════════════════════════════════════════════

@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    """Send notification (email/slack/sms)"""
    data = request.json
    
    result = notification_manager.send(
        notification_type=data['type'],
        recipient=data['recipient'],
        subject=data.get('subject'),
        message=data['message'],
        priority=data.get('priority', 'normal')
    )
    
    return jsonify(result)


@app.route('/api/notifications/setup', methods=['POST'])
def setup_notifications():
    """Setup automated notifications"""
    data = request.json
    
    result = notification_manager.setup_automation(
        client_id=data['client_id'],
        triggers=data['triggers'],
        channels=data['channels']
    )
    
    return jsonify(result)


# ═══════════════════════════════════════════════════════════
# API ROUTES - HEALTH & MONITORING
# ═══════════════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health_check():
    """Agent health check"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'version': '1.0.0',
        'active_sessions': len(agent_sessions),
        'connected_clients': len(client_manager.get_all_clients()),
        'uptime': 'N/A'  # TODO: Track uptime
    })


@app.route('/api/tools', methods=['GET'])
def list_tools():
    """List all available agent tools"""
    tools = tool_registry.get_all_tools()
    return jsonify({
        'success': True,
        'tools': tools
    })


# ═══════════════════════════════════════════════════════════
# RUN SERVER
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 70)
    print("🤖 VSA AUTOMATION AI AGENT - Advanced Processing Intelligence")
    print("=" * 70)
    print(f"🌐 Agent Dashboard: http://localhost:5300")
    print(f"🧠 AI Model: Claude 4 Sonnet with Extended Thinking")
    print(f"🔧 Tools Available: {len(tool_registry.get_all_tools())}")
    print(f"💾 Multi-Client Support: Enabled")
    print(f"📊 Features: Processing, Monitoring, Google APIs, Notifications")
    print("=" * 70)
    
    app.run(
        host='0.0.0.0',
        port=5300,
        debug=True,
        threaded=True
    )

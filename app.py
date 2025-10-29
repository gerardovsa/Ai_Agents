"""
AI Agent Platform - Flask Backend for Render.com
Main application entry point
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env.master (master configuration file)
# PRIORITY: Always use .env.master as the primary source
env_master_path = os.path.join(os.path.dirname(__file__), '.env.master')
env_path = os.path.join(os.path.dirname(__file__), '.env')

# Load .env.master with override=True to ensure it takes priority
if os.path.exists(env_master_path):
    load_dotenv(env_master_path, override=True)
    print("[OK] Loaded environment from: .env.master (primary)")
    print(f"     Service Account: {os.getenv('SERVICE_ACCOUNT_EMAIL', 'NOT FOUND')}")
    print(f"     Cloud Run Project: {os.getenv('GOOGLE_CLOUD_PROJECT', 'NOT FOUND')}")
    print(f"     Credentials File: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'NOT FOUND')}")
elif os.path.exists(env_path):
    # Fallback to .env if .env.master doesn't exist
    load_dotenv(env_path, override=True)
    print("[WARN] Loaded environment from: .env (fallback)")
else:
    print("[ERROR] No environment file found! Create .env.master or .env")

# Set Google Cloud credentials from environment variable (already set in .env.master)
gcp_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if gcp_creds and os.path.exists(gcp_creds):
    print(f"[OK] Google Cloud credentials configured")
    print(f"     Project: {os.getenv('GOOGLE_CLOUD_PROJECT', 'NOT SET')}")
    print(f"     Service Account: {os.getenv('CLOUD_RUN_SERVICE_ACCOUNT_EMAIL', 'NOT SET')}")

# Add paths to system path for proper imports
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dir, 'Render_backend'))
sys.path.insert(0, os.path.join(current_dir, 'AI_infrastructure'))
sys.path.insert(0, current_dir)  # Add root directory as well

try:
    from ai_render_integration import AIRenderClient
    ai_client = AIRenderClient()
    print("[OK] AI Render Client initialized")
except ImportError as e:
    print(f"[WARN] AI Render Client not available: {e}")
    ai_client = None

# Initialize Flask app
app = Flask(__name__)

# Configure session
app.secret_key = os.getenv('SESSION_SECRET', 'your-secret-key-change-in-production-VERY-IMPORTANT')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# ==================== REGISTER AI INFRASTRUCTURE BLUEPRINT ====================
# This enables 281 tools across 19 platforms (Slack, Gmail, WooCommerce, etc.)
try:
    # Add AI_infrastructure to Python path BEFORE importing
    ai_infra_path = os.path.join(current_dir, 'AI_infrastructure')
    if ai_infra_path not in sys.path:
        sys.path.insert(0, ai_infra_path)
    
    # Now import the blueprint
    from routes.agent_routes import agent_bp
    app.register_blueprint(agent_bp)
    print("AI Infrastructure blueprint registered with 281 tools")
    print("   Tools endpoint: /api/agent/tools")
    print("   Chat endpoint: /api/agent/chat (tool-enabled)")
    
    # Import authentication routes
    from routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)
    print("Authentication routes registered")
    print("   Endpoints: /api/auth/register, /api/auth/login, /api/auth/verify")
    
    # Import OAuth routes
    from routes.oauth_routes import oauth_bp
    app.register_blueprint(oauth_bp)
    print("OAuth routes registered")
    print("   Endpoints: /api/oauth/workspace/start, /api/oauth/workspace/callback")
    
    # Import Microsoft 365 authentication routes
    from routes.microsoft_auth_routes import microsoft_auth_bp
    app.register_blueprint(microsoft_auth_bp)
    print("Microsoft 365 authentication routes registered")
    print("   Endpoints: /api/auth/microsoft/login, /api/auth/microsoft/callback")
    
except ImportError as e:
    print(f"AI Infrastructure blueprint not available: {e}")
    print(f"   Import error details: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    print("   Using fallback simple chat endpoint")

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:*",
            "http://127.0.0.1:*",
            "https://*.onrender.com",
            "file://*"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Session storage (in-memory for now, use Redis in production)
sessions = {}

# ==================== HTML PAGE ROUTES ====================

from flask import render_template, send_from_directory

@app.route('/')
def index():
    """Landing page - redirect to login"""
    return render_template('login.html')

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        "status": "healthy",
        "service": "AI Agent Platform",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "ai_models": {
            "deepseek": bool(os.getenv('DEEPSEEK_API_KEY_1')),
            "anthropic": bool(os.getenv('ANTHROPIC_API_KEY')),
            "openai": bool(os.getenv('OPENAI_API_KEY'))
        },
        "integrations": {
            "google": bool(os.getenv('GOOGLE_OAUTH_CLIENT_ID')),
            "woocommerce": bool(os.getenv('WC_CONSUMER_KEY')),
            "cloudflare": bool(os.getenv('CLOUDFLARE_ACCOUNT_ID')),
            "supabase": bool(os.getenv('SUPABASE_URL'))
        }
    })

# ==================== AI AGENT ENDPOINTS ====================
# DEPRECATED: These endpoints are replaced by AI Infrastructure blueprint
# The simple endpoints below are kept as fallback only if blueprint fails to load

@app.route('/api/agent/chat-simple', methods=['POST'])
def agent_chat_simple():
    """
    DEPRECATED: Simple chat endpoint without tool integration
    Use /api/agent/chat instead (from AI Infrastructure blueprint)
    This endpoint is kept as fallback only
    """
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        context = data.get('context', {})
        provider = data.get('provider', 'deepseek')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get or create session
        if session_id not in sessions:
            sessions[session_id] = {
                "messages": [],
                "created_at": datetime.now().isoformat()
            }
        
        # Add user message to session
        sessions[session_id]["messages"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process with AI
        if ai_client:
            result = ai_client.process_with_ai(
                message,
                provider=provider,
                max_tokens=8000
            )
            
            if result.get("success"):
                response_text = result["content"]
                
                # Add AI response to session
                sessions[session_id]["messages"].append({
                    "role": "assistant",
                    "content": response_text,
                    "provider": result.get("provider"),
                    "model": result.get("model"),
                    "timestamp": datetime.now().isoformat()
                })
                
                return jsonify({
                    "response": response_text,
                    "session_id": session_id,
                    "provider": result.get("provider"),
                    "model": result.get("model"),
                    "usage": result.get("usage")
                })
            else:
                return jsonify({
                    "error": result.get("error", "AI processing failed"),
                    "provider": provider
                }), 500
        else:
            return jsonify({
                "error": "AI client not available"
            }), 503
            
    except Exception as e:
        print(f"[ERROR] Chat error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent/tools-simple', methods=['GET'])
def list_tools_simple():
    """
    DEPRECATED: Simple tools list without registry integration
    Use /api/agent/tools instead (from AI Infrastructure blueprint)
    This endpoint is kept as fallback only
    """
    tools = []
    
    # AI Models
    if os.getenv('DEEPSEEK_API_KEY_1'):
        tools.append({
            "name": "DeepSeek AI Chat",
            "platform": "DeepSeek",
            "category": "AI Models",
            "description": "Advanced AI reasoning and chat",
            "status": "active"
        })
    
    if os.getenv('ANTHROPIC_API_KEY'):
        tools.append({
            "name": "Claude AI Chat",
            "platform": "Anthropic",
            "category": "AI Models",
            "description": "Safety-focused AI assistant",
            "status": "active"
        })
    
    if os.getenv('OPENAI_API_KEY'):
        tools.append({
            "name": "GPT AI Chat",
            "platform": "OpenAI",
            "category": "AI Models",
            "description": "Advanced language model",
            "status": "active"
        })
    
    # Google Workspace
    if os.getenv('GOOGLE_OAUTH_CLIENT_ID'):
        tools.extend([
            {
                "name": "Google Docs",
                "platform": "Google",
                "category": "Productivity",
                "description": "Read and write Google Docs",
                "status": "configured"
            },
            {
                "name": "Google Sheets",
                "platform": "Google",
                "category": "Data",
                "description": "Read and write Google Sheets",
                "status": "configured"
            },
            {
                "name": "Google Drive",
                "platform": "Google",
                "category": "Storage",
                "description": "Access Google Drive files",
                "status": "configured"
            }
        ])
    
    # WooCommerce
    if os.getenv('WC_CONSUMER_KEY'):
        tools.extend([
            {
                "name": "WooCommerce Orders",
                "platform": "WooCommerce",
                "category": "E-Commerce",
                "description": "Manage store orders",
                "status": "configured"
            },
            {
                "name": "WooCommerce Products",
                "platform": "WooCommerce",
                "category": "E-Commerce",
                "description": "Manage products",
                "status": "configured"
            }
        ])
    
    # Cloudflare
    if os.getenv('CLOUDFLARE_ACCOUNT_ID'):
        tools.append({
            "name": "Cloudflare Workers",
            "platform": "Cloudflare",
            "category": "Infrastructure",
            "description": "Serverless computing",
            "status": "configured"
        })
    
    # Supabase
    if os.getenv('SUPABASE_URL'):
        tools.append({
            "name": "Supabase Database",
            "platform": "Supabase",
            "category": "Database",
            "description": "PostgreSQL database",
            "status": "configured"
        })
    
    return jsonify({
        "tools": tools,
        "total": len(tools),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/agent/models', methods=['GET'])
def list_models():
    """List available AI models"""
    models = []
    
    if os.getenv('DEEPSEEK_API_KEY_1'):
        models.append({
            "provider": "deepseek",
            "model": "deepseek-chat",
            "name": "DeepSeek Chat",
            "status": "active"
        })
    
    if os.getenv('ANTHROPIC_API_KEY'):
        models.append({
            "provider": "anthropic",
            "model": "claude-sonnet-4-20250514",
            "name": "Claude Sonnet 4",
            "status": "active"
        })
    
    if os.getenv('OPENAI_API_KEY'):
        models.append({
            "provider": "openai",
            "model": "gpt-4",
            "name": "GPT-4",
            "status": "active"
        })
    
    return jsonify({
        "models": models,
        "default": os.getenv('DEFAULT_AI_PROVIDER', 'deepseek')
    })

# ==================== SESSION MANAGEMENT ====================

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all sessions"""
    return jsonify({
        "sessions": [
            {
                "session_id": sid,
                "message_count": len(session["messages"]),
                "created_at": session["created_at"]
            }
            for sid, session in sessions.items()
        ]
    })

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify({
        "session_id": session_id,
        "messages": sessions[session_id]["messages"],
        "created_at": sessions[session_id]["created_at"]
    })

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print("=" * 80)
    print("AI AGENT PLATFORM - FLASK BACKEND")
    print("=" * 80)
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"AI Client: {'[OK] Available' if ai_client else '[WARN] Not available'}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print("=" * 80)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

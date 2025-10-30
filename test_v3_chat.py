"""
Test V3 Chat Endpoint - Minimal working chat with tool execution

This creates a minimal Flask endpoint using V3 infrastructure to test if 
we can process a chat request successfully.
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify
from anthropic import Anthropic

# Add root to path
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from AI_infrastructure.routes.agent_routes_v3 import (
    ToolExecutor,
    ToolCallProcessor
)

# Initialize Flask
app = Flask(__name__)

# Initialize V3 components
print("🔧 Initializing V3 components...")
tool_executor = ToolExecutor()
tool_processor = ToolCallProcessor(tool_executor)
print(f"✅ V3 components ready: {len(tool_executor.registry.tools)} tools loaded")

# Initialize Anthropic
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
if not anthropic_key:
    print("❌ ANTHROPIC_API_KEY not found in environment")
    sys.exit(1)

client = Anthropic(api_key=anthropic_key)
print(f"✅ Anthropic client initialized")


@app.route('/api/v3/chat', methods=['POST'])
def v3_chat():
    """
    Minimal V3 chat endpoint
    
    Request:
    {
        "message": "List my Gmail messages",
        "user_id": 1
    }
    
    Response:
    {
        "response": "AI response text",
        "tools_used": [...],
        "success": true
    }
    """
    
    try:
        data = request.get_json()
        message = data.get('message')
        user_id = data.get('user_id', 1)
        
        print(f"\n{'='*80}")
        print(f"📨 V3 CHAT REQUEST")
        print(f"{'='*80}")
        print(f"Message: {message}")
        print(f"User ID: {user_id}")
        
        # Step 1: Get tools for AI
        print(f"\n[1] Loading tools for Claude...")
        
        # Convert V3 tools to Anthropic format
        all_tools = []
        for tool_name, tool_def in tool_executor.registry.tools.items():
            # Convert to Anthropic input_schema format
            anthropic_tool = {
                "name": tool_name,
                "description": tool_def.get("description", ""),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
            # Convert parameters to input_schema
            params = tool_def.get("parameters", {})
            for param_name, param_info in params.items():
                # Handle case where param_info might be a string or dict
                if isinstance(param_info, str):
                    # Simple string type definition
                    anthropic_tool["input_schema"]["properties"][param_name] = {
                        "type": param_info,
                        "description": ""
                    }
                elif isinstance(param_info, dict):
                    # Full parameter definition
                    anthropic_tool["input_schema"]["properties"][param_name] = {
                        "type": param_info.get("type", "string"),
                        "description": param_info.get("description", "")
                    }
                    if param_info.get("required"):
                        anthropic_tool["input_schema"]["required"].append(param_name)
                else:
                    # Unknown format, skip
                    continue
            
            all_tools.append(anthropic_tool)
        
        print(f"✅ Loaded {len(all_tools)} tools for Claude")
        
        # Step 2: Build system prompt (minimal version)
        system_prompt = """You are an AI assistant with access to business tools.

When the user asks you to do something, USE THE TOOLS to accomplish it.

DO NOT describe what tools you would use - ACTUALLY USE THEM.

Use the Anthropic tool_use format:
{
  "type": "tool_use",
  "id": "toolu_01ABC...",
  "name": "tool_name",
  "input": {...}
}

Example: If user says "list my emails", use the gmail_list_messages tool."""
        
        # Step 3: Call Claude with tools
        print(f"\n[2] Calling Claude with tools...")
        
        conversation = [{"role": "user", "content": message}]
        
        response_obj = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8000,
            system=system_prompt,
            messages=conversation,
            tools=all_tools[:50],  # Limit to 50 tools for testing
            tool_choice={"type": "auto"}
        )
        
        print(f"✅ Claude responded")
        print(f"   Stop reason: {response_obj.stop_reason}")
        print(f"   Content blocks: {len(response_obj.content)}")
        
        # Step 4: Process response
        ai_response = ""
        tools_used = []
        
        for block in response_obj.content:
            if block.type == "text":
                ai_response += block.text
                print(f"   📝 Text block: {block.text[:100]}...")
                
            elif block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input
                tool_id = block.id
                
                print(f"\n   🔧 Tool use detected: {tool_name}")
                print(f"      ID: {tool_id}")
                print(f"      Input: {tool_input}")
                
                # Execute tool with V3 system
                print(f"   ⚙️ Executing with V3 system...")
                
                try:
                    # Simulate user credentials (would come from database)
                    user_credentials = {
                        "platform": "google",
                        "access_token": "test_token"
                    }
                    
                    result = tool_processor.process_tool_call(
                        tool_name=tool_name,
                        tool_input=tool_input,
                        user_id=user_id,
                        credentials=user_credentials
                    )
                    
                    print(f"   ✅ Tool executed: {result.get('status')}")
                    tools_used.append({
                        "name": tool_name,
                        "success": result.get("status") == "success",
                        "error": result.get("error")
                    })
                    
                except Exception as e:
                    print(f"   ❌ Tool execution failed: {e}")
                    tools_used.append({
                        "name": tool_name,
                        "success": False,
                        "error": str(e)
                    })
        
        # Step 5: Return response
        print(f"\n[3] Returning response to client...")
        
        return jsonify({
            "success": True,
            "response": ai_response,
            "tools_used": tools_used,
            "stop_reason": response_obj.stop_reason
        })
        
    except Exception as e:
        print(f"\n❌ Error in V3 chat: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/v3/status', methods=['GET'])
def v3_status():
    """Check if V3 system is operational"""
    return jsonify({
        "status": "operational",
        "version": "v3",
        "tools_loaded": len(tool_executor.registry.tools),
        "implementations": len(tool_executor.registry.implementations)
    })


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 V3 CHAT TEST SERVER")
    print("="*80)
    print(f"   Tools: {len(tool_executor.registry.tools)}")
    print(f"   Implementations: {len(tool_executor.registry.implementations)}")
    print(f"   Server: http://localhost:5002")
    print("="*80 + "\n")
    
    app.run(host='0.0.0.0', port=5002, debug=False)

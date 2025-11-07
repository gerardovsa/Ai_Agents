"""
AI Agents Tool Tester CLI
==========================

Rapid testing of tools with user credentials through the actual AI agent flow

Usage:
    python tool_tester.py                           # Interactive mode
    python tool_tester.py --user 12 --tool gmail_send_email --to test@example.com
    python tool_tester.py --list-users              # List all users
    python tool_tester.py --list-tools              # List all available tools
    python tool_tester.py --search gmail            # Search for tools by name
    
Features:
    - Tests through the REAL AI agent execution path (Flask API)
    - Uses the same credential injection as Claude would
    - Simulates actual tool_use blocks from Anthropic API
    - Shows full request/response for debugging
"""

import sys
import os
import json
import argparse
import requests
from typing import Dict, List, Optional
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from tools.registry_v3 import RegistryV3
import sqlite3

class ToolTester:
    """CLI tool for testing AI agent tools with user credentials through the real AI flow"""
    
    def __init__(self, api_url: str = "http://localhost:5001"):
        self.root_dir = Path(__file__).parent
        self.db_path = self.root_dir / 'data' / 'ai_infrastructure.db'
        self.registry = None
        self.api_url = api_url
        
    def check_server(self) -> bool:
        """Check if Flask server is running"""
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=2)
            return response.status_code == 200
        except:
            return False
        
    def init_registry(self):
        """Initialize tool registry"""
        if not self.registry:
            print("Loading tool registry...")
            self.registry = RegistryV3()
            print(f"Loaded {len(self.registry.tools)} tools")
    
    def list_users(self):
        """List all users in the system"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, role, created_at
            FROM users
            ORDER BY id
        """)
        users = cursor.fetchall()
        conn.close()
        
        if not users:
            print("No users found in database")
            return []
        
        print("\nAvailable Users:")
        print("-" * 100)
        print(f"{'ID':<5} {'Username':<20} {'Email':<35} {'Role':<10} {'Created':<20}")
        print("-" * 100)
        
        for user in users:
            user_id, username, email, role, created_at = user
            print(f"{user_id:<5} {username:<20} {email:<35} {role:<10} {created_at:<20}")
        
        print("-" * 100)
        return users
    
    def get_user_credentials(self, user_id: int) -> Dict:
        """Get user's OAuth credentials"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("SELECT username, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return {'error': f'User {user_id} not found'}
        
        # Get Google OAuth
        cursor.execute("""
            SELECT access_token, refresh_token, expires_at, is_valid
            FROM oauth_tokens
            WHERE user_id = ? AND platform = 'google'
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        google_oauth = cursor.fetchone()
        
        # Get Microsoft OAuth
        cursor.execute("""
            SELECT access_token, refresh_token, expires_at, is_valid
            FROM oauth_tokens
            WHERE user_id = ? AND platform = 'microsoft'
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        microsoft_oauth = cursor.fetchone()
        
        conn.close()
        
        return {
            'user_id': user_id,
            'username': user[0],
            'email': user[1],
            'google_oauth': {
                'has_token': bool(google_oauth),
                'is_valid': google_oauth[3] if google_oauth else False,
                'expires_at': google_oauth[2] if google_oauth else None
            } if google_oauth else None,
            'microsoft_oauth': {
                'has_token': bool(microsoft_oauth),
                'is_valid': microsoft_oauth[3] if microsoft_oauth else False,
                'expires_at': microsoft_oauth[2] if microsoft_oauth else None
            } if microsoft_oauth else None
        }
    
    def list_tools(self, search: str = None):
        """List available tools"""
        self.init_registry()
        
        tools = self.registry.tools
        
        if search:
            tools = {k: v for k, v in tools.items() if search.lower() in k.lower()}
        
        if not tools:
            print(f"No tools found matching '{search}'")
            return
        
        # Group by platform
        by_platform = {}
        for tool_name in tools.keys():
            platform = tool_name.split('_')[0] if '_' in tool_name else 'other'
            if platform not in by_platform:
                by_platform[platform] = []
            by_platform[platform].append(tool_name)
        
        print(f"\nAvailable Tools ({len(tools)} total):")
        print("=" * 100)
        
        for platform, tool_names in sorted(by_platform.items()):
            print(f"\n{platform.upper()} ({len(tool_names)} tools):")
            for tool_name in sorted(tool_names):
                print(f"  - {tool_name}")
        
        print("=" * 100)
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get detailed tool information"""
        self.init_registry()
        
        if tool_name not in self.registry.tools:
            print(f"Tool '{tool_name}' not found")
            return None
        
        tool = self.registry.get_tool(tool_name)
        
        print(f"\nTool: {tool_name}")
        print("=" * 100)
        print(f"Description: {tool.get('description', 'N/A')}")
        
        # Get parameters
        input_schema = tool.get('input_schema', {})
        properties = input_schema.get('properties', {})
        required = input_schema.get('required', [])
        
        if properties:
            print("\nParameters:")
            for param_name, param_info in properties.items():
                req_marker = "REQUIRED" if param_name in required else "optional"
                param_type = param_info.get('type', 'unknown')
                param_desc = param_info.get('description', '')
                print(f"  - {param_name} ({param_type}) [{req_marker}]")
                if param_desc:
                    print(f"      {param_desc}")
        
        print("=" * 100)
        return tool
    
    def execute_tool(self, tool_name: str, user_id: int, params: Dict):
        """Execute a tool through the REAL AI agent flow (Flask API)"""
        self.init_registry()
        
        # Check tool exists
        if tool_name not in self.registry.tools:
            print(f"ERROR: Tool '{tool_name}' not found")
            return None
        
        # Check server is running
        if not self.check_server():
            print(f"ERROR: Flask server not running at {self.api_url}")
            print("Please start the server with: BISTART")
            return None
        
        # Get user credentials
        creds = self.get_user_credentials(user_id)
        if 'error' in creds:
            print(f"ERROR: {creds['error']}")
            return None
        
        print(f"\nExecuting through AI Agent Flow: {tool_name}")
        print(f"API Endpoint: {self.api_url}/api/agent/execute-tool")
        print(f"User: {creds['username']} ({creds['email']})")
        print(f"Parameters: {json.dumps(params, indent=2)}")
        print("-" * 100)
        
        # Build request payload (simulating what Claude sends)
        payload = {
            "tool_name": tool_name,
            "tool_input": params,
            "user_id": user_id
        }
        
        print("\nRequest Payload:")
        print(json.dumps(payload, indent=2))
        print("-" * 100)
        
        # Execute through Flask API (the real AI agent path)
        try:
            response = requests.post(
                f"{self.api_url}/api/agent/execute-tool",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"\nResponse Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("\nRESULT (from AI agent flow):")
                print(json.dumps(result, indent=2, default=str))
                print("-" * 100)
                return result
            else:
                print(f"\nERROR Response:")
                print(response.text)
                print("-" * 100)
                return None
            
        except requests.exceptions.Timeout:
            print(f"\nERROR: Request timed out after 30 seconds")
            return None
        except Exception as e:
            print(f"\nERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def execute_tool_direct(self, tool_name: str, user_id: int, params: Dict):
        """Execute tool directly (bypassing Flask API) - for comparison"""
        self.init_registry()
        
        # Check tool exists
        if tool_name not in self.registry.tools:
            print(f"ERROR: Tool '{tool_name}' not found")
            return None
        
        # Get user credentials
        creds = self.get_user_credentials(user_id)
        if 'error' in creds:
            print(f"ERROR: {creds['error']}")
            return None
        
        print(f"\nExecuting DIRECTLY (bypassing AI flow): {tool_name}")
        print(f"User: {creds['username']} ({creds['email']})")
        print(f"Parameters: {json.dumps(params, indent=2)}")
        print("-" * 100)
        
        # Execute tool directly via registry
        try:
            result = self.registry.execute_tool(
                tool_name=tool_name,
                _user_id=user_id,
                _injected_credentials=True,
                **params
            )
            
            print("\nRESULT (direct execution):")
            print(json.dumps(result, indent=2, default=str))
            print("-" * 100)
            return result
            
        except Exception as e:
            print(f"\nERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def interactive_mode(self):
        """Interactive mode for testing tools"""
        print("\n" + "="*100)
        print("AI AGENTS TOOL TESTER - INTERACTIVE MODE")
        print("Testing through REAL AI agent execution flow (Flask API)")
        print("="*100)
        
        # Check server status
        if self.check_server():
            print(f"Server Status: ONLINE at {self.api_url}")
        else:
            print(f"WARNING: Server not detected at {self.api_url}")
            print("Some features require the server to be running (BISTART)")
        
        # Select user
        users = self.list_users()
        if not users:
            print("No users available. Please create a user first.")
            return
        
        while True:
            try:
                user_id = int(input("\nEnter User ID (or 0 to exit): "))
                if user_id == 0:
                    return
                
                creds = self.get_user_credentials(user_id)
                if 'error' not in creds:
                    break
                print(creds['error'])
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        # Show credentials
        print(f"\nUser: {creds['username']} ({creds['email']})")
        if creds['google_oauth']:
            status = "Valid" if creds['google_oauth']['is_valid'] else "Expired"
            print(f"  Google OAuth: {status} (expires: {creds['google_oauth']['expires_at']})")
        if creds['microsoft_oauth']:
            status = "Valid" if creds['microsoft_oauth']['is_valid'] else "Expired"
            print(f"  Microsoft OAuth: {status} (expires: {creds['microsoft_oauth']['expires_at']})")
        
        # Tool testing loop
        while True:
            print("\n" + "="*100)
            print("Commands:")
            print("  list [search]  - List tools (optionally filter by search term)")
            print("  info <tool>    - Show tool information")
            print("  test <tool>    - Test a tool through AI agent flow (Flask API)")
            print("  direct <tool>  - Test a tool directly (bypass Flask API)")
            print("  compare <tool> - Test both ways and compare results")
            print("  user           - Change user")
            print("  exit           - Exit")
            print("="*100)
            
            command = input("\nCommand: ").strip()
            
            if not command:
                continue
            
            parts = command.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None
            
            if cmd == 'exit':
                break
            
            elif cmd == 'user':
                return self.interactive_mode()
            
            elif cmd == 'list':
                self.list_tools(arg)
            
            elif cmd == 'info':
                if not arg:
                    print("Usage: info <tool_name>")
                else:
                    self.get_tool_info(arg)
            
            elif cmd == 'test':
                if not arg:
                    print("Usage: test <tool_name>")
                else:
                    self.test_tool_interactive(arg, user_id, mode='api')
            
            elif cmd == 'direct':
                if not arg:
                    print("Usage: direct <tool_name>")
                else:
                    self.test_tool_interactive(arg, user_id, mode='direct')
            
            elif cmd == 'compare':
                if not arg:
                    print("Usage: compare <tool_name>")
                else:
                    self.test_tool_interactive(arg, user_id, mode='compare')
            
            else:
                print(f"Unknown command: {cmd}")
    
    def test_tool_interactive(self, tool_name: str, user_id: int, mode: str = 'api'):
        """Interactive tool testing
        
        Args:
            mode: 'api' (through Flask), 'direct' (bypass Flask), or 'compare' (both)
        """
        # Get tool info
        tool = self.get_tool_info(tool_name)
        if not tool:
            return
        
        # Get parameters
        input_schema = tool.get('input_schema', {})
        properties = input_schema.get('properties', {})
        required = input_schema.get('required', [])
        
        params = {}
        
        print("\nEnter parameter values (press Enter to skip optional parameters):")
        
        for param_name, param_info in properties.items():
            param_type = param_info.get('type', 'string')
            param_desc = param_info.get('description', '')
            is_required = param_name in required
            
            while True:
                prompt = f"{param_name} ({param_type})"
                if is_required:
                    prompt += " [REQUIRED]"
                if param_desc:
                    prompt += f"\n  {param_desc}"
                prompt += "\n  Value: "
                
                value = input(prompt).strip()
                
                if not value and not is_required:
                    break
                
                if not value and is_required:
                    print("  This parameter is required!")
                    continue
                
                # Type conversion
                try:
                    if param_type == 'integer':
                        params[param_name] = int(value)
                    elif param_type == 'number':
                        params[param_name] = float(value)
                    elif param_type == 'boolean':
                        params[param_name] = value.lower() in ('true', 'yes', '1')
                    elif param_type == 'array':
                        # Simple comma-separated list
                        params[param_name] = [v.strip() for v in value.split(',')]
                    else:
                        params[param_name] = value
                    break
                except ValueError as e:
                    print(f"  Invalid value for {param_type}: {e}")
        
        # Confirm execution
        print("\n" + "="*100)
        print("Ready to execute:")
        print(f"Tool: {tool_name}")
        print(f"Mode: {mode.upper()}")
        print(f"Parameters: {json.dumps(params, indent=2)}")
        confirm = input("\nExecute? (y/n): ").strip().lower()
        
        if confirm != 'y':
            return
        
        # Execute based on mode
        if mode == 'api':
            self.execute_tool(tool_name, user_id, params)
        elif mode == 'direct':
            self.execute_tool_direct(tool_name, user_id, params)
        elif mode == 'compare':
            print("\n" + "="*100)
            print("COMPARISON TEST")
            print("="*100)
            
            print("\n>>> TEST 1: Through AI Agent Flow (Flask API)")
            print("="*100)
            result_api = self.execute_tool(tool_name, user_id, params)
            
            print("\n>>> TEST 2: Direct Registry Execution")
            print("="*100)
            result_direct = self.execute_tool_direct(tool_name, user_id, params)
            
            print("\n" + "="*100)
            print("COMPARISON RESULTS")
            print("="*100)
            
            if result_api and result_direct:
                print("Both methods succeeded")
                if json.dumps(result_api, sort_keys=True) == json.dumps(result_direct, sort_keys=True):
                    print("Results are IDENTICAL")
                else:
                    print("Results DIFFER:")
                    print("\nAPI Result:")
                    print(json.dumps(result_api, indent=2, default=str))
                    print("\nDirect Result:")
                    print(json.dumps(result_direct, indent=2, default=str))
            elif result_api and not result_direct:
                print("API succeeded, Direct failed")
            elif not result_api and result_direct:
                print("Direct succeeded, API failed")
            else:
                print("Both methods failed")
            print("="*100)


def main():
    parser = argparse.ArgumentParser(
        description='AI Agents Tool Tester - Test tools through the REAL AI agent execution flow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tool_tester.py                                    # Interactive mode
  python tool_tester.py --list-users                       # List all users
  python tool_tester.py --list-tools                       # List all tools
  python tool_tester.py --search gmail                     # Search for gmail tools
  python tool_tester.py --info gmail_send_email            # Show tool info
  
  # Test through AI agent flow (Flask API - default)
  python tool_tester.py --user 12 --tool gmail_send_email --params '{"to":"test@example.com","subject":"Test","body":"Hello"}'
  
  # Test directly (bypass Flask API)
  python tool_tester.py --user 12 --tool gmail_send_email --params '{"to":"test@example.com","subject":"Test","body":"Hello"}' --direct
  
  # Compare both methods
  python tool_tester.py --user 12 --tool google_slides_create_presentation --params '{"title":"Test"}' --compare
        """
    )
    
    parser.add_argument('--list-users', action='store_true', help='List all users')
    parser.add_argument('--list-tools', action='store_true', help='List all tools')
    parser.add_argument('--search', type=str, help='Search for tools by name')
    parser.add_argument('--info', type=str, help='Show tool information')
    parser.add_argument('--user', type=int, help='User ID for tool execution')
    parser.add_argument('--tool', type=str, help='Tool name to execute')
    parser.add_argument('--params', type=str, help='Tool parameters as JSON')
    parser.add_argument('--direct', action='store_true', help='Execute directly (bypass Flask API)')
    parser.add_argument('--compare', action='store_true', help='Compare API vs direct execution')
    parser.add_argument('--api-url', type=str, default='http://localhost:5001', help='Flask API URL (default: http://localhost:5001)')
    
    args = parser.parse_args()
    
    tester = ToolTester(api_url=args.api_url)
    
    # Handle commands
    if args.list_users:
        tester.list_users()
    
    elif args.list_tools:
        tester.list_tools()
    
    elif args.search:
        tester.list_tools(args.search)
    
    elif args.info:
        tester.get_tool_info(args.info)
    
    elif args.user and args.tool:
        # Execute tool
        params = {}
        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError as e:
                print(f"Error parsing params JSON: {e}")
                sys.exit(1)
        
        # Determine execution mode
        if args.compare:
            # Compare both methods
            print("\n" + "="*100)
            print("COMPARISON TEST")
            print("="*100)
            
            print("\n>>> TEST 1: Through AI Agent Flow (Flask API)")
            print("="*100)
            result_api = tester.execute_tool(args.tool, args.user, params)
            
            print("\n>>> TEST 2: Direct Registry Execution")
            print("="*100)
            result_direct = tester.execute_tool_direct(args.tool, args.user, params)
            
            print("\n" + "="*100)
            print("COMPARISON RESULTS")
            print("="*100)
            
            if result_api and result_direct:
                print("Both methods succeeded")
                if json.dumps(result_api, sort_keys=True) == json.dumps(result_direct, sort_keys=True):
                    print("Results are IDENTICAL")
                else:
                    print("Results DIFFER")
            elif result_api and not result_direct:
                print("API succeeded, Direct failed")
            elif not result_api and result_direct:
                print("Direct succeeded, API failed")
            else:
                print("Both methods failed")
            print("="*100)
            
        elif args.direct:
            # Direct execution
            tester.execute_tool_direct(args.tool, args.user, params)
        else:
            # API execution (default)
            tester.execute_tool(args.tool, args.user, params)
    
    else:
        # Interactive mode
        tester.interactive_mode()


if __name__ == '__main__':
    main()

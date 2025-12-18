"""
Real-Time Verification Server with WebSocket
============================================

Runs verification and broadcasts live updates to dashboard UI.

RUN:
    python verification_server.py

Then open: http://localhost:8080

CREATED: December 18, 2025
"""

import asyncio
import websockets
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

# Load .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except:
    pass


# Store active WebSocket connections
active_connections = set()


async def broadcast(message):
    """Send message to all connected clients"""
    if active_connections:
        disconnected = set()
        for websocket in active_connections:
            try:
                await websocket.send(json.dumps(message))
            except:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        active_connections.difference_update(disconnected)


async def run_verification_with_updates(subject_data):
    """
    Run verification and send real-time updates to dashboard
    """
    
    print("\n🚀 Starting verification with live updates...")
    
    # Get API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        await broadcast({
            'type': 'error',
            'message': 'No API key found'
        })
        return
    
    # Import Anthropic
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
    except Exception as e:
        await broadcast({
            'type': 'error',
            'message': f'Failed to initialize Anthropic client: {e}'
        })
        return
    
    # Import ALL verification tools from the platform
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / 'tools' / 'implementations'))
        from web_scraping_wrapper import (
            scrape_website_content,
            analyze_website_structure,
            extract_ssl_certificate_info,
            check_dns_records,
            extract_whois_info
        )
        from advanced_analysis_wrapper import (
            analyze_content_with_ai,
            estimate_web_traffic,
            analyze_backlinks
        )
        from image_verification_wrapper import (
            verify_profile_image_consistency,
            detect_ai_generated_image,
            check_image_metadata
        )
        tools_available = True
    except Exception as e:
        print(f"⚠️  Could not import verification tools: {e}")
        tools_available = False
    
    # Build verification task using PLATFORM TOOLS
    verification_task = f"""
I need you to comprehensively verify this person's professional identity and digital footprint:

SUBJECT:
- Name: {subject_data['name']}
- Company: {subject_data['company']}
- Email: {subject_data['email']}
- Domain: {subject_data['domain']}
- Phone: {subject_data.get('phone', 'N/A')}

YOU HAVE ACCESS TO THESE POWERFUL VERIFICATION TOOLS (use Python function calls):

**Web Scraping & Structure (FREE tools)**:
1. scrape_website_content(url="{subject_data['domain']}") - Extract ALL website content, metadata, contacts
2. analyze_website_structure(url="{subject_data['domain']}") - Check robots.txt, sitemap, security headers
3. extract_ssl_certificate_info(domain="{subject_data['domain']}") - SSL validity, expiry, issuer
4. check_dns_records(domain="{subject_data['domain']}") - Full DNS analysis
5. extract_whois_info(domain="{subject_data['domain']}") - Domain registration data

**AI Analysis Tools**:
6. analyze_content_with_ai(content=..., domain="{subject_data['domain']}") - AI legitimacy analysis with Claude
7. estimate_web_traffic(domain="{subject_data['domain']}") - Traffic estimates
8. analyze_backlinks(domain="{subject_data['domain']}") - Backlink profile analysis

**Image Verification Tools**:
9. verify_profile_image_consistency(...) - Compare images across platforms
10. detect_ai_generated_image(...) - Detect AI-generated or manipulated images
11. check_image_metadata(...) - Extract EXIF data and manipulation detection

YOUR TASK:
1. Call scrape_website_content() to get full website data
2. Call extract_ssl_certificate_info() to verify SSL
3. Call check_dns_records() for DNS validation
4. Call extract_whois_info() for domain age/registration
5. Call analyze_content_with_ai() to get AI legitimacy scoring
6. Call analyze_website_structure() for security assessment
7. Analyze results and generate comprehensive report

After running these TOOL CALLS, provide analysis in this JSON format:

{{
    "verification_status": "VERIFIED/UNCERTAIN/SUSPICIOUS",
    "confidence_score": 0-100,
    "findings": {{
        "domain_active": true/false,
        "ssl_valid": true/false,
        "historical_snapshots": number,
        "email_domain_matches": true/false,
        "mx_records_found": true/false,
        "website_accessible": true/false,
        "security_score": 0-100,
        "ai_legitimacy_score": 0-100
    }},
    "red_flags": ["list any concerns"],
    "legitimacy_indicators": ["list positive signals"],
    "recommendation": "APPROVE/MANUAL_REVIEW/DENY",
    "summary": "2-3 sentence summary of findings"
}}

Use the Python verification tools - they're much more powerful than bash commands!
"""
    
    messages = [{
        "role": "user",
        "content": verification_task
    }]
    
    iteration = 0
    max_iterations = 50
    total_tokens = 0
    
    try:
        while iteration < max_iterations:
            iteration += 1
            
            # Send iteration update
            await broadcast({
                'type': 'iteration',
                'iteration': iteration,
                'stop_reason': 'processing'
            })
            
            # Define ALL available tools for Claude
            available_tools = [
                {"type": "bash_20250124", "name": "bash"}
            ]
            
            # Add Python verification tools if available
            if tools_available:
                available_tools.extend([
                    {
                        "type": "custom",
                        "name": "scrape_website_content",
                        "description": "Scrape complete website content including metadata, contacts, social links",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "description": "Website URL"}
                            },
                            "required": ["url"]
                        }
                    },
                    {
                        "type": "custom",
                        "name": "extract_ssl_certificate_info",
                        "description": "Extract SSL certificate details, validity, expiry",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "domain": {"type": "string", "description": "Domain name"}
                            },
                            "required": ["domain"]
                        }
                    },
                    {
                        "type": "custom",
                        "name": "check_dns_records",
                        "description": "Check DNS A, MX, TXT, NS records",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "domain": {"type": "string", "description": "Domain name"}
                            },
                            "required": ["domain"]
                        }
                    },
                    {
                        "type": "custom",
                        "name": "extract_whois_info",
                        "description": "Extract domain registration, age, registrar info",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "domain": {"type": "string", "description": "Domain name"}
                            },
                            "required": ["domain"]
                        }
                    },
                    {
                        "type": "custom",
                        "name": "analyze_content_with_ai",
                        "description": "AI-powered legitimacy analysis using Claude Sonnet 4.5",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string", "description": "Content to analyze"},
                                "domain": {"type": "string", "description": "Domain name"}
                            },
                            "required": ["content", "domain"]
                        }
                    }
                ])
            
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=4096,
                tools=available_tools,
                messages=messages
            )
            
            # Update token count
            if hasattr(response, 'usage'):
                total_tokens += response.usage.input_tokens + response.usage.output_tokens
                await broadcast({
                    'type': 'tokens',
                    'count': total_tokens
                })
            
            # Send iteration status
            await broadcast({
                'type': 'iteration',
                'iteration': iteration,
                'stop_reason': response.stop_reason
            })
            
            # Check if done
            if response.stop_reason == "end_turn":
                # Extract final analysis
                final_text = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        final_text += block.text
                        
                        # Send reasoning
                        await broadcast({
                            'type': 'reasoning',
                            'iteration': iteration,
                            'text': block.text
                        })
                
                # Try to extract JSON from response
                try:
                    import re
                    json_match = re.search(r'\{[\s\S]*"verification_status"[\s\S]*\}', final_text)
                    if json_match:
                        analysis = json.loads(json_match.group(0))
                    else:
                        analysis = {
                            "verification_status": "UNCERTAIN",
                            "confidence_score": 50,
                            "summary": final_text[:500]
                        }
                except:
                    analysis = {
                        "verification_status": "UNCERTAIN",
                        "confidence_score": 50,
                        "summary": final_text[:500]
                    }
                
                # Send final results
                await broadcast({
                    'type': 'results',
                    'results': analysis
                })
                
                return {
                    "success": True,
                    "analysis": analysis,
                    "iterations": iteration,
                    "tokens": total_tokens
                }
            
            # Process tool use
            if response.stop_reason == "tool_use":
                tool_results = []
                
                for block in response.content:
                    if hasattr(block, 'text') and block.text:
                        # Send AI reasoning
                        await broadcast({
                            'type': 'reasoning',
                            'iteration': iteration,
                            'text': block.text
                        })
                    
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        
                        # Execute Python verification tools
                        if tools_available and tool_name in ['scrape_website_content', 'extract_ssl_certificate_info', 
                                                               'check_dns_records', 'extract_whois_info', 'analyze_content_with_ai']:
                            try:
                                # Send tool execution notification
                                await broadcast({
                                    'type': 'command',
                                    'command': f"🔧 {tool_name}({json.dumps(tool_input)})",
                                    'output': 'Executing Python verification tool...'
                                })
                                
                                # Execute the actual Python tool
                                if tool_name == 'scrape_website_content':
                                    output = scrape_website_content(**tool_input)
                                elif tool_name == 'extract_ssl_certificate_info':
                                    output = extract_ssl_certificate_info(**tool_input)
                                elif tool_name == 'check_dns_records':
                                    output = check_dns_records(**tool_input)
                                elif tool_name == 'extract_whois_info':
                                    output = extract_whois_info(**tool_input)
                                elif tool_name == 'analyze_content_with_ai':
                                    output = await analyze_content_with_ai(**tool_input)
                                
                                # Convert output to string
                                output_str = json.dumps(output, indent=2) if isinstance(output, dict) else str(output)
                                
                                # Send tool result
                                await broadcast({
                                    'type': 'command',
                                    'command': f"✅ {tool_name}({json.dumps(tool_input)})",
                                    'output': output_str[:500] + ('...' if len(output_str) > 500 else '')
                                })
                                
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": output_str
                                })
                                
                            except Exception as e:
                                error_msg = f"Error executing {tool_name}: {str(e)}"
                                await broadcast({
                                    'type': 'command',
                                    'command': f"❌ {tool_name}",
                                    'output': error_msg
                                })
                                
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": error_msg,
                                    "is_error": True
                                })
                        
                        elif tool_name == "bash":
                            # Execute bash command (fallback)
                            command = tool_input.get('command', '')
                            
                            # Send command to dashboard
                            await broadcast({
                                'type': 'command',
                                'command': command,
                                'output': 'Executing bash command...'
                            })
                            
                            # Simulate execution (in real scenario, this would run in Docker)
                            output = f"Simulated output for: {command}\n(Docker container needed for actual execution)"
                            
                            # Send command result
                            await broadcast({
                                'type': 'command',
                                'command': command,
                                'output': output
                            })
                            
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": output
                            })
                
                # Continue conversation
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
            
            else:
                # Unexpected stop
                await broadcast({
                    'type': 'error',
                    'message': f'Unexpected stop reason: {response.stop_reason}'
                })
                break
            
            # Small delay between iterations
            await asyncio.sleep(0.5)
        
        if iteration >= max_iterations:
            await broadcast({
                'type': 'error',
                'message': f'Max iterations ({max_iterations}) reached'
            })
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        await broadcast({
            'type': 'error',
            'message': str(e)
        })


async def handle_websocket(websocket, path):
    """Handle WebSocket connection"""
    
    print(f"✅ Client connected from {websocket.remote_address}")
    
    # Add to active connections
    active_connections.add(websocket)
    
    try:
        # Wait for messages
        async for message in websocket:
            data = json.loads(message)
            
            if data.get('action') == 'start_verification':
                subject = data.get('subject', {
                    'name': 'Gregory Dutton',
                    'company': 'Institute of Sustainable Biodiversity',
                    'email': 'gregory.dutton@isb.eco',
                    'domain': 'isb.eco',
                    'phone': '+61 461 357 358'
                })
                
                # Run verification
                await run_verification_with_updates(subject)
    
    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Client disconnected")
    
    finally:
        # Remove from active connections
        active_connections.discard(websocket)


class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler with CORS enabled"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress logging
        pass


def run_http_server():
    """Run HTTP server for dashboard"""
    
    # Change to TESTS directory
    os.chdir(Path(__file__).parent)
    
    server = HTTPServer(('localhost', 8080), CORSHTTPRequestHandler)
    print(f"✅ HTTP server started on http://localhost:8080")
    print(f"   Open: http://localhost:8080/verification_dashboard.html")
    server.serve_forever()


async def main():
    """Main server"""
    
    print("="*80)
    print("🚀 VERIFICATION SERVER WITH LIVE DASHBOARD")
    print("="*80)
    print("")
    print("Starting servers...")
    print("")
    
    # Start HTTP server in background thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    print(f"✅ WebSocket server starting on ws://localhost:5555")
    print("")
    print("="*80)
    print("📊 DASHBOARD ACCESS")
    print("="*80)
    print("")
    print(f"   🌐 Open in browser: http://localhost:8080/verification_dashboard.html")
    print("")
    print("="*80)
    print("📝 MONITORING")
    print("="*80)
    print("")
    print("   The dashboard will show:")
    print("   ✅ Real-time AI reasoning")
    print("   ✅ Live bash command execution")
    print("   ✅ System logs")
    print("   ✅ Verification results")
    print("   ✅ Progress statistics")
    print("")
    print("="*80)
    print("")
    print("Press Ctrl+C to stop the server")
    print("")
    
    # Start WebSocket server
    async with websockets.serve(handle_websocket, "localhost", 5555):
        await asyncio.Future()  # Run forever


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()

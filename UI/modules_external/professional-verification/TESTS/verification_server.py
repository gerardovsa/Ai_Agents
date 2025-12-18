"""
Enhanced Verification Server with Comprehensive Risk Assessment
================================================================

Runs verification with:
- Multiple search variations and objective scrutiny
- Risk management analysis and mitigation strategies
- Comprehensive markdown reports with appendix
- Real-time dashboard updates

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
import re

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
    Run ENHANCED verification with comprehensive risk assessment and markdown reporting
    """
    
    print("\n🚀 Starting ENHANCED verification with comprehensive analysis...")
    
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
    
    # Build COMPREHENSIVE verification prompt with markdown reporting
    verification_task = f"""
You are a professional verification specialist conducting a comprehensive risk assessment. You must be OBJECTIVE, THOROUGH, and execute MULTIPLE search variations.

# SUBJECT TO VERIFY

**Name:** {subject_data['name']}
**Company:** {subject_data['company']}
**Email:** {subject_data['email']}
**Domain:** {subject_data['domain']}
**Phone:** {subject_data.get('phone', 'N/A')}

# COMPREHENSIVE VERIFICATION PROTOCOL

Execute ALL these checks using bash commands. DO NOT skip any. Be thorough and skeptical.

## Phase 1: Domain & Infrastructure (Multiple Methods)

1. **Domain Resolution** - Try ALL these:
   ```bash
   curl -I https://{subject_data['domain']}
   curl -I https://www.{subject_data['domain']}
   curl -I http://{subject_data['domain']}
   nslookup {subject_data['domain']}
   nslookup {subject_data['domain']} 8.8.8.8
   ping -c 2 {subject_data['domain']}
   ```

2. **SSL Deep Analysis**:
   ```bash
   openssl s_client -connect {subject_data['domain']}:443 </dev/null 2>&1 | head -n 30
   echo | openssl s_client -connect {subject_data['domain']}:443 2>/dev/null | openssl x509 -noout -dates
   echo | openssl s_client -connect {subject_data['domain']}:443 2>/dev/null | openssl x509 -noout -issuer
   ```

3. **Email Infrastructure**:
   ```bash
   nslookup -type=mx {subject_data['email'].split('@')[1]}
   nslookup -type=txt {subject_data['email'].split('@')[1]} | grep -i spf
   ```

## Phase 2: Web Presence (Multiple Pages)

4. **Website Content**:
   ```bash
   curl -s https://{subject_data['domain']} | head -n 100
   curl -s https://{subject_data['domain']}/about | head -n 50
   curl -s https://{subject_data['domain']}/team | head -n 50
   curl -s https://{subject_data['domain']}/contact | head -n 50
   curl -s https://{subject_data['domain']}/robots.txt
   curl -s https://{subject_data['domain']}/sitemap.xml | head -n 50
   ```

5. **Historical Data**:
   ```bash
   curl -s "http://archive.org/wayback/available?url={subject_data['domain']}"
   curl -s "http://web.archive.org/cdx/search/cdx?url={subject_data['domain']}&output=json" | head -n 20
   ```

## Phase 3: CRITICAL - Multiple Search Variations

DO MULTIPLE searches, not just one! Try these variations:

6. **Name Searches** (simulate or note what to search):
   - "{subject_data['name']}" "{subject_data['company']}"
   - "{subject_data['name']}" LinkedIn
   - "{subject_data['name']}" "{subject_data['domain']}"
   - "{subject_data['name']}" professional bio
   - "{subject_data['name']}" research
   - "{subject_data['name']}" contact

7. **Company Searches**:
   - "{subject_data['company']}" official
   - "{subject_data['company']}" registration
   - "{subject_data['company']}" LinkedIn
   - "{subject_data['company']}" news

## Phase 4: Cross-Reference

8. **Consistency Checks**:
   - Email matches domain?
   - Phone country code matches location?
   - Website claims match searches?

# OUTPUT: COMPREHENSIVE MARKDOWN REPORT

After executing ALL checks above, generate a complete markdown report with this EXACT structure:

```markdown
# Professional Identity Verification Report

**Subject:** {subject_data['name']}  
**Organization:** {subject_data['company']}  
**Verification Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Report ID:** VER-{datetime.now().strftime('%Y%m%d-%H%M%S')}

---

## Executive Summary

[3-4 sentences: What you found, overall risk level, key concerns]

**Overall Risk:** [CRITICAL/HIGH/MEDIUM/LOW]  
**Confidence:** [0-100]%  
**Recommendation:** [APPROVE/MANUAL_REVIEW/DENY]

---

## 1. Subject Information Verification

| Field | Value | Status | Notes |
|-------|-------|--------|-------|
| Name | {subject_data['name']} | ✓/⚠/✗ | [Found in X sources / Not found] |
| Organization | {subject_data['company']} | ✓/⚠/✗ | [Verified via Y / Claims only] |
| Email | {subject_data['email']} | ✓/⚠/✗ | [Domain matches / Suspicious] |
| Domain | {subject_data['domain']} | ✓/⚠/✗ | [Active / Inactive / Issues] |
| Phone | {subject_data.get('phone')} | ✓/⚠/✗ | [Format valid / Unverified] |

---

## 2. Technical Infrastructure Analysis

### 2.1 Domain Status
**Finding:** [Explain what you discovered]  
**Evidence:** [Results from curl, nslookup commands]  
**Risk Level:** [LOW/MEDIUM/HIGH]

### 2.2 SSL Certificate
**Finding:** [Valid/Invalid/Expired - details]  
**Issuer:** [Certificate authority]  
**Expiry:** [Date]  
**Risk Level:** [LOW/MEDIUM/HIGH]

### 2.3 Email Infrastructure
**MX Records:** [Found/Not found]  
**SPF:** [Configured/Missing]  
**Match:** [Email domain matches company domain? Yes/No]  
**Risk Level:** [LOW/MEDIUM/HIGH]

### 2.4 Website Security
**HTTPS:** [Enabled/Disabled]  
**Headers:** [Security headers present]  
**Content:** [Professional/Amateur/Suspicious]  
**Risk Level:** [LOW/MEDIUM/HIGH]

---

## 3. Historical & Digital Footprint

### 3.1 Web Archive History
**Snapshots Found:** [Number]  
**First Recorded:** [Date or "Not found"]  
**Last Activity:** [Date]  
**Analysis:** [Legitimate history / Recent creation / Gaps / Suspicious]

### 3.2 Search Presence Analysis

Document EACH search variation you tried:

#### Search: "{subject_data['name']} {subject_data['company']}"
- **Results:** [Found/Limited/None]
- **Quality:** [Professional/Personal/Suspicious]
- **Consistency:** [Matches claimed identity / Contradicts / Unclear]

#### Search: "{subject_data['name']} LinkedIn"
- **Profile Found:** [Yes/No]
- **Details:** [Job title, connections, activity level]
- **Verification:** [Matches/Doesn't match]

#### Search: "{subject_data['name']} {subject_data['domain']}"
- **Results:** [Found/Not found]
- **Context:** [Official listings / News / Other]

[Continue for ALL search variations performed...]

**Overall Digital Footprint:** [Strong/Moderate/Weak/Absent/Suspicious]

---

## 4. Risk Assessment

### 4.1 CRITICAL Risks 🔴
[List any immediate red flags]
- **[Risk Name]:** [Description]
  - **Impact:** [Why this matters]
  - **Evidence:** [What triggered this]
  - **Mitigation:** [What to do about it]

### 4.2 HIGH Risks 🟠
[Significant concerns]
- **[Risk Name]:** [Description + Impact + Evidence]

### 4.3 MEDIUM Risks 🟡
[Moderate concerns to monitor]

### 4.4 LOW Risks 🟢
[Minor notes]

### 4.5 Positive Indicators ✅
[Evidence supporting legitimacy]
- **[Indicator]:** [Description and supporting evidence]

---

## 5. Mitigation Strategies

### If CRITICAL/HIGH Risks Exist:

**Immediate Actions:**
1. **[Action]:** [What to do, why, when]
2. **[Action]:** [Details]

**Additional Verification:**
1. **[Step]:** [How to further verify]
2. **[Step]:** [Resources needed]

**Monitoring Plan:**
- **[What to monitor]:** [Frequency, what to watch for]

---

## 6. Methodology Explanation

### What I Did and Why

**Approach:** [Explain your verification strategy]

**Commands Executed:** [Total count]
- Domain checks: [Number] variations
- SSL analysis: [Number] methods
- Email verification: [Number] checks  
- Web searches: [Number] variations
- Historical analysis: [Number] sources

**Why Multiple Searches:** [Explain importance of not taking things at face value]

**Objective Scrutiny:** [How you remained unbiased]

---

## 7. Final Recommendation

**Decision:** [APPROVE / MANUAL_REVIEW / DENY]

**Justification:**
[Detailed explanation referencing specific findings. Be clear about:
- What was verified
- What couldn't be verified
- What raised concerns
- Why this recommendation makes sense]

**Confidence:** [0-100]%

**Next Steps:**
1. [Specific action if approved]
2. [Specific action if denied]
3. [What to monitor ongoing]

---

## Appendix A: Raw Command Outputs

### Domain Resolution
```bash
# Command: curl -I https://{subject_data['domain']}
[Paste actual output]

# Command: nslookup {subject_data['domain']}
[Paste actual output]
```

### SSL Certificate
```
[Full SSL output]
```

### Email Infrastructure
```
[MX records output]
[SPF/DMARC results]
```

### Website Content Samples
```
[Relevant excerpts]
```

### Historical Data
```json
[Archive.org responses]
```

---

## Appendix B: Search Results Summary

| Search Query | Found | Quality | Notes |
|--------------|-------|---------|-------|
| [Query 1] | Y/N | [Rating] | [Brief note] |
| [Query 2] | Y/N | [Rating] | [Brief note] |
[All searches...]

---

## Document Control

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Analyst:** Claude AI Verification System v2.0  
**Protocol:** Enhanced Multi-Source Validation  
**Iterations:** [Count]  
**Commands:** [Count]  
**Confidential:** Yes

---

*This automated verification should be reviewed by qualified personnel before final decisions.*
```

CRITICAL: Fill in EVERY section. Include ALL raw outputs in appendix. Be thorough, objective, and explain your reasoning
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
                # Extract final report/analysis
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
                
                # Save markdown report to file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_filename = f"VERIFICATION_REPORT_{subject_data['name'].replace(' ', '_')}_{timestamp}.md"
                report_path = Path(__file__).parent / report_filename
                
                try:
                    with open(report_path, 'w', encoding='utf-8') as f:
                        f.write(final_text)
                    
                    print(f"\n✅ Markdown report saved: {report_filename}")
                    
                    await broadcast({
                        'type': 'report_saved',
                        'filename': report_filename,
                        'path': str(report_path)
                    })
                except Exception as e:
                    print(f"\n⚠️  Could not save report: {e}")
                
                # Try to extract JSON from response (for dashboard display)
                try:
                    json_match = re.search(r'\{[\s\S]*"verification_status"[\s\S]*\}', final_text)
                    if json_match:
                        analysis = json.loads(json_match.group(0))
                    else:
                        # Extract confidence from markdown if present
                        confidence_match = re.search(r'\*\*Confidence:\*\*.*?(\d+)%', final_text)
                        confidence = int(confidence_match.group(1)) if confidence_match else 50
                        
                        analysis = {
                            "verification_status": "REPORT_GENERATED",
                            "confidence_score": confidence,
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

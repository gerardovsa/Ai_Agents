"""
Professional Verification System - Integrated into Main Flask App
=================================================================

Interactive AI-powered verification with Computer Use
Accessible at /verification-dashboard

INTEGRATION:
- Uses main Flask SocketIO server
- Separate namespace: /ws/verification
- Serves dashboard from UI/modules_external/professional-verification/TESTS/

CREATED: December 19, 2025
"""

import os
import sys
import asyncio
import requests
from pathlib import Path
from datetime import datetime
import json

# Get AI_agents root
ai_agents_root = Path(__file__).parent.parent.parent
verification_path = ai_agents_root / 'UI' / 'modules_external' / 'professional-verification' / 'TESTS'

# GitHub API configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_API_BASE = 'https://api.github.com'


def search_github_users(name):
    """
    Search GitHub users API by name
    Returns user data if found, None otherwise
    """
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured", "found": False}
    
    try:
        url = f"{GITHUB_API_BASE}/search/users"
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        params = {'q': name, 'per_page': 5}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('total_count', 0) > 0:
                # Get detailed info for top result
                user = data['items'][0]
                user_url = user['url']
                
                user_response = requests.get(user_url, headers=headers, timeout=10)
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    return {
                        "found": True,
                        "username": user_data.get('login'),
                        "name": user_data.get('name'),
                        "url": user_data.get('html_url'),
                        "bio": user_data.get('bio'),
                        "company": user_data.get('company'),
                        "location": user_data.get('location'),
                        "email": user_data.get('email'),
                        "blog": user_data.get('blog'),
                        "twitter": user_data.get('twitter_username'),
                        "public_repos": user_data.get('public_repos'),
                        "followers": user_data.get('followers'),
                        "following": user_data.get('following'),
                        "created_at": user_data.get('created_at'),
                        "total_matches": data.get('total_count')
                    }
            return {"found": False, "message": "No GitHub profiles found"}
        else:
            return {"error": f"GitHub API returned {response.status_code}", "found": False}
    
    except Exception as e:
        return {"error": str(e), "found": False}


def register_verification_routes(app, socketio):
    """
    Register verification dashboard routes and WebSocket handlers
    
    Args:
        app: Flask app instance
        socketio: Flask-SocketIO instance
    """
    
    print(f"\n{'='*80}")
    print("🔍 REGISTERING PROFESSIONAL VERIFICATION SYSTEM")
    print(f"{'='*80}")
    
    from flask import send_from_directory, render_template_string
    
    # ============================================================================
    # HTTP ROUTES - Dashboard Access
    # ============================================================================
    
    @app.route('/verification-dashboard')
    def verification_dashboard():
        """Serve the verification dashboard HTML"""
        try:
            dashboard_file = verification_path / 'verification_dashboard.html'
            if dashboard_file.exists():
                return send_from_directory(str(verification_path), 'verification_dashboard.html')
            else:
                return f"<h1>Error: Dashboard not found</h1><p>{dashboard_file}</p>", 404
        except Exception as e:
            return f"<h1>Error loading dashboard</h1><p>{str(e)}</p>", 500
    
    @app.route('/verification-assets/<path:filename>')
    def verification_assets(filename):
        """Serve verification assets (if needed)"""
        return send_from_directory(str(verification_path), filename)
    
    # ============================================================================
    # WEBSOCKET HANDLERS - Interactive Verification
    # ============================================================================
    
    # Store active verification sessions
    active_verifications = {}
    
    @socketio.on('connect', namespace='/ws/verification')
    def handle_verification_connect():
        """Handle client connection to verification namespace"""
        from flask_socketio import emit
        from flask import request
        
        sid = request.sid
        print(f"✅ [VERIFICATION] Client connected: {sid}")
        
        emit('connected', {
            'message': 'Connected to verification server',
            'sid': sid,
            'timestamp': datetime.now().isoformat()
        })
    
    @socketio.on('disconnect', namespace='/ws/verification')
    def handle_verification_disconnect(reason=None):
        """Handle client disconnection"""
        from flask import request
        
        sid = request.sid
        print(f"❌ [VERIFICATION] Client disconnected: {sid} (reason: {reason})")
        
        # Clean up any active verification for this session
        if sid in active_verifications:
            del active_verifications[sid]
    
    @socketio.on('start_verification', namespace='/ws/verification')
    def handle_start_verification(data):
        """
        Start verification process
        
        Expected data:
            {
                "subject_text": "Free-form text about subject to verify"
            }
        """
        from flask_socketio import emit
        from flask import request
        
        sid = request.sid
        subject_text = data.get('subject_text', '')
        
        print(f"\n🔍 [VERIFICATION] Starting verification for session {sid}")
        print(f"   Subject text length: {len(subject_text)} characters")
        
        if not subject_text or len(subject_text) < 10:
            emit('error', {
                'message': 'Invalid subject text (minimum 10 characters required)'
            }, namespace='/ws/verification')
            return
        
        # Store verification session
        active_verifications[sid] = {
            'subject_text': subject_text,
            'started_at': datetime.now().isoformat(),
            'status': 'running'
        }
        
        # Run verification in background thread
        socketio.start_background_task(
            run_verification_task,
            sid,
            subject_text
        )
    
    @socketio.on('chat_message', namespace='/ws/verification')
    def handle_chat_message(data):
        """
        Handle interactive chat message during verification
        
        Expected data:
            {
                "message": "User message text",
                "conversation_history": [...]
            }
        """
        from flask_socketio import emit
        from flask import request
        
        sid = request.sid
        message = data.get('message', '')
        conversation_history = data.get('conversation_history', [])
        
        print(f"💬 [VERIFICATION] Chat message from {sid}: {message[:80]}...")
        
        # Run chat response in background
        socketio.start_background_task(
            handle_chat_task,
            sid,
            message,
            conversation_history
        )
    
    # ============================================================================
    # BACKGROUND TASKS - AI Verification & Chat
    # ============================================================================
    
    def run_verification_task(sid, subject_text):
        """
        Background task to run comprehensive verification
        Uses Anthropic Claude with Computer Use (bash_20250124)
        """
        try:
            # Import here to avoid circular imports
            from anthropic import Anthropic
            
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                socketio.emit('error', {
                    'message': 'ANTHROPIC_API_KEY not found in environment'
                }, namespace='/ws/verification', room=sid)
                return
            
            client = Anthropic(api_key=api_key)
            
            # Build comprehensive verification prompt
            verification_prompt = build_verification_prompt(subject_text)
            
            messages = [{
                "role": "user",
                "content": verification_prompt
            }]
            
            iteration = 0
            max_iterations = 100
            total_tokens = 0
            all_commands = []
            
            while iteration < max_iterations:
                iteration += 1
                
                print(f"   🔄 Iteration {iteration}")
                
                # Send iteration update
                socketio.emit('iteration', {
                    'iteration': iteration,
                    'stop_reason': 'processing'
                }, namespace='/ws/verification', room=sid)
                
                # Call Claude with bash tools
                response = client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=8000,
                    temperature=0.3,
                    tools=[{"type": "bash_20250124", "name": "bash"}],
                    messages=messages
                )
                
                total_tokens += response.usage.input_tokens + response.usage.output_tokens
                
                # Send token update
                socketio.emit('tokens', {
                    'tokens': total_tokens
                }, namespace='/ws/verification', room=sid)
                
                # Process response
                if response.stop_reason == 'end_turn':
                    # Verification complete
                    final_text = ""
                    for block in response.content:
                        if hasattr(block, 'text'):
                            final_text += block.text
                    
                    # Save markdown report
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    report_filename = f"VERIFICATION_REPORT_{timestamp}.md"
                    report_path = verification_path / report_filename
                    
                    with open(report_path, 'w', encoding='utf-8') as f:
                        f.write(final_text)
                    
                    print(f"   ✅ Report saved: {report_filename}")
                    
                    # Send results
                    socketio.emit('results', {
                        'text': final_text,
                        'total_iterations': iteration,
                        'total_commands': len(all_commands),
                        'total_tokens': total_tokens,
                        'report_filename': report_filename
                    }, namespace='/ws/verification', room=sid)
                    
                    break
                
                elif response.stop_reason == 'tool_use':
                    # Process tool calls
                    tool_results = []
                    
                    for block in response.content:
                        if hasattr(block, 'text'):
                            # Send reasoning
                            socketio.emit('reasoning', {
                                'text': block.text,
                                'iteration': iteration
                            }, namespace='/ws/verification', room=sid)
                        
                        elif block.type == 'tool_use' and block.name == 'bash':
                            # Execute bash command
                            command = block.input.get('command', '')
                            
                            print(f"   💻 Executing: {command[:80]}...")
                            
                            all_commands.append(command)
                            
                            # Send command count update
                            socketio.emit('command_count', {
                                'count': len(all_commands)
                            }, namespace='/ws/verification', room=sid)
                            
                            # Execute command
                            import subprocess
                            try:
                                proc = subprocess.run(
                                    command,
                                    shell=True,
                                    capture_output=True,
                                    text=True,
                                    timeout=30,
                                    encoding='utf-8',
                                    errors='replace'  # Replace unicode errors instead of crashing
                                )
                                
                                output = proc.stdout if proc.stdout else ""
                                if proc.stderr:
                                    output += f"\n[STDERR]: {proc.stderr}"
                                
                                # If no output at all, note it
                                if not output or output.strip() == "":
                                    output = "(Command executed successfully but produced no output)"
                                
                                # Limit output size
                                if len(output) > 10000:
                                    output = output[:10000] + "\n... (output truncated)"
                                
                            except subprocess.TimeoutExpired:
                                output = f"Command timed out after 30 seconds"
                            except UnicodeDecodeError as e:
                                output = f"Unicode decoding error: {str(e)}"
                            except Exception as e:
                                output = f"Error executing command: {str(e)}"
                            
                            # Send command result
                            socketio.emit('command', {
                                'command': command,
                                'output': output
                            }, namespace='/ws/verification', room=sid)
                            
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
                    socketio.emit('error', {
                        'message': f'Unexpected stop reason: {response.stop_reason}'
                    }, namespace='/ws/verification', room=sid)
                    break
            
            if iteration >= max_iterations:
                socketio.emit('error', {
                    'message': f'Max iterations ({max_iterations}) reached'
                }, namespace='/ws/verification', room=sid)
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
            socketio.emit('error', {
                'message': str(e)
            }, namespace='/ws/verification', room=sid)
    
    def handle_chat_task(sid, message, conversation_history):
        """
        Handle chat message - AI responds to user questions
        Automatically detects when to start verification
        """
        try:
            from anthropic import Anthropic
            
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                socketio.emit('error', {
                    'message': 'ANTHROPIC_API_KEY not found'
                }, namespace='/ws/verification', room=sid)
                return
            
            client = Anthropic(api_key=api_key)
            
            # Check if this is a verification request (has enough info to verify someone)
            verification_keywords = [
                'verify', 'investigate', 'check', 'background', 'look into', 'research',
                'requesting', 'access', 'account', 'permission', 'credential', 'login',
                'analyze', 'deep dive', 'comprehensive', 'full', 'extensive', 'detailed'
            ]
            is_verification_request = False
            if len(message) > 30 and any(keyword in message.lower() for keyword in verification_keywords):
                is_verification_request = True
            
            # If it looks like a verification request, start verification WITH COMPUTER USE
            if is_verification_request and sid not in active_verifications:
                print(f"\n{'='*80}")
                print(f"🔍 DETECTED VERIFICATION REQUEST")
                print(f"   Session: {sid}")
                print(f"   Message length: {len(message)} characters")
                print(f"   Starting Computer Use investigation...")
                print(f"{'='*80}\n")
                
                # Store verification session
                active_verifications[sid] = {
                    'subject_text': message,
                    'started_at': datetime.now().isoformat(),
                    'status': 'running'
                }
                
                # Send initial response
                socketio.emit('chat_response', {
                    'message': '🔍 **Starting comprehensive investigation with Computer Use tools...**\n\nI\'ll execute bash commands to verify the information. Watch the panels for real-time updates!'
                }, namespace='/ws/verification', room=sid)
                
                # Start verification in background WITH COMPUTER USE
                socketio.start_background_task(
                    run_verification_task,
                    sid,
                    message
                )
                return
            
            # Otherwise, handle as normal chat
            # Build message history
            messages = []
            
            # Add system prompt for chat mode
            if len(conversation_history) == 0:
                system_context = """You are a professional verification assistant. You can:

1. **Chat normally** - Answer questions, have conversations
2. **Start verification** - When user provides subject information

If the user greets you or asks general questions, respond naturally.
If they provide information about someone to verify (name, email, company, context), offer to start an investigation.

Be helpful, professional, and conversational."""
                
                messages.append({
                    "role": "user",
                    "content": system_context + "\n\nUser: " + message
                })
            else:
                # Continue existing conversation
                for msg in conversation_history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                
                messages.append({
                    "role": "user",
                    "content": message
                })
            
            # Get AI response
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                temperature=0.7,
                messages=messages
            )
            
            ai_response = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    ai_response += block.text
            
            # Send response
            socketio.emit('chat_response', {
                'message': ai_response
            }, namespace='/ws/verification', room=sid)
            
            print(f"   ✅ Sent chat response: {ai_response[:80]}...")
        
        except Exception as e:
            print(f"   ❌ Chat error: {e}")
            socketio.emit('error', {
                'message': f'Chat error: {str(e)}'
            }, namespace='/ws/verification', room=sid)
    
    def build_verification_prompt(subject_text):
        """Build comprehensive verification prompt"""
        
        prompt = f"""
You are a PROFESSIONAL VERIFICATION SPECIALIST conducting a COMPREHENSIVE RISK ASSESSMENT.

# SYSTEM ENVIRONMENT
**CRITICAL:** You are running on **WINDOWS** (not Linux). Use Windows-compatible commands:
- ✅ Use `powershell` commands when needed
- ✅ Paths: Use `C:\\Temp` or `%TEMP%` (NOT `/tmp`)
- ✅ Use `curl.exe` (Windows has native curl)
- ✅ Use `nslookup` (Windows native)
- ❌ DO NOT use: pwd, head, tail, grep, ls, cd (unless prefixed with powershell)
- ✅ For text processing: Use PowerShell cmdlets or redirect to files

# SUBJECT INFORMATION

{subject_text}

# YOUR MISSION

Conduct a thorough investigation into the individuals/organizations mentioned. Execute comprehensive checks using Windows-compatible bash commands.

## VERIFICATION CHECKLIST

Execute these WINDOWS-COMPATIBLE commands. Handle errors gracefully - if a command fails, note it and move on.

### 1. Domain & Infrastructure Checks
```bash
# Domain resolution (use nslookup - native Windows command)
nslookup scatechnology.ai
nslookup isb.eco

# Website headers (use curl - check hosting, SSL, age)
curl -I https://scatechnology.ai 2>&1
curl -I https://isb.eco 2>&1
curl -I https://www.isb.eco 2>&1

# Check website last modified dates
curl -I https://scatechnology.ai 2>&1 | findstr /i "last-modified date server"
curl -I https://isb.eco 2>&1 | findstr /i "last-modified date server"

# SSL Certificate details (Python one-liner for Windows)
python -c "import ssl,socket;c=ssl.create_default_context();s=socket.create_connection(('scatechnology.ai',443));ss=c.wrap_socket(s,server_hostname='scatechnology.ai');cert=ss.getpeercert();print('Issuer:',dict(x[0] for x in cert['issuer']));print('Subject:',dict(x[0] for x in cert['subject']));print('Valid from:',cert['notBefore']);print('Valid until:',cert['notAfter']);ss.close();s.close()"

python -c "import ssl,socket;c=ssl.create_default_context();s=socket.create_connection(('isb.eco',443));ss=c.wrap_socket(s,server_hostname='isb.eco');cert=ss.getpeercert();print('Issuer:',dict(x[0] for x in cert['issuer']));print('Subject:',dict(x[0] for x in cert['subject']));print('Valid from:',cert['notBefore']);print('Valid until:',cert['notAfter']);ss.close();s.close()"

# Website content analysis (look for mentions of people/company)
python -c "import requests;r=requests.get('https://scatechnology.ai',timeout=10);content=r.text.lower();print('dutton' in content,'casey' in content,'greg' in content)"

python -c "import requests;r=requests.get('https://isb.eco',timeout=10);content=r.text.lower();print('dutton' in content,'gregory' in content)"
```

### 2. Web Archive Historical Check (Domain Age)
```bash
# Check domain history via Wayback Machine API
curl -s "http://archive.org/wayback/available?url=scatechnology.ai" 2>&1

curl -s "http://archive.org/wayback/available?url=isb.eco" 2>&1
```

### 3. GitHub Profile Search (OFFICIAL API - RELIABLE)
```bash
# Search GitHub for developer profiles (uses official GitHub API with authentication)
# Gregory Dutton search
python -c "import requests,os,json;token=os.getenv('GITHUB_TOKEN');h={{'Authorization':'token '+token,'Accept':'application/vnd.github.v3+json'}} if token else {{}};r=requests.get('https://api.github.com/search/users',headers=h,params={{'q':'Gregory Dutton','per_page':5}},timeout=10);d=r.json();print('Found:',d.get('total_count',0),'profiles');items=d.get('items',[]);[print(i['login'],i['html_url']) for i in items[:3]]"

# Casey Dutton search
python -c "import requests,os,json;token=os.getenv('GITHUB_TOKEN');h={{'Authorization':'token '+token,'Accept':'application/vnd.github.v3+json'}} if token else {{}};r=requests.get('https://api.github.com/search/users',headers=h,params={{'q':'Casey Dutton','per_page':5}},timeout=10);d=r.json();print('Found:',d.get('total_count',0),'profiles');items=d.get('items',[]);[print(i['login'],i['html_url']) for i in items[:3]]"

# Search by company name
python -c "import requests,os;token=os.getenv('GITHUB_TOKEN');h={{'Authorization':'token '+token}} if token else {{}};r=requests.get('https://api.github.com/search/users',headers=h,params={{'q':'scatechnology','per_page':5}},timeout=10);d=r.json();print('Found:',d.get('total_count',0),'users with scatechnology');[print(i['login'],i['html_url']) for i in d.get('items',[])]"

# If profiles found, get detailed info (replace USERNAME with actual username from above)
# python -c "import requests,os;token=os.getenv('GITHUB_TOKEN');h={{'Authorization':'token '+token}} if token else {{}};r=requests.get('https://api.github.com/users/USERNAME',headers=h,timeout=10);d=r.json();print('Name:',d.get('name'));print('Company:',d.get('company'));print('Location:',d.get('location'));print('Email:',d.get('email'));print('Bio:',d.get('bio'));print('Created:',d.get('created_at'));print('Repos:',d.get('public_repos'));print('Followers:',d.get('followers'))"
```

### 4. Search Engine Reputation Checks
```bash
# Note: Google blocks automated searches, so use alternative methods
# Search DuckDuckGo for mentions (less restrictive)
curl -s "https://html.duckduckgo.com/html/?q=scatechnology.ai+reviews" 2>&1 | findstr /i "scatechnology"

curl -s "https://html.duckduckgo.com/html/?q=Gregory+Dutton+scatechnology" 2>&1 | findstr /i "dutton"

curl -s "https://html.duckduckgo.com/html/?q=scatechnology.ai+scam+fraud" 2>&1 | findstr /i "scam fraud"
```

### 4. WHOIS/Domain Registration (Via Web Services)
```bash
# WHOIS lookup via web interface (scrape for registration date)
curl -s "https://www.whois.com/whois/scatechnology.ai" 2>&1 | findstr /i "created registered updated"

curl -s "https://www.whois.com/whois/isb.eco" 2>&1 | findstr /i "created registered updated"
```

### 5. IP Address & Hosting Provider
```bash
# Ping to get IP addresses
ping -n 1 scatechnology.ai 2>&1 | findstr /i "reply bytes"

ping -n 1 isb.eco 2>&1 | findstr /i "reply bytes"

# Reverse IP lookup (find other sites on same server - suspicious if many)
curl -s "https://api.hackertarget.com/reverseiplookup/?q=216.198.79.1" 2>&1
```

### 6. Email Domain Validation
```bash
# Check if email domains actually work (MX records)
nslookup -type=MX scatechnology.ai
nslookup -type=MX isb.eco

# Check if email address format is valid
python -c "import re;email='gregory.dutton@isb.eco';print('Valid:',bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',email)))"
```

**IMPORTANT COMMAND HANDLING:**
- If a command fails with an error, LOG THE ERROR and continue
- Some commands may timeout - that's valuable information (site slow/unresponsive)
- Unicode errors in output - use Python with proper encoding
- If a command returns no data, that's also a finding (site doesn't exist, etc.)
- DO NOT use: pwd, head, tail, cd /tmp, date (without proper Windows syntax)

## CRITICAL RED FLAGS TO IDENTIFY

1. **Domain Age**: Recently registered (<6 months) = HIGH RISK
2. **Hosting**: Cheap hosting (Wix, Vercel, shared) vs professional = MEDIUM RISK
3. **Business Registration**: No ABN found = CRITICAL RISK
4. **Web Presence**: No search results, reviews = HIGH RISK
5. **SSL Certificate**: Self-signed or very recent = MEDIUM RISK
6. **Website Content**: Template-based, minimal content = HIGH RISK
7. **Email Domain Mismatch**: Using isb.eco for SCA Technology = HIGH RISK
8. **Inconsistencies**: Claims don't match evidence = CRITICAL RISK

## OUTPUT FORMAT

Generate a comprehensive markdown report with:

1. **🚨 EXECUTIVE SUMMARY**
   - Overall Risk Level (CRITICAL/HIGH/MEDIUM/LOW)
   - Key Findings (3-5 bullet points)
   - Recommendation (PROCEED/ADDITIONAL VERIFICATION/REJECT)

2. **🔍 TECHNICAL INFRASTRUCTURE ANALYSIS**
   - Domain details (age, registrar, hosting)
   - Website analysis (platform, content quality)
   - SSL certificate details
   - IP addresses and DNS records

3. **📊 RISK ASSESSMENT**
   - Risk Score (0-100)
   - Individual risk factors with severity
   - Red flags identified

4. **⚠️ FRAUD INDICATORS**
   - Suspicious patterns found
   - Inconsistencies detected
   - Missing information

5. **🛡️ MITIGATION STRATEGIES**
   - Immediate actions required
   - Additional verification steps
   - Contact points for reporting

6. **📎 APPENDIX - COMMAND OUTPUTS**
   - All raw command outputs
   - Technical evidence

**EXECUTE ALL COMMANDS AND BASE YOUR ANALYSIS ON ACTUAL DATA, NOT ASSUMPTIONS.**

BEGIN COMPREHENSIVE VERIFICATION NOW.
"""
        
        return prompt
    
    # ============================================================================
    # COMPLETION MESSAGE
    # ============================================================================
    
    print(f"✅ Verification system registered")
    print(f"   Dashboard: http://localhost:5001/verification-dashboard")
    print(f"   WebSocket: ws://localhost:5001/ws/verification")
    print(f"{'='*80}\n")

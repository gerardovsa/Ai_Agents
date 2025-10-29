# 🧠 Context-Aware AI Integration Guide

## Overview

This guide shows how to integrate the Context-Aware AI system into your agent routes to give AI:
- **User profile awareness** (name, role, preferences)
- **Temporal awareness** (time of day, timezone, work hours)
- **Geographic awareness** (location from IP)
- **Conversation memory** (past discussions)
- **Event-driven activation** (proactive AI)
- **Project tracking** (links to past work)

## ✅ What's Already Implemented

### Core Systems (Complete)
1. **Context Engine** - `AI_infrastructure/core/context_engine.py` ✅
2. **Event Trigger System** - `AI_infrastructure/core/event_triggers.py` ✅
3. **Context-Aware AI Integration** - `AI_infrastructure/core/context_aware_ai.py` ✅
4. **AI Personal Tasks** - `google_workspace/ai_personal_tasks.py` ✅

### What You Get
- Rich user context (profile, timezone, preferences)
- Time-aware greetings ("Good morning!", "It's evening for you")
- Conversation memory (AI remembers past discussions)
- Event triggers (daily briefings, deadline warnings, weekly reviews)
- Project links (AI tracks work it has done for you)
- Proactive AI (activates based on events, not just user input)

## 🚀 Integration Steps

### Step 1: Import Context-Aware AI into agent_routes.py

Add this import at the top of `AI_infrastructure/routes/agent_routes.py`:

```python
# Add after existing imports
from core.context_aware_ai import enhance_system_prompt_with_context
```

### Step 2: Enhance System Prompts with Context

**For Main Agent Endpoint (around line 351):**

**BEFORE:**
```python
system_prompt = """You are an AI assistant with direct access to 296+ business tools across 20+ platforms.
...
[rest of system prompt]
"""
```

**AFTER:**
```python
# Base system prompt (keep existing content)
base_system_prompt = """You are an AI assistant with direct access to 296+ business tools across 20+ platforms.
...
[rest of system prompt]
"""

# Get user_id from authentication
user_id = request.headers.get('X-User-ID', 'default_user')
ip_address = request.remote_addr

# Enhance with context awareness
system_prompt = enhance_system_prompt_with_context(
    user_id=user_id,
    base_prompt=base_system_prompt,
    ip_address=ip_address
)
```

### Step 3: Apply to All Agent Endpoints

Apply the same pattern to all endpoints that use system prompts:

- **Main agent endpoint** (line ~351) ✅
- **Streaming agent endpoint** (line ~661) ✅  
- **Simple agent endpoint** (line ~907) ✅
- **Multi-agent endpoint** (line ~978) ✅

### Step 4: Record Conversations (Optional but Recommended)

Add conversation recording at the end of agent endpoints:

```python
from core.context_aware_ai import get_context_aware_ai

# After AI completes conversation
context_ai = get_context_aware_ai()
context_ai.record_conversation(
    user_id=user_id,
    conversation_summary="User asked about Gmail bulk sending",
    topics=['gmail', 'bulk_operations', 'email'],
    tools_used=['gmail_smart_bulk_send_personalized'],
    outcome="Successfully implemented bulk email feature"
)
```

### Step 5: Record Projects (Optional)

When AI creates documents, sheets, etc., record them:

```python
# After AI creates Google Doc/Sheet/etc.
context_ai.record_project(
    user_id=user_id,
    project_name="Email Marketing Campaign",
    description="Bulk email system with personalized templates",
    links=[
        'https://docs.google.com/document/d/abc123',
        'https://sheets.google.com/spreadsheets/d/xyz789'
    ],
    tags=['email', 'marketing', 'automation']
)
```

## 📋 Complete Integration Example

Here's a complete example for the main agent endpoint:

```python
@agent_bp.route('/v2/agent', methods=['POST'])
@require_auth
def agent_endpoint_v2():
    """Main agent endpoint with context awareness"""
    try:
        # Get request data
        data = request.json
        user_message = data.get('message', '')
        
        # Get user context
        user_id = request.headers.get('X-User-ID', 'default_user')
        ip_address = request.remote_addr
        
        # Base system prompt
        base_system_prompt = """You are an AI assistant with direct access to 296+ business tools across 20+ platforms.

**INTERLEAVED THINKING & MULTI-TOOL USAGE:**
You can use MULTIPLE tools in a single conversation, think between tool calls, and provide updates to the user...

[rest of existing system prompt - keep everything]
"""
        
        # 🌟 ENHANCE WITH CONTEXT AWARENESS
        system_prompt = enhance_system_prompt_with_context(
            user_id=user_id,
            base_prompt=base_system_prompt,
            ip_address=ip_address
        )
        
        # Continue with existing AI call...
        ai_client = get_ai_client()
        response = ai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            tools=tool_definitions,
            tool_choice="auto"
        )
        
        # ... rest of existing code ...
        
        # 🌟 OPTIONAL: Record conversation
        from core.context_aware_ai import get_context_aware_ai
        context_ai = get_context_aware_ai()
        
        # Extract tools used from response
        tools_used = []
        topics = []
        # ... extract from response ...
        
        context_ai.record_conversation(
            user_id=user_id,
            conversation_summary=user_message[:100],
            topics=topics,
            tools_used=tools_used,
            outcome="Successfully handled user request"
        )
        
        return success_response(data=response_data)
        
    except Exception as e:
        return error_response(str(e))
```

## 🧪 Testing the Integration

### Test 1: Basic Context Awareness

**Start the server:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

**Test with CHAT command:**
```powershell
CHAT Hello! What time is it for me?
```

**Expected AI Response:**
```
Good morning! Based on your timezone (America/New_York), it's currently 
9:30 AM on Monday, October 28, 2025. You're in your work hours. How can I help you today?
```

### Test 2: Memory Continuity

**First conversation:**
```powershell
CHAT Create a Google Doc about project planning
```

**Second conversation (later):**
```powershell
CHAT What did we work on last time?
```

**Expected AI Response:**
```
Last time we spoke (on 2025-10-28), we created a Google Doc about project planning. 
Would you like me to continue working on that project or start something new?
```

### Test 3: AI Task Persistence

**Test AI remembering across sessions:**
```powershell
CHAT Remember to send follow-up email about meeting next week
```

**AI creates task, then restart server:**
```powershell
BISTOP
BISTART
```

**New conversation:**
```powershell
CHAT What do I have pending?
```

**Expected AI Response:**
```
I have 1 pending task:
🔴 Send follow-up email about meeting
Due: 2025-11-05

Would you like me to work on this now?
```

## 🎯 What Users Will Experience

### Before Context-Aware System:
```
User: Hello
AI: Hello! How can I help you today?
```

### After Context-Aware System:
```
User: Hello
AI: Good morning, John! It's Monday morning. I see you have 2 high-priority 
tasks from our work on Friday about the Gmail bulk sending feature. 
You also have a deadline in 3 days for the Dashboard project. 
Would you like me to help prioritize today's work?
```

## ⚙️ Configuration Options

### Set Up User Automations

```python
from core.context_aware_ai import get_context_aware_ai

context_ai = get_context_aware_ai()

# Set up daily briefings and weekly reviews
context_ai.setup_user_automations(
    user_id='user_123',
    preferences={
        'daily_briefing': True,
        'briefing_time_hour': 8,  # 8am
        'weekly_review': True,
        'review_day': 4,  # Friday
        'review_time_hour': 17,  # 5pm
        'deadline_warnings': True,
        'warning_hours': 24  # 24 hours before deadline
    }
)
```

### Create User Profile

```python
from core.context_engine import get_context_engine

engine = get_context_engine()

# Create/update user profile
user_profile = {
    'name': 'John Doe',
    'role': 'developer',
    'timezone': 'America/New_York',
    'language': 'en',
    'preferences': {
        'communication_style': 'professional',  # or 'casual', 'formal'
        'detail_level': 'comprehensive',  # or 'concise', 'detailed'
        'preferred_tools': ['gmail', 'google_docs', 'google_tasks'],
        'notification_hours': {'start': 9, 'end': 18},
        'work_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    }
}

engine.user_profiles['user_123'] = user_profile
```

## 🔮 Advanced: Event-Driven AI Activation

### Set Up Proactive AI (Background Service)

Create `AI_infrastructure/services/trigger_monitor.py`:

```python
"""
Background service that monitors event triggers and proactively activates AI
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from AI_infrastructure.core.event_triggers import get_event_trigger_system

async def activate_ai_conversation(trigger):
    """
    Called when trigger fires - starts AI conversation with user
    """
    from AI_infrastructure.core.event_triggers import EventTriggerSystem
    
    user_id = trigger.user_id
    prompt = EventTriggerSystem().generate_ai_activation_prompt(trigger)
    
    print(f"🤖 AI Proactively Activated for user {user_id}")
    print(f"📋 Trigger: {trigger.trigger_type.value}")
    print(f"💬 Prompt: {prompt[:100]}...")
    
    # TODO: Create AI conversation in database
    # TODO: Send notification to user (email, push, etc.)
    # TODO: Optionally start AI response generation

async def start_monitor():
    """Start background monitoring"""
    system = get_event_trigger_system()
    
    # Register callback
    system.register_callback(activate_ai_conversation)
    
    print("🔄 Event trigger monitor started")
    print("📡 Monitoring for events every 60 seconds")
    
    # Run monitoring loop
    await system.run_monitor_loop(check_interval_seconds=60)

if __name__ == '__main__':
    print("🚀 Starting Event Trigger Monitor...")
    asyncio.run(start_monitor())
```

**Run background service:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python AI_infrastructure/services/trigger_monitor.py
```

## 📊 Benefits Summary

| Feature | Before | After |
|---------|--------|-------|
| **User Awareness** | No context | AI knows user name, role, preferences |
| **Time Awareness** | Generic greetings | "Good morning!", time-appropriate responses |
| **Memory** | Forgets between sessions | Remembers past conversations |
| **Project Tracking** | No links | AI tracks work it created for you |
| **Proactivity** | Purely reactive | Daily briefings, deadline warnings |
| **Continuity** | Starts fresh each time | "Last time we worked on..." |

## 🔍 Debugging

### Check Context Engine Status

```python
from core.context_engine import get_context_engine

engine = get_context_engine()

# Get full context for user
context = engine.get_full_context('user_123', '192.168.1.1')
print(json.dumps(context, indent=2))
```

### Check Event Triggers

```python
from core.event_triggers import get_event_trigger_system

system = get_event_trigger_system()

# List user's triggers
triggers = system.get_user_triggers('user_123')
print(f"User has {len(triggers)} active triggers")

for trigger in triggers:
    print(f"- {trigger.trigger_type.value} at {trigger.scheduled_time}")
```

### Test Context-Aware Prompt Generation

```python
from core.context_aware_ai import enhance_system_prompt_with_context

enhanced = enhance_system_prompt_with_context(
    user_id='user_123',
    base_prompt='You are an AI assistant.',
    ip_address='192.168.1.1'
)

print(enhanced)
```

## 📚 Next Steps

1. ✅ **Integrate into agent_routes.py** (follow Step 1-3)
2. ✅ **Test basic context awareness** (restart server, test with CHAT)
3. ⏳ **Create database schema** for persistent user profiles (PostgreSQL/MongoDB)
4. ⏳ **Set up background trigger monitor** for proactive AI
5. ⏳ **Implement IP geolocation** (MaxMind, ipapi.co)
6. ⏳ **Add conversation recording** to track topics/tools used
7. ⏳ **Create user profile management UI** (optional)

## 🎉 Impact

With this integration, your AI becomes:
- **Personalized** - Knows who users are and their preferences
- **Intelligent** - Understands time, location, context
- **Persistent** - Remembers past work and continues projects
- **Proactive** - Activates based on events, not just user input
- **Continuous** - Feels like same AI across sessions, not new each time

---

**Last Updated:** October 28, 2025  
**Status:** ✅ Ready for Integration  
**Files Created:** 3 core systems + this guide

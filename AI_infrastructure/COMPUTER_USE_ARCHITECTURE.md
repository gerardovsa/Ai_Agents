# Computer Use Architecture - Platform-Wide Infrastructure

## 🎯 Design Philosophy

**Generic, Task-Agnostic Browser Automation**

The Computer Use infrastructure is designed as a **platform-wide service** that ANY module can use for ANY web-based task. It is NOT tied to verification - it's universal automation.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Platform Layer                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Computer Use Executor (SINGLETON)                   │   │
│  │ AI_infrastructure/core/computer_use_executor.py    │   │
│  │                                                     │   │
│  │ - get_browser_container()                          │   │
│  │ - take_screenshot()                                │   │
│  │ - move_mouse() / click_mouse()                     │   │
│  │ - type_text() / press_key()                        │   │
│  │ - execute_bash()                                   │   │
│  │ - execute_computer_action() ← Routes Claude cmds   │   │
│  └────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Generic Computer Use Tools (Tool Registry V3)      │   │
│  │ AI_infrastructure/tools/computer_use_tools.py     │   │
│  │                                                     │   │
│  │ 1. computer_use_browse_and_extract()              │   │
│  │    - Universal web scraping/extraction             │   │
│  │    - Competitor research                           │   │
│  │    - Quote calculators                             │   │
│  │    - Product data                                  │   │
│  │    - ANY website interaction                       │   │
│  │                                                     │   │
│  │ 2. computer_use_fill_form()                       │   │
│  │    - Automatic form filling                        │   │
│  │    - Contact forms                                 │   │
│  │    - Quote requests                                │   │
│  │    - Account creation                              │   │
│  │                                                     │   │
│  │ 3. computer_use_compare_competitors()             │   │
│  │    - Multi-site comparison                         │   │
│  │    - Side-by-side analysis                         │   │
│  │    - Pricing research                              │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Docker Layer                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Browser Container (professional-verification-      │   │
│  │                   browser:latest)                  │   │
│  │ docker/computer-use/Dockerfile                     │   │
│  │                                                     │   │
│  │ - Ubuntu 22.04                                     │   │
│  │ - Xvfb :1 (virtual display 1920x1080)             │   │
│  │ - x11vnc (VNC server on port 5900)                │   │
│  │ - fluxbox (window manager)                         │   │
│  │ - Chromium + Firefox browsers                      │   │
│  │ - xdotool (mouse/keyboard automation)             │   │
│  │ - scrot (screenshots)                              │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              Anthropic Computer Use API                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Claude Sonnet 4 with computer_20241022 tool:             │
│                                                             │
│  Actions:                                                   │
│  - screenshot → Captures display                           │
│  - mouse_move → Move cursor                                │
│  - left_click → Click at position                          │
│  - type → Type text                                        │
│  - key → Press special keys                                │
│                                                             │
│  Iterative Loop:                                           │
│  Claude → tool_use → Execute → Result → Claude...         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 Module Usage Examples

### Professional Verification Module

```python
# Uses generic platform tools
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# LinkedIn verification
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Navigate to LinkedIn, search for "John Doe at Google", extract profile data',
    _user_id='user123'
)

# Medical license verification
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Navigate to AHPRA registry, search medical registration AHP123456, extract status',
    _user_id='user123'
)
```

---

### Competitor Research Module (NEW - Example)

```python
# Same tools, different use case
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Navigate to vistaprint.com quote calculator, configure 1000 business cards 4-color both sides, extract final price',
    return_format='json',
    _user_id='user123'
)

# Multi-competitor comparison
result = registry.execute_tool(
    'computer_use_compare_competitors',
    competitors=['vistaprint.com', 'moo.com', 'printful.com'],
    comparison_task='Extract pricing for 1000 business cards, 4-color both sides',
    _user_id='user123'
)
```

---

### Product Research Module (NEW - Example)

```python
# E-commerce scraping
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Go to amazon.com, search for "thermal label printer", extract top 5 product names, prices, ratings',
    return_format='json',
    _user_id='user123'
)
```

---

### Testing/QA Module (NEW - Example)

```python
# UI/UX testing
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Navigate to mycompany.com, click "Get Quote", fill form with test data, count number of clicks to checkout, extract total time',
    _user_id='user123'
)
```

---

### OSINT Module (NEW - Example)

```python
# Social media research
result = registry.execute_tool(
    'computer_use_browse_and_extract',
    task='Search Twitter for mentions of "printing company near me" in last 24 hours, extract top 10 tweets with sentiment',
    return_format='json',
    _user_id='user123'
)
```

---

## 📁 File Structure

```
AI_agents/
├── AI_infrastructure/
│   ├── core/
│   │   └── computer_use_executor.py      ← GLOBAL SINGLETON SERVICE
│   │
│   ├── tools/
│   │   ├── computer_use_tools.py         ← GENERIC PLATFORM TOOLS
│   │   ├── computer_use_tools_schema.json ← Tool Registry V3 schema
│   │   └── COMPUTER_USE_GUIDE.md         ← Complete usage guide
│   │
│   └── utils/
│       └── document_parser.py             ← Global utility (PDF/DOCX/TXT)
│
├── docker/
│   └── computer-use/
│       ├── Dockerfile                     ← Browser container image
│       ├── docker-compose.yml             ← Production deployment
│       ├── start.sh                       ← Container startup script
│       └── README.md                      ← Docker setup guide
│
└── UI/
    └── modules_external/
        └── professional-verification/
            ├── tools/
            │   └── implementations/
            │       └── computer_use_verification.py  ← Module-specific wrappers
            │                                            (uses generic tools)
            └── README.md
```

---

## 🔄 Data Flow

### Example: Competitor Quote Calculator Research

```
┌─────────────────────────────────────────────────────────────┐
│ USER REQUEST                                                │
│ "Research vistaprint.com pricing for business cards"       │
└────────────┬────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────┐
│ AI AGENT                                                    │
│ Analyzes request → Identifies need for browser automation  │
│ Calls: computer_use_browse_and_extract                     │
└────────────┬────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────┐
│ TOOL REGISTRY V3                                            │
│ Loads: AI_infrastructure/tools/computer_use_tools.py       │
│ Injects: _user_id, _injected_credentials                   │
└────────────┬────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────┐
│ GenericComputerUseSession                                   │
│ 1. Get browser container from ComputerUseExecutor          │
│ 2. Build task prompt with return format                    │
│ 3. Initialize Claude conversation                          │
└────────────┬────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────┐
│ ITERATION 1: Claude analyzes task                          │
│ Claude: "I need to see the screen first"                   │
│ Action: screenshot                                          │
└────────────┬────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────┐
│ ComputerUseExecutor.execute_computer_action()              │
│ - Routes to: take_screenshot(container_id)                 │
│ - Executes: scrot -o /tmp/screenshot.png in container      │
│ - Returns: base64-encoded image                            │
└────────────┬────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────┐
│ ITERATION 2: Claude sees browser                           │
│ Claude: "I see blank page. Navigate to vistaprint.com"     │
│ Action: type "vistaprint.com" + key "Return"               │
└────────────┬────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────┐
│ ComputerUseExecutor.type_text() + press_key()              │
│ - Executes: xdotool type 'vistaprint.com'                  │
│ - Executes: xdotool key Return                             │
└────────────┬────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────┐
│ ITERATION 3-10: Claude navigates site                      │
│ - Click "Business Cards"                                   │
│ - Select quantity: 1000                                    │
│ - Select options: 4-color both sides                       │
│ - Take screenshot of pricing                               │
└────────────┬────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────┐
│ ITERATION 11: Claude extracts data                         │
│ Claude: "I can see the price now"                          │
│ Returns: {"price": "$29.99", "delivery": "3-5 days"}      │
└────────────┬────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────┐
│ RESULT RETURNED TO USER                                    │
│ {                                                           │
│   "success": true,                                         │
│   "result": {"price": "$29.99", "delivery": "3-5 days"},  │
│   "screenshots": [11 base64 images],                       │
│   "iterations": 11                                         │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Design Decisions

### 1. **Singleton Executor**

ComputerUseExecutor is a singleton to:
- Reuse Docker client connection
- Pool browser containers (don't spawn new container for every task)
- Share resources across all modules

```python
# All modules get same instance
from AI_infrastructure.core.computer_use_executor import get_computer_use_executor

executor = get_computer_use_executor()  # Always returns same instance
```

---

### 2. **Generic Session Manager**

GenericComputerUseSession handles iterative Claude conversations:
- Manages request → tool_use → execute → result loop
- Stores screenshots for evidence
- Handles errors and timeouts
- Supports JSON or text return formats

```python
session = GenericComputerUseSession(
    task_description="Navigate to X, extract Y",
    max_iterations=30,
    return_format='json'
)
result = await session.run()
```

---

### 3. **Natural Language Interface**

No brittle selectors or XPaths. Just describe WHAT you want:

```python
# ✅ Good - Natural language
task = "Navigate to vistaprint.com quote calculator, configure 1000 business cards 4-color both sides, extract final price"

# ❌ Bad - Brittle selectors (OLD WAY)
driver.find_element(By.CSS_SELECTOR, '#quantity-selector').click()
driver.find_element(By.XPATH, '//option[@value="1000"]').click()
```

Claude figures out HOW to accomplish the task. If site layout changes, Claude adapts.

---

### 4. **Container Pooling**

Containers are reused to avoid startup overhead:

```python
# Get container (reuses existing if available)
container_id = await executor.get_browser_container(reuse=True)

# Use container for multiple tasks
result1 = await session1.run()
result2 = await session2.run()

# Release back to pool (don't destroy)
executor.release_container(container_id)
```

---

### 5. **Tool Registry V3 Integration**

All tools auto-discovered and available to AI agents:

```json
{
  "name": "computer_use_browse_and_extract",
  "platform_availability": "global",
  "ai_agent_enabled": true
}
```

AI agents automatically know when to use Computer Use vs other tools.

---

## 🔐 Security Considerations

### Container Isolation

Each browser container runs in isolated Docker environment:
- No access to host filesystem (except mounted volumes)
- Resource limits (2GB RAM, 2 CPU cores)
- Network isolation (verification-net bridge)

### Credential Handling

Sensitive credentials never stored in task descriptions:
- LinkedIn credentials injected via `_injected_credentials` parameter
- API keys from environment variables (`ANTHROPIC_API_KEY`)
- Stored securely in Platform Connections UI

### Rate Limiting

Platform enforces rate limits:
- 100 calls/hour per user
- 500 calls/day per user
- Prevents abuse and excessive API costs

---

## 💰 Cost Analysis

**Per Task Costs:**

| Task Complexity | Iterations | Anthropic Cost | Time |
|----------------|------------|---------------|------|
| Simple (single page) | 5-10 | $0.05-$0.10 | 10-20s |
| Medium (multi-page) | 15-30 | $0.10-$0.30 | 30-60s |
| Complex (checkout flow) | 30-50 | $0.30-$0.50 | 1-2min |
| Comparison (3 sites) | 50-100 | $0.50-$2.00 | 2-5min |

**Monthly Budget Estimates:**

- Light usage (100 tasks/month): ~$20-30/month
- Medium usage (500 tasks/month): ~$100-150/month
- Heavy usage (2000 tasks/month): ~$400-600/month

---

## 📊 Performance Metrics

**Container Startup:**
- First container: 5-10 seconds (Docker image pull + Xvfb startup)
- Subsequent containers: 2-3 seconds (image cached)
- Container reuse: <100ms (already running)

**Task Execution:**
- Simple extraction: 10-20 seconds
- Form filling: 15-30 seconds
- Multi-page navigation: 30-60 seconds
- Complex research: 1-3 minutes

**Resource Usage:**
- RAM per container: 1-2GB
- CPU per container: 1-2 cores
- Disk per container: ~2GB (image + temporary files)

---

## 🚀 Future Enhancements

### Planned Features

1. **Multi-Browser Support**
   - Firefox vs Chromium comparison
   - Mobile browser emulation
   - Specific browser version testing

2. **Parallel Execution**
   - Run multiple tasks simultaneously
   - Compare competitors in parallel
   - Reduce total execution time

3. **Smart Caching**
   - Cache screenshots for repeated tasks
   - Cache extracted data with TTL
   - Reduce API costs for common queries

4. **Enhanced Error Handling**
   - Auto-retry on transient failures
   - CAPTCHA detection and user prompt
   - Site-specific workarounds (load delays, pop-up handling)

5. **Performance Monitoring**
   - Track task success rates
   - Identify slow sites or failing patterns
   - Auto-optimize iteration counts

---

## 📝 Summary

**Computer Use is a PLATFORM SERVICE, not a module feature.**

- ✅ **Generic** - Works for ANY web-based task
- ✅ **Reusable** - Available to ALL modules via Tool Registry V3
- ✅ **Scalable** - Container pooling and resource limits
- ✅ **Intelligent** - Natural language interface, Claude figures out HOW
- ✅ **Secure** - Docker isolation, credential injection, rate limiting
- ✅ **Cost-Effective** - Pay only for what you use, ~$0.05-$0.50/task

**Use it for:**
- Competitor research (quote calculators, pricing)
- Web scraping (product data, reviews)
- Form automation (contact forms, quote requests)
- Testing (UI/UX, checkout flows)
- OSINT (social media, forums, databases)
- Professional verification (LinkedIn, credential registries)
- E-commerce analysis (price comparisons)
- **ANY task requiring browser interaction**

---

**Documentation:**
- Setup: `docker/computer-use/README.md`
- Usage: `AI_infrastructure/tools/COMPUTER_USE_GUIDE.md`
- Source: `AI_infrastructure/core/computer_use_executor.py`
- Tools: `AI_infrastructure/tools/computer_use_tools.py`

**Last Updated:** December 16, 2025  
**Version:** 1.0.0  
**Platform:** Valor AI - MustCare

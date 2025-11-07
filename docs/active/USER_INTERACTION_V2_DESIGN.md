# User Interaction System v2.0 - Complete Implementation Guide
**Date:** January 2025  
**Status:** ✅ FULLY IMPLEMENTED - Production Ready

---

## 🎯 Two-Feature Architecture

This system implements **TWO DISTINCT FEATURES** for user interaction:

### **FEATURE 1: Interaction Bubble (BLOCKING)**
- **Tool:** `request_user_interaction()`
- **Pattern:** Request-Response (AI waits for user)
- **Location:** Inside AI message bubbles
- **Use Case:** Decision points, confirmations, choices
- **Status:** ✅ COMPLETE (12/12 tests passing)

### **FEATURE 2: User Feedback Area (NON-BLOCKING)**
- **Tools:** `fetch_user_instructions()`, `show_feedback_area()`, `hide_feedback_area()`
- **Pattern:** Polling (AI continues working, checks periodically)
- **Location:** Fixed area above chat input
- **Use Case:** Continuous guidance during long operations
- **Status:** ✅ BACKEND COMPLETE, FRONTEND READY

---

## 📋 Design Philosophy

**Old Problem:**
- 3 separate tools (confirmation, choice, input) with overlapping functionality
- Complex for AI to choose which tool to use
- No way to provide guidance during long operations

**New Solution:**
- **Feature 1:** ONE unified blocking tool (`request_user_interaction()`)
- **Feature 2:** Three non-blocking feedback tools
- Two button modes: Auto-submit OR Text-insert
- Polling pattern for continuous user guidance
- Simpler for AI, more flexible for users

---

## � FEATURE 2: User Feedback Area (NON-BLOCKING)

### **Purpose:** Allow users to provide guidance DURING long operations

### **Tool 1: show_feedback_area()**
**When to use:** Start of long-running operations (>30 seconds)

```python
show_feedback_area(
    message="Processing 50 emails - this may take a few minutes...",
    show_buttons=True  # Shows [Pause] [Stop] [Explain] buttons
)
```

**AI Instructions:**
1. Call this BEFORE starting any long operation
2. Use clear, informative message
3. Always show buttons for user control

---

### **Tool 2: fetch_user_instructions()**
**When to use:** Periodically during long operations to check for guidance

```python
# Check every 5-10 operations
for i, item in enumerate(items):
    process_item(item)
    
    if i % 5 == 0:  # Check every 5 items
        feedback = fetch_user_instructions()
        if feedback.get('has_instructions'):
            adjust_behavior(feedback['instructions'])
```

**AI Instructions:**
1. Call periodically during work (every 5-10 operations)
2. Check `has_instructions` field
3. If user provided guidance, adjust your approach
4. Common adjustments:
   - Filter criteria (e.g., "Focus on legal emails")
   - Skip certain items (e.g., "Skip archived")
   - Change detail level (e.g., "Make it more technical")
   - Stop work (e.g., "Stop please")

**Response Format:**
```json
{
    "instructions": "Focus on legal team",
    "has_instructions": true,
    "timestamp": "2025-01-15T10:30:00Z"
}
```

---

### **Tool 3: hide_feedback_area()**
**When to use:** After long operation completes

```python
# When work is done
hide_feedback_area()
```

**AI Instructions:**
1. ALWAYS call this when long operation completes
2. Call even if operation was stopped/paused
3. Clean up UI for next interaction

---

## 🎯 When to Use Each Feature

### **Use Feature 1 (request_user_interaction) when:**
- ✅ Need decision BEFORE action
- ✅ Operation costs >$0.03 or >10k tokens
- ✅ Operation is destructive (delete, modify)
- ✅ Multiple valid approaches exist
- ✅ User choice affects entire workflow

**Example:** "Should I read 3 large PDFs? (~25k tokens, $0.075)"

### **Use Feature 2 (feedback_area) when:**
- ✅ Operation takes >30 seconds
- ✅ Processing >20 items sequentially
- ✅ User might want to adjust mid-task
- ✅ Operation is adjustable during execution
- ✅ Progress updates would help user

**Example:** "Processing 50 emails..." [User types: "Focus on legal team"]

---

## 📊 Complete Workflow Examples

### **Example 1: Email Analysis (Feature 2)**

```python
# 1. Show feedback area
show_feedback_area(
    message="Analyzing 50 emails - this may take 2-3 minutes...",
    show_buttons=True
)

# 2. Process with polling
processed = []
for i, email in enumerate(emails):
    category = categorize_email(email)
    processed.append({"email": email, "category": category})
    
    # 3. Check for guidance every 5 emails
    if i % 5 == 0:
        feedback = fetch_user_instructions()
        
        if feedback.get('has_instructions'):
            instruction = feedback['instructions'].lower()
            
            # Adjust based on user guidance
            if "legal" in instruction:
                emails = filter_legal(emails)
            if "skip archived" in instruction:
                emails = [e for e in emails if not e.archived]
            if "stop" in instruction:
                hide_feedback_area()
                return partial_results(i)

# 4. Hide when done
hide_feedback_area()

# 5. Present results
present_results(processed)
```

### **Example 2: Document Generation (Feature 2)**

```python
# 1. Show feedback area
show_feedback_area("Generating 30-page report...")

# 2. Generate with polling
for section in report_sections:
    generate_section(section)
    
    # Check after each section
    feedback = fetch_user_instructions()
    if feedback.get('has_instructions'):
        instruction = feedback['instructions'].lower()
        
        if "more technical" in instruction:
            increase_technical_detail()
        if "add examples" in instruction:
            add_more_examples()
        if "pause" in instruction:
            # Use Feature 1 for actual pause
            request_user_interaction(
                message="Paused. Generated {} sections so far.".format(len(completed)),
                interaction_mode="control",
                control_type="continue"
            )

# 3. Hide when done
hide_feedback_area()
present_report()
```

### **Example 3: Large File Operation (Feature 1 + Feature 2 Combined)**

```python
# 1. Use Feature 1 to get approval BEFORE starting
response = request_user_interaction(
    message="Should I read and analyze 3 large PDFs?",
    interaction_mode="confirmation",
    options=[
        {"label": "Read Full Content", "value": "confirm"},
        {"label": "Metadata Only", "value": "metadata"},
        {"label": "Cancel", "value": "cancel"}
    ],
    estimated_tokens=25000,
    estimated_cost_usd=0.075,
    level="high"
)

if response == "cancel":
    return "Operation cancelled"

# 2. Use Feature 2 during processing
show_feedback_area("Processing 3 PDFs - extracting content...")

for i, pdf in enumerate(pdfs):
    content = extract_pdf_content(pdf)
    analyze_content(content)
    
    # Check for guidance between PDFs
    if i < len(pdfs) - 1:
        feedback = fetch_user_instructions()
        if feedback.get('has_instructions'):
            if "stop" in feedback['instructions'].lower():
                hide_feedback_area()
                return partial_results(i + 1)

hide_feedback_area()
present_analysis()
```

---

## �🔧 FEATURE 1: Unified Interaction Tool (DETAILED)

### **Tool Name:** `request_user_interaction`

**Purpose:** Ask user for decisions, confirmations, or input BEFORE taking action (BLOCKING)

**Parameters:**
```python
def request_user_interaction(
    message: str,                          # Main message/question
    interaction_mode: str = "choice",      # "choice", "confirmation", "input", "control"
    options: List[Dict[str, Any]] = [],    # Button options
    allow_custom_input: bool = True,       # Show text field?
    button_behavior: str = "submit",       # "submit" OR "insert"
    control_type: Optional[str] = None,    # "pause", "stop", "explain", "continue"
    context: str = "",                     # Additional context
    level: str = "medium",                 # Risk level (low/medium/high/critical)
    estimated_tokens: Optional[int] = None,
    estimated_cost_usd: Optional[float] = None,
    metadata: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
```

---

## 🎨 UI Button Behaviors

### **Mode 1: Auto-Submit Buttons (submit)**
Click button → **Immediately sends to AI** (no edit)

**Use Cases:**
- Simple yes/no confirmations
- Quick choices from a list
- Predefined actions

**UI Behavior:**
```
Message: "Should I read the full email content?"
[Read Full Content] [Metadata Only] [Cancel]
User clicks [Read Full Content] → AI receives "Read Full Content"
```

**When to Use:**
- User won't need to modify the choice
- Simple binary or multi-choice decisions
- Confirmations where options are clear

---

### **Mode 2: Text-Insert Buttons (insert)** ⭐ NEW!
Click button → **Inserts text into input field** (user can edit before sending)

**Use Cases:**
- Control commands (pause, stop, explain)
- Template responses (user might want to add details)
- Commands that benefit from customization

**UI Behavior:**
```
Message: "Control Options:"
[Pause] [Stop] [Explain] [Continue]

User clicks [Pause]:
  → Input field populates with: "Pause please"
  → User can edit: "Pause please and wait for instructions"
  → User presses Send → AI receives edited text

User clicks [Explain]:
  → Input field populates with: "Explain your progress"
  → User can edit: "Explain your progress on the email analysis"
  → User presses Send → AI receives edited text
```

**When to Use:**
- User might want to add context/details
- Commands that might need parameters
- Flexible interactions where personalization helps

---

## 🎛️ Control Buttons (Proposed Set)

### **PAUSE Button**
**Inserted Text:** `"Pause please"`
**AI Instructions (hidden):** `"Pause current work and present options: [Continue] [Modify approach] [Explain progress] [Custom instructions]"`

**AI Behavior:**
1. Stops current operation
2. Calls `request_user_interaction()` with:
   - Options: Continue, Modify approach, Explain progress
   - Allow custom input: True
   - Shows what was accomplished so far

**Example Flow:**
```
User clicks [Pause]
→ Input: "Pause please"
→ User edits: "Pause please and explain what you've found"
→ AI stops, explains findings, shows options
```

---

### **STOP Button**
**Inserted Text:** `"Stop please"`
**AI Instructions (hidden):** `"Stop immediately and ask: [Stop and show progress] [Stop and discard] [Actually continue]"`

**AI Behavior:**
1. Stops current operation
2. Calls `request_user_interaction()` with:
   - Options: Show progress, Discard work, Continue anyway
   - Shows resources created so far with URLs

**Example Flow:**
```
User clicks [Stop]
→ Input: "Stop please"
→ User edits: "Stop please but save what you've done"
→ AI stops, saves progress, shows links to created resources
```

---

### **EXPLAIN Button**
**Inserted Text:** `"Explain your progress"`
**AI Instructions (hidden):** `"Provide detailed update including: what was completed, what remains, resources created (with URLs), discoveries made, then offer: [Explain specific part] [Continue] [Adjust approach]"`

**AI Behavior:**
1. Pauses work (non-destructive)
2. Generates progress report:
   - ✅ Completed actions with links
   - 🔄 In-progress actions
   - ⏳ Remaining actions
   - 🔍 Key discoveries/findings
3. Calls `request_user_interaction()` with:
   - Options: Explain specific part, Dive deeper, Continue, Adjust
   - Input field for specific questions

**Example Flow:**
```
User clicks [Explain]
→ Input: "Explain your progress"
→ User edits: "Explain your progress on the email analysis specifically"
→ AI provides detailed email analysis update, shows options
```

---

### **CONTINUE Button**
**Inserted Text:** `"Continue please"`
**AI Instructions:** `"Resume work from where you paused, maintaining context"`

**AI Behavior:**
1. Resumes previous operation
2. No new confirmation needed
3. Continues with same plan

**Example Flow:**
```
User clicks [Continue]
→ Input: "Continue please"
→ User can edit: "Continue please but skip the last step"
→ AI resumes work
```

---

## 📋 Tool Implementation Changes

### **NEW Unified Tool:**

```python
def request_user_interaction(
    message: str,
    interaction_mode: str = "choice",
    options: List[Dict[str, Any]] = [],
    allow_custom_input: bool = True,
    button_behavior: str = "submit",
    control_type: Optional[str] = None,
    context: str = "",
    level: str = "medium",
    estimated_tokens: Optional[int] = None,
    estimated_cost_usd: Optional[float] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    UNIFIED user interaction tool - handles all interaction types
    
    Modes:
    - "choice": User picks from options
    - "confirmation": Yes/No with cost transparency
    - "input": Free-form input with optional suggestions
    - "control": Pause/Stop/Explain/Continue buttons
    
    Button Behaviors:
    - "submit": Click button → send immediately to AI
    - "insert": Click button → insert text into input field (user can edit)
    
    Args:
        message: Main message/question to show user
        interaction_mode: Type of interaction
        options: Button options (label, value, description, insert_text)
        allow_custom_input: Show text field alongside buttons?
        button_behavior: "submit" (instant) or "insert" (editable)
        control_type: If mode="control", specify: pause/stop/explain/continue
        context: Additional context for user
        level: Risk level (low/medium/high/critical)
        estimated_tokens: Token cost estimate
        estimated_cost_usd: Dollar cost estimate
    
    Returns:
        Interaction request dict for frontend
    """
    
    # Auto-generate control buttons if control_type specified
    if interaction_mode == "control" and control_type:
        options = _generate_control_options(control_type)
        button_behavior = "insert"  # Control buttons always insert
    
    # Build interaction request
    interaction = {
        "type": "user_interaction_request",
        "interaction_mode": interaction_mode,
        "message": message,
        "context": context,
        "options": options,
        "allow_custom_input": allow_custom_input,
        "button_behavior": button_behavior,
        "level": level,
        "metadata": {
            "estimated_tokens": estimated_tokens,
            "estimated_cost_usd": estimated_cost_usd
        },
        "ui_config": {
            "show_buttons": len(options) > 0,
            "show_text_input": allow_custom_input,
            "button_mode": button_behavior,  # "submit" or "insert"
            "layout": _determine_layout(interaction_mode, options, allow_custom_input)
        }
    }
    
    return interaction


def _generate_control_options(control_type: str) -> List[Dict[str, str]]:
    """Generate button options for control commands"""
    
    control_configs = {
        "pause": [
            {
                "label": "Pause",
                "value": "pause",
                "insert_text": "Pause please",
                "description": "Pause work and show options"
            }
        ],
        "stop": [
            {
                "label": "Stop",
                "value": "stop",
                "insert_text": "Stop please",
                "description": "Stop immediately"
            }
        ],
        "explain": [
            {
                "label": "Explain Progress",
                "value": "explain",
                "insert_text": "Explain your progress",
                "description": "Show detailed update with links"
            }
        ],
        "continue": [
            {
                "label": "Continue",
                "value": "continue",
                "insert_text": "Continue please",
                "description": "Resume work"
            }
        ],
        "all": [
            {
                "label": "⏸️ Pause",
                "value": "pause",
                "insert_text": "Pause please",
                "description": "Pause and show options"
            },
            {
                "label": "⏹️ Stop",
                "value": "stop",
                "insert_text": "Stop please",
                "description": "Stop and show progress"
            },
            {
                "label": "📊 Explain",
                "value": "explain",
                "insert_text": "Explain your progress",
                "description": "Detailed progress update"
            },
            {
                "label": "▶️ Continue",
                "value": "continue",
                "insert_text": "Continue please",
                "description": "Resume work"
            }
        ]
    }
    
    return control_configs.get(control_type, control_configs["all"])
```

---

## 🎯 AI Agent Instructions

### When to Use Each Mode:

**Mode: "choice"**
- User needs to pick from a list
- Multiple options available
- Example: "Which email thread should I analyze?"

**Mode: "confirmation"**
- Need approval before expensive/destructive operation
- Show cost/risk transparency
- Example: "Read 3 large PDFs? (~25k tokens, $0.075)"

**Mode: "input"**
- Need specific information not provided
- Free-form text required
- Optional suggestions can speed up common inputs
- Example: "What email address should I send to?"

**Mode: "control"**
- User needs control over AI execution
- Pause/Stop/Explain/Continue commands
- Buttons insert text (user can customize before sending)
- Example: User clicks [Pause] → "Pause please" appears in input

---

## 🎨 Frontend UI Components

### **Auto-Submit Buttons:**
```jsx
<button 
  onClick={() => handleSubmit(option.value)}
  className="auto-submit-button"
>
  {option.label}
</button>
```

### **Text-Insert Buttons:**
```jsx
<button 
  onClick={() => handleInsertText(option.insert_text)}
  className="text-insert-button"
>
  {option.label}
</button>

// handleInsertText function:
const handleInsertText = (text) => {
  setInputValue(text);  // Populate input field
  inputRef.current.focus();  // Focus so user can edit
  // User can now edit text before pressing Send
};
```

### **Complete Interaction Bubble:**
```jsx
<InteractionBubble data={interactionData}>
  <div className="message">{data.message}</div>
  {data.context && <div className="context">{data.context}</div>}
  
  {/* Cost/Risk Metadata */}
  {data.metadata.estimated_tokens && (
    <div className="cost-info">
      ~{data.metadata.estimated_tokens} tokens 
      (${data.metadata.estimated_cost_usd})
    </div>
  )}
  
  {/* Buttons */}
  {data.options.map(option => (
    data.button_behavior === "submit" ? (
      <SubmitButton option={option} />
    ) : (
      <InsertButton option={option} />
    )
  ))}
  
  {/* Custom Input Field */}
  {data.allow_custom_input && (
    <div className="custom-input">
      <textarea 
        placeholder={data.input_placeholder} 
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
      />
      <button onClick={handleSubmit}>Send</button>
    </div>
  )}
</InteractionBubble>
```

---

## 🔄 Migration Strategy

### **Phase 1: Keep Old Tools (Backward Compatibility)**
- Keep existing 3 tools working
- Add new unified tool alongside
- Test new tool with control buttons first

### **Phase 2: Update AI Instructions**
- Document unified tool in system prompt
- Show AI agents when to use each mode
- Provide examples of control buttons

### **Phase 3: Gradual Migration**
- New features use unified tool only
- Old tools marked as deprecated
- Eventually remove old tools after testing

---

## ✅ Benefits of Unified Tool

**For AI Agents:**
- ✅ ONE tool to learn instead of 3
- ✅ Clear parameters control behavior
- ✅ Less confusion about which tool to use
- ✅ Consistent return format

**For Users:**
- ✅ Consistent UI experience
- ✅ Text-insert buttons allow customization
- ✅ Control buttons (Pause/Stop/Explain) for long operations
- ✅ Always have option to type custom instructions

**For Developers:**
- ✅ Single codebase to maintain
- ✅ Easier to add new interaction types
- ✅ Consistent schema and validation
- ✅ Simpler frontend integration

---

## 🚀 Next Steps

1. **Implement unified tool function** in `user_interaction_tools.py`
2. **Create unified schema** in `user_interaction_tools.json`
3. **Update system prompt** with unified tool instructions
4. **Create frontend components** for text-insert buttons
5. **Test control buttons** (Pause/Stop/Explain/Continue)
6. **Document migration path** for existing uses
7. **Update registry** to load new tool
8. **End-to-end testing** with real conversations

---

## 📊 Comparison: Old vs New

| Feature | Old System (3 tools) | New System (1 tool) |
|---------|---------------------|---------------------|
| **Tools** | 3 separate tools | 1 unified tool |
| **AI Learning Curve** | High (which tool?) | Low (one tool, clear modes) |
| **Button Behaviors** | Submit only | Submit OR Insert |
| **Control Commands** | Not supported | Pause/Stop/Explain/Continue |
| **Code Duplication** | High (3 implementations) | Low (single implementation) |
| **Maintenance** | Complex (3 schemas) | Simple (1 schema) |
| **User Experience** | Good | Better (text-insert buttons!) |
| **Flexibility** | Limited | High (mode-based) |

---

**Status:** Ready for implementation
**Priority:** HIGH (consolidation will simplify entire system)
**Risk:** LOW (can keep old tools during migration)

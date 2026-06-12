# Tool Result Visual Mockup - What You Want

**Date:** November 19, 2025

---

## Current AI Agents Behavior (What You Have Now)

```
┌──────────────────────────────────────┐
│ 🟣 [Purple Brain - PULSING]         │
│ Thinking: Analyzing your request... │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ 🟡→🟢 [Yellow Cog SPINNING]          │  (turns green when done)
│ Tool: gmail_list_messages           │
│ Input: {max_results: 5}             │
│ ─────────────────────────────       │  (result merged in same bubble)
│ Result: [array of emails...]        │
│ [collapse] [copy]                   │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ 📝 [AI Avatar]                      │
│ I found 5 emails in your inbox...   │
│ [collapse] [copy] [raw]             │
└──────────────────────────────────────┘
```

---

## What You Want (New Behavior)

```
┌──────────────────────────────────────┐
│ 🟣 [Purple Brain - PULSING]         │  ✅ KEEP THIS
│ Thinking: Analyzing your request... │  ✅ EXACTLY AS IS
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ 🟡→🟢 [Yellow Cog SPINNING]          │  ✅ KEEP THIS
│ Tool: gmail_list_messages           │  ✅ Yellow when running
│ Input: {max_results: 5}             │  ✅ Green when complete
│ [collapse] [copy]                   │  ✅ Spinning animation
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ 🔵 [Blue Flag Icon] Success ✓       │  🆕 NEW BUBBLE!
│ Tool Result: gmail_list_messages    │  🆕 Blue flag avatar
│                                      │  🆕 Simpler styling
│ Result:                              │  🆕 Separate from tool
│ [array of emails...]                 │
│                                      │
│ [collapse] [copy] [raw]              │  🆕 THREE BUTTONS
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ 📝 [AI Avatar]                      │  ✅ KEEP THIS
│ I found 5 emails in your inbox...   │  ✅ No changes
│ [collapse] [copy] [raw]             │  ✅ Same as before
└──────────────────────────────────────┘
```

---

## Icon & Color Guide

### 1. Thinking Bubble (KEEP)
```
Icon: 🧠 (fa-brain)
Background: Purple (#8b5cf6)
Animation: Pulsing (thinkingPulse)
Status: ✅ DON'T CHANGE
```

### 2. Tool Use Bubble (KEEP)
```
Icon: ⚙️ (fa-cog)
Background: 
  - 🟡 Yellow (#eab308) when running
  - 🟢 Green (#22c55e) when complete
  - 🔴 Red (#ef4444) on error
Animation: Spinning (spinCog) when running
Status: ✅ DON'T CHANGE
```

### 3. Tool Result Bubble (NEW!)
```
Icon: 🚩 (fa-flag)  ← YOU WANT THIS?
Background: Blue (#60A5FA)
Animation: None (static flag)
Style: Simpler than tool use
Buttons: Copy + Collapse + Raw
Status: 🆕 IMPLEMENT THIS
```

### 4. Text Response (KEEP)
```
Icon: 🤖 (AI avatar)
Background: Default (white/gray)
Buttons: Copy + Collapse + Raw
Status: ✅ DON'T CHANGE
```

---

## Button Layout Options

### Option A: Header Buttons (Right-aligned)
```
┌──────────────────────────────────────────────┐
│ 🔵 TOOL RESULT           [↕️] [📋] [</>]    │
│ gmail_list_messages                          │
│                                              │
│ Result: {...}                                │
└──────────────────────────────────────────────┘
```

### Option B: Bottom Buttons (Centered)
```
┌──────────────────────────────────────────────┐
│ 🔵 TOOL RESULT: gmail_list_messages          │
│                                              │
│ Result: {...}                                │
│                                              │
│         [↕️ Collapse] [📋 Copy] [</> Raw]    │
└──────────────────────────────────────────────┘
```

### Option C: Inline Buttons (Like Tool Use)
```
┌──────────────────────────────────────────────┐
│ 🔵 [TOOL RESULT] gmail_list_messages  [↕️][📋][</>]│
│                                              │
│ Result: {...}                                │
└──────────────────────────────────────────────┘
```

**Which layout do you prefer?**

---

## Styling Comparison

### Tool Use Bubble (Current - Complex)
```css
.tool-bubble {
    background: linear-gradient(135deg, ...);
    border: 2px solid ...;
    box-shadow: 0 4px 12px ...;
    padding: 16px;
    border-radius: 12px;
    /* Complex gradients, shadows, animations */
}
```

### Tool Result Bubble (NEW - Simpler)
```css
.tool-result-bubble {
    background: #1e293b;  /* Solid color, no gradient */
    border-left: 4px solid #60A5FA;  /* Simple blue border */
    padding: 12px;  /* Less padding */
    border-radius: 8px;  /* Smaller radius */
    /* No shadows, no fancy effects */
}
```

**Is this the "simpler" you want?**

---

## Animation Comparison

### Thinking Bubble
```css
animation: thinkingPulse 2s ease-in-out infinite;
/* Smooth pulsing effect */
```

### Tool Use Bubble (Running)
```css
animation: spinCog 2s linear infinite;
/* Spinning cog animation */
```

### Tool Result Bubble (NEW)
```css
/* NO ANIMATION - Static flag icon */
```

---

## Button Icons

```
[↕️] = fa-chevron-down/up (Collapse/Expand)
[📋] = fa-copy (Copy content)
[</>] = fa-code (Copy raw JSON/markdown)
```

---

## Multi-Tool Example

When multiple tools are used:

```
🟣 Thinking...

🟡→🟢 Tool 1: gmail_list_messages

🔵 Result 1: 5 emails found  ← NEW!

🟡→🟢 Tool 2: google_calendar_list_events

🔵 Result 2: 3 events today  ← NEW!

📝 You have 5 emails and 3 calendar events
```

**Each tool gets its own result bubble!**

---

## Error Handling

### Success Case:
```
┌──────────────────────────────────┐
│ 🟢 [Green Cog] Tool Complete     │
└──────────────────────────────────┘
        ↓
┌──────────────────────────────────┐
│ 🔵 [Blue Flag] Success ✓         │
│ Result: {...}                    │
└──────────────────────────────────┘
```

### Error Case:
```
┌──────────────────────────────────┐
│ 🔴 [Red Cog] Tool Error          │
└──────────────────────────────────┘
        ↓
┌──────────────────────────────────┐
│ 🔴 [Red Flag?] Error ✗           │  ← Should flag be red on error?
│ Error: Permission denied         │  ← Or stay blue?
└──────────────────────────────────┘
```

**Should tool result flag change color on error?**
- Option A: Keep blue flag, show "Error ✗" in red text
- Option B: Red flag icon on error (like tool cog)

---

## Questions for You

### 1. Icon Confirmation
- Blue flag (fa-flag) - YES or NO?
- If NO, which icon? (fa-clipboard-check, fa-file-alt, fa-check-square?)

### 2. Button Layout
- Option A (header right), Option B (bottom center), or Option C (inline)?

### 3. Simpler Styling
- My interpretation correct? (solid bg, less padding, no shadows)
- Or something different?

### 4. Error Handling
- Blue flag + red text on error?
- Or red flag icon on error?

### 5. Collapse Default
- Start expanded (show results immediately)?
- Start collapsed (like tool use)?

### 6. Raw Button Content
What should "Raw" button copy?
- Formatted JSON: `{\n  "success": true,\n  "data": [...]\n}`
- Minified JSON: `{"success":true,"data":[...]}`
- As-received from API (might be string or object)

---

## Implementation Checklist

Once you confirm the above, I will:

- [ ] Find AI Agents streaming handler (likely separate from Prime AI)
- [ ] Create `.tool-result-bubble` CSS with simpler styling
- [ ] Add blue flag icon with blue background
- [ ] Implement Copy + Collapse + Raw buttons
- [ ] Update tool_result event handler to create separate bubble
- [ ] Test with single tool call
- [ ] Test with multiple tool calls
- [ ] Test error handling
- [ ] Test button functionality (copy, collapse, raw)
- [ ] Update documentation

---

**Status:** Awaiting your answers to the 6 questions above  
**Ready to implement:** As soon as you confirm the details

---

**Last Updated:** November 19, 2025, 8:35 PM

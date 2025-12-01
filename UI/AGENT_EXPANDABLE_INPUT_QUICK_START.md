# Agent Expandable Input - Quick Start Testing Guide
**Date:** December 1, 2025  
**Purpose:** Fast testing guide for new expandable input system

---

## 🚀 Quick Test (5 Minutes)

### **Step 1: Load Application**
```powershell
# Start AI Agent server
cd c:\Users\gpoli\GIT\AI_agents
BISTART

# Wait 15 seconds for server to start
# Open browser to http://localhost:5001
```

### **Step 2: Open Console**
Press `F12` → Console tab

**Expected output:**
```
[AgentInput] Initialized state for Agent-1
[AgentInput] Agent-1 handlers initialized
[createAgentColumn] Agent-1 expandable input handlers initialized
```

**❌ If you see errors:**
- Check script loading order in HTML
- Verify all 4 files exist (agent-column.js, agent-input-manager.js, agent-ui.css, agent-js.js)

---

### **Step 3: Load Thread**
1. Click "Start New Chat" button in Agent-1
2. Type test message: "Hello Agent 1"
3. Send message

**Expected:**
- Input container appears at bottom (30px collapsed bar)
- Chevrons visible in center
- Hover shows accent glow

---

### **Step 4: Test Expand/Collapse**
**Test 1: Click to expand**
- Click the collapsed bar
- Should expand with smooth animation
- 6 buttons appear on right side
- Textarea gains focus

**Test 2: Blur to collapse**
- Click outside textarea (empty state)
- After 200ms, should collapse back to 30px bar

**Test 3: Hover animation**
- Hover collapsed bar
- Chevrons should:
  - Change to accent color
  - Animate upward (bouncing)
  - Border glows with accent color

---

### **Step 5: Test Voice Transcription (CRITICAL)**
**This tests column isolation**

1. **Start recording in Agent-1:**
   - Click microphone button (4th from bottom)
   - Button turns red with pulse animation
   - Icon changes from microphone to stop
   - Allow microphone access

2. **Speak:** "This is Agent One"

3. **Verify transcript appears in Agent-1 input only**

4. **Start recording in Agent-2:**
   - Load different thread in Agent-2
   - Click Agent-2's mic button
   - Speak: "This is Agent Two"

5. **Verify isolation:**
   - Agent-1 input contains: "This is Agent One"
   - Agent-2 input contains: "This is Agent Two"
   - No cross-contamination

**✅ PASS:** Each agent receives only its own transcript  
**❌ FAIL:** Transcripts appear in wrong agent or multiple agents

---

### **Step 6: Test Feedback System**
1. **Open feedback in Agent-1:**
   - Click feedback button (3rd from bottom, comment-dots icon)
   - Feedback area slides down above input

2. **Test quick feedback:**
   - Click pause button (⏸️)
   - Should insert: "Please pause and wait for my instructions."

3. **Send feedback:**
   - Click send button (📤)
   - Feedback sent as message
   - Feedback area closes

4. **Verify isolation:**
   - Agent-2 feedback area should remain closed
   - Only Agent-1 received the feedback message

---

### **Step 7: Test Auto-Scroll Toggle**
1. **Disable auto-scroll in Agent-1:**
   - Click auto-scroll button (2nd from bottom, angle-double-down icon)
   - Button loses `.active` class (visual change)

2. **Send messages to Agent-1:**
   - Messages container should NOT auto-scroll

3. **Verify Agent-2 still auto-scrolls:**
   - Send messages to Agent-2
   - Should scroll to bottom automatically

---

## ✅ Success Criteria

After 5-minute test, all should be TRUE:
- [ ] Input container expands/collapses smoothly
- [ ] Chevron animation works on hover
- [ ] Voice transcription routes to correct agent
- [ ] Feedback system works per-agent
- [ ] Auto-scroll toggle works per-agent
- [ ] No console errors
- [ ] No cross-contamination between agents

---

## 🐛 Common Issues & Fixes

### **Issue: Input container doesn't appear**
**Symptoms:** No collapsed bar at bottom of agent column

**Cause:** Thread not loaded or display: none not removed

**Fix:**
```javascript
// Console command:
const container = document.querySelector('#agent-column-1 .agent-input-container');
console.log('Container:', container, 'Display:', container?.style.display);

// Should show: Display: "block" (not "none")
```

---

### **Issue: Chevrons not visible**
**Symptoms:** Collapsed bar is blank

**Cause:** Font Awesome not loaded or CSS issue

**Fix:**
- Verify Font Awesome loaded: `console.log(getComputedStyle(document.querySelector('.agent-input-container'), '::after').content)`
- Should show: "\f077\A\f077" (Unicode chevron-up characters)

---

### **Issue: Transcription goes to wrong agent**
**Symptoms:** Speaking to Agent-2 but text appears in Agent-1

**Cause:** SharedTranscriptionState routing issue

**Fix:**
```javascript
// Console debug:
window.SharedTranscriptionState.currentTarget
// Should show: "agent-2" when recording in Agent-2
```

**Permanent fix:** Check agent-input-manager.js line 229:
```javascript
window.SharedTranscriptionState.startRecording(null, (finalTranscript) => {
    const targetInput = document.getElementById(`agent-input-${agentId}`);  // ← Verify agentId correct
    targetInput.value += finalTranscript + ' ';
});
```

---

### **Issue: Buttons not clickable**
**Symptoms:** Clicking buttons does nothing

**Cause:** `pointer-events: none` on wrapper

**Fix:**
```javascript
// Console command:
const wrapper = document.querySelector('#agent-column-1 .agent-input-wrapper');
console.log('Pointer events:', getComputedStyle(wrapper).pointerEvents);

// Should show: "auto" when expanded, "none" when collapsed
```

---

### **Issue: Input doesn't collapse on blur**
**Symptoms:** Stays expanded forever

**Cause:** Focus moved to another element within container

**Fix:**
- Blur handler has 200ms delay to allow button clicks
- If textarea is empty, should collapse
- Check agent-input-manager.js line 117-124

---

## 🔧 Advanced Debugging

### **Check state for specific agent:**
```javascript
// Console command:
console.log('Agent-1 state:', window.AgentInput.states?.[1] || AgentInputStates?.[1]);

// Expected output:
{
    isExpanded: false,
    isFeedbackOpen: false,
    isRecording: false,
    isAutoScrollEnabled: true,
    feedbackText: '',
    transcriptionActive: false,
    attachedFiles: []
}
```

### **Check event handlers:**
```javascript
// Console command:
console.log('Agent-1 handlers:', AgentInput.handlers?.[1]);

// Should show object with: containerClick, textareaFocus, textareaBlur, textareaKeydown, fileChange
```

### **Force expand input:**
```javascript
// Console command:
AgentInput.expand(1);

// Input should expand immediately
```

### **Force show input container:**
```javascript
// Console command:
document.querySelector('#agent-column-1 .agent-input-container').style.display = 'block';

// Container should appear
```

---

## 📊 Performance Checks

### **Memory leaks:**
```javascript
// Before closing agent:
console.log('Handlers count:', Object.keys(AgentInput.handlers || {}).length);

// Close Agent-1 column

// After closing:
console.log('Handlers count:', Object.keys(AgentInput.handlers || {}).length);
// Should decrease by 1
```

### **Animation performance:**
```javascript
// Console → Performance tab
// Record while expanding/collapsing
// Check for 60 FPS (16.67ms per frame)
// No layout thrashing
```

---

## 🎯 Critical Test: Multi-Agent Isolation

**This is the MOST IMPORTANT test for column-specific isolation:**

```
Setup: Load threads in Agent-1, Agent-2, Agent-3

Test Sequence:
1. Expand Agent-1 input → Verify Agent-2/3 stay collapsed
2. Open feedback in Agent-2 → Verify Agent-1/3 unaffected
3. Start recording in Agent-3 → Verify only Agent-3 receives transcript
4. Toggle auto-scroll in Agent-1 → Verify Agent-2/3 still auto-scroll
5. Type in Agent-1 input → Verify Agent-2/3 inputs empty

Expected Result: ZERO cross-contamination
```

**✅ PASS:** All agents completely independent  
**❌ FAIL:** Any state leaks between agents

---

## 📝 Report Issues

If tests fail, provide:
1. **Browser:** Chrome/Edge/Firefox + version
2. **Console errors:** Full error text
3. **Steps to reproduce:** Exact sequence
4. **State dump:** Output of debug commands above

**Quick report format:**
```
Issue: [Brief description]
Browser: Chrome 120
Console: [Error text]
Steps: 1) Load thread, 2) Click mic, 3) Transcript appears in wrong agent
State: Agent-1 isRecording=true, Agent-2 input has transcript
```

---

**Last Updated:** December 1, 2025  
**Testing Time:** 5 minutes  
**Critical Tests:** Voice transcription routing, column isolation

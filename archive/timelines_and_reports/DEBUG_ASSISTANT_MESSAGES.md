# Debug Assistant Message Rendering

## Steps to Debug:

1. **Open browser console** (F12)
2. **Load the thread** that has assistant messages
3. **Look for these specific logs:**

### Expected Log Pattern:

```
[renderAssistantContent] CALLED with content type: object array[3]
[renderAssistantContent] Processing 3 blocks
[renderAssistantContent] Processing block type: thinking
[renderAssistantContent] ✅ Added thinking block
[renderAssistantContent] Processing block type: text
[renderAssistantContent] Rendering text block (206 chars)
[renderAssistantContent] ✅ Visualization engine rendered 1234 chars
[renderAssistantContent] ✅ Added text block to contentDiv
[renderAssistantContent] Processing block type: tool_use
[renderAssistantContent] ✅ Added tool_use block
[renderAssistantContent] ✅ COMPLETED - contentDiv has 3 children, innerHTML length: 5678
```

### What to Check:

**If you DON'T see `[renderAssistantContent] CALLED`:**
- The render function isn't being called for assistant messages
- Check: `[UnifiedMessageRenderer] Rendering ASSISTANT message`

**If you see `CALLED` but NOT `✅ COMPLETED`:**
- The function is crashing or returning early
- Look for error messages

**If you see `✅ COMPLETED` with innerHTML length > 0:**
- Content IS being rendered
- **PROBLEM IS CSS/VISIBILITY**
- Open DevTools Elements tab
- Find `.ai-message.assistant` elements
- Check their computed styles for:
  - `display: none`
  - `visibility: hidden`
  - `opacity: 0`
  - `height: 0`
  - Parent container issues

**If you see `✅ COMPLETED` but innerHTML length = 0:**
- Content blocks are empty or not rendering
- Check block types and content

## Quick CSS Check:

Open console and run:
```javascript
// Find all assistant messages
const assistantMessages = document.querySelectorAll('.ai-message.assistant');
console.log(`Found ${assistantMessages.length} assistant messages`);

// Check each one
assistantMessages.forEach((msg, i) => {
    const computed = window.getComputedStyle(msg);
    const contentDiv = msg.querySelector('.ai-message-content');
    console.log(`Assistant message ${i+1}:
        display: ${computed.display}
        visibility: ${computed.visibility}
        opacity: ${computed.opacity}
        height: ${computed.height}
        innerHTML length: ${contentDiv?.innerHTML.length || 0}
        children count: ${contentDiv?.children.length || 0}
    `);
});
```

## Share with me:

1. ✅ or ❌ Do you see `[renderAssistantContent] CALLED` logs?
2. ✅ or ❌ Do you see `✅ COMPLETED` logs?
3. What are the innerHTML lengths?
4. Result of the CSS check script above

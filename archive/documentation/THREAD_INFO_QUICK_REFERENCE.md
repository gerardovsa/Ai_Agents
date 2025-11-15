# Thread Info Container - Quick Reference Card

**One-page reference for developers**

---

## 🎯 Core Function

```javascript
ThreadManager.renderThreadInfoContainer(location, threadId, compact)
```

**Parameters:**
- `location`: 'prime' | 'agent-1' | 'agent-2' | 'agent-3' | 'synergy'
- `threadId`: String (thread_slug)
- `compact`: Boolean (true = smaller, false = full size)

**Returns:** HTML string with 5-row structure

---

## 📋 5-Row Structure

```
ROW 1: [Title] ...................... [Agent Badge]
ROW 2: [💬 Count] [📅 Date] [🕐 Time]
ROW 3: [#️⃣ Thread ID] .............. [+ Tag Btn]
ROW 4: [Tag Pills] ..................... (if tags)
ROW 5: [🔗 Synergy Badge] .............. (if linked)
```

---

## 📍 Usage by Location

### Prime Panel
```javascript
// Already in HTML, just update
ThreadManager.updatePrimeHeader(threadId);
```

### Agent Column
```javascript
// Dynamic render on thread load
const html = ThreadManager.renderThreadInfoContainer(
    `agent-${agentId}`, 
    threadId, 
    true  // compact
);
document.getElementById(`thread-info-${agentId}`).innerHTML = html;
```

### Synergy Card
```javascript
// Wrapper + render
const html = ThreadManager.renderThreadInfoContainer(
    'synergy', 
    threadId, 
    true  // compact
);
return `<div class="synergy-linked-thread-wrapper">${html}</div>`;
```

---

## 🎨 CSS Classes

### Container
- `.ai-chat-header-info` - Base container
- `.thread-info-compact` - Compact mode modifier

### Agent Badges
- `.thread-agent-badge-prime` - Gold (Prime)
- `.thread-agent-badge-agent` - Blue (Agents)

### Wrappers
- `.synergy-linked-thread-wrapper` - Clickable Synergy container
- `.no-thread-message` - Empty state

---

## 🔧 Helper Functions

```javascript
// Copy thread ID
ThreadManager.copyThreadId(threadId)

// Copy Synergy info
ThreadManager.copySynergyInfo(synergyId, synergyName)

// Edit title
ThreadManager.startInlineTitleEdit(location)

// Add tag
ThreadManager.showAddTagModal(location)

// Remove tag
ThreadManager.removeTag(threadId, tag)

// Unlink Synergy
ThreadManager.unlinkFromSynergy(threadId)
```

---

## 📊 Data Sources

| Display | Source | Fallback |
|---------|--------|----------|
| Title | `thread.title` | "Untitled" |
| Agent | `thread.agent` or location | "Prime" |
| Msg Count | `thread.message_count` | `messages.length` or 0 |
| Date | `thread.created` | "--" |
| Time | `thread.updated` | `thread.created` or "--" |
| Thread ID | `thread.id` | - |
| Tags | `thread.tags` | [] |
| Synergy ID | `thread.synergy_card_id` | null |

---

## 🎨 Sizing Reference

### Full Mode (Prime)
```css
padding: 15px
title: 16px (bold)
metadata: 12px
```

### Compact Mode (Agents/Synergy)
```css
padding: 10px
title: 14px (bold)
metadata: 11px
```

---

## ✅ Quick Testing

```javascript
// 1. Check thread exists
ThreadManager.threads.find(t => t.id === threadId)

// 2. Render HTML
const html = ThreadManager.renderThreadInfoContainer('agent-1', threadId, true);
console.log(html);

// 3. Update container
document.getElementById('thread-info-1').innerHTML = html;

// 4. Verify
document.querySelector('[data-thread-id]')  // Should exist
```

---

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| Container blank | Check `threadId` exists in `ThreadManager.threads` |
| Wrong size | Check `compact` parameter (true/false) |
| Not updating | Call `renderThreadInfoContainer()` after changes |
| Missing Synergy | Check `thread.synergy_card_id` is set |
| Tags not showing | Check `thread.tags` is array |

---

## 📂 File Locations

**Main File:** `UI/business-ai-platform-v2.html`

**Function Location:** Lines 16973-17226
```javascript
ThreadManager.renderThreadInfoContainer()
```

**CSS Location:** Lines 1357-1465
```css
.thread-info-compact { ... }
```

---

## 🔄 Update Flow

```
User Action
    ↓
Update thread object
    ↓
[Prime]    ThreadManager.updatePrimeHeader(threadId)
[Agent]    Re-render via renderThreadInfoContainer()
[Synergy]  Re-render via renderLinkedThreads()
    ↓
UI updates automatically
```

---

## 🚀 Integration Checklist

- [ ] Thread loaded → Call render function
- [ ] Thread updated → Call render function
- [ ] Use correct location parameter
- [ ] Use compact=true for agents/synergy
- [ ] Handle empty state (no thread)
- [ ] Update container innerHTML
- [ ] Verify all 5 rows display

---

## 💡 Pro Tips

1. **Don't re-render on every update** - Update specific elements when possible
2. **Cache Synergy data** - Avoid duplicate fetches
3. **Use compact mode** - For space-constrained areas
4. **Check thread exists** - Before rendering
5. **Handle errors gracefully** - Show empty state if missing

---

## 📚 Full Documentation

- `THREAD_INFO_CONTAINER_UNIFIED.md` - Complete implementation
- `THREAD_INFO_VISUAL_GUIDE.md` - Visual diagrams
- `UNIFIED_THREAD_INFO_SUMMARY.md` - Executive overview
- `THREAD_INFO_TESTING_CHECKLIST.md` - Testing guide

---

**Last Updated:** November 10, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅

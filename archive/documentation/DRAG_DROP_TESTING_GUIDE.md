# Drag-and-Drop Testing Guide - Quick Start

**Quick reference for testing the new drag-and-drop features**

---

## 🎯 What to Test

You now have **full drag-and-drop** between all locations:

1. ✅ Thread menu items → Prime/Agent/Synergy
2. ✅ Prime thread-info card → Agent/Synergy  
3. ✅ Agent thread-info cards → Prime/Other Agents/Synergy
4. ✅ Synergy cards now show linked threads (no more errors)

---

## 🔍 Quick Visual Check

### Look for Drag Handles
Open the platform and check if you see grip icons (≡≡) on thread-info cards:

```
┌────────────────────────────────┐
│ ≡≡  My Thread Title            │  ← Should see grip icon
│     Agent 1                    │
│     5 messages • 2 hours ago   │
└────────────────────────────────┘
```

**Where to look**:
- Prime panel header (if thread loaded)
- Agent column headers (if threads loaded)
- Hover over the grip icon - it should brighten and scale slightly

---

## 🧪 Test Scenarios (Simple)

### Test 1: Thread Menu → Agent (Basic)
```
1. Click hamburger menu (☰) to open thread list
2. Grab ANY thread item
3. Drag to Agent 1 column (middle panel)
4. Drop

✅ PASS if:
- Agent 1 shows thread-info with grip icon
- Messages load in Agent 1
- No errors in console (F12)
```

---

### Test 2: Agent → Agent (New Feature!)
```
1. Load thread in Agent 1 (from previous test)
2. Grab the GRIP ICON (≡≡) in Agent 1 header
3. Drag to Agent 2 column
4. Drop

✅ PASS if:
- Agent 1 header clears ("No thread assigned")
- Agent 2 shows thread-info with grip icon
- Messages load in Agent 2
- Thread moved (not copied)
```

---

### Test 3: Agent → Synergy (Link, Don't Move)
```
1. Load thread in Agent 1
2. Click "Synergy" tab (top navigation)
3. Grab GRIP ICON (≡≡) from Agent 1 header
4. Drag to ANY Synergy card
5. Drop

✅ PASS if:
- Synergy card glows GREEN with dashed border
- "Thread linked to Synergy session" notification
- Thread STAYS in Agent 1 (not moved!)
- Synergy card shows thread in "Linked Threads" section
```

---

### Test 4: Synergy Card Error Fix
```
1. Go to Synergy tab
2. Find card with linked threads
3. Look at "Linked Threads" section

✅ PASS if:
- See threads listed (not "Error loading threads")
- Each thread shows in compact 5-row format
- Click thread opens it in correct location
- NO console errors
```

---

## 🐛 Common Issues & Fixes

### Issue: No Grip Icons Visible
**Check**: Look in Prime header or Agent headers when threads are loaded  
**Fix**: Refresh page (Ctrl+R)

### Issue: Can't Grab Grip Icon
**Check**: Cursor should change to "move" cursor over icon  
**Fix**: Try clicking and holding for 500ms before dragging

### Issue: Drop Doesn't Work
**Check**: Console (F12) for errors  
**Possible Causes**:
- Target area not a valid drop zone
- JavaScript error during drop
- Network issue (backend API call failed)

### Issue: Synergy Still Shows Errors
**Check**: Exact error message in console  
**Fix**: Verify backend API `/api/threads/details` returns proper format

---

## 📊 Console Logs to Watch

Open browser console (F12) and look for these:

### ✅ Good Logs (Success)
```
[DRAG CARD] Started dragging thread: 1234567890 from agent-1
[DROP] Thread 1234567890 from agent-1 dropped on Agent 2
[DROP] Rendered thread-info in Agent 2 header
[CLEAR] Cleared thread-info at agent-1
Thread linked to Synergy session
```

### ❌ Bad Logs (Problems)
```
[DRAG] No threadId found on card
[DROP] Agent 2 header-info element not found
TypeError: Cannot read properties of undefined
[SYNERGY] Invalid API response format
```

---

## 🎨 Visual Effects to Check

### During Drag
- Card becomes semi-transparent (50% opacity)
- Dashed border around card
- Cursor changes to "move" icon

### On Drop Zone Hover
**Agent Columns**:
- Blue glow effect
- `drag-over` class applied

**Synergy Cards**:
- Green dashed border
- Card scales up slightly (1.02x)
- Green glow effect

### After Drop
**Source** (if moved):
- Cleared with "No thread assigned" message

**Target**:
- Thread-info appears instantly
- Grip icon visible
- Messages load (may take 1-2 seconds)

---

## 🏃 Quick Test Script (1 Minute)

**Do this in order**:

1. **Open platform** → Load any thread in Prime
2. **Grab grip icon** in Prime → Drag to Agent 1 → Drop  
   → Check: Agent 1 shows thread ✅

3. **Grab grip icon** in Agent 1 → Drag to Agent 2 → Drop  
   → Check: Agent 1 clears, Agent 2 shows thread ✅

4. **Open Synergy tab** → Grab grip icon from Agent 2  
   → Drag to Synergy card → Drop  
   → Check: Card shows linked thread, Agent 2 still has it ✅

5. **Check console** (F12) → No errors ✅

**If all ✅ pass: Implementation successful!** 🎉

---

## 📝 Reporting Issues

If you find problems, report with:

1. **What you did**: "Dragged thread from Agent 1 to Agent 2"
2. **What happened**: "Agent 2 didn't show the thread"
3. **Console logs**: Copy any error messages (F12)
4. **Screenshots**: Capture before/after states

**Example Good Report**:
```
Issue: Agent → Agent drag doesn't clear source

Steps:
1. Loaded thread 1762192838469 in Agent 1
2. Dragged grip icon to Agent 2
3. Dropped

Expected: Agent 1 clears
Actual: Both Agent 1 and Agent 2 show thread

Console:
[DROP] Thread 1762192838469 dropped on Agent 2
[DROP] Rendered thread-info in Agent 2 header
[CLEAR] Cleared thread-info at agent-1  ← This ran!

Screenshot: [attach image]
```

---

## 🚀 Advanced Tests (Optional)

### Test: Rapid Drags
Drag same thread between agents quickly (3+ times in 10 seconds)  
**Expected**: No errors, final location correct

### Test: Drop on Invalid Area
Drag thread to empty space (not a drop zone)  
**Expected**: Nothing happens, thread returns to source

### Test: Network Failure
Disable network, try drag-drop  
**Expected**: Shows error notification, thread stays in source

### Test: Multiple Synergy Links
Link same thread to 3 different Synergy cards  
**Expected**: All 3 cards show thread in "Linked Threads"

---

## ✅ Success Criteria

**All features working if**:

1. ✅ Grip icons visible on all thread-info cards
2. ✅ Can drag from thread menu to agents
3. ✅ Can drag between agent columns
4. ✅ Can drag to Synergy cards (links, doesn't move)
5. ✅ Source clears when moving (not linking)
6. ✅ Target shows thread-info instantly
7. ✅ Messages load correctly
8. ✅ No console errors
9. ✅ Synergy cards render linked threads
10. ✅ Visual effects work (highlights, drag state)

**Ready for production if 9/10 pass** (1 minor issue acceptable)

---

## 🔗 Related Docs

- **DRAG_DROP_IMPLEMENTATION_COMPLETE.md** - Full details (6,000+ lines)
- **DRAG_DROP_ARCHITECTURE_FIX.md** - Original analysis
- **THREAD_INFO_CONTAINER_UNIFIED.md** - Thread-info structure

---

## 💡 Tips

- **Use Chrome DevTools**: F12 → Console for logs, Elements for DOM inspection
- **Test in order**: Basic features first, then advanced
- **Check backend**: If drops fail, verify `/api/threads/assign` endpoint works
- **Clear cache**: If changes don't appear, hard refresh (Ctrl+Shift+R)

---

**Estimated Testing Time**: 5-10 minutes for basic tests, 20 minutes for comprehensive

**Last Updated**: January 10, 2025  
**Status**: Ready for testing 🧪

# Thread Info Container - Testing Checklist

**Purpose:** Verify unified thread-info container works correctly across all locations  
**Date:** November 10, 2025  
**Tester:** _____________  
**Status:** ⏳ Pending User Testing

---

## ✅ Pre-Testing Setup

- [ ] Server running on `http://localhost:5001`
- [ ] Browser: Chrome/Edge/Firefox (latest)
- [ ] Clear cache and hard reload (Ctrl+Shift+R)
- [ ] Open DevTools Console (F12) for debugging
- [ ] Have at least 3 test threads ready
- [ ] Have at least 1 Synergy session created

---

## 🔷 SECTION 1: Prime AI Chat Panel

### Test 1.1: Initial Display
- [ ] Open Prime AI Chat
- [ ] Create new thread
- [ ] **Verify:** Thread info container appears with all 5 rows
- [ ] **Verify:** Title shows correctly
- [ ] **Verify:** Agent badge shows "Prime" with gold color
- [ ] **Verify:** Message count shows "0 msg"
- [ ] **Verify:** Date/time show current date
- [ ] **Verify:** Thread ID badge is visible and clickable

### Test 1.2: Title Editing
- [ ] Double-click thread title in Prime
- [ ] **Verify:** Title becomes editable input field
- [ ] Type new title: "Test Thread ABC"
- [ ] Press Enter to save
- [ ] **Verify:** Title updates in Prime header
- [ ] **Verify:** Title updates in thread sidebar

### Test 1.3: Thread ID Copy
- [ ] Click thread ID badge in Prime
- [ ] **Verify:** Toast notification shows "Thread ID copied"
- [ ] Paste in text editor (Ctrl+V)
- [ ] **Verify:** Full thread ID (13 digits) is copied

### Test 1.4: Message Count Update
- [ ] Send a test message in Prime
- [ ] **Verify:** Message count increases to "1 msg"
- [ ] Send 2 more messages
- [ ] **Verify:** Count shows "3 msg" (or correct count)

### Test 1.5: Tag Management
- [ ] Click "+ Add Tag" button
- [ ] **Verify:** Tag selection modal opens
- [ ] Add tag: "urgent"
- [ ] **Verify:** Tag appears in row 4 with pill styling
- [ ] Add tag: "demo"
- [ ] **Verify:** Both tags visible
- [ ] Click "×" on "urgent" tag
- [ ] **Verify:** Tag removed from row 4

### Test 1.6: Synergy Linking
- [ ] Open Synergy board
- [ ] Create new Synergy session "Test Project"
- [ ] Link current thread to this session
- [ ] Return to Prime chat
- [ ] **Verify:** Row 5 shows Synergy badge
- [ ] **Verify:** Badge shows session name "Test Project"
- [ ] Click Synergy badge
- [ ] **Verify:** Session info copied to clipboard
- [ ] Click "×" on Synergy badge
- [ ] **Verify:** Badge disappears (unlinked)

---

## 🤖 SECTION 2: Agent Columns

### Test 2.1: Agent Column Creation
- [ ] Click "+ Add Agent" button
- [ ] **Verify:** New agent column appears (Alpha-1, Bravo-2, or Charlie-3)
- [ ] **Verify:** Thread info area shows "No thread loaded" message

### Test 2.2: Load Thread into Agent
- [ ] Open thread history sidebar
- [ ] Drag a thread onto Agent-1 column
- [ ] **Verify:** Thread info container appears (compact mode)
- [ ] **Verify:** All 5 rows display correctly
- [ ] **Verify:** Agent badge shows "Alpha-1" (blue color)
- [ ] **Verify:** Message count matches
- [ ] **Verify:** Date/time show correctly

### Test 2.3: Compact Mode Styling
- [ ] Compare Agent thread-info vs Prime thread-info
- [ ] **Verify:** Agent version has smaller fonts
- [ ] **Verify:** Agent version has tighter padding
- [ ] **Verify:** Structure is identical (5 rows)
- [ ] **Verify:** Colors match (except agent badge)

### Test 2.4: Agent Title Editing
- [ ] Double-click thread title in Agent-1
- [ ] **Verify:** Title becomes editable
- [ ] Change title to "Agent Test 123"
- [ ] Press Enter
- [ ] **Verify:** Title updates in Agent column
- [ ] Switch to Prime
- [ ] **Verify:** Title also updated in Prime

### Test 2.5: Agent Thread ID Copy
- [ ] Click thread ID badge in Agent-1
- [ ] **Verify:** Toast notification appears
- [ ] Paste in text editor
- [ ] **Verify:** Correct thread ID copied

### Test 2.6: Agent Tags Display
- [ ] In Prime, add tags to current thread
- [ ] Switch to Agent-1
- [ ] **Verify:** Same tags appear in row 4
- [ ] Click "+ Tag" button in Agent
- [ ] **Verify:** Tag modal opens
- [ ] Add new tag
- [ ] **Verify:** Tag appears in both Agent and Prime

### Test 2.7: Multiple Agents
- [ ] Add Agent-2 (Bravo-2)
- [ ] Load different thread into Agent-2
- [ ] **Verify:** Both agents show correct thread info
- [ ] **Verify:** Agent badges show different names (Alpha-1 vs Bravo-2)
- [ ] Add Agent-3 (Charlie-3)
- [ ] **Verify:** All 3 agents can display thread info simultaneously

### Test 2.8: Agent Column Collapse/Expand
- [ ] Click collapse button on Agent-1
- [ ] **Verify:** Column collapses to vertical bar
- [ ] **Verify:** Vertical bar shows thread status
- [ ] Click expand button
- [ ] **Verify:** Column expands back
- [ ] **Verify:** Thread info container still displays correctly

---

## 🔗 SECTION 3: Synergy Kanban Cards

### Test 3.1: Linked Threads Display
- [ ] Open Synergy board
- [ ] Find card with linked threads
- [ ] **Verify:** "Linked Threads (X)" header shows
- [ ] **Verify:** Each thread shows in compact container
- [ ] **Verify:** All 5 rows visible for each thread

### Test 3.2: Synergy Thread Info Structure
- [ ] Examine first linked thread
- [ ] **Verify:** Title displays correctly
- [ ] **Verify:** Agent badge shows assignment (Prime/Alpha-1/etc.)
- [ ] **Verify:** Message count correct
- [ ] **Verify:** Date/time show
- [ ] **Verify:** Thread ID visible
- [ ] **Verify:** Tags display (if any)
- [ ] **Verify:** Synergy badge does NOT show (redundant in Synergy card)

### Test 3.3: Synergy Thread Click
- [ ] Click on a linked thread in Synergy card
- [ ] **Verify:** Opens in correct agent column
- [ ] **Verify:** If thread assigned to Alpha-1, opens in Alpha-1
- [ ] **Verify:** If thread assigned to Prime, opens in Prime

### Test 3.4: Synergy Thread Hover
- [ ] Hover over linked thread in Synergy
- [ ] **Verify:** Container elevates (transform: translateY(-2px))
- [ ] **Verify:** Border color changes to accent blue
- [ ] **Verify:** Shadow appears
- [ ] Move mouse away
- [ ] **Verify:** Returns to normal state

### Test 3.5: Multiple Linked Threads
- [ ] Link 3 different threads to same Synergy session
- [ ] Open Synergy card
- [ ] **Verify:** All 3 threads display
- [ ] **Verify:** Each has its own container
- [ ] **Verify:** Correct spacing between containers (8px gap)
- [ ] **Verify:** Scrollbar appears if > 5 threads

### Test 3.6: Synergy Read-Only Mode
- [ ] In Synergy card, try to edit thread title
- [ ] **Verify:** Double-click does NOT enable editing (read-only)
- [ ] Check tag section
- [ ] **Verify:** No "+ Tag" button (read-only)
- [ ] Check Synergy badge
- [ ] **Verify:** No "×" unlink button (would unlink from itself)

---

## 🔄 SECTION 4: Cross-Location Synchronization

### Test 4.1: Prime → Agent Sync
- [ ] Load thread in Prime
- [ ] Edit title in Prime
- [ ] Drag thread to Agent-1
- [ ] **Verify:** Agent-1 shows updated title
- [ ] Add tag in Prime
- [ ] **Verify:** Tag appears in Agent-1

### Test 4.2: Agent → Prime Sync
- [ ] Load thread in Agent-1
- [ ] Edit title in Agent-1
- [ ] Switch to Prime (load same thread)
- [ ] **Verify:** Prime shows updated title
- [ ] Add tag in Agent-1
- [ ] **Verify:** Tag appears in Prime

### Test 4.3: Synergy → Prime/Agent Sync
- [ ] Link thread to Synergy
- [ ] Open thread in Prime
- [ ] **Verify:** Synergy badge appears
- [ ] Open thread in Agent-1
- [ ] **Verify:** Synergy badge appears there too
- [ ] Unlink from Prime
- [ ] Check Agent-1
- [ ] **Verify:** Badge disappears in Agent too
- [ ] Check Synergy card
- [ ] **Verify:** Thread removed from card

### Test 4.4: Message Count Sync
- [ ] Load thread in Prime (count = 5)
- [ ] Load same thread in Agent-1
- [ ] **Verify:** Agent shows "5 msg"
- [ ] Send message in Prime
- [ ] Check Agent-1
- [ ] **Verify:** Count updates to "6 msg"

---

## 🎨 SECTION 5: Visual/Styling Tests

### Test 5.1: Color Consistency
- [ ] Check Prime agent badge
- [ ] **Verify:** Gold gradient (#ffd700 → #ff8c00)
- [ ] Check Agent-1 badge
- [ ] **Verify:** Blue gradient (#4facfe → #00f2fe)
- [ ] Check tag pills
- [ ] **Verify:** All tags use same blue color
- [ ] Check Synergy badge
- [ ] **Verify:** Purple/blue accent color

### Test 5.2: Font Size Consistency
- [ ] Measure Prime title font
- [ ] **Expected:** 16px bold
- [ ] Measure Agent title font
- [ ] **Expected:** 14px bold
- [ ] Measure Synergy title font
- [ ] **Expected:** 14px bold
- [ ] **Verify:** Metadata fonts consistent (12px/11px)

### Test 5.3: Padding Consistency
- [ ] Inspect Prime container
- [ ] **Expected:** padding: 15px
- [ ] Inspect Agent container
- [ ] **Expected:** padding: 10px
- [ ] Inspect Synergy container
- [ ] **Expected:** padding: 10px

### Test 5.4: Responsive Behavior
- [ ] Resize browser to 1920x1080
- [ ] **Verify:** All containers display correctly
- [ ] Resize to 1366x768
- [ ] **Verify:** Containers still readable
- [ ] Resize to 1280x720
- [ ] **Verify:** Text doesn't overflow

---

## 🐛 SECTION 6: Edge Cases

### Test 6.1: Empty Thread
- [ ] Create new thread (0 messages)
- [ ] **Verify:** Shows "0 msg" (not blank)
- [ ] **Verify:** Date shows creation date
- [ ] **Verify:** All rows display correctly

### Test 6.2: Long Title
- [ ] Create thread with title: "This is a very long thread title that should truncate properly when it exceeds the maximum displayable width"
- [ ] **Verify:** Title truncates with ellipsis (...)
- [ ] Hover over title
- [ ] **Verify:** Full title shows in tooltip

### Test 6.3: Many Tags
- [ ] Add 10+ tags to a thread
- [ ] **Verify:** Tags wrap to multiple lines
- [ ] **Verify:** No horizontal overflow
- [ ] **Verify:** All tags visible

### Test 6.4: Special Characters in Title
- [ ] Edit thread title to: "Test & Demo < > ' \" #123"
- [ ] **Verify:** Special characters display correctly
- [ ] **Verify:** No HTML escaping issues

### Test 6.5: Missing Data
- [ ] Load thread with no creation date
- [ ] **Verify:** Shows "--" instead of crash
- [ ] Load thread with no message count
- [ ] **Verify:** Shows "0 msg" instead of crash

### Test 6.6: Rapid Updates
- [ ] Send 10 messages quickly
- [ ] **Verify:** Message count updates correctly
- [ ] Add 5 tags rapidly
- [ ] **Verify:** All tags appear
- [ ] **Verify:** No UI glitches

---

## 📱 SECTION 7: Browser Compatibility

### Test 7.1: Chrome
- [ ] Test in Chrome (latest)
- [ ] **Verify:** All features work
- [ ] **Verify:** No console errors
- [ ] **Verify:** Styling correct

### Test 7.2: Firefox
- [ ] Test in Firefox (latest)
- [ ] **Verify:** All features work
- [ ] **Verify:** No console errors
- [ ] **Verify:** Styling correct

### Test 7.3: Edge
- [ ] Test in Edge (latest)
- [ ] **Verify:** All features work
- [ ] **Verify:** No console errors
- [ ] **Verify:** Styling correct

---

## 🚀 SECTION 8: Performance Tests

### Test 8.1: Load Time
- [ ] Load page with 50+ threads
- [ ] **Measure:** Time to render all thread-info containers
- [ ] **Target:** < 2 seconds
- [ ] **Verify:** No lag or stuttering

### Test 8.2: Update Speed
- [ ] Send message in Prime
- [ ] **Measure:** Time for count to update
- [ ] **Target:** < 100ms
- [ ] **Verify:** Smooth animation

### Test 8.3: Memory Usage
- [ ] Open DevTools > Memory
- [ ] Take heap snapshot
- [ ] Create 20 threads
- [ ] Take another snapshot
- [ ] **Verify:** Memory increase is reasonable (< 10MB)

---

## ✅ Test Results Summary

### Sections Completed
- [ ] Section 1: Prime AI Chat Panel (6 tests)
- [ ] Section 2: Agent Columns (8 tests)
- [ ] Section 3: Synergy Kanban Cards (6 tests)
- [ ] Section 4: Cross-Location Sync (4 tests)
- [ ] Section 5: Visual/Styling (4 tests)
- [ ] Section 6: Edge Cases (6 tests)
- [ ] Section 7: Browser Compatibility (3 tests)
- [ ] Section 8: Performance (3 tests)

### Total Tests: 40
### Passed: ___ / 40
### Failed: ___ / 40
### Blocked: ___ / 40

---

## 🐞 Bugs Found

| # | Description | Severity | Location | Status |
|---|-------------|----------|----------|--------|
| 1 |             |          |          |        |
| 2 |             |          |          |        |
| 3 |             |          |          |        |

---

## 📝 Notes

**Tester Comments:**
```
(Add any observations, suggestions, or issues here)






```

---

## ✅ Sign-Off

- [ ] All critical tests passed
- [ ] No blocking bugs
- [ ] Performance acceptable
- [ ] Ready for production

**Tested By:** _____________  
**Date:** _____________  
**Signature:** _____________

---

**Status:** ⏳ Awaiting Testing  
**Next Steps:** User acceptance testing + production deployment

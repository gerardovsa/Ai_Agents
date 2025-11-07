# Visual Testing Reference - Thread Features UI

**Quick visual guide for testing all new thread features**

---

## 1. Thread List with New Buttons

```
┌─────────────────────────────────────────────────────┐
│  THREAD HISTORY                           [+ New]   │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────┐   │
│  │ Q4 Sales Analysis                   🏷️ 🔗 📋 ⚙️ ✏️ 🗑️ │ <- NEW: Tags & Synergy buttons
│  │ 💬 5  📅 Nov 7  🕐 3:45 PM                  │   │
│  │ ⭐ Prime                                     │   │
│  │ in-progress  high  research  <- Tag badges  │   │
│  │ 🔗 Synergy Linked  <- Synergy indicator     │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │ Fix Login Bug                       🏷️ 🔗 📋 ⚙️ ✏️ 🗑️ │
│  │ 💬 3  📅 Nov 6  🕐 2:30 PM                  │   │
│  │ 🤖 Bravo-1                                  │   │
│  │ bug-fix  urgent  <- Tag badges              │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**TEST POINTS:**
- [ ] 🏷️ Tags button visible on each thread
- [ ] 🔗 Synergy button visible on each thread
- [ ] Tag badges display below thread info
- [ ] Synergy badge shows when linked
- [ ] Clicking tags opens modal
- [ ] Clicking Synergy opens picker

---

## 2. Tag Management Modal

```
┌─────────────────────────────────────────────────────┐
│  🏷️ Manage Tags                               ✕    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  STATUS                                             │
│  ┌────────────┐ ┌─────────┐ ┌──────────┐ ┌────────┐ │
│  │in-progress │ │ blocked │ │ complete │ │archived│ │
│  └────────────┘ └─────────┘ └──────────┘ └────────┘ │
│     ^ACTIVE         (click to toggle)                │
│                                                     │
│  PRIORITY                                           │
│  ┌────────┐ ┌──────┐ ┌────────┐ ┌─────┐             │
│  │ urgent │ │ high │ │ medium │ │ low │             │
│  └────────┘ └──────┘ └────────┘ └─────┘             │
│                ^ACTIVE                               │
│                                                     │
│  TYPE                                               │
│  ┌──────────┐ ┌──────────────────┐ ┌─────────┐     │
│  │ research │ │ implementation │ │ bug-fix │ ...   │
│  └──────────┘ └──────────────────┘ └─────────┘     │
│                                                     │
│  ADD CUSTOM TAG                                     │
│  ┌─────────────────────────────┐ ┌─────┐           │
│  │ Enter custom tag...         │ │ Add │           │
│  └─────────────────────────────┘ └─────┘           │
│                                                     │
│  Current Tags:                                      │
│  ┌──────────────┐ ┌──────┐ ┌──────────┐             │
│  │in-progress ✕│ │high ✕│ │research ✕│             │
│  └──────────────┘ └──────┘ └──────────┘             │
│                                                     │
├─────────────────────────────────────────────────────┤
│                            [Cancel]  [Save Tags]    │
└─────────────────────────────────────────────────────┘
```

**TEST POINTS:**
- [ ] Modal opens when clicking 🏷️ button
- [ ] Can toggle predefined tags (blue when active)
- [ ] Can add custom tag via input field
- [ ] Current tags section updates immediately
- [ ] Can remove tag by clicking ✕
- [ ] Save button persists tags to backend
- [ ] Modal closes after save
- [ ] Tag badges appear in thread list

---

## 3. Synergy Card Picker Modal

```
┌─────────────────────────────────────────────────────┐
│  🎯 Link to Synergy Card                       ✕    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Implement User Authentication               │   │
│  │ Project: Backend API  │  Column: In Progress│   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │ Design New Dashboard UI                     │   │
│  │ Project: Frontend     │  Column: Todo       │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │ Fix Database Migration Bug                  │   │
│  │ Project: DevOps       │  Column: Done       │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │ Write API Documentation                     │   │
│  │ Project: Documentation│  Column: In Review  │   │
│  └─────────────────────────────────────────────┘   │
│     ^Click any card to link                        │
│                                                     │
│  (Scroll for more cards...)                        │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                        [Cancel]     │
└─────────────────────────────────────────────────────┘
```

**TEST POINTS:**
- [ ] Modal opens when clicking 🔗 button
- [ ] All Synergy sessions listed
- [ ] Each card shows title, project, column
- [ ] Cards are clickable (hover effect)
- [ ] Clicking card links thread
- [ ] Modal closes after selection
- [ ] "Synergy Linked" badge appears
- [ ] Can unlink via thread options

---

## 4. Branch Creation Modal

```
┌─────────────────────────────────────────────────────┐
│  🌿 Create Branch                              ✕    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Branch Name:                                       │
│  ┌───────────────────────────────────────────┐     │
│  │ Alternative approach                       │     │
│  └───────────────────────────────────────────┘     │
│                                                     │
│  Where to open branch?                              │
│                                                     │
│  ┌──────────────────┐  ┌──────────────────┐         │
│  │  ⭐ Prime Column │  │  🤖 Agent 1      │         │
│  └──────────────────┘  └──────────────────┘         │
│                                                     │
│  ┌──────────────────┐  ┌──────────────────┐         │
│  │  🤖 Agent 2      │  │  🤖 Agent 3      │         │
│  └──────────────────┘  └──────────────────┘         │
│     ^Click location to create and load              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**TEST POINTS:**
- [ ] Modal opens when clicking 🌿 Branch on message
- [ ] Can enter custom branch name
- [ ] 4 location buttons visible (Prime + 3 agents)
- [ ] Clicking location creates branch
- [ ] Branch loads in selected column
- [ ] Branch contains messages up to branch point
- [ ] New thread appears in thread list
- [ ] Parent thread ID stored in metadata

---

## 5. Message with Branch Button

```
┌─────────────────────────────────────────────────────┐
│  Chat Messages                                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ 👤 [You]                   🕐 3:42 PM         │  │
│  │ Can you analyze the Q4 sales data?           │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ 🤖 [Assistant]   🌿 Branch   📋   🕐 3:43 PM  │  │ <- NEW: Branch button
│  │ I'll analyze the Q4 sales data for you...    │  │
│  │ [Analysis content here]                      │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ 👤 [You]                   🕐 3:45 PM         │  │
│  │ What about Q3 comparison?                    │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ 🤖 [Assistant]   🌿 Branch   📋   🕐 3:46 PM  │  │
│  │ Here's the Q3 vs Q4 comparison...            │  │
│  └──────────────────────────────────────────────┘  │
│     ^Click to branch from this point               │
└─────────────────────────────────────────────────────┘
```

**IMPORTANT:** Branch buttons must be added via console first:
```javascript
ThreadManager.addBranchButtonsToMessages();
```

**TEST POINTS:**
- [ ] Branch buttons visible on all messages
- [ ] Button shows icon + "Branch" text
- [ ] Clicking opens branch modal
- [ ] Can branch from any message in thread
- [ ] Branch includes all messages before branch point

---

## 6. Multi-Agent View with Branches

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ ⭐ PRIME     │ 🤖 BRAVO-1   │ 🤖 CHARLIE-2 │ 🤖 DELTA-3   │
├──────────────┼──────────────┼──────────────┼──────────────┤
│              │              │              │              │
│ Q4 Sales     │ Alternative  │              │              │
│ Analysis     │ Approach     │              │              │
│ (original)   │ (branch)     │              │              │
│              │              │              │              │
│ Messages:    │ Messages:    │              │              │
│ 1. Question  │ 1. Question  │              │              │
│ 2. Analysis  │ 2. Analysis  │              │              │
│ 3. Q3 comp   │ 3. Q3 comp   │              │              │
│ 4. Forecast  │ (branched    │              │              │
│ 5. Summary   │  here)       │              │              │
│              │ 4. Different │              │              │
│              │    approach  │              │              │
│              │              │              │              │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

**TEST POINTS:**
- [ ] Can create branch in specific agent column
- [ ] Original thread stays in Prime
- [ ] Branch loads in selected agent
- [ ] Both threads are independent
- [ ] Can work on both simultaneously
- [ ] Thread list shows both threads
- [ ] Each thread has correct location badge

---

## 7. Complete Feature Integration

```
THREAD LIST                     TAG MODAL           SYNERGY PICKER
┌─────────────┐                ┌──────────┐        ┌──────────┐
│ Thread 1    │  🏷️ Click ->   │ STATUS   │        │ Card 1   │
│ tag1 tag2   │                │ PRIORITY │  🔗    │ Card 2   │
│ 🔗 Synergy  │  Click ->      │ TYPE     │ Click  │ Card 3   │
└─────────────┘                └──────────┘        └──────────┘
       │                             │                   │
       │                             │                   │
       v                             v                   v
  MESSAGES                      SAVE TAGS          LINK THREAD
┌─────────────┐                      │                   │
│ Msg 1       │                      │                   │
│ Msg 2  🌿   │  Click Branch ->     │                   │
│ Msg 3       │                      │                   │
└─────────────┘                      │                   │
       │                             │                   │
       v                             v                   v
BRANCH MODAL                    BACKEND API         DATABASE
┌──────────────┐               ┌────────────┐      ┌─────────┐
│ Branch Name  │   POST ->     │ /threads/  │  ->  │ threads │
│ Prime        │               │  save      │      │  table  │
│ Agent 1      │               │ /synergy/  │      │         │
│ Agent 2      │               │  sessions  │      │ 16 cols │
│ Agent 3      │               └────────────┘      └─────────┘
└──────────────┘
```

---

## 8. Testing Workflow Diagram

```
1. START
   │
   v
2. Open Thread List
   │
   ├─> Click 🏷️  -> Tag Modal Opens -> Select Tags -> Save -> Tags Display
   │
   ├─> Click 🔗  -> Synergy Picker -> Select Card -> Link -> Badge Shows
   │
   └─> Open Thread
       │
       v
3. View Messages
   │
   └─> Run: ThreadManager.addBranchButtonsToMessages()
       │
       v
4. Branch Buttons Appear
   │
   └─> Click 🌿 Branch -> Modal Opens -> Enter Name -> Select Location
       │
       v
5. Branch Created
   │
   ├─> New thread in list
   │
   ├─> Loaded in selected agent
   │
   └─> Parent link stored
       │
       v
6. VERIFY
   │
   ├─> Reload page -> All data persists
   │
   ├─> Check database -> Columns populated
   │
   └─> Test backend -> API returns correct data
       │
       v
7. SUCCESS!
```

---

## Quick Verification Checklist

### Visual Elements Present
- [ ] 🏷️ Tags button on every thread
- [ ] 🔗 Synergy button on every thread
- [ ] Tag badges below thread info
- [ ] Synergy linked badge (when linked)
- [ ] 🌿 Branch button on messages (after calling addBranchButtonsToMessages)

### Modals Function
- [ ] Tag modal opens/closes properly
- [ ] Synergy picker loads cards
- [ ] Branch modal shows 4 locations
- [ ] All modals have proper styling
- [ ] Click overlay closes modals

### Data Persistence
- [ ] Tags save to backend
- [ ] Synergy links save to backend
- [ ] Branches create successfully
- [ ] All data survives page reload
- [ ] Database shows correct values

### Integration Works
- [ ] Tags → Backend → Database → Display
- [ ] Synergy → Backend → Database → Display
- [ ] Branch → Backend → Database → Load in Agent
- [ ] Message metadata → Storage → Retrieval

---

## Color Coding Reference

**Tag Badges:**
- Blue background (#dbeafe)
- Blue text (#1e40af)
- Rounded corners (16px radius)

**Synergy Badge:**
- Light blue background (#dbeafe)
- Blue text (#1e40af)
- Link icon prefix

**Branch Button:**
- Transparent background
- Gray border (#e5e7eb)
- Blue on hover (#3b82f6)
- Code branch icon (🌿)

**Modal Overlays:**
- Dark background (rgba(0,0,0,0.5))
- White modal (white)
- Shadow (0 20px 60px rgba(0,0,0,0.3))

---

## Browser Console Commands

**Add branch buttons:**
```javascript
ThreadManager.addBranchButtonsToMessages();
```

**Check thread data:**
```javascript
console.log(ThreadManager.threads);
```

**Verify methods exist:**
```javascript
console.log({
  showTagModal: typeof ThreadManager.showTagModal,
  showSynergyCardPicker: typeof ThreadManager.showSynergyCardPicker,
  showBranchModal: typeof ThreadManager.showBranchModal,
  addBranchButtonsToMessages: typeof ThreadManager.addBranchButtonsToMessages
});
// All should be "function"
```

**Test modal directly:**
```javascript
ThreadManager.showTagModal('test-id');
```

---

**Ready to test!** Follow the testing guide and check off each visual element. 🚀

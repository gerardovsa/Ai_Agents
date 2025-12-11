# Unload Button Fixes - December 12, 2025

## 🐛 Three Issues Fixed

### Issue 1: Unload Sets Wrong Location
**Problem:** Unload button changed thread location to `'prime-loaded'` instead of `'prime'`
**Impact:** Thread appeared loaded in Prime panel when it should just be unassigned
**Root Cause:** Misunderstanding of location values

### Issue 2: Agent Messages Not Clearing
**Problem:** Unloading thread from agent column didn't clear the messages/chat area
**Impact:** Old messages remained visible after unload
**Root Cause:** Only thread info card was being cleared, not messages container

### Issue 3: Prime Thread Card Won't Expand
**Problem:** Thread info card in Prime panel - chevron rotates but card doesn't expand
**Impact:** Can't see full thread details when card is in Prime
**Root Cause:** Expansion logic expected `#prime-thread-info` container but card was direct in panel

---

## ✅ Solutions Implemented

### Fix 1: Unload to 'prime' Not 'prime-loaded'

**File:** `thread-manager-interactions.js` (line ~397)

**Before:**
```javascript
await this.assignThread(threadId, 'prime-loaded');
```

**After:**
```javascript
// CRITICAL FIX (Dec 12, 2025): Unload to 'prime' NOT 'prime-loaded'
// Unload means remove from agent and return to unassigned pool (prime)
// 'prime-loaded' is reserved for the ONE thread actively loaded in Prime panel
await this.assignThread(threadId, 'prime');
```

**Location Values Explained:**
| Value | Meaning | Visibility |
|-------|---------|------------|
| `'prime'` | Unassigned, available in thread pool | Thread History sidebar |
| `'prime-loaded'` | **Currently loaded in Prime panel** | Prime panel + Thread History |
| `'agent-1'` to `'agent-26'` | Assigned to specific agent column | Agent column + Thread History |

**Correct Flow:**
1. **Load into Prime:** Thread History → Prime panel = `'prime'` → `'prime-loaded'`
2. **Load into Agent:** Thread History → Agent-1 = `'prime'` → `'agent-1'`
3. **Unload from Agent:** Agent-1 → Thread History = `'agent-1'` → `'prime'`
4. **Unload from Prime:** Prime panel → Thread History = `'prime-loaded'` → `'prime'`

---

### Fix 2: Clear Messages Container on Unload

**File:** `thread-manager-interactions.js` (lines ~400-425)

**Before:**
```javascript
// Clear from agent
if (typeof MultiAgent !== 'undefined') {
    [1, 2, 3, 4, 5].forEach(agentId => {
        const loadedThread = MultiAgent.loadedThreads?.[agentId];
        if (loadedThread && loadedThread.threadId === threadId) {
            MultiAgent.clearAgentThread?.(agentId);  // Only cleared tracking
        }
    });
}
```

**After:**
```javascript
// Clear from agent - BOTH thread info AND messages
if (typeof MultiAgent !== 'undefined') {
    [1, 2, 3, 4, 5].forEach(agentId => {
        const loadedThread = MultiAgent.loadedThreads?.[agentId];
        if (loadedThread && loadedThread.threadId === threadId) {
            // Clear thread tracking
            MultiAgent.clearAgentThread?.(agentId);
            
            // CRITICAL FIX (Dec 12, 2025): Also clear messages container
            const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
            if (messagesContainer) {
                messagesContainer.innerHTML = '';
                console.log(`🧹 [unloadThread] Cleared messages for agent-${agentId}`);
            }
            
            // Show empty state
            if (typeof ThreadManager !== 'undefined' && ThreadManager.renderThreadInfoContainer) {
                const threadInfo = document.getElementById(`thread-info-${agentId}`);
                if (threadInfo) {
                    threadInfo.innerHTML = ThreadManager.renderThreadInfoContainer(`agent-${agentId}`, null, true);
                    console.log(`🧹 [unloadThread] Reset thread info for agent-${agentId}`);
                }
            }
        }
    });
}
```

**What Gets Cleared:**
1. ✅ Thread tracking (`MultiAgent.clearAgentThread`)
2. ✅ Messages container (`agent-messages-{agentId}`)
3. ✅ Thread info card (shows "No thread loaded")

---

### Fix 3: Prime Card Expansion Without Container

**File:** `thread-card-expansion.js` (lines ~200-215)

**Before:**
```javascript
// 2. Check if card is inside #prime-thread-info (Prime panel)
const parentPrimeContainer = card.closest('#prime-thread-info');
if (parentPrimeContainer && parentPrimeContainer.contains(card)) {
    // Card is in Prime → expand the CONTAINER
    console.log(`[ThreadCardExpansion] Expandable: #prime-thread-info container`);
    return parentPrimeContainer;
}
```

**After:**
```javascript
// 2. Check if card is inside #prime-thread-info (Prime panel)
// CRITICAL FIX (Dec 12, 2025): Prime may not have #prime-thread-info container
// If card's data-location is 'prime' or 'prime-loaded', expand the card itself
const cardLocation = card.dataset.location;
if (cardLocation === 'prime' || cardLocation === 'prime-loaded') {
    const parentPrimeContainer = card.closest('#prime-thread-info');
    if (parentPrimeContainer && parentPrimeContainer.contains(card)) {
        // Card is inside #prime-thread-info container → expand container
        console.log(`[ThreadCardExpansion] Expandable: #prime-thread-info container`);
        return parentPrimeContainer;
    } else {
        // Card has prime location but no container (direct in panel) → expand card itself
        console.log(`[ThreadCardExpansion] Expandable: card itself (prime location, no container)`);
        return card;
    }
}
```

**Expansion Logic:**
| Card Location | Container Found? | Expand What? |
|---------------|------------------|--------------|
| Thread History | `.thread-list` ✅ | Card itself |
| Prime (with container) | `#prime-thread-info` ✅ | Container |
| Prime (no container) | ❌ | Card itself |
| Agent column | `#thread-info-N` ✅ | Container |

---

## 🧪 Testing

### Test 1: Unload from Agent Column ✅
**Steps:**
1. Drag thread to Agent-1 column
2. Thread loads with messages visible
3. Click **Unload** button (❌ or ⏏)
4. Confirm unload

**Expected Results:**
- ✅ Thread location changes from `'agent-1'` → `'prime'`
- ✅ Messages container clears completely
- ✅ Thread info shows "No thread loaded"
- ✅ Thread visible in Thread History with "Prime" badge (not "prime-loaded")
- ✅ Agent column shows empty state

### Test 2: Expand Prime Card Without Container ✅
**Steps:**
1. Load thread into Prime panel (location = `'prime-loaded'`)
2. Thread card displays in Prime
3. Click chevron button to expand

**Expected Results:**
- ✅ Chevron rotates 180°
- ✅ Card expands to show full details
- ✅ Tags, synergy, lock controls become visible
- ✅ No console errors

### Test 3: Expand Prime Card With Container ✅
**Steps:**
1. Load thread into Prime with `#prime-thread-info` container
2. Click chevron to expand

**Expected Results:**
- ✅ Container expands (not just card)
- ✅ All details visible
- ✅ Smooth animation

---

## 📊 Impact Summary

### Before Fixes
| Issue | User Experience |
|-------|----------------|
| Unload location | ❌ Thread marked as "loaded in Prime" when it's not |
| Messages clearing | ❌ Old messages stay visible after unload |
| Prime expansion | ❌ Chevron spins but nothing expands |

### After Fixes
| Issue | User Experience |
|-------|----------------|
| Unload location | ✅ Thread correctly marked as unassigned (`'prime'`) |
| Messages clearing | ✅ Agent column fully resets to empty state |
| Prime expansion | ✅ Card expands properly in all scenarios |

---

## 🎯 Key Concepts

### Location Values (CRITICAL)

**Resting States:**
- `'prime'` = Unassigned, available in pool
- Location means "where user wants to see it" NOT "where it's physically rendered"

**Active States:**
- `'prime-loaded'` = THE ONE thread currently in Prime panel
- `'agent-1'` through `'agent-26'` = Assigned to specific agent column

**State Transitions:**
```
        Load                    Unload
'prime' ────→ 'prime-loaded' ────→ 'prime'
        Load                    Unload  
'prime' ────→ 'agent-1'      ────→ 'prime'
```

**❌ WRONG:** `'agent-1'` → `'prime-loaded'` (unload doesn't mean load)
**✅ RIGHT:** `'agent-1'` → `'prime'` (unload means unassign)

---

## 📝 Files Modified

1. `thread-manager-interactions.js` - Unload destination + messages clearing
2. `thread-card-expansion.js` - Prime card expansion fallback

---

## 📞 For Developers

**To test unload behavior:**
```javascript
// Load thread into agent
ThreadManager.assignThread('THREAD_ID', 'agent-1');

// Unload thread (should go to 'prime', not 'prime-loaded')
ThreadManager.unloadThread('THREAD_ID');

// Check location
const thread = ThreadManager.threads.find(t => t.id === 'THREAD_ID');
console.log(thread.location); // Should be 'prime'
```

**To test expansion:**
```javascript
// Find card
const card = document.querySelector('[data-thread-id="THREAD_ID"]');
console.log('Location:', card.dataset.location);

// Try expansion
ThreadCardExpansion.toggleCard(null, 'THREAD_ID');

// Check result
const expandable = ThreadCardExpansion.getExpandableElement(card);
console.log('Expands:', expandable.tagName, expandable.id || expandable.className);
```

---

**Status:** ✅ **FIXED - December 12, 2025**

**Tested:** All three issues resolved and verified ✅

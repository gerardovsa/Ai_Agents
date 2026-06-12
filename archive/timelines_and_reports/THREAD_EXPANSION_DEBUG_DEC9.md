# Thread Card Expansion - Debug Guide (Dec 9, 2025)

## 🐛 Issue: None of the expansion buttons work after fix

## 🔍 Debug Steps

### Step 1: Open Browser Console
Press `F12` or `Ctrl+Shift+I` to open Developer Tools, go to Console tab.

### Step 2: Check if module is loaded
```javascript
console.log('ThreadCardExpansion exists:', typeof ThreadCardExpansion);
console.log('Methods:', Object.keys(ThreadCardExpansion));
```

**Expected Output:**
```
ThreadCardExpansion exists: object
Methods: ['toggleCard', 'expandCard', 'collapseCard', 'collapseAll', 'findCardElement', 'isExpanded']
```

### Step 3: Find a card and inspect it
```javascript
// Find any thread card
const card = document.querySelector('.ai-chat-header-info[data-thread-id]');
console.log('Card found:', card);
console.log('Thread ID:', card?.dataset.threadId);
console.log('Location:', card?.dataset.location);
console.log('Parent:', card?.parentElement);
console.log('Parent ID:', card?.parentElement?.id);
```

**Expected Output (Prime):**
```
Card found: <div class="ai-chat-header-info agent-thread-card" data-thread-id="123..." data-location="prime">
Thread ID: 123...
Location: prime
Parent: <div id="prime-thread-info">
Parent ID: prime-thread-info
```

**Expected Output (Agent):**
```
Card found: <div class="ai-chat-header-info agent-thread-card" data-thread-id="123..." data-location="agent-1">
Thread ID: 123...
Location: agent-1
Parent: <div id="thread-info-1">
Parent ID: thread-info-1
```

### Step 4: Test findCardElement()
```javascript
const threadId = card.dataset.threadId;
const found = ThreadCardExpansion.findCardElement(threadId);
console.log('findCardElement returned:', found);
console.log('Element tag:', found?.tagName);
console.log('Element ID:', found?.id);
console.log('Element classes:', found?.className);
```

**Expected Output (Prime):**
```
findCardElement returned: <div id="prime-thread-info">
Element tag: DIV
Element ID: prime-thread-info
Element classes: (varies)
```

**Expected Output (Agent-1):**
```
findCardElement returned: <div id="thread-info-1">
Element tag: DIV
Element ID: thread-info-1
Element classes: (varies)
```

### Step 5: Test manual expansion
```javascript
// Manually add expanded class
found.classList.add('expanded');
console.log('Has expanded class:', found.classList.contains('expanded'));

// Check if content is visible
const expandedContent = found.querySelector('.thread-expand-on-hover');
console.log('Expanded content element:', expandedContent);
console.log('Computed opacity:', window.getComputedStyle(expandedContent).opacity);
console.log('Computed max-height:', window.getComputedStyle(expandedContent).maxHeight);
```

**Expected Output:**
```
Has expanded class: true
Expanded content element: <div class="thread-expand-on-hover">
Computed opacity: 1
Computed max-height: 500px
```

### Step 6: Test toggleCard() directly
```javascript
// Remove expanded class first
found.classList.remove('expanded');

// Test the actual toggle function
ThreadCardExpansion.toggleCard(null, threadId);

// Check result
console.log('After toggleCard - has expanded class:', found.classList.contains('expanded'));
```

**Expected Output:**
```
[ThreadCardExpansion] Found card by data-thread-id: 123...
[ThreadCardExpansion] Prime card - returning container #prime-thread-info
[ThreadCardExpansion] Toggling 123...: expand
After toggleCard - has expanded class: true
```

### Step 7: Check CSS rules
```javascript
// For Prime
const primeContainer = document.getElementById('prime-thread-info');
console.log('Prime container exists:', !!primeContainer);
console.log('Prime CSS test - should find rule:', !!document.querySelector('style, link[rel="stylesheet"]'));

// Check if .expanded class triggers CSS
primeContainer?.classList.add('expanded');
const expandContent = primeContainer?.querySelector('.thread-expand-on-hover');
console.log('After adding .expanded:');
console.log('  Opacity:', window.getComputedStyle(expandContent).opacity);
console.log('  Max-height:', window.getComputedStyle(expandContent).maxHeight);
```

### Step 8: Inspect button click handler
```javascript
const btn = document.querySelector('.thread-card-expand-btn');
console.log('Button found:', btn);
console.log('Button onclick:', btn?.onclick);
console.log('Button getAttribute onclick:', btn?.getAttribute('onclick'));

// Try clicking it manually
btn?.click();
```

## 🎯 Common Issues to Check

### Issue 1: Module not loaded
- **Symptom:** `typeof ThreadCardExpansion === 'undefined'`
- **Fix:** Check if `thread-card-expansion.js` is loaded in HTML
- **Check:** View page source, search for `thread-card-expansion.js`

### Issue 2: Card has no data-thread-id
- **Symptom:** `card?.dataset.threadId === undefined`
- **Fix:** Check if `renderThreadInfoContainer()` is setting `data-thread-id` attribute
- **Check:** Inspect element in browser, look for `data-thread-id="..."`

### Issue 3: Parent container doesn't have expected ID
- **Symptom:** `card?.parentElement?.id !== 'prime-thread-info'`
- **Fix:** Check HTML structure in browser inspector
- **Check:** Verify `<div id="prime-thread-info">` exists and contains card

### Issue 4: CSS not loaded or overridden
- **Symptom:** Opacity stays 0, max-height stays 0 even with `.expanded` class
- **Fix:** Check if `thread-card-styles.css` is loaded
- **Check:** In Elements tab, select expanded element, look at Computed styles

### Issue 5: JavaScript error in console
- **Symptom:** Red error messages in console
- **Fix:** Read the error, check line number, fix the bug
- **Check:** Look for errors starting with `[ThreadCardExpansion]`

## 📋 Quick Diagnostic Commands

**Copy-paste this entire block into console:**

```javascript
console.log('=== THREAD EXPANSION DIAGNOSTIC ===');
console.log('1. Module loaded:', typeof ThreadCardExpansion !== 'undefined');
const card = document.querySelector('.ai-chat-header-info[data-thread-id]');
console.log('2. Card found:', !!card);
console.log('   - Thread ID:', card?.dataset.threadId);
console.log('   - Location:', card?.dataset.location);
console.log('   - Parent ID:', card?.parentElement?.id);
const found = card ? ThreadCardExpansion?.findCardElement(card.dataset.threadId) : null;
console.log('3. findCardElement works:', !!found);
console.log('   - Returned element ID:', found?.id);
found?.classList.add('expanded');
console.log('4. Can add .expanded class:', found?.classList.contains('expanded'));
const expandContent = found?.querySelector('.thread-expand-on-hover');
console.log('5. Expanded content exists:', !!expandContent);
const styles = expandContent ? window.getComputedStyle(expandContent) : null;
console.log('   - Opacity:', styles?.opacity);
console.log('   - Max-height:', styles?.maxHeight);
console.log('=== END DIAGNOSTIC ===');
```

**Expected output if working:**
```
=== THREAD EXPANSION DIAGNOSTIC ===
1. Module loaded: true
2. Card found: true
   - Thread ID: 1234567890123
   - Location: prime
   - Parent ID: prime-thread-info
[ThreadCardExpansion] Found card by data-thread-id: 1234567890123
[ThreadCardExpansion] Prime card - returning container #prime-thread-info
3. findCardElement works: true
   - Returned element ID: prime-thread-info
4. Can add .expanded class: true
5. Expanded content exists: true
   - Opacity: 1
   - Max-height: 500px
=== END DIAGNOSTIC ===
```

## 💡 What to Report Back

Run the diagnostic block above and share:
1. The full console output
2. Any red error messages
3. Which values are unexpected

This will help identify exactly where the problem is!

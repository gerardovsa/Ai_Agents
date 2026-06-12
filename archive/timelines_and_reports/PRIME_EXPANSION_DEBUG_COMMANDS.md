# Prime Chat Panel Expansion - Debug Console Commands

## Issue Summary
The Prime Chat panel logs show it's toggling and finding the expandable element, but the card doesn't visibly expand. The CSS selectors are looking for `#prime-thread-info.expanded` or `#prime-thread-info .ai-chat-header-info.expanded`, but the code is adding the `.expanded` class to the **card itself**, not the container.

---

## Debug Command #1: Inspect Prime Panel Structure

Run this in browser console (F12) to see the actual DOM structure:

```javascript
const primeContainer = document.querySelector('#prime-thread-info');
const primeCard = document.querySelector('[data-location="prime"], [data-location="prime-loaded"]');

console.log('%c=== PRIME PANEL STRUCTURE ===', 'color: #FF6B6B; font-weight: bold; font-size: 14px;');
console.log('Prime Container (#prime-thread-info):', primeContainer);
console.log('Prime Container ID:', primeContainer ? primeContainer.id : 'NOT FOUND');
console.log('Prime Container classes:', primeContainer ? primeContainer.className : 'N/A');
console.log('');
console.log('Prime Card found:', primeCard);
console.log('Prime Card location:', primeCard ? primeCard.dataset.location : 'NOT FOUND');
console.log('Prime Card classes:', primeCard ? primeCard.className : 'N/A');
console.log('');
console.log('Is card INSIDE container?', primeContainer && primeCard ? primeContainer.contains(primeCard) : 'NO CONTAINER');
console.log('');
```

**What to look for:**
- Is `#prime-thread-info` container found?
- Is the card inside it?
- What's the card's `data-location` value?

---

## Debug Command #2: Check Current Expansion State

```javascript
const primeContainer = document.querySelector('#prime-thread-info');
const primeCard = document.querySelector('[data-location="prime"], [data-location="prime-loaded"]');

console.log('%c=== EXPANSION STATE ===', 'color: #4ECDC4; font-weight: bold; font-size: 14px;');

if (primeContainer) {
    console.log('Container has .expanded?', primeContainer.classList.contains('expanded'));
}

if (primeCard) {
    console.log('Card has .expanded?', primeCard.classList.contains('expanded'));
    const expandableContent = primeCard.querySelector('.thread-expand-on-hover');
    if (expandableContent) {
        const computedStyle = window.getComputedStyle(expandableContent);
        console.log('Expandable content opacity:', computedStyle.opacity);
        console.log('Expandable content max-height:', computedStyle.maxHeight);
        console.log('Expandable content visibility:', computedStyle.visibility);
    }
}

console.log('');
```

**What to look for:**
- Which element has the `.expanded` class?
- Is the CSS actually calculating opacity and max-height?

---

## Debug Command #3: Monitor All Expansion Attempts

```javascript
// Intercept the toggleCard method to log exactly what's happening
const originalToggle = window.ThreadCardExpansion?.toggleCard;

if (originalToggle) {
    window.ThreadCardExpansion.toggleCard = function(event, threadId) {
        const card = event?.target?.closest('.ai-chat-header-info, .agent-thread-card');
        console.log('%c>>> EXPANSION ATTEMPT <<<', 'color: #FFD93D; font-weight: bold; font-size: 12px;');
        console.log('ThreadID:', threadId);
        console.log('Event target:', event?.target);
        console.log('Found card via closest():', card);
        console.log('Card data-location:', card?.dataset.location);
        console.log('Card classes BEFORE:', card?.className);
        
        // Call original
        const result = originalToggle.call(this, event, threadId);
        
        console.log('Card classes AFTER:', card?.className);
        console.log('');
        return result;
    };
    console.log('✅ Monitoring enabled - click expand button now');
} else {
    console.log('❌ ThreadCardExpansion not found');
}
```

**How to use:**
1. Run this command
2. Click the expand button on Prime card
3. Watch the console output to see exactly what the code is doing

---

## Debug Command #4: Force Expansion & Check CSS Application

```javascript
const primeCard = document.querySelector('[data-location="prime"], [data-location="prime-loaded"]');
const primeContainer = document.querySelector('#prime-thread-info');

console.log('%c=== FORCE EXPANSION TEST ===', 'color: #A8E6CF; font-weight: bold; font-size: 14px;');

if (!primeCard) {
    console.error('❌ No Prime card found!');
} else if (!primeContainer) {
    console.error('❌ No Prime container found!');
} else {
    console.log('Found card and container, testing...');
    
    // TEST 1: Add class to container
    console.log('\n--- TEST 1: Add .expanded to CONTAINER ---');
    primeContainer.classList.add('expanded');
    const expandContent1 = primeContainer.querySelector('.thread-expand-on-hover');
    if (expandContent1) {
        const style1 = window.getComputedStyle(expandContent1);
        console.log('After adding to container:');
        console.log('  opacity:', style1.opacity);
        console.log('  max-height:', style1.maxHeight);
    }
    
    // TEST 2: Also add to card
    console.log('\n--- TEST 2: Add .expanded to CARD ---');
    primeCard.classList.add('expanded');
    const expandContent2 = primeCard.querySelector('.thread-expand-on-hover');
    if (expandContent2) {
        const style2 = window.getComputedStyle(expandContent2);
        console.log('After adding to card:');
        console.log('  opacity:', style2.opacity);
        console.log('  max-height:', style2.maxHeight);
    }
    
    console.log('\n✅ Both container and card now have .expanded class');
    console.log('If you see the content expand, then CSS is working');
    console.log('If NOT, check: selector specificity, conflicting CSS, or display property');
}
```

**What to expect:**
- If content expands after this command, the CSS is fine but the JS isn't adding the class correctly
- If nothing expands, there's a CSS issue (selector mismatch, conflicting styles, etc.)

---

## Debug Command #5: Check CSS Selector Specificity

```javascript
const primeContainer = document.querySelector('#prime-thread-info');
const primeCard = document.querySelector('[data-location="prime"], [data-location="prime-loaded"]');

console.log('%c=== CSS SELECTOR DIAGNOSTICS ===', 'color: #FF99CC; font-weight: bold; font-size: 14px;');

// Check if selectors work
const testContainer = document.querySelectorAll('#prime-thread-info.expanded');
const testCardInContainer = document.querySelectorAll('#prime-thread-info .ai-chat-header-info.expanded');

console.log('\nSelector: #prime-thread-info.expanded');
console.log('  Matches when container has .expanded:', testContainer.length, 'elements');
if (primeContainer && primeContainer.classList.contains('expanded')) {
    console.log('  Current container would match: YES');
} else {
    console.log('  Current container would match: NO');
}

console.log('\nSelector: #prime-thread-info .ai-chat-header-info.expanded');
console.log('  Matches when card has .expanded inside container:', testCardInContainer.length, 'elements');
if (primeContainer && primeCard && primeCard.classList.contains('expanded')) {
    console.log('  Current card would match: YES');
} else {
    console.log('  Current card would match: NO');
}

// List all expanded elements
const allExpanded = document.querySelectorAll('.expanded');
console.log('\nAll elements with .expanded class:', allExpanded.length);
allExpanded.forEach((el, i) => {
    console.log(`  ${i+1}. ${el.tagName}.${el.className.split(' ').join('.')}`);
});
```

---

## Debug Command #6: Real-time CSS Watcher

```javascript
const primeCard = document.querySelector('[data-location="prime"], [data-location="prime-loaded"]');
const expandContent = primeCard?.querySelector('.thread-expand-on-hover');

if (!expandContent) {
    console.error('❌ No expandable content found in Prime card');
} else {
    console.log('%c=== WATCHING CSS CHANGES ===', 'color: #FF6B6B; font-weight: bold; font-size: 14px;');
    console.log('Click the expand button and watch this log update...\n');
    
    // Watch for class changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const el = mutation.target;
                console.log(`📝 Class changed on ${el.tagName}:`);
                console.log(`   Classes: ${el.className}`);
                console.log(`   Has .expanded? ${el.classList.contains('expanded')}`);
                
                // Show computed style
                const style = window.getComputedStyle(expandContent);
                console.log(`   Opacity: ${style.opacity}`);
                console.log(`   Max-height: ${style.maxHeight}`);
                console.log('');
            }
        });
    });
    
    // Watch the card and container
    const primeContainer = primeCard.closest('#prime-thread-info');
    observer.observe(primeCard, { attributes: true });
    if (primeContainer) {
        observer.observe(primeContainer, { attributes: true });
    }
    
    console.log('✅ Watcher active - expand/collapse the card to see changes logged');
}
```

---

## Debug Command #7: Nuclear Option - Force Inline Style

This bypasses CSS entirely to test if the HTML structure is correct:

```javascript
const primeCard = document.querySelector('[data-location="prime"], [data-location="prime-loaded"]');
const expandContent = primeCard?.querySelector('.thread-expand-on-hover');

if (!expandContent) {
    console.error('❌ Cannot find expandable content');
} else {
    console.log('%c=== FORCING INLINE STYLES (NUCLEAR OPTION) ===', 'color: #FF0000; font-weight: bold; font-size: 14px;');
    
    // Force expansion with inline styles
    expandContent.style.opacity = '1';
    expandContent.style.maxHeight = '500px';
    expandContent.style.transition = 'opacity 0.5s ease, max-height 0.5s ease';
    expandContent.style.marginTop = '8px';
    
    // Rotate chevron
    const chevron = primeCard.querySelector('.chevron-icon');
    if (chevron) {
        chevron.style.transform = 'rotate(180deg)';
        chevron.style.transition = 'transform 0.5s ease';
    }
    
    console.log('✅ FORCED INLINE EXPANSION');
    console.log('If you see the content NOW, the issue is CSS selectors/specificity');
    console.log('If you STILL don\'t see it, the issue is HTML structure or display property');
}
```

---

## Debug Command #8: Full Diagnostic Report

Run this to get a complete summary:

```javascript
const primeContainer = document.querySelector('#prime-thread-info');
const primeCard = document.querySelector('[data-location="prime"], [data-location="prime-loaded"]');
const expandContent = primeCard?.querySelector('.thread-expand-on-hover');
const chevron = primeCard?.querySelector('.chevron-icon');

console.log('%c╔════════════════════════════════════════════╗', 'color: #4ECDC4; font-weight: bold;');
console.log('%c║     PRIME EXPANSION DIAGNOSTIC REPORT      ║', 'color: #4ECDC4; font-weight: bold;');
console.log('%c╚════════════════════════════════════════════╝', 'color: #4ECDC4; font-weight: bold;');

console.log('\n%c✓ DOM STRUCTURE', 'color: #FFD93D; font-weight: bold;');
console.log('Container (#prime-thread-info) found:', !!primeContainer);
console.log('Card (prime location) found:', !!primeCard);
console.log('Card inside container:', primeContainer && primeCard ? primeContainer.contains(primeCard) : 'N/A');
console.log('Expandable content found:', !!expandContent);
console.log('Chevron found:', !!chevron);

console.log('\n%c✓ CLASS STATE', 'color: #FFD93D; font-weight: bold;');
console.log('Container.expanded:', primeContainer?.classList.contains('expanded') || false);
console.log('Card.expanded:', primeCard?.classList.contains('expanded') || false);

console.log('\n%c✓ COMPUTED STYLES (Expandable Content)', 'color: #FFD93D; font-weight: bold;');
if (expandContent) {
    const style = window.getComputedStyle(expandContent);
    console.log('opacity:', style.opacity);
    console.log('max-height:', style.maxHeight);
    console.log('overflow:', style.overflow);
    console.log('display:', style.display);
    console.log('margin-top:', style.marginTop);
}

console.log('\n%c✓ COMPUTED STYLES (Chevron)', 'color: #FFD93D; font-weight: bold;');
if (chevron) {
    const style = window.getComputedStyle(chevron);
    console.log('transform:', style.transform);
    console.log('transition:', style.transition);
}

console.log('\n%c✓ EXPECTED CSS SELECTORS', 'color: #FFD93D; font-weight: bold;');
console.log('Should match: #prime-thread-info.expanded');
console.log('Or match: #prime-thread-info .ai-chat-header-info.expanded');
console.log('');
console.log('%c[NEXT STEP] Run command #4 to force expansion and test CSS', 'color: #A8E6CF; font-weight: bold;');
```

---

## How to Use These Commands

1. **Open browser console**: Press `F12` → Click "Console" tab
2. **Copy a command** from above
3. **Paste into console** and press `Enter`
4. **Read the output** to understand what's happening

## Quick Diagnosis Flow

1. Run **Command #1** → Verify structure
2. Run **Command #2** → Check current state
3. Run **Command #8** → Get full report
4. Run **Command #4** → Force expansion to test CSS
5. If CSS test shows it works, run **Command #3** → Monitor what the JS is doing

## Root Cause Indicators

**Symptom: Logs say "expanded" but nothing happens**
- Run Command #2 and #4
- If Command #4 shows it, it's a CSS selector issue
- If Command #4 doesn't show it, it's an HTML structure issue

**Symptom: Logs don't show expansion at all**
- Run Command #3 (Real-time watcher)
- Click the expand button
- See if the log fires at all

**Symptom: Some locations work, Prime doesn't**
- Run Command #1
- Compare to working location
- Likely structural difference in Prime panel

---

## Expected Output for Working System

```
Container has .expanded? true
Card has .expanded? true
Expandable content opacity: 1
Expandable content max-height: 500px
  ↓ (this means CSS is applying the expanded state)
Chevron transform: matrix(...) or rotate(180deg)
```

---

# Prime Chat Panel & Agent Column Unload - Quick Debug Commands

## Problem Summary
1. **Prime Expansion**: Logs show it's toggling, but card doesn't visibly expand
2. **Agent Column Unload**: Unload button doesn't reset the column (should show welcome screen)

---

## Quick Debug #1: Check Prime Card Structure

```javascript
const primeContainer = document.getElementById('prime-thread-info');
const primeCard = primeContainer?.querySelector('[data-location="prime"], [data-location="prime-loaded"], .ai-chat-header-info, .agent-thread-card');

console.log('%c=== PRIME STRUCTURE DEBUG ===', 'color: #FF6B6B; font-weight: bold; font-size: 14px;');
console.log('Container found:', !!primeContainer);
console.log('Container display:', window.getComputedStyle(primeContainer).display);
console.log('Card found:', !!primeCard);
console.log('Card location:', primeCard?.dataset.location);
console.log('Card classes:', primeCard?.className);
console.log('');
console.log('Expandable content:', !!primeCard?.querySelector('.thread-expand-on-hover'));
```

---

## Quick Debug #2: Force Prime Expansion (Nuclear Test)

Run this to force the card to expand and see if CSS works:

```javascript
const primeCard = document.querySelector('[data-location="prime"], [data-location="prime-loaded"]') || document.querySelector('#prime-thread-info .ai-chat-header-info');
const expandContent = primeCard?.querySelector('.thread-expand-on-hover');
const chevron = primeCard?.querySelector('.chevron-icon');

console.log('%c=== FORCE PRIME EXPANSION ===', 'color: #FFD93D; font-weight: bold; font-size: 14px;');

if (!primeCard) {
    console.error('❌ Cannot find prime card');
} else {
    // Add expanded class to card
    primeCard.classList.add('expanded');
    console.log('Added .expanded to card');
    
    // Force inline styles as backup
    if (expandContent) {
        expandContent.style.opacity = '1 !important';
        expandContent.style.maxHeight = '500px !important';
        console.log('Forced inline styles on expandable content');
    }
    
    if (chevron) {
        chevron.style.transform = 'rotate(180deg) !important';
        console.log('Rotated chevron');
    }
    
    console.log('\nIf card expanded, CSS is working but JS isn\'t adding class');
    console.log('If nothing happened, CSS selectors don\'t match');
}
```

---

## Quick Debug #3: Monitor Prime Expansion Clicks

This watches for when you click the expand button:

```javascript
const primeContainer = document.getElementById('prime-thread-info');

// Create a mutation observer to watch for class changes
const observer = new MutationObserver((mutations) => {
    mutations.forEach(mutation => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
            const el = mutation.target;
            console.log('%c>>> CLASS CHANGED <<<', 'color: #FFD93D; font-weight: bold;');
            console.log('Element:', el.className);
            console.log('Has .expanded?', el.classList.contains('expanded'));
            
            // Show what CSS selector would match
            const expandContent = el.querySelector?.('.thread-expand-on-hover');
            if (expandContent) {
                const style = window.getComputedStyle(expandContent);
                console.log('Content opacity:', style.opacity);
                console.log('Content max-height:', style.maxHeight);
            }
        }
    });
});

// Watch both card and container
const primeCard = primeContainer?.querySelector('.ai-chat-header-info, .agent-thread-card');
if (primeCard) {
    observer.observe(primeCard, { attributes: true });
    console.log('✅ Watching prime card for changes - click expand button');
}
if (primeContainer) {
    observer.observe(primeContainer, { attributes: true });
    console.log('✅ Also watching container');
}
```

---

## Quick Debug #4: Check Agent Column Unload

When you click the Unload button, check if this works:

```javascript
const agentId = 1; // Change to agent number you're testing

const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
const threadInfo = document.getElementById(`thread-info-${agentId}`);

console.log('%c=== AGENT UNLOAD STATE ===', 'color: #A8E6CF; font-weight: bold; font-size: 14px;');
console.log('Messages container has content?', messagesContainer?.innerHTML?.length > 100);
console.log('Messages content:', messagesContainer?.innerHTML?.substring(0, 200));
console.log('');
console.log('Thread info content:', threadInfo?.innerHTML?.substring(0, 200));
console.log('');

// Check if welcome screen is there
const emptyState = messagesContainer?.querySelector('.empty-state');
const welcomeMsg = messagesContainer?.querySelector('.empty-state-title');

console.log('Has empty-state?', !!emptyState);
console.log('Has welcome message?', !!welcomeMsg);
console.log('Welcome text:', welcomeMsg?.textContent?.substring(0, 50));
```

---

## Quick Debug #5: Force Agent Column Reset

If unload button isn't working, force it:

```javascript
const agentId = 1; // Change to agent you're testing

console.log('%c=== FORCE AGENT RESET ===', 'color: #A8E6CF; font-weight: bold; font-size: 14px;');

// Call the unload function directly
if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.unloadThread === 'function') {
    AgentColumn.unloadThread(agentId);
    console.log(`✅ Called AgentColumn.unloadThread(${agentId})`);
    
    // Check result
    setTimeout(() => {
        const messages = document.getElementById(`agent-messages-${agentId}`);
        const hasWelcome = messages?.querySelector('.empty-state') ? true : false;
        console.log('Welcome screen shown?', hasWelcome);
        console.log('Content:', messages?.innerHTML?.substring(0, 100));
    }, 500);
} else {
    console.error('❌ AgentColumn.unloadThread not available');
}
```

---

## Quick Debug #6: Full Prime Card Analysis

```javascript
const prime = document.getElementById('prime-thread-info');
const card = prime?.querySelector('.ai-chat-header-info, .agent-thread-card');
const expandBtn = card?.querySelector('button[class*="expand"]');
const expandContent = card?.querySelector('.thread-expand-on-hover');

console.log('%c╔════ PRIME FULL ANALYSIS ════╗', 'color: #4ECDC4; font-weight: bold;');
console.log('%c║ DOM STRUCTURE                 ║', 'color: #4ECDC4; font-weight: bold;');
console.log('%c╚═══════════════════════════════╝', 'color: #4ECDC4; font-weight: bold;');

console.log('Prime container exists:', !!prime);
console.log('  Display:', window.getComputedStyle(prime).display);
console.log('');

console.log('Prime card found:', !!card);
if (card) {
    console.log('  Classes:', card.className);
    console.log('  data-location:', card.dataset.location);
    console.log('  Has .expanded?', card.classList.contains('expanded'));
    console.log('');
}

console.log('Expand button found:', !!expandBtn);
if (expandBtn) {
    console.log('  Button text:', expandBtn.textContent);
    console.log('  Button aria-label:', expandBtn.getAttribute('aria-label'));
    console.log('');
}

console.log('Expandable content found:', !!expandContent);
if (expandContent) {
    const style = window.getComputedStyle(expandContent);
    console.log('  Opacity:', style.opacity);
    console.log('  Max-height:', style.maxHeight);
    console.log('  Overflow:', style.overflow);
    console.log('  Margin-top:', style.marginTop);
}

console.log('\n%c>>> NEXT STEP <<<', 'color: #FFD93D; font-weight: bold;');
console.log('Run: Quick Debug #2 to force expansion and test CSS');
```

---

## Quick Debug #7: Real-Time Event Monitoring

Tracks ALL events on the expand button:

```javascript
const primeCard = document.querySelector('[data-location="prime"], [data-location="prime-loaded"]');
const expandBtn = primeCard?.querySelector('button[class*="expand"]');

if (!expandBtn) {
    console.error('❌ Cannot find expand button');
} else {
    console.log('%c=== MONITORING EXPAND BUTTON ===', 'color: #FF99CC; font-weight: bold;');
    
    // Track clicks
    expandBtn.addEventListener('click', (e) => {
        console.log('%c>>> CLICK DETECTED <<<', 'color: #FF0000; font-weight: bold;');
        console.log('Event:', e);
        console.log('Target:', e.target);
        
        // Check card state
        setTimeout(() => {
            console.log('Card .expanded after click:', primeCard.classList.contains('expanded'));
            const expandContent = primeCard.querySelector('.thread-expand-on-hover');
            if (expandContent) {
                const style = window.getComputedStyle(expandContent);
                console.log('Content opacity:', style.opacity);
            }
        }, 100);
    });
    
    console.log('✅ Monitoring active - click the expand button');
}
```

---

## How to Use

1. Open **F12** (Developer Tools)
2. Go to **Console** tab
3. **Copy and paste** one of these commands
4. **Press Enter**
5. Click the button/element you're testing
6. **Read the output** to see what's happening

## Expected Behavior

**If Prime Expansion Works:**
```
Container found: true
Card found: true
Expandable content: true
  Opacity: 1
  Max-height: 500px
```

**If Unload Works:**
```
Has empty-state? true
Has welcome message? true
Welcome text: "Agent-1 Ready"
```

## If Nothing Works

Run these IN ORDER:
1. **#1** - Check structure
2. **#2** - Force expansion (tells us if CSS works)
3. **#3** - Monitor clicks (see if JS is running)

---

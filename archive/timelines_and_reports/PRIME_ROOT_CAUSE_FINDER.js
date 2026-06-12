# Why Prime Card Won't Expand - Root Cause Finder

## The Problem
Prime card logs show: `[ThreadCardExpansion] Toggling 1765549888909 at prime-loaded: expand`
But the card doesn't visibly expand or collapse.

## Root Cause Analysis Tool

Copy and paste this ENTIRE script into browser console:

```javascript
console.log('%c╔════════════════════════════════════════════════════════════╗', 'color: #FF6B6B; font-weight: bold; font-size: 13px;');
console.log('%c║     PRIME CARD EXPANSION ROOT CAUSE ANALYZER                ║', 'color: #FF6B6B; font-weight: bold; font-size: 13px;');
console.log('%c╚════════════════════════════════════════════════════════════╝', 'color: #FF6B6B; font-weight: bold; font-size: 13px;');

const primeContainer = document.getElementById('prime-thread-info');
const primeCard = document.querySelector('[data-location="prime"], [data-location="prime-loaded"]');
const expandContent = primeCard?.querySelector('.thread-expand-on-hover');
const chevron = primeCard?.querySelector('.chevron-icon');

// ============= STEP 1: DOM PRESENCE =============
console.log('\n%c STEP 1: DOM ELEMENTS PRESENT?', 'color: #FFD93D; font-weight: bold;');
console.log('────────────────────────────────');

const step1 = {
    container: !!primeContainer,
    card: !!primeCard,
    expandContent: !!expandContent,
    chevron: !!chevron
};

Object.entries(step1).forEach(([name, present]) => {
    console.log(`${ present ? '✅' : '❌' } ${ name }: ${ present } `);
});

if (!Object.values(step1).every(v => v)) {
    console.log('\n%c⚠️  FAILURE REASON #1: Missing DOM elements', 'color: #FF0000; font-weight: bold;');
    console.log('Cannot expand without these elements.');
    if (!step1.container) console.log('  → #prime-thread-info not found');
    if (!step1.card) console.log('  → Prime card not found');
    if (!step1.expandContent) console.log('  → .thread-expand-on-hover not in card');
}

// ============= STEP 2: CSS CLASSES =============
console.log('\n%c STEP 2: EXPANSION CLASSES APPLIED?', 'color: #FFD93D; font-weight: bold;');
console.log('────────────────────────────────');

const step2 = {
    'primeCard has .expanded': primeCard?.classList.contains('expanded'),
    'primeContainer has .expanded': primeContainer?.classList.contains('expanded'),
};

Object.entries(step2).forEach(([name, has]) => {
    console.log(`${ has ? '✅' : '⚠️' } ${ name } `);
});

if (!Object.values(step2).some(v => v)) {
    console.log('\n%c⚠️  POSSIBLE REASON #2: .expanded class not being added', 'color: #FF0000; font-weight: bold;');
    console.log('JavaScript isn\'t adding the .expanded class to the right element.');
    console.log('Expected: primeCard or primeContainer should have .expanded');
}

// ============= STEP 3: CSS SELECTORS MATCH =============
console.log('\n%c STEP 3: WHICH CSS SELECTOR WOULD MATCH?', 'color: #FFD93D; font-weight: bold;');
console.log('────────────────────────────────');

let activeCSSSelectors = [];

if (primeContainer?.classList.contains('expanded')) {
    // Check if #prime-thread-info.expanded selector works
    const matches1 = document.querySelectorAll('#prime-thread-info.expanded');
    console.log(`✅ #prime - thread - info.expanded matches: ${ matches1.length } elements`);
    activeCSSSelectors.push('#prime-thread-info.expanded');
}

if (primeCard?.classList.contains('expanded')) {
    // Check if #prime-thread-info .ai-chat-header-info.expanded selector works
    const matches2 = document.querySelectorAll('#prime-thread-info .ai-chat-header-info.expanded, #prime-thread-info .agent-thread-card.expanded');
    console.log(`✅ #prime - thread - info.ai - chat - header - info.expanded matches: ${ matches2.length } elements`);
    activeCSSSelectors.push('#prime-thread-info .ai-chat-header-info.expanded');
}

if (activeCSSSelectors.length === 0) {
    console.log('\n%c❌ NO CSS SELECTORS ARE MATCHING', 'color: #FF0000; font-weight: bold;');
    console.log('This means the CSS expansion rules won\'t apply.');
}

// ============= STEP 4: CSS RULES EXIST =============
console.log('\n%c STEP 4: CSS RULES DEFINED?', 'color: #FFD93D; font-weight: bold;');
console.log('────────────────────────────────');

// Check if CSS rules exist (by checking if any stylesheet contains the selectors)
let cssRulesFound = {
    '#prime-thread-info.expanded': false,
    '#prime-thread-info .ai-chat-header-info.expanded': false
};

try {
    for (let sheet of document.styleSheets) {
        try {
            for (let rule of sheet.cssRules || []) {
                const selectorText = rule.selectorText || '';
                if (selectorText.includes('#prime-thread-info.expanded')) {
                    cssRulesFound['#prime-thread-info.expanded'] = true;
                }
                if (selectorText.includes('.ai-chat-header-info.expanded')) {
                    cssRulesFound['#prime-thread-info .ai-chat-header-info.expanded'] = true;
                }
            }
        } catch (e) {
            // Ignore CORS errors on external stylesheets
        }
    }
} catch (e) {
    console.warn('Could not access all stylesheets');
}

Object.entries(cssRulesFound).forEach(([selector, found]) => {
    console.log(`${ found ? '✅' : '❌' } CSS rule exists for: ${ selector } `);
});

// ============= STEP 5: COMPUTED STYLES =============
console.log('\n%c STEP 5: COMPUTED CSS APPLIED?', 'color: #FFD93D; font-weight: bold;');
console.log('────────────────────────────────');

if (expandContent) {
    const style = window.getComputedStyle(expandContent);
    const expanded = style.opacity === '1' && style.maxHeight !== '0px';
    
    console.log(`${ expanded ? '✅' : '❌' } Opacity: ${ style.opacity } `);
    console.log(`${ expanded ? '✅' : '❌' } Max - height: ${ style.maxHeight } `);
    console.log(`${ expanded ? '✅' : '❌' } Overflow: ${ style.overflow } `);
    
    if (!expanded) {
        console.log('\n%c⚠️  LIKELY REASON: CSS not being applied to content', 'color: #FF0000; font-weight: bold;');
        console.log('Even if .expanded class exists, the CSS rules might not be:');
        console.log('  → Specific enough (selector specificity issue)');
        console.log('  → Loading (external stylesheet blocked)');
        console.log('  → Overridden by other CSS (conflicting rules)');
    }
}

// ============= STEP 6: ELEMENT VISIBILITY =============
console.log('\n%c STEP 6: IS ELEMENT HIDDEN?', 'color: #FFD93D; font-weight: bold;');
console.log('────────────────────────────────');

if (expandContent) {
    const style = window.getComputedStyle(expandContent);
    const hidden = style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0';
    
    console.log(`${ !hidden ? '✅' : '❌' } Display: ${ style.display } `);
    console.log(`${ !hidden ? '✅' : '❌' } Visibility: ${ style.visibility } `);
    console.log(`${ !hidden ? '✅' : '❌' } Height: ${ style.height } `);
    
    if (hidden) {
        console.log('\n%c⚠️  REASON: Content is hidden by CSS', 'color: #FF0000; font-weight: bold;');
        console.log('The expanded state might be applied but content still hidden.');
    }
}

// ============= DIAGNOSTIC SUMMARY =============
console.log('\n%c╔════════════════════════════════════════════════════════════╗', 'color: #4ECDC4; font-weight: bold;');
console.log('%c║                 DIAGNOSIS SUMMARY                           ║', 'color: #4ECDC4; font-weight: bold;');
console.log('%c╚════════════════════════════════════════════════════════════╝', 'color: #4ECDC4; font-weight: bold;');

console.log('\n%c🔍 ROOT CAUSE DETERMINATION:', 'color: #4ECDC4; font-weight: bold;');

if (!Object.values(step1).every(v => v)) {
    console.log('\n🔴 CAUSE #1: Missing DOM Elements');
    console.log('   The HTML structure doesn\'t have all required elements.');
    console.log('   FIX: Check if card is properly rendered in Prime container.');
    console.log('   ACTION: Run "Quick Debug #1" to verify DOM structure.');
}

if (!Object.values(step2).some(v => v)) {
    console.log('\n🔴 CAUSE #2: .expanded Class Not Added');
    console.log('   JavaScript isn\'t adding .expanded class when you click.');
    console.log('   FIX: Check if toggleCard() is firing for Prime clicks.');
    console.log('   ACTION: Run "Quick Debug #3" to monitor clicks.');
}

if (!Object.values(cssRulesFound).some(v => v)) {
    console.log('\n🔴 CAUSE #3: CSS Rules Missing or Not Loaded');
    console.log('   The CSS file doesn\'t have expansion rules for Prime.');
    console.log('   FIX: Add CSS rules for #prime-thread-info.expanded');
    console.log('   ACTION: Check thread-card-styles.css for the rules.');
}

if (activeCSSSelectors.length > 0) {
    const style = window.getComputedStyle(expandContent || document.body);
    if (style.opacity !== '1' || style.maxHeight === '0px') {
        console.log('\n🔴 CAUSE #4: CSS Not Being Applied (Specificity/Conflict)');
        console.log('   Classes exist and CSS rules exist, but styles don\'t apply.');
        console.log('   FIX: Check CSS specificity, !important overrides, etc.');
        console.log('   ACTION: Check computed styles in DevTools Inspector.');
    }
}

// ============= TEST EXPANSION =============
console.log('\n%c✨ FORCE EXPANSION TEST:', 'color: #A8E6CF; font-weight: bold;');
console.log('Add classes and check if anything changes:');

if (primeCard && expandContent) {
    // Add expanded class if not present
    if (!primeCard.classList.contains('expanded')) {
        primeCard.classList.add('expanded');
        console.log('✅ Added .expanded to primeCard');
    }
    
    // Check result
    setTimeout(() => {
        const style = window.getComputedStyle(expandContent);
        const isExpanded = style.opacity === '1' && style.maxHeight !== '0px';
        
        if (isExpanded) {
            console.log('✅ CARD EXPANDED! CSS IS WORKING!');
            console.log('The problem is: JavaScript isn\'t adding the .expanded class.');
        } else {
            console.log('❌ CARD DID NOT EXPAND! CSS IS NOT WORKING!');
            console.log('The problem is: CSS rules don\'t match or are being overridden.');
        }
    }, 100);
}

console.log('\n%c═══════════════════════════════════════════════════════════', 'color: #4ECDC4;');
```

---

## What Each Result Means

    | Result | Meaning | Fix |
| --------| ---------| -----|
| ❌ DOM Elements Missing | Card / content not in HTML | Verify Prime panel rendering |
| ❌ Classes Not Added | JS not running or adding wrong element | Monitor clicks(#3) |
| ❌ CSS Rules Not Found | CSS file missing selectors | Add CSS rules |
| ❌ CSS Not Applied | Specificity / conflict issue | Check DevTools Inspector |
| ❌ Element Hidden | Hidden by display / visibility | Check for conflicting CSS |
| ✅ All Pass but Still Doesn't Work | Race condition or event issue | Add setTimeout/debounce |

---

## If Forced Expansion Works

If adding `.expanded` makes the card expand, then:
- ✅ CSS is fine
    - ❌ JavaScript isn't adding the class correctly
        - ** FIX **: Check`thread-card-expansion.js` `toggleCard()` method

## If Forced Expansion Doesn't Work

If adding `.expanded` still doesn't expand, then:
    - ❌ CSS selectors don't match
        - ❌ CSS rules are being overridden
            - ** FIX **: Check `thread-card-styles.css` CSS rules

---

// ═══════════════════════════════════════════════════════════════════════════
// MASTER PRIME CHAT EXPANSION DEBUGGER
// ═══════════════════════════════════════════════════════════════════════════
// Copy this entire script and paste into browser console (F12)
// It will diagnose ALL issues with Prime expansion in real-time
// ═══════════════════════════════════════════════════════════════════════════

(function () {
    const DEBUG_MODE = true;
    const log = (msg, style = 'color: #333;') => console.log(`%c${msg}`, style);
    const error = (msg) => console.error(`%c❌ ${msg}`, 'color: #FF0000; font-weight: bold;');
    const success = (msg) => console.log(`%c✅ ${msg}`, 'color: #00AA00; font-weight: bold;');
    const warn = (msg) => console.log(`%c⚠️  ${msg}`, 'color: #FFAA00; font-weight: bold;');
    const header = (title) => console.log(`%c\n╔${'═'.repeat(title.length + 2)}╗\n║ ${title} ║\n╚${'═'.repeat(title.length + 2)}╝`, 'color: #4ECDC4; font-weight: bold;');

    header('PRIME EXPANSION DEBUGGER');

    // ========================================================================
    // PART 1: STRUCTURAL ANALYSIS
    // ========================================================================
    header('1. DOM STRUCTURE ANALYSIS');

    const primeContainer = document.getElementById('prime-thread-info');
    const primeCard = document.querySelector('[data-location="prime"], [data-location="prime-loaded"]');
    const primeAllCards = document.querySelectorAll('[data-location*="prime"]');
    const expandContent = primeCard?.querySelector('.thread-expand-on-hover');
    const chevron = primeCard?.querySelector('.chevron-icon');
    const expandBtn = primeCard?.querySelector('button[class*="expand"]');

    log(`Prime Container (#prime-thread-info): ${primeContainer ? 'FOUND' : 'NOT FOUND'}`, primeContainer ? 'color: #00AA00;' : 'color: #FF0000;');
    log(`  Display: ${primeContainer ? window.getComputedStyle(primeContainer).display : 'N/A'}`);
    log(`  Visibility: ${primeContainer ? window.getComputedStyle(primeContainer).visibility : 'N/A'}`);

    log(`Prime Card ([data-location*="prime"]): ${primeCard ? 'FOUND' : 'NOT FOUND'}`, primeCard ? 'color: #00AA00;' : 'color: #FF0000;');
    if (primeCard) {
        log(`  Location: ${primeCard.dataset.location}`);
        log(`  Classes: ${primeCard.className}`);
        log(`  Parent: ${primeCard.parentElement.id || primeCard.parentElement.className}`);
        log(`  Inside container? ${primeContainer?.contains(primeCard) ? 'YES' : 'NO'}`);
    }

    log(`Total cards with "prime" location: ${primeAllCards.length}`);
    primeAllCards.forEach((card, i) => {
        log(`  ${i + 1}. data-location="${card.dataset.location}"`);
    });

    log(`Expandable content (.thread-expand-on-hover): ${expandContent ? 'FOUND' : 'NOT FOUND'}`, expandContent ? 'color: #00AA00;' : 'color: #FF0000;');
    log(`Chevron (.chevron-icon): ${chevron ? 'FOUND' : 'NOT FOUND'}`, chevron ? 'color: #00AA00;' : 'color: #FF0000;');
    log(`Expand button: ${expandBtn ? 'FOUND' : 'NOT FOUND'}`, expandBtn ? 'color: #00AA00;' : 'color: #FF0000;');

    // ========================================================================
    // PART 2: CLASS & STATE ANALYSIS
    // ========================================================================
    header('2. EXPANSION STATE ANALYSIS');

    const hasExpandedContainer = primeContainer?.classList.contains('expanded');
    const hasExpandedCard = primeCard?.classList.contains('expanded');

    log(`Container has .expanded class? ${hasExpandedContainer ? 'YES' : 'NO'}`, hasExpandedContainer ? 'color: #00AA00;' : 'color: #FFAA00;');
    log(`Card has .expanded class? ${hasExpandedCard ? 'YES' : 'NO'}`, hasExpandedCard ? 'color: #00AA00;' : 'color: #FFAA00;');

    if (!hasExpandedContainer && !hasExpandedCard) {
        warn('Neither container nor card has .expanded - check if toggle is firing');
    }

    // ========================================================================
    // PART 3: CSS RULES CHECK
    // ========================================================================
    header('3. CSS RULES ANALYSIS');

    let cssRules = {
        '#prime-thread-info.expanded': false,
        '#prime-thread-info .ai-chat-header-info.expanded': false,
        '#prime-thread-info .agent-thread-card.expanded': false,
        '#prime-thread-info .thread-expand-on-hover': false,
        '#prime-thread-info.expanded .thread-expand-on-hover': false,
        '#prime-thread-info .ai-chat-header-info.expanded .thread-expand-on-hover': false,
    };

    try {
        for (let sheet of document.styleSheets) {
            try {
                for (let rule of sheet.cssRules || []) {
                    const selector = rule.selectorText || '';
                    for (let cssRule in cssRules) {
                        if (selector.includes(cssRule.split(' ')[0]) || selector === cssRule) {
                            cssRules[cssRule] = true;
                        }
                    }
                }
            } catch (e) {
                // CORS errors on external sheets - ignore
            }
        }
    } catch (e) {
        error('Could not access stylesheets');
    }

    log('CSS Rules Found:');
    Object.entries(cssRules).forEach(([selector, found]) => {
        log(`  ${found ? '✅' : '❌'} ${selector}`, found ? 'color: #00AA00;' : 'color: #FF0000;');
    });

    // ========================================================================
    // PART 4: COMPUTED STYLES CHECK
    // ========================================================================
    header('4. COMPUTED STYLES ANALYSIS');

    if (expandContent) {
        const style = window.getComputedStyle(expandContent);
        const isVisible = style.opacity !== '0' && style.maxHeight !== '0px' && style.display !== 'none';

        log('Expandable Content Styles:');
        log(`  Opacity: ${style.opacity}`, isVisible ? 'color: #00AA00;' : 'color: #FF0000;');
        log(`  Max-height: ${style.maxHeight}`, isVisible ? 'color: #00AA00;' : 'color: #FF0000;');
        log(`  Overflow: ${style.overflow}`);
        log(`  Display: ${style.display}`, style.display !== 'none' ? 'color: #00AA00;' : 'color: #FF0000;');
        log(`  Visibility: ${style.visibility}`, style.visibility !== 'hidden' ? 'color: #00AA00;' : 'color: #FF0000;');
        log(`  Height: ${style.height}`);
        log(`  Margin-top: ${style.marginTop}`);

        if (!isVisible) {
            warn('Content is hidden - expansion CSS not being applied');
        }
    }

    if (chevron) {
        const style = window.getComputedStyle(chevron);
        log(`\nChevron Transform: ${style.transform}`);
        if (style.transform === 'matrix(1, 0, 0, 1, 0, 0)' || style.transform === 'none') {
            warn('Chevron not rotated - should be rotate(180deg) when expanded');
        }
    }

    // ========================================================================
    // PART 5: EVENT LISTENER CHECK
    // ========================================================================
    header('5. EVENT LISTENER ANALYSIS');

    if (expandBtn) {
        log('Expand button found - checking for event listeners...');
        log('Attempting to trigger click handler check...');

        // Create a test click event
        const testEvent = new MouseEvent('click', { bubbles: true, cancelable: true });
        let clickFired = false;

        const originalLog = console.log;
        const originalError = console.error;

        // Temporarily capture logs
        let tempLogs = [];
        console.log = function (...args) {
            tempLogs.push(args.join(' '));
            originalLog.apply(console, args);
        };

        expandBtn.dispatchEvent(testEvent);

        console.log = originalLog;

        if (tempLogs.some(l => l.includes('ThreadCardExpansion') || l.includes('Toggling'))) {
            success('Click event fired and was handled');
        } else {
            warn('Could not confirm click event handling');
        }
    }

    // ========================================================================
    // PART 6: FORCE TEST
    // ========================================================================
    header('6. FORCE EXPANSION TEST');

    if (primeCard && expandContent) {
        log('Adding .expanded class to card and checking CSS application...');

        // Remember original state
        const hadExpanded = primeCard.classList.contains('expanded');

        // Force add class
        primeCard.classList.add('expanded');

        // Check computed styles after
        setTimeout(() => {
            const style = window.getComputedStyle(expandContent);
            const nowVisible = style.opacity === '1' && style.maxHeight !== '0px';

            log(`\nAfter adding .expanded class:`);
            log(`  Opacity: ${style.opacity}`);
            log(`  Max-height: ${style.maxHeight}`);
            log(`  Content visible? ${nowVisible ? 'YES' : 'NO'}`, nowVisible ? 'color: #00AA00;' : 'color: #FF0000;');

            if (nowVisible) {
                success('CSS WORKS! Problem is JavaScript not adding .expanded class');
                log('  → Check: thread-card-expansion.js toggleCard() and getExpandableElement()');
            } else {
                error('CSS DOES NOT WORK! Even with forced .expanded class');
                log('  → Check: CSS selectors, specificity, or conflicting rules in thread-card-styles.css');
            }

            // Restore original state
            if (!hadExpanded) {
                primeCard.classList.remove('expanded');
            }
        }, 100);
    } else {
        error('Cannot perform force test - missing elements');
    }

    // ========================================================================
    // PART 7: ROOT CAUSE DETERMINATION
    // ========================================================================
    header('7. ROOT CAUSE DETERMINATION');

    let rootCauses = [];

    if (!primeContainer) {
        rootCauses.push('❌ CAUSE #1: Prime container (#prime-thread-info) not found - check HTML');
    }
    if (!primeCard) {
        rootCauses.push('❌ CAUSE #2: Prime card not found - check if card is rendered in Prime');
    }
    if (!expandContent) {
        rootCauses.push('❌ CAUSE #3: Expandable content missing - card HTML structure incomplete');
    }
    if (!hasExpandedContainer && !hasExpandedCard) {
        rootCauses.push('⚠️  CAUSE #4: .expanded class not being added - check if click triggers toggle');
    }
    if (!Object.values(cssRules).some(v => v)) {
        rootCauses.push('❌ CAUSE #5: CSS rules missing - check thread-card-styles.css');
    }

    if (rootCauses.length === 0) {
        success('All checks passed! Expansion should work.');
        log('If it still doesn\'t work, there may be a race condition or event binding issue.');
    } else {
        log('\nDetected Issues:');
        rootCauses.forEach(cause => console.log(`  ${cause}`));
    }

    // ========================================================================
    // PART 8: NEXT STEPS
    // ========================================================================
    header('8. RECOMMENDED NEXT STEPS');

    log('Based on this analysis:');
    log('');
    log('1️⃣  If CSS WORKED in force test:');
    log('   → Problem: JavaScript not adding .expanded class');
    log('   → Check: thread-card-expansion.js toggleCard() method');
    log('   → Fix: Verify getExpandableElement() returns correct element for Prime');
    log('');
    log('2️⃣  If CSS FAILED in force test:');
    log('   → Problem: CSS selectors don\'t match or rules are overridden');
    log('   → Check: thread-card-styles.css lines 290-315');
    log('   → Fix: Ensure selectors are specific enough and !important if needed');
    log('');
    log('3️⃣  If elements MISSING:');
    log('   → Problem: HTML structure incomplete');
    log('   → Check: Prime card rendering in ThreadManager');
    log('   → Fix: Verify renderThreadInfoContainer() works for Prime');
    log('');
    log('4️⃣  If .expanded NOT ADDED:');
    log('   → Problem: Click event not triggering or event handler not working');
    log('   → Run: window.ThreadCardExpansion?.toggleCard(event, threadId) manually');
    log('   → Check: Event listener attached to expand button');

    log('\n═══════════════════════════════════════════════════════════════════════════');
    log('DEBUG REPORT COMPLETE - Check console output above for issues', 'color: #4ECDC4; font-weight: bold;');
    log('═══════════════════════════════════════════════════════════════════════════');

})();

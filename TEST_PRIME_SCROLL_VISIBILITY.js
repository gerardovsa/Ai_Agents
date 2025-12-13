// ═══════════════════════════════════════════════════════════════════════════
// PRIME SCROLL CONTROLS VISIBILITY CHECKER
// ═══════════════════════════════════════════════════════════════════════════
// Paste this into browser console to verify scroll buttons are visible
// ═══════════════════════════════════════════════════════════════════════════

(function() {
    const header = (title) => console.log(`%c\n╔${'═'.repeat(title.length + 2)}╗\n║ ${title} ║\n╚${'═'.repeat(title.length + 2)}╝`, 'color: #4ECDC4; font-weight: bold;');
    const success = (msg) => console.log(`%c✅ ${msg}`, 'color: #00AA00; font-weight: bold;');
    const error = (msg) => console.error(`%c❌ ${msg}`, 'color: #FF0000; font-weight: bold;');
    const warn = (msg) => console.log(`%c⚠️  ${msg}`, 'color: #FFAA00; font-weight: bold;');
    const log = (msg) => console.log(`%c${msg}`, 'color: #333;');

    header('PRIME SCROLL CONTROLS VISIBILITY CHECK');

    // 1. Check if controls container exists
    const controlsContainer = document.querySelector('.prime-scroll-controls');
    log('1. Controls Container:');
    if (controlsContainer) {
        success('Found .prime-scroll-controls');
        const style = window.getComputedStyle(controlsContainer);
        log(`   Position: ${style.position}`);
        log(`   Display: ${style.display}`);
        log(`   Visibility: ${style.visibility}`);
        log(`   Opacity: ${style.opacity}`);
        log(`   Z-index: ${style.zIndex}`);
        log(`   Top: ${style.top}`);
        log(`   Right: ${style.right}`);
    } else {
        error('Controls container NOT FOUND');
    }

    // 2. Check parent container
    log('\n2. Parent Container (#ai-chat-messages):');
    const messagesContainer = document.querySelector('#ai-chat-messages');
    if (messagesContainer) {
        success('Found #ai-chat-messages');
        const style = window.getComputedStyle(messagesContainer);
        log(`   Position: ${style.position}`);
        log(`   Display: ${style.display}`);
        log(`   Visibility: ${style.visibility}`);
        
        if (style.position !== 'relative' && style.position !== 'absolute' && style.position !== 'fixed') {
            warn('Parent is not positioned - controls may not align correctly');
        } else {
            success('Parent has correct positioning context');
        }
    } else {
        error('Messages container NOT FOUND');
    }

    // 3. Check individual buttons
    log('\n3. Scroll Control Buttons:');
    const buttons = {
        'Scroll Top': '.prime-scroll-top-btn',
        'Scroll Bottom': '.prime-scroll-bottom-btn',
        'Auto-scroll': '.prime-autoscroll-btn'
    };

    Object.entries(buttons).forEach(([name, selector]) => {
        const btn = document.querySelector(selector);
        if (btn) {
            success(`${name} button FOUND`);
            const style = window.getComputedStyle(btn);
            log(`   Position: ${style.position}`);
            log(`   Display: ${style.display}`);
            log(`   Visibility: ${style.visibility}`);
            log(`   Opacity: ${style.opacity}`);
            log(`   Width: ${style.width}, Height: ${style.height}`);
            
            // Check if clickable
            const rect = btn.getBoundingClientRect();
            log(`   Viewport coords: (${Math.round(rect.left)}, ${Math.round(rect.top)}) to (${Math.round(rect.right)}, ${Math.round(rect.bottom)})`);
            
            if (rect.width > 0 && rect.height > 0) {
                success(`   Clickable: YES`);
            } else {
                warn(`   Clickable: NO (dimensions are 0)`);
            }
        } else {
            error(`${name} button NOT FOUND`);
        }
    });

    // 4. Test if functions exist
    log('\n4. JavaScript Functions:');
    if (typeof PrimeChat !== 'undefined') {
        success('PrimeChat object exists');
        
        if (typeof PrimeChat.scrollToTop === 'function') {
            success('scrollToTop() method found');
        } else {
            error('scrollToTop() method NOT FOUND');
        }
        
        if (typeof PrimeChat.scrollToBottom === 'function') {
            success('scrollToBottom() method found');
        } else {
            error('scrollToBottom() method NOT FOUND');
        }
        
        if (typeof PrimeChat.toggleAutoScroll === 'function') {
            success('toggleAutoScroll() method found');
        } else {
            error('toggleAutoScroll() method NOT FOUND');
        }
    } else {
        error('PrimeChat object NOT FOUND');
    }

    // 5. Manual button test
    log('\n5. Button Click Test:');
    const topBtn = document.querySelector('.prime-scroll-top-btn');
    if (topBtn) {
        log('   Testing scroll top button click...');
        try {
            topBtn.click();
            success('   Scroll to top triggered');
        } catch (e) {
            error(`   Click failed: ${e.message}`);
        }
    }

    // 6. Final verdict
    log('\n6. Summary:');
    const allGood = 
        controlsContainer && 
        messagesContainer && 
        document.querySelector('.prime-scroll-top-btn') &&
        document.querySelector('.prime-scroll-bottom-btn') &&
        document.querySelector('.prime-autoscroll-btn') &&
        typeof PrimeChat !== 'undefined';

    if (allGood) {
        success('ALL CHECKS PASSED - Scroll buttons should be visible!');
        log('\n   If you still don\'t see the buttons:');
        log('   1. Hard refresh (Ctrl+Shift+R)');
        log('   2. Check browser console for JavaScript errors');
        log('   3. Load a thread into Prime Chat first');
    } else {
        error('SOME CHECKS FAILED - See above for details');
    }

    log('\n═══════════════════════════════════════════════════════════════════════════');

})();

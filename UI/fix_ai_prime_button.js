// ============================================================
// FIX AI PRIME TOGGLE BUTTON
// Copy and paste this entire script into browser console
// ============================================================

console.log('%c🤖 FIXING AI PRIME TOGGLE BUTTON', 'color: #58a6ff; font-size: 16px; font-weight: bold;');

const btn = document.getElementById('ai-prime-toggle-btn');
const panel = document.getElementById('ai-chat-panel');
const wrapper = document.getElementById('main-content-wrapper');

if (!btn) {
    console.error('❌ Button not found!');
} else if (!panel) {
    console.error('❌ Chat panel not found!');
} else if (!wrapper) {
    console.error('❌ Wrapper not found!');
} else {
    // Remove all existing listeners by cloning
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);

    // Add fresh click listener
    newBtn.addEventListener('click', function () {
        const isOpen = !wrapper.classList.contains('chat-collapsed');

        if (isOpen) {
            // Close chat
            wrapper.classList.add('chat-collapsed');
            panel.style.display = 'none';
            newBtn.classList.remove('active');
            if (typeof AppState !== 'undefined') AppState.chatOpen = false;
            console.log('🤖 AI Prime chat CLOSED');
        } else {
            // Open chat
            wrapper.classList.remove('chat-collapsed');
            panel.style.display = 'flex';
            newBtn.classList.add('active');
            if (typeof AppState !== 'undefined') AppState.chatOpen = true;
            console.log('🤖 AI Prime chat OPENED');
        }
    });

    console.log('✅ AI Prime button FIXED and working!');
    console.log('👉 Click the button to test it');
}

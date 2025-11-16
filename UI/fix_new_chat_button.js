// ============================================================
// FIX NEW CHAT BUTTON
// Copy and paste this entire script into browser console
// ============================================================

console.log('%c➕ FIXING NEW CHAT BUTTON', 'color: #58a6ff; font-size: 16px; font-weight: bold;');

const btn = document.getElementById('new-chat-btn');

console.log('Button:', btn);
console.log('ThreadManager:', typeof ThreadManager);

if (!btn) {
    console.error('❌ New Chat button not found!');
} else {
    // Remove all existing listeners by cloning
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);

    // Add fresh click listener
    newBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        // Check if modal already exists
        const existingModal = document.getElementById('newChatModalOverlay');
        if (existingModal) {
            console.warn('💬 Modal already open, skipping...');
            return;
        }

        // Try ThreadManager first
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.showNewChatModal === 'function') {
            ThreadManager.showNewChatModal('prime');
            console.log('➕ New Chat modal opened');
        } else {
            console.error('❌ ThreadManager.showNewChatModal not found!');
        }
    });

    console.log('✅ New Chat button FIXED and working!');
    console.log('👉 Click the button to test it');
}

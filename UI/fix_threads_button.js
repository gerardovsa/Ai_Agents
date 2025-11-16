// ============================================================
// FIX THREADS BUTTON (Thread History)
// Copy and paste this entire script into browser console
// ============================================================

console.log('%c💬 FIXING THREADS BUTTON', 'color: #58a6ff; font-size: 16px; font-weight: bold;');

const btn = document.getElementById('threads-btn');
const menu = document.getElementById('thread-menu');

console.log('Button:', btn);
console.log('Thread Menu:', menu);
console.log('ThreadManager:', typeof ThreadManager);

if (!btn) {
    console.error('❌ Threads button not found!');
} else if (!menu) {
    console.error('❌ Thread menu not found!');
} else {
    // Remove all existing listeners by cloning
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);

    // Add fresh click listener
    newBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        // Try ThreadManager first, fallback to direct toggle
        if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.toggleThreadMenu === 'function') {
            ThreadManager.toggleThreadMenu();
        } else {
            menu.classList.toggle('active');
            console.log('💬 Thread menu', menu.classList.contains('active') ? 'OPENED' : 'CLOSED');
        }
    });

    console.log('✅ Threads button FIXED and working!');
    console.log('👉 Click the button to test it');
}

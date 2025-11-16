// ============================================================
// FIX QUICK ACTIONS BUTTON (Instructions Catalogue)
// Copy and paste this entire script into browser console
// ============================================================

console.log('%c⚡ FIXING QUICK ACTIONS BUTTON', 'color: #58a6ff; font-size: 16px; font-weight: bold;');

const btn = document.getElementById('quick-actions-btn');
const promptSidebar = document.getElementById('prompt-sidebar');

console.log('Button:', btn);
console.log('Prompt Sidebar:', promptSidebar);

if (!btn) {
    console.error('❌ Quick Actions button not found!');
} else if (!promptSidebar) {
    console.error('❌ Prompt sidebar not found! Make sure prompt-library.js is loaded.');
} else {
    // Remove all existing listeners by cloning
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);

    // Add fresh click listener
    newBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        promptSidebar.classList.toggle('show');
        console.log('⚡ Instructions Catalogue', promptSidebar.classList.contains('show') ? 'OPENED' : 'CLOSED');
    });

    console.log('✅ Quick Actions button FIXED and working!');
    console.log('👉 Click the button to test it');
}

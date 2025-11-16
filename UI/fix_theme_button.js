// ============================================================
// FIX THEME TOGGLE BUTTON
// Copy and paste this entire script into browser console
// ============================================================

console.log('%c🌓 FIXING THEME TOGGLE BUTTON', 'color: #58a6ff; font-size: 16px; font-weight: bold;');

const btn = document.getElementById('theme-toggle-btn-sidebar');

console.log('Button:', btn);
console.log('Current theme:', document.documentElement.getAttribute('data-theme'));

if (!btn) {
    console.error('❌ Theme toggle button not found!');
} else {
    // Remove all existing listeners by cloning
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);

    // Add fresh click listener
    newBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        console.log('🌓 Theme changed from', currentTheme, 'to', newTheme);
    });

    console.log('✅ Theme toggle button FIXED and working!');
    console.log('👉 Click the button to test it');
}

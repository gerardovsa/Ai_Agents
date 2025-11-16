// ============================================================
// FIX USER PROFILE BUTTON
// Copy and paste this entire script into browser console
// ============================================================

console.log('%c👤 FIXING USER PROFILE BUTTON', 'color: #58a6ff; font-size: 16px; font-weight: bold;');

const container = document.getElementById('userProfileContainer');
const menu = document.getElementById('userDropdownMenu');
const btnSidebar = document.getElementById('userProfileBtn-sidebar');
const btnHeader = document.getElementById('userProfileBtn');

console.log('Container:', container);
console.log('Menu:', menu);
console.log('Sidebar Button:', btnSidebar);
console.log('Header Button:', btnHeader);

if (!container) {
    console.error('❌ Profile container not found!');
} else if (!menu) {
    console.error('❌ Dropdown menu not found!');
} else {
    // Make sure container is visible
    container.style.display = 'flex';
    container.style.visibility = 'visible';
    console.log('✅ Profile container shown');

    // Create toggle function
    window.toggleProfileMenu = function () {
        menu.classList.toggle('active');
        if (btnSidebar) btnSidebar.classList.toggle('active');
        if (btnHeader) btnHeader.classList.toggle('active');
        console.log('👤 Profile menu', menu.classList.contains('active') ? 'OPENED' : 'CLOSED');
    };

    // Fix sidebar button
    if (btnSidebar) {
        const newBtn = btnSidebar.cloneNode(true);
        btnSidebar.parentNode.replaceChild(newBtn, btnSidebar);
        newBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            window.toggleProfileMenu();
        });
        console.log('✅ Sidebar button fixed');
    }

    // Fix header button
    if (btnHeader) {
        const newBtn = btnHeader.cloneNode(true);
        btnHeader.parentNode.replaceChild(newBtn, btnHeader);
        newBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            window.toggleProfileMenu();
        });
        console.log('✅ Header button fixed');
    }

    // Close menu when clicking outside
    document.addEventListener('click', function (e) {
        if (!menu.contains(e.target) &&
            e.target.id !== 'userProfileBtn' &&
            e.target.id !== 'userProfileBtn-sidebar' &&
            !e.target.closest('#userProfileBtn') &&
            !e.target.closest('#userProfileBtn-sidebar')) {
            menu.classList.remove('active');
            if (btnSidebar) btnSidebar.classList.remove('active');
            if (btnHeader) btnHeader.classList.remove('active');
        }
    });

    console.log('✅ User Profile button FIXED and working!');
    console.log('👉 Click the button in the right sidebar to test it');
}

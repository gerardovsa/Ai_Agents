/**
 * LOAD VECTOR DATABASE WITH FIXED STRUCTURE
 * 
 * This loads the new HTML structure that uses universal-sidebar framework
 */

(async function () {
    console.log('🔄 Loading Vector Database with universal-sidebar framework...\n');

    const sidebar = document.getElementById('vector-database');

    if (!sidebar) {
        console.error('❌ Sidebar element not found!');
        return;
    }

    console.log('1️⃣ Current classes:', sidebar.className);
    console.log('2️⃣ Current HTML length:', sidebar.innerHTML.length);

    // Fetch the new HTML template
    console.log('\n📥 Fetching HTML template...');
    try {
        const response = await fetch('/modules_internal/vector_database/vector_database.html?v=' + Date.now());
        if (response.ok) {
            const html = await response.text();
            sidebar.innerHTML = html;
            console.log('✅ HTML loaded:', html.length, 'characters');
        } else {
            console.error('❌ Failed to fetch HTML:', response.status);
            return;
        }
    } catch (error) {
        console.error('❌ Error:', error);
        return;
    }

    // Open the sidebar
    console.log('\n📂 Opening sidebar...');
    sidebar.classList.remove('collapsed');
    sidebar.classList.add('expanded');

    // Wait for render
    await new Promise(resolve => setTimeout(resolve, 300));

    // Inspect structure
    console.log('\n🔍 STRUCTURE CHECK:');
    console.log('Classes:', sidebar.className);
    console.log('Transform:', window.getComputedStyle(sidebar).transform);
    console.log('Width:', window.getComputedStyle(sidebar).width);
    console.log('Right:', window.getComputedStyle(sidebar).right);

    const header = sidebar.querySelector('.universal-sidebar-header');
    const content = sidebar.querySelector('.universal-sidebar-content');
    const footer = sidebar.querySelector('.universal-sidebar-footer');

    console.log('\n📦 COMPONENTS:');
    console.log('Header:', !!header, header ? `(${header.offsetWidth}x${header.offsetHeight}px)` : '');
    console.log('Content:', !!content, content ? `(${content.offsetWidth}x${content.offsetHeight}px)` : '');
    console.log('Footer:', !!footer, footer ? `(${footer.offsetWidth}x${footer.offsetHeight}px)` : '');

    if (content) {
        const provider = content.querySelector('#provider-selector');
        const tabs = content.querySelectorAll('.vector-db-tab');
        const tabContents = content.querySelectorAll('.tab-content');

        console.log('\n📋 CONTENT ELEMENTS:');
        console.log('Provider selector:', !!provider);
        console.log('Tabs:', tabs.length);
        console.log('Tab contents:', tabContents.length);

        // Show first tab
        if (tabContents.length > 0) {
            tabContents[0].style.display = 'block';
            console.log('✅ Activated first tab');
        }
    }

    console.log('\n✅ Vector Database should now be visible on the right side!');
})();

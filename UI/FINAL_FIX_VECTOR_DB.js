/**
 * ✅ FINAL FIX: Load Vector Database with Universal Sidebar Framework
 * 
 * This version:
 * 1. Uses universal-sidebar CSS for positioning (like other sidebars)
 * 2. Uses vector_database.css only for internal styling
 * 3. Should work exactly like Synergy sidebar but on the right side
 */

(async function () {
    console.log('🔧 FINAL FIX: Loading Vector Database Sidebar\n');

    // Get the sidebar container
    const sidebar = document.getElementById('vector-database');
    if (!sidebar) {
        console.error('❌ Sidebar element #vector-database not found!');
        return;
    }

    console.log('1️⃣ Container found:', sidebar.id);
    console.log('2️⃣ Current classes:', sidebar.className);

    // Fetch the updated HTML template
    console.log('\n📥 Fetching updated HTML...');
    try {
        const response = await fetch('/modules_internal/vector_database/vector_database.html?v=' + Date.now());
        if (!response.ok) {
            console.error('❌ Failed to fetch HTML:', response.status);
            return;
        }

        const html = await response.text();
        sidebar.innerHTML = html;
        console.log('✅ HTML loaded:', html.length, 'characters');

    } catch (error) {
        console.error('❌ Error loading HTML:', error);
        return;
    }

    // Open the sidebar (remove collapsed, add expanded)
    console.log('\n📂 Opening sidebar...');
    sidebar.classList.remove('collapsed');
    sidebar.classList.add('expanded');

    // Wait for render
    await new Promise(resolve => setTimeout(resolve, 300));

    // Diagnostic check
    console.log('\n🔍 DIAGNOSTIC:');
    const styles = window.getComputedStyle(sidebar);
    console.log('Classes:', sidebar.className);
    console.log('Transform:', styles.transform);
    console.log('Position:', styles.position, 'Right:', styles.right);
    console.log('Width:', styles.width, 'Height:', styles.height);
    console.log('Z-index:', styles.zIndex);
    console.log('Background:', styles.backgroundColor);

    // Check structure
    const header = sidebar.querySelector('.universal-sidebar-header');
    const content = sidebar.querySelector('.universal-sidebar-content');
    const footer = sidebar.querySelector('.universal-sidebar-footer');

    console.log('\n📦 STRUCTURE:');
    console.log('Header:', !!header, header ? `visible (${header.offsetWidth}x${header.offsetHeight})` : 'MISSING');
    console.log('Content:', !!content, content ? `visible (${content.offsetWidth}x${content.offsetHeight})` : 'MISSING');
    console.log('Footer:', !!footer, footer ? `visible (${footer.offsetWidth}x${footer.offsetHeight})` : 'MISSING');

    if (header) {
        const title = header.querySelector('.universal-sidebar-title');
        const stats = header.querySelector('.vector-db-stats');
        console.log('\nHeader components:');
        console.log('  Title:', title ? title.textContent.trim() : 'missing');
        console.log('  Stats:', !!stats, stats ? `(${stats.children.length} stats)` : '');
    }

    if (content) {
        const tabs = content.querySelectorAll('.vector-db-tab');
        const tabContents = content.querySelectorAll('.tab-content');
        console.log('\nContent components:');
        console.log('  Tabs:', tabs.length);
        console.log('  Tab contents:', tabContents.length);

        // Activate first tab
        if (tabContents.length > 0) {
            // Hide all tabs first
            tabContents.forEach(tab => tab.style.display = 'none');
            // Show first tab
            tabContents[0].style.display = 'block';
            console.log('  ✅ Activated first tab');
        }
    }

    console.log('\n' + '='.repeat(60));
    console.log('✅ VECTOR DATABASE SHOULD NOW BE VISIBLE!');
    console.log('='.repeat(60));
    console.log('\nIf you still see a black box:');
    console.log('1. Hard refresh browser (Ctrl+Shift+R)');
    console.log('2. Check console for CSS load errors');
    console.log('3. Verify sidebar-manager.css is loaded');
})();

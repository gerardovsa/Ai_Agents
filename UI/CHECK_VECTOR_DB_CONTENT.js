/**
 * Check if Vector DB sidebar has content
 */

const sidebar = document.getElementById('vector-database');
console.log('🔍 VECTOR DB SIDEBAR DIAGNOSTIC\n');

console.log('1️⃣ SIDEBAR EXISTS:', !!sidebar);
if (!sidebar) {
    console.error('❌ Sidebar element not found!');
} else {
    console.log('2️⃣ CLASSES:', sidebar.className);
    console.log('3️⃣ TRANSFORM:', window.getComputedStyle(sidebar).transform);
    console.log('4️⃣ POSITION:', {
        position: window.getComputedStyle(sidebar).position,
        right: window.getComputedStyle(sidebar).right,
        top: window.getComputedStyle(sidebar).top,
        width: window.getComputedStyle(sidebar).width,
        height: window.getComputedStyle(sidebar).height
    });

    console.log('\n5️⃣ INNER HTML LENGTH:', sidebar.innerHTML.length);
    console.log('6️⃣ INNER HTML PREVIEW:');
    console.log(sidebar.innerHTML.substring(0, 500));

    console.log('\n7️⃣ CHILDREN COUNT:', sidebar.children.length);
    console.log('8️⃣ CHILDREN:');
    Array.from(sidebar.children).forEach((child, i) => {
        console.log(`   [${i}]`, child.tagName, child.className,
            `(${child.offsetWidth}x${child.offsetHeight})`);
    });

    console.log('\n9️⃣ VISIBILITY CHECK:');
    console.log('   Display:', window.getComputedStyle(sidebar).display);
    console.log('   Visibility:', window.getComputedStyle(sidebar).visibility);
    console.log('   Opacity:', window.getComputedStyle(sidebar).opacity);
    console.log('   Z-index:', window.getComputedStyle(sidebar).zIndex);

    // Check for specific Vector DB elements
    console.log('\n🔟 VECTOR DB SPECIFIC ELEMENTS:');
    const header = sidebar.querySelector('.vector-db-sidebar-header');
    const stats = sidebar.querySelector('.vector-db-stats');
    const tabs = sidebar.querySelectorAll('.tab-btn');
    const tabContents = sidebar.querySelectorAll('.tab-content');

    console.log('   Header:', !!header, header ? `(${header.offsetWidth}x${header.offsetHeight})` : '');
    console.log('   Stats:', !!stats, stats ? `(${stats.offsetWidth}x${stats.offsetHeight})` : '');
    console.log('   Tab buttons:', tabs.length);
    console.log('   Tab contents:', tabContents.length);

    // Check visibility of tab contents
    if (tabContents.length > 0) {
        console.log('\n1️⃣1️⃣ TAB CONTENT VISIBILITY:');
        tabContents.forEach((tab, i) => {
            const styles = window.getComputedStyle(tab);
            console.log(`   Tab ${i}:`, {
                display: styles.display,
                hasActiveClass: tab.classList.contains('active'),
                offsetHeight: tab.offsetHeight
            });
        });
    }
}

/**
 * FIX: Vector DB Sidebar Class Mismatch
 * 
 * Problem: CSS expects ".expanded" class, but SidebarManager adds ".collapsed" 
 * Solution: Remove "collapsed", add "expanded" when sidebar opens
 */

// Fix the class mismatch
const sidebar = document.getElementById('vector-database');
if (sidebar) {
    console.log('🔍 Current classes:', sidebar.className);

    // Remove collapsed class
    sidebar.classList.remove('collapsed');

    // Add expanded class (what CSS expects)
    sidebar.classList.add('expanded');

    // Also ensure it's marked as right-side if needed
    if (!sidebar.classList.contains('right-side')) {
        sidebar.classList.add('right-side');
    }

    console.log('✅ Updated classes:', sidebar.className);
    console.log('📐 Transform:', window.getComputedStyle(sidebar).transform);
}

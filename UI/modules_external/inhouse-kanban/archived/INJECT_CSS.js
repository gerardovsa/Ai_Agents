// =====================================================
// EMERGENCY CSS INJECTOR - Paste this in browser console
// =====================================================

console.log("🚨 Injecting Kanban Board CSS directly...");

// Remove any existing injected style
const existingStyle = document.getElementById('kanban-emergency-css');
if (existingStyle) {
    existingStyle.remove();
}

// Create style element
const style = document.createElement('style');
style.id = 'kanban-emergency-css';
style.textContent = `
/* EMERGENCY KANBAN BOARD FIX */
.kanban-board {
    display: flex !important;
    flex-direction: row !important;
    gap: 20px !important;
    padding: 20px !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    flex: 1 !important;
    background: #0B0E13 !important;
    align-items: flex-start !important;
    min-height: 0 !important;
    width: 100% !important;
}

.kanban-column {
    min-width: 340px !important;
    max-width: 340px !important;
    background: #1A1F2E !important;
    border: 1px solid #2A3142 !important;
    border-radius: 8px !important;
    display: flex !important;
    flex-direction: column !important;
    height: fit-content !important;
    max-height: calc(100vh - 450px) !important;
    flex-shrink: 0 !important;
    overflow: hidden !important;
}

.column-header {
    padding: 16px !important;
    border-bottom: 2px solid #2A3142 !important;
    background: #1A1F2E !important;
}

.column-body {
    padding: 12px !important;
    overflow-y: auto !important;
    flex: 1 !important;
}

.kanban-card {
    background: #0B0E13 !important;
    border: 1px solid #2A3142 !important;
    border-radius: 6px !important;
    padding: 12px !important;
    margin-bottom: 12px !important;
    cursor: pointer !important;
}

.kanban-card:hover {
    border-color: #00509E !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0, 80, 158, 0.3) !important;
}
`;

// Inject into document
document.head.appendChild(style);

console.log("✅ CSS Injected!");
console.log("");
console.log("🔍 Verifying...");

// Verify
const board = document.querySelector('.kanban-board');
if (board) {
    const styles = getComputedStyle(board);
    console.log("Display:", styles.display);
    console.log("Flex Direction:", styles.flexDirection);
    console.log("Gap:", styles.gap);

    if (styles.display === 'flex' && styles.flexDirection === 'row') {
        console.log("");
        console.log("🎉 SUCCESS! Columns should now be side-by-side!");
    } else {
        console.log("");
        console.log("⚠️ Still not working. Check for other CSS conflicts.");
    }
} else {
    console.log("❌ .kanban-board element not found!");
}

// ==============================================
// KANBAN BOARD DIAGNOSTIC SCRIPT
// Run this in browser console (F12)
// ==============================================

console.log(" Kanban Board Layout Diagnostic");
console.log("=====================================");
console.log("");

// Check if board exists
const board = document.querySelector(".kanban-board");
if (!board) {
    console.error(" ERROR: .kanban-board element not found!");
    console.log("    Check if module loaded correctly");
} else {
    console.log(" Found .kanban-board element");
    
    // Get computed styles
    const styles = getComputedStyle(board);
    
    console.log("");
    console.log(" Board Container Styles:");
    console.log("   Display:", styles.display);
    console.log("   Flex Direction:", styles.flexDirection);
    console.log("   Gap:", styles.gap);
    console.log("   Overflow X:", styles.overflowX);
    console.log("   Width:", styles.width);
    console.log("   Min Height:", styles.minHeight);
    
    // Check columns
    const columns = board.querySelectorAll(".kanban-column");
    console.log("");
    console.log(" Columns Found:", columns.length);
    
    if (columns.length === 0) {
        console.warn("  No columns found - check JavaScript rendering");
    } else {
        console.log(" Columns detected:", columns.length);
        
        // Check first column
        const firstCol = columns[0];
        const colStyles = getComputedStyle(firstCol);
        
        console.log("");
        console.log(" First Column Styles:");
        console.log("   Display:", colStyles.display);
        console.log("   Flex Direction:", colStyles.flexDirection);
        console.log("   Min Width:", colStyles.minWidth);
        console.log("   Max Width:", colStyles.maxWidth);
        console.log("   Flex Shrink:", colStyles.flexShrink);
    }
    
    // Layout validation
    console.log("");
    console.log(" Layout Validation:");
    
    const isFlexRow = styles.display === "flex" && styles.flexDirection === "row";
    const hasProperOverflow = styles.overflowX === "auto" && styles.overflowY === "hidden";
    const hasColumns = columns.length > 0;
    
    console.log("   Flex Row Layout:", isFlexRow ? " PASS" : " FAIL");
    console.log("   Proper Overflow:", hasProperOverflow ? " PASS" : " FAIL");
    console.log("   Has Columns:", hasColumns ? " PASS" : " FAIL");
    
    console.log("");
    
    if (isFlexRow && hasProperOverflow && hasColumns) {
        console.log(" SUCCESS! Layout should be working correctly!");
        console.log("    Columns should display side-by-side");
        console.log("    Horizontal scrolling should work");
    } else {
        console.log("  ISSUES DETECTED!");
        
        if (!isFlexRow) {
            console.log("    Board is not using flex row layout");
            console.log("    Check if CSS loaded correctly (hard refresh?)");
        }
        
        if (!hasProperOverflow) {
            console.log("    Overflow settings incorrect");
            console.log("    Scrolling may not work properly");
        }
        
        if (!hasColumns) {
            console.log("    No columns rendered");
            console.log("    Check JavaScript console for errors");
        }
    }
}

console.log("");
console.log("=====================================");

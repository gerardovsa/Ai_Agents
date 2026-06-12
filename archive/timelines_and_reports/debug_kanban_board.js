console.log(' DEBUGGING INHOUSE KANBAN BOARD RENDERING');
console.log('==========================================');

// Check if module exists
if (!window.currentKanbanModule) {
    console.error(' window.currentKanbanModule not found!');
} else {
    console.log(' Module found:', window.currentKanbanModule);
    
    // Check UI elements
    console.log('\n UI Elements:');
    console.log('  kanbanBoard:', window.currentKanbanModule.ui.kanbanBoard);
    console.log('  workboardSelector:', window.currentKanbanModule.ui.workboardSelector);
    console.log('  metricsContainer:', window.currentKanbanModule.ui.metricsContainer);
    
    // Check state
    console.log('\n State:');
    console.log('  jobs:', window.currentKanbanModule.state.jobs.length);
    console.log('  stages:', window.currentKanbanModule.state.stages.length);
    console.log('  activeWorkboard:', window.currentKanbanModule.state.activeWorkboard);
    
    // Check workboard config
    const wb = window.currentKanbanModule.state.activeWorkboard;
    const config = window.currentKanbanModule.workboards[wb];
    console.log('  workboard config:', config);
    
    // Check if board element has content
    const board = document.getElementById('kanban-board');
    console.log('\n Kanban Board Element:');
    console.log('  exists:', !!board);
    console.log('  innerHTML length:', board?.innerHTML?.length || 0);
    console.log('  children count:', board?.children?.length || 0);
    
    // Try to manually render
    console.log('\n Attempting manual render...');
    try {
        window.currentKanbanModule.renderKanbanBoard();
        console.log(' Manual render complete');
        console.log('  Board innerHTML after render:', board?.innerHTML?.length || 0);
        console.log('  Board children after render:', board?.children?.length || 0);
    } catch (error) {
        console.error(' Manual render failed:', error);
    }
}

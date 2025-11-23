/**
 * Automation Canvas Diagnostics
 * Run these tests in browser console to verify button functionality
 * 
 * Usage:
 *   window.testAutomationCanvas()          - Run all tests
 *   window.fixAutomationButtons()          - Emergency fix for buttons
 *   window.automationCanvas.verifyEventListeners()  - Check event listeners
 */

// Complete diagnostic test suite
window.testAutomationCanvas = function() {
    console.log('\n========================================');
    console.log('🔍 AUTOMATION CANVAS DIAGNOSTICS');
    console.log('========================================\n');

    // Test 1: Canvas Initialization
    console.log('1️⃣ Canvas Initialization:');
    console.log('   window.automationCanvas:', !!window.automationCanvas);
    if (window.automationCanvas) {
        console.log('   Is AutomationCanvas instance:', window.automationCanvas.constructor.name === 'AutomationCanvas');
        console.log('   Shapes count:', window.automationCanvas.shapes?.length || 0);
    }

    // Test 2: Button Existence
    console.log('\n2️⃣ Button Existence:');
    const buttonIds = [
        'new-workflow-btn', 'load-workflow-btn', 'save-workflow-btn',
        'export-workflow-btn', 'print-workflow-btn', 'automation-send-ai-btn',
        'zoom-in-btn', 'zoom-out-btn', 'zoom-reset-btn', 'recenter-btn'
    ];

    let foundButtons = 0;
    buttonIds.forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            foundButtons++;
            console.log(`   ✅ ${id}`);
        } else {
            console.log(`   ❌ ${id} NOT FOUND`);
        }
    });
    console.log(`   Total: ${foundButtons}/${buttonIds.length} buttons found`);

    // Test 3: Function Existence
    console.log('\n3️⃣ Function Existence:');
    const functions = [
        'openWorkflowModal', 'showLoadWorkflowDialog', 'saveWorkflow',
        'exportToJSON', 'printWorkflow', 'sendToAI',
        'zoomIn', 'zoomOut', 'zoomReset', 'recenterToShapes',
        'verifyEventListeners'
    ];

    let foundFunctions = 0;
    functions.forEach(fn => {
        const exists = typeof window.automationCanvas?.[fn] === 'function';
        if (exists) {
            foundFunctions++;
            console.log(`   ✅ ${fn}`);
        } else {
            console.log(`   ❌ ${fn} NOT FOUND`);
        }
    });
    console.log(`   Total: ${foundFunctions}/${functions.length} functions found`);

    // Test 4: Tab Visibility
    console.log('\n4️⃣ Tab Visibility:');
    const automationTab = document.getElementById('tab-automation');
    const canvasWrapper = document.getElementById('automation-canvas-wrapper');
    console.log('   Tab display:', automationTab?.style.display || 'default');
    console.log('   Tab classList:', automationTab?.classList.toString() || 'none');
    console.log('   Canvas wrapper visible:', canvasWrapper?.offsetParent !== null);
    console.log('   Canvas wrapper display:', canvasWrapper?.style.display || 'default');

    // Test 5: Event Listener Verification
    console.log('\n5️⃣ Event Listener Verification:');
    if (window.automationCanvas?.verifyEventListeners) {
        const result = window.automationCanvas.verifyEventListeners();
        console.log(`   Result: ${result.attached} attached, ${result.missing} missing`);
    } else {
        console.error('   ❌ verifyEventListeners() not available');
    }

    // Test 6: Manual Function Test
    console.log('\n6️⃣ Manual Function Test:');
    try {
        if (typeof window.automationCanvas?.openWorkflowModal === 'function') {
            console.log('   ✅ openWorkflowModal() exists and is callable');
        } else {
            console.error('   ❌ openWorkflowModal() not available');
        }
    } catch (e) {
        console.error('   ❌ Error:', e.message);
    }

    console.log('\n========================================');
    console.log('📊 DIAGNOSTIC SUMMARY');
    console.log('========================================');
    console.log(`Canvas: ${window.automationCanvas ? '✅' : '❌'}`);
    console.log(`Buttons: ${foundButtons}/${buttonIds.length}`);
    console.log(`Functions: ${foundFunctions}/${functions.length}`);
    console.log('\n💡 TIP: If buttons don\'t work, run: window.fixAutomationButtons()');
    console.log('========================================\n');
};

// Emergency fix function
window.fixAutomationButtons = function() {
    console.log('\n🔧 EMERGENCY FIX: Manually attaching button handlers...\n');
    
    const canvas = window.automationCanvas;
    if (!canvas) {
        console.error('❌ Canvas not found! Cannot attach handlers.');
        return;
    }
    
    const handlers = {
        'new-workflow-btn': () => canvas.openWorkflowModal(),
        'load-workflow-btn': () => canvas.showLoadWorkflowDialog(),
        'save-workflow-btn': () => canvas.saveWorkflow(),
        'export-workflow-btn': () => canvas.exportToJSON(),
        'print-workflow-btn': () => canvas.printWorkflow(),
        'automation-send-ai-btn': () => canvas.sendToAI(),
        'zoom-in-btn': () => canvas.zoomIn(),
        'zoom-out-btn': () => canvas.zoomOut(),
        'zoom-reset-btn': () => canvas.zoomReset(),
        'recenter-btn': () => canvas.recenterToShapes()
    };
    
    let attached = 0;
    let missing = 0;
    
    Object.entries(handlers).forEach(([id, handler]) => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.onclick = handler;
            attached++;
            console.log(`✅ Attached: ${id}`);
        } else {
            missing++;
            console.warn(`⚠️ Missing: ${id}`);
        }
    });
    
    console.log(`\n✅ EMERGENCY FIX COMPLETE`);
    console.log(`   ${attached} buttons fixed`);
    console.log(`   ${missing} buttons missing\n`);
    
    if (attached > 0) {
        console.log('🎉 Buttons should work now! Try clicking them.');
    } else {
        console.error('❌ No buttons found - they may not be in the DOM yet.');
    }
};

console.log('✅ Automation Canvas Diagnostics loaded');
console.log('   Run: window.testAutomationCanvas() to test');
console.log('   Run: window.fixAutomationButtons() for emergency fix');

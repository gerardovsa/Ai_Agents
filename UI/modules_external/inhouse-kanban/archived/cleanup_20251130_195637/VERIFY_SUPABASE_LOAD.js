/**
 * Supabase UI Loading Verification Script
 * 
 * Run this in browser console to diagnose loading issues
 * 
 * Usage:
 *   1. Copy entire script
 *   2. Paste in browser console
 *   3. Press Enter
 */

(async function verifySupabaseLoad() {
    console.log('%c=== Supabase UI Loading Diagnostic ===', 'color: #00d4ff; font-size: 16px; font-weight: bold;');
    
    const results = {
        passed: [],
        failed: [],
        warnings: []
    };
    
    // Test 1: Check if module loader supports additional_scripts
    console.log('\n%c[TEST 1] Module Loader Check', 'color: #ffa500; font-weight: bold;');
    try {
        const manifestResponse = await fetch('external/modules/inhouse-kanban/manifest.json');
        if (!manifestResponse.ok) throw new Error('Failed to fetch manifest');
        
        const manifest = await manifestResponse.json();
        
        if (manifest.additional_scripts && Array.isArray(manifest.additional_scripts)) {
            console.log('  ✅ Manifest has additional_scripts:', manifest.additional_scripts);
            results.passed.push('Manifest configuration');
        } else {
            console.error('  ❌ Manifest missing additional_scripts property');
            results.failed.push('Manifest configuration');
        }
    } catch (error) {
        console.error('  ❌ Failed to check manifest:', error);
        results.failed.push('Manifest check');
    }
    
    // Test 2: Check if script files exist
    console.log('\n%c[TEST 2] Script Files Check', 'color: #ffa500; font-weight: bold;');
    const scripts = [
        'external/modules/inhouse-kanban/kanban-supabase-integration.js',
        'external/modules/inhouse-kanban/kanban-supabase-ui.js'
    ];
    
    for (const scriptPath of scripts) {
        try {
            const response = await fetch(scriptPath);
            if (response.ok) {
                const size = (response.headers.get('content-length') / 1024).toFixed(2);
                console.log(`  ✅ ${scriptPath.split('/').pop()} exists (${size} KB)`);
                results.passed.push(scriptPath.split('/').pop());
            } else {
                console.error(`  ❌ ${scriptPath} - HTTP ${response.status}`);
                results.failed.push(scriptPath.split('/').pop());
            }
        } catch (error) {
            console.error(`  ❌ ${scriptPath} - ${error.message}`);
            results.failed.push(scriptPath.split('/').pop());
        }
    }
    
    // Test 3: Check if scripts are loaded in DOM
    console.log('\n%c[TEST 3] DOM Script Tags Check', 'color: #ffa500; font-weight: bold;');
    const integrationScript = document.querySelector('script[src*="kanban-supabase-integration"]');
    const uiScript = document.querySelector('script[src*="kanban-supabase-ui"]');
    
    if (integrationScript) {
        console.log('  ✅ kanban-supabase-integration.js loaded in DOM');
        console.log('     ', integrationScript.src);
        results.passed.push('Integration script tag');
    } else {
        console.error('  ❌ kanban-supabase-integration.js NOT in DOM');
        results.failed.push('Integration script tag');
    }
    
    if (uiScript) {
        console.log('  ✅ kanban-supabase-ui.js loaded in DOM');
        console.log('     ', uiScript.src);
        results.passed.push('UI script tag');
    } else {
        console.error('  ❌ kanban-supabase-ui.js NOT in DOM');
        results.failed.push('UI script tag');
    }
    
    // Test 4: Check if global objects exist
    console.log('\n%c[TEST 4] Global Objects Check', 'color: #ffa500; font-weight: bold;');
    
    if (typeof window.KanbanSupabaseIntegration !== 'undefined') {
        console.log('  ✅ window.KanbanSupabaseIntegration exists');
        console.log('     Type:', typeof window.KanbanSupabaseIntegration);
        results.passed.push('KanbanSupabaseIntegration object');
    } else {
        console.error('  ❌ window.KanbanSupabaseIntegration is undefined');
        results.failed.push('KanbanSupabaseIntegration object');
    }
    
    if (typeof window.kanbanSupabaseUI !== 'undefined') {
        console.log('  ✅ window.kanbanSupabaseUI exists');
        console.log('     Type:', typeof window.kanbanSupabaseUI);
        console.log('     Initialized:', window.kanbanSupabaseUI.initialized || false);
        results.passed.push('kanbanSupabaseUI object');
        
        // Check available methods
        const methods = Object.keys(window.kanbanSupabaseUI).filter(k => typeof window.kanbanSupabaseUI[k] === 'function');
        console.log('     Available methods:', methods.length);
        console.log('     Key methods:', methods.slice(0, 5).join(', ') + (methods.length > 5 ? '...' : ''));
    } else {
        console.error('  ❌ window.kanbanSupabaseUI is undefined');
        results.failed.push('kanbanSupabaseUI object');
    }
    
    // Test 5: Check module loader logs
    console.log('\n%c[TEST 5] Module Loader Logs Check', 'color: #ffa500; font-weight: bold;');
    console.log('  ℹ️  Check console history for:');
    console.log('     "[ModuleLoader] ✅ Loaded additional script for inhouse-kanban"');
    console.log('  ');
    console.log('  If you don\'t see these logs, the module was loaded BEFORE changes.');
    console.log('  Solution: Hard refresh (Ctrl+Shift+R) and reopen module.');
    
    // Test 6: Check if module is loaded
    console.log('\n%c[TEST 6] Module Registry Check', 'color: #ffa500; font-weight: bold;');
    
    if (window.ModuleRegistry && window.ModuleRegistry['inhouse-kanban']) {
        console.log('  ✅ InHouse Kanban module registered');
        const module = window.ModuleRegistry['inhouse-kanban'];
        console.log('     Has instance:', !!module.instance);
        console.log('     Has sidebar:', !!module.sidebar);
        console.log('     Has init function:', typeof module.init === 'function');
        results.passed.push('Module registry');
    } else {
        console.warn('  ⚠️  InHouse Kanban module not registered yet');
        console.log('     This is normal if module hasn\'t been opened yet.');
        results.warnings.push('Module not loaded (open it to load)');
    }
    
    // Summary
    console.log('\n%c=== SUMMARY ===', 'color: #00d4ff; font-size: 16px; font-weight: bold;');
    console.log(`✅ Passed: ${results.passed.length} tests`);
    console.log(`❌ Failed: ${results.failed.length} tests`);
    console.log(`⚠️  Warnings: ${results.warnings.length} items`);
    
    if (results.failed.length === 0 && results.passed.length >= 6) {
        console.log('\n%c🎉 ALL SYSTEMS GO! Supabase UI is ready to use!', 'color: #00ff00; font-size: 14px; font-weight: bold;');
        console.log('\nNext steps:');
        console.log('1. Open InHouse Kanban module (if not already open)');
        console.log('2. Run: await window.kanbanSupabaseUI.initialize()');
        console.log('3. Test card enhancement on a Kanban card');
    } else if (results.failed.some(f => f.includes('NOT in DOM') || f.includes('undefined'))) {
        console.log('\n%c⚠️  SCRIPTS NOT LOADED', 'color: #ff6b00; font-size: 14px; font-weight: bold;');
        console.log('\nLikely cause: Module was already loaded before manifest changes.');
        console.log('\nFix:');
        console.log('1. Hard refresh browser (Ctrl+Shift+R)');
        console.log('2. Clear "loadedModules" cache: window.ModuleLoader?.loadedModules?.delete("inhouse-kanban")');
        console.log('3. Reopen InHouse Kanban module');
        console.log('4. Run this diagnostic again');
    } else {
        console.log('\n%c❌ ISSUES DETECTED', 'color: #ff0000; font-size: 14px; font-weight: bold;');
        console.log('\nFailed tests:', results.failed.join(', '));
        console.log('\nCheck errors above for details.');
    }
    
    // Return results for programmatic use
    return {
        passed: results.passed.length,
        failed: results.failed.length,
        warnings: results.warnings.length,
        ready: results.failed.length === 0 && results.passed.length >= 6,
        details: results
    };
})();

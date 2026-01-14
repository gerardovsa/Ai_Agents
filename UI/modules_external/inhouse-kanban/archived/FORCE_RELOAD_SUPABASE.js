/**
 * Force Reload Supabase Integration Scripts
 * 
 * CORRECTED VERSION - Uses window.moduleLoader (lowercase)
 * 
 * Run this in browser console to force reload InHouse Kanban module
 * with Supabase integration scripts
 */

(async function forceReloadSupabase() {
    console.log('%c🔄 Forcing InHouse Kanban Module Reload...', 'color: #00d4ff; font-size: 14px; font-weight: bold;');
    
    // 1. Clear module cache
    if (window.moduleLoader && window.moduleLoader.loadedModules) {
        const wasLoaded = window.moduleLoader.loadedModules.has('inhouse-kanban');
        window.moduleLoader.loadedModules.delete('inhouse-kanban');
        console.log('✅ Cleared module cache (was loaded:', wasLoaded, ')');
    } else {
        console.warn('⚠️  window.moduleLoader not found or no loadedModules');
    }
    
    // 2. Remove existing script tags
    console.log('\n📦 Removing existing scripts...');
    const scripts = document.querySelectorAll('script[data-module="inhouse-kanban"], script[data-additional-script*="inhouse-kanban"]');
    console.log(`   Found ${scripts.length} script tags to remove`);
    scripts.forEach(s => {
        const fileName = s.src.split('/').pop();
        console.log('   🗑️  Removing:', fileName);
        s.remove();
    });
    
    // 3. Clear module registry
    if (window.ModuleRegistry && window.ModuleRegistry['inhouse-kanban']) {
        delete window.ModuleRegistry['inhouse-kanban'];
        console.log('✅ Cleared module registry');
    }
    
    // 4. Clear global references
    if (window.inhouseKanbanSidebar) {
        delete window.inhouseKanbanSidebar;
        console.log('✅ Cleared sidebar reference');
    }
    
    // 5. Reload the module
    if (window.moduleLoader) {
        console.log('\n📥 Reloading InHouse Kanban module...');
        console.log('   This will load main script + additional scripts from manifest');
        
        try {
            await window.moduleLoader.loadModule('inhouse-kanban');
            console.log('✅ Module reload complete!');
        } catch (error) {
            console.error('❌ Module reload failed:', error);
            return;
        }
        
        // 6. Check if Supabase loaded
        console.log('\n⏳ Waiting for scripts to execute...');
        setTimeout(() => {
            console.log('\n%c🔍 Verification Results:', 'color: #ffa500; font-size: 13px; font-weight: bold;');
            
            // Check integration layer
            const hasIntegration = typeof window.KanbanSupabaseIntegration !== 'undefined';
            console.log(
                `  ${hasIntegration ? '✅' : '❌'} KanbanSupabaseIntegration:`,
                hasIntegration ? 'LOADED' : 'NOT FOUND'
            );
            
            // Check UI layer
            const hasUI = typeof window.kanbanSupabaseUI !== 'undefined';
            console.log(
                `  ${hasUI ? '✅' : '❌'} kanbanSupabaseUI:`,
                hasUI ? 'LOADED' : 'NOT FOUND'
            );
            
            // Check module registry
            const hasModule = window.ModuleRegistry && window.ModuleRegistry['inhouse-kanban'];
            console.log(
                `  ${hasModule ? '✅' : '❌'} Module Registry:`,
                hasModule ? 'REGISTERED' : 'NOT REGISTERED'
            );
            
            // Check if initialized
            if (hasUI && window.kanbanSupabaseUI.initialized) {
                console.log('  ✅ UI Initialized: YES');
            } else if (hasUI) {
                console.log('  ⚠️  UI Initialized: NO (needs initialization)');
            }
            
            // Summary
            if (hasIntegration && hasUI) {
                console.log('\n%c🎉 SUCCESS! Supabase integration is now loaded!', 'color: #00ff00; font-size: 14px; font-weight: bold;');
                
                if (!window.kanbanSupabaseUI.initialized) {
                    console.log('\n📋 Next step - Initialize the UI:');
                    console.log('   await window.kanbanSupabaseUI.initialize()');
                    console.log('\n📋 Then test card enhancement:');
                    console.log('   const card = document.querySelector(".kanban-card");');
                    console.log('   await window.kanbanSupabaseUI.enhanceCard(card, 12345);');
                } else {
                    console.log('\n✅ UI is already initialized and ready to use!');
                    console.log('\n📋 Test card enhancement:');
                    console.log('   const card = document.querySelector(".kanban-card");');
                    console.log('   const ticketId = parseInt(card.dataset.ticketId);');
                    console.log('   await window.kanbanSupabaseUI.enhanceCard(card, ticketId);');
                }
            } else {
                console.log('\n%c❌ FAILED - Scripts did not load', 'color: #ff0000; font-size: 14px; font-weight: bold;');
                console.log('\n🔍 Debugging info:');
                console.log('   1. Check Network tab in DevTools for failed requests');
                console.log('   2. Look for console errors during module load');
                console.log('   3. Verify files exist:');
                console.log('      - external/modules/inhouse-kanban/kanban-supabase-integration.js');
                console.log('      - external/modules/inhouse-kanban/kanban-supabase-ui.js');
                console.log('\n💡 Alternative: Try hard refresh (Ctrl+Shift+R)');
            }
            
            // Check console logs
            console.log('\n📋 Look for these logs above:');
            console.log('   [ModuleLoader] ✅ Loaded additional script for inhouse-kanban: ...');
            console.log('   [Supabase UI] Initializing...');
            
        }, 1500); // Wait 1.5 seconds for scripts to execute
        
    } else {
        console.error('%c❌ CRITICAL ERROR', 'color: #ff0000; font-size: 14px; font-weight: bold;');
        console.error('window.moduleLoader not found!');
        console.error('\nThis means the module system is not initialized.');
        console.error('Try refreshing the page (F5) and run this script again.');
    }
})();

// ================================================
// MISSING SIDEBAR BUTTONS FIX - ONE COMMAND
// Copy-paste this entire block into browser console
// ================================================

(async function fixMissingButtons() {
    console.log('🔧 Starting button fix...');

    // Step 1: Ensure module system is initialized
    if (window.initializeModuleSystem) {
        console.log('🔄 Triggering module system initialization...');
        try {
            await window.initializeModuleSystem(false);
        } catch (e) {
            console.warn('⚠️ Initialization error (may already be initialized):', e.message);
        }
    } else {
        console.error('❌ initializeModuleSystem not found! This should never happen after the fix.');
        console.log('💡 Hard refresh the page (CTRL+SHIFT+R) to load the updated code.');
        return;
    }

    // Step 2: Wait for module loader to be ready
    let attempts = 0;
    const maxAttempts = 20;

    while ((!window.moduleLoader || !window.moduleLoader.modules || window.moduleLoader.modules.size === 0) && attempts < maxAttempts) {
        if (attempts === 0) {
            console.log('⏳ Waiting for ModuleLoader to complete initialization...');
        }
        await new Promise(resolve => setTimeout(resolve, 500));
        attempts++;
    }

    // Step 3: Final check if module loader exists
    if (!window.moduleLoader) {
        console.error('❌ ModuleLoader still not found after waiting 10 seconds!');
        console.log('💡 Check browser console for JavaScript errors during page load.');
        console.log('💡 Try: Hard refresh (CTRL+SHIFT+R) and wait for "Platform ready" message');
        return;
    }

    // Step 4: Check if modules are loaded
    if (!window.moduleLoader.modules || window.moduleLoader.modules.size === 0) {
        console.error('❌ No modules loaded! Module system initialization failed.');
        console.log('💡 Check for JavaScript errors in console.');
        return;
    }

    console.log(`✅ Found ${window.moduleLoader.modules.size} modules`);

    // Step 4: Find communication-hub and universal-search
    const comm = window.moduleLoader.modules.get('communication-hub');
    const univ = window.moduleLoader.modules.get('universal-search');

    console.log('📧 Communication Hub:', comm ? `Found (available: ${comm.available})` : '❌ NOT FOUND');
    console.log('🔍 Universal Search:', univ ? `Found (available: ${univ.available})` : '❌ NOT FOUND');

    // Step 5: Force set as available if not already
    let needsRegeneration = false;

    if (comm && !comm.available) {
        console.log('🔧 Setting communication-hub as available...');
        comm.available = true;
        needsRegeneration = true;
    }

    if (univ && !univ.available) {
        console.log('🔧 Setting universal-search as available...');
        univ.available = true;
        needsRegeneration = true;
    }

    // Step 6: Regenerate buttons if needed
    if (needsRegeneration) {
        console.log('🔄 Regenerating sidebar buttons...');
        await window.moduleLoader.generateSidebarButtons();
        console.log('✅ Buttons regenerated!');
    } else {
        console.log('✅ Both modules already available, checking buttons...');
    }

    // Step 7: Verify buttons now exist
    const container = document.getElementById('module-buttons-container');
    if (!container) {
        console.error('❌ Sidebar container not found!');
        return;
    }

    const buttonIds = Array.from(container.children).map(btn => btn.dataset.moduleId);
    const hasComm = buttonIds.includes('communication-hub');
    const hasUniv = buttonIds.includes('universal-search');

    console.log(`📊 Total buttons: ${buttonIds.length}`);
    console.log(`📧 Communication Hub button: ${hasComm ? '✅ EXISTS' : '❌ MISSING'}`);
    console.log(`🔍 Universal Search button: ${hasUniv ? '✅ EXISTS' : '❌ MISSING'}`);

    // Step 8: If still missing, create manually
    if (!hasComm && comm) {
        console.log('🔧 Manually creating Communication Hub button...');
        const btn = document.createElement('button');
        btn.className = 'sidebar-icon-btn';
        btn.title = 'Communication Hub';
        btn.dataset.moduleId = 'communication-hub';
        const icon = document.createElement('i');
        icon.className = 'fas fa-comments';
        icon.style.color = '#6366f1';
        btn.appendChild(icon);
        btn.addEventListener('click', async () => {
            console.log('📧 Communication Hub clicked');
            await window.moduleLoader.loadModule('communication-hub', 'dashboard');
        });
        container.appendChild(btn);
        console.log('✅ Communication Hub button created!');
    }

    if (!hasUniv && univ) {
        console.log('🔧 Manually creating Universal Search button...');
        const btn = document.createElement('button');
        btn.className = 'sidebar-icon-btn';
        btn.title = 'Universal Search';
        btn.dataset.moduleId = 'universal-search';
        const icon = document.createElement('i');
        icon.className = 'fas fa-search';
        icon.style.color = '#6B7280';
        btn.appendChild(icon);
        btn.addEventListener('click', async () => {
            console.log('🔍 Universal Search clicked');
            await window.moduleLoader.loadModule('universal-search', 'sidebar');
        });
        container.appendChild(btn);
        console.log('✅ Universal Search button created!');
    }

    // Step 9: Final verification
    const finalButtonIds = Array.from(container.children).map(btn => btn.dataset.moduleId);
    const finalComm = finalButtonIds.includes('communication-hub');
    const finalUniv = finalButtonIds.includes('universal-search');

    console.log('\n🎯 FINAL STATUS:');
    console.log(`   Total buttons: ${finalButtonIds.length}`);
    console.log(`   Communication Hub: ${finalComm ? '✅ READY' : '❌ FAILED'}`);
    console.log(`   Universal Search: ${finalUniv ? '✅ READY' : '❌ FAILED'}`);

    if (finalComm && finalUniv) {
        console.log('\n🎉 SUCCESS! Both buttons are now in the sidebar.');
        console.log('💡 Click them to test functionality.');
    } else {
        console.log('\n⚠️ Some buttons still missing. Check console errors above.');
    }
})();

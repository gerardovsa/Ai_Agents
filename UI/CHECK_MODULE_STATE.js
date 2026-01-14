// ===========================================================
// COMPLETE MODULE SYSTEM DIAGNOSTIC - RUN IN BROWSER CONSOLE
// ===========================================================
// Copy ALL of this and paste into browser console (F12)

console.log('\n🔍 === MODULE SYSTEM DIAGNOSTIC ===\n');

// Step 1: Check if pre-loader defined the function
console.log('Step 1: Pre-loader Check');
console.log('  window.initializeModuleSystem exists:', typeof window.initializeModuleSystem !== 'undefined' ? '✅' : '❌');

// Step 2: Check if ES6 module loaded
console.log('\nStep 2: ES6 Module Check');
console.log('  window.ModuleLoaderV4 (class) exists:', typeof window.ModuleLoaderV4 !== 'undefined' ? '✅' : '❌');
console.log('  window.moduleLoader (instance) exists:', typeof window.moduleLoader !== 'undefined' ? '✅' : '❌');

// Step 3: Check initialization state
console.log('\nStep 3: Initialization State');
if (window.ModuleLoaderV4) {
    console.log('  ModuleLoaderV4.initialized:', window.ModuleLoaderV4.initialized ? '✅' : '❌');
    console.log('  Total modules loaded:', window.ModuleLoaderV4.initialized ? window.moduleLoader.modules.size : 'N/A');
} else {
    console.log('  ❌ ModuleLoaderV4 not loaded yet');
}

// Step 4: Check module availability
console.log('\nStep 4: Module Availability Check');
if (window.moduleLoader && window.moduleLoader.modules) {
    const commHub = window.moduleLoader.modules.get('communication-hub');
    const uniSearch = window.moduleLoader.modules.get('universal-search');
    
    console.log('  Communication Hub:');
    console.log('    - Exists:', commHub ? '✅' : '❌');
    if (commHub) {
        console.log('    - Available:', commHub.available ? '✅' : '❌');
        console.log('    - Sidebar enabled:', commHub.sidebar?.enabled ? '✅' : '❌');
        console.log('    - Show button:', commHub.sidebar?.show_button ? '✅' : '❌');
    }
    
    console.log('  Universal Search:');
    console.log('    - Exists:', uniSearch ? '✅' : '❌');
    if (uniSearch) {
        console.log('    - Available:', uniSearch.available ? '✅' : '❌');
        console.log('    - Sidebar enabled:', uniSearch.sidebar?.enabled ? '✅' : '❌');
        console.log('    - Show button:', uniSearch.sidebar?.show_button ? '✅' : '❌');
    }
} else {
    console.log('  ❌ Module loader not initialized or no modules loaded');
}

// Step 5: Check sidebar buttons
console.log('\nStep 5: Sidebar Button Check');
const commButton = document.querySelector('[data-module-id="communication-hub"]');
const searchButton = document.querySelector('[data-module-id="universal-search"]');

console.log('  Communication Hub button in DOM:', commButton ? '✅' : '❌');
console.log('  Universal Search button in DOM:', searchButton ? '✅' : '❌');

// Step 6: Backend API check
console.log('\nStep 6: Backend API Check (fetching...)');
fetch('/api/modules/available?user_id=1')
    .then(res => res.json())
    .then(data => {
        console.log('  Total available modules from API:', data.available_modules?.length || 0);
        const commAvail = data.available_modules?.find(m => m.id === 'communication-hub');
        const searchAvail = data.available_modules?.find(m => m.id === 'universal-search');
        
        console.log('  Communication Hub API:');
        console.log('    - In response:', commAvail ? '✅' : '❌');
        if (commAvail) {
            console.log('    - capabilities.sidebar.enabled:', commAvail.capabilities?.sidebar?.enabled ? '✅' : '❌');
            console.log('    - capabilities.sidebar.show_button:', commAvail.capabilities?.sidebar?.show_button ? '✅' : '❌');
        }
        
        console.log('  Universal Search API:');
        console.log('    - In response:', searchAvail ? '✅' : '❌');
        if (searchAvail) {
            console.log('    - capabilities.sidebar.enabled:', searchAvail.capabilities?.sidebar?.enabled ? '✅' : '❌');
            console.log('    - capabilities.sidebar.show_button:', searchAvail.capabilities?.sidebar?.show_button ? '✅' : '❌');
        }
        
        console.log('\n📊 DIAGNOSTIC SUMMARY:');
        const preloaderOk = typeof window.initializeModuleSystem !== 'undefined';
        const moduleLoaded = typeof window.moduleLoader !== 'undefined';
        const initialized = window.ModuleLoaderV4?.initialized || false;
        const commExists = commAvail !== undefined;
        const searchExists = searchAvail !== undefined;
        const commButton = document.querySelector('[data-module-id="communication-hub"]') !== null;
        const searchButton = document.querySelector('[data-module-id="universal-search"]') !== null;
        
        console.log('  Pre-loader:', preloaderOk ? '✅' : '❌ FAILED');
        console.log('  Module loaded:', moduleLoaded ? '✅' : '❌ FAILED');
        console.log('  Initialized:', initialized ? '✅' : '❌ FAILED');
        console.log('  Backend returns comm-hub:', commExists ? '✅' : '❌ FAILED');
        console.log('  Backend returns uni-search:', searchExists ? '✅' : '❌ FAILED');
        console.log('  Comm-hub button exists:', commButton ? '✅' : '❌ MISSING');
        console.log('  Uni-search button exists:', searchButton ? '✅' : '❌ MISSING');
        
        console.log('\n🎯 NEXT STEPS:');
        if (!preloaderOk) {
            console.log('  ❌ Pre-loader failed - HTML file may not be updated. Hard refresh again (CTRL+SHIFT+R)');
        } else if (!moduleLoaded) {
            console.log('  ❌ ES6 module failed to load - Check browser console for JavaScript errors');
        } else if (!initialized) {
            console.log('  ❌ Module system not initialized - Try running: await window.initializeModuleSystem(true)');
        } else if (!commExists || !searchExists) {
            console.log('  ❌ Modules not returned by API - Check Flask backend and manifest files');
        } else if (!commButton || !searchButton) {
            console.log('  ❌ Buttons not generated - Run FIX_MISSING_BUTTONS.js to manually create them');
        } else {
            console.log('  ✅ Everything looks correct! Buttons should be visible in sidebar.');
        }
    })
    .catch(err => {
        console.error('  ❌ Backend API error:', err);
        console.log('  Make sure Flask server is running on port 5001');
    });

console.log('\n=== END DIAGNOSTIC ===\n');

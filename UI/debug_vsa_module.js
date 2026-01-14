/**
 * VSA Module Debug Console Command
 * 
 * USAGE: Paste this into browser console, then call:
 *   debugVSA()
 * 
 * Shows complete module state, utility composition, and DOM container status
 */

window.debugVSA = function () {
    console.log('\n='.repeat(80));
    console.log('🔍 VSA VETERINARY ALERTS MODULE DEBUG');
    console.log('='.repeat(80));

    // 1. Check if module is registered
    console.log('\n📦 MODULE REGISTRY:');
    if (window.ModuleRegistry && window.ModuleRegistry.modules) {
        const vsaModule = window.ModuleRegistry.modules.get('vsa-veterinary-alerts');
        if (vsaModule) {
            console.log('  ✅ Module registered in ModuleRegistry');
            console.log('  📋 Module metadata:', {
                moduleId: vsaModule.moduleId,
                version: vsaModule.version,
                framework: vsaModule.framework,
                hasDependencies: !!vsaModule.dependencies,
                requestedUtilities: vsaModule.dependencies?.utilities || []
            });
        } else {
            console.log('  ❌ Module NOT found in ModuleRegistry');
        }
    } else {
        console.log('  ⚠️  ModuleRegistry not available');
    }

    // 2. Check module loader state
    console.log('\n🔄 MODULE LOADER STATE:');
    if (window.ModuleLoaderV4) {
        const loader = window.ModuleLoaderV4;
        console.log('  ✅ ModuleLoaderV4 available');
        console.log('  📊 Loaded modules:', loader.loadedModules ? loader.loadedModules.size : 'unknown');

        if (loader.loadedModules && loader.loadedModules.has('vsa-veterinary-alerts')) {
            const moduleData = loader.loadedModules.get('vsa-veterinary-alerts');
            console.log('  ✅ VSA module is loaded');
            console.log('  📋 Module data:', moduleData);
        } else {
            console.log('  ❌ VSA module NOT in loaded modules map');
        }
    } else {
        console.log('  ❌ ModuleLoaderV4 not available');
    }

    // 3. Check UtilityComposer
    console.log('\n🛠️  UTILITY COMPOSER:');
    if (window.UtilityComposer || (window.ModuleUtilities && window.ModuleUtilities.UtilityComposer)) {
        const composer = window.UtilityComposer || window.ModuleUtilities.UtilityComposer;
        console.log('  ✅ UtilityComposer available');
        console.log('  📋 Available utilities:', Object.keys(composer.availableUtilities || {}));
    } else {
        console.log('  ❌ UtilityComposer not available');
    }

    // 4. Check DOM containers
    console.log('\n📦 DOM CONTAINERS:');
    const containers = [
        'tab-vsa-veterinary-alerts',
        'vsa-alerts-dashboard',
        'vsa-sidebar-container'
    ];

    containers.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            console.log(`  ✅ #${id}:`, {
                exists: true,
                visible: window.getComputedStyle(el).display !== 'none',
                hasContent: el.children.length > 0,
                childCount: el.children.length,
                classes: el.className
            });
        } else {
            console.log(`  ❌ #${id}: NOT FOUND`);
        }
    });

    // 5. Check if module instance exists
    console.log('\n🎯 MODULE INSTANCE:');
    if (window.VSAVeterinaryAlerts) {
        console.log('  ✅ VSAVeterinaryAlerts global exists');
        console.log('  📋 Instance properties:', {
            hasUtilities: !!window.VSAVeterinaryAlerts.utilities,
            hasDom: !!window.VSAVeterinaryAlerts.dom,
            hasApi: !!window.VSAVeterinaryAlerts.api,
            hasStorage: !!window.VSAVeterinaryAlerts.storage,
            hasEvents: !!window.VSAVeterinaryAlerts.events,
            hasLog: !!window.VSAVeterinaryAlerts.log,
            hasContainer: !!window.VSAVeterinaryAlerts.container,
            hasSupabaseClient: !!window.VSAVeterinaryAlerts.state?.supabaseClient
        });

        // Check which utilities are actually available
        console.log('  🔍 Utility methods check:');
        if (window.VSAVeterinaryAlerts.dom) {
            console.log('    ✅ dom.on:', typeof window.VSAVeterinaryAlerts.dom.on);
            console.log('    ✅ dom.getContainer:', typeof window.VSAVeterinaryAlerts.dom.getContainer);
        } else {
            console.log('    ❌ dom: undefined');
        }

        if (window.VSAVeterinaryAlerts.log) {
            console.log('    ✅ log.info:', typeof window.VSAVeterinaryAlerts.log.info);
            console.log('    ✅ log.error:', typeof window.VSAVeterinaryAlerts.log.error);
        } else {
            console.log('    ❌ log: undefined');
        }
    } else {
        console.log('  ⚠️  VSAVeterinaryAlerts not exposed globally (expected for V4 modules)');
    }

    // 6. Check recent console logs
    console.log('\n📝 RECENT CONSOLE ACTIVITY:');
    console.log('  💡 Check console above for these key messages:');
    console.log('    - [UtilityComposer] Composing for vsa-veterinary-alerts');
    console.log('    - [UtilityComposer] Composed utilities for vsa-veterinary-alerts: [...]');
    console.log('    - [vsa-veterinary-alerts] VSA Alerts Dashboard loading...');
    console.log('    - [vsa-veterinary-alerts] Container found/created');

    // 7. Recommended actions
    console.log('\n💡 TROUBLESHOOTING STEPS:');
    console.log('  1️⃣  Check if dependencies declared in module:');
    console.log('     - Look for: dependencies: { utilities: [...] }');
    console.log('     - Should include: [\'dom\', \'api\', \'storage\', \'events\']');
    console.log('\n  2️⃣  Verify UtilityComposer.compose() was called:');
    console.log('     - Look for console log: "[UtilityComposer] Composing for vsa-veterinary-alerts"');
    console.log('     - Should show: "requested: [\'dom\', \'api\', \'storage\', \'events\']"');
    console.log('\n  3️⃣  Check if utilities were stored in module:');
    console.log('     - onDashboardLoad should have: this.dom = dom; this.api = api; etc.');
    console.log('\n  4️⃣  Hard refresh browser:');
    console.log('     - CTRL+SHIFT+R to bypass cache');
    console.log('     - Or clear cache in DevTools');

    // 8. Quick test command
    console.log('\n🧪 QUICK TEST:');
    console.log('  Run this to test utility composition:');
    console.log('  ```');
    console.log('  import("/shared/js/module-utilities.js").then(module => {');
    console.log('    const composer = module.UtilityComposer;');
    console.log('    const testUtils = composer.compose({');
    console.log('      utilities: ["dom", "api", "storage", "events"]');
    console.log('    }, "vsa-veterinary-alerts");');
    console.log('    console.log("Test composition result:", Object.keys(testUtils));');
    console.log('  });');
    console.log('  ```');

    console.log('\n' + '='.repeat(80));
    console.log('✅ DEBUG COMPLETE');
    console.log('='.repeat(80) + '\n');

    return {
        message: 'Debug info logged above. Scroll up to see full report.',
        quickChecks: {
            moduleRegistered: !!(window.ModuleRegistry?.modules?.has('vsa-veterinary-alerts')),
            moduleLoaded: !!(window.ModuleLoaderV4?.loadedModules?.has('vsa-veterinary-alerts')),
            utilityComposerAvailable: !!(window.UtilityComposer || window.ModuleUtilities?.UtilityComposer),
            containerExists: !!document.getElementById('tab-vsa-veterinary-alerts'),
            moduleInstanceExists: !!window.VSAVeterinaryAlerts
        }
    };
};

// Auto-run on load if VSA module button is visible
console.log('💡 VSA Debug Command Loaded!');
console.log('📌 Usage: Type debugVSA() in console to inspect module state');
console.log('📌 Quick access: window.debugVSA()');

/**
 * VSA Veterinary Alerts - Browser Console Verification Script
 * 
 * Copy and paste this into your browser console to test the module
 */

(async function verifyVSAModule() {
    console.log('%c=== VSA Veterinary Alerts Module Verification ===', 'color: #d32f2f; font-size: 16px; font-weight: bold;');

    const results = {
        passed: [],
        failed: [],
        warnings: []
    };

    // Test 1: Check ModuleLoaderV4 exists
    console.log('\n%c[Test 1] Checking ModuleLoaderV4...', 'color: #1E88E5; font-weight: bold;');
    if (typeof window.ModuleLoaderV4 !== 'undefined') {
        console.log('✅ ModuleLoaderV4 found');
        results.passed.push('ModuleLoaderV4 exists');
    } else {
        console.error('❌ ModuleLoaderV4 not found - module loader not initialized');
        results.failed.push('ModuleLoaderV4 not found');
        return results;
    }

    const loader = window.ModuleLoaderV4;

    // Test 2: Check module available
    console.log('\n%c[Test 2] Checking module availability...', 'color: #1E88E5; font-weight: bold;');
    const isAvailable = loader.isModuleAvailable('vsa-veterinary-alerts');
    if (isAvailable) {
        console.log('✅ vsa-veterinary-alerts module is available');
        results.passed.push('Module available');
    } else {
        console.error('❌ vsa-veterinary-alerts module not found in registry');
        results.failed.push('Module not available');
        return results;
    }

    // Test 3: Check manifest
    console.log('\n%c[Test 3] Checking manifest.json...', 'color: #1E88E5; font-weight: bold;');
    const manifest = loader.getModuleManifest('vsa-veterinary-alerts');
    if (manifest) {
        console.log('✅ Manifest loaded:');
        console.log('   - ID:', manifest.id);
        console.log('   - Name:', manifest.name);
        console.log('   - Version:', manifest.version);
        console.log('   - Type:', manifest.type);
        console.log('   - Category:', manifest.category);

        // Check utilities
        if (manifest.dependencies && manifest.dependencies.utilities) {
            console.log('   - Utilities:', manifest.dependencies.utilities.join(', '));
            results.passed.push('Manifest valid with utilities');
        } else {
            console.warn('⚠️  Manifest missing dependencies.utilities');
            results.warnings.push('Missing dependencies.utilities in manifest');
        }
    } else {
        console.error('❌ Manifest not found');
        results.failed.push('Manifest not found');
    }

    // Test 4: Load module
    console.log('\n%c[Test 4] Loading module (dashboard)...', 'color: #1E88E5; font-weight: bold;');
    try {
        await loader.loadModule('vsa-veterinary-alerts', 'dashboard');
        console.log('✅ Module loaded successfully');
        results.passed.push('Module loaded');
    } catch (error) {
        console.error('❌ Failed to load module:', error);
        results.failed.push('Module load failed: ' + error.message);
        return results;
    }

    // Test 5: Check module instance
    console.log('\n%c[Test 5] Checking module instance...', 'color: #1E88E5; font-weight: bold;');
    const isLoaded = loader.isModuleLoaded('vsa-veterinary-alerts');
    if (isLoaded) {
        console.log('✅ Module is loaded');
        results.passed.push('Module instance exists');

        // Get instance
        const instance = loader.moduleInstances.get('vsa-veterinary-alerts');
        if (instance) {
            console.log('✅ Module instance accessible');

            // Check utilities injected
            console.log('\n%c[Test 5a] Checking utilities injection...', 'color: #1E88E5; font-weight: bold;');
            const utilities = ['dom', 'api', 'storage', 'events', 'log'];
            const missingUtilities = utilities.filter(u => !instance[u]);

            if (missingUtilities.length === 0) {
                console.log('✅ All utilities injected:', utilities.join(', '));
                results.passed.push('All utilities injected');
            } else {
                console.error('❌ Missing utilities:', missingUtilities.join(', '));
                results.failed.push('Missing utilities: ' + missingUtilities.join(', '));
            }

            // Check state
            console.log('\n%c[Test 5b] Checking module state...', 'color: #1E88E5; font-weight: bold;');
            if (instance.state) {
                console.log('✅ Module state exists');
                console.log('   - Supabase URL:', instance.state.supabaseUrl);
                console.log('   - Alerts:', instance.state.alerts.length);
                console.log('   - Follow-ups:', instance.state.followUps.length);
                console.log('   - Loading:', instance.state.loading);
                console.log('   - Error:', instance.state.error || 'None');
                console.log('   - View:', instance.state.view);
                console.log('   - Last Refresh:', instance.state.lastRefresh || 'Never');

                results.passed.push('Module state valid');

                // Check Supabase client
                if (instance.state.supabaseClient) {
                    console.log('✅ Supabase client initialized');
                    results.passed.push('Supabase client initialized');
                } else {
                    console.warn('⚠️  Supabase client not initialized (might still be loading)');
                    results.warnings.push('Supabase client not initialized');
                }

                // Check data loaded
                if (instance.state.alerts.length > 0 || instance.state.followUps.length > 0) {
                    console.log('✅ Data loaded successfully');
                    console.log('   - Total alerts:', instance.state.alerts.length);
                    console.log('   - Total follow-ups:', instance.state.followUps.length);
                    results.passed.push('Data loaded from Supabase');
                } else if (instance.state.loading) {
                    console.log('⏳ Data still loading...');
                    results.warnings.push('Data still loading');
                } else if (instance.state.error) {
                    console.error('❌ Data load error:', instance.state.error);
                    results.failed.push('Data load error: ' + instance.state.error);
                } else {
                    console.warn('⚠️  No data loaded (might be empty database)');
                    results.warnings.push('No data loaded');
                }

            } else {
                console.error('❌ Module state missing');
                results.failed.push('Module state missing');
            }

        } else {
            console.error('❌ Module instance not accessible');
            results.failed.push('Module instance not accessible');
        }
    } else {
        console.error('❌ Module not loaded');
        results.failed.push('Module not loaded');
    }

    // Test 6: Check stats
    console.log('\n%c[Test 6] Checking module stats...', 'color: #1E88E5; font-weight: bold;');
    const stats = loader.getStats();
    console.log('Module Loader Stats:');
    console.log('   - Total modules:', stats.total);
    console.log('   - Available modules:', stats.available);
    console.log('   - Loaded modules:', stats.loaded);
    console.log('   - Modern modules:', stats.modern);
    console.log('   - Legacy modules:', stats.legacy);
    results.passed.push('Module stats retrieved');

    // Summary
    console.log('\n%c=== Verification Summary ===', 'color: #d32f2f; font-size: 16px; font-weight: bold;');
    console.log(`%c✅ Passed: ${results.passed.length}`, 'color: #388e3c; font-weight: bold;');
    results.passed.forEach(p => console.log('   -', p));

    if (results.warnings.length > 0) {
        console.log(`%c⚠️  Warnings: ${results.warnings.length}`, 'color: #f57c00; font-weight: bold;');
        results.warnings.forEach(w => console.log('   -', w));
    }

    if (results.failed.length > 0) {
        console.log(`%c❌ Failed: ${results.failed.length}`, 'color: #d32f2f; font-weight: bold;');
        results.failed.forEach(f => console.log('   -', f));
    }

    // Final verdict
    console.log('\n%c=== Final Verdict ===', 'color: #d32f2f; font-size: 16px; font-weight: bold;');
    if (results.failed.length === 0) {
        console.log('%c🎉 ALL TESTS PASSED! Module is working correctly.', 'color: #388e3c; font-size: 14px; font-weight: bold;');
    } else {
        console.log('%c❌ TESTS FAILED. See errors above for details.', 'color: #d32f2f; font-size: 14px; font-weight: bold;');
    }

    // Additional debug info
    console.log('\n%c=== Debug Commands ===', 'color: #1E88E5; font-size: 14px; font-weight: bold;');
    console.log('Enable debug mode:', 'window.ModuleLoaderV4.enableDebug()');
    console.log('Get module instance:', 'window.ModuleLoaderV4.moduleInstances.get("vsa-veterinary-alerts")');
    console.log('Reload module:', 'await window.ModuleLoaderV4.reloadModule("vsa-veterinary-alerts")');
    console.log('Unload module:', 'await window.ModuleLoaderV4.unloadModule("vsa-veterinary-alerts")');

    return results;
})();

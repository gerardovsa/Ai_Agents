/**
 * FILE: UI/modules/threads/thread_manager.js
 * PURPOSE: Modular thread management system - MAIN LOADER
 * 
 * ARCHITECTURE:
 * This file orchestrates the loading of modular components instead of being a monolithic 12,959-line file.
 * Components are loaded on-demand to reduce initial bundle size and improve maintainability.
 * 
 * COMPONENTS:
 * - thread_manager_core.js (461 lines) - Core thread management, welcome system, assignment logic
 * - message_store.js (150 lines) - Message caching with duplicate detection
 * - device_lock_manager.js (350 lines) - Multi-device thread locking
 * - user_auth.js (500 lines) - Authentication system
 * - thread_ui.js (~2000 lines) - UI rendering methods
 * - synergy_board.js (~4000 lines) - Kanban board integration
 * 
 * TOTAL: 12,959 lines -> 7 focused modules (~400-2000 lines each)
 * 
 * EXPORTS:
 * - ThreadManager (from core) - Main thread management
 * - MessageStore (from message_store) - Message storage
 * - DeviceLockManager (from device_lock) - Device locking
 * - UserAuth (from user_auth) - Authentication
 * 
 * DEPENDENCIES:
 * - Component files in components/ folder
 * 
 * LAST MODIFIED: 2025-11-20 - Refactored from monolithic 12,959-line file
 */

(async function initializeThreadManager() {
    console.log('[ThreadManager Loader] Starting modular initialization...');

    // Track component loading
    const componentsToLoad = [
        { name: 'MessageStore', path: 'components/message_store.js', critical: true },
        { name: 'DeviceLockManager', path: 'components/device_lock_manager.js', critical: true },
        { name: 'ThreadManagerCore', path: 'components/thread_manager_core.js', critical: true }
    ];

    const loadedComponents = [];
    const failedComponents = [];

    // Load each component dynamically
    for (const component of componentsToLoad) {
        try {
            console.log(`[ThreadManager Loader] Loading ${component.name}...`);
            
            // Create script element
            const script = document.createElement('script');
            script.src = `modules/threads/${component.path}`;
            script.async = false; // Maintain load order
            
            // Wait for script to load
            await new Promise((resolve, reject) => {
                script.onload = () => {
                    console.log(`[ThreadManager Loader] ${component.name} loaded`);
                    loadedComponents.push(component.name);
                    resolve();
                };
                script.onerror = () => {
                    console.error(`[ThreadManager Loader] Failed to load ${component.name}`);
                    failedComponents.push(component.name);
                    if (component.critical) {
                        reject(new Error(`Critical component ${component.name} failed to load`));
                    } else {
                        resolve(); // Non-critical, continue
                    }
                };
                document.head.appendChild(script);
            });

        } catch (error) {
            console.error(`[ThreadManager Loader] Error loading ${component.name}:`, error);
            if (component.critical) {
                throw error;
            }
        }
    }

    // Wait for all components to be available
    await new Promise(resolve => setTimeout(resolve, 100));

    // Verify all critical components loaded
    const missingComponents = [];
    if (typeof window.MessageStore === 'undefined') missingComponents.push('MessageStore');
    if (typeof window.DeviceLockManager === 'undefined') missingComponents.push('DeviceLockManager');
    if (typeof window.ThreadManager === 'undefined') missingComponents.push('ThreadManager');

    if (missingComponents.length > 0) {
        console.error('[ThreadManager Loader] Missing components:', missingComponents);
        throw new Error(`Critical components failed to load: ${missingComponents.join(', ')}`);
    }

    // Initialize components in order
    console.log('[ThreadManager Loader] Initializing components...');

    // 1. MessageStore (no async init needed - auto-initialized in module)
    console.log('[ThreadManager Loader] MessageStore ready');

    // 2. DeviceLockManager (needs async init)
    if (typeof DeviceLockManager.init === 'function') {
        await DeviceLockManager.init();
    }

    // 3. ThreadManager init method (will be called by main app after auth)
    console.log('[ThreadManager Loader] ThreadManager ready (init deferred until after auth)');

    // Report loading stats
    console.log('[ThreadManager Loader] Initialization complete');
    console.log('[ThreadManager Loader] Loaded components:', loadedComponents);
    if (failedComponents.length > 0) {
        console.warn('[ThreadManager Loader] Failed components (non-critical):', failedComponents);
    }

    // Dispatch ready event
    window.dispatchEvent(new CustomEvent('threadmanager-ready', {
        detail: {
            loadedComponents,
            failedComponents,
            timestamp: new Date().toISOString()
        }
    }));

})().catch(error => {
    console.error('[ThreadManager Loader] FATAL: Initialization failed:', error);
    // Show error to user
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = 'position:fixed;top:20px;right:20px;background:#ff4444;color:white;padding:16px;border-radius:8px;z-index:10000;max-width:400px;';
    errorDiv.innerHTML = `
        <strong>ThreadManager Failed to Load</strong><br>
        <small>${error.message}</small><br>
        <button onclick="location.reload()" style="margin-top:8px;padding:4px 12px;background:white;color:#ff4444;border:none;border-radius:4px;cursor:pointer;">
            Reload Page
        </button>
    `;
    document.body.appendChild(errorDiv);
});

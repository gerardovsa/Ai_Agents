/**
 * FILE: UI/modules_internal/synergy/synergy-manager.js
 * PURPOSE: Central manager for Synergy integration features
 * 
 * EXPORTS:
 * - SynergyManager (class) - Manages synergy session integration with threads
 * 
 * DEPENDENCIES:
 * - Synergy module scripts (must be loaded first)
 * 
 * LAST MODIFIED: 2025-12-01 - Created to resolve SynergyManager initialization
 */

if (typeof SynergyManager === 'undefined') {
    class SynergyManager {
        constructor() {
            this.initialized = false;
            this.activeSessions = new Map();
            this.init();
        }

        async init() {
            if (this.initialized) {
                console.debug('[SynergyManager] Already initialized');
                return;
            }

            console.log('[SynergyManager] Initializing synergy integration...');

            // Initialize synergy features if available
            if (typeof window.initializeSynergyBoard === 'function') {
                try {
                    await window.initializeSynergyBoard();
                    console.log('[SynergyManager] Board initialized');
                } catch (error) {
                    console.debug('[SynergyManager] Board initialization skipped:', error.message);
                }
            }

            // Initialize thread integration if available
            if (typeof window.initializeSynergyThreadIntegration === 'function') {
                try {
                    window.initializeSynergyThreadIntegration();
                    console.log('[SynergyManager] Thread integration initialized');
                } catch (error) {
                    console.debug('[SynergyManager] Thread integration skipped:', error.message);
                }
            }

            this.initialized = true;
            console.log('✅ [SynergyManager] Initialization complete');
        }

        // Get active synergy sessions
        getActiveSessions() {
            return Array.from(this.activeSessions.values());
        }

        // Link synergy session to thread
        linkSessionToThread(sessionId, threadSlug) {
            this.activeSessions.set(threadSlug, sessionId);
            console.log(`[SynergyManager] Linked session ${sessionId} to thread ${threadSlug}`);
        }

        // Unlink synergy session from thread
        unlinkSessionFromThread(threadSlug) {
            const sessionId = this.activeSessions.get(threadSlug);
            this.activeSessions.delete(threadSlug);
            console.log(`[SynergyManager] Unlinked session from thread ${threadSlug}`);
            return sessionId;
        }

        // Check if thread has linked synergy session
        hasLinkedSession(threadSlug) {
            return this.activeSessions.has(threadSlug);
        }

        // Get linked session for thread
        getLinkedSession(threadSlug) {
            return this.activeSessions.get(threadSlug);
        }
    }

    // Export to global scope
    window.SynergyManager = SynergyManager;
    console.log('📦 [SynergyManager] Class loaded');
}

/**
 * Thread Location Constants
 * Single source of truth for all thread location values
 * Prevents typos and makes refactoring easier
 */

export const THREAD_LOCATIONS = {
    // Unassigned - thread exists but not displayed in any panel
    UNASSIGNED: 'unassigned',

    // Prime AI chat panel (actively loaded)
    PRIME: 'prime',

    // Legacy support (will be merged with PRIME later)
    // PRIME_LOADED removed - use PRIME instead

    // Synergy collaborative board
    SYNERGY: 'synergy',

    // Agent columns (Alpha through Zulu, 1-26)
    agent: (id) => `agent-${id}`,

    // Validation helper
    isAgent: (location) => location && location.startsWith('agent-'),
    isUnassigned: (location) => location === 'unassigned',
    isPrime: (location) => location === 'prime',
    isSynergy: (location) => location === 'synergy'
};

// Make available globally for non-module scripts
if (typeof window !== 'undefined') {
    window.THREAD_LOCATIONS = THREAD_LOCATIONS;
}

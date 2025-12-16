/**
 * FILE: UI/shared/js/typing-indicators.js
 * PURPOSE: Real-time typing indicators for multi-agent collaboration
 * 
 * FEATURES:
 * - Show "User is typing..." indicators
 * - Per-agent typing indicators
 * - Global typing indicators
 * - Auto-hide after 10 seconds
 * - Animated dots
 * 
 * DEPENDENCIES:
 * - synergy-realtime.js (WebSocket events)
 * 
 * USAGE:
 * - TypingIndicators.show('John Doe', 'Alpha-1')
 * - TypingIndicators.hide('John Doe', 'Alpha-1')
 */

window.TypingIndicators = {
    indicators: new Map(), // Map<agentId|'global', Set<userName>>
    timeouts: new Map(),   // Map<userName+agentId, timeoutId>
    
    /**
     * Show typing indicator for user
     * @param {string} userName - Name of user typing
     * @param {string|null} agentId - Agent ID (null for global)
     */
    show(userName, agentId = null) {
        const key = agentId || 'global';
        
        // Get or create user set for this location
        if (!this.indicators.has(key)) {
            this.indicators.set(key, new Set());
        }
        
        const users = this.indicators.get(key);
        users.add(userName);
        
        // Render indicator
        this._render(key);
        
        // Clear existing timeout
        const timeoutKey = `${userName}:${key}`;
        if (this.timeouts.has(timeoutKey)) {
            clearTimeout(this.timeouts.get(timeoutKey));
        }
        
        // Auto-hide after 10 seconds
        const timeoutId = setTimeout(() => {
            this.hide(userName, agentId);
        }, 10000);
        
        this.timeouts.set(timeoutKey, timeoutId);
    },
    
    /**
     * Hide typing indicator for user
     * @param {string} userName - Name of user
     * @param {string|null} agentId - Agent ID (null for global)
     */
    hide(userName, agentId = null) {
        const key = agentId || 'global';
        
        if (!this.indicators.has(key)) {
            return;
        }
        
        const users = this.indicators.get(key);
        users.delete(userName);
        
        // Clear timeout
        const timeoutKey = `${userName}:${key}`;
        if (this.timeouts.has(timeoutKey)) {
            clearTimeout(this.timeouts.get(timeoutKey));
            this.timeouts.delete(timeoutKey);
        }
        
        // Remove set if empty
        if (users.size === 0) {
            this.indicators.delete(key);
        }
        
        // Re-render
        this._render(key);
    },
    
    /**
     * Clear all typing indicators
     */
    clearAll() {
        // Clear all timeouts
        this.timeouts.forEach(timeoutId => clearTimeout(timeoutId));
        this.timeouts.clear();
        
        // Clear all indicators
        this.indicators.forEach((users, key) => {
            this._render(key); // Remove UI
        });
        
        this.indicators.clear();
    },
    
    /**
     * Render typing indicator for location
     * @param {string} key - Location key (agentId or 'global')
     */
    _render(key) {
        const users = this.indicators.get(key);
        const containerId = key === 'global' 
            ? 'typing-indicator-global' 
            : `typing-indicator-${key}`;
        
        let container = document.getElementById(containerId);
        
        // Remove if no users typing
        if (!users || users.size === 0) {
            if (container) {
                container.remove();
            }
            return;
        }
        
        // Create container if doesn't exist
        if (!container) {
            container = document.createElement('div');
            container.id = containerId;
            container.className = 'typing-indicator';
            
            // Find target location to insert
            const target = this._findInsertTarget(key);
            if (target) {
                target.parentNode.insertBefore(container, target);
            } else {
                console.warn('[TYPING] Could not find insert target for', key);
                return;
            }
        }
        
        // Generate text
        const userArray = Array.from(users);
        let text;
        
        if (userArray.length === 1) {
            text = `${userArray[0]} is typing...`;
        } else if (userArray.length === 2) {
            text = `${userArray[0]} and ${userArray[1]} are typing...`;
        } else {
            text = `${userArray[0]} and ${userArray.length - 1} others are typing...`;
        }
        
        // Update content
        container.innerHTML = `
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
            <span class="typing-text">${text}</span>
        `;
    },
    
    /**
     * Find DOM target to insert typing indicator before
     * @param {string} key - Location key
     * @returns {HTMLElement|null}
     */
    _findInsertTarget(key) {
        if (key === 'global') {
            // Insert above global chat input area
            return document.getElementById('chat-input-area') 
                || document.querySelector('.chat-input-container')
                || document.querySelector('textarea[placeholder*="message"]');
        } else {
            // Insert above agent-specific input
            return document.getElementById(`agent-input-${key}`)
                || document.querySelector(`[data-agent-id="${key}"] textarea`)
                || document.querySelector(`#${key} .agent-input`);
        }
    }
};

// Initialize event listeners from WebSocket
if (typeof SynergyRealtime !== 'undefined') {
    // Wait for connection
    const initListeners = () => {
        if (!SynergyRealtime.socket) {
            setTimeout(initListeners, 100);
            return;
        }
        
        // Listen for typing events
        SynergyRealtime.socket.on('user_typing', (data) => {
            TypingIndicators.show(data.user_name, data.agent_id);
        });
        
        SynergyRealtime.socket.on('user_stopped_typing', (data) => {
            TypingIndicators.hide(data.user_name, data.agent_id);
        });
        
        console.log('[TYPING] Event listeners initialized');
    };
    
    initListeners();
}

// Inject CSS styles
const typingStyles = document.createElement('style');
typingStyles.textContent = `
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: var(--bg-tertiary, #2a2d35);
        border-radius: 6px;
        margin-bottom: 8px;
        font-size: 13px;
        color: var(--text-secondary, #a0a0a0);
        animation: typing-fade-in 0.2s ease-out;
    }
    
    @keyframes typing-fade-in {
        from {
            opacity: 0;
            transform: translateY(-5px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .typing-dots {
        display: flex;
        gap: 4px;
    }
    
    .typing-dots span {
        width: 6px;
        height: 6px;
        background: var(--accent-primary, #4a9eff);
        border-radius: 50%;
        animation: typing-bounce 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing-bounce {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.7;
        }
        30% {
            transform: translateY(-8px);
            opacity: 1;
        }
    }
    
    .typing-text {
        font-style: italic;
    }
`;
document.head.appendChild(typingStyles);

console.log('[TYPING INDICATORS] Loaded and ready');

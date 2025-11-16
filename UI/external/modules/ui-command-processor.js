/**
 * UI Command Processor Module
 * 
 * Processes UI commands returned from multi-agent coordination tools.
 * Enables automatic UI updates like tab switching, agent column opening,
 * thread info display, and cross-thread request notifications.
 * 
 * Commands supported:
 * - switch_tab: Switch to Multi-Agent or Synergy tab
 * - open_agent_column: Expand and highlight agent column
 * - show_thread_info: Display thread info card with badges
 * - trigger_agent_request: Load thread and trigger AI processing
 * - show_cross_thread_request: Show visual request indicator
 * - notify_thread_response: Notify when response arrives
 * 
 * Usage:
 * 1. Include this script in business-ai-platform-v2.html
 * 2. Emit 'tool-response-received' event when tools return ui_commands
 * 3. Processor handles all UI updates automatically
 */

const UICommandProcessor = {
    
    /**
     * Process array of UI commands from tool response
     * @param {Array} commands - Array of command objects
     */
    processCommands: function(commands) {
        if (!Array.isArray(commands)) {
            console.warn('[UICommandProcessor] Commands must be an array');
            return;
        }
        
        console.log(`[UICommandProcessor] Processing ${commands.length} commands`);
        
        commands.forEach((cmd, index) => {
            try {
                this.executeCommand(cmd, index);
            } catch (error) {
                console.error(`[UICommandProcessor] Error executing command ${index}:`, error, cmd);
            }
        });
    },
    
    /**
     * Execute a single command
     * @param {Object} cmd - Command object with 'command' field
     * @param {Number} index - Command index for logging
     */
    executeCommand: function(cmd, index) {
        const commandType = cmd.command;
        
        console.log(`[UICommandProcessor] Executing command ${index}: ${commandType}`);
        
        switch (commandType) {
            case 'switch_tab':
                this.switchTab(cmd);
                break;
                
            case 'open_agent_column':
                this.openAgentColumn(cmd);
                break;
                
            case 'show_thread_info':
                this.showThreadInfo(cmd);
                break;
                
            case 'trigger_agent_request':
                this.triggerAgentRequest(cmd);
                break;
                
            case 'show_cross_thread_request':
                this.showCrossThreadRequest(cmd);
                break;
                
            case 'notify_thread_response':
                this.notifyThreadResponse(cmd);
                break;
                
            default:
                console.warn(`[UICommandProcessor] Unknown command: ${commandType}`);
        }
    },
    
    /**
     * Switch to specified tab
     * @param {Object} cmd - {tab_name: 'multi-agent' | 'synergy'}
     */
    switchTab: function(cmd) {
        const tabName = cmd.tab_name;
        
        if (tabName === 'multi-agent') {
            // Find and click Multi-Agent tab
            const multiAgentTab = document.querySelector('[data-tab="multi-agent"], .tab-button[onclick*="multiAgent"]');
            if (multiAgentTab) {
                multiAgentTab.click();
                console.log('[UICommandProcessor] Switched to Multi-Agent tab');
            } else {
                console.warn('[UICommandProcessor] Multi-Agent tab not found');
            }
        } else if (tabName === 'synergy') {
            // Find and click Synergy tab
            const synergyTab = document.querySelector('[data-tab="synergy"], .tab-button[onclick*="synergy"]');
            if (synergyTab) {
                synergyTab.click();
                console.log('[UICommandProcessor] Switched to Synergy tab');
            } else {
                console.warn('[UICommandProcessor] Synergy tab not found');
            }
        }
    },
    
    /**
     * Open and highlight agent column
     * @param {Object} cmd - {agent_location, agent_number, agent_name, highlight}
     */
    openAgentColumn: function(cmd) {
        const agentNum = cmd.agent_number;
        const agentName = cmd.agent_name;
        const shouldHighlight = cmd.highlight !== false;
        
        // Find agent column by data attribute or ID
        const agentColumn = document.querySelector(`[data-agent="${agentNum}"], #agent-${agentNum}, .agent-column[data-agent-number="${agentNum}"]`);
        
        if (!agentColumn) {
            console.warn(`[UICommandProcessor] Agent column ${agentNum} not found`);
            return;
        }
        
        // Expand if collapsed
        const isCollapsed = agentColumn.classList.contains('collapsed');
        if (isCollapsed) {
            const expandButton = agentColumn.querySelector('.expand-button, .toggle-button');
            if (expandButton) {
                expandButton.click();
            }
        }
        
        // Scroll into view
        agentColumn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Highlight effect
        if (shouldHighlight) {
            agentColumn.classList.add('agent-highlight');
            setTimeout(() => {
                agentColumn.classList.remove('agent-highlight');
            }, 2000);
        }
        
        console.log(`[UICommandProcessor] Opened agent column: ${agentName} (${agentNum})`);
    },
    
    /**
     * Show thread info card with resource badges
     * @param {Object} cmd - {thread_id, thread_location, badges: {workflow, internal_doc, synergy}}
     */
    showThreadInfo: function(cmd) {
        const threadId = cmd.thread_id;
        const location = cmd.thread_location;
        const badges = cmd.badges || {};
        
        // Find agent column
        const agentNum = parseInt(location.split('-')[1]);
        const agentColumn = document.querySelector(`[data-agent="${agentNum}"], #agent-${agentNum}`);
        
        if (!agentColumn) {
            console.warn(`[UICommandProcessor] Agent column not found for ${location}`);
            return;
        }
        
        // Find or create thread info container
        let threadInfo = agentColumn.querySelector('.thread-info-container');
        if (!threadInfo) {
            threadInfo = document.createElement('div');
            threadInfo.className = 'thread-info-container';
            agentColumn.appendChild(threadInfo);
        }
        
        // Build badges HTML
        let badgesHtml = '';
        if (badges.workflow) {
            badgesHtml += `<span class="resource-badge workflow-badge" title="${badges.workflow}">Workflow</span>`;
        }
        if (badges.internal_doc) {
            badgesHtml += `<span class="resource-badge doc-badge" title="${badges.internal_doc}">Docs</span>`;
        }
        if (badges.synergy) {
            badgesHtml += `<span class="resource-badge synergy-badge">Synergy</span>`;
        }
        
        // Update thread info display
        threadInfo.innerHTML = `
            <div class="thread-info-card" data-thread-id="${threadId}">
                <div class="thread-id-label">Thread: ${threadId.substring(0, 8)}...</div>
                <div class="resource-badges">${badgesHtml}</div>
            </div>
        `;
        
        // Update synergy card if synergy_session_id present
        if (badges.synergy) {
            this.updateSynergyCardThreads(threadId, location);
        }
        
        console.log(`[UICommandProcessor] Showed thread info for ${threadId} in ${location}`);
    },
    
    /**
     * Trigger agent AI processing
     * @param {Object} cmd - {thread_id, agent_location, message_id}
     */
    triggerAgentRequest: function(cmd) {
        const threadId = cmd.thread_id;
        const location = cmd.agent_location;
        
        // Load thread into agent if not already loaded
        if (typeof MultiAgent !== 'undefined' && MultiAgent.loadThreadIntoAgent) {
            const agentNum = parseInt(location.split('-')[1]);
            
            // Get thread data
            if (typeof ThreadManager !== 'undefined' && ThreadManager.getThreadById) {
                const thread = ThreadManager.getThreadById(threadId);
                if (thread) {
                    MultiAgent.loadThreadIntoAgent(agentNum, thread);
                    console.log(`[UICommandProcessor] Loaded thread ${threadId} into agent ${agentNum}`);
                    
                    // Trigger AI request
                    setTimeout(() => {
                        const sendButton = document.querySelector(`#agent-${agentNum} .send-button, [data-agent="${agentNum}"] .send-button`);
                        if (sendButton) {
                            sendButton.click();
                            console.log(`[UICommandProcessor] Triggered AI request for agent ${agentNum}`);
                        }
                    }, 500);
                }
            }
        }
    },
    
    /**
     * Show visual indicator for cross-thread request
     * @param {Object} cmd - {request_id, target_thread_id, priority}
     */
    showCrossThreadRequest: function(cmd) {
        const requestId = cmd.request_id;
        const targetThreadId = cmd.target_thread_id;
        const priority = cmd.priority || 'medium';
        
        // Add notification badge to target agent
        // This would be enhanced based on actual UI structure
        console.log(`[UICommandProcessor] Cross-thread request ${requestId} sent to ${targetThreadId} (priority: ${priority})`);
        
        // Show toast notification
        this.showToast(`Request sent to ${targetThreadId}`, 'info');
    },
    
    /**
     * Notify when cross-thread response arrives
     * @param {Object} cmd - {source_thread_id, request_id}
     */
    notifyThreadResponse: function(cmd) {
        const sourceThreadId = cmd.source_thread_id;
        const requestId = cmd.request_id;
        
        console.log(`[UICommandProcessor] Response received for request ${requestId}`);
        
        // Show toast notification
        this.showToast('Response received from agent', 'success');
        
        // Add notification badge to source thread
        // This would be enhanced based on actual UI structure
    },
    
    /**
     * Update synergy card with linked thread info
     * @param {String} threadId - Thread ID
     * @param {String} location - Thread location (agent-N)
     */
    updateSynergyCardThreads: function(threadId, location) {
        // This would integrate with actual synergy board implementation
        console.log(`[UICommandProcessor] Updating synergy card for thread ${threadId} at ${location}`);
        
        // If synergyBoard exists, trigger update
        if (typeof synergyBoard !== 'undefined' && synergyBoard.renderLinkedThreads) {
            synergyBoard.renderLinkedThreads();
        }
    },
    
    /**
     * Show toast notification
     * @param {String} message - Notification message
     * @param {String} type - Notification type (info, success, warning, error)
     */
    showToast: function(message, type = 'info') {
        // Find or create toast container
        let toastContainer = document.getElementById('ui-command-toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'ui-command-toast-container';
            toastContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 10000;';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `ui-command-toast ui-command-toast-${type}`;
        toast.style.cssText = `
            padding: 12px 20px;
            margin-bottom: 10px;
            border-radius: 4px;
            background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : type === 'warning' ? '#ff9800' : '#2196F3'};
            color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            animation: slideInRight 0.3s ease-out;
        `;
        toast.textContent = message;
        
        toastContainer.appendChild(toast);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                toastContainer.removeChild(toast);
            }, 300);
        }, 3000);
    }
};

// Event listener for tool responses
document.addEventListener('tool-response-received', function(event) {
    const response = event.detail;
    
    if (response && response.ui_commands) {
        console.log('[UICommandProcessor] Received tool response with UI commands:', response.ui_commands);
        UICommandProcessor.processCommands(response.ui_commands);
    }
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
    
    .agent-highlight {
        animation: agentPulse 2s ease-in-out;
        box-shadow: 0 0 20px rgba(33, 150, 243, 0.6) !important;
    }
    
    @keyframes agentPulse {
        0%, 100% {
            box-shadow: 0 0 0 rgba(33, 150, 243, 0);
        }
        50% {
            box-shadow: 0 0 20px rgba(33, 150, 243, 0.6);
        }
    }
    
    .resource-badge {
        display: inline-block;
        padding: 2px 8px;
        margin: 2px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: 600;
        color: white;
    }
    
    .workflow-badge {
        background: #2196F3;
    }
    
    .doc-badge {
        background: #4CAF50;
    }
    
    .synergy-badge {
        background: #9C27B0;
    }
    
    .thread-info-card {
        padding: 10px;
        margin: 10px 0;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .thread-id-label {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 5px;
    }
    
    .resource-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
    }
`;
document.head.appendChild(style);

console.log('[UICommandProcessor] Module loaded and ready');

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UICommandProcessor;
}

/**
 * AGENT INTERACTION BUBBLES
 * Inline message bubbles for AI-human two-way interaction
 * 
 * Features:
 * - AI Input Request bubbles (2FA, CAPTCHA, text input, choices)
 * - Progress Update bubbles (live streaming progress)
 * - Choice Request bubbles (multiple options with buttons)
 * - Screenshot Display bubbles (computer use integration)
 * - Visual states: waiting, responded, timeout
 * - Disable/enable regular input while AI waits
 * - Quick-nav badge updates (orange pulsing when waiting)
 * - Notification system integration
 * 
 * Date: December 16, 2025
 */

const AgentInteractionBubbles = (function () {
    'use strict';

    // Track active input requests per agent
    const activeRequests = {}; // agentId -> { request_id, bubble_element, timestamp }

    /**
     * Render AI Input Request bubble (inline in messages)
     * @param {number} agentId - Agent ID
     * @param {Object} data - Input request data from StreamingManager
     * @returns {HTMLElement} Bubble element
     */
    function renderInputRequestBubble(agentId, data) {
        const {
            request_id,
            prompt,
            input_type = 'text', // text, password, choice, 2fa_code, captcha
            options = [], // For choice type
            required = true,
            timeout_seconds = 300,
            metadata = {}
        } = data;

        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        if (!messagesContainer) {
            console.error(`[Interaction] Messages container not found for agent ${agentId}`);
            return null;
        }

        // Create bubble wrapper
        const bubble = document.createElement('div');
        bubble.className = 'ai-message ai-interaction-request waiting';
        bubble.id = `input-request-${request_id}`;
        bubble.dataset.requestId = request_id;
        bubble.dataset.agentId = agentId;

        // Build input field based on type
        let inputHTML = '';
        if (input_type === 'choice' && options.length > 0) {
            // Multiple choice buttons
            inputHTML = `
                <div class="interaction-choices">
                    ${options.map((opt, idx) => `
                        <button class="interaction-choice-btn" 
                                data-value="${opt}"
                                onclick="AgentInteractionBubbles.submitChoice(${agentId}, '${request_id}', '${opt}')">
                            ${opt}
                        </button>
                    `).join('')}
                </div>
            `;
        } else {
            // Text input
            const inputType = input_type === 'password' ? 'password' : 'text';
            const placeholder = input_type === '2fa_code' ? 'Enter 6-digit code' :
                input_type === 'captcha' ? 'Enter characters shown' :
                    'Type your response...';

            inputHTML = `
                <div class="interaction-input-wrapper">
                    <input type="${inputType}" 
                           id="input-field-${request_id}"
                           class="interaction-input-field"
                           placeholder="${placeholder}"
                           ${input_type === '2fa_code' ? 'maxlength="6" pattern="[0-9]{6}"' : ''}
                           ${required ? 'required' : ''}
                           autocomplete="off">
                    <div class="interaction-actions">
                        <button class="interaction-cancel-btn"
                                onclick="AgentInteractionBubbles.cancelInput(${agentId}, '${request_id}')">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                        <button class="interaction-submit-btn"
                                onclick="AgentInteractionBubbles.submitInput(${agentId}, '${request_id}')">
                            <i class="fas fa-paper-plane"></i> Submit
                        </button>
                    </div>
                </div>
            `;
        }

        // Bubble content
        bubble.innerHTML = `
            <div class="ai-message-header">
                <div class="ai-message-avatar pulsing-orange">
                    <i class="fas fa-hand-paper"></i>
                </div>
                <div class="interaction-status-badge waiting">
                    <i class="fas fa-clock"></i> Waiting for your response
                </div>
            </div>
            <div class="ai-message-content">
                <div class="interaction-prompt">
                    <i class="fas fa-info-circle"></i>
                    <span>${prompt}</span>
                </div>
                ${metadata.screenshot ? `
                    <div class="interaction-screenshot">
                        <img src="data:image/png;base64,${metadata.screenshot}" alt="Context screenshot">
                    </div>
                ` : ''}
                ${inputHTML}
                <div class="interaction-timeout">
                    <i class="fas fa-hourglass-half"></i>
                    Timeout in <span id="timeout-${request_id}">${formatTimeout(timeout_seconds)}</span>
                </div>
            </div>
        `;

        // Append to messages
        messagesContainer.appendChild(bubble);

        // Auto-focus input field
        if (input_type !== 'choice') {
            setTimeout(() => {
                const inputField = document.getElementById(`input-field-${request_id}`);
                if (inputField) inputField.focus();
            }, 100);
        }

        // Start timeout countdown
        startTimeoutCountdown(request_id, timeout_seconds);

        // Track active request
        activeRequests[agentId] = {
            request_id,
            bubble_element: bubble,
            timestamp: Date.now()
        };

        // Disable regular input
        disableAgentInput(agentId, 'AI is waiting for your response...');

        // Update quick-nav badge (orange pulsing)
        updateQuickNavBadge(agentId, 'waiting');

        // Send notification
        if (typeof showNotification === 'function') {
            showNotification(`${getAgentName(agentId)} needs your input`, 'warning');
        }

        // Auto-scroll to bubble
        setTimeout(() => bubble.scrollIntoView({ behavior: 'smooth', block: 'center' }), 200);

        console.log(`[Interaction] Rendered input request bubble for agent ${agentId}:`, request_id);
        return bubble;
    }

    /**
     * Render Progress Update bubble (non-blocking, updates in place)
     * @param {number} agentId - Agent ID
     * @param {Object} data - Progress data
     * @returns {HTMLElement} Bubble element
     */
    function renderProgressBubble(agentId, data) {
        const {
            session_id,
            current_step,
            total_steps,
            message,
            percentage
        } = data;

        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        if (!messagesContainer) return null;

        // Check if progress bubble already exists
        let bubble = document.getElementById(`progress-${session_id}`);

        if (!bubble) {
            // Create new progress bubble
            bubble = document.createElement('div');
            bubble.className = 'ai-message ai-progress-update';
            bubble.id = `progress-${session_id}`;
            messagesContainer.appendChild(bubble);
        }

        // Update content
        const percent = percentage || Math.round((current_step / total_steps) * 100);
        bubble.innerHTML = `
            <div class="ai-message-header">
                <div class="ai-message-avatar">
                    <i class="fas fa-sync fa-spin"></i>
                </div>
                <div class="progress-status-badge">
                    <i class="fas fa-tasks"></i> In Progress
                </div>
            </div>
            <div class="ai-message-content">
                <div class="progress-message">${message}</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" style="width: ${percent}%"></div>
                    <div class="progress-bar-text">${current_step} / ${total_steps} (${percent}%)</div>
                </div>
            </div>
        `;

        // Auto-scroll if near bottom
        const container = messagesContainer;
        const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 100;
        if (isNearBottom) {
            setTimeout(() => container.scrollTop = container.scrollHeight, 50);
        }

        return bubble;
    }

    /**
     * Submit user input (text/password/2FA)
     * @param {number} agentId - Agent ID
     * @param {string} requestId - Request ID
     */
    function submitInput(agentId, requestId) {
        const inputField = document.getElementById(`input-field-${requestId}`);
        const bubble = document.getElementById(`input-request-${requestId}`);

        if (!inputField || !bubble) {
            console.error('[Interaction] Input field or bubble not found');
            return;
        }

        const value = inputField.value.trim();
        if (!value) {
            inputField.classList.add('error');
            setTimeout(() => inputField.classList.remove('error'), 300);
            return;
        }

        // Mark as responded
        markAsResponded(bubble, value);

        // Send to backend via WebSocket
        sendInputResponse(agentId, requestId, value);

        // Re-enable regular input
        enableAgentInput(agentId);

        // Update quick-nav badge
        updateQuickNavBadge(agentId, 'responded');

        // Clear active request
        delete activeRequests[agentId];
    }

    /**
     * Submit choice selection
     * @param {number} agentId - Agent ID
     * @param {string} requestId - Request ID
     * @param {string} choice - Selected choice
     */
    function submitChoice(agentId, requestId, choice) {
        const bubble = document.getElementById(`input-request-${requestId}`);
        if (!bubble) return;

        // Mark as responded
        markAsResponded(bubble, choice);

        // Send to backend
        sendInputResponse(agentId, requestId, choice);

        // Re-enable input
        enableAgentInput(agentId);
        updateQuickNavBadge(agentId, 'responded');

        delete activeRequests[agentId];
    }

    /**
     * Cancel input request
     * @param {number} agentId - Agent ID
     * @param {string} requestId - Request ID
     */
    function cancelInput(agentId, requestId) {
        const bubble = document.getElementById(`input-request-${requestId}`);
        if (!bubble) return;

        // Mark as cancelled
        bubble.classList.remove('waiting');
        bubble.classList.add('cancelled');

        // Re-enable input
        enableAgentInput(agentId);
        updateQuickNavBadge(agentId, 'default');

        delete activeRequests[agentId];

        // Send cancellation to backend
        sendInputResponse(agentId, requestId, null);
    }

    /**
     * Mark bubble as responded
     * @param {HTMLElement} bubble - Bubble element
     * @param {string} value - User's response
     */
    function markAsResponded(bubble, value) {
        bubble.classList.remove('waiting');
        bubble.classList.add('responded');

        // Update status badge
        const statusBadge = bubble.querySelector('.interaction-status-badge');
        if (statusBadge) {
            statusBadge.className = 'interaction-status-badge responded';
            statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Submitted';
        }

        // Disable inputs
        const inputs = bubble.querySelectorAll('input, button');
        inputs.forEach(input => {
            input.disabled = true;
        });

        // Show submitted value
        const content = bubble.querySelector('.ai-message-content');
        if (content) {
            const responseDiv = document.createElement('div');
            responseDiv.className = 'interaction-response-display';
            responseDiv.innerHTML = `<i class="fas fa-arrow-right"></i> Your response: <strong>${value}</strong>`;
            content.appendChild(responseDiv);
        }
    }

    /**
     * Disable agent input while waiting
     * @param {number} agentId - Agent ID
     * @param {string} message - Placeholder message
     */
    function disableAgentInput(agentId, message) {
        const textarea = document.getElementById(`agent-input-${agentId}`);
        const sendBtn = document.getElementById(`agent-send-${agentId}`);

        if (textarea) {
            textarea.disabled = true;
            textarea.placeholder = message;
            textarea.classList.add('disabled');
        }

        if (sendBtn) {
            sendBtn.disabled = true;
            sendBtn.classList.add('disabled');
        }
    }

    /**
     * Re-enable agent input
     * @param {number} agentId - Agent ID
     */
    function enableAgentInput(agentId) {
        const textarea = document.getElementById(`agent-input-${agentId}`);
        const sendBtn = document.getElementById(`agent-send-${agentId}`);

        if (textarea) {
            textarea.disabled = false;
            textarea.placeholder = `Type your message to ${getAgentName(agentId)}...`;
            textarea.classList.remove('disabled');
        }

        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.classList.remove('disabled');
        }
    }

    /**
     * Update quick-nav badge state
     * @param {number} agentId - Agent ID
     * @param {string} state - State: 'waiting', 'responded', 'default'
     */
    function updateQuickNavBadge(agentId, state) {
        const badge = document.querySelector(`[data-agent-id="${agentId}"]`)?.querySelector('.agent-quick-nav-badge');
        if (!badge) return;

        badge.classList.remove('waiting', 'responded', 'has-thread');

        if (state === 'waiting') {
            badge.classList.add('waiting');
        } else if (state === 'responded') {
            badge.classList.add('responded');
            setTimeout(() => badge.classList.remove('responded'), 2000);
        } else {
            badge.classList.add('has-thread'); // Default state
        }
    }

    /**
     * Send input response to backend via WebSocket
     * @param {number} agentId - Agent ID
     * @param {string} requestId - Request ID
     * @param {*} value - User's input value
     */
    function sendInputResponse(agentId, requestId, value) {
        console.log(`[Interaction] Sending response:`, { agentId, requestId, value });

        // Use WebSocket integration if available
        if (typeof AgentInteractionWebSocket !== 'undefined') {
            const success = AgentInteractionWebSocket.sendInputResponse(agentId, requestId, value);
            if (!success) {
                showNotification('Failed to send response - connection error', 'error');
            }
            return success;
        } else {
            console.warn('AgentInteractionWebSocket module not loaded - cannot send response');
            showNotification('WebSocket not connected - response not sent', 'warning');
            return false;
        }
    }

    /**
     * Start timeout countdown
     * @param {string} requestId - Request ID
     * @param {number} seconds - Timeout in seconds
     */
    function startTimeoutCountdown(requestId, seconds) {
        const timeoutEl = document.getElementById(`timeout-${requestId}`);
        if (!timeoutEl) return;

        let remaining = seconds;
        const interval = setInterval(() => {
            remaining--;
            timeoutEl.textContent = formatTimeout(remaining);

            if (remaining <= 0) {
                clearInterval(interval);
                handleTimeout(requestId);
            }
        }, 1000);

        // Store interval ID for cleanup
        timeoutEl.dataset.intervalId = interval;
    }

    /**
     * Handle timeout
     * @param {string} requestId - Request ID
     */
    function handleTimeout(requestId) {
        const bubble = document.getElementById(`input-request-${requestId}`);
        if (!bubble) return;

        bubble.classList.remove('waiting');
        bubble.classList.add('timeout');

        const statusBadge = bubble.querySelector('.interaction-status-badge');
        if (statusBadge) {
            statusBadge.className = 'interaction-status-badge timeout';
            statusBadge.innerHTML = '<i class="fas fa-clock"></i> Timed out';
        }

        // Disable inputs
        const inputs = bubble.querySelectorAll('input, button');
        inputs.forEach(input => input.disabled = true);

        // Re-enable agent input
        const agentId = parseInt(bubble.dataset.agentId);
        if (agentId) {
            enableAgentInput(agentId);
            updateQuickNavBadge(agentId, 'default');
            delete activeRequests[agentId];
        }
    }

    /**
     * Format timeout display
     * @param {number} seconds - Seconds remaining
     * @returns {string} Formatted string
     */
    function formatTimeout(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
    }

    /**
     * Get agent name by ID
     * @param {number} agentId - Agent ID
     * @returns {string} Agent name
     */
    function getAgentName(agentId) {
        const names = { 1: 'Alpha', 2: 'Bravo', 3: 'Charlie', 4: 'Delta', 5: 'Echo', 6: 'Foxtrot', 7: 'Golf', 8: 'Hotel' };
        return names[agentId] || `Agent ${agentId}`;
    }

    // Public API
    return {
        renderInputRequestBubble,
        renderProgressBubble,
        submitInput,
        submitChoice,
        cancelInput
    };
})();

// Make globally available
window.AgentInteractionBubbles = AgentInteractionBubbles;
console.log('[AgentInteractionBubbles] Module loaded');

/**
 * CONFIRMATION BUBBLE COMPONENT
 * ==============================
 * 
 * Renders confirmation requests as interactive message bubbles
 * in the AI chat interface. Handles user responses and continues
 * the conversation seamlessly.
 * 
 * Integration with: business-ai-platform-v2.html
 * 
 * Usage:
 *   When AI tool returns {status: 'confirmation_required'},
 *   render this component in the message bubble.
 */

/* ==================== STYLES ==================== */

const confirmationBubbleStyles = `
<style>
    /* Confirmation bubble container */
    .confirmation-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        color: white;
        animation: fadeInUp 0.3s ease-out;
    }
    
    .confirmation-bubble.low {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .confirmation-bubble.medium {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .confirmation-bubble.high {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .confirmation-bubble.critical {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        border: 2px solid #ff4444;
    }
    
    /* Header section */
    .confirmation-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
    }
    
    .confirmation-icon {
        font-size: 24px;
        animation: pulse 2s infinite;
    }
    
    .confirmation-title {
        font-size: 16px;
        font-weight: 600;
        flex: 1;
    }
    
    .confirmation-level-badge {
        background: rgba(255, 255, 255, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Content section */
    .confirmation-content {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }
    
    .confirmation-summary {
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 10px;
    }
    
    .confirmation-reason {
        font-size: 12px;
        opacity: 0.9;
        font-style: italic;
        margin-bottom: 15px;
    }
    
    /* Stats section */
    .confirmation-stats {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        margin-bottom: 15px;
    }
    
    .confirmation-stat {
        display: flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.15);
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .confirmation-stat-icon {
        font-size: 14px;
    }
    
    /* Warning section */
    .confirmation-warning {
        background: rgba(255, 77, 77, 0.2);
        border-left: 4px solid #ff4d4d;
        padding: 10px 15px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
    
    .confirmation-warning-title {
        font-weight: 600;
        font-size: 13px;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .confirmation-warning-list {
        font-size: 12px;
        opacity: 0.95;
        margin-left: 20px;
    }
    
    /* Affected items */
    .confirmation-affected {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 15px;
        max-height: 150px;
        overflow-y: auto;
    }
    
    .confirmation-affected-title {
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
        opacity: 0.9;
    }
    
    .confirmation-affected-list {
        font-size: 11px;
        line-height: 1.8;
    }
    
    .confirmation-affected-item {
        padding: 2px 0;
        opacity: 0.85;
    }
    
    .confirmation-affected-more {
        font-style: italic;
        opacity: 0.7;
        margin-top: 5px;
    }
    
    /* Action buttons */
    .confirmation-actions {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    
    .confirmation-button {
        flex: 1;
        min-width: 120px;
        padding: 12px 20px;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        position: relative;
        overflow: hidden;
    }
    
    .confirmation-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .confirmation-button:active {
        transform: translateY(0);
    }
    
    .confirmation-button.primary {
        background: white;
        color: #667eea;
    }
    
    .confirmation-button.secondary {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    .confirmation-button.danger {
        background: rgba(255, 255, 255, 0.15);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .confirmation-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none !important;
    }
    
    .confirmation-button-icon {
        font-size: 16px;
    }
    
    /* Loading state */
    .confirmation-bubble.loading {
        opacity: 0.6;
        pointer-events: none;
    }
    
    .confirmation-bubble.loading::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(2px);
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.1);
        }
    }
    
    /* Responsive */
    @media (max-width: 600px) {
        .confirmation-actions {
            flex-direction: column;
        }
        
        .confirmation-button {
            width: 100%;
        }
    }
</style>
`;

/* ==================== COMPONENT RENDERER ==================== */

/**
 * Render confirmation bubble in message container
 * 
 * @param {Object} confirmation - Confirmation request object
 * @param {string} confirmation.status - Always 'confirmation_required'
 * @param {string} confirmation.level - 'low', 'medium', 'high', 'critical'
 * @param {string} confirmation.operation_summary - Short operation description
 * @param {string} confirmation.reason - Why confirmation is needed
 * @param {number} confirmation.estimated_tokens - Token estimate
 * @param {number} confirmation.estimated_cost_usd - Cost estimate
 * @param {number} confirmation.estimated_time_seconds - Time estimate
 * @param {boolean} confirmation.is_destructive - Destructive operation flag
 * @param {boolean} confirmation.is_reversible - Reversible operation flag
 * @param {Array<string>} confirmation.affected_items - List of affected items
 * @param {Array<Object>} confirmation.options - User choice options
 * @param {string} confirmation.confirmation_prompt - Full prompt text
 * @param {Function} onResponse - Callback(choice) when user clicks button
 * 
 * @returns {HTMLElement} Confirmation bubble element
 */
function renderConfirmationBubble(confirmation, onResponse) {
    const container = document.createElement('div');
    container.className = `confirmation-bubble ${confirmation.level || 'medium'}`;
    container.dataset.toolName = confirmation.tool_name;

    // Get appropriate icon based on level
    const icons = {
        'low': '💡',
        'medium': '⚠️',
        'high': '🚨',
        'critical': '⛔'
    };
    const icon = icons[confirmation.level] || '⚠️';

    // Build HTML
    let html = `
        <!-- Header -->
        <div class="confirmation-header">
            <span class="confirmation-icon">${icon}</span>
            <div class="confirmation-title">${confirmation.operation_summary}</div>
            <span class="confirmation-level-badge">${confirmation.level || 'medium'}</span>
        </div>
        
        <!-- Content -->
        <div class="confirmation-content">
            ${confirmation.reason ? `
                <div class="confirmation-reason">
                    ${confirmation.reason}
                </div>
            ` : ''}
            
            <!-- Stats -->
            ${confirmation.estimated_tokens || confirmation.estimated_cost_usd || confirmation.estimated_time_seconds ? `
                <div class="confirmation-stats">
                    ${confirmation.estimated_tokens ? `
                        <div class="confirmation-stat">
                            <span class="confirmation-stat-icon">📊</span>
                            <span>${confirmation.estimated_tokens.toLocaleString()} tokens</span>
                        </div>
                    ` : ''}
                    ${confirmation.estimated_cost_usd ? `
                        <div class="confirmation-stat">
                            <span class="confirmation-stat-icon">💰</span>
                            <span>$${confirmation.estimated_cost_usd.toFixed(4)}</span>
                        </div>
                    ` : ''}
                    ${confirmation.estimated_time_seconds ? `
                        <div class="confirmation-stat">
                            <span class="confirmation-stat-icon">⏱️</span>
                            <span>${formatTime(confirmation.estimated_time_seconds)}</span>
                        </div>
                    ` : ''}
                </div>
            ` : ''}
            
            <!-- Warnings -->
            ${confirmation.is_destructive || !confirmation.is_reversible ? `
                <div class="confirmation-warning">
                    <div class="confirmation-warning-title">
                        ⚠️ Important Warnings
                    </div>
                    <div class="confirmation-warning-list">
                        ${confirmation.is_destructive ? '• This operation is <strong>DESTRUCTIVE</strong><br>' : ''}
                        ${!confirmation.is_reversible ? '• This operation <strong>CANNOT BE UNDONE</strong><br>' : ''}
                    </div>
                </div>
            ` : ''}
            
            <!-- Affected items -->
            ${confirmation.affected_items && confirmation.affected_items.length > 0 ? `
                <div class="confirmation-affected">
                    <div class="confirmation-affected-title">
                        Affected Items (${confirmation.affected_items.length}):
                    </div>
                    <div class="confirmation-affected-list">
                        ${confirmation.affected_items.slice(0, 5).map(item =>
        `<div class="confirmation-affected-item">• ${escapeHtml(item)}</div>`
    ).join('')}
                        ${confirmation.affected_items.length > 5 ? `
                            <div class="confirmation-affected-more">
                                ... and ${confirmation.affected_items.length - 5} more
                            </div>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
        </div>
        
        <!-- Actions -->
        <div class="confirmation-actions">
            ${confirmation.options.map((option, index) => {
        const isPrimary = option.value === confirmation.default_option;
        const isDanger = option.value === 'cancel';
        const buttonClass = isPrimary ? 'primary' : (isDanger ? 'danger' : 'secondary');
        const buttonIcon = getOptionIcon(option.value);

        return `
                    <button 
                        class="confirmation-button ${buttonClass}"
                        data-value="${option.value}"
                        title="${option.description || option.label}">
                        <span class="confirmation-button-icon">${buttonIcon}</span>
                        <span>${option.label}</span>
                    </button>
                `;
    }).join('')}
        </div>
    `;

    container.innerHTML = html;

    // Add click handlers to buttons
    const buttons = container.querySelectorAll('.confirmation-button');
    buttons.forEach(button => {
        button.addEventListener('click', (e) => {
            const choice = e.currentTarget.dataset.value;

            // Disable all buttons
            buttons.forEach(btn => btn.disabled = true);
            container.classList.add('loading');

            // Call callback
            onResponse(choice, confirmation);
        });
    });

    return container;
}

/* ==================== HELPER FUNCTIONS ==================== */

function formatTime(seconds) {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return secs > 0 ? `${minutes}m ${secs}s` : `${minutes}m`;
}

function getOptionIcon(value) {
    const icons = {
        'confirm': '✓',
        'proceed': '▶️',
        'cancel': '✕',
        'metadata': '📋',
        'json': '📄',
        'pdf': '📑',
        'modify': '✏️'
    };
    return icons[value] || '•';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/* ==================== INTEGRATION WITH CHAT ==================== */

/**
 * Handle AI response that may contain confirmation requests
 * 
 * @param {Object} response - AI response object
 * @param {string} currentSessionId - Current session ID (CRITICAL for continuation)
 * @param {number} currentUserId - Current user ID
 * @returns {HTMLElement} Rendered message element
 */
function handleAIResponse(response, currentSessionId, currentUserId) {
    const messageContainer = document.createElement('div');
    messageContainer.className = 'agent-message ai';

    // Check for confirmation requests in tool results
    if (response.tool_results) {
        const confirmationRequests = response.tool_results.filter(
            result => result.status === 'confirmation_required'
        );

        if (confirmationRequests.length > 0) {
            // Handle each confirmation request
            confirmationRequests.forEach(confirmation => {
                const confirmationBubble = renderConfirmationBubble(
                    confirmation,
                    (choice, confirmedData) => {
                        handleConfirmationResponse(
                            choice,
                            confirmedData,
                            currentSessionId,
                            currentUserId
                        );
                    }
                );
                messageContainer.appendChild(confirmationBubble);
            });

            return messageContainer;
        }
    }

    // Normal message rendering (no confirmation)
    messageContainer.innerHTML = `
        <div class="agent-message-bubble">
            ${response.content || response.text || ''}
        </div>
    `;

    return messageContainer;
}

/**
 * Handle user's response to confirmation request
 * 
 * @param {string} choice - User's choice ('confirm', 'cancel', etc.)
 * @param {Object} confirmation - Original confirmation data
 * @param {string} sessionId - CRITICAL: Same session ID for continuation
 * @param {number} userId - User ID
 */
async function handleConfirmationResponse(choice, confirmation, sessionId, userId) {
    // Build natural language response
    let message;
    if (choice === 'confirm' || choice === 'proceed') {
        message = `Yes, proceed with ${confirmation.operation_summary}`;
    } else if (choice === 'cancel') {
        message = `No, cancel the operation`;
    } else if (choice === 'metadata') {
        message = `Just show me the metadata, skip full content`;
    } else if (choice === 'json') {
        message = `Return as JSON timeline`;
    } else if (choice === 'pdf') {
        message = `Convert to comprehensive PDF`;
    } else {
        message = choice; // Use choice value directly
    }

    // Send continuation request with SAME session ID
    try {
        const response = await fetch('/api/agent/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,  // CRITICAL: Same session preserves context
                user_id: userId
            })
        });

        const data = await response.json();

        // Render AI's response
        const responseElement = handleAIResponse(data, sessionId, userId);
        document.getElementById('chat-container').appendChild(responseElement);

    } catch (error) {
        console.error('Failed to send confirmation response:', error);
        alert('Failed to send response. Please try again.');
    }
}

/* ==================== EXPORT ==================== */

// Make available globally
window.renderConfirmationBubble = renderConfirmationBubble;
window.handleAIResponse = handleAIResponse;
window.confirmationBubbleStyles = confirmationBubbleStyles;

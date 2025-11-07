/**
 * USER FEEDBACK AREA COMPONENT (FEATURE 2)
 * =========================================
 * 
 * FEATURE 2: User sends instructions mid-execution (NON-BLOCKING)
 * 
 * DIFFERENCE FROM FEATURE 1 (user_interaction_tools):
 * - Feature 1: AI ASKS user → Blocking modal → User MUST respond
 * - Feature 2: User TELLS AI → Non-blocking icon → User OPTIONAL
 * 
 * HOW IT WORKS:
 * 1. AI calls show_feedback_area("Processing emails...")
 * 2. Small icon appears (bottom-right, pulsing)
 * 3. User clicks icon → panel slides up
 * 4. User types: "Focus on legal emails only"
 * 5. User clicks SEND button
 * 6. Saved to localStorage
 * 7. AI continues working...
 * 8. Next tool execution → execute_tool() reads localStorage
 * 9. Injects: "_user_feedback": "USER SAYS: Focus on legal emails"
 * 10. AI sees feedback and adjusts behavior
 * 11. Feedback cleared from localStorage
 * 
 * Integration: business-ai-platform-v2.html
 */

/* ==================== STYLES (MATCHING YOUR UI THEME) ==================== */

const feedbackAreaStyles = `
<style>
    /* Feedback Icon - Floating button */
    .user-feedback-icon {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 56px;
        height: 56px;
        background: var(--bg-tertiary, #1c2128);
        border: 1px solid var(--border-default, #30363d);
        border-radius: 50%;
        display: none;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        animation: fadeInBounce 0.4s ease-out;
    }
    
    .user-feedback-icon.visible {
        display: flex;
    }
    
    .user-feedback-icon:hover {
        background: var(--bg-hover, #21262d);
        border-color: var(--accent-primary, #58a6ff);
        transform: scale(1.05);
    }
    
    .user-feedback-icon i {
        font-size: 24px;
        color: var(--accent-primary, #58a6ff);
        animation: pulse 2s infinite;
    }
    
    .feedback-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        background: var(--accent-error, #f85149);
        color: white;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        font-size: 11px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid var(--bg-primary, #0d1117);
    }
    
    /* Feedback Container - Inside chat input area */
    .user-feedback-container {
        position: absolute;
        bottom: 100%;
        left: 0;
        right: 0;
        width: 100%;
        max-height: 300px;
        background: var(--bg-secondary, #161b22);
        border: 1px solid var(--border-default, #30363d);
        border-bottom: none;
        border-radius: 12px 12px 0 0;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.4);
        display: none;
        flex-direction: column;
        z-index: 999;
        animation: slideUp 0.3s ease-out;
        margin-bottom: 0;
    }
    
    .user-feedback-container.open {
        display: flex;
    }
    
    /* Header */
    .feedback-header {
        background: var(--bg-tertiary, #1c2128);
        border-bottom: 1px solid var(--border-default, #30363d);
        padding: 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 12px 12px 0 0;
    }
    
    .feedback-header-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .feedback-header-icon {
        font-size: 18px;
        color: var(--accent-primary, #58a6ff);
        animation: pulse 2s infinite;
    }
    
    .feedback-header-text {
        color: var(--text-primary, #f3f4f6);
        font-size: 14px;
        font-weight: 600;
    }
    
    .feedback-close-btn {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: 6px;
        padding: var(--space-2) var(--space-3);
        color: var(--text-primary);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: var(--space-2);
        transition: all 0.2s ease;
        font-size: 14px;
    }
    
    .feedback-close-btn:hover {
        background: var(--bg-tertiary);
        color: var(--text-primary, #f3f4f6);
        border: 1px solid var(--accent-primary);
        border-radius: 6px;
    }
    
    /* Controls */
    .feedback-controls {
        padding: 15px;
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        background: var(--bg-secondary, #161b22);
        border-bottom: 1px solid var(--border-default, #30363d);
    }
    
    .feedback-control-btn {
        flex: 1;
        min-width: 80px;
        background: var(--bg-tertiary, #1c2128);
        border: 1px solid var(--border-default, #30363d);
        color: var(--text-primary, #f3f4f6);
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    
    .feedback-control-btn:hover {
        background: var(--bg-hover, #21262d);
        border-color: var(--accent-primary, #58a6ff);
        transform: translateY(-1px);
    }
    
    .feedback-control-btn:active {
        transform: translateY(0);
    }
    
    /* Body */
    .feedback-body {
        flex: 1;
        padding: 15px;
        background: var(--bg-secondary, #161b22);
        overflow-y: auto;
    }
    
    .feedback-textarea {
        width: 100%;
        min-height: 100px;
        max-height: 250px;
        padding: 12px;
        border: 1px solid var(--border-default, #30363d);
        border-radius: 8px;
        background: var(--bg-primary, #0d1117);
        color: var(--text-primary, #f3f4f6);
        font-size: 14px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        resize: vertical;
        transition: border-color 0.2s ease;
    }
    
    .feedback-textarea:focus {
        outline: none;
        border-color: var(--accent-primary, #58a6ff);
        background: var(--bg-primary, #0d1117);
    }
    
    .feedback-textarea::placeholder {
        color: var(--text-muted, #9ca3af);
    }
    
    .feedback-hint {
        color: var(--text-muted, #9ca3af);
        font-size: 11px;
        margin-top: 8px;
        font-style: italic;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Button Container */
    .feedback-quick-buttons {
        display: flex;
        gap: 8px;
        margin-top: 12px;
        width: 100%;
    }
    
    /* Button Row Container (legacy support) */
    .feedback-button-row {
        display: flex;
        gap: 8px;
        margin-top: 12px;
        width: 100%;
    }
    
    /* Quick Action Buttons (Icon-only with hover text) */
    .feedback-quick-btn, .feedback-send-btn {
        flex: 1;
        min-width: 40px;
        height: 38px;
        padding: 0;
        background: var(--accent-hover, #4a93e0);
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 16px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }
    
    .feedback-quick-btn:hover,
    .feedback-send-btn:hover {
        background: var(--accent-primary, #58a6ff);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(88, 166, 255, 0.3);
    }
    
    .feedback-quick-btn:active,
    .feedback-send-btn:active {
        transform: translateY(0);
    }
    
    .feedback-send-btn:disabled {
        background: var(--bg-tertiary, #1c2128);
        color: var(--text-muted, #9ca3af);
        cursor: not-allowed;
        transform: none;
    }
    
    .feedback-send-btn i {
        font-size: 16px;
    }
    
    /* Animations */
    @keyframes slideUp {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeInBounce {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .user-feedback-container {
            right: 15px;
            width: calc(100% - 30px);
            max-width: 400px;
        }
        
        .user-feedback-icon {
            right: 15px;
            bottom: 80px;
        }
    }
</style>
`;

/* ==================== FUNCTIONS ==================== */

/**
 * Initialize feedback area (inject styles and HTML)
 */
function initFeedbackArea() {
    // Inject styles
    if (!document.getElementById('feedback-area-styles')) {
        const styleEl = document.createElement('div');
        styleEl.id = 'feedback-area-styles';
        styleEl.innerHTML = feedbackAreaStyles;
        document.head.appendChild(styleEl);
    }

    // Inject HTML if not exists
    if (!document.getElementById('user-feedback-icon')) {
        const html = `
            <!-- Feedback Icon -->
            <div class="user-feedback-icon" id="user-feedback-icon">
                <i class="fas fa-comments"></i>
                <span class="feedback-badge" id="feedback-badge" style="display: none;">!</span>
            </div>
            
            <!-- Feedback Container -->
            <div class="user-feedback-container" id="user-feedback-container">
                <div class="feedback-header">
                    <div class="feedback-header-left">
                        <i class="fas fa-comments feedback-header-icon"></i>
                        <span class="feedback-header-text" id="feedback-header-text">AI is working...</span>
                    </div>
                    <button class="feedback-close-btn" onclick="toggleFeedbackContainer()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="feedback-controls" id="feedback-controls">
                    <button class="feedback-control-btn" onclick="insertFeedback('Pause please')">
                        <i class="fas fa-pause"></i>
                        <span>Pause</span>
                    </button>
                    <button class="feedback-control-btn" onclick="insertFeedback('Stop please')">
                        <i class="fas fa-stop"></i>
                        <span>Stop</span>
                    </button>
                    <button class="feedback-control-btn" onclick="insertFeedback('Explain your progress')">
                        <i class="fas fa-info-circle"></i>
                        <span>Explain</span>
                    </button>
                </div>
                
                <div class="feedback-body">
                    <textarea 
                        class="feedback-textarea" 
                        id="user-feedback-text"
                        placeholder="Type guidance or instructions for AI..."
                        aria-label="User feedback instructions"
                    ></textarea>
                    
                    <div class="feedback-button-row">
                        <button class="feedback-quick-btn" onclick="insertFeedback('Pause please')">
                            <i class="fas fa-pause"></i>
                            <span>Pause</span>
                        </button>
                        <button class="feedback-quick-btn" onclick="insertFeedback('Stop please')">
                            <i class="fas fa-stop"></i>
                            <span>Stop</span>
                        </button>
                        <button class="feedback-quick-btn" onclick="insertFeedback('Explain your progress')">
                            <i class="fas fa-info-circle"></i>
                            <span>Explain</span>
                        </button>
                        <button class="feedback-send-btn" id="feedback-send-btn" onclick="sendFeedback()">
                            <i class="fas fa-paper-plane"></i>
                            <span>Send</span>
                        </button>
                    </div>
                    
                    <div class="feedback-hint">
                        <i class="fas fa-lightbulb"></i>
                        <span>Click Send to inject instructions into AI's next tool call</span>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', html);

        // Setup event listeners
        document.getElementById('user-feedback-icon').addEventListener('click', toggleFeedbackContainer);
    }
}

/**
 * Toggle feedback container open/closed
 */
function toggleFeedbackContainer() {
    const container = document.getElementById('user-feedback-container');
    const icon = document.getElementById('user-feedback-icon');

    if (container.classList.contains('open')) {
        container.classList.remove('open');
    } else {
        container.classList.add('open');
        // Focus textarea
        setTimeout(() => {
            document.getElementById('user-feedback-text')?.focus();
        }, 300);
    }
}

/**
 * Show feedback icon (called by AI when starting long operation)
 * 
 * @param {Object} response - Response from show_feedback_area tool
 */
function showFeedbackArea(response) {
    console.log('[FEEDBACK] Showing feedback area:', response);

    // Initialize if not done yet
    initFeedbackArea();

    const icon = document.getElementById('user-feedback-icon');
    const headerText = document.getElementById('feedback-header-text');
    const controls = document.getElementById('feedback-controls');

    if (!icon) {
        console.error('[FEEDBACK] Icon element not found');
        return;
    }

    // Update header text
    if (headerText) {
        headerText.textContent = response.message || 'AI is working...';
    }

    // Show/hide control buttons
    if (controls && response.show_buttons === false) {
        controls.style.display = 'none';
    } else if (controls) {
        controls.style.display = 'flex';
    }

    // Show icon
    icon.classList.add('visible');

    console.log('[FEEDBACK] Feedback icon shown');
}

/**
 * Hide feedback area (called by AI when task complete)
 */
function hideFeedbackArea() {
    console.log('[FEEDBACK] Hiding feedback area');

    const icon = document.getElementById('user-feedback-icon');
    const container = document.getElementById('user-feedback-container');

    if (icon) {
        icon.classList.remove('visible');
    }

    if (container) {
        container.classList.remove('open');
    }

    // Clear textarea
    clearFeedback();

    console.log('[FEEDBACK] Feedback area hidden');
}

/**
 * Insert feedback text into textarea (called by control buttons)
 * 
 * @param {string} text - Text to insert
 */
function insertFeedback(text) {
    const textarea = document.getElementById('user-feedback-text');
    if (textarea) {
        textarea.value = text;
        textarea.focus();
        console.log('[FEEDBACK] Inserted:', text);
    }
}

/**
 * Get current feedback text
 * 
 * @returns {Object} Feedback data
 */
function getCurrentFeedback() {
    const textarea = document.getElementById('user-feedback-text');
    const instructions = textarea ? textarea.value.trim() : '';

    return {
        instructions: instructions,
        has_instructions: instructions.length > 0,
        timestamp: new Date().toISOString()
    };
}

/**
 * Clear feedback textarea
 */
function clearFeedback() {
    const textarea = document.getElementById('user-feedback-text');
    if (textarea) {
        textarea.value = '';
        console.log('[FEEDBACK] Cleared');
    }
}

/**
 * Send feedback to backend (called by SEND button)
 * 
 * User clicks SEND → Saves to backend → Polls for injection confirmation → Shows visual feedback
 */
function sendFeedback() {
    const textarea = document.getElementById('user-feedback-text');
    const sendBtn = document.getElementById('feedback-send-btn');
    const headerText = document.getElementById('feedback-message');
    const instructions = textarea ? textarea.value.trim() : '';

    if (!instructions) {
        alert('Please type instructions first');
        return;
    }

    console.log('[FEEDBACK] User clicked SEND:', instructions);

    // Get session ID from window context
    const sessionId = window.currentSessionId || window.sessionId || 'default';

    // Show "Sending..." state
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }

    if (headerText) {
        headerText.textContent = 'Sending feedback...';
        headerText.style.color = '#fbbf24'; // Yellow
    }

    // Save to backend storage (for execute_tool to read)
    fetch('http://localhost:5001/api/agent/user-feedback/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: sessionId,
            instructions: instructions,
            timestamp: new Date().toISOString()
        })
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                console.log('[FEEDBACK] Sent successfully, waiting for AI to pick it up...');

                // Show "Waiting for AI..." state
                if (sendBtn) {
                    sendBtn.innerHTML = '<i class="fas fa-clock"></i>';
                }

                if (headerText) {
                    headerText.textContent = 'Waiting for AI to receive...';
                    headerText.style.color = '#fbbf24'; // Yellow
                }

                // Clear textarea
                clearFeedback();

                // Start polling for injection confirmation
                startPollingForInjection(sessionId, sendBtn, headerText);
            } else {
                console.error('[FEEDBACK] Failed to send:', result);
                resetFeedbackUI(sendBtn, headerText, 'Failed to send feedback');
                alert('Failed to send feedback. Please try again.');
            }
        })
        .catch(error => {
            console.error('[FEEDBACK] Network error:', error);
            resetFeedbackUI(sendBtn, headerText, 'Network error');
            alert('Network error. Please check connection.');
        });
}

/**
 * Poll backend for feedback injection confirmation
 * 
 * Checks every 500ms if execute_tool() has picked up the feedback
 * Shows visual confirmation when injection happens
 */
function startPollingForInjection(sessionId, sendBtn, headerText) {
    let pollCount = 0;
    const maxPolls = 60; // 30 seconds max (60 * 500ms)

    const pollInterval = setInterval(() => {
        pollCount++;

        // Stop polling after 30 seconds
        if (pollCount > maxPolls) {
            clearInterval(pollInterval);
            resetFeedbackUI(sendBtn, headerText, 'Timeout - feedback may still be picked up');
            console.warn('[FEEDBACK] Polling timeout - feedback stored but no injection detected yet');
            return;
        }

        // Check injection status
        fetch(`http://localhost:5001/api/agent/user-feedback/injection-status/${sessionId}`)
            .then(response => response.json())
            .then(data => {
                if (data.injected) {
                    // SUCCESS! AI received the feedback
                    clearInterval(pollInterval);

                    console.log('[FEEDBACK] AI RECEIVED FEEDBACK:', data.feedback);

                    // Show success state
                    if (sendBtn) {
                        sendBtn.innerHTML = '<i class="fas fa-check-circle"></i>';
                        sendBtn.style.color = '#10b981'; // Green
                    }

                    if (headerText) {
                        headerText.textContent = 'AI received your feedback!';
                        headerText.style.color = '#10b981'; // Green
                    }

                    // Auto-hide success message after 5 seconds
                    setTimeout(() => {
                        resetFeedbackUI(sendBtn, headerText, null);
                    }, 5000);
                } else {
                    // Still waiting...
                    console.log(`[FEEDBACK] Poll ${pollCount}: ${data.message}`);
                }
            })
            .catch(error => {
                console.error('[FEEDBACK] Polling error:', error);
                // Don't stop polling on network errors, just log them
            });
    }, 500); // Poll every 500ms
}

/**
 * Reset feedback UI to default state
 */
function resetFeedbackUI(sendBtn, headerText, errorMessage) {
    if (sendBtn) {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        sendBtn.style.color = ''; // Reset to default
    }

    if (headerText) {
        if (errorMessage) {
            headerText.textContent = errorMessage;
            headerText.style.color = '#f87171'; // Red

            // Reset to default after 3 seconds
            setTimeout(() => {
                headerText.textContent = 'Provide guidance to AI';
                headerText.style.color = '';
            }, 3000);
        } else {
            headerText.textContent = 'Provide guidance to AI';
            headerText.style.color = '';
        }
    }
}

/**
 * Handle fetch_user_instructions request from AI (LEGACY - not used in new flow)
 * 
 * New flow: execute_tool() automatically checks localStorage, no SSE needed
 */
async function handleFetchInstructionsRequest() {
    const feedback = getCurrentFeedback();

    // Show badge if has instructions
    const badge = document.getElementById('feedback-badge');
    if (feedback.has_instructions && badge) {
        badge.style.display = 'flex';
    } else if (badge) {
        badge.style.display = 'none';
    }

    // Clear textarea after reading
    if (feedback.has_instructions) {
        clearFeedback();
    }

    return feedback;
}

/* ==================== EXPORT ==================== */

// Make available globally
window.initFeedbackArea = initFeedbackArea;
window.showFeedbackArea = showFeedbackArea;
window.hideFeedbackArea = hideFeedbackArea;
window.toggleFeedbackContainer = toggleFeedbackContainer;
window.insertFeedback = insertFeedback;
window.getCurrentFeedback = getCurrentFeedback;
window.clearFeedback = clearFeedback;
window.sendFeedback = sendFeedback;
window.handleFetchInstructionsRequest = handleFetchInstructionsRequest;

// Auto-initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFeedbackArea);
} else {
    initFeedbackArea();
}

console.log('[FEEDBACK] Feature 2 module loaded - User sends instructions (non-blocking)');

/**
 * USER FEEDBACK AREA COMPONENT
 * =============================
 * 
 * Passive feedback collection during AI operations.
 * 
 * FEATURE: Always-on textarea where users can type guidance/instructions
 * while AI is working. AI fetches periodically (polling pattern).
 * 
 * FLOW:
 * 1. User sends message: "Analyze 50 emails"
 * 2. Feedback icon appears (show_feedback_area)
 * 3. User clicks icon to open feedback panel
 * 4. User types: "Focus on legal team"
 * 5. AI calls fetch_user_instructions() periodically
 * 6. AI receives instructions, textarea cleared
 * 7. AI adjusts behavior
 * 8. Repeat steps 4-7 as needed
 * 9. Task complete, feedback icon hidden (hide_feedback_area)
 * 
 * Integration: business-ai-platform-v2.html
 */

/* ==================== STYLES (MATCHING YOUR UI THEME) ==================== */

const feedbackAreaStyles = `
<style>
    /* Feedback Icon - Always visible when AI is working */
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
    
    /* Feedback Container - Slides up from bottom */
    .user-feedback-container {
        position: fixed;
        bottom: 0;
        right: 30px;
        width: 400px;
        max-height: 500px;
        background: var(--bg-secondary, #161b22);
        border: 1px solid var(--border-default, #30363d);
        border-bottom: none;
        border-radius: 12px 12px 0 0;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.4);
        display: none;
        flex-direction: column;
        z-index: 999;
        animation: slideUp 0.3s ease-out;
    }
    
    .user-feedback-container.open {
        display: flex;
    }
    
    /* Feedback Header */
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
        background: none;
        border: none;
        color: var(--text-muted, #9ca3af);
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 4px;
        transition: all 0.2s ease;
    }
    
    .feedback-close-btn:hover {
        background: var(--bg-hover, #21262d);
        color: var(--text-primary, #f3f4f6);
    }
    
    /* Feedback Controls */
    .feedback-controls {
        padding: 15px;
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        background: var(--bg-secondary, #161b22);
        border-bottom: 1px solid var(--border-default, #30363d);
    }
    
    .feedback-control-btn {
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
    
    /* Feedback Body */
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
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
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

/* ==================== COMPONENT ==================== */

/**
 * Render user feedback area HTML
 * 
 * @param {Object} config - Configuration
 * @param {string} config.message - Header message
 * @param {boolean} config.showButtons - Show control buttons
 * @param {string} config.containerId - Container ID for insertion
 * @returns {string} HTML for feedback area
 */
function renderFeedbackArea(config = {}) {
    const {
        message = "Working on your request...",
        showButtons = true,
        containerId = "user-feedback-area"
    } = config;

    return `
        ${feedbackAreaStyles}
<div class="user-feedback-container" id="${containerId}">
    <div class="feedback-header">
        <span class="feedback-header-icon">💬</span>
        <span>${message}</span>
    </div>

    ${showButtons ? `
            <div class="feedback-controls">
                <button class="feedback-control-btn" onclick="insertFeedback('Pause please')">
                    <span>⏸️</span>
                    <span>Pause</span>
                </button>
                <button class="feedback-control-btn" onclick="insertFeedback('Stop please')">
                    <span>⏹️</span>
                    <span>Stop</span>
                </button>
                <button class="feedback-control-btn" onclick="insertFeedback('Explain your progress')">
                    <span>🔍</span>
                    <span>Explain</span>
                </button>
            </div>
            ` : ''}

    <textarea
        class="feedback-textarea"
        id="${containerId}-text"
        placeholder="Type guidance or instructions for AI..."
        aria-label="User feedback instructions"
    ></textarea>

    <div class="feedback-hint">
        💡 AI will check this periodically and adjust its work based on your guidance
    </div>
</div>
`;
}

/**
 * Show feedback area in UI
 * 
 * @param {Object} response - Response from show_feedback_area tool
 * @param {string} insertBeforeSelector - CSS selector for insertion point
 */
function showFeedbackArea(response, insertBeforeSelector = '.ai-chat-input-container') {
    const containerId = 'user-feedback-area';

    // Remove existing if present
    const existing = document.getElementById(containerId);
    if (existing) {
        existing.remove();
    }

    // Create new feedback area
    const html = renderFeedbackArea({
        message: response.message || "Working on your request...",
        showButtons: response.show_buttons !== false,
        containerId: containerId
    });

    // Insert before chat input
    const insertPoint = document.querySelector(insertBeforeSelector);
    if (insertPoint) {
        insertPoint.insertAdjacentHTML('beforebegin', html);

        // Make visible with animation
        setTimeout(() => {
            document.getElementById(containerId).classList.add('visible');
        }, 10);

        console.log('✅ Feedback area shown');
    } else {
        console.error('❌ Could not find insertion point:', insertBeforeSelector);
    }
}

/**
 * Hide feedback area
 */
function hideFeedbackArea() {
    const container = document.getElementById('user-feedback-area');
    if (container) {
        container.classList.remove('visible');
        setTimeout(() => container.remove(), 300);
        console.log('✅ Feedback area hidden');
    }
}

/**
 * Insert feedback text into textarea
 * 
 * @param {string} text - Text to insert
 */
function insertFeedback(text) {
    const textarea = document.getElementById('user-feedback-area-text');
    if (textarea) {
        textarea.value = text;
        textarea.focus();
        console.log('✅ Inserted feedback:', text);
    }
}

/**
 * Get current feedback text (for API endpoint)
 * 
 * @returns {Object} Feedback data
 */
function getCurrentFeedback() {
    const textarea = document.getElementById('user-feedback-area-text');
    const instructions = textarea ? textarea.value.trim() : '';

    return {
        instructions: instructions,
        has_instructions: instructions.length > 0,
        timestamp: new Date().toISOString()
    };
}

/**
 * Clear feedback textarea after AI reads it
 */
function clearFeedback() {
    const textarea = document.getElementById('user-feedback-area-text');
    if (textarea) {
        textarea.value = '';
        console.log('✅ Feedback cleared');
    }
}

/* ==================== API ENDPOINT ==================== */

/**
 * Handle fetch_user_instructions request from AI
 * 
 * This is called by backend when AI uses fetch_user_instructions() tool
 */
async function handleFetchInstructionsRequest() {
    const feedback = getCurrentFeedback();

    // Clear textarea after reading
    if (feedback.has_instructions) {
        clearFeedback();
    }

    return feedback;
}

/* ==================== EXPORT ==================== */

// Make available globally
window.renderFeedbackArea = renderFeedbackArea;
window.showFeedbackArea = showFeedbackArea;
window.hideFeedbackArea = hideFeedbackArea;
window.insertFeedback = insertFeedback;
window.getCurrentFeedback = getCurrentFeedback;
window.clearFeedback = clearFeedback;
window.handleFetchInstructionsRequest = handleFetchInstructionsRequest;
window.feedbackAreaStyles = feedbackAreaStyles;

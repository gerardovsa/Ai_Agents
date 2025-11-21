/**
 * FILE: UI/modules/shared/message_renderer.js
 * PURPOSE: Unified message rendering for both AI Prime and Agent columns
 * 
 * CRITICAL DESIGN:
 * - Single HTML structure for all messages (Prime and Agent columns)
 * - Based on AI Prime's superior design (message headers, avatars, actions)
 * - Container-agnostic (works with ai-chat-messages or agent-messages-container)
 * - Supports visualization engine (TwoRuleStreamProcessor) and basic markdown
 * 
 * DEPENDENCIES:
 * - TwoRuleStreamProcessor (visualization engine) - optional
 * - marked.js (markdown rendering) - optional fallback
 * - MessageStore (centralized message storage)
 * 
 * EXPORTS:
 * - UnifiedMessageRenderer.render(container, role, content, options)
 * - UnifiedMessageRenderer.copyRenderedText(messageElement, button)
 * - UnifiedMessageRenderer.copyRawContent(messageElement, button)
 * 
 * USED BY:
 * - prime_ai_chat.js (AI Prime column)
 * - agent-js.js (Agent columns)
 * 
 * LAST MODIFIED: 2025-11-20 - Initial creation for unified message rendering
 */

const UnifiedMessageRenderer = (function () {
    'use strict';

    /**
     * Render a message in the specified container
     * 
     * @param {HTMLElement|string} container - Container element or selector (e.g., '#ai-chat-messages' or '#agent-messages-1')
     * @param {string} role - Message role: 'user', 'assistant', or 'tool'
     * @param {string|object} content - Message content (string or structured object)
     * @param {object} options - Rendering options
     * @param {boolean} options.isThinking - Show thinking animation (default: false)
     * @param {boolean} options.scrollToBottom - Auto-scroll after render (default: true)
     * @param {string} options.threadId - Thread ID for MessageStore (optional)
     * @param {boolean} options.syncToBackend - Sync to backend via MessageStore (default: false)
     * @returns {HTMLElement} Created message element
     */
    function render(container, role, content, options = {}) {
        // Resolve container
        const messagesContainer = typeof container === 'string'
            ? document.querySelector(container)
            : container;

        if (!messagesContainer) {
            console.error('[UnifiedMessageRenderer] Container not found:', container);
            return null;
        }

        // Default options
        const {
            isThinking = false,
            scrollToBottom = true,
            threadId = null,
            syncToBackend = false
        } = options;

        // Add to MessageStore if threadId provided (centralized deduplication)
        if (threadId && typeof window.MessageStore !== 'undefined') {
            window.MessageStore.addMessage(threadId, {
                role: role === 'ai' ? 'assistant' : role,
                content: content
            }, {
                checkDuplicates: true,
                syncToBackend: syncToBackend
            }).catch(err => {
                console.warn('[UnifiedMessageRenderer] MessageStore sync failed:', err);
            });
        }

        // Create message wrapper
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message ${role}${isThinking ? ' thinking' : ''}`;
        messageDiv.setAttribute('data-raw-content', typeof content === 'string' ? content : JSON.stringify(content));

        // Create message header (avatar + toggle + actions)
        const headerDiv = createMessageHeader(role, messageDiv);

        // Create message content bubble
        const contentDiv = document.createElement('div');
        contentDiv.className = 'ai-message-content';

        // Render content based on role and options
        if (isThinking) {
            // Show thinking animation
            contentDiv.innerHTML = '<div class="ai-thinking-dots"><span></span><span></span><span></span></div>';
        } else if (role === 'assistant' || role === 'ai') {
            // Render AI response with visualization engine or markdown
            renderAssistantContent(contentDiv, content);
        } else if (role === 'user') {
            // Render user message (plain text or simple markdown)
            contentDiv.textContent = extractTextContent(content);
        } else if (role === 'tool') {
            // Render tool output (formatted JSON or text)
            renderToolContent(contentDiv, content);
        } else {
            // Fallback: plain text
            contentDiv.textContent = extractTextContent(content);
        }

        // Assemble message
        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);

        // Append to container
        messagesContainer.appendChild(messageDiv);

        // Auto-scroll if enabled
        if (scrollToBottom) {
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight + 50;
            }, 50);
        }

        console.log(`[UnifiedMessageRenderer] Rendered ${role} message in`, messagesContainer.id);
        return messageDiv;
    }

    /**
     * Create message header with avatar, toggle, and action buttons
     * @param {string} role - Message role
     * @param {HTMLElement} messageDiv - Parent message div for toggle functionality
     * @returns {HTMLElement} Header div element
     */
    function createMessageHeader(role, messageDiv) {
        const headerDiv = document.createElement('div');
        headerDiv.className = 'ai-message-header';

        // Avatar icon
        const avatar = document.createElement('div');
        avatar.className = 'ai-message-avatar';

        if (role === 'user') {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        } else if (role === 'tool') {
            avatar.innerHTML = '<i class="fas fa-wrench"></i>';
        } else {
            // assistant or ai
            avatar.innerHTML = '<i class="fa-solid fa-atom"></i>';
        }

        // Toggle button (collapse/expand)
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'ai-message-toggle';
        toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
        toggleBtn.title = 'Collapse/Expand message';
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            messageDiv.classList.toggle('collapsed');
        });

        // Action buttons (copy)
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'ai-message-actions';

        // Copy rendered text button
        const copyRenderedBtn = document.createElement('button');
        copyRenderedBtn.className = 'ai-message-copy-btn';
        copyRenderedBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyRenderedBtn.title = 'Copy rendered text';
        copyRenderedBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            copyRenderedText(messageDiv, copyRenderedBtn);
        });

        // Copy raw content button
        const copyRawBtn = document.createElement('button');
        copyRawBtn.className = 'ai-message-copy-btn';
        copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
        copyRawBtn.title = 'Copy raw content';
        copyRawBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            copyRawContent(messageDiv, copyRawBtn);
        });

        actionsDiv.appendChild(copyRenderedBtn);
        actionsDiv.appendChild(copyRawBtn);

        // Assemble header
        headerDiv.appendChild(avatar);
        headerDiv.appendChild(toggleBtn);
        headerDiv.appendChild(actionsDiv);

        return headerDiv;
    }

    /**
     * Render assistant/AI content using visualization engine or markdown
     * @param {HTMLElement} contentDiv - Content container
     * @param {string|object} content - Content to render
     */
    function renderAssistantContent(contentDiv, content) {
        // Extract text content from various formats
        const contentStr = extractTextContent(content);

        if (!contentStr || contentStr.trim() === '') {
            console.warn('[UnifiedMessageRenderer] No text content found, skipping render');
            return;
        }

        console.log(`[UnifiedMessageRenderer] Rendering ${contentStr.length} chars`);

        // TRY VISUALIZATION ENGINE FIRST (if available)
        if (!window.USE_BASIC_RENDERER && typeof TwoRuleStreamProcessor !== 'undefined') {
            try {
                console.log('[UnifiedMessageRenderer] Using TwoRuleStreamProcessor...');
                const processor = new TwoRuleStreamProcessor(contentDiv);
                processor.processChunk(contentStr);

                // Verify content was rendered
                if (!contentDiv.innerHTML || contentDiv.innerHTML.trim() === '') {
                    console.warn('[UnifiedMessageRenderer] Visualization engine produced empty content, using markdown fallback');
                    renderMarkdown(contentDiv, contentStr);
                } else {
                    console.log('[UnifiedMessageRenderer] Visualization engine success');
                }
                return;
            } catch (error) {
                console.error('[UnifiedMessageRenderer] Visualization engine error:', error);
                // Fall through to markdown
            }
        }

        // FALLBACK: Markdown renderer
        renderMarkdown(contentDiv, contentStr);
    }

    /**
     * Render tool output (formatted JSON or code)
     * @param {HTMLElement} contentDiv - Content container
     * @param {string|object} content - Tool output
     */
    function renderToolContent(contentDiv, content) {
        const contentStr = typeof content === 'string' ? content : JSON.stringify(content, null, 2);

        // Wrap in code block
        const pre = document.createElement('pre');
        const code = document.createElement('code');
        code.className = 'language-json';
        code.textContent = contentStr;
        pre.appendChild(code);
        contentDiv.appendChild(pre);

        // Apply syntax highlighting if Prism.js available
        if (typeof Prism !== 'undefined') {
            Prism.highlightElement(code);
        }
    }

    /**
     * Render markdown content
     * @param {HTMLElement} contentDiv - Content container
     * @param {string} markdown - Markdown text
     */
    function renderMarkdown(contentDiv, markdown) {
        if (typeof marked !== 'undefined') {
            try {
                contentDiv.innerHTML = marked.parse(markdown);

                // Apply syntax highlighting to code blocks
                if (typeof Prism !== 'undefined') {
                    contentDiv.querySelectorAll('pre code').forEach(block => {
                        Prism.highlightElement(block);
                    });
                }
            } catch (error) {
                console.error('[UnifiedMessageRenderer] Markdown parsing error:', error);
                contentDiv.textContent = markdown;
            }
        } else {
            // No markdown library - use plain text with line breaks
            contentDiv.innerHTML = markdown.replace(/\n/g, '<br>');
        }
    }

    /**
     * Extract text content from various content formats
     * @param {string|object|array} content - Content to extract text from
     * @returns {string} Extracted text
     */
    function extractTextContent(content) {
        if (typeof content === 'string') {
            return content;
        }

        if (Array.isArray(content)) {
            // Array of content blocks (Claude API format)
            // Extract text from text blocks, skip thinking/tool_use blocks
            const textBlocks = content
                .filter(block => block && block.type === 'text')
                .map(block => block.text || '');

            if (textBlocks.length > 0) {
                return textBlocks.join('\n\n');
            }

            // If no text blocks, check for thinking blocks (Extended Thinking)
            const thinkingBlocks = content
                .filter(block => block && (block.type === 'thinking' || block.type === 'redacted_thinking'))
                .map(block => `🧠 Thinking: ${block.thinking || '[Thinking process]'}`);

            if (thinkingBlocks.length > 0) {
                return thinkingBlocks.join('\n\n');
            }

            // If no text or thinking, return empty (tool_use messages shouldn't be rendered)
            return '';
        }

        if (content && typeof content === 'object') {
            // Single content block object
            if (content.type === 'text' && content.text) {
                return content.text;
            }
            if (content.type === 'thinking' && content.thinking) {
                return `🧠 Thinking: ${content.thinking}`;
            }
            if (content.text) {
                return content.text;
            }
            if (content.content) {
                // Nested content - recurse
                return extractTextContent(content.content);
            }
            // Last resort - stringify
            return JSON.stringify(content, null, 2);
        }

        return '';
    }

    /**
     * Copy rendered text from message
     * @param {HTMLElement} messageDiv - Message element
     * @param {HTMLElement} button - Copy button element
     */
    function copyRenderedText(messageDiv, button) {
        const contentDiv = messageDiv.querySelector('.ai-message-content');
        if (!contentDiv) return;

        const text = contentDiv.innerText || contentDiv.textContent;

        navigator.clipboard.writeText(text).then(() => {
            button.classList.add('copied');
            button.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                button.classList.remove('copied');
                button.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        }).catch(err => {
            console.error('[UnifiedMessageRenderer] Copy failed:', err);
        });
    }

    /**
     * Copy raw content from message
     * @param {HTMLElement} messageDiv - Message element
     * @param {HTMLElement} button - Copy button element
     */
    function copyRawContent(messageDiv, button) {
        const rawContent = messageDiv.getAttribute('data-raw-content') || '';

        navigator.clipboard.writeText(rawContent).then(() => {
            button.classList.add('copied');
            button.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                button.classList.remove('copied');
                button.innerHTML = '<i class="fas fa-code"></i>';
            }, 2000);
        }).catch(err => {
            console.error('[UnifiedMessageRenderer] Copy failed:', err);
        });
    }

    /**
     * Update existing thinking message with real content
     * @param {HTMLElement} messageDiv - Existing message element with thinking animation
     * @param {string|object} content - New content to render
     */
    function updateThinkingMessage(messageDiv, content) {
        if (!messageDiv) return;

        // Remove thinking class
        messageDiv.classList.remove('thinking');

        // Find content div
        const contentDiv = messageDiv.querySelector('.ai-message-content');
        if (!contentDiv) return;

        // Clear thinking animation
        contentDiv.innerHTML = '';

        // Render real content
        renderAssistantContent(contentDiv, content);

        // Update raw content attribute
        messageDiv.setAttribute('data-raw-content', typeof content === 'string' ? content : JSON.stringify(content));
    }

    // Public API
    return {
        render,
        copyRenderedText,
        copyRawContent,
        updateThinkingMessage
    };
})();

// Make globally available
window.UnifiedMessageRenderer = UnifiedMessageRenderer;

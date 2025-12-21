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
            syncToBackend = false,
            createdAt = null
        } = options;

        // CRITICAL FIX: Skip rendering user messages that ONLY contain tool_result blocks
        // Backend stores tool results as role="user" but UI shouldn't show empty bubbles
        if (role === 'user' && Array.isArray(content)) {
            const hasOnlyToolResults = content.every(block =>
                block && typeof block === 'object' && block.type === 'tool_result'
            );

            if (hasOnlyToolResults && content.length > 0) {
                console.log(`[UnifiedMessageRenderer] Skipping user message with ${content.length} tool_result blocks (no visible content)`);
                return null;
            }
        }

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

        // Create message header (avatar + toggle + actions + timestamp)
        const headerDiv = createMessageHeader(role, messageDiv, createdAt || new Date().toISOString());

        // Create message content bubble
        const contentDiv = document.createElement('div');
        contentDiv.className = 'ai-message-content';

        // Render content based on role and options
        if (isThinking) {
            // Skip rendering thinking animation (doesn't display properly)
            // Content will be replaced when actual response arrives
            contentDiv.innerHTML = '';
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

        // Final render confirmation with container info
        console.log(`[UnifiedMessageRenderer] Rendered ${role} message in ${messagesContainer.id}`);
        return messageDiv;
    }

    /**
     * Create message header with avatar, toggle, and action buttons
     * @param {string} role - Message role
     * @param {HTMLElement} messageDiv - Parent message div for toggle functionality
     * @param {string} createdAt - ISO timestamp string (optional)
     * @returns {HTMLElement} Header div element
     */
    function createMessageHeader(role, messageDiv, createdAt = null) {
        const headerDiv = document.createElement('div');
        headerDiv.className = 'ai-message-header';

        // Left group: Avatar + Toggle + Actions
        const leftGroup = document.createElement('div');
        leftGroup.className = 'ai-message-header-left';

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

        // Pop-out button (opens message in clean modal)
        const popOutBtn = document.createElement('button');
        popOutBtn.className = 'ai-message-popout-btn';
        popOutBtn.innerHTML = '<i class="fas fa-external-link-alt"></i>';
        popOutBtn.title = 'Open in pop-out view';
        popOutBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openMessagePopout(messageDiv);
        });

        actionsDiv.appendChild(copyRenderedBtn);
        actionsDiv.appendChild(copyRawBtn);
        actionsDiv.appendChild(popOutBtn);

        // Assemble left group
        // For user messages, avatar should be LAST (rightmost)
        // For AI messages, avatar should be FIRST (leftmost)
        if (role === 'user') {
            leftGroup.appendChild(toggleBtn);
            leftGroup.appendChild(actionsDiv);
            leftGroup.appendChild(avatar); // Avatar LAST for user
        } else {
            leftGroup.appendChild(avatar); // Avatar FIRST for AI
            leftGroup.appendChild(toggleBtn);
            leftGroup.appendChild(actionsDiv);
        }

        // Right group: Timestamp
        const rightGroup = document.createElement('div');
        rightGroup.className = 'ai-message-header-right';

        const timestamp = document.createElement('div');
        timestamp.className = 'ai-message-timestamp';
        timestamp.textContent = formatMessageTimestamp(createdAt);
        timestamp.title = createdAt || ''; // ISO string on hover

        rightGroup.appendChild(timestamp);

        // Assemble header
        headerDiv.appendChild(leftGroup);
        headerDiv.appendChild(rightGroup);

        return headerDiv;
    }

    /**
     * Format timestamp for display
     * @param {string} createdAt - ISO timestamp string
     * @returns {string} Formatted timestamp: Mon 13 Dec 14:35
     */
    function formatMessageTimestamp(createdAt) {
        if (!createdAt) return '';

        try {
            const date = new Date(createdAt);

            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

            const day = days[date.getDay()];
            const dateNum = date.getDate();
            const month = months[date.getMonth()];
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const time = `${hours}:${minutes}`;

            // ALWAYS return full format: Mon 13 Dec 14:35
            return `${day} ${dateNum} ${month} ${time}`;
        } catch (e) {
            return '';
        }
    }

    /**
     * Render assistant/AI content using visualization engine or markdown
     * @param {HTMLElement} contentDiv - Content container
     * @param {string|object} content - Content to render
     */
    function renderAssistantContent(contentDiv, content) {
        // Handle array of content blocks (Claude API format with tool_use)
        if (Array.isArray(content)) {
            let hasRenderedContent = false;

            content.forEach((block, index) => {
                if (block.type === 'text' && block.text) {
                    // Render text block
                    const textDiv = document.createElement('div');
                    textDiv.className = 'content-block-text';

                    const textContent = block.text;
                    const startTime = performance.now();

                    // Try visualization engine first
                    if (!window.USE_BASIC_RENDERER && typeof TwoRuleStreamProcessor !== 'undefined') {
                        try {
                            const processor = new TwoRuleStreamProcessor(textDiv);
                            processor.processChunk(textContent);
                            if (!textDiv.innerHTML || textDiv.innerHTML.trim() === '') {
                                renderMarkdown(textDiv, textContent);
                            }
                        } catch (error) {
                            console.error('[UnifiedMessageRenderer] Visualization engine error:', error);
                            renderMarkdown(textDiv, textContent);
                        }
                    } else {
                        renderMarkdown(textDiv, textContent);
                    }

                    contentDiv.appendChild(textDiv);
                    hasRenderedContent = true;

                } else if (block.type === 'tool_use' && block.name) {
                    // Render tool_use block
                    const toolDiv = document.createElement('div');
                    toolDiv.className = 'tool-request-block';
                    toolDiv.innerHTML = `
                        <div class="tool-request-header">
                            <i class="fas fa-wrench"></i>
                            <span class="tool-name">Using Tool: ${block.name}</span>
                            <span class="tool-id">#${block.id || 'unknown'}</span>
                        </div>
                        <div class="tool-json-label">JSON</div>
                        <button class="tool-copy-btn" aria-label="Copy code to clipboard" title="Copy to clipboard" type="button"><i class="fas fa-copy"></i></button>
                        <pre><code class="language-json">${JSON.stringify(block.input || {}, null, 2)}</code></pre>
                    `;
                    contentDiv.appendChild(toolDiv);

                    // Add copy functionality
                    const copyBtn = toolDiv.querySelector('.tool-copy-btn');
                    const codeElement = toolDiv.querySelector('code');
                    if (copyBtn && codeElement) {
                        copyBtn.addEventListener('click', () => {
                            const code = codeElement.textContent;
                            navigator.clipboard.writeText(code).then(() => {
                                const icon = copyBtn.querySelector('i');
                                icon.className = 'fas fa-check';
                                setTimeout(() => {
                                    icon.className = 'fas fa-copy';
                                }, 2000);
                            });
                        });
                    }

                    // Apply syntax highlighting
                    if (window.codeBlockEnhancer && window.codeBlockEnhancer.initialized) {
                        window.codeBlockEnhancer.enhanceContainer(toolDiv);
                    } else if (typeof Prism !== 'undefined') {
                        toolDiv.querySelectorAll('pre code').forEach(block => {
                            Prism.highlightElement(block);
                        });
                    }

                    hasRenderedContent = true;
                }
            });

            if (!hasRenderedContent) {
                console.warn('[UnifiedMessageRenderer] No renderable content blocks found');
            }
            return;
        }

        // Extract text content from various formats (fallback for non-array content)
        const contentStr = extractTextContent(content);

        if (!contentStr || contentStr.trim() === '') {
            console.warn('[UnifiedMessageRenderer] No text content found, skipping render');
            return;
        }

        // Start timing for consolidated log
        const startTime = performance.now();
        const charCount = contentStr.length;
        let processorUsed = 'markdown';
        let success = false;

        // TRY VISUALIZATION ENGINE FIRST (if available)
        if (!window.USE_BASIC_RENDERER && typeof TwoRuleStreamProcessor !== 'undefined') {
            try {
                processorUsed = 'TwoRuleStreamProcessor';
                const processor = new TwoRuleStreamProcessor(contentDiv);
                processor.processChunk(contentStr);

                // Verify content was rendered
                if (!contentDiv.innerHTML || contentDiv.innerHTML.trim() === '') {
                    console.warn('[UnifiedMessageRenderer] Visualization engine produced empty content, using markdown fallback');
                    renderMarkdown(contentDiv, contentStr);
                    processorUsed = 'markdown (fallback)';
                    success = true;
                } else {
                    success = true;
                }
            } catch (error) {
                console.error('[UnifiedMessageRenderer] Visualization engine error:', error);
                renderMarkdown(contentDiv, contentStr);
                processorUsed = 'markdown (error fallback)';
                success = false;
            }
        } else {
            // FALLBACK: Markdown renderer
            renderMarkdown(contentDiv, contentStr);
            success = true;
        }

        // CONSOLIDATED LOG - Single summary of entire rendering flow
        const duration = (performance.now() - startTime).toFixed(2);
        const status = success ? '✅' : '❌';
        console.log(
            `[UnifiedMessageRenderer] ${charCount} chars → ${processorUsed} → ${status} Success (${duration}ms)` +
            (window.DEBUG_TWO_RULE ? ' [Debug mode ON - see detailed logs above]' : ' [Debug mode OFF - use window.DEBUG_TWO_RULE=true for details]')
        );
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

        // 🎨 ENHANCED CODE BLOCK SUPPORT
        // Use the full CodeBlockEnhancer if available (copy buttons, language labels, etc.)
        if (window.codeBlockEnhancer && window.codeBlockEnhancer.initialized) {
            window.codeBlockEnhancer.enhanceContainer(contentDiv);
        } else if (typeof Prism !== 'undefined') {
            // Fallback: Basic syntax highlighting only
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
                // Configure marked.js for better code block handling
                if (!marked._configuredForCodeBlocks) {
                    marked.setOptions({
                        breaks: true,  // Support GitHub-style line breaks
                        gfm: true,     // GitHub Flavored Markdown
                        headerIds: true,
                        mangle: false,
                        pedantic: false,
                        sanitize: false,
                        smartLists: true,
                        smartypants: false
                    });

                    // Configure renderer to open all links in new tabs
                    const renderer = new marked.Renderer();
                    const originalLinkRenderer = renderer.link.bind(renderer);
                    renderer.link = function (href, title, text) {
                        const html = originalLinkRenderer(href, title, text);
                        return html.replace('<a', '<a target="_blank" rel="noopener noreferrer"');
                    };
                    marked.use({ renderer });

                    marked._configuredForCodeBlocks = true;
                }

                contentDiv.innerHTML = marked.parse(markdown);

                // 🎨 ENHANCED CODE BLOCK SUPPORT
                // Use the full CodeBlockEnhancer if available (copy buttons, language labels, etc.)
                if (window.codeBlockEnhancer && window.codeBlockEnhancer.initialized) {
                    window.codeBlockEnhancer.enhanceContainer(contentDiv);
                } else if (typeof Prism !== 'undefined') {
                    // Fallback: Basic syntax highlighting only
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
                .map(block => `🧠 ${block.thinking || '[Thinking process]'}`);

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
                return `🧠 ${content.thinking}`;
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

    // Track z-index for stacking windows
    let nextZIndex = 10000;
    let windowCount = 0;

    /**
     * Open message in floating, movable, resizable window
     * @param {HTMLElement} messageDiv - Message element to display
     */
    function openMessagePopout(messageDiv) {
        // Get message content
        const contentDiv = messageDiv.querySelector('.ai-message-content');
        if (!contentDiv) {
            console.error('[MessagePopout] No content found in message');
            return;
        }

        windowCount++;
        const windowId = `popout-${Date.now()}-${windowCount}`;

        // Create floating window (NO overlay - non-blocking)
        const floatingWindow = document.createElement('div');
        floatingWindow.className = 'message-popout-window';
        floatingWindow.id = windowId;
        floatingWindow.style.zIndex = nextZIndex++;

        // Position with cascade offset
        const offset = (windowCount - 1) * 30;
        floatingWindow.style.left = `${50 + offset}px`;
        floatingWindow.style.top = `${50 + offset}px`;

        floatingWindow.innerHTML = `
            <div class="popout-header">
                <div class="popout-title">
                    <i class="fas fa-message"></i>
                    <span>Message View #${windowCount}</span>
                </div>
                <div class="popout-controls">
                    <button class="popout-copy-btn" title="Copy content">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button class="popout-close-btn" title="Close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="popout-content"></div>
            <div class="popout-resize-handle"></div>
        `;

        // Clone and insert content
        const popoutContent = floatingWindow.querySelector('.popout-content');
        const contentClone = contentDiv.cloneNode(true);
        popoutContent.appendChild(contentClone);

        // Add to body
        document.body.appendChild(floatingWindow);

        // Get elements
        const header = floatingWindow.querySelector('.popout-header');
        const closeBtn = floatingWindow.querySelector('.popout-close-btn');
        const copyBtn = floatingWindow.querySelector('.popout-copy-btn');
        const resizeHandle = floatingWindow.querySelector('.popout-resize-handle');

        // Close window
        const closeWindow = () => {
            floatingWindow.classList.add('closing');
            setTimeout(() => floatingWindow.remove(), 200);
        };

        closeBtn.addEventListener('click', closeWindow);

        // Copy functionality
        copyBtn.addEventListener('click', () => {
            const text = popoutContent.innerText;
            navigator.clipboard.writeText(text).then(() => {
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                }, 1500);
            }).catch(err => {
                console.error('[MessagePopout] Copy failed:', err);
            });
        });

        // Bring to front on click
        floatingWindow.addEventListener('mousedown', () => {
            floatingWindow.style.zIndex = nextZIndex++;
        });

        // Make draggable
        let isDragging = false;
        let dragOffsetX = 0;
        let dragOffsetY = 0;

        header.addEventListener('mousedown', (e) => {
            // Don't drag if clicking buttons
            if (e.target.closest('button')) return;

            isDragging = true;
            const rect = floatingWindow.getBoundingClientRect();
            dragOffsetX = e.clientX - rect.left;
            dragOffsetY = e.clientY - rect.top;
            header.style.cursor = 'grabbing';
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            const x = e.clientX - dragOffsetX;
            const y = e.clientY - dragOffsetY;

            // Keep within viewport bounds
            const maxX = window.innerWidth - 100;
            const maxY = window.innerHeight - 50;

            floatingWindow.style.left = `${Math.max(0, Math.min(x, maxX))}px`;
            floatingWindow.style.top = `${Math.max(0, Math.min(y, maxY))}px`;
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                header.style.cursor = 'grab';
            }
        });

        // Make resizable
        let isResizing = false;
        let startX = 0;
        let startY = 0;
        let startWidth = 0;
        let startHeight = 0;

        resizeHandle.addEventListener('mousedown', (e) => {
            isResizing = true;
            startX = e.clientX;
            startY = e.clientY;
            const rect = floatingWindow.getBoundingClientRect();
            startWidth = rect.width;
            startHeight = rect.height;
            e.preventDefault();
            e.stopPropagation();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;

            const newWidth = Math.max(300, startWidth + deltaX);
            const newHeight = Math.max(200, startHeight + deltaY);

            floatingWindow.style.width = `${newWidth}px`;
            floatingWindow.style.height = `${newHeight}px`;
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
            }
        });

        // Animate in
        requestAnimationFrame(() => floatingWindow.classList.add('visible'));

        console.log(`[MessagePopout] Window opened: ${windowId}`);
    }

    // Public API
    return {
        render,
        copyRenderedText,
        copyRawContent,
        updateThinkingMessage,
        openMessagePopout
    };
})();

// Make globally available
window.UnifiedMessageRenderer = UnifiedMessageRenderer;

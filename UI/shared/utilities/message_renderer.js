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
 * - UnifiedMessageRenderer.updateThinkingMessage(messageElement, content)
 * - UnifiedMessageRenderer.openMessagePopout(messageElement)
 * 
 * USED BY:
 * - prime_ai_chat.js (AI Prime column)
 * - agent-js.js (Agent columns)
 * 
 * LAST MODIFIED: 2025-01-XX - Refactored for better maintainability and performance
 */

const UnifiedMessageRenderer = (function () {
    'use strict';

    // ============================================================================
    // CONSTANTS
    // ============================================================================

    const SCROLL_OFFSET = 50;
    const SCROLL_DELAY_MS = 50;
    const ASSISTANT_ROLES = new Set(['assistant', 'ai']);
    const Z_INDEX_START = 10000;
    const Z_INDEX_MAX = 2147483647 - 1000; // Prevent overflow
    const COPY_FEEDBACK_DURATION = 2000;
    const POPOUT_CLOSE_ANIMATION_DURATION = 200;
    const MIN_POPOUT_WIDTH = 300;
    const MIN_POPOUT_HEIGHT = 200;
    const POPOUT_CASCADE_OFFSET = 30;
    const POPOUT_INITIAL_OFFSET = 50;

    // ============================================================================
    // STATE
    // ============================================================================

    let nextZIndex = Z_INDEX_START;
    let windowCount = 0;
    const activePopouts = new Map(); // Track active popouts for cleanup

    // ============================================================================
    // UTILITY FUNCTIONS
    // ============================================================================

    /**
     * Get next z-index with overflow protection
     * @returns {number} Next z-index value
     */
    function getNextZIndex() {
        if (nextZIndex > Z_INDEX_MAX) {
            console.warn('[UnifiedMessageRenderer] Z-index approaching max, resetting');
            nextZIndex = Z_INDEX_START;
        }
        return nextZIndex++;
    }

    /**
     * Validate and parse timestamp
     * @param {string|Date} timestamp - Timestamp to validate
     * @returns {Date|null} Valid Date object or null
     */
    function validateTimestamp(timestamp) {
        if (!timestamp) return null;

        try {
            const date = new Date(timestamp);
            if (isNaN(date.getTime())) {
                console.warn('[UnifiedMessageRenderer] Invalid timestamp:', timestamp);
                return null;
            }
            return date;
        } catch (e) {
            console.warn('[UnifiedMessageRenderer] Timestamp parsing error:', e);
            return null;
        }
    }

    /**
     * Format timestamp for display
     * @param {string|Date} createdAt - Timestamp to format
     * @returns {string} Formatted timestamp: Mon 13 Dec 14:35
     */
    function formatMessageTimestamp(createdAt) {
        const date = validateTimestamp(createdAt);
        if (!date) return '';

        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

        const dayName = days[date.getDay()];
        const dateNum = date.getDate();
        const month = months[date.getMonth()];
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');

        return `${dayName} ${dateNum} ${month} ${hours}:${minutes}`;
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
            // Extract text from text blocks, skip thinking/tool_use blocks
            const textBlocks = content
                .filter(block => block && block.type === 'text')
                .map(block => block.text || '');

            if (textBlocks.length > 0) {
                return textBlocks.join('\n\n');
            }

            // Check for thinking blocks (Extended Thinking)
            const thinkingBlocks = content
                .filter(block => block && (block.type === 'thinking' || block.type === 'redacted_thinking'))
                .map(block => `🧠 ${block.thinking || '[Thinking process]'}`);

            if (thinkingBlocks.length > 0) {
                return thinkingBlocks.join('\n\n');
            }

            // No text or thinking - return empty (tool_use messages shouldn't be rendered)
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
     * Check if content should be skipped (empty or tool-result only)
     * @param {string} role - Message role
     * @param {any} content - Message content
     * @returns {string|null} Skip reason or null if should render
     */
    function shouldSkipMessage(role, content) {
        // DISABLED (Jan 3, 2026): Don't skip tool_result messages - render them compactly instead
        // Users need to see the complete conversation flow including tool executions

        // DEBUG: Log what we're checking
        if (!content) {
            console.warn(`[shouldSkipMessage] ${role} message has no content`);
            return 'Empty content';
        }

        // Check for empty arrays
        if (Array.isArray(content) && content.length === 0) {
            console.warn(`[shouldSkipMessage] ${role} message has empty array content`);
            return 'Empty array content';
        }

        // Check for arrays with no visible content
        if (Array.isArray(content)) {
            const hasVisibleContent = content.some(block =>
                block && (block.type === 'text' || block.type === 'thinking' || block.type === 'tool_use' || block.type === 'tool_result')
            );
            if (!hasVisibleContent) {
                console.warn(`[shouldSkipMessage] ${role} message array has no visible content blocks:`, content.map(b => b?.type));
                return 'Array with no visible content blocks';
            }
        }

        return null;  // Don't skip - render the message
    }

    // ============================================================================
    // MARKDOWN AND SYNTAX HIGHLIGHTING
    // ============================================================================

    /**
     * Configure marked.js for better rendering
     * (Only runs once)
     */
    function configureMarked() {
        if (typeof marked === 'undefined' || marked._configuredForCodeBlocks) {
            return;
        }

        marked.setOptions({
            breaks: true,
            gfm: true,
            headerIds: true,
            mangle: false,
            pedantic: false,
            sanitize: false,
            smartLists: true,
            smartypants: false
        });

        // Configure renderer to open links in new tabs
        const renderer = new marked.Renderer();
        const originalLinkRenderer = renderer.link.bind(renderer);
        renderer.link = function (href, title, text) {
            const html = originalLinkRenderer(href, title, text);
            return html.replace('<a', '<a target="_blank" rel="noopener noreferrer"');
        };
        marked.use({ renderer });

        marked._configuredForCodeBlocks = true;
    }

    /**
     * Render markdown content
     * @param {HTMLElement} contentDiv - Content container
     * @param {string} markdown - Markdown text
     */
    function renderMarkdown(contentDiv, markdown) {
        if (typeof marked !== 'undefined') {
            try {
                configureMarked();
                contentDiv.innerHTML = marked.parse(markdown);
                enhanceCodeBlocks(contentDiv);
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
     * Apply syntax highlighting to code blocks
     * @param {HTMLElement} container - Container with code blocks
     */
    function enhanceCodeBlocks(container) {
        if (window.codeBlockEnhancer && window.codeBlockEnhancer.initialized) {
            window.codeBlockEnhancer.enhanceContainer(container);
        } else if (typeof Prism !== 'undefined') {
            container.querySelectorAll('pre code').forEach(block => {
                Prism.highlightElement(block);
            });
        }
    }

    // ============================================================================
    // CONTENT RENDERING
    // ============================================================================

    /**
     * Render tool output (formatted JSON or code)
     * @param {HTMLElement} contentDiv - Content container
     * @param {string|object} content - Tool output
     */
    function renderToolContent(contentDiv, content) {
        const contentStr = typeof content === 'string' ? content : JSON.stringify(content, null, 2);

        const pre = document.createElement('pre');
        const code = document.createElement('code');
        code.className = 'language-json';
        code.textContent = contentStr;
        pre.appendChild(code);
        contentDiv.appendChild(pre);

        enhanceCodeBlocks(contentDiv);
    }

    /**
     * Create collapsible block (for thinking and tool_use)
     * @param {object} options - Block configuration
     * @returns {HTMLElement} Collapsible block element
     */
    function createCollapsibleBlock(options) {
        const {
            type,
            icon,
            title,
            content,
            blockClass,
            iconClass,
            headerClass,
            contentClass
        } = options;

        const blockDiv = document.createElement('div');
        blockDiv.className = `${blockClass} collapsed`;

        blockDiv.innerHTML = `
            <div class="${iconClass}" title="Click to view ${type}">
                <i class="fas fa-${icon}"></i>
            </div>
            <div class="expanded-content" style="display: none;">
                <div class="${headerClass}">
                    <i class="fas fa-${icon}"></i>
                    <span>${title}</span>
                </div>
                <div class="${contentClass}"></div>
            </div>
        `;

        const iconToggle = blockDiv.querySelector(`.${iconClass}`);
        const expandedContent = blockDiv.querySelector('.expanded-content');
        const contentContainer = blockDiv.querySelector(`.${contentClass}`);
        const header = blockDiv.querySelector(`.${headerClass}`);

        // Render content
        if (typeof content === 'string') {
            renderMarkdown(contentContainer, content);
        } else {
            contentContainer.appendChild(content);
        }

        // Toggle: expand
        iconToggle.addEventListener('click', () => {
            if (blockDiv.classList.contains('collapsed')) {
                blockDiv.classList.remove('collapsed');
                iconToggle.style.display = 'none';
                expandedContent.style.display = 'block';
            }
        });

        // Toggle: collapse
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            blockDiv.classList.add('collapsed');
            iconToggle.style.display = 'flex';
            expandedContent.style.display = 'none';
        });

        return blockDiv;
    }

    /**
     * Create thinking block (Extended Thinking)
     * @param {string} thinkingContent - Thinking text
     * @returns {HTMLElement} Thinking block element
     */
    function createThinkingBlock(thinkingContent) {
        const thinkingDiv = createCollapsibleBlock({
            type: 'AI reasoning process',
            icon: 'brain',
            title: 'AI Reasoning Process',
            content: thinkingContent,
            blockClass: 'thinking-block',
            iconClass: 'thinking-icon-toggle',
            headerClass: 'thinking-header',
            contentClass: 'thinking-content'
        });

        return thinkingDiv;
    }

    /**
     * Create tool_use block
     * @param {object} toolBlock - Tool use block data
     * @returns {HTMLElement} Tool block element
     */
    function createToolUseBlock(toolBlock) {
        const { name, id, input } = toolBlock;

        const toolDiv = document.createElement('div');
        toolDiv.className = 'tool-request-block collapsed';

        toolDiv.innerHTML = `
            <div class="tool-icon-toggle" title="Click to view tool details: ${name}">
                <i class="fas fa-wrench"></i>
            </div>
            <div class="expanded-content" style="display: none;">
                <div class="tool-request-header">
                    <i class="fas fa-wrench"></i>
                    <span class="tool-name">Using Tool: ${name}</span>
                    <span class="tool-id">#${id || 'unknown'}</span>
                </div>
                <div class="tool-json-label">JSON</div>
                <button class="tool-copy-btn" aria-label="Copy code to clipboard" title="Copy to clipboard" type="button">
                    <i class="fas fa-copy"></i>
                </button>
                <pre><code class="language-json">${JSON.stringify(input || {}, null, 2)}</code></pre>
            </div>
        `;

        const iconToggle = toolDiv.querySelector('.tool-icon-toggle');
        const expandedContent = toolDiv.querySelector('.expanded-content');
        const header = toolDiv.querySelector('.tool-request-header');

        // Toggle: expand
        iconToggle.addEventListener('click', () => {
            if (toolDiv.classList.contains('collapsed')) {
                toolDiv.classList.remove('collapsed');
                iconToggle.style.display = 'none';
                expandedContent.style.display = 'block';
            }
        });

        // Toggle: collapse
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            toolDiv.classList.add('collapsed');
            iconToggle.style.display = 'flex';
            expandedContent.style.display = 'none';
        });

        // Copy functionality
        const copyBtn = toolDiv.querySelector('.tool-copy-btn');
        const codeElement = toolDiv.querySelector('code');
        copyBtn.addEventListener('click', () => {
            const code = codeElement.textContent;
            navigator.clipboard.writeText(code).then(() => {
                const icon = copyBtn.querySelector('i');
                icon.className = 'fas fa-check';
                setTimeout(() => {
                    icon.className = 'fas fa-copy';
                }, COPY_FEEDBACK_DURATION);
            });
        });

        enhanceCodeBlocks(toolDiv);

        return toolDiv;
    }

    /**
     * Render assistant/AI content using visualization engine or markdown
     * @param {HTMLElement} contentDiv - Content container
     * @param {string|object|array} content - Content to render
     */
    async function renderAssistantContent(contentDiv, content) {
        console.log('[renderAssistantContent] CALLED with content type:', typeof content, Array.isArray(content) ? `array[${content.length}]` : '');

        // Handle array of content blocks (Claude API format)
        if (Array.isArray(content)) {
            console.log(`[renderAssistantContent] Processing ${content.length} blocks`);
            let hasRenderedContent = false;
            let hasVisibleText = false;

            // ✅ CRITICAL FIX: Use for...of instead of forEach to support await
            for (const block of content) {
                console.log(`[renderAssistantContent] Processing block type: ${block?.type}`);

                if (block.type === 'thinking' && block.thinking) {
                    // Render thinking block (Extended Thinking) - COLLAPSED BY DEFAULT
                    const thinkingDiv = createThinkingBlock(block.thinking);
                    contentDiv.appendChild(thinkingDiv);
                    hasRenderedContent = true;
                    console.log('[renderAssistantContent] ✅ Added thinking block');

                } else if (block.type === 'text' && block.text) {
                    // Render text block
                    const textDiv = document.createElement('div');
                    textDiv.className = 'content-block-text';

                    const textContent = block.text;

                    // Check if text is meaningful
                    if (textContent.trim().length > 0) {
                        hasVisibleText = true;
                    }

                    console.log(`[renderAssistantContent] Rendering text block (${textContent.length} chars)`);

                    // Try visualization engine first
                    if (!window.USE_BASIC_RENDERER && typeof TwoRuleStreamProcessor !== 'undefined') {
                        try {
                            const processor = new TwoRuleStreamProcessor(textDiv);
                            await processor.processChunk(textContent);  // ✅ FIX: AWAIT the async operation

                            if (!textDiv.innerHTML || textDiv.innerHTML.trim() === '') {
                                console.warn('[renderAssistantContent] Visualization engine produced empty HTML, using markdown fallback');
                                renderMarkdown(textDiv, textContent);
                            } else {
                                console.log(`[renderAssistantContent] ✅ Visualization engine rendered ${textDiv.innerHTML.length} chars`);
                            }
                        } catch (error) {
                            console.error('[renderAssistantContent] Visualization engine error:', error);
                            renderMarkdown(textDiv, textContent);
                        }
                    } else {
                        console.log('[renderAssistantContent] Using markdown (no viz engine)');
                        renderMarkdown(textDiv, textContent);
                    }

                    contentDiv.appendChild(textDiv);
                    hasRenderedContent = true;
                    console.log('[renderAssistantContent] ✅ Added text block to contentDiv');

                } else if (block.type === 'tool_use' && block.name) {
                    // Render tool_use block - COLLAPSED BY DEFAULT
                    const toolDiv = createToolUseBlock(block);
                    contentDiv.appendChild(toolDiv);
                    hasRenderedContent = true;
                    console.log('[renderAssistantContent] ✅ Added tool_use block');
                }
            }

            // If no visible text was rendered, don't add placeholder (icons are self-explanatory)
            if (hasRenderedContent && !hasVisibleText) {
                console.log('[renderAssistantContent] Message has only thinking/tool blocks (no text content)');
            }

            if (!hasRenderedContent) {
                console.warn('[renderAssistantContent] ❌ NO RENDERABLE CONTENT BLOCKS FOUND');
            } else {
                console.log(`[renderAssistantContent] ✅ COMPLETED - contentDiv has ${contentDiv.children.length} children, innerHTML length: ${contentDiv.innerHTML.length}`);
            }

            // Array processing complete
            return;
        }

        // String content processing
        const contentStr = extractTextContent(content);

        if (!contentStr || contentStr.trim() === '') {
            console.warn('[UnifiedMessageRenderer] ⚠️ ASSISTANT MESSAGE EMPTY CONTENT');
            console.log('[UnifiedMessageRenderer] Content type:', typeof content);
            console.log('[UnifiedMessageRenderer] Content value:', content);
            console.log('[UnifiedMessageRenderer] Extracted text:', contentStr);
            return;
        }

        const startTime = performance.now();
        let processorUsed = 'markdown';
        let success = false;

        // Try visualization engine first
        if (!window.USE_BASIC_RENDERER && typeof TwoRuleStreamProcessor !== 'undefined') {
            try {
                processorUsed = 'TwoRuleStreamProcessor';
                const processor = new TwoRuleStreamProcessor(contentDiv);
                await processor.processChunk(contentStr);  // ✅ FIX: AWAIT the async operation

                // Verify content was rendered
                if (!contentDiv.innerHTML || contentDiv.innerHTML.trim() === '') {
                    console.warn('[UnifiedMessageRenderer] Visualization engine produced empty content, using markdown');
                    renderMarkdown(contentDiv, contentStr);
                    processorUsed = 'markdown (fallback)';
                }
                success = true;
            } catch (error) {
                console.error('[UnifiedMessageRenderer] Visualization engine error:', error);
                renderMarkdown(contentDiv, contentStr);
                processorUsed = 'markdown (error fallback)';
                success = false;
            }
        } else {
            // Fallback: Markdown renderer
            renderMarkdown(contentDiv, contentStr);
            success = true;
        }

        // Consolidated log
        const duration = (performance.now() - startTime).toFixed(2);
        const status = success ? '✅' : '❌';
        console.log(
            `[UnifiedMessageRenderer] ${contentStr.length} chars → ${processorUsed} → ${status} (${duration}ms)`
        );
    }

    /**
     * Render user content (plain text or simple markdown)
     * @param {HTMLElement} contentDiv - Content container
     * @param {any} content - Message content
     */
    function renderUserContent(contentDiv, content) {
        // Handle array of content blocks (includes tool_result blocks)
        if (Array.isArray(content)) {
            let hasRenderedContent = false;

            console.log(`[renderUserContent] Processing array with ${content.length} blocks:`, content.map(b => b?.type));

            content.forEach((block, index) => {
                console.log(`[renderUserContent] Block ${index + 1}/${content.length}: type="${block?.type}"`);

                if (block.type === 'tool_result') {
                    console.log(`[renderUserContent] ✅ Rendering tool_result block`, block);
                    // Render tool_result block compactly
                    const resultDiv = document.createElement('div');
                    resultDiv.className = 'content-block tool-result-block';
                    resultDiv.style.cssText = 'margin: 8px 0; padding: 10px; background: #f0f9ff; border-left: 3px solid #3b82f6; border-radius: 4px;';

                    // Tool result header
                    const headerDiv = document.createElement('div');
                    headerDiv.style.cssText = 'display: flex; align-items: center; gap: 8px; color: #1e40af; font-weight: 500; margin-bottom: 8px;';
                    headerDiv.innerHTML = `
                        <i class="fas fa-check-circle" style="color: #10b981;"></i>
                        <span>Tool Result</span>
                        ${block.tool_use_id ? `<span style="font-size: 0.75em; color: #6b7280; font-family: monospace;">${block.tool_use_id.substring(0, 12)}...</span>` : ''}
                    `;
                    resultDiv.appendChild(headerDiv);

                    // Tool result content (collapsed by default, show first 200 chars)
                    if (block.content) {
                        const contentPreview = document.createElement('div');
                        contentPreview.style.cssText = 'font-size: 0.85em; color: #4b5563; font-family: monospace; white-space: pre-wrap; max-height: 100px; overflow: hidden;';

                        const contentStr = typeof block.content === 'string'
                            ? block.content
                            : JSON.stringify(block.content, null, 2);

                        contentPreview.textContent = contentStr.substring(0, 200) + (contentStr.length > 200 ? '...' : '');
                        resultDiv.appendChild(contentPreview);
                    }

                    contentDiv.appendChild(resultDiv);
                    hasRenderedContent = true;

                } else if (block.type === 'text' && block.text) {
                    console.log(`[renderUserContent] ✅ Rendering text block (${block.text.length} chars)`);
                    // Render text block
                    const textDiv = document.createElement('div');
                    textDiv.className = 'content-block-text';
                    textDiv.textContent = block.text;
                    contentDiv.appendChild(textDiv);
                    hasRenderedContent = true;
                } else {
                    console.warn(`[renderUserContent] ⚠️ Skipping block type="${block?.type}" (not text or tool_result)`);
                }
            });

            if (!hasRenderedContent) {
                console.warn(`[renderUserContent] ⚠️ No content rendered, using fallback extraction`);
                // Fallback: extract text from all blocks
                contentDiv.textContent = extractTextContent(content);
            } else {
                console.log(`[renderUserContent] ✅ Rendered user content successfully`);
            }

            return;
        }

        // String content
        contentDiv.textContent = extractTextContent(content);
    }

    // ============================================================================
    // MESSAGE HEADER
    // ============================================================================

    /**
     * Create message header with avatar, toggle, and action buttons
     * @param {string} role - Message role
     * @param {HTMLElement} messageDiv - Parent message div for toggle functionality
     * @param {string} createdAt - ISO timestamp string
     * @returns {HTMLElement} Header div element
     */
    function createMessageHeader(role, messageDiv, createdAt) {
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

        // Action buttons container
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

        // Pop-out button
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

        // Assemble left group (avatar position depends on role)
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
        timestamp.title = createdAt || '';

        rightGroup.appendChild(timestamp);

        // Assemble header
        headerDiv.appendChild(leftGroup);
        headerDiv.appendChild(rightGroup);

        return headerDiv;
    }

    // ============================================================================
    // MESSAGE STORE INTEGRATION
    // ============================================================================

    /**
     * Add message to MessageStore with duplicate detection
     * @param {string} threadId - Thread ID
     * @param {string} role - Message role
     * @param {any} content - Message content
     * @param {boolean} checkDuplicates - Whether to check for duplicates
     * @param {boolean} syncToBackend - Whether to sync to backend
     * @returns {Promise<object|null>} MessageStore result or null
     */
    async function addToMessageStore(threadId, role, content, checkDuplicates, syncToBackend) {
        if (!threadId || typeof window.MessageStore === 'undefined') {
            return null;
        }

        if (!checkDuplicates) {
            return null; // Skip for historical loads
        }

        try {
            const messageStoreResult = await window.MessageStore.addMessage(threadId, {
                role: role === 'ai' ? 'assistant' : role,
                content: content
            }, {
                checkDuplicates: true,
                syncToBackend: syncToBackend
            });

            // Check if duplicate detected
            if (messageStoreResult && messageStoreResult._isDuplicate) {
                console.log(`[UnifiedMessageRenderer] Duplicate detected, skipping DOM creation for message ID: ${messageStoreResult.id}`);
                return { isDuplicate: true };
            }

            return messageStoreResult;
        } catch (err) {
            console.warn('[UnifiedMessageRenderer] MessageStore sync failed:', err);
            return null;
        }
    }

    // ============================================================================
    // MAIN RENDER FUNCTION
    // ============================================================================

    /**
     * Render a message in the specified container
     * 
     * @param {HTMLElement|string} container - Container element or selector
     * @param {string} role - Message role: 'user', 'assistant', or 'tool'
     * @param {string|object} content - Message content
     * @param {object} options - Rendering options
     * @returns {Promise<HTMLElement|null>} Created message element (or null if skipped)
     */
    async function render(container, role, content, options = {}) {
        try {
            // Resolve container
            const messagesContainer = typeof container === 'string'
                ? document.querySelector(container)
                : container;

            if (!messagesContainer) {
                console.error('[UnifiedMessageRenderer] Container not found:', container);
                return null;
            }

            // Extract options with defaults
            const {
                isThinking = false,
                scrollToBottom = true,
                threadId = null,
                syncToBackend = false,
                createdAt = null,
                checkDuplicates = true,
                messageId = null
            } = options;

            // Check if message should be skipped
            const skipReason = shouldSkipMessage(role, content);
            if (skipReason) {
                console.warn(`[UnifiedMessageRenderer] ⚠️ SKIPPING ${role} message: ${skipReason}`);
                console.log(`[UnifiedMessageRenderer] Skipped content type: ${typeof content}, value:`, content);
                return null;
            }

            // Add to MessageStore (with duplicate check)
            const storeResult = await addToMessageStore(
                threadId,
                role,
                content,
                checkDuplicates,
                syncToBackend
            );

            if (storeResult && storeResult.isDuplicate) {
                return null; // Skip duplicate
            }

            // Create message wrapper
            const messageDiv = document.createElement('div');
            messageDiv.className = `ai-message ${role}${isThinking ? ' thinking' : ''}`;
            messageDiv.setAttribute('data-raw-content',
                typeof content === 'string' ? content : JSON.stringify(content)
            );

            if (messageId) {
                messageDiv.dataset.messageId = messageId;
            }

            // Create message header
            const headerDiv = createMessageHeader(
                role,
                messageDiv,
                createdAt || new Date().toISOString()
            );

            // Create message content bubble
            const contentDiv = document.createElement('div');
            contentDiv.className = 'ai-message-content';

            // Render content based on role
            if (!isThinking) {
                if (ASSISTANT_ROLES.has(role)) {
                    console.log(`[UnifiedMessageRenderer] Rendering ASSISTANT message, content type: ${typeof content}`);
                    await renderAssistantContent(contentDiv, content);  // ✅ AWAIT async render
                    console.log(`[UnifiedMessageRenderer] ASSISTANT render complete, contentDiv.innerHTML length: ${contentDiv.innerHTML.length}`);
                } else if (role === 'user') {
                    renderUserContent(contentDiv, content);
                } else if (role === 'tool') {
                    renderToolContent(contentDiv, content);
                } else {
                    contentDiv.textContent = extractTextContent(content);
                }
            }

            // Assemble message
            messageDiv.appendChild(headerDiv);
            messageDiv.appendChild(contentDiv);

            console.log(`[UnifiedMessageRenderer] Assembled ${role} message, messageDiv has ${messageDiv.children.length} children`);
            console.log(`[UnifiedMessageRenderer] contentDiv innerHTML length: ${contentDiv.innerHTML.length}`);

            // Append to container
            messagesContainer.appendChild(messageDiv);

            console.log(`[UnifiedMessageRenderer] Appended to container ${messagesContainer.id}, container now has ${messagesContainer.children.length} messages`);

            // Auto-scroll if enabled
            if (scrollToBottom) {
                setTimeout(() => {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight + SCROLL_OFFSET;
                }, SCROLL_DELAY_MS);
            }

            console.log(`[UnifiedMessageRenderer] ✅ Rendered ${role} message in ${messagesContainer.id}`);
            return messageDiv;

        } catch (error) {
            console.error('[UnifiedMessageRenderer] Render error:', error);
            return null;
        }
    }

    // ============================================================================
    // COPY FUNCTIONS
    // ============================================================================

    /**
     * Copy rendered text from message
     * @param {HTMLElement} messageDiv - Message element
     * @param {HTMLElement} button - Copy button element
     */
    function copyRenderedText(messageDiv, button) {
        const contentDiv = messageDiv.querySelector('.ai-message-content');
        if (!contentDiv) {
            console.warn('[UnifiedMessageRenderer] No content div found for copy');
            return;
        }

        const text = contentDiv.innerText || contentDiv.textContent;

        navigator.clipboard.writeText(text).then(() => {
            button.classList.add('copied');
            button.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                button.classList.remove('copied');
                button.innerHTML = '<i class="fas fa-copy"></i>';
            }, COPY_FEEDBACK_DURATION);
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
            }, COPY_FEEDBACK_DURATION);
        }).catch(err => {
            console.error('[UnifiedMessageRenderer] Copy failed:', err);
        });
    }

    // ============================================================================
    // UPDATE FUNCTION
    // ============================================================================

    /**
     * Update existing thinking message with real content
     * @param {HTMLElement} messageDiv - Existing message element with thinking animation
     * @param {string|object} content - New content to render
     */
    async function updateThinkingMessage(messageDiv, content) {
        if (!messageDiv) {
            console.warn('[UnifiedMessageRenderer] No message element provided to update');
            return;
        }

        // Remove thinking class
        messageDiv.classList.remove('thinking');

        // Find content div
        const contentDiv = messageDiv.querySelector('.ai-message-content');
        if (!contentDiv) {
            console.warn('[UnifiedMessageRenderer] No content div found to update');
            return;
        }

        // Clear thinking animation
        contentDiv.innerHTML = '';

        // Render real content
        const role = messageDiv.classList.contains('user') ? 'user'
            : messageDiv.classList.contains('assistant') ? 'assistant'
                : 'ai';

        if (ASSISTANT_ROLES.has(role)) {
            await renderAssistantContent(contentDiv, content);  // ✅ AWAIT async render
        } else {
            contentDiv.textContent = extractTextContent(content);
        }

        // Update raw content attribute
        messageDiv.setAttribute('data-raw-content',
            typeof content === 'string' ? content : JSON.stringify(content)
        );

        console.log('[UnifiedMessageRenderer] ✅ Updated thinking message with real content');
    }

    // ============================================================================
    // POP-OUT WINDOW
    // ============================================================================

    /**
     * Create event handlers for dragging
     * @param {HTMLElement} window - Popout window
     * @param {HTMLElement} header - Draggable header
     * @returns {object} Event handlers and cleanup function
     */
    function createDragHandlers(window, header) {
        let isDragging = false;
        let dragOffsetX = 0;
        let dragOffsetY = 0;

        const onMouseDown = (e) => {
            if (e.target.closest('button')) return;

            isDragging = true;
            const rect = window.getBoundingClientRect();
            dragOffsetX = e.clientX - rect.left;
            dragOffsetY = e.clientY - rect.top;
            header.style.cursor = 'grabbing';
            e.preventDefault();
        };

        const onMouseMove = (e) => {
            if (!isDragging) return;

            const x = e.clientX - dragOffsetX;
            const y = e.clientY - dragOffsetY;

            // Keep within viewport bounds
            const maxX = window.innerWidth - 100;
            const maxY = window.innerHeight - 50;

            window.style.left = `${Math.max(0, Math.min(x, maxX))}px`;
            window.style.top = `${Math.max(0, Math.min(y, maxY))}px`;
        };

        const onMouseUp = () => {
            if (isDragging) {
                isDragging = false;
                header.style.cursor = 'grab';
            }
        };

        const cleanup = () => {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };

        header.addEventListener('mousedown', onMouseDown);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);

        return { cleanup };
    }

    /**
     * Create event handlers for resizing
     * @param {HTMLElement} window - Popout window
     * @param {HTMLElement} handle - Resize handle
     * @returns {object} Event handlers and cleanup function
     */
    function createResizeHandlers(window, handle) {
        let isResizing = false;
        let startX = 0;
        let startY = 0;
        let startWidth = 0;
        let startHeight = 0;

        const onMouseDown = (e) => {
            isResizing = true;
            startX = e.clientX;
            startY = e.clientY;
            const rect = window.getBoundingClientRect();
            startWidth = rect.width;
            startHeight = rect.height;
            e.preventDefault();
            e.stopPropagation();
        };

        const onMouseMove = (e) => {
            if (!isResizing) return;

            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;

            const newWidth = Math.max(MIN_POPOUT_WIDTH, startWidth + deltaX);
            const newHeight = Math.max(MIN_POPOUT_HEIGHT, startHeight + deltaY);

            window.style.width = `${newWidth}px`;
            window.style.height = `${newHeight}px`;
        };

        const onMouseUp = () => {
            if (isResizing) {
                isResizing = false;
            }
        };

        const cleanup = () => {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };

        handle.addEventListener('mousedown', onMouseDown);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);

        return { cleanup };
    }

    /**
     * Open message in floating, movable, resizable window
     * @param {HTMLElement} messageDiv - Message element to display
     */
    function openMessagePopout(messageDiv) {
        const contentDiv = messageDiv.querySelector('.ai-message-content');
        if (!contentDiv) {
            console.error('[UnifiedMessageRenderer] No content found in message');
            return;
        }

        windowCount++;
        const windowId = `popout-${Date.now()}-${windowCount}`;

        // Create floating window
        const floatingWindow = document.createElement('div');
        floatingWindow.className = 'message-popout-window';
        floatingWindow.id = windowId;
        floatingWindow.style.zIndex = getNextZIndex();

        // Position with cascade offset
        const offset = (windowCount - 1) * POPOUT_CASCADE_OFFSET;
        floatingWindow.style.left = `${POPOUT_INITIAL_OFFSET + offset}px`;
        floatingWindow.style.top = `${POPOUT_INITIAL_OFFSET + offset}px`;

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

        // Setup drag and resize handlers
        const dragHandlers = createDragHandlers(floatingWindow, header);
        const resizeHandlers = createResizeHandlers(floatingWindow, resizeHandle);

        // Cleanup function
        const cleanup = () => {
            dragHandlers.cleanup();
            resizeHandlers.cleanup();
            activePopouts.delete(windowId);
        };

        // Close window
        const closeWindow = () => {
            floatingWindow.classList.add('closing');
            setTimeout(() => {
                floatingWindow.remove();
                cleanup();
            }, POPOUT_CLOSE_ANIMATION_DURATION);
        };

        closeBtn.addEventListener('click', closeWindow);

        // Copy functionality
        copyBtn.addEventListener('click', () => {
            const text = popoutContent.innerText;
            navigator.clipboard.writeText(text).then(() => {
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                }, COPY_FEEDBACK_DURATION);
            }).catch(err => {
                console.error('[UnifiedMessageRenderer] Copy failed:', err);
            });
        });

        // Bring to front on click
        floatingWindow.addEventListener('mousedown', () => {
            floatingWindow.style.zIndex = getNextZIndex();
        });

        // Track active popout
        activePopouts.set(windowId, { element: floatingWindow, cleanup });

        // Animate in
        requestAnimationFrame(() => floatingWindow.classList.add('visible'));

        console.log(`[UnifiedMessageRenderer] ✅ Popout window opened: ${windowId}`);
    }

    // ============================================================================
    // CLEANUP
    // ============================================================================

    /**
     * Close all active popout windows
     */
    function closeAllPopouts() {
        activePopouts.forEach(({ element, cleanup }) => {
            element.classList.add('closing');
            setTimeout(() => {
                element.remove();
                cleanup();
            }, POPOUT_CLOSE_ANIMATION_DURATION);
        });
        activePopouts.clear();
        console.log('[UnifiedMessageRenderer] All popouts closed');
    }

    // ============================================================================
    // PUBLIC API
    // ============================================================================

    return {
        render,
        copyRenderedText,
        copyRawContent,
        updateThinkingMessage,
        openMessagePopout,
        closeAllPopouts
    };
})();

// Make globally available
window.UnifiedMessageRenderer = UnifiedMessageRenderer;
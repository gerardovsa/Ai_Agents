/**
 * ================================================================
 * CRITICAL: Two-Rule Streaming + Enhanced Markdown Renderer
 * ---------------------------------------------------------------
 * AI assistants and future maintainers:
 * - This file contains carefully tuned newline, list, heading, and HR handling.
 * - DO NOT reintroduce naive newline conversions (e.g., text.replace(/\n/g,'<br>'))
 *   before or after the centralized renderer.
 * - DO NOT change the order of transformations without running the full
 *   comprehensive-workflow-test.html and validating streaming + reload paths.
 * - The logic below prevents doubled line breaks, preserves single newlines,
 *   and ensures no extra spacing after headings, list items, and hr rules.
 * - If you must modify, update both this file and the release variant,
 *   and keep the cleanup rules intact.
 * ================================================================
 */
// =====================================
// COMPLETE TWO-RULE STREAMING SYSTEM
// Unified Replacement for streaming.js
// Black & White Content Classification
// =====================================

/**
 * COMPLETE TWO-RULE STREAMING PROCESSOR
 * 
 * RULE 1: Any Raw Buffered Content CANNOT be put into both groups
 * RULE 2: Once a delimiter is detected, ALL content is Visual Type until END delimiter
 * 
 * Architecture:
 * Stream Input → Raw Buffer (append only) → Content Parser → Controlled Release → UI Append
 * 
 * This file completely replaces streaming.js with a unified Two-Rule system
 * that includes all streaming functions, markdown processing, and visualization handling.
 */

// =====================================
// DEBUG MODE CONFIGURATION
// =====================================
// Set to true to see detailed TWO-RULE logs
// Set to false to only see consolidated summary logs
window.DEBUG_TWO_RULE = window.DEBUG_TWO_RULE || false;

// Debug logging function - only logs if DEBUG_TWO_RULE is enabled
function debugLog(...args) {
    if (window.DEBUG_TWO_RULE) {
        console.log(...args);
    }
}

// =====================================
// GLOBAL STATE MANAGEMENT
// =====================================

// Global Two-Rule processor instance
let globalTwoRuleProcessor = null;

// Global streaming message element reference
let streamingMessageElement = null;

// Global streaming state
let streamingState = {
    isFirstContent: true,
    lastProcessedLength: 0,
    renderedComponents: [],
    lastActivityTs: 0
};

// Plotly responsive management
const plotlyResizeObservers = new WeakMap();
const pendingPlotlyResizeHandles = new WeakMap();
let plotlyWindowResizeHandlerRegistered = false;

// Sidebar visualization state (use global state from sidebar.js)
// let sidebarVisualizationState = ... // REMOVED - using window.sidebarVisualizationState

// SIMPLE FIX #1: Robust thinking indicator removal
function removeAllThinkingIndicators(container) {
    if (!container) return;

    // Remove by ID
    const thinkingById = container.querySelector('#thinkingIndicator');
    if (thinkingById) {
        thinkingById.remove();
        console.log('emoved thinking indicator by ID');
    }

    // Remove by class (backup)
    const thinkingByClass = container.querySelectorAll('.thinking-indicator');
    thinkingByClass.forEach(indicator => {
        indicator.remove();
        console.log('emoved thinking indicator by class');
    });

    // Remove any element containing "thinking..." text
    const allElements = container.querySelectorAll('*');
    allElements.forEach(el => {
        if (el.textContent && el.textContent.toLowerCase().includes('thinking')) {
            el.remove();
            console.log('emoved thinking indicator by text content');
        }
    });
}

class TwoRuleStreamProcessor {
    constructor(container) {
        // ORE: Single Source of Truth - Raw Buffer
        this.container = container || document.createElement('div');
        this.rawBuffer = '';
        this.bufferPosition = 0;

        // TATE MACHINE: Delimiter Detection (Black & White States)
        this.state = 'NORMAL'; // NORMAL | BUFFERING_VISUAL
        this.currentDelimiter = null;
        this.visualBufferStart = 0;

        // Log thread initialization
        debugLog('🚀 TWO-RULE: New streaming thread started');
        this.visualBufferEnd = 0;

        // ENDERING/QUEUE STATE
        // CRITICAL FIX: Eagerly create the markdown wrapper and attach it to the
        // streaming container NOW, before any content arrives.  The synchronous
        // state-machine parser (parseNormalState) inserts anchors and loading
        // indicators via `this.markdownContainer || this.container`.  When the
        // markdown container only exists LAZILY (created later in async
        // renderMarkdownPackage), any anchor or loading indicator created before
        // the first async render fires lands as a direct child of this.container.
        // That makes every subsequent markdownContainer (with all text) append
        // AFTER those stranded viz/anchor nodes — resulting in all
        // visualisations appearing above all markdown text.  Eager creation
        // ensures every anchor, loading indicator and text block always go into
        // the same wrapper, in stream order, from the very first chunk.
        this.markdownContainer = document.createElement('div');
        this.markdownContainer.className = 'two-rule-markdown-container';
        this.markdownContainer.style.cssText = [
            'line-height: 1.4',
            'color: var(--text-primary)',
            'word-wrap: break-word',
        ].join(';');
        this.container.appendChild(this.markdownContainer);

        this.loadingIndicator = null;
        this.isReleasing = false;

        // ACKAGE/QUEUE STORAGE
        this.markdownPackages = [];
        this.visualPackages = [];
        this.nextPackageId = 1;
        this.lastReleasedPosition = 0;

        // ETRICS
        this.stats = {
            chunksProcessed: 0,
            totalProcessingTime: 0,
            markdownPackages: 0,
            visualPackages: 0,
            packagesReleased: 0
        };
    }

    /**
     * HUNK PROCESSING: Process and parse a new content chunk
     */
    async processChunk(newContent) {
        if (!newContent) return;
        const t0 = performance.now();

        // Append to single source of truth buffer
        this.rawBuffer += newContent;

        // Drive state machine until no further progress can be made
        let progressed = true;
        let guard = 0;
        while (progressed && guard < 1000) {
            progressed = false;
            if (this.state === 'BUFFERING_VISUAL') {
                const before = this.bufferPosition;
                this.parseBufferingState();
                // Progress if bufferPosition advanced or state changed
                if (this.state === 'NORMAL' || this.bufferPosition > before) {
                    progressed = true;
                }
            } else {
                progressed = this.parseNormalState();
            }
            guard++;
        }

        // Release any ready packages (markdown/visual)
        await this.releaseReadyPackages();

        // Metrics
        this.stats.chunksProcessed++;
        this.stats.totalProcessingTime += (performance.now() - t0);
    }

    /**
     * FINALIZE: Complete processing and flush remaining content
     * 🎯 FIX: Called when stream ends to ensure last line is rendered
     */
    async finalize() {
        console.log('🏁 TWO-RULE: Finalizing stream processing...');

        // Package any remaining markdown content in buffer
        const remainingContent = this.rawBuffer.slice(this.bufferPosition);

        if (remainingContent.trim()) {
            console.log(`🔥 TWO-RULE: Flushing final ${remainingContent.length} chars`);
            this.packageMarkdownContent(remainingContent, this.bufferPosition);
            this.bufferPosition = this.rawBuffer.length;
        }

        // Release all pending packages
        await this.releaseReadyPackages();

        // Clear any lingering buffering indicator
        this.removeBufferingIndicator();

        // Process deferred visualizations (containers that were off-DOM during processChunk)
        if (this.deferredRenders && this.deferredRenders.length > 0) {
            if (document.contains(this.container)) {
                // Container is already in the DOM - render immediately
                console.log(`🔄 TWO-RULE: Container in DOM - processing ${this.deferredRenders.length} deferred renders now`);
                await this._processDeferredRenders();
            } else {
                // Container is NOT yet in the DOM (message_renderer appends it after finalize returns).
                // Use a MutationObserver so we fire the instant the container is attached.
                console.log(`📌 TWO-RULE: Container off-DOM - registering MutationObserver for ${this.deferredRenders.length} deferred renders`);
                const self = this;
                let resolved = false;

                const observer = new MutationObserver(() => {
                    if (!resolved && document.contains(self.container)) {
                        resolved = true;
                        observer.disconnect();
                        console.log(`✅ TWO-RULE: Container entered DOM - triggering deferred renders`);
                        self._processDeferredRenders().catch(err => {
                            console.error('❌ TWO-RULE: Deferred render error after DOM attachment:', err);
                        });
                    }
                });
                observer.observe(document.body, { childList: true, subtree: true });

                // Safety fallback: give up waiting after 5 s and render anyway
                setTimeout(() => {
                    if (!resolved) {
                        resolved = true;
                        observer.disconnect();
                        console.warn('⚠️ TWO-RULE: Deferred render 5s timeout - forcing render');
                        self._processDeferredRenders().catch(err => {
                            console.error('❌ TWO-RULE: Deferred render timeout error:', err);
                        });
                    }
                }, 5000);
            }
        }

        console.log(`✅ TWO-RULE: Finalized (${this.stats.chunksProcessed} chunks, ${this.stats.markdownPackages} markdown, ${this.stats.visualPackages} visuals)`);
    }

    /**
     * Process all queued deferred visualizations.
     * Called either immediately (container already in DOM) or via MutationObserver.
     */
    async _processDeferredRenders() {
        if (!this.deferredRenders || this.deferredRenders.length === 0) return;

        console.log(`🎨 TWO-RULE: _processDeferredRenders – ${this.deferredRenders.length} items`);

        // One rAF + tiny timeout so the browser has painted the message bubble
        await new Promise(resolve => requestAnimationFrame(resolve));
        await new Promise(resolve => setTimeout(resolve, 50));

        for (const deferred of this.deferredRenders) {
            try {
                console.log(`🎨 TWO-RULE: Rendering deferred ${deferred.type} (in DOM: ${document.contains(deferred.container)})`);

                // Clear the loading placeholder inside the inner content area
                const vizContentArea = deferred.container.querySelector('.viz-content-area') || deferred.container;
                vizContentArea.innerHTML = '';

                await this.renderVisualization(deferred.type, deferred.content, vizContentArea);

                console.log(`✅ TWO-RULE: Deferred ${deferred.type} rendered successfully`);
            } catch (error) {
                console.error(`❌ TWO-RULE: Deferred ${deferred.type} render failed:`, error);
                const vizContentArea = deferred.container.querySelector('.viz-content-area') || deferred.container;
                vizContentArea.innerHTML = `
                    <div class="viz-error" style="text-align:center;padding:20px;color:var(--accent-red);background:rgba(239,68,68,0.1);border-radius:8px;">
                        <h3 style="margin:0 0 8px 0;font-size:16px;">⚠️ ${deferred.type.toUpperCase()} Render Failed</h3>
                        <p style="margin:0;font-size:13px;color:var(--text-secondary);">${error.message}</p>
                        <details style="margin-top:12px;text-align:left;font-size:11px;">
                            <summary style="cursor:pointer;color:var(--accent-primary);">Show Details</summary>
                            <pre style="background:rgba(0,0,0,0.2);padding:8px;border-radius:4px;overflow-x:auto;white-space:pre-wrap;margin-top:8px;">${error.stack || 'No stack trace'}</pre>
                        </details>
                    </div>
                `;
            }
        }

        this.deferredRenders = [];
    }

    /**
     * FORCE FLUSH: Immediately release any buffered markdown content
     * 🔥 FIX: Called when switching from content_delta to tool_use events
     * 🛡️ CRITICAL: Don't flush if we're inside an incomplete code fence
     */
    forceFlush() {
        const remainingContent = this.rawBuffer.slice(this.bufferPosition);
        if (!remainingContent || !remainingContent.trim()) {
            return; // Nothing to flush
        }

        // �️ CRITICAL FIX: Check if we're inside an incomplete code block
        // Count ``` occurrences in the ENTIRE buffer to check current state
        const allFences = (this.rawBuffer.match(/```/g) || []).length;

        // If odd number of fences, we're currently inside a code block - DON'T FLUSH
        if (allFences % 2 === 1) {
            console.log(`🛡️ TWO-RULE: Skipping force flush - currently inside code block (${allFences} total fences, waiting for closing fence)`);
            return;
        }

        // Safe to flush - even number of fences means we're NOT in a code block
        console.log(`🔥 TWO-RULE: Force flushing ${remainingContent.length} buffered chars (${allFences} total fences = ${allFences / 2} complete pairs)`);
        this.packageMarkdownContent(remainingContent, this.bufferPosition);
        this.bufferPosition = this.rawBuffer.length;
        // Release immediately
        this.releaseReadyPackages();
    }

    /**
     * ORMAL STATE: Parse and process content in NORMAL state
     * RULE 1: BLACK AND WHITE - Distinguish between Raw and Visual content
     */
    parseNormalState() {
        // Remaining content from current buffer position
        const remainingContent = this.rawBuffer.slice(this.bufferPosition);
        if (!remainingContent) return false;

        // Detect visualization start delimiter, respecting code fences
        const delimiterMatch = this.findVisualizationStart(remainingContent);
        if (delimiterMatch) {
            // Calculate visual start position BEFORE advancing buffer
            const visualStartPos = this.bufferPosition + delimiterMatch.position;

            // RITICAL FIX: Package any text BEFORE the delimiter
            const textBeforeDelimiter = remainingContent.slice(0, delimiterMatch.position);
            if (textBeforeDelimiter.trim()) {
                const startPos = this.bufferPosition;
                this.packageMarkdownContent(textBeforeDelimiter, startPos);
                this.bufferPosition += textBeforeDelimiter.length;
                console.log(`📝 TWO-RULE: Packaged text before delimiter (${textBeforeDelimiter.length} chars at position ${startPos})`);
            }

            // Enter visual buffering state
            this.currentDelimiter = {
                type: delimiterMatch.type,
                startDelimiter: delimiterMatch.startDelimiter,
                endDelimiter: delimiterMatch.endDelimiter
            };
            this.visualBufferStart = visualStartPos;

            // Insert an anchor so we can place the eventual viz according to stream position
            try {
                const target = this.markdownContainer || this.container;
                if (target) {
                    const anchor = document.createElement('div');
                    anchor.className = 'two-rule-anchor';
                    anchor.setAttribute('data-stream-position', String(this.visualBufferStart));

                    const candidates = Array.from(target.children).filter(el => {
                        if (!(el instanceof Element)) return false;
                        const cls = el.classList || { contains: () => false };
                        return cls.contains('two-rule-markdown-content') || cls.contains('viz-container') || cls.contains('two-rule-anchor');
                    });
                    let referenceNode = null;
                    for (const el of candidates) {
                        const posAttr = el.getAttribute('data-stream-position');
                        const pos = posAttr ? parseInt(posAttr, 10) : Number.MAX_SAFE_INTEGER;
                        if (pos > this.visualBufferStart) {
                            referenceNode = el;
                            break;
                        }
                    }
                    if (referenceNode) {
                        target.insertBefore(anchor, referenceNode);
                    } else {
                        target.appendChild(anchor);
                    }
                }
            } catch (_) { }

            // Switch state and present buffering indicator
            this.state = 'BUFFERING_VISUAL';
            this.showBufferingIndicator(this.currentDelimiter.type);
            return true;
        }

        // Progressive markdown packaging when no visual delimiter is found
        // Hold back any partial start-delimiter suffix at the end of the buffer
        const suffixLen = this.getPotentialDelimiterSuffixLength(remainingContent);
        const available = suffixLen > 0 ? remainingContent.slice(0, -suffixLen) : remainingContent;

        if (!available || available.length === 0) {
            // Not enough content to safely package yet
            return false;
        }

        // Prefer packaging only at line boundaries to avoid chopping tokens
        const shouldRelease = this.shouldPackageMarkdownNow(available, available.length);
        if (!shouldRelease) {
            return false; // Wait for more content
        }

        // Prefer releasing up to the last double-newline (paragraph) or single newline
        let releaseLen = available.lastIndexOf('\n\n');
        if (releaseLen !== -1) {
            releaseLen = releaseLen + 2; // include the blank line
        } else {
            releaseLen = available.lastIndexOf('\n');
            if (releaseLen !== -1) {
                releaseLen = releaseLen + 1; // include newline
            } else {
                // 🔥 FIX: Release small punctuation chunks immediately (periods, commas, etc.)
                // This prevents periods from being held in buffer as separate chunks
                if (available.length <= 3 && /^[.,;:!?)\]}\s]*$/.test(available)) {
                    releaseLen = available.length;
                } else {
                    // No newline yet: hold content to avoid breaking markdown tokens
                    releaseLen = 0;
                }
            }
        }

        if (releaseLen > 0) {
            const toRelease = available.slice(0, releaseLen);
            const startPos = this.bufferPosition;
            this.packageMarkdownContent(toRelease, startPos);
            this.bufferPosition += releaseLen; // Advance past released text
            return true;
        }

        return false;
    }

    /**
     * Decide when to package markdown chunks during NORMAL state.
     * Heuristic: release when we see markdown triggers, line breaks, or content gets long.
     */
    shouldPackageMarkdownNow(content, totalLength) {
        try {
            if (!content) return false;
            // Strong markdown signals -> release immediately
            if (this.hasMarkdownTrigger(content)) return true;
            // Safe line boundary -> release
            if (content.includes('\n')) return true;
            // 🔥 FIX: Release text between tool calls faster (50 chars instead of 200)
            if (typeof totalLength === 'number' && totalLength > 50) return true;
            return false;
        } catch (_) {
            // On any error, be conservative and do not release
            return false;
        }
    }

    /**
     * UFFERING STATE: Accumulate ALL content until end delimiter found
     * RULE 2: BLACK AND WHITE - Everything goes to Visual Type
     */
    parseBufferingState() {
        const contentFromStart = this.rawBuffer.slice(this.visualBufferStart);
        const endDelimiter = this.currentDelimiter.endDelimiter;

        const endIndex = contentFromStart.indexOf(endDelimiter);

        if (endIndex !== -1) {
            // End delimiter found - package complete visual content
            const visualEndPosition = this.visualBufferStart + endIndex + endDelimiter.length;
            const completeVisualContent = this.rawBuffer.slice(this.visualBufferStart, visualEndPosition);

            console.log(`WO-RULE: Visual content complete (${completeVisualContent.length} chars)`);

            this.packageVisualContent(completeVisualContent, this.currentDelimiter.type);

            // 🔥 CRITICAL FIX: Reset state BEFORE releasing packages so the while loop
            // in processChunk detects progress and continues scanning the remainder of
            // the buffer for more visualizations / markdown text.
            this.bufferPosition = visualEndPosition;
            this.state = 'NORMAL';
            this.currentDelimiter = null;
            this.removeBufferingIndicator();

            // Release packages now that state is reset
            this.releaseReadyPackages().catch(err => {
                console.error('❌ TWO-RULE: Error releasing visual packages after buffering complete:', err);
            });
        }
    }

    /**
     * ACKAGE CREATION: Create Type 1 (Markdown) content package
     */
    packageMarkdownContent(content, startPosition = null) {
        if (!content.trim()) return;

        // IMPLE FIX #4: Deduplication check for markdown
        const contentHash = this.generateContentHash({ type: 'markdown', content: content });
        const existingPackage = this.markdownPackages.find(pkg =>
            pkg.contentHash === contentHash ||
            (pkg.content === content)
        );

        if (existingPackage) {
            return;
        }

        // RITICAL FIX: Use provided start position or calculate from buffer position
        const actualPosition = startPosition !== null ? startPosition : (this.bufferPosition - content.length);

        const pkg = {
            id: this.nextPackageId++,
            type: 'markdown',
            content: content,
            contentHash: contentHash,
            position: actualPosition, // IXED: Use actual stream position
            ready: true,
            timestamp: Date.now()
        };

        this.markdownPackages.push(pkg);
        this.stats.markdownPackages++;
    }

    /**
     * ACKAGE CREATION: Create Type 2 (Visual) content package
     */
    packageVisualContent(content, type) {
        // IMPLE FIX #4: Deduplication check for visual content
        const contentHash = this.generateContentHash({ type: 'visual', content: content });
        const existingPackage = this.visualPackages.find(pkg =>
            pkg.contentHash === contentHash ||
            (pkg.content === content && pkg.subType === type)
        );

        if (existingPackage) {
            return;
        }

        const pkg = {
            id: this.nextPackageId++,
            type: 'visual',
            subType: type,
            content: content,
            contentHash: contentHash, // DD hash for deduplication
            position: this.visualBufferStart, // ORRECT: Use delimiter start position
            ready: true,
            timestamp: Date.now()
        };

        this.visualPackages.push(pkg);
        this.stats.visualPackages++;
    }

    /**
     * ONTROLLED RELEASE: Release ready packages in order
     * Maintains stream sequence and uses append-only rendering
     */
    async releaseReadyPackages() {
        if (this.isReleasing) {
            // Avoid re-entrancy that can cause duplicate renders
            return;
        }
        this.isReleasing = true;
        // RITICAL FIX: Don't release packages while buffering visual content
        // This prevents raw visual content from appearing in UI
        if (this.state === 'BUFFERING_VISUAL') {
            this.isReleasing = false;
            return; // Wait until visual content is complete
        }

        try {
            const allPackages = [...this.markdownPackages, ...this.visualPackages]
                .filter(pkg => pkg.ready)
                .sort((a, b) => a.position - b.position);

            for (const pkg of allPackages) {
                // Skip if a container with this package already exists (extra safety)
                if (pkg.type === 'visual') {
                    const existing = this.container.querySelector(`.viz-container[data-package-id="${pkg.id}"]`);
                    if (existing) {
                        // Remove from queue
                        const idx = this.visualPackages.indexOf(pkg);
                        if (idx > -1) this.visualPackages.splice(idx, 1);
                        continue;
                    }
                }

                await this.renderPackage(pkg);

                // Remove from respective array
                if (pkg.type === 'markdown') {
                    const index = this.markdownPackages.indexOf(pkg);
                    if (index > -1) this.markdownPackages.splice(index, 1);
                } else {
                    const index = this.visualPackages.indexOf(pkg);
                    if (index > -1) this.visualPackages.splice(index, 1);
                }

                this.lastReleasedPosition = pkg.position + pkg.content.length;
                this.stats.packagesReleased++;
            }
        } finally {
            this.isReleasing = false;
        }
    }

    /**
     * PPEND-ONLY RENDERING: Render individual package to UI
     * Never re-renders existing content - only appends new packages
     */
    async renderPackage(pkg) {
        try {
            if (pkg.type === 'markdown') {
                await this.renderMarkdownPackage(pkg);
            } else if (pkg.type === 'visual') {
                await this.renderVisualPackage(pkg);
            }
        } catch (error) {
            console.error('❌ TWO-RULE: Error rendering package:', error);
            this.renderErrorPackage(pkg, error);
        }
    }

    /**
     * ARKDOWN RENDERING: Render Type 1 content with TRUE text concatenation
     * RULE: TYPE 1 content MUST be concatenated as flowing text, NOT fragmented
     */
    async renderMarkdownPackage(pkg) {
        // markdownContainer is now eagerly created in the constructor; this
        // guard is kept as a safety net only (should never be null in practice).
        if (!this.markdownContainer) {
            this.markdownContainer = document.createElement('div');
            this.markdownContainer.className = 'two-rule-markdown-container';
            this.markdownContainer.style.cssText = 'line-height:1.4;color:var(--text-primary);word-wrap:break-word;';
            this.container.appendChild(this.markdownContainer);
        }

        // RITICAL FIX: ALWAYS concatenate TYPE 1 content unless there's a visual break
        // Check if we can append to the last element instead of creating new one
        const lastElement = this.markdownContainer.lastElementChild;
        const canAppendToPrevious = lastElement &&
            lastElement.className === 'two-rule-markdown-content' &&
            !pkg.content.trim().startsWith('#') && // Don't concat headers
            !this.hasVisualBreakBefore(pkg); // No visual content between this and last

        if (canAppendToPrevious) {
            // RUE CONCATENATION: Concatenate RAW text first, then render as one unit
            const currentRawText = lastElement.getAttribute('data-raw-text') || '';
            const incoming = pkg.content;
            // If incoming starts with a block token and previous text doesn't end with newline, add one
            const startsWithBlockToken = /^(\s*)(#{1,6}\s|[-*+]\s|\d+\.\s|>\s|\|.*|---\s*$)/m.test(incoming);
            let newRawText = currentRawText;
            if (startsWithBlockToken) {
                const prevEndsWithNewline = /\n$/.test(newRawText);
                const incomingStartsWithNewline = /^\n/.test(incoming);
                // Only inject a single separating newline if neither side already provides it
                if (!prevEndsWithNewline && !incomingStartsWithNewline) {
                    newRawText += '\n';
                }
            }
            newRawText += incoming; // PRESERVE ALL \n formatting

            // Store the concatenated raw text
            lastElement.setAttribute('data-raw-text', newRawText);

            // RESERVE loading indicators before re-rendering
            const loadingIndicators = [];
            if (this.markdownContainer) {
                const indicators = this.markdownContainer.querySelectorAll('.two-rule-loading-indicator');
                indicators.forEach(indicator => {
                    loadingIndicators.push({
                        element: indicator.cloneNode(true),
                        nextSibling: indicator.nextSibling
                    });
                });
            }

            // Re-render the ENTIRE concatenated raw text as one markdown unit
            console.log('🔍 TWO-RULE: Attempting markdown render, marked available?', typeof window.marked);
            //  LEGACY RENDERING COMMENTED OUT - Causes extra line breaks
            // if (typeof window.renderEnhancedMarkdown === 'function') {
            //     console.log('📝 TWO-RULE: Using renderEnhancedMarkdown');
            //     lastElement.innerHTML = window.renderEnhancedMarkdown(newRawText);
            // } else 
            if (window.marked && typeof window.marked.parse === 'function') {
                console.log('📝 TWO-RULE: Using marked.parse for', newRawText.length, 'chars');

                // CONFIGURE MARKED FOR BETTER RENDERING
                if (window.marked.setOptions) {
                    window.marked.setOptions({
                        breaks: false,         // DON'T convert newlines to <br> (causes issues in code blocks)
                        gfm: true,             // GitHub Flavored Markdown
                        pedantic: false,       // Don't be strict
                        smartLists: true,      // Use smarter list behavior
                        smartypants: false,    // Don't replace quotes
                        headerIds: false,      // Don't add IDs to headers
                        mangle: false          // Don't escape email addresses
                    });
                }

                let rendered = window.marked.parse(newRawText);

                // NHANCE CODE BLOCKS: Add proper styling
                rendered = rendered.replace(/<pre><code class="language-(\w+)">([\s\S]*?)<\/code><\/pre>/g,
                    '<pre class="code-block"><code class="language-$1">$2</code></pre>');

                // Add class to code blocks without language
                rendered = rendered.replace(/<pre><code>([\s\S]*?)<\/code><\/pre>/g,
                    '<pre class="code-block"><code>$1</code></pre>');

                // IX NESTED LISTS: Ensure proper nesting structure
                rendered = rendered.replace(/<\/li>\s*<ol>/g, '<ol>');
                rendered = rendered.replace(/<\/ol>\s*<\/li>/g, '</ol></li>');
                rendered = rendered.replace(/<\/li>\s*<ul>/g, '<ul>');
                rendered = rendered.replace(/<\/ul>\s*<\/li>/g, '</ul></li>');

                // Apply legacy cleaning if available
                if (typeof cleanMarkdownHTML === 'function') {
                    rendered = cleanMarkdownHTML(rendered);
                }
                console.log('📝 TWO-RULE: Rendered HTML:', rendered.substring(0, 200));
                lastElement.innerHTML = rendered;
            } else {
                console.warn('⚠️ TWO-RULE: Marked not available, using fallback');
                // Fallback: escape only; preserve raw newlines to avoid double <br>
                const safe = this.escapeHtml(newRawText);
                lastElement.innerHTML = `<div class="markdown-fallback" style="white-space: pre-wrap;">${safe}</div>`;
            }

            // ESTORE loading indicators after re-rendering
            loadingIndicators.forEach(({ element, nextSibling }) => {
                if (nextSibling && nextSibling.parentElement === this.markdownContainer) {
                    this.markdownContainer.insertBefore(element, nextSibling);
                } else {
                    this.markdownContainer.appendChild(element);
                }
                // Update reference if this was our current loading indicator
                if (this.loadingIndicator && element.className === this.loadingIndicator.className) {
                    this.loadingIndicator = element;
                }
            });

            // 🎨 ENHANCE CODE BLOCKS: Apply syntax highlighting after rendering
            if (window.codeBlockEnhancer && window.codeBlockEnhancer.initialized) {
                window.codeBlockEnhancer.enhanceContainer(lastElement);
            }

            console.log(`📝 TWO-RULE: Raw text concatenated and re-rendered (total: ${newRawText.length} chars)`);

        } else {
            // Create new content element ONLY when starting fresh or after visual content
            const contentElement = document.createElement('div');
            contentElement.className = 'two-rule-markdown-content';
            contentElement.setAttribute('data-package-id', pkg.id);
            contentElement.setAttribute('data-raw-text', pkg.content); // Store raw text
            contentElement.setAttribute('data-stream-position', pkg.position.toString()); // DD position tracking

            // Apply initial markdown formatting
            console.log('🔍 TWO-RULE: New markdown block, marked available?', typeof window.marked);
            if (typeof window.renderEnhancedMarkdown === 'function') {
                console.log('📝 TWO-RULE: Using renderEnhancedMarkdown');
                contentElement.innerHTML = window.renderEnhancedMarkdown(pkg.content);
            } else if (window.marked && typeof window.marked.parse === 'function') {
                console.log('📝 TWO-RULE: Using marked.parse for', pkg.content.length, 'chars');

                // ONFIGURE MARKED FOR BETTER RENDERING
                if (window.marked.setOptions) {
                    window.marked.setOptions({
                        breaks: true,
                        gfm: true,
                        pedantic: false,
                        smartLists: true,
                        smartypants: false,
                        headerIds: false,
                        mangle: false
                    });
                }

                const rendered = window.marked.parse(pkg.content);
                console.log('📝 TWO-RULE: Rendered HTML:', rendered.substring(0, 200));
                contentElement.innerHTML = rendered;
            } else {
                console.warn('⚠️ TWO-RULE: Marked not available, using fallback');
                // Fallback: escape only; preserve raw newlines
                const safe = this.escapeHtml(pkg.content);
                contentElement.innerHTML = `<div class="markdown-fallback" style="white-space: pre-wrap;">${safe}</div>`;
            }

            // Position-aware insertion: place BEFORE any child with a higher stream position.
            // This ensures that when a viz anchor sits at position 0 (inserted while
            // markdownContainer was still empty), a markdown package arriving later
            // with a LOWER actual position is correctly inserted BEFORE the anchor
            // rather than blindly appended after it.
            {
                let insertBeforeChild = null;
                const newPos = pkg.position;
                for (const child of Array.from(this.markdownContainer.children)) {
                    const childPos = parseInt(child.getAttribute('data-stream-position') || '-1', 10);
                    if (childPos > newPos) {
                        insertBeforeChild = child;
                        break;
                    }
                }
                if (insertBeforeChild) {
                    this.markdownContainer.insertBefore(contentElement, insertBeforeChild);
                } else {
                    this.markdownContainer.appendChild(contentElement);
                }
            }

            // 🎨 ENHANCE CODE BLOCKS: Apply syntax highlighting to new content
            if (window.codeBlockEnhancer && window.codeBlockEnhancer.initialized) {
                window.codeBlockEnhancer.enhanceContainer(contentElement);
            }

            console.log(`📝 TWO-RULE: New markdown element created (${pkg.content.length} chars)`);
        }
    }

    /**
     * ELPER: Check if there was a visual break before this markdown package
     */
    hasVisualBreakBefore(pkg) {
        // Check if there were any visual packages rendered since last markdown
        const allPackages = [...this.markdownPackages, ...this.visualPackages]
            .sort((a, b) => a.position - b.position);

        const currentIndex = allPackages.findIndex(p => p.id === pkg.id);
        if (currentIndex <= 0) return false;

        // Check if previous package was visual
        const previousPackage = allPackages[currentIndex - 1];
        return previousPackage && previousPackage.type === 'visual';
    }

    /**
     * ELPER: Check if content has significant markdown formatting
     */
    hasSignificantMarkdown(content) {
        const significantTriggers = [
            /^#{1,6}\s/m,           // Headers
            /\*\*.*?\*\*/,          // Bold
            /```[\s\S]*?```/,       // Code blocks
            /\|.*\|/,               // Tables
            /^\* /m,                // Bullet lists
            /^\d+\. /m,             // Numbered lists
            /^---\s*$/m,            // Horizontal rules
            /\[.*?\]\(.*?\)/,       // Links
        ];

        return significantTriggers.some(trigger => trigger.test(content));
    }

    /**
     * ISUAL RENDERING: Render Type 2 content with visualization engine
     */
    async renderVisualPackage(pkg) {
        console.log('🎨 TWO-RULE: renderVisualPackage called', {
            packageId: pkg.id,
            subType: pkg.subType,
            position: pkg.position,
            contentLength: pkg.content?.length,
            contentPreview: pkg.content?.substring(0, 100)
        });

        // Extract inner content (remove delimiters)
        const startDelimiter = this.getStartDelimiter(pkg.subType);
        const endDelimiter = this.getEndDelimiter(pkg.subType);

        console.log('🔍 TWO-RULE: Extracting content', {
            startDelimiter,
            endDelimiter,
            startIndex: pkg.content.indexOf(startDelimiter),
            endIndex: pkg.content.lastIndexOf(endDelimiter)
        });

        const startIndex = pkg.content.indexOf(startDelimiter) + startDelimiter.length;
        const endIndex = pkg.content.lastIndexOf(endDelimiter);
        const innerContent = pkg.content.slice(startIndex, endIndex).trim();

        console.log('📊 TWO-RULE: Extracted inner content', {
            innerContentLength: innerContent.length,
            innerContentPreview: innerContent.substring(0, 200)
        });

        // IMPLE FIX #3: Position-based insertion logic
        let vizContainer = null;

        // Prefer inserting at an anchor matching data-stream-position
        const anchor = this.container.querySelector(`.two-rule-anchor[data-stream-position="${pkg.position}"]`);
        if (anchor && anchor.parentElement) {
            vizContainer = document.createElement('div');
            vizContainer.className = 'viz-container';
            vizContainer.setAttribute('data-package-id', pkg.id);
            vizContainer.setAttribute('data-viz-type', pkg.subType);
            vizContainer.setAttribute('data-stream-position', pkg.position.toString());

            const contentArea = document.createElement('div');
            contentArea.className = 'viz-content-area';
            // Remove large fixed min-height to prevent empty gaps; allow content to drive height
            contentArea.style.cssText = 'width:100%;height:auto;min-height:0;';
            vizContainer.appendChild(contentArea);

            anchor.parentElement.replaceChild(vizContainer, anchor);
        } else if (this.loadingIndicator && this.loadingIndicator.parentElement) {
            // Replace the loading indicator with the visualization container (legacy)
            vizContainer = document.createElement('div');
            vizContainer.className = 'viz-container'; // IXED: Use existing CSS class
            vizContainer.setAttribute('data-package-id', pkg.id);
            vizContainer.setAttribute('data-viz-type', pkg.subType);
            vizContainer.setAttribute('data-stream-position', pkg.position.toString()); // DD position tracking

            // RITICAL: Add required content area for visualization engine
            const contentArea = document.createElement('div');
            contentArea.className = 'viz-content-area';
            contentArea.style.cssText = `
                width: 100%;
                height: auto;
                min-height: 0;
            `;
            vizContainer.appendChild(contentArea);

            // Replace loading indicator with visualization container
            this.loadingIndicator.parentElement.replaceChild(vizContainer, this.loadingIndicator);
            this.loadingIndicator = null;
        } else {
            // IMPLE FIX #3: Position-aware insertion instead of simple appendChild
            vizContainer = document.createElement('div');
            vizContainer.className = 'viz-container';
            vizContainer.setAttribute('data-package-id', pkg.id);
            vizContainer.setAttribute('data-viz-type', pkg.subType);
            vizContainer.setAttribute('data-stream-position', pkg.position.toString()); // DD position tracking

            // RITICAL: Add required content area for visualization engine
            const contentArea = document.createElement('div');
            contentArea.className = 'viz-content-area';
            contentArea.style.cssText = `
                width: 100%;
                height: auto;
                min-height: 0;
            `;
            vizContainer.appendChild(contentArea);

            // IMPLE FIX #3: Position-aware insertion
            const existingContainers = this.container.querySelectorAll('.viz-container, .two-rule-markdown-container > div');
            let insertionPoint = null;

            // Find where this package should be inserted based on position
            for (let i = 0; i < existingContainers.length; i++) {
                const containerPos = parseInt(existingContainers[i].getAttribute('data-stream-position') || '0');
                if (pkg.position < containerPos) {
                    insertionPoint = existingContainers[i];
                    break;
                }
            }

            if (insertionPoint) {
                this.container.insertBefore(vizContainer, insertionPoint);
                console.log(`🎯 Inserted visual at position ${pkg.position} before existing content`);
            } else {
                this.container.appendChild(vizContainer);
                console.log(`🎯 Appended visual at position ${pkg.position} (last in sequence)`);
            }
        }

        // ─── DOM-ATTACHMENT CHECK ────────────────────────────────────────────────────
        // KEY DESIGN (June 2026): DO NOT use a retry loop here.
        //
        // During thread load the processor runs while the message element is still
        // off-DOM (message_renderer appends it AFTER finalize() returns).  A retry
        // loop would hold `isReleasing = true` for seconds, blocking every subsequent
        // releaseReadyPackages() call and preventing markdown packages (text after the
        // viz) from ever rendering.
        //
        // Instead: check once, synchronously.
        //   • Off-DOM → push to deferredRenders immediately (no awaits).
        //               finalize()'s MutationObserver fires the instant the message
        //               is appended and _processDeferredRenders() renders the viz.
        //   • In-DOM  → brief rAF wait for layout, then render now (live streaming).
        let isInDom = false;
        let checkEl = vizContainer;
        for (let i = 0; i < 3 && checkEl; i++) {
            if (document.contains(checkEl)) { isInDom = true; break; }
            checkEl = checkEl.parentElement || this.container;
        }

        if (!isInDom) {
            // Off-DOM: defer immediately — NO awaits so isReleasing frees up at once.
            if (!this.deferredRenders) this.deferredRenders = [];
            this.deferredRenders.push({
                type: pkg.subType,
                content: innerContent,
                container: vizContainer,
                chartId: `viz-${pkg.id || Date.now()}`
            });

            const vizContentArea = vizContainer.querySelector('.viz-content-area') || vizContainer;
            vizContentArea.innerHTML = `
                <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
                    <div style="width: 32px; height: 32px; border: 3px solid var(--border-secondary); border-top: 3px solid var(--accent-primary); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 12px;"></div>
                    <p style="font-size: 14px; margin: 0;">Loading ${pkg.subType.toUpperCase()} visualization...</p>
                </div>
            `;
            console.log(`📌 TWO-RULE: Deferred ${pkg.subType} render (off-DOM – MutationObserver will handle)`);
            return; // Synchronous return – isReleasing freed up immediately
        }

        // In-DOM (live streaming): brief rAF so the browser has laid out the container.
        await new Promise(resolve => requestAnimationFrame(resolve));

        // Render visualization using available engine
        await this.renderVisualization(pkg.subType, innerContent, vizContainer);

        // Post-render corrective pass: ensure placement is still correct and stable
        try {
            const parent = this.markdownContainer || this.container;
            // If markdown container exists, ensure viz lives inside it to align with text flow
            if (this.markdownContainer && vizContainer.parentElement !== this.markdownContainer) {
                this.markdownContainer.appendChild(vizContainer);
            }

            // Build ordered list of candidate siblings within the chosen parent
            const candidates = Array.from(parent.children).filter(el => {
                if (!(el instanceof Element)) return false;
                const cls = el.classList || { contains: () => false };
                return cls.contains('two-rule-markdown-content') || cls.contains('viz-container');
            });

            // Find the first element with a position greater than this viz
            let referenceNode = null;
            for (const el of candidates) {
                const posAttr = el.getAttribute('data-stream-position');
                const pos = posAttr ? parseInt(posAttr, 10) : Number.MAX_SAFE_INTEGER; // markdown content always has pos; guard just in case
                if (pos > pkg.position) {
                    referenceNode = el;
                    break;
                }
            }

            if (referenceNode) {
                if (vizContainer.nextSibling !== referenceNode) {
                    parent.insertBefore(vizContainer, referenceNode);
                }
            } else {
                // Should be last in order
                if (vizContainer.parentElement !== parent || vizContainer !== parent.lastElementChild) {
                    parent.appendChild(vizContainer);
                }
            }
        } catch (_) { }

        console.log(`🎨 TWO-RULE: Visual package appended (${pkg.subType}, ${innerContent.length} chars)`);
    }

    /**
     * ISUALIZATION ENGINE: Render specific visualization type
     */
    async renderVisualization(type, content, container) {
        console.log('🎯 TWO-RULE: renderVisualization called', {
            type,
            contentLength: content?.length,
            contentPreview: content?.substring(0, 150),
            containerClass: container?.className,
            hasContentArea: !!container?.querySelector('.viz-content-area')
        });

        try {
            // 🔥 FIX (Jan 21, 2026): Only validate container exists, not DOM attachment
            // Container may not be in DOM during initial message rendering
            if (!container) {
                throw new Error('Container is null');
            }
            
            // Log but don't fail if container not in DOM yet
            if (!document.contains(container)) {
                console.log('⚠️ TWO-RULE: Container not in DOM yet (will be attached after message rendering)');
            }

            console.log('TWO-RULE: Container validation passed');

            // IMING FIX: Add small delay to ensure DOM stability
            await new Promise(resolve => requestAnimationFrame(resolve));
            // Always render into the inner .viz-content-area when available
            const targetContainer = container.querySelector('.viz-content-area') || container;

            console.log('🎯 TWO-RULE: Target container selected', {
                isContentArea: targetContainer.className?.includes('viz-content-area'),
                targetClass: targetContainer.className
            });

            // Ensure target container has a measurable size to prevent Plotly/Mermaid hiccups
            await this.ensureContainerReady(targetContainer);

            console.log('TWO-RULE: Container ready check passed');

            // 🔥 FIX (Jan 21, 2026): Remove strict DOM attachment requirements
            // Only validate container exists, not DOM attachment status
            // The container will be attached when parent message is appended to chat
            if (!targetContainer) {
                throw new Error(`Container not available for ${type} visualization`);
            }
            
            // Log DOM status for debugging but don't fail
            const inDOM = document.contains(targetContainer);
            console.log(`TWO-RULE: Target container DOM status: ${inDOM ? 'attached' : 'not attached (will attach after message render)'}`);

            const chartId = `two-rule-${type}-${Date.now()}`;

            // Find available visualization engine
            let engine = null;

            if (window.sidebarVisualizationState?.engine && window.sidebarVisualizationState.isInitialized) {
                engine = window.sidebarVisualizationState.engine;
            } else if (window.vizEngine && window.vizEngine.renderVisualizationDirectly) {
                engine = window.vizEngine;
            } else if (window.VisualizationEngine) {
                engine = new window.VisualizationEngine();
                await engine.init();
            }

            if (!engine) {
                throw new Error('No visualization engine available');
            }

            const item = { type: type, content: content };

            // CRITICAL FIX: Add DOM validation before rendering
            console.log(`🎯 TWO-RULE: Rendering ${type} in container:`, targetContainer.className, 'DOM attached:', document.contains(targetContainer));
            
            // Ensure target container is in DOM before rendering
            if (!document.contains(targetContainer)) {
                console.warn(`⚠️ VIZ-V3: Container not in DOM yet (will be attached after message rendering)`);
            }

            // Render with targeted handling for Plotly streaming reliability
            if (type === 'plotly') {
                const tryRender = async () => {
                    if (engine.renderPlotlyDirectly) {
                        await engine.renderPlotlyDirectly(item, targetContainer, chartId);
                    } else if (engine.renderVisualizationDirectly) {
                        await engine.renderVisualizationDirectly(item, container, chartId);
                    } else {
                        await engine.renderVisualization(item, container, chartId);
                    }
                };

                let attempt = 0;
                const maxAttempts = 3;
                let lastError = null;
                while (attempt < maxAttempts) {
                    try {
                        await tryRender();
                        //  RESIZE DISABLED - Was destroying Plotly charts
                        // Plotly already renders with responsive config, no resize needed
                        console.log('WO-RULE: Plotly rendered, skipping resize (uses responsive config)');
                        lastError = null;
                        break;
                    } catch (e) {
                        lastError = e;
                        await new Promise(r => setTimeout(r, 150));
                        await this.ensureContainerReady(container, 600);
                        attempt++;
                    }
                }
                if (lastError) throw lastError;
            } else if (type === 'mermaid') {
                if (engine.renderMermaidDirectly) {
                    // Route Mermaid directly into the inner .viz-content-area
                    await engine.renderMermaidDirectly(item, targetContainer, chartId);
                } else if (engine.renderVisualizationDirectly) {
                    await engine.renderVisualizationDirectly(item, container, chartId);
                } else {
                    await engine.renderVisualization(item, container, chartId);
                }
            } else if (type === 'react' || type === 'html' || type === 'latex' || type === 'svg' || type === 'cad' || type === 'schematic' || type === 'blueprint' || type === 'molecule' || type === 'apexcharts' || type === 'chartjs' || type === 'threejs' || type === 'gsap' || type === 'lottie') {
                // 🔥 FIX (April 9, 2026): Use targetContainer for all viz types, not just Plotly/Mermaid
                // This ensures viz-content-area is used consistently for all renders
                if (engine.renderVisualizationDirectly) {
                    await engine.renderVisualizationDirectly(item, targetContainer, chartId);
                } else if (engine.renderVisualization) {
                    await engine.renderVisualization(item, targetContainer, chartId);
                } else {
                    throw new Error(`No render method available for ${type}`);
                }
            } else {
                // Fallback for any other types
                if (engine.renderVisualizationDirectly) {
                    await engine.renderVisualizationDirectly(item, targetContainer, chartId);
                } else if (engine.renderVisualization) {
                    await engine.renderVisualization(item, targetContainer, chartId);
                } else {
                    throw new Error(`No render method available for ${type}`);
                }
            }

        } catch (error) {
            console.error(` TWO-RULE: Visualization rendering failed:`, error);

            // 🔥 FIX (Jan 21, 2026): Display error even if container not in DOM yet
            // Container may be attached after message rendering completes
            if (container) {
                container.innerHTML = `
                    <div class="two-rule-viz-error" style="text-align: center; padding: 20px; color: var(--accent-red);">
                        <h3>⚠️ ${type.toUpperCase()} Visualization Error</h3>
                        <p>${error.message}</p>
                        <details style="margin-top: 12px; text-align: left;">
                            <summary style="cursor: pointer;">Show Raw Content</summary>
                            <pre style="background: rgba(0,0,0,0.1); padding: 12px; border-radius: 4px; font-size: 11px; overflow-x: auto; white-space: pre-wrap;">${content}</pre>
                        </details>
                    </div>
                `;
                
                if (!document.contains(container)) {
                    console.warn('⚠️ TWO-RULE: Error displayed in container not yet in DOM (will be visible after message render)');
                }
            } else {
                console.error('❌ TWO-RULE: Cannot display error - container is null');
            }
        }
    }

    // Wait for container to be attached and have non-zero size
    async ensureContainerReady(container, maxWaitMs = 500) {
        const start = performance.now();
        
        // 🔥 FIX (Jan 21, 2026): Don't require DOM attachment
        // Container may not be in DOM during initial message rendering
        while (performance.now() - start < maxWaitMs) {
            // If container is in DOM and visible, we're done
            if (document.contains(container)) {
                const rect = container.getBoundingClientRect();
                const visible = rect.width > 1 && rect.height > 1 && container.offsetParent !== null;
                if (visible) return;
            }
            // Otherwise wait a bit and check again
            await new Promise(r => setTimeout(r, 50));
        }
        // Timeout reached - proceed anyway (container will be attached soon)
        console.log('⏱️ TWO-RULE: ensureContainerReady timeout, proceeding with render');
    }

    /**
     * RROR HANDLING: Render error package
     */
    renderErrorPackage(pkg, error) {
        const errorElement = document.createElement('div');
        errorElement.className = 'two-rule-error-package';
        errorElement.style.cssText = `
            padding: 12px;
            margin: 8px 0;
            background: var(--bg-error, #ffe6e6);
            border: 1px solid var(--border-error, #ff4444);
            border-radius: 6px;
            color: var(--text-error, #cc0000);
        `;

        errorElement.innerHTML = `
            <strong> Package ${pkg.id} Error (${pkg.type})</strong><br>
            ${error.message}
        `;

        this.container.appendChild(errorElement);
    }

    /**
     * ELIMITER DETECTION: Find visualization start delimiter
     */
    findVisualizationStart(content) {
        const patterns = [
            // ✅ Original
            { type: 'mermaid', start: '<MERMAID>', end: '</MERMAID>' },
            { type: 'plotly', start: '<PLOTLY>', end: '</PLOTLY>' },
            { type: 'google', start: '<GRAPH>', end: '</GRAPH>' },

            // ✨ Chart Libraries
            { type: 'chartjs', start: '<CHARTJS>', end: '</CHARTJS>' },
            { type: 'apexcharts', start: '<APEXCHARTS>', end: '</APEXCHARTS>' },

            // ✨ 3D & Animation
            { type: 'threejs', start: '<THREEJS>', end: '</THREEJS>' },
            { type: 'gsap', start: '<GSAP>', end: '</GSAP>' },
            { type: 'lottie', start: '<LOTTIE>', end: '</LOTTIE>' },

            // ✨ Interactive HTML
            { type: 'html', start: '<EXECUTE_HTML>', end: '</EXECUTE_HTML>' },
            { type: 'react', start: '<EXECUTE_REACT>', end: '</EXECUTE_REACT>' },

            // ✨ SVG/Technical Diagrams
            { type: 'svg', start: '<SVG_VISUAL>', end: '</SVG_VISUAL>' },
            { type: 'cad', start: '<CAD>', end: '</CAD>' },
            { type: 'schematic', start: '<SCHEMATIC>', end: '</SCHEMATIC>' },
            { type: 'blueprint', start: '<BLUEPRINT>', end: '</BLUEPRINT>' },
            { type: 'molecule', start: '<MOLECULE>', end: '</MOLECULE>' },

            // ✨ Engineering CAD Metadata
            { type: 'engineering_cad', start: '<ENGINEERING_CAD>', end: '</ENGINEERING_CAD>' },
            { type: 'technical_drawing', start: '<TECHNICAL_DRAWING>', end: '</TECHNICAL_DRAWING>' },
            { type: 'constraints_info', start: '<CONSTRAINTS_INFO>', end: '</CONSTRAINTS_INFO>' },
            { type: 'bom', start: '<BOM>', end: '</BOM>' },

            // ✨ Math
            { type: 'latex', start: '<LATEX>', end: '</LATEX>' }
        ];

        let best = null;
        for (const pattern of patterns) {
            let searchFrom = 0;
            while (true) {
                const pos = content.indexOf(pattern.start, searchFrom);
                if (pos === -1) break;

                const leftNewline = content.lastIndexOf('\n', pos);
                const leftSegment = content.slice(leftNewline + 1, pos);
                const onlyWhitespaceBefore = /^\s*$/.test(leftSegment);
                const nextChar = content[pos + pattern.start.length];
                const rightBoundaryOk = nextChar === undefined || nextChar === '\n' || nextChar === '\r';

                const globalPos = this.bufferPosition + pos;
                const insideFence = this.isInsideCodeFence(globalPos);

                if (onlyWhitespaceBefore && rightBoundaryOk && !insideFence) {
                    if (!best || pos < best.position) {
                        best = {
                            type: pattern.type,
                            position: pos,
                            startDelimiter: pattern.start,
                            endDelimiter: pattern.end
                        };
                    }
                    break; // This pattern's earliest valid occurrence found
                }
                searchFrom = pos + 1;
            }
        }
        return best;
    }

    // Detect if global index lies within a triple-backtick fenced code block
    isInsideCodeFence(globalIndex) {
        try {
            const upto = this.rawBuffer.slice(0, globalIndex);
            let count = 0;
            let idx = 0;
            while (true) {
                const fence = upto.indexOf('```', idx);
                if (fence === -1) break;
                count++;
                idx = fence + 3;
            }
            return count % 2 === 1; // odd -> inside fence
        } catch (_) {
            return false;
        }
    }

    // Longest length L such that content ends with a prefix of any start delimiter of length L
    getPotentialDelimiterSuffixLength(text) {
        if (!text) return 0;
        const starts = [
            '<MERMAID>', '<PLOTLY>', '<GRAPH>',
            '<CHARTJS>', '<APEXCHARTS>',
            '<THREEJS>', '<GSAP>', '<LOTTIE>',
            '<EXECUTE_HTML>',
            '<EXECUTE_REACT>',
            '<SVG_VISUAL>', '<CAD>', '<SCHEMATIC>', '<BLUEPRINT>', '<MOLECULE>',
            '<ENGINEERING_CAD>', '<TECHNICAL_DRAWING>', '<CONSTRAINTS_INFO>', '<BOM>',
            '<LATEX>'
        ];
        let maxLen = 0;
        for (const s of starts) {
            const maxCheck = s.length - 1; // proper prefix only
            for (let k = 1; k <= maxCheck; k++) {
                if (k <= text.length && text.endsWith(s.slice(0, k))) {
                    if (k > maxLen) maxLen = k;
                }
            }
        }
        return maxLen;
    }

    /**
     * ARKDOWN TRIGGERS: Check if content should trigger markdown release
     */
    hasMarkdownTrigger(content) {
        const triggers = [
            /\n/,                    // Line breaks
            /^#{1,6}\s/m,           // Headers
            /\*\*.*?\*\*/,          // Bold
            /```[\s\S]*?```/,       // Code blocks
            /\|.*\|/,               // Tables
            /^\* /m,                // Bullet lists
            /^\d+\. /m,             // Numbered lists
            /^---\s*$/m             // Horizontal rules
        ];

        return triggers.some(trigger => trigger.test(content));
    }

    /**
     * OADING INDICATORS: Show buffering state
     */
    showBufferingIndicator(type) {
        this.removeBufferingIndicator();

        this.loadingIndicator = document.createElement('div');
        this.loadingIndicator.className = 'two-rule-loading-indicator';
        this.loadingIndicator.style.cssText = `
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 6px;
            color: var(--text-secondary);
            font-size: 13px;
            margin: 8px 0;
        `;

        this.loadingIndicator.innerHTML = `
            <div style="width: 16px; height: 16px; border: 2px solid var(--border-secondary); border-top: 2px solid var(--accent-primary); border-radius: 50%; animation: spin 1s linear infinite;"></div>
            <span>Loading ${type.toUpperCase()} visualization...</span>
        `;

        // MPROVED: Append to markdown container if it exists, otherwise main container
        const targetContainer = this.markdownContainer || this.container;
        targetContainer.appendChild(this.loadingIndicator);

        // Add CSS animation if not already present
        if (!document.querySelector('#two-rule-spinner')) {
            const style = document.createElement('style');
            style.id = 'two-rule-spinner';
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * OADING INDICATORS: Update buffering progress
     */
    updateBufferingIndicator(bufferSize) {
        if (this.loadingIndicator) {
            const span = this.loadingIndicator.querySelector('span');
            if (span) {
                span.textContent = `Loading ${this.currentDelimiter.type.toUpperCase()} visualization... (${bufferSize} chars)`;
            }
        }
    }

    /**
     * OADING INDICATORS: Remove buffering indicator
     */
    removeBufferingIndicator() {
        if (this.loadingIndicator) {
            this.loadingIndicator.remove();
            this.loadingIndicator = null;
        }
    }

    /**
     * INALIZATION: Handle end of stream
     */
    async finalizeStream() {
        console.log('🏁 TWO-RULE: Finalizing stream');

        // Handle any remaining content in NORMAL state
        if (this.state === 'NORMAL' && this.bufferPosition < this.rawBuffer.length) {
            const remainingContent = this.rawBuffer.slice(this.bufferPosition);
            if (remainingContent.trim()) {
                this.packageMarkdownContent(remainingContent, this.bufferPosition);
            }
        }

        // Handle incomplete visual content in BUFFERING state
        if (this.state === 'BUFFERING_VISUAL') {
            console.warn('⚠️ TWO-RULE: Stream ended with incomplete visual content');
            this.removeBufferingIndicator();

            // Package as markdown to avoid losing content
            const incompleteContent = this.rawBuffer.slice(this.visualBufferStart);
            this.packageMarkdownContent(incompleteContent, this.visualBufferStart);
            this.state = 'NORMAL';
        }

        // Release any remaining packages
        await this.releaseReadyPackages();

        // GGRESSIVE: Clean up <br> tags around lists in the target container
        if (this.targetElement && typeof window.removeBreaksAroundLists === 'function') {
            setTimeout(() => {
                window.removeBreaksAroundLists(this.targetElement);
                console.log('WO-RULE: Post-stream <br> cleanup completed');
            }, 100);
        }

        console.log('✅ TWO-RULE: Thread completed successfully');
    }

    /**
     * TILITIES: Get delimiter strings
     */
    getStartDelimiter(type) {
        const delimiters = {
            // ✅ Existing
            'mermaid': '<MERMAID>',
            'plotly': '<PLOTLY>',
            'google': '<GRAPH>',
            'chartjs': '<CHARTJS>',

            // ✨ NEW: SVG/Technical Diagrams
            'svg': '<SVG_VISUAL>',
            'cad': '<CAD>',
            'schematic': '<SCHEMATIC>',
            'blueprint': '<BLUEPRINT>',
            'molecule': '<MOLECULE>',

            // ✨ NEW: Math & Interactive
            'latex': '<LATEX>',
            'html': '<EXECUTE_HTML>',
            'react': '<EXECUTE_REACT>',

            // ✨ NEW: 3D & Animation
            'apexcharts': '<APEXCHARTS>',
            'threejs': '<THREEJS>',
            'gsap': '<GSAP>',
            'lottie': '<LOTTIE>'
        };
        return delimiters[type] || '';
    }

    getEndDelimiter(type) {
        const delimiters = {
            // ✅ Existing
            'mermaid': '</MERMAID>',
            'plotly': '</PLOTLY>',
            'google': '</GRAPH>',
            'chartjs': '</CHARTJS>',

            // ✨ NEW: SVG/Technical Diagrams
            'svg': '</SVG_VISUAL>',
            'cad': '</CAD>',
            'schematic': '</SCHEMATIC>',
            'blueprint': '</BLUEPRINT>',
            'molecule': '</MOLECULE>',

            // ✨ NEW: Math & Interactive
            'latex': '</LATEX>',
            'html': '</EXECUTE_HTML>',
            'react': '</EXECUTE_REACT>',

            // ✨ NEW: 3D & Animation
            'apexcharts': '</APEXCHARTS>',
            'threejs': '</THREEJS>',
            'gsap': '</GSAP>',
            'lottie': '</LOTTIE>'
        };
        return delimiters[type] || '';
    }

    /**
     * TILITIES: HTML escaping
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * TILITIES: Generate content hash for deduplication
     */
    generateContentHash(item) {
        const content = typeof item.content === 'string' ? item.content : JSON.stringify(item.content);
        const hashInput = `${item.type}:${content}`;

        let hash = 0;
        for (let i = 0; i < hashInput.length; i++) {
            const char = hashInput.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }

        return Math.abs(hash).toString(36);
    }

    /**
     * RROR HANDLING: Handle processing errors
     */
    handleError(error) {
        console.error(' TWO-RULE: Processing error:', error);

        // Reset to safe state
        this.state = 'NORMAL';
        this.currentDelimiter = null;
        this.removeBufferingIndicator();

        // Show error message
        const errorElement = document.createElement('div');
        errorElement.className = 'two-rule-system-error';
        errorElement.style.cssText = `
            padding: 16px;
            margin: 8px 0;
            background: var(--bg-error, #ffe6e6);
            border: 1px solid var(--border-error, #ff4444);
            border-radius: 6px;
            color: var(--text-error, #cc0000);
        `;
        errorElement.innerHTML = `
            <strong> Two-Rule System Error</strong><br>
            ${error.message}<br>
            <small>System reset to normal state</small>
        `;

        this.container.appendChild(errorElement);
    }

    /**
     * EBUGGING: Log performance statistics
     */
    logStats() {
        const avgProcessingTime = this.stats.totalProcessingTime / this.stats.chunksProcessed;

        console.log('📊 TWO-RULE: Final Statistics', {
            chunksProcessed: this.stats.chunksProcessed,
            packagesReleased: this.stats.packagesReleased,
            markdownPackages: this.stats.markdownPackages,
            visualPackages: this.stats.visualPackages,
            totalProcessingTime: this.stats.totalProcessingTime.toFixed(2) + 'ms',
            averageChunkTime: avgProcessingTime.toFixed(2) + 'ms',
            bufferSize: this.rawBuffer.length,
            finalState: this.state
        });
    }
}

// =====================================
// INTEGRATION FUNCTIONS
// =====================================

/**
 * NTEGRATION: Initialize Two-Rule processor for streaming message
 */
function initializeTwoRuleProcessor(container) {
    console.log('🚀 TWO-RULE: Initializing processor');

    globalTwoRuleProcessor = new TwoRuleStreamProcessor(container);

    console.log('WO-RULE: Processor initialized');
    return globalTwoRuleProcessor;
}

/**
 * NTEGRATION: Process streaming content chunk
 */
async function processTwoRuleStreamingChunk(content) {
    if (!globalTwoRuleProcessor) {
        console.error(' TWO-RULE: Processor not initialized');
        return;
    }

    // RITICAL FIX: Pass FULL content, let processor handle incremental processing
    // The processor will calculate the NEW content internally
    const currentBufferLength = globalTwoRuleProcessor.rawBuffer?.length || 0;

    if (content.length <= currentBufferLength) {
        console.log(`📝 TWO-RULE: No new content (current: ${content.length}, buffer: ${currentBufferLength})`);
        return; // No new content
    }

    // Extract only the NEW content that hasn't been processed yet
    const newContent = content.slice(currentBufferLength);
    console.log(`📝 TWO-RULE: Processing ${newContent.length} new chars (total: ${content.length})`);

    await globalTwoRuleProcessor.processChunk(newContent);
}

/**
 * NTEGRATION: Finalize Two-Rule streaming
 */
async function finalizeTwoRuleStreaming() {
    if (globalTwoRuleProcessor) {
        await globalTwoRuleProcessor.finalizeStream();
        globalTwoRuleProcessor = null;
        console.log('🏁 TWO-RULE: Streaming finalized and processor cleaned up');
    }
}

/**
 * NTEGRATION: Reset Two-Rule system
 */
function resetTwoRuleSystem() {
    globalTwoRuleProcessor = null;
    console.log('🔄 TWO-RULE: System reset');
}

// =====================================
// MAIN STREAMING FUNCTIONS
// (Complete replacement for original streaming.js functions)
// =====================================

/**
 * AIN STREAMING: Process streaming response
 * Complete replacement for processStreamResponse
 */
async function processStreamResponse(response) {
    // Defensive: mark last activity to now so stale monitors don't immediately trigger
    try { if (window.streamingState) window.streamingState.lastActivityTs = Date.now(); } catch (_) { }
    // Validate response
    if (!response || !response.ok) {
        console.error(' Invalid response received:', {
            status: response?.status,
            statusText: response?.statusText,
            headers: response?.headers ? Object.fromEntries(response.headers.entries()) : 'No headers'
        });
        if (window.messageManager) {
            window.messageManager.addMessage(` Server error: ${response?.status} ${response?.statusText}. Please try again.`, false);
        }
        // Ensure UI/state are not left in loading state
        try {
            if (window.currentState) window.currentState.isLoading = false;
            window.messageManager?.hideProcessingToast?.();
            const sendButton = document.getElementById('sendButton');
            const messageInput = document.getElementById('messageInput');
            if (sendButton) sendButton.disabled = false;
            if (messageInput) messageInput.disabled = false;
        } catch (_) { }
        return;
    }

    if (!response.body) {
        console.error(' Response has no body');
        if (window.messageManager) {
            window.messageManager.addMessage(' No response body received. Please try again.', false);
        }
        return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullResponse = '';
    let isStreaming = false;
    let buffer = '';
    let lastChatId = null;
    let dataLineCount = 0;
    let contentChunks = 0;
    let chunkCount = 0;
    let totalLength = 0;

    console.log('📊 Starting Two-Rule progressive stream processing...');
    console.log('🔍 Stream response details:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        bodyType: typeof response.body
    });

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                console.log('🔍 Stream reader done');
                break;
            }

            const chunk = decoder.decode(value, { stream: true });
            buffer += chunk;
            chunkCount++;
            totalLength += chunk.length;

            if (chunkCount <= 3) {
                console.log(`🔍 Chunk ${chunkCount} raw content:`, JSON.stringify(chunk));
            }

            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            console.log(`🔍 Processing ${lines.length} lines from chunk ${chunkCount}`);

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    dataLineCount++;
                    // Define outside try so it can be logged in catch safely
                    let dataContent = '';
                    try {
                        dataContent = line.slice(6).trim();
                        console.log(`🔍 Data line ${dataLineCount}: "${dataContent.slice(0, 50)}${dataContent.length > 50 ? '...' : ''}"`);

                        if (dataContent && dataContent !== '[DONE]') {
                            const data = JSON.parse(dataContent);
                            console.log('🔍 Parsed data:', data);

                            // Check for content in multiple possible properties
                            let contentToAdd = null;
                            if (data.content) {
                                contentToAdd = data.content;
                            } else if (data.textResponse) {
                                contentToAdd = data.textResponse;
                            } else if (data.text) {
                                contentToAdd = data.text;
                            }

                            if (contentToAdd) {
                                contentChunks++;
                                fullResponse += contentToAdd;
                                console.log(`📝 Added content chunk ${contentChunks}: "${contentToAdd.slice(0, 30)}${contentToAdd.length > 30 ? '...' : ''}" (total response: ${fullResponse.length} chars)`);

                                if (!isStreaming) {
                                    console.log('🎬 Starting Two-Rule streaming message display');
                                    startStreamingMessage();
                                    isStreaming = true;
                                }

                                // Use Two-Rule system for content processing
                                await updateStreamingMessageTwoRule(fullResponse);
                            } else {
                                console.log('⚠️ Data chunk has no recognized content property:', data);
                                console.log('🔍 Available properties:', Object.keys(data));
                            }

                            if (data.chatId) {
                                lastChatId = data.chatId;
                            }
                        }
                    } catch (parseError) {
                        console.warn('⚠️ Failed to parse streaming data:', parseError.message);
                        console.log('🔍 Problematic line:', JSON.stringify(line));
                        try {
                            console.log('🔍 Data content that failed:', JSON.stringify(dataContent));
                        } catch (_) {
                            // no-op
                        }
                    }
                } else if (line.trim()) {
                    // Fallback: handle non-SSE lines as raw content unless they are SSE control lines
                    const trimmed = line.trim();
                    const isControl = trimmed.startsWith('event:') || trimmed.startsWith('id:') || trimmed.startsWith(':');
                    if (!isControl) {
                        if (!isStreaming) {
                            console.log('🎬 Starting Two-Rule streaming (raw content fallback)');
                            startStreamingMessage();
                            isStreaming = true;
                        }
                        fullResponse += trimmed + '\n';
                        contentChunks++;
                        await updateStreamingMessageTwoRule(fullResponse);
                    } else {
                        console.log('🔍 SSE control line:', JSON.stringify(line.slice(0, 100)));
                    }
                }
            }

            // Yield control periodically
            if (chunkCount % 25 === 0) {
                await new Promise(resolve => setTimeout(resolve, 0));
            }
        }

        // Process remaining buffer content
        console.log('🔍 Processing remaining buffer:', buffer ? `"${buffer.slice(0, 100)}${buffer.length > 100 ? '...' : ''}"` : 'EMPTY');
        if (buffer.trim() && buffer.startsWith('data: ')) {
            console.log('🔍 Processing final buffer as data line');
            try {
                const dataContent = buffer.slice(6).trim();
                console.log('🔍 Final buffer data content:', JSON.stringify(dataContent));
                if (dataContent && dataContent !== '[DONE]') {
                    const data = JSON.parse(dataContent);
                    console.log('🔍 Final buffer parsed data:', data);

                    // Check for content in multiple possible properties
                    let contentToAdd = null;
                    if (data.content) {
                        contentToAdd = data.content;
                    } else if (data.textResponse) {
                        contentToAdd = data.textResponse;
                    } else if (data.text) {
                        contentToAdd = data.text;
                    }

                    if (contentToAdd) {
                        fullResponse += contentToAdd;
                        console.log('🔍 Added final buffer content, total response now:', fullResponse.length, 'chars');
                        if (isStreaming) {
                            await updateStreamingMessageTwoRule(fullResponse);
                        }
                    }
                    if (data.chatId) {
                        lastChatId = data.chatId;
                    }
                }
            } catch (parseError) {
                console.warn('⚠️ Failed to parse final buffer:', parseError.message);
                console.log('🔍 Final buffer that failed:', JSON.stringify(buffer));
            }
        } else if (buffer.trim()) {
            // Fallback: treat remaining buffer as raw content
            const trimmed = buffer.trim();
            const isControl = trimmed.startsWith('event:') || trimmed.startsWith('id:') || trimmed.startsWith(':');
            if (!isControl) {
                fullResponse += trimmed;
                if (isStreaming) {
                    await updateStreamingMessageTwoRule(fullResponse);
                } else if (trimmed.length > 0 && window.messageManager) {
                    // If we never started streaming but have raw content, show it directly
                    window.messageManager.addMessage(fullResponse, false);
                }
            } else {
                console.log('🔍 Final buffer contains SSE control text only');
            }
        }

        if (isStreaming) {
            console.log('🏁 Stream ended - finishing Two-Rule message');

            if (streamingMessageElement && lastChatId) {
                streamingMessageElement.setAttribute('data-chat-id', lastChatId);

                // RITICAL FIX: Safe chatIdTracker access
                if (window.messageManager && window.messageManager.chatIdTracker) {
                    if (typeof window.messageManager.chatIdTracker.set === 'function') {
                        window.messageManager.chatIdTracker.set(streamingMessageElement, lastChatId);
                    } else if (typeof window.messageManager.chatIdTracker === 'object') {
                        // Alternative: Direct object assignment if it's a Map-like object
                        window.messageManager.chatIdTracker[lastChatId] = streamingMessageElement;
                    } else {
                        console.warn('⚠️ TWO-RULE: chatIdTracker format not recognized');
                    }
                } else {
                    console.warn('⚠️ TWO-RULE: messageManager or chatIdTracker not available');
                }
            }

            finishStreamingMessage();
        } else if (fullResponse && window.messageManager) {
            console.log('📝 Adding complete message (no streaming UI was shown)');
            window.messageManager.addMessage(fullResponse, false, null, [], null, lastChatId);
        } else {
            console.warn('⚠️ No response content received');
            console.log('🔍 Debug info:', {
                fullResponseLength: fullResponse.length,
                isStreaming,
                chunkCount,
                dataLineCount,
                contentChunks,
                totalLength,
                messageManagerExists: !!window.messageManager
            });

            if (window.messageManager) {
                window.messageManager.addMessage(' No response received. Please try again.', false);
            } else {
                console.error(' No messageManager available to show error message');
            }
            // If a streaming UI exists (pre-created), close it to avoid lingering spinners
            if (!isStreaming && typeof streamingMessageElement !== 'undefined' && streamingMessageElement) {
                finishStreamingMessage();
            }
        }

    } catch (error) {
        console.error(' Two-Rule streaming processing error:', error);
        console.log('🔍 Error context:', {
            fullResponseLength: fullResponse.length,
            isStreaming,
            chunkCount,
            totalLength,
            errorType: error.constructor.name,
            errorMessage: error.message,
            errorStack: error.stack?.split('\n').slice(0, 5)
        });

        if (fullResponse) {
            console.log('🔄 Attempting to recover with partial response...');
            if (isStreaming) {
                if (streamingMessageElement && lastChatId) {
                    streamingMessageElement.setAttribute('data-chat-id', lastChatId);
                    // RITICAL FIX: Safe chatIdTracker access  
                    if (window.messageManager && window.messageManager.chatIdTracker) {
                        if (typeof window.messageManager.chatIdTracker.set === 'function') {
                            window.messageManager.chatIdTracker.set(streamingMessageElement, lastChatId);
                        } else if (typeof window.messageManager.chatIdTracker === 'object') {
                            window.messageManager.chatIdTracker[lastChatId] = streamingMessageElement;
                        } else {
                            console.warn('⚠️ TWO-RULE: chatIdTracker format not recognized');
                        }
                    } else {
                        console.warn('⚠️ TWO-RULE: messageManager or chatIdTracker not available');
                    }
                }
                finishStreamingMessage();
            } else if (window.messageManager) {
                window.messageManager.addMessage(fullResponse, false, null, [], null, lastChatId);
            }
        } else if (window.messageManager) {
            window.messageManager.addMessage(` Error processing streaming response: ${error.message}. Please try again.`, false);
        }
        // Defensive: finalize UI/state on error
        try {
            if (typeof finishStreamingMessage === 'function') finishStreamingMessage();
        } catch (_) { }
        try {
            if (window.currentState) window.currentState.isLoading = false;
            window.messageManager?.hideProcessingToast?.();
            const sendButton = document.getElementById('sendButton');
            const messageInput = document.getElementById('messageInput');
            if (sendButton) sendButton.disabled = false;
            if (messageInput) messageInput.disabled = false;
            window.updateStatus?.('Ready', 'connected');
        } catch (_) { }
    } finally {
        console.log(`📊 Two-Rule stream processing complete. Final response: ${fullResponse.length} characters`);
        console.log('🔍 Final processing stats:', {
            chunkCount,
            dataLineCount: dataLineCount || 0,
            contentChunks: contentChunks || 0,
            totalLength,
            isStreaming,
            lastChatId
        });
        // Ensure loading state isn't left dangling if upstream callers bail early
        try {
            if (window.currentState) window.currentState.isLoading = false;
        } catch (_) { }
    }
}

/**
 * TREAMING UPDATE: Update streaming message with Two-Rule system
 * Complete replacement for updateStreamingMessageIncremental
 */
async function updateStreamingMessageTwoRule(content) {
    if (!streamingMessageElement || !content) return;

    const streamedContentDiv = streamingMessageElement.querySelector('#streamedContent');
    const thinkingIndicator = streamingMessageElement.querySelector('#thinkingIndicator');

    if (!streamedContentDiv) return;

    // IMPLE FIX #1: Always try to remove thinking indicators on ANY real content
    if (content.trim() && content.length > 0) {
        removeAllThinkingIndicators(streamingMessageElement);
        streamingState.isFirstContent = false;
        console.log('🎯 Removed thinking indicators, starting Two-Rule content display');
    }

    // Initialize Two-Rule processor if not exists
    if (!globalTwoRuleProcessor) {
        globalTwoRuleProcessor = new TwoRuleStreamProcessor(streamedContentDiv);
        console.log('🚀 NEW: Two-Rule ProgressiveStreamProcessor initialized');
    }

    // Process content through Two-Rule system
    await processTwoRuleStreamingChunk(content);

    // Keep absolute RAW content up to date on the bubble for exact Raw copy
    try {
        const bubble = streamingMessageElement?.querySelector('.message-bubble');
        if (bubble && typeof content === 'string') {
            bubble.setAttribute('data-original-raw', content);
        }
    } catch (e) {
        console.warn('⚠️ Failed to update data-original-raw during stream:', e);
    }

    // Auto-scroll if enabled - using AutoScrollManager API
    if (window.autoScrollManager && window.autoScrollManager.isEnabled()) {
        window.autoScrollManager.scrollDuringStream();
    }
}

/**
 * TREAMING START: Initialize streaming message container
 * Enhanced version with Two-Rule system support
 */
function startStreamingMessage() {
    console.log('🎬 Starting Two-Rule progressive streaming message display');

    // RITICAL FIX: Reset streaming state for new message
    streamingState.isFirstContent = true;
    streamingState.lastProcessedLength = 0;
    streamingState.renderedComponents = [];

    // Mark streaming as started - using AutoScrollManager API
    if (window.autoScrollManager) {
        window.autoScrollManager.startStreaming();
        console.log('🔄 Started streaming - auto-scroll enabled for new message');
    }

    // Reset Two-Rule system
    resetTwoRuleSystem();

    // Remove existing loading message
    const existingLoading = document.getElementById('loadingMessage');
    if (existingLoading) {
        existingLoading.remove();
    }

    // Create streaming message element
    streamingMessageElement = document.createElement('div');
    streamingMessageElement.className = 'message assistant';

    streamingMessageElement.innerHTML = `<div class="message-avatar"><i class="fa-solid fa-atom ai-message-avatar" title="AI Assistant - Two-Rule Streaming Response"></i></div><div class="message-content-wrapper"><div class="message-bubble assistant-bubble text-${window.currentTextSize || 'normal'}"><button class="collapse-toggle-btn top-right" title="Collapse message"><i class="fa-solid fa-chevron-down"></i></button><div class="message-content"><div id="streamedContent" class="progressive-stream-content two-rule-content"></div></div><button class="collapse-toggle-btn bottom-right" title="Expand message"><i class="fa-solid fa-chevron-up"></i></button></div><div class="message-meta"><div class="message-timestamp">${typeof formatTime === 'function' ? formatTime(Date.now()) : new Date().toLocaleTimeString()}</div><div class="message-actions"><button class="message-action-btn" data-action="voice" title="Read aloud"><i class="fa-solid fa-volume-up"></i></button><button class="message-action-btn" data-action="regenerate" title="Regenerate response"><i class="fa-solid fa-redo"></i></button><button class="copy-btn" title="Copy message"><i class="fas fa-copy"></i></button><button class="message-action-btn print print-btn" title="Print message"><i class="fas fa-print"></i></button><button class="message-action-btn edit" title="Edit message"><i class="fas fa-edit"></i></button><button class="message-action-btn delete" title="Delete message"><i class="fas fa-trash"></i></button></div></div></div>`;

    // Setup event listeners
    setupStreamingMessageEventListeners();

    // Add to messages container
    const messagesContainer = window.elements?.messagesContainer || document.getElementById('messagesContainer');
    if (messagesContainer) {
        messagesContainer.appendChild(streamingMessageElement);

        // Auto-scroll to the new message - using AutoScrollManager
        if (window.autoScrollManager && window.autoScrollManager.isEnabled()) {
            window.autoScrollManager.scrollDuringStream();
        }
    } else {
        console.error(' Messages container not found for streaming message');
        return;
    }

    // Initialize absolute RAW holder for streaming assistant message
    try {
        const bubble = streamingMessageElement.querySelector('.message-bubble');
        if (bubble) {
            bubble.setAttribute('data-original-raw', '');
        }
    } catch (e) {
        console.warn('⚠️ Could not initialize data-original-raw on streaming bubble:', e);
    }

    // Enhance copy/print for this streaming message, if available
    try {
        if (typeof window.enhanceMessageWithPrintCopy === 'function') {
            window.enhanceMessageWithPrintCopy(streamingMessageElement);
        }
    } catch (e) {
        console.warn('⚠️ Could not enhance streaming message with Print & Copy module:', e);
    }

    // Reset streaming state
    streamingState = {
        isFirstContent: true,
        lastProcessedLength: 0,
        renderedComponents: [],
        lastActivityTs: Date.now()
    };

    console.log('wo-Rule progressive streaming message container created and ready');
    // Mark app as streaming-active if state exists
    try { if (window.currentState) window.currentState.isLoading = true; } catch (_) { }
    return streamingMessageElement;
}

/**
 * VENT LISTENERS: Setup streaming message event handlers
 */
function setupStreamingMessageEventListeners() {
    if (!streamingMessageElement) return;

    const copyBtn = streamingMessageElement.querySelector('.copy-btn');
    const editBtn = streamingMessageElement.querySelector('.edit');
    const deleteBtn = streamingMessageElement.querySelector('.delete');
    const printBtn = streamingMessageElement.querySelector('.print-btn');
    const collapseBtns = streamingMessageElement.querySelectorAll('.collapse-toggle-btn');

    if (copyBtn) {
        copyBtn.addEventListener('click', function () {
            copyMessage(this);
        });
    }

    if (editBtn) {
        editBtn.addEventListener('click', function () {
            editMessage(this.closest('.message'));
        });
    }

    if (deleteBtn) {
        deleteBtn.addEventListener('click', function () {
            deleteMessage(this.closest('.message'));
        });
    }

    if (printBtn) {
        printBtn.addEventListener('click', function () {
            if (window.printCopyModule) {
                window.printCopyModule.printMessage(this.closest('.message'));
            } else {
                console.warn('Print module not available');
            }
        });
    }

    collapseBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            toggleMessageCollapse(this);
        });
    });
}

/**
 * TREAMING FINISH: Complete streaming message processing
 */
function finishStreamingMessage() {
    console.log('🏁 Finishing Two-Rule progressive streaming message');

    // Finalize any remaining buffered content
    if (globalTwoRuleProcessor) {
        console.log('🔚 Finalizing Two-Rule stream to handle any remaining content');
        finalizeTwoRuleStreaming();
    }

    if (streamingMessageElement) {
        // Remove thinking indicator if still present
        const thinkingIndicator = streamingMessageElement.querySelector('#thinkingIndicator');
        if (thinkingIndicator) {
            thinkingIndicator.remove();
        }

        // Enhance message with print/copy capabilities
        if (window.printCopyModule) {
            window.printCopyModule.enhanceNewMessage(streamingMessageElement);
        }

        // Update UI counters
        if (window.currentState) {
            window.currentState.messageCounter++;
        }
        if (window.updateCollapseAllButtonState) {
            window.updateCollapseAllButtonState();
        }

        streamingMessageElement = null;
        console.log('wo-Rule progressive streaming message completed successfully');
    }

    // Mark streaming as finished - using AutoScrollManager API
    // This will clear temporary pause and reset auto-scroll to default ON
    if (window.autoScrollManager) {
        window.autoScrollManager.finishStreaming();
        console.log('🔄 Finished streaming - auto-scroll reset to default ON');
    }

    // Reset streaming state
    streamingState = {
        isFirstContent: true,
        lastProcessedLength: 0,
        renderedComponents: []
    };

    resetTwoRuleSystem();

    // Ensure app state/input are unlocked after finishing stream
    try {
        if (window.currentState) window.currentState.isLoading = false;
        const sendButton = document.getElementById('sendButton');
        const messageInput = document.getElementById('messageInput');
        if (sendButton) sendButton.disabled = false;
        if (messageInput) messageInput.disabled = false;
        if (typeof window.updateStatus === 'function') window.updateStatus('Ready', 'connected');
        // Also hide any processing toast left visible
        window.messageManager?.hideProcessingToast?.();
    } catch (e) {
        console.warn('⚠️ Could not reset UI/state on stream finish:', e?.message || e);
    }
}
// =====================================
// LEGACY COMPATIBILITY FUNCTIONS
// (For backward compatibility with existing code)
// =====================================

/**
 * EGACY: Compatibility wrapper for updateStreamingMessageIncremental
 */
async function updateStreamingMessageIncremental(content) {
    return await updateStreamingMessageTwoRule(content);
}

/**
 * EGACY: Compatibility wrapper for updateStreamingMessage
 */
function updateStreamingMessage(content) {
    return updateStreamingMessageTwoRule(content);
}

// =====================================
// MARKDOWN RENDERING SYSTEM
// (Complete markdown processing with Two-Rule compatibility)
// =====================================

/**
 * AIN MARKDOWN: Primary markdown rendering function
 */
function renderMarkdown(text) {
    if (!text) return '';

    // Check for visualizations
    const hasVisualizations = /<(PLOTLY|MERMAID|GRAPH|CHARTJS)>/i.test(text) ||
        /\{\{(PLOTLY|MERMAID|GRAPH|CHARTJS)_START\}\}/i.test(text);

    if (hasVisualizations) {
        console.log('🎨 Content has visualizations, using VisualizationEngine...');

        if (window.sidebarVisualizationState?.engine && window.sidebarVisualizationState.isInitialized) {
            const containerId = `sidebar-viz-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
            const vizHtml = `<div id="${containerId}" class="sidebar-viz-content" data-original-viz="${escapeHtml(text)}">${text}</div>`;

            setTimeout(async () => {
                const container = document.getElementById(containerId);
                if (container) {
                    try {
                        await window.sidebarVisualizationState.engine.renderAll(text, container);
                        console.log('idebar visualization rendered via VisualizationEngine');

                        const vizContainers = container.querySelectorAll('.viz-container');
                        vizContainers.forEach(vizContainer => {
                            vizContainer.setAttribute('data-original-viz', text);
                        });
                    } catch (error) {
                        console.error(' VisualizationEngine rendering failed:', error);
                        // Prefer centralized formatter if available; avoid local renderer to prevent interference
                        if (typeof window.renderEnhancedMarkdown === 'function') {
                            container.innerHTML = window.renderEnhancedMarkdown(text);
                        } else {
                            const safe = escapeHtml(text);
                            container.innerHTML = `<div class="markdown-fallback" style="white-space: pre-wrap;">${safe}</div>`;
                        }
                    }
                }
            }, 10);

            return vizHtml;
        } else {
            console.warn('⚠️ VisualizationEngine not ready, using centralized enhanced markdown');
            // Prefer centralized formatter if available; avoid local renderer to prevent interference
            if (typeof window.renderEnhancedMarkdown === 'function') {
                return window.renderEnhancedMarkdown(text);
            }
            const safe = escapeHtml(text);
            return `<div class="markdown-fallback" style="white-space: pre-wrap;">${safe}</div>`;
        }
    }
    // Always delegate to centralized formatter for non-visual content
    if (typeof window.renderEnhancedMarkdown === 'function') {
        return window.renderEnhancedMarkdown(text);
    }
    const safe = escapeHtml(text);
    return `<div class="markdown-fallback" style="white-space: pre-wrap;">${safe}</div>`;
}

/**
 * NHANCED MARKDOWN: Advanced markdown processing
 */
function renderEnhancedMarkdown(text) {
    let htmlOutput;

    // Always delegate to centralized formatter to avoid interference and double-processing
    try {
        if (!htmlOutput && window.markdownFormatter && typeof window.markdownFormatter.renderEnhancedMarkdown === 'function') {
            htmlOutput = window.markdownFormatter.renderEnhancedMarkdown(text);
        }

        if (!htmlOutput) {
            const globalRenderMarkdown = typeof window.renderMarkdown === 'function' ? window.renderMarkdown : null;
            if (globalRenderMarkdown &&
                globalRenderMarkdown !== renderEnhancedMarkdown &&
                globalRenderMarkdown !== renderMarkdown) {
                // Fall back to externally supplied renderer if available
                htmlOutput = globalRenderMarkdown(text);
            }
        }
    } catch (error) {
        console.warn('⚠️ Two-Rule: Enhanced markdown delegation failed, using local fallback', error);
    }

    // Prefer marked.js for local rendering when no centralized formatter exists
    if (!htmlOutput) {
        try {
            if (window.marked && typeof window.marked.parse === 'function') {
                htmlOutput = window.marked.parse(text || '');
            }
        } catch (error) {
            console.warn('⚠️ Two-Rule: marked.js parsing failed, falling back to plain text', error);
        }
    }

    // Minimal safe fallback: escape and preserve newlines via pre-wrap
    if (!htmlOutput) {
        const div = document.createElement('div');
        div.textContent = (text || '').toString();
        htmlOutput = `<div class="markdown-fallback" style="white-space: pre-wrap;">${div.innerHTML}</div>`;
    }

    return postProcessMarkdownHTML(htmlOutput);
}

function postProcessMarkdownHTML(html) {
    if (html == null) return html;
    if (typeof html !== 'string') {
        // Some renderers may return DOM nodes; leave untouched
        return html;
    }

    if (!/<\s*(ul|ol|li|p)\b/i.test(html)) {
        return html;
    }

    let cleaned = html;

    // RITICAL FIX: Remove <br> tags before and after <p> tags
    cleaned = cleaned.replace(/(?:\s*<br\s*\/?>\s*)+(?=<\s*p\b)/gi, '');
    cleaned = cleaned.replace(/<\/p>\s*(?:<br\s*\/?>\s*)+/gi, '</p>');

    // emove <br> at the very start or end of <p> tags
    cleaned = cleaned.replace(/(<p\b[^>]*>)\s*(?:<br\s*\/?>\s*)+/gi, '$1');
    cleaned = cleaned.replace(/(?:<br\s*\/?>\s*)+\s*<\/p>/gi, '</p>');

    // OMPREHENSIVE: Remove all <br> variations around lists
    cleaned = cleaned.replace(/(?:\s*<br\s*\/?>\s*)+(?=<\s*(ul|ol)\b)/gi, '');
    cleaned = cleaned.replace(/(?:\s*<br\s*\/?>\s*)+(?=<\s*li\b)/gi, '');
    cleaned = cleaned.replace(/<\/(ul|ol)>\s*(?:<br\s*\/?>\s*)+/gi, '<\/$1>');
    cleaned = cleaned.replace(/<\/li>\s*(?:<br\s*\/?>\s*)+/gi, '<\/li>');
    cleaned = cleaned.replace(/<li>\s*(?:<br\s*\/?>\s*)+/gi, '<li>');
    cleaned = cleaned.replace(/(?:<br\s*\/?>\s*)+<\/li>/gi, '<\/li>');

    // emove <br> between </p> and <ul>/<ol>
    cleaned = cleaned.replace(/<\/p>\s*(?:<br\s*\/?>\s*)+\s*(?=<\s*(ul|ol)\b)/gi, '</p>');

    // emove <br> between </ul>/</ol> and <p>
    cleaned = cleaned.replace(/<\/(ul|ol)>\s*(?:<br\s*\/?>\s*)+\s*(?=<\s*p\b)/gi, '<\/$1>');

    // Remove empty paragraphs with only <br>
    cleaned = cleaned.replace(/<p>\s*(?:<br\s*\/?>\s*)+\s*<\/p>/gi, '');

    // EW: Clean up around bullet spans specifically
    cleaned = cleaned.replace(/<br\s*\/?>\s*(<span class="mermaid-bullet">)/gi, '$1');
    cleaned = cleaned.replace(/(<\/span>)\s*<br\s*\/?>\s*(<span class="mermaid-bullet">)/gi, '$1$2');
    cleaned = cleaned.replace(/(<span class="mermaid-bullet">[^<]*<\/span>)\s*<br\s*\/?>/gi, '$1');

    // EW: Remove excessive consecutive <br> tags (max 2 for paragraph)
    cleaned = cleaned.replace(/(<br\s*\/?>\s*){3,}/gi, '<br><br>');

    return cleaned;
}

function ensurePlotlyResponsive(root) {
    if (!window.Plotly) return;
    const scope = root instanceof Element ? root : document;
    const charts = scope.querySelectorAll ? scope.querySelectorAll('.js-plotly-plot') : [];
    charts.forEach(chart => {
        if (!(chart instanceof HTMLElement)) return;
        chart.style.width = '100%';
        chart.style.maxWidth = '100%';
        if (chart.parentElement) {
            chart.parentElement.style.width = '100%';
            chart.parentElement.style.maxWidth = '100%';
        }
        requestPlotlyResize(chart);
        attachPlotlyResizeObserver(chart);
    });
    registerGlobalPlotlyResizeHandler();
}

function requestPlotlyResize(chart) {
    if (!window.Plotly || !chart) return;
    if (pendingPlotlyResizeHandles.has(chart)) {
        return;
    }
    const handle = requestAnimationFrame(() => {
        pendingPlotlyResizeHandles.delete(chart);

        // IX: Check if element is in DOM and visible before resizing
        if (!document.body.contains(chart)) {
            console.debug('⏭️ Skipping Plotly resize - element not in DOM');
            return;
        }

        if (!chart.offsetParent) {
            // Element is not visible (display: none, visibility: hidden, or parent hidden)
            console.debug('⏭️ Skipping Plotly resize - element not visible');
            return;
        }

        // Check if chart is actually a Plotly div with data
        if (!chart._fullLayout || !chart.layout) {
            console.debug('⏭️ Skipping Plotly resize - not a valid Plotly chart');
            return;
        }

        try {
            window.Plotly.Plots.resize(chart);
        } catch (error) {
            // Silently skip - element was likely moved/removed during animation
            console.debug('⏭️ Plotly resize skipped:', error.message);
        }
    });
    pendingPlotlyResizeHandles.set(chart, handle);
}

function attachPlotlyResizeObserver(chart) {
    if (!window.ResizeObserver || plotlyResizeObservers.has(chart)) return;
    const observeTarget = chart.closest('.viz-content-area') || chart.parentElement || chart;
    if (!observeTarget) return;
    const observer = new ResizeObserver(() => requestPlotlyResize(chart));
    observer.observe(observeTarget);
    plotlyResizeObservers.set(chart, observer);
}

function registerGlobalPlotlyResizeHandler() {
    if (plotlyWindowResizeHandlerRegistered) return;
    window.addEventListener('resize', () => ensurePlotlyResponsive(document));
    plotlyWindowResizeHandlerRegistered = true;
}

/**
 * IST PROCESSING: Enhanced list handling
 */
function processEnhancedLists(text) {
    const lines = text.split('\n');
    const result = [];
    let inList = false;
    let listType = null;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();

        const unorderedMatch = line.match(/^(\s*)[-*+]\s+(.+)$/);
        const orderedMatch = line.match(/^(\s*)\d+\.\s+(.+)$/);

        if (unorderedMatch || orderedMatch) {
            const content = (unorderedMatch || orderedMatch)[2];
            const currentType = unorderedMatch ? 'ul' : 'ol';

            if (!inList) {
                result.push(`<${currentType} class="markdown-list markdown-${currentType}">`);
                inList = true;
                listType = currentType;
            }

            result.push(`<li class="markdown-list-item">${content}</li>`);
        } else {
            if (inList) {
                result.push(`</${listType}>`);
                inList = false;
                listType = null;
            }
            // Preserve blank lines and normal lines to keep paragraph spacing and HR markers
            result.push(line);
        }
    }

    if (inList) {
        result.push(`</${listType}>`);
    }
    // Join with newline to preserve line breaks for downstream paragraph/HR processing
    return result.join('');
}

/**
 * ONTENT DETECTION: Check for markdown patterns
 */
function isMarkdownContent(content) {
    if (!content || typeof content !== 'string') return false;

    const markdownIndicators = [
        /^#{1,6}\s/m,           // Headers
        /\*\*.*?\*\*/,          // Bold
        /\*.*?\*/,              // Italic
        /```[\s\S]*?```/,       // Code blocks
        /`.*?`/,                // Inline code
        /^\* /m,                // Bullet lists
        /^\d+\. /m,             // Numbered lists
        /\[.*?\]\(.*?\)/,       // Links
        /^\>/m,                 // Blockquotes
        /^---\s*$/m             // Horizontal rules
    ];

    return markdownIndicators.some(pattern => pattern.test(content));
}

/**
 * ONTENT DETECTION: Check for visualization content
 */
function hasVisualizationContent(content) {
    if (!content || typeof content !== 'string') return false;

    const patterns = [
        /<(PLOTLY|MERMAID|GRAPH|CHARTJS)>/i,
        /\{\{(PLOTLY|MERMAID|GRAPH|CHARTJS)_START\}\}/i
    ];

    return patterns.some(pattern => pattern.test(content));
}

/**
 * TML UTILITY: Escape HTML characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// =====================================
// VISUALIZATION ENGINE INTEGRATION
// =====================================

/**
 * IZ ENGINE: Initialize sidebar visualization engine
 */
async function initializeSidebarVisualizationEngine() {
    try {
        console.log('🎨 Initializing Two-Rule compatible visualization engine...');

        // Ensure window.sidebarVisualizationState exists (created by sidebar.js)
        if (!window.sidebarVisualizationState) {
            console.warn('⚠️ window.sidebarVisualizationState not found - waiting for sidebar.js to initialize...');
            let attempts = 0;
            while (!window.sidebarVisualizationState && attempts < 20) {
                await new Promise(resolve => setTimeout(resolve, 100));
                attempts++;
            }

            if (!window.sidebarVisualizationState) {
                console.error(' window.sidebarVisualizationState still not available after 2 seconds');
                return false;
            }
        }

        // Wait for VisualizationEngine class to be available
        let attempts = 0;
        while (!window.VisualizationEngine && attempts < 50) {
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }

        if (!window.VisualizationEngine) {
            console.error(' VisualizationEngine class not found after 5 seconds');
            console.log('🔍 Make sure visualisation_copy.js is loaded before this file');
            return false;
        }

        console.log('isualizationEngine class found, creating instance...');

        window.sidebarVisualizationState.engine = new VisualizationEngine({
            theme: document.body.getAttribute('data-theme') || 'light',
            defaultHeight: 400,
            enableInteractivity: true,
            enableExport: true,
            enableResize: true
        });

        await window.sidebarVisualizationState.engine.init();

        window.sidebarVisualizationState.isInitialized = true;
        window.sidebarVisualizationState.currentTheme = document.body.getAttribute('data-theme') || 'light';

        console.log('wo-Rule compatible visualization engine initialized successfully');
        return true;

    } catch (error) {
        console.error(' Failed to initialize visualization engine:', error);
        console.log('🔄 Will attempt to use global engines during streaming');
        return false;
    }
}

// =====================================
// LEGACY COMPATIBILITY & STUB FUNCTIONS
// (For complete compatibility with original streaming.js)
// =====================================

/**
 * EGACY STUBS: Disabled legacy functions for compatibility
 * These functions are disabled and redirect to Two-Rule system
 */
function processProgressiveUpdate(fullContent, newContent, container) {
    console.log('🚫 Legacy processProgressiveUpdate disabled - using Two-Rule system');
    return;
}

function renderProgressiveMarkdown(fullContent, container) {
    console.log('🚫 Legacy renderProgressiveMarkdown disabled - using Two-Rule system');
    return;
}

function showProgressiveRawText(fullContent, container) {
    console.log('🚫 Legacy showProgressiveRawText disabled - using Two-Rule system');
    return;
}

/**
 * EGACY TRACKING: Visualization tracking compatibility
 */
let visualizationTracker = {
    renderedVisualizations: new Map(),
    contentHashes: new Set(),
    lastScanPosition: 0,
    processingQueue: new Set(),
    lastScanTime: 0,
    scanCooldown: 100
};

function resetVisualizationTracking() {
    visualizationTracker.renderedVisualizations.clear();
    visualizationTracker.contentHashes.clear();
    visualizationTracker.lastScanPosition = 0;
    visualizationTracker.processingQueue.clear();
    visualizationTracker.lastScanTime = 0;
    resetTwoRuleSystem();
    console.log('🔄 Two-Rule visualization tracking reset');
}

/**
 * EGACY COMPATIBILITY: Stub functions for backward compatibility
 */
function checkForVisualizationStart(content, fromPosition = 0) {
    console.log('🔄 Legacy checkForVisualizationStart - redirecting to Two-Rule system');
    return null; // Two-Rule system handles this internally
}

function checkForVisualizationEnd(content) {
    console.log('🔄 Legacy checkForVisualizationEnd - redirecting to Two-Rule system');
    return null; // Two-Rule system handles this internally
}

function showVisualizationBufferingIndicator(container, type) {
    console.log('🔄 Legacy buffering indicator - handled by Two-Rule system');
    // Two-Rule system manages its own buffering indicators
}

function removeVisualizationBufferingIndicator(container) {
    console.log('🔄 Legacy buffering indicator removal - handled by Two-Rule system');
    // Two-Rule system manages its own buffering indicators
}

function updateVisualizationBufferingIndicator(container, type, bufferSize) {
    console.log('🔄 Legacy buffering indicator update - handled by Two-Rule system');
    // Two-Rule system manages its own buffering indicators
}

// =====================================
// GLOBAL EXPORTS & WINDOW OBJECT INTEGRATION
// =====================================

// Export all main streaming functions
window.processStreamResponse = processStreamResponse;
window.startStreamingMessage = startStreamingMessage;
window.updateStreamingMessageIncremental = updateStreamingMessageIncremental;
window.updateStreamingMessageTwoRule = updateStreamingMessageTwoRule;
window.finishStreamingMessage = finishStreamingMessage;
window.updateStreamingMessage = updateStreamingMessage;
// Lightweight streaming status for guards
window.isStreamingActive = function () {
    try {
        return !!(typeof streamingMessageElement !== 'undefined' && streamingMessageElement);
    } catch (_) {
        return false;
    }
};

// Export markdown rendering functions
// Respect centralized formatter if already defined to avoid collisions
if (typeof window.renderMarkdown !== 'function') {
    window.renderMarkdown = renderMarkdown;
}
if (typeof window.renderEnhancedMarkdown !== 'function') {
    window.renderEnhancedMarkdown = renderEnhancedMarkdown;
}
if (typeof window.cleanMarkdownHTML !== 'function') {
    window.cleanMarkdownHTML = postProcessMarkdownHTML;
}
if (typeof window.ensurePlotlyResponsive !== 'function') {
    window.ensurePlotlyResponsive = ensurePlotlyResponsive;
}
window.isMarkdownContent = isMarkdownContent;
window.hasVisualizationContent = hasVisualizationContent;
window.escapeHtml = escapeHtml;

// Export visualization functions
window.initializeSidebarVisualizationEngine = initializeSidebarVisualizationEngine;
window.resetVisualizationTracking = resetVisualizationTracking;

// Export Two-Rule system functions
window.TwoRuleStreamProcessor = TwoRuleStreamProcessor;
window.initializeTwoRuleProcessor = initializeTwoRuleProcessor;
window.processTwoRuleStreamingChunk = processTwoRuleStreamingChunk;
window.finalizeTwoRuleStreaming = finalizeTwoRuleStreaming;
window.resetTwoRuleSystem = resetTwoRuleSystem;

// Export legacy compatibility functions
window.processProgressiveUpdate = processProgressiveUpdate;
window.renderProgressiveMarkdown = renderProgressiveMarkdown;
window.showProgressiveRawText = showProgressiveRawText;
window.checkForVisualizationStart = checkForVisualizationStart;
window.checkForVisualizationEnd = checkForVisualizationEnd;
window.showVisualizationBufferingIndicator = showVisualizationBufferingIndicator;
window.removeVisualizationBufferingIndicator = removeVisualizationBufferingIndicator;
window.updateVisualizationBufferingIndicator = updateVisualizationBufferingIndicator;

// Export global state references
// NOTE: sidebarVisualizationState is managed by sidebar.js - we just use window.sidebarVisualizationState
window.visualizationTracker = visualizationTracker;

console.log('⚙️ Initializing Two-Rule Streaming System...');
console.log('✅ Two-Rule Streaming System loaded successfully');
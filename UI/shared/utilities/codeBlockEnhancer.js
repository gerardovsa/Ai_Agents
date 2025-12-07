/**
 * ================================================================
 * CODE BLOCK ENHANCER - Syntax Highlighting & Interactive Features
 * ================================================================
 * Enhances code blocks in markdown content with:
 * - Syntax highlighting via Prism.js
 * - Copy-to-clipboard functionality
 * - Line numbers
 * - Language detection
 * - Dark/Light theme support
 * 
 * This module works non-disruptively alongside existing markdown rendering.
 * Adapted for AI_agents from V7_MustCare implementation.
 * ================================================================
 */

class CodeBlockEnhancer {
    constructor(options = {}) {
        this.options = {
            enableSyntaxHighlighting: true,
            enableCopyButton: true,
            enableLineNumbers: false,  // Disabled by default for cleaner look
            enableLanguageDetection: true,
            ...options
        };

        this.initialized = false;
        this.processedBlocks = new WeakSet();
        this.observers = new Map();

        console.log('🔧 CodeBlockEnhancer: initialized');
    }

    /**
     * Initialize the enhancer - wait for Prism to be available
     */
    async initialize() {
        if (this.initialized) return;

        // Wait for Prism.js to be loaded
        await this.waitForPrism();

        // Setup mutation observer for dynamic content
        this.setupObserver();

        this.initialized = true;
        console.log('✅ CodeBlockEnhancer: ready');
    }

    /**
     * Wait for Prism library to be available
     */
    waitForPrism() {
        return new Promise((resolve) => {
            if (typeof Prism !== 'undefined') {
                console.log('✅ Prism.js detected and loaded');
                resolve();
                return;
            }

            // Wait up to 5 seconds for Prism to load
            let attempts = 0;
            const maxAttempts = 50;
            const checkInterval = setInterval(() => {
                attempts++;
                if (typeof Prism !== 'undefined') {
                    clearInterval(checkInterval);
                    console.log('✅ Prism.js loaded after waiting');
                    resolve();
                } else if (attempts >= maxAttempts) {
                    clearInterval(checkInterval);
                    console.warn('⚠️ Prism.js not available - code blocks will use basic styling');
                    resolve();
                }
            }, 100);
        });
    }

    /**
     * Setup mutation observer for dynamic code block detection
     */
    setupObserver() {
        if (!document.body) return;

        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.enhanceContainer(node);
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: false,
            characterData: false
        });

        console.log('🔍 CodeBlockEnhancer: mutation observer setup');
    }

    /**
     * Enhance all code blocks in a container
     */
    enhanceContainer(container) {
        if (!this.initialized) return;

        try {
            const codeBlocks = container.querySelectorAll('pre code, code');

            codeBlocks.forEach((block) => {
                // Skip if already processed
                if (this.processedBlocks.has(block)) return;

                this.enhanceCodeBlock(block);
                this.processedBlocks.add(block);
            });

            if (codeBlocks.length > 0) {
                console.log(`🎨 CodeBlockEnhancer: enhanced ${codeBlocks.length} code blocks`);
            }
        } catch (error) {
            console.error('❌ CodeBlockEnhancer.enhanceContainer failed:', error);
        }
    }

    /**
     * Enhance a single code block
     */
    enhanceCodeBlock(block) {
        try {
            // Skip inline code in flow
            if (block.parentElement?.tagName !== 'PRE') {
                return; // This is inline code, not a code block
            }

            const pre = block.parentElement;

            // Detect language
            const language = this.detectLanguage(block, pre);

            // Apply syntax highlighting
            if (this.options.enableSyntaxHighlighting && typeof Prism !== 'undefined') {
                this.applySyntaxHighlighting(block, language);
            }

            // Wrap in container for better styling
            this.wrapCodeBlock(pre);

            // Create code block header (language label + copy button)
            this.createCodeBlockHeader(pre, block, language);

            // Apply line numbers if enabled
            if (this.options.enableLineNumbers) {
                this.applyLineNumbers(block);
            }
        } catch (error) {
            console.error('❌ CodeBlockEnhancer.enhanceCodeBlock failed:', error);
        }
    }

    /**
     * Detect programming language from code block
     */
    detectLanguage(block, pre) {
        // Check class attribute
        const classMatch = block.className.match(/language-(\w+)/);
        if (classMatch) {
            return classMatch[1].toLowerCase();
        }

        // Check data attributes
        if (block.dataset.language) {
            return block.dataset.language.toLowerCase();
        }

        if (pre.dataset.language) {
            return pre.dataset.language.toLowerCase();
        }

        // Try to detect from content (simple heuristic)
        const content = block.textContent;
        if (content.includes('import ') || content.includes('def ') || content.includes('print(')) {
            return 'python';
        }
        if (content.includes('const ') || content.includes('function ') || content.includes('=>')) {
            return 'javascript';
        }
        if (content.includes('SELECT ') || content.includes('INSERT ') || content.includes('FROM ')) {
            return 'sql';
        }
        if (content.includes('<?php') || content.includes('$_GET') || content.includes('$_POST')) {
            return 'php';
        }
        if (content.includes('<html') || content.includes('<div') || content.includes('<span')) {
            return 'html';
        }

        return null;
    }

    /**
     * Apply Prism syntax highlighting
     */
    applySyntaxHighlighting(block, language) {
        try {
            if (!language) return;

            // Check if Prism is available
            if (typeof Prism === 'undefined' || !Prism.languages) {
                console.log(`ℹ️ Prism not available - skipping syntax highlighting for ${language}`);
                return;
            }

            const grammar = Prism.languages[language];
            if (grammar) {
                block.classList.add(`language-${language}`);
                const highlighted = Prism.highlight(
                    block.textContent,
                    grammar,
                    language
                );
                block.innerHTML = highlighted;
                console.log(`✅ Syntax highlighting applied: ${language}`);
            }
        } catch (error) {
            console.warn(`⚠️ Syntax highlighting failed for ${language}:`, error);
        }
    }

    /**
     * Wrap code block in enhanced container
     */
    wrapCodeBlock(pre) {
        // Check if already wrapped
        if (pre.classList.contains('code-block-enhanced')) {
            return;
        }

        pre.classList.add('code-block-enhanced');
        pre.style.position = 'relative';

        // Add theme-aware class
        if (document.documentElement.getAttribute('data-theme') === 'dark') {
            pre.classList.add('code-block-dark');
        }
    }

    /**
     * Create code block header with language label and copy button
     */
    createCodeBlockHeader(pre, block, language) {
        try {
            // Check if header already exists
            if (pre.querySelector('.code-block-header')) {
                return;
            }

            // Create header container
            const header = document.createElement('div');
            header.className = 'code-block-header';

            // Create language label (left side)
            if (language) {
                const label = document.createElement('div');
                label.className = 'code-language-label';
                label.textContent = language.toUpperCase();
                header.appendChild(label);
            } else {
                // Empty div for spacing if no language
                const spacer = document.createElement('div');
                header.appendChild(spacer);
            }

            // Create copy button (right side)
            const copyBtn = document.createElement('button');
            copyBtn.className = 'code-copy-btn';
            copyBtn.setAttribute('aria-label', 'Copy code to clipboard');
            copyBtn.setAttribute('title', 'Copy to clipboard');
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.type = 'button';

            // Get code content
            const codeContent = block.textContent;

            // Copy functionality
            copyBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();

                navigator.clipboard.writeText(codeContent).then(() => {
                    console.log('✅ Code copied to clipboard');

                    // Visual feedback
                    const originalHTML = copyBtn.innerHTML;
                    copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                    copyBtn.classList.add('copied');
                    copyBtn.setAttribute('title', 'Copied!');

                    // Reset after 2 seconds
                    setTimeout(() => {
                        copyBtn.innerHTML = originalHTML;
                        copyBtn.classList.remove('copied');
                        copyBtn.setAttribute('title', 'Copy to clipboard');
                    }, 2000);
                }).catch((error) => {
                    console.error('❌ Failed to copy code:', error);
                    const originalHTML = copyBtn.innerHTML;
                    copyBtn.innerHTML = '<i class="fas fa-exclamation"></i>';
                    copyBtn.setAttribute('title', 'Copy failed');
                    setTimeout(() => {
                        copyBtn.innerHTML = originalHTML;
                        copyBtn.setAttribute('title', 'Copy to clipboard');
                    }, 2000);
                });
            });

            header.appendChild(copyBtn);

            // Insert header at the beginning of pre element
            pre.insertBefore(header, pre.firstChild);
        } catch (error) {
            console.error('❌ CodeBlockEnhancer.createCodeBlockHeader failed:', error);
        }
    }

    /**
     * Add copy-to-clipboard button (DEPRECATED - use createCodeBlockHeader instead)
     */
    addCopyButton(pre, block) {
        // This method is kept for backwards compatibility but does nothing
        // The new createCodeBlockHeader method handles both label and button
        console.log('ℹ️ addCopyButton called but using createCodeBlockHeader instead');
    }

    /**
     * Add language label to code block (DEPRECATED - use createCodeBlockHeader instead)
     */
    addLanguageLabel(pre, language) {
        // This method is kept for backwards compatibility but does nothing
        // The new createCodeBlockHeader method handles both label and button
        console.log('ℹ️ addLanguageLabel called but using createCodeBlockHeader instead');
    }

    /**
     * Apply line numbers to code block
     */
    applyLineNumbers(block) {
        try {
            if (!block.parentElement || !block.parentElement.classList.contains('code-block-enhanced')) {
                return;
            }

            // Prism line-numbers plugin - add class to parent pre
            block.parentElement.classList.add('line-numbers');

            console.log('✅ Line numbers applied');
        } catch (error) {
            console.warn('⚠️ Failed to apply line numbers:', error);
        }
    }

    /**
     * Enhance existing content on page
     */
    enhanceExistingContent() {
        if (!this.initialized) {
            console.warn('⚠️ CodeBlockEnhancer not initialized');
            return;
        }

        this.enhanceContainer(document.body);
    }

    /**
     * Public API: Enhance content after rendering
     */
    processContent(container) {
        if (!container) return;

        // Wait for initialization if needed
        if (!this.initialized) {
            this.initialize().then(() => {
                this.enhanceContainer(container);
            });
        } else {
            this.enhanceContainer(container);
        }
    }

    /**
     * Reset and destroy
     */
    destroy() {
        try {
            this.processedBlocks = new WeakSet();
            this.observers.forEach((observer) => observer.disconnect());
            this.observers.clear();
            console.log('🧹 CodeBlockEnhancer destroyed');
        } catch (error) {
            console.error('❌ CodeBlockEnhancer.destroy failed:', error);
        }
    }
}

// Create singleton instance
const codeBlockEnhancer = new CodeBlockEnhancer();

// Auto-initialize when module loads
if (typeof window !== 'undefined') {
    // Initialize on load or after a short delay
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            codeBlockEnhancer.initialize().catch(error => {
                console.error('❌ Failed to initialize CodeBlockEnhancer:', error);
            });
        });
    } else {
        codeBlockEnhancer.initialize().catch(error => {
            console.error('❌ Failed to initialize CodeBlockEnhancer:', error);
        });
    }

    // Expose globally
    window.codeBlockEnhancer = codeBlockEnhancer;

    console.log('✅ CodeBlockEnhancer module loaded');
}

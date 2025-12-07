/**
 * Global Link Handler
 * Ensures ALL external links in the UI open in new tabs
 * 
 * Purpose:
 * - Prevents users from losing their AI session when clicking links
 * - Adds target="_blank" to all external links dynamically
 * - Works as a safety net for any links not explicitly configured
 * 
 * Usage: Automatically initialized on DOMContentLoaded
 */

(function () {
    'use strict';

    /**
     * Check if a URL is external (not same origin)
     */
    function isExternalLink(url) {
        try {
            const linkUrl = new URL(url, window.location.origin);
            return linkUrl.origin !== window.location.origin;
        } catch (e) {
            // Invalid URL or relative path
            return false;
        }
    }

    /**
     * Process a single link element
     */
    function processLink(link) {
        const href = link.getAttribute('href');

        // Skip if no href, already has target, or is a download link
        if (!href || link.hasAttribute('target') || link.hasAttribute('download')) {
            return;
        }

        // Skip internal anchors and javascript: links
        if (href.startsWith('#') || href.startsWith('javascript:')) {
            return;
        }

        // Add target="_blank" to external links
        if (isExternalLink(href)) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');

            // Optional: Add visual indicator for external links
            if (!link.classList.contains('external-link-processed')) {
                link.classList.add('external-link-processed');
            }
        }
    }

    /**
     * Process all links in a container
     */
    function processAllLinks(container = document.body) {
        const links = container.querySelectorAll('a[href]');
        links.forEach(processLink);
    }

    /**
     * Set up MutationObserver to handle dynamically added links
     */
    function setupObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                // Process newly added nodes
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // If the node itself is a link
                        if (node.tagName === 'A') {
                            processLink(node);
                        }
                        // Check for links within the added node
                        if (node.querySelectorAll) {
                            const links = node.querySelectorAll('a[href]');
                            links.forEach(processLink);
                        }
                    }
                });
            });
        });

        // Observe the entire document for changes
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        console.log('[Global Link Handler] MutationObserver initialized');
    }

    /**
     * Add click event listener as fallback
     */
    function setupClickListener() {
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href]');
            if (link) {
                const href = link.getAttribute('href');

                // Skip download links and internal links
                if (link.hasAttribute('download') || !href || href.startsWith('#') || href.startsWith('javascript:')) {
                    return;
                }

                // Force external links to open in new tab
                if (isExternalLink(href) && !link.hasAttribute('target')) {
                    e.preventDefault();
                    window.open(href, '_blank', 'noopener,noreferrer');
                    console.log('[Global Link Handler] Opened external link in new tab:', href);
                }
            }
        }, true); // Use capture phase to catch events early

        console.log('[Global Link Handler] Click listener initialized');
    }

    /**
     * Initialize the global link handler
     */
    function init() {
        // Process existing links
        processAllLinks();

        // Set up observer for dynamic content
        setupObserver();

        // Add click listener as fallback
        setupClickListener();

        console.log('[Global Link Handler] ✅ Initialized - All external links will open in new tabs');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose utility for manual processing if needed
    window.GlobalLinkHandler = {
        processLink,
        processAllLinks,
        isExternalLink
    };

})();

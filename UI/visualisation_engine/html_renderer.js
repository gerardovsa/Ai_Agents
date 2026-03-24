/**
 * HTML RENDERER MODULE
 * ====================
 * 
 * Renders interactive HTML content in sandboxed iframes.
 * Provides secure execution of HTML/CSS/JavaScript widgets.
 * 
 * Security features:
 * - Sandboxed iframe with srcdoc (no cross-origin issues)
 * - Isolated execution environment
 * - Controlled permissions via sandbox attribute
 * 
 * Supported content:
 * - Interactive HTML widgets
 * - Custom visualizations
 * - Embedded applications
 * - Form components
 */

class HTMLRenderer {
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
    }

    /**
     * Render HTML visualization
     * @param {Object} item - Visualization item with content
     * @param {HTMLElement} contentArea - Target container
     * @param {string} chartId - Unique chart identifier
     */
    async render(item, contentArea, chartId) {
        try {
            // Extract HTML content: strip outer delimiters only
            let htmlContent = item.content
                .replace(/<\/?EXECUTE_HTML>/gi, '')
                .replace(/<\/?HTML>/gi, '')
                .trim();

            // ─── AUTO-RESIZE: inject a small postMessage script so the iframe reports
            // its scrollHeight back to us without needing same-origin access.
            const resizeScript = `<script>
(function() {
    function sendHeight() {
        var h = Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0);
        window.parent.postMessage({ type: 'iframe-resize', id: '${chartId}', height: h }, '*');
    }
    window.addEventListener('load', sendHeight);
    window.addEventListener('resize', sendHeight);
    // Also fire after a short delay in case dynamic content changes height
    setTimeout(sendHeight, 300);
    setTimeout(sendHeight, 1000);
})();
<\/script>`;

            // ─── SMART WRAPPING: If the AI produced a full HTML document already,
            // inject the resize script just before </body> and use it directly.
            // NEVER double-wrap – that breaks function scoping (e.g. "randomColor is not defined").
            const isFullDocument = /^\s*<!DOCTYPE\s+html/i.test(htmlContent) || /^\s*<html[\s>]/i.test(htmlContent);

            let srcdoc;
            if (isFullDocument) {
                // Insert resize script before </body> if present, otherwise append
                if (/<\/body>/i.test(htmlContent)) {
                    srcdoc = htmlContent.replace(/<\/body>/i, `${resizeScript}</body>`);
                } else {
                    srcdoc = htmlContent + resizeScript;
                }
            } else {
                // Partial HTML: wrap it properly
                srcdoc = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: auto; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; padding: 1rem; box-sizing: border-box; }
        * { box-sizing: border-box; }
    </style>
</head>
<body>
${htmlContent}
${resizeScript}
</body>
</html>`;
            }

            const iframe = document.createElement('iframe');
            iframe.id = chartId;

            // ─── SECURITY: No allow-same-origin — prevents iframe JS from
            // accessing window.parent.document and mutating the parent UI.
            // allow-scripts alone is sufficient for interactive widgets.
            iframe.sandbox = 'allow-scripts allow-forms allow-modals allow-pointer-lock';

            // ─── PERMISSIONS: allow clipboard-write so copy-to-clipboard buttons
            // inside generated HTML work (Clipboard API is blocked by sandbox by default).
            iframe.allow = 'clipboard-write';

            iframe.style.cssText = `
                width: 100%;
                height: 400px;
                min-height: 200px;
                border: 1px solid var(--border-color, #444);
                border-radius: 8px;
                background: white;
                display: block;
                transition: height 0.2s ease;
            `;

            iframe.srcdoc = srcdoc;

            // ─── AUTO-RESIZE via postMessage (works without same-origin)
            const onMessage = (event) => {
                if (event.data && event.data.type === 'iframe-resize' && event.data.id === chartId) {
                    const newHeight = Math.min(Math.max(event.data.height + 24, 200), 900);
                    iframe.style.height = `${newHeight}px`;
                }
            };
            window.addEventListener('message', onMessage);

            // Cleanup listener when iframe is removed from DOM
            const observer = new MutationObserver(() => {
                if (!document.contains(iframe)) {
                    window.removeEventListener('message', onMessage);
                    observer.disconnect();
                }
            });
            observer.observe(document.body, { childList: true, subtree: true });

            contentArea.appendChild(iframe);

            console.log('✅ HTML rendered successfully in sandboxed iframe (isolated)');
        } catch (error) {
            console.error('Error rendering HTML:', error);
            throw error;
        }
    }
}

// Export for use in visualization engine
if (typeof window !== 'undefined') {
    window.HTMLRenderer = HTMLRenderer;
}

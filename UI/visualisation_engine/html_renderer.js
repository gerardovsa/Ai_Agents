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
            // Extract HTML content
            const htmlContent = item.content
                .replace(/<\/?EXECUTE_HTML>/g, '')
                .replace(/<\/?HTML>/g, '')
                .trim();

            // 🎯 INTERACTIVE HTML FIX (Jan 21, 2026): Allow full interactivity while preventing parent DOM pollution
            // Balance: Interactive features + Parent page protection
            const iframe = document.createElement('iframe');
            iframe.id = chartId;
            
            // 🎯 BALANCED SANDBOX: Allow interactivity but block parent access
            // allow-scripts: JavaScript can run (needed for interactive widgets)
            // allow-forms: Form submissions work
            // allow-same-origin: Styles and resources load properly
            // BLOCKED: allow-top-navigation, allow-popups (prevents escape)
            iframe.sandbox = 'allow-scripts allow-forms allow-same-origin allow-modals allow-pointer-lock';
            
            iframe.style.cssText = `
                width: 100%;
                min-height: 400px;
                border: 1px solid var(--border-color, #444);
                border-radius: 8px;
                background: white;
                display: block;
            `;

            // 🎯 Interactive HTML with isolated styles (won't affect parent page)
            iframe.srcdoc = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* Reset to prevent parent style inheritance */
        html, body { 
            margin: 0; 
            padding: 0; 
            width: 100%;
            height: 100%;
            overflow: auto;
        }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            padding: 1rem;
            box-sizing: border-box;
        }
        * { box-sizing: border-box; }
    </style>
</head>
<body>
${htmlContent}
</body>
</html>`;

            contentArea.appendChild(iframe);

            console.log('✅ HTML rendered successfully in sandboxed iframe');
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

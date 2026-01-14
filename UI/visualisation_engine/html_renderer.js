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

            // Create sandboxed iframe with srcdoc (SECURE - no same-origin to prevent escape)
            const iframe = document.createElement('iframe');
            iframe.id = chartId;
            iframe.sandbox = 'allow-scripts';
            iframe.style.cssText = `
                width: 100%;
                min-height: 400px;
                border: 1px solid #444;
                border-radius: 8px;
                background: white;
            `;

            // Use srcdoc to avoid cross-origin errors
            iframe.srcdoc = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, sans-serif; padding: 1rem; }
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

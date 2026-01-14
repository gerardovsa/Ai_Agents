/**
 * SVG RENDERER MODULE
 * ===================
 * 
 * Renders SVG-based visualizations including molecular structures,
 * technical drawings, diagrams, and custom SVG graphics.
 * 
 * Supported types:
 * - SVG (generic SVG visualization)
 * - Molecule structures (chemical diagrams)
 * 
 * Handles:
 * - Responsive scaling
 * - Container sizing
 * - SVG optimization
 */

class SVGRenderer {
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
    }

    /**
     * Render SVG visualization
     * @param {Object} item - Visualization item with content
     * @param {HTMLElement} contentArea - Target container
     * @param {string} chartId - Unique chart identifier
     */
    async render(item, contentArea, chartId) {
        try {
            // Extract SVG content
            const svgContent = item.content
                .replace(/<\/?MOLECULE>/g, '')
                .replace(/<\/?SVG_VISUAL>/g, '')
                .trim();

            // Create container
            const svgContainer = document.createElement('div');
            svgContainer.id = chartId;
            svgContainer.style.cssText = `
                width: 100%;
                min-height: 400px;
                height: auto;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
                overflow: visible;
            `;
            svgContainer.innerHTML = svgContent;

            // Ensure SVG scales properly
            const svg = svgContainer.querySelector('svg');
            if (svg) {
                svg.style.cssText = `
                    max-width: 100%;
                    height: auto;
                    display: block;
                `;
            }

            contentArea.appendChild(svgContainer);
            console.log(`✅ ${item.type.toUpperCase()} rendered successfully`);
        } catch (error) {
            console.error(`Error rendering ${item.type}:`, error);
            throw error;
        }
    }
}

// Export for use in visualization engine
if (typeof window !== 'undefined') {
    window.SVGRenderer = SVGRenderer;
}

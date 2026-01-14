/**
 * LATEX RENDERER MODULE
 * ======================
 * 
 * Renders LaTeX mathematical equations using KaTeX.
 * KaTeX is a fast, easy-to-use JavaScript library for TeX math rendering.
 * 
 * Supported features:
 * - Display mode equations
 * - Inline equations
 * - Complex mathematical notation
 * - Chemical formulas (with mhchem extension)
 * 
 * CDN: https://cdn.jsdelivr.net/npm/katex@0.16.9
 * Docs: https://katex.org/
 */

class LatexRenderer {
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
    }

    /**
     * Render LaTeX visualization
     * @param {Object} item - Visualization item with content
     * @param {HTMLElement} contentArea - Target container
     * @param {string} chartId - Unique chart identifier
     */
    async render(item, contentArea, chartId) {
        try {
            // Ensure KaTeX is loaded
            if (!window.katex) {
                await this.loadKaTeX();
            }

            // Extract LaTeX content
            const latexContent = item.content
                .replace(/<\/?LATEX>/g, '')
                .trim();

            // Create container
            const latexContainer = document.createElement('div');
            latexContainer.id = chartId;
            latexContainer.style.cssText = `
                width: 100%;
                padding: 20px;
                font-size: 1.2em;
                text-align: center;
            `;

            // Render using KaTeX
            window.katex.render(latexContent, latexContainer, {
                throwOnError: false,
                displayMode: true
            });

            contentArea.appendChild(latexContainer);
            console.log('✅ LATEX rendered successfully');
        } catch (error) {
            console.error('Error rendering latex:', error);
            throw error;
        }
    }

    /**
     * Load KaTeX library dynamically
     */
    async loadKaTeX() {
        return new Promise((resolve, reject) => {
            if (window.katex) {
                resolve();
                return;
            }

            // Load CSS
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css';
            document.head.appendChild(link);

            // Load JavaScript
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js';
            script.onload = () => {
                console.log('✅ KaTeX library loaded');
                resolve();
            };
            script.onerror = () => reject(new Error('Failed to load KaTeX library'));
            document.head.appendChild(script);
        });
    }
}

// Export for use in visualization engine
if (typeof window !== 'undefined') {
    window.LatexRenderer = LatexRenderer;
}

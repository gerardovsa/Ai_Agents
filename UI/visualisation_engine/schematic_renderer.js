/**
 * SCHEMATIC RENDERER MODULE
 * =========================
 * 
 * Renders technical schematics and circuit diagrams.
 * Uses SVG for crisp, scalable technical drawings.
 * 
 * Supported diagram types:
 * - Electrical circuits
 * - System architecture diagrams
 * - Network topology
 * - Process flow diagrams
 * 
 * Built on native SVG - no external dependencies
 */

class SchematicRenderer {
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
        this.schematics = new Map(); // Track schematic instances
    }

    /**
     * Render schematic diagram
     * @param {Object} item - Visualization item with content
     * @param {HTMLElement} contentArea - Target container
     * @param {string} chartId - Unique chart identifier
     */
    async render(item, contentArea, chartId) {
        // DOM validation
        if (!contentArea || !document.contains(contentArea)) {
            throw new Error('Schematic: Invalid content area');
        }

        // Parse configuration - handle both SVG markup and JSON
        let config;
        if (typeof item.content === 'string') {
            const cleanContent = item.content.replace(/<\/?SCHEMATIC>/g, '').trim();

            // Check if content is SVG markup
            if (cleanContent.startsWith('<svg') || cleanContent.startsWith('<?xml')) {
                // It's SVG markup - render directly like CAD
                return this.renderSVGSchematic(cleanContent, contentArea, chartId);
            } else {
                // It's JSON config
                try {
                    config = JSON.parse(cleanContent);
                } catch (e) {
                    console.error('Schematic: JSON parse failed', e);
                    throw new Error(`Invalid schematic config: ${e.message}`);
                }
            }
        } else {
            config = item.content;
        }

        // Create container
        const schematicContainer = document.createElement('div');
        schematicContainer.id = chartId;
        schematicContainer.className = 'schematic-diagram-container';
        schematicContainer.style.cssText = `
            width: 100%;
            min-height: ${config.height || 600}px;
            position: relative;
            background: ${config.background || '#ffffff'};
            padding: 20px;
            box-sizing: border-box;
        `;

        contentArea.appendChild(schematicContainer);

        // Create SVG
        const svg = this.createSVG(schematicContainer, config);

        // Render schematic elements
        await this.renderElements(svg, config);

        // Store instance
        this.schematics.set(chartId, { container: schematicContainer, svg, config });

        // Add action bar
        const vizContainer = contentArea.closest('.viz-container');
        if (vizContainer && this.vizEngine?.addUnifiedActionBar) {
            this.vizEngine.addUnifiedActionBar(vizContainer, item, chartId, 'schematic');
            this.addSchematicControls(vizContainer, chartId);
        }

        return svg;
    }

    /**
     * Create SVG element
     */
    createSVG(container, config) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', config.height || 600);
        svg.setAttribute('viewBox', config.viewBox || `0 0 ${config.width || 800} ${config.height || 600}`);
        svg.style.cssText = 'display: block; margin: 0 auto;';

        // Add definitions for reusable elements
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        this.addCommonDefs(defs, config);
        svg.appendChild(defs);

        container.appendChild(svg);
        return svg;
    }

    /**
     * Add common definitions (markers, patterns, etc.)
     */
    addCommonDefs(defs, config) {
        // Get dynamic theme colors
        const colors = window.ThemeDetector ? window.ThemeDetector.getColors() : null;
        const strokeColor = colors ? colors.text : '#24292f';
        const isDark = window.ThemeDetector ? window.ThemeDetector.isDark() : (config.theme === 'dark');

        // Arrow marker
        const arrowMarker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        arrowMarker.setAttribute('id', 'arrow');
        arrowMarker.setAttribute('viewBox', '0 0 10 10');
        arrowMarker.setAttribute('refX', '5');
        arrowMarker.setAttribute('refY', '5');
        arrowMarker.setAttribute('markerWidth', '6');
        arrowMarker.setAttribute('markerHeight', '6');
        arrowMarker.setAttribute('orient', 'auto-start-reverse');

        const arrowPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        arrowPath.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
        arrowPath.setAttribute('fill', strokeColor);
        arrowMarker.appendChild(arrowPath);
        defs.appendChild(arrowMarker);

        // Grid pattern
        const gridPattern = document.createElementNS('http://www.w3.org/2000/svg', 'pattern');
        gridPattern.setAttribute('id', 'grid');
        gridPattern.setAttribute('width', '20');
        gridPattern.setAttribute('height', '20');
        gridPattern.setAttribute('patternUnits', 'userSpaceOnUse');

        const gridPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        gridPath.setAttribute('d', 'M 20 0 L 0 0 0 20');
        gridPath.setAttribute('fill', 'none');
        gridPath.setAttribute('stroke', colors ? colors.border : '#d0d7de');
        gridPath.setAttribute('stroke-width', '0.5');
        gridPattern.appendChild(gridPath);
        defs.appendChild(gridPattern);
    }

    /**
     * Render schematic elements
     */
    async renderElements(svg, config) {
        // Get dynamic theme colors
        const colors = window.ThemeDetector ? window.ThemeDetector.getColors() : null;
        const strokeColor = colors ? colors.text : '#24292f';
        const fillColor = colors ? colors.background : '#ffffff';

        // Show grid if enabled
        if (config.showGrid !== false) {
            const gridRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            gridRect.setAttribute('width', '100%');
            gridRect.setAttribute('height', '100%');
            gridRect.setAttribute('fill', 'url(#grid)');
            svg.appendChild(gridRect);
        }

        // Render elements from config
        if (config.elements && Array.isArray(config.elements)) {
            for (const element of config.elements) {
                await this.renderElement(svg, element, strokeColor, fillColor);
            }
        }

        // Render connections
        if (config.connections && Array.isArray(config.connections)) {
            for (const connection of config.connections) {
                this.renderConnection(svg, connection, strokeColor);
            }
        }

        // Add labels
        if (config.labels && Array.isArray(config.labels)) {
            for (const label of config.labels) {
                this.renderLabel(svg, label, strokeColor);
            }
        }
    }

    /**
     * Render individual schematic element
     */
    async renderElement(svg, element, strokeColor, fillColor) {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('transform', `translate(${element.x || 0}, ${element.y || 0})`);

        switch (element.type) {
            case 'resistor':
                this.drawResistor(group, element, strokeColor);
                break;
            case 'capacitor':
                this.drawCapacitor(group, element, strokeColor);
                break;
            case 'battery':
                this.drawBattery(group, element, strokeColor);
                break;
            case 'box':
                this.drawBox(group, element, strokeColor, fillColor);
                break;
            case 'circle':
                this.drawCircle(group, element, strokeColor, fillColor);
                break;
            default:
                console.warn(`Unknown schematic element type: ${element.type}`);
        }

        svg.appendChild(group);
    }

    /**
     * Draw resistor symbol
     */
    drawResistor(group, element, strokeColor) {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', 'M 0 0 L 10 0 L 15 -10 L 25 10 L 35 -10 L 45 10 L 55 -10 L 65 10 L 70 0 L 80 0');
        path.setAttribute('stroke', strokeColor);
        path.setAttribute('stroke-width', element.strokeWidth || 2);
        path.setAttribute('fill', 'none');
        group.appendChild(path);
    }

    /**
     * Draw capacitor symbol
     */
    drawCapacitor(group, element, strokeColor) {
        const line1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line1.setAttribute('x1', '0');
        line1.setAttribute('y1', '0');
        line1.setAttribute('x2', '35');
        line1.setAttribute('y2', '0');
        line1.setAttribute('stroke', strokeColor);
        line1.setAttribute('stroke-width', element.strokeWidth || 2);
        group.appendChild(line1);

        const line2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line2.setAttribute('x1', '35');
        line2.setAttribute('y1', '-15');
        line2.setAttribute('x2', '35');
        line2.setAttribute('y2', '15');
        line2.setAttribute('stroke', strokeColor);
        line2.setAttribute('stroke-width', element.strokeWidth || 2);
        group.appendChild(line2);

        const line3 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line3.setAttribute('x1', '45');
        line3.setAttribute('y1', '-15');
        line3.setAttribute('x2', '45');
        line3.setAttribute('y2', '15');
        line3.setAttribute('stroke', strokeColor);
        line3.setAttribute('stroke-width', element.strokeWidth || 2);
        group.appendChild(line3);

        const line4 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line4.setAttribute('x1', '45');
        line4.setAttribute('y1', '0');
        line4.setAttribute('x2', '80');
        line4.setAttribute('y2', '0');
        line4.setAttribute('stroke', strokeColor);
        line4.setAttribute('stroke-width', element.strokeWidth || 2);
        group.appendChild(line4);
    }

    /**
     * Draw battery symbol
     */
    drawBattery(group, element, strokeColor) {
        // Positive terminal (longer line)
        const pos = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        pos.setAttribute('x1', '0');
        pos.setAttribute('y1', '-15');
        pos.setAttribute('x2', '0');
        pos.setAttribute('y2', '15');
        pos.setAttribute('stroke', strokeColor);
        pos.setAttribute('stroke-width', element.strokeWidth || 3);
        group.appendChild(pos);

        // Negative terminal (shorter line)
        const neg = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        neg.setAttribute('x1', '20');
        neg.setAttribute('y1', '-10');
        neg.setAttribute('x2', '20');
        neg.setAttribute('y2', '10');
        neg.setAttribute('stroke', strokeColor);
        neg.setAttribute('stroke-width', element.strokeWidth || 3);
        group.appendChild(neg);
    }

    /**
     * Draw box
     */
    drawBox(group, element, strokeColor, fillColor) {
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('width', element.width || 100);
        rect.setAttribute('height', element.height || 60);
        rect.setAttribute('stroke', strokeColor);
        rect.setAttribute('stroke-width', element.strokeWidth || 2);
        rect.setAttribute('fill', element.fill || fillColor);
        rect.setAttribute('rx', element.rx || 5);
        group.appendChild(rect);

        // Add text if provided
        if (element.text) {
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', (element.width || 100) / 2);
            text.setAttribute('y', (element.height || 60) / 2);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('dominant-baseline', 'middle');
            text.setAttribute('fill', strokeColor);
            text.setAttribute('font-size', element.fontSize || 14);
            text.textContent = element.text;
            group.appendChild(text);
        }
    }

    /**
     * Draw circle
     */
    drawCircle(group, element, strokeColor, fillColor) {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('r', element.radius || 30);
        circle.setAttribute('stroke', strokeColor);
        circle.setAttribute('stroke-width', element.strokeWidth || 2);
        circle.setAttribute('fill', element.fill || fillColor);
        group.appendChild(circle);
    }

    /**
     * Render connection line
     */
    renderConnection(svg, connection, strokeColor) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', connection.x1);
        line.setAttribute('y1', connection.y1);
        line.setAttribute('x2', connection.x2);
        line.setAttribute('y2', connection.y2);
        line.setAttribute('stroke', strokeColor);
        line.setAttribute('stroke-width', connection.strokeWidth || 2);

        if (connection.arrow) {
            line.setAttribute('marker-end', 'url(#arrow)');
        }

        if (connection.dashed) {
            line.setAttribute('stroke-dasharray', '5,5');
        }

        svg.appendChild(line);
    }

    /**
     * Render label
     */
    renderLabel(svg, label, strokeColor) {
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', label.x);
        text.setAttribute('y', label.y);
        text.setAttribute('fill', strokeColor);
        text.setAttribute('font-size', label.fontSize || 12);
        text.setAttribute('font-family', 'monospace');
        text.textContent = label.text;
        svg.appendChild(text);
    }

    /**
     * Add schematic-specific controls
     */
    addSchematicControls(vizContainer, chartId) {
        const actionBar = vizContainer.querySelector('.viz-unified-action-bar');
        if (!actionBar) return;

        // Zoom controls can be added here if needed
        // For now, SVG handles zoom via viewBox manipulation
    }

    /**
     * Destroy schematic and cleanup
     */
    destroy(chartId) {
        const schematic = this.schematics.get(chartId);
        if (schematic) {
            schematic.container.remove();
            this.schematics.delete(chartId);
        }
    }

    /**
     * Render SVG schematic directly (for SVG markup input)
     */
    renderSVGSchematic(svgContent, contentArea, chartId) {
        // Create container
        const svgContainer = document.createElement('div');
        svgContainer.id = chartId;
        svgContainer.className = 'schematic-svg-container';
        svgContainer.style.cssText = `
            width: 100%;
            max-width: 100%;
            min-height: 400px;
            overflow: auto;
            background: #ffffff;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 0;
            box-sizing: border-box;
        `;

        console.log('✅ Schematic: Rendering SVG drawing:', chartId);

        // Insert SVG content
        try {
            svgContainer.innerHTML = svgContent;
            console.log('✅ Schematic: SVG content inserted');
        } catch (error) {
            console.error('❌ Schematic: Failed to insert SVG:', error);
            svgContainer.innerHTML = '<div style="padding: 20px; color: red;">Error: Failed to render schematic</div>';
        }

        // Make SVG responsive
        const svgElement = svgContainer.querySelector('svg');
        if (svgElement) {
            if (!svgElement.hasAttribute('width')) {
                svgElement.style.width = '100%';
                svgElement.style.height = 'auto';
            }
            console.log('✅ Schematic: SVG element styled');
        }

        contentArea.appendChild(svgContainer);

        // Add action bar
        const vizContainer = contentArea.closest('.viz-container');
        if (vizContainer && this.vizEngine?.addUnifiedActionBar) {
            this.vizEngine.addUnifiedActionBar(vizContainer, { content: svgContent }, chartId, 'schematic');
        }

        return { container: svgContainer, svg: svgElement };
    }

    /**
     * Destroy all schematics
     */
    destroyAll() {
        this.schematics.forEach((schematic, chartId) => {
            schematic.container.remove();
        });
        this.schematics.clear();
    }
}

// Export for use in visualization engine
if (typeof window !== 'undefined') {
    window.SchematicRenderer = SchematicRenderer;
}

/**
 * =============================================================================
 * SVG & CAD RENDERING ENHANCEMENT
 * =============================================================================
 * Purpose: Extend Two-Rule streaming system to support inline SVG rendering
 * Date: December 5, 2025
 * Author: AI Infrastructure Team
 * 
 * This module adds SVG, CAD, schematic, and LaTeX rendering capabilities to
 * the existing visualization engine without breaking current Plotly/Mermaid support.
 * 
 * Integration: Merge these methods into streamingTwoRule.js class
 * =============================================================================
 */

/**
 * =====================================================================
 * SECTION 1: ENHANCED DELIMITER SYSTEM
 * =====================================================================
 */

/**
 * Get start delimiter for visualization type (ENHANCED VERSION)
 */
getStartDelimiterEnhanced(type) {
    const delimiters = {
        // Existing
        'mermaid': '<MERMAID>',
        'plotly': '<PLOTLY>',
        'google': '<GRAPH>',
        'chartjs': '<CHARTJS>',
        
        // ✨ NEW: Technical Drawing & CAD
        'svg': '<SVG>',
        'cad': '<CAD>',
        'schematic': '<SCHEMATIC>',
        'diagram': '<DIAGRAM>',
        
        // ✨ NEW: Scientific & Mathematical
        'latex': '<LATEX>',
        'math': '<MATH>',
        'molecule': '<MOLECULE>',
        
        // ✨ NEW: Professional Diagrams
        'flowchart': '<FLOWCHART>',
        'uml': '<UML>',
        'gantt': '<GANTT>',
        'sequence': '<SEQUENCE>',
        
        // ✨ NEW: 3D & Spatial
        'threed': '<3D>',
        'map': '<MAP>',
        'blueprint': '<BLUEPRINT>'
    };
    return delimiters[type.toLowerCase()] || '';
}

/**
 * Get end delimiter for visualization type (ENHANCED VERSION)
 */
getEndDelimiterEnhanced(type) {
    const delimiters = {
        // Existing
        'mermaid': '</MERMAID>',
        'plotly': '</PLOTLY>',
        'google': '</GRAPH>',
        'chartjs': '</CHARTJS>',
        
        // ✨ NEW: Technical Drawing & CAD
        'svg': '</SVG>',
        'cad': '</CAD>',
        'schematic': '</SCHEMATIC>',
        'diagram': '</DIAGRAM>',
        
        // ✨ NEW: Scientific & Mathematical
        'latex': '</LATEX>',
        'math': '</MATH>',
        'molecule': '</MOLECULE>',
        
        // ✨ NEW: Professional Diagrams
        'flowchart': '</FLOWCHART>',
        'uml': '</UML>',
        'gantt': '</GANTT>',
        'sequence': '</SEQUENCE>',
        
        // ✨ NEW: 3D & Spatial
        'threed': '</3D>',
        'map': '</MAP>',
        'blueprint': '</BLUEPRINT>'
    };
    return delimiters[type.toLowerCase()] || '';
}

/**
 * Check for visualization start delimiter (ENHANCED VERSION)
 * Supports all new visualization types
 */
checkForVisualizationStartEnhanced(text) {
    const types = [
        // Priority order: check most specific first
        'schematic', 'blueprint', 'diagram', 'cad', 'svg',
        'molecule', 'latex', 'math',
        'flowchart', 'sequence', 'gantt', 'uml',
        'threed', 'map',
        'plotly', 'mermaid', 'google', 'chartjs'
    ];
    
    for (const type of types) {
        const delimiter = this.getStartDelimiterEnhanced(type);
        if (delimiter) {
            const index = text.indexOf(delimiter);
            if (index !== -1) {
                return { type, index, delimiter };
            }
        }
    }
    
    return null;
}

/**
 * =====================================================================
 * SECTION 2: SVG RENDERING ENGINE
 * =====================================================================
 */

/**
 * Main SVG rendering dispatcher
 * Routes different visualization types to appropriate handlers
 */
async renderVisualizationEnhanced(type, content, container) {
    try {
        console.log(`📊 TWO-RULE: Rendering ${type} visualization`);
        
        const typeMap = {
            // Existing handlers
            'plotly': () => this.visualizationEngine.renderPlotly(content, container),
            'mermaid': () => this.visualizationEngine.renderMermaid(content, container),
            
            // ✨ NEW: SVG-based rendering
            'svg': () => this.renderSVGContent(content, container, 'svg'),
            'cad': () => this.renderSVGContent(content, container, 'cad'),
            'schematic': () => this.renderSVGContent(content, container, 'schematic'),
            'diagram': () => this.renderSVGContent(content, container, 'diagram'),
            'blueprint': () => this.renderSVGContent(content, container, 'blueprint'),
            'molecule': () => this.renderSVGContent(content, container, 'molecule'),
            
            // ✨ NEW: Mathematical rendering
            'latex': () => this.renderLatex(content, container),
            'math': () => this.renderLatex(content, container),
            
            // ✨ NEW: Mermaid alternatives
            'flowchart': () => this.renderFlowchart(content, container),
            'sequence': () => this.renderSequence(content, container),
            'gantt': () => this.renderGantt(content, container),
            'uml': () => this.renderUML(content, container),
            
            // Future: 3D rendering
            'threed': () => this.render3D(content, container),
            'map': () => this.renderMap(content, container)
        };
        
        const handler = typeMap[type.toLowerCase()];
        if (handler) {
            await handler();
        } else {
            console.warn(`⚠️ Unknown visualization type: ${type}`);
            container.innerHTML = `<pre class="unknown-viz-type">${this.escapeHtml(content)}</pre>`;
        }
        
        console.log(`✅ TWO-RULE: ${type} rendered successfully`);
    } catch (error) {
        console.error(`❌ TWO-RULE: Error rendering ${type}:`, error);
        this.handleVisualizationError(error, container, type);
    }
}

/**
 * =====================================================================
 * SECTION 3: SVG CONTENT RENDERER
 * =====================================================================
 */

/**
 * Render inline SVG content with safety and styling
 * @param {string} svgCode - Raw SVG markup
 * @param {HTMLElement} container - Target container
 * @param {string} type - Visualization type (svg, cad, schematic, etc.)
 */
async renderSVGContent(svgCode, container, type) {
    console.log(`🎨 Rendering ${type} SVG content`);
    
    // Step 1: Sanitize SVG to prevent XSS
    const sanitizedSVG = this.sanitizeSVG(svgCode);
    
    // Step 2: Create styled wrapper
    const wrapper = document.createElement('div');
    wrapper.className = `visualization-svg-container ${type}-diagram`;
    wrapper.setAttribute('data-viz-type', type);
    wrapper.style.cssText = this.getSVGContainerStyles(type);
    
    // Step 3: Insert SVG content
    wrapper.innerHTML = sanitizedSVG;
    
    // Step 4: Enhance SVG element
    const svgElement = wrapper.querySelector('svg');
    if (svgElement) {
        this.enhanceSVGElement(svgElement, type);
    }
    
    // Step 5: Add controls and metadata
    this.addSVGControls(wrapper, sanitizedSVG, type);
    this.addSVGMetadata(wrapper, svgElement, type);
    
    // Step 6: Apply professional styling
    this.applySVGTheming(wrapper, type);
    
    // Step 7: Append to container
    container.appendChild(wrapper);
    
    // Step 8: Post-render enhancements
    this.enableSVGInteractivity(wrapper, type);
    
    console.log(`✅ ${type} SVG rendered with ${svgElement ? svgElement.children.length : 0} elements`);
}

/**
 * =====================================================================
 * SECTION 4: SVG SECURITY & SANITIZATION
 * =====================================================================
 */

/**
 * Sanitize SVG to prevent XSS attacks while preserving functionality
 * @param {string} svgCode - Raw SVG markup
 * @returns {string} - Sanitized SVG
 */
sanitizeSVG(svgCode) {
    console.log('🔒 Sanitizing SVG content');
    
    // Dangerous elements that should be removed
    const dangerousElements = [
        'script', 'iframe', 'object', 'embed', 'link', 'style[^>]*javascript'
    ];
    
    // Dangerous attributes that should be removed
    const dangerousAttrs = [
        'onload', 'onerror', 'onclick', 'onmouseover', 'onmouseout',
        'onmousemove', 'onmousedown', 'onmouseup', 'ondblclick',
        'onkeydown', 'onkeyup', 'onkeypress', 'onfocus', 'onblur',
        'onchange', 'onsubmit', 'onreset', 'onselect', 'oninput'
    ];
    
    let cleaned = svgCode;
    
    // Remove dangerous elements
    dangerousElements.forEach(tag => {
        const regex = new RegExp(`<${tag}[^>]*>.*?</${tag}>`, 'gi');
        cleaned = cleaned.replace(regex, '');
        const selfClosing = new RegExp(`<${tag}[^>]*/?>`, 'gi');
        cleaned = cleaned.replace(selfClosing, '');
    });
    
    // Remove dangerous attributes
    dangerousAttrs.forEach(attr => {
        const regex = new RegExp(`\\s${attr}\\s*=\\s*["'][^"']*["']`, 'gi');
        cleaned = cleaned.replace(regex, '');
    });
    
    // Remove javascript: protocol in href/xlink:href
    cleaned = cleaned.replace(/href\s*=\s*["']javascript:[^"']*["']/gi, '');
    cleaned = cleaned.replace(/xlink:href\s*=\s*["']javascript:[^"']*["']/gi, '');
    
    // Ensure proper SVG wrapper if missing
    if (!cleaned.trim().toLowerCase().startsWith('<svg')) {
        console.warn('⚠️ SVG missing root element, wrapping...');
        cleaned = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">${cleaned}</svg>`;
    }
    
    // Validate XML structure
    try {
        const parser = new DOMParser();
        const doc = parser.parseFromString(cleaned, 'image/svg+xml');
        const parserError = doc.querySelector('parsererror');
        if (parserError) {
            console.error('❌ SVG parsing error:', parserError.textContent);
            throw new Error('Invalid SVG XML structure');
        }
    } catch (error) {
        console.error('❌ SVG validation failed:', error);
        return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
            <rect width="100%" height="100%" fill="#fee"/>
            <text x="200" y="100" text-anchor="middle" fill="#c00" font-size="14">
                Invalid SVG: ${this.escapeHtml(error.message)}
            </text>
        </svg>`;
    }
    
    console.log('✅ SVG sanitized successfully');
    return cleaned;
}

/**
 * =====================================================================
 * SECTION 5: SVG ENHANCEMENT & RESPONSIVENESS
 * =====================================================================
 */

/**
 * Enhance SVG element with responsive behavior and accessibility
 * @param {SVGElement} svgElement - The SVG DOM element
 * @param {string} type - Visualization type
 */
enhanceSVGElement(svgElement, type) {
    // Ensure viewBox for responsiveness
    if (!svgElement.hasAttribute('viewBox')) {
        const width = svgElement.getAttribute('width') || '800';
        const height = svgElement.getAttribute('height') || '600';
        const vbWidth = parseFloat(width);
        const vbHeight = parseFloat(height);
        svgElement.setAttribute('viewBox', `0 0 ${vbWidth} ${vbHeight}`);
        console.log(`📐 Auto-generated viewBox: 0 0 ${vbWidth} ${vbHeight}`);
    }
    
    // Remove fixed dimensions to allow scaling
    svgElement.removeAttribute('width');
    svgElement.removeAttribute('height');
    
    // Add responsive styling
    svgElement.style.cssText = `
        max-width: 100%;
        height: auto;
        display: block;
        margin: 0 auto;
    `;
    
    // Ensure namespace
    if (!svgElement.getAttribute('xmlns')) {
        svgElement.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    }
    
    // Add ARIA attributes for accessibility
    if (!svgElement.getAttribute('role')) {
        svgElement.setAttribute('role', 'img');
    }
    if (!svgElement.getAttribute('aria-label')) {
        const title = svgElement.querySelector('title');
        if (title) {
            svgElement.setAttribute('aria-label', title.textContent);
        } else {
            svgElement.setAttribute('aria-label', `${type} diagram`);
        }
    }
    
    // Add data attributes for tracking
    svgElement.setAttribute('data-viz-type', type);
    svgElement.setAttribute('data-render-timestamp', Date.now());
    
    console.log('✨ SVG element enhanced with responsive and a11y features');
}

/**
 * =====================================================================
 * SECTION 6: SVG CONTROLS & EXPORT
 * =====================================================================
 */

/**
 * Add control buttons for SVG manipulation
 * @param {HTMLElement} wrapper - Container element
 * @param {string} svgContent - Raw SVG content
 * @param {string} type - Visualization type
 */
addSVGControls(wrapper, svgContent, type) {
    const controlBar = document.createElement('div');
    controlBar.className = 'svg-control-bar';
    controlBar.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        display: flex;
        gap: 0.5rem;
        z-index: 10;
    `;
    
    // Export button
    const exportBtn = this.createControlButton('📥', 'Download SVG', () => {
        this.exportSVG(svgContent, type);
    });
    controlBar.appendChild(exportBtn);
    
    // Copy button
    const copyBtn = this.createControlButton('📋', 'Copy SVG Code', () => {
        this.copySVGCode(svgContent);
    });
    controlBar.appendChild(copyBtn);
    
    // Zoom button
    const zoomBtn = this.createControlButton('🔍', 'Toggle Zoom', () => {
        this.toggleSVGZoom(wrapper);
    });
    controlBar.appendChild(zoomBtn);
    
    // Info button
    const infoBtn = this.createControlButton('ℹ️', 'Show Info', () => {
        this.showSVGInfo(wrapper);
    });
    controlBar.appendChild(infoBtn);
    
    wrapper.style.position = 'relative';
    wrapper.appendChild(controlBar);
}

/**
 * Create a control button
 */
createControlButton(icon, title, onClick) {
    const btn = document.createElement('button');
    btn.className = 'svg-control-btn';
    btn.innerHTML = icon;
    btn.title = title;
    btn.style.cssText = `
        padding: 0.5rem;
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #ddd;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    `;
    btn.addEventListener('click', onClick);
    btn.addEventListener('mouseenter', () => {
        btn.style.background = '#4CAF50';
        btn.style.transform = 'scale(1.1)';
        btn.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
    });
    btn.addEventListener('mouseleave', () => {
        btn.style.background = 'rgba(255, 255, 255, 0.95)';
        btn.style.transform = 'scale(1)';
        btn.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    });
    return btn;
}

/**
 * Export SVG to file
 */
exportSVG(svgContent, type) {
    try {
        const blob = new Blob([svgContent], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}-diagram-${Date.now()}.svg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        console.log('✅ SVG exported successfully');
    } catch (error) {
        console.error('❌ SVG export failed:', error);
        alert('Failed to export SVG');
    }
}

/**
 * Copy SVG code to clipboard
 */
async copySVGCode(svgContent) {
    try {
        await navigator.clipboard.writeText(svgContent);
        console.log('✅ SVG code copied to clipboard');
        // Show temporary notification
        this.showNotification('SVG code copied!', 'success');
    } catch (error) {
        console.error('❌ Copy failed:', error);
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = svgContent;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        this.showNotification('SVG code copied!', 'success');
    }
}

/**
 * Toggle zoom mode
 */
toggleSVGZoom(wrapper) {
    const svg = wrapper.querySelector('svg');
    if (!svg) return;
    
    const isZoomed = wrapper.classList.toggle('svg-zoomed');
    if (isZoomed) {
        svg.style.cursor = 'zoom-out';
        svg.style.maxWidth = 'none';
        svg.style.width = '150%';
        wrapper.style.overflow = 'auto';
    } else {
        svg.style.cursor = 'zoom-in';
        svg.style.maxWidth = '100%';
        svg.style.width = 'auto';
        wrapper.style.overflow = 'hidden';
    }
}

/**
 * Show SVG metadata info
 */
showSVGInfo(wrapper) {
    const svg = wrapper.querySelector('svg');
    if (!svg) return;
    
    const viewBox = svg.getAttribute('viewBox');
    const title = svg.querySelector('title')?.textContent || 'Untitled';
    const desc = svg.querySelector('desc')?.textContent || 'No description';
    const elementCount = svg.querySelectorAll('*').length;
    
    const info = `
📊 SVG Information:
━━━━━━━━━━━━━━━━━━━━━━
Title: ${title}
Description: ${desc}
ViewBox: ${viewBox || 'Not set'}
Elements: ${elementCount}
Rendered: ${new Date(parseInt(svg.getAttribute('data-render-timestamp'))).toLocaleString()}
    `.trim();
    
    alert(info);
}

/**
 * Show temporary notification
 */
showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `svg-notification svg-notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#4CAF50' : '#2196F3'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 2000);
}

/**
 * =====================================================================
 * SECTION 7: SVG STYLING & THEMING
 * =====================================================================
 */

/**
 * Get container styles based on visualization type
 */
getSVGContainerStyles(type) {
    const baseStyles = `
        width: 100%;
        max-width: 1200px;
        margin: 1rem auto;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        transition: all 0.3s ease;
    `;
    
    const typeStyles = {
        'cad': 'background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border: 2px solid #8e9eab;',
        'schematic': 'background: #fffff0; border: 2px solid #ffd700;',
        'blueprint': 'background: #001f3f; border: 2px solid #0074D9;',
        'molecule': 'background: #f0f8ff; border: 2px solid #4682b4;',
        'diagram': 'background: #fafafa; border: 1px solid #e0e0e0;',
        'svg': 'background: white; border: 1px solid #ddd;'
    };
    
    return baseStyles + (typeStyles[type] || typeStyles['svg']);
}

/**
 * Apply professional theming to SVG wrapper
 */
applySVGTheming(wrapper, type) {
    // Add hover effect
    wrapper.addEventListener('mouseenter', () => {
        wrapper.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.15)';
        wrapper.style.transform = 'translateY(-2px)';
    });
    wrapper.addEventListener('mouseleave', () => {
        wrapper.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
        wrapper.style.transform = 'translateY(0)';
    });
}

/**
 * Add metadata overlay
 */
addSVGMetadata(wrapper, svgElement, type) {
    if (!svgElement) return;
    
    const title = svgElement.querySelector('title')?.textContent;
    if (title) {
        const titleBar = document.createElement('div');
        titleBar.className = 'svg-title-bar';
        titleBar.textContent = title;
        titleBar.style.cssText = `
            position: absolute;
            bottom: 10px;
            left: 10px;
            padding: 0.5rem 1rem;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            font-size: 14px;
            font-weight: bold;
            border-radius: 4px;
            pointer-events: none;
        `;
        wrapper.appendChild(titleBar);
    }
}

/**
 * Enable interactive features
 */
enableSVGInteractivity(wrapper, type) {
    const svg = wrapper.querySelector('svg');
    if (!svg) return;
    
    // Enable click-to-zoom on SVG elements with IDs
    svg.querySelectorAll('[id]').forEach(element => {
        element.style.cursor = 'pointer';
        element.addEventListener('click', (e) => {
            e.stopPropagation();
            console.log('SVG element clicked:', element.id);
            // Could highlight, zoom, or show details
        });
    });
}

/**
 * =====================================================================
 * SECTION 8: LATEX RENDERING
 * =====================================================================
 */

/**
 * Render LaTeX mathematical equations
 */
async renderLatex(latexCode, container) {
    console.log('🔢 Rendering LaTeX equation');
    
    // Check if KaTeX is loaded
    if (typeof katex === 'undefined') {
        console.warn('⚠️ KaTeX not loaded, loading dynamically...');
        await this.loadKaTeX();
    }
    
    const wrapper = document.createElement('div');
    wrapper.className = 'visualization-latex-container';
    wrapper.style.cssText = `
        width: 100%;
        max-width: 800px;
        margin: 1rem auto;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #e8eef3 100%);
        border-left: 4px solid #4CAF50;
        border-radius: 8px;
        text-align: center;
        font-size: 1.2em;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    `;
    
    try {
        katex.render(latexCode.trim(), wrapper, {
            throwOnError: false,
            displayMode: true,
            trust: false // Security
        });
        console.log('✅ LaTeX rendered successfully');
    } catch (error) {
        console.error('❌ LaTeX rendering error:', error);
        wrapper.innerHTML = `
            <div style="color: #c00; font-family: monospace;">
                <strong>LaTeX Rendering Error:</strong><br>
                ${this.escapeHtml(error.message)}
                <pre style="text-align: left; margin-top: 1rem; background: #fee; padding: 1rem;">
${this.escapeHtml(latexCode)}
                </pre>
            </div>
        `;
    }
    
    // Add copy button
    const copyBtn = this.createControlButton('📋', 'Copy LaTeX', () => {
        this.copySVGCode(latexCode);
    });
    copyBtn.style.position = 'absolute';
    copyBtn.style.top = '10px';
    copyBtn.style.right = '10px';
    wrapper.style.position = 'relative';
    wrapper.appendChild(copyBtn);
    
    container.appendChild(wrapper);
}

/**
 * Dynamically load KaTeX library
 */
async loadKaTeX() {
    return new Promise((resolve, reject) => {
        // Load CSS
        if (!document.querySelector('link[href*="katex.min.css"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css';
            link.crossOrigin = 'anonymous';
            document.head.appendChild(link);
        }
        
        // Load JS
        if (!document.querySelector('script[src*="katex.min.js"]')) {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js';
            script.crossOrigin = 'anonymous';
            script.onload = () => {
                console.log('✅ KaTeX loaded successfully');
                resolve();
            };
            script.onerror = (error) => {
                console.error('❌ Failed to load KaTeX:', error);
                reject(error);
            };
            document.head.appendChild(script);
        } else {
            resolve();
        }
    });
}

/**
 * =====================================================================
 * SECTION 9: ALTERNATIVE DIAGRAM RENDERERS
 * =====================================================================
 */

/**
 * Render flowchart (Mermaid wrapper with flowchart syntax)
 */
async renderFlowchart(content, container) {
    const mermaidCode = `flowchart TD\n${content}`;
    await this.visualizationEngine.renderMermaid(mermaidCode, container);
}

/**
 * Render sequence diagram (Mermaid wrapper)
 */
async renderSequence(content, container) {
    const mermaidCode = `sequenceDiagram\n${content}`;
    await this.visualizationEngine.renderMermaid(mermaidCode, container);
}

/**
 * Render Gantt chart (Mermaid wrapper)
 */
async renderGantt(content, container) {
    const mermaidCode = `gantt\n${content}`;
    await this.visualizationEngine.renderMermaid(mermaidCode, container);
}

/**
 * Render UML diagram (Mermaid wrapper)
 */
async renderUML(content, container) {
    const mermaidCode = `classDiagram\n${content}`;
    await this.visualizationEngine.renderMermaid(mermaidCode, container);
}

/**
 * =====================================================================
 * SECTION 10: FUTURE: 3D & MAP RENDERING
 * =====================================================================
 */

/**
 * Placeholder for 3D rendering (Three.js integration)
 */
async render3D(content, container) {
    console.log('🚧 3D rendering not yet implemented');
    container.innerHTML = `
        <div style="padding: 2rem; text-align: center; background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px;">
            <h3>🚧 3D Rendering Coming Soon</h3>
            <p>Three.js integration in development</p>
            <pre style="text-align: left; max-width: 600px; margin: 1rem auto; background: #fff; padding: 1rem; border-radius: 4px;">
${this.escapeHtml(content)}
            </pre>
        </div>
    `;
}

/**
 * Placeholder for map rendering (Leaflet/Mapbox integration)
 */
async renderMap(content, container) {
    console.log('🚧 Map rendering not yet implemented');
    container.innerHTML = `
        <div style="padding: 2rem; text-align: center; background: #d1ecf1; border: 1px solid #0c5460; border-radius: 8px;">
            <h3>🗺️ Geographic Map Rendering Coming Soon</h3>
            <p>Leaflet/Mapbox integration in development</p>
            <pre style="text-align: left; max-width: 600px; margin: 1rem auto; background: #fff; padding: 1rem; border-radius: 4px;">
${this.escapeHtml(content)}
            </pre>
        </div>
    `;
}

/**
 * =====================================================================
 * EXPORT: Make functions available globally
 * =====================================================================
 */

// Export to window for integration
window.SVGRendererEnhancement = {
    renderSVGContent: renderSVGContent.bind(this),
    renderLatex: renderLatex.bind(this),
    sanitizeSVG: sanitizeSVG.bind(this),
    enhanceSVGElement: enhanceSVGElement.bind(this),
    getStartDelimiterEnhanced: getStartDelimiterEnhanced.bind(this),
    getEndDelimiterEnhanced: getEndDelimiterEnhanced.bind(this)
};

console.log('✅ SVG Renderer Enhancement loaded successfully');

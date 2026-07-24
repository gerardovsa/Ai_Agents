
/**
 * =============================================================================
 * SECTION 1: CORE SYSTEM CLASSES & CONTROLLERS
 * =============================================================================
 */

/**
 * 1.1 MERMAID FONT SIZE MANAGEMENT SYSTEM
 */
class MermaidFontController {
    // 1.1.1
    constructor() {
        this.defaultSize = 'normal';
        this.availableSizes = {
            'tiny': { value: 10, label: 'Tiny', icon: '🔍', scale: 0.8 },
            'small': { value: 12, label: 'Small', icon: '📝', scale: 0.9 },
            'normal': { value: 14, label: 'Normal', icon: '📄', scale: 1.0 },
            'medium': { value: 16, label: 'Medium', icon: '📋', scale: 1.1 },
            'large': { value: 18, label: 'Large', icon: '📊', scale: 1.2 },
            'huge': { value: 22, label: 'Huge', icon: '📈', scale: 1.4 },
            'giant': { value: 26, label: 'Giant', icon: '📐', scale: 1.6 }
        };

        this.injectCSS();
    }

    // 1.1.2
    injectCSS() {
        if (document.getElementById('mermaid-font-controller-css')) return;

        const style = document.createElement('style');
        style.id = 'mermaid-font-controller-css';
        style.textContent = `
            /* CSS Variables for font control */
            :root {
                --mermaid-active-font-size: 10px;
                --mermaid-container-scale: 1.8;
            }
            
            /* ont size data attributes */
            .viz-container[data-font-size="10"] { --mermaid-active-font-size: 10px; --mermaid-container-scale: 0.8; }
            .viz-container[data-font-size="12"] { --mermaid-active-font-size: 12px; --mermaid-container-scale: 0.9; }
            .viz-container[data-font-size="14"] { --mermaid-active-font-size: 14px; --mermaid-container-scale: 1.0; }
            .viz-container[data-font-size="16"] { --mermaid-active-font-size: 16px; --mermaid-container-scale: 1.1; }
            .viz-container[data-font-size="18"] { --mermaid-active-font-size: 18px; --mermaid-container-scale: 1.2; }
            .viz-container[data-font-size="22"] { --mermaid-active-font-size: 22px; --mermaid-container-scale: 1.4; }
            .viz-container[data-font-size="26"] { --mermaid-active-font-size: 26px; --mermaid-container-scale: 1.6; }
            
            /* PDATED: Isolated Mermaid text targeting - SCOPED TO VIZ CONTAINERS ONLY */
            .viz-container .mermaid text,
            .viz-container .mermaid tspan,
            .viz-container .mermaid .nodeLabel,
            .viz-container .mermaid .edgeLabel {
                font-size: var(--mermaid-active-font-size) !important;
                font-weight: 500 !important;
                font-family: "Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
                line-height: 1 !important;
                height: auto !important;
            }
            
            /* PDATED: Isolated HTML formatting classes - SCOPED TO VIZ CONTAINERS ONLY */
            .viz-container .mermaid svg text .mermaid-bold,
            .viz-container .mermaid text .mermaid-bold,
            .viz-container .mermaid tspan .mermaid-bold {
                font-weight: 700 !important;
                font-size: inherit !important;
                line-height: inherit !important;
                font-family: inherit !important;
            }
            
            .viz-container .mermaid svg text .mermaid-italic,
            .viz-container .mermaid text .mermaid-italic,
            .viz-container .mermaid tspan .mermaid-italic {
                font-style: italic !important;
                font-weight: inherit !important;
                font-size: inherit !important;
                line-height: inherit !important;
                font-family: inherit !important;
            }
            
            .viz-container .mermaid svg text .mermaid-code,
            .viz-container .mermaid text .mermaid-code,
            .viz-container .mermaid tspan .mermaid-code {
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
                font-size: 0.9em !important;
                font-weight: 500 !important;
                background: rgba(255, 255, 255, 0.1) !important;
                padding: 1px 3px !important;
                border-radius: 2px !important;
                line-height: inherit !important;
            }
            
            .viz-container .mermaid svg text .mermaid-small,
            .viz-container .mermaid text .mermaid-small,
            .viz-container .mermaid tspan .mermaid-small {
                font-size: 0.8em !important;
                font-weight: inherit !important;
                line-height: inherit !important;
                font-family: inherit !important;
                opacity: 0.8 !important;
            }
            
            .viz-container .mermaid svg text .mermaid-label,
            .viz-container .mermaid text .mermaid-label,
            .viz-container .mermaid tspan .mermaid-label {
                font-weight: 600 !important;
                font-size: inherit !important;
                line-height: inherit !important;
                font-family: inherit !important;
            }
            
            /* ompact bullets inside Mermaid HTML labels - SCOPED TO VIZ CONTAINERS ONLY */
            .viz-container .mermaid .mermaid-bullet {
                display: block !important;
                line-height: 1.2 !important;
                margin: 0.5px 0 !important;
            }

            /* ullet-only spacing fix: hide BR right after a bullet to avoid double spacing */
            .mermaid .mermaid-bullet + br.mermaid-br {
                display: none !important;
            }

            /* revent host container CSS (e.g., message-bubble pre-wrap) from affecting label HTML */
            .mermaid foreignObject div,
            .mermaid foreignObject p,
            .mermaid foreignObject span,
            .mermaid foreignObject li {
                white-space: normal !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            
            /* ontainer scaling */
            .mermaid rect.node,
            .mermaid circle.node {
                transform: scale(var(--mermaid-container-scale)) !important;
                transform-origin: center !important;
                transition: transform 0.3s ease !important;
            }
        `;
        document.head.appendChild(style);
    }

    // 1.1.3
    setFontSize(container, sizeName) {
        const sizeConfig = this.availableSizes[sizeName];
        if (!sizeConfig) return;

        // Remove old classes
        Object.keys(this.availableSizes).forEach(size => {
            container.classList.remove(`font-${size}`);
        });

        // Add new class and data
        container.classList.add(`font-${sizeName}`);
        container.setAttribute('data-font-size', sizeConfig.value.toString());
        container.setAttribute('data-font-name', sizeName);

        // Update CSS variables
        container.style.setProperty('--mermaid-active-font-size', `${sizeConfig.value}px`);
        container.style.setProperty('--mermaid-container-scale', sizeConfig.scale.toString());

        this.saveUserPreference(sizeName);
        this.showNotification(`Font size: ${sizeConfig.label} (${sizeConfig.value}px)`, 'success');

        return sizeConfig;
    }

    // 1.1.4
    getCurrentSize(container) {
        return container.getAttribute('data-font-name') || this.defaultSize;
    }

    // 1.1.5
    cycleFontSize(container, direction = 'up') {
        const currentSize = this.getCurrentSize(container);
        const sizeNames = Object.keys(this.availableSizes);
        const currentIndex = sizeNames.indexOf(currentSize);

        let newIndex;
        if (direction === 'up') {
            newIndex = currentIndex < sizeNames.length - 1 ? currentIndex + 1 : 0;
        } else {
            newIndex = currentIndex > 0 ? currentIndex - 1 : sizeNames.length - 1;
        }

        const newSize = sizeNames[newIndex];
        return this.setFontSize(container, newSize);
    }

    // 1.1.6
    saveUserPreference(sizeName) {
        try {
            localStorage.setItem('mermaid-font-preference', sizeName);
        } catch (e) {
            console.warn('Could not save font preference:', e);
        }
    }

    // 1.1.7
    loadUserPreference() {
        try {
            return localStorage.getItem('mermaid-font-preference') || this.defaultSize;
        } catch (e) {
            return this.defaultSize;
        }
    }

    // 1.1.8
    applyUserPreference(container) {
        const preferredSize = this.loadUserPreference();
        this.setFontSize(container, preferredSize);
    }

    // 1.1.9
    showNotification(message, type = 'info') {
        if (window.vizEngine && window.vizEngine.showNotification) {
            window.vizEngine.showNotification(message, type);
        } else {
            console.log(`📢 ${message}`);
        }
    }
}

/**
 * 1.1.4 – Export CSS helper so exports match chat rendering exactly
 * What & why:
 * - When exporting a Mermaid diagram, the serialized SVG/PNG can reintroduce <br> nodes
 *   between bullet spans inside foreignObject HTML, causing an empty line between bullets.
 * - In chat, we intentionally preserve <br> in content, but visually format bullets compactly.
 * - For exports only, we embed a tiny CSS into the cloned SVG that hides those specific
 *   <br class="mermaid-br"> nodes following a `.mermaid-bullet`, so the export spacing
 *   matches the on-screen look without mutating the live DOM.
 * Scope:
 * - Used only on cloned SVGs in export paths (SVG/PNG). Chat rendering is unaffected.
 */
window.MermaidExportCSS = function MermaidExportCSS() {
    try {
        return `
        /* Ensure bullets and line breaks render the same in exports */
        .mermaid .mermaid-bullet { display: block !important; line-height: 1.2 !important; margin: 0.5px 0 !important; }
        .mermaid .mermaid-bullet + br.mermaid-br { display: none !important; }
        .mermaid svg text .mermaid-label,
        .mermaid text .mermaid-label,
        .mermaid tspan .mermaid-label { font-weight: 600 !important; }
        .mermaid svg text .mermaid-code,
        .mermaid text .mermaid-code,
        .mermaid tspan .mermaid-code { font-family: 'Monaco','Menlo','Ubuntu Mono',monospace !important; font-size: 0.9em !important; font-weight: 500 !important; }
        /* Prevent host container whitespace rules from affecting inner HTML */
        .mermaid foreignObject div,
        .mermaid foreignObject p,
        .mermaid foreignObject span,
        .mermaid foreignObject li { white-space: normal !important; margin: 0 !important; padding: 0 !important; }
        /* Make node boxes visible and consistent */
        .mermaid g.node > rect,
        .mermaid g.node > circle,
        .mermaid g.node > polygon { fill: #ffffff !important; stroke: #b3b3b3 !important; stroke-width: 1.2 !important; shape-rendering: geometricPrecision !important; }
        /* Ensure edges have no fills (prevents black shadow wedges) */
        .mermaid g.edgePath path { fill: none !important; stroke: #6b7280 !important; }
        /* Extra safety: remove fill on any bare paths outside node groups */
        .mermaid svg > g path:not(.node):not(.arrowMarkerPath) { fill: none !important; }
        /* Arrowheads should use stroke color without extra outlines */
        .mermaid marker path,
        .mermaid marker polygon { fill: currentColor !important; stroke: none !important; }
        `;
    } catch (_e) {
        return '';
    }
};

/**
 * Utility: Embed export CSS into a given SVG element via <style> so when serialized it keeps exact spacing.
 */
function embedStyleIntoSvg(svgEl, cssText) {
    try {
        if (!svgEl || !cssText) return;
        const defs = svgEl.querySelector('defs') || (() => { const d = document.createElementNS('http://www.w3.org/2000/svg', 'defs'); svgEl.insertBefore(d, svgEl.firstChild); return d; })();
        const style = document.createElementNS('http://www.w3.org/2000/svg', 'style');
        style.setAttribute('type', 'text/css');
        style.textContent = cssText;
        defs.appendChild(style);
    } catch (e) {
        console.warn('⚠️ Failed to embed CSS into SVG:', e);
    }
}

// Utility: Remove redundant <br class="mermaid-br"> around bullet spans inside a container
// Purpose:
// - Some render paths (or intermediate conversions) can leave explicit BR nodes between
//   consecutive `.mermaid-bullet` spans. That creates a blank line in exports.
// - This utility cleans those BRs around bullets.
// Safety:
// - We call this on a cloned SVG (export-only) or a cloned DOM via html2canvas onclone,
//   never on the live chat DOM, so UI behavior remains unchanged.
function stripBreaksAroundBullets(root) {
    try {
        if (!root) return;

        const TEXT_NODE = 3;
        const ELEMENT_NODE = 1;

        const isWhitespace = (node) => node && node.nodeType === TEXT_NODE && !node.nodeValue.trim();
        const isBreakElement = (node) => node && node.nodeType === ELEMENT_NODE && node.tagName.toLowerCase() === 'br';
        const isRemovableBreak = (br) => {
            if (!isBreakElement(br)) return false;
            if (!br.classList || br.classList.length === 0) return true;
            return br.classList.contains('mermaid-br')
                || br.classList.contains('mermaid-generated-br')
                || br.classList.contains('markdown-softbreak');
        };
        const pruneChain = (startNode, stepKey) => {
            let cursor = startNode;
            while (cursor) {
                if (isWhitespace(cursor) || isRemovableBreak(cursor)) {
                    const toRemove = cursor;
                    cursor = cursor[stepKey];
                    toRemove.parentNode && toRemove.parentNode.removeChild(toRemove);
                    continue;
                }
                break;
            }
        };
        const isBulletElement = (node) => {
            if (!node || node.nodeType !== ELEMENT_NODE) return false;
            if (node.classList?.contains('mermaid-bullet')) return true;
            if (node.matches && node.matches('li.mermaid-bullet')) return true;
            return false;
        };

        const bulletNodes = root.querySelectorAll('span.mermaid-bullet, div.mermaid-bullet, p.mermaid-bullet, li.mermaid-bullet, li .mermaid-bullet');
        bulletNodes.forEach((bullet) => {
            pruneChain(bullet.previousSibling, 'previousSibling');
            pruneChain(bullet.nextSibling, 'nextSibling');

            const parent = bullet.parentElement;
            if (parent && parent !== root && parent.classList?.contains('mermaid-bullet-line')) {
                pruneChain(parent.previousSibling, 'previousSibling');
                pruneChain(parent.nextSibling, 'nextSibling');
            }

            const li = bullet.closest && bullet.closest('li');
            if (li) {
                Array.from(li.childNodes).forEach((child) => {
                    if (isRemovableBreak(child)) {
                        const prev = child.previousSibling;
                        const next = child.nextSibling;
                        if (isBulletElement(prev) || isBulletElement(next)) {
                            child.parentNode && child.parentNode.removeChild(child);
                        }
                    } else if (isWhitespace(child)) {
                        const prev = child.previousSibling;
                        const next = child.nextSibling;
                        const prevIsBullet = isBulletElement(prev);
                        const nextIsBullet = isBulletElement(next);
                        if (prevIsBullet || nextIsBullet) {
                            child.parentNode && child.parentNode.removeChild(child);
                        }
                    }
                });
            }
        });

        root.querySelectorAll('foreignObject').forEach((fo) => {
            let cursor = fo.firstChild;
            let lastWasBullet = false;
            while (cursor) {
                const next = cursor.nextSibling;
                if (isRemovableBreak(cursor) && lastWasBullet) {
                    let lookAhead = next;
                    while (lookAhead && isWhitespace(lookAhead)) {
                        lookAhead = lookAhead.nextSibling;
                    }
                    if (!lookAhead || isBulletElement(lookAhead)) {
                        cursor.parentNode && cursor.parentNode.removeChild(cursor);
                        cursor = next;
                        continue;
                    }
                }
                lastWasBullet = isBulletElement(cursor);
                cursor = next;
            }

            Array.from(fo.querySelectorAll('br')).forEach((br) => {
                if (!isRemovableBreak(br)) return;
                const prevEl = br.previousElementSibling;
                const nextEl = br.nextElementSibling;
                if (isBulletElement(prevEl) || isBulletElement(nextEl)) {
                    br.parentNode && br.parentNode.removeChild(br);
                }
            });
        });
    } catch (e) {
        console.warn('⚠️ stripBreaksAroundBullets failed:', e);
    }
}

// Utility: Normalize SVG visuals for export to avoid dark boxes and filled edge artifacts
function hardenSvgForExport(svgEl, { theme = 'light' } = {}) {
    try {
        if (!svgEl) return;
        const isDark = document.documentElement.classList.contains('dark') || theme === 'dark';
        // 1) Ensure nodes have visible fill/stroke
        svgEl.querySelectorAll('g.node rect, g.node circle, g.node polygon').forEach(el => {
            try {
                if (el.matches('rect.label-container')) return; // keep label-container styling managed elsewhere
                el.setAttribute('fill', '#ffffff');
                el.setAttribute('stroke', isDark ? '#6b7280' : '#b3b3b3');
                el.setAttribute('stroke-width', '1.2');
                el.style.fill = '#ffffff';
                el.style.stroke = isDark ? '#6b7280' : '#b3b3b3';
                el.style.strokeWidth = '1.2px';
            } catch (_e) { }
        });
        // 2) Remove fills from edge paths to prevent wedge artifacts
        svgEl.querySelectorAll('g.edgePath path').forEach(p => {
            try {
                p.setAttribute('fill', 'none');
                p.style.fill = 'none';
                // Keep stroke visible
                const stroke = p.getAttribute('stroke') || (isDark ? '#7d8590' : '#6b7280');
                p.setAttribute('stroke', stroke);
                p.style.stroke = stroke;
            } catch (_e) { }
        });
        // 3) Arrowhead marker cleanup
        // First, set a safe baseline
        svgEl.querySelectorAll('marker path, marker polygon').forEach(m => {
            try {
                m.setAttribute('stroke', 'none');
                m.style.stroke = 'none';
            } catch (_e) { }
        });
        // Then, for each path that references a marker, use its stroke color for the marker fill
        const refAttrs = ['marker-end', 'marker-mid', 'marker-start'];
        svgEl.querySelectorAll('path').forEach(p => {
            try {
                // Only treat edge-like paths or any with marker reference
                const hasMarker = refAttrs.some(a => p.hasAttribute(a));
                if (!hasMarker) return;
                const stroke = p.getAttribute('stroke') || (isDark ? '#7d8590' : '#6b7280');
                refAttrs.forEach(a => {
                    const url = p.getAttribute(a);
                    if (!url) return;
                    const id = url.replace(/url\(#|\)/g, '');
                    const marker = svgEl.querySelector(`marker#${CSS.escape(id)}`);
                    if (!marker) return;
                    marker.querySelectorAll('path, polygon').forEach(m => {
                        m.setAttribute('fill', stroke);
                        m.style.fill = stroke;
                        m.setAttribute('stroke', 'none');
                        m.style.stroke = 'none';
                    });
                });
            } catch (_e) { }
        });
    } catch (e) {
        console.warn('⚠️ hardenSvgForExport failed:', e);
    }
}

// Utility: Expand label-container widths to fit FO content to prevent right-side text clipping in exports
function expandLabelContainerWidthForExport(svgEl, { padding = 12 } = {}) {
    try {
        if (!svgEl) return;
        const rects = svgEl.querySelectorAll('rect');
        rects.forEach(rect => {
            const cls = (rect.getAttribute('class') || '').toLowerCase();
            if (!cls.includes('label-container')) return;
            const rectX = parseFloat(rect.getAttribute('x') || '0') || 0;
            let width = parseFloat(rect.getAttribute('width') || '0') || 0;
            const nodeGroup = rect.closest('g.node');
            if (!nodeGroup) return;
            const labelGroup = nodeGroup.querySelector('g.label');
            const fo = labelGroup ? labelGroup.querySelector('foreignObject') : null;
            if (!fo) return;
            // Measure inner content width
            let innerWidth = 0;
            try {
                const inner = fo.querySelector('div, span, p') || fo.firstElementChild;
                const gbr = inner?.getBoundingClientRect?.();
                innerWidth = Math.ceil(gbr?.width || inner?.scrollWidth || fo.getBBox?.().width || 0);
            } catch (_e) { }
            if (innerWidth > 0) {
                const targetW = innerWidth + padding * 2;
                if (targetW > width) {
                    rect.setAttribute('width', String(targetW));
                    // Shift x a little left to keep center similar
                    const newX = rectX - (targetW - width) / 2;
                    if (isFinite(newX)) rect.setAttribute('x', String(newX));
                    // Update foreignObject width
                    const foW = Math.max(10, targetW - padding * 2);
                    fo.setAttribute('width', String(foW));
                    // Update clipPath width if present
                    const clipId = (labelGroup && labelGroup.getAttribute('clip-path')) ? labelGroup.getAttribute('clip-path') : null;
                    if (clipId) {
                        const id = clipId.replace(/url\(#|\)/g, '');
                        const cp = svgEl.querySelector(`#${id}`);
                        const cpRect = cp?.querySelector('rect');
                        if (cpRect) {
                            cpRect.setAttribute('width', String(targetW - 2));
                        }
                    }
                }
            }
        });
    } catch (e) {
        console.warn('⚠️ expandLabelContainerWidthForExport failed:', e);
    }
}


/**
 * 1.2 PLOTLY SPACING CONFIGURATION UTILITY
 */
class PlotlySpacingController {
    // 1.2.1
    constructor() {
        this.spacingPresets = {
            'compact': {
                name: 'Compact',
                margin: { l: 60, r: 40, t: 40, b: 60, pad: 5 },
                bargap: 0.05,
                bargroupgap: 0.02,
                gridSpacing: { nticks: 12 }
            },
            'normal': {
                name: 'Normal',
                margin: { l: 80, r: 60, t: 50, b: 80, pad: 10 },
                bargap: 0.15,
                bargroupgap: 0.05,
                gridSpacing: { nticks: 10 }
            },
            'spacious': {
                name: 'Spacious',
                margin: { l: 100, r: 80, t: 60, b: 100, pad: 15 },
                bargap: 0.25,
                bargroupgap: 0.1,
                gridSpacing: { nticks: 8 }
            },
            'minimal': {
                name: 'Minimal',
                margin: { l: 40, r: 30, t: 30, b: 40, pad: 5 },
                bargap: 0.1,
                bargroupgap: 0.03,
                gridSpacing: { nticks: 6 }
            }
        };
    }

    // 1.2.2
    applySpacingPreset(plotlyData, presetName = 'normal') {
        const preset = this.spacingPresets[presetName];
        if (!preset) return;

        // Apply margin settings
        plotlyData.layout.margin = { ...plotlyData.layout.margin, ...preset.margin };

        // Apply bar spacing
        plotlyData.layout.bargap = preset.bargap;
        plotlyData.layout.bargroupgap = preset.bargroupgap;

        // Apply grid spacing
        if (plotlyData.layout.xaxis) {
            plotlyData.layout.xaxis.nticks = preset.gridSpacing.nticks;
        }
        if (plotlyData.layout.yaxis) {
            plotlyData.layout.yaxis.nticks = preset.gridSpacing.nticks - 2;
        }

        console.log(`pplied ${preset.name} spacing preset`);
    }

    // 1.2.3
    setBarSpacing(plotlyData, bargap = 0.15, bargroupgap = 0.05) {
        plotlyData.layout.bargap = Math.max(0, Math.min(1, bargap));
        plotlyData.layout.bargroupgap = Math.max(0, Math.min(1, bargroupgap));
    }

    // 1.2.4
    setMargins(plotlyData, margins = {}) {
        plotlyData.layout.margin = {
            ...plotlyData.layout.margin,
            ...margins
        };
    }

    // 1.2.5
    setGridDensity(plotlyData, density = 'normal') {
        const densities = {
            'sparse': { x: 6, y: 5 },
            'normal': { x: 10, y: 8 },
            'dense': { x: 15, y: 12 }
        };

        const config = densities[density] || densities.normal;

        if (plotlyData.layout.xaxis) {
            plotlyData.layout.xaxis.nticks = config.x;
        }
        if (plotlyData.layout.yaxis) {
            plotlyData.layout.yaxis.nticks = config.y;
        }
    }
}

/**
 * =============================================================================
 * SECTION 2: MAIN VISUALIZATION ENGINE CLASS
 * =============================================================================
 */

/**
 * 2.1 UNIFIED Visualization Engine V1.19 - NO LOADING STATES
 */
class VisualizationEngine {
    // 2.1.1
    constructor(options = {}) {
        this.options = {
            theme: 'light', // IXED: Changed from 'dark' to 'light' for default theme
            defaultHeight: 'auto', // HANGED: Fixed 600px → auto for dynamic sizing
            enableInteractivity: true,
            enableExport: true,
            enableResize: true,
            enableAnimation: false,
            enableRealTimeResize: true,
            fontFamily: 'Roboto, Arial, sans-serif',
            colorScheme: {
                primary: '#2E5D79',
                secondary: '#4E92B5',
                accent: '#3F78A0',
                background: '#161b22',
                text: '#e6edf3'
            },
            spacing: {
                containerPadding: 16,
                visualizationMargin: 12,
                containerGap: 8,
                headerHeight: 40,
                footerHeight: 30,
                responsiveBreakpoints: {
                    mobile: 480,
                    tablet: 768,
                    desktop: 1200
                }
            },
            animations: {
                renderDuration: 150,
                themeSwitchDuration: 250,
                resizeThrottle: 50,
                smoothTransitions: true
            },
            ...options
        };

        this.charts = new Map();
        this.isInitialized = false;
        this.loadingPromises = new Map();
        this.renderCount = 0;

        this.resizeObserver = null;
        this.animationFrameId = null;
        this.pendingResizes = new Set();

        this.layoutState = {
            containerDimensions: new Map(),
            responsiveBreakpoint: 'desktop',
            currentTheme: this.options.theme,
            isRendering: false
        };

        this.init();
    }

    // 2.1.2
    async init() {
        if (this.isInitialized) return;

        try {
            await this.loadFontAwesome();

            this.loadLibrariesAsync();
            this.setupLightweightObservation();
            this.setupResponsiveDesign();
            this.injectUnifiedStyles();
            this.setupGlobalListeners();
            this.setupJSONFileHandling();
            this.setupTooltipPositioning();
            this.initializeMermaidFontController();

            this.isInitialized = true;

        } catch (error) {
            console.error(' Failed to initialize UNIFIED Visualization Engine V1.19:', error);
            throw error;
        }
    }

    // 2.1.3 - Wait for renderer module to load
    async waitForRenderer(rendererName, scriptFile, timeout = 10000) {
        const startTime = Date.now();

        // Check if already loaded
        if (typeof window[rendererName] !== 'undefined') {
            console.log(`✅ ${rendererName} already loaded`);
            return;
        }

        console.log(`⏳ Waiting for ${rendererName} to load...`);

        // Poll for renderer to become available
        return new Promise((resolve, reject) => {
            const checkInterval = setInterval(() => {
                if (typeof window[rendererName] !== 'undefined') {
                    clearInterval(checkInterval);
                    console.log(`✅ ${rendererName} loaded successfully`);
                    resolve();
                } else if (Date.now() - startTime > timeout) {
                    clearInterval(checkInterval);
                    reject(new Error(`${rendererName} failed to load within ${timeout}ms. Check that ${scriptFile} is included in HTML.`));
                }
            }, 50); // Check every 50ms
        });
    }

    // 2.1.4
    loadFontAwesome() {
        return new Promise((resolve, reject) => {
            // Check if FontAwesome is already loaded
            if (document.querySelector('link[href*="font-awesome"]') || window.FontAwesome) {
                if (document.body) {
                    document.body.classList.add('fa-loaded');
                }
                resolve();
                return;
            }

            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
            link.crossOrigin = 'anonymous';

            link.onload = () => {
                console.log('ontAwesome loaded successfully');
                if (document.body) {
                    document.body.classList.add('fa-loaded');
                }
                this.addIconFallbackStyles();
                resolve();
            };

            link.onerror = () => {
                console.warn('⚠️ FontAwesome failed to load, using fallback icons');
                this.addIconFallbackStyles();
                resolve();
            };

            document.head.appendChild(link);

            setTimeout(() => {
                if (!link.sheet && !document.body.classList.contains('fa-loaded')) {
                    console.warn('⚠️ FontAwesome load timeout, using fallback icons');
                    this.addIconFallbackStyles();
                    resolve();
                }
            }, 5000);
        });
    }

    // 2.1.4
    initializeMermaidFontController() {
        try {
            window.mermaidFontController = new MermaidFontController();
        } catch (error) {
            console.error(' Failed to initialize Mermaid font controller:', error);
        }
    }

    // 2.1.5
    addIconFallbackStyles() {
        const iconFallbackCSS = `
        /* Fallback icons if FontAwesome fails */
        .viz-action-btn i {
            display: inline-block;
            font-style: normal;
            font-weight: bold;
            font-size: 12px;
            line-height: 1;
            text-align: center;
            width: 12px;
            height: 12px;
        }
        
        /* Specific fallback icons */
        .viz-action-btn i.fas.fa-copy::before { content: "⧉"; }
        .viz-action-btn i.fas.fa-chart-line::before { content: "📈"; }
        .viz-action-btn i.fas.fa-search-plus::before { content: "🔍"; }
        .viz-action-btn i.fas.fa-hand-paper::before { content: "✋"; }
        .viz-action-btn i.fas.fa-home::before { content: "🏠"; }
        .viz-action-btn i.fas.fa-calculator::before { content: "🧮"; }
        .viz-action-btn i.fas.fa-expand::before { content: "⛶"; }
        .viz-action-btn i.fas.fa-palette::before { content: "🎨"; }
        .viz-action-btn i.fas.fa-share-alt::before { content: "🔗"; }
        .viz-action-btn i.fas.fa-print::before { content: "🖨"; }
        .viz-action-btn i.fas.fa-download::before { content: "⬇"; }
        `;

        const fallbackStyle = document.createElement('style');
        fallbackStyle.id = 'icon-fallback-styles';
        fallbackStyle.textContent = iconFallbackCSS;
        document.head.appendChild(fallbackStyle);
    }

    // 2.2.1
    async loadLibrariesAsync() {
        setTimeout(async () => {
            try {
                await this.loadLibraries();
            } catch (error) {
                console.warn('Some libraries failed to load:', error);
            }
        }, 0);
    }

    // 2.2.2
    async loadLibraries() {
        const libraries = [
            {
                name: 'Plotly',
                check: () => window.Plotly,
                load: () => this.waitForLibrary('Plotly')
            },
            {
                name: 'Chart.js',
                check: () => window.Chart,
                load: () => this.waitForLibrary('Chart')
            },
            {
                name: 'Mermaid',
                check: () => window.mermaid,
                load: () => this.waitForLibrary('mermaid')
            },
            {
                name: 'Marked',
                check: () => window.marked,
                load: () => this.waitForLibrary('marked')
            }
        ];

        const loadPromises = libraries.map(async (lib) => {
            if (!lib.check()) {
                console.log(`📦 Loading ${lib.name}...`);
                await lib.load();
            }
        });

        await Promise.all(loadPromises);
    }

    // 2.2.3
    waitForLibrary(libraryName) {
        return new Promise((resolve, reject) => {
            let attempts = 0;
            const maxAttempts = 50;

            const checkLibrary = () => {
                attempts++;

                if (window[libraryName]) {
                    console.log(`{libraryName} library found`);
                    resolve();
                    return;
                }

                if (attempts >= maxAttempts) {
                    console.warn(`⚠️ ${libraryName} library not found after waiting`);
                    reject(new Error(`${libraryName} library not loaded`));
                    return;
                }

                setTimeout(checkLibrary, 100);
            };

            checkLibrary();
        });
    }

    // 2.2.4 - ENHANCED: Better Mermaid initialization like ALTERNATIVE file
    async loadMermaid() {
        await this.waitForLibrary('mermaid');

        if (window.mermaid) {
            // ========================================================================
            // EW (Jul 22 2026): Mermaid 10.x staging-element invariant.
            //
            // `mermaid.render(id, source)` creates a body-level element with id
            // `d{id}` and measures its `getBoundingClientRect()` to compute
            // layout (node positions, edge routing, pie radius, label offsets).
            // The SPA-level rule in business-ai-platform-v2.html keeps that
            // element OFF-SCREEN-BUT-MEASURABLE (position:fixed, top:-10000px,
            // min-width:700px). DO NOT remove that rule from the SPA CSS or
            // pies will emit `viewBox="0 0 0 450"` and flowcharts will throw
            // `Could not find a suitable point for the given distance` from
            // `calcLabelPosition`.
            //
            // See:
            //   - business-ai-platform-v2.html L~10730 (the staging CSS rule)
            //   - VISUALIZATION_SYSTEM_DOCUMENTATION.md "Mermaid Render Lifecycle"
            //   - VISUALIZATION_MERMAID_RENDERING_FIX_JULY22_2026.md (root)
            // ========================================================================
            // NHANCED: More comprehensive Mermaid configuration
            mermaid.initialize({
                startOnLoad: false,
                theme: this.options.theme === 'dark' ? 'dark' : 'default',
                securityLevel: 'loose', // llow HTML labels
                htmlLabels: true, // nable HTML content in nodes
                flowchart: {
                    useMaxWidth: true,
                    htmlLabels: true // pecifically enable for flowcharts
                },
                themeVariables: {
                    primaryColor: this.options.colorScheme.primary,
                    primaryTextColor: this.options.colorScheme.text,
                    primaryBorderColor: this.options.colorScheme.accent,
                    lineColor: this.options.colorScheme.secondary
                },
                // EW: Better error handling
                logLevel: 'error',
                suppressErrorRendering: true
            });

            // FIX: Intercept Mermaid's dynamic <style> injections that cause
            // purple borders to bleed onto the entire page layout.
            this._installMermaidStyleGuard();
        }
    }

    /**
     * MutationObserver that watches for <style> tags injected by Mermaid v10
     * and strips any border/background rules that bleed outside viz-containers.
     * This prevents the "purple border around everything" issue.
     */
    _installMermaidStyleGuard() {
        if (this._mermaidStyleGuardInstalled) return;
        this._mermaidStyleGuardInstalled = true;

        const sanitizeMermaidStyle = (styleEl) => {
            try {
                if (!styleEl || !styleEl.textContent) return;
                const id = styleEl.id || '';
                // Only process mermaid-generated style tags (not our own)
                if (id.includes('mermaid-font-controller') || id.includes('viz-engine')) return;

                let css = styleEl.textContent;
                let changed = false;

                // Remove global .mermaid border rules that bleed to the whole page
                const globalBorderPattern = /(?:^|\})\s*\.mermaid\s*\{([^}]*border[^}]*)\}/gm;
                if (globalBorderPattern.test(css)) {
                    css = css.replace(globalBorderPattern, (match, props) => {
                        // Strip border properties but keep others
                        const cleaned = props.replace(/border[^;]*;?/g, '');
                        return match.replace(props, cleaned + 'border:none!important;');
                    });
                    changed = true;
                }

                // NOTE: We deliberately do NOT strip `#d?mermaid…` rules from
                // Mermaid's injected styles.  Mermaid 10.x uses those selectors
                // for its render output, and stripping them silently breaks
                // rendering.  Error styling is handled via the .mermaid-error-*
                // class selectors below (and via showMermaidError), not by ID.

                if (changed) styleEl.textContent = css;
            } catch (e) {
                // Silently ignore
            }
        };

        // Watch for dynamically injected <style> tags from mermaid.
        // NOTE: We deliberately do NOT remove nodes whose IDs start with
        // "dmermaid" / "d-mermaid".  Mermaid's `mermaid.render()` creates a
        // temporary staging element on the body with id `d${renderId}` to
        // measure layout while it builds the SVG.  If that element is removed
        // or hidden mid-render, Mermaid produces a `0 0 0 H` viewBox, which
        // cascades into broken pies, broken flowcharts, and an unbounded retry
        // storm.  Let Mermaid own its own staging node lifecycle.
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.tagName === 'STYLE') {
                        sanitizeMermaidStyle(node);
                    }
                });
            });
        });

        observer.observe(document.head, { childList: true, subtree: false });
        observer.observe(document.body, { childList: true, subtree: false });

        // Also sanitize any already-injected mermaid styles
        document.querySelectorAll('head style').forEach(sanitizeMermaidStyle);
    }

    // 2.2.5
    loadScript(src) {
        if (this.loadingPromises.has(src)) {
            return this.loadingPromises.get(src);
        }

        const promise = new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });

        this.loadingPromises.set(src, promise);
        return promise;
    }

    // 2.3.1
    injectUnifiedStyles() {
        const isDark = this.options.theme === 'dark';
        const seamlessBg = 'transparent'; /* 🎨 TRANSPARENT: Works in both light and dark mode */
        const textColor = isDark ? this.options.colorScheme.text : '#24292f';
        const borderColor = isDark ? '#30363d' : '#d0d7de';

        const styles = `
        /* IMPLIFIED: Containers without loading states */
        .viz-container {
            position: relative;
            display: block;
            width: 100%;
            margin: ${this.options.spacing.visualizationMargin + 50}px 0 ${this.options.spacing.visualizationMargin}px 0;
            padding: ${this.options.spacing.containerPadding}px;
            background: ${seamlessBg} !important;
            border-radius: 8px;
            overflow: visible;
            z-index: auto;
            box-sizing: border-box;
            height: auto; /* NCREASED: 300px → 450px to prevent truncation */
            padding-top: 40px;
            border: 1px solid var(--border-default);
        }

        /* irect content area - auto-size to its content; hide when empty to avoid gaps */
        .viz-content-area {
            position: relative;
            width: 100%;
            height: auto;
            min-height: 0;
            padding-bottom: 40px;
            border-radius: 8px;
            opacity: 1;
            display: block;
            overflow: auto;
        }
        .viz-content-area:empty { display: none; }

        .viz-content-area.is-resizing {
            cursor: ns-resize;
            user-select: none;
        }

        .viz-resize-handle {
            position: absolute;
            left: 50%;
            bottom: 12px;
            transform: translateX(-50%);
            width: 68px;
            height: 10px;
            border-radius: 999px;
            background: linear-gradient(90deg, 
                var(--accent-primary-alpha-25, rgba(59, 130, 246, 0.25)), 
                var(--accent-primary-alpha-65, rgba(59, 130, 246, 0.65)), 
                var(--accent-primary-alpha-25, rgba(59, 130, 246, 0.25))
            );
            box-shadow: 0 2px 6px rgba(0,0,0,0.35);
            cursor: ns-resize;
            transition: background 0.2s ease, opacity 0.2s ease, box-shadow 0.2s ease;
            z-index: 20;
        }

        .viz-resize-handle::after {
            content: '';
            position: absolute;
            inset: 2px 10px;
            border-radius: 999px;
            background: var(--bg-tertiary, rgba(0,0,0,0.4));
        }

        .viz-content-area.is-resizing .viz-resize-handle,
        .viz-resize-handle:hover {
            background: linear-gradient(90deg, 
                var(--accent-primary-alpha-45, rgba(59, 130, 246, 0.45)), 
                var(--accent-primary-alpha-85, rgba(59, 130, 246, 0.85)), 
                var(--accent-primary-alpha-45, rgba(59, 130, 246, 0.45))
            );
            box-shadow: 0 3px 8px rgba(0,0,0,0.45);
        }

        /* ction bar styling */
        .viz-action-bar {
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            display: flex;
            gap: 2px;
            background: rgba(30, 30, 30, 0.08);
            backdrop-filter: blur(3px);
            border-radius: 6px;
            padding: 4px 8px;
            opacity: 0.3;
            transition: opacity 0.3s ease;
            flex-wrap: nowrap;
            max-width: 90%;
            justify-content: center;
            overflow: visible !important;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }

        .viz-action-bar:hover {
            opacity: 1;
            background: rgba(30, 30, 30, 0.15);
        }

        /* 🎨 Action buttons - CONSISTENT STYLE */
        .viz-action-btn {
            width: 28px;
            height: 28px;
            margin: 0 1px;
            font-size: 12px;
            background: #2a2a2a;                  /* 🔑 Dark grey background */
            border: none;                         /* 🔑 No borders */
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;                         /* 🔑 White icons */
            padding: 4px;
            transition: all 0.15s ease;
            position: relative;
            box-sizing: border-box;
            flex-shrink: 0;
        }
        
        .viz-action-btn:hover {
            background: #FF7A00;                  /* 🔑 Orange hover */
        }

        /* con rendering with FontAwesome support */
        .viz-action-btn i {
            font-size: 12px;
            color: white;                         /* 🔑 White icons */
        }
            line-height: 1;
            display: inline-block;
            font-style: normal;
            font-variant: normal;
            text-rendering: auto;
            -webkit-font-smoothing: antialiased;
            font-family: "Font Awesome 6 Free", "Font Awesome 6 Pro", sans-serif;
            font-weight: 900;
        }

        /* efault icon color: brand primary (subtle) inside viz action bar */
        .viz-action-bar .viz-action-btn i,
        .viz-action-bar .viz-action-btn .fa-solid,
        .viz-action-bar .viz-action-btn .fa-regular,
        .viz-action-bar .viz-action-btn .fa-brands {
            /* Use brand primary via user-elements with a touch of transparency */
            color: color-mix(in srgb, var(--user-elements) 85%, transparent) !important;
        }

        .viz-action-btn i.fas::before {
            font-family: "Font Awesome 6 Free";
            font-weight: 900;
            display: inline-block;
        }

        .viz-action-btn i.fas {
            font-size: 12px;
        }

        /* ide Unicode fallback when FontAwesome is loaded */
        .fa-loaded .viz-action-btn i.fas {
            text-indent: -9999px;
            overflow: hidden;
        }

        .fa-loaded .viz-action-btn i.fas::before {
            text-indent: 0;
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
        }

        /* 🎨 Button hover states - CONSISTENT ORANGE HOVER */
        .viz-action-btn[data-action="export"]:hover,
        .viz-action-btn[data-action="copy"]:hover,
        .viz-action-btn[data-action="share"]:hover,
        .viz-action-btn[data-action="view"]:hover,
        .viz-action-btn[data-action="analysis"]:hover,
        .viz-action-btn[data-action="plotly"]:hover {
            background: #FF7A00 !important;       /* 🔑 Orange hover */
            border: none !important;
            opacity: 1 !important;
            transform: scale(1.05);
        }

        .viz-action-btn[data-action="export"]:hover i,
        .viz-action-btn[data-action="copy"]:hover i,
        .viz-action-btn[data-action="share"]:hover i,
        .viz-action-btn[data-action="view"]:hover i,
        .viz-action-btn[data-action="analysis"]:hover i,
        .viz-action-btn[data-action="plotly"]:hover i {
            color: white !important;              /* 🔑 White icons on hover */
        }

        /* ide default Plotly modebar */
        .plotly-container .modebar {
            display: none !important;
        }

        /* ropdown styling */
        .chart-type-switcher,
        .export-options-switcher,
        .color-theme-switcher,
        .font-size-switcher {
            position: absolute;
            top: -45px;
            z-index: 1001;
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border-primary) !important;
            border-radius: 6px !important;
            padding: 6px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            min-width: 160px;
        }

        .chart-type-select,
        .export-format-select,
        .color-theme-select,
        .font-size-select {
            background: var(--bg-secondary) !important;
            border: none !important;
            border-radius: 4px !important;
            padding: 8px 12px !important;
            font-size: 12px !important;
            cursor: pointer !important;
            color: var(--text-primary) !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }

        /* ont size menu styling */
        .font-size-menu {
            position: absolute;
            top: 35px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1002;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 6px;
            padding: 6px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            min-width: 180px;
            animation: popupSlideIn 0.2s ease-out;
        }

        .font-menu-item {
            width: 100%;
            background: transparent;
            color: var(--text-primary);
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin: 1px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s ease;
        }

        .font-menu-item:hover {
            background: var(--bg-tertiary) !important;
        }

        .font-menu-item.active {
            background: var(--accent-blue) !important;
            color: white !important;
        }

        /* efault clamp for Mermaid in Two-Rule containers to prevent oversized blocks */
        .viz-container[data-viz-type="mermaid"] .viz-content-area {
            max-height: 500px;
            overflow: auto;
        }

        @keyframes popupSlideIn {
            from {
                opacity: 0;
                transform: translateX(-50%) translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateX(-50%) translateY(0);
            }
        }

        /* heme variables with vibrant accent colors */
        [data-theme="dark"] {
            --button-border-color: #30363d;
            --button-icon-color: #9ca3af;
            --button-hover-bg: rgba(255, 255, 255, 0.1);
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --text-primary: #e6edf3;
            --text-secondary: #7d8590;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-orange: #f59e0b;
            --accent-red: #ef4444;
            --accent-purple: #8b5cf6;
            --accent-cyan: #06b6d4;
            --border-primary: #30363d;
        }

        [data-theme="light"] {
            --button-border-color: #d0d7de;
            --button-icon-color: #9ca3af;
            --button-hover-bg: rgba(0, 0, 0, 0.05);
            --bg-primary: #ffffff;
            --bg-secondary: #f6f8fa;
            --bg-tertiary: #eaeef2;
            --text-primary: #24292f;
            --text-secondary: #656d76;
            --accent-blue: #2563eb;
            --accent-green: #059669;
            --accent-orange: #d97706;
            --accent-red: #dc2626;
            --accent-purple: #7c3aed;
            --accent-cyan: #0891b2;
            --border-primary: #d0d7de;
        }

        /* isualization container styles */
        .plotly-container {
            background: ${seamlessBg} !important;
            border-radius: 8px;
            color: ${textColor} !important;
            min-height: 300px; /* EDUCED: 500px → 300px for auto-sizing */
            padding: 10px;
            position: relative;
            overflow: visible;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            max-width: 100%;
        }

        .plotly-graph-div {
            background: ${seamlessBg} !important;
            position: relative;
            width: 100% !important;
            min-width: 400px !important;
            max-width: 100% !important;
            height: auto !important;
            margin: 0 auto;
            display: block;
            border-radius: 6px;
            margin-bottom: 20px;
        }

        .mermaid-container {
            background: ${seamlessBg} !important;
            border-radius: 8px;
            color: ${textColor} !important;
            padding: 20px;
            text-align: center;
            position: relative;
            overflow: visible;
            height: auto; /* EDUCED: 500px → 300px for auto-sizing */
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            max-width: 100%;
            min-width: 0; /* RESPONSIVE: let the container fit narrow chat viewports */
            box-sizing: border-box;
        }

        /* EW: Expanded Mermaid containers for complex diagrams */
        .mermaid-container.mermaid-expanded {
            max-width: 95vw !important;
            min-width: 0 !important;
            overflow-x: auto;
            overflow-y: visible;
        }

        .mermaid-container .mermaid {
            width: 100%;
            height: auto;
            overflow: visible;
        }

        /* EW: Fullscreen Mermaid viewer */
        .mermaid-fullscreen-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.95);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(5px);
        }

        .mermaid-fullscreen-container {
            position: relative;
            width: 95vw;
            height: 90vh;
            background: ${seamlessBg};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .mermaid-fullscreen-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 0 15px 0;
            border-bottom: 1px solid var(--border-primary);
            margin-bottom: 15px;
        }

        .mermaid-fullscreen-title {
            font-size: 18px;
            font-weight: 600;
            color: ${textColor};
            margin: 0;
        }

        .mermaid-fullscreen-controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .mermaid-fullscreen-btn {
            padding: 8px 12px;
            background: #2a2a2a;              /* 🔑 Dark grey background */
            border: none;                     /* 🔑 No borders */
            border-radius: 6px;
            color: white;                     /* 🔑 White text */
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .mermaid-fullscreen-btn:hover {
            background: #FF7A00;              /* 🔑 Orange hover */
        }

        .mermaid-fullscreen-content {
            flex: 1;
            position: relative;
            overflow: hidden;
            border: 1px solid var(--border-primary);
            border-radius: 8px;
            background: white;
        }

        .mermaid-fullscreen-viewport {
            width: 100%;
            height: 100%;
            overflow: hidden;
            position: relative;
            cursor: grab;
        }

        .mermaid-fullscreen-viewport:active {
            cursor: grabbing;
        }

        .mermaid-fullscreen-diagram {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            transition: transform 0.1s ease;
            transform-origin: center;
        }

        /* ative Browser Fullscreen Mode - Enable vertical scrolling for tall diagrams */
        .viz-container:fullscreen {
            overflow-y: auto !important;
            overflow-x: hidden !important;
            height: 100vh !important;
            width: 100vw !important;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            box-sizing: border-box;
        }

        .viz-container:fullscreen .viz-content-area {
            overflow-y: visible !important;
            overflow-x: auto !important;
            max-width: 100%;
            width: 100%;
            height: auto;
            min-height: 100%;
        }

        /* rowser-specific fullscreen selectors */
        .viz-container:-webkit-full-screen {
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }

        .viz-container:-moz-full-screen {
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }

        .viz-container:-ms-fullscreen {
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }

        /* ullscreen backdrop styling */
        .viz-container::backdrop {
            background: rgba(0, 0, 0, 0.95);
        }

        .viz-container::-webkit-backdrop {
            background: rgba(0, 0, 0, 0.95);
        }

        .mermaid-zoom-indicator {
            position: absolute;
            bottom: 15px;
            right: 15px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 11px;
            pointer-events: none;
        }

        .chart-container {
            background: ${seamlessBg} !important;
            border-radius: 8px;
            color: ${textColor} !important;
            padding: 20px;
            position: relative;
            overflow: visible;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: auto; /* EDUCED: 500px → 300px for auto-sizing */
        }

        /* rror display */
        .viz-error {
            text-align: center;
            padding: 40px 20px;
            color: var(--accent-red);
            border: 1px dashed var(--accent-red);
            border-radius: 8px;
            margin: 20px;
            background: rgba(255, 0, 0, 0.05);
        }

        .viz-error h3 {
            margin: 0 0 10px 0;
            font-size: 16px;
        }

        .viz-error p {
            margin: 0;
            font-size: 14px;
            opacity: 0.8;
        }

        /* otifications */
        .viz-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 16px;
            color: white;
            border-radius: 6px;
            z-index: 10600;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            max-width: 300px;
        }

        .viz-notification.success { background: var(--accent-green); }
        .viz-notification.error { background: var(--accent-red); }
        .viz-notification.info { background: var(--accent-blue); }
        .viz-notification.warning { background: var(--accent-orange); }

        /* IXED: Compact text content styling - no excessive spacing */
        .viz-text-content {
            margin: 6px 0;
            line-height: 1.4;
            color: var(--text-primary);
            text-align: left;
            font-size: 14px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .viz-text-content h1,
        .viz-text-content h2,
        .viz-text-content h3,
        .viz-text-content h4,
        .viz-text-content h5,
        .viz-text-content h6 {
            color: var(--text-primary);
            margin: 12px 0 4px 0;
            line-height: 1.3;
        }

        .viz-text-content p {
            margin: 8px 0;
            color: var(--text-primary);
        }

        .viz-text-content ul,
        .viz-text-content ol {
            margin: 8px 0;
            padding-left: 24px;
            color: var(--text-primary);
        }

        .viz-text-content li {
            margin: 4px 0;
            color: var(--text-primary);
        }

        .viz-text-content code {
            background: var(--bg-secondary);
            color: var(--text-primary);
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 0.9em;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }

        .viz-text-content pre {
            background: var(--bg-secondary);
            color: var(--text-primary);
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 10px 0;
            border: 1px solid var(--border-primary);
        }

        .viz-text-content blockquote {
            border-left: 4px solid var(--accent-blue);
            padding-left: 16px;
            margin: 16px 0;
            color: var(--text-secondary);
            font-style: italic;
        }

        /* esponsive design */
        @media (max-width: 768px) {
            .viz-action-btn {
                width: 24px;
                height: 24px;
                font-size: 10px;
                margin: 0;
            }
            
            .viz-action-bar {
                gap: 1px;
                padding: 2px 4px;
            }
            
            .viz-container {
                margin: 20px 0;
                padding: 12px;
                min-height: 300px;
            }
            
            .plotly-graph-div {
                min-width: 320px !important;
            }
            
            .chart-type-switcher,
            .export-options-switcher,
            .color-theme-switcher,
            .font-size-switcher {
                min-width: 140px;
                right: 0;
            }
        }

        @media (max-width: 480px) {
            .viz-action-bar {
                max-width: 95%;
                flex-wrap: wrap;
                gap: 2px;
            }
            
            .plotly-graph-div {
                min-width: 280px !important;
            }
            
            .viz-action-btn {
                width: 20px;
                height: 20px;
                font-size: 9px;
            }
        }

        /* ===================================================================
         * MERMAID GLOBAL CSS OVERRIDE - Prevent mermaid from injecting
         * purple/colored borders and backgrounds onto the page globally.
         * Mermaid v10 injects <style> tags that target .mermaid globally,
         * which bleeds onto the entire page layout. These rules neutralize
         * that bleed while keeping proper rendering INSIDE viz containers.
         * =================================================================== */

        /* Neutralize any global .mermaid styles mermaid injects */
        body > .mermaid,
        .mermaid:not(.viz-container .mermaid):not([id*="mermaid-"]) {
            border: none !important;
            background: transparent !important;
            outline: none !important;
            box-shadow: none !important;
        }

        /* Hide Mermaid runtime error classes.  We deliberately do NOT hide nodes
           whose IDs start with 'dmermaid' -- those are Mermaid own staging
           elements that must remain visible while mermaid.render measures them. */
        .mermaid-error-icon,
        .error-icon,
        .error-text {
            display: none !important;
        }

        /* Give Mermaid's body-level staging element enough room to lay out
           against, independent of the visible container's width.  When the
           visible .mermaid-container is narrow (chat column, deferred thread
           render, collapsed sidebar), Mermaid's calcLabelPosition otherwise
           fails with 'Could not find a suitable point for the given distance'
           because every offset along the edge collides with squeezed node
           boxes.  Staging width controls layout; useMaxWidth:true then scales
           the resulting SVG to fit the (potentially narrower) visible
           container.  Scoped to Mermaid staging ids only -- Plotly, Apex and
           CAD use different id conventions and are unaffected. */
        [id^="dmermaid"],
        [id^="d-mermaid"] {
            min-width: 700px;
        }

        /* Ensure mermaid syntax errors stay inside the viz-content-area */
        .viz-content-area .mermaid-syntax-error,
        .viz-content-area .mermaid-error-msg {
            display: block !important;
            color: var(--accent-red, #ef4444);
            padding: 12px;
            border-radius: 6px;
            background: rgba(239, 68, 68, 0.08);
            border: 1px dashed rgba(239, 68, 68, 0.4);
            font-size: 13px;
        }

        /* Override mermaid's default theme border that bleeds globally */
        .mermaid svg {
            max-width: 100%;
        }

        /* Prevent mermaid injected global styles from adding purple borders */
        :root {
            --mermaid-global-border-override: none;
        }
        `;

        const oldStyle = document.getElementById('viz-engine-styles');
        if (oldStyle) {
            oldStyle.remove();
        }

        const styleSheet = document.createElement('style');
        styleSheet.id = 'viz-engine-styles';
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }

    // 2.3.2
    setupLightweightObservation() {
        this.resizeObserver = new ResizeObserver((entries) => {
            if (this.animationFrameId) {
                cancelAnimationFrame(this.animationFrameId);
            }

            this.animationFrameId = requestAnimationFrame(() => {
                this.handleSimpleResize(entries);
            });
        });
    }

    // 2.3.3
    setupResponsiveDesign() {
        const mediaQueries = {
            mobile: window.matchMedia(`(max-width: ${this.options.spacing.responsiveBreakpoints.mobile}px)`),
            tablet: window.matchMedia(`(max-width: ${this.options.spacing.responsiveBreakpoints.tablet}px)`),
            desktop: window.matchMedia(`(min-width: ${this.options.spacing.responsiveBreakpoints.desktop}px)`)
        };

        Object.entries(mediaQueries).forEach(([breakpoint, mediaQuery]) => {
            mediaQuery.addEventListener('change', (e) => {
                if (e.matches) {
                    this.layoutState.responsiveBreakpoint = breakpoint;
                    this.handleBreakpointChange(breakpoint);
                }
            });

            if (mediaQuery.matches) {
                this.layoutState.responsiveBreakpoint = breakpoint;
            }
        });
    }

    // 2.3.4
    setupGlobalListeners() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleWindowResize();
            }, this.options.animations.resizeThrottle);
        });

        document.addEventListener('themeChanged', (e) => {
            this.updateTheme(e.detail.theme);
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.export-dropdown')) {
                document.querySelectorAll('.export-dropdown.open').forEach(dropdown => {
                    dropdown.classList.remove('open');
                });
            }
        });
    }

    // 2.3.5
    setupTooltipPositioning() {
        document.addEventListener('mouseover', (e) => {
            if (e.target.classList.contains('viz-action-btn')) {
                const button = e.target;
                const tooltip = window.getComputedStyle(button, '::after');

                const rect = button.getBoundingClientRect();

                const tooltipX = rect.left + (rect.width / 2);
                const tooltipY = rect.bottom + 10;

                button.style.setProperty('--tooltip-x', tooltipX + 'px');
                button.style.setProperty('--tooltip-y', tooltipY + 'px');
            }
        });
    }

    // 2.4.1
    setupJSONFileHandling() {
        document.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        document.addEventListener('drop', (e) => {
            e.preventDefault();
            const files = Array.from(e.dataTransfer.files);
            const jsonFiles = files.filter(file =>
                file.type === 'application/json' || file.name.endsWith('.json')
            );

            if (jsonFiles.length > 0) {
                this.handleJSONFiles(jsonFiles);
            }
        });
    }

    // 2.4.2
    async handleJSONFiles(files) {
        for (const file of files) {
            try {
                const content = await this.readFileAsText(file);
                const jsonData = JSON.parse(content);

                const chartType = this.detectChartType(jsonData);

                console.log(`📁 Loaded JSON file: ${file.name} as ${chartType}`);

                let container = document.querySelector('.viz-main-container');
                if (!container) {
                    container = document.createElement('div');
                    container.className = 'viz-main-container';
                    document.body.appendChild(container);
                }

                const vizContainer = this.createVisualizationContainer(chartType);
                vizContainer.setAttribute('data-source', file.name);
                container.appendChild(vizContainer);

                await this.renderVisualization({
                    type: chartType,
                    ...jsonData,
                    fileName: file.name
                }, vizContainer, `json-${Date.now()}`);

            } catch (error) {
                console.error(`Error processing ${file.name}:`, error);
            }
        }
    }

    // 2.4.3
    detectChartType(jsonData) {
        if (jsonData.data && Array.isArray(jsonData.data) && jsonData.layout) {
            return 'plotly';
        }

        if (jsonData.type && jsonData.data && (jsonData.data.labels || jsonData.data.datasets)) {
            return 'chartjs';
        }

        if (jsonData.chartType && (jsonData.data || jsonData.dataTable)) {
            return 'google';
        }

        if (Array.isArray(jsonData) && jsonData.length > 0) {
            return 'plotly';
        }

        return 'plotly';
    }

    // 2.4.4
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    /**
     * =============================================================================
     * SECTION 3: CONTENT PARSING & PROCESSING
     * =============================================================================
     */

    // 3.1.1
    parseContent(content) {
        if (!content || typeof content !== 'string') {
            return [{ type: 'text', content: 'No content available' }];
        }

        const items = [];

        const patterns = {
            plotly: /<PLOTLY>([\s\S]*?)<\/PLOTLY>/g,
            google: /<GRAPH>([\s\S]*?)<\/GRAPH>/g,
            chartjs: /<CHARTJS>([\s\S]*?)<\/CHARTJS>/g,
            mermaid: /<MERMAID>([\s\S]*?)<\/MERMAID>/g,
            plotly_curly: /\{\{PLOTLY_START\}\}([\s\S]*?)\{\{PLOTLY_END\}\}/g,
            mermaid_curly: /\{\{MERMAID_START\}\}([\s\S]*?)\{\{MERMAID_END\}\}/g,
            google_curly: /\{\{GRAPH_START\}\}([\s\S]*?)\{\{GRAPH_END\}\}/g,
            chartjs_curly: /\{\{CHARTJS_START\}\}([\s\S]*?)\{\{CHARTJS_END\}\}/g
        };

        let matches = [];

        Object.entries(patterns).forEach(([patternKey, pattern]) => {
            let match;
            pattern.lastIndex = 0;

            while ((match = pattern.exec(content)) !== null) {
                let baseType;
                if (patternKey.includes('plotly')) baseType = 'plotly';
                else if (patternKey.includes('mermaid')) baseType = 'mermaid';
                else if (patternKey.includes('google')) baseType = 'google';
                else if (patternKey.includes('chartjs')) baseType = 'chartjs';
                else baseType = patternKey;

                matches.push({
                    type: baseType,
                    content: match[1].trim(),
                    start: match.index,
                    end: match.index + match[0].length,
                    fullMatch: match[0],
                    delimiter: patternKey.includes('_curly') ? 'curly' : 'xml'
                });
            }
        });

        matches.sort((a, b) => a.start - b.start);

        let lastIndex = 0;

        matches.forEach(match => {
            if (match.start > lastIndex) {
                const textContent = content.substring(lastIndex, match.start).trim();
                if (textContent) {
                    items.push({ type: 'text', content: textContent });
                }
            }

            try {
                if (match.type === 'mermaid') {
                    items.push({
                        type: 'mermaid',
                        content: match.content,
                        delimiter: match.delimiter
                    });
                } else {
                    // SE NEW SAFE JSON PARSING
                    try {
                        const parsedContent = this.safeJSONParse(match.content);
                        items.push({
                            type: match.type,
                            ...parsedContent,
                            delimiter: match.delimiter
                        });
                    } catch (safeParseError) {
                        console.error(' Safe JSON parsing failed:', safeParseError);
                        items.push({
                            type: 'error',
                            content: `Error parsing ${match.type} visualization: ${safeParseError.message}`,
                            delimiter: match.delimiter,
                            originalContent: match.content
                        });
                    }
                }
            } catch (error) {
                console.error(` Error processing ${match.type} content:`, error);
                items.push({
                    type: 'error',
                    content: `Error processing ${match.type} visualization: ${error.message}`,
                    delimiter: match.delimiter
                });
            }

            lastIndex = match.end;
        });

        if (lastIndex < content.length) {
            const remainingText = content.substring(lastIndex).trim();
            if (remainingText) {
                items.push({ type: 'text', content: remainingText });
            }
        }

        if (matches.length === 0 && content.trim()) {
            items.push({ type: 'text', content: content.trim() });
        }

        return items;
    }

    // 3.1.2  =     isMarkdownContent(content) {  moveed to sidebar.js


    // 3.2.1
    createVisualizationContainer(type) {
        const container = document.createElement('div');
        container.className = `viz-container ${type}-container`;

        container.innerHTML = `
            <div class="viz-content-area">
                <!-- Content renders directly here -->
            </div>
        `;

        const contentArea = container.querySelector('.viz-content-area');
        this.attachResizeHandle(contentArea);

        return container;
    }

    /**
     * Build a descriptive label for a viz panel/float:
     *   "Thread Title — HH:MM"  (if both available)
     *   "Thread Title"           (if only thread title)
     *   vizType                  (fallback)
     */
    _buildVizLabel(container, vizType) {
        const parts = [];
        try {
            const tm = window.ThreadManager;
            if (tm) {
                const tid = tm.currentThreadId;
                const threads = tm.threads;
                if (tid && Array.isArray(threads)) {
                    const thread = threads.find(t => t.id === tid);
                    if (thread?.title) parts.push(thread.title);
                }
            }
        } catch (_) {}
        try {
            const msgEl = container.closest?.('.ai-message');
            if (msgEl) {
                const ts = msgEl.querySelector('.ai-message-timestamp');
                if (ts?.textContent?.trim()) parts.push(ts.textContent.trim());
            }
        } catch (_) {}
        return parts.length ? parts.join(' \u2014 ') : vizType;
    }

    /**
     * Adds a small "Float / Panel" action bar to HTML and React iframe containers.
     * Delegates to window.vizPopupManager (loaded from viz_popup_manager.js).
     * @param {HTMLElement} container   - The .viz-container div
     * @param {HTMLElement} contentArea - The .viz-content-area div (contains the iframe)
     * @param {string}      chartId     - Unique chart id
     * @param {string}      vizType     - Display label used to build the popup header title
     */
    addIframeActionBar(container, contentArea, chartId, vizType = 'Widget') {
        if (!container || container.querySelector('.viz-iframe-action-bar')) return;

        // Derive a human-readable label from thread title + message timestamp
        const label = this._buildVizLabel(container, vizType);

        const bar = document.createElement('div');
        bar.className = 'viz-action-bar viz-iframe-action-bar';
        bar.style.cssText = `
            display: flex;
            gap: 4px;
            padding: 4px 10px;
            justify-content: flex-end;
            border-top: 1px solid var(--border-color, #333);
            background: var(--bg-secondary, #1e1e2e);
        `;
        bar.innerHTML = `
            <button class="viz-action-btn" title="Open in side panel">&#x229F;</button>
            <button class="viz-action-btn" title="Open as floating window">&#x229E;</button>
            <button class="viz-action-btn viz-tier1-trigger" title="Export, save, and more (Tier 1)">&#x22EE;</button>
        `;

        const btns = bar.querySelectorAll('.viz-action-btn');
        const panelBtn = btns[0];
        const floatBtn = btns[1];
        const kebabBtn = btns[2];

        panelBtn.addEventListener('click', () => {
            if (window.vizPopupManager) {
                window.vizPopupManager.openPanel(contentArea, chartId, label);
            }
        });
        floatBtn.addEventListener('click', () => {
            if (window.vizPopupManager) {
                window.vizPopupManager.openFloat(contentArea, chartId, label);
            }
        });

        // Tier-1 toolbar (PNG / PDF / CSV / Copy / Fullscreen / Save)
        // Derive the iframe from contentArea; the wrapper owns the lifecycle.
        const iframe = contentArea?.querySelector?.('iframe') || null;
        if (kebabBtn && iframe) {
            this.addIframeTier1Toolbar(container, contentArea, chartId, iframe, kebabBtn);
        }

        container.appendChild(bar);
    }

    /**
     * Tier-1 toolbar — kebab popover with PNG / PDF / CSV / Copy / Fullscreen / Save.
     *
     * Communication:
     *   parent -> child : { type: 'iframe-export-svg', id: chartId }
     *   parent -> child : { type: 'iframe-export-data', id: chartId }
     *   child  -> parent: { type: 'iframe-svg', id: chartId, svg: string|null }
     *   child  -> parent: { type: 'iframe-data', id: chartId, payload: object|null }
     *
     * The renderer-side hook (window.__REACT_RENDERER__) is installed by
     * react_renderer.js; it serialises the first <svg> by default and reads
     * window.__EXPORT_DATA__ when present.
     *
     * No emoji in source literals (CLAUDE.md §5) — FontAwesome classes only.
     */
    addIframeTier1Toolbar(container, contentArea, chartId, iframe, kebabBtn) {
        if (!container || !iframe || kebabBtn.dataset.tier1Wired === '1') return;
        kebabBtn.dataset.tier1Wired = '1';

        // Build popover (appended to <body> so absolute positioning is reliable).
        const popover = document.createElement('div');
        popover.className = 'viz-tier1-popover';
        popover.setAttribute('role', 'menu');
        popover.style.cssText = [
            'position: absolute',
            'z-index: 9999',
            'display: none',
            'min-width: 200px',
            'padding: 6px',
            'background: var(--bg-secondary, #1e1e2e)',
            'border: 1px solid var(--border-color, #333)',
            'border-radius: 8px',
            'box-shadow: 0 8px 24px rgba(0,0,0,0.35)',
            'color: var(--text-primary, #e6e6e6)',
            'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            'font-size: 13px',
        ].join(';');

        // 6 actions — FontAwesome classes only (no emoji in source literals).
        const actions = [
            { id: 'png',        label: 'Export PNG',        iconClass: 'fas fa-image'      },
            { id: 'pdf',        label: 'Export PDF',        iconClass: 'fas fa-file-pdf'   },
            { id: 'csv',        label: 'Export CSV',        iconClass: 'fas fa-file-csv'   },
            { id: 'copy',       label: 'Copy image',        iconClass: 'fas fa-copy'       },
            { id: 'fullscreen', label: 'Fullscreen',        iconClass: 'fas fa-expand'     },
            { id: 'save',       label: 'Save to library',   iconClass: 'fas fa-bookmark'   },
        ];

        popover.innerHTML = actions.map(a => `
            <button class="viz-tier1-action" data-action="${a.id}" role="menuitem"
                    style="display:flex;align-items:center;gap:8px;width:100%;
                           padding:8px 10px;border:0;background:transparent;
                           color:inherit;text-align:left;cursor:pointer;
                           border-radius:6px;font:inherit;">
                <i class="${a.iconClass}" style="width:16px;display:inline-block;
                   text-align:center;flex:0 0 16px;"></i>
                <span>${a.label}</span>
            </button>
        `).join('');

        // Hover style for popover buttons (one-shot, idempotent).
        if (!document.getElementById('viz-tier1-popover-styles')) {
            const style = document.createElement('style');
            style.id = 'viz-tier1-popover-styles';
            style.textContent = `
                .viz-tier1-popover .viz-tier1-action:hover { background: rgba(88,166,255,0.12); }
                .viz-tier1-popover .viz-tier1-action:focus  { outline: 2px solid rgba(88,166,255,0.5); outline-offset: -2px; }
                .viz-tier1-trigger[aria-expanded="true"]    { background: rgba(88,166,255,0.18); }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(popover);

        const closePopover = () => {
            popover.style.display = 'none';
            kebabBtn.setAttribute('aria-expanded', 'false');
        };

        const openPopover = () => {
            // Anchor to kebab button's bounding rect.
            const rect = kebabBtn.getBoundingClientRect();
            const popW = 208; // approx; allow a bit of width for the labels
            const popH = actions.length * 36 + 12;
            let top = rect.bottom + 6 + window.scrollY;
            let left = rect.right - popW + window.scrollX;
            // Keep on-screen
            const maxLeft = window.scrollX + window.innerWidth - popW - 8;
            if (left > maxLeft) left = maxLeft;
            if (left < window.scrollX + 8) left = window.scrollX + 8;
            const maxTop = window.scrollY + window.innerHeight - popH - 8;
            if (top > maxTop) top = rect.top - popH - 6 + window.scrollY;
            popover.style.top = `${Math.max(8, top)}px`;
            popover.style.left = `${Math.max(8, left)}px`;
            popover.style.display = 'block';
            kebabBtn.setAttribute('aria-expanded', 'true');
        };

        kebabBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (popover.style.display === 'block') {
                closePopover();
            } else {
                openPopover();
            }
        });

        // Close on outside click / Escape.
        const onDocClick = (ev) => {
            if (popover.style.display !== 'block') return;
            if (popover.contains(ev.target) || kebabBtn.contains(ev.target)) return;
            closePopover();
        };
        const onKey = (ev) => {
            if (ev.key === 'Escape' && popover.style.display === 'block') {
                closePopover();
                kebabBtn.focus();
            }
        };
        document.addEventListener('click', onDocClick);
        document.addEventListener('keydown', onKey);

        // Click handlers (delegated).
        popover.addEventListener('click', async (ev) => {
            const btn = ev.target.closest('.viz-tier1-action');
            if (!btn) return;
            const action = btn.dataset.action;
            closePopover();
            try {
                await this._runTier1Action(action, {
                    container, contentArea, chartId, iframe,
                });
            } catch (err) {
                console.error('[viz-tier1] action failed:', action, err);
                this._tier1Toast(`Action "${action}" failed: ${err?.message || err}`, 'error');
            }
        });

        // Track lifecycle so we can clean up if the container is removed.
        container.addEventListener('DOMNodeRemoved', () => {
            document.removeEventListener('click', onDocClick);
            document.removeEventListener('keydown', onKey);
            if (popover.parentNode) popover.parentNode.removeChild(popover);
        });
    }

    /**
     * Dispatch a single Tier-1 action. All actions are async; errors surface
     * via showToast. Keep this method small — split out the heavy helpers
     * below so each is reviewable on its own.
     */
    async _runTier1Action(action, ctx) {
        const { chartId, iframe, container } = ctx;
        switch (action) {
            case 'png':        return this._tier1ExportPng(iframe, chartId, container);
            case 'pdf':        return this._tier1ExportPdf(iframe, chartId);
            case 'csv':        return this._tier1ExportCsv(iframe, chartId);
            case 'copy':       return this._tier1CopyImage(iframe, chartId, container);
            case 'fullscreen': return this._tier1Fullscreen(iframe);
            case 'save':       return this._tier1Save(iframe, chartId, container);
            default:           throw new Error(`Unknown action: ${action}`);
        }
    }

    /**
     * Resolve an iframe-export-* request and resolve with the matching
     * child->parent reply. Each request gets a unique nonce so multiple
     * in-flight exports can co-exist.
     */
    _tier1Request(iframe, chartId, type, timeoutMs = 5000) {
        return new Promise((resolve, reject) => {
            const nonce = `${chartId}:${type}:${Date.now()}:${Math.random().toString(36).slice(2, 8)}`;
            const onMessage = (ev) => {
                if (!ev.data || typeof ev.data !== 'object') return;
                if (ev.source !== iframe.contentWindow) return;
                const replyType = type === 'iframe-export-svg' ? 'iframe-svg' : 'iframe-data';
                if (ev.data.type !== replyType) return;
                if (ev.data.id !== chartId) return;
                window.removeEventListener('message', onMessage);
                clearTimeout(timer);
                resolve(ev.data);
            };
            const timer = setTimeout(() => {
                window.removeEventListener('message', onMessage);
                reject(new Error(`Timeout waiting for ${type} reply from chart ${chartId}`));
            }, timeoutMs);
            window.addEventListener('message', onMessage);
            try {
                iframe.contentWindow.postMessage({ type, id: chartId, nonce }, '*');
            } catch (err) {
                window.removeEventListener('message', onMessage);
                clearTimeout(timer);
                reject(err);
            }
        });
    }

    /**
     * Rasterise an SVG string on a parent-side canvas and return a PNG Blob.
     * Falls back to JPEG if the canvas becomes tainted (foreignObject images).
     */
    async _tier1SvgToBlob(svgString) {
        if (!svgString) throw new Error('Empty SVG payload from chart');
        // Parse the SVG to honour viewBox / width / height if present.
        const parser = new DOMParser();
        const doc = parser.parseFromString(svgString, 'image/svg+xml');
        const svg = doc.documentElement;
        const w = parseFloat(svg.getAttribute('width')) || 1200;
        const h = parseFloat(svg.getAttribute('height')) || 800;
        const blobIn = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(blobIn);
        try {
            const img = await new Promise((resolve, reject) => {
                const i = new Image();
                i.onload = () => resolve(i);
                i.onerror = () => reject(new Error('SVG image failed to load'));
                i.src = url;
            });
            const canvas = document.createElement('canvas');
            // 2x for crisper exports.
            const scale = Math.min(2, Math.max(1, window.devicePixelRatio || 1));
            canvas.width = Math.round(w * scale);
            canvas.height = Math.round(h * scale);
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = getComputedStyle(document.body).backgroundColor || '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            return await new Promise((resolve) => {
                canvas.toBlob((b) => resolve(b), 'image/png');
            });
        } finally {
            URL.revokeObjectURL(url);
        }
    }

    _tier1Toast(message, type = 'info') {
        try {
            if (typeof window.showToast === 'function') {
                window.showToast(message, type);
                return;
            }
        } catch (_) { /* fall through */ }
        console.log(`[viz-tier1] (${type}) ${message}`);
    }

    async _tier1ExportPng(iframe, chartId, container) {
        const reply = await this._tier1Request(iframe, chartId, 'iframe-export-svg');
        const blob = await this._tier1SvgToBlob(reply.svg);
        if (!blob) throw new Error('Canvas rasterisation returned empty blob');
        this._tier1TriggerDownload(blob, `viz-${chartId}.png`);
        // Side-effect: persist as thumbnail if this iframe has a saved snapshot.
        const snapshotId = container?.dataset?.vizSnapshotId || container?.getAttribute?.('data-viz-snapshot-id');
        if (snapshotId) {
            this._tier1UploadThumbnail(snapshotId, blob).catch((err) => {
                console.warn('[viz-tier1] thumbnail upload failed:', err);
            });
        }
        this._tier1Toast(`Exported ${chartId}.png`, 'success');
    }

    async _tier1UploadThumbnail(snapshotId, pngBlob) {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken') || '';
        const reader = new FileReader();
        const dataUrl = await new Promise((resolve, reject) => {
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(reader.error);
            reader.readAsDataURL(pngBlob);
        });
        const base64 = String(dataUrl).split(',', 2)[1] || '';
        const resp = await fetch(`/api/viz/snapshots/${encodeURIComponent(snapshotId)}/thumbnail`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : '',
            },
            body: JSON.stringify({ png_base64: base64 }),
        });
        if (!resp.ok) {
            const text = await resp.text().catch(() => '');
            throw new Error(`HTTP ${resp.status}: ${text.slice(0, 120)}`);
        }
        return resp.json().catch(() => ({}));
    }

    async _tier1ExportPdf(iframe, chartId) {
        const reply = await this._tier1Request(iframe, chartId, 'iframe-export-svg');
        // V1: open print dialog with the SVG embedded in an HTML wrapper.
        // V2 may swap to jsPDF for true file output (see hand-off doc).
        const html = `<!doctype html><html><head><meta charset="utf-8"><title>viz-${chartId}</title>
<style>html,body{margin:0;padding:24px;background:#fff;color:#111;
font-family:-apple-system,BlinkMacSystemFont,sans-serif;}
svg{max-width:100%;height:auto;display:block;margin:0 auto;}</style>
</head><body>${reply.svg || '<p>(no SVG returned)</p>'}
<script>window.addEventListener('load',()=>{setTimeout(()=>{window.print();},200);});</script>
</body></html>`;
        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const w = window.open(url, '_blank', 'noopener,noreferrer');
        if (!w) {
            // Popup blocked — fall back to a same-tab data URL the user can
            // right-click -> Print on.
            window.location.href = url;
            this._tier1Toast('Popup blocked — opening in same tab. Use Print.', 'info');
        } else {
            this._tier1Toast('Opening print dialog…', 'success');
        }
        // Revoke later (give the new window time to load).
        setTimeout(() => URL.revokeObjectURL(url), 60000);
    }

    async _tier1ExportCsv(iframe, chartId) {
        const reply = await this._tier1Request(iframe, chartId, 'iframe-export-data');
        const payload = reply.payload || {};
        if (payload.error) {
            throw new Error(`Chart did not expose data: ${payload.error}`);
        }
        const csv = this._tier1BuildCsv(payload);
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
        this._tier1TriggerDownload(blob, `viz-${chartId}.csv`);
        this._tier1Toast(`Exported ${chartId}.csv`, 'success');
    }

    _tier1BuildCsv(payload) {
        // Accept either a flat rows array or {labels, series} shape.
        if (Array.isArray(payload.rows)) {
            return payload.rows.map((r) => Array.isArray(r) ? r.join(',') : JSON.stringify(r)).join('\n');
        }
        const labels = Array.isArray(payload.labels) ? payload.labels : [];
        const series = Array.isArray(payload.series) ? payload.series : [];
        const header = ['label', ...series.map((s) => s?.name || 'series')];
        const lines = [header.join(',')];
        labels.forEach((lbl, i) => {
            const row = [lbl, ...series.map((s) => {
                const v = Array.isArray(s?.data) ? s.data[i] : (s?.data?.[i] ?? '');
                return typeof v === 'number' ? v : JSON.stringify(v ?? '');
            })];
            lines.push(row.join(','));
        });
        return lines.join('\n');
    }

    async _tier1CopyImage(iframe, chartId, container) {
        if (!navigator.clipboard || typeof navigator.clipboard.write !== 'function') {
            throw new Error('Clipboard image write not supported in this browser');
        }
        const reply = await this._tier1Request(iframe, chartId, 'iframe-export-svg');
        const blob = await this._tier1SvgToBlob(reply.svg);
        if (!blob) throw new Error('Canvas rasterisation returned empty blob');
        await navigator.clipboard.write([
            new ClipboardItem({ 'image/png': blob }),
        ]);
        this._tier1Toast('Image copied to clipboard', 'success');
        // Same side-effect as PNG export.
        const snapshotId = container?.dataset?.vizSnapshotId || container?.getAttribute?.('data-viz-snapshot-id');
        if (snapshotId) {
            this._tier1UploadThumbnail(snapshotId, blob).catch((err) => {
                console.warn('[viz-tier1] thumbnail upload failed:', err);
            });
        }
    }

    async _tier1Fullscreen(iframe) {
        if (typeof iframe.requestFullscreen === 'function') {
            await iframe.requestFullscreen();
            return;
        }
        // WebKit/legacy fallbacks
        if (typeof iframe.webkitRequestFullscreen === 'function') {
            iframe.webkitRequestFullscreen();
            return;
        }
        throw new Error('Fullscreen API not available in this browser');
    }

    async _tier1Save(iframe, chartId, container) {
        // 1. Prompt for title + tags.
        const existing = container?.dataset?.vizSnapshotId
            || container?.getAttribute?.('data-viz-snapshot-id')
            || '';
        const defaultTitle = container?.dataset?.vizTitle || `Visualization ${chartId}`;
        const title = (window.prompt('Save visualization — title?', defaultTitle) || '').trim();
        if (!title) return;
        const tagsRaw = (window.prompt('Tags (comma-separated, optional)', '') || '').trim();
        const tags = tagsRaw ? tagsRaw.split(',').map((t) => t.trim()).filter(Boolean) : [];

        // 2. Extract JSX from iframe.srcdoc.
        const srcdoc = iframe.getAttribute('src') === 'about:blank' ? '' : (iframe.srcdoc || '');
        const jsx_source = this._tier1ExtractJsx(srcdoc);
        if (!jsx_source) {
            throw new Error('Could not extract JSX from iframe. Re-render the chart and try again.');
        }
        const css_source = this._tier1ExtractCss(srcdoc);

        // 3. Heuristics for what the chart uses.
        const uses_lucide = /lucide/i.test(srcdoc);
        const uses_recharts = /recharts/i.test(srcdoc);
        const uses_tailwind = /tailwind/i.test(srcdoc);

        // 4. POST or PATCH depending on existing id.
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken') || '';
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : '',
        };
        if (existing) {
            const resp = await fetch(`/api/viz/snapshots/${encodeURIComponent(existing)}`, {
                method: 'PATCH',
                headers,
                body: JSON.stringify({ title, tags, css_source }),
            });
            if (!resp.ok) {
                const t = await resp.text().catch(() => '');
                throw new Error(`Update failed (${resp.status}): ${t.slice(0, 160)}`);
            }
            this._tier1Toast(`Updated "${title}"`, 'success');
            return;
        }
        const resp = await fetch('/api/viz/snapshots/', {
            method: 'POST',
            headers,
            body: JSON.stringify({
                title,
                jsx_source,
                css_source,
                tags,
                uses_lucide,
                uses_recharts,
                uses_tailwind,
            }),
        });
        if (!resp.ok) {
            const t = await resp.text().catch(() => '');
            throw new Error(`Create failed (${resp.status}): ${t.slice(0, 160)}`);
        }
        const body = await resp.json().catch(() => ({}));
        const newId = body?.id || body?.snapshot?.id;
        if (newId && container) {
            container.setAttribute('data-viz-snapshot-id', newId);
            container.dataset.vizSnapshotId = newId;
            container.dataset.vizTitle = title;
        }
        this._tier1Toast(`Saved "${title}" to library`, 'success');
    }

    /**
     * Strip react_renderer.js's HTML wrapper down to the user-authored JSX.
     * Looks for a <script type="text/babel"> block that contains the App
     * component, then returns the body between the first top-level `function App`
     * / `const App =` / `class App` and the matching closing brace (best-effort).
     */
    _tier1ExtractJsx(srcdoc) {
        if (!srcdoc) return '';
        const babelMatch = srcdoc.match(/<script[^>]*type=["']text\/babel["'][^>]*>([\s\S]*?)<\/script>/i);
        if (!babelMatch) return '';
        const body = babelMatch[1];
        // Find the start of App definition; stop at the ReactDOM.createRoot
        // call which is the renderer wrapper's own code.
        const startPatterns = [
            /\bfunction\s+App\s*\(/,
            /\bconst\s+App\s*=/,
            /\bclass\s+App\s+/,
            /\bfunction\s+Chart\s*\(/,
            /\bconst\s+Chart\s*=/,
        ];
        let startIdx = -1;
        for (const p of startPatterns) {
            const m = body.search(p);
            if (m !== -1) { startIdx = m; break; }
        }
        if (startIdx === -1) return body.trim();
        // Cut at ReactDOM.createRoot or ReactDOM.render (renderer marker).
        const endMatch = body.slice(startIdx).match(/ReactDOM\.(createRoot|render)\s*\(/);
        const endIdx = endMatch ? startIdx + endMatch.index : -1;
        const trimmed = endIdx > startIdx ? body.slice(startIdx, endIdx).trim() : body.slice(startIdx).trim();
        return trimmed;
    }

    /**
     * Optional <style> block inside the srcdoc — used as css_source on the
     * saved snapshot so re-mounts render identically.
     */
    _tier1ExtractCss(srcdoc) {
        if (!srcdoc) return '';
        const m = srcdoc.match(/<style[^>]*>([\s\S]*?)<\/style>/i);
        return m ? m[1].trim() : '';
    }

    _tier1TriggerDownload(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 0);
    }

    attachResizeHandle(contentArea) {
        if (!contentArea) return;

        const minHeight = Math.max(parseInt(contentArea.dataset.minHeight || '0', 10) || 320, 200);
        const existingHandle = contentArea.querySelector('.viz-resize-handle');
        if (existingHandle) {
            existingHandle.remove();
        }

        const handle = document.createElement('div');
        handle.className = 'viz-resize-handle';
        contentArea.appendChild(handle);

        let startY = 0;
        let startHeight = 0;
        const container = contentArea.closest('.viz-container');

        const endResize = (event) => {
            document.removeEventListener('pointermove', updateHeight);
            document.removeEventListener('pointerup', endResize);
            document.removeEventListener('pointercancel', endResize);
            contentArea.classList.remove('is-resizing');
            if (event && handle.releasePointerCapture) {
                try {
                    handle.releasePointerCapture(event.pointerId);
                } catch (_) { }
            }
            const target = container || contentArea;
            if (typeof window.ensurePlotlyResponsive === 'function') {
                window.ensurePlotlyResponsive(target);
            }
        };

        const updateHeight = (event) => {
            const delta = event.clientY - startY;
            const newHeight = Math.max(minHeight, startHeight + delta);
            contentArea.style.height = `${newHeight}px`;
            contentArea.dataset.manualHeight = String(newHeight);
            if (container) {
                this.updateSingleContainerSize(container);
            }
        };

        handle.addEventListener('pointerdown', (event) => {
            event.preventDefault();
            startY = event.clientY;
            startHeight = contentArea.getBoundingClientRect().height;
            contentArea.classList.add('is-resizing');
            if (handle.setPointerCapture) {
                try {
                    handle.setPointerCapture(event.pointerId);
                } catch (_) { }
            }
            document.addEventListener('pointermove', updateHeight);
            document.addEventListener('pointerup', endResize);
            document.addEventListener('pointercancel', endResize);
        });
    }

    // 3.2.2
    createInlineContainer(type) {
        const container = document.createElement('div');
        container.className = `viz-container ${type}-container`;

        if (type === 'text') {
            container.style.position = 'relative';
            container.style.display = 'block';
            container.style.width = '100%';
            container.style.margin = `${this.options.spacing.visualizationMargin}px 0`;
            container.style.textAlign = 'left';
        } else {
            container.style.position = 'relative';
            container.style.display = 'flex';
            container.style.flexDirection = 'column';
            container.style.alignItems = 'center';
            container.style.justifyContent = 'center';
            container.style.width = '100%';
            container.style.margin = `${this.options.spacing.visualizationMargin}px 0`;
        }

        return container;
    }

    // 3.2.3
    cleanupContainer(container) {
        try {
            const chartsToRemove = [];
            this.charts.forEach((chart, chartId) => {
                if (chart.container === container || container.contains(chart.container)) {
                    chartsToRemove.push(chartId);
                }
            });

            chartsToRemove.forEach(chartId => {
                const chart = this.charts.get(chartId);
                if (chart && chart.type === 'plotly' && window.Plotly) {
                    try {
                        const plotlyDiv = document.getElementById(chartId);
                        if (plotlyDiv && plotlyDiv._plotly_plots) {
                            window.Plotly.purge(plotlyDiv);
                        }
                    } catch (e) {
                        console.warn('Warning cleaning up Plotly chart:', e);
                    }
                }
                this.charts.delete(chartId);
            });
        } catch (error) {
            console.error('Error cleaning up container:', error);
        }
    }

    // 3.3.1
    enableStreamingMode(container) {
        if (container) {
            container.setAttribute('data-streaming', 'true');
            console.log('🔄 Streaming mode enabled for container:', container.id);
        }
    }

    // 3.3.2
    disableStreamingMode(container) {
        if (container) {
            container.removeAttribute('data-streaming');
            console.log('⏹️ Streaming mode disabled for container:', container.id);
        }
    }

    // 3.3.3
    isStreamingMode(container) {
        return container && container.hasAttribute('data-streaming');
    }

    // 3.3.4
    clearContentHashes(container) {
        if (container) {
            const vizContainers = container.querySelectorAll('.viz-container[data-content-hash]');
            vizContainers.forEach(vizContainer => {
                vizContainer.removeAttribute('data-content-hash');
            });
            console.log(`🧹 Cleared ${vizContainers.length} content hashes`);
        }
    }

    // 3.3.5
    getExistingContainerStates(container) {
        const states = [];
        const existingVizContainers = container.querySelectorAll('.viz-container');

        existingVizContainers.forEach((vizContainer, index) => {
            const contentArea = vizContainer.querySelector('.viz-content-area');
            const contentHash = vizContainer.getAttribute('data-content-hash');
            const vizType = vizContainer.className.match(/(\w+)-container/)?.[1];

            states.push({
                index,
                container: vizContainer,
                contentHash,
                type: vizType,
                hasContent: !!contentArea?.innerHTML.trim()
            });
        });

        return states;
    }

    // 3.3.6
    createIncrementalRenderPlan(newItems, existingStates) {
        const plan = {
            newItems: [],
            existingItems: [],
            updatedItems: []
        };

        let vizIndex = 0;

        newItems.forEach((item, itemIndex) => {
            if (item.type === 'text') {
                plan.newItems.push(item);
                return;
            }

            const newHash = this.generateContentHash(item);
            const existingState = existingStates[vizIndex];

            if (!existingState) {
                plan.newItems.push(item);
            } else if (existingState.contentHash === newHash) {
                plan.existingItems.push({
                    item,
                    existingState,
                    action: 'skip'
                });
                console.log(`⏭️ Skipping already rendered ${item.type} (hash: ${newHash})`);
            } else if (existingState.contentHash !== newHash) {
                plan.updatedItems.push({
                    ...item,
                    oldHash: existingState.contentHash,
                    newHash
                });
                console.log(`🔄 Content changed for ${item.type} (${existingState.contentHash} → ${newHash})`);
            } else {
                plan.newItems.push(item);
            }

            vizIndex++;
        });

        return plan;
    }

    // 3.3.7
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
     * =============================================================================
     * SECTION 4: MAIN RENDERING SYSTEM
     * =============================================================================
     */

    // 4.1.1
    async renderAll(content, container, options = {}) {
        if (!container) {
            throw new Error('Container element is required');
        }

        const containerId = container.id || `container-${Date.now()}`;
        if (!container.id) {
            container.id = containerId;
        }

        const renderingKey = `rendering-${containerId}`;
        if (container.hasAttribute('data-rendering') || this.activeRenders?.has(renderingKey)) {
            console.warn(' Render already in progress for container:', containerId);
            return;
        }

        if (!this.activeRenders) {
            this.activeRenders = new Set();
        }
        this.activeRenders.add(renderingKey);
        container.setAttribute('data-rendering', 'true');

        try {
            await this.init();
            const newItems = this.parseContent(content);

            const isStreaming = options.streaming || container.hasAttribute('data-streaming');

            console.log(`🎯 RenderAll: ${isStreaming ? 'STREAMING' : 'FULL'} mode for ${containerId} with ${newItems.length} items`);

            if (isStreaming) {
                console.log(`🔄 Smart streaming render: ${newItems.length} items for ${containerId}`);
                await this.renderItemsIncrementally(newItems, container, containerId);
            } else {
                console.log(`🎯 Full render: ${newItems.length} items for ${containerId}`);
                this.cleanupContainer(container);
                container.innerHTML = '';
                await this.renderItemsDirectly(newItems, container, containerId);
            }

            if (this.resizeObserver) {
                this.resizeObserver.observe(container);
            }

            console.log(`endered ${newItems.length} items successfully in ${containerId} (${isStreaming ? 'streaming' : 'full'} mode)`);

        } catch (error) {
            console.error(' Error rendering visualizations:', error);
            this.showError(container, error.message);
            throw error;
        } finally {
            container.removeAttribute('data-rendering');
            this.activeRenders?.delete(renderingKey);
        }
    }

    // 4.1.2
    async renderItemsDirectly(items, container, containerId) {
        for (let i = 0; i < items.length; i++) {
            try {
                const item = items[i];

                if (item.type === 'text') {
                    // IXED: Use renderEnhancedMarkdown directly
                    await this.renderTextUsingEnhancedMarkdown(item, container);
                } else {
                    const vizContainer = this.createVisualizationContainer(item.type);
                    if (item.delimiter) {
                        vizContainer.setAttribute('data-delimiter', item.delimiter);
                    }
                    container.appendChild(vizContainer);

                    await this.renderVisualizationDirectly(item, vizContainer, `${containerId}-${i}`);
                }
            } catch (error) {
                console.error(` Error rendering item ${i}:`, error);

                // MPROVED: Continue rendering other items even if one fails
                const errorContainer = document.createElement('div');
                errorContainer.style.cssText = `
                    margin: 8px 0;
                    padding: 12px;
                    border: 1px solid var(--accent-red);
                    border-radius: 6px;
                    background: rgba(248, 81, 73, 0.1);
                    color: var(--accent-red);
                    font-size: 12px;
                `;
                errorContainer.innerHTML = `
                    <strong>⚠️ Rendering Error:</strong><br>
                    ${error.message}
                `;
                container.appendChild(errorContainer);
            }
        }
    }

    // 4.1.3
    async renderItemsIncrementally(newItems, container, containerId) {
        const existingContainers = this.getExistingContainerStates(container);
        const renderPlan = this.createIncrementalRenderPlan(newItems, existingContainers);

        console.log(`📊 Incremental render plan:`, {
            total: newItems.length,
            new: renderPlan.newItems.length,
            existing: renderPlan.existingItems.length,
            updated: renderPlan.updatedItems.length
        });

        for (const item of renderPlan.newItems) {
            if (item.type === 'text') {
                // IXED: Use renderEnhancedMarkdown directly
                await this.renderTextUsingEnhancedMarkdown(item, container);
            } else {
                const vizContainer = this.createVisualizationContainer(item.type);
                if (item.delimiter) {
                    vizContainer.setAttribute('data-delimiter', item.delimiter);
                }
                vizContainer.setAttribute('data-content-hash', this.generateContentHash(item));
                container.appendChild(vizContainer);

                await this.renderVisualizationDirectly(item, vizContainer, `${containerId}-${Date.now()}`);
            }
        }

        for (const item of renderPlan.updatedItems) {
            const existingContainer = container.querySelector(`[data-content-hash="${item.oldHash}"]`);
            if (existingContainer) {
                console.log(`🔄 Updating existing ${item.type} container`);
                const newHash = this.generateContentHash(item);
                existingContainer.setAttribute('data-content-hash', newHash);

                const contentArea = existingContainer.querySelector('.viz-content-area');
                if (contentArea) {
                    contentArea.innerHTML = '';
                    await this.renderVisualizationDirectly(item, existingContainer, `${containerId}-updated-${Date.now()}`);
                }
            }
        }
    }

    // 4.1.4
    async renderVisualizationDirectly(item, container, chartId) {
        // 🔥 FIX (Jan 21, 2026): Only validate container exists, not DOM attachment
        // Container may not be in DOM during initial message rendering
        if (!container) {
            throw new Error('Container is null - cannot render visualization');
        }
        
        // Log but don't fail if container not in DOM yet
        if (!document.contains(container)) {
            console.log('⚠️ VIZ-V3: Container not in DOM yet (will be attached after message rendering)');
        }

        let contentArea = container.querySelector('.viz-content-area');

        // RITICAL: Ensure content area exists - create it if missing (fallback for containers built externally)
        if (!contentArea) {
            console.warn('⚠️ VIZ-V3: .viz-content-area missing from container, creating fallback');
            contentArea = document.createElement('div');
            contentArea.className = 'viz-content-area';
            contentArea.style.cssText = 'width:100%;height:auto;min-height:0;';
            container.appendChild(contentArea);
        }

        this.attachResizeHandle(contentArea);

        try {
            // Use modular renderers for new visualization types
            switch (item.type) {
                case 'plotly':
                    await this.renderPlotlyDirectly(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'google':
                    await this.renderGoogleChartDirectly(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'chartjs':
                    await this.renderChartJSDirectly(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'mermaid':
                    await this.renderMermaidDirectly(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'apexcharts':
                    // Delegate to modular ApexCharts renderer
                    if (!this.apexchartsRenderer) {
                        // Wait for renderer to load if not ready
                        await this.waitForRenderer('ApexChartsRenderer', 'apexcharts_renderer.js');
                        this.apexchartsRenderer = new window.ApexChartsRenderer(this);
                    }
                    await this.apexchartsRenderer.render(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'lottie':
                    // Delegate to modular Lottie renderer
                    if (!this.lottieRenderer) {
                        // Wait for renderer to load if not ready
                        await this.waitForRenderer('LottieRenderer', 'lottie_renderer.js');
                        this.lottieRenderer = new window.LottieRenderer(this);
                    }
                    await this.lottieRenderer.render(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'gsap':
                    // Delegate to modular GSAP renderer
                    if (!this.gsapRenderer) {
                        // Wait for renderer to load if not ready
                        await this.waitForRenderer('GSAPRenderer', 'gsap_renderer.js');
                        this.gsapRenderer = new window.GSAPRenderer(this);
                    }
                    await this.gsapRenderer.render(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'cad':
                case 'blueprint':
                    // Delegate to modular CAD renderer (handles CAD and BLUEPRINT)
                    if (!this.cadRenderer) {
                        // Wait for renderer to load if not ready
                        await this.waitForRenderer('CADRenderer', 'cad_renderer.js');
                        this.cadRenderer = new window.CADRenderer(this);
                    }
                    await this.cadRenderer.render(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'schematic':
                    // Delegate to modular Schematic renderer
                    if (!this.schematicRenderer) {
                        // Wait for renderer to load if not ready
                        await this.waitForRenderer('SchematicRenderer', 'schematic_renderer.js');
                        this.schematicRenderer = new window.SchematicRenderer(this);
                    }
                    await this.schematicRenderer.render(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'molecule':
                case 'svg':
                    // Delegate to modular SVG renderer
                    if (!this.svgRenderer) {
                        await this.waitForRenderer('SVGRenderer', 'svg_renderer.js');
                        this.svgRenderer = new window.SVGRenderer(this);
                    }
                    await this.svgRenderer.render(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'latex':
                    // Delegate to modular LaTeX renderer
                    if (!this.latexRenderer) {
                        await this.waitForRenderer('LatexRenderer', 'latex_renderer.js');
                        this.latexRenderer = new window.LatexRenderer(this);
                    }
                    await this.latexRenderer.render(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'html':
                case 'execute_html':
                    // Delegate to modular HTML renderer
                    if (!this.htmlRenderer) {
                        await this.waitForRenderer('HTMLRenderer', 'html_renderer.js');
                        this.htmlRenderer = new window.HTMLRenderer(this);
                    }
                    await this.htmlRenderer.render(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'react':
                case 'execute_react':
                    // Delegate to modular React renderer (Babel + UMD globals, no build step)
                    if (!this.reactRenderer) {
                        await this.waitForRenderer('ReactRenderer', 'react_renderer.js');
                        this.reactRenderer = new window.ReactRenderer(this);
                    }
                    await this.reactRenderer.render(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'threejs':
                    // Delegate to modular Three.js renderer
                    if (!this.threejsRenderer) {
                        await this.waitForRenderer('ThreeJSRenderer', 'threejs_renderer.js');
                        this.threejsRenderer = new window.ThreeJSRenderer(this);
                    }
                    await this.threejsRenderer.render(item, contentArea, chartId);
                    this.addIframeActionBar(container, contentArea, chartId, 'Visualisation Viewer');
                    break;
                case 'error':
                    this.showErrorDirectly(contentArea, item.content);
                    break;
                default:
                    throw new Error(`Unknown visualization type: ${item.type}`);
            }

            const chartRecord = {
                item,
                container,
                type: item.type,
                plotlyData: item.__normalizedPlotlyData
                    ? JSON.parse(JSON.stringify(item.__normalizedPlotlyData))
                    : null,
                createdAt: Date.now()
            };

            this.charts.set(chartId, chartRecord);

        } catch (error) {
            console.error(`Error rendering ${item.type}:`, error);
            this.showErrorDirectly(contentArea, `Error rendering ${item.type}: ${error.message}`);
        }
    }

    // EW: Simple wrapper to use renderEnhancedMarkdown consistently
    async renderTextUsingEnhancedMarkdown(item, container) {
        let content = item.content;

        //  LEGACY renderEnhancedMarkdown COMMENTED OUT - Use triple_agent clean markdown
        // if (window && typeof window.renderEnhancedMarkdown === 'function') {
        //     content = window.renderEnhancedMarkdown(content);
        // } else {
        //     console.warn('renderEnhancedMarkdown not available, using fallback');
        //     // Simple fallback that matches the streaming logic
        //     content = content.replace(/\n{3,}/g, '\n\n')
        //                     .replace(/\n\n/g, '<br><br>')
        //                     .replace(/\n/g, '<br>');
        // }

        // SE TRIPLE-AGENT CLEAN MARKDOWN (NO EXTRA LINE BREAKS)
        if (window.marked && typeof window.marked.parse === 'function') {
            content = window.marked.parse(content);
            // Apply cleanMarkdownHTML if available (preserves code blocks)
            if (typeof window.cleanMarkdownHTML === 'function') {
                content = window.cleanMarkdownHTML(content);
            }
        } else {
            console.warn('marked.js not available, using plain text');
            // Escape HTML for safety
            content = content.replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
        }

        const textDiv = document.createElement('div');
        textDiv.className = 'viz-text-content';
        textDiv.innerHTML = content;
        textDiv.style.cssText = `
            margin: 6px 0;
            line-height: 1.4;
            color: var(--text-primary);
            text-align: left;
            white-space: normal;
            word-wrap: break-word;
        `;

        container.appendChild(textDiv);
        console.log('ext rendered using triple-agent clean markdown (consistent with streaming)');
    }




    /*
        // 4.1.5
        async renderTextDirectly(item, container) {
            let content = item.content;
            
           /  RITICAL FIX: Don't process line breaks here - let the main renderer handle it
            if (window.marked && isMarkdownContent(content)) {
                // Use centralized markdown renderer when available for consistency with chat bubbles
                if (typeof window.renderEnhancedMarkdown === 'function') {
                    content = window.renderEnhancedMarkdown(content);
                } else if (typeof marked !== 'undefined' && marked.parse) {
                    content = marked.parse(content);
                } else {
                    content = (content || '').replace(/\n/g, '<br>');
                }
            } else if (typeof renderMarkdown === 'function' && isMarkdownContent(content)) {
                content = renderMarkdown(content);
            }
    
            const textDiv = document.createElement('div');
            textDiv.className = 'viz-text-content';
            textDiv.innerHTML = content;
            textDiv.style.cssText = `
                margin: 6px 0;
                line-height: 1.4;
                color: var(--text-primary);
                text-align: left;
                white-space: pre-wrap;
                word-wrap: break-word;
            `;
            
            container.appendChild(textDiv);
        }
    
    */


    // 4.2.1
    async renderVisualization(item, container, chartId) {
        try {
            switch (item.type) {
                case 'plotly':
                    await this.renderPlotly(item, container, chartId);
                    break;
                case 'google':
                    await this.renderGoogleChart(item, container, chartId);
                    break;
                case 'chartjs':
                    await this.renderChartJS(item, container, chartId);
                    break;
                case 'mermaid':
                    await this.renderMermaid(item, container, chartId);
                    break;




                case 'error':
                    this.showError(container, item.content);
                    break;
                default:
                    throw new Error(`Unknown visualization type: ${item.type}`);
            }

            this.charts.set(chartId, {
                item,
                container,
                type: item.type,
                createdAt: Date.now()
            });

        } catch (error) {
            console.error(`Error rendering ${item.type}:`, error);
            this.showError(container, `Error rendering ${item.type}: ${error.message}`);
        }
    }

    /**
     * =============================================================================
     * SECTION 5: PLOTLY CHART RENDERING
     * =============================================================================
     */

    // 5.1.1
    async renderPlotlyDirectly(item, contentArea, chartId) {
        if (!window.Plotly) {
            throw new Error('Plotly library not loaded');
        }

        // RITICAL: DOM validation before any DOM manipulation
        if (!contentArea) {
            throw new Error('Content area is null - cannot render Plotly');
        }
        if (!document.contains(contentArea)) {
            console.log('⚠️ VIZ-V3: Plotly content area not in DOM yet (will be attached after message rendering)');
        }

        // IMING SAFETY: Add micro-delay to ensure DOM stability
        await new Promise(resolve => requestAnimationFrame(resolve));

        console.log(`🎯 Direct Plotly render for: ${chartId}`);

        const plotDiv = document.createElement('div');
        plotDiv.id = chartId;
        plotDiv.className = 'plotly-graph-div';
        plotDiv.style.cssText = `
            width: 100%;
            min-width: 400px;
            height: 500px;                   // 00px height for proper margins
            position: relative;
            display: block;
            margin: 0 auto;
            border-radius: 6px;
            background: transparent;
            z-index: 10;                     // ORMAL: Reasonable z-index
            overflow: visible;               // nsure content isn't clipped
        `;

        // RITICAL: Triple-check DOM validity right before manipulation
        if (!contentArea || !document.contains(contentArea)) {
            throw new Error('Content area became invalid before appendChild - DOM timing issue');
        }

        contentArea.appendChild(plotDiv);

        let plotlyData;
        try {
            if (typeof item.content === 'string') {
                try {
                    // Try safe JSON parsing first
                    plotlyData = this.safeJSONParse(item.content);
                } catch (jsonError) {
                    // Fallback to JavaScript eval for object literal syntax (this is expected for JS configs)
                    console.log('ℹ️ Plotly: Using JavaScript eval for object literal syntax');
                    try {
                        plotlyData = (new Function('return ' + item.content))();
                        console.log('✅ Plotly: Config parsed successfully');
                    } catch (evalError) {
                        throw new Error(`Both JSON and JavaScript parsing failed. JSON: ${jsonError.message}, Eval: ${evalError.message}`);
                    }
                }
            } else if (item.data && item.layout) {
                plotlyData = item;
            } else {
                plotlyData = item.content;
            }

            this.applyEnhancedPlotlyTheme(plotlyData);

        } catch (error) {
            console.error(' PLOTLY JSON Parse Error:', error);
            console.error(' Original content type:', typeof item.content);
            console.error(' Original content preview:', typeof item.content === 'string' ? item.content.substring(0, 200) : 'Non-string content');

            throw new Error(`Plotly data parsing failed: ${error.message}`);
        }

        const config = {
            displayModeBar: true,          // Show zoom/pan/reset controls
            responsive: true,
            displaylogo: false,            // Remove Plotly watermark logo
            modeBarButtonsToRemove: ['sendDataToCloud']  // Remove cloud upload button
        };

        try {
            // alidate plotlyData structure before rendering
            if (!plotlyData || !plotlyData.data || !Array.isArray(plotlyData.data)) {
                throw new Error('Invalid Plotly data structure: missing or invalid data array');
            }

            // heck for common data issues (respect orientation and categories)
            // KIP validation for non-Cartesian chart types (polar, 3D, geo, etc.)
            plotlyData.data.forEach((trace, index) => {
                const type = (trace.type || 'scatter').toLowerCase();
                const orientation = (trace.orientation || 'v').toLowerCase();

                // KIP CARTESIAN VALIDATION for polar, 3D, geo, ternary, and hierarchical charts
                const nonCartesianTypes = [
                    'scatter3d', 'surface', 'mesh3d', 'cone', 'streamtube', 'volume', 'isosurface',
                    'scatterpolar', 'scatterpolargl', 'barpolar', 'radar',
                    'scattergeo', 'choropleth', 'scattermapbox', 'choroplethmapbox', 'densitymapbox',
                    'scatterternary',
                    'sankey', 'sunburst', 'treemap', 'icicle', 'funnelarea', 'pie'
                ];

                if (nonCartesianTypes.includes(type)) {
                    console.log(`kipping Cartesian validation for ${type} chart (trace ${index})`);
                    return; // Skip validation for non-Cartesian types
                }

                // Helper to coerce numeric strings to numbers (keep nulls)
                const coerceNumericArray = (arr) => Array.isArray(arr)
                    ? arr.map(v => {
                        if (typeof v === 'number' || v === null) return v;
                        if (typeof v === 'string') {
                            const cleaned = v.replace(/^\+/, '');
                            const parsed = parseFloat(cleaned);
                            return isNaN(parsed) ? null : parsed;
                        }
                        return null;
                    })
                    : arr;

                // Detect categorical arrays (strings that are not numeric)
                const isCategoricalArray = (arr) => Array.isArray(arr) && arr.some(v => {
                    if (typeof v !== 'string') return false;
                    const cleaned = v.replace(/^\+/, '');
                    return isNaN(parseFloat(cleaned));
                });

                // Horizontal bars: y can be categories, x must be numeric
                if (type === 'bar' && orientation === 'h') {
                    const yIsCategorical = isCategoricalArray(trace.y);
                    if (yIsCategorical) {
                        // Expected: categories on y
                        if (!plotlyData.layout) plotlyData.layout = {};
                        plotlyData.layout.yaxis = { ...(plotlyData.layout.yaxis || {}), type: 'category', automargin: true };
                    } else if (Array.isArray(trace.y)) {
                        // If y is numeric strings, coerce to numbers to be safe
                        trace.y = coerceNumericArray(trace.y);
                    }
                    // Ensure x is numeric for horizontal bars
                    if (Array.isArray(trace.x)) {
                        const nonNumericX = trace.x.filter(v => typeof v !== 'number' && v !== null && !(typeof v === 'string' && !isNaN(parseFloat(v))));
                        if (nonNumericX.length > 0) {
                            console.warn(`⚠️ Non-numeric values in trace ${index} x-data for horizontal bar:`, nonNumericX);
                        }
                        trace.x = coerceNumericArray(trace.x);
                    }
                } else {
                    // Vertical or other types: y typically numeric, x may be categorical
                    if (Array.isArray(trace.y)) {
                        const yHasNonNumeric = trace.y.some(v => typeof v !== 'number' && v !== null);
                        if (yHasNonNumeric) {
                            // Try to coerce numeric strings; if still non-numeric, treat as categories
                            const coerced = coerceNumericArray(trace.y);
                            const stillNonNumeric = coerced.some(v => v === null);
                            if (stillNonNumeric) {
                                if (!plotlyData.layout) plotlyData.layout = {};
                                plotlyData.layout.yaxis = { ...(plotlyData.layout.yaxis || {}), type: 'category', automargin: true };
                                // Keep original categorical labels
                            } else {
                                trace.y = coerced;
                            }
                        }
                    }
                    // If x contains non-numeric strings, likely categories
                    if (Array.isArray(trace.x) && isCategoricalArray(trace.x)) {
                        if (!plotlyData.layout) plotlyData.layout = {};
                        plotlyData.layout.xaxis = { ...(plotlyData.layout.xaxis || {}), type: 'category', automargin: true };
                    }
                }
            });

            await window.Plotly.newPlot(chartId, plotlyData.data, plotlyData.layout, config);

            const normalizedPlotlyData = JSON.parse(JSON.stringify(plotlyData));
            normalizedPlotlyData.config = { ...config };
            item.__normalizedPlotlyData = normalizedPlotlyData;
            item.__plotlyConfig = { ...config };

            const vizContainer = contentArea.closest('.viz-container');
            if (vizContainer) {
                vizContainer.dataset.chartId = chartId;
                vizContainer.dataset.chartType = 'plotly';
                this.addUnifiedActionBar(vizContainer, plotlyData, chartId, 'plotly');
            }

            contentArea.dataset.chartId = chartId;
            contentArea.dataset.chartType = 'plotly';
            plotDiv.dataset.chartId = chartId;

            if (typeof window.ensurePlotlyResponsive === 'function') {
                window.ensurePlotlyResponsive(vizContainer || plotDiv);
            }

            setTimeout(() => {
                this.setupClickableLegend(plotDiv);
            }, 800);

            console.log('lotly chart rendered successfully:', chartId);

        } catch (error) {
            console.error(' Error in Plotly.newPlot:', error);
            console.error(' Plotly data that failed:', JSON.stringify(plotlyData, null, 2));

            // Show user-friendly error message
            plotDiv.innerHTML = `
                <div style="padding: 20px; text-align: center; color: #f85149; background: rgba(248, 81, 73, 0.1); border: 1px solid #f85149; border-radius: 6px;">
                    <h4 style="margin: 0 0 10px 0;">⚠️ PLOTLY Visualization Error</h4>
                    <p style="margin: 0; font-size: 14px;">${error.message}</p>
                    ${error.message.includes('JSON') ? '<p style="margin: 10px 0 0 0; font-size: 12px; opacity: 0.8;">Check console for detailed JSON structure</p>' : ''}
                </div>
            `;

            throw error;
        }
    }

    // 5.1.2
    applyEnhancedPlotlyTheme(plotlyData) {
        if (!plotlyData) {
            console.error("Invalid plotlyData in applyEnhancedPlotlyTheme");
            return;
        }

        // EW (Jul 22 2026): Always-white chart canvas. The AI picks axis/grid/
        // text colours that may read fine against one UI theme but disappear
        // against the other. A constant white canvas means every AI-picked
        // colour combination is legible regardless of light/dark UI mode,
        // and Plotly's paper_bgcolor export (downloadImage/toImage) yields
        // an opaque white PNG that matches Mermaid's hard-coded-white PNG
        // export. See VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md.
        //
        // gridColor chosen as a mid-tone slate (#94a3b8, ~2.8:1 on white)
        // rather than the previous GitHub-border-default #e1e4e8 (~1.2:1,
        // essentially invisible) — user reported invisible 3D axes and grid
        // on the new white canvas. See VISUALIZATION_PLOTLY_AXIS_GRID_VISIBILITY_FIX_JULY22_2026.md.
        const bgColor = '#ffffff';
        const textColor = '#24292f';
        const gridColor = '#94a3b8';
        const axisLineColor = '#7c8694';
        const zeroLineColor = '#cbd5e1';

        plotlyData.layout = plotlyData.layout || {};

        // ETECT CHART TYPE: Determine if chart uses Cartesian, Polar, 3D, or other coordinate system
        const chartTypes = new Set();
        if (plotlyData.data && Array.isArray(plotlyData.data)) {
            plotlyData.data.forEach(trace => {
                const type = (trace.type || 'scatter').toLowerCase();

                // Categorize chart types
                if (['scatter3d', 'surface', 'mesh3d', 'cone', 'streamtube', 'volume', 'isosurface'].includes(type)) {
                    chartTypes.add('3d');
                } else if (['scatterpolar', 'scatterpolargl', 'barpolar'].includes(type) || type === 'radar') {
                    chartTypes.add('polar');
                } else if (['scattergeo', 'choropleth', 'scattermapbox', 'choroplethmapbox', 'densitymapbox'].includes(type)) {
                    chartTypes.add('geo');
                } else if (['scatterternary', 'scatterternary'].includes(type)) {
                    chartTypes.add('ternary');
                } else if (['sankey', 'sunburst', 'treemap', 'icicle', 'funnelarea', 'pie'].includes(type)) {
                    chartTypes.add('hierarchical');
                } else {
                    // Default: Cartesian charts (bar, line, scatter, etc.)
                    chartTypes.add('cartesian');
                }
            });
        } else {
            chartTypes.add('cartesian'); // Default fallback
        }

        console.log('🔍 Detected chart types:', Array.from(chartTypes));

        // EPOSITIONED LEGEND: Bottom-left as requested
        const safeLegend = {
            orientation: 'h',                 // HANGED: Vertical instead of horizontal
            x: 0.0,                        // OSITIONED: Left side, outside plot area
            y: -0.3,                         // OSITIONED: Below plot area
            bgcolor: 'rgba(0,0,0,0)',     /* 🎨 TRANSPARENT background */
            bordercolor: gridColor,        /* 🎨 Uses theme gridColor (white in dark, gray in light) */
            borderwidth: 1,
            font: {
                family: this.options.fontFamily,
                size: 11,
                color: textColor           /* 🎨 Uses theme textColor (white in dark, black in light) */
            },
            xanchor: 'left',
            yanchor: 'top'
        };

        // ASE LAYOUT: Apply universal settings for all chart types
        const baseLayout = {
            autosize: true,
            font: {
                family: this.options.fontFamily,
                size: 14,
                color: textColor
            },
            paper_bgcolor: bgColor,
            plot_bgcolor: bgColor,
            // EW (Jul 22 2026): Apply 2D axis colours at baseLayout so every
            // Cartesian chart (bar/line/scatter/box/histogram/area) gets
            // themed axes -- previously the Cartesian branch at L~3340 had
            // no explicit xaxis/yaxis, so AI charts that didn't specify
            // gridcolor/linecolor fell through to Plotly's invisible '#eee'
            // template default. Plotly spreads *baseLayout first then
            // AI layout last, so per-AI colour overrides still win.
            xaxis: {
                gridcolor: gridColor,
                linecolor: axisLineColor,
                tickcolor: axisLineColor,
                zerolinecolor: zeroLineColor,
                zerolinewidth: 1,
                tickfont: { color: textColor }
            },
            yaxis: {
                gridcolor: gridColor,
                linecolor: axisLineColor,
                tickcolor: axisLineColor,
                zerolinecolor: zeroLineColor,
                zerolinewidth: 1,
                tickfont: { color: textColor }
            },
            legend: safeLegend,
            title: {
                ...plotlyData.layout.title,
                pad: { t: 20, b: 20, l: 10, r: 10 },
                font: {
                    size: 16,
                    color: textColor,
                    family: this.options.fontFamily
                }
            }
        };

        // ONDITIONAL LAYOUT: Apply coordinate-system-specific settings
        if (chartTypes.has('polar')) {
            // OLAR CHARTS: Radar, polar scatter, polar bar
            console.log('🎯 Applying POLAR theme (radar/polar charts)');

            plotlyData.layout = {
                ...baseLayout,
                ...plotlyData.layout,

                // OLAR-SPECIFIC: Preserve and enhance polar configuration
                polar: {
                    bgcolor: bgColor,
                    ...plotlyData.layout.polar,
                    radialaxis: {
                        visible: true,
                        gridcolor: gridColor,
                        linecolor: gridColor,
                        tickcolor: gridColor,
                        tickfont: {
                            color: textColor,
                            size: 11
                        },
                        ...plotlyData.layout.polar?.radialaxis
                    },
                    angularaxis: {
                        gridcolor: gridColor,
                        linecolor: gridColor,
                        tickcolor: gridColor,
                        tickfont: {
                            color: textColor,
                            size: 11
                        },
                        ...plotlyData.layout.polar?.angularaxis
                    }
                },

                // OLAR MARGINS: Different margin requirements
                margin: {
                    l: 80,
                    r: 80,
                    t: 80,
                    b: 120,
                    pad: 0
                },
                height: 700                /* 🔑 INCREASED: 500 → 700px for polar charts */
                /* 🔑 NO WIDTH: Let autosize expand to full container width */
            };

        } else if (chartTypes.has('3d')) {
            // D CHARTS: Surface, mesh3d, scatter3d
            console.log('🎯 Applying 3D theme');

            plotlyData.layout = {
                ...baseLayout,
                ...plotlyData.layout,

                // D-SPECIFIC: Scene configuration
                scene: {
                    bgcolor: bgColor,
                    ...plotlyData.layout.scene,
                    // Set default camera position to see models immediately
                    camera: {
                        eye: { x: 1.5, y: 1.5, z: 1.5 },
                        center: { x: 0, y: 0, z: 0 },
                        up: { x: 0, y: 0, z: 1 }
                    },
                    // EW (Jul 22 2026): Use darker axisLineColor for the
                    // axis line on each 3D wall (Plotly draws 3D axes as
                    // lines on the wall edges -- distinct from the grid
                    // colour). Use gridColor (mid-slate) for the wall grid
                    // and zeroLineColor for the bold zero reference line.
                    // AI's scene.xaxis/yaxis/zaxis still merged last via the
                    // spread, so per-AI overrides still win.
                    xaxis: {
                        gridcolor: gridColor,
                        linecolor: axisLineColor,
                        tickcolor: axisLineColor,
                        zerolinecolor: zeroLineColor,
                        zerolinewidth: 2,
                        showgrid: true,
                        tickfont: { color: textColor, size: 10 },
                        ...plotlyData.layout.scene?.xaxis
                    },
                    yaxis: {
                        gridcolor: gridColor,
                        linecolor: axisLineColor,
                        tickcolor: axisLineColor,
                        zerolinecolor: zeroLineColor,
                        zerolinewidth: 2,
                        showgrid: true,
                        tickfont: { color: textColor, size: 10 },
                        ...plotlyData.layout.scene?.yaxis
                    },
                    zaxis: {
                        gridcolor: gridColor,
                        linecolor: axisLineColor,
                        tickcolor: axisLineColor,
                        zerolinecolor: zeroLineColor,
                        zerolinewidth: 2,
                        showgrid: true,
                        tickfont: { color: textColor, size: 10 },
                        ...plotlyData.layout.scene?.zaxis
                    }
                },
                margin: {
                    l: 60,
                    r: 60,
                    t: 80,
                    b: 120,
                    pad: 0
                },
                height: 700                /* 🔑 INCREASED: 500 → 700px for 3D charts */
                /* 🔑 NO WIDTH: Let autosize expand to full container width */
            };

        } else if (chartTypes.has('geo')) {
            // EO CHARTS: Map-based visualizations
            console.log('🎯 Applying GEO theme');

            plotlyData.layout = {
                ...baseLayout,
                ...plotlyData.layout,

                geo: {
                    bgcolor: bgColor,
                    ...plotlyData.layout.geo
                },
                margin: {
                    l: 40,
                    r: 40,
                    t: 80,
                    b: 100,
                    pad: 0
                },
                height: 700                /* 🔑 INCREASED: 500 → 700px for geo charts */
                /* 🔑 NO WIDTH: Let autosize expand to full container width */
            };

        } else if (chartTypes.has('ternary')) {
            // ERNARY CHARTS: Ternary plots
            console.log('🎯 Applying TERNARY theme');

            plotlyData.layout = {
                ...baseLayout,
                ...plotlyData.layout,

                ternary: {
                    bgcolor: bgColor,
                    ...plotlyData.layout.ternary
                },
                margin: {
                    l: 80,
                    r: 80,
                    t: 80,
                    b: 120,
                    pad: 0
                },
                height: 700                /* 🔑 INCREASED: 500 → 700px for ternary charts */
                /* 🔑 NO WIDTH: Let autosize expand to full container width */
            };

        } else if (chartTypes.has('hierarchical')) {
            // IERARCHICAL CHARTS: Sankey, sunburst, treemap, pie
            console.log('🎯 Applying HIERARCHICAL theme (pie, sunburst, etc.)');

            plotlyData.layout = {
                ...baseLayout,
                ...plotlyData.layout,

                margin: {
                    l: 40,
                    r: 40,
                    t: 80,
                    b: 100,
                    pad: 0
                },
                height: 700                /* 🔑 INCREASED: 500 → 700px for hierarchical charts */
                /* 🔑 NO WIDTH: Let autosize expand to full container width */
            };

        } else {
            // ARTESIAN CHARTS: Bar, line, scatter, box, histogram, etc.
            console.log('🎯 Applying CARTESIAN theme (bar, line, scatter, etc.)');

            plotlyData.layout = {
                ...baseLayout,
                ...plotlyData.layout,

                // PTIMIZED MARGINS: Prevent text truncation and ensure proper spacing
                margin: {
                    l: 90,
                    r: 80,
                    t: 80,
                    b: 120,
                    pad: 0
                },

                height: 700,                /* 🔑 INCREASED: 500 → 700px for cartesian charts */
                /* 🔑 NO WIDTH: Let autosize expand to full container width */

                // AR SPACING: Control bar chart gaps
                bargap: 0.15,
                bargroupgap: 0.05,

                // ARTESIAN AXES: Full axis configuration
                xaxis: {
                    ...plotlyData.layout.xaxis,
                    gridcolor: gridColor,
                    linecolor: gridColor,
                    tickcolor: gridColor,
                    tickfont: {
                        color: textColor,
                        size: 12
                    },
                    dtick: undefined,
                    nticks: 10,
                    domain: [0, 1],
                    range: undefined,
                    automargin: true,
                    ticklen: 5,
                    tickwidth: 1,
                    showgrid: true,
                    gridwidth: 1,
                    showline: true,
                    zeroline: true,
                    showticklabels: true,
                    ticks: 'outside',
                    title: {
                        ...plotlyData.layout.xaxis?.title,
                        standoff: 0,
                        font: {
                            size: 13,
                            color: textColor
                        }
                    }
                },

                yaxis: {
                    ...plotlyData.layout.yaxis,
                    gridcolor: gridColor,
                    linecolor: gridColor,
                    tickcolor: gridColor,
                    tickfont: {
                        color: textColor,
                        size: 12
                    },
                    dtick: undefined,
                    nticks: 8,
                    domain: [0, 1],
                    range: undefined,
                    automargin: true,
                    ticklen: 5,
                    tickwidth: 1,
                    showgrid: true,
                    gridwidth: 1,
                    showline: true,
                    zeroline: true,
                    showticklabels: true,
                    ticks: 'outside',
                    title: {
                        ...plotlyData.layout.yaxis?.title,
                        standoff: 0,
                        font: {
                            size: 13,
                            color: textColor
                        }
                    }
                },

                // NNOTATION SPACING: Control text annotation positioning
                annotations: plotlyData.layout.annotations || []
            };
        }

        console.log('nhanced Plotly theme applied with coordinate-system-aware configuration');
    }

    // 5.1.3
    setupClickableLegend(plotDiv) {
        try {
            if (!plotDiv) {
                return; // ILENT: Just return, don't log warning
            }

            // ETTER: Check multiple ways to find element
            let actualElement = plotDiv;
            if (typeof plotDiv === 'string') {
                actualElement = document.getElementById(plotDiv);
            }

            if (!actualElement || !document.contains(actualElement)) {
                return; // ILENT: Element not in DOM yet, just return
            }

            // NHANCED: Wait for Plotly with shorter timeout
            const waitForPlotlyReady = (attempts = 0) => {
                const maxAttempts = 10; // EDUCED: Shorter wait time

                if (attempts >= maxAttempts) {
                    return; // ILENT: Stop trying quietly
                }

                // Check if element still exists and has Plotly data
                if (!document.contains(actualElement) ||
                    !actualElement._fullLayout ||
                    !actualElement.data ||
                    !Array.isArray(actualElement.data)) {

                    setTimeout(() => waitForPlotlyReady(attempts + 1), 100);
                    return;
                }

                // UCCESS: Setup legend if not already done
                try {
                    if (actualElement._legendSetup) {
                        return; // Already set up
                    }

                    actualElement.on('plotly_legenddoubleclick', function (data) {
                        try {
                            if (!data || typeof data.curveNumber !== 'number') {
                                return false;
                            }

                            const traceIndex = data.curveNumber;

                            if (!actualElement.data || traceIndex >= actualElement.data.length) {
                                return false;
                            }

                            const currentVisibility = actualElement.data.map(trace =>
                                trace.visible !== false ? true : trace.visible
                            );
                            const newVisibility = currentVisibility.map((visible, i) =>
                                i === traceIndex ? true : 'legendonly'
                            );

                            window.Plotly.restyle(actualElement, 'visible', newVisibility).catch(() => {
                                // ILENT: Handle error silently
                            });

                            return false;
                        } catch (error) {
                            return false;
                        }
                    });

                    actualElement._legendSetup = true;

                } catch (error) {
                    // ILENT: Setup failed, no logging
                }
            };

            waitForPlotlyReady();

        } catch (error) {
            // ILENT: Handle all errors silently
        }
    }

    // 5.1.4
    enhanceAxisTitles(plotlyData) {
        if (!plotlyData || !plotlyData.layout) return;

        // Detect common units based on data patterns
        const detectUnits = (title, values, axisType) => {
            if (!title || typeof title !== 'string') return title;
            if (title.includes('(') && title.includes(')')) return title; // Already has units

            // Check for common metric prefixes in the title
            const lowerTitle = title.toLowerCase();

            // Determine units based on patterns in data and title
            if (values && Array.isArray(values)) {
                // Check data patterns
                const max = Math.max(...values.filter(v => typeof v === 'number'));
                const min = Math.min(...values.filter(v => typeof v === 'number'));
                const allInteger = values.every(v => typeof v === 'number' && Number.isInteger(v));

                // Unit mapping based on title keywords and data characteristics
                const unitMap = [
                    // Financial metrics
                    { test: () => /price|cost|revenue|sales|profit|income|expense|budget|dollar|eur|gbp|jpy|usd|£|€|¥|\$/i.test(lowerTitle), unit: '$' },
                    // Percentages
                    { test: () => /percent|ratio|rate|growth|change|increase|decrease|share|proportion/i.test(lowerTitle) || (max <= 100 && min >= 0), unit: '%' },
                    // Time metrics
                    { test: () => /time|duration|period|minute|second|hour|ms|sec/i.test(lowerTitle), unit: 'sec' },
                    // Counts/quantity
                    { test: () => /count|quantity|number|total|sum|amount|volume|inventory/i.test(lowerTitle) && allInteger, unit: '' },
                    // Weights
                    { test: () => /weight|mass|kg|gram|pound|lb|ton/i.test(lowerTitle), unit: 'kg' },
                    // Distance
                    { test: () => /distance|length|height|width|depth|km|mile|meter|m|ft|cm/i.test(lowerTitle), unit: 'm' },
                    // Temperature
                    { test: () => /temp|temperature|degree|fahrenheit|celsius|°c|°f/i.test(lowerTitle), unit: '°C' },
                    // Speed
                    { test: () => /speed|velocity|pace|mph|kph|kmh/i.test(lowerTitle), unit: 'km/h' },
                    // Energy
                    { test: () => /energy|power|watt|joule|calorie|btu/i.test(lowerTitle), unit: 'W' },
                    // Frequency
                    { test: () => /frequency|hz|khz|mhz|ghz/i.test(lowerTitle), unit: 'Hz' }
                ];

                // Find the first matching unit pattern
                for (const { test, unit } of unitMap) {
                    if (test()) {
                        return unit ? `${title} (${unit})` : title;
                    }
                }
            }

            // Default unit mappings for axis types
            if (axisType === 'xaxis' && /date|time|month|year|day|week/i.test(lowerTitle)) {
                return title; // No units for time axes
            } else if (axisType === 'yaxis' && !title.includes('unit')) {
                return `${title} (units)`; // Generic units for y-axis
            }

            return title; // No change if no pattern detected
        };

        // Process x-axis
        if (plotlyData.layout.xaxis) {
            if (typeof plotlyData.layout.xaxis.title === 'string') {
                plotlyData.layout.xaxis.title = {
                    text: detectUnits(plotlyData.layout.xaxis.title,
                        plotlyData.data?.[0]?.x, 'xaxis')
                };
            } else if (plotlyData.layout.xaxis.title?.text) {
                plotlyData.layout.xaxis.title.text = detectUnits(
                    plotlyData.layout.xaxis.title.text,
                    plotlyData.data?.[0]?.x, 'xaxis'
                );
            }
        }

        // Process y-axis
        if (plotlyData.layout.yaxis) {
            if (typeof plotlyData.layout.yaxis.title === 'string') {
                plotlyData.layout.yaxis.title = {
                    text: detectUnits(plotlyData.layout.yaxis.title,
                        plotlyData.data?.[0]?.y, 'yaxis')
                };
            } else if (plotlyData.layout.yaxis.title?.text) {
                plotlyData.layout.yaxis.title.text = detectUnits(
                    plotlyData.layout.yaxis.title.text,
                    plotlyData.data?.[0]?.y, 'yaxis'
                );
            }
        }

        // Process secondary y-axis if it exists
        if (plotlyData.layout.yaxis2) {
            if (typeof plotlyData.layout.yaxis2.title === 'string') {
                plotlyData.layout.yaxis2.title = {
                    text: detectUnits(plotlyData.layout.yaxis2.title,
                        plotlyData.data?.find(d => d.yaxis === 'y2')?.y, 'yaxis')
                };
            } else if (plotlyData.layout.yaxis2.title?.text) {
                plotlyData.layout.yaxis2.title.text = detectUnits(
                    plotlyData.layout.yaxis2.title.text,
                    plotlyData.data?.find(d => d.yaxis === 'y2')?.y, 'yaxis'
                );
            }
        }
    }

    // 5.2.1
    toggleChartTypeSwitcher(container, plotlyData, chartId) {
        const existing = container.querySelector('.chart-type-switcher');
        if (existing) {
            existing.remove();
            return;
        }

        const switcher = document.createElement('div');
        switcher.className = 'chart-type-switcher';
        switcher.style.right = '120px'; // Position it properly

        const compatibleTypes = this.getCompatibleChartTypes(plotlyData.data[0]);

        const select = document.createElement('select');
        select.className = 'chart-type-select';

        compatibleTypes.forEach(({ value, label, icon }) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = `${icon} ${label}`;
            if (plotlyData.data[0]?.type === value) {
                option.selected = true;
            }
            select.appendChild(option);
        });

        select.onchange = (e) => {
            const newType = e.target.value;
            this.smartChartTypeChange(plotlyData, chartId, newType);
            // ON'T auto-remove - let it stay open
        };

        switcher.appendChild(select);
        container.appendChild(switcher);

        // IX: Only remove when clicking outside
        const handleClickOutside = (e) => {
            if (!switcher.contains(e.target) && !e.target.closest('[data-function="chartType"]')) {
                switcher.remove();
                document.removeEventListener('click', handleClickOutside);
            }
        };

        // Add slight delay to prevent immediate closure
        setTimeout(() => {
            document.addEventListener('click', handleClickOutside);
        }, 100);
    }

    // 5.2.2
    getCompatibleChartTypes(trace) {
        if (!trace) return [{ value: 'scatter', label: 'Line Chart', icon: '📈' }];

        // Always allow these core types regardless of current state
        const coreTypes = [
            { value: 'scatter', label: 'Line/Scatter', icon: '📈' },
            { value: 'bar', label: 'Bar Chart', icon: '📊' },
            { value: 'pie', label: 'Pie Chart', icon: '🥧' }
        ];

        // Additional types based on data availability
        const additionalTypes = [
            { value: 'histogram', label: 'Histogram', icon: '📊' },
            { value: 'box', label: 'Box Plot', icon: '📦' }
        ];

        return [...coreTypes, ...additionalTypes];
    }

    // 5.2.3
    smartChartTypeChange(plotlyData, chartId, newType) {
        if (!window.Plotly) {
            this.showNotification(' Plotly not available', 'error');
            return;
        }

        try {
            const newData = JSON.parse(JSON.stringify(plotlyData.data));

            newData.forEach(trace => {
                const originalType = trace.type;
                trace.type = newType;

                switch (newType) {
                    case 'pie':
                        if (trace.y && !trace.values) {
                            trace.values = trace.y;
                            trace.labels = trace.x || trace.y.map((_, i) => `Item ${i + 1}`);
                            delete trace.x;
                            delete trace.y;
                            delete trace.mode;
                        }
                        break;

                    case 'histogram':
                        // IXED: Proper histogram configuration
                        if (trace.y && !trace.x) {
                            trace.x = trace.y;  // Use Y data as X for histogram
                            delete trace.y;
                        } else if (trace.x && trace.y) {
                            // If both x and y exist, use x for histogram
                            delete trace.y;
                        }

                        // RITICAL: Histogram-specific settings
                        delete trace.mode;
                        trace.nbinsx = 20;           // Number of bins
                        trace.histnorm = '';         // Don't normalize (show counts)
                        trace.autobinx = true;       // Auto-calculate bin size
                        trace.marker = {
                            ...trace.marker,
                            line: {
                                color: 'rgba(255,255,255,0.6)',
                                width: 1
                            }
                        };
                        break;

                    case 'box':
                        if (!trace.y && trace.x) {
                            trace.y = trace.x;
                            delete trace.x;
                        }
                        delete trace.mode;
                        break;

                    case 'scatter':
                        if (trace.values && !trace.y) {
                            trace.y = trace.values;
                            trace.x = trace.labels || trace.y.map((_, i) => i);
                            delete trace.values;
                            delete trace.labels;
                        }
                        trace.mode = trace.mode || 'lines+markers';
                        break;

                    case 'bar':
                        if (trace.values && !trace.y) {
                            trace.y = trace.values;
                            trace.x = trace.labels || trace.y.map((_, i) => `Item ${i + 1}`);
                            delete trace.values;
                            delete trace.labels;
                        }
                        delete trace.mode;
                        break;
                }
            });

            // NHANCED: Layout adjustments for different chart types
            let layoutUpdates = {};

            if (newType === 'histogram') {
                layoutUpdates = {
                    'xaxis.title': 'Value',
                    'yaxis.title': 'Frequency',
                    'bargap': 0.1,           // Small gap between bins
                    'bargroupgap': 0.0       // No gap between groups
                };
            } else if (newType === 'bar') {
                layoutUpdates = {
                    'bargap': 0.2,           // Larger gap for bar charts
                    'bargroupgap': 0.1
                };
            }

            // Update the chart
            Plotly.react(chartId, newData, { ...plotlyData.layout, ...layoutUpdates });
            this.showNotification(`📊 Chart changed to ${this.getChartTypeName(newType)}`, 'success');

            // Update stored data
            plotlyData.data = newData;

        } catch (error) {
            console.error('Error changing chart type:', error);
            this.showNotification(' Failed to change chart type', 'error');
        }
    }

    // 5.2.4
    getChartTypeName(type) {
        const names = {
            'scatter': 'Line/Scatter Plot',
            'bar': 'Bar Chart',
            'pie': 'Pie Chart',
            'histogram': 'Histogram',
            'box': 'Box Plot'
        };
        return names[type] || type;
    }

    // 5.3.1
    activatePlotlyTool(chartId, tool) {
        if (!window.Plotly) return;

        const plotDiv = document.getElementById(chartId);
        if (!plotDiv) return;

        switch (tool) {
            case 'zoom':
                Plotly.relayout(chartId, { 'dragmode': 'zoom' });
                this.showNotification('🔍 Zoom mode activated - drag to zoom', 'info');
                break;
            case 'pan':
                Plotly.relayout(chartId, { 'dragmode': 'pan' });
                this.showNotification('✋ Pan mode activated - drag to move', 'info');
                break;
            case 'select':
                Plotly.relayout(chartId, { 'dragmode': 'select' });
                this.showNotification('👆 Select mode activated - drag to select', 'info');
                break;
        }
    }

    // 5.3.2
    resetPlotlyView(chartId) {
        if (!window.Plotly) return;

        const plotDiv = document.getElementById(chartId);
        if (!plotDiv) return;

        // Check if this is a 3D chart
        const is3D = plotDiv.data && plotDiv.data.some(trace =>
            ['scatter3d', 'surface', 'mesh3d', 'cone', 'streamtube', 'volume', 'isosurface'].includes(trace.type)
        );

        if (is3D) {
            // Reset 3D camera to default view with proper distance
            Plotly.relayout(chartId, {
                'scene.camera': {
                    eye: { x: 1.5, y: 1.5, z: 1.5 },
                    center: { x: 0, y: 0, z: 0 },
                    up: { x: 0, y: 0, z: 1 }
                },
                'scene.xaxis.autorange': true,
                'scene.yaxis.autorange': true,
                'scene.zaxis.autorange': true,
                'dragmode': 'orbit'
            });
            this.showNotification('🏠 3D view reset to original', 'success');
        } else {
            // Reset 2D chart axes
            Plotly.relayout(chartId, {
                'xaxis.autorange': true,
                'yaxis.autorange': true,
                'dragmode': 'zoom'
            });
            this.showNotification('🏠 View reset to original', 'success');
        }
    }

    // 5.3.3
    addTrendLine(chartId, plotlyData) {
        if (!window.Plotly || !plotlyData.data[0]) return;

        const trace = plotlyData.data[0];
        if (!trace.x || !trace.y) return;

        // Calculate linear regression
        const regression = this.calculateLinearRegression(trace.x, trace.y);

        const trendTrace = {
            x: trace.x,
            y: regression.trendY,
            type: 'scatter',
            mode: 'lines',
            name: `Trend (R² = ${regression.r2.toFixed(3)})`,
            showlegend: false,
            line: {
                color: '#ff6b6b',
                width: 2,
                dash: 'dash'
            }
        };

        Plotly.addTraces(chartId, trendTrace);
        this.showNotification(`📈 Trend line added (R² = ${regression.r2.toFixed(3)})`, 'success');
    }

    // 5.3.4
    calculateLinearRegression(x, y) {
        const n = x.length;
        const sumX = x.reduce((a, b) => a + b, 0);
        const sumY = y.reduce((a, b) => a + b, 0);
        const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
        const sumXX = x.reduce((sum, xi) => sum + xi * xi, 0);

        const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;

        const trendY = x.map(xi => slope * xi + intercept);

        // Calculate R²
        const meanY = sumY / n;
        const totalSumSquares = y.reduce((sum, yi) => sum + Math.pow(yi - meanY, 2), 0);
        const residualSumSquares = y.reduce((sum, yi, i) => sum + Math.pow(yi - trendY[i], 2), 0);
        const r2 = 1 - (residualSumSquares / totalSumSquares);

        return { trendY, slope, intercept, r2 };
    }

    // 5.3.5
    showStatistics(plotlyData) {
        if (!plotlyData.data[0] || !plotlyData.data[0].y) return;

        const data = plotlyData.data[0].y.filter(v => typeof v === 'number');
        if (data.length === 0) return;

        const stats = this.calculateComprehensiveStatistics(data);

        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.id = 'stats-modal-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.4);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(2px);
            animation: fadeIn 0.2s ease;
        `;

        const modal = document.createElement('div');
        modal.style.cssText = `
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 12px;
            padding: 24px;
            max-width: 420px;
            width: 85%;
            max-height: 70vh;
            overflow-y: auto;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
            color: var(--text-primary);
            position: relative;
            animation: slideIn 0.3s ease;
            transform-origin: center;
        `;

        modal.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0; color: var(--text-primary); display: flex; align-items: center; font-size: 18px;">
                    📊 Statistics Summary
                </h3>
                <button id="stats-close-btn" style="
                    background: transparent;
                    color: var(--text-secondary);
                    border: none;
                    border-radius: 50%;
                    width: 28px;
                    height: 28px;
                    cursor: pointer;
                    font-size: 18px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    transition: all 0.2s ease;
                " onmouseover="this.style.background='var(--accent-red)'; this.style.color='white';" 
                   onmouseout="this.style.background='transparent'; this.style.color='var(--text-secondary)';">×</button>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px 16px; color: var(--text-primary); font-size: 13px;">
                <div style="font-weight: 500;">Count:</div><div style="font-family: 'Monaco', monospace;">${stats.count}</div>
                <div style="font-weight: 500;">Mean:</div><div style="font-family: 'Monaco', monospace;">${stats.mean.toFixed(3)}</div>
                <div style="font-weight: 500;">Median:</div><div style="font-family: 'Monaco', monospace;">${stats.median.toFixed(3)}</div>
                <div style="font-weight: 500;">Mode:</div><div style="font-family: 'Monaco', monospace;">${stats.mode ? stats.mode.toFixed(3) : 'None'}</div>
                <div style="font-weight: 500;">Std Dev:</div><div style="font-family: 'Monaco', monospace;">${stats.stdDev.toFixed(3)}</div>
                <div style="font-weight: 500;">Variance:</div><div style="font-family: 'Monaco', monospace;">${stats.variance.toFixed(3)}</div>
                <div style="font-weight: 500;">Minimum:</div><div style="font-family: 'Monaco', monospace;">${stats.min.toFixed(3)}</div>
                <div style="font-weight: 500;">Maximum:</div><div style="font-family: 'Monaco', monospace;">${stats.max.toFixed(3)}</div>
                <div style="font-weight: 500;">Range:</div><div style="font-family: 'Monaco', monospace;">${stats.range.toFixed(3)}</div>
                <div style="font-weight: 500;">Q1 (25th):</div><div style="font-family: 'Monaco', monospace;">${stats.q1.toFixed(3)}</div>
                <div style="font-weight: 500;">Q3 (75th):</div><div style="font-family: 'Monaco', monospace;">${stats.q3.toFixed(3)}</div>
                <div style="font-weight: 500;">IQR:</div><div style="font-family: 'Monaco', monospace;">${stats.iqr.toFixed(3)}</div>
            </div>
            
            <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--border-primary);">
                <div style="font-size: 11px; color: var(--text-secondary); line-height: 1.4;">
                    📈 <strong>Dataset:</strong> ${stats.count} data points from ${stats.min.toFixed(2)} to ${stats.max.toFixed(2)}
                </div>
            </div>
        `;

        // dd CSS animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideIn {
                from { opacity: 0; transform: scale(0.9) translateY(-20px); }
                to { opacity: 1; transform: scale(1) translateY(0); }
            }
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
            @keyframes slideOut {
                from { opacity: 1; transform: scale(1) translateY(0); }
                to { opacity: 0; transform: scale(0.9) translateY(-20px); }
            }
        `;
        document.head.appendChild(style);

        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        // IXED: Proper close handlers
        const closeBtn = modal.querySelector('#stats-close-btn');

        const closeModal = () => {
            // Animate out
            overlay.style.animation = 'fadeOut 0.2s ease forwards';
            modal.style.animation = 'slideOut 0.2s ease forwards';

            setTimeout(() => {
                if (overlay.parentNode) {
                    overlay.remove();
                }
                if (style.parentNode) {
                    style.remove();
                }
            }, 200);
        };

        // LICK OUTSIDE TO CLOSE
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                console.log('Clicked outside modal - closing');
                closeModal();
            }
        });

        // LOSE BUTTON
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            console.log('Close button clicked');
            closeModal();
        });

        // SC KEY TO CLOSE
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                console.log('ESC key pressed - closing');
                closeModal();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);

        // REVENT MODAL CONTENT CLICKS FROM CLOSING
        modal.addEventListener('click', (e) => {
            e.stopPropagation();
        });

        console.log('tatistics modal opened with close handlers');
    }

    // 5.3.6
    calculateComprehensiveStatistics(data) {
        const sorted = [...data].sort((a, b) => a - b);
        const count = data.length;
        const sum = data.reduce((a, b) => a + b, 0);
        const mean = sum / count;

        // Median
        const median = count % 2 === 0
            ? (sorted[count / 2 - 1] + sorted[count / 2]) / 2
            : sorted[Math.floor(count / 2)];

        // Mode
        const frequency = {};
        let maxFreq = 0;
        let mode = null;
        data.forEach(val => {
            frequency[val] = (frequency[val] || 0) + 1;
            if (frequency[val] > maxFreq) {
                maxFreq = frequency[val];
                mode = val;
            }
        });
        mode = maxFreq > 1 ? mode : null;

        // Variance and Standard Deviation
        const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / count;
        const stdDev = Math.sqrt(variance);

        // Quartiles
        const q1Index = Math.floor(count * 0.25);
        const q3Index = Math.floor(count * 0.75);
        const q1 = sorted[q1Index];
        const q3 = sorted[q3Index];
        const iqr = q3 - q1;

        return {
            count,
            mean,
            median,
            mode,
            variance,
            stdDev,
            min: sorted[0],
            max: sorted[sorted.length - 1],
            range: sorted[sorted.length - 1] - sorted[0],
            q1,
            q3,
            iqr
        };
    }

    // 5.4.1
    toggleAnimation(chartId, plotlyData) {
        if (!window.Plotly) return;

        const plotDiv = document.getElementById(chartId);
        if (!plotDiv) return;

        // Check if animation is already running
        const isAnimating = plotDiv.getAttribute('data-animating') === 'true';

        if (isAnimating) {
            // Stop animation
            if (this._animationInterval) {
                clearInterval(this._animationInterval);
                this._animationInterval = null;
            }
            plotDiv.setAttribute('data-animating', 'false');
            this.showNotification('⏹️ Animation stopped', 'info');
            return;
        }

        // Start animation - create frame-by-frame animation effect
        const data = plotlyData.data[0];
        if (!data || !data.x || !data.y) {
            this.showNotification(' This chart type cannot be animated', 'error');
            return;
        }

        const originalData = JSON.parse(JSON.stringify(data));
        const steps = 30; // Number of animation frames

        let frame = 0;
        plotDiv.setAttribute('data-animating', 'true');

        this._animationInterval = setInterval(() => {
            // Animate by gradually revealing data points
            const pointsToShow = Math.floor((frame / steps) * originalData.x.length);
            const animatedData = {
                ...originalData,
                x: originalData.x.slice(0, pointsToShow),
                y: originalData.y.slice(0, pointsToShow)
            };

            Plotly.animate(chartId, {
                data: [animatedData],
                traces: [0],
                layout: {}
            }, {
                transition: { duration: 100, easing: 'cubic-in-out' },
                frame: { duration: 100 }
            });

            frame = (frame + 1) % (steps + 10); // Add pause at the end

            // Reset animation after completion
            if (frame === 0) {
                Plotly.animate(chartId, {
                    data: [originalData],
                    traces: [0],
                    layout: {}
                });
            }
        }, 200);

        this.showNotification('▶️ Animation started', 'success');
    }

    // 5.4.2
    toggle3DView(chartId, plotlyData) {
        if (!window.Plotly) {
            this.showNotification(' Plotly library not loaded', 'error');
            return;
        }

        const plotDiv = document.getElementById(chartId);
        if (!plotDiv) {
            this.showNotification(' Chart element not found', 'error');
            return;
        }

        try {
            // Check if already in 3D mode
            const is3D = plotDiv.getAttribute('data-3d') === 'true';

            if (is3D) {
                // Switch back to 2D
                const original2DData = JSON.parse(plotDiv.getAttribute('data-original') || '{}');
                if (Object.keys(original2DData).length) {
                    Plotly.react(chartId, original2DData.data, original2DData.layout);
                    plotDiv.removeAttribute('data-original');
                    plotDiv.setAttribute('data-3d', 'false');
                    this.showNotification('📊 Returned to 2D view', 'success');
                }
                return;
            }

            // Save original data
            plotDiv.setAttribute('data-original', JSON.stringify({
                data: plotlyData.data,
                layout: plotlyData.layout
            }));

            // Create a simple 3D surface
            const size = 20;
            const xValues = Array.from({ length: size }, (_, i) => i - size / 2);
            const yValues = Array.from({ length: size }, (_, i) => i - size / 2);

            const zValues = [];
            for (let i = 0; i < size; i++) {
                const row = [];
                for (let j = 0; j < size; j++) {
                    const x = xValues[i];
                    const y = yValues[j];
                    row.push(5 * Math.sin(Math.sqrt(x * x + y * y) / 2));
                }
                zValues.push(row);
            }

            const data3D = [{
                type: 'surface',
                x: xValues,
                y: yValues,
                z: zValues,
                colorscale: 'Viridis',
                contours: {
                    z: { show: true, usecolormap: true, highlightcolor: "#42f462" }
                }
            }];

            // EW (Jul 22 2026): Always-white chart canvas (matching the
            // applyEnhancedPlotlyTheme path). See VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md.
            //
            // Also apply per-axis grid/line/tick colours inline -- this
            // synthesised 3D scene was previously shipped with only
            // {title: ...} per axis, leaving grid/line/tick at Plotly's
            // template defaults (which read as white-on-white on our
            // forced white canvas). See VISUALIZATION_PLOTLY_AXIS_GRID_VISIBILITY_FIX_JULY22_2026.md.
            const bgColor = '#ffffff';
            const textColor = '#24292f';
            const gridColor = '#94a3b8';
            const axisLineColor = '#7c8694';
            const zeroLineColor = '#cbd5e1';

            const layout3D = {
                title: 'Interactive 3D Surface',
                scene: {
                    bgcolor: bgColor,
                    xaxis: {
                        title: 'X Axis (units)',
                        gridcolor: gridColor,
                        linecolor: axisLineColor,
                        tickcolor: axisLineColor,
                        zerolinecolor: zeroLineColor,
                        zerolinewidth: 2,
                        tickfont: { color: textColor }
                    },
                    yaxis: {
                        title: 'Y Axis (units)',
                        gridcolor: gridColor,
                        linecolor: axisLineColor,
                        tickcolor: axisLineColor,
                        zerolinecolor: zeroLineColor,
                        zerolinewidth: 2,
                        tickfont: { color: textColor }
                    },
                    zaxis: {
                        title: 'Z Axis (units)',
                        gridcolor: gridColor,
                        linecolor: axisLineColor,
                        tickcolor: axisLineColor,
                        zerolinecolor: zeroLineColor,
                        zerolinewidth: 2,
                        tickfont: { color: textColor }
                    }
                },
                paper_bgcolor: bgColor,
                plot_bgcolor: bgColor,
                font: { color: textColor },
                margin: { l: 0, r: 0, b: 0, t: 40, pad: 0 }
            };

            Plotly.react(chartId, data3D, layout3D);
            plotDiv.setAttribute('data-3d', 'true');
            this.showNotification('🧊 Switched to 3D view', 'success');

        } catch (err) {
            console.error('3D view error:', err);
            this.showNotification(' Error creating 3D view', 'error');
        }
    }

    // 5.4.3
    toggleAnnotations(chartId) {
        if (!window.Plotly) return;

        const plotDiv = document.getElementById(chartId);
        if (!plotDiv) return;

        // Check if annotations are enabled
        const hasAnnotations = plotDiv.getAttribute('data-annotations') === 'true';

        if (hasAnnotations) {
            // Remove annotations
            Plotly.relayout(chartId, {
                'annotations': []
            });
            plotDiv.setAttribute('data-annotations', 'false');
            this.showNotification('📝 Annotations removed', 'info');
            return;
        }

        // Get current data
        const data = plotDiv.data?.[0];
        if (!data || !data.x || !data.y) {
            this.showNotification(' This chart cannot be annotated', 'error');
            return;
        }

        // Create annotations for important points
        const annotations = [];

        // Find local maxima and minima
        for (let i = 1; i < data.y.length - 1; i++) {
            const prev = data.y[i - 1];
            const curr = data.y[i];
            const next = data.y[i + 1];

            // Local maximum
            if (curr > prev && curr > next) {
                annotations.push({
                    x: data.x[i],
                    y: data.y[i],
                    text: 'Peak',
                    arrowhead: 2,
                    ax: 0,
                    ay: -30,
                    bgcolor: 'rgba(255,255,255,0.9)',
                    bordercolor: '#ff6b6b',
                    borderwidth: 1,
                    font: { size: 10 }
                });
            }

            // Local minimum
            if (curr < prev && curr < next) {
                annotations.push({
                    x: data.x[i],
                    y: data.y[i],
                    text: 'Valley',
                    arrowhead: 2,
                    ax: 0,
                    ay: 30,
                    bgcolor: 'rgba(255,255,255,0.9)',
                    bordercolor: '#4dabf7',
                    borderwidth: 1,
                    font: { size: 10 }
                });
            }
        }

        // Add start and end points
        annotations.push({
            x: data.x[0],
            y: data.y[0],
            text: 'Start',
            arrowhead: 2,
            ax: -30,
            ay: 0,
            bgcolor: 'rgba(255,255,255,0.9)',
            bordercolor: '#37b24d',
            borderwidth: 1,
            font: { size: 10 }
        });

        annotations.push({
            x: data.x[data.x.length - 1],
            y: data.y[data.y.length - 1],
            text: 'End',
            arrowhead: 2,
            ax: 30,
            ay: 0,
            bgcolor: 'rgba(255,255,255,0.9)',
            bordercolor: '#f76707',
            borderwidth: 1,
            font: { size: 10 }
        });

        // Limit to at most 10 annotations to avoid cluttering
        if (annotations.length > 10) {
            annotations.splice(2, annotations.length - 8);
        }

        Plotly.relayout(chartId, {
            'annotations': annotations
        });

        plotDiv.setAttribute('data-annotations', 'true');
        this.showNotification('📝 Added annotations to key points', 'success');
    }

    /**
     * =============================================================================
     * SECTION 6: MERMAID DIAGRAM RENDERING
     * =============================================================================
     */

    // 6.1.1
    // 6.1.1 - ENHANCED: Mermaid rendering with enhanced height management + compatibility
    async renderMermaidDirectly(item, contentArea, chartId, retryContext = null) {
        // Cap on the number of times we will defer-and-retry a Mermaid render
        // when the container is initially 0-px wide.  The initial call counts
        // as attempt 0, so up to MAX_MERMAID_RETRIES additional retries are
        // permitted before we surface an error to the user.
        const MAX_MERMAID_RETRIES = 2;

        if (!window.mermaid) {
            throw new Error('Mermaid library not loaded');
        }

        // Bounded retry: preserve the original chartId as baseId and track the
        // current attempt number.  Retries use <base>-retry-N (never timestamped)
        // so the chain is bounded and debuggable.
        const baseId = retryContext ? retryContext.baseId : chartId;
        const attempt = retryContext ? retryContext.attempt : 0;

        // EW (Jul 24 2026): Render-token for concurrent re-render safety.
        // When two renderMermaidDirectly calls race on the same contentArea
        // (stream-finalize + chunk-handler both triggering a render, or
        // _scheduleMermaidRerender racing the original attempt), the second
        // call's cleanup at L5063 wipes the first call's <svg>-bearing div
        // before the first call's awaited mermaid.render resolves.  Without
        // this token, the stale call would write SVG into a detached div
        // AND attach an action bar to the outer viz-container — leaving the
        // user with a visible action bar but an empty body.  Bumping the
        // token on entry and checking it after every await makes the LATEST
        // in-flight render the only one that commits, mirroring the React 18
        // pattern for dropping stale render commits.
        const myRenderToken = (contentArea._mermaidRenderToken = (contentArea._mermaidRenderToken || 0) + 1);

        // RITICAL: DOM validation before any DOM manipulation
        if (!contentArea) {
            throw new Error('Content area is null - cannot render Mermaid');
        }
        if (!document.contains(contentArea)) {
            console.log('⚠️ VIZ-V3: Mermaid content area not in DOM yet (will be attached after message rendering)');
        }

        // IMING SAFETY: Add micro-delay to ensure DOM stability
        await new Promise(resolve => requestAnimationFrame(resolve));

        console.log(`🎯 Enhanced Mermaid render with improved approach: ${chartId}`);

        const mermaidDiv = document.createElement('div');
        mermaidDiv.id = chartId;
        mermaidDiv.className = 'mermaid';

        // ERMAID CONTAINER: Normal document flow, no absolute positioning
        mermaidDiv.style.cssText = `
            width: 100%;
            min-height: 200px;
            height: auto;
            display: block;
            text-align: center;
            overflow: auto;
            padding: 20px;
            margin: 20px 0;
            box-sizing: border-box;
        `;

        // RITICAL: Triple-check DOM validity right before manipulation
        if (!contentArea || !document.contains(contentArea)) {
            console.log('⚠️ VIZ-V3: Mermaid content area not in DOM before appendChild (proceeding with render)');
        }

        // EW: Clean up any prior Mermaid divs (e.g., left over from a previous
        // broken render attempt, or from the orchestrator-defer path). Each
        // viz-content-area corresponds to one <MERMAID> block, so this is safe.
        contentArea.querySelectorAll('.mermaid, .mermaid-deferred-placeholder').forEach(d => d.remove());

        contentArea.appendChild(mermaidDiv);

        try {
            // EW (Jul 22 2026): Always-white chart canvas. Drop all isDark
            // branching so chart text/fills read against the constant white
            // canvas regardless of UI theme. See
            // VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md.
            mermaid.initialize({
                startOnLoad: false,
                theme: 'base',
                securityLevel: 'loose',
                htmlLabels: true,
                maxTextSize: 50000,
                maxEdges: 2000,

                // nhanced: Enhanced spacing configuration
                flowchart: {
                    htmlLabels: true,
                    useMaxWidth: true,
                    curve: 'basis',
                    padding: 35,              // Container padding around diagram
                    nodeSpacing: 100,         // Spacing between nodes
                    rankSpacing: 100,         // Spacing between ranks
                    diagramPadding: 40,       // Outer diagram padding
                    edgePadding: 25,          // Space around edges
                    nodePadding: 8,           // REDUCED: Internal node padding (was 20)
                    textHeight: 20,           // Slightly smaller text height assumption (was 24)
                    lineHeight: 1.3           // REDUCED: Line height multiplier (was 1.6)
                },

                themeVariables: {
                    primaryColor: '#f0f0f0',
                    primaryTextColor: '#24292f',
                    primaryBorderColor: '#cccccc',
                    lineColor: '#656d76',
                    backgroundColor: '#ffffff',
                    textColor: '#24292f',
                    nodeTextColor: '#24292f',
                    nodeBkg: '#f0f0f0',
                    nodeBorder: '#cccccc',

                    // Padding variables
                    nodePadding: '8px',       // REDUCED: was 20px
                    nodeMargin: '12px',       // Slightly reduced outer margin
                    edgeMargin: '8px'
                },

                fontFamily: '"Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                logLevel: 'error',
                suppressErrorRendering: true
            });

            // NHANCED: Universal content transformation (handles both formats)
            let mermaidContent = this.transformMermaidContentToHTML(item.content);

            // TORE: Original content for direction toggle
            const vizContainer = contentArea.closest('.viz-container');
            if (vizContainer) {
                vizContainer.setAttribute('data-original-content', item.content);
                vizContainer.setAttribute('data-chart-id', chartId);
            }

            console.log('🎯 Enhanced Mermaid transformation applied:', mermaidContent.substring(0, 200) + '...');

            const renderPromise = mermaid.render(`mermaid-${chartId}`, mermaidContent);
            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Mermaid rendering timeout')), 15000)
            );

            const { svg } = await Promise.race([renderPromise, timeoutPromise]);

            if (!svg || svg.trim() === '') {
                throw new Error('Mermaid returned empty SVG');
            }

            // RITICAL: Defend against Mermaid running against a 0-px container.
            // When that happens, Mermaid emits a viewBox of "0 0 0 450" (width=0),
            // which causes <circle r="-39"> (pie) and "Could not find a suitable
            // point for the given distance" (flowchart) on next render pass.
            // We parse the SVG string in isolation so a broken diagram never reaches
            // the live DOM; the user sees the deferred-render placeholder instead.
            const parsedForCheck = new DOMParser().parseFromString(svg, 'image/svg+xml');
            const parsedSvgEl = parsedForCheck.querySelector('svg');
            let mermaidProducedValidViewBox = true;
            if (parsedSvgEl) {
                const vb = parsedSvgEl.getAttribute('viewBox') || '';
                const m = vb.match(/^[\d.\-]+\s+[\d.\-]+\s+([\d.\-]+)\s+([\d.\-]+)/);
                if (m) {
                    const w = parseFloat(m[1]);
                    const h = parseFloat(m[2]);
                    if (!isFinite(w) || w <= 0 || !isFinite(h) || h <= 0) {
                        mermaidProducedValidViewBox = false;
                        console.warn(`⚠️ VIZ-V3: Mermaid produced broken viewBox "${vb}" — deferring render until container is sized`);
                    }
                }
            }

            if (!mermaidProducedValidViewBox) {
                // Don't insert the broken SVG.  If we still have retries left,
                // schedule a bounded re-render once the container has a real
                // size.  Otherwise, surface the failure to the user via the
                // existing error path instead of looping forever.
                if (attempt < MAX_MERMAID_RETRIES) {
                    this._scheduleMermaidRerender(item, contentArea, baseId, attempt + 1, MAX_MERMAID_RETRIES);
                } else {
                    console.error(
                        `❌ VIZ-V3: Mermaid produced a broken viewBox after ${attempt + 1} attempt(s); giving up.`
                    );
                    this.showMermaidError(
                        mermaidDiv,
                        new Error(
                            `Mermaid could not produce a valid SVG after ${attempt + 1} attempts. ` +
                            `The container may be 0-px wide or hidden.`
                        ),
                        item.content
                    );
                }
                return;
            }

            // EW (Jul 24 2026): Bail out before any DOM mutation if a newer
            // render has superseded us.  See render-token comment at the top
            // of this function for the race this guards against.
            if (contentArea._mermaidRenderToken !== myRenderToken) {
                console.log(`🔁 VIZ-V3: Mermaid render superseded (token ${myRenderToken} -> ${contentArea._mermaidRenderToken}); discarding stale SVG`);
                return;
            }

            mermaidDiv.innerHTML = svg;

            // OVERRIDE: Mermaid sets style="max-width: Xpx" based on the SVG's own
            // computed size.  When the container has zero visible width at render time
            // (e.g. off-DOM deferred render, or very narrow initial layout), this
            // produces a tiny max-width (as small as 80px) that makes the chart
            // illegible.  Force width:100% so the diagram always fills its parent.
            {
                const svgEl = mermaidDiv.querySelector('svg');
                if (svgEl) {
                    // Remove inline max-width from mermaid and let CSS control sizing
                    svgEl.style.maxWidth = '100%';
                    svgEl.style.width = '100%';
                    // Preserve the viewBox so the diagram still scales correctly
                }
            }

            // nhanced: Dynamic height calculation based on actual content
            const svgElement = mermaidDiv.querySelector('svg');
            if (svgElement) {
                this.applySimplifiedMermaidPostProcessing(svgElement);

                // nhanced: Dynamic height adjustment for wide diagrams
                setTimeout(() => {
                    const bbox = svgElement.getBBox();
                    if (bbox && bbox.width > bbox.height * 3) {
                        // For very wide diagrams, ensure minimum height
                        const minHeight = Math.max(400, bbox.height * 1.4);  // 0% more than baseline
                        svgElement.style.minHeight = minHeight + 'px';
                        console.log(`📏 Adjusted SVG height to ${minHeight}px for wide diagram`);
                    }

                    // EW: Auto-expand container for large/complex diagrams
                    const mermaidContainer = vizContainer.querySelector('.mermaid-container');
                    if (mermaidContainer && bbox) {
                        const isWideOrComplex = bbox.width > 800 ||
                            bbox.height > 600 ||
                            item.content.length > 500 ||
                            (item.content.match(/-->/g) || []).length > 15;

                        if (isWideOrComplex) {
                            mermaidContainer.classList.add('mermaid-expanded');
                            console.log('📏 Auto-expanded Mermaid container for complex diagram');
                        }
                    }
                }, 100);
            }

            if (vizContainer) {
                // EW (Jul 24 2026): Re-check token before attaching the action
                // bar.  If a newer render has superseded us between the SVG
                // write and this point, skip the action bar so the surviving
                // render owns the viz-container's UI state — otherwise the
                // user ends up with multiple action bars and the wrong one
                // bound to the (now-stale) chartId.
                if (contentArea._mermaidRenderToken !== myRenderToken) {
                    console.log(`🔁 VIZ-V3: Mermaid render superseded before action bar (token ${myRenderToken}); skipping`);
                    return;
                }
                vizContainer.setAttribute('data-color-theme', 'default');
                vizContainer.setAttribute('data-font-size', '14');
                this.addMermaidUnifiedActionBar(vizContainer, item.content, chartId);
            }

            console.log('nhanced Mermaid with improved approach rendered successfully');

        } catch (error) {
            // EW (Jul 24 2026): If a newer render has superseded us, swallow
            // the error silently — the new render owns the viz-container's
            // UI state and will surface its own success or error outcome.
            // Showing a stale error here would be misleading.
            if (contentArea._mermaidRenderToken !== myRenderToken) {
                console.log(`🔁 VIZ-V3: Mermaid render superseded in catch (token ${myRenderToken}); skipping stale error render`);
                return;
            }
            console.error(' Enhanced Mermaid rendering error:', error);

            // Translate Mermaid 10's internal layout-routing failure into a
            // user-actionable hint.  calcLabelPosition fires this when no
            // offset along an edge is free of collisions -- typically because
            // the staged layout canvas is too narrow for the diagram's edge
            // labels.  showMermaidError renders error.message verbatim, so we
            // wrap the original message with a hint that survives the UI.
            let userFacingError = error;
            const rawMessage = (error && error.message) ? error.message : '';
            if (/suitable point for the given distance/i.test(rawMessage)) {
                userFacingError = new Error(
                    'Diagram layout could not fit in the available width. ' +
                    'Try direction LR instead of TD, shorten node or edge ' +
                    'labels, or render in a wider panel. ' +
                    '(Mermaid: ' + rawMessage + ')'
                );
                userFacingError.stack = error.stack;
            }
            this.showMermaidError(mermaidDiv, userFacingError, item.content);
        }
    }

    // 6.1.1b - EW: Schedule a Mermaid re-render once the container has a real size.
    // Called when Mermaid was initialised against a 0-px container (deferred thread
    // render, hidden tab, collapsed panel) and produced a broken viewBox. We avoid
    // inserting the broken SVG into the live DOM by handling the deferral here
    // instead. A ResizeObserver watches the contentArea; once it has measurable
    // dimensions we re-run renderMermaidDirectly with a fresh chartId so Mermaid's
    // internal cache doesn't return the previous (broken) result.
    //
    // Bounded: the retry chartId is <baseId>-retry-<N> (never timestamped), and
    // renderMermaidDirectly is responsible for surfacing an error once the
    // per-render attempt budget is exhausted.
    _scheduleMermaidRerender(item, contentArea, baseId, nextAttempt, maxRetries) {
        // EW (Jul 24 2026): The calling renderMermaidDirectly has already
        // created an empty `.mermaid` div (L5052 + L5079) and appended it to
        // contentArea. When the broken-viewBox path fires the deferral, we
        // must remove that empty div before showing the placeholder — otherwise
        // the user sees an empty `.mermaid` body alongside the "Preparing…"
        // placeholder, exactly the symptom we are trying to eliminate.
        //
        // This is also defensive against a second concurrent renderMermaidDirectly
        // call (e.g. _processDeferredRenders in streamingTwoRule.js wipes
        // vizContentArea.innerHTML = '' at L280, then re-renders; or a stream-
        // finalize fires a second renderMermaidDirectly) that creates a fresh
        // empty `.mermaid` div mid-await.  Clearing both selectors here keeps
        // the contentArea tidy regardless of how we got here.
        contentArea.querySelectorAll('.mermaid, .mermaid-deferred-placeholder').forEach(d => d.remove());

        // Lightweight placeholder so the user knows the render is pending, not failed
        const placeholder = document.createElement('div');
        placeholder.className = 'mermaid-deferred-placeholder';
        placeholder.style.cssText = 'padding: 24px; text-align: center; color: var(--text-muted, #6e7681); font-style: italic; font-size: 0.95em;';
        placeholder.textContent = '⏳ Preparing diagram…';
        contentArea.appendChild(placeholder);

        // EW: Only require WIDTH — Mermaid measures width to compute radius/layout.
        // The container's height is 0 until Mermaid populates it (chicken-and-egg).
        // We deliberately do NOT check offsetParent: in some chat layouts (e.g. a
        // position: fixed ancestor, or a <dialog>/modal) offsetParent is null even
        // when the element IS visible and has a real width, which deadlocks us.
        const isWidthReady = (el) => {
            const r = el.getBoundingClientRect();
            return r.width > 1;
        };

        let observer = null;
        let timeoutId = null;
        let triggered = false;

        const cleanup = () => {
            if (observer) { observer.disconnect(); observer = null; }
            if (timeoutId) { clearTimeout(timeoutId); timeoutId = null; }
            if (placeholder.parentNode) { placeholder.parentNode.removeChild(placeholder); }
        };

        const tryRerender = () => {
            if (triggered) return;
            triggered = true;
            cleanup();
            // Stable, bounded retry id: never timestamped, never chained off a
            // previous retry id.  Always <originalBase>-retry-<attemptNumber>.
            const retryChartId = `${baseId}-retry-${nextAttempt}`;
            console.log(`✅ VIZ-V3: Container now sized — retrying Mermaid render (attempt ${nextAttempt}/${maxRetries})`);
            this.renderMermaidDirectly(item, contentArea, retryChartId, {
                baseId,
                attempt: nextAttempt
            }).catch(err => {
                console.error('❌ VIZ-V3: Mermaid re-render failed:', err);
            });
        };

        // ResizeObserver fires when the container gets a real size
        if (typeof ResizeObserver !== 'undefined') {
            observer = new ResizeObserver((entries) => {
                for (const entry of entries) {
                    if (entry.contentRect.width > 1) {
                        tryRerender();
                        return;
                    }
                }
            });
            observer.observe(contentArea);

            // RITICAL: ResizeObserver only fires on CHANGES, not initial size.
            // Probe immediately so we don't miss the case where the container
            // became sized before/during our observe() call.
            if (isWidthReady(contentArea)) {
                tryRerender();
                return;
            }
        } else {
            // Fallback: poll with rAF for older browsers
            const poll = () => {
                if (triggered) return;
                if (isWidthReady(contentArea)) {
                    tryRerender();
                } else {
                    requestAnimationFrame(poll);
                }
            };
            requestAnimationFrame(poll);
        }

        // Safety net: give up after 8s so we never leave a placeholder forever.
        // Log the last-seen size + a few visibility hints so we can tell from
        // the console whether the container is genuinely 0-px (deep layout
        // issue) or just hidden (display:none on an ancestor).  Also render a
        // visible error inline so the user is not left staring at a blank area.
        timeoutId = setTimeout(() => {
            if (triggered) return;
            const rect = contentArea.getBoundingClientRect();
            const cs = window.getComputedStyle(contentArea);
            const parent = contentArea.parentElement;
            const parentCs = parent ? window.getComputedStyle(parent) : null;
            console.error(
                '❌ VIZ-V3: Container never got a real size after 8s — giving up on re-render',
                {
                    rect: { w: rect.width, h: rect.height },
                    contentArea: { display: cs.display, visibility: cs.visibility, position: cs.position },
                    parent: parent ? { display: parentCs.display, visibility: parentCs.visibility, position: parentCs.position, tag: parent.tagName } : null,
                }
            );
            cleanup();
            const errorDiv = document.createElement('div');
            errorDiv.className = 'mermaid-render-timeout';
            errorDiv.style.cssText = 'padding: 16px; color: var(--accent-red, #ef4444); font-size: 13px; text-align: center; border: 1px dashed rgba(239, 68, 68, 0.4); border-radius: 6px; background: rgba(239, 68, 68, 0.08);';
            errorDiv.textContent = '⚠️ Diagram could not be rendered (container never reached a measurable size).';
            contentArea.appendChild(errorDiv);
        }, 8000);
    }

    // 6.1.2
    async renderMermaid(item, container, chartId) {
        if (!window.mermaid) {
            throw new Error('Mermaid library not loaded');
        }

        const mermaidDiv = document.createElement('div');
        mermaidDiv.id = chartId;
        mermaidDiv.className = 'mermaid';
        mermaidDiv.style.cssText = `
            width: 100%;
            height: auto;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        `;

        container.appendChild(mermaidDiv);

        try {
            // NHANCED: Initialize with default color theme
            const defaultTheme = this.getMermaidColorThemes().default;

            // EW (Jul 22 2026): Always-white chart canvas. Drop all isDark
            // branching so chart text/fills read against the constant white
            // canvas regardless of UI theme. See
            // VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md.
            mermaid.initialize({
                startOnLoad: false,
                theme: 'base',
                securityLevel: 'loose',
                htmlLabels: true,
                maxTextSize: 50000,
                maxEdges: 2000,

                // Conservative spacing configuration (restored to prior working values)
                flowchart: {
                    htmlLabels: true,
                    useMaxWidth: true,
                    curve: 'basis',
                    padding: 10,
                    nodeSpacing: 40,
                    rankSpacing: 40,
                    diagramPadding: 12,
                    // Additional spacing controls
                    edgePadding: 8,
                    nodePadding: 15,
                    textHeight: 20,
                    lineHeight: 1.6
                },

                // NHANCED: Better theme variables
                themeVariables: {
                    primaryColor: '#f0f0f0',
                    primaryTextColor: '#24292f',
                    primaryBorderColor: '#cccccc',
                    lineColor: '#656d76',
                    backgroundColor: '#ffffff',

                    // Text and node sizing variables (keep conservative defaults)
                    textColor: '#24292f',
                    nodeTextColor: '#24292f',
                    nodeBkg: '#f0f0f0',
                    nodeBorder: '#cccccc',

                    // Padding and spacing variables
                    nodePadding: '15px',
                    nodeMargin: '8px',
                    edgeMargin: '8px'
                },

                fontFamily: '"Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                logLevel: 'error',
                suppressErrorRendering: true
            });

            const { svg } = await mermaid.render(`mermaid-${chartId}`, item.content);
            mermaidDiv.innerHTML = svg;

            // EW: Auto-expand container for large/complex diagrams
            const renderedSvg = mermaidDiv.querySelector('svg');
            if (renderedSvg) {
                setTimeout(() => {
                    const bbox = renderedSvg.getBBox();
                    const mermaidContainer = container.querySelector('.mermaid-container');

                    if (mermaidContainer && bbox) {
                        const isWideOrComplex = bbox.width > 800 ||
                            bbox.height > 600 ||
                            item.content.length > 500 ||
                            (item.content.match(/-->/g) || []).length > 15;

                        if (isWideOrComplex) {
                            mermaidContainer.classList.add('mermaid-expanded');
                            console.log('📏 Auto-expanded Mermaid container for complex diagram (renderMermaid)');
                        }
                    }
                }, 100);
            }

            // Remove custom SVG post-processing - let Mermaid render with its native sizing
            // and theming. Post-processing was causing oversized node boxes and
            // unexpected artifacts. If we need theme adjustments later we should
            // perform them inside Mermaid's themeVariables only.

            // Set default color theme attribute
            container.setAttribute('data-color-theme', 'default');

            this.addMermaidUnifiedActionBar(container, item.content, chartId);

        } catch (error) {
            console.error('Mermaid rendering error:', error);
            this.showMermaidError(mermaidDiv, error, item.content);
        }
    }

    // NHANCED: 6.1.3 Comprehensive HTML transformation like ALTERNATIVE file
    // 6.1.2 - FIXED: Universal Mermaid content transformation (no conflicts)
    //
    // Mermaid 10.6.1 asymmetric-shape syntax reference (EW, Jul 23 2026):
    //   A[/Lean right/]                -> lean_right
    //   A[\Lean left\]                 -> lean_left
    //   A{Odd Shape}                   -> rect_left_inv_arrow
    //   A[/Trapezoid one\]             -> trapezoid
    //   A[\Trapezoid alt/]             -> inv_trapezoid
    // `A>Asymmetric Right"]` is INVALID in 10.6.1 — `>` is not a
    // recognised shape delimiter. Do not auto-correct malformed input
    // because the intended shape cannot be inferred safely; let Mermaid
    // surface its normal syntax error. See VISUALIZATION_MERMAID_BOLD_
    // SHAPE_SIZING_FIX_JULY23_2026.md at the repo root for the full
    // investigation and verified DOM-shape selectors.
    transformMermaidContentToHTML(content) {
        if (!content || typeof content !== 'string') return content;

        try {
            console.log('🔄 FIXED Mermaid transformation starting...');

            // TEP 1: Handle direct \n in the content
            let transformedContent = content.replace(/\\n/g, '\n');

            // EW: STEP 1.5: Fix Gantt / Journey chart syntax issues when needed
            // Both diagram types use  section Name  +  task: score: actor  syntax — a colon
            // inside a section label (e.g. "section Day 1-2: Preparation") confuses the
            // parser into treating the text after the colon as 'taskData'.
            const trimmedForCheck = transformedContent.trim();
            if (trimmedForCheck.startsWith('gantt') || trimmedForCheck.startsWith('journey')) {
                const hasProblematicSections = transformedContent.includes('section') &&
                    (transformedContent.match(/section[^\n]*:/g) ||   // Any section line with a colon
                     transformedContent.includes('taskData'));

                if (hasProblematicSections) {
                    console.log('🔄 Detected problematic section colons in', trimmedForCheck.split('\n')[0], '— applying fixes...');
                    transformedContent = this.fixGanttSyntax(transformedContent);
                } else {
                    console.log('Chart section syntax appears clean, skipping fixes');
                }
            }

            // EW: STEP 1.6: Fix subgraph spacing issues
            if (transformedContent.includes('subgraph')) {
                console.log('🔄 Fixing subgraph spacing...');
                transformedContent = this.fixSubgraphSpacing(transformedContent);
            }

            // TEP 2: FIXED node label processor (no conflicts)
            function processNodeLabel(label) {
                // Skip if already processed
                if (label.includes('mermaid-br') || label.includes('mermaid-bold') ||
                    label.includes('mermaid-italic') || label.includes('mermaid-code')) {
                    console.log('abel already processed, skipping');
                    return label;
                }

                let processedLabel = label;

                // TEP 1: Clean numeric values and special chars FIRST
                processedLabel = processedLabel
                    .replace(/\b(\d{1,3}),(\d{3})\b/g, '$1$2')
                    .replace(/\b(\d{1,3}),(\d{3}),(\d{3})\b/g, '$1$2$3')
                    .replace(/×/g, '&times;')
                    .replace(/÷/g, '&divide;')
                    .replace(/±/g, '&plusmn;');

                // TEP 2: Process bullets BEFORE line breaks (critical!)
                processedLabel = processedLabel
                    .replace(/^\s*[•·▪▫]\s+(.+)$/gm, '<span class="mermaid-bullet">• $1</span>')
                    .replace(/^\s*[-]\s+(?!>)(.+)$/gm, '<span class="mermaid-bullet">• $1</span>')
                    .replace(/^\s*\d+\.\s+(.+)$/gm, '<span class="mermaid-bullet">1. $1</span>');

                // TEP 3: Process bold. EW (Jul 23 2026): preserve native
                // <b>/<strong> tags as-is when the user already wrote them.
                // The browser HTML parser closes <b> and <strong> correctly
                // before any following <br/>, so injecting a "mermaid-bold"
                // class adds no styling value (the foreignObject CSS at
                // business-ai-platform-v2.html L10878-L10888 already
                // targets bare `strong` and `b`) and may desynchronise
                // Mermaid's downstream label-tokenisation pass — bold
                // appeared to "leak" past a <br/> into the next line in
                // the Jul 23 investigation. Only markdown **bold** is
                // converted, to plain <strong>; native tags stay native.
                if (!/<(?:strong|b)\b/i.test(processedLabel)) {
                    processedLabel = processedLabel.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                }
                // Track whether the label now contains any bold markup so
                // the <br> normalisation below can emit plain <br/> tags
                // (no class) when bold is present.
                const hasBoldMarkup = /<(?:strong|b)\b/i.test(processedLabel);

                if (!processedLabel.includes('<em') && !processedLabel.includes('<i>')) {
                    processedLabel = processedLabel.replace(/(?<!\*)\*([^*]+?)\*(?!\*)/g, '<em class="mermaid-italic">$1</em>');
                }
                processedLabel = processedLabel
                    .replace(/<(em|i)(?![^>]*class\s*=\s*["\'][^"\']*mermaid[^"\']*["\'])[^>]*>(.*?)<\/(em|i)>/gi,
                        '<em class="mermaid-italic">$2</em>');

                if (!processedLabel.includes('<code')) {
                    processedLabel = processedLabel.replace(/`(.*?)`/g, '<code class="mermaid-code">$1</code>');
                }
                processedLabel = processedLabel
                    .replace(/<code(?![^>]*class\s*=\s*["\'][^"\']*mermaid[^"\']*["\'])[^>]*>(.*?)<\/code>/gi,
                        '<code class="mermaid-code">$1</code>');

                // TEP 4: Now convert line breaks (ONLY ONCE!)
                // Temporarily protect bullet spans
                const bulletLines = [];
                processedLabel = processedLabel.replace(/(<span class="mermaid-bullet">.*?<\/span>)/g, (match) => {
                    bulletLines.push(match);
                    return `__BULLET_${bulletLines.length - 1}__`;
                });

                // EW (Jul 22 2026): Normalize any <br> / <br/> self-closing tags
                // already in the source. The original conversion below only
                // handled literal \n — any <br/> written by the AI or user
                // (e.g. stadium and subroutine labels like
                // `(["Line 1<br/>Line 2"])`) was passed through unchanged,
                // and Mermaid 10.6.1's HTML-label parser would silently
                // drop or join these on certain shape paths, producing
                // "Line 1Line 2" without line breaks. By normalizing all
                // <br> variants to <br class="mermaid-br"/> here, both
                // existing tags and newlines converge on the same
                // well-formed marker that Mermaid reliably renders. The
                // .mermaid-br class also makes the bullet-spacing CSS
                // rule at L121 work uniformly.
                //
                // EW (Jul 23 2026): when bold markup is present in the
                // label, emit plain <br/> tags instead of class-bearing
                // ones. Mixing class-bearing <br> with bold markup caused
                // Mermaid's label-tokenisation pass to drop or merge
                // lines after bold spans (the user reported
                // `text<b>bold</b><br/>plain` losing the line break and
                // showing "plain" as bold). Plain <br/> avoids the
                // class injection while still letting Mermaid's HTML
                // parser handle the line break.
                processedLabel = processedLabel.replace(/<br\s*\/?\s*>/gi,
                    hasBoldMarkup ? '<br/>' : '<br class="mermaid-br"/>');

                // Convert line breaks - normalize first, then convert once
                processedLabel = processedLabel
                    .replace(/\\n/g, '\n')  // Normalize escaped newlines
                    .replace(/\n/g, hasBoldMarkup ? '<br/>' : '<br class="mermaid-br"/>');  // Convert ONCE

                // Restore bullet lines
                processedLabel = processedLabel.replace(/__BULLET_(\d+)__/g, (match, index) => {
                    return bulletLines[parseInt(index)];
                });

                // TEP 5: Final cleanup - remove any <br> around bullets
                processedLabel = processedLabel
                    .replace(/<br\s+class=["']mermaid-br["']\s*\/?>\s*(<span class="mermaid-bullet">)/gi, '$1')
                    .replace(/(<span class="mermaid-bullet">[^<]*<\/span>)\s*<br\s+class=["']mermaid-br["']\s*\/?>/gi, '$1');

                // TEP 6: Preserve special characters
                processedLabel = processedLabel
                    .replace(/\$([0-9,]+)/g, '$$1')
                    .replace(/([0-9]+)%/g, '$1%')
                    .replace(/@([a-zA-Z0-9_]+)/g, '@$1');

                return processedLabel;
            }

            // TEP 3: Process different node types (FIXED - no conflicts)

            // Process [square bracket] nodes
            transformedContent = transformedContent.replace(/\[([^\[\]]*(?:\[[^\]]*\][^\[\]]*)*)\]/gs, function (match, label) {
                return `[${processNodeLabel(label)}]`;
            });

            // Process {{curly bracket}} nodes  
            transformedContent = transformedContent.replace(/\{\{([^{}]*(?:\{[^}]*\}[^{}]*)*)\}\}/gs, function (match, label) {
                return `{{${processNodeLabel(label)}}}`;
            });

            // Process [[double square bracket]] nodes
            transformedContent = transformedContent.replace(/\[\[([^\[\]]*(?:\[[^\]]*\][^\[\]]*)*)\]\]/gs, function (match, label) {
                return `[[${processNodeLabel(label)}]]`;
            });

            // Process (parenthesis) nodes - but skip edge labels
            transformedContent = transformedContent.replace(/\(([^()]*(?:\([^)]*\)[^()]*)*)\)/gs, function (match, label) {
                // Skip if this looks like an edge with a label, not a node
                if (match.includes('-->') || match.includes('---') || match.includes('-.->')) {
                    return match;
                }
                return `(${processNodeLabel(label)})`;
            });

            // Handle quoted node labels
            transformedContent = transformedContent.replace(/(\w+)\["([^"]*)"\]/g, (match, nodeId, nodeContent) => {
                const processedContent = processNodeLabel(nodeContent);
                return `${nodeId}["${processedContent}"]`;
            });

            console.log('IXED Mermaid transformation completed without conflicts');
            return transformedContent;

        } catch (error) {
            console.error(' Error in FIXED Mermaid content transformation:', error);
            console.error('Content that caused error:', content);
            return content || 'graph TD\nA[Error in processing]';
        }
    }

    // EW: Comprehensive JSON normalization and repair
    normalizeAndRepairJSON(jsonString) {
        // Silently normalize - only log on errors
        if (!jsonString || typeof jsonString !== 'string') {
            throw new Error('Invalid JSON input: not a string');
        }

        let normalizedJson = jsonString;

        try {
            // TEP 1: Fix common number formatting issues

            // Fix arrays with +/- numbers: [-2, +2, +3] -> [-2, 2, 3]
            normalizedJson = normalizedJson.replace(/:\s*\[\s*([+-]?\d+(?:\.\d+)?(?:\s*,\s*[+-]?\d+(?:\.\d+)?)*)\s*\]/g, (match, numbers) => {
                const cleanNumbers = numbers
                    .split(',')
                    .map(num => {
                        const trimmed = num.trim();
                        // Remove leading + from positive numbers, keep - for negative
                        return trimmed.startsWith('+') ? trimmed.substring(1) : trimmed;
                    })
                    .join(', ');
                return `: [${cleanNumbers}]`;
            });

            // Fix individual number values: "value": +123 -> "value": 123
            normalizedJson = normalizedJson.replace(/:\s*\+(\d+(?:\.\d+)?)/g, ': $1');

            // TEP 2: Fix object property formatting
            normalizedJson = normalizedJson.replace(/,\s*\+(\d)/g, ', $1'); // Fix: , +2 -> , 2
            normalizedJson = normalizedJson.replace(/\[\s*\+(\d)/g, '[$1');   // Fix: [+2 -> [2

            // TEP 3: Preserve display text (don't modify text intended for display)
            // Text arrays should keep their + signs for display purposes
            const textMatches = [];
            normalizedJson = normalizedJson.replace(/"text":\s*\[[^\]]+\]/g, (match, offset) => {
                textMatches.push({ match, offset });
                return `__TEXT_PLACEHOLDER_${textMatches.length - 1}__`;
            });

            // TEP 4: More aggressive number cleanup
            normalizedJson = normalizedJson
                .replace(/\+(\d+(?:\.\d+)?)/g, '$1')  // Remove all remaining + signs before numbers
                .replace(/([+-]?\d+(?:\.\d+)?)\s*,/g, '$1,') // Clean spacing around commas
                .replace(/,\s*([+-]?\d+(?:\.\d+)?)/g, ', $1'); // Ensure proper spacing after commas

            // TEP 5: Restore preserved text content
            textMatches.forEach((item, index) => {
                normalizedJson = normalizedJson.replace(`__TEXT_PLACEHOLDER_${index}__`, item.match);
            });

            // TEP 6: Final JSON structure validation
            normalizedJson = normalizedJson
                .replace(/,\s*}/g, '}')      // Remove trailing commas before }
                .replace(/,\s*\]/g, ']')     // Remove trailing commas before ]
                .replace(/\s+/g, ' ')        // Normalize whitespace
                .trim();

            return normalizedJson;

        } catch (error) {
            console.error(' Error during JSON normalization:', error);
            throw new Error(`JSON normalization failed: ${error.message}`);
        }
    }

    // EW: Safe JSON parsing with multiple fallback strategies
    safeJSONParse(jsonString) {
        if (!jsonString) {
            throw new Error('Empty JSON string provided');
        }

        let firstError;

        // Strategy 1: Try direct parsing
        try {
            return JSON.parse(jsonString);
        } catch (directError) {
            firstError = directError;
            // Try normalization without warning for expected +/- notation
        }

        // Strategy 2: Try with normalization
        try {
            const normalizedJson = this.normalizeAndRepairJSON(jsonString);
            return JSON.parse(normalizedJson);
        } catch (normalizedError) {
            // Only log detailed error in development
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.error('❌ JSON parsing failed after normalization');
                console.error('📄 Content preview:', jsonString.substring(0, 200) + '...');
            }

            throw new Error(`All JSON parsing strategies failed. Original error: ${firstError.message}, Normalized error: ${normalizedError.message}`);
        }
    }

    // EW: Fix Gantt chart syntax issues
    fixGanttSyntax(content) {
        console.log('🔧 Applying Gantt chart syntax fixes...');
        console.log('🔧 Original content length:', content.length, 'characters');

        let fixedContent = content;

        try {
            // RITICAL PRE-FIX: Handle the specific "taskData" error
            // This error suggests the parser is seeing unexpected content after section names

            // Split into lines for processing
            const lines = fixedContent.split('\n');
            const fixedLines = [];
            let inGantt = false;
            let isJourney = false;

            for (let i = 0; i < lines.length; i++) {
                let line = lines[i].trim();

                // Track if we're in a gantt or journey section (both use same section syntax)
                if (line.startsWith('gantt') || line.startsWith('journey')) {
                    inGantt = true;
                    isJourney = line.startsWith('journey');
                    fixedLines.push(line);
                    continue;
                }

                // Skip empty lines (but preserve them)
                if (!line) {
                    fixedLines.push('');
                    continue;
                }

                // RITICAL FIX: More comprehensive section line handling  
                if (line.startsWith('section') && inGantt) {
                    console.log('🔧 Processing section line:', line);

                    // Extract section name
                    let sectionName = line.replace(/^section\s*/, '').trim();

                    // NHANCED PROBLEM DETECTION: More aggressive detection for 'taskData' errors
                    const hasProblems = sectionName.includes(':') ||         // Any colon (common cause)
                        sectionName.match(/[^\w\s:\-]/) ||
                        sectionName.includes('--') ||
                        sectionName.includes('taskData') ||
                        sectionName.match(/:\s+\S+/) ||       // Extra content after colon
                        sectionName.length > 50 ||            // Very long section names
                        sectionName.match(/\s{3,}/);          // Multiple consecutive spaces

                    if (hasProblems) {
                        console.log('🔧 Section has syntax issues, cleaning:', sectionName);

                        // NHANCED CLEANING: Aggressive cleaning for 'taskData' errors
                        sectionName = sectionName
                            .replace(/[^\w\s:\-]/g, ' ')     // Replace problematic chars with spaces
                            .replace(/[-]{2,}/g, ' ')        // Replace multiple dashes with spaces  
                            .replace(/:\s+.*$/, '')          // Remove everything after "colon + space"
                            .replace(/-+\s*$/, '')           // Remove trailing dashes
                            .replace(/\s+-+.*$/, '')         // Remove " -" and everything after
                            .replace(/\s*-+\s*$/, '')        // Remove any trailing dash patterns
                            .replace(/\s+/g, ' ')            // Normalize multiple spaces
                            .trim();

                        // DDITIONAL: Truncate very long section names
                        if (sectionName.length > 30) {
                            sectionName = sectionName.substring(0, 30).trim();
                            console.log('🔧 Truncated long section name:', sectionName);
                        }

                        // ALLBACK: If still problematic, create simple section name
                        if (!sectionName || sectionName.length === 0) {
                            const sectionCount = fixedLines.filter(l => l.trim().startsWith('section')).length + 1;
                            sectionName = `Phase ${sectionCount}`;
                            console.warn('⚠️ Created safe fallback section name:', sectionName);
                        }

                        // Reconstruct section line
                        line = `section ${sectionName}`;
                        console.log('🔧 Fixed section line:', line);
                    } else {
                        console.log('ection line is clean, keeping as-is:', line);
                    }

                    fixedLines.push(line);
                    continue;
                }

                // IX 1: Ensure proper task syntax format
                // Only apply Gantt task rewriting for gantt diagrams, NOT journey —
                // journey task format  "task: score: actor"  is already valid.
                if (line && inGantt && !isJourney &&
                    !line.startsWith('gantt') &&
                    !line.startsWith('title') &&
                    !line.startsWith('dateFormat') &&
                    !line.startsWith('section') &&
                    !line.startsWith('%') &&
                    !line.startsWith('--') &&
                    line.includes(':')) {

                    console.log('🔧 Processing task line:', line);

                    // IX 2: Ensure task format is: Task Name :status, id, start, duration
                    // Split by first colon to separate name from definition
                    const colonIndex = line.indexOf(':');
                    if (colonIndex > 0) {
                        const taskName = line.substring(0, colonIndex).trim();
                        const taskDef = line.substring(colonIndex + 1).trim();

                        // IX 3: Clean up common syntax issues
                        let cleanedDef = taskDef;

                        // RITICAL: If task definition is missing, create a valid one
                        if (!cleanedDef || cleanedDef === '') {
                            // Create a basic task definition
                            const taskId = taskName.toLowerCase().replace(/[^a-z0-9]/g, '');
                            cleanedDef = `task${i}, ${taskId}, 1d`;
                            console.log('🔧 Created missing task definition:', cleanedDef);
                        }

                        // Fix spacing around commas
                        cleanedDef = cleanedDef.replace(/\s*,\s*/g, ', ');

                        // Split the definition parts
                        const parts = cleanedDef.split(',').map(p => p.trim());

                        if (parts.length >= 1) {
                            // NHANCED: Better task definition reconstruction
                            let status = '';
                            let id = '';
                            let startDate = '';
                            let duration = '';

                            // IX: Determine if first part is a status or ID
                            const firstPart = parts[0].trim();
                            if (firstPart.match(/^(active|done|crit|milestone)$/)) {
                                // First part is a status
                                status = firstPart;
                                id = parts.length > 1 ? parts[1].trim() : '';
                                startDate = parts.length > 2 ? parts[2].trim() : '';
                                duration = parts.length > 3 ? parts[3].trim() : '';
                            } else {
                                // First part is likely an ID (no status specified)
                                status = '';
                                id = firstPart;
                                startDate = parts.length > 1 ? parts[1].trim() : '';
                                duration = parts.length > 2 ? parts[2].trim() : '';
                            }

                            // lean and validate each part
                            // Clean ID format (no spaces, alphanumeric + underscore)
                            id = id.replace(/[^a-zA-Z0-9_]/g, '') || `task${i}`;

                            // Validate start date or 'after' reference
                            if (startDate) {
                                if (startDate.match(/\d{4}-\d{2}-\d{2}/)) {
                                    // Valid date format, keep as is
                                } else if (startDate.startsWith('after')) {
                                    // Already has 'after', just clean the referenced ID
                                    const afterMatch = startDate.match(/after\s+(.+)/);
                                    if (afterMatch) {
                                        const referencedId = afterMatch[1].trim().replace(/[^a-zA-Z0-9_]/g, '');
                                        startDate = `after ${referencedId}`;
                                    }
                                } else if (startDate.match(/^[a-zA-Z0-9_\s]+$/)) {
                                    // Looks like an ID reference, add 'after' and clean the ID
                                    const cleanRef = startDate.replace(/[^a-zA-Z0-9_]/g, '');
                                    if (cleanRef) {
                                        startDate = `after ${cleanRef}`;
                                    }
                                }
                            }

                            // Ensure duration format
                            if (duration && !duration.includes('d') && !duration.includes('h')) {
                                if (duration.match(/^\d+$/)) {
                                    duration = `${duration}d`;
                                }
                            }

                            // RITICAL: Reconstruct with proper Gantt syntax
                            // Format: TaskName : [status,] id, start, duration
                            const defParts = [];
                            if (status) defParts.push(status);
                            if (id) defParts.push(id);
                            if (startDate) defParts.push(startDate);
                            if (duration) defParts.push(duration);

                            if (defParts.length >= 2) { // At minimum need id and one other part
                                cleanedDef = defParts.join(', ');
                            } else {
                                // Fallback: create basic task definition
                                cleanedDef = `task${i}, 1d`;
                                console.warn(`⚠️ Created fallback task definition for: ${taskName}`);
                            }
                        }

                        // Reconstruct the line with proper format
                        line = `    ${taskName} : ${cleanedDef}`;
                        console.log('🔧 Fixed task line:', line);
                    }

                    fixedLines.push(line);
                    continue;
                }

                // IX 4: Handle other gantt directives  
                if (inGantt && (line.startsWith('title') || line.startsWith('dateFormat') || line.startsWith('%'))) {
                    // Ensure proper indentation and format
                    if (line.startsWith('dateFormat')) {
                        // Validate dateFormat syntax
                        if (!line.includes('YYYY-MM-DD') && !line.includes('DD-MM-YYYY') && !line.includes('MM-DD-YYYY')) {
                            console.warn('⚠️ Unusual dateFormat detected:', line);
                        }
                    }
                    fixedLines.push(`    ${line}`);
                    continue;
                }

                // For all other lines in gantt context, add basic indentation
                if (inGantt && line && !line.startsWith('    ')) {
                    fixedLines.push(`    ${line}`);
                } else {
                    fixedLines.push(line);
                }
            }

            const result = fixedLines.join('\n');
            console.log('🔧 Fixed Gantt content:', result);
            return result;

        } catch (error) {
            console.error(' Error fixing Gantt syntax:', error);
            return content; // Return original if fixing fails
        }
    }

    // EW: Fix subgraph spacing and layout issues
    fixSubgraphSpacing(content) {
        console.log('🔧 Applying subgraph spacing fixes...');

        let fixedContent = content;

        try {
            // Split into lines for processing
            const lines = fixedContent.split('\n');
            const fixedLines = [];

            for (let i = 0; i < lines.length; i++) {
                let line = lines[i];
                const trimmedLine = line.trim();

                // IX 1: Add spacing after subgraph declarations
                if (trimmedLine.startsWith('subgraph ')) {
                    fixedLines.push(line);
                    // Add an empty line after subgraph title for better spacing
                    fixedLines.push('');
                    continue;
                }

                // IX 2: Add spacing before 'end' statements
                if (trimmedLine === 'end') {
                    // Add empty line before 'end' for better separation
                    if (fixedLines.length > 0 && fixedLines[fixedLines.length - 1].trim() !== '') {
                        fixedLines.push('');
                    }
                    fixedLines.push(line);
                    // Add empty line after 'end' for separation between subgraphs
                    fixedLines.push('');
                    continue;
                }

                // IX 3: Ensure proper spacing for node declarations with HTML content
                if (trimmedLine.includes('[') && trimmedLine.includes('div style')) {
                    // For nodes with HTML content, ensure proper spacing
                    fixedLines.push('');
                    fixedLines.push(line);
                    continue;
                }

                fixedLines.push(line);
            }

            fixedContent = fixedLines.join('\n');

            // IX 4: Clean up multiple consecutive empty lines (but keep some for spacing)
            fixedContent = fixedContent.replace(/\n\s*\n\s*\n\s*\n/g, '\n\n\n');

            // IX 5: Add CSS-like margin hints for better subgraph rendering
            // This won't change the syntax but may help with rendering engine spacing
            fixedContent = fixedContent.replace(
                /subgraph\s+"([^"]+)"/g,
                (match, title) => {
                    // Keep original but add spacing hints in a way that doesn't break syntax
                    return `subgraph "${title}"`;
                }
            );

            console.log('ubgraph spacing fixes applied');
            console.log('Fixed content preview:', fixedContent.substring(0, 300) + '...');

            return fixedContent;

        } catch (error) {
            console.error(' Error fixing subgraph spacing:', error);
            return content; // Return original if fixing fails
        }
    }

    // 6.1.4 - ENHANCED: Enhanced post-processing with intelligent node sizing
    applySimplifiedMermaidPostProcessing(svgElement) {
        console.log('🎨 Applying enhanced post-processing...');

        // Ensure bullet labels render tightly without stray manual line breaks
        stripBreaksAroundBullets(svgElement);

        // EW (Jul 22 2026): Chart-type detection. The rect inflation
        // heuristic below (60px height floor at L5764 + lineCount*30 floor
        // at L5762 + width-scaling horizontalPadding at L5754) is designed
        // for flowchart nodes, where foreignObject labels need generous
        // padding inside the node rect. But it inflates pie legend rects,
        // git graph commit rects, and gantt task rects to ~60-100px tall
        // — far larger than the text they contain. The user reported this
        // as "the boxes around the text are much larger than the text"
        // across pie legend, git graph branches/commits, and gantt tasks.
        // Detect non-flowchart diagrams and skip the inflation while
        // preserving stroke styling. See
        // VISUALIZATION_RECT_TIGHTENING_FIX_JULY22_2026.md.
        const isPieChart = !!svgElement.querySelector('g.pieGroup');
        const isGitGraph = !!svgElement.querySelector('g.commit, g.branch, [class*="commit-"]');
        const isGantt = !!svgElement.querySelector('g.section, g.task, [class*="section-"], [class*="task-"]');
        const skipRectInflation = isPieChart || isGitGraph || isGantt;

        try {
            // Clamp overly large HTML label fonts in narrow, non-fullscreen containers
            const container = svgElement.closest('.viz-container');
            const isFullscreen = !!svgElement.closest('.mermaid-fullscreen-container');
            if (container && !isFullscreen) {
                const host = container.querySelector('.viz-content-area') || container;
                const hostRect = host.getBoundingClientRect?.() || { width: 0 };
                const narrow = hostRect.width && hostRect.width < 520; // typical chat bubble width
                if (narrow) {
                    const foInners = svgElement.querySelectorAll('foreignObject div, foreignObject span, foreignObject p');
                    foInners.forEach((el) => {
                        const cs = window.getComputedStyle(el);
                        const fs = parseFloat(cs.fontSize) || 0;
                        if (fs > 15) {
                            el.style.fontSize = '15px';
                        }
                    });
                    console.log('🔧 Clamped HTML label fonts for narrow container');
                }
            }
        } catch (e) {
            console.warn('⚠️ Font clamp pass skipped:', e);
        }

        // NHANCED: Better text styling that preserves dynamic sizing
        // EW (Jul 22 2026): Canvas is always white, so text fill is always
        // dark (was: isDark ? '#e6edf3' : '#24292f'). The isDark parameter
        // has been removed; callers that still pass it harmlessly ignore.
        // See VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md.
        const textElements = svgElement.querySelectorAll('text, tspan');
        textElements.forEach(text => {
            text.setAttribute('fill', '#24292f');
            text.setAttribute('font-weight', '500');
            text.setAttribute('font-family', '"Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif');
            // RITICAL: Don't override font-size - let Mermaid handle it naturally
        });

        // nhanced: Intelligent node sizing based on actual content
        const rects = svgElement.querySelectorAll('rect');
        rects.forEach(rect => {
            const width = parseFloat(rect.getAttribute('width') || 0);
            const height = parseFloat(rect.getAttribute('height') || 0);

            if (width > 10 && height > 10) {
                // Allow label-container rects to expand height to avoid clipping, but avoid heavy styling/width changes
                const cls = (rect.getAttribute('class') || '').toLowerCase();
                const isLabelContainerRect = cls.includes('label-container');

                // EW (Jul 22 2026): Skip aggressive rect inflation for
                // non-flowchart diagrams (pie, git graph, gantt). Mermaid
                // already sizes these rects correctly; the 60px floor +
                // width-scaling padding over-shoots by 3-5x, producing
                // huge gray boxes around short labels. Apply minimal
                // stroke styling (preserves the always-white canvas fix)
                // and return early to skip the size/position mutation.
                if (skipRectInflation) {
                    if (!isLabelContainerRect) {
                        rect.setAttribute('stroke', '#cccccc');
                        rect.setAttribute('stroke-width', '1');
                    }
                    return;
                }

                // nhanced: Find associated text content for this rect
                const rectX = parseFloat(rect.getAttribute('x') || 0);
                const rectY = parseFloat(rect.getAttribute('y') || 0);
                const rectCenterX = rectX + width / 2;
                const rectCenterY = rectY + height / 2;

                // Find text elements within or near this rectangle
                let maxTextHeight = 0;
                let lineCount = 1;
                let hasHtmlContent = false;
                let contentComplexity = 1;
                let averageFontSize = 14; // EFAULT: Fallback font size
                let fontSizeCount = 0;

                // EW: Accurate bounds measurement using getBBox to prevent bottom clipping
                let measuredTop = Number.POSITIVE_INFINITY;
                let measuredBottom = Number.NEGATIVE_INFINITY;
                let measuredLeft = Number.POSITIVE_INFINITY;
                let measuredRight = Number.NEGATIVE_INFINITY;
                let measuredAny = false;
                const inflatedRect = { x: rectX, y: rectY, width, height };
                const overlapMargin = Math.min(16, Math.max(8, width * 0.08));
                const overlaps = (a, b, margin = 0) => {
                    return (
                        a.x + a.width >= b.x - margin &&
                        b.x + b.width >= a.x - margin &&
                        a.y + a.height >= b.y - margin &&
                        b.y + b.height >= a.y - margin
                    );
                };
                const considerBounds = (bbox) => {
                    measuredAny = true;
                    measuredTop = Math.min(measuredTop, bbox.y);
                    measuredBottom = Math.max(measuredBottom, bbox.y + bbox.height);
                    measuredLeft = Math.min(measuredLeft, bbox.x);
                    measuredRight = Math.max(measuredRight, bbox.x + bbox.width);
                };
                // Cache for foreignObject inner heights so we can reuse later when resizing
                const foInnerHeights = new WeakMap();

                textElements.forEach(text => {
                    const textX = parseFloat(text.getAttribute('x') || 0);
                    const textY = parseFloat(text.getAttribute('y') || 0);

                    // Check if text is within or near this rectangle
                    if (Math.abs(textX - rectCenterX) < width * 1.5 &&
                        Math.abs(textY - rectCenterY) < height * 2.5) {

                        const textContent = text.textContent || '';
                        const fontSize = parseFloat(text.getAttribute('font-size') || 14);

                        // RACK: Accumulate font sizes for average calculation
                        averageFontSize = ((averageFontSize * fontSizeCount) + fontSize) / (fontSizeCount + 1);
                        fontSizeCount++;

                        // IXED: Comprehensive line break detection
                        const allLineBreaks = [
                            (textContent.match(/<br[^>]*>/gi) || []).length,  // All <br> variants
                            (textContent.match(/\n/g) || []).length,          // Newlines
                            (textContent.match(/\\n/g) || []).length          // Escaped newlines
                        ];
                        const explicitLines = Math.max(...allLineBreaks) + 1;

                        // IXED: More realistic character wrapping (15 chars per line in narrow nodes)
                        const estimatedLineWidth = Math.max(15, Math.min(40, width / 8)); // Dynamic based on node width
                        const naturalLines = Math.ceil(textContent.replace(/<[^>]*>/g, '').length / estimatedLineWidth);

                        // IXED: Add explicit + natural lines for HTML content, not max
                        const totalLines = hasHtmlContent ?
                            explicitLines + Math.ceil(naturalLines * 0.3) : // HTML: Add some natural wrapping
                            Math.max(explicitLines, naturalLines);          // Plain text: Use max

                        lineCount = Math.max(lineCount, totalLines);
                        maxTextHeight = Math.max(maxTextHeight, fontSize * totalLines * 1.4);

                        // nhanced: Check for complex content
                        if (textContent.includes('<') || textContent.includes('&') ||
                            textContent.includes('mermaid-') || textContent.length > 50) {
                            hasHtmlContent = true;
                            contentComplexity = Math.max(contentComplexity, textContent.length / 30);
                        }

                        // EW: Measure actual text bbox if it overlaps the rect area
                        try {
                            if (text.getBBox) {
                                const bbox = text.getBBox();
                                if (bbox && isFinite(bbox.x) && isFinite(bbox.y) && isFinite(bbox.width) && isFinite(bbox.height)) {
                                    if (overlaps(inflatedRect, bbox, overlapMargin)) {
                                        considerBounds(bbox);
                                    }
                                }
                            }
                        } catch (bboxErr) {
                            // Non-fatal; fall back to heuristics
                        }
                    }
                });

                // EW: Also include foreignObject contents when present (HTML labels)
                try {
                    const foNodes = svgElement.querySelectorAll('foreignObject');
                    foNodes.forEach(fo => {
                        try {
                            if (fo.getBBox) {
                                const foBBox = fo.getBBox();
                                if (foBBox && isFinite(foBBox.x) && isFinite(foBBox.y) && isFinite(foBBox.width) && isFinite(foBBox.height)) {
                                    if (overlaps(inflatedRect, foBBox, overlapMargin)) {
                                        // Measure inner HTML content height to detect overflow beyond FO's own box
                                        let innerH = 0;
                                        try {
                                            // Prefer the immediate child container if present
                                            let inner = fo.querySelector(':scope > *');
                                            if (!inner) inner = fo.querySelector('div');
                                            // As a fallback, compute max of children
                                            if (!inner) {
                                                let maxH = 0;
                                                fo.querySelectorAll('*').forEach(el => {
                                                    const gbr = el.getBoundingClientRect?.();
                                                    maxH = Math.max(maxH, el.scrollHeight || 0, gbr?.height || 0);
                                                });
                                                innerH = maxH;
                                            } else {
                                                const gbr = inner.getBoundingClientRect?.();
                                                innerH = Math.max(inner?.scrollHeight || 0, gbr?.height || 0);
                                            }
                                        } catch { }
                                        const effHeight = Math.max(foBBox.height, innerH || 0);
                                        if (innerH) foInnerHeights.set(fo, innerH);
                                        considerBounds({ x: foBBox.x, y: foBBox.y, width: foBBox.width, height: effHeight });
                                        hasHtmlContent = true;
                                    }
                                }
                            }
                        } catch { }
                    });
                } catch { }

                // nhanced: Calculate required padding based on content complexity
                const basePadding = 10; // REDUCED overall base padding
                const complexityMultiplier = Math.min(1.5, Math.max(1.0, contentComplexity * 0.2));
                const lineHeightMultiplier = 1.3; // REDUCED line height multiplier

                // IXED: Proper height scaling that doesn't underestimate
                let heightMultiplier = 1;
                if (lineCount > 1) {
                    // Calmer scaling: 1.2x base + 0.45x per additional line
                    heightMultiplier = 1.2 + (lineCount - 1) * 0.45;
                }
                if (hasHtmlContent) {
                    heightMultiplier *= 1.2; // Smaller bump for HTML content
                }

                const horizontalPadding = basePadding * Math.max(1, width / 120);
                const verticalPadding = basePadding * heightMultiplier * complexityMultiplier;

                // IXED: Much more realistic height calculation
                let newWidth = isLabelContainerRect ? width : (width + horizontalPadding);
                let newHeightHeuristic = Math.max(
                    height + verticalPadding,
                    maxTextHeight + (basePadding * 1.5),
                    lineCount * 30 + basePadding,
                    lineCount * averageFontSize * 1.4 + basePadding,
                    60 // Lower absolute minimum to avoid giant nodes
                );

                // EW: Use measured bounds to guarantee no bottom clipping
                let newY = rectY;
                if (measuredAny && isFinite(measuredTop) && isFinite(measuredBottom)) {
                    // Top/bottom padding tuned to avoid clipping descenders on the last line
                    const topPad = Math.max(6, basePadding * 0.9);
                    const bottomClipFudge = Math.max(10, averageFontSize * 0.8) + (lineCount > 1 ? Math.min(14, (lineCount - 1) * 1.6) : 0) + (hasHtmlContent ? 4 : 0);
                    const bottomPad = Math.max(basePadding * 1.1, bottomClipFudge);

                    // Prefer expanding downward; only move up if content starts above current top
                    newY = Math.min(rectY, measuredTop - topPad);
                    // For label-container rects, do not move Y to avoid vertical drift
                    const newYUsed = isLabelContainerRect ? rectY : newY;
                    const measuredHeightNeed = (measuredBottom + bottomPad) - newYUsed;
                    const newHeightMeasured = Math.max(height + (rectY - newYUsed), measuredHeightNeed);

                    // Combine with heuristic to be safe, never shrink
                    var newHeight = Math.max(newHeightHeuristic, newHeightMeasured, height);

                    rect.setAttribute('y', isFinite(newYUsed) ? newYUsed.toString() : rectY.toString());
                    rect.setAttribute('height', isFinite(newHeight) ? newHeight.toString() : height.toString());
                } else {
                    // Fallback to heuristic-only path
                    var newHeight = newHeightHeuristic;
                    rect.setAttribute('height', isFinite(newHeight) ? newHeight.toString() : height.toString());
                }
                // lamp to safe positive sizes
                if (!isFinite(newWidth)) newWidth = width || 1;
                if (!isFinite(newHeight)) newHeight = height || 1;
                newWidth = Math.max(1, newWidth);
                newHeight = Math.max(1, newHeight);
                rect.setAttribute('width', newWidth.toString());

                // nhanced: Center the expanded rectangle
                const x = parseFloat(rect.getAttribute('x') || 0);
                const y = parseFloat(rect.getAttribute('y') || 0);
                // Keep x centered. Do NOT shift y upward anymore; height was already adjusted to include bottom padding.
                const safeX = isLabelContainerRect ? x : (isFinite(x - horizontalPadding / 2) ? (x - horizontalPadding / 2) : x);
                rect.setAttribute('x', safeX.toString());

                // AFE SYNC: If this is the label-container rect, increase its foreignObject height to fit content
                if (isLabelContainerRect) {
                    try {
                        const rectH = parseFloat(rect.getAttribute('height') || '0');
                        const nodeGroup = rect.closest('g.node');
                        const labelGroup = nodeGroup ? nodeGroup.querySelector('g.label') : null;
                        const fo = labelGroup ? labelGroup.querySelector('foreignObject') : null;
                        let foMeasuredInnerH = 0; // make available for compaction even if 'fo' branch ends
                        if (fo) {
                            // Measure inner HTML content height
                            let innerH = 0;
                            try {
                                let inner = fo.querySelector(':scope > *') || fo.querySelector('div') || fo.querySelector('span');
                                if (!inner) {
                                    let maxH = 0;
                                    fo.querySelectorAll('*').forEach(el => {
                                        const gbr = el.getBoundingClientRect?.();
                                        maxH = Math.max(maxH, el.scrollHeight || 0, gbr?.height || 0);
                                    });
                                    innerH = maxH;
                                } else {
                                    const gbr = inner.getBoundingClientRect?.();
                                    innerH = Math.max(inner?.scrollHeight || 0, gbr?.height || 0);
                                }
                            } catch { }
                            foMeasuredInnerH = innerH || 0;
                            const currentFoH = parseFloat(fo.getAttribute('height') || '0') || 0;

                            // Calibrated padding model:
                            // - Total vertical padding ≈ 1.2 * fontSize (matches 16.8 at 14px)
                            // - Top padding ≈ 0.9 * fontSize (matches ~12.5 at 14px)
                            // - Bottom padding = totalPad - topPad (≈ 0.3 * fontSize)
                            const totalPad = Math.max(14, averageFontSize * 1.2);
                            const topPadCal = Math.max(8, averageFontSize * 0.9);
                            const bottomPadCal = Math.max(4, totalPad - topPadCal);

                            // Target rect height to hug content plus calibrated padding
                            const desiredRectH = Math.max(50, (foMeasuredInnerH || innerH || 0) + totalPad);
                            const curRectH = parseFloat(rect.getAttribute('height') || '0') || 0;
                            const targetRectH = Math.max(curRectH, desiredRectH); // never shrink during growth pass
                            if (isFinite(targetRectH) && targetRectH > 0 && Math.abs(targetRectH - curRectH) > 0.5) {
                                // Keep Y anchored to avoid vertical drift
                                rect.setAttribute('height', targetRectH.toString());
                            }

                            // ForeignObject height should fill the content area inside the rect (rectH - padding)
                            const rectHForFo = parseFloat(rect.getAttribute('height') || targetRectH.toString()) || targetRectH;
                            const foCap = Math.max(0, rectHForFo - (topPadCal + bottomPadCal));
                            const desiredFoH = Math.max(Math.min(foMeasuredInnerH || innerH || 0, foCap), Math.min(foCap, currentFoH));
                            if (isFinite(desiredFoH) && desiredFoH >= 0 && Math.abs(desiredFoH - currentFoH) > 0.5) {
                                fo.setAttribute('height', desiredFoH.toString());
                            }

                            // Update any clipPath applied to the label group so it matches the rect height
                            const clipAttr = (labelGroup && labelGroup.getAttribute('clip-path')) || fo.getAttribute('clip-path');
                            if (clipAttr) {
                                const m = clipAttr.match(/url\(#([^\)]+)\)/);
                                const clipId = m ? m[1] : null;
                                if (clipId) {
                                    const cp = svgElement.querySelector(`#${clipId}`);
                                    if (cp) {
                                        const cpRect = cp.querySelector('rect');
                                        if (cpRect) {
                                            const clipH = Math.max(desiredFoH || 0, (parseFloat(rect.getAttribute('height') || '0') || rectH) - 2);
                                            if (isFinite(clipH) && clipH > 0) {
                                                cpRect.setAttribute('height', clipH.toString());
                                            }
                                            // Ensure width is not less than the rect width
                                            const clipW = Math.max(parseFloat(cpRect.getAttribute('width') || '0') || 0, newWidth - 2);
                                            if (isFinite(clipW) && clipW > 0) {
                                                cpRect.setAttribute('width', clipW.toString());
                                            }
                                        }
                                    }
                                }
                            }

                            // Align the label group translate to calibrated top padding relative to rect.y
                            try {
                                if (labelGroup) {
                                    const rectXNow = parseFloat(rect.getAttribute('x') || '0') || 0;
                                    const rectYNow = parseFloat(rect.getAttribute('y') || '0') || 0;
                                    const rectWNow = parseFloat(rect.getAttribute('width') || '0') || 0;
                                    const foW = parseFloat(fo.getAttribute('width') || '0') || 0;

                                    // Compute desired translate positions
                                    const desiredTx = rectXNow + Math.max(0, (rectWNow - foW) / 2);
                                    const desiredTy = rectYNow + topPadCal;

                                    // Parse existing transform to preserve rotation/scales if any (rare); only replace translate
                                    const currentTransform = labelGroup.getAttribute('transform') || '';
                                    const newTranslate = `translate(${desiredTx}, ${desiredTy})`;
                                    if (!currentTransform || /translate\([^)]*\)/.test(currentTransform)) {
                                        const updated = currentTransform
                                            ? currentTransform.replace(/translate\([^)]*\)/, newTranslate)
                                            : newTranslate;
                                        labelGroup.setAttribute('transform', updated);
                                    } else {
                                        // Prepend translate if none present
                                        labelGroup.setAttribute('transform', `${newTranslate} ${currentTransform}`.trim());
                                    }

                                    console.log('📐 Calibrated label alignment:', { topPadCal, totalPad, desiredTx, desiredTy });
                                }
                            } catch (alignErr) {
                                console.warn('⚠️ Label alignment skipped:', alignErr);
                            }
                        }
                        // After FO sync, compact the label-container rect height to hug content + symmetric pad
                        const foH = fo ? (parseFloat(fo.getAttribute('height') || '0') || 0) : 0;
                        const contentH = Math.max(foH, foMeasuredInnerH || 0);
                        // Use the same calibrated padding for compaction to keep math consistent
                        const totalPad2 = Math.max(14, averageFontSize * 1.2);
                        const topPad2 = Math.max(8, averageFontSize * 0.9);
                        const bottomPad2 = Math.max(4, totalPad2 - topPad2);
                        const minRectH = 50;
                        const compactH = Math.max(minRectH, contentH + topPad2 + bottomPad2);
                        const curRectH = parseFloat(rect.getAttribute('height') || '0') || 0;
                        if (isFinite(compactH) && compactH > 0 && curRectH > 0) {
                            // Shrink only if current rect is larger than needed; keep top (y) anchored to avoid vertical drift
                            const targetRectH = Math.min(curRectH, compactH);
                            if (targetRectH < curRectH - 0.5) {
                                rect.setAttribute('height', targetRectH.toString());
                                // Do not change y here; avoid recentering which can shift node by ~40–50px
                            }
                        }
                    } catch { /* non-fatal */ }
                }

                // Keep labels managed by Mermaid; only adjust node rect sizes

                // nhanced: Enhanced styling
                if (!isLabelContainerRect) {
                    // EW (Jul 22 2026): canvas is always white, so use light-mode
                    // stroke (medium grey reads on white; the previous dark-mode
                    // '#666666' would be invisible on a white node fill).
                    rect.setAttribute('stroke', '#cccccc');
                    rect.setAttribute('stroke-width', '1.2');
                }

                console.log(`📏 Rect adjusted - lines=${lineCount}, measured=${measuredAny}, complexity=${contentComplexity.toFixed(1)}, height=${height}→${newHeight}`);
            }
        });

        // nhanced: Enhanced other shapes
        const circles = svgElement.querySelectorAll('circle');
        circles.forEach(circle => {
            const radius = parseFloat(circle.getAttribute('r') || 0);
            if (radius > 5) {
                // nhanced: Expand circles slightly for better text fit
                circle.setAttribute('r', (radius * 1.2).toString());
            }
            // EW (Jul 22 2026): always-light stroke (see rect stroke note above)
            circle.setAttribute('stroke', '#cccccc');
            circle.setAttribute('stroke-width', '1.5');
        });

        const polygons = svgElement.querySelectorAll('polygon');
        polygons.forEach(polygon => {
            // EW (Jul 22 2026): always-light stroke (see rect stroke note above)
            polygon.setAttribute('stroke', '#cccccc');
            polygon.setAttribute('stroke-width', '1.5');
        });

        // EW: Enhanced subgraph spacing and styling
        // EW (Jul 22 2026): drop isDark arg — canvas is always white
        this.applySubgraphSpacingStyles(svgElement);

        // INAL GUARD: Sanitize any negative/NaN dimensions from upstream quirks
        svgElement.querySelectorAll('rect').forEach(r => {
            let w = parseFloat(r.getAttribute('width') || '0');
            let h = parseFloat(r.getAttribute('height') || '0');
            if (!isFinite(w) || w <= 0) { r.setAttribute('width', Math.max(1, isFinite(w) ? w : 1).toString()); }
            if (!isFinite(h) || h <= 0) { r.setAttribute('height', Math.max(1, isFinite(h) ? h : 1).toString()); }
        });

        console.log('implified post-processing completed');
    }

    // EW: Apply specific styling fixes for subgraph spacing
    // EW (Jul 22 2026): drop isDark parameter — canvas is always white,
    // so all subgraph styling uses light-mode constants (subtle dark tint
    // for backgrounds, dark text, white halos for title contrast).
    applySubgraphSpacingStyles(svgElement) {
        console.log('🎨 Applying subgraph spacing styles...');
        console.log('🔍 SVG element structure:', svgElement.outerHTML.substring(0, 500));

        try {
            // NHANCED: Find subgraph elements using multiple selector strategies
            const potentialSubgraphs = [
                ...svgElement.querySelectorAll('g.cluster'),
                ...svgElement.querySelectorAll('g[id*="cluster"]'),
                ...svgElement.querySelectorAll('g[class*="cluster"]'),
                ...svgElement.querySelectorAll('rect.cluster'),
                ...svgElement.querySelectorAll('rect[id*="cluster"]'),
                ...svgElement.querySelectorAll('g.subgraph'),
                ...svgElement.querySelectorAll('g[id*="subgraph"]')
            ];

            console.log(`🔍 Found ${potentialSubgraphs.length} potential subgraph elements`);

            // NHANCED: Apply spacing to all subgraph-related elements
            potentialSubgraphs.forEach((element, index) => {
                console.log(`🔧 Processing subgraph element ${index}:`, element.tagName, element.className.baseVal || element.className, element.id);

                if (element.tagName === 'g') {
                    // Handle group elements (containers)
                    const transform = element.getAttribute('transform');
                    if (transform) {
                        console.log('🔧 Original transform:', transform);

                        const translateMatch = transform.match(/translate\(([^,]+),\s*([^)]+)\)/);
                        if (translateMatch) {
                            const x = parseFloat(translateMatch[1]);
                            const y = parseFloat(translateMatch[2]);

                            // Add extra spacing between subgraphs
                            const extraSpacing = index > 0 ? 40 : 20;
                            const newY = y + extraSpacing;
                            const newTransform = transform.replace(/translate\([^)]+\)/, `translate(${x}, ${newY})`);

                            element.setAttribute('transform', newTransform);
                            console.log('🔧 Updated transform:', newTransform);
                        }
                    }

                    // Find and enhance child rectangles (subgraph backgrounds)
                    const rects = element.querySelectorAll('rect');
                    rects.forEach(rect => {
                        // Style subgraph background — always light-mode values
                        rect.setAttribute('fill', 'rgba(0,0,0,0.03)');
                        rect.setAttribute('stroke', 'rgba(0,0,0,0.15)');
                        rect.setAttribute('stroke-width', '1');
                        rect.setAttribute('rx', '6');
                        rect.setAttribute('ry', '6');

                        // Expand padding
                        const width = parseFloat(rect.getAttribute('width') || 0);
                        const height = parseFloat(rect.getAttribute('height') || 0);
                        const x = parseFloat(rect.getAttribute('x') || 0);
                        const y = parseFloat(rect.getAttribute('y') || 0);

                        const newW = Math.max(1, isFinite(width + 20) ? (width + 20) : width || 1);
                        const newH = Math.max(1, isFinite(height + 30) ? (height + 30) : height || 1);
                        rect.setAttribute('width', newW.toString());
                        rect.setAttribute('height', newH.toString());
                        rect.setAttribute('x', (x - 10).toString());
                        rect.setAttribute('y', (y - 15).toString());
                    });

                } else if (element.tagName === 'rect') {
                    // Handle direct rectangle elements — always light-mode values
                    element.setAttribute('fill', 'rgba(0,0,0,0.03)');
                    element.setAttribute('stroke', 'rgba(0,0,0,0.15)');
                    element.setAttribute('stroke-width', '1');
                    element.setAttribute('rx', '6');
                    element.setAttribute('ry', '6');
                }
            });

            // NHANCED: Find and enhance subgraph titles using multiple strategies
            const allText = svgElement.querySelectorAll('text');
            const titleTexts = [];

            allText.forEach(text => {
                const textContent = (text.textContent || '').trim();
                const textLength = textContent.length;

                // NHANCED: Better subgraph title detection
                // Look for actual subgraph titles, not node content
                const isSubgraphTitle = (
                    // Check for common subgraph naming patterns
                    (textContent.includes('WINDAROO') && textContent.includes('Model')) ||
                    (textContent.includes('MT GRAVATT') && textContent.includes('Model')) ||
                    (textContent.includes('COMPTON') && textContent.includes('Model')) ||
                    (textContent.includes('ALGESTER') && textContent.includes('Model')) ||
                    (textContent.includes('Phase') && textContent.includes(':')) ||
                    // More generic patterns for subgraph titles
                    (textLength > 10 && textLength < 80 && (
                        textContent.includes(' - ') || // Common subgraph pattern: "Name - Description"
                        textContent.includes(' Model') ||
                        textContent.includes(' Hours') ||
                        (textContent.includes('Extended') && !textContent.includes('<')) ||
                        (textContent.includes('Standard') && !textContent.includes('<')) ||
                        (textContent.includes('Balanced') && !textContent.includes('<'))
                    )) ||
                    // Look for text that appears to be titles based on structure
                    (text.getAttribute('text-anchor') === 'middle' &&
                        textLength > 8 &&
                        !textContent.includes('<') && // Exclude HTML content 
                        !textContent.includes('•') &&  // Exclude bullet points
                        !textContent.includes('Mon-Fri')) // Exclude schedule content
                );

                if (isSubgraphTitle) {
                    titleTexts.push(text);
                    console.log(`🔍 Detected subgraph title: "${textContent}"`);
                }
            });

            console.log(`🔍 Found ${titleTexts.length} potential subgraph title texts`);

            // RITICAL FIX: Position subgraph titles at the top of their containers
            titleTexts.forEach((text, index) => {
                console.log(`🔧 Processing subgraph title ${index}: "${text.textContent}"`);

                // NHANCED: Find the associated subgraph container more accurately
                let parentContainer = null;

                // Strategy 1: Look for direct parent cluster
                parentContainer = text.closest('g.cluster') || text.closest('g[id*="cluster"]') || text.closest('g[id*="subgraph"]');

                // Strategy 2: If not found, look for nearby cluster by position
                if (!parentContainer) {
                    const textY = parseFloat(text.getAttribute('y') || 0);
                    const textX = parseFloat(text.getAttribute('x') || 0);

                    const clusters = svgElement.querySelectorAll('g.cluster, g[id*="cluster"], g[id*="subgraph"]');
                    clusters.forEach(cluster => {
                        const clusterRect = cluster.querySelector('rect');
                        if (clusterRect) {
                            const rectY = parseFloat(clusterRect.getAttribute('y') || 0);
                            const rectX = parseFloat(clusterRect.getAttribute('x') || 0);
                            const rectWidth = parseFloat(clusterRect.getAttribute('width') || 0);
                            const rectHeight = parseFloat(clusterRect.getAttribute('height') || 0);

                            // Check if title is within or near the cluster bounds
                            if (textX >= rectX - 50 && textX <= rectX + rectWidth + 50 &&
                                textY >= rectY - 100 && textY <= rectY + rectHeight + 50) {
                                parentContainer = cluster;
                                console.log(`🔧 Found nearby cluster for title "${text.textContent}"`);
                            }
                        }
                    });
                }

                if (parentContainer) {
                    // Find the background rectangle of this subgraph
                    const backgroundRect = parentContainer.querySelector('rect');

                    if (backgroundRect) {
                        const rectX = parseFloat(backgroundRect.getAttribute('x') || 0);
                        const rectY = parseFloat(backgroundRect.getAttribute('y') || 0);
                        const rectWidth = parseFloat(backgroundRect.getAttribute('width') || 0);

                        // RITICAL: Position title ABOVE the subgraph box, not inside
                        const titleX = rectX + (rectWidth / 2); // Center horizontally
                        const titleY = rectY - 10; // Position ABOVE the box (negative offset)

                        text.setAttribute('x', titleX.toString());
                        text.setAttribute('y', titleY.toString());
                        text.setAttribute('text-anchor', 'middle');
                        text.setAttribute('dominant-baseline', 'bottom'); // Align bottom of text to position

                        console.log(`🔧 Repositioned title "${text.textContent}" to (${titleX}, ${titleY}) - ABOVE subgraph`);

                        // RITICAL: Expand the subgraph box upward to accommodate the title
                        const newRectY = titleY - 25; // Make room for title
                        const newRectHeight = (parseFloat(backgroundRect.getAttribute('height') || 0)) + Math.abs(rectY - newRectY);

                        backgroundRect.setAttribute('y', newRectY.toString());
                        backgroundRect.setAttribute('height', newRectHeight.toString());

                        console.log(`🔧 Expanded subgraph box: y=${newRectY}, height=${newRectHeight}`);
                    }
                } else {
                    console.warn(`⚠️ Could not find parent container for title: "${text.textContent}"`);
                }

                // nhance title styling
                text.setAttribute('font-weight', 'bold');
                text.setAttribute('font-size', '14');
                // EW (Jul 22 2026): always dark text on white canvas
                text.setAttribute('fill', '#24292f');

                // dd a subtle background to make titles more visible
                try {
                    const textBBox = text.getBBox ? text.getBBox() : {
                        x: parseFloat(text.getAttribute('x') || 0) - 50,
                        y: parseFloat(text.getAttribute('y') || 0) - 12,
                        width: text.textContent.length * 8, // Estimate width
                        height: 16
                    };

                    const bgRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                    bgRect.setAttribute('x', (textBBox.x - 5).toString());
                    bgRect.setAttribute('y', (textBBox.y - 2).toString());
                    bgRect.setAttribute('width', (textBBox.width + 10).toString());
                    bgRect.setAttribute('height', (textBBox.height + 4).toString());
                    // EW (Jul 22 2026): always white halo on dark text for contrast
                    bgRect.setAttribute('fill', 'rgba(255,255,255,0.9)');
                    bgRect.setAttribute('stroke', 'rgba(0,0,0,0.2)');
                    bgRect.setAttribute('stroke-width', '1');
                    bgRect.setAttribute('rx', '4');
                    bgRect.setAttribute('ry', '4');

                    // Insert background before the text
                    if (text.parentNode) {
                        text.parentNode.insertBefore(bgRect, text);
                        console.log(`🎨 Added background for title: "${text.textContent}"`);
                    }
                } catch (bboxError) {
                    console.warn('⚠️ Could not add background for title:', bboxError.message);
                }
            });

            // NHANCED: Try to inject CSS for additional styling
            let styleElement = svgElement.querySelector('style');
            if (!styleElement) {
                styleElement = document.createElementNS('http://www.w3.org/2000/svg', 'style');
                svgElement.insertBefore(styleElement, svgElement.firstChild);
            }

            const additionalStyles = `
                .cluster { 
                    margin: 30px 0 !important; 
                }
                .cluster rect { 
                    padding: 25px 15px !important; 
                    margin-bottom: 15px !important;
                    /* EW (Jul 22 2026): always-light cluster rect styling */
                    fill: rgba(0,0,0,0.03) !important;
                    stroke: rgba(0,0,0,0.15) !important;
                }
                text[font-weight="bold"] { 
                    margin-bottom: 20px !important;
                    dominant-baseline: text-before-edge !important;
                    z-index: 1000 !important;
                }
                .cluster text:first-of-type {
                    transform: translateY(-30px) !important;
                }
                g.cluster > text {
                    position: relative !important;
                    z-index: 10 !important;
                }
                /* Ensure subgraph titles are always visible and on top */
                g.cluster text[text-anchor="middle"] {
                    paint-order: stroke markers fill !important;
                    /* EW (Jul 22 2026): always-white halo for text contrast */
                    stroke: #ffffff !important;
                    stroke-width: 3 !important;
                    stroke-linejoin: round !important;
                    font-weight: bold !important;
                }
            `;

            styleElement.textContent = (styleElement.textContent || '') + additionalStyles;

            // RITICAL: Adjust SVG viewBox to accommodate titles positioned above subgraphs.
            // Only run when there are actual subgraph titles to make room for — otherwise
            // (pie / sequence / class / state / gantt / er / journey / gitGraph / plain
            // flowcharts) this block would silently mangle the viewBox for no reason.
            if (titleTexts.length > 0) {
                const viewBox = svgElement.getAttribute('viewBox');
                if (viewBox) {
                    const [x, y, width, height] = viewBox.split(' ').map(Number);

                    // Defend against broken upstream viewBox (e.g. Mermaid was initialised
                    // against a 0-px container and produced `0 0 0 450`).
                    const safeWidth  = isFinite(width)  && width  > 0 ? width  : (svgElement.clientWidth || 600);
                    const safeHeight = isFinite(height) && height > 0 ? height : 450;

                    // Expand viewBox upward and increase overall height to accommodate titles
                    const newY = y - 50; // Extend upward for titles
                    const newHeight = safeHeight + 100; // Add extra space for titles and spacing

                    svgElement.setAttribute('viewBox', `${x} ${newY} ${safeWidth} ${newHeight}`);
                    console.log(`🔧 Adjusted SVG viewBox to accommodate subgraph titles: ${x} ${newY} ${safeWidth} ${newHeight}`);
                }
            }

            console.log('ubgraph spacing styles applied successfully');

        } catch (error) {
            console.error(' Error applying subgraph spacing styles:', error);
        }
    }

    // 6.2.1
    addMermaidUnifiedActionBar(container, diagramContent, chartId) {
        const actionBar = document.createElement('div');
        actionBar.className = 'viz-action-bar';

        actionBar.innerHTML = `
            <button class="viz-action-btn" data-action="copy" title="Copy Code" data-function="copyMermaidCode">
                <i class="fas fa-copy">⧉</i>
            </button>
            
            <button class="viz-action-btn font-control" data-action="view" title="Smaller Font" data-function="fontSizeDown">
                <i class="fas fa-minus">A-</i>
            </button>
            
            <button class="viz-action-btn font-control" data-action="view" title="Font Size Menu" data-function="fontSizeMenu">
                <i class="fas fa-text-height">Aa</i>
            </button>
            
            <button class="viz-action-btn font-control" data-action="view" title="Larger Font" data-function="fontSizeUp">
                <i class="fas fa-plus">A+</i>
            </button>
            
            <button class="viz-action-btn" data-action="view" title="Toggle Direction" data-function="toggleDirection">
                <i class="fas fa-arrows-alt-h">↔</i>
            </button>
            
            <button class="viz-action-btn" data-action="view" title="Color Themes" data-function="colorThemes">
                <i class="fas fa-palette">🎨</i>
            </button>
            
            <button class="viz-action-btn" data-action="view" title="Fullscreen View" data-function="fullscreenView">
                <i class="fas fa-expand">⛶</i>
            </button>
            
            <button class="viz-action-btn" data-action="export" title="Export" data-function="exportOptions">
                <i class="fas fa-download">⬇</i>
            </button>
        `;

        container.appendChild(actionBar);
        this.setupMermaidButtonHandlers(actionBar, container, diagramContent, chartId);
    }

    // 6.2.2
    // 6.2.2 - FIXED: Better parameter handling and error checking
    // 6.2.2 - FIXED: Better container identification and export handling
    setupMermaidButtonHandlers(actionBar, container, diagramContent, chartId) {
        const buttons = actionBar.querySelectorAll('.viz-action-btn');

        buttons.forEach(button => {
            const functionName = button.getAttribute('data-function');

            button.addEventListener('click', (e) => {
                e.stopPropagation();

                // FIXED: Always find the closest viz-container for exports
                const vizContainer = button.closest('.viz-container') || container;

                console.log('🔍 Mermaid button clicked:', {
                    functionName,
                    hasVizContainer: !!vizContainer,
                    hasVizContentArea: !!vizContainer?.querySelector('.viz-content-area'),
                    hasSvg: !!vizContainer?.querySelector('svg'),
                    diagramContentLength: diagramContent?.length,
                    chartId
                });

                switch (functionName) {
                    case 'copyMermaidCode':
                        this.copyMermaidCode(diagramContent);
                        break;

                    // Font size controls...
                    case 'fontSizeDown':
                        window.mermaidFontController.cycleFontSize(vizContainer, 'down');
                        this.updateFontButtonStates(vizContainer, actionBar);
                        // FIX: Re-render fullscreen if it's open
                        this.reRenderFullscreenIfOpen(vizContainer, diagramContent, chartId);
                        break;

                    case 'fontSizeUp':
                        window.mermaidFontController.cycleFontSize(vizContainer, 'up');
                        this.updateFontButtonStates(vizContainer, actionBar);
                        // FIX: Re-render fullscreen if it's open
                        this.reRenderFullscreenIfOpen(vizContainer, diagramContent, chartId);
                        break;

                    case 'fontSizeMenu':
                        this.showFontSizeMenu(vizContainer, button);
                        break;

                    case 'toggleDirection':
                        this.toggleMermaidDirection(vizContainer, diagramContent, chartId);
                        // FIX: Re-render fullscreen if it's open
                        this.reRenderFullscreenIfOpen(vizContainer, diagramContent, chartId);
                        break;
                    case 'colorThemes':
                        this.toggleMermaidColorThemes(vizContainer, diagramContent, chartId);
                        // FIX: Re-render fullscreen if it's open
                        this.reRenderFullscreenIfOpen(vizContainer, diagramContent, chartId);
                        break;
                    case 'fullscreenView':
                        this.openMermaidFullscreen(vizContainer, diagramContent, chartId);
                        break;
                    case 'exportOptions':
                        // FIXED: Use the vizContainer and ensure we have content
                        const contentToExport = diagramContent ||
                            vizContainer.getAttribute('data-original-content') ||
                            '';
                        console.log('📤 Export options for viz-container:', {
                            hasContent: !!contentToExport,
                            contentLength: contentToExport.length,
                            hasVizContentArea: !!vizContainer.querySelector('.viz-content-area'),
                            hasSvg: !!vizContainer.querySelector('svg')
                        });

                        if (!contentToExport) {
                            this.showNotification(' No diagram content available for export', 'error');
                            return;
                        }

                        this.toggleMermaidExportOptions(vizContainer, contentToExport, chartId);
                        break;
                }
            });
        });

        // Apply user font preference on load
        if (window.mermaidFontController) {
            window.mermaidFontController.applyUserPreference(container);
            this.updateFontButtonStates(container, actionBar);
        }
    }

    // 6.3.1
    // LSO UPDATE: Direction toggle for consistency
    async toggleMermaidDirection(container, diagramContent, chartId) {
        console.log('🔄 Toggling Mermaid direction...');

        try {
            const originalContent = container.getAttribute('data-original-content');
            if (!originalContent) {
                console.error(' No original content stored');
                return;
            }

            // ETTER DETECTION: More robust direction detection
            let currentDirection = 'TD';
            const contentUpper = originalContent.toUpperCase();

            if (contentUpper.includes('GRAPH LR') || contentUpper.includes('FLOWCHART LR')) {
                currentDirection = 'LR';
            } else if (contentUpper.includes('GRAPH TD') || contentUpper.includes('FLOWCHART TD')) {
                currentDirection = 'TD';
            } else if (contentUpper.includes('GRAPH RL') || contentUpper.includes('FLOWCHART RL')) {
                currentDirection = 'RL';
            } else if (contentUpper.includes('GRAPH BT') || contentUpper.includes('FLOWCHART BT')) {
                currentDirection = 'BT';
            }

            // Toggle direction - simple TD ↔ LR
            let newDirection = currentDirection === 'TD' ? 'LR' : 'TD';

            console.log(`🔄 Changing direction from ${currentDirection} to ${newDirection}`);

            // RANSFORM: Better content transformation
            let newContent = this.transformMermaidDirection(originalContent, newDirection);
            console.log('🔄 Transformed content:', newContent.substring(0, 100) + '...');

            // Apply HTML transformation
            newContent = this.transformMermaidContentToHTML(newContent);

            // NHANCED: Try multiple selectors to find mermaid content
            let mermaidDiv = container.querySelector('.mermaid');

            // If not found directly, try within viz-content areas
            if (!mermaidDiv) {
                const vizContent = container.querySelector('.viz-content, .viz-content-area');
                if (vizContent) {
                    mermaidDiv = vizContent.querySelector('.mermaid');
                }
            }

            // Still not found? Try finding any element with mermaid id pattern
            if (!mermaidDiv) {
                mermaidDiv = container.querySelector('[id*="mermaid"], [class*="mermaid"]');
            }

            if (!mermaidDiv) {
                // Try alternative selectors
                const svgElement = container.querySelector('svg');
                const vizElement = container.querySelector('.viz-content');
                const allChildren = Array.from(container.children);

                console.error(' Mermaid div not found. Container info:');
                console.log('Container class:', container.className);
                console.log('Container id:', container.id);
                console.log('Container tag:', container.tagName);
                console.log('Container children count:', allChildren.length);
                console.log('Children details:', allChildren.map(child => ({
                    tag: child.tagName,
                    class: child.className,
                    id: child.id,
                    hasClass: child.classList.contains('mermaid'),
                    innerHTML: child.innerHTML.substring(0, 100) + '...'
                })));
                console.log('Has SVG:', !!svgElement);
                console.log('Has viz-content:', !!vizElement);

                // If we have SVG directly, try to find/create a proper mermaid wrapper
                if (svgElement && !mermaidDiv) {
                    console.log('🔧 Found SVG without mermaid wrapper, creating wrapper...');
                    const wrapper = document.createElement('div');
                    wrapper.className = 'mermaid';
                    wrapper.style.cssText = `
                        width: 100%;
                        height: auto;
                        position: relative;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    `;

                    // Move SVG into wrapper
                    svgElement.parentNode.insertBefore(wrapper, svgElement);
                    wrapper.appendChild(svgElement);
                    mermaidDiv = wrapper; // RITICAL FIX: Set the reference to the created wrapper
                    console.log('reated mermaid wrapper for existing SVG');
                } else {
                    // Try looking deeper in the structure
                    const vizContent = container.querySelector('.viz-content, .viz-content-area');
                    const directSvg = container.querySelector('svg');

                    console.log('🔍 Searching for alternative structures...');
                    console.log('Found viz-content:', !!vizContent);
                    console.log('Found direct SVG:', !!directSvg);

                    if (vizContent) {
                        const vizMermaid = vizContent.querySelector('.mermaid');
                        if (vizMermaid) {
                            console.log('ound mermaid in viz-content, using that');
                            // Update container reference to point to the correct element
                            return this.toggleMermaidDirection(vizContent.parentElement, diagramContent, chartId);
                        }
                    }
                }
            }

            // If we still don't have a mermaid div at this point, there's a structure issue
            if (!mermaidDiv) {
                this.showNotification(' Cannot find Mermaid diagram to toggle direction. Structure may be incompatible.', 'error');
                return;
            }

            // Re-render
            // EW (Jul 22 2026): Always-white canvas — force theme 'base' so
            // Mermaid renders with the light palette regardless of UI theme.
            // See VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md.
            const fontSize = parseInt(container.getAttribute('data-font-size') || '14');

            mermaid.initialize({
                startOnLoad: false,
                theme: 'base',
                securityLevel: 'loose',
                htmlLabels: true,
                fontSize: fontSize,
                flowchart: {
                    htmlLabels: true,
                    padding: Math.max(25, fontSize * 1.4),
                    nodeSpacing: Math.max(80, fontSize * 4.5),
                    rankSpacing: Math.max(80, fontSize * 4.5),
                    diagramPadding: Math.max(35, fontSize * 2.0)
                }
            });

            // Use the found/created mermaidDiv directly
            const newChartId = `${chartId}-${newDirection}-${Date.now()}`;
            const { svg } = await mermaid.render(newChartId, newContent);

            if (svg) {
                mermaidDiv.innerHTML = svg;

                // RITICAL FIX: Always apply post-processing after direction change
                const svgElement = mermaidDiv.querySelector('svg');
                if (svgElement) {
                    console.log('🔧 Applying consistent post-processing for direction change...');

                    // TEP 1: Apply intelligent node sizing
                    this.applySimplifiedMermaidPostProcessing(svgElement);

                    // TEP 2: Apply current theme colors
                    const currentTheme = container.getAttribute('data-color-theme') || 'default';
                    const colorThemes = this.getMermaidColorThemes();
                    const selectedTheme = colorThemes[currentTheme] || colorThemes.default;
                    this.applyMermaidThemeColors(svgElement, selectedTheme, container);

                    console.log('irection change post-processing complete');
                }

                // Update stored content
                const updatedOriginalContent = this.transformMermaidDirection(originalContent, newDirection);
                container.setAttribute('data-original-content', updatedOriginalContent);

                const directionNames = {
                    'TD': 'Top → Down',
                    'LR': 'Left → Right'
                };

                this.showNotification(`🔄 Direction: ${directionNames[newDirection]} with consistent sizing`, 'success');

                // pdate fullscreen if open
                if (window.reRenderFullscreenIfOpen) {
                    window.reRenderFullscreenIfOpen();
                }
            }

        } catch (error) {
            console.error(' Error toggling Mermaid direction:', error);
            this.showNotification(' Failed to change direction', 'error');
        }
    }


    // 6.3.2
    transformMermaidDirection(content, newDirection) {
        if (!content || typeof content !== 'string') return content;

        let transformed = content;

        // OMPREHENSIVE: Handle all possible direction patterns
        const patterns = [
            /graph\s+(TD|LR|RL|BT|TB)/gi,
            /flowchart\s+(TD|LR|RL|BT|TB)/gi,
            /^graph\s*$/gim,
            /^flowchart\s*$/gim
        ];

        let foundPattern = false;

        patterns.forEach(pattern => {
            if (pattern.test(transformed)) {
                foundPattern = true;
                transformed = transformed.replace(pattern, (match) => {
                    if (match.toLowerCase().startsWith('graph')) {
                        return `graph ${newDirection}`;
                    } else {
                        return `flowchart ${newDirection}`;
                    }
                });
            }
        });

        // If no pattern found, add it
        if (!foundPattern) {
            const lines = transformed.split('\n');
            const firstLine = lines[0].trim();

            if (firstLine === 'graph' || firstLine === 'flowchart') {
                lines[0] = `${firstLine} ${newDirection}`;
                transformed = lines.join('\n');
            } else {
                transformed = `graph ${newDirection}\n${transformed}`;
            }
        }

        return transformed;
    }

    // 6.4.1
    toggleMermaidColorThemes(container, diagramContent, chartId) {
        const existing = container.querySelector('.color-theme-switcher');
        if (existing) {
            existing.remove();
            return;
        }

        const switcher = document.createElement('div');
        switcher.className = 'color-theme-switcher';
        switcher.style.cssText = `
            position: absolute;
            top: 10px;
            right: 120px;
            z-index: 1001;
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border-primary) !important;
            border-radius: 6px !important;
            padding: 6px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            min-width: 160px;
        `;

        const select = document.createElement('select');
        select.className = 'color-theme-select';
        select.style.cssText = `
            background: var(--bg-secondary) !important;
            border: none !important;
            border-radius: 4px !important;
            padding: 8px 12px !important;
            font-size: 12px !important;
            cursor: pointer !important;
            color: var(--text-primary) !important;
            width: 100% !important;
            box-sizing: border-box !important;
        `;

        const colorThemes = this.getMermaidColorThemes();
        const currentTheme = container.getAttribute('data-color-theme') || 'default';

        Object.entries(colorThemes).forEach(([key, theme]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = `${theme.icon} ${theme.name}`;
            if (key === currentTheme) {
                option.selected = true;
            }
            select.appendChild(option);
        });

        select.onchange = (e) => {
            const newTheme = e.target.value;
            this.applyMermaidColorTheme(container, diagramContent, chartId, newTheme);
            container.setAttribute('data-color-theme', newTheme);
            // Don't remove dropdown - let it stay open like chart type

            // pdate fullscreen if open
            if (window.reRenderFullscreenIfOpen) {
                window.reRenderFullscreenIfOpen();
            }
        };

        switcher.appendChild(select);
        container.appendChild(switcher);

        // lick outside to close
        const handleClickOutside = (e) => {
            if (!switcher.contains(e.target) && !e.target.closest('[data-function="colorThemes"]')) {
                switcher.remove();
                document.removeEventListener('click', handleClickOutside);
            }
        };

        setTimeout(() => {
            document.addEventListener('click', handleClickOutside);
        }, 100);
    }


    // 6.4.2 - FIXED: Consistent node sizing for UI and exports
    async applyMermaidColorTheme(container, diagramContent, chartId, themeName) {
        if (!window.mermaid) return;

        try {
            const colorThemes = this.getMermaidColorThemes();
            const selectedTheme = colorThemes[themeName] || colorThemes.default;

            console.log(`🎨 Applying ${selectedTheme.name} theme to Mermaid diagram`);

            // FIXED: Proper Mermaid theme configuration with enhanced text contrast
            // EW (Jul 22 2026): Drop isDark branching — canvas is always white,
            // so we always pass light-mode values for the canvas-bound variables.
            // The many #ffffff text forces further down are load-bearing (white
            // text on palette-colored nodes) and remain unchanged.
            // See VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md.
            const themeConfig = {
                startOnLoad: false,
                theme: 'base',
                themeVariables: {
                    // Core theme
                    primaryColor: selectedTheme.colors.fillType0,
                    primaryTextColor: '#ffffff',  // Force white text for maximum contrast
                    primaryBorderColor: '#333333',
                    lineColor: '#656d76',

                    // Background colors
                    backgroundColor: '#ffffff',
                    mainBkg: selectedTheme.colors.fillType0,
                    secondBkg: selectedTheme.colors.fillType1,
                    tertiaryColor: selectedTheme.colors.fillType2,

                    // CRITICAL: Direct color assignments for different node types
                    cScale0: selectedTheme.colors.fillType0,
                    cScale1: selectedTheme.colors.fillType1,
                    cScale2: selectedTheme.colors.fillType2,
                    cScale3: selectedTheme.colors.fillType3,
                    cScale4: selectedTheme.colors.fillType4,
                    cScale5: selectedTheme.colors.fillType5,
                    cScale6: selectedTheme.colors.fillType6,
                    cScale7: selectedTheme.colors.fillType7,

                    // FLOWCHART specific colors
                    fillType0: selectedTheme.colors.fillType0,
                    fillType1: selectedTheme.colors.fillType1,
                    fillType2: selectedTheme.colors.fillType2,
                    fillType3: selectedTheme.colors.fillType3,
                    fillType4: selectedTheme.colors.fillType4,
                    fillType5: selectedTheme.colors.fillType5,
                    fillType6: selectedTheme.colors.fillType6,
                    fillType7: selectedTheme.colors.fillType7,

                    // ENHANCED: Force white text on all elements for maximum readability
                    textColor: '#ffffff',
                    nodeTextColor: '#ffffff',
                    classText: '#ffffff',
                    labelTextColor: '#ffffff',
                    taskTextColor: '#ffffff',
                    activeTaskTextColor: '#ffffff',
                    signalTextColor: '#ffffff',
                    actorTextColor: '#ffffff',
                    pieTitleTextColor: '#ffffff',
                    pieSectionTextColor: '#ffffff',
                    pieLegendTextColor: '#ffffff',

                    // NODE specific colors with strong borders
                    nodeBkg: selectedTheme.colors.fillType0,
                    nodeBorder: '#333333',

                    // CLUSTER colors
                    clusterBkg: selectedTheme.colors.fillType1,
                    clusterBorder: '#333333',

                    // ADDITIONAL flowchart colors
                    defaultLinkColor: '#666666',
                    titleColor: '#ffffff',
                    edgeLabelBackground: '#ffffff',

                    // SECTION colors for sequence diagrams
                    sectionBkgColor: selectedTheme.colors.fillType0,
                    altSectionBkgColor: selectedTheme.colors.fillType1,

                    // ACTOR colors for sequence diagrams
                    actorBkg: selectedTheme.colors.fillType2,
                    actorBorder: '#333333',
                    actorLineColor: '#666666',

                    // SIGNAL colors
                    signalColor: '#ffffff',

                    // LABEL colors
                    labelBoxBkgColor: selectedTheme.colors.fillType5,
                    labelBoxBorderColor: '#333333'
                },

                // ENHANCED: Better font configuration
                fontFamily: '"Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                fontSize: parseInt(container.getAttribute('data-font-size') || '14'),

                // ENHANCED: Flowchart improvements for better text fit
                flowchart: {
                    htmlLabels: true,
                    curve: 'basis',
                    padding: 25,
                    nodeSpacing: 80,
                    rankSpacing: 80,
                    diagramPadding: 35,
                    // Additional spacing controls
                    edgePadding: 20,
                    nodePadding: 8,     // REDUCED
                    textHeight: 18,
                    lineHeight: 1.3
                }
            };

            // REINITIALIZE Mermaid with new theme
            mermaid.initialize(themeConfig);

            // GENERATE new unique ID to force re-render
            const newId = `mermaid-${chartId}-${themeName}-${Date.now()}`;

            // RE-RENDER with new configuration
            const { svg } = await mermaid.render(newId, diagramContent);

            const mermaidDiv = container.querySelector('.mermaid');
            if (mermaidDiv) {
                mermaidDiv.innerHTML = svg;

                // CRITICAL FIX: Always apply post-processing after re-render
                const svgElement = mermaidDiv.querySelector('svg');
                if (svgElement) {
                    console.log('🔧 Applying consistent post-processing for theme change...');

                    // STEP 1: Apply intelligent node sizing (same as initial render)
                    this.applySimplifiedMermaidPostProcessing(svgElement);

                    // STEP 2: Apply theme-specific colors AFTER sizing
                    this.applyMermaidThemeColors(svgElement, selectedTheme, container);

                    console.log('✅ Post-processing complete - UI and export sizes will match');
                }

                this.showNotification(`🎨 Applied ${selectedTheme.name} color theme`, 'success');
            } else {
                console.error('Mermaid div not found');
            }

        } catch (error) {
            console.error('Error applying color theme:', error);
            this.showNotification('❌ Failed to apply color theme', 'error');
        }
    }

    // NEW: Separated color application for better organization
    applyMermaidThemeColors(svgElement, selectedTheme, container) {
        console.log('🎨 Applying theme colors to enhanced nodes...');

        // Find and color rectangles (boxes/nodes)
        const rects = svgElement.querySelectorAll('rect');
        console.log(`Found ${rects.length} rectangles to color`);

        rects.forEach((rect, index) => {
            // Skip very small rects (likely borders or decorations)
            const width = parseFloat(rect.getAttribute('width') || 0);
            const height = parseFloat(rect.getAttribute('height') || 0);

            if (width > 10 && height > 10) {
                const colorIndex = index % Object.keys(selectedTheme.colors).length;
                const colorKeys = Object.keys(selectedTheme.colors);
                const color = selectedTheme.colors[colorKeys[colorIndex]];

                rect.setAttribute('fill', color);
                rect.setAttribute('stroke', '#333333');
                rect.setAttribute('stroke-width', '2');

                console.log(`Applied color ${color} to enhanced rect ${index} (${width}x${height})`);
            }
        });

        // Color circles (for flowchart circles, decision points)
        const circles = svgElement.querySelectorAll('circle');
        circles.forEach((circle, index) => {
            const radius = parseFloat(circle.getAttribute('r') || 0);
            if (radius > 5) {
                const colorIndex = index % Object.keys(selectedTheme.colors).length;
                const colorKeys = Object.keys(selectedTheme.colors);
                const color = selectedTheme.colors[colorKeys[colorIndex]];

                circle.setAttribute('fill', color);
                circle.setAttribute('stroke', '#333333');
                circle.setAttribute('stroke-width', '2');
            }
        });

        // Color polygons (for diamond shapes, etc.)
        const polygons = svgElement.querySelectorAll('polygon');
        polygons.forEach((polygon, index) => {
            const colorIndex = index % Object.keys(selectedTheme.colors).length;
            const colorKeys = Object.keys(selectedTheme.colors);
            const color = selectedTheme.colors[colorKeys[colorIndex]];

            polygon.setAttribute('fill', color);
            polygon.setAttribute('stroke', '#333333');
            polygon.setAttribute('stroke-width', '2');
        });

        // ENHANCED: Force maximum text visibility (preserve enhanced font sizes)
        const textElements = svgElement.querySelectorAll('text, tspan');
        const fontSize = parseInt(container.getAttribute('data-font-size') || '14');
        textElements.forEach(text => {
            // PRESERVE existing font-size from post-processing
            const currentFontSize = text.getAttribute('font-size') || fontSize.toString();
            text.setAttribute('fill', '#ffffff');
            text.setAttribute('font-weight', '700');
            text.setAttribute('font-size', currentFontSize); // Keep enhanced size
            text.style.textShadow = '1px 1px 2px rgba(0, 0, 0, 0.8)';
        });

        // COLOR paths/lines with better visibility
        const paths = svgElement.querySelectorAll('path');
        paths.forEach(path => {
            if (path.getAttribute('stroke') && path.getAttribute('stroke') !== 'none') {
                path.setAttribute('stroke', '#666666');
                path.setAttribute('stroke-width', '2');
            }
        });
    }

    // ALSO UPDATE: Font size change method for consistency
    async applyMermaidFontSize(container, diagramContent, chartId, fontSize) {
        try {
            // Store new size
            container.setAttribute('data-font-size', fontSize.toString());

            // Get current theme and apply with new font size
            const currentTheme = container.getAttribute('data-color-theme') || 'default';
            const colorThemes = this.getMermaidColorThemes();
            const selectedTheme = colorThemes[currentTheme] || colorThemes.default;

            // Enhanced theme configuration with custom font size
            // EW (Jul 22 2026): Drop isDark branching — canvas is always white,
            // so we always pass light-mode values for the canvas-bound variables.
            // The #ffffff text forces below are load-bearing (white text on
            // palette-colored nodes). See
            // VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md.
            const themeConfig = {
                startOnLoad: false,
                theme: 'base',
                themeVariables: {
                    // Enhanced text colors for better contrast
                    primaryColor: selectedTheme.colors.fillType0,
                    primaryTextColor: '#ffffff',
                    primaryBorderColor: '#333333',
                    lineColor: '#656d76',

                    // Background and node colors
                    backgroundColor: '#ffffff',
                    mainBkg: selectedTheme.colors.fillType0,
                    secondBkg: selectedTheme.colors.fillType1,

                    // All fillType colors from selected theme
                    ...selectedTheme.colors,

                    // Text colors - force white for maximum contrast
                    textColor: '#ffffff',
                    nodeTextColor: '#ffffff',
                    classText: '#ffffff',
                    labelTextColor: '#ffffff',
                    taskTextColor: '#ffffff',
                    activeTaskTextColor: '#ffffff',
                    signalTextColor: '#ffffff',
                    actorTextColor: '#ffffff',
                    pieTitleTextColor: '#ffffff',
                    pieSectionTextColor: '#ffffff',
                    pieLegendTextColor: '#ffffff',

                    // Node styles
                    nodeBkg: selectedTheme.colors.fillType0,
                    nodeBorder: '#333333',
                    clusterBkg: selectedTheme.colors.fillType1,
                    clusterBorder: '#333333',

                    // Actor styles for sequence diagrams
                    actorBkg: selectedTheme.colors.fillType2,
                    actorBorder: '#333333',
                    actorLineColor: '#666666'
                },

                // ENHANCED: Custom font configuration
                fontFamily: '"Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                fontSize: fontSize,

                // NODE-SPECIFIC font sizes and spacing
                flowchart: {
                    htmlLabels: true,
                    curve: 'basis',
                    padding: Math.max(25, fontSize * 1.4),       // SCALE with font size
                    nodeSpacing: Math.max(80, fontSize * 4.5),   // SCALE with font size
                    rankSpacing: Math.max(80, fontSize * 4.5),   // SCALE with font size
                    diagramPadding: Math.max(35, fontSize * 2.0),// SCALE with font size
                    edgePadding: Math.max(20, fontSize * 1.2),
                    nodePadding: Math.max(8, fontSize * 0.5),
                    textHeight: fontSize * 1.2,
                    lineHeight: 1.3
                }
            };

            // Reinitialize Mermaid with new configuration
            mermaid.initialize(themeConfig);

            // Generate new unique ID
            const newId = `mermaid-${chartId}-font${fontSize}-${Date.now()}`;

            // Re-render diagram
            const { svg } = await mermaid.render(newId, diagramContent);

            const mermaidDiv = container.querySelector('.mermaid');
            if (mermaidDiv) {
                mermaidDiv.innerHTML = svg;

                // CRITICAL FIX: Always apply post-processing after font size change
                const svgElement = mermaidDiv.querySelector('svg');
                if (svgElement) {
                    console.log(`🔧 Applying consistent post-processing for font size ${fontSize}px...`);

                    // STEP 1: Apply intelligent node sizing with new font size
                    this.applySimplifiedMermaidPostProcessing(svgElement);

                    // STEP 2: Apply current theme colors AFTER sizing
                    this.applyMermaidThemeColors(svgElement, selectedTheme, container);

                    console.log('✅ Font size post-processing complete - UI and export sizes will match');
                }

                this.showNotification(`🔤 Font size: ${fontSize}px applied with consistent sizing`, 'success');
            }

        } catch (error) {
            console.error('Error changing font size:', error);
            this.showNotification(' Failed to change font size', 'error');
        }
    }


    // 6.4.3
    // 6.4.3 - FIXED: Much paler pastel colors
    getMermaidColorThemes() {
        return {
            default: {
                name: 'Soft Pastels',
                icon: '🔷',
                colors: {
                    // IXED: Much paler, pastel colors for better readability
                    fillType0: '#E8F4FD', // Very pale blue
                    fillType1: '#F0F9F0', // Very pale green  
                    fillType2: '#FFF9E6', // Very pale orange
                    fillType3: '#FDF2F8', // Very pale pink
                    fillType4: '#F8F0FF', // Very pale purple
                    fillType5: '#F0FDFA', // Very pale teal
                    fillType6: '#FFFEF0', // Very pale yellow
                    fillType7: '#F8FDF0'  // Very pale lime
                },
                textColor: '#2d3748',      // Dark gray text for contrast
                nodeTextColor: '#2d3748'
            },
            ocean: {
                name: 'Ocean Breeze',
                icon: '🌊',
                colors: {
                    fillType0: '#F0F9FF', // Lightest blue
                    fillType1: '#E0F2FE', // Very light sky blue
                    fillType2: '#BAE6FD', // Light blue
                    fillType3: '#F0FDFA', // Very light cyan
                    fillType4: '#CCFBF1', // Light turquoise
                    fillType5: '#A7F3D0', // Light mint
                    fillType6: '#F8FAFC', // Almost white blue
                    fillType7: '#F1F9FF'  // Very light blue tint
                },
                textColor: '#1e40af',      // Dark blue text
                nodeTextColor: '#1e40af'
            },
            forest: {
                name: 'Fresh Greens',
                icon: '🌲',
                colors: {
                    fillType0: '#F0FDF4', // Very light green
                    fillType1: '#DCFCE7', // Light green
                    fillType2: '#BBF7D0', // Medium light green
                    fillType3: '#F7FEE7', // Very light lime
                    fillType4: '#ECFCCB', // Light lime
                    fillType5: '#D9F99D', // Medium lime
                    fillType6: '#F0FDF0', // Mint white
                    fillType7: '#FEFFFE'  // Almost white green
                },
                textColor: '#15803d',      // Dark green text
                nodeTextColor: '#15803d'
            },
            sunset: {
                name: 'Warm Sunset',
                icon: '🌅',
                colors: {
                    fillType0: '#FFFBEB', // Very light orange
                    fillType1: '#FEF3C7', // Light orange
                    fillType2: '#FDE68A', // Medium orange
                    fillType3: '#FEF7F7', // Very light pink
                    fillType4: '#FECACA', // Light pink
                    fillType5: '#F9A8D4', // Medium pink
                    fillType6: '#FFFEF7', // Very light cream
                    fillType7: '#FEF9C3'  // Light yellow
                },
                textColor: '#c2410c',      // Dark orange text
                nodeTextColor: '#c2410c'
            },
            royal: {
                name: 'Lavender Dreams',
                icon: '👑',
                colors: {
                    fillType0: '#FAF5FF', // Very light purple
                    fillType1: '#F3E8FF', // Light purple
                    fillType2: '#E9D5FF', // Medium purple
                    fillType3: '#F8FAFC', // Very light indigo
                    fillType4: '#EDE9FE', // Light indigo
                    fillType5: '#DDD6FE', // Medium indigo
                    fillType6: '#FEFCFF', // Very light lavender
                    fillType7: '#F1F5F9'  // Very light blue-purple
                },
                textColor: '#7c3aed',      // Dark purple text
                nodeTextColor: '#7c3aed'
            },
            professional: {
                name: 'Light Grays',
                icon: '💼',
                colors: {
                    fillType0: '#FEFEFE', // Almost white
                    fillType1: '#F9FAFB', // Very light gray
                    fillType2: '#F3F4F6', // Light gray
                    fillType3: '#F0F0F0', // Light warm gray
                    fillType4: '#E5E7EB', // Medium light gray
                    fillType5: '#D1D5DB', // Medium gray
                    fillType6: '#FAFBFC', // Very light blue-gray
                    fillType7: '#F8F9FA'  // Light blue-gray
                },
                textColor: '#374151',      // Dark gray text
                nodeTextColor: '#374151'
            }
        };
    }

    // 6.5.1
    showFontSizeMenu(container, triggerButton) {
        const existing = container.querySelector('.font-size-menu');
        if (existing) {
            existing.remove();
            return;
        }

        const menu = document.createElement('div');
        menu.className = 'font-size-menu';
        menu.style.cssText = `
            position: absolute;
            top: 35px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1002;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 6px;
            padding: 6px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            min-width: 180px;
        `;

        const currentSize = window.mermaidFontController.getCurrentSize(container);

        Object.entries(window.mermaidFontController.availableSizes).forEach(([sizeName, config]) => {
            const item = document.createElement('button');
            item.className = `font-menu-item ${sizeName === currentSize ? 'active' : ''}`;
            item.style.cssText = `
                width: 100%;
                background: ${sizeName === currentSize ? 'var(--accent-blue)' : 'transparent'};
                color: ${sizeName === currentSize ? 'white' : 'var(--text-primary)'};
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                margin: 1px 0;
                display: flex;
                align-items: center;
                justify-content: space-between;
                transition: all 0.2s ease;
            `;

            item.innerHTML = `
                <span>${config.icon} ${config.label}</span>
                <span style="font-size: 10px; opacity: 0.8;">${config.value}px</span>
            `;

            item.addEventListener('click', () => {
                window.mermaidFontController.setFontSize(container, sizeName);
                menu.remove();
                this.updateFontButtonStates(container, triggerButton.closest('.viz-action-bar'));
                // IX: Re-render fullscreen if it's open
                this.reRenderFullscreenIfOpen(container, container.getAttribute('data-original-content'), container.getAttribute('data-chart-id'));
            });

            menu.appendChild(item);
        });

        container.appendChild(menu);

        const closeMenu = (e) => {
            if (!menu.contains(e.target) && e.target !== triggerButton) {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            }
        };

        setTimeout(() => document.addEventListener('click', closeMenu), 100);
    }

    // 6.5.2
    updateFontButtonStates(container, actionBar) {
        const currentSize = window.mermaidFontController.getCurrentSize(container);
        const sizeConfig = window.mermaidFontController.availableSizes[currentSize];

        const fontMenuBtn = actionBar.querySelector('[data-function="fontSizeMenu"]');
        if (fontMenuBtn && sizeConfig) {
            fontMenuBtn.title = `Font: ${sizeConfig.label} (${sizeConfig.value}px)`;
            fontMenuBtn.innerHTML = `<i class="fas fa-text-height">${sizeConfig.icon}</i>`;
        }

        const sizeNames = Object.keys(window.mermaidFontController.availableSizes);
        const currentIndex = sizeNames.indexOf(currentSize);

        const fontDownBtn = actionBar.querySelector('[data-function="fontSizeDown"]');
        const fontUpBtn = actionBar.querySelector('[data-function="fontSizeUp"]');

        if (fontDownBtn) {
            fontDownBtn.disabled = currentIndex === 0;
            fontDownBtn.style.opacity = currentIndex === 0 ? '0.5' : '1';
        }

        if (fontUpBtn) {
            fontUpBtn.disabled = currentIndex === sizeNames.length - 1;
            fontUpBtn.style.opacity = currentIndex === sizeNames.length - 1 ? '0.5' : '1';
        }
    }

    // 6.5.3
    async toggleMermaidFontSize(container, diagramContent, chartId) {
        const existing = container.querySelector('.font-size-switcher');
        if (existing) {
            existing.remove();
            return;
        }

        const switcher = document.createElement('div');
        switcher.className = 'font-size-switcher';
        switcher.style.cssText = `
            position: absolute;
            top: 35px;
            right: 200px;
            z-index: 1001;
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border-primary) !important;
            border-radius: 6px !important;
            padding: 6px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            min-width: 120px;
        `;

        const select = document.createElement('select');
        select.className = 'font-size-select';
        select.style.cssText = `
            background: var(--bg-secondary) !important;
            border: none !important;
            border-radius: 4px !important;
            padding: 8px 12px !important;
            font-size: 12px !important;
            cursor: pointer !important;
            color: var(--text-primary) !important;
            width: 100% !important;
            box-sizing: border-box !important;
        `;

        // Font size options
        const fontSizes = [
            { value: '10', label: '10px - Tiny' },
            { value: '12', label: '12px - Small' },
            { value: '14', label: '14px - Normal' },
            { value: '16', label: '16px - Medium' },
            { value: '18', label: '18px - Large' },
            { value: '20', label: '20px - Extra Large' },
            { value: '24', label: '24px - Huge' }
        ];

        const currentSize = container.getAttribute('data-font-size') || '14';

        fontSizes.forEach(({ value, label }) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            if (value === currentSize) {
                option.selected = true;
            }
            select.appendChild(option);
        });

        select.onchange = async (e) => {
            const newSize = parseInt(e.target.value);
            await this.applyMermaidFontSize(container, diagramContent, chartId, newSize);
            // Keep dropdown open for easy size comparison
        };

        switcher.appendChild(select);
        container.appendChild(switcher);

        // lick outside to close
        const handleClickOutside = (e) => {
            if (!switcher.contains(e.target) && !e.target.closest('[data-function="toggleFontSize"]')) {
                switcher.remove();
                document.removeEventListener('click', handleClickOutside);
            }
        };

        setTimeout(() => {
            document.addEventListener('click', handleClickOutside);
        }, 100);
    }


    // 6.6.1 - FIXED: Better error handling and parameter validation
    toggleMermaidExportOptions(container, diagramContent, chartId) {
        const existing = container.querySelector('.export-options-switcher');
        if (existing) {
            existing.remove();
            return;
        }

        // ALIDATION: Check if we have content to export
        if (!diagramContent || diagramContent.trim() === '') {
            console.error(' No diagram content available for export');
            this.showNotification(' No diagram content to export', 'error');
            return;
        }

        console.log('🎯 Creating export options for Mermaid:', {
            contentLength: diagramContent.length,
            hasContainer: !!container,
            chartId
        });

        const switcher = document.createElement('div');
        switcher.className = 'export-options-switcher';
        switcher.style.cssText = `
            position: absolute;
            top: 10px;
            right: 40px;
            z-index: 1001;
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border-primary) !important;
            border-radius: 6px !important;
            padding: 8px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            display: flex;
            gap: 4px;
            min-width: 200px;
        `;

        const exportFormats = [
            { value: 'png', label: 'PNG', icon: '🖼️', title: 'Export as PNG Image' },
            { value: 'svg', label: 'SVG', icon: '◻️', title: 'Export as SVG Vector' },
            { value: 'mermaid', label: 'Code', icon: '💾', title: 'Export Mermaid Code' }
        ];

        exportFormats.forEach(({ value, label, icon, title }) => {
            const button = document.createElement('button');
            button.className = 'export-format-btn';
            button.value = value;
            button.title = title;
            button.innerHTML = `${icon}<br><span style="font-size: 10px;">${label}</span>`;
            button.style.cssText = `
                background: var(--bg-primary) !important;
                border: 1px solid var(--border-primary) !important;
                border-radius: 4px !important;
                padding: 8px 6px !important;
                font-size: 11px !important;
                cursor: pointer !important;
                color: var(--text-primary) !important;
                flex: 1;
                text-align: center;
                transition: all 0.2s ease;
                line-height: 1.2;
            `;

            // Hover effect
            button.onmouseenter = () => {
                button.style.background = 'var(--bg-tertiary) !important';
                button.style.borderColor = 'var(--accent-primary) !important';
            };
            button.onmouseleave = () => {
                button.style.background = 'var(--bg-primary) !important';
                button.style.borderColor = 'var(--border-primary) !important';
            };

            button.onclick = async (e) => {
                e.preventDefault();
                e.stopPropagation();

                const format = button.value;
                console.log('🎯 Export format selected:', format);

                // Disable button during export
                button.disabled = true;
                button.style.opacity = '0.6';
                button.innerHTML = `⏳<br><span style="font-size: 10px;">Wait...</span>`;

                try {
                    console.log('🔄 Calling exportMermaidChart with:', {
                        hasContainer: !!container,
                        contentLength: diagramContent.length,
                        format
                    });

                    await this.exportMermaidChart(container, diagramContent, format);
                    switcher.remove();
                } catch (error) {
                    console.error(' Export failed:', error);
                    this.showNotification(' Export failed: ' + error.message, 'error');

                    // Restore button on error
                    button.disabled = false;
                    button.style.opacity = '1';
                    button.innerHTML = `${icon}<br><span style="font-size: 10px;">${label}</span>`;
                }
            };

            switcher.appendChild(button);
        });

        container.appendChild(switcher);

        // Click outside to close
        const handleClickOutside = (e) => {
            if (!switcher.contains(e.target) && !e.target.closest('[data-function="exportOptions"]')) {
                switcher.remove();
                document.removeEventListener('click', handleClickOutside);
            }
        };

        setTimeout(() => {
            document.addEventListener('click', handleClickOutside);
        }, 100);
    }

    // 6.6.2 - COMPLETELY FIXED: Better validation and comprehensive export handling
    async exportMermaidChart(container, diagramContent, format) {
        const timestamp = new Date().toISOString().slice(0, 16).replace(/[:]/g, '-');
        const filename = `mermaid-${timestamp}`;

        console.log('🎯 exportMermaidChart called:', {
            format,
            filename,
            hasContainer: !!container,
            contentLength: diagramContent?.length || 0
        });

        // ALIDATION: Check parameters
        if (!container) {
            console.error(' No container provided');
            this.showNotification(' Export failed: No container', 'error');
            return;
        }

        if (!diagramContent || diagramContent.trim() === '') {
            console.error(' No diagram content provided');
            this.showNotification(' Export failed: No diagram content', 'error');
            return;
        }

        try {
            switch (format) {
                case 'png':
                    console.log('📷 Starting FIXED PNG export...');
                    await this.exportMermaidToPNGFixed(container, filename);
                    break;

                case 'svg':
                    console.log('📊 Starting FIXED SVG export...');
                    await this.exportMermaidToSVGFixed(container, filename);
                    break;

                case 'mermaid':
                    console.log('💾 Starting Mermaid code export...');
                    this.downloadFile(diagramContent, `${filename}.mmd`, 'text/plain');
                    this.showNotification('ermaid code exported', 'success');
                    break;

                default:
                    console.error(' Unknown export format:', format);
                    this.showNotification(' Unknown export format', 'error');
            }
        } catch (error) {
            console.error(' Mermaid export error:', error);
            this.showNotification(' Export failed: ' + error.message, 'error');
        }
    }

    // (Removed V5-specific export CSS embedding helper to align with V4 behavior)

    // OMPLETELY NEW: Fixed SVG export that preserves UI styling
    //  COLETELY NEW: Fixed SVG export that preserves UI styling
    // OMPLETELY FIXED: SVG export that preserves exact UI display
    async exportMermaidToSVGFixed(container, filename) {
        console.log('📊 exportMermaidToSVGFixed - Using WORKING test UI approach for SVG export');

        try {
            // STEP 1: Get the SVG element (same as working test UI)
            const vizContentArea = container.querySelector('.viz-content-area');
            if (!vizContentArea) {
                console.error('❌ No viz-content-area found in container');
                this.showNotification('❌ No content area found to export', 'error');
                return;
            }

            const renderedSvg = vizContentArea.querySelector('svg');
            if (!renderedSvg) {
                console.error('❌ No SVG element found in viz-content-area');
                this.showNotification('❌ No diagram found to export', 'error');
                return;
            }

            console.log('✅ Found SVG for SVG export');

            // STEP 2: Clone and apply post-processing (working test UI approach)
            const clonedSvg = renderedSvg.cloneNode(true);

            // Apply post-processing to SVG export (this was the missing piece!)
            // EW (Jul 22 2026): drop isDark arg — canvas is always white now
            this.applySimplifiedMermaidPostProcessing(clonedSvg);
            // Note: Hardening helpers remain disabled; we only add a minimal CSS snippet later
            //       to normalize bullet BRs for export without changing live chat rendering.
            console.log('🎨 Applied UI post-processing to SVG export');

            const svgRect = renderedSvg.getBoundingClientRect();
            const displayedWidth = svgRect.width;
            const displayedHeight = svgRect.height;

            console.log('📐 SVG export dimensions from UI:', { displayedWidth, displayedHeight });

            // STEP 3: Copy styles (working test UI approach)
            const originalElements = renderedSvg.querySelectorAll('*');
            const clonedElements = clonedSvg.querySelectorAll('*');

            Array.from(renderedSvg.attributes).forEach(attr => {
                clonedSvg.setAttribute(attr.name, attr.value);
            });

            originalElements.forEach((originalEl, index) => {
                const clonedEl = clonedElements[index];
                if (!clonedEl) return;

                Array.from(originalEl.attributes).forEach(attr => {
                    clonedEl.setAttribute(attr.name, attr.value);
                });

                const computedStyle = window.getComputedStyle(originalEl);
                const criticalProps = [
                    'width', 'height', 'x', 'y', 'cx', 'cy', 'r', 'rx', 'ry',
                    'fill', 'stroke', 'stroke-width', 'stroke-dasharray',
                    'font-family', 'font-size', 'font-weight', 'font-style',
                    'text-anchor', 'dominant-baseline', 'alignment-baseline',
                    'opacity', 'visibility', 'display', 'transform'
                ];

                const styleProps = [];
                criticalProps.forEach(prop => {
                    let value = computedStyle.getPropertyValue(prop);
                    if (value && value !== 'none' && value !== 'auto' && value !== 'normal' && value !== '') {
                        // Font size reduction for export while keeping nodes same size
                        if (prop === 'font-size' && originalEl.tagName.toLowerCase() === 'text') {
                            const fontSize = parseFloat(value);
                            if (!isNaN(fontSize)) {
                                const reducedSize = fontSize * 0.9; // 10% reduction
                                value = `${reducedSize}px`;
                                console.log(`📝 SVG Export font size reduced: ${fontSize}px → ${reducedSize}px`);
                            }
                        }
                        styleProps.push(`${prop}: ${value}`);
                    }
                });

                if (styleProps.length > 0) {
                    const existingStyle = clonedEl.getAttribute('style') || '';
                    clonedEl.setAttribute('style', existingStyle + (existingStyle ? '; ' : '') + styleProps.join('; '));
                }
            });

            // STEP 4: Set proper SVG export attributes (working test UI approach)
            clonedSvg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
            clonedSvg.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
            clonedSvg.setAttribute('width', displayedWidth);
            clonedSvg.setAttribute('height', displayedHeight);

            // Preserve current viewBox
            const originalViewBox = renderedSvg.getAttribute('viewBox');
            if (originalViewBox) {
                clonedSvg.setAttribute('viewBox', originalViewBox);
            } else {
                const bbox = renderedSvg.getBBox();
                if (bbox && bbox.width > 0 && bbox.height > 0) {
                    clonedSvg.setAttribute('viewBox', `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`);
                }
            }

            // STEP 5: Add background and proper styling (working test UI approach)
            clonedSvg.setAttribute('style', `
            background: white;
            font-family: "Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            width: ${displayedWidth}px;
            height: ${displayedHeight}px;
        `);

            // STEP 5.5: Export-only bullet spacing fix (hide/remove <br> between bullets)
            // Explanation:
            // - Exports are generated from a cloned SVG to avoid side-effects.
            // - We embed a compact CSS (MermaidExportCSS) to hide BRs after bullet spans and
            //   also programmatically strip any stray BR nodes around bullets. This prevents
            //   the "empty line between bullets" issue in exported images.
            try {
                // Embed CSS that hides BRs between bullet spans inside FO content
                if (typeof window.MermaidExportCSS === 'function') {
                    const css = window.MermaidExportCSS();
                    if (css) embedStyleIntoSvg(clonedSvg, css);
                }
                // Also strip explicit <br class="mermaid-br"> siblings around bullet spans to avoid empty lines
                stripBreaksAroundBullets(clonedSvg);
                console.log('✅ Applied export-only bullet BR cleanup for SVG');
            } catch (e) {
                console.warn('⚠️ Failed export-only bullet cleanup (SVG):', e);
            }

            // STEP 6: Create and download SVG file (working test UI approach)
            const serializer = new XMLSerializer();
            let svgData = serializer.serializeToString(clonedSvg);

            // Add XML declaration for better compatibility
            svgData = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
${svgData}`;

            console.log('📊 UI-exact SVG data prepared with working test UI approach');

            // Download the file
            this.downloadFile(svgData, `${filename}.svg`, 'image/svg+xml');
            this.showNotificati(' ermaid exported as SVG with working test UI approach', 'success');

        } catch (error) {
            console.error(' SVG export error:', error);
            this.showNotification(' SVG export failed: ' + error.message, 'error');
            throw error;
        }
    }

    // 6.6.3 - FIXED: Better error handling for file download
    downloadFile(content, filename, mimeType) {
        console.log('📥 downloadFile called:', {
            contentLength: content?.length || 0,
            filename,
            mimeType
        });

        try {
            if (!content) {
                throw new Error('No content to download');
            }

            const blob = new Blob([content], { type: mimeType });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');

            link.href = url;
            link.download = filename;
            link.style.display = 'none';

            document.body.appendChild(link);

            console.log('🔽 Triggering download...', { href: link.href, download: link.download });
            link.click();

            // Cleanup
            document.body.removeChild(link);
            URL.revokeObjectURL(url);

            console.log('ownload triggered successfully');

        } catch (error) {
            console.error(' Download file error:', error);
            this.showNotification(' Download failed: ' + error.message, 'error');
            throw error;
        }
    }

    // 6.6.4 OMPLETELY FIXED: Simple PNG export using html2canvas (like Plotly)
    // OMPLETELY FIXED: PNG export using the EXACT approach from working test UI
    async exportMermaidToPNGFixed(container, filename) {
        console.log('🚀 exportMermaidToPNGFixed - Using WORKING test UI approach');

        try {
            // TEP 1: Get the SVG element (same as working test UI)
            const vizContentArea = container.querySelector('.viz-content-area');
            if (!vizContentArea) {
                console.error(' No viz-content-area found in container');
                this.showNotification(' No content area found to export', 'error');
                return;
            }

            const renderedSvg = vizContentArea.querySelector('svg');
            if (!renderedSvg) {
                console.error(' No SVG element found in viz-content-area');
                this.showNotification(' No diagram found to export', 'error');
                return;
            }

            console.log('ound SVG for PNG export');

            // TEP 2: Get COMPLETE SVG bounds using getBBox() (working test UI approach)
            const svgBBox = renderedSvg.getBBox();
            const contentX = svgBBox.x;
            const contentY = svgBBox.y;
            const contentWidth = svgBBox.width;
            const contentHeight = svgBBox.height;

            console.log(`📏 Content bounds: ${contentX},${contentY} ${contentWidth}x${contentHeight}`);

            // Add padding around content
            const padding = 20;
            const exportX = contentX - padding;
            const exportY = contentY - padding;
            const exportWidth = contentWidth + (padding * 2);
            const exportHeight = contentHeight + (padding * 2);

            console.log(`� Export bounds: ${exportX},${exportY} ${exportWidth}x${exportHeight}`);

            // TEP 3: Create clean clone (working test UI approach)
            const clonedSvg = renderedSvg.cloneNode(true);

            // RITICAL: Remove transform attributes (working test UI fix)
            clonedSvg.removeAttribute('transform');
            clonedSvg.style.transform = '';

            // Apply post-processing to match working SVG export
            // EW (Jul 22 2026): drop isDark arg — canvas is always white now
            this.applySimplifiedMermaidPostProcessing(clonedSvg);
            // Note: Other export hardening helpers remain disabled; we inject only minimal
            //       CSS later to normalize bullet BRs specifically for export.
            console.log('🎨 Applied UI post-processing to clean SVG clone');

            // TEP 4: Copy styles (working test UI approach)
            const originalElements = renderedSvg.querySelectorAll('*');
            const clonedElements = clonedSvg.querySelectorAll('*');

            Array.from(renderedSvg.attributes).forEach(attr => {
                if (attr.name !== 'transform') { // Skip transform attributes
                    clonedSvg.setAttribute(attr.name, attr.value);
                }
            });

            originalElements.forEach((originalEl, index) => {
                const clonedEl = clonedElements[index];
                if (!clonedEl) return;

                Array.from(originalEl.attributes).forEach(attr => {
                    if (attr.name !== 'transform') { // Skip transform attributes
                        clonedEl.setAttribute(attr.name, attr.value);
                    }
                });

                const computedStyle = window.getComputedStyle(originalEl);
                const criticalProps = [
                    'width', 'height', 'x', 'y', 'cx', 'cy', 'r', 'rx', 'ry',
                    'fill', 'stroke', 'stroke-width', 'stroke-dasharray',
                    'font-family', 'font-size', 'font-weight', 'font-style',
                    'text-anchor', 'dominant-baseline', 'alignment-baseline',
                    'opacity', 'visibility', 'display'
                    // Removed 'transform' from critical props (working test UI fix)
                ];

                const styleProps = [];
                criticalProps.forEach(prop => {
                    let value = computedStyle.getPropertyValue(prop);
                    if (value && value !== 'none' && value !== 'auto' && value !== 'normal' && value !== '') {
                        // ont size reduction for export while keeping nodes same size
                        if (prop === 'font-size' && originalEl.tagName.toLowerCase() === 'text') {
                            const fontSize = parseFloat(value);
                            if (!isNaN(fontSize)) {
                                const reducedSize = fontSize * 0.9; // 10% reduction
                                value = `${reducedSize}px`;
                                console.log(`📝 Export font size reduced: ${fontSize}px → ${reducedSize}px`);
                            }
                        }
                        styleProps.push(`${prop}: ${value}`);
                    }
                });

                if (styleProps.length > 0) {
                    const existingStyle = clonedEl.getAttribute('style') || '';
                    // Remove any transform styles (working test UI fix)
                    const cleanStyle = existingStyle.replace(/transform[^;]*;?/g, '');
                    clonedEl.setAttribute('style', cleanStyle + (cleanStyle ? '; ' : '') + styleProps.join('; '));
                }
            });

            // TEP 5: Set dimensions and viewBox (working test UI approach)
            clonedSvg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
            clonedSvg.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
            clonedSvg.setAttribute('width', exportWidth);
            clonedSvg.setAttribute('height', exportHeight);

            // RITICAL: Set viewBox to capture all content (working test UI approach)
            clonedSvg.setAttribute('viewBox', `${exportX} ${exportY} ${exportWidth} ${exportHeight}`);

            clonedSvg.setAttribute('style', `
                background: white;
                font-family: "Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                width: ${exportWidth}px;
                height: ${exportHeight}px;
                transform: none;
            `);

            // TEP 5.5: Export-only bullet spacing fix (hide/remove <br> between bullets)
            // Explanation:
            // - Before rasterizing the cloned SVG to PNG, embed minimal CSS and strip BRs
            //   around `.mermaid-bullet` so the PNG has compact bullets like the chat UI.
            // - Operates on the clone only; live DOM is untouched.
            try {
                if (typeof window.MermaidExportCSS === 'function') {
                    const css = window.MermaidExportCSS();
                    if (css) embedStyleIntoSvg(clonedSvg, css);
                }
                stripBreaksAroundBullets(clonedSvg);
                console.log('pplied export-only bullet BR cleanup for PNG (SVG->PNG path)');
            } catch (e) {
                console.warn('⚠️ Failed export-only bullet cleanup (PNG path):', e);
            }

            // TEP 6: Convert to PNG (working test UI approach)
            const serializer = new XMLSerializer();
            const svgString = serializer.serializeToString(clonedSvg);

            // Create high-quality canvas using COMPLETE content dimensions
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const scale = 2; // Reasonable scale for quality

            canvas.width = exportWidth * scale;
            canvas.height = exportHeight * scale;
            canvas.style.width = exportWidth + 'px';
            canvas.style.height = exportHeight + 'px';

            ctx.scale(scale, scale);
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, exportWidth, exportHeight);

            // Convert SVG to data URL (working test UI approach)
            const svgDataUrl = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgString)));

            const self = this;
            return new Promise((resolve, reject) => {
                const img = new Image();

                img.onload = function () {
                    try {
                        console.log('🖼️ Complete SVG loaded, drawing full content to PNG canvas...');

                        // Draw the complete content
                        ctx.drawImage(img, 0, 0, exportWidth, exportHeight);

                        canvas.toBlob(blob => {
                            if (blob && blob.size > 0) {
                                const url = URL.createObjectURL(blob);
                                const link = document.createElement('a');
                                link.href = url;
                                link.download = `${filename}.png`;
                                link.style.display = 'none';

                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                                URL.revokeObjectURL(url);

                                self.showNotification(`NG exported with complete content (${exportWidth}x${exportHeight} @ ${scale}x quality)`, 'success');
                                console.log(`omplete PNG export completed (${exportWidth}x${exportHeight} @ ${scale}x quality)`);
                                resolve();

                            } else {
                                console.log(' Complete PNG Canvas toBlob failed');
                                console.log('🔄 Method 1 failed, trying Method 2...');
                                self.exportMermaidToPNGMethod2(container, filename).then(resolve).catch(reject);
                            }
                        }, 'image/png', 0.98);

                    } catch (drawError) {
                        console.log(` Complete PNG drawing error: ${drawError.message}`);
                        console.log('🔄 Method 1 failed, trying Method 2...');
                        self.exportMermaidToPNGMethod2(container, filename).then(resolve).catch(reject);
                    }
                };

                img.onerror = function (error) {
                    console.log(` Complete SVG image load error: ${error}`);
                    console.log('🔄 Method 1 failed, trying Method 2...');
                    self.exportMermaidToPNGMethod2(container, filename).then(resolve).catch(reject);
                };

                console.log('🔄 Loading complete SVG with full content bounds...');
                img.src = svgDataUrl;
            });

        } catch (error) {
            console.error(' Method 1 PNG export error:', error);
            console.log('🔄 Method 1 failed, trying Method 2...');
            return this.exportMermaidToPNGMethod2(container, filename);
        }
    }

    // EW: Method 2 - html2canvas direct capture
    async exportMermaidToPNGMethod2(container, filename) {
        console.log('🚀 exportMermaidToPNGMethod2 - Method 2: Direct html2canvas');

        try {
            const vizContentArea = container.querySelector('.viz-content-area');
            if (!vizContentArea) {
                throw new Error('No content area found for Method 2');
            }

            // Check if html2canvas is available
            if (typeof html2canvas !== 'function') {
                console.log('🔄 html2canvas not available, trying Method 3...');
                return this.exportMermaidToPNGMethod3(container, filename);
            }

            console.log('� Using html2canvas for direct capture...');

            const canvas = await html2canvas(vizContentArea, {
                backgroundColor: '#ffffff',
                scale: 3, // High quality
                useCORS: true,
                allowTaint: false,
                foreignObjectRendering: true,
                logging: false,
                removeContainer: true,
                imageTimeout: 15000,
                onclone: (clonedDoc) => {
                    const clonedVizArea = clonedDoc.querySelector('.viz-content-area');
                    if (clonedVizArea) {
                        clonedVizArea.style.fontFamily = '"Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
                        // Export-only cleanup inside the html2canvas clone:
                        // - Remove BR nodes that follow `.mermaid-bullet` within cloned SVG
                        //   foreignObject HTML so screenshots don't show empty lines between bullets.
                        // - Operates on the cloned document only; the live chat UI remains unchanged.
                        try {
                            // Remove <br class="mermaid-br"> following bullet spans inside any cloned SVG foreignObject
                            const targetRoots = clonedVizArea.querySelectorAll('svg');
                            targetRoots.forEach(svg => {
                                // Direct removal of BRs after bullet spans
                                svg.querySelectorAll('span.mermaid-bullet + br.mermaid-br').forEach(br => {
                                    br.parentNode && br.parentNode.removeChild(br);
                                });
                                // Also remove preceding BRs if any stray ones remain
                                svg.querySelectorAll('span.mermaid-bullet').forEach(span => {
                                    const prev = span.previousSibling;
                                    if (prev && prev.nodeType === 1 && prev.tagName.toLowerCase() === 'br' && prev.classList.contains('mermaid-br')) {
                                        prev.parentNode && prev.parentNode.removeChild(prev);
                                    }
                                });
                            });
                            console.log('pplied export-only bullet BR cleanup in html2canvas clone');
                        } catch (e) {
                            console.warn('⚠️ Failed bullet BR cleanup in html2canvas clone:', e);
                        }
                    }
                }
            });

            return new Promise((resolve, reject) => {
                canvas.toBlob(blob => {
                    if (blob && blob.size > 0) {
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.download = `${filename}.png`;
                        link.style.display = 'none';

                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        URL.revokeObjectURL(url);

                        this.showNotification('NG exported via html2canvas (Method 2)', 'success');
                        console.log('ethod 2 PNG export completed successfully');
                        resolve();
                    } else {
                        console.log('🔄 Method 2 failed, trying Method 3...');
                        this.exportMermaidToPNGMethod3(container, filename).then(resolve).catch(reject);
                    }
                }, 'image/png', 0.95);
            });

        } catch (error) {
            console.error(' Method 2 error:', error);
            console.log('🔄 Method 2 failed, trying Method 3...');
            return this.exportMermaidToPNGMethod3(container, filename);
        }
    }

    // EW: Method 3 - Fallback to SVG export
    async exportMermaidToPNGMethod3(container, filename) {
        console.log('🚀 exportMermaidToPNGMethod3 - Method 3: SVG fallback');

        try {
            console.log('🔄 All PNG methods failed, exporting as SVG...');
            await this.exportMermaidToSVGFixed(container, filename);
            this.showNotification('⚠️ PNG export failed, saved as SVG instead', 'warning');
        } catch (svgError) {
            console.error(' All export methods failed:', svgError);
            this.showNotification(' All export methods failed - please try again', 'error');
        }
    }

    // NHANCED: Improved fallback PNG export with comprehensive options based on online research
    async exportMermaidToPNGFallback(container, filename) {
        console.log('🔄 Using enhanced fallback PNG export method...');

        try {
            const vizContentArea = container.querySelector('.viz-content-area');
            if (!vizContentArea) {
                throw new Error('No content area found to export');
            }

            // EST PRACTICE: Try html2canvas first (most reliable for complex DOM)
            if (window.html2canvas) {
                console.log('📸 Attempting html2canvas export with optimized settings...');

                const canvas = await html2canvas(vizContentArea, {
                    backgroundColor: '#ffffff',
                    scale: 3, // Higher quality for better export
                    useCORS: true,
                    allowTaint: false,
                    foreignObjectRendering: true,
                    logging: false,
                    removeContainer: true,
                    imageTimeout: 15000,
                    // ESEARCH FINDING: Better cross-browser compatibility
                    onclone: (clonedDoc) => {
                        // Ensure all fonts are loaded in cloned document
                        const clonedVizArea = clonedDoc.querySelector('.viz-content-area');
                        if (clonedVizArea) {
                            clonedVizArea.style.fontFamily = '"Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
                        }
                    }
                });

                return new Promise((resolve, reject) => {
                    canvas.toBlob(blob => {
                        if (blob && blob.size > 0) {
                            const url = URL.createObjectURL(blob);
                            const link = document.createElement('a');
                            link.href = url;
                            link.download = `${filename}.png`;
                            link.style.display = 'none';

                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            URL.revokeObjectURL(url);

                            this.showNotification('ermaid exported as PNG using html2canvas', 'success');
                            resolve();
                        } else {
                            reject(new Error('html2canvas failed to create valid blob'));
                        }
                    }, 'image/png', 0.98);
                });
            }

            // ALLBACK 2: Direct DOM-to-Canvas if html2canvas unavailable
            console.log('🔄 html2canvas not available, trying DOM-to-Canvas...');
            await this.exportViaDOMToCanvas(vizContentArea, filename);

        } catch (error) {
            console.error(' Enhanced fallback PNG export error:', error);

            // INAL FALLBACK: SVG export with user notification
            try {
                console.log('🔄 All PNG methods failed, exporting as SVG...');
                await this.exportMermaidToSVGFixed(container, filename);
                this.showNotification('⚠️ PNG export failed, saved as SVG instead', 'warning');
            } catch (svgError) {
                console.error(' All export methods failed:', svgError);
                this.showNotification(' All export methods failed - please try again', 'error');
            }
        }
    }

    // EW: Additional fallback method for DOM-to-Canvas export
    async exportViaDOMToCanvas(vizContentArea, filename) {
        console.log('🎨 Attempting direct DOM-to-Canvas export...');

        const svgElement = vizContentArea.querySelector('svg');
        if (!svgElement) {
            throw new Error('No SVG element found for DOM-to-Canvas export');
        }

        const rect = svgElement.getBoundingClientRect();
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const scale = 2;

        canvas.width = rect.width * scale;
        canvas.height = rect.height * scale;
        ctx.scale(scale, scale);
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, rect.width, rect.height);

        // ESEARCH FINDING: Use serialized SVG data URL approach
        const serializer = new XMLSerializer();
        const svgString = serializer.serializeToString(svgElement);
        const svgDataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgString)}`;

        return new Promise((resolve, reject) => {
            const img = new Image();

            img.onload = () => {
                try {
                    ctx.drawImage(img, 0, 0, rect.width, rect.height);
                    canvas.toBlob(blob => {
                        if (blob && blob.size > 0) {
                            const url = URL.createObjectURL(blob);
                            const link = document.createElement('a');
                            link.href = url;
                            link.download = `${filename}.png`;
                            link.style.display = 'none';

                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            URL.revokeObjectURL(url);

                            this.showNotification('ermaid exported via DOM-to-Canvas method', 'success');
                            resolve();
                        } else {
                            reject(new Error('DOM-to-Canvas failed to create valid blob'));
                        }
                    }, 'image/png', 0.95);
                } catch (drawError) {
                    reject(drawError);
                }
            };

            img.onerror = () => reject(new Error('Failed to load SVG for DOM-to-Canvas'));
            img.src = svgDataUrl;
        });
    }

    // NHANCED: Direct SVG to Canvas conversion with improved error handling
    async svgToCanvas(svgElement, filename) {
        const self = this; // Store reference to this for use in callbacks
        return new Promise((resolve, reject) => {
            try {
                // Get SVG dimensions
                const bbox = svgElement.getBBox();
                const svgWidth = parseInt(svgElement.getAttribute('width')) || bbox.width || 800;
                const svgHeight = parseInt(svgElement.getAttribute('height')) || bbox.height || 600;

                console.log('🎨 Enhanced SVG to Canvas conversion:', { svgWidth, svgHeight, bbox });

                // Create a canvas with high DPI
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                const scale = 3; // Higher resolution for better quality

                canvas.width = svgWidth * scale;
                canvas.height = svgHeight * scale;
                ctx.scale(scale, scale);

                // Fill white background
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, svgWidth, svgHeight);

                // Clone and prepare SVG for export
                const clonedSvg = svgElement.cloneNode(true);
                clonedSvg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
                clonedSvg.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
                clonedSvg.setAttribute('width', svgWidth);
                clonedSvg.setAttribute('height', svgHeight);

                // ESEARCH FINDING: Better SVG serialization
                const serializer = new XMLSerializer();
                const svgString = serializer.serializeToString(clonedSvg);
                const svgDataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgString)}`;

                const img = new Image();

                // NHANCED: Better CORS handling
                img.crossOrigin = 'anonymous';
                img.setAttribute('crossorigin', 'anonymous');

                img.onload = function () {
                    try {
                        // ESEARCH FINDING: Test canvas for taint
                        try {
                            ctx.getImageData(0, 0, 1, 1);
                        } catch (testError) {
                            reject(new Error('Canvas tainted before drawing SVG'));
                            return;
                        }

                        ctx.drawImage(img, 0, 0, svgWidth, svgHeight);

                        // Test again after drawing
                        try {
                            ctx.getImageData(0, 0, 1, 1);
                        } catch (postDrawError) {
                            reject(new Error('Canvas tainted after drawing SVG'));
                            return;
                        }

                        canvas.toBlob(blob => {
                            if (blob && blob.size > 0) {
                                const url = URL.createObjectURL(blob);
                                const link = document.createElement('a');
                                link.href = url;
                                link.download = `${filename}.png`;
                                link.style.display = 'none';

                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                                URL.revokeObjectURL(url);

                                self.showNotification('ermaid exported via enhanced SVG-to-Canvas', 'success');
                                resolve();
                            } else {
                                reject(new Error('Failed to create PNG blob from SVG'));
                            }
                        }, 'image/png', 0.98);

                    } catch (drawError) {
                        reject(drawError);
                    }
                };

                img.onerror = function (error) {
                    reject(new Error('Failed to load SVG image for canvas conversion'));
                };

                img.src = svgDataUrl;

            } catch (error) {
                reject(error);
            }
        });
    }

    // 6.6.3
    async copyMermaidCode(diagramContent) {
        try {
            await navigator.clipboard.writeText(diagramContent);
            this.showNotification('📋 Mermaid code copied to clipboard', 'success');
        } catch (err) {
            console.error('Failed to copy:', err);
            this.showNotification(' Failed to copy code', 'error');
        }
    }

    // 6.6.4
    showMermaidError(mermaidDiv, error, originalContent) {
        const errorMessage = error.message || 'Unknown error';

        // Sanitize the error message and content to avoid XSS
        const escapeHtml = (str) => String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');

        const safeError = escapeHtml(errorMessage);
        const safeContent = escapeHtml(originalContent || '');

        // Ensure the mermaidDiv is contained within the viz-content-area
        // and does NOT leak outside by using contained inline styles only
        mermaidDiv.style.cssText = `
            width: 100%;
            box-sizing: border-box;
            border: none !important;
            background: transparent !important;
            outline: none !important;
        `;

        mermaidDiv.innerHTML = `
            <div style="
                padding: 16px 20px;
                border: 1px dashed rgba(239, 68, 68, 0.5);
                border-radius: 8px;
                background: rgba(239, 68, 68, 0.06);
                color: var(--text-primary, #24292f);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                text-align: left;
                max-width: 100%;
                width: 100%;
                box-sizing: border-box;
                overflow: hidden;
            ">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                    <span style="color: #ef4444; font-size: 16px;">⚠️</span>
                    <strong style="color: #ef4444; font-size: 14px;">Diagram Syntax Error</strong>
                </div>
                <p style="margin: 0 0 10px 0; font-size: 13px; color: var(--text-secondary, #656d76); line-height: 1.5;">
                    ${safeError}
                </p>
                <details style="margin-top: 8px;">
                    <summary style="cursor: pointer; font-size: 12px; color: var(--accent-blue, #3b82f6); user-select: none;">
                        View diagram source
                    </summary>
                    <pre style="
                        margin: 8px 0 0 0;
                        padding: 10px;
                        background: rgba(0,0,0,0.08);
                        border-radius: 4px;
                        font-family: 'Monaco', 'Menlo', monospace;
                        font-size: 11px;
                        max-height: 180px;
                        overflow-y: auto;
                        white-space: pre-wrap;
                        word-break: break-word;
                        color: var(--text-primary, #24292f);
                        border: none;
                        outline: none;
                    ">${safeContent}</pre>
                </details>
            </div>
        `;

        // Remove any mermaid-injected error elements that escape the container
        this._cleanupMermaidGlobalErrors();
    }

    /**
     * Remove orphan Mermaid elements that escape their container.
     * NOTE: We deliberately do NOT remove nodes whose IDs start with
     * 'dmermaid' -- those are Mermaid's own render staging elements and
     * are normally cleaned up by Mermaid after `render()` settles.  Removing
     * them mid-flight produces the broken viewBox / retry storm.
     */
    _cleanupMermaidGlobalErrors() {
        try {
            // Only target truly orphaned .mermaid containers (outside viz wrappers).
            // Mermaid's d-renderId staging nodes are excluded by design.
            const orphanedErrorNodes = document.querySelectorAll(
                'body > .mermaid:not(.viz-container .mermaid)'
            );
            orphanedErrorNodes.forEach(el => el.remove());

            // Also remove any mermaid-injected <style> tags that add purple borders globally
            const mermaidStyles = document.querySelectorAll('style[id^="mermaid-"]');
            mermaidStyles.forEach(style => {
                // Keep our own styles, only remove mermaid's injected ones
                if (!style.id.includes('font-controller') && !style.id.includes('viz-engine')) {
                    // Override border rules to none rather than removing (safer)
                    const content = style.textContent || '';
                    if (content.includes('border') && (
                        content.includes('#') || content.includes('purple') || content.includes('rgb')
                    )) {
                        style.textContent = style.textContent
                            .replace(/\.mermaid\s*\{[^}]*border[^}]*\}/g, '.mermaid { border: none !important; }');
                    }
                }
            });
        } catch (e) {
            // Silently ignore cleanup errors
        }
    }

    /**
     * =============================================================================
     * SECTION 7: OTHER CHART TYPES
     * =============================================================================
     */

    // 7.1.1
    async renderGoogleChartDirectly(item, contentArea, chartId) {
        if (!window.google || !window.google.visualization) {
            throw new Error('Google Charts library not loaded');
        }

        // RITICAL: DOM validation before any DOM manipulation
        if (!contentArea) {
            throw new Error('Content area is null - cannot render Google Chart');
        }
        if (!document.contains(contentArea)) {
            console.log('⚠️ VIZ-V3: Google Chart content area not in DOM yet (will be attached after message rendering)');
        }

        // IMING SAFETY: Add micro-delay to ensure DOM stability
        await new Promise(resolve => requestAnimationFrame(resolve));

        const chartDiv = document.createElement('div');
        chartDiv.id = chartId;
        chartDiv.style.cssText = `
            width: 100%;
            height: ${this.options.defaultHeight}px;
            position: relative;
            display: block;
            margin: 0 auto;
        `;

        // RITICAL: Triple-check DOM validity right before manipulation
        if (!contentArea || !document.contains(contentArea)) {
            console.log('⚠️ VIZ-V3: Google Chart content area not in DOM before appendChild (proceeding with render)');
        }

        contentArea.appendChild(chartDiv);

        const data = google.visualization.arrayToDataTable(item.data || item.dataTable);
        const ChartConstructor = google.visualization[item.chartType];

        if (!ChartConstructor) {
            throw new Error(`Unsupported Google Chart type: ${item.chartType}`);
        }

        const chart = new ChartConstructor(chartDiv);
        const isDark = this.options.theme === 'dark';

        const options = {
            ...item.options,
            fontName: this.options.fontFamily,
            backgroundColor: isDark ? '#0d1117' : '#ffffff',
            chartArea: { left: '10%', top: '15%', width: '75%', height: '70%' },
            legend: {
                position: 'bottom',
                alignment: 'center',
                textStyle: {
                    fontSize: 12,
                    color: isDark ? '#e6edf3' : '#24292f'
                }
            },
            height: this.options.defaultHeight,
            titleTextStyle: {
                color: isDark ? '#e6edf3' : '#24292f'
            },
            hAxis: {
                textStyle: { color: isDark ? '#e6edf3' : '#24292f' },
                titleTextStyle: { color: isDark ? '#e6edf3' : '#24292f' }
            },
            vAxis: {
                textStyle: { color: isDark ? '#e6edf3' : '#24292f' },
                titleTextStyle: { color: isDark ? '#e6edf3' : '#24292f' }
            }
        };

        chart.draw(data, options);

        const vizContainer = contentArea.closest('.viz-container');
        if (vizContainer) {
            this.addUnifiedActionBar(vizContainer, item, chartId, 'google');
        }
    }

    // 7.1.2
    async renderGoogleChart(item, container, chartId) {
        if (!window.google || !window.google.visualization) {
            throw new Error('Google Charts library not loaded');
        }

        const chartDiv = document.createElement('div');
        chartDiv.id = chartId;
        chartDiv.style.cssText = `
            width: 100%;
            height: ${this.options.defaultHeight}px;
            position: relative;
            display: block;
            margin: 0 auto;
        `;

        container.appendChild(chartDiv);

        const data = google.visualization.arrayToDataTable(item.data || item.dataTable);
        const ChartConstructor = google.visualization[item.chartType];

        if (!ChartConstructor) {
            throw new Error(`Unsupported Google Chart type: ${item.chartType}`);
        }

        const chart = new ChartConstructor(chartDiv);
        const isDark = this.options.theme === 'dark';

        const options = {
            ...item.options,
            fontName: this.options.fontFamily,
            backgroundColor: isDark ? '#0d1117' : '#ffffff',
            chartArea: { left: '10%', top: '15%', width: '75%', height: '70%' },
            legend: {
                position: 'bottom',
                alignment: 'center',
                textStyle: {
                    fontSize: 12,
                    color: isDark ? '#e6edf3' : '#24292f'
                }
            },
            height: this.options.defaultHeight,
            titleTextStyle: {
                color: isDark ? '#e6edf3' : '#24292f'
            },
            hAxis: {
                textStyle: { color: isDark ? '#e6edf3' : '#24292f' },
                titleTextStyle: { color: isDark ? '#e6edf3' : '#24292f' }
            },
            vAxis: {
                textStyle: { color: isDark ? '#e6edf3' : '#24292f' },
                titleTextStyle: { color: isDark ? '#e6edf3' : '#24292f' }
            }
        };

        chart.draw(data, options);

        // NIFIED: Add unified action bar for Google Charts
        this.addUnifiedActionBar(container, item, chartId, 'google');
    }

    // 7.2.1
    async renderChartJSDirectly(item, contentArea, chartId) {
        if (!window.Chart) {
            throw new Error('Chart.js library not loaded');
        }

        // RITICAL: DOM validation before any DOM manipulation
        if (!contentArea) {
            throw new Error('Content area is null - cannot render Chart.js');
        }
        if (!document.contains(contentArea)) {
            console.log('⚠️ VIZ-V3: Chart.js content area not in DOM yet (will be attached after message rendering)');
        }

        // IMING SAFETY: Add micro-delay to ensure DOM stability
        await new Promise(resolve => requestAnimationFrame(resolve));

        const canvas = document.createElement('canvas');
        canvas.id = chartId;

        // Chart.js requires explicit height (doesn't work with 'auto')
        const explicitHeight = (typeof this.options.defaultHeight === 'number')
            ? this.options.defaultHeight
            : 400; // Default to 400px if 'auto' or other string

        // Set canvas internal resolution
        canvas.width = 800;
        canvas.height = explicitHeight;

        canvas.style.cssText = `
            width: 100%;
            height: ${explicitHeight}px;
            position: relative;
            display: block;
            margin: 0 auto;
            box-sizing: border-box;
        `;

        // RITICAL: Triple-check DOM validity right before manipulation
        if (!contentArea || !document.contains(contentArea)) {
            console.log('⚠️ VIZ-V3: Chart.js content area not in DOM before appendChild (proceeding with render)');
        }

        // Wrap canvas in container to ensure proper sizing
        const canvasWrapper = document.createElement('div');
        canvasWrapper.className = 'chartjs-canvas-wrapper';
        canvasWrapper.style.cssText = `
            width: 100%;
            min-height: ${explicitHeight}px;
            position: relative;
            display: block;
        `;
        canvasWrapper.appendChild(canvas);
        contentArea.appendChild(canvasWrapper);

        // Parse config - handle both JSON and JavaScript notation with functions
        let config;
        if (typeof item.content === 'string') {
            try {
                config = JSON.parse(item.content);
            } catch (e) {
                // Fallback to JavaScript eval for function support (tooltips, formatters, etc.)
                console.log('ChartJS: Using JavaScript eval for object notation');
                try {
                    config = (new Function('return ' + item.content))();
                } catch (evalError) {
                    throw new Error(`Invalid ChartJS config: ${evalError.message}`);
                }
            }
        } else {
            config = item.content;
        }

        const isDark = this.options.theme === 'dark';
        if (config.options) {
            config.options.responsive = true;
            config.options.maintainAspectRatio = false;
            config.options.plugins = config.options.plugins || {};
            config.options.plugins.legend = config.options.plugins.legend || {};
            config.options.plugins.legend.position = 'bottom';
            config.options.plugins.legend.labels = {
                ...config.options.plugins.legend.labels,
                color: isDark ? '#e6edf3' : '#24292f'
            };
        }

        new Chart(canvas, config);

        const vizContainer = contentArea.closest('.viz-container');
        if (vizContainer) {
            this.addUnifiedActionBar(vizContainer, item, chartId, 'chartjs');
        }
    }

    // 7.2.2
    async renderChartJS(item, container, chartId) {
        if (!window.Chart) {
            throw new Error('Chart.js library not loaded');
        }

        const canvas = document.createElement('canvas');
        canvas.id = chartId;

        // Chart.js requires explicit height (doesn't work with 'auto')
        const explicitHeight = (typeof this.options.defaultHeight === 'number')
            ? this.options.defaultHeight
            : 400; // Default to 400px if 'auto' or other string

        // CRITICAL: Set canvas width/height attributes (not just CSS)
        // Chart.js reads these for rendering dimensions
        canvas.width = 800;  // Internal resolution
        canvas.height = explicitHeight;

        canvas.style.cssText = `
            width: 100%;
            height: ${explicitHeight}px;
            position: relative;
            display: block;
            margin: 0 auto;
            box-sizing: border-box;
        `;

        container.appendChild(canvas);

        // Parse config - handle both JSON and JavaScript notation with functions
        let config;
        if (typeof item.content === 'string') {
            try {
                config = JSON.parse(item.content);
            } catch (e) {
                // Fallback to JavaScript eval for function support
                console.warn('ChartJS (legacy): JSON parse failed, using JavaScript eval', e.message);
                try {
                    config = (new Function('return ' + item.content))();
                } catch (evalError) {
                    throw new Error(`Invalid ChartJS config: ${evalError.message}`);
                }
            }
        } else {
            config = item.content;
        }

        const isDark = this.options.theme === 'dark';
        if (config.options) {
            config.options.responsive = true;
            config.options.maintainAspectRatio = false;
            config.options.plugins = config.options.plugins || {};
            config.options.plugins.legend = config.options.plugins.legend || {};
            config.options.plugins.legend.position = 'bottom';
            config.options.plugins.legend.labels = {
                ...config.options.plugins.legend.labels,
                color: isDark ? '#e6edf3' : '#24292f'
            };
        }

        new Chart(canvas, config);

        // NIFIED: Add unified action bar for Chart.js
        this.addUnifiedActionBar(container, item, chartId, 'chartjs');
    }

    // 7.3.1
    // AI-GUIDANCE: Use the centralized markdown renderer here.
    // Do not replace \n with <br> directly – that caused spacing regressions.
    async renderText(item, container) {
        let content = item.content || '';

        // Prefer centralized enhanced renderer
        if (typeof window.renderEnhancedMarkdown === 'function') {
            content = window.renderEnhancedMarkdown(content);
        } else if (typeof window.renderMarkdown === 'function') {
            content = window.renderMarkdown(content);
        } else if (typeof marked !== 'undefined' && marked.parse) {
            // Use marked directly, then apply centralized postprocess if available
            const rawHtml = marked.parse(content);
            content = (window.markdownFormatter && typeof window.markdownFormatter.postprocessHtml === 'function')
                ? window.markdownFormatter.postprocessHtml(rawHtml)
                : rawHtml;
        } else {
            // Last-resort safe fallback: escape + pre-wrap, no <br> injection
            const div = document.createElement('div');
            div.textContent = content;
            content = `<div class="markdown-fallback" style="white-space: pre-wrap;">${div.innerHTML}</div>`;
        }

        const textDiv = document.createElement('div');
        textDiv.innerHTML = content;
        textDiv.style.textAlign = 'left';
        textDiv.style.width = '100%';
        textDiv.style.maxWidth = '100%';
        container.appendChild(textDiv);

        const tables = textDiv.querySelectorAll('table');
        tables.forEach(table => {
            this.styleTable(table);
            this.processSeparatorRows(table);
        });
    }

    // 7.3.2
    styleTable(table) {
        // able-level styles
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';
        table.style.margin = '20px 0';
        table.style.borderRadius = '8px';
        table.style.overflow = 'hidden';
        table.style.textAlign = 'left';
        table.style.marginLeft = '0';
        table.style.marginRight = 'auto';
        table.style.border = '2px solid #6e7681'; // EDIUM GRAY OUTER BORDER

        // EW: Style table headers (th elements)
        const headers = table.querySelectorAll('th');
        headers.forEach(th => {
            th.style.border = '1px solid #484f58'; // IGHTER GRAY BORDERS
            th.style.padding = '12px 16px';
            th.style.backgroundColor = '#161b22';
            th.style.color = '#e6edf3';
            th.style.fontWeight = '600';
            th.style.textAlign = 'left';
            th.style.fontSize = '14px';
            th.style.borderBottom = '2px solid #6e7681'; // EDIUM GRAY BOTTOM BORDER
        });

        // EW: Style table cells (td elements)
        const cells = table.querySelectorAll('td');
        cells.forEach(td => {
            td.style.border = '1px solid #484f58'; // IGHTER GRAY BORDERS
            td.style.padding = '10px 16px';
            td.style.color = '#e6edf3';
            td.style.fontSize = '13px';
            td.style.lineHeight = '1.5';
        });

        // EW: Alternating row colors (stripe pattern)
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach((tr, idx) => {
            if (idx % 2 === 0) {
                tr.style.backgroundColor = '#0d1117'; // Even rows: darker
            } else {
                tr.style.backgroundColor = 'rgba(110, 118, 129, 0.08)'; // Odd rows: subtle gray tint
            }
        });
    }

    // 7.3.3
    processSeparatorRows(table) {
        const rows = table.querySelectorAll('tr');

        // Skip the header row
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.querySelectorAll('td');

            // Check if this is a separator row (all cells contain primarily dashes or separator chars)
            let isSeparatorRow = true;

            cells.forEach(cell => {
                const text = cell.textContent.trim();
                // Check if cell contains primarily separator characters (dashes, underscores, or |)
                if (!text.match(/^[-|_]+$/) && text !== '' && text !== '—') {
                    isSeparatorRow = false;
                }
            });

            if (isSeparatorRow) {
                // Apply separator styling
                row.classList.add('table-separator-row');

                // Replace cells with a single cell spanning all columns
                const columnCount = cells.length;
                row.innerHTML = '';

                const separatorCell = document.createElement('td');
                separatorCell.setAttribute('colspan', columnCount.toString());
                separatorCell.classList.add('table-separator-cell');
                separatorCell.innerHTML = '<div class="table-separator"></div>';
                row.appendChild(separatorCell);
            }
        }
    }

    /**
     * =============================================================================
     * SECTION 8: ACTION BAR & USER INTERACTIONS
     * =============================================================================
     */

    // 8.1.1
    addUnifiedActionBar(container, plotlyData, chartId, chartType = 'plotly') {
        const actionBar = document.createElement('div');
        actionBar.className = 'viz-action-bar';

        actionBar.innerHTML = `
            <!-- CORE BUTTONS -->
            <button class="viz-action-btn" data-action="copy" title="Copy Data" data-function="copyData">
                <i class="fas fa-copy"></i>
            </button>
            
            <button class="viz-action-btn" data-action="view" title="Chart Type" data-function="chartType">
                <i class="fas fa-chart-line"></i>
            </button>
            
            <!-- PLOTLY TOOLS -->
            <button class="viz-action-btn" data-action="plotly" title="Zoom Mode" data-function="plotlyZoom">
                <i class="fas fa-search-plus"></i>
            </button>
            
            <button class="viz-action-btn" data-action="plotly" title="Pan Mode" data-function="plotlyPan">
                <i class="fas fa-hand-paper"></i>
            </button>
            
            <button class="viz-action-btn" data-action="plotly" title="Reset View" data-function="plotlyReset">
                <i class="fas fa-home"></i>
            </button>
            
            <!-- ANALYSIS -->
            <button class="viz-action-btn" data-action="analysis" title="Add Trend Line" data-function="addTrend">
                <i class="fas fa-chart-line"></i>
            </button>
            
            <button class="viz-action-btn" data-action="analysis" title="Statistics" data-function="showStats">
                <i class="fas fa-calculator"></i>
            </button>
            
            <!-- VIEW CONTROLS -->
            <button class="viz-action-btn" data-action="view" title="Fullscreen" data-function="toggleFullscreen">
                <i class="fas fa-expand"></i>
            </button>
            
            <button class="viz-action-btn" data-action="view" title="Toggle Theme" data-function="toggleTheme">
                <i class="fas fa-palette"></i>
            </button>
            
            <!-- SHARING -->
            <button class="viz-action-btn" data-action="share" title="Share as PNG" data-function="shareChart">
                <i class="fas fa-share-alt"></i>
            </button>
            
            <button class="viz-action-btn" data-action="export" title="Print" data-function="printChart">
                <i class="fas fa-print"></i>
            </button>
            
            <!-- EXPORT -->
            <button class="viz-action-btn" data-action="export" title="Export" data-function="exportOptions">
                <i class="fas fa-download"></i>
            </button>
        `;

        container.appendChild(actionBar);
        this.setupUnifiedButtonHandlers(actionBar, container, plotlyData, chartId);

        return actionBar;
    }

    // 8.1.2
    setupUnifiedButtonHandlers(actionBar, container, plotlyData, chartId) {
        const buttons = actionBar.querySelectorAll('.viz-action-btn');
        const chartRecord = chartId ? this.charts.get(chartId) : null;

        const resolveChartId = () => {
            if (chartId) return chartId;
            const plotlyDiv = container.querySelector('.plotly-graph-div');
            return plotlyDiv?.id || container.dataset.viewerChartId || container.dataset.chartId || null;
        };

        const resolvePlotlyData = () => {
            const stored = plotlyData || chartRecord?.plotlyData || null;
            if (stored?.data) {
                return stored;
            }

            if (chartRecord?.item?.__normalizedPlotlyData?.data) {
                return chartRecord.item.__normalizedPlotlyData;
            }

            const domSnapshot = this.getChartDataFromContainer(container);
            if (domSnapshot?.data) {
                return domSnapshot;
            }

            return null;
        };

        buttons.forEach(button => {
            const functionName = button.getAttribute('data-function');

            button.addEventListener('click', (e) => {
                e.stopPropagation();
                const targetChartId = resolveChartId();
                const dataForAction = resolvePlotlyData();

                switch (functionName) {
                    case 'copyData':
                        if (!dataForAction) {
                            this.showNotification(' Chart data not available yet', 'error');
                            return;
                        }
                        this.copyChartData(dataForAction);
                        break;
                    case 'chartType':
                        if (!dataForAction) {
                            this.showNotification(' Chart data not available yet', 'error');
                            return;
                        }
                        this.toggleChartTypeSwitcher(container, dataForAction, targetChartId);
                        break;
                    case 'exportOptions':
                        if (!dataForAction) {
                            this.showNotification(' Chart data not available yet', 'error');
                            return;
                        }
                        this.toggleExportOptions(container, dataForAction, targetChartId);
                        break;
                    case 'plotlyZoom':
                        if (!targetChartId) {
                            this.showNotification(' Chart not ready for interaction', 'error');
                            return;
                        }
                        this.activatePlotlyTool(targetChartId, 'zoom');
                        break;
                    case 'plotlyPan':
                        if (!targetChartId) {
                            this.showNotification(' Chart not ready for interaction', 'error');
                            return;
                        }
                        this.activatePlotlyTool(targetChartId, 'pan');
                        break;
                    case 'plotlyReset':
                        if (!targetChartId) {
                            this.showNotification(' Chart not ready for interaction', 'error');
                            return;
                        }
                        this.resetPlotlyView(targetChartId);
                        break;
                    case 'addTrend':  // EW: Add trend line
                        if (!dataForAction || !targetChartId) {
                            this.showNotification(' Chart data not available yet', 'error');
                            return;
                        }
                        this.addTrendLine(targetChartId, dataForAction);
                        break;
                    case 'showStats':
                        if (!dataForAction) {
                            this.showNotification(' Chart data not available yet', 'error');
                            return;
                        }
                        this.showStatistics(dataForAction);
                        break;
                    case 'toggleFullscreen':
                        this.toggleFullscreen(container);
                        break;
                    case 'toggleTheme':
                        this.handleThemeToggle();
                        break;
                    case 'shareChart':
                        if (!targetChartId) {
                            this.showNotification(' Chart not ready for sharing', 'error');
                            return;
                        }
                        this.shareChartAsPNG(container, dataForAction, targetChartId);  // EW: Share as PNG
                        break;
                    case 'printChart':
                        this.printChart(container);
                        break;
                }
            });
        });
    }

    // 8.2.1
    // 8.2.1 - FIXED: Button-based export instead of dropdown
    toggleExportOptions(container, plotlyData, chartId) {
        const existing = container.querySelector('.export-options-switcher');
        if (existing) {
            existing.remove();
            return;
        }

        const switcher = document.createElement('div');
        switcher.className = 'export-options-switcher';
        switcher.style.cssText = `
            position: absolute;
            top: 10px;
            right: 40px;
            z-index: 1001;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 6px;
            padding: 6px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        `;

        const exportFormats = [
            { value: 'png', label: 'PNG', icon: '🖼️', title: 'Export as PNG Image' },
            { value: 'svg', label: 'SVG', icon: '◻️', title: 'Export as SVG Vector' },
            { value: 'pdf', label: 'PDF', icon: '📄', title: 'Print as PDF' },
            { value: 'csv', label: 'CSV', icon: '📊', title: 'Export Data as CSV' },
            { value: 'json', label: 'JSON', icon: '💾', title: 'Export Data as JSON' }
        ];

        exportFormats.forEach(({ value, label, icon, title }) => {
            const button = document.createElement('button');
            button.className = 'export-format-btn';
            button.value = value;
            button.title = title;
            button.innerHTML = `${icon}<br><span style="font-size: 9px;">${label}</span>`;
            button.style.cssText = `
                background: var(--bg-primary) !important;
                border: 1px solid var(--border-primary) !important;
                border-radius: 4px !important;
                padding: 6px 4px !important;
                font-size: 10px !important;
                cursor: pointer !important;
                color: var(--text-primary) !important;
                width: 45px;
                height: 35px;
                text-align: center;
                transition: all 0.2s ease;
                line-height: 1.1;
                margin: 1px;
            `;

            button.onmouseenter = () => {
                button.style.background = 'var(--bg-tertiary) !important';
                button.style.borderColor = 'var(--accent-blue) !important';
            };
            button.onmouseleave = () => {
                button.style.background = 'var(--bg-primary) !important';
                button.style.borderColor = 'var(--border-primary) !important';
            };

            button.onclick = async (e) => {
                e.preventDefault();
                e.stopPropagation();

                const format = button.value;
                button.disabled = true;
                button.style.opacity = '0.6';
                button.innerHTML = `⏳<br><span style="font-size: 9px;">Wait</span>`;

                try {
                    let chartType = 'unknown';
                    if (container.querySelector('.plotly-graph-div')) {
                        chartType = 'plotly';
                    } else if (container.querySelector('.mermaid')) {
                        chartType = 'mermaid';
                    } else if (container.querySelector('canvas')) {
                        chartType = 'chartjs';
                    }

                    await this.exportChart(container, plotlyData, chartType, format);
                    switcher.remove();
                } catch (error) {
                    console.error(' Export failed:', error);
                    this.showNotification(' Export failed: ' + error.message, 'error');

                    button.disabled = false;
                    button.style.opacity = '1';
                    button.innerHTML = `${icon}<br><span style="font-size: 9px;">${label}</span>`;
                }
            };

            switcher.appendChild(button);
        });

        container.appendChild(switcher);

        const handleClickOutside = (e) => {
            if (!switcher.contains(e.target) && !e.target.closest('[data-function="exportOptions"]')) {
                switcher.remove();
                document.removeEventListener('click', handleClickOutside);
            }
        };

        setTimeout(() => {
            document.addEventListener('click', handleClickOutside);
        }, 100);
    }

    // IXED: Plotly export with better fallback handling
    async exportChart(container, chartData, chartType, format) {
        const timestamp = new Date().toISOString().slice(0, 16).replace(/[:]/g, '-');
        const filename = `chart-${timestamp}`;

        console.log('🔄 Export triggered:', { format, chartType, hasChartData: !!chartData });

        try {
            switch (format) {
                case 'png':
                case 'svg':
                    if (chartType === 'plotly' && window.Plotly) {
                        const plotlyDiv = container.querySelector('.plotly-graph-div');
                        console.log('📊 Plotly export:', { hasPlotlyDiv: !!plotlyDiv, hasPlotly: !!window.Plotly });

                        if (plotlyDiv) {
                            console.log('⬇️ Starting Plotly download...', format);
                            try {
                                // IXED: Better Plotly export options
                                await Plotly.downloadImage(plotlyDiv, {
                                    format: format,
                                    filename: filename,
                                    width: 1200,
                                    height: 800,
                                    scale: 2,
                                    imageDataOnly: false
                                });

                                this.showNotification(`hart exported as ${format.toUpperCase()}`, 'success');
                            } catch (plotlyError) {
                                console.error(' Plotly.downloadImage failed:', plotlyError);

                                // MPROVED FALLBACK: Try alternative methods
                                if (format === 'png') {
                                    try {
                                        console.log('🔄 Trying html2canvas fallback...');
                                        const canvas = await html2canvas(plotlyDiv, {
                                            backgroundColor: null,
                                            scale: 2,
                                            logging: false
                                        });

                                        canvas.toBlob(blob => {
                                            if (blob) {
                                                const url = URL.createObjectURL(blob);
                                                const link = document.createElement('a');
                                                link.href = url;
                                                link.download = `${filename}.png`;
                                                document.body.appendChild(link);
                                                link.click();
                                                document.body.removeChild(link);
                                                URL.revokeObjectURL(url);
                                                this.showNotification('hart exported as PNG (fallback)', 'success');
                                            }
                                        }, 'image/png');
                                    } catch (fallbackError) {
                                        console.error(' html2canvas fallback also failed:', fallbackError);
                                        this.showNotification(' PNG export failed, try SVG or print-to-PDF', 'error');
                                    }
                                } else if (format === 'svg') {
                                    // SVG fallback: Extract from DOM
                                    try {
                                        const svgElement = plotlyDiv.querySelector('svg');
                                        if (svgElement) {
                                            const svgData = new XMLSerializer().serializeToString(svgElement);
                                            this.downloadFile(svgData, `${filename}.svg`, 'image/svg+xml');
                                            this.showNotification('hart exported as SVG (fallback)', 'success');
                                        } else {
                                            this.showNotification(' No SVG found in chart', 'error');
                                        }
                                    } catch (svgError) {
                                        console.error(' SVG fallback failed:', svgError);
                                        this.showNotification(' SVG export failed', 'error');
                                    }
                                }
                            }
                        } else {
                            console.error(' No plotly div found in container');
                            this.showNotification(' Chart not ready for export', 'error');
                        }
                    }

                    // ERMAID EXPORT: Use the new fixed methods
                    else if (chartType === 'mermaid') {
                        if (format === 'svg') {
                            await this.exportMermaidToSVGFixed(container, filename);
                        } else if (format === 'png') {
                            await this.exportMermaidToPNGFixed(container, filename);
                        }
                    }
                    break;

                case 'pdf':
                    window.print();
                    this.showNotification('🖨️ Use browser\'s print-to-PDF option', 'info');
                    break;

                case 'json':
                    const json = JSON.stringify(chartData, null, 2);
                    this.downloadFile(json, `${filename}.json`, 'application/json');
                    this.showNotification('hart data exported as JSON', 'success');
                    break;

                case 'csv':
                    if (chartData.data && chartData.data[0]) {
                        const trace = chartData.data[0];
                        let csv = 'X,Y\n';
                        const length = Math.max(trace.x?.length || 0, trace.y?.length || 0, trace.values?.length || 0);

                        for (let i = 0; i < length; i++) {
                            const x = trace.x?.[i] || trace.labels?.[i] || i;
                            const y = trace.y?.[i] || trace.values?.[i] || '';
                            csv += `${x},${y}\n`;
                        }
                        this.downloadFile(csv, `${filename}.csv`, 'text/csv');
                        this.showNotification('hart data exported as CSV', 'success');
                    }
                    break;
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showNotification(' Export failed: ' + error.message, 'error');
        }
    }

    // 8.2.3
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    // 8.2.4
    async shareChartAsPNG(container, plotlyData, chartId) {
        try {
            const plotlyDiv = document.getElementById(chartId);
            if (!plotlyDiv || !window.Plotly) {
                this.showNotification(' Chart not available for sharing', 'error');
                return;
            }

            // Generate PNG
            const imgData = await Plotly.toImage(plotlyDiv, {
                format: 'png',
                width: 1200,
                height: 800,
                scale: 2
            });

            // Convert to blob
            const response = await fetch(imgData);
            const blob = await response.blob();

            // Try native sharing first
            if (navigator.share && navigator.canShare && navigator.canShare({ files: [new File([blob], 'chart.png', { type: 'image/png' })] })) {
                const file = new File([blob], `chart-${Date.now()}.png`, { type: 'image/png' });
                await navigator.share({
                    title: 'Chart Visualization',
                    text: 'Check out this chart!',
                    files: [file]
                });
                this.showNotification('📤 Chart shared successfully', 'success');
            } else {
                // Fallback: Download the PNG
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `chart-${Date.now()}.png`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
                this.showNotification('📥 Chart PNG downloaded', 'success');
            }

        } catch (error) {
            console.error('Error sharing chart as PNG:', error);
            this.showNotification(' Failed to share chart', 'error');
        }
    }

    // 8.3.1
    toggleFullscreen(container) {
        if (!document.fullscreenElement) {
            container.requestFullscreen().then(() => {
                this.showNotification('🖥️ Entered fullscreen mode', 'info');
            }).catch(err => {
                this.showNotification(' Fullscreen not supported', 'error');
            });
        } else {
            document.exitFullscreen().then(() => {
                this.showNotification('🪟 Exited fullscreen mode', 'info');
            });
        }
    }

    // 8.3.2
    shareChart(container, plotlyData) {
        const shareData = {
            title: 'Chart Visualization',
            text: 'Check out this interactive chart!',
            url: window.location.href
        };

        if (navigator.share) {
            navigator.share(shareData).then(() => {
                this.showNotification('📤 Chart shared successfully', 'success');
            }).catch(err => {
                this.fallbackShare();
            });
        } else {
            this.fallbackShare();
        }
    }

    // 8.3.3
    fallbackShare() {
        navigator.clipboard.writeText(window.location.href).then(() => {
            this.showNotification('🔗 Chart URL copied to clipboard', 'success');
        }).catch(() => {
            this.showNotification(' Unable to share', 'error');
        });
    }

    // 8.3.4
    generateEmbedCode(container, plotlyData) {
        const embedCode = `<iframe src="${window.location.href}" width="800" height="600" frameborder="0"></iframe>`;

        navigator.clipboard.writeText(embedCode).then(() => {
            this.showNotification('📋 Embed code copied to clipboard', 'success');
        }).catch(() => {
            this.showNotification(' Failed to copy embed code', 'error');
        });
    }

    // 8.3.5
    printChart(container) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Chart Print</title>
                    <style>
                        body { margin: 0; padding: 20px; }
                        .viz-container { margin: 0; padding: 0; }
                    </style>
                </head>
                <body>
                    ${container.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
        this.showNotification('🖨️ Print dialog opened', 'info');
    }

    // 8.3.6
    async copyChartData(plotlyData) {
        try {
            if (!plotlyData || !Array.isArray(plotlyData.data)) {
                this.showNotification(' No chart data available to copy', 'error');
                return;
            }
            const dataText = JSON.stringify(plotlyData.data, null, 2);
            await navigator.clipboard.writeText(dataText);
            this.showNotification('hart data copied to clipboard', 'success');
        } catch (err) {
            console.error('Failed to copy:', err);
            this.showNotification(' Failed to copy data', 'error');
        }
    }

    // Additional helper functions for action bar
    setupExportDropdown(actionBar) {
        const dropdown = actionBar.querySelector('.export-dropdown');
        if (!dropdown) return;

        const trigger = dropdown.querySelector('.viz-action-btn');
        const options = dropdown.querySelector('.export-options');

        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('open');
        });

        // Setup export options
        const exportOptions = dropdown.querySelectorAll('.export-option');
        exportOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                const format = option.getAttribute('data-format');
                const container = dropdown.closest('.viz-container');
                const chartData = this.getChartDataFromContainer(container);

                this.exportChart(container, chartData, 'plotly', format);
                dropdown.classList.remove('open');
            });
        });
    }

    getChartDataFromContainer(container) {
        const plotlyDiv = container.querySelector('.plotly-graph-div');
        if (plotlyDiv && plotlyDiv.data) {
            return { data: plotlyDiv.data, layout: plotlyDiv.layout };
        }
        return null;
    }

    /**
     * =============================================================================
     * SECTION 9: THEME & RESPONSIVE SYSTEM
     * =============================================================================
     */

    // 9.1.1
    updateTheme(newTheme) {
        console.log(`🎨 Updating theme to ${newTheme}`);

        const oldTheme = this.options.theme;
        this.options.theme = newTheme;
        this.layoutState.currentTheme = newTheme;

        document.body.setAttribute('data-theme', newTheme);

        if (newTheme === 'dark') {
            this.options.colorScheme = {
                primary: '#1f6feb',
                secondary: '#238636',
                accent: '#a855f7',
                background: '#0d1117',
                text: '#e6edf3'
            };
        } else {
            this.options.colorScheme = {
                primary: '#0969da',
                secondary: '#1a7f37',
                accent: '#8250df',
                background: '#ffffff',
                text: '#24292f'
            };
        }

        // Reinject all styles
        this.injectUnifiedStyles();

        // ORCE UPDATE ALL PLOTLY CHARTS
        this.charts.forEach((chart, chartId) => {
            try {
                if (chart.type === 'plotly' && window.Plotly) {
                    const element = document.getElementById(chartId);
                    if (element && element.data && element.layout) {
                        // EW (Jul 22 2026): Always-white chart canvas (theme
                        // toggle no longer repaints the canvas). See
                        // VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md.
                        //
                        // gridColor darkened from '#e1e4e8' to '#94a3b8' so
                        // lines are clearly visible on the forced white canvas.
                        // See VISUALIZATION_PLOTLY_AXIS_GRID_VISIBILITY_FIX_JULY22_2026.md.
                        const bgColor = '#ffffff';
                        const textColor = '#24292f';
                        const gridColor = '#94a3b8';
                        const axisLineColor = '#7c8694';
                        const zeroLineColor = '#cbd5e1';

                        console.log(`🔄 Updating Plotly chart ${chartId} legend background to: ${bgColor}`);

                        // ORCE LEGEND BACKGROUND UPDATE
                        const updateObj = {
                            paper_bgcolor: bgColor,
                            plot_bgcolor: bgColor,
                            'font.color': textColor,
                            'legend.bgcolor': bgColor, // RITICAL!
                            'legend.bordercolor': gridColor,
                            'legend.font.color': textColor,
                            'xaxis.gridcolor': gridColor,
                            'xaxis.linecolor': axisLineColor,
                            'xaxis.tickcolor': axisLineColor,
                            'xaxis.zerolinecolor': zeroLineColor,
                            'xaxis.tickfont.color': textColor,
                            'yaxis.gridcolor': gridColor,
                            'yaxis.linecolor': axisLineColor,
                            'yaxis.tickcolor': axisLineColor,
                            'yaxis.zerolinecolor': zeroLineColor,
                            'yaxis.tickfont.color': textColor
                        };

                        // EW (Jul 22 2026): If this chart is 3D, also
                        // relayout scene.* axes. (Without this, toggling
                        // theme on a 3D chart leaves scene axes stuck at
                        // the original Plotly defaults.) The trace-type
                        // sniff mirrors applyEnhancedPlotlyTheme's
                        // chartTypes-detection block.
                        const is3D = Array.isArray(element.data) && element.data.some(trace => {
                            const t = (trace?.type || 'scatter').toLowerCase();
                            return ['scatter3d', 'surface', 'mesh3d', 'cone', 'streamtube', 'volume', 'isosurface'].includes(t);
                        });
                        if (is3D) {
                            updateObj['scene.bgcolor'] = bgColor;
                            ['xaxis', 'yaxis', 'zaxis'].forEach(axisKey => {
                                updateObj[`scene.${axisKey}.gridcolor`] = gridColor;
                                updateObj[`scene.${axisKey}.linecolor`] = axisLineColor;
                                updateObj[`scene.${axisKey}.tickcolor`] = axisLineColor;
                                updateObj[`scene.${axisKey}.zerolinecolor`] = zeroLineColor;
                                updateObj[`scene.${axisKey}.tickfont.color`] = textColor;
                            });
                        }

                        Plotly.relayout(chartId, updateObj);
                        console.log('lotly chart updated with new legend background');
                    }
                }
            } catch (err) {
                console.error(`Error updating theme for chart ${chartId}:`, err);
            }
        });

        this.showNotification(`🎨 Theme updated to ${newTheme}`, 'success');
    }

    // 9.1.2
    updateChartTheme(chartId, chart) {
        const element = document.getElementById(chartId);
        if (!element) return;
        // EW (Jul 22 2026): Always-white chart canvas. See
        // VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md.
        //
        // gridColor darkened from '#e1e4e8' to '#94a3b8' so lines read
        // clearly on the forced white canvas. See
        // VISUALIZATION_PLOTLY_AXIS_GRID_VISIBILITY_FIX_JULY22_2026.md.
        const bgColor = '#ffffff';
        const textColor = '#24292f';
        const gridColor = '#94a3b8';
        const axisLineColor = '#7c8694';
        const zeroLineColor = '#cbd5e1';

        try {
            switch (chart.type) {
                case 'plotly':
                    if (window.Plotly && element._fullLayout) {
                        // Update Plotly theme
                        const newLayout = {
                            paper_bgcolor: bgColor,
                            plot_bgcolor: bgColor,
                            font: {
                                color: textColor
                            },
                            xaxis: {
                                gridcolor: gridColor,
                                linecolor: axisLineColor,
                                tickcolor: axisLineColor,
                                zerolinecolor: zeroLineColor,
                                tickfont: { color: textColor }
                            },
                            yaxis: {
                                gridcolor: gridColor,
                                linecolor: axisLineColor,
                                tickcolor: axisLineColor,
                                zerolinecolor: zeroLineColor,
                                tickfont: { color: textColor }
                            },
                            legend: {
                                bgcolor: bgColor,
                                bordercolor: gridColor,
                                font: { color: textColor }
                            }
                        };
                        // EW (Jul 22 2026): For 3D charts, also relayout
                        // the scene.* axes. Mirror of the updateTheme
                        // change so single-chart refresh hits 3D too.
                        if (Array.isArray(element.data) && element.data.some(trace => {
                            const t = (trace?.type || 'scatter').toLowerCase();
                            return ['scatter3d', 'surface', 'mesh3d', 'cone', 'streamtube', 'volume', 'isosurface'].includes(t);
                        })) {
                            newLayout.scene = {
                                bgcolor: bgColor,
                                xaxis: {
                                    gridcolor: gridColor,
                                    linecolor: axisLineColor,
                                    tickcolor: axisLineColor,
                                    zerolinecolor: zeroLineColor,
                                    tickfont: { color: textColor }
                                },
                                yaxis: {
                                    gridcolor: gridColor,
                                    linecolor: axisLineColor,
                                    tickcolor: axisLineColor,
                                    zerolinecolor: zeroLineColor,
                                    tickfont: { color: textColor }
                                },
                                zaxis: {
                                    gridcolor: gridColor,
                                    linecolor: axisLineColor,
                                    tickcolor: axisLineColor,
                                    zerolinecolor: zeroLineColor,
                                    tickfont: { color: textColor }
                                }
                            };
                        }
                        Plotly.relayout(chartId, newLayout);
                    }
                    break;

                case 'mermaid':
                    // Re-render mermaid diagram with new theme.
                    // EW (Jul 22 2026): Always use 'base' (the canvas is
                    // always white; 'dark' would invert Mermaid's internal
                    // palette and produce invisible text). See
                    // VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md.
                    if (window.mermaid && chart.item?.content) {
                        mermaid.initialize({
                            startOnLoad: false,
                            theme: 'base'
                        });

                        mermaid.render(`mermaid-${chartId}-${Date.now()}`, chart.item.content)
                            .then(({ svg }) => {
                                const mermaidDiv = element.querySelector('.mermaid');
                                if (mermaidDiv) mermaidDiv.innerHTML = svg;
                            });
                    }
                    break;

                case 'chartjs':
                    // Update Chart.js theme
                    if (window.Chart) {
                        const chartInstance = Chart.getChart(chartId);
                        if (chartInstance) {
                            chartInstance.options.color = textColor;
                            chartInstance.options.scales.x.grid.color = gridColor;
                            chartInstance.options.scales.y.grid.color = gridColor;
                            chartInstance.update();
                        }
                    }
                    break;

                case 'google':
                    // Re-render Google chart with new theme
                    if (window.google && window.google.visualization && chart.item) {
                        // We need to completely re-render the chart
                        this.renderGoogleChart(chart.item, chart.container, chartId);
                    }
                    break;
            }
        } catch (error) {
            console.error(`Error updating theme for ${chart.type} chart:`, error);
        }
    }

    // 9.1.3
    handleThemeToggle() {
        // Use your existing toggleTheme function
        if (typeof toggleTheme === 'function') {
            toggleTheme();
        } else {
            // Fallback theme toggle
            const currentTheme = document.body.getAttribute('data-theme') || 'dark';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', newTheme);
            this.updateTheme(newTheme);
        }
    }

    // 9.2.1
    handleBreakpointChange(newBreakpoint) {
        console.log(`📱 Breakpoint changed to: ${newBreakpoint}`);

        this.charts.forEach((chart, chartId) => {
            const element = document.getElementById(chartId);
            if (element) {
                this.updateVisualizationForBreakpoint(element, newBreakpoint);
            }
        });
    }

    // 9.2.2
    updateVisualizationForBreakpoint(element, breakpoint) {
        element.classList.remove('breakpoint-mobile', 'breakpoint-tablet', 'breakpoint-desktop');
        element.classList.add(`breakpoint-${breakpoint}`);
    }

    // 9.2.3
    handleWindowResize() {
        console.log('[VIZ] Skipping window resize - Plotly charts use responsive config');
        //  DISABLED - Plotly resize breaks properly-rendered charts
        // this.charts.forEach((chart, chartId) => {
        //     if (chart.type === 'plotly' && window.Plotly) {
        //         try {
        //             const plotlyDiv = document.getElementById(chartId);
        //             if (plotlyDiv && plotlyDiv._fullLayout) {
        //                 window.Plotly.Plots.resize(plotlyDiv);
        //             }
        //         } catch (e) {
        //             console.warn('Warning resizing Plotly chart:', e);
        //         }
        //     }
        // });
    }

    // 9.2.4
    handleSimpleResize(entries) {
        entries.forEach((entry) => {
            const container = entry.target;
            if (container.classList.contains('viz-container')) {
                this.updateSingleContainerSize(container);
            }
        });
    }

    // 9.2.5
    updateSingleContainerSize(container) {
        console.log('[VIZ] Skipping container resize - Plotly charts use responsive config');
        //  DISABLED - Plotly resize breaks properly-rendered charts
        // const plotlyDiv = container.querySelector('.plotly-graph-div');
        // if (plotlyDiv && window.Plotly && plotlyDiv._fullLayout) {
        //     try {
        //         window.Plotly.Plots.resize(plotlyDiv);
        //     } catch (e) {
        //         console.warn('Warning resizing Plotly chart:', e);
        //     }
        // }
    }

    async rehydrateViewerContent(rootElement, options = {}) {
        const scope = rootElement || document;
        const containers = Array.from(scope.querySelectorAll?.('.viz-container') || []);

        // XTRACT FORCED DIMENSIONS FOR VIEWER REHYDRATION
        const forceWidth = options.forceWidth || null;
        const forceHeight = options.forceHeight || null;

        for (const container of containers) {
            const plotlyDiv = container.querySelector('.plotly-graph-div');
            const inferredId = container.dataset.sourceChartId
                || container.dataset.chartId
                || plotlyDiv?.dataset.chartId
                || plotlyDiv?.getAttribute('data-chart-id')
                || plotlyDiv?.id;

            if (!inferredId) continue;

            const record = this.charts.get(inferredId);
            if (!record) continue;

            const alreadyFrom = container.dataset.viewerChartRenderedFrom;
            const existingViewerId = container.dataset.viewerChartId;

            if (alreadyFrom === inferredId && existingViewerId) {
                if (window.Plotly) {
                    const viewerDiv = document.getElementById(existingViewerId);
                    if (viewerDiv && viewerDiv._fullLayout) {
                        try {
                            //  RESIZE DISABLED - Was destroying charts in viewer
                            // Plotly already renders with responsive config, no resize needed
                            console.log('IEWER: Plotly chart found, skipping resize (uses responsive config)');

                            // NLY relayout if forced dimensions requested
                            if (forceWidth || forceHeight) {
                                const update = {};
                                if (forceWidth) update.width = forceWidth;
                                if (forceHeight) update.height = forceHeight;
                                await window.Plotly.relayout(viewerDiv, update);
                            }
                        } catch (error) {
                            console.warn('Viewer resize warning:', error);
                        }
                    }
                }
                continue;
            }

            const newChartId = existingViewerId || `${inferredId}__viewer_${Date.now()}_${Math.floor(Math.random() * 1000)}`;

            // ASS FORCED DIMENSIONS TO CLONE FUNCTION
            await this.cloneVisualizationForViewer(inferredId, container, newChartId, forceWidth, forceHeight);
        }

        this.reattachActionBars(scope);

        if (typeof window.ensurePlotlyResponsive === 'function') {
            window.ensurePlotlyResponsive(scope);
        }
    }

    async cloneVisualizationForViewer(sourceChartId, targetContainer, targetChartId, forceWidth = null, forceHeight = null) {
        if (!targetContainer) return;

        const record = this.charts.get(sourceChartId);
        if (!record) {
            console.warn('No stored visualization record for', sourceChartId);
            return;
        }

        const contentArea = targetContainer.querySelector('.viz-content-area');
        if (!contentArea) {
            console.warn('Viewer container missing viz-content-area');
            return;
        }

        const resolvedChartId = targetChartId || `${sourceChartId}__viewer_${Date.now()}`;

        contentArea.innerHTML = '';
        this.attachResizeHandle(contentArea);

        const viewerItem = { type: record.type };

        if (record.type === 'plotly') {
            if (!record.plotlyData) {
                console.warn('Missing Plotly snapshot for viewer clone:', sourceChartId);
                return;
            }

            // IX: Deep clone Plotly data but preserve reactivity
            const viewerPlotlyData = JSON.parse(JSON.stringify(record.plotlyData));

            // ORCE LARGER DIMENSIONS FOR VIEWER PLOTLY CHARTS
            // Use passed dimensions or defaults (wider and taller for viewer)
            const viewerWidth = forceWidth || 1400;   // ncreased from 1200 to 1400
            const viewerHeight = forceHeight || 700;  // ncreased from 600 to 700

            // IX: Set dimensions but ENABLE autosize for responsive behavior
            viewerPlotlyData.layout.width = viewerWidth;
            viewerPlotlyData.layout.height = viewerHeight;

            // RITICAL FIX: Enable autosize for responsive resizing in viewer panel
            viewerPlotlyData.layout.autosize = true;  // FIXED: Was false, now true for responsiveness

            // nsure responsive mode is enabled
            viewerPlotlyData.config = viewerPlotlyData.config || {};
            viewerPlotlyData.config.responsive = true;

            viewerItem.data = viewerPlotlyData.data;
            viewerItem.layout = viewerPlotlyData.layout;
            viewerItem.__normalizedPlotlyData = viewerPlotlyData;
        } else if (record.type === 'mermaid') {
            viewerItem.content = record.item?.content || '';
        } else if (record.type === 'chartjs') {
            viewerItem.content = record.item?.content;
            viewerItem.data = record.item?.data;
        } else {
            viewerItem.content = record.item?.content || '';
        }

        targetContainer.dataset.sourceChartId = sourceChartId;
        targetContainer.dataset.viewerChartId = resolvedChartId;
        targetContainer.dataset.viewerChartRenderedFrom = sourceChartId;

        await this.renderVisualizationDirectly(viewerItem, targetContainer, resolvedChartId);
    }

    reattachActionBars(rootElement) {
        const scope = rootElement || document;
        const actionBars = Array.from(scope.querySelectorAll?.('.viz-action-bar') || []);

        actionBars.forEach(actionBar => {
            const container = actionBar.closest('.viz-container');
            if (!container) return;

            const plotlyDiv = container.querySelector('.plotly-graph-div');
            const chartId = plotlyDiv?.id
                || container.dataset.viewerChartId
                || container.dataset.chartId
                || plotlyDiv?.dataset.chartId;

            const record = chartId ? this.charts.get(chartId) : null;
            const clonedBar = actionBar.cloneNode(true);
            actionBar.replaceWith(clonedBar);

            let plotlySnapshot = null;
            if (record?.plotlyData) {
                plotlySnapshot = JSON.parse(JSON.stringify(record.plotlyData));
            }

            this.setupUnifiedButtonHandlers(clonedBar, container, plotlySnapshot, chartId);
        });
    }

    /**
     * =============================================================================
     * SECTION 10: UTILITIES & HELPERS
     * =============================================================================
     */

    // 10.1.1
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const colors = {
            success: 'var(--accent-green)',
            error: 'var(--accent-red)',
            info: 'var(--accent-blue)',
            warning: 'var(--accent-orange)'
        };

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 16px;
            background: ${colors[type]};
            color: white;
            border-radius: 6px;
            z-index: 10001;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            max-width: 300px;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // 10.2.1
    showError(container, message) {
        container.innerHTML = `
            <div class="viz-error">
                <h3>⚠️ Visualization Error</h3>
                <p>${message}</p>
            </div>
        `;
    }

    // 10.2.2
    showErrorDirectly(contentArea, message) {
        // CRITICAL: Container validation (doesn't need to be in DOM yet)
        if (!contentArea) {
            console.error('❌ Cannot show error - content area is null:', message);
            return;
        }
        
        // Log DOM attachment status but don't block error display
        if (!document.contains(contentArea)) {
            console.warn('⚠️ Showing error in container not yet in DOM (will be visible after message render):', message);
        }

        contentArea.innerHTML = `
            <div class="viz-error" style="
                text-align: center;
                padding: 40px 20px;
                color: var(--accent-red);
                border: 1px dashed var(--accent-red);
                border-radius: 8px;
                margin: 20px;
            ">
                <h3 style="margin: 0 0 10px 0;">⚠️ Visualization Error</h3>
                <p style="margin: 0; font-size: 14px;">${message}</p>
            </div>
        `;
    }

    // EW: Fullscreen Mermaid viewer with zoom and pan
    async openMermaidFullscreen(container, diagramContent, chartId) {
        console.log('🖥️ Opening Mermaid fullscreen view...');

        // Get the current SVG element
        let currentSvg = container.querySelector('svg');
        // EW (Jul 24 2026): Track a hidden holder for a fallback-rendered
        // SVG so we can clean it up immediately after cloning.  See the
        // fallback branch below for the race that triggers it.
        let parkedHolder = null;

        // EW (Jul 24 2026): Defensive fallback render.  When the inline
        // SVG is missing but the action bar is visible (visible
        // copy/zoom/theme buttons on an empty body), the underlying
        // .mermaid div was removed by a concurrent re-render's
        // contentArea cleanup (renderMermaidDirectly L5063) while the
        // outer .viz-container -- where the action bar lives --
        // survived.  The diagram source is preserved on vizContainer
        // via data-original-content (set in renderMermaidDirectly at
        // L5123), so re-render synchronously into an off-screen staging
        // div, park the result in a hidden holder on the container, and
        // continue with the existing overlay-creation flow.  The hidden
        // holder is removed immediately after the SVG is cloned below.
        if (!currentSvg) {
            const source = (container.getAttribute && container.getAttribute('data-original-content'))
                || diagramContent || '';
            if (!source || typeof window === 'undefined' || !window.mermaid || typeof window.mermaid.render !== 'function') {
                this.showNotification(' No diagram found to display', 'error');
                return;
            }
            const staging = document.createElement('div');
            staging.style.cssText = 'position:absolute;left:-99999px;top:0;visibility:hidden;width:1px;height:1px;overflow:hidden;pointer-events:none;';
            const fallbackId = `fs-fallback-${chartId || Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
            document.body.appendChild(staging);
            try {
                const svgString = await window.mermaid.render(fallbackId, source);
                if (!svgString) {
                    this.showNotification(' No diagram found to display', 'error');
                    return;
                }
                staging.innerHTML = svgString;
                const stagedSvg = staging.querySelector('svg');
                if (!stagedSvg) {
                    this.showNotification(' No diagram found to display', 'error');
                    return;
                }
                parkedHolder = document.createElement('div');
                parkedHolder.style.cssText = 'display:none';
                parkedHolder.appendChild(stagedSvg);
                container.appendChild(parkedHolder);
                currentSvg = stagedSvg;
            } catch (err) {
                console.error('🖥️ Mermaid fallback render failed:', err);
                this.showNotification(' No diagram found to display', 'error');
                return;
            } finally {
                if (staging.parentNode) staging.remove();
            }
        }

        // Create fullscreen overlay
        const overlay = document.createElement('div');
        overlay.className = 'mermaid-fullscreen-overlay';

        // Create fullscreen container
        const fullscreenContainer = document.createElement('div');
        fullscreenContainer.className = 'mermaid-fullscreen-container viz-container';
        // Ensure handlers treat fullscreen as a proper viz-container target
        try {
            const originalContent = container.getAttribute('data-original-content') || diagramContent || '';
            if (originalContent) fullscreenContainer.setAttribute('data-original-content', originalContent);
            const originalFont = container.getAttribute('data-font-size') || '14';
            fullscreenContainer.setAttribute('data-font-size', originalFont);
            const colorTheme = container.getAttribute('data-color-theme');
            if (colorTheme) fullscreenContainer.setAttribute('data-color-theme', colorTheme);
        } catch (e) { /* noop */ }

        // Create header with controls
        const header = document.createElement('div');
        header.className = 'mermaid-fullscreen-header';

        const title = document.createElement('h3');
        title.className = 'mermaid-fullscreen-title';
        title.textContent = 'Mermaid Diagram - Fullscreen View';

        const controls = document.createElement('div');
        controls.className = 'mermaid-fullscreen-controls';

        // Use viz-action-btn styling and Font Awesome icons
        controls.innerHTML = `
        <button class="viz-action-btn" id="zoom-out" title="Zoom Out">
            <i class="fas fa-search-minus"></i>
        </button>
        <button class="viz-action-btn" id="zoom-reset" title="Reset Zoom">
            <i class="fas fa-bullseye"></i>
        </button>
        <button class="viz-action-btn" id="zoom-in" title="Zoom In">
            <i class="fas fa-search-plus"></i>
        </button>
        <button class="viz-action-btn" id="fit-screen" title="Fit to Screen">
            <i class="fas fa-search-plus"></i>
        </button>
        <button class="viz-action-btn" id="close-fullscreen" title="Close">
            <i class="far fa-window-close"></i>
        </button>
    `;

        header.appendChild(title);
        header.appendChild(controls);

        // FIXED: Add Mermaid action controls to fullscreen
        const fullscreenActionBar = document.createElement('div');
        fullscreenActionBar.className = 'viz-action-bar';
        fullscreenActionBar.style.cssText = `
        position: relative;
        top: 0;
        left: 0;
        transform: none;
        margin: 10px 0;
        opacity: 1;
        background: rgba(255, 255, 255, 0.1);
    `;

        fullscreenActionBar.innerHTML = `
        <button class="viz-action-btn" data-action="copy" title="Copy Code" data-function="copyMermaidCode">
            <i class="fas fa-copy">⧉</i>
        </button>
        
        <button class="viz-action-btn font-control" data-action="view" title="Smaller Font" data-function="fontSizeDown">
            <i class="fas fa-minus">A-</i>
        </button>
        
        <button class="viz-action-btn font-control" data-action="view" title="Font Size Menu" data-function="fontSizeMenu">
            <i class="fas fa-text-height">Aa</i>
        </button>
        
        <button class="viz-action-btn font-control" data-action="view" title="Larger Font" data-function="fontSizeUp">
            <i class="fas fa-plus">A+</i>
        </button>
        
        <button class="viz-action-btn" data-action="view" title="Toggle Direction" data-function="toggleDirection">
            <i class="fas fa-arrows-alt-h">↔</i>
        </button>
        
        <button class="viz-action-btn" data-action="view" title="Color Themes" data-function="colorThemes">
            <i class="fas fa-palette">🎨</i>
        </button>
        
        <button class="viz-action-btn" data-action="export" title="Export" data-function="exportOptions">
            <i class="fas fa-download">⬇</i>
        </button>
    `;

        header.appendChild(fullscreenActionBar);

        // Create content area
        const content = document.createElement('div');
        content.className = 'mermaid-fullscreen-content';

        const viewport = document.createElement('div');
        viewport.className = 'mermaid-fullscreen-viewport';

        // Wrap fullscreen diagram in a viz-content-area so existing logic finds it
        const vizContentArea = document.createElement('div');
        vizContentArea.className = 'viz-content-area';

        const diagramContainer = document.createElement('div');
        // Do NOT add 'mermaid' class here to avoid automatic re-init; we clone the existing SVG
        diagramContainer.className = 'mermaid-fullscreen-diagram';

        // Clone and prepare SVG
        const clonedSvg = currentSvg.cloneNode(true);
        // EW (Jul 24 2026): If the fallback branch parked a hidden SVG
        // holder, remove it now that the clone owns the content.  Keeps
        // subsequent re-render paths (reRenderFullscreenIfOpen, font/theme
        // handlers) from picking up a stale SVG instead of the live one.
        if (parkedHolder && parkedHolder.parentElement === container) {
            parkedHolder.remove();
        }

        // Get the actual rendered dimensions of the original SVG
        const originalRect = currentSvg.getBoundingClientRect();
        console.log('📐 Original SVG rendered dimensions:', originalRect);

        // Get bounding box safely
        let bbox;
        try {
            bbox = currentSvg.getBBox();
            console.log('📦 SVG bounding box:', bbox);
        } catch (e) {
            console.warn('Could not get SVG bounding box:', e);
            bbox = null;
        }

        // SIMPLIFIED: Let SVG scale naturally to fill fullscreen container
        // Configure the cloned SVG with responsive scaling

        // Set viewBox - prefer bbox for proper content bounds
        if (bbox && bbox.width > 0 && bbox.height > 0) {
            clonedSvg.setAttribute('viewBox', `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`);
            console.log('🎯 Using bbox for viewBox:', `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`);
        } else {
            // Fallback: use original SVG viewBox or create from current dimensions
            const originalViewBox = currentSvg.getAttribute('viewBox');
            if (originalViewBox) {
                clonedSvg.setAttribute('viewBox', originalViewBox);
                console.log('🎯 Using original viewBox:', originalViewBox);
            } else {
                // Last resort: create viewBox from original dimensions
                const origWidth = currentSvg.getAttribute('width') || '800';
                const origHeight = currentSvg.getAttribute('height') || '600';
                const vbWidth = parseFloat(origWidth.toString().replace(/[^\d.]/g, '')) || 800;
                const vbHeight = parseFloat(origHeight.toString().replace(/[^\d.]/g, '')) || 600;
                clonedSvg.setAttribute('viewBox', `0 0 ${vbWidth} ${vbHeight}`);
                console.log('🎯 Created viewBox from dimensions:', `0 0 ${vbWidth} ${vbHeight}`);
            }
        }

        // Apply CSS for proper scaling
        clonedSvg.style.cssText = `
        width: 100%;
        height: 100%;
        display: block;
        margin: auto;
        max-width: 100%;
        max-height: 100%;
    `;

        // Copy styles
        const originalElements = currentSvg.querySelectorAll('*');
        const clonedElements = clonedSvg.querySelectorAll('*');

        originalElements.forEach((originalEl, index) => {
            const clonedEl = clonedElements[index];
            if (!clonedEl) return;

            const computedStyle = window.getComputedStyle(originalEl);
            const importantProps = [
                'fill', 'stroke', 'stroke-width', 'font-family', 'font-size', 'font-weight'
            ];

            const styleProps = [];
            importantProps.forEach(prop => {
                const value = computedStyle.getPropertyValue(prop);
                if (value && value !== 'none' && value !== '') {
                    styleProps.push(`${prop}: ${value}`);
                }
            });

            if (styleProps.length > 0) {
                const originalStyle = clonedEl.getAttribute('style') || '';
                clonedEl.setAttribute('style', originalStyle + ';' + styleProps.join(';'));
            }

            Array.from(originalEl.attributes).forEach(attr => {
                if (attr.name !== 'style') {
                    clonedEl.setAttribute(attr.name, attr.value);
                }
            });
        });

        // SVG styling already applied above - width/height 100% with proper viewBox
        console.log('✅ SVG configured for responsive fullscreen scaling');

        diagramContainer.appendChild(clonedSvg);
        vizContentArea.appendChild(diagramContainer);
        viewport.appendChild(vizContentArea);

        // Ensure all containers are properly sized and visible
        diagramContainer.style.cssText = `
        display: block !important;
        visibility: visible !important;
        width: fit-content !important;
        height: fit-content !important;
        position: relative !important;
    `;

        vizContentArea.style.cssText = `
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        height: 100% !important;
    `;

        viewport.style.cssText = `
        position: relative !important;
        width: 100% !important;
        height: 100% !important;
        overflow: hidden !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        cursor: grab !important;
    `;
        content.appendChild(viewport);

        // Add zoom indicator
        const zoomIndicator = document.createElement('div');
        zoomIndicator.className = 'mermaid-zoom-indicator';
        zoomIndicator.textContent = '100%';
        content.appendChild(zoomIndicator);

        // Assemble fullscreen container
        fullscreenContainer.appendChild(header);
        fullscreenContainer.appendChild(content);
        overlay.appendChild(fullscreenContainer);

        // Add to DOM
        document.body.appendChild(overlay);

        // DEBUG: Log actual DOM dimensions after adding to document
        setTimeout(() => {
            const overlayRect = overlay.getBoundingClientRect();
            const containerRect = fullscreenContainer.getBoundingClientRect();
            const viewportRect = viewport.getBoundingClientRect();
            const svgRect = clonedSvg.getBoundingClientRect();

            console.log('🔍 DEBUG - Fullscreen DOM dimensions:', {
                overlay: { width: overlayRect.width, height: overlayRect.height },
                container: { width: containerRect.width, height: containerRect.height },
                viewport: { width: viewportRect.width, height: viewportRect.height },
                svg: { width: svgRect.width, height: svgRect.height },
                svgAttributes: {
                    width: clonedSvg.getAttribute('width'),
                    height: clonedSvg.getAttribute('height'),
                    viewBox: clonedSvg.getAttribute('viewBox')
                }
            });
        }, 100);

        // FIXED: Setup action bar handlers for fullscreen
        this.setupMermaidButtonHandlers(fullscreenActionBar, fullscreenContainer, diagramContent, chartId);

        // Initialize zoom controls - fit-to-screen logic will determine optimal scale
        setTimeout(() => {
            this.initFullscreenControls(viewport, diagramContainer, clonedSvg, zoomIndicator, overlay, 0.8);
        }, 300); this.showNotification('🖥️ Fullscreen view opened with full controls', 'success');
    }

    /**
     * EW: Re-render fullscreen view if it's currently open
     */
    reRenderFullscreenIfOpen(originalContainer, diagramContent, chartId) {
        const fullscreenOverlay = document.querySelector('.mermaid-fullscreen-overlay');
        if (!fullscreenOverlay) {
            return; // Fullscreen not open
        }

        console.log('🔄 Re-rendering fullscreen view with updated settings...');

        // Get the updated SVG from the original container
        const updatedSvg = originalContainer.querySelector('svg');
        if (!updatedSvg) {
            console.warn('No updated SVG found in original container');
            return;
        }

        // Find the fullscreen SVG container
        const fullscreenSvgContainer = fullscreenOverlay.querySelector('.mermaid-fullscreen-diagram');
        if (!fullscreenSvgContainer) {
            console.warn('No fullscreen SVG container found');
            return;
        }

        // Clone the updated SVG with our improved sizing logic
        const clonedSvg = updatedSvg.cloneNode(true);

        // Apply the same dimension correction logic as in openMermaidFullscreen
        const originalRect = updatedSvg.getBoundingClientRect();
        let bbox;
        try {
            bbox = updatedSvg.getBBox();
        } catch (e) {
            bbox = null;
        }

        let finalWidth, finalHeight;

        if (originalRect.width > 0 && originalRect.height > 0) {
            finalWidth = Math.max(originalRect.width, 200);
            finalHeight = Math.max(originalRect.height, 150);
        } else {
            let attrWidth = parseFloat(updatedSvg.getAttribute('width')?.replace(/[^\d.]/g, '')) || 800;
            let attrHeight = parseFloat(updatedSvg.getAttribute('height')?.replace(/[^\d.]/g, '')) || 600;

            finalWidth = Math.max(attrWidth, 200);
            finalHeight = Math.max(finalHeight, 150);
        }

        // Fix extreme aspect ratios
        if (bbox && bbox.width > 0 && bbox.height > 0) {
            const currentRatio = finalWidth / finalHeight;
            const viewBoxRatio = bbox.width / bbox.height;

            if (currentRatio < 0.2 || currentRatio > 5) {
                console.log('🔧 Fixing aspect ratio in fullscreen re-render');
                const targetSize = 700;
                if (viewBoxRatio >= 1) {
                    finalWidth = targetSize;
                    finalHeight = targetSize / viewBoxRatio;
                } else {
                    finalHeight = targetSize;
                    finalWidth = targetSize * viewBoxRatio;
                }

                finalWidth = Math.max(finalWidth, 300);
                finalHeight = Math.max(finalHeight, 200);
            }
        }

        // Configure the updated SVG
        clonedSvg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
        clonedSvg.setAttribute('width', finalWidth);
        clonedSvg.setAttribute('height', finalHeight);
        clonedSvg.setAttribute('preserveAspectRatio', 'xMidYMid meet');

        if (bbox && bbox.width > 0 && bbox.height > 0) {
            clonedSvg.setAttribute('viewBox', `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`);
        } else {
            clonedSvg.setAttribute('viewBox', `0 0 ${finalWidth} ${finalHeight}`);
        }

        // Apply styling
        clonedSvg.style.cssText = `
            max-width: none !important;
            max-height: none !important;
            width: ${finalWidth}px !important;
            height: ${finalHeight}px !important;
            display: block !important;
            visibility: visible !important;
            background: white !important;
            border: 1px solid #ddd !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        `;

        // Replace the old SVG with the new one
        fullscreenSvgContainer.innerHTML = '';
        fullscreenSvgContainer.appendChild(clonedSvg);

        // Trigger a re-fit to ensure proper sizing
        // EW (Jul 22 2026): Double-rAF instead of setTimeout(100). Two frames
        // (~32ms at 60fps) is enough for the SVG insertion + style flush to
        // settle before we click #fit-screen, matching the single-fit pattern
        // in initFullscreenControls. The previous 100ms timeout was a magic
        // number that occasionally raced against slower style flushes.
        const fitButton = fullscreenOverlay.querySelector('#fit-screen');
        if (fitButton) {
            requestAnimationFrame(() => requestAnimationFrame(() => fitButton.click()));
        }

        console.log('ullscreen view re-rendered successfully');
    }

    // EW: Initialize zoom and pan controls for fullscreen view
    initFullscreenControls(viewport, diagramContainer, svg, zoomIndicator, overlay, initialScale = 0.8) {
        console.log('🎮 Initializing fullscreen controls...', {
            viewport: !!viewport,
            diagramContainer: !!diagramContainer,
            svg: !!svg,
            initialScale: initialScale,
            svgDimensions: svg ? {
                width: svg.getAttribute('width'),
                height: svg.getAttribute('height')
            } : null
        });

        let scale = initialScale; // Use the passed initial scale
        let translateX = 0;
        let translateY = 0;
        let isDragging = false;
        let lastX = 0;
        let lastY = 0;

        const updateTransform = () => {
            diagramContainer.style.transform = `translate(-50%, -50%) translate(${translateX}px, ${translateY}px) scale(${scale})`;
            zoomIndicator.textContent = `${Math.round(scale * 100)}%`;
        };

        // Apply initial transform immediately
        updateTransform();

        const fitToScreen = () => {
            // Get viewport dimensions first
            const viewportRect = viewport.getBoundingClientRect();

            if (viewportRect.width <= 0 || viewportRect.height <= 0) {
                console.warn('⚠️ Viewport not ready, using default scale');
                scale = 0.8; // Start at 80% to ensure visibility
                translateX = 0;
                translateY = 0;
                updateTransform();
                return;
            }

            // Get SVG dimensions - prefer the actual final dimensions we set
            let svgWidth = parseFloat(svg.getAttribute('width'));
            let svgHeight = parseFloat(svg.getAttribute('height'));

            // If attributes are not available, try getBoundingClientRect as fallback
            if (!svgWidth || !svgHeight || svgWidth <= 0 || svgHeight <= 0) {
                const svgRect = svg.getBoundingClientRect();
                if (svgRect.width > 0 && svgRect.height > 0) {
                    svgWidth = svgRect.width;
                    svgHeight = svgRect.height;
                } else {
                    // Final fallback to viewport-relative size
                    svgWidth = viewportRect.width * 0.6;
                    svgHeight = viewportRect.height * 0.6;
                }
            }

            console.log('🎯 Fitting to screen:', {
                svgDimensions: { width: svgWidth, height: svgHeight },
                viewportDimensions: { width: viewportRect.width, height: viewportRect.height }
            });

            if (svgWidth > 0 && svgHeight > 0) {
                // Calculate scale to fit with some padding (85% of viewport)
                const scaleX = (viewportRect.width * 0.85) / svgWidth;
                const scaleY = (viewportRect.height * 0.85) / svgHeight;

                // Use the smaller scale to ensure it fits in both dimensions
                const newScale = Math.min(scaleX, scaleY);

                // Ensure reasonable scale limits - minimum 0.3x for very large diagrams, maximum 5x for very small ones
                scale = Math.min(Math.max(newScale, 0.3), 5);

                // Special handling for very small scales - boost them to ensure visibility
                if (scale < 0.8 && (svgWidth < 400 || svgHeight < 300)) {
                    scale = Math.min(scale * 2, 2.0); // Double the scale for small SVGs, max 2x
                    console.log('🔍 Boosting scale for small diagram:', scale);
                }
                translateX = 0;
                translateY = 0;
                updateTransform();

                console.log('itted to screen with scale:', scale, 'from scales:', { scaleX, scaleY });
            } else {
                console.warn('⚠️ Could not determine SVG dimensions, using default scale');
                scale = 0.8; // Default to 80% if we can't determine dimensions
                translateX = 0;
                translateY = 0;
                updateTransform();
            }
        };

        // Control button handlers
        document.getElementById('zoom-in').onclick = () => {
            scale = Math.min(scale * 1.25, 5);
            updateTransform();
        };

        document.getElementById('zoom-out').onclick = () => {
            scale = Math.max(scale / 1.25, 0.1);
            updateTransform();
        };

        document.getElementById('zoom-reset').onclick = () => {
            scale = 1;
            translateX = 0;
            translateY = 0;
            updateTransform();
        };

        document.getElementById('fit-screen').onclick = fitToScreen;

        const closeFullscreen = () => {
            try {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
                document.removeEventListener('keydown', handleKeyDown);
                // EW (Jul 22 2026): Disconnect the fullscreen ResizeObserver
                // (added in initFullscreenControls) so it doesn't leak
                // across open/close cycles. Without this, every fullscreen
                // open leaves an observer alive that pins the closed overlay
                // element in memory.
                if (this._fullscreenResizeObserver) {
                    this._fullscreenResizeObserver.disconnect();
                    this._fullscreenResizeObserver = null;
                }
                if (this._fullscreenResizeRaf) {
                    cancelAnimationFrame(this._fullscreenResizeRaf);
                    this._fullscreenResizeRaf = null;
                }
            } catch (_) { }
            overlay.remove();
        };
        document.getElementById('close-fullscreen').onclick = closeFullscreen;

        // Mouse wheel zoom
        viewport.addEventListener('wheel', (e) => {
            e.preventDefault();

            const rect = viewport.getBoundingClientRect();
            const mouseX = e.clientX - rect.left - rect.width / 2;
            const mouseY = e.clientY - rect.top - rect.height / 2;

            const delta = e.deltaY < 0 ? 1.1 : 0.9;
            const newScale = Math.min(Math.max(scale * delta, 0.1), 5);

            // Zoom towards mouse position
            const scaleDiff = newScale - scale;
            translateX -= (mouseX / scale) * scaleDiff;
            translateY -= (mouseY / scale) * scaleDiff;

            scale = newScale;
            updateTransform();
        });

        // Mouse drag pan
        const onMouseMove = (e) => {
            if (!isDragging) return;
            const deltaX = e.clientX - lastX;
            const deltaY = e.clientY - lastY;
            translateX += deltaX;
            translateY += deltaY;
            lastX = e.clientX;
            lastY = e.clientY;
            updateTransform();
        };
        const onMouseUp = () => {
            isDragging = false;
            viewport.style.cursor = 'grab';
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };
        viewport.addEventListener('mousedown', (e) => {
            isDragging = true;
            lastX = e.clientX;
            lastY = e.clientY;
            viewport.style.cursor = 'grabbing';
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });

        // Close on ESC key
        const handleKeyDown = (e) => {
            if (e.key === 'Escape') {
                closeFullscreen();
            }
        };
        document.addEventListener('keydown', handleKeyDown);

        // Close on overlay click (but not on content)
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeFullscreen();
            }
        });

        // EW (Jul 22 2026): Single-fit, ResizeObserver-driven. The previous
        // 3-setTimeout chain produced a visible race in the console log
        // (4.458 -> 0.803 -> 4.458) because the viewport was transiently
        // narrower mid-CSS-layout during the middle fit, and there was no
        // live resize listener so a window resize required a manual click
        // on #fit-screen. Now: wait one frame for layout, fit exactly once,
        // then keep fitting on real size changes only.
        const initialFit = () => {
            const r = viewport.getBoundingClientRect();
            if (r.width <= 0 || r.height <= 0) {
                requestAnimationFrame(initialFit);  // viewport still settling
                return;
            }
            fitToScreen();
        };
        requestAnimationFrame(initialFit);

        // Live resize support — the overlay previously had no resize listener.
        if (typeof ResizeObserver !== 'undefined') {
            const ro = new ResizeObserver(() => {
                if (this._fullscreenResizeRaf) cancelAnimationFrame(this._fullscreenResizeRaf);
                this._fullscreenResizeRaf = requestAnimationFrame(fitToScreen);
            });
            ro.observe(viewport);
            // Store on instance for cleanup on close
            this._fullscreenResizeObserver = ro;
        }
    }
}






/**
 * =============================================================================
 * SECTION 11: INITIALIZATION & GLOBALS
 * =============================================================================
 */

// 11.1.1
if (typeof window !== 'undefined') {
    window.mermaidFontController = new MermaidFontController();
}

// Export for use by visualization engine (only if defined here and not already provided)
if (typeof window !== 'undefined' &&
    typeof window.renderEnhancedMarkdown !== 'function' &&
    typeof renderEnhancedMarkdown === 'function') {
    window.renderEnhancedMarkdown = renderEnhancedMarkdown;
}


// 11.1.2
window.plotlySpacingController = new PlotlySpacingController();

// 11.1.3
window.VisualizationEngine = VisualizationEngine;

// 11.1.4 - Initialize after DOM is ready
if (typeof module === 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.vizEngine = new VisualizationEngine();
        });
    } else {
        // DOM already loaded
        window.vizEngine = new VisualizationEngine();
    }
}

console.log('⚙️ Initializing Unified Visualization Engine V1.19...');
console.log('✅ Unified Visualization Engine V1.19 loaded successfully');







/**
 * VIZ POPUP MANAGER
 * =================
 *
 * Provides two expansion modes for HTML/React iframe visualizations:
 *
 *   1. Side Panel Column â€” inserted as a sibling flex column INSIDE
 *                          #multi-agent-container, immediately to the RIGHT
 *                          of the originating agent column. Multiple panels
 *                          can be open simultaneously (one per unique chartId).
 *                          Clicking the panel button again on the same viz
 *                          toggles it closed. Panels can be drag-reordered
 *                          via the grip handle, but always stay to the right
 *                          of their origin agent column. Right-edge resize handle.
 *
 *   2. Floating Modal    â€” draggable, resizable free-floating window.
 *                          Corner-drag resizes using pointer capture (hold and
 *                          drag â€” no click-to-toggle). Multiple floats coexist.
 *                          Height grows with iframe content via postMessage.
 *                          Default size: 640px wide Ã— 400px iframe.
 *
 * All resize interactions use Pointer Events + setPointerCapture for correct
 * click-hold-drag-release behaviour on all devices.
 *
 * Usage (called from viz action bars):
 *   window.vizPopupManager.openPanel(vizContainer, chartId, title)
 *   window.vizPopupManager.openFloat(vizContainer, chartId, title)
 *
 * Relies on the origin viz container having an <iframe> with srcdoc set.
 * Re-creates a fresh iframe in the popup using the same srcdoc.
 */

class VizPopupManager {
    constructor() {
        this._floats   = new Map(); // chartId â†’ float el
        this._panels   = new Map(); // chartId â†’ { panel, agentCol }
        this._zBase    = 9000;
        this._zCounter = 0;

        this._injectStyles();
    }

    // â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    //  PUBLIC API
    // â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    /** Open (or focus) a draggable free-floating modal for this viz. */
    openFloat(vizContainer, chartId, title = 'Visualization') {
        if (this._floats.has(chartId)) {
            this._raise(this._floats.get(chartId));
            return;
        }

        // Check if this is an iframe-based viz (HTML/React) or data-based (Plotly/etc)
        const srcdoc = this._getSrcdoc(vizContainer);
        const isIframeBased = !!srcdoc;

        if (!isIframeBased) {
            // Non-iframe viz: fetch from vizEngine and re-render
            return this._openFloatViz(chartId, title);
        }

        const originRect = vizContainer.getBoundingClientRect();
        const left = Math.min(originRect.left + 20, window.innerWidth  - 660);
        const top  = Math.max(originRect.top  - 30, 20);

        const modal = document.createElement('div');
        modal.className  = 'vpm-float';
        modal.style.left = `${Math.max(left, 10)}px`;
        modal.style.top  = `${Math.max(top,  10)}px`;
        modal.style.zIndex = String(this._zBase + ++this._zCounter);
        modal.dataset.chartId = chartId;

        modal.innerHTML = `
            <div class="vpm-header vpm-drag-handle">
                <span class="vpm-title">${this._esc(title)}</span>
                <div class="vpm-controls">
                    <button class="vpm-btn vpm-btn-panel" title="Open as side panel">&#x229F;</button>
                    <button class="vpm-btn vpm-btn-close" title="Close">&#x2715;</button>
                </div>
            </div>
            <div class="vpm-body"></div>
            <div class="vpm-resize-corner" title="Hold and drag to resize"></div>
        `;

        modal.querySelector('.vpm-btn-close').addEventListener('click', () => this.closeFloat(chartId));
        modal.querySelector('.vpm-btn-panel').addEventListener('click', () => {
            this.closeFloat(chartId);
            this.openPanel(vizContainer, chartId, title);
        });

        const body  = modal.querySelector('.vpm-body');
        const newId = `vpm-float-${chartId}`;
        body.appendChild(this._buildFloatIframe(srcdoc, newId));
        this._attachFloatResizeListener(newId, body);

        this._makeDraggable(modal, modal.querySelector('.vpm-drag-handle'));
        this._makeResizableCorner(modal, modal.querySelector('.vpm-resize-corner'));

        modal.addEventListener('pointerdown', () => this._raise(modal), true);

        document.body.appendChild(modal);
        this._floats.set(chartId, modal);
    }

    /** Close a floating modal by chartId. */
    closeFloat(chartId) {
        const el = this._floats.get(chartId);
        if (!el) return;
        el.remove();
        this._floats.delete(chartId);
    }

    /**
     * Open a side-panel column for this viz inside #multi-agent-container,
     * inserted after the originating agent column (and after any existing
     * panels for it).  Multiple panels can coexist â€” one per chartId.
     * Clicking the button again on an already-open panel toggles it closed.
     */
    openPanel(vizContainer, chartId, title = 'Visualization') {
        // Toggle off if already open
        if (this._panels.has(chartId)) {
            this._removePanel(chartId);
            return;
        }

        // Check if this is an iframe-based viz (HTML/React) or data-based (Plotly/etc)
        const srcdoc = this._getSrcdoc(vizContainer);
        const isIframeBased = !!srcdoc;

        if (!isIframeBased) {
            // Non-iframe viz: fetch from vizEngine and re-render
            return this._openPanelViz(vizContainer, chartId, title);
        }

        const agentCol = vizContainer.closest('.agent-column');
        const mac = document.getElementById('multi-agent-container');

        const panel = document.createElement('div');
        panel.className = 'vpm-panel-col';
        panel.dataset.chartId = chartId;
        if (agentCol) panel.dataset.originAgentId = agentCol.dataset.agentId || '';

        panel.innerHTML = `
            <div class="vpm-panel-header">
                <span class="vpm-panel-grip" title="Drag to reorder">&#x22EE;&#x22EE;</span>
                <span class="vpm-title">${this._esc(title)}</span>
                <div class="vpm-controls">
                    <button class="vpm-btn vpm-btn-float" title="Open as floating window">&#x229E;</button>
                    <button class="vpm-btn vpm-btn-close" title="Close panel">&#x2715;</button>
                </div>
            </div>
            <div class="vpm-panel-body"></div>
            <div class="vpm-panel-resize" title="Hold and drag to resize panel width"></div>
        `;

        panel.querySelector('.vpm-btn-close').addEventListener('click', () => this._removePanel(chartId));
        panel.querySelector('.vpm-btn-float').addEventListener('click', () => {
            this._removePanel(chartId);
            this.openFloat(vizContainer, chartId, title);
        });

        const body  = panel.querySelector('.vpm-panel-body');
        const newId = `vpm-panel-${chartId}`;
        body.appendChild(this._buildPanelIframe(srcdoc, newId));

        this._makePanelWidthResizable(panel, panel.querySelector('.vpm-panel-resize'));
        this._makePanelReorderable(panel, panel.querySelector('.vpm-panel-grip'));

        // Insert after origin agent column and any existing panels following it
        if (mac && agentCol && agentCol.parentNode === mac) {
            const insertRef = this._findPanelInsertionPoint(mac, agentCol);
            mac.insertBefore(panel, insertRef);  // insertRef=null â†’ appendChild
        } else if (mac) {
            mac.appendChild(panel);
        } else {
            document.body.appendChild(panel);
        }

        requestAnimationFrame(() => {
            panel.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
        });

        this._panels.set(chartId, { panel, agentCol });
    }

    // â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    //  PRIVATE HELPERS
    // â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    /**
     * Find the DOM reference node for inserting a new panel after agentCol.
     * Scans rightward past existing vpm-panel-col siblings until it hits
     * the next .agent-column or the end of mac.
     * Returns null â†’ use mac.appendChild.
     */
    _findPanelInsertionPoint(mac, agentCol) {
        let node = agentCol.nextSibling;
        while (node) {
            if (node.nodeType === Node.ELEMENT_NODE) {
                if (node.classList.contains('agent-column')) return node;
                // vpm-panel-col / other â†’ keep scanning
            }
            node = node.nextSibling;
        }
        return null; // append at end
    }

    _removePanel(chartId) {
        const entry = this._panels.get(chartId);
        if (!entry) return;
        entry.panel.remove();
        this._panels.delete(chartId);
    }

    _getSrcdoc(vizContainer) {
        const iframe = vizContainer.querySelector('iframe');
        return iframe?.srcdoc || null;
    }
    /** Get viz engine instance from window globals */
    _getVizEngine() {
        // Try multiple locations where engine might be registered
        if (window.sidebarVisualizationState?.engine) {
            return window.sidebarVisualizationState.engine;
        }
        if (window.vizEngine) {
            return window.vizEngine;
        }
        console.error('[VizPopup] No visualization engine found');
        return null;
    }

    /** Open float for non-iframe viz types (Plotly, ChartJS, etc) */
    async _openFloatViz(chartId, title) {
        const engine = this._getVizEngine();
        if (!engine) return;

        const chartRecord = engine.charts.get(chartId);
        if (!chartRecord) {
            console.warn('[VizPopup] No chart data found for:', chartId);
            return;
        }

        const originRect = chartRecord.container?.getBoundingClientRect() || { left: 100, top: 100 };
        const left = Math.min(originRect.left + 20, window.innerWidth  - 660);
        const top  = Math.max(originRect.top  - 30, 20);

        const modal = document.createElement('div');
        modal.className  = 'vpm-float';
        modal.style.left = `${Math.max(left, 10)}px`;
        modal.style.top  = `${Math.max(top,  10)}px`;
        modal.style.zIndex = String(this._zBase + ++this._zCounter);
        modal.dataset.chartId = chartId;

        modal.innerHTML = `
            <div class="vpm-header vpm-drag-handle">
                <span class="vpm-title">${this._esc(title)}</span>
                <div class="vpm-controls">
                    <button class="vpm-btn vpm-btn-panel" title="Open as side panel">&#x229F;</button>
                    <button class="vpm-btn vpm-btn-close" title="Close">&#x2715;</button>
                </div>
            </div>
            <div class="vpm-body"></div>
            <div class="vpm-resize-corner" title="Hold and drag to resize"></div>
        `;

        modal.querySelector('.vpm-btn-close').addEventListener('click', () => this.closeFloat(chartId));
        modal.querySelector('.vpm-btn-panel').addEventListener('click', () => {
            this.closeFloat(chartId);
            const origContainer = chartRecord.container?.closest('.viz-container');
            if (origContainer) {
                this.openPanel(origContainer, chartId, title);
            }
        });

        const body = modal.querySelector('.vpm-body');
        const vizContainer = document.createElement('div');
        vizContainer.className = 'viz-container';
        vizContainer.style.cssText = 'width:100%;height:100%;min-height:300px;';

        const contentArea = document.createElement('div');
        contentArea.className = 'viz-content-area';
        contentArea.style.cssText = 'width:100%;height:100%;';
        vizContainer.appendChild(contentArea);
        body.appendChild(vizContainer);

        this._makeDraggable(modal, modal.querySelector('.vpm-drag-handle'));
        this._makeResizableCorner(modal, modal.querySelector('.vpm-resize-corner'));
        modal.addEventListener('pointerdown', () => this._raise(modal), true);

        document.body.appendChild(modal);
        this._floats.set(chartId, modal);

        // Re-render the viz in the popup
        const newChartId = `${chartId}__float_${Date.now()}`;
        try {
            await engine.renderVisualizationDirectly(chartRecord.item, vizContainer, newChartId);
            console.log('[VizPopup] Float viz rendered:', chartRecord.type);
        } catch (err) {
            console.error('[VizPopup] Float render failed:', err);
            body.innerHTML = `<div style="padding:20px;color:#f85149;">Failed to render ${chartRecord.type}: ${err.message}</div>`;
        }
    }

    /** Open panel for non-iframe viz types */
    async _openPanelViz(vizContainer, chartId, title) {
        const engine = this._getVizEngine();
        if (!engine) return;

        const chartRecord = engine.charts.get(chartId);
        if (!chartRecord) {
            console.warn('[VizPopup] No chart data found for:', chartId);
            return;
        }

        const agentCol = vizContainer.closest('.agent-column');
        const mac = document.getElementById('multi-agent-container');

        const panel = document.createElement('div');
        panel.className = 'vpm-panel-col';
        panel.dataset.chartId = chartId;
        if (agentCol) panel.dataset.originAgentId = agentCol.dataset.agentId || '';

        panel.innerHTML = `
            <div class="vpm-panel-header">
                <span class="vpm-panel-grip" title="Drag to reorder">&#x22EE;&#x22EE;</span>
                <span class="vpm-title">${this._esc(title)}</span>
                <div class="vpm-controls">
                    <button class="vpm-btn vpm-btn-float" title="Open as floating window">&#x229E;</button>
                    <button class="vpm-btn vpm-btn-close" title="Close panel">&#x2715;</button>
                </div>
            </div>
            <div class="vpm-panel-body"></div>
            <div class="vpm-panel-resize" title="Hold and drag to resize panel width"></div>
        `;

        panel.querySelector('.vpm-btn-close').addEventListener('click', () => this._removePanel(chartId));
        panel.querySelector('.vpm-btn-float').addEventListener('click', () => {
            this._removePanel(chartId);
            this._openFloatViz(chartId, title);
        });

        const body = panel.querySelector('.vpm-panel-body');
        const panelVizContainer = document.createElement('div');
        panelVizContainer.className = 'viz-container';
        panelVizContainer.style.cssText = 'width:100%;height:100%;';

        const contentArea = document.createElement('div');
        contentArea.className = 'viz-content-area';
        contentArea.style.cssText = 'width:100%;height:100%;';
        panelVizContainer.appendChild(contentArea);
        body.appendChild(panelVizContainer);

        this._makePanelWidthResizable(panel, panel.querySelector('.vpm-panel-resize'));
        this._makePanelReorderable(panel, panel.querySelector('.vpm-panel-grip'));

        // Insert after origin agent column and any existing panels following it
        if (mac && agentCol && agentCol.parentNode === mac) {
            const insertRef = this._findPanelInsertionPoint(mac, agentCol);
            mac.insertBefore(panel, insertRef);
        } else if (mac) {
            mac.appendChild(panel);
        } else {
            document.body.appendChild(panel);
        }

        requestAnimationFrame(() => {
            panel.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
        });

        this._panels.set(chartId, { panel, agentCol });

        // Re-render the viz in the panel
        const newChartId = `${chartId}__panel_${Date.now()}`;
        try {
            await engine.renderVisualizationDirectly(chartRecord.item, panelVizContainer, newChartId);
            console.log('[VizPopup] Panel viz rendered:', chartRecord.type);
        } catch (err) {
            console.error('[VizPopup] Panel render failed:', err);
            body.innerHTML = `<div style="padding:20px;color:#f85149;">Failed to render ${chartRecord.type}: ${err.message}</div>`;
        }
    }
    /** Float iframe â€” starts at 400px height, grows via postMessage. */
    _buildFloatIframe(srcdoc, id) {
        const iframe = document.createElement('iframe');
        iframe.id = id;
        iframe.sandbox = 'allow-scripts allow-forms allow-modals allow-pointer-lock allow-downloads';
        iframe.allow   = 'clipboard-write';
        iframe.style.cssText = 'width:100%;height:400px;min-height:300px;border:none;display:block;background:white;';
        iframe.srcdoc = srcdoc;
        return iframe;
    }

    /** Panel iframe â€” fills body via height:100%. */
    _buildPanelIframe(srcdoc, id) {
        const iframe = document.createElement('iframe');
        iframe.id = id;
        iframe.sandbox = 'allow-scripts allow-forms allow-modals allow-pointer-lock allow-downloads';
        iframe.allow   = 'clipboard-write';
        iframe.style.cssText = 'width:100%;height:100%;border:none;display:block;background:white;';
        iframe.srcdoc = srcdoc;
        return iframe;
    }

    /** Listen for postMessage resize events and grow float iframe height. */
    _attachFloatResizeListener(iframeId, bodyEl) {
        // The srcdoc script broadcasts the *original* chartId (e.g. "two-rule-html-123"),
        // not the prefixed popup id ("vpm-float-two-rule-html-123").  Strip the prefix.
        const originalId = iframeId.replace(/^vpm-(float|panel)-/, '');

        window.addEventListener('message', (ev) => {
            if (ev.data?.type === 'iframe-resize' && ev.data.id === originalId) {
                const targetH = Math.min(
                    Math.max(ev.data.height + 24, 300),
                    Math.floor(window.innerHeight * 0.88)
                );
                // CSS.escape added 2026-07-26 (bug-findings M3): chartId is
                // user-supplied. If it contains `.`, `[`, `:`, or any other
                // CSS combinator, the raw `#${id}` selector throws SyntaxError
                // and the resize handler silently falls through. Escape it.
                const iframe = bodyEl.querySelector(`#${CSS.escape(iframeId)}`);
                if (iframe) {
                    iframe.style.height = targetH + 'px';
                    // Keep body in sync so corner-drag baseline stays accurate
                    bodyEl.style.height = targetH + 'px';
                }
            } else if (ev.data?.type === 'react-render-snapshot' && ev.data.id === originalId) {
                // Happy-path diagnostic (added 2026-07-23). Captures the
                // iframe's full runtime state RIGHT BEFORE auto-mount so we
                // can diagnose "Babel succeeded, no errors, blank iframe"
                // without opening DevTools inside each child iframe.
                try {
                    window.__renderSnapshots__ = window.__renderSnapshots__ || {};
                    window.__renderSnapshots__[ev.data.id] = ev.data.snap;
                    window.__lastRenderSnapshotId = ev.data.id;
                    console.log('[REACT_RENDERER_PARENT_DIAG] snapshot for', ev.data.id, JSON.stringify(ev.data.snap, null, 2));
                } catch (_) {}
            }
        });
    }

    _raise(el) {
        el.style.zIndex = String(this._zBase + ++this._zCounter);
    }

    _esc(str) {
        // Quotes added 2026-07-26 (bug-findings M3). The HTML we generate
        // only uses this in text-content positions today (between tags),
        // where quote-escape isn't strictly required — but adding the two
        // quotes is one-line hygiene and makes the helper safe to paste
        // into attribute-context interpolations in the future.
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // â”€â”€ Draggable float header (pointer-captured) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    _makeDraggable(el, handle) {
        let ox = 0, oy = 0;
        handle.style.cursor = 'grab';

        const onMove = (e) => {
            let nx = e.clientX - ox;
            let ny = e.clientY - oy;
            nx = Math.max(0, Math.min(nx, window.innerWidth  - el.offsetWidth));
            ny = Math.max(0, Math.min(ny, window.innerHeight - 48));
            el.style.left = nx + 'px';
            el.style.top  = ny + 'px';
        };
        const onUp = (e) => {
            handle.style.cursor = 'grab';
            handle.releasePointerCapture(e.pointerId);
            handle.removeEventListener('pointermove',   onMove);
            handle.removeEventListener('pointerup',     onUp);
            handle.removeEventListener('pointercancel', onUp);
        };
        handle.addEventListener('pointerdown', (e) => {
            if (e.target.classList.contains('vpm-btn')) return;
            e.preventDefault();
            handle.style.cursor = 'grabbing';
            ox = e.clientX - el.getBoundingClientRect().left;
            oy = e.clientY - el.getBoundingClientRect().top;
            handle.setPointerCapture(e.pointerId);
            handle.addEventListener('pointermove',   onMove);
            handle.addEventListener('pointerup',     onUp);
            handle.addEventListener('pointercancel', onUp);
        });
    }

    // â”€â”€ Float corner resize (pointer-captured) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    _makeResizableCorner(el, corner) {
        let sx, sy, sw, sh;
        corner.style.cursor = 'nwse-resize';
        corner.style.touchAction = 'none';

        const onMove = (e) => {
            const nw = Math.max(360, sw + (e.clientX - sx));
            const nh = Math.max(280, sh + (e.clientY - sy));
            el.style.width = nw + 'px';
            const body    = el.querySelector('.vpm-body');
            const headerH = el.querySelector('.vpm-header')?.offsetHeight || 42;
            if (body) {
                const bodyH = nh - headerH;
                body.style.height = bodyH + 'px';
                // Also explicitly resize the iframe — it has an inline height
                // set at creation time that won't auto-stretch with the body.
                const iframe = body.querySelector('iframe');
                if (iframe) iframe.style.height = bodyH + 'px';
            }
        };
        const onUp = (e) => {
            corner.releasePointerCapture(e.pointerId);
            corner.removeEventListener('pointermove',   onMove);
            corner.removeEventListener('pointerup',     onUp);
            corner.removeEventListener('pointercancel', onUp);
        };
        corner.addEventListener('pointerdown', (e) => {
            e.preventDefault();
            e.stopPropagation();
            sx = e.clientX; sy = e.clientY;
            sw = el.offsetWidth; sh = el.offsetHeight;
            corner.setPointerCapture(e.pointerId);
            corner.addEventListener('pointermove',   onMove);
            corner.addEventListener('pointerup',     onUp);
            corner.addEventListener('pointercancel', onUp);
        });
    }

    // â”€â”€ Panel right-edge width resize (pointer-captured) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    _makePanelWidthResizable(panel, resizeEl) {
        let sx, sw;
        resizeEl.style.cursor = 'ew-resize';
        resizeEl.style.touchAction = 'none';

        const onMove = (e) => {
            const nw = Math.max(280, Math.min(sw + (e.clientX - sx), window.innerWidth * 0.72));
            panel.style.flex = `0 0 ${nw}px`;
        };
        const onUp = (e) => {
            resizeEl.releasePointerCapture(e.pointerId);
            resizeEl.removeEventListener('pointermove',   onMove);
            resizeEl.removeEventListener('pointerup',     onUp);
            resizeEl.removeEventListener('pointercancel', onUp);
        };
        resizeEl.addEventListener('pointerdown', (e) => {
            e.preventDefault();
            sx = e.clientX;
            sw = panel.getBoundingClientRect().width;
            resizeEl.setPointerCapture(e.pointerId);
            resizeEl.addEventListener('pointermove',   onMove);
            resizeEl.addEventListener('pointerup',     onUp);
            resizeEl.addEventListener('pointercancel', onUp);
        });
    }

    // â”€â”€ Panel drag-to-reorder (pointer-captured) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    /**
     * Drag a panel's grip handle to reorder it within #multi-agent-container.
     * The panel must always stay to the right of its origin agent column.
     * A translucent ghost follows the cursor; a dashed placeholder shows
     * where the panel will land.
     */
    _makePanelReorderable(panel, grip) {
        if (!grip) return;
        grip.style.cursor = 'grab';
        grip.style.touchAction = 'none';

        let ghost       = null;
        let placeholder = null;
        let ox = 0;

        const onMove = (e) => {
            if (!ghost) return;

            // Move ghost
            const ghostLeft = e.clientX - ox;
            ghost.style.left = ghostLeft + 'px';

            // Determine insertion point among all vpm-panel-col siblings
            const mac = document.getElementById('multi-agent-container');
            if (!mac) return;

            const allPanels = Array.from(mac.querySelectorAll('.vpm-panel-col')).filter(p => p !== panel);
            let newRef = null; // insertBefore target; null â†’ append

            for (const sibling of allPanels) {
                const rect = sibling.getBoundingClientRect();
                if (e.clientX < rect.left + rect.width / 2) {
                    newRef = sibling;
                    break;
                }
            }

            // Constraint: must stay after origin agent column
            const originId = panel.dataset.originAgentId;
            if (newRef && originId) {
                const originCol = mac.querySelector(`.agent-column[data-agent-id="${originId}"]`);
                if (originCol) {
                    // If newRef precedes or equals the origin column, block the move
                    let scan = newRef;
                    let foundOriginBefore = false;
                    while (scan) {
                        if (scan === originCol) { foundOriginBefore = true; break; }
                        scan = scan.previousElementSibling;
                    }
                    if (foundOriginBefore) newRef = null; // clamp to end
                }
            }

            if (placeholder) {
                if (newRef) mac.insertBefore(placeholder, newRef);
                else        mac.appendChild(placeholder);
            }
        };

        const onUp = (e) => {
            grip.style.cursor = 'grab';
            grip.releasePointerCapture(e.pointerId);
            grip.removeEventListener('pointermove',   onMove);
            grip.removeEventListener('pointerup',     onUp);
            grip.removeEventListener('pointercancel', onUp);

            if (ghost) { ghost.remove(); ghost = null; }
            if (placeholder) {
                placeholder.parentElement?.insertBefore(panel, placeholder);
                placeholder.remove();
                placeholder = null;
            }

            panel.style.opacity       = '';
            panel.style.pointerEvents = '';
        };

        grip.addEventListener('pointerdown', (e) => {
            if (e.button !== 0) return;
            e.preventDefault();
            e.stopPropagation();

            const mac = document.getElementById('multi-agent-container');
            if (!mac) return;

            grip.style.cursor = 'grabbing';
            const rect = panel.getBoundingClientRect();
            ox = e.clientX - rect.left;

            // Placeholder fills original slot
            placeholder = document.createElement('div');
            placeholder.className = 'vpm-panel-placeholder';
            placeholder.style.cssText = [
                `flex: 0 0 ${rect.width}px`,
                'height: 100%',
                'background: rgba(88,166,255,0.07)',
                'border: 2px dashed rgba(88,166,255,0.4)',
                'border-radius: 8px',
                'pointer-events: none',
                'flex-shrink: 0',
            ].join(';');
            panel.parentElement?.insertBefore(placeholder, panel.nextSibling);

            // Ghost: visual clone following cursor
            ghost = document.createElement('div');
            ghost.className = 'vpm-panel-ghost';
            ghost.style.cssText = [
                `width: ${rect.width}px`,
                `height: ${Math.min(rect.height, 120)}px`,
                `top: ${rect.top}px`,
                `left: ${rect.left}px`,
                'position: fixed',
                `z-index: ${this._zBase + 8000}`,
                'opacity: 0.78',
                'pointer-events: none',
                'background: var(--bg-tertiary, #161b22)',
                'border: 2px solid var(--accent-primary, #58a6ff)',
                'border-radius: 8px',
                'box-shadow: 0 12px 40px rgba(0,0,0,0.5)',
                'overflow: hidden',
                'transition: none',
            ].join(';');
            ghost.innerHTML = panel.querySelector('.vpm-panel-header')?.outerHTML || '';
            // Ghost header buttons should not be interactive
            ghost.querySelectorAll('button').forEach(b => b.style.pointerEvents = 'none');
            document.body.appendChild(ghost);

            // Dim original
            panel.style.opacity = '0.3';
            panel.style.pointerEvents = 'none';

            grip.setPointerCapture(e.pointerId);
            grip.addEventListener('pointermove',   onMove);
            grip.addEventListener('pointerup',     onUp);
            grip.addEventListener('pointercancel', onUp);
        });
    }

    // â”€â”€ Styles â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    _injectStyles() {
        if (document.getElementById('vpm-styles')) return;
        const style = document.createElement('style');
        style.id = 'vpm-styles';
        style.textContent = `
            /* â”€â”€ Common header / controls â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
            .vpm-header,
            .vpm-panel-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 8px 10px;
                background: var(--bg-tertiary, #161b22);
                border-bottom: 1px solid var(--border-default, #30363d);
                border-radius: 8px 8px 0 0;
                user-select: none;
                flex-shrink: 0;
                gap: 6px;
            }
            .vpm-title {
                font-size: 12px;
                font-weight: 600;
                color: var(--text-primary, #e2e8f0);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                flex: 1;
                min-width: 0;
            }
            .vpm-controls {
                display: flex;
                gap: 4px;
                flex-shrink: 0;
            }
            /* Panel grip / drag handle */
            .vpm-panel-grip {
                font-size: 11px;
                color: var(--text-muted, #6e7681);
                cursor: grab;
                padding: 0 2px;
                flex-shrink: 0;
                letter-spacing: -2px;
                opacity: 0.7;
                transition: opacity 0.15s, color 0.15s;
                touch-action: none;
            }
            .vpm-panel-grip:hover {
                opacity: 1;
                color: var(--accent-primary, #58a6ff);
            }

            /* â”€â”€ Icon-only header buttons â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
            .vpm-btn {
                width: 24px;
                height: 24px;
                padding: 0;
                background: transparent;
                border: 1px solid var(--border-default, #30363d);
                color: var(--text-secondary, #8b949e);
                border-radius: 4px;
                font-size: 14px;
                line-height: 1;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.15s, color 0.15s, border-color 0.15s;
                flex-shrink: 0;
            }
            .vpm-btn:hover {
                background: var(--border-default, #30363d);
                color: var(--text-primary, #e2e8f0);
            }
            .vpm-btn-close:hover {
                background: #a93226;
                border-color: #a93226;
                color: #fff;
            }

            /* â”€â”€ Floating Modal â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
            .vpm-float {
                position: fixed;
                width: 640px;          /* sensible default; user can drag-resize */
                min-width: 360px;
                min-height: 320px;
                background: var(--bg-secondary, #0d1117);
                border: 1px solid var(--border-default, #30363d);
                border-radius: 10px;
                box-shadow: 0 16px 56px rgba(0, 0, 0, 0.55);
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .vpm-body {
                flex: 1;
                overflow: auto;
                background: white;
                min-height: 300px;
            }
            .vpm-resize-corner {
                position: absolute;
                bottom: 0;
                right: 0;
                width: 20px;
                height: 20px;
                background: linear-gradient(135deg, transparent 40%, var(--border-default, #555) 40%);
                border-bottom-right-radius: 8px;
                cursor: nwse-resize;
                z-index: 2;
                touch-action: none;
            }

            /* â”€â”€ Side Panel Column â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
            .vpm-panel-col {
                flex: 0 0 400px;
                background: var(--bg-secondary, #0d1117);
                border: 1px solid var(--border-default, #30363d);
                border-radius: 8px;
                display: flex;
                flex-direction: column;
                height: 100%;
                position: relative;
                overflow: hidden;
                min-width: 0;
            }
            .vpm-panel-col:hover {
                border-color: var(--accent-primary, #58a6ff);
            }
            .vpm-panel-body {
                flex: 1;
                overflow: hidden;
                background: white;
                min-height: 0;
            }
            /* Right-edge width resize handle */
            .vpm-panel-resize {
                position: absolute;
                top: 0;
                right: 0;
                width: 6px;
                height: 100%;
                cursor: ew-resize;
                background: transparent;
                transition: background 0.15s;
                z-index: 2;
                touch-action: none;
            }
            .vpm-panel-resize:hover {
                background: rgba(88,166,255,0.4);
            }

            /* Drag-reorder placeholder */
            .vpm-panel-placeholder {
                flex-shrink: 0;
                transition: none;
            }
        `;
        document.head.appendChild(style);
    }
}

// Singleton: create once, expose globally
window.vizPopupManager = new VizPopupManager();

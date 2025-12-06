/**
 * PROFESSIONAL VISUALIZATION TOOLBAR SYSTEM
 * ==========================================
 * Provides universal toolbar with export, fullscreen, copy, share capabilities
 * for ALL visualization types.
 */

class VisualizationToolbar {
    constructor(visualizationEngine) {
        this.engine = visualizationEngine;
        this.toolbars = new Map();
    }

    /**
     * Create toolbar for a visualization
     * @param {string} type - Visualization type (apexcharts, cad, etc.)
     * @param {HTMLElement} container - Visualization container
     * @param {Object} data - Visualization data
     * @param {string} id - Unique visualization ID
     */
    createToolbar(type, container, data, id) {
        const toolbar = document.createElement('div');
        toolbar.className = 'viz-toolbar';
        toolbar.dataset.vizId = id;
        toolbar.dataset.vizType = type;

        // Universal buttons (all visualizations)
        const universalButtons = this.createUniversalButtons(type, container, data, id);
        toolbar.appendChild(universalButtons);

        // Type-specific buttons
        const typeButtons = this.createTypeSpecificButtons(type, container, data, id);
        if (typeButtons) {
            toolbar.appendChild(typeButtons);
        }

        // Store toolbar reference
        this.toolbars.set(id, toolbar);

        return toolbar;
    }

    /**
     * Create universal buttons (all visualizations have these)
     */
    createUniversalButtons(type, container, data, id) {
        const group = document.createElement('div');
        group.className = 'viz-toolbar-group universal-group';

        // Export dropdown
        group.appendChild(this.createExportButton(type, container, data, id));

        // Fullscreen button
        group.appendChild(this.createFullscreenButton(container));

        // Copy button
        group.appendChild(this.createCopyButton(container, data));

        // Share button
        group.appendChild(this.createShareButton(type, data, id));

        return group;
    }

    /**
     * Create export dropdown button
     */
    createExportButton(type, container, data, id) {
        const btn = this.createButton('export', 'Export', 'Export visualization');
        const dropdown = document.createElement('div');
        dropdown.className = 'viz-dropdown viz-dropdown-hidden';

        // Export options based on type
        const exportOptions = this.getExportOptions(type);
        exportOptions.forEach(option => {
            const item = document.createElement('div');
            item.className = 'viz-dropdown-item';
            item.textContent = option.label;
            item.onclick = () => this.handleExport(type, container, data, option.format);
            dropdown.appendChild(item);
        });

        btn.appendChild(dropdown);
        btn.onclick = (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('viz-dropdown-hidden');
        };

        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            dropdown.classList.add('viz-dropdown-hidden');
        });

        return btn;
    }

    /**
     * Get export options for visualization type
     */
    getExportOptions(type) {
        const baseOptions = [
            { label: 'Download PNG', format: 'png' },
            { label: 'Download SVG', format: 'svg' },
            { label: 'Download PDF', format: 'pdf' }
        ];

        const typeOptions = {
            'apexcharts': [
                ...baseOptions,
                { label: 'Download Data (CSV)', format: 'csv' },
                { label: 'Download Data (Excel)', format: 'xlsx' }
            ],
            'plotly': [
                ...baseOptions,
                { label: 'Download Data (CSV)', format: 'csv' }
            ],
            'cad': [
                ...baseOptions,
                { label: 'Download DXF', format: 'dxf' },
                { label: 'Download DWG', format: 'dwg' }
            ],
            'blueprint': [
                ...baseOptions,
                { label: 'Download DXF', format: 'dxf' }
            ],
            'schematic': [
                ...baseOptions,
                { label: 'Download Net List', format: 'net' },
                { label: 'Download Parts List (CSV)', format: 'parts-csv' }
            ],
            'latex': [
                { label: 'Download PNG', format: 'png' },
                { label: 'Download SVG', format: 'svg' },
                { label: 'Download LaTeX Source', format: 'tex' },
                { label: 'Download MathML', format: 'mathml' }
            ],
            'lottie': [
                { label: 'Download Animation (GIF)', format: 'gif' },
                { label: 'Download Animation (MP4)', format: 'mp4' },
                { label: 'Download Lottie JSON', format: 'json' }
            ],
            'execute_html': [
                { label: 'Download HTML', format: 'html' },
                { label: 'Download Screenshot (PNG)', format: 'png' }
            ]
        };

        return typeOptions[type] || baseOptions;
    }

    /**
     * Handle export action
     */
    async handleExport(type, container, data, format) {
        try {
            if (!window.ExportManager) {
                throw new Error('ExportManager not loaded');
            }

            const exportManager = new window.ExportManager();
            await exportManager.export(type, container, data, format);

            this.showToast('Export successful!', 'success');
        } catch (error) {
            console.error('Export failed:', error);
            this.showToast('Export failed: ' + error.message, 'error');
        }
    }

    /**
     * Create fullscreen button
     */
    createFullscreenButton(container) {
        const btn = this.createButton('fullscreen', 'Fullscreen', 'Enter fullscreen mode');
        
        btn.onclick = () => {
            if (!document.fullscreenElement) {
                container.requestFullscreen();
                btn.querySelector('.viz-button-icon').textContent = '✕';
                btn.title = 'Exit fullscreen (ESC)';
            } else {
                document.exitFullscreen();
                btn.querySelector('.viz-button-icon').textContent = '⛶';
                btn.title = 'Enter fullscreen mode';
            }
        };

        // Listen for fullscreen change
        document.addEventListener('fullscreenchange', () => {
            if (!document.fullscreenElement) {
                btn.querySelector('.viz-button-icon').textContent = '⛶';
                btn.title = 'Enter fullscreen mode';
            }
        });

        return btn;
    }

    /**
     * Create copy button
     */
    createCopyButton(container, data) {
        const btn = this.createButton('copy', '📋', 'Copy to clipboard');
        
        btn.onclick = async () => {
            try {
                // Try to copy as image first
                const canvas = await this.containerToCanvas(container);
                canvas.toBlob(async (blob) => {
                    try {
                        await navigator.clipboard.write([
                            new ClipboardItem({ 'image/png': blob })
                        ]);
                        this.showToast('Copied to clipboard!', 'success');
                    } catch (err) {
                        // Fallback: copy as text
                        await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
                        this.showToast('Data copied as text', 'success');
                    }
                });
            } catch (error) {
                console.error('Copy failed:', error);
                this.showToast('Copy failed', 'error');
            }
        };

        return btn;
    }

    /**
     * Create share button
     */
    createShareButton(type, data, id) {
        const btn = this.createButton('share', '🔗', 'Share visualization');
        const dropdown = document.createElement('div');
        dropdown.className = 'viz-dropdown viz-dropdown-hidden';

        // Share options
        const shareOptions = [
            { label: 'Generate Link', action: 'link' },
            { label: 'Generate Embed Code', action: 'embed' },
            { label: 'Generate QR Code', action: 'qr' }
        ];

        shareOptions.forEach(option => {
            const item = document.createElement('div');
            item.className = 'viz-dropdown-item';
            item.textContent = option.label;
            item.onclick = () => this.handleShare(type, data, id, option.action);
            dropdown.appendChild(item);
        });

        btn.appendChild(dropdown);
        btn.onclick = (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('viz-dropdown-hidden');
        };

        return btn;
    }

    /**
     * Handle share action
     */
    async handleShare(type, data, id, action) {
        try {
            if (!window.ShareManager) {
                throw new Error('ShareManager not loaded');
            }

            const shareManager = new window.ShareManager();
            const result = await shareManager.share(type, data, id, action);

            // Show result in modal
            this.showShareModal(result, action);
        } catch (error) {
            console.error('Share failed:', error);
            this.showToast('Share failed: ' + error.message, 'error');
        }
    }

    /**
     * Create type-specific buttons
     */
    createTypeSpecificButtons(type, container, data, id) {
        const group = document.createElement('div');
        group.className = 'viz-toolbar-group type-specific-group';

        switch (type) {
            case 'apexcharts':
                return this.createApexChartsButtons(container, data);
            case 'cad':
            case 'blueprint':
                return this.createCADButtons(container, data);
            case 'schematic':
                return this.createSchematicButtons(container, data);
            case 'lottie':
            case 'gsap':
                return this.createAnimationButtons(container, data);
            case 'threejs':
            case 'molecule':
                return this.create3DButtons(container, data);
            default:
                return null;
        }
    }

    /**
     * Create ApexCharts-specific buttons
     */
    createApexChartsButtons(container, data) {
        const group = document.createElement('div');
        group.className = 'viz-toolbar-group type-specific-group';

        // Data table toggle
        const tableBtn = this.createButton('table', '📊', 'Toggle data table');
        tableBtn.onclick = () => this.toggleDataTable(container, data);
        group.appendChild(tableBtn);

        // Reset zoom
        const resetBtn = this.createButton('reset', '⟲', 'Reset zoom');
        resetBtn.onclick = () => this.resetApexChartsZoom(container);
        group.appendChild(resetBtn);

        return group;
    }

    /**
     * Create CAD-specific buttons
     */
    createCADButtons(container, data) {
        const group = document.createElement('div');
        group.className = 'viz-toolbar-group type-specific-group';

        // Zoom controls
        const zoomInBtn = this.createButton('zoom-in', '🔍+', 'Zoom in');
        zoomInBtn.onclick = () => this.cadZoom(container, 1.25);
        group.appendChild(zoomInBtn);

        const zoomOutBtn = this.createButton('zoom-out', '🔍−', 'Zoom out');
        zoomOutBtn.onclick = () => this.cadZoom(container, 0.8);
        group.appendChild(zoomOutBtn);

        const fitBtn = this.createButton('fit', '⊡', 'Fit to view');
        fitBtn.onclick = () => this.cadFit(container);
        group.appendChild(fitBtn);

        // Measure tool
        const measureBtn = this.createButton('measure', '📏', 'Measure tool');
        measureBtn.onclick = () => this.toggleMeasureTool(container);
        group.appendChild(measureBtn);

        // Layer toggle
        const layerBtn = this.createButton('layers', '☰', 'Toggle layers');
        layerBtn.onclick = () => this.toggleLayers(container);
        group.appendChild(layerBtn);

        return group;
    }

    /**
     * Create Schematic-specific buttons
     */
    createSchematicButtons(container, data) {
        const group = document.createElement('div');
        group.className = 'viz-toolbar-group type-specific-group';

        // Net list
        const netListBtn = this.createButton('netlist', '⚡', 'Show net list');
        netListBtn.onclick = () => this.showNetList(container, data);
        group.appendChild(netListBtn);

        // Parts list
        const partsBtn = this.createButton('parts', '🔌', 'Show parts list');
        partsBtn.onclick = () => this.showPartsList(container, data);
        group.appendChild(partsBtn);

        // Component info
        const infoBtn = this.createButton('info', 'ⓘ', 'Component info');
        infoBtn.onclick = () => this.toggleComponentInfo(container);
        group.appendChild(infoBtn);

        return group;
    }

    /**
     * Create Animation-specific buttons
     */
    createAnimationButtons(container, data) {
        const group = document.createElement('div');
        group.className = 'viz-toolbar-group type-specific-group';

        // Play/pause
        const playBtn = this.createButton('play', '▶', 'Play/Pause');
        playBtn.onclick = () => this.toggleAnimation(container, playBtn);
        group.appendChild(playBtn);

        // Speed control
        const speedBtn = this.createButton('speed', '1×', 'Animation speed');
        const speedDropdown = this.createSpeedDropdown();
        speedBtn.appendChild(speedDropdown);
        speedBtn.onclick = (e) => {
            e.stopPropagation();
            speedDropdown.classList.toggle('viz-dropdown-hidden');
        };
        group.appendChild(speedBtn);

        // Restart
        const restartBtn = this.createButton('restart', '⟲', 'Restart animation');
        restartBtn.onclick = () => this.restartAnimation(container);
        group.appendChild(restartBtn);

        return group;
    }

    /**
     * Create 3D-specific buttons
     */
    create3DButtons(container, data) {
        const group = document.createElement('div');
        group.className = 'viz-toolbar-group type-specific-group';

        // Reset camera
        const resetBtn = this.createButton('reset-camera', '📷', 'Reset camera');
        resetBtn.onclick = () => this.reset3DCamera(container);
        group.appendChild(resetBtn);

        // Auto-rotate toggle
        const rotateBtn = this.createButton('auto-rotate', '↻', 'Auto-rotate');
        rotateBtn.onclick = () => this.toggle3DAutoRotate(container, rotateBtn);
        group.appendChild(rotateBtn);

        return group;
    }

    /**
     * Create generic button
     */
    createButton(id, icon, tooltip) {
        const btn = document.createElement('button');
        btn.className = 'viz-button';
        btn.dataset.action = id;
        btn.title = tooltip;
        
        const iconSpan = document.createElement('span');
        iconSpan.className = 'viz-button-icon';
        iconSpan.textContent = icon;
        btn.appendChild(iconSpan);

        return btn;
    }

    /**
     * Convert container to canvas (for export/copy)
     */
    async containerToCanvas(container) {
        // Use html2canvas library if available
        if (window.html2canvas) {
            return await html2canvas(container, {
                backgroundColor: null,
                scale: 2, // 2x for high-res
                logging: false
            });
        } else {
            throw new Error('html2canvas library not loaded');
        }
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `viz-toast viz-toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('viz-toast-show'), 10);
        setTimeout(() => {
            toast.classList.remove('viz-toast-show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Show share modal
     */
    showShareModal(result, action) {
        const modal = document.createElement('div');
        modal.className = 'viz-modal';
        modal.innerHTML = `
            <div class="viz-modal-content">
                <div class="viz-modal-header">
                    <h3>${action === 'link' ? 'Share Link' : action === 'embed' ? 'Embed Code' : 'QR Code'}</h3>
                    <button class="viz-modal-close">✕</button>
                </div>
                <div class="viz-modal-body">
                    ${action === 'qr' ? `<img src="${result}" alt="QR Code">` : `
                        <textarea readonly>${result}</textarea>
                        <button class="viz-copy-result">Copy to Clipboard</button>
                    `}
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Close button
        modal.querySelector('.viz-modal-close').onclick = () => modal.remove();
        modal.onclick = (e) => {
            if (e.target === modal) modal.remove();
        };

        // Copy button
        const copyBtn = modal.querySelector('.viz-copy-result');
        if (copyBtn) {
            copyBtn.onclick = () => {
                const textarea = modal.querySelector('textarea');
                textarea.select();
                document.execCommand('copy');
                this.showToast('Copied to clipboard!', 'success');
            };
        }
    }

    /**
     * Create speed dropdown for animations
     */
    createSpeedDropdown() {
        const dropdown = document.createElement('div');
        dropdown.className = 'viz-dropdown viz-dropdown-hidden';

        const speeds = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2];
        speeds.forEach(speed => {
            const item = document.createElement('div');
            item.className = 'viz-dropdown-item';
            item.textContent = `${speed}×`;
            item.onclick = () => this.setAnimationSpeed(speed);
            dropdown.appendChild(item);
        });

        return dropdown;
    }

    // Placeholder methods (to be implemented based on renderer capabilities)
    toggleDataTable(container, data) { console.log('Toggle data table'); }
    resetApexChartsZoom(container) { console.log('Reset ApexCharts zoom'); }
    cadZoom(container, factor) { console.log('CAD zoom:', factor); }
    cadFit(container) { console.log('CAD fit to view'); }
    toggleMeasureTool(container) { console.log('Toggle measure tool'); }
    toggleLayers(container) { console.log('Toggle layers'); }
    showNetList(container, data) { console.log('Show net list'); }
    showPartsList(container, data) { console.log('Show parts list'); }
    toggleComponentInfo(container) { console.log('Toggle component info'); }
    toggleAnimation(container, btn) { console.log('Toggle animation'); }
    setAnimationSpeed(speed) { console.log('Set speed:', speed); }
    restartAnimation(container) { console.log('Restart animation'); }
    reset3DCamera(container) { console.log('Reset 3D camera'); }
    toggle3DAutoRotate(container, btn) { console.log('Toggle auto-rotate'); }
}

// Export to window
if (typeof window !== 'undefined') {
    window.VisualizationToolbar = VisualizationToolbar;
}

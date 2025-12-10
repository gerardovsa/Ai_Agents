/**
 * Design Engineering Module - Frontend Logic
 * AI-powered T-slot aluminum structure design system
 * 
 * Features:
 * - Natural language design input
 * - Real-time structural analysis
 * - 3D CAD visualization
 * - BOM generation with pricing
 * - Multi-supplier comparison
 */

class DesignEngineeringModule {
    constructor() {
        this.currentDesign = null;
        this.currentAnalysis = null;
        this.currentBOM = null;
        this.apiBase = '/api/engineering';

        // UI Elements
        this.elements = {
            designInput: null,
            analyzeBtn: null,
            resultsContainer: null,
            cadViewer: null,
            bomTable: null,
            supplierSelect: null
        };

        // State
        this.isAnalyzing = false;
        this.selectedSupplier = 'all';

        console.log('[DESIGN ENGINEERING] Module initialized');
    }

    /**
     * Initialize the module when DOM is ready
     */
    async init() {
        try {
            console.log('[DESIGN ENGINEERING] Starting initialization...');

            // Wait for DOM
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }

            // Get UI elements
            this.cacheElements();

            // Attach event listeners
            this.attachEventListeners();

            // Load example designs
            this.loadExampleDesigns();

            // Initialize CAD renderer
            this.initializeCADRenderer();

            console.log('[DESIGN ENGINEERING] ✅ Initialization complete');

        } catch (error) {
            console.error('[DESIGN ENGINEERING] Initialization error:', error);
            this.showError('Failed to initialize Design Engineering module');
        }
    }

    /**
     * Cache DOM element references
     */
    cacheElements() {
        this.elements = {
            designInput: document.getElementById('design-input'),
            analyzeBtn: document.getElementById('analyze-design-btn'),
            clearBtn: document.getElementById('clear-design-btn'),
            resultsContainer: document.getElementById('results-container'),
            cadViewer: document.getElementById('cad-viewer'),
            bomTable: document.getElementById('bom-table'),
            supplierSelect: document.getElementById('supplier-filter'),
            examplesContainer: document.getElementById('examples-container'),
            exportBtn: document.getElementById('export-bom-btn'),
            loadingIndicator: document.getElementById('analysis-loading'),
            errorContainer: document.getElementById('error-container')
        };

        // Verify critical elements exist
        if (!this.elements.designInput) {
            console.warn('[DESIGN ENGINEERING] Design input field not found');
        }
    }

    /**
     * Attach event listeners to UI elements
     */
    attachEventListeners() {
        // Analyze button
        if (this.elements.analyzeBtn) {
            this.elements.analyzeBtn.addEventListener('click', () => {
                this.analyzeDesign();
            });
        }

        // Clear button
        if (this.elements.clearBtn) {
            this.elements.clearBtn.addEventListener('click', () => {
                this.clearDesign();
            });
        }

        // Enter key in design input
        if (this.elements.designInput) {
            this.elements.designInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.analyzeDesign();
                }
            });
        }

        // Supplier filter
        if (this.elements.supplierSelect) {
            this.elements.supplierSelect.addEventListener('change', (e) => {
                this.selectedSupplier = e.target.value;
                this.filterBOMBySupplier();
            });
        }

        // Export BOM button
        if (this.elements.exportBtn) {
            this.elements.exportBtn.addEventListener('click', () => {
                this.exportBOM();
            });
        }

        console.log('[DESIGN ENGINEERING] Event listeners attached');
    }

    /**
     * Load example designs into UI
     */
    loadExampleDesigns() {
        const examples = [
            {
                name: 'Camper Bed Frame',
                description: '1800mm × 1200mm bed frame with 40mm profiles',
                prompt: 'Design a bed frame for a campervan: 1800mm long, 1200mm wide, using 40mm T-slot profiles. Load capacity: 200kg distributed'
            },
            {
                name: 'Workbench',
                description: '2000mm × 800mm workbench with 60mm legs',
                prompt: 'Design a heavy-duty workbench: 2000mm × 800mm × 900mm tall. Use 60mm profiles for legs, 40mm for frame. Load: 500kg'
            },
            {
                name: 'Storage Shelf',
                description: '1000mm × 400mm 3-tier shelf',
                prompt: 'Design a 3-tier storage shelf: each level 1000mm × 400mm, total height 1500mm, using 30mm profiles. Each shelf holds 50kg'
            },
            {
                name: 'Display Stand',
                description: 'Exhibition display stand 800mm tall',
                prompt: 'Design a product display stand: 600mm × 600mm base, 800mm tall, using 40mm profiles with bracing'
            }
        ];

        if (this.elements.examplesContainer) {
            examples.forEach(example => {
                const card = this.createExampleCard(example);
                this.elements.examplesContainer.appendChild(card);
            });
        }
    }

    /**
     * Create example design card
     */
    createExampleCard(example) {
        const card = document.createElement('div');
        card.className = 'example-card';
        card.innerHTML = `
            <h4>${example.name}</h4>
            <p>${example.description}</p>
            <button class="btn-secondary btn-sm">Use This Example</button>
        `;

        card.querySelector('button').addEventListener('click', () => {
            if (this.elements.designInput) {
                this.elements.designInput.value = example.prompt;
                this.elements.designInput.focus();
            }
        });

        return card;
    }

    /**
     * Analyze design from natural language input
     */
    async analyzeDesign() {
        if (this.isAnalyzing) {
            console.warn('[DESIGN ENGINEERING] Analysis already in progress');
            return;
        }

        const designText = this.elements.designInput?.value.trim();
        if (!designText) {
            this.showError('Please enter a design description');
            return;
        }

        this.isAnalyzing = true;
        this.showLoading(true);
        this.clearError();

        console.log('[DESIGN ENGINEERING] Starting analysis:', designText);

        try {
            // Call AI agent API endpoint
            const response = await fetch(`${this.apiBase}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    description: designText,
                    include_cad: true,
                    include_bom: true,
                    include_analysis: true
                })
            });

            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('[DESIGN ENGINEERING] Analysis complete:', result);

            // Store results
            this.currentDesign = result.design;
            this.currentAnalysis = result.analysis;
            this.currentBOM = result.bom;

            // Display results
            this.displayResults(result);

        } catch (error) {
            console.error('[DESIGN ENGINEERING] Analysis error:', error);
            this.showError(`Analysis failed: ${error.message}`);
        } finally {
            this.isAnalyzing = false;
            this.showLoading(false);
        }
    }

    /**
     * Display analysis results
     */
    displayResults(result) {
        if (!this.elements.resultsContainer) return;

        // Show results container
        this.elements.resultsContainer.style.display = 'block';

        // Display structural analysis
        this.displayStructuralAnalysis(result.analysis);

        // Display CAD model
        this.displayCADModel(result.design);

        // Display BOM
        this.displayBOM(result.bom);

        // Scroll to results
        this.elements.resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    /**
     * Display structural analysis results
     */
    displayStructuralAnalysis(analysis) {
        const container = document.getElementById('analysis-results');
        if (!container || !analysis) return;

        const safetyClass = analysis.safety_factor >= 2.0 ? 'safe' :
            analysis.safety_factor >= 1.5 ? 'warning' : 'danger';

        container.innerHTML = `
            <div class="analysis-card">
                <h3>Structural Analysis</h3>
                
                <div class="analysis-grid">
                    <div class="analysis-metric">
                        <span class="label">Profile Selected:</span>
                        <span class="value">${analysis.profile_size || 'N/A'}</span>
                    </div>
                    
                    <div class="analysis-metric">
                        <span class="label">Max Deflection:</span>
                        <span class="value">${analysis.max_deflection?.toFixed(2) || 'N/A'} mm</span>
                    </div>
                    
                    <div class="analysis-metric">
                        <span class="label">Max Stress:</span>
                        <span class="value">${analysis.max_stress?.toFixed(1) || 'N/A'} MPa</span>
                    </div>
                    
                    <div class="analysis-metric safety-${safetyClass}">
                        <span class="label">Safety Factor:</span>
                        <span class="value">${analysis.safety_factor?.toFixed(2) || 'N/A'}</span>
                    </div>
                </div>
                
                ${analysis.recommendations ? `
                    <div class="recommendations">
                        <h4>Recommendations:</h4>
                        <ul>
                            ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Display CAD model in viewer
     */
    displayCADModel(design) {
        if (!this.elements.cadViewer || !design) return;

        // Check if design has CAD data in delimiter format
        if (design.cad_model) {
            // Parse ```ENGINEERING_CAD delimiter
            const cadMatch = design.cad_model.match(/```ENGINEERING_CAD\n([\s\S]*?)```/);
            if (cadMatch) {
                this.renderCAD(cadMatch[1]);
            }
        } else if (design.technical_drawing) {
            // Display SVG technical drawing
            this.elements.cadViewer.innerHTML = design.technical_drawing;
        } else {
            this.elements.cadViewer.innerHTML = '<p class="no-data">No CAD visualization available</p>';
        }
    }

    /**
     * Render CAD using Three.js (integration with existing renderer)
     */
    renderCAD(cadData) {
        // Check if CAD renderer exists
        if (typeof window.CADRenderer !== 'undefined') {
            window.CADRenderer.render(this.elements.cadViewer, cadData);
        } else {
            console.warn('[DESIGN ENGINEERING] CAD renderer not available');
            this.elements.cadViewer.innerHTML = `
                <div class="cad-fallback">
                    <pre>${cadData}</pre>
                </div>
            `;
        }
    }

    /**
     * Display Bill of Materials
     */
    displayBOM(bom) {
        if (!this.elements.bomTable || !bom) return;

        const parts = bom.parts || [];
        if (parts.length === 0) {
            this.elements.bomTable.innerHTML = '<p class="no-data">No parts in BOM</p>';
            return;
        }

        let html = `
            <table class="bom-table">
                <thead>
                    <tr>
                        <th>Part</th>
                        <th>Description</th>
                        <th>Qty</th>
                        <th>Supplier</th>
                        <th>Part Number</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
        `;

        let totalCost = 0;

        parts.forEach(part => {
            const lineTotal = part.quantity * (part.unit_price || 0);
            totalCost += lineTotal;

            html += `
                <tr>
                    <td>${part.part_name || 'N/A'}</td>
                    <td>${part.description || ''}</td>
                    <td>${part.quantity || 0}</td>
                    <td>${part.supplier || 'N/A'}</td>
                    <td>${part.part_number || 'N/A'}</td>
                    <td>$${(part.unit_price || 0).toFixed(2)}</td>
                    <td>$${lineTotal.toFixed(2)}</td>
                </tr>
            `;
        });

        html += `
                </tbody>
                <tfoot>
                    <tr class="total-row">
                        <td colspan="6"><strong>Total Cost (AUD):</strong></td>
                        <td><strong>$${totalCost.toFixed(2)}</strong></td>
                    </tr>
                </tfoot>
            </table>
        `;

        // Add shipping note if present
        if (bom.shipping_estimate) {
            html += `<p class="shipping-note">+ Estimated shipping: $${bom.shipping_estimate.toFixed(2)}</p>`;
        }

        this.elements.bomTable.innerHTML = html;
    }

    /**
     * Filter BOM by selected supplier
     */
    filterBOMBySupplier() {
        if (!this.currentBOM) return;

        const filteredBOM = {
            ...this.currentBOM,
            parts: this.selectedSupplier === 'all'
                ? this.currentBOM.parts
                : this.currentBOM.parts.filter(p => p.supplier === this.selectedSupplier)
        };

        this.displayBOM(filteredBOM);
    }

    /**
     * Export BOM to CSV
     */
    exportBOM() {
        if (!this.currentBOM || !this.currentBOM.parts) {
            this.showError('No BOM to export');
            return;
        }

        // Create CSV content
        let csv = 'Part Name,Description,Quantity,Supplier,Part Number,Unit Price,Total\n';

        this.currentBOM.parts.forEach(part => {
            const lineTotal = part.quantity * (part.unit_price || 0);
            csv += `"${part.part_name}","${part.description}",${part.quantity},"${part.supplier}","${part.part_number}",${part.unit_price},${lineTotal}\n`;
        });

        // Create download link
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `bom-${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url);

        console.log('[DESIGN ENGINEERING] BOM exported');
    }

    /**
     * Clear design input and results
     */
    clearDesign() {
        if (this.elements.designInput) {
            this.elements.designInput.value = '';
        }

        if (this.elements.resultsContainer) {
            this.elements.resultsContainer.style.display = 'none';
        }

        this.currentDesign = null;
        this.currentAnalysis = null;
        this.currentBOM = null;

        this.clearError();
        console.log('[DESIGN ENGINEERING] Design cleared');
    }

    /**
     * Initialize CAD renderer integration
     */
    initializeCADRenderer() {
        // Check if global CAD renderer exists
        if (typeof window.CADRenderer === 'undefined') {
            console.warn('[DESIGN ENGINEERING] CAD renderer not loaded, loading now...');

            // Dynamically load CAD renderer script
            const script = document.createElement('script');
            script.src = '/UI/visualisation_engine/cad_renderer_engineering.js';
            script.onload = () => {
                console.log('[DESIGN ENGINEERING] CAD renderer loaded');
            };
            script.onerror = () => {
                console.error('[DESIGN ENGINEERING] Failed to load CAD renderer');
            };
            document.head.appendChild(script);
        }
    }

    /**
     * Show loading indicator
     */
    showLoading(show) {
        if (this.elements.loadingIndicator) {
            this.elements.loadingIndicator.style.display = show ? 'flex' : 'none';
        }

        if (this.elements.analyzeBtn) {
            this.elements.analyzeBtn.disabled = show;
            this.elements.analyzeBtn.textContent = show ? 'Analyzing...' : 'Analyze Design';
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        if (this.elements.errorContainer) {
            this.elements.errorContainer.textContent = message;
            this.elements.errorContainer.style.display = 'block';
        }
        console.error('[DESIGN ENGINEERING] Error:', message);
    }

    /**
     * Clear error message
     */
    clearError() {
        if (this.elements.errorContainer) {
            this.elements.errorContainer.textContent = '';
            this.elements.errorContainer.style.display = 'none';
        }
    }
}

// Initialize module when script loads
const designEngineering = new DesignEngineeringModule();

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        designEngineering.init();
    });
} else {
    designEngineering.init();
}

// Export for global access
window.DesignEngineeringModule = designEngineering;

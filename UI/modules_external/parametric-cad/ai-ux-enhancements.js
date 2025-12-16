/**
 * AI-Driven UX Enhancements for CAD
 * Natural language controls, contextual suggestions, visual feedback
 * Based on Plotly Express and Jupyter AI best practices
 */

class AICADExperience {
    constructor(cadModule) {
        this.cadModule = cadModule;
        this.linter = new CADLinter();

        // Suggestion system
        this.suggestionHistory = [];
        this.lastUserInput = '';

        // Context awareness
        this.currentDesign = null;
        this.recentErrors = [];

        // UI elements
        this.initializeUI();
    }

    /**
     * Initialize UI elements for AI assistance
     */
    initializeUI() {
        // Create suggestion panel
        this.createSuggestionPanel();

        // Create contextual help tooltip
        this.createContextualHelp();

        // Create error recovery panel
        this.createErrorRecoveryPanel();

        // Create natural language input
        this.createNaturalLanguageInput();
    }

    /**
     * Create suggestion panel
     */
    createSuggestionPanel() {
        const panel = document.createElement('div');
        panel.id = 'ai-suggestions';
        panel.className = 'ai-panel';
        panel.style.cssText = `
            position: absolute;
            bottom: 80px;
            right: 20px;
            width: 300px;
            max-height: 400px;
            background: rgba(33, 33, 33, 0.95);
            border: 1px solid #444;
            border-radius: 8px;
            padding: 16px;
            overflow-y: auto;
            display: none;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        `;

        panel.innerHTML = `
            <div class="ai-panel-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="margin: 0; color: #4CAF50; font-size: 14px;">
                    <span style="margin-right: 8px;">🤖</span>AI Suggestions
                </h4>
                <button id="close-suggestions" style="background: none; border: none; color: #888; cursor: pointer; font-size: 18px;">&times;</button>
            </div>
            <div id="suggestion-content" style="color: #ddd; font-size: 13px;"></div>
        `;

        document.body.appendChild(panel);

        // Close button
        document.getElementById('close-suggestions').onclick = () => {
            panel.style.display = 'none';
        };

        this.suggestionPanel = panel;
    }

    /**
     * Create contextual help tooltip
     */
    createContextualHelp() {
        const tooltip = document.createElement('div');
        tooltip.id = 'contextual-help';
        tooltip.className = 'ai-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(76, 175, 80, 0.95);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            display: none;
            z-index: 2000;
            pointer-events: none;
            max-width: 250px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.4);
        `;

        document.body.appendChild(tooltip);
        this.contextualTooltip = tooltip;
    }

    /**
     * Create error recovery panel
     */
    createErrorRecoveryPanel() {
        const panel = document.createElement('div');
        panel.id = 'error-recovery';
        panel.className = 'ai-panel';
        panel.style.cssText = `
            position: absolute;
            top: 20px;
            right: 20px;
            width: 350px;
            background: rgba(244, 67, 54, 0.95);
            border: 1px solid #d32f2f;
            border-radius: 8px;
            padding: 16px;
            display: none;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        `;

        panel.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <div>
                    <h4 style="margin: 0 0 4px 0; color: white; font-size: 14px;">⚠️ Error Detected</h4>
                    <p id="error-message" style="margin: 0; color: rgba(255,255,255,0.9); font-size: 12px;"></p>
                </div>
                <button id="close-error" style="background: none; border: none; color: white; cursor: pointer; font-size: 18px;">&times;</button>
            </div>
            <div id="error-suggestions" style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.2);"></div>
        `;

        document.body.appendChild(panel);

        document.getElementById('close-error').onclick = () => {
            panel.style.display = 'none';
        };

        this.errorPanel = panel;
    }

    /**
     * Create natural language input
     */
    createNaturalLanguageInput() {
        const container = document.createElement('div');
        container.id = 'nl-input-container';
        container.style.cssText = `
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 600px;
            background: rgba(33, 33, 33, 0.95);
            border: 2px solid #4CAF50;
            border-radius: 24px;
            padding: 8px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            z-index: 1000;
            box-shadow: 0 4px 16px rgba(0,0,0,0.6);
        `;

        container.innerHTML = `
            <span style="font-size: 20px;">💬</span>
            <input 
                type="text" 
                id="nl-input" 
                placeholder="Describe what you want to create..." 
                style="flex: 1; background: transparent; border: none; color: white; font-size: 14px; outline: none;"
            />
            <button id="nl-submit" style="background: #4CAF50; border: none; color: white; padding: 8px 16px; border-radius: 16px; cursor: pointer; font-size: 13px; font-weight: 500;">Generate</button>
        `;

        document.body.appendChild(container);

        const input = document.getElementById('nl-input');
        const submit = document.getElementById('nl-submit');

        // Submit handler
        const handleSubmit = () => {
            const text = input.value.trim();
            if (text) {
                this.processNaturalLanguage(text);
                input.value = '';
            }
        };

        submit.onclick = handleSubmit;
        input.onkeypress = (e) => {
            if (e.key === 'Enter') handleSubmit();
        };

        // Auto-suggestions as user types
        input.oninput = (e) => {
            this.showAutoSuggestions(e.target.value);
        };

        this.nlInput = input;
    }

    /**
     * Process natural language input
     * @param {string} text - User's natural language request
     */
    async processNaturalLanguage(text) {
        console.log('[AI UX] Processing:', text);
        this.lastUserInput = text;

        try {
            // Show processing indicator
            this.showProcessing(true);

            // Parse intent
            const intent = this.parseIntent(text);

            // Generate suggestions before execution
            this.showPreExecutionSuggestions(intent);

            // Execute based on intent
            switch (intent.action) {
                case 'create':
                    await this.handleCreate(intent);
                    break;
                case 'modify':
                    await this.handleModify(intent);
                    break;
                case 'analyze':
                    await this.handleAnalyze(intent);
                    break;
                case 'export':
                    await this.handleExport(intent);
                    break;
                default:
                    this.showSuggestion('I understand you want to: ' + text + '. Let me help with that.');
            }

            this.showProcessing(false);

        } catch (error) {
            this.showProcessing(false);
            this.handleError(error);
        }
    }

    /**
     * Parse user intent from natural language
     * @param {string} text - Natural language input
     * @returns {object} Intent object
     */
    parseIntent(text) {
        const lowerText = text.toLowerCase();

        // Detect action
        let action = 'create';  // Default

        if (lowerText.match(/create|make|generate|design|build/)) {
            action = 'create';
        } else if (lowerText.match(/modify|change|update|edit|adjust/)) {
            action = 'modify';
        } else if (lowerText.match(/analyze|check|validate|verify|inspect/)) {
            action = 'analyze';
        } else if (lowerText.match(/export|save|download|output/)) {
            action = 'export';
        }

        // Extract parameters
        const params = {
            profile: this.extractProfile(text),
            dimensions: this.extractDimensions(text),
            material: this.extractMaterial(text),
            quantity: this.extractQuantity(text)
        };

        return {
            action,
            rawText: text,
            params
        };
    }

    /**
     * Extract profile from text
     */
    extractProfile(text) {
        const profiles = {
            'profile-5': /profile.?5|20mm|20x20/i,
            'profile-6': /profile.?6|30mm|30x30/i,
            'profile-8': /profile.?8|40mm|40x40/i,
            '1010': /10.?10|1.?inch/i,
            '1515': /15.?15|1\.5.?inch/i,
            '2020': /20.?20|2.?inch/i
        };

        for (const [profile, pattern] of Object.entries(profiles)) {
            if (pattern.test(text)) return profile;
        }

        return 'profile-5';  // Default
    }

    /**
     * Extract dimensions from text
     */
    extractDimensions(text) {
        const dims = {};

        // Extract length (most common)
        const lengthMatch = text.match(/(\d+(?:\.\d+)?)\s*(mm|cm|m|inch|in|ft)?(?:\s+long)?/i);
        if (lengthMatch) {
            let value = parseFloat(lengthMatch[1]);
            const unit = (lengthMatch[2] || 'mm').toLowerCase();

            // Convert to meters
            if (unit === 'mm') value /= 1000;
            else if (unit === 'cm') value /= 100;
            else if (unit === 'in' || unit === 'inch') value *= 0.0254;
            else if (unit === 'ft') value *= 0.3048;

            dims.length = value;
        }

        return dims;
    }

    /**
     * Extract material from text
     */
    extractMaterial(text) {
        const materials = {
            'Aluminum 6061-T6': /aluminum|aluminium|6061/i,
            'Steel': /steel/i,
            'Stainless Steel': /stainless/i,
            'Carbon Fiber': /carbon/i
        };

        for (const [material, pattern] of Object.entries(materials)) {
            if (pattern.test(text)) return material;
        }

        return null;
    }

    /**
     * Extract quantity from text
     */
    extractQuantity(text) {
        const match = text.match(/(\d+)\s+(piece|pieces|unit|units|beam|beams)/i);
        return match ? parseInt(match[1]) : 1;
    }

    /**
     * Handle create action
     */
    async handleCreate(intent) {
        console.log('[AI UX] Creating:', intent);

        // Build CAD specification
        const cadSpec = {
            type: 'parametric_cad',
            model3D: {
                type: 'extrusion',
                profile: intent.params.profile,
                length: intent.params.dimensions.length || 0.5,
                position: { x: 0, y: 0, z: 0 },
                rotation: { x: 0, y: 0, z: 0 }
            },
            camera: {
                position: { x: 1.5, y: 1.5, z: 1.5 },
                target: { x: 0, y: 0, z: 0 }
            }
        };

        if (intent.params.material) {
            cadSpec.constraints = {
                material: intent.params.material
            };
        }

        // Lint before rendering
        const lintResult = this.linter.lint(cadSpec);

        if (!lintResult.valid) {
            this.showLintErrors(lintResult);
            return;
        }

        // Show warnings if any
        if (lintResult.warnings.length > 0) {
            this.showLintWarnings(lintResult);
        }

        // Create visualization
        await this.cadModule.createFromSpec(cadSpec);

        // Show success feedback
        this.showSuccess('Created ' + intent.rawText);
    }

    /**
     * Handle modify action
     */
    async handleModify(intent) {
        if (!this.currentDesign) {
            this.showError('No design to modify. Create one first.');
            return;
        }

        console.log('[AI UX] Modifying:', intent);
        // Implementation depends on modification type
        this.showSuggestion('Modification feature coming soon!');
    }

    /**
     * Handle analyze action
     */
    async handleAnalyze(intent) {
        if (!this.currentDesign) {
            this.showError('No design to analyze. Create one first.');
            return;
        }

        const lintResult = this.linter.lint(this.currentDesign);

        this.showAnalysisResults({
            valid: lintResult.valid,
            errors: lintResult.errors,
            warnings: lintResult.warnings,
            stats: this.calculateStats(this.currentDesign)
        });
    }

    /**
     * Handle export action
     */
    async handleExport(intent) {
        if (!this.currentDesign) {
            this.showError('No design to export. Create one first.');
            return;
        }

        // Determine export format
        const format = intent.rawText.match(/stl|dxf|json|svg/i)?.[0]?.toLowerCase() || 'json';

        this.showSuggestion(`Exporting as ${format.toUpperCase()}...`);

        // Call appropriate export function
        await this.cadModule.exportDesign(format);

        this.showSuccess(`Exported as ${format.toUpperCase()}`);
    }

    /**
     * Show auto-suggestions as user types
     */
    showAutoSuggestions(text) {
        if (text.length < 3) return;

        const suggestions = [
            'Create a 500mm T-slot beam',
            'Make a 1 meter profile-6 extrusion',
            'Generate a 2020 aluminum beam 3 feet long',
            'Create a 40mm x 40mm frame member'
        ];

        // Filter based on input
        const filtered = suggestions.filter(s =>
            s.toLowerCase().includes(text.toLowerCase())
        );

        if (filtered.length > 0) {
            this.showContextualHelp(filtered[0], this.nlInput);
        }
    }

    /**
     * Show pre-execution suggestions
     */
    showPreExecutionSuggestions(intent) {
        const suggestions = [];

        if (intent.action === 'create') {
            suggestions.push('✓ Profile: ' + intent.params.profile);
            if (intent.params.dimensions.length) {
                suggestions.push('✓ Length: ' + (intent.params.dimensions.length * 1000) + 'mm');
            }
            if (intent.params.material) {
                suggestions.push('✓ Material: ' + intent.params.material);
            }
        }

        if (suggestions.length > 0) {
            this.showSuggestions(suggestions);
        }
    }

    /**
     * Show suggestions panel
     */
    showSuggestions(suggestions) {
        const content = document.getElementById('suggestion-content');
        content.innerHTML = suggestions.map(s =>
            `<div style="padding: 8px; margin: 4px 0; background: rgba(76, 175, 80, 0.2); border-left: 3px solid #4CAF50; border-radius: 4px;">${s}</div>`
        ).join('');

        this.suggestionPanel.style.display = 'block';
    }

    /**
     * Show single suggestion
     */
    showSuggestion(text) {
        this.showSuggestions([text]);
    }

    /**
     * Show contextual help tooltip
     */
    showContextualHelp(text, element) {
        const rect = element.getBoundingClientRect();

        this.contextualTooltip.textContent = text;
        this.contextualTooltip.style.display = 'block';
        this.contextualTooltip.style.left = rect.left + 'px';
        this.contextualTooltip.style.top = (rect.bottom + 8) + 'px';

        // Auto-hide after 3 seconds
        setTimeout(() => {
            this.contextualTooltip.style.display = 'none';
        }, 3000);
    }

    /**
     * Show lint errors
     */
    showLintErrors(lintResult) {
        document.getElementById('error-message').textContent =
            lintResult.errors[0] || 'Validation failed';

        const suggestionsHtml = lintResult.errors.map((err, i) =>
            `<div style="color: white; font-size: 12px; margin: 4px 0;">• ${err}</div>`
        ).join('');

        document.getElementById('error-suggestions').innerHTML = suggestionsHtml;
        this.errorPanel.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.errorPanel.style.display = 'none';
        }, 5000);
    }

    /**
     * Show lint warnings
     */
    showLintWarnings(lintResult) {
        this.showSuggestions(
            lintResult.warnings.map(w => '⚠️ ' + w)
        );
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        this.showSuggestion('✅ ' + message);
    }

    /**
     * Show error
     */
    showError(message) {
        document.getElementById('error-message').textContent = message;
        document.getElementById('error-suggestions').innerHTML = '';
        this.errorPanel.style.display = 'block';
    }

    /**
     * Handle error with recovery suggestions
     */
    handleError(error) {
        console.error('[AI UX] Error:', error);
        this.recentErrors.push(error);

        const recovery = this.suggestErrorRecovery(error);

        document.getElementById('error-message').textContent = error.message;
        document.getElementById('error-suggestions').innerHTML =
            recovery.map(r =>
                `<button onclick="this.executeRecovery('${r.action}')" style="background: white; color: #d32f2f; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; margin: 4px; font-size: 12px;">${r.label}</button>`
            ).join('');

        this.errorPanel.style.display = 'block';
    }

    /**
     * Suggest error recovery actions
     */
    suggestErrorRecovery(error) {
        const recoveryActions = [];

        if (error.message.includes('dimension')) {
            recoveryActions.push({
                action: 'reset_dimensions',
                label: 'Use default dimensions'
            });
        }

        if (error.message.includes('camera')) {
            recoveryActions.push({
                action: 'reset_camera',
                label: 'Reset camera to isometric view'
            });
        }

        recoveryActions.push({
            action: 'retry',
            label: 'Try again'
        });

        return recoveryActions;
    }

    /**
     * Calculate design statistics
     */
    calculateStats(design) {
        const model3d = design.model3D;
        const dims = model3d.dimensions || {};

        return {
            volume: (dims.width || 0.02) * (dims.height || 0.02) * (model3d.length || 0.5),
            surfaceArea: 2 * ((dims.width * dims.height) + (dims.width * model3d.length) + (dims.height * model3d.length)),
            weight: 'TBD'  // Would need material density
        };
    }

    /**
     * Show analysis results
     */
    showAnalysisResults(analysis) {
        const results = [
            `Status: ${analysis.valid ? '✅ Valid' : '❌ Invalid'}`,
            `Errors: ${analysis.errors.length}`,
            `Warnings: ${analysis.warnings.length}`,
            `Volume: ${(analysis.stats.volume * 1e9).toFixed(2)} cm³`,
            `Surface Area: ${(analysis.stats.surfaceArea * 1e4).toFixed(2)} cm²`
        ];

        this.showSuggestions(results);
    }

    /**
     * Show processing indicator
     */
    showProcessing(show) {
        const submit = document.getElementById('nl-submit');
        if (show) {
            submit.textContent = '⏳ Processing...';
            submit.disabled = true;
        } else {
            submit.textContent = 'Generate';
            submit.disabled = false;
        }
    }
}

// Export
window.AICADExperience = AICADExperience;

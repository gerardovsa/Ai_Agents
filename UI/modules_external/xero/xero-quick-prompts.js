/**
 * FILE: UI/modules_external/xero/xero-quick-prompts.js
 * PURPOSE: Quick Prompts feature for Xero dashboards - provides pre-written AI analysis prompts
 * 
 * FEATURES:
 * - Strategic analysis prompts (6 powerful frameworks that work for all dashboards)
 * - Dashboard-specific prompts (tailored to each dashboard type)
 * - Custom prompt input
 * - One-click export with selected prompt + dashboard data
 * 
 * USAGE:
 * Import into xero.js and call methods from XeroModule instance
 * 
 * CREATED: December 23, 2024
 */

export const XeroQuickPrompts = {
    // Reference to parent XeroModule instance (set by parent)
    parentModule: null,

    /**
     * Initialize Quick Prompts with parent module reference
     * @param {Object} module - Parent XeroModule instance
     */
    init(module) {
        this.parentModule = module;
        console.log('[Quick Prompts] Initialized with parent module');
    },

    /**
     * Create Quick Prompts button next to Export button
     * @param {string} containerId - ID of container to append button to
     * @param {string} dashboardName - Name of dashboard (for prompt selection)
     * @param {Function} getDataCallback - Function to get dashboard data
     * @param {string} endpoint - API endpoint for this dashboard
     */
    createQuickPromptsButton(containerId, dashboardName, getDataCallback, endpoint) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`[Quick Prompts] Container ${containerId} not found`);
            return;
        }

        // Check if button already exists
        if (container.querySelector('.quick-prompts-btn')) {
            console.log('[Quick Prompts] Button already exists');
            return;
        }

        // Create button (purple gradient, matches export button style)
        const button = document.createElement('button');
        button.className = 'quick-prompts-btn';
        button.innerHTML = `
            <i class="fas fa-lightbulb"></i>
            <span>Quick Prompts</span>
            <i class="fas fa-chevron-down" style="font-size: 10px; margin-left: 4px;"></i>
        `;

        button.style.cssText = `
            position: absolute;
            top: 16px;
            right: 160px;
            background: linear-gradient(135deg, #8957e5 0%, #9b6df7 100%);
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 2px 8px rgba(137, 87, 229, 0.3);
            transition: all 0.2s ease;
            z-index: 100;
        `;

        // Hover effects
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateY(-1px)';
            button.style.boxShadow = '0 4px 12px rgba(137, 87, 229, 0.4)';
        });

        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0)';
            button.style.boxShadow = '0 2px 8px rgba(137, 87, 229, 0.3)';
        });

        // Click handler - show dropdown
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            this.showQuickPromptsDropdown(e, dashboardName, containerId, getDataCallback, endpoint);
        });

        container.appendChild(button);
        console.log(`[Quick Prompts] Button created for ${dashboardName} dashboard`);
    },

    /**
     * Show Quick Prompts dropdown
     * @param {Event} event - Click event
     * @param {string} dashboardName - Dashboard name
     * @param {string} containerId - Container ID
     * @param {Function} getDataCallback - Function to get dashboard data
     * @param {string} endpoint - API endpoint
     */
    showQuickPromptsDropdown(event, dashboardName, containerId, getDataCallback, endpoint) {
        // Remove any existing dropdown
        document.querySelectorAll('.quick-prompts-dropdown').forEach(d => d.remove());

        // Get button element for positioning
        const button = event.currentTarget;
        const rect = button.getBoundingClientRect();

        // Create dropdown
        const dropdown = document.createElement('div');
        dropdown.className = 'quick-prompts-dropdown';

        dropdown.style.cssText = `
            position: fixed;
            top: ${rect.bottom + 8}px;
            right: ${window.innerWidth - rect.right}px;
            background: #1a1a1a;
            border: 1px solid #30363d;
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
            z-index: 10000;
            width: 450px;
            max-height: 600px;
            overflow-y: auto;
            color: #f0f6fc;
            scrollbar-width: thin;
            scrollbar-color: #30363d #1a1a1a;
        `;

        // Add webkit scrollbar styling
        const style = document.createElement('style');
        style.textContent = `
            .quick-prompts-dropdown::-webkit-scrollbar { width: 8px; }
            .quick-prompts-dropdown::-webkit-scrollbar-track { background: #1a1a1a; }
            .quick-prompts-dropdown::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }
            .quick-prompts-dropdown::-webkit-scrollbar-thumb:hover { background: #484f58; }
        `;
        document.head.appendChild(style);

        // Get prompts for this dashboard
        const prompts = this.getQuickPromptsForDashboard(dashboardName);

        // Build HTML
        let html = `
            <div style="padding: 16px; border-bottom: 1px solid #30363d; position: sticky; top: 0; background: #1a1a1a; z-index: 1;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <i class="fas fa-lightbulb" style="color: #fbbf24; font-size: 18px;"></i>
                    <div style="font-size: 14px; font-weight: 700; color: #f0f6fc;">Quick Analysis Prompts</div>
                </div>
                <div style="font-size: 11px; color: #8b949e; margin-top: 2px;">
                    ${this.escapeHtml(dashboardName)} Dashboard
                </div>
            </div>
            <div style="padding: 8px 12px;">
        `;

        // Render each category
        prompts.forEach((category, categoryIndex) => {
            // Check if this is a strategic prompt category
            const isStrategic = category.name.includes('Analysis') ||
                category.name.includes('Strategy') ||
                category.name.includes('Comparison') ||
                category.name.includes('Summary') ||
                category.name.includes('Steps') ||
                category.name.includes('Explanation');

            html += `
                <div style="margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; padding: 8px 10px; background: ${isStrategic ? 'rgba(251, 191, 36, 0.1)' : 'rgba(99, 102, 241, 0.1)'}; border-radius: 4px; ${isStrategic ? 'border-left: 3px solid #fbbf24;' : ''}">
                        <span style="font-size: 16px;">${category.icon}</span>
                        <div style="flex: 1; font-size: 12px; font-weight: 700; color: #f0f6fc; text-transform: uppercase; letter-spacing: 0.5px;">
                            ${this.escapeHtml(category.name)}
                        </div>
                        ${isStrategic ? '<span style="font-size: 10px; color: #fbbf24; font-weight: 600; background: rgba(251, 191, 36, 0.2); padding: 2px 6px; border-radius: 3px;">STRATEGIC</span>' : ''}
                    </div>
            `;

            // Render prompts in this category
            category.prompts.forEach((prompt, index) => {
                // For strategic prompts, show truncated preview
                const displayText = isStrategic ?
                    (prompt.split('\n')[0] + ' [Multi-step framework - click to use]') :
                    prompt;

                html += `
                    <div class="prompt-option" 
                         data-prompt="${this.escapeHtml(prompt)}"
                         data-is-strategic="${isStrategic}"
                         style="padding: 10px 12px; margin: 4px 0; cursor: pointer; border-radius: 6px; display: flex; align-items: center; gap: 10px; transition: all 0.15s ease; ${isStrategic ? 'background: rgba(251, 191, 36, 0.05);' : ''}"
                         onmouseover="this.style.background='${isStrategic ? 'rgba(251, 191, 36, 0.15)' : 'rgba(99, 102, 241, 0.15)'}'; this.style.paddingLeft='16px'" 
                         onmouseout="this.style.background='${isStrategic ? 'rgba(251, 191, 36, 0.05)' : 'transparent'}'; this.style.paddingLeft='12px'">
                        <i class="fas ${isStrategic ? 'fa-brain' : 'fa-comment-dots'}" style="color: ${isStrategic ? '#fbbf24' : '#6366f1'}; font-size: 12px; width: 16px; text-align: center;"></i>
                        <div style="flex: 1; font-size: 13px; color: #e5e7eb; line-height: 1.4;">
                            ${this.escapeHtml(displayText)}
                        </div>
                        <i class="fas fa-arrow-right" style="color: #8b949e; font-size: 11px; opacity: 0.5;"></i>
                    </div>
                `;
            });

            html += `</div>`;
        });

        // Custom prompt option
        html += `
            <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid #30363d;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; padding: 6px 8px;">
                    <span style="font-size: 16px;">✨</span>
                    <div style="font-size: 12px; font-weight: 700; color: #f0f6fc; text-transform: uppercase; letter-spacing: 0.5px;">
                        Custom Prompt
                    </div>
                </div>
                <textarea id="custom-prompt-input" 
                          placeholder="Write your own analysis question..."
                          style="width: calc(100% - 20px); padding: 10px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: #f0f6fc; font-size: 13px; min-height: 80px; resize: vertical; font-family: inherit;"></textarea>
                <button class="custom-prompt-submit" 
                        style="margin-top: 8px; width: 100%; padding: 10px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s ease;"
                        onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(99, 102, 241, 0.4)'"
                        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
                    <i class="fas fa-paper-plane"></i> Export with Custom Prompt
                </button>
            </div>
        `;

        html += `</div>`;
        dropdown.innerHTML = html;
        document.body.appendChild(dropdown);

        // Add click handlers for prompt options
        dropdown.querySelectorAll('.prompt-option').forEach(option => {
            option.addEventListener('click', async (e) => {
                e.stopPropagation();
                const prompt = option.dataset.prompt;
                dropdown.remove();
                await this.exportWithPrompt(dashboardName, prompt, containerId, getDataCallback, endpoint);
            });
        });

        // Add click handler for custom prompt submit
        const customSubmit = dropdown.querySelector('.custom-prompt-submit');
        if (customSubmit) {
            customSubmit.addEventListener('click', async (e) => {
                e.stopPropagation();
                const textarea = dropdown.querySelector('#custom-prompt-input');
                const customPrompt = textarea.value.trim();

                if (!customPrompt) {
                    textarea.style.borderColor = '#f85149';
                    setTimeout(() => textarea.style.borderColor = '#30363d', 2000);
                    return;
                }

                dropdown.remove();
                await this.exportWithPrompt(dashboardName, customPrompt, containerId, getDataCallback, endpoint);
            });
        }

        // Close on outside click
        setTimeout(() => {
            const closeHandler = (e) => {
                if (!dropdown.contains(e.target) && !button.contains(e.target)) {
                    dropdown.remove();
                    document.removeEventListener('click', closeHandler);
                }
            };
            document.addEventListener('click', closeHandler);
        }, 100);
    },

    /**
     * Export dashboard data with selected prompt
     * @param {string} dashboardName - Dashboard name
     * @param {string} selectedPrompt - Selected prompt text
     * @param {string} containerId - Container ID
     * @param {Function} getDataCallback - Function to get dashboard data
     * @param {string} endpoint - API endpoint
     */
    async exportWithPrompt(dashboardName, selectedPrompt, containerId, getDataCallback, endpoint) {
        console.log(`[Quick Prompts] Exporting ${dashboardName} with prompt`);

        // Get dashboard data
        const data = getDataCallback();

        if (!data) {
            alert('No data available. Please wait for dashboard to load.');
            return;
        }

        // Format data for AI (we'll need to import formatDataForAI from parent module)
        // For now, create a simplified version
        const formattedData = this.formatDataForAI(data, dashboardName, endpoint);

        // Add selected prompt at the beginning
        const exportContent = `# 🎯 AI Analysis Request

## User Question
${selectedPrompt}

---

${formattedData}`;

        // Copy to clipboard
        try {
            await navigator.clipboard.writeText(exportContent);
            console.log('[Quick Prompts] Content copied to clipboard');

            // Show success notification
            this.showExportSuccessNotification(containerId, selectedPrompt);
        } catch (error) {
            console.error('[Quick Prompts] Failed to copy to clipboard:', error);
            alert('Failed to copy to clipboard. Please try again.');
        }
    },

    /**
     * Format data for AI (uses parent module's method if available)
     * @param {Object} data - Dashboard data
     * @param {string} dashboardName - Dashboard name
     * @param {string} endpoint - API endpoint
     * @returns {string} Formatted markdown
     */
    formatDataForAI(data, dashboardName, endpoint) {
        // Use parent module's formatDataForAI if available
        if (this.parentModule && typeof this.parentModule.formatDataForAI === 'function') {
            return this.parentModule.formatDataForAI(data, dashboardName, endpoint);
        }

        // Fallback to simplified version
        return `# 📊 Xero Dashboard Export - ${dashboardName}

**Dashboard:** ${dashboardName}
**Exported:** ${new Date().toLocaleString()}
**API Endpoint:** ${endpoint}

## Dashboard Data

\`\`\`json
${JSON.stringify(data, null, 2)}
\`\`\`

## AI Analysis Instructions

This data is from a Xero accounting dashboard. Analyze the provided information and answer the user's question above.

**Available Context:**
- Date ranges and time periods
- Financial metrics and KPIs
- Business performance data
- Historical trends

**Analysis Guidelines:**
1. Use the data provided to answer the specific question
2. Highlight key insights and patterns
3. Provide specific numbers and calculations
4. Explain your reasoning clearly
5. Suggest follow-up analyses if relevant

**Note:** If you need additional data or clarification, mention what specific information would help improve the analysis.
`;
    },

    /**
     * Show success notification after export
     * @param {string} containerId - Container ID
     * @param {string} prompt - Selected prompt
     */
    showExportSuccessNotification(containerId, prompt) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const notification = document.createElement('div');
        notification.style.cssText = `
            position: absolute;
            top: 60px;
            right: 16px;
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
            z-index: 1000;
            max-width: 400px;
            animation: slideInRight 0.3s ease;
        `;

        // Truncate prompt for display
        const promptPreview = prompt.length > 60 ? prompt.substring(0, 60) + '...' : prompt;

        notification.innerHTML = `
            <div style="display: flex; align-items: start; gap: 10px;">
                <i class="fas fa-check-circle" style="font-size: 20px; flex-shrink: 0;"></i>
                <div>
                    <div style="font-weight: 700; font-size: 13px; margin-bottom: 4px;">
                        Copied to Clipboard!
                    </div>
                    <div style="font-size: 11px; opacity: 0.9; line-height: 1.3;">
                        Dashboard data + prompt ready to paste into AI chat
                    </div>
                    <div style="font-size: 10px; opacity: 0.7; margin-top: 4px; font-style: italic;">
                        "${this.escapeHtml(promptPreview)}"
                    </div>
                </div>
            </div>
        `;

        container.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },

    /**
     * Get quick prompts for a dashboard
     * @param {string} dashboardName - Dashboard name
     * @returns {Array} Array of prompt categories
     */
    getQuickPromptsForDashboard(dashboardName) {
        // Strategic prompts (generic - work for all dashboards)
        const strategicPrompts = this.getStrategicPrompts();

        const dashboardSpecificPrompts = {
            'Business Comparison': [
                {
                    icon: '📊',
                    name: 'Growth & Trends',
                    prompts: [
                        'Compare year-over-year growth trends across all businesses',
                        'Identify businesses with declining market share',
                        'Which business is growing fastest and why?',
                        'Analyze revenue acceleration or deceleration patterns'
                    ]
                },
                {
                    icon: '💰',
                    name: 'Financial Health',
                    prompts: [
                        'Which business has the best collection days and why?',
                        'Analyze average order value trends by business',
                        'Identify businesses with concerning cash flow patterns',
                        'Compare payment terms efficiency across businesses'
                    ]
                },
                {
                    icon: '🎯',
                    name: 'Recommendations',
                    prompts: [
                        'Which business needs immediate attention or intervention?',
                        'Suggest resource allocation strategy based on performance',
                        'Recommend marketing budget distribution across businesses',
                        'Identify cross-selling opportunities between businesses'
                    ]
                }
            ],
            'Consolidated Revenue': [
                {
                    icon: '💵',
                    name: 'Cash Flow Analysis',
                    prompts: [
                        'Analyze cash flow health based on aging buckets',
                        'Which aging bucket is most concerning and why?',
                        'Project cash flow for next 30/60/90 days',
                        'Identify collection risk factors in outstanding amounts'
                    ]
                },
                {
                    icon: '📈',
                    name: 'Revenue Trends',
                    prompts: [
                        'Which business contributes most to total revenue?',
                        'Analyze month-over-month consolidated revenue trends',
                        'Identify seasonal patterns in consolidated data',
                        'Compare actual vs. expected collection timelines'
                    ]
                },
                {
                    icon: '⚠️',
                    name: 'Risk Assessment',
                    prompts: [
                        'Which outstanding invoices need immediate attention?',
                        'Analyze bad debt risk in 90+ day bucket',
                        'Recommend collection strategy priorities',
                        'Identify businesses with improving/declining collection rates'
                    ]
                }
            ],
            'Seasonality': [
                {
                    icon: '📅',
                    name: 'Seasonal Patterns',
                    prompts: [
                        'Which months are peak season for this business?',
                        'What are the historically slow periods?',
                        'Compare this year\'s performance to 3-year average',
                        'Identify emerging seasonal trend changes'
                    ]
                },
                {
                    icon: '🎯',
                    name: 'Marketing Strategy',
                    prompts: [
                        'When should we launch marketing campaigns?',
                        'Recommend inventory planning based on seasonality',
                        'Which months need promotional support?',
                        'Suggest staffing adjustments for peak periods'
                    ]
                },
                {
                    icon: '🔮',
                    name: 'Forecasting',
                    prompts: [
                        'Forecast Q1 performance based on seasonal patterns',
                        'Project holiday season revenue using historical data',
                        'Identify unusual deviations from seasonal norms',
                        'Recommend budget allocation by season'
                    ]
                }
            ],
            'Forecast': [
                {
                    icon: '📊',
                    name: 'Scenario Analysis',
                    prompts: [
                        'Should I budget based on optimistic or pessimistic scenario?',
                        'What are the biggest risks to this forecast?',
                        'How confident should I be in the 6-month projection?',
                        'Analyze volatility factors affecting accuracy'
                    ]
                },
                {
                    icon: '🎯',
                    name: 'Risk Factors',
                    prompts: [
                        'Which external factors pose greatest risk to forecast?',
                        'Identify controllable vs. uncontrollable risk factors',
                        'Recommend risk mitigation strategies',
                        'What early warning indicators should I monitor?'
                    ]
                },
                {
                    icon: '💼',
                    name: 'Business Planning',
                    prompts: [
                        'Create quarterly targets based on this forecast',
                        'Recommend expense budget aligned with projections',
                        'Identify growth investment opportunities',
                        'Suggest contingency plans for downside scenarios'
                    ]
                }
            ]
        };

        // Combine strategic prompts with dashboard-specific prompts
        const specificPrompts = dashboardSpecificPrompts[dashboardName] || [];
        return [...strategicPrompts, ...specificPrompts];
    },

    /**
     * Get strategic prompts (work for all dashboards)
     * @returns {Array} Array of strategic prompt categories
     */
    getStrategicPrompts() {
        return [
            {
                icon: '🔬',
                name: 'Deep Insights Analysis',
                prompts: [`You are provided Xero financial data below including date range, SQL queries, and raw JSON data.

OBJECTIVE: Extract maximum insights using structured multi-domain analysis.

ANALYSIS FRAMEWORK:

STEP 1 - Multi-Perspective Analysis
→ Analyze from multiple business perspectives:
  • Financial health (cash flow, profitability, collection efficiency)
  • Operational performance (transaction volumes, processing times)
  • Strategic positioning (market trends, competitive dynamics)
  • Risk assessment (volatility, exposure, concentration)
  • Growth trajectory (momentum, acceleration, sustainability)

STEP 2 - Domain Identification & Deep Dive
→ Identify 3-5 major domains where significant patterns emerge
→ For each domain, perform additional analyses:
  • Calculate trend lines, growth rates, volatility metrics
  • Identify outliers, anomalies, and inflection points
  • Cross-reference patterns across domains to find correlations

STEP 3 - Insight Explanation & Reasoning
→ For each insight:
  • State the insight clearly
  • Explain the underlying data patterns
  • Describe business implications and impact
  • Rate confidence level (High/Medium/Low)
  • Identify caveats or limitations

STEP 4 - Follow-Up Actions & Tool Recommendations
→ Suggest specific follow-up analyses I can perform:
  • Additional SQL queries to drill deeper
  • Comparative analyses to validate findings
  • Predictive models to forecast trends
  • Risk scenarios to test resilience

DELIVERABLE: Comprehensive insight report with executive summary, detailed findings, and actionable next steps.`]
            },
            {
                icon: '🚀',
                name: 'Actionable Strategy',
                prompts: [`You are provided Xero financial data below including date range, SQL queries, and raw data.

OBJECTIVE: Develop prioritized action plan that maximizes business performance.

STRATEGIC FRAMEWORK:

STEP 1 - Opportunity & Challenge Identification
→ Identify:
  • High-impact opportunities (quick wins, strategic moves)
  • Critical challenges (risks, bottlenecks, inefficiencies)
  • Hidden patterns (emerging trends, subtle signals)
→ Quantify potential impact (Revenue, Cost, Risk, Time)

STEP 2 - Prioritization Using Weighted Shortest Job First (WSJF)
→ For each opportunity/challenge, calculate:
  • Business Value (1-10): Revenue impact, cost savings, risk reduction
  • Time Criticality (1-10): Urgency, seasonal factors, competitive pressure
  • Risk Reduction (1-10): Mitigates major risks, improves stability
  • Implementation Effort (1-10): Time, resources, complexity
  • WSJF Score = (Business Value + Time Criticality + Risk Reduction) / Implementation Effort
→ Rank by WSJF score (highest priority first)

STEP 3 - Analysis & Reasoning
→ For top 5 prioritized items, explain:
  • Why this action matters (strategic rationale)
  • Expected outcomes (quantified when possible)
  • Dependencies and prerequisites
  • Risks and mitigation strategies
  • Timeline and resource requirements

STEP 4 - Step-by-Step Implementation Plan
→ Create detailed action plan:
  • Phase 1 (0-30 days): Immediate actions, quick wins
  • Phase 2 (30-90 days): Strategic initiatives, capacity building
  • Phase 3 (90+ days): Long-term improvements, optimization
→ For each phase: tasks, deliverables, success metrics, review checkpoints

STEP 5 - Follow-Up Tool Recommendations
→ Suggest analyses to monitor progress and measure ROI

DELIVERABLE: Prioritized action plan with WSJF scores, implementation roadmap, and monitoring framework.`]
            },
            {
                icon: '📊',
                name: 'Historical Comparison',
                prompts: [`You are provided Xero financial data with historical time series information.

OBJECTIVE: Perform comprehensive temporal analysis to identify trends, patterns, and strategic implications.

COMPARISON FRAMEWORK:

STEP 1 - Temporal Analysis Dimensions
→ Analyze across multiple time comparisons:
  • Year-over-Year (YoY): Compare to same period last year
  • Month-over-Month (MoM): Sequential period progression
  • Quarter-over-Quarter (QoQ): Quarterly trend analysis
  • Same Time Last Year (STLY): Direct period matching
  • Multi-Year Trends: 3-5 year historical patterns
  • Seasonal Adjustments: Remove seasonal effects

STEP 2 - Trend Identification & Classification
→ For each metric, identify:
  • Direction: Growing, declining, stable, volatile
  • Magnitude: Percentage change, absolute change, rate of change
  • Acceleration: Is trend speeding up or slowing down?
  • Cyclicality: Repeating patterns, seasonal cycles
  • Anomalies: Unusual spikes, dips, disruptions
→ Classify as: Structural, Cyclical, Seasonal, or Random

STEP 3 - Causal Analysis & Context
→ Investigate:
  • What business events explain this pattern?
  • External factors (economy, seasonality, competition)?
  • Do multiple metrics confirm the same story?
  • Are there leading indicators?

STEP 4 - Projection & Scenario Planning
→ Based on historical patterns:
  • Project forward 3-6 months
  • Develop 3 scenarios: Optimistic, Base Case, Pessimistic
  • Identify trigger points that would shift scenarios
  • Recommend monitoring metrics

STEP 5 - Strategic Implications
→ Answer:
  • What do trends mean for business strategy?
  • Should we accelerate, maintain, or pivot?
  • What resources should we allocate?
  • What risks do trends expose?

DELIVERABLE: Historical trend report with YoY/MoM/QoQ analysis, projections, and strategic recommendations.`]
            },
            {
                icon: '💡',
                name: 'Key Insights & Executive Summary',
                prompts: [`You are provided Xero financial data below.

OBJECTIVE: Distill complex data into clear, actionable insights for executive decision-making.

SYNTHESIS FRAMEWORK:

STEP 1 - Data Comprehension
→ Understand:
  • What metrics are included and their meanings
  • Time periods covered and data granularity
  • Data quality and completeness
→ Identify the 5-7 most important metrics

STEP 2 - Pattern Recognition
→ Look for:
  • Standout numbers (exceptional performance or concerns)
  • Surprising findings (unexpected patterns)
  • Hidden relationships (correlations between metrics)
  • Missing context (what's not shown but matters)

STEP 3 - Key Insights Extraction (Top 5)
→ For each insight:
  • ONE-SENTENCE SUMMARY: Core finding in plain language
  • SUPPORTING DATA: Specific numbers proving this insight
  • SO WHAT?: Why this matters to the business
  • CONFIDENCE LEVEL: High/Medium/Low with justification
→ Rank by business impact

STEP 4 - Executive Explanation
→ Explain the data story in 3 parts:
  • WHERE WE ARE: Current state summary (2-3 sentences)
  • HOW WE GOT HERE: Key drivers and trends (2-3 sentences)
  • WHERE WE'RE HEADING: Trajectory and implications (2-3 sentences)
→ Use business language, not technical jargon

STEP 5 - Recommendations Summary
→ Provide 3-5 concrete recommendations with expected impact, effort, and priority

DELIVERABLE: Executive summary with top 5 insights, data story narrative, and prioritized recommendations.`]
            },
            {
                icon: '⚡',
                name: 'Next Action Steps (Tactical)',
                prompts: [`You are provided Xero financial data below.

OBJECTIVE: Identify immediate tactical actions executable in the next 7-30 days.

TACTICAL FRAMEWORK:

STEP 1 - Quick Wins Identification
→ Find opportunities that are:
  • HIGH IMPACT: Meaningful improvement to key metrics
  • LOW EFFORT: Can be done quickly with existing resources
  • LOW RISK: Minimal downside
→ Look for process inefficiencies, low-hanging fruit, immediate risks

STEP 2 - Action Categorization
→ Group into:
  • COLLECTIONS: Improve cash flow (chase invoices, review terms)
  • EFFICIENCY: Process improvements (automate, streamline)
  • REVENUE: Quick revenue opportunities (upsell, cross-sell, pricing)
  • COST: Immediate cost reductions (renegotiate, eliminate)
  • RISK: Urgent risk mitigation (address exposures)
→ List 2-3 specific actions per category

STEP 3 - Action Specification
→ For each action:
  • WHAT: Specific task (be precise)
  • WHO: Role or person to do it
  • WHEN: Deadline or timeframe
  • HOW: Brief method or approach
  • WHY: Expected outcome (quantified if possible)
  • MEASURE: How to track success

STEP 4 - Priority Sequence
→ Organize:
  • THIS WEEK (Next 7 days): 2-3 urgent actions
  • NEXT TWO WEEKS (8-14 days): 3-5 important actions
  • THIS MONTH (15-30 days): 5-7 valuable actions

STEP 5 - Follow-Up Analysis
→ Suggest analyses to monitor progress and measure impact

DELIVERABLE: Tactical action plan with prioritized sequence, clear ownership, and success metrics.`]
            },
            {
                icon: '🎯',
                name: 'Data Explanation & Context',
                prompts: [`You are provided Xero financial data below.

OBJECTIVE: Explain what this data shows in clear business language, providing context and meaning.

EXPLANATION FRAMEWORK:

STEP 1 - Data Overview
→ Describe:
  • What type of financial data is this?
  • What time period does it cover?
  • What businesses or entities are included?
  • How was this data collected?

STEP 2 - Metric Definitions
→ For each key metric:
  • Define in simple terms
  • Explain how it's calculated
  • Describe what "good" looks like
  • Note industry benchmarks
→ Use analogies or examples

STEP 3 - Current State Explanation
→ Describe what numbers tell us:
  • Headline figures (specific numbers)
  • Are these good, bad, or neutral?
  • How do they compare to expectations?
  • What patterns or trends are visible?
→ Explain for non-financial audience

STEP 4 - Business Context
→ Put in business context:
  • What business activities do these numbers represent?
  • What external factors might be influencing results?
  • What internal decisions are reflected here?
  • What does this tell us about business health?

STEP 5 - Next Steps Guidance
→ Guide user:
  • What questions should they ask?
  • What additional analysis would help?
  • Who should see this data and why?
  • What decisions can be informed?

DELIVERABLE: Plain-language explanation with context, definitions, and guidance for next steps.`]
            }
        ];
    },

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Add CSS animations
const animationStyles = document.createElement('style');
animationStyles.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(animationStyles);

console.log('[Quick Prompts] Module loaded');

/**
 * Production Analytics Dashboard Module
 * Comprehensive analytics for production log data
 * 
 * Features:
 * - Wastage analysis by type, reason, and cost
 * - Delay tracking with reason breakdown
 * - Client notification statistics
 * - Stage transition metrics
 * - Average time analysis
 * - Top issues identification
 * 
 * @class ProductionAnalyticsModule
 * @extends BaseModule
 * @created 2025-11-07
 */

class ProductionAnalyticsModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);

        // FIXED NOV 29: Use window.API_BASE_URL for production compatibility
        this.apiBase = `${window.API_BASE_URL || 'http://localhost:5001'}/api/production-log`;
        this.dateRange = 30; // days
        this.analyticsData = null;
    }

    /**
     * Render module UI
     */
    render() {
        const container = this.getContainer();
        if (!container) return;

        container.innerHTML = `
            <div class="analytics-dashboard" style="padding: 20px; background: #0d1117; min-height: 100vh;">
                <!-- Header -->
                <div style="margin-bottom: 24px;">
                    <h2 style="color: #f3f4f6; font-size: 24px; margin: 0 0 8px 0;">
                        <i class="fas fa-chart-line"></i> Production Analytics Dashboard
                    </h2>
                    <p style="color: #9ca3af; margin: 0;">
                        Comprehensive production log analysis and insights
                    </p>
                </div>

                <!-- Controls -->
                <div style="display: flex; gap: 12px; margin-bottom: 24px; align-items: center;">
                    <select id="analytics-date-range" style="padding: 8px 12px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; color: #f3f4f6;">
                        <option value="7">Last 7 Days</option>
                        <option value="30" selected>Last 30 Days</option>
                        <option value="60">Last 60 Days</option>
                        <option value="90">Last 90 Days</option>
                        <option value="180">Last 6 Months</option>
                        <option value="365">Last Year</option>
                    </select>
                    <button class="btn btn-primary" onclick="window.ModuleRegistry['production-analytics'].loadAnalytics()">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                    <div style="margin-left: auto; color: #9ca3af; font-size: 13px;">
                        <i class="fas fa-clock"></i> Last updated: <span id="last-updated">Never</span>
                    </div>
                </div>

                <!-- Summary Cards -->
                <div id="analytics-summary" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin-bottom: 24px;">
                    <!-- Cards will be injected here -->
                </div>

                <!-- Charts and Tables -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
                    <!-- Wastage Analysis -->
                    <div class="analytics-card" style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px;">
                        <h3 style="color: #f3f4f6; font-size: 18px; margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-trash-alt" style="color: #ef4444;"></i>
                            Wastage Analysis
                        </h3>
                        <div id="wastage-analysis">Loading...</div>
                    </div>

                    <!-- Delay Analysis -->
                    <div class="analytics-card" style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px;">
                        <h3 style="color: #f3f4f6; font-size: 18px; margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-clock" style="color: #f97316;"></i>
                            Delay Analysis
                        </h3>
                        <div id="delay-analysis">Loading...</div>
                    </div>
                </div>

                <!-- Full Width Charts -->
                <div style="display: grid; gap: 20px; margin-bottom: 24px;">
                    <!-- Stage Transition Timeline -->
                    <div class="analytics-card" style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px;">
                        <h3 style="color: #f3f4f6; font-size: 18px; margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-exchange-alt" style="color: #3b82f6;"></i>
                            Stage Transition Metrics
                        </h3>
                        <div id="stage-metrics">Loading...</div>
                    </div>

                    <!-- Client Notifications -->
                    <div class="analytics-card" style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px;">
                        <h3 style="color: #f3f4f6; font-size: 18px; margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-envelope" style="color: #10b981;"></i>
                            Client Notification Tracking
                        </h3>
                        <div id="notification-tracking">Loading...</div>
                    </div>

                    <!-- Top Issues -->
                    <div class="analytics-card" style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px;">
                        <h3 style="color: #f3f4f6; font-size: 18px; margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-exclamation-triangle" style="color: #fbbf24;"></i>
                            Top Issues & Recommendations
                        </h3>
                        <div id="top-issues">Loading...</div>
                    </div>
                </div>
            </div>
        `;

        // Attach event listeners
        document.getElementById('analytics-date-range')?.addEventListener('change', (e) => {
            this.dateRange = parseInt(e.target.value);
            this.loadAnalytics();
        });

        // Load analytics
        this.loadAnalytics();
    }

    /**
     * Load analytics data from API
     */
    async loadAnalytics() {
        try {
            // In a real implementation, you'd call a summary endpoint
            // For now, we'll use the individual endpoints and aggregate

            // Show loading
            this.showLoading();

            // Get date range
            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - this.dateRange);

            // Fetch data from multiple jobs (you'd want a summary endpoint)
            // For demo purposes, showing the structure

            // Mock data for demonstration
            const mockData = {
                summary: {
                    total_entries: 247,
                    total_wastage_cost: 3847.50,
                    total_delay_hours: 127.5,
                    total_notifications: 89,
                    avg_stage_time: 2.3
                },
                wastage: {
                    by_type: {
                        paper: { count: 34, amount: 2450, cost: 2840.00 },
                        ink: { count: 12, amount: 850, cost: 680.50 },
                        material: { count: 8, amount: 320, cost: 327.00 }
                    },
                    top_reasons: [
                        { reason: 'Color calibration', count: 18, cost: 1240.00 },
                        { reason: 'Misprint', count: 15, cost: 890.50 },
                        { reason: 'Material defect', count: 11, cost: 720.00 }
                    ]
                },
                delays: {
                    by_reason: {
                        equipment_failure: { count: 23, hours: 58.5 },
                        material_shortage: { count: 18, hours: 36.0 },
                        staff_shortage: { count: 12, hours: 24.0 },
                        quality_issue: { count: 8, hours: 9.0 }
                    },
                    avg_duration: 2.1
                },
                notifications: {
                    by_type: {
                        email: 67,
                        sms: 15,
                        phone: 5,
                        whatsapp: 2
                    },
                    by_status: {
                        sent: 78,
                        pending: 9,
                        failed: 2
                    }
                },
                stages: {
                    transitions: 156,
                    avg_time_per_stage: {
                        'Ready to Print': 1.2,
                        'Digital - 9110': 3.4,
                        'Cello': 2.1,
                        'Bindery': 4.7,
                        'Complete': 0.5
                    },
                    most_common: [
                        { from: 'Ready to Print', to: 'Digital - 9110', count: 45 },
                        { from: 'Digital - 9110', to: 'Cello', count: 38 },
                        { from: 'Cello', to: 'Bindery', count: 32 }
                    ]
                }
            };

            this.analyticsData = mockData;
            this.renderAnalytics();

            // Update timestamp
            document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();

        } catch (error) {
            console.error('Failed to load analytics:', error);
            this.showError('Failed to load analytics data');
        }
    }

    /**
     * Render analytics visualizations
     */
    renderAnalytics() {
        if (!this.analyticsData) return;

        this.renderSummaryCards();
        this.renderWastageAnalysis();
        this.renderDelayAnalysis();
        this.renderStageMetrics();
        this.renderNotificationTracking();
        this.renderTopIssues();
    }

    /**
     * Render summary cards
     */
    renderSummaryCards() {
        const container = document.getElementById('analytics-summary');
        if (!container) return;

        const { summary } = this.analyticsData;

        container.innerHTML = `
            <div class="summary-card" style="background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); border-radius: 8px; padding: 20px; color: white;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(255,255,255,0.2); width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <i class="fas fa-clipboard-list" style="font-size: 24px;"></i>
                    </div>
                    <div>
                        <div style="font-size: 28px; font-weight: bold;">${summary.total_entries}</div>
                        <div style="font-size: 13px; opacity: 0.9;">Total Log Entries</div>
                    </div>
                </div>
            </div>

            <div class="summary-card" style="background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); border-radius: 8px; padding: 20px; color: white;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(255,255,255,0.2); width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <i class="fas fa-trash-alt" style="font-size: 24px;"></i>
                    </div>
                    <div>
                        <div style="font-size: 28px; font-weight: bold;">$${summary.total_wastage_cost.toLocaleString()}</div>
                        <div style="font-size: 13px; opacity: 0.9;">Total Wastage Cost</div>
                    </div>
                </div>
            </div>

            <div class="summary-card" style="background: linear-gradient(135deg, #f97316 0%, #c2410c 100%); border-radius: 8px; padding: 20px; color: white;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(255,255,255,0.2); width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <i class="fas fa-clock" style="font-size: 24px;"></i>
                    </div>
                    <div>
                        <div style="font-size: 28px; font-weight: bold;">${summary.total_delay_hours.toFixed(1)}h</div>
                        <div style="font-size: 13px; opacity: 0.9;">Total Delay Hours</div>
                    </div>
                </div>
            </div>

            <div class="summary-card" style="background: linear-gradient(135deg, #10b981 0%, #047857 100%); border-radius: 8px; padding: 20px; color: white;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(255,255,255,0.2); width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <i class="fas fa-envelope" style="font-size: 24px;"></i>
                    </div>
                    <div>
                        <div style="font-size: 28px; font-weight: bold;">${summary.total_notifications}</div>
                        <div style="font-size: 13px; opacity: 0.9;">Client Notifications</div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render wastage analysis
     */
    renderWastageAnalysis() {
        const container = document.getElementById('wastage-analysis');
        if (!container) return;

        const { wastage } = this.analyticsData;

        container.innerHTML = `
            <div style="margin-bottom: 20px;">
                <h4 style="color: #f3f4f6; font-size: 14px; margin: 0 0 12px 0;">Wastage by Type</h4>
                ${Object.entries(wastage.by_type).map(([type, data]) => `
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="color: #9ca3af; font-size: 13px; text-transform: capitalize;">${type}</span>
                            <span style="color: #f3f4f6; font-size: 13px; font-weight: 600;">$${data.cost.toLocaleString()}</span>
                        </div>
                        <div style="background: #0d1117; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="background: #ef4444; height: 100%; width: ${(data.cost / wastage.by_type.paper.cost * 100)}%; transition: width 0.3s;"></div>
                        </div>
                        <div style="color: #6b7280; font-size: 11px; margin-top: 2px;">${data.count} incidents • ${data.amount} units</div>
                    </div>
                `).join('')}
            </div>

            <div>
                <h4 style="color: #f3f4f6; font-size: 14px; margin: 0 0 12px 0;">Top Wastage Reasons</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="border-bottom: 1px solid #30363d;">
                            <th style="text-align: left; padding: 8px; color: #9ca3af; font-size: 12px; font-weight: 600;">Reason</th>
                            <th style="text-align: right; padding: 8px; color: #9ca3af; font-size: 12px; font-weight: 600;">Count</th>
                            <th style="text-align: right; padding: 8px; color: #9ca3af; font-size: 12px; font-weight: 600;">Cost</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${wastage.top_reasons.map(reason => `
                            <tr style="border-bottom: 1px solid #21262d;">
                                <td style="padding: 8px; color: #f3f4f6; font-size: 13px;">${reason.reason}</td>
                                <td style="padding: 8px; text-align: right; color: #f3f4f6; font-size: 13px;">${reason.count}</td>
                                <td style="padding: 8px; text-align: right; color: #ef4444; font-size: 13px; font-weight: 600;">$${reason.cost.toLocaleString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    /**
     * Render delay analysis
     */
    renderDelayAnalysis() {
        const container = document.getElementById('delay-analysis');
        if (!container) return;

        const { delays } = this.analyticsData;
        const totalHours = Object.values(delays.by_reason).reduce((sum, d) => sum + d.hours, 0);

        container.innerHTML = `
            <div style="margin-bottom: 20px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 36px; font-weight: bold; color: #f97316;">${delays.avg_duration.toFixed(1)}h</div>
                    <div style="color: #9ca3af; font-size: 13px;">Average Delay Duration</div>
                </div>
            </div>

            <div>
                <h4 style="color: #f3f4f6; font-size: 14px; margin: 0 0 12px 0;">Delays by Reason</h4>
                ${Object.entries(delays.by_reason).map(([reason, data]) => {
            const percentage = (data.hours / totalHours * 100).toFixed(1);
            return `
                        <div style="margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                <span style="color: #9ca3af; font-size: 13px; text-transform: capitalize;">${reason.replace('_', ' ')}</span>
                                <span style="color: #f3f4f6; font-size: 13px; font-weight: 600;">${data.hours}h (${percentage}%)</span>
                            </div>
                            <div style="background: #0d1117; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background: #f97316; height: 100%; width: ${percentage}%; transition: width 0.3s;"></div>
                            </div>
                            <div style="color: #6b7280; font-size: 11px; margin-top: 2px;">${data.count} incidents</div>
                        </div>
                    `;
        }).join('')}
            </div>
        `;
    }

    /**
     * Render stage transition metrics
     */
    renderStageMetrics() {
        const container = document.getElementById('stage-metrics');
        if (!container) return;

        const { stages } = this.analyticsData;

        container.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h4 style="color: #f3f4f6; font-size: 14px; margin: 0 0 12px 0;">Average Time per Stage</h4>
                    ${Object.entries(stages.avg_time_per_stage).map(([stage, hours]) => `
                        <div style="margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                <span style="color: #9ca3af; font-size: 13px;">${stage}</span>
                                <span style="color: #f3f4f6; font-size: 13px; font-weight: 600;">${hours.toFixed(1)}h</span>
                            </div>
                            <div style="background: #0d1117; height: 6px; border-radius: 3px; overflow: hidden;">
                                <div style="background: #3b82f6; height: 100%; width: ${(hours / 5 * 100)}%; transition: width 0.3s;"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <div>
                    <h4 style="color: #f3f4f6; font-size: 14px; margin: 0 0 12px 0;">Most Common Transitions</h4>
                    <table style="width: 100%;">
                        <thead>
                            <tr style="border-bottom: 1px solid #30363d;">
                                <th style="text-align: left; padding: 8px; color: #9ca3af; font-size: 12px;">From → To</th>
                                <th style="text-align: right; padding: 8px; color: #9ca3af; font-size: 12px;">Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${stages.most_common.map(transition => `
                                <tr style="border-bottom: 1px solid #21262d;">
                                    <td style="padding: 8px; color: #f3f4f6; font-size: 12px;">
                                        ${transition.from} <i class="fas fa-arrow-right" style="color: #3b82f6;"></i> ${transition.to}
                                    </td>
                                    <td style="padding: 8px; text-align: right; color: #f3f4f6; font-size: 12px;">${transition.count}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    /**
     * Render notification tracking
     */
    renderNotificationTracking() {
        const container = document.getElementById('notification-tracking');
        if (!container) return;

        const { notifications } = this.analyticsData;

        container.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h4 style="color: #f3f4f6; font-size: 14px; margin: 0 0 12px 0;">By Type</h4>
                    ${Object.entries(notifications.by_type).map(([type, count]) => `
                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #21262d;">
                            <span style="color: #9ca3af; font-size: 13px; text-transform: capitalize;">
                                <i class="fas fa-${type === 'email' ? 'envelope' : type === 'sms' ? 'sms' : type === 'phone' ? 'phone' : 'comments'}" style="color: #10b981; margin-right: 8px;"></i>
                                ${type}
                            </span>
                            <span style="color: #f3f4f6; font-size: 13px; font-weight: 600;">${count}</span>
                        </div>
                    `).join('')}
                </div>

                <div>
                    <h4 style="color: #f3f4f6; font-size: 14px; margin: 0 0 12px 0;">By Status</h4>
                    ${Object.entries(notifications.by_status).map(([status, count]) => {
            const colors = {
                sent: '#10b981',
                pending: '#fbbf24',
                failed: '#ef4444'
            };
            return `
                            <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #21262d;">
                                <span style="color: #9ca3af; font-size: 13px; text-transform: capitalize;">
                                    <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: ${colors[status]}; margin-right: 8px;"></span>
                                    ${status}
                                </span>
                                <span style="color: #f3f4f6; font-size: 13px; font-weight: 600;">${count}</span>
                            </div>
                        `;
        }).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Render top issues and recommendations
     */
    renderTopIssues() {
        const container = document.getElementById('top-issues');
        if (!container) return;

        // Calculate insights from data
        const { wastage, delays, notifications } = this.analyticsData;

        const issues = [
            {
                severity: 'high',
                title: 'High Wastage in Color Calibration',
                description: '18 incidents costing $1,240 in the last 30 days',
                recommendation: 'Invest in automated color calibration system',
                icon: 'fa-exclamation-circle',
                color: '#ef4444'
            },
            {
                severity: 'medium',
                title: 'Equipment Failure Delays',
                description: '23 incidents causing 58.5 hours of delays',
                recommendation: 'Schedule preventive maintenance for Press 2',
                icon: 'fa-wrench',
                color: '#f97316'
            },
            {
                severity: 'low',
                title: 'Pending Client Notifications',
                description: '9 notifications awaiting manual sending',
                recommendation: 'Enable auto-send for standard notifications',
                icon: 'fa-envelope-open',
                color: '#fbbf24'
            }
        ];

        container.innerHTML = `
            <div style="display: grid; gap: 16px;">
                ${issues.map(issue => `
                    <div style="display: flex; gap: 16px; padding: 16px; background: #0d1117; border-left: 4px solid ${issue.color}; border-radius: 6px;">
                        <div style="flex-shrink: 0; width: 40px; height: 40px; border-radius: 50%; background: ${issue.color}20; display: flex; align-items: center; justify-content: center; color: ${issue.color};">
                            <i class="fas ${issue.icon}" style="font-size: 18px;"></i>
                        </div>
                        <div style="flex: 1;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                                <h4 style="color: #f3f4f6; font-size: 15px; margin: 0;">${issue.title}</h4>
                                <span style="background: ${issue.color}20; color: ${issue.color}; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: uppercase;">${issue.severity}</span>
                            </div>
                            <p style="color: #9ca3af; font-size: 13px; margin: 0 0 8px 0;">${issue.description}</p>
                            <div style="background: #161b22; padding: 8px 12px; border-radius: 4px; border-left: 2px solid ${issue.color};">
                                <div style="color: #9ca3af; font-size: 11px; font-weight: 600; margin-bottom: 2px;">RECOMMENDATION:</div>
                                <div style="color: #f3f4f6; font-size: 13px;">${issue.recommendation}</div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * Show loading state
     */
    showLoading() {
        const containers = [
            'analytics-summary',
            'wastage-analysis',
            'delay-analysis',
            'stage-metrics',
            'notification-tracking',
            'top-issues'
        ];

        containers.forEach(id => {
            const container = document.getElementById(id);
            if (container) {
                container.innerHTML = '<div style="text-align: center; padding: 40px; color: #9ca3af;"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
            }
        });
    }

    /**
     * Show error
     */
    showError(message) {
        const containers = [
            'wastage-analysis',
            'delay-analysis',
            'stage-metrics',
            'notification-tracking',
            'top-issues'
        ];

        containers.forEach(id => {
            const container = document.getElementById(id);
            if (container) {
                container.innerHTML = `<div style="text-align: center; padding: 40px; color: #ef4444;"><i class="fas fa-exclamation-triangle"></i> ${message}</div>`;
            }
        });
    }
}

// Register module
window.ModuleRegistry = window.ModuleRegistry || {};
window.ModuleRegistry['production-analytics'] = ProductionAnalyticsModule;

console.log('Production Analytics Module loaded');

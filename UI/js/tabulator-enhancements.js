/**
 * Tabulator Enhancements - Advanced Features Suite
 * Version: 1.0.0
 * Last Updated: November 7, 2025
 * 
 * Purpose:
 * - 10 powerful enhancements for Tabulator tables
 * - Advanced filtering, saved presets, inline editing, bulk actions
 * - Real-time updates, smart alerts, export options, history tracking
 * - Column grouping, mobile responsive layouts
 * 
 * Dependencies:
 * - Tabulator 5.5.2
 * - tabulator-functions.js
 * - tabulator-theme-adapter.js
 */

// =============================================================================
// ENHANCEMENT 1: ADVANCED FILTERING SYSTEM
// =============================================================================

class AdvancedFilterSystem {
    constructor(helper) {
        this.helper = helper;
        this.activeFilters = {};
    }

    /**
     * Apply multi-column filter
     */
    applyMultiFilter(tableKey, filters) {
        const table = this.helper.getTable(tableKey);
        if (!table) return;

        table.setFilter(filters);
        this.activeFilters[tableKey] = filters;

        console.log(`[Advanced Filter] Applied ${filters.length} filters to ${tableKey}`);
    }

    /**
     * Apply date range filter
     */
    applyDateRangeFilter(tableKey, field, startDate, endDate) {
        const table = this.helper.getTable(tableKey);
        if (!table) return;

        table.setFilter((data) => {
            const date = new Date(data[field]);
            return date >= new Date(startDate) && date <= new Date(endDate);
        });

        console.log(`[Advanced Filter] Date range: ${startDate} to ${endDate}`);
    }

    /**
     * Apply custom filter function
     */
    applyCustomFilter(tableKey, filterFunction) {
        const table = this.helper.getTable(tableKey);
        if (!table) return;

        table.setFilter(filterFunction);
    }

    /**
     * Clear all filters
     */
    clearFilters(tableKey) {
        const table = this.helper.getTable(tableKey);
        if (!table) return;

        table.clearFilter();
        delete this.activeFilters[tableKey];

        console.log(`[Advanced Filter] Cleared all filters from ${tableKey}`);
    }

    /**
     * Get active filters
     */
    getActiveFilters(tableKey) {
        return this.activeFilters[tableKey] || [];
    }
}

// =============================================================================
// ENHANCEMENT 2: SAVED VIEWS / PRESETS
// =============================================================================

class TabulatorPresets {
    constructor(helper) {
        this.helper = helper;
        this.presets = this.loadPresets();
    }

    /**
     * Load presets from localStorage
     */
    loadPresets() {
        try {
            const stored = localStorage.getItem('tabulator_presets');
            return stored ? JSON.parse(stored) : {};
        } catch (error) {
            console.error('[Presets] Failed to load:', error);
            return {};
        }
    }

    /**
     * Save current view as preset
     */
    savePreset(name, tableKey) {
        const table = this.helper.getTable(tableKey);
        if (!table) return false;

        try {
            this.presets[`${tableKey}_${name}`] = {
                name: name,
                tableKey: tableKey,
                filters: table.getFilters(),
                sort: table.getSorters(),
                columns: table.getColumns().map(c => ({
                    field: c.getField(),
                    visible: c.isVisible(),
                    width: c.getWidth()
                })),
                pageSize: table.getPageSize(),
                created: new Date().toISOString()
            };

            localStorage.setItem('tabulator_presets', JSON.stringify(this.presets));

            console.log(`[Presets] Saved: ${name}`);
            return true;
        } catch (error) {
            console.error('[Presets] Failed to save:', error);
            return false;
        }
    }

    /**
     * Load preset
     */
    loadPreset(name, tableKey) {
        const preset = this.presets[`${tableKey}_${name}`];
        if (!preset) {
            console.warn(`[Presets] Preset not found: ${name}`);
            return false;
        }

        const table = this.helper.getTable(tableKey);
        if (!table) return false;

        try {
            // Apply filters
            if (preset.filters && preset.filters.length > 0) {
                table.setFilter(preset.filters);
            } else {
                table.clearFilter();
            }

            // Apply sorting
            if (preset.sort && preset.sort.length > 0) {
                table.setSort(preset.sort);
            }

            // Apply column config
            if (preset.columns) {
                preset.columns.forEach(col => {
                    const column = table.getColumn(col.field);
                    if (column) {
                        if (col.visible) {
                            column.show();
                        } else {
                            column.hide();
                        }
                        if (col.width) {
                            column.setWidth(col.width);
                        }
                    }
                });
            }

            // Apply page size
            if (preset.pageSize) {
                table.setPageSize(preset.pageSize);
            }

            console.log(`[Presets] Loaded: ${name}`);
            return true;
        } catch (error) {
            console.error('[Presets] Failed to load:', error);
            return false;
        }
    }

    /**
     * Delete preset
     */
    deletePreset(name, tableKey) {
        const key = `${tableKey}_${name}`;
        if (this.presets[key]) {
            delete this.presets[key];
            localStorage.setItem('tabulator_presets', JSON.stringify(this.presets));
            console.log(`[Presets] Deleted: ${name}`);
            return true;
        }
        return false;
    }

    /**
     * Get all presets for table
     */
    getPresets(tableKey) {
        return Object.values(this.presets).filter(p => p.tableKey === tableKey);
    }

    /**
     * Get all preset names for table
     */
    getPresetNames(tableKey) {
        return this.getPresets(tableKey).map(p => p.name);
    }
}

// =============================================================================
// ENHANCEMENT 3: INLINE EDITING WITH BACKEND SYNC
// =============================================================================

class InlineEditingSystem {
    constructor(helper, backendUrl) {
        this.helper = helper;
        this.backendUrl = backendUrl;
        this.pendingEdits = {};
    }

    /**
     * Setup inline editing for table
     */
    setupInlineEditing(tableKey, config) {
        const table = this.helper.getTable(tableKey);
        if (!table) return;

        table.on("cellEdited", async (cell) => {
            await this.handleCellEdit(cell, tableKey, config);
        });

        console.log(`[Inline Editing] Setup for ${tableKey}`);
    }

    /**
     * Handle cell edit
     */
    async handleCellEdit(cell, tableKey, config) {
        const rowData = cell.getRow().getData();
        const field = cell.getField();
        const newValue = cell.getValue();
        const oldValue = cell.getOldValue();

        // Show pending indicator
        cell.getElement().style.backgroundColor = 'rgba(255, 193, 7, 0.2)';

        try {
            const response = await fetch(`${this.backendUrl}${config.endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    [config.idField]: rowData[config.idField],
                    field: field,
                    value: newValue,
                    oldValue: oldValue
                })
            });

            if (response.ok) {
                // Show success indicator
                cell.getElement().style.backgroundColor = 'rgba(40, 167, 69, 0.2)';
                setTimeout(() => {
                    cell.getElement().style.backgroundColor = '';
                }, 1000);

                console.log(`[Inline Editing] Saved: ${field} = ${newValue}`);
            } else {
                // Revert on error
                cell.restoreOldValue();
                cell.getElement().style.backgroundColor = 'rgba(220, 53, 69, 0.2)';

                const error = await response.text();
                console.error('[Inline Editing] Failed:', error);

                alert(`Failed to save: ${error}`);
            }
        } catch (error) {
            // Revert on error
            cell.restoreOldValue();
            cell.getElement().style.backgroundColor = 'rgba(220, 53, 69, 0.2)';

            console.error('[Inline Editing] Error:', error);
            alert('Network error - changes not saved');
        }
    }
}

// =============================================================================
// ENHANCEMENT 4: BULK ACTIONS MENU
// =============================================================================

class BulkActionsMenu {
    constructor(helper, backendUrl) {
        this.helper = helper;
        this.backendUrl = backendUrl;
    }

    /**
     * Show bulk actions menu
     */
    showMenu(tableKey, actions) {
        const selected = this.helper.getSelectedRows(tableKey);

        if (selected.length === 0) {
            alert('No rows selected');
            return;
        }

        const menuHtml = `
            <div class="bulk-actions-menu" id="bulk-actions-menu-${tableKey}">
                <div class="bulk-actions-header">
                    <span>${selected.length} items selected</span>
                    <button onclick="bulkActions.closeMenu('${tableKey}')">×</button>
                </div>
                <div class="bulk-actions-body">
                    ${actions.map(action => `
                        <button class="bulk-action-btn ${action.danger ? 'danger' : ''}" 
                                onclick="bulkActions.${action.handler}('${tableKey}')">
                            <i class="fas fa-${action.icon}"></i> ${action.label}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;

        // Show menu
        const container = document.getElementById('bulk-actions-container');
        if (container) {
            container.innerHTML = menuHtml;
            container.style.display = 'block';
        }
    }

    /**
     * Close menu
     */
    closeMenu(tableKey) {
        const container = document.getElementById('bulk-actions-container');
        if (container) {
            container.style.display = 'none';
        }
    }

    /**
     * Bulk order action
     */
    async bulkOrder(tableKey) {
        const selected = this.helper.getSelectedRows(tableKey);

        try {
            const response = await fetch(`${this.backendUrl}/api/stock/bulk-order`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ items: selected })
            });

            if (response.ok) {
                const result = await response.json();
                alert(`✅ Created ${result.count} purchase orders`);
                this.closeMenu(tableKey);
            } else {
                throw new Error('Failed to create orders');
            }
        } catch (error) {
            console.error('[Bulk Actions] Order failed:', error);
            alert('Failed to create purchase orders');
        }
    }

    /**
     * Bulk tag action
     */
    async bulkTag(tableKey, color) {
        if (typeof window.TabulatorFunctions !== 'undefined') {
            const table = this.helper.getTable(tableKey);
            await window.TabulatorFunctions.bulkTagRows(table, color, 'sku');
            this.closeMenu(tableKey);
        }
    }

    /**
     * Bulk export action
     */
    async bulkExport(tableKey, format = 'xlsx') {
        const table = this.helper.getTable(tableKey);
        const selected = this.helper.getSelectedRows(tableKey);

        // Create temporary table with selected rows
        const tempDiv = document.createElement('div');
        tempDiv.style.display = 'none';
        document.body.appendChild(tempDiv);

        const tempTable = new Tabulator(tempDiv, {
            data: selected,
            columns: table.getColumns().map(c => c.getDefinition())
        });

        // Export
        tempTable.download(format, `selected-items-${Date.now()}.${format}`);

        // Cleanup
        setTimeout(() => {
            tempTable.destroy();
            document.body.removeChild(tempDiv);
        }, 1000);

        this.closeMenu(tableKey);
    }

    /**
     * Bulk delete action
     */
    async bulkDelete(tableKey, deleteCallback) {
        if (typeof window.TabulatorFunctions !== 'undefined') {
            const table = this.helper.getTable(tableKey);
            await window.TabulatorFunctions.bulkDeleteRows(
                table,
                deleteCallback,
                "Are you sure you want to delete selected items?"
            );
            this.closeMenu(tableKey);
        }
    }

    /**
     * Bulk email action
     */
    async bulkEmail(tableKey) {
        const selected = this.helper.getSelectedRows(tableKey);

        // Generate report
        const report = this.generateReport(selected);

        // Open email modal
        const subject = `Stock Report - ${selected.length} items`;
        const body = encodeURIComponent(report);

        window.location.href = `mailto:?subject=${subject}&body=${body}`;

        this.closeMenu(tableKey);
    }

    /**
     * Generate text report
     */
    generateReport(items) {
        let report = `Stock Report\n`;
        report += `Generated: ${new Date().toLocaleString()}\n`;
        report += `Items: ${items.length}\n\n`;

        items.forEach((item, index) => {
            report += `${index + 1}. ${item.product_name || item.name}\n`;
            report += `   SKU: ${item.sku}\n`;
            report += `   Stock: ${item.current_stock}\n\n`;
        });

        return report;
    }
}

// =============================================================================
// ENHANCEMENT 5: REAL-TIME AUTO-REFRESH
// =============================================================================

class AutoRefreshSystem {
    constructor(helper, backendUrl) {
        this.helper = helper;
        this.backendUrl = backendUrl;
        this.intervals = {};
    }

    /**
     * Enable auto-refresh for table
     */
    enableAutoRefresh(tableKey, endpoint, intervalSeconds = 30) {
        // Clear existing interval
        this.disableAutoRefresh(tableKey);

        const table = this.helper.getTable(tableKey);
        if (!table) return;

        this.intervals[tableKey] = setInterval(async () => {
            await this.refreshTable(table, endpoint, tableKey);
        }, intervalSeconds * 1000);

        console.log(`[Auto-Refresh] Enabled for ${tableKey} (${intervalSeconds}s)`);
    }

    /**
     * Disable auto-refresh
     */
    disableAutoRefresh(tableKey) {
        if (this.intervals[tableKey]) {
            clearInterval(this.intervals[tableKey]);
            delete this.intervals[tableKey];
            console.log(`[Auto-Refresh] Disabled for ${tableKey}`);
        }
    }

    /**
     * Refresh table data
     */
    async refreshTable(table, endpoint, tableKey) {
        try {
            // Get current scroll position
            const scrollPos = table.element.querySelector('.tabulator-tableholder')?.scrollTop || 0;

            // Fetch new data
            const response = await fetch(`${this.backendUrl}${endpoint}`);
            if (!response.ok) throw new Error('Fetch failed');

            const newData = await response.json();

            // Update only changed rows (smart diff)
            table.updateData(newData);

            // Restore scroll position
            const holder = table.element.querySelector('.tabulator-tableholder');
            if (holder) {
                holder.scrollTop = scrollPos;
            }

            console.log(`[Auto-Refresh] ${tableKey} updated - ${newData.length} rows`);
        } catch (error) {
            console.error('[Auto-Refresh] Failed:', error);
        }
    }

    /**
     * Get refresh status
     */
    isEnabled(tableKey) {
        return !!this.intervals[tableKey];
    }

    /**
     * Disable all auto-refresh
     */
    disableAll() {
        Object.keys(this.intervals).forEach(key => {
            this.disableAutoRefresh(key);
        });
    }
}

// =============================================================================
// ENHANCEMENT 6: ADVANCED EXPORT OPTIONS
// =============================================================================

class AdvancedExportSystem {
    constructor(helper) {
        this.helper = helper;
    }

    /**
     * Export with formatting
     */
    exportWithFormatting(tableKey, format, options = {}) {
        const table = this.helper.getTable(tableKey);
        if (!table) return;

        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        const filename = `${tableKey}-${timestamp}`;

        switch (format) {
            case 'excel':
            case 'xlsx':
                table.download("xlsx", `${filename}.xlsx`, {
                    sheetName: options.sheetName || "Data",
                    ...options
                });
                break;

            case 'pdf':
                table.download("pdf", `${filename}.pdf`, {
                    orientation: "landscape",
                    title: options.title || "Report",
                    autoTable: {
                        styles: { fontSize: 8 },
                        headStyles: { fillColor: [0, 120, 212] }
                    },
                    ...options
                });
                break;

            case 'csv':
                table.download("csv", `${filename}.csv`, options);
                break;

            case 'json':
                table.download("json", `${filename}.json`, options);
                break;

            case 'html':
                table.download("html", `${filename}.html`, {
                    style: true,
                    ...options
                });
                break;

            default:
                console.error('[Export] Unknown format:', format);
        }

        console.log(`[Export] Exported ${format.toUpperCase()}: ${filename}`);
    }

    /**
     * Export selected rows only
     */
    exportSelected(tableKey, format) {
        const selected = this.helper.getSelectedRows(tableKey);

        if (selected.length === 0) {
            alert('No rows selected');
            return;
        }

        const table = this.helper.getTable(tableKey);
        const tempDiv = document.createElement('div');
        tempDiv.style.display = 'none';
        document.body.appendChild(tempDiv);

        const tempTable = new Tabulator(tempDiv, {
            data: selected,
            columns: table.getColumns().map(c => c.getDefinition())
        });

        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        tempTable.download(format, `${tableKey}-selected-${timestamp}.${format}`);

        setTimeout(() => {
            tempTable.destroy();
            document.body.removeChild(tempDiv);
        }, 1000);
    }

    /**
     * Export with custom columns
     */
    exportCustomColumns(tableKey, format, columnFields) {
        const table = this.helper.getTable(tableKey);
        const data = table.getData();

        // Filter data to include only specified columns
        const filteredData = data.map(row => {
            const filtered = {};
            columnFields.forEach(field => {
                filtered[field] = row[field];
            });
            return filtered;
        });

        // Create temporary table
        const tempDiv = document.createElement('div');
        tempDiv.style.display = 'none';
        document.body.appendChild(tempDiv);

        const columns = columnFields.map(field => {
            const originalColumn = table.getColumn(field);
            return originalColumn ? originalColumn.getDefinition() : { title: field, field: field };
        });

        const tempTable = new Tabulator(tempDiv, {
            data: filteredData,
            columns: columns
        });

        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        tempTable.download(format, `${tableKey}-custom-${timestamp}.${format}`);

        setTimeout(() => {
            tempTable.destroy();
            document.body.removeChild(tempDiv);
        }, 1000);
    }
}

// =============================================================================
// ENHANCEMENT 7: ROW HISTORY / AUDIT TRAIL
// =============================================================================

class RowHistoryTracker {
    constructor(helper, backendUrl) {
        this.helper = helper;
        this.backendUrl = backendUrl;
        this.history = {};
    }

    /**
     * Track changes for table
     */
    trackChanges(tableKey, idField = 'id') {
        const table = this.helper.getTable(tableKey);
        if (!table) return;

        table.on("cellEdited", (cell) => {
            this.recordChange(cell, tableKey, idField);
        });

        console.log(`[History] Tracking enabled for ${tableKey}`);
    }

    /**
     * Record a change
     */
    recordChange(cell, tableKey, idField) {
        const rowData = cell.getRow().getData();
        const rowId = rowData[idField];
        const field = cell.getField();
        const oldValue = cell.getOldValue();
        const newValue = cell.getValue();

        if (!this.history[rowId]) {
            this.history[rowId] = [];
        }

        const change = {
            timestamp: new Date().toISOString(),
            field: field,
            oldValue: oldValue,
            newValue: newValue,
            user: window.currentUser || 'Unknown',
            tableKey: tableKey
        };

        this.history[rowId].push(change);

        // Save to backend
        this.saveHistory(rowId, change);

        console.log(`[History] Recorded: ${rowId}.${field}`);
    }

    /**
     * Save history to backend
     */
    async saveHistory(rowId, change) {
        try {
            await fetch(`${this.backendUrl}/api/history/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rowId, change })
            });
        } catch (error) {
            console.error('[History] Failed to save:', error);
        }
    }

    /**
     * Get history for row
     */
    getHistory(rowId) {
        return this.history[rowId] || [];
    }

    /**
     * Show history modal
     */
    showHistory(rowId) {
        const history = this.getHistory(rowId);

        if (history.length === 0) {
            alert('No change history for this item');
            return;
        }

        const modalHtml = `
            <div class="history-modal-overlay" onclick="rowHistory.closeHistory()">
                <div class="history-modal-content" onclick="event.stopPropagation()">
                    <div class="history-modal-header">
                        <h3><i class="fas fa-history"></i> Change History: ${rowId}</h3>
                        <button onclick="rowHistory.closeHistory()">×</button>
                    </div>
                    <div class="history-modal-body">
                        <table class="history-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Field</th>
                                    <th>Old Value</th>
                                    <th>New Value</th>
                                    <th>User</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${history.map(h => `
                                    <tr>
                                        <td>${new Date(h.timestamp).toLocaleString()}</td>
                                        <td>${h.field}</td>
                                        <td>${this.formatValue(h.oldValue)}</td>
                                        <td>${this.formatValue(h.newValue)}</td>
                                        <td>${h.user}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    /**
     * Close history modal
     */
    closeHistory() {
        const modal = document.querySelector('.history-modal-overlay');
        if (modal) {
            modal.remove();
        }
    }

    /**
     * Format value for display
     */
    formatValue(value) {
        if (value === null || value === undefined) return '-';
        if (typeof value === 'object') return JSON.stringify(value);
        return String(value);
    }
}

// =============================================================================
// ENHANCEMENT 8: SMART ALERTS / NOTIFICATIONS
// =============================================================================

class TabulatorAlerts {
    constructor(helper) {
        this.helper = helper;
        this.rules = [];
    }

    /**
     * Add alert rule
     */
    addAlertRule(rule) {
        this.rules.push({
            id: rule.id || `rule_${Date.now()}`,
            type: rule.type || 'info',
            title: rule.title,
            message: rule.message,
            condition: rule.condition,
            action: rule.action
        });

        console.log(`[Alerts] Added rule: ${rule.title}`);
    }

    /**
     * Check alerts for table
     */
    checkAlerts(tableKey) {
        const table = this.helper.getTable(tableKey);
        if (!table) return;

        const data = table.getData();

        this.rules.forEach(rule => {
            const matches = data.filter(row => rule.condition(row));

            if (matches.length > 0) {
                this.showAlert({
                    type: rule.type,
                    title: rule.title,
                    message: `${matches.length} ${rule.message}`,
                    data: matches,
                    action: rule.action
                });
            }
        });
    }

    /**
     * Show alert notification
     */
    showAlert(alert) {
        const icon = this.getIcon(alert.type);
        const color = this.getColor(alert.type);

        const toastHtml = `
            <div class="alert-toast alert-${alert.type}" style="border-left: 4px solid ${color}">
                <i class="fas fa-${icon}" style="color: ${color}"></i>
                <div class="alert-content">
                    <strong>${alert.title}</strong>
                    <p>${alert.message}</p>
                    ${alert.action ? `<button onclick="${alert.action}" class="alert-action-btn">View Details</button>` : ''}
                </div>
                <button onclick="this.parentElement.remove()" class="alert-close-btn">×</button>
            </div>
        `;

        let container = document.getElementById('alert-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'alert-container';
            container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 10000;';
            document.body.appendChild(container);
        }

        container.insertAdjacentHTML('beforeend', toastHtml);

        // Auto-remove after 10 seconds
        setTimeout(() => {
            const toast = container.querySelector(`.alert-${alert.type}`);
            if (toast) toast.remove();
        }, 10000);

        console.log(`[Alerts] Shown: ${alert.title}`);
    }

    /**
     * Get icon for alert type
     */
    getIcon(type) {
        const icons = {
            'critical': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle',
            'success': 'check-circle'
        };
        return icons[type] || 'bell';
    }

    /**
     * Get color for alert type
     */
    getColor(type) {
        const colors = {
            'critical': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'success': '#28a745'
        };
        return colors[type] || '#6c757d';
    }

    /**
     * Clear all alerts
     */
    clearAlerts() {
        const container = document.getElementById('alert-container');
        if (container) {
            container.innerHTML = '';
        }
    }

    /**
     * Remove alert rule
     */
    removeAlertRule(ruleId) {
        this.rules = this.rules.filter(r => r.id !== ruleId);
    }
}

// =============================================================================
// ENHANCEMENT 9: COLUMN GROUPS / PIVOT TABLES
// =============================================================================

class PivotTableSystem {
    constructor(helper) {
        this.helper = helper;
    }

    /**
     * Create pivot view
     */
    createPivotView(tableKey, config) {
        const table = this.helper.getTable(tableKey);
        if (!table) return;

        const data = table.getData();
        const pivotData = this.pivotData(data, config);

        // Create pivot table in new container
        const pivotContainer = document.getElementById(config.containerId);
        if (!pivotContainer) {
            console.error('[Pivot] Container not found:', config.containerId);
            return;
        }

        new Tabulator(pivotContainer, {
            data: pivotData,
            layout: "fitDataStretch",
            columns: config.columns
        });

        console.log(`[Pivot] Created: ${config.groupBy.join(', ')}`);
    }

    /**
     * Pivot data by grouping
     */
    pivotData(data, config) {
        const grouped = {};

        data.forEach(row => {
            // Build key from groupBy fields
            const key = config.groupBy.map(field => row[field]).join('|');

            if (!grouped[key]) {
                grouped[key] = {
                    ...config.groupBy.reduce((acc, field) => {
                        acc[field] = row[field];
                        return acc;
                    }, {}),
                    count: 0
                };

                // Initialize aggregate fields
                config.aggregates.forEach(agg => {
                    grouped[key][agg.field] = 0;
                });
            }

            grouped[key].count++;

            // Apply aggregates
            config.aggregates.forEach(agg => {
                switch (agg.operation) {
                    case 'sum':
                        grouped[key][agg.field] += row[agg.sourceField] || 0;
                        break;
                    case 'avg':
                        grouped[key][agg.field] =
                            (grouped[key][agg.field] * (grouped[key].count - 1) + (row[agg.sourceField] || 0)) / grouped[key].count;
                        break;
                    case 'count':
                        if (row[agg.sourceField]) {
                            grouped[key][agg.field]++;
                        }
                        break;
                }
            });
        });

        return Object.values(grouped);
    }
}

// =============================================================================
// ENHANCEMENT 10: MOBILE RESPONSIVE LAYOUT
// =============================================================================

class MobileResponsiveSystem {
    constructor(helper) {
        this.helper = helper;
        this.breakpoint = 768;
    }

    /**
     * Setup responsive layout for table
     */
    setupResponsive(tableKey) {
        const table = this.helper.getTable(tableKey);
        if (!table) return;

        // Check screen size on resize
        window.addEventListener('resize', () => {
            this.handleResize(table);
        });

        // Initial check
        this.handleResize(table);

        console.log(`[Mobile] Responsive enabled for ${tableKey}`);
    }

    /**
     * Handle resize event
     */
    handleResize(table) {
        const isMobile = window.innerWidth < this.breakpoint;

        if (isMobile) {
            // Switch to mobile layout
            table.setColumns(this.getMobileColumns(table));
        } else {
            // Switch to desktop layout
            table.setColumns(this.getDesktopColumns(table));
        }
    }

    /**
     * Get mobile column configuration
     */
    getMobileColumns(table) {
        // Get first few important columns only
        const desktopColumns = table.getColumnDefinitions();

        return [{
            title: "",
            field: "_mobile",
            width: "100%",
            formatter: (cell) => {
                const data = cell.getRow().getData();
                return this.formatMobileCard(data);
            }
        }];
    }

    /**
     * Get desktop column configuration
     */
    getDesktopColumns(table) {
        return table.getColumnDefinitions();
    }

    /**
     * Format mobile card view
     */
    formatMobileCard(data) {
        return `
            <div class="mobile-table-card">
                <div class="mobile-card-title">${data.product_name || data.name || 'Item'}</div>
                <div class="mobile-card-subtitle">SKU: ${data.sku || '-'}</div>
                <div class="mobile-card-row">
                    <span class="mobile-card-label">Stock:</span>
                    <span class="mobile-card-value">${data.current_stock || 0}</span>
                </div>
                <div class="mobile-card-row">
                    <span class="mobile-card-label">Status:</span>
                    <span class="mobile-card-value mobile-card-status-${data.status}">${data.status || 'N/A'}</span>
                </div>
            </div>
        `;
    }
}

// =============================================================================
// MAIN ENHANCEMENTS MANAGER
// =============================================================================

class TabulatorEnhancements {
    constructor(helper, backendUrl) {
        this.helper = helper;
        this.backendUrl = backendUrl;

        // Initialize all enhancement systems
        this.advancedFilter = new AdvancedFilterSystem(helper);
        this.presets = new TabulatorPresets(helper);
        this.inlineEditing = new InlineEditingSystem(helper, backendUrl);
        this.bulkActions = new BulkActionsMenu(helper, backendUrl);
        this.autoRefresh = new AutoRefreshSystem(helper, backendUrl);
        this.advancedExport = new AdvancedExportSystem(helper);
        this.rowHistory = new RowHistoryTracker(helper, backendUrl);
        this.alerts = new TabulatorAlerts(helper);
        this.pivot = new PivotTableSystem(helper);
        this.mobile = new MobileResponsiveSystem(helper);

        console.log('[Enhancements] All systems initialized');
    }

    /**
     * Enable all enhancements for a table
     */
    enableAll(tableKey, config = {}) {
        // Setup inline editing
        if (config.inlineEditing) {
            this.inlineEditing.setupInlineEditing(tableKey, config.inlineEditing);
        }

        // Setup history tracking
        if (config.tracking) {
            this.rowHistory.trackChanges(tableKey, config.tracking.idField);
        }

        // Setup auto-refresh
        if (config.autoRefresh) {
            this.autoRefresh.enableAutoRefresh(
                tableKey,
                config.autoRefresh.endpoint,
                config.autoRefresh.interval
            );
        }

        // Setup mobile responsive
        if (config.mobile !== false) {
            this.mobile.setupResponsive(tableKey);
        }

        // Setup alerts
        if (config.alerts) {
            config.alerts.forEach(rule => {
                this.alerts.addAlertRule(rule);
            });
            this.alerts.checkAlerts(tableKey);
        }

        console.log(`[Enhancements] Enabled for ${tableKey}`);
    }

    /**
     * Cleanup all enhancements
     */
    cleanup() {
        this.autoRefresh.disableAll();
        this.alerts.clearAlerts();
        console.log('[Enhancements] Cleanup complete');
    }
}

// =============================================================================
// EXPORT TO WINDOW
// =============================================================================

window.TabulatorEnhancements = TabulatorEnhancements;
window.AdvancedFilterSystem = AdvancedFilterSystem;
window.TabulatorPresets = TabulatorPresets;
window.InlineEditingSystem = InlineEditingSystem;
window.BulkActionsMenu = BulkActionsMenu;
window.AutoRefreshSystem = AutoRefreshSystem;
window.AdvancedExportSystem = AdvancedExportSystem;
window.RowHistoryTracker = RowHistoryTracker;
window.TabulatorAlerts = TabulatorAlerts;
window.PivotTableSystem = PivotTableSystem;
window.MobileResponsiveSystem = MobileResponsiveSystem;

console.log('[Tabulator Enhancements] All 10 enhancement systems loaded');

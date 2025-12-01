/**
 * KanbanLogger - Centralized logging utility for InHouse Kanban Module
 * 
 * Replaces excessive console.log usage with structured, filterable logging
 * Supports log levels, categories, and export functionality
 * 
 * Usage:
 *   const logger = new KanbanLogger({ level: 'info', enabled: true });
 *   logger.info('Module initialized', { jobs: 150 });
 *   logger.error('Failed to load data', error);
 *   logger.debug('Card rendered', { cardId: 123 });
 */

class KanbanLogger {
    constructor(options = {}) {
        this.enabled = options.enabled !== false; // Default: enabled
        this.level = options.level || 'info'; // debug, info, warn, error
        this.category = options.category || 'kanban';
        this.logs = []; // Store logs for export
        this.maxLogs = options.maxLogs || 1000; // Limit log history

        // Log levels (higher number = higher priority)
        this.levels = {
            debug: 0,
            info: 1,
            warn: 2,
            error: 3
        };

        // Emoji icons for each level
        this.icons = {
            debug: '🔍',
            info: '✅',
            warn: '⚠️',
            error: '❌',
            success: '🎉',
            loading: '⏳',
            data: '📊',
            network: '🌐',
            ui: '🎨'
        };
    }

    /**
     * Check if a log should be output based on current level
     */
    shouldLog(level) {
        if (!this.enabled) return false;
        return this.levels[level] >= this.levels[this.level];
    }

    /**
     * Format log message with timestamp and metadata
     */
    formatMessage(level, message, data = null) {
        const timestamp = new Date().toISOString().split('T')[1].split('.')[0]; // HH:MM:SS
        const icon = this.icons[level] || '📝';
        const prefix = `${icon} [${timestamp}] [${this.category}]`;

        return {
            timestamp: new Date().toISOString(),
            level,
            category: this.category,
            message,
            data,
            formatted: `${prefix} ${message}`
        };
    }

    /**
     * Store log entry in history
     */
    storeLog(logEntry) {
        this.logs.push(logEntry);

        // Limit log history size
        if (this.logs.length > this.maxLogs) {
            this.logs.shift(); // Remove oldest log
        }
    }

    /**
     * Debug level - detailed information for debugging
     */
    debug(message, data = null) {
        if (!this.shouldLog('debug')) return;

        const logEntry = this.formatMessage('debug', message, data);
        this.storeLog(logEntry);

        if (data) {
            console.debug(logEntry.formatted, data);
        } else {
            console.debug(logEntry.formatted);
        }
    }

    /**
     * Info level - general information
     */
    info(message, data = null) {
        if (!this.shouldLog('info')) return;

        const logEntry = this.formatMessage('info', message, data);
        this.storeLog(logEntry);

        if (data) {
            console.log(logEntry.formatted, data);
        } else {
            console.log(logEntry.formatted);
        }
    }

    /**
     * Warn level - warnings and non-critical issues
     */
    warn(message, data = null) {
        if (!this.shouldLog('warn')) return;

        const logEntry = this.formatMessage('warn', message, data);
        this.storeLog(logEntry);

        if (data) {
            console.warn(logEntry.formatted, data);
        } else {
            console.warn(logEntry.formatted);
        }
    }

    /**
     * Error level - errors and critical issues
     */
    error(message, error = null) {
        if (!this.shouldLog('error')) return;

        const logEntry = this.formatMessage('error', message, error);
        this.storeLog(logEntry);

        if (error) {
            console.error(logEntry.formatted, error);
        } else {
            console.error(logEntry.formatted);
        }
    }

    /**
     * Special logging methods with custom icons
     */
    success(message, data = null) {
        const logEntry = this.formatMessage('success', message, data);
        logEntry.formatted = logEntry.formatted.replace('📝', this.icons.success);
        this.storeLog(logEntry);
        console.log(logEntry.formatted, data || '');
    }

    loading(message, data = null) {
        const logEntry = this.formatMessage('loading', message, data);
        logEntry.formatted = logEntry.formatted.replace('📝', this.icons.loading);
        this.storeLog(logEntry);
        console.log(logEntry.formatted, data || '');
    }

    data(message, data = null) {
        const logEntry = this.formatMessage('data', message, data);
        logEntry.formatted = logEntry.formatted.replace('📝', this.icons.data);
        this.storeLog(logEntry);
        console.log(logEntry.formatted, data || '');
    }

    network(message, data = null) {
        const logEntry = this.formatMessage('network', message, data);
        logEntry.formatted = logEntry.formatted.replace('📝', this.icons.network);
        this.storeLog(logEntry);
        console.log(logEntry.formatted, data || '');
    }

    ui(message, data = null) {
        const logEntry = this.formatMessage('ui', message, data);
        logEntry.formatted = logEntry.formatted.replace('📝', this.icons.ui);
        this.storeLog(logEntry);
        console.log(logEntry.formatted, data || '');
    }

    /**
     * Group related logs together
     */
    group(label) {
        if (!this.enabled) return;
        console.group(`${this.icons.info} ${label}`);
    }

    groupEnd() {
        if (!this.enabled) return;
        console.groupEnd();
    }

    /**
     * Log with timing information
     */
    time(label) {
        if (!this.enabled) return;
        console.time(`⏱️ ${label}`);
    }

    timeEnd(label) {
        if (!this.enabled) return;
        console.timeEnd(`⏱️ ${label}`);
    }

    /**
     * Get all logs (for export or display)
     */
    getLogs(filter = {}) {
        let filtered = this.logs;

        if (filter.level) {
            filtered = filtered.filter(log => log.level === filter.level);
        }

        if (filter.category) {
            filtered = filtered.filter(log => log.category === filter.category);
        }

        if (filter.search) {
            const searchLower = filter.search.toLowerCase();
            filtered = filtered.filter(log =>
                log.message.toLowerCase().includes(searchLower)
            );
        }

        return filtered;
    }

    /**
     * Export logs as JSON
     */
    exportJSON() {
        const data = {
            exported_at: new Date().toISOString(),
            total_logs: this.logs.length,
            logs: this.logs
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `kanban-logs-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Export logs as CSV
     */
    exportCSV() {
        const headers = ['Timestamp', 'Level', 'Category', 'Message'];
        const rows = this.logs.map(log => [
            log.timestamp,
            log.level,
            log.category,
            log.message
        ]);

        const csv = [headers, ...rows]
            .map(row => row.map(cell => `"${cell}"`).join(','))
            .join('\n');

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `kanban-logs-${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Clear all logs
     */
    clear() {
        this.logs = [];
        console.clear();
        this.info('Logs cleared');
    }

    /**
     * Print log summary
     */
    summary() {
        const summary = {
            total: this.logs.length,
            by_level: {}
        };

        Object.keys(this.levels).forEach(level => {
            summary.by_level[level] = this.logs.filter(log => log.level === level).length;
        });

        console.table(summary.by_level);
        return summary;
    }

    /**
     * Enable/disable logging
     */
    enable() {
        this.enabled = true;
        this.info('Logging enabled');
    }

    disable() {
        this.enabled = false;
    }

    /**
     * Set log level
     */
    setLevel(level) {
        if (this.levels[level] !== undefined) {
            this.level = level;
            this.info(`Log level set to: ${level}`);
        } else {
            this.warn(`Invalid log level: ${level}`);
        }
    }
}

// Export for use in module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KanbanLogger;
}

// Make available globally for browser usage
if (typeof window !== 'undefined') {
    window.KanbanLogger = KanbanLogger;
}

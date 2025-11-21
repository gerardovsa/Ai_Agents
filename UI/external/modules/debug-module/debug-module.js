/**
 * DEBUG MODULE - JAVASCRIPT
 * 
 * Advanced debugging tools for thread persistence and message tracking
 * Extracts clean, structured logs for AI analysis
 * 
 * Features:
 * - Thread save/load tracking
 * - Message persistence debugging
 * - Conversation history inspection
 * - API request/response logging
 * - Clean log extraction (no clutter)
 */

const DebugModule = {
    logs: [],
    maxLogs: 500,
    filters: {
        threadSave: true,
        threadLoad: true,
        messageSave: true,
        messageLoad: true,
        apiCalls: true,
        errors: true,
        truncateResults: true
    },

    init() {
        console.log('[DEBUG MODULE] Initializing...');
        this.interceptConsoleLogs();
        this.monitorThreadOperations();
        this.monitorAPIRequests();
        console.log('[DEBUG MODULE] Ready');
    },

    /**
     * Intercept console logs and filter for relevant debug info
     */
    interceptConsoleLogs() {
        const originalLog = console.log;
        const originalError = console.error;
        const originalWarn = console.warn;

        console.log = (...args) => {
            this.captureLog('log', args);
            originalLog.apply(console, args);
        };

        console.error = (...args) => {
            this.captureLog('error', args);
            originalError.apply(console, args);
        };

        console.warn = (...args) => {
            this.captureLog('warn', args);
            originalWarn.apply(console, args);
        };
    },

    /**
     * Capture relevant log messages
     */
    captureLog(level, args) {
        const message = args.map(arg =>
            typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
        ).join(' ');

        // Filter for relevant patterns
        const patterns = [
            /\[MESSAGE SAVE\]/i,
            /\[Thread.*save\]/i,
            /loadThreadsFromBackend/i,
            /saveMessagesToBackend/i,
            /saveThreadToBackend/i,
            /updateCurrentThread/i,
            /conversation.*history/i,
            /tool_use.*tool_result/i,
            /POST.*\/api\/threads/i,
            /GET.*\/api\/threads/i
        ];

        const isRelevant = patterns.some(pattern => pattern.test(message));

        if (isRelevant || level === 'error') {
            this.logs.push({
                timestamp: new Date().toISOString(),
                level,
                message,
                stack: level === 'error' ? new Error().stack : null
            });

            // Keep only last maxLogs entries
            if (this.logs.length > this.maxLogs) {
                this.logs.shift();
            }

            // Real-time update: Refresh the logs display if sidebar is open
            if (DebugSidebar && DebugSidebar.isOpen && DebugSidebar.currentTab === 'logs') {
                DebugSidebar.renderLogs();
            }
        }
    },

    /**
     * Monitor ThreadManager operations
     */
    monitorThreadOperations() {
        if (typeof ThreadManager === 'undefined') {
            console.warn('[DEBUG MODULE] ThreadManager not found');
            return;
        }

        // Wrap key methods
        const originalUpdateCurrent = ThreadManager.updateCurrentThread;
        ThreadManager.updateCurrentThread = function (...args) {
            DebugModule.captureLog('log', ['[DEBUG HOOK] updateCurrentThread called', args]);
            return originalUpdateCurrent.apply(this, args);
        };

        const originalSaveMessages = ThreadManager.saveMessagesToBackend;
        ThreadManager.saveMessagesToBackend = async function (...args) {
            DebugModule.captureLog('log', ['[DEBUG HOOK] saveMessagesToBackend called', args]);
            const result = await originalSaveMessages.apply(this, args);
            DebugModule.captureLog('log', ['[DEBUG HOOK] saveMessagesToBackend result:', result]);
            return result;
        };

        const originalSaveThread = ThreadManager.saveThreadToBackend;
        ThreadManager.saveThreadToBackend = async function (...args) {
            DebugModule.captureLog('log', ['[DEBUG HOOK] saveThreadToBackend called', args]);
            const result = await originalSaveThread.apply(this, args);
            DebugModule.captureLog('log', ['[DEBUG HOOK] saveThreadToBackend result:', result]);
            return result;
        };

        const originalLoadThreads = ThreadManager.loadThreadsFromBackend;
        ThreadManager.loadThreadsFromBackend = async function (...args) {
            DebugModule.captureLog('log', ['[DEBUG HOOK] loadThreadsFromBackend called']);
            const result = await originalLoadThreads.apply(this, args);
            DebugModule.captureLog('log', [`[DEBUG HOOK] loadThreadsFromBackend loaded ${ThreadManager.threads.length} threads`]);
            return result;
        };
    },

    /**
     * Monitor fetch API requests
     */
    monitorAPIRequests() {
        const originalFetch = window.fetch;
        window.fetch = async function (...args) {
            const [url, options] = args;

            // Only log thread/message API calls
            if (url.includes('/api/threads') || url.includes('/api/messages')) {
                DebugModule.captureLog('log', [`[API REQUEST] ${options?.method || 'GET'} ${url}`]);

                if (options?.body) {
                    try {
                        const body = JSON.parse(options.body);
                        DebugModule.captureLog('log', [`[API REQUEST BODY]`, body]);
                    } catch (e) {
                        // Not JSON
                    }
                }
            }

            const response = await originalFetch.apply(this, args);

            // Log response for thread/message APIs
            if (url.includes('/api/threads') || url.includes('/api/messages')) {
                const clonedResponse = response.clone();
                try {
                    const data = await clonedResponse.json();
                    DebugModule.captureLog('log', [`[API RESPONSE] ${response.status}`, data]);
                } catch (e) {
                    DebugModule.captureLog('log', [`[API RESPONSE] ${response.status} (non-JSON)`]);
                }
            }

            return response;
        };
    },

    /**
     * Extract structured logs for export
     */
    extractLogs() {
        const filtered = this.logs.filter(log => {
            if (log.message.includes('[MESSAGE SAVE]') && !this.filters.messageSave) return false;
            if (log.message.includes('saveThreadToBackend') && !this.filters.threadSave) return false;
            if (log.message.includes('loadThreadsFromBackend') && !this.filters.threadLoad) return false;
            if (log.message.includes('[API REQUEST]') && !this.filters.apiCalls) return false;
            if (log.level === 'error' && !this.filters.errors) return false;
            return true;
        });

        return {
            extracted_at: new Date().toISOString(),
            total_logs: filtered.length,
            filters_applied: this.filters,
            thread_state: this.getThreadState(),
            app_state: this.getAppState(),
            logs: filtered.map(log => ({
                time: log.timestamp,
                level: log.level,
                message: log.message
            }))
        };
    },

    /**
     * Get current thread state
     */
    getThreadState() {
        if (typeof ThreadManager === 'undefined') return null;

        return {
            total_threads: ThreadManager.threads.length,
            current_thread: ThreadManager.getCurrentThread()?.id || null,
            threads: ThreadManager.threads.map(t => ({
                id: t.id,
                title: t.title,
                location: t.location,
                message_count: t.messages?.length || 0,
                updated: t.updated
            }))
        };
    },

    /**
     * ENHANCED: Get detailed thread structure with full message sequences
     */
    extractThreadStructure() {
        if (typeof ThreadManager === 'undefined') {
            return { error: 'ThreadManager not available' };
        }

        const currentThread = ThreadManager.getCurrentThread();

        return {
            extracted_at: new Date().toISOString(),
            summary: {
                total_threads: ThreadManager.threads.length,
                current_thread_id: currentThread?.id || null,
                current_thread_title: currentThread?.title || null,
                threads_by_location: this.groupThreadsByLocation()
            },
            current_thread_detail: currentThread ? {
                id: currentThread.id,
                title: currentThread.title,
                location: currentThread.location,
                created: currentThread.created,
                updated: currentThread.updated,
                message_count: currentThread.messages?.length || 0,
                messages: (currentThread.messages || []).map((msg, idx) => ({
                    index: idx,
                    role: msg.role,
                    content_preview: typeof msg.content === 'string'
                        ? msg.content.substring(0, 100) + '...'
                        : JSON.stringify(msg.content).substring(0, 100) + '...',
                    content_length: typeof msg.content === 'string'
                        ? msg.content.length
                        : JSON.stringify(msg.content).length,
                    timestamp: msg.timestamp || 'unknown'
                }))
            } : null,
            all_threads_structure: ThreadManager.threads.map(thread => ({
                id: thread.id,
                title: thread.title,
                location: thread.location,
                message_count: thread.messages?.length || 0,
                message_roles: (thread.messages || []).map(m => m.role),
                created: thread.created,
                updated: thread.updated,
                has_tool_use: (thread.messages || []).some(m => m.role === 'assistant' &&
                    (m.content?.some?.(c => c.type === 'tool_use') || false)),
                has_tool_result: (thread.messages || []).some(m => m.role === 'user' &&
                    (m.content?.some?.(c => c.type === 'tool_result') || false))
            })),
            appstate_messages: this.extractAppStateMessages()
        };
    },

    /**
     * Group threads by location
     */
    groupThreadsByLocation() {
        if (typeof ThreadManager === 'undefined') return {};

        const grouped = {};
        ThreadManager.threads.forEach(thread => {
            const loc = thread.location || 'unknown';
            if (!grouped[loc]) {
                grouped[loc] = [];
            }
            grouped[loc].push({
                id: thread.id,
                title: thread.title,
                message_count: thread.messages?.length || 0
            });
        });
        return grouped;
    },

    /**
     * Extract AppState messages structure
     */
    extractAppStateMessages() {
        if (typeof AppState === 'undefined' || !AppState.chatMessages) {
            return { error: 'AppState not available' };
        }

        return {
            total_messages: AppState.chatMessages.length,
            message_sequence: AppState.chatMessages.map((msg, idx) => ({
                index: idx,
                role: msg.role,
                has_content: !!msg.content,
                content_type: Array.isArray(msg.content) ? 'array' : typeof msg.content,
                content_blocks: Array.isArray(msg.content) ? msg.content.length : null,
                block_types: Array.isArray(msg.content)
                    ? msg.content.map(c => c.type || 'text')
                    : null
            })),
            role_distribution: this.getRoleDistribution(AppState.chatMessages),
            has_tool_blocks: AppState.chatMessages.some(m =>
                Array.isArray(m.content) && m.content.some(c =>
                    c.type === 'tool_use' || c.type === 'tool_result'
                )
            )
        };
    },

    /**
     * Get role distribution
     */
    getRoleDistribution(messages) {
        const dist = {};
        messages.forEach(msg => {
            dist[msg.role] = (dist[msg.role] || 0) + 1;
        });
        return dist;
    },

    /**
     * ENHANCED: Extract clean console logs (filtered)
     */
    extractConsoleLogs() {
        return {
            extracted_at: new Date().toISOString(),
            total_captured: this.logs.length,
            filters: this.filters,
            logs_by_level: {
                log: this.logs.filter(l => l.level === 'log').length,
                warn: this.logs.filter(l => l.level === 'warn').length,
                error: this.logs.filter(l => l.level === 'error').length
            },
            recent_logs: this.logs.slice(-100).map(log => ({
                time: log.timestamp,
                level: log.level,
                message: log.message,
                stack: log.stack
            })),
            error_logs: this.logs.filter(l => l.level === 'error').map(log => ({
                time: log.timestamp,
                message: log.message,
                stack: log.stack
            })),
            thread_related_logs: this.logs.filter(l =>
                l.message.includes('Thread') ||
                l.message.includes('saveMessages') ||
                l.message.includes('loadThreads')
            ).map(log => ({
                time: log.timestamp,
                level: log.level,
                message: log.message
            }))
        };
    },

    /**
     * ENHANCED: Extract HTML tree structure
     */
    extractHTMLTree() {
        const extractElement = (element, depth = 0, maxDepth = 5) => {
            if (!element || depth > maxDepth) return null;

            const result = {
                tag: element.tagName?.toLowerCase() || 'text',
                id: element.id || null,
                classes: element.className ? element.className.split(' ').filter(c => c) : [],
                attributes: {},
                children_count: element.children?.length || 0,
                text_preview: element.childNodes?.length === 1 && element.childNodes[0].nodeType === 3
                    ? element.textContent?.substring(0, 50) + '...'
                    : null
            };

            // Extract key attributes
            if (element.attributes) {
                ['data-location', 'data-thread-id', 'data-tab', 'data-section'].forEach(attr => {
                    if (element.hasAttribute(attr)) {
                        result.attributes[attr] = element.getAttribute(attr);
                    }
                });
            }

            return result;
        };

        return {
            extracted_at: new Date().toISOString(),
            document_structure: {
                title: document.title,
                url: window.location.href,
                body_classes: document.body.className.split(' ').filter(c => c)
            },
            key_containers: {
                prime_chat: extractElement(document.getElementById('prime-chat-container'), 0, 3),
                agent_columns: Array.from(document.querySelectorAll('.agent-column')).map(el => ({
                    ...extractElement(el, 0, 2),
                    thread_cards_count: el.querySelectorAll('.thread-card').length
                })),
                synergy_panel: extractElement(document.getElementById('synergy-main-panel'), 0, 3),
                debug_sidebar: extractElement(document.getElementById('debug-sidebar'), 0, 2)
            },
            thread_cards: Array.from(document.querySelectorAll('.thread-card')).map(card => ({
                id: card.id,
                location: card.getAttribute('data-location'),
                thread_id: card.getAttribute('data-thread-id'),
                title: card.querySelector('.thread-card-title')?.textContent?.trim(),
                visible: card.offsetParent !== null
            })),
            active_elements: {
                active_tab: document.querySelector('.tab.active')?.id || null,
                open_modals: Array.from(document.querySelectorAll('.modal')).filter(m =>
                    m.style.display !== 'none'
                ).map(m => m.id),
                visible_sidebars: Array.from(document.querySelectorAll('.sidebar, .automations-sidebar, .debug-sidebar'))
                    .filter(s => !s.classList.contains('collapsed') && s.style.display !== 'none')
                    .map(s => s.id)
            }
        };
    },

    /**
     * Get app state
     */
    getAppState() {
        if (typeof AppState === 'undefined') return null;

        return {
            chat_messages_count: AppState.chatMessages?.length || 0,
            chat_messages_roles: AppState.chatMessages?.map(m => m.role) || []
        };
    },

    /**
     * Export thread structure as JSON
     */
    exportThreadStructure() {
        const data = this.extractThreadStructure();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `thread-structure-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    },

    /**
     * Export console logs as JSON
     */
    exportConsoleLogsJSON() {
        const data = this.extractConsoleLogs();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `console-logs-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    },

    /**
     * Export HTML tree as JSON
     */
    exportHTMLTree() {
        const data = this.extractHTMLTree();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `html-tree-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    },

    /**
     * Export logs as JSON
     */
    exportJSON() {
        const data = this.extractLogs();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `debug-logs-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    },

    /**
     * Export logs as text
     */
    exportText() {
        const data = this.extractLogs();
        const text = data.logs.map(log =>
            `[${log.time}] [${log.level.toUpperCase()}] ${log.message}`
        ).join('\n\n');

        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `debug-logs-${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    },

    /**
     * Copy logs to clipboard
     */
    async copyToClipboard() {
        const data = this.extractLogs();
        const text = JSON.stringify(data, null, 2);

        try {
            await navigator.clipboard.writeText(text);
            if (typeof showNotification === 'function') {
                showNotification('Logs copied to clipboard', 'success');
            }
        } catch (error) {
            console.error('Failed to copy logs:', error);
            if (typeof showNotification === 'function') {
                showNotification('Failed to copy logs', 'error');
            }
        }
    },

    /**
     * Export AppState messages
     */
    exportAppStateMessages() {
        const structure = this.extractThreadStructure();
        const data = {
            extracted_at: new Date().toISOString(),
            appstate_messages: structure.appstate_messages
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `appstate-messages-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    },

    /**
     * Clear logs
     */
    clearLogs() {
        this.logs = [];
    }
};

// Sidebar UI Manager
const DebugSidebar = {
    isOpen: false,
    currentTab: 'logs',
    refreshInterval: null,

    async toggleSidebar() {
        console.log('[DEBUG SIDEBAR] Toggle clicked');

        const sidebar = document.getElementById('debug-sidebar');
        if (!sidebar) {
            console.error('[DEBUG SIDEBAR] Sidebar element not found');
            return;
        }

        this.isOpen = !this.isOpen;

        if (this.isOpen) {
            sidebar.classList.add('open');
            this.render();
            // Start auto-refresh when sidebar opens
            this.startAutoRefresh();
        } else {
            sidebar.classList.remove('open');
            // Stop auto-refresh when sidebar closes
            this.stopAutoRefresh();
        }
    },

    /**
     * Start auto-refresh timer for real-time updates
     */
    startAutoRefresh() {
        if (this.refreshInterval) return; // Already running

        this.refreshInterval = setInterval(() => {
            if (this.isOpen) {
                this.render();
            }
        }, 2000); // Refresh every 2 seconds
    },

    /**
     * Stop auto-refresh timer
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    },

    switchTab(tabId) {
        this.currentTab = tabId;

        // Update tab buttons
        document.querySelectorAll('.debug-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabId);
        });

        // Update sections
        document.querySelectorAll('.debug-section').forEach(section => {
            section.classList.toggle('active', section.dataset.section === tabId);
        });

        this.render();
    },

    render() {
        if (this.currentTab === 'logs') {
            this.renderLogs();
        } else if (this.currentTab === 'threads') {
            this.renderConversation();
        } else if (this.currentTab === 'htmltree') {
            this.renderHTMLTree();
        } else if (this.currentTab === 'dbstructure') {
            this.renderDBStructure();
        } else if (this.currentTab === 'parsing') {
            this.renderParsing();
        } else if (this.currentTab === 'consolelogs') {
            this.renderConsoleLogs();
        } else if (this.currentTab === 'autosave') {
            this.renderAutoSave();
        } else if (this.currentTab === 'validation') {
            this.renderValidation();
        } else if (this.currentTab === 'poolmonitor') {
            this.renderPoolMonitor();
        }
    },

    renderLogs() {
        const output = document.getElementById('debug-log-output');
        const totalElement = document.getElementById('debug-total-logs');
        const filteredElement = document.getElementById('debug-filtered-logs');

        if (!output) return;

        const data = DebugModule.extractLogs();

        // Update stats
        if (totalElement) totalElement.textContent = DebugModule.logs.length;
        if (filteredElement) filteredElement.textContent = data.total_logs;

        // Format logs for display (recent logs only, formatted nicely)
        const recentLogs = data.logs.slice(-50); // Last 50 logs
        const formattedLogs = recentLogs.map(log => {
            const time = new Date(log.time).toLocaleTimeString();
            const levelColor = log.level === 'error' ? '#EF4444' : log.level === 'warn' ? '#F59E0B' : '#10B981';

            // Truncate long tool results if enabled
            let message = log.message;
            if (DebugModule.filters.truncateResults && message.includes('tool_result')) {
                if (message.length > 300) {
                    message = message.substring(0, 300) + '... [TRUNCATED]';
                }
            }

            // Truncate long signatures (base64 strings in "signature":"...")
            message = message.replace(/"signature"\s*:\s*"([^"]{50})[^"]*"/g, '"signature":"$1...[TRUNCATED]"');

            return `[${time}] <span style="color: ${levelColor}">[${log.level.toUpperCase()}]</span> ${message}`;
        }).join('\n\n');

        output.innerHTML = formattedLogs || '<span style="color: #666;">No logs captured yet...</span>';
        // Auto-scroll removed per user request
    },

    copyLogsToClipboard() {
        const output = document.getElementById('debug-log-output');
        if (!output) return;

        const text = output.innerText;
        navigator.clipboard.writeText(text).then(() => {
            alert('Logs copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy logs:', err);
        });
    },

    copyConversationToClipboard() {
        const output = document.getElementById('debug-conversation-content');
        if (!output) return;

        const text = output.innerText;
        navigator.clipboard.writeText(text).then(() => {
            alert('Conversation data copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy conversation:', err);
        });
    },

    renderHTMLTree() {
        const output = document.getElementById('debug-htmltree-output');
        if (!output) return;

        const treeData = DebugModule.extractHTMLTree();

        if (!treeData || treeData.error) {
            output.innerHTML = `<span style="color: #EF4444;">${treeData?.error || 'Failed to extract HTML tree'}</span>`;
            return;
        }

        // Format the structured data for display
        const formatElement = (el, label, indent = 0) => {
            if (!el) return '';
            const indentStr = '  '.repeat(indent);
            let result = `${indentStr}<span style="color: #10B981;">${label}:</span>\n`;
            result += `${indentStr}  <span style="color: #3B82F6;">&lt;${el.tag}&gt;</span>`;
            if (el.id) result += ` <span style="color: #F59E0B;">#${el.id}</span>`;
            if (el.classes && el.classes.length > 0) result += ` <span style="color: #8B5CF6;">.${el.classes.join('.')}</span>`;
            if (el.children_count > 0) result += ` <span style="color: #666;">(${el.children_count} children)</span>`;
            result += '\n';
            return result;
        };

        let treeText = '';

        // Document Structure
        treeText += '<span style="color: #10B981; font-weight: bold;">📄 DOCUMENT</span>\n';
        treeText += `  Title: ${treeData.document_structure.title}\n`;
        treeText += `  Body Classes: ${treeData.document_structure.body_classes.join(', ') || '(none)'}\n\n`;

        // Key Containers
        treeText += '<span style="color: #10B981; font-weight: bold;">📦 KEY CONTAINERS</span>\n';
        treeText += formatElement(treeData.key_containers.prime_chat, 'Prime Chat', 1);

        if (treeData.key_containers.agent_columns && treeData.key_containers.agent_columns.length > 0) {
            treeText += `  <span style="color: #10B981;">Agent Columns:</span> ${treeData.key_containers.agent_columns.length}\n`;
            treeData.key_containers.agent_columns.forEach((col, idx) => {
                if (col.tag) {
                    treeText += `    [${idx}] <span style="color: #3B82F6;">&lt;${col.tag}&gt;</span>`;
                    if (col.id) treeText += ` <span style="color: #F59E0B;">#${col.id}</span>`;
                    treeText += ` <span style="color: #666;">(${col.thread_cards_count} threads)</span>\n`;
                }
            });
        }

        treeText += formatElement(treeData.key_containers.synergy_panel, 'Synergy Panel', 1);
        treeText += formatElement(treeData.key_containers.debug_sidebar, 'Debug Sidebar', 1);
        treeText += '\n';

        // Thread Cards
        if (treeData.thread_cards && treeData.thread_cards.length > 0) {
            treeText += `<span style="color: #10B981; font-weight: bold;">💬 THREAD CARDS</span> (${treeData.thread_cards.length})\n`;
            treeData.thread_cards.forEach((card, idx) => {
                const visIcon = card.visible ? '👁️' : '🚫';
                treeText += `  ${visIcon} [${idx}] <span style="color: #F59E0B;">#${card.id || 'no-id'}</span> - ${card.title || 'Untitled'}\n`;
                treeText += `      Location: ${card.location || 'unknown'} | Thread ID: ${card.thread_id || 'none'}\n`;
            });
            treeText += '\n';
        }

        // Active Elements
        treeText += '<span style="color: #10B981; font-weight: bold;">✨ ACTIVE ELEMENTS</span>\n';
        treeText += `  Active Tab: <span style="color: #F59E0B;">${treeData.active_elements.active_tab || '(none)'}</span>\n`;
        treeText += `  Open Modals: ${treeData.active_elements.open_modals.length > 0 ? treeData.active_elements.open_modals.join(', ') : '(none)'}\n`;
        treeText += `  Visible Sidebars: ${treeData.active_elements.visible_sidebars.length > 0 ? treeData.active_elements.visible_sidebars.join(', ') : '(none)'}\n`;

        output.innerHTML = `<pre style="margin: 0; font-size: 11px; line-height: 1.8; color: #d4d4d4;">${treeText}</pre>`;
    },

    copyHTMLTreeToClipboard() {
        const output = document.getElementById('debug-htmltree-output');
        if (!output) return;

        const text = output.innerText;
        navigator.clipboard.writeText(text).then(() => {
            alert('HTML Tree copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy HTML tree:', err);
        });
    }, renderThreads() {
        const container = document.getElementById('debug-threads-content');
        if (!container) return;

        const structure = DebugModule.extractThreadStructure();
        if (structure.error) {
            container.innerHTML = `<p style="color: var(--text-secondary);">${structure.error}</p>`;
            return;
        }

        // Group threads by location
        const groupedHTML = Object.entries(structure.summary.threads_by_location || {})
            .map(([location, threads]) => `
                <div style="margin-bottom: 20px;">
                    <h4 style="color: var(--accent-primary); font-size: 14px; margin-bottom: 10px;">
                        <i class="fas fa-map-marker-alt"></i> ${location.toUpperCase()} (${threads.length})
                    </h4>
                    <div class="debug-thread-list">
                        ${threads.map(t => `
                            <div class="debug-thread-item" style="padding: 8px; margin-bottom: 6px;">
                                <div class="debug-thread-title" style="font-size: 13px;">${t.title}</div>
                                <div class="debug-thread-meta" style="font-size: 11px;">
                                    <span><i class="fas fa-hashtag"></i> ${t.id.substring(0, 10)}</span>
                                    <span><i class="fas fa-envelope"></i> ${t.message_count} msgs</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `).join('');

        // Current thread detail
        const currentThreadHTML = structure.current_thread_detail ? `
            <div style="background: var(--bg-tertiary); padding: 16px; border-radius: 8px; margin-top: 20px;">
                <h4 style="color: var(--accent-primary); margin-bottom: 12px;">
                    <i class="fas fa-star"></i> Current Thread Details
                </h4>
                <div style="font-size: 13px; line-height: 1.6;">
                    <div><strong>Title:</strong> ${structure.current_thread_detail.title}</div>
                    <div><strong>ID:</strong> ${structure.current_thread_detail.id}</div>
                    <div><strong>Location:</strong> ${structure.current_thread_detail.location}</div>
                    <div><strong>Messages:</strong> ${structure.current_thread_detail.message_count}</div>
                    <div style="margin-top: 12px;"><strong>Message Sequence:</strong></div>
                    <div style="font-family: monospace; font-size: 11px; background: #1e1e1e; padding: 8px; border-radius: 4px; margin-top: 6px; max-height: 200px; overflow-y: auto;">
                        ${structure.current_thread_detail.messages.map(msg =>
            `${msg.index}: ${msg.role} (${msg.content_length} chars)`
        ).join('\n')}
                    </div>
                </div>
            </div>
        ` : '';

        container.innerHTML = `
            <div class="debug-stats-grid">
                <div class="debug-stat-card">
                    <div class="debug-stat-label">Total Threads</div>
                    <div class="debug-stat-value">${structure.summary.total_threads}</div>
                </div>
                <div class="debug-stat-card">
                    <div class="debug-stat-label">Current Thread</div>
                    <div class="debug-stat-value">${structure.summary.current_thread_id ? structure.summary.current_thread_id.substring(0, 10) : 'None'}</div>
                </div>
                <div class="debug-stat-card">
                    <div class="debug-stat-label">Locations</div>
                    <div class="debug-stat-value">${Object.keys(structure.summary.threads_by_location || {}).length}</div>
                </div>
            </div>
            ${groupedHTML}
            ${currentThreadHTML}
        `;
    },

    renderMessages() {
        const container = document.getElementById('debug-messages-content');
        if (!container) return;

        const structure = DebugModule.extractThreadStructure();
        const appStateMessages = structure.appstate_messages;

        if (appStateMessages.error) {
            container.innerHTML = `<p style="color: var(--text-secondary);">${appStateMessages.error}</p>`;
            return;
        }

        // Role distribution
        const roleDistHTML = Object.entries(appStateMessages.role_distribution || {})
            .map(([role, count]) => `
                <div class="debug-stat-card">
                    <div class="debug-stat-label">${role}</div>
                    <div class="debug-stat-value">${count}</div>
                </div>
            `).join('');

        // Message sequence with block types
        const sequenceHTML = (appStateMessages.message_sequence || []).map(msg => {
            const blockInfo = msg.block_types ? ` [${msg.block_types.join(', ')}]` : '';
            return `${msg.index}: ${msg.role}${blockInfo} (${msg.content_type})`;
        }).join('\n');

        container.innerHTML = `
            <div class="debug-stats-grid">
                <div class="debug-stat-card">
                    <div class="debug-stat-label">Total Messages</div>
                    <div class="debug-stat-value">${appStateMessages.total_messages}</div>
                </div>
                ${roleDistHTML}
                <div class="debug-stat-card" style="grid-column: span 2;">
                    <div class="debug-stat-label">Has Tool Blocks</div>
                    <div class="debug-stat-value" style="color: ${appStateMessages.has_tool_blocks ? '#10B981' : '#EF4444'}">
                        ${appStateMessages.has_tool_blocks ? 'YES' : 'NO'}
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <h4 style="color: var(--accent-primary); font-size: 14px; margin-bottom: 10px;">
                    <i class="fas fa-list-ol"></i> Message Sequence & Structure
                </h4>
                <div class="debug-log-output" style="max-height: 400px;">
${sequenceHTML}
                </div>
            </div>

            <div style="margin-top: 20px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px; font-size: 12px;">
                <strong>Legend:</strong><br>
                • <code>text</code> - Simple text message<br>
                • <code>tool_use</code> - AI requesting to use a tool<br>
                • <code>tool_result</code> - Result from tool execution<br>
                • <code>array</code> - Multiple content blocks (text + tool_use/tool_result)
            </div>
        `;
    },

    renderConversation() {
        const container = document.getElementById('debug-conversation-content');
        if (!container) return;

        const structure = DebugModule.extractThreadStructure();
        const appStateMessages = structure.appstate_messages;

        if (appStateMessages.error) {
            container.innerHTML = `<p style="color: var(--text-secondary);">${appStateMessages.error}</p>`;
            return;
        }

        // Count actual user/AI exchanges (not bubbles)
        const messages = appStateMessages.messages || [];
        let userCount = 0;
        let aiCount = 0;
        let bubbleCount = 0;

        // Group bubbles by message exchange
        const messageGroups = [];
        let currentGroup = null;

        messages.forEach((msg, idx) => {
            if (msg.role === 'user') {
                if (currentGroup) {
                    messageGroups.push(currentGroup);
                }
                currentGroup = {
                    exchangeNum: userCount + 1,
                    user: msg,
                    ai: []
                };
                userCount++;
            } else if (msg.role === 'assistant' && currentGroup) {
                currentGroup.ai.push(msg);
                aiCount++;
            }
            bubbleCount++;
        });
        if (currentGroup) {
            messageGroups.push(currentGroup);
        }

        // Build conversation display
        const conversationHTML = messageGroups.map((group, idx) => {
            const userBubbles = this.formatMessageBubbles(group.user, 'User');
            const aiBubbles = group.ai.map(ai => this.formatMessageBubbles(ai, 'AI')).join('');

            return `
                <div style="margin-bottom: 24px; padding: 16px; background: var(--bg-tertiary); border-radius: 8px; border-left: 3px solid var(--accent-primary);">
                    <h4 style="color: var(--accent-primary); margin-bottom: 12px; font-size: 13px;">
                        Exchange #${idx + 1}
                    </h4>
                    ${userBubbles}
                    ${aiBubbles}
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="debug-stats-grid" style="margin-bottom: 20px;">
                <div class="debug-stat-card">
                    <div class="debug-stat-label">User Messages</div>
                    <div class="debug-stat-value">${userCount}</div>
                </div>
                <div class="debug-stat-card">
                    <div class="debug-stat-label">AI Responses</div>
                    <div class="debug-stat-value">${aiCount}</div>
                </div>
                <div class="debug-stat-card">
                    <div class="debug-stat-label">Total Bubbles</div>
                    <div class="debug-stat-value">${bubbleCount}</div>
                </div>
                <div class="debug-stat-card">
                    <div class="debug-stat-label">Has Tools</div>
                    <div class="debug-stat-value" style="color: ${appStateMessages.has_tool_blocks ? '#10B981' : '#999'}">
                        ${appStateMessages.has_tool_blocks ? 'YES' : 'NO'}
                    </div>
                </div>
            </div>
            
            <div style="max-height: calc(100vh - 400px); overflow-y: auto;">
                ${conversationHTML || '<p style="color: var(--text-secondary);">No messages in conversation</p>'}
            </div>
        `;
    },

    formatMessageBubbles(message, roleLabel) {
        if (!message) return '';

        const content = message.content;
        const isArray = Array.isArray(content);

        if (!isArray) {
            // Simple text message
            const charCount = typeof content === 'string' ? content.length : JSON.stringify(content).length;
            return `
                <div style="font-family: monospace; font-size: 11px; padding: 8px; margin: 4px 0; background: #1e1e1e; border-radius: 4px; border-left: 3px solid ${roleLabel === 'User' ? '#3B82F6' : '#10B981'};">
                    <strong style="color: ${roleLabel === 'User' ? '#3B82F6' : '#10B981'};">${roleLabel}</strong> • 
                    <span style="color: #666;">${charCount} chars</span> • 
                    <span style="color: #888;">text</span>
                </div>
            `;
        }

        // Array of blocks (thinking/tool_use/tool_result/text)
        return content.map((block, idx) => {
            const blockType = block.type || 'unknown';
            let charCount = 0;
            let typeLabel = blockType;
            let typeColor = '#888';

            if (blockType === 'text') {
                charCount = block.text ? block.text.length : 0;
                typeColor = '#10B981';
            } else if (blockType === 'thinking') {
                charCount = block.thinking ? block.thinking.length : 0;
                typeColor = '#8B5CF6';
                typeLabel = 'thinking';
            } else if (blockType === 'tool_use') {
                charCount = JSON.stringify(block.input || {}).length;
                typeColor = '#F59E0B';
                typeLabel = `tool_use: ${block.name || 'unknown'}`;
            } else if (blockType === 'tool_result') {
                charCount = JSON.stringify(block.content || '').length;
                typeColor = '#06B6D4';
                typeLabel = 'tool_result';
            }

            return `
                <div style="font-family: monospace; font-size: 11px; padding: 8px; margin: 4px 0; background: #1e1e1e; border-radius: 4px; border-left: 3px solid ${roleLabel === 'User' ? '#3B82F6' : '#10B981'};">
                    <strong style="color: ${roleLabel === 'User' ? '#3B82F6' : '#10B981'};">${roleLabel}</strong> • 
                    Bubble #${idx + 1} • 
                    <span style="color: #666;">${charCount} chars</span> • 
                    <span style="color: ${typeColor};">${typeLabel}</span>
                </div>
            `;
        }).join('');
    },

    // ==================== NEW TEST TABS ====================

    /**
     * TEST 1: Database Structure - Check message content format
     */
    renderDBStructure() {
        const output = document.getElementById('debug-dbstructure-output');
        if (!output) return;

        const currentThread = ThreadManager?.getCurrentThread();
        if (!currentThread || !currentThread.messages || currentThread.messages.length === 0) {
            output.innerHTML = '<span style="color: #666;">No messages in current thread</span>';
            return;
        }

        const messages = currentThread.messages.slice(-5); // Last 5 messages
        let report = '<div style="font-family: monospace; font-size: 11px; line-height: 1.8;">';

        report += '<div style="color: #10B981; font-weight: bold; margin-bottom: 12px;">📊 MESSAGE CONTENT STRUCTURE</div>\n\n';

        messages.forEach((msg, idx) => {
            const contentType = typeof msg.content;
            const isString = contentType === 'string';
            const isArray = Array.isArray(msg.content);
            const isObject = contentType === 'object' && !isArray;

            let preview = '';
            let structureIcon = '';
            let structureColor = '';

            if (isString) {
                structureIcon = '📝';
                structureColor = '#F59E0B';
                preview = msg.content.substring(0, 100);
                // Check if it looks like JSON
                if (msg.content.trim().startsWith('[') || msg.content.trim().startsWith('{')) {
                    structureIcon = '⚠️';
                    structureColor = '#EF4444';
                    preview = '⚠️ STRING CONTAINING JSON (needs parsing!)';
                }
            } else if (isArray) {
                structureIcon = '✅';
                structureColor = '#10B981';
                preview = `Array with ${msg.content.length} blocks: [${msg.content.map(c => c.type || 'unknown').join(', ')}]`;
            } else if (isObject) {
                structureIcon = '📦';
                structureColor = '#3B82F6';
                preview = `Object with keys: ${Object.keys(msg.content).join(', ')}`;
            }

            report += `<div style="margin-bottom: 16px; padding: 12px; background: #1e1e1e; border-radius: 6px; border-left: 3px solid ${structureColor};">\n`;
            report += `  <div style="color: ${structureColor}; font-weight: bold;">${structureIcon} Message ${idx + 1} - ${msg.role}</div>\n`;
            report += `  <div style="color: #888; margin-top: 4px;">Type: <span style="color: ${structureColor};">${contentType}${isArray ? ' (array)' : ''}</span></div>\n`;
            report += `  <div style="color: #ccc; margin-top: 6px; font-size: 10px; word-break: break-all;">${preview}</div>\n`;

            // Show structure test
            if (isString && (msg.content.trim().startsWith('[') || msg.content.trim().startsWith('{'))) {
                report += `  <div style="color: #EF4444; margin-top: 8px; padding: 6px; background: rgba(239, 68, 68, 0.1); border-radius: 4px;">\n`;
                report += `    ❌ PROBLEM: Content is JSON string, not parsed array\n`;
                report += `    ✅ SOLUTION: JSON.parse() needed in loadThreadsFromBackend()\n`;
                report += `  </div>\n`;
            } else if (isArray) {
                report += `  <div style="color: #10B981; margin-top: 8px; padding: 6px; background: rgba(16, 185, 129, 0.1); border-radius: 4px;">\n`;
                report += `    ✅ CORRECT: Content is properly parsed array\n`;
                report += `  </div>\n`;
            }

            report += `</div>\n\n`;
        });

        report += '<div style="margin-top: 16px; padding: 12px; background: #2d2d2d; border-radius: 6px;">\n';
        report += '<div style="color: #10B981; font-weight: bold; margin-bottom: 8px;">🎯 EXPECTED BEHAVIOR:</div>\n';
        report += '<div style="color: #ccc; font-size: 10px; line-height: 1.6;">\n';
        report += '• Database stores content as JSON string: "[{\\"type\\":\\"text\\",\\"text\\":\\"Hello\\"}]"\n';
        report += '• Frontend MUST parse: JSON.parse(msg.content) → [{type: "text", text: "Hello"}]\n';
        report += '• Result: content becomes array of content blocks\n';
        report += '</div>\n';
        report += '</div>\n';

        report += '</div>';
        output.innerHTML = report;
    },

    copyDBStructureToClipboard() {
        const output = document.getElementById('debug-dbstructure-output');
        if (!output) return;
        navigator.clipboard.writeText(output.innerText).then(() => {
            alert('DB Structure report copied to clipboard!');
        });
    },

    /**
     * TEST 2: Message Parsing - Test JSON.parse() behavior
     */
    renderParsing() {
        const output = document.getElementById('debug-parsing-output');
        if (!output) return;

        const currentThread = ThreadManager?.getCurrentThread();
        if (!currentThread || !currentThread.messages || currentThread.messages.length === 0) {
            output.innerHTML = '<span style="color: #666;">No messages in current thread</span>';
            return;
        }

        let report = '<div style="font-family: monospace; font-size: 11px; line-height: 1.8;">';
        report += '<div style="color: #10B981; font-weight: bold; margin-bottom: 12px;">🧪 JSON PARSING TEST</div>\n\n';

        const testMessage = currentThread.messages[0];
        const rawContent = testMessage.content;

        report += '<div style="padding: 12px; background: #1e1e1e; border-radius: 6px; margin-bottom: 16px;">\n';
        report += '<div style="color: #F59E0B; font-weight: bold;">RAW CONTENT:</div>\n';
        report += `<div style="color: #888; margin-top: 4px;">Type: ${typeof rawContent}</div>\n`;
        report += `<div style="color: #ccc; margin-top: 6px; font-size: 10px; word-break: break-all;">${JSON.stringify(rawContent).substring(0, 200)}...</div>\n`;
        report += '</div>\n\n';

        // Test parsing
        let parseResult = null;
        let parseError = null;

        if (typeof rawContent === 'string') {
            try {
                parseResult = JSON.parse(rawContent);
                report += '<div style="padding: 12px; background: #1e1e1e; border-radius: 6px; margin-bottom: 16px; border-left: 3px solid #10B981;">\n';
                report += '<div style="color: #10B981; font-weight: bold;">✅ PARSE SUCCESSFUL:</div>\n';
                report += `<div style="color: #888; margin-top: 4px;">Result Type: ${Array.isArray(parseResult) ? 'array' : typeof parseResult}</div>\n`;
                if (Array.isArray(parseResult)) {
                    report += `<div style="color: #888;">Array Length: ${parseResult.length}</div>\n`;
                    report += `<div style="color: #888;">Block Types: [${parseResult.map(c => c.type || 'unknown').join(', ')}]</div>\n`;
                }
                report += `<div style="color: #ccc; margin-top: 6px; font-size: 10px;">${JSON.stringify(parseResult, null, 2).substring(0, 300)}...</div>\n`;
                report += '</div>\n\n';
            } catch (e) {
                parseError = e.message;
                report += '<div style="padding: 12px; background: #1e1e1e; border-radius: 6px; margin-bottom: 16px; border-left: 3px solid #EF4444;">\n';
                report += '<div style="color: #EF4444; font-weight: bold;">❌ PARSE FAILED:</div>\n';
                report += `<div style="color: #EF4444; margin-top: 6px;">${e.message}</div>\n`;
                report += '</div>\n\n';
            }
        } else {
            report += '<div style="padding: 12px; background: #1e1e1e; border-radius: 6px; margin-bottom: 16px; border-left: 3px solid #3B82F6;">\n';
            report += '<div style="color: #3B82F6; font-weight: bold;">ℹ️ NO PARSING NEEDED:</div>\n';
            report += '<div style="color: #888; margin-top: 4px;">Content is already a JavaScript object/array</div>\n';
            report += '</div>\n\n';
        }

        // Show fix location
        report += '<div style="padding: 12px; background: #2d2d2d; border-radius: 6px;">\n';
        report += '<div style="color: #10B981; font-weight: bold; margin-bottom: 8px;">📍 FIX LOCATION:</div>\n';
        report += '<div style="color: #ccc; font-size: 10px; line-height: 1.6;">\n';
        report += '<span style="color: #F59E0B;">File:</span> modules/thread-manager/thread-manager-core.js\n';
        report += '<span style="color: #F59E0B;">Function:</span> loadThreadsFromBackend()\n';
        report += '<span style="color: #F59E0B;">Lines:</span> 237-262\n\n';
        report += '<span style="color: #10B981;">Code:</span>\n';
        report += 'const messages = (thread.messages || []).map(msg => {\n';
        report += '  if (typeof msg.content === \'string\') {\n';
        report += '    try {\n';
        report += '      return { ...msg, content: JSON.parse(msg.content) };\n';
        report += '    } catch (e) { return msg; }\n';
        report += '  }\n';
        report += '  return msg;\n';
        report += '});\n';
        report += '</div>\n';
        report += '</div>\n';

        report += '</div>';
        output.innerHTML = report;
    },

    copyParsingToClipboard() {
        const output = document.getElementById('debug-parsing-output');
        if (!output) return;
        navigator.clipboard.writeText(output.innerText).then(() => {
            alert('Parsing test copied to clipboard!');
        });
    },

    /**
     * TEST 3: Console Logs - Filtered thread-related logs
     */
    renderConsoleLogs() {
        const output = document.getElementById('debug-consolelogs-output');
        if (!output) return;

        const threadLogs = DebugModule.logs.filter(log =>
            log.message.includes('Thread') ||
            log.message.includes('saveMessages') ||
            log.message.includes('loadThreads') ||
            log.message.includes('[Interactions]') ||
            log.message.includes('[AutoSave]') ||
            log.message.includes('[MESSAGE SAVE]')
        );

        if (threadLogs.length === 0) {
            output.innerHTML = '<span style="color: #666;">No thread-related logs captured yet</span>';
            return;
        }

        const recentLogs = threadLogs.slice(-30);
        const formatted = recentLogs.map(log => {
            const time = new Date(log.time).toLocaleTimeString();
            const levelColor = log.level === 'error' ? '#EF4444' : log.level === 'warn' ? '#F59E0B' : '#10B981';
            return `[${time}] <span style="color: ${levelColor}">[${log.level.toUpperCase()}]</span> ${log.message}`;
        }).join('\n\n');

        output.innerHTML = `<pre style="margin: 0; font-size: 11px; line-height: 1.8;">${formatted}</pre>`;
    },

    copyConsoleLogsToClipboard() {
        const output = document.getElementById('debug-consolelogs-output');
        if (!output) return;
        navigator.clipboard.writeText(output.innerText).then(() => {
            alert('Console logs copied to clipboard!');
        });
    },

    /**
     * TEST 4: Auto-Save Timing - Track save intervals
     */
    renderAutoSave() {
        const output = document.getElementById('debug-autosave-output');
        if (!output) return;

        const saveLogs = DebugModule.logs.filter(log =>
            log.message.includes('[AutoSave]') ||
            log.message.includes('saveThreadToBackend') ||
            log.message.includes('saveMessagesToBackend')
        );

        if (saveLogs.length === 0) {
            output.innerHTML = '<span style="color: #666;">No save operations captured yet. Wait for auto-save...</span>';
            return;
        }

        // Calculate intervals between saves
        const intervals = [];
        for (let i = 1; i < saveLogs.length; i++) {
            const prev = new Date(saveLogs[i - 1].timestamp);
            const curr = new Date(saveLogs[i].timestamp);
            const diffSeconds = (curr - prev) / 1000;
            intervals.push({ time: curr.toLocaleTimeString(), interval: diffSeconds });
        }

        let report = '<div style="font-family: monospace; font-size: 11px; line-height: 1.8;">';
        report += '<div style="color: #10B981; font-weight: bold; margin-bottom: 12px;">⏱️ AUTO-SAVE TIMING ANALYSIS</div>\n\n';

        // Stats
        const avgInterval = intervals.length > 0 ? intervals.reduce((sum, i) => sum + i.interval, 0) / intervals.length : 0;
        const minInterval = intervals.length > 0 ? Math.min(...intervals.map(i => i.interval)) : 0;
        const maxInterval = intervals.length > 0 ? Math.max(...intervals.map(i => i.interval)) : 0;

        report += '<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 16px;">\n';
        report += `<div style="padding: 12px; background: #1e1e1e; border-radius: 6px; text-align: center;">\n`;
        report += `  <div style="color: #888; font-size: 10px;">AVERAGE</div>\n`;
        report += `  <div style="color: ${avgInterval >= 55 && avgInterval <= 65 ? '#10B981' : '#EF4444'}; font-size: 18px; font-weight: bold;">${avgInterval.toFixed(1)}s</div>\n`;
        report += `</div>\n`;
        report += `<div style="padding: 12px; background: #1e1e1e; border-radius: 6px; text-align: center;">\n`;
        report += `  <div style="color: #888; font-size: 10px;">MIN</div>\n`;
        report += `  <div style="color: #3B82F6; font-size: 18px; font-weight: bold;">${minInterval.toFixed(1)}s</div>\n`;
        report += `</div>\n`;
        report += `<div style="padding: 12px; background: #1e1e1e; border-radius: 6px; text-align: center;">\n`;
        report += `  <div style="color: #888; font-size: 10px;">MAX</div>\n`;
        report += `  <div style="color: #F59E0B; font-size: 18px; font-weight: bold;">${maxInterval.toFixed(1)}s</div>\n`;
        report += `</div>\n`;
        report += '</div>\n\n';

        // Recent intervals
        report += '<div style="color: #F59E0B; font-weight: bold; margin-bottom: 8px;">RECENT SAVE INTERVALS:</div>\n';
        intervals.slice(-10).forEach((interval, idx) => {
            const color = interval.interval >= 55 && interval.interval <= 65 ? '#10B981' : '#EF4444';
            const icon = interval.interval >= 55 && interval.interval <= 65 ? '✅' : '⚠️';
            report += `<div style="padding: 6px; margin-bottom: 4px; background: #1e1e1e; border-radius: 4px;">\n`;
            report += `  ${icon} [${interval.time}] <span style="color: ${color};">${interval.interval.toFixed(1)}s</span> since last save\n`;
            report += `</div>\n`;
        });

        report += '\n<div style="margin-top: 16px; padding: 12px; background: #2d2d2d; border-radius: 6px;">\n';
        report += '<div style="color: #10B981; font-weight: bold; margin-bottom: 8px;">🎯 EXPECTED BEHAVIOR:</div>\n';
        report += '<div style="color: #ccc; font-size: 10px; line-height: 1.6;">\n';
        report += '• Auto-save interval: 60 seconds ±5s tolerance\n';
        report += '• NO immediate saves after each message\n';
        report += '• Config: thread-manager-core.js line 335 (setInterval 60000ms)\n';
        report += `• Current status: ${avgInterval >= 55 && avgInterval <= 65 ? '✅ CORRECT' : '❌ NEEDS FIX'}\n`;
        report += '</div>\n';
        report += '</div>\n';

        report += '</div>';
        output.innerHTML = report;
    },

    copyAutoSaveToClipboard() {
        const output = document.getElementById('debug-autosave-output');
        if (!output) return;
        navigator.clipboard.writeText(output.innerText).then(() => {
            alert('Auto-save timing copied to clipboard!');
        });
    },

    /**
     * TEST 5: Validation Status - Check tool_use/tool_result pairing
     */
    renderValidation() {
        const output = document.getElementById('debug-validation-output');
        if (!output) return;

        const currentThread = ThreadManager?.getCurrentThread();
        if (!currentThread || !currentThread.messages || currentThread.messages.length === 0) {
            output.innerHTML = '<span style="color: #666;">No messages in current thread</span>';
            return;
        }

        let report = '<div style="font-family: monospace; font-size: 11px; line-height: 1.8;">';
        report += '<div style="color: #10B981; font-weight: bold; margin-bottom: 12px;">🔍 CONVERSATION VALIDATION</div>\n\n';

        const messages = currentThread.messages;
        let toolUseBlocks = [];
        let toolResultBlocks = [];
        let issues = [];

        // Scan for tool blocks
        messages.forEach((msg, msgIdx) => {
            if (Array.isArray(msg.content)) {
                msg.content.forEach((block, blockIdx) => {
                    if (block.type === 'tool_use') {
                        toolUseBlocks.push({
                            msgIdx,
                            blockIdx,
                            id: block.id,
                            name: block.name,
                            role: msg.role
                        });
                    }
                    if (block.type === 'tool_result') {
                        toolResultBlocks.push({
                            msgIdx,
                            blockIdx,
                            tool_use_id: block.tool_use_id,
                            role: msg.role
                        });
                    }
                });
            }
        });

        // Check for orphaned tool_use blocks
        toolUseBlocks.forEach(toolUse => {
            const hasResult = toolResultBlocks.some(result => result.tool_use_id === toolUse.id);
            if (!hasResult) {
                issues.push({
                    type: 'orphaned_tool_use',
                    severity: 'critical',
                    msgIdx: toolUse.msgIdx,
                    details: `tool_use ${toolUse.id} (${toolUse.name}) has no matching tool_result`
                });
            }
        });

        // Check for wrong message order
        messages.forEach((msg, idx) => {
            if (idx > 0) {
                const prevRole = messages[idx - 1].role;
                const currRole = msg.role;
                if (prevRole === currRole) {
                    issues.push({
                        type: 'wrong_order',
                        severity: 'warning',
                        msgIdx: idx,
                        details: `Two consecutive ${currRole} messages (index ${idx - 1} and ${idx})`
                    });
                }
            }
        });

        // Display stats
        report += '<div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; margin-bottom: 16px;">\n';
        report += `<div style="padding: 12px; background: #1e1e1e; border-radius: 6px; text-align: center;">\n`;
        report += `  <div style="color: #888; font-size: 10px;">MESSAGES</div>\n`;
        report += `  <div style="color: #3B82F6; font-size: 18px; font-weight: bold;">${messages.length}</div>\n`;
        report += `</div>\n`;
        report += `<div style="padding: 12px; background: #1e1e1e; border-radius: 6px; text-align: center;">\n`;
        report += `  <div style="color: #888; font-size: 10px;">TOOL USE</div>\n`;
        report += `  <div style="color: #F59E0B; font-size: 18px; font-weight: bold;">${toolUseBlocks.length}</div>\n`;
        report += `</div>\n`;
        report += `<div style="padding: 12px; background: #1e1e1e; border-radius: 6px; text-align: center;">\n`;
        report += `  <div style="color: #888; font-size: 10px;">TOOL RESULT</div>\n`;
        report += `  <div style="color: #06B6D4; font-size: 18px; font-weight: bold;">${toolResultBlocks.length}</div>\n`;
        report += `</div>\n`;
        report += `<div style="padding: 12px; background: #1e1e1e; border-radius: 6px; text-align: center;">\n`;
        report += `  <div style="color: #888; font-size: 10px;">ISSUES</div>\n`;
        report += `  <div style="color: ${issues.length > 0 ? '#EF4444' : '#10B981'}; font-size: 18px; font-weight: bold;">${issues.length}</div>\n`;
        report += `</div>\n`;
        report += '</div>\n\n';

        // Issues
        if (issues.length > 0) {
            report += '<div style="color: #EF4444; font-weight: bold; margin-bottom: 8px;">⚠️ VALIDATION ISSUES FOUND:</div>\n';
            issues.forEach(issue => {
                const color = issue.severity === 'critical' ? '#EF4444' : '#F59E0B';
                report += `<div style="padding: 8px; margin-bottom: 6px; background: rgba(239, 68, 68, 0.1); border-left: 3px solid ${color}; border-radius: 4px;">\n`;
                report += `  <div style="color: ${color}; font-weight: bold;">${issue.severity.toUpperCase()}: ${issue.type}</div>\n`;
                report += `  <div style="color: #ccc; font-size: 10px; margin-top: 4px;">Message ${issue.msgIdx}: ${issue.details}</div>\n`;
                report += `</div>\n`;
            });

            report += '\n<div style="margin-top: 12px; padding: 12px; background: #2d2d2d; border-radius: 6px;">\n';
            report += '<div style="color: #EF4444; font-weight: bold; margin-bottom: 8px;">🔧 FIX LOCATION:</div>\n';
            report += '<div style="color: #ccc; font-size: 10px; line-height: 1.6;">\n';
            report += '<span style="color: #F59E0B;">File:</span> AI_infrastructure/core/combined_agent_worker.py\n';
            report += '<span style="color: #F59E0B;">Function:</span> validate_conversation_history()\n';
            report += '<span style="color: #F59E0B;">Lines:</span> 1920-1980\n\n';
            report += '<span style="color: #10B981;">Fix:</span> ALWAYS truncate at orphaned tool_use (lines 1938-1945)\n';
            report += 'Remove: if ai_thinking_enabled: PRESERVE logic\n';
            report += '</div>\n';
            report += '</div>\n';
        } else {
            report += '<div style="padding: 12px; background: rgba(16, 185, 129, 0.1); border-left: 3px solid #10B981; border-radius: 6px;">\n';
            report += '<div style="color: #10B981; font-weight: bold;">✅ VALIDATION PASSED</div>\n';
            report += '<div style="color: #ccc; font-size: 10px; margin-top: 4px;">All tool_use blocks have matching tool_result blocks</div>\n';
            report += '<div style="color: #ccc; font-size: 10px;">Message sequence is correct (alternating user/assistant)</div>\n';
            report += '</div>\n';
        }

        report += '</div>';
        output.innerHTML = report;
    },

    copyValidationToClipboard() {
        const output = document.getElementById('debug-validation-output');
        if (!output) return;
        navigator.clipboard.writeText(output.innerText).then(() => {
            alert('Validation report copied to clipboard!');
        });
    },

    async renderPoolMonitor() {
        const output = document.getElementById('debug-poolmonitor-output');
        if (!output) return;

        try {
            const response = await fetch('/api/pool/stats');
            const data = await response.json();

            const healthResponse = await fetch('/api/pool/health');
            const healthData = await healthResponse.json();

            // Fetch live connections
            let liveData = null;
            try {
                const liveResponse = await fetch('/api/pool/connections/live');
                liveData = await liveResponse.json();
            } catch (e) {
                console.warn('Live connections unavailable:', e);
            }

            let html = '<div style="font-family: monospace; font-size: 11px;">';

            // Health Status Card
            const healthColor = healthData.healthy ? '#10B981' : '#EF4444';
            const healthIcon = healthData.healthy ? '✅' : '⚠️';
            html += `<div style="padding: 12px; background: rgba(${healthData.healthy ? '16, 185, 129' : '239, 68, 68'}, 0.1); border-left: 3px solid ${healthColor}; border-radius: 6px; margin-bottom: 16px;">`;
            html += `<div style="color: ${healthColor}; font-weight: bold; margin-bottom: 8px;">${healthIcon} POOL HEALTH: ${healthData.healthy ? 'HEALTHY' : 'WARNING'}</div>`;
            if (healthData.warnings && healthData.warnings.length > 0) {
                html += '<div style="color: #F59E0B; font-size: 10px; margin-top: 4px;">';
                healthData.warnings.forEach(w => {
                    html += `⚠️ ${w}<br>`;
                });
                html += '</div>';
            }
            html += '</div>';

            // Stats Grid
            html += '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">';

            // Pools Created
            html += '<div style="padding: 12px; background: #1e1e1e; border-radius: 6px;">';
            html += '<div style="color: #888; font-size: 9px;">POOLS CREATED</div>';
            html += `<div style="color: #3B82F6; font-size: 24px; font-weight: bold;">${data.pools_created || 0}</div>`;
            html += '</div>';

            // Hit Rate
            const hitRate = ((data.pool_hits || 0) / Math.max(1, (data.pool_hits || 0) + (data.pool_misses || 0)) * 100).toFixed(1);
            const hitRateColor = hitRate > 90 ? '#10B981' : hitRate > 70 ? '#F59E0B' : '#EF4444';
            html += '<div style="padding: 12px; background: #1e1e1e; border-radius: 6px;">';
            html += '<div style="color: #888; font-size: 9px;">HIT RATE</div>';
            html += `<div style="color: ${hitRateColor}; font-size: 24px; font-weight: bold;">${hitRate}%</div>`;
            html += '</div>';

            // Avg Wait Time
            const avgWait = ((data.avg_wait_time || 0) * 1000).toFixed(1);
            const waitColor = avgWait < 50 ? '#10B981' : avgWait < 200 ? '#F59E0B' : '#EF4444';
            html += '<div style="padding: 12px; background: #1e1e1e; border-radius: 6px;">';
            html += '<div style="color: #888; font-size: 9px;">AVG WAIT TIME</div>';
            html += `<div style="color: ${waitColor}; font-size: 24px; font-weight: bold;">${avgWait}<span style="font-size: 12px;">ms</span></div>`;
            html += '</div>';

            // Active Connections
            const activeConns = (data.connections_acquired || 0) - (data.connections_returned || 0);
            const connColor = activeConns < 10 ? '#10B981' : activeConns < 50 ? '#F59E0B' : '#EF4444';
            html += '<div style="padding: 12px; background: #1e1e1e; border-radius: 6px;">';
            html += '<div style="color: #888; font-size: 9px;">ACTIVE CONNS</div>';
            html += `<div style="color: ${connColor}; font-size: 24px; font-weight: bold;">${activeConns}</div>`;
            html += '</div>';

            html += '</div>';

            // Live Connections Section
            if (liveData && liveData.connections) {
                html += '<div style="margin-top: 16px; margin-bottom: 12px;">';
                html += '<div style="color: #10B981; font-weight: bold; margin-bottom: 8px;">🔌 LIVE CONNECTIONS</div>';

                // Summary bar
                html += '<div style="display: flex; gap: 16px; padding: 8px; background: #1e1e1e; border-radius: 4px; margin-bottom: 8px;">';
                html += `<span style="color: #3B82F6;">Total: ${liveData.total_connections}</span>`;
                html += `<span style="color: #10B981;">Active: ${liveData.active_queries}</span>`;
                html += `<span style="color: #888;">Idle: ${liveData.idle_connections}</span>`;
                html += '</div>';

                // Show active queries (limit to 5)
                const activeConns = liveData.connections.filter(c => c.state === 'active').slice(0, 5);
                if (activeConns.length > 0) {
                    html += '<div style="color: #F59E0B; font-size: 10px; font-weight: bold; margin-top: 8px; margin-bottom: 4px;">⚡ ACTIVE QUERIES:</div>';
                    activeConns.forEach(conn => {
                        const duration = conn.duration_seconds ? conn.duration_seconds.toFixed(2) : '0.00';
                        const durationColor = duration > 5 ? '#EF4444' : duration > 1 ? '#F59E0B' : '#10B981';

                        html += '<div style="padding: 6px; margin-bottom: 4px; background: rgba(59, 130, 246, 0.05); border-left: 2px solid #3B82F6; border-radius: 2px;">';
                        html += `<div style="display: flex; justify-content: space-between; align-items: center;">`;
                        html += `<span style="color: #3B82F6; font-size: 10px;">PID ${conn.pid} • ${conn.database}</span>`;
                        html += `<span style="color: ${durationColor}; font-size: 9px;">${duration}s</span>`;
                        html += '</div>';

                        if (conn.query && conn.query.length > 0) {
                            const displayQuery = conn.query.length > 80 ? conn.query.substring(0, 80) + '...' : conn.query;
                            html += `<div style="color: #888; font-size: 9px; margin-top: 2px; font-family: 'Courier New', monospace;">${displayQuery}</div>`;
                        }

                        if (conn.wait_event) {
                            html += `<div style="color: #F59E0B; font-size: 9px; margin-top: 2px;">⏱️ Waiting: ${conn.wait_event}</div>`;
                        }
                        html += '</div>';
                    });
                }

                // Show idle connections count
                if (liveData.idle_connections > 0) {
                    html += `<div style="color: #888; font-size: 9px; margin-top: 6px; padding: 4px;">`;
                    html += `💤 ${liveData.idle_connections} idle connection(s) in pool`;
                    html += '</div>';
                }

                html += '</div>';
            }

            // Pool Details
            if (data.pools && Object.keys(data.pools).length > 0) {
                html += '<div style="color: #10B981; font-weight: bold; margin-bottom: 8px;">📊 POOL CONFIGURATION</div>';
                Object.entries(data.pools).forEach(([name, pool]) => {
                    html += '<div style="padding: 8px; margin-bottom: 6px; background: #1e1e1e; border-radius: 4px;">';
                    html += `<div style="color: #3B82F6; font-weight: bold;">${name}</div>`;
                    html += '<div style="color: #888; font-size: 10px; margin-top: 4px;">';
                    html += `Min: ${pool.min_connections || 0} | Max: ${pool.max_connections || 0} | Status: <span style="color: #10B981;">${pool.status || 'active'}</span>`;
                    html += '</div></div>';
                });
            }

            // Connection Stats
            html += '<div style="margin-top: 16px; padding: 8px; background: #1e1e1e; border-radius: 4px;">';
            html += '<div style="color: #888; font-size: 10px;">';
            html += `Acquired: ${data.connections_acquired || 0} | `;
            html += `Returned: ${data.connections_returned || 0} | `;
            html += `Hits: ${data.pool_hits || 0} | `;
            html += `Misses: ${data.pool_misses || 0}`;
            html += '</div></div>';

            // Link to Full Dashboard
            html += '<div style="margin-top: 16px; padding: 12px; background: rgba(59, 130, 246, 0.1); border-radius: 6px; text-align: center;">';
            html += '<a href="/api/pool/dashboard" target="_blank" style="color: #3B82F6; text-decoration: none; font-weight: bold;">';
            html += '🔷 Open Full Dashboard →';
            html += '</a></div>';

            html += '</div>';
            output.innerHTML = html;

        } catch (error) {
            output.innerHTML = `<div style="color: #EF4444;">Failed to fetch pool stats: ${error.message}</div>`;
        }
    }
};

// Initialize when loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => DebugModule.init());
} else {
    DebugModule.init();
}

// Export to window
window.DebugModule = DebugModule;
window.DebugSidebar = DebugSidebar;

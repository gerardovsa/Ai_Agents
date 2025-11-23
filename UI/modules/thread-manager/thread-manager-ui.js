/**
 * FILE: UI/modules/thread-manager/thread-manager-ui.js
 * PURPOSE: UI rendering for threads - cards, headers, displays
 * 
 * DEPENDENCIES:
 * - UI/modules/thread-manager/thread-manager-core.js (must load first)
 * 
 * EXPORTS:
 * - Extends window.ThreadManager with UI rendering methods
 * 
 * USED BY:
 * - UI/business-ai-platform-v2.html (main application)
 * - UI/modules/thread-manager/thread-manager-crud.js (after CRUD operations)
 * - UI/modules/thread-manager/thread-manager-filters.js (after filtering)
 * 
 * RELATED FILES:
 * - UI/modules/thread-manager/thread-manager-core.js (core object)
 * - UI/modules/thread-manager/thread-manager-interactions.js (event handlers)
 * 
 * NOTES:
 * - Handles all UI rendering logic
 * - Creates thread cards, headers, and visual elements
 * - Pure UI layer - no business logic
 * 
 * LAST MODIFIED: 2025-11-20 - Initial file creation
 */

// UI rendering methods will be defined here
// Awaiting code paste from user


// ==================== THREAD MANAGER - UI MODULE (Part A) ====================
/**
 * UI Rendering & Updates
 * Handles all visual updates and DOM manipulation
 */

window.ThreadManagerUI = {
    /**
     * Render thread list in sidebar
     */
    async renderThreadList() {
        const listContainer = document.getElementById('thread-list');
        if (!listContainer) return;

        // Access ThreadManager's threads array
        const threads = window.ThreadManager.threads || [];

        if (threads.length === 0) {
            listContainer.innerHTML = '<div style="padding: var(--space-4); text-align: center; color: var(--text-secondary);">No threads yet</div>';
            return;
        }

        // Build location mapping
        const threadToLocation = {};
        threads.forEach(thread => {
            if (thread.location && thread.location !== 'prime') {
                threadToLocation[thread.id] = thread.location;
            }
        });

        // Filter threads using ThreadManager's state
        const currentFilter = window.ThreadManager.currentFilter || 'active';
        const searchQuery = window.ThreadManager.searchQuery || '';
        const locationFilter = window.ThreadManager.locationFilter || 'all';
        const activeTagFilter = window.ThreadManager.activeTagFilter || null;
        const dateRangeFilter = window.ThreadManager.dateRangeFilter || { range: 'all', startDate: null };

        const filteredThreads = threads.filter(thread => {
            const isArchived = thread.archived || false;

            // Active/Archived filter
            if (currentFilter === 'archived' ? !isArchived : isArchived) {
                return false;
            }

            // Search query
            if (searchQuery) {
                const query = searchQuery.toLowerCase();
                const titleMatch = thread.title.toLowerCase().includes(query);
                const idMatch = thread.id.includes(query);

                let dateMatch = false;
                if (thread.updated) {
                    const threadDate = new Date(thread.updated);
                    const dateStr = threadDate.toLocaleDateString('en-US', {
                        month: 'short', day: 'numeric', year: 'numeric'
                    }).toLowerCase();
                    dateMatch = dateStr.includes(query);
                }

                if (!titleMatch && !idMatch && !dateMatch) {
                    return false;
                }
            }

            // Location filter
            if (locationFilter && locationFilter !== 'all') {
                const threadLocation = thread.location || 'prime';

                if (locationFilter === 'prime' && threadLocation !== 'prime') {
                    return false;
                } else if (locationFilter === 'all-agents' && threadLocation === 'prime') {
                    return false;
                } else if (locationFilter.startsWith('agent-') && threadLocation !== locationFilter) {
                    return false;
                }
            }

            // Tag filter
            if (activeTagFilter) {
                if (activeTagFilter === 'synergy' && !thread.synergy_card_id) {
                    return false;
                }
                if (activeTagFilter === 'automation' && !thread.automation_workflow_id) {
                    return false;
                }
            }

            // Date range filter
            if (dateRangeFilter && dateRangeFilter.startDate && thread.updated) {
                const threadDate = new Date(thread.updated);
                if (threadDate < dateRangeFilter.startDate) {
                    return false;
                }
            }

            return true;
        });

        if (filteredThreads.length === 0) {
            listContainer.innerHTML = `<div style="padding: var(--space-4); text-align: center; color: var(--text-secondary);">
                ${currentFilter === 'archived' ? 'No archived threads' : 'No active threads'}
            </div>`;
            return;
        }

        // Sort by date based on sortOrder setting
        const sortOrder = this.sortOrder || 'updated';
        if (sortOrder === 'created') {
            // Sort by creation date (oldest first for chronological)
            filteredThreads.sort((a, b) => new Date(a.created) - new Date(b.created));
        } else {
            // Sort by updated date (newest first for recent activity)
            filteredThreads.sort((a, b) => new Date(b.updated) - new Date(a.updated));
        }

        // Group by date
        const groupedThreads = [];
        // thread-manager-ui.js (lines 134-269)
        let currentDateGroup = null;

        filteredThreads.forEach(thread => {
            const dateField = sortOrder === 'created' ? thread.created : thread.updated;
            const threadDate = new Date(dateField);
            const dateLabel = window.ThreadManagerUI.getDateLabel(threadDate);

            if (currentDateGroup !== dateLabel) {
                groupedThreads.push({ type: 'separator', label: dateLabel });
                currentDateGroup = dateLabel;
            }
            groupedThreads.push({ type: 'thread', data: thread });
        });

        // Render
        listContainer.innerHTML = groupedThreads.map(item => {
            if (item.type === 'separator') {
                return `<div class="thread-date-separator"><span>${item.label}</span></div>`;
            }

            const thread = item.data;
            // ✅ FIX: Use window.ThreadManagerUI explicitly
            return window.ThreadManagerUI.renderThreadCard(thread, threadToLocation[thread.id] || 'prime');
        }).join('');
    },

    /**
     * Render individual thread card with expandable hover content
     * Uses ThreadCardTemplates if available, fallback to inline template
     */
    renderThreadCard(thread, currentLocation) {
        const date = new Date(thread.updated);
        const meta = {
            msgCount: thread.message_count || 0,
            dateStr: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
            timeStr: date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
        };

        let agentLabel = 'Prime';
        let agentIcon = 'fa-star';
        let agentClass = 'main';

        if (currentLocation && currentLocation !== 'prime') {
            const match = currentLocation.match(/agent-(\d+)/);
            if (match) {
                const agentId = parseInt(match[1]);
                agentLabel = (typeof MultiAgent !== 'undefined' && MultiAgent.getAgentName) ?
                    MultiAgent.getAgentName(agentId) : `Agent-${agentId}`;
                agentIcon = (typeof MultiAgent !== 'undefined' && MultiAgent.getAgentIcon) ?
                    MultiAgent.getAgentIcon(agentId) : 'fa-atom';
                agentClass = 'agent';
            }
        }

        const agent = { name: agentLabel, icon: agentIcon, class: agentClass };
        const threadTitle = thread.title || 'Untitled';
        const threadSlug = thread.thread_slug || thread.id;
        const slug = threadSlug.substring(0, 8);

        // Use ThreadCardTemplates if available
        if (typeof window.ThreadCardTemplates !== 'undefined') {
            return window.ThreadCardTemplates.compactCard(thread, 'thread-history', agent, meta, slug, null, currentLocation);
        }

        // Fallback: inline expandable template
        const truncatedTitle = threadTitle.length > 35 ? threadTitle.substring(0, 32) + '...' : threadTitle;

        return `
            <div class="thread-item agent-thread-card ${thread.id === window.ThreadManager.currentThreadId ? 'active' : ''}"
                draggable="true"
                data-thread-id="${thread.id}"
                data-current-location="${currentLocation}"
                ondragstart="ThreadManager.handleDragStart(event)"
                ondragend="ThreadManager.handleDragEnd(event)"
                ondblclick="ThreadManager.handleThreadDoubleClick('${thread.id}', '${currentLocation}')">
                
                <!-- ALWAYS VISIBLE: Title + Agent Badge + Actions -->
                <div class="thread-item-header">
                    <span class="thread-item-title" title="${threadTitle}">${truncatedTitle}</span>
                </div>
                <div class="thread-item-header" style="margin-top: 8px;">
                    <div class="thread-item-agent-badge ${agentClass}">
                        <i class="fas ${agentIcon}"></i> ${agentLabel}
                    </div>
                    <div class="thread-item-actions">
                        ${currentLocation && currentLocation.startsWith('agent-') ? `
                        <button class="thread-action-btn unload" 
                            onclick="event.stopPropagation(); ThreadManager.unloadThread('${thread.id}')" 
                            title="Unload from agent">
                            <i class="fas fa-sign-out-alt"></i>
                        </button>
                        ` : ''}
                        ${thread.location === 'prime' || thread.location === 'prime-loaded' ? `
                        <button class="thread-action-btn ${thread.location === 'prime-loaded' ? 'active' : ''}" 
                            onclick="event.stopPropagation(); ThreadManager.markAsPrimeLoaded('${thread.id}')" 
                            title="${thread.location === 'prime-loaded' ? 'Loads on startup (active)' : 'Set to load on startup'}">
                            <i class="fas fa-home"></i>
                        </button>
                        ` : ''}
                        <button class="thread-action-btn edit" 
                            onclick="event.stopPropagation(); ThreadManager.editThread('${thread.id}')" 
                            title="Edit thread">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="thread-action-btn delete" 
                            onclick="event.stopPropagation(); ThreadManager.deleteThread('${thread.id}')" 
                            title="Delete thread">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                
                <!-- ALWAYS VISIBLE: Meta Row -->
                <div class="thread-meta-row-always-visible" style="display: flex; align-items: center; gap: 12px; margin-top: 8px;">
                    <span class="thread-meta-item" title="Message count">
                        <i class="fas fa-comments"></i> ${meta.msgCount} msgs
                    </span>
                    <span class="thread-meta-item" title="Last updated">
                        <i class="fas fa-calendar"></i> ${meta.dateStr}
                    </span>
                    <span class="thread-meta-item" title="Time">
                        <i class="fas fa-clock"></i> ${meta.timeStr}
                    </span>
                </div>
                
                <!-- HOVER EXPAND: Additional Info -->
                <div class="thread-expand-on-hover">
                    
                    <!-- Copy + Thread ID -->
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 8px;">
                        <button class="thread-copy-btn" onclick="event.stopPropagation(); ThreadManager.copyThreadId('${thread.id}')" title="Copy thread ID">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                        <span class="thread-id-badge" title="${threadSlug}">${slug}...</span>
                    </div>
                    
                    <!-- Synergy / Workflow Pills -->
                    ${thread.synergy_card_id || thread.workflow_slug ? `
                    <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;">
                        ${thread.synergy_card_id ? `
                        <span class="thread-pill thread-pill-synergy">
                            <i class="fas fa-users"></i> ${thread.synergy_card_title || thread.synergy_card_id}
                        </span>
                        ` : ''}
                        ${thread.workflow_slug ? `
                        <span class="thread-pill thread-pill-workflow">
                            <i class="fas fa-robot"></i> ${thread.workflow_title || thread.workflow_slug}
                        </span>
                        ` : ''}
                    </div>
                    ` : ''}
                    
                    <!-- Tags -->
                    ${thread.tags && thread.tags.length > 0 ? `
                    <div class="thread-tags-row" style="margin-top: 8px;">
                        ${thread.tags.map(tag => `
                            <span class="thread-tag-pill">
                                <i class="fas fa-tag"></i> ${tag}
                            </span>
                        `).join('')}
                    </div>
                    ` : ''}
                    
                </div>
            </div>
        `;
    },

    /**
     * Get date label for grouping
     */
    getDateLabel(date) {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        const threadDay = new Date(date.getFullYear(), date.getMonth(), date.getDate());

        if (threadDay.getTime() === today.getTime()) {
            return 'Today';
        } else if (threadDay.getTime() === yesterday.getTime()) {
            return 'Yesterday';
        } else if (threadDay > new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)) {
            return 'This Week';
        } else {
            return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        }
    },

    /**
     * Render thread info container (for Prime/Agent headers)
     */
    renderThreadInfoContainer(location, threadId, compact = false) {
        const threads = window.ThreadManager.threads || [];
        const thread = threads.find(t => t.id === threadId);

        if (!thread) {
            return this.renderEmptyThreadInfo(location);
        }

        // Use ThreadCardTemplates for consistent 7-row structure
        if (typeof ThreadCardTemplates === 'undefined') {
            console.error('[renderThreadInfoContainer] ThreadCardTemplates not loaded!');
            return this.renderEmptyThreadInfo(location);
        }

        const updatedDate = new Date(thread.updated || thread.created);
        const meta = {
            msgCount: thread.message_count || 0,
            dateStr: updatedDate.toLocaleDateString('en-US', {
                month: 'short', day: 'numeric', year: 'numeric'
            }),
            timeStr: updatedDate.toLocaleTimeString('en-US', {
                hour: 'numeric', minute: '2-digit'
            })
        };

        // Agent metadata (varies by location)
        let agent = {
            name: 'Prime',
            icon: 'fa-star',
            class: 'main'
        };

        if (location && location.startsWith('agent-')) {
            const agentIdMatch = location.match(/agent-(\d+)/);
            if (agentIdMatch && typeof MultiAgent !== 'undefined') {
                const agentId = parseInt(agentIdMatch[1]);
                agent = {
                    name: MultiAgent.getAgentName(agentId),
                    icon: MultiAgent.getAgentIcon(agentId),
                    class: 'agent'
                };
            }
        } else if (location === 'synergy') {
            agent = {
                name: 'Synergy',
                icon: 'fa-users',
                class: 'synergy'
            };
        }

        // Thread slug (shortened for display)
        const slug = threadId.substring(0, 8);

        // Current location (for thread-history cards)
        const currentLocation = thread.location || 'prime';

        // Use ThreadCardTemplates.compactCard() for all locations
        return ThreadCardTemplates.compactCard(
            thread,
            location,
            agent,
            meta,
            slug,
            null,  // synergyMeta (fetched separately if needed)
            currentLocation
        );
    },

    /**
     * Render empty thread info (no thread loaded)
     * Uses ThreadCardTemplates for consistency across all locations
     */
    renderEmptyThreadInfo(location) {
        // Use ThreadCardTemplates for consistency
        if (typeof ThreadCardTemplates !== 'undefined') {
            let agentName = 'Prime';
            let agentIcon = 'fa-star';
            let agentId = null;

            if (location === 'synergy') {
                agentName = 'Synergy';
                agentIcon = 'fa-users';
            } else if (location !== 'prime') {
                const match = location.match(/agent-(\d+)/);
                if (match && typeof MultiAgent !== 'undefined') {
                    agentId = parseInt(match[1]);
                    agentName = MultiAgent.getAgentName(agentId);
                    agentIcon = MultiAgent.getAgentIcon(agentId);
                }
            }

            return ThreadCardTemplates.noThreadMessage(agentName, agentIcon, agentId);
        }

        // Fallback (if ThreadCardTemplates not loaded)
        return `
            <div class="no-thread-message" style="padding: 20px; text-align: center; color: #666;">
                <i class="fas fa-inbox" style="font-size: 48px; margin-bottom: 12px; opacity: 0.5;"></i>
                <div style="font-size: 16px; font-weight: 500;">No thread loaded</div>
            </div>
        `;
    },

    /**
     * Update Prime header with thread info card or welcome message
     */
    updatePrimeHeader(threadId) {
        const container = document.getElementById('prime-thread-info');
        if (!container) {
            console.warn('[updatePrimeHeader] Container #prime-thread-info not found');
            return;
        }

        if (!threadId) {
            // Show clickable thread selector dropdown (no welcome screen)
            container.innerHTML = this.renderEmptyThreadInfo('prime');
            return;
        }

        // Render thread info card using ThreadCardTemplates
        const html = this.renderThreadInfoContainer('prime', threadId, false);
        if (html) {
            container.innerHTML = html;
            console.log(`[updatePrimeHeader] Rendered thread card for Prime: ${threadId}`);
        } else {
            console.warn(`[updatePrimeHeader] Empty HTML for thread ${threadId}`);
        }
    },


    /**
     * Refresh all thread-info cards for a specific thread across the entire UI
     * Also updates UI pills (Synergy, Workflow, etc.)
     */
    refreshAllThreadInfoCards(threadId) {
        console.log(`🔄 [refreshAllThreadInfoCards] Refreshing all cards for thread ${threadId}`);

        // Find all thread-info cards with this thread ID
        const threadCards = document.querySelectorAll(`[data-thread-id="${threadId}"]`);

        threadCards.forEach(card => {
            // Get the location from the card's context
            const location = card.getAttribute('data-location') || 'prime';

            // Re-render the card with updated agent info AND UI pills
            const newCardHTML = this.renderThreadInfoContainer(location, threadId, card.classList.contains('compact'));

            // Replace the card's innerHTML
            card.outerHTML = newCardHTML;

            console.log(`✅ [refreshAllThreadInfoCards] Updated thread-info card at ${location}`);
        });

        // Also update sidebar thread items (shows UI pills)
        const threads = window.ThreadManager.threads || [];
        const thread = threads.find(t => t.id === threadId);
        if (thread) {
            const sidebarItem = document.querySelector(`[data-thread-id="${threadId}"].thread-item`);
            if (sidebarItem) {
                // Re-render just the pills section
                this.updateThreadPills(sidebarItem, thread);
            }
        }

        // REALTIME: No need to refresh Synergy board - Supabase realtime handles it
        // Synergy board subscribes to postgres_changes on synergy_sessions table
        // Removed synergyBoard.loadSessions() to prevent unnecessary API calls
    },



    /**
     * Update UI pills on a thread item (Synergy=green, Workflow=orange, etc.)
     */
    updateThreadPills(threadElement, thread) {
        // Find or create pills container
        let pillsContainer = threadElement.querySelector('.thread-ui-pills');
        if (!pillsContainer) {
            pillsContainer = document.createElement('div');
            pillsContainer.className = 'thread-ui-pills';
            pillsContainer.style.cssText = 'display: flex; gap: 6px; margin-top: 6px; flex-wrap: wrap;';
            threadElement.appendChild(pillsContainer);
        }

        // Clear existing pills
        pillsContainer.innerHTML = '';

        // Add Synergy pill (green)
        if (thread.synergy_card_id) {
            const synergyPill = document.createElement('span');
            synergyPill.className = 'thread-pill thread-pill-synergy';
            synergyPill.style.cssText = 'background: #10b981; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; display: flex; align-items: center; gap: 4px;';
            synergyPill.innerHTML = `<i class="fas fa-link" style="font-size: 10px;"></i> Synergy`;
            synergyPill.title = thread.synergy_card_name || thread.synergy_card_id;
            pillsContainer.appendChild(synergyPill);
        }

        // Add Workflow pill (orange)
        if (thread.workflow_id) {
            const workflowPill = document.createElement('span');
            workflowPill.className = 'thread-pill thread-pill-workflow';
            workflowPill.style.cssText = 'background: #f97316; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; display: flex; align-items: center; gap: 4px;';
            workflowPill.innerHTML = `<i class="fas fa-robot" style="font-size: 10px;"></i> Workflow`;
            workflowPill.title = thread.workflow_name || thread.workflow_id;
            pillsContainer.appendChild(workflowPill);
        }

        // Add Custom pills (extensible for future link types)
        if (thread.custom_links && Array.isArray(thread.custom_links)) {
            thread.custom_links.forEach(link => {
                const customPill = document.createElement('span');
                customPill.className = `thread-pill thread-pill-${link.type}`;
                customPill.style.cssText = `background: ${link.color || '#6366f1'}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; display: flex; align-items: center; gap: 4px;`;
                customPill.innerHTML = `<i class="fas ${link.icon || 'fa-link'}" style="font-size: 10px;"></i> ${link.label}`;
                customPill.title = link.description || link.id;
                pillsContainer.appendChild(customPill);
            });
        }
    },

    /**
     * Show "Start New Chat" button
     */
    showStartNewChatButton(containerId, location = 'prime') {
        const container = document.getElementById(containerId);
        if (!container) return;

        const greeting = (typeof window.ThreadManagerWelcome !== 'undefined' && typeof window.ThreadManagerWelcome.getTimeBasedGreeting === 'function') ?
            window.ThreadManagerWelcome.getTimeBasedGreeting() :
            { title: 'Welcome!', subtitle: 'Start a new conversation', icon: 'fa-star', color: '#8b5cf6' };

        const emptyStateHtml = `
            <div class="welcome-container" id="${location}-welcome-container">
                <div class="welcome-content">
                    <div class="welcome-icon">
                        <i class="fas ${greeting.icon}" style="color: ${greeting.color};"></i>
                    </div>
                    <h3 class="welcome-title" id="${location}-welcome-title">${greeting.title}</h3>
                    <p class="welcome-subtitle" id="${location}-welcome-subtitle">${greeting.subtitle}</p>
                    
                    <div class="welcome-actions">
                        <button class="welcome-btn welcome-btn-primary" onclick="ThreadManager.showNewChatModal('${location}')">
                            <i class="fas fa-plus"></i> Start New Chat
                        </button>
                        <button class="welcome-btn welcome-btn-secondary" onclick="ThreadManager.toggleThreadMenu()">
                            <i class="fas fa-history"></i> Thread History
                        </button>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = emptyStateHtml;

        // Hide input wrapper
        if (location === 'prime') {
            const primeInputWrapper = document.querySelector('.ai-chat-input-wrapper');
            if (primeInputWrapper) {
                primeInputWrapper.style.display = 'none';
            }
        } else if (location.startsWith('agent-')) {
            const agentId = location.replace('agent-', '');
            const agentInputArea = document.querySelector(`#agent-${agentId} .agent-input-area`);
            if (agentInputArea) {
                agentInputArea.style.display = 'none';
            }
        }
    }
};

console.log('✅ ThreadManager-UI module loaded');
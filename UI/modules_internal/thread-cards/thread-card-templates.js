/**
 * FILE: AI_infrastructure/threads/frontend/thread_card_templates.js
 * PURPOSE: HTML template generation for thread info cards (extracted from business-ai-platform-v2.html)
 * 
 * DEPENDENCIES:
 * - None (pure template functions)
 * - Uses ES6 template literals
 * 
 * EXPORTS:
 * - ThreadCardTemplates.welcomeContainer(toolCount) - Prime welcome screen (no thread loaded)
 * - ThreadCardTemplates.noThreadMessage(agentName, agentIcon, agentId) - No-thread message (clickable selector for agents)
 * - ThreadCardTemplates.compactCard(thread, location, agent, meta, slug) - Compact card (agents, synergy, sidebar)
 * - ThreadCardTemplates.fullCard(thread, location, agent, meta, slug) - Full card (Prime panel)
 * - ThreadCardTemplates.headerRow(thread, location, agent, compact) - Row 1: Title, agent badge, actions
 * - ThreadCardTemplates.metaRow(thread, meta) - Row 2: Message count, date, time
 * - ThreadCardTemplates.copyThreadRow(thread, slug) - Row 3: Copy dropdown + thread ID badge
 * - ThreadCardTemplates.uiLinksRow(thread, location, synergyMeta) - Row 4: Synergy/Workflow pills
 * - ThreadCardTemplates.tagsRow(thread, location) - Row 5: Tags + token count + add tag button
 * - ThreadCardTemplates.lockControlsRow(thread) - Row 6: Device lock controls (full mode only)
 * 
 * USED BY:
 * - business-ai-platform-v2.html (ThreadManager.renderThreadInfoContainer)
 * 
 * RELATED FILES:
 * - AI_infrastructure/threads/styles/thread_card_styles.css (styling)
 * - AI_infrastructure/threads/frontend/thread_card_actions.js (event handlers)
 * - AI_infrastructure/threads/frontend/thread_card.js (core module with Realtime)
 * 
 * NOTES:
 * - All HTML uses ES6 template literals for readability
 * - Uses safeEscape() for user-generated content (defined in parent scope)
 * - Maintains exact same HTML structure as original (no breaking changes)
 * - Supports both compact (agents, synergy, sidebar) and full (Prime) modes
 * - Synergy metadata includes priority, description, users, last active
 * - Workflow metadata includes workflow_name, workflow_id
 * - Device lock controls show lock/unlock buttons based on state
 * 
 * LAST MODIFIED: 2025-01-XX - Extracted from business-ai-platform-v2.html (Phase 2)
 */

// Global namespace for thread card templates
window.ThreadCardTemplates = {

    /**
     * Welcome Container - Prime panel (no thread loaded)
     * Shows interactive visualizations, tool count, quick start buttons
     * 
     * COMMENTED OUT - Nov 22, 2025: Prime now uses thread selector (noThreadMessage) instead
     * The "Welcome to Prime" message was incorrect - should show "Click to select a thread"
     * 
     * @param {number} toolCount - Number of available tools (default: 594)
     * @returns {string} HTML string for welcome container
     */
    /* DISABLED - Use noThreadMessage() for Prime instead
    welcomeContainer(toolCount = 594) {
        return `
            <div class="ai-chat-header-info" id="prime-thread-info" style="padding: 20px; text-align: center;">
                <div style="font-size: 24px; font-weight: 600; color: #1a1a2e; margin-bottom: 12px;">
                    Welcome to Prime
                </div>
                <div style="font-size: 14px; color: #666; margin-bottom: 20px;">
                    Your AI assistant with ${toolCount} tools and interactive visualizations
                </div>
                <div style="display: flex; gap: 12px; justify-content: center;">
                    <button onclick="ThreadManager.createNewThread('prime')" 
                            style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-plus"></i> Start New Chat
                    </button>
                    <button onclick="ThreadManager.showThreadHistory('prime')" 
                            style="background: white; color: #667eea; border: 2px solid #667eea; padding: 12px 24px; border-radius: 8px; font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-history"></i> Thread History
                    </button>
                </div>
            </div>
        `;
    },
    */

    /**
     * No Thread Message - Agents/Synergy panels (no thread assigned)
     * Simple message showing agent icon and name
     * 
     * @param {string} agentName - Agent display name (e.g., "Agent-1", "Synergy")
     * @param {string} agentIcon - FontAwesome icon class (e.g., "fa-robot", "fa-users")
     * @returns {string} HTML string for no-thread message
     */
    noThreadMessage(agentName, agentIcon, agentId = null) {
        // For agent columns: clickable selector dropdown with proper agentId
        if (agentId !== null && agentId !== undefined) {
            return `
                <div class="thread-info-wrapper">
                    <div class="no-thread-message clickable" onclick="AgentColumn.showThreadSelector(${agentId})">
                        <i class="fas fa-inbox"></i> 
                        <span>Click to select a thread</span>
                        <i class="fas fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
                    </div>
                    <div class="thread-selector-dropdown" id="thread-selector-${agentId}" style="display: none;"></div>
                </div>
            `;
        } else if (agentName === 'Prime') {
            // For Prime: clickable selector dropdown (same as agents but with 'prime' identifier)
            // CRITICAL: No inline onclick - event delegation with stopPropagation handles clicks
            return `
                <div class="thread-info-wrapper">
                    <div class="no-thread-message clickable" id="prime-no-thread" style="cursor: pointer !important;">
                        <i class="fas fa-inbox"></i>
                        <span>Click to select a thread</span>
                        <i class="fas fa-chevron-down" style="margin-left: auto; font-size: 10px;"></i>
                    </div>
                    <div class="thread-selector-dropdown" id="thread-selector-prime" style="display: none;"></div>
                </div>
            `;
        } else {
            // For Synergy: static empty state message (Synergy doesn't load individual threads)
            return `
                <div class="ai-chat-header-info" style="padding: 20px; text-align: center; color: #666;">
                    <i class="fas ${agentIcon}" style="font-size: 48px; margin-bottom: 12px; opacity: 0.5;"></i>
                    <div style="font-size: 16px; font-weight: 500;">
                        No thread loaded in ${agentName}
                    </div>
                </div>
            `;
        }
    },

    /**
     * Compact Card - Used for ALL locations (Prime, Agents, Thread History)
     * Updated Nov 18, 2025 - Now unified across all thread card locations
     * 
     * ALWAYS VISIBLE: 
     *   Row 1: Title + Agent Badge + Header Actions (varies by location)
     *          - Prime: Clean header (no buttons)
     *          - Agents: Unload button [X]
     *          - Thread History: Full action button set
     *   Row 2: Meta (msgs/date/time)
     * 
     * HOVER EXPAND (smooth transition):
     *   Row 3: Copy Thread + Thread Slug
     *   Row 4: Synergy Session (green pill)
     *   Row 5: Workflow Automation (orange pill)
     *   Row 6: Tags
     *   Row 7: Lock/Unlock + Device
     * 
     * @param {Object} thread - Thread object from database
     * @param {string} location - Location identifier (e.g., "prime", "agent-1", "thread-history")
     * @param {Object} agent - Agent metadata {name, icon, class}
     * @param {Object} meta - Display metadata {msgCount, dateStr, timeStr}
     * @param {string} slug - Shortened thread slug for display
     * @param {Object} synergyMeta - Synergy session metadata (optional)
     * @param {string} currentLocation - Current thread location (for thread-history)
     * @returns {string} HTML string for compact thread card with hover expand
     */
    compactCard(thread, location, agent, meta, slug, synergyMeta = null, currentLocation = null) {
        const synergyDisplay = thread.synergy_card_title || thread.synergy_card_id || 'Synergy Session';
        const synergyPriority = synergyMeta?.priority || '';

        // Use different header based on location
        const isThreadHistory = location === 'thread-history';
        const isPrime = location === 'prime';
        const isAgent = location && location.startsWith('agent-');

        let headerHtml;
        if (isThreadHistory) {
            headerHtml = this.headerRowWithActions(thread, location, agent, currentLocation);
        } else if (isPrime) {
            headerHtml = this.headerRowClean(thread, location, agent);
        } else {
            headerHtml = this.headerRowWithUnload(thread, location, agent);
        }

        // CRITICAL FIX (Dec 9, 2025): Do NOT add ID to cards - causes duplicate IDs
        // Prime has outer <div id="prime-thread-info"> container - card inside should not have ID
        // Thread History cards are multiple items in a list - cannot share same ID
        // Agent columns work correctly without ID (container has id="thread-info-1" etc.)
        // All cards use data-thread-id for identification - findCardElement() searches by this

        // Set appropriate tooltip based on location
        // Thread History: Double-click loads into Prime
        // Prime/Agents: Double-click expands card (no reload action)
        const doubleClickTooltip = isThreadHistory
            ? 'Double-click to load into AI Prime'
            : 'Double-click to expand/collapse card';

        return `
            <div class="ai-chat-header-info agent-thread-card" 
                 data-thread-id="${thread.id}" 
                 data-location="${location}"
                 draggable="true"
                 ondragstart="ThreadManager.handleDragStart(event)"
                 ondragend="ThreadManager.handleDragEnd(event)"
                 ondblclick="ThreadManager.handleThreadDoubleClick('${thread.id}', '${location}')"
                 style="cursor: pointer;" 
                 title="${doubleClickTooltip}">
                
                <!-- Row 1: Title + Agent Badge + Chevron -->
                <div class="thread-item-header" style="display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 0;">
                    <span class="thread-item-title" style="flex: 1; font-size: 18px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${thread.title || 'Untitled'}
                    </span>
                    <div class="thread-item-agent-badge ${agent.class}" style="flex-shrink: 0; font-size: 13px;">
                        <i class="fas ${agent.icon}"></i> ${agent.name}
                    </div>
                    <button class="thread-card-expand-btn" 
                            onclick="ThreadCardExpansion.toggleCard(event, '${thread.id}'); return false;"
                            aria-label="Expand details"
                            title="Click to expand/collapse details"
                            style="flex-shrink: 0;">
                        <i class="fas fa-chevron-down chevron-icon"></i>
                    </button>
                </div>
                
                <!-- Row 2: Meta (msgs/date/time) + Action Buttons -->
                <div class="thread-meta-row-always-visible" style="display: flex; align-items: center; gap: 12px;">
                    <span class="thread-meta-item" title="Message count">
                        <i class="fas fa-comments"></i> ${meta.msgCount} msgs
                    </span>
                    <span class="thread-meta-item" title="Last updated">
                        <i class="fas fa-calendar"></i> ${meta.dateStr}
                    </span>
                    <span class="thread-meta-item" title="Time">
                        <i class="fas fa-clock"></i> ${meta.timeStr}
                    </span>
                    ${headerHtml}
                </div>
                
                <!-- HOVER EXPAND: Rows 3-7 -->
                <div class="thread-expand-on-hover">
                    
                    <!-- Row 3: Copy + Thread ID -->
                    <div style="display: flex; align-items: center; gap: 8px;">
                        ${this._copyThreadDropdown(thread)}
                        ${this._threadIdBadge(thread, slug)}
                    </div>
                    
                    <!-- Row 4-5: Synergy + Workflow UI Links -->
                    ${this.uiLinksRow(thread, location, synergyMeta)}
                    
                    <!-- Row 6: Tags -->
                    ${this.tagsRow(thread, location)}
                    
                    <!-- Row 7: Lock Controls -->
                    ${this.lockControlsRow(thread)}
                    
                </div>
                
            </div>
        `;
    },

    /**
     * Full Card - DEPRECATED (Nov 18, 2025)
     * Prime now uses compactCard() with headerRowClean() for consistency
     * Kept for backwards compatibility only
     * 
     * @deprecated Use compactCard() instead
     * @param {Object} thread - Thread object from database
     * @param {string} location - Location identifier (should be "prime")
     * @param {Object} agent - Agent metadata {name, icon, class}
     * @param {Object} meta - Display metadata {msgCount, dateStr, timeStr}
     * @param {string} slug - Shortened thread slug for display
     * @param {Object} synergyMeta - Synergy session metadata (optional)
     * @returns {string} HTML string for full thread card
     */
    fullCard(thread, location, agent, meta, slug, synergyMeta = null) {
        const synergyDisplay = thread.synergy_card_title || thread.synergy_card_id || 'Synergy Session';
        const synergyPriority = synergyMeta?.priority || '';

        return `
            <div class="ai-chat-header-info" 
                 id="${location}-thread-info" 
                 data-thread-id="${thread.id}" 
                 data-location="${location}"
                 draggable="true"
                 ondragstart="ThreadManager.handleDragStart(event)"
                 ondragend="ThreadManager.handleDragEnd(event)"
                 ondblclick="ThreadManager.handleThreadDoubleClick('${thread.id}', '${location}')"
                 style="cursor: pointer;" 
                 title="Double-click to load in Prime">
                
                <!-- Row 1: Title + Agent Badge + Chevron -->
                <div class="thread-item-header" style="display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 0;">
                    <span class="thread-item-title" style="flex: 1; font-size: 18px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${thread.title || 'Untitled'}
                    </span>
                    <div class="thread-item-agent-badge ${agent.class}" style="flex-shrink: 0; font-size: 13px;">
                        <i class="fas ${agent.icon}"></i> ${agent.name}
                    </div>
                    <button class="thread-card-expand-btn" 
                            onclick="ThreadCardExpansion.toggleCard(event, '${thread.id}'); return false;"
                            aria-label="Expand details"
                            title="Click to expand/collapse details"
                            style="flex-shrink: 0;">
                        <i class="fas fa-chevron-down chevron-icon"></i>
                    </button>
                </div>
                
                <!-- Row 2: Meta (msgs/date/time) - ALWAYS VISIBLE -->
                <div style="display: flex; align-items: center; gap: 12px; margin-top: 8px;">
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
                
                <!-- EXPAND ON CLICK: Rows 3-7 -->
                <div class="thread-expand-on-hover">
                    
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 8px;">
                        ${this._copyThreadDropdown(thread)}
                        ${this._threadIdBadge(thread, slug)}
                    </div>
                    
                    ${this._synergyRow(thread, synergyMeta)}
                    
                    ${this.tagsRow(thread, location, true)}
                    
                    ${this.lockControlsRow(thread)}
                    
                </div>
                
            </div>
        `;
    },

    /**
     * Header Row Clean - Title + Agent Badge ONLY (for Prime)
     * NO action buttons, NO unload button - clean design for Prime panel
     * 
     * @param {Object} thread - Thread object
     * @param {string} location - Location identifier
     * @param {Object} agent - Agent metadata {name, icon, class}
     * @returns {string} HTML string for clean header row
     */
    headerRowClean(thread, location, agent) {
        // Agent badge now in Row 1 with title - this returns empty for Prime (clean header)
        return '';
    },

    /**
     * Header Row With Unload - Title + Agent Badge + Unload Button (for Agent columns)
     * Includes [X] unload button to send thread back to Prime
     * 
     * @param {Object} thread - Thread object
     * @param {string} location - Location identifier (e.g., "agent-1")
     * @param {Object} agent - Agent metadata {name, icon, class}
     * @returns {string} HTML string for header row with unload button
     */
    headerRowWithUnload(thread, location, agent) {
        // Agent badge now in Row 1 with title - this only shows unload button
        return `
            <button class="agent-unload-btn" 
                    onclick="event.stopPropagation(); ThreadManager.unloadThread('${thread.id}')" 
                    title="Unload thread from agent (move to Prime)"
                    style="flex-shrink: 0; margin-left: auto;">
                <i class="fas fa-sign-out-alt"></i>
            </button>
        `;
    },

    /**
     * Header Row With Actions - Agent Badge + All Action Buttons (for Thread History)
     * Includes all action buttons: unload (if in agent), rename, edit, fork, clone, archive, delete
     * 
     * @param {Object} thread - Thread object
     * @param {string} location - Location identifier (e.g., "thread-history")
     * @param {Object} agent - Agent metadata {name, icon, class}
     * @param {string} currentLocation - Where thread is currently assigned (prime, agent-1, etc.)
     * @returns {string} HTML string for header row with action buttons
     */
    headerRowWithActions(thread, location, agent, currentLocation) {
        const isInAgent = currentLocation && currentLocation.startsWith('agent-');

        // Agent badge now in Row 1 with title - this only shows action buttons
        return `
            <div class="thread-item-actions" style="display: flex; gap: 4px; flex-shrink: 0; margin-left: auto;">
                ${isInAgent ? `
                <button class="thread-action-btn unload"
                    onclick="event.stopPropagation(); ThreadManager.unloadThread('${thread.id}')"
                    title="Unload thread from agent (move to Prime)">
                    <i class="fas fa-sign-out-alt"></i>
                </button>
                ` : ''}
                <button class="thread-action-btn rename"
                    onclick="event.stopPropagation(); ThreadManager.startRename('${thread.id}')"
                    title="Rename thread">
                    <i class="fas fa-pen"></i>
                </button>
                <button class="thread-action-btn edit"
                    onclick="event.stopPropagation(); ThreadManager.editThread('${thread.id}')"
                    title="Edit thread">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="thread-action-btn fork"
                    onclick="event.stopPropagation(); ThreadManager.forkThread('${thread.id}')"
                    title="Fork thread (branch from current point)">
                    <i class="fas fa-code-branch"></i>
                </button>
                <button class="thread-action-btn clone"
                    onclick="event.stopPropagation(); ThreadManager.cloneThread('${thread.id}')"
                    title="Clone thread (duplicate all messages)">
                    <i class="fas fa-clone"></i>
                </button>
                <button class="thread-action-btn archive"
                    onclick="event.stopPropagation(); ThreadManager.archiveThread('${thread.id}')"
                    title="Archive thread">
                    <i class="fas fa-archive"></i>
                </button>
                <button class="thread-action-btn delete"
                    onclick="event.stopPropagation(); ThreadManager.deleteThread('${thread.id}')"
                    title="Delete thread">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
    },

    /**
     * Header Row (Row 1) - Title | Agent Badge | Action Buttons/Unload
     * LEGACY - Keep for backward compatibility with sidebar thread list items
     * Compact mode: Title, agent badge, action buttons (rename, edit, fork, clone, archive, delete)
     * Full mode: Title, agent badge, unload button (agent panels only)
     * 
     * @param {Object} thread - Thread object
     * @param {string} location - Location identifier
     * @param {Object} agent - Agent metadata {name, icon, class}
     * @param {boolean} compact - Compact mode flag
     * @returns {string} HTML string for header row
     */
    headerRow(thread, location, agent, compact) {
        const actionButtons = compact && location !== 'synergy' ? `
            <button class="thread-action-btn rename"
                onclick="event.stopPropagation(); ThreadManager.renameThread('${thread.id}')"
                title="Rename thread">
                <i class="fas fa-pencil-alt"></i>
            </button>
            <button class="thread-action-btn edit"
                onclick="event.stopPropagation(); ThreadManager.editThread('${thread.id}')"
                title="Edit thread">
                <i class="fas fa-edit"></i>
            </button>
            <button class="thread-action-btn fork"
                onclick="event.stopPropagation(); ThreadManager.forkThread('${thread.id}')"
                title="Fork thread (branch from current point)">
                <i class="fas fa-code-branch"></i>
            </button>
            <button class="thread-action-btn clone"
                onclick="event.stopPropagation(); ThreadManager.cloneThread('${thread.id}')"
                title="Clone thread (duplicate all messages)">
                <i class="fas fa-clone"></i>
            </button>
            <button class="thread-action-btn archive"
                onclick="event.stopPropagation(); ThreadManager.archiveThread('${thread.id}')"
                title="Archive thread">
                <i class="fas fa-archive"></i>
            </button>
            <button class="thread-action-btn delete"
                onclick="event.stopPropagation(); ThreadManager.deleteThread('${thread.id}')"
                title="Delete thread">
                <i class="fas fa-trash"></i>
            </button>
        ` : '';

        const unloadButton = !compact && location !== 'synergy' && location !== 'prime' && location.startsWith('agent-') ? `
            <button class="agent-unload-btn"
                onclick="event.stopPropagation(); ThreadManager.unloadThread('${thread.id}')"
                title="Unload thread from agent (move to Prime)">
                <i class="fas fa-sign-out-alt"></i>
            </button>
        ` : '';

        return `
            <div class="thread-item-header">
                <span class="thread-item-title" id="${location}-thread-title" title="${thread.title || 'Untitled'}" style="flex: 1; font-size: ${compact ? '14px' : '16px'}; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${thread.title || 'Untitled'}
                </span>
                <div style="display: flex; align-items: center; gap: ${compact ? '6px' : '8px'}; flex-shrink: 0;">
                    <div class="thread-item-agent-badge ${agent.class}">
                        <i class="fas ${agent.icon}"></i> ${agent.name}
                    </div>
                    ${actionButtons}
                    ${unloadButton}
                </div>
            </div>
        `;
    },

    /**
     * Meta Row (Row 2) - Message count, date, time
     * 
     * @param {Object} thread - Thread object
     * @param {Object} meta - Display metadata {msgCount, dateStr, timeStr}
     * @returns {string} HTML string for meta row
     */
    metaRow(thread, meta) {
        return `
            <div class="thread-item-meta" style="display: flex; align-items: center; gap: 12px; flex: 1;">
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
        `;
    },

    /**
     * Copy Thread Row (Row 3) - Copy dropdown + Thread ID badge
     * 
     * @param {Object} thread - Thread object
     * @param {string} slug - Shortened thread slug
     * @returns {string} HTML string for copy row
     */
    copyThreadRow(thread, slug) {
        return `
            <div class="thread-item-meta" style="display: flex; align-items: center; justify-content: space-between; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
                    <span class="thread-meta-item" title="Message count">
                        <i class="fas fa-comments"></i> ${thread.message_count || 0} msgs
                    </span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    ${this._copyThreadDropdown(thread)}
                    ${this._threadIdBadge(thread, slug)}
                </div>
            </div>
        `;
    },

    /**
     * UI Links Row (Row 4) - Synergy (green) and Workflow (orange) pills
     * NOW USES ThreadCardRegistry for dynamic badge rendering
     * 
     * @param {Object} thread - Thread object
     * @param {string} location - Location identifier
     * @param {Object} synergyMeta - Synergy session metadata (optional)
     * @returns {string} HTML string for UI links row
     */
    uiLinksRow(thread, location, synergyMeta = null) {
        // ✅ ALWAYS use fallback rendering (Dec 1, 2025 fix)
        // ThreadCardRegistry.renderPlaceholder() was generating malformed HTML
        // Fallback system has correct HTML structure, colors, icons, and functions

        // Check if ThreadCardRegistry has linked badges to inject
        if (window.ThreadCardRegistry && window.ThreadCardRegistry.initialized) {
            try {
                const registryHtml = window.ThreadCardRegistry.renderBadgesForThread(thread, location);

                // If registry returned empty (no linked badges), use full fallback
                if (!registryHtml || registryHtml.trim() === '') {
                    // Silent fallback - no log needed (happens for every unlinked thread)
                    return this._fallbackBadgeRendering(thread, location, synergyMeta);
                }

                // If registry returned content, it's ONLY linked badges (no placeholders)
                // We still need to merge with fallback to show placeholders for unlinked items
                // Silent merge - no log needed

                // ✅ TODO: Merge linked badges from registry with placeholders from fallback
                // For now, just use fallback (which includes both linked and unlinked)
                return this._fallbackBadgeRendering(thread, location, synergyMeta);

            } catch (error) {
                console.error('[ThreadCardTemplates] Error from ThreadCardRegistry:', error);
            }
        }

        // FALLBACK: Use hardcoded rendering (includes ALL badges + placeholders)
        // Silent fallback when registry not ready - no log spam
        return this._fallbackBadgeRendering(thread, location, synergyMeta);
    },

    /**
     * Fallback badge rendering (used during initialization)
     * Maintains backward compatibility while ThreadCardRegistry loads
     * 
     * UPDATED: Always shows all 4 placeholder pills (Synergy, Workflow, Automation, Internal Doc)
     * for Thread History and Agent columns, matching Prime panel behavior
     * 
     * @param {Object} thread - Thread object
     * @param {string} location - Location identifier
     * @param {Object} synergyMeta - Synergy session metadata (optional)
     * @returns {string} HTML string for UI links row
     */
    _fallbackBadgeRendering(thread, location, synergyMeta = null) {
        const synergyDisplay = thread.synergy_card_title || thread.synergy_card_id || 'Synergy Session';
        const synergyPriority = synergyMeta?.priority || '';

        const safeEscape = window.safeEscape || ((str) => String(str).replace(/[&<>"']/g, ''));

        // CRITICAL FIX: Ensure all 4 pills show for ALL locations (not just Prime)
        // Previously, only Prime showed all 4 pills, but Thread History/Agent columns need them too
        const showAllPills = true;  // Force all pills to appear

        return `
            <div class="thread-ui-links-row" style="display: flex; flex-direction: column; gap: 8px; margin-top: 8px;">
                
                <!-- Synergy Session (GREEN pill) -->
                ${thread.synergy_card_id ? `
                    <div class="thread-item-synergy thread-item-synergy-linked" data-synergy-id="${thread.synergy_card_id}">
                        <div style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 8px; padding: 8px; background: rgba(16, 185, 129, 0.05); border-left: 3px solid #10b981; border-radius: 4px;">
                            <div style="font-weight: 600; font-size: 13px; color: #10b981;">
                                <i class="fas fa-link" style="margin-right: 4px;"></i>
                                ${safeEscape(synergyDisplay)}
                            </div>
                            ${synergyMeta && synergyMeta.description ? `
                                <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.4; opacity: 0.9;">
                                    ${safeEscape(synergyMeta.description).substring(0, 120)}${synergyMeta.description.length > 120 ? '...' : ''}
                                </div>
                            ` : ''}
                        </div>
                        <button class="synergy-badge" style="background: #10b981; color: white; border: none; padding: 6px 12px; border-radius: 6px; display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer; flex: 1;"
                            onclick="event.stopPropagation(); ThreadManager.copySynergyInfo('${safeEscape(thread.synergy_card_id)}', '${safeEscape(synergyDisplay)}')"
                            data-tooltip-title="${safeEscape(synergyDisplay)}"
                            data-tooltip-desc="${synergyMeta ? safeEscape(synergyMeta.description || '') : ''}"
                            data-tooltip-users="${synergyMeta && Array.isArray(synergyMeta.assignees) ? safeEscape(synergyMeta.assignees.join(', ')) : ''}"
                            data-tooltip-updated="${synergyMeta && synergyMeta.last_active ? new Date(synergyMeta.last_active).toLocaleString() : ''}">
                            <i class="fas fa-link"></i>
                            <span class="synergy-badge-title">${synergyDisplay}</span>
                            ${synergyPriority ? `<span class="synergy-badge-priority" style="background: white; color: #10b981; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-left: 4px;">${synergyPriority}</span>` : ''}
                        </button>
                        <button class="thread-synergy-info" title="Show description" onclick="event.stopPropagation(); const badge = this.parentElement.querySelector('.synergy-badge[data-tooltip-title]'); if (badge && window.showSynergyTooltip) { window.showSynergyTooltip(badge, event); }">
                            <i class="fas fa-question-circle"></i>
                        </button>
                        <button class="thread-synergy-popout" title="Open in popup" onclick="event.stopPropagation(); if(window.synergyPopupModal) { window.synergyPopupModal.open('${safeEscape(thread.synergy_card_id)}'); } else { console.error('Synergy popup modal not loaded'); }">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                        ${location !== 'synergy' ? `
                            <button class="thread-synergy-unlink" title="Unlink Synergy session" onclick="event.stopPropagation(); ThreadManager.unlinkSynergy('${thread.id}', '${thread.synergy_card_id}')">
                                <i class="fas fa-unlink"></i>
                            </button>
                        ` : ''}
                    </div>
                ` : (location !== 'synergy' ? `
                    <div class="thread-item-synergy thread-item-synergy-unlinked" onclick="event.stopPropagation(); ThreadManager.openSynergySyncModal('${thread.id}')" title="Link thread to Synergy session">
                        <i class="fas fa-link"></i>
                        <span>Link Synergy Session</span>
                    </div>
                ` : '')}
                
                <!-- Automated Workflows (PURPLE pill) - Always visible -->
                ${thread.workflow_id ? `
                    <div class="thread-item-workflow thread-item-workflow-linked" data-workflow-id="${thread.workflow_id}">
                        <button class="workflow-badge" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; border: none; padding: 8px 14px; border-radius: 8px; display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: 500; cursor: pointer; flex: 1; box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3); transition: all 0.2s ease; position: relative; overflow: hidden;"
                            onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(139, 92, 246, 0.4)'"
                            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(139, 92, 246, 0.3)'"
                            onclick="event.stopPropagation(); ThreadManager.openWorkflowDetails('${thread.workflow_id}')"
                            title="${thread.workflow_name || thread.workflow_id}">
                            <i class="fas fa-robot" style="font-size: 14px; opacity: 0.95;"></i>
                            <span class="workflow-badge-title" style="letter-spacing: 0.01em;">${thread.workflow_name || thread.workflow_id}</span>
                        </button>
                        ${location !== 'synergy' ? `
                            <button class="thread-workflow-unlink" title="Unlink workflow" 
                                style="background: rgba(220, 38, 38, 0.1); color: #dc2626; border: 1px solid rgba(220, 38, 38, 0.3); padding: 6px 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s ease;"
                                onmouseover="this.style.background='rgba(220, 38, 38, 0.2)'; this.style.borderColor='rgba(220, 38, 38, 0.5)'"
                                onmouseout="this.style.background='rgba(220, 38, 38, 0.1)'; this.style.borderColor='rgba(220, 38, 38, 0.3)'"
                                onclick="event.stopPropagation(); ThreadManager.unlinkWorkflow('${thread.id}', '${thread.workflow_id}')">
                                <i class="fas fa-unlink"></i>
                            </button>
                        ` : ''}
                    </div>
                ` : `
                    <div class="thread-item-workflow thread-item-workflow-unlinked" onclick="event.stopPropagation(); ThreadManager.openWorkflowLinkModal('${thread.id}')" 
                        title="Link thread to Automated Workflow" 
                        style="border: 2px dashed rgba(139, 92, 246, 0.4); color: #8b5cf6; padding: 8px 14px; border-radius: 8px; cursor: pointer; transition: all 0.2s ease; background: rgba(139, 92, 246, 0.05); display: flex; align-items: center; gap: 8px;"
                        onmouseover="this.style.borderColor='rgba(139, 92, 246, 0.6)'; this.style.background='rgba(139, 92, 246, 0.1)'"
                        onmouseout="this.style.borderColor='rgba(139, 92, 246, 0.4)'; this.style.background='rgba(139, 92, 246, 0.05)'">
                        <i class="fas fa-robot"></i>
                        <span>Link Automated Workflow</span>
                    </div>
                `}
                
                <!-- Workflows (BLUE pill) - Always visible -->
                ${thread.automation_slug ? `
                    <div class="thread-item-automation thread-item-automation-linked" data-automation-id="${safeEscape(thread.automation_slug)}">
                        <button class="automation-badge" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; padding: 8px 14px; border-radius: 8px; display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: 500; cursor: pointer; flex: 1; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3); transition: all 0.2s ease; position: relative; overflow: hidden;"
                            onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(59, 130, 246, 0.4)'"
                            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(59, 130, 246, 0.3)'"
                            onclick="event.stopPropagation(); window.AutomationThreadIntegration.openAutomation('${safeEscape(thread.automation_slug)}')"
                            title="${safeEscape(thread.automation_title || thread.automation_slug)}">
                            <i class="fas fa-cogs" style="font-size: 14px; opacity: 0.95;"></i>
                            <span class="automation-badge-title" style="letter-spacing: 0.01em;">${safeEscape(thread.automation_title || thread.automation_slug)}</span>
                        </button>
                        ${location !== 'synergy' ? `
                            <button class="automation-unlink" title="Unlink automation" 
                                style="background: rgba(220, 38, 38, 0.1); color: #dc2626; border: 1px solid rgba(220, 38, 38, 0.3); padding: 6px 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s ease;"
                                onmouseover="this.style.background='rgba(220, 38, 38, 0.2)'; this.style.borderColor='rgba(220, 38, 38, 0.5)'"
                                onmouseout="this.style.background='rgba(220, 38, 38, 0.1)'; this.style.borderColor='rgba(220, 38, 38, 0.3)'"
                                onclick="event.stopPropagation(); window.AutomationThreadIntegration.unlinkAutomation('${thread.id}', '${safeEscape(thread.automation_slug)}')">
                                <i class="fas fa-unlink"></i>
                            </button>
                        ` : ''}
                    </div>
                ` : `
                    <div class="thread-item-automation thread-item-automation-unlinked" onclick="event.stopPropagation(); window.AutomationThreadIntegration.openLinkModal('${thread.id}')" 
                        title="Link thread to Workflow"
                        style="border: 2px dashed rgba(59, 130, 246, 0.4); color: #3b82f6; padding: 8px 14px; border-radius: 8px; cursor: pointer; transition: all 0.2s ease; background: rgba(59, 130, 246, 0.05); display: flex; align-items: center; gap: 8px;"
                        onmouseover="this.style.borderColor='rgba(59, 130, 246, 0.6)'; this.style.background='rgba(59, 130, 246, 0.1)'"
                        onmouseout="this.style.borderColor='rgba(59, 130, 246, 0.4)'; this.style.background='rgba(59, 130, 246, 0.05)'">
                        <i class="fas fa-cogs"></i>
                        <span>Link Workflow</span>
                    </div>
                `}
                
                <!-- Internal Docs/Sheets (AMBER pill) - Always visible -->
                ${thread.internal_doc_id ? `
                    <div class="thread-item-internal-doc thread-item-internal-doc-linked" data-internal-doc-id="${safeEscape(thread.internal_doc_id)}">
                        <button class="internal-doc-badge" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; border: none; padding: 8px 14px; border-radius: 8px; display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: 500; cursor: pointer; flex: 1; box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3); transition: all 0.2s ease; position: relative; overflow: hidden;"
                            onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(245, 158, 11, 0.4)'"
                            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(245, 158, 11, 0.3)'"
                            onclick="event.stopPropagation(); window.InternalDocsThreadIntegration.openDoc('${safeEscape(thread.internal_doc_id)}', '${thread.internal_doc_type || 'doc'}')"
                            title="${safeEscape(thread.internal_doc_title || thread.internal_doc_id)}">
                            <i class="fas ${thread.internal_doc_type === 'sheet' ? 'fa-table' : 'fa-file-alt'}" style="font-size: 14px; opacity: 0.95;"></i>
                            <span class="internal-doc-badge-title" style="letter-spacing: 0.01em;">${safeEscape(thread.internal_doc_title || thread.internal_doc_id)}</span>
                        </button>
                        ${location !== 'synergy' ? `
                            <button class="doc-unlink" title="Unlink document" 
                                style="background: rgba(220, 38, 38, 0.1); color: #dc2626; border: 1px solid rgba(220, 38, 38, 0.3); padding: 6px 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s ease;"
                                onmouseover="this.style.background='rgba(220, 38, 38, 0.2)'; this.style.borderColor='rgba(220, 38, 38, 0.5)'"
                                onmouseout="this.style.background='rgba(220, 38, 38, 0.1)'; this.style.borderColor='rgba(220, 38, 38, 0.3)'"
                                onclick="event.stopPropagation(); window.InternalDocsThreadIntegration.unlinkDoc('${thread.id}', '${safeEscape(thread.internal_doc_id)}')">
                                <i class="fas fa-unlink"></i>
                            </button>
                        ` : ''}
                    </div>
                ` : `
                    <div class="thread-item-internal-doc thread-item-internal-doc-unlinked" onclick="event.stopPropagation(); window.InternalDocsThreadIntegration.openLinkModal('${thread.id}')" 
                        title="Link thread to Internal Doc/Sheet"
                        style="border: 2px dashed rgba(245, 158, 11, 0.4); color: #f59e0b; padding: 8px 14px; border-radius: 8px; cursor: pointer; transition: all 0.2s ease; background: rgba(245, 158, 11, 0.05); display: flex; align-items: center; gap: 8px;"
                        onmouseover="this.style.borderColor='rgba(245, 158, 11, 0.6)'; this.style.background='rgba(245, 158, 11, 0.1)'"
                        onmouseout="this.style.borderColor='rgba(245, 158, 11, 0.4)'; this.style.background='rgba(245, 158, 11, 0.05)'">
                        <i class="fas fa-file-alt"></i>
                        <span>Link Internal Doc</span>
                    </div>
                `}

                <!-- Email Thread (TEAL pill) - Shows when thread has email data -->
                ${thread.email_thread_id ? `
                    <div class="thread-item-email thread-item-email-linked" data-email-id="${safeEscape(thread.email_thread_id)}">
                        <button class="email-badge" style="background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%); color: white; border: none; padding: 8px 14px; border-radius: 8px; display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: 500; cursor: pointer; flex: 1; box-shadow: 0 2px 8px rgba(20, 184, 166, 0.3); transition: all 0.2s ease; position: relative; overflow: hidden;"
                            onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(20, 184, 166, 0.4)'"
                            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(20, 184, 166, 0.3)'"
                            onclick="event.stopPropagation(); window.CommunicationHub?.openEmailPreview('${safeEscape(thread.email_thread_id)}')"
                            title="${safeEscape(thread.email_subject || 'Email')}">
                            <i class="fas fa-envelope" style="font-size: 14px; opacity: 0.95;"></i>
                            <span class="email-badge-title" style="letter-spacing: 0.01em;">${safeEscape(thread.email_subject || 'Email Thread')}</span>
                            ${thread.email_participants ? `<span style="opacity: 0.8; font-size: 11px; margin-left: 4px;">from ${safeEscape(thread.email_participants)}</span>` : ''}
                        </button>
                        ${location !== 'synergy' ? `
                            <button class="email-unlink" title="Unlink email" 
                                style="background: rgba(220, 38, 38, 0.1); color: #dc2626; border: 1px solid rgba(220, 38, 38, 0.3); padding: 6px 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s ease;"
                                onmouseover="this.style.background='rgba(220, 38, 38, 0.2)'; this.style.borderColor='rgba(220, 38, 38, 0.5)'"
                                onmouseout="this.style.background='rgba(220, 38, 38, 0.1)'; this.style.borderColor='rgba(220, 38, 38, 0.3)'"
                                onclick="event.stopPropagation(); ThreadManager.unlinkEmail('${thread.id}', '${safeEscape(thread.email_thread_id)}')">
                                <i class="fas fa-unlink"></i>
                            </button>
                        ` : ''}
                    </div>
                ` : ''}
                
            </div>
        `;
    },

    /**
     * Tags Row (Row 5) - Tags + Token count + Add tag button + Workflow slug (full mode only)
     * 
     * @param {Object} thread - Thread object
     * @param {string} location - Location identifier
     * @param {boolean} fullMode - Full mode flag (includes workflow slug)
     * @returns {string} HTML string for tags row
     */
    tagsRow(thread, location, fullMode = false) {
        const workflowSlug = fullMode && thread.workflow_slug ? `
            <span class="thread-workflow-slug" id="workflow-slug-${thread.id}" style="display: inline-flex; align-items: center; gap: 4px; background: rgba(255, 140, 0, 0.15); border: 1px solid #ff8c00; border-radius: 12px; padding: 4px 10px; font-size: 11px; font-family: 'Courier New', monospace; color: #ff8c00; cursor: pointer;" title="Click to load workflow" onclick="event.stopPropagation(); ThreadManager.loadWorkflowFromSlug('${thread.id}')">
                <i class="fas fa-project-diagram"></i> <span id="workflow-slug-text-${thread.id}">${thread.workflow_slug}</span>
                <button onclick="event.stopPropagation(); ThreadManager.unlinkWorkflowSlug('${thread.id}')" style="border: none; background: none; color: #ff8c00; padding: 0 2px; cursor: pointer; font-size: 12px; line-height: 1;" title="Remove workflow link">&times;</button>
            </span>
        ` : (fullMode ? `
            <span class="thread-workflow-slug" id="workflow-slug-${thread.id}" style="display: none; align-items: center; gap: 4px; background: rgba(255, 140, 0, 0.15); border: 1px solid #ff8c00; border-radius: 12px; padding: 4px 10px; font-size: 11px; font-family: 'Courier New', monospace; color: #ff8c00; cursor: pointer;" title="Click to load workflow" onclick="event.stopPropagation(); ThreadManager.loadWorkflowFromSlug('${thread.id}')">
                <i class="fas fa-project-diagram"></i> <span id="workflow-slug-text-${thread.id}"></span>
                <button onclick="event.stopPropagation(); ThreadManager.unlinkWorkflowSlug('${thread.id}')" style="border: none; background: none; color: #ff8c00; padding: 0 2px; cursor: pointer; font-size: 12px; line-height: 1; display: none;" title="Remove workflow link">&times;</button>
            </span>
        ` : '');

        return `
            <div class="thread-tags-row" id="thread-tags-row-${thread.id}" style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-top: 8px;">
                ${thread.tags ? thread.tags.map(tag => `
                    <span class="thread-tag-pill">
                        <i class="fas fa-tag"></i> ${tag}
                        ${location !== 'synergy' ? `
                            <button onclick="event.stopPropagation(); ThreadManager.removeTag('${thread.id}', '${tag}')" 
                                    class="tag-remove-btn" 
                                    title="Remove tag">&times;</button>
                        ` : ''}
                    </span>
                `).join('') : ''}
                ${workflowSlug}
                ${typeof thread.token_count !== 'undefined' ? `
                    <span class="thread-token-count" id="token-count-${thread.id}" title="Estimated tokens: ${thread.token_count}">
                        Tokens: <strong>${(thread.token_count).toLocaleString()}</strong>
                    </span>
                ` : `
                    <span class="thread-token-count" id="token-count-${thread.id}" style="display:none">
                        Tokens: <strong>0</strong>
                    </span>
                `}
                ${location !== 'synergy' ? `
                    <button class="add-tag-btn" 
                            onclick="event.stopPropagation(); ThreadManager.showAddTagModal('${location}', '${thread.id}')" 
                            title="Add tags to this thread">
                        <i class="fas fa-plus"></i> Tag
                    </button>
                ` : ''}
            </div>
        `;
    },

    /**
     * Lock Controls Row (Row 6) - Device lock/unlock toggle + device name (full mode only)
     * Shows lock status badge OR single lock/unlock toggle button + edit device name button
     * 
     * @param {Object} thread - Thread object
     * @returns {string} HTML string for lock controls row
     */
    lockControlsRow(thread) {
        return `
            <div class="lock-unlock-container" id="lock-controls-${thread.id}" style="display: flex; gap: 8px; margin-top: 8px;">
                <!-- Lock Status Badge (shown when locked by another device) -->
                <div class="lock-status-badge" id="lock-status-${thread.id}" style="display: none;">
                    <i class="fas fa-lock"></i>
                    <span>Locked to <strong id="lock-device-name-${thread.id}">Unknown Device</strong></span>
                </div>
                
                <!-- Single Lock/Unlock Toggle Button -->
                <button class="lock-toggle-btn" 
                        id="lock-toggle-${thread.id}" 
                        data-locked="false"
                        onclick="event.stopPropagation(); DeviceLockManager.toggleThreadLock('${thread.id}')"
                        title="Lock/Unlock this thread">
                    <i class="fas fa-lock-open"></i>
                    <span class="lock-toggle-text">Lock Thread</span>
                </button>
                
                <!-- Edit Device Name Button -->
                <button class="edit-device-name-btn" 
                        onclick="event.stopPropagation(); DeviceLockManager.showDeviceNameModal()"
                        title="Set a custom name for this device">
                    <i class="fas fa-edit"></i>
                    <span id="current-device-name-display">Edit Device Name</span>
                </button>
            </div>
        `;
    },

    // === PRIVATE HELPER METHODS ===

    /**
     * Copy Thread Dropdown - Internal helper
     * @private
     */
    _copyThreadDropdown(thread) {
        return `
            <div class="thread-copy-dropdown" style="position: relative;">
                <button class="thread-copy-btn"
                    onclick="event.stopPropagation(); ThreadManager.copyThreadConversation('${thread.id}')"
                    title="Copy full thread conversation">
                    <i class="fas fa-file-alt"></i>
                </button>
            </div>
        `;
    },

    /**
     * Thread ID Badge - Internal helper
     * @private
     */
    _threadIdBadge(thread, slug) {
        return `
            <button class="thread-id-badge"
                onclick="event.stopPropagation(); ThreadManager.copyThreadId('${thread.id}')"
                title="Copy thread slug: ${thread.id}">
                <i class="fas fa-hashtag"></i> ${slug}
            </button>
        `;
    },

    /**
     * Synergy Row - Full mode synergy section (internal helper)
     * @private
     */
    _synergyRow(thread, synergyMeta) {
        const safeEscape = window.safeEscape || ((str) => String(str).replace(/[&<>"']/g, ''));
        const synergyDisplay = thread.synergy_card_title || thread.synergy_card_id || 'Synergy Session';
        const synergyPriority = synergyMeta?.priority || '';

        // File count badge (Gap #1 fix)
        const fileCount = synergyMeta?.internal_docs_count || 0;
        const fileList = synergyMeta?.internal_docs || [];
        const fileTooltip = fileList.length > 0
            ? fileList.map(f => `📄 ${f.title} (${f.doc_type})`).join('\n')
            : 'No files attached';

        return thread.synergy_card_id ? `
            <div class="thread-item-synergy" data-synergy-id="${thread.synergy_card_id}">
                <button class="synergy-badge"
                    onclick="event.stopPropagation(); ThreadManager.copySynergyInfo('${safeEscape(thread.synergy_card_id)}', '${safeEscape(synergyDisplay)}')"
                    data-tooltip-title="${safeEscape(synergyDisplay)}"
                    data-tooltip-desc="${safeEscape(synergyMeta?.description || thread.synergy_card_desc || '')}"
                    data-tooltip-users="${safeEscape(thread.synergy_card_users || '')}"
                    data-tooltip-updated="${thread.synergy_card_updated || ''}">
                    <i class="fas fa-link"></i>
                    <span class="synergy-badge-title">${synergyDisplay}</span>
                    ${synergyPriority ? `<span class="synergy-badge-priority">${synergyPriority}</span>` : ''}
                </button>
                ${fileCount > 0 ? `
                <span class="synergy-file-count-badge" 
                      title="${safeEscape(fileTooltip)}"
                      onclick="event.stopPropagation(); ThreadManager.showSynergyFiles('${thread.synergy_card_id}')">
                    <i class="fas fa-file-alt"></i>
                    <span class="file-count">${fileCount}</span>
                </span>
                ` : ''}
                <button class="thread-synergy-unlink" title="Unlink Synergy session" onclick="event.stopPropagation(); ThreadManager.unlinkSynergy('${thread.id}', '${thread.synergy_card_id}')">
                    <i class="fas fa-unlink"></i>
                </button>
            </div>
        ` : `
            <div class="thread-item-synergy thread-item-synergy-unlinked">
                <button class="synergy-create-link" onclick="event.stopPropagation(); ThreadManager.openSynergySyncModal('${thread.id}')" title="Link thread to Synergy session">
                    <i class="fas fa-link"></i> Synergy Sync
                </button>
            </div>
        `;
    }
};

// Confirm module loaded
console.log('✅ [ThreadCardTemplates] Module loaded successfully');

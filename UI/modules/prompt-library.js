/**
 * PROMPT LIBRARY MODULE - JAVASCRIPT
 * 
 * Modular JavaScript for the prompt library feature
 * Handles API calls, state management, UI updates, and modal logic
 * Integrates with existing chat system
 * 
 * NO EMOJIS - Font Awesome icons only
 */

console.log('[PROMPT LIBRARY] ========================================');
console.log('[PROMPT LIBRARY] Module file loading...');
console.log('[PROMPT LIBRARY] ========================================');

(function () {
    'use strict';

    console.log('[PROMPT LIBRARY] IIFE executing...');

    // ==================== STATE MANAGEMENT ====================

    let selectedPrompts = [];
    let allPrompts = [];
    let editingPromptId = null;
    let isDropdownOpen = false;

    // Category icon mapping (Font Awesome)
    const categoryIcons = {
        'development': 'fa-code',
        'analysis': 'fa-chart-bar',
        'data': 'fa-database',
        'style': 'fa-comment',
        'business': 'fa-briefcase',
        'creative': 'fa-pen-fancy'
    };

    // ==================== API INTEGRATION ====================

    /**
     * Get API base URL (matches existing pattern in main file)
     */
    function getApiBaseUrl() {
        return window.API_BASE_URL || (window.location.hostname === 'localhost'
            ? 'http://localhost:5001'
            : window.location.origin);
    }

    /**
     * Get auth token from localStorage
     */
    function getAuthToken() {
        return localStorage.getItem('auth_token') || localStorage.getItem('token');
    }

    /**
     * Fetch prompt library from API
     */
    async function fetchPromptLibrary() {
        try {
            const token = getAuthToken();
            const response = await fetch(`${getApiBaseUrl()}/api/prompts/library/db?user_id=1`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                    'X-User-ID': '1'  // TODO: Get from actual user session
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            allPrompts = data.prompts || [];
            console.log('[PROMPT LIBRARY] Loaded prompts:', allPrompts.length);
            return allPrompts;
        } catch (error) {
            console.error('[PROMPT LIBRARY] Failed to fetch prompts:', error);
            showNotification('Failed to load prompt library', 'error');
            return [];
        }
    }

    /**
     * Save prompt (create or update)
     */
    async function savePromptToApi(promptData) {
        try {
            const token = getAuthToken();
            const url = editingPromptId
                ? `${getApiBaseUrl()}/api/prompts/library/db/${editingPromptId}`
                : `${getApiBaseUrl()}/api/prompts/library/db`;

            const method = editingPromptId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                    'X-User-ID': '1'  // TODO: Get from actual user session
                },
                body: JSON.stringify(promptData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[PROMPT LIBRARY] Saved prompt:', data);
            showNotification('Prompt saved successfully', 'success');
            return data;
        } catch (error) {
            console.error('[PROMPT LIBRARY] Failed to save prompt:', error);
            showNotification('Failed to save prompt', 'error');
            return null;
        }
    }

    /**
     * Delete prompt
     */
    async function deletePromptFromApi(promptId) {
        try {
            const token = getAuthToken();
            const response = await fetch(`${getApiBaseUrl()}/api/prompts/library/db/${promptId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                    'X-User-ID': '1'  // TODO: Get from actual user session
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            console.log('[PROMPT LIBRARY] Deleted prompt:', promptId);
            showNotification('Prompt deleted successfully', 'success');
            return true;
        } catch (error) {
            console.error('[PROMPT LIBRARY] Failed to delete prompt:', error);
            showNotification('Failed to delete prompt', 'error');
            return false;
        }
    }

    // ==================== UI INITIALIZATION ====================

    /**
     * Initialize the prompt library system
     */
    function initPromptLibrary() {
        console.log('[PROMPT LIBRARY] Initializing...');

        // Inject HTML templates into DOM
        injectHtmlTemplates();

        // Setup event listeners
        setupEventListeners();

        // Load prompts from API
        fetchPromptLibrary().then(prompts => {
            renderPromptList();
            console.log('[PROMPT LIBRARY] Initialization complete');
        });
    }

    /**
     * Inject HTML templates into the page
     */
    function injectHtmlTemplates() {
        // Find the chat input container
        const chatInputWrapper = document.querySelector('.ai-chat-input-wrapper');
        if (!chatInputWrapper) {
            console.error('[PROMPT LIBRARY] Chat input wrapper not found');
            return;
        }

        // Create active prompts bar
        const activePromptsBar = document.createElement('div');
        activePromptsBar.id = 'active-prompts-bar';
        activePromptsBar.className = 'active-prompts-bar';
        chatInputWrapper.insertBefore(activePromptsBar, chatInputWrapper.firstChild);

        // Create UNIFIED SIDEBAR (replaces dropdown + modal)
        // Only shows when user clicks bolt icon - NOT on page load
        const sidebar = document.createElement('div');
        sidebar.id = 'prompt-sidebar';
        sidebar.className = 'prompt-sidebar'; // NO 'show' class - starts hidden
        sidebar.innerHTML = `
            <div class="prompt-sidebar-header">
                <div class="prompt-sidebar-title">
                    <i class="fas fa-bolt"></i>
                    <span>Instructions Catalogue</span>
                </div>
            </div>
            
            <!-- TABS -->
            <div class="prompt-sidebar-tabs">
                <button class="sidebar-tab active" data-tab="browse" onclick="window.switchSidebarTab('browse')">
                    <i class="fas fa-list"></i> Browse
                </button>
                <button class="sidebar-tab" data-tab="editor" onclick="window.switchSidebarTab('editor')">
                    <i class="fas fa-edit"></i> <span id="editor-tab-label">Create New</span>
                </button>
            </div>
            
            <div class="prompt-sidebar-body">
                <!-- TAB 1: BROWSE PROMPTS -->
                <div id="browse-tab" class="sidebar-tab-content active">
                    <div class="prompt-dropdown-search-row">
                        <div class="search-wrapper">
                            <i class="fas fa-search search-icon"></i>
                            <input type="text" class="inline-search" id="inline-search" placeholder="Search prompts...">
                        </div>
                        <select class="category-dropdown" id="category-dropdown">
                            <option value="all">All Categories</option>
                            <option value="development">Development</option>
                            <option value="analysis">Analysis</option>
                            <option value="data">Data & SQL</option>
                            <option value="style">Communication Style</option>
                            <option value="business">Business</option>
                            <option value="creative">Creative</option>
                        </select>
                    </div>
                    
                    <div class="action-buttons-row">
                        <button class="action-btn active" data-filter="all" data-tooltip="Show All" onclick="window.filterPromptsByType('all')">
                            <i class="fas fa-th"></i>
                        </button>
                        <button class="action-btn" data-filter="quick" data-tooltip="Quick Actions" onclick="window.filterPromptsByType('quick')">
                            <i class="fas fa-bolt"></i>
                        </button>
                        <button class="action-btn" data-filter="detailed" data-tooltip="Detailed Prompts" onclick="window.filterPromptsByType('detailed')">
                            <i class="fas fa-list-ul"></i>
                        </button>
                        <button class="action-btn action-btn-create" data-tooltip="Create New Prompt" onclick="window.showEditorTab()">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>

                    <div class="prompt-list-scroll-area">
                        <div id="prompt-list-container"></div>
                    </div>
                </div>
                
                <!-- TAB 2: CREATE/EDIT (UNIFIED FORM) -->
                <div id="editor-tab" class="sidebar-tab-content">
                    <form id="prompt-form" onsubmit="event.preventDefault(); window.savePrompt();">
                        <input type="hidden" id="editing-prompt-id" value="">
                        
                        <div class="form-group">
                            <label for="prompt-title"><i class="fas fa-heading"></i> Prompt Title</label>
                            <input type="text" id="prompt-title" class="form-control" placeholder="e.g., Code Review Assistant" required>
                        </div>
                        <div class="form-group">
                            <label for="prompt-category"><i class="fas fa-folder"></i> Category</label>
                            <div style="display: flex; gap: 8px;">
                                <select id="prompt-category" class="form-control" required style="flex: 1;">
                                    <option value="development">Development</option>
                                    <option value="analysis">Analysis</option>
                                    <option value="data">Data & SQL</option>
                                    <option value="style">Communication Style</option>
                                    <option value="business">Business</option>
                                    <option value="creative">Creative</option>
                                </select>
                                <button type="button" class="btn-icon" onclick="window.addNewCategory()" title="Add Category" style="padding: 8px 12px; background: var(--accent-primary); color: white; border: none; border-radius: 6px; cursor: pointer;">
                                    <i class="fas fa-plus"></i>
                                </button>
                            </div>
                        </div>
                        <div class="form-group">
                            <label><i class="fas fa-bolt"></i> Prompt Type</label>
                            <div class="radio-group">
                                <label class="radio-label">
                                    <input type="radio" name="prompt-type" id="type-quick" value="quick_action" checked>
                                    <span>Quick Action</span>
                                    <small>Short directive (e.g., "Be concise")</small>
                                </label>
                                <label class="radio-label">
                                    <input type="radio" name="prompt-type" id="type-full" value="full_prompt">
                                    <span>Full Prompt</span>
                                    <small>Complete instructions with context</small>
                                </label>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="prompt-short-desc"><i class="fas fa-align-left"></i> Short Description</label>
                            <input type="text" id="prompt-short-desc" class="form-control" placeholder="Brief description shown in dropdown">
                        </div>
                        <div class="form-group">
                            <label for="prompt-text"><i class="fas fa-file-alt"></i> Prompt Text</label>
                            <textarea id="prompt-text" class="form-control" rows="8" placeholder="Enter your prompt instructions here..." required></textarea>
                        </div>
                        <div class="form-group">
                            <label for="prompt-tags"><i class="fas fa-tags"></i> Tags</label>
                            <input type="text" id="prompt-tags" class="form-control" placeholder="code, review, python (comma-separated)">
                        </div>
                        <div class="form-group">
                            <label for="prompt-visibility"><i class="fas fa-eye"></i> Visibility</label>
                            <select id="prompt-visibility" class="form-control">
                                <option value="private">Private (only you)</option>
                                <option value="workspace">Workspace (all members)</option>
                                <option value="public">Public (everyone)</option>
                            </select>
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- FOOTER -->
            <div class="prompt-sidebar-footer">
                <div id="browse-footer" class="footer-content active">
                    <button class="btn-secondary" onclick="window.closeSidebar()">Close</button>
                </div>
                <div id="editor-footer" class="footer-content">
                    <button id="delete-btn" class="btn-delete" onclick="window.deletePrompt()" style="display:none;">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                    <div style="flex: 1;"></div>
                    <button class="btn-secondary" onclick="window.cancelEditor()">Cancel</button>
                    <button class="btn-primary" onclick="window.savePrompt()">
                        <i class="fas fa-save"></i> <span id="save-btn-text">Create</span>
                    </button>
                </div>
            </div>
        `;
        chatInputWrapper.insertBefore(sidebar, chatInputWrapper.firstChild);

        console.log('[PROMPT LIBRARY] Unified sidebar created (starts hidden)');
    }

    /**
     * Setup event listeners
     */
    function setupEventListeners() {
        // Prompt trigger button click
        const triggerBtn = document.getElementById('ai-chat-prompt-library-btn');
        console.log('[PROMPT LIBRARY] Looking for button with ID: ai-chat-prompt-library-btn');
        console.log('[PROMPT LIBRARY] Button found:', triggerBtn);

        if (triggerBtn) {
            triggerBtn.addEventListener('click', function (e) {
                console.log('[PROMPT LIBRARY] Button clicked!');
                e.preventDefault();
                e.stopPropagation();
                togglePromptDropdown();
            });
            console.log('[PROMPT LIBRARY] Click listener attached to button');
        } else {
            console.error('[PROMPT LIBRARY] ERROR: Button not found! Cannot attach click listener.');
        }

        // Category dropdown change
        const categoryDropdown = document.getElementById('category-dropdown');
        if (categoryDropdown) {
            categoryDropdown.addEventListener('change', function (e) {
                filterPrompts(e.target.value);
            });
        }

        // Search input
        const searchInput = document.getElementById('inline-search');
        if (searchInput) {
            searchInput.addEventListener('input', function (e) {
                searchPrompts(e.target.value);
            });
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function (e) {
            const dropdown = document.getElementById('inline-prompt-dropdown');
            const triggerBtn = document.getElementById('ai-chat-prompt-library-btn');

            if (dropdown && triggerBtn &&
                !dropdown.contains(e.target) &&
                !triggerBtn.contains(e.target)) {
                closeDropdown();
            }
        });

        // Close sidebar when clicking outside (handled by global click listener above)
        
        console.log('[PROMPT LIBRARY] Event listeners setup complete');
    }

    // ==================== DROPDOWN LOGIC ====================

    /**
     * Toggle sidebar visibility (replaces old dropdown)
     */
    function togglePromptDropdown() {
        console.log('[PROMPT LIBRARY] togglePromptDropdown called (using sidebar)');
        const sidebar = document.getElementById('prompt-sidebar');
        const triggerBtn = document.getElementById('ai-chat-prompt-library-btn');

        if (!sidebar) {
            console.error('[PROMPT LIBRARY] ERROR: Sidebar element not found!');
            return;
        }

        if (!triggerBtn) {
            console.error('[PROMPT LIBRARY] ERROR: Button element not found!');
            return;
        }

        isDropdownOpen = !isDropdownOpen;
        console.log('[PROMPT LIBRARY] Sidebar open:', isDropdownOpen);

        if (isDropdownOpen) {
            console.log('[PROMPT LIBRARY] Opening sidebar...');
            sidebar.classList.add('show');
            triggerBtn.classList.add('active');
            // Always start on Browse tab
            window.switchSidebarTab('browse');
            document.getElementById('inline-search')?.focus();
        } else {
            console.log('[PROMPT LIBRARY] Closing sidebar...');
            window.closeSidebar();
        }
    }

    /**
     * Close sidebar
     */
    function closeSidebar() {
        const sidebar = document.getElementById('prompt-sidebar');
        const triggerBtn = document.getElementById('ai-chat-prompt-library-btn');

        if (sidebar) sidebar.classList.remove('show');
        if (triggerBtn) triggerBtn.classList.remove('active');
        isDropdownOpen = false;
        console.log('[PROMPT LIBRARY] Sidebar closed');
    }

    /**
     * Switch between Browse and Editor tabs
     */
    function switchSidebarTab(tabName) {
        console.log('[PROMPT LIBRARY] Switching to tab:', tabName);

        // Update tab buttons
        const tabs = document.querySelectorAll('.sidebar-tab');
        tabs.forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        // Update tab content
        const browseTab = document.getElementById('browse-tab');
        const editorTab = document.getElementById('editor-tab');

        if (tabName === 'browse') {
            browseTab?.classList.add('active');
            editorTab?.classList.remove('active');
            document.getElementById('browse-footer')?.classList.add('active');
            document.getElementById('editor-footer')?.classList.remove('active');
        } else if (tabName === 'editor') {
            browseTab?.classList.remove('active');
            editorTab?.classList.add('active');
            document.getElementById('browse-footer')?.classList.remove('active');
            document.getElementById('editor-footer')?.classList.add('active');
        }
    }

    /**
     * Show editor tab (for creating new or editing existing prompt)
     * @param {number} promptId - Optional: If provided, loads prompt for editing
     */
    function showEditorTab(promptId = null) {
        console.log('[PROMPT LIBRARY] showEditorTab called, promptId:', promptId);

        if (promptId) {
            // EDIT MODE: Load existing prompt
            const prompt = allPrompts.find(p => p.id === promptId);
            if (prompt) {
                console.log('[PROMPT LIBRARY] Loading prompt for editing:', prompt.name);

                // Set editing ID
                document.getElementById('editing-prompt-id').value = promptId;

                // Populate form (map to correct database columns)
                document.getElementById('prompt-title').value = prompt.name || '';
                document.getElementById('prompt-category').value = prompt.category || 'development';
                document.getElementById('prompt-short-desc').value = prompt.description || '';
                document.getElementById('prompt-text').value = prompt.prompt_text || '';

                // Handle tags - could be array or comma-separated string
                let tagsValue = '';
                if (prompt.tags) {
                    if (Array.isArray(prompt.tags)) {
                        tagsValue = prompt.tags.join(', ');
                    } else if (typeof prompt.tags === 'string') {
                        tagsValue = prompt.tags;
                    }
                }
                document.getElementById('prompt-tags').value = tagsValue;

                document.getElementById('prompt-visibility').value = prompt.visibility || 'private';

                // Set prompt type
                if (prompt.type === 'quick_action') {
                    document.getElementById('type-quick').checked = true;
                } else {
                    document.getElementById('type-full').checked = true;
                }

                // Update UI for edit mode
                document.getElementById('editor-tab-label').textContent = 'Edit Prompt';
                document.getElementById('save-btn-text').textContent = 'Save Changes';
                document.getElementById('delete-btn').style.display = 'block';
            }
        } else {
            // CREATE MODE: Clear form
            document.getElementById('editing-prompt-id').value = '';
            document.getElementById('prompt-form').reset();
            document.getElementById('type-quick').checked = true;

            // Update UI for create mode
            document.getElementById('editor-tab-label').textContent = 'Create New';
            document.getElementById('save-btn-text').textContent = 'Create';
            document.getElementById('delete-btn').style.display = 'none';
        }

        // Switch to editor tab
        switchSidebarTab('editor');
    }

    /**
     * Cancel editor and return to browse tab
     */
    function cancelEditor() {
        console.log('[PROMPT LIBRARY] Canceling editor');

        // Clear form
        document.getElementById('prompt-form').reset();
        document.getElementById('editing-prompt-id').value = '';

        // Switch back to browse tab
        switchSidebarTab('browse');
    }

    // Expose functions globally
    window.closeSidebar = closeSidebar;
    window.switchSidebarTab = switchSidebarTab;
    window.showEditorTab = showEditorTab;
    window.cancelEditor = cancelEditor;

    /**
     * Initialize modal drag functionality
     */
    function initializeModalDrag() {
        const modal = document.querySelector('.prompt-modal');
        const header = document.querySelector('.prompt-modal-header');

        if (!modal || !header) return;

        let isDragging = false;
        let currentX, currentY, initialX, initialY;

        header.style.cursor = 'move';

        header.addEventListener('mousedown', function (e) {
            if (e.target.classList.contains('prompt-modal-close')) return;
            isDragging = true;
            initialX = e.clientX - (modal.offsetLeft || 0);
            initialY = e.clientY - (modal.offsetTop || 0);
            modal.style.position = 'fixed';
        });

        document.addEventListener('mousemove', function (e) {
            if (!isDragging) return;
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            modal.style.left = currentX + 'px';
            modal.style.top = currentY + 'px';
            modal.style.transform = 'none';
        });

        document.addEventListener('mouseup', function () {
            isDragging = false;
        });
    }

    /**
     * Render prompt list in dropdown
     */
    function renderPromptList(filter = 'all', searchTerm = '') {
        const container = document.getElementById('prompt-list-container');
        if (!container) return;

        let filteredPrompts = [...allPrompts];

        // Filter by category
        if (filter !== 'all') {
            filteredPrompts = filteredPrompts.filter(p => p.category === filter);
        }

        // Filter by search term
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            filteredPrompts = filteredPrompts.filter(p =>
                p.name.toLowerCase().includes(term) ||
                (p.description && p.description.toLowerCase().includes(term)) ||
                (p.tags && p.tags.toLowerCase().includes(term))
            );
        }

        // Sort by name
        filteredPrompts.sort((a, b) => a.name.localeCompare(b.name));

        if (filteredPrompts.length === 0) {
            container.innerHTML = `
                <div class="prompt-empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>No prompts found</p>
                    <p class="text-muted">Try adjusting your search or filters</p>
                </div>
            `;
            return;
        }

        container.innerHTML = filteredPrompts.map(prompt => {
            const isSelected = selectedPrompts.some(p => p.id === prompt.id);
            const iconClass = categoryIcons[prompt.category] || 'fa-bolt';

            return `
                <div class="prompt-list-item ${isSelected ? 'selected' : ''}"
                     onclick="window.togglePromptSelection(${prompt.id})"
                     data-id="${prompt.id}">
                    <i class="prompt-icon fas ${iconClass}"></i>
                    <div class="prompt-info">
                        <div class="prompt-name">${escapeHtml(prompt.name)}</div>
                        <div class="prompt-description">${escapeHtml(prompt.description || '')}</div>
                    </div>
                    <div class="prompt-actions">
                        <button class="prompt-edit-btn" 
                                onclick="event.stopPropagation(); window.showEditorTab(${prompt.id});"
                                title="Edit prompt">
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                        <span class="prompt-type-badge ${prompt.type === 'quick_action' ? 'quick' : 'full'}">
                            ${prompt.type === 'quick_action' ? 'Quick' : 'Full'}
                        </span>
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Filter prompts by category
     */
    function filterPrompts(category) {
        const searchTerm = document.getElementById('inline-search')?.value || '';
        renderPromptList(category, searchTerm);
    }

    /**
     * Search prompts
     */
    function searchPrompts(searchTerm) {
        const activeCategory = document.querySelector('.filter-btn.active')?.dataset.category || 'all';
        renderPromptList(activeCategory, searchTerm);
    }

    /**
     * Toggle prompt selection
     */
    window.togglePromptSelection = function (promptId) {
        const prompt = allPrompts.find(p => p.id === promptId);
        if (!prompt) return;

        const index = selectedPrompts.findIndex(p => p.id === promptId);

        if (index > -1) {
            // Remove
            selectedPrompts.splice(index, 1);
        } else {
            // Add
            selectedPrompts.push(prompt);
        }

        updateActivePromptsBar();
        renderPromptList(
            document.querySelector('.filter-btn.active')?.dataset.category || 'all',
            document.getElementById('inline-search')?.value || ''
        );
        updateButtonBadge();

        console.log('[PROMPT LIBRARY] Selected prompts:', selectedPrompts.length);
    };

    /**
     * Update active prompts bar
     */
    function updateActivePromptsBar() {
        const bar = document.getElementById('active-prompts-bar');
        if (!bar) return;

        if (selectedPrompts.length === 0) {
            bar.classList.remove('show');
            return;
        }

        bar.classList.add('show');

        const promptTags = selectedPrompts.map(prompt => {
            const iconClass = categoryIcons[prompt.category] || 'fa-bolt';
            return `
            <div class="active-prompt-tag">
                    <i class="icon fas ${iconClass}"></i>
                    <span class="name">${escapeHtml(prompt.name)}</span>
                    <span class="remove" onclick="window.removePrompt(${prompt.id})">×</span>
                </div>
            `;
        }).join('');

        bar.innerHTML = `
            ${promptTags}
        <button class="clear-all-prompts" onclick="window.clearAllPrompts()">Clear All</button>
        `;
    }

    /**
     * Update button badge with count
     */
    function updateButtonBadge() {
        const btn = document.getElementById('ai-chat-prompt-library-btn');
        if (!btn) return;

        let badge = btn.querySelector('.prompt-count-badge');

        if (selectedPrompts.length > 0) {
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'prompt-count-badge';
                btn.appendChild(badge);
            }
            badge.textContent = selectedPrompts.length;
        } else {
            if (badge) badge.remove();
        }
    }

    /**
     * Remove single prompt
     */
    window.removePrompt = function (promptId) {
        window.togglePromptSelection(promptId);
    };

    /**
     * Clear all prompts
     */
    window.clearAllPrompts = function () {
        selectedPrompts = [];
        updateActivePromptsBar();
        renderPromptList(
            document.querySelector('.filter-btn.active')?.dataset.category || 'all',
            document.getElementById('inline-search')?.value || ''
        );
        updateButtonBadge();
    };

    // ==================== MODAL LOGIC ====================

    /**
     * OLD MODAL CODE - DISABLED (Use window.showEditorTab instead)
     */
    window.openPromptModal = function (promptId = null, openTab = null) {
        console.log('[PROMPT LIBRARY] openPromptModal is deprecated. Use window.showEditorTab() instead.');
        // Redirect to new sidebar system
        if (promptId) {
            window.showEditorTab(promptId);
        } else {
            window.showEditorTab();
        }
    };

    /**
     * Switch between Create and Edit tabs
     */
    window.switchPromptTab = function (tabName) {
        // Update tab buttons
        document.querySelectorAll('.prompt-tab').forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName} -tab`)?.classList.add('active');

        // Update footer
        document.querySelectorAll('.footer-content').forEach(footer => {
            footer.classList.remove('active');
        });
        document.getElementById(`${tabName} -footer`)?.classList.add('active');

        // Reset form if switching to create tab
        if (tabName === 'create') {
            document.getElementById('prompt-form')?.reset();
            editingPromptId = null;
        } else if (tabName === 'edit') {
            // Hide edit form until a prompt is selected
            const editFormContainer = document.getElementById('edit-form-container');
            if (editFormContainer) {
                editFormContainer.style.display = 'none';
            }
            // Clear selection
            document.querySelectorAll('.edit-prompt-item').forEach(item => {
                item.classList.remove('selected');
            });
            editingPromptId = null;
        }
    };

    /**
     * Load prompts into edit tab
     */
    window.loadEditPrompts = function () {
        const container = document.getElementById('edit-prompts-container');
        if (!container) return;

        if (allPrompts.length === 0) {
            container.innerHTML = `
            <div style="text-align: center; padding: 40px 20px; color: var(--text-muted);">
                    <i class="fas fa-inbox" style="font-size: 48px; margin-bottom: 16px; opacity: 0.3;"></i>
                    <p>No prompts yet. Create your first one!</p>
                </div>
            `;
            return;
        }

        const promptsHtml = allPrompts.map(prompt => {
            const icon = prompt.type === 'quick_action' ? 'fa-bolt' : 'fa-list-ul';
            const typeLabel = prompt.type === 'quick_action' ? 'Quick' : 'Detailed';
            const typeClass = prompt.type === 'quick_action' ? 'quick' : 'detailed';

            return `
            <div class="edit-prompt-item" onclick="window.selectPromptForEdit(${prompt.id})">
                <div class="edit-prompt-item-header">
                    <i class="fas ${icon} edit-prompt-item-icon"></i>
                    <span class="edit-prompt-item-name">${escapeHtml(prompt.name)}</span>
                    <span class="edit-prompt-item-type ${typeClass}">${typeLabel}</span>
                </div>
                    ${prompt.description ? `<p class="edit-prompt-item-desc">${escapeHtml(prompt.description)}</p>` : ''}
        <span class="edit-prompt-item-category">${escapeHtml(prompt.category)}</span>
                </div>
            `;
        }).join('');

        container.innerHTML = promptsHtml;
    };

    /**
     * Filter prompts in edit tab
     */
    window.filterEditPrompts = function (searchTerm) {
        const term = searchTerm.toLowerCase();
        const items = document.querySelectorAll('.edit-prompt-item');

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(term)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    };

    /**
     * Select a prompt for editing
     */
    window.selectPromptForEdit = function (promptId) {
        const prompt = allPrompts.find(p => p.id === promptId);
        if (!prompt) return;

        // Update UI - highlight selected item
        document.querySelectorAll('.edit-prompt-item').forEach(item => {
            item.classList.remove('selected');
        });
        event?.currentTarget?.classList.add('selected');

        // Store the editing ID
        editingPromptId = promptId;

        // Show the edit form container
        const editFormContainer = document.getElementById('edit-form-container');
        if (editFormContainer) {
            editFormContainer.style.display = 'block';

            // Scroll to form
            setTimeout(() => {
                editFormContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
        }

        // Update the "Editing" label
        const editingNameLabel = document.getElementById('editing-prompt-name');
        if (editingNameLabel) {
            editingNameLabel.textContent = prompt.name;
        }

        // Fill the edit form with this prompt's data
        document.getElementById('edit-prompt-title').value = prompt.name;
        document.getElementById('edit-prompt-category').value = prompt.category;
        document.getElementById('edit-prompt-short-desc').value = prompt.description || '';
        document.getElementById('edit-prompt-text').value = prompt.prompt_text;
        document.getElementById('edit-prompt-tags').value = prompt.tags || '';
        document.getElementById('edit-prompt-visibility').value = prompt.visibility || 'private';

        if (prompt.type === 'quick_action') {
            document.getElementById('edit-type-quick').checked = true;
        } else {
            document.getElementById('edit-type-full').checked = true;
        }

        // Show edit footer buttons
        document.getElementById('edit-footer').classList.add('active');
        document.getElementById('create-footer').classList.remove('active');
    };

    /**
     * DEPRECATED: Use closeSidebar() instead
     * Kept for backward compatibility
     */
    window.closePromptModal = function () {
        console.log('[PROMPT LIBRARY] closePromptModal is deprecated. Redirecting to closeSidebar()');
        window.closeSidebar();
    };

    /**
     * Save new prompt (Create tab)
     */
    window.savePrompt = async function () {
        const name = document.getElementById('prompt-title')?.value?.trim();
        const category = document.getElementById('prompt-category')?.value;
        const description = document.getElementById('prompt-short-desc')?.value?.trim();
        const promptText = document.getElementById('prompt-text')?.value?.trim();
        const tags = document.getElementById('prompt-tags')?.value?.trim();
        const visibility = document.getElementById('prompt-visibility')?.value || 'private';
        const type = document.querySelector('input[name="prompt-type"]:checked')?.value || 'quick_action';

        if (!name || !category || !promptText) {
            showNotification('Please fill in all required fields', 'error');
            return;
        }

        const promptData = {
            name: name,
            category: category,
            type: type,
            description: description,
            prompt_text: promptText,
            tags: tags,
            visibility: visibility
        };

        const result = await savePromptToApi(promptData);

        if (result) {
            showNotification('Prompt created successfully!', 'success');
            // Reload prompts
            await fetchPromptLibrary();
            renderPromptList();
            window.loadEditPrompts(); // Refresh edit tab list
            // Clear form and return to browse
            document.getElementById('prompt-form')?.reset();
            switchSidebarTab('browse');
        }
    };

    /**
     * Save edited prompt (Edit tab)
     */
    window.saveEditedPrompt = async function () {
        if (!editingPromptId) {
            showNotification('No prompt selected for editing', 'error');
            return;
        }

        const name = document.getElementById('edit-prompt-title')?.value?.trim();
        const category = document.getElementById('edit-prompt-category')?.value;
        const description = document.getElementById('edit-prompt-short-desc')?.value?.trim();
        const promptText = document.getElementById('edit-prompt-text')?.value?.trim();
        const tags = document.getElementById('edit-prompt-tags')?.value?.trim();
        const visibility = document.getElementById('edit-prompt-visibility')?.value || 'private';
        const type = document.querySelector('input[name="edit-prompt-type"]:checked')?.value || 'quick_action';

        if (!name || !category || !promptText) {
            showNotification('Please fill in all required fields', 'error');
            return;
        }

        const promptData = {
            id: editingPromptId,
            name: name,
            category: category,
            type: type,
            description: description,
            prompt_text: promptText,
            tags: tags,
            visibility: visibility
        };

        const result = await savePromptToApi(promptData);

        if (result) {
            showNotification('Prompt updated successfully!', 'success');
            // Reload prompts
            await fetchPromptLibrary();
            renderPromptList();
            window.loadEditPrompts(); // Refresh edit tab list
            switchSidebarTab('browse'); // Return to browse tab
        }
    };

    /**
     * Delete prompt
     */
    window.deletePrompt = async function () {
        if (!editingPromptId) return;

        if (!confirm('Are you sure you want to delete this prompt?')) {
            return;
        }

        const success = await deletePromptFromApi(editingPromptId);

        if (success) {
            // Remove from selected if present
            selectedPrompts = selectedPrompts.filter(p => p.id !== editingPromptId);

            // Reload prompts
            await fetchPromptLibrary();
            renderPromptList();
            updateActivePromptsBar();
            updateButtonBadge();
            switchSidebarTab('browse'); // Return to browse tab
        }
    };

    // ==================== INTEGRATION WITH CHAT ====================

    /**
     * Get selected prompts for injection into system prompt
     */
    window.getSelectedPrompts = function () {
        return selectedPrompts;
    };

    /**
     * Inject selected prompts into chat request
     * This should be called before sending a message
     */
    window.injectPromptsIntoRequest = function (requestData) {
        if (selectedPrompts.length > 0) {
            requestData.selected_prompts = selectedPrompts.map(p => ({
                id: p.id,
                name: p.name,
                prompt_text: p.prompt_text
            }));
        }
        return requestData;
    };

    /**
     * Filter prompts by type (quick/detailed/all)
     */
    window.filterPromptsByType = function (filterType) {
        // Update active button
        document.querySelectorAll('.action-btn[data-filter]').forEach(btn => {
            btn.classList.remove('active');
        });
        const activeBtn = document.querySelector(`.action-btn[data-filter="${filterType}"]`);
        if (activeBtn) activeBtn.classList.add('active');

        // Filter prompts
        const category = document.getElementById('category-dropdown')?.value || 'all';
        const searchTerm = document.getElementById('inline-search')?.value || '';

        let filteredPrompts = [...allPrompts];

        // Filter by category
        if (category !== 'all') {
            filteredPrompts = filteredPrompts.filter(p => p.category === category);
        }

        // Filter by type
        if (filterType === 'quick') {
            filteredPrompts = filteredPrompts.filter(p => p.type === 'quick_action');
        } else if (filterType === 'detailed') {
            filteredPrompts = filteredPrompts.filter(p => p.type === 'full_prompt');
        }

        // Filter by search term
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            filteredPrompts = filteredPrompts.filter(p =>
                p.name.toLowerCase().includes(term) ||
                (p.description && p.description.toLowerCase().includes(term)) ||
                (p.tags && p.tags.toLowerCase().includes(term))
            );
        }

        // Render filtered prompts
        renderFilteredPrompts(filteredPrompts);
    };

    /**
     * Toggle edit mode for prompts
     */
    window.toggleEditMode = function () {
        const editBtn = document.querySelector('.action-btn-edit');
        const isEditMode = editBtn.classList.toggle('active');

        // Toggle visibility of edit buttons
        const editButtons = document.querySelectorAll('.prompt-edit-btn');
        editButtons.forEach(btn => {
            btn.style.display = isEditMode ? 'flex' : 'none';
        });

        console.log('[PROMPT LIBRARY] Edit mode:', isEditMode ? 'ON' : 'OFF');
    };

    /**
     * Render filtered prompts (helper function)
     */
    function renderFilteredPrompts(prompts) {
        const container = document.getElementById('prompt-list-container');
        if (!container) return;

        prompts.sort((a, b) => a.name.localeCompare(b.name));

        if (prompts.length === 0) {
            container.innerHTML = `
            <div class="prompt-empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>No prompts found</p>
                    <p class="text-muted">Try adjusting your search or filters</p>
                </div>
            `;
            return;
        }

        container.innerHTML = prompts.map(prompt => {
            const isSelected = selectedPrompts.some(p => p.id === prompt.id);
            const iconClass = categoryIcons[prompt.category] || 'fa-bolt';

            return `
            <div class="prompt-list-item ${isSelected ? 'selected' : ''}" data-id="${prompt.id}">
                    <div class="prompt-clickable" onclick="window.togglePromptSelection(${prompt.id})">
                        <i class="prompt-icon fas ${iconClass}"></i>
                        <div class="prompt-info">
                            <div class="prompt-name">${escapeHtml(prompt.name)}</div>
                            <div class="prompt-description">${escapeHtml(prompt.description || '')}</div>
                        </div>
                        <span class="prompt-type-badge ${prompt.type === 'quick_action' ? 'quick' : 'full'}">
                            ${prompt.type === 'quick_action' ? 'Quick' : 'Detailed'}
                        </span>
                    </div>
                    <button class="prompt-edit-btn" style="display: none;"
                            onclick="event.stopPropagation(); window.openPromptModal(${prompt.id})"
                            title="Edit prompt">
                        <i class="fas fa-pencil-alt"></i>
                    </button>
                </div>
            `;
        }).join('');
    }

    // ==================== UTILITY FUNCTIONS ====================

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Show notification (reuses existing notification system if available)
     */
    function showNotification(message, type = 'info') {
        // Try to use existing notification system
        if (window.showNotification && typeof window.showNotification === 'function') {
            window.showNotification(message, type);
            return;
        }

        // Fallback to custom toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 100000;
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            animation: slideInRight 0.3s ease-out;
        `;

        const icon = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
        toast.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s';
            setTimeout(() => {
                if (toast.parentNode) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 3000);

        console.log(`[PROMPT LIBRARY] ${type.toUpperCase()}: ${message}`);
    }

    /**
     * Add new category to dropdown
     */
    window.addNewCategory = function () {
        const newCategory = prompt('Enter new category name:');
        if (newCategory && newCategory.trim()) {
            const categorySelect = document.getElementById('prompt-category');
            const categoryValue = newCategory.trim().toLowerCase().replace(/\s+/g, '_');
            const categoryLabel = newCategory.trim();

            // Check if category already exists
            const exists = Array.from(categorySelect.options).some(opt => opt.value === categoryValue);
            if (exists) {
                alert('This category already exists!');
                return;
            }

            // Add new option
            const option = document.createElement('option');
            option.value = categoryValue;
            option.textContent = categoryLabel;
            categorySelect.appendChild(option);
            categorySelect.value = categoryValue;

            console.log('[PROMPT LIBRARY] Added new category:', categoryLabel);
        }
    }

    // ==================== INITIALIZATION ====================

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPromptLibrary);
    } else {
        initPromptLibrary();
    }

    console.log('[PROMPT LIBRARY] Module loaded');

})();

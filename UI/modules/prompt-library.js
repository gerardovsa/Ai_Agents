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

        // Create inline dropdown
        const dropdown = document.createElement('div');
        dropdown.id = 'inline-prompt-dropdown';
        dropdown.className = 'inline-prompt-dropdown';
        dropdown.innerHTML = `
            <div class="prompt-dropdown-header">
                <div class="prompt-dropdown-title">
                    <i class="fas fa-wand-magic-sparkles"></i>
                    <span>Instructions Catalogue</span>
                </div>
                <button class="prompt-dropdown-close" onclick="window.closeDropdown()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div class="prompt-dropdown-search">
                <i class="fas fa-search search-icon"></i>
                <input type="text" class="inline-search" id="inline-search" placeholder="Search prompts...">
            </div>
            
            <div class="category-filter">
                <button class="filter-btn active" data-category="all">
                    <i class="fas fa-th"></i> All
                </button>
                <button class="filter-btn" data-category="development">
                    <i class="fas fa-code"></i> Dev
                </button>
                <button class="filter-btn" data-category="analysis">
                    <i class="fas fa-chart-bar"></i> Analysis
                </button>
                <button class="filter-btn" data-category="data">
                    <i class="fas fa-database"></i> Data
                </button>
                <button class="filter-btn" data-category="style">
                    <i class="fas fa-comment"></i> Style
                </button>
                <button class="filter-btn" data-category="business">
                    <i class="fas fa-briefcase"></i> Business
                </button>
                <button class="filter-btn" data-category="creative">
                    <i class="fas fa-pen-fancy"></i> Creative
                </button>
            </div>

            <div class="prompt-list-scroll-area">
                <div id="prompt-list-container"></div>
            </div>

            <div class="prompt-dropdown-footer">
                <button class="add-new-prompt-btn" onclick="window.openPromptModal()">
                    <i class="fas fa-plus-circle"></i>
                    <span>Create New Prompt</span>
                </button>
            </div>
        `;
        chatInputWrapper.insertBefore(dropdown, chatInputWrapper.firstChild);

        // Create modal overlay
        const modalOverlay = document.createElement('div');
        modalOverlay.id = 'prompt-modal-overlay';
        modalOverlay.className = 'prompt-modal-overlay';
        modalOverlay.innerHTML = `
            <div class="prompt-modal">
                <div class="prompt-modal-header">
                    <h2><i class="fas fa-bolt"></i> <span id="prompt-modal-title">Create New Prompt</span></h2>
                    <button class="prompt-modal-close" onclick="window.closePromptModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="prompt-modal-body">
                    <form id="prompt-form">
                        <div class="form-group">
                            <label class="form-label">Prompt Title <span class="required">*</span></label>
                            <input type="text" class="form-input" id="prompt-title" placeholder="e.g., Expert Coder" required>
                            <div class="form-help">A clear, descriptive name for the prompt</div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Category <span class="required">*</span></label>
                            <div class="category-management">
                                <select class="form-select" id="prompt-category" required>
                                    <option value="">Select Category</option>
                                    <option value="development">Development</option>
                                    <option value="analysis">Analysis</option>
                                    <option value="data">Data & SQL</option>
                                    <option value="style">Style</option>
                                    <option value="business">Business</option>
                                    <option value="creative">Creative</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Prompt Type <span class="required">*</span></label>
                            <div class="radio-group">
                                <div class="radio-option">
                                    <input type="radio" id="type-quick" name="promptType" value="quick_action" checked>
                                    <label for="type-quick">Quick Action (Short, focused)</label>
                                </div>
                                <div class="radio-option">
                                    <input type="radio" id="type-full" name="promptType" value="full_prompt">
                                    <label for="type-full">Full Prompt (Detailed, long)</label>
                                </div>
                            </div>
                            <div class="form-help">
                                Quick Action: Brief instructions (e.g., "Be concise", "Use type hints")<br>
                                Full Prompt: Comprehensive instructions with examples and guidelines
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Short Description</label>
                            <input type="text" class="form-input" id="prompt-short-desc" placeholder="One-line description for the dropdown" maxlength="100">
                            <div class="form-help">Brief description shown in prompt list (50-100 characters)</div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Prompt Content <span class="required">*</span></label>
                            <textarea class="form-textarea large" id="prompt-text" placeholder="Enter the full prompt instructions..." required></textarea>
                            <div class="form-help">
                                The actual prompt text that will be injected into the AI's system prompt.<br>
                                Be specific and clear about what you want the AI to do.
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Tags (comma-separated)</label>
                            <input type="text" class="form-input" id="prompt-tags" placeholder="python, coding, best-practices">
                            <div class="form-help">Keywords for search and discovery</div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Visibility</label>
                            <select class="form-select" id="prompt-visibility">
                                <option value="private">Private (Only me)</option>
                                <option value="workspace">Workspace (Team)</option>
                                <option value="public">Public (Everyone)</option>
                            </select>
                        </div>
                    </form>
                </div>
                <div class="prompt-modal-footer">
                    <button class="btn btn-secondary" onclick="window.closePromptModal()">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                    <button class="btn btn-danger hidden" id="delete-prompt-btn" onclick="window.deletePrompt()">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                    <button class="btn btn-primary" onclick="window.savePrompt()">
                        <i class="fas fa-save"></i> Save Prompt
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modalOverlay);

        console.log('[PROMPT LIBRARY] HTML templates injected');
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

        // Category filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                filterPrompts(this.dataset.category);
            });
        });

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

        // Close modal when clicking overlay
        const modalOverlay = document.getElementById('prompt-modal-overlay');
        if (modalOverlay) {
            modalOverlay.addEventListener('click', function (e) {
                if (e.target === this) {
                    window.closePromptModal();
                }
            });
        }

        console.log('[PROMPT LIBRARY] Event listeners setup complete');
    }

    // ==================== DROPDOWN LOGIC ====================

    /**
     * Toggle prompt dropdown visibility
     */
    function togglePromptDropdown() {
        console.log('[PROMPT LIBRARY] togglePromptDropdown called');
        const dropdown = document.getElementById('inline-prompt-dropdown');
        const triggerBtn = document.getElementById('ai-chat-prompt-library-btn');

        console.log('[PROMPT LIBRARY] Dropdown element:', dropdown);
        console.log('[PROMPT LIBRARY] Button element:', triggerBtn);

        if (!dropdown) {
            console.error('[PROMPT LIBRARY] ERROR: Dropdown element not found!');
            return;
        }

        if (!triggerBtn) {
            console.error('[PROMPT LIBRARY] ERROR: Button element not found!');
            return;
        }

        isDropdownOpen = !isDropdownOpen;
        console.log('[PROMPT LIBRARY] isDropdownOpen:', isDropdownOpen);

        if (isDropdownOpen) {
            console.log('[PROMPT LIBRARY] Opening dropdown...');
            dropdown.classList.add('show');
            triggerBtn.classList.add('active');
            document.getElementById('inline-search')?.focus();
            console.log('[PROMPT LIBRARY] Dropdown should now be visible');
        } else {
            console.log('[PROMPT LIBRARY] Closing dropdown...');
            closeDropdown();
        }
    }

    /**
     * Close dropdown
     */
    function closeDropdown() {
        const dropdown = document.getElementById('inline-prompt-dropdown');
        const triggerBtn = document.getElementById('ai-chat-prompt-library-btn');

        if (dropdown) dropdown.classList.remove('show');
        if (triggerBtn) triggerBtn.classList.remove('active');
        isDropdownOpen = false;
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
                    <span class="prompt-type-badge ${prompt.type === 'quick_action' ? 'quick' : 'full'}">
                        ${prompt.type === 'quick_action' ? 'Quick' : 'Full'}
                    </span>
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
     * Open modal for creating/editing prompt
     */
    window.openPromptModal = function (promptId = null) {
        editingPromptId = promptId;
        const modal = document.getElementById('prompt-modal-overlay');
        const title = document.getElementById('prompt-modal-title');
        const deleteBtn = document.getElementById('delete-prompt-btn');

        if (!modal) return;

        if (promptId) {
            // Edit mode
            const prompt = allPrompts.find(p => p.id === promptId);
            if (!prompt) return;

            title.textContent = 'Edit Prompt';
            deleteBtn?.classList.remove('hidden');

            // Fill form
            document.getElementById('prompt-title').value = prompt.name;
            document.getElementById('prompt-category').value = prompt.category;
            document.getElementById('prompt-short-desc').value = prompt.description || '';
            document.getElementById('prompt-text').value = prompt.prompt_text;
            document.getElementById('prompt-tags').value = prompt.tags || '';
            document.getElementById('prompt-visibility').value = prompt.visibility || 'private';

            if (prompt.type === 'quick_action') {
                document.getElementById('type-quick').checked = true;
            } else {
                document.getElementById('type-full').checked = true;
            }
        } else {
            // Create mode
            title.textContent = 'Create New Prompt';
            deleteBtn?.classList.add('hidden');
            document.getElementById('prompt-form')?.reset();
        }

        modal.classList.add('show');
    };

    /**
     * Close modal
     */
    window.closePromptModal = function () {
        const modal = document.getElementById('prompt-modal-overlay');
        if (modal) modal.classList.remove('show');
        editingPromptId = null;
    };

    /**
     * Save prompt
     */
    window.savePrompt = async function () {
        const name = document.getElementById('prompt-title')?.value;
        const category = document.getElementById('prompt-category')?.value;
        const description = document.getElementById('prompt-short-desc')?.value;
        const promptText = document.getElementById('prompt-text')?.value;
        const tags = document.getElementById('prompt-tags')?.value;
        const visibility = document.getElementById('prompt-visibility')?.value || 'private';
        const type = document.querySelector('input[name="promptType"]:checked')?.value || 'quick_action';

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
            // Reload prompts
            await fetchPromptLibrary();
            renderPromptList();
            window.closePromptModal();
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
            window.closePromptModal();
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
        if (window.showNotification) {
            window.showNotification(message, type);
            return;
        }

        // Fallback to console
        console.log(`[PROMPT LIBRARY] ${type.toUpperCase()}: ${message}`);
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

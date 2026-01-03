/**
 * FILE: UI/modules/thread-manager/thread-manager-crud.js
 * PURPOSE: Create, Update, Delete operations for threads
 * 
 * DEPENDENCIES:
 * - UI/modules/thread-manager/thread-manager-core.js (must load first)
 * 
 * EXPORTS:
 * - Extends window.ThreadManager with CRUD methods
 * 
 * USED BY:
 * - UI/business-ai-platform-v2.html (main application)
 * - UI/modules/thread-manager/thread-manager-ui.js (thread cards)
 * - UI/modules/thread-manager/thread-manager-interactions.js (user actions)
 * 
 * RELATED FILES:
 * - UI/modules/thread-manager/thread-manager-core.js (core object)
 * - UI/modules/thread-manager/thread-manager-ui.js (UI updates)
 * 
 * NOTES:
 * - Handles all thread lifecycle operations
 * - Create new threads, update existing, delete threads
 * - Manages API calls for thread persistence
 * 
 * LAST MODIFIED: 2025-11-20 - Initial file creation
 */

// CRUD methods will be defined here
// Awaiting code paste from user


// ==================== THREAD MANAGER - CRUD MODULE ====================
/**
 * Thread CRUD Operations
 * Create, Read, Update, Delete threads
 * 
 * ARCHITECTURE:
 * - Uses ThreadLoader for backend persistence (data layer)
 * - Manages local thread state (this.threads array)
 * - Updates UI via renderThreadList()
 */

// Extend ThreadManager with CRUD methods
window.ThreadManager = window.ThreadManager || {};
Object.assign(window.ThreadManager, {
    /**
     * Create new thread (client-side only - for quick UI updates)
     */
    createThread() {
        const thread = {
            id: Date.now().toString(),
            title: 'New Chat',
            messages: [],
            created: new Date().toISOString(),
            updated: new Date().toISOString(),
            archived: false,
            agent: 'main',
            location: 'unassigned',
            message_count: 0,
            tags: []
        };

        this.threads.unshift(thread);
        console.log('✅ [CRUD] Thread created:', thread.id);

        // Save to backend using ThreadLoader (async)
        if (typeof window.ThreadLoader !== 'undefined') {
            window.ThreadLoader.saveThreadToBackend(thread).catch(err => {
                console.error('❌ [CRUD] Backend save failed:', err);
            });
        }

        return thread.id;
    },

    /**
     * Create thread with full metadata (backend-first)
     */
    async createThreadWithMetadata(title, tags, location = 'prime') {
        console.log('🔄 [CRUD] Creating thread with metadata:', { title, tags, location });

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/threads/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1,
                    title: title,
                    tags: tags || [],
                    location: location
                })
            });

            if (!response.ok) {
                throw new Error(`Thread creation failed: ${response.statusText}`);
            }

            const data = await response.json();

            console.log('🔍 [CRUD] Backend response:', data);

            if (!data.success) {
                throw new Error(`Thread creation failed: ${data.error || 'Unknown error'}`);
            }

            // Extract thread from various possible response structures
            const newThread = data.thread || data.data?.thread || data.data || null;

            if (!newThread) {
                console.error('❌ [CRUD] No thread in response. Full data:', JSON.stringify(data, null, 2));
                throw new Error('Backend returned success but no thread data. Check console for details.');
            }

            const newThreadId = newThread.id || newThread.thread_id;

            // Add to local threads array
            const threadForUI = {
                id: newThreadId,
                title: title || 'Untitled Thread',
                messages: [],
                tags: tags || [],
                location: location || 'unassigned',
                agent: location === 'unassigned' ? null : location,
                created: newThread.created_at || new Date().toISOString(),
                updated: newThread.updated_at || new Date().toISOString(),
                message_count: 0,
                archived: false
            };

            this.threads.unshift(threadForUI);
            console.log('✅ [CRUD] Thread created with metadata:', newThreadId);

            // 🔔 NEW: Add notification for thread creation
            if (typeof NotificationCenter !== 'undefined' && NotificationCenter.add) {
                NotificationCenter.add({
                    type: 'THREAD_CREATED',
                    message: `Thread "${title || 'Untitled'}" created successfully`,
                    metadata: {
                        threadId: newThreadId,
                        threadName: title || 'Untitled Thread',
                        location: location,
                        tags: tags || []
                    },
                    action: {
                        type: 'open_thread',
                        target: { threadId: newThreadId }
                    }
                });
                console.log(`[CRUD] 🔔 Notification added for thread creation: ${newThreadId}`);
            }

            // Assign to location (force 'prime' instead of 'unassigned')
            if (typeof this.assignThread === 'function') {
                await this.assignThread(newThreadId, location === 'unassigned' ? 'prime' : location);
            }

            // Refresh UI - IMMEDIATE (thread creation)
            if (typeof this.renderThreadList === 'function') {
                this.renderThreadList(true); // immediate=true bypasses debounce
            }

            return newThreadId;

        } catch (error) {
            console.error('❌ [CRUD] Failed to create thread:', error);
            throw error;
        }
    },

    /**
     * Delete thread
     */
    async deleteThread(threadId) {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.warn('[CRUD] Thread not found:', threadId);
            return;
        }

        // Show confirmation
        if (typeof showConfirmation === 'function') {
            showConfirmation(
                'Delete Thread?',
                `Are you sure you want to delete "${thread.title}"? This action cannot be undone.`,
                async () => {
                    try {
                        // Delete from backend
                        const response = await fetch(`${this.apiBaseUrl}/api/threads/${threadId}`, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${UserAuth.token || ''}`
                            }
                        });

                        if (!response.ok) {
                            throw new Error(`Failed to delete: ${response.statusText}`);
                        }

                        // Remove from local array
                        this.threads = this.threads.filter(t => t.id !== threadId);

                        // Clear from UI if currently loaded
                        if (this.currentThreadId === threadId) {
                            this.currentThreadId = null;
                            const primeMessages = document.getElementById('ai-chat-messages');
                            if (primeMessages) primeMessages.innerHTML = '';
                            if (typeof this.showStartNewChatButton === 'function') {
                                this.showStartNewChatButton('ai-chat-messages', 'prime');
                            }
                        }

                        // Refresh UI - IMMEDIATE (user action)
                        if (typeof this.renderThreadList === 'function') {
                            this.renderThreadList(true); // immediate=true bypasses debounce
                        }

                        if (typeof showNotification === 'function') {
                            showNotification('Thread deleted successfully', 'success');
                        }

                        console.log('✅ [CRUD] Thread deleted:', threadId);

                    } catch (error) {
                        console.error('❌ [CRUD] Delete failed:', error);
                        if (typeof showNotification === 'function') {
                            showNotification('Failed to delete thread', 'error');
                        }
                    }
                }
            );
        }
    },

    /**
     * Edit thread metadata
     */
    async editThread(threadId) {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.warn('[CRUD] Thread not found:', threadId);
            return;
        }

        // Show edit modal
        const modalHTML = `
            <div class="modal-overlay" id="editThreadModalOverlay">
                <div class="new-chat-modal">
                    <div class="modal-header">
                        <h3>✏️ Edit Thread</h3>
                        <button class="modal-close" onclick="document.getElementById('editThreadModalOverlay').remove()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <form id="editThreadForm">
                            <div class="form-group">
                                <label for="editThreadTitle">Thread Title <span style="color: var(--accent-error);">*</span></label>
                                <input type="text" id="editThreadTitle" class="form-control" value="${thread.title}" required autofocus>
                            </div>
                            <div class="form-group">
                                <label for="editThreadTags">Tags (comma-separated)</label>
                                <input type="text" id="editThreadTags" class="form-control" value="${(thread.tags || []).join(', ')}" placeholder="e.g., urgent, research, client-work">
                            </div>
                            <div class="modal-actions">
                                <button type="button" class="btn btn-secondary" onclick="document.getElementById('editThreadModalOverlay').remove()">
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save"></i> Save Changes
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Handle form submission
        const form = document.getElementById('editThreadForm');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const newTitle = document.getElementById('editThreadTitle').value.trim();
            const newTagsStr = document.getElementById('editThreadTags').value.trim();
            const newTags = newTagsStr ? newTagsStr.split(',').map(t => t.trim()).filter(t => t) : [];

            if (!newTitle) {
                alert('Please enter a thread title');
                return;
            }

            try {
                // Update backend
                const response = await fetch(`${this.apiBaseUrl}/api/threads/${threadId}/update`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: newTitle,
                        tags: newTags
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to update thread');
                }

                // Update local thread
                thread.title = newTitle;
                thread.tags = newTags;
                thread.updated = new Date().toISOString();

                // Close modal
                document.getElementById('editThreadModalOverlay').remove();

                // Refresh UI
                if (typeof this.renderThreadList === 'function') {
                    this.renderThreadList();
                }
                if (typeof this.refreshAllThreadInfoCards === 'function') {
                    this.refreshAllThreadInfoCards(threadId);
                }

                if (typeof showNotification === 'function') {
                    showNotification('Thread updated successfully', 'success');
                }

                console.log('✅ [CRUD] Thread updated:', threadId);

            } catch (error) {
                console.error('❌ [CRUD] Update failed:', error);
                alert('Failed to update thread. Please try again.');
            }
        });
    },

    /**
     * Fork thread (branch from current point)
     */
    async forkThread(threadId) {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.warn('[CRUD] Thread not found:', threadId);
            return;
        }

        const messageCount = thread.message_count || thread.messages?.length || 0;

        if (messageCount === 0) {
            if (typeof showNotification === 'function') {
                showNotification('Cannot fork empty thread', 'warning');
            }
            return;
        }

        const branchName = prompt(`Fork thread "${thread.title}"\n\nEnter branch name:`, `${thread.title} (fork)`);
        if (!branchName) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/messages/fork`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: threadId,
                    message_id: null,
                    branch_name: branchName,
                    user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1
                })
            });

            if (!response.ok) {
                throw new Error('Fork failed');
            }

            const result = await response.json();

            if (typeof showNotification === 'function') {
                showNotification(`Thread forked! ${result.messages_copied} messages copied.`, 'success');
            }

            // Reload threads
            await this.loadThreadsFromBackend();
            if (typeof this.renderThreadList === 'function') {
                this.renderThreadList();
            }

            // Switch to new thread
            if (result.new_thread_id && typeof this.switchThread === 'function') {
                await this.switchThread(result.new_thread_id);
            }

            console.log('✅ [CRUD] Thread forked:', result.new_thread_id);

        } catch (error) {
            console.error('❌ [CRUD] Fork failed:', error);
            if (typeof showNotification === 'function') {
                showNotification('Failed to fork thread', 'error');
            }
        }
    },

    /**
     * Clone thread (duplicate all messages)
     */
    async cloneThread(threadId) {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) {
            console.warn('[CRUD] Thread not found:', threadId);
            return;
        }

        const messageCount = thread.message_count || thread.messages?.length || 0;

        if (messageCount === 0) {
            if (typeof showNotification === 'function') {
                showNotification('Cannot clone empty thread', 'warning');
            }
            return;
        }

        const newName = prompt(`Clone thread "${thread.title}"\n\nEnter new thread name:`, `${thread.title} (copy)`);
        if (!newName) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/messages/clone`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: threadId,
                    new_name: newName,
                    user_id: (UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1
                })
            });

            if (!response.ok) {
                throw new Error('Clone failed');
            }

            const result = await response.json();

            if (typeof showNotification === 'function') {
                showNotification(`Thread cloned! ${result.messages_cloned} messages copied.`, 'success');
            }

            // Reload threads
            await this.loadThreadsFromBackend();
            if (typeof this.renderThreadList === 'function') {
                this.renderThreadList();
            }

            // Switch to new thread
            if (result.new_thread_id && typeof this.switchThread === 'function') {
                await this.switchThread(result.new_thread_id);
            }

            console.log('✅ [CRUD] Thread cloned:', result.new_thread_id);

        } catch (error) {
            console.error('❌ [CRUD] Clone failed:', error);
            if (typeof showNotification === 'function') {
                showNotification('Failed to clone thread', 'error');
            }
        }
    },

    /**
     * Archive thread
     */
    async archiveThread(threadId) {
        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) return;

        if (typeof showConfirmation === 'function') {
            showConfirmation(
                'Archive Thread?',
                `Archive "${thread.title}"? You can restore it later from the Archived filter.`,
                async () => {
                    thread.archived = true;
                    thread.updated = new Date().toISOString();

                    await this.saveThreadToBackend(thread);

                    if (typeof this.renderThreadList === 'function') {
                        this.renderThreadList(true); // immediate=true bypasses debounce
                    }

                    if (typeof showNotification === 'function') {
                        showNotification('Thread archived', 'success');
                    }
                }
            );
        }
    },

    /**
     * Start inline title edit
     */
    startInlineTitleEdit(location, threadId) {
        const titleEl = document.getElementById(`${location}-thread-title`);
        if (!titleEl) return;

        const thread = this.threads.find(t => t.id === threadId);
        if (!thread) return;

        const currentTitle = thread.title || 'Untitled Thread';

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'thread-title-input';
        input.value = currentTitle;

        titleEl.innerHTML = '';
        titleEl.classList.add('editing');
        titleEl.appendChild(input);
        input.focus();
        input.select();

        const saveEdit = async () => {
            const newTitle = input.value.trim();

            if (newTitle && newTitle !== currentTitle) {
                thread.title = newTitle;
                thread.updated = new Date().toISOString();

                try {
                    await fetch(`${this.apiBaseUrl}/api/threads/${threadId}/update`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: newTitle })
                    });

                    if (typeof showNotification === 'function') {
                        showNotification(`Thread renamed to "${newTitle}"`, 'success');
                    }
                } catch (error) {
                    console.error('❌ [CRUD] Failed to save title:', error);
                }
            }

            titleEl.classList.remove('editing');
            if (typeof this.updatePrimeHeader === 'function' && location === 'unassigned') {
                this.updatePrimeHeader(thread);
            }
            if (typeof this.renderThreadList === 'function') {
                this.renderThreadList();
            }
        };

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveEdit();
            }
        });

        input.addEventListener('blur', saveEdit);

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                e.preventDefault();
                titleEl.classList.remove('editing');
                if (location === 'unassigned' && typeof this.updatePrimeHeader === 'function') {
                    this.updatePrimeHeader(thread);
                }
            }
        });
    },

    /**
     * Mark thread as prime (main AI sidebar)
     * Automatically unmarks any existing prime thread
     */
    async markAsPrimeLoaded(threadId) {
        try {
            const thread = this.threads.find(t => t.id === threadId);
            if (!thread) {
                showNotification('Thread not found', 'error');
                return;
            }

            // Check if already in prime
            if (thread.location === 'prime') {
                showNotification('This thread is already in Prime', 'info');
                return;
            }

            // Use assignThread to update location to 'prime'
            await this.assignThread(threadId, 'prime');

            // Update local thread state
            // Unmark all other prime threads
            this.threads.forEach(t => {
                if (t.location === 'prime' && t.id !== threadId) {
                    t.location = 'unassigned';
                }
            });

            // Mark this thread
            thread.location = 'prime';
            thread.updated = new Date().toISOString();

            // Update UI
            this.renderThreadList();

            showNotification('Thread assigned to Prime', 'success');
            console.log(`🎯 [ThreadManager] Marked thread ${threadId} as prime`);

        } catch (error) {
            console.error('❌ [ThreadManager] Failed to mark as prime:', error);
            showNotification('Failed to set startup thread', 'error');
        }
    }
});

console.log('✅ ThreadManager-CRUD module loaded');
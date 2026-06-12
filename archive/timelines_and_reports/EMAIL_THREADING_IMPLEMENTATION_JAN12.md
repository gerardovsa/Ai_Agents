# Email Threading Implementation - Gmail-Style Collapsed View
**Date**: January 12, 2026  
**Feature**: Collapse email threads by default and show full conversation on click

---

## Changes Required

### 1. Add State for Thread Expansion (Line ~83)

```javascript
// FIND:
        emailTags: {}, // { emailId: 'green' | 'orange' | 'red' | null }
        emailThreads: {}, // { emailId: thread_slug }
        threads: [], // Array of thread assignments from backend

        // UI state
        currentTab: 'unified-inbox',

// REPLACE WITH:
        emailTags: {}, // { emailId: 'green' | 'orange' | 'red' | null }
        emailThreads: {}, // { emailId: thread_slug }
        threads: [], // Array of thread assignments from backend
        expandedThreads: new Set(), // Set of thread_ids that are expanded
        collapsedEmails: [], // Collapsed view (only latest per thread)

        // UI state
        currentTab: 'unified-inbox',
```

---

### 2. Add createCollapsedView Function (Line ~1288 after groupEmailsByThread)

```javascript
    /**
     * Create collapsed view (Gmail-style: show only latest message per thread)
     * @param {Object} groupingStats - Result from groupEmailsByThread()
     * @returns {Array} Collapsed email list
     */
    createCollapsedView(groupingStats) {
        const collapsedView = [];

        // Add latest message from each chain
        groupingStats.chains.forEach(chain => {
            const latestEmail = chain.latest_message;
            // Mark as thread for UI rendering
            latestEmail._isThread = true;
            latestEmail._threadCount = chain.message_count;
            latestEmail._threadMessages = chain.messages;
            collapsedView.push(latestEmail);
        });

        // Add all single messages
        groupingStats.singles.forEach(email => {
            email._isThread = false;
            email._threadCount = 1;
            collapsedView.push(email);
        });

        // Sort by date (newest first)
        collapsedView.sort((a, b) => new Date(b.date) - new Date(a.date));

        return collapsedView;
    },
```

---

### 3. Update loadEmails to Create Collapsed View (Line ~1315)

```javascript
// FIND (around line 1315):
            this.state.emails = response.emails || [];

            // NEW: Calculate conversation stats
            const groupingStats = this.groupEmailsByThread(this.state.emails);
            this.log.success(`Loaded ${this.state.emails.length} emails in ${groupingStats.stats.total_conversations} conversations (${groupingStats.stats.chain_count} chains, ${groupingStats.stats.single_count} singles)`);

            // Check if no emails returned and no accounts connected

// REPLACE WITH:
            this.state.emails = response.emails || [];

            // NEW: Calculate conversation stats and create collapsed view
            const groupingStats = this.groupEmailsByThread(this.state.emails);
            this.log.success(`Loaded ${this.state.emails.length} emails in ${groupingStats.stats.total_conversations} conversations (${groupingStats.stats.chain_count} chains, ${groupingStats.stats.single_count} singles)`);

            // Create collapsed view (show only latest message per thread)
            this.state.collapsedEmails = this.createCollapsedView(groupingStats);
            this.log.info(`Collapsed view: ${this.state.collapsedEmails.length} rows (from ${this.state.emails.length} emails)`);

            // Check if no emails returned and no accounts connected
```

---

### 4. Update createEmailTable to Use Collapsed Data (Line ~1424)

```javascript
// FIND (around line 1424):
        // Create table (WooCommerce Gold Standard Pattern)
        // Phase 2 Features: Header filters, pagination with size selector, movable/resizable columns, persistent layout
        const tableData = this.state.emails;

// REPLACE WITH:
        // Create table (WooCommerce Gold Standard Pattern)
        // Phase 2 Features: Header filters, pagination with size selector, movable/resizable columns, persistent layout
        const tableData = this.state.collapsedEmails.length > 0 ? this.state.collapsedEmails : this.state.emails;
```

---

### 5. Update Subject Column Formatter (Line ~1538)

```javascript
// FIND the Subject column formatter (starts around line 1538):
                    formatter: (cell) => {
                        const value = cell.getValue() || '(No subject)';
                        const data = cell.getRow().getData();
                        const hasThread = this.state.emailThreads[data.id];
                        const isRead = data.is_read;
                        const hasAttachments = data.has_attachments;

                        // NEW: Detect if this email is part of a chain (multiple emails with same thread_id)
                        const threadId = data.thread_id;
                        const chainCount = threadId ? this.state.emails.filter(e => e.thread_id === threadId).length : 0;
                        const isChain = chainCount > 1;

                        let html = '<div style="display: flex; align-items: center; gap: 8px;">';

                        // NEW: Chain badge (shows message count if >1)
                        if (isChain) {
                            html += `<span style="background: #6366f1; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;" title="${chainCount} messages in conversation">${chainCount}</span>`;
                        }

                        // Thread indicator (AI assignment)
                        if (hasThread) {
                            html += `<i class="fas fa-comments" style="color: #6366f1; font-size: 12px;" title="Assigned to AI agent"></i>`;
                        }

                        // Subject text
                        html += `<span style="color: #ffffff; font-weight: ${isRead ? '400' : '600'}; flex: 1;">${this.escapeHtml(value)}</span>`;

                        // Attachment indicator
                        if (hasAttachments) {
                            html += `<i class="fas fa-paperclip" style="color: #6b7280; font-size: 11px;"></i>`;
                        }

                        html += '</div>';
                        return html;
                    }

// REPLACE WITH:
                    formatter: (cell) => {
                        const value = cell.getValue() || '(No subject)';
                        const data = cell.getRow().getData();
                        const hasThread = this.state.emailThreads[data.id];
                        const isRead = data.is_read;
                        const hasAttachments = data.has_attachments;

                        // Check if this is a collapsed thread
                        const isThread = data._isThread === true;
                        const threadCount = data._threadCount || 1;
                        const threadId = data.thread_id;
                        const isExpanded = this.state.expandedThreads.has(threadId);
                        const isThreadChild = data._isThreadChild === true;

                        let html = '<div style="display: flex; align-items: center; gap: 8px;">';

                        // Indentation for thread children
                        if (isThreadChild) {
                            html += '<span style="width: 24px;"></span>';
                        }

                        // Expand/collapse button for threads
                        if (isThread && threadCount > 1) {
                            const icon = isExpanded ? 'chevron-down' : 'chevron-right';
                            html += `<button 
                                onclick="window.communicationHub.toggleThread('${threadId}', event)" 
                                style="background: none; border: none; color: #9ca3af; cursor: pointer; padding: 4px; display: flex; align-items: center; justify-content: center; transition: color 0.2s;"
                                onmouseover="this.style.color='#3b82f6'"
                                onmouseout="this.style.color='#9ca3af'"
                                title="${isExpanded ? 'Collapse' : 'Expand'} thread"
                            >
                                <i class="fas fa-${icon}" style="font-size: 12px;"></i>
                            </button>`;
                            
                            // Thread count badge
                            html += `<span style="background: #6366f1; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;" title="${threadCount} messages in conversation">${threadCount}</span>`;
                        }

                        // Thread indicator (AI assignment)
                        if (hasThread && !isThreadChild) {
                            html += `<i class="fas fa-comments" style="color: #6366f1; font-size: 12px;" title="Assigned to AI agent"></i>`;
                        }

                        // Subject text
                        html += `<span style="color: #ffffff; font-weight: ${isRead ? '400' : '600'}; flex: 1;">${this.escapeHtml(value)}</span>`;

                        // Attachment indicator
                        if (hasAttachments) {
                            html += `<i class="fas fa-paperclip" style="color: #6b7280; font-size: 11px;"></i>`;
                        }

                        html += '</div>';
                        return html;
                    }
```

---

### 6. Add toggleThread and refreshTableWithThreads Functions (Before hideEmailPreview ~line 3500)

```javascript
    /**
     * Toggle thread expansion/collapse (Gmail-style)
     */
    toggleThread(threadId, event) {
        if (event) {
            event.stopPropagation();
        }

        const isExpanded = this.state.expandedThreads.has(threadId);

        if (isExpanded) {
            // Collapse: remove thread from expanded set
            this.state.expandedThreads.delete(threadId);
            this.log.debug(`Collapsed thread: ${threadId}`);
        } else {
            // Expand: add thread to expanded set
            this.state.expandedThreads.add(threadId);
            this.log.debug(`Expanded thread: ${threadId}`);
        }

        // Rebuild table data with expanded threads
        this.refreshTableWithThreads();
    },

    /**
     * Refresh table data with expanded threads shown
     */
    refreshTableWithThreads() {
        if (!this.state.tabulatorTable) return;

        const expandedData = [];

        // Build new data array with expanded threads inline
        this.state.collapsedEmails.forEach(email => {
            if (email._isThread && email._threadCount > 1) {
                const threadId = email.thread_id;
                const isExpanded = this.state.expandedThreads.has(threadId);

                // Always add the parent (collapsed view)
                expandedData.push(email);

                // If expanded, add all child messages indented
                if (isExpanded && email._threadMessages) {
                    // Sort thread messages by date (oldest first for chronological order)
                    const sortedMessages = [...email._threadMessages].sort((a, b) => 
                        new Date(a.date) - new Date(b.date)
                    );

                    // Add child messages (skip the first one as it's the parent)
                    sortedMessages.slice(1).forEach(childEmail => {
                        expandedData.push({
                            ...childEmail,
                            _isThreadChild: true,
                            _parentThreadId: threadId
                        });
                    });
                }
            } else {
                // Single email
                expandedData.push(email);
            }
        });

        // Update table data
        this.state.tabulatorTable.setData(expandedData);
        this.log.debug(`Table refreshed: ${expandedData.length} rows (${this.state.expandedThreads.size} expanded threads)`);
    },
```

---

### 7. Update showEmailPreview to Show Conversation Thread (Line ~3760)

```javascript
// FIND (around line 3760):
            // Check if email is part of thread
            const threadSlug = this.state.emailThreads[emailData.id];
            let threadEmails = [];

            // ENABLED: Fetch all emails in thread for chronological preview
            if (threadSlug) {
                this.log.info(`📬 Email is part of thread: ${threadSlug}`);
                try {
                    threadEmails = await this.fetchThreadEmails(threadSlug);
                    this.log.success(`Fetched ${threadEmails.length} emails in thread`);
                } catch (threadError) {
                    this.log.warn('Could not fetch thread emails:', threadError);
                    // Continue with single email view
                }
            }

// REPLACE WITH:
            // Check if email is part of conversation thread
            const threadId = fullEmail.thread_id;
            let conversationEmails = [];

            // Show full conversation if this email is part of a thread
            if (threadId) {
                // Find all emails in this conversation
                conversationEmails = this.state.emails
                    .filter(e => e.thread_id === threadId)
                    .sort((a, b) => new Date(a.date) - new Date(b.date)); // Chronological order

                this.log.info(`📬 Showing conversation with ${conversationEmails.length} messages`);
            }

            // Check if email is assigned to AI thread
            const threadSlug = this.state.emailThreads[emailData.id];
            let aiThreadEmails = [];

            // ENABLED: Fetch AI thread emails if assigned
            if (threadSlug) {
                this.log.info(`🤖 Email is assigned to AI thread: ${threadSlug}`);
                try {
                    aiThreadEmails = await this.fetchThreadEmails(threadSlug);
                    this.log.success(`Fetched ${aiThreadEmails.length} emails from AI thread`);
                } catch (threadError) {
                    this.log.warn('Could not fetch AI thread emails:', threadError);
                }
            }
```

---

### 8. Update Preview HTML to Use Conversation Thread (Line ~3775)

```javascript
// FIND (around line 3775):
            // Render preview based on thread status
            let contentHtml = '';

            if (threadEmails.length > 1) {
                // Thread view with all emails
                contentHtml = this.renderThreadPreview(threadEmails, emailData.id);
            } else {

// REPLACE WITH:
            // Render preview based on thread status
            let contentHtml = '';

            if (conversationEmails.length > 1) {
                // Show full conversation thread (Gmail-style)
                contentHtml = this.renderConversationThread(conversationEmails, fullEmail);
            } else {
```

---

### 9. Add renderConversationThread Function (Before renderAttachmentsSection ~line 4100)

```javascript
    /**
     * Render conversation thread (Gmail-style)
     */
    renderConversationThread(conversationEmails, currentEmail) {
        let html = `
            <div style="padding: 16px 20px;">
                <div style="background: rgba(59, 130, 246, 0.1); border-left: 3px solid #3b82f6; padding: 12px 16px; border-radius: 4px; margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 8px; color: #3b82f6; font-weight: 600; font-size: 13px;">
                        <i class="fas fa-comments"></i>
                        <span>Conversation Thread (${conversationEmails.length} messages)</span>
                    </div>
                </div>
        `;

        // Render each message in the conversation
        conversationEmails.forEach((email, index) => {
            const isCurrent = email.id === currentEmail.id;
            const isLast = index === conversationEmails.length - 1;

            html += `
                <div style="
                    border-left: 3px solid ${isCurrent ? '#3b82f6' : '#30363d'};
                    padding-left: 16px;
                    margin-bottom: ${isLast ? '0' : '24px'};
                    background: ${isCurrent ? 'rgba(59, 130, 246, 0.05)' : 'transparent'};
                    border-radius: 4px;
                    padding: 12px;
                ">
                    <!-- Message header -->
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                        <div style="flex: 1;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                                ${isCurrent ? '<span style="background: #3b82f6; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 700;">CURRENT</span>' : ''}
                                <span style="color: #ffffff; font-weight: 600; font-size: 14px;">${this.escapeHtml(email.from)}</span>
                            </div>
                            <div style="color: #6b7280; font-size: 12px;">
                                ${this.formatDate(email.date)}
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            ${email.has_attachments ? '<i class="fas fa-paperclip" style="color: #6b7280; font-size: 12px;" title="Has attachments"></i>' : ''}
                            <span style="color: #6b7280; font-size: 11px;">Message ${index + 1} of ${conversationEmails.length}</span>
                        </div>
                    </div>

                    <!-- Message content -->
                    <div style="color: #e6edf3; font-size: 13px; line-height: 1.6;">
                        ${email.snippet || '(No preview available)'}
                    </div>

                    ${isCurrent && email.body ? `
                        <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #30363d;">
                            <div style="color: #6b7280; font-size: 11px; margin-bottom: 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                <i class="fas fa-align-left" style="margin-right: 4px;"></i>
                                Full Message Content
                            </div>
                            ${this.renderEmailBody({ body: email.body })}
                        </div>
                    ` : ''}
                </div>
            `;
        });

        html += `</div>`;
        return html;
    },
```

---

## Summary

### What This Implements:

✅ **Collapsed View by Default**: Shows only the latest message per conversation thread  
✅ **Thread Count Badge**: Displays number of messages in conversation (e.g., `[3]`)  
✅ **Expand/Collapse Button**: Chevron icon to toggle thread expansion  
✅ **Full Conversation View**: When clicking an email in a thread, shows all messages chronologically  
✅ **Gmail-Style UI**: Blue highlights for current message, chronological ordering  

### User Experience:

1. **Inbox View**: User sees collapsed threads (one row per conversation)
2. **Click Chevron**: Expands thread inline, shows all messages
3. **Click Email**: Opens preview with full conversation thread
4. **Scroll Preview**: Sees all messages in conversation with the current one highlighted

---

**Status**: Implementation code ready - apply changes to `communication-hub-v4-modern.js`

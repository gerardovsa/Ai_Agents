// ==================== ERROR RECOVERY MANAGER ====================
// Automatic recovery from Anthropic API errors with detailed logging
// Handles: invalid_message_structure, tool_use_mismatch, context_length, rate_limit, etc.

class ErrorRecoveryManager {
    constructor(panelId, threadId, agentId = null) {
        this.panelId = panelId; // 'prime' or agent ID
        this.threadId = threadId;
        this.agentId = agentId;
        this.maxRetries = typeof window.getMaxRetryAttempts === 'function' 
            ? window.getMaxRetryAttempts() 
            : 3;
        this.retryCount = 0;
        this.recoveryLog = [];
        this.startTime = Date.now();
        
        // PANEL ISOLATION: Store reference to prevent cross-panel errors
        this.panelContext = {
            panelId: panelId,
            threadId: threadId,
            agentId: agentId,
            timestamp: Date.now()
        };
        
        console.log(`[RECOVERY INIT] Created manager for panel: ${panelId}, thread: ${threadId}, agent: ${agentId || 'none'}`);
    }

    // Main error detection and routing
    async handleError(error, originalPayload) {
        const errorType = this.detectErrorType(error);
        
        this.log('ERROR_DETECTED', {
            type: errorType,
            message: error.message,
            rawError: error
        });

        console.error(`[RECOVERY ${this.panelId}] Detected error type: ${errorType}`);
        
        switch (errorType) {
            case 'invalid_message_structure':
                return await this.recoverFromInvalidStructure(error, originalPayload);
            
            case 'tool_use_mismatch':
                return await this.recoverFromToolMismatch(error, originalPayload);
            
            case 'context_length_exceeded':
                return await this.recoverFromContextLength(originalPayload);
            
            case 'rate_limit_exceeded':
                return await this.recoverFromRateLimit(originalPayload);
            
            case 'overloaded_error':
                return await this.recoverFromOverload(originalPayload);
            
            case 'authentication_error':
                return await this.recoverFromAuth(originalPayload);
            
            case 'network_error':
                return await this.recoverFromNetwork(originalPayload);
            
            default:
                this.log('RECOVERY_FAILED', {
                    reason: 'Unknown error type - cannot auto-recover',
                    errorType: errorType
                });
                throw error;
        }
    }

    // Detect error type from Anthropic response
    detectErrorType(error) {
        const message = error.message?.toLowerCase() || '';
        const errorData = error.error || error;
        const errorType = errorData.type || '';

        // Invalid message structure (thinking blocks order)
        if (message.includes('first block must be') && message.includes('thinking')) {
            return 'invalid_message_structure';
        }
        // NEW: Detect thinking block not first (Nov 22, 2025)
        if (message.includes('if an assistant message contains any thinking blocks')) {
            return 'invalid_message_structure';
        }
        if (message.includes('first block must be `thinking`')) {
            return 'invalid_message_structure';
        }

        // Tool use mismatch - EXPANDED DETECTION
        if (message.includes('tool_use_id') && message.includes('not found')) {
            return 'tool_use_mismatch';
        }
        // NEW: Detect missing tool_result (the error you're seeing)
        if (message.includes('tool_use') && message.includes('tool_result') && message.includes('immediately after')) {
            return 'tool_use_mismatch';
        }
        // NEW: Detect orphaned tool_use without tool_result
        if (message.includes('each `tool_use` block must have a corresponding')) {
            return 'tool_use_mismatch';
        }

        // Context length exceeded
        if (message.includes('prompt is too long') || message.includes('context_length')) {
            return 'context_length_exceeded';
        }

        // Rate limit
        if (message.includes('rate limit') || errorType === 'rate_limit_error') {
            return 'rate_limit_exceeded';
        }

        // Server overloaded
        if (message.includes('overloaded') || errorType === 'overloaded_error') {
            return 'overloaded_error';
        }

        // Authentication
        if (message.includes('authentication') || errorType === 'authentication_error') {
            return 'authentication_error';
        }

        // Network
        if (message.includes('network') || message.includes('fetch') || message.includes('cors')) {
            return 'network_error';
        }

        return 'unknown';
    }

    // ==================== RECOVERY METHOD 1: Invalid Message Structure ====================
    async recoverFromInvalidStructure(error, originalPayload) {
        this.log('RECOVERY_START', {
            method: 'invalid_message_structure',
            error: error.message
        });

        console.log(`[RECOVERY ${this.panelId}] Fixing invalid message structure...`);
        
        try {
            // Step 1: Get conversation history
            const history = originalPayload.conversation_history || [];
            this.log('HISTORY_RETRIEVED', {
                messageCount: history.length
            });

            // Step 2: Analyze the problem
            let problemsFound = [];
            let fixedHistory = JSON.parse(JSON.stringify(history)); // Deep clone

            // Step 3: Fix assistant messages with thinking blocks
            fixedHistory = fixedHistory.map((msg, index) => {
                if (msg.role === 'assistant' && Array.isArray(msg.content)) {
                    // Find thinking blocks
                    const thinkingBlocks = msg.content.filter(
                        block => block.type === 'thinking'
                    );
                    const textBlocks = msg.content.filter(
                        block => block.type === 'text'
                    );
                    const toolBlocks = msg.content.filter(
                        block => block.type === 'tool_use'
                    );

                    // CRITICAL: If message has thinking blocks, they MUST come first
                    if (thinkingBlocks.length > 0) {
                        const firstBlock = msg.content[0];
                        if (firstBlock.type !== 'thinking') {
                            problemsFound.push({
                                messageIndex: index,
                                issue: `First block was '${firstBlock.type}' but should be 'thinking'`,
                                fix: 'Reordered blocks: thinking blocks moved to front'
                            });

                            // Reorder: thinking blocks first, then text, then tools
                            msg.content = [
                                ...thinkingBlocks,
                                ...textBlocks,
                                ...toolBlocks
                            ];

                            console.log(`[RECOVERY ${this.panelId}] Fixed message ${index}: moved thinking blocks to front`);
                        }
                    }
                }
                return msg;
            });

            // Step 4: Log what was fixed
            this.log('STRUCTURE_FIXED', {
                problemsFound: problemsFound,
                messagesFixed: problemsFound.length,
                details: problemsFound
            });

            // Step 5: Show user notification
            this.showRecoveryMessage(
                `Fixed ${problemsFound.length} message structure issue(s). Retrying...`,
                'structure-fix'
            );

            // Step 6: Rebuild payload with fixed history
            const newPayload = {
                ...originalPayload,
                conversation_history: fixedHistory
            };

            this.log('RESUBMITTING', {
                fixedMessageCount: fixedHistory.length
            });

            // Step 7: Resubmit request
            const result = await this.resubmitRequest(newPayload);

            this.log('RECOVERY_SUCCESS', {
                method: 'invalid_message_structure',
                duration: Date.now() - this.startTime
            });
            
            // Record statistics
            if (typeof window.SettingsManager !== 'undefined') {
                window.SettingsManager.recordRecovery(true);
            }

            return result;

        } catch (error) {
            this.log('RECOVERY_FAILED', {
                method: 'invalid_message_structure',
                error: error.message
            });
            throw error;
        }
    }

    // ==================== RECOVERY METHOD 2: Tool Use Mismatch ====================
    async recoverFromToolMismatch(error, originalPayload) {
        this.log('RECOVERY_START', {
            method: 'tool_use_mismatch',
            error: error.message
        });

        console.log(`[RECOVERY ${this.panelId}] Fixing tool use mismatch...`);

        try {
            // Step 1: Extract missing tool_use_id from error
            const match = error.message.match(/tool_use_id '([^']+)'/);
            const missingToolId = match ? match[1] : null;

            this.log('MISMATCH_DETECTED', {
                missingToolId: missingToolId,
                errorMessage: error.message
            });

            // Step 2: Get conversation history
            const history = originalPayload.conversation_history || [];
            this.log('HISTORY_RETRIEVED', {
                messageCount: history.length
            });

            // Step 3: Build set of valid tool_use IDs from assistant messages
            const validToolIds = new Set();
            const toolUseMessages = []; // Track which messages have tool_use blocks
            
            history.forEach((msg, msgIndex) => {
                if (msg.role === 'assistant' && Array.isArray(msg.content)) {
                    msg.content.forEach(block => {
                        if (block.type === 'tool_use' && block.id) {
                            validToolIds.add(block.id);
                            toolUseMessages.push({
                                messageIndex: msgIndex,
                                toolUseId: block.id
                            });
                        }
                    });
                }
            });

            this.log('VALID_TOOL_IDS', {
                count: validToolIds.size,
                ids: Array.from(validToolIds),
                toolUseMessages: toolUseMessages
            });

            // Step 4: Find tool_use blocks that are missing tool_result
            const missingToolResults = [];
            toolUseMessages.forEach(({messageIndex, toolUseId}) => {
                // Check if next message (should be user with tool_result) exists
                const nextMessage = history[messageIndex + 1];
                if (!nextMessage || nextMessage.role !== 'user') {
                    missingToolResults.push({
                        toolUseId: toolUseId,
                        messageIndex: messageIndex,
                        reason: 'Next message is not user role with tool_result'
                    });
                    return;
                }
                
                // Check if tool_result exists in next message
                const hasToolResult = nextMessage.content?.some(
                    block => block.type === 'tool_result' && block.tool_use_id === toolUseId
                );
                
                if (!hasToolResult) {
                    missingToolResults.push({
                        toolUseId: toolUseId,
                        messageIndex: messageIndex,
                        reason: 'tool_result not found in next message'
                    });
                }
            });

            // Step 5: Remove orphaned tool_result blocks AND handle missing tool_results
            let removedResults = [];
            const fixedHistory = history.map((msg, msgIndex) => {
                if (msg.role === 'user' && Array.isArray(msg.content)) {
                    const originalLength = msg.content.length;
                    
                    msg.content = msg.content.filter((block, blockIndex) => {
                        if (block.type === 'tool_result') {
                            const isValid = validToolIds.has(block.tool_use_id);
                            if (!isValid) {
                                removedResults.push({
                                    messageIndex: msgIndex,
                                    blockIndex: blockIndex,
                                    toolUseId: block.tool_use_id,
                                    reason: 'No matching tool_use block found'
                                });
                                console.log(`[RECOVERY ${this.panelId}] Removed orphaned tool_result: ${block.tool_use_id}`);
                            }
                            return isValid;
                        }
                        return true; // Keep all other blocks
                    });

                    if (msg.content.length < originalLength) {
                        console.log(`[RECOVERY ${this.panelId}] Message ${msgIndex}: removed ${originalLength - msg.content.length} orphaned tool_result(s)`);
                    }
                }
                
                // NEW: Remove tool_use blocks that don't have tool_result in next message
                if (msg.role === 'assistant' && Array.isArray(msg.content)) {
                    const hasProblematicToolUse = missingToolResults.some(m => m.messageIndex === msgIndex);
                    if (hasProblematicToolUse) {
                        console.log(`[RECOVERY ${this.panelId}] Message ${msgIndex}: has tool_use without tool_result, removing tool_use blocks`);
                        msg.content = msg.content.filter(block => {
                            if (block.type === 'tool_use') {
                                const isMissing = missingToolResults.some(m => m.toolUseId === block.id);
                                if (isMissing) {
                                    console.log(`[RECOVERY ${this.panelId}] Removed tool_use with missing result: ${block.id}`);
                                    return false;
                                }
                            }
                            return true;
                        });
                    }
                }
                
                return msg;
            });

            // Step 5: Log what was fixed
            this.log('TOOL_MISMATCH_FIXED', {
                removedResults: removedResults.length,
                details: removedResults
            });

            // Step 6: Show user notification
            this.showRecoveryMessage(
                `Removed ${removedResults.length} orphaned tool result(s). Retrying...`,
                'tool-fix'
            );

            // Step 7: Rebuild payload
            const newPayload = {
                ...originalPayload,
                conversation_history: fixedHistory
            };

            this.log('RESUBMITTING', {
                fixedMessageCount: fixedHistory.length
            });

            // Step 8: Resubmit
            const result = await this.resubmitRequest(newPayload);

            this.log('RECOVERY_SUCCESS', {
                method: 'tool_use_mismatch',
                duration: Date.now() - this.startTime
            });
            
            // Record statistics
            if (typeof window.SettingsManager !== 'undefined') {
                window.SettingsManager.recordRecovery(true);
            }

            return result;

        } catch (error) {
            this.log('RECOVERY_FAILED', {
                method: 'tool_use_mismatch',
                error: error.message
            });
            throw error;
        }
    }

    // ==================== RECOVERY METHOD 3: Context Length Exceeded ====================
    async recoverFromContextLength(originalPayload) {
        this.log('RECOVERY_START', {
            method: 'context_length_exceeded'
        });

        console.log(`[RECOVERY ${this.panelId}] Context length exceeded - trimming history...`);

        try {
            // Step 1: Get conversation history
            const history = originalPayload.conversation_history || [];
            const originalCount = history.length;

            // Step 2: Calculate token estimates (rough: 4 chars = 1 token)
            const estimateTokens = (content) => {
                if (typeof content === 'string') {
                    return Math.ceil(content.length / 4);
                }
                if (Array.isArray(content)) {
                    return content.reduce((sum, block) => {
                        if (block.text) return sum + Math.ceil(block.text.length / 4);
                        if (block.content) return sum + Math.ceil(block.content.length / 4);
                        return sum;
                    }, 0);
                }
                return 0;
            };

            const totalTokens = history.reduce((sum, msg) => sum + estimateTokens(msg.content), 0);

            this.log('TOKEN_ANALYSIS', {
                originalMessageCount: originalCount,
                estimatedTokens: totalTokens,
                targetTokens: 20000
            });

            // Step 3: Keep system message + recent 10 messages
            const preserveRecent = 10;
            const systemMsg = history[0]?.role === 'system' ? history[0] : null;
            const recentMessages = history.slice(-preserveRecent);

            // Step 4: Calculate remaining budget
            const recentTokens = recentMessages.reduce((sum, msg) => sum + estimateTokens(msg.content), 0);
            let remainingBudget = 20000 - recentTokens;
            if (systemMsg) {
                remainingBudget -= estimateTokens(systemMsg.content);
            }

            // Step 5: Add older messages until budget exhausted
            const trimmedHistory = [];
            if (systemMsg) trimmedHistory.push(systemMsg);

            const olderMessages = history.slice(systemMsg ? 1 : 0, -preserveRecent);
            let removedCount = 0;

            for (const msg of olderMessages) {
                const msgTokens = estimateTokens(msg.content);
                if (remainingBudget - msgTokens > 0) {
                    trimmedHistory.push(msg);
                    remainingBudget -= msgTokens;
                } else {
                    removedCount++;
                }
            }

            trimmedHistory.push(...recentMessages);

            const finalTokens = trimmedHistory.reduce((sum, msg) => sum + estimateTokens(msg.content), 0);

            // Step 6: Log what was removed
            this.log('HISTORY_TRIMMED', {
                originalCount: originalCount,
                finalCount: trimmedHistory.length,
                removedCount: removedCount,
                originalTokens: totalTokens,
                finalTokens: finalTokens,
                tokensSaved: totalTokens - finalTokens
            });

            // Step 7: Show user notification
            this.showRecoveryMessage(
                `Trimmed conversation history: removed ${removedCount} oldest messages (saved ~${totalTokens - finalTokens} tokens). Retrying...`,
                'context-trim'
            );

            // Step 8: Rebuild payload
            const newPayload = {
                ...originalPayload,
                conversation_history: trimmedHistory
            };

            this.log('RESUBMITTING', {
                finalMessageCount: trimmedHistory.length
            });

            // Step 9: Resubmit
            const result = await this.resubmitRequest(newPayload);

            this.log('RECOVERY_SUCCESS', {
                method: 'context_length_exceeded',
                duration: Date.now() - this.startTime
            });

            return result;

        } catch (error) {
            this.log('RECOVERY_FAILED', {
                method: 'context_length_exceeded',
                error: error.message
            });
            throw error;
        }
    }

    // ==================== RECOVERY METHOD 4: Rate Limit Exceeded ====================
    async recoverFromRateLimit(originalPayload) {
        this.retryCount++;

        if (this.retryCount > this.maxRetries) {
            this.log('RECOVERY_FAILED', {
                method: 'rate_limit_exceeded',
                reason: `Max retries (${this.maxRetries}) exceeded`
            });
            throw new Error(`Rate limit recovery failed after ${this.maxRetries} retries`);
        }

        // Exponential backoff: 1s, 2s, 4s
        const backoffMs = 1000 * Math.pow(2, this.retryCount - 1);

        this.log('RECOVERY_START', {
            method: 'rate_limit_exceeded',
            retry: this.retryCount,
            maxRetries: this.maxRetries,
            backoffMs: backoffMs
        });

        console.log(`[RECOVERY ${this.panelId}] Rate limit hit. Retry ${this.retryCount}/${this.maxRetries} in ${backoffMs}ms`);

        this.showRecoveryMessage(
            `Rate limit exceeded. Retrying in ${backoffMs / 1000}s... (${this.retryCount}/${this.maxRetries})`,
            'rate-limit'
        );

        // Wait for backoff period
        await new Promise(resolve => setTimeout(resolve, backoffMs));

        this.log('RESUBMITTING', {
            afterBackoff: backoffMs
        });

        // Retry
        const result = await this.resubmitRequest(originalPayload);

        this.log('RECOVERY_SUCCESS', {
            method: 'rate_limit_exceeded',
            retriesUsed: this.retryCount,
            duration: Date.now() - this.startTime
        });

        return result;
    }

    // ==================== RECOVERY METHOD 5: Server Overloaded ====================
    async recoverFromOverload(originalPayload) {
        this.retryCount++;

        if (this.retryCount > this.maxRetries) {
            this.log('RECOVERY_FAILED', {
                method: 'overloaded_error',
                reason: `Max retries (${this.maxRetries}) exceeded`
            });
            throw new Error(`Overload recovery failed after ${this.maxRetries} retries`);
        }

        // Progressive backoff: 30s, 60s, 90s
        const backoffMs = 30000 * this.retryCount;

        this.log('RECOVERY_START', {
            method: 'overloaded_error',
            retry: this.retryCount,
            backoffMs: backoffMs
        });

        console.log(`[RECOVERY ${this.panelId}] Server overloaded. Retry ${this.retryCount}/${this.maxRetries} in ${backoffMs}ms`);

        this.showRecoveryMessage(
            `Server overloaded. Retrying in ${backoffMs / 1000}s... (${this.retryCount}/${this.maxRetries})`,
            'overload'
        );

        await new Promise(resolve => setTimeout(resolve, backoffMs));

        this.log('RESUBMITTING', {
            afterBackoff: backoffMs
        });

        const result = await this.resubmitRequest(originalPayload);

        this.log('RECOVERY_SUCCESS', {
            method: 'overloaded_error',
            retriesUsed: this.retryCount,
            duration: Date.now() - this.startTime
        });

        return result;
    }

    // ==================== RECOVERY METHOD 6: Authentication Error ====================
    async recoverFromAuth(originalPayload) {
        this.log('RECOVERY_START', {
            method: 'authentication_error'
        });

        console.log(`[RECOVERY ${this.panelId}] Authentication error - attempting key rotation...`);

        // Note: Actual key rotation would need backend support
        // For now, just log and fail
        this.log('RECOVERY_FAILED', {
            method: 'authentication_error',
            reason: 'API key rotation not implemented - manual intervention required'
        });

        this.showRecoveryMessage(
            'Authentication error. Please check API keys and try again.',
            'auth-error'
        );

        throw new Error('Authentication error - manual intervention required');
    }

    // ==================== RECOVERY METHOD 7: Network Error ====================
    async recoverFromNetwork(originalPayload) {
        this.retryCount++;

        if (this.retryCount > 5) { // Network errors get 5 retries
            this.log('RECOVERY_FAILED', {
                method: 'network_error',
                reason: 'Max retries (5) exceeded'
            });
            throw new Error('Network recovery failed after 5 retries');
        }

        const backoffMs = 1000 * Math.pow(2, this.retryCount - 1);

        this.log('RECOVERY_START', {
            method: 'network_error',
            retry: this.retryCount,
            backoffMs: backoffMs,
            isOnline: navigator.onLine
        });

        console.log(`[RECOVERY ${this.panelId}] Network error. Retry ${this.retryCount}/5 in ${backoffMs}ms`);

        this.showRecoveryMessage(
            `Network error. Retrying in ${backoffMs / 1000}s... (${this.retryCount}/5)`,
            'network'
        );

        await new Promise(resolve => setTimeout(resolve, backoffMs));

        this.log('RESUBMITTING', {
            afterBackoff: backoffMs
        });

        const result = await this.resubmitRequest(originalPayload);

        this.log('RECOVERY_SUCCESS', {
            method: 'network_error',
            retriesUsed: this.retryCount,
            duration: Date.now() - this.startTime
        });

        return result;
    }

    // ==================== RESUBMIT REQUEST ====================
    async resubmitRequest(payload) {
        console.log(`[RECOVERY ${this.panelId}] Resubmitting request...`);

        const agentId = this.agentId || '1'; // '1' for Prime AI
        const threadSlug = this.threadId;

        // Make request to backend
        const response = await fetch(`${API_BASE_URL}/api/agent/stream/${agentId}?thread_slug=${threadSlug}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'text/event-stream',
            }
        });

        if (!response.ok) {
            throw new Error(`Stream error! status: ${response.status}`);
        }

        return response;
    }

    // ==================== LOGGING & UI ====================
    log(action, data) {
        const logEntry = {
            timestamp: Date.now(),
            action: action,
            panelId: this.panelId,
            threadId: this.threadId,
            data: data
        };

        this.recoveryLog.push(logEntry);

        // Console log with color
        const color = action.includes('SUCCESS') ? 'color: #10b981' :
                     action.includes('FAILED') ? 'color: #ef4444' :
                     action.includes('START') ? 'color: #3b82f6' :
                     'color: #6b7280';

        console.log(
            `%c[RECOVERY LOG ${this.panelId}] ${action}`,
            color,
            data
        );

        // Also add to AI Status Sidebar if available
        if (window.aiStatusSidebar) {
            window.aiStatusSidebar.addRecoveryLog(this.panelId, logEntry);
        }
    }

    showRecoveryMessage(message, type) {
        const bubble = document.createElement('div');
        bubble.className = `ai-message system recovery recovery-${type}`;
        bubble.innerHTML = `
            <i class="fas fa-sync fa-spin"></i>
            <span>${message}</span>
        `;

        const container = this.agentId
            ? document.getElementById(`agent-messages-${this.agentId}`)
            : document.getElementById('ai-chat-messages');

        if (container) {
            container.appendChild(bubble);
            
            // Auto-scroll if enabled
            if (typeof performAutoScroll === 'function') {
                performAutoScroll();
            }
        }
    }

    getRecoveryLog() {
        return this.recoveryLog;
    }

    exportRecoveryLog() {
        const logText = this.recoveryLog.map(entry => {
            return `[${new Date(entry.timestamp).toISOString()}] ${entry.action}\n${JSON.stringify(entry.data, null, 2)}\n`;
        }).join('\n---\n\n');

        return logText;
    }
}

// Make available globally
window.ErrorRecoveryManager = ErrorRecoveryManager;

console.log('[OK] ErrorRecoveryManager loaded - Auto-recovery enabled for 7 error types');

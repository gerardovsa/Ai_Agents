// ==================== AI CHAT PANEL ====================
// Use global API_BASE_URL from window scope (declared in HTML)
// No need to redeclare - causes "already declared" error

// Auto-scroll state
let autoScrollEnabled = true;

// AI streaming control - AbortController for stopping mid-request
let currentStreamController = null;
let isStreaming = false;

// Message visibility state tracking (Prime chat)
// Combined view modes:
// 1. 'all-collapsed': Show all - tools collapsed
// 2. 'all-expanded': Show all - expand all
// 3. 'ai-collapsed': Show AI only - collapsed tools
// 4. 'ai-expanded': Show AI only - expanded tools
// 5. 'ai-user': Show AI and user - no tools/no tool results
let primeViewMode = 'all-expanded';

// Layout constants - centralized magic numbers
const LAYOUT_CONSTANTS = {
    SCROLL_CLEARANCE: 50,      // Extra pixels for comfortable reading
    PADDING_BUFFER: 16,        // Space between input and last message
    SCROLL_THRESHOLD: 100,     // Distance from bottom to disable auto-scroll
    AUTO_SCROLL_DELAY: 50,     // Wait for DOM render before scrolling
    SCROLL_DEBOUNCE: 50,       // Debounce scroll detection (reduced from 150)
    BLUR_DELAY: 200,           // Wait before removing padding on blur
    MAX_INPUT_HEIGHT: 300      // Max textarea height before scroll
};

// Perform auto-scroll with extra clearance
function performAutoScroll() {
    if (!autoScrollEnabled) return;

    const messagesContainer = document.querySelector('.ai-chat-messages');
    if (!messagesContainer) return;

    // Scroll to bottom + extra clearance for comfortable reading
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight + LAYOUT_CONSTANTS.SCROLL_CLEARANCE;
    }, LAYOUT_CONSTANTS.AUTO_SCROLL_DELAY);
}

// Toggle auto-scroll functionality
function toggleAutoScroll() {
    autoScrollEnabled = !autoScrollEnabled;
    const btn = document.getElementById('ai-chat-autoscroll-btn');

    if (autoScrollEnabled) {
        btn?.classList.add('active');
        btn?.setAttribute('title', 'Auto-scroll enabled - Click to disable');
        performAutoScroll();
    } else {
        btn?.classList.remove('active');
        btn?.setAttribute('title', 'Auto-scroll disabled - Click to enable');
    }
}

function updateMessagesBottomPadding() {
    performAutoScroll();
}

function resetMessagesBottomPadding() {
    // Flex layout naturally gives messages more space when input collapses
}

function initChatPanel() {
    const closeBtn = document.getElementById('chat-close-btn');
    const sendBtn = document.getElementById('ai-chat-send-btn');
    const input = document.getElementById('ai-chat-input');
    const panel = document.getElementById('ai-chat-panel');
    const attachBtn = document.getElementById('ai-chat-attach-btn');
    const fileInput = document.getElementById('ai-chat-file-input');
    const attachedFilesContainer = document.getElementById('ai-chat-attached-files');

    // File attachment state
    let attachedFiles = [];

    // Stop button already exists in HTML, just attach event listener
    const stopBtn = document.getElementById('ai-chat-stop-btn');
    if (stopBtn) {
        stopBtn.addEventListener('click', stopAIStream);
    }

    // Initialize textarea height
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, LAYOUT_CONSTANTS.MAX_INPUT_HEIGHT) + 'px';

    // Initialize without padding (messages go to bottom)
    const welcomeContainer = document.getElementById('prime-welcome-container');
    const welcomeVisible = welcomeContainer && !welcomeContainer.style.display.includes('none');
    if (!welcomeVisible) {
        resetMessagesBottomPadding();
    }

    // Detect user scrolling up to disable auto-scroll
    const messagesContainer = document.querySelector('.ai-chat-messages');
    if (messagesContainer) {
        let scrollTimeout;
        let lastScrollTop = messagesContainer.scrollTop;

        messagesContainer.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);

            scrollTimeout = setTimeout(() => {
                const currentScrollTop = messagesContainer.scrollTop;
                const maxScroll = messagesContainer.scrollHeight - messagesContainer.clientHeight;
                const distanceFromBottom = maxScroll - currentScrollTop;

                if (currentScrollTop < lastScrollTop && distanceFromBottom > LAYOUT_CONSTANTS.SCROLL_THRESHOLD && autoScrollEnabled) {
                    autoScrollEnabled = false;
                    const btn = document.getElementById('ai-chat-autoscroll-btn');
                    btn?.classList.remove('active');
                    btn?.setAttribute('title', 'Auto-scroll disabled - Click to enable');
                }

                lastScrollTop = currentScrollTop;
            }, LAYOUT_CONSTANTS.SCROLL_DEBOUNCE);
        });
    }

    closeBtn.addEventListener('click', toggleChat);
    sendBtn.addEventListener('click', sendChatMessage);

    // ==================== 4-STATE SLIDING INPUT SYSTEM ====================
    const inputContainer = document.querySelector('.ai-chat-input-container');
    const messagesArea = document.querySelector('.ai-chat-messages');
    let isExpanded = false;

    function expandInputArea() {
        if (isExpanded) return;

        isExpanded = true;
        inputContainer?.classList.add('expanded');

        // ALWAYS scroll to bottom when expanding (compensate for lost message space)
        // This is separate from auto-scroll toggle - expansion changes viewport
        setTimeout(() => {
            const messagesContainer = document.querySelector('.ai-chat-messages');
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight + LAYOUT_CONSTANTS.SCROLL_CLEARANCE;
            }
        }, 100);

        input?.focus();

        console.log('[STATE 4] Input area expanded - flex layout handles space');
    }

    function collapseInputArea() {
        if (!isExpanded) return;

        isExpanded = false;
        inputContainer?.classList.remove('expanded');

        console.log('[STATE 1] Input area collapsed - messages naturally expand');
    }

    inputContainer.addEventListener('click', (e) => {
        if (!isExpanded && e.target === inputContainer) {
            expandInputArea();
        }
    });

    input.addEventListener('focus', () => {
        expandInputArea();
    });

    input.addEventListener('blur', () => {
        setTimeout(() => {
            if (document.activeElement !== input && input.value.trim() === '') {
                collapseInputArea();
            }
        }, LAYOUT_CONSTANTS.BLUR_DELAY);
    });

    // File attachment button click
    attachBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFileSelection(e.target.files);
    });

    // Drag and drop handlers
    input.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        input.classList.add('drag-over');
    });

    input.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        input.classList.remove('drag-over');
    });

    input.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        input.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files);
        }
    });

    // Auto-expand textarea as text is added
    input.addEventListener('input', (e) => {
        input.style.height = 'auto';

        const newHeight = Math.min(input.scrollHeight, LAYOUT_CONSTANTS.MAX_INPUT_HEIGHT);
        input.style.height = newHeight + 'px';

        if (inputContainer?.classList.contains('expanded') && autoScrollEnabled) {
            setTimeout(() => performAutoScroll(), 0);
        }
    });

    // Handle paste events
    input.addEventListener('paste', (e) => {
        setTimeout(() => {
            input.style.height = 'auto';
            const newHeight = Math.min(input.scrollHeight, LAYOUT_CONSTANTS.MAX_INPUT_HEIGHT);
            input.style.height = newHeight + 'px';
        }, 0);
    });

    function handleFileSelection(files) {
        for (let file of files) {
            const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
            if (!validTypes.includes(file.type)) {
                showNotification(`Invalid file type: ${file.name}. Only PDF and images are supported.`, 'error');
                continue;
            }

            const maxSize = file.type === 'application/pdf' ? 32 * 1024 * 1024 : 5 * 1024 * 1024;
            if (file.size > maxSize) {
                showNotification(`File too large: ${file.name}. Max size: ${maxSize / 1024 / 1024}MB`, 'error');
                continue;
            }

            attachedFiles.push(file);
        }

        updateAttachedFilesUI();
        fileInput.value = '';
    }

    function updateAttachedFilesUI() {
        attachedFilesContainer.innerHTML = '';

        attachedFiles.forEach((file, index) => {
            const chip = document.createElement('div');
            chip.className = 'ai-chat-file-chip';

            const icon = file.type === 'application/pdf' ? 'fa-file-pdf' : 'fa-image';
            const size = (file.size / 1024).toFixed(1);

            chip.innerHTML = `
                <i class="fas ${icon}"></i>
                <span>${file.name} (${size}KB)</span>
                <button class="ai-chat-file-chip-remove" data-index="${index}">×</button>
            `;

            chip.querySelector('.ai-chat-file-chip-remove').addEventListener('click', () => {
                attachedFiles.splice(index, 1);
                updateAttachedFilesUI();
            });

            attachedFilesContainer.appendChild(chip);
        });

        const inputContainer = document.querySelector('.ai-chat-input-container');
        if (inputContainer?.classList.contains('active')) {
            setTimeout(() => updateMessagesBottomPadding(), 0);
        }
    }

    window.chatAttachedFiles = attachedFiles;
    window.clearChatAttachedFiles = () => {
        // Use splice to clear array without breaking reference
        attachedFiles.splice(0, attachedFiles.length);
        updateAttachedFilesUI();

        const inputContainer = document.querySelector('.ai-chat-input-container');
        if (inputContainer?.classList.contains('active')) {
            setTimeout(() => updateMessagesBottomPadding(), 0);
        }
    };

    // Enter to send (Shift+Enter for new line)
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });

    // Resizable chat panel
    let isResizing = false;
    let startX = 0;
    let startWidth = 0;

    const savedWidth = localStorage.getItem('ai_chat_panel_width');
    if (savedWidth) {
        document.documentElement.style.setProperty('--chat-width', savedWidth);
    }

    panel.addEventListener('mousedown', (e) => {
        const rect = panel.getBoundingClientRect();
        if (e.clientX - rect.left <= 6) {
            isResizing = true;
            startX = e.clientX;
            startWidth = panel.offsetWidth;
            e.preventDefault();
            document.body.style.cursor = 'ew-resize';
        }
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;

        const deltaX = startX - e.clientX;
        const newWidth = startWidth + deltaX;

        if (newWidth >= 300 && newWidth <= 800) {
            document.documentElement.style.setProperty('--chat-width', newWidth + 'px');
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = 'default';

            const currentWidth = getComputedStyle(document.documentElement)
                .getPropertyValue('--chat-width').trim();
            localStorage.setItem('ai_chat_panel_width', currentWidth);
        }
    });

    initInputResizeObserver();
}

// Stop AI streaming mid-request
function stopAIStream() {
    if (currentStreamController) {
        console.log('🛑 User requested stop - aborting stream');
        currentStreamController.abort();
        currentStreamController = null;
        isStreaming = false;
        
        // Hide stop button, show send button
        const stopBtn = document.getElementById('ai-chat-stop-btn');
        const sendBtn = document.getElementById('ai-chat-send-btn');
        if (stopBtn) stopBtn.style.display = 'none';
        if (sendBtn) sendBtn.style.display = 'inline-flex';
        
        // Remove thinking indicator
        removeThinkingIndicator();
        if (typeof window.hidePrimeProcessingIndicator === 'function') {
            window.hidePrimeProcessingIndicator();
        }
        
        // Add system message indicating interruption
        addChatMessage('system', '⏸️ Response stopped by user', false, false);
    }
}

// Helper function to gather user context
async function gatherUserContext() {
    // Gather browser context
    let browserContext = {};
    try {
        browserContext = await BrowserContext.getContext();
        console.log('[OK] Browser context gathered');
    } catch (error) {
        console.warn('[WARN] Could not gather browser context:', error);
    }

    // Load user preferences and memories
    let userContext = {
        nickname: '',
        communication_style: 'professional',
        detail_level: 'standard',
        location: '',
        timezone: '',
        country: '',
        auth_platform: null,
        google_authenticated: false,
        microsoft_authenticated: false,
        preferred_tools: [],
        custom_preferences: [],
        memories: [],
        browser: browserContext
    };

    try {
        const prefsResponse = await fetch(`${window.API_BASE_URL}/api/user/preferences`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });

        if (prefsResponse.ok) {
            const prefsData = await prefsResponse.json();
            const data = prefsData.data || prefsData;

            const authPlatform = data.auth_platform || null;
            const googleConnected = data.google_oauth_connected || false;
            const microsoftConnected = data.microsoft_oauth_connected || false;

            userContext = {
                nickname: data.nickname || '',
                communication_style: data.communication_style || 'professional',
                detail_level: data.detail_level || 'standard',
                location: data.use_manual_location ? data.manual_location_override : data.detected_city,
                timezone: data.use_manual_timezone ? data.manual_timezone_override : data.detected_timezone,
                country: data.detected_country || '',
                auth_platform: authPlatform,
                google_authenticated: authPlatform === 'google' || googleConnected,
                microsoft_authenticated: authPlatform === 'microsoft' || microsoftConnected,
                preferred_tools: data.preferred_tools ? (typeof data.preferred_tools === 'string' ? JSON.parse(data.preferred_tools) : data.preferred_tools) : [],
                custom_preferences: data.custom_preferences ? (typeof data.custom_preferences === 'string' ? JSON.parse(data.custom_preferences) : data.custom_preferences) : [],
                memories: data.ai_memories ? (typeof data.ai_memories === 'string' ? JSON.parse(data.ai_memories) : data.ai_memories) : [],
                browser: browserContext
            };
        }
    } catch (error) {
        console.warn('[WARN] Could not load user preferences:', error);
    }

    return userContext;
}

function initInputResizeObserver() {
    const inputContainer = document.querySelector('.ai-chat-input-container');
    const messagesContainer = document.querySelector('.ai-chat-messages');

    if (!inputContainer || !messagesContainer) {
        console.warn('[RESIZE OBSERVER] Input or messages container not found');
        return;
    }

    const resizeObserver = new ResizeObserver(entries => {
        if (inputContainer.classList.contains('expanded') && autoScrollEnabled) {
            performAutoScroll();
        }
    });

    resizeObserver.observe(inputContainer);
    console.log('[RESIZE OBSERVER] Watching .ai-chat-input-container for size changes (flex layout)');
}

function toggleChat() {
    const panel = document.getElementById('ai-chat-panel');
    const wrapper = document.getElementById('main-content-wrapper');
    AppState.chatOpen = !AppState.chatOpen;

    if (AppState.chatOpen) {
        wrapper.classList.remove('chat-collapsed');
        panel.style.display = 'flex';
    } else {
        wrapper.classList.add('chat-collapsed');
        panel.style.display = 'none';
    }

    console.log('💬 Chat toggled:', AppState.chatOpen ? 'Open' : 'Collapsed');
}

// ==================== PLATFORM STATUS ====================
async function loadPlatformStatus() {
    const grid = document.getElementById('platform-status-grid');

    grid.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Loading platforms...</div>';

    if (!AppState.isConnected) {
        grid.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Backend disconnected</div>';
        return;
    }

    try {
        const response = await fetch(`${window.API_BASE_URL}/api/agent/tools`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        const platformMap = new Map();

        if (data.tools && Array.isArray(data.tools)) {
            data.tools.forEach(tool => {
                const platform = tool.platform || 'Unknown';
                if (!platformMap.has(platform)) {
                    platformMap.set(platform, {
                        name: platform,
                        status: 'connected',
                        tools: [],
                        icon: getPlatformIcon(platform),
                        color: getPlatformColor(platform)
                    });
                }
                platformMap.get(platform).tools.push(tool.name);
            });
        }

        const platforms = Array.from(platformMap.values());

        if (platforms.length === 0) {
            grid.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">No platforms configured</div>';
            return;
        }

        grid.innerHTML = platforms.map(p => `
            <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg-tertiary); border-radius: 6px; margin-bottom: 8px;">
                <div style="width: 40px; height: 40px; background: ${p.color}; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: white;">
                    <i class="fab ${p.icon}"></i>
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: 600;">${p.name}</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">${p.tools.length} tools available</div>
                </div>
                <div style="width: 8px; height: 8px; background: var(--accent-success); border-radius: 50%;"></div>
            </div>
        `).join('');

        console.log(`✅ Loaded ${platforms.length} platforms with ${data.tools.length} tools`);

    } catch (error) {
        console.error('❌ Failed to load platforms:', error);
        grid.innerHTML = `
            <div style="padding: 20px; text-align: center;">
                <div style="color: var(--accent-error); margin-bottom: 8px;">
                    <i class="fas fa-exclamation-triangle"></i> Failed to load platforms
                </div>
                <div style="font-size: 12px; color: var(--text-secondary);">${error.message}</div>
            </div>
        `;
    }
}

function getPlatformIcon(platform) {
    const iconMap = {
        'slack': 'fa-slack',
        'woocommerce': 'fa-shopping-cart',
        'google': 'fa-google',
        'stripe': 'fa-stripe',
        'github': 'fa-github',
        'database': 'fa-database',
        'analytics': 'fa-chart-line',
        'email': 'fa-envelope',
        'shopify': 'fa-shopping-bag',
        'supabase': 'fa-database'
    };

    const lowerPlatform = platform.toLowerCase();
    for (const [key, icon] of Object.entries(iconMap)) {
        if (lowerPlatform.includes(key)) return icon;
    }
    return 'fa-cube';
}

function getPlatformColor(platform) {
    const colorMap = {
        'slack': '#4a154b',
        'woocommerce': '#7f54b3',
        'google': '#4285f4',
        'stripe': '#635bff',
        'github': '#58a6ff',
        'supabase': '#3fb950',
        'shopify': '#96bf48',
        'database': '#2c3e50',
        'analytics': '#ff6b6b'
    };

    const lowerPlatform = platform.toLowerCase();
    for (const [key, color] of Object.entries(colorMap)) {
        if (lowerPlatform.includes(key)) return color;
    }
    return '#6c5ce7';
}

// ==================== CHAT MESSAGE SENDING ====================
async function sendChatMessage() {
    const input = document.getElementById('ai-chat-input');
    const message = input.value.trim();

    if (!message) {
        console.warn('[WARN] Message is empty, not sending');
        return;
    }

    // CRITICAL: Verify MessageStore is loaded
    if (!window.MessageStore) {
        console.error('[ERROR] MessageStore not loaded! Cannot send message.');
        showNotification('System error: MessageStore not loaded', 'error');
        return;
    }

    // Initialize stream timeout ID for cleanup
    let streamTimeoutId = null;

    // Check for attached files
    const hasFiles = window.chatAttachedFiles && window.chatAttachedFiles.length > 0;
    console.log(`[ATTACH] File check: hasFiles=${hasFiles}, count=${window.chatAttachedFiles?.length || 0}`);
    if (hasFiles) {
        console.log('[ATTACH] Files detected:', window.chatAttachedFiles.map(f => f.name));
    }

    if (!AppState.isConnected) {
        console.warn('[WARN] Connection check reported disconnected, but trying anyway...');
    }

    // Clear input immediately
    input.value = '';

    // Reset textarea height
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 300) + 'px';

    // Get or create thread_slug
    let currentThreadId;
    if (window.ThreadManager && window.ThreadManager.currentThreadId) {
        currentThreadId = window.ThreadManager.currentThreadId;
        console.log(`✅ [THREAD] Using loaded thread: ${currentThreadId}`);
    } else {
        currentThreadId = String(Date.now());
        console.log(`✅ [THREAD] Generated new thread_slug for Prime: ${currentThreadId}`);
    }

    // Build message content with file attachments if present
    let messageContent = message;
    if (hasFiles) {
        const fileList = window.chatAttachedFiles.map(f => f.name).join(', ');
        messageContent = `${message}\n\n[ATTACH] Attached: ${fileList}`;
    }

    // Add user message to UI
    const userMessageDiv = UnifiedMessageRenderer.render(
        '#ai-chat-messages',
        'user',
        messageContent,
        {
            isThinking: false,
            scrollToBottom: autoScrollEnabled,
            threadId: currentThreadId,
            syncToBackend: true,  // ✅ FIX: Save user message to database
            messageId: null  // User-typed message, ID assigned after backend sync
        }
    );

    if (!userMessageDiv) {
        console.error('[Prime] Failed to render user message');
        return;
    }

    console.log(`✅ [MessageStore] User message added via UnifiedMessageRenderer`);

    const sessionId = currentThreadId;

    // Show processing indicator
    if (typeof window.showPrimeProcessingIndicator === 'function') {
        window.showPrimeProcessingIndicator();
    }

    // Update status indicator
    if (typeof AgentStatusIndicator !== 'undefined') {
        AgentStatusIndicator.update('thinking', null);
    }

    const startTime = Date.now();

    try {
        // Check if we need to use file upload endpoint
        if (hasFiles) {
            console.log('[ATTACH] Sending message with file attachments...');
            await sendChatMessageWithFiles(message, sessionId, startTime);
            return;
        }

        console.log('🚀 Preparing chat request with tool support...');
        console.log(`[🔧] ${ToolManager.availableTools.length} tools available for AI use`);

        // ============================================
        // ✅ DATABASE AS SOURCE OF TRUTH: Don't send conversation_history
        // Backend will load it from database
        // ============================================
        console.log('📦 [DATABASE] Backend will load conversation from database (not sending history)');

        const userContext = await gatherUserContext();

        // ✅ SIMPLIFIED REQUEST BODY: No conversation_history
        const requestBody = {
            message: message,
            session_id: currentThreadId,
            thread_id: currentThreadId,
            thread_slug: currentThreadId,
            // ❌ REMOVED: conversation_history: conversationHistory,
            user_context: userContext,
            context: {
                tab: AppState.currentTab,
                platform: 'business_ai_platform',
                tools_enabled: true,
                available_tools: ToolManager.availableTools.length,
                google_auth: AuthManager.isAuthenticated ? AuthManager.getAccessToken() : null
            },
            preferences: {
                use_tools: true,
                verbose_tool_output: true,
                streaming: true
            }
        };

        console.log('✅ [REQUEST] Sending ONLY current message (backend will load conversation from DB)');

        const agentId = '1';

        // Step 1: Start the agent
        console.log('🚀 Starting agent processing...');
        const startResponse = await fetch(`${window.API_BASE_URL}/api/agent/agent/${agentId}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        if (!startResponse.ok) {
            throw new Error(`HTTP error! status: ${startResponse.status}`);
        }

        const startData = await startResponse.json();
        console.log('[OK] Agent started:', startData);

        // ✅ DATABASE AS SOURCE OF TRUTH: Accept backend's conversation
        // Backend wraps response in { success: true, data: {...} }
        const responseData = startData.data || startData;
        const conversation = responseData.conversation;

        if (conversation && Array.isArray(conversation)) {
            console.log(`✅ [SYNC] Backend returned ${conversation.length} messages (authoritative)`);
            console.log(`📥 [SYNC] Replacing frontend state with backend conversation`);

            // Replace MessageStore with backend's conversation
            if (window.MessageStore) {
                // Clear current thread messages
                window.MessageStore.clearThread(currentThreadId);

                // Add all messages from backend
                for (const msg of conversation) {
                    await window.MessageStore.addMessage(currentThreadId, msg, {
                        checkDuplicates: false,
                        silent: true
                    });
                }
                console.log(`✅ [MessageStore] Synced ${conversation.length} messages from backend`);
            }

            // Also update AppState for backward compatibility
            AppState.chatMessages = conversation;
        } else {
            console.warn('⚠️ Backend did not return conversation in start response');
            console.warn('Response structure:', { hasData: !!startData.data, hasConversation: !!conversation });
        }

        // Step 2: Connect to SSE stream
        console.log('🌊 Connecting to SSE stream...');

        // Get prompt injection parameters
        let promptParams = '';
        if (typeof window.getSelectedPrompts === 'function') {
            const selectedPrompts = window.getSelectedPrompts();
            if (selectedPrompts && selectedPrompts.length > 0) {
                const quickActions = selectedPrompts.filter(p => p.type === 'quick_action').map(p => p.name);
                const libraryPrompts = selectedPrompts.filter(p => p.type === 'full_prompt').map(p => p.name);

                if (quickActions.length > 0) {
                    promptParams += `&quick_actions=${encodeURIComponent(quickActions.join(','))}`;
                }
                if (libraryPrompts.length > 0) {
                    promptParams += `&library_prompts=${encodeURIComponent(libraryPrompts.join(','))}`;
                }

                console.log(`[PROMPT INJECTION] Quick Actions: ${quickActions.join(', ')}`);
                console.log(`[PROMPT INJECTION] Library Prompts: ${libraryPrompts.join(', ')}`);
            }
        }

        const threadSlug = currentThreadId;
        const streamUrl = `${window.API_BASE_URL}/api/agent/stream/${agentId}?thread_slug=${threadSlug}${promptParams}`;
        console.log(`[Stream] Connecting with thread_slug: ${threadSlug}`);
        
        // Create AbortController for this stream
        currentStreamController = new AbortController();
        isStreaming = true;
        
        // Show stop button, hide send button (use flex for floating buttons)
        const stopBtn = document.getElementById('ai-chat-stop-btn');
        const sendBtn = document.getElementById('ai-chat-send-btn');
        if (stopBtn) stopBtn.style.display = 'inline-flex';
        if (sendBtn) sendBtn.style.display = 'none';
        
        // ✅ TEAM COLLABORATION FIX: Send socket ID to prevent message echo
        const headers = {};
        if (window.SynergyRealtime?.socket?.id) {
            headers['X-Socket-ID'] = window.SynergyRealtime.socket.id;
            console.log('[Stream] Adding X-Socket-ID header:', window.SynergyRealtime.socket.id);
        }
        
        const response = await fetch(streamUrl, { 
            signal: currentStreamController.signal,
            headers: headers
        });

        if (!response.ok) {
            throw new Error(`Stream error! status: ${response.status}`);
        }

        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('text/event-stream')) {
            // HANDLE STREAMING RESPONSE
            console.log('🌊 Receiving streamed response...');

            const chatMessages = document.getElementById('ai-chat-messages');
            if (!chatMessages) {
                console.error('[ERROR] Could not find ai-chat-messages element!');
                throw new Error('Chat messages container not found');
            }

            let fullResponse = '';
            let fullThinkingContent = '';
            let toolsUsed = [];
            let toolResults = [];
            let firstContentReceived = false;
            let thinkingBubble = null;
            let textBubble = null;
            let lastEventType = null;

            let threadErrorCount = 0;
            const maxThreadErrors = 10;
            let threadFailed = false;

            window._thinkingRoundCounter = 0;
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                const messages = buffer.split('\n\n');

                buffer = messages.pop() || '';

                for (const message of messages) {
                    const lines = message.split('\n');
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const jsonStr = line.substring(6).trim();
                                if (jsonStr) {
                                    const data = JSON.parse(jsonStr);

                                    if (data.type === 'thinking_block' || data.type === 'thinking') {
                                        console.log('🧠 [THINKING EVENT] Received thinking content:', data.content?.substring(0, 50) + '...');

                                        const thinkingText = data.content || data.thinking || '';
                                        if (!thinkingText || thinkingText.trim().length === 0) {
                                            console.log('[WARN] Skipping empty thinking content');
                                            continue;
                                        }

                                        updateAIStatusIndicator('thinking');

                                        if (!firstContentReceived) {
                                            removeThinkingIndicator();
                                            // Hide processing indicator when first content arrives
                                            if (typeof window.hidePrimeProcessingIndicator === 'function') {
                                                window.hidePrimeProcessingIndicator();
                                            }
                                            firstContentReceived = true;
                                            console.log('[OK] Removed bouncing dots indicator');
                                        }

                                        if (!thinkingBubble) {
                                            console.log('💭 Creating new thinking bubble...');
                                            thinkingBubble = document.createElement('div');
                                            thinkingBubble.className = 'ai-message assistant thinking-bubble';

                                            const headerDiv = document.createElement('div');
                                            headerDiv.className = 'ai-message-header';

                                            const avatar = document.createElement('div');
                                            avatar.className = 'ai-message-avatar';
                                            avatar.style.background = '#8b5cf6';
                                            avatar.innerHTML = '<i class="fa-solid fa-brain" style="color: white;"></i>';

                                            const toggleBtn = document.createElement('button');
                                            toggleBtn.className = 'ai-message-toggle';
                                            toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
                                            toggleBtn.title = 'Collapse/Expand thinking';
                                            toggleBtn.addEventListener('click', (e) => {
                                                e.stopPropagation();
                                                thinkingBubble.classList.toggle('collapsed');
                                            });

                                            headerDiv.appendChild(avatar);
                                            headerDiv.appendChild(toggleBtn);

                                            const actionsDiv = document.createElement('div');
                                            actionsDiv.className = 'ai-message-actions';

                                            const copyBtn = document.createElement('button');
                                            copyBtn.className = 'ai-message-copy-btn';
                                            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                            copyBtn.title = 'Copy thinking content';
                                            copyBtn.addEventListener('click', (e) => {
                                                e.stopPropagation();
                                                const content = thinkingBubble.querySelector('.ai-message-content').textContent;
                                                navigator.clipboard.writeText(content).then(() => {
                                                    copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                                                    setTimeout(() => {
                                                        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                                    }, 2000);
                                                });
                                            });

                                            const copyRawBtn = document.createElement('button');
                                            copyRawBtn.className = 'ai-message-copy-btn';
                                            copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
                                            copyRawBtn.title = 'Copy raw thinking';
                                            copyRawBtn.addEventListener('click', (e) => {
                                                e.stopPropagation();
                                                const content = thinkingBubble.querySelector('.ai-message-content').textContent;
                                                navigator.clipboard.writeText(content).then(() => {
                                                    copyRawBtn.innerHTML = '<i class="fas fa-check"></i>';
                                                    setTimeout(() => {
                                                        copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
                                                    }, 2000);
                                                });
                                            });

                                            const expandBtn = document.createElement('button');
                                            expandBtn.className = 'ai-message-copy-btn';
                                            expandBtn.innerHTML = '<i class="fas fa-expand-alt"></i>';
                                            expandBtn.title = 'Expand message fullscreen';
                                            expandBtn.addEventListener('click', (e) => {
                                                e.stopPropagation();
                                                if (typeof window.openMessageFullscreen === 'function') {
                                                    window.openMessageFullscreen(thinkingBubble);
                                                }
                                            });

                                            actionsDiv.appendChild(copyBtn);
                                            actionsDiv.appendChild(copyRawBtn);
                                            actionsDiv.appendChild(expandBtn);
                                            headerDiv.appendChild(actionsDiv);

                                            const contentDiv = document.createElement('div');
                                            contentDiv.className = 'ai-message-content';

                                            thinkingBubble.appendChild(headerDiv);
                                            thinkingBubble.appendChild(contentDiv);
                                            thinkingBubble.classList.add('collapsed');
                                            chatMessages.appendChild(thinkingBubble);
                                            console.log('[OK] Thinking bubble created and added');

                                            // Add fullscreen double-click handler
                                            if (typeof window.addMessageFullscreenHandler === 'function') {
                                                window.addMessageFullscreenHandler(thinkingBubble);
                                            }
                                        }

                                        lastEventType = 'thinking';

                                        const thinkingContent = thinkingBubble.querySelector('.ai-message-content');

                                        if (!thinkingBubble._fullThinkingText) {
                                            thinkingBubble._fullThinkingText = '';
                                        }

                                        // AUTO SEPARATOR: Add visual break when new thinking block starts
                                        if (data.delta_type === 'start') {
                                            if (thinkingBubble._fullThinkingText.trim()) {
                                                // New thinking block detected - add separator before it
                                                const beforeLen = thinkingBubble._fullThinkingText.length;
                                                thinkingBubble._fullThinkingText += '\n\n---\n\n';
                                                console.log('🔄 [THINKING SEPARATOR] New thinking block detected', {
                                                    beforeLength: beforeLen,
                                                    afterLength: thinkingBubble._fullThinkingText.length,
                                                    lastChars: thinkingBubble._fullThinkingText.slice(-30)
                                                });
                                            } else {
                                                console.log('🔄 [THINKING START] First thinking block, no separator needed');
                                            }
                                        }

                                        const beforeAppend = thinkingBubble._fullThinkingText.length;
                                        thinkingBubble._fullThinkingText += thinkingText;
                                        console.log('📝 [THINKING DELTA] Appended:', {
                                            deltaLength: thinkingText.length,
                                            totalLength: thinkingBubble._fullThinkingText.length,
                                            preview: thinkingText.substring(0, 50)
                                        });

                                        fullThinkingContent += thinkingText;

                                        if (window.marked) {
                                            try {
                                                const parsed = marked.parse(thinkingBubble._fullThinkingText, {
                                                    breaks: true,
                                                    gfm: true
                                                });
                                                thinkingContent.innerHTML = parsed;
                                                console.log('✅ [THINKING RENDERED] Markdown parsed, HTML length:', parsed.length);
                                            } catch (e) {
                                                console.error('[ERROR] Markdown parse error in thinking:', e);
                                                thinkingContent.innerHTML = renderBasicMarkdown(thinkingBubble._fullThinkingText);
                                            }
                                        } else {
                                            thinkingContent.innerHTML = renderBasicMarkdown(thinkingBubble._fullThinkingText);
                                        }
                                        console.log('💭 Thinking content updated, total text length:', thinkingBubble._fullThinkingText.length);

                                    } else if (data.type === 'tool_use') {
                                        if (window._twoRuleProcessors && window._twoRuleProcessors.size) {
                                            console.log('🔧 Flushing buffered content from active TwoRule processors before tool use...');
                                            for (const _p of Array.from(window._twoRuleProcessors)) {
                                                try {
                                                    if (_p && typeof _p.forceFlush === 'function') {
                                                        _p.forceFlush();
                                                    }
                                                } catch (e) {
                                                    console.warn('[WARN] Error flushing TwoRule processor:', e);
                                                }
                                            }
                                        }

                                        const toolId = data.tool_id || data.tool_use_id || data.id;
                                        console.log('⚙️ [TOOL_USE EVENT] Tool:', data.tool_name, 'ID:', toolId);

                                        updateAIStatusIndicator('tool-running');
                                        if (typeof AgentStatusIndicator !== 'undefined') {
                                            AgentStatusIndicator.update('tool-running', null);
                                        }

                                        if (!firstContentReceived) {
                                            removeThinkingIndicator();
                                            firstContentReceived = true;
                                            console.log('[OK] Removed bouncing dots indicator');
                                        }

                                        const toolBubble = document.createElement('div');
                                        toolBubble.className = 'ai-message assistant tool-bubble';
                                        toolBubble.setAttribute('data-tool-id', toolId);

                                        const headerDiv = document.createElement('div');
                                        headerDiv.className = 'ai-message-header';

                                        const avatar = document.createElement('div');
                                        avatar.className = 'ai-message-avatar';
                                        avatar.style.background = '#eab308';
                                        avatar.innerHTML = '<i class="fas fa-cog" style="color: white;"></i>';

                                        const toggleBtn = document.createElement('button');
                                        toggleBtn.className = 'ai-message-toggle';
                                        toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
                                        toggleBtn.title = 'Collapse/Expand tool details';
                                        toggleBtn.addEventListener('click', (e) => {
                                            e.stopPropagation();
                                            toolBubble.classList.toggle('collapsed');
                                        });

                                        headerDiv.appendChild(avatar);
                                        headerDiv.appendChild(toggleBtn);

                                        const actionsDiv = document.createElement('div');
                                        actionsDiv.className = 'ai-message-actions';

                                        const copyBtn = document.createElement('button');
                                        copyBtn.className = 'ai-message-copy-btn';
                                        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                        copyBtn.title = 'Copy tool content';
                                        copyBtn.addEventListener('click', (e) => {
                                            e.stopPropagation();
                                            const contentDiv = toolBubble.querySelector('.ai-message-content');
                                            const content = contentDiv ? contentDiv.textContent : JSON.stringify({
                                                tool: data.name || data.tool_name,
                                                input: data.input || data.tool_input
                                            }, null, 2);
                                            navigator.clipboard.writeText(content).then(() => {
                                                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                                                setTimeout(() => {
                                                    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                                }, 2000);
                                            });
                                        });

                                        const expandBtn = document.createElement('button');
                                        expandBtn.className = 'ai-message-copy-btn';
                                        expandBtn.innerHTML = '<i class="fas fa-expand-alt"></i>';
                                        expandBtn.title = 'Expand message fullscreen';
                                        expandBtn.addEventListener('click', (e) => {
                                            e.stopPropagation();
                                            if (typeof window.openMessageFullscreen === 'function') {
                                                window.openMessageFullscreen(toolBubble);
                                            }
                                        });

                                        actionsDiv.appendChild(copyBtn);
                                        actionsDiv.appendChild(expandBtn);
                                        headerDiv.appendChild(actionsDiv);

                                        const contentDiv = document.createElement('div');
                                        contentDiv.className = 'ai-message-content';
                                        contentDiv.innerHTML = `
                                            <div style="margin-bottom: 8px;"><strong>Tool:</strong> ${data.name || data.tool_name}</div>
                                            <pre>${JSON.stringify(data.input || data.tool_input, null, 2)}</pre>
                                        `;

                                        toolBubble.appendChild(headerDiv);
                                        toolBubble.appendChild(contentDiv);
                                        toolBubble.classList.add('collapsed');
                                        chatMessages.appendChild(toolBubble);

                                        // Add fullscreen double-click handler
                                        if (typeof window.addMessageFullscreenHandler === 'function') {
                                            window.addMessageFullscreenHandler(toolBubble);
                                        }

                                        lastEventType = 'tool_use';

                                        toolsUsed.push({
                                            name: data.name || data.tool_name,
                                            input: data.input || data.tool_input,
                                            id: toolId
                                        });

                                    } else if (data.type === 'tool_input_complete') {
                                        console.log('⚙️ [TOOL_INPUT_COMPLETE EVENT] Updating tool bubble with complete input');

                                        const toolBubble = chatMessages.querySelector(`[data-tool-id="${data.tool_id}"]`);
                                        if (toolBubble) {
                                            const contentDiv = toolBubble.querySelector('.ai-message-content');
                                            if (contentDiv) {
                                                contentDiv.innerHTML = `
                                                    <div style="margin-bottom: 8px;"><strong>Tool:</strong> ${data.tool_name}</div>
                                                    <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 6px; overflow-x: auto;">${JSON.stringify(data.tool_input, null, 2)}</pre>
                                                `;
                                                console.log('[OK] Updated tool bubble content with complete input');
                                            }
                                        } else {
                                            console.warn('[WARN] Tool bubble not found for ID:', data.tool_id);
                                        }

                                    } else if (data.type === 'content_delta') {
                                        console.log('💬 [CONTENT_DELTA EVENT] Received text chunk:', data.text?.substring(0, 50) + '...');

                                        updateAIStatusIndicator('writing');

                                        if (!firstContentReceived) {
                                            removeThinkingIndicator();
                                            firstContentReceived = true;
                                            console.log('[OK] Removed bouncing dots indicator');
                                        }

                                        if (lastEventType !== 'content_delta' && lastEventType !== null) {
                                            if (textBubble) {
                                                console.log('💬 Creating new text bubble (switching from', lastEventType, 'to content_delta)');
                                                const oldBubble = textBubble;
                                                textBubble = null;
                                                fullResponse = '';
                                                if (oldBubble && oldBubble._twoRuleProcessor) {
                                                    try {
                                                        if (typeof oldBubble._twoRuleProcessor.forceFlush === 'function') {
                                                            oldBubble._twoRuleProcessor.forceFlush();
                                                        }
                                                    } catch (e) {
                                                        console.warn('[WARN] Error flushing bubble TwoRule processor during switch:', e);
                                                    }
                                                    if (window._twoRuleProcessors) {
                                                        window._twoRuleProcessors.delete(oldBubble._twoRuleProcessor);
                                                    }
                                                    oldBubble._twoRuleProcessor = null;
                                                }
                                            }
                                        }

                                        fullResponse += data.text;

                                        lastEventType = 'content_delta';

                                        if (!textBubble) {
                                            console.log('💬 Creating new text bubble...');
                                            textBubble = document.createElement('div');
                                            textBubble.className = 'ai-message assistant text-bubble';

                                            const headerDiv = document.createElement('div');
                                            headerDiv.className = 'ai-message-header';

                                            const avatar = document.createElement('div');
                                            avatar.className = 'ai-message-avatar';
                                            avatar.innerHTML = '<i class="fa-solid fa-atom"></i>';

                                            const toggleBtn = document.createElement('button');
                                            toggleBtn.className = 'ai-message-toggle';
                                            toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
                                            toggleBtn.title = 'Collapse/Expand message';
                                            toggleBtn.addEventListener('click', (e) => {
                                                e.stopPropagation();
                                                textBubble.classList.toggle('collapsed');
                                            });

                                            headerDiv.appendChild(avatar);
                                            headerDiv.appendChild(toggleBtn);

                                            const actionsDiv = document.createElement('div');
                                            actionsDiv.className = 'ai-message-actions';

                                            const copyBtn = document.createElement('button');
                                            copyBtn.className = 'ai-message-copy-btn';
                                            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                            copyBtn.title = 'Copy message';
                                            copyBtn.addEventListener('click', (e) => {
                                                e.stopPropagation();
                                                const content = textBubble.querySelector('.ai-message-content').textContent;
                                                navigator.clipboard.writeText(content).then(() => {
                                                    copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                                                    setTimeout(() => {
                                                        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                                    }, 2000);
                                                });
                                            });

                                            const copyRawBtn = document.createElement('button');
                                            copyRawBtn.className = 'ai-message-copy-btn';
                                            copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
                                            copyRawBtn.title = 'Copy raw markdown';
                                            copyRawBtn.addEventListener('click', (e) => {
                                                e.stopPropagation();
                                                navigator.clipboard.writeText(fullResponse).then(() => {
                                                    copyRawBtn.innerHTML = '<i class="fas fa-check"></i>';
                                                    setTimeout(() => {
                                                        copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
                                                    }, 2000);
                                                });
                                            });

                                            const expandBtn = document.createElement('button');
                                            expandBtn.className = 'ai-message-copy-btn';
                                            expandBtn.innerHTML = '<i class="fas fa-expand-alt"></i>';
                                            expandBtn.title = 'Expand message fullscreen';
                                            expandBtn.addEventListener('click', (e) => {
                                                e.stopPropagation();
                                                if (typeof window.openMessageFullscreen === 'function') {
                                                    window.openMessageFullscreen(textBubble);
                                                }
                                            });

                                            actionsDiv.appendChild(copyBtn);
                                            actionsDiv.appendChild(copyRawBtn);
                                            actionsDiv.appendChild(expandBtn);
                                            headerDiv.appendChild(actionsDiv);

                                            textBubble.appendChild(headerDiv);

                                            const contentDiv = document.createElement('div');
                                            contentDiv.className = 'ai-message-content';
                                            textBubble.appendChild(contentDiv);

                                            chatMessages.appendChild(textBubble);
                                            console.log('[OK] Text bubble created and added');

                                            // Add fullscreen double-click handler
                                            if (typeof window.addMessageFullscreenHandler === 'function') {
                                                window.addMessageFullscreenHandler(textBubble);
                                            }

                                            if (typeof TwoRuleStreamProcessor !== 'undefined') {
                                                console.log('🎨 Initializing TwoRuleStreamProcessor for visualization rendering...');
                                                try {
                                                    const _proc = new TwoRuleStreamProcessor(contentDiv);
                                                    textBubble._twoRuleProcessor = _proc;
                                                    window._twoRuleProcessors = window._twoRuleProcessors || new Set();
                                                    window._twoRuleProcessors.add(_proc);

                                                    if (window._twoRuleProcessors.size > 50) {
                                                        console.warn(`[PERFORMANCE] ${window._twoRuleProcessors.size} active TwoRule processors - possible memory leak`);
                                                    }

                                                    console.log('[OK] TwoRuleStreamProcessor initialized for bubble');
                                                } catch (e) {
                                                    console.warn('[WARN] TwoRuleStreamProcessor initialization failed:', e);
                                                }
                                            } else {
                                                console.warn('[WARN] TwoRuleStreamProcessor not available - visualizations will not render');
                                            }

                                            if (typeof VisualizationEngine !== 'undefined' && !window.visualizationEngine) {
                                                console.log('🎨 Initializing VisualizationEngine for fullscreen support...');
                                                window.visualizationEngine = new VisualizationEngine();
                                                console.log('[OK] VisualizationEngine initialized');
                                            }

                                            contentDiv.addEventListener('dblclick', (e) => {
                                                if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || e.target.closest('button') || e.target.closest('a')) {
                                                    return;
                                                }
                                                console.log('🔍 Opening message in popup (double-click)...');
                                                openMessagePopup('assistant', fullResponse);
                                            });
                                        }

                                        const textContent = textBubble.querySelector('.ai-message-content');

                                        if (textContent) {
                                            const _processor = (textBubble && textBubble._twoRuleProcessor) || (window.globalTwoRuleProcessor || null);

                                            if (textBubble && !textBubble._twoRuleProcessor && window.globalTwoRuleProcessor) {
                                                console.warn('[DEPRECATED] Stream using global TwoRule processor instead of per-bubble instance');
                                            }

                                            if (_processor && typeof _processor.processChunk === 'function') {
                                                console.log('🎨 Processing chunk through TwoRuleStreamProcessor (Plotly + Mermaid support)...');
                                                _processor.processChunk(data.text).then(() => {
                                                    console.log('[OK] Visualization processor handled chunk successfully');
                                                }).catch((e) => {
                                                    console.error('[ERROR] Visualization processor error:', e);
                                                    textContent.innerHTML = renderBasicMarkdown(fullResponse);
                                                });
                                            } else {
                                                console.log('[WARN] Using fallback markdown rendering (no visualizations)');
                                                if (window.marked) {
                                                    try {
                                                        textContent.innerHTML = marked.parse(fullResponse, {
                                                            breaks: true,
                                                            gfm: true
                                                        });
                                                        console.log('[OK] Markdown rendered successfully');
                                                    } catch (e) {
                                                        console.error('[ERROR] Markdown parse error:', e);
                                                        textContent.textContent = fullResponse;
                                                    }
                                                } else {
                                                    console.log('[WARN] Marked.js not available, using basic markdown');
                                                    textContent.innerHTML = renderBasicMarkdown(fullResponse);
                                                }
                                            }

                                            textBubble.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                                        } else {
                                            console.error('[ERROR] Could not find .ai-message-content in textBubble!');
                                        }

                                    } else if (data.type === 'conversation_sync') {
                                        // ✅ DATABASE AS SOURCE OF TRUTH: Accept backend's conversation
                                        console.log(`📥 [SYNC] Received conversation_sync: ${data.message_count} messages (round ${data.round})`);

                                        if (data.conversation_history && Array.isArray(data.conversation_history)) {
                                            console.log(`✅ [SYNC] Backend is authoritative - replacing frontend state`);
                                            console.log(`   Backend: ${data.message_count} messages`);
                                            console.log(`   Frontend (before): ${AppState.chatMessages.length} messages`);

                                            // Replace frontend conversation with backend's authoritative version
                                            AppState.chatMessages = data.conversation_history;

                                            // Sync to MessageStore
                                            if (window.MessageStore) {
                                                window.MessageStore.clearThread(currentThreadId);
                                                for (const msg of data.conversation_history) {
                                                    await window.MessageStore.addMessage(currentThreadId, msg, {
                                                        checkDuplicates: false,
                                                        silent: true
                                                    });
                                                }
                                            }

                                            console.log(`   Frontend (after): ${AppState.chatMessages.length} messages`);
                                            console.log(`✅ [SYNC] Frontend synced with backend's authoritative conversation`);

                                            // Log structure for debugging
                                            data.conversation_history.forEach((msg, idx) => {
                                                const contentTypes = Array.isArray(msg.content)
                                                    ? msg.content.map(b => b.type).join(', ')
                                                    : 'string';
                                                console.log(`  [${idx}] ${msg.role}: ${contentTypes}`);
                                            });
                                        }

                                    } else if (data.type === 'complete') {
                                        console.log('[OK] [COMPLETE EVENT] Stream finished');

                                        clearAIStatusIndicator();
                                        if (typeof AgentStatusIndicator !== 'undefined') {
                                            AgentStatusIndicator.clear(null);
                                        }

                                        console.log('💬 Full response length:', fullResponse.length);
                                        console.log('💬 Total bubbles created - Thinking:', thinkingBubble ? 'Yes' : 'No', 'Text:', textBubble ? 'Yes' : 'No');

                                        // ✅ DATABASE AS SOURCE OF TRUTH: Accept backend's complete conversation
                                        if (data.conversation_history && Array.isArray(data.conversation_history)) {
                                            console.log(`✅ [COMPLETE] Backend returned ${data.conversation_history.length} messages (authoritative)`);

                                            // Replace frontend state with backend's final conversation
                                            AppState.chatMessages = data.conversation_history;

                                            // Sync MessageStore
                                            if (window.MessageStore) {
                                                console.log(`[COMPLETE] Syncing MessageStore with backend's ${data.conversation_history.length} messages...`);

                                                window.MessageStore.clearThread(currentThreadId);
                                                for (const msg of data.conversation_history) {
                                                    await window.MessageStore.addMessage(currentThreadId, msg, {
                                                        checkDuplicates: false,
                                                        silent: true
                                                    });
                                                }
                                                console.log(`✅ [MessageStore] Synced complete conversation from backend`);
                                            }

                                            // Save thread with backend's authoritative conversation
                                            if (typeof ThreadManager !== 'undefined') {
                                                ThreadManager.updateCurrentThread(data.conversation_history);
                                                console.log(`✅ [Thread] Saved complete conversation (${data.conversation_history.length} messages)`);
                                            }
                                        } else {
                                            console.warn('⚠️ Backend did not return conversation_history in complete event');
                                        }

                                        const _finalProc = (textBubble && textBubble._twoRuleProcessor) || (window.globalTwoRuleProcessor || null);

                                        if (textBubble && !textBubble._twoRuleProcessor && window.globalTwoRuleProcessor) {
                                            console.warn('[DEPRECATED] Finalizing global TwoRule processor instead of per-bubble instance');
                                        }

                                        if (_finalProc && typeof _finalProc.finalize === 'function') {
                                            console.log('🎨 Finalizing TwoRuleStreamProcessor (rendering any pending visualizations)...');
                                            try {
                                                await _finalProc.finalize();
                                                console.log('[OK] Visualization processor finalized successfully');

                                                if (textBubble) {
                                                    const textContent = textBubble.querySelector('.ai-message-content');
                                                    if (textContent && (!textContent.innerHTML || textContent.innerHTML.trim() === '')) {
                                                        console.log('[WARN] Processor finalized but no content visible - forcing markdown render');
                                                        if (window.marked) {
                                                            textContent.innerHTML = marked.parse(fullResponse, { breaks: true, gfm: true });
                                                        } else {
                                                            textContent.innerHTML = renderBasicMarkdown(fullResponse);
                                                        }
                                                    }
                                                }
                                            } catch (e) {
                                                console.error('[ERROR] Visualization processor finalize error:', e);
                                            }
                                        }

                                        if (textBubble && fullResponse.length > 0) {
                                            const textContent = textBubble.querySelector('.ai-message-content');
                                            if (textContent) {
                                                // ✅ CRITICAL FIX: Check if content is actually visible (not just empty)
                                                const visibleText = textContent.textContent?.trim() || '';
                                                if (visibleText.length === 0 || visibleText.length < fullResponse.length * 0.5) {
                                                    console.warn(`[Prime] ⚠️ Content missing or incomplete in DOM (${visibleText.length} vs ${fullResponse.length} chars) - forcing full render`);
                                                    if (window.marked) {
                                                        textContent.innerHTML = marked.parse(fullResponse, { breaks: true, gfm: true });
                                                    } else {
                                                        textContent.innerHTML = renderBasicMarkdown(fullResponse);
                                                    }
                                                    console.log(`[Prime] ✅ Forced full content render - ${fullResponse.length} chars`);
                                                } else {
                                                    console.log('[OK] Final rendered content length:', textContent.innerHTML.length);
                                                    console.log('[OK] Streaming complete - content already displayed via incremental updates');
                                                }

                                                if (typeof Prism !== 'undefined') {
                                                    textContent.querySelectorAll('pre code').forEach(block => {
                                                        try {
                                                            Prism.highlightElement(block);
                                                        } catch (e) {
                                                            console.warn('[WARN] Prism highlighting failed:', e);
                                                        }
                                                    });
                                                }
                                            }
                                        }

                                        if (fullResponse.length === 0 && thinkingBubble) {
                                            thinkingBubble.classList.remove('collapsed');
                                        }

                                    } else if (data.type === 'tool_result') {
                                        if (window._twoRuleProcessors && window._twoRuleProcessors.size) {
                                            console.log('🔧 Flushing buffered content from active TwoRule processors after tool result...');
                                            for (const _p of Array.from(window._twoRuleProcessors)) {
                                                try {
                                                    if (_p && typeof _p.forceFlush === 'function') {
                                                        _p.forceFlush();
                                                    }
                                                } catch (e) {
                                                    console.warn('[WARN] Error flushing TwoRule processor:', e);
                                                }
                                            }
                                        }

                                        console.log('[OK] [TOOL_RESULT EVENT] Creating separate tool result bubble');

                                        updateAIStatusIndicator('tool-success');
                                        if (typeof AgentStatusIndicator !== 'undefined') {
                                            AgentStatusIndicator.update('tool-success', null);
                                        }

                                        if (!firstContentReceived) {
                                            removeThinkingIndicator();
                                            firstContentReceived = true;
                                        }

                                        const isError = !data.success;
                                        const resultText = data.result || '(no result)';
                                        const rawResult = data.result || '';

                                        const toolResultBubble = document.createElement('div');
                                        toolResultBubble.className = 'ai-message assistant tool-result-bubble';
                                        toolResultBubble.setAttribute('data-tool-result-id', data.tool_id);

                                        const headerDiv = document.createElement('div');
                                        headerDiv.className = 'ai-message-header';

                                        const avatar = document.createElement('div');
                                        avatar.className = 'ai-message-avatar';
                                        avatar.style.background = isError ? '#ef4444' : '#60A5FA';
                                        avatar.innerHTML = '<i class="fas fa-flag" style="color: white; font-size: 14px;"></i>';

                                        const toggleBtn = document.createElement('button');
                                        toggleBtn.className = 'ai-message-toggle';
                                        toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
                                        toggleBtn.title = 'Collapse/Expand result';
                                        toggleBtn.addEventListener('click', (e) => {
                                            e.stopPropagation();
                                            toolResultBubble.classList.toggle('collapsed');
                                        });

                                        headerDiv.appendChild(avatar);
                                        headerDiv.appendChild(toggleBtn);

                                        const actionsDiv = document.createElement('div');
                                        actionsDiv.className = 'ai-message-actions';

                                        const copyBtn = document.createElement('button');
                                        copyBtn.className = 'ai-message-copy-btn';
                                        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                        copyBtn.title = 'Copy result';
                                        copyBtn.addEventListener('click', (e) => {
                                            e.stopPropagation();
                                            const content = toolResultBubble.querySelector('.ai-message-content').textContent;
                                            navigator.clipboard.writeText(content).then(() => {
                                                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                                                setTimeout(() => {
                                                    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                                }, 2000);
                                            });
                                        });

                                        const copyRawBtn = document.createElement('button');
                                        copyRawBtn.className = 'ai-message-copy-btn';
                                        copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
                                        copyRawBtn.title = 'Copy raw result';
                                        copyRawBtn.addEventListener('click', (e) => {
                                            e.stopPropagation();
                                            navigator.clipboard.writeText(rawResult).then(() => {
                                                copyRawBtn.innerHTML = '<i class="fas fa-check"></i>';
                                                setTimeout(() => {
                                                    copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
                                                }, 2000);
                                            });
                                        });

                                        const expandBtn = document.createElement('button');
                                        expandBtn.className = 'ai-message-copy-btn';
                                        expandBtn.innerHTML = '<i class="fas fa-expand-alt"></i>';
                                        expandBtn.title = 'Expand message fullscreen';
                                        expandBtn.addEventListener('click', (e) => {
                                            e.stopPropagation();
                                            if (typeof window.openMessageFullscreen === 'function') {
                                                window.openMessageFullscreen(toolResultBubble);
                                            }
                                        });

                                        actionsDiv.appendChild(copyBtn);
                                        actionsDiv.appendChild(copyRawBtn);
                                        actionsDiv.appendChild(expandBtn);
                                        headerDiv.appendChild(actionsDiv);

                                        toolResultBubble.appendChild(headerDiv);

                                        const contentDiv = document.createElement('div');
                                        contentDiv.className = 'ai-message-content';

                                        let formattedResult = resultText;
                                        try {
                                            const parsed = JSON.parse(resultText);
                                            formattedResult = JSON.stringify(parsed, null, 2);
                                        } catch (e) {
                                            // Keep as-is if not JSON
                                        }

                                        contentDiv.innerHTML = `
                                            <div style="margin-bottom: 8px; color: ${isError ? '#ef4444' : '#60A5FA'};">
                                                <strong><i class="fas ${isError ? 'fa-times-circle' : 'fa-check-circle'}"></i> Tool Result: ${data.tool_name}</strong>
                                            </div>
                                            <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 6px; overflow-x: auto; max-height: 400px; overflow-y: auto; color: ${isError ? '#fca5a5' : '#86efac'};">${formattedResult}</pre>
                                        `;

                                        toolResultBubble.appendChild(contentDiv);

                                        chatMessages.appendChild(toolResultBubble);
                                        chatMessages.scrollTop = chatMessages.scrollHeight;

                                        console.log('[OK] Tool result bubble created with white flag icon');

                                        let parsedResult;
                                        try {
                                            parsedResult = JSON.parse(resultText);
                                        } catch (e) {
                                            parsedResult = resultText;
                                        }

                                        toolResults.push({
                                            type: 'tool_result',
                                            tool_use_id: data.tool_id,
                                            content: parsedResult,
                                            is_error: !data.success
                                        });
                                        console.log('[OK] Tracked tool_result for conversation history:', data.tool_id);

                                        // Handle UI commands from tool results
                                        if (parsedResult && typeof parsedResult === 'object') {
                                            const uiCommand = parsedResult.ui_command || parsedResult.result?.ui_command;

                                            if (uiCommand === 'open_workflow') {
                                                const slug = parsedResult.slug || parsedResult.result?.slug;
                                                const title = parsedResult.workflow_title || parsedResult.result?.workflow_title;

                                                if (slug) {
                                                    console.log(`🎨 [UI_COMMAND] Opening workflow in automation canvas: ${slug}`);

                                                    // Switch to automation tab
                                                    if (typeof window.switchToTab === 'function') {
                                                        window.switchToTab('automation');
                                                    }

                                                    // Wait for tab to be visible and automation canvas to be ready
                                                    setTimeout(async () => {
                                                        if (!window.automationCanvas) {
                                                            console.error('❌ [UI_COMMAND] AutomationCanvas not available');
                                                            return;
                                                        }

                                                        try {
                                                            // Ensure workflows are loaded
                                                            if (!window.automationCanvas.workflows || window.automationCanvas.workflows.length === 0) {
                                                                console.log('🔄 [UI_COMMAND] Loading workflows list first...');
                                                                await window.automationCanvas.loadWorkflows();
                                                            }

                                                            // Load the workflow by slug
                                                            await window.automationCanvas.loadWorkflowBySlug(slug);
                                                            console.log(`✅ [UI_COMMAND] Workflow opened: ${title || slug}`);
                                                        } catch (error) {
                                                            console.error('❌ [UI_COMMAND] Failed to open workflow:', error);
                                                        }
                                                    }, 300);
                                                }
                                            }
                                        }

                                    } else if (data.type === 'server_tool_use') {
                                        console.log('🌐 [SERVER_TOOL_USE EVENT] Server tool requested:', data.name);

                                        if (!firstContentReceived) {
                                            removeThinkingIndicator();
                                            firstContentReceived = true;
                                        }

                                        const serverToolBubble = document.createElement('div');
                                        serverToolBubble.className = 'ai-message assistant server-tool-bubble';
                                        serverToolBubble.setAttribute('data-server-tool-id', data.id);

                                        const headerDiv = document.createElement('div');
                                        headerDiv.className = 'ai-message-header';

                                        const avatar = document.createElement('div');
                                        avatar.className = 'ai-message-avatar';
                                        avatar.innerHTML = data.name === 'web_search'
                                            ? '<i class="fas fa-search" style="color: #4ADE80;"></i>'
                                            : '<i class="fas fa-globe" style="color: #60A5FA;"></i>';

                                        const toggleBtn = document.createElement('button');
                                        toggleBtn.className = 'ai-message-toggle';
                                        toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
                                        toggleBtn.title = 'Collapse/Expand server tool details';
                                        toggleBtn.addEventListener('click', (e) => {
                                            e.stopPropagation();
                                            serverToolBubble.classList.toggle('collapsed');
                                        });

                                        headerDiv.appendChild(avatar);
                                        headerDiv.appendChild(toggleBtn);

                                        const actionsDiv = document.createElement('div');
                                        actionsDiv.className = 'ai-message-actions';

                                        const copyBtn = document.createElement('button');
                                        copyBtn.className = 'ai-message-copy-btn';
                                        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                        copyBtn.title = 'Copy server tool content';
                                        copyBtn.addEventListener('click', (e) => {
                                            e.stopPropagation();
                                            const contentDiv = serverToolBubble.querySelector('.ai-message-content');
                                            const content = contentDiv ? contentDiv.textContent : '';
                                            navigator.clipboard.writeText(content).then(() => {
                                                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                                                setTimeout(() => {
                                                    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                                }, 2000);
                                            });
                                        });

                                        const expandBtn = document.createElement('button');
                                        expandBtn.className = 'ai-message-copy-btn';
                                        expandBtn.innerHTML = '<i class="fas fa-expand-alt"></i>';
                                        expandBtn.title = 'Expand message fullscreen';
                                        expandBtn.addEventListener('click', (e) => {
                                            e.stopPropagation();
                                            if (typeof window.openMessageFullscreen === 'function') {
                                                window.openMessageFullscreen(serverToolBubble);
                                            }
                                        });

                                        actionsDiv.appendChild(copyBtn);
                                        actionsDiv.appendChild(expandBtn);
                                        headerDiv.appendChild(actionsDiv);

                                        const contentDiv = document.createElement('div');
                                        contentDiv.className = 'ai-message-content';

                                        const toolLabel = data.name === 'web_search' ? '[WEBSEARCH]' : '[WEBFETCH]';
                                        const toolColor = data.name === 'web_search' ? '#4ADE80' : '#60A5FA';
                                        const query = data.input?.query || data.input?.url || 'Processing...';

                                        contentDiv.innerHTML = `
                                            <div style="margin-bottom: 8px;">
                                                <strong style="color: ${toolColor};">${toolLabel}</strong>
                                            </div>
                                            <div style="margin-bottom: 8px; color: var(--text-secondary);">
                                                <strong>Query:</strong> ${query}
                                            </div>
                                            <div style="color: var(--text-muted); font-size: 12px;">
                                                <i class="fas fa-spinner fa-spin"></i> Searching...
                                            </div>
                                        `;

                                        serverToolBubble.appendChild(headerDiv);
                                        serverToolBubble.appendChild(contentDiv);
                                        serverToolBubble.classList.add('collapsed');
                                        chatMessages.appendChild(serverToolBubble);

                                        lastEventType = 'server_tool_use';

                                        console.log('[OK] Server tool bubble created');

                                    } else if (data.type === 'error') {
                                        // Enhanced error logging with full context
                                        console.error('═══════════════════════════════════════════════════');
                                        console.error('❌ [STREAM ERROR RECEIVED]');
                                        console.error('═══════════════════════════════════════════════════');
                                        console.error('Error Type:', data.error_type || 'Unknown');
                                        console.error('Error Category:', data.error_category || 'Unknown');
                                        console.error('Error Message:', data.error_message || data.error);
                                        console.error('User Message:', data.user_message || 'No user message');
                                        console.error('Session ID:', data.session_id);
                                        console.error('Round:', data.round);
                                        if (data.stack_trace) {
                                            console.error('Stack Trace:', data.stack_trace);
                                        }
                                        console.error('═══════════════════════════════════════════════════');

                                        const is413Error = data.error && (
                                            data.error.includes('413') ||
                                            data.error.includes('request_too_large') ||
                                            data.error.includes('Request exceeds the maximum size') ||
                                            data.error_category === 'REQUEST_TOO_LARGE'
                                        );

                                        if (is413Error) {
                                            console.error('[413 ERROR] Request too large - clearing failed message and reloading thread');

                                            const lastAssistantMsg = document.querySelector('.ai-message.assistant:last-child');
                                            if (lastAssistantMsg) {
                                                lastAssistantMsg.remove();
                                            }

                                            if (AppState.chatMessages.length > 0 && AppState.chatMessages[AppState.chatMessages.length - 1].role === 'assistant') {
                                                AppState.chatMessages.pop();
                                            }

                                            const container = document.getElementById('notification-container');
                                            const notification = document.createElement('div');
                                            notification.className = 'notification error';
                                            notification.innerHTML = `
                                                <div class="notification-icon">
                                                    <i class="fas fa-exclamation-triangle"></i>
                                                </div>
                                                <div class="notification-content">
                                                    <div class="notification-message">
                                                        <strong>Conversation Too Large</strong><br>
                                                        Request exceeded API limits. Truncating conversation and reloading thread...
                                                    </div>
                                                </div>
                                                <button class="notification-close" onclick="this.parentElement.remove()">
                                                    <i class="fas fa-times"></i>
                                                </button>
                                            `;
                                            container.appendChild(notification);
                                            setTimeout(() => notification.remove(), 4000);

                                            setTimeout(() => {
                                                if (typeof ThreadManager !== 'undefined' && ThreadManager.currentThreadSlug) {
                                                    console.log('[413 RECOVERY] Reloading thread:', ThreadManager.currentThreadSlug);
                                                    ThreadManager.loadThread(ThreadManager.currentThreadSlug);
                                                } else {
                                                    console.log('[413 RECOVERY] No thread to reload, refreshing chat');
                                                    location.reload();
                                                }
                                            }, 2000);

                                            fullResponse = '';
                                        } else {
                                            // Use user-friendly message if available, otherwise show technical details
                                            const displayMessage = data.user_message || data.error_message || data.error || 'Unknown error occurred';
                                            const errorCategory = data.error_category || 'ERROR';

                                            // Determine icon based on error category
                                            let errorIcon = '❌';
                                            if (errorCategory === 'TIMEOUT') errorIcon = '⏱️';
                                            else if (errorCategory === 'RATE_LIMIT') errorIcon = '🚦';
                                            else if (errorCategory === 'AUTH_ERROR') errorIcon = '🔒';

                                            fullResponse = `Error: ${displayMessage}`;
                                            const lastMsg = document.querySelector('.ai-message.assistant:last-child .ai-message-content');
                                            if (lastMsg) {
                                                lastMsg.innerHTML = `<div style="color: #ef4444; padding: 16px; background: rgba(239, 68, 68, 0.1); border-radius: 8px; border-left: 4px solid #ef4444;">
                                                    <div style="display: flex; align-items: start; gap: 12px;">
                                                        <div style="font-size: 24px;">${errorIcon}</div>
                                                        <div style="flex: 1;">
                                                            <strong style="display: block; margin-bottom: 8px;">${errorCategory.replace(/_/g, ' ')}</strong>
                                                            <div style="margin-bottom: 8px;">${displayMessage}</div>
                                                            ${data.error_type ? `<div style="font-size: 12px; opacity: 0.7; margin-top: 8px;">Error Type: ${data.error_type}</div>` : ''}
                                                            ${data.round ? `<div style="font-size: 12px; opacity: 0.7;">Round: ${data.round}</div>` : ''}
                                                        </div>
                                                    </div>
                                                </div>`;
                                            }

                                            // Show notification for critical errors
                                            if (errorCategory === 'TIMEOUT' || errorCategory === 'RATE_LIMIT') {
                                                const container = document.getElementById('notification-container');
                                                if (container) {
                                                    const notification = document.createElement('div');
                                                    notification.className = 'notification error';
                                                    notification.innerHTML = `
                                                        <div class="notification-icon">
                                                            <i class="fas fa-exclamation-triangle"></i>
                                                        </div>
                                                        <div class="notification-content">
                                                            <div class="notification-message">
                                                                <strong>${errorIcon} ${errorCategory.replace(/_/g, ' ')}</strong><br>
                                                                ${displayMessage}
                                                            </div>
                                                        </div>
                                                        <button class="notification-close" onclick="this.parentElement.remove()">
                                                            <i class="fas fa-times"></i>
                                                        </button>
                                                    `;
                                                    container.appendChild(notification);
                                                    setTimeout(() => notification.remove(), 6000);
                                                }
                                            }
                                        }
                                    }
                                }
                            } catch (e) {
                                threadErrorCount++;
                                console.error(`[Prime] SSE parse error (${threadErrorCount}/${maxThreadErrors}):`, e, 'Line:', line);

                                if (threadErrorCount >= maxThreadErrors) {
                                    threadFailed = true;
                                    console.error(`[Prime] Thread ${threadSlug} failed after ${maxThreadErrors} errors - stopping THIS thread only`);
                                    break;
                                }
                            }
                        }
                    }

                    if (threadFailed) {
                        console.error(`[Prime] Exiting stream reader for failed thread ${threadSlug}`);
                        break;
                    }
                }
            }

            if (threadFailed) {
                addChatMessage('assistant', `❌ Thread error: Too many parse errors. Please try again.`);
            }

            // Clean up timeout check
            if (streamTimeoutId) {
                clearInterval(streamTimeoutId);
            }

            removeThinkingIndicator();
            // Hide processing indicator when streaming completes
            if (typeof window.hidePrimeProcessingIndicator === 'function') {
                window.hidePrimeProcessingIndicator();
            }
            
            // Clean up stream controls
            currentStreamController = null;
            isStreaming = false;
            const stopBtn = document.getElementById('ai-chat-stop-btn');
            const sendBtn = document.getElementById('ai-chat-send-btn');
            if (stopBtn) stopBtn.style.display = 'none';
            if (sendBtn) sendBtn.style.display = 'inline-flex';
            
            const responseTime = Date.now() - startTime;
            console.log(`✅ Streamed response received in ${responseTime}ms`);

            // ✅ FIX: Save fullResponse to MessageStore after streaming completes
            if (fullResponse && fullResponse.trim().length > 0) {
                if (window.MessageStore) {
                    await window.MessageStore.addMessage(currentThreadId, {
                        role: 'assistant',
                        content: fullResponse,
                        response_time: responseTime
                    }, {
                        checkDuplicates: true,
                        syncToBackend: false  // Backend handles via conversation_sync
                    });
                    console.log('✅ [MessageStore] Streamed assistant response added to history');
                } else {
                    console.error('[ERROR] MessageStore not available for saving assistant response');
                }
            } else {
                console.log('[WARN] No streaming response content to add to history');
            }

        } else {
            // NON-STREAMING JSON RESPONSE
            const data = await response.json();
            const responseTime = Date.now() - startTime;

            removeThinkingIndicator();
            // Hide processing indicator for non-streaming response
            if (typeof window.hidePrimeProcessingIndicator === 'function') {
                window.hidePrimeProcessingIndicator();
            }

            if (data.tools_used && Array.isArray(data.tools_used)) {
                console.log(`🔧 AI used ${data.tools_used.length} tools:`, data.tools_used);
                data.tools_used.forEach(tool => {
                    ToolManager.recordToolCall(
                        tool.name || tool,
                        tool.success !== false,
                        tool.duration || 0
                    );
                });

                if (data.tools_used.length > 0) {
                    addToolUsageMessage(data.tools_used);
                    showNotification(`AI used ${data.tools_used.length} tool(s)`, 'info', 2000);
                }
            }

            if (data.response) {
                addChatMessage('assistant', data.response);
                console.log(`✅ Chat response received in ${responseTime}ms`);
            } else if (data.error) {
                addChatMessage('assistant', `Error: ${data.error}`);
                showNotification('AI Error: ' + data.error, 'error');
            }

            const responseContent = data.response || data.error || '';
            if (responseContent.trim().length > 0) {
                if (window.MessageStore) {
                    await window.MessageStore.addMessage(currentThreadId, {
                        role: 'assistant',
                        content: responseContent,
                        tools_used: data.tools_used || [],
                        response_time: responseTime
                    }, {
                        checkDuplicates: true,
                        silent: false
                    });
                    console.log('✅ [MessageStore] Assistant response added to history');
                } else {
                    console.error('[ERROR] MessageStore not available for saving assistant response');
                }
            } else {
                console.log('[WARN] No response content to add to history (empty response)');
            }
        }

    } catch (error) {
        console.error('❌ Chat error:', error);
        console.error('Error details:', {
            message: error.message,
            type: error.name,
            stack: error.stack
        });

        // Clean up stream controls on error
        currentStreamController = null;
        isStreaming = false;
        const stopBtn = document.getElementById('ai-chat-stop-btn');
        const sendBtn = document.getElementById('ai-chat-send-btn');
        if (stopBtn) stopBtn.style.display = 'none';
        if (sendBtn) sendBtn.style.display = 'inline-flex';

        // Hide processing indicator on error
        if (typeof window.hidePrimeProcessingIndicator === 'function') {
            window.hidePrimeProcessingIndicator();
        }

        // Show user-friendly toast notification for common errors
        const errorMsg = error.message || '';
        if (errorMsg.includes('502') || errorMsg.includes('Bad Gateway')) {
            if (typeof showNotification === 'function') {
                showNotification('⚠️ Backend is restarting. Please wait 30 seconds and try again.', 'warning', 8000);
            }
        } else if (errorMsg.includes('503') || errorMsg.includes('Service Unavailable')) {
            if (typeof showNotification === 'function') {
                showNotification('⚠️ Service temporarily unavailable. Retrying in a moment...', 'warning', 5000);
            }
        } else if (errorMsg.includes('500') || errorMsg.includes('Internal Server Error')) {
            if (typeof showNotification === 'function') {
                showNotification('❌ Server error occurred. Please try again or contact support.', 'error', 6000);
            }
        } else if (errorMsg.includes('401') || errorMsg.includes('Unauthorized')) {
            if (typeof showNotification === 'function') {
                showNotification('🔒 Session expired. Please refresh and log in again.', 'error', 6000);
            }
        } else if (errorMsg.includes('429') || errorMsg.includes('rate limit')) {
            if (typeof showNotification === 'function') {
                showNotification('⏰ Rate limit reached. Please wait a moment and try again.', 'warning', 6000);
            }
        } else if (errorMsg.includes('network') || errorMsg.includes('fetch') || errorMsg.includes('Failed to fetch')) {
            if (typeof showNotification === 'function') {
                showNotification('📡 Network error. Check your connection and try again.', 'error', 5000);
            }
        } else {
            // Generic error notification
            if (typeof showNotification === 'function') {
                showNotification('❌ An error occurred. Please try again.', 'error', 4000);
            }
        }

        if (window.ErrorRecoveryManager && error.message) {
            const errorMsgLower = error.message.toLowerCase();
            const isRecoverable = errorMsgLower.includes('invalid_request_error') ||
                errorMsgLower.includes('tool_use_id') ||
                errorMsgLower.includes('first block must be') ||
                errorMsgLower.includes('thinking') ||
                errorMsgLower.includes('rate limit') ||
                errorMsgLower.includes('context_length') ||
                errorMsgLower.includes('prompt is too long') ||
                errorMsgLower.includes('overloaded');

            // DETAILED LOGGING FOR ERROR RECOVERY DEBUGGING
            console.group('🔴 ERROR RECOVERY SYSTEM TRIGGERED');
            console.log('📍 Location: Prime AI Chat');
            console.log('⚠️ Error Object:', error);
            console.log('📝 Error Message:', error.message);
            console.log('🔍 Error Type:', error.name);
            console.log('🎯 Is Recoverable:', isRecoverable);
            // Note: requestBody not available in catch scope (defined in try block)
            console.log('🧵 Thread ID:', currentThreadId);
            console.log('⏰ Timestamp:', new Date().toISOString());
            console.groupEnd();

            if (isRecoverable) {
                // Check if auto-recovery is enabled in settings
                const recoveryEnabled = typeof window.isErrorRecoveryEnabled === 'function'
                    ? window.isErrorRecoveryEnabled(errorType)
                    : true;

                if (!recoveryEnabled) {
                    console.log('⛔ Auto-recovery disabled in settings - skipping recovery');
                    throw error; // Rethrow to show error normally
                }

                console.log('🔄 Attempting auto-recovery...');

                try {
                    const recoveryManager = new ErrorRecoveryManager(
                        'prime',
                        currentThreadId,
                        null
                    );

                    const recoveryResponse = await recoveryManager.handleError(error, requestBody);

                    if (recoveryResponse) {
                        console.log('✅ Auto-recovery successful!');

                        const recoveryLog = recoveryManager.exportRecoveryLog();
                        console.log('=== RECOVERY LOG ===\n' + recoveryLog);

                        if (typeof showNotification === 'function') {
                            showNotification('Auto-recovery successful - message sent', 'success');
                        }

                        return;
                    }
                } catch (recoveryError) {
                    console.error('❌ Auto-recovery failed:', recoveryError);
                }
            }
        }

        removeThinkingIndicator();

        const is413Error = error.message && (
            error.message.includes('413') ||
            error.message.includes('request_too_large') ||
            error.message.includes('Request exceeds the maximum size')
        );

        if (is413Error) {
            console.error('[413 ERROR] Request too large caught in error handler');

            const lastAssistantMsg = document.querySelector('.ai-message.assistant:last-child');
            if (lastAssistantMsg) {
                lastAssistantMsg.remove();
            }

            if (AppState.chatMessages.length > 0 && AppState.chatMessages[AppState.chatMessages.length - 1].role === 'assistant') {
                AppState.chatMessages.pop();
            }

            const container = document.getElementById('notification-container');
            const notification = document.createElement('div');
            notification.className = 'notification error';
            notification.innerHTML = `
                <div class="notification-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-message">
                        <strong>Conversation Too Large</strong><br>
                        Request exceeded API limits. Truncating conversation and reloading thread...
                    </div>
                </div>
                <button class="notification-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            `;
            container.appendChild(notification);
            setTimeout(() => notification.remove(), 4000);

            setTimeout(() => {
                if (typeof ThreadManager !== 'undefined' && ThreadManager.currentThreadSlug) {
                    console.log('[413 RECOVERY] Reloading thread:', ThreadManager.currentThreadSlug);
                    ThreadManager.loadThread(ThreadManager.currentThreadSlug);
                } else {
                    console.log('[413 RECOVERY] No thread to reload, refreshing chat');
                    location.reload();
                }
            }, 2000);

            return;
        }

        let userErrorMsg = 'Sorry, I encountered an error. ';
        if (error.message.includes('aborted') || error.message.includes('BodyStreamBuffer')) {
            // User stopped the response - this is intentional, not an error
            return; // Don't show error message
        } else if (error.message.includes('Failed to fetch')) {
            userErrorMsg += 'Could not connect to backend. Is Flask running on port 5001?';
            console.error('❌ Fix: Run BISTART or start Flask manually');
        } else if (error.message.includes('NetworkError')) {
            userErrorMsg += 'Network error. Check your connection.';
        } else {
            userErrorMsg += error.message;
        }

        addChatMessage('assistant', userErrorMsg);
        showNotification('Chat Error: ' + error.message, 'error');

        if (!AppState.isConnected && error.message.includes('200')) {
            AppState.isConnected = true;
            console.log('✅ Backend is actually working! Marking as connected.');
        }
    }
}

function addToolUsageMessage(toolsUsed) {
    if (!toolsUsed || toolsUsed.length === 0) return;

    const toolsHtml = toolsUsed.map(tool => {
        const success = tool.success !== false;
        const duration = tool.duration || 0;
        const icon = success ? 'fa-check-circle' : 'fa-exclamation-circle';
        const statusClass = success ? 'success' : 'error';

        return `
            <div class="tool-item ${statusClass}">
                <div class="tool-item-icon">
                    <i class="fas ${icon}"></i>
                </div>
                <div class="tool-item-name">${tool.name || tool}</div>
                <div class="tool-item-duration">${duration}ms</div>
            </div>
        `;
    }).join('');

    const toolContent = `
        <div class="tool-usage-header">
            <div class="tool-icon">
                <i class="fas fa-wrench"></i>
            </div>
            <div class="tool-title">Tools Used (${toolsUsed.length})</div>
        </div>
        <div class="tool-usage-list">
            ${toolsHtml}
        </div>
    `;

    addChatMessage('tool', toolContent, false);
}

async function sendChatMessageWithFiles(message, sessionId, startTime) {
    console.log('[ATTACH] [FILE UPLOAD] Preparing to send message with files...');
    console.log(`[FILES] Files attached: ${window.chatAttachedFiles.length}`);

    try {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('message', message || 'Analyze these files');

        window.chatAttachedFiles.forEach(file => {
            formData.append('files', file);
            console.log(`[ATTACH] Added file: ${file.name} (${file.type}, ${file.size} bytes)`);
        });

        console.log('📤 Sending files to /api/chat/upload...');
        const uploadResponse = await fetch(`${window.API_BASE_URL}/api/chat/upload`, {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            throw new Error(`HTTP error! status: ${uploadResponse.status}`);
        }

        const uploadData = await uploadResponse.json();
        console.log('[OK] Files uploaded and processed:', uploadData);

        // Files are now in session context, send the chat message
        console.log('📨 Sending chat message with file context...');

        // Clear files after successful upload
        console.log('[CLEAN] Clearing attached files from UI after successful upload...');
        if (window.clearChatAttachedFiles) {
            window.clearChatAttachedFiles();
        }

        // Now send the actual chat message - files are already in session context
        const agentId = '1';
        const requestBody = {
            message: message || 'Please analyze the uploaded files',
            session_id: sessionId,
            thread_id: sessionId,
            thread_slug: sessionId,
            user_context: await gatherUserContext(),
            context: {
                tab: AppState.currentTab,
                platform: 'business_ai_platform',
                tools_enabled: true,
                has_file_attachments: true  // Signal that files were uploaded
            },
            preferences: {
                use_tools: true,
                verbose_tool_output: true,
                streaming: true
            }
        };

        console.log('🚀 Starting agent with file context...');
        const startResponse = await fetch(`${window.API_BASE_URL}/api/agent/agent/${agentId}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        if (!startResponse.ok) {
            throw new Error(`Agent start error! status: ${startResponse.status}`);
        }

        const startData = await startResponse.json();
        console.log('[OK] Agent started with file context');

        console.log('🌊 Connecting to SSE stream...');
        const streamUrl = `${window.API_BASE_URL}/api/agent/stream/${agentId}?thread_slug=${sessionId}`;
        
        // ✅ TEAM COLLABORATION FIX: Send socket ID to prevent message echo
        const headers = {};
        if (window.SynergyRealtime?.socket?.id) {
            headers['X-Socket-ID'] = window.SynergyRealtime.socket.id;
            console.log('[Stream] Adding X-Socket-ID header:', window.SynergyRealtime.socket.id);
        }
        
        const response = await fetch(streamUrl, { headers: headers });

        if (!response.ok) {
            throw new Error(`Stream error! status: ${response.status}`);
        }

        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('text/event-stream')) {
            console.log('🌊 Receiving streamed response with file context...');

            removeThinkingIndicator();

            const chatMessages = document.getElementById('ai-chat-messages');

            let fullResponse = '';
            let firstContentReceived = false;
            let textBubble = null;
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const messages = buffer.split('\n\n');
                buffer = messages.pop() || '';

                for (const message of messages) {
                    const lines = message.split('\n');
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const jsonStr = line.substring(6).trim();
                                if (jsonStr) {
                                    const data = JSON.parse(jsonStr);

                                    if (data.type === 'content_delta') {
                                        fullResponse += data.text;

                                        if (!textBubble) {
                                            textBubble = document.createElement('div');
                                            textBubble.className = 'ai-message assistant text-bubble';
                                            textBubble.innerHTML = `
                                                <div class="ai-message-header">
                                                    <div class="ai-message-avatar">
                                                        <i class="fa-solid fa-atom"></i>
                                                    </div>
                                                </div>
                                                <div class="ai-message-content"></div>
                                            `;
                                            chatMessages.appendChild(textBubble);
                                        }

                                        const contentDiv = textBubble.querySelector('.ai-message-content');
                                        const _tbProc = textBubble._twoRuleProcessor || textBubble.processor || null;
                                        if (_tbProc && typeof _tbProc.processChunk === 'function') {
                                            try {
                                                const result = _tbProc.processChunk(data.text);
                                                if (result && typeof result.catch === 'function') {
                                                    result.catch(err => {
                                                        console.warn('[WARN] processor.processChunk error:', err);
                                                        contentDiv.innerHTML += data.text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                                                    });
                                                }
                                            } catch (e) {
                                                console.warn('[WARN] processChunk exception:', e);
                                                contentDiv.innerHTML += data.text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                                            }
                                        } else {
                                            contentDiv.innerHTML += data.text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                                        }

                                        chatMessages.scrollTop = chatMessages.scrollHeight;
                                    }
                                }
                            } catch (e) {
                                console.error('Failed to parse SSE data:', e);
                            }
                        }
                    }
                }
            }

            const responseTime = Date.now() - startTime;
            console.log(`[ATTACH] File upload + response completed in ${responseTime}ms`);

            if (fullResponse && fullResponse.trim().length > 0) {
                const currentThreadId = AppState.currentThreadId || 'prime-ai-default';
                await window.MessageStore.addMessage(currentThreadId, {
                    role: 'assistant',
                    content: fullResponse,
                    response_time: responseTime
                });
            }

            // 🔧 FIX #2: Reload conversation from backend (database is source of truth)
            // Backend has the file upload message saved, don't use stale AppState
            if (typeof ThreadManager !== 'undefined') {
                try {
                    const apiBaseUrl = window.API_BASE_URL || 'http://localhost:5001';
                    const threadResponse = await fetch(`${apiBaseUrl}/api/threads/${currentThreadId}`);
                    if (threadResponse.ok) {
                        const threadData = await threadResponse.json();
                        if (threadData.messages) {
                            ThreadManager.updateCurrentThread(threadData.messages);
                        }
                    }
                } catch (error) {
                    console.error('❌ [PrimeAI] Failed to reload thread after file upload:', error);
                    // Fallback to AppState if backend unavailable
                    ThreadManager.updateCurrentThread(AppState.chatMessages);
                }
            }
        }

    } catch (error) {
        console.error('[ERROR] File upload error:', error);
        removeThinkingIndicator();
        addChatMessage('assistant', `Error uploading files: ${error.message}`);
        showNotification('Failed to upload files', 'error');

        console.log('[CLEAN] Clearing attached files after error...');
        if (window.clearChatAttachedFiles) {
            window.clearChatAttachedFiles();
        }
    }
}

async function addChatMessage(role, content, isThinking = false, checkDuplicates = true, messageId = null) {
    // SAFETY CHECK: Ensure UnifiedMessageRenderer is loaded before proceeding
    if (typeof UnifiedMessageRenderer === 'undefined') {
        console.error('[addChatMessage] UnifiedMessageRenderer not loaded yet - deferring render');
        setTimeout(() => addChatMessage(role, content, isThinking, checkDuplicates, messageId), 100);
        return;
    }

    const threadId = ThreadManager.currentThreadId;

    // CRITICAL: Await async render (now handles duplicates and tool_result skipping)
    const messageDiv = await UnifiedMessageRenderer.render(
        '#ai-chat-messages',
        role === 'ai' ? 'assistant' : role,
        content,
        {
            isThinking: isThinking,
            scrollToBottom: autoScrollEnabled,
            threadId: threadId,
            syncToBackend: false,
            checkDuplicates: checkDuplicates,  // Pass through (false for historical, true for real-time)
            messageId: messageId || null  // CRITICAL: Pass message ID from database
        }
    );

    if (!messageDiv) {
        console.log('[Prime] Message rendering skipped (duplicate or tool_result-only)');
        return null;
    }

    return messageDiv;
}

// ==================== MESSAGE POPUP FUNCTIONS ====================
function openMessagePopup(role, content) {
    const overlay = document.getElementById('message-popup-overlay');
    const body = document.getElementById('message-popup-body');
    const titleText = document.getElementById('message-popup-title-text');

    titleText.textContent = 'Message Details';

    if (role === 'assistant') {
        console.log('🎨 Rendering popup content...');

        if (!window.USE_BASIC_RENDERER && typeof TwoRuleStreamProcessor !== 'undefined') {
            try {
                console.log('🎨 Using TwoRuleStreamProcessor for popup...');
                body.innerHTML = '';
                const processor = new TwoRuleStreamProcessor(body);
                processor.processChunk(content);

                if (typeof processor.finalize === 'function') {
                    processor.finalize();
                } else if (typeof processor.complete === 'function') {
                    processor.complete();
                }

                if (!body.innerHTML || body.innerHTML.trim() === '') {
                    console.warn('[WARN] Visualization engine produced empty popup content, using basic renderer');
                    body.innerHTML = renderBasicMarkdown(content);
                }
            } catch (error) {
                console.error('❌ Visualization engine error in popup:', error);
                console.log('↩️ Falling back to basic markdown renderer');
                body.innerHTML = renderBasicMarkdown(content);
            }
        } else {
            console.log('📝 Using basic markdown renderer for popup');
            body.innerHTML = renderBasicMarkdown(content);
        }

        if (!body.innerHTML || body.innerHTML.trim() === '') {
            console.error('❌ All popup rendering methods failed! Using raw text.');
            body.textContent = content;
        }

        console.log('✅ Popup content rendered successfully');
    } else {
        body.innerHTML = content;
    }

    overlay.dataset.content = content;

    overlay.classList.add('active');

    overlay.onclick = (e) => {
        if (e.target === overlay) {
            closeMessagePopup();
        }
    };
}

function closeMessagePopup() {
    const overlay = document.getElementById('message-popup-overlay');
    overlay.classList.remove('active');
}

function copyMessageContent() {
    const overlay = document.getElementById('message-popup-overlay');
    const content = overlay.dataset.content;

    const temp = document.createElement('div');
    temp.innerHTML = content;
    const text = temp.textContent || temp.innerText;

    navigator.clipboard.writeText(text).then(() => {
        showNotification('Message copied to clipboard!', 'success');
    });
}

function removeThinkingIndicator() {
    const thinking = document.querySelector('.ai-message.thinking');
    if (thinking) thinking.remove();
}

// ==================== STATUS INDICATOR FUNCTIONS ====================
function updateAIStatusIndicator(status) {
    const primeIcon = document.querySelector('.ai-chat-title .ai-icon');
    if (primeIcon) {
        primeIcon.classList.remove('status-thinking', 'status-tool-running', 'status-tool-success', 'status-writing');

        if (status) {
            primeIcon.classList.add(`status-${status}`);
        }

        console.log(`[STATUS] Prime AI icon status: ${status || 'idle'}`);
    }

    // REMOVED: No longer update all agent icons - each agent manages its own status
    // Prime chat should only update its own icon, not all agent icons in Command Center
}

function clearAIStatusIndicator() {
    updateAIStatusIndicator(null);
    if (typeof AgentStatusIndicator !== 'undefined') {
        AgentStatusIndicator.clear(null);
    }
}

function updateAIChatContext(tabId) {
    console.log(`🔄 Updating AI context for tab: ${tabId}`);
}

// ==================== THEME TOGGLE ====================
function initThemeToggle() {
    if (window._themeToggleInitialized) {
        console.warn('Theme toggle already initialized, skipping...');
        return;
    }

    const toggleBtn = document.getElementById('theme-toggle-btn-sidebar');
    if (!toggleBtn) {
        console.warn('Theme toggle button not found');
        return;
    }

    window._themeToggleInitialized = true;
    console.log('✅ Initializing theme toggle...');

    const html = document.documentElement;
    if (!html.getAttribute('data-theme')) {
        html.setAttribute('data-theme', 'dark');
        console.log('✅ Default theme set to: dark');
    }

    toggleBtn.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        html.setAttribute('data-theme', newTheme);
        AppState.theme = newTheme;

        if (window.sidebarVisualizationState) {
            window.sidebarVisualizationState.currentTheme = newTheme;
            window.sidebarVisualizationState.mermaidTheme = newTheme;
        }

        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                startOnLoad: false,
                theme: newTheme,
                securityLevel: 'loose',
                fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'
            });
        }

        const icon = toggleBtn.querySelector('i');
        icon.className = newTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';

        showNotification(`Switched to ${newTheme} theme`, 'info');
    });
}

/**
 * Toggle view mode dropdown menu for Prime chat
 */
function toggleViewModeMenuPrime() {
    const menu = document.getElementById('prime-view-mode-menu');
    if (!menu) return;

    // Close agent dropdowns if any
    document.querySelectorAll('.view-mode-dropdown.show').forEach(dropdown => {
        if (dropdown.id !== 'prime-view-mode-menu') {
            dropdown.classList.remove('show');
        }
    });

    // Toggle Prime dropdown
    menu.classList.toggle('show');
}

/**
 * Set view mode for Prime chat
 * @param {string} mode - View mode to set
 */
function setViewModePrime(mode) {
    primeViewMode = mode;

    // Update button icon and title
    const btn = document.getElementById('prime-view-mode-btn');
    const icon = document.getElementById('prime-view-mode-icon');
    if (icon) {
        const modeIcons = {
            'all-collapsed': 'fa-list',
            'all-expanded': 'fa-expand-alt',
            'ai-collapsed': 'fa-robot',
            'ai-expanded': 'fa-bolt',
            'ai-user': 'fa-users'
        };
        icon.className = `fas ${modeIcons[mode]}`;
    }

    // Update hover text with current mode
    if (btn) {
        const modeNames = {
            'all-collapsed': 'All Collapsed',
            'all-expanded': 'All Expanded',
            'ai-collapsed': 'AI + Tools Collapsed',
            'ai-expanded': 'AI + Tools Expanded',
            'ai-user': 'AI + User Only'
        };
        btn.title = `Change View Mode\nCurrent: ${modeNames[mode]}`;
    }

    // Update active state in menu
    const menu = document.getElementById('prime-view-mode-menu');
    if (menu) {
        menu.querySelectorAll('.view-mode-item').forEach(item => {
            if (item.dataset.mode === mode) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    // Close dropdown
    if (menu) {
        menu.classList.remove('show');
    }

    // Apply view mode to all messages
    applyViewModeToPrime(mode);

    console.log(`📐 [PrimeAI] View mode: ${mode}`);
}

/**
 * Legacy function - cycle through view modes (for backward compatibility)
 */
function cycleExpandModePrime() {
    const modes = ['all-collapsed', 'all-expanded', 'ai-collapsed', 'ai-expanded', 'ai-user'];
    const currentIndex = modes.indexOf(primeViewMode);
    const nextIndex = (currentIndex + 1) % modes.length;
    const nextMode = modes[nextIndex];

    setViewModePrime(nextMode);
}

/**
 * Apply view mode to Prime messages
 * @param {string} mode - View mode
 */
function applyViewModeToPrime(mode) {
    const messagesContainer = document.getElementById('ai-chat-messages');
    if (!messagesContainer) return;

    const messages = messagesContainer.querySelectorAll('.ai-message');

    messages.forEach(message => {
        const isAI = message.classList.contains('assistant');
        const isUser = message.classList.contains('user');
        const isThinking = message.classList.contains('thinking-bubble');
        const isTool = message.classList.contains('tool-bubble') || message.classList.contains('tool');

        // Reset classes and visibility
        message.classList.remove('expanded', 'collapsed');
        message.style.display = '';

        switch (mode) {
            case 'all-collapsed':
                // Show all - tools collapsed
                message.classList.add('collapsed');
                break;

            case 'all-expanded':
                // Show all - expand all
                message.classList.add('expanded');
                break;

            case 'ai-collapsed':
                // Show AI only - collapsed tools
                if (isAI) {
                    message.classList.add('expanded');
                } else if (isTool) {
                    message.classList.add('collapsed');
                } else if (isUser || isThinking) {
                    message.style.display = 'none';
                }
                break;

            case 'ai-expanded':
                // Show AI only - expanded tools
                if (isAI || isTool) {
                    message.classList.add('expanded');
                } else if (isUser || isThinking) {
                    message.style.display = 'none';
                }
                break;

            case 'ai-user':
                // Show AI and user - no tools/no tool results
                if (isAI || isUser) {
                    message.classList.add('expanded');
                } else if (isTool || isThinking) {
                    message.style.display = 'none';
                }
                break;
        }
    });
}

/**
 * Legacy function - now just calls cycleExpandModePrime
 */
function toggleThinkingToolBubblesPrime() {
    // For backward compatibility, just cycle to next mode
    cycleExpandModePrime();
}

// ========================================
// EXPORTS - Make functions globally accessible
// ========================================

// Dummy function for compatibility (resize is handled inside initChatPanel)
function initChatPanelResize() {
    console.log('[CHAT PANEL] Resize functionality already initialized in initChatPanel()');
}

/**
 * Unload thread from Prime AI without closing Prime
 */
function unloadThreadFromPrime() {
    console.log('[PrimeAI] Unloading thread from Prime...');

    // STEP 1: Clear message bubbles (but keep welcome container and processing indicator)
    const messagesContainer = document.getElementById('ai-chat-messages');
    if (messagesContainer) {
        // Remove only message elements, keep welcome-container and processing-indicator
        const messageElements = messagesContainer.querySelectorAll('.message-wrapper, .user-message, .ai-message, .tool-message, .empty-state');
        messageElements.forEach(el => el.remove());
        console.log('[PrimeAI] Cleared message bubbles');
    }

    // STEP 2: Show welcome container (with greeting, tip, and buttons)
    const welcomeContainer = document.getElementById('prime-welcome-container');
    if (welcomeContainer) {
        welcomeContainer.style.display = 'flex';

        // Initialize with fresh time-based greeting and random tip
        if (typeof ThreadManagerWelcome !== 'undefined' && typeof ThreadManagerWelcome.initWelcomeMessage === 'function') {
            ThreadManagerWelcome.initWelcomeMessage('prime');
        }

        console.log('[PrimeAI] Shown welcome container with greeting and tip');
    } else {
        console.warn('[PrimeAI] Welcome container not found - showing fallback empty state');
    }

    // STEP 3: Clear thread info and show selector
    const threadInfoContainer = document.getElementById('prime-thread-info');
    if (threadInfoContainer && typeof ThreadManager !== 'undefined' && typeof ThreadManager.renderThreadInfoContainer === 'function') {
        threadInfoContainer.innerHTML = ThreadManager.renderThreadInfoContainer('prime', null, false);
        threadInfoContainer.style.display = 'block'; // Show container with selector
        console.log('[PrimeAI] Reset thread info and shown selector');
    } else {
        console.warn('[PrimeAI] Failed to reset thread info:', {
            containerFound: !!threadInfoContainer,
            threadManagerExists: typeof ThreadManager !== 'undefined',
            renderFunctionExists: typeof ThreadManager?.renderThreadInfoContainer === 'function'
        });
    }

    // STEP 4: Hide input container (expandable Prime-style input system)
    const inputContainer = document.querySelector('.ai-chat-input-container');
    if (inputContainer) {
        inputContainer.style.display = 'none';
        console.log('[PrimeAI] Hidden input container (empty state)');
    }

    // STEP 5: Clear input
    const inputTextarea = document.getElementById('ai-chat-input');
    if (inputTextarea) {
        inputTextarea.value = '';
    }

    const attachedFilesContainer = document.getElementById('ai-chat-attached-files');
    if (attachedFilesContainer) {
        attachedFilesContainer.innerHTML = '';
    }

    // STEP 6: Clear session/thread ID in AppState
    if (typeof AppState !== 'undefined') {
        AppState.sessionId = null;
        AppState.currentThreadId = null;
        console.log('[PrimeAI] Cleared AppState session/thread ID');
    }

    // STEP 7: Clear ThreadManager current thread
    if (typeof ThreadManager !== 'undefined') {
        ThreadManager.currentThreadId = null;
        console.log('[PrimeAI] Cleared ThreadManager current thread');
    }

    // STEP 8: Abort any active streaming
    if (typeof window.abortController !== 'undefined' && window.abortController.prime) {
        try {
            window.abortController.prime.abort();
            delete window.abortController.prime;
            console.log('[PrimeAI] Aborted active stream');
        } catch (e) {
            console.warn('[PrimeAI] Failed to abort stream:', e);
        }
    }

    // STEP 9: Dispatch unload event
    const unloadEvent = new CustomEvent('thread-unloaded', {
        detail: { location: 'prime' }
    });
    document.dispatchEvent(unloadEvent);

    console.log('[PrimeAI] ✅ Thread unloaded from Prime');
}

// ==================== PRIME CHAT SCROLL CONTROLS ====================

const PrimeChat = {
    /**
     * Scroll to top of messages container
     */
    scrollToTop() {
        const messagesContainer = document.querySelector('.ai-chat-messages');
        if (!messagesContainer) return;

        messagesContainer.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    },

    /**
     * Scroll to bottom of messages container
     */
    scrollToBottom() {
        const messagesContainer = document.querySelector('.ai-chat-messages');
        if (!messagesContainer) return;

        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight + LAYOUT_CONSTANTS.SCROLL_CLEARANCE;
        }, LAYOUT_CONSTANTS.AUTO_SCROLL_DELAY);
    },

    /**
     * Toggle auto-scroll functionality for Prime chat
     */
    toggleAutoScroll() {
        autoScrollEnabled = !autoScrollEnabled;
        const btn = document.getElementById('prime-autoscroll-btn');

        if (autoScrollEnabled) {
            btn?.classList.add('active');
            btn?.setAttribute('title', 'Auto-scroll enabled - Click to disable');
            this.scrollToBottom();
        } else {
            btn?.classList.remove('active');
            btn?.setAttribute('title', 'Auto-scroll disabled - Click to enable');
        }

        console.log(`[PrimeChat] Auto-scroll: ${autoScrollEnabled ? 'enabled' : 'disabled'}`);
    }
};

// Create PrimeAI namespace object for cleaner API
const PrimeAI = {
    cycleExpandMode: cycleExpandModePrime,
    toggleThinkingToolBubbles: toggleThinkingToolBubblesPrime,
    toggleViewModeMenu: toggleViewModeMenuPrime,
    setViewMode: setViewModePrime,
    unloadThread: unloadThreadFromPrime,

    // Lock system methods
    showLockBanner(lockedByDisplayName) {
        const panel = document.getElementById('ai-chat-panel');
        const messagesContainer = document.getElementById('ai-chat-messages');
        if (!panel || !messagesContainer) return;

        // Add locked state to panel
        panel.classList.add('locked-by-other');

        // Create lock banner if it doesn't exist
        let banner = messagesContainer.querySelector('.prime-lock-banner');
        if (!banner) {
            banner = document.createElement('div');
            banner.className = 'prime-lock-banner';
            banner.innerHTML = `<i class="fas fa-lock"></i> Locked by ${lockedByDisplayName || 'another user'}`;
            messagesContainer.appendChild(banner);
        } else {
            banner.innerHTML = `<i class="fas fa-lock"></i> Locked by ${lockedByDisplayName || 'another user'}`;
            banner.style.display = 'flex';
        }

        console.log(`🔒 [Prime] Locked by ${lockedByDisplayName}`);
    },

    hideLockBanner() {
        const panel = document.getElementById('ai-chat-panel');
        const messagesContainer = document.getElementById('ai-chat-messages');
        if (!panel || !messagesContainer) return;

        // Remove locked state
        panel.classList.remove('locked-by-other');

        // Hide banner
        const banner = messagesContainer.querySelector('.prime-lock-banner');
        if (banner) {
            banner.style.display = 'none';
        }

        console.log(`🔓 [Prime] Unlocked`);
    },

    disableInput() {
        const input = document.getElementById('ai-chat-input');
        if (input) {
            input.disabled = true;
            input.placeholder = 'This chat is locked by another user...';
            console.log(`⛔ [Prime] Input disabled`);
        }
    },

    enableInput() {
        const input = document.getElementById('ai-chat-input');
        if (input) {
            input.disabled = false;
            input.placeholder = 'Message AI...';
            console.log(`✅ [Prime] Input enabled`);
        }
    }
};

// ==================== SCROLL CONTROLS VISIBILITY ====================
// Show scroll controls only when messages exist
function updateScrollControlsVisibility() {
    const messagesContainer = document.getElementById('ai-chat-messages');
    if (!messagesContainer) return;

    // Check if any messages exist (ai-message class is used by UnifiedMessageRenderer)
    const messageCount = messagesContainer.querySelectorAll('.ai-message').length;

    if (messageCount > 0) {
        messagesContainer.classList.add('has-messages');
    } else {
        messagesContainer.classList.remove('has-messages');
    }
}

// Observe messages container for changes
function initScrollControlsObserver() {
    const messagesContainer = document.getElementById('ai-chat-messages');
    if (!messagesContainer) return;

    // Initial check
    updateScrollControlsVisibility();

    // Watch for DOM changes (messages added/removed)
    const observer = new MutationObserver(() => {
        updateScrollControlsVisibility();
    });

    observer.observe(messagesContainer, {
        childList: true,
        subtree: true
    });
}

// Initialize observer when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initScrollControlsObserver);
} else {
    initScrollControlsObserver();
}

window.initChatPanel = initChatPanel;
window.initChatPanelResize = initChatPanelResize;
window.initThemeToggle = initThemeToggle;
window.PrimeChat = PrimeChat;
window.PrimeAI = PrimeAI;
window.updateScrollControlsVisibility = updateScrollControlsVisibility;

// Close Prime dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('#prime-view-mode-btn') && !e.target.closest('#prime-view-mode-menu')) {
        const menu = document.getElementById('prime-view-mode-menu');
        if (menu) {
            menu.classList.remove('show');
        }
    }
});
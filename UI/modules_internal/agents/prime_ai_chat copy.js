


// ==================== AI CHAT PANEL ====================
// Auto-scroll state
let autoScrollEnabled = true;

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
        // console.log(`[AUTO-SCROLL] Scrolled to: ${messagesContainer.scrollTop} (height: ${messagesContainer.scrollHeight})`);
    }, LAYOUT_CONSTANTS.AUTO_SCROLL_DELAY);
}

// Toggle auto-scroll functionality
function toggleAutoScroll() {
    autoScrollEnabled = !autoScrollEnabled;
    const btn = document.getElementById('ai-chat-autoscroll-btn');

    if (autoScrollEnabled) {
        btn?.classList.add('active');
        btn?.setAttribute('title', 'Auto-scroll enabled - Click to disable');
        // Scroll to bottom immediately when re-enabled
        performAutoScroll();
    } else {
        btn?.classList.remove('active');
        btn?.setAttribute('title', 'Auto-scroll disabled - Click to enable');
    }

    // console.log(`[AUTO-SCROLL] ${autoScrollEnabled ? 'Enabled' : 'Disabled'}`);
}

// No longer needed - flex layout handles space automatically
function updateMessagesBottomPadding() {
    // Flex layout naturally pushes messages up when input expands
    // Just trigger auto-scroll
    performAutoScroll();
}

// No longer needed - flex layout handles space automatically
function resetMessagesBottomPadding() {
    // Flex layout naturally gives messages more space when input collapses
    // Nothing to do
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

    // Initialize textarea height
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, LAYOUT_CONSTANTS.MAX_INPUT_HEIGHT) + 'px';

    // Initialize without padding (messages go to bottom)
    // Only reset if welcome container is NOT visible
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
            // Clear previous timeout
            clearTimeout(scrollTimeout);

            // Debounce scroll detection (only act after scrolling stops)
            scrollTimeout = setTimeout(() => {
                const currentScrollTop = messagesContainer.scrollTop;
                const maxScroll = messagesContainer.scrollHeight - messagesContainer.clientHeight;
                const distanceFromBottom = maxScroll - currentScrollTop;

                // Only disable if user scrolled UP and is MORE than threshold from bottom
                if (currentScrollTop < lastScrollTop && distanceFromBottom > LAYOUT_CONSTANTS.SCROLL_THRESHOLD && autoScrollEnabled) {
                    autoScrollEnabled = false;
                    const btn = document.getElementById('ai-chat-autoscroll-btn');
                    btn?.classList.remove('active');
                    btn?.setAttribute('title', 'Auto-scroll disabled - Click to enable');
                    // console.log(`[AUTO-SCROLL] Disabled (user scrolled up - distance from bottom: ${distanceFromBottom}px)`);
                }

                lastScrollTop = currentScrollTop;
            }, LAYOUT_CONSTANTS.SCROLL_DEBOUNCE); // Reduced from 150ms for faster response
        });
    }

    // Note: AI Prime toggle button is handled in initRightSidebar()
    closeBtn.addEventListener('click', toggleChat);
    sendBtn.addEventListener('click', sendChatMessage);

    // ==================== 4-STATE SLIDING INPUT SYSTEM ====================
    const inputContainer = document.querySelector('.ai-chat-input-container');
    const messagesArea = document.querySelector('.ai-chat-messages');
    let isExpanded = false;

    // STATE 4: Expand input area (click on bar or focus input)
    function expandInputArea() {
        if (isExpanded) return;

        isExpanded = true;
        inputContainer?.classList.add('expanded');

        // Auto-scroll after expansion (flex layout handles space automatically)
        setTimeout(() => {
            performAutoScroll();
        }, 100);

        // Focus input
        input?.focus();

        console.log('[STATE 4] Input area expanded - flex layout handles space');
    }

    // STATE 1: Collapse input area (blur with empty input)
    function collapseInputArea() {
        if (!isExpanded) return;

        isExpanded = false;
        inputContainer?.classList.remove('expanded');

        console.log('[STATE 1] Input area collapsed - messages naturally expand');
    }

    // Click on collapsed bar to expand (STATE 1 ? STATE 4)
    inputContainer.addEventListener('click', (e) => {
        if (!isExpanded && e.target === inputContainer) {
            expandInputArea();
        }
    });

    // Focus input to expand (STATE 1 ? STATE 4)
    input.addEventListener('focus', () => {
        expandInputArea();
    });

    // Blur to collapse (STATE 4 ? STATE 1) - only if empty
    input.addEventListener('blur', () => {
        setTimeout(() => {
            if (document.activeElement !== input && input.value.trim() === '') {
                collapseInputArea();
            }
        }, LAYOUT_CONSTANTS.BLUR_DELAY);
    });

    // After sending message, keep expanded (STATE 4 stays)
    // (Handled by sendChatMessage - don't auto-collapse)            // File attachment button click
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
        // Reset height to auto to get the correct scrollHeight
        input.style.height = 'auto';

        // Set height to scrollHeight but respect min/max
        const newHeight = Math.min(input.scrollHeight, LAYOUT_CONSTANTS.MAX_INPUT_HEIGHT);
        input.style.height = newHeight + 'px';

        // Flex layout automatically handles space - just scroll if needed
        if (inputContainer?.classList.contains('expanded') && autoScrollEnabled) {
            setTimeout(() => performAutoScroll(), 0);
        }
    });

    // Handle paste events (sometimes needed for correct height calculation)
    input.addEventListener('paste', (e) => {
        setTimeout(() => {
            input.style.height = 'auto';
            const newHeight = Math.min(input.scrollHeight, LAYOUT_CONSTANTS.MAX_INPUT_HEIGHT);
            input.style.height = newHeight + 'px';
        }, 0);
    });

    function handleFileSelection(files) {
        // Add files to attachedFiles array
        for (let file of files) {
            // Check file type
            const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
            if (!validTypes.includes(file.type)) {
                showNotification(`Invalid file type: ${file.name}. Only PDF and images are supported.`, 'error');
                continue;
            }

            // Check file size (32MB max for PDFs, 5MB for images)
            const maxSize = file.type === 'application/pdf' ? 32 * 1024 * 1024 : 5 * 1024 * 1024;
            if (file.size > maxSize) {
                showNotification(`File too large: ${file.name}. Max size: ${maxSize / 1024 / 1024}MB`, 'error');
                continue;
            }

            attachedFiles.push(file);
        }

        updateAttachedFilesUI();
        fileInput.value = ''; // Reset input
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

        // Input container height changed - update padding if active
        const inputContainer = document.querySelector('.ai-chat-input-container');
        if (inputContainer?.classList.contains('active')) {
            setTimeout(() => updateMessagesBottomPadding(), 0);
        }
    }

    // Store attachedFiles in global scope so sendChatMessage can access it
    window.chatAttachedFiles = attachedFiles;
    window.clearChatAttachedFiles = () => {
        attachedFiles = [];
        updateAttachedFilesUI();

        // Input container height changed - update padding if active
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

    // Resizable chat panel with drag handle (horizontal only)
    let isResizing = false;
    let startX = 0;
    let startWidth = 0;

    // Restore saved width on load
    const savedWidth = localStorage.getItem('ai_chat_panel_width');
    if (savedWidth) {
        document.documentElement.style.setProperty('--chat-width', savedWidth);
    }

    panel.addEventListener('mousedown', (e) => {
        // Check if click is on the left border resize area (within 6px)
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

        const deltaX = startX - e.clientX; // Reverse: dragging left increases width
        const newWidth = startWidth + deltaX;

        // Constrain between min and max width
        if (newWidth >= 300 && newWidth <= 800) {
            // Update CSS variable - grid will automatically adjust main-content
            document.documentElement.style.setProperty('--chat-width', newWidth + 'px');
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = 'default';

            // Save panel width to localStorage
            const currentWidth = getComputedStyle(document.documentElement)
                .getPropertyValue('--chat-width').trim();
            localStorage.setItem('ai_chat_panel_width', currentWidth);
        }
    });

    // Initialize ResizeObserver for input container
    initInputResizeObserver();
}

// Watch for input container size changes (textarea expand, file chips, feedback container)
function initInputResizeObserver() {
    const inputContainer = document.querySelector('.ai-chat-input-container');
    const messagesContainer = document.querySelector('.ai-chat-messages');

    if (!inputContainer || !messagesContainer) {
        console.warn('[RESIZE OBSERVER] Input or messages container not found');
        return;
    }

    const resizeObserver = new ResizeObserver(entries => {
        // Flex layout automatically handles space
        // Just auto-scroll if needed
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

    console.log(' Chat toggled:', AppState.chatOpen ? 'Open' : 'Collapsed');
}

// ==================== PLATFORM STATUS ====================
async function loadPlatformStatus() {
    const grid = document.getElementById('platform-status-grid');

    // Show loading state
    grid.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Loading platforms...</div>';

    if (!AppState.isConnected) {
        grid.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Backend disconnected</div>';
        return;
    }

    try {
        // Fetch tool list from Flask
        const response = await fetch(`${API_BASE_URL}/api/agent/tools`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Extract unique platforms from tools
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

        // Render platforms
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

        console.log(`Loaded ${platforms.length} platforms with ${data.tools.length} tools`);

    } catch (error) {
        console.error(' Failed to load platforms:', error);
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

// Get platform icon based on name
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
    return 'fa-cube'; // Default icon
}

// Get platform color based on name
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
    return '#6c5ce7'; // Default color
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

    // Check for attached files
    const hasFiles = window.chatAttachedFiles && window.chatAttachedFiles.length > 0;

    // FIX: Try to send anyway, even if connection check failed
    // Connection check might fail due to CORS from file:// but actual requests work
    if (!AppState.isConnected) {
        console.warn('[WARN] Connection check reported disconnected, but trying anyway...');
        // Don't return - try to send the message
    }

    // Clear input immediately
    input.value = '';

    // Reset textarea height after clearing
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 300) + 'px';

    // CRITICAL: Get or create thread_slug (timestamp-based for database compatibility)
    // If ThreadManager has a loaded thread, use its thread_slug
    // Otherwise, create a new timestamp-based thread_slug for Prime
    let currentThreadId;
    if (window.ThreadManager && window.ThreadManager.currentThreadId) {
        currentThreadId = window.ThreadManager.currentThreadId;
        console.log(`✅ [THREAD] Using loaded thread: ${currentThreadId}`);
    } else {
        // Generate new timestamp-based thread_slug for Prime location
        currentThreadId = String(Date.now());
        console.log(`✅ [THREAD] Generated new thread_slug for Prime: ${currentThreadId}`);
    }

    // Build message content with file attachments if present
    let messageContent = message;
    if (hasFiles) {
        const fileList = window.chatAttachedFiles.map(f => f.name).join(', ');
        messageContent = `${message}\n\n[ATTACH] Attached: ${fileList}`;
    }

    // CRITICAL: Add user message to UI (UnifiedMessageRenderer will add to MessageStore automatically)
    // UnifiedMessageRenderer.render() handles MessageStore.addMessage() with deduplication
    // No duplicate addChatMessage() call needed - UnifiedMessageRenderer handles everything
    const userMessageDiv = UnifiedMessageRenderer.render(
        '#ai-chat-messages',
        'user',
        messageContent,
        {
            isThinking: false,
            scrollToBottom: autoScrollEnabled,
            threadId: currentThreadId,
            syncToBackend: false  // Don't sync yet - backend will save when processing
        }
    );

    if (!userMessageDiv) {
        console.error('[Prime] Failed to render user message');
        return;
    }

    console.log(`✅ [MessageStore] User message added via UnifiedMessageRenderer`);

    // Use same thread_slug for BOTH endpoints (session_id and thread_slug must match)
    const sessionId = currentThreadId;  // Thread slug for isolation

    // Update status indicator (no visual thinking dots)
    if (typeof AgentStatusIndicator !== 'undefined') {
        AgentStatusIndicator.update('thinking', null);  // null = Prime AI
    }

    const startTime = Date.now();

    try {
        // Check if we need to use file upload endpoint
        if (hasFiles) {
            console.log('[ATTACH] Sending message with file attachments...');
            await sendChatMessageWithFiles(message, sessionId, startTime);
            return;
        }

        // ENHANCED: Include tool configuration in request
        console.log(' Preparing chat request with tool support...');
        console.log(`[CHART] ${ToolManager.availableTools.length} tools available for AI use`);

        // GET CURRENT CONVERSATION HISTORY with proper tool_use/tool_result splitting
        // CRITICAL: Use buildConversationHistoryForAPI to properly format for Anthropic
        // PHASE 2: Read from MessageStore instead of AppState.chatMessages
        const messagesFromStore = window.MessageStore.getMessages(currentThreadId);
        console.log(`📦 [MessageStore] Retrieved ${messagesFromStore.length} messages from thread ${currentThreadId}`);

        let conversationHistory = [];
        try {
            // Verify buildConversationHistoryForAPI exists
            if (typeof buildConversationHistoryForAPI !== 'function') {
                throw new Error('buildConversationHistoryForAPI not loaded');
            }

            conversationHistory = buildConversationHistoryForAPI(
                messagesFromStore.filter(msg => {
                    // Keep messages with non-empty content
                    if (typeof msg.content === 'string') {
                        return msg.content && msg.content.trim().length > 0;
                    }
                    if (Array.isArray(msg.content)) {
                        return msg.content.length > 0;
                    }
                    return false;
                })
            );
            console.log(`✅ Sending ${conversationHistory.length} messages in conversation history (properly formatted for Anthropic API)`);
        } catch (error) {
            console.error('[ERROR] Failed to build conversation history:', error);
            // Fallback: Use basic format without splitting tool_use/tool_result
            conversationHistory = messagesFromStore
                .filter(msg => msg.content && (typeof msg.content === 'string' ? msg.content.trim().length > 0 : msg.content.length > 0))
                .map(msg => ({
                    role: msg.role,
                    content: typeof msg.content === 'string' ? [{ type: 'text', text: msg.content }] : msg.content
                }));
            console.warn(`⚠️ Using fallback conversation format (${conversationHistory.length} messages)`);
        }

        // Gather browser context (timezone, location, weather, etc.)
        let browserContext = {};
        try {
            browserContext = await BrowserContext.getContext();
            console.log('[OK] Browser context gathered:', browserContext);
        } catch (error) {
            console.warn('[WARN] Could not gather browser context:', error);
        }

        // Load user preferences and memories from backend
        let userContext = {
            nickname: '',
            communication_style: 'professional',
            detail_level: 'standard',
            location: '',
            timezone: '',
            country: '',
            auth_platform: null,  // CRITICAL: 'google' or 'microsoft'
            google_authenticated: false,
            microsoft_authenticated: false,
            preferred_tools: [],
            custom_preferences: [],
            memories: [],
            // Add browser context
            browser: browserContext
        };

        try {
            const prefsResponse = await fetch(`${API_BASE_URL}/api/user/preferences`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });

            if (prefsResponse.ok) {
                const prefsData = await prefsResponse.json();
                const data = prefsData.data || prefsData;  // Handle both response formats

                // CRITICAL: Determine which platform user is authenticated with
                const authPlatform = data.auth_platform || null;  // 'google' or 'microsoft'
                const googleConnected = data.google_oauth_connected || false;
                const microsoftConnected = data.microsoft_oauth_connected || false;

                userContext = {
                    nickname: data.nickname || '',
                    communication_style: data.communication_style || 'professional',
                    detail_level: data.detail_level || 'standard',
                    location: data.use_manual_location ? data.manual_location_override : data.detected_city,
                    timezone: data.use_manual_timezone ? data.manual_timezone_override : data.detected_timezone,
                    country: data.detected_country || '',
                    auth_platform: authPlatform,  // CRITICAL: Tell AI which platform user is using
                    google_authenticated: authPlatform === 'google' || googleConnected,
                    microsoft_authenticated: authPlatform === 'microsoft' || microsoftConnected,
                    preferred_tools: data.preferred_tools ? (typeof data.preferred_tools === 'string' ? JSON.parse(data.preferred_tools) : data.preferred_tools) : [],
                    custom_preferences: data.custom_preferences ? (typeof data.custom_preferences === 'string' ? JSON.parse(data.custom_preferences) : data.custom_preferences) : [],
                    memories: data.ai_memories ? (typeof data.ai_memories === 'string' ? JSON.parse(data.ai_memories) : data.ai_memories) : [],
                    // Preserve browser context gathered earlier
                    browser: browserContext
                };
                console.log('[OK] User context loaded:', userContext);

                // Log browser context details
                if (browserContext.geolocation?.available) {
                    console.log(`[OK] Browser location: ${browserContext.geolocation.latitude.toFixed(4)}, ${browserContext.geolocation.longitude.toFixed(4)}`);
                    if (browserContext.weather?.available) {
                        console.log(`[OK] Weather: ${browserContext.weather.weatherDescription}, ${browserContext.weather.temperature}C`);
                    }
                }
                console.log(`[OK] Timezone: ${browserContext.locale?.timezone || 'unknown'}, Time: ${browserContext.datetime?.localTime || 'unknown'}`);
                console.log(` CRITICAL: User authenticated with: ${authPlatform || 'local'} (Google: ${userContext.google_authenticated}, Microsoft: ${userContext.microsoft_authenticated})`);
            } else {
                console.warn(`[WARN] Could not load user context: ${prefsResponse.status} ${prefsResponse.statusText}`);
            }
        } catch (error) {
            console.warn('[WARN] Could not load user context:', error);
            // Continue with default empty context
        }

        // STREAMING: Use fetch-event-stream for SSE
        const requestBody = {
            message: message,
            session_id: currentThreadId,       // Use thread slug consistently
            thread_id: currentThreadId,        // Use thread slug consistently
            thread_slug: currentThreadId,      // Explicit thread slug for backend
            conversation_history: conversationHistory,
            user_context: userContext,  // NEW: Include user personalisation
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
                streaming: true  // Enable streaming
            }
        };                // Make POST request to start agent processing
        // Use agent ID '1' for main chat interface
        const agentId = '1';

        // Step 1: Start the agent (POST to /start)
        console.log(' Starting agent processing...');
        const startResponse = await fetch(`${API_BASE_URL}/api/agent/agent/${agentId}/start`, {
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

        // Step 2: Connect to SSE stream to receive response
        console.log(' Connecting to SSE stream...');

        // PROMPT INJECTION: Get selected prompts from prompt library
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

        // CRITICAL FIX: Use thread_slug for stream isolation (standardized with currentThreadId)
        const threadSlug = currentThreadId;
        const streamUrl = `${API_BASE_URL}/api/agent/stream/${agentId}?thread_slug=${threadSlug}${promptParams}`;
        console.log(`[Stream] Connecting with thread_slug: ${threadSlug}`);
        const response = await fetch(streamUrl);

        if (!response.ok) {
            throw new Error(`Stream error! status: ${response.status}`);
        }

        // Check if response is streaming (text/event-stream) or JSON
        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('text/event-stream')) {
            // HANDLE STREAMING RESPONSE
            console.log(' Receiving streamed response...');

            // DON'T remove thinking indicator yet - it will be replaced when first content arrives
            // removeThinkingIndicator(); // REMOVED - keep bouncing dots visible

            // Get chat messages container
            const chatMessages = document.getElementById('ai-chat-messages');
            if (!chatMessages) {
                console.error('[ERROR] Could not find ai-chat-messages element!');
                throw new Error('Chat messages container not found');
            }

            // Each bubble will be added directly to chatMessages (no wrapper container)
            // This allows for independent bubbles with global controls (hide all thinking, etc.)
            let fullResponse = '';
            let fullThinkingContent = '';  // Track ALL thinking content
            let toolsUsed = [];  // Track all tools used (tool_use blocks)
            let toolResults = [];  // Track all tool results (tool_result blocks) - NEW!
            let firstContentReceived = false;
            let thinkingBubble = null;
            let textBubble = null;
            let lastEventType = null;  // Track event type to detect text sequence changes

            // ISOLATION FIX: Thread-specific error tracking (prevents one thread breaking others)
            let threadErrorCount = 0;
            const maxThreadErrors = 10;  // Allow some parse errors before stopping THIS thread
            let threadFailed = false;

            // Reset round counter for new stream
            window._thinkingRoundCounter = 0;
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';  // Buffer for incomplete SSE messages

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                // Decode chunk and add to buffer
                buffer += decoder.decode(value, { stream: true });

                // Split on double newline (SSE message separator)
                const messages = buffer.split('\n\n');

                // Keep the last incomplete message in buffer
                buffer = messages.pop() || '';

                // Process complete messages
                for (const message of messages) {
                    const lines = message.split('\n');
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const jsonStr = line.substring(6).trim();
                                if (jsonStr) {
                                    const data = JSON.parse(jsonStr);

                                    if (data.type === 'thinking_block' || data.type === 'thinking') {
                                        console.log(' [THINKING EVENT] Received thinking content:', data.content?.substring(0, 50) + '...');

                                        // Skip if no actual content
                                        const thinkingText = data.content || data.thinking || '';
                                        if (!thinkingText || thinkingText.trim().length === 0) {
                                            console.log('[WARN] Skipping empty thinking content');
                                            continue;
                                        }

                                        // Update status indicator - thinking (purple pulse)
                                        updateAIStatusIndicator('thinking');

                                        // Remove bouncing dots on first content
                                        if (!firstContentReceived) {
                                            removeThinkingIndicator();
                                            firstContentReceived = true;
                                            console.log('[OK] Removed bouncing dots indicator');
                                        }

                                        // Create thinking bubble if it doesn't exist (and we have content)
                                        if (!thinkingBubble) {
                                            console.log(' Creating new thinking bubble...');
                                            thinkingBubble = document.createElement('div');
                                            thinkingBubble.className = 'ai-message assistant thinking-bubble';

                                            // Create header with BRAIN avatar
                                            const headerDiv = document.createElement('div');
                                            headerDiv.className = 'ai-message-header';

                                            const avatar = document.createElement('div');
                                            avatar.className = 'ai-message-avatar';
                                            avatar.style.background = '#8b5cf6'; // Purple for thinking
                                            avatar.innerHTML = '<i class="fa-solid fa-brain" style="color: white;"></i>'; // BRAIN ICON

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

                                            // Add copy buttons
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

                                            actionsDiv.appendChild(copyBtn);
                                            actionsDiv.appendChild(copyRawBtn);
                                            headerDiv.appendChild(actionsDiv);

                                            // Create content div (NO DEFAULT TEXT)
                                            const contentDiv = document.createElement('div');
                                            contentDiv.className = 'ai-message-content';
                                            // NO default "Processing..." text - only actual thinking content

                                            thinkingBubble.appendChild(headerDiv);
                                            thinkingBubble.appendChild(contentDiv);
                                            thinkingBubble.classList.add('collapsed'); // Start collapsed
                                            chatMessages.appendChild(thinkingBubble); // Add directly to chatMessages
                                            console.log('[OK] Thinking bubble created and added');
                                        }

                                        // Track that we're in a thinking event
                                        lastEventType = 'thinking';

                                        // Append thinking content (streaming) - we already validated it's not empty above
                                        const thinkingContent = thinkingBubble.querySelector('.ai-message-content');

                                        // Accumulate thinking text for markdown rendering
                                        if (!thinkingBubble._fullThinkingText) {
                                            thinkingBubble._fullThinkingText = '';
                                        }
                                        
                                        // AUTO SEPARATOR: Add visual break when new thinking block starts
                                        if (data.delta_type === 'start' && thinkingBubble._fullThinkingText.trim()) {
                                            // New thinking block detected - add separator before it
                                            thinkingBubble._fullThinkingText += '\n\n---\n\n';
                                            console.log('[THINKING] New thinking block detected, added visual separator');
                                        }
                                        
                                        thinkingBubble._fullThinkingText += thinkingText;

                                        // ALSO accumulate for conversation history
                                        fullThinkingContent += thinkingText;                                                // Render markdown (use marked.js if available, fallback to renderBasicMarkdown)
                                        if (window.marked) {
                                            try {
                                                thinkingContent.innerHTML = marked.parse(thinkingBubble._fullThinkingText, {
                                                    breaks: true,
                                                    gfm: true
                                                });
                                            } catch (e) {
                                                console.error('[ERROR] Markdown parse error in thinking:', e);
                                                thinkingContent.innerHTML = renderBasicMarkdown(thinkingBubble._fullThinkingText);
                                            }
                                        } else {
                                            thinkingContent.innerHTML = renderBasicMarkdown(thinkingBubble._fullThinkingText);
                                        }
                                        console.log(' Thinking content updated with markdown, length:', thinkingBubble._fullThinkingText.length);

                                    } else if (data.type === 'tool_use') {
                                        //  FIX: Flush any buffered text content BEFORE showing tool
                                        // This ensures text like "Let me check that..." displays before the tool bubble
                                        // Flush any buffered content from active TwoRule processors
                                        if (window._twoRuleProcessors && window._twoRuleProcessors.size) {
                                            console.log(' Flushing buffered content from active TwoRule processors before tool use...');
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

                                        // CRITICAL FIX: Check multiple field names for tool ID (backend inconsistency)
                                        const toolId = data.tool_id || data.tool_use_id || data.id;
                                        console.log('⚙️ [TOOL_USE EVENT] Tool:', data.tool_name, 'ID:', toolId);
                                        console.log('[CHART] Tool input:', JSON.stringify(data.tool_input).substring(0, 100) + '...');
                                        console.log('[SEARCH] DEBUG - data.tool_id:', data.tool_id, 'data.tool_use_id:', data.tool_use_id, 'data.id:', data.id);

                                        // Update status indicator - tool running (yellow pulse)
                                        updateAIStatusIndicator('tool-running');
                                        if (typeof AgentStatusIndicator !== 'undefined') {
                                            AgentStatusIndicator.update('tool-running', null);
                                        }

                                        // Remove bouncing dots on first content
                                        if (!firstContentReceived) {
                                            removeThinkingIndicator();
                                            firstContentReceived = true;
                                            console.log('[OK] Removed bouncing dots indicator');
                                        }

                                        // Create tool use bubble
                                        const toolBubble = document.createElement('div');
                                        toolBubble.className = 'ai-message assistant tool-bubble';
                                        toolBubble.setAttribute('data-tool-id', toolId);

                                        // Create header with COG avatar
                                        const headerDiv = document.createElement('div');
                                        headerDiv.className = 'ai-message-header';

                                        const avatar = document.createElement('div');
                                        avatar.className = 'ai-message-avatar';
                                        avatar.style.background = '#eab308'; // Yellow for tool running
                                        avatar.innerHTML = '<i class="fas fa-cog" style="color: white;"></i>'; // COG ICON

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

                                        // Add copy buttons
                                        const actionsDiv = document.createElement('div');
                                        actionsDiv.className = 'ai-message-actions';

                                        const copyBtn = document.createElement('button');
                                        copyBtn.className = 'ai-message-copy-btn';
                                        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                                        copyBtn.title = 'Copy tool content';
                                        copyBtn.addEventListener('click', (e) => {
                                            e.stopPropagation();
                                            //  FIX: Copy the CURRENT visible content from the bubble (includes result)
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

                                        actionsDiv.appendChild(copyBtn);
                                        headerDiv.appendChild(actionsDiv);

                                        // Create content div with tool details
                                        const contentDiv = document.createElement('div');
                                        contentDiv.className = 'ai-message-content';
                                        contentDiv.innerHTML = `
                                                    <div style="margin-bottom: 8px;"><strong>Tool:</strong> ${data.name || data.tool_name}</div>
                                                    <pre>${JSON.stringify(data.input || data.tool_input, null, 2)}</pre>
                                                `;

                                        toolBubble.appendChild(headerDiv);
                                        toolBubble.appendChild(contentDiv);
                                        toolBubble.classList.add('collapsed'); // Start collapsed
                                        chatMessages.appendChild(toolBubble); // FIX: Use chatMessages instead of undefined messageContainer

                                        // Track that we're in a tool event
                                        lastEventType = 'tool_use';

                                        // Track tool for conversation history (use consistent toolId)
                                        toolsUsed.push({
                                            name: data.name || data.tool_name,
                                            input: data.input || data.tool_input,
                                            id: toolId
                                        });

                                    } else if (data.type === 'tool_input_complete') {
                                        console.log(' [TOOL_INPUT_COMPLETE EVENT] Updating tool bubble with complete input');
                                        console.log('[CHART] Tool:', data.tool_name);
                                        console.log('[CHART] Tool ID:', data.tool_id);
                                        console.log('[CHART] Input:', data.tool_input);

                                        // Find the tool bubble by tool_id and update its content
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
                                        console.log(' [CONTENT_DELTA EVENT] Received text chunk:', data.text?.substring(0, 50) + '...');
                                        console.log('[CHART] data.text value:', data.text);
                                        console.log('[CHART] data.text type:', typeof data.text);

                                        // Update status indicator - writing content (white pulse)
                                        updateAIStatusIndicator('writing');

                                        // Remove bouncing dots on first content
                                        if (!firstContentReceived) {
                                            removeThinkingIndicator();
                                            firstContentReceived = true;
                                            console.log('[OK] Removed bouncing dots indicator');
                                        }

                                        // CHANGE: Create NEW text bubble when switching from non-text event to text event
                                        // This creates separate bubbles for each text response
                                        if (lastEventType !== 'content_delta' && lastEventType !== null) {
                                            // We've had a thinking/tool event between text events - create new bubble
                                            if (textBubble) {
                                                console.log(' Creating new text bubble (switching from', lastEventType, 'to content_delta)');
                                                // CRITICAL FIX: Store reference BEFORE nulling
                                                const oldBubble = textBubble;
                                                textBubble = null;
                                                fullResponse = '';
                                                // Reset the streaming processor for new message
                                                // If the previous bubble had a processor, flush it and remove from registry
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

                                        // Now accumulate the text
                                        fullResponse += data.text;
                                        console.log('[CHART] fullResponse updated to length:', fullResponse.length);

                                        // Track that we're in a text event
                                        lastEventType = 'content_delta';

                                        // Create text bubble if it doesn't exist
                                        if (!textBubble) {
                                            console.log(' Creating new text bubble...');
                                            textBubble = document.createElement('div');
                                            textBubble.className = 'ai-message assistant text-bubble';

                                            // Create header with ROBOT avatar
                                            const headerDiv = document.createElement('div');
                                            headerDiv.className = 'ai-message-header';

                                            const avatar = document.createElement('div');
                                            avatar.className = 'ai-message-avatar';
                                            avatar.innerHTML = '<i class="fa-solid fa-atom"></i>'; // ATOM ICON (AI AGENT)

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

                                            // Add copy buttons
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

                                            actionsDiv.appendChild(copyBtn);
                                            actionsDiv.appendChild(copyRawBtn);
                                            headerDiv.appendChild(actionsDiv);

                                            textBubble.appendChild(headerDiv);

                                            // Create content div
                                            const contentDiv = document.createElement('div');
                                            contentDiv.className = 'ai-message-content';
                                            textBubble.appendChild(contentDiv);

                                            chatMessages.appendChild(textBubble); // Add directly to chatMessages
                                            console.log('[OK] Text bubble created and added');

                                            // ===== VISUALIZATION ENGINE INTEGRATION =====
                                            // Initialize TwoRuleStreamProcessor for visualization rendering
                                            if (typeof TwoRuleStreamProcessor !== 'undefined') {
                                                console.log(' Initializing TwoRuleStreamProcessor for visualization rendering (per-bubble instance)...');
                                                try {
                                                    const _proc = new TwoRuleStreamProcessor(contentDiv);
                                                    // Store on the bubble so concurrent streams don't share state
                                                    textBubble._twoRuleProcessor = _proc;
                                                    // Lightweight global registry for active processors
                                                    window._twoRuleProcessors = window._twoRuleProcessors || new Set();
                                                    window._twoRuleProcessors.add(_proc);

                                                    // Monitor registry size for performance issues
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

                                            // Initialize VisualizationEngine for fullscreen/modal support
                                            if (typeof VisualizationEngine !== 'undefined' && !window.visualizationEngine) {
                                                console.log(' Initializing VisualizationEngine for fullscreen support...');
                                                window.visualizationEngine = new VisualizationEngine();
                                                console.log('[OK] VisualizationEngine initialized');
                                            }

                                            // Add double-click handler to open message in popup
                                            contentDiv.addEventListener('dblclick', (e) => {
                                                // Don't trigger if clicking on a link or button
                                                if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || e.target.closest('button') || e.target.closest('a')) {
                                                    return;
                                                }
                                                console.log(' Opening message in popup (double-click)...');
                                                openMessagePopup('assistant', fullResponse);
                                            });
                                            // =========================================
                                        }                                                // ===== PROCESS STREAMING CONTENT THROUGH VISUALIZATION ENGINE =====
                                        const textContent = textBubble.querySelector('.ai-message-content');
                                        console.log(' Processing content chunk, fullResponse length:', fullResponse.length);
                                        console.log(' textContent element:', textContent);
                                        console.log(' Current text preview:', fullResponse.substring(0, 100));

                                        if (textContent) {
                                            // Use TwoRuleStreamProcessor if available (handles visualizations + markdown)
                                            // Prefer per-bubble processor; fall back to any global processor for compatibility
                                            const _processor = (textBubble && textBubble._twoRuleProcessor) || (window.globalTwoRuleProcessor || null);

                                            // Deprecation warning
                                            if (textBubble && !textBubble._twoRuleProcessor && window.globalTwoRuleProcessor) {
                                                console.warn('[DEPRECATED] Stream using global TwoRule processor instead of per-bubble instance');
                                            }

                                            if (_processor && typeof _processor.processChunk === 'function') {
                                                console.log(' Processing chunk through TwoRuleStreamProcessor (Plotly + Mermaid support)...');
                                                // Process the new chunk (NOT full response - processor maintains state)
                                                _processor.processChunk(data.text).then(() => {
                                                    console.log('[OK] Visualization processor handled chunk successfully');
                                                }).catch((e) => {
                                                    console.error('[ERROR] Visualization processor error:', e);
                                                    // Fallback to basic markdown rendering
                                                    textContent.innerHTML = renderBasicMarkdown(fullResponse);
                                                });
                                            } else {
                                                // Fallback: Basic markdown rendering (no visualizations)
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
                                            console.log('[SIZE] Content updated');

                                            // Auto-scroll to show streaming content
                                            textBubble.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                                            console.log(' Auto-scrolled to show new content');
                                        } else {
                                            console.error('[ERROR] Could not find .ai-message-content in textBubble!');
                                        }
                                        // =========================================
                                    } else if (data.type === 'conversation_sync') {
                                        // CRITICAL FIX (Nov 22, 2025): DO NOT sync from backend!
                                        // Backend's conversation_history is VALIDATED/PRUNED and missing user messages!
                                        // Frontend MessageStore is authoritative - keep frontend's conversation!
                                        console.log(`[SYNC] 📥 Received conversation_sync: ${data.message_count} messages (round ${data.round})`);
                                        console.log(`ℹ️  [SYNC] IGNORING backend conversation (frontend is authoritative)`);
                                        console.log(`ℹ️  [SYNC] Backend has ${data.message_count} messages, frontend has ${AppState.chatMessages.length} messages`);
                                        
                                        // Log backend structure for debugging ONLY (don't use it)
                                        if (data.conversation_history && Array.isArray(data.conversation_history)) {
                                            console.log('[SYNC] Backend message structure (for debugging only):');
                                            data.conversation_history.forEach((msg, idx) => {
                                                const contentTypes = Array.isArray(msg.content) 
                                                    ? msg.content.map(b => b.type).join(', ')
                                                    : 'string';
                                                console.log(`  [${idx}] ${msg.role}: ${contentTypes}`);
                                            });
                                        }

                                    } else if (data.type === 'complete') {
                                        console.log('[OK] [COMPLETE EVENT] Stream finished');

                                        // Clear status indicator - back to idle
                                        clearAIStatusIndicator();
                                        if (typeof AgentStatusIndicator !== 'undefined') {
                                            AgentStatusIndicator.clear(null);
                                        }

                                        console.log(' Full response length:', fullResponse.length);
                                        console.log(' Total bubbles created - Thinking:', thinkingBubble ? 'Yes' : 'No', 'Text:', textBubble ? 'Yes' : 'No');

                                        // CRITICAL FIX (Nov 22, 2025): DO NOT sync from backend's conversation_history!
                                        // Backend returns VALIDATED/PRUNED conversation missing user messages
                                        // Frontend MessageStore is authoritative - keep frontend's conversation!
                                        console.log(`ℹ️  [COMPLETE] Frontend has ${AppState.chatMessages.length} messages (authoritative)`);
                                        if (data.conversation_history && Array.isArray(data.conversation_history)) {
                                            console.log(`ℹ️  [COMPLETE] Backend sent ${data.conversation_history.length} messages (ignored)`);
                                        }

                                        // ===== FINALIZE VISUALIZATION PROCESSOR =====
                                        // Finalize the per-bubble processor if present, else finalize any global processor
                                        const _finalProc = (textBubble && textBubble._twoRuleProcessor) || (window.globalTwoRuleProcessor || null);

                                        // Deprecation warning
                                        if (textBubble && !textBubble._twoRuleProcessor && window.globalTwoRuleProcessor) {
                                            console.warn('[DEPRECATED] Finalizing global TwoRule processor instead of per-bubble instance');
                                        }

                                        if (_finalProc && typeof _finalProc.finalize === 'function') {
                                            console.log(' Finalizing TwoRuleStreamProcessor (rendering any pending visualizations)...');
                                            try {
                                                await _finalProc.finalize();
                                                console.log('[OK] Visualization processor finalized successfully');

                                                // CRITICAL FIX: If still no content rendered, force basic markdown
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
                                        // =========================================

                                        // Content was already rendered during streaming via content_delta events
                                        // NO NEED to re-render - just verify and enhance
                                        if (textBubble && fullResponse.length > 0) {
                                            const textContent = textBubble.querySelector('.ai-message-content');
                                            if (textContent) {
                                                console.log('[SIZE] Final rendered content length:', textContent.innerHTML.length);
                                                console.log('[OK] Streaming complete - content already displayed via incremental updates');

                                                // Apply syntax highlighting to code blocks if present
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

                                        // If no text but we have thinking, show it
                                        if (fullResponse.length === 0 && thinkingBubble) {
                                            thinkingBubble.classList.remove('collapsed');
                                        }

                                    } else if (data.type === 'tool_result') {
                                        // Flush any buffered content from active TwoRule processors
                                        if (window._twoRuleProcessors && window._twoRuleProcessors.size) {
                                            console.log(' Flushing buffered content from active TwoRule processors after tool result...');
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

                                        // NEW IMPLEMENTATION: Separate tool result bubble with white flag icon
                                        console.log('[OK] [TOOL_RESULT EVENT] Creating separate tool result bubble');
                                        console.log('[CHART] Tool name:', data.tool_name);
                                        console.log('[CHART] Tool ID:', data.tool_id);
                                        console.log('[CHART] Success:', data.success);

                                        // Update status indicator - tool success (blue pulse)
                                        updateAIStatusIndicator('tool-success');
                                        if (typeof AgentStatusIndicator !== 'undefined') {
                                            AgentStatusIndicator.update('tool-success', null);
                                        }

                                        // Remove bouncing dots on first content
                                        if (!firstContentReceived) {
                                            removeThinkingIndicator();
                                            firstContentReceived = true;
                                        }

                                        const isError = !data.success;
                                        const resultText = data.result || '(no result)';
                                        const rawResult = data.result || ''; // Store raw for raw button

                                        // Create tool result bubble (ai-message style like text bubbles)
                                        const toolResultBubble = document.createElement('div');
                                        toolResultBubble.className = 'ai-message assistant tool-result-bubble';
                                        toolResultBubble.setAttribute('data-tool-result-id', data.tool_id);

                                        // Create header with white flag icon and buttons (matching text bubble style)
                                        const headerDiv = document.createElement('div');
                                        headerDiv.className = 'ai-message-header';

                                        // White flag icon on blue/red background
                                        const avatar = document.createElement('div');
                                        avatar.className = 'ai-message-avatar';
                                        avatar.style.background = isError ? '#ef4444' : '#60A5FA';
                                        avatar.innerHTML = '<i class="fas fa-flag" style="color: white; font-size: 14px;"></i>';

                                        // Collapse toggle button
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

                                        // Add copy, raw buttons (matching text bubble actions)
                                        const actionsDiv = document.createElement('div');
                                        actionsDiv.className = 'ai-message-actions';

                                        // Copy button (formatted content)
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

                                        // Raw button (unrendered response)
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

                                        actionsDiv.appendChild(copyBtn);
                                        actionsDiv.appendChild(copyRawBtn);
                                        headerDiv.appendChild(actionsDiv);

                                        toolResultBubble.appendChild(headerDiv);

                                        // Create content div
                                        const contentDiv = document.createElement('div');
                                        contentDiv.className = 'ai-message-content';

                                        // Format result text nicely
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

                                        // Add to chat (start expanded)
                                        chatMessages.appendChild(toolResultBubble);
                                        chatMessages.scrollTop = chatMessages.scrollHeight;

                                        console.log('[OK] Tool result bubble created with white flag icon');

                                        // Track tool_result for conversation history
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
                                    } else if (data.type === 'tool_result_update') {
                                        // Handle tool result update (second handler for updating status)
                                        console.log(' [TOOL_RESULT_UPDATE EVENT] Updating tool status:', data.tool_use_id);
                                        const success = !data.is_error;

                                        // Update the tool indicator with result
                                        const toolIndicator = document.querySelector(`[data-tool-id="${data.tool_use_id}"]`);
                                        if (toolIndicator) {
                                            const icon = success ? 'fa-check-circle' : 'fa-exclamation-circle';
                                            const statusClass = success ? 'success' : 'error';
                                            const resultPreview = typeof data.content === 'string'
                                                ? data.content.substring(0, 100)
                                                : JSON.stringify(data.content).substring(0, 100);

                                            toolIndicator.className = `tool-execution-result ${statusClass}`;
                                            toolIndicator.innerHTML = `
                                                        <div class="tool-icon"><i class="fas ${icon}"></i></div>
                                                        <div class="tool-details">
                                                            <div class="tool-name">${data.tool_use_id}</div>
                                                            <div class="tool-result-preview">${resultPreview}${resultPreview.length >= 100 ? '...' : ''}</div>
                                                        </div>
                                                    `;
                                        }

                                        // Record tool usage
                                        ToolManager.recordToolCall(data.tool_use_id, success, 0);

                                    } else if (data.type === 'server_tool_use') {
                                        // Handle server tool use (web_search, web_fetch)
                                        console.log(' [SERVER_TOOL_USE EVENT] Server tool requested:', data.name);
                                        console.log('[CHART] Tool name:', data.name);
                                        console.log('[CHART] Input:', data.input);

                                        // Remove bouncing dots on first content
                                        if (!firstContentReceived) {
                                            removeThinkingIndicator();
                                            firstContentReceived = true;
                                        }

                                        // Create server tool bubble
                                        const serverToolBubble = document.createElement('div');
                                        serverToolBubble.className = 'ai-message assistant server-tool-bubble';
                                        serverToolBubble.setAttribute('data-server-tool-id', data.id);

                                        // Create header with GLOBE avatar
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

                                        // Add copy buttons
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

                                        actionsDiv.appendChild(copyBtn);
                                        headerDiv.appendChild(actionsDiv);

                                        // Create content div with tool details
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
                                        serverToolBubble.classList.add('collapsed'); // Start collapsed
                                        chatMessages.appendChild(serverToolBubble);

                                        // Track event type
                                        lastEventType = 'server_tool_use';

                                        console.log('[OK] Server tool bubble created');

                                    } else if (data.type === 'web_search_tool_result') {
                                        // Handle web search results
                                        console.log('[SEARCH] [WEB_SEARCH_RESULT EVENT] Search completed:', data.tool_use_id);
                                        console.log('[CHART] Results count:', data.content?.length || 0);

                                        // Find and update the server tool bubble
                                        const serverToolBubble = chatMessages.querySelector(`[data-server-tool-id="${data.tool_use_id}"]`);
                                        if (serverToolBubble) {
                                            const contentDiv = serverToolBubble.querySelector('.ai-message-content');
                                            if (contentDiv) {
                                                const results = data.content || [];
                                                const resultsHtml = results.map((result, idx) => `
                                                            <div style="margin-bottom: 12px; padding: 12px; background: rgba(74, 222, 128, 0.1); border-left: 3px solid #4ADE80; border-radius: 4px;">
                                                                <div style="margin-bottom: 4px;">
                                                                    <strong style="color: #4ADE80;">${idx + 1}. ${result.title || 'Result'}</strong>
                                                                </div>
                                                                <div style="margin-bottom: 4px; font-size: 12px;">
                                                                    <a href="${result.url}" target="_blank" style="color: var(--accent-primary);">
                                                                        ${result.url}
                                                                    </a>
                                                                </div>
                                                                ${result.page_age ? `<div style="font-size: 11px; color: var(--text-muted);">Updated: ${result.page_age}</div>` : ''}
                                                            </div>
                                                        `).join('');

                                                contentDiv.innerHTML = `
                                                            <div style="margin-bottom: 12px;">
                                                                <strong style="color: #4ADE80;">[WEBSEARCH]</strong>
                                                                <span style="margin-left: 8px; color: var(--text-muted); font-size: 12px;">
                                                                    <i class="fas fa-check-circle"></i> Found ${results.length} results
                                                                </span>
                                                            </div>
                                                            ${resultsHtml}
                                                        `;

                                                // Update avatar to show success
                                                const avatar = serverToolBubble.querySelector('.ai-message-avatar');
                                                if (avatar) {
                                                    avatar.innerHTML = '<i class="fas fa-check-circle" style="color: #4ADE80;"></i>';
                                                }
                                            }
                                            console.log('[OK] Web search bubble updated with results');
                                        } else {
                                            console.warn('[WARN] Server tool bubble not found for ID:', data.tool_use_id);
                                        }

                                    } else if (data.type === 'web_fetch_tool_result') {
                                        // Handle web fetch results
                                        console.log(' [WEB_FETCH_RESULT EVENT] Fetch completed:', data.tool_use_id);

                                        // Find and update the server tool bubble
                                        const serverToolBubble = chatMessages.querySelector(`[data-server-tool-id="${data.tool_use_id}"]`);
                                        if (serverToolBubble) {
                                            const contentDiv = serverToolBubble.querySelector('.ai-message-content');
                                            if (contentDiv) {
                                                const result = data.content || {};
                                                const url = result.url || 'Unknown URL';
                                                const title = result.content?.title || 'Document';
                                                const contentPreview = result.content?.source?.data
                                                    ? `${result.content.source.data.substring(0, 200)}...`
                                                    : 'Content fetched successfully';

                                                contentDiv.innerHTML = `
                                                            <div style="margin-bottom: 12px;">
                                                                <strong style="color: #60A5FA;">[WEBFETCH]</strong>
                                                                <span style="margin-left: 8px; color: var(--text-muted); font-size: 12px;">
                                                                    <i class="fas fa-check-circle"></i> Fetched successfully
                                                                </span>
                                                            </div>
                                                            <div style="margin-bottom: 12px; padding: 12px; background: rgba(96, 165, 250, 0.1); border-left: 3px solid #60A5FA; border-radius: 4px;">
                                                                <div style="margin-bottom: 4px;">
                                                                    <strong style="color: #60A5FA;">${title}</strong>
                                                                </div>
                                                                <div style="margin-bottom: 8px; font-size: 12px;">
                                                                    <a href="${url}" target="_blank" style="color: var(--accent-primary);">
                                                                        ${url}
                                                                    </a>
                                                                </div>
                                                                <div style="font-size: 12px; color: var(--text-secondary); font-family: monospace; white-space: pre-wrap;">
                                                                    ${contentPreview}
                                                                </div>
                                                            </div>
                                                        `;

                                                // Update avatar to show success
                                                const avatar = serverToolBubble.querySelector('.ai-message-avatar');
                                                if (avatar) {
                                                    avatar.innerHTML = '<i class="fas fa-check-circle" style="color: #60A5FA;"></i>';
                                                }
                                            }
                                            console.log('[OK] Web fetch bubble updated with results');
                                        } else {
                                            console.warn('[WARN] Server tool bubble not found for ID:', data.tool_use_id);
                                        }

                                    } else if (data.type === 'show_feedback_area') {
                                        // Handle show_feedback_area tool
                                        console.log(' [SHOW_FEEDBACK_AREA] Showing feedback area:', data);
                                        if (typeof showFeedbackArea === 'function') {
                                            showFeedbackArea(data);
                                        } else {
                                            console.error('[ERROR] showFeedbackArea function not available');
                                        }

                                    } else if (data.type === 'hide_feedback_area') {
                                        // Handle hide_feedback_area tool
                                        console.log(' [HIDE_FEEDBACK_AREA] Hiding feedback area');
                                        if (typeof hideFeedbackArea === 'function') {
                                            hideFeedbackArea();
                                        } else {
                                            console.error('[ERROR] hideFeedbackArea function not available');
                                        }

                                    } else if (data.type === 'fetch_instructions_request') {
                                        // Handle fetch_user_instructions tool
                                        console.log(' [FETCH_INSTRUCTIONS] AI is polling for user feedback');
                                        if (typeof handleFetchInstructionsRequest === 'function') {
                                            const feedback = await handleFetchInstructionsRequest();
                                            console.log(' User feedback:', feedback);

                                            // Send feedback back to AI via API
                                            if (feedback.has_instructions) {
                                                try {
                                                    const response = await fetch(`${API_BASE_URL}/api/agent/user-feedback/submit`, {
                                                        method: 'POST',
                                                        headers: {
                                                            'Content-Type': 'application/json'
                                                        },
                                                        body: JSON.stringify({
                                                            session_id: currentSessionId || sessionId,
                                                            agent_id: currentAgentId,
                                                            instructions: feedback.instructions,
                                                            timestamp: feedback.timestamp
                                                        })
                                                    });

                                                    const result = await response.json();
                                                    if (result.success) {
                                                        console.log('[OK] [FEEDBACK_SUBMIT] Feedback sent to AI:', result);
                                                    } else {
                                                        console.error('[ERROR] [FEEDBACK_SUBMIT] Failed to send feedback:', result);
                                                    }
                                                } catch (error) {
                                                    console.error('[ERROR] [FEEDBACK_SUBMIT] Network error:', error);
                                                }
                                            } else {
                                                console.log(' [FEEDBACK_SUBMIT] No instructions to send (textarea empty)');
                                            }
                                        } else {
                                            console.error('[ERROR] handleFetchInstructionsRequest function not available');
                                        }


                                    } else if (data.type === 'error') {
                                        console.error('[ERROR] [ERROR EVENT] Stream error:', data.error);
                                        console.error('[CHART] Error details:', JSON.stringify(data.error, null, 2));

                                        // Check if it's a 413 error (request too large)
                                        const is413Error = data.error && (
                                            data.error.includes('413') ||
                                            data.error.includes('request_too_large') ||
                                            data.error.includes('Request exceeds the maximum size')
                                        );

                                        if (is413Error) {
                                            console.error('[413 ERROR] Request too large - clearing failed message and reloading thread');

                                            // Remove the last assistant message (failed response)
                                            const lastAssistantMsg = document.querySelector('.ai-message.assistant:last-child');
                                            if (lastAssistantMsg) {
                                                lastAssistantMsg.remove();
                                            }

                                            // Remove from conversation history
                                            if (AppState.chatMessages.length > 0 && AppState.chatMessages[AppState.chatMessages.length - 1].role === 'assistant') {
                                                AppState.chatMessages.pop();
                                            }

                                            // Add to Updates container
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

                                            // Reload the thread after 2 seconds to clear state
                                            setTimeout(() => {
                                                if (typeof ThreadManager !== 'undefined' && ThreadManager.currentThreadSlug) {
                                                    console.log('[413 RECOVERY] Reloading thread:', ThreadManager.currentThreadSlug);
                                                    ThreadManager.loadThread(ThreadManager.currentThreadSlug);
                                                } else {
                                                    console.log('[413 RECOVERY] No thread to reload, refreshing chat');
                                                    location.reload();
                                                }
                                            }, 2000);

                                            fullResponse = ''; // Clear response to prevent adding to history
                                        } else {
                                            // Regular error handling
                                            fullResponse = `Error: ${JSON.stringify(data.error)}`;
                                            // Update the message to show the error
                                            const lastMsg = document.querySelector('.ai-message.assistant:last-child .ai-message-content');
                                            if (lastMsg) {
                                                lastMsg.innerHTML = `<div style="color: #ef4444; padding: 12px; background: rgba(239, 68, 68, 0.1); border-radius: 6px; border-left: 4px solid #ef4444;">
                                                            <strong> Stream Error:</strong><br>
                                                            <pre style="margin-top: 8px; white-space: pre-wrap;">${JSON.stringify(data.error, null, 2)}</pre>
                                                        </div>`;
                                            }
                                        }
                                    }
                                }
                            } catch (e) {
                                // ISOLATION FIX: Only increment error count for THIS thread
                                threadErrorCount++;
                                console.error(`[Prime] SSE parse error (${threadErrorCount}/${maxThreadErrors}):`, e, 'Line:', line);
                                
                                // If too many errors in THIS thread, stop THIS thread only
                                if (threadErrorCount >= maxThreadErrors) {
                                    threadFailed = true;
                                    console.error(`[Prime] Thread ${threadSlug} failed after ${maxThreadErrors} errors - stopping THIS thread only`);
                                    break;  // Exit line loop
                                }
                                // Otherwise continue - don't let one bad event break the whole stream
                            }
                        }
                    }
                    
                    // If thread failed, break outer message loop too
                    if (threadFailed) {
                        console.error(`[Prime] Exiting stream reader for failed thread ${threadSlug}`);
                        break;
                    }
                }
            }

            // Thread-specific cleanup
            if (threadFailed) {
                addChatMessage('assistant', ` Thread error: Too many parse errors. Please try again.`);
            }

            removeThinkingIndicator();
            const responseTime = Date.now() - startTime;
            console.log(`Streamed response received in ${responseTime}ms`);

            // CRITICAL FIX (Nov 22, 2025): DON'T add text-only message!
            // Backend already sent complete conversation history with full blocks in 'complete' event
            // AppState.chatMessages was synced with backend's authoritative conversation (line ~1370)
            // Just save the complete backend conversation - no reconstruction needed!

            console.log(`[OK] Using backend's authoritative conversation (${AppState.chatMessages.length} messages with full blocks)`);

            // Sync MessageStore with backend's complete conversation
            if (window.MessageStore && AppState.chatMessages.length > 0) {
                console.log(`[SYNC] Syncing MessageStore with backend's ${AppState.chatMessages.length} messages...`);
                
                // Clear and rebuild MessageStore from backend's authoritative conversation
                // This ensures MessageStore has the same structure as backend (with all blocks)
                for (const msg of AppState.chatMessages) {
                    await window.MessageStore.addMessage(currentThreadId, msg, {
                        checkDuplicates: true,
                        silent: true  // Silent to avoid log spam
                    });
                }
                console.log(`✅ [MessageStore] Synced ${AppState.chatMessages.length} messages from backend (includes thinking/tool_use/tool_result blocks)`);
            }

            // Save thread with backend's complete conversation
            if (typeof ThreadManager !== 'undefined' && AppState.chatMessages.length > 0) {
                ThreadManager.updateCurrentThread(AppState.chatMessages);
                console.log(`✅ [Thread] Saved complete conversation (${AppState.chatMessages.length} messages, ${responseTime}ms)`);
            }

        } else {
            // HANDLE NON-STREAMING JSON RESPONSE (fallback)
            const data = await response.json();
            const responseTime = Date.now() - startTime;

            removeThinkingIndicator();

            // Track and display tool usage
            if (data.tools_used && Array.isArray(data.tools_used)) {
                console.log(` AI used ${data.tools_used.length} tools:`, data.tools_used);
                data.tools_used.forEach(tool => {
                    ToolManager.recordToolCall(
                        tool.name || tool,
                        tool.success !== false,
                        tool.duration || 0
                    );
                });

                if (data.tools_used.length > 0) {
                    // Show tool usage message bubble with green border
                    addToolUsageMessage(data.tools_used);
                    showNotification(`AI used ${data.tools_used.length} tool(s)`, 'info', 2000);
                }
            }

            // Add AI response
            if (data.response) {
                addChatMessage('assistant', data.response);
                console.log(`Chat response received in ${responseTime}ms`);
            } else if (data.error) {
                addChatMessage('assistant', `Error: ${data.error}`);
                showNotification('AI Error: ' + data.error, 'error');
            }

            // Store ONLY assistant response in chat history
            // (User message already added before request - don't duplicate)
            // CRITICAL FIX: Only add to history if content is non-empty
            const responseContent = data.response || data.error || '';
            if (responseContent.trim().length > 0) {
                // PHASE 2: Use MessageStore instead of AppState.chatMessages
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
        console.error(' Chat error:', error);
        console.error('Error details:', {
            message: error.message,
            type: error.name,
            stack: error.stack
        });

        // CRITICAL: Attempt auto-recovery with ErrorRecoveryManager FIRST
        if (window.ErrorRecoveryManager && error.message) {
            const errorMsg = error.message.toLowerCase();
            const isRecoverable = errorMsg.includes('invalid_request_error') ||
                                 errorMsg.includes('tool_use_id') ||
                                 errorMsg.includes('first block must be') ||
                                 errorMsg.includes('thinking') ||
                                 errorMsg.includes('rate limit') ||
                                 errorMsg.includes('context_length') ||
                                 errorMsg.includes('prompt is too long') ||
                                 errorMsg.includes('overloaded');

            if (isRecoverable) {
                console.log(' Attempting auto-recovery...');
                
                try {
                    // Create recovery manager
                    const recoveryManager = new ErrorRecoveryManager(
                        'prime',
                        currentThreadId,
                        null  // null = Prime AI
                    );

                    // Attempt recovery with original request payload
                    const recoveryResponse = await recoveryManager.handleError(error, requestBody);

                    // If recovery succeeded, process the new stream
                    if (recoveryResponse) {
                        console.log(' Auto-recovery successful!');
                        
                        // Show recovery log in console
                        const recoveryLog = recoveryManager.exportRecoveryLog();
                        console.log('=== RECOVERY LOG ===\\n' + recoveryLog);
                        
                        // Show success notification
                        if (typeof showNotification === 'function') {
                            showNotification('Auto-recovery successful - message sent', 'success');
                        }
                        
                        // Note: Recovery manager handles resubmission
                        // Exit and let the new stream process
                        return;
                    }
                } catch (recoveryError) {
                    console.error(' Auto-recovery failed:', recoveryError);
                    // Fall through to normal error handling
                }
            }
        }

        removeThinkingIndicator();

        // Check if it's a 413 error from catch block
        const is413Error = error.message && (
            error.message.includes('413') ||
            error.message.includes('request_too_large') ||
            error.message.includes('Request exceeds the maximum size')
        );

        if (is413Error) {
            console.error('[413 ERROR] Request too large caught in error handler');

            // Remove the last assistant message if it exists
            const lastAssistantMsg = document.querySelector('.ai-message.assistant:last-child');
            if (lastAssistantMsg) {
                lastAssistantMsg.remove();
            }

            // Remove from conversation history
            if (AppState.chatMessages.length > 0 && AppState.chatMessages[AppState.chatMessages.length - 1].role === 'assistant') {
                AppState.chatMessages.pop();
            }

            // Add to Updates container
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

            // Reload the thread after 2 seconds
            setTimeout(() => {
                if (typeof ThreadManager !== 'undefined' && ThreadManager.currentThreadSlug) {
                    console.log('[413 RECOVERY] Reloading thread:', ThreadManager.currentThreadSlug);
                    ThreadManager.loadThread(ThreadManager.currentThreadSlug);
                } else {
                    console.log('[413 RECOVERY] No thread to reload, refreshing chat');
                    location.reload();
                }
            }, 2000);

            return; // Exit early to prevent adding error message
        }

        // More helpful error messages
        let errorMsg = 'Sorry, I encountered an error. ';
        if (error.message.includes('Failed to fetch')) {
            errorMsg += 'Could not connect to backend. Is Flask running on port 5001?';
            console.error(' Fix: Run BISTART or start Flask manually');
        } else if (error.message.includes('NetworkError')) {
            errorMsg += 'Network error. Check your connection.';
        } else {
            errorMsg += error.message;
        }

        addChatMessage('assistant', errorMsg);
        showNotification('Chat Error: ' + error.message, 'error');

        // Mark as connected on first successful request (even if health check failed)
        if (!AppState.isConnected && error.message.includes('200')) {
            AppState.isConnected = true;
            console.log('Backend is actually working! Marking as connected.');
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
    console.log(`[CHART] Files attached: ${window.chatAttachedFiles.length}`);

    try {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('ui_context', 'business_ai_chat');
        formData.append('prompt', message);
        formData.append('provider', 'anthropic'); // Only Claude supports Vision

        // Add files to FormData
        window.chatAttachedFiles.forEach(file => {
            formData.append('files', file);
            console.log(`[ATTACH] Added file: ${file.name} (${file.type}, ${file.size} bytes)`);
        });

        //  CRITICAL: Clear attached files IMMEDIATELY after adding to FormData
        // This prevents files from persisting to next message
        console.log('[CLEAN] Clearing attached files from UI...');
        if (window.clearChatAttachedFiles) {
            window.clearChatAttachedFiles();
        }

        // Send request to file upload endpoint
        console.log(' Sending files to /api/chat/send-with-files...');
        const uploadResponse = await fetch(`${API_BASE_URL}/api/chat/send-with-files`, {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            throw new Error(`HTTP error! status: ${uploadResponse.status}`);
        }

        const uploadData = await uploadResponse.json();
        console.log('[OK] Files uploaded successfully:', uploadData);

        // Now stream the response
        console.log(' Connecting to SSE stream for file processing...');
        const streamUrl = `${API_BASE_URL}/api/agent/stream/1?session_id=${sessionId}`;
        const response = await fetch(streamUrl);

        if (!response.ok) {
            throw new Error(`Stream error! status: ${response.status}`);
        }

        // Process streaming response (reuse existing streaming logic)
        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('text/event-stream')) {
            console.log(' Receiving streamed response with file context...');

            // Remove thinking indicator
            removeThinkingIndicator();

            // Get chat messages container
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
                                                // Handle both sync and async processChunk
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

            // Store assistant response
            if (fullResponse && fullResponse.trim().length > 0) {
                // PHASE 2: Use MessageStore instead of AppState.chatMessages
                const currentThreadId = AppState.currentThreadId || 'prime-ai-default';
                await window.MessageStore.addMessage(currentThreadId, {
                    role: 'assistant',
                    content: fullResponse,
                    response_time: responseTime
                });
            }

            // Save thread
            if (typeof ThreadManager !== 'undefined') {
                ThreadManager.updateCurrentThread(AppState.chatMessages);
            }
        }

    } catch (error) {
        console.error('[ERROR] File upload error:', error);
        removeThinkingIndicator();
        addChatMessage('assistant', `Error uploading files: ${error.message}`);
        showNotification('Failed to upload files', 'error');

        //  CRITICAL: Clear files on error too (in case clearChatAttachedFiles was skipped)
        console.log('[CLEAN] Clearing attached files after error...');
        if (window.clearChatAttachedFiles) {
            window.clearChatAttachedFiles();
        }
    }
}

function addChatMessage(role, content, isThinking = false) {
    // Use unified message renderer
    const threadId = ThreadManager.currentThreadId;

    const messageDiv = UnifiedMessageRenderer.render(
        '#ai-chat-messages',
        role === 'ai' ? 'assistant' : role,
        content,
        {
            isThinking: isThinking,
            scrollToBottom: autoScrollEnabled,
            threadId: threadId,
            syncToBackend: false
        }
    );

    if (!messageDiv) {
        console.error('[Prime] Failed to render message');
        return;
    }

    return messageDiv;

    // OLD CODE BELOW (REPLACED BY UNIFIED RENDERER)
    /*
    const messagesContainer = document.getElementById('ai-chat-messages');

    // Add error handling
    if (!messagesContainer) {
        console.error('[ERROR] ai-chat-messages container not found!');
        return;
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `ai-message ${role}${isThinking ? ' thinking' : ''}`;

    // Store raw content for copy functionality
    messageDiv.setAttribute('data-raw-content', content);

    // Create header with avatar and toggle
    const headerDiv = document.createElement('div');
    headerDiv.className = 'ai-message-header';

    const avatar = document.createElement('div');
    avatar.className = 'ai-message-avatar';
    // Set icon based on role
    if (role === 'user') {
        avatar.innerHTML = '<i class="fas fa-user"></i>';
    } else if (role === 'tool') {
        avatar.innerHTML = '<i class="fas fa-wrench"></i>';
    } else {
        avatar.innerHTML = '<i class="fa-solid fa-atom"></i>';
    }

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'ai-message-toggle';
    toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
    toggleBtn.title = 'Collapse/Expand message';
    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        messageDiv.classList.toggle('collapsed');
    });

    headerDiv.appendChild(avatar);
    headerDiv.appendChild(toggleBtn);

    // Add copy buttons
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'ai-message-actions';

    // Copy rendered text button
    const copyRenderedBtn = document.createElement('button');
    copyRenderedBtn.className = 'ai-message-copy-btn';
    copyRenderedBtn.innerHTML = '<i class="fas fa-copy"></i>';
    copyRenderedBtn.title = 'Copy rendered text';
    copyRenderedBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        copyRenderedText(messageDiv, copyRenderedBtn);
    });

    // Copy raw content button
    const copyRawBtn = document.createElement('button');
    copyRawBtn.className = 'ai-message-copy-btn';
    copyRawBtn.innerHTML = '<i class="fas fa-code"></i>';
    copyRawBtn.title = 'Copy raw content';
    copyRawBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        copyRawContent(messageDiv, copyRawBtn);
    });

    actionsDiv.appendChild(copyRenderedBtn);
    actionsDiv.appendChild(copyRawBtn);
    headerDiv.appendChild(actionsDiv);

    const contentDiv = document.createElement('div');
    contentDiv.className = 'ai-message-content';

    // RENDER AI RESPONSES
    if (role === 'assistant' && !isThinking && content) {
        console.log(' Rendering AI message...');

        // Extract text content from various formats
        let contentStr = '';

        if (typeof content === 'string') {
            // Already a string
            contentStr = content;
        } else if (Array.isArray(content)) {
            // Array of content blocks (Claude API format)
            contentStr = content
                .filter(block => block && block.type === 'text')
                .map(block => block.text || '')
                .join('\n\n');
        } else if (content && typeof content === 'object') {
            // Single content block object
            if (content.type === 'text' && content.text) {
                contentStr = content.text;
            } else if (content.text) {
                // Object with text property (but no type)
                contentStr = content.text;
            } else if (content.content) {
                // Nested content - recurse if needed
                if (typeof content.content === 'string') {
                    contentStr = content.content;
                } else if (Array.isArray(content.content)) {
                    // Nested array of blocks
                    contentStr = content.content
                        .filter(block => block && block.type === 'text')
                        .map(block => block.text || '')
                        .join('\n\n');
                } else {
                    contentStr = JSON.stringify(content.content, null, 2);
                }
            } else {
                // Last resort - stringify with proper formatting
                console.warn('[WARN] Unable to extract text from content object:', content);
                contentStr = JSON.stringify(content, null, 2);
            }
        }

        console.log(' Content preview:', contentStr.substring(0, 100));
        console.log(' Content length:', contentStr.length);

        // If no text content extracted, don't create a message bubble at all
        if (!contentStr || contentStr.trim() === '') {
            console.warn('[WARN] No text content found, skipping message bubble creation');
            return;
        }

        // TRY VISUALIZATION ENGINE FIRST
        if (!window.USE_BASIC_RENDERER && typeof TwoRuleStreamProcessor !== 'undefined') {
            try {
                console.log(' Using TwoRuleStreamProcessor...');
                const processor = new TwoRuleStreamProcessor(contentDiv);

                // Process content
                processor.processChunk(contentStr);

                // TwoRuleStreamProcessor auto-renders, no finalize needed

                console.log('Visualization processing complete');
                console.log('[SIZE] Rendered HTML length:', contentDiv.innerHTML.length);

                // Verify content was rendered
                if (!contentDiv.innerHTML || contentDiv.innerHTML.trim() === '') {
                    console.warn('[WARN] Visualization engine produced empty content, using basic renderer');
                    contentDiv.innerHTML = renderBasicMarkdown(contentStr);
                }
            } catch (error) {
                console.error(' Visualization engine error:', error);
                console.log('↩️ Falling back to basic markdown renderer');
                contentDiv.innerHTML = renderBasicMarkdown(contentStr);
            }
        } else {
            // USE BASIC MARKDOWN RENDERER
            console.log(' Using basic markdown renderer');
            contentDiv.innerHTML = renderBasicMarkdown(contentStr);
        }

        // FINAL SAFETY CHECK
        if (!contentDiv.innerHTML || contentDiv.innerHTML.trim() === '') {
            console.error(' All rendering methods failed! Using raw text.');
            contentDiv.textContent = contentStr;
        }

        console.log('Message rendered successfully');

        // Add double-click event to open popup (allow single click for links)
        contentDiv.addEventListener('dblclick', () => {
            openMessagePopup(role, content);
        });

        // Make links open in new tab
        contentDiv.querySelectorAll('a').forEach(link => {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
            link.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent double-click event from firing
            });
        });
    } else {
        // For user messages and thinking indicators, use direct HTML
        contentDiv.innerHTML = content;

        // Add double-click event to open popup (not for thinking indicators)
        if (!isThinking) {
            contentDiv.addEventListener('dblclick', () => {
                openMessagePopup(role, content);
            });

            // Make links open in new tab
            contentDiv.querySelectorAll('a').forEach(link => {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
                link.addEventListener('click', (e) => {
                    e.stopPropagation();
                });
            });
        }
    }

    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    console.log('[OK] Message added to DOM, total messages:', messagesContainer.children.length);

    // Hide welcome container when any message is added (handled by thread loading now)
    // Welcome is only shown when no thread is loaded, not based on message count
    const welcomeContainer = document.getElementById('prime-welcome-container');
    if (welcomeContainer && !isThinking) {
        welcomeContainer.style.display = 'none';
    }

    // Fix links in newly added message
    contentDiv.querySelectorAll('a').forEach(link => {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
    });

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    */
}

// ==================== MESSAGE POPUP FUNCTIONS ====================
function openMessagePopup(role, content) {
    const overlay = document.getElementById('message-popup-overlay');
    const body = document.getElementById('message-popup-body');
    const titleText = document.getElementById('message-popup-title-text');

    titleText.textContent = 'Message Details';

    // RENDER CONTENT PROPERLY (same as chat messages)
    if (role === 'assistant') {
        console.log(' Rendering popup content...');

        // Try Visualization Engine first
        if (!window.USE_BASIC_RENDERER && typeof TwoRuleStreamProcessor !== 'undefined') {
            try {
                console.log(' Using TwoRuleStreamProcessor for popup...');
                body.innerHTML = ''; // Clear first
                const processor = new TwoRuleStreamProcessor(body);
                processor.processChunk(content);

                // FIX: Check if finalize method exists before calling
                if (typeof processor.finalize === 'function') {
                    processor.finalize();
                } else if (typeof processor.complete === 'function') {
                    processor.complete();
                }

                // Verify content rendered
                if (!body.innerHTML || body.innerHTML.trim() === '') {
                    console.warn('[WARN] Visualization engine produced empty popup content, using basic renderer');
                    body.innerHTML = renderBasicMarkdown(content);
                }
            } catch (error) {
                console.error(' Visualization engine error in popup:', error);
                console.log('↩️ Falling back to basic markdown renderer');
                body.innerHTML = renderBasicMarkdown(content);
            }
        } else {
            // Use basic markdown renderer
            console.log(' Using basic markdown renderer for popup');
            body.innerHTML = renderBasicMarkdown(content);
        }

        // Final safety check
        if (!body.innerHTML || body.innerHTML.trim() === '') {
            console.error(' All popup rendering methods failed! Using raw text.');
            body.textContent = content;
        }

        console.log('Popup content rendered successfully');
    } else {
        // User messages - just display as-is
        body.innerHTML = content;
    }

    // Store ORIGINAL content for copy function (not rendered HTML)
    overlay.dataset.content = content;

    overlay.classList.add('active');

    // Close on overlay click
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

    // Create temporary element to strip HTML
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
// Update AI icon status border based on current activity
function updateAIStatusIndicator(status) {
    // For Prime AI
    const primeIcon = document.querySelector('.ai-chat-title .ai-icon');
    if (primeIcon) {
        // Remove all status classes
        primeIcon.classList.remove('status-thinking', 'status-tool-running', 'status-tool-success', 'status-writing');

        // Add new status class
        if (status) {
            primeIcon.classList.add(`status-${status}`);
        }

        console.log(`[STATUS] Prime AI icon status: ${status || 'idle'}`);
    }

    // For Agent icons in multi-agent columns
    const agentIcons = document.querySelectorAll('.agent-header h2 i');
    agentIcons.forEach(icon => {
        // Remove all status classes
        icon.classList.remove('status-thinking', 'status-tool-running', 'status-tool-success', 'status-writing');

        // Add new status class
        if (status) {
            icon.classList.add(`status-${status}`);
        }
    });
}

// Clear status indicator (back to idle - no border)
function clearAIStatusIndicator() {
    updateAIStatusIndicator(null);
    if (typeof AgentStatusIndicator !== 'undefined') {
        AgentStatusIndicator.clear(null);
    }
}

// ==================== LEGACY SSE STREAMING (DEPRECATED) ====================
/**
 * @deprecated This function is LEGACY and should NOT be used.
 * Use sendChatMessage() instead which includes:
 * - MessageStore integration
 * - buildConversationHistoryForAPI() formatting
 * - thread_slug isolation
 * - User context and preferences
 * 
 * This function remains for backward compatibility only.
 * DO NOT CALL THIS FUNCTION.
 */
async function sendStreamingChatMessage(message) {
    console.warn('[DEPRECATED] sendStreamingChatMessage() called - use sendChatMessage() instead');
    const sessionId = ensureSession();

    // Check backend connection
    if (!AppState.isConnected) {
        showNotification('Backend disconnected. Please check Flask server.', 'error');
        return;
    }

    // Add user message
    addChatMessage('user', message);

    // Create AI message container for streaming
    const aiMessageDiv = document.createElement('div');
    aiMessageDiv.className = 'ai-message assistant';
    aiMessageDiv.innerHTML = '<div class="ai-streaming-text"></div>';
    document.getElementById('ai-chat-messages').appendChild(aiMessageDiv);

    const streamingTextDiv = aiMessageDiv.querySelector('.ai-streaming-text');
    let fullResponse = '';

    try {
        // PROMPT INJECTION: Get selected prompts from prompt library
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

        // Connect to SSE stream - FIXED: Use correct agent-specific URL format
        const eventSource = new EventSource(
            `${API_BASE_URL}/api/agent/stream/prime?thread_slug=${sessionId}${promptParams}`
        );

        // Handle content blocks
        eventSource.addEventListener('content_block_delta', (e) => {
            try {
                const data = JSON.parse(e.data);
                if (data.text) {
                    fullResponse += data.text;
                    streamingTextDiv.textContent = fullResponse;
                    // Scroll to bottom
                    const chatMessages = document.getElementById('ai-chat-messages');
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            } catch (error) {
                console.error(' Stream parsing error:', error);
            }
        });

        // Handle message complete
        eventSource.addEventListener('message_stop', async (e) => {
            console.log('Streaming complete');
            eventSource.close();

            // USE VISUALIZATION ENGINE instead of marked.parse()
            console.log(' Processing streamed content through visualization engine...');

            if (typeof TwoRuleStreamProcessor !== 'undefined') {
                try {
                    // Clear the plain text
                    streamingTextDiv.innerHTML = '';

                    // Create processor for visualization
                    const processor = new TwoRuleStreamProcessor(streamingTextDiv);

                    // Process the full response through visualization engine
                    processor.processChunk(fullResponse);
                    // TwoRuleStreamProcessor auto-renders, no finalize needed

                    console.log('Visualization engine processing complete for stream');
                } catch (error) {
                    console.error(' Visualization engine error in stream:', error);
                    // Fallback to basic rendering
                    streamingTextDiv.innerHTML = fullResponse;
                }
            } else {
                console.warn('[WARN] TwoRuleStreamProcessor not available, using plain text');
                streamingTextDiv.innerHTML = fullResponse;
            }

            /*  COMMENTED OUT: Old marked.parse() rendering
            // Render markdown
            if (window.marked) {
                streamingTextDiv.innerHTML = marked.parse(fullResponse);
            }
            */

            // Store in history
            // PHASE 2: Use MessageStore instead of AppState.chatMessages
            const currentThreadId = AppState.currentThreadId || 'prime-ai-default';
            await window.MessageStore.addMessage(currentThreadId, {
                role: 'assistant',
                content: fullResponse,
                timestamp: new Date().toISOString()
            });
        });

        // Handle errors
        eventSource.addEventListener('error', (e) => {
            console.error(' SSE error:', e);
            eventSource.close();
            streamingTextDiv.innerHTML = '<span style="color: #e74c3c;">Streaming error. Please try again.</span>';
            showNotification('Streaming failed. Falling back to standard mode.', 'error');
        });

        // Store eventSource reference
        AppState.eventSource = eventSource;

    } catch (error) {
        console.error(' Streaming setup error:', error);
        showNotification('Failed to start streaming: ' + error.message, 'error');
    }
}

// Update AI message during streaming
function updateAIMessage(text) {
    const streamingText = document.querySelector('.ai-streaming-text');
    if (streamingText) {
        streamingText.textContent += text;
        const chatMessages = document.getElementById('ai-chat-messages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Clean up SSE connections
function closeStreamingConnection() {
    if (AppState.eventSource) {
        console.log(' Closing SSE connection...');
        AppState.eventSource.close();
        AppState.eventSource = null;
    }
}

function updateAIChatContext(tabId) {
    console.log(` Updating AI context for tab: ${tabId}`);
    // In production, send context to backend
}

// ==================== THEME TOGGLE ====================
function initThemeToggle() {
    // Prevent duplicate initialization
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
    console.log('Initializing theme toggle...');

    // Set default theme if not set
    const html = document.documentElement;
    if (!html.getAttribute('data-theme')) {
        html.setAttribute('data-theme', 'dark');
        console.log('Default theme set to: dark');
    }

    toggleBtn.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        html.setAttribute('data-theme', newTheme);
        AppState.theme = newTheme;

        // Update visualization engine theme
        if (window.sidebarVisualizationState) {
            window.sidebarVisualizationState.currentTheme = newTheme;
            window.sidebarVisualizationState.mermaidTheme = newTheme;
        }

        // Reinitialize Mermaid with new theme
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                startOnLoad: false,
                theme: newTheme,
                securityLevel: 'loose',
                fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'
            });
        }

        // Update icon
        const icon = toggleBtn.querySelector('i');
        icon.className = newTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';

        showNotification(`Switched to ${newTheme} theme`, 'info');
    });
}
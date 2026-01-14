/**
 * AGENT INTERACTION WEBSOCKET
 * WebSocket integration for real-time AI-human two-way interaction
 * 
 * Connects to StreamingManager backend to:
 * - Receive input_request messages from AI agents
 * - Send provide_input responses from users
 * - Handle progress_update streaming
 * - Display screenshots and CAPTCHA images
 * 
 * Date: December 16, 2025
 */

const AgentInteractionWebSocket = (function () {

    // WebSocket connection per agent
    const connections = {};

    // Message handlers
    const messageHandlers = {
        'input_request': handleInputRequest,
        'progress_update': handleProgressUpdate,
        'screenshot': handleScreenshot
    };

    /**
     * Connect to StreamingManager WebSocket for specific agent
     * @param {number} agentId - Agent ID (1 = Alpha, 2 = Bravo, etc.)
     * @param {string} sessionId - Session ID from backend
     * @param {string} wsUrl - WebSocket URL (e.g., 'ws://localhost:8080/ws/streaming')
     */
    function connect(agentId, sessionId, wsUrl) {
        if (connections[agentId]) {
            console.log(`Agent ${agentId} already connected to WebSocket`);
            return;
        }

        const fullUrl = `${wsUrl}/${sessionId}`;
        console.log(`Connecting agent ${agentId} to ${fullUrl}`);

        const ws = new WebSocket(fullUrl);

        ws.onopen = () => {
            console.log(`Agent ${agentId} WebSocket connected`);
            connections[agentId] = {
                socket: ws,
                sessionId: sessionId,
                connected: true
            };

            // Send initial handshake
            sendMessage(agentId, {
                type: 'handshake',
                participant: `user_${Date.now()}`,
                agent_id: agentId
            });
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log(`Agent ${agentId} received message:`, data);

                const handler = messageHandlers[data.type];
                if (handler) {
                    handler(agentId, data);
                } else {
                    console.warn(`Unknown message type: ${data.type}`, data);
                }
            } catch (error) {
                console.error(`Error parsing WebSocket message:`, error, event.data);
            }
        };

        ws.onerror = (error) => {
            console.error(`Agent ${agentId} WebSocket error:`, error);
            showNotification(`Connection error for agent ${getAgentName(agentId)}`, 'error');
        };

        ws.onclose = () => {
            console.log(`Agent ${agentId} WebSocket closed`);
            if (connections[agentId]) {
                connections[agentId].connected = false;
            }

            // Attempt reconnect after 5 seconds
            setTimeout(() => {
                if (connections[agentId] && !connections[agentId].connected) {
                    console.log(`Attempting to reconnect agent ${agentId}...`);
                    connect(agentId, sessionId, wsUrl);
                }
            }, 5000);
        };
    }

    /**
     * Disconnect WebSocket for specific agent
     * @param {number} agentId - Agent ID
     */
    function disconnect(agentId) {
        if (connections[agentId] && connections[agentId].socket) {
            connections[agentId].socket.close();
            delete connections[agentId];
            console.log(`Agent ${agentId} WebSocket disconnected`);
        }
    }

    /**
     * Send message to backend via WebSocket
     * @param {number} agentId - Agent ID
     * @param {object} message - Message object
     */
    function sendMessage(agentId, message) {
        const conn = connections[agentId];
        if (!conn || !conn.connected || conn.socket.readyState !== WebSocket.OPEN) {
            console.error(`Agent ${agentId} WebSocket not connected`);
            showNotification(`Cannot send message - agent ${getAgentName(agentId)} disconnected`, 'error');
            return false;
        }

        try {
            conn.socket.send(JSON.stringify(message));
            console.log(`Agent ${agentId} sent message:`, message);
            return true;
        } catch (error) {
            console.error(`Error sending message:`, error);
            showNotification(`Failed to send message to agent ${getAgentName(agentId)}`, 'error');
            return false;
        }
    }

    /**
     * Send user input response to backend
     * @param {number} agentId - Agent ID
     * @param {string} requestId - Request ID from input_request message
     * @param {*} value - User input value (string, number, boolean, or null for cancel)
     */
    function sendInputResponse(agentId, requestId, value) {
        return sendMessage(agentId, {
            type: 'provide_input',
            session_id: connections[agentId]?.sessionId,
            request_id: requestId,
            input_value: value,
            from_participant: `user_${Date.now()}`,
            timestamp: new Date().toISOString()
        });
    }

    // ==================== MESSAGE HANDLERS ====================

    /**
     * Handle input_request message from AI agent
     * Renders inline input request bubble
     * 
     * Message format:
     * {
     *   type: 'input_request',
     *   request_id: 'abc-123',
     *   prompt: 'Enter your 2FA code',
     *   input_type: '2fa_code',  // text, password, choice, 2fa_code, captcha
     *   choices: ['Yes', 'No'],  // For choice type
     *   required: true,
     *   timeout_seconds: 300,
     *   metadata: {
     *     screenshot: 'base64_data...',
     *     captcha_url: 'https://...'
     *   }
     * }
     */
    function handleInputRequest(agentId, data) {
        console.log(`Agent ${agentId} input request:`, data);

        // Render inline interaction bubble
        if (typeof AgentInteractionBubbles !== 'undefined') {
            AgentInteractionBubbles.renderInputRequestBubble(agentId, data);
        } else {
            console.error('AgentInteractionBubbles module not loaded');
            showNotification(`Cannot display input request - module not loaded`, 'error');
        }
    }

    /**
     * Handle progress_update message from AI agent
     * Updates inline progress bubble
     * 
     * Message format:
     * {
     *   type: 'progress_update',
     *   message: 'Processing documents...',
     *   current_step: 3,
     *   total_steps: 10,
     *   percent: 30
     * }
     */
    function handleProgressUpdate(agentId, data) {
        console.log(`Agent ${agentId} progress update:`, data);

        // Render/update inline progress bubble
        if (typeof AgentInteractionBubbles !== 'undefined') {
            AgentInteractionBubbles.renderProgressBubble(agentId, data);
        } else {
            console.error('AgentInteractionBubbles module not loaded');
        }
    }

    /**
     * Handle screenshot message from AI agent
     * Displays screenshot in existing input request bubble
     * 
     * Message format:
     * {
     *   type: 'screenshot',
     *   request_id: 'abc-123',
     *   image_data: 'base64_data...',
     *   format: 'png'
     * }
     */
    function handleScreenshot(agentId, data) {
        console.log(`Agent ${agentId} screenshot received:`, data);

        // Find existing input request bubble
        const requestData = AgentInteractionBubbles?.activeRequests?.[agentId];
        if (requestData && requestData.bubble_element) {
            const screenshotDiv = requestData.bubble_element.querySelector('.interaction-screenshot');
            if (screenshotDiv) {
                screenshotDiv.innerHTML = `<img src="data:image/${data.format || 'png'};base64,${data.image_data}" alt="Screenshot">`;
            }
        }
    }

    // ==================== HELPER FUNCTIONS ====================

    /**
     * Get agent name from agent ID
     * @param {number} agentId - Agent ID (1, 2, 3, etc.)
     * @returns {string} Agent name (Alpha, Bravo, Charlie, etc.)
     */
    function getAgentName(agentId) {
        const names = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot'];
        return names[agentId - 1] || `Agent ${agentId}`;
    }

    /**
     * Check if agent is connected
     * @param {number} agentId - Agent ID
     * @returns {boolean} True if connected
     */
    function isConnected(agentId) {
        return connections[agentId]?.connected === true;
    }

    /**
     * Get connection info for agent
     * @param {number} agentId - Agent ID
     * @returns {object|null} Connection info or null if not connected
     */
    function getConnection(agentId) {
        return connections[agentId] || null;
    }

    // Public API
    return {
        connect,
        disconnect,
        sendMessage,
        sendInputResponse,
        isConnected,
        getConnection
    };
})();

// Expose globally
if (typeof window !== 'undefined') {
    window.AgentInteractionWebSocket = AgentInteractionWebSocket;
}

/**
 * USAGE EXAMPLE:
 * 
 * // 1. Connect to StreamingManager WebSocket
 * AgentInteractionWebSocket.connect(
 *     1,  // Agent ID (Alpha)
 *     'session-abc-123',  // Session ID from backend
 *     'ws://localhost:8080/ws/streaming'  // WebSocket URL
 * );
 * 
 * // 2. Wait for input_request message from backend
 * // WebSocket will automatically render inline bubble via AgentInteractionBubbles
 * 
 * // 3. User submits input via bubble UI
 * // AgentInteractionBubbles.submitInput() will call sendInputResponse()
 * 
 * // 4. Receive progress_update messages
 * // WebSocket will automatically update inline progress bubble
 * 
 * // 5. Disconnect when done
 * AgentInteractionWebSocket.disconnect(1);
 */

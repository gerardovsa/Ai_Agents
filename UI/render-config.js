/**
 * AI Agent Platform - Render Configuration
 * Automatically detects environment and uses appropriate API endpoints
 */

const RenderConfig = {
    // Environment detection
    isProduction: window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1',
    
    // Render service URLs
    render: {
        flask: 'https://inhouseprint-flask.onrender.com',
        streamlit: 'https://inhouseprint-streamlit.onrender.com'
    },
    
    // Local development URLs
    local: {
        flask: 'http://localhost:4000',
        vsaAgent: 'http://localhost:5300'
    },
    
    /**
     * Get the appropriate API base URL based on environment
     */
    getApiBaseUrl() {
        if (this.isProduction) {
            console.log('🌐 Production Mode: Using Render Flask endpoint');
            return this.render.flask;
        } else {
            console.log('🔧 Development Mode: Using localhost endpoints');
            return this.local.flask;
        }
    },
    
    /**
     * Get VSA Agent API URL
     */
    getVsaApiUrl() {
        if (this.isProduction) {
            // In production, VSA might be on Render too (add when deployed)
            console.log('⚠️ VSA Agent not yet deployed to Render, using localhost');
            return this.local.vsaAgent;
        } else {
            return this.local.vsaAgent;
        }
    },
    
    /**
     * Get full endpoint URL
     */
    getEndpoint(path) {
        return `${this.getApiBaseUrl()}${path}`;
    },
    
    /**
     * Test connection to Render services
     */
    async testConnection() {
        console.log('🔍 Testing Render connection...');
        
        try {
            const response = await fetch(`${this.render.flask}/health`, {
                method: 'GET',
                mode: 'cors',
                cache: 'no-cache'
            });
            
            const data = await response.json();
            console.log('✅ Render Flask connected:', data);
            return { success: true, data };
        } catch (error) {
            console.error('❌ Render connection failed:', error);
            return { success: false, error: error.message };
        }
    },
    
    /**
     * Get AI model configuration from Render
     */
    async getAiModels() {
        try {
            const response = await fetch(this.getEndpoint('/api/agent/models'));
            return await response.json();
        } catch (error) {
            console.error('❌ Failed to fetch AI models:', error);
            return {
                models: ['deepseek-chat', 'claude-sonnet-4', 'gpt-4'],
                default: 'deepseek-chat'
            };
        }
    },
    
    /**
     * Get available tools from backend
     */
    async getAvailableTools() {
        try {
            const response = await fetch(this.getEndpoint('/api/agent/tools'));
            return await response.json();
        } catch (error) {
            console.error('❌ Failed to fetch tools:', error);
            return { tools: [] };
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RenderConfig;
}

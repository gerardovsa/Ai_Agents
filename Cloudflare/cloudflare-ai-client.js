/**
 * Cloudflare AI Worker Client
 * 
 * Core module for connecting to Cloudflare Workers AI API
 * Supports text generation, embeddings, image analysis, and more
 */

const https = require('https');
const fs = require('fs').promises;
const path = require('path');

class CloudflareAIClient {
    constructor(options = {}) {
        this.accountId = options.accountId || 'd31a1c9ec65f373f4008216c30b071cc';
        this.apiToken = options.apiToken || process.env.CLOUDFLARE_API_TOKEN;
        this.baseUrl = `https://api.cloudflare.com/client/v4/accounts/${this.accountId}/ai`;
        
        if (!this.apiToken) {
            throw new Error('❌ API token is required. Set CLOUDFLARE_API_TOKEN environment variable.');
        }
        
        console.log('✅ Cloudflare AI Client initialized');
    }

    /**
     * Make API request to Cloudflare
     */
    async makeRequest(endpoint, method = 'POST', data = null) {
        return new Promise((resolve, reject) => {
            // Construct full path
            const fullPath = `/client/v4/accounts/${this.accountId}/ai${endpoint}`;
            
            const requestData = data ? JSON.stringify(data) : null;
            
            const options = {
                hostname: 'api.cloudflare.com',
                port: 443,
                path: fullPath,
                method: method,
                headers: {
                    'Authorization': `Bearer ${this.apiToken}`,
                    'Content-Type': 'application/json'
                }
            };

            if (requestData) {
                options.headers['Content-Length'] = Buffer.byteLength(requestData);
            }

            console.log(`🔧 Making ${method} request to: ${fullPath}`);

            const req = https.request(options, (res) => {
                let body = '';

                res.on('data', (chunk) => {
                    body += chunk;
                });

                res.on('end', () => {
                    try {
                        const response = JSON.parse(body);
                        
                        if (res.statusCode >= 200 && res.statusCode < 300) {
                            console.log('✅ Request successful');
                            resolve(response);
                        } else {
                            console.error('❌ API Error:', response);
                            reject(new Error(`API Error: ${response.errors?.[0]?.message || 'Unknown error'}`));
                        }
                    } catch (error) {
                        console.error('❌ Parse error:', error);
                        reject(error);
                    }
                });
            });

            req.on('error', (error) => {
                console.error('❌ Request failed:', error);
                reject(error);
            });

            if (requestData) {
                req.write(requestData);
            }

            req.end();
        });
    }

    /**
     * Text Generation using Llama models
     */
    async generateText(prompt, options = {}) {
        console.log('🔧 Generating text with AI...');
        
        const model = options.model || '@cf/meta/llama-3.1-8b-instruct';
        const maxTokens = options.maxTokens || 2048;
        
        const payload = {
            messages: [
                { role: 'system', content: options.systemPrompt || 'You are a helpful AI assistant.' },
                { role: 'user', content: prompt }
            ],
            max_tokens: maxTokens,
            temperature: options.temperature || 0.7,
            stream: false
        };

        try {
            const response = await this.makeRequest(`/run/${model}`, 'POST', payload);
            console.log('✅ Text generation complete');
            return response.result?.response || response.result;
        } catch (error) {
            console.error('❌ Text generation failed:', error.message);
            throw error;
        }
    }

    /**
     * Generate embeddings for text
     */
    async generateEmbeddings(text, model = '@cf/baai/bge-base-en-v1.5') {
        console.log('🔧 Generating embeddings...');
        
        const payload = {
            text: Array.isArray(text) ? text : [text]
        };

        try {
            const response = await this.makeRequest(`/run/${model}`, 'POST', payload);
            console.log('✅ Embeddings generated');
            return response.result;
        } catch (error) {
            console.error('❌ Embedding generation failed:', error.message);
            throw error;
        }
    }

    /**
     * Image classification
     */
    async classifyImage(imageBuffer, model = '@cf/microsoft/resnet-50') {
        console.log('🔧 Classifying image...');
        
        const base64Image = imageBuffer.toString('base64');
        const payload = { image: base64Image };

        try {
            const response = await this.makeRequest(`/run/${model}`, 'POST', payload);
            console.log('✅ Image classification complete');
            return response.result;
        } catch (error) {
            console.error('❌ Image classification failed:', error.message);
            throw error;
        }
    }

    /**
     * Get available models
     */
    async listModels() {
        console.log('🔧 Fetching available models...');
        
        try {
            const response = await this.makeRequest('/models', 'GET');
            console.log('✅ Models list retrieved');
            return response.result;
        } catch (error) {
            console.error('❌ Failed to fetch models:', error.message);
            throw error;
        }
    }

    /**
     * Verify API token by making a simple AI call
     */
    async verifyToken() {
        console.log('🔧 Verifying API token...');
        
        try {
            // Make a simple AI call to verify the token works
            const response = await this.generateText('Respond with only: "Token verified"', {
                maxTokens: 10,
                temperature: 0
            });
            
            console.log('✅ Token is valid - Workers AI is accessible');
            return {
                status: 'Active',
                verified: true,
                accountId: this.accountId,
                message: response
            };
        } catch (error) {
            console.error('❌ Token verification failed');
            throw error;
        }
    }

    /**
     * Analyze and debug Cloudflare errors
     */
    async diagnoseError(errorCode, errorMessage) {
        console.log(`🔍 Diagnosing Cloudflare Error ${errorCode}...`);
        
        const prompt = `You are a Cloudflare expert. Analyze this error and provide:
1. Root cause analysis
2. Step-by-step solution
3. Prevention tips

Error Code: ${errorCode}
Error Message: ${errorMessage}

Provide a clear, actionable response.`;

        try {
            const diagnosis = await this.generateText(prompt, {
                systemPrompt: 'You are a Cloudflare infrastructure expert specializing in error diagnosis and resolution.',
                maxTokens: 1500
            });
            
            return {
                errorCode,
                errorMessage,
                diagnosis,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error('❌ Diagnosis failed:', error.message);
            throw error;
        }
    }
}

module.exports = CloudflareAIClient;

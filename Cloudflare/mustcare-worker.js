/**
 * Cloudflare Worker for mustcare.valorsynergysuite.com
 * Acts as API Gateway/Proxy to Google Cloud Backend
 */

export default {
    async fetch(request, env) {
        try {
            const url = new URL(request.url);
            
            // Health check endpoint
            if (url.pathname === '/health' || url.pathname === '/api/health') {
                return new Response(JSON.stringify({
                    status: 'ok',
                    timestamp: new Date().toISOString(),
                    worker: 'mustcare-api-gateway'
                }), {
                    status: 200,
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    }
                });
            }

            // CORS Headers
            const corsHeaders = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            };

            // Handle OPTIONS preflight
            if (request.method === 'OPTIONS') {
                return new Response(null, {
                    status: 204,
                    headers: corsHeaders
                });
            }

            // Proxy to Google Cloud Backend
            // Try HTTPS first, fallback to HTTP if needed
            const backendHost = env.BACKEND_URL || 'http://34.143.73.2';
            const backendUrl = `${backendHost}${url.pathname}${url.search}`;
            
            console.log(`Proxying request: ${request.method} ${backendUrl}`);

            // Create new headers - pass through most headers but set critical ones
            const proxyHeaders = new Headers();
            
            // Copy important headers from original request
            for (const [key, value] of request.headers.entries()) {
                // Skip headers that should not be forwarded
                if (!['host', 'cf-ray', 'cf-connecting-ip', 'cf-ipcountry'].includes(key.toLowerCase())) {
                    proxyHeaders.set(key, value);
                }
            }
            
            // Set required headers for backend
            proxyHeaders.set('X-Forwarded-Host', url.hostname);
            proxyHeaders.set('X-Forwarded-Proto', 'https');
            proxyHeaders.set('X-Real-IP', request.headers.get('CF-Connecting-IP') || '');
            proxyHeaders.set('X-Forwarded-For', request.headers.get('CF-Connecting-IP') || '');

            // Prepare fetch options - only include body for methods that support it
            const fetchOptions = {
                method: request.method,
                headers: proxyHeaders,
                signal: AbortSignal.timeout(30000)
            };

            // Only add body for POST, PUT, PATCH, DELETE methods
            if (request.method !== 'GET' && request.method !== 'HEAD') {
                fetchOptions.body = request.body;
            }

            const response = await fetch(backendUrl, fetchOptions);

            // Add CORS headers to response
            const newHeaders = new Headers(response.headers);
            Object.entries(corsHeaders).forEach(([key, value]) => {
                newHeaders.set(key, value);
            });

            return new Response(response.body, {
                status: response.status,
                statusText: response.statusText,
                headers: newHeaders
            });

        } catch (error) {
            console.error('Worker Error:', error);

            // Return JSON error instead of crashing
            return new Response(JSON.stringify({
                error: 'Worker Error',
                message: error.message || 'Internal server error',
                timestamp: new Date().toISOString()
            }), {
                status: 500,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            });
        }
    }
};

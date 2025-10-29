/**
 * Cloudflare Account Manager
 * 
 * Manage Cloudflare domains, DNS, settings, alerts, and configuration
 */

const https = require('https');

class CloudflareManager {
    constructor(options = {}) {
        this.accountId = options.accountId || 'd31a1c9ec65f373f4008216c30b071cc';
        // Use the AI_AGENT token if available, fallback to API_TOKEN
        this.apiToken = options.apiToken || process.env.CLOUDFLARE_AI_AGENT_TOKEN || process.env.CLOUDFLARE_API_TOKEN;
        
        if (!this.apiToken) {
            throw new Error('❌ API token is required. Set CLOUDFLARE_AI_AGENT_TOKEN or CLOUDFLARE_API_TOKEN environment variable.');
        }
        
        console.log('✅ Cloudflare Manager initialized');
    }

    /**
     * Make API request to Cloudflare
     */
    async makeRequest(path, method = 'GET', data = null) {
        return new Promise((resolve, reject) => {
            const requestData = data ? JSON.stringify(data) : null;
            
            const options = {
                hostname: 'api.cloudflare.com',
                port: 443,
                path: path,
                method: method,
                headers: {
                    'Authorization': `Bearer ${this.apiToken}`,
                    'Content-Type': 'application/json'
                }
            };

            if (requestData) {
                options.headers['Content-Length'] = Buffer.byteLength(requestData);
            }

            console.log(`🔧 ${method} ${path}`);

            const req = https.request(options, (res) => {
                let body = '';

                res.on('data', (chunk) => {
                    body += chunk;
                });

                res.on('end', () => {
                    try {
                        const response = JSON.parse(body);
                        
                        if (response.success) {
                            console.log('✅ Request successful');
                            resolve(response);
                        } else {
                            console.error('❌ API Error:', response.errors);
                            reject(new Error(`API Error: ${response.errors?.[0]?.message || 'Unknown error'}`));
                        }
                    } catch (error) {
                        console.error('❌ Parse error:', error);
                        console.error('Response:', body);
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
     * List all zones (domains) in account
     */
    async listZones() {
        console.log('🔧 Fetching zones (domains)...');
        
        try {
            const response = await this.makeRequest(`/client/v4/zones?account.id=${this.accountId}&per_page=50`);
            console.log(`✅ Found ${response.result.length} zone(s)`);
            return response.result;
        } catch (error) {
            console.error('❌ Failed to fetch zones:', error.message);
            throw error;
        }
    }

    /**
     * Get zone details
     */
    async getZoneDetails(zoneId) {
        console.log(`🔧 Fetching zone details for ${zoneId}...`);
        
        try {
            const response = await this.makeRequest(`/client/v4/zones/${zoneId}`);
            return response.result;
        } catch (error) {
            console.error('❌ Failed to fetch zone details:', error.message);
            throw error;
        }
    }

    /**
     * Get DNS records for a zone
     */
    async getDNSRecords(zoneId) {
        console.log(`🔧 Fetching DNS records for zone ${zoneId}...`);
        
        try {
            const response = await this.makeRequest(`/client/v4/zones/${zoneId}/dns_records?per_page=100`);
            console.log(`✅ Found ${response.result.length} DNS record(s)`);
            return response.result;
        } catch (error) {
            console.error('❌ Failed to fetch DNS records:', error.message);
            throw error;
        }
    }

    /**
     * Get zone settings
     */
    async getZoneSettings(zoneId) {
        console.log(`🔧 Fetching settings for zone ${zoneId}...`);
        
        try {
            const response = await this.makeRequest(`/client/v4/zones/${zoneId}/settings`);
            return response.result;
        } catch (error) {
            console.error('❌ Failed to fetch zone settings:', error.message);
            throw error;
        }
    }

    /**
     * Get account alerts/notifications
     */
    async getAlerts() {
        console.log('🔧 Fetching account alerts...');
        
        try {
            const response = await this.makeRequest(`/client/v4/accounts/${this.accountId}/alerting/v3/policies`);
            console.log(`✅ Found ${response.result?.length || 0} alert(s)`);
            return response.result || [];
        } catch (error) {
            console.error('❌ Failed to fetch alerts:', error.message);
            // Return empty array if alerts endpoint fails
            return [];
        }
    }

    /**
     * Get analytics for a zone
     */
    async getZoneAnalytics(zoneId, since = -10080) {
        console.log(`🔧 Fetching analytics for zone ${zoneId}...`);
        
        try {
            const response = await this.makeRequest(
                `/client/v4/zones/${zoneId}/analytics/dashboard?since=${since}`
            );
            return response.result;
        } catch (error) {
            console.error('❌ Failed to fetch analytics:', error.message);
            return null;
        }
    }

    /**
     * Get account details
     */
    async getAccountInfo() {
        console.log('🔧 Fetching account information...');
        
        try {
            const response = await this.makeRequest(`/client/v4/accounts/${this.accountId}`);
            return response.result;
        } catch (error) {
            console.error('❌ Failed to fetch account info:', error.message);
            throw error;
        }
    }

    /**
     * Get zone health check
     */
    async getZoneHealth(zoneId) {
        console.log(`🔧 Checking zone health for ${zoneId}...`);
        
        try {
            const [details, settings] = await Promise.all([
                this.getZoneDetails(zoneId),
                this.getZoneSettings(zoneId)
            ]);

            const health = {
                status: details.status,
                paused: details.paused,
                nameServers: details.name_servers,
                originalNameServers: details.original_name_servers,
                plan: details.plan?.name || 'Unknown',
                ssl: settings.find(s => s.id === 'ssl')?.value || 'unknown',
                securityLevel: settings.find(s => s.id === 'security_level')?.value || 'unknown',
                alwaysOnline: settings.find(s => s.id === 'always_online')?.value || 'unknown'
            };

            return health;
        } catch (error) {
            console.error('❌ Failed to check zone health:', error.message);
            throw error;
        }
    }

    /**
     * Get comprehensive domain overview
     */
    async getDomainOverview() {
        console.log('📊 Generating comprehensive domain overview...\n');
        
        try {
            // Get zones
            const zones = await this.listZones();
            
            if (zones.length === 0) {
                return {
                    zones: [],
                    account: await this.getAccountInfo(),
                    alerts: await this.getAlerts()
                };
            }

            // Get details for each zone
            const zoneDetails = await Promise.all(
                zones.map(async (zone) => {
                    try {
                        const [dns, health, analytics] = await Promise.all([
                            this.getDNSRecords(zone.id),
                            this.getZoneHealth(zone.id),
                            this.getZoneAnalytics(zone.id)
                        ]);

                        return {
                            ...zone,
                            dns,
                            health,
                            analytics
                        };
                    } catch (error) {
                        console.error(`⚠️ Error fetching details for ${zone.name}:`, error.message);
                        return {
                            ...zone,
                            error: error.message
                        };
                    }
                })
            );

            return {
                zones: zoneDetails,
                account: await this.getAccountInfo(),
                alerts: await this.getAlerts()
            };
        } catch (error) {
            console.error('❌ Failed to generate overview:', error.message);
            throw error;
        }
    }
}

module.exports = CloudflareManager;

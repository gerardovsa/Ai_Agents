/**
 * Add Worker Route via API
 * This script adds a route to connect the Worker to mustcare.valorsynergysuite.com
 */

const https = require('https');

const ACCOUNT_ID = 'd31a1c9ec65f373f4008216c30b071cc';
const ZONE_ID = 'd575f903247d1653725514134aedc208';
const API_TOKEN = process.env.CLOUDFLARE_AI_AGENT_TOKEN || process.env.CLOUDFLARE_API_TOKEN;

/**
 * Make an HTTPS request to Cloudflare API
 */
function makeRequest(method, path, data = null) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'api.cloudflare.com',
            path: `/client/v4${path}`,
            method: method,
            headers: {
                'Authorization': `Bearer ${API_TOKEN}`,
                'Content-Type': 'application/json'
            }
        };

        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => {
                try {
                    const response = JSON.parse(body);
                    if (response.success) {
                        resolve(response.result);
                    } else {
                        reject(new Error(`API Error: ${JSON.stringify(response.errors)}`));
                    }
                } catch (error) {
                    reject(new Error(`Parse Error: ${error.message}\nBody: ${body}`));
                }
            });
        });

        req.on('error', reject);
        
        if (data) {
            req.write(JSON.stringify(data));
        }
        
        req.end();
    });
}

/**
 * Check if route already exists
 */
async function checkExistingRoute() {
    console.log('🔍 Checking for existing routes...');
    try {
        const routes = await makeRequest('GET', `/zones/${ZONE_ID}/workers/routes`);
        
        const existingRoute = routes.find(r => r.pattern === 'mustcare.valorsynergysuite.com/*');
        
        if (existingRoute) {
            console.log('✅ Route already exists:');
            console.log(JSON.stringify(existingRoute, null, 2));
            return existingRoute;
        }
        
        console.log('📋 Found', routes.length, 'existing routes');
        return null;
    } catch (error) {
        console.error('❌ Failed to check routes:', error.message);
        return null;
    }
}

/**
 * Add route for mustcare.valorsynergysuite.com
 */
async function addRoute() {
    console.log('🚀 Adding route for mustcare.valorsynergysuite.com...\n');
    
    // First check if route exists
    const existing = await checkExistingRoute();
    if (existing) {
        console.log('\n✅ Route already configured - nothing to do!');
        return;
    }
    
    // Add new route
    console.log('\n📝 Creating new route...');
    const routeData = {
        pattern: 'mustcare.valorsynergysuite.com/*',
        script: 'mustcare-worker'
    };
    
    try {
        const result = await makeRequest('POST', `/zones/${ZONE_ID}/workers/routes`, routeData);
        
        console.log('\n✅ Route added successfully!');
        console.log(JSON.stringify(result, null, 2));
        console.log('\n🎉 Your Worker is now live at: https://mustcare.valorsynergysuite.com');
        console.log('🔧 Test health endpoint: https://mustcare.valorsynergysuite.com/health');
    } catch (error) {
        console.error('\n❌ Failed to add route:', error.message);
        console.log('\n📋 Manual Steps:');
        console.log('1. Go to: https://dash.cloudflare.com/' + ACCOUNT_ID + '/workers-and-pages');
        console.log('2. Click on "mustcare-worker"');
        console.log('3. Go to "Settings" → "Triggers"');
        console.log('4. Click "Add Route"');
        console.log('5. Enter: mustcare.valorsynergysuite.com/*');
        console.log('6. Select zone: valorsynergysuite.com');
        console.log('7. Click "Add Route"');
    }
}

// Run
addRoute().catch(error => {
    console.error('❌ Fatal error:', error);
    process.exit(1);
});

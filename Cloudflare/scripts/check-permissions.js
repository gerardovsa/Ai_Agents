/**
 * Check what permissions and access the current API token has
 */

const https = require('https');
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

// Use the AI_AGENT token if available, fallback to API_TOKEN
const API_TOKEN = process.env.CLOUDFLARE_AI_AGENT_TOKEN || process.env.CLOUDFLARE_API_TOKEN;

console.log(`🔑 Using token: ${API_TOKEN ? API_TOKEN.substring(0, 10) + '...' : 'NOT FOUND'}\n`);

async function testEndpoint(name, path, method = 'GET') {
    return new Promise((resolve) => {
        const options = {
            hostname: 'api.cloudflare.com',
            port: 443,
            path: path,
            method: method,
            headers: {
                'Authorization': `Bearer ${API_TOKEN}`,
                'Content-Type': 'application/json'
            }
        };

        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => { body += chunk; });
            res.on('end', () => {
                try {
                    const response = JSON.parse(body);
                    resolve({
                        name,
                        path,
                        status: res.statusCode,
                        success: response.success,
                        error: response.errors?.[0]?.message
                    });
                } catch (error) {
                    resolve({
                        name,
                        path,
                        status: res.statusCode,
                        success: false,
                        error: 'Parse error'
                    });
                }
            });
        });

        req.on('error', (error) => {
            resolve({
                name,
                path,
                status: 0,
                success: false,
                error: error.message
            });
        });

        req.end();
    });
}

async function checkPermissions() {
    console.log('🔍 Checking API Token Permissions...\n');
    console.log('━'.repeat(80));

    const tests = [
        // Token info
        { name: 'Token Verification', path: '/client/v4/user/tokens/verify' },

        // Account access
        { name: 'Account Info', path: '/client/v4/accounts/d31a1c9ec65f373f4008216c30b071cc' },
        { name: 'List Zones', path: '/client/v4/zones' },

        // Workers AI (should work)
        { name: 'Workers AI Models', path: '/client/v4/accounts/d31a1c9ec65f373f4008216c30b071cc/ai/models' },

        // Workers
        { name: 'List Workers', path: '/client/v4/accounts/d31a1c9ec65f373f4008216c30b071cc/workers/scripts' },

        // Alerts
        { name: 'Alerting Policies', path: '/client/v4/accounts/d31a1c9ec65f373f4008216c30b071cc/alerting/v3/policies' },

        // Analytics
        { name: 'Account Analytics', path: '/client/v4/accounts/d31a1c9ec65f373f4008216c30b071cc/analytics/dashboard' },
    ];

    const results = [];

    for (const test of tests) {
        process.stdout.write(`Testing: ${test.name}...`);
        const result = await testEndpoint(test.name, test.path);
        results.push(result);

        if (result.success) {
            console.log(' Accessible');
        } else {
            console.log(`  ${result.error || 'Failed'}`);
        }
    }

    console.log('\n' + '━'.repeat(80));
    console.log('📊 SUMMARY');
    console.log('━'.repeat(80));

    const accessible = results.filter(r => r.success);
    const denied = results.filter(r => !r.success);

    console.log(`\nccessible Endpoints: ${accessible.length}`);
    accessible.forEach(r => console.log(`   • ${r.name}`));

    console.log(`\n Restricted Endpoints: ${denied.length}`);
    denied.forEach(r => console.log(`   • ${r.name}: ${r.error}`));

    console.log('\n' + '━'.repeat(80));
    console.log('💡 RECOMMENDATION');
    console.log('━'.repeat(80));

    if (accessible.some(r => r.name.includes('Workers AI'))) {
        console.log('\nour token has Workers AI access.');
        console.log('   You can use AI features for diagnostics and chat.\n');
    }

    if (denied.some(r => r.name === 'Account Info' || r.name === 'List Zones')) {
        console.log('\n⚠️  Your token does NOT have account/domain management access.');
        console.log('   To view domains and DNS settings, you need a token with:');
        console.log('   • Zone:Read permission');
        console.log('   • Account:Read permission');
        console.log('\n   Create a new API token at:');
        console.log('   https://dash.cloudflare.com/profile/api-tokens\n');
    }
}

checkPermissions().catch(console.error);

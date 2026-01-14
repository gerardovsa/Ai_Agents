/**
 * Check Workers and get logs
 */

const https = require('https');
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const API_TOKEN = process.env.CLOUDFLARE_AI_AGENT_TOKEN || process.env.CLOUDFLARE_API_TOKEN;
const ACCOUNT_ID = 'd31a1c9ec65f373f4008216c30b071cc';

async function makeRequest(path) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'api.cloudflare.com',
            port: 443,
            path: path,
            method: 'GET',
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
                    if (response.success) {
                        resolve(response.result);
                    } else {
                        reject(new Error(response.errors?.[0]?.message || 'API Error'));
                    }
                } catch (error) {
                    reject(error);
                }
            });
        });

        req.on('error', reject);
        req.end();
    });
}

async function checkWorkers() {
    console.log('\n🔧 CHECKING CLOUDFLARE WORKERS\n');
    console.log('━'.repeat(80));

    try {
        // Get all Workers
        console.log('\n📋 Fetching deployed Workers...\n');
        const workers = await makeRequest(`/client/v4/accounts/${ACCOUNT_ID}/workers/scripts`);

        if (workers.length === 0) {
            console.log('⚠️  No Workers found in account.\n');
            console.log('💡 This might mean:');
            console.log('   1. The error is from a different type of Cloudflare configuration');
            console.log('   2. Workers are deployed but not showing in API');
            console.log('   3. The subdomain might be using a different routing method\n');
            return;
        }

        console.log(`Found ${workers.length} Worker(s):\n`);

        for (const worker of workers) {
            console.log(`📦 ${worker.id}`);
            console.log(`   Created: ${new Date(worker.created_on).toLocaleString()}`);
            console.log(`   Modified: ${new Date(worker.modified_on).toLocaleString()}`);

            // Try to get routes
            try {
                const routes = await makeRequest(`/client/v4/accounts/${ACCOUNT_ID}/workers/scripts/${worker.id}/routes`);
                if (routes.length > 0) {
                    console.log(`   Routes:`);
                    routes.forEach(route => {
                        console.log(`      • ${route.pattern}`);
                    });
                }
            } catch (error) {
                console.log(`   ⚠️  Could not fetch routes`);
            }

            console.log('');
        }

        // Check zone routes
        console.log('\n🌐 Checking Zone-specific Worker Routes...\n');
        const zones = await makeRequest(`/client/v4/zones?account.id=${ACCOUNT_ID}`);

        for (const zone of zones) {
            console.log(`📍 ${zone.name}:`);
            try {
                const routes = await makeRequest(`/client/v4/zones/${zone.id}/workers/routes`);
                if (routes.length > 0) {
                    routes.forEach(route => {
                        console.log(`   {route.pattern} → ${route.script || 'No script'}`);
                    });
                } else {
                    console.log(`   ℹ️  No Worker routes configured`);
                }
            } catch (error) {
                console.log(`    Could not fetch routes: ${error.message}`);
            }
            console.log('');
        }

    } catch (error) {
        console.error(' Error:', error.message);
    }

    console.log('━'.repeat(80));
    console.log('\n💡 NEXT STEPS:\n');
    console.log('1. Check if mustcare.valorsynergysuite.com uses a Worker');
    console.log('2. If yes, review Worker logs in Cloudflare Dashboard');
    console.log('3. If no, the issue might be with the backend server (34.143.73.2)');
    console.log('4. Check if the backend server is responding properly\n');
}

checkWorkers();

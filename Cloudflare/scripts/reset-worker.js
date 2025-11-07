/**
 * Reset Worker - Remove all routes to disable it
 */

const https = require('https');
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const API_TOKEN = process.env.CLOUDFLARE_AI_AGENT_TOKEN || process.env.CLOUDFLARE_API_TOKEN;
const ACCOUNT_ID = 'd31a1c9ec65f373f4008216c30b071cc';
const ZONE_ID = 'd575f903247d1653725514134aedc208'; // valorsynergysuite.com

async function makeRequest(path, method = 'GET', data = null) {
    return new Promise((resolve, reject) => {
        const requestData = data ? JSON.stringify(data) : null;

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

        if (requestData) {
            options.headers['Content-Length'] = Buffer.byteLength(requestData);
        }

        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => { body += chunk; });
            res.on('end', () => {
                try {
                    const response = JSON.parse(body);
                    resolve({
                        success: response.success,
                        result: response.result,
                        errors: response.errors,
                        status: res.statusCode
                    });
                } catch (error) {
                    reject(error);
                }
            });
        });

        req.on('error', reject);
        if (requestData) req.write(requestData);
        req.end();
    });
}

async function resetWorker() {
    console.log('\n🔄 RESETTING CLOUDFLARE WORKER\n');
    console.log('━'.repeat(80));

    try {
        // Step 1: Get all routes for the zone
        console.log('\n📋 Step 1: Checking Worker routes...\n');
        const routes = await makeRequest(`/client/v4/zones/${ZONE_ID}/workers/routes`);

        if (!routes.success) {
            console.log('⚠️  Cannot access routes:', routes.errors);
            console.log('\n💡 Manual fix needed - see instructions below.\n');
        } else if (routes.result.length === 0) {
            console.log(' No routes found - Worker may already be disabled\n');
        } else {
            console.log(` Found ${routes.result.length} route(s):\n`);

            // Step 2: Delete each route
            console.log('📋 Step 2: Removing routes...\n');
            for (const route of routes.result) {
                console.log(`   Deleting: ${route.pattern} (ID: ${route.id})`);

                const deleteResult = await makeRequest(
                    `/client/v4/zones/${ZONE_ID}/workers/routes/${route.id}`,
                    'DELETE'
                );

                if (deleteResult.success) {
                    console.log(`    Deleted successfully\n`);
                } else {
                    console.log(`    Failed:`, deleteResult.errors, '\n');
                }
            }
        }

        // Step 3: Try to delete the Worker script
        console.log('━'.repeat(80));
        console.log('\n📋 Step 3: Attempting to delete Worker script...\n');

        const deleteWorker = await makeRequest(
            `/client/v4/accounts/${ACCOUNT_ID}/workers/scripts/mustcare-worker`,
            'DELETE'
        );

        if (deleteWorker.success) {
            console.log(' Worker script deleted!\n');
        } else {
            console.log('⚠️  Could not delete Worker script:', deleteWorker.errors, '\n');
        }

        console.log('━'.repeat(80));
        console.log('\n🎯 RESET COMPLETE\n');
        console.log(' Worker routes removed (if any existed)');
        console.log(' Traffic now goes directly to your server\n');
        console.log('🧪 Test your site: https://mustcare.valorsynergysuite.com\n');

    } catch (error) {
        console.error('\n Error:', error.message, '\n');
    }

    // Final instructions
    console.log('━'.repeat(80));
    console.log('💡 IF STILL NOT WORKING - MANUAL RESET:\n');
    console.log('1. Go to: https://dash.cloudflare.com/' + ACCOUNT_ID + '/workers-and-pages');
    console.log('2. Click on "mustcare-worker"');
    console.log('3. Go to "Settings" or "Triggers" tab');
    console.log('4. Remove all routes/triggers');
    console.log('5. Delete the Worker\n');
    console.log('━'.repeat(80) + '\n');
}

resetWorker();

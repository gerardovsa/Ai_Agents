/**
 * Test Live Worker Deployment
 * Tests both workers.dev URL and custom domain to verify routing
 */

const https = require('https');

const WORKER_DEV_URL = 'mustcare-worker.gerardo-d31.workers.dev';
const CUSTOM_DOMAIN = 'mustcare.valorsynergysuite.com';

/**
 * Make HTTPS GET request
 */
function testEndpoint(hostname, path = '/health') {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: hostname,
            path: path,
            method: 'GET',
            headers: {
                'User-Agent': 'Cloudflare-Test/1.0'
            }
        };

        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    headers: res.headers,
                    body: body
                });
            });
        });

        req.on('error', (error) => {
            resolve({
                statusCode: 0,
                error: error.message
            });
        });

        req.setTimeout(10000, () => {
            req.destroy();
            resolve({
                statusCode: 0,
                error: 'Request timeout'
            });
        });

        req.end();
    });
}

/**
 * Test Worker deployment
 */
async function testWorkerDeployment() {
    console.log('🔧 TESTING WORKER DEPLOYMENT\n');
    console.log('━'.repeat(80) + '\n');

    // Test 1: Workers.dev URL
    console.log('📍 Test 1: Workers.dev URL');
    console.log(`   URL: https://${WORKER_DEV_URL}/health`);
    
    const test1 = await testEndpoint(WORKER_DEV_URL, '/health');
    
    if (test1.error) {
        console.log(`   ❌ Failed: ${test1.error}`);
    } else {
        console.log(`   ✅ Status: ${test1.statusCode}`);
        console.log(`   📦 Response: ${test1.body}`);
        console.log(`   🔧 CF-Ray: ${test1.headers['cf-ray'] || 'N/A'}`);
    }
    
    console.log('\n' + '━'.repeat(80) + '\n');

    // Test 2: Custom Domain
    console.log('📍 Test 2: Custom Domain');
    console.log(`   URL: https://${CUSTOM_DOMAIN}/health`);
    
    const test2 = await testEndpoint(CUSTOM_DOMAIN, '/health');
    
    if (test2.error) {
        console.log(`   ❌ Failed: ${test2.error}`);
        console.log('\n   ⚠️  This means the route is NOT configured yet!');
        console.log('   📋 You need to add the route manually in Cloudflare Dashboard');
    } else {
        console.log(`   ✅ Status: ${test2.statusCode}`);
        
        if (test2.statusCode === 200) {
            console.log(`   📦 Response: ${test2.body}`);
            console.log(`   🔧 CF-Ray: ${test2.headers['cf-ray'] || 'N/A'}`);
            console.log('\n   🎉 SUCCESS! Route is configured and working!');
        } else if (test2.statusCode === 404) {
            console.log(`   ⚠️  404 Error - Route is NOT configured`);
            console.log('   📋 The Worker exists but is not connected to the domain');
        } else if (test2.statusCode === 1101) {
            console.log(`   ⚠️  Error 1101 - Worker is connected but throwing errors`);
        } else {
            console.log(`   📦 Response: ${test2.body}`);
        }
    }
    
    console.log('\n' + '━'.repeat(80) + '\n');

    // Test 3: Backend connectivity (from local machine)
    console.log('📍 Test 3: Backend Server (Direct)');
    console.log(`   URL: http://34.143.73.2`);
    
    // Note: Can't test HTTP from HTTPS node script easily, skip this
    console.log('   ⏭️  Skipped (requires HTTP client)');
    
    console.log('\n' + '━'.repeat(80) + '\n');

    // Summary
    console.log('📊 SUMMARY:\n');
    
    if (test1.statusCode === 200 && test2.statusCode === 200) {
        console.log('✅ Worker is deployed and route is configured correctly!');
        console.log('🎉 Your Chrome extension should work now!\n');
    } else if (test1.statusCode === 200 && test2.statusCode !== 200) {
        console.log('⚠️  Worker is deployed but route is NOT configured');
        console.log('📋 Manual action required:\n');
        console.log('1. Go to: https://dash.cloudflare.com/d31a1c9ec65f373f4008216c30b071cc/workers-and-pages');
        console.log('2. Click on "mustcare-worker"');
        console.log('3. Go to "Settings" → "Triggers"');
        console.log('4. Click "Add Route"');
        console.log('5. Enter: mustcare.valorsynergysuite.com/*');
        console.log('6. Select zone: valorsynergysuite.com');
        console.log('7. Click "Add Route"\n');
    } else {
        console.log('❌ Worker deployment issue detected');
        console.log('🔧 Check Cloudflare Dashboard for more details\n');
    }
}

// Run
testWorkerDeployment().catch(error => {
    console.error('❌ Fatal error:', error);
    process.exit(1);
});

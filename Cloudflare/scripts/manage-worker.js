/**
 * Worker Management Tool
 * Restart, view, and manage Cloudflare Workers
 */

const https = require('https');
const readline = require('readline');
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const API_TOKEN = process.env.CLOUDFLARE_AI_AGENT_TOKEN || process.env.CLOUDFLARE_API_TOKEN;
const ACCOUNT_ID = 'd31a1c9ec65f373f4008216c30b071cc';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function ask(question) {
    return new Promise((resolve) => {
        rl.question(question, resolve);
    });
}

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
                    resolve({ success: response.success, result: response.result, errors: response.errors, status: res.statusCode });
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

async function getWorkerScript(scriptName) {
    console.log(`\n🔍 Fetching Worker script: ${scriptName}...`);
    
    try {
        const response = await makeRequest(`/client/v4/accounts/${ACCOUNT_ID}/workers/scripts/${scriptName}`);
        return response;
    } catch (error) {
        console.error('❌ Error:', error.message);
        return null;
    }
}

async function getTailLogs(scriptName) {
    console.log(`\n📊 Recent logs for: ${scriptName}...`);
    console.log('(Note: You may need to enable logging in dashboard first)\n');
    
    try {
        // Try to get tail logs
        const response = await makeRequest(`/client/v4/accounts/${ACCOUNT_ID}/workers/scripts/${scriptName}/tails`);
        return response;
    } catch (error) {
        console.log('⚠️  Could not fetch logs via API. Check Cloudflare Dashboard → Workers → Logs');
        return null;
    }
}

async function deleteWorker(scriptName) {
    console.log(`\n🗑️  Deleting Worker: ${scriptName}...`);
    
    const confirm = await ask('⚠️  Are you sure? This cannot be undone. (yes/no): ');
    
    if (confirm.toLowerCase() !== 'yes') {
        console.log('❌ Cancelled');
        return false;
    }
    
    try {
        const response = await makeRequest(
            `/client/v4/accounts/${ACCOUNT_ID}/workers/scripts/${scriptName}`,
            'DELETE'
        );
        
        if (response.success) {
            console.log('✅ Worker deleted successfully!');
            console.log('💡 Traffic will now go directly to your origin server (34.143.73.2)');
            return true;
        } else {
            console.error('❌ Failed to delete:', response.errors);
            return false;
        }
    } catch (error) {
        console.error('❌ Error:', error.message);
        return false;
    }
}

async function workerManagement() {
    console.log('\n╔══════════════════════════════════════════════════════════════╗');
    console.log('║         Cloudflare Worker Management Tool                    ║');
    console.log('╚══════════════════════════════════════════════════════════════╝\n');

    // Get workers
    console.log('📋 Fetching Workers...\n');
    const workersResponse = await makeRequest(`/client/v4/accounts/${ACCOUNT_ID}/workers/scripts`);
    
    if (!workersResponse.success || workersResponse.result.length === 0) {
        console.log('⚠️  No Workers found.');
        rl.close();
        return;
    }

    const workers = workersResponse.result;
    console.log(`✅ Found ${workers.length} Worker(s):\n`);
    
    workers.forEach((worker, index) => {
        console.log(`${index + 1}. ${worker.id}`);
        console.log(`   Created: ${new Date(worker.created_on).toLocaleString()}`);
        console.log(`   Modified: ${new Date(worker.modified_on).toLocaleString()}\n`);
    });

    console.log('━'.repeat(80));
    console.log('\n🔧 AVAILABLE ACTIONS:\n');
    console.log('1. View Worker Code');
    console.log('2. Check Logs (if available)');
    console.log('3. Delete Worker (Quick Fix - stops errors immediately)');
    console.log('4. Get Dashboard Link');
    console.log('5. Exit\n');

    const choice = await ask('Select an option (1-5): ');

    switch (choice) {
        case '1':
            const scriptName1 = await ask('\nEnter Worker name (or press Enter for mustcare-worker): ');
            const name1 = scriptName1.trim() || 'mustcare-worker';
            const script = await getWorkerScript(name1);
            if (script) {
                console.log('\n📄 Worker Script:\n');
                console.log(script.result || 'Could not fetch script content');
            }
            break;

        case '2':
            const scriptName2 = await ask('\nEnter Worker name (or press Enter for mustcare-worker): ');
            const name2 = scriptName2.trim() || 'mustcare-worker';
            await getTailLogs(name2);
            break;

        case '3':
            const scriptName3 = await ask('\nEnter Worker name (or press Enter for mustcare-worker): ');
            const name3 = scriptName3.trim() || 'mustcare-worker';
            await deleteWorker(name3);
            break;

        case '4':
            console.log('\n🌐 Dashboard Links:\n');
            console.log('Workers Overview:');
            console.log(`https://dash.cloudflare.com/${ACCOUNT_ID}/workers-and-pages\n`);
            console.log('mustcare-worker Direct:');
            console.log(`https://dash.cloudflare.com/${ACCOUNT_ID}/workers/services/view/mustcare-worker\n`);
            break;

        case '5':
            console.log('\n👋 Goodbye!\n');
            break;

        default:
            console.log('\n❌ Invalid option');
    }

    rl.close();
}

// Run
workerManagement().catch(error => {
    console.error('\n❌ Fatal error:', error.message);
    rl.close();
    process.exit(1);
});

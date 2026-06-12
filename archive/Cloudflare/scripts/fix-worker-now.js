/**
 * Quick Fix - Delete broken Worker
 */

const https = require('https');
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const API_TOKEN = process.env.CLOUDFLARE_AI_AGENT_TOKEN || process.env.CLOUDFLARE_API_TOKEN;
const ACCOUNT_ID = 'd31a1c9ec65f373f4008216c30b071cc';

async function deleteWorker(scriptName) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'api.cloudflare.com',
            port: 443,
            path: `/client/v4/accounts/${ACCOUNT_ID}/workers/scripts/${scriptName}`,
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${API_TOKEN}`,
                'Content-Type': 'application/json'
            }
        };

        console.log(`🗑️  Deleting Worker: ${scriptName}...`);

        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => { body += chunk; });
            res.on('end', () => {
                try {
                    const response = JSON.parse(body);
                    resolve({ success: response.success, errors: response.errors, status: res.statusCode });
                } catch (error) {
                    reject(error);
                }
            });
        });

        req.on('error', reject);
        req.end();
    });
}

async function fixWorkerError() {
    console.log('\n🔧 FIXING CLOUDFLARE WORKER ERROR\n');
    console.log('━'.repeat(80));
    console.log('\n⚡ Quick Fix: Deleting broken "mustcare-worker"...\n');

    try {
        const result = await deleteWorker('mustcare-worker');

        if (result.success) {
            console.log('━'.repeat(80));
            console.log(' SUCCESS! Worker Deleted');
            console.log('━'.repeat(80));
            console.log('\n The broken Worker has been removed!');
            console.log(' mustcare.valorsynergysuite.com should work now!');
            console.log('\n💡 What happened:');
            console.log('   • Removed the crashing Worker code');
            console.log('   • Traffic now goes directly to your server (34.143.73.2)');
            console.log('   • Error 1101 should be resolved\n');
            console.log('🧪 Test your site now: https://mustcare.valorsynergysuite.com\n');
        } else {
            console.log('━'.repeat(80));
            console.log(' FAILED TO DELETE');
            console.log('━'.repeat(80));
            console.log('\nError:', result.errors);
            console.log('\n💡 Alternative: Delete manually:');
            console.log(`   1. Go to: https://dash.cloudflare.com/${ACCOUNT_ID}/workers-and-pages`);
            console.log('   2. Find "mustcare-worker"');
            console.log('   3. Click Delete\n');
        }
    } catch (error) {
        console.error(' Error:', error.message);
        console.log('\n💡 Manual fix:');
        console.log(`   Go to: https://dash.cloudflare.com/${ACCOUNT_ID}/workers-and-pages`);
        console.log('   Delete "mustcare-worker"\n');
    }
}

fixWorkerError();

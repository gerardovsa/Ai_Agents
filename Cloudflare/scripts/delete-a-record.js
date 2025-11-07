/**
 * Delete DNS A Record
 * Removes the A record so Worker can handle all traffic
 */

const https = require('https');

const ZONE_ID = 'd575f903247d1653725514134aedc208';
const RECORD_ID = 'd120e258d494d29fcdf047f4d22b0052'; // From previous script
const API_TOKEN = process.env.CLOUDFLARE_AI_AGENT_TOKEN || process.env.CLOUDFLARE_API_TOKEN;

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

async function deleteARecord() {
    console.log('🗑️  DELETING DNS A RECORD\n');
    console.log('━'.repeat(80) + '\n');

    console.log('⚠️  This will delete the A record for mustcare.valorsynergysuite.com');
    console.log('   The Worker will then handle ALL traffic to the domain\n');

    try {
        const result = await makeRequest('DELETE', `/zones/${ZONE_ID}/dns_records/${RECORD_ID}`);

        console.log('DNS A record deleted successfully!');
        console.log(`   Record ID: ${result.id}\n`);
        console.log('━'.repeat(80) + '\n');
        console.log('🎉 NOW the Worker will handle all requests!');
        console.log('🔧 Test it: https://mustcare.valorsynergysuite.com/health');
        console.log('⏱️  Wait 30-60 seconds for DNS propagation\n');

    } catch (error) {
        console.error(' Failed:', error.message);
        console.log('\n📋 Manual Steps:');
        console.log('1. Go to: https://dash.cloudflare.com/d31a1c9ec65f373f4008216c30b071cc/valorsynergysuite.com/dns');
        console.log('2. Find the A record for "mustcare.valorsynergysuite.com → 34.143.73.2"');
        console.log('3. Click the Delete button (trash icon)');
        console.log('4. Confirm deletion');
        console.log('5. Test: https://mustcare.valorsynergysuite.com/health\n');
    }
}

deleteARecord().catch(error => {
    console.error(' Fatal error:', error);
    process.exit(1);
});

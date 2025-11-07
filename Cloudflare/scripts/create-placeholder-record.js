/**
 * Create Placeholder A Record for Worker
 * Creates a proxied A record so the Worker route can handle traffic
 */

const https = require('https');

const ZONE_ID = 'd575f903247d1653725514134aedc208';
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

async function createPlaceholderRecord() {
    console.log('🔧 CREATING PLACEHOLDER A RECORD FOR WORKER\n');
    console.log('━'.repeat(80) + '\n');

    const recordData = {
        type: 'A',
        name: 'mustcare',
        content: '192.0.2.1',  // RFC 5737 documentation placeholder IP
        ttl: 1,  // Auto (Cloudflare proxy)
        proxied: true,  // Orange cloud - required for Worker routes
        comment: 'Placeholder for Worker route'
    };

    try {
        const result = await makeRequest('POST', `/zones/${ZONE_ID}/dns_records`, recordData);

        console.log('Placeholder A record created successfully!');
        console.log(`   ${result.name} → ${result.content}`);
        console.log(`   Proxied: ${result.proxied ? '🟠 YES (ORANGE CLOUD)' : '⚪ NO'}`);
        console.log(`   Record ID: ${result.id}\n`);
        console.log('━'.repeat(80) + '\n');
        console.log('🎉 Worker route will now handle all traffic!');
        console.log('🔧 Test it: https://mustcare.valorsynergysuite.com/');
        console.log('⏱️  Wait 10-30 seconds for DNS propagation\n');

    } catch (error) {
        console.error(' Failed:', error.message);

        if (error.message.includes('already exists')) {
            console.log('\n record already exists - this is fine!');
            console.log('   The Worker route should be handling traffic\n');
        } else {
            console.log('\n📋 Manual Steps:');
            console.log('1. Go to: https://dash.cloudflare.com/d31a1c9ec65f373f4008216c30b071cc/valorsynergysuite.com/dns');
            console.log('2. Click "Add record"');
            console.log('3. Type: A');
            console.log('4. Name: mustcare');
            console.log('5. IPv4 address: 192.0.2.1');
            console.log('6. Proxy status: Proxied (Orange cloud)');
            console.log('7. Click "Save"\n');
        }
    }
}

createPlaceholderRecord().catch(error => {
    console.error(' Fatal error:', error);
    process.exit(1);
});

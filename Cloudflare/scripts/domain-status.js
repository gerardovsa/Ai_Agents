/**
 * Quick domain status check
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

async function quickStatus() {
    console.log('\n🌐 CLOUDFLARE DOMAIN STATUS\n');
    console.log('━'.repeat(80));

    try {
        // Get zones
        const zones = await makeRequest(`/client/v4/zones?account.id=${ACCOUNT_ID}`);

        for (const zone of zones) {
            console.log(`\n📍 ${zone.name.toUpperCase()}`);
            console.log(`   Status: ${zone.status === 'active' ? ' Active' : '⚠️ ' + zone.status}`);
            console.log(`   Plan: ${zone.plan.name}`);
            console.log(`   Paused: ${zone.paused ? ' Yes' : ' No'}`);

            // Name servers
            console.log(`\n   📡 Name Servers:`);
            zone.name_servers.forEach(ns => console.log(`       ${ns}`));

            if (zone.original_name_servers?.length > 0) {
                console.log(`\n   📡 Original Name Servers (GoDaddy):`);
                zone.original_name_servers.forEach(ns => console.log(`      • ${ns}`));
            }

            // Get DNS records
            try {
                const dns = await makeRequest(`/client/v4/zones/${zone.id}/dns_records`);
                console.log(`\n   📝 DNS Records (${dns.length}):`);

                const byType = {};
                dns.forEach(record => {
                    if (!byType[record.type]) byType[record.type] = [];
                    byType[record.type].push(record);
                });

                Object.keys(byType).sort().forEach(type => {
                    console.log(`\n      ${type} Records:`);
                    byType[type].forEach(record => {
                        const proxied = record.proxied ? '🟠 Proxied' : '⚪ DNS Only';
                        console.log(`         ${record.name}`);
                        console.log(`            → ${record.content} ${proxied}`);
                    });
                });
            } catch (error) {
                console.log(`    Could not fetch DNS records: ${error.message}`);
            }
        }

        console.log('\n' + '━'.repeat(80));
        console.log('\n Domain status check complete!\n');

    } catch (error) {
        console.error('\n Error:', error.message, '\n');
        process.exit(1);
    }
}

quickStatus();

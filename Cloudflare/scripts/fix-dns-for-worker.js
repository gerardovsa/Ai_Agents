/**
 * Fix DNS Record for Worker
 * Changes mustcare.valorsynergysuite.com A record to DNS-only or removes it
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

async function fixDNSRecord() {
    console.log('🔧 FIXING DNS RECORD FOR WORKER\n');
    console.log('━'.repeat(80) + '\n');

    // Step 1: Get current DNS records
    console.log('📋 Step 1: Finding mustcare.valorsynergysuite.com A record...');
    
    try {
        const records = await makeRequest('GET', `/zones/${ZONE_ID}/dns_records?type=A&name=mustcare.valorsynergysuite.com`);
        
        if (records.length === 0) {
            console.log('✅ No A record found - Worker should work correctly!');
            console.log('\n🎉 DNS is configured correctly for Worker-only mode');
            return;
        }
        
        const record = records[0];
        console.log(`✅ Found A record: ${record.name} → ${record.content}`);
        console.log(`   Proxied: ${record.proxied ? '🟠 YES (ORANGE CLOUD)' : '⚪ NO (GRAY CLOUD)'}`);
        console.log(`   Record ID: ${record.id}\n`);
        
        if (record.proxied) {
            console.log('⚠️  PROBLEM IDENTIFIED:');
            console.log('   The A record is Proxied (Orange Cloud) which conflicts with the Worker');
            console.log('   This causes Error 1003 because Cloudflare tries to reach the IP directly\n');
            
            console.log('━'.repeat(80) + '\n');
            console.log('📋 Step 2: Updating DNS record to DNS-only (Gray Cloud)...\n');
            
            // Update the record to DNS-only
            const updated = await makeRequest('PATCH', `/zones/${ZONE_ID}/dns_records/${record.id}`, {
                proxied: false
            });
            
            console.log('✅ DNS record updated successfully!');
            console.log(`   ${updated.name} → ${updated.content}`);
            console.log(`   Proxied: ${updated.proxied ? '🟠 YES' : '⚪ NO (GRAY CLOUD)'}\n`);
            console.log('━'.repeat(80) + '\n');
            console.log('🎉 SUCCESS! The Worker should now handle all requests');
            console.log('🔧 Test it: https://mustcare.valorsynergysuite.com/health');
            console.log('⏱️  Wait 30 seconds for DNS propagation\n');
            
        } else {
            console.log('✅ A record is already DNS-only (Gray Cloud)');
            console.log('⚠️  But Worker still might not work if the record exists');
            console.log('\n💡 RECOMMENDATION: Delete the A record entirely');
            console.log(`   Run: DELETE /zones/${ZONE_ID}/dns_records/${record.id}`);
            console.log('   This will let the Worker handle everything\n');
        }
        
    } catch (error) {
        console.error('❌ Failed:', error.message);
        console.log('\n📋 Manual Steps:');
        console.log('1. Go to: https://dash.cloudflare.com/d31a1c9ec65f373f4008216c30b071cc/valorsynergysuite.com/dns');
        console.log('2. Find the A record for "mustcare.valorsynergysuite.com"');
        console.log('3. Click the Orange Cloud icon to make it Gray (DNS-only)');
        console.log('4. OR delete the A record entirely');
        console.log('5. Test: https://mustcare.valorsynergysuite.com/health\n');
    }
}

fixDNSRecord().catch(error => {
    console.error('❌ Fatal error:', error);
    process.exit(1);
});

/**
 * Quick Test - Direct Workers AI API Call
 * Tests if the token works with Workers AI endpoints
 */

const https = require('https');

const ACCOUNT_ID = 'd31a1c9ec65f373f4008216c30b071cc';
const API_TOKEN = 'EtoWSdK-wK7l7aUb662b6G1o4hdfbh84GWipdlNv';

// Test with a simple AI model
function testWorkersAI() {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({
            messages: [
                { role: 'user', content: 'Say "Hello, Cloudflare Workers AI is working!" in one sentence.' }
            ],
            max_tokens: 50
        });

        const options = {
            hostname: 'api.cloudflare.com',
            port: 443,
            path: `/client/v4/accounts/${ACCOUNT_ID}/ai/run/@cf/meta/llama-3.1-8b-instruct`,
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${API_TOKEN}`,
                'Content-Type': 'application/json',
                'Content-Length': data.length
            }
        };

        console.log('🔧 Testing Workers AI endpoint...');
        console.log(`   URL: ${options.hostname}${options.path}`);
        console.log(`   Token: ${API_TOKEN.substring(0, 10)}...`);
        console.log('');

        const req = https.request(options, (res) => {
            let body = '';

            res.on('data', (chunk) => {
                body += chunk;
            });

            res.on('end', () => {
                console.log(`📊 Status Code: ${res.statusCode}`);
                console.log(`📊 Response:\n${body}\n`);

                try {
                    const response = JSON.parse(body);

                    if (res.statusCode === 200 && response.success) {
                        console.log(' SUCCESS! Workers AI is working!');
                        console.log(`   AI Response: ${response.result?.response || JSON.stringify(response.result)}`);
                        resolve(response);
                    } else {
                        console.error(' FAILED');
                        console.error(`   Errors: ${JSON.stringify(response.errors, null, 2)}`);
                        reject(new Error('API call failed'));
                    }
                } catch (error) {
                    console.error(' Parse error:', error.message);
                    reject(error);
                }
            });
        });

        req.on('error', (error) => {
            console.error(' Request error:', error.message);
            reject(error);
        });

        req.write(data);
        req.end();
    });
}

// Run test
console.log('━'.repeat(80));
console.log('CLOUDFLARE WORKERS AI - DIRECT API TEST');
console.log('━'.repeat(80));
console.log('');

testWorkersAI()
    .then(() => {
        console.log('\n━'.repeat(80));
        console.log(' Test completed successfully!');
        console.log('━'.repeat(80));
    })
    .catch((error) => {
        console.log('\n━'.repeat(80));
        console.error(' Test failed:', error.message);
        console.log('━'.repeat(80));
        process.exit(1);
    });

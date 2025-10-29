/**
 * Test script for Cloudflare AI Client
 * Run with: node test-client.js
 */

const CloudflareAIClient = require('./cloudflare-ai-client');
const fs = require('fs').promises;
const path = require('path');

// Load API token from .env
async function loadApiToken() {
    try {
        const envPath = path.join(__dirname, '..', '.env');
        const envContent = await fs.readFile(envPath, 'utf8');
        const lines = envContent.split('\n');
        const token = lines.find(line => line.trim() && !line.startsWith('curl') && !line.includes('token') && line.length > 30);
        
        if (token) {
            process.env.CLOUDFLARE_API_TOKEN = token.trim();
            return token.trim();
        }
    } catch (error) {
        console.error('❌ Failed to load API token:', error.message);
        process.exit(1);
    }
}

async function runTests() {
    console.log('🧪 Starting Cloudflare AI Client Tests...\n');

    await loadApiToken();
    const client = new CloudflareAIClient();

    // Test 1: Verify Token
    console.log('━'.repeat(80));
    console.log('TEST 1: Token Verification');
    console.log('━'.repeat(80));
    try {
        const tokenInfo = await client.verifyToken();
        console.log('✅ Token is valid');
        console.log(`   Status: ${tokenInfo.status}`);
        console.log(`   Expires: ${new Date(tokenInfo.expires_on).toLocaleString()}\n`);
    } catch (error) {
        console.error('❌ Token verification failed:', error.message);
        process.exit(1);
    }

    // Test 2: List Models
    console.log('━'.repeat(80));
    console.log('TEST 2: List Available Models');
    console.log('━'.repeat(80));
    try {
        const models = await client.listModels();
        console.log(`✅ Found ${models.length} models`);
        console.log(`   First 5 models:`);
        models.slice(0, 5).forEach((model, i) => {
            console.log(`   ${i + 1}. ${model.name} (${model.task?.name || 'N/A'})`);
        });
        console.log('');
    } catch (error) {
        console.error('❌ Failed to list models:', error.message);
    }

    // Test 3: Text Generation
    console.log('━'.repeat(80));
    console.log('TEST 3: Text Generation');
    console.log('━'.repeat(80));
    try {
        const response = await client.generateText('Explain what Cloudflare Workers are in one sentence.', {
            maxTokens: 100
        });
        console.log('✅ Text generation successful');
        console.log(`   Response: ${response}\n`);
    } catch (error) {
        console.error('❌ Text generation failed:', error.message);
    }

    // Test 4: Error Diagnosis
    console.log('━'.repeat(80));
    console.log('TEST 4: Error Diagnosis');
    console.log('━'.repeat(80));
    try {
        const diagnosis = await client.diagnoseError('1101', 'Worker threw JavaScript exception');
        console.log('✅ Error diagnosis successful');
        console.log(`   Diagnosis preview: ${diagnosis.diagnosis.substring(0, 200)}...\n`);
    } catch (error) {
        console.error('❌ Error diagnosis failed:', error.message);
    }

    // Test 5: Embeddings
    console.log('━'.repeat(80));
    console.log('TEST 5: Generate Embeddings');
    console.log('━'.repeat(80));
    try {
        const embeddings = await client.generateEmbeddings('Cloudflare Workers AI');
        console.log('✅ Embeddings generated');
        console.log(`   Embedding dimensions: ${embeddings.data?.[0]?.values?.length || 'N/A'}\n`);
    } catch (error) {
        console.error('❌ Embedding generation failed:', error.message);
    }

    console.log('━'.repeat(80));
    console.log('🎉 All tests completed!');
    console.log('━'.repeat(80));
}

// Run tests
runTests().catch(error => {
    console.error('\n❌ Test suite failed:', error.message);
    process.exit(1);
});

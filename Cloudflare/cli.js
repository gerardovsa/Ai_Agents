#!/usr/bin/env node

/**
 * Cloudflare AI CLI Tool
 * 
 * Command-line interface for managing Cloudflare services,
 * debugging issues, and performing AI-powered tasks
 */

const CloudflareAIClient = require('./cloudflare-ai-client');
const CloudflareManager = require('./cloudflare-manager');
const fs = require('fs').promises;
const path = require('path');

// Load environment variables
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

// Parse API token from .env file
async function loadApiToken() {
    // dotenv should have already loaded it
    if (process.env.CLOUDFLARE_API_TOKEN) {
        return process.env.CLOUDFLARE_API_TOKEN;
    }

    console.error(' CLOUDFLARE_API_TOKEN not found in .env file');
    process.exit(1);
}

// CLI Commands
const commands = {
    async verify() {
        console.log('\n🔐 Verifying Cloudflare API Token...\n');

        await loadApiToken();
        const client = new CloudflareAIClient();

        try {
            const result = await client.verifyToken();
            console.log('\nToken Verification Successful!\n');
            console.log('📊 Token Details:');
            console.log(`   Status: ${result.status}`);
            console.log(`   Account ID: ${result.accountId}`);
            console.log(`   Workers AI: Accessible`);
            console.log(`   Test Response: "${result.message}"`);
            console.log('\n');
        } catch (error) {
            console.error('\n Verification Failed:', error.message, '\n');
            process.exit(1);
        }
    },

    async models() {
        console.log('\n🤖 Fetching Available AI Models...\n');

        await loadApiToken();
        const client = new CloudflareAIClient();

        try {
            const models = await client.listModels();
            console.log(`\n📊 Found ${models.length} models:\n`);

            // Group by task type
            const grouped = models.reduce((acc, model) => {
                const task = model.task?.name || 'other';
                if (!acc[task]) acc[task] = [];
                acc[task].push(model);
                return acc;
            }, {});

            Object.keys(grouped).sort().forEach(task => {
                console.log(`\n${task.toUpperCase()}:`);
                grouped[task].forEach(model => {
                    console.log(`  • ${model.name}`);
                    if (model.description) {
                        console.log(`    ${model.description}`);
                    }
                });
            });

            console.log('\n');
        } catch (error) {
            console.error('\n Failed to fetch models:', error.message, '\n');
            process.exit(1);
        }
    },

    async chat(message) {
        if (!message) {
            console.error(' Please provide a message: node cli.js chat "your message"');
            process.exit(1);
        }

        console.log('\n💬 Chatting with Cloudflare AI...\n');
        console.log(`You: ${message}\n`);

        await loadApiToken();
        const client = new CloudflareAIClient();

        try {
            const response = await client.generateText(message, {
                systemPrompt: 'You are a helpful AI assistant specializing in Cloudflare services, web development, and technical problem-solving.'
            });

            console.log(`AI: ${response}\n`);
        } catch (error) {
            console.error('\n Chat failed:', error.message, '\n');
            process.exit(1);
        }
    },

    async diagnose(errorCode, errorMessage) {
        if (!errorCode) {
            console.error(' Usage: node cli.js diagnose <error_code> <error_message>');
            process.exit(1);
        }

        console.log(`\n🔍 Diagnosing Cloudflare Error ${errorCode}...\n`);

        await loadApiToken();
        const client = new CloudflareAIClient();

        try {
            const result = await client.diagnoseError(errorCode, errorMessage || 'No message provided');

            console.log('━'.repeat(80));
            console.log(`📊 ERROR DIAGNOSIS REPORT`);
            console.log('━'.repeat(80));
            console.log(`\nError Code: ${result.errorCode}`);
            console.log(`Error Message: ${result.errorMessage}`);
            console.log(`Timestamp: ${result.timestamp}\n`);
            console.log('━'.repeat(80));
            console.log('ANALYSIS:');
            console.log('━'.repeat(80));
            console.log(`\n${result.diagnosis}\n`);
            console.log('━'.repeat(80));

            // Save report
            const reportPath = path.join(__dirname, 'logs', `error-${errorCode}-${Date.now()}.json`);
            await fs.mkdir(path.join(__dirname, 'logs'), { recursive: true });
            await fs.writeFile(reportPath, JSON.stringify(result, null, 2));
            console.log(`\n💾 Report saved to: ${reportPath}\n`);
        } catch (error) {
            console.error('\n Diagnosis failed:', error.message, '\n');
            process.exit(1);
        }
    },

    async analyze(filePath) {
        if (!filePath) {
            console.error(' Usage: node cli.js analyze <file_path>');
            process.exit(1);
        }

        console.log(`\n📊 Analyzing file: ${filePath}...\n`);

        await loadApiToken();
        const client = new CloudflareAIClient();

        try {
            const content = await fs.readFile(filePath, 'utf8');
            const fileExt = path.extname(filePath);

            let prompt = `Analyze this ${fileExt} file and provide:
1. Summary of what it does
2. Potential issues or improvements
3. Security considerations
4. Performance suggestions

File content:
\`\`\`
${content.substring(0, 8000)} ${content.length > 8000 ? '...(truncated)' : ''}
\`\`\``;

            const analysis = await client.generateText(prompt, {
                systemPrompt: 'You are an expert code reviewer and security analyst.',
                maxTokens: 2000
            });

            console.log('━'.repeat(80));
            console.log('FILE ANALYSIS REPORT');
            console.log('━'.repeat(80));
            console.log(`\n${analysis}\n`);
            console.log('━'.repeat(80) + '\n');
        } catch (error) {
            console.error('\n Analysis failed:', error.message, '\n');
            process.exit(1);
        }
    },

    async logs(count = 10) {
        console.log(`\n📋 Recent Error Logs (last ${count})...\n`);

        try {
            const logsDir = path.join(__dirname, 'logs');
            const files = await fs.readdir(logsDir);
            const errorLogs = files.filter(f => f.startsWith('error-')).sort().reverse().slice(0, count);

            if (errorLogs.length === 0) {
                console.log('📭 No error logs found.\n');
                return;
            }

            for (const logFile of errorLogs) {
                const logPath = path.join(logsDir, logFile);
                const log = JSON.parse(await fs.readFile(logPath, 'utf8'));

                console.log('━'.repeat(80));
                console.log(`Error ${log.errorCode} - ${new Date(log.timestamp).toLocaleString()}`);
                console.log(`Message: ${log.errorMessage}`);
                console.log('━'.repeat(80) + '\n');
            }
        } catch (error) {
            console.error('\n Failed to read logs:', error.message, '\n');
        }
    },

    async domains() {
        console.log('\n🌐 Fetching Cloudflare Domains & Configuration...\n');

        await loadApiToken();
        const manager = new CloudflareManager();

        try {
            const overview = await manager.getDomainOverview();

            // Display account info
            console.log('━'.repeat(80));
            console.log('📊 ACCOUNT INFORMATION');
            console.log('━'.repeat(80));
            console.log(`Name: ${overview.account.name}`);
            console.log(`ID: ${overview.account.id}`);
            console.log(`Type: ${overview.account.type || 'Standard'}`);
            console.log('');

            // Display zones/domains
            if (overview.zones.length === 0) {
                console.log('📭 No domains found in this account.\n');
                return;
            }

            console.log('━'.repeat(80));
            console.log(`🌐 DOMAINS (${overview.zones.length})`);
            console.log('━'.repeat(80));

            for (const zone of overview.zones) {
                if (zone.error) {
                    console.log(`\n ${zone.name} - Error: ${zone.error}`);
                    continue;
                }

                console.log(`\n📍 ${zone.name.toUpperCase()}`);
                console.log(`   ID: ${zone.id}`);
                console.log(`   Status: ${zone.health?.status || zone.status}`);
                console.log(`   Plan: ${zone.health?.plan || zone.plan?.name || 'Unknown'}`);
                console.log(`   Paused: ${zone.health?.paused ? 'Yes' : 'No'}`);

                // Name servers
                if (zone.health?.nameServers?.length > 0) {
                    console.log(`   Name Servers:`);
                    zone.health.nameServers.forEach(ns => console.log(`      • ${ns}`));
                }

                // Security settings
                console.log(`   SSL: ${zone.health?.ssl || 'unknown'}`);
                console.log(`   Security Level: ${zone.health?.securityLevel || 'unknown'}`);
                console.log(`   Always Online: ${zone.health?.alwaysOnline || 'unknown'}`);

                // DNS records
                if (zone.dns && zone.dns.length > 0) {
                    console.log(`\n   📝 DNS Records (${zone.dns.length}):`);
                    const recordsByType = {};
                    zone.dns.forEach(record => {
                        if (!recordsByType[record.type]) recordsByType[record.type] = [];
                        recordsByType[record.type].push(record);
                    });

                    Object.keys(recordsByType).sort().forEach(type => {
                        console.log(`      ${type}: ${recordsByType[type].length} record(s)`);
                        recordsByType[type].slice(0, 3).forEach(record => {
                            console.log(`         ${record.name} → ${record.content}`);
                        });
                        if (recordsByType[type].length > 3) {
                            console.log(`         ... and ${recordsByType[type].length - 3} more`);
                        }
                    });
                }

                // Analytics
                if (zone.analytics) {
                    console.log(`\n   📊 Analytics (Last 7 days):`);
                    console.log(`      Requests: ${zone.analytics.totals?.requests?.all || 'N/A'}`);
                    console.log(`      Bandwidth: ${zone.analytics.totals?.bandwidth?.all || 'N/A'} bytes`);
                    console.log(`      Threats: ${zone.analytics.totals?.threats?.all || 'N/A'}`);
                }

                console.log('');
            }

            // Display alerts
            if (overview.alerts.length > 0) {
                console.log('━'.repeat(80));
                console.log(`🔔 ALERTS & NOTIFICATIONS (${overview.alerts.length})`);
                console.log('━'.repeat(80));
                overview.alerts.forEach(alert => {
                    console.log(`\n📌 ${alert.name}`);
                    console.log(`   Type: ${alert.alert_type}`);
                    console.log(`   Enabled: ${alert.enabled ? 'Yes' : 'No'}`);
                    if (alert.description) {
                        console.log(`   Description: ${alert.description}`);
                    }
                });
                console.log('');
            } else {
                console.log('━'.repeat(80));
                console.log('🔔 ALERTS & NOTIFICATIONS');
                console.log('━'.repeat(80));
                console.log('No alerts configured.\n');
            }

            // Save to file
            const reportPath = path.join(__dirname, 'logs', `domain-overview-${Date.now()}.json`);
            await fs.mkdir(path.join(__dirname, 'logs'), { recursive: true });
            await fs.writeFile(reportPath, JSON.stringify(overview, null, 2));
            console.log(`💾 Full report saved to: ${reportPath}\n`);

        } catch (error) {
            console.error('\n Failed to fetch domains:', error.message, '\n');
            process.exit(1);
        }
    },

    async alerts() {
        console.log('\n🔔 Fetching Cloudflare Alerts...\n');

        await loadApiToken();
        const manager = new CloudflareManager();

        try {
            const alerts = await manager.getAlerts();

            if (alerts.length === 0) {
                console.log('📭 No alerts configured.\n');
                return;
            }

            console.log('━'.repeat(80));
            console.log(`CONFIGURED ALERTS (${alerts.length})`);
            console.log('━'.repeat(80));

            alerts.forEach((alert, index) => {
                console.log(`\n${index + 1}. ${alert.name}`);
                console.log(`   ID: ${alert.id}`);
                console.log(`   Type: ${alert.alert_type}`);
                console.log(`   Enabled: ${alert.enabled ? 'es' : ' No'}`);
                if (alert.description) {
                    console.log(`   Description: ${alert.description}`);
                }
                if (alert.filters) {
                    console.log(`   Filters: ${JSON.stringify(alert.filters)}`);
                }
            });

            console.log('\n');
        } catch (error) {
            console.error('\n Failed to fetch alerts:', error.message, '\n');
            process.exit(1);
        }
    },

    help() {
        console.log(`
╔══════════════════════════════════════════════════════════════════════╗
║           Cloudflare AI CLI - Command Reference                      ║
╚══════════════════════════════════════════════════════════════════════╝

📌 AUTHENTICATION & SETUP:
   node cli.js verify                    Verify API token
   
🌐 ACCOUNT & DOMAIN MANAGEMENT:
   node cli.js domains                   List all domains & configuration
   node cli.js alerts                    View configured alerts
   
🤖 AI MODELS:
   node cli.js models                    List all available AI models
   node cli.js chat "message"            Chat with AI assistant
   
🔍 DIAGNOSTICS & DEBUGGING:
   node cli.js diagnose <code> [msg]     Diagnose Cloudflare error
   node cli.js analyze <file>            Analyze code file with AI
   node cli.js logs [count]              View recent error logs
   
💡 EXAMPLES:
   node cli.js verify
   node cli.js domains
   node cli.js alerts
   node cli.js chat "How do I fix CORS errors?"
   node cli.js diagnose 1101 "Worker threw exception"
   node cli.js analyze ../background.js
   node cli.js logs 5

📚 For more information, visit:
   https://developers.cloudflare.com/workers-ai/

        `);
    }
};

// Main CLI handler
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    const commandArgs = args.slice(1);

    if (!command || command === 'help' || command === '--help' || command === '-h') {
        commands.help();
        return;
    }

    if (commands[command]) {
        try {
            await commands[command](...commandArgs);
        } catch (error) {
            console.error('\n Command failed:', error.message, '\n');
            process.exit(1);
        }
    } else {
        console.error(`\n Unknown command: ${command}\n`);
        console.log('Run "node cli.js help" for available commands.\n');
        process.exit(1);
    }
}

// Run CLI
main().catch(error => {
    console.error('\n Fatal error:', error.message, '\n');
    process.exit(1);
});

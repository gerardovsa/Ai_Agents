import re

file_path = r"c:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the function
old_pattern = r'async restoreThreadAssignments\(\) \{.*?^\s{12}\},'
new_function = '''async restoreThreadAssignments() {
                console.log('[RESTORE] Starting thread restoration using thread.location field...');

                try {
                    // Wait for MultiAgent to be ready
                    if (typeof MultiAgent === 'undefined') {
                        console.warn('[WARN] [RESTORE] MultiAgent not available yet, waiting...');
                        await new Promise(resolve => setTimeout(resolve, 500));
                    }

                    // USE THREAD.LOCATION FIELD - single source of truth from sessions.threads.location
                    // Threads already loaded with location field from /api/threads/list
                    const threadsInAgents = this.threads.filter(t => 
                        t.location && 
                        t.location !== 'prime' && 
                        t.location.startsWith('agent-')
                    );

                    console.log(`[RESTORE] Found ${threadsInAgents.length} threads assigned to agents`);
                    
                    if (threadsInAgents.length === 0) {
                        console.log('[RESTORE] No threads in agent columns to restore');
                        return;
                    }

                    // Log what we're restoring
                    threadsInAgents.forEach(t => {
                        const msgCount = (t.messages && t.messages.length) || 0;
                        console.log(`  [RESTORE] Thread "${t.title}" -> ${t.location} (${msgCount} messages)`);
                    });

                    // Restore each thread to its assigned agent column
                    for (const thread of threadsInAgents) {
                        const location = thread.location;
                        const agentId = parseInt(location.replace('agent-', ''));

                        console.log(`[RESTORE] Restoring thread "${thread.title}" to ${location}...`);

                        try {
                            // Update thread's agent property for consistency
                            thread.agent = location;

                            // Load into MultiAgent with full rendering
                            if (typeof MultiAgent !== 'undefined') {
                                // CRITICAL: Use loadThreadIntoAgent for full rendering with TwoRuleStreamProcessor
                                await MultiAgent.loadThreadIntoAgent(agentId, thread);

                                // Update agent header info card
                                MultiAgent.updateAgentHeader(agentId);

                                console.log(`[OK] [RESTORE] Thread "${thread.title}" restored to ${location}`);
                            }
                        } catch (error) {
                            console.error(`[ERROR] [RESTORE] Failed to restore thread "${thread.title}":`, error);
                        }

                        // Small delay to prevent UI blocking
                        await new Promise(resolve => setTimeout(resolve, 50));
                    }

                    // Refresh thread list to show all agent badges
                    this.renderThreadList();

                    console.log(`[OK] [RESTORE] All ${threadsInAgents.length} thread assignments restored`);

                } catch (error) {
                    console.error('[ERROR] [RESTORE] Error restoring thread assignments:', error);
                }
            },'''

new_content = re.sub(old_pattern, new_function, content, flags=re.DOTALL | re.MULTILINE)

if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('[OK] Function replaced successfully')
else:
    print('[ERROR] No replacement made - pattern not found')

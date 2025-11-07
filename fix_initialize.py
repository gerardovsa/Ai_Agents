#!/usr/bin/env python3
"""
Fix the initializeSubTabs method in stock-management.js
"""

file_path = r"C:\Users\gpoli\GIT\AI_agents\UI\external\modules\stock-management\stock-management.js"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the initializeSubTabs method and replace it
new_method = """    initializeSubTabs() {
        console.log('[INIT] Scheduling Stock Management sub-tabs initialization...');
        console.log('[TIMING] Using double RAF for DOM readiness...');

        // Use DOUBLE requestAnimationFrame to ensure DOM is fully rendered AND painted
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                console.log('[TIMING] DOM ready. Checking containers...');
                const requiredTabs = ['invoice-processing', 'usage-analytics', 'reorder-dashboard', 'profit-analysis', 'sql-viewer', 'ai-analytics'];
                console.log('[CHECK] Verifying sub-tab containers...');
                const containerStatus = requiredTabs.map(tabId => {
                    const container = this.getSubTabContainer(tabId);
                    const found = !!container;
                    console.log(`   [${found ? 'OK' : 'MISSING'}] ${this.moduleId}-subtab-${tabId}`);
                    return { tabId, found, container };
                });
                const missingTabs = containerStatus.filter(s => !s.found).map(s => s.tabId);
                if (missingTabs.length > 0) {
                    console.error('[ERROR] Missing containers:', missingTabs);
                    console.error('[DEBUG] Module ID:', this.moduleId);
                    const allContainers = document.querySelectorAll(`[id^="${this.moduleId}-subtab-"]`);
                    console.error('[DEBUG] Found:', Array.from(allContainers).map(el => el.id));
                    return;
                }
                console.log('[INIT] All containers found. Initializing...');
                this.initializeInvoiceProcessingTab();
                this.initializeUsageAnalyticsTab();
                this.initializeReorderDashboardTab();
                this.initializeProfitAnalysisTab();
                this.initializeSQLViewerTab();
                this.initializeAIAnalyticsTab();
                console.log('[INIT] All sub-tabs initialized successfully');
            });
        });
    }
"""

# Find the method start and end
start_line = None
end_line = None
in_method = False
brace_count = 0

for i, line in enumerate(lines):
    if 'initializeSubTabs()' in line and not in_method:
        start_line = i
        in_method = True
        brace_count = 0
    
    if in_method:
        brace_count += line.count('{') - line.count('}')
        if brace_count == 0 and i > start_line:
            end_line = i
            break

print(f"Found method at lines {start_line+1} to {end_line+1}")

# Replace the method
new_lines = lines[:start_line] + [new_method + '\n'] + lines[end_line+1:]

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Method replaced successfully!")
print(f"Removed {end_line - start_line + 1} lines, added {len(new_method.split(chr(10)))} lines")

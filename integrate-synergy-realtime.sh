#!/bin/bash

# FILE: integrate-synergy-realtime.sh
# PURPOSE: Automated integration of enhanced Synergy realtime
# USAGE: ./integrate-synergy-realtime.sh

set -e

echo "🚀 Starting Synergy Realtime Enhanced Integration..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Find all files referencing old module
echo -e "${YELLOW}Step 1: Finding files referencing synergy-realtime.js...${NC}"
files=$(grep -rl "synergy-realtime\.js" UI/ --include="*.html" --include="*.js" || true)

if [ -z "$files" ]; then
    echo -e "${RED}No files found referencing synergy-realtime.js${NC}"
    echo "Skipping replacement..."
else
    echo "Found files:"
    echo "$files"
    echo ""

    # Step 2: Backup old files
    echo -e "${YELLOW}Step 2: Creating backups...${NC}"
    backup_dir="backups/synergy-realtime-$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    for file in $files; do
        cp "$file" "$backup_dir/"
        echo "  ✓ Backed up: $file"
    done
    echo ""

    # Step 3: Replace references
    echo -e "${YELLOW}Step 3: Replacing module references...${NC}"
    for file in $files; do
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' 's/synergy-realtime\.js/synergy-realtime-enhanced.js/g' "$file"
        else
            # Linux
            sed -i 's/synergy-realtime\.js/synergy-realtime-enhanced.js/g' "$file"
        fi
        echo "  ✓ Updated: $file"
    done
    echo ""
fi

# Step 4: Update initialization code
echo -e "${YELLOW}Step 4: Checking initialization patterns...${NC}"
init_files=$(grep -rl "synergyRealtime\.connect\|new SynergyRealtime" UI/ --include="*.js" || true)

if [ -z "$init_files" ]; then
    echo "No initialization code found"
else
    echo "Found initialization in:"
    echo "$init_files"
    echo ""
    echo -e "${YELLOW}⚠️  Manual update required:${NC}"
    echo "Replace:"
    echo "  window.synergyRealtime = new SynergyRealtime();"
    echo "  window.synergyRealtime.connect();"
    echo ""
    echo "With:"
    echo "  const userId = window.userSession?.user_id || null;"
    echo "  window.SynergyRealtimeEnhanced.connect(userId);"
    echo ""
fi

# Step 5: Check for server-side WebSocket code
echo -e "${YELLOW}Step 5: Checking server-side WebSocket code...${NC}"
ws_files=$(find AI_infrastructure -name "*synergy*" -o -name "*websocket*" -o -name "*socketio*" | grep -E "\.(py|js)$" || true)

if [ -z "$ws_files" ]; then
    echo "No server-side WebSocket files found"
else
    echo "Found server files:"
    echo "$ws_files"
    echo ""
    echo -e "${YELLOW}⚠️  Server-side update needed:${NC}"
    echo "Add metadata change event emission:"
    echo ""
    echo "  socketio.emit('session_metadata_changed', {"
    echo "      'session_id': session_id,"
    echo "      'field': 'tags',"
    echo "      'old_value': old_value,"
    echo "      'new_value': new_value,"
    echo "      'session': session_dict"
    echo "  }, namespace='/ws/synergy', room='synergy_board')"
    echo ""
fi

# Step 6: Validate files exist
echo -e "${YELLOW}Step 6: Validating enhanced module...${NC}"
if [ -f "UI/shared/js/synergy-realtime-enhanced.js" ]; then
    echo -e "${GREEN}✓ Enhanced module exists${NC}"
    lines=$(wc -l < "UI/shared/js/synergy-realtime-enhanced.js")
    echo "  Lines: $lines"
else
    echo -e "${RED}✗ Enhanced module NOT found!${NC}"
    exit 1
fi

# Step 7: Create test file
echo ""
echo -e "${YELLOW}Step 7: Creating test file...${NC}"
cat > "test-synergy-realtime-enhanced.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Synergy Realtime Enhanced Test</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="/shared/js/synergy-realtime-enhanced.js"></script>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .status { padding: 10px; border-radius: 4px; margin: 10px 0; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #d1ecf1; color: #0c5460; }
        button { padding: 8px 16px; margin: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>🧪 Synergy Realtime Enhanced Test</h1>
    
    <div id="status" class="status info">Not connected</div>
    
    <h2>Connection</h2>
    <button onclick="testConnect()">Connect</button>
    <button onclick="testDisconnect()">Disconnect</button>
    <button onclick="testStatus()">Check Status</button>
    
    <h2>View Detection</h2>
    <div data-tab="synergy" style="display: inline-block; padding: 10px; border: 1px solid #ccc; margin: 10px;">
        <label>
            <input type="checkbox" id="synergyActive" onchange="toggleSynergyView()"> Synergy Tab Active
        </label>
    </div>
    <button onclick="testViewCheck()">Check if Viewing Synergy</button>
    
    <h2>Simulated Events</h2>
    <button onclick="simulateSessionCreated()">Simulate Session Created</button>
    <button onclick="simulateSessionUpdated()">Simulate Session Updated</button>
    <button onclick="simulateMetadataChanged()">Simulate Metadata Changed</button>
    
    <h2>Output</h2>
    <pre id="output" style="background: #f4f4f4; padding: 15px; border-radius: 4px; max-height: 400px; overflow-y: auto;"></pre>
    
    <script>
        window.API_BASE_URL = 'http://localhost:5001';
        const TEST_USER_ID = 123;
        
        function log(message, type = 'info') {
            const output = document.getElementById('output');
            const timestamp = new Date().toLocaleTimeString();
            output.textContent += `[${timestamp}] ${message}\n`;
            output.scrollTop = output.scrollHeight;
            
            if (type === 'error') {
                console.error(message);
            } else {
                console.log(message);
            }
        }
        
        function updateStatus(message, type = 'info') {
            const statusEl = document.getElementById('status');
            statusEl.textContent = message;
            statusEl.className = `status ${type}`;
        }
        
        function testConnect() {
            log('Testing connection...');
            window.SynergyRealtimeEnhanced.connect(TEST_USER_ID);
            updateStatus('Connecting...', 'info');
        }
        
        function testDisconnect() {
            log('Testing disconnection...');
            window.SynergyRealtimeEnhanced.disconnect();
            updateStatus('Disconnected', 'error');
        }
        
        function testStatus() {
            const connected = window.SynergyRealtimeEnhanced.isConnected();
            log(`Connection status: ${connected}`);
            updateStatus(connected ? 'Connected' : 'Disconnected', connected ? 'success' : 'error');
        }
        
        function toggleSynergyView() {
            const checkbox = document.getElementById('synergyActive');
            const tab = document.querySelector('[data-tab="synergy"]');
            if (checkbox.checked) {
                tab.classList.add('active');
                log('✓ Synergy tab activated');
            } else {
                tab.classList.remove('active');
                log('✗ Synergy tab deactivated');
            }
        }
        
        function testViewCheck() {
            const viewing = window.SynergyRealtimeEnhanced.isUserViewingSynergy();
            log(`Is viewing Synergy: ${viewing}`, viewing ? 'success' : 'info');
        }
        
        function simulateSessionCreated() {
            log('Simulating session_created event...');
            window.SynergyRealtimeEnhanced._handleSessionCreated({
                session_id: 999,
                session: {
                    id: 999,
                    title: 'Test Session',
                    owner_user_id: TEST_USER_ID,
                    status: 'active',
                    color_hex: '#3b82f6'
                }
            });
        }
        
        function simulateSessionUpdated() {
            log('Simulating session_updated event...');
            window.SynergyRealtimeEnhanced._handleSessionUpdated({
                session_id: 999,
                updates: {
                    title: 'Updated Test Session',
                    priority: 'high',
                    tags: ['urgent', 'test']
                },
                session: {
                    id: 999,
                    title: 'Updated Test Session',
                    owner_user_id: TEST_USER_ID
                }
            });
        }
        
        function simulateMetadataChanged() {
            log('Simulating session_metadata_changed event...');
            window.SynergyRealtimeEnhanced._handleMetadataChanged({
                session_id: 999,
                field: 'tags',
                old_value: ['test'],
                new_value: ['test', 'vip'],
                session: {
                    id: 999,
                    title: 'Test Session',
                    owner_user_id: TEST_USER_ID
                }
            });
        }
        
        // Log module loaded
        log('✓ Synergy Realtime Enhanced module loaded');
        updateStatus('Module loaded - Ready to test', 'success');
    </script>
</body>
</html>
EOF

echo -e "${GREEN}✓ Test file created: test-synergy-realtime-enhanced.html${NC}"
echo ""

# Step 8: Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✨ Integration Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Review changes in backups/ directory"
echo "2. Update initialization code (see manual updates above)"
echo "3. Add server-side event emission (see examples above)"
echo "4. Test using: test-synergy-realtime-enhanced.html"
echo "5. Commit changes"
echo ""
echo "Documentation:"
echo "  - SYNERGY_REALTIME_ENHANCEMENTS_DEC9.md"
echo ""
echo -e "${GREEN}Ready to deploy!${NC} 🚀"

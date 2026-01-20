"""
Verify Communication Hub Immediate UI Fix Implementation
Date: January 21, 2026
"""

import re
from pathlib import Path

def verify_changes():
    """Verify all 5 critical changes are present in communication-hub-v4-modern.js"""
    
    js_file = Path("UI/modules_internal/communication-hub/communication-hub-v4-modern.js")
    
    if not js_file.exists():
        print("❌ ERROR: communication-hub-v4-modern.js not found!")
        return False
    
    content = js_file.read_text(encoding='utf-8')
    
    checks = []
    
    # CHECK 1: Store as object (not string) in assignEmailToAgentWithTask
    check1 = "this.state.emailThreads[emailId] = {" in content and \
             "slug: threadSlug," in content and \
             "location: location," in content and \
             "agentName: agentName," in content and \
             "synced: false" in content
    checks.append(("Store full metadata object", check1))
    
    # CHECK 2: Formatter checks local cache first
    check2 = "const threadInfo = this.state.emailThreads?.[emailId];" in content and \
             "typeof threadInfo === 'string'" in content and \
             "agentName = threadInfo.agentName;" in content
    checks.append(("Formatter uses local cache", check2))
    
    # CHECK 3: Sync spinner in badge
    check3 = '!synced ? \'<i class="fas fa-sync fa-spin"' in content
    checks.append(("Sync spinner in badge", check3))
    
    # CHECK 4: Background sync marks synced=true
    check4 = "this.state.emailThreads[emailId].synced = true;" in content
    checks.append(("Background sync marks synced", check4))
    
    # CHECK 5: renderAISection uses local cache
    check5_pattern = r'renderAISection\(email\)\s*\{[^}]*const threadInfo = this\.state\.emailThreads\?\.\[email\.id\];'
    check5 = bool(re.search(check5_pattern, content, re.DOTALL))
    checks.append(("renderAISection uses cache", check5))
    
    # CHECK 6: loadThreadAssignments stores full metadata
    check6 = "this.state.emailThreads[emailId] = {" in content and \
             "agentName: agentName," in content and \
             "synced: true  // Already synced from database" in content
    checks.append(("loadThreadAssignments full metadata", check6))
    
    # Print results
    print("\n" + "="*60)
    print("COMMUNICATION HUB IMMEDIATE UI FIX VERIFICATION")
    print("="*60 + "\n")
    
    all_passed = True
    for name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Ready for browser testing!")
        print("="*60 + "\n")
        print("Next Steps:")
        print("1. Open browser: http://127.0.0.1:5001/UI/pages/communication-hub.html")
        print("2. Login as user ID 14 (printing@inhouseprint.com.au)")
        print("3. Select an unassigned email")
        print("4. Click AI Agent column → Select agent (e.g., Lima) → Select task type")
        print("5. Verify IMMEDIATE agent badge display (< 100ms)")
        print("6. Verify Continue Chat button visible immediately in preview")
        print("7. Verify small sync spinner disappears in 1-2 seconds")
        print("8. Refresh page → Verify agent badge shows immediately on load")
    else:
        print("❌ SOME CHECKS FAILED - Review code changes needed")
        print("="*60)
    
    return all_passed

if __name__ == "__main__":
    verify_changes()

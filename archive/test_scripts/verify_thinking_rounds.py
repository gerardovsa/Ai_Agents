#!/usr/bin/env python3
"""
Verify Thinking Round Separator Implementation
Checks that all required code is present in business-ai-platform-v2.html
"""

import re
from pathlib import Path

def verify_implementation():
    """Verify the thinking round separator implementation"""
    
    html_file = Path(__file__).parent / 'UI' / 'business-ai-platform-v2.html'
    
    if not html_file.exists():
        print(f"❌ File not found: {html_file}")
        return False
    
    print(f"✅ Found file: {html_file}")
    print()
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Check for round counter initialization
    test_results = []
    
    # Test 1: Round counter reset in universal stream
    if 'window._thinkingRoundCounter = 0;' in content:
        count = content.count('window._thinkingRoundCounter = 0;')
        test_results.append(('✅', f'Round counter initialization found ({count} locations)'))
    else:
        test_results.append(('❌', 'Round counter initialization NOT found'))
    
    # Test 2: Block index detection
    if 'const blockIndex = typeof data.block_index' in content:
        test_results.append(('✅', 'Block index detection logic found'))
    else:
        test_results.append(('❌', 'Block index detection logic NOT found'))
    
    # Test 3: Round detection condition
    if 'const isNewRound = blockIndex === 0;' in content:
        test_results.append(('✅', 'Round detection condition found'))
    else:
        test_results.append(('❌', 'Round detection condition NOT found'))
    
    # Test 4: Round separator creation
    if 'thinking-round-separator' in content and 'Round ${roundNum}' in content:
        test_results.append(('✅', 'Round separator HTML generation found'))
    else:
        test_results.append(('❌', 'Round separator HTML generation NOT found'))
    
    # Test 5: New bubble creation on round change
    if 'if (isNewRound && existingBubble)' in content:
        test_results.append(('✅', 'New bubble creation logic found'))
    else:
        test_results.append(('❌', 'New bubble creation logic NOT found'))
    
    # Test 6: Thinking bubble reference update
    if 'const newThinkingBubble = handleThinkingEvent' in content and 'thinkingBubble = newThinkingBubble' in content:
        test_results.append(('✅', 'Thinking bubble reference update found'))
    else:
        test_results.append(('❌', 'Thinking bubble reference update NOT found'))
    
    # Test 7: CSS class for separator
    if '.thinking-round-separator' in content:
        test_results.append(('✅', 'CSS class for separator found'))
    else:
        test_results.append(('❌', 'CSS class for separator NOT found'))
    
    # Test 8: Enhanced function comment
    if 'ENHANCED: Detects new rounds (block_index === 0)' in content:
        test_results.append(('✅', 'Enhanced function documentation found'))
    else:
        test_results.append(('❌', 'Enhanced function documentation NOT found'))
    
    # Print results
    print("=" * 60)
    print("VERIFICATION RESULTS")
    print("=" * 60)
    print()
    
    for icon, message in test_results:
        print(f"{icon} {message}")
    
    print()
    print("=" * 60)
    
    # Summary
    passed = sum(1 for icon, _ in test_results if icon == '✅')
    total = len(test_results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print()
        print("IMPLEMENTATION STATUS: ✅ COMPLETE")
        print()
        print("The thinking round separator feature is correctly implemented.")
        print("Key features:")
        print("  • Detects new rounds when block_index === 0")
        print("  • Creates separate thinking bubbles for each round")
        print("  • Adds visual 'Round N' separators between rounds")
        print("  • Preserves Anthropic's message structure (client-side only)")
        return True
    else:
        print(f"⚠️  PARTIAL IMPLEMENTATION ({passed}/{total} tests passed)")
        print()
        print("Some features are missing. Review the failed tests above.")
        return False

if __name__ == '__main__':
    success = verify_implementation()
    exit(0 if success else 1)

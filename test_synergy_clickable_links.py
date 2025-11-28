"""
Test Synergy Clickable Links - Validation Script

This script validates that the AI agent receives proper instructions
about creating clickable documents and links in Synergy.
"""

from tools.implementations.synergy_instructions import synergy_agent_instructions

print("=" * 80)
print("SYNERGY CLICKABLE LINKS VALIDATION")
print("=" * 80)

# Test 1: Check quickstart instructions mention clickability
print("\n1. Checking QUICKSTART instructions...")
result = synergy_agent_instructions('quickstart')
guide = result['guide']

checks = {
    'CLICKABLE mentioned': 'CLICKABLE' in guide,
    'FULL URL requirement': 'FULL URL' in guide,
    'URL REQUIREMENTS section': 'URL REQUIREMENTS' in guide,
    'type field requirement': '"type"' in guide and 'Required' in guide,
    'Opens in new tab': 'new tab' in guide.lower() or 'new browser' in guide.lower(),
    'Internal doc exception': 'internal_doc' in guide and 'modal' in guide.lower()
}

for check, passed in checks.items():
    status = "PASS" if passed else "FAIL"
    print(f"   [{status}] {check}")

all_passed = all(checks.values())
print(f"\n   Result: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")

# Test 2: Check troubleshooting includes clickable links issue
print("\n2. Checking TROUBLESHOOTING instructions...")
result = synergy_agent_instructions('troubleshooting')
guide = result['guide']

checks = {
    'Not clickable issue': 'Not Clickable' in guide or 'not clickable' in guide,
    'URL format examples': 'https://docs.google.com/' in guide,
    'Document types listed': 'google_sheet' in guide and 'google_doc' in guide,
    'Wrong format shown': 'WRONG' in guide or 'Wrong' in guide,
    'Correct format shown': 'CORRECT' in guide or 'Correct' in guide
}

for check, passed in checks.items():
    status = "PASS" if passed else "FAIL"
    print(f"   [{status}] {check}")

all_passed = all(checks.values())
print(f"\n   Result: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")

# Test 3: Extract key guidance for AI agents
print("\n3. Key guidance for AI agents:")
print("-" * 80)

guidance = [
    "Use synergy_add_document() to add clickable documents",
    "Provide FULL URL from creation response (https://docs.google.com/...)",
    "Include document type (google_sheet, google_doc, etc.) for proper icon",
    "Use descriptive titles (not 'Document 1')",
    "Documents open in NEW TAB when clicked",
    "Exception: internal_doc/internal_sheet open in modal popup",
    "Use synergy_add_link() for external resources (dashboards, APIs)",
    "Links are fully clickable and open in new tabs"
]

for i, item in enumerate(guidance, 1):
    print(f"   {i}. {item}")

print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)

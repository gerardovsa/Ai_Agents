"""
Smoke test: Verify backend can retrieve AI settings
"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from routes.user_preferences_routes import get_user_preferences

print("=" * 80)
print("BACKEND SMOKE TEST")
print("=" * 80)

prefs = get_user_preferences(14)

if prefs:
    print("\n✅ Backend GET Test:")
    print(f"  User ID: {prefs['user_id']}")
    print(f"  Nickname: {prefs['nickname']}")
    print(f"  AI Model: {prefs['ai_model']}")
    print(f"  Temperature: {prefs['ai_temperature']}")
    print(f"  Max Tokens: {prefs['ai_max_tokens']}")
    print(f"  Thinking: {'Enabled' if prefs['ai_thinking_enabled'] else 'Disabled'}")
    print(f"  Budget: {prefs['ai_thinking_budget']}")
    print("\n✅ Backend route can retrieve AI settings!")
else:
    print("\n❌ Failed to retrieve preferences")
    exit(1)

print("=" * 80)

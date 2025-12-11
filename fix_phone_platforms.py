import json

# Read the phone system tools JSON
with open('c:/Users/gpoli/GIT/AI_agents/tools/schemas/phone_system_tools.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# Add platform field to each tool that doesn't have one
count = 0
for tool in data['tools']:
    if 'platform' not in tool or tool['platform'] == '':
        tool['platform'] = 'phone_system'
        count += 1

# Write back
with open('c:/Users/gpoli/GIT/AI_agents/tools/schemas/phone_system_tools.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f'✅ Added platform="phone_system" to {count} phone tools')

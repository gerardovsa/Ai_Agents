import codecs

file_path = r'c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\prompts\tool_usage_system_prompt.md'

with codecs.open(file_path, 'r', 'utf-8') as f:
    content = f.read()

# Replace emojis and special characters with ASCII
replacements = {
    '→': '->',
    '↓': 'v',
    '┌': '+',
    '┐': '+',
    '└': '+',
    '┘': '+',
    '─': '-',
    '│': '|',
    '├': '|',
    '┴': '+',
    '━': '=',
    '═': '=',
    '✅': '[OK]',
    '❌': '[X]',
    '⛔': '[STOP]',
    '⚠️': '[!]',
    '🔥': '[CRITICAL]',
    '📌': '[PIN]',
    '🔗': '[LINK]',
    '🏷️': '[TAG]',
    '👥': '[USERS]',
    '📧': '[EMAIL]',
    '🖨️': '[PRINT]',
    '🗄️': '[DB]',
    '📊': '[CHART]',
    '🎨': '[ART]',
    '🚨': '[ALERT]',
    '🔍': '[SEARCH]',
    '≠': '!=',
    '°C': 'C',
    '°F': 'F',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with codecs.open(file_path, 'w', 'utf-8') as f:
    f.write(content)

print('[OK] Removed all emojis and fixed encoding!')

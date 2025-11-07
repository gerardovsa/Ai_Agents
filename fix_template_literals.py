"""
Fix template literal spacing and emojis in business-ai-platform-v2.html
Removes spaces around ${variable} in template strings
Removes emojis from console.log statements (causes Unicode errors)
"""
import re

file_path = r'c:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html'

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix spaces in template literals: ${ var } -> ${var}
# Pattern matches ${ followed by spaces, word characters, optional spaces, and }
content = re.sub(r'\$\{\s+(\w+)\s+\}', r'${\1}', content)

# Also fix spaces in ID selectors: #agent - ${ agentId } -> #agent-${agentId}
content = re.sub(r'#agent\s+-\s+\$\{\s*(\w+)\s*\}', r'#agent-${\1}', content)
content = re.sub(r'agent\s+-\s+\$\{\s*(\w+)\s*\}', r'agent-${\1}', content)
content = re.sub(r'messages\s+-\s+\$\{\s*(\w+)\s*\}', r'messages-${\1}', content)
content = re.sub(r'input\s+-\s+\$\{\s*(\w+)\s*\}', r'input-${\1}', content)
content = re.sub(r'send\s+-\s+\$\{\s*(\w+)\s*\}', r'send-${\1}', content)
content = re.sub(r'status\s+-\s+\$\{\s*(\w+)\s*\}', r'status-${\1}', content)
content = re.sub(r'attach\s+-\s+\$\{\s*(\w+)\s*\}', r'attach-${\1}', content)
content = re.sub(r'file\s+-\s+input\s+-\s+\$\{\s*(\w+)\s*\}', r'file-input-${\1}', content)
content = re.sub(r'width\s+-\s+icon\s+-\s+\$\{\s*(\w+)\s*\}', r'width-icon-${\1}', content)
content = re.sub(r'collapsed\s+-\s+status\s+-\s+\$\{\s*(\w+)\s*\}', r'collapsed-status-${\1}', content)
content = re.sub(r'collapsed\s+-\s+timestamp\s+-\s+\$\{\s*(\w+)\s*\}', r'collapsed-timestamp-${\1}', content)
content = re.sub(r'menu\s+-\s+\$\{\s*(\w+)\s*\}', r'menu-${\1}', content)
content = re.sub(r'multi\s+-\s+agent\s+-\s+\$\{\s*(\w+)\s*\}', r'multi-agent-${\1}', content)

# Fix CSS class selectors: .agent - messages -> .agent-messages
content = re.sub(r'\.agent\s+-\s+messages', r'.agent-messages', content)
content = re.sub(r'\.agent\s+-\s+messages\s+-\s+container', r'.agent-messages-container', content)

# Fix complex template literals with expressions: ${ expr } -> ${expr}
# Pattern for any content between ${ and } including spaces
content = re.sub(r'\$\{\s+([^}]+?)\s+\}', r'${\1}', content)

# REMOVE EMOJIS from console.log statements (causes Unicode errors)
# Common emoji patterns in the file
emoji_map = {
    '📥': '[LOAD]',
    '❌': '[ERROR]',
    '✅': '[OK]',
    '📐': '[LAYOUT]',
    '📏': '[SIZE]',
    '🔍': '[SEARCH]',
    '✨': '[NEW]',
    '🆕': '[NEW]',
    '📂': '[DATA]',
    '📎': '[ATTACH]',
    '🧹': '[CLEAN]',
    '📊': '[CHART]',
    '⚠️': '[WARN]',
    '🔒': '[LOCK]',
}

for emoji, replacement in emoji_map.items():
    content = content.replace(emoji, replacement)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed business-ai-platform-v2.html:")
print("- Removed spaces: ${ var } -> ${var}")
print("- Fixed ID selectors: #agent - ${id} -> #agent-${id}")
print("- Fixed class selectors: .agent - messages -> .agent-messages")
print(f"- Removed {len(emoji_map)} emoji types and replaced with text markers")

"""Find all script tags and their line numbers to identify the mismatch."""
import re

html_file = r"UI\business-ai-platform-v2.html"

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Find all script tags with their positions
script_opens = []
script_closes = []

for i, line in enumerate(lines, 1):
    # Find all <script tags on this line
    for match in re.finditer(r'<script(?:\s|>)', line):
        script_opens.append((i, match.start(), line.strip()[:80]))
    
    # Find all </script> tags on this line
    for match in re.finditer(r'</script>', line):
        script_closes.append((i, match.start(), line.strip()[:80]))

print(f"Found {len(script_opens)} opening <script> tags")
print(f"Found {len(script_closes)} closing </script> tags")
print(f"Difference: {len(script_opens) - len(script_closes)}")

# Try to match them up
print("\n🔍 Analyzing script blocks...")
print("\nLast 10 script openings:")
for line_num, pos, text in script_opens[-10:]:
    print(f"  Line {line_num:5d}: {text}")

print("\nLast 10 script closings:")
for line_num, pos, text in script_closes[-10:]:
    print(f"  Line {line_num:5d}: {text}")

# Check if the last opening has a matching close
last_open = script_opens[-1][0]
last_close = script_closes[-1][0]

print(f"\n📊 Last opening <script>: Line {last_open}")
print(f"📊 Last closing </script>: Line {last_close}")

if last_close < last_open:
    print(f"\n❌ PROBLEM: Last script opened at line {last_open} but last close is at line {last_close}")
    print(f"   This script block is UNCLOSED!")
    
    # Show context
    print(f"\n🔍 Context around line {last_open}:")
    for i in range(max(0, last_open - 3), min(len(lines), last_open + 5)):
        marker = ">>>" if i == last_open - 1 else "   "
        print(f"{marker} {i+1:5d}: {lines[i][:100]}")

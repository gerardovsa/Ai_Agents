"""Find the exact location of the unclosed script tag."""

html_file = r"UI\business-ai-platform-v2.html"

with open(html_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

script_stack = []
depth = 0
line_num = 0

for i, line in enumerate(lines, 1):
    # Count opening script tags on this line
    opens = line.count('<script')
    closes = line.count('</script>')
    
    for _ in range(opens):
        script_stack.append(i)
        depth += 1
    
    for _ in range(closes):
        if script_stack:
            script_stack.pop()
        depth -= 1
    
    # If depth ever goes negative, we have too many closers
    if depth < 0:
        print(f"❌ Line {i}: EXTRA closing </script> tag")
        print(f"   Content: {line.strip()[:100]}")
        break

# After processing all lines, check if any scripts are still open
if script_stack:
    print(f"\n❌ UNCLOSED SCRIPT TAGS FOUND: {len(script_stack)}")
    print(f"\nOpened at these lines:")
    for line_num in script_stack[-5:]:  # Show last 5
        print(f"  Line {line_num}: {lines[line_num-1].strip()[:80]}")
    
    print(f"\n🔍 Checking context around line {script_stack[-1]}...")
    start = max(0, script_stack[-1] - 3)
    end = min(len(lines), script_stack[-1] + 10)
    
    for i in range(start, end):
        marker = ">>>" if i == script_stack[-1] - 1 else "   "
        print(f"{marker} {i+1:5d}: {lines[i].rstrip()[:100]}")
else:
    print("✅ All script tags properly closed")

print(f"\n📊 Summary:")
print(f"   Total <script> tags: {sum(1 for line in lines for _ in range(line.count('<script')))}")
print(f"   Total </script> tags: {sum(1 for line in lines for _ in range(line.count('</script>')))}") 

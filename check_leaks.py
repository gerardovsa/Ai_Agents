"""Check for database connection leaks in thread_routes.py"""
import re

# Read the file
with open('AI_infrastructure/routes/thread_routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("Checking for connection leaks in thread_routes.py...")
print("-" * 60)

# Find all fetchall() calls
fetchall_lines = []
for i, line in enumerate(content.split('\n'), 1):
    if 'fetchall()' in line:
        fetchall_lines.append((i, line.strip()))

print(f"\nFound {len(fetchall_lines)} fetchall() calls:")
for line_num, line in fetchall_lines:
    print(f"  Line {line_num}: {line}")

# Now check each one to see if processing happens inside with block
print("\n" + "=" * 60)
print("Analyzing each fetchall() for proper context manager usage...")
print("=" * 60)

lines = content.split('\n')
leak_count = 0

for line_num, _ in fetchall_lines:
    # Find the with block that contains this fetchall
    with_start = None
    indent_level = None
    
    # Search backwards to find the with statement
    for i in range(line_num - 1, max(0, line_num - 50), -1):
        line = lines[i - 1]
        if 'with get_database_connection' in line:
            with_start = i
            indent_level = len(line) - len(line.lstrip())
            break
    
    if with_start:
        # Find where the with block ends (next line with same or less indentation)
        with_end = None
        for i in range(line_num, min(len(lines), line_num + 100)):
            line = lines[i]
            if line.strip() and not line.strip().startswith('#'):
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level:
                    with_end = i + 1
                    break
        
        if with_end:
            # Check if data processing happens after with block
            processing_after = False
            for i in range(line_num, min(len(lines), line_num + 20)):
                line = lines[i]
                if i >= with_end and ('for row in' in line or 'results[0]' in line or 'rows[0]' in line):
                    processing_after = True
                    break
            
            if processing_after:
                leak_count += 1
                print(f"\n[LEAK DETECTED] Line {line_num}")
                print(f"  with block: lines {with_start}-{with_end}")
                print(f"  fetchall(): line {line_num}")
                print(f"  Processing happens AFTER line {with_end} (outside with block)")
            else:
                print(f"\n[OK] Line {line_num} - Processing inside with block")

print("\n" + "=" * 60)
print(f"SUMMARY: {leak_count} connection leaks detected")
print("=" * 60)

if leak_count == 0:
    print("✅ All connection leaks fixed! All data processing happens inside with blocks.")
else:
    print(f"❌ {leak_count} connection leaks still present. Data processing outside with blocks.")

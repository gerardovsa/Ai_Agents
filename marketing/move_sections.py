#!/usr/bin/env python3
"""Move V4 section before V3 section in the HTML file"""

# Read the file
with open('VETERINARY_WEBSITE_PHASE1_BUSINESS_V3.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find V4 section start
v4_start_marker = '    <!-- Real-Time Data Flow & Analysis V4 (USER Only - No VetAI) -->'
v4_start = content.find(v4_start_marker)

# Find V4 section end (the closing script tag before GUIDE section)
v4_end_marker = '    <!-- ========================================'
v4_end = content.find(v4_end_marker, v4_start)

# Extract V4 section
v4_section = content[v4_start:v4_end]

# Find V3 section start
v3_start_marker = '    <!-- Real-Time Data Flow & Analysis -->'
v3_start = content.find(v3_start_marker)

# Build new content: everything before V3 + V4 section + V3 to end (without V4)
before_v3 = content[:v3_start]
v3_to_v4 = content[v3_start:v4_start]
after_v4 = content[v4_end:]

new_content = before_v3 + v4_section + '\n' + v3_to_v4 + after_v4

# Write back
with open('VETERINARY_WEBSITE_PHASE1_BUSINESS_V3.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✓ V4 section moved successfully")
print(f"  V4 was at position {v4_start}, now at position {v3_start}")
print(f"  V4 section length: {v4_end - v4_start} characters")

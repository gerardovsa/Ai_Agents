"""
Update workflow spacing from 130px to 200px
Changes Y coordinates: 100→100, 230→300, 360→500, 490→700, 620→900, 750→1100, 880→1300, 1010→1500, 1140→1700
"""

import re

# Read the file
with open('create_sample_workflows.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Mapping of old Y coordinates to new (130px → 200px spacing)
y_mapping = {
    230: 300,   # 100 + 200
    360: 500,   # 100 + 200*2
    490: 700,   # 100 + 200*3
    620: 900,   # 100 + 200*4
    750: 1100,  # 100 + 200*5
    880: 1300,  # 100 + 200*6
    1010: 1500, # 100 + 200*7
    1140: 1700  # 100 + 200*8
}

# Replace each Y coordinate
for old_y, new_y in y_mapping.items():
    # Pattern: "y": 230 (with surrounding context)
    pattern = f'"y": {old_y},'
    replacement = f'"y": {new_y},'
    content = content.replace(pattern, replacement)
    print(f'Replaced "y": {old_y} → "y": {new_y}')

# Write back
with open('create_sample_workflows.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('\nSpacing update complete! New spacing: 200px between shapes')
print('Coordinates: 100, 300, 500, 700, 900, 1100, 1300, 1500, 1700...')

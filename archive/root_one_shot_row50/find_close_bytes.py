import os

routes_dir = r'c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes'
fname = 'communication_routes.py'
fpath = os.path.join(routes_dir, fname)

with open(fpath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Searching {fname} for 'close' anywhere:\n")
for i, line in enumerate(lines, 1):
    if 'close' in line.lower():
        print(f"Line {i}: {line.rstrip()}")
        # Show hex bytes of the word "close"
        if 'cursor' in line.lower() and 'close' in line.lower():
            print(f"  → HEX: {line.encode('utf-8').hex()}")

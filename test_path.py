from pathlib import Path

p = Path('c:/Users/gpoli/GIT/AI_agents/UI/modules_external/quote-calculator/implementations/calculator_wrapper.py')
print('calculator_wrapper.py location:')
print(p)
print()
print('Parent directories:')
for i, parent in enumerate(p.parents[:6]):
    print(f'  Level {i}: {parent.name} -> {parent}')

print()
print('Path to AI_agents root (parent.parent.parent.parent):')
project_root = p.parent.parent.parent.parent
print(f'  {project_root}')
print(f'  Exists: {project_root.exists()}')
print(f'  Name: {project_root.name}')

print()
print('Path to AI_infrastructure/auth:')
auth_path = project_root / 'AI_infrastructure' / 'auth'
print(f'  {auth_path}')
print(f'  Exists: {auth_path.exists()}')

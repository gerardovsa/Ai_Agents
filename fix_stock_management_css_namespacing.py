"""
Fix Stock Management CSS Namespacing
Add 'sm-' prefix to all Stock Management CSS classes to prevent conflicts

This script:
1. Updates stock-management.css with namespaced classes
2. Updates stock-management.js to use namespaced classes
3. Preserves platform-wide classes like 'btn', 'dashboard-card', etc.
"""

import re
import os

# Classes that should NOT be namespaced (platform-wide classes)
PLATFORM_CLASSES = {
    'btn', 'btn-primary', 'btn-secondary', 'btn-success', 'btn-danger',
    'dashboard-card', 'card-header', 'card-title', 'card-actions',
    'tab-content', 'form-control', 'form-group', 'modal', 'modal-content'
}

# Mapping of old class names to new namespaced names
class_mapping = {}

def should_namespace(class_name):
    """Check if a class should be namespaced"""
    # Don't namespace platform-wide classes
    if class_name in PLATFORM_CLASSES:
        return False
    # Don't namespace if already namespaced
    if class_name.startswith('sm-'):
        return False
    return True

def extract_css_classes(css_content):
    """Extract all class names from CSS file"""
    # Match class selectors: .classname
    pattern = r'\.([a-zA-Z][a-zA-Z0-9_-]*)'
    matches = re.findall(pattern, css_content)
    return list(set(matches))

def namespace_css_file(css_path):
    """Add sm- prefix to all CSS classes"""
    print(f"Processing CSS file: {css_path}")
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all classes
    classes = extract_css_classes(content)
    print(f"Found {len(classes)} unique classes")
    
    # Create mapping for classes that should be namespaced
    for class_name in classes:
        if should_namespace(class_name):
            class_mapping[class_name] = f'sm-{class_name}'
    
    print(f"Will namespace {len(class_mapping)} classes")
    
    # Replace class selectors in CSS
    # Sort by length (longest first) to avoid partial replacements
    sorted_classes = sorted(class_mapping.items(), key=lambda x: len(x[0]), reverse=True)
    
    for old_class, new_class in sorted_classes:
        # Match .old-class followed by space, comma, colon, or brace
        pattern = r'\.' + re.escape(old_class) + r'(?=[\s,:{])'
        content = re.sub(pattern, f'.{new_class}', content)
    
    # Write updated CSS
    backup_path = css_path + '.backup'
    os.rename(css_path, backup_path)
    
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ CSS file updated. Backup saved to {backup_path}")
    return len(class_mapping)

def namespace_js_file(js_path):
    """Update JavaScript to use namespaced classes"""
    print(f"\nProcessing JS file: {js_path}")
    
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Sort by length (longest first) to avoid partial replacements
    sorted_classes = sorted(class_mapping.items(), key=lambda x: len(x[0]), reverse=True)
    
    replacements = 0
    for old_class, new_class in sorted_classes:
        # Match class="old-class" or class="... old-class ..."
        patterns = [
            # class="old-class"
            (r'class="' + re.escape(old_class) + r'"', f'class="{new_class}"'),
            # class="prefix old-class"
            (r'class="([^"]*\s)' + re.escape(old_class) + r'"', rf'class="\1{new_class}"'),
            # class="old-class suffix"
            (r'class="' + re.escape(old_class) + r'(\s[^"]*)"', rf'class="{new_class}\1"'),
            # class="prefix old-class suffix"
            (r'class="([^"]*\s)' + re.escape(old_class) + r'(\s[^"]*)"', rf'class="\1{new_class}\2"'),
            # classList.add('old-class')
            (r"classList\.add\(['\"]" + re.escape(old_class) + r"['\"]\)", f"classList.add('{new_class}')"),
            # classList.remove('old-class')
            (r"classList\.remove\(['\"]" + re.escape(old_class) + r"['\"]\)", f"classList.remove('{new_class}')"),
            # classList.toggle('old-class')
            (r"classList\.toggle\(['\"]" + re.escape(old_class) + r"['\"]\)", f"classList.toggle('{new_class}')"),
            # classList.contains('old-class')
            (r"classList\.contains\(['\"]" + re.escape(old_class) + r"['\"]\)", f"classList.contains('{new_class}')"),
            # querySelector('.old-class')
            (r"querySelector\(['\"]\\." + re.escape(old_class) + r"['\"]\)", f"querySelector('.{new_class}')"),
            # querySelectorAll('.old-class')
            (r"querySelectorAll\(['\"]\\." + re.escape(old_class) + r"['\"]\)", f"querySelectorAll('.{new_class}')"),
            # getElementsByClassName('old-class')
            (r"getElementsByClassName\(['\"]" + re.escape(old_class) + r"['\"]\)", f"getElementsByClassName('{new_class}')"),
        ]
        
        for pattern, replacement in patterns:
            old_content = content
            content = re.sub(pattern, replacement, content)
            if content != old_content:
                replacements += 1
    
    # Write updated JS
    backup_path = js_path + '.backup'
    if os.path.exists(backup_path):
        os.remove(backup_path)
    os.rename(js_path, backup_path)
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ JS file updated with {replacements} class replacements. Backup saved to {backup_path}")
    return replacements

def main():
    base_dir = r'C:\Users\gpoli\GIT\AI_agents\UI\external\modules\stock-management'
    
    css_path = os.path.join(base_dir, 'stock-management.css')
    js_path = os.path.join(base_dir, 'stock-management.js')
    
    print("=" * 70)
    print("STOCK MANAGEMENT CSS NAMESPACING FIX")
    print("=" * 70)
    print()
    print("This will add 'sm-' prefix to all Stock Management classes")
    print("to prevent CSS conflicts with other modules.")
    print()
    
    # Step 1: Namespace CSS
    css_count = namespace_css_file(css_path)
    
    # Step 2: Update JS to use namespaced classes
    js_count = namespace_js_file(js_path)
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✅ Namespaced {css_count} CSS classes")
    print(f"✅ Updated {js_count} JavaScript class references")
    print()
    print("Class Mapping (first 20):")
    for i, (old, new) in enumerate(list(class_mapping.items())[:20]):
        print(f"  {old} → {new}")
    if len(class_mapping) > 20:
        print(f"  ... and {len(class_mapping) - 20} more")
    print()
    print("✅ COMPLETE! Stock Management classes are now namespaced.")
    print()
    print("Next steps:")
    print("1. Bump version in manifest.json (1.1.6 → 1.1.7)")
    print("2. Hard refresh browser (Ctrl+F5)")
    print("3. Test Stock Management module")
    print()

if __name__ == '__main__':
    main()

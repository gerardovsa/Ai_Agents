#!/usr/bin/env python3
"""Check CSS and HTML files for syntax errors"""
from pathlib import Path
import re

errors = []
warnings = []

# Check all CSS files
css_files = list(Path('UI').rglob('*.css'))
print(f"Checking {len(css_files)} CSS files...")

for css_file in css_files:
    try:
        content = css_file.read_text(encoding='utf-8')
        
        # Check for unclosed comments
        open_comments = content.count('/*')
        close_comments = content.count('*/')
        if open_comments != close_comments:
            errors.append(f"{css_file}: Unclosed comment (/* {open_comments}, */ {close_comments})")
        
        # Check for unmatched braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            errors.append(f"{css_file}: Unmatched braces ({{ {open_braces}, }} {close_braces})")
        
        # Check for nested comments (not allowed in CSS)
        if re.search(r'/\*[^*]*?/\*', content):
            warnings.append(f"{css_file}: Possible nested comment")
        
        # Check for invalid comment syntax
        if '/* font-weight:' in content and '*/ */' in content:
            errors.append(f"{css_file}: Double closing comment markers")
            
    except Exception as e:
        errors.append(f"{css_file}: Error reading file - {e}")

# Check main HTML file
html_file = Path('UI/business-ai-platform-v2.html')
if html_file.exists():
    try:
        content = html_file.read_text(encoding='utf-8')
        
        # Check for unclosed style tags
        if content.count('<style') != content.count('</style>'):
            errors.append(f"{html_file}: Unclosed <style> tags")
        
        # Check for unclosed script tags
        if content.count('<script') != content.count('</script>'):
            errors.append(f"{html_file}: Unclosed <script> tags")
            
        # Check for CSS in style tags
        style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
        for i, block in enumerate(style_blocks):
            open_comments = block.count('/*')
            close_comments = block.count('*/')
            if open_comments != close_comments:
                errors.append(f"{html_file}: Style block {i+1} has unclosed comment")
            
            open_braces = block.count('{')
            close_braces = block.count('}')
            if open_braces != close_braces:
                errors.append(f"{html_file}: Style block {i+1} has unmatched braces")
    except Exception as e:
        errors.append(f"{html_file}: Error reading file - {e}")

# Report results
print("\n" + "="*70)
if errors:
    print("ERRORS FOUND:")
    print("="*70)
    for error in errors:
        print(f"  ❌ {error}")
else:
    print("✅ NO ERRORS FOUND")

if warnings:
    print("\n" + "="*70)
    print("WARNINGS:")
    print("="*70)
    for warning in warnings:
        print(f"  ⚠️  {warning}")

print("="*70)
print(f"\nChecked: {len(css_files)} CSS files + 1 HTML file")
print(f"Status: {'FAIL - Fix errors above' if errors else 'PASS'}")
print("="*70)

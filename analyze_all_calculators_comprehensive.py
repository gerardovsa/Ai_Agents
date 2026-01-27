"""
Comprehensive analysis of all calculator JSONs in TXT file vs backend implementations.
Produces detailed report of matches, mismatches, and implementation status.
"""

import os
import re
from pathlib import Path

# File paths
TXT_FILE = Path(r'UI\modules_external\quote-calculator\ARCHIVE_CONSOLIDATED\CALCULATOR_JSONS\SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt')
BACKEND_DIR = Path(r'UI\modules_external\quote-calculator\backend\shopify_calculators')

# Read TXT file
with open(TXT_FILE, 'r', encoding='utf-8') as f:
    txt_content = f.read()
    txt_lines = txt_content.split('\n')

# Find all calculator names in TXT file
# Looking for headings that are followed by formulas or JSON configurations
calculators_in_txt = set()
txt_sections = {}

for i, line in enumerate(txt_lines):
    line_stripped = line.strip()
    
    # Check if this is followed by "Constants or Custom Variables"
    if i < len(txt_lines) - 2:
        next_2_lines = ' '.join(txt_lines[i+1:i+3])
        
        if 'Constants or Custom Variables' in next_2_lines or 'JSON calculator configuration' in next_2_lines:
            # This is a calculator heading
            if (line_stripped and 
                len(line_stripped) < 80 and 
                not line_stripped.startswith('var ') and
                not line_stripped.startswith('{') and
                not line_stripped.startswith('//') and
                'Constants' not in line_stripped and
                'JSON' not in line_stripped and
                '```' not in line_stripped and
                not any(op in line_stripped for op in ['>=', '<=', '==', '?', ':', '&&', '||'])):
                
                # Clean up the name
                clean_name = line_stripped.strip()
                
                # Store it
                calculators_in_txt.add(clean_name)
                
                # Find if it has a formula section
                has_formula = 'var q =' in next_2_lines or 'var subTotal' in next_2_lines or 'var total' in next_2_lines
                has_json = 'JSON calculator configuration' in next_2_lines
                
                txt_sections[clean_name] = {
                    'line': i + 1,
                    'has_formula': has_formula,
                    'has_json': has_json
                }

# List all backend calculator files
backend_files = {}
if BACKEND_DIR.exists():
    for file in BACKEND_DIR.glob('*.py'):
        if file.name not in ['__init__.py', 'config_manager.py', 'test_flexible_quantity.py']:
            backend_files[file.stem] = {
                'file': file.name,
                'path': file,
                'lines': len(file.read_text(encoding='utf-8').split('\n'))
            }

# Create mapping between TXT names and backend files
# Common patterns:
# "Notepads A5" -> "NotepadsA5_Shopify_Calculator.py"
# "Premium Bookmarks" -> "PremiumBookmarks_Shopify_Calculator.py"
# "A-Frames" -> "CorfluteInsertA-Frame_Shopify_Calculator.py" or "CorfluteInsertA_Frame_Shopify_Calculator.py"

def normalize_name(name):
    """Normalize calculator name for comparison"""
    return name.lower().replace(' ', '').replace('-', '').replace('_', '')

def try_match_backend(txt_name):
    """Try to find matching backend file for TXT calculator name"""
    normalized_txt = normalize_name(txt_name)
    
    # Try exact matches with common patterns
    possible_patterns = [
        txt_name.replace(' ', '').replace('-', '') + '_Shopify_Calculator',
        txt_name.replace(' ', '').replace('-', '_') + '_Shopify_Calculator',
        txt_name.replace(' ', '') + '_Shopify_Calculator',
        txt_name.lower().replace(' ', '_') + '_calculator_shopify',
        txt_name.lower().replace(' ', '_') + '_shopify_calculator',
        # Special cases
        txt_name.replace(' ', '').replace('-', 'Bound') if 'Bound' in txt_name else '',
    ]
    
    for pattern in possible_patterns:
        pattern_norm = normalize_name(pattern)
        for backend_key, backend_data in backend_files.items():
            backend_norm = normalize_name(backend_key)
            if pattern_norm == backend_norm:
                return backend_key
    
    # Try partial matches
    for backend_key in backend_files.keys():
        backend_norm = normalize_name(backend_key)
        # Check if significant parts match
        txt_words = set(normalized_txt.split())
        backend_words = set(backend_norm.split())
        
        # Special handling for compound names
        if 'notepads' in normalized_txt and 'notepads' in backend_norm:
            if 'a5' in normalized_txt and 'a5' in backend_norm:
                return backend_key
            if 'a4' in normalized_txt and 'a4' in backend_norm:
                return backend_key
            if 'a6' in normalized_txt and 'a6' in backend_norm:
                return backend_key
        
        if 'businesscard' in normalized_txt and 'businesscard' in backend_norm:
            if 'premium' in normalized_txt and 'premium' in backend_norm:
                return backend_key
            if 'economical' in normalized_txt and 'economical' in backend_norm:
                return backend_key
        
        if 'aframe' in normalized_txt and 'aframe' in backend_norm:
            if 'metal' in normalized_txt and 'metal' in backend_norm:
                return backend_key
            if 'corflute' in normalized_txt or 'corflute' in backend_norm:
                return backend_key
        
        if 'strutcard' in normalized_txt and 'strutcard' in backend_norm:
            if 'a3' in normalized_txt and 'a3' in backend_norm:
                return backend_key
            if 'a4' in normalized_txt and 'a4' in backend_norm:
                return backend_key
    
    return None

# Create mapping
txt_to_backend_mapping = {}
matched_backends = set()

for txt_name in sorted(calculators_in_txt):
    backend_match = try_match_backend(txt_name)
    if backend_match:
        txt_to_backend_mapping[txt_name] = backend_match
        matched_backends.add(backend_match)

# Find backends without TXT entries
unmatched_backends = set(backend_files.keys()) - matched_backends

# Generate comprehensive report
print("=" * 80)
print("COMPREHENSIVE CALCULATOR ANALYSIS: TXT FILE vs BACKEND IMPLEMENTATIONS")
print("=" * 80)
print()

print(f"📄 TXT File: {TXT_FILE.name}")
print(f"📁 Backend Directory: {BACKEND_DIR.name}")
print()

print("=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)
print(f"Calculators in TXT file:        {len(calculators_in_txt)}")
print(f"Backend implementation files:    {len(backend_files)}")
print(f"Matched (TXT + Backend):         {len(txt_to_backend_mapping)}")
print(f"TXT only (no backend):           {len(calculators_in_txt) - len(txt_to_backend_mapping)}")
print(f"Backend only (no TXT):           {len(unmatched_backends)}")
print()

print("=" * 80)
print("MATCHED CALCULATORS (TXT + BACKEND)")
print("=" * 80)
print()

for i, (txt_name, backend_key) in enumerate(sorted(txt_to_backend_mapping.items()), 1):
    backend_data = backend_files[backend_key]
    txt_data = txt_sections.get(txt_name, {})
    
    status = []
    if txt_data.get('has_formula'):
        status.append("✅ Formula")
    else:
        status.append("❌ No Formula")
    
    if txt_data.get('has_json'):
        status.append("✅ JSON")
    else:
        status.append("❌ No JSON")
    
    status.append(f"{backend_data['lines']} lines")
    
    print(f"{i:2}. {txt_name}")
    print(f"    TXT:     Line {txt_data.get('line', '?'):5} | {' | '.join(status[:2])}")
    print(f"    Backend: {backend_data['file']:50} | {status[2]}")
    print()

print("=" * 80)
print("CALCULATORS IN TXT WITHOUT BACKEND IMPLEMENTATION")
print("=" * 80)
print()

txt_only = sorted(calculators_in_txt - set(txt_to_backend_mapping.keys()))
if txt_only:
    for i, txt_name in enumerate(txt_only, 1):
        txt_data = txt_sections.get(txt_name, {})
        status = []
        if txt_data.get('has_formula'):
            status.append("✅ Formula")
        else:
            status.append("❌ No Formula")
        if txt_data.get('has_json'):
            status.append("✅ JSON")
        else:
            status.append("❌ No JSON")
        
        print(f"{i:2}. {txt_name} (Line {txt_data.get('line', '?')})")
        print(f"    Status: {' | '.join(status)}")
        print()
else:
    print("✅ All TXT calculators have backend implementations!")
    print()

print("=" * 80)
print("BACKEND IMPLEMENTATIONS WITHOUT TXT DOCUMENTATION")
print("=" * 80)
print()

if unmatched_backends:
    for i, backend_key in enumerate(sorted(unmatched_backends), 1):
        backend_data = backend_files[backend_key]
        print(f"{i:2}. {backend_data['file']}")
        print(f"    Lines: {backend_data['lines']:4} | Path: {backend_data['path'].name}")
        print()
else:
    print("✅ All backend implementations are documented in TXT file!")
    print()

print("=" * 80)
print("DETAILED TXT CALCULATOR LIST")
print("=" * 80)
print()

for i, calc_name in enumerate(sorted(calculators_in_txt), 1):
    txt_data = txt_sections.get(calc_name, {})
    backend_match = txt_to_backend_mapping.get(calc_name, "NO BACKEND")
    
    formula_status = "✅" if txt_data.get('has_formula') else "❌"
    json_status = "✅" if txt_data.get('has_json') else "❌"
    backend_status = "✅" if backend_match != "NO BACKEND" else "❌"
    
    print(f"{i:2}. {calc_name}")
    print(f"    Line: {txt_data.get('line', '?'):5} | Formula: {formula_status} | JSON: {json_status} | Backend: {backend_status}")
    if backend_match != "NO BACKEND":
        print(f"    Backend: {backend_files[backend_match]['file']}")
    print()

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)

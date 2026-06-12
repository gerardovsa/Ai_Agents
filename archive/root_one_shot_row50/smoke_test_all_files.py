#!/usr/bin/env python3
"""
Comprehensive Smoke Test for HTML, CSS, and JavaScript Files
Checks for syntax errors, unclosed tags, and common issues
December 4, 2025
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict
import json

class SmokeTest:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {'html': 0, 'css': 0, 'js': 0}
    
    def test_html_file(self, file_path: Path) -> None:
        """Test HTML file for common issues"""
        print(f"  Testing: {file_path.relative_to(Path.cwd())}")
        self.stats['html'] += 1
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Test 1: Script tag balance
            script_opens = []
            script_closes = []
            
            for i, line in enumerate(lines, 1):
                # Count opening <script> tags (but not self-closing like <script ... />)
                for match in re.finditer(r'<script(?:\s[^>]*)?>(?!</script>)', line):
                    # Make sure it's not immediately closed on same line
                    if '</script>' not in line[match.end():]:
                        script_opens.append(i)
                
                # Count closing </script> tags
                for match in re.finditer(r'</script>', line):
                    script_closes.append(i)
            
            if len(script_opens) != len(script_closes):
                self.errors.append(
                    f"{file_path}: Script tag mismatch ({len(script_opens)} opens, {len(script_closes)} closes)"
                )
                if script_opens:
                    last_open = script_opens[-1]
                    self.errors.append(f"  → Last unclosed <script> at line {last_open}")
            
            # Test 2: Style tag balance
            style_opens = content.count('<style')
            style_closes = content.count('</style>')
            if style_opens != style_closes:
                self.errors.append(
                    f"{file_path}: Style tag mismatch ({style_opens} opens, {style_closes} closes)"
                )
            
            # Test 3: Check for common issues
            if '/* font-weight:' in content and '*/ */' in content:
                self.warnings.append(f"{file_path}: Possible double closing comment markers")
            
            # Test 4: Check CSS in style blocks
            style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
            for idx, block in enumerate(style_blocks):
                if block.count('{') != block.count('}'):
                    self.errors.append(f"{file_path}: Style block {idx+1} has unbalanced braces")
                
                if block.count('/*') != block.count('*/'):
                    self.errors.append(f"{file_path}: Style block {idx+1} has unbalanced comments")
            
            print(f"    ✓ HTML structure OK")
            
        except Exception as e:
            self.errors.append(f"{file_path}: Error reading file - {e}")
    
    def test_css_file(self, file_path: Path) -> None:
        """Test CSS file for syntax errors"""
        self.stats['css'] += 1
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Test 1: Brace balance
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                self.errors.append(
                    f"{file_path}: Unbalanced braces ({{ {open_braces}, }} {close_braces})"
                )
            
            # Test 2: Comment balance
            open_comments = content.count('/*')
            close_comments = content.count('*/')
            if open_comments != close_comments:
                self.errors.append(
                    f"{file_path}: Unbalanced comments (/* {open_comments}, */ {close_comments})"
                )
            
            # Test 3: Check for nested comments (not allowed in CSS)
            if re.search(r'/\*[^*]*?/\*', content):
                self.warnings.append(f"{file_path}: Possible nested comment")
            
            # Test 4: Check for double closing markers
            if '*/ */' in content:
                self.errors.append(f"{file_path}: Double closing comment markers found")
            
        except Exception as e:
            self.errors.append(f"{file_path}: Error reading file - {e}")
    
    def test_js_file(self, file_path: Path) -> None:
        """Test JavaScript file for basic syntax"""
        self.stats['js'] += 1
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Test 1: Brace balance
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                self.errors.append(
                    f"{file_path}: Unbalanced braces ({{ {open_braces}, }} {close_braces})"
                )
            
            # Test 2: Parenthesis balance
            open_parens = content.count('(')
            close_parens = content.count(')')
            if open_parens != close_parens:
                self.errors.append(
                    f"{file_path}: Unbalanced parentheses (( {open_parens}, ) {close_parens})"
                )
            
            # Test 3: Bracket balance
            open_brackets = content.count('[')
            close_brackets = content.count(']')
            if open_brackets != close_brackets:
                self.errors.append(
                    f"{file_path}: Unbalanced brackets ([ {open_brackets}, ] {close_brackets})"
                )
            
            # Test 4: Comment balance (multi-line)
            open_comments = content.count('/*')
            close_comments = content.count('*/')
            if open_comments != close_comments:
                self.warnings.append(
                    f"{file_path}: Unbalanced multi-line comments (/* {open_comments}, */ {close_comments})"
                )
            
        except Exception as e:
            self.errors.append(f"{file_path}: Error reading file - {e}")
    
    def run_tests(self, base_path: Path = None) -> None:
        """Run all smoke tests"""
        if base_path is None:
            base_path = Path.cwd() / 'UI'
        
        print("\n" + "="*70)
        print(" SMOKE TEST - HTML, CSS, JavaScript Files")
        print("="*70 + "\n")
        
        # Test HTML files
        print("Testing HTML files...")
        html_files = list(base_path.glob('**/*.html'))
        for html_file in html_files:
            self.test_html_file(html_file)
        
        # Test CSS files
        print(f"\nTesting CSS files...")
        css_files = list(base_path.glob('**/*.css'))
        for css_file in css_files:
            self.test_css_file(css_file)
        
        # Test JavaScript files
        print(f"\nTesting JavaScript files...")
        js_files = list(base_path.glob('**/*.js'))
        for js_file in js_files:
            self.test_js_file(js_file)
        
        # Print results
        self.print_results()
    
    def print_results(self) -> None:
        """Print test results"""
        print("\n" + "="*70)
        print(" SMOKE TEST RESULTS")
        print("="*70)
        
        print(f"\nFiles Tested:")
        print(f"  HTML: {self.stats['html']}")
        print(f"  CSS:  {self.stats['css']}")
        print(f"  JS:   {self.stats['js']}")
        print(f"  TOTAL: {sum(self.stats.values())}")
        
        if self.errors:
            print(f"\n❌ ERRORS FOUND: {len(self.errors)}")
            print("="*70)
            for error in self.errors:
                print(f"  {error}")
        else:
            print(f"\n✅ NO ERRORS FOUND")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS: {len(self.warnings)}")
            print("="*70)
            for warning in self.warnings:
                print(f"  {warning}")
        
        print("\n" + "="*70)
        if self.errors:
            print("STATUS: ❌ FAILED - Fix errors above")
        elif self.warnings:
            print("STATUS: ⚠️  PASSED WITH WARNINGS")
        else:
            print("STATUS: ✅ ALL TESTS PASSED")
        print("="*70 + "\n")

if __name__ == '__main__':
    tester = SmokeTest()
    tester.run_tests()

"""
Code Quality Checker for AI_agents
Analyzes code quality, complexity, and standards compliance.
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any

class CodeQualityChecker:
    def __init__(self, files: List[str]):
        self.files = files
        self.issues = []
        
    def check_all(self) -> Dict[str, Any]:
        """Run all quality checks"""
        print("✨ Running code quality checks...")
        
        self.check_python_quality()
        self.check_file_size()
        self.check_line_length()
        self.check_imports()
        self.check_documentation()
        
        return {
            'issues': self.issues,
            'files_checked': len(self.files),
            'total_issues': len(self.issues),
            'severity_breakdown': self.get_severity_breakdown()
        }
    
    def check_python_quality(self):
        """Check Python code quality"""
        py_files = [f for f in self.files if f.endswith('.py') and os.path.exists(f)]
        
        if not py_files:
            return
        
        # Check with pylint if available
        try:
            for file_path in py_files:
                result = subprocess.run(
                    ['python', '-m', 'pylint', '--output-format=json', file_path],
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    try:
                        pylint_issues = json.loads(result.stdout)
                        for issue in pylint_issues:
                            severity = 'ERROR' if issue['type'] in ['error', 'fatal'] else 'WARNING'
                            self.issues.append({
                                'tool': 'Pylint',
                                'severity': severity,
                                'file': file_path,
                                'line': issue['line'],
                                'message': issue['message'],
                                'symbol': issue.get('symbol', 'N/A')
                            })
                    except json.JSONDecodeError:
                        pass
        except FileNotFoundError:
            print("  ⚠️  pylint not installed, skipping Python quality checks")
    
    def check_file_size(self):
        """Check for excessively large files"""
        for file_path in self.files:
            if not os.path.exists(file_path):
                continue
                
            try:
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                
                if size_mb > 10:
                    self.issues.append({
                        'tool': 'File Size',
                        'severity': 'ERROR',
                        'file': file_path,
                        'message': f'File too large: {size_mb:.1f}MB (max 10MB)',
                        'recommendation': 'Consider splitting into multiple files or using Git LFS'
                    })
                elif size_mb > 5:
                    self.issues.append({
                        'tool': 'File Size',
                        'severity': 'WARNING',
                        'file': file_path,
                        'message': f'Large file: {size_mb:.1f}MB',
                        'recommendation': 'Consider refactoring or splitting'
                    })
            except Exception as e:
                print(f"  ⚠️  Error checking size for {file_path}: {e}")
    
    def check_line_length(self):
        """Check for excessively long lines"""
        for file_path in self.files:
            if not file_path.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                continue
                
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines, 1):
                    line_length = len(line.rstrip())
                    
                    if line_length > 120:
                        self.issues.append({
                            'tool': 'Line Length',
                            'severity': 'WARNING',
                            'file': file_path,
                            'line': i,
                            'message': f'Line too long: {line_length} characters (max 120)',
                            'recommendation': 'Break into multiple lines'
                        })
            except Exception as e:
                print(f"  ⚠️  Error checking line length for {file_path}: {e}")
    
    def check_imports(self):
        """Check for problematic imports"""
        for file_path in self.files:
            if not file_path.endswith('.py'):
                continue
                
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines, 1):
                    # Check for wildcard imports
                    if 'import *' in line:
                        self.issues.append({
                            'tool': 'Imports',
                            'severity': 'WARNING',
                            'file': file_path,
                            'line': i,
                            'message': 'Wildcard import detected',
                            'recommendation': 'Import specific names instead'
                        })
                    
                    # Check for unused imports (basic check)
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        # Extract module name
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            module = parts[1].split('.')[0]
                            # Check if module is used in file
                            content = ''.join(lines)
                            if content.count(module) == 1:
                                self.issues.append({
                                    'tool': 'Imports',
                                    'severity': 'INFO',
                                    'file': file_path,
                                    'line': i,
                                    'message': f'Possibly unused import: {module}',
                                    'recommendation': 'Remove if not needed'
                                })
            except Exception as e:
                print(f"  ⚠️  Error checking imports for {file_path}: {e}")
    
    def check_documentation(self):
        """Check for missing documentation"""
        for file_path in self.files:
            if not file_path.endswith('.py'):
                continue
                
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Check for module docstring
                if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
                    self.issues.append({
                        'tool': 'Documentation',
                        'severity': 'WARNING',
                        'file': file_path,
                        'line': 1,
                        'message': 'Missing module docstring',
                        'recommendation': 'Add docstring describing module purpose'
                    })
                
                # Check for function/class docstrings (basic)
                in_function = False
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    
                    if stripped.startswith('def ') or stripped.startswith('class '):
                        in_function = True
                        func_name = stripped.split('(')[0].replace('def ', '').replace('class ', '')
                        
                        # Check if next non-empty line is docstring
                        next_lines = lines[i:i+3]
                        has_docstring = any('"""' in l or "'''" in l for l in next_lines)
                        
                        if not has_docstring and not func_name.startswith('_'):
                            self.issues.append({
                                'tool': 'Documentation',
                                'severity': 'INFO',
                                'file': file_path,
                                'line': i,
                                'message': f'Missing docstring for {func_name}',
                                'recommendation': 'Add docstring describing purpose and parameters'
                            })
            except Exception as e:
                print(f"  ⚠️  Error checking documentation for {file_path}: {e}")
    
    def get_severity_breakdown(self) -> Dict[str, int]:
        """Count issues by severity"""
        breakdown = {'ERROR': 0, 'WARNING': 0, 'INFO': 0}
        for issue in self.issues:
            severity = issue.get('severity', 'INFO')
            breakdown[severity] = breakdown.get(severity, 0) + 1
        return breakdown
    
    def print_report(self, results: Dict[str, Any]):
        """Print quality report"""
        print("\n" + "="*80)
        print("✨ CODE QUALITY REPORT")
        print("="*80)
        
        print(f"\n📊 Summary:")
        print(f"  Files checked: {results['files_checked']}")
        print(f"  Total issues: {results['total_issues']}")
        print(f"  Errors: {results['severity_breakdown']['ERROR']}")
        print(f"  Warnings: {results['severity_breakdown']['WARNING']}")
        print(f"  Info: {results['severity_breakdown']['INFO']}")
        
        if results['issues']:
            # Group by severity
            for severity in ['ERROR', 'WARNING', 'INFO']:
                severity_issues = [i for i in results['issues'] if i.get('severity') == severity]
                
                if severity_issues:
                    icon = '🔴' if severity == 'ERROR' else ('🟡' if severity == 'WARNING' else '🔵')
                    print(f"\n{icon} {severity} Issues ({len(severity_issues)}):")
                    
                    for issue in severity_issues[:10]:  # Show first 10
                        print(f"\n  {issue['tool']}: {issue['message']}")
                        print(f"     File: {issue['file']}")
                        if 'line' in issue:
                            print(f"     Line: {issue['line']}")
                        if 'recommendation' in issue:
                            print(f"     Fix: {issue['recommendation']}")
                    
                    if len(severity_issues) > 10:
                        print(f"\n  ... and {len(severity_issues) - 10} more")
        else:
            print("\n✅ No quality issues detected!")
        
        print("\n" + "="*80)


def get_staged_files() -> List[str]:
    """Get list of staged files from git"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=True
        )
        
        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        return files
    except subprocess.CalledProcessError:
        print("⚠️  Failed to get staged files")
        return []


def main():
    """Main entry point"""
    print("╔════════════════════════════════════════╗")
    print("║   CODE QUALITY CHECKER                ║")
    print("╚════════════════════════════════════════╝")
    
    # Get staged files
    files = get_staged_files()
    
    if not files:
        print("\n✅ No files to check")
        return 0
    
    print(f"\n📁 Checking {len(files)} staged files...")
    
    # Run checker
    checker = CodeQualityChecker(files)
    results = checker.check_all()
    
    # Print report
    checker.print_report(results)
    
    # Determine exit code
    if results['severity_breakdown']['ERROR'] > 0:
        print(f"\n❌ {results['severity_breakdown']['ERROR']} errors must be fixed before commit")
        return 1
    elif results['severity_breakdown']['WARNING'] > 10:
        print(f"\n⚠️  {results['severity_breakdown']['WARNING']} warnings found")
        response = input("   Continue with commit? (y/N): ")
        if response.lower() != 'y':
            return 1
    
    print("\n✅ Code quality check passed")
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""
Pre-Commit Security Scanner for AI_agents
Detects security vulnerabilities, secrets, and code issues before commits.
"""

import re
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

class PreCommitSecurityScanner:
    def __init__(self, git_diff_files: List[str]):
        self.files = git_diff_files
        self.vulnerabilities = []
        self.secrets_found = []
        
    def scan_all(self) -> Dict[str, Any]:
        """Run all security checks"""
        print("🔒 Running security scans...")
        
        self.scan_secrets()
        self.scan_sql_injection()
        self.scan_xss_vulnerabilities()
        self.scan_hardcoded_credentials()
        self.scan_api_keys()
        
        return {
            'secrets': self.secrets_found,
            'vulnerabilities': self.vulnerabilities,
            'severity': self.calculate_severity(),
            'files_scanned': len(self.files)
        }
    
    def scan_secrets(self):
        """Detect hardcoded secrets and credentials"""
        
        secret_patterns = {
            'AWS_ACCESS_KEY': r'AKIA[0-9A-Z]{16}',
            'AWS_SECRET_KEY': r'aws_secret_access_key\s*=\s*["\']([^"\']+)["\']',
            'GITHUB_TOKEN': r'ghp_[a-zA-Z0-9]{36}',
            'SLACK_TOKEN': r'xox[baprs]-[a-zA-Z0-9-]+',
            'OPENAI_API_KEY': r'sk-[a-zA-Z0-9]{32,}',
            'ANTHROPIC_API_KEY': r'sk-ant-[a-zA-Z0-9_-]{95,}',
            'DEEPSEEK_API_KEY': r'sk-[a-zA-Z0-9]{32,}',
            'STRIPE_SECRET': r'sk_live_[a-zA-Z0-9]{24,}',
            'PRIVATE_KEY': r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----',
            'GENERIC_API_KEY': r'api[_-]?key\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
            'PASSWORD': r'password\s*[:=]\s*["\']([^"\']{8,})["\']',
            'DATABASE_URL': r'(postgres|mysql|mongodb):\/\/[^:]+:[^@]+@',
            'JWT_SECRET': r'jwt[_-]?secret\s*[:=]\s*["\']([^"\']{16,})["\']',
            'SUPABASE_KEY': r'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
        }
        
        for file_path in self.files:
            if not os.path.exists(file_path):
                continue
                
            # Skip certain file types
            if file_path.endswith(('.json', '.md', '.txt', '.lock', '.yaml', '.yml')):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for secret_type, pattern in secret_patterns.items():
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        # Check if it's in a comment (less severe)
                        line_start = content.rfind('\n', 0, match.start()) + 1
                        line = content[line_start:content.find('\n', match.start())]
                        is_comment = line.strip().startswith(('#', '//', '/*', '*'))
                        
                        # Check if it's an example/placeholder
                        is_placeholder = any(p in match.group(0).lower() for p in [
                            'example', 'placeholder', 'your_', 'xxx', '***', 'fake',
                            'test', 'dummy', 'sample', '<', '>'
                        ])
                        
                        if not is_placeholder:
                            line_num = content[:match.start()].count('\n') + 1
                            self.secrets_found.append({
                                'type': secret_type,
                                'file': file_path,
                                'line': line_num,
                                'severity': 'LOW' if is_comment else 'CRITICAL',
                                'value': match.group(0)[:30] + '...',
                                'recommendation': 'Move to environment variables or .env.master'
                            })
            except Exception as e:
                print(f"⚠️  Error scanning {file_path}: {e}")
    
    def scan_sql_injection(self):
        """Detect potential SQL injection vulnerabilities"""
        
        sql_injection_patterns = [
            r'(SELECT|INSERT|UPDATE|DELETE).*[\+\$\{]',  # String concatenation
            r'\.query\([\'"`].*\+',  # Query with concatenation
            r'execute\([\'"`].*\+',  # Execute with concatenation
            r'raw\([\'"`].*\+',  # Raw query with concatenation
            r'f[\'"].*SELECT.*\{',  # Python f-string with SELECT
        ]
        
        for file_path in self.files:
            if not file_path.endswith(('.js', '.ts', '.py', '.java', '.php')):
                continue
                
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines, 1):
                    for pattern in sql_injection_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Check if parameterized query is used nearby
                            context = ''.join(lines[max(0, i-3):i+2])
                            is_parameterized = any(p in context for p in ['%s', '$1', 'prepared', 'bind', ':param', '?'])
                            
                            if not is_parameterized:
                                self.vulnerabilities.append({
                                    'type': 'SQL_INJECTION',
                                    'severity': 'CRITICAL',
                                    'file': file_path,
                                    'line': i,
                                    'code': line.strip()[:100],
                                    'description': 'Possible SQL injection via string concatenation',
                                    'fix': 'Use parameterized queries or prepared statements'
                                })
            except Exception as e:
                print(f"⚠️  Error scanning {file_path}: {e}")
    
    def scan_xss_vulnerabilities(self):
        """Detect potential XSS vulnerabilities"""
        
        xss_patterns = [
            r'innerHTML\s*=',
            r'dangerouslySetInnerHTML',
            r'\.html\(',
            r'document\.write\(',
            r'eval\(',
        ]
        
        for file_path in self.files:
            if not file_path.endswith(('.js', '.jsx', '.ts', '.tsx', '.html')):
                continue
                
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines, 1):
                    for pattern in xss_patterns:
                        if re.search(pattern, line):
                            # Check if input is sanitized
                            context = ''.join(lines[max(0, i-3):i+2])
                            is_sanitized = any(s in context for s in [
                                'sanitize', 'escape', 'DOMPurify', 'validator.escape',
                                'textContent', 'createTextNode'
                            ])
                            
                            if not is_sanitized:
                                self.vulnerabilities.append({
                                    'type': 'XSS',
                                    'severity': 'HIGH',
                                    'file': file_path,
                                    'line': i,
                                    'code': line.strip()[:100],
                                    'description': 'Potential XSS vulnerability - unsanitized user input',
                                    'fix': 'Sanitize user input before rendering or use textContent'
                                })
            except Exception as e:
                print(f"⚠️  Error scanning {file_path}: {e}")
    
    def scan_hardcoded_credentials(self):
        """Scan for hardcoded database credentials"""
        
        credential_patterns = [
            r'(host|server)\s*[:=]\s*["\'](?!localhost)[^"\']+["\']',
            r'(user|username)\s*[:=]\s*["\'](?!admin|root|test)[^"\']+["\']',
            r'(pass|password)\s*[:=]\s*["\'](?!password|test)[^"\']+["\']',
            r'(port)\s*[:=]\s*["\']?\d{4,5}',
        ]
        
        for file_path in self.files:
            if file_path.endswith(('.md', '.txt', '.json')):
                continue
                
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Look for credential clusters (multiple credential patterns near each other)
                for match in re.finditer(credential_patterns[0], content, re.IGNORECASE):
                    start = max(0, match.start() - 200)
                    end = min(len(content), match.end() + 200)
                    cluster = content[start:end]
                    
                    # Count how many credential patterns are in this cluster
                    credential_count = sum(1 for p in credential_patterns if re.search(p, cluster, re.IGNORECASE))
                    
                    if credential_count >= 3:
                        line_num = content[:match.start()].count('\n') + 1
                        self.secrets_found.append({
                            'type': 'HARDCODED_CREDENTIALS',
                            'file': file_path,
                            'line': line_num,
                            'severity': 'HIGH',
                            'value': 'Multiple credentials found in close proximity',
                            'recommendation': 'Move credentials to .env.master or config.py'
                        })
                        break
            except Exception as e:
                print(f"⚠️  Error scanning {file_path}: {e}")
    
    def scan_api_keys(self):
        """Scan for API keys that should be in config"""
        
        api_key_patterns = {
            'ANTHROPIC': r'sk-ant-[a-zA-Z0-9_-]{95,}',
            'OPENAI': r'sk-proj-[a-zA-Z0-9]{48,}',
            'DEEPSEEK': r'sk-[a-zA-Z0-9]{48,}',
            'GOOGLE': r'AIza[0-9A-Za-z_-]{35}',
        }
        
        for file_path in self.files:
            # Skip config files where keys are expected
            if 'config' in file_path.lower() or '.env' in file_path:
                continue
                
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for provider, pattern in api_key_patterns.items():
                    if re.search(pattern, content):
                        line_num = 1
                        self.secrets_found.append({
                            'type': f'{provider}_API_KEY',
                            'file': file_path,
                            'line': line_num,
                            'severity': 'CRITICAL',
                            'value': f'{provider} API key detected',
                            'recommendation': 'Import from config.py using get_api_key_enhanced()'
                        })
            except Exception as e:
                print(f"⚠️  Error scanning {file_path}: {e}")
    
    def calculate_severity(self) -> str:
        """Calculate overall severity"""
        if any(s['severity'] == 'CRITICAL' for s in self.secrets_found + self.vulnerabilities):
            return 'CRITICAL'
        elif any(s['severity'] == 'HIGH' for s in self.vulnerabilities):
            return 'HIGH'
        elif len(self.secrets_found) + len(self.vulnerabilities) > 0:
            return 'MEDIUM'
        return 'LOW'
    
    def print_report(self, results: Dict[str, Any]):
        """Print detailed security report"""
        print("\n" + "="*80)
        print("🔒 SECURITY SCAN REPORT")
        print("="*80)
        
        print(f"\n📊 Summary:")
        print(f"  Files scanned: {results['files_scanned']}")
        print(f"  Secrets found: {len(results['secrets'])}")
        print(f"  Vulnerabilities: {len(results['vulnerabilities'])}")
        print(f"  Overall severity: {results['severity']}")
        
        if results['secrets']:
            print(f"\n🔐 Secrets Detected ({len(results['secrets'])}):")
            for secret in results['secrets']:
                severity_color = '🔴' if secret['severity'] == 'CRITICAL' else '🟡'
                print(f"\n  {severity_color} {secret['type']}")
                print(f"     File: {secret['file']}:{secret['line']}")
                print(f"     Value: {secret['value']}")
                print(f"     Fix: {secret['recommendation']}")
        
        if results['vulnerabilities']:
            print(f"\n⚠️  Vulnerabilities Detected ({len(results['vulnerabilities'])}):")
            for vuln in results['vulnerabilities']:
                severity_color = '🔴' if vuln['severity'] == 'CRITICAL' else '🟠'
                print(f"\n  {severity_color} {vuln['type']}")
                print(f"     File: {vuln['file']}:{vuln['line']}")
                print(f"     Code: {vuln['code']}")
                print(f"     Description: {vuln['description']}")
                print(f"     Fix: {vuln['fix']}")
        
        if not results['secrets'] and not results['vulnerabilities']:
            print("\n✅ No security issues detected!")
        
        print("\n" + "="*80)


def get_staged_files() -> List[str]:
    """Get list of staged files from git"""
    import subprocess
    
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
    print("║   PRE-COMMIT SECURITY SCANNER         ║")
    print("╚════════════════════════════════════════╝")
    
    # Get staged files
    files = get_staged_files()
    
    if not files:
        print("\n✅ No files to scan")
        return 0
    
    print(f"\n📁 Scanning {len(files)} staged files...")
    
    # Run scanner
    scanner = PreCommitSecurityScanner(files)
    results = scanner.scan_all()
    
    # Print report
    scanner.print_report(results)
    
    # Determine exit code
    if results['severity'] == 'CRITICAL':
        print("\n❌ COMMIT BLOCKED: Critical security issues must be fixed!")
        print("   Fix the issues above and try again.")
        return 1
    elif results['severity'] == 'HIGH':
        print("\n⚠️  WARNING: High severity issues found!")
        response = input("   Continue with commit anyway? (y/N): ")
        if response.lower() != 'y':
            return 1
    elif results['severity'] == 'MEDIUM':
        print("\n⚠️  Medium severity issues found - review recommended")
    
    print("\n✅ Security scan passed")
    return 0


if __name__ == '__main__':
    sys.exit(main())

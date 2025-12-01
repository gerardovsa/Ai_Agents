"""
Commit Message Validator for AI_agents
Validates commit messages against conventional commits format.
"""

import sys
import re
from typing import Dict, List

class CommitMessageValidator:
    # Valid commit types from Conventional Commits
    VALID_TYPES = [
        'feat', 'fix', 'docs', 'style', 'refactor', 
        'perf', 'test', 'chore', 'build', 'ci', 'revert'
    ]
    
    def __init__(self, commit_msg: str):
        self.commit_msg = commit_msg
        self.errors = []
        self.warnings = []
        
    def validate(self) -> Dict[str, any]:
        """Validate commit message against standards"""
        self.check_format()
        self.check_length()
        self.check_type()
        self.check_breaking_changes()
        self.check_body()
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def check_format(self):
        """Check conventional commits format: type(scope): description"""
        lines = self.commit_msg.split('\n')
        first_line = lines[0] if lines else ''
        
        # Pattern: type(scope): description OR type: description
        pattern = r'^(feat|fix|docs|style|refactor|perf|test|chore|build|ci|revert)(\([a-z0-9_-]+\))?: .+'
        
        if not re.match(pattern, first_line, re.IGNORECASE):
            self.errors.append(
                'Commit message must follow conventional commits format:\n'
                '  type(scope): description\n'
                f'  Valid types: {", ".join(self.VALID_TYPES)}\n'
                '  Example: feat(auth): add Google OAuth integration'
            )
    
    def check_length(self):
        """Check subject line length"""
        lines = self.commit_msg.split('\n')
        first_line = lines[0] if lines else ''
        
        if len(first_line) > 72:
            self.errors.append(
                f'Subject line too long ({len(first_line)} chars, max 72)\n'
                '  Keep subject concise, use body for details'
            )
        elif len(first_line) < 10:
            self.warnings.append(
                f'Subject line very short ({len(first_line)} chars)\n'
                '  Consider adding more context'
            )
    
    def check_type(self):
        """Check if commit type is appropriate"""
        lines = self.commit_msg.split('\n')
        first_line = lines[0] if lines else ''
        
        # Extract type
        match = re.match(r'^([a-z]+)', first_line, re.IGNORECASE)
        if not match:
            return
        
        commit_type = match.group(1).lower()
        full_message = self.commit_msg.lower()
        
        # Check for common mismatches
        if commit_type == 'fix' and 'test' not in full_message:
            self.warnings.append(
                'Bug fix commits should ideally include test updates\n'
                '  Consider adding or updating tests'
            )
        
        if commit_type == 'feat' and 'doc' not in full_message:
            self.warnings.append(
                'Feature commits should include documentation\n'
                '  Consider updating README or adding docs'
            )
        
        if commit_type == 'refactor':
            if 'test' not in full_message:
                self.warnings.append(
                    'Refactoring should include test verification\n'
                    '  Ensure existing tests still pass'
                )
    
    def check_breaking_changes(self):
        """Check for BREAKING CHANGE footer"""
        if 'BREAKING CHANGE' in self.commit_msg or '!' in self.commit_msg.split('\n')[0]:
            # Check if there's an explanation
            if 'BREAKING CHANGE:' in self.commit_msg:
                explanation = self.commit_msg.split('BREAKING CHANGE:')[1].strip()
                if len(explanation) < 20:
                    self.errors.append(
                        'BREAKING CHANGE must include detailed explanation\n'
                        '  Explain what breaks and how to migrate'
                    )
            else:
                self.warnings.append(
                    'Breaking change indicator (!) found but no BREAKING CHANGE footer\n'
                    '  Add footer: BREAKING CHANGE: <explanation>'
                )
    
    def check_body(self):
        """Check commit body format"""
        lines = self.commit_msg.split('\n')
        
        if len(lines) > 1:
            # Check for blank line after subject
            if len(lines) > 1 and lines[1].strip() != '':
                self.warnings.append(
                    'Add blank line between subject and body\n'
                    '  Improves readability in git log'
                )
            
            # Check body line length
            for i, line in enumerate(lines[2:], start=3):
                if len(line) > 80 and not line.startswith('http'):
                    self.warnings.append(
                        f'Body line {i} too long ({len(line)} chars, max 80)\n'
                        '  Wrap body text at 72-80 characters'
                    )
                    break
    
    def print_report(self, results: Dict):
        """Print validation report"""
        print("\n" + "="*80)
        print("📝 COMMIT MESSAGE VALIDATION")
        print("="*80)
        
        if results['errors']:
            print("\n❌ ERRORS:")
            for error in results['errors']:
                print(f"\n  {error}")
        
        if results['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in results['warnings']:
                print(f"\n  {warning}")
        
        if not results['errors'] and not results['warnings']:
            print("\n✅ Commit message is valid!")
        
        print("\n" + "="*80)


def main():
    """Main entry point (called by commit-msg git hook)"""
    if len(sys.argv) < 2:
        print("Usage: commit_message_validator.py <commit-msg-file>")
        return 1
    
    commit_msg_file = sys.argv[1]
    
    try:
        with open(commit_msg_file, 'r', encoding='utf-8') as f:
            commit_msg = f.read()
    except Exception as e:
        print(f"Error reading commit message: {e}")
        return 1
    
    print("╔════════════════════════════════════════╗")
    print("║   COMMIT MESSAGE VALIDATOR            ║")
    print("╚════════════════════════════════════════╝")
    
    validator = CommitMessageValidator(commit_msg)
    results = validator.validate()
    
    validator.print_report(results)
    
    if results['errors']:
        print("\n❌ Commit message validation failed!")
        print("   Fix the errors above and try again.\n")
        return 1
    
    if results['warnings']:
        print("\n⚠️  Commit message has warnings")
        response = input("   Continue with commit? (y/N): ")
        if response.lower() != 'y':
            return 1
    
    print("\n✅ Commit message validated")
    return 0


if __name__ == '__main__':
    sys.exit(main())

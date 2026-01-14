#!/usr/bin/env python3
"""
Auto-detect deployment version from branch name or environment
Used during Docker build to embed version info
"""
import os
import subprocess
import json
import sys

def get_version_info():
    """Detect version from git branch or environment"""
    version_info = {
        'branch': 'unknown',
        'version': 'unknown',
        'commit': 'unknown',
        'expected_url': None
    }
    
    try:
        # Get current branch name
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        version_info['branch'] = branch
        
        # Extract version number from branch (v10, v11, v12, etc.)
        if branch.startswith('v') and len(branch) > 1:
            version_num = branch[1:]
            if version_num.isdigit():
                version_info['version'] = version_num
                version_info['expected_url'] = f'https://ai-agents-v{version_num}.onrender.com'
        
        # Get commit hash
        commit = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        version_info['commit'] = commit
        
    except Exception as e:
        print(f"Warning: Could not detect version from git: {e}", file=sys.stderr)
    
    # Check for environment override
    if os.getenv('VERSION_NUMBER'):
        version_info['version'] = os.getenv('VERSION_NUMBER')
        version_info['expected_url'] = f"https://ai-agents-v{os.getenv('VERSION_NUMBER')}.onrender.com"
    
    if os.getenv('EXPECTED_URL'):
        version_info['expected_url'] = os.getenv('EXPECTED_URL')
    
    return version_info

if __name__ == '__main__':
    info = get_version_info()
    print(json.dumps(info, indent=2))

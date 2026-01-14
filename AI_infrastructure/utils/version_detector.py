"""
Version Detection Utility
Auto-detects deployment version from embedded version info or git branch
Used for constructing correct frontend URLs without manual configuration
"""
import os
import json
import subprocess
from typing import Optional, Dict

class VersionDetector:
    """Detects deployment version and constructs expected URLs"""
    
    def __init__(self):
        self._version_info = None
        self._load_version_info()
    
    def _load_version_info(self):
        """Load embedded version info from Docker build"""
        version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'version_info.json')
        
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    self._version_info = json.load(f)
                    print(f"Loaded version info: {self._version_info}")
                    return
            except Exception as e:
                print(f"Warning: Could not load version_info.json: {e}")
        
        # Fallback: detect from git
        self._version_info = self._detect_from_git()
    
    def _detect_from_git(self) -> Dict[str, Optional[str]]:
        """Detect version from git branch name"""
        try:
            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8').strip()
            
            version_info = {
                'branch': branch,
                'version': 'unknown',
                'expected_url': None
            }
            
            # Extract version from branch name (v10, v11, etc.)
            if branch.startswith('v') and len(branch) > 1:
                version_num = branch[1:]
                if version_num.isdigit():
                    version_info['version'] = version_num
                    version_info['expected_url'] = f'https://ai-agents-v{version_num}.onrender.com'
            
            return version_info
            
        except Exception as e:
            print(f"Warning: Could not detect version from git: {e}")
            return {
                'branch': 'unknown',
                'version': 'unknown',
                'expected_url': None
            }
    
    def get_version_number(self) -> Optional[str]:
        """Get version number (10, 11, 12, etc.)"""
        return self._version_info.get('version')
    
    def get_branch_name(self) -> Optional[str]:
        """Get git branch name"""
        return self._version_info.get('branch')
    
    def get_expected_frontend_url(self) -> Optional[str]:
        """Get expected frontend URL for this version"""
        # Check environment override first
        if os.getenv('EXPECTED_URL'):
            return os.getenv('EXPECTED_URL')
        
        # Use embedded/detected URL
        return self._version_info.get('expected_url')
    
    def get_version_info(self) -> Dict:
        """Get complete version info dictionary"""
        return self._version_info.copy()


# Global instance
_version_detector = None

def get_version_detector() -> VersionDetector:
    """Get singleton VersionDetector instance"""
    global _version_detector
    if _version_detector is None:
        _version_detector = VersionDetector()
    return _version_detector

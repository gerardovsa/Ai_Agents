"""
Work Timeline Tool - Configuration Template
Copy this file to 'config.py' and customize for your projects
"""

# ============================================
# PROJECT CONFIGURATION
# ============================================

# Define your projects here
# Format: 'DisplayName': 'C:/full/path/to/project'
PROJECTS = {
    'ProjectName1': 'C:/Users/YourName/Projects/project1',
    'ProjectName2': 'C:/Users/YourName/Projects/project2',
}

# ============================================
# FILE CATEGORIZATION RULES
# ============================================

# Customize how files are categorized
# Each category returns: (Category, Technical Label, Business Label)

def get_file_category(file_path):
    """
    Categorize files based on extension and path
    Returns: (category, technical_label, business_label)
    """
    path_lower = file_path.lower()
    
    # Python Backend
    if path_lower.endswith('.py'):
        if 'test' in path_lower:
            return ('Python Backend', 'Python Testing', 'Testing & Validation')
        elif 'route' in path_lower or 'api' in path_lower:
            return ('Python Backend', 'API Routes', 'Server APIs')
        elif 'auth' in path_lower:
            return ('Python Backend', 'Authentication', 'Security & Access')
        elif 'db' in path_lower or 'database' in path_lower:
            return ('Python Backend', 'Database Connections', 'Database Integration')
        elif 'tool' in path_lower:
            return ('Python Backend', 'Tool Implementation', 'Feature Tools')
        elif 'util' in path_lower or 'helper' in path_lower:
            return ('Python Backend', 'Utilities', 'Helper Functions')
        else:
            return ('Python Backend', 'Core Logic', 'Business Logic')
    
    # Frontend
    elif path_lower.endswith(('.html', '.htm')):
        if 'ui' in path_lower or 'interface' in path_lower:
            return ('Frontend', 'Interface Pages', 'User Interfaces')
        return ('Frontend', 'Interface Pages', 'User Interfaces')
    
    elif path_lower.endswith('.css'):
        return ('Frontend', 'Stylesheets', 'Visual Styling')
    
    elif path_lower.endswith(('.js', '.jsx', '.ts', '.tsx')):
        if 'test' in path_lower:
            return ('Frontend', 'JavaScript Testing', 'Testing & Validation')
        elif 'chart' in path_lower or 'graph' in path_lower:
            return ('Frontend', 'Data Display - Graphs & Charts', 'Data Visualization')
        return ('Frontend', 'Frontend Functions', 'Client Logic')
    
    # Database
    elif path_lower.endswith('.sql'):
        if 'migration' in path_lower:
            return ('Database', 'Data Migrations', 'Database Updates')
        elif 'function' in path_lower or 'proc' in path_lower:
            return ('Database', 'SQL Functions', 'Database Operations')
        return ('Database', 'Database Tables & Schemas', 'Database Structure')
    
    elif path_lower.endswith(('.db', '.sqlite', '.sqlite3')):
        return ('Database', 'Database Tables & Schemas', 'Database Structure')
    
    # Configuration
    elif path_lower.endswith(('.json', '.yaml', '.yml', '.toml', '.ini')):
        if 'schema' in path_lower:
            return ('Configuration', 'Data Schemas', 'Data Structure')
        elif 'config' in path_lower or 'setting' in path_lower:
            return ('Configuration', 'Configuration Files', 'Settings')
        return ('Configuration', 'Application Settings', 'Configuration')
    
    elif path_lower.endswith(('.env', '.env.example')):
        return ('Configuration', 'Application Settings', 'Configuration')
    
    # Documentation
    elif path_lower.endswith(('.md', '.txt', '.rst')):
        if 'readme' in path_lower:
            return ('Documentation', 'Project Overview', 'Documentation')
        elif 'changelog' in path_lower or 'history' in path_lower:
            return ('Documentation', 'Change History', 'Version Tracking')
        elif 'guide' in path_lower or 'tutorial' in path_lower:
            return ('Documentation', 'User Guides', 'How-To Documents')
        return ('Documentation', 'Technical Documentation', 'Documentation')
    
    # Testing
    elif 'test' in path_lower:
        if path_lower.endswith(('.json', '.xml', '.csv')):
            return ('Testing', 'Test Data', 'Test Assets')
        elif path_lower.endswith(('.log', '.txt')):
            return ('Testing', 'Debug Logs', 'Testing Outputs')
        return ('Testing', 'Test Data', 'Test Assets')
    
    # Build/Deploy
    elif path_lower.endswith(('.sh', '.bat', '.ps1')):
        return ('Build/Deploy', 'Deployment Scripts', 'Build & Deploy')
    
    elif 'venv' in path_lower or 'env' in path_lower or 'virtualenv' in path_lower:
        return ('Build/Deploy', 'Virtual Environment', 'Environment Setup')
    
    elif 'node_modules' in path_lower or 'site-packages' in path_lower:
        return ('Build/Deploy', 'External Code Libraries', 'Dependencies')
    
    # Other
    elif path_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico')):
        return ('Other', 'Images & Graphics', 'Visual Assets')
    
    elif path_lower.endswith(('.ttf', '.woff', '.woff2', '.eot')):
        return ('Other', 'Font Files', 'Typography')
    
    elif path_lower.endswith(('.git', '.gitignore', '.gitattributes')):
        return ('Other', 'Version Control', 'Git Files')
    
    else:
        return ('Other', 'Miscellaneous', 'Other Files')


# ============================================
# HOUR CALCULATION SETTINGS
# ============================================

# Adjust how hours are estimated from file counts
# Formula: hours = (file_count / FILES_PER_HOUR) capped at MAX_HOURS_PER_DAY
FILES_PER_HOUR = 100  # Average files edited per hour
MAX_HOURS_PER_DAY = 18  # Maximum realistic work hours per day

# ============================================
# INTENSITY LEVEL THRESHOLDS
# ============================================

INTENSITY_LEVELS = {
    'marathon': 14,  # 14+ hours
    'long': 10,      # 10-14 hours
    'full': 7,       # 7-10 hours
    'half': 0        # <7 hours
}

# ============================================
# COLOR SCHEME
# ============================================

CATEGORY_COLORS = {
    'Python Backend': '#3498db',      # Blue
    'Frontend': '#e74c3c',            # Red
    'Database': '#9b59b6',            # Purple
    'Configuration': '#f39c12',       # Orange
    'Documentation': '#27ae60',       # Green
    'Testing': '#16a085',             # Cyan
    'Build/Deploy': '#8e44ad',        # Deep Purple
    'Other': '#95a5a6'                # Gray
}

# ============================================
# OUTPUT SETTINGS
# ============================================

OUTPUT_HTML = 'focused_timeline_detailed.html'
OUTPUT_JSON = 'timeline_data.json'  # Optional JSON export

# Date format for display
DATE_FORMAT = '%b %d'  # Example: "Nov 11"
FULL_DATE_FORMAT = '%Y-%m-%d'  # Example: "2025-11-11"

# ============================================
# EXCLUSION PATTERNS
# ============================================

# Folders to exclude from scanning
EXCLUDE_FOLDERS = [
    'node_modules',
    '__pycache__',
    '.git',
    'venv',
    'env',
    '.vscode',
    '.idea',
    'dist',
    'build',
    '.pytest_cache'
]

# File patterns to exclude
EXCLUDE_FILES = [
    '*.pyc',
    '*.pyo',
    '*.log',
    '.DS_Store',
    'Thumbs.db'
]

# ============================================
# USAGE NOTES
# ============================================

"""
To use this configuration:

1. Copy this file to 'config.py'
2. Update PROJECTS with your project paths
3. Customize get_file_category() for your file types
4. Adjust thresholds and colors as needed
5. Run: python create_focused_timeline.py

The tool will:
- Scan all files in specified projects
- Categorize them using your rules
- Generate interactive HTML dashboard
- Auto-populate statistics and charts
"""

"""
FOCUSED TIMELINE - InHouse Print + AI_agents + G_Folder
Detailed categorization with color-coded component types
"""

import os
from datetime import datetime
from collections import defaultdict
import math

# Only these projects
FOCUSED_PROJECTS = [
    'AI_agents',
    'In_House_SQL',
    'In_House_Print',
    'In_House_V2',
    'In_House_FRED',
    'G_Folder Oct 8th',
    'G_Folder Oct 10th',
    'G_Folder Oct 14th',
    'G_Folder Oct 15th',
    'G_Folder Oct 17th'
]

def categorize_file_detailed(filename, filepath):
    """Categorize file by type with detailed sub-categories"""
    ext = os.path.splitext(filename)[1].lower()
    path_lower = filepath.lower()
    
    # Python Backend
    if ext == '.py':
        if 'test_' in filename or '_test.py' in filename or 'testing' in path_lower:
            return ('Python Backend', 'Python Testing', 'Testing & Validation')
        elif 'route' in path_lower or 'endpoint' in path_lower:
            return ('Python Backend', 'API Routes', 'Server APIs')
        elif 'auth' in path_lower or 'oauth' in path_lower:
            return ('Python Backend', 'Authentication', 'Security & Access')
        elif 'database' in path_lower or 'db_' in filename or 'model' in path_lower:
            return ('Python Backend', 'Database Connections', 'Database Integration')
        elif 'tool' in path_lower or 'implementation' in path_lower:
            return ('Python Backend', 'Tool Implementation', 'Feature Tools')
        elif 'util' in path_lower or 'helper' in path_lower:
            return ('Python Backend', 'Utilities', 'Helper Functions')
        elif 'calculator' in path_lower or 'pricing' in path_lower:
            return ('Python Backend', 'Calculators', 'Business Logic')
        else:
            return ('Python Backend', 'Core Logic', 'Server Logic')
    
    # Frontend - HTML/CSS
    elif ext in ['.html', '.htm']:
        if 'timeline' in filename or 'chart' in filename or 'graph' in filename:
            return ('Frontend', 'Data Display - Graphs & Charts', 'Data Visualization')
        elif 'dashboard' in filename or 'ui' in path_lower:
            return ('Frontend', 'Interface Pages', 'User Interfaces')
        elif 'stock' in path_lower:
            return ('Frontend', 'Stock Management UI', 'Business Features')
        elif 'template' in path_lower:
            return ('Frontend', 'Interface Pages', 'User Interfaces')
        else:
            return ('Frontend', 'Interface Pages', 'User Interfaces')
    
    elif ext == '.css':
        return ('Frontend', 'Stylesheets', 'Visual Styling')
    
    # JavaScript
    elif ext == '.js' or ext == '.mjs':
        if 'test' in filename:
            return ('Frontend', 'JavaScript Testing', 'Testing & Validation')
        elif 'chart' in filename or 'graph' in filename or 'visual' in filename:
            return ('Frontend', 'Data Display - Graphs & Charts', 'Data Visualization')
        elif 'api' in filename or 'fetch' in filename:
            return ('Frontend', 'Frontend Functions', 'Client Logic')
        else:
            return ('Frontend', 'Frontend Functions', 'Client Logic')
    
    # Database
    elif ext in ['.sql', '.db', '.sqlite', '.sqlite3']:
        if 'migration' in path_lower:
            return ('Database', 'Data Migrations', 'Database Updates')
        elif 'schema' in filename:
            return ('Database', 'Database Tables & Schemas', 'Database Structure')
        else:
            return ('Database', 'SQL Functions', 'Database Operations')
    
    # Configuration
    elif ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf']:
        if 'package' in filename:
            return ('Configuration', 'External Code Libraries', 'Dependencies')
        elif 'config' in filename or 'settings' in filename:
            return ('Configuration', 'Application Settings', 'Configuration')
        elif 'schema' in filename:
            return ('Configuration', 'Data Schemas', 'Data Structure')
        else:
            return ('Configuration', 'Configuration Files', 'Settings')
    
    # Documentation
    elif ext in ['.md', '.rst', '.txt']:
        if 'readme' in filename.lower():
            return ('Documentation', 'Project Overview', 'Documentation')
        elif 'changelog' in filename.lower():
            return ('Documentation', 'Change History', 'Version Tracking')
        elif 'guide' in filename.lower() or 'tutorial' in filename.lower():
            return ('Documentation', 'User Guides', 'How-To Documents')
        else:
            return ('Documentation', 'Technical Documentation', 'Documentation')
    
    # Testing Data
    elif ext in ['.csv', '.xlsx', '.xls']:
        if 'test' in path_lower or 'mock' in path_lower or 'fixture' in path_lower:
            return ('Testing', 'Test Data', 'Test Assets')
        else:
            return ('Testing', 'Data Files', 'Test Assets')
    
    # Images & Assets (library imports - miscellaneous)
    elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp']:
        return ('Other', 'Images & Graphics', 'Visual Assets')
    
    elif ext in ['.ttf', '.woff', '.woff2', '.eot', '.otf']:
        return ('Other', 'Font Files', 'Typography')
    
    # Build & Deploy
    elif ext in ['.bat', '.ps1', '.sh']:
        return ('Build/Deploy', 'Deployment Scripts', 'Build & Deploy')
    
    elif filename in ['Dockerfile', 'docker-compose.yml', '.dockerignore']:
        return ('Build/Deploy', 'Virtual Environment', 'Environment Setup')
    
    elif filename in ['requirements.txt', 'setup.py', 'pyproject.toml']:
        return ('Build/Deploy', 'External Code Libraries', 'Dependencies')
    
    # Logs & Temp (debugging/testing output)
    elif ext in ['.log', '.tmp', '.cache']:
        return ('Testing', 'Debug Logs', 'Testing Outputs')
    
    # Git
    elif '.git' in path_lower and ext != '.md':
        return ('Other', 'Version Control', 'Git Files')
    
    # Default
    else:
        return ('Other', 'Miscellaneous', 'Other Files')

def scan_focused_projects():
    """Scan only InHouse Print, AI_agents, and G_Folder projects"""
    base_path = r"C:\Users\gpoli\GIT"
    
    print("Scanning focused projects...")
    
    files_by_date = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    total_files = 0
    
    for project in FOCUSED_PROJECTS:
        project_path = os.path.join(base_path, project)
        
        if not os.path.exists(project_path):
            continue
        
        print(f"  {project}...", end='', flush=True)
        count = 0
        
        try:
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 
                                                          '.vscode', 'venv', 'env', 'archive',
                                                          'dist', 'build', '.pytest_cache']]
                
                for filename in files:
                    if filename.startswith('.'):
                        continue
                    
                    filepath = os.path.join(root, filename)
                    try:
                        stats = os.stat(filepath)
                        created = datetime.fromtimestamp(stats.st_ctime)
                        date_str = created.strftime('%Y-%m-%d')
                        
                        # Categorize file
                        category, technical_label, business_label = categorize_file_detailed(filename, filepath)
                        
                        files_by_date[date_str][project][f"{category}|{technical_label}|{business_label}"] += 1
                        count += 1
                        total_files += 1
                    except:
                        continue
            
            print(f" {count:,}")
        except Exception as e:
            print(f" ERROR: {e}")
    
    print(f"\nTotal files: {total_files:,}")
    return files_by_date

def create_focused_timeline_html(files_by_date):
    """Create detailed timeline with categorization"""
    
    dates = sorted(files_by_date.keys())
    
    # Color scheme for categories - ALL UNIQUE COLORS
    category_colors = {
        'Python Backend': {
            'base': '#3498db',
            'subcategories': {
                'API Routes': '#2980b9',
                'Authentication': '#1f618d',
                'Database': '#5dade2',
                'Tool Implementation': '#85c1e9',
                'Utilities': '#aed6f1',
                'Calculators': '#d6eaf8',
                'Testing': '#ebf5fb',
                'Core Logic': '#3498db'
            }
        },
        'Frontend': {
            'base': '#e74c3c',
            'subcategories': {
                'UI Pages': '#c0392b',
                'Visualizations': '#e74c3c',
                'Stock Management': '#ec7063',
                'Templates': '#f1948a',
                'Stylesheets': '#f5b7b1',
                'JavaScript': '#fadbd8',
                'Charting': '#f8e1e0',
                'API Client': '#cb4335',
                'JS Testing': '#e6b0aa',
                'HTML Pages': '#e74c3c'
            }
        },
        'Database': {
            'base': '#9b59b6',
            'subcategories': {
                'Schema': '#8e44ad',
                'Migrations': '#a569bd',
                'SQL Files': '#bb8fce'
            }
        },
        'Configuration': {
            'base': '#f39c12',
            'subcategories': {
                'Settings': '#d68910',
                'Dependencies': '#f39c12',
                'Schemas': '#f8c471',
                'Config Files': '#fad7a0'
            }
        },
        'Documentation': {
            'base': '#27ae60',
            'subcategories': {
                'README': '#229954',
                'Changelog': '#27ae60',
                'Guides': '#52be80',
                'Documentation': '#7dcea0'
            }
        },
        'Testing': {
            'base': '#00bcd4',
            'subcategories': {
                'Test Data': '#0097a7',
                'Data Files': '#26c6da',
                'Debug Logs': '#00acc1'
            }
        },
        'Build/Deploy': {
            'base': '#8e44ad',
            'subcategories': {
                'Scripts': '#7d3c98',
                'Docker': '#8e44ad',
                'Dependencies': '#a569bd'
            }
        },
        'Other': {
            'base': '#95a5a6',
            'subcategories': {
                'Miscellaneous': '#7f8c8d',
                'Images': '#95a5a6',
                'Fonts': '#bdc3c7',
                'Git Files': '#34495e'
            }
        }
    }
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InHouse Print & AI Agents - Detailed Timeline</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        
        .container {{
            max-width: 100%;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            font-size: 1.3em;
            opacity: 0.9;
            margin-bottom: 20px;
        }}
        
        .header .period {{
            font-size: 1.1em;
            opacity: 0.8;
        }}
        
        .view-toggle {{
            margin-top: 20px;
        }}
        
        .toggle-btn {{
            background: white;
            color: #2c3e50;
            border: none;
            padding: 12px 30px;
            font-size: 1em;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        
        .toggle-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.3);
        }}
        
        .toggle-btn:active {{
            transform: translateY(0);
        }}
        
        .toggle-btn.business {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        
        .stat-card .label {{
            font-size: 0.9em;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .timeline-container {{
            padding: 30px;
            display: flex;
            gap: 20px;
        }}
        
        .sidebar {{
            width: 280px;
            flex-shrink: 0;
            overflow-y: auto;
            max-height: 700px;
            border-right: 3px solid #ecf0f1;
            padding-right: 20px;
        }}
        
        .category-group {{
            margin-bottom: 25px;
        }}
        
        .category-title {{
            font-weight: bold;
            color: #2c3e50;
            padding: 12px 0;
            border-bottom: 3px solid;
            margin-bottom: 12px;
            font-size: 1em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .subcategory-item {{
            padding: 8px 0 8px 15px;
            font-size: 0.85em;
            color: #555;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .color-box {{
            width: 14px;
            height: 14px;
            border-radius: 3px;
            flex-shrink: 0;
        }}
        
        .timeline {{
            flex: 1;
            overflow-x: auto;
            overflow-y: auto;
            max-height: 700px;
        }}
        
        .timeline-header {{
            display: flex;
            margin-bottom: 15px;
            font-weight: bold;
            font-size: 0.9em;
            color: #2c3e50;
            position: sticky;
            top: 0;
            background: white;
            z-index: 10;
            padding-bottom: 15px;
            border-bottom: 3px solid #ecf0f1;
        }}
        
        .date-column {{
            width: 130px;
            flex-shrink: 0;
        }}
        
        .bars-column {{
            flex: 1;
            min-width: 1000px;
        }}
        
        .timeline-row {{
            display: flex;
            margin-bottom: 3px;
            align-items: center;
            min-height: 35px;
        }}
        
        .timeline-row:hover {{
            background: #f8f9fa;
        }}
        
        .date-label {{
            width: 130px;
            flex-shrink: 0;
            font-size: 0.85em;
            padding-right: 15px;
        }}
        
        .date-main {{
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .date-day {{
            color: #95a5a6;
            font-size: 0.85em;
            margin-left: 5px;
        }}
        
        .bars-container {{
            flex: 1;
            display: flex;
            flex-wrap: wrap;
            gap: 3px;
            min-width: 1000px;
            align-items: center;
        }}
        
        .component-bar {{
            height: 28px;
            border-radius: 5px;
            position: relative;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7em;
            color: white;
            font-weight: 600;
            padding: 0 8px;
            white-space: nowrap;
        }}
        
        .component-bar[data-category="Testing"] {{
            height: 32px;
            font-weight: 700;
            border: 2px solid rgba(255, 255, 255, 0.4);
            box-shadow: 0 2px 8px rgba(0, 188, 212, 0.3);
        }}
        
        .component-bar:hover {{
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 100;
        }}
        
        .component-bar .tooltip {{
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #2c3e50;
            color: white;
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 0.8em;
            white-space: nowrap;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 1000;
            margin-bottom: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        
        .component-bar:hover .tooltip {{
            opacity: 1;
        }}
        
        .legend {{
            padding: 30px;
            background: #f8f9fa;
            border-top: 3px solid #ecf0f1;
        }}
        
        .legend-title {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.3em;
        }}
        
        .legend-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 25px;
        }}
        
        .legend-category {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .legend-category-title {{
            font-weight: bold;
            font-size: 1em;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid;
        }}
        
        .legend-subcategory {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 8px 0;
            font-size: 0.85em;
        }}
        
        .legend-color {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            flex-shrink: 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>InHouse Print & AI Agents</h1>
            <div class="subtitle">Detailed Component Timeline</div>
            <div class="period">August 20 - November 8, 2025</div>
            <div class="view-toggle">
                <button class="toggle-btn" id="viewToggle" onclick="toggleView()">
                    Switch to Business View
                </button>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="value">{sum(sum(sum(cat.values()) for cat in files_by_date[d].values()) for d in dates):,}</div>
                <div class="label">Total Files</div>
            </div>
            <div class="stat-card">
                <div class="value">{len(dates)}</div>
                <div class="label">Work Days</div>
            </div>
            <div class="stat-card">
                <div class="value">{len(FOCUSED_PROJECTS)}</div>
                <div class="label">Projects</div>
            </div>
            <div class="stat-card">
                <div class="value">{len(category_colors)}</div>
                <div class="label">Categories</div>
            </div>
        </div>
        
        <div class="timeline-container">
            <div class="sidebar">"""
    
    # Sidebar with categories
    for category, colors in sorted(category_colors.items()):
        base_color = colors['base']
        html += f"""
                <div class="category-group">
                    <div class="category-title" style="border-color: {base_color}; color: {base_color};">
                        {category}
                    </div>"""
        
        for subcat, color in sorted(colors['subcategories'].items()):
            html += f"""
                    <div class="subcategory-item" data-technical="{subcat}">
                        <div class="color-box" style="background: {color};"></div>
                        <span class="subcat-label">{subcat}</span>
                    </div>"""
        
        html += """
                </div>"""
    
    html += """
            </div>
            
            <div class="timeline">
                <div class="timeline-header">
                    <div class="date-column">Date</div>
                    <div class="bars-column">Components</div>
                </div>"""
    
    # Timeline rows
    for date_str in dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_name = date_obj.strftime('%a')
        display_date = date_obj.strftime('%b %d')
        
        html += f"""
                <div class="timeline-row">
                    <div class="date-label">
                        <span class="date-main">{display_date}</span>
                        <span class="date-day">{day_name}</span>
                    </div>
                    <div class="bars-container">"""
        
        # Collect all components for this date across all projects
        all_components = defaultdict(int)
        for project_data in files_by_date[date_str].values():
            for component, count in project_data.items():
                all_components[component] += count
        
        # Sort by category first (to group by color), then by count within category
        # Category order: Python Backend, Frontend, Database, Configuration, Documentation, Testing, Build/Deploy, Other
        category_order = {
            'Python Backend': 1,
            'Frontend': 2,
            'Database': 3,
            'Configuration': 4,
            'Documentation': 5,
            'Testing': 6,
            'Build/Deploy': 7,
            'Other': 8
        }
        
        sorted_components = sorted(
            all_components.items(),
            key=lambda x: (
                category_order.get(x[0].split('|')[0], 99),  # Sort by category order
                -x[1]  # Then by count (descending) within category
            )
        )
        
        # Create bars
        for component_key, count in sorted_components:
            parts = component_key.split('|')
            category = parts[0]
            technical_label = parts[1] if len(parts) > 1 else 'Unknown'
            business_label = parts[2] if len(parts) > 2 else technical_label
            
            # Get color (use technical_label to match old subcategory logic)
            color = category_colors.get(category, {}).get('subcategories', {}).get(technical_label, '#95a5a6')
            
            # Width based on count (logarithmic)
            width = min(150, max(40, math.log(count + 1) * 25))
            
            # Show count if bar is wide enough
            show_count = width > 60
            
            html += f"""
                        <div class="component-bar" 
                             style="width: {width}px; background: {color};"
                             data-category="{category}"
                             data-technical="{technical_label}"
                             data-business="{business_label}">
                            {f'{count}' if show_count else ''}
                            <div class="tooltip">
                                <span class="tooltip-label">{category}: {technical_label}</span>
                                <br>{count:,} files
                            </div>
                        </div>"""
        
        html += """
                    </div>
                </div>"""
    
    html += """
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-title">Component Categories & Types</div>
            <div class="legend-grid">"""
    
    # Legend
    for category, colors in sorted(category_colors.items()):
        base_color = colors['base']
        html += f"""
                <div class="legend-category">
                    <div class="legend-category-title" style="color: {base_color}; border-color: {base_color};">
                        {category}
                    </div>"""
        
        for subcat, color in sorted(colors['subcategories'].items()):
            html += f"""
                    <div class="legend-subcategory" data-technical="{subcat}">
                        <div class="legend-color" style="background: {color};"></div>
                        <span class="legend-label">{subcat}</span>
                    </div>"""
        
        html += """
                </div>"""
    
    html += """
            </div>
        </div>
    </div>
    
    <script>
        // View mode state
        let isBusinessView = false;
        
        // Label mapping: technical -> business
        const labelMapping = {
            // Python Backend
            'Python Testing': 'Testing & Validation',
            'Database Connections': 'Database Integration',
            'API Routes': 'Server APIs',
            'Authentication': 'Security & Access',
            'Feature Tools': 'Feature Tools',
            'Helper Functions': 'Helper Functions',
            'Business Logic': 'Business Logic',
            'Server Logic': 'Server Logic',
            
            // Frontend
            'Interface Pages': 'User Interfaces',
            'Data Display - Graphs & Charts': 'Data Visualization',
            'Stock Management UI': 'Business Features',
            'Stylesheets': 'Visual Styling',
            'Frontend Functions': 'Client Logic',
            'JavaScript Testing': 'Testing & Validation',
            
            // Database
            'Data Migrations': 'Database Updates',
            'Database Tables & Schemas': 'Database Structure',
            'SQL Functions': 'Database Operations',
            
            // Testing
            'Test Data': 'Test Assets',
            'Data Files': 'Test Assets',
            'Debug Logs': 'Testing Outputs',
            
            // Build/Deploy
            'Deployment Scripts': 'Build & Deploy',
            'Virtual Environment': 'Environment Setup',
            'External Code Libraries': 'Dependencies',
            
            // Configuration
            'Application Settings': 'Configuration',
            'Data Schemas': 'Data Structure',
            'Configuration Files': 'Settings',
            
            // Documentation
            'Project Overview': 'Documentation',
            'Change History': 'Version Tracking',
            'User Guides': 'How-To Documents',
            'Technical Documentation': 'Documentation',
            
            // Other
            'Images & Graphics': 'Visual Assets',
            'Font Files': 'Typography',
            'Version Control': 'Git Files',
            'Miscellaneous': 'Other Files'
        };
        
        function toggleView() {
            isBusinessView = !isBusinessView;
            const btn = document.getElementById('viewToggle');
            
            if (isBusinessView) {
                btn.textContent = 'Switch to Technical View';
                btn.classList.add('business');
                updateLabels('business');
            } else {
                btn.textContent = 'Switch to Business View';
                btn.classList.remove('business');
                updateLabels('technical');
            }
            
            // Save preference
            localStorage.setItem('timelineView', isBusinessView ? 'business' : 'technical');
        }
        
        function updateLabels(mode) {
            // Update component bars tooltips
            document.querySelectorAll('.component-bar').forEach(bar => {
                const category = bar.dataset.category;
                const technical = bar.dataset.technical;
                const business = bar.dataset.business;
                
                const label = mode === 'business' ? business : technical;
                const tooltipLabel = bar.querySelector('.tooltip-label');
                if (tooltipLabel) {
                    tooltipLabel.textContent = category + ': ' + label;
                }
            });
            
            // Update sidebar subcategory items
            document.querySelectorAll('.subcategory-item').forEach(item => {
                const technical = item.dataset.technical;
                const business = labelMapping[technical] || technical;
                const label = mode === 'business' ? business : technical;
                
                const span = item.querySelector('.subcat-label');
                if (span) {
                    span.textContent = label;
                }
            });
            
            // Update bottom legend subcategory items
            document.querySelectorAll('.legend-subcategory').forEach(item => {
                const technical = item.dataset.technical;
                const business = labelMapping[technical] || technical;
                const label = mode === 'business' ? business : technical;
                
                const span = item.querySelector('.legend-label');
                if (span) {
                    span.textContent = label;
                }
            });
        }
        
        // Load saved preference
        window.addEventListener('DOMContentLoaded', () => {
            const savedView = localStorage.getItem('timelineView');
            if (savedView === 'business') {
                toggleView();
            }
        });
        
        // Synchronize scrolling
        const sidebar = document.querySelector('.sidebar');
        const timeline = document.querySelector('.timeline');
        
        timeline.addEventListener('scroll', () => {
            sidebar.scrollTop = timeline.scrollTop;
        });
        
        // Log stats
        console.log('Timeline loaded with detailed categorization and view toggle');
    </script>
</body>
</html>"""
    
    return html

if __name__ == "__main__":
    print("\n" + "="*80)
    print("FOCUSED TIMELINE - InHouse Print + AI_agents + G_Folder")
    print("="*80 + "\n")
    
    # Scan projects
    files_by_date = scan_focused_projects()
    
    # Create HTML
    html = create_focused_timeline_html(files_by_date)
    
    # Save
    output_file = 'focused_timeline_detailed.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n{'='*80}")
    print(f"DONE - Focused timeline with detailed categorization")
    print(f"Saved to: {output_file}")
    print(f"{'='*80}\n")

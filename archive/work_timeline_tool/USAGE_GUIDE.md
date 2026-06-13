# Work Timeline Tool - Complete Usage Guide

## 📋 Table of Contents
1. [First Time Setup](#first-time-setup)
2. [Basic Usage](#basic-usage)
3. [Customization](#customization)
4. [Advanced Features](#advanced-features)
5. [Troubleshooting](#troubleshooting)
6. [Tips & Tricks](#tips--tricks)

---

## 🚀 First Time Setup

### Step 1: Create Configuration File

```powershell
# Copy the template
Copy-Item config_template.py config.py
```

### Step 2: Edit Configuration

Open `config.py` and update your project paths:

```python
PROJECTS = {
    'MyWebApp': 'C:/Users/YourName/Projects/webapp',
    'MobileApp': 'C:/Users/YourName/Projects/mobile',
}
```

### Step 3: Generate Timeline

**Option A: Using Quick Start Scripts**
```powershell
# PowerShell
.\quick_start.ps1

# OR Command Prompt
quick_start.bat
```

**Option B: Manual Python Execution**
```powershell
python create_focused_timeline.py
```

### Step 4: View Dashboard

The script will automatically open `focused_timeline_detailed.html` in your browser.

---

## 📊 Basic Usage

### Generating a New Timeline

Every time you want to update the timeline with new work:

```powershell
cd work_timeline_tool
python create_focused_timeline.py
```

This will:
- Scan all files in configured projects
- Extract creation timestamps
- Categorize files by type
- Generate updated HTML dashboard
- Preserve all styling and features

### Understanding the Dashboard

The generated dashboard has **5 tabs**:

#### 1. 📅 Timeline View
- Visual timeline of all file changes
- Color-coded by category (8 categories)
- Horizontal bars show file volumes
- Toggle between Technical/Business labels
- Expandable legend with all subcategories

#### 2. 📊 Labor Summary
- Total hours and work days
- Project breakdown (hours per project)
- Work patterns analysis
- Consecutive work streaks
- Weekend work statistics

#### 3. ⏰ Daily Hours (Auto-Populated!)
- **Automatically shows ALL dates** from your timeline
- Hours worked per day
- File count per day
- Intensity level (Marathon/Long/Full/Half)
- Visual progress bars
- **No manual updates needed!**

#### 4. 🔥 Work Intensity
- Top 5 most intense days
- Top 5 most productive days
- Intensity category breakdown
- Visual badges and highlights

#### 5. 📋 Combined Analysis
- Weekend work details
- Time period distribution
- After-hours work analysis
- Work intensity breakdown
- Dedication metrics
- Comparison to standard workweek

---

## 🎨 Customization

### Adding New Project

Edit `config.py`:

```python
PROJECTS = {
    'ExistingProject': 'C:/existing/path',
    'NewProject': 'C:/new/project/path',  # Add this line
}
```

Then regenerate:
```powershell
python create_focused_timeline.py
```

### Custom File Categories

Edit the `get_file_category()` function in `config.py`:

```python
def get_file_category(file_path):
    path_lower = file_path.lower()
    
    # Add your custom rules
    if path_lower.endswith('.vue'):
        return ('Frontend', 'Vue Components', 'UI Components')
    
    if 'microservice' in path_lower:
        return ('Python Backend', 'Microservices', 'Service Architecture')
    
    # ... existing rules ...
```

### Adjusting Hour Calculations

In `config.py`:

```python
# More aggressive hour counting (more hours per file)
FILES_PER_HOUR = 50  # Default: 100

# Allow higher daily hours
MAX_HOURS_PER_DAY = 20  # Default: 18
```

### Changing Intensity Thresholds

In `config.py`:

```python
INTENSITY_LEVELS = {
    'marathon': 16,  # Increase marathon threshold
    'long': 12,      # Increase long day threshold
    'full': 8,       # Increase full day threshold
    'half': 0        # Everything else is half day
}
```

### Custom Color Scheme

In `config.py`:

```python
CATEGORY_COLORS = {
    'Python Backend': '#2ecc71',    # Change to green
    'Frontend': '#3498db',          # Change to blue
    # ... customize other colors ...
}
```

---

## 🔧 Advanced Features

### Excluding Folders/Files

In `config.py`:

```python
EXCLUDE_FOLDERS = [
    'node_modules',
    '__pycache__',
    'my_custom_folder_to_exclude',  # Add custom exclusions
]

EXCLUDE_FILES = [
    '*.pyc',
    '*.log',
    'temp_*.txt',  # Add patterns
]
```

### Multiple Timeline Versions

Keep different configurations for different purposes:

```powershell
# Create specialized configs
Copy-Item config.py config_client_presentation.py
Copy-Item config.py config_internal_review.py

# Use specific config (modify script to import it)
python create_focused_timeline.py
```

### Exporting Data

The timeline data is embedded in the HTML. To extract:

1. Open browser Developer Tools (F12)
2. Run in console:
```javascript
const data = extractTimelineData();
console.table(data);
// Copy data or export as needed
```

### Automating Timeline Generation

Create a scheduled task or cron job:

**PowerShell (Windows Task Scheduler)**:
```powershell
cd C:\path\to\work_timeline_tool
python create_focused_timeline.py
```

Run daily/weekly to keep timeline updated.

---

## 🐛 Troubleshooting

### Issue: "config.py not found"

**Solution**: Copy the template:
```powershell
Copy-Item config_template.py config.py
```

### Issue: "No timeline data generated"

**Causes**:
- Invalid project paths
- Empty projects
- Permission issues

**Solution**: Check paths in config.py:
```python
# Verify paths exist
import os
for name, path in PROJECTS.items():
    print(f"{name}: {os.path.exists(path)}")
```

### Issue: "Daily Hours tab is empty"

**Solution**: The auto-population system runs on page load. 
- Refresh the page (F5)
- Check browser console (F12) for errors
- Verify timeline has data in Timeline View tab

### Issue: "Hours seem incorrect"

**Solution**: Adjust calculation formula in `config.py`:
```python
FILES_PER_HOUR = 150  # Increase for fewer hours
MAX_HOURS_PER_DAY = 16  # Decrease max cap
```

### Issue: "Files in wrong categories"

**Solution**: Update `get_file_category()` in `config.py` with more specific rules:
```python
# Add more specific rules at the TOP of the function
if 'my_special_folder' in path_lower:
    return ('Custom Category', 'Special Files', 'Business Label')
```

### Issue: "Python not found"

**Solution**: 
1. Install Python 3.x from python.org
2. Add to PATH during installation
3. Restart terminal/PowerShell
4. Verify: `python --version`

---

## 💡 Tips & Tricks

### Tip 1: Label Toggle for Presentations

- Click "Toggle View" to switch between technical and business-friendly labels
- Business labels are better for client presentations
- Technical labels are better for team reviews

### Tip 2: Filtering by Category

- Click any subcategory in the legend
- Files are visually highlighted
- Great for isolating specific types of work

### Tip 3: Intensity Analysis

Use the Work Intensity tab to:
- Find your most productive days
- Identify patterns (late nights? weekends?)
- Balance workload better

### Tip 4: Exporting for Invoices

1. Open Combined Analysis tab
2. Take screenshot (Win+Shift+S)
3. Include in client invoice as work breakdown
4. Professional presentation of hours worked

### Tip 5: Comparing Projects

Generate separate timelines for each project:
```python
# config_project1.py
PROJECTS = {'Project1': 'path1'}

# config_project2.py
PROJECTS = {'Project2': 'path2'}
```

Compare outputs side-by-side.

### Tip 6: Date Range Focus

To focus on specific date range:
1. Generate full timeline
2. In browser, use Find (Ctrl+F)
3. Search for specific month: "Oct", "Nov", etc.
4. Browser highlights relevant days

### Tip 7: Quick Stats

Open browser console (F12) and run:
```javascript
const stats = calculateStatistics();
console.table(stats);
```

Instant overview of all metrics!

---

## 📱 Browser Compatibility

✅ **Fully Supported**:
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

⚠️ **Limited Support**:
- Internet Explorer (not recommended)

---

## 🔄 Updating the Tool

To get latest features:
1. Backup your `config.py`
2. Replace all other files with new versions
3. Restore your `config.py`
4. Regenerate timeline

---

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review README.md
3. Check browser console for JavaScript errors
4. Verify Python script runs without errors

---

## 🎯 Best Practices

1. **Regular Updates**: Regenerate timeline weekly
2. **Consistent Categorization**: Keep file categories consistent
3. **Meaningful Labels**: Use clear business-friendly labels
4. **Backup Configs**: Keep backup of custom configurations
5. **Version Control**: Track timeline HTMLs in Git (optional)
6. **Performance**: For projects with 10,000+ files, consider filtering

---

**Happy Timeline Tracking! 📊**

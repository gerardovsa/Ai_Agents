# Work Timeline Tool 📊

A professional, reusable tool for generating interactive work timeline visualizations and labor analysis dashboards from any Git repository or project folder.

## 🎯 Features

### Interactive Timeline Visualization
- **File-level tracking** with category-based color coding
- **Dual-view toggle**: Technical labels ↔ Business-friendly labels
- **8 category system**: Python Backend, Frontend, Database, Configuration, Documentation, Testing, Build/Deploy, Other
- **Auto-sorting by category** with expandable subcategories
- **Smart tooltips** showing file counts and descriptions

### Labor Statistics Dashboard
- **5 comprehensive tabs**:
  1. 📅 Timeline View - Visual timeline with all file changes
  2. 📊 Labor Summary - Project breakdown and work patterns
  3. ⏰ Daily Hours - Complete daily breakdown (auto-populated!)
  4. 🔥 Work Intensity - Top intense/productive days
  5. 📋 Combined Analysis - Work schedule and dedication metrics

### Auto-Population System 🚀
- **Dynamic data extraction** from timeline
- **Automatic calculations** for hours, intensity, statistics
- **No manual HTML editing** required
- **Real-time updates** when timeline data changes

## 📁 Files

### Core Scripts
- **`create_focused_timeline.py`** - Main timeline generator (recommended)
- **`analyze_all_work.py`** - Work hours analyzer with daily breakdowns
- **`calculate_actual_work_hours.py`** - Accurate work hours calculator
- **`professional_timeline.py`** - Alternative timeline generator
- **`analyze_file_activity_timeline.py`** - File activity analysis

### Output Files
- **`focused_timeline_detailed.html`** - Complete interactive dashboard (main output)
- **`professional_timeline.html`** - Alternative timeline view

## 🚀 Quick Start

### Step 1: Configure Projects

Edit the project paths in `create_focused_timeline.py`:

```python
PROJECTS = {
    'ProjectName1': 'C:/path/to/project1',
    'ProjectName2': 'C:/path/to/project2',
}
```

### Step 2: Generate Timeline

```powershell
cd work_timeline_tool
python create_focused_timeline.py
```

This will:
1. Scan all files in specified projects
2. Extract file creation timestamps
3. Generate categorized timeline
4. Create interactive HTML dashboard
5. Output: `focused_timeline_detailed.html`

### Step 3: View Dashboard

Open `focused_timeline_detailed.html` in any browser. The auto-population system will:
- Extract all timeline data
- Calculate hours and statistics
- Populate all tabs dynamically
- Display complete date range

## 📊 Customization

### Add New Project
```python
PROJECTS = {
    'YourProject': 'C:/path/to/your/project',
    'Another': 'D:/another/project',
}
```

### Adjust File Categories

Edit the `get_file_category()` function in `create_focused_timeline.py`:

```python
def get_file_category(file_path):
    if file_path.endswith('.py'):
        return ('Python Backend', 'Core Logic', 'Server Logic')
    # Add your custom rules here
```

### Modify Intensity Thresholds

In `focused_timeline_detailed.html`, edit the `getIntensityLevel()` function:

```javascript
function getIntensityLevel(hours) {
    if (hours >= 14) return { level: 'marathon', label: 'Marathon', color: '#e74c3c' };
    if (hours >= 10) return { level: 'long', label: 'Long Day', color: '#f39c12' };
    if (hours >= 7) return { level: 'full', label: 'Full Day', color: '#3498db' };
    return { level: 'half', label: 'Half Day', color: '#27ae60' };
}
```

## 🎨 Color Scheme

| Category | Primary Color | Usage |
|----------|--------------|-------|
| Python Backend | Blues (#3498db) | Core logic, APIs, authentication |
| Frontend | Reds (#e74c3c) | UI, HTML, CSS, JavaScript |
| Database | Purples (#9b59b6) | SQL, migrations, schemas |
| Configuration | Oranges (#f39c12) | Config files, settings |
| Documentation | Greens (#27ae60) | README, docs, guides |
| Testing | Cyan (#16a085) | Test files, debug logs |
| Build/Deploy | Deep Purple (#8e44ad) | Deployment, environment |
| Other | Grays (#95a5a6) | Assets, fonts, misc |

## 🔧 Advanced Features

### Auto-Population System

The HTML dashboard includes JavaScript that:
- **Extracts timeline data** from DOM on page load
- **Calculates statistics** (hours, intensity, breakdowns)
- **Populates Daily Hours tab** with ALL dates
- **Updates header metrics** dynamically
- **Console logging** for debugging

No manual updates needed - just regenerate the Python script!

### View Toggle

Click "Toggle View" button to switch between:
- **Technical View**: Developer-focused labels (e.g., "API Routes")
- **Business View**: Client-friendly labels (e.g., "Server APIs")

### Responsive Design

- **Grid layout** adapts to screen size
- **Horizontal scroll** on legend/categories
- **Mobile-friendly** cards and tables
- **Professional gradient** backgrounds

## 📈 Use Cases

1. **Client Presentations**: Show work breakdown and hours
2. **Project Quotes**: Calculate accurate labor costs
3. **Team Reports**: Visualize development progress
4. **Time Tracking**: Analyze work patterns and intensity
5. **Portfolio**: Demonstrate project complexity

## 🛠️ Requirements

- Python 3.x
- No external libraries required (uses only standard library)
- Modern web browser (Chrome, Firefox, Edge, Safari)

## 📝 Data Privacy

All processing is done locally:
- No external API calls
- No data uploaded to servers
- Files stay on your machine
- Safe for confidential projects

## 🐛 Troubleshooting

### Issue: Empty timeline
**Solution**: Check project paths in `PROJECTS` dictionary

### Issue: Missing dates in Daily Hours tab
**Solution**: Refresh page - auto-population runs on load (500ms delay)

### Issue: Incorrect hour calculations
**Solution**: Adjust the formula in `extractTimelineData()`:
```javascript
const estimatedHours = Math.min(Math.round((totalFiles / 100) * 10) / 10, 18);
```

### Issue: Wrong file categories
**Solution**: Update `get_file_category()` function in Python script

## 📦 Export & Share

The generated HTML file is:
- **Self-contained** (all CSS/JS inline)
- **No dependencies** required
- **Email-friendly** (single file)
- **Print-ready** via browser print function

## 🔄 Updates

To update with new work:
1. Run `python create_focused_timeline.py` again
2. New timeline generated with latest files
3. Open updated HTML
4. Auto-population extracts new data

## 📄 License

Free to use for personal and commercial projects.

## 🤝 Contributing

To enhance this tool:
1. Modify Python scripts for data extraction
2. Update HTML/CSS for styling changes
3. Edit JavaScript for calculation logic
4. Add new tabs/sections as needed

## 🎯 Future Enhancements

Potential additions:
- [ ] Export to PDF
- [ ] JSON data export
- [ ] Date range filtering
- [ ] Project comparison view
- [ ] Cost calculator integration
- [ ] CSV export for spreadsheets
- [ ] Dark mode theme
- [ ] Multi-language support

---

**Version**: 2.0  
**Last Updated**: November 11, 2025  
**Status**: Production Ready with Auto-Population

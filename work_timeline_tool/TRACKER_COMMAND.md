# TRACKER - Global Command Documentation

## ✅ Installation Complete!

The **TRACKER** command has been successfully installed as a global PowerShell function.

---

## 🚀 Usage

### From ANY folder, simply run:

```powershell
TRACKER
```

That's it! The command will:
1. Navigate to the timeline tool folder
2. Check/create config.py if needed
3. Generate your timeline
4. Open it in a new browser tab
5. Return you to your original folder

---

## 📍 Command Features

### ✅ Works From Anywhere
```powershell
# From your project folder
PS C:\Users\gpoli\GIT\MyProject> TRACKER

# From your desktop
PS C:\Users\gpoli\Desktop> TRACKER

# From any location
PS D:\SomeOtherFolder> TRACKER
```

### ✅ Auto-Setup
- Creates `config.py` from template if missing
- Opens config in editor for first-time setup
- Validates Python installation
- Checks all dependencies

### ✅ Error Handling
- Clear error messages
- Troubleshooting hints
- Graceful failures
- Returns to original folder even on error

### ✅ Browser Integration
- Opens timeline in new browser tab
- Uses your default browser
- Doesn't interrupt your current work

---

## 🎯 Common Workflows

### First Time Use
```powershell
# Run TRACKER
TRACKER

# It will create config.py and open it
# Edit your project paths
# Save and close

# Run TRACKER again
TRACKER

# Timeline generates and opens!
```

### Regular Use
```powershell
# Just run TRACKER whenever you want updated timeline
TRACKER
```

### Quick Check
```powershell
# From your current project
cd C:\Users\gpoli\GIT\MyProject

# Generate timeline
TRACKER

# Continue working - you're back in MyProject folder
```

---

## 📊 What You Get

When TRACKER runs successfully, you'll see:

```
===============================================
   TRACKER - Work Timeline Generator
===============================================

[1/4] Navigating to tool directory...
[2/4] Checking Python...
  Python 3.13.0
[3/4] Generating timeline...
  (This may take a few moments for large projects)

[4/4] Opening timeline in new browser tab...

===============================================
   SUCCESS! Timeline Generated & Opened
===============================================

Dashboard opened in your browser:
  C:\Users\gpoli\GIT\AI_agents\work_timeline_tool\focused_timeline_detailed.html

Features:
  - Timeline View (visual file changes)
  - Labor Summary (project breakdown)
  - Daily Hours (all dates, auto-populated!)
  - Work Intensity (top days)
  - Combined Analysis (schedule breakdown)

Tip: Run TRACKER anytime to regenerate with latest data
```

---

## 🔧 Configuration

### Location
The TRACKER function is defined in:
```
C:\Users\gpoli\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
```

### Tool Location
Points to:
```
C:\Users\gpoli\GIT\AI_agents\work_timeline_tool
```

### Editing
To modify the TRACKER function:
```powershell
# Open profile in editor
code $PROFILE

# Or in Notepad
notepad $PROFILE

# Find the "function TRACKER" section
# Make changes
# Save

# Reload profile
. $PROFILE
```

---

## 🐛 Troubleshooting

### Issue: "TRACKER command not found"

**Solution**: Reload PowerShell profile
```powershell
. $PROFILE
```

Or restart PowerShell.

---

### Issue: "config.py not found"

**Solution**: TRACKER will auto-create it
- Run `TRACKER`
- It creates `config.py` from template
- Opens it for editing
- Edit project paths
- Save
- Run `TRACKER` again

---

### Issue: "Timeline generation failed"

**Causes**:
- Invalid project paths in `config.py`
- Missing project folders
- Permission issues

**Solution**:
1. Open config: `code C:\Users\gpoli\GIT\AI_agents\work_timeline_tool\config.py`
2. Verify paths exist
3. Check folder permissions
4. Run `TRACKER` again

---

### Issue: "Python not found"

**Solution**: 
1. Install Python 3.x from python.org
2. Add to PATH during installation
3. Restart PowerShell
4. Run `python --version` to verify
5. Run `TRACKER` again

---

### Issue: Browser doesn't open

**Solution**: Manually open the file
```
C:\Users\gpoli\GIT\AI_agents\work_timeline_tool\focused_timeline_detailed.html
```

---

## 🔄 Updating TRACKER

If a new version is released:

```powershell
cd C:\Users\gpoli\GIT\AI_agents\work_timeline_tool
.\install_tracker_command.ps1
```

Select "y" to update when prompted.

---

## 📝 Similar Commands

You now have these global commands:

| Command | Purpose |
|---------|---------|
| `TRACKER` | Work timeline generator |
| `BISTART` | Launch AI Agents platform |
| `RESTARTNEW` | Launch In House Print |
| `RESTARTVALOR` | Launch VSA |
| `TRANSCRIPTIONHTML` | Launch Transcription UI |

---

## 💡 Pro Tips

### Tip 1: Quick Updates
```powershell
# After working on projects, quickly regenerate timeline
TRACKER
```

### Tip 2: Multiple Projects
```powershell
# Edit config.py to add/remove projects
code C:\Users\gpoli\GIT\AI_agents\work_timeline_tool\config.py

# Add new project
PROJECTS = {
    'ExistingProject': 'C:/path1',
    'NewProject': 'C:/path2',  # Add this
}

# Run TRACKER to include new project
TRACKER
```

### Tip 3: Automation
Create a scheduled task to run TRACKER daily:
```powershell
# In Task Scheduler, run:
powershell.exe -Command "TRACKER"
```

### Tip 4: Share Timeline
```powershell
# Generate timeline
TRACKER

# Copy the HTML file
Copy-Item C:\Users\gpoli\GIT\AI_agents\work_timeline_tool\focused_timeline_detailed.html C:\Users\gpoli\Desktop\client_work_report.html

# Email to client - it's self-contained!
```

---

## 📚 Additional Resources

- **README.md** - Full tool documentation
- **USAGE_GUIDE.md** - Detailed usage guide
- **CHANGELOG.md** - Version history
- **INDEX.md** - File navigation

All located in:
```
C:\Users\gpoli\GIT\AI_agents\work_timeline_tool\
```

---

## 🎉 Success!

You can now run **TRACKER** from anywhere to instantly generate and view your work timeline!

**Test it now:**
```powershell
TRACKER
```

---

**Last Updated**: November 11, 2025  
**Version**: 2.0.0  
**Status**: ✅ Installed & Ready

# Documentation Standards Quick Reference

**For AI_agents Project**

---

## 📋 File Headers

### When Creating ANY New File
Add this header at the top:

**JavaScript/TypeScript:**
```javascript
/**
 * FILE: path/to/file.js
 * PURPOSE: What this file does
 * DEPENDENCIES: internal files + packages
 * EXPORTS: functions/classes
 * USED BY: who imports this
 * RELATED FILES: related files
 * NOTES: important details
 * LAST MODIFIED: YYYY-MM-DD - what changed
 */
```

**Python:**
```python
"""
FILE: path/to/file.py
PURPOSE: What this file does
DEPENDENCIES: internal modules + packages
EXPORTS: functions/classes with types
USED BY: who imports this
RELATED FILES: related files
NOTES: important details
LAST MODIFIED: YYYY-MM-DD - what changed
"""
```

---

## 📁 Folder Documentation

### Every Folder Needs
- ✅ **README.md** - Overview, structure, patterns

### Active Development Folders Need
- ✅ **README.md** - Overview
- ✅ **NOTES.md** - Current work, decisions, session log

### Production Code Folders Need
- ✅ **README.md** - Overview
- ✅ **CHANGELOG.md** - Change history

### Large Folders (10+ files) Need
- ✅ **README.md** - Overview
- ✅ **INDEX.md** - Complete file inventory

---

## 🔄 Update Workflow

### When Modifying Code
1. Update the code
2. Update file header LAST MODIFIED
3. Update NOTES.md (what you did)
4. Update README.md (if behavior changed)

### When Completing Work
1. Move NOTES.md entries to CHANGELOG.md
2. Update README.md (if needed)
3. Update INDEX.md (if new files added)
4. Commit with descriptive message

---

## 🤖 AI Usage

### Creating New File
```
@file:templates/FILE_HEADER_TEMPLATE.md
Create path/to/newFile.js with proper header
```

### Creating Folder Docs
```
@file:templates/README_TEMPLATE.md
Create README.md for folder/name/
```

### Tracking Development
```
@file:templates/NOTES_TEMPLATE.md
Create NOTES.md for active development tracking
```

### Creating Agent Context
```
@file:templates/AGENT_CONTEXT_TEMPLATE.md
Create agents/FEATURE_AGENT.md
```

---

## 📚 Templates Location

All templates: `c:\Users\gpoli\GIT\AI_agents\templates\`

- `FILE_HEADER_TEMPLATE.md` - Code file headers
- `README_TEMPLATE.md` - Folder overview
- `NOTES_TEMPLATE.md` - Development tracking
- `CHANGELOG_TEMPLATE.md` - Change history
- `INDEX_TEMPLATE.md` - File inventory
- `AGENT_CONTEXT_TEMPLATE.md` - Agent scope

---

## ✅ Checklist

### Before Starting Work
- [ ] Read folder README.md
- [ ] Check NOTES.md for current state
- [ ] Check agent context file (if applicable)

### When Creating Files
- [ ] Add file header from template
- [ ] Document in folder README.md
- [ ] Add to INDEX.md (if exists)
- [ ] Log in NOTES.md

### When Modifying Files
- [ ] Update LAST MODIFIED in header
- [ ] Log changes in NOTES.md
- [ ] Update README.md (if needed)

### Before Deployment
- [ ] Move NOTES.md entries to CHANGELOG.md
- [ ] Verify all headers are current
- [ ] Check README.md is accurate
- [ ] Update INDEX.md (if needed)

---

## 🚫 DON'Ts

- ❌ Don't create files without headers
- ❌ Don't create duplicate implementations
- ❌ Don't skip updating documentation
- ❌ Don't forget LAST MODIFIED field
- ❌ Don't create new patterns without documenting

## ✅ DOs

- ✅ Use templates for consistency
- ✅ Update headers when modifying
- ✅ Document decisions in NOTES.md
- ✅ Follow existing patterns
- ✅ Reference related files

---

**Full Documentation:** See `DOCUMENTATION_STANDARDS_IMPLEMENTATION.md`  
**Last Updated:** 2025-11-02

# Module Development Documentation

**Last Updated:** November 4, 2025  
**Purpose:** Complete guide for developing modules in the AI Agents Platform  
**Status:** Production Ready ✅

---

## 🆕 MAJOR UPDATE: Plug-and-Play Plugin System (Nov 4, 2025)

The module system now supports **auto-discovery and auto-registration of AI tools and Flask routes**!

### What's New?

#### 1. **AI Tool Auto-Discovery** (Module Plugin Loader)
- Drop `schema/` and `implementations/` folders in your module
- Define tool schemas in JSON
- Implement Python wrappers
- **Tools auto-load into Registry V3 - no manual registration!**

#### 2. **Flask Route Auto-Discovery** (Module Blueprint Loader)
- Drop `routes/` folder in your module
- Define Flask blueprints
- **Routes auto-register with Flask - no manual registration!**

#### 3. **Quote Calculator Example**
```
UI/external/modules/quote-calculator/
├── schema/calculator_tools.json      ← 7 AI tool definitions
├── implementations/calculator_wrapper.py  ← Python wrappers
└── routes/calculator_routes.py       ← 11 Flask routes
```

**Result:** 7 AI tools + 11 Flask routes automatically available after restart!

### Documentation for New System

See:
- **New:** `PLUGIN_SYSTEM_GUIDE.md` - Complete plugin system documentation
- **New:** `MODULE_ARCHITECTURE_COMPLETE.md` - Full architecture with diagrams
- **Existing:** All original docs still apply to UI modules

---

## 📚 Documentation Structure

This folder contains all documentation for developing modules in the AI Agents Platform. Files are organized by purpose:

### **🎯 START HERE - Essential Guides**

1. **[Instructions.md](Instructions.md)** - **MAIN GUIDE**
   - Complete technical reference (1,489 lines)
   - Auto-discovery system explained
   - Naming conventions (CRITICAL!)
   - Module structure templates
   - Development workflow
   - Testing and deployment
   - **Read this first!**

2. **[MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md)** - **BEST PRACTICES** ⭐
   - Golden rules for module development
   - Reference implementation: `stock-management`
   - File structure patterns
   - JavaScript/CSS standards
   - Backend integration guide
   - Documentation requirements
   - **Use stock-management as your template!**

### **🆕 Plugin System (NEW - Nov 4, 2025)**

3. **[PLUGIN_SYSTEM_GUIDE.md](PLUGIN_SYSTEM_GUIDE.md)** - **NEW: Plugin Architecture**
   - AI Tool auto-discovery (Module Plugin Loader)
   - Flask route auto-discovery (Module Blueprint Loader)
   - Quote calculator example implementation
   - How to add AI tools to your module
   - How to add Flask routes to your module
   - **Read this to understand the new system!**

4. **Module Plugin System Documentation:**
   - `MODULE_ARCHITECTURE_COMPLETE.md` (in root) - Full system architecture
   - `MODULE_TEST_CHECKLIST.md` (in root) - Testing procedures
   - `test_module_architecture.py` (in root) - Smoke test suite

### **🏗️ Architecture & Design**

5. **[MODULE_ARCHITECTURE_V2.md](MODULE_ARCHITECTURE_V2.md)** - System architecture
   - Module system overview
   - BaseModule class explained
   - Auto-discovery mechanism
   - Module lifecycle
   - Event system

6. **[UNDERSTANDING_AUTO_DISCOVERY.md](UNDERSTANDING_AUTO_DISCOVERY.md)** - Auto-discovery deep dive
   - How modules are discovered
   - manifest.json system
   - Module registration
   - FAQ and troubleshooting

### **📊 Module Assessments**

7. **[STOCK_MANAGEMENT_ASSESSMENT.md](STOCK_MANAGEMENT_ASSESSMENT.md)** - Plugin Integration Analysis
   - Current state of stock-management module
   - Plugin system readiness evaluation
   - Opportunities: AI tools + Flask routes
   - Implementation phases (1-3 days)
   - Migration checklist
   - Recommendations for enhancement

### **🎨 Styling & Design**

5. **[STYLING_GUIDE.md](STYLING_GUIDE.md)** - Visual design standards
   - Color schemes
   - Typography
   - Component patterns
   - Responsive design
   - Accessibility guidelines

### **💾 Database Integration**

6. **[MODULE_DATABASE_GUIDE.md](MODULE_DATABASE_GUIDE.md)** - Database integration
   - When to use module databases
   - SQLite best practices
   - Schema design
   - Data migration
   - Connection patterns

### **🤖 AI Integration**

7. **[SMART_TOOLS_ANALYSIS.md](SMART_TOOLS_ANALYSIS.md)** - AI tool integration
   - How modules call AI agents
   - Tool registry access
   - Credential management
   - Error handling patterns

8. **[AI_prompt.md](AI_prompt.md)** - AI-assisted development
   - Prompts for generating modules
   - Conversion workflows
   - Best practices for AI assistance

---

## 🚀 Quick Start Guide

### For First-Time Module Developers

**Step 1: Read the essentials**
1. Read [Instructions.md](Instructions.md) - sections 1-5 (basics)
2. Review [MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md) - Golden Rules section
3. Study the reference: `UI/external/modules/stock-management/`

**Step 2: Create your module**
1. Choose a module ID (lowercase-with-hyphens)
2. Create folder: `UI/external/modules/your-module-id/`
3. Create `manifest.json` (use template from Instructions.md)
4. Create `your-module-id.js` (use template from MODULE_BEST_PRACTICES.md)
5. Create `your-module-id.css` (optional)

**Step 3: Validate and test**
1. Run: `python scripts/maintenance/validate_modules.py`
2. Fix any errors reported
3. Add module to main manifest: `UI/external/modules/manifest.json`
4. Reload browser and test

**Step 4: Document**
1. Create `README.md` in your module folder
2. Document features and usage
3. Add test files (optional but recommended)

---

## 📖 Documentation Index

### By Topic

**Getting Started:**
- Naming conventions → [Instructions.md](Instructions.md) Section 3
- File structure → [MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md) Section 2
- Quick start → [MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md) Section 12

**Development:**
- JavaScript patterns → [MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md) Section 5
- CSS standards → [MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md) Section 6
- Backend routes → [MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md) Section 7

**Advanced:**
- Database integration → [MODULE_DATABASE_GUIDE.md](MODULE_DATABASE_GUIDE.md)
- AI tools → [SMART_TOOLS_ANALYSIS.md](SMART_TOOLS_ANALYSIS.md)
- Architecture → [MODULE_ARCHITECTURE_V2.md](MODULE_ARCHITECTURE_V2.md)

**Reference:**
- Best practices → [MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md)
- Styling guide → [STYLING_GUIDE.md](STYLING_GUIDE.md)
- Auto-discovery → [UNDERSTANDING_AUTO_DISCOVERY.md](UNDERSTANDING_AUTO_DISCOVERY.md)

---

## 🎯 Module Examples

Study these existing modules to understand patterns:

### **Minimal Module** (Simplest)
- **Location:** `UI/external/modules/salesforce/`
- **Complexity:** Low
- **Use Case:** Basic integration with single responsibility
- **Study For:** Minimal viable module structure

### **Standard Module** (Typical)
- **Location:** `UI/external/modules/database-visualizer/`
- **Complexity:** Medium
- **Use Case:** Feature-rich module with external dependencies
- **Study For:** Tabbed interface, external library integration (Tabulator)

### **Advanced Module** (Reference Implementation) ⭐
- **Location:** `UI/external/modules/stock-management/`
- **Complexity:** High
- **Use Case:** Full-featured module with backend, AI, and comprehensive documentation
- **Study For:** Everything! This is your template.
  - Backend integration (`stock_routes.py`)
  - AI features (invoice processing)
  - Analytics (Chart.js, Plotly)
  - Comprehensive documentation (8+ docs)
  - Test files (3 HTML test pages)
  - Enhanced version pattern

### **Quote Calculator** (Recently Implemented with Plugins!)
- **Location:** `UI/external/modules/quote-calculator/`
- **Complexity:** Medium-High
- **Use Case:** Calculator tools integration with AI tools + Flask routes
- **Study For:** InHouse Print calculator integration, multi-tab forms, **plugin system example**
- **Features:**
  - ✅ 7 AI tools (auto-discovered)
  - ✅ 11 Flask routes (auto-registered)
  - ✅ All features work without manual registration

---

## 🆕 Plugin System: AI Tools & Flask Routes

**NEW (Nov 4, 2025):** Your modules can now provide both **AI tools** and **Flask API routes** with automatic discovery!

### How It Works

Instead of manually registering tools and routes, your module structure does it automatically:

```
your-module/
├── manifest.json
├── your-module.js
├── your-module.css
│
├── schema/                          ← AI Tools (NEW!)
│   └── my_tools.json               (Define what AI can do)
│
├── implementations/                 ← AI Tools (NEW!)
│   ├── __init__.py
│   └── my_wrapper.py               (How AI tools work)
│
└── routes/                          ← Flask Routes (NEW!)
    ├── __init__.py
    └── my_routes.py                (How to call from HTTP)
```

### Key Benefits

| Before | After |
|--------|-------|
| Manually add tools to registry | Drop in schema/ folder ✅ |
| Manually register routes | Drop in routes/ folder ✅ |
| Find scattered code to remove | Delete folder (that's it!) ✅ |
| 2-3 files to update | 1 file to update ✅ |

### Quick Example

**Tell AI to "Calculate business cards quote":**

```
1. User: "Calculate business cards quote"
   ↓
2. AI discovers: calculate_business_cards tool (from quote-calculator/schema/)
   ↓
3. AI calls implementation (from quote-calculator/implementations/)
   ↓
4. Returns quote
```

**Call from HTTP:**

```bash
curl -X POST http://localhost:5001/api/quote-calculator/business-cards \
  -H "Content-Type: application/json" \
  -d '{"quantity":1000,"stock":"satin"}'
```

### Implementation Guide

**See:** `PLUGIN_SYSTEM_GUIDE.md` (this folder)
- Complete tutorial
- Real example: quote-calculator module
- Step-by-step setup
- Troubleshooting guide

### Add Plugins to Your Module

Optional for existing modules! You can:
- Keep your module UI-only (no changes needed)
- OR add `schema/` folder to expose AI tools
- OR add `routes/` folder to expose HTTP endpoints
- OR both!

**No breaking changes** - backward compatible with existing modules.

---

## 🚨 Critical Rules (MUST FOLLOW)

### **The Four Commandments**

1. **Folder Name = Module ID**
   ```
   ✅ CORRECT: quote-calculator/ (manifest id: "quote-calculator")
   ❌ WRONG: calculator-module/ (manifest id: "quote-calculator")
   ```

2. **File Names Match Module ID**
   ```
   ✅ CORRECT: stock-management.js, stock-management.css
   ❌ WRONG: stockManagement.js, stock.css
   ```

3. **Class Name = PascalCase(ID) + "Module"**
   ```javascript
   ✅ CORRECT: class StockManagementModule extends BaseModule {}
   ❌ WRONG: class StockModule extends BaseModule {}
   ```

4. **Extend BaseModule**
   ```javascript
   ✅ CORRECT: class MyModule extends BaseModule {
                 constructor(moduleId) { super(moduleId); }
               }
   ❌ WRONG: class MyModule { constructor() {} }
   ```

**Breaking these rules causes 404 errors and module loading failures!**

---

## 🛠️ Development Tools

### Validation Script
**Location:** `scripts/maintenance/validate_modules.py`

**Usage:**
```bash
cd C:\Users\gpoli\GIT\AI_agents
python scripts/maintenance/validate_modules.py
```

**What it checks:**
- ✅ Folder name matches module ID
- ✅ JavaScript file naming
- ✅ CSS file naming
- ✅ manifest.json validity
- ✅ Module ID format
- ✅ File structure compliance

**Run before every deployment!**

### Module Templates

Templates available in documentation:
- manifest.json template → [Instructions.md](Instructions.md) Section 4
- JavaScript class template → [MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md) Section 5
- CSS template → [MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md) Section 6
- Backend routes template → [MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md) Section 7

---

## 📊 Module System Overview

```
Main manifest.json → Lists all available modules
     ↓
module-loader.js → Discovers and loads enabled modules
     ↓
module-manager.js → Manages module lifecycle
     ↓
BaseModule → Provides common functionality
     ↓
YourModule → Extends BaseModule with specific features
     ↓
User Interface → Module appears in sidebar with icon
```

**Key Concept:** Just add your folder to `UI/external/modules/` and it's automatically discovered!

---

## 🔍 Troubleshooting

### Module Not Appearing
1. Check folder name matches module ID in manifest.json
2. Verify module is enabled in main manifest: `UI/external/modules/manifest.json`
3. Run validation script: `python scripts/maintenance/validate_modules.py`
4. Check browser console for JavaScript errors
5. Hard refresh browser (Ctrl + F5)

### 404 Errors on Module Files
- **Cause:** Folder name doesn't match module ID
- **Fix:** Rename folder to match manifest.json "id" field
- **Prevention:** Run validation script before deployment

### Module Loads But Broken
1. Check JavaScript console for errors
2. Verify class extends BaseModule
3. Ensure constructor calls super(moduleId)
4. Check all async methods use await
5. Verify backend endpoints exist (if used)

### CSS Not Loading
1. Verify CSS file name matches module ID
2. OR ensure CSS is listed in manifest.json dependencies
3. Clear browser cache (Ctrl + F5)
4. Check CSS file path in Network tab

---

## 📝 Documentation Standards

### Required Files in Your Module

**Minimal:**
- `manifest.json` - Module configuration
- `{module-id}.js` - Module code
- `README.md` - Basic documentation

**Recommended:**
- `{module-id}.css` - Module styles
- `IMPLEMENTATION_COMPLETE.md` - Implementation guide
- Test files - Demonstration/testing pages

**Advanced (stock-management pattern):**
- Multiple documentation files
- Integration guides
- Feature summaries
- Usage examples
- Visual dashboards

---

## 🤝 Contributing

### Adding New Documentation

1. Create file in `UI/module_development/`
2. Use clear, descriptive filename
3. Add entry to this README
4. Follow markdown formatting standards
5. Include examples and code snippets

### Updating Existing Docs

1. Update file content
2. Update "Last Updated" date
3. Add changelog entry (if significant)
4. Update this README if structure changes

---

## 📚 Related Documentation

### Platform-Wide Documentation
- `ARCHITECTURE.md` - Complete platform architecture
- `.github/copilot-instructions.md` - Development standards
- `DATABASE_PATH_FIX_COMPLETE.md` - Database configuration
- `MODULE_ASSESSMENT_NOV3_2025.md` - Module quality assessment

### Module-Specific Documentation
- Each module should have its own README.md
- See `UI/external/modules/stock-management/` for examples

---

## 🎓 Learning Path

### Week 1: Fundamentals
- Day 1-2: Read Instructions.md (sections 1-5)
- Day 3-4: Study salesforce module (simple example)
- Day 5: Create your first simple module

### Week 2: Intermediate
- Day 1-2: Read MODULE_BEST_PRACTICES.md completely
- Day 3-4: Study database-visualizer module
- Day 5: Add backend routes to your module

### Week 3: Advanced
- Day 1-2: Study stock-management module (reference implementation)
- Day 3-4: Add AI integration, analytics, or advanced features
- Day 5: Create comprehensive documentation

### Ongoing
- Review SMART_TOOLS_ANALYSIS.md for AI integration
- Study STYLING_GUIDE.md for visual consistency
- Keep modules validated and documented

---

## 📞 Getting Help

### Before Asking for Help

1. **Read the docs:**
   - Instructions.md for technical details
   - MODULE_BEST_PRACTICES.md for patterns
   - Existing modules for examples

2. **Run validation:**
   ```bash
   python scripts/maintenance/validate_modules.py
   ```

3. **Check browser console:**
   - F12 → Console tab
   - Look for red errors

4. **Verify backend:**
   - Is Flask running? (`BISTART`)
   - Are endpoints responding?

### Common Issues - Already Solved

- **Folder name mismatch** → Rename folder to match module ID
- **undefined tab names** → Use "name" not "label" in manifest.json tabs
- **Module not loading** → Check enabled flag in main manifest.json
- **CSS not working** → Name file {module-id}.css OR list in manifest dependencies

---

## 🎉 Success Criteria

Your module is production-ready when:

- [ ] Validation script shows: ✅ {module-name}: VALID
- [ ] Module appears in sidebar with correct icon
- [ ] All tabs render without errors
- [ ] Backend endpoints respond (if applicable)
- [ ] No console errors in browser
- [ ] README.md documents all features
- [ ] Test files demonstrate functionality
- [ ] Follows naming conventions perfectly

---

## 📅 Changelog

### November 4, 2025 - Plugin System Documentation Complete 🆕
- Created `PLUGIN_SYSTEM_GUIDE.md` (1,000+ lines, comprehensive plugin tutorial)
  - AI Tool auto-discovery (Module Plugin Loader)
  - Flask route auto-discovery (Module Blueprint Loader)
  - Step-by-step implementation guide
  - Complete examples (quote-calculator)
  - Troubleshooting and best practices
  
- Created `STOCK_MANAGEMENT_ASSESSMENT.md` (400+ lines, module analysis)
  - Evaluated stock-management module for plugin compatibility
  - Identified 5+ AI tool opportunities
  - Identified 6+ Flask route opportunities
  - Provided 3-phase implementation plan (1-4 days total)
  - Created migration checklist
  
- Updated `README.md` (this file)
  - Added plugin system overview section
  - Highlighted quote-calculator as working example
  - Added plugin system benefits table
  - Reorganized documentation structure
  
**Impact:** Developers can now add AI tools and Flask routes to modules without manual registration!

### November 3, 2025 - Major Documentation Overhaul
- Created this comprehensive README
- Added MODULE_BEST_PRACTICES.md (reference: stock-management)
- Enhanced validation script with smart CSS detection
- Cleaned up outdated documentation (deleted 6 obsolete files)
- Added database-visualizer README
- Consolidated module development guidance

### October 30, 2025 - Module System Established
- Created Instructions.md (1,489 lines)
- Established auto-discovery system
- Documented naming conventions
- Created module templates

---

**Remember:** When in doubt, follow the `stock-management` module pattern. It's the gold standard! ⭐

**Questions?** Check the relevant documentation file first, then review existing modules for examples.

**Ready to build?** Start with [MODULE_BEST_PRACTICES.md](MODULE_BEST_PRACTICES.md) Section 12: "Quick Start: New Module in 10 Minutes"

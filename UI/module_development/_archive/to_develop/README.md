# To Develop Folder

**Purpose:** Place your existing HTML/JavaScript/CSS code here for conversion to module format

---

## What Goes Here?

Place any existing code you want to convert into a module:

- HTML dashboard files
- JavaScript applications
- React/Vue components (will be converted to vanilla JS)
- CSS stylesheets
- Complete web applications
- Platform integrations (Salesforce, HubSpot, etc.)

---

## Conversion Workflow

### Step 1: Add Your Files

```
to_develop/
├── my-dashboard.html        ← Your existing HTML
├── my-dashboard.js          ← Your existing JavaScript
├── my-dashboard.css         ← Your existing CSS
└── README.md               ← This file
```

### Step 2: Analyze Structure

Open your files and identify:
- **Main sections** → Will become sub-tabs
- **Data sources** → Will become API methods
- **UI components** → Will use BaseModule utilities
- **Event handlers** → Will become module methods

### Step 3: Use AI Conversion

1. Open `../AI_prompt.md`
2. Copy the entire AI prompt
3. Paste into your AI assistant (ChatGPT, Claude, etc.)
4. Provide your code from this folder
5. Receive converted module files

### Step 4: Create Module

1. Create folder: `UI/external/modules/[module-id]/`
2. Add generated files:
   - `manifest.json`
   - `[module-id].js`
   - `[module-id].css` (optional)
3. Update main manifest: `UI/external/modules/manifest.json`
4. Test in browser

---

## Example Structure

**Before (in this folder):**
```
to_develop/
└── sales-dashboard/
    ├── index.html
    ├── script.js
    ├── styles.css
    └── api.js
```

**After (converted module):**
```
UI/external/modules/sales-dashboard/
├── manifest.json
├── sales-dashboard.js
└── sales-dashboard.css (optional)
```

---

## Tips for Conversion

### Make Conversion Easier

- **Organize your code** - Separate HTML, JS, CSS clearly
- **Comment your code** - Explain what each section does
- **Document APIs** - List all endpoints used
- **List dependencies** - Note any libraries required (Chart.js, etc.)

### Common Patterns

**If your code has:**
- Multiple pages → Create multiple sub-tabs
- Data tables → Use `.data-table` class in module
- Charts → Keep chart libraries, integrate in module
- Forms → Convert to module methods
- API calls → Move to async methods in module

---

## Resources

**In parent folder:**
- `Instructions.md` - Complete technical guide
- `AI_prompt.md` - AI conversion prompt (copy this to AI!)
- `MODULE_DATABASE_GUIDE.md` - **When & how to create module .db files**
- `STYLING_GUIDE.md` - Design system and color standards
- `MODULE_ARCHITECTURE_V2.md` - AI-integrated architecture
- `SMART_TOOLS_ANALYSIS.md` - Tool system patterns

**Examples:**
- `UI/external/modules/salesforce/` - Working example module

**Documentation:**
- `UI/IMPLEMENTATION_COMPLETE.md` - Implementation details
- `UI/QUICK_START_TEST.md` - Testing guide

---

## Checklist for Files in This Folder

Before converting, ensure your code has:

- [ ] Clear structure (HTML/JS/CSS separated or clearly identified)
- [ ] Comments explaining functionality
- [ ] API endpoints documented (if any)
- [ ] Libraries/dependencies listed (if any)
- [ ] Event handlers identified
- [ ] Data sources identified
- [ ] UI sections identified
- [ ] **Database needs assessed** (see MODULE_DATABASE_GUIDE.md if complex data)

---

## Database Considerations

**Does your module need its own database?**

**Create module .db if:**
- Module manages complex entities (10+ tables)
- Large data volumes (thousands of records)
- Data should be deletable with module
- Module needs portability/export features

** Use shared database or APIs if:**
- Module displays external API data
- Simple configuration (<5 fields)
- Data shared across modules
- Lightweight lookup tables

**📖 See:** `../MODULE_DATABASE_GUIDE.md` for complete instructions

---

## Quick Start

**To convert your code:**

1. **Add files here** (this folder)
2. **Assess database needs** (see MODULE_DATABASE_GUIDE.md)
3. **Open** `../AI_prompt.md`
4. **Copy** entire prompt
5. **Paste** to AI assistant
6. **Provide** your code files
7. **Receive** converted module
8. **Create** module folder in `UI/external/modules/`
9. **Test** in browser

**That's it!**

---

## Need Help?

**Common Questions:**

**Q: My code is messy, can it still be converted?**  
A: Yes! The AI prompt helps organize messy code. Just provide what you have.

**Q: My code uses React/Vue, will it work?**  
A: The AI will convert it to vanilla JavaScript that works with the module system.

**Q: I have multiple dashboards to convert**  
A: Create a subfolder for each dashboard in this folder, then convert one at a time.

**Q: What if my code has complex dependencies?**  
A: List them in the manifest.json `dependencies` array. Most libraries work fine.

**Q: Should my module have its own database?**  
A: Read `../MODULE_DATABASE_GUIDE.md` to decide. Most modules DON'T need one.

**Q: What happens to module data when I uninstall?**  
A: If module has its own .db, data is deleted with module (after backup). If using shared database, data persists unless explicitly cleaned up.

---

**Ready to convert?** Add your files and follow the steps above!


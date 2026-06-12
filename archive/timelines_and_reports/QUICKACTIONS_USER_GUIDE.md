# QuickActions User Guide
**How to Create, Modify, Delete, and Use Quick Actions**

**Created**: December 6, 2025  
**For**: MustCare ValorAI Platform & Chrome Extension Users

---

## 🎯 Overview

Quick Actions provide instant access to AI-powered veterinary protocols, emergency procedures, consultation tools, and clinical guidance. You can use the pre-built system defaults OR create your own custom actions tailored to your practice.

### **Two Ways to Access Quick Actions**

1. **Chrome Extension (V7_MustCare)** - Sidebar menu for quick access during consultations
2. **Backend Platform (ValorAI)** - Full management interface for administrators

---

## 📱 Using Quick Actions (Chrome Extension)

### **Step 1: Open Quick Actions Menu**

**Location**: In the Chrome extension sidebar

1. Look for the **⚡ Quick Assist** button in the action container (usually bottom-right of sidebar)
2. Click the button to open the main menu

```
┌────────────────────────┐
│  ⚡ Quick Assist       │ ← Click here
└────────────────────────┘
```

---

### **Step 2: Navigate Categories**

When you click Quick Assist, you'll see a menu of categories:

```
┌─────────────────────────────┐
│ 💊 Medications              │
│ 🚨 Emergency Protocols      │
│ 📋 Consultation Analysis    │
│ 💬 Client Communication     │
│ 🔬 Clinical Procedures      │
│ 📊 Data Analysis            │
└─────────────────────────────┘
```

**Categories include**:
- **Medications** (3 actions) - Dosing, interactions, calculations
- **Emergency Protocols** (14 actions) - CPR, GDV, trauma, toxicity
- **Consultation Analysis** (5 actions) - SOAP notes, summaries, billing
- **Client Communication** (3 actions) - Difficult conversations, cost discussions
- **Clinical Procedures** (3 actions) - Surgical prep, imaging, blood work
- **Data Analysis** (11 actions) - Dashboards, trends, forecasting
- **Marketing Analytics** (4 actions) - Campaign analysis, segmentation
- **Business Financials** (3+ actions) - Financial dashboards

---

### **Step 3: Select an Action**

1. **Hover or click** on a category (e.g., "💊 Medications")
2. A **flyout menu** appears to the right showing actions:

```
┌────────────────────┐  ┌──────────────────────────┐
│ 💊 Medications  →  │  │ 📋 Create Dosage Table  │
└────────────────────┘  │ ⚠️ Drug Interactions    │
                        │ 🧮 Dosage Calculator     │
                        └──────────────────────────┘
                              ↑ Click one
```

3. Click the action you want
4. The AI will respond with guidance!

---

### **What Happens When You Select an Action?**

The system injects a **three-part message** to the AI:

**1. User Message (Visible)** - Friendly explanation
```
I'll help you create a dosage table for common veterinary medications.

To provide the most accurate table, please let me know:
- Drug name - Which medication do you need?
- Species - Dog, cat, horse, exotic?
- Weight range - What size patients?
- Condition - What are you treating?
```

**2. System Context (Hidden)** - AI understands your intent
```
"The user has selected Quick Action assistance for creating a medication dosage table."
```

**3. User Priming (Hidden)** - Instructions for AI response quality
```
"Create a detailed, accurate veterinary medication dosage table. 
Focus on safety, precision, and clear administration instructions. 
Include weight-based calculations and any relevant contraindications."
```

**Then**: You provide additional details, and the AI responds with expert guidance!

---

## 🛠️ Managing Custom Quick Actions (Chrome Extension)

### **Opening the Management Interface**

**Option 1**: Via browser console (developer access)
```javascript
quickActionsUI.showManagementModal()
```

**Option 2**: Custom button (if added to your UI)
```html
<button onclick="quickActionsUI.showManagementModal()">
  Manage Quick Actions
</button>
```

---

### **Management Modal Layout**

```
┌──────────────────────────────────────────────────────────────┐
│ 🔩 Manage Quick Actions                               [X]   │
├───────────────┬──────────────────────────────────────────────┤
│               │ [🔍 Search] [+ Create] [⭐ Favorites]        │
│ Categories    ├──────────────────────────────────────────────┤
│               │                                              │
│ 💊 Medications│  ┌──────────────────────────────────────┐   │
│    (5)        │  │ 📋 Create Dosage Table               │   │
│               │  │ [👁️ View] [✏️ Edit] [🗑️ Delete]    │   │
│ 🚨 Emergency  │  │ Custom • ⭐                          │   │
│    (12)       │  └──────────────────────────────────────┘   │
│               │                                              │
│ 📋 Consultation  ┌──────────────────────────────────────┐   │
│    (6)        │  │ ⚠️ Drug Interactions                 │   │
│               │  │ [👁️ View]                            │   │
│ + Add Category│  │ System                               │   │
│               │  └──────────────────────────────────────┘   │
└───────────────┴──────────────────────────────────────────────┘
```

**Features**:
- **Search bar** - Find actions by name/description
- **Category sidebar** - Browse by category (shows action count)
- **Action cards** - Visual distinction between System and Custom
- **Favorites** - Star icon to mark frequently used actions
- **CRUD buttons** - View, Edit, Delete (for custom actions only)

---

## ➕ Creating a New Quick Action

### **Step 1: Click "Create Custom Action"**

In the management modal, click the **[+ Create]** button

---

### **Step 2: Fill in the Form**

A form appears with the following fields:

#### **1. Category** (Required)
Select which category this action belongs to
```
[Dropdown: Medications, Emergency, Consultation Analysis, etc.]
```

---

#### **2. Action Name** (Required)
Give your action a clear, descriptive name
```
Example: "Calculate Metronidazole Dose"
```

---

#### **3. Icon** (Optional)
Font Awesome icon class
```
Default: fa-solid fa-star
Examples:
- fa-solid fa-pills (medication)
- fa-solid fa-syringe (injection)
- fa-solid fa-calculator (calculation)
- fa-solid fa-notes-medical (notes)
```

Browse icons: https://fontawesome.com/icons

---

#### **4. Description** (Optional)
Brief description (shown in action card)
```
Example: "Quick metronidazole dosing based on patient weight"
```

---

#### **5. UI Message** (Required) ⭐
**This is what the USER sees** when they select your action

**Guidelines**:
- ✅ Friendly, conversational tone
- ✅ Explain what you'll help with
- ✅ Ask for required information
- ✅ Use bullet points or numbered lists
- ✅ Be clear about what details you need

**Example**:
```markdown
I'll help you calculate the correct metronidazole dosage for your patient.

Please provide:
- **Patient weight** - In kg or lbs?
- **Species** - Dog, cat, etc.?
- **Indication** - Giardia, bacterial infection, inflammatory bowel disease?
- **Route** - Oral or IV?

I'll calculate the precise dose and provide administration guidance.
```

---

#### **6. System Context** (Optional)
**Hidden from user** - Tells the AI what the user selected

**Guidelines**:
- ✅ Short, factual statement
- ✅ Describes user's intent
- ❌ Not shown in chat

**Example**:
```
The user has selected Quick Action assistance for metronidazole dosage calculation.
```

---

#### **7. User Info Priming** (Optional)
**Hidden from user** - Instructs the AI on HOW to respond

**Guidelines**:
- ✅ Define quality standards
- ✅ Specify format or structure
- ✅ Include domain-specific requirements
- ✅ Provide safety considerations
- ❌ Not shown in chat

**Example**:
```
Provide the assistance and perform the task:

"Calculate metronidazole dosage using current veterinary standards. 
Include weight-based calculations, dosing frequency, duration, 
and any contraindications or side effects. Ensure dosing is safe 
and appropriate for the specific indication."

Use the additional information the user provided below:
```

---

### **Step 3: Save Your Action**

Click **[Create Action]** button

**What happens**:
1. ✅ Action saved to database (via API)
2. ✅ Available immediately in your Quick Actions menu
3. ✅ Synced across all your devices
4. ✅ Cached locally for offline access

**Success message**: "Custom action created successfully! ✅"

---

## ✏️ Editing a Custom Quick Action

### **Prerequisites**
- ✅ Can only edit **custom actions** (not system defaults)
- ✅ Must have permission (creator or admin)

### **Steps**:

1. **Open management modal** (`quickActionsUI.showManagementModal()`)
2. **Find your custom action** (marked with "Custom" badge)
3. **Click [✏️ Edit]** button
4. **Update form fields** (same fields as create)
5. **Click [Save Changes]**

**What happens**:
- ✅ Action updated in database
- ✅ Changes sync immediately
- ✅ Cache refreshed

**Note**: System default actions (marked "System") cannot be edited - they're read-only.

---

## 🗑️ Deleting a Custom Quick Action

### **Prerequisites**
- ✅ Can only delete **custom actions** (not system defaults)
- ✅ Must have permission (creator or admin)

### **Steps**:

1. **Open management modal**
2. **Find your custom action**
3. **Click [🗑️ Delete]** button
4. **Confirm deletion** in popup

```
┌─────────────────────────────────────┐
│ Delete "Calculate Metronidazole"?  │
│                                     │
│ This action will be permanently     │
│ removed.                            │
│                                     │
│     [Cancel]  [Delete]              │
└─────────────────────────────────────┘
```

**What happens**:
- ✅ Action removed from database
- ✅ Removed from your Quick Actions menu
- ✅ Removed from all users (if organization-wide)
- ❌ **Cannot be undone**

---

## ⭐ Favorites System

### **Why Use Favorites?**
- ✅ Quick access to frequently used actions
- ✅ Personal to each user
- ✅ View all favorites in one place

### **Adding to Favorites**

**Option 1**: In the menu
```
While browsing actions, click the ⭐ star icon next to any action
```

**Option 2**: In management modal
```
Click the star icon on any action card
```

**Visual feedback**:
- ⭐ **Gold star** = Favorited
- ☆ **Gray star** = Not favorited

---

### **Viewing Favorites**

**In management modal**:
1. Click **[⭐ Favorites]** button in toolbar
2. See all your favorited actions in one view
3. Organized by category

**In Quick Actions menu**:
- Favorited actions stay in their categories
- Look for the ⭐ icon next to action names (if displayed)

---

## 🔍 Searching Quick Actions

### **In Management Modal**

Use the **search bar** at the top:

```
┌────────────────────────────────────┐
│ 🔍 Search actions...               │
└────────────────────────────────────┘
```

**Search features**:
- ✅ Searches **action names**
- ✅ Searches **descriptions**
- ✅ Instant results as you type
- ✅ Shows category label for each result

**Example**: Type "dosage" → See all dosing-related actions

---

## 🌐 Online vs. Offline Behavior

### **Online (Connected to API)**
✅ System defaults available  
✅ Custom actions sync from server  
✅ Create/edit/delete custom actions  
✅ Usage tracking & analytics  
✅ Favorites sync across devices  

### **Offline (No Internet)**
✅ System defaults still work  
✅ Previously synced custom actions available (from cache)  
⚠️ Cannot create/edit/delete custom actions  
⚠️ Favorites changes saved locally (sync when back online)  
⚠️ No usage tracking  

**Graceful Degradation**:
- ❌ **No error messages** if API unavailable
- ✅ **Silent fallback** to cached data
- ✅ **Auto-retry** when connection restored
- ✅ **Seamless experience** - user may not notice

---

## 🔐 Permissions & Access Control

### **User Roles**

| Role | View Actions | Use Actions | Create Custom | Edit Own | Edit Any | Delete Own | Delete Any | Analytics |
|------|--------------|-------------|---------------|----------|----------|------------|------------|-----------|
| **Default User** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Manager** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### **Action Visibility**

**System Defaults**: Visible to everyone, cannot be edited/deleted  
**Organization-Wide**: Visible to all users in organization  
**Private**: Only visible to creator + admins  
**Favorites**: Personal to each user

---

## 💡 Best Practices

### **Creating Effective Quick Actions**

#### **1. Clear, Descriptive Names**
```
✅ Good: "Calculate Metronidazole Dose"
❌ Bad: "Metronidazole" or "Calculate Dose"
```

#### **2. Comprehensive UI Messages**
```
✅ Good: Ask for ALL required information upfront
   - Species, weight, indication, route, patient history

❌ Bad: Vague messages that require back-and-forth
   - "Tell me about your patient"
```

#### **3. Specific System Context**
```
✅ Good: "User selected metronidazole dosage calculator for GI indication"
❌ Bad: "User wants help" (too vague)
```

#### **4. Detailed User Priming**
```
✅ Good: Specify format, safety requirements, calculation standards
❌ Bad: Generic "help the user" instructions
```

#### **5. Appropriate Categories**
- Put actions in logical categories
- Don't create duplicate categories
- Use existing categories when possible

---

### **Organizing Your Actions**

**Use Categories Effectively**:
```
Medications/
├── Dosage calculations
├── Drug interactions
└── Administration protocols

Emergency/
├── Triage protocols
├── Life-saving procedures
└── Critical care guidelines

Consultation/
├── SOAP note generation
├── Billing extraction
└── Discharge instructions
```

**Favorite Frequently Used Actions**:
- ⭐ Emergency protocols you use daily
- ⭐ Common medication calculations
- ⭐ Routine consultation templates

---

## 🔧 Troubleshooting

### **Problem: Quick Actions menu doesn't open**

**Check**:
1. ✅ Is the Quick Assist button visible?
2. ✅ Are you logged in to the extension?
3. ✅ Check browser console for errors

**Solution**:
```javascript
// In browser console:
console.log(window.quickActionsDisplay);
console.log(window.quickActionsManager);

// Manual trigger:
quickActionsDisplay.initialize();
```

---

### **Problem: Custom actions not appearing**

**Check**:
1. ✅ Are you online?
2. ✅ Did the action save successfully?
3. ✅ Try manual sync:

```javascript
// Force sync with API
await quickActionsManager.forceSync();
```

---

### **Problem: "Cannot create custom actions while offline"**

**Explanation**: Custom actions require API access to save to database

**Solutions**:
1. ✅ Connect to internet
2. ✅ Wait for auto-reconnect
3. ✅ Use system defaults while offline (still available)

---

### **Problem: Changes not syncing across devices**

**Check**:
1. ✅ Are you logged in with same account on both devices?
2. ✅ Is internet connection stable?
3. ✅ Wait 5 minutes (auto-sync interval)
4. ✅ Force refresh:

```javascript
await quickActionsManager.forceSync();
```

---

### **Problem: "Can only edit/delete custom actions"**

**Explanation**: System default actions are read-only for consistency

**Solutions**:
1. ✅ Create a **copy** of the system action as a custom action
2. ✅ Modify the custom copy as needed
3. ✅ System defaults remain unchanged for all users

---

## 📊 Usage Analytics (Admin/Manager Only)

### **Viewing Analytics**

**Via API**:
```javascript
const analytics = await quickActionsAPI.getAnalytics();
console.log(analytics);
```

**Data Includes**:
- Total categories & actions
- System vs. custom action counts
- Active user count
- Total usage events
- Top 10 most-used actions
- Usage by category
- Usage trends over time

---

## 🚀 Advanced Features

### **Programmatic Access**

**Get all actions**:
```javascript
const actions = quickActionsManager.getActions();
console.log(actions);
```

**Get specific action**:
```javascript
const action = quickActionsManager.getAction('medications', 'dosage_table');
console.log(action);
```

**Check if action is custom**:
```javascript
const isCustom = quickActionsManager.isCustomAction('medications', 'my_custom_action');
```

**Get favorites**:
```javascript
const favorites = quickActionsManager.getFavorites();
console.log(favorites);
```

**Manual sync**:
```javascript
await quickActionsManager.forceSync();
```

**Check sync status**:
```javascript
const status = quickActionsManager.getSyncStatus();
console.log(status);
// { isOnline: true, lastSync: 1733443200000, hasCache: true, actionCount: 52 }
```

---

## 🎓 Quick Reference

### **Common Tasks**

| Task | Action |
|------|--------|
| Use a quick action | Click ⚡ button → Select category → Click action |
| Create custom action | Open management modal → [+ Create] → Fill form → Save |
| Edit custom action | Management modal → Find action → [Edit] → Update → Save |
| Delete custom action | Management modal → Find action → [Delete] → Confirm |
| Add to favorites | Click ⭐ star icon next to action |
| View favorites | Management modal → [Favorites] button |
| Search actions | Management modal → Type in search bar |
| Force sync | Console: `await quickActionsManager.forceSync()` |

---

### **Keyboard Shortcuts** (If Implemented)

```
Ctrl+Q         Open Quick Actions menu
Ctrl+Shift+Q   Open Management Modal
/search        Focus search bar (in management modal)
Esc            Close menu/modal
```

---

## 📝 Example: Creating a Custom Action

### **Scenario**: Create a "CBC Interpretation" action

**Steps**:

1. **Open management modal**
2. **Click [+ Create Custom Action]**
3. **Fill in form**:

```
Category: Clinical Procedures

Name: CBC Interpretation Guide

Icon: fa-solid fa-microscope

Description: Interpret complete blood count results with clinical significance

UI Message:
I'll help you interpret CBC (Complete Blood Count) results.

Please provide:
- **CBC values** - Paste the lab results or key abnormal values
- **Patient details** - Species, age, breed, sex
- **Clinical signs** - What symptoms is the patient showing?
- **History** - Chronic conditions, medications, recent procedures?

I'll explain the clinical significance of abnormal values and provide differential diagnoses.

System Context:
The user has selected Quick Action assistance for interpreting complete blood count (CBC) results.

User Info Priming:
Provide the assistance and perform the task:

"Interpret CBC results with clinical correlation. Explain the significance of abnormal values (high/low RBC, WBC, platelets, etc.). Provide differential diagnoses based on the pattern of abnormalities. Consider patient signalment and clinical presentation. Use veterinary clinical pathology standards."

Use the additional information the user provided below:
```

4. **Click [Create Action]**
5. **Success!** ✅ Your action is now available

**Result**: 
- Find under "Clinical Procedures" → "CBC Interpretation Guide"
- Available immediately across all devices
- Share with team if organization-wide

---

## 🌟 Pro Tips

### **Tip 1: Template Your Messages**
Create a consistent format for similar actions:
```markdown
I'll help you [ACTION VERB] [TASK].

Please provide:
- **Field 1** - Description
- **Field 2** - Description
- **Field 3** - Description

I'll [OUTCOME].
```

### **Tip 2: Use Markdown Formatting**
Make UI messages more readable:
- `**Bold**` for emphasis
- `- Bullets` for lists
- `## Headers` for sections
- `[Link text](url)` for references

### **Tip 3: Leverage System Context**
Use system context to prime the AI about:
- Emergency urgency level
- Required accuracy (dosing vs. general info)
- Expected output format (table, list, paragraph)

### **Tip 4: Create Action Families**
Group related actions together:
```
Metronidazole Suite:
├── Calculate Dose
├── Drug Interactions
├── Administration Guide
└── Side Effects Monitor
```

### **Tip 5: Test Before Sharing**
1. Create action as **private** first
2. Test with real cases
3. Refine based on AI responses
4. Mark as **organization-wide** when ready

---

## 🆘 Support & Resources

### **Need Help?**

**Developer Console Access**:
```javascript
// Check system status
quickActionsManager.getSyncStatus()

// View all actions
quickActionsManager.getActions()

// Force sync
await quickActionsManager.forceSync()

// Open management UI
quickActionsUI.showManagementModal()
```

**Documentation**:
- Architecture Guide: `QUICKACTIONS_ARCHITECTURE_ANALYSIS.md`
- API Reference: Backend server `/api/v1/quick-actions`
- Code Location: `V7_MustCare/js/messaging/quickActions*.js`

---

## 📅 Version History

**Version 2.0** (Current)
- ✅ Database-driven custom actions
- ✅ Multi-user support with roles
- ✅ Favorites system
- ✅ Usage analytics
- ✅ Offline caching
- ✅ Organization-wide sharing

**Version 1.0** (Legacy)
- Hardcoded actions only
- No customization
- No database integration

---

**Document Version**: 1.0  
**Last Updated**: December 6, 2025  
**For**: MustCare Veterinary AI Platform Users


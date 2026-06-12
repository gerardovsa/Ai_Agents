# QuickActions Visual Workflows

**Visual guides for creating, editing, and using Quick Actions**

---

## 🎯 Quick Action Selection Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER WORKFLOW                             │
└─────────────────────────────────────────────────────────────┘

1️⃣ User opens extension sidebar
   │
   ├─→ [⚡ Quick Assist] button visible
   │
2️⃣ User clicks Quick Assist button
   │
   ├─→ Main menu opens (8 categories)
   │
   │   ┌───────────────────────┐
   │   │ 💊 Medications        │
   │   │ 🚨 Emergency          │
   │   │ 📋 Consultation       │
   │   │ 💬 Communication      │
   │   │ 🔬 Procedures         │
   │   │ 📊 Data Analysis      │
   │   │ 📈 Marketing          │
   │   │ 💰 Financial          │
   │   └───────────────────────┘
   │
3️⃣ User hovers/clicks category (e.g., Medications)
   │
   ├─→ Flyout menu appears to the right
   │
   │   ┌────────────┐  ┌──────────────────────┐
   │   │ Medications│─→│ 📋 Dosage Table      │
   │   └────────────┘  │ ⚠️ Interactions      │
   │                   │ 🧮 Calculator        │
   │                   └──────────────────────┘
   │
4️⃣ User clicks action (e.g., "Dosage Table")
   │
   ├─→ Menus close automatically
   │
   ├─→ AI message injected (3 parts):
   │   ├─ User Message (visible): "I'll help you create..."
   │   ├─ System Context (hidden): "User selected dosage table"
   │   └─ User Priming (hidden): "Create accurate table..."
   │
5️⃣ AI responds with guidance
   │
   ├─→ User provides details (drug, species, weight)
   │
6️⃣ AI generates complete response
   │
   └─→ ✅ Task complete!
```

---

## ➕ Creating Custom Action Flow

```
┌─────────────────────────────────────────────────────────────┐
│              CREATE CUSTOM ACTION WORKFLOW                   │
└─────────────────────────────────────────────────────────────┘

1️⃣ Open Management Modal
   │
   ├─→ Console: quickActionsUI.showManagementModal()
   │   OR
   └─→ Click [Manage Quick Actions] button (if in UI)
   │
   │   ┌──────────────────────────────────────┐
   │   │ 🔩 Manage Quick Actions       [X]   │
   │   ├──────────────────────────────────────┤
   │   │ [Search] [+ Create] [Favorites]      │
   │   └──────────────────────────────────────┘
   │
2️⃣ Click [+ Create Custom Action]
   │
   ├─→ Create form appears
   │
   │   ┌──────────────────────────────────────┐
   │   │ Create Custom Quick Action           │
   │   ├──────────────────────────────────────┤
   │   │ Category: [Dropdown ▼]               │
   │   │ Name: [__________________]           │
   │   │ Icon: [fa-solid fa-star__]          │
   │   │ Description: [___________]           │
   │   │ UI Message: [____________]           │
   │   │              (What user sees)        │
   │   │ System Context: [________]           │
   │   │                  (Hidden)            │
   │   │ User Priming: [__________]           │
   │   │                (AI instructions)     │
   │   ├──────────────────────────────────────┤
   │   │      [Cancel]  [Create Action]       │
   │   └──────────────────────────────────────┘
   │
3️⃣ User fills in fields
   │
   ├─→ Category: "Clinical Procedures"
   ├─→ Name: "CBC Interpretation Guide"
   ├─→ Icon: "fa-solid fa-microscope"
   ├─→ Description: "Interpret CBC results..."
   ├─→ UI Message: "I'll help you interpret CBC..."
   ├─→ System Context: "User selected CBC interpretation"
   └─→ User Priming: "Interpret CBC with clinical correlation..."
   │
4️⃣ User clicks [Create Action]
   │
   ├─→ FRONTEND (quickActionsUI.js)
   │   └─→ handleCreateAction()
   │       └─→ Calls: quickActionsManager.createCustomAction()
   │
   ├─→ MANAGER (quickActionsManager.js)
   │   └─→ createCustomAction()
   │       ├─ Checks: isOnline? ✅
   │       ├─ Finds: categoryId from API
   │       └─→ Calls: quickActionsAPI.createQuickAction()
   │
   ├─→ API CLIENT (quickActionsAPI.js)
   │   └─→ createQuickAction()
   │       ├─ POST /api/v1/quick-actions
   │       ├─ Headers: Authorization: Bearer <JWT>
   │       └─ Body: { categoryId, name, icon, uiMessage, ... }
   │
   ├─→ BACKEND (Express.js)
   │   └─→ POST /quick-actions endpoint
   │       ├─ Validates: User authenticated? ✅
   │       ├─ Validates: Form data valid? ✅
   │       └─→ Calls: QuickActions.createQuickAction()
   │
   ├─→ DATABASE (PostgreSQL)
   │   └─→ INSERT INTO quick_actions
   │       ├─ Generates: slug from name
   │       ├─ Sets: createdBy = user.id
   │       ├─ Sets: isSystemDefault = false
   │       └─ Returns: new action with ID
   │
   ├─→ RESPONSE BACK TO FRONTEND
   │   └─→ { success: true, quickAction: {...} }
   │
   ├─→ MANAGER SYNCS
   │   └─→ quickActionsManager.syncWithAPI()
   │       ├─ Fetches: Updated actions from API
   │       ├─ Merges: System + API actions
   │       └─ Saves: To LocalStorage
   │
   ├─→ UI REFRESHES
   │   └─→ quickActionsUI.loadCategories()
   │       └─→ Shows updated action list
   │
5️⃣ Success notification
   │
   └─→ ✅ "Custom action created successfully!"
   │
6️⃣ Action available immediately
   │
   ├─→ In Quick Actions menu
   ├─→ Marked with "Custom" badge
   ├─→ Synced across all devices
   └─→ Cached for offline use
```

---

## ✏️ Edit Custom Action Flow

```
┌─────────────────────────────────────────────────────────────┐
│              EDIT CUSTOM ACTION WORKFLOW                     │
└─────────────────────────────────────────────────────────────┘

1️⃣ Open Management Modal
   │
2️⃣ Navigate to custom action
   │
   ├─→ Browse category OR
   ├─→ Search by name OR
   └─→ View favorites
   │
3️⃣ Find action card (marked "Custom")
   │
   │   ┌──────────────────────────────────┐
   │   │ 🔬 CBC Interpretation            │
   │   │ [👁️ View] [✏️ Edit] [🗑️ Del]│
   │   │ Custom • ⭐                      │
   │   └──────────────────────────────────┘
   │
4️⃣ Click [✏️ Edit] button
   │
   ├─→ Check: Is this a custom action? ✅
   ├─→ Check: Do I have permission? ✅
   │   (Owner OR Admin)
   │
5️⃣ Edit form opens (pre-filled)
   │
   │   ┌──────────────────────────────────────┐
   │   │ Edit Custom Quick Action             │
   │   ├──────────────────────────────────────┤
   │   │ Category: [Clinical Procedures ▼]    │
   │   │ Name: [CBC Interpretation Guide_]   │
   │   │ Icon: [fa-solid fa-microscope___]   │
   │   │ ... (all fields pre-filled)          │
   │   ├──────────────────────────────────────┤
   │   │      [Cancel]  [Save Changes]        │
   │   └──────────────────────────────────────┘
   │
6️⃣ User modifies fields
   │
   ├─→ Updates: UI Message with more clarity
   ├─→ Adds: Additional priming instructions
   └─→ Changes: Icon to better representation
   │
7️⃣ User clicks [Save Changes]
   │
   ├─→ FRONTEND → MANAGER → API → BACKEND
   │   └─→ PUT /api/v1/quick-actions/:id
   │       ├─ Validates: User owns action OR is admin
   │       ├─ Validates: Cannot edit system defaults
   │       └─ Updates: Database record
   │
   ├─→ RESPONSE → SYNC → UI REFRESH
   │
8️⃣ Success notification
   │
   └─→ ✅ "Action updated successfully!"
```

---

## 🗑️ Delete Custom Action Flow

```
┌─────────────────────────────────────────────────────────────┐
│              DELETE CUSTOM ACTION WORKFLOW                   │
└─────────────────────────────────────────────────────────────┘

1️⃣ Navigate to custom action in management modal
   │
2️⃣ Click [🗑️ Delete] button
   │
   ├─→ Check: Is this a custom action? ✅
   ├─→ Check: Do I have permission? ✅
   │
3️⃣ Confirmation dialog appears
   │
   │   ┌─────────────────────────────────────┐
   │   │ Delete "CBC Interpretation Guide"?  │
   │   │                                     │
   │   │ This action will be permanently     │
   │   │ removed from all users.             │
   │   │                                     │
   │   │ ⚠️ This cannot be undone.          │
   │   │                                     │
   │   │     [Cancel]  [Delete]              │
   │   └─────────────────────────────────────┘
   │
4️⃣ User clicks [Delete]
   │
   ├─→ FRONTEND → MANAGER → API → BACKEND
   │   └─→ DELETE /api/v1/quick-actions/:id
   │       ├─ Validates: User owns action OR is admin
   │       ├─ Validates: Cannot delete system defaults
   │       ├─ Deletes: Database record (CASCADE)
   │       │   ├─ Removes: quick_actions row
   │       │   ├─ Removes: usage_logs (cascade)
   │       │   └─ Removes: favorites (cascade)
   │       └─ Returns: { success: true }
   │
   ├─→ MANAGER SYNCS
   │   └─→ Removes from mergedActions
   │       └─→ Saves to LocalStorage
   │
   ├─→ UI REFRESHES
   │   └─→ Action removed from list
   │
5️⃣ Success notification
   │
   └─→ ✅ "Action deleted successfully"
```

---

## ⭐ Favorites Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    FAVORITES WORKFLOW                        │
└─────────────────────────────────────────────────────────────┘

1️⃣ User finds action to favorite
   │
   ├─→ Browsing in management modal OR
   └─→ Using Quick Actions menu
   │
2️⃣ User clicks ⭐ star icon
   │
   │   ┌──────────────────────────┐
   │   │ 🔬 CBC Guide      [⭐]  │ ← Click
   │   └──────────────────────────┘
   │
3️⃣ Toggle favorite status
   │
   ├─→ FRONTEND (quickActionsUI.js)
   │   └─→ toggleFavorite(categorySlug, actionSlug)
   │
   ├─→ MANAGER (quickActionsManager.js)
   │   └─→ toggleFavorite()
   │       ├─ Gets: Action from mergedActions
   │       ├─ Toggles: action.isFavorited = !isFavorited
   │       └─→ If online & has API ID:
   │           └─→ Calls: quickActionsAPI.toggleFavorite(id)
   │
   ├─→ API CLIENT
   │   └─→ POST /api/v1/quick-actions/:id/favorite
   │
   ├─→ BACKEND
   │   └─→ Database operation:
   │       ├─ Check: Does favorite exist?
   │       │   ├─ YES → DELETE from quick_action_user_favorites
   │       │   └─ NO  → INSERT into quick_action_user_favorites
   │       └─ Returns: { success: true, isFavorited: true/false }
   │
   ├─→ UI UPDATE
   │   ├─ Icon changes: ☆ → ⭐ (or vice versa)
   │   ├─ Tooltip updates: "Add to favorites" ↔ "Remove from favorites"
   │   └─ Button class: .favorited (gold) or not (gray)
   │
4️⃣ Notification
   │
   ├─→ ✅ "Added to favorites"
   └─→ OR ✅ "Removed from favorites"
   │
5️⃣ View all favorites
   │
   ├─→ Management modal → [⭐ Favorites] button
   │
   └─→ Shows all favorited actions
       ├─ Grouped display
       ├─ Category labels
       └─ Quick access to View/Use
```

---

## 🔄 Sync & Offline Flow

```
┌─────────────────────────────────────────────────────────────┐
│              SYNC & OFFLINE WORKFLOW                         │
└─────────────────────────────────────────────────────────────┘

INITIALIZATION (Extension Loads)
═══════════════════════════════════

1️⃣ Extension starts
   │
2️⃣ quickActionsAPI.initialize()
   │
   ├─→ Check: window.API_CONFIG.jwtToken? ✅
   │   └─→ OR chrome.storage.local.authToken? ✅
   │       └─→ OR window.API_CONFIG.apiKey? ✅
   │           └─→ OR chrome.storage.local.apiKey? ✅
   │
3️⃣ quickActionsManager.initialize(QUICK_ACTIONS)
   │
   ├─→ Load: System defaults (hardcoded)
   │   └─→ this.systemDefaults = QUICK_ACTIONS
   │
   ├─→ Load: LocalStorage cache
   │   └─→ chrome.storage.local.get(['quickActions_merged'])
   │       └─→ If exists: this.mergedActions = cached
   │
   ├─→ Check: navigator.onLine?
   │   │
   │   ├─→ YES (Online)
   │   │   └─→ syncWithAPI()
   │   │       ├─ Fetch: Categories
   │   │       ├─ Fetch: Actions
   │   │       ├─ Convert: API format → QUICK_ACTIONS format
   │   │       ├─ Merge: systemDefaults + apiActions
   │   │       ├─ Save: To LocalStorage
   │   │       └─→ this.mergedActions = merged
   │   │
   │   └─→ NO (Offline)
   │       └─→ Use: Cached or system defaults
   │           └─→ this.mergedActions = cached || systemDefaults
   │
4️⃣ quickActionsDisplay.updateQuickAssistMenuHTML()
   │
   └─→ Populate menu with merged actions


AUTO-SYNC (Every 5 Minutes)
═══════════════════════════

⏰ Timer fires every 5 minutes
   │
   ├─→ Check: navigator.onLine?
   │   │
   │   ├─→ YES → syncWithAPI()
   │   │   └─→ Updates mergedActions
   │   │       └─→ UI refreshes automatically
   │   │
   │   └─→ NO → Skip (use cached)


OFFLINE SCENARIO
═══════════════

1️⃣ User loses internet connection
   │
2️⃣ Browser fires 'offline' event
   │
   ├─→ quickActionsManager.handleOnlineStatusChange(false)
   │   ├─ Sets: this.isOnline = false
   │   └─ Log: "Offline - using cached data"
   │
3️⃣ User tries to use Quick Actions
   │
   ├─→ ✅ Menu opens normally
   ├─→ ✅ System defaults available
   ├─→ ✅ Previously synced custom actions available (from cache)
   │
4️⃣ User tries to CREATE custom action
   │
   ├─→ ❌ Error: "Cannot create custom actions while offline"
   │   └─→ User-friendly message
   │
5️⃣ User tries to toggle FAVORITE
   │
   ├─→ ✅ Changes saved locally
   ├─→ ⚠️ Will sync when back online
   │
6️⃣ User connection restores
   │
   ├─→ Browser fires 'online' event
   │
   ├─→ quickActionsManager.handleOnlineStatusChange(true)
   │   ├─ Sets: this.isOnline = true
   │   ├─ Log: "Back online - syncing..."
   │   └─→ syncWithAPI()
   │       └─→ Syncs all pending favorites
   │           └─→ Fetches latest actions
   │               └─→ Updates cache
   │
   └─→ ✅ Seamless transition back online


ERROR HANDLING
═════════════

API Unavailable (Server Down)
   │
   ├─→ fetch() throws error
   │
   ├─→ quickActionsAPI.request() catches
   │   └─→ Checks: Is it HTML response? (<!DOCTYPE)
   │       ├─→ YES → "API not available"
   │       └─→ NO  → Log actual error
   │
   ├─→ quickActionsManager.syncWithAPI() catches
   │   └─→ Fallback to cached/system defaults
   │       └─→ Log: "API unavailable, using defaults"
   │
   └─→ ✅ No user-facing error
       └─→ Silent degradation
```

---

## 🔐 Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│              AUTHENTICATION WORKFLOW                         │
└─────────────────────────────────────────────────────────────┘

USER LOGS IN
═══════════

1️⃣ User enters credentials in extension
   │
2️⃣ unifiedAuthController.login()
   │
   ├─→ POST /api/auth/login
   │   └─→ Returns: { jwtToken, user: {...} }
   │
3️⃣ Store authentication
   │
   ├─→ window.API_CONFIG.jwtToken = token
   ├─→ chrome.storage.local.set({ authToken: token })
   └─→ quickActionsAPI.authToken = token
   │
4️⃣ Quick Actions auto-initialize
   │
   └─→ quickActionsAPI.initialize()
       └─→ Finds JWT token
           └─→ Ready for API calls!


API REQUEST WITH AUTH
═══════════════════

1️⃣ User triggers action (e.g., create custom)
   │
2️⃣ quickActionsAPI.createQuickAction(data)
   │
3️⃣ quickActionsAPI.request(endpoint, options)
   │
   ├─→ getAuthHeaders()
   │   │
   │   ├─→ Check: this.authToken exists?
   │   │   └─→ YES → Headers: { Authorization: "Bearer <token>" }
   │   │
   │   └─→ Check: this.apiKey exists?
   │       └─→ YES → Headers: { X-API-Key: "<key>" }
   │
4️⃣ fetch(url, { headers: authHeaders })
   │
5️⃣ Backend receives request
   │
   ├─→ Middleware: flexUserRoleValid([ROLES.all])
   │   ├─ Extracts: JWT from Authorization header
   │   ├─ Verifies: JWT signature with JWT_SECRET
   │   ├─ Decodes: User ID and role
   │   └─→ Attaches: res.locals.user = { id, role, ... }
   │
6️⃣ Endpoint handler accesses user
   │
   └─→ const user = await userFromSession(req, res);
       └─→ user = { id: 123, role: 'default', ... }


PERMISSION CHECK
═══════════════

Example: Deleting a custom action

1️⃣ User clicks [Delete] on action
   │
2️⃣ DELETE /api/v1/quick-actions/:id
   │
3️⃣ Backend endpoint handler
   │
   ├─→ Gets: User from session (JWT)
   │   └─→ user = { id: 123, role: 'default' }
   │
   ├─→ Gets: Action from database
   │   └─→ action = { id: 5, createdBy: 123, ... }
   │
   ├─→ Check permissions:
   │   ├─ Is user admin? → Can delete anything
   │   ├─ Is user the creator? → Can delete own
   │   └─ Otherwise → 403 Forbidden
   │
   └─→ If authorized → DELETE from database
       └─→ Response: { success: true }
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA FLOW                        │
└─────────────────────────────────────────────────────────────┘

FRONTEND (Chrome Extension)
═══════════════════════════

┌─────────────────────────────────────────────────┐
│ USER INTERFACE                                  │
│ ┌──────────────┐  ┌───────────────────────┐   │
│ │Quick Actions │  │  Management Modal     │   │
│ │    Menu      │  │  (CRUD Interface)     │   │
│ │  (Display)   │  │   ┌────────────────┐  │   │
│ └──────────────┘  │   │ Search/Filter  │  │   │
│        │          │   │ Create Form    │  │   │
│        │          │   │ Edit Form      │  │   │
│        │          │   │ Delete Confirm │  │   │
│        │          │   │ Favorites      │  │   │
│        ▼          │   └────────────────┘  │   │
│ ┌──────────────┐  └───────────────────────┘   │
│ │ quickActions │           │                   │
│ │  Display.js  │◄──────────┘                   │
│ └──────────────┘                               │
│        │                                        │
│        ▼                                        │
│ ┌──────────────┐  Uses                         │
│ │ quickActions │◄──────┐                       │
│ │  Manager.js  │       │                       │
│ └──────────────┘       │                       │
│   │          │         │                       │
│   │ Merges   │ Calls   │                       │
│   │ System+  │ API     │                       │
│   │ API      │         │                       │
│   │          ▼         │                       │
│   │   ┌──────────────┐ │                       │
│   │   │ quickActions │ │                       │
│   │   │    API.js    │ │                       │
│   │   └──────────────┘ │                       │
│   │          │         │                       │
│   │          │ HTTP    │                       │
│   │          │ Requests│                       │
│   ▼          ▼         │                       │
│ ┌──────────────────────┴────────┐              │
│ │  CACHING & STORAGE            │              │
│ │  ┌────────────────────────┐   │              │
│ │  │ LocalStorage           │   │              │
│ │  │ - mergedActions        │   │              │
│ │  │ - lastSync timestamp   │   │              │
│ │  └────────────────────────┘   │              │
│ │  ┌────────────────────────┐   │              │
│ │  │ chrome.storage.local   │   │              │
│ │  │ - authToken (JWT)      │   │              │
│ │  │ - apiKey               │   │              │
│ │  └────────────────────────┘   │              │
│ └────────────────────────────────┘              │
└─────────────────────────────────────────────────┘
                    │
                    │ HTTPS
                    │ Authorization: Bearer <JWT>
                    │
                    ▼

BACKEND (Express.js Server)
═══════════════════════════

┌─────────────────────────────────────────────────┐
│ API ENDPOINTS                                   │
│                                                 │
│ /api/v1/quick-actions/                         │
│ ┌─────────────────────────────────────────┐   │
│ │ GET    /categories                      │   │
│ │ POST   /categories                      │   │
│ │ PUT    /categories/:id                  │   │
│ │ DELETE /categories/:id                  │   │
│ │                                         │   │
│ │ GET    /                (actions)       │   │
│ │ GET    /:id                             │   │
│ │ POST   /                                │   │
│ │ PUT    /:id                             │   │
│ │ DELETE /:id                             │   │
│ │                                         │   │
│ │ POST   /:id/use         (log usage)    │   │
│ │ POST   /:id/favorite    (toggle)       │   │
│ │ GET    /favorites                       │   │
│ │                                         │   │
│ │ GET    /admin/analytics (admin only)   │   │
│ │ POST   /admin/seed-defaults            │   │
│ └─────────────────────────────────────────┘   │
│                    │                           │
│                    │ Uses                      │
│                    ▼                           │
│ ┌─────────────────────────────────────────┐   │
│ │ MIDDLEWARE                              │   │
│ │ - validatedRequest                      │   │
│ │ - flexUserRoleValid([ROLES.all])       │   │
│ │ - JWT verification                      │   │
│ │ - Permission checks                     │   │
│ └─────────────────────────────────────────┘   │
│                    │                           │
│                    ▼                           │
│ ┌─────────────────────────────────────────┐   │
│ │ MODELS (Business Logic)                 │   │
│ │ QuickActions.js                         │   │
│ │ - getCategories()                       │   │
│ │ - createCategory()                      │   │
│ │ - getQuickActions()                     │   │
│ │ - createQuickAction()                   │   │
│ │ - updateQuickAction()                   │   │
│ │ - deleteQuickAction()                   │   │
│ │ - toggleFavorite()                      │   │
│ │ - logUsage()                            │   │
│ │ - getAnalytics()                        │   │
│ └─────────────────────────────────────────┘   │
│                    │                           │
│                    │ Uses Prisma ORM           │
│                    ▼                           │
└─────────────────────────────────────────────────┘
                    │
                    │ SQL Queries
                    │
                    ▼

DATABASE (PostgreSQL)
════════════════════

┌─────────────────────────────────────────────────┐
│ TABLES                                          │
│                                                 │
│ ┌─────────────────────────────────────────┐   │
│ │ quick_action_categories                 │   │
│ │ - id (PK)                               │   │
│ │ - name, slug, icon, description         │   │
│ │ - organizationWide, isSystemDefault     │   │
│ │ - isActive, orderIndex                  │   │
│ │ - createdBy (FK → users)                │   │
│ │ - created_at, updated_at                │   │
│ └─────────────────────────────────────────┘   │
│                    │ 1:N                       │
│                    ▼                           │
│ ┌─────────────────────────────────────────┐   │
│ │ quick_actions                           │   │
│ │ - id (PK)                               │   │
│ │ - categoryId (FK)                       │   │
│ │ - name, slug, icon, description         │   │
│ │ - uiMessage, systemContext, priming     │   │
│ │ - organizationWide, isPublic            │   │
│ │ - isSystemDefault, isActive             │   │
│ │ - orderIndex                            │   │
│ │ - createdBy (FK → users)                │   │
│ │ - created_at, updated_at                │   │
│ └─────────────────────────────────────────┘   │
│          │ 1:N                  │ 1:N          │
│          ▼                      ▼              │
│ ┌─────────────────┐  ┌─────────────────────┐ │
│ │ usage_logs      │  │ user_favorites      │ │
│ │ - id            │  │ - id                │ │
│ │ - actionId (FK) │  │ - actionId (FK)     │ │
│ │ - userId (FK)   │  │ - userId (FK)       │ │
│ │ - workspaceId   │  │ - created_at        │ │
│ │ - used_at       │  │                     │ │
│ └─────────────────┘  └─────────────────────┘ │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

**Document Version**: 1.0  
**Last Updated**: December 6, 2025

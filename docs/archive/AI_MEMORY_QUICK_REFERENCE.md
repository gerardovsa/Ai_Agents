# AI Memory System - Quick Reference Guide

**Date:** November 4, 2025  
**Status:** ✅ PRODUCTION READY  

---

## 🚀 QUICK START

### For Users:
1. **View Memories:** Profile → Settings → Expand "AI Memories" section
2. **Add Memory:** Ask AI: "Remember that [information]"
3. **Delete Memory:** Click trash icon on memory card

### For Developers:
1. **Start Server:** `BISTART`
2. **Test Tools:** `python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print([t for t in r.tools.keys() if 'memory' in t])"`
3. **Check DB:** `sqlite3 data/ai_infrastructure.db "SELECT ai_memories FROM user_preferences;"`

---

## 📦 WHAT WAS ADDED

### 4 AI Tools:
- `read_user_memories` - Fetch memories
- `add_user_memory` - Store new memory
- `update_user_memory` - Update existing memory
- `delete_user_memory` - Remove memory

### 2 UI Sections:
- **User Preferences** - Preferred tools, custom preferences
- **AI Memories** - View, manage stored memories

### Database Fields:
- `ai_memories TEXT` - JSON array of memories
- `memory_updated_at TIMESTAMP` - Last update time

---

## 💬 HOW TO USE (User Perspective)

### Adding Memories:
Just tell the AI to remember something:
- "Remember that I prefer detailed explanations"
- "Save this preference: use Gmail for emails"
- "Keep in mind I'm in PST timezone"
- "Don't forget my deadline is Friday"

### Viewing Memories:
1. Click profile avatar (top right)
2. Click "Settings"
3. Scroll to "AI Memories" section
4. Expand it to see all stored memories

### Managing Memories:
- **Delete:** Click trash icon, confirm
- **Refresh:** Click "Refresh Memories" button
- **Count:** Badge shows total memories

---

## 🔧 MEMORY CATEGORIES

| Category | Icon | Color | Use For |
|----------|------|-------|---------|
| `preferences` | 💜 | Purple | Communication style, tool preferences |
| `personal` | 💙 | Blue | Name, timezone, location, personal facts |
| `work` | 💚 | Green | Job info, deadlines, projects, colleagues |
| `health` | ❤️ | Red | Medical info, appointments, medications |
| `general` | 🩶 | Gray | Everything else |

---

## 🛠️ DEVELOPER REFERENCE

### Tool Usage (AI Agent):

```python
# Read all memories
result = registry.execute_tool(
    'read_user_memories',
    _user_id=1
)

# Add new memory
result = registry.execute_tool(
    'add_user_memory',
    content="User prefers detailed responses",
    category="preferences",
    tags=["communication"],
    _user_id=1
)

# Update memory
result = registry.execute_tool(
    'update_user_memory',
    memory_id="mem_abc123",
    content="Updated content",
    _user_id=1
)

# Delete memory
result = registry.execute_tool(
    'delete_user_memory',
    memory_id="mem_abc123",
    _user_id=1
)
```

### JavaScript Functions:

```javascript
// Load memories from backend
const memories = await loadUserMemories();

// Refresh UI
await refreshMemories();

// Render memories in UI
renderMemories(memories);

// Delete specific memory
await deleteMemory('mem_abc123');
```

### Database Query:

```sql
-- Get user memories
SELECT ai_memories 
FROM user_preferences 
WHERE user_id = 1;

-- Update memories
UPDATE user_preferences 
SET ai_memories = '[...]',
    memory_updated_at = CURRENT_TIMESTAMP
WHERE user_id = 1;
```

---

## 📁 KEY FILES

| File | Purpose | Lines |
|------|---------|-------|
| `tools/implementations/memory_tools.py` | Memory CRUD operations | 480 |
| `tools/schemas/memory_tools.json` | Tool definitions | 140 |
| `AI_infrastructure/routes/user_preferences_routes.py` | Backend API | Modified |
| `UI/business-ai-platform-v2.html` | UI + JavaScript | +340 |

---

## 🧪 TESTING COMMANDS

```powershell
# Check tools loaded
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print([t for t in r.tools.keys() if 'memory' in t])"

# Check database schema
sqlite3 data/ai_infrastructure.db ".schema user_preferences"

# View stored memories
sqlite3 data/ai_infrastructure.db "SELECT user_id, ai_memories FROM user_preferences;"

# Start server
BISTART
```

---

## 🎯 COMMON USE CASES

### Communication Preferences:
**User:** "Remember I prefer brief responses"  
**Result:** AI adjusts future response style

### Timezone Management:
**User:** "I'm in PST timezone"  
**Result:** AI converts times automatically

### Tool Preferences:
**User:** "Always use Gmail, not Outlook"  
**Result:** AI prioritizes Gmail for email tasks

### Work Context:
**User:** "My manager is Sarah at sarah@company.com"  
**Result:** AI knows who to address in work emails

### Deadlines:
**User:** "Project deadline is Dec 1"  
**Result:** AI reminds and tracks progress

---

## 🐛 QUICK TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Memories not showing | Check JWT token, refresh page |
| AI not remembering | Check tool registry loaded |
| Delete not working | Check backend logs, verify auth |
| Count badge wrong | Click refresh button |

---

## 📊 MEMORY STRUCTURE

```json
{
  "id": "mem_abc123",
  "category": "preferences",
  "content": "Prefers detailed explanations",
  "created_at": "2025-11-04T10:30:00Z",
  "relevance_score": 1.0,
  "tags": ["communication"]
}
```

---

## ⚡ QUICK STATS

- **Implementation Time:** 75 minutes
- **Lines of Code:** ~980 lines
- **Files Created:** 2
- **Files Modified:** 2
- **AI Tools Added:** 4
- **UI Sections Added:** 2
- **Database Fields Added:** 2

---

## 🎉 READY TO USE!

1. ✅ Database schema updated
2. ✅ Backend API handles memories
3. ✅ AI tools loaded in registry
4. ✅ UI displays memories
5. ✅ JavaScript functions working
6. ✅ Delete functionality active
7. ✅ Auto-load on modal open

**Start using:** `BISTART` → Login → Ask AI to remember something!

---

**For full documentation, see:** `AI_MEMORY_SYSTEM_COMPLETE.md`

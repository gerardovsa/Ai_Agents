# Synergy Kanban - Quick User Guide

**🎯 Drag-and-Drop & Column Management**

---

## 📋 Moving Cards Between Columns

### **Method 1: Drag and Drop** (New!)

1. **Click and hold** any Synergy card
2. **Drag** over target column (column will highlight blue)
3. **Release** to drop
4. Card moves instantly! ✨

**Visual Cues**:
- Card becomes semi-transparent while dragging
- Target column highlights with blue border
- Success notification appears

---

## 🎛️ Managing Columns

### **Open Column Menu**
- Click the **three dots (⋯)** button in any column header

### **Available Actions**:

#### **1. Rename Column**
- Choose "Rename Column"
- Enter new name
- Column updates instantly

#### **2. Change Column Color**
- Choose "Change Color"
- Enter hex color (e.g., `#3b82f6`)
- Column icon changes color

#### **3. Rearrange Columns**
- Choose "Move Left" or "Move Right"
- Column swaps with adjacent column
- Custom columns only (default columns fixed)

#### **4. Delete Column**
- Choose "Delete Column"
- Confirm deletion
- Cards automatically move to Backlog
- Custom columns only (can't delete defaults)

---

## ➕ Adding Custom Columns

### **Create New Column**:
1. Click **"+ Add Column"** button (right side of board)
2. Enter column name
3. New column appears with default icon
4. Drag cards into it!

**Example Use Cases**:
- Add "QA Testing" column for quality assurance
- Add "Blocked" column for stuck tasks
- Add "Ready to Deploy" for deployment queue

---

## 💡 Quick Tips

### **Default Columns** (Can't Delete):
- 📥 Backlog
- 🔄 In Progress
- 👁️ Review
- ✅ Done

### **Custom Columns**:
- Can rename, reorder, delete
- Saved to your browser
- Persist across sessions

### **Moving Cards**:
- Drag within same column = no change
- Drag to different column = updates status
- Backend saves automatically
- Real-time updates for other users

### **Column Counts**:
- Badge shows card count per column
- Updates automatically after moves

---

## 🎨 Customization

### **Column Colors** (Icon Colors):
- Blue (`#3b82f6`) - Active work
- Green (`#10b981`) - Completed
- Yellow (`#f59e0b`) - Needs review
- Red (`#ef4444`) - Blocked
- Purple (`#a855f7`) - Special category
- Gray (`#6b7280`) - Default

### **Suggested Icons** (Advanced - localStorage edit):
- `fa-inbox` - Backlog
- `fa-spinner` - In Progress
- `fa-eye` - Review
- `fa-check-circle` - Done
- `fa-list` - General
- `fa-bug` - Bug tracking
- `fa-rocket` - Deployment

---

## ⌨️ Keyboard Shortcuts

*Coming soon!*

---

## ❓ FAQ

**Q: Where are my custom columns saved?**  
A: In your browser's localStorage. Clear browser data = lose custom columns.

**Q: Can I share column layout with my team?**  
A: Not yet - feature planned for future release.

**Q: What happens to cards if I delete a column?**  
A: All cards automatically move to Backlog before column deletion.

**Q: Can I change the order of default columns?**  
A: Not yet - only custom columns can be reordered.

**Q: Do drag-and-drop changes sync in real-time?**  
A: Yes! Other users see card moves instantly via WebSocket.

---

## 🐛 Troubleshooting

**Card won't drag?**
- Refresh page
- Check if you're clicking the card content (not buttons)

**Column menu not appearing?**
- Try clicking the three dots (⋯) button again
- Check browser console for errors

**Custom columns disappeared?**
- Check if browser data was cleared
- Columns stored in localStorage

---

**Need Help?** Check full documentation: `SYNERGY_KANBAN_DRAG_DROP_COMPLETE.md`

**Version**: 1.0 | **Last Updated**: November 24, 2025

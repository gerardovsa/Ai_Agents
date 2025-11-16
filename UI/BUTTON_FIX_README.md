# BUTTON FIX SCRIPTS - Quick Reference

These are individual console scripts to fix right sidebar buttons.

## 📋 How to Use:

1. **Open browser console** (F12)
2. **Copy entire contents** of the script you need
3. **Paste into console** and press Enter
4. **Test the button** - it should work immediately

## 🔧 Available Scripts:

### 1. AI Prime Toggle Button (🤖)
**File:** `fix_ai_prime_button.js`
**Fixes:** Shows/hides AI Prime chat panel
**Button ID:** `ai-prime-toggle-btn`

### 2. User Profile Button (👤)
**File:** `fix_user_profile_button.js`
**Fixes:** Opens user profile dropdown menu
**Button IDs:** `userProfileBtn-sidebar`, `userProfileBtn`
**Note:** Also makes the profile container visible

### 3. Quick Actions Button (⚡)
**File:** `fix_quick_actions_button.js`
**Fixes:** Opens Instructions Catalogue sidebar
**Button ID:** `quick-actions-btn`

### 4. Threads Button (💬)
**File:** `fix_threads_button.js`
**Fixes:** Opens thread history menu
**Button ID:** `threads-btn`

### 5. Theme Toggle Button (🌓)
**File:** `fix_theme_button.js`
**Fixes:** Switches between dark/light theme
**Button ID:** `theme-toggle-btn-sidebar`

### 6. New Chat Button (➕)
**File:** `fix_new_chat_button.js`
**Fixes:** Opens new chat modal
**Button ID:** `new-chat-btn`

## 🎯 What Each Script Does:

- ✅ **Removes duplicate event listeners** (by cloning the button)
- ✅ **Adds clean single click handler** 
- ✅ **Shows hidden elements** (for user profile)
- ✅ **Provides console feedback** showing success/failure
- ✅ **Works immediately** - no page reload needed

## 💡 Tips:

- **Run scripts one at a time** as you test each button
- **Console logs** will show if the button is working
- **Green ✅ messages** mean success
- **Red ❌ messages** mean elements are missing (check HTML)

## 🔍 Troubleshooting:

**If a script doesn't work:**
1. Check console for error messages
2. Verify the button exists in HTML (check Button ID)
3. Check that required elements exist (panel, menu, etc.)
4. Try refreshing the page and running the script again

**Common Issues:**
- **User Profile not showing:** Profile container was hidden - script fixes this
- **AI Prime not toggling:** Duplicate listeners - script removes them
- **Quick Actions not working:** Prompt sidebar not loaded - check prompt-library.js

## 📝 Notes:

These are **temporary fixes** for testing. For permanent fixes, the issues should be resolved in the actual HTML/JavaScript files:
- Remove duplicate event listeners
- Ensure profile container is visible by default
- Use single initialization pattern with guards

# Modal System - Complete Usage Guide
**Version:** 1.0.0  
**Created:** November 12, 2025  
**Status:** Production Ready ✅

## 🎯 Overview

Complete modal system with 8 variants replacing all native browser dialogs (alert, confirm). Features focus trap, scroll lock, keyboard navigation, responsive design, and full accessibility support.

### Features
- ✅ **8 Modal Types**: Base, Confirmation, Alert, Loading, Wizard, Drawer, Form, Multi-Action
- ✅ **Focus Trap**: Keeps keyboard users inside modal
- ✅ **Scroll Lock**: Prevents background scrolling
- ✅ **ESC Key**: Close modals with Escape key
- ✅ **Stacking**: Multiple modals with proper z-index
- ✅ **Animations**: Fade, slide, scale, or none
- ✅ **Responsive**: Mobile-friendly with breakpoints
- ✅ **Accessible**: ARIA labels, keyboard navigation
- ✅ **Dark Mode**: Automatic dark theme support

---

## 📦 Installation

### 1. Include Required Files

```html
<!-- In your HTML <head> -->
<link rel="stylesheet" href="path/to/design-tokens.css">
<link rel="stylesheet" href="path/to/modal-system.css">

<!-- Before </body> -->
<script src="path/to/modal-system.js"></script>
<script src="path/to/ui-components.js"></script>
```

### 2. Verify Global Instance

```javascript
// Check if ModalSystem is loaded
console.log(window.ModalSystem); // Should show ModalSystem object
console.log(window.UIComponents); // Should show UIComponents object
```

---

## 🚀 Quick Start

### Simple Confirmation (Replaces `confirm()`)

**Before (Native):**
```javascript
if (confirm('Delete this item?')) {
    deleteItem();
}
```

**After (Custom Modal):**
```javascript
UIComponents.showConfirmation({
    title: 'Delete Item?',
    message: 'This action cannot be undone.',
    variant: 'danger',
    confirmLabel: 'Delete',
    cancelLabel: 'Cancel',
    onConfirm: () => {
        deleteItem();
    }
});
```

### Simple Alert (Replaces `alert()`)

**Before (Native):**
```javascript
alert('Item saved successfully!');
```

**After (Custom Modal):**
```javascript
UIComponents.showAlert({
    title: 'Success',
    message: 'Item saved successfully!',
    variant: 'success'
});
```

### Loading Modal

```javascript
const loader = UIComponents.showLoading({
    title: 'Saving',
    message: 'Please wait...',
    cancelable: false
});

// Do async work
await saveData();

// Hide when done
loader.hide();
```

---

## 📚 API Reference

### 1. Base Modal (ModalSystem.createModal)

Create a custom modal with full control.

```javascript
const modal = ModalSystem.createModal({
    title: 'My Modal',
    content: '<p>Modal content goes here</p>',
    size: 'md',              // sm, md, lg, xl, full
    variant: 'default',      // default, danger, warning, info, success
    animation: 'fade',       // fade, slide, scale, none
    closeOnBackdrop: true,   // Click outside to close
    closeOnEscape: true,     // Press ESC to close
    showCloseButton: true,   // Show X button
    scrollLock: true,        // Lock body scroll
    focusTrap: true,         // Trap focus inside
    actions: [
        {
            label: 'Cancel',
            variant: 'secondary',
            icon: 'fas fa-times',
            handler: (modal) => modal.hide()
        },
        {
            label: 'Save',
            variant: 'primary',
            icon: 'fas fa-check',
            showLoading: true,     // Show loading state
            loadingLabel: 'Saving...',
            handler: async (modal) => {
                await save();
                modal.hide();
            }
        }
    ],
    onOpen: (modal) => console.log('Modal opened'),
    onClose: (modal) => console.log('Modal closed')
});

// Show the modal
modal.show();

// Methods available
modal.hide();                           // Hide modal
modal.destroy();                        // Remove from DOM
modal.updateContent('<p>New content</p>');  // Change content
modal.updateActions([...]);              // Change actions
```

### 2. Confirmation Modal (UIComponents.showConfirmation)

Standard confirmation dialog with two buttons.

```javascript
UIComponents.showConfirmation({
    title: 'Delete Session?',
    message: 'This will permanently delete all session data. This action cannot be undone.',
    variant: 'danger',        // danger, warning, info, default
    confirmLabel: 'Delete',   // Default: 'Confirm'
    cancelLabel: 'Cancel',    // Default: 'Cancel'
    confirmIcon: 'fas fa-trash',  // Optional icon
    onConfirm: async () => {
        await deleteSession();
        console.log('Deleted');
    },
    onCancel: () => {
        console.log('Cancelled');
    }
});
```

**Variants:**
- `danger` - Red header, for destructive actions (delete, remove)
- `warning` - Yellow header, for cautionary actions (reset, clear)
- `info` - Blue header, for informational confirmations
- `default` - Gray header, for neutral confirmations

### 3. Alert Modal (UIComponents.showAlert)

One-button alert dialog.

```javascript
UIComponents.showAlert({
    title: 'Save Successful',
    message: 'Your changes have been saved successfully.',
    variant: 'success',  // success, error, warning, info
    okLabel: 'Got it',   // Default: 'OK'
    onOk: () => {
        console.log('User acknowledged');
    }
});
```

**Variants:**
- `success` - Green header, for success messages
- `error` - Red header, for error messages
- `warning` - Yellow header, for warnings
- `info` - Blue header, for informational alerts

### 4. Loading Modal (UIComponents.showLoading)

Show loading indicator during async operations.

```javascript
// Basic loading
const loader = UIComponents.showLoading({
    title: 'Loading',
    message: 'Please wait while we fetch your data...',
    cancelable: false  // Can't close until done
});

await fetchData();
loader.hide();

// With progress bar
const loader = UIComponents.showLoading({
    title: 'Uploading',
    message: 'Uploading files...',
    progress: 0,
    cancelable: true,
    onCancel: () => {
        abortUpload();
    }
});

// Update progress
for (let i = 0; i <= 100; i += 10) {
    loader.updateProgress(i);
    await uploadChunk(i);
}

loader.hide();
```

### 5. Wizard Modal (UIComponents.showWizard)

Multi-step wizard with progress indicator.

```javascript
UIComponents.showWizard({
    title: 'Project Setup Wizard',
    size: 'lg',
    steps: [
        {
            title: 'Basic Info',
            content: `
                <form>
                    <input type="text" name="projectName" placeholder="Project Name" />
                    <textarea name="description" placeholder="Description"></textarea>
                </form>
            `
        },
        {
            title: 'Team Members',
            content: `
                <p>Select team members to add:</p>
                <select multiple>
                    <option>John Doe</option>
                    <option>Jane Smith</option>
                </select>
            `
        },
        {
            title: 'Settings',
            content: `
                <label><input type="checkbox" /> Enable notifications</label>
                <label><input type="checkbox" /> Public project</label>
            `
        }
    ],
    finishLabel: 'Create Project',
    onFinish: async () => {
        await createProject();
    }
});
```

### 6. Drawer Modal (UIComponents.showDrawer)

Side panel/drawer for secondary content.

```javascript
UIComponents.showDrawer({
    title: 'Settings',
    position: 'right',  // left, right, top, bottom
    width: '400px',
    content: `
        <div class="settings-panel">
            <h4>Account Settings</h4>
            <form>
                <input type="text" placeholder="Username" />
                <input type="email" placeholder="Email" />
            </form>
        </div>
    `,
    actions: [
        {
            label: 'Cancel',
            variant: 'secondary',
            handler: (modal) => modal.hide()
        },
        {
            label: 'Save',
            variant: 'primary',
            handler: async (modal) => {
                await saveSettings();
                modal.hide();
            }
        }
    ]
});
```

### 7. Form Modal (UIComponents.showForm)

Form with validation.

```javascript
UIComponents.showForm({
    title: 'Create User',
    size: 'md',
    fields: [
        {
            name: 'username',
            label: 'Username',
            type: 'text',
            placeholder: 'Enter username',
            required: true,
            validation: (value) => value.length >= 3,
            errorMessage: 'Username must be at least 3 characters'
        },
        {
            name: 'email',
            label: 'Email',
            type: 'email',
            required: true,
            validation: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
            errorMessage: 'Please enter a valid email'
        },
        {
            name: 'role',
            label: 'Role',
            type: 'select',
            required: true,
            options: [
                { value: 'admin', label: 'Administrator' },
                { value: 'user', label: 'User' },
                { value: 'guest', label: 'Guest' }
            ]
        },
        {
            name: 'bio',
            label: 'Bio',
            type: 'textarea',
            rows: 4,
            required: false
        },
        {
            name: 'newsletter',
            label: 'Subscribe to newsletter',
            type: 'checkbox',
            value: true
        }
    ],
    submitLabel: 'Create User',
    cancelLabel: 'Cancel',
    onSubmit: async (formData) => {
        console.log('Form data:', formData);
        await createUser(formData);
    },
    onCancel: () => {
        console.log('Form cancelled');
    }
});
```

**Field Types:**
- `text`, `email`, `number`, `password` - Standard inputs
- `textarea` - Multi-line text
- `select` - Dropdown with options
- `checkbox` - Boolean field

---

## 💡 Common Use Cases

### Delete Confirmation with Danger Variant

```javascript
function deleteSession(sessionId) {
    UIComponents.showConfirmation({
        title: 'Delete Session?',
        message: 'This will permanently delete the session and all its data. This action cannot be undone.',
        variant: 'danger',
        confirmLabel: 'Delete',
        cancelLabel: 'Cancel',
        onConfirm: async () => {
            await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
            UIComponents.showAlert({
                title: 'Deleted',
                message: 'Session deleted successfully',
                variant: 'success'
            });
        }
    });
}
```

### File Upload with Progress

```javascript
async function uploadFiles(files) {
    const loader = UIComponents.showLoading({
        title: 'Uploading Files',
        message: `Uploading ${files.length} file(s)...`,
        progress: 0,
        cancelable: true,
        onCancel: () => {
            uploadAborted = true;
        }
    });

    for (let i = 0; i < files.length; i++) {
        if (uploadAborted) break;
        
        await uploadFile(files[i]);
        
        const progress = Math.round(((i + 1) / files.length) * 100);
        loader.updateProgress(progress);
    }

    loader.hide();
    
    UIComponents.showAlert({
        title: 'Upload Complete',
        message: `Successfully uploaded ${files.length} file(s)`,
        variant: 'success'
    });
}
```

### Settings Drawer

```javascript
function openSettingsDrawer() {
    UIComponents.showDrawer({
        title: 'Settings',
        position: 'right',
        width: '400px',
        content: `
            <div class="settings-panel">
                <h4>Preferences</h4>
                <label>
                    <input type="checkbox" id="darkMode" />
                    Enable Dark Mode
                </label>
                <label>
                    <input type="checkbox" id="notifications" />
                    Show Notifications
                </label>
                <label>
                    Theme
                    <select id="theme">
                        <option>Blue</option>
                        <option>Green</option>
                        <option>Purple</option>
                    </select>
                </label>
            </div>
        `,
        actions: [
            {
                label: 'Save',
                variant: 'primary',
                handler: (modal) => {
                    const darkMode = document.getElementById('darkMode').checked;
                    const notifications = document.getElementById('notifications').checked;
                    const theme = document.getElementById('theme').value;
                    
                    saveSettings({ darkMode, notifications, theme });
                    modal.hide();
                }
            }
        ]
    });
}
```

---

## 🎨 Styling & Customization

### Size Variants

```javascript
UIComponents.createModal({
    size: 'sm'   // 400px max-width
});

UIComponents.createModal({
    size: 'md'   // 600px (default)
});

UIComponents.createModal({
    size: 'lg'   // 800px
});

UIComponents.createModal({
    size: 'xl'   // 1200px
});

UIComponents.createModal({
    size: 'full'  // 100vw x 100vh (fullscreen)
});
```

### Animation Types

```javascript
UIComponents.createModal({
    animation: 'fade'   // Fade in/out (default)
});

UIComponents.createModal({
    animation: 'slide'  // Slide from top
});

UIComponents.createModal({
    animation: 'scale'  // Scale from 70% to 100%
});

UIComponents.createModal({
    animation: 'none'   // No animation
});
```

### Custom Button Actions

```javascript
UIComponents.createModal({
    actions: [
        {
            label: 'Cancel',
            variant: 'secondary',     // secondary, primary, danger, success, warning
            icon: 'fas fa-times',     // Font Awesome icon
            disabled: false,           // Disable button
            showLoading: true,         // Show loading during handler
            loadingLabel: 'Processing...', // Text during loading
            handler: async (modal) => {
                // Do async work
                await doSomething();
                modal.hide();
            }
        }
    ]
});
```

---

## ♿ Accessibility Features

### Keyboard Navigation

- ✅ **ESC Key**: Close modal (if `closeOnEscape: true`)
- ✅ **Tab Key**: Navigate between focusable elements
- ✅ **Shift+Tab**: Navigate backwards
- ✅ **Focus Trap**: Tab cycles within modal only
- ✅ **Auto-focus**: First focusable element gets focus on open

### ARIA Attributes

```html
<div role="dialog" 
     aria-modal="true" 
     aria-labelledby="modal-title">
    <h3 id="modal-title">Modal Title</h3>
    ...
</div>
```

### Screen Reader Support

- All modals announce title and role
- Form fields have associated labels
- Buttons have descriptive labels
- Loading states announce changes

---

## 📱 Responsive Design

### Mobile Behavior

- Modals become 95% width on screens < 768px
- Actions stack vertically
- Drawers become full-width
- Wizard steps show vertically
- Progress indicators adapt

### Breakpoint

```css
@media (max-width: 768px) {
    .modal-container {
        width: 95% !important;
        max-width: 95% !important;
    }
    
    .modal-actions {
        flex-direction: column;
    }
}
```

---

## 🔧 Advanced Usage

### Modal Stacking

```javascript
// Open first modal
const modal1 = UIComponents.showAlert({
    title: 'First Modal',
    message: 'This is the first modal'
});

// Open second modal (automatically higher z-index)
const modal2 = UIComponents.showAlert({
    title: 'Second Modal',
    message: 'This modal appears on top'
});

// Close all modals
ModalSystem.hideAll();
```

### Custom Content with HTML

```javascript
UIComponents.createModal({
    title: 'Custom Content',
    content: `
        <div style="padding: 20px;">
            <img src="image.jpg" style="width: 100%;">
            <p>Custom HTML content goes here</p>
            <button onclick="doSomething()">Click Me</button>
        </div>
    `
});
```

### Dynamic Content Updates

```javascript
const modal = UIComponents.showLoading({
    title: 'Processing',
    message: 'Step 1 of 3...'
});

// Update message
setTimeout(() => {
    modal.updateContent(`
        <div class="loading-modal-content">
            <div class="loading-spinner"><i class="fas fa-spinner fa-spin fa-3x"></i></div>
            <p class="loading-message">Step 2 of 3...</p>
        </div>
    `);
}, 1000);
```

---

## ⚠️ Migration from Native Dialogs

### Find & Replace Guide

**1. Replace confirm():**

```javascript
// Find:
if (confirm('Delete this?')) {
    delete();
}

// Replace with:
UIComponents.showConfirmation({
    title: 'Delete?',
    message: 'Are you sure?',
    variant: 'danger',
    onConfirm: () => delete()
});
```

**2. Replace alert():**

```javascript
// Find:
alert('Saved successfully!');

// Replace with:
UIComponents.showAlert({
    title: 'Success',
    message: 'Saved successfully!',
    variant: 'success'
});
```

**3. Add loading states:**

```javascript
// Before:
async function save() {
    await saveData();
    alert('Saved!');
}

// After:
async function save() {
    const loader = UIComponents.showLoading({
        title: 'Saving',
        message: 'Please wait...'
    });
    
    await saveData();
    loader.hide();
    
    UIComponents.showAlert({
        title: 'Success',
        message: 'Saved successfully!',
        variant: 'success'
    });
}
```

---

## 🐛 Troubleshooting

### Modal Not Showing

1. Check if ModalSystem is loaded:
   ```javascript
   console.log(window.ModalSystem); // Should be defined
   ```

2. Check if CSS is loaded:
   ```javascript
   console.log(document.querySelectorAll('link[href*="modal-system"]'));
   ```

3. Check console for errors

### Focus Trap Not Working

- Ensure modal has focusable elements (buttons, inputs, links)
- Check `focusTrap: true` in config
- Verify no z-index conflicts

### Scroll Lock Not Working

- Check `scrollLock: true` in config
- Verify no parent elements with `overflow: auto`
- Check for conflicting JavaScript

### Buttons Not Responding

- Verify `handler` function is provided
- Check for JavaScript errors in handler
- Ensure modal isn't destroyed prematurely

---

## 📝 Examples

### Complete Delete Flow

```javascript
async function deleteCard(sessionId) {
    UIComponents.showConfirmation({
        title: 'Delete Session?',
        message: 'This action cannot be undone. All session data will be permanently deleted.',
        variant: 'danger',
        confirmLabel: 'Delete',
        cancelLabel: 'Cancel',
        onConfirm: async () => {
            const loader = UIComponents.showLoading({
                title: 'Deleting',
                message: 'Deleting session...',
                cancelable: false
            });
            
            try {
                await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
                loader.hide();
                
                UIComponents.showAlert({
                    title: 'Deleted',
                    message: 'Session deleted successfully',
                    variant: 'success'
                });
                
                // Refresh UI
                refreshSessionList();
            } catch (error) {
                loader.hide();
                
                UIComponents.showAlert({
                    title: 'Error',
                    message: `Failed to delete session: ${error.message}`,
                    variant: 'error'
                });
            }
        }
    });
}
```

---

## 📊 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile Safari iOS 14+
- ✅ Chrome Android 90+

---

## 🎯 Best Practices

1. **Use appropriate variants:**
   - `danger` for destructive actions (delete, remove)
   - `warning` for cautionary actions (reset, clear)
   - `success` for success messages
   - `error` for error messages

2. **Provide clear messages:**
   - State what will happen
   - Mention if action is irreversible
   - Give context for the action

3. **Use loading states:**
   - Show loading during async operations
   - Update progress when possible
   - Always hide loader when done

4. **Handle errors:**
   - Catch exceptions in handlers
   - Show error alerts to users
   - Log errors for debugging

5. **Keep modals focused:**
   - One action per modal
   - Don't nest too many modals
   - Use drawers for secondary content

---

## 📄 License

MIT License - Free to use and modify

---

## 🆘 Support

For issues or questions:
1. Check this documentation
2. Check console for errors
3. Verify all files are loaded
4. Check browser compatibility

**Last Updated:** November 12, 2025

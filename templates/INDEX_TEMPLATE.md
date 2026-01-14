# INDEX.md Template

Use this for folders with 10+ files:

---

# [Folder Name] Index

Complete inventory of all files in this folder.

**Last Updated:** YYYY-MM-DD  
**Total Files:** [Number]  
**Agent Owner:** [PRIMARY_AGENT]

---

## Files

### filename1.js
- **Purpose:** [What this file does]
- **Type:** [Service / Model / Controller / Utility / etc.]
- **Exports:** 
  - `functionName()` - [Description]
  - `ClassName` - [Description]
- **Dependencies:**
  - [internal/file.js]
  - [package-name]
- **Used By:**
  - [consumer/file.js]
- **Related Files:**
  - [related/file.js]
- **Agent:** [Which agent owns this]
- **Status:** [Active / Deprecated / In Development]
- **Last Modified:** YYYY-MM-DD
- **Lines of Code:** ~[approximate]

### filename2.js
[Repeat above format]

---

## Quick Reference

### By Feature
- **Authentication:** `authService.js`, `authMiddleware.js`, `jwt.js`
- **Payments:** `paymentService.js`, `stripeService.js`, `webhooks.js`
- **Users:** `userService.js`, `profileService.js`, `validation.js`

### By Type
- **Services:** `authService.js`, `paymentService.js`, `userService.js`
- **Utilities:** `jwt.js`, `validation.js`, `logger.js`
- **Middleware:** `authMiddleware.js`, `errorMiddleware.js`

### By Agent
- **AUTH_AGENT:** `authService.js`, `jwt.js`, `authMiddleware.js`
- **PAYMENT_AGENT:** `paymentService.js`, `stripeService.js`
- **USER_AGENT:** `userService.js`, `profileService.js`

---

## Dependency Graph
```
┌─────────────────┐
│  authService    │
└────────┬────────┘
         │ uses
         ▼
┌─────────────────┐     ┌──────────────┐
│  userService    │────→│ emailService │
└────────┬────────┘     └──────────────┘
         │ uses
         ▼
┌─────────────────┐
│  User.js        │
└─────────────────┘
```

---

## Statistics

- **Total Functions:** [Number]
- **Total Classes:** [Number]
- **Average File Size:** ~[Number] lines
- **Test Coverage:** [Percentage]%
- **Last Major Refactor:** YYYY-MM-DD

---

## Deprecated Files

### oldFilename.js
- **Deprecated:** YYYY-MM-DD
- **Replaced By:** `newFilename.js`
- **Reason:** [Why it was deprecated]
- **Removal Date:** [When it will be removed]

---

## AI Usage Instructions

When working in this folder:
```
@file:folder/INDEX.md

Find all files related to [feature].
Reference this index for dependencies and relationships.
```

When adding new files:
```
@file:folder/INDEX.md

Update index with new file: filename.js
Add to appropriate quick reference sections.
Update dependency graph if needed.
```

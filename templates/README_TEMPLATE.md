# README.md Template

Copy this to any folder that needs documentation:

---

# [Folder Name]

## Purpose
[2-3 sentences explaining what this folder contains and why it exists]

## Structure
```
folder/
├── file1.js - [Brief one-line description]
├── file2.js - [Brief one-line description]
├── subfolder/
│   └── file3.js - [Brief one-line description]
└── README.md - This file
```

## Key Files

### file1.js
**Purpose:** [Detailed explanation of what this file does]
**Used By:** [What imports/uses this]
**Dependencies:** [What this imports/uses]

### file2.js
**Purpose:** [Detailed explanation]
**Used By:** [What imports/uses this]
**Dependencies:** [What this imports/uses]

## Conventions & Patterns

### Naming Convention
- [Rule 1, e.g., "Use camelCase for functions"]
- [Rule 2, e.g., "Use PascalCase for classes"]

### Code Pattern
All files in this folder follow this pattern:
```javascript
// [Show common pattern used across files]
```

### Error Handling
- [How errors are handled, e.g., "Use ErrorHandler from src/shared/"]
- [Exception cases]

## Dependencies

### External Packages
- [package-name] ^[version] - [What it's used for]

### Internal Dependencies
- [path/to/module] - [What it provides]

## Related Folders
- [/path/to/related/folder] - [Relationship, e.g., "Calls these services"]
- [/path/to/another/folder] - [Relationship]

## Agent Ownership
**Primary Agent:** [AUTH_AGENT / PAYMENT_AGENT / etc.]
**Agent Context File:** [agents/AGENT_NAME.md]

## Last Updated
YYYY-MM-DD - [Brief summary of recent changes]

---

## AI Usage Instructions

When working with AI in this folder:
```
@file:folder/README.md

I'm working on [feature] in this folder.
Follow the patterns and conventions documented here.
```

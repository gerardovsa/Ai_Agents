# File Header Template

Copy and customize this header for each file:

## JavaScript/TypeScript
```javascript
/**
 * FILE: [path/to/file.js]
 * PURPOSE: [One-line description]
 * 
 * DEPENDENCIES:
 * - [internal/file.js] ([what it provides])
 * - [package-name] ^[version] ([what it's used for])
 * 
 * EXPORTS:
 * - [functionName(params)] - [description]
 * - [ClassName] - [description]
 * 
 * USED BY:
 * - [path/to/consumer.js] ([how it's used])
 * 
 * RELATED FILES:
 * - [path/to/related.js] ([relationship])
 * 
 * NOTES:
 * - [Important implementation detail]
 * - [Security consideration]
 * - [Performance note]
 * - [Known limitation]
 * 
 * LAST MODIFIED: YYYY-MM-DD - [Change description]
 */
```

## Python
```python
"""
FILE: path/to/file.py
PURPOSE: [One-line description]

DEPENDENCIES:
- internal.module ([what it provides])
- package==version ([what it's used for])

EXPORTS:
- function_name(params: type) -> return_type - [description]
- ClassName - [description]

USED BY:
- path.to.consumer ([how it's used])

RELATED FILES:
- path.to.related ([relationship])

NOTES:
- [Important implementation detail]
- [Security consideration]
- [Performance note]
- [Known limitation]

LAST MODIFIED: YYYY-MM-DD - [Change description]
"""
```

## Usage with AI

When asking AI to create or document a file:
```
@file:templates/FILE_HEADER_TEMPLATE.md

Create src/services/emailService.js with proper header following this template.
```

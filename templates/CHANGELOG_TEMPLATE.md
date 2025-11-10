# CHANGELOG.md Template

Copy this to production code folders:

---

# [Folder Name] Changelog

All notable changes to files in this folder will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]
### Added
- [New file or feature]

### Changed
- [Modified behavior or refactoring]

### Fixed
- [Bug fix]

### Deprecated
- [Feature marked for removal]

### Removed
- [Deleted file or feature]

### Security
- [Security improvement or fix]

---

## [YYYY-MM-DD]
### Added
- `filename.js` - [Description of new file]
- Feature: [Description of new feature]
- Function `functionName()` in `file.js` - [What it does]

### Changed
- `filename.js` - [What changed and why]
- Updated [component] to [new behavior]
- Refactored [area] for [reason]

### Fixed
- `filename.js` - [Bug that was fixed]
- Issue with [component] where [problem description]

### Deprecated
- `oldFile.js` - Use `newFile.js` instead
- Function `oldFunction()` - Use `newFunction()` instead

### Removed
- `obsoleteFile.js` - [Why it was removed]

### Security
- Fixed [security issue]
- Updated [dependency] to patch [vulnerability]

---

## [YYYY-MM-DD]
### Added
...

---

## Template Usage

### When to Update
- After completing work and before deployment
- After code review approval
- When moving items from NOTES.md

### Format Guidelines
- Use past tense ("Added", "Fixed", not "Add", "Fix")
- Be specific with file names and function names
- Include brief "why" when it adds clarity
- Group related changes together
- Most recent changes at top

### Examples

**Good:**
```
### Added
- `paymentService.js` - Stripe subscription management with webhook support
- Function `handleSubscriptionUpdate()` - Processes Stripe subscription.updated webhooks
```

**Bad:**
```
### Added
- Payment stuff
- Some webhook thing
```

---

## AI Usage Instructions

When completing work:
```
@file:folder/NOTES.md
@file:folder/CHANGELOG.md

Move completed items from NOTES.md to CHANGELOG.md.
Add proper date section and categorize changes.
```

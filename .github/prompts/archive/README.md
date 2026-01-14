# Archived Prompts - AI Agents Platform

**Archive Date:** November 30, 2025

## Purpose

This directory contains obsolete prompt files that have been superseded by newer versions. These files are preserved for historical reference but should not be used for active development.

## Archived Files

### Module Architect V3.0.prompt.md
- **Archived:** November 30, 2025
- **Reason:** Superseded by Module Architect V4.0 - Modern Framework Edition
- **Key Changes:** 
  - V3.0 focused on BaseModule inheritance pattern
  - V4.0 uses Modern Module Loading Framework (composition-based)
  - V4.0 provides 100% alignment with ModuleLoaderV4
  - V4.0 includes complete migration guides from BaseModule to composition

### MODULE_ARCHITECT_V2_UPDATES.md
- **Archived:** November 30, 2025
- **Reason:** Updates integrated into V4.0 prompt
- **Key Changes:**
  - V2 updates described two architecture patterns (separate files vs inline HTML-in-JS)
  - V4.0 fully incorporates both patterns in modern framework context
  - V4.0 adds composition pattern as primary approach

## Active Prompts

For current module development, use:
- **Module Architect V4.0 - Modern Framework.prompt.md** - Primary module creation/refactoring prompt

## Historical Context

### Evolution of Module Architect

**V1.0** (Original)
- Single architecture pattern only
- BaseModule inheritance required
- Manual instantiation code

**V2.0** (November 27, 2025)
- Added support for two architecture patterns
- Recognized inline HTML-in-JS as valid approach
- Still used BaseModule inheritance

**V3.0** (November 29, 2025)
- Extended capabilities system (WebRTC, AI, WebSocket)
- V3.0 manifest schema
- Module types (internal/external)
- Improved troubleshooting guides
- Still used BaseModule inheritance

**V4.0** (November 30, 2025) - CURRENT
- **Modern Module Loading Framework** alignment
- Composition over inheritance
- No BaseModule required
- Automatic lifecycle management
- Explicit utility injection
- 100% testable modules
- Complete migration guides

## Migration Path

If you're working with a module using patterns from archived prompts:

1. **Read V4.0 prompt** - Understand modern framework benefits
2. **Review migration guide** - Step-by-step conversion process
3. **Update manifest** - Add `dependencies.utilities`
4. **Convert code** - Class to export default object
5. **Test thoroughly** - Use ModuleLoaderV4 API

## Reference Documentation

Related modern framework documentation:
- `UI/shared/js/MODERN_MODULE_FRAMEWORK_GUIDE.md` (1,500+ lines)
- `UI/shared/js/MIGRATION_CHECKLIST.md` (800+ lines)
- `UI/shared/js/QUICK_REFERENCE_CARD.md` (600+ lines)
- `UI/shared/js/example-modern-module.js` (700+ lines)
- `UI/shared/js/FRAMEWORK_COMPLETE.md` (500+ lines)
- `UI/shared/js/DOCUMENTATION_INDEX.md` (1,500+ lines)

**Total Modern Framework Documentation:** 5,600+ lines

---

**Note:** Do not delete archived files. They provide historical context and may be useful for understanding legacy code or migration decisions.

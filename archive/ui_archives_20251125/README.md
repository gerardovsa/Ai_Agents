# Archived UI Files - November 25, 2025

## Reason for Archiving
These files were archived to prevent conflicts with the new self-registering module system.
The new system uses a unified ModuleRegistry pattern (like the tool registry) with automatic
credential discovery and dynamic loading.

## Archived Files

### From UI/js/
- module-loader.js (OLD manual loader)
- module-manager.js (OLD manual manager)
- module-base.js (OLD base class)
- module-base copy.js (OLD backup)
- ui-builder.js (OLD UI builder)

### From UI/module_builder/
- All module builder templates and toolkit files

## New System Location
The new self-registering module system is located at:
- Backend: AI_infrastructure/core/module_registry.py
- Routes: AI_infrastructure/routes/module_routes.py
- Frontend: frontend/modules/module_loader.js

## Migration Path
Modules are now located in:
- frontend/modules/<module_name>/
  - manifest.json (defines everything)
  - <module_name>.html
  - <module_name>.js
  - <module_name>.css

See MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md for full documentation.

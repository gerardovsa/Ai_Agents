# Module Manifest Schema V3.0
## JSON Schema for Validation & Developer Reference

This document defines the complete JSON schema for module manifest files and provides validation examples.

---

## 📋 Complete Schema Definition

See `tools/schemas/module_manifest_schema.json` for the actual JSON schema file.

---

## ✅ Validation Examples

### Python Validation

```python
import json
import jsonschema

def validate_manifest(manifest_path):
    """Validate module manifest against V3 schema"""
    schema_path = "tools/schemas/module_manifest_schema.json"
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    with open(schema_path) as f:
        schema = json.load(f)
    
    try:
        jsonschema.validate(instance=manifest, schema=schema)
        print(f"✅ {manifest_path} is valid")
        return True, None
    except jsonschema.ValidationError as e:
        print(f"❌ {manifest_path} validation failed:")
        print(f"   Path: {'.'.join(str(p) for p in e.path)}")
        print(f"   Error: {e.message}")
        return False, e.message

# Usage
validate_manifest("UI/modules_internal/settings/manifest.json")
```

### JavaScript/Node.js Validation

```javascript
import Ajv from 'ajv';
import fs from 'fs';

function validateManifest(manifestPath) {
  const schemaPath = 'tools/schemas/module_manifest_schema.json';
  const ajv = new Ajv({ allErrors: true });
  
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
  
  const validate = ajv.compile(schema);
  const valid = validate(manifest);
  
  if (valid) {
    console.log(`✅ ${manifestPath} is valid`);
    return { valid: true };
  } else {
    console.log(`❌ ${manifestPath} validation failed:`);
    validate.errors.forEach(err => {
      console.log(`   ${err.instancePath} ${err.message}`);
    });
    return { valid: false, errors: validate.errors };
  }
}

// Usage
validateManifest('UI/modules_internal/settings/manifest.json');
```

---

## 🔍 Business Logic Validation

Beyond schema validation, these rules must also be enforced:

### Rule 1: Capability Consistency

```javascript
function validateCapabilities(manifest) {
  const { capabilities } = manifest;
  
  // If sidebar enabled, position is required
  if (capabilities.sidebar.enabled && !capabilities.sidebar.position) {
    throw new Error("sidebar.position required when sidebar.enabled=true");
  }
  
  // If dashboard enabled with html_file, file must exist
  if (capabilities.dashboard.enabled && capabilities.dashboard.html_file) {
    const htmlPath = `UI/modules_${manifest.type}/${manifest.id}/${capabilities.dashboard.html_file}`;
    if (!fs.existsSync(htmlPath)) {
      throw new Error(`Dashboard HTML not found: ${htmlPath}`);
    }
  }
  
  // At least one capability must be enabled
  if (!capabilities.dashboard.enabled && !capabilities.sidebar.enabled) {
    throw new Error("Module must have at least one capability (dashboard or sidebar)");
  }
}
```

### Rule 2: Loading Dependencies

```javascript
function validateDependencies(manifest, allModules) {
  const { loading } = manifest;
  
  // Check all dependencies exist
  if (loading.dependencies) {
    for (const depId of loading.dependencies) {
      if (!allModules.find(m => m.id === depId)) {
        throw new Error(`Dependency not found: ${depId}`);
      }
    }
  }
  
  // Check for circular dependencies
  const visited = new Set();
  const stack = new Set();
  
  function hasCycle(moduleId) {
    if (stack.has(moduleId)) return true;
    if (visited.has(moduleId)) return false;
    
    visited.add(moduleId);
    stack.add(moduleId);
    
    const module = allModules.find(m => m.id === moduleId);
    if (module && module.loading.dependencies) {
      for (const depId of module.loading.dependencies) {
        if (hasCycle(depId)) return true;
      }
    }
    
    stack.delete(moduleId);
    return false;
  }
  
  if (hasCycle(manifest.id)) {
    throw new Error(`Circular dependency detected for module: ${manifest.id}`);
  }
}
```

### Rule 3: Credentials Configuration

```javascript
function validateCredentials(manifest) {
  const { credentials } = manifest;
  
  if (credentials && credentials.required) {
    // Must specify fallback behavior
    if (!credentials.fallback_behavior) {
      throw new Error("fallback_behavior required when credentials.required=true");
    }
    
    // Must specify platforms or oauth_scopes
    if ((!credentials.platforms || credentials.platforms.length === 0) &&
        (!credentials.oauth_scopes || credentials.oauth_scopes.length === 0)) {
      throw new Error("Must specify platforms or oauth_scopes when credentials required");
    }
  }
}
```

### Rule 4: Module Type Restrictions

```javascript
function validateModuleType(manifest) {
  const { type, loading, credentials } = manifest;
  
  if (type === "internal") {
    // Internal modules cannot require platform credentials
    if (credentials && credentials.platforms && credentials.platforms.length > 0) {
      throw new Error("Internal modules cannot require platform credentials");
    }
    
    // Internal modules must load at startup
    if (loading.strategy !== "startup") {
      throw new Error("Internal modules must use loading.strategy='startup'");
    }
    
    // Internal modules should have low priority (1-50)
    if (loading.priority > 50) {
      console.warn(`Warning: Internal module ${manifest.id} has priority > 50`);
    }
  }
  
  if (type === "external") {
    // External modules should have higher priority (51-100)
    if (loading.priority < 51) {
      console.warn(`Warning: External module ${manifest.id} has priority < 51`);
    }
  }
}
```

### Rule 5: Sidebar Button Consistency

```javascript
function validateSidebarButton(manifest) {
  const { sidebar_button, icon } = manifest;
  
  if (sidebar_button.enabled) {
    // Must have icon and label
    if (!sidebar_button.icon || !sidebar_button.label) {
      throw new Error("icon and label required when sidebar_button.enabled=true");
    }
    
    // Position must be positive integer
    if (!Number.isInteger(sidebar_button.position) || sidebar_button.position < 1) {
      throw new Error("sidebar_button.position must be positive integer");
    }
  }
}
```

---

## 🛠️ Complete Validation Function

```javascript
async function validateModuleManifest(manifestPath, allManifests = []) {
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const errors = [];
  const warnings = [];
  
  try {
    // 1. JSON Schema Validation
    const schemaResult = validateManifestSchema(manifest);
    if (!schemaResult.valid) {
      errors.push(...schemaResult.errors.map(e => e.message));
    }
    
    // 2. Capability Validation
    try {
      validateCapabilities(manifest);
    } catch (e) {
      errors.push(e.message);
    }
    
    // 3. Dependencies Validation
    if (allManifests.length > 0) {
      try {
        validateDependencies(manifest, allManifests);
      } catch (e) {
        errors.push(e.message);
      }
    }
    
    // 4. Credentials Validation
    try {
      validateCredentials(manifest);
    } catch (e) {
      errors.push(e.message);
    }
    
    // 5. Module Type Validation
    try {
      validateModuleType(manifest);
    } catch (e) {
      errors.push(e.message);
    }
    
    // 6. Sidebar Button Validation
    try {
      validateSidebarButton(manifest);
    } catch (e) {
      errors.push(e.message);
    }
    
    // 7. File Existence Checks
    const moduleDir = `UI/modules_${manifest.type}/${manifest.id}`;
    
    // Check script files exist
    if (manifest.assets && manifest.assets.scripts) {
      for (const script of manifest.assets.scripts) {
        const scriptPath = `${moduleDir}/${script.path}`;
        if (!fs.existsSync(scriptPath)) {
          errors.push(`Script file not found: ${scriptPath}`);
        }
      }
    }
    
    // Check style files exist
    if (manifest.assets && manifest.assets.styles) {
      for (const style of manifest.assets.styles) {
        const stylePath = `${moduleDir}/${style.path}`;
        if (!fs.existsSync(stylePath)) {
          errors.push(`Style file not found: ${stylePath}`);
        }
      }
    }
    
    // Report results
    if (errors.length > 0) {
      console.log(`\n❌ ${manifestPath} validation FAILED`);
      errors.forEach(err => console.log(`   - ${err}`));
      return { valid: false, errors, warnings };
    }
    
    if (warnings.length > 0) {
      console.log(`\n⚠️  ${manifestPath} has warnings:`);
      warnings.forEach(warn => console.log(`   - ${warn}`));
    }
    
    console.log(`\n✅ ${manifestPath} validation PASSED`);
    return { valid: true, errors: [], warnings };
    
  } catch (e) {
    console.error(`\n💥 Unexpected error validating ${manifestPath}:`, e.message);
    return { valid: false, errors: [e.message], warnings };
  }
}
```

---

## 📊 Validation Report Example

```
=== Module Manifest Validation Report ===

Validating: UI/modules_internal/settings/manifest.json
✅ JSON Schema: PASS
✅ Capabilities: PASS
✅ Dependencies: PASS
✅ Credentials: PASS
✅ Module Type: PASS
✅ Sidebar Button: PASS
✅ File Existence: PASS

Result: ✅ VALID

---

Validating: UI/modules_external/inhouse-kanban/manifest.json
✅ JSON Schema: PASS
✅ Capabilities: PASS
✅ Dependencies: PASS
✅ Credentials: PASS
⚠️  Module Type: WARNING - Priority 50 is borderline for external module
✅ Sidebar Button: PASS
❌ File Existence: FAIL
   - Script file not found: UI/modules_external/inhouse-kanban/kanban-v3.js
   - Style file not found: UI/modules_external/inhouse-kanban/kanban.css

Result: ❌ INVALID (1 error, 1 warning)

---

Summary:
- Total Modules: 15
- Valid: 12
- Invalid: 3
- Warnings: 5
```

---

## 🚀 CLI Validation Tool

```bash
# Validate single manifest
node tools/validate-manifest.js UI/modules_internal/settings/manifest.json

# Validate all manifests
node tools/validate-manifest.js --all

# Validate and fix common issues
node tools/validate-manifest.js --all --fix

# Generate validation report
node tools/validate-manifest.js --all --report validation-report.json
```

---

**Schema Version:** 3.0.0  
**Document Version:** 1.0.0  
**Last Updated:** November 29, 2025  
**Status:** ✅ Ready for Use  
**Related:** `MODULE_SYSTEM_ARCHITECTURE_V3.md`

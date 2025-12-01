"""
Module Analyzer CLI Tool
Comprehensive analysis of module architecture, integrations, and V3.0 compliance

Usage:
    python scripts/testing/module_analyzer.py <module_folder_path> [options]
    python scripts/testing/module_analyzer.py UI/modules_external/inhouse-kanban
    python scripts/testing/module_analyzer.py UI/modules_external/inhouse-kanban --test-endpoints
    python scripts/testing/module_analyzer.py UI/modules_external/inhouse-kanban --endpoints /api/test,/api/health

Features:
- V3.0 manifest compliance checking
- Architecture pattern detection (Architecture 1 vs 2)
- Sidebar integration analysis
- API endpoint detection
- Live API endpoint testing (optional)
- UI rendering validation
- Connection/integration mapping
- File structure analysis
- Documentation coverage
- Best practices validation

Options:
    --test-endpoints         Enable live API endpoint testing
    --endpoints <list>       Comma-separated list of endpoints to test
    --base-url <url>         Base URL for API testing (default: http://localhost:5001)
    --token <token>          Authentication token for API requests
    --timeout <seconds>      Request timeout (default: 5)
    --output <path>          Custom output file path
"""

import os
import sys
import json
import re
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error


class ModuleAnalyzer:
    """Analyzes module architecture and compliance"""
    
    def __init__(self, module_path: str, test_endpoints: bool = False, 
                 endpoints: List[str] = None, base_url: str = "http://localhost:5001",
                 auth_token: str = None, timeout: int = 5):
        self.module_path = Path(module_path).resolve()
        self.module_name = self.module_path.name
        self.manifest = None
        self.issues = []
        self.warnings = []
        self.recommendations = []
        self.metrics = {}
        
        # API testing configuration
        self.test_endpoints = test_endpoints
        self.custom_endpoints = endpoints or []
        self.base_url = base_url
        self.auth_token = auth_token
        self.timeout = timeout
        
    def analyze(self) -> Dict:
        """Run complete analysis"""
        print(f"\n{'='*80}")
        print(f"MODULE ANALYZER - V3.0 Compliance & Architecture Analysis")
        print(f"{'='*80}\n")
        print(f"Module: {self.module_name}")
        print(f"Path: {self.module_path}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if not self.module_path.exists():
            print(f"ERROR: Module path does not exist: {self.module_path}")
            return {"success": False, "error": "Module path not found"}
        
        # Run all analysis checks
        print("Running analysis checks...\n")
        
        results = {
            "module_name": self.module_name,
            "module_path": str(self.module_path),
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "file_structure": self._check_file_structure(),
                "manifest_compliance": self._check_manifest_compliance(),
                "dependencies_validation": self._check_dependencies_validation(),
                "html_path_validation": self._check_html_path_validation(),
                "es6_v4_compliance": self._check_es6_v4_compliance(),
                "architecture_pattern": self._detect_architecture_pattern(),
                "sidebar_integration": self._check_sidebar_integration(),
                "api_endpoints": self._detect_api_endpoints(),
                "api_endpoint_testing": self._test_api_endpoints(),
                "authentication_pattern": self._check_authentication_pattern(),
                "ui_rendering": self._check_ui_rendering(),
                "runtime_diagnostic": self._check_runtime_diagnostic(),
                "module_registry_compat": self._check_module_registry_compatibility(),
                "connections": self._detect_connections(),
                "documentation": self._check_documentation(),
                "best_practices": self._check_best_practices(),
                "duplicate_declarations": self._check_duplicate_declarations()
            },
            "issues": self.issues,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "metrics": self.metrics,
            "compliance_score": 0
        }
        
        # Calculate compliance score
        results["compliance_score"] = self._calculate_compliance_score(results)
        
        # Print results
        self._print_results(results)
        
        return results
    
    def _check_file_structure(self) -> Dict:
        """Analyze module file structure"""
        print("1. Checking file structure...")
        
        files = {
            "manifest": None,
            "javascript": [],
            "css": [],
            "html": [],
            "docs": [],
            "backups": [],
            "test_files": []
        }
        
        for item in self.module_path.iterdir():
            if item.is_file():
                name = item.name.lower()
                
                if name == "manifest.json":
                    files["manifest"] = item
                elif name.endswith(".js"):
                    if "test" in name or "diagnostic" in name:
                        files["test_files"].append(item)
                    elif "backup" in name or "copy" in name:
                        files["backups"].append(item)
                    else:
                        files["javascript"].append(item)
                elif name.endswith(".css"):
                    if "backup" in name:
                        files["backups"].append(item)
                    else:
                        files["css"].append(item)
                elif name.endswith(".html"):
                    files["html"].append(item)
                elif name.endswith(".md"):
                    files["docs"].append(item)
        
        # Analysis
        result = {
            "has_manifest": files["manifest"] is not None,
            "js_files": len(files["javascript"]),
            "css_files": len(files["css"]),
            "html_files": len(files["html"]),
            "doc_files": len(files["docs"]),
            "backup_files": len(files["backups"]),
            "test_files": len(files["test_files"]),
            "status": "PASS"
        }
        
        # Issues
        if not files["manifest"]:
            self.issues.append("CRITICAL: manifest.json not found")
            result["status"] = "FAIL"
        
        if result["js_files"] == 0:
            self.issues.append("CRITICAL: No JavaScript files found")
            result["status"] = "FAIL"
        
        if len(files["backups"]) > 3:
            self.warnings.append(f"Multiple backup files found ({len(files['backups'])}), consider cleanup")
        
        if len(files["docs"]) > 5:
            self.recommendations.append(f"Many documentation files ({len(files['docs'])}), consider consolidation")
        
        print(f"   Manifest: {'SUCCESS Found' if result['has_manifest'] else 'ERROR  Missing'}")
        print(f"   JavaScript: {result['js_files']} files")
        print(f"   CSS: {result['css_files']} files")
        print(f"   HTML: {result['html_files']} files")
        print(f"   Docs: {result['doc_files']} files")
        print(f"   Status: {result['status']}\n")
        
        return result
    
    def _check_manifest_compliance(self) -> Dict:
        """Check manifest V3.0 compliance"""
        print("2. Checking manifest V3.0 compliance...")
        
        manifest_path = self.module_path / "manifest.json"
        if not manifest_path.exists():
            print("   ERROR  Manifest not found\n")
            return {"status": "FAIL", "version": "none"}
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                self.manifest = json.load(f)
        except json.JSONDecodeError as e:
            self.issues.append(f"CRITICAL: Invalid JSON in manifest.json: {e}")
            print(f"   ERROR  Invalid JSON: {e}\n")
            return {"status": "FAIL", "version": "invalid"}
        
        # V3.0 required fields
        v3_required = ["id", "name", "version", "type", "category"]
        v3_optional = ["loading", "capabilities", "sidebar_button"]
        
        # Check required fields
        missing_required = [f for f in v3_required if f not in self.manifest]
        has_optional = [f for f in v3_optional if f in self.manifest]
        
        # Determine version
        if "type" in self.manifest and "category" in self.manifest:
            version = "3.0"
        elif "scriptPath" in self.manifest:
            version = "2.x"
        else:
            version = "1.x"
        
        result = {
            "version": version,
            "has_all_required": len(missing_required) == 0,
            "missing_required": missing_required,
            "has_optional": has_optional,
            "capabilities_defined": "capabilities" in self.manifest,
            "status": "PASS" if len(missing_required) == 0 else "FAIL"
        }
        
        # Issues
        if missing_required:
            self.issues.append(f"V3.0 missing required fields: {', '.join(missing_required)}")
        
        if version != "3.0":
            self.warnings.append(f"Manifest is {version}, should be V3.0")
            self.recommendations.append("Upgrade manifest to V3.0 schema")
        
        # Check capabilities structure
        if "capabilities" in self.manifest:
            caps = self.manifest["capabilities"]
            if "dashboard" in caps:
                if not isinstance(caps["dashboard"], dict):
                    self.issues.append("capabilities.dashboard should be an object with 'enabled' field")
            if "sidebar" in caps:
                if not isinstance(caps["sidebar"], dict):
                    self.issues.append("capabilities.sidebar should be an object with 'enabled', 'position' fields")
        
        print(f"   Version: {version}")
        print(f"   Required fields: {'SUCCESS Complete' if result['has_all_required'] else 'ERROR  Missing: ' + ', '.join(missing_required)}")
        print(f"   Capabilities: {'SUCCESS Defined' if result['capabilities_defined'] else 'WARNING Not defined'}")
        print(f"   Status: {result['status']}\n")
        
        return result
    
    def _check_dependencies_validation(self) -> Dict:
        """Validate dependencies structure for module registry compatibility"""
        print("2a. Validating dependencies structure...")
        
        if not self.manifest:
            print("   SKIP   No manifest loaded\n")
            return {"status": "SKIP", "message": "No manifest loaded"}
        
        dependencies = self.manifest.get('dependencies')
        issues = []
        warnings = []
        
        if dependencies is None:
            print("   WARN   No dependencies field\n")
            return {
                "status": "WARN",
                "dependencies": None,
                "message": "No dependencies field in manifest",
                "issues": ["Missing dependencies field - should be dict or list"]
            }
        
        # Check format (dict or list)
        if isinstance(dependencies, dict):
            # Modern format: {"utilities": [...], "frameworks": [...], "modules": [...]}
            format_type = "dict (modern)"
            
            # Validate structure
            expected_keys = ['utilities', 'frameworks', 'modules']
            present_keys = [k for k in expected_keys if k in dependencies]
            
            if not present_keys:
                issues.append("Dependencies dict exists but has no standard keys (utilities/frameworks/modules)")
            
            # Check if values are lists
            for key, value in dependencies.items():
                if not isinstance(value, list):
                    issues.append(f"dependencies.{key} should be a list, got {type(value).__name__}")
                elif key == 'modules' and value:
                    # Check for dict items in modules list (causes unhashable error)
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            issues.append(f"dependencies.modules[{i}] is dict - should be string. This causes 'unhashable type: dict' error!")
        
        elif isinstance(dependencies, list):
            # Legacy format: ["module1", "module2"]
            format_type = "list (legacy)"
            
            # Check all items are strings
            for i, item in enumerate(dependencies):
                if isinstance(item, dict):
                    issues.append(f"dependencies[{i}] is dict - should be string. This causes 'unhashable type: dict' error!")
                elif not isinstance(item, str):
                    issues.append(f"dependencies[{i}] is {type(item).__name__} - should be string")
        else:
            format_type = f"{type(dependencies).__name__} (invalid)"
            issues.append(f"dependencies must be dict or list, got {type(dependencies).__name__}")
        
        status = "ERROR" if issues else "PASS"
        
        print(f"   Format: {format_type}")
        print(f"   Issues: {len(issues)}")
        print(f"   Status: {status}\n")
        
        return {
            "status": status,
            "format": format_type,
            "dependencies": dependencies,
            "issues": issues,
            "warnings": warnings,
            "message": "Dependencies format valid" if not issues else "Dependencies format has issues"
        }
    
    def _check_html_path_validation(self) -> Dict:
        """
        Validate HTML file paths in manifest match actual files
        CRITICAL CHECK - Prevents 404 errors and failed module loading
        """
        print("3. Validating HTML file paths (CRITICAL)...")
        
        result = {
            "html_file_exists": False,
            "html_path_exists": False,
            "html_file_value": None,
            "html_path_value": None,
            "actual_html_files": [],
            "path_mismatches": [],
            "recommendations": [],
            "status": "UNKNOWN"
        }
        
        # Get actual HTML files
        html_files = list(self.module_path.glob("*.html"))
        result["actual_html_files"] = [f.name for f in html_files]
        
        if not self.manifest:
            result["status"] = "NO_MANIFEST"
            return result
        
        # Check manifest html_file field
        html_file = self.manifest.get("html_file")
        result["html_file_value"] = html_file
        
        if html_file:
            html_file_path = self.module_path / html_file
            result["html_file_exists"] = html_file_path.exists()
            
            if not result["html_file_exists"]:
                result["path_mismatches"].append({
                    "field": "html_file",
                    "value": html_file,
                    "exists": False
                })
                self.issues.append(
                    f"CRITICAL: manifest.json 'html_file' points to non-existent file: {html_file}"
                )
                result["recommendations"].append(
                    f"Fix manifest.json: 'html_file' should be one of: {', '.join(result['actual_html_files'])}"
                )
        
        # Check manifest htmlPath field (used by module_loader.js)
        html_path = None
        if "sidebar" in self.manifest and isinstance(self.manifest["sidebar"], dict):
            html_path = self.manifest["sidebar"].get("htmlPath")
        if not html_path and "capabilities" in self.manifest:
            caps = self.manifest["capabilities"]
            if isinstance(caps, dict) and "sidebar" in caps:
                if isinstance(caps["sidebar"], dict):
                    html_path = caps["sidebar"].get("htmlPath")
        
        result["html_path_value"] = html_path
        
        if html_path:
            # htmlPath can be relative to UI folder or module folder
            # Check common patterns
            possible_paths = [
                self.module_path / html_path,  # Direct relative
                self.module_path / Path(html_path).name,  # Just filename
                Path("UI") / html_path,  # UI-relative
            ]
            
            result["html_path_exists"] = any(p.exists() for p in possible_paths if p != Path("."))
            
            if not result["html_path_exists"]:
                result["path_mismatches"].append({
                    "field": "htmlPath",
                    "value": html_path,
                    "exists": False
                })
                self.issues.append(
                    f"CRITICAL: manifest.json 'htmlPath' points to non-existent file: {html_path}"
                )
                
                # Extract filename from path
                html_filename = Path(html_path).name
                if html_filename in result["actual_html_files"]:
                    # Found file but path is wrong - detect module type
                    module_path_str = str(self.module_path)
                    
                    if "modules_internal" in module_path_str:
                        # Internal module (transcription, automation, etc.)
                        correct_path = f"modules_internal/{self.module_name}/{html_filename}"
                    elif "modules_external" in module_path_str:
                        # External module (inhouse-kanban, communication-hub, etc.)
                        correct_path = f"external/modules/{self.module_name}/{html_filename}"
                    else:
                        # Fallback - try to detect from manifest category
                        correct_path = f"modules/{self.module_name}/{html_filename}"
                    
                    result["recommendations"].append(
                        f"Fix manifest.json: Change 'htmlPath' from '{html_path}' to '{correct_path}'"
                    )
                    self.issues.append(
                        f"CRITICAL: HTML file exists but path is wrong! File: {html_filename}, Wrong path: {html_path}"
                    )
                else:
                    result["recommendations"].append(
                        f"Fix manifest.json: 'htmlPath' should point to one of: {', '.join(result['actual_html_files'])}"
                    )
        
        # Determine status
        if len(result["path_mismatches"]) > 0:
            result["status"] = "CRITICAL"
            self.issues.append(
                f"HTML path validation FAILED - Module will fail to load with 404 errors!"
            )
            result["recommendations"].append(
                "CRITICAL FIX REQUIRED: Update manifest.json paths to match actual HTML files"
            )
        elif html_file and result["html_file_exists"]:
            result["status"] = "PASS"
        elif html_path and result["html_path_exists"]:
            result["status"] = "PASS"
        elif len(result["actual_html_files"]) > 0:
            result["status"] = "WARNING"
            self.warnings.append("HTML files exist but not declared in manifest.json")
            result["recommendations"].append("Add 'html_file' or 'htmlPath' to manifest.json")
        else:
            result["status"] = "NO_HTML"
            self.warnings.append("No HTML files found - module may use programmatic UI generation")
        
        # Print results
        print(f"   Actual HTML files: {len(result['actual_html_files'])}")
        if result["actual_html_files"]:
            for html in result["actual_html_files"]:
                print(f"      - {html}")
        
        print(f"   Manifest 'html_file': {html_file or 'Not specified'}")
        if html_file:
            print(f"      File exists: {'✅' if result['html_file_exists'] else '❌ CRITICAL'}")
        
        print(f"   Manifest 'htmlPath': {html_path or 'Not specified'}")
        if html_path:
            print(f"      Path exists: {'✅' if result['html_path_exists'] else '❌ CRITICAL'}")
        
        if result["path_mismatches"]:
            print(f"   CRITICAL Path mismatches: {len(result['path_mismatches'])}")
            for mismatch in result["path_mismatches"]:
                print(f"      ❌ {mismatch['field']}: '{mismatch['value']}' → File not found!")
        
        print(f"   Status: {result['status']}\n")
        
        return result
    
    def _check_es6_v4_compliance(self) -> Dict:
        """Check if module is ES6/Modern Framework V4 compliant"""
        print("3a. Checking ES6 / Modern Framework V4 compliance...")
        
        result = {
            "pattern": "unknown",
            "es6_compliant": False,
            "v4_ready": False,
            "legacy_compatible": True,
            "has_export_default": False,
            "has_composition": False,
            "has_lifecycle_hooks": [],
            "extends_base_module": False,
            "is_class_based": False,
            "manifest_framework": None,
            "migration_needed": [],
            "migration_steps": [],
            "status": "UNKNOWN"
        }
        
        js_files = [f for f in self.module_path.glob("*.js") 
                    if "test" not in f.name.lower() and "backup" not in f.name.lower() 
                    and "verify" not in f.name.lower()]
        
        if not js_files:
            print("   SKIP   No JavaScript files found\n")
            return result
        
        # Prefer main module file (matches module folder name) or first JS file
        module_name = self.module_path.name
        main_js = None
        for js_file in js_files:
            if js_file.stem == module_name or js_file.stem == module_name.replace('-', '_'):
                main_js = js_file
                break
        if not main_js:
            main_js = js_files[0]
        
        print(f"   Checking: {main_js.name}")
        
        try:
            content = main_js.read_text(encoding='utf-8')
            
            # Check for ES6 export patterns (handles both inline and newline)
            result["has_export_default"] = bool(re.search(r'export\s+default\s*\{', content, re.MULTILINE))
            
            # Check for Modern Framework V4 patterns
            result["has_composition"] = bool(re.search(r'Object\.assign\(this,\s*utilities\)', content))
            
            # Check lifecycle hooks (handles both with and without async)
            lifecycle_hooks = ['onLoad', 'onDashboardLoad', 'onSidebarLoad', 'onUnload']
            for hook in lifecycle_hooks:
                # Match: onLoad(utilities), async onLoad(utilities), onLoad (utilities), etc.
                if re.search(rf'(async\s+)?{hook}\s*\(\s*utilities\s*\)', content, re.MULTILINE):
                    result["has_lifecycle_hooks"].append(hook)
            
            # Check for Legacy patterns (bad)
            result["extends_base_module"] = bool(re.search(r'class\s+\w+\s+extends\s+BaseModule', content))
            result["is_class_based"] = bool(re.search(r'class\s+\w+\s*\{', content)) and not result["has_export_default"]
            
            # Check manifest for framework declaration
            if self.manifest and "loading" in self.manifest:
                result["manifest_framework"] = self.manifest["loading"].get("framework")
            
            # Determine pattern and compliance
            if result["extends_base_module"]:
                result["pattern"] = "Legacy (BaseModule inheritance)"
                result["es6_compliant"] = False
                result["v4_ready"] = False
                result["legacy_compatible"] = True
                result["status"] = "NEEDS_MIGRATION"
                
                self.issues.append("Module uses legacy BaseModule pattern - must migrate to Modern Framework V4 for ES6")
                result["migration_needed"].append("Remove BaseModule inheritance")
                result["migration_needed"].append("Convert class to export default object")
                result["migration_needed"].append("Add lifecycle hooks (onLoad, onDashboardLoad)")
                result["migration_needed"].append("Add Object.assign(this, utilities)")
                
            elif result["has_export_default"] and result["has_composition"] and len(result["has_lifecycle_hooks"]) > 0:
                result["pattern"] = "Modern Framework V4 (ES6 composition)"
                result["es6_compliant"] = True
                result["v4_ready"] = True
                result["legacy_compatible"] = result["manifest_framework"] != "v4"  # Can run on legacy if not explicitly v4
                result["status"] = "READY"
                
                if result["manifest_framework"] == "v4":
                    print("   SUCCESS Module is ES6 V4 compliant and configured!")
                else:
                    self.recommendations.append("Module is V4 ready! Add 'loading.framework: v4' to manifest to enable ES6 loading")
                
            elif result["has_export_default"]:
                result["pattern"] = "Partial ES6 (export default only)"
                result["es6_compliant"] = True
                result["v4_ready"] = False
                result["legacy_compatible"] = True
                result["status"] = "PARTIAL"
                
                self.warnings.append("Module uses export default but missing Modern Framework V4 patterns")
                
                if not result["has_composition"]:
                    result["migration_needed"].append("Add Object.assign(this, utilities) in lifecycle hooks")
                
                if len(result["has_lifecycle_hooks"]) == 0:
                    result["migration_needed"].append("Add lifecycle hooks: onLoad(utilities) or onDashboardLoad(utilities)")
                else:
                    # Has some hooks but maybe not utilities parameter
                    result["migration_needed"].append("Ensure all lifecycle hooks accept 'utilities' parameter")
                
            elif result["is_class_based"]:
                result["pattern"] = "Class-based (non-BaseModule)"
                result["es6_compliant"] = False
                result["v4_ready"] = False
                result["legacy_compatible"] = True
                result["status"] = "NEEDS_REFACTOR"
                
                self.warnings.append("Module uses class pattern - should convert to export default object for V4")
                result["migration_needed"].append("Convert class to export default object")
                result["migration_needed"].append("Add lifecycle hooks (onLoad, onDashboardLoad)")
                result["migration_needed"].append("Add Object.assign(this, utilities)")
                
            else:
                result["pattern"] = "Unknown pattern"
                result["es6_compliant"] = False
                result["v4_ready"] = False
                result["legacy_compatible"] = True
                result["status"] = "UNKNOWN"
            
            # Generate migration steps if needed
            if result["migration_needed"]:
                result["migration_steps"] = self._generate_migration_steps(result)
            
            # Print summary
            print(f"   Pattern: {result['pattern']}")
            print(f"   ES6 Compliant: {'YES' if result['es6_compliant'] else 'NO'}")
            print(f"   V4 Ready: {'YES' if result['v4_ready'] else 'NO'}")
            print(f"   Legacy Compatible: {'YES' if result['legacy_compatible'] else 'NO'}")
            print(f"   Export default: {'YES' if result['has_export_default'] else 'NO'}")
            print(f"   Composition: {'YES' if result['has_composition'] else 'NO'}")
            print(f"   Lifecycle hooks: {', '.join(result['has_lifecycle_hooks']) if result['has_lifecycle_hooks'] else 'None'}")
            print(f"   Manifest framework: {result['manifest_framework'] or 'Not specified'}")
            print(f"   Status: {result['status']}")
            
            if result["migration_needed"]:
                print(f"   Migration needed: {len(result['migration_needed'])} items")
                for item in result["migration_needed"]:
                    print(f"      - {item}")
            
            print()
            
        except Exception as e:
            print(f"   ERROR  Failed to analyze: {e}\n")
            result["status"] = "ERROR"
        
        return result
    
    def _generate_migration_steps(self, es6_check: Dict) -> list:
        """Generate detailed migration steps based on ES6 compliance check"""
        steps = []
        
        if es6_check["extends_base_module"]:
            steps.append({
                "step": 1,
                "title": "Remove BaseModule inheritance",
                "before": "class MyModule extends BaseModule { ... }",
                "after": "// Remove class declaration",
                "description": "BaseModule inheritance prevents ES6 module loading"
            })
        
        if not es6_check["has_export_default"]:
            steps.append({
                "step": len(steps) + 1,
                "title": "Convert to export default object",
                "before": "class MyModule { ... }",
                "after": "export default { state: { ... }, async onLoad(utilities) { ... } }",
                "description": "ES6 modules require export default for Modern Framework V4"
            })
        
        if not es6_check["has_composition"]:
            steps.append({
                "step": len(steps) + 1,
                "title": "Add utility composition",
                "before": "async onLoad() { this.container = ...; }",
                "after": "async onLoad(utilities) { Object.assign(this, utilities); this.container = this.dom.getContainer(); }",
                "description": "Utilities must be explicitly injected via composition"
            })
        
        if len(es6_check["has_lifecycle_hooks"]) == 0:
            steps.append({
                "step": len(steps) + 1,
                "title": "Add lifecycle hooks",
                "before": "async initialize() { ... }",
                "after": "async onDashboardLoad(utilities) { Object.assign(this, utilities); ... }",
                "description": "Modern Framework V4 uses lifecycle hooks instead of initialize()"
            })
        
        if es6_check["v4_ready"] and not es6_check["manifest_framework"]:
            steps.append({
                "step": len(steps) + 1,
                "title": "Update manifest to enable V4 loading",
                "before": '"loading": { "strategy": "lazy" }',
                "after": '"loading": { "strategy": "lazy", "framework": "v4" }',
                "description": "Add framework: v4 to enable ES6 dynamic import loading"
            })
        
        return steps
    
    def _detect_architecture_pattern(self) -> Dict:
        """Detect if module uses Architecture 1 or 2"""
        print("4. Detecting architecture pattern...")
        
        js_files = list(self.module_path.glob("*.js"))
        html_files = list(self.module_path.glob("*.html"))
        
        # Exclude test/backup files
        js_files = [f for f in js_files if "test" not in f.name.lower() and "backup" not in f.name.lower()]
        
        architecture = "unknown"
        confidence = 0
        
        if len(js_files) > 0:
            # Check main JS file for HTML generation patterns
            main_js = None
            if self.manifest and "js_file" in self.manifest:
                main_js = self.module_path / self.manifest["js_file"]
            elif js_files:
                main_js = js_files[0]
            
            if main_js and main_js.exists():
                with open(main_js, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Architecture 2 indicators
                has_innerHTML = "innerHTML" in content
                has_template_literals = "``" in content or "`<" in content
                has_generate_html = "generateHTML" in content or "generate_html" in content
                has_container_query = "getElementById" in content or "querySelector" in content
                
                # Architecture 1 indicators
                has_separate_html = len(html_files) > 0
                has_dom_manipulation = "appendChild" in content or "createElement" in content
                
                if has_innerHTML and has_template_literals and not has_separate_html:
                    architecture = "Architecture 2 (Inline HTML-in-JS)"
                    confidence = 90
                elif has_separate_html and has_dom_manipulation:
                    architecture = "Architecture 1 (Separate Files)"
                    confidence = 80
                elif has_innerHTML:
                    architecture = "Hybrid (Mixed approach)"
                    confidence = 60
        
        result = {
            "architecture": architecture,
            "confidence": confidence,
            "js_files": len(js_files),
            "html_files": len(html_files),
            "status": "PASS" if confidence > 50 else "UNKNOWN"
        }
        
        if architecture == "Architecture 2 (Inline HTML-in-JS)":
            self.recommendations.append("Architecture 2 detected - ensure getSubTabContainer() helper method exists")
        elif architecture == "Architecture 1 (Separate Files)":
            self.recommendations.append("Architecture 1 detected - verify HTML templates are properly structured")
        
        print(f"   Pattern: {architecture}")
        print(f"   Confidence: {confidence}%")
        print(f"   JS files: {result['js_files']}, HTML files: {result['html_files']}")
        print(f"   Status: {result['status']}\n")
        
        return result
    
    def _check_sidebar_integration(self) -> Dict:
        """Check if module uses SidebarManager framework"""
        print("4. Checking sidebar integration...")
        
        result = {
            "uses_sidebar": False,
            "uses_sidebar_manager": False,
            "custom_implementation": False,
            "sidebar_files": [],
            "recommendations": [],
            "status": "N/A"
        }
        
        # Check manifest
        if self.manifest:
            if "sidebar" in self.manifest:
                result["uses_sidebar"] = True
            if "capabilities" in self.manifest and "sidebar" in self.manifest["capabilities"]:
                if self.manifest["capabilities"]["sidebar"].get("enabled"):
                    result["uses_sidebar"] = True
        
        # Check for sidebar HTML files
        sidebar_html = [f for f in self.module_path.glob("*sidebar*.html")]
        result["sidebar_files"] = [f.name for f in sidebar_html]
        
        # Check JS files for SidebarManager usage
        js_files = [f for f in self.module_path.glob("*.js") if "test" not in f.name.lower()]
        
        for js_file in js_files:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for SidebarManager.register usage
            if "SidebarManager.register" in content:
                result["uses_sidebar_manager"] = True
                
                # Check if toggleButtonId is provided
                register_pattern = r"SidebarManager\.register\(\{([^}]+)\}\)"
                matches = re.findall(register_pattern, content, re.DOTALL)
                
                has_toggle_button_id = False
                for match in matches:
                    if "toggleButtonId" in match:
                        has_toggle_button_id = True
                        # Extract the toggleButtonId value
                        toggle_id_pattern = r"toggleButtonId:\s*['\"]([^'\"]+)['\"]"
                        toggle_match = re.search(toggle_id_pattern, match)
                        if toggle_match:
                            toggle_id = toggle_match.group(1)
                            # Check if it follows naming convention
                            expected_toggle_id = f"{self.module_name}-floating-toggle"
                            if toggle_id != expected_toggle_id:
                                self.warnings.append(
                                    f"Sidebar toggle button ID is '{toggle_id}' but should be '{expected_toggle_id}'"
                                )
                                result["recommendations"].append(
                                    f"Change toggleButtonId to '{expected_toggle_id}' to match ModuleLoader convention"
                                )
                
                if not has_toggle_button_id and "floating_toggle" in str(self.manifest):
                    self.issues.append(
                        "CRITICAL: Module has floating_toggle in manifest but SidebarManager.register() missing toggleButtonId parameter"
                    )
                    result["recommendations"].append(
                        f"Add toggleButtonId: '{self.module_name}-floating-toggle' to SidebarManager.register() call"
                    )
                    result["status"] = "INCOMPLETE"
                else:
                    result["status"] = "PASS"
                break
            elif "sidebar" in content.lower() and "class" in content:
                result["custom_implementation"] = True
                result["status"] = "CUSTOM"
        
        # Analysis
        if result["uses_sidebar"] and not result["uses_sidebar_manager"] and not result["custom_implementation"]:
            self.warnings.append("Sidebar declared in manifest but no implementation found")
            result["status"] = "INCOMPLETE"
        
        if result["uses_sidebar"] and result["custom_implementation"] and not result["uses_sidebar_manager"]:
            self.recommendations.append("Sidebar uses custom implementation - consider migrating to SidebarManager framework")
        
        if result["uses_sidebar"] and result["uses_sidebar_manager"]:
            print(f"   SUCCESS Uses SidebarManager framework")
        elif result["uses_sidebar"] and result["custom_implementation"]:
            print(f"   WARNING Uses custom sidebar implementation")
        elif result["uses_sidebar"]:
            print(f"   ERROR  Sidebar declared but not implemented")
        else:
            print(f"   NOTICE No sidebar capability")
        
        if result["sidebar_files"]:
            print(f"   Sidebar files: {', '.join(result['sidebar_files'])}")
        print(f"   Status: {result['status']}\n")
        
        return result
    
    def _detect_api_endpoints(self) -> Dict:
        """Detect API endpoint connections"""
        print("6. Detecting API endpoints...")
        
        endpoints = {
            "fetch_calls": [],
            "api_routes": [],
            "backend_url": None
        }
        
        js_files = [f for f in self.module_path.glob("*.js") if "test" not in f.name.lower()]
        
        for js_file in js_files:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find fetch() calls
            fetch_pattern = r"fetch\(['\"]([^'\"]+)['\"]"
            matches = re.findall(fetch_pattern, content)
            endpoints["fetch_calls"].extend(matches)
            
            # Find API route definitions
            api_pattern = r"['\"]api['\"]:\s*['\"]([^'\"]+)['\"]"
            matches = re.findall(api_pattern, content)
            endpoints["api_routes"].extend(matches)
            
            # Find backend URL
            backend_pattern = r"backendUrl.*?['\"]([^'\"]+)['\"]"
            match = re.search(backend_pattern, content)
            if match:
                endpoints["backend_url"] = match.group(1)
        
        # Deduplicate
        endpoints["fetch_calls"] = list(set(endpoints["fetch_calls"]))
        endpoints["api_routes"] = list(set(endpoints["api_routes"]))
        
        result = {
            "total_endpoints": len(endpoints["fetch_calls"]),
            "api_routes": len(endpoints["api_routes"]),
            "has_backend_url": endpoints["backend_url"] is not None,
            "endpoints": endpoints["fetch_calls"][:10],  # First 10
            "status": "PASS" if len(endpoints["fetch_calls"]) > 0 else "NONE"
        }
        
        if result["total_endpoints"] == 0:
            self.warnings.append("No API endpoints detected - module may be static only")
        
        print(f"   Endpoints detected: {result['total_endpoints']}")
        if result["total_endpoints"] > 0:
            print(f"   Sample endpoints:")
            for endpoint in endpoints["fetch_calls"][:5]:
                print(f"      - {endpoint}")
        print(f"   Backend URL: {endpoints['backend_url'] or 'Not specified'}")
        print(f"   Status: {result['status']}\n")
        
        return result
    
    def _check_authentication_pattern(self) -> Dict:
        """Check for correct Flask authentication patterns in routes files"""
        print("5a. Checking authentication patterns in routes...")
        
        routes_dir = self.module_path / "routes"
        
        if not routes_dir.exists():
            print("   SKIP   No routes folder found\n")
            return {
                "status": "SKIP",
                "message": "No routes folder found",
                "has_routes": False
            }
        
        route_files = list(routes_dir.glob("*.py"))
        if not route_files:
            print("   SKIP   No Python route files found\n")
            return {
                "status": "SKIP",
                "message": "No Python route files found",
                "has_routes": False
            }
        
        issues = []
        warnings = []
        correct_patterns = 0
        incorrect_patterns = 0
        
        for route_file in route_files:
            try:
                content = route_file.read_text(encoding='utf-8')
                
                # Check for WRONG pattern: @auth_manager.require_auth
                wrong_pattern = re.findall(r'@auth_manager\.require_auth', content)
                if wrong_pattern:
                    incorrect_patterns += len(wrong_pattern)
                    issues.append({
                        "file": route_file.name,
                        "pattern": "@auth_manager.require_auth",
                        "count": len(wrong_pattern),
                        "fix": "Change to @require_auth (standalone function)"
                    })
                
                # Check for CORRECT pattern: @require_auth
                correct_pattern = re.findall(r'@require_auth(?!\w)', content)
                if correct_pattern:
                    correct_patterns += len(correct_pattern)
                
                # Check for correct import
                has_correct_import = bool(re.search(r'from .* import .*require_auth', content))
                if '@require_auth' in content or '@auth_manager.require_auth' in content:
                    if not has_correct_import:
                        warnings.append({
                            "file": route_file.name,
                            "issue": "Uses @require_auth but missing import statement",
                            "fix": "Add: from AI_infrastructure.auth.user_auth import UserAuthManager, require_auth"
                        })
            
            except Exception as e:
                warnings.append({"file": route_file.name, "error": str(e)})
        
        status = "ERROR" if incorrect_patterns > 0 else ("PASS" if correct_patterns > 0 else "SKIP")
        
        print(f"   Route files: {len(route_files)}")
        print(f"   Correct patterns: {correct_patterns}")
        print(f"   Incorrect patterns: {incorrect_patterns}")
        print(f"   Status: {status}\n")
        
        return {
            "status": status,
            "has_routes": True,
            "route_files": len(route_files),
            "correct_patterns": correct_patterns,
            "incorrect_patterns": incorrect_patterns,
            "issues": issues,
            "warnings": warnings,
            "message": f"Found {correct_patterns} correct, {incorrect_patterns} incorrect auth patterns"
        }
    
    def _check_ui_rendering(self) -> Dict:
        """Check UI rendering implementation with deep validation"""
        print("6. Checking UI rendering...")
        
        result = {
            "has_initialize": False,
            "has_render_method": False,
            "has_container_helper": False,
            "has_event_listeners": False,
            "render_implementation_valid": False,
            "render_calls_valid_methods": False,
            "undefined_method_calls": [],
            "container_id_mismatches": [],
            "rendering_issues": [],
            "status": "UNKNOWN"
        }
        
        js_files = [f for f in self.module_path.glob("*.js") if "test" not in f.name.lower() and "backup" not in f.name.lower()]
        
        all_defined_methods = set()
        all_called_methods = set()
        render_method_content = ""
        
        for js_file in js_files:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract all defined methods (both function declarations and arrow functions)
            method_patterns = [
                r'^\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{',  # Regular methods: methodName() {
                r'^\s*(?:async\s+)?(\w+)\s*=\s*\([^)]*\)\s*=>\s*\{',  # Arrow functions: methodName = () => {
                r'^\s*this\.(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*\{',  # this.methodName = () => {
            ]
            
            for pattern in method_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                all_defined_methods.update(matches)
            
            # Extract all method calls (this.methodName())
            call_pattern = r'this\.(\w+)\s*\('
            calls = re.findall(call_pattern, content)
            all_called_methods.update(calls)
            
            # Check for key methods
            if "async initialize()" in content or "initialize() {" in content or "initialize():" in content:
                result["has_initialize"] = True
            
            if "render()" in content or "renderUI()" in content or "generateHTML()" in content:
                result["has_render_method"] = True
                
                # Extract render() method content for deep inspection
                render_pattern = r'render\s*\(\s*\)\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
                match = re.search(render_pattern, content, re.DOTALL)
                if match:
                    render_method_content = match.group(1)
            
            if "getSubTabContainer" in content or "getContainer" in content:
                result["has_container_helper"] = True
            
            if "addEventListener" in content or "onclick" in content:
                result["has_event_listeners"] = True
            
            # Check for common rendering issues
            if ".innerHTML" in content and "getSubTabContainer" not in content and "getElementById" not in content:
                result["rendering_issues"].append("innerHTML used without clear container reference")
            
            if "initializeKanbanBoard" in content or "initializeDashboard" in content:
                # Check if it's actually called
                if "this.initializeKanbanBoard()" not in content and "this.initializeDashboard()" not in content:
                    result["rendering_issues"].append("Initialization method defined but may not be called")
        
        # CRITICAL: Check for container ID consistency across HTML generation and rendering
        container_ids_created = set()
        container_ids_queried = set()
        
        for js_file in js_files:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all container IDs created in HTML (id="...")
            created_pattern = r'id\s*=\s*["\']([^"\']+)["\']'
            matches = re.findall(created_pattern, content)
            container_ids_created.update(matches)
            
            # Find all container IDs queried (getElementById('...'))
            queried_pattern = r'getElementById\s*\(\s*["\']([^"\']+)["\']\s*\)'
            matches = re.findall(queried_pattern, content)
            container_ids_queried.update(matches)
        
        # Check for mismatches - queried IDs that are never created
        missing_containers = container_ids_queried - container_ids_created
        # Filter out common platform IDs that might be in base HTML
        platform_ids = {'sidebar', 'main-content', 'header', 'footer', 'nav', 
                       'app-container', 'root', 'app', 'body'}
        missing_containers = {cid for cid in missing_containers 
                             if not any(pid in cid for pid in platform_ids)}
        
        if missing_containers:
            result["container_id_mismatches"] = list(missing_containers)
            for container_id in list(missing_containers)[:3]:  # Report first 3
                result["rendering_issues"].append(
                    f"Container ID mismatch: getElementById('{container_id}') but ID never created in HTML"
                )
        
        # CRITICAL: Check for undefined method calls
        undefined_calls = all_called_methods - all_defined_methods
        # Filter out common built-in methods that might not be in this file
        common_builtins = {
            # Array methods
            'push', 'pop', 'filter', 'map', 'forEach', 'includes', 'indexOf', 
            'find', 'findIndex', 'some', 'every', 'reduce', 'sort', 'reverse',
            'shift', 'unshift', 'splice', 'concat', 'slice', 'join',
            # DOM methods
            'addEventListener', 'removeEventListener', 'querySelector', 
            'querySelectorAll', 'getElementById', 'getElementsByClassName',
            'setAttribute', 'getAttribute', 'removeAttribute', 'hasAttribute',
            'classList', 'appendChild', 'removeChild', 'insertBefore',
            'closest', 'matches', 'contains', 'cloneNode', 'remove',
            'focus', 'blur', 'click', 'submit', 'reset', 'scrollIntoView',
            # String methods
            'toLowerCase', 'toUpperCase', 'trim', 'split', 'replace',
            'startsWith', 'endsWith', 'padStart', 'padEnd', 'repeat',
            # Object methods
            'hasOwnProperty', 'toString', 'valueOf', 'keys', 'values', 'entries',
            # Promise/async methods
            'then', 'catch', 'finally', 'resolve', 'reject',
            # Console methods
            'log', 'warn', 'error', 'info', 'debug', 'table', 'group', 'groupEnd',
            # Math/Number methods
            'toFixed', 'toPrecision', 'toExponential', 'parseInt', 'parseFloat',
            # Date methods
            'getTime', 'getFullYear', 'getMonth', 'getDate', 'getHours',
            # Storage methods
            'getItem', 'setItem', 'removeItem', 'clear',
            # Common utility methods that may be imported
            'fetch', 'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
            'requestAnimationFrame', 'cancelAnimationFrame'
        }
        undefined_calls = undefined_calls - common_builtins
        
        if undefined_calls:
            result["undefined_method_calls"] = list(undefined_calls)
            for method in undefined_calls:
                result["rendering_issues"].append(f"Method '{method}()' is called but not defined - may cause silent failures")
        
        # DEEP VALIDATION: Check if render() method calls valid rendering methods
        if render_method_content:
            result["render_implementation_valid"] = True
            
            # Check for proper rendering flow
            rendering_methods = ['renderBoardUI', 'renderKanbanBoard', 'renderDashboard', 
                               'displayBoard', 'showBoard', 'updateUI', 'refreshUI',
                               'generateBoardHTML', 'generateHTML', 'createBoardStructure']
            
            calls_valid_method = False
            for method in rendering_methods:
                if method in render_method_content:
                    # Verify the method is actually defined
                    if method in all_defined_methods:
                        calls_valid_method = True
                        break
                    else:
                        result["rendering_issues"].append(
                            f"render() calls '{method}()' which is NOT DEFINED - will fail silently!"
                        )
            
            result["render_calls_valid_methods"] = calls_valid_method
            
            if not calls_valid_method:
                result["rendering_issues"].append(
                    "render() method exists but doesn't call any valid rendering method"
                )
        
        # Determine status with stricter validation
        if (result["has_initialize"] and result["has_render_method"] and 
            result["render_calls_valid_methods"] and 
            len(result["undefined_method_calls"]) == 0):
            result["status"] = "PASS"
        elif result["has_initialize"] and result["has_render_method"]:
            if not result["render_calls_valid_methods"]:
                result["status"] = "FAIL"  # render() exists but broken
                self.issues.append("CRITICAL: render() method calls undefined methods - will fail at runtime")
            elif result["undefined_method_calls"]:
                result["status"] = "WARNING"  # Has undefined calls elsewhere
            else:
                result["status"] = "PARTIAL"
        elif result["has_initialize"]:
            result["status"] = "PARTIAL"
        else:
            result["status"] = "FAIL"
        
        # Recommendations
        if not result["has_container_helper"]:
            self.recommendations.append("Add getSubTabContainer() helper method for reliable container access")
        
        if result["undefined_method_calls"]:
            self.issues.append(
                f"CRITICAL: {len(result['undefined_method_calls'])} undefined method(s) called: " +
                ", ".join(result["undefined_method_calls"][:5])
            )
            self.recommendations.append(
                "Review all method calls in the code - undefined methods cause silent failures"
            )
        
        if result["has_render_method"] and not result["render_calls_valid_methods"]:
            self.issues.append(
                "CRITICAL: render() method exists but doesn't call valid rendering methods"
            )
            self.recommendations.append(
                "Ensure render() calls an actual rendering method like renderKanbanBoard() or renderUI()"
            )
        
        if result["container_id_mismatches"]:
            self.issues.append(
                f"CRITICAL: {len(result['container_id_mismatches'])} container ID mismatch(es) - " +
                "getElementById() looking for IDs that don't exist in HTML"
            )
            self.recommendations.append(
                "Fix container ID mismatches: Ensure getElementById('X') matches id='X' in generated HTML"
            )
        
        if result["rendering_issues"]:
            for issue in result["rendering_issues"]:
                self.warnings.append(f"Rendering: {issue}")
        
        print(f"   Initialize method: {'✅' if result['has_initialize'] else 'ERROR '}")
        print(f"   Render method: {'✅' if result['has_render_method'] else 'ERROR '}")
        print(f"   Render calls valid methods: {'✅' if result['render_calls_valid_methods'] else 'ERROR '}")
        print(f"   Container helper: {'✅' if result['has_container_helper'] else 'WARNING'}")
        print(f"   Event listeners: {'✅' if result['has_event_listeners'] else 'WARNING'}")
        if result["undefined_method_calls"]:
            print(f"   CRITICAL Undefined method calls: {len(result['undefined_method_calls'])}")
            for method in result["undefined_method_calls"][:5]:
                print(f"      - {method}()")
        if result["container_id_mismatches"]:
            print(f"   CRITICAL Container ID mismatches: {len(result['container_id_mismatches'])}")
            for container_id in result["container_id_mismatches"][:3]:
                print(f"      - getElementById('{container_id}') but ID not in HTML")
        if result["rendering_issues"]:
            print(f"   Issues found: {len(result['rendering_issues'])}")
            for issue in result["rendering_issues"][:3]:
                print(f"      - {issue}")
        print(f"   Status: {result['status']}\n")
        
        return result
    
    def _check_runtime_diagnostic(self) -> Dict:
        """
        Check runtime initialization and container generation
        Simulates the browser diagnostic that checks if containers exist and module initializes
        """
        print("7. Checking runtime initialization (container generation)...")
        
        result = {
            "containers_checked": [],
            "container_generation": {
                "tab_container": False,
                "main_container": False,
                "board_container": False
            },
            "module_registry": {
                "should_register": False,
                "init_method_exists": False
            },
            "initialization_flow": {
                "has_initialize_method": False,
                "calls_init_board": False,
                "calls_display_board": False,
                "calls_refresh_data": False
            },
            "diagnostic_issues": [],
            "recommendations": [],
            "status": "UNKNOWN"
        }
        
        # Read manifest to get module ID
        manifest_file = self.module_path / "manifest.json"
        module_id = self.module_name
        if manifest_file.exists():
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                module_id = manifest.get("id", self.module_name)
        
        # Check if module should create main tab container
        result["containers_checked"] = [
            f"tab-{module_id}",
            f"{module_id}-main-container",
            f"{module_id}-board" if "kanban" in module_id else f"{module_id}-content"
        ]
        
        # Analyze JS files for initialization pattern
        js_files = [f for f in self.module_path.glob("*.js") 
                    if "test" not in f.name.lower() and "backup" not in f.name.lower()]
        
        for js_file in js_files:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for ModuleRegistry registration
            if f"window.ModuleRegistry['{module_id}']" in content or \
               f'window.ModuleRegistry["{module_id}"]' in content:
                result["module_registry"]["should_register"] = True
            
            # Check for init() method
            if re.search(r'init\s*\(\s*\)\s*{', content):
                result["module_registry"]["init_method_exists"] = True
            
            # Check for initialize() method
            if re.search(r'initialize\s*\(\s*\)\s*{', content):
                result["initialization_flow"]["has_initialize_method"] = True
            
            # Check for board initialization calls
            if "initializeKanbanBoard" in content or "initializeDashboard" in content or "initializeBoard" in content:
                result["initialization_flow"]["calls_init_board"] = True
            
            # Check for display/render calls
            if "displayBoard" in content or "renderBoard" in content or "showBoard" in content:
                result["initialization_flow"]["calls_display_board"] = True
            
            # Check for data refresh
            if "refreshData" in content or "loadData" in content or "fetchData" in content:
                result["initialization_flow"]["calls_refresh_data"] = True
        
        # Analyze HTML files for container generation
        html_files = list(self.module_path.glob("*.html"))
        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Check for main containers
            if f'id="tab-{module_id}"' in html_content:
                result["container_generation"]["tab_container"] = True
            if f'id="{module_id}-main-container"' in html_content:
                result["container_generation"]["main_container"] = True
            if "board" in html_content or "dashboard" in html_content:
                result["container_generation"]["board_container"] = True
        
        # Diagnostic analysis (similar to browser console diagnostic)
        if not result["module_registry"]["should_register"]:
            result["diagnostic_issues"].append(
                f"Module does not register in window.ModuleRegistry['{module_id}']"
            )
            result["recommendations"].append(
                "Add ModuleRegistry registration in init() method"
            )
        
        if result["initialization_flow"]["has_initialize_method"]:
            if not result["initialization_flow"]["calls_init_board"]:
                result["diagnostic_issues"].append(
                    "initialize() exists but doesn't call initializeBoard/initializeDashboard"
                )
                result["recommendations"].append(
                    "Call initializeKanbanBoard() or initializeDashboard() in initialize() method"
                )
            
            if result["initialization_flow"]["calls_refresh_data"] and \
               not result["initialization_flow"]["calls_display_board"]:
                result["diagnostic_issues"].append(
                    "CRITICAL: refreshData() called but displayBoard() NOT called - dashboard will be empty!"
                )
                result["recommendations"].append(
                    "Add displayBoard() call after refreshData() completes (see MODULE_LOADING_COMPLETE_FIX_NOV29.md)"
                )
                self.issues.append(
                    f"CRITICAL: Module loads data but never displays it - add displayBoard() call after refreshData()"
                )
        
        # Check container generation logic
        if not result["container_generation"]["main_container"] and \
           not result["initialization_flow"]["calls_init_board"]:
            result["diagnostic_issues"].append(
                "No main container in HTML and no programmatic container creation detected"
            )
            result["recommendations"].append(
                "Either add container to HTML or create it programmatically in initializeBoard()"
            )
        
        # Determine status
        has_container_issue = len([k for k, v in result["container_generation"].items() if not v]) > 1
        has_init_issue = len([k for k, v in result["initialization_flow"].items() if not v]) > 2
        
        if len(result["diagnostic_issues"]) == 0:
            result["status"] = "PASS"
        elif "CRITICAL" in str(result["diagnostic_issues"]):
            result["status"] = "CRITICAL"
        elif has_container_issue or has_init_issue:
            result["status"] = "WARNING"
        else:
            result["status"] = "PASS"
        
        # Print diagnostic results
        print(f"   Container generation:")
        print(f"      Tab container ({result['containers_checked'][0]}): {'✅' if result['container_generation']['tab_container'] else 'WARNING'}")
        print(f"      Main container ({result['containers_checked'][1]}): {'✅' if result['container_generation']['main_container'] else 'WARNING'}")
        print(f"      Board/content container: {'✅' if result['container_generation']['board_container'] else 'WARNING'}")
        
        print(f"   Module registry:")
        print(f"      Should register: {'✅' if result['module_registry']['should_register'] else 'WARNING'}")
        print(f"      Has init() method: {'✅' if result['module_registry']['init_method_exists'] else 'WARNING'}")
        
        print(f"   Initialization flow:")
        print(f"      Has initialize() method: {'✅' if result['initialization_flow']['has_initialize_method'] else 'ERROR '}")
        print(f"      Calls initBoard: {'✅' if result['initialization_flow']['calls_init_board'] else 'WARNING'}")
        print(f"      Calls displayBoard: {'✅' if result['initialization_flow']['calls_display_board'] else 'ERROR '}")
        print(f"      Calls refreshData: {'✅' if result['initialization_flow']['calls_refresh_data'] else 'WARNING'}")
        
        if result["diagnostic_issues"]:
            print(f"   CRITICAL Diagnostic issues: {len(result['diagnostic_issues'])}")
            for issue in result["diagnostic_issues"]:
                print(f"      - {issue}")
        
        print(f"   Status: {result['status']}\n")
        
        # Add recommendations to global list
        for rec in result["recommendations"]:
            if rec not in self.recommendations:
                self.recommendations.append(rec)
        
        return result
    
    def _check_module_registry_compatibility(self) -> Dict:
        """Check if module is compatible with ModuleRegistry loading system"""
        print("7a. Checking module registry compatibility...")
        
        if not self.manifest:
            print("   SKIP   No manifest loaded\n")
            return {"status": "SKIP", "message": "No manifest loaded"}
        
        issues = []
        warnings = []
        compatibility_score = 0
        max_score = 10
        
        # Check 1: Has required fields (id, name, version)
        if all(k in self.manifest for k in ['id', 'name', 'version']):
            compatibility_score += 2
        else:
            missing = [k for k in ['id', 'name', 'version'] if k not in self.manifest]
            issues.append(f"Missing required fields: {', '.join(missing)}")
        
        # Check 2: Dependencies are hashable (not dicts in list)
        deps = self.manifest.get('dependencies')
        deps_valid = True
        if deps:
            if isinstance(deps, list):
                for item in deps:
                    if isinstance(item, dict):
                        issues.append("Dependencies list contains dict items (causes unhashable error)")
                        deps_valid = False
                        break
            elif isinstance(deps, dict):
                # Check modules subkey
                modules = deps.get('modules', [])
                for item in modules:
                    if isinstance(item, dict):
                        issues.append("dependencies.modules contains dict items (causes unhashable error)")
                        deps_valid = False
                        break
        
        if deps_valid:
            compatibility_score += 2
        
        # Check 3: api_routes/api_endpoints structure
        api_routes = self.manifest.get('api_routes') or self.manifest.get('api_endpoints')
        if api_routes:
            if isinstance(api_routes, list):
                compatibility_score += 1
            elif isinstance(api_routes, dict):
                # Dict format is OK - registry will flatten it
                compatibility_score += 1
                warnings.append("api_endpoints is dict - will be flattened to list by registry")
        
        # Check 4: Has icon and color (UI requirements)
        if 'icon' in self.manifest and 'color' in self.manifest:
            compatibility_score += 1
        else:
            warnings.append("Missing icon or color - UI may not display properly")
        
        # Check 5: File paths specified
        has_files = any(k in self.manifest for k in ['html_file', 'js_file', 'css_file', 'files'])
        if has_files:
            compatibility_score += 2
        else:
            warnings.append("No file paths specified (html_file, js_file, css_file)")
        
        # Check 6: Sidebar configuration
        has_sidebar = self.manifest.get('sidebar_position') or self.manifest.get('capabilities', {}).get('sidebar')
        if has_sidebar:
            compatibility_score += 1
        
        # Check 7: Valid version format (semver)
        version = self.manifest.get('version', '')
        if re.match(r'^\d+\.\d+\.\d+', version):
            compatibility_score += 1
        else:
            warnings.append(f"Version '{version}' doesn't follow semver format (x.y.z)")
        
        status = "ERROR" if issues else ("PASS" if compatibility_score >= 7 else "WARN")
        percentage = int((compatibility_score / max_score) * 100)
        
        print(f"   Compatibility score: {compatibility_score}/{max_score} ({percentage}%)")
        print(f"   Issues: {len(issues)}")
        print(f"   Warnings: {len(warnings)}")
        print(f"   Status: {status}\n")
        
        return {
            "status": status,
            "compatibility_score": compatibility_score,
            "max_score": max_score,
            "percentage": percentage,
            "issues": issues,
            "warnings": warnings,
            "message": f"Registry compatibility: {compatibility_score}/{max_score} ({percentage}%)"
        }
    
    def _test_api_endpoints(self) -> Dict:
        """Test live API endpoint connections (non-blocking)"""
        print("8. Testing API endpoints (live connections)...")
        
        result = {
            "enabled": True,
            "endpoints_tested": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
            "test_results": [],
            "avg_response_time_ms": 0,
            "status": "SKIPPED"
        }
        
        # Get detected endpoints from previous check
        js_files = [f for f in self.module_path.glob("*.js") if "test" not in f.name.lower() and "backup" not in f.name.lower()]
        
        endpoints_to_test = []
        backend_base_url = "http://localhost:5001"  # Default
        
        # Extract endpoints and base URL
        for js_file in js_files:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find backend URL
                backend_pattern = r"(?:backendUrl|apiUrl|baseUrl).*?['\"]([^'\"]+)['\"]"
                match = re.search(backend_pattern, content)
                if match:
                    backend_base_url = match.group(1)
                
                # Find fetch() calls with full URLs or relative paths
                fetch_pattern = r"fetch\(['\"]([^'\"]+)['\"]"
                matches = re.findall(fetch_pattern, content)
                endpoints_to_test.extend(matches)
                
                # Find API endpoint definitions
                api_def_pattern = r"['\"](?:endpoint|url|api)['\"]:\s*['\"]([^'\"]+)['\"]"
                matches = re.findall(api_def_pattern, content)
                endpoints_to_test.extend(matches)
                
            except Exception as e:
                result["errors"].append(f"Error reading {js_file.name}: {str(e)}")
        
        # Deduplicate and filter valid endpoints
        endpoints_to_test = list(set(endpoints_to_test))
        endpoints_to_test = [ep for ep in endpoints_to_test if not ep.startswith("javascript:") 
                             and not ep.startswith("data:") 
                             and not ep.startswith("#")
                             and not "${" in ep]  # Skip template strings
        
        result["endpoints_tested"] = len(endpoints_to_test)
        
        if len(endpoints_to_test) == 0:
            print(f"   No testable endpoints found")
            print(f"   Status: SKIPPED\n")
            result["status"] = "SKIPPED"
            return result
        
        print(f"   Found {len(endpoints_to_test)} endpoints to test")
        
        # Test each endpoint (with timeout and error handling)
        response_times = []
        
        for endpoint in endpoints_to_test[:10]:  # Limit to 10 endpoints to avoid long waits
            test_result = {
                "endpoint": endpoint,
                "full_url": "",
                "status": "unknown",
                "status_code": None,
                "response_time_ms": None,
                "error": None,
                "skipped": False
            }
            
            try:
                # Build full URL
                if endpoint.startswith("http://") or endpoint.startswith("https://"):
                    full_url = endpoint
                elif endpoint.startswith("/"):
                    full_url = backend_base_url.rstrip("/") + endpoint
                else:
                    full_url = backend_base_url.rstrip("/") + "/" + endpoint
                
                test_result["full_url"] = full_url
                
                # Make request with short timeout (non-blocking)
                start_time = time.time()
                response = requests.get(
                    full_url, 
                    timeout=3,  # 3 second timeout
                    allow_redirects=True,
                    headers={
                        "User-Agent": "ModuleAnalyzer/1.0",
                        "Accept": "application/json"
                    }
                )
                end_time = time.time()
                
                response_time = int((end_time - start_time) * 1000)
                response_times.append(response_time)
                
                test_result["status_code"] = response.status_code
                test_result["response_time_ms"] = response_time
                
                # Determine status
                if response.status_code == 200:
                    test_result["status"] = "passed"
                    result["passed"] += 1
                elif response.status_code == 401:
                    test_result["status"] = "auth_required"
                    test_result["error"] = "Authentication required (401)"
                    result["passed"] += 1  # Not a failure, just needs auth
                elif response.status_code == 404:
                    test_result["status"] = "not_found"
                    test_result["error"] = "Endpoint not found (404)"
                    result["failed"] += 1
                elif response.status_code >= 500:
                    test_result["status"] = "server_error"
                    test_result["error"] = f"Server error ({response.status_code})"
                    result["failed"] += 1
                else:
                    test_result["status"] = "other"
                    test_result["error"] = f"Status code: {response.status_code}"
                    result["passed"] += 1  # Not necessarily a failure
                
            except requests.exceptions.Timeout:
                test_result["status"] = "timeout"
                test_result["error"] = "Request timeout (>3s)"
                result["skipped"] += 1
                
            except requests.exceptions.ConnectionError:
                test_result["status"] = "connection_error"
                test_result["error"] = "Connection refused (server may not be running)"
                result["skipped"] += 1
                
            except requests.exceptions.RequestException as e:
                test_result["status"] = "error"
                test_result["error"] = str(e)[:100]  # Truncate long errors
                result["skipped"] += 1
                
            except Exception as e:
                test_result["status"] = "error"
                test_result["error"] = f"Unexpected error: {str(e)[:100]}"
                result["skipped"] += 1
            
            result["test_results"].append(test_result)
        
        # Calculate average response time
        if response_times:
            result["avg_response_time_ms"] = int(sum(response_times) / len(response_times))
        
        # Determine overall status
        if result["endpoints_tested"] == 0:
            result["status"] = "SKIPPED"
        elif result["passed"] == result["endpoints_tested"]:
            result["status"] = "PASS"
        elif result["failed"] > 0:
            result["status"] = "FAIL"
        elif result["skipped"] == result["endpoints_tested"]:
            result["status"] = "SKIPPED"
        else:
            result["status"] = "PARTIAL"
        
        # Add to issues/warnings (non-blocking)
        if result["failed"] > 0:
            self.warnings.append(f"API Testing: {result['failed']} endpoints returned errors")
        
        if result["skipped"] > 0:
            self.recommendations.append(f"API Testing: {result['skipped']} endpoints skipped (server may not be running)")
        
        # Print results
        print(f"   Tested: {result['endpoints_tested']} endpoints")
        print(f"   Passed: {result['passed']} (SUCCESS 200 OK, 401 Auth)")
        print(f"   Failed: {result['failed']} (ERROR  404, 500+)")
        print(f"   Skipped: {result['skipped']} (⏭️ Timeout, Connection)")
        
        if response_times:
            print(f"   Avg Response: {result['avg_response_time_ms']}ms")
        
        print(f"   Status: {result['status']}\n")
        
        return result
    
    def _detect_connections(self) -> Dict:
        """Detect external connections and integrations"""
        print("9. Detecting connections and integrations...")
        
        connections = {
            "databases": [],
            "external_apis": [],
            "websockets": [],
            "credentials": []
        }
        
        js_files = [f for f in self.module_path.glob("*.js") if "test" not in f.name.lower()]
        
        for js_file in js_files:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Database connections
            if "supabase" in content.lower():
                connections["databases"].append("Supabase")
            if "postgresql" in content.lower() or "postgres" in content.lower():
                connections["databases"].append("PostgreSQL")
            if "sql server" in content.lower() or "mssql" in content.lower():
                connections["databases"].append("SQL Server")
            
            # External APIs
            if "shopify" in content.lower():
                connections["external_apis"].append("Shopify")
            if "salesforce" in content.lower():
                connections["external_apis"].append("Salesforce")
            if "stripe" in content.lower():
                connections["external_apis"].append("Stripe")
            if "openai" in content.lower():
                connections["external_apis"].append("OpenAI")
            
            # WebSocket connections
            if "WebSocket" in content or "websocket" in content.lower():
                ws_pattern = r"WebSocket\(['\"]([^'\"]+)['\"]"
                matches = re.findall(ws_pattern, content)
                connections["websockets"].extend(matches)
            
            # Credentials
            if "credentials" in content.lower() or "api_key" in content.lower():
                connections["credentials"].append("API credentials required")
        
        # Check manifest for credentials
        if self.manifest and "credentials" in self.manifest:
            creds = self.manifest["credentials"]
            if creds.get("required"):
                connections["credentials"].append("Credentials declared in manifest")
        
        # Deduplicate
        connections["databases"] = list(set(connections["databases"]))
        connections["external_apis"] = list(set(connections["external_apis"]))
        connections["websockets"] = list(set(connections["websockets"]))
        connections["credentials"] = list(set(connections["credentials"]))
        
        result = {
            "databases": connections["databases"],
            "external_apis": connections["external_apis"],
            "websockets": connections["websockets"],
            "requires_credentials": len(connections["credentials"]) > 0,
            "total_connections": len(connections["databases"]) + len(connections["external_apis"]) + len(connections["websockets"]),
            "status": "PASS"
        }
        
        print(f"   Databases: {', '.join(connections['databases']) if connections['databases'] else 'None'}")
        print(f"   External APIs: {', '.join(connections['external_apis']) if connections['external_apis'] else 'None'}")
        print(f"   WebSockets: {len(connections['websockets'])} connections")
        print(f"   Credentials: {'SUCCESS Required' if result['requires_credentials'] else 'NOTICE Not required'}")
        print(f"   Status: {result['status']}\n")
        
        return result
    
    def _check_documentation(self) -> Dict:
        """Check documentation coverage"""
        print("10. Checking documentation...")
        
        docs = {
            "readme": False,
            "integration_guide": False,
            "api_docs": False,
            "total_docs": 0,
            "doc_files": []
        }
        
        for md_file in self.module_path.glob("*.md"):
            docs["total_docs"] += 1
            docs["doc_files"].append(md_file.name)
            
            name = md_file.name.lower()
            if name == "readme.md":
                docs["readme"] = True
            if "integration" in name or "guide" in name:
                docs["integration_guide"] = True
            if "api" in name:
                docs["api_docs"] = True
        
        result = {
            "has_readme": docs["readme"],
            "has_integration_guide": docs["integration_guide"],
            "total_docs": docs["total_docs"],
            "doc_files": docs["doc_files"],
            "status": "PASS" if docs["readme"] else "INCOMPLETE"
        }
        
        if not docs["readme"]:
            self.warnings.append("No README.md found")
            self.recommendations.append("Create README.md with module overview and usage instructions")
        
        if docs["total_docs"] > 10:
            self.recommendations.append(f"Many documentation files ({docs['total_docs']}) - consider consolidation")
        
        print(f"   README.md: {'✅' if docs['readme'] else 'ERROR '}")
        print(f"   Integration guide: {'✅' if docs['integration_guide'] else 'WARNING'}")
        print(f"   Total docs: {docs['total_docs']}")
        if docs["total_docs"] > 0:
            print(f"   Files: {', '.join(docs['doc_files'][:5])}")
        print(f"   Status: {result['status']}\n")
        
        return result
    
    def _check_best_practices(self) -> Dict:
        """Check adherence to best practices"""
        print("11. Checking best practices...")
        
        practices = {
            "issues": [],
            "good_practices": []
        }
        
        js_files = [f for f in self.module_path.glob("*.js") if "test" not in f.name.lower() and "backup" not in f.name.lower()]
        
        for js_file in js_files:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for console.log (should use proper logging)
            console_logs = content.count("console.log")
            if console_logs > 50:
                practices["issues"].append(f"Excessive console.log usage ({console_logs} instances)")
            elif console_logs > 0:
                practices["good_practices"].append(f"Uses logging ({console_logs} instances)")
            
            # Check for error handling
            has_try_catch = "try {" in content and "catch" in content
            if has_try_catch:
                practices["good_practices"].append("Uses try-catch error handling")
            else:
                practices["issues"].append("Limited error handling detected")
            
            # Check for async/await
            has_async = "async " in content and "await " in content
            if has_async:
                practices["good_practices"].append("Uses modern async/await")
            
            # Check for class-based structure
            has_class = "class " in content
            if has_class:
                practices["good_practices"].append("Uses class-based architecture")
            
            # Check for inline styles (should use CSS)
            inline_styles = content.count("style=")
            if inline_styles > 20:
                practices["issues"].append(f"Excessive inline styles ({inline_styles}) - use CSS instead")
        
        result = {
            "good_practices": len(practices["good_practices"]),
            "issues": len(practices["issues"]),
            "practices_list": practices["good_practices"],
            "issues_list": practices["issues"],
            "status": "PASS" if len(practices["issues"]) < 3 else "NEEDS_IMPROVEMENT"
        }
        
        print(f"   Good practices: {result['good_practices']}")
        for practice in practices["good_practices"][:3]:
            print(f"      SUCCESS {practice}")
        
        if practices["issues"]:
            print(f"   Issues: {result['issues']}")
            for issue in practices["issues"][:3]:
                print(f"      WARNING {issue}")
        
        print(f"   Status: {result['status']}\n")
        
        return result
    
    def _check_duplicate_declarations(self) -> Dict:
        """Check for duplicate class and function declarations that cause SyntaxError"""
        print("12. Checking for duplicate declarations (CRITICAL)...")
        
        duplicates = {
            "duplicate_classes": [],
            "duplicate_functions": [],
            "redeclared_globals": [],
            "files_with_issues": []
        }
        
        js_files = [f for f in self.module_path.glob("*.js") if "test" not in f.name.lower() and "backup" not in f.name.lower()]
        
        # Known global classes that should NOT be redeclared in modules
        global_classes = ["BaseModule", "SidebarManager", "ModuleRegistry", "ThreadCardTemplates"]
        
        for js_file in js_files:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all class declarations
                class_pattern = r'\bclass\s+(\w+)\s*(?:extends|{)'
                class_matches = re.findall(class_pattern, content)
                
                # Check for duplicate class names within the same file
                seen_classes = {}
                for class_name in class_matches:
                    if class_name in seen_classes:
                        duplicates["duplicate_classes"].append({
                            "file": js_file.name,
                            "class": class_name,
                            "count": seen_classes[class_name] + 1
                        })
                        seen_classes[class_name] += 1
                    else:
                        seen_classes[class_name] = 1
                
                # Check for redeclaration of global classes
                for global_class in global_classes:
                    if f"class {global_class}" in content:
                        duplicates["redeclared_globals"].append({
                            "file": js_file.name,
                            "class": global_class,
                            "issue": f"Module redeclares global class '{global_class}' - will cause SyntaxError"
                        })
                
                # Find all function declarations (top-level only, not methods)
                # Match: function name(...) or const name = function(...) or const name = async function(...)
                func_pattern = r'(?:^|\n)\s*(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function)'
                func_matches = re.findall(func_pattern, content, re.MULTILINE)
                func_names = [m[0] or m[1] for m in func_matches if m[0] or m[1]]
                
                # Check for duplicate function names
                seen_functions = {}
                for func_name in func_names:
                    if func_name in seen_functions:
                        duplicates["duplicate_functions"].append({
                            "file": js_file.name,
                            "function": func_name,
                            "count": seen_functions[func_name] + 1
                        })
                        seen_functions[func_name] += 1
                    else:
                        seen_functions[func_name] = 1
                
                # Track files with issues
                if (class_name in seen_classes and seen_classes[class_name] > 1) or \
                   any(g["file"] == js_file.name for g in duplicates["redeclared_globals"]) or \
                   (func_name in seen_functions and seen_functions[func_name] > 1):
                    if js_file.name not in duplicates["files_with_issues"]:
                        duplicates["files_with_issues"].append(js_file.name)
                        
            except Exception as e:
                self.warnings.append(f"Error analyzing {js_file.name} for duplicates: {str(e)}")
        
        result = {
            "duplicate_classes": duplicates["duplicate_classes"],
            "duplicate_functions": duplicates["duplicate_functions"],
            "redeclared_globals": duplicates["redeclared_globals"],
            "files_with_issues": duplicates["files_with_issues"],
            "total_issues": len(duplicates["duplicate_classes"]) + len(duplicates["duplicate_functions"]) + len(duplicates["redeclared_globals"]),
            "status": "PASS"
        }
        
        # Add critical issues
        if duplicates["redeclared_globals"]:
            result["status"] = "CRITICAL"
            for item in duplicates["redeclared_globals"]:
                self.issues.append(f"CRITICAL: {item['file']} redeclares global class '{item['class']}' - causes SyntaxError!")
                self.recommendations.append(f"Remove 'class {item['class']}' from {item['file']} - use 'extends {item['class']}' instead")
        
        if duplicates["duplicate_classes"]:
            result["status"] = "CRITICAL" if result["status"] != "CRITICAL" else result["status"]
            for item in duplicates["duplicate_classes"]:
                self.issues.append(f"CRITICAL: {item['file']} has duplicate class '{item['class']}' ({item['count']} declarations)")
                self.recommendations.append(f"Remove duplicate 'class {item['class']}' declaration in {item['file']}")
        
        if duplicates["duplicate_functions"]:
            result["status"] = "WARNING" if result["status"] == "PASS" else result["status"]
            for item in duplicates["duplicate_functions"]:
                self.warnings.append(f"WARNING: {item['file']} has duplicate function '{item['function']}' ({item['count']} declarations)")
        
        # Print results
        print(f"   Duplicate classes: {len(duplicates['duplicate_classes'])}")
        print(f"   Redeclared globals: {len(duplicates['redeclared_globals'])}")
        print(f"   Duplicate functions: {len(duplicates['duplicate_functions'])}")
        
        if duplicates["redeclared_globals"]:
            print(f"   CRITICAL Global redeclarations:")
            for item in duplicates["redeclared_globals"][:3]:
                print(f"      ❌ {item['file']}: class {item['class']}")
        
        if duplicates["duplicate_classes"]:
            print(f"   CRITICAL Duplicate classes:")
            for item in duplicates["duplicate_classes"][:3]:
                print(f"      ❌ {item['file']}: {item['class']} ({item['count']}x)")
        
        if duplicates["duplicate_functions"]:
            print(f"   WARNING Duplicate functions:")
            for item in duplicates["duplicate_functions"][:3]:
                print(f"      ⚠️  {item['file']}: {item['function']} ({item['count']}x)")
        
        print(f"   Files with issues: {len(duplicates['files_with_issues'])}")
        print(f"   Status: {result['status']}\n")
        
        return result
    
    def _calculate_compliance_score(self, results: Dict) -> int:
        """Calculate overall V3.0 compliance score (0-100)"""
        score = 0
        max_score = 100
        
        checks = results["checks"]
        
        # File structure (10 points)
        if checks["file_structure"]["status"] == "PASS":
            score += 10
        
        # Manifest compliance (20 points)
        if checks["manifest_compliance"]["version"] == "3.0":
            score += 20
        elif checks["manifest_compliance"]["version"] == "2.x":
            score += 10
        
        # HTML path validation (10 points) - CRITICAL CHECK
        if checks["html_path_validation"]["status"] == "PASS":
            score += 10
        elif checks["html_path_validation"]["status"] == "WARNING":
            score += 5
        elif checks["html_path_validation"]["status"] == "CRITICAL":
            score += 0
            self.issues.append("CRITICAL: HTML path validation failed - module will not load!")
        
        # Architecture pattern (10 points) - Reduced from 15 to accommodate HTML path check
        if checks["architecture_pattern"]["confidence"] > 70:
            score += 10
        elif checks["architecture_pattern"]["confidence"] > 50:
            score += 5
        
        # Sidebar integration (10 points)
        if checks["sidebar_integration"]["status"] == "PASS":
            score += 10
        elif checks["sidebar_integration"]["status"] == "CUSTOM":
            score += 5
        
        # API endpoints (10 points)
        if checks["api_endpoints"]["status"] == "PASS":
            score += 10
        
        # UI rendering (10 points)
        if checks["ui_rendering"]["status"] == "PASS":
            score += 10
        elif checks["ui_rendering"]["status"] == "PARTIAL":
            score += 5
        
        # Runtime diagnostic (10 points) - NEW
        if checks["runtime_diagnostic"]["status"] == "PASS":
            score += 10
        elif checks["runtime_diagnostic"]["status"] == "WARNING":
            score += 5
        elif checks["runtime_diagnostic"]["status"] == "CRITICAL":
            score += 0
            self.issues.append("CRITICAL runtime diagnostic issues found - module may not initialize properly")
        
        # Connections (10 points)
        if checks["connections"]["total_connections"] > 0:
            score += 10
        
        # Documentation (10 points)
        if checks["documentation"]["status"] == "PASS":
            score += 10
        elif checks["documentation"]["has_readme"]:
            score += 5
        
        # Duplicate declarations (10 points) - CRITICAL CHECK
        if checks["duplicate_declarations"]["status"] == "PASS":
            score += 10
        elif checks["duplicate_declarations"]["status"] == "WARNING":
            score += 5
        elif checks["duplicate_declarations"]["status"] == "CRITICAL":
            score += 0
            self.issues.append("CRITICAL: Duplicate class/function declarations found - will cause SyntaxError!")
        
        # ES6/V4 compliance (10 points) - BONUS points for modern framework readiness
        if "es6_v4_compliance" in checks:
            es6_status = checks["es6_v4_compliance"]["status"]
            if es6_status == "READY":
                score += 10
                self.recommendations.append("ES6 READY: Module can use Modern Framework V4 loader for 50% performance improvement")
            elif es6_status == "PARTIAL":
                score += 5
                self.warnings.append(f"ES6 PARTIAL: Module needs {len(checks['es6_v4_compliance']['migration_needed'])} updates for V4 compliance")
            elif es6_status == "NEEDS_MIGRATION":
                score += 0
                self.recommendations.append("ES6 MIGRATION: Module uses legacy BaseModule pattern - follow migration steps")
            elif es6_status == "NEEDS_REFACTOR":
                score += 3
                self.recommendations.append("ES6 REFACTOR: Convert class-based module to composition pattern")
        
        return score
    
    def _print_results(self, results: Dict):
        """Print formatted analysis results"""
        print(f"\n{'='*80}")
        print(f"ANALYSIS COMPLETE")
        print(f"{'='*80}\n")
        
        # Compliance score
        score = results["compliance_score"]
        if score >= 80:
            status = "SUCCESS EXCELLENT"
            color = "green"
        elif score >= 60:
            status = "WARNING GOOD"
            color = "yellow"
        elif score >= 40:
            status = "WARNING NEEDS IMPROVEMENT"
            color = "yellow"
        else:
            status = "ERROR  POOR"
            color = "red"
        
        print(f"V3.0 COMPLIANCE SCORE: {score}/100 - {status}\n")
        
        # Issues
        if self.issues:
            print(f"🔴 CRITICAL ISSUES ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   - {issue}")
            print()
        
        # Warnings
        if self.warnings:
            print(f"WARNING WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:5]:
                print(f"   - {warning}")
            if len(self.warnings) > 5:
                print(f"   ... and {len(self.warnings) - 5} more")
            print()
        
        # Recommendations
        if self.recommendations:
            print(f"💡 RECOMMENDATIONS ({len(self.recommendations)}):")
            for rec in self.recommendations[:5]:
                print(f"   - {rec}")
            if len(self.recommendations) > 5:
                print(f"   ... and {len(self.recommendations) - 5} more")
            print()
        
        # Summary
        print(f"{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"Manifest Version: {results['checks']['manifest_compliance'].get('version', 'N/A')}")
        print(f"Architecture: {results['checks']['architecture_pattern']['architecture']}")
        print(f"API Endpoints: {results['checks']['api_endpoints']['total_endpoints']}")
        print(f"Sidebar: {results['checks']['sidebar_integration']['status']}")
        print(f"Documentation: {results['checks']['documentation']['total_docs']} files")
        print(f"{'='*80}\n")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Module Analyzer - V3.0 Compliance & Architecture Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/testing/module_analyzer.py UI/modules_external/inhouse-kanban
  python scripts/testing/module_analyzer.py UI/modules_external/inhouse-kanban --test-endpoints
  python scripts/testing/module_analyzer.py UI/modules_external/inhouse-kanban --endpoints /api/test,/api/health
  python scripts/testing/module_analyzer.py UI/modules_external/inhouse-kanban --base-url http://localhost:5001 --token abc123
        """
    )
    
    parser.add_argument('module_path', help='Path to module folder')
    parser.add_argument('--test-endpoints', action='store_true', 
                        help='Enable live API endpoint testing (checks if endpoints are reachable)')
    parser.add_argument('--endpoints', type=str,
                        help='Comma-separated list of endpoints to test (e.g., /api/test,/api/health)')
    parser.add_argument('--base-url', type=str, default='http://localhost:5001',
                        help='Base URL for API testing (default: http://localhost:5001)')
    parser.add_argument('--token', type=str,
                        help='Authentication token for API requests')
    parser.add_argument('--timeout', type=int, default=5,
                        help='Request timeout in seconds (default: 5)')
    parser.add_argument('--output', type=str,
                        help='Custom output file path')
    
    args = parser.parse_args()
    
    # Parse endpoints
    endpoints = []
    if args.endpoints:
        endpoints = [e.strip() for e in args.endpoints.split(',')]
    
    # Create analyzer with configuration
    analyzer = ModuleAnalyzer(
        module_path=args.module_path,
        test_endpoints=args.test_endpoints,
        endpoints=endpoints,
        base_url=args.base_url,
        auth_token=args.token,
        timeout=args.timeout
    )
    
    results = analyzer.analyze()
    
    # Generate timestamped output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    module_name = Path(args.module_path).name
    
    if args.output:
        output_file = Path(args.output)
    else:
        # Format: modulename_analysis_20251129_143045.json
        output_file = Path(args.module_path) / f"{module_name}_analysis_{timestamp}.json"
    
    # Save results to JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {output_file}\n")
    except Exception as e:
        print(f"Warning: Could not save results file: {e}\n")
    
    # Exit with code based on score
    score = results["compliance_score"]
    if score >= 70:
        sys.exit(0)  # Success
    elif score >= 40:
        sys.exit(1)  # Needs improvement
    else:
        sys.exit(2)  # Poor compliance


if __name__ == "__main__":
    main()

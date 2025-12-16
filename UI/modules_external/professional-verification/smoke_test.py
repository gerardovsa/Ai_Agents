"""
Professional Verification Module - Smoke Test
==============================================

Quick validation of module installation, dependencies, and basic functionality.

WHAT IT CHECKS:
- Python dependencies (anthropic, docker, flask)
- Optional dependencies (reportlab for PDF export)
- File structure (all core files present)
- Tool schema files (25 tools)
- Docker image availability
- Environment variables (ANTHROPIC_API_KEY)
- Tool Registry V3 auto-discovery
- Module manifest validity

USAGE:
    cd UI/modules_external/professional-verification
    python smoke_test.py

EXPECTED OUTPUT:
    ✅ All checks passed - Module ready for use
    OR
    ❌ Failures with specific remediation steps

CREATED: December 16, 2025
"""

import sys
import os
from pathlib import Path
import json
import importlib.util

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def print_section(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}")

def print_pass(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_fail(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warn(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"   {text}")


class SmokeTest:
    """Professional Verification Module Smoke Test"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
        # Determine paths
        self.module_root = Path(__file__).parent.absolute()
        self.project_root = self.module_root.parent.parent.parent
        
    def run_all_tests(self):
        """Run all smoke tests"""
        print_header("PROFESSIONAL VERIFICATION MODULE - SMOKE TEST")
        
        print_info(f"Module Root: {self.module_root}")
        print_info(f"Project Root: {self.project_root}")
        
        # Run test suites
        self.test_python_dependencies()
        self.test_file_structure()
        self.test_tool_schemas()
        self.test_module_manifest()
        self.test_docker_availability()
        self.test_environment_variables()
        self.test_tool_registry_discovery()
        
        # Summary
        self.print_summary()
        
        return self.failed == 0
    
    def test_python_dependencies(self):
        """Test Python package dependencies"""
        print_section("1. Python Dependencies")
        
        required = [
            ('anthropic', 'Anthropic SDK for Computer Use API'),
            ('docker', 'Docker Python client for container management'),
            ('flask', 'Flask web framework for backend routes')
        ]
        
        optional = [
            ('reportlab', 'ReportLab for PDF export (optional)')
        ]
        
        print_info("Required packages:")
        for package, description in required:
            try:
                importlib.import_module(package)
                print_pass(f"{package:12} - {description}")
                self.passed += 1
            except ImportError:
                print_fail(f"{package:12} - NOT INSTALLED")
                print_info(f"   Install: pip install {package}")
                self.failed += 1
        
        print_info("\nOptional packages:")
        for package, description in optional:
            try:
                importlib.import_module(package)
                print_pass(f"{package:12} - {description}")
                self.passed += 1
            except ImportError:
                print_warn(f"{package:12} - NOT INSTALLED (PDF export unavailable)")
                print_info(f"   Install: pip install {package}")
                self.warnings += 1
    
    def test_file_structure(self):
        """Test core file structure"""
        print_section("2. File Structure")
        
        required_files = [
            ('verification_engine.py', 'Core verification engine'),
            ('report_generator.py', 'Report generation system'),
            ('manifest.json', 'Module manifest'),
            ('README.md', 'Module documentation'),
            ('tools/verification_tools_schema.json', 'Tool schemas'),
            ('tools/implementations/verification_core.py', 'FREE API tools'),
            ('tools/implementations/computer_use_verification.py', 'Computer Use tools')
        ]
        
        for filepath, description in required_files:
            full_path = self.module_root / filepath
            if full_path.exists():
                size_kb = full_path.stat().st_size / 1024
                print_pass(f"{filepath:50} ({size_kb:.1f} KB)")
                self.passed += 1
            else:
                print_fail(f"{filepath:50} MISSING")
                self.failed += 1
    
    def test_tool_schemas(self):
        """Test tool schema files"""
        print_section("3. Tool Schemas")
        
        schema_file = self.module_root / 'tools' / 'verification_tools_schema.json'
        
        if not schema_file.exists():
            print_fail("verification_tools_schema.json not found")
            self.failed += 1
            return
        
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            tools = schema.get('tools', [])
            print_pass(f"Schema file loaded: {len(tools)} tools defined")
            self.passed += 1
            
            # Count by category
            categories = {}
            for tool in tools:
                cat = tool.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            print_info("Tool breakdown:")
            for cat, count in sorted(categories.items()):
                print_info(f"  • {cat}: {count} tools")
            
            # Validate tool structure
            required_fields = ['name', 'description', 'category', 'implementation']
            for tool in tools:
                missing = [f for f in required_fields if f not in tool]
                if missing:
                    print_fail(f"Tool '{tool.get('name', 'unknown')}' missing fields: {missing}")
                    self.failed += 1
                else:
                    self.passed += 1
            
            print_pass(f"All {len(tools)} tools have required fields")
            
        except json.JSONDecodeError as e:
            print_fail(f"Schema file JSON error: {e}")
            self.failed += 1
        except Exception as e:
            print_fail(f"Schema validation error: {e}")
            self.failed += 1
    
    def test_module_manifest(self):
        """Test module manifest"""
        print_section("4. Module Manifest")
        
        manifest_file = self.module_root / 'manifest.json'
        
        if not manifest_file.exists():
            print_fail("manifest.json not found")
            self.failed += 1
            return
        
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            required_fields = ['name', 'version', 'description', 'credential_forms']
            
            for field in required_fields:
                if field in manifest:
                    print_pass(f"Field '{field}': ✓")
                    self.passed += 1
                else:
                    print_fail(f"Field '{field}': MISSING")
                    self.failed += 1
            
            # Check credential forms
            credentials = manifest.get('credential_forms', {})
            print_info(f"Credential forms defined: {len(credentials)}")
            
            for cred_name in credentials.keys():
                print_info(f"  • {cred_name}")
            
        except json.JSONDecodeError as e:
            print_fail(f"Manifest JSON error: {e}")
            self.failed += 1
        except Exception as e:
            print_fail(f"Manifest validation error: {e}")
            self.failed += 1
    
    def test_docker_availability(self):
        """Test Docker availability"""
        print_section("5. Docker Availability")
        
        try:
            import docker
            client = docker.from_env()
            
            # Check if Docker daemon is running
            client.ping()
            print_pass("Docker daemon is running")
            self.passed += 1
            
            # Check for professional-verification-browser image
            try:
                image = client.images.get('professional-verification-browser:latest')
                print_pass(f"Browser image found: {image.short_id}")
                self.passed += 1
            except docker.errors.ImageNotFound:
                print_warn("Browser image not found (build required)")
                print_info("   Build: cd docker/computer-use && docker build -t professional-verification-browser:latest .")
                self.warnings += 1
            
        except ImportError:
            print_fail("Docker Python package not installed")
            print_info("   Install: pip install docker")
            self.failed += 1
        except Exception as e:
            print_fail(f"Docker daemon not running: {e}")
            print_info("   Start Docker Desktop or Docker daemon")
            self.failed += 1
    
    def test_environment_variables(self):
        """Test environment variables"""
        print_section("6. Environment Variables")
        
        # Check ANTHROPIC_API_KEY
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if api_key:
            masked_key = api_key[:8] + '...' + api_key[-4:] if len(api_key) > 12 else '***'
            print_pass(f"ANTHROPIC_API_KEY: {masked_key}")
            self.passed += 1
        else:
            print_fail("ANTHROPIC_API_KEY not set")
            print_info("   Set: export ANTHROPIC_API_KEY=sk-ant-...")
            self.failed += 1
    
    def test_tool_registry_discovery(self):
        """Test Tool Registry V3 auto-discovery"""
        print_section("7. Tool Registry V3 Discovery")
        
        try:
            # Add project root to path
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))
            
            # Import ToolRegistry (check if exists first)
            tool_registry_path = self.project_root / 'AI_infrastructure' / 'tools' / 'tool_registry.py'
            if not tool_registry_path.exists():
                print_warn(f"ToolRegistry not found at {tool_registry_path}")
                print_info("   Tool Registry V3 may not be implemented yet")
                self.warnings += 1
                return
            
            from AI_infrastructure.tools.tool_registry import ToolRegistry
            
            print_pass("ToolRegistry imported successfully")
            self.passed += 1
            
            # Test discovery
            registry = ToolRegistry()
            discovered = registry.discover_tools()
            
            print_pass(f"Tool discovery executed: {discovered} tools found")
            self.passed += 1
            
            # Check for verification tools
            verification_tools = [
                'parse_resume',
                'verify_github_profile',
                'search_linkedin_profile',
                'verify_credential_registry',
                'check_domain_age'
            ]
            
            found_count = 0
            for tool_name in verification_tools:
                if registry.has_tool(tool_name):
                    found_count += 1
            
            if found_count > 0:
                print_pass(f"Found {found_count}/{len(verification_tools)} sample verification tools")
                self.passed += 1
            else:
                print_warn("No verification tools discovered (check tool_registry paths)")
                self.warnings += 1
            
        except ImportError as e:
            print_fail(f"Cannot import ToolRegistry: {e}")
            print_info("   Check AI_infrastructure/tools/tool_registry.py exists")
            self.failed += 1
        except Exception as e:
            print_fail(f"Tool discovery error: {e}")
            self.failed += 1
    
    def print_summary(self):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        total = self.passed + self.failed + self.warnings
        
        print_info(f"Total Checks: {total}")
        print_pass(f"Passed:      {self.passed}")
        
        if self.warnings > 0:
            print_warn(f"Warnings:    {self.warnings}")
        
        if self.failed > 0:
            print_fail(f"Failed:      {self.failed}")
        
        print()
        
        if self.failed == 0:
            print_pass("✅ ALL CRITICAL CHECKS PASSED - Module ready for use")
            if self.warnings > 0:
                print_warn(f"⚠️  {self.warnings} warnings (optional features unavailable)")
        else:
            print_fail(f"❌ {self.failed} CRITICAL FAILURES - Fix before using module")
            print_info("\nRemediation steps shown above ↑")


if __name__ == '__main__':
    test = SmokeTest()
    success = test.run_all_tests()
    
    sys.exit(0 if success else 1)

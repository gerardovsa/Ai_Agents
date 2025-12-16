"""
Professional Verification Module - End-to-End Test Suite
=========================================================

Comprehensive testing for:
- Tool Registry V3 discovery and execution
- Verification Engine risk scoring
- Report Generator exports
- Full workflow integration

USAGE:
    cd UI/modules_external/professional-verification
    python test_suite.py

    # Run specific test
    python test_suite.py TestToolRegistry
    python test_suite.py TestVerificationEngine
    python test_suite.py TestReportGenerator
    python test_suite.py TestEndToEnd

CREATED: December 16, 2025
"""

import unittest
import sys
import os
from pathlib import Path
import json
import tempfile
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import modules to test
from UI.modules_external.professional_verification.verification_engine import VerificationEngine
from UI.modules_external.professional_verification.report_generator import ReportGenerator


class TestToolRegistry(unittest.TestCase):
    """Test Tool Registry V3 auto-discovery and execution"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        try:
            from AI_infrastructure.tools.tool_registry import ToolRegistry
            cls.registry = ToolRegistry()
            cls.discovered = cls.registry.discover_tools()
        except ImportError:
            cls.registry = None
            cls.discovered = 0
    
    def test_registry_import(self):
        """Test ToolRegistry can be imported"""
        self.assertIsNotNone(self.registry, "ToolRegistry import failed")
    
    def test_tool_discovery(self):
        """Test tool auto-discovery"""
        self.assertGreater(self.discovered, 0, "No tools discovered")
        print(f"\n✅ Discovered {self.discovered} tools")
    
    def test_verification_tools_discovered(self):
        """Test verification tools are discovered"""
        expected_tools = [
            'parse_resume',
            'verify_github_profile',
            'search_linkedin_profile',
            'verify_credential_registry',
            'check_domain_age',
            'check_wayback_history'
        ]
        
        for tool_name in expected_tools:
            with self.subTest(tool=tool_name):
                self.assertTrue(
                    self.registry.has_tool(tool_name),
                    f"Tool '{tool_name}' not discovered"
                )
    
    def test_computer_use_tools_discovered(self):
        """Test generic Computer Use tools are discovered"""
        expected_tools = [
            'computer_use_browse_and_extract',
            'computer_use_fill_form',
            'computer_use_compare_competitors'
        ]
        
        for tool_name in expected_tools:
            with self.subTest(tool=tool_name):
                self.assertTrue(
                    self.registry.has_tool(tool_name),
                    f"Computer Use tool '{tool_name}' not discovered"
                )
    
    def test_tool_metadata(self):
        """Test tools have required metadata"""
        if not self.registry.has_tool('parse_resume'):
            self.skipTest("parse_resume tool not available")
        
        metadata = self.registry.get_tool_metadata('parse_resume')
        
        self.assertIn('name', metadata)
        self.assertIn('description', metadata)
        self.assertIn('category', metadata)
        self.assertEqual(metadata['name'], 'parse_resume')


class TestVerificationEngine(unittest.TestCase):
    """Test Verification Engine risk scoring"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = VerificationEngine(profession='software_engineer')
    
    def test_engine_initialization(self):
        """Test engine initializes with profession"""
        self.assertEqual(self.engine.profession, 'software_engineer')
        self.assertIn('resume_authenticity', self.engine.weights)
        self.assertIn('online_presence', self.engine.weights)
    
    def test_profession_templates(self):
        """Test different profession templates have different weights"""
        it_engine = VerificationEngine(profession='software_engineer')
        medical_engine = VerificationEngine(profession='medical_professional')
        
        # IT should weight online presence higher
        self.assertGreater(
            it_engine.weights['online_presence'],
            medical_engine.weights['online_presence']
        )
        
        # Medical should weight credentials higher
        self.assertGreater(
            medical_engine.weights['credential_validity'],
            it_engine.weights['credential_validity']
        )
    
    def test_add_result(self):
        """Test adding tool results"""
        self.engine.add_result('parse_resume', {
            'result': {'name': 'John Doe', 'experience': []}
        })
        
        self.assertIn('parse_resume', self.engine.results)
    
    def test_risk_score_calculation(self):
        """Test risk score calculation"""
        # Add sample results
        self.engine.add_result('parse_resume', {
            'result': {
                'name': 'John Doe',
                'ai_detection': {'is_ai_generated': False, 'confidence': 10},
                'experience': []
            }
        })
        
        self.engine.add_result('verify_github_profile', {
            'result': {
                'profile_exists': True,
                'activity_score': 75,
                'public_repos': 25
            }
        })
        
        risk_assessment = self.engine.calculate_risk_score()
        
        self.assertIn('overall_score', risk_assessment)
        self.assertIn('risk_level', risk_assessment)
        self.assertIn('category_scores', risk_assessment)
        
        self.assertGreaterEqual(risk_assessment['overall_score'], 0)
        self.assertLessEqual(risk_assessment['overall_score'], 100)
        
        self.assertIn(risk_assessment['risk_level'], ['Low', 'Medium', 'High', 'Critical'])
        
        print(f"\n✅ Risk Score: {risk_assessment['overall_score']}/100 ({risk_assessment['risk_level']})")
    
    def test_red_flag_detection(self):
        """Test red flag detection"""
        # Add critical red flag: AI-generated resume
        self.engine.add_result('parse_resume', {
            'result': {
                'name': 'John Doe',
                'ai_detection': {'is_ai_generated': True, 'confidence': 85}
            }
        })
        
        red_flags = self.engine.detect_red_flags()
        
        self.assertIsInstance(red_flags, list)
        
        # Should have at least one critical flag
        critical_flags = [f for f in red_flags if f['severity'] == 'CRITICAL']
        self.assertGreater(len(critical_flags), 0, "No critical flag for AI-generated resume")
        
        print(f"\n✅ Detected {len(red_flags)} red flags ({len(critical_flags)} critical)")
    
    def test_cross_reference_data(self):
        """Test cross-referencing data"""
        self.engine.add_result('parse_resume', {
            'result': {'name': 'John Doe'}
        })
        
        self.engine.add_result('verify_github_profile', {
            'result': {'name': 'John Doe'}
        })
        
        cross_ref = self.engine.cross_reference_data()
        
        self.assertIn('verified_claims', cross_ref)
        self.assertIn('unverified_claims', cross_ref)
        
        # Name should be verified (2 sources)
        self.assertGreater(len(cross_ref['verified_claims']), 0)
    
    def test_timeline_analysis(self):
        """Test timeline gap detection"""
        self.engine.add_result('parse_resume', {
            'result': {
                'experience': [
                    {
                        'company': 'Company A',
                        'title': 'Developer',
                        'start_date': '2020-01',
                        'end_date': '2021-06',
                        'duration_months': 17
                    },
                    {
                        'company': 'Company B',
                        'title': 'Senior Developer',
                        'start_date': '2022-01',
                        'end_date': '2024-12',
                        'duration_months': 35
                    }
                ]
            }
        })
        
        self.engine._build_timeline()
        gaps = self.engine._find_timeline_gaps()
        
        # Should detect 6-month gap
        self.assertGreater(len(gaps), 0, "Gap not detected")
        
        print(f"\n✅ Detected {len(gaps)} timeline gaps")


class TestReportGenerator(unittest.TestCase):
    """Test Report Generator exports"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = VerificationEngine(profession='software_engineer')
        
        # Add sample data
        self.engine.add_result('parse_resume', {
            'result': {
                'name': 'Test Candidate',
                'ai_detection': {'is_ai_generated': False, 'confidence': 10},
                'experience': []
            }
        })
        
        self.generator = ReportGenerator(self.engine)
    
    def test_generator_initialization(self):
        """Test generator initializes"""
        self.assertIsNotNone(self.generator.engine)
    
    def test_compile_report(self):
        """Test report compilation"""
        report = self.generator.compile_report()
        
        self.assertIn('metadata', report)
        self.assertIn('risk_assessment', report)
        self.assertIn('red_flags', report)
        self.assertIn('recommendations', report)
        
        print(f"\n✅ Report compiled with {len(report.keys())} sections")
    
    def test_risk_assessment_compilation(self):
        """Test risk assessment section"""
        assessment = self.generator.compile_risk_assessment()
        
        self.assertIn('overall_risk', assessment)
        self.assertIn('category_scores', assessment)
        
        self.assertIn('score', assessment['overall_risk'])
        self.assertIn('level', assessment['overall_risk'])
    
    def test_claims_categorization(self):
        """Test claims analysis"""
        claims = self.generator.categorize_claims()
        
        self.assertIn('summary', claims)
        self.assertIn('verified_claims', claims)
        self.assertIn('unverified_claims', claims)
    
    def test_timeline_visualization(self):
        """Test timeline visualization data"""
        timeline = self.generator.generate_timeline_visualization()
        
        self.assertIn('events', timeline)
        self.assertIn('gaps', timeline)
        self.assertIn('overlaps', timeline)
    
    def test_json_export(self):
        """Test JSON export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            output_path = self.generator.export_to_json(temp_path)
            
            self.assertTrue(Path(output_path).exists(), "JSON file not created")
            
            # Validate JSON
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            self.assertIn('metadata', data)
            self.assertIn('risk_assessment', data)
            
            print(f"\n✅ JSON export: {Path(output_path).stat().st_size} bytes")
            
        finally:
            if Path(temp_path).exists():
                Path(temp_path).unlink()
    
    def test_html_export(self):
        """Test HTML export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            temp_path = f.name
        
        try:
            output_path = self.generator.export_to_html(temp_path)
            
            self.assertTrue(Path(output_path).exists(), "HTML file not created")
            
            # Check HTML content
            with open(output_path, 'r', encoding='utf-8') as f:
                html = f.read()
            
            self.assertIn('<!DOCTYPE html>', html)
            self.assertIn('Professional Verification Report', html)
            
            print(f"\n✅ HTML export: {Path(output_path).stat().st_size} bytes")
            
        finally:
            if Path(temp_path).exists():
                Path(temp_path).unlink()


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration test"""
    
    def test_full_verification_workflow(self):
        """Test complete verification workflow"""
        print("\n" + "="*70)
        print("RUNNING END-TO-END VERIFICATION WORKFLOW")
        print("="*70)
        
        # Step 1: Initialize engine
        print("\n[1/6] Initializing engine for software_engineer...")
        engine = VerificationEngine(profession='software_engineer')
        self.assertEqual(engine.profession, 'software_engineer')
        print("✅ Engine initialized")
        
        # Step 2: Add verification results
        print("\n[2/6] Adding verification results...")
        
        engine.add_result('parse_resume', {
            'result': {
                'name': 'Jane Smith',
                'contact': {'email': 'jane@example.com'},
                'ai_detection': {'is_ai_generated': False, 'confidence': 15},
                'experience': [
                    {
                        'company': 'TechCorp',
                        'title': 'Senior Developer',
                        'start_date': '2020-01',
                        'end_date': '2023-12',
                        'duration_months': 47
                    }
                ],
                'education': [
                    {'degree': 'BS Computer Science', 'institution': 'MIT', 'year': 2019}
                ]
            }
        })
        
        engine.add_result('verify_github_profile', {
            'result': {
                'profile_exists': True,
                'name': 'Jane Smith',
                'activity_score': 85,
                'public_repos': 42,
                'followers': 156
            }
        })
        
        engine.add_result('search_linkedin_profile', {
            'result': {
                'profile_found': True,
                'name': 'Jane Smith',
                'profile_complete': True,
                'connections': 450
            }
        })
        
        engine.add_result('verify_credential_registry', {
            'result': {
                'credential_valid': True,
                'status': 'Active',
                'disciplinary_actions': False
            }
        })
        
        engine.add_result('check_domain_age', {
            'result': {
                'is_recently_created': False,
                'age_days': 2500
            }
        })
        
        print(f"✅ Added {len(engine.results)} verification results")
        
        # Step 3: Calculate risk score
        print("\n[3/6] Calculating risk score...")
        risk_assessment = engine.calculate_risk_score()
        
        print(f"   Overall Score: {risk_assessment['overall_score']}/100")
        print(f"   Risk Level: {risk_assessment['risk_level']}")
        print(f"   Confidence: {risk_assessment['confidence']}%")
        
        self.assertIn('overall_score', risk_assessment)
        self.assertIn('risk_level', risk_assessment)
        print("✅ Risk score calculated")
        
        # Step 4: Detect red flags
        print("\n[4/6] Detecting red flags...")
        red_flags = engine.detect_red_flags()
        
        critical = len([f for f in red_flags if f['severity'] == 'CRITICAL'])
        high = len([f for f in red_flags if f['severity'] == 'HIGH'])
        
        print(f"   Total Flags: {len(red_flags)}")
        print(f"   Critical: {critical}")
        print(f"   High: {high}")
        
        print("✅ Red flags detected")
        
        # Step 5: Cross-reference data
        print("\n[5/6] Cross-referencing data...")
        cross_ref = engine.cross_reference_data()
        
        print(f"   Verified Claims: {len(cross_ref['verified_claims'])}")
        print(f"   Unverified Claims: {len(cross_ref['unverified_claims'])}")
        
        print("✅ Data cross-referenced")
        
        # Step 6: Generate report
        print("\n[6/6] Generating comprehensive report...")
        generator = ReportGenerator(engine)
        report = generator.compile_report()
        
        print(f"   Report Sections: {len(report.keys())}")
        print(f"   Recommendations: {len(report['recommendations'])}")
        
        # Export to temp files
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / 'report.json'
            html_path = Path(temp_dir) / 'report.html'
            
            generator.export_to_json(str(json_path))
            generator.export_to_html(str(html_path))
            
            self.assertTrue(json_path.exists())
            self.assertTrue(html_path.exists())
            
            print(f"   JSON: {json_path.stat().st_size:,} bytes")
            print(f"   HTML: {html_path.stat().st_size:,} bytes")
        
        print("✅ Report generated and exported")
        
        print("\n" + "="*70)
        print("END-TO-END TEST COMPLETE")
        print("="*70)
        
        # Final assertions
        self.assertLessEqual(risk_assessment['overall_score'], 50, "Risk score too high for clean candidate")
        self.assertEqual(critical, 0, "Should have no critical flags for clean candidate")


def run_tests():
    """Run all tests with verbose output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestToolRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestVerificationEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

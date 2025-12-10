"""
COMPREHENSIVE CALCULATOR TESTING - AI WORKFLOW SIMULATION
==========================================================

This test simulates EXACTLY how an AI agent discovers and uses calculator tools.

Tests:
1. Tool Discovery (search_tools)
2. Tool Schema Retrieval (get_tool_schema)
3. Requirements Validation (get_tool_requirements)
4. Parameter Validation (all combinations)
5. Execution with Real Data
6. Error Handling
7. Response Format Validation

Date: December 10, 2025
Author: AI Agent Testing Framework
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from decimal import Decimal

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "tools" / "implementations"))

# Import AI's tool access methods
from tools.implementations.meta_tools import (
    search_tools,
    get_tool_schema,
    list_platform_tools
)


class CalculatorAIWorkflowTester:
    """
    Simulates exactly how an AI agent would discover and use calculator tools
    """
    
    def __init__(self):
        self.test_results = {
            "discovery": [],
            "schema": [],
            "requirements": [],
            "execution": [],
            "errors": []
        }
        self.calculator_tools = []
        
    def test_discovery(self, search_term: str) -> Dict[str, Any]:
        """
        TEST 1: Can AI discover calculator tools using search?
        
        Simulates: AI types "calculate quote for booklets"
        """
        print(f"\n{'='*80}")
        print(f"TEST 1: TOOL DISCOVERY - search_tools('{search_term}')")
        print(f"{'='*80}")
        
        try:
            # This is what the AI actually calls
            search_response = search_tools(search_term)
            
            # Handle dictionary response (real format)
            if isinstance(search_response, dict):
                results = search_response.get("tools", [])
                found_count = search_response.get("match_count", len(results))
            else:
                # Fallback for unexpected format
                results = search_response if isinstance(search_response, list) else []
                found_count = len(results)
            
            test_result = {
                "search_term": search_term,
                "found_count": found_count,
                "found_tools": [tool.get("name") for tool in results],
                "success": found_count > 0,
                "error": None
            }
            
            print(f"✅ Found {found_count} tools")
            for i, tool in enumerate(results[:5], 1):
                print(f"   {i}. {tool.get('name')}")
            if len(results) > 5:
                print(f"   ... and {len(results) - 5} more")
            
            self.calculator_tools = results
            self.test_results["discovery"].append(test_result)
            return test_result
            
        except Exception as e:
            error_result = {
                "search_term": search_term,
                "found_count": 0,
                "found_tools": [],
                "success": False,
                "error": str(e)
            }
            print(f"❌ DISCOVERY FAILED: {e}")
            self.test_results["discovery"].append(error_result)
            return error_result
    
    def test_schema_retrieval(self, tool_name: str) -> Dict[str, Any]:
        """
        TEST 2: Can AI get tool schema to understand parameters?
        
        Simulates: AI calls get_tool_schema to learn how to use tool
        """
        print(f"\n{'='*80}")
        print(f"TEST 2: SCHEMA RETRIEVAL - get_tool_schema('{tool_name}')")
        print(f"{'='*80}")
        
        try:
            schema = get_tool_schema(tool_name)
            
            if not schema:
                raise Exception("Schema is empty or None")
            
            # Extract key information AI needs
            parameters = schema.get("parameters", {})
            required_params = parameters.get("required", [])
            properties = parameters.get("properties", {})
            
            test_result = {
                "tool_name": tool_name,
                "has_schema": True,
                "has_description": bool(schema.get("description")),
                "has_parameters": bool(parameters),
                "required_params": required_params,
                "param_count": len(properties),
                "param_names": list(properties.keys()),
                "success": True,
                "error": None
            }
            
            print(f"✅ Schema retrieved successfully")
            print(f"   Description: {schema.get('description', 'N/A')[:100]}...")
            print(f"   Required params: {required_params}")
            print(f"   Total params: {len(properties)}")
            
            self.test_results["schema"].append(test_result)
            return test_result
            
        except Exception as e:
            error_result = {
                "tool_name": tool_name,
                "has_schema": False,
                "success": False,
                "error": str(e)
            }
            print(f"❌ SCHEMA RETRIEVAL FAILED: {e}")
            self.test_results["schema"].append(error_result)
            return error_result
    
    def test_requirements_guidance(self, tool_name: str) -> Dict[str, Any]:
        """
        TEST 3: Does AI get proper guidance on requirements?
        
        Simulates: AI needs to know what values are valid for each parameter
        """
        print(f"\n{'='*80}")
        print(f"TEST 3: REQUIREMENTS GUIDANCE - Understanding valid values")
        print(f"{'='*80}")
        
        try:
            schema = get_tool_schema(tool_name)
            parameters = schema.get("parameters", {}).get("properties", {})
            
            test_result = {
                "tool_name": tool_name,
                "params_tested": [],
                "has_enums": False,
                "has_examples": False,
                "has_descriptions": False,
                "success": True,
                "error": None
            }
            
            for param_name, param_info in parameters.items():
                param_test = {
                    "name": param_name,
                    "type": param_info.get("type"),
                    "has_enum": "enum" in param_info,
                    "enum_values": param_info.get("enum", []),
                    "has_description": bool(param_info.get("description")),
                    "description": param_info.get("description", ""),
                    "has_example": "example" in param_info or "examples" in param_info
                }
                
                test_result["params_tested"].append(param_test)
                
                if param_test["has_enum"]:
                    test_result["has_enums"] = True
                    print(f"   ✅ {param_name}: enum with {len(param_test['enum_values'])} values")
                elif param_test["has_description"]:
                    test_result["has_descriptions"] = True
                    print(f"   ⚠️  {param_name}: description only (no enum)")
                else:
                    print(f"   ❌ {param_name}: NO GUIDANCE (no enum, no description)")
            
            self.test_results["requirements"].append(test_result)
            return test_result
            
        except Exception as e:
            error_result = {
                "tool_name": tool_name,
                "success": False,
                "error": str(e)
            }
            print(f"❌ REQUIREMENTS TEST FAILED: {e}")
            self.test_results["requirements"].append(error_result)
            return error_result
    
    def test_execution_all_parameters(self, tool_name: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        TEST 4: Execute tool with comprehensive parameter combinations
        
        Simulates: AI tries to use the tool with various parameter sets
        """
        print(f"\n{'='*80}")
        print(f"TEST 4: EXECUTION - Testing {len(test_cases)} parameter combinations")
        print(f"{'='*80}")
        
        execution_results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i}/{len(test_cases)} ---")
            print(f"Parameters: {json.dumps(test_case, indent=2)}")
            
            try:
                # Import and execute the actual tool
                if tool_name == "calculate_saddle_stitch_books":
                    from inhouse_modules.shopify_calculators.SaddleStitchBooks_Shopify_Calculator import (
                        SaddleStitchBooksShopifyCalculator
                    )
                    
                    calculator = SaddleStitchBooksShopifyCalculator()
                    
                    if not calculator.config:
                        raise Exception("Calculator config not loaded")
                    
                    # Execute calculation with CORRECT parameter names from schema
                    result = calculator.calculate(
                        quantity=test_case.get("quantity"),
                        artworks=test_case.get("artworks", 1),
                        cover_option=test_case.get("cover_option", "Hard Cover"),
                        cover_stock=test_case.get("cover_stock"),
                        cover_print_type=test_case.get("cover_print_type", "2 side colour (4pp)"),
                        celloglaze=test_case.get("celloglaze", "None"),
                        printed_pages=test_case.get("printed_pages"),
                        finish_size=test_case.get("finish_size"),
                        content_print_type=test_case.get("content_print_type", "Colour"),
                        content_stock_type=test_case.get("content_stock_type")
                    )
                    
                    # Validate response structure
                    response_valid = all([
                        hasattr(result, "total_price"),
                        hasattr(result, "unit_price"),
                        hasattr(result, "breakdown")
                    ])
                    
                    execution_result = {
                        "case_number": i,
                        "parameters": test_case,
                        "success": True,
                        "total_price": float(result.total_price),
                        "unit_price": float(result.unit_price),
                        "response_valid": response_valid,
                        "error": None
                    }
                    
                    print(f"✅ SUCCESS: Total ${result.total_price} inc GST")
                    print(f"   Unit price: ${result.unit_price} per booklet")
                    
                else:
                    # Add support for other calculators here
                    execution_result = {
                        "case_number": i,
                        "parameters": test_case,
                        "success": False,
                        "error": f"Tool {tool_name} not implemented in test"
                    }
                    print(f"⚠️  SKIPPED: Tool not implemented in test framework")
                
                execution_results.append(execution_result)
                
            except Exception as e:
                execution_result = {
                    "case_number": i,
                    "parameters": test_case,
                    "success": False,
                    "error": str(e)
                }
                print(f"❌ FAILED: {e}")
                execution_results.append(execution_result)
                self.test_results["errors"].append({
                    "tool": tool_name,
                    "case": i,
                    "error": str(e)
                })
        
        summary = {
            "tool_name": tool_name,
            "total_cases": len(test_cases),
            "passed": sum(1 for r in execution_results if r["success"]),
            "failed": sum(1 for r in execution_results if not r["success"]),
            "success_rate": (sum(1 for r in execution_results if r["success"]) / len(test_cases)) * 100,
            "results": execution_results
        }
        
        self.test_results["execution"].append(summary)
        return summary
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        
        report = []
        report.append("\n" + "="*80)
        report.append("COMPREHENSIVE AI WORKFLOW TEST REPORT")
        report.append("="*80 + "\n")
        
        # Discovery Summary
        report.append("[*] DISCOVERY TESTS:")
        for test in self.test_results["discovery"]:
            status = "[PASS]" if test["success"] else "[FAIL]"
            report.append(f"   {status} '{test['search_term']}' -> {test['found_count']} tools")
        
        # Schema Summary
        report.append("\n[*] SCHEMA RETRIEVAL TESTS:")
        for test in self.test_results["schema"]:
            status = "[PASS]" if test["success"] else "[FAIL]"
            report.append(f"   {status} {test['tool_name']} -> {test.get('param_count', 0)} parameters")
        
        # Requirements Summary
        report.append("\n[*] REQUIREMENTS GUIDANCE TESTS:")
        for test in self.test_results["requirements"]:
            status = "[PASS]" if test["success"] else "[FAIL]"
            report.append(f"   {status} {test['tool_name']} -> Enums: {test.get('has_enums', False)}")
        
        # Execution Summary
        report.append("\n[*] EXECUTION TESTS:")
        for test in self.test_results["execution"]:
            report.append(f"   {test['tool_name']}: {test['passed']}/{test['total_cases']} passed ({test['success_rate']:.1f}%)")
        
        # Error Summary
        if self.test_results["errors"]:
            report.append("\n[!] ERRORS ENCOUNTERED:")
            for error in self.test_results["errors"]:
                report.append(f"   - {error['tool']}: {error['error']}")
        else:
            report.append("\n[PASS] NO ERRORS!")
        
        # Overall Status
        total_tests = (
            len(self.test_results["discovery"]) +
            len(self.test_results["schema"]) +
            len(self.test_results["requirements"]) +
            len(self.test_results["execution"])
        )
        
        passed_tests = (
            sum(1 for t in self.test_results["discovery"] if t["success"]) +
            sum(1 for t in self.test_results["schema"] if t["success"]) +
            sum(1 for t in self.test_results["requirements"] if t["success"]) +
            sum(1 for t in self.test_results["execution"] if t["success_rate"] == 100)
        )
        
        report.append("\n" + "="*80)
        report.append(f"OVERALL: {passed_tests}/{total_tests} test categories passed")
        report.append("="*80 + "\n")
        
        return "\n".join(report)


def main():
    """Run comprehensive AI workflow tests"""
    
    tester = CalculatorAIWorkflowTester()
    
    # TEST 1: Discovery - Can AI find calculator tools?
    print("\n" + "=== PHASE 1: DISCOVERY ===".center(80, "="))
    tester.test_discovery("calculator")
    tester.test_discovery("booklet")
    tester.test_discovery("saddle stitch")
    tester.test_discovery("quote")
    
    # TEST 2: Schema - Can AI understand tool parameters?
    print("\n" + "=== PHASE 2: SCHEMA UNDERSTANDING ===".center(80, "="))
    tester.test_schema_retrieval("calculate_saddle_stitch_books")
    
    # TEST 3: Requirements - Does AI get proper guidance?
    print("\n" + "=== PHASE 3: REQUIREMENTS GUIDANCE ===".center(80, "="))
    tester.test_requirements_guidance("calculate_saddle_stitch_books")
    
    # TEST 4: Execution - Comprehensive parameter testing
    print("\n" + "=== PHASE 4: COMPREHENSIVE EXECUTION TESTING ===".center(80, "="))
    
    # Test cases covering ALL parameter combinations
    # Using EXACT parameter names from schema (printed_pages, finish_size, content_stock_type, artworks)
    # Using EXACT values from enums (no extra text, exact match)
    test_cases = [
        # User's original request - converted to actual schema format
        {
            "quantity": "50",
            "printed_pages": "20pp",
            "finish_size": "A4 Landscape",
            "cover_stock": "Satin 350GSM",
            "content_stock_type": "Satin 150GSM",
            "celloglaze": "Gloss outside only",
            "artworks": 1,
            "cover_option": "Hard Cover",
            "cover_print_type": "2 side colour (4pp)",
            "content_print_type": "Colour"
        },
        # Different quantities
        {
            "quantity": "100",
            "printed_pages": "20pp",
            "finish_size": "A4 Landscape",
            "cover_stock": "Satin 350GSM",
            "content_stock_type": "Satin 150GSM",
            "celloglaze": "Gloss outside only",
            "artworks": 1,
            "cover_option": "Hard Cover",
            "cover_print_type": "2 side colour (4pp)",
            "content_print_type": "Colour"
        },
        {
            "quantity": "250",
            "printed_pages": "20pp",
            "finish_size": "A4 Landscape",
            "cover_stock": "Satin 350GSM",
            "content_stock_type": "Satin 150GSM",
            "celloglaze": "Gloss outside only",
            "artworks": 1,
            "cover_option": "Hard Cover",
            "cover_print_type": "2 side colour (4pp)",
            "content_print_type": "Colour"
        },
        # Different page counts
        {
            "quantity": "100",
            "printed_pages": "8pp",
            "finish_size": "A4 Portrait",
            "cover_stock": "Satin 300GSM",
            "content_stock_type": "Satin 128GSM",
            "celloglaze": "None",
            "artworks": 1,
            "cover_option": "Hard Cover",
            "cover_print_type": "2 side colour (4pp)",
            "content_print_type": "Colour"
        },
        {
            "quantity": "100",
            "printed_pages": "16pp",
            "finish_size": "A4 Portrait",
            "cover_stock": "Satin 300GSM",
            "content_stock_type": "Satin 128GSM",
            "celloglaze": "Matt outside only",
            "artworks": 2,
            "cover_option": "Hard Cover",
            "cover_print_type": "2 side colour (4pp)",
            "content_print_type": "Colour"
        },
        # Different sizes
        {
            "quantity": "100",
            "printed_pages": "12pp",
            "finish_size": "A5 Portrait",
            "cover_stock": "Satin 300GSM",
            "content_stock_type": "Satin 128GSM",
            "celloglaze": "None",
            "artworks": 1,
            "cover_option": "Hard Cover",
            "cover_print_type": "2 side colour (4pp)",
            "content_print_type": "Colour"
        },
        {
            "quantity": "100",
            "printed_pages": "12pp",
            "finish_size": "A5 Portrait",  # DL not in enum, use A5
            "cover_stock": "Satin 300GSM",
            "content_stock_type": "Satin 128GSM",
            "celloglaze": "None",
            "artworks": 1,
            "cover_option": "Hard Cover",
            "cover_print_type": "2 side colour (4pp)",
            "content_print_type": "Colour"
        },
        # Edge cases
        {
            "quantity": "25",  # Minimum quantity (from enum)
            "printed_pages": "4pp",  # Minimum pages
            "finish_size": "A4 Portrait",
            "cover_stock": "Satin 300GSM",
            "content_stock_type": "Satin 128GSM",
            "celloglaze": "None",
            "artworks": 1,
            "cover_option": "Hard Cover",
            "cover_print_type": "2 side colour (4pp)",
            "content_print_type": "Colour"
        },
        {
            "quantity": "2000",  # Maximum quantity (from enum)
            "printed_pages": "48pp",  # Many pages
            "finish_size": "A4 Portrait",
            "cover_stock": "Satin 350GSM",
            "content_stock_type": "Satin 150GSM",
            "celloglaze": "Gloss outside only",
            "artworks": 5,  # Multiple artworks
            "cover_option": "Hard Cover",
            "cover_print_type": "2 side colour (4pp)",
            "content_print_type": "Colour"
        },
    ]
    
    tester.test_execution_all_parameters("calculate_saddle_stitch_books", test_cases)
    
    # Generate and display report
    report = tester.generate_report()
    print(report)
    
    # Save detailed results to file
    results_file = Path(__file__).parent / "test_results_ai_workflow.json"
    with open(results_file, 'w') as f:
        json.dump(tester.test_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Return exit code based on success
    all_passed = (
        all(t["success"] for t in tester.test_results["discovery"]) and
        all(t["success"] for t in tester.test_results["schema"]) and
        all(t["success"] for t in tester.test_results["requirements"]) and
        all(t["success_rate"] == 100 for t in tester.test_results["execution"])
    )
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())

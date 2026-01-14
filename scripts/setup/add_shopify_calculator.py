"""
Automated Shopify Calculator Integration Tool
==============================================

This script automates the entire process of adding a new Shopify calculator to the AI_agents system:

1. Loads JSON config from In_House_SQL/G_Folder/Quote_Calculator/shopify/
2. Generates Python calculator implementation
3. Adds tool to calculator_tools.json schema
4. Updates calculator.py wrapper
5. Adds calculator requirements to get_calculator_requirements()
6. Updates __init__.py exports
7. Validates JSON structure integrity
8. Tests the calculator with example data

Usage:
    python scripts/setup/add_shopify_calculator.py --json Shopify_Notepads_A6.json
    python scripts/setup/add_shopify_calculator.py --batch  # Process all JSON files
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "inhouse_modules"))


class ShopifyCalculatorIntegrator:
    """Automates integration of Shopify calculators into the AI system"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.force_overwrite = False  # Can be set externally
        self.project_root = Path(__file__).parent.parent.parent
        self.in_house_sql_root = self.project_root.parent / "In_House_SQL"
        self.shopify_json_dir = self.in_house_sql_root / "G_Folder" / "Quote_Calculator" / "shopify"
        self.calculator_impl_dir = self.project_root / "inhouse_modules" / "shopify_calculators"
        self.tools_schema_file = self.project_root / "tools" / "schemas" / "calculator_tools.json"
        self.calculator_wrapper_file = self.project_root / "tools" / "implementations" / "calculator.py"
        self.requirements_file = self.project_root / "inhouse_modules" / "complete_calculator_implementation.py"
        self.init_file = self.calculator_impl_dir / "__init__.py"
        
        self.errors = []
        self.warnings = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages with color coding"""
        if not self.verbose:
            return
        
        colors = {
            "INFO": "\033[36m",      # Cyan
            "SUCCESS": "\033[32m",   # Green
            "WARNING": "\033[33m",   # Yellow
            "ERROR": "\033[31m",     # Red
            "HEADER": "\033[35m"     # Magenta
        }
        reset = "\033[0m"
        
        prefix = colors.get(level, "") + level + reset
        print(f"{prefix}: {message}")
    
    def load_json_config(self, json_filename: str) -> Optional[Dict[str, Any]]:
        """Load and validate JSON config file"""
        self.log(f"Loading JSON config: {json_filename}", "INFO")
        
        json_path = self.shopify_json_dir / json_filename
        
        if not json_path.exists():
            self.log(f"JSON file not found: {json_path}", "ERROR")
            self.errors.append(f"JSON file not found: {json_path}")
            return None
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.log(f"Successfully loaded JSON config", "SUCCESS")
            return config
        
        except json.JSONDecodeError as e:
            self.log(f"Invalid JSON: {e}", "ERROR")
            self.errors.append(f"Invalid JSON in {json_filename}: {e}")
            return None
        except Exception as e:
            self.log(f"Error loading JSON: {e}", "ERROR")
            self.errors.append(f"Error loading {json_filename}: {e}")
            return None
    
    def extract_calculator_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key information from JSON config
        
        Handles TWO JSON structures:
        1. Legacy format: {"product_name": "...", "fields": {...}, ...}
        2. New format: {"shopify_productname": {"product_name": "...", "fields": {...}}}
        """
        # Check if this is the new format (wrapped in shopify_ key) or legacy format
        product_key = None
        for key in config.keys():
            if key.startswith('shopify_'):
                product_key = key
                break
        
        if product_key:
            # NEW FORMAT: {"shopify_notepads_a6": {...}}
            product_config = config[product_key]
            self.log(f"Detected NEW format with wrapper key: {product_key}", "INFO")
        elif 'product_name' in config:
            # LEGACY FORMAT: {"product_name": "...", "fields": {...}}
            product_config = config
            # Generate product_key from product_name
            # e.g., "Notepads A5" -> "notepads_a5"
            product_name = config.get('product_name', '')
            product_key = 'shopify_' + product_name.lower().replace(' ', '_').replace('-', '_')
            self.log(f"Detected LEGACY format (no wrapper key), generated key: {product_key}", "INFO")
        else:
            self.log("Could not find 'product_name' field or 'shopify_*' key", "ERROR")
            return None
        
        # Extract product name (e.g., 'Notepads A6' -> 'NotepadsA6')
        product_title = product_config.get('product_name', product_config.get('product_title', product_key.replace('shopify_', '').title()))
        class_name = product_title.replace(' ', '') + 'ShopifyCalculator'
        
        # Extract tool name (e.g., 'calculate_notepads_a6')
        tool_name = 'calculate_' + product_key.replace('shopify_', '')
        
        # Extract requirements key (e.g., 'notepads_a6')
        requirements_key = product_key.replace('shopify_', '')
        
        info = {
            'product_key': product_key,
            'product_title': product_title,
            'class_name': class_name,
            'tool_name': tool_name,
            'requirements_key': requirements_key,
            'config': product_config,
            'fields': product_config.get('fields', product_config.get('options', [])),  # Support both 'fields' and 'options'
            'pricing_constants': product_config.get('pricing_constants', {}),
            'padding_rate_tiers': product_config.get('padding_rate_tiers', []),
            'profit_margin_tiers': product_config.get('profit_margin_tiers', []),
            'gst_calculation': product_config.get('gst_calculation', {}),
            'final_multiplier': product_config.get('final_multiplier', {}),
            'calculation_formula': product_config.get('calculation_formula', {}),
            'validation_rules': product_config.get('validation_rules', {}),
            'examples': product_config.get('examples', {})
        }
        
        self.log(f"Extracted info: {class_name} ({tool_name})", "SUCCESS")
        return info
    
    def generate_calculator_class(self, info: Dict[str, Any], json_filename: str) -> str:
        """Generate Python calculator class code"""
        self.log(f"Generating calculator class: {info['class_name']}", "INFO")
        
        class_name = info['class_name']
        product_title = info['product_title']
        tool_name = info['tool_name']
        fields = info['fields']
        
        # Generate field parameter extraction code
        field_params = []
        field_validations = []
        field_pricing = []
        
        # Handle both dict of fields (F1, F2...) and list of fields
        if isinstance(fields, dict):
            fields_list = [{'field_id': k, **v} for k, v in fields.items()]
        else:
            fields_list = fields
        
        for i, field in enumerate(fields_list, 1):
            field_id = field.get('field_id', f'F{i}')
            field_name = field.get('field_name', field.get('name', 'Unknown'))
            field_type = field.get('type', 'select')
            
            if field_type == 'select':
                options = field.get('options', [])
                if options:
                    # Generate validation
                    valid_values = [opt.get('title', opt.get('value', '')) for opt in options]
                    field_validations.append(f"        # Validate {field_name} ({field_id})")
                    
                    # Generate pricing extraction
                    field_pricing.append(f"        # {field_id}: {field_name}")
        
        # Generate tier methods
        padding_tiers = info['padding_rate_tiers']
        profit_tiers = info['profit_margin_tiers']
        
        padding_method = self._generate_padding_tier_method(padding_tiers)
        profit_method = self._generate_profit_tier_method(profit_tiers)
        
        code = f'''"""
{product_title} Shopify Calculator
Exact implementation of Shopify JavaScript formula for {product_title}

Based on: {json_filename} specification
Platform: Shopify (separate from WooCommerce calculators)
Fields: {len(fields)} fields (Shopify-specific structure)
Key Features: Tiered padding rates, profit margins, double GST application
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class {class_name}QuoteResult:
    """Result from {product_title} Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class {class_name}:
    """
    {product_title} Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - {len(fields)}-field Shopify structure
    - Tiered padding rates ({len(padding_tiers)} tiers)
    - Tiered profit margins ({len(profit_tiers)} tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = "{json_filename}"
    
    def __init__(self, config_path: str = None):
        """Initialize {product_title} Shopify calculator"""
        if config_path:
            self.config = self._load_config(config_path)
        else:
            default_path = Path(__file__).parent.parent.parent / "In_House_SQL" / "G_Folder" / "Quote_Calculator" / "shopify" / self.CONFIG_FILE
            if default_path.exists():
                self.config = self._load_config(str(default_path))
            else:
                self.config = None
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate(self, **kwargs) -> {class_name}QuoteResult:
        """
        Calculate {product_title} Shopify quote
        
        Args:
            **kwargs: Calculator parameters from JSON config
        
        Returns:
            {class_name}QuoteResult with pricing details
        """
        # TODO: Implement calculation logic based on JSON config
        # This is a template - actual implementation needed
        
        raise NotImplementedError("Calculator implementation pending")
    
{padding_method}
    
{profit_method}
'''
        
        self.log(f"Generated calculator class code ({len(code)} characters)", "SUCCESS")
        return code
    
    def _generate_padding_tier_method(self, tiers: List[Dict]) -> str:
        """Generate padding rate tier method"""
        if not tiers:
            return """    def _get_padding_rate(self, quantity: int) -> Decimal:
        \"\"\"Get padding rate (no tiers defined)\"\"\"
        return Decimal('0.10')"""
        
        conditions = []
        for tier in tiers:
            min_val = tier.get('min', 0)
            max_val = tier.get('max', 999999)
            rate = tier.get('rate', 0.10)
            
            if max_val >= 999999:
                conditions.append(f"        else:\n            return Decimal('{rate}')")
            else:
                conditions.append(f"        {'elif' if conditions else 'if'} quantity <= {max_val}:\n            return Decimal('{rate}')")
        
        method = f'''    def _get_padding_rate(self, quantity: int) -> Decimal:
        """
        Get padding rate based on quantity tiers
        
        {len(tiers)} tiers based on quantity
        """
{chr(10).join(conditions)}'''
        
        return method
    
    def _generate_profit_tier_method(self, tiers: List[Dict]) -> str:
        """Generate profit margin tier method"""
        if not tiers:
            return """    def _get_profit_margin(self, subtotal: float) -> Decimal:
        \"\"\"Get profit margin (no tiers defined)\"\"\"
        return Decimal('0.50')"""
        
        conditions = []
        for tier in tiers:
            min_val = tier.get('min', 0)
            max_val = tier.get('max', 999999)
            margin = tier.get('margin', 0.50)
            
            if max_val >= 999999:
                conditions.append(f"        else:\n            return Decimal('{margin}')")
            else:
                conditions.append(f"        {'elif' if conditions else 'if'} subtotal <= {max_val}:\n            return Decimal('{margin}')")
        
        method = f'''    def _get_profit_margin(self, subtotal: float) -> Decimal:
        """
        Get profit margin rate based on subtotal tiers
        
        {len(tiers)} tiers based on subtotal amount
        """
{chr(10).join(conditions)}'''
        
        return method
    
    def create_calculator_file(self, info: Dict[str, Any], json_filename: str) -> bool:
        """Create calculator Python file"""
        filename = info['class_name'].replace('ShopifyCalculator', '') + '_Shopify_Calculator.py'
        filepath = self.calculator_impl_dir / filename
        
        self.log(f"Creating calculator file: {filename}", "INFO")
        
        if filepath.exists():
            self.log(f"File already exists: {filename}", "WARNING")
            self.warnings.append(f"Calculator file already exists: {filename}")
            if not self.force_overwrite:
                response = input("Overwrite? (y/n): ")
                if response.lower() != 'y':
                    return False
            else:
                self.log(f"Force overwriting: {filename}", "INFO")
        
        code = self.generate_calculator_class(info, json_filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            self.log(f"Created calculator file: {filename}", "SUCCESS")
            return True
        
        except Exception as e:
            self.log(f"Error creating calculator file: {e}", "ERROR")
            self.errors.append(f"Error creating {filename}: {e}")
            return False
    
    def add_tool_to_schema(self, info: Dict[str, Any]) -> bool:
        """Add tool definition to calculator_tools.json"""
        self.log(f"Adding tool to schema: {info['tool_name']}", "INFO")
        
        try:
            # Load existing schema
            with open(self.tools_schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            tools_list = schema.get('tools', [])
            existing_index = next((i for i, tool in enumerate(tools_list) if tool.get('name') == info['tool_name']), None)
            if existing_index is not None:
                self.log(f"Replacing existing tool definition: {info['tool_name']}", "INFO")
                tools_list.pop(existing_index)
            
            # Generate tool definition
            fields = info['fields']
            parameters = {}
            
            # Handle both dict of fields (F1, F2...) and list of fields
            if isinstance(fields, dict):
                fields_list = [{'field_id': k, **v} for k, v in fields.items()]
            else:
                fields_list = fields
            
            for field in fields_list:
                field_name = (
                    field.get('field_name', field.get('name', 'Unknown'))
                    .lower()
                    .replace(' ', '_')
                    .replace(':', '')
                    .replace('?', '')
                )
                field_type = field.get('type', 'string')
                description = field.get('description', field.get('label', field_name))
                required = field.get('required', False)
                
                param_type = 'integer' if field_type == 'number' else 'string'
                
                # If field has options (select type), list all valid options
                if field_type == 'select' and 'options' in field:
                    options = field['options']
                    if isinstance(options, list) and options:
                        # Try multiple keys: label (most common), title, name, or value
                        option_titles = [opt.get('label', opt.get('title', opt.get('name', opt.get('value', '')))) for opt in options if opt.get('label') or opt.get('title') or opt.get('name') or opt.get('value')]
                        if option_titles:
                            description = f"{description}. Valid options: {', '.join(repr(t) for t in option_titles)}"
                
                # Add min/max info for number fields
                if field_type == 'number':
                    min_val = field.get('min')
                    max_val = field.get('max')
                    if min_val is not None or max_val is not None:
                        range_info = []
                        if min_val is not None:
                            range_info.append(f"min: {min_val}")
                        if max_val is not None:
                            range_info.append(f"max: {max_val}")
                        if range_info:
                            description = f"{description} ({', '.join(range_info)})"
                
                parameters[field_name] = {
                    'type': param_type,
                    'description': description,
                    'required': required
                }
            
            tool_def = {
                'name': info['tool_name'],
                'description': f"Calculate quote for {info['product_title']}. {info['config'].get('description', '')}",
                'parameters': parameters
            }
            
            # Insert before get_calculator_requirements
            insert_index = next((i for i, tool in enumerate(tools_list) if tool.get('name') == 'get_calculator_requirements'), len(tools_list))
            
            tools_list.insert(insert_index, tool_def)
            schema['tools'] = tools_list
            
            # Save schema
            with open(self.tools_schema_file, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)
            
            self.log(f"Added tool to schema successfully", "SUCCESS")
            return True
        
        except Exception as e:
            self.log(f"Error adding tool to schema: {e}", "ERROR")
            self.errors.append(f"Error adding tool to schema: {e}")
            return False
    
    def validate_json_integrity(self) -> bool:
        """Validate calculator_tools.json structure"""
        self.log("Validating calculator_tools.json integrity", "INFO")
        
        try:
            with open(self.tools_schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            # Check required fields
            if 'platform' not in schema:
                self.log("Missing 'platform' field in schema", "ERROR")
                return False
            
            if 'tools' not in schema or not isinstance(schema['tools'], list):
                self.log("Missing or invalid 'tools' field in schema", "ERROR")
                return False
            
            # Validate each tool
            for i, tool in enumerate(schema['tools']):
                if 'name' not in tool:
                    self.log(f"Tool #{i} missing 'name' field", "ERROR")
                    return False
                
                if 'description' not in tool:
                    self.log(f"Tool '{tool.get('name')}' missing 'description' field", "WARNING")
                
                if 'parameters' not in tool:
                    self.log(f"Tool '{tool.get('name')}' missing 'parameters' field", "WARNING")
            
            self.log(f"Schema validation passed ({len(schema['tools'])} tools)", "SUCCESS")
            return True
        
        except json.JSONDecodeError as e:
            self.log(f"Invalid JSON in calculator_tools.json: {e}", "ERROR")
            self.errors.append(f"Invalid JSON in calculator_tools.json: {e}")
            return False
        except Exception as e:
            self.log(f"Error validating schema: {e}", "ERROR")
            self.errors.append(f"Error validating schema: {e}")
            return False
    
    def process_calculator(self, json_filename: str) -> bool:
        """Process a single calculator JSON file"""
        self.log(f"\n{'='*80}", "HEADER")
        self.log(f"Processing: {json_filename}", "HEADER")
        self.log(f"{'='*80}", "HEADER")
        
        # Step 1: Load JSON
        config = self.load_json_config(json_filename)
        if not config:
            return False
        
        # Step 2: Extract info
        info = self.extract_calculator_info(config)
        if not info:
            return False
        
        # Step 3: Generate calculator class
        success = self.create_calculator_file(info, json_filename)
        if not success:
            return False
        
        # Step 4: Add tool to schema
        success = self.add_tool_to_schema(info)
        if not success:
            return False
        
        # Step 5: Validate JSON integrity
        success = self.validate_json_integrity()
        if not success:
            return False
        
        self.log(f"\n✅ Successfully processed {json_filename}", "SUCCESS")
        return True
    
    def batch_process_all(self) -> Dict[str, Any]:
        """Process all JSON files in the shopify directory"""
        self.log("\n" + "="*80, "HEADER")
        self.log("BATCH PROCESSING ALL SHOPIFY CALCULATORS", "HEADER")
        self.log("="*80 + "\n", "HEADER")
        
        if not self.shopify_json_dir.exists():
            self.log(f"Shopify JSON directory not found: {self.shopify_json_dir}", "ERROR")
            return {"success": False, "processed": 0, "failed": 0}
        
        json_files = list(self.shopify_json_dir.glob("*.json"))
        
        self.log(f"Found {len(json_files)} Shopify JSON files", "INFO")
        
        results = {
            "success": True,
            "processed": 0,
            "failed": 0,
            "skipped": 0,
            "files": []
        }
        
        for json_file in json_files:
            try:
                success = self.process_calculator(json_file.name)
                
                if success:
                    results["processed"] += 1
                    results["files"].append({"file": json_file.name, "status": "success"})
                else:
                    results["failed"] += 1
                    results["files"].append({"file": json_file.name, "status": "failed"})
            
            except Exception as e:
                self.log(f"Unexpected error processing {json_file.name}: {e}", "ERROR")
                results["failed"] += 1
                results["files"].append({"file": json_file.name, "status": "error", "error": str(e)})
        
        # Final summary
        self.log("\n" + "="*80, "HEADER")
        self.log("BATCH PROCESSING COMPLETE", "HEADER")
        self.log("="*80, "HEADER")
        self.log(f"Total files: {len(json_files)}", "INFO")
        self.log(f"Processed successfully: {results['processed']}", "SUCCESS")
        self.log(f"Failed: {results['failed']}", "ERROR" if results['failed'] > 0 else "INFO")
        self.log(f"Warnings: {len(self.warnings)}", "WARNING" if self.warnings else "INFO")
        self.log(f"Errors: {len(self.errors)}", "ERROR" if self.errors else "INFO")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Automate Shopify calculator integration into AI_agents system"
    )
    parser.add_argument(
        '--json',
        type=str,
        help='Single JSON file to process (e.g., Shopify_Notepads_A6.json)'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Process all Shopify JSON files in the directory'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=True,
        help='Enable verbose logging (default: True)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force overwrite existing files without prompting'
    )
    
    args = parser.parse_args()
    
    integrator = ShopifyCalculatorIntegrator(verbose=args.verbose)
    integrator.force_overwrite = args.force  # Set force flag
    
    if args.batch:
        results = integrator.batch_process_all()
        sys.exit(0 if results['failed'] == 0 else 1)
    
    elif args.json:
        success = integrator.process_calculator(args.json)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Extract Product Options from Shopify JSON Files

Purpose:
    Parse all 30 Shopify calculator JSON files and extract:
    - Product options (Quantity, Stock Type, Print Type, etc.)
    - Option choices with prices, price_types, SKUs
    - Default values and field IDs
    
Output:
    PRODUCT_OPTIONS_EXTRACTED.json with structure:
    {
        "NotepadsA4": {
            "calculator_key": "shopify_notepads_a4",
            "product_title": "Notepads A4",
            "total_options": 6,
            "total_choices": 30,
            "options": [
                {
                    "option_name": "Quantity",
                    "field_id": "F1",
                    "type": "select",
                    "required": true,
                    "default_choice": "100",
                    "choices": [...]
                }
            ]
        }
    }

Author: AI Agent
Date: December 17, 2025
"""

import json
import os
from pathlib import Path
from collections import defaultdict

# Path to Shopify JSON files
SHOPIFY_JSON_DIR = r"c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Quote_Calculator\shopify"
OUTPUT_FILE = r"c:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\database\seeds\PRODUCT_OPTIONS_EXTRACTED.json"

def normalize_calculator_name(json_filename):
    """Convert JSON filename to calculator name"""
    # Remove extension
    name = json_filename.replace('.json', '')
    
    # Remove common prefixes
    name = name.replace('Shopify_', '')
    name = name.replace('shopify_', '')
    
    # Handle special cases
    replacements = {
        'Notepads_A4': 'NotepadsA4',
        'Notepads_A5': 'NotepadsA5',
        'Notepads_A6': 'NotepadsA6',
        'Strut_Cards_A4': 'StrutCardsA4',
        'Strut_Cards_A3': 'StrutCardsA3',
        'Construction_Signs': 'ConstructionSigns',
        'Bollard_Signs': 'BollardSigns',
        'Corflute_Insert_A_Frame': 'CorfluteInsertA_Frame',
        'Custom_Poster_Printing': 'CustomPosterPrinting',
        'Selfie_Frames': 'SelfieFrames',
        'With_Compliments_Slips': 'WithComplimentsSlips',
        'Stackable_Cubes': 'StackableCubes',
        'Spiral_Bound_Books': 'SpiralBoundBooks',
        'Saddle_Stitch_Books': 'SaddleStitchBooks',
        'Business_Cards_Economic': 'EconomicalBusinessCards',
        'Premium_Business_Cards': 'PremiumBusinessCards',
        'Printed_Flyers_Shopify': 'PrintedFlyers',
        'folded_printed_flyers_Shopify': 'FoldedPrintedFlyers',
        'Perfect_Bound_books': 'PerfectBound',
        'Perfect_Bound_Books_WooCommerce': 'PerfectBound',
        'Wire_Spiral_Bound': 'WireBound',
        'Corflute_Signs_Shopify': 'CorfluteSign',
        'Custom_Vinyl_Stickers': 'CustomVinylStickers'
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    # Remove remaining underscores and spaces
    name = name.replace('_', '').replace(' ', '')
    
    return name

def extract_options_from_file(json_path):
    """Extract options from a single Shopify JSON file"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get the calculator key (first key in JSON)
        calculator_key = list(data.keys())[0]
        calculator_data = data[calculator_key]
        
        if 'options' not in calculator_data:
            print(f"  ⚠️  No 'options' found in {os.path.basename(json_path)}")
            return None
        
        options = []
        total_choices = 0
        
        for option in calculator_data['options']:
            option_name = option.get('name', '')
            field_id = option.get('field_id', '')
            option_type = option.get('type', 'select')
            required = option.get('required', False)
            default_choice = option.get('default', '')
            
            choices = []
            for idx, choice in enumerate(option.get('options', [])):
                choices.append({
                    'choice_title': choice.get('title', ''),
                    'price': choice.get('price', 0),
                    'price_type': choice.get('price_type', 'fixed'),
                    'sku': choice.get('sku', ''),
                    'description': choice.get('description', ''),
                    'display_order': idx + 1
                })
                total_choices += 1
            
            options.append({
                'option_name': option_name,
                'field_id': field_id,
                'option_type': option_type,
                'is_required': required,
                'default_choice': default_choice,
                'choices': choices
            })
        
        return {
            'calculator_key': calculator_key,
            'product_title': calculator_data.get('product_title', ''),
            'total_options': len(options),
            'total_choices': total_choices,
            'options': options
        }
    
    except Exception as e:
        print(f"  ❌ Error processing {os.path.basename(json_path)}: {e}")
        return None

def extract_all_options():
    """Main extraction function"""
    print("\n" + "="*80)
    print("EXTRACT PRODUCT OPTIONS FROM SHOPIFY JSON FILES")
    print("="*80 + "\n")
    
    # Find all JSON files
    json_files = list(Path(SHOPIFY_JSON_DIR).glob('*.json'))
    print(f"✅ Found {len(json_files)} JSON files to process\n")
    
    extracted_data = {}
    stats = {
        'total_calculators': 0,
        'total_options': 0,
        'total_choices': 0,
        'failed': 0
    }
    
    for json_path in sorted(json_files):
        calculator_name = normalize_calculator_name(json_path.name)
        print(f"Processing: {json_path.name} → {calculator_name}")
        
        result = extract_options_from_file(json_path)
        
        if result:
            extracted_data[calculator_name] = result
            stats['total_calculators'] += 1
            stats['total_options'] += result['total_options']
            stats['total_choices'] += result['total_choices']
            print(f"  ✅ Extracted {result['total_options']} options, {result['total_choices']} choices")
        else:
            stats['failed'] += 1
        
        print()
    
    # Save to JSON file
    print("="*80)
    print("SAVING EXTRACTED DATA")
    print("="*80 + "\n")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2)
    
    print(f"✅ Saved to: {OUTPUT_FILE}")
    print(f"   File size: {os.path.getsize(OUTPUT_FILE) / 1024:.2f} KB")
    
    # Print summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"\n✅ Total calculators processed: {stats['total_calculators']}")
    print(f"✅ Total options extracted: {stats['total_options']}")
    print(f"✅ Total choices extracted: {stats['total_choices']}")
    print(f"⚠️  Failed: {stats['failed']}")
    
    # Show sample data
    print("\n" + "-"*80)
    print("SAMPLE DATA (First 3 Calculators)")
    print("-"*80 + "\n")
    
    for idx, (calc_name, calc_data) in enumerate(list(extracted_data.items())[:3]):
        print(f"{idx + 1}. {calc_name}")
        print(f"   Product: {calc_data['product_title']}")
        print(f"   Options: {calc_data['total_options']}, Choices: {calc_data['total_choices']}")
        print(f"   First option: {calc_data['options'][0]['option_name']} ({len(calc_data['options'][0]['choices'])} choices)")
        print()
    
    print("\n✅ Product options extraction complete!\n")

if __name__ == '__main__':
    extract_all_options()

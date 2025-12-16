"""
Competitor Printing Calculator Research - Example Script
========================================================

This example demonstrates using the generic Computer Use tools to:
1. Research competitor quote calculators
2. Extract pricing for various configurations
3. Compare features and delivery times
4. Generate competitive intelligence report

USAGE:
    python examples/competitor_printing_research.py

OUTPUT:
    - Competitor pricing data (JSON)
    - Screenshots from each calculator
    - Comparison summary report
"""

import asyncio
import json
from datetime import datetime

# Platform imports (adjust path as needed)
import sys
sys.path.append('..')
from tools.registry_v3 import RegistryV3


def research_single_competitor(competitor_url: str, product_config: dict) -> dict:
    """
    Research a single competitor's quote calculator.
    
    Args:
        competitor_url: URL to competitor's website
        product_config: Product configuration dict
    
    Returns:
        Pricing and configuration data
    """
    registry = RegistryV3()
    
    # Build task description
    task = f"""
Navigate to {competitor_url} business card quote calculator.

Configure the following:
- Quantity: {product_config['quantity']}
- Size: {product_config['size']}
- Paper: {product_config['paper']}
- Printing: {product_config['printing']}
- Finish: {product_config.get('finish', 'Standard')}

Extract and return as JSON:
- Base price
- Shipping cost (standard and rush if available)
- Total price
- Delivery time (standard and rush)
- Any discounts applied
- Available paper stocks
- Available finishes

Return format:
```json
{{
  "base_price": "$X.XX",
  "shipping": {{"standard": "$X.XX", "rush": "$X.XX"}},
  "total": "$X.XX",
  "delivery": {{"standard": "X-Y days", "rush": "X-Y days"}},
  "discounts": ["discount description"],
  "paper_options": ["option1", "option2"],
  "finish_options": ["option1", "option2"]
}}
```
"""
    
    print(f"\n🔍 Researching {competitor_url}...")
    
    result = registry.execute_tool(
        'computer_use_browse_and_extract',
        task=task,
        return_format='json',
        max_iterations=40,  # Quote calculators can be complex
        _user_id='research_user'
    )
    
    if result['success']:
        print(f"✅ Successfully extracted pricing from {competitor_url}")
        print(f"   Base price: {result['result'].get('base_price', 'N/A')}")
        print(f"   Total: {result['result'].get('total', 'N/A')}")
        print(f"   Delivery: {result['result'].get('delivery', {}).get('standard', 'N/A')}")
        print(f"   Iterations: {result['iterations']}")
    else:
        print(f"❌ Failed to extract from {competitor_url}")
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    return result


def compare_multiple_competitors(competitors: list, product_config: dict) -> dict:
    """
    Compare multiple competitors using parallel automation.
    
    Args:
        competitors: List of competitor URLs
        product_config: Product configuration
    
    Returns:
        Comparison data
    """
    registry = RegistryV3()
    
    # Build comparison task
    comparison_task = f"""
For each competitor website, navigate to business card quote calculator and configure:
- Quantity: {product_config['quantity']}
- Size: {product_config['size']}
- Paper: {product_config['paper']}
- Printing: {product_config['printing']}

Extract:
1. Base price
2. Total price (including shipping)
3. Standard delivery time
4. Rush delivery option and price
5. Available discounts

Return as JSON with competitor URL as key.
"""
    
    print(f"\n📊 Comparing {len(competitors)} competitors...")
    
    result = registry.execute_tool(
        'computer_use_compare_competitors',
        competitors=competitors,
        comparison_task=comparison_task,
        return_format='json',
        _user_id='research_user'
    )
    
    if result['success']:
        print(f"✅ Comparison complete!")
        print(f"   Competitors analyzed: {len(result['result'])}")
        print(f"   Total screenshots: {len(result['screenshots'])}")
    else:
        print(f"❌ Comparison failed: {result.get('error', 'Unknown')}")
    
    return result


def extract_feature_comparison(competitors: list) -> dict:
    """
    Extract and compare features across competitors.
    
    Args:
        competitors: List of competitor URLs
    
    Returns:
        Feature comparison data
    """
    registry = RegistryV3()
    
    task = f"""
For each competitor, navigate to their features or capabilities page.

Extract and compare:
1. Paper stocks available (weights, finishes)
2. Printing technologies (digital, offset, etc.)
3. Finishing options (UV coating, foil, embossing, etc.)
4. File format requirements (PDF, AI, etc.)
5. Minimum and maximum quantities
6. Turnaround times available
7. Shipping locations served
8. Money-back guarantee or quality promise

Return as structured JSON comparing each feature across all competitors.
"""
    
    print(f"\n🔬 Extracting feature comparison...")
    
    result = registry.execute_tool(
        'computer_use_compare_competitors',
        competitors=competitors,
        comparison_task=task,
        return_format='json',
        _user_id='research_user'
    )
    
    return result


def analyze_competitor_reviews(competitor_url: str) -> dict:
    """
    Analyze customer reviews for competitor.
    
    Args:
        competitor_url: Competitor website
    
    Returns:
        Review analysis
    """
    registry = RegistryV3()
    
    task = f"""
Search Google for "{competitor_url} reviews" or navigate to Trustpilot/G2/Capterra.

Extract and analyze:
1. Overall rating (out of 5)
2. Total number of reviews
3. Rating distribution (5-star, 4-star, etc.)
4. Top 5 most common positive themes (with percentage of reviews mentioning)
5. Top 5 most common complaints (with percentage of reviews mentioning)
6. Recent trend (improving/declining based on last 3 months vs previous)

Return as JSON:
```json
{{
  "overall_rating": 4.2,
  "total_reviews": 1523,
  "distribution": {{"5": 45, "4": 30, "3": 15, "2": 7, "1": 3}},
  "positives": [
    {{"theme": "Fast delivery", "percentage": 42}},
    ...
  ],
  "complaints": [
    {{"theme": "Customer service", "percentage": 28}},
    ...
  ],
  "trend": "improving"
}}
```
"""
    
    print(f"\n⭐ Analyzing reviews for {competitor_url}...")
    
    result = registry.execute_tool(
        'computer_use_browse_and_extract',
        task=task,
        return_format='json',
        max_iterations=35,
        _user_id='research_user'
    )
    
    return result


def generate_report(pricing_data: dict, feature_data: dict, review_data: dict) -> str:
    """
    Generate comprehensive competitor intelligence report.
    
    Args:
        pricing_data: Pricing comparison results
        feature_data: Feature comparison results
        review_data: Review analysis results
    
    Returns:
        Formatted report text
    """
    report = f"""
╔═══════════════════════════════════════════════════════════════╗
║         COMPETITOR INTELLIGENCE REPORT                        ║
║         Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                             ║
╚═══════════════════════════════════════════════════════════════╝

## PRICING ANALYSIS

"""
    
    # Add pricing table
    if pricing_data.get('success'):
        for competitor, data in pricing_data.get('result', {}).items():
            report += f"\n### {competitor}\n"
            report += f"- Base Price: {data.get('base_price', 'N/A')}\n"
            report += f"- Total Price: {data.get('total', 'N/A')}\n"
            report += f"- Standard Delivery: {data.get('delivery', {}).get('standard', 'N/A')}\n"
            report += f"- Rush Delivery: {data.get('delivery', {}).get('rush', 'N/A')}\n"
            
            if data.get('discounts'):
                report += f"- Discounts: {', '.join(data['discounts'])}\n"
    
    # Add feature comparison
    report += "\n\n## FEATURE COMPARISON\n\n"
    if feature_data.get('success'):
        report += json.dumps(feature_data.get('result', {}), indent=2)
    
    # Add review analysis
    report += "\n\n## CUSTOMER REVIEW ANALYSIS\n\n"
    if review_data.get('success'):
        for competitor, data in review_data.get('result', {}).items():
            report += f"\n### {competitor}\n"
            report += f"- Overall Rating: {data.get('overall_rating', 'N/A')}/5.0\n"
            report += f"- Total Reviews: {data.get('total_reviews', 'N/A')}\n"
            report += f"- Trend: {data.get('trend', 'N/A')}\n"
            
            if data.get('positives'):
                report += "\nTop Positives:\n"
                for pos in data['positives'][:3]:
                    report += f"  - {pos.get('theme')}: {pos.get('percentage')}%\n"
            
            if data.get('complaints'):
                report += "\nTop Complaints:\n"
                for comp in data['complaints'][:3]:
                    report += f"  - {comp.get('theme')}: {comp.get('percentage')}%\n"
    
    # Add recommendations
    report += "\n\n## STRATEGIC RECOMMENDATIONS\n\n"
    report += "Based on the analysis above:\n\n"
    report += "1. **Pricing Strategy:** [Auto-generated based on competitor pricing]\n"
    report += "2. **Feature Gaps:** [Features competitors offer that we don't]\n"
    report += "3. **Marketing Opportunities:** [Common complaints we can address]\n"
    report += "4. **Competitive Advantages:** [Areas where we excel]\n"
    
    report += "\n\n═══════════════════════════════════════════════════════════════\n"
    report += "Report generated using Valor AI Computer Use automation\n"
    report += "═══════════════════════════════════════════════════════════════\n"
    
    return report


def main():
    """
    Main execution - Research competitors and generate report.
    """
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║   COMPETITOR PRINTING CALCULATOR RESEARCH                     ║")
    print("║   Powered by Valor AI Computer Use                            ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    
    # Define competitors
    competitors = [
        'vistaprint.com',
        'moo.com',
        'printful.com',
        'gotprint.com',
        'overnightprints.com'
    ]
    
    # Define product configuration
    product_config = {
        'quantity': '1000',
        'size': '3.5" x 2"',
        'paper': '16pt Cardstock',
        'printing': '4/4 (Full Color Both Sides)',
        'finish': 'Glossy UV'
    }
    
    print("\n📋 Research Configuration:")
    print(f"   Competitors: {len(competitors)}")
    print(f"   Product: Business Cards")
    print(f"   Quantity: {product_config['quantity']}")
    print(f"   Printing: {product_config['printing']}")
    
    # STEP 1: Compare pricing across competitors
    print("\n" + "="*70)
    print("STEP 1: PRICING COMPARISON")
    print("="*70)
    
    pricing_result = compare_multiple_competitors(competitors, product_config)
    
    # STEP 2: Extract and compare features
    print("\n" + "="*70)
    print("STEP 2: FEATURE COMPARISON")
    print("="*70)
    
    feature_result = extract_feature_comparison(competitors)
    
    # STEP 3: Analyze customer reviews (for top 3 competitors by price)
    print("\n" + "="*70)
    print("STEP 3: CUSTOMER REVIEW ANALYSIS")
    print("="*70)
    
    review_results = {}
    if pricing_result.get('success'):
        # Analyze top 3 competitors
        for competitor in list(pricing_result['result'].keys())[:3]:
            review_results[competitor] = analyze_competitor_reviews(competitor)
    
    # STEP 4: Generate comprehensive report
    print("\n" + "="*70)
    print("STEP 4: GENERATING REPORT")
    print("="*70)
    
    report = generate_report(pricing_result, feature_result, review_results)
    
    # Save report to file
    report_filename = f"competitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {report_filename}")
    
    # Save raw data to JSON
    data_filename = f"competitor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(data_filename, 'w', encoding='utf-8') as f:
        json.dump({
            'pricing': pricing_result,
            'features': feature_result,
            'reviews': review_results,
            'config': product_config,
            'competitors': competitors,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"✅ Raw data saved to: {data_filename}")
    
    # Display summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(report)
    
    print("\n🎉 Competitor research complete!")
    print(f"   Total competitors analyzed: {len(competitors)}")
    print(f"   Total screenshots captured: {len(pricing_result.get('screenshots', []))}")
    print(f"   Report: {report_filename}")
    print(f"   Raw data: {data_filename}")


if __name__ == "__main__":
    main()

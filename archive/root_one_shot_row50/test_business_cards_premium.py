import sys
sys.path.insert(0, 'C:/Users/gpoli/GIT/AI_Agents_V11/AI_agents/UI/modules_external/quote-calculator/backend/shopify_calculators')
from business_card_calculator_shopify import ShopifyBusinessCardCalculator, PrintType, FinishSize, StockTypePremium, CelloglazePremium
from decimal import Decimal

calc = ShopifyBusinessCardCalculator()

print("="*80)
print("PREMIUM BUSINESS CARDS - WEBSITE VALIDATION TEST")
print("="*80)
print()

# TEST: Website config - 1000 qty, King Kong, Double sided, Colour, 2 Side Gloss, 1 artwork
print("TEST: 1000 qty, King Kong 420GSM, Double sided, Colour, 2 Side Gloss, 1 artwork")
print("-"*80)
result = calc.calculate_premium_business_cards(
    quantity=1000,
    sides=2,
    print_type=PrintType.COLOR,
    finish_size=FinishSize.STANDARD_90X55,
    stock_type=StockTypePremium.KINGKONG_420GSM,
    celloglaze=CelloglazePremium.TWO_SIDE_GLOSS,
    artworks=1
)

website_price = Decimal('161.70')
difference = abs(result.total_inc_gst - website_price)

print(f'Backend Result: ${result.total_inc_gst:.2f}')
print(f'Website Price: ${website_price:.2f}')
print(f'Difference: ${difference:.2f}')
print(f'Status: {"PASS" if difference < 1 else "FAIL"}')
print(f'\nCost Breakdown:')
print(f'  Setup: ${result.cost_breakdown["setup_cost"]:.2f}')
print(f'  Paper: ${result.cost_breakdown["paper_cost"]:.2f}')
print(f'  Clicks: ${result.cost_breakdown["click_cost"]:.2f}')
print(f'  Cutting: ${result.cost_breakdown["cutting_cost"]:.2f}')
print(f'  Celloglaze: ${result.cost_breakdown["celloglaze_cost"]:.2f}')
print(f'  Profit ({result.profit_margin_pct:.0f}%): ${result.cost_breakdown["profit_margin"]:.2f}')
print(f'  Unit Price: ${result.unit_price_inc_gst:.4f}/card')

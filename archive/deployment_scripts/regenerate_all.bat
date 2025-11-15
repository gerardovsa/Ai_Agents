@echo off
echo ============================================================================
echo REGENERATING 9 RECENT CALCULATORS WITH IMPROVED SCHEMA
echo ============================================================================
echo.

cd C:\Users\gpoli\GIT\AI_agents

python scripts\setup\add_shopify_calculator.py --json Shopify_Saddle_Stitch_Books.json --force
echo.

python scripts\setup\add_shopify_calculator.py --json Shopify_Spiral_Bound_Books.json --force
echo.

python scripts\setup\add_shopify_calculator.py --json Shopify_Bollard_Signs.json --force
echo.

python scripts\setup\add_shopify_calculator.py --json Shopify_Stackable_Cubes.json --force
echo.

python scripts\setup\add_shopify_calculator.py --json Shopify_Election_Signs.json --force
echo.

python scripts\setup\add_shopify_calculator.py --json Shopify_Selfie_Frames.json --force
echo.

python scripts\setup\add_shopify_calculator.py --json Shopify_Construction_Signs.json --force
echo.

python scripts\setup\add_shopify_calculator.py --json Shopify_Strut_Cards_A3.json --force
echo.

python scripts\setup\add_shopify_calculator.py --json Shopify_Strut_Cards_A4.json --force
echo.

echo ============================================================================
echo REGENERATION COMPLETE
echo ============================================================================

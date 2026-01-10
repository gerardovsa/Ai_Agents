"""
Verify ML Routes - Check all route definitions without running Flask
"""

import re

ML_ROUTES_FILE = "AI_infrastructure/routes/ml_routes.py"

print("=" * 80)
print("ML ROUTES VERIFICATION")
print("=" * 80)

with open(ML_ROUTES_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all route definitions
route_pattern = r"@ml_bp\.route\('([^']+)'.*?\)\s*@cross_origin\(\)\s*def\s+(\w+)"
matches = re.findall(route_pattern, content, re.MULTILINE | re.DOTALL)

print(f"\n✅ Found {len(matches)} ML route definitions:\n")

expected_routes = [
    ("/dashboard/summary", "Dashboard Summary"),
    ("/predict/churn/<contact_id>", "Churn Prediction"),
    ("/predict/ltv/<contact_id>", "LTV Prediction"),
    ("/predict/payment/<invoice_id>", "Payment Timing"),
    ("/forecast/revenue", "Revenue Forecast"),
    ("/analytics/customer/segments", "Customer Segmentation"),
    ("/detect/anomalies/invoice", "Invoice Anomaly Detection")
]

print("Route Path".ljust(40), "Function Name".ljust(35), "Status")
print("-" * 80)

found_paths = [m[0] for m in matches]

for expected_path, description in expected_routes:
    if expected_path in found_paths:
        match = next(m for m in matches if m[0] == expected_path)
        print(f"{expected_path.ljust(40)} {match[1].ljust(35)} ✅ FOUND")
    else:
        print(f"{expected_path.ljust(40)} {'???'.ljust(35)} ❌ MISSING")

print("\n" + "=" * 80)
print(f"SUMMARY: {len([p for p, _ in expected_routes if p in found_paths])}/{len(expected_routes)} expected routes found")
print("=" * 80)

# Show actual routes found
print("\n📋 Complete route list from file:\n")
for i, (path, func) in enumerate(matches, 1):
    print(f"  {i}. {path} → {func}()")

from app import app

print("\n=== Registered Blueprints ===")
for bp_name, bp in app.blueprints.items():
    print(f"  ✅ {bp_name}")

print("\n=== Auth Routes ===")
for rule in app.url_map.iter_rules():
    if '/auth/' in str(rule):
        print(f"  {list(rule.methods)} {rule.rule}")

# 🚀 Quick Start: Calculator Tools

##  What's Done
- 7 calculator tools integrated
- 576 total tools loaded
- Schema + implementation created
- Tests passing

## 🎯 Next Step (CRITICAL)
**Restart Flask server to activate calculator tools:**

```powershell
# From any directory (PATH command):
BISTART

# Or manually:
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
python flask_app.py
```

## 🧪 Test Queries

Once server restarted, try these:

### Test 1: Business Cards
```
"Calculate a quote for 1,000 business cards, double-sided, 350GSM Satin"
```

**Expected**: AI calls `calculate_business_cards` tool, returns price breakdown

### Test 2: Flyers
```
"How much for 5,000 A4 flyers, 170GSM, full color both sides?"
```

**Expected**: AI calls `calculate_flyers` tool with dimensions 210x297mm

### Test 3: Requirements
```
"What information do you need to calculate a corflute sign quote?"
```

**Expected**: AI calls `get_calculator_requirements` tool, lists parameters

## 📋 Available Calculator Tools

1. `calculate_business_cards` - Business cards (Shopify pricing)
2. `calculate_flyers` - Flyers/leaflets (also handles business cards)
3. `calculate_perfect_bound_books` - Books with glued spine
4. `calculate_corflute_signs` - Rigid signage
5. `calculate_booklets` - Stapled booklets
6. `get_stock_list` - Available paper stocks
7. `get_calculator_requirements` - Parameter requirements

## 🔍 Verify Tools Loaded

After restart, check server logs for:
```
[SCHEMA] Loaded: calculate_flyers
[SCHEMA] Loaded: calculate_business_cards
[IMPL] Loaded: calculator
[OK] Tool Registry ready - 576 tools loaded
```

## 🎯 Success Criteria

 Server starts without errors  
 Calculator tools appear in logs  
 AI responds to test queries with quotes  
 Quotes include price breakdown  

## 📚 Documentation

- `CALCULATOR_INTEGRATION_COMPLETE.md` - Full summary
- `COMPLETE_AI_TOOL_FLOW_EXPLANATION.md` - Architecture details
- `.github/copilot-instructions.md` - Updated with calculator info

## ⚠️ Troubleshooting

**Issue**: "Calculator not available"  
**Fix**: Check In_House_SQL project accessible at `C:\Users\gpoli\GIT\In_House_SQL\G_Folder`

**Issue**: Tools not found  
**Fix**: Restart Flask server with `BISTART`

**Issue**: Calculation error  
**Fix**: Check SQL Server connection at `3.25.76.138\INHPSQLSERVER`

---

## 🎉 You're Ready!

Run `BISTART` and test the calculator tools!

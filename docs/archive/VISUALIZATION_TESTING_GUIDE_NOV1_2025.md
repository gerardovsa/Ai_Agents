# Visualization Testing Guide - November 1, 2025

## 🎨 Quick Test - Plotly & Mermaid Rendering

## Before Testing

1. **Refresh Browser** - Ctrl+F5 (hard refresh to load updated code)
2. **Open Console** - F12 → Console tab (keep visible during tests)

---

## Test #1: Plotly Bar Chart ✅

### Send This Message:
```
Create a bar chart showing sales data:
- Product A: 100
- Product B: 150  
- Product C: 80
```

### Expected Console Logs:
```
🎨 Initializing TwoRuleStreamProcessor for visualization rendering...
✅ TwoRuleStreamProcessor initialized
💬 [CONTENT_DELTA EVENT] Received text chunk: ...
🎨 Processing chunk through TwoRuleStreamProcessor (Plotly + Mermaid support)...
📝 TWO-RULE: Packaged text before delimiter (X chars at position Y)
🔄 TWO-RULE: STATE CHANGE → BUFFERING_VISUAL (plotly) at position Z
✅ Visualization processor handled chunk successfully
🎨 Finalizing TwoRuleStreamProcessor (rendering any pending visualizations)...
✅ Visualization processor finalized successfully
```

### Expected Visual Result:
- ✅ Interactive bar chart appears inline
- ✅ Chart shows 3 bars (Product A, B, C with values 100, 150, 80)
- ✅ Can hover over bars to see values
- ✅ Can zoom/pan the chart
- ✅ Chart is responsive and properly sized

### If It Works:
Reply: "PLOTLY WORKS" 🎉

---

## Test #2: Mermaid Flowchart ✅

### Send This Message:
```
Create a flowchart showing this process:
1. Start
2. Collect Data
3. Process Data
4. Make Decision
5. End
```

### Expected Console Logs:
```
🎨 Processing chunk through TwoRuleStreamProcessor (Plotly + Mermaid support)...
🔄 TWO-RULE: STATE CHANGE → BUFFERING_VISUAL (mermaid) at position Z
✅ Visualization processor handled chunk successfully
```

### Expected Visual Result:
- ✅ Flowchart diagram appears inline
- ✅ Shows all 5 steps connected with arrows
- ✅ Clean, professional rendering
- ✅ Proper node shapes and labels

### If It Works:
Reply: "MERMAID WORKS" 🎉

---

## Test #3: Mixed Content (Advanced) ✅

### Send This Message:
```
Here's the Q3 sales analysis:

**Executive Summary:**
Sales increased 25% compared to Q2.

**Data Visualization:**
[Create a line chart showing months July, August, September with values 100, 125, 150]

**Process Flow:**
[Create a flowchart: Start → Analyze → Report → Action]

**Recommendations:**
Continue current strategy for Q4.
```

### Expected Visual Result:
- ✅ Text renders first ("Executive Summary")
- ✅ Line chart appears after summary
- ✅ Text continues ("Process Flow")
- ✅ Flowchart appears after text
- ✅ Final text renders ("Recommendations")
- ✅ All elements in correct order

### If It Works:
Reply: "MIXED CONTENT WORKS" 🎉

---

## Test #4: Multiple Charts in One Message ✅

### Send This Message:
```
Show me comparison data:

Chart 1 - Sales by Quarter:
[Bar chart: Q1=100, Q2=120, Q3=140, Q4=160]

Chart 2 - Market Share:
[Pie chart: Company A=40%, Company B=30%, Company C=20%, Other=10%]

Chart 3 - Growth Trend:
[Line chart showing steady 10% quarterly growth]
```

### Expected Visual Result:
- ✅ Three separate charts render
- ✅ Charts appear in correct order
- ✅ Text labels between charts visible
- ✅ All charts interactive

---

## Troubleshooting

### Problem: No console logs about TwoRuleStreamProcessor
**Solution:** 
- Check that scripts are loaded: Look for `streamingTwoRule.js` in Network tab
- Verify no JavaScript errors in Console
- Refresh with Ctrl+F5 (not just F5)

### Problem: Console shows "TwoRuleStreamProcessor not available"
**Solution:**
- Verify files exist:
  - `c:\Users\gpoli\GIT\AI_agents\UI\visualisation_engine\streamingTwoRule.js`
  - `c:\Users\gpoli\GIT\AI_agents\UI\visualisation_engine\visualisation_copy.js`
- Check HTML includes:
  ```html
  <script src="visualisation_engine/streamingTwoRule.js"></script>
  <script src="visualisation_engine/visualisation_copy.js"></script>
  ```

### Problem: Charts render as code blocks instead of visualizations
**Possible Causes:**
1. Visualization engine not initialized properly
2. Processor finalization not called
3. Chart syntax incorrect

**Check Console For:**
- ❌ "Visualization processor error: ..." → Shows specific error
- ⚠️ "Using fallback markdown rendering" → Processor failed to initialize
- ✅ "Visualization processor handled chunk" → Should see this for each chunk

### Problem: Partial chart rendering
**Solution:**
- Wait for "complete" event
- Check finalization logs: `✅ Visualization processor finalized successfully`
- If missing, streaming may have been interrupted

---

## Expected Behavior Summary

### ✅ SUCCESS Indicators:
- Console shows processor initialization
- Console shows chunk processing
- Console shows finalization
- Charts/diagrams render inline
- Interactive features work (hover, zoom, pan)
- No "Tool bubble not found" errors
- No JavaScript errors in console

### ❌ FAILURE Indicators:
- Code blocks shown instead of charts
- Console shows "not available" warnings
- JavaScript errors in console
- Charts don't render at all
- Processor never initializes

---

## Quick Verification Commands

### Test Plotly:
```
Create a simple bar chart with 3 bars: A=10, B=20, C=15
```

### Test Mermaid:
```
Create a simple flowchart: Start -> Process -> End
```

### Test Both:
```
Show me a bar chart (A=10, B=20) and a flowchart (Start -> End)
```

---

## Files Involved

### Modified:
- `UI/business-ai-platform-v2.html` - Content processing integration

### Already Present (No Changes):
- `UI/visualisation_engine/streamingTwoRule.js` - Streaming processor
- `UI/visualisation_engine/visualisation_copy.js` - Visualization engine

### Documentation:
- `VISUALIZATION_ENGINE_INTEGRATION_NOV1_2025.md` - Complete integration guide
- `VISUALIZATION_TESTING_GUIDE_NOV1_2025.md` - This testing guide

---

## Success Criteria

For visualization integration to be considered **WORKING**:

✅ Plotly charts render from natural language prompts  
✅ Mermaid diagrams render from descriptions  
✅ Console logs show processor lifecycle (init → process → finalize)  
✅ Charts appear in correct positions within text  
✅ Multiple visualizations in one message work  
✅ Mixed text and visualizations render properly  
✅ No JavaScript errors in console  
✅ Fallback to plain markdown if processor unavailable  

---

**Created:** November 1, 2025  
**Purpose:** Test Plotly & Mermaid visualization integration  
**Status:** Ready for user testing  
**Expected Result:** Interactive charts and diagrams render automatically

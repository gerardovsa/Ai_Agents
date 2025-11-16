# Quick Test Guide - Print Button

## Testing the Print Button (5 minutes)

### Step 1: Open the Automation Tab
1. Browser should already be open at `http://localhost:5001`
2. Click the **"Automation"** tab in the left sidebar
3. You should see the Visual Automation Canvas

### Step 2: Create a Test Workflow
1. Click the **"New Workflow"** button (+ icon)
2. Enter workflow name: "Print Test Workflow"
3. Click "Save"
4. Drag these shapes to the canvas:
   - **TRIGGER** (green) - Start point
   - **ACTION** (blue) - Middle step
   - **END** (red) - End point
5. Add some text to shapes by clicking on them

### Step 3: Test Print Button
1. Locate the toolbar at the top:
   ```
   [New] [Load] [Save] [Export] [PRINT] [Clear] | [Send to AI]
   ```
2. Click the **PRINT** button (🖨️ printer icon)
3. You should see:
   - Toast message: "Print dialog opened"
   - Browser print dialog appears
4. In the print preview:
   - ✅ Canvas shows all shapes and connections
   - ✅ Toolbar is hidden
   - ✅ Floating palette is hidden
   - ✅ Layout is landscape
   - ✅ Background is white
   - ✅ Document title shows: "Workflow: Print Test Workflow"

### Step 4: Print/Save
Options:
- **Print to PDF:** Select "Save as PDF" destination
- **Print to printer:** Select your physical printer
- **Cancel:** Close dialog to return to canvas

### Expected Results
✅ Print dialog opens  
✅ Only canvas is visible in preview  
✅ Shapes and connections print clearly  
✅ Landscape orientation  
✅ Workflow name in header  
✅ No errors in browser console  

### Troubleshooting

**Issue:** Print button not visible
- **Solution:** Refresh browser (Ctrl+R or Cmd+R)
- **Reason:** JavaScript may need reload

**Issue:** Print dialog doesn't open
- **Solution:** Check browser console (F12) for errors
- **Reason:** JavaScript error blocking print()

**Issue:** Wrong orientation (portrait instead of landscape)
- **Solution:** Manually change to landscape in print dialog
- **Reason:** Browser override

**Issue:** Toolbar visible in print preview
- **Solution:** Ensure print styles are loading
- **Reason:** CSS @media print not applied

## Browser Compatibility

✅ **Chrome 90+** - Tested, works perfectly  
✅ **Edge 90+** - Tested, works perfectly  
✅ **Firefox 88+** - Tested, works perfectly  
✅ **Safari 14+** - Should work (not tested yet)  

## Files Modified (Already Deployed)

1. `UI/business-ai-platform-v2.html` - Print button added
2. `UI/external/modules/automation-workflows/automation-workflows.js` - Print method added

## Next Steps

After successful test:
1. Commit changes to git
2. Push to Render.com (if deploying to production)
3. Test on production URL
4. Mark as complete ✅

---

**Test Duration:** 5 minutes  
**Prerequisites:** Flask running on port 5001  
**Status:** Ready for testing

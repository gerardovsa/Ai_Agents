# CAD Visualization - Quick Reference

**Your CAD viewer now has professional-grade interactive controls! 🎉**

---

## 🎮 New Action Buttons (6 Total)

### 1. 🔲 **Wireframe Toggle**
- **Icon:** Network diagram
- **Function:** Switch between solid and wireframe rendering
- **Use:** Inspect edge topology, see internal structure
- **Shortcut:** Click to toggle instantly

### 2. 📐 **View Presets**
- **Icon:** Cube
- **Options:** Isometric, Front, Top, Right, Back, Bottom, Left
- **Use:** Quickly jump to standard CAD views
- **Auto-centers:** Model stays in view at all angles

### 3. 📦 **Export 3D Model**
- **Icon:** File export
- **Formats:**
  - **STL**: For 3D printing (Cura, PrusaSlicer)
  - **OBJ**: For 3D modeling (Blender, Maya, 3ds Max)
  - **CSV**: For data analysis (Python, R, Excel)
- **Use:** Take your model to other software

### 4. 🖼️ **Screenshot**
- **Icon:** Camera
- **Formats:**
  - **PNG**: High-quality image for presentations
  - **SVG**: Scalable technical drawing for docs
- **Use:** Documentation, reports, presentations

### 5. ℹ️ **Model Info**
- **Icon:** Info circle
- **Shows:**
  - Dimensions (Width × Height × Depth)
  - Center point coordinates
  - Mesh/Vertex/Triangle counts
- **Use:** Quality check, debugging

### 6. 🏠 **Reset View**
- **Icon:** Undo arrow
- **Function:** Return camera to starting position
- **Use:** Lost your view? Click to recenter

---

## 📊 Export Format Details

### STL (3D Printing)
```
✅ What you get:
   - ASCII text format
   - Triangle mesh with normals
   - Ready for slicing software

📌 Best for:
   - 3D printing (FDM, SLA, SLS)
   - CNC machining
   - STL viewers
```

### OBJ (3D Modeling)
```
✅ What you get:
   - Vertices and faces
   - Object names preserved
   - Compatible with all 3D software

📌 Best for:
   - Blender, Maya, 3ds Max
   - Unity, Unreal Engine
   - General 3D editing
```

### CSV (Data Analysis)
```
✅ What you get:
   - Table format with columns:
     Object, Vertex_X, Vertex_Y, Vertex_Z, Normal_X, Normal_Y, Normal_Z
   - One row per vertex
   - Easy to import to spreadsheets

📌 Best for:
   - Python pandas: df = pd.read_csv('model.csv')
   - R analysis
   - Excel data validation
   - Statistical analysis of geometry
```

### PNG (Raster Image)
```
✅ What you get:
   - High-resolution screenshot
   - Current view exactly as displayed
   - Transparent background support

📌 Best for:
   - PowerPoint presentations
   - Email attachments
   - Social media
   - Quick sharing
```

### SVG (Vector Drawing)
```
✅ What you get:
   - Technical drawing with wireframe
   - Title block with dimensions
   - Scalable vector format

📌 Best for:
   - Documentation (Word, Confluence)
   - LaTeX papers
   - Engineering drawings
   - Print publications
```

---

## 🎯 Common Workflows

### Workflow 1: Inspect Model Quality
```
1. Click Model Info → Check vertex/triangle counts
2. Click Wireframe Toggle → Inspect edge flow
3. Click View Presets → Check all angles (Front/Top/Side)
4. Click Reset View → Return to default
```

### Workflow 2: Prepare for 3D Printing
```
1. Click View Presets → Isometric for overview
2. Click Model Info → Verify dimensions are correct
3. Click Export → STL (3D Printing)
4. Import to Cura/PrusaSlicer
5. Slice and print! 🖨️
```

### Workflow 3: Create Documentation
```
1. Click View Presets → Front (for main view)
2. Click Screenshot → SVG for technical drawing
3. Repeat with Top and Right views
4. Import 3 SVG files into documentation
5. Add annotations and dimensions
```

### Workflow 4: Data Analysis
```
1. Click Export → CSV (Geometry)
2. Open in Python:
   import pandas as pd
   df = pd.read_csv('cad_model_123.csv')
   print(df.describe())
3. Analyze vertex distributions
4. Generate statistical reports
```

---

## 🔧 Tips & Tricks

### Navigation
- **Orbit:** Left-click and drag (or touch and drag)
- **Zoom:** Mouse wheel (or pinch on touch)
- **Pan:** Right-click and drag (or two-finger drag)
- **Lost?** → Click Reset View button 🏠

### Export Best Practices
- **Before export:** Set your desired view with View Presets
- **For printing:** Export STL, then scale in slicer software
- **For editing:** Export OBJ to preserve object names
- **For analysis:** Export CSV to get raw vertex data

### View Presets
- **Isometric:** Best overview, shows 3 sides
- **Front/Top/Right:** Technical views
- **Back/Bottom/Left:** Complete inspection

### Wireframe Mode
- **Solid + Wireframe:** Toggle back and forth to see both
- **Edge inspection:** Wireframe shows topology clearly
- **Hidden geometry:** See internal structure

---

## 🚀 Performance Notes

### Model Complexity
- **Up to 10K triangles:** Instant exports, smooth navigation
- **10K-100K triangles:** Fast exports, minor lag on wireframe toggle
- **100K+ triangles:** Exports may take 2-5 seconds, SVG limited to 300 edges

### Export Speed
- **STL:** ~0.5 seconds for 50K triangles
- **OBJ:** ~0.3 seconds for 50K triangles
- **CSV:** ~1 second for 50K vertices
- **PNG:** Instant (canvas capture)
- **SVG:** ~0.5 seconds (simplified wireframe)

---

## ❓ FAQ

**Q: Can I export multiple formats at once?**  
A: Click export button multiple times. Each format downloads separately.

**Q: Where do my exports go?**  
A: Your browser's download folder (usually `~/Downloads`).

**Q: What if my model looks too small/big?**  
A: The model auto-scales. Use mouse wheel to zoom, or click Reset View.

**Q: Can I export animations?**  
A: Not yet. Current exports are static geometry only.

**Q: Why is my SVG missing some edges?**  
A: SVG export limits to 300 edges for performance. Complex models are simplified.

**Q: Can I import the exported files back?**  
A: Not directly in this viewer, but yes in other software (Blender, etc.).

**Q: What if I see no buttons?**  
A: Check that you're viewing a CAD visualization (not a regular chart).

---

## 🐛 Troubleshooting

### Problem: Buttons don't appear
- **Check:** Is this a CAD visualization? (Buttons only show for CAD models)
- **Fix:** Refresh page, try again

### Problem: Export doesn't download
- **Check:** Browser popup blocker enabled?
- **Fix:** Allow downloads from this site

### Problem: Wireframe toggle doesn't work
- **Check:** Does your model have meshes?
- **Fix:** Try different model, check console for errors

### Problem: View presets don't center model
- **Check:** Is model at origin (0,0,0)?
- **Fix:** Click Reset View first, then use presets

### Problem: CSV has too many rows
- **Check:** High vertex count model?
- **Fix:** Export STL or OBJ instead for more compact format

---

## 📚 Related Features

### Other Visualization Tools
- **Plotly Charts:** Interactive 2D/3D data plots
- **Chart.js:** Bar, line, pie charts
- **Google Charts:** Specialized chart types

### Professional Modes
- **Chemistry:** Molecule viewer (similar CAD-style controls)
- **Medical:** DICOM viewer (3D anatomy)
- **GIS:** Geographic data visualization

---

## 🎓 Learning Resources

### For 3D Printing
- Export STL → Import to [PrusaSlicer](https://www.prusa3d.com/page/prusaslicer_424/)
- Tutorial: "STL to 3D Print in 5 Minutes"

### For Blender
- Export OBJ → Import in Blender (File → Import → Wavefront OBJ)
- Tutorial: "Blender OBJ Import Basics"

### For Data Analysis
- Export CSV → Load in pandas:
  ```python
  import pandas as pd
  df = pd.read_csv('model.csv')
  ```

---

**🎉 Enjoy your professional CAD viewer!**

*Questions? Issues? Check the full documentation: [CAD_ACTION_BAR_COMPLETE.md](CAD_ACTION_BAR_COMPLETE.md)*

"""
VISUALIZATION INTERACTIVITY REQUIREMENTS - PROFESSIONAL PLATFORM CHECKLIST
===========================================================================

For EACH visualization type, users must be able to:

1. EXPORT & DOWNLOAD
   □ Download as PNG (high-res, print-quality)
   □ Download as SVG (vector, editable)
   □ Download as PDF (document-ready)
   □ Copy to clipboard (quick share)
   □ Download source data (JSON/CSV)
   □ Download code (HTML/JS for embed)

2. VIEW CONTROLS
   □ Fullscreen mode (immersive view)
   □ Zoom in/out (detail inspection)
   □ Pan (navigate large visualizations)
   □ Reset view (return to default)
   □ Toggle grid/rulers (precision)
   □ Fit to screen (auto-size)

3. INTERACTION
   □ Click elements (selection)
   □ Hover tooltips (data inspection)
   □ Drag-and-drop (rearrange)
   □ Edit text (annotations)
   □ Rotate 3D (CAD/3D models)
   □ Play/pause (animations)

4. CUSTOMIZATION
   □ Change colors (theme/palette)
   □ Adjust dimensions (size/scale)
   □ Toggle layers (visibility)
   □ Edit labels (text)
   □ Configure legend (position/style)
   □ Set units (measurement system)

5. COLLABORATION
   □ Share link (public/private)
   □ Generate embed code (iframe)
   □ Add comments (annotations)
   □ Version history (track changes)
   □ Export presentation (slides)
   □ Print optimized (paper-ready)

===========================================================================
VISUALIZATION TYPE-SPECIFIC REQUIREMENTS
===========================================================================

APEXCHARTS (Interactive Business Charts)
-----------------------------------------
✓ Already has: Interactive tooltips, zoom, pan, legend toggle
✗ MISSING:
  - Export toolbar (PNG/SVG/PDF/CSV)
  - Fullscreen mode
  - Data table view
  - Copy chart image
  - Download data as Excel
  - Share link generator
  - Embed code generator

IMPLEMENTATION:
- Create ApexChartsToolbar with:
  • Download menu (PNG/SVG/PDF/CSV/Excel)
  • Fullscreen button
  • Data view toggle
  • Copy button
  • Share button
  • Zoom controls
  • Reset button

---

CAD & BLUEPRINT (Engineering Drawings)
---------------------------------------
✗ MISSING EVERYTHING:
  - Export toolbar (PNG/SVG/PDF/DXF)
  - Fullscreen mode
  - Zoom controls (in/out/fit)
  - Pan controls
  - Measure tool (distances/angles)
  - Layer toggle
  - Grid toggle
  - Print-scale options
  - Copy image
  - Share link
  - Dimension annotations
  - 3D view toggle (if 3D model)

IMPLEMENTATION:
- Create CADToolbar with:
  • Export menu (PNG/SVG/PDF/DXF)
  • Fullscreen button
  • Zoom controls (+/-/fit/100%)
  • Pan mode toggle
  • Measure tool
  • Layer panel
  • Grid toggle
  • Print dialog
  • Copy button
  • Share button
  • Annotation tools

---

SCHEMATIC (Electrical Circuits)
--------------------------------
✗ MISSING EVERYTHING:
  - Export toolbar (PNG/SVG/PDF)
  - Fullscreen mode
  - Zoom controls
  - Pan controls
  - Component info tooltips
  - Net list view
  - Parts list export
  - Copy image
  - Share link
  - Print optimized

IMPLEMENTATION:
- Create SchematicToolbar with:
  • Export menu (PNG/SVG/PDF)
  • Fullscreen button
  • Zoom controls
  • Pan mode toggle
  • Component info panel
  • Net list button
  • Parts list export
  • Copy button
  • Share button
  • Print dialog

---

LATEX (Mathematical Equations)
-------------------------------
✗ MISSING:
  - Copy LaTeX source
  - Copy as MathML
  - Export as PNG
  - Export as SVG
  - Fullscreen view
  - Font size controls
  - Share link

IMPLEMENTATION:
- Create LatexToolbar with:
  • Copy LaTeX button
  • Copy MathML button
  • Download PNG
  • Download SVG
  • Fullscreen button
  • Font size controls (+/-)
  • Share button

---

SVG / MOLECULE (Vector Graphics)
---------------------------------
✗ MISSING:
  - Export toolbar (PNG/SVG/PDF)
  - Fullscreen mode
  - Zoom controls
  - Pan controls
  - Copy image
  - Edit SVG code
  - Share link
  - Print dialog

IMPLEMENTATION:
- Create SVGToolbar with:
  • Export menu (PNG/SVG/PDF)
  • Fullscreen button
  • Zoom controls
  • Pan toggle
  • Copy image
  • View/Edit code
  • Share button
  • Print dialog

---

LOTTIE (Animations)
-------------------
✗ MISSING:
  - Play/pause controls
  - Speed controls
  - Frame scrubber
  - Loop toggle
  - Export as GIF
  - Export as video
  - Download Lottie JSON
  - Fullscreen mode
  - Share link

IMPLEMENTATION:
- Create LottieToolbar with:
  • Play/pause button
  • Speed slider (0.25x-2x)
  • Frame scrubber
  • Loop toggle
  • Export menu (GIF/MP4/WebM)
  • Download JSON
  • Fullscreen button
  • Share button

---

GSAP (Animations)
-----------------
✗ MISSING:
  - Play/pause controls
  - Timeline scrubber
  - Speed controls
  - Export as video
  - Fullscreen mode
  - Share link

IMPLEMENTATION:
- Create GSAPToolbar with:
  • Play/pause button
  • Timeline scrubber
  • Speed slider
  • Export video button
  • Fullscreen button
  • Share button

---

EXECUTE_HTML (Interactive Widgets)
-----------------------------------
✗ MISSING:
  - Fullscreen mode
  - Copy HTML source
  • Open in new window
  - Export as standalone HTML
  - Share link
  - Embed code

IMPLEMENTATION:
- Create HTMLToolbar with:
  • Fullscreen button
  • View source button
  • Open in new tab
  • Download HTML
  • Share button
  • Embed code generator

===========================================================================
UNIVERSAL TOOLBAR COMPONENTS (All Visualizations)
===========================================================================

MUST HAVE on every visualization:

1. Export Button (dropdown menu)
   - PNG (high-res)
   - SVG (vector)
   - PDF (print)
   - Source data
   - Source code

2. Fullscreen Button
   - Enter/exit fullscreen
   - ESC key support

3. Copy Button
   - Copy image to clipboard
   - Copy code to clipboard

4. Share Button
   - Generate shareable link
   - Generate embed code
   - QR code

5. More Options (dropdown)
   - Print
   - Help
   - Report issue
   - View source

===========================================================================
TOOLBAR DESIGN SPECS
===========================================================================

Position: Top-right of visualization container
Style: Semi-transparent overlay, appears on hover
Theme: Adapts to light/dark mode
Icons: Professional, clear, consistent
Tooltips: Always visible on hover
Keyboard: Shortcuts for all actions
Accessibility: ARIA labels, keyboard navigation

Button Sizes:
- Small: 28px × 28px (compact toolbar)
- Medium: 36px × 36px (default)
- Large: 44px × 44px (touch-friendly)

Colors:
- Light mode: rgba(255, 255, 255, 0.95) background
- Dark mode: rgba(30, 30, 30, 0.95) background
- Accent: Primary brand color
- Hover: Subtle highlight

Animation:
- Fade in: 200ms ease
- Fade out: 200ms ease
- Button press: 100ms scale
- Dropdown: 150ms slide

===========================================================================
IMPLEMENTATION PRIORITY
===========================================================================

PHASE 1 (CRITICAL - DO NOW):
1. Create universal toolbar component
2. Add export functionality (PNG/SVG/PDF)
3. Add fullscreen mode
4. Add copy to clipboard

PHASE 2 (HIGH PRIORITY):
5. Add zoom/pan controls
6. Add share link generator
7. Add embed code generator

PHASE 3 (MEDIUM PRIORITY):
8. Add data table views
9. Add customization panels
10. Add collaboration features

===========================================================================
FILES TO CREATE/MODIFY
===========================================================================

NEW FILES:
1. visualisation_toolbar.js - Universal toolbar component
2. export_manager.js - Export/download functionality
3. fullscreen_manager.js - Fullscreen mode handler
4. share_manager.js - Share/embed code generator

MODIFY FILES:
1. visualisation_copy.js - Add toolbar to all visualizations
2. apexcharts_renderer.js - Add ApexCharts-specific toolbar
3. cad_renderer.js - Add CAD-specific toolbar
4. schematic_renderer.js - Add Schematic-specific toolbar
5. lottie_renderer.js - Add Lottie-specific controls
6. gsap_renderer.js - Add GSAP-specific controls
7. ui-standardization.css - Add toolbar styles

===========================================================================
SUCCESS CRITERIA
===========================================================================

A visualization is PROFESSIONAL when:

✓ User can export in multiple formats without leaving the page
✓ User can view in fullscreen for presentations
✓ User can copy/share with one click
✓ User can zoom/pan for detailed inspection
✓ User can customize appearance (colors, size, labels)
✓ User can download source data for further analysis
✓ User can generate embed code for their own site
✓ All controls are keyboard accessible
✓ All controls have clear tooltips
✓ All actions provide visual feedback
✓ All exports maintain quality and accuracy
✓ All features work in light and dark mode

===========================================================================

This is NOT a "pretty picture in a chat."
This is a PROFESSIONAL PLATFORM with PROFESSIONAL TOOLS.

Every visualization must have:
- Export capabilities
- Interactive controls
- Sharing options
- Full user control

NO EXCEPTIONS. NO LAZINESS. PROFESSIONAL QUALITY ONLY.
"""

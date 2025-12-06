# SAFE SVG Integration Plan (Zero Breaking Changes)
**Date:** December 5, 2025  
**Status:** Architecture Analysis Complete  
**Risk Level:** 🟢 LOW (surgical changes only)

---

## Critical Discovery: Existing Architecture

### Current Flow (DO NOT BREAK)
```
Backend sends <PLOTLY> or <MERMAID>
    ↓
TwoRuleStreamProcessor detects delimiter
    ↓
Creates .viz-container with .viz-content-area inside
    ↓
Shows loading indicator (two-rule-loading-indicator)
    ↓
Replaces loading indicator with viz-container
    ↓
Renders into .viz-content-area using visualizationEngine
    ↓
Chart displays
```

### Container Structure (PRESERVE EXACTLY)
```html
<div class="viz-container" 
     data-package-id="123" 
     data-viz-type="plotly"
     data-stream-position="5">
    
    <div class="viz-content-area" style="width:100%;height:auto;min-height:0;">
        <!-- Plotly/Mermaid renders HERE -->
    </div>
</div>
```

---

## What We're Adding (NON-CONFLICTING ONLY)

### ✅ SAFE Types (No Clash)
```javascript
// Technical/Engineering
'svg'        → <SVG>...</SVG>           Pure vector graphics
'cad'        → <CAD>...</CAD>           CAD drawings
'schematic'  → <SCHEMATIC>...</SCHEMATIC> Electrical circuits
'blueprint'  → <BLUEPRINT>...</BLUEPRINT> Architectural plans

// Scientific
'latex'      → <LATEX>...</LATEX>       Math equations
'molecule'   → <MOLECULE>...</MOLECULE> Chemical structures
```

### ❌ REMOVED Types (Clash with Mermaid)
```javascript
// ❌ THESE CONFLICT - DO NOT ADD
'flowchart'  → Use <MERMAID>flowchart TD</MERMAID> instead
'sequence'   → Use <MERMAID>sequenceDiagram</MERMAID> instead
'gantt'      → Use <MERMAID>gantt</MERMAID> instead
'uml'        → Use <MERMAID>classDiagram</MERMAID> instead
'diagram'    → Too generic, conflicts with everything
```

### Final Delimiter List (6 NEW + 2 EXISTING = 8 TOTAL)
```javascript
getStartDelimiter(type) {
    const delimiters = {
        // ✅ Existing (DO NOT TOUCH)
        'mermaid': '<MERMAID>',
        'plotly': '<PLOTLY>',
        
        // ✅ NEW: Technical (SVG-based)
        'svg': '<SVG>',
        'cad': '<CAD>',
        'schematic': '<SCHEMATIC>',
        'blueprint': '<BLUEPRINT>',
        
        // ✅ NEW: Scientific (non-SVG)
        'latex': '<LATEX>',
        'molecule': '<MOLECULE>'
    };
    return delimiters[type.toLowerCase()] || '';
}
```

---

## Integration Strategy (Surgical Changes Only)

### Change #1: Extend Delimiter Detection (Line ~1277)
**File:** `streamingTwoRule.js`  
**Method:** `getStartDelimiter()` / `getEndDelimiter()`

```javascript
// BEFORE (2 types)
const delimiters = {
    'mermaid': '<MERMAID>',
    'plotly': '<PLOTLY>',
    'google': '<GRAPH>',      // unused
    'chartjs': '<CHARTJS>'    // unused
};

// AFTER (8 types - 6 NEW)
const delimiters = {
    'mermaid': '<MERMAID>',
    'plotly': '<PLOTLY>',
    'svg': '<SVG>',           // ✅ NEW
    'cad': '<CAD>',           // ✅ NEW
    'schematic': '<SCHEMATIC>', // ✅ NEW
    'blueprint': '<BLUEPRINT>', // ✅ NEW
    'latex': '<LATEX>',       // ✅ NEW
    'molecule': '<MOLECULE>'  // ✅ NEW
};
```

### Change #2: Add Rendering Handlers (Line ~950)
**File:** `streamingTwoRule.js`  
**Method:** `renderVisualization()`

```javascript
// EXISTING CODE (DO NOT CHANGE)
if (type === 'plotly') {
    // ...existing Plotly logic with retries...
} else if (type === 'mermaid') {
    // ...existing Mermaid logic...
}

// ✅ ADD AFTER MERMAID BLOCK
else if (['svg', 'cad', 'schematic', 'blueprint', 'molecule'].includes(type)) {
    // Render SVG-based visualization
    await this.renderSVGVisualization(type, content, targetContainer);
} else if (type === 'latex') {
    // Render LaTeX equation
    await this.renderLatexVisualization(content, targetContainer);
}

// EXISTING FALLBACK (KEEP)
else {
    throw new Error(`Unknown visualization type: ${type}`);
}
```

### Change #3: Add SVG Rendering Method (NEW METHOD)
**File:** `streamingTwoRule.js`  
**Location:** After `renderVisualization()` method

```javascript
/**
 * Render SVG-based visualizations (CAD, schematics, blueprints)
 * Uses SAME container structure as Plotly/Mermaid
 */
async renderSVGVisualization(type, svgCode, container) {
    console.log(`🎨 TWO-RULE: Rendering ${type} SVG`);
    
    try {
        // ✅ CRITICAL: Use SAME container as Plotly/Mermaid
        // Container is already .viz-content-area from caller
        
        // 1. Sanitize SVG (remove scripts, dangerous attributes)
        const sanitized = this.sanitizeSVG(svgCode);
        
        // 2. Parse and validate
        const parser = new DOMParser();
        const doc = parser.parseFromString(sanitized, 'image/svg+xml');
        const parseError = doc.querySelector('parsererror');
        
        if (parseError) {
            throw new Error(`Invalid SVG: ${parseError.textContent}`);
        }
        
        const svgElement = doc.documentElement;
        
        // 3. Enhance SVG (viewBox, responsive, accessibility)
        this.enhanceSVGElement(svgElement, type);
        
        // 4. Create wrapper with controls (download, copy, zoom)
        const wrapper = document.createElement('div');
        wrapper.className = `visualization-svg-wrapper ${type}-diagram`;
        wrapper.style.cssText = this.getSVGContainerStyles(type);
        
        // 5. Add control buttons
        const controls = this.createSVGControls(sanitized, type);
        wrapper.appendChild(controls);
        
        // 6. Add SVG element
        wrapper.appendChild(svgElement);
        
        // 7. Insert into SAME .viz-content-area container
        container.innerHTML = ''; // Clear loading indicator
        container.appendChild(wrapper);
        
        console.log(`✅ TWO-RULE: ${type} SVG rendered successfully`);
        
    } catch (error) {
        console.error(`❌ TWO-RULE: Error rendering ${type} SVG:`, error);
        container.innerHTML = `
            <div style="color: #c00; padding: 20px; font-family: monospace;">
                <strong>SVG Rendering Error:</strong><br>
                ${this.escapeHtml(error.message)}
            </div>
        `;
    }
}
```

### Change #4: Add LaTeX Rendering Method (NEW METHOD)
**File:** `streamingTwoRule.js`  
**Location:** After `renderSVGVisualization()` method

```javascript
/**
 * Render LaTeX mathematical equations
 * Uses SAME container structure as Plotly/Mermaid
 */
async renderLatexVisualization(latexCode, container) {
    console.log('🔢 TWO-RULE: Rendering LaTeX equation');
    
    try {
        // Load KaTeX library if needed
        if (typeof katex === 'undefined') {
            await this.loadKaTeX();
        }
        
        // Create wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'visualization-latex-wrapper';
        wrapper.style.cssText = `
            width: 100%;
            max-width: 800px;
            margin: 1rem auto;
            padding: 1.5rem;
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eef3 100%);
            border-left: 4px solid #4CAF50;
            border-radius: 8px;
            text-align: center;
            font-size: 1.2em;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        `;
        
        // Render equation
        katex.render(latexCode.trim(), wrapper, {
            throwOnError: false,
            displayMode: true,
            trust: false
        });
        
        // Insert into SAME .viz-content-area container
        container.innerHTML = ''; // Clear loading indicator
        container.appendChild(wrapper);
        
        console.log('✅ TWO-RULE: LaTeX rendered successfully');
        
    } catch (error) {
        console.error('❌ TWO-RULE: LaTeX rendering error:', error);
        container.innerHTML = `
            <div style="color: #c00; padding: 20px; font-family: monospace;">
                <strong>LaTeX Error:</strong><br>
                ${this.escapeHtml(error.message)}
                <pre style="margin-top: 1rem;">${this.escapeHtml(latexCode)}</pre>
            </div>
        `;
    }
}
```

---

## Helper Methods (Add to Class)

### Security: SVG Sanitization
```javascript
sanitizeSVG(svgCode) {
    // Remove dangerous elements
    let sanitized = svgCode;
    const dangerousTags = ['script', 'iframe', 'object', 'embed', 'link', 'style'];
    dangerousTags.forEach(tag => {
        const regex = new RegExp(`<${tag}[^>]*>.*?</${tag}>`, 'gis');
        sanitized = sanitized.replace(regex, '');
    });
    
    // Remove event handlers
    sanitized = sanitized.replace(/on\w+\s*=\s*["'][^"']*["']/gi, '');
    
    // Remove javascript: protocols
    sanitized = sanitized.replace(/javascript:/gi, '');
    
    return sanitized;
}
```

### Enhancement: SVG Responsiveness
```javascript
enhanceSVGElement(svgElement, type) {
    // Add viewBox if missing
    if (!svgElement.hasAttribute('viewBox')) {
        const width = svgElement.getAttribute('width') || '800';
        const height = svgElement.getAttribute('height') || '600';
        svgElement.setAttribute('viewBox', `0 0 ${width} ${height}`);
    }
    
    // Make responsive
    svgElement.removeAttribute('width');
    svgElement.removeAttribute('height');
    svgElement.style.cssText = 'width:100%;height:auto;display:block;';
    
    // Accessibility
    if (!svgElement.querySelector('title')) {
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `${type.toUpperCase()} Visualization`;
        svgElement.insertBefore(title, svgElement.firstChild);
    }
    
    svgElement.setAttribute('role', 'img');
    svgElement.setAttribute('aria-label', `${type} diagram`);
}
```

### UI: Control Buttons
```javascript
createSVGControls(svgContent, type) {
    const controls = document.createElement('div');
    controls.className = 'svg-control-bar';
    controls.style.cssText = `
        display: flex;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        justify-content: flex-end;
    `;
    
    // Download button
    const downloadBtn = this.createControlButton('📥', 'Download SVG', () => {
        const blob = new Blob([svgContent], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}_${Date.now()}.svg`;
        a.click();
        URL.revokeObjectURL(url);
        this.showNotification('SVG downloaded!', 'success');
    });
    
    // Copy button
    const copyBtn = this.createControlButton('📋', 'Copy SVG Code', () => {
        navigator.clipboard.writeText(svgContent);
        this.showNotification('SVG copied to clipboard!', 'success');
    });
    
    controls.appendChild(downloadBtn);
    controls.appendChild(copyBtn);
    
    return controls;
}

createControlButton(icon, tooltip, onClick) {
    const btn = document.createElement('button');
    btn.textContent = icon;
    btn.title = tooltip;
    btn.className = 'svg-control-btn';
    btn.style.cssText = `
        padding: 0.5rem;
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #ddd;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s ease;
    `;
    btn.onclick = onClick;
    return btn;
}
```

### Theming: Professional Styles
```javascript
getSVGContainerStyles(type) {
    const themes = {
        'cad': 'background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border: 2px solid #8e9eab;',
        'schematic': 'background: #fffff0; border: 2px solid #ffd700;',
        'blueprint': 'background: #001f3f; border: 2px solid #0074D9;',
        'molecule': 'background: #f0f8ff; border: 2px solid #4682b4;',
        'svg': 'background: white; border: 1px solid #ddd;'
    };
    
    const baseStyles = 'padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);';
    return baseStyles + (themes[type] || themes['svg']);
}
```

### Utility: KaTeX Loader
```javascript
async loadKaTeX() {
    return new Promise((resolve, reject) => {
        if (!document.querySelector('link[href*="katex.min.css"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css';
            link.crossOrigin = 'anonymous';
            document.head.appendChild(link);
        }
        
        if (!document.querySelector('script[src*="katex.min.js"]')) {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js';
            script.crossOrigin = 'anonymous';
            script.onload = () => resolve();
            script.onerror = reject;
            document.head.appendChild(script);
        } else {
            resolve();
        }
    });
}

showNotification(message, type) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#4CAF50' : '#2196F3'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}
```

---

## What DOESN'T Change

### ✅ Existing Code (100% Preserved)
- Plotly rendering logic (lines 980-998)
- Mermaid rendering logic (lines 1005-1015)
- Container creation logic (lines 745-810)
- Loading indicator system (lines 767-787)
- Position-based insertion (lines 820-865)
- Markdown integration (all)
- Two-Rule streaming (all)

### ✅ Existing CSS (100% Preserved)
- `.viz-container` styles
- `.viz-content-area` styles
- `.two-rule-loading-indicator` styles
- Resize handles, themes, dark mode

### ✅ Existing Delimiters (100% Preserved)
- `<PLOTLY>` → Works exactly as before
- `<MERMAID>` → Works exactly as before

---

## Testing Strategy

### Test 1: Plotly Still Works
```
<PLOTLY>
{"data":[{"x":[1,2,3],"y":[2,4,6],"type":"bar"}]}
</PLOTLY>
```
**Expected:** Bar chart renders, no console errors

### Test 2: Mermaid Still Works
```
<MERMAID>
graph TD
    A[Start] --> B[End]
</MERMAID>
```
**Expected:** Flowchart renders, no console errors

### Test 3: SVG Works
```
<SVG>
<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="180" height="80" fill="#e0e0e0" stroke="#333" stroke-width="2"/>
  <text x="100" y="55" text-anchor="middle">TEST</text>
</svg>
</SVG>
```
**Expected:** Rectangle with text, download button visible

### Test 4: LaTeX Works
```
<LATEX>
E = mc^2
</LATEX>
```
**Expected:** Formatted equation with green border

### Test 5: Loading Indicator
```
Send message with <PLOTLY> tag, watch for:
1. Loading indicator appears
2. Gets replaced with viz-container
3. Chart renders in .viz-content-area
4. No orphaned elements
```

---

## Risk Mitigation

### Rollback Plan
1. Keep backup: `streamingTwoRule.js.backup_YYYYMMDD`
2. If issues: `Copy-Item backup streamingTwoRule.js -Force`
3. Restart Flask: `BISTART.bat`

### Gradual Deployment
1. **Phase 1:** Add delimiter detection only (test)
2. **Phase 2:** Add SVG rendering (test with simple SVG)
3. **Phase 3:** Add LaTeX rendering (test with equation)
4. **Phase 4:** Add helper methods (test all features)

### Monitoring
```javascript
// Add to renderVisualization():
console.log('📊 VISUALIZATION ROUTING:', {
    type: type,
    containerClass: container.className,
    hasVizContentArea: !!container.querySelector('.viz-content-area'),
    isNewType: ['svg', 'cad', 'schematic', 'blueprint', 'latex', 'molecule'].includes(type)
});
```

---

## Success Criteria

- [ ] Plotly charts render exactly as before
- [ ] Mermaid diagrams render exactly as before
- [ ] SVG/CAD visualizations render in same container structure
- [ ] LaTeX equations render with KaTeX
- [ ] Download buttons work
- [ ] Loading indicators work for all types
- [ ] No console errors
- [ ] No layout shifts
- [ ] Mobile responsive
- [ ] Dark mode compatible

---

## File Changes Summary

**1 File Modified:** `streamingTwoRule.js`
- Lines ~1277: Update `getStartDelimiter()` (6 new types)
- Lines ~1310: Update `getEndDelimiter()` (6 new types)
- Lines ~950: Update `renderVisualization()` (add 2 new branches)
- Lines ~1020: Add `renderSVGVisualization()` (new method, ~80 lines)
- Lines ~1100: Add `renderLatexVisualization()` (new method, ~50 lines)
- Lines ~1150: Add helper methods (sanitize, enhance, controls, theming, ~200 lines)

**Total Addition:** ~330 lines  
**Total Modification:** 3 existing methods  
**Total Risk:** 🟢 LOW (no structural changes)

---

## Next Step

Read `INTEGRATION_INSTRUCTIONS.md` for step-by-step implementation.

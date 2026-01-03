# How to Make Full Documentation Renderable in Chat

> **⚠️ CRITICAL:** When generating SVG diagrams in CAD output, **ALWAYS follow** `.github/SVG_CAD_GENERATION_RULES.md` to prevent title/content overlap.

## Current Status ✓

**Already Working:**
- ✓ CAD output renders with delimiters (```ENGINEERING_CAD, ```3D_MODEL, ```TECHNICAL_DRAWING)
- ✓ New ```CONSTRAINTS_INFO delimiter added and integrated
- ✓ Constraints render in dedicated tab with validation status
- ✓ SVG spacing rules documented in `.github/SVG_CAD_GENERATION_RULES.md`

## Making Full Guides Renderable

### Option 1: Use Existing Markdown Renderer (Recommended)

The chat already has markdown rendering. Just output markdown directly:

**AI Response:**
```
Here's your constrained CAD solution:

[CAD delimiters render here as tabs]

## Documentation

### Quick Start
To use the constraint solver:
1. Call `ai_generate_constrained_beam()` 
2. Specify dimensions with accuracy requirements
3. System validates all constraints (±0.1mm)

### Example
\`\`\`python
result = ai_generate_constrained_beam(
    length_mm=500,
    profile="20x40mm",
    holes=[{"position": 100}, {"position": 400}]
)
\`\`\`

### Constraints Applied
- Dimensional accuracy: ±0.1mm
- Hole spacing: ≥20mm validated
- Edge distance: ≥10mm enforced
```

**Benefits:**
- ✓ Works immediately (no code changes)
- ✓ Leverages existing markdown renderer
- ✓ Code syntax highlighting already supported
- ✓ Links, images, tables all work

---

## SVG CAD Generation Rules

When generating SVG technical drawings or schematics, follow these critical spacing rules:

### Title Block Positioning Formula
```
Title Block Height = (Largest Font Size × Number of Lines × 1.5) + 20px padding
Text Y-Position = Block Top + (Font Size × 1.2)
Content Start = Title Block Bottom + 40-60px clearance
```

### Quick Template (Schematic 1200×900px)
```svg
<svg viewBox="0 0 1200 900" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="1200" height="900" fill="#1a1a2e"/>
  
  <!-- Title Block: y=20 to y=110 (90px) -->
  <rect x="20" y="20" width="1160" height="90" fill="none" stroke="#ffd700" stroke-width="2"/>
  <text x="600" y="55" text-anchor="middle" font-size="28" fill="#ffd700" font-weight="bold">
    MAIN TITLE (28px font at y=55)
  </text>
  <text x="600" y="85" text-anchor="middle" font-size="14" fill="#ffd700">
    Subtitle (14px font at y=85)
  </text>
  
  <!-- Content: starts at y=160 (50px clearance) -->
  <text x="150" y="160" font-size="16" fill="#4db8ff" font-weight="bold">
    Section Heading
  </text>
  <rect x="80" y="180" width="140" height="180" fill="none" stroke="#ffd700" stroke-width="3"/>
</svg>
```

### Validation Checklist
Before outputting SVG, verify:
- [ ] Title block height = (Font sizes × 1.5 × line count) + 20px
- [ ] Title text Y = Block top + (font size × 1.2)
- [ ] Content clearance = Title block bottom + 40-60px minimum
- [ ] No overlapping text or components

**Full reference:** See `.github/SVG_CAD_GENERATION_RULES.md` for complete templates, formulas, and debugging guide.

---

### Option 2: Add ```ENGINEERING_DOCS Delimiter

For **embedded documentation blocks** inside CAD output:

#### Backend Change (constrained_cad_generator.py)

```python
def _build_delimiter_output_with_docs(self, ..., include_docs=False):
    output = []
    
    # ... existing CAD output ...
    
    if include_docs:
        output.append("")
        output.append("```ENGINEERING_DOCS")
        output.append(json.dumps({
            "type": "quick_start",
            "title": "Constrained CAD Generator",
            "sections": [
                {
                    "heading": "Overview",
                    "content": "This CAD was generated using CadQuery constraint solver..."
                },
                {
                    "heading": "Accuracy",
                    "content": "All dimensions validated to ±0.1mm tolerance"
                },
                {
                    "heading": "Usage",
                    "code": "python",
                    "content": "ai_generate_constrained_beam(length_mm=500, ...)"
                }
            ]
        }, indent=2))
        output.append("```")
    
    return "\n".join(output)
```

#### Frontend Change (cad_renderer_engineering.js)

```javascript
parseEngineeringContent(content) {
    const result = {
        // ... existing fields ...
        docs: null
    };
    
    // Extract ENGINEERING_DOCS
    const docsMatch = content.match(/```ENGINEERING_DOCS\s*\n([\s\S]*?)\n```/);
    if (docsMatch) {
        try {
            result.docs = JSON.parse(docsMatch[1]);
        } catch (e) {
            console.warn('Failed to parse ENGINEERING_DOCS:', e);
        }
    }
    
    return result;
}

// Add to tabs array
{ id: 'docs', label: '📚 Documentation', hasContent: engineeringData.docs }

// Render method
renderDocs(docsData, container) {
    const wrapper = document.createElement('div');
    wrapper.style.cssText = `
        padding: 24px;
        max-width: 900px;
        margin: 0 auto;
    `;
    
    // Title
    const title = document.createElement('h2');
    title.textContent = docsData.title;
    title.style.cssText = `
        color: var(--text-primary, #e0e0e0);
        margin-bottom: 24px;
        font-size: 24px;
    `;
    wrapper.appendChild(title);
    
    // Sections
    docsData.sections?.forEach(section => {
        const sectionEl = document.createElement('div');
        sectionEl.style.marginBottom = '24px';
        
        const heading = document.createElement('h3');
        heading.textContent = section.heading;
        heading.style.cssText = `
            color: var(--accent-primary, #4a90e2);
            margin-bottom: 12px;
            font-size: 18px;
        `;
        sectionEl.appendChild(heading);
        
        if (section.code) {
            // Code block
            const code = document.createElement('pre');
            code.style.cssText = `
                background: var(--bg-secondary, #1a1a2e);
                padding: 16px;
                border-radius: 6px;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
                color: var(--text-primary, #e0e0e0);
            `;
            code.textContent = section.content;
            sectionEl.appendChild(code);
        } else {
            // Regular content
            const content = document.createElement('p');
            content.textContent = section.content;
            content.style.cssText = `
                color: var(--text-secondary, #b0b0b0);
                line-height: 1.6;
            `;
            sectionEl.appendChild(content);
        }
        
        wrapper.appendChild(sectionEl);
    });
    
    container.appendChild(wrapper);
}
```

---

### Option 3: External Documentation Links

Add URL references in constraints info:

```python
output.append("```CONSTRAINTS_INFO")
output.append(json.dumps({
    "accuracy": "±0.1mm tolerance",
    "validation": {...},
    "constraints": [...],
    "documentation": {
        "quick_start": "file:///c:/Users/.../CAD_ACCURACY_FIX_README.md",
        "full_guide": "file:///c:/Users/.../CONSTRAINED_CAD_SOLUTION.md",
        "examples": "file:///c:/Users/.../CONSTRAINED_CAD_EXAMPLES.py"
    }
}, indent=2))
```

Frontend renders clickable links in constraints tab.

---

## Recommendation

**Use Option 1 (Markdown) for now:**

The AI can output documentation as markdown **after** the CAD delimiters:

```
[AI generates CAD with delimiters - renders as tabs]

## 📖 How to Use This CAD

This model uses the CadQuery constraint solver for ±0.1mm accuracy.

### Key Features
- Dimensional validation
- Spacing constraints
- Perpendicularity enforcement

### Modify the Design
\`\`\`python
# Generate similar beam with different length
result = ai_generate_constrained_beam(
    length_mm=800,  # Change to 800mm
    profile="20x40mm"
)
\`\`\`
```

**Why this works:**
1. No code changes needed
2. Markdown already styled correctly
3. Code blocks get syntax highlighting
4. Users can scroll through explanation
5. Documentation lives "with" the CAD output

---

## Implementation Status

✅ **Completed:**
- Constraints info renders in tab
- Validation status visible
- Applied constraints listed

🎯 **Recommended Next:**
- AI outputs markdown docs after CAD delimiters
- Keep documentation contextual to each CAD generation
- Use existing markdown renderer (no new code)

⏳ **Future Enhancement:**
- Add ```ENGINEERING_DOCS delimiter (Option 2)
- Create rich documentation tab with sections
- Add interactive examples

---

## Example Complete Output

What the AI will generate:

````markdown
I've generated your T-slot beam with constraints:

```ENGINEERING_CAD
{"type": "tslot_beam_constrained", ...}
```

```3D_MODEL
{...}
```

```TECHNICAL_DRAWING
<svg>...</svg>
```

```CONSTRAINTS_INFO
{"accuracy": "±0.1mm", ...}
```

## 📖 About This Design

Your 500mm beam uses the **CadQuery constraint solver** to maintain accuracy.

### ✓ Validated Constraints
- **Length**: Exactly 500mm (±0.1mm)
- **Cross-section**: 20×40mm T-slot profile
- **Holes**: 2 mounting holes with validated spacing

### 🔧 Modify the Design

Change the length:
\`\`\`python
ai_generate_constrained_beam(
    length_mm=800,  # <-- Change this
    profile="20x40mm",
    holes=[{"position": 100}, {"position": 700}]
)
\`\`\`

Add more holes:
\`\`\`python
ai_generate_constrained_beam(
    length_mm=500,
    holes=[
        {"position": 100},
        {"position": 250},  # <-- New hole
        {"position": 400}
    ]
)
\`\`\`

### 📊 Accuracy Comparison

| Feature | Old System | New System |
|---------|-----------|------------|
| Tolerance | ±5mm | **±0.1mm** |
| Hole spacing | Not validated | **✓ Validated (≥20mm)** |
| Edge distance | Not validated | **✓ Validated (≥10mm)** |
| Perpendicularity | Approximate | **✓ Exact (90°)** |

The constraints tab shows all validation results.
````

This renders beautifully with **zero code changes** required!

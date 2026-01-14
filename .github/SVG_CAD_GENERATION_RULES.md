# SVG CAD Generation Rules
**For AI Agents Creating Technical Diagrams**

---

## 🎨 Critical Spacing Rules

### Title Block Positioning

**RULE 1: Calculate title block height**
```
Title Block Height = (Largest Font Size × Number of Lines × 1.5) + 20px padding
```

**Example:**
- Line 1: 28px font (main title)
- Line 2: 14px font (subtitle)
- Calculation: (28 × 1.5) + (14 × 1.5) + 20 = 42 + 21 + 20 = **83px**
- Round up to: **90px**

**RULE 2: Position title text**
```
Text Y-Position = Title Block Top + (Font Size × 1.2)
```

**Example:**
```svg
<!-- Title block from y=20 to y=110 (90px height) -->
<rect x="20" y="20" width="1160" height="90"/>

<!-- Main title: 28px font -->
<text x="600" y="55">Title</text>  <!-- 20 + (28 × 1.2) = 53.6 ≈ 55 -->

<!-- Subtitle: 14px font, 30px below main -->
<text x="600" y="85">Subtitle</text>  <!-- 55 + 30 = 85 -->
```

**RULE 3: Content clearance**
```
Content Start Y = Title Block Bottom + 40-60px clearance
```

**Example:**
```svg
<!-- Title block ends at y=110 -->
<rect x="20" y="20" width="1160" height="90"/>

<!-- Content starts at y=160 (50px clearance) -->
<text x="150" y="160">Content Section Heading</text>
<rect x="80" y="180" width="140" height="180"/>  <!-- +20px below heading -->
```

---

## 📐 Complete Template

### Electrical Schematic (1200×900px)

```svg
<svg viewBox="0 0 1200 900" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="1200" height="900" fill="#1a1a2e"/>
  
  <!-- Title Block: y=20 to y=110 (90px) -->
  <rect x="20" y="20" width="1160" height="90" fill="none" stroke="#ffd700" stroke-width="2"/>
  <text x="600" y="55" text-anchor="middle" font-size="28" fill="#ffd700" font-weight="bold">
    MAIN TITLE
  </text>
  <text x="600" y="85" text-anchor="middle" font-size="14" fill="#ffd700">
    Subtitle | Additional Info
  </text>
  
  <!-- Section Heading: y=160 (50px clearance from title block) -->
  <text x="150" y="160" font-size="16" fill="#4db8ff" font-weight="bold">
    Section Heading
  </text>
  
  <!-- Content: starts at y=180 (20px below section heading) -->
  <rect x="80" y="180" width="140" height="180" fill="none" stroke="#ffd700" stroke-width="3"/>
  <text x="150" y="210" text-anchor="middle" font-size="14" fill="#ffd700">
    Component Label
  </text>
  
  <!-- Footer/Legend: y=850+ (50px from bottom) -->
  <rect x="50" y="850" width="200" height="30"/>
  <text x="150" y="870" text-anchor="middle" font-size="12">Legend Item</text>
</svg>
```

### Blueprint/Layout (1400×1100px)

```svg
<svg viewBox="0 0 1400 1100" xmlns="http://www.w3.org/2000/svg">
  <!-- Background with grid -->
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#0074D9" stroke-width="0.5" opacity="0.3"/>
    </pattern>
  </defs>
  <rect width="1400" height="1100" fill="#0a1628"/>
  <rect width="1400" height="1100" fill="url(#grid)"/>
  
  <!-- Title Block: y=30 to y=110 (80px) -->
  <rect x="50" y="30" width="1300" height="80" fill="none" stroke="#0074D9" stroke-width="3"/>
  <text x="700" y="65" text-anchor="middle" font-size="24" fill="#4db8ff" font-weight="bold">
    BLUEPRINT TITLE
  </text>
  <text x="700" y="95" text-anchor="middle" font-size="14" fill="#4db8ff">
    Scale: 1:10 | All dimensions in millimeters
  </text>
  
  <!-- Enclosure/Main Content: starts at y=160 (50px clearance) -->
  <rect x="150" y="160" width="1100" height="750" fill="none" stroke="#0074D9" stroke-width="4"/>
  
  <!-- Components: y=210+ (50px inside enclosure) -->
  <rect x="200" y="210" width="535" height="205" fill="#16213e" stroke="#ffd700" stroke-width="3"/>
  <text x="467" y="290" text-anchor="middle" font-size="18" fill="#ffd700">Component A</text>
</svg>
```

---

## ✅ Validation Checklist

Before outputting SVG, verify:

- [ ] **Title block height** = (Font sizes × 1.5 × line count) + 20px
- [ ] **Title text positions** = Block top + (font size × 1.2) for each line
- [ ] **Content clearance** = Title block bottom + 40-60px minimum
- [ ] **Section headings** = Content start + 0-20px
- [ ] **Component content** = Section heading + 20-40px
- [ ] **Footer clearance** = 40-60px from bottom of viewBox

---

## ❌ Common Mistakes to Avoid

### ❌ WRONG: Insufficient clearance
```svg
<!-- Title block ends at y=100 -->
<rect x="20" y="20" width="1160" height="80"/>
<text x="600" y="60">Title</text>
<text x="600" y="85">Subtitle</text>

<!-- TOO CLOSE! Only 40px gap -->
<text x="150" y="140">Content Heading</text>  ❌
```

### ✅ CORRECT: Proper clearance
```svg
<!-- Title block ends at y=110 -->
<rect x="20" y="20" width="1160" height="90"/>
<text x="600" y="55">Title</text>
<text x="600" y="85">Subtitle</text>

<!-- GOOD! 50px gap -->
<text x="150" y="160">Content Heading</text>  ✅
```

---

## 🎯 Quick Reference

| Element | Font Size | Y-Position Formula | Example |
|---------|-----------|-------------------|---------|
| **Main Title** | 24-28px | Block top + (font × 1.2) | y=20 + (28 × 1.2) = **55** |
| **Subtitle** | 12-14px | Main title Y + 30px | y=55 + 30 = **85** |
| **Title Block** | N/A | Height = (fonts × 1.5 × lines) + 20 | (28×1.5 + 14×1.5) + 20 = **83** |
| **Section Heading** | 14-16px | Block bottom + 40-60px | y=110 + 50 = **160** |
| **Component Content** | 12-14px | Heading Y + 20-40px | y=160 + 20 = **180** |
| **Footer** | 10-12px | ViewBox height - 50px | y=900 - 50 = **850** |

---

## 💡 Pro Tips

1. **Always round up** clearances to nearest 5px or 10px for clean coordinates
2. **Use consistent spacing** throughout the diagram (e.g., always 50px clearance)
3. **Account for descenders** on large fonts (add 5-10px extra for letters like 'g', 'y', 'p')
4. **Test with longest text** - if title is very long, increase title block height
5. **Mobile-friendly** - ensure minimum 40px clearances work on small screens

---

## 🔧 Debugging Overlaps

If titles overlap content:

1. **Check title block height**: Is it tall enough for all text lines?
2. **Check text Y-positions**: Are they inside the title block bounds?
3. **Check content start**: Is there 40-60px clearance after title block?
4. **Increase viewBox height**: Add 100px if diagram feels cramped

**Quick Fix Formula:**
```
New Content Y = Current Content Y + 30px
(Shift everything down by 30 pixels)
```

---

## 📚 Examples

See these files for working examples:
- `battery-system-schematic-fixed.html` - Electrical schematic with proper spacing
- `battery-system-blueprint-fixed.html` - Blueprint with proper spacing
- `parametric-cad.html` - 3D CAD viewer with proper title positioning

---

**Last Updated:** December 29, 2025  
**Version:** 1.0  
**Author:** AI Development Team

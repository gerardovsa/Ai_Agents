/**
 * COMPREHENSIVE CSS AUDIT TOOL
 * 
 * PURPOSE: Extract ALL CSS properties from synergy elements
 * USAGE: Copy-paste into browser console when synergy is loaded
 * OUTPUT: Complete CSS consolidation report + downloadable files
 */

(function comprehensiveAudit() {
    console.log('═══════════════════════════════════════════════');
    console.log('🔍 COMPREHENSIVE CSS AUDIT - SYNERGY SYSTEM');
    console.log('═══════════════════════════════════════════════\n');

    // ==================== PART 1: FIND ALL SYNERGY ELEMENTS ====================

    const allElements = document.querySelectorAll('[class*="synergy"], [class*="milestone"], [class*="task"]');
    console.log(`📊 Found ${allElements.length} synergy-related elements\n`);

    // Group by class name
    const elementsByClass = {};
    allElements.forEach(el => {
        const classes = el.className.split(' ').filter(c => c.includes('synergy') || c.includes('milestone') || c.includes('task'));
        classes.forEach(className => {
            if (!elementsByClass[className]) {
                elementsByClass[className] = [];
            }
            elementsByClass[className].push(el);
        });
    });

    console.log(`📋 Found ${Object.keys(elementsByClass).length} unique class names:\n`);
    Object.keys(elementsByClass).sort().forEach(cls => {
        console.log(`   .${cls} (${elementsByClass[cls].length} instances)`);
    });

    // ==================== PART 2: EXTRACT ALL CSS PROPERTIES ====================

    console.log('\n\n═══════════════════════════════════════════════');
    console.log('🎨 EXTRACTING ALL CSS PROPERTIES');
    console.log('═══════════════════════════════════════════════\n');

    const cssProperties = [
        // Typography
        'fontSize', 'fontWeight', 'fontFamily', 'lineHeight', 'letterSpacing', 'textAlign', 'textTransform',
        // Colors
        'color', 'backgroundColor', 'borderColor',
        // Spacing
        'padding', 'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
        'margin', 'marginTop', 'marginRight', 'marginBottom', 'marginLeft',
        'gap',
        // Layout
        'display', 'flexDirection', 'justifyContent', 'alignItems', 'width', 'height',
        // Border
        'border', 'borderRadius', 'borderWidth', 'borderStyle',
        // Effects
        'boxShadow', 'opacity', 'transform', 'transition'
    ];

    const consolidatedData = {};

    Object.keys(elementsByClass).forEach(className => {
        const elements = elementsByClass[className];
        const element = elements[0]; // Use first instance
        const computed = window.getComputedStyle(element);

        const styles = {};
        cssProperties.forEach(prop => {
            const value = computed[prop];
            if (value && value !== '' && value !== 'normal' && value !== 'none' && value !== 'auto') {
                styles[prop] = value;
            }
        });

        consolidatedData[className] = {
            count: elements.length,
            styles: styles,
            context: element.closest('[data-context]')?.dataset.context || 'unknown'
        };
    });

    // ==================== PART 3: ANALYZE PATTERNS ====================

    console.log('🔍 ANALYZING PATTERNS...\n');

    // Font sizes
    const fontSizes = new Map();
    Object.entries(consolidatedData).forEach(([cls, data]) => {
        if (data.styles.fontSize) {
            const size = data.styles.fontSize;
            if (!fontSizes.has(size)) {
                fontSizes.set(size, []);
            }
            fontSizes.get(size).push(cls);
        }
    });

    console.log('📏 Font Size Distribution:');
    [...fontSizes.entries()].sort((a, b) => parseFloat(a[0]) - parseFloat(b[0])).forEach(([size, classes]) => {
        console.log(`   ${size}: ${classes.length} classes`);
        console.log(`      ${classes.slice(0, 5).join(', ')}${classes.length > 5 ? '...' : ''}`);
    });

    // Colors
    const colors = new Map();
    Object.entries(consolidatedData).forEach(([cls, data]) => {
        if (data.styles.color) {
            const color = data.styles.color;
            if (!colors.has(color)) {
                colors.set(color, []);
            }
            colors.get(color).push(cls);
        }
    });

    console.log('\n🎨 Color Distribution:');
    [...colors.entries()].slice(0, 10).forEach(([color, classes]) => {
        console.log(`   ${color}: ${classes.length} classes`);
    });

    // Spacing patterns
    const paddings = new Map();
    Object.entries(consolidatedData).forEach(([cls, data]) => {
        if (data.styles.padding) {
            const padding = data.styles.padding;
            if (!paddings.has(padding)) {
                paddings.set(padding, []);
            }
            paddings.get(padding).push(cls);
        }
    });

    console.log('\n📦 Padding Distribution:');
    [...paddings.entries()].slice(0, 10).forEach(([padding, classes]) => {
        console.log(`   ${padding}: ${classes.length} classes`);
    });

    // ==================== PART 4: GENERATE CONSOLIDATED CSS ====================

    console.log('\n\n═══════════════════════════════════════════════');
    console.log('🎯 GENERATING CONSOLIDATED CSS');
    console.log('═══════════════════════════════════════════════\n');

    // Design Tokens
    const tokens = {
        fontSize: [...new Set([...fontSizes.keys()].map(s => parseFloat(s)))].sort((a, b) => a - b),
        colors: [...new Set([...colors.keys()])],
        paddings: [...new Set([...paddings.keys()])].slice(0, 10)
    };

    let consolidatedCSS = `/**
 * CONSOLIDATED SYNERGY STYLES
 * Generated: ${new Date().toISOString()}
 * Total Classes: ${Object.keys(consolidatedData).length}
 * Elements Audited: ${allElements.length}
 */

/* ==================== DESIGN TOKENS ==================== */

:root {
  /* Font Sizes (${tokens.fontSize.length} unique values) */\n`;

    const sizeNames = ['2xs', 'xs', 'sm', 'base', 'md', 'lg', 'xl', '2xl', '3xl', '4xl'];
    tokens.fontSize.forEach((size, i) => {
        const name = sizeNames[i] || `size-${i}`;
        consolidatedCSS += `  --synergy-text-${name}: ${size}px;\n`;
    });

    consolidatedCSS += `\n  /* Colors (top 10 most used) */\n`;
    [...colors.entries()].slice(0, 10).forEach(([color, classes], i) => {
        const name = ['primary', 'secondary', 'tertiary', 'accent', 'muted', 'subtle', 'emphasis', 'info', 'success', 'warning'][i];
        consolidatedCSS += `  --synergy-color-${name}: ${color}; /* Used by ${classes.length} classes */\n`;
    });

    consolidatedCSS += `\n  /* Common Paddings */\n`;
    [...paddings.entries()].slice(0, 8).forEach(([padding], i) => {
        consolidatedCSS += `  --synergy-padding-${i + 1}: ${padding};\n`;
    });

    consolidatedCSS += `}\n\n/* ==================== COMPONENT STYLES ==================== */\n\n`;

    // Generate CSS for each class
    Object.entries(consolidatedData).sort().forEach(([className, data]) => {
        consolidatedCSS += `.${className} {\n`;

        // Typography
        if (data.styles.fontSize) {
            const sizeIndex = tokens.fontSize.indexOf(parseFloat(data.styles.fontSize));
            const sizeName = sizeNames[sizeIndex] || `size-${sizeIndex}`;
            consolidatedCSS += `  font-size: var(--synergy-text-${sizeName});\n`;
        }
        if (data.styles.fontWeight && data.styles.fontWeight !== '400') {
            consolidatedCSS += `  font-weight: ${data.styles.fontWeight};\n`;
        }
        if (data.styles.lineHeight && data.styles.lineHeight !== '1.5') {
            consolidatedCSS += `  line-height: ${data.styles.lineHeight};\n`;
        }

        // Colors
        if (data.styles.color) {
            const colorIndex = [...colors.keys()].indexOf(data.styles.color);
            if (colorIndex < 10) {
                const colorName = ['primary', 'secondary', 'tertiary', 'accent', 'muted', 'subtle', 'emphasis', 'info', 'success', 'warning'][colorIndex];
                consolidatedCSS += `  color: var(--synergy-color-${colorName});\n`;
            } else {
                consolidatedCSS += `  color: ${data.styles.color};\n`;
            }
        }

        // Layout
        if (data.styles.display && data.styles.display !== 'block') {
            consolidatedCSS += `  display: ${data.styles.display};\n`;
        }
        if (data.styles.padding) {
            const paddingIndex = [...paddings.keys()].indexOf(data.styles.padding);
            if (paddingIndex >= 0 && paddingIndex < 8) {
                consolidatedCSS += `  padding: var(--synergy-padding-${paddingIndex + 1});\n`;
            } else {
                consolidatedCSS += `  padding: ${data.styles.padding};\n`;
            }
        }
        if (data.styles.gap) {
            consolidatedCSS += `  gap: ${data.styles.gap};\n`;
        }

        // Border
        if (data.styles.borderRadius && data.styles.borderRadius !== '0px') {
            consolidatedCSS += `  border-radius: ${data.styles.borderRadius};\n`;
        }

        consolidatedCSS += `}\n\n`;
    });

    // ==================== PART 5: SAVE RESULTS ====================

    console.log('💾 Saving results...\n');

    // Save to window for access
    window.synergyAuditComplete = {
        elementsByClass,
        consolidatedData,
        tokens,
        css: consolidatedCSS
    };

    // Display summary
    console.log('✅ AUDIT COMPLETE!\n');
    console.log(`📊 Summary:`);
    console.log(`   - Elements found: ${allElements.length}`);
    console.log(`   - Unique classes: ${Object.keys(consolidatedData).length}`);
    console.log(`   - Font sizes: ${tokens.fontSize.length}`);
    console.log(`   - Colors: ${tokens.colors.length}`);
    console.log(`   - Padding variants: ${tokens.paddings.length}`);
    console.log(`\n📋 Data saved to: window.synergyAuditComplete`);
    console.log(`\n📥 To download CSS file, run: downloadConsolidatedCSS()\n`);

    // ==================== PART 6: DOWNLOAD FUNCTION ====================

    window.downloadConsolidatedCSS = function () {
        const blob = new Blob([consolidatedCSS], { type: 'text/css' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'synergy-consolidated-full.css';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        console.log('✅ Downloaded: synergy-consolidated-full.css');
    };

    // ==================== PART 7: COMPARISON REPORT ====================

    console.log('\n═══════════════════════════════════════════════');
    console.log('📊 CONSOLIDATION OPPORTUNITIES');
    console.log('═══════════════════════════════════════════════\n');

    // Find duplicate styles
    const styleGroups = new Map();
    Object.entries(consolidatedData).forEach(([className, data]) => {
        const styleKey = JSON.stringify(data.styles);
        if (!styleGroups.has(styleKey)) {
            styleGroups.set(styleKey, []);
        }
        styleGroups.get(styleKey).push(className);
    });

    const duplicates = [...styleGroups.entries()].filter(([_, classes]) => classes.length > 1);

    if (duplicates.length > 0) {
        console.log(`⚠️ Found ${duplicates.length} groups of classes with IDENTICAL styles:\n`);
        duplicates.slice(0, 5).forEach(([styles, classes]) => {
            console.log(`   ${classes.join(', ')}`);
            console.log(`   → Can merge into single class\n`);
        });
        if (duplicates.length > 5) {
            console.log(`   ... and ${duplicates.length - 5} more groups\n`);
        }
    }

    // Font size consolidation
    console.log(`\n📏 Font Size Consolidation:`);
    console.log(`   Current: ${fontSizes.size} different sizes`);
    console.log(`   Recommended: ${Math.min(9, fontSizes.size)} sizes`);
    console.log(`   Savings: ${fontSizes.size - Math.min(9, fontSizes.size)} redundant definitions\n`);

    // Color consolidation
    console.log(`🎨 Color Consolidation:`);
    console.log(`   Current: ${colors.size} different colors`);
    console.log(`   Recommended: ${Math.min(15, colors.size)} semantic colors`);
    console.log(`   Savings: ${colors.size - Math.min(15, colors.size)} redundant definitions\n`);

    console.log('═══════════════════════════════════════════════\n');

    return {
        summary: `Audited ${allElements.length} elements with ${Object.keys(consolidatedData).length} classes`,
        data: consolidatedData,
        css: consolidatedCSS,
        download: 'Run downloadConsolidatedCSS() to save'
    };
})();

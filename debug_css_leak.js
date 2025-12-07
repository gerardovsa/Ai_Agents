/**
 * CSS LEAK DEBUGGER
 * =================
 * Identifies all CSS rules affecting specific elements and their sources
 * 
 * Usage in browser console:
 * 1. Copy this entire file
 * 2. Paste into console
 * 3. Run: debugCSSLeak('.agent-header-controls')
 * 4. Run: debugCSSLeak('.agent-input-container')
 */

function debugCSSLeak(selector, options = {}) {
    const {
        showInherited = true,
        showComputed = true,
        showSpecificity = true,
        groupBySource = true
    } = options;

    console.clear();
    console.log(`%c🔍 CSS LEAK DEBUGGER`, 'font-size: 20px; font-weight: bold; color: #ff6b6b;');
    console.log(`%cSelector: ${selector}`, 'font-size: 14px; color: #4ecdc4;');
    console.log('━'.repeat(80));

    const elements = document.querySelectorAll(selector);

    if (elements.length === 0) {
        console.error(`❌ No elements found matching: ${selector}`);
        return;
    }

    console.log(`%c✅ Found ${elements.length} element(s)`, 'color: #95e1d3; font-weight: bold;');
    console.log('');

    elements.forEach((element, index) => {
        console.log(`%c═══ ELEMENT ${index + 1} / ${elements.length} ═══`, 'font-size: 16px; font-weight: bold; color: #f38181;');
        console.log('Element:', element);
        console.log('');

        // Get all applied styles
        const computedStyle = window.getComputedStyle(element);
        const matchedRules = getMatchedCSSRules(element);

        // Group by source
        const rulesBySource = new Map();

        matchedRules.forEach(rule => {
            const source = rule.source || 'Unknown';
            if (!rulesBySource.has(source)) {
                rulesBySource.set(source, []);
            }
            rulesBySource.get(source).push(rule);
        });

        // Display by source
        console.log(`%c📚 CSS RULES BY SOURCE (${rulesBySource.size} sources)`, 'font-weight: bold; color: #ffd93d;');

        rulesBySource.forEach((rules, source) => {
            console.log('');
            console.log(`%c📄 ${source} (${rules.length} rules)`, 'color: #6bcf7f; font-weight: bold;');
            console.log(`${'─'.repeat(80)}`);

            rules.forEach(rule => {
                console.log(`%c${rule.selector}`, 'color: #95a5a6; font-size: 11px;');

                if (showSpecificity) {
                    console.log(`  Specificity: ${rule.specificity || 'N/A'}`);
                }

                console.log(`  Properties (${rule.properties.length}):`);
                rule.properties.forEach(prop => {
                    const computedValue = computedStyle.getPropertyValue(prop.name);
                    const match = prop.value === computedValue ? '✅' : '⚠️';
                    console.log(`    ${match} ${prop.name}: ${prop.value}`);
                    if (prop.value !== computedValue) {
                        console.log(`       (computed: ${computedValue})`);
                    }
                });
                console.log('');
            });
        });

        // Show important computed styles
        if (showComputed) {
            console.log('');
            console.log(`%c🎨 KEY COMPUTED STYLES`, 'font-weight: bold; color: #a29bfe;');
            console.log('─'.repeat(80));

            const keyProperties = [
                'display', 'position', 'width', 'height', 'margin', 'padding',
                'background', 'background-color', 'border', 'z-index',
                'overflow', 'flex', 'grid', 'opacity', 'visibility',
                'transform', 'transition', 'animation'
            ];

            keyProperties.forEach(prop => {
                const value = computedStyle.getPropertyValue(prop);
                if (value && value !== 'none' && value !== 'normal' && value !== 'auto') {
                    console.log(`  ${prop}: ${value}`);
                }
            });
        }

        // Check for inline styles
        if (element.style.length > 0) {
            console.log('');
            console.log(`%c⚠️ INLINE STYLES DETECTED (${element.style.length})`, 'color: #ff6b6b; font-weight: bold;');
            console.log('─'.repeat(80));
            for (let i = 0; i < element.style.length; i++) {
                const prop = element.style[i];
                console.log(`  ${prop}: ${element.style[prop]}`);
            }
        }

        // Check for affecting classes
        console.log('');
        console.log(`%c🏷️ CLASSES (${element.classList.length})`, 'font-weight: bold; color: #74b9ff;');
        console.log('─'.repeat(80));
        element.classList.forEach(cls => {
            console.log(`  .${cls}`);
        });

        console.log('');
        console.log('═'.repeat(80));
        console.log('');
    });

    // Additional leak detection
    detectCommonLeaks(elements);
}

function getMatchedCSSRules(element) {
    const rules = [];
    const sheets = document.styleSheets;

    for (let i = 0; i < sheets.length; i++) {
        const sheet = sheets[i];
        let sheetRules;

        try {
            sheetRules = sheet.cssRules || sheet.rules;
        } catch (e) {
            console.warn(`Cannot access stylesheet: ${sheet.href} (CORS)`);
            continue;
        }

        if (!sheetRules) continue;

        const source = sheet.href ||
            (sheet.ownerNode?.id ? `<style id="${sheet.ownerNode.id}">` : '<style>') ||
            'Inline';

        processRules(sheetRules, element, source, rules);
    }

    return rules;
}

function processRules(cssRules, element, source, results) {
    for (let i = 0; i < cssRules.length; i++) {
        const rule = cssRules[i];

        // Handle @media, @supports, etc.
        if (rule.cssRules) {
            processRules(rule.cssRules, element, source, results);
            continue;
        }

        if (rule.selectorText) {
            try {
                if (element.matches(rule.selectorText)) {
                    const properties = [];
                    const style = rule.style;

                    for (let j = 0; j < style.length; j++) {
                        const propName = style[j];
                        properties.push({
                            name: propName,
                            value: style.getPropertyValue(propName),
                            important: style.getPropertyPriority(propName) === 'important'
                        });
                    }

                    results.push({
                        selector: rule.selectorText,
                        properties: properties,
                        source: source,
                        specificity: calculateSpecificity(rule.selectorText)
                    });
                }
            } catch (e) {
                // Invalid selector or pseudo-element
            }
        }
    }
}

function calculateSpecificity(selector) {
    // Simple specificity calculator
    const ids = (selector.match(/#/g) || []).length;
    const classes = (selector.match(/\./g) || []).length;
    const attrs = (selector.match(/\[/g) || []).length;
    const tags = selector.split(/[\s>+~]/).filter(s => s && !s.match(/[#.:[\]]/)).length;

    return `${ids},${classes + attrs},${tags}`;
}

function detectCommonLeaks(elements) {
    console.log('%c🔬 LEAK DETECTION ANALYSIS', 'font-size: 16px; font-weight: bold; color: #ff6b6b;');
    console.log('═'.repeat(80));

    elements.forEach((element, index) => {
        console.log(`%cElement ${index + 1}:`, 'font-weight: bold;');

        // Check for z-index stacking
        const zIndex = window.getComputedStyle(element).zIndex;
        if (zIndex !== 'auto') {
            console.log(`  ⚠️ z-index: ${zIndex} (may cause stacking issues)`);
        }

        // Check for absolute/fixed positioning
        const position = window.getComputedStyle(element).position;
        if (position === 'absolute' || position === 'fixed') {
            console.log(`  ⚠️ position: ${position} (may escape container)`);
        }

        // Check for transforms
        const transform = window.getComputedStyle(element).transform;
        if (transform !== 'none') {
            console.log(`  ℹ️ transform: ${transform} (creates new stacking context)`);
        }

        // Check for overflow issues
        const overflow = window.getComputedStyle(element).overflow;
        if (overflow !== 'visible') {
            console.log(`  ℹ️ overflow: ${overflow}`);
        }

        // Check parent styles affecting children
        let parent = element.parentElement;
        let depth = 0;
        console.log(`  📦 Parent chain:`);

        while (parent && depth < 5) {
            const parentStyle = window.getComputedStyle(parent);
            const issues = [];

            if (parentStyle.overflow !== 'visible') issues.push(`overflow:${parentStyle.overflow}`);
            if (parentStyle.position !== 'static') issues.push(`position:${parentStyle.position}`);
            if (parentStyle.zIndex !== 'auto') issues.push(`z-index:${parentStyle.zIndex}`);
            if (parentStyle.transform !== 'none') issues.push(`transform:${parentStyle.transform}`);

            if (issues.length > 0) {
                console.log(`    ${'  '.repeat(depth)}↑ ${parent.tagName}.${parent.className} [${issues.join(', ')}]`);
            } else {
                console.log(`    ${'  '.repeat(depth)}↑ ${parent.tagName}.${parent.className}`);
            }

            parent = parent.parentElement;
            depth++;
        }

        console.log('');
    });
}

// QUICK ACCESS FUNCTIONS
function findCSSSource(propertyName, element) {
    const rules = getMatchedCSSRules(element);
    const sources = new Set();

    rules.forEach(rule => {
        rule.properties.forEach(prop => {
            if (prop.name === propertyName) {
                sources.add(rule.source);
            }
        });
    });

    return Array.from(sources);
}

function compareElements(selector1, selector2) {
    console.clear();
    console.log('%c🔄 COMPARING TWO ELEMENTS', 'font-size: 18px; font-weight: bold; color: #a29bfe;');

    const el1 = document.querySelector(selector1);
    const el2 = document.querySelector(selector2);

    if (!el1 || !el2) {
        console.error('One or both elements not found');
        return;
    }

    const style1 = window.getComputedStyle(el1);
    const style2 = window.getComputedStyle(el2);

    const allProps = new Set([...Object.keys(style1), ...Object.keys(style2)]);
    const differences = [];

    allProps.forEach(prop => {
        if (typeof style1[prop] === 'string' && style1[prop] !== style2[prop]) {
            differences.push({
                property: prop,
                value1: style1[prop],
                value2: style2[prop]
            });
        }
    });

    console.log(`%cFound ${differences.length} differences`, 'font-weight: bold; color: #ff6b6b;');
    differences.forEach(diff => {
        console.log(`\n${diff.property}:`);
        console.log(`  1️⃣ ${selector1}: ${diff.value1}`);
        console.log(`  2️⃣ ${selector2}: ${diff.value2}`);
    });
}

// AUTO-RUN FOR SPECIFIC ELEMENTS
console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #95e1d3;');
console.log('%c CSS LEAK DEBUGGER LOADED', 'font-size: 16px; font-weight: bold; color: #4ecdc4;');
console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #95e1d3;');
console.log('');
console.log('%cAvailable commands:', 'font-weight: bold; color: #ffd93d;');
console.log('  debugCSSLeak(".agent-header-controls")');
console.log('  debugCSSLeak(".agent-input-container")');
console.log('  findCSSSource("property-name", element)');
console.log('  compareElements(".selector1", ".selector2")');
console.log('');
console.log('%cRunning auto-analysis...', 'color: #95e1d3;');
console.log('');

// Auto-run for the reported elements
setTimeout(() => {
    debugCSSLeak('.agent-header-controls');
    console.log('\n\n');
    debugCSSLeak('.agent-input-container');
}, 500);

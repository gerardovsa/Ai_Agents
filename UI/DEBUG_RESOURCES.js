/**
 * RESOURCE DIAGNOSTIC TOOL
 * Shows all loaded CSS/JS and their cache status
 */

console.log('📦 RESOURCE DIAGNOSTIC REPORT\n' + '='.repeat(80));

// 1. All Stylesheets
console.log('\n🎨 LOADED STYLESHEETS:');
const stylesheets = Array.from(document.styleSheets);
stylesheets.forEach((sheet, index) => {
    if (sheet.href) {
        console.log(`  [${index}] ${sheet.href}`);
        try {
            console.log(`      Rules: ${sheet.cssRules?.length || 0}`);
        } catch (e) {
            console.log(`      Rules: BLOCKED (CORS)`);
        }
        console.log(`      Disabled: ${sheet.disabled}`);
    } else if (sheet.ownerNode?.tagName === 'STYLE') {
        const parent = sheet.ownerNode.parentElement?.tagName || 'unknown';
        const id = sheet.ownerNode.id || 'no-id';
        console.log(`  [${index}] <style> tag in <${parent}> (id: ${id})`);
        try {
            console.log(`      Rules: ${sheet.cssRules?.length || 0}`);
        } catch (e) {
            console.log(`      Rules: BLOCKED (CORS)`);
        }
        console.log(`      Content length: ${sheet.ownerNode.textContent?.length || 0} chars`);
    }
});

// 2. All <style> tags
console.log('\n📝 INLINE STYLE TAGS:');
const styleTags = document.querySelectorAll('style');
console.log(`  Total: ${styleTags.length}`);
styleTags.forEach((style, index) => {
    const location = style.parentElement?.tagName || 'unknown';
    const id = style.id || 'no-id';
    const classes = style.className || 'no-class';
    console.log(`  [${index}] <style id="${id}" class="${classes}"> in <${location}>`);
    console.log(`      Length: ${style.textContent.length} chars`);
    console.log(`      First 100 chars: ${style.textContent.substring(0, 100)}...`);
});

// 3. All external CSS files
console.log('\n🔗 EXTERNAL CSS FILES:');
const links = document.querySelectorAll('link[rel="stylesheet"]');
links.forEach((link, index) => {
    console.log(`  [${index}] ${link.href}`);
    console.log(`      Media: ${link.media || 'all'}`);
    console.log(`      Disabled: ${link.disabled}`);
});

// 4. All JavaScript files
console.log('\n📜 LOADED JAVASCRIPT FILES:');
const scripts = document.querySelectorAll('script[src]');
scripts.forEach((script, index) => {
    console.log(`  [${index}] ${script.src}`);
    console.log(`      Async: ${script.async}`);
    console.log(`      Defer: ${script.defer}`);
    console.log(`      Type: ${script.type || 'text/javascript'}`);
});

// 5. Check for specific critical CSS rules
console.log('\n🔍 CRITICAL CSS RULES CHECK:');

function findCSSRule(selector) {
    for (let sheet of document.styleSheets) {
        try {
            const rules = sheet.cssRules || sheet.rules;
            for (let rule of rules) {
                if (rule.selectorText === selector) {
                    return rule.style.cssText;
                }
            }
        } catch (e) {
            // Cross-origin stylesheet
        }
    }
    return 'NOT FOUND';
}

const criticalSelectors = [
    '.platform-container',
    '.main-content-wrapper',
    '.main-content',
    '.universal-sidebar',
    '.sidebar',
    '.right-sidebar',
    '.top-header',
    '.ai-chat-panel'
];

criticalSelectors.forEach(selector => {
    const rule = findCSSRule(selector);
    console.log(`  ${selector}:`);
    if (rule === 'NOT FOUND') {
        console.log('    ❌ NOT FOUND');
    } else {
        console.log(`    ✅ ${rule.substring(0, 100)}${rule.length > 100 ? '...' : ''}`);
    }
});

// 6. Check computed styles for key elements
console.log('\n💻 COMPUTED STYLES (LIVE):');

const platformContainer = document.querySelector('.platform-container');
if (platformContainer) {
    const styles = getComputedStyle(platformContainer);
    console.log('  .platform-container:');
    console.log(`    display: ${styles.display}`);
    console.log(`    grid-template-columns: ${styles.gridTemplateColumns}`);
    console.log(`    grid-template-rows: ${styles.gridTemplateRows}`);
}

const mainWrapper = document.querySelector('.main-content-wrapper');
if (mainWrapper) {
    const styles = getComputedStyle(mainWrapper);
    console.log('  .main-content-wrapper:');
    console.log(`    display: ${styles.display}`);
    console.log(`    grid-column: ${styles.gridColumn}`);
    console.log(`    grid-row: ${styles.gridRow}`);
    console.log(`    height: ${styles.height}`);
}

const mainContent = document.querySelector('.main-content');
if (mainContent) {
    const styles = getComputedStyle(mainContent);
    console.log('  .main-content:');
    console.log(`    height: ${styles.height}`);
    console.log(`    overflow-y: ${styles.overflowY}`);
}

// 7. Check if CSS is from cache
console.log('\n🗄️ CACHE STATUS:');
if (performance && performance.getEntriesByType) {
    const resources = performance.getEntriesByType('resource');
    const cssResources = resources.filter(r => r.name.includes('.css'));

    console.log(`  Total CSS resources: ${cssResources.length}`);
    cssResources.forEach(resource => {
        const url = resource.name.split('/').pop();
        console.log(`  ${url}:`);
        console.log(`    Transfer size: ${resource.transferSize} bytes`);
        console.log(`    Cached: ${resource.transferSize === 0 ? 'YES (from cache)' : 'NO (fresh)'}`);
        console.log(`    Duration: ${resource.duration.toFixed(2)}ms`);
    });
}

// 8. Document structure check
console.log('\n🌳 DOCUMENT STRUCTURE:');
console.log(`  <html> classes: ${document.documentElement.className || 'none'}`);
console.log(`  <body> classes: ${document.body.className || 'none'}`);
console.log(`  .platform-container exists: ${!!document.querySelector('.platform-container')}`);
console.log(`  .platform-container.active: ${document.querySelector('.platform-container.active') ? 'YES' : 'NO'}`);

// 9. Browser info
console.log('\n🌐 BROWSER INFO:');
console.log(`  User Agent: ${navigator.userAgent}`);
console.log(`  Viewport: ${window.innerWidth}x${window.innerHeight}`);
console.log(`  Device Pixel Ratio: ${window.devicePixelRatio}`);

// 10. Check for CSS variable values
console.log('\n🎨 CSS CUSTOM PROPERTIES:');
const root = document.documentElement;
const rootStyles = getComputedStyle(root);
const cssVars = [
    '--sidebar-width',
    '--header-height',
    '--chat-width',
    '--bg-primary',
    '--bg-secondary',
    '--text-primary',
    '--accent-primary'
];

cssVars.forEach(varName => {
    const value = rootStyles.getPropertyValue(varName);
    console.log(`  ${varName}: ${value || 'NOT SET'}`);
});

console.log('\n' + '='.repeat(80));
console.log('✅ RESOURCE DIAGNOSTIC COMPLETE');
console.log('💡 If CSS rules show "NOT FOUND", the stylesheet is not loaded properly');
console.log('💡 If "Cached: YES", you may need to hard refresh or clear cache');

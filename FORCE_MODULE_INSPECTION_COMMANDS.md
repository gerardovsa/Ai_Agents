# Force Module Inspection Commands

Copy and paste these commands into the browser console to force modules to load and inspect their HTML structure and CSS.

---

## 🔍 Universal Search Dashboard

### Command 1: Force Load Universal Search Dashboard
```javascript
(async function() {
    console.log('🔍 [INSPECT] Loading Universal Search Dashboard...');
    
    // Check if module is registered
    console.log('📋 [CHECK] Module Loader exists:', !!window.moduleLoader);
    console.log('📋 [CHECK] ModuleLoaderV4 exists:', !!window.ModuleLoaderV4);
    
    if (window.moduleLoader) {
        console.log('📋 [CHECK] Loaded modules:', Object.keys(window.moduleLoader.loadedModules || {}));
        console.log('📋 [CHECK] Module registry:', window.moduleLoader.moduleRegistry);
    }
    
    // Check if UniversalSearch class exists
    console.log('📋 [CHECK] UniversalSearch class:', typeof window.UniversalSearch);
    
    // Switch to Universal Search tab
    switchTab('universal-search');
    
    // Wait for tab to activate
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Try multiple loading approaches
    console.log('🔄 [LOADING] Attempting to load module...');
    
    // Approach 1: Via module loader
    if (window.moduleLoader) {
        try {
            await window.moduleLoader.loadModule('universal-search', 'dashboard');
            console.log('✅ Module loader succeeded');
        } catch (error) {
            console.warn('❌ Module loader failed:', error.message);
        }
    }
    
    // Approach 2: Direct instantiation if class exists
    if (window.UniversalSearch && !window.moduleLoader?.loadedModules?.['universal-search']) {
        console.log('🔄 [LOADING] Trying direct instantiation...');
        try {
            const module = new window.UniversalSearch();
            const container = document.getElementById('universal-search-container');
            if (container && module.onDashboardLoad) {
                const utilities = {
                    dom: { getContainer: () => container },
                    api: { get: () => Promise.resolve({ sources: {} }) },
                    storage: { get: () => null, set: () => {} },
                    events: { track: () => {} },
                    log: { info: console.log, warn: console.warn, error: console.error }
                };
                await module.onDashboardLoad(utilities);
                console.log('✅ Direct instantiation succeeded');
            }
        } catch (error) {
            console.warn('❌ Direct instantiation failed:', error);
        }
    }
    
    // Wait for content to render
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Find the container
    const container = document.getElementById('universal-search-container');
    const tabContent = document.getElementById('tab-universal-search');
    
    console.log('📦 [INSPECT] Container Found:', !!container);
    console.log('📦 [INSPECT] Tab Content Found:', !!tabContent);
    
    if (container) {
        console.log('📄 [HTML STRUCTURE]');
        console.log(container.innerHTML.substring(0, 2000) + '...');
        console.log('\n🎨 [CSS CLASSES]');
        console.log('Container classes:', container.className);
        
        // List all child elements with classes
        const elements = container.querySelectorAll('[class]');
        const classMap = {};
        elements.forEach(el => {
            const classes = el.className.split(' ').filter(c => c);
            classes.forEach(c => {
                if (!classMap[c]) classMap[c] = 0;
                classMap[c]++;
            });
        });
        
        console.log('\n📊 [CLASS USAGE COUNT]');
        Object.entries(classMap)
            .sort((a, b) => b[1] - a[1])
            .forEach(([className, count]) => {
                console.log(`  ${className}: ${count} times`);
            });
        
        // Get computed styles for main elements
        console.log('\n💅 [COMPUTED STYLES - Container]');
        const containerStyles = window.getComputedStyle(container);
        console.log('Display:', containerStyles.display);
        console.log('Position:', containerStyles.position);
        console.log('Width:', containerStyles.width);
        console.log('Height:', containerStyles.height);
        console.log('Padding:', containerStyles.padding);
        console.log('Background:', containerStyles.backgroundColor);
        
        // Find dashboard cards
        const cards = container.querySelectorAll('.dashboard-card');
        console.log(`\n🎴 [DASHBOARD CARDS] Found ${cards.length} cards`);
        cards.forEach((card, i) => {
            console.log(`\nCard ${i + 1}:`);
            console.log('  Classes:', card.className);
            const header = card.querySelector('.card-header');
            if (header) {
                const title = header.querySelector('.card-title');
                console.log('  Title:', title ? title.textContent.trim() : 'No title');
            }
        });
    }
    
    console.log('\n✅ [INSPECT] Universal Search inspection complete!');
})();
```

---

## 📊 Vector Database Sidebar

### Command 2: Force Load Vector Database Sidebar
```javascript
(async function() {
    console.log('📊 [INSPECT] Loading Vector Database Sidebar...');
    
    // Step 1: Load HTML template
    const sidebar = document.getElementById('vector-database');
    console.log('📦 [INSPECT] Sidebar Found:', !!sidebar);
    
    if (sidebar) {
        console.log('🔄 [LOADING] Fetching HTML template...');
        try {
            const response = await fetch('/modules_internal/vector_database/vector_database.html');
            if (response.ok) {
                const html = await response.text();
                sidebar.innerHTML = html;
                console.log('✅ [LOADING] HTML template loaded');
            } else {
                console.error('❌ [LOADING] Failed to fetch HTML:', response.status);
            }
        } catch (error) {
            console.error('❌ [LOADING] Error fetching HTML:', error);
        }
    }
    
    // Step 2: Force open the sidebar
    console.log('🔄 [OPENING] Forcing sidebar open...');
    if (sidebar) {
        sidebar.classList.remove('collapsed');
        sidebar.classList.add('expanded');
        sidebar.style.transform = 'translateX(0)';
        console.log('✅ [OPENING] Sidebar should now be visible');
    }
    
    // Wait for content to render
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Step 3: Inspect the result
    if (sidebar) {
        console.log('\n📄 [HTML STRUCTURE]');
        console.log(sidebar.innerHTML.substring(0, 500) + '...');
        
        console.log('\n🎨 [CSS CLASSES]');
        console.log('Sidebar classes:', sidebar.className);
        
        // Check if sidebar is visible
        const styles = window.getComputedStyle(sidebar);
        console.log('\n👁️ [VISIBILITY]');
        console.log('Display:', styles.display);
        console.log('Visibility:', styles.visibility);
        console.log('Opacity:', styles.opacity);
        console.log('Transform:', styles.transform);
        console.log('Right position:', styles.right);
        console.log('Z-index:', styles.zIndex);
        
        // Check for collapsed class
        console.log('\n🔍 [STATE]');
        console.log('Has collapsed class:', sidebar.classList.contains('collapsed'));
        console.log('All classes:', Array.from(sidebar.classList).join(', '));
        
        // List all child elements with classes
        const elements = sidebar.querySelectorAll('[class]');
        const classMap = {};
        elements.forEach(el => {
            const classes = el.className.split(' ').filter(c => c);
            classes.forEach(c => {
                if (!classMap[c]) classMap[c] = 0;
                classMap[c]++;
            });
        });
        
        console.log('\n📊 [CLASS USAGE COUNT]');
        Object.entries(classMap)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 20)
            .forEach(([className, count]) => {
                console.log(`  ${className}: ${count} times`);
            });
        
        // Check for content
        const header = sidebar.querySelector('.vector-db-sidebar-header, [class*="header"]');
        console.log('\n📋 [CONTENT CHECK]');
        console.log('Has header:', !!header);
        console.log('Inner HTML length:', sidebar.innerHTML.length);
        console.log('Has meaningful content:', sidebar.innerHTML.length > 100);
    }
    
    console.log('\n✅ [INSPECT] Vector Database inspection complete!');
})();
```

---

## 🔄 Database Visualizer

### Command 3: Force Load Database Visualizer
```javascript
(async function() {
    console.log('🔄 [INSPECT] Loading Database Visualizer...');
    
    // Find and click the Database Visualizer button
    const dbBtn = document.querySelector('[data-module="database-visualizer"]');
    if (dbBtn) {
        console.log('🔘 [INSPECT] Clicking Database Visualizer button...');
        dbBtn.click();
    }
    
    // Wait for module to load
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Check both sidebar and dashboard
    const sidebar = document.querySelector('#database-visualizer-sidebar, [id*="database-visualizer"]');
    const dashboard = document.getElementById('tab-database-visualizer');
    
    console.log('📦 [INSPECT] Sidebar Found:', !!sidebar);
    console.log('📦 [INSPECT] Dashboard Found:', !!dashboard);
    
    const container = sidebar || dashboard;
    
    if (container) {
        console.log('📄 [HTML STRUCTURE]');
        console.log(container.innerHTML.substring(0, 2000) + '...');
        
        console.log('\n🎨 [CSS CLASSES]');
        console.log('Container classes:', container.className);
        console.log('Container ID:', container.id);
        
        // Get all unique classes
        const elements = container.querySelectorAll('[class]');
        const allClasses = new Set();
        elements.forEach(el => {
            el.className.split(' ').filter(c => c).forEach(c => allClasses.add(c));
        });
        
        console.log('\n📊 [ALL CSS CLASSES USED]');
        Array.from(allClasses).sort().forEach(className => {
            console.log(`  .${className}`);
        });
    }
    
    console.log('\n✅ [INSPECT] Database Visualizer inspection complete!');
})();
```

---

## 🎯 All Modules Complete Inspection

### Command 4: Inspect All Three Modules
```javascript
(async function() {
    console.log('🎯 [INSPECT ALL] Starting complete inspection...\n');
    
    const modules = [
        { name: 'Universal Search', tab: 'universal-search', container: 'universal-search-container' },
        { name: 'Vector Database', button: '[data-action="vectordb"]', container: 'vector-database' },
        { name: 'Database Visualizer', button: '[data-module="database-visualizer"]', container: 'database-visualizer-sidebar' }
    ];
    
    for (const module of modules) {
        console.log(`\n${'='.repeat(60)}`);
        console.log(`📦 MODULE: ${module.name}`);
        console.log('='.repeat(60));
        
        // Activate module
        if (module.tab) {
            switchTab(module.tab);
        } else if (module.button) {
            const btn = document.querySelector(module.button);
            if (btn) btn.click();
        }
        
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Find container
        const container = document.getElementById(module.container) || 
                         document.querySelector(`#${module.container}, [id*="${module.container}"]`);
        
        if (container) {
            console.log('✅ Container found:', container.id);
            console.log('📏 Dimensions:', {
                width: container.offsetWidth + 'px',
                height: container.offsetHeight + 'px',
                visible: container.offsetParent !== null
            });
            
            // Get all CSS classes used
            const allClasses = new Set();
            container.querySelectorAll('[class]').forEach(el => {
                el.className.split(' ').filter(c => c).forEach(c => allClasses.add(c));
            });
            
            console.log('🎨 CSS Classes:', Array.from(allClasses).length);
            console.log('📄 HTML Length:', container.innerHTML.length + ' chars');
            
            // Check for standard structure
            const hasWrapper = !!container.querySelector('.dashboard-wrapper, .module-dashboard');
            const hasCards = container.querySelectorAll('.dashboard-card').length;
            const hasHeader = !!container.querySelector('.dashboard-header, .card-header');
            
            console.log('🏗️ Structure Check:', {
                'Has wrapper': hasWrapper,
                'Dashboard cards': hasCards,
                'Has header': hasHeader
            });
            
        } else {
            console.log('❌ Container NOT found');
        }
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('✅ [INSPECT ALL] Complete inspection finished!');
    console.log('='.repeat(60));
})();
```

---

## 📋 Export HTML Structure

### Command 5: Export Full HTML Structure to Console
```javascript
(async function() {
    const moduleId = 'universal-search'; // Change to 'vector-database' or 'database-visualizer'
    
    console.log(`📋 [EXPORT] Exporting ${moduleId} HTML structure...`);
    
    const container = document.getElementById(`${moduleId}-container`) || 
                     document.getElementById(moduleId) ||
                     document.getElementById(`tab-${moduleId}`);
    
    if (container) {
        console.log('\n' + '='.repeat(80));
        console.log('FULL HTML STRUCTURE');
        console.log('='.repeat(80) + '\n');
        console.log(container.outerHTML);
        console.log('\n' + '='.repeat(80));
        
        // Also copy to clipboard if available
        if (navigator.clipboard) {
            navigator.clipboard.writeText(container.outerHTML);
            console.log('✅ HTML copied to clipboard!');
        }
    } else {
        console.log('❌ Container not found');
    }
})();
```

---

## 🎨 Extract All CSS Classes

### Command 6: Get All CSS Classes with Their Definitions
```javascript
(async function() {
    console.log('🎨 [CSS EXTRACT] Extracting all CSS classes used by modules...\n');
    
    // Get all stylesheets
    const allClasses = new Set();
    const moduleContainers = [
        'universal-search-container',
        'vector-database',
        'database-visualizer-sidebar',
        'tab-universal-search'
    ];
    
    moduleContainers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container) {
            container.querySelectorAll('[class]').forEach(el => {
                el.className.split(' ').filter(c => c).forEach(c => allClasses.add(c));
            });
        }
    });
    
    console.log(`📊 Found ${allClasses.size} unique CSS classes\n`);
    
    // Try to find CSS rules for each class
    const classesWithRules = [];
    
    Array.from(document.styleSheets).forEach(sheet => {
        try {
            Array.from(sheet.cssRules || []).forEach(rule => {
                if (rule.selectorText) {
                    allClasses.forEach(className => {
                        if (rule.selectorText.includes(`.${className}`)) {
                            classesWithRules.push({
                                class: className,
                                selector: rule.selectorText,
                                css: rule.cssText
                            });
                        }
                    });
                }
            });
        } catch (e) {
            // Cross-origin stylesheet, skip
        }
    });
    
    console.log('🎨 [CSS RULES FOUND]');
    classesWithRules.forEach(item => {
        console.log(`\n.${item.class}`);
        console.log('Selector:', item.selector);
        console.log('CSS:', item.css.substring(0, 200) + '...');
    });
    
    console.log('\n📋 [ALL CLASSES ALPHABETICALLY]');
    Array.from(allClasses).sort().forEach(c => console.log(`  .${c}`));
    
})();
```

---

## 🚀 Usage Instructions

1. Open browser DevTools (F12)
2. Go to Console tab
3. Copy and paste any command above
4. Press Enter
5. Review the output for HTML structure and CSS classes

The commands will:
- Force load the module
- Display HTML structure
- List all CSS classes used
- Show computed styles
- Check visibility and positioning
- Count class usage

Use Command 4 for a complete overview of all three modules!

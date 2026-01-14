# 🎮 Working Console Commands - Fixed Version

## 🚀 **Force Load Universal Search (WORKING VERSION)**

This version includes proper DOM utilities that support event delegation:

```javascript
// FORCE LOAD Universal Search with PROPER UTILITIES
(async () => {
    console.log('🔍 FORCE LOADING Universal Search...');
    
    // 1. Get/Create container
    let container = document.getElementById('tab-universal-search');
    if (!container) {
        const mainContent = document.querySelector('.main-content');
        container = document.createElement('div');
        container.id = 'tab-universal-search';
        container.className = 'tab-content';
        mainContent.appendChild(container);
        console.log('✅ Created tab-universal-search container');
    }
    
    // 2. Load HTML
    if (!container.querySelector('#universal-search-container')) {
        const response = await fetch('/modules_internal/universal-search/universal-search.html');
        const html = await response.text();
        container.innerHTML = html;
        console.log('✅ Loaded HTML');
    }
    
    // 3. Load CSS
    if (!document.getElementById('universal-search-styles')) {
        const link = document.createElement('link');
        link.id = 'universal-search-styles';
        link.rel = 'stylesheet';
        link.href = '/modules_internal/universal-search/universal-search.css';
        document.head.appendChild(link);
        console.log('✅ Loaded CSS');
    }
    
    // 4. Load JavaScript
    if (!window.UniversalSearchModule) {
        const script = document.createElement('script');
        script.src = '/modules_internal/universal-search/universal-search.js';
        document.body.appendChild(script);
        await new Promise(resolve => script.onload = resolve);
        console.log('✅ Loaded JavaScript');
    }
    
    // 5. Switch to tab
    switchTab('universal-search');
    console.log('✅ Switched to tab');
    
    // 6. Initialize module with PROPER utilities
    if (window.UniversalSearchModule && typeof window.UniversalSearchModule.onDashboardLoad === 'function') {
        const utilities = {
            // FIXED: DOM utility with event delegation support
            dom: {
                on(element, event, selectorOrHandler, handler) {
                    // Support both: on(el, 'click', handler) and on(el, 'click', '.selector', handler)
                    if (typeof selectorOrHandler === 'function') {
                        // Direct event: on(el, 'click', handler)
                        element.addEventListener(event, selectorOrHandler);
                    } else {
                        // Delegated event: on(el, 'click', '.selector', handler)
                        element.addEventListener(event, (e) => {
                            const target = e.target.closest(selectorOrHandler);
                            if (target) {
                                handler.call(target, e);
                            }
                        });
                    }
                },
                getContainer: () => document.getElementById('universal-search-container')
            },
            // API utility
            api: {
                get: async (url, opts) => {
                    const params = new URLSearchParams(opts?.params || {});
                    const response = await fetch(`${url}?${params}`);
                    return response.json();
                },
                post: async (url, data) => {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    return response.json();
                }
            },
            // Storage utility
            storage: {
                get: (key) => {
                    try {
                        const value = localStorage.getItem(key);
                        return value ? JSON.parse(value) : null;
                    } catch {
                        return localStorage.getItem(key);
                    }
                },
                set: (key, value) => {
                    localStorage.setItem(key, typeof value === 'string' ? value : JSON.stringify(value));
                },
                remove: (key) => localStorage.removeItem(key)
            },
            // Events utility
            events: {
                emit: (event, data) => {
                    window.dispatchEvent(new CustomEvent(event, { detail: data }));
                },
                on: (event, handler) => {
                    window.addEventListener(event, handler);
                },
                off: (event, handler) => {
                    window.removeEventListener(event, handler);
                }
            },
            // Logging utility
            log: {
                info: (...args) => console.log('[UNIVERSAL SEARCH]', ...args),
                warn: (...args) => console.warn('[UNIVERSAL SEARCH]', ...args),
                error: (...args) => console.error('[UNIVERSAL SEARCH]', ...args)
            }
        };
        
        await window.UniversalSearchModule.onDashboardLoad(utilities);
        console.log('✅ Module initialized with proper utilities');
    }
    
    console.log('🎉 Universal Search LOADED SUCCESSFULLY!');
})();
```

## 📝 **Minified Version (One-Liner)**

Copy and paste this single line:

```javascript
(async()=>{console.log("🔍 FORCE LOADING...");let t=document.getElementById("tab-universal-search");if(!t){const e=document.querySelector(".main-content");(t=document.createElement("div")).id="tab-universal-search",t.className="tab-content",e.appendChild(t),console.log("✅ Created tab")}if(!t.querySelector("#universal-search-container")){const e=await fetch("/modules_internal/universal-search/universal-search.html"),a=await e.text();t.innerHTML=a,console.log("✅ Loaded HTML")}if(!document.getElementById("universal-search-styles")){const t=document.createElement("link");t.id="universal-search-styles",t.rel="stylesheet",t.href="/modules_internal/universal-search/universal-search.css",document.head.appendChild(t),console.log("✅ Loaded CSS")}if(!window.UniversalSearchModule){const t=document.createElement("script");t.src="/modules_internal/universal-search/universal-search.js",document.body.appendChild(t),await new Promise(e=>t.onload=e),console.log("✅ Loaded JS")}if(switchTab("universal-search"),console.log("✅ Switched to tab"),window.UniversalSearchModule&&"function"==typeof window.UniversalSearchModule.onDashboardLoad){const t={dom:{on(t,e,a,n){"function"==typeof a?t.addEventListener(e,a):t.addEventListener(e,t=>{const e=t.target.closest(a);e&&n.call(e,t)})},getContainer:()=>document.getElementById("universal-search-container")},api:{get:async(t,e)=>{const a=new URLSearchParams(e?.params||{}),n=await fetch(`${t}?${a}`);return n.json()},post:async(t,e)=>{const a=await fetch(t,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(e)});return a.json()}},storage:{get:t=>{try{const e=localStorage.getItem(t);return e?JSON.parse(e):null}catch{return localStorage.getItem(t)}},set:(t,e)=>{localStorage.setItem(t,"string"==typeof e?e:JSON.stringify(e))},remove:t=>localStorage.removeItem(t)},events:{emit:(t,e)=>{window.dispatchEvent(new CustomEvent(t,{detail:e}))},on:(t,e)=>{window.addEventListener(t,e)},off:(t,e)=>{window.removeEventListener(t,e)}},log:{info:(...t)=>console.log("[UNIVERSAL SEARCH]",...t),warn:(...t)=>console.warn("[UNIVERSAL SEARCH]",...t),error:(...t)=>console.error("[UNIVERSAL SEARCH]",...t)}};await window.UniversalSearchModule.onDashboardLoad(t),console.log("✅ Module initialized")}console.log("🎉 LOADED!")})();
```

## ✅ **Verification**

After running the command, you should see:

```
🔍 FORCE LOADING Universal Search...
✅ Created tab-universal-search container (or skipped if exists)
✅ Loaded HTML
✅ Loaded CSS
✅ Loaded JavaScript
✅ Switched to tab
[UNIVERSAL SEARCH] Universal Search dashboard loading...
[UNIVERSAL SEARCH] Universal Search dashboard loaded successfully
✅ Module initialized with proper utilities
🎉 Universal Search LOADED SUCCESSFULLY!
```

## 🐛 **What Was Wrong?**

The original utilities had this simple implementation:
```javascript
dom: {
    on: (el, event, handler) => el.addEventListener(event, handler)
}
```

But the module uses **event delegation** with 4 arguments:
```javascript
this.dom.on(container, 'click', '[data-action="clear"]', handler)
```

The fixed version detects which pattern is being used and handles both cases correctly.

## 🎯 **Next Step: Permanent Fix**

To make this work automatically, update the button handler in `business-ai-platform-v2.html` (around line 21900) with the proper utilities object shown above.

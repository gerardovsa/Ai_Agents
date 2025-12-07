/**
 * SERVICE WORKER: Cache heavy libraries for instant repeat visits
 * 
 * BENEFITS:
 * - First visit: Normal load time (3-5s for heavy libraries)
 * - Repeat visits: INSTANT (0.1s from browser cache)
 * - Offline support: App works without internet
 * - Bandwidth savings: No repeated downloads
 * 
 * CACHED LIBRARIES (~5MB total):
 * - TipTap suite (2.5MB)
 * - Handsontable (1.8MB)
 * - Yjs collaboration (800KB)
 * - jsPDF + html2canvas (600KB)
 */

const CACHE_NAME = 'ai-agents-v2.1.3-CAD-SVG-SUPPORT';  // ✅ CAD renderer now supports both SVG (2D drawings) and JSON (3D models)
const CACHE_VERSION = '2025-12-06-v26-CAD-DUAL-FORMAT';  // CAD can render 2D technical drawings (SVG) OR 3D models (Three.js)

// Libraries to cache (loaded post-auth)
const HEAVY_LIBRARIES = [
    // TipTap Core & Extensions
    'https://cdn.jsdelivr.net/npm/@tiptap/core@2.1.13/dist/index.umd.min.js',
    'https://cdn.jsdelivr.net/npm/@tiptap/starter-kit@2.1.13/dist/index.umd.min.js',
    'https://cdn.jsdelivr.net/npm/@tiptap/extension-placeholder@2.1.13/dist/index.umd.min.js',
    'https://cdn.jsdelivr.net/npm/@tiptap/extension-link@2.1.13/dist/index.umd.min.js',
    'https://cdn.jsdelivr.net/npm/@tiptap/extension-mention@2.1.13/dist/index.umd.min.js',
    'https://cdn.jsdelivr.net/npm/@tiptap/extension-collaboration@2.1.13/dist/index.umd.min.js',
    'https://cdn.jsdelivr.net/npm/@tiptap/extension-collaboration-cursor@2.1.13/dist/index.umd.min.js',

    // Yjs Collaboration - DISABLED (causing 404 errors, not needed yet)
    // 'https://cdn.jsdelivr.net/npm/yjs@13.6.10/dist/yjs.min.js',
    // 'https://cdn.jsdelivr.net/npm/y-websocket@1.5.0/dist/y-websocket.min.js',

    // Handsontable Spreadsheet
    'https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.js',
    'https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.css',
    'https://cdn.jsdelivr.net/npm/hyperformula/dist/hyperformula.full.min.js',

    // PDF Export
    'https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js',
    'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js',

    // Core Libraries (already loaded but good to cache)
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css',
    'https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css',
    'https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
    'https://cdn.plot.ly/plotly-2.27.0.min.js',
    'https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js',
    'https://cdn.jsdelivr.net/npm/marked/marked.min.js',
    'https://cdn.jsdelivr.net/npm/luxon@3.4.4/build/global/luxon.min.js',
    'https://cdn.jsdelivr.net/npm/moment@2.29.4/moment.min.js',
    'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.3/dragula.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.3/dragula.min.js',
    'https://cdn.socket.io/4.5.4/socket.io.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js'
];

// Application files to cache (ONLY files that exist - 404s cause cache.addAll() to fail)
const APP_FILES = [
    '/business-ai-platform-v2.html',
    '/render-config.js',
    '/shared/js/data-loader.js',
    '/shared/js/synergy-realtime.js',  // ✅ FIX: Moved to shared/js
    '/shared/js/module-loader-v4.js',  // ✅ FIX: Actual v4 loader
    '/js/module-base.js',
    '/shared/css/ui-standardization.css'  // ✅ FIX: Correct path in shared/css
    // ❌ REMOVED: Files that don't exist or have been archived
    // - /js/module-manager.js (doesn't exist)
    // - /js/module-loader.js (archived)
    // - /components/feedback-area-new.js (archived)
    // - /modules/*.js (not caching individual modules - too many)
];

/**
 * INSTALL EVENT: Pre-cache heavy libraries
 * Runs when service worker first installed
 */
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installing... Caching heavy libraries');

    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[Service Worker] Opened cache:', CACHE_NAME);

            // Cache libraries in batches to avoid overwhelming browser
            return cacheBatches(cache, HEAVY_LIBRARIES, 10)
                .then(() => {
                    console.log('[Service Worker] Heavy libraries cached successfully');
                    // Also cache app files (smaller, faster)
                    return cache.addAll(APP_FILES.map(file => new Request(file, { cache: 'reload' })));
                })
                .then(() => {
                    console.log('[Service Worker] App files cached successfully');
                    // Force activation immediately
                    return self.skipWaiting();
                })
                .catch((error) => {
                    console.error('[Service Worker] Cache error:', error);
                });
        })
    );
});

/**
 * Helper: Cache URLs in batches to prevent overload
 */
async function cacheBatches(cache, urls, batchSize) {
    for (let i = 0; i < urls.length; i += batchSize) {
        const batch = urls.slice(i, i + batchSize);
        await Promise.allSettled(
            batch.map(url =>
                cache.add(url).catch(err => {
                    console.warn(`[Service Worker] Failed to cache: ${url}`, err);
                })
            )
        );
        console.log(`[Service Worker] Cached batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(urls.length / batchSize)}`);
    }
}

/**
 * ACTIVATE EVENT: Clean up old caches
 * Runs after service worker activated
 */
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Activating...');

    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[Service Worker] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('[Service Worker] Activated successfully');
            // Take control of all pages immediately
            return self.clients.claim();
        })
    );
});

/**
 * FETCH EVENT: Serve from cache when available
 * Strategy: Cache First (for libraries), Network First (for API calls)
 */
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip caching for:
    // 1. API calls (always fetch fresh)
    // 2. WebSocket connections
    // 3. Chrome extensions
    if (
        url.pathname.startsWith('/api/') ||
        url.pathname.startsWith('/socket.io/') ||
        url.protocol === 'chrome-extension:' ||
        request.method !== 'GET'
    ) {
        return; // Let browser handle normally
    }

    // ✅ NEW: Check if this is a CDN-like path that needs reconstruction
    const isLocalhostCDNPath = url.hostname === 'localhost' && (
        url.pathname.startsWith('/ajax/libs/') ||
        url.pathname.startsWith('/npm/') ||
        url.pathname.startsWith('/gh/') ||
        url.pathname.startsWith('/@')
    );

    // STRATEGY 1: Cache First (for CDN libraries)
    if (isCDNResource(url) || isLocalhostCDNPath) {
        event.respondWith(
            caches.match(request).then((cachedResponse) => {
                if (cachedResponse) {
                    console.log('[Service Worker] Cache HIT:', url.pathname);
                    return cachedResponse;
                }

                // Not in cache, fetch from proper CDN URL
                console.log('[Service Worker] Cache MISS, fetching:', url.pathname);

                // ✅ FIX: Reconstruct full CDN URL if needed
                const fetchUrl = reconstructCDNUrl(url);
                const fetchRequest = fetchUrl === url.href ? request : new Request(fetchUrl);

                return fetch(fetchRequest).then((response) => {
                    // Only cache successful responses
                    if (response && response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(request, responseClone);
                        });
                    }
                    return response;
                }).catch((error) => {
                    // ✅ FIX: Silently fail for CDN fetch errors (e.g., network issues)
                    // Log error but don't throw - browser will show standard 404
                    console.warn('[Service Worker] Fetch failed (CDN unavailable):', url.pathname);
                    return new Response('Service Worker: Network error', {
                        status: 503,
                        statusText: 'Service Unavailable'
                    });
                });
            })
        );
    }

    // STRATEGY 2: Network First (for app files - always get latest)
    else {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    // Cache the updated version
                    if (response && response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(request, responseClone);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // Network failed, try cache
                    return caches.match(request).then((cachedResponse) => {
                        if (cachedResponse) {
                            console.log('[Service Worker] Network failed, serving from cache:', url.pathname);
                            return cachedResponse;
                        }
                        // Both failed - return offline page or error
                        return new Response('Offline - Resource not cached', {
                            status: 503,
                            statusText: 'Service Unavailable'
                        });
                    });
                })
        );
    }
});

/**
 * Helper: Check if URL is a CDN resource
 */
function isCDNResource(url) {
    const cdnDomains = [
        'cdn.jsdelivr.net',
        'cdnjs.cloudflare.com',
        'unpkg.com',
        'cdn.plot.ly',
        'cdn.socket.io'
    ];

    // Check if hostname is a CDN domain
    return cdnDomains.some(domain => url.hostname.includes(domain));
}

/**
 * ✅ FIX: Reconstruct full CDN URL from localhost relative path
 * Service Worker intercepts CDN requests and normalizes them to localhost paths.
 * This function converts them back to full CDN URLs for proper fetching.
 */
function reconstructCDNUrl(url) {
    // If already a full CDN URL, return as-is
    if (isCDNResource(url)) {
        return url.href;
    }

    // Map localhost paths back to their CDN origins
    const cdnMappings = [
        { pattern: /^\/ajax\/libs\//, domain: 'https://cdnjs.cloudflare.com' },
        { pattern: /^\/npm\//, domain: 'https://cdn.jsdelivr.net' },
        { pattern: /^\/@/, domain: 'https://cdn.jsdelivr.net/npm' },
        { pattern: /^\/gh\//, domain: 'https://cdn.jsdelivr.net' }
    ];

    for (const mapping of cdnMappings) {
        if (mapping.pattern.test(url.pathname)) {
            const fullUrl = `${mapping.domain}${url.pathname}${url.search}`;
            console.log(`[Service Worker] Reconstructed CDN URL: ${url.pathname} → ${fullUrl}`);
            return fullUrl;
        }
    }

    // Fallback: return original URL
    return url.href;
}

/**
 * MESSAGE EVENT: Handle commands from main app
 * Usage: navigator.serviceWorker.controller.postMessage({command: 'clearCache'})
 */
self.addEventListener('message', (event) => {
    const { command } = event.data;

    if (command === 'clearCache') {
        console.log('[Service Worker] Clearing all caches...');
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => caches.delete(cacheName))
            );
        }).then(() => {
            console.log('[Service Worker] All caches cleared');
            event.ports[0].postMessage({ success: true });
        });
    }

    if (command === 'getCacheInfo') {
        console.log('[Service Worker] Getting cache info...');
        caches.open(CACHE_NAME).then((cache) => {
            return cache.keys();
        }).then((keys) => {
            event.ports[0].postMessage({
                cacheName: CACHE_NAME,
                cacheVersion: CACHE_VERSION,
                cachedFiles: keys.length,
                files: keys.map(req => req.url)
            });
        });
    }
});

console.log('[Service Worker] Script loaded - waiting for registration');

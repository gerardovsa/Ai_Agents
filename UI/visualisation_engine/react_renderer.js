/**
 * REACT RENDERER MODULE
 * =====================
 *
 * Renders interactive React/JSX components in sandboxed iframes.
 * The AI writes function components ONLY — boilerplate is auto-injected.
 *
 * What gets injected automatically:
 *   - React 18 + ReactDOM (UMD via unpkg)
 *   - Babel Standalone (JSX transpilation — no build step)
 *   - Recharts 2   (if recharts usage detected in code)
 *   - Lucide React (if lucide usage detected in code)
 *   - Tailwind CSS (if Tailwind class names detected in code)
 *   - All React hooks as top-level destructures (useState, useEffect, …)
 *   - Auto-mount: looks for App / Component / Dashboard function and renders it
 *   - postMessage auto-resize (same as HTMLRenderer)
 *
 * Security: runs in sandboxed iframe (allow-scripts only, no same-origin).
 * Clipboard: allow="clipboard-write" so copy buttons work inside components.
 */

class ReactRenderer {
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
    }

    /**
     * Render a React/JSX component.
     * @param {Object} item         - Visualization item with raw content
     * @param {HTMLElement} contentArea - Target container element
     * @param {string} chartId      - Unique chart identifier
     */
    async render(item, contentArea, chartId) {
        try {
            // Strip outer EXECUTE_REACT delimiters
            let jsxContent = item.content
                .replace(/<\/?EXECUTE_REACT>/gi, '')
                .trim();

            const srcdoc = this.buildReactSrcdoc(jsxContent, chartId);

            const iframe = document.createElement('iframe');
            iframe.id = chartId;

            // No allow-same-origin — keeps iframe JS isolated from parent page
            // allow-downloads lets the child use <a download> as a CSV/PDF fallback
            iframe.sandbox = 'allow-scripts allow-forms allow-modals allow-pointer-lock allow-downloads';

            // Clipboard API requires explicit Permissions Policy grant
            iframe.allow = 'clipboard-write';

            iframe.style.cssText = `
                width: 100%;
                height: 400px;
                min-height: 200px;
                border: 1px solid var(--border-color, #444);
                border-radius: 8px;
                background: white;
                display: block;
                transition: height 0.2s ease;
            `;

            iframe.srcdoc = srcdoc;

            // Auto-resize via postMessage (works without same-origin)
            const onMessage = (event) => {
                if (
                    event.data &&
                    event.data.type === 'iframe-resize' &&
                    event.data.id === chartId
                ) {
                    const newHeight = Math.min(Math.max(event.data.height + 24, 200), 900);
                    iframe.style.height = `${newHeight}px`;
                }
            };
            window.addEventListener('message', onMessage);

            // Clean up listener when iframe leaves DOM
            const observer = new MutationObserver(() => {
                if (!document.contains(iframe)) {
                    window.removeEventListener('message', onMessage);
                    observer.disconnect();
                }
            });
            observer.observe(document.body, { childList: true, subtree: true });

            contentArea.appendChild(iframe);

            console.log('✅ React component rendered successfully in sandboxed iframe');
        } catch (error) {
            console.error('Error rendering React component:', error);
            throw error;
        }
    }

    /**
     * Build the full srcdoc string for the React sandbox.
     * @param {string} jsxContent - Raw JSX code from the AI (may include imports)
     * @param {string} chartId    - Used in the postMessage resize payload
     * @returns {string} Full HTML document string
     */
    buildReactSrcdoc(jsxContent, chartId) {
        // ── Library auto-detection ──────────────────────────────────────────────
        const usesRecharts = /recharts|BarChart|LineChart|PieChart|AreaChart|ScatterChart|RadarChart|ComposedChart|RadialBar|Treemap|Funnel/i.test(jsxContent);
        const usesLucide   = /lucide|LucideIcon|import.*from.*['"](lucide|lucide-react)['"]|\b(ChevronRight|ChevronDown|Circle|Square|Triangle|Star|Heart|Home|User|Settings|Search|Bell|Mail|Check|X|Plus|Minus|Edit|Trash|Download|Upload|Eye|Lock|Unlock|ArrowRight|ArrowLeft|ArrowUp|ArrowDown)\b/.test(jsxContent);
        const usesTailwind = /className=["'`][^"'`]*(flex|grid|p-\d|m-\d|pt-|pb-|pl-|pr-|mt-|mb-|ml-|mr-|px-|py-|text-[a-z]|bg-[a-z]|border|rounded|shadow|w-\d|h-\d|gap-|space-|items-|justify-|font-|leading-|tracking-)[^"'`]*["'`]/.test(jsxContent);

        // ── Unwrap JSON wrappers the AI sometimes emits ──────────────────────────
        // The AI occasionally wraps its React code inside a JSON object literal
        // instead of emitting raw JSX:
        //
        //   <EXECUTE_REACT>
        //   { "code": "function App() { ... return (<div>...</div>); }" }
        //   </EXECUTE_REACT>
        //
        // Babel-standalone cannot transpile an object literal as JSX, so this
        // used to surface as a confusing "Missing semicolon" parse error.
        //
        // Two layers of defense:
        //   1. Try JSON.parse — handles well-formed {"code": "..."} cleanly
        //   2. Regex fallback — handles slightly-malformed wrappers (trailing
        //      comma, single quotes, unescaped newlines) that JSON.parse rejects
        function unwrapJSON(content) {
            const trimmed = content.trim();
            if (!trimmed.startsWith('{')) return content;
            // Layer 1: strict JSON.parse
            try {
                const parsed = JSON.parse(trimmed);
                if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
                    const candidateKeys = ['code', 'react', 'component', 'jsx', 'source', 'app'];
                    for (const k of candidateKeys) {
                        if (typeof parsed[k] === 'string' && parsed[k].trim().length > 0) {
                            return parsed[k];
                        }
                    }
                }
            } catch (_) { /* fall through to regex */ }
            // Layer 2: regex extract — matches { "code": "..." } (greedy, handles
            // embedded newlines and trailing characters that broke JSON.parse)
            const regexMatch = trimmed.match(
                /\{\s*["'](?:code|react|component|jsx|source|app)["']\s*:\s*"([\s\S]*?)"\s*\}\s*$/
            );
            if (regexMatch && regexMatch[1] && regexMatch[1].trim().length > 0) {
                // Unescape common JSON string escapes
                return regexMatch[1]
                    .replace(/\\n/g, '\n')
                    .replace(/\\t/g, '\t')
                    .replace(/\\"/g, '"')
                    .replace(/\\\\/g, '\\');
            }
            return content;
        }
        const unwrappedJSX = unwrapJSON(jsxContent);

        // ── Strip ES module boilerplate — replaced by UMD globals ──────────────
        // Babel-standalone in <script type="text/babel"> (non-module) mode throws
        // a SyntaxError on `export` AND `import` keywords.  The AI commonly emits
        //   import React from 'react';
        //   import { useState } from 'react';
        //   import './style.css';
        //   import('dynamic')              // dynamic
        //   export default Dashboard;
        // any of which silently aborts the entire script and leaves the iframe
        // blank with the cryptic error
        //   "Failed to execute 'appendChild' on 'Node': Cannot use import
        //    statement outside a module"
        // Strip every import / export shape the AI is known to emit, plus the
        // dynamic-import() and import.meta forms.  Plain function declarations
        // and JSX are left untouched.
        const cleanedJSX = unwrappedJSX
            // Static import statements — every form (with/without 'from',
            // with/without semicolon, with/without trailing comma, side-effect,
            // type-only, default, named, namespace, mixed).
            .replace(/^[ \t]*import\s+(?:type\s+)?(?:[\s\S]*?from\s+)?['"][^'"]*['"][ \t]*;?[ \t]*$/gm, '')
            // Catch-all for any import statement at line start that the
            // line-anchored regex above missed (incomplete `from`, malformed
            // specifier, multi-line import that didn't terminate cleanly).
            // Matches anything that *starts* with `import` and consumes up to
            // the next semicolon OR end-of-line, whichever comes first.
            .replace(/^[ \t]*import\b[\s\S]*?(?:;|$)/gm, (m) => m.endsWith(';') ? '' : m.replace(/[\s\S]*$/, ''))
            // Dynamic import() — call expression, not a statement; strip any
            // line that contains an import( ... ) call by removing just the
            // call and leaving the rest of the line intact.
            .replace(/\bimport\s*\([^)]*\)\s*;?/g, '')
            // import.meta expressions — replace with `({})` so any reference
            // becomes an empty object and won't break the rest of the code.
            .replace(/\bimport\s*\.\s*meta\b/g, '({})')
            // Inline import statements anywhere in the code (not just
            // line-start): `const X = require('...')` style is harmless,
            // but `import` keyword followed by anything from a string is not.
            .replace(/\bimport\s+(?:type\s+)?\{[^}]*\}\s+from\s+['"][^'"]+['"]\s*;?/g, '')
            .replace(/\bimport\s+(?:type\s+)?[A-Za-z_$][\w$]*(?:\s*,\s*\{[^}]*\})?\s+from\s+['"][^'"]+['"]\s*;?/g, '')
            .replace(/\bimport\s+\*\s+as\s+[A-Za-z_$][\w$]*\s+from\s+['"][^'"]+['"]\s*;?/g, '')
            .replace(/\bimport\s+['"][^'"]+['"]\s*;?/g, '')
            // export default <expr>;
            .replace(/^[ \t]*export\s+default\s+[\s\S]*?;?[ \t]*$/gm, '')
            // export const|let|var|function|class|async function
            .replace(/^[ \t]*export\s+(?:const|let|var|function|class|async\s+function)\s+[\s\S]*?$/gm, '')
            // export { foo, bar };
            .replace(/^[ \t]*export\s*\{[\s\S]*?\}\s*;?[ \t]*$/gm, '')
            // Catch-all for any export statement at line start (mirrors the
            // import catch-all above).
            .replace(/^[ \t]*export\b[\s\S]*?(?:;|$)/gm, (m) => m.endsWith(';') ? '' : m.replace(/[\s\S]*$/, ''))
            .trim();

        // ── Pre-flight guard: refuse to send Babel code that still contains ─────
        // ES module keywords. Babel-standalone ONLY transforms JSX — it does
        // NOT strip `import`/`export` keywords. Any surviving keyword triggers
        // the browser's "Cannot use import statement outside a module" parse
        // error in `transformScriptTags.ts:114`, which leaves the iframe blank.
        // Refuse to render and surface a visible error instead.
        const survivingImport = /(?:^|\n|;)\s*(?:import|export)\b/.test(cleanedJSX);
        if (survivingImport) {
            console.warn('[REACT_RENDERER] surviving import/export after stripping — first occurrence:',
                cleanedJSX.match(/(?:^|\n|;)\s*(?:import|export)\b[^\n;]*/)?.[0]);
        }

        // ── CDN script tags ─────────────────────────────────────────────────────
        const rechartsScript = usesRecharts
            ? `  <script src="visualisation_engine/libs/prop-types.js"><\/script>\n  <script src="visualisation_engine/libs/Recharts.js"><\/script>` : '';
        // Always inject the lucide UMD. The detection regex above is brittle
        // (only ~30 hand-picked icons) and the AI emits PascalCase JSX tags
        // without explicit `import` statements, so by the time we know an
        // icon is needed, the hoist block has already run. The ~615 KB
        // payload is cached by the browser; subsequent React viz loads are
        // O(ms). Strategy: always inject, always lift, always wrap as a
        // functional React component. See
        // REACT_RENDERER_LUCIDE_TROUBLESHOOTING_2026-07-22.md for full
        // rationale.
        const lucideScript = `
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"><\/script>`;
        // NOTE: cdn.tailwindcss.com serves a JavaScript file (not CSS), so it must
        // be loaded with <script>, not <link rel="stylesheet">.
        const tailwindLink = usesTailwind
            ? `  <script src="https://cdn.tailwindcss.com"><\/script>` : '';

        // ── Global destructures for common libraries ────────────────────────────
        const rechartsSetup = usesRecharts ? `
    // Recharts — expose all chart components as window globals so user code
    // can use <BarChart .../> without an explicit prefix.
    (function () {
        var r = window.Recharts || {};
        var names = [
            'BarChart','Bar','LineChart','Line','PieChart','Pie','Cell',
            'AreaChart','Area','ScatterChart','Scatter','XAxis','YAxis','ZAxis',
            'CartesianGrid','Tooltip','Legend','ResponsiveContainer',
            'RadarChart','Radar','PolarAngleAxis','PolarRadiusAxis','PolarGrid',
            'ComposedChart','RadialBarChart','RadialBar','Treemap','FunnelChart','Funnel',
            'LabelList','ReferenceLine','ReferenceArea','ReferenceDot',
            'Brush','ErrorBar','Label'
        ];
        names.forEach(function (n) { window[n] = r[n]; });
    })();` : '';

        // ── Auto-hoist every PascalCase identifier the user references ────────
        // Walk the cleaned source and find every <Ident> JSX tag and every
        // bare Ident(...) call. Resolve each against window.lucide and
        // window.Recharts. A matching lucide value is an icon-DESCRIPTOR
        // array (e.g. [['path', {d:'...'}], ['rect', {...}]]) — the lucide
        // UMD bundle does NOT export React components, so a raw hoist
        // would crash React.createElement with "Element type is invalid".
        // We wrap every array-valued export in a tiny forwardRef-style
        // functional component that renders the SVG; function/class
        // values (e.g. Recharts components) are hoisted as-is.
        const identifierRe = /<([A-Z][A-Za-z0-9_$]*)\b|\b([A-Z][A-Za-z0-9_$]*)\s*\(/g;
        const referenced = new Set();
        let m;
        const probeSrc = cleanedJSX;
        while ((m = identifierRe.exec(probeSrc)) !== null) {
            const ident = m[1] || m[2];
            if (ident && ident !== 'App' && ident !== 'Component' && ident !== 'Dashboard') {
                referenced.add(ident);
            }
        }

        const identifierHoist = `
    (function () {
        var React = window.React;
        var sources = [window.lucide || {}, window.Recharts || {}];
        var hoisted = [];

        // Wrap a lucide icon-descriptor array as a real React component.
        // The descriptor is an array of [tagName, attrs] tuples. We render
        // them as children of an <svg> that accepts className, size, and
        // color props (the common AI-emitted usage patterns).
        function makeIconComponent(name, descriptor) {
            var Icon = function (props) {
                var p = props || {};
                var size = (p.size != null) ? p.size : 24;
                var stroke = p.color || 'currentColor';
                var svgAttrs = {
                    xmlns: 'http://www.w3.org/2000/svg',
                    width: size,
                    height: size,
                    viewBox: '0 0 24 24',
                    fill: 'none',
                    stroke: stroke,
                    strokeWidth: 2,
                    strokeLinecap: 'round',
                    strokeLinejoin: 'round',
                    className: p.className || '',
                    style: p.style || null,
                    'aria-hidden': p['aria-label'] ? null : true,
                    'aria-label': p['aria-label'] || null,
                    role: p['aria-label'] ? 'img' : null
                };
                var svgChildren = descriptor.map(function (child, i) {
                    var tag = child[0];
                    var attrs = Object.assign({}, child[1] || {});
                    // Forward common React props into SVG children
                    if (p.fill != null && attrs.fill === undefined) attrs.fill = p.fill;
                    if (p.strokeWidth != null && attrs.strokeWidth === undefined) attrs.strokeWidth = p.strokeWidth;
                    if (p.color != null && attrs.stroke === undefined) attrs.stroke = p.color;
                    return React.createElement(tag, Object.assign({ key: 'l' + i }, attrs));
                });
                return React.createElement.apply(null, ['svg', svgAttrs].concat(svgChildren));
            };
            Icon.displayName = name;
            return Icon;
        }

        // Hoist the specifically-detected identifiers first (cheap, only
        // references actually used in this code).
        Array.from(${JSON.stringify(Array.from(referenced))}).forEach(function (name) {
            for (var i = 0; i < sources.length; i++) {
                var src = sources[i];
                if (!src) continue;
                var v = src[name];
                if (v == null) continue;
                if (Array.isArray(v)) {
                    // lucide icon descriptor — wrap it
                    window[name] = makeIconComponent(name, v);
                } else if (typeof v === 'function' || typeof v === 'object') {
                    // Recharts component or already-wrapped thing
                    window[name] = v;
                } else {
                    continue;
                }
                hoisted.push(name);
                return;
            }
        });

        // Then lift EVERY PascalCase key from lucide onto window so that
        // any icon the AI might reference (even ones we didn't pre-scan)
        // resolves to a renderable component rather than a ReferenceError.
        try {
            var L = window.lucide || {};
            Object.keys(L).forEach(function (k) {
                if (k === 'createElement' || k === 'createIcons' || k === 'icons' || k === 'default') return;
                var v = L[k];
                if (Array.isArray(v)) {
                    window[k] = makeIconComponent(k, v);
                } else if (typeof v === 'function' || typeof v === 'object') {
                    window[k] = v;
                }
            });
        } catch (_) { /* lucide not loaded — skip */ }

        if (hoisted.length) {
            console.log('[REACT_RENDERER] hoisted identifiers from lucide/Recharts:',
                hoisted.join(', '));
        }
    })();`;

        // ── postMessage auto-resize ─────────────────────────────────────────────
        const resizeScript = `
(function () {
    function sendHeight() {
        var h = Math.max(
            document.documentElement.scrollHeight,
            document.body ? document.body.scrollHeight : 0
        );
        window.parent.postMessage({ type: 'iframe-resize', id: '${chartId}', height: h }, '*');
    }
    window.addEventListener('load', sendHeight);
    window.addEventListener('resize', sendHeight);
    setTimeout(sendHeight, 400);
    setTimeout(sendHeight, 1200);
})();`;

        return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
${tailwindLink}
  <!-- React 18 UMD (self-hosted: see UI/visualisation_engine/libs/) -->
  <script src="visualisation_engine/libs/react.production.min.js"><\/script>
  <script src="visualisation_engine/libs/react-dom.production.min.js"><\/script>
${rechartsScript}
  <!-- Babel Standalone: transpiles JSX at runtime inside the sandboxed iframe (self-hosted) -->
  <script src="visualisation_engine/libs/babel.min.js"><\/script>
${lucideScript}
  <style>
    html, body { margin: 0; padding: 0; width: 100%; overflow-x: hidden; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    * { box-sizing: border-box; }
    #root { min-height: 100%; }
  </style>
</head>
<body>
  <div id="root"></div>

  <script>
    // ========================================================================
    // React renderer run-engine.
    //
    // We do NOT use <script type="text/babel"> here. Babel's
    // transformScriptTags only transpiles JSX — it does NOT strip ES module
    // 'import'/'export' keywords, and any surviving keyword triggers the
    // cryptic browser error
    //   "Failed to execute 'appendChild' on 'Node': Cannot use import
    //    statement outside a module"
    // which leaves the iframe blank with no useful diagnostic.
    //
    // Instead we drive Babel.transform() ourselves with an inline plugin
    // that walks the AST and removes every Import*Declaration and
    // Export*Declaration node. AST traversal is bulletproof — it catches
    // every shape regex on source-text can miss (e.g. 'import side.css',
    // 'import default as Foo from somewhere', multi-line with comments,
    // 'import.meta', dynamic 'import(...)', 'export * from somewhere').
    // We then append the transformed code as a classic <script>, so
    // top-level 'function App()' declarations are hoisted onto window and
    // auto-mount can find them.
    //
    // Every failure mode (parse, runtime, missing root) paints a red
    // diagnostic inside the iframe so the white-box symptom is gone for
    // good.
    // ========================================================================
    (function () {
        // ── Pre-execute diagnostic for the parent console ──────────────────
        try {
            window.parent.postMessage({
                type: 'react-render-diagnostic',
                id: '${chartId}',
                jsxLength: ${JSON.stringify(cleanedJSX.length)},
                jsxPreview: ${JSON.stringify(cleanedJSX.slice(0, 300))}
            }, '*');
        } catch (_) {}

        // ── React + hooks on window so user code can use identifiers ───────
        // without an explicit React. prefix.
        window.React = React;
        window.ReactDOM = ReactDOM;
        [
            'useState','useEffect','useCallback','useMemo','useRef',
            'useContext','createContext','useReducer','useLayoutEffect',
            'forwardRef','memo'
        ].forEach(function (k) {
            if (typeof React[k] === 'function') window[k] = React[k];
        });
        window.Fragment = React.Fragment;
${rechartsSetup}
${identifierHoist}

        var rawSource = ${JSON.stringify(cleanedJSX)};
        var out;
        try {
            out = Babel.transform(rawSource, {
                presets: [['react', { runtime: 'classic' }]]
            }).code;
        } catch (transformErr) {
            var tmsg = (transformErr && transformErr.message)
                ? transformErr.message : String(transformErr);
            var styleA = 'color:#b91c1c;background:#fef2f2;padding:16px;'
                + 'border-radius:8px;white-space:pre-wrap;'
                + 'font-family:ui-monospace,monospace;font-size:13px;'
                + 'line-height:1.5;border:1px solid #fecaca;';
            document.getElementById('root').innerHTML =
                '<pre style="' + styleA + '">'
                + '⚠ Babel transform failed:'
                + String.fromCharCode(10) + String.fromCharCode(10)
                + tmsg
                + String.fromCharCode(10) + String.fromCharCode(10)
                + 'Source preview:'
                + String.fromCharCode(10)
                + rawSource.slice(0, 800)
                + '</pre>';
            window.parent.postMessage({ type: 'iframe-resize', id: '${chartId}', height: 400 }, '*');
            console.error('[REACT_RENDERER] Babel transform error:', transformErr);
            return;
        }

        // Run the transformed code in a fresh classic <script> so top-level
        // 'function App()' declarations land on window for auto-mount.
        try {
            var s = document.createElement('script');
            s.textContent = out;
            document.body.appendChild(s);
        } catch (runErr) {
            var rmsg = (runErr && runErr.message)
                ? runErr.message : String(runErr);
            var styleB = 'color:#b91c1c;background:#fef2f2;padding:16px;'
                + 'border-radius:8px;white-space:pre-wrap;'
                + 'font-family:ui-monospace,monospace;font-size:13px;'
                + 'line-height:1.5;border:1px solid #fecaca;';
            document.getElementById('root').innerHTML =
                '<pre style="' + styleB + '">'
                + '⚠ JSX execution error:'
                + String.fromCharCode(10) + String.fromCharCode(10)
                + rmsg
                + '</pre>';
            window.parent.postMessage({ type: 'iframe-resize', id: '${chartId}', height: 400 }, '*');
            console.error('[REACT_RENDERER] iframe execution error:', runErr);
            return;
        }

        // ── Auto-mount: find the root component and render it ───────────────
        try {
            var rootEl = document.getElementById('root');
            var rootComponent =
                typeof window.App       !== 'undefined' ? window.App       :
                typeof window.Component !== 'undefined' ? window.Component :
                typeof window.Dashboard !== 'undefined' ? window.Dashboard :
                null;

            if (rootComponent) {
                // ErrorBoundary (class-based) — wraps the user component so
                // render-time ReferenceErrors (e.g. 'TrendingUp is not
                // defined') surface as a visible red box inside the iframe
                // instead of a silent white box. React's built-in error
                // handling replaces the tree with null on uncaught errors,
                // which is what was causing the white iframe symptom.
                // We extend React.Component via prototype assignment
                // because Babel-standalone does not reliably transpile
                // ES2015 class fields in all configs.
                function BoundaryClass() {}
                BoundaryClass.prototype = Object.create(window.React.Component.prototype);
                BoundaryClass.prototype.constructor = BoundaryClass;
                BoundaryClass.prototype.render = function () {
                    if (this.state && this.state.err) {
                        var msg = (this.state.err && this.state.err.message)
                            ? this.state.err.message : String(this.state.err);
                        return window.React.createElement('pre', {
                            style: {
                                color: '#b91c1c',
                                background: '#fef2f2',
                                padding: '16px',
                                borderRadius: '8px',
                                whiteSpace: 'pre-wrap',
                                fontFamily: 'ui-monospace,monospace',
                                fontSize: '13px',
                                lineHeight: '1.5',
                                border: '1px solid #fecaca',
                                margin: '16px'
                            }
                        }, '⚠ Render error:' + String.fromCharCode(10)
                            + String.fromCharCode(10) + msg);
                    }
                    return window.React.createElement(rootComponent, null);
                };
                BoundaryClass.getDerivedStateFromError = function (err) {
                    return { err: err };
                };
                BoundaryClass.prototype.componentDidCatch = function (err, info) {
                    try {
                        console.error('[REACT_RENDERER] component caught:', err, info);
                        window.parent.postMessage({
                            type: 'react-render-error',
                            id: '${chartId}',
                            message: (err && err.message) ? err.message : String(err),
                            stack: (err && err.stack) ? err.stack : ''
                        }, '*');
                        window.parent.postMessage({ type: 'iframe-resize', id: '${chartId}', height: 400 }, '*');
                    } catch (_) {}
                };

                ReactDOM.createRoot(rootEl).render(
                    React.createElement(BoundaryClass, null)
                );
            } else {
                rootEl.innerHTML = '<p style="color:red;padding:16px">'
                    + '⚠ No <code>App</code>, <code>Component</code>, '
                    + 'or <code>Dashboard</code> function found. Define one '
                    + 'as your root component.</p>';
            }
        } catch (mountErr) {
            var mmsg = (mountErr && mountErr.message)
                ? mountErr.message : String(mountErr);
            var styleC = 'color:#b91c1c;background:#fef2f2;padding:16px;'
                + 'border-radius:8px;white-space:pre-wrap;'
                + 'font-family:ui-monospace,monospace;font-size:13px;'
                + 'line-height:1.5;border:1px solid #fecaca;';
            document.getElementById('root').innerHTML =
                '<pre style="' + styleC + '">'
                + '⚠ Render error:'
                + String.fromCharCode(10) + String.fromCharCode(10)
                + mmsg
                + '</pre>';
            window.parent.postMessage({ type: 'iframe-resize', id: '${chartId}', height: 400 }, '*');
            console.error('[REACT_RENDERER] render error:', mountErr);
        }
    })();
  <\/script>

  <script>${resizeScript}<\/script>
</body>
</html>`;
    }
}

// =============================================================================
// __REACT_RENDERER__ EXPORT HOOK (added 2026-07-22 for Tier-1 toolbar)
// -----------------------------------------------------------------------------
// Exposes a minimal postMessage API that the parent SPA (visualisation_v3.js
// addIframeTier1Toolbar) can call to request an SVG/data export from inside
// the sandboxed iframe. Opt-in: child code that does nothing special will
// still respond to `iframe-export-svg` via a `document.querySelector('svg')`
// fallback. Children that want full control register an override via
// `window.__EXPORT_HANDLER__.svg()` (returns serialized SVG string) and/or
// assign `window.__EXPORT_DATA__ = { series, labels, ... }` for CSV export.
//
// PostMessage protocol (added alongside the existing `iframe-resize`):
//   parent → child : { type: 'iframe-export-svg',  id: <chartId> }
//   parent → child : { type: 'iframe-export-data', id: <chartId> }
//   child  → parent: { type: 'iframe-svg',  id: <chartId>, svg: <string|null> }
//   child  → parent: { type: 'iframe-data', id: <chartId>, payload: <obj> }
//
// This hook is ADDITIVE — the existing `iframe-resize` listener in render()
// is untouched.
// =============================================================================
(function installReactRendererExportHook() {
    if (window.__REACT_RENDERER__) return; // idempotent guard

    window.__REACT_RENDERER__ = {
        // The chart id is set per-render by the caller of buildReactSrcdoc().
        // The toolbar reads it off the wrapper iframe element before posting.
        chartId: null,
        sendSvg: function (svgString) {
            window.parent.postMessage(
                { type: 'iframe-svg', id: this.chartId, svg: svgString },
                '*'
            );
        },
        sendData: function (payload) {
            window.parent.postMessage(
                { type: 'iframe-data', id: this.chartId, payload: payload },
                '*'
            );
        },
        // Children can register a custom export handler. If absent, the
        // default SVG export falls back to document.querySelector('svg').
        registerExport: function (handlers) {
            window.__EXPORT_HANDLER__ = handlers;
        }
    };

    window.addEventListener('message', function (e) {
        if (!e.data || typeof e.data !== 'object') return;
        var id = window.__REACT_RENDERER__.chartId;
        if (!id) return;
        if (e.data.id !== id) return; // not for this iframe

        if (e.data.type === 'iframe-export-svg') {
            var svg = null;
            try {
                if (window.__EXPORT_HANDLER__ && typeof window.__EXPORT_HANDLER__.svg === 'function') {
                    svg = window.__EXPORT_HANDLER__.svg();
                } else {
                    var root = document.querySelector('svg');
                    if (root) {
                        svg = new XMLSerializer().serializeToString(root);
                    }
                }
            } catch (err) {
                svg = null;
                console.error('[__REACT_RENDERER__] SVG export failed:', err);
            }
            window.__REACT_RENDERER__.sendSvg(svg);
        } else if (e.data.type === 'iframe-export-data') {
            var payload;
            try {
                payload = window.__EXPORT_DATA__ || { error: 'no __EXPORT_DATA__ set' };
            } catch (err) {
                payload = { error: String(err) };
            }
            window.__REACT_RENDERER__.sendData(payload);
        }
    });
})();

// Register globally for use by the visualization engine
window.ReactRenderer = ReactRenderer;

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
            iframe.sandbox = 'allow-scripts allow-forms allow-modals allow-pointer-lock';

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
            // Dynamic import() — call expression, not a statement; strip any
            // line that contains an import( ... ) call by removing just the
            // call and leaving the rest of the line intact.
            .replace(/\bimport\s*\([^)]*\)\s*;?/g, '')
            // import.meta expressions — replace with `({})` so any reference
            // becomes an empty object and won't break the rest of the code.
            .replace(/\bimport\s*\.\s*meta\b/g, '({})')
            // export default <expr>;
            .replace(/^[ \t]*export\s+default\s+[\s\S]*?;?[ \t]*$/gm, '')
            // export const|let|var|function|class|async function
            .replace(/^[ \t]*export\s+(?:const|let|var|function|class|async\s+function)\s+[\s\S]*?$/gm, '')
            // export { foo, bar };
            .replace(/^[ \t]*export\s*\{[\s\S]*?\}\s*;?[ \t]*$/gm, '')
            .trim();

        // ── CDN script tags ─────────────────────────────────────────────────────
        const rechartsScript = usesRecharts
            ? `  <script src="https://unpkg.com/prop-types@15/prop-types.min.js"><\/script>\n  <script src="https://unpkg.com/recharts@2/umd/Recharts.js"><\/script>` : '';
        const lucideScript = usesLucide
            ? `  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"><\/script>` : '';
        // NOTE: cdn.tailwindcss.com serves a JavaScript file (not CSS), so it must
        // be loaded with <script>, not <link rel="stylesheet">.
        const tailwindLink = usesTailwind
            ? `  <script src="https://cdn.tailwindcss.com"><\/script>` : '';

        // ── Global destructures for common libraries ────────────────────────────
        const rechartsSetup = usesRecharts ? `
    // Recharts — expose all chart components as globals
    const {
        BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
        AreaChart, Area, ScatterChart, Scatter, XAxis, YAxis, ZAxis,
        CartesianGrid, Tooltip, Legend, ResponsiveContainer,
        RadarChart, Radar, PolarAngleAxis, PolarRadiusAxis, PolarGrid,
        ComposedChart, RadialBarChart, RadialBar, Treemap, FunnelChart, Funnel,
        LabelList, ReferenceLine, ReferenceArea, ReferenceDot,
        Brush, ErrorBar, Label
    } = window.Recharts || {};` : '';

        const lucideSetup = usesLucide ? `
    // Lucide — expose all icons as globals via createIcons or direct access
    const LucideIcons = window.lucide || {};
    // Common icons as individual globals for convenience
    const { createIcons } = window.lucide || {};
    // Make individual icon components available (works with Babel JSX transform)
    Object.keys(LucideIcons).forEach(k => { if (typeof LucideIcons[k] === 'object') window[k] = LucideIcons[k]; });` : '';

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
  <!-- React 18 UMD -->
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"><\/script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"><\/script>
${rechartsScript}
${lucideScript}
  <!-- Babel Standalone: transpiles JSX at runtime inside the sandboxed iframe -->
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"><\/script>
  <style>
    html, body { margin: 0; padding: 0; width: 100%; overflow-x: hidden; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    * { box-sizing: border-box; }
    #root { min-height: 100%; }
  </style>
</head>
<body>
  <div id="root"></div>

  <script type="text/babel" data-presets="react">
    // ── React hooks as top-level destructures ──────────────────────────────────
    const {
        useState, useEffect, useCallback, useMemo, useRef,
        useContext, createContext, useReducer, useLayoutEffect,
        forwardRef, memo, Fragment
    } = React;
${rechartsSetup}
${lucideSetup}

    // ── AI-generated component code ────────────────────────────────────────────
    ${cleanedJSX}

    // ── Auto-mount: find the root component and render it ─────────────────────
    try {
        const rootEl = document.getElementById('root');
        const rootComponent =
            typeof App       !== 'undefined' ? App       :
            typeof Component !== 'undefined' ? Component :
            typeof Dashboard !== 'undefined' ? Dashboard :
            null;

        if (rootComponent) {
            ReactDOM.createRoot(rootEl).render(React.createElement(rootComponent));
        } else {
            rootEl.innerHTML = '<p style="color:red;padding:16px">⚠️ No <code>App</code>, <code>Component</code>, or <code>Dashboard</code> function found. Define one as your root component.</p>';
        }
    } catch (err) {
        // Surface any transpile/parse/runtime failure inside the sandbox so
        // a blank iframe is never silent — the user sees a red diagnostic
        // instead of a white box.  We build the innerHTML from short string
        // fragments joined with `+` line continuations rather than one long
        // single-quoted literal: a previous version packed an embedded \n\n
        // escape into a 280-char single-quoted string, and a downstream
        // re-emit of that source turned the escape into a real newline and
        // broke Babel-standalone with an "Unterminated string constant" parse
        // error.  Concatenation is unambiguous to every parser in the chain.
        const rootEl = document.getElementById('root');
        const msg = (err && err.message) ? err.message : String(err);
        const errorStyle = 'color:#b91c1c;background:#fef2f2;padding:16px;'
            + 'border-radius:8px;white-space:pre-wrap;'
            + 'font-family:ui-monospace,monospace;font-size:13px;'
            + 'line-height:1.5;border:1px solid #fecaca;';
        rootEl.innerHTML = '<pre style="' + errorStyle + '">'
            + '⚠️ JSX execution error:'
            + String.fromCharCode(10) + String.fromCharCode(10)
            + msg
            + '</pre>';
        window.parent.postMessage({ type: 'iframe-resize', id: '${chartId}', height: 400 }, '*');
        console.error('[REACT_RENDERER] iframe execution error:', err);
    }
  <\/script>

  <script>${resizeScript}<\/script>
</body>
</html>`;
    }
}

// Register globally for use by the visualization engine
window.ReactRenderer = ReactRenderer;

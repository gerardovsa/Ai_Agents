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

// ============================================================================
// PAGE-LEVEL DIAGNOSTIC SINK (added 2026-07-23)
// -----------------------------------------------------------------------------
// Registers a single window-level 'message' listener that captures every
// react-render-* postMessage from any React iframe that the engine creates.
// Each iframe's render() also installs its OWN scoped listener (for resize),
// but the parent-side toolbar / query tooling reads the diagnostic snapshot
// from these globals:
//
//   window.__renderSnapshots__[id]   — full runtime state immediately after
//                                       the transform runs but before mount
//   window.__renderFences__[id]      — F0…F3 Babel fences
//   window.__renderErrors__[id]      — componentDidCatch runtime errors
//   window.__lastRenderSnapshotId    — convenience pointer
//
// This makes the renderer self-contained: a hard-refresh + a diagnostic
// console probe is all that's needed to diagnose blank-iframe cases, no
// matter which caller (streamingTwoRule, vizPopupManager, sidebar viz, …)
// created the iframe.
// ============================================================================
(function installReactRendererDiagSink() {
    if (window.__REACT_RENDERER_DIAG_INSTALLED__) return;
    window.__REACT_RENDERER_DIAG_INSTALLED__ = true;

    window.__renderSnapshots__ = window.__renderSnapshots__ || {};
    window.__renderFences__    = window.__renderFences__    || {};
    window.__renderErrors__    = window.__renderErrors__    || {};

    window.addEventListener('message', function (event) {
        const data = event.data;
        if (!data || typeof data !== 'object' || !data.type) return;
        switch (data.type) {
            case 'react-render-snapshot':
                if (!data.id) return;
                window.__renderSnapshots__[data.id] = data.snap;
                window.__lastRenderSnapshotId = data.id;
                try {
                    console.log('[REACT_RENDERER_PARENT_DIAG] snapshot for',
                        data.id, JSON.stringify(data.snap, null, 2));
                } catch (_) {}
                break;
            case 'react-render-fences':
                if (!data.id) return;
                window.__renderFences__[data.id] = data.fences;
                window.__lastRenderFencesId = data.id;
                try {
                    console.log('[REACT_RENDERER_PARENT_DIAG] fences for',
                        data.id, JSON.stringify(data.fences, null, 2));
                } catch (_) {}
                break;
            case 'react-render-error':
                if (!data.id) return;
                window.__renderErrors__[data.id] = data;
                window.__lastRenderErrorId = data.id;
                try {
                    console.error('[REACT_RENDERER_PARENT_DIAG] runtime error for',
                        data.id, data.message);
                    if (data.stack) console.error('  stackHead:', data.stack.split('\n').slice(0, 4).join('\n           '));
                } catch (_) {}
                break;
            case 'react-render-script-error':
                // DIAGNOSTIC (added 2026-07-26, see bug-findings H1):
                // companion to the runtime-error case above. Captures the
                // post-transform parse error so blank-iframe bugs leave a
                // trail.  `outTail` is the last 2KB of Babel output — paste
                // into `new Function(outTail)` to reproduce offline.
                if (!data.id) return;
                window.__renderScriptErrors__ = window.__renderScriptErrors__ || {};
                window.__renderScriptErrors__[data.id] = data;
                window.__lastRenderScriptErrorId = data.id;
                try {
                    console.error('[REACT_RENDERER_PARENT_DIAG] script parse error for',
                        data.id, '(' + data.source + ')', data.message);
                } catch (_) {}
                break;
            case 'react-render-babel-output':
                // DIAGNOSTIC v8 (2026-07-26): iframe posts the EXACT bytes Babel
                // produced. The v5/v6 capture inside the iframe used
                // window.parent.__lastChartOut__ which silently fails in
                // srcdoc-sandboxed iframes (opaque-origin). postMessage is
                // cross-origin-safe, so this capture survives even when the
                // appended <script> tag throws a script-body SyntaxError and
                // kills the rest of the iframe script.
                if (!data.id) return;
                window.__babelOutputs__ = window.__babelOutputs__ || {};
                window.__babelOutputs__[data.id] = data;
                window.__lastBabelOutputId = data.id;
                window.__lastChartOut__     = data.babelOut;
                window.__lastChartOutLen__  = data.babelOutLen;
                window.__lastChartRaw__     = data.rawSource;
                window.__lastChartRawLen__  = data.rawSourceLen;
                window.__lastChartRawId__   = data.id;
                try {
                    console.log('[REACT_RENDERER_PARENT_DIAG] v8 babel-output captured.',
                        'id:', data.id,
                        'rawLen:', data.rawSourceLen,
                        'outLen:', data.babelOutLen);
                } catch (_) {}
                break;
            case 'react-render-babel-error':
                // DIAGNOSTIC v8 (2026-07-26): mirror of the in-iframe
                // __lastBadJsx capture, but cross-origin-safe. Surfaces the
                // exact Babel error message + failing source when Babel.transform
                // itself throws (separate from the script-body SyntaxError
                // case captured by react-render-babel-output).
                if (!data.id) return;
                window.__babelErrors__ = window.__babelErrors__ || {};
                window.__babelErrors__[data.id] = data;
                window.__lastBabelErrorId = data.id;
                try {
                    console.error('[REACT_RENDERER_PARENT_DIAG] v8 babel-error captured.',
                        'id:', data.id,
                        'rawLen:', data.rawSourceLen,
                        'msg:', data.errorMessage);
                } catch (_) {}
                break;
            case 'react-render-pre-transform':
                // DIAGNOSTIC v8 (2026-07-26): captures the cleaned JSX
                // (after import-strip + {flag&&JSX} regex rewrite) that is
                // about to be fed to Babel. Lets us reproduce the exact
                // Babel input offline when __lastChartOut__ reveals a
                // script-body SyntaxError.
                if (!data.id) return;
                window.__preTransform__ = window.__preTransform__ || {};
                window.__preTransform__[data.id] = data;
                window.__lastPreTransformId = data.id;
                window.__lastChartRaw__    = data.rawSource;
                window.__lastChartRawLen__ = data.rawSourceLen;
                try {
                    console.log('[REACT_RENDERER_PARENT_DIAG] v8 pre-transform captured.',
                        'id:', data.id,
                        'len:', data.rawSourceLen);
                } catch (_) {}
                break;
            case 'react-render-console-batch':
                // DIAGNOSTIC v9 (2026-07-27): reply to the parent's
                // 'react-render-console-request'. The iframe's console-capture
                // IIFE (installed at the top of its run-engine) holds a 50-entry
                // ring buffer of every console.{log,warn,error,info,debug} call
                // it saw. The parent copies the buffer into the diag popover
                // so the user can paste it into chat without re-attaching
                // DevTools to the sandboxed child iframe. See
                // __REACT_VIZ_DIAG__ flag in addIframeActionBar() (in
                // visualisation_v3.js) — set false to hide the diag button.
                if (!data.id) return;
                window.__renderConsoleBatches__ = window.__renderConsoleBatches__ || {};
                window.__renderConsoleBatches__[data.id] = data;
                window.__lastRenderConsoleBatchId = data.id;
                try {
                    console.log('[REACT_RENDERER_PARENT_DIAG] v9 console-batch captured.',
                        'id:', data.id,
                        'entries:', (data.entries || []).length);
                } catch (_) {}
                break;
        }
    });
})();

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
                } else if (
                    event.data &&
                    event.data.type === 'react-render-snapshot' &&
                    event.data.id === chartId
                ) {
                    // Happy-path diagnostic (added 2026-07-23). The renderer
                    // posts its full runtime state from inside the iframe
                    // immediately after the transformed script executes but
                    // BEFORE auto-mount. Capture it on the parent so the
                    // "blank iframe, no console errors" class of bug can be
                    // diagnosed from one DevTools console instead of having
                    // to attach to each sandboxed child iframe.
                    try {
                        window.__renderSnapshots__ = window.__renderSnapshots__ || {};
                        window.__renderSnapshots__[event.data.id] = event.data.snap;
                        window.__lastRenderSnapshotId = event.data.id;
                        console.log('[REACT_RENDERER_PARENT_DIAG] snapshot for', event.data.id, JSON.stringify(event.data.snap, null, 2));
                    } catch (_) {}
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

    /**
     * safeJsString — wrap a user/AI-controlled string as a JavaScript string
     * literal that is also safe to embed inside a `<script>` element.
     *
     * The browser's HTML parser scans the raw bytes of the page for the byte
     * sequence `</script` (case-insensitive) and treats it as the end of the
     * enclosing `<script>` element, REGARDLESS of JavaScript string quoting.
     * When an AI emits a literal `</script>` inside a template string in
     * its JSX (e.g. an `</script>` HTML snippet inside a `<Tooltip>` or a
     * `<style>` template), it survives JSON.stringify (JSON does not escape
     * `<` or `/`) and breaks the host `<script>` block — every line of the
     * run-engine that follows becomes raw HTML, producing a white iframe
     * with `SyntaxError: Invalid or unexpected token (at about:srcdoc:N:36)`.
     *
     * Fix: after JSON.stringify, replace `</script` with `<\/script`. Inside
     * the resulting JS source the string literal `"<\/script>"` is parsed by
     * the JS engine as `<\/script>` → escape sequence `\/` → `/` literal →
     * final string value `</script>` (the AI's intent is preserved). The
     * HTML parser never sees `</script>`, so the host script stays open.
     *
     * @param {string} s  Raw string value (the AI's JSX, identifier list, etc.)
     * @returns {string}  A JS string literal safe to embed inside <script>
     */
    safeJsString(s) {
        return JSON.stringify(s).replace(/<\/(script)/gi, '<\\/$1');
    }

    /**
     * rewriteShortCircuitJSX — convert `{flag && <JSX/>}` to
     * `{flag ? (<JSX/>) : null}` so the JSX renders as a stable React
     * element of type `null` when flag is falsy, instead of a primitive
     * `false` that Recharts' per-axis child registry mishandles.
     *
     * Recharts walks children with React.Children.forEach at first mount
     * to register scale slots keyed by child position. When a child is the
     * literal `false` (the result of `flag && JSX` when flag is falsy),
     * the slot is left undefined; the next render call hits
     * `TypeError: t.has is not a function` (Recharts.js On.o.domain).
     *
     * The 2026-07-25 simple-flag regex only matched `{flag && (<X/>)}`
     * (paren-wrapped). Six common AI patterns slipped through:
     *   1. `{flag && <X/>}` (no parens — most common)
     *   2. `{flag && <X></X>}` (no parens, closing tag)
     *   3. `{state.x && <X/>}` (member flag, no parens)
     *   4. `{period === '1y' && <X/>}` (comparison flag, parens)
     *   5. `{flag && (\n  <X/>\n)}` (multi-line paren JSX)
     *   6. `{flag && (<><X/><X/></>)}` (fragment)
     *
     * This walker handles all six. Anchoring the right-hand side on `<`
     * (JSX opener) prevents false-positives on `{x && y}`, `{x && 5}`,
     * `{x && "str"}`, `{x && y.length}`, etc. Patterns where the flag
     * itself contains a `&&` (e.g. `.map((p) => p.x && <Row/>}`) are
     * intentionally LEFT ALONE — they don't reach Recharts' axis registry.
     *
     * @param {string} src  JSX source after import/export stripping
     * @returns {string}    Source with short-circuit JSX rewritten
     */
    rewriteShortCircuitJSX(src) {
        // Match the OPEN of a JSX expression `{ ... && ` where the left
        // operand is a simple identifier (with optional dotted access) or
        // a comparison expression. Captures the flag so we can put it back
        // on the LHS of the ternary.
        const FLAG_RE = /\{\s*([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*(?:\s*(?:==|!=|===|!==|<=|>=|<|>)\s*[^&]+?)?)\s*&&\s*/g;
        let out = '';
        let lastEnd = 0;
        let m;
        while ((m = FLAG_RE.exec(src)) !== null) {
            const flag = m[1];
            const afterAnd = FLAG_RE.lastIndex;
            const rest = src.slice(afterAnd);

            // Skip whitespace, optionally consume an outer `(`
            let i = 0;
            while (i < rest.length && /\s/.test(rest[i])) i++;
            const wrappedInParen = rest[i] === '(';
            if (wrappedInParen) i++;
            while (i < rest.length && /\s/.test(rest[i])) i++;

            // Must now see `<` (JSX opener) — otherwise this `&&` isn't
            // the chart-axis-registry pattern; bail without rewriting.
            if (rest[i] !== '<') {
                FLAG_RE.lastIndex = afterAnd;  // re-attempt from after `&&`
                continue;
            }

            // Walk forward tracking brace + paren depth. The outer `{`
            // counts as 1, the optional `(` adds another. We stop when
            // depth returns to 0 (i.e. we've consumed the matching `}`
            // that closes the JSX expression). The closing `}` itself
            // is then excluded from the JSX slice (see `j - 1` below)
            // so the ternary output doesn't end with a stray `}`.
            let depth = 1 + (wrappedInParen ? 1 : 0);
            let inString = null;  // '"', "'", or '`'
            let sawJsxContent = false;
            let j = i;
            while (j < rest.length && depth > 0) {
                const c = rest[j];
                if (inString) {
                    if (c === '\\') { j += 2; continue; }
                    if (c === inString) inString = null;
                    j++; continue;
                }
                if (c === '"' || c === "'" || c === '`') { inString = c; j++; continue; }
                if (c === '{') { depth++; j++; sawJsxContent = true; continue; }
                if (c === '}') { depth--; j++; continue; }
                if (c === '(') { depth++; j++; continue; }
                if (c === ')') { depth--; j++; continue; }
                if (c === '<') { sawJsxContent = true; j++; continue; }
                j++;
            }
            // Bail if the JSX didn't close cleanly or didn't contain a `<`
            if (!sawJsxContent || depth !== 0) {
                FLAG_RE.lastIndex = afterAnd;
                continue;
            }

            // Build the ternary. The walker exits the loop AFTER consuming
            // the closing `}` of the JSX expression container, so back up
            // by 1 to exclude it from the JSX slice. Strip the optional
            // outer paren from the JSX slice so we don't end up with
            // `? ((<X/>)) :` (still syntactically valid, just ugly).
            let jsxSlice = rest.slice(0, j - 1);
            if (jsxSlice.startsWith('(') && jsxSlice.endsWith(')')) {
                jsxSlice = jsxSlice.slice(1, -1);
            }

            out += src.slice(lastEnd, m.index);
            out += `{${flag} ? (${jsxSlice.trim()}) : null}`;
            // lastEnd advances past the closing `}` of the JSX expression
            // container. The substitution `{flag ? ... : null}` already
            // has its own closing `}`, so we MUST consume the source's
            // closing `}` to avoid emitting two of them back-to-back.
            // (Without this, the output renders as `null}}` which is
            // syntax-invalid and crashes Babel.)
            lastEnd = afterAnd + j;
            FLAG_RE.lastIndex = lastEnd;
        }
        out += src.slice(lastEnd);
        return out;
    }

    buildReactSrcdoc(jsxContent, chartId) {
        // ── DIAGNOSTIC v7 (2026-07-25): UNCONDITIONAL entry-point log ──────────
        // If you see this in the parent console, buildReactSrcdoc IS being
        // called and your browser has the latest react_renderer.js. If you
        // do NOT see this, the browser is serving a stale version of the
        // file even after a hard reload — likely a service worker or
        // Cloudflare cache. Workaround: open DevTools → Application →
        // Service Workers → Unregister, then hard-reload again.
        try {
            window.__buildReactSrcdocCalls = (window.__buildReactSrcdocCalls || 0) + 1;
            console.log(
                '[REACT_RENDERER_DIAG] v7 buildReactSrcdoc ENTRY.',
                'call#:', window.__buildReactSrcdocCalls,
                'id:', chartId,
                'inLen:', jsxContent && jsxContent.length
            );
        } catch (_) { /* paranoid */ }

        // ── Library auto-detection ──────────────────────────────────────────────
        const usesRecharts = /recharts|BarChart|LineChart|PieChart|AreaChart|ScatterChart|RadarChart|ComposedChart|RadialBar|Treemap|Funnel/i.test(jsxContent);
        const usesLucide   = /lucide|LucideIcon|import.*from.*['"](lucide|lucide-react)['"]|\b(ChevronRight|ChevronDown|Circle|Square|Triangle|Star|Heart|Home|User|Settings|Search|Bell|Mail|Check|X|Plus|Minus|Edit|Trash|Download|Upload|Eye|Lock|Unlock|ArrowRight|ArrowLeft|ArrowUp|ArrowDown)\b/.test(jsxContent);
        // Tailwind detection — covers all 4 forms of className the AI commonly emits:
        //   1. className="flex ..."           (plain double-quoted string)
        //   2. className='flex ...'           (plain single-quoted)
        //   3. className={"flex ..."}         (JS string literal in braces)
        //   4. className={`flex ...`}         (template literal in braces)
        // The OLD regex only matched form 1, so any AI emission in forms 3/4
        // produced usesTailwind=false → Tailwind was never injected → the
        // dashboard rendered as naked text. Symptom: "huge icons, text with no
        // structure". Bug filed 2026-07-27 against d3f516bc-era logic.
        //
        // Each Tailwind utility keyword is anchored with left+right
        // word-boundary lookarounds so substrings inside longer identifiers
        // (e.g. "hidden" inside "another-class") don't false-positive.
        const tailwindClassAttrRegex = /className=(?:"([^"']*?)"|'([^"']*?)'|\{"([^"']*?)"\}|'\{`([^`]*?)`\}'|\{`([^`]*?)`\})/g;
        const tailwindKeywordPattern = /(?:^|\s|["'`\\$])(?:flex|grid|p-\d+|m-\d+|pt-\d+|pb-\d+|pl-\d+|pr-\d+|mt-\d+|mb-\d+|ml-\d+|mr-\d+|mx-\d+|my-\d+|px-\d+|py-\d+|text-[a-z]+|bg-[a-z]+|border|rounded|shadow|w-\d+|h-\d+|min-h-|max-w-|gap-\d+|space-[xy]-|items-|justify-|font-|leading-|tracking-|opacity-\d+|z-\d+|top-|right-|bottom-|left-|absolute|relative|fixed|sticky|hidden|block|inline|overflow-|cursor-|transition|duration-|ease-|hover:|focus:|sm:|md:|lg:|xl:|2xl:)(?=\s|$|["'`}])/;
        const usesTailwind = (() => {
            tailwindClassAttrRegex.lastIndex = 0;
            let m;
            while ((m = tailwindClassAttrRegex.exec(jsxContent)) !== null) {
                const value = m[1] || m[2] || m[3] || m[4] || m[5];
                if (value && tailwindKeywordPattern.test(value)) return true;
            }
            return false;
        })();

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
        const _cleanedJSX = unwrappedJSX
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
            // `await import(...)` — the dynamic-import regex below would
            // match the `import(...)` substring, leaving a stranded `await`
            // keyword at the top level (a syntax error in any classic
            // non-module script). Strip the `await` prefix so the next
            // replace catches the rewritten `import(`. (Added 2026-07-26.)
            .replace(/\bawait\s+import\s*\(/g, 'import(')
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
            // ── Convert short-circuit `{flag && JSX}` to ternary `{flag ? JSX : null}` ──
            // Recharts's per-axis registry walks children with React.Children.forEach.
            // Short-circuit booleans (false from `flag && JSX` when flag is false)
            // are filtered out correctly, BUT when ComposedChart combines multiple
            // children that share a yAxisId (Area+Bar on left, Line on right), the
            // initial mount computes the scale's domain BEFORE all children have
            // registered. The unrendered child leaves its slot undefined; the next
            // pass calls `.has()` on the undefined slot and crashes with
            //   TypeError: t.has is not a function  (Recharts.js On.o.domain)
            // Converting to the ternary form produces a stable React element of
            // type `null` when flag is false instead of a primitive boolean, which
            // Recharts handles cleanly across remounts. Toggle behaviour is
            // preserved — the JSX renders when flag is truthy and renders nothing
            // (a null child) when flag is falsy.
            //
            // The 2026-07-25 simple-flag regex only matched the parenthesised
            // form `{flag && (<X/>)}` and silently let six common AI patterns
            // through:
            //   1. {flag && <X/>}            (no parens — MOST COMMON)
            //   2. {flag && <X></X>}         (no parens, closing tag)
            //   3. {state.x && <X/>}         (member flag, no parens)
            //   4. {period === '1y' && <X/>} (comparison flag)
            //   5. {flag && (\n  <X/>\n)}    (multi-line paren JSX)
            //   6. {flag && (<><X/></>)}     (fragment)
            // These all crashed charts silently (chart axes never rendered) and
            // surfaced only as `TypeError: t.has is not a function` deep inside
            // Recharts' scale-merging code. The walker above (rewriteShortCircuitJSX)
            // handles all six by anchoring the right-hand side on `<` (JSX opener)
            // and walking brace + paren depth to find the matching `}`. See
            // REACT_RENDERER_LUCIDE_TROUBLESHOOTING_2026-07-22.md §3 for the
            // original investigation.
            .trim();

        // Run the JSX-aware walker on the accumulated string. The walker is
        // not a simple .replace() callback (it needs to see the whole source
        // to advance `lastIndex` across matches), so it runs as a separate
        // pass after the chain above.
        const cleanedJSX = this.rewriteShortCircuitJSX(_cleanedJSX);

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
            ? `  <script src="visualisation_engine/libs/prop-types.js?v=20260727_1640"><\/script>\n  <script src="visualisation_engine/libs/Recharts.js?v=20260727_1640"><\/script>` : '';
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
        // Recharts — expose all chart components as window globals so user code
        // can use <BarChart .../> without an explicit prefix.
        //
        // Defensive v2 (2026-07-24): the previous version did
        //     var r = window.Recharts || {};
        //     names.forEach(function (n) { window[n] = r[n]; });
        // which silently assigned `undefined` to every name if window.Recharts
        // was not yet set when this IIFE fired (it lives in the inline script
        // after a <script src="...Recharts.js?..."> tag; classic <script>
        // tags run in document order so Recharts should be set, but we saw
        // a render where BarChart / ScatterChart ended up as functions
        // (came from rechartsSetup OR a later hoist) while ResponsiveContainer
        // / Cell / CartesianGrid were undefined — inconsistent with both
        // sources being available at the same instant, which suggests the
        // snapshot itself raced the UMD evaluation in some browsers).
        //
        // New contract:
        //   1) Poll for window.Recharts to appear (max 3 s) — robust against
        //      UMD evaluation order races and slow CDN responses.
        //   2) Only assign window[name] when r[name] is actually defined —
        //      never write `undefined` into a slot.
        //   3) Surface a clear console error if window.Recharts never appears
        //      (e.g. prop-types.js failed to load, breaking the UMD factory
        //      and leaving window.Recharts permanently missing).
        const rechartsSetup = usesRecharts ? `
    // Recharts — expose all chart components as window globals so user code
    // can use <BarChart .../> without an explicit prefix.
    (function () {
        var names = [
            'BarChart','Bar','LineChart','Line','PieChart','Pie','Cell',
            'AreaChart','Area','ScatterChart','Scatter','XAxis','YAxis','ZAxis',
            'CartesianGrid','Tooltip','Legend','ResponsiveContainer',
            'RadarChart','Radar','PolarAngleAxis','PolarRadiusAxis','PolarGrid',
            'ComposedChart','RadialBarChart','RadialBar','Treemap','FunnelChart','Funnel',
            'LabelList','ReferenceLine','ReferenceArea','ReferenceDot',
            'Brush','ErrorBar','Label'
        ];
        var assigned = [];
        function tryAssign() {
            var r = window.Recharts;
            if (!r || typeof r !== 'object') return false;
            for (var i = 0; i < names.length; i++) {
                var n = names[i];
                var v = r[n];
                if (typeof v === 'function' || typeof v === 'object') {
                    if (window[n] !== v) { window[n] = v; assigned.push(n); }
                }
            }
            return true;
        }
        if (!tryAssign()) {
            var waited = 0;
            var poll = setInterval(function () {
                waited += 50;
                if (tryAssign() || waited >= 3000) {
                    clearInterval(poll);
                    if (waited >= 3000 && !window.Recharts) {
                        console.error('[REACT_RENDERER] window.Recharts never appeared within 3 s. ' +
                            'prop-types.js may have failed to load (Recharts UMD factory needs it). ' +
                            'Check Network tab for visualisation_engine/libs/prop-types.js — a 404 / CORS / MIME error here breaks the entire chart.');
                    } else if (assigned.length) {
                        console.log('[REACT_RENDERER] rechartsSetup resolved after ' + waited + ' ms:',
                            assigned.length + ' components on window');
                    }
                }
            }, 50);
        } else if (assigned.length) {
            console.log('[REACT_RENDERER] rechartsSetup resolved synchronously:',
                assigned.length + ' components on window');
        }
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

        // Recharts component names that ALSO exist as Lucide icons
        // (BarChart, LineChart, PieChart, Brush, Bar, ...). For these
        // names we MUST resolve to the Recharts component — Lucide's
        // icon would render as a giant SVG instead of a chart. Mirror
        // the names list used by rechartsSetup above so any name we
        // pre-lift onto window is also excluded from the Lucide pass.
        const RECHARTS_PRIORITY_NAMES = [
            'BarChart','Bar','LineChart','Line','PieChart','Pie','Cell',
            'AreaChart','Area','ScatterChart','Scatter','XAxis','YAxis','ZAxis',
            'CartesianGrid','Tooltip','Legend','ResponsiveContainer',
            'RadarChart','Radar','PolarAngleAxis','PolarRadiusAxis','PolarGrid',
            'ComposedChart','RadialBarChart','RadialBar','Treemap','FunnelChart','Funnel',
            'LabelList','ReferenceLine','ReferenceArea','ReferenceDot',
            'Brush','ErrorBar','Label'
        ];

        const identifierHoist = `
    (function () {
        var React = window.React;
        var R = window.Recharts || {};
        var L = window.lucide || {};
        // Names that need Recharts resolution BEFORE Lucide. Lucide UMD
        // exports icons with the same names as several Recharts components
        // (PieChart, BarChart, LineChart, Brush, Bar, ...). Without this
        // priority list, the first pass would wrap Lucide's icon descriptor
        // as a "component" and the user's <PieChart> would render a giant
        // Lucide pie-chart SVG instead of a real Recharts pie chart.
        var priorityNames = ${JSON.stringify(RECHARTS_PRIORITY_NAMES)};
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
            // For Recharts priority names, resolve Recharts BEFORE Lucide.
            // For everything else, fall back to Lucide-first (the previous
            // behaviour, which is correct for non-colliding Lucide icons).
            var sources = priorityNames.indexOf(name) >= 0 ? [R, L] : [L, R];
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
        // SKIP Recharts priority names so Lucide's array descriptors do
        // not overwrite Recharts components that rechartsSetup already set
        // (this was the root cause of the giant-Lucide-PieChart bug).
        try {
            Object.keys(L).forEach(function (k) {
                if (k === 'createElement' || k === 'createIcons' || k === 'icons' || k === 'default') return;
                if (priorityNames.indexOf(k) >= 0) return;
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

        // ── DIAGNOSTIC v6 (2026-07-25): PARENT-side capture ────────────────────
        // The Babel.transform at line 717 runs INSIDE the iframe (it's part of
        // the srcdoc). If the iframe's <script> tag has a script-body
        // SyntaxError, every line in that script (including the postMessage-
        // based diagnostics) is dead before it can execute. The parent has
        // the raw source in cleanedJSX at this exact moment, so we capture
        // it on the parent BEFORE returning the srcdoc. This runs even when
        // the iframe ends up blank, because the parent SPA is unaffected by
        // iframe script parse failures.
        try {
            if (typeof window !== 'undefined') {
                window.__lastChartRaw__      = cleanedJSX;
                window.__lastChartRawLen__   = cleanedJSX.length;
                window.__lastChartRawHead__  = cleanedJSX.slice(0, 1200);
                window.__lastChartRawId__    = chartId;
                console.log(
                    '[REACT_RENDERER_DIAG] v6 captured parent-side raw.',
                    'len:', cleanedJSX.length,
                    'id:', chartId
                );
            }
        } catch (_diagIgnoreErr) { /* paranoid */ }

        return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
${tailwindLink}
  <!-- Pre-React Map shim v2: react-dom 18.3.1 commit-phase child-fiber mapper
       (function d inside Dh) does for(a=new Map;...) a.set(b.index,b).
       If Map.prototype.set is missing or non-callable, every re-render
       crashes with a.set is not a function deep in react-dom. v1 only
       restored when broken AT iframe load — useless if the corruption
       happens between mount and the first hover/scroll re-render. v2
       unconditionally installs an accessor (getter/setter) pair on
       Map.prototype.{set,get,has,delete}: the getter always returns
       the saved native (or a __m_<key> storage fallback if the native
       was already broken at load), and the silent setter absorbs any
       later Map.prototype.set = somethingElse assignment. Also wraps
       window.Map with an accessor so reassigning the global Map
       constructor is absorbed too. Survives polyfill overrides that
       happen AFTER iframe load. -->
  <script>(function(){if(typeof window==="undefined"||!window.Map)return;var NativeMap=window.Map;var p=NativeMap.prototype;function fbSet(k,v){this["__m_"+k]=v;return this;}function fbGet(k){return this["__m_"+k];}function fbHas(k){return"__m_"+k in this;}function fbDel(k){return delete this["__m_"+k];}function guard(n,fb){var cur=p[n],fn=(typeof cur==="function")?cur:fb;try{Object.defineProperty(p,n,{configurable:true,enumerable:false,get:function(){return fn;},set:function(v){}});}catch(e){try{p[n]=fn;}catch(_){}}}guard("set",fbSet);guard("get",fbGet);guard("has",fbHas);guard("delete",fbDel);try{Object.defineProperty(window,"Map",{configurable:true,enumerable:false,get:function(){return NativeMap;},set:function(v){}});}catch(e){}})();<\/script>
  <!-- React 18 UMD (self-hosted: see UI/visualisation_engine/libs/) -->
  <script src="visualisation_engine/libs/react.production.min.js?v=20260727_1820"><\/script>
  <script src="visualisation_engine/libs/react-dom.production.min.js?v=20260727_1820"><\/script>
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
        // ── DIAGNOSTIC v9 (2026-07-27): IFRAME CONSOLE CAPTURE ─────────────
        // Patches console.{log,warn,error,info,debug} to push into a 50-entry
        // ring buffer, then forwards to the real console (no double-log).
        // The parent posts 'react-render-console-request' and we reply with
        // 'react-render-console-batch'. The diag kebab in addIframeActionBar
        // (visualisation_v3.js) surfaces the buffer in a copy-to-clipboard
        // action so the user can paste iframe logs into chat without
        // re-attaching DevTools to the sandboxed child. See __REACT_VIZ_DIAG__
        // flag — set false to hide the diag button.
        (function installDiagConsoleCapture() {
            try {
                if (window.__DIAG_CONSOLE_INSTALLED__) return;
                window.__DIAG_CONSOLE_INSTALLED__ = true;
                var __buf = [];
                var __MAX = 50;
                function __push(level, args) {
                    try {
                        var parts = [];
                        for (var i = 0; i < args.length; i++) {
                            var a = args[i];
                            if (a instanceof Error) parts.push(a.stack || a.message);
                            else if (typeof a === 'object') {
                                try { parts.push(JSON.stringify(a)); }
                                catch (_) { parts.push(String(a)); }
                            } else parts.push(String(a));
                        }
                        __buf.push({ t: Date.now(), level: level, msg: parts.join(' ') });
                        if (__buf.length > __MAX) __buf.shift();
                    } catch (_) { /* never throw out of console */ }
                }
                ['log','warn','error','info','debug'].forEach(function (k) {
                    var orig = console[k];
                    console[k] = function () {
                        __push(k, arguments);
                        try { return orig.apply(console, arguments); } catch (_) {}
                    };
                });
                window.__DIAG_CONSOLE_BUFFER__ = function () { return __buf.slice(); };
                window.addEventListener('message', function (e) {
                    if (!e.data || typeof e.data !== 'object') return;
                    if (e.data.type === 'react-render-console-request' &&
                        e.data.id === '${chartId}') {
                        try {
                            window.parent.postMessage({
                                type: 'react-render-console-batch',
                                id: '${chartId}',
                                entries: __buf.slice()
                            }, '*');
                        } catch (_) {}
                    }
                });
            } catch (_) { /* capture is best-effort */ }
        })();

        // ── Pre-execute diagnostic for the parent console ──────────────────
        try {
            window.parent.postMessage({
                type: 'react-render-diagnostic',
                id: '${chartId}',
                jsxLength: ${JSON.stringify(cleanedJSX.length)},
                jsxPreview: ${this.safeJsString(cleanedJSX.slice(0, 300))}
            }, '*');
        } catch (_) {}

        // ── DIAGNOSTIC FENCES (2026-07-23) ─────────────────────────────────
        // The recurring bug "e.get is not a function" at babel.min.js:1:925003
        // fires inside makeWeakCache (function NI(e,t,r) in the minified
        // bundle). That cache is initialised by @babel/core when it resolves
        // plugins for a file. We do not know which renderer setup step
        // corrupts the cache reference, so we probe Babel.transform with a
        // trivial JSX source at each seam between setup steps. Whichever
        // fence reports ok=false narrows the search.
        //
        // Results are surfaced two ways:
        //   1) window.parent.__babelFences  (same-origin only; wrapped in
        //      try/catch because the iframe is srcdoc-sandboxed and the
        //      write throws SecurityError cross-origin)
        //   2) postMessage 'react-render-fences'  (cross-origin safe)
        var __babelFences = [];
        function __babelFence(label) {
            try {
                Babel.transform('function T(){return <div/>;}', {
                    presets: [['react', { runtime: 'classic' }]]
                });
                __babelFences.push({ label: label, ok: true });
            } catch (e) {
                __babelFences.push({
                    label: label,
                    ok: false,
                    err: e.message,
                    stackHead: ((e.stack || '').split(String.fromCharCode(10)).slice(0, 3).join(' | '))
                });
            }
        }
        __babelFence('F0 — Babel initial state (no setup yet)');

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
        __babelFence('F1 — after React hooks assigned to window');

${rechartsSetup}
        __babelFence('F2 — after Recharts globals on window');

        // NOTE: the identifierHoist IIFE is intentionally NOT injected here.
        // The 2026-07-23 fence diagnostic proved that running it before
        // Babel.transform corrupts Babel's internal plugin cache
        // (makeWeakCache throws "TypeError: e.get is not a function" the
        // next time Babel.transform is called). The hoist only needs to run
        // before the transformed source is EXECUTED, not before it is
        // TRANSFORMED — Babel's syntax pass doesn't care whether
        // window.BarChart is set yet. The IIFE is therefore injected later,
        // between the transform-success and the classic-<script> append.
        __babelFence('F3 — before actual transform (final Babel sanity check)');

        // Surface fence results to parent for offline inspection. The
        // postMessage is the cross-origin-safe channel; the direct property
        // assignment is the same-origin fast path (silently fails in sandbox).
        try {
            window.parent.__babelFences = __babelFences;
            window.parent.__lastFenceFrameId = '${chartId}';
        } catch (_) {}
        try {
            window.parent.postMessage({
                type: 'react-render-fences',
                id: '${chartId}',
                fences: __babelFences
            }, '*');
        } catch (_) {}

        // DIAGNOSTIC v8 (2026-07-26): forward the cleaned JSX source to the
        // parent BEFORE Babel.transform runs. The raw capture inside the
        // iframe (v6) lives on window.__lastChartRaw__, but v6 reads from
        // 'cleanedJSX' after import/export stripping + the {flag && JSX}
        // regex rewrite -- which is exactly what gets fed to Babel. Sending
        // it via postMessage (cross-origin-safe) lets the parent console
        // inspect the EXACT bytes Babel sees even when the iframe script
        // later dies with a script-body SyntaxError.
        //
        // Note: rawSource must be assigned BEFORE this postMessage runs, so
        // the JSON.stringify has a defined value to send.
        var rawSource = ${this.safeJsString(cleanedJSX)};
        try {
            window.parent.postMessage({
                type: 'react-render-pre-transform',
                id: '${chartId}',
                rawSource: rawSource,
                rawSourceLen: rawSource.length,
                fencesAtStart: __babelFences.slice()
            }, '*');
        } catch (_) {}

        var out;
        try {
            // ----- Babel plugin: rewrite {cond && <JSX/>} -> {cond ? <JSX/> : null}
            // Recharts builds its per-axis registry via React.Children.toArray()
            // at first mount. toArray() treats the literal false (the result of
            // 'cond && <X/>' when cond is falsy) by inserting a placeholder text
            // child, whereas null (the result of 'cond ? <X/> : null') is
            // dropped entirely. Recharts caches scale slots keyed on those child
            // positions; a false child causes the next render to call .has() on
            // an undefined slot, throwing 't.has is not a function' from a
            // Recharts Map subclass during domain merging.
            //
            // The 2026-07-23 fence+tail diagnostic captured the exact failing
            // pattern: <ComposedChart> with {showX && (<Component yAxisId="..."/>)}
            // children that all share/duplicate axis IDs destabilise the
            // registry on first mount. The text-based simple-identifier regex
            // above (~line 304) already covers {flag && (<JSX/>)} which is the
            // most common form that triggers Recharts' axis registry falsy-
            // placeholder bug.
            //
            // Defensive v4 (2026-07-25): the AST plugin is DISABLED entirely.
            // Rationale: the previous rewrite (cond && X -> cond ? X : null) is
            // sound for the simple-identifier case the regex already covers, but
            // its expansion to handle complex right-hand sides (Identifier /
            // MemberExpression / CallExpression / ConditionalExpression /
            // LogicalExpression) and even its 2-type JSXElement/JSXFragment
            // restriction still produced SyntaxError-at-script-time output for at
            // least one real-world chart pattern that bypassed every locally-
            // tested case. The iframe would render blank with no recoverable
            // state because new Function() (function-body parse) is more
            // permissive than the <script> parser the browser actually uses to
            // execute the code (script-body parse). Without a plugin,
            // Babel.transform only emits standard React.createElement output
            // that the <script> parser is guaranteed to accept.
            // Trade-off: the {complexCond && (<JSX/>)} pattern reverts to the
            // original Recharts bug (a.set is not a function /
            // i.set is not a function on axis registry falsy-placeholder). The
            // user will see the chart render with a visible runtime error in
            // DevTools instead of a completely blank iframe - a much better
            // failure mode than blank-canvas. The simple-identifier regex
            // above still handles the {flag && (<JSX/>)} case which is the most
            // common Recharts offender.
            // DIAGNOSTIC v9 (2026-07-28): auto-fixup for AI-emitted JSX with bare
            // array literals on attributes, e.g. the AI writes
            //   <ComposedChart data=[{...}, {...}] />
            // where JSX grammar requires either quoted text or a curly-brace
            // expression. A bare [ ... ] is a parse error. Without this fixup
            // Babel throws BEFORE ReactDOM.createRoot().render(), so
            // BoundaryClass never mounts and componentDidCatch never fires -
            // the iframe ends up blank with only the red diagnostic panel,
            // which is invisible from the parent DevTools because of the
            // cross-origin sandbox (allow-scripts only, no allow-same-origin).
            // The regex matches an equals-sign followed by [ array ] where
            // the array contains 0..1 levels of nested brackets. This covers
            // every chart payload shape the AI emits in practice. Wrapping
            // [ ... ] in { ... } is idempotent: a well-formed attr={ [...] }
            // is already wrapped, so the inner [ is preceded by {, not by an
            // equals-sign, and the regex never matches it.
            // ── F5: defensive rename of destructured [id, X] parameters ────────
            // BUGFIX 2026-07-28. Babel Standalone 7.24.7 has a silent scope-
            // shadow bug when JSX contains BOTH <X id="..."/> AND a nested
            // .map(([id, ...]) => {...}) callback: the destructured \'id\'
            // parameter is dropped from the emitted scope, so the React
            // render throws \'ReferenceError: id is not defined\' even though
            // the Babel output passes the \'new Function()\' pre-parse and
            // the <script> append succeeds. The error is also a runtime
            // (not a script-body) failure, so the iframe sandbox hides it
            // from the parent console.
            //
            // The pre-pass scans the rawSource for \'([id, X])\' destructuring
            // patterns, finds the matching \'=>\' arrow + \'{ ... }\' body, and
            // renames \'id\' -> \'__entryId__\' everywhere inside that callback.
            // The rename regex \'(?<![.\w])id(?!\w)(?!:)\' is precise:
            //   - (?<![.\w]) rejects \'node.id\' (preceded by \'.\') and \'hidden\'
            //     (preceded by word char)
            //   - (?!\w) rejects \'idempotent\' (followed by word char)
            //   - (?!:) rejects the \'id:\' shorthand-key position in \'{id: id}\'
            //     -- the *property key* is left alone, only the *value ref*
            //     is renamed. This matters because Babel transforms JSX
            //     <X id="..."> into \'{id: "..."}\' createElement props, and
            //     the property key stays put.
            //
            // State machine correctness: skips string literals (with
            // backslash escapes for \" \\ \\' \'), line comments, and block
            // comments when scanning for the \'([id,\' token and when
            // counting brace depth. Skips implicit-return single-expression
            // arrows (no \'{\' body) and unbalanced braces (assumes our
            // heuristic was wrong and lets Babel have the original source).
            //
            // Fixes: chartId 'two-rule-react-1785241715598' (Business Process
            // Flow, 12-step decision tree with branching paths). Without
            // this, the user has to retry the AI with "rename your destructured
            // id parameter", which is a prompt-level workaround and would
            // block React parity with Mermaid for flow diagrams.
            //
            // Diagnostic: every rename is reported on the F5 fence so we can
            // see in the kebab menu exactly how many bindings were rewritten.
            var __idShadowFixApplied = false;
            var __idShadowFixRenames = 0;
            try {
                var __idShadowResult = (function () {
                    var s = rawSource;
                    var out = '';
                    var i = 0;
                    var n = s.length;
                    var renames = 0;
                    // Match standalone \'id\' -- not preceded by \'.\' or word
                    // char, not followed by word char, not followed by \':\'.
                    var idRefRegex = /(?<![.\w])id(?!\w)(?!:)/g;
                    function skipStr(j) {
                        var c = s.charAt(j);
                        if (c !== '"' && c !== "'" && c !== String.fromCharCode(96)) return j + 1;
                        var q = c; j++;
                        while (j < n) {
                            var cc = s.charAt(j);
                            if (cc === '\\') { j += 2; continue; }
                            if (cc === q) { j++; return j; }
                            j++;
                        }
                        return j;
                    }
                    function skipComment(j) {
                        if (s.charAt(j) === '/' && s.charAt(j + 1) === '/') {
                            while (j < n && s.charAt(j) !== '\n') j++;
                            return j;
                        }
                        if (s.charAt(j) === '/' && s.charAt(j + 1) === '*') {
                            j += 2;
                            while (j < n - 1 && !(s.charAt(j) === '*' && s.charAt(j + 1) === '/')) j++;
                            return j + 2;
                        }
                        return j + 1;
                    }
                    function skipStrOrComment(j) {
                        var c = s.charAt(j);
                        if (c === '"' || c === "'" || c === String.fromCharCode(96)) return skipStr(j);
                        if (c === '/' && (s.charAt(j + 1) === '/' || s.charAt(j + 1) === '*')) return skipComment(j);
                        return j + 1;
                    }
                    function findArrow(j) {
                        // Find \'=>\' not inside string/comment, after \']\'
                        while (j < n) {
                            var c = s.charAt(j);
                            if (c === '"' || c === "'" || c === String.fromCharCode(96) || (c === '/' && (s.charAt(j + 1) === '/' || s.charAt(j + 1) === '*'))) {
                                j = skipStrOrComment(j); continue;
                            }
                            if (c === '=' && s.charAt(j + 1) === '>') return j;
                            j++;
                        }
                        return -1;
                    }
                    while (i < n) {
                        // Find next \'([id,\' (skip strings/comments)
                        var idx = -1;
                        var k = i;
                        while (k < n) {
                            var ck = s.charAt(k);
                            if (ck === '"' || ck === "'" || ck === String.fromCharCode(96) || (ck === '/' && (s.charAt(k + 1) === '/' || s.charAt(k + 1) === '*'))) {
                                k = skipStrOrComment(k); continue;
                            }
                            if (ck === '(' && s.charAt(k + 1) === '[' && s.charAt(k + 2) === 'i' && s.charAt(k + 3) === 'd' && s.charAt(k + 4) === ',') {
                                idx = k; break;
                            }
                            k++;
                        }
                        if (idx === -1) { out += s.slice(i); break; }
                        // Emit everything up to and including the open bracket
                        out += s.slice(i, idx + 2);
                        // Find the fat arrow after the destructuring
                        var arrowIdx = findArrow(idx + 4);
                        if (arrowIdx === -1) { out += s.slice(idx + 2); break; }
                        // Emit the renamed identifier (replacing id)
                        out += '__entryId__';
                        renames++;
                        // BUGFIX 2026-07-29: emit the trailing slice UP TO AND
                        // INCLUDING the fat arrow. Previous slice ended at
                        // arrowIdx (the equals sign), so the arrow operator
                        // was dropped from the output and produced syntax
                        // like map( ([__entryId__, next]) { ... } ) with no
                        // fat-arrow between the param list and body. Caught
                        // by f5_smoke.py before deploy.
                        out += s.slice(idx + 4, arrowIdx + 2);
                        // Find the opening \'{\' of the arrow body (skip ws)
                        var braceStart = arrowIdx + 2;
                        while (braceStart < n && /\s/.test(s.charAt(braceStart))) braceStart++;
                        if (s.charAt(braceStart) !== '{') {
                            // Implicit-return single expression -- skip
                            // rename for safety (regex scope guess is too
                            // risky vs the cost of a false-positive rename)
                            i = braceStart;
                            continue;
                        }
                        // Find matching \'}\' by brace depth (skip strings/comments)
                        var depth = 1;
                        var j = braceStart + 1;
                        while (j < n && depth > 0) {
                            var cj = s.charAt(j);
                            if (cj === '"' || cj === "'" || cj === String.fromCharCode(96) || (cj === '/' && (s.charAt(j + 1) === '/' || s.charAt(j + 1) === '*'))) {
                                j = skipStrOrComment(j); continue;
                            }
                            if (cj === '{') depth++;
                            else if (cj === '}') depth--;
                            j++;
                        }
                        if (depth !== 0) {
                            // Unbalanced -- bail out, leave Babel to try
                            i = braceStart + 1;
                            continue;
                        }
                        // Emit the body with 'id' references renamed
                        var body = s.slice(braceStart + 1, j - 1);
                        var renamedBody = body.replace(idRefRegex, '__entryId__');
                        var bodyRenames = (body.match(idRefRegex) || []).length;
                        renames += bodyRenames;
                        out += '{' + renamedBody + '}';
                        i = j;
                    }
                    return { src: out, renames: renames };
                })();
                if (__idShadowResult.renames > 0) {
                    rawSource = __idShadowResult.src;
                    __idShadowFixApplied = true;
                    __idShadowFixRenames = __idShadowResult.renames;
                }
                __babelFences.push({
                    label: 'F5 -- id shadow rename (destructured [id, X] => __entryId__)',
                    ok: __idShadowFixApplied,
                    renames: __idShadowFixRenames
                });
            } catch (__idShadowErr) {
                // Pre-process failed -- safe to ignore, Babel will still try.
                try {
                    __babelFences.push({
                        label: 'F5 -- id shadow rename (skipped: ' + ((__idShadowErr && __idShadowErr.message) || 'unknown') + ')',
                        ok: false
                    });
                } catch (_) {}
            }

            var __babelFixupApplied = false;
            try {
                out = Babel.transform(rawSource, {
                    presets: [['react', { runtime: 'classic' }]]
                }).code;
            } catch (__babelErr) {
                if (__babelErr && typeof __babelErr.message === 'string' &&
                    __babelErr.message.indexOf('JSX value should be either') !== -1) {
                    // ── BUGFIX 2026-07-28: double-escape every backslash in
                    // the regex literal below. The entire run-engine block
                    // lives inside the srcdoc template literal at line 861;
                    // JS template literals silently strip UNRECOGNISED escape
                    // sequences (\s, \[, \]) at parse time (same rule as
                    // regular string literals), turning /(=\s*)\[...\]/g into
                    // /(=s*)[...]/g at runtime - a regex that matches literal
                    // 's' and literal '[' / ']' instead of the intended
                    // metacharacters, so the fixup silently no-ops and the
                    // original Babel error re-throws to the diagnostic path.
                    // Doubling every \ leaves exactly one \ after template
                    // literal evaluation, which is the regex source we want.
                    var __fixedSrc = rawSource.replace(
                        /(=\\s*)\\[((?:[^\\[\\]]|\\[[^\\[\\]]*\\])*)\\]/g,
                        function (_m, _eq, _arr) { return _eq + '{' + _arr + '}'; }
                    );
                    if (__fixedSrc !== rawSource) {
                        __babelFixupApplied = true;
                        out = Babel.transform(__fixedSrc, {
                            presets: [['react', { runtime: 'classic' }]]
                        }).code;
                    } else {
                        // Regex did not change anything but Babel still
                        // complained - re-throw so the existing diagnostic
                        // path paints the red panel.
                        throw __babelErr;
                    }
                } else {
                    throw __babelErr;
                }
            }
            if (typeof __babelFences !== 'undefined') {
                __babelFences.push({
                    label: 'F2b -- plugin disabled v4, raw Babel output',
                    ok: true
                });
                __babelFences.push({
                    label: 'F4 -- JSX attr array wrap fixup',
                    ok: __babelFixupApplied
                });
            }

            // DIAGNOSTIC v8 (2026-07-26): postMessage the Babel output to the
            // parent IMMEDIATELY after transform succeeds, BEFORE the
            // identifierHoist IIFE and the classic-<script> append. This
            // captures the exact bytes the iframe's script parser will
            // (attempt to) parse -- if that parser later throws a script-body
            // SyntaxError at 'about:srcdoc:653:36', we can pull __lastChartOut__
            // from the parent console and reproduce the parse failure offline.
            // postMessage is cross-origin-safe; the direct window.parent.X =
            // assignments below are NOT (srcdoc iframes are opaque-origin and
            // those writes fail silently, which is why __lastChartOut__ was
            // undefined in v5/v6/v7 diagnostic runs).
            try {
                window.parent.postMessage({
                    type: 'react-render-babel-output',
                    id: '${chartId}',
                    rawSource: rawSource,
                    rawSourceLen: rawSource.length,
                    babelOut: out,
                    babelOutLen: out.length,
                    babelFences: __babelFences.slice()
                }, '*');
            } catch (_postMsgErr) { /* never throws */ }

            // DIAGNOSTIC v5 (2026-07-25): unconditionally capture the raw
            // JSX source AND the Babel output on parent.__lastChartRaw__ /
            // parent.__lastChartOut__. The postMessage-based __renderSnapshots__
            // only fires from a SUCCESSFULLY-parsed iframe script - if the
            // <script> tag has a script-body SyntaxError, the entire iframe
            // script is dead and no snapshot ever gets captured, which is the
            // exact failure mode we are trying to debug right now. The parent
            // has access to both inputs synchronously (Babel runs on the
            // parent; the iframe is just where it gets injected), so saving
            // them on parent always succeeds - even when the iframe ends up
            // blank. From DevTools the user can pull these with:
            //   window.parent.__lastChartRaw__
            //   window.parent.__lastChartOut__
            // and paste them back so we can reproduce offline. Removed once
            // the root cause is identified.
            try {
                if (typeof window !== 'undefined' && window.parent) {
                    window.parent.__lastChartRaw__ = rawSource;
                    window.parent.__lastChartOut__ = out;
                    window.parent.__lastChartRawLen__ = rawSource.length;
                    window.parent.__lastChartOutLen__ = out.length;
                    // Optional prefix-only preview of the babel output so the
                    // user can eyeball it in DevTools without grepping a 5k+
                    // string into the clipboard.
                    window.parent.__lastChartOutHead__ = out.slice(0, 1200);
                    // v9 (2026-07-29): surface F5 (id shadow rename) outcome
                    // on the parent window so the diag kebab can show how many
                    // destructured [id, X] bindings were rewritten even on
                    // successful renders. Falls back to false/0 because the
                    // vars are declared inside the F5 try block; outside the
                    // iframe-script root scope they exist if Babel got past it.
                    window.parent.__lastIdShadowFixApplied = (typeof __idShadowFixApplied === 'boolean') ? __idShadowFixApplied : false;
                    window.parent.__lastIdShadowFixRenames = (typeof __idShadowFixRenames === 'number') ? __idShadowFixRenames : 0;
                    console.log(
                        '[REACT_RENDERER_DIAG] v5 captured raw/out on parent.',
                        'rawLen:', rawSource.length,
                        'outLen:', out.length
                    );
                }
            } catch (_diagIgnoreErr) {
                /* parent unreachable (srcdoc sandbox restrictions) */
            }
        } catch (transformErr) {
            var tmsg = (transformErr && transformErr.message)
                ? transformErr.message : String(transformErr);
            var styleA = 'color:#b91c1c;background:#fef2f2;padding:16px;'
                + 'border-radius:8px;white-space:pre-wrap;'
                + 'font-family:ui-monospace,monospace;font-size:13px;'
                + 'line-height:1.5;border:1px solid #fecaca;';
            (document.getElementById('root') || document.body).innerHTML =
                '<pre style="' + styleA + '">'
                + '⚠ Babel transform failed:'
                + String.fromCharCode(10) + String.fromCharCode(10)
                + tmsg
                + String.fromCharCode(10) + String.fromCharCode(10)
                + 'Source preview (first 800 chars):'
                + String.fromCharCode(10)
                + rawSource.slice(0, 800)
                + '</pre>';
            window.parent.postMessage({ type: 'iframe-resize', id: '${chartId}', height: 400 }, '*');
            console.error('[REACT_RENDERER] Babel transform error:', transformErr);
            // ── DIAGNOSTIC: expose full failing source to parent for offline ───
            // analysis. Set by the renderer at the moment Babel throws so a
            // console-only investigation (no DevTools DOM inspection needed)
            // can recover the exact JSX payload that triggered the bug.
            try {
                window.parent.__lastBadJsx     = rawSource;
                window.parent.__lastBadLen     = rawSource.length;
                window.parent.__lastBadMsg     = tmsg;
                window.parent.__lastBadFrameId = '${chartId}';
                window.parent.__lastBadFences  = __babelFences;
                window.parent.__lastIdShadowFixRenames = __idShadowFixRenames;
                window.parent.__lastIdShadowFixApplied = __idShadowFixApplied;
                console.error('[REACT_RENDERER_DIAG] Captured failing JSX on window.parent.__lastBadJsx — length:',
                    rawSource.length, 'preview:', rawSource.slice(0, 200));
                console.error('[REACT_RENDERER_DIAG] Babel fence results at throw:',
                    JSON.stringify(__babelFences, null, 2));
            } catch (_) { /* parent unreachable (srcdoc sandbox) */ }
            // DIAGNOSTIC v8 (2026-07-26): cross-origin-safe postMessage mirror
            // of the failing-source capture above. The window.parent.X writes
            // silently fail in srcdoc iframes; postMessage does not.
            // v9 (2026-07-29): include idShadowFixApplied/Renames so the parent
            // can surface the F5 outcome in the diag kebab even if Babel throws
            // *after* F5 rewrote the source.
            try {
                window.parent.postMessage({
                    type: 'react-render-babel-error',
                    id: '${chartId}',
                    rawSource: rawSource,
                    rawSourceLen: rawSource.length,
                    errorMessage: tmsg,
                    babelFences: __babelFences.slice(),
                    idShadowFixApplied: typeof __idShadowFixApplied === 'boolean' ? __idShadowFixApplied : false,
                    idShadowFixRenames: typeof __idShadowFixRenames === 'number' ? __idShadowFixRenames : 0
                }, '*');
            } catch (_) {}
            return;
        }

        // ── Identifier hoist (moved here from before F3 on 2026-07-23) ───────
        // The IIFE lifts every PascalCase identifier the user references
        // (BarChart, Briefcase, etc.) onto window so the transformed source
        // can call them without an explicit prefix. It MUST run AFTER
        // Babel.transform — running it before corrupted Babel's
        // makeWeakCache plugin cache (the F3 fence caught this as
        // "TypeError: e.get is not a function" at babel.min.js:1:925003).
        // Babel's syntax pass doesn't need window.BarChart, but the
        // executed code does — hence the placement between the transform
        // success and the classic-<script> append.
        //
        // ROLLBACK (added 2026-07-26, see bug-findings H3): the hoist
        // writes to window[name] for each detected identifier; if it
        // throws mid-loop, the iframe is left in a half-rendered state
        // where some identifiers are present and others are not. Snapshot
        // the pre-hoist window state so we can restore on failure.
        var __preHoistRecharts = window.Recharts;
        var __preHoistLucide = window.lucide;
        var __preHoistKeys = {};
        for (var __kk in window) {
            if (Object.prototype.hasOwnProperty.call(window, __kk) && /^[A-Z]/.test(__kk)) {
                __preHoistKeys[__kk] = window[__kk];
            }
        }
        try {
${identifierHoist}
        } catch (hoistErr) {
            // Restore any PascalCase key the hoist may have touched.
            // Keys that existed before the hoist get their prior value
            // back; keys the hoist created (not in pre-snapshot) get
            // deleted.
            var __rollbackKeys = [];
            for (var __jj in window) {
                if (Object.prototype.hasOwnProperty.call(window, __jj) && /^[A-Z]/.test(__jj)) {
                    __rollbackKeys.push(__jj);
                }
            }
            for (var __i = 0; __i < __rollbackKeys.length; __i++) {
                var __kk = __rollbackKeys[__i];
                if (Object.prototype.hasOwnProperty.call(__preHoistKeys, __kk)) {
                    window[__kk] = __preHoistKeys[__kk];
                } else {
                    try { delete window[__kk]; } catch (_) {}
                }
            }
            window.Recharts = __preHoistRecharts;
            window.lucide = __preHoistLucide;
            console.warn('[REACT_RENDERER] identifier hoist failed (best-effort, rolled back):', hoistErr);
        }

        // Run the transformed code in a fresh classic <script> so top-level
        // 'function App()' declarations land on window for auto-mount.
        //
        // SAFETY NET (added 2026-07-26, see bug-findings H1): V8 fires
        // parse errors on an appended <script> as an 'error' event, NOT an
        // exception — the catch below could not see them, leaving the iframe
        // blank. Two layers prevent that:
        //   (1) Pre-parse with 'new Function(out)' so the parse error fires
        //       as a regular exception BEFORE the append, paints a
        //       diagnostic in the iframe, and posts
        //       'react-render-script-error' to the parent diag-sink.
        //   (2) Backup script.onerror for the rare case where the two
        //       parsers disagree (strict-mode-only constructs, top-level
        //       await, etc.).
        try {
            try {
                new Function(out);
            } catch (parseErr) {
                var pmsg = (parseErr && parseErr.message)
                    ? parseErr.message : String(parseErr);
                try {
                    window.parent.postMessage({
                        type: 'react-render-script-error',
                        id: '${chartId}',
                        source: 'pre-parse',
                        message: pmsg,
                        outTail: out.slice(Math.max(0, out.length - 2000))
                    }, '*');
                } catch (_) {}
                var styleP = 'color:#b91c1c;background:#fef2f2;padding:16px;'
                    + 'border-radius:8px;white-space:pre-wrap;'
                    + 'font-family:ui-monospace,monospace;font-size:13px;'
                    + 'line-height:1.5;border:1px solid #fecaca;';
                (document.getElementById('root') || document.body).innerHTML =
                    '<pre style="' + styleP + '">'
                    + '⚠ JSX parse error after transform:'
                    + String.fromCharCode(10) + String.fromCharCode(10)
                    + pmsg
                    + '</pre>';
                window.parent.postMessage({ type: 'iframe-resize', id: '${chartId}', height: 400 }, '*');
                console.error('[REACT_RENDERER] pre-parse failed:', parseErr);
                return;
            }
            var s = document.createElement('script');
            s.onerror = function (parseErr) {
                var smsg = String((parseErr && parseErr.message) || parseErr || 'unknown');
                try {
                    window.parent.postMessage({
                        type: 'react-render-script-error',
                        id: '${chartId}',
                        source: 'script-onerror',
                        message: smsg
                    }, '*');
                } catch (_) {}
                try {
                    var styleS = 'color:#b91c1c;background:#fef2f2;padding:16px;'
                        + 'border-radius:8px;white-space:pre-wrap;'
                        + 'font-family:ui-monospace,monospace;font-size:13px;'
                        + 'line-height:1.5;border:1px solid #fecaca;';
                    (document.getElementById('root') || document.body).innerHTML =
                        '<pre style="' + styleS + '">'
                        + '⚠ Inline script failed to execute:'
                        + String.fromCharCode(10) + String.fromCharCode(10)
                        + smsg
                        + '</pre>';
                    window.parent.postMessage({ type: 'iframe-resize', id: '${chartId}', height: 400 }, '*');
                } catch (_) {}
            };
            s.textContent = out;
            document.body.appendChild(s);
        } catch (runErr) {
            var rmsg = (runErr && runErr.message)
                ? runErr.message : String(runErr);
            var styleB = 'color:#b91c1c;background:#fef2f2;padding:16px;'
                + 'border-radius:8px;white-space:pre-wrap;'
                + 'font-family:ui-monospace,monospace;font-size:13px;'
                + 'line-height:1.5;border:1px solid #fecaca;';
            (document.getElementById('root') || document.body).innerHTML =
                '<pre style="' + styleB + '">'
                + '⚠ JSX execution error:'
                + String.fromCharCode(10) + String.fromCharCode(10)
                + rmsg
                + '</pre>';
            window.parent.postMessage({ type: 'iframe-resize', id: '${chartId}', height: 400 }, '*');
            console.error('[REACT_RENDERER] iframe execution error:', runErr);
            return;
        }

        // ── POST-EXECUTION SNAPSHOT (added 2026-07-23) ──────────────────────
        // The class of bug we're hunting right now is "Babel.transform
        // succeeded, no console.error, but the iframe is blank". That's a
        // happy-path failure that the existing catch blocks can't see
        // because nothing throws. Capture the full runtime state at the
        // handoff to auto-mount so the parent console can show where things
        // silently went wrong (missing root component, Tailwind absent,
        // Recharts/hooks not on window, etc.).
        try {
            var rootElSnap = document.getElementById('root');
            var tailwindEl = document.querySelector('script[src*="tailwindcss"]');
            // The Tailwind PLAY CDN (cdn.tailwindcss.com) injects styles into a
            // bare <style type="text/css"> element with NO [data-tailwind] or
            // [id="__tw_style__"] marker (those markers are only added by some
            // build-step / PostCSS toolchains, NOT the runtime CDN we ship
            // here). The reliable detection is to look for a <style> whose
            // text contains a Tailwind utility class definition like
            // .bg-blue-500 or .flex { display: flex }. Fixed 2026-07-27:
            // the previous selector returned false-negatives every render,
            // making the dashboard "Tailwind absent" reading misleading.
            var allStyleEls = document.querySelectorAll('style');
            var tailwindRuntimeStyle = Array.prototype.filter.call(
                allStyleEls,
                function (s) { return /\.bg-(?:blue|red|emerald|slate|white|black)-\d|\.flex\b|\.grid\b|\.rounded\b|\.shadow\b/.test(s.textContent || ''); }
            ).length;
            var snap = {
                rawSourceLen:      typeof rawSource === 'string' ? rawSource.length : null,
                rawSourceFirst4k:  typeof rawSource === 'string' ? rawSource.slice(0, 4000) : null,
                rawSourceTail4k:   typeof rawSource === 'string' ? rawSource.slice(Math.max(0, rawSource.length - 4000)) : null,
                outLen:            typeof out       === 'string' ? out.length       : null,
                hasReact:       typeof window.React,
                hasReactDOM:    typeof window.ReactDOM,
                hasReactCpt:    typeof window.Component,
                hasReactMemo:   typeof window.memo,
                hasFragment:    typeof window.Fragment,
                hasUseState:    typeof window.useState,
                hasUseEffect:   typeof window.useEffect,
                hasUseMemo:     typeof window.useMemo,
                hasUseCallback: typeof window.useCallback,
                hasUseRef:      typeof window.useRef,
                hasRecharts:    typeof window.Recharts,
                hasLucide:      typeof window.lucide,
                hasApp:         typeof window.App,
                hasComponent:   typeof window.Component,
                hasDashboard:   typeof window.Dashboard,
                hasBarChart:    typeof window.BarChart,
                hasLineChart:   typeof window.LineChart,
                hasPieChart:    typeof window.PieChart,
                hasScatter:     typeof window.ScatterChart,
                hasResponsive:  typeof window.ResponsiveContainer,
                hasBriefcase:   typeof window.Briefcase,
                hasDollarSign:  typeof window.DollarSign,
                hasTarget:      typeof window.Target,
                hasUsers:       typeof window.Users,
                hasWallet:      typeof window.Wallet,
                hasCreditCard:  typeof window.CreditCard,
                // Identity-vs-Recharts check (Round 5 follow-up; cf. §14.9 of
                // REACT_RENDERER_LUCIDE_TROUBLESHOOTING_2026-07-22.md).
                // The hasX fields above only check typeof — a wrapped
                // makeIconComponent('PieChart', lucideArray) is also a
                // function, so the snapshot would lie. The identity check
                // is the only signal that distinguishes the wrapped Lucide
                // icon from the real Recharts component. For each priority
                // name we record whether window[name] is the SAME function
                // reference as window.Recharts[name]. A clashCount > 0 with
                // the hasX fields all "function" is the signature of the
                // Lucide-vs-Recharts name collision — mirror the priority
                // list with RECHARTS_PRIORITY_NAMES at line 738 if you
                // add a new colliding name here.
                identityClashReport: (function () {
                    var names = ${JSON.stringify(RECHARTS_PRIORITY_NAMES)};
                    var r = window.Recharts || {};
                    var rows = [];
                    var clashCount = 0;
                    for (var i = 0; i < names.length; i++) {
                        var n = names[i];
                        var wn = window[n];
                        var rn = r[n];
                        var sameRef = (wn === rn);
                        var hasFn = (typeof wn === 'function');
                        if (hasFn && !sameRef) clashCount++;
                        rows.push({ name: n, hasFn: hasFn, matchesRecharts: sameRef });
                    }
                    return { clashCount: clashCount, total: names.length, rows: rows };
                })(),
                tailwindLoaded: !!tailwindEl,
                tailwindStyleInjected: !!tailwindRuntimeStyle,
                rootElExists:   !!rootElSnap,
                rootElChildren: rootElSnap ? rootElSnap.childElementCount : -1,
                bodyChildren:   document.body.childElementCount,
                docTitle:       document.title,
                fencesSummary:  __babelFences.map(function (f) {
                    return f.label.split(' — ')[0] + '=' + (f.ok ? 'OK' : 'FAIL');
                }).join(', ')
            };
            console.log('[REACT_RENDERER_DIAG] post-exec snapshot:', JSON.stringify(snap, null, 2));
            try {
                window.parent.__lastExecSnap   = snap;
                window.parent.__lastExecSnapId = '${chartId}';
            } catch (_) {}
            try {
                window.parent.postMessage({
                    type: 'react-render-snapshot',
                    id:   '${chartId}',
                    snap: snap
                }, '*');
            } catch (_) {}
        } catch (_) { /* snapshot is best-effort, never throws */ }

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

                        // Graceful fallback: detect the known Recharts internal
                        // bug 't.has is not a function' thrown when the source
                        // uses <ComposedChart> with multiple YAxes. This is a
                        // real Recharts bug (verified by greping the deployed
                        // bundle at offsets 121494 / 122031 / 122831 on
                        // 2026-07-24) — Recharts' class vn / class On
                        // internal Map extension dereferences a missing
                        // _intern slot during domain merging. Show the user a
                        // yellow hint panel explaining the workaround instead
                        // of the raw red stack trace.
                        var isRechartsComposedBug =
                            (typeof msg === 'string')
                            && (msg.indexOf('t.has is not a function') !== -1)
                            && (typeof rawSource === 'string')
                            && (rawSource.indexOf('ComposedChart') !== -1);

                        // Companion Recharts-internal bug: "a.set is not a function"
                        // thrown from react-dom.production.min.js:85 inside function d()
                        // (the child-map builder mapIntoArray). Reproduces for ANY
                        // Recharts chart in the patched bundle — verified 2026-07-26
                        // with a single BarChart/Bar pattern (no ComposedChart, no
                        // multiple YAxes). Root cause is the same class of bug as
                        // t.has: a Recharts internal Map extension dereferences a
                        // missing _intern slot. Show the same yellow hint panel so
                        // the user gets an actionable message instead of a raw red
                        // stack trace.
                        var isRechartsSetBug =
                            (typeof msg === 'string')
                            && (msg.indexOf('a.set is not a function') !== -1)
                            && (typeof rawSource === 'string')
                            && rawSource.indexOf('Recharts.') !== -1;

                        if (isRechartsComposedBug || isRechartsSetBug) {
                            var headerTitle = isRechartsComposedBug
                                ? '⚠ ComposedChart with multiple YAxes hit a Recharts internal bug'
                                : '⚠ Recharts internal bug in the patched bundle';
                            var bodyText = isRechartsComposedBug
                                ? 'The chart pattern using <ComposedChart> with dual YAxes plus Area/Bar/Line children triggered t.has is not a function inside Recharts domain merging (verified on Recharts.js:2:121494).'
                                : 'The patched Recharts bundle threw "a.set is not a function" from react-dom.production.min.js:85 inside the child-map builder. This is the same class of bug as t.has — a Recharts internal Map extension dereferences a missing _intern slot during render. Verified 2026-07-26 with a single <BarChart><Bar/></BarChart> pattern (no ComposedChart).';
                            return window.React.createElement('div', {
                                style: {
                                    color: '#92400e',
                                    background: '#fffbeb',
                                    padding: '20px',
                                    borderRadius: '10px',
                                    border: '1px solid #fde68a',
                                    margin: '16px',
                                    fontFamily: 'system-ui,-apple-system,Segoe UI,sans-serif',
                                    lineHeight: '1.5'
                                }
                            }, [
                                window.React.createElement('div', {
                                    key: 'h',
                                    style: { fontSize: '15px', fontWeight: 600, marginBottom: '12px' }
                                }, headerTitle),
                                window.React.createElement('div', {
                                    key: 'p1',
                                    style: { fontSize: '13px', marginBottom: '10px' }
                                }, bodyText),
                                window.React.createElement('div', {
                                    key: 'p2',
                                    style: { fontSize: '13px', marginBottom: '6px', fontWeight: 600 }
                                }, 'Workaround'),
                                window.React.createElement('div', {
                                    key: 'p3',
                                    style: { fontSize: '13px', marginBottom: '6px' }
                                }, 'Ask for the dashboard as separate single-axis charts, e.g.'),
                                window.React.createElement('pre', {
                                    key: 'p4',
                                    style: {
                                        background: '#fef3c7',
                                        padding: '10px',
                                        borderRadius: '6px',
                                        fontSize: '12px',
                                        fontFamily: 'ui-monospace,monospace',
                                        margin: '8px 0 12px 0',
                                        whiteSpace: 'pre-wrap'
                                    }
                                }, '"Build 3 side-by-side charts: revenue as a LineChart (single YAxis, left), users as a BarChart (single YAxis, middle), conversion as a LineChart (single YAxis, right)."'),
                                window.React.createElement('div', {
                                    key: 'p5',
                                    style: { fontSize: '12px', color: '#78350f' }
                                }, 'This is a known issue in the self-hosted Recharts.js bundle (UI/visualisation_engine/libs/Recharts.js). Workaround: use plain HTML/CSS/SVG charts, or regenerate the visualisation without Recharts. See ARCHIVE_CLEANUP / TRACKER for the open ticket on Recharts runtime bugs.'),
                                window.React.createElement('details', {
                                    key: 'p6',
                                    style: { fontSize: '11px', marginTop: '10px', color: '#78350f' }
                                }, [
                                    window.React.createElement('summary', { key: 's' }, 'Show raw error'),
                                    window.React.createElement('pre', {
                                        key: 'e',
                                        style: {
                                            background: '#fff7ed',
                                            padding: '8px',
                                            borderRadius: '4px',
                                            marginTop: '6px',
                                            whiteSpace: 'pre-wrap',
                                            fontFamily: 'ui-monospace,monospace',
                                            fontSize: '11px'
                                        }
                                    }, msg)
                                ])
                            ]);
                        }

                        // Graceful fallback: a second flavour of the same
                        // underlying Recharts instability. When a Logical-
                        // Expression JSX child of <ComposedChart> slips past
                        // the logicalToConditionalPlugin (e.g. an Identifier
                        // component reference, a CallExpression returning
                        // JSX, or a nested LogicalExpression on the right
                        // that Babel's post-order traversal rewrote but did
                        // not recurse into), React inserts a "false"
                        // placeholder fiber into the child list. Recharts'
                        // axis registry corrupts, and the resulting throw
                        // surfaces inside React's own commit phase as
                        // "a.set is not a function" at
                        // react-dom.production.min.js:85. Show the same
                        // yellow ComposedChart hint panel so the user gets a
                        // coherent workaround message instead of a raw stack.
                        var isRechartsRenderPhaseBug =
                            (typeof msg === 'string')
                            && (msg.indexOf('a.set is not a function') !== -1)
                            && (typeof rawSource === 'string')
                            && (rawSource.indexOf('ComposedChart') !== -1);

                        if (isRechartsRenderPhaseBug) {
                            return window.React.createElement('div', {
                                style: {
                                    color: '#92400e',
                                    background: '#fffbeb',
                                    padding: '20px',
                                    borderRadius: '10px',
                                    border: '1px solid #fde68a',
                                    margin: '16px',
                                    fontFamily: 'system-ui,-apple-system,Segoe UI,sans-serif',
                                    lineHeight: '1.5'
                                }
                            }, [
                                window.React.createElement('div', {
                                    key: 'h',
                                    style: { fontSize: '15px', fontWeight: 600, marginBottom: '12px' }
                                }, '⚠ ComposedChart hit a React commit-phase bug from a Recharts fiber corruption'),
                                window.React.createElement('div', {
                                    key: 'p1',
                                    style: { fontSize: '13px', marginBottom: '10px' }
                                }, 'The chart triggered "a.set is not a function" inside React\\\'s commit phase (react-dom.production.min.js:85). This is the same family of Recharts internal-bug crashes as the yellow ComposedChart panel below: a LogicalExpression JSX child of <ComposedChart> (e.g. {cond && ComponentRef}) was not rewritten to a conditional in time, the falsy branch produced a placeholder fiber, and Recharts\\\' axis registry corrupted on first mount.'),
                                window.React.createElement('div', {
                                    key: 'p2',
                                    style: { fontSize: '13px', marginBottom: '6px', fontWeight: 600 }
                                }, 'Workaround'),
                                window.React.createElement('div', {
                                    key: 'p3',
                                    style: { fontSize: '13px', marginBottom: '6px' }
                                }, 'Rewrite any "cond && Component" patterns inside <ComposedChart> as explicit conditionals, or ask for separate single-axis charts:'),
                                window.React.createElement('pre', {
                                    key: 'p4',
                                    style: {
                                        background: '#fef3c7',
                                        padding: '10px',
                                        borderRadius: '6px',
                                        fontSize: '12px',
                                        fontFamily: 'ui-monospace,monospace',
                                        margin: '8px 0 12px 0',
                                        whiteSpace: 'pre-wrap'
                                    }
                                }, '// Instead of:\\n{showLegend && <Legend />}\\n// Use:\\n{showLegend ? <Legend /> : null}\\n\\n// Or split into side-by-side single-axis charts.'),
                                window.React.createElement('div', {
                                    key: 'p5',
                                    style: { fontSize: '12px', color: '#78350f' }
                                }, 'Single-axis LineChart / BarChart / PieChart already render correctly here. Only ComposedChart-with-LogicalExpression-children is blocked.'),
                                window.React.createElement('details', {
                                    key: 'p6',
                                    style: { fontSize: '11px', marginTop: '10px', color: '#78350f' }
                                }, [
                                    window.React.createElement('summary', { key: 's' }, 'Show raw error'),
                                    window.React.createElement('pre', {
                                        key: 'e',
                                        style: {
                                            background: '#fff7ed',
                                            padding: '8px',
                                            borderRadius: '4px',
                                            marginTop: '6px',
                                            whiteSpace: 'pre-wrap',
                                            fontFamily: 'ui-monospace,monospace',
                                            fontSize: '11px'
                                        }
                                    }, msg)
                                ])
                            ]);
                        }

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
                        // Capture the source that caused this runtime error so the
                        // parent console can inspect it without rerunning the
                        // chart. Mirrors the __lastBadJsx pattern for Babel
                        // failures (see line ~649) so the diagnostic can pick up
                        // either path with the same DevTools query.
                        try {
                            window.parent.__lastFailingSource     = (typeof rawSource === 'string') ? rawSource.slice(0, 4000) : null;
                            window.parent.__lastFailingSourceLen  = (typeof rawSource === 'string') ? rawSource.length      : null;
                            window.parent.__lastFailingSourceId   = '${chartId}';
                        } catch (_) {}
                        window.parent.postMessage({
                            type: 'react-render-error',
                            id: '${chartId}',
                            message: (err && err.message) ? err.message : String(err),
                            stack: (err && err.stack) ? err.stack : '',
                            rawSource: (typeof rawSource === 'string') ? rawSource.slice(0, 4000) : null,
                            rawSourceLen: (typeof rawSource === 'string') ? rawSource.length : null
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
            (document.getElementById('root') || document.body).innerHTML =
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

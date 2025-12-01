(function () {
    // Diagnostic script loader - ensures key modal and integration scripts are loaded with cache-busting
    const importantScripts = [
        'modules_internal/workflow/workflow-link-modal.js',
        'modules_internal/workflow/workflow-thread-integration.js',
        'modules_internal/automation/automation-link-modal.js',
        'modules_internal/automation-workflows/automation-thread-integration.js',
        'modules_internal/internal-docs/internal-docs-link-modal.js',
        'modules_internal/internal_docs/docs-thread-integration.js',
        'modules_internal/thread-manager/thread-manager-workflows.js'
    ];

    function log(msg, ...args) {
        try { console.log('[ScriptLoaderDiag] ' + msg, ...args); } catch (e) { }
    }

    // Expose check function
    window.ScriptLoaderDiagnostics = window.ScriptLoaderDiagnostics || {
        check: function () {
            log('Running script presence check...');
            importantScripts.forEach(src => {
                const loaded = Array.from(document.scripts).some(s => s.src && s.src.indexOf(src) !== -1);
                log(src + ' ->', loaded ? 'LOADED' : 'MISSING');
            });
        },
        ensure: function () {
            // Ensure missing scripts are injected with cache-bust
            importantScripts.forEach(src => {
                const already = Array.from(document.scripts).some(s => s.src && s.src.indexOf(src) !== -1);
                if (!already) {
                    try {
                        const s = document.createElement('script');
                        s.src = src + '?_cb=' + Date.now();
                        s.onload = () => log('Injected and loaded:', src);
                        s.onerror = (e) => log('Failed to load injected script:', src, e);
                        document.head.appendChild(s);
                        log('Injected (cache-busted):', src);
                    } catch (e) {
                        log('Exception injecting script:', src, e);
                    }
                }
            });
        },
        listLoaded: function () {
            return Array.from(document.scripts).map(s => ({ src: s.src || '', async: !!s.async, defer: !!s.defer }));
        }
    };

    // Auto-run a quick check on load (non-blocking)
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setTimeout(() => {
            window.ScriptLoaderDiagnostics.check();
        }, 50);
    } else {
        document.addEventListener('DOMContentLoaded', () => setTimeout(() => window.ScriptLoaderDiagnostics.check(), 50));
    }

    log('Script loader diagnostics installed. Use window.ScriptLoaderDiagnostics.check() and .ensure()');
})();

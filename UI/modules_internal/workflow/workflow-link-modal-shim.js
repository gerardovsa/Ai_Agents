(function () {
    // Shim to ensure a global WorkflowLinkModal wrapper exists early
    window.WorkflowLinkModal = window.WorkflowLinkModal || {
        open: function (threadId) {
            window.__modalCallQueue = window.__modalCallQueue || [];
            window.__modalCallQueue.push({ method: 'openWorkflowLinkModal', args: [threadId] });
            // Start polling flush in case modal definitions become available later
            if (!window.__modalCallQueue._polling) {
                window.__modalCallQueue._polling = true;
                const poll = setInterval(() => {
                    if (typeof ThreadManager !== 'undefined' && typeof ThreadManager.openWorkflowLinkModal === 'function') {
                        try {
                            while (window.__modalCallQueue.length > 0) {
                                const job = window.__modalCallQueue.shift();
                                if (typeof ThreadManager[job.method] === 'function') {
                                    ThreadManager[job.method].apply(ThreadManager, job.args);
                                }
                            }
                        } catch (e) {
                            console.error('[WorkflowLinkModalShim] Error flushing queue', e);
                        }
                        clearInterval(poll);
                        window.__modalCallQueue._polling = false;
                    }
                }, 200);
            }
        }
    };

    // If the modal script was executed early and returned (because ThreadManager wasn't ready),
    // we need to reload it once ThreadManager becomes available so the real implementations are registered.
    if (typeof ThreadManager === 'undefined') {
        // Watch for ThreadManager to be defined, then inject the real modal script (cache-busted)
        let attempts = 0;
        const maxAttempts = 60; // ~12s
        const watcher = setInterval(() => {
            attempts++;
            if (typeof ThreadManager !== 'undefined') {
                clearInterval(watcher);
                try {
                    const script = document.createElement('script');
                    script.src = 'modules_internal/workflow/workflow-link-modal.js?v=' + Date.now();
                    script.onload = function () {
                        console.log('[WorkflowLinkModalShim] Injected workflow-link-modal.js after ThreadManager became available');
                        // Flush any queued calls (the modal's own wrapper or ThreadManager methods may handle this too)
                        if (window.__modalCallQueue && window.__modalCallQueue.length > 0) {
                            try {
                                while (window.__modalCallQueue.length > 0) {
                                    const job = window.__modalCallQueue.shift();
                                    if (typeof ThreadManager[job.method] === 'function') {
                                        ThreadManager[job.method].apply(ThreadManager, job.args);
                                    }
                                }
                            } catch (e) {
                                console.error('[WorkflowLinkModalShim] Error flushing queue after script load', e);
                            }
                        }
                    };
                    script.onerror = function (e) {
                        console.error('[WorkflowLinkModalShim] Failed to load workflow-link-modal.js after injecting', e);
                    };
                    document.head.appendChild(script);
                } catch (e) {
                    console.error('[WorkflowLinkModalShim] Exception injecting modal script', e);
                }
                return;
            }

            if (attempts >= maxAttempts) {
                clearInterval(watcher);
                console.warn('[WorkflowLinkModalShim] ThreadManager did not appear within timeout; modal definitions may be missing');
            }
        }, 200);
    }
})();

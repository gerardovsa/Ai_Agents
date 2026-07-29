/**
 * FILE:    UI/modules_internal/visualizations/visualizations-module.js
 * PURPOSE: Gallery for the user's saved AI-rendered React visualizations.
 *          Binds to the existing `tab-analytics` stub (formerly "Analytics
 *          content coming soon..."). Lets the user browse, search, filter by
 *          tag, and re-mount any saved viz with the Tier-1 toolbar intact.
 *
 * PATTERN: ES-module export `{onDashboardLoad, onDashboardUnload}`. The host
 *          page (business-ai-platform-v2.html) lazy-imports this file the
 *          first time the user clicks the `data-tab="analytics"` button.
 *          Same convention as vsa-veterinary-alerts / woocommerce-v4 modules.
 *
 * DEPENDENCIES:
 *   - window.vizEngine         (Tier-1 toolbar + addIframeActionBar)
 *   - window.ReactRenderer     (buildReactSrcdoc for re-mount)
 *   - window.showToast         (notifications; falls back to console)
 *   - window.AuthToken / localStorage.getItem('authToken') (Bearer)
 *
 * API USED (Flask routes added in migration 057 + 058):
 *   - GET    /api/viz/snapshots/?mine=true&limit=100      summaries
 *   - GET    /api/viz/snapshots/<id>                     full record (jsx_source)
 *   - DELETE /api/viz/snapshots/<id>                     owner-only soft delete
 *
 * RELATED FILES:
 *   - AI_infrastructure/routes/viz_snapshots_routes.py
 *   - tools/implementations/viz_snapshots.py             AI tool wrappers
 *   - UI/visualisation_engine/react_renderer.js          srcdoc builder
 *   - UI/visualisation_engine/visualisation_v3.js        Tier-1 toolbar
 *
 * LAST MODIFIED: 2026-07-22
 */

const STYLE_ID = 'viz-gallery-styles';

function injectStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = `
        /* ===== Visualizations gallery ===== */
        .viz-gallery-toolbar {
            display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-3, 12px);
            margin: var(--space-5, 24px) 0 var(--space-4, 16px) 0;
        }
        .viz-gallery-search {
            flex: 1 1 220px; min-width: 200px;
            padding: 8px 12px;
            background: var(--bg-secondary, #1e1e2e);
            border: 1px solid var(--border-default, #30363d);
            border-radius: 8px;
            color: var(--text-primary, #f3f4f6);
            font: inherit;
        }
        .viz-gallery-search:focus { outline: none; border-color: var(--accent-primary, #58a6ff); box-shadow: 0 0 0 3px rgba(88,166,255,0.1); }
        .viz-gallery-tags {
            display: flex; flex-wrap: wrap; gap: 6px;
        }
        .viz-gallery-tag {
            padding: 4px 10px; border-radius: 999px; font-size: 12px;
            background: var(--bg-secondary, #1e1e2e);
            border: 1px solid var(--border-default, #30363d);
            color: var(--text-secondary, #d1d5db);
            cursor: pointer; user-select: none;
        }
        .viz-gallery-tag[aria-pressed="true"] {
            background: rgba(88,166,255,0.18); color: var(--accent-primary, #58a6ff); border-color: var(--accent-primary, #58a6ff);
        }
        .viz-gallery-new {
            padding: 8px 14px;
            background: var(--accent-primary, #58a6ff); color: #fff;
            border: 0; border-radius: 8px; font: inherit;
            cursor: pointer;
        }
        .viz-gallery-new:hover { filter: brightness(1.1); }
        .viz-gallery-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: var(--space-4, 16px);
        }
        .viz-gallery-card {
            display: flex; flex-direction: column;
            background: var(--bg-secondary, #1e1e2e);
            border: 1px solid var(--border-default, #30363d);
            border-radius: 12px; overflow: hidden;
            cursor: pointer;
            transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
        }
        .viz-gallery-card:hover {
            transform: translateY(-2px);
            border-color: var(--accent-primary, #58a6ff);
            box-shadow: 0 8px 24px rgba(0,0,0,0.35);
        }
        .viz-gallery-thumb {
            aspect-ratio: 16 / 10;
            background: linear-gradient(135deg, rgba(88,166,255,0.10), rgba(63,185,80,0.10));
            display: flex; align-items: center; justify-content: center;
            font-size: 42px; color: var(--text-secondary, #d1d5db);
        }
        .viz-gallery-thumb img { width: 100%; height: 100%; object-fit: cover; }
        .viz-gallery-card-body { padding: var(--space-3, 12px) var(--space-4, 16px); }
        .viz-gallery-card-title {
            font-weight: 600; color: var(--text-primary, #f3f4f6);
            margin: 0 0 4px 0; line-height: 1.3;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
        }
        .viz-gallery-card-meta {
            font-size: 12px; color: var(--text-secondary, #d1d5db);
            display: flex; gap: 8px; flex-wrap: wrap; align-items: center;
        }
        .viz-gallery-card-tags {
            margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px;
        }
        .viz-gallery-card-tag {
            font-size: 11px; padding: 2px 6px;
            background: rgba(88,166,255,0.12); color: var(--accent-primary, #58a6ff);
            border-radius: 4px;
        }
        .viz-gallery-empty {
            grid-column: 1 / -1;
            padding: 48px 24px; text-align: center;
            color: var(--text-secondary, #d1d5db);
        }
        .viz-gallery-empty .icon { font-size: 48px; margin-bottom: var(--space-4, 16px); display: block; opacity: 0.55; }
        .viz-gallery-error {
            padding: 16px; border-radius: 8px;
            background: rgba(248,81,73,0.12); color: var(--accent-error, #f85149);
            border: 1px solid rgba(248,81,73,0.3);
        }
        /* Re-mount modal */
        .viz-gallery-modal {
            position: fixed; inset: 0;
            background: rgba(0,0,0,0.65);
            display: flex; align-items: center; justify-content: center;
            z-index: 10000;
        }
        .viz-gallery-modal .modal-inner {
            background: var(--bg-primary, #0d1117);
            border: 1px solid var(--border-default, #30363d);
            border-radius: 12px;
            width: min(960px, 95vw);
            max-height: 92vh;
            display: flex; flex-direction: column;
            overflow: hidden;
        }
        .viz-gallery-modal .modal-header {
            display: flex; align-items: center; gap: var(--space-3, 12px);
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-default, #30363d);
        }
        .viz-gallery-modal .modal-title {
            flex: 1; font-weight: 600; color: var(--text-primary, #f3f4f6);
            margin: 0;
        }
        .viz-gallery-modal .modal-close {
            background: transparent; color: var(--text-secondary, #d1d5db);
            border: 0; padding: 4px 8px; cursor: pointer; font-size: 18px;
        }
        .viz-gallery-modal .modal-body {
            padding: var(--space-4, 16px); overflow: auto;
            background: var(--bg-secondary, #161b22);
        }
        .viz-gallery-modal .modal-body .viz-container {
            margin-top: 0 !important;
        }
    `;
    document.head.appendChild(style);
}

function getToken() {
    try {
        return (localStorage.getItem('authToken') || sessionStorage.getItem('authToken') || '').trim();
    } catch (_) {
        return '';
    }
}

function toast(message, type = 'info') {
    try {
        if (typeof window.showToast === 'function') { window.showToast(message, type); return; }
    } catch (_) { /* fall through */ }
    // eslint-disable-next-line no-console
    console.log(`[viz-gallery] (${type}) ${message}`);
}

async function apiListSnapshots(params = {}) {
    const url = new URL('/api/viz/snapshots/', window.location.origin);
    url.searchParams.set('mine', 'true');
    url.searchParams.set('limit', String(params.limit || 100));
    if (params.q) url.searchParams.set('q', params.q);
    if (params.tag) url.searchParams.set('tag', params.tag);
    const token = getToken();
    const resp = await fetch(url.toString(), {
        headers: { 'Authorization': token ? `Bearer ${token}` : '' },
    });
    if (!resp.ok) {
        const text = await resp.text().catch(() => '');
        throw new Error(`List failed (${resp.status}): ${text.slice(0, 160)}`);
    }
    const body = await resp.json();
    return body.snapshots || [];
}

async function apiGetSnapshot(id) {
    const token = getToken();
    const resp = await fetch(`/api/viz/snapshots/${encodeURIComponent(id)}`, {
        headers: { 'Authorization': token ? `Bearer ${token}` : '' },
    });
    if (!resp.ok) {
        const text = await resp.text().catch(() => '');
        throw new Error(`Get failed (${resp.status}): ${text.slice(0, 160)}`);
    }
    const body = await resp.json();
    return body.snapshot;
}

async function apiDeleteSnapshot(id) {
    const token = getToken();
    const resp = await fetch(`/api/viz/snapshots/${encodeURIComponent(id)}`, {
        method: 'DELETE',
        headers: { 'Authorization': token ? `Bearer ${token}` : '' },
    });
    if (!resp.ok) {
        const text = await resp.text().catch(() => '');
        throw new Error(`Delete failed (${resp.status}): ${text.slice(0, 160)}`);
    }
    return resp.json().catch(() => ({}));
}

function relativeTime(iso) {
    if (!iso) return '';
    const then = new Date(iso).getTime();
    if (Number.isNaN(then)) return '';
    const diff = (Date.now() - then) / 1000;
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 86400 * 30) return `${Math.floor(diff / 86400)}d ago`;
    return new Date(iso).toLocaleDateString();
}

function escapeHtml(s) {
    return String(s == null ? '' : s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function renderCard(snap) {
    const tags = Array.isArray(snap.tags) ? snap.tags : [];
    const thumbHtml = snap.thumbnail_png
        ? `<img src="data:image/png;base64,${escapeHtml(snap.thumbnail_png)}" alt="${escapeHtml(snap.title)}" />`
        : `<span class="icon"><i class="fas fa-chart-area"></i></span>`;
    return `
        <div class="viz-gallery-card" data-snapshot-id="${escapeHtml(snap.id)}" tabindex="0" role="button">
            <div class="viz-gallery-thumb">${thumbHtml}</div>
            <div class="viz-gallery-card-body">
                <h3 class="viz-gallery-card-title">${escapeHtml(snap.title || 'Untitled')}</h3>
                <div class="viz-gallery-card-meta">
                    <span><i class="fas fa-clock"></i> ${escapeHtml(relativeTime(snap.updated_at || snap.created_at))}</span>
                    ${snap.thread_title ? `<span title="Linked thread"><i class="fas fa-comments"></i> ${escapeHtml(snap.thread_title)}</span>` : ''}
                    ${snap.synergy_session_id ? `<span title="Linked Synergy session"><i class="fas fa-link"></i> Synergy</span>` : ''}
                    ${snap.is_public ? `<span title="Public"><i class="fas fa-globe"></i> Public</span>` : ''}
                </div>
                ${tags.length ? `<div class="viz-gallery-card-tags">${tags.slice(0, 6).map((t) => `<span class="viz-gallery-card-tag">${escapeHtml(t)}</span>`).join('')}</div>` : ''}
            </div>
        </div>
    `;
}

function renderEmptyState() {
    return `
        <div class="viz-gallery-empty">
            <span class="icon"><i class="fas fa-chart-area"></i></span>
            <h3 style="margin: 0 0 8px 0; color: var(--text-primary, #f3f4f6);">No visualizations yet</h3>
            <p style="margin: 0 0 16px 0;">Ask the AI in chat to build a dashboard, then click the Tier-1 kebab in the chart's action bar and choose <strong>Save to library</strong>.</p>
        </div>
    `;
}

function renderErrorState(message) {
    return `<div class="viz-gallery-error"><i class="fas fa-exclamation-triangle"></i> ${escapeHtml(message)}</div>`;
}

/**
 * Build a modal that re-mounts the saved viz in a fresh iframe and wires
 * the existing Tier-1 toolbar (addIframeActionBar + addIframeTier1Toolbar).
 */
async function openVizModal(snapshotId, summary) {
    const modal = document.createElement('div');
    modal.className = 'viz-gallery-modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');

    const inner = document.createElement('div');
    inner.className = 'modal-inner';

    const header = document.createElement('div');
    header.className = 'modal-header';

    const title = document.createElement('h3');
    title.className = 'modal-title';
    title.textContent = (summary && summary.title) || 'Loading…';

    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'modal-close';
    deleteBtn.title = 'Delete snapshot';
    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
    deleteBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        if (!window.confirm('Delete this snapshot? (soft delete — recoverable by admin)')) return;
        try {
            await apiDeleteSnapshot(snapshotId);
            toast('Snapshot deleted', 'success');
            modal.remove();
            // Re-fetch the gallery
            const tab = document.getElementById('tab-analytics');
            if (tab && tab.__vizGalleryInstance) {
                tab.__vizGalleryInstance.refresh();
            }
        } catch (err) {
            toast(`Delete failed: ${err.message}`, 'error');
        }
    });

    const closeBtn = document.createElement('button');
    closeBtn.className = 'modal-close';
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.innerHTML = '<i class="fas fa-times"></i>';
    closeBtn.addEventListener('click', () => modal.remove());

    header.appendChild(title);
    header.appendChild(deleteBtn);
    header.appendChild(closeBtn);

    const body = document.createElement('div');
    body.className = 'modal-body';

    // Spinner while we fetch + mount.
    body.innerHTML = '<div style="padding:48px;text-align:center;color:var(--text-secondary);"><i class="fas fa-spinner fa-spin"></i> Loading visualization…</div>';

    inner.appendChild(header);
    inner.appendChild(body);
    modal.appendChild(inner);
    document.body.appendChild(modal);

    modal.addEventListener('click', (ev) => {
        if (ev.target === modal) modal.remove();
    });
    const onKey = (ev) => {
        if (ev.key === 'Escape') { modal.remove(); document.removeEventListener('keydown', onKey); }
    };
    document.addEventListener('keydown', onKey);

    try {
        const snap = await apiGetSnapshot(snapshotId);
        const chartId = `viz-${(snap.id || snapshotId).slice(0, 8)}`;
        const jsx = snap.jsx_source || '';

        if (!jsx) {
            body.innerHTML = renderErrorState('Snapshot has no JSX source. The original renderer was probably not captured.');
            return;
        }

        title.textContent = snap.title || 'Untitled';

        // Build a viz-container + content area + iframe, then mount the JSX.
        const container = document.createElement('div');
        container.className = 'viz-container react-container';
        container.setAttribute('data-viz-snapshot-id', snap.id);
        container.dataset.vizSnapshotId = snap.id;
        container.dataset.vizTitle = snap.title || '';

        const contentArea = document.createElement('div');
        contentArea.className = 'viz-content-area';

        const iframe = document.createElement('iframe');
        iframe.className = 'viz-iframe';
        iframe.setAttribute('sandbox', 'allow-scripts allow-forms allow-modals allow-pointer-lock allow-downloads');
        iframe.setAttribute('allow', 'clipboard-write');
        iframe.style.cssText = 'width:100%;min-height:480px;border:0;display:block;';

        // Use the existing ReactRenderer.buildReactSrcdoc if available.
        const ReactRenderer = window.ReactRenderer;
        if (!ReactRenderer || typeof ReactRenderer.buildReactSrcdoc !== 'function') {
            body.innerHTML = renderErrorState('ReactRenderer.buildReactSrcdoc not available — is the renderer loaded?');
            return;
        }
        iframe.srcdoc = ReactRenderer.buildReactSrcdoc(jsx, chartId);

        contentArea.appendChild(iframe);
        container.appendChild(contentArea);
        body.innerHTML = '';
        body.appendChild(container);

        // Wire the existing Tier-1 toolbar (panel + float + kebab).
        const vizEngine = window.vizEngine;
        if (vizEngine) {
            if (typeof vizEngine.addIframeActionBar === 'function') {
                vizEngine.addIframeActionBar(container, contentArea, chartId, 'Saved Visualization');
            }
            if (typeof vizEngine.addIframeTier1Toolbar === 'function') {
                const bar = container.querySelector('.viz-action-bar');
                const kebabBtn = bar ? bar.querySelector('.viz-tier1-trigger') : null;
                if (kebabBtn) vizEngine.addIframeTier1Toolbar(container, contentArea, chartId, iframe, kebabBtn);
            }
        }
    } catch (err) {
        body.innerHTML = renderErrorState(err.message || String(err));
    }
}

class VizGallery {
    constructor(tabEl) {
        this.tabEl = tabEl;
        this.snapshots = [];
        this.activeTag = '';
        this.search = '';
        tabEl.__vizGalleryInstance = this;
    }

    async load() {
        try {
            this.snapshots = await apiListSnapshots({ limit: 100 });
        } catch (err) {
            this.renderError(err.message || String(err));
            return;
        }
        this.render();
    }

    refresh() { this.load(); }

    allTags() {
        const set = new Set();
        this.snapshots.forEach((s) => Array.isArray(s.tags) && s.tags.forEach((t) => set.add(t)));
        return Array.from(set).sort();
    }

    filtered() {
        const q = this.search.trim().toLowerCase();
        return this.snapshots.filter((s) => {
            if (this.activeTag && !(Array.isArray(s.tags) && s.tags.includes(this.activeTag))) return false;
            if (!q) return true;
            const hay = `${s.title || ''} ${(s.tags || []).join(' ')} ${s.thread_title || ''}`.toLowerCase();
            return hay.includes(q);
        });
    }

    render() {
        const tags = this.allTags();
        const visible = this.filtered();

        const toolbarHtml = `
            <div class="viz-gallery-toolbar">
                <input class="viz-gallery-search" type="search" placeholder="Search visualizations by title or tag…" aria-label="Search visualizations" />
                <div class="viz-gallery-tags" role="group" aria-label="Filter by tag">
                    ${tags.map((t) => `<button class="viz-gallery-tag" data-tag="${escapeHtml(t)}" aria-pressed="${t === this.activeTag ? 'true' : 'false'}">${escapeHtml(t)}</button>`).join('')}
                    ${this.activeTag ? `<button class="viz-gallery-tag" data-tag="" aria-pressed="false"><i class="fas fa-times"></i> Clear</button>` : ''}
                </div>
                <button class="viz-gallery-new" type="button" title="Create a new visualization — ask the AI in chat to build one, then save it here.">
                    <i class="fas fa-plus"></i> New viz
                </button>
            </div>
        `;

        const gridHtml = `
            <div class="viz-gallery-grid">
                ${visible.length ? visible.map(renderCard).join('') : renderEmptyState()}
            </div>
        `;

        // Preserve the existing h2 if present; otherwise inject one.
        const existingH2 = this.tabEl.querySelector(':scope > h2');
        this.tabEl.innerHTML = `
            ${existingH2 ? existingH2.outerHTML : `<h2 style="margin-bottom: var(--space-5); font-size: 28px;"><i class="fas fa-chart-area"></i> My Visualizations</h2>`}
            ${toolbarHtml}
            ${gridHtml}
        `;

        // Bind search
        const searchInput = this.tabEl.querySelector('.viz-gallery-search');
        if (searchInput) {
            searchInput.value = this.search;
            searchInput.addEventListener('input', (e) => {
                this.search = e.target.value;
                this.render();
                // Re-focus the search box after re-render.
                const again = this.tabEl.querySelector('.viz-gallery-search');
                if (again) {
                    again.focus();
                    const len = again.value.length;
                    try { again.setSelectionRange(len, len); } catch (_) { /* noop */ }
                }
            });
        }

        // Bind tag chips
        this.tabEl.querySelectorAll('.viz-gallery-tag').forEach((chip) => {
            chip.addEventListener('click', () => {
                this.activeTag = chip.getAttribute('data-tag') || '';
                this.render();
            });
        });

        // Bind cards
        this.tabEl.querySelectorAll('.viz-gallery-card').forEach((card) => {
            card.addEventListener('click', () => {
                const id = card.getAttribute('data-snapshot-id');
                const summary = this.snapshots.find((s) => s.id === id);
                openVizModal(id, summary);
            });
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    card.click();
                }
            });
        });

        // "New viz" — for V1, just nudge the user.
        const newBtn = this.tabEl.querySelector('.viz-gallery-new');
        if (newBtn) {
            newBtn.addEventListener('click', () => {
                toast('Ask the AI in chat to build a chart, then use the kebab (⋮) → Save to library.', 'info');
            });
        }
    }

    renderError(message) {
        const existingH2 = this.tabEl.querySelector(':scope > h2');
        this.tabEl.innerHTML = `
            ${existingH2 ? existingH2.outerHTML : ''}
            ${renderErrorState(message)}
        `;
    }
}

export async function onDashboardLoad(tabEl) {
    const el = tabEl || document.getElementById('tab-analytics');
    if (!el) {
        console.warn('[viz-gallery] tab-analytics not found');
        return;
    }
    injectStyles();
    const gallery = new VizGallery(el);
    await gallery.load();
}

export async function onDashboardUnload(tabEl) {
    const el = tabEl || document.getElementById('tab-analytics');
    if (!el) return;
    delete el.__vizGalleryInstance;
}

export default { onDashboardLoad, onDashboardUnload };
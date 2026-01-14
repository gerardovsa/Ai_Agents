/**
 * FILE: UI/modules/internal-docs-manager.js
 * PURPOSE: Complete internal document management system for Synergy platform
 * 
 * FEATURES:
 * - Rich text editor with TipTap
 * - Spreadsheet editor with Handsontable
 * - Document creation with metadata (title, description, tags)
 * - Floating popup windows (draggable, resizable, collapsible)
 * - Auto-save functionality
 * - Export to multiple formats
 * - Activity log and version history
 * - Editable titles
 * 
 * DEPENDENCIES:
 * - TipTap (CDN)
 * - Handsontable (CDN)
 * - FontAwesome icons
 * - DocumentService (shared utility)
 * 
 * EXPORTS:
 * - InternalDocsManager class
 * 
 * LAST MODIFIED: December 21, 2025 - Integrated with DocumentService
 */

import { documentService } from '../shared/document-service.js';

class InternalDocsManager {
    constructor(apiBaseUrl = window.API_BASE_URL || window.location.origin) {
        this.apiBaseUrl = apiBaseUrl;
        this.popupWindows = {};
        this.popupZIndex = 9000;
        this.currentUser = {
            email: 'user@example.com', // Will be populated from auth
            user_id: 1
        };

        // Inject CSS styles
        this.injectStyles();

        console.log('📄 InternalDocsManager initialized with API:', this.apiBaseUrl);
    }

    /**
     * Inject CSS styles into the document
     */
    injectStyles() {
        if (document.getElementById('internal-docs-manager-styles')) {
            return; // Already injected
        }

        const styleElement = document.createElement('style');
        styleElement.id = 'internal-docs-manager-styles';
        styleElement.textContent = `
            /* Document Editor Container */
            .doc-editor-container {
                flex: 1;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }

            /* Editor Toolbar */
            .doc-editor-toolbar {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                background: var(--bg-tertiary);
                border-bottom: 1px solid var(--border-default);
                flex-wrap: wrap;
            }

            .toolbar-group {
                display: flex;
                align-items: center;
                gap: 4px;
                padding: 0 8px;
                border-right: 1px solid var(--border-default);
            }

            .toolbar-group:last-child {
                border-right: none;
            }

            .toolbar-btn {
                min-width: 36px;
                height: 36px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                padding: 0 10px;
                background: transparent;
                border: none;
                border-radius: 8px;
                color: var(--text-secondary);
                cursor: pointer;
                transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
                font-size: 14px;
                font-weight: 500;
                position: relative;
            }

            .toolbar-btn:hover {
                background: rgba(88, 166, 255, 0.12);
                color: var(--accent-primary);
                transform: translateY(-1px);
            }

            .toolbar-btn.active {
                background: rgba(88, 166, 255, 0.2);
                color: var(--accent-primary);
                box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.3);
            }

            .toolbar-btn:active {
                transform: translateY(0);
            }

            .toolbar-separator {
                width: 1px;
                height: 24px;
                background: var(--border-default);
                margin: 0 4px;
            }

            /* Editor Content Area */
            .doc-editor-content {
                flex: 1;
                overflow-y: auto;
                padding: 0;
                background: linear-gradient(180deg, var(--bg-primary) 0%, rgba(0, 0, 0, 0.02) 100%);
                position: relative;
            }

            .doc-editor-content::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.1) 50%, transparent 100%);
            }

            .doc-editor-wrapper {
                margin: 0;
                padding: 0;
                border: none;
                border-radius: 0;
                background: transparent;
                min-height: 100%;
            }

            /* TipTap Editor Styles */
            .tiptap-editor {
                min-height: calc(100% - 64px);
                max-width: 820px;
                margin: 0 auto;
                padding: 8px 16px;
                color: var(--text-primary);
                font-size: 15px;
                line-height: 1.5;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                letter-spacing: 0.01em;
            }

            .tiptap-editor:focus {
                outline: none;
            }

            .tiptap-editor::selection {
                background: rgba(88, 166, 255, 0.3);
            }

            .tiptap-editor h1 {
                font-size: 32px;
                font-weight: 700;
                margin: 32px 0 20px;
                color: var(--text-primary);
                letter-spacing: -0.02em;
                line-height: 1.2;
            }

            .tiptap-editor h2 {
                font-size: 24px;
                font-weight: 650;
                margin: 28px 0 16px;
                color: var(--text-primary);
                letter-spacing: -0.01em;
                line-height: 1.3;
            }

            .tiptap-editor h3 {
                font-size: 20px;
                font-weight: 600;
                margin: 24px 0 12px;
                color: var(--text-primary);
                letter-spacing: -0.005em;
                line-height: 1.4;
            }

            .tiptap-editor p {
                margin: 0 0 12px;
            }

            .tiptap-editor ul,
            .tiptap-editor ol {
                padding-left: 24px;
                margin: 12px 0;
            }

            .tiptap-editor li {
                margin: 4px 0;
            }

            .tiptap-editor code {
                background: rgba(88, 166, 255, 0.12);
                padding: 3px 8px;
                border-radius: 6px;
                font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Courier New', monospace;
                font-size: 13.5px;
                color: #79c0ff;
                border: 1px solid rgba(88, 166, 255, 0.2);
            }

            .tiptap-editor pre {
                background: rgba(0, 0, 0, 0.4);
                padding: 20px 24px;
                border-radius: 12px;
                overflow-x: auto;
                margin: 20px 0;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2);
            }

            .tiptap-editor pre code {
                background: transparent;
                padding: 0;
                border: none;
                color: #e2e8f0;
            }

            .tiptap-editor blockquote {
                border-left: 4px solid var(--accent-primary);
                padding-left: 16px;
                margin: 16px 0;
                color: var(--text-secondary);
            }

            .tiptap-editor a {
                color: var(--accent-primary);
                text-decoration: underline;
                cursor: pointer;
            }

            .tiptap-editor a:hover {
                color: var(--accent-secondary);
            }

            .tiptap-editor img {
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                margin: 12px 0;
            }

            /* Mention Styling */
            .tiptap-editor .mention {
                background-color: rgba(79, 108, 255, 0.2);
                border-radius: 4px;
                padding: 2px 6px;
                color: var(--accent-primary);
                font-weight: 500;
            }

            /* Auto-save indicator */
            .auto-save-indicator {
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .auto-save-indicator i {
                animation: pulse 2s ease-in-out infinite;
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }

            /* Spreadsheet Container */
            .spreadsheet-container {
                flex: 1;
                overflow: auto;
                background: var(--bg-primary);
                padding: 0;
            }

            .spreadsheet-wrapper {
                margin: 10px;
                padding: 10px;
                border: 1px solid rgba(88, 166, 255, 0.15);
                border-radius: 8px;
                background: rgba(88, 166, 255, 0.03);
                min-height: calc(100% - 20px);
                overflow: auto;
            }

            .spreadsheet-container table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                font-size: 13px;
            }

            .spreadsheet-container th {
                background: rgba(88, 166, 255, 0.12);
                padding: 10px 12px;
                text-align: left;
                font-weight: 600;
                color: var(--text-primary);
                border: 1px solid var(--border-default);
                position: sticky;
                top: 0;
                z-index: 10;
            }

            .spreadsheet-container td {
                padding: 8px 12px;
                border: 1px solid var(--border-default);
                background: var(--bg-secondary);
                transition: background 0.15s ease;
            }

            .spreadsheet-container tr:hover td {
                background: rgba(88, 166, 255, 0.06);
            }

            .spreadsheet-container td:focus {
                outline: 2px solid var(--accent-primary);
                outline-offset: -2px;
                background: rgba(88, 166, 255, 0.1);
            }

            /* Popup Footer - Action Buttons */
            .internal-doc-popup-footer {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 12px 16px;
                background: var(--bg-tertiary);
                border-top: 1px solid var(--border-default);
                border-radius: 0 0 12px 12px;
            }

            .internal-doc-popup.collapsed .internal-doc-popup-footer {
                display: none;
            }

            .popup-footer-left {
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 12px;
                color: var(--text-secondary);
            }

            .save-status {
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .save-status i {
                font-size: 10px;
            }

            .save-status.saving {
                color: #ffc107;
            }

            .save-status.saved {
                color: #4caf50;
            }

            .save-status.error {
                color: #f44336;
            }

            .popup-footer-right {
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .popup-action-btn {
                padding: 8px 16px;
                background: transparent;
                border: 1px solid var(--border-default);
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                color: var(--text-secondary);
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .popup-action-btn:hover {
                background: var(--bg-hover);
                border-color: var(--accent-primary);
                color: var(--accent-primary);
            }

            .popup-action-btn.primary {
                background: var(--accent-primary);
                border-color: var(--accent-primary);
                color: white;
            }

            .popup-action-btn.primary:hover {
                background: #4a8fe7;
                box-shadow: 0 2px 8px rgba(88, 166, 255, 0.3);
            }

            /* Resize Handles */
            .popup-resize-handle {
                position: absolute;
                background: transparent;
                z-index: 10;
            }

            .popup-resize-handle.n {
                top: 0;
                left: 0;
                right: 0;
                height: 8px;
                cursor: n-resize;
            }

            .popup-resize-handle.s {
                bottom: 0;
                left: 0;
                right: 0;
                height: 8px;
                cursor: s-resize;
            }

            .popup-resize-handle.e {
                top: 0;
                right: 0;
                bottom: 0;
                width: 8px;
                cursor: e-resize;
            }

            .popup-resize-handle.w {
                top: 0;
                left: 0;
                bottom: 0;
                width: 8px;
                cursor: w-resize;
            }

            .popup-resize-handle.ne {
                top: 0;
                right: 0;
                width: 16px;
                height: 16px;
                cursor: ne-resize;
            }

            .popup-resize-handle.nw {
                top: 0;
                left: 0;
                width: 16px;
                height: 16px;
                cursor: nw-resize;
            }

            .popup-resize-handle.se {
                bottom: 0;
                right: 0;
                width: 16px;
                height: 16px;
                cursor: se-resize;
            }

            .popup-resize-handle.sw {
                bottom: 0;
                left: 0;
                width: 16px;
                height: 16px;
                cursor: sw-resize;
            }

            /* Popup Animations */
            @keyframes popupSlideIn {
                from {
                    opacity: 0;
                    transform: translate(-50%, -45%);
                }
                to {
                    opacity: 1;
                    transform: translate(-50%, -50%);
                }
            }

            .internal-doc-popup.animating {
                animation: popupSlideIn 0.3s ease-out;
            }

            /* Loading State */
            .popup-loading {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 16px;
                padding: 40px;
                height: 100%;
            }

            .popup-loading i {
                font-size: 32px;
                color: var(--accent-primary);
                animation: spin 1s linear infinite;
            }

            /* Formula Help Panel */
            .formula-help-panel {
                position: absolute;
                top: 80px;
                right: 20px;
                width: 380px;
                max-height: calc(100% - 100px);
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                z-index: 10000;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }

            .formula-help-header {
                padding: 16px;
                background: var(--bg-tertiary);
                border-bottom: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .formula-help-header h3 {
                margin: 0;
                font-size: 16px;
                color: var(--text-primary);
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .formula-help-header .close-btn {
                background: none;
                border: none;
                color: var(--text-secondary);
                cursor: pointer;
                padding: 4px 8px;
                border-radius: 4px;
                transition: all 0.2s;
            }

            .formula-help-header .close-btn:hover {
                background: var(--bg-hover);
                color: var(--text-primary);
            }

            .formula-help-content {
                padding: 16px;
                overflow-y: auto;
                max-height: 600px;
            }

            .formula-category {
                margin-bottom: 20px;
            }

            .formula-category h4 {
                margin: 0 0 8px 0;
                font-size: 14px;
                color: var(--accent-primary);
                font-weight: 600;
            }

            .formula-category ul {
                list-style: none;
                padding: 0;
                margin: 0;
            }

            .formula-category li {
                padding: 6px 0;
                font-size: 13px;
                color: var(--text-secondary);
                line-height: 1.5;
            }

            .formula-category code {
                background: var(--bg-tertiary);
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                color: var(--accent-success);
            }

            .formula-tip {
                margin-top: 16px;
                padding: 12px;
                background: rgba(79, 108, 255, 0.1);
                border-left: 3px solid var(--accent-primary);
                border-radius: 4px;
                font-size: 13px;
                color: var(--text-secondary);
                line-height: 1.6;
            }

            .formula-tip i {
                color: var(--accent-warning);
                margin-right: 8px;
            }

            .formula-tip strong {
                color: var(--text-primary);
            }

            /* Chart Dialog */
            .chart-dialog {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 600px;
                max-width: 90%;
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                z-index: 10001;
                overflow: hidden;
            }

            .chart-dialog-header {
                padding: 20px;
                background: var(--bg-tertiary);
                border-bottom: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .chart-dialog-header h3 {
                margin: 0;
                font-size: 18px;
                color: var(--text-primary);
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .chart-dialog-content {
                padding: 24px;
            }

            .chart-type-selector h4 {
                margin: 0 0 12px 0;
                font-size: 14px;
                color: var(--text-secondary);
            }

            .chart-type-buttons {
                display: flex;
                gap: 8px;
                margin-bottom: 20px;
            }

            .chart-type-btn {
                flex: 1;
                padding: 12px;
                background: var(--bg-tertiary);
                border: 2px solid var(--border-color);
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
                color: var(--text-secondary);
                font-size: 13px;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 6px;
            }

            .chart-type-btn i {
                font-size: 20px;
            }

            .chart-type-btn:hover {
                background: var(--bg-hover);
                border-color: var(--accent-primary);
                color: var(--text-primary);
            }

            .chart-type-btn.active {
                background: rgba(79, 108, 255, 0.1);
                border-color: var(--accent-primary);
                color: var(--accent-primary);
            }

            .chart-actions {
                margin-top: 20px;
                display: flex;
                justify-content: flex-end;
                gap: 12px;
            }

            .btn-secondary, .btn-primary {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .btn-secondary {
                background: var(--bg-tertiary);
                color: var(--text-primary);
            }

            .btn-secondary:hover {
                background: var(--bg-hover);
            }

            .btn-primary {
                background: var(--accent-primary);
                color: white;
            }

            .btn-primary:hover {
                background: rgba(79, 108, 255, 0.8);
                box-shadow: 0 2px 8px rgba(79, 108, 255, 0.3);
            }

            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            .popup-loading-text {
                font-size: 14px;
                color: var(--text-secondary);
            }

            /* Attach Existing Document Modal */
            .attach-doc-list {
                max-height: 400px;
                overflow-y: auto;
                margin: 16px 0;
            }

            .attach-doc-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px;
                background: var(--bg-tertiary);
                border: 1px solid var(--border-default);
                border-radius: 8px;
                margin-bottom: 8px;
                cursor: pointer;
                transition: all 0.2s;
            }

            .attach-doc-item:hover {
                background: var(--bg-hover);
                border-color: var(--accent-primary);
            }

            .attach-doc-item.selected {
                background: rgba(79, 108, 255, 0.15);
                border-color: var(--accent-primary);
            }

            .attach-doc-icon {
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(79, 108, 255, 0.1);
                border-radius: 8px;
                color: var(--accent-primary);
                font-size: 18px;
            }

            .attach-doc-info {
                flex: 1;
            }

            .attach-doc-title {
                font-size: 14px;
                font-weight: 600;
                color: var(--text-primary);
                margin-bottom: 4px;
            }

            .attach-doc-meta {
                font-size: 12px;
                color: var(--text-secondary);
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .attach-doc-meta span {
                display: flex;
                align-items: center;
                gap: 4px;
            }
        `;

        document.head.appendChild(styleElement);
        console.log('✅ Internal Docs Manager CSS injected');
    }

    /**
     * Initialize the module
     */
    async init() {
        // ⚠️ ONLY initialize after user is authenticated
        // Don't fetch profile here - wait for UserAuth to provide it

        // Ensure container exists
        if (!document.getElementById('internalDocPopupContainer')) {
            const container = document.createElement('div');
            container.id = 'internalDocPopupContainer';
            document.body.appendChild(container);
        }

        console.log('✅ InternalDocsManager ready (awaiting authentication)');
    }

    // ⚠️ NEW: Call this AFTER user authentication
    async loadUserProfile() {
        try {
            // Check if UserAuth and token are available
            if (!window.UserAuth || !window.UserAuth.token) {
                console.warn('⚠️ [Internal Docs] UserAuth token not available yet, using defaults');
                return;
            }

            const response = await fetch(`${this.apiBaseUrl}/api/auth/profile`, {
                headers: window.UserAuth.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                this.currentUser.email = data.profile?.email || data.email || 'user@example.com';
                this.currentUser.user_id = data.profile?.id || data.user_id || 1;
                console.log('✅ InternalDocsManager user profile loaded:', this.currentUser.email);
            } else {
                console.warn(`⚠️ [Internal Docs] Profile fetch failed: ${response.status}`);
            }
        } catch (error) {
            console.warn('⚠️ [Internal Docs] Could not load user profile, using defaults:', error.message);
        }
    }

    // ==================== PUBLIC API ====================

    /**
     * Create a new internal document with metadata form
     */
    async createInternalDoc(sessionId) {
        console.log('📄 Creating new internal document for session:', sessionId);

        const popupId = `doc-create-${Date.now()}`;
        const popup = this.createPopupWindow(popupId, 'Create Internal Document', 600, 1000);

        const timestamp = new Date().toLocaleString();

        popup.bodyElement.innerHTML = `
            <div style="padding: 24px;">
                <form id="create-doc-form" style="display: flex; flex-direction: column; gap: 20px;">
                    <!-- Title -->
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            Title <span style="color: #f44336;">*</span>
                        </label>
                        <input type="text" id="doc-title-input" required
                            style="width: 100%; padding: 10px 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); 
                            border-radius: 6px; color: var(--text-primary); font-size: 14px;"
                            placeholder="Enter document title...">
                    </div>

                    <!-- Created By (readonly) -->
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            Created By
                        </label>
                        <input type="text" value="${this.currentUser.email}" readonly
                            style="width: 100%; padding: 10px 12px; background: var(--bg-hover); border: 1px solid var(--border-default); 
                            border-radius: 6px; color: var(--text-secondary); font-size: 14px; cursor: not-allowed;">
                    </div>

                    <!-- Created At (readonly) -->
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            Created At
                        </label>
                        <input type="text" value="${timestamp}" readonly
                            style="width: 100%; padding: 10px 12px; background: var(--bg-hover); border: 1px solid var(--border-default); 
                            border-radius: 6px; color: var(--text-secondary); font-size: 14px; cursor: not-allowed;">
                    </div>

                    <!-- Description -->
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            Description
                        </label>
                        <textarea id="doc-description-input" rows="3"
                            style="width: 100%; height: 150px; padding: 10px 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); 
                            border-radius: 6px; color: var(--text-primary); font-size: 14px; resize: vertical; font-family: inherit;"
                            placeholder="Brief description of this document..."></textarea>
                    </div>

                    <!-- Tags -->
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary);">
                            Tags
                        </label>
                        <input type="text" id="doc-tags-input"
                            style="width: 100%; padding: 10px 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); 
                            border-radius: 6px; color: var(--text-primary); font-size: 14px;"
                            placeholder="tag1, tag2, tag3">
                        <small style="color: var(--text-muted); font-size: 12px; display: block; margin-top: 4px;">
                            Separate tags with commas
                        </small>
                    </div>

                    <!-- Document Type -->
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 12px; font-weight: 600; color: var(--text-primary);">
                            Document Type <span style="color: #f44336;">*</span>
                        </label>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                            <div class="doc-type-option" data-type="richtext" 
                                style="padding: 16px; background: var(--bg-tertiary); border: 2px solid var(--border-default); 
                                border-radius: 8px; cursor: pointer; transition: all 0.2s; text-align: center;">
                                <i class="fas fa-file-alt" style="font-size: 24px; color: var(--accent-primary); margin-bottom: 6px;"></i>
                                <div style="font-weight: 600; color: var(--text-primary);">Document</div>
                            </div>
                            <div class="doc-type-option" data-type="spreadsheet"
                                style="padding: 16px; background: var(--bg-tertiary); border: 2px solid var(--border-default); 
                                border-radius: 8px; cursor: pointer; transition: all 0.2s; text-align: center;">
                                <i class="fas fa-table" style="font-size: 24px; color: var(--accent-primary); margin-bottom: 6px;"></i>
                                <div style="font-weight: 600; color: var(--text-primary);">Spreadsheet</div>
                            </div>
                        </div>
                        <input type="hidden" id="doc-type-input" value="richtext">
                    </div>
                </form>
            </div>
        `;

        // Add type selector logic
        popup.bodyElement.querySelectorAll('.doc-type-option').forEach(option => {
            option.addEventListener('click', () => {
                popup.bodyElement.querySelectorAll('.doc-type-option').forEach(opt => {
                    opt.style.borderColor = 'var(--border-default)';
                    opt.style.background = 'var(--bg-tertiary)';
                });
                option.style.borderColor = 'var(--accent-primary)';
                option.style.background = 'rgba(79, 108, 255, 0.1)';
                document.getElementById('doc-type-input').value = option.dataset.type;
            });
        });

        // Select richtext by default
        popup.bodyElement.querySelector('[data-type="richtext"]').click();

        // Footer buttons
        popup.footerRightElement.innerHTML = `
            <button class="popup-action-btn" onclick="window.internalDocsManager.closePopup('${popupId}')">
                <i class="fas fa-times"></i>
                Cancel
            </button>
            <button class="popup-action-btn primary" onclick="window.internalDocsManager.submitCreateForm('${sessionId}', '${popupId}')">
                <i class="fas fa-plus"></i>
                Create Document
            </button>
        `;

        this.showPopup(popupId);
    }

    /**
     * Submit the create document form
     */
    async submitCreateForm(sessionId, popupId) {
        const title = document.getElementById('doc-title-input').value.trim();
        const description = document.getElementById('doc-description-input').value.trim();
        const tags = document.getElementById('doc-tags-input').value.trim();
        const docType = document.getElementById('doc-type-input').value;

        if (!title) {
            alert('Please enter a document title');
            return;
        }

        try {
            const data = await documentService.createDocument({
                session_id: sessionId,
                title: title,
                content: '',
                content_json: docType === 'richtext' ? '{"type":"doc","content":[]}' : '[]',
                doc_type: docType,
                format: docType === 'richtext' ? 'markdown' : 'json',
                description: description,
                tags: tags
            });

            if (data.success) {
                console.log('✅ Document created:', data.doc_id);
                this.closePopup(popupId);
                await this.openInternalDocPopup(data.doc_id, sessionId);

                // Refresh synergy board if available
                if (window.synergyBoard) {
                    await window.synergyBoard.loadSessions();
                    window.synergyBoard.renderAllCards();
                }
            } else {
                alert('Failed to create document: ' + data.error);
            }
        } catch (error) {
            console.error('Error creating document:', error);
            alert('Failed to create document');
        }
    }

    /**
     * Open an internal document in a floating editor popup
     */
    async openInternalDocPopup(docId, sessionId) {
        console.log('📖 Opening internal document:', docId);

        const popupId = `doc-${docId}`;
        const popup = this.createPopupWindow(popupId, 'Loading...', 900, 600);

        popup.bodyElement.innerHTML = `
            <div class="popup-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <div class="popup-loading-text">Loading document...</div>
            </div>
        `;

        this.showPopup(popupId);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': String(this.currentUser.user_id)
                }
            });

            const data = await response.json();

            if (data.success) {
                const doc = {
                    doc_id: data.doc_id,
                    session_id: data.session_id,
                    title: data.title,
                    content: data.content,
                    content_json: data.content_json,
                    format: data.format,
                    doc_type: data.doc_type || 'richtext',
                    created_at: data.created_at,
                    updated_at: data.updated_at,
                    created_by: data.created_by,
                    version: data.version,
                    linked_to_ai: data.linked_to_ai
                };

                // Format creation date
                const createdDate = doc.created_at ? new Date(doc.created_at) : new Date();
                const formattedDate = createdDate.toLocaleString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });

                // Update popup title - Icon + Title input (left-aligned)
                popup.titleElement.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <i class="fas fa-${doc.doc_type === 'spreadsheet' ? 'table' : 'file-alt'}" style="font-size: 18px; color: var(--accent-primary);"></i>
                        <input type="text" value="${doc.title || 'Untitled'}" 
                            id="doc-title-edit-${docId}"
                            style="background: transparent; border: none; color: var(--text-primary); 
                            font-size: 20px; font-weight: 600; padding: 4px 8px; border-radius: 4px; width: auto; min-width: 150px; max-width: 600px;"
                            onblur="window.internalDocsManager.updateDocumentTitle('${docId}', this.value)"
                            oninput="this.style.width = Math.max(150, Math.min(600, (this.value.length * 12) + 20)) + 'px'"
                            onkeypress="if(event.key==='Enter'){this.blur();}">
                    </div>
                `;

                // Update timestamp element (separate, right-aligned before buttons)
                popup.timestampElement.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <i class="fas fa-clock" style="font-size: 10px; color: var(--text-muted);"></i>
                        <span style="color: var(--text-muted); font-size: 11px; white-space: nowrap;">Created ${formattedDate}</span>
                    </div>
                `;

                // Add description section as separate container below header (before body content)
                const descriptionContainer = document.createElement('div');
                descriptionContainer.style.cssText = 'padding: 12px 20px; border-bottom: 1px solid var(--border-color); background: var(--bg-primary);';
                descriptionContainer.innerHTML = `
                    <details ${doc.description ? 'open' : ''}>
                        <summary style="cursor: pointer; color: var(--text-muted); font-size: 12px; user-select: none; font-weight: 500;">
                            <i class="fas fa-align-left" style="font-size: 10px; margin-right: 6px;"></i>
                            Description
                        </summary>
                        <div style="margin-top: 8px; padding: 10px; background: var(--bg-secondary); border-radius: 6px; border-left: 3px solid var(--accent-primary);">
                            <textarea id="doc-description-${docId}" 
                                placeholder="Add a description for this ${doc.doc_type}..."
                                style="width: 100%; min-height: 60px; background: transparent; border: none; color: var(--text-primary); font-size: 12px; resize: vertical; padding: 4px; font-family: inherit;"
                                onblur="window.internalDocsManager.updateDocumentDescription('${docId}', this.value)"
                                onclick="event.stopPropagation()">${doc.description || ''}</textarea>
                        </div>
                    </details>
                `;

                // Insert description container before body content
                popup.bodyElement.parentElement.insertBefore(descriptionContainer, popup.bodyElement);

                // Create editor based on doc type
                if (doc.doc_type === 'spreadsheet') {
                    this.renderSpreadsheetEditor(popup, doc, sessionId);
                } else {
                    this.renderRichTextEditor(popup, doc, sessionId);
                }

                // Load and display share URL
                this.loadShareUrl(docId);

                // Update footer with save status and metadata row
                popup.footerLeftElement.innerHTML = `
                    <div style="display: flex; flex-direction: column; gap: 8px; width: 100%;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div class="save-status saved">
                                <i class="fas fa-check-circle"></i>
                                <span>Saved</span>
                            </div>
                            <span style="color: var(--text-muted); font-size: 11px;">Version ${doc.version || 1}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px; font-size: 11px; color: var(--text-muted);">
                            <i class="fas fa-folder" style="font-size: 10px;"></i>
                            <span>Session: ${doc.session_id}</span>
                            <span style="margin: 0 4px;">•</span>
                            <span>Doc ID: ${doc.doc_id}</span>
                            <span style="margin: 0 4px;">•</span>
                            <i class="fas fa-link" style="font-size: 10px;"></i>
                            <span id="doc-share-url-${docId}" style="color: var(--accent-primary); cursor: pointer;" onclick="window.internalDocsManager.copyDocumentUrl('${docId}')" title="Click to copy share URL">/internal-docs/${docId}</span>
                        </div>
                    </div>
                `;
            } else {
                popup.bodyElement.innerHTML = `
                    <div class="popup-loading">
                        <i class="fas fa-exclamation-triangle" style="color: #f44336;"></i>
                        <div class="popup-loading-text">Failed to load document: ${data.error}</div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading document:', error);
            popup.bodyElement.innerHTML = `
                <div class="popup-loading">
                    <i class="fas fa-exclamation-triangle" style="color: #f44336;"></i>
                    <div class="popup-loading-text">Error loading document</div>
                </div>
            `;
        }
    }

    /**
     * Render rich text editor with Tiptap
     */
    renderRichTextEditor(popup, doc, sessionId) {
        popup.bodyElement.innerHTML = `
            <div class="doc-editor-container">
                <div class="doc-editor-toolbar" id="tiptap-toolbar-${doc.doc_id}">
                    <!-- Toolbar will be populated by Tiptap initialization -->
                </div>
                <div class="doc-editor-content">
                    <div class="tiptap-editor" id="editor-${doc.doc_id}"></div>
                </div>
            </div>
        `;

        // Initialize Tiptap editor
        this.initializeTiptapEditor(doc, popup, sessionId);

        // Add footer buttons
        popup.footerRightElement.innerHTML = `
            <button class="toolbar-btn" title="Export to PDF" onclick="window.internalDocsManager.exportToPDF('${doc.doc_id}')" style="padding: 8px 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                <i class="fas fa-file-pdf"></i>
            </button>
            <button class="toolbar-btn" title="Export Markdown" onclick="window.internalDocsManager.exportDocument('${doc.doc_id}', 'markdown')" style="padding: 8px 12px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                <i class="fas fa-download"></i>
            </button>
            <button class="toolbar-btn" title="Save Document" onclick="window.internalDocsManager.saveTiptapContent('${doc.doc_id}')" style="padding: 10px 14px; background: var(--accent-primary); border: 1px solid var(--accent-primary); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: white; box-shadow: 0 2px 8px rgba(79, 108, 255, 0.3); margin-left: 8px;">
                <i class="fas fa-save" style="font-size: 16px;"></i>
            </button>
        `;
    }

    /**
     * Initialize Tiptap editor with all extensions
     */
    initializeTiptapEditor(doc, popup, sessionId) {
        // Check if Tiptap is loaded
        if (typeof window.tiptapCore === 'undefined') {
            console.error('Tiptap not loaded - falling back to basic editor');
            document.getElementById(`editor-${doc.doc_id}`).innerHTML = doc.content || '<p>Start typing...</p>';
            document.getElementById(`editor-${doc.doc_id}`).setAttribute('contenteditable', 'true');
            return;
        }

        const editorElement = document.getElementById(`editor-${doc.doc_id}`);
        const { Editor } = window.tiptapCore;
        const StarterKit = window.tiptapStarterKit?.StarterKit || window.tiptapStarterKit;

        // Create Tiptap editor instance
        const editor = new Editor({
            element: editorElement,
            extensions: [
                StarterKit,
            ].filter(Boolean),
            content: doc.content || '<p>Start typing your document...</p>',
            editorProps: {
                handleDrop: (view, event, slice, moved) => {
                    if (!moved && event.dataTransfer?.files?.[0]) {
                        this.handleFileUpload(event.dataTransfer.files[0], doc.doc_id, view, event);
                        return true;
                    }
                    return false;
                },
            },
            onUpdate: ({ editor }) => {
                // Auto-save after 2 seconds
                clearTimeout(this.tiptapSaveTimeout);
                const statusEl = popup.footerLeftElement?.querySelector('.save-status');
                if (statusEl) {
                    statusEl.className = 'save-status saving';
                    statusEl.querySelector('span').textContent = 'Saving...';
                }

                this.tiptapSaveTimeout = setTimeout(() => {
                    const html = editor.getHTML();
                    this.saveDocumentContent(doc.doc_id, html, popup, true);
                }, 2000);
            },
        });

        // Store editor instance
        if (!this.tiptapEditors) {
            this.tiptapEditors = {};
        }
        this.tiptapEditors[doc.doc_id] = editor;

        // Create toolbar
        this.createTiptapToolbar(doc.doc_id, editor);
    }

    /**
     * Create Tiptap toolbar
     */
    createTiptapToolbar(docId, editor) {
        const toolbar = document.getElementById(`tiptap-toolbar-${docId}`);
        if (!toolbar) return;

        toolbar.innerHTML = `
            <div class="toolbar-group">
                <button class="toolbar-btn tiptap-bold" title="Bold (Ctrl+B)">
                    <i class="fas fa-bold"></i>
                </button>
                <button class="toolbar-btn tiptap-italic" title="Italic (Ctrl+I)">
                    <i class="fas fa-italic"></i>
                </button>
                <button class="toolbar-btn tiptap-strike" title="Strikethrough">
                    <i class="fas fa-strikethrough"></i>
                </button>
                <button class="toolbar-btn tiptap-code" title="Code">
                    <i class="fas fa-code"></i>
                </button>
            </div>
            <div class="toolbar-group">
                <button class="toolbar-btn tiptap-h1" title="Heading 1">H1</button>
                <button class="toolbar-btn tiptap-h2" title="Heading 2">H2</button>
                <button class="toolbar-btn tiptap-h3" title="Heading 3">H3</button>
            </div>
            <div class="toolbar-group">
                <button class="toolbar-btn tiptap-bullet" title="Bullet List">
                    <i class="fas fa-list-ul"></i>
                </button>
                <button class="toolbar-btn tiptap-ordered" title="Numbered List">
                    <i class="fas fa-list-ol"></i>
                </button>
                <button class="toolbar-btn tiptap-quote" title="Quote">
                    <i class="fas fa-quote-right"></i>
                </button>
            </div>
            <div class="toolbar-group">
                <button class="toolbar-btn tiptap-undo" title="Undo (Ctrl+Z)">
                    <i class="fas fa-undo"></i>
                </button>
                <button class="toolbar-btn tiptap-redo" title="Redo (Ctrl+Y)">
                    <i class="fas fa-redo"></i>
                </button>
            </div>
            <div class="toolbar-group">
                <button class="toolbar-btn tiptap-link" title="Insert Link">
                    <i class="fas fa-link"></i>
                </button>
                <button class="toolbar-btn tiptap-image" title="Insert Image URL">
                    <i class="fas fa-image"></i>
                </button>
                <button class="toolbar-btn tiptap-upload" title="Upload File (or drag & drop)">
                    <i class="fas fa-upload"></i>
                </button>
            </div>
            <div class="toolbar-group" style="margin-left: auto;">
                <span class="auto-save-indicator" style="color: var(--text-secondary); font-size: 13px; padding: 0px;">
                    <i class="fas fa-circle" style="font-size: 8px; color: var(--accent-success);"></i>
                    Auto-save enabled
                </span>
            </div>
        `;

        // Attach event listeners
        toolbar.querySelector('.tiptap-bold').onclick = () => editor.chain().focus().toggleBold().run();
        toolbar.querySelector('.tiptap-italic').onclick = () => editor.chain().focus().toggleItalic().run();
        toolbar.querySelector('.tiptap-strike').onclick = () => editor.chain().focus().toggleStrike().run();
        toolbar.querySelector('.tiptap-code').onclick = () => editor.chain().focus().toggleCode().run();
        toolbar.querySelector('.tiptap-h1').onclick = () => editor.chain().focus().toggleHeading({ level: 1 }).run();
        toolbar.querySelector('.tiptap-h2').onclick = () => editor.chain().focus().toggleHeading({ level: 2 }).run();
        toolbar.querySelector('.tiptap-h3').onclick = () => editor.chain().focus().toggleHeading({ level: 3 }).run();
        toolbar.querySelector('.tiptap-bullet').onclick = () => editor.chain().focus().toggleBulletList().run();
        toolbar.querySelector('.tiptap-ordered').onclick = () => editor.chain().focus().toggleOrderedList().run();
        toolbar.querySelector('.tiptap-quote').onclick = () => editor.chain().focus().toggleBlockquote().run();
        toolbar.querySelector('.tiptap-undo').onclick = () => editor.chain().focus().undo().run();
        toolbar.querySelector('.tiptap-redo').onclick = () => editor.chain().focus().redo().run();

        toolbar.querySelector('.tiptap-link').onclick = () => {
            const url = prompt('Enter URL:');
            if (url) {
                editor.chain().focus().setLink({ href: url }).run();
            }
        };

        toolbar.querySelector('.tiptap-image').onclick = () => {
            const url = prompt('Enter image URL:');
            if (url) {
                editor.chain().focus().setImage({ src: url }).run();
            }
        };

        toolbar.querySelector('.tiptap-upload').onclick = () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.onchange = (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.handleFileUpload(file, docId, editor.view, null);
                }
            };
            input.click();
        };
    }

    /**
     * Handle file upload (drag & drop or button)
     */
    handleFileUpload(file, docId, view, event) {
        const filesize = ((file.size / 1024) / 1024).toFixed(4);

        if (filesize > 10) {
            this.showToast('File too large (max 10MB)', 'error');
            return;
        }

        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const editor = this.tiptapEditors[docId];
                if (editor) {
                    editor.chain().focus().setImage({ src: e.target.result }).run();
                    this.showToast(`Image uploaded: ${file.name}`, 'success');
                }
            };
            reader.readAsDataURL(file);
        } else {
            this.showToast(`File attached: ${file.name} (displayed as link)`, 'info');
        }
    }

    /**
     * Save Tiptap content
     */
    saveTiptapContent(docId) {
        const editor = this.tiptapEditors?.[docId];
        if (!editor) {
            this.showToast('Editor not initialized', 'error');
            return;
        }

        const html = editor.getHTML();
        const popup = document.querySelector(`[data-doc-id="${docId}"]`);
        this.saveDocumentContent(docId, html, popup, false);
    }

    /**
     * Export to PDF
     */
    async exportToPDF(docId) {
        const editor = this.tiptapEditors?.[docId];
        if (!editor) {
            this.showToast('Editor not initialized', 'error');
            return;
        }

        if (typeof jspdf === 'undefined' || typeof html2canvas === 'undefined') {
            this.showToast('PDF export libraries not loaded', 'error');
            return;
        }

        const content = document.getElementById(`editor-${docId}`);

        try {
            this.showToast('Generating PDF...', 'info');

            const canvas = await html2canvas(content, {
                scale: 2,
                backgroundColor: '#ffffff'
            });

            const imgData = canvas.toDataURL('image/png');
            const pdf = new jspdf.jsPDF({
                orientation: 'portrait',
                unit: 'mm',
                format: 'a4'
            });

            const imgWidth = 210;
            const imgHeight = (canvas.height * imgWidth) / canvas.width;

            pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
            pdf.save(`document-${docId}-${Date.now()}.pdf`);

            this.showToast('PDF exported successfully', 'success');
        } catch (error) {
            console.error('PDF export error:', error);
            this.showToast('PDF export failed', 'error');
        }
    }

    /**
     * Render spreadsheet editor with Handsontable
     */
    renderSpreadsheetEditor(popup, doc, sessionId) {
        popup.bodyElement.innerHTML = `
            <div style="display: flex; flex-direction: column; height: 100%; overflow: hidden;">
                <div class="doc-editor-toolbar" style="display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 16px; background: var(--bg-secondary); border-bottom: 1px solid var(--border-default); flex-shrink: 0;">
                    <!-- Row/Column Actions -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; padding-right: 8px; border-right: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Add Row Below" onclick="window.internalDocsManager.addRow('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary); display: flex; align-items: center; gap: 4px;">
                            <i class="fas fa-plus" style="font-size: 12px;"></i>
                            <i class="fas fa-grip-lines" style="font-size: 10px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Add Column Right" onclick="window.internalDocsManager.addColumn('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary); display: flex; align-items: center; gap: 4px;">
                            <i class="fas fa-plus" style="font-size: 12px;"></i>
                            <i class="fas fa-grip-lines-vertical" style="font-size: 10px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Delete Selected Rows" onclick="window.internalDocsManager.deleteRow('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary); display: flex; align-items: center; gap: 4px;">
                            <i class="fas fa-minus" style="font-size: 12px;"></i>
                            <i class="fas fa-grip-lines" style="font-size: 10px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Delete Selected Columns" onclick="window.internalDocsManager.deleteColumn('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary); display: flex; align-items: center; gap: 4px;">
                            <i class="fas fa-minus" style="font-size: 12px;"></i>
                            <i class="fas fa-grip-lines-vertical" style="font-size: 10px;"></i>
                        </button>
                    </div>
                    
                    <!-- Formatting Actions -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; padding-right: 8px; border-right: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Merge Cells" onclick="window.internalDocsManager.mergeCells('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-object-group" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Unmerge Cells" onclick="window.internalDocsManager.unmergeCells('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-object-ungroup" style="font-size: 14px;"></i>
                        </button>
                    </div>
                    
                    <!-- Clipboard Actions -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; padding-right: 8px; border-right: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Copy" onclick="window.internalDocsManager.copySelection('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-copy" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Paste" onclick="window.internalDocsManager.pasteSelection('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-paste" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Clear Contents" onclick="window.internalDocsManager.clearSelection('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-eraser" style="font-size: 14px;"></i>
                        </button>
                    </div>
                    
                    <!-- Sorting/Filtering -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; padding-right: 8px; border-right: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Sort Ascending" onclick="window.internalDocsManager.sortAscending('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-sort-amount-down" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Sort Descending" onclick="window.internalDocsManager.sortDescending('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-sort-amount-up" style="font-size: 14px;"></i>
                        </button>
                    </div>
                    
                    <!-- Undo/Redo -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; padding-right: 8px; border-right: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Undo" onclick="window.internalDocsManager.undoSpreadsheet('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-undo" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Redo" onclick="window.internalDocsManager.redoSpreadsheet('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-redo" style="font-size: 14px;"></i>
                        </button>
                    </div>
                    
                    <!-- Formulas -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; padding-right: 8px; border-right: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Insert SUM Formula" onclick="window.internalDocsManager.insertFormula('${doc.doc_id}', 'SUM')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--accent-success);">
                            <i class="fas fa-function" style="font-size: 12px;"></i> SUM
                        </button>
                        <button class="toolbar-btn" title="Insert AVERAGE Formula" onclick="window.internalDocsManager.insertFormula('${doc.doc_id}', 'AVERAGE')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--accent-success);">
                            <i class="fas fa-function" style="font-size: 12px;"></i> AVG
                        </button>
                        <button class="toolbar-btn" title="Insert IF Formula" onclick="window.internalDocsManager.insertFormula('${doc.doc_id}', 'IF')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--accent-success);">
                            <i class="fas fa-function" style="font-size: 12px;"></i> IF
                        </button>
                        <button class="toolbar-btn" title="Formula Help" onclick="window.internalDocsManager.toggleFormulaHelp('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--accent-primary);">
                            <i class="fas fa-question-circle" style="font-size: 14px;"></i> fx
                        </button>
                    </div>
                    
                    <!-- Advanced Features -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; padding-right: 8px; border-right: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Create Chart from Selection" onclick="window.internalDocsManager.createChart('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--accent-info);">
                            <i class="fas fa-chart-bar" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Create Pivot Table" onclick="window.internalDocsManager.createPivotTable('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--accent-warning);">
                            <i class="fas fa-table" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Export to Excel (XLSX)" onclick="window.internalDocsManager.exportToExcel('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--accent-success);">
                            <i class="fas fa-file-excel" style="font-size: 14px;"></i>
                        </button>
                    </div>
                    
                    <!-- Export/Share -->
                    <div class="toolbar-group" style="display: flex; gap: 4px;">
                        <button class="toolbar-btn" title="Export CSV" onclick="window.internalDocsManager.exportDocument('${doc.doc_id}', 'csv')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-file-csv" style="font-size: 14px;"></i>
                        </button>
                        <button class="toolbar-btn" title="Copy Share Link" onclick="window.internalDocsManager.copyDocumentUrl('${doc.doc_id}')" style="padding: 8px 10px; background: var(--bg-tertiary); border: 1px solid var(--border-default); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: var(--text-primary);">
                            <i class="fas fa-link" style="font-size: 14px;"></i>
                        </button>
                    </div>
                    
                    <!-- SAVE BUTTON (Prominent) -->
                    <div class="toolbar-group" style="display: flex; gap: 4px; margin-left: auto; padding-left: 8px; border-left: 1px solid var(--border-default);">
                        <button class="toolbar-btn" title="Save Spreadsheet" onclick="window.internalDocsManager.saveSpreadsheetWithNotification('${doc.doc_id}')" style="padding: 10px 14px; background: var(--accent-primary); border: 1px solid var(--accent-primary); border-radius: 4px; cursor: pointer; transition: all 0.2s; color: white; box-shadow: 0 2px 8px rgba(79, 108, 255, 0.3);">
                            <i class="fas fa-save" style="font-size: 16px;"></i>
                        </button>
                    </div>
                </div>
                <div id="spreadsheet-${doc.doc_id}" style="flex: 1; width: 100%; overflow: auto; background: var(--bg-primary);">
                    <!-- Handsontable will be initialized here -->
                </div>
            </div>
        `;

        // Initialize Handsontable
        const container = document.getElementById(`spreadsheet-${doc.doc_id}`);

        // Parse existing data or create empty grid
        let data = [];
        try {
            data = JSON.parse(doc.content_json || doc.content || '[]');
            if (!Array.isArray(data) || data.length === 0) {
                // Create 100x20 empty grid
                data = Array(100).fill(null).map(() => Array(20).fill(''));
            }
        } catch (e) {
            // Create 100x20 empty grid on error
            data = Array(100).fill(null).map(() => Array(20).fill(''));
        }

        // Check if Handsontable is loaded
        if (typeof Handsontable === 'undefined') {
            container.innerHTML = `
                <div style="padding: 40px; text-align: center; color: var(--text-secondary);">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #ffc107; margin-bottom: 16px;"></i>
                    <h3>Handsontable Not Loaded</h3>
                    <p style="margin: 16px 0;">Please include Handsontable in your HTML:</p>
                    <code style="display: block; background: var(--bg-tertiary); padding: 12px; border-radius: 6px; margin: 16px 0;">
                        &lt;script src="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.js"&gt;&lt;/script&gt;<br>
                        &lt;link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.css"&gt;
                    </code>
                    <p style="margin-top: 16px;">
                        <a href="https://handsontable.com/docs/" target="_blank" style="color: var(--accent-primary);">
                            View Handsontable Documentation
                        </a>
                    </p>
                </div>
            `;
        } else {
            // Initialize Handsontable instance storage
            if (!this.handsontableInstances) {
                this.handsontableInstances = {};
            }

            // Initialize HyperFormula engine for Excel-like formulas
            const hyperformulaInstance = typeof HyperFormula !== 'undefined' ? HyperFormula.buildEmpty({
                licenseKey: 'gpl-v3'
            }) : null;

            // Initialize Handsontable with FULL configuration - ALL FEATURES ENABLED
            const hot = new Handsontable(container, {
                data: data,
                width: '100%',
                height: '100%',
                licenseKey: 'non-commercial-and-evaluation',

                // FORMULAS - Enable Excel-like formulas (=SUM, =AVERAGE, =IF, etc.)
                formulas: hyperformulaInstance ? {
                    engine: hyperformulaInstance
                } : false,

                // HEADERS
                rowHeaders: true,
                colHeaders: true,

                // CONTEXT MENU - Enable with ALL options
                contextMenu: [
                    'row_above',
                    'row_below',
                    'col_left',
                    'col_right',
                    '---------',
                    'remove_row',
                    'remove_col',
                    '---------',
                    'undo',
                    'redo',
                    '---------',
                    'make_read_only',
                    '---------',
                    'alignment',
                    '---------',
                    'copy',
                    'cut',
                    '---------',
                    'mergeCells',
                    '---------',
                    'commentsAddEdit',
                    'commentsRemove'
                ],

                // DROPDOWN MENU - Column header menus
                dropdownMenu: [
                    'filter_by_condition',
                    'filter_operators',
                    'filter_by_condition2',
                    'filter_by_value',
                    'filter_action_bar',
                    '---------',
                    'alignment',
                    '---------',
                    'freeze_column',
                    '---------',
                    'clear_column'
                ],

                // COLUMN/ROW MANIPULATION
                manualRowResize: true,
                manualColumnResize: true,
                manualRowMove: true,
                manualColumnMove: true,
                autoWrapRow: true,
                autoWrapCol: true,

                // CELL FEATURES
                copyPaste: true,
                fillHandle: true,

                // UNDO/REDO
                undo: true,

                // COMMENTS
                comments: true,

                // CUSTOM BORDERS
                customBorders: true,

                // MERGE CELLS
                mergeCells: true,

                // SORTING
                columnSorting: {
                    indicator: true,
                    headerAction: true,
                    sortEmptyCells: true
                },

                // FILTERS
                filters: true,
                dropdownMenu: true,

                // COLUMN FREEZING
                fixedColumnsStart: 0,
                fixedRowsTop: 0,
                fixedRowsBottom: 0,

                // SELECTION
                selectionMode: 'multiple',
                outsideClickDeselects: false,

                // EDITOR OPTIONS
                enterBeginsEditing: true,
                enterMoves: { row: 1, col: 0 },
                tabMoves: { row: 0, col: 1 },

                // CELL NAVIGATION
                autoWrapCol: true,
                autoWrapRow: true,

                // VIRTUAL SCROLLING
                renderAllRows: false,
                renderAllColumns: false,

                // SPARE ROWS/COLS
                minSpareRows: 1,
                minSpareCols: 1,

                // SEARCH
                search: true,

                // ALLOW INSERTIONS
                allowInsertRow: true,
                allowInsertColumn: true,
                allowRemoveRow: true,
                allowRemoveColumn: true,

                // CELL TYPES (enable all cell types)
                cells: function (row, col) {
                    const cellProperties = {};
                    // Default to text type with auto-detection
                    cellProperties.type = 'text';
                    return cellProperties;
                },

                // EVENT HANDLERS
                afterSelection: (row, column, row2, column2) => {
                    // Log selection for debugging
                    console.log('✅ Selected:', { row, column, row2, column2 });
                },

                afterChange: (changes, source) => {
                    if (source !== 'loadData') {
                        // Auto-save on change
                        clearTimeout(this.spreadsheetSaveTimeout);
                        const statusEl = popup.footerLeftElement.querySelector('.save-status');
                        if (statusEl) {
                            statusEl.className = 'save-status saving';
                            statusEl.querySelector('span').textContent = 'Saving...';
                        }

                        this.spreadsheetSaveTimeout = setTimeout(() => {
                            const data = hot.getData();
                            this.saveDocumentContent(doc.doc_id, JSON.stringify(data), popup, true);
                        }, 1000);
                    }
                },

                afterSelection: (row, column, row2, column2) => {
                    console.log('Selection:', { row, column, row2, column2 });
                },

                afterCreateRow: (index, amount) => {
                    console.log('Row created at:', index, 'amount:', amount);
                },

                afterCreateCol: (index, amount) => {
                    console.log('Column created at:', index, 'amount:', amount);
                },

                afterRemoveRow: (index, amount) => {
                    console.log('Row removed at:', index, 'amount:', amount);
                },

                afterRemoveCol: (index, amount) => {
                    console.log('Column removed at:', index, 'amount:', amount);
                },

                // STYLING
                className: 'htCenter htMiddle',

                // COLUMN WIDTH OPTIONS
                colWidths: 100,

                // ROW HEIGHT OPTIONS
                rowHeights: 23,

                // WORD WRAP
                wordWrap: true,

                // STRETCH
                stretchH: 'all'
            });

            // Store instance for toolbar actions
            this.handsontableInstances = this.handsontableInstances || {};
            this.handsontableInstances[doc.doc_id] = hot;
        }

        // Add footer buttons with save status
        popup.footerLeftElement.innerHTML = `
            <div class="save-status saved" style="display: flex; align-items: center; gap: 8px; color: var(--text-secondary); font-size: 13px;">
                <i class="fas fa-check-circle"></i>
                <span>Saved</span>
            </div>
            <span style="color: var(--text-muted); font-size: 13px;">Version 1</span>
        `;

        popup.footerRightElement.innerHTML = ``;
    }

    /**
     * Save spreadsheet with toast notification
     */
    async saveSpreadsheetWithNotification(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) {
            console.error('Handsontable instance not found for:', docId);
            return;
        }

        const data = hot.getData();
        const popup = this.popupWindows[`doc-${docId}`];

        await this.saveDocumentContent(docId, JSON.stringify(data), popup, true);

        // Show toast notification
        this.showToast('Document saved successfully!', 'success');
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : '#f44336'};
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 100000;
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 12px;
            animation: slideIn 0.3s ease-out;
        `;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}" style="font-size: 18px;"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s';
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 2500);
    }

    /**
     * Save document content
     */
    async saveDocumentContent(docId, content, popup = null, isJson = false) {
        try {
            const payload = isJson ? {
                content_json: content
            } : {
                content: content
            };

            const data = await documentService.updateDocument(docId, payload);

            if (data.success) {
                console.log('✅ Document saved:', docId);
                if (popup) {
                    const statusEl = popup.footerLeftElement.querySelector('.save-status');
                    if (statusEl) {
                        statusEl.className = 'save-status saved';
                        statusEl.querySelector('span').textContent = 'Saved';

                        // Update version
                        const versionEl = popup.footerLeftElement.querySelector('span[style*="text-muted"]');
                        if (versionEl && data.version) {
                            versionEl.textContent = `Version ${data.version}`;
                        }
                    }
                }

                // Refresh synergy board if available
                if (window.synergyBoard) {
                    await window.synergyBoard.loadSessions();
                    window.synergyBoard.renderAllCards();
                }
            } else {
                console.error('Failed to save document:', data.error);
                if (popup) {
                    const statusEl = popup.footerLeftElement.querySelector('.save-status');
                    if (statusEl) {
                        statusEl.className = 'save-status error';
                        statusEl.querySelector('span').textContent = 'Error';
                    }
                }
            }
        } catch (error) {
            console.error('Error saving document:', error);
            if (popup) {
                const statusEl = popup.footerLeftElement.querySelector('.save-status');
                if (statusEl) {
                    statusEl.className = 'save-status error';
                    statusEl.querySelector('span').textContent = 'Error';
                }
            }
        }
    }

    /**
     * Export document
     */
    async exportDocument(docId, format) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}/export/${format}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': String(this.currentUser.user_id)
                }
            });

            const contentType = response.headers.get('content-type');

            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                alert('Export failed: ' + (data.error || 'Unknown error'));
                return;
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            const disposition = response.headers.get('content-disposition');
            let filename = `document.${format}`;
            if (disposition && disposition.includes('filename=')) {
                const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
                if (matches != null && matches[1]) {
                    filename = matches[1].replace(/['"]/g, '');
                }
            }

            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            console.log('✅ Document exported:', filename);
        } catch (error) {
            console.error('Error exporting document:', error);
            alert('Failed to export document');
        }
    }

    /**
     * SPREADSHEET TOOLBAR ACTIONS
     */

    mergeCells(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) {
            alert('Please select cells to merge');
            return;
        }

        const [startRow, startCol, endRow, endCol] = selected[0];
        hot.getPlugin('mergeCells').merge(startRow, startCol, endRow, endCol);
        console.log('Cells merged:', startRow, startCol, endRow, endCol);
    }

    unmergeCells(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) {
            alert('Please select merged cells to unmerge');
            return;
        }

        const [startRow, startCol] = selected[0];
        hot.getPlugin('mergeCells').unmerge(startRow, startCol);
        console.log('Cells unmerged:', startRow, startCol);
    }

    copySelection(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const plugin = hot.getPlugin('copyPaste');
        plugin.copy();
        console.log('Selection copied to clipboard');
    }

    pasteSelection(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const plugin = hot.getPlugin('copyPaste');
        plugin.paste();
        console.log('Pasted from clipboard');
    }

    clearSelection(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) return;

        selected.forEach(([startRow, startCol, endRow, endCol]) => {
            for (let row = startRow; row <= endRow; row++) {
                for (let col = startCol; col <= endCol; col++) {
                    hot.setDataAtCell(row, col, '');
                }
            }
        });
        console.log('Selection cleared');
    }

    sortAscending(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) {
            alert('Please select a column to sort');
            return;
        }

        const col = selected[0][1];
        const plugin = hot.getPlugin('columnSorting');
        plugin.sort({ column: col, sortOrder: 'asc' });
        console.log('Sorted column', col, 'ascending');
    }

    sortDescending(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) {
            alert('Please select a column to sort');
            return;
        }

        const col = selected[0][1];
        const plugin = hot.getPlugin('columnSorting');
        plugin.sort({ column: col, sortOrder: 'desc' });
        console.log('Sorted column', col, 'descending');
    }

    undoSpreadsheet(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        if (hot.isUndoAvailable()) {
            hot.undo();
            console.log('Undo performed');
        } else {
            console.log('Nothing to undo');
        }
    }

    redoSpreadsheet(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) return;

        if (hot.isRedoAvailable()) {
            hot.redo();
            console.log('Redo performed');
        } else {
            console.log('Nothing to redo');
        }
    }

    /**
     * Load and display share URL in document header
     */
    async loadShareUrl(docId) {
        try {
            const data = await documentService.fetchDocument(docId);

            if (data.success) {
                const urlElement = document.getElementById(`doc-share-url-${docId}`);
                if (urlElement) {
                    const slug = data.slug || docId;
                    const shareUrl = `/internal-docs/${slug}`;
                    urlElement.textContent = shareUrl;
                }
            }
        } catch (error) {
            console.error('Error loading share URL:', error);
            const urlElement = document.getElementById(`doc-share-url-${docId}`);
            if (urlElement) {
                urlElement.textContent = `/internal-docs/${docId}`;
            }
        }
    }

    /**
     * Insert formula at selected cell
     * @param {number} docId - Document ID
     * @param {string} formulaType - Type of formula (SUM, AVERAGE, IF, etc.)
     */
    insertFormula(docId, formulaType) {
        const hot = this.handsontableInstances[docId];
        if (!hot) {
            alert('Spreadsheet not initialized');
            return;
        }

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) {
            alert('Please select a cell to insert formula');
            return;
        }

        const [row, col] = selected[0];
        let formula = '';

        switch (formulaType) {
            case 'SUM':
                formula = '=SUM(A1:A10)';
                break;
            case 'AVERAGE':
                formula = '=AVERAGE(A1:A10)';
                break;
            case 'IF':
                formula = '=IF(A1>10, "Yes", "No")';
                break;
            case 'COUNT':
                formula = '=COUNT(A1:A10)';
                break;
            case 'MAX':
                formula = '=MAX(A1:A10)';
                break;
            case 'MIN':
                formula = '=MIN(A1:A10)';
                break;
            default:
                formula = '=SUM(A1:A10)';
        }

        hot.setDataAtCell(row, col, formula);
        this.showToast('Formula inserted! Edit cell to customize range', 'success');
    }

    /**
     * Toggle formula help panel
     * @param {number} docId - Document ID
     */
    toggleFormulaHelp(docId) {
        const popup = document.querySelector(`[data-doc-id="${docId}"]`);
        if (!popup) return;

        // Check if help panel already exists
        let helpPanel = popup.querySelector('.formula-help-panel');

        if (helpPanel) {
            helpPanel.remove();
            return;
        }

        // Create help panel
        helpPanel = document.createElement('div');
        helpPanel.className = 'formula-help-panel';
        helpPanel.innerHTML = `
            <div class="formula-help-header">
                <h3><i class="fas fa-function"></i> Excel-like Formulas</h3>
                <button class="close-btn" onclick="this.closest('.formula-help-panel').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="formula-help-content">
                <div class="formula-category">
                    <h4>Math & Statistics</h4>
                    <ul>
                        <li><code>=SUM(A1:A10)</code> - Sum of range</li>
                        <li><code>=AVERAGE(A1:A10)</code> - Average of range</li>
                        <li><code>=COUNT(A1:A10)</code> - Count numbers</li>
                        <li><code>=MAX(A1:A10)</code> - Maximum value</li>
                        <li><code>=MIN(A1:A10)</code> - Minimum value</li>
                        <li><code>=MEDIAN(A1:A10)</code> - Median value</li>
                    </ul>
                </div>
                <div class="formula-category">
                    <h4>Logical</h4>
                    <ul>
                        <li><code>=IF(A1>10, "Yes", "No")</code> - Conditional</li>
                        <li><code>=AND(A1>0, B1<100)</code> - All conditions true</li>
                        <li><code>=OR(A1>100, B1<0)</code> - Any condition true</li>
                        <li><code>=NOT(A1=0)</code> - Negate condition</li>
                    </ul>
                </div>
                <div class="formula-category">
                    <h4>Text</h4>
                    <ul>
                        <li><code>=CONCATENATE(A1, B1)</code> - Join text</li>
                        <li><code>=LEN(A1)</code> - Text length</li>
                        <li><code>=UPPER(A1)</code> - Convert to uppercase</li>
                        <li><code>=LOWER(A1)</code> - Convert to lowercase</li>
                    </ul>
                </div>
                <div class="formula-category">
                    <h4>Lookup</h4>
                    <ul>
                        <li><code>=VLOOKUP(value, range, col, 0)</code> - Vertical lookup</li>
                        <li><code>=HLOOKUP(value, range, row, 0)</code> - Horizontal lookup</li>
                    </ul>
                </div>
                <div class="formula-category">
                    <h4>Date & Time</h4>
                    <ul>
                        <li><code>=TODAY()</code> - Current date</li>
                        <li><code>=NOW()</code> - Current date & time</li>
                        <li><code>=YEAR(A1)</code> - Extract year</li>
                        <li><code>=MONTH(A1)</code> - Extract month</li>
                    </ul>
                </div>
                <div class="formula-tip">
                    <i class="fas fa-lightbulb"></i>
                    <strong>Tip:</strong> Start formulas with <code>=</code> symbol. 
                    Click a cell and type <code>=</code> to begin. Use cell references (A1, B2) or ranges (A1:A10).
                </div>
            </div>
        `;

        const mainContent = popup.querySelector('.internal-doc-popup-main-content');
        mainContent.appendChild(helpPanel);
    }

    /**
     * Copy document URL to clipboard with detailed context for AI agents
     */
    async copyDocumentUrl(docId) {
        try {
            // Fetch document to get full details
            const data = await documentService.fetchDocument(docId);

            if (!data.success) {
                throw new Error('Failed to fetch document');
            }

            // Fetch session details to get session title/slug
            let sessionTitle = 'Unknown Session';
            let sessionSlug = data.session_id;
            try {
                const sessionResponse = await fetch(`${this.apiBaseUrl}/api/synergy/session/${data.session_id}`, {
                    headers: {
                        'X-User-ID': String(this.currentUser.user_id)
                    }
                });
                const sessionData = await sessionResponse.json();
                if (sessionData.success) {
                    sessionTitle = sessionData.title || sessionData.session_id;
                    // Extract slug from session_id (format: sess_timestamp_slug)
                    const parts = sessionData.session_id.split('_');
                    if (parts.length > 2) {
                        sessionSlug = parts.slice(2).join('_');
                    }
                }
            } catch (e) {
                console.warn('Could not fetch session details:', e);
            }

            // Build comprehensive context for AI agents
            const slug = data.slug || docId;
            const url = `${window.location.origin}/internal-docs/${slug}`;

            // Create detailed context text
            const contextText = `Internal Document Reference:

Title: ${data.title}
Document Type: ${data.doc_type || 'richtext'}
Document Slug: ${slug}

Session: ${sessionTitle}
Session Slug: ${sessionSlug}
Session ID: ${data.session_id}

Format: ${data.format || 'markdown'}
Created: ${data.created_at}
${data.description ? `Description: ${data.description}\n` : ''}${data.tags ? `Tags: ${data.tags}\n` : ''}
Direct URL: ${url}

Note: Use the document slug "${slug}" to reference this document in Synergy sessions.`;

            await navigator.clipboard.writeText(contextText);

            // Show success message
            const message = document.createElement('div');
            message.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--accent-primary);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 100000;
                font-size: 14px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
            `;
            message.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <span>Document details copied to clipboard!</span>
            `;
            document.body.appendChild(message);

            setTimeout(() => {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.3s';
                setTimeout(() => document.body.removeChild(message), 300);
            }, 2000);

            console.log('Document context copied:\n', contextText);
        } catch (error) {
            console.error('Failed to copy URL:', error);
            alert('Failed to copy link to clipboard');
        }
    }

    /**
     * Update document title
     */
    async updateDocumentTitle(docId, newTitle) {
        if (!newTitle.trim()) return;

        try {
            const data = await documentService.updateDocument(docId, {
                title: newTitle
            });

            if (data.success) {
                console.log('✅ Title updated:', newTitle);

                // Refresh synergy board if available
                if (window.synergyBoard) {
                    await window.synergyBoard.loadSessions();
                    window.synergyBoard.renderAllCards();
                }
            } else {
                alert('Failed to update title: ' + data.error);
            }
        } catch (error) {
            console.error('Error updating title:', error);
            alert('Failed to update title');
        }
    }

    /**
     * Update document description
     */
    async updateDocumentDescription(docId, newDescription) {
        try {
            const data = await documentService.updateDocument(docId, {
                description: newDescription
            });

            if (data.success) {
                console.log('✅ Description updated');
            } else {
                console.error('Failed to update description:', data.error);
            }
        } catch (error) {
            console.error('Error updating description:', error);
        }
    }

    /**
     * Show activity log with version history
     */
    async showActivityLog(docId) {
        const popupId = `activity-log-${docId}`;
        const popup = this.createPopupWindow(popupId, 'Activity Log & Version History', 700, 500);

        popup.bodyElement.innerHTML = `
            <div class="popup-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <div class="popup-loading-text">Loading activity log...</div>
            </div>
        `;

        this.showPopup(popupId);

        // TODO: Implement activity log API endpoint
        // For now, show placeholder
        setTimeout(() => {
            popup.bodyElement.innerHTML = `
                <div style="padding: 24px;">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border-default);">
                        <i class="fas fa-history" style="font-size: 24px; color: var(--accent-primary);"></i>
                        <div>
                            <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: var(--text-primary);">Document Activity</h3>
                            <p style="margin: 4px 0 0; font-size: 12px; color: var(--text-secondary);">Track changes and version history</p>
                        </div>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 12px;">
                        <!-- Activity items -->
                        <div style="padding: 12px; background: var(--bg-tertiary); border-radius: 8px; border-left: 3px solid #4caf50;">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                                <span style="font-weight: 600; color: var(--text-primary);">
                                    <i class="fas fa-file-alt" style="color: #4caf50; margin-right: 8px;"></i>
                                    Document Created
                                </span>
                                <span style="font-size: 12px; color: var(--text-muted);">Just now</span>
                            </div>
                            <div style="font-size: 13px; color: var(--text-secondary);">
                                Created by ${this.currentUser.email}
                            </div>
                        </div>

                        <div style="padding: 12px; background: var(--bg-tertiary); border-radius: 8px; border-left: 3px solid var(--accent-primary);">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                                <span style="font-weight: 600; color: var(--text-primary);">
                                    <i class="fas fa-eye" style="color: var(--accent-primary); margin-right: 8px;"></i>
                                    Document Opened
                                </span>
                                <span style="font-size: 12px; color: var(--text-muted);">Now</span>
                            </div>
                            <div style="font-size: 13px; color: var(--text-secondary);">
                                Opened by ${this.currentUser.email}
                            </div>
                        </div>

                        <!-- Coming soon message -->
                        <div style="margin-top: 20px; padding: 16px; background: rgba(255, 193, 7, 0.1); border-radius: 8px; text-align: center;">
                            <i class="fas fa-info-circle" style="color: #ffc107; font-size: 24px; margin-bottom: 8px;"></i>
                            <p style="margin: 0; font-size: 13px; color: var(--text-secondary);">
                                Full version history tracking coming soon!<br>
                                Will include timestamps, user actions, and version rollback.
                            </p>
                        </div>
                    </div>
                </div>
            `;
        }, 500);

        popup.footerRightElement.innerHTML = `
            <button class="popup-action-btn" onclick="window.internalDocsManager.closePopup('${popupId}')">
                <i class="fas fa-times"></i>
                Close
            </button>
        `;
    }

    /**
     * Insert link helper
     */
    insertLink() {
        const url = prompt('Enter URL:');
        if (url) {
            document.execCommand('createLink', false, url);
        }
    }

    /**
     * Handsontable toolbar actions
     */
    addRow(docId) {
        const hot = this.handsontableInstances?.[docId];
        if (hot) {
            hot.alter('insert_row_below', hot.countRows() - 1);
        }
    }

    addColumn(docId) {
        const hot = this.handsontableInstances?.[docId];
        if (hot) {
            hot.alter('insert_col_end', hot.countCols() - 1);
        }
    }

    deleteRow(docId) {
        const hot = this.handsontableInstances?.[docId];
        if (hot) {
            const selected = hot.getSelected();
            if (selected && selected.length > 0) {
                const row = selected[0][0];
                hot.alter('remove_row', row);
            } else {
                alert('Please select a row to delete');
            }
        }
    }

    deleteColumn(docId) {
        const hot = this.handsontableInstances?.[docId];
        if (hot) {
            const selected = hot.getSelected();
            if (selected && selected.length > 0) {
                const col = selected[0][1];
                hot.alter('remove_col', col);
            } else {
                alert('Please select a column to delete');
            }
        }
    }

    // ==================== POPUP WINDOW MANAGEMENT ====================

    /**
     * Create a floating popup window
     */
    createPopupWindow(id, title, width = 800, height = 700) {
        const container = document.getElementById('internalDocPopupContainer');

        if (this.popupWindows[id]) {
            this.showPopup(id);
            return this.popupWindows[id];
        }

        const left = (window.innerWidth - width) / 2;
        const top = (window.innerHeight - height) / 2;

        const popupHTML = `
            <div class="internal-doc-popup" id="${id}" style="width: ${width}px; height: ${height}px; left: ${left}px; top: ${top}px;">
                <div class="popup-resize-handle n"></div>
                <div class="popup-resize-handle s"></div>
                <div class="popup-resize-handle e"></div>
                <div class="popup-resize-handle w"></div>
                <div class="popup-resize-handle ne"></div>
                <div class="popup-resize-handle nw"></div>
                <div class="popup-resize-handle se"></div>
                <div class="popup-resize-handle sw"></div>

                <div class="internal-doc-popup-header">
                    <div class="internal-doc-popup-title">${title}</div>
                    <div class="internal-doc-popup-timestamp"></div>
                    <div class="internal-doc-popup-controls">
                        <button class="popup-control-btn minimize" title="Minimize" onclick="window.internalDocsManager.toggleCollapse('${id}')">
                            <i class="fas fa-minus"></i>
                        </button>
                        <button class="popup-control-btn maximize" title="Maximize" onclick="window.internalDocsManager.toggleMaximize('${id}')">
                            <i class="fas fa-expand"></i>
                        </button>
                        <button class="popup-control-btn close" title="Close" onclick="window.internalDocsManager.closePopup('${id}')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>

                <div class="internal-doc-popup-body"></div>

                <div class="internal-doc-popup-footer">
                    <div class="popup-footer-left"></div>
                    <div class="popup-footer-right"></div>
                </div>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', popupHTML);

        const popupElement = document.getElementById(id);
        const headerElement = popupElement.querySelector('.internal-doc-popup-header');
        const titleElement = popupElement.querySelector('.internal-doc-popup-title');
        const timestampElement = popupElement.querySelector('.internal-doc-popup-timestamp');
        const bodyElement = popupElement.querySelector('.internal-doc-popup-body');
        const footerElement = popupElement.querySelector('.internal-doc-popup-footer');
        const footerLeftElement = popupElement.querySelector('.popup-footer-left');
        const footerRightElement = popupElement.querySelector('.popup-footer-right');

        const popup = {
            id,
            popupElement,
            headerElement,
            titleElement,
            timestampElement,
            bodyElement,
            footerElement,
            footerLeftElement,
            footerRightElement,
            width,
            height,
            left,
            top,
            isCollapsed: false,
            isMaximized: false
        };

        this.popupWindows[id] = popup;
        this.initPopupDrag(popup);
        this.initPopupResize(popup);

        return popup;
    }

    showPopup(id) {
        const popup = this.popupWindows[id];
        if (!popup) return;

        popup.popupElement.classList.add('active', 'animating');
        popup.popupElement.style.zIndex = ++this.popupZIndex;

        setTimeout(() => {
            popup.popupElement.classList.remove('animating');
        }, 300);
    }

    closePopup(id) {
        const popup = this.popupWindows[id];
        if (!popup) return;

        popup.popupElement.classList.remove('active');

        setTimeout(() => {
            popup.popupElement.remove();
            delete this.popupWindows[id];
        }, 200);
    }

    toggleCollapse(id) {
        const popup = this.popupWindows[id];
        if (!popup) return;

        popup.isCollapsed = !popup.isCollapsed;
        popup.popupElement.classList.toggle('collapsed', popup.isCollapsed);

        const icon = popup.headerElement.querySelector('.minimize i');
        icon.className = popup.isCollapsed ? 'fas fa-plus' : 'fas fa-minus';
    }

    toggleMaximize(id) {
        const popup = this.popupWindows[id];
        if (!popup) return;

        popup.isMaximized = !popup.isMaximized;
        popup.popupElement.classList.toggle('maximized', popup.isMaximized);

        const icon = popup.headerElement.querySelector('.maximize i');
        icon.className = popup.isMaximized ? 'fas fa-compress' : 'fas fa-expand';
    }

    initPopupDrag(popup) {
        let isDragging = false;
        let dragOffsetX = 0;
        let dragOffsetY = 0;

        popup.headerElement.addEventListener('mousedown', (e) => {
            if (e.target.closest('.popup-control-btn') || e.target.tagName === 'INPUT') return;
            if (popup.isMaximized) return;

            isDragging = true;
            dragOffsetX = e.clientX - popup.popupElement.offsetLeft;
            dragOffsetY = e.clientY - popup.popupElement.offsetTop;

            popup.popupElement.style.zIndex = ++this.popupZIndex;

            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            const newLeft = e.clientX - dragOffsetX;
            const newTop = e.clientY - dragOffsetY;

            popup.popupElement.style.left = `${newLeft}px`;
            popup.popupElement.style.top = `${newTop}px`;
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });
    }

    initPopupResize(popup) {
        const handles = popup.popupElement.querySelectorAll('.popup-resize-handle');

        handles.forEach(handle => {
            const direction = handle.className.split(' ').pop(); // Get last class (n, s, e, w, ne, nw, se, sw)

            handle.addEventListener('mousedown', (e) => {
                if (popup.isMaximized) return;

                e.preventDefault();
                e.stopPropagation();

                const startX = e.clientX;
                const startY = e.clientY;
                const startWidth = popup.popupElement.offsetWidth;
                const startHeight = popup.popupElement.offsetHeight;
                const startLeft = popup.popupElement.offsetLeft;
                const startTop = popup.popupElement.offsetTop;

                const handleMouseMove = (moveEvent) => {
                    const deltaX = moveEvent.clientX - startX;
                    const deltaY = moveEvent.clientY - startY;

                    if (direction.includes('e')) {
                        popup.popupElement.style.width = `${Math.max(400, startWidth + deltaX)}px`;
                    }
                    if (direction.includes('w')) {
                        const newWidth = Math.max(400, startWidth - deltaX);
                        popup.popupElement.style.width = `${newWidth}px`;
                        popup.popupElement.style.left = `${startLeft + (startWidth - newWidth)}px`;
                    }
                    if (direction.includes('s')) {
                        popup.popupElement.style.height = `${Math.max(300, startHeight + deltaY)}px`;
                    }
                    if (direction.includes('n')) {
                        const newHeight = Math.max(300, startHeight - deltaY);
                        popup.popupElement.style.height = `${newHeight}px`;
                        popup.popupElement.style.top = `${startTop + (startHeight - newHeight)}px`;
                    }
                };

                const handleMouseUp = () => {
                    document.removeEventListener('mousemove', handleMouseMove);
                    document.removeEventListener('mouseup', handleMouseUp);
                };

                document.addEventListener('mousemove', handleMouseMove);
                document.addEventListener('mouseup', handleMouseUp);
            });
        });
    }

    /**
     * Create chart from selected data
     * @param {number} docId - Document ID
     */
    createChart(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) {
            alert('Spreadsheet not initialized');
            return;
        }

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) {
            alert('Please select data range for chart (e.g., 2+ columns with headers)');
            return;
        }

        const [startRow, startCol, endRow, endCol] = selected[0];
        const selectedData = [];

        // Extract data from selection
        for (let row = startRow; row <= endRow; row++) {
            const rowData = [];
            for (let col = startCol; col <= endCol; col++) {
                rowData.push(hot.getDataAtCell(row, col));
            }
            selectedData.push(rowData);
        }

        // Create chart dialog
        const popup = document.querySelector(`[data-doc-id="${docId}"]`);
        if (!popup) return;

        const chartDialog = document.createElement('div');
        chartDialog.className = 'chart-dialog';
        chartDialog.innerHTML = `
            <div class="chart-dialog-header">
                <h3><i class="fas fa-chart-bar"></i> Create Chart</h3>
                <button class="close-btn" onclick="this.closest('.chart-dialog').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="chart-dialog-content">
                <div class="chart-type-selector">
                    <h4>Chart Type:</h4>
                    <div class="chart-type-buttons">
                        <button class="chart-type-btn active" data-type="bar">
                            <i class="fas fa-chart-bar"></i> Bar
                        </button>
                        <button class="chart-type-btn" data-type="line">
                            <i class="fas fa-chart-line"></i> Line
                        </button>
                        <button class="chart-type-btn" data-type="pie">
                            <i class="fas fa-chart-pie"></i> Pie
                        </button>
                        <button class="chart-type-btn" data-type="doughnut">
                            <i class="fas fa-circle-notch"></i> Doughnut
                        </button>
                    </div>
                </div>
                <canvas id="chart-preview-${docId}" width="400" height="250"></canvas>
                <div class="chart-actions">
                    <button class="btn-secondary" onclick="this.closest('.chart-dialog').remove()">Cancel</button>
                    <button class="btn-primary" onclick="window.internalDocsManager.saveChartAsImage('${docId}')">
                        <i class="fas fa-download"></i> Save as Image
                    </button>
                </div>
            </div>
        `;

        const mainContent = popup.querySelector('.internal-doc-popup-main-content');
        mainContent.appendChild(chartDialog);

        // Initialize chart
        const ctx = document.getElementById(`chart-preview-${docId}`).getContext('2d');
        let currentChart = null;

        const createChartInstance = (type) => {
            if (currentChart) {
                currentChart.destroy();
            }

            const labels = selectedData.slice(1).map(row => row[0]);
            const datasets = [];

            for (let col = 1; col < selectedData[0].length; col++) {
                datasets.push({
                    label: selectedData[0][col] || `Series ${col}`,
                    data: selectedData.slice(1).map(row => parseFloat(row[col]) || 0),
                    backgroundColor: this.getChartColors(datasets.length),
                    borderColor: this.getChartColors(datasets.length, 0.8),
                    borderWidth: 2
                });
            }

            currentChart = new Chart(ctx, {
                type: type,
                data: { labels, datasets },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: 'Chart Preview' }
                    }
                }
            });

            window[`currentChart_${docId}`] = currentChart;
        };

        createChartInstance('bar');

        // Chart type buttons
        chartDialog.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                chartDialog.querySelectorAll('.chart-type-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                createChartInstance(btn.dataset.type);
            });
        });
    }

    /**
     * Get chart colors
     */
    getChartColors(index, alpha = 0.6) {
        const colors = [
            `rgba(79, 108, 255, ${alpha})`,
            `rgba(52, 211, 153, ${alpha})`,
            `rgba(251, 146, 60, ${alpha})`,
            `rgba(239, 68, 68, ${alpha})`,
            `rgba(168, 85, 247, ${alpha})`,
            `rgba(236, 72, 153, ${alpha})`
        ];
        return colors[index % colors.length];
    }

    /**
     * Save chart as image
     */
    saveChartAsImage(docId) {
        const chart = window[`currentChart_${docId}`];
        if (!chart) return;

        const canvas = chart.canvas;
        canvas.toBlob(blob => {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `chart-${docId}-${Date.now()}.png`;
            link.click();
            URL.revokeObjectURL(url);
            this.showToast('Chart saved as image', 'success');
        });
    }

    /**
     * Create pivot table from selection
     */
    createPivotTable(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) {
            alert('Spreadsheet not initialized');
            return;
        }

        const selected = hot.getSelected();
        if (!selected || selected.length === 0) {
            alert('Please select data range for pivot table');
            return;
        }

        this.showToast('Pivot table feature - Select rows to group, columns to aggregate', 'info');

        // Simple pivot table implementation
        const [startRow, startCol, endRow, endCol] = selected[0];
        const data = [];

        for (let row = startRow; row <= endRow; row++) {
            const rowData = [];
            for (let col = startCol; col <= endCol; col++) {
                rowData.push(hot.getDataAtCell(row, col));
            }
            data.push(rowData);
        }

        // Show pivot dialog
        this.showToast(`Pivot: ${data.length} rows, ${data[0].length} columns selected`, 'info');
    }

    /**
     * Export to Excel (XLSX) with formulas preserved
     */
    exportToExcel(docId) {
        const hot = this.handsontableInstances[docId];
        if (!hot) {
            alert('Spreadsheet not initialized');
            return;
        }

        if (typeof XLSX === 'undefined') {
            alert('XLSX library not loaded. Include SheetJS CDN.');
            return;
        }

        const data = hot.getData();

        // Create workbook
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.aoa_to_sheet(data);

        // Add worksheet to workbook
        XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');

        // Generate file
        const fileName = `spreadsheet-${docId}-${Date.now()}.xlsx`;
        XLSX.writeFile(wb, fileName);

        this.showToast('Exported to Excel (XLSX) successfully', 'success');
    }
}

// Auto-initialize and expose globally
window.internalDocsManager = new InternalDocsManager(window.API_BASE_URL || 'http://localhost:5001');

// ⚠️ REMOVED: Don't auto-initialize on DOM load - wait for authentication!
// Old code that caused premature database connections:
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => {
//         window.internalDocsManager.init();
//     });
// } else {
//     window.internalDocsManager.init();
// }

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InternalDocsManager;
}

// Create global instance
window.InternalDocsManager = InternalDocsManager;
window.internalDocsManager = new InternalDocsManager();

// ✅ NEW: Initialize AFTER authentication in business-ai-platform-v2.html
// Call window.internalDocsManager.init() in UserAuth.showMainApp() or initializeMainApp()
// Then call window.internalDocsManager.loadUserProfile() to load user data

console.log('✅ Internal Docs Manager module loaded (awaiting authentication)');

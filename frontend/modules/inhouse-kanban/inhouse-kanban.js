/**
 * InHousePrint Production Workflow Module
 * AI-Integrated Kanban board for production tracking
 * 
 * Features:
 * - Real-time job tracking from SQL Server
 * - AI-powered priority scoring (0-999)
 * - Customer tier badges (VIP/Premium/Regular/New)
 * - WIP status indicators (DELAYED/AT_RISK/ON_TRACK)
 * - Multi-stage workflow visualization
 * - Advanced filtering and search
 * - Responsive Kanban layout
 * - Job detail modals
 * 
 * @class InhouseKanbanModule
 * @extends BaseModule
 * @created 2025-11-03
 * @updated 2025-11-03 15:30 - Fixed StageID filtering
 */

console.log('🔷 InHouse Kanban Module Loading - VERSION 3.0 - BaseModule.initialize() FIXED');

// BaseModule polyfill (lightweight replacement since BaseModule.js not loaded)
// VERSION 3.0 - Added initialize() method
class BaseModule {
    constructor(moduleId) {
        this.moduleId = moduleId;
        this.manifest = null;
        this.backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        console.log(`✅ BaseModule constructor - moduleId: ${moduleId}`);
    }
    
    async initialize() {
        console.log(`✅ BaseModule.initialize() called for ${this.moduleId}`);
        // Load manifest from backend
        try {
            const response = await fetch(`${this.backendUrl}/api/modules/${this.moduleId}`);
            if (response.ok) {
                this.manifest = await response.json();
                console.log(`✅ Manifest loaded for ${this.moduleId}:`, this.manifest);
            } else {
                console.warn(`⚠️ Failed to load manifest (HTTP ${response.status})`);
            }
        } catch (error) {
            console.warn(`⚠️ Failed to load manifest for ${this.moduleId}:`, error);
        }
    }
}

class InhouseKanbanModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);

        console.log('🔷 InhouseKanbanModule constructor called - Using numeric StageID filtering');

        // Configuration
        this.apiEndpoint = '/api/inhouse-kanban';
        this.API_BASE_URL = window.API_BASE_URL || 'http://localhost:5001';
        this.analyticsApiBase = this.API_BASE_URL + '/api/inhouse-kanban'; // ✅ FIX: Initialize analytics API base URL

        // State management
        this.jobs = [];
        this.stages = [];
        this.metrics = {};
        this.filters = {
            timeframe_months: -6,
            priority_filter: 'all',
            stage_id: null,
            search_text: ''
        };

        // Stage transition cache for timestamp display
        this.stageTransitionCache = new Map();

        // Card mute settings (per-card customization)
        this.mutedCards = new Map(); // Map<TicketID, MuteSettings>
        this.loadMutedCards(); // Load from localStorage

        // Color settings (global color customization)
        this.colorSettings = null; // Will be loaded from localStorage
        this.loadColorSettings(); // Load color settings

        // Color toggle settings (on/off switches)
        this.colorToggles = {
            showBorderColors: true,
            showBackgroundColors: true,
            showBannerColors: true
        };
        this.loadColorToggles(); // Load toggle state

        // UI State
        this.currentView = 'kanban-board';
        this.selectedJob = null;

        // Data cache
        this.dataCache = new Map();
        this.lastRefresh = null;

        // Auto-refresh timer
        this.refreshTimer = null;

        // Stage mapping with Font Awesome icons and colors
        this.stageMapping = {
            'ArtOnly': { icon: 'fa-brush', color: '#FF6B6B', label: 'Art Only' },
            'ArtAndPrint': { icon: 'fa-palette', color: '#FF8E53', label: 'Art & Print' },
            'OnHold': { icon: 'fa-pause-circle', color: '#FFA500', label: 'On Hold' },
            'Digital - 9110': { icon: 'fa-print', color: '#4ECDC4', label: 'Digital - 9110' },
            'Digital - Other': { icon: 'fa-print', color: '#45B7D1', label: 'Digital - Other' },
            'Digital - OutSource': { icon: 'fa-exchange', color: '#96CEB4', label: 'Digital - OutSource' },
            'Digital - Cello': { icon: 'fa-star', color: '#FFEAA7', label: 'Digital - Cello' },
            'Digital - Bindery': { icon: 'fa-book', color: '#DDA0DD', label: 'Digital - Bindery' },
            'TicketComplete': { icon: 'fa-check', color: '#98D8C8', label: 'Ticket Complete' },
            'ReadyToPrint': { icon: 'fa-hourglass-start', color: '#F7DC6F', label: 'Ready to Print' },
            'Signs - UV': { icon: 'fa-sun', color: '#BB8FCE', label: 'Signs - UV' },
            'Signs - Solvent': { icon: 'fa-droplet', color: '#AED6F1', label: 'Signs - Solvent' },
            'Signs - Laminate': { icon: 'fa-layer-group', color: '#A3E4D7', label: 'Signs - Laminate' },
            'Signs - Finishing': { icon: 'fa-toolbox', color: '#D5A6BD', label: 'Signs - Finishing' }
        };

        // Stage display order (Main board workflow left to right)
        this.stageOrder = [
            'ReadyToPrint',
            'Digital - 9110',
            'Digital - Other',
            'Digital - OutSource',
            'Digital - Cello',
            'Digital - Bindery',
            'TicketComplete',
            'ArtOnly',
            'ArtAndPrint',
            'OnHold',
            'Signs - UV',
            'Signs - Solvent',
            'Signs - Laminate',
            'Signs - Finishing'
        ];

        // Workboard definitions (filter stage display by StageID)
        // NOTE: Stages 5 (Digital-Other) and 7 (Digital-Cello) don't exist in current database
        // Using only stages that actually exist: 3, 4, 6, 8, 9, 11, 12, 13, 14, 15
        this.workboards = {
            'main': {
                name: 'Main Workflow',
                icon: 'fa-stream',
                stages: [11, 4, 6, 8, 9]  // ReadyToPrint, Digital-9110, OutSource, Bindery, Complete
            },
            'wide-format': {
                name: 'Wide Format',
                icon: 'fa-rectangle-landscape',
                stages: [11, 12, 13, 14, 15, 9]  // ReadyToPrint, UV, Solvent, Laminate, Finishing, Complete
            },
            'apg': {
                name: 'APG Supplies',
                icon: 'fa-box-open',
                stages: [3, 6, 8, 9]  // OnHold, OutSource, Bindery, Complete (removed non-existent 1, 7)
            },
            'publishing': {
                name: 'Publishing',
                icon: 'fa-book',
                stages: [11, 4, 8, 9]  // ReadyToPrint, Digital-9110, Bindery, Complete (removed non-existent 5, 7)
            }
        };

        // Current active workboard
        this.activeWorkboard = 'main';

        // Priority function to get icon and label
        this.getPriorityInfo = (score) => {
            score = score || 0;
            if (score >= 800) return { icon: 'fa-fire', label: 'CRITICAL', color: '#B71C1C' };
            if (score >= 600) return { icon: 'fa-exclamation-triangle', label: 'HIGH', color: '#D32F2F' };
            if (score >= 400) return { icon: 'fa-circle', label: 'MEDIUM', color: '#FF8800' };
            if (score >= 200) return { icon: 'fa-list', label: 'NORMAL', color: '#4CAF50' };
            return { icon: 'fa-circle-o', label: 'LOW', color: '#2196F3' };
        };

        // Customer tier badges
        this.getTierIcon = (tierName) => {
            const tiers = {
                'VIP': 'fa-gem',
                'Premium': 'fa-star',
                'Regular': 'fa-check',
                'New': 'fa-plus'
            };
            return tiers[tierName] || 'fa-circle';
        };
    }

    /**
     * Initialize module
     */
    async initialize() {
        console.log('🔧 Initializing InHouse Print Production Workflow module...');

        // Store reference for onclick handlers
        window.currentKanbanModule = this;

        // CRITICAL: Inject CSS styles inline to ensure they load
        this.injectCriticalStyles();

        // Initialize UI from BaseModule (loads manifest first)
        await super.initialize();

        // Apply module colors (after manifest is loaded)
        this.applyModuleColors();

        // Load initial data
        await this.loadInitialData();

        // Set up event listeners
        this.setupEventListeners();

        // Start auto-refresh
        this.startAutoRefresh();

        console.log('✅ InHouse Print Production Workflow module ready');
    }

    /**
     * Inject critical CSS styles inline (emergency fallback)
     */
    injectCriticalStyles() {
        const styleId = 'inhouse-kanban-critical-styles';

        // Remove existing if present
        const existingStyle = document.getElementById(styleId);
        if (existingStyle) {
            existingStyle.remove();
        }

        const style = document.createElement('style');
        style.id = styleId;
        style.setAttribute('data-module', 'inhouse-kanban'); // Mark for cleanup
        style.textContent = `
            /* InHouse Production Kanban - Scoped Critical Styles */
            /* ONLY applies when #tab-inhouse-kanban is visible and active */
            
            /* FILTERS BAR - ALL IN ONE ROW */
            #tab-inhouse-kanban.active .filters-bar {
                display: flex !important;
                flex-direction: row !important;
                gap: 16px !important;
                align-items: center !important;
                padding: 16px 20px !important;
                border-bottom: 1px solid #2A3142 !important;
                flex-wrap: nowrap !important;
            }
            
            #tab-inhouse-kanban.active .filter-group {
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
                white-space: nowrap !important;
            }
            
            #tab-inhouse-kanban.active .filter-group label {
                font-size: 13px !important;
                color: #9CA3AF !important;
                font-weight: 600 !important;
                display: flex !important;
                align-items: center !important;
                gap: 6px !important;
            }
            
            #tab-inhouse-kanban.active .filter-select,
            #tab-inhouse-kanban.active .filter-input {
                padding: 8px 12px !important;
                background: #0B0E13 !important;
                border: 1px solid #2A3142 !important;
                border-radius: 6px !important;
                color: #E5E7EB !important;
                font-size: 13px !important;
            }
            
            #tab-inhouse-kanban.active .last-refresh {
                font-size: 12px !important;
                color: #6B7280 !important;
            }
            
            /* WORKBOARD SELECTOR - ALL IN ONE ROW */
            #tab-inhouse-kanban.active .workboard-selector {
                display: flex !important;
                flex-direction: row !important;
                gap: 0 !important;
                padding: 0 20px !important;
                background: #0B0E13 !important;
                border-bottom: 1px solid #2A3142 !important;
                overflow-x: auto !important;
                margin-top: 40px;
            }
            
            /* METRICS ROW - ALL IN ONE ROW */
            #tab-inhouse-kanban.active .kanban-metrics {
                display: flex !important;
                flex-direction: row !important;
                gap: 16px !important;
                padding: 20px !important;
                background: #0B0E13 !important;
                border-bottom: 1px solid #2A3142 !important;
                flex-wrap: nowrap !important;
            }
            
            #tab-inhouse-kanban.active .metric-card {
                flex: 1 !important;
                min-width: 200px !important;
                background: #1A1F2E !important;
                border: 1px solid #2A3142 !important;
                border-radius: 8px !important;
                padding: 16px !important;
                display: flex !important;
                align-items: center !important;
                gap: 16px !important;
            }
            
            #tab-inhouse-kanban.active .metric-icon {
                width: 48px !important;
                height: 48px !important;
                border-radius: 8px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-size: 20px !important;
            }
            
            #tab-inhouse-kanban.active .metric-content {
                flex: 1 !important;
            }
            
            #tab-inhouse-kanban.active .metric-label {
                font-size: 12px !important;
                color: #9CA3AF !important;
                margin-bottom: 4px !important;
            }
            
            #tab-inhouse-kanban.active .metric-value {
                font-size: 24px !important;
                font-weight: 700 !important;
                color: #E5E7EB !important;
            }
            
            /* KANBAN BOARD - HORIZONTAL COLUMNS */
            #tab-inhouse-kanban.active .kanban-board {
                display: flex !important;
                flex-direction: row !important;
                gap: 20px !important;
                padding: 20px !important;
                overflow-x: auto !important;
                overflow-y: visible !important;
                flex: 1 !important;
                background: #0B0E13 !important;
                align-items: flex-start !important;
                min-height: fit-content !important;
                width: 100% !important;
            }
            
            #tab-inhouse-kanban.active .kanban-column {
                min-width: 400px !important;
                max-width: 40px !important;
            /*    background: #1A1F2E !important; */
                border: 1px solid #2A3142 !important;
                border-radius: 8px !important;
                display: flex !important;
                flex-direction: column !important;
                height: auto !important;
                max-height: none !important;
                flex-shrink: 0 !important;
                overflow: visible !important;
            }
            
            #tab-inhouse-kanban.active .column-header {
                padding: 16px !important;
                border-bottom: 2px solid #2A3142 !important;
                display: flex !important;
                flex-direction: column !important;
                gap: 8px !important;
                flex-shrink: 0 !important;
                background: #1A1F2E !important;
            }
            
            #tab-inhouse-kanban.active .column-title {
                font-size: 16px !important;
                font-weight: 700 !important;
                color: #E5E7EB !important;
                margin: 0 !important;
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
            }
            
            #tab-inhouse-kanban.active .column-metrics {
                display: flex !important;
                align-items: center !important;
                gap: 16px !important;
                font-size: 12px !important;
                color: #9CA3AF !important;
            }
            
            #tab-inhouse-kanban.active .job-count,
            #tab-inhouse-kanban.active .stage-value {
                font-weight: 600 !important;
            }
            
            #tab-inhouse-kanban.active .column-body {
                padding: 12px !important;
                overflow-y: visible !important;
                overflow-x: hidden !important;
                flex: 1 !important;
                min-height: auto !important;
            }
            
            #tab-inhouse-kanban.active .kanban-card {
                background: #0B0E13 !important;
                border: 1px solid #2A3142 !important;
                border-radius: 6px !important;
                padding: 12px !important;
                margin-bottom: 12px !important;
                cursor: pointer !important;
                transition: all 0.2s ease !important;
            }
            
            #tab-inhouse-kanban.active .kanban-card:hover {
                border-color: #00509E !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 12px rgba(0, 80, 158, 0.3) !important;
            }
            
            #tab-inhouse-kanban.active .kanban-card-header {
                display: flex !important;
                justify-content: space-between !important;
                align-items: flex-start !important;
                margin-bottom: 12px !important;
            }
            
            #tab-inhouse-kanban.active .job-number {
                font-size: 14px !important;
                font-weight: 700 !important;
                color: #00509E !important;
            }
            
            #tab-inhouse-kanban.active .client-name {
                font-size: 13px !important;
                color: #E5E7EB !important;
                font-weight: 600 !important;
                margin-bottom: 4px !important;
            }
            
            #tab-inhouse-kanban.active .card-meta {
                display: flex !important;
                gap: 12px !important;
                margin-top: 8px !important;
                padding-top: 8px !important;
                border-top: 1px solid #2A3142 !important;
            }
            
            #tab-inhouse-kanban.active .meta-item {
                font-size: 11px !important;
                color: #9CA3AF !important;
                display: flex !important;
                align-items: center !important;
                gap: 4px !important;
            }
            
            #tab-inhouse-kanban.active .priority-badge {
                padding: 3px 8px !important;
                border-radius: 4px !important;
                font-size: 10px !important;
                font-weight: 700 !important;
                text-transform: uppercase !important;
            }
            
            #tab-inhouse-kanban.active .priority-critical {
                background: rgba(239, 68, 68, 0.2) !important;
                color: #EF4444 !important;
            }
            
            #tab-inhouse-kanban.active .priority-high {
                background: rgba(249, 115, 22, 0.2) !important;
                color: #F97316 !important;
            }
            
            #tab-inhouse-kanban.active .priority-normal {
                background: rgba(59, 130, 246, 0.2) !important;
                color: #3B82F6 !important;
            }
            
            #tab-inhouse-kanban.active .priority-low {
                background: rgba(107, 114, 128, 0.2) !important;
                color: #6B7280 !important;
            }
            
            /* Due Date Classes */
            #tab-inhouse-kanban.active .due-date-overdue {
                color: #EF4444 !important;
                font-weight: 700 !important;
            }
            
            #tab-inhouse-kanban.active .due-date-critical {
                color: #F97316 !important;
                font-weight: 700 !important;
            }
            
            #tab-inhouse-kanban.active .due-date-high {
                color: #FBBF24 !important;
                font-weight: 600 !important;
            }
            
            #tab-inhouse-kanban.active .due-date-medium {
                color: #3B82F6 !important;
            }
            
            #tab-inhouse-kanban.active .due-date-low {
                color: #9CA3AF !important;
            }
            
            #tab-inhouse-kanban.active .workboard-tab {
                padding: 12px 20px !important;
                background: transparent !important;
                border: none !important;
                border-bottom: 3px solid transparent !important;
                color: #9CA3AF !important;
                font-size: 14px !important;
                font-weight: 600 !important;
                cursor: pointer !important;
                display: flex !important;
                align-items: center !important;
                gap: 12px !important;
                transition: all 0.2s ease !important;
            }
            
            #tab-inhouse-kanban.active .workboard-tab:hover {
                color: #E5E7EB !important;
                background: rgba(0, 80, 158, 0.1) !important;
            }
            
            #tab-inhouse-kanban.active .workboard-tab.active {
                border-bottom-color: #00509E !important;
                background: rgba(0, 80, 158, 0.15) !important;
            }
            
            /* Tab container layout fix - ENABLE VERTICAL SCROLL ON TAB */
            #tab-inhouse-kanban.active {
                display: flex !important;
                flex-direction: column !important;
                height: 100% !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
            }
            
            #tab-inhouse-kanban.active .module-content {
                display: flex !important;
                flex-direction: column !important;
                flex: 1 !important;
                overflow: visible !important;
                min-height: fit-content !important;
            }
            
            /* MODAL - Draggable and Resizable */
            #tab-inhouse-kanban.active .modal-overlay {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                bottom: 0 !important;
                background: rgba(0, 0, 0, 0.7) !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                z-index: 10000 !important;
            }
            
            #tab-inhouse-kanban.active .draggable-modal {
                position: fixed !important;
                background: var(--bg-secondary, #1A1F2E) !important;
                border: 2px solid var(--border-default, #2A3142) !important;
                border-radius: 12px !important;
                box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5) !important;
                z-index: 10000 !important;
                display: flex !important;
                flex-direction: column !important;
                min-width: 500px !important;
                min-height: 400px !important;
                width: 500px !important;
                height: 700px !important;
                max-width: 90vw !important;
                max-height: 90vh !important;
                overflow: hidden !important;
                resize: both !important;
                transition: border-color 0.2s ease !important;
            }
            
            #tab-inhouse-kanban.active .modal-header {
                padding: 20px 24px !important;
                background: linear-gradient(135deg, #2A3142 0%, #1A1F2E 100%) !important;
                border-bottom: 2px solid #00509E !important;
                display: flex !important;
                justify-content: space-between !important;
                align-items: center !important;
                flex-shrink: 0 !important;
                user-select: none !important;
            }
            
            #tab-inhouse-kanban.active .modal-header h3 {
                margin: 0 !important;
                color: #E5E7EB !important;
                font-size: 16px !important;
                font-weight: 700 !important;
                display: flex !important;
                align-items: center !important;
                gap: 12px !important;
            }
            
            #tab-inhouse-kanban.active .modal-header h3 i {
                color: #00509E !important;
                font-size: 16px !important;
            }
            
            #tab-inhouse-kanban.active #modal-body-scroll {
                flex: 1 !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                padding: 24px !important;
                background: var(--bg-secondary, #1A1F2E) !important;
            }
            
            #tab-inhouse-kanban.active .modal-body {
                flex: 1 !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                padding: 24px !important;
                background: var(--bg-secondary, #1A1F2E) !important;
            }
            
            #tab-inhouse-kanban.active .modal-footer {
                padding: 16px 24px !important;
                background: #0B0E13 !important;
                border-top: 1px solid #2A3142 !important;
                display: flex !important;
                justify-content: flex-end !important;
                gap: 12px !important;
                flex-shrink: 0 !important;
            }
            
            #tab-inhouse-kanban.active .modal-close-btn {
                background: transparent !important;
                border: none !important;
                color: #9CA3AF !important;
                font-size: 20px !important;
                cursor: pointer !important;
                padding: 8px !important;
                width: 36px !important;
                height: 36px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                border-radius: 6px !important;
                transition: all 0.2s ease !important;
            }
            
            #tab-inhouse-kanban.active .modal-close-btn:hover {
                background: rgba(239, 68, 68, 0.2) !important;
                color: #EF4444 !important;
            }
            
            /* Resize Handles */
            #tab-inhouse-kanban.active .resize-handle {
                position: absolute !important;
                background: transparent !important;
                z-index: 10 !important;
            }
            
            #tab-inhouse-kanban.active .resize-handle-n {
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                height: 8px !important;
                cursor: ns-resize !important;
            }
            
            #tab-inhouse-kanban.active .resize-handle-s {
                bottom: 0 !important;
                left: 0 !important;
                right: 0 !important;
                height: 8px !important;
                cursor: ns-resize !important;
            }
            
            #tab-inhouse-kanban.active .resize-handle-e {
                top: 0 !important;
                right: 0 !important;
                bottom: 0 !important;
                width: 8px !important;
                cursor: ew-resize !important;
            }
            
            #tab-inhouse-kanban.active .resize-handle-w {
                top: 0 !important;
                left: 0 !important;
                bottom: 0 !important;
                width: 8px !important;
                cursor: ew-resize !important;
            }
            
            #tab-inhouse-kanban.active .resize-handle-ne {
                top: 0 !important;
                right: 0 !important;
                width: 16px !important;
                height: 16px !important;
                cursor: nesw-resize !important;
            }
            
            #tab-inhouse-kanban.active .resize-handle-nw {
                top: 0 !important;
                left: 0 !important;
                width: 16px !important;
                height: 16px !important;
                cursor: nwse-resize !important;
            }
            
            #tab-inhouse-kanban.active .resize-handle-se {
                bottom: 0 !important;
                right: 0 !important;
                width: 16px !important;
                height: 16px !important;
                cursor: nwse-resize !important;
            }
            
            #tab-inhouse-kanban.active .resize-handle-sw {
                bottom: 0 !important;
                left: 0 !important;
                width: 16px !important;
                height: 16px !important;
                cursor: nesw-resize !important;
            }
            
            /* Modal Content Sections - Card Style */
            #tab-inhouse-kanban.active .status-badges {
                display: flex !important;
                gap: 12px !important;
                flex-wrap: wrap !important;
            }
            
            #tab-inhouse-kanban.active .badge {
                padding: 8px 16px !important;
                border-radius: 6px !important;
                font-size: 12px !important;
                font-weight: 700 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
                display: inline-flex !important;
                align-items: center !important;
                gap: 6px !important;
                color: white !important;
            }
            
            /* ==================== KANBAN JOB MODAL - NEW STRUCTURE ==================== */
            /* CRITICAL: NO #tab-inhouse-kanban.active prefix - modal is created outside tab */
            
            .kanban-job-modal {
                position: fixed !important;
                background: #131820 !important;
                border: 3px solid #00509E !important;
                border-radius: 12px !important;
                box-shadow: 0 12px 48px rgba(0, 0, 0, 0.7), 0 0 24px rgba(0, 80, 158, 0.2) !important;
                z-index: 10000 !important;
                display: flex !important;
                flex-direction: column !important;
                min-width: 500px !important;
                min-height: 400px !important;
                width: 600px !important;
                height: 700px !important;
                max-width: 90vw !important;
                max-height: 90vh !important;
                overflow: hidden !important;
                resize: both !important;
            }
            
            .kanban-modal-header {
                background: linear-gradient(135deg, #2A3142 0%, #1A1F2E 100%) !important;
                border-bottom: 2px solid #00509E !important;
                padding: 20px 24px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: space-between !important;
                flex-shrink: 0 !important;
                user-select: none !important;
            }
            
            .kanban-modal-title {
                color: #E5E7EB !important;
                font-size: 16px !important;
                font-weight: 700 !important;
                display: flex !important;
                align-items: center !important;
                gap: 12px !important;
                margin: 0 !important;
            }
            
            .kanban-modal-title i {
                color: #00509E !important;
                font-size: 16px !important;
            }
            
            .kanban-modal-close-btn {
                background: transparent !important;
                border: none !important;
                color: #9CA3AF !important;
                font-size: 20px !important;
                cursor: pointer !important;
                padding: 8px !important;
                width: 36px !important;
                height: 36px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                border-radius: 6px !important;
                transition: all 0.2s ease !important;
            }
            
            .kanban-modal-close-btn:hover {
                background: rgba(239, 68, 68, 0.2) !important;
                color: #EF4444 !important;
            }
            
            .kanban-modal-body {
                flex: 1 !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                padding: 24px !important;
                background: #131820 !important;
            }
            
            /* CONTENT SECTIONS - Title + Content Container */
            .kanban-content-section {
                margin-bottom: 24px !important;
            }
            
            .kanban-content-section:last-child {
                margin-bottom: 0 !important;
            }
            
            .kanban-section-title {
                font-size: 13px !important;
                font-weight: 700 !important;
                color: #00D9FF !important;
                margin-bottom: 14px !important;
                display: flex !important;
                align-items: center !important;
                gap: 10px !important;
                text-transform: uppercase !important;
                letter-spacing: 0.8px !important;
                padding-bottom: 8px !important;
                border-bottom: 2px solid #00509E !important;
            }
            
            .kanban-section-title i {
                color: #00509E !important;
                font-size: 14px !important;
            }
            
            .kanban-section-content {
                background: #0F1419 !important;
                border: 2px solid #00509E !important;
                border-radius: 8px !important;
                padding: 16px !important;
                box-shadow: inset 0 0 0 1px rgba(0, 80, 158, 0.3) !important;
            }
            
            /* DETAIL GRID - For structured data */
            .kanban-detail-grid {
                display: grid !important;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)) !important;
                gap: 12px !important;
            }
            
            .kanban-detail-item {
                display: flex !important;
                flex-direction: column !important;
                gap: 4px !important;
            }
            
            .kanban-detail-label {
                font-size: 10px !important;
                font-weight: 600 !important;
                color: #00D9FF !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
            }
            
            .kanban-detail-value {
                font-size: 14px !important;
                color: #FFFFFF !important;
                font-weight: 600 !important;
            }
            
            /* TEXT CONTENT - For notes */
            .kanban-notes-text {
                background: #1A2332 !important;
                border-left: 4px solid #00D9FF !important;
                padding: 14px !important;
                border-radius: 4px !important;
                color: #FFFFFF !important;
                font-size: 14px !important;
                line-height: 1.6 !important;
                white-space: pre-wrap !important;
                word-wrap: break-word !important;
            }
            
            .kanban-modal-footer {
                background: #0B0E13 !important;
                border-top: 1px solid #2A3142 !important;
                padding: 16px 24px !important;
                display: flex !important;
                justify-content: flex-end !important;
                gap: 12px !important;
                flex-shrink: 0 !important;
            }
            
            /* Button Styling */
            .kanban-modal-footer button {
                padding: 8px 16px !important;
                border-radius: 6px !important;
                font-size: 14px !important;
                font-weight: 600 !important;
                cursor: pointer !important;
                border: none !important;
                transition: all 0.2s ease !important;
            }
        `;

        document.head.appendChild(style);
        console.log('✅ Kanban Modal CSS injected with proper styling');
    }

    /**
     * Apply module-specific colors as CSS variables
     */
    applyModuleColors() {
        // CRITICAL: Safe null-checking for manifest colors
        // Manifest is loaded by super.initialize(), check it exists
        if (!this.manifest) {
            console.warn('⚠️ Manifest not loaded yet, skipping color application');
            return;
        }

        // Use manifest.color (singular) as primary color
        const primaryColor = this.manifest.color || '#00509E';
        const tabContainer = document.getElementById(`tab-${this.moduleId}`);

        if (tabContainer) {
            tabContainer.style.setProperty('--module-primary', primaryColor);
            tabContainer.style.setProperty('--module-primary-light', this.lightenColor(primaryColor, 0.1));
            console.log(`✅ Applied module colors: ${primaryColor}`);
        } else {
            console.warn(`⚠️ Tab container not found: tab-${this.moduleId}`);
        }
    }

    /**
     * Lighten color for backgrounds
     */
    lightenColor(color, opacity) {
        const hex = color.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }

    /**
     * Load initial data
     */
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadJobs(),
                this.loadStages(),
                this.loadMetrics(),
                this.loadStageTransitions() // NEW: Load transition data from analytics DB
            ]);
            this.lastRefresh = new Date();
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showNotification('error', 'Failed to load data from InHouse Print system');
        }
    }

    /**
     * Load stage transitions from analytics database
     */
    async loadStageTransitions() {
        try {
            // Get current job IDs
            const jobIds = this.jobs.map(j => j.TicketID).join(',');
            if (!jobIds) return;

            // For each job, get latest transition (time in current stage)
            for (const job of this.jobs) {
                try {
                    const response = await fetch(`${this.analyticsApiBase}/transitions/${job.TicketID}`);
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success && data.transitions && data.transitions.length > 0) {
                            // Get most recent transition (current stage entry)
                            const latestTransition = data.transitions[data.transitions.length - 1];

                            // Use business_hours and total_hours from analytics database
                            // If not available, calculate from transition_date
                            let businessHours = latestTransition.business_hours;
                            let totalHours = latestTransition.total_hours;

                            if (!businessHours || !totalHours) {
                                // Fallback: calculate from transition date
                                const entryTime = new Date(latestTransition.transition_date);
                                const now = new Date();
                                totalHours = (now - entryTime) / (1000 * 60 * 60);
                                businessHours = totalHours * 0.4; // Rough estimate: 40% of time is business hours
                            }

                            this.stageTransitionCache.set(job.TicketID, {
                                entry_time: latestTransition.transition_date,
                                business_hours: businessHours,
                                total_hours: totalHours,
                                stage_id: latestTransition.to_stage_id,
                                full_history: data.transitions
                            });
                        }
                    }
                } catch (err) {
                    // Silently fail for individual jobs - analytics DB might not have data yet
                    console.debug(`No transition data for job ${job.TicketID}`);
                }
            }

            console.log(`Loaded transition data for ${this.stageTransitionCache.size} jobs`);
        } catch (error) {
            console.warn('Failed to load stage transitions (analytics DB may not be synced yet):', error);
        }
    }

    /**
     * Load jobs from backend
     */
    async loadJobs() {
        try {
            const params = new URLSearchParams({
                timeframe_months: this.filters.timeframe_months,
                priority_filter: this.filters.priority_filter,
                limit: 200
            });

            if (this.filters.stage_id) {
                params.append('stage_id', this.filters.stage_id);
            }

            const response = await fetch(`${this.backendUrl}${this.apiEndpoint}/jobs?${params}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.jobs = data.jobs || [];

            // Apply client-side search filter
            if (this.filters.search_text) {
                this.jobs = this.jobs.filter(job =>
                    job.ClientName?.toLowerCase().includes(this.filters.search_text.toLowerCase()) ||
                    job.ShortJobDesc?.toLowerCase().includes(this.filters.search_text.toLowerCase()) ||
                    job.TicketID?.toString().includes(this.filters.search_text)
                );
            }

            console.log(`Loaded ${this.jobs.length} jobs`);

        } catch (error) {
            console.error('Failed to load jobs:', error);
            throw error;
        }
    }

    /**
     * Load stages summary
     */
    async loadStages() {
        try {
            const response = await fetch(
                `${this.backendUrl}${this.apiEndpoint}/stages?timeframe_months=${this.filters.timeframe_months}`
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.stages = data.stages || [];

        } catch (error) {
            console.error('Failed to load stages:', error);
            throw error;
        }
    }

    /**
     * Load dashboard metrics
     */
    async loadMetrics() {
        try {
            const response = await fetch(
                `${this.backendUrl}${this.apiEndpoint}/metrics?timeframe_months=${this.filters.timeframe_months}`
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.metrics = data.metrics || {};

        } catch (error) {
            console.error('Failed to load metrics:', error);
            throw error;
        }
    }

    /**
     * Refresh all data
     */
    async refreshData() {
        console.log('Refreshing InHouse Print data...');
        const refreshBtn = document.getElementById('inhouse-refresh-btn');
        if (refreshBtn) {
            refreshBtn.innerHTML = '<i class="fas fa-sync fa-spin"></i> Refreshing...';
            refreshBtn.disabled = true;
        }

        try {
            await this.loadInitialData();

            // Re-render current view
            if (this.currentView === 'kanban-board') {
                this.renderKanbanBoard();
            } else if (this.currentView === 'analytics') {
                this.renderAnalytics();
            }

            this.showNotification('success', 'Data refreshed successfully');

        } catch (error) {
            this.showNotification('error', 'Failed to refresh data');
        } finally {
            if (refreshBtn) {
                refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh';
                refreshBtn.disabled = false;
            }
        }
    }

    /**
     * Initialize sub-tabs
     */
    initializeSubTabs() {
        this.initializeKanbanBoard();
        this.initializeAnalytics();
    }

    /**
     * Initialize Kanban Board tab
     */
    initializeKanbanBoard() {
        const container = this.getSubTabContainer('kanban-board');
        const primaryColor = this.manifest?.colors?.primary || '#00509E';

        container.innerHTML = `
            <div class="filters-bar">
                <div class="filter-group">
                    <label><i class="fas fa-calendar-alt"></i> Timeframe:</label>
                    <select id="timeframe-selector" class="filter-select">
                        <option value="-1">Last 1 month</option>
                        <option value="-2">Last 2 months</option>
                        <option value="-3">Last 3 months</option>
                        <option value="-6" selected>Last 6 months</option>
                        <option value="-9">Last 9 months</option>
                        <option value="-12">Last 12 months</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label><i class="fas fa-filter"></i> Priority:</label>
                    <select id="priority-selector" class="filter-select">
                        <option value="all">All Priorities</option>
                        <option value="critical">Critical Only</option>
                        <option value="high">High Priority</option>
                        <option value="urgent">Urgent</option>
                        <option value="normal">Normal</option>
                        <option value="low">Low Priority</option>
                    </select>
                </div>
                
                <div class="filter-group" style="flex: 1;">
                    <label><i class="fas fa-search"></i> Search:</label>
                    <input type="text" id="search-input" class="filter-input" placeholder="Search by client, job, or ticket #...">
                </div>
                
                <div class="filter-group">
                    <button id="inhouse-refresh-btn" class="btn-secondary" style="border-color: ${primaryColor};">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </div>
                
                <div class="filter-group">
                    <span class="last-refresh" id="last-refresh-time">
                        <span class="time-value">Just now</span>
                    </span>
                </div>
            </div>
            
            <!-- Color Toggle Controls -->
            <div style="margin: 15px 20px; padding: 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 8px; color: #8b949e; font-weight: bold;">
                    <i class="fas fa-palette"></i>
                    <span>Color Coding:</span>
                </div>
                <button id="toggle-border-colors" class="color-toggle-btn active" 
                        onclick="window.currentKanbanModule.toggleColorSetting('showBorderColors')" 
                        style="padding: 6px 14px; border: 2px solid #58a6ff; background: #0d1117; color: #58a6ff; border-radius: 6px; cursor: pointer; font-size: 0.9em; display: flex; align-items: center; gap: 6px; transition: all 0.2s;">
                    <i class="fas fa-border-left"></i>
                    <span>Border (Priority)</span>
                    <i class="fas fa-check" style="color: #22c55e;"></i>
                </button>
                <button id="toggle-background-colors" class="color-toggle-btn active" 
                        onclick="window.currentKanbanModule.toggleColorSetting('showBackgroundColors')" 
                        style="padding: 6px 14px; border: 2px solid #58a6ff; background: #0d1117; color: #58a6ff; border-radius: 6px; cursor: pointer; font-size: 0.9em; display: flex; align-items: center; gap: 6px; transition: all 0.2s;">
                    <i class="fas fa-fill"></i>
                    <span>Background (Due Date)</span>
                    <i class="fas fa-check" style="color: #22c55e;"></i>
                </button>
                <button id="toggle-banner-colors" class="color-toggle-btn active" 
                        onclick="window.currentKanbanModule.toggleColorSetting('showBannerColors')" 
                        style="padding: 6px 14px; border: 2px solid #58a6ff; background: #0d1117; color: #58a6ff; border-radius: 6px; cursor: pointer; font-size: 0.9em; display: flex; align-items: center; gap: 6px; transition: all 0.2s;">
                    <i class="fas fa-flag"></i>
                    <span>Banner (Urgency)</span>
                    <i class="fas fa-check" style="color: #22c55e;"></i>
                </button>
                <div style="margin-left: auto; font-size: 0.85em; color: #8b949e;">
                    <i class="fas fa-info-circle"></i> Click buttons to toggle color coding on/off
                </div>
            </div>
            
            <!-- Detailed Color Legend -->
            <details class="color-legend-expander" style="margin: 15px 20px; border: 1px solid #30363d; border-radius: 6px; background: #161b22; padding: 10px;">
                <summary style="cursor: pointer; font-weight: bold; color: #58a6ff; padding: 8px; user-select: none; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-info-circle"></i> Card Color Guide (Read-Only Reference)
                    <span style="font-size: 0.85em; color: #8b949e; font-weight: normal; margin-left: auto;">(Click to expand)</span>
                </summary>
                <div style="padding: 15px 10px 5px 10px;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                        
                        <!-- Left Border Colors (Priority) -->
                        <div>
                            <h4 style="color: #f0f6fc; margin: 0 0 10px 0; font-size: 0.95em; display: flex; align-items: center; gap: 6px;">
                                <i class="fas fa-border-left"></i> Left Border = Priority Level
                            </h4>
                            <div style="display: flex; flex-direction: column; gap: 6px; font-size: 0.9em;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 6px; height: 30px; background: #B71C1C; border-radius: 2px;"></div>
                                    <span style="color: #f0f6fc;"><strong>CRITICAL</strong> (800+)</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 6px; height: 30px; background: #D32F2F; border-radius: 2px;"></div>
                                    <span style="color: #f0f6fc;"><strong>HIGH</strong> (600-799)</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 6px; height: 30px; background: #FF8800; border-radius: 2px;"></div>
                                    <span style="color: #f0f6fc;"><strong>MEDIUM</strong> (400-599)</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 6px; height: 30px; background: #4CAF50; border-radius: 2px;"></div>
                                    <span style="color: #f0f6fc;"><strong>NORMAL</strong> (200-399)</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 6px; height: 30px; background: #2196F3; border-radius: 2px;"></div>
                                    <span style="color: #f0f6fc;"><strong>LOW</strong> (0-199)</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Border Colors (Due Date) -->
                        <div>
                            <h4 style="color: #f0f6fc; margin: 0 0 10px 0; font-size: 0.95em; display: flex; align-items: center; gap: 6px;">
                                <i class="fas fa-border-style"></i> Top/Right/Bottom Borders = Due Date
                            </h4>
                            <div style="display: flex; flex-direction: column; gap: 6px; font-size: 0.85em;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 50px; height: 3px; background: #8B0000; border-radius: 1px; border: 1px dotted #8B0000;"></div>
                                    <span style="color: #f0f6fc;"><strong style="color: #8B0000;">Dotted Dark Red</strong> - 8+ days overdue</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 50px; height: 4px; background: #E53935; border-radius: 1px;"></div>
                                    <span style="color: #f0f6fc;"><strong style="color: #E53935;">Solid Red</strong> - 4-7 days overdue</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 50px; height: 4px; background: #B71C1C; border-radius: 1px; box-shadow: 0 0 6px rgba(183, 28, 28, 0.6);"></div>
                                    <span style="color: #f0f6fc;"><strong style="color: #B71C1C;">Dark Red + PULSE</strong> - 1-3 days overdue</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 50px; height: 4px; background: #FF6D00; border-radius: 1px;"></div>
                                    <span style="color: #f0f6fc;"><strong style="color: #FF6D00;">Vibrant Orange</strong> - Due TODAY</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 50px; height: 4px; background: #f3ff4e; border-radius: 1px;"></div>
                                    <span style="color: #f0f6fc;"><strong style="color: #f3ff4e;">Bright Yellow</strong> - Due TOMORROW</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 50px; height: 4px; background: #2196F3; border-radius: 1px;"></div>
                                    <span style="color: #f0f6fc;"><strong style="color: #2196F3;">Solid Blue</strong> - Due in 2-3 days</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 50px; height: 3px; background: #4CAF50; border-radius: 1px; border: 1px dashed #4CAF50;"></div>
                                    <span style="color: #f0f6fc;"><strong style="color: #4CAF50;">Dashed Blue</strong> - Due in 4-5 days</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 50px; height: 3px; background: #4CAF50; border-radius: 1px; border: 1px dashed #4CAF50;"></div>
                                    <span style="color: #f0f6fc;"><strong style="color: #4CAF50;">Dashed Green</strong> - Due in 6-7 days</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 50px; height: 2px; background: #FFFFFF; border-radius: 1px; border: 1px dashed #FFFFFF;"></div>
                                    <span style="color: #f0f6fc;"><strong style="color: #FFFFFF;">Thin White</strong> - Due in 8+ days</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Banner Colors (Top Alert) -->
                        <div>
                            <h4 style="color: #f0f6fc; margin: 0 0 10px 0; font-size: 0.95em; display: flex; align-items: center; gap: 6px;">
                                <i class="fas fa-flag"></i> Top Banner = Urgency Alert
                            </h4>
                            <div style="display: flex; flex-direction: column; gap: 6px; font-size: 0.9em;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 40px; height: 24px; background: #B71C1C; border: 1px solid #ccc; border-radius: 3px;"></div>
                                    <span style="color: #f0f6fc;"><strong>OVERDUE 7+</strong></span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 40px; height: 24px; background: #D32F2F; border: 1px solid #ccc; border-radius: 3px;"></div>
                                    <span style="color: #f0f6fc;"><strong>OVERDUE</strong></span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 40px; height: 24px; background: #FF6F00; border: 3px solid #D32F2F; border-radius: 3px;"></div>
                                    <span style="color: #f0f6fc;"><strong>DUE TODAY</strong></span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 40px; height: 24px; background: #FFB300; border: 1px solid #ccc; border-radius: 3px;"></div>
                                    <span style="color: #f0f6fc;"><strong>TOMORROW</strong></span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 40px; height: 24px; background: #FFF176; border: 1px solid #ccc; border-radius: 3px;"></div>
                                    <span style="color: #f0f6fc;"><strong>2-3 DAYS</strong></span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 40px; height: 24px; background: #52f757; border: 1px solid #ccc; border-radius: 3px;"></div>
                                    <span style="color: #f0f6fc;"><strong>4-7 DAYS</strong></span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="width: 40px; height: 24px; background: #2568f7; border: 1px solid #ccc; border-radius: 3px;"></div>
                                    <span style="color: #f0f6fc;"><strong>8+ DAYS</strong></span>
                                </div>
                            </div>
                        </div>
                        
                    </div>
                    
                    <div style="margin-top: 15px; padding-top: 12px; border-top: 1px solid #30363d; font-size: 0.85em; color: #8b949e;">
                        <strong style="color: #58a6ff;">Tip:</strong> Cards combine all three color elements to show priority, urgency, and due date status at a glance. 
                        On Hold jobs always show grey background regardless of due date.
                    </div>
                </div>
            </details>
            
            <!-- Card Customisations (Advanced Settings - Placed AFTER Color Guide) -->
            <details class="card-customisations-expander" open style="margin: 15px 20px; border: 2px solid #58a6ff; border-radius: 8px; background: #161b22; padding: 12px;">
                <summary style="cursor: pointer; font-weight: bold; color: #58a6ff; padding: 10px; user-select: none; display: flex; align-items: center; gap: 10px; font-size: 1.05em;">
                    <i class="fas fa-cogs"></i> Advanced Color Customization
                    <span style="font-size: 0.85em; color: #8b949e; font-weight: normal; margin-left: auto;">(Edit colors, borders, & styles - LINKED TO GUIDE ABOVE)</span>
                </summary>
                <div style="padding: 20px;">
                
                    <p style="color: #fbbf24; background: rgba(251, 191, 36, 0.1); padding: 12px; border-radius: 6px; border-left: 4px solid #fbbf24; margin-bottom: 20px; font-size: 0.9em;">
                        <i class="fas fa-link"></i> <strong>Note:</strong> Changes here update the Color Guide above in real-time. Test before saving!
                    </p>

                    <!-- PRIORITY SETTINGS (Left Border) -->
                    <div style="margin-bottom: 30px;">
                        <h3 style="color: #f0f6fc; margin: 0 0 15px 0; font-size: 1.1em; display: flex; align-items: center; gap: 8px; border-bottom: 2px solid #30363d; padding-bottom: 10px;">
                            <i class="fas fa-border-left" style="color: #58a6ff;"></i> Priority Settings (Left Border)
                        </h3>
                        
                        <div style="overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse; background: #0d1117; border-radius: 6px; overflow: hidden;">
                                <thead>
                                    <tr style="background: #161b22; border-bottom: 2px solid #30363d;">
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">PRIORITY</th>
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">COLOR</th>
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">WIDTH</th>
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">PREVIEW</th>
                                    </tr>
                                </thead>
                                <tbody id="priority-settings-table">
                                    <!-- Dynamic rows will be inserted here -->
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- DUE DATE SETTINGS (Card Borders & Backgrounds) -->
                    <div style="margin-bottom: 30px;">
                        <h3 style="color: #f0f6fc; margin: 0 0 15px 0; font-size: 1.1em; display: flex; align-items: center; gap: 8px; border-bottom: 2px solid #30363d; padding-bottom: 10px;">
                            <i class="fas fa-calendar-alt" style="color: #58a6ff;"></i> Due Date Settings (Card Borders & Backgrounds)
                        </h3>
                        
                        <div style="overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse; background: #0d1117; border-radius: 6px; overflow: hidden;">
                                <thead>
                                    <tr style="background: #161b22; border-bottom: 2px solid #30363d;">
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">DAYS RANGE</th>
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">BORDER COLOR</th>
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">BORDER TYPE</th>
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">WIDTH</th>
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">PULSE</th>
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">BG COLOR</th>
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">PREVIEW</th>
                                    </tr>
                                </thead>
                                <tbody id="duedate-settings-table">
                                    <!-- Dynamic rows will be inserted here -->
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- BANNER SETTINGS (Top Alert Banner) -->
                    <div style="margin-bottom: 30px;">
                        <h3 style="color: #f0f6fc; margin: 0 0 15px 0; font-size: 1.1em; display: flex; align-items: center; gap: 8px; border-bottom: 2px solid #30363d; padding-bottom: 10px;">
                            <i class="fas fa-flag" style="color: #58a6ff;"></i> Banner Settings (Top Urgency Alert)
                        </h3>
                        
                        <div style="overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse; background: #0d1117; border-radius: 6px; overflow: hidden;">
                                <thead>
                                    <tr style="background: #161b22; border-bottom: 2px solid #30363d;">
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">STATE</th>
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">BG COLOR</th>
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">TEXT</th>
                                        <th style="padding: 12px; text-align: left; color: #8b949e; font-size: 0.85em;">PREVIEW</th>
                                    </tr>
                                </thead>
                                <tbody id="banner-settings-table">
                                    <!-- Dynamic rows will be inserted here -->
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- ACTION BUTTONS -->
                    <div style="display: flex; gap: 12px; justify-content: flex-end; padding: 20px; background: #0d1117; border-radius: 6px; border: 2px solid #30363d;">
                        <button onclick="window.currentKanbanModule.testAdvancedColorSettings()" 
                                style="padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.95em; display: flex; align-items: center; gap: 8px; font-weight: bold;">
                                <i class="fas fa-flask"></i> Test Settings (Preview Only)
                        </button>
                        <button onclick="window.currentKanbanModule.saveAdvancedColorSettings()" 
                                style="padding: 10px 20px; background: #10b981; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.95em; display: flex; align-items: center; gap: 8px; font-weight: bold;">
                                <i class="fas fa-database"></i> Save to Database
                        </button>
                        <button onclick="window.currentKanbanModule.resetAdvancedColorSettings()" 
                                style="padding: 10px 20px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.95em; display: flex; align-items: center; gap: 8px; font-weight: bold;">
                                <i class="fas fa-undo-alt"></i> Reset to Defaults
                        </button>
                    </div>

                    <!-- MUTE OPTIONS (Collapsed by Default) -->
                    <details style="margin-top: 30px; padding: 15px; background: #0d1117; border-radius: 6px; border: 1px solid #30363d;">
                        <summary style="cursor: pointer; font-weight: bold; color: #fbbf24; padding: 8px; user-select: none; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-eye-slash"></i> Per-Card Mute Options
                            <span class="muted-cards-count" style="font-size: 0.85em; color: #58a6ff; font-weight: normal; margin-left: auto;"></span>
                        </summary>
                        <div style="padding: 15px 10px;">
                            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px;">
                                <button onclick="window.currentKanbanModule.clearAllMutedCards()" 
                                        style="padding: 6px 12px; background: #21262d; color: #f0f6fc; border: 1px solid #30363d; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                                    <i class="fas fa-eraser"></i> Clear All Mutes
                                </button>
                                <button onclick="window.currentKanbanModule.showMutedCardsOnly()" 
                                        style="padding: 6px 12px; background: #21262d; color: #f0f6fc; border: 1px solid #30363d; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                                    <i class="fas fa-filter"></i> Show Muted Only
                                </button>
                                <button onclick="window.currentKanbanModule.exportMutedCards()" 
                                        style="padding: 6px 12px; background: #21262d; color: #f0f6fc; border: 1px solid #30363d; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                                    <i class="fas fa-download"></i> Export List
                                </button>
                            </div>
                            <p style="color: #8b949e; font-size: 0.85em;">
                                <i class="fas fa-info-circle"></i> Click any card to access per-card mute options in the job details modal.
                            </p>
                        </div>
                    </details>

                </div>
            </details>
            
            <div class="workboard-selector" id="workboard-selector"></div>
            
            <div class="kanban-metrics" id="kanban-metrics"></div>
            
            <div class="kanban-board" id="kanban-board"></div>
        `;

        // Render initial content AFTER adding HTML to DOM
        // Load data first, then render
        this.loadInitialData().then(() => {
            this.renderWorkboardSelector();
            this.renderMetrics();
            this.renderKanbanBoard();
            this.updateLastRefreshTime();
            this.updateMutedCardCount();
            this.updateColorToggleButtons();
            this.renderAdvancedColorTables(); // Populate customization tables
            this.attachFilterListeners();
        }).catch(error => {
            console.error('Failed to load initial data:', error);
            this.showNotification('error', 'Failed to load production data');
        });
    }

    /**
     * Render top metrics row
     */
    renderMetrics() {
        const container = document.getElementById('kanban-metrics');
        if (!container) return;

        const primaryColor = this.manifest?.colors?.primary || '#00509E';

        container.innerHTML = `
            ${this.createMetricCard('Total Active Jobs', this.metrics.total_jobs || 0, 'fas fa-clipboard-list', primaryColor)}
            ${this.createMetricCard('Pipeline Value', '$' + this.formatCurrency(this.metrics.pipeline_value || 0), 'fas fa-dollar-sign', '#22c55e')}
            ${this.createMetricCard('Overdue Jobs', this.metrics.overdue_jobs || 0, 'fas fa-exclamation-triangle', '#ef4444')}
            ${this.createMetricCard('Avg Days in System', (this.metrics.avg_days_in_system || 0).toFixed(1), 'fas fa-clock', '#f97316')}
        `;
    }

    /**
     * Create metric card HTML
     */
    createMetricCard(label, value, icon, color) {
        return `
            <div class="metric-card">
                <div class="metric-icon" style="background: ${this.lightenColor(color, 0.1)}; color: ${color};">
                    <i class="${icon}"></i>
                </div>
                <div class="metric-content">
                    <div class="metric-value">${value}</div>
                    <div class="metric-label">${label}</div>
                </div>
            </div>
        `;
    }

    /**
     * Render workboard selector tabs
     */
    renderWorkboardSelector() {
        const container = document.getElementById('workboard-selector');
        if (!container) return;

        let tabsHtml = '';
        Object.keys(this.workboards).forEach(boardKey => {
            const board = this.workboards[boardKey];
            const isActive = boardKey === this.activeWorkboard ? 'active' : '';
            tabsHtml += `
                <button class="workboard-tab ${isActive}" onclick="window.ModuleRegistry['inhouse-kanban'].switchWorkboard('${boardKey}')">
                    <i class="fas ${board.icon}"></i>
                    ${board.name}
                </button>
            `;
        });

        container.innerHTML = tabsHtml;
    }

    /**
     * Switch to a different workboard
     */
    switchWorkboard(boardKey) {
        this.activeWorkboard = boardKey;
        this.renderWorkboardSelector();
        this.renderKanbanBoard();
    }

    /**
     * Get ordered stages for current workboard
     */
    /**
     * Get stages for current workboard, filtered and ordered by StageID
     */
    getOrderedStages() {
        const workboard = this.workboards[this.activeWorkboard];
        const allowedStageIds = workboard.stages;  // Array of numeric StageIDs

        console.log('🔷 getOrderedStages() called');
        console.log('  Active workboard:', this.activeWorkboard);
        console.log('  Allowed stage IDs:', allowedStageIds);
        console.log('  All stages available:', this.stages.map(s => `${s.StageID}: ${s.StageDescription}`));

        // Filter stages based on workboard definition (by StageID)
        const filtered = this.stages.filter(stage => allowedStageIds.includes(stage.StageID));

        console.log('  Filtered stages:', filtered.map(s => `${s.StageID}: ${s.StageDescription}`));

        // Sort by the order defined in workboard config
        return filtered.sort((a, b) => {
            const aOrder = allowedStageIds.indexOf(a.StageID);
            const bOrder = allowedStageIds.indexOf(b.StageID);
            return aOrder - bOrder;
        });
    }

    /**
     * Attach filter event listeners
     */
    attachFilterListeners() {
        const timeframeSelector = document.getElementById('timeframe-selector');
        const prioritySelector = document.getElementById('priority-selector');
        const searchInput = document.getElementById('search-input');
        const refreshBtn = document.getElementById('inhouse-refresh-btn');

        if (timeframeSelector) {
            timeframeSelector.addEventListener('change', (e) => {
                this.filters.timeframe_months = parseInt(e.target.value);
                this.loadJobs();
                this.renderKanbanBoard();
            });
        }

        if (prioritySelector) {
            prioritySelector.addEventListener('change', (e) => {
                this.filters.priority_filter = e.target.value;
                this.applyPriorityFilter();
                this.renderKanbanBoard();
            });
        }

        if (searchInput) {
            searchInput.addEventListener('keyup', (e) => {
                this.filters.search_text = e.target.value;
                this.loadJobs();
                this.renderKanbanBoard();
            });
        }

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }
    }

    /**
     * Apply priority filter to jobs
     */
    applyPriorityFilter() {
        if (this.filters.priority_filter === 'all') return;

        this.jobs = this.jobs.filter(job => {
            const score = job.AIPriorityScore || 0;
            switch (this.filters.priority_filter) {
                case 'critical':
                    return score >= 800;
                case 'high':
                    return score >= 600;
                case 'urgent':
                    return score >= 400;
                case 'normal':
                    return score >= 200;
                case 'low':
                    return score < 200;
                default:
                    return true;
            }
        });
    }

    /**
     * Render Kanban board with proper columns for active workboard
     */
    renderKanbanBoard() {
        const container = document.getElementById('kanban-board');
        if (!container) {
            console.error('❌ Kanban board container not found!');
            return;
        }

        console.log('🔷 renderKanbanBoard() called');
        console.log('  Total jobs:', this.jobs.length);
        console.log('  Total stages:', this.stages.length);

        // Group jobs by stage ID (numeric)
        const jobsByStageId = {};
        this.stages.forEach(stage => {
            jobsByStageId[stage.StageID] = [];
        });

        this.jobs.forEach(job => {
            if (jobsByStageId[job.StageID]) {
                jobsByStageId[job.StageID].push(job);
            }
        });

        console.log('  Jobs grouped by stage:', Object.keys(jobsByStageId).map(id => `${id}: ${jobsByStageId[id].length} jobs`));

        // Get ordered stages for current workboard
        const orderedStages = this.getOrderedStages();

        console.log('  Ordered stages for rendering:', orderedStages.length);

        // If no stages for workboard, show message
        if (orderedStages.length === 0) {
            console.warn('⚠️  No stages returned from getOrderedStages()');
            container.innerHTML = '<div class="empty-column" style="grid-column: 1/-1; text-align: center; padding: 40px;"><i class="fas fa-inbox" style="font-size: 48px; opacity: 0.3;"></i><p>No stages configured for this workboard</p></div>';
            return;
        }

        // Render columns for each stage in the workboard
        console.log('  Rendering columns...');
        container.innerHTML = orderedStages
            .map(stage => this.renderStageColumn(stage, jobsByStageId[stage.StageID] || []))
            .join('');

        console.log('✅ Kanban board rendered successfully');
    }

    /**
     * Render stage column
     */
    renderStageColumn(stage, jobs) {
        const primaryColor = this.manifest?.colors?.primary || '#00509E';
        const stageInfo = this.stageMapping[stage.StageDescription] || {};
        const stageIcon = stageInfo.icon ? `<i class="fas ${stageInfo.icon}"></i>` : '';
        const stageColor = stageInfo.color || primaryColor;
        const stageName = stageInfo.label || stage.StageDescription || 'Unknown Stage';

        return `
            <div class="kanban-column" data-stage-id="${stage.StageID}" style="border-left: 4px solid ${stageColor};">
                <div class="column-header" style="border-bottom-color: ${stageColor}; background: linear-gradient(135deg, ${stageColor}20 0%, ${stageColor}10 100%);">
                    <h3 class="column-title">${stageIcon} ${this.escapeHtml(stageName)}</h3>
                    <div class="column-metrics">
                        <span class="job-count"><i class="fas fa-layer-group"></i> ${stage.JobCount || 0}</span>
                        <span class="stage-value"><i class="fas fa-tag"></i> ${this.formatCurrency(stage.TotalValue || 0)}</span>
                    </div>
                </div>
                
                <div class="column-body" 
                     ondragover="event.preventDefault(); event.currentTarget.style.background='#1c2128';"
                     ondragleave="event.currentTarget.style.background='';"
                     ondrop="window.ModuleRegistry['inhouse-kanban'].handleDrop(event, ${stage.StageID}, '${this.escapeHtml(stageName)}'); event.currentTarget.style.background='';">
                    ${jobs.length > 0 ? jobs.map(job => this.renderJobCard(job)).join('') : '<div class="empty-column"><i class="fas fa-inbox"></i> No jobs</div>'}
                </div>
            </div>
        `;
    }    /**
     * Render job card (simplified Synergy style with stage timestamp)
     */
    renderJobCard(job) {
        const priorityColor = job.PriorityColorHex || '#6b7280';
        const priorityInfo = this.getPriorityInfo(job.AIPriorityScore);

        // Calculate time in current stage (from cache if available)
        const stageTimeInfo = this.calculateTimeInStage(job);

        // Get color coding (respects toggle settings)
        const cardStyles = this.getCardColorStyles(job);

        return `
            <div class="kanban-card${cardStyles.pulseClass}" 
                 data-job-id="${job.TicketID}"
                 data-stage-id="${job.StageID}"
                 draggable="true"
                 ondragstart="window.ModuleRegistry['inhouse-kanban'].handleDragStart(event, ${job.TicketID}, ${job.StageID})"
                 onclick="window.ModuleRegistry['inhouse-kanban'].showJobDetailsModal(${job.TicketID})"
                 style="${cardStyles.cardStyle}">
                
                ${cardStyles.banner}
                
                <div class="card-header">
                    <div class="card-priority" style="color: ${priorityColor};">
                        <i class="fas ${priorityInfo.icon}"></i>
                    </div>
                </div>
                
                <div class="card-title">${this.escapeHtml(job.ShortJobDesc || 'No description')}</div>
                
                <div class="card-meta">
                    <div class="card-project">
                        <i class="fas fa-building"></i>
                        ${this.escapeHtml(job.ClientName || 'Unknown Client')}
                    </div>
                    <div class="card-status-row">
                        <span class="status-badge ${this.getStatusClass(job.WIPStatus)}">
                            ${job.WIPStatus || 'ACTIVE'}
                        </span>
                        <span class="card-time">${job.DaysInSystem || 0}d in system</span>
                    </div>
                </div>
                
                <div class="card-stage-time ${stageTimeInfo.cssClass}">
                    <i class="fas fa-clock"></i>
                    <span class="stage-time-text">${stageTimeInfo.display}</span>
                </div>
                
                <div class="card-footer">
                    <div class="card-tags">
                        <span class="card-tag"><i class="fas fa-hashtag"></i> ${job.TicketID}</span>
                        <span class="card-tag"><i class="fas fa-dollar-sign"></i> ${this.formatCurrency(job.Cost || 0)}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Get card color styles based on toggle settings
     * Returns border, background, banner styling, and pulse class
     */
    getCardColorStyles(job) {
        let cardStyle = '';
        let banner = '';
        let pulseClass = '';

        // BORDER COLORS (Priority) - Controlled by showBorderColors toggle
        if (this.colorToggles.showBorderColors) {
            const priorityColor = job.PriorityColorHex || '#6b7280';
            cardStyle += `border-left: 4px solid ${priorityColor} !important; `;
        }

        // BACKGROUND COLORS (Due Date Borders & Backgrounds) - Controlled by showBackgroundColors toggle
        if (this.colorToggles.showBackgroundColors && job.DateRequired) {
            const daysUntilDue = this.calculateDaysUntilDue(job.DateRequired);
            const dueDateColors = this.getDueDateColors(daysUntilDue);
            if (dueDateColors) {
                // Apply border (overrides priority border if both toggles are on)
                cardStyle += `border: ${dueDateColors.borderWidth} ${dueDateColors.borderStyle} ${dueDateColors.borderColor} !important; `;
                // Apply background
                if (dueDateColors.backgroundColor) {
                    cardStyle += `background-color: ${dueDateColors.backgroundColor} !important; `;
                }
                // Apply pulse animation if enabled
                if (dueDateColors.pulse) {
                    pulseClass = ' pulse-border';
                }
            }
        }

        // BANNER COLORS (Urgency Alert) - Controlled by showBannerColors toggle
        if (this.colorToggles.showBannerColors && job.UrgencyLevel) {
            const bannerInfo = this.getUrgencyBannerInfo(job.UrgencyLevel);
            if (bannerInfo) {
                banner = `
                    <div style="background: ${bannerInfo.color}; color: ${bannerInfo.textColor}; 
                                padding: 4px 8px; font-size: 11px; font-weight: 600; 
                                text-align: center; text-transform: uppercase; letter-spacing: 0.5px;">
                        ${bannerInfo.text}
                    </div>
                `;
            }
        }

        return { cardStyle, banner, pulseClass };
    }

    /**
     * Calculate days until due date
     */
    calculateDaysUntilDue(dateRequired) {
        if (!dateRequired) return null;
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const dueDate = new Date(dateRequired);
        dueDate.setHours(0, 0, 0, 0);
        const diffTime = dueDate - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    }

    /**
     * Get due date border and background colors based on days until due
     * Returns object with borderColor, borderStyle, borderWidth, backgroundColor, and pulse
     */
    getDueDateColors(daysUntilDue) {
        if (daysUntilDue === null) return null;

        // 8+ days overdue - Dark red, solid, thick border with red background + PULSE
        if (daysUntilDue <= -8) {
            return {
                borderColor: '#dc2626',
                borderStyle: 'solid',
                borderWidth: '3px',
                backgroundColor: 'rgba(220, 38, 38, 0.25)',
                pulse: true
            };
        }

        // 4-7 days overdue - Red, solid border with red background + PULSE
        if (daysUntilDue <= -4) {
            return {
                borderColor: '#ef4444',
                borderStyle: 'solid',
                borderWidth: '3px',
                backgroundColor: 'rgba(239, 68, 68, 0.20)',
                pulse: true
            };
        }

        // 2-3 days overdue - Light red, dashed border with pink background + PULSE
        if (daysUntilDue <= -2) {
            return {
                borderColor: '#f87171',
                borderStyle: 'dashed',
                borderWidth: '2px',
                backgroundColor: 'rgba(248, 113, 113, 0.15)',
                pulse: true
            };
        }

        // 1 day overdue - Orange-red, dashed border with light red background
        if (daysUntilDue === -1) {
            return {
                borderColor: '#fb923c',
                borderStyle: 'dashed',
                borderWidth: '2px',
                backgroundColor: 'rgba(251, 146, 60, 0.12)',
                pulse: false
            };
        }

        // Due today - Orange, solid border with orange background
        if (daysUntilDue === 0) {
            return {
                borderColor: '#f59e0b',
                borderStyle: 'solid',
                borderWidth: '2px',
                backgroundColor: 'rgba(245, 158, 11, 0.15)',
                pulse: false
            };
        }

        // Due tomorrow - Yellow, dotted border with yellow background
        if (daysUntilDue === 1) {
            return {
                borderColor: '#fbbf24',
                borderStyle: 'dotted',
                borderWidth: '2px',
                backgroundColor: 'rgba(251, 191, 36, 0.12)',
                pulse: false
            };
        }

        // Due in 2-3 days - Light yellow, dotted border with pale yellow background
        if (daysUntilDue <= 3) {
            return {
                borderColor: '#fde047',
                borderStyle: 'dotted',
                borderWidth: '2px',
                backgroundColor: 'rgba(253, 224, 71, 0.08)',
                pulse: false
            };
        }

        // Due in 4-7 days - Very light yellow, dotted border with very pale background
        if (daysUntilDue <= 7) {
            return {
                borderColor: '#fef08a',
                borderStyle: 'dotted',
                borderWidth: '2px',
                backgroundColor: 'rgba(254, 240, 138, 0.05)',
                pulse: false
            };
        }

        // 8+ days in future - No special styling
        return null;
    }

    /**
     * Get urgency banner info based on urgency level
     */
    getUrgencyBannerInfo(urgencyLevel) {
        if (!urgencyLevel) return null;
        const level = urgencyLevel.toUpperCase();

        const bannerMap = {
            'CRITICAL_OVERDUE': { color: '#dc2626', textColor: '#ffffff', text: 'CRITICAL OVERDUE' },
            'SEVERE_OVERDUE': { color: '#dc2626', textColor: '#ffffff', text: 'SEVERE OVERDUE' },
            'OVERDUE': { color: '#ef4444', textColor: '#ffffff', text: 'OVERDUE' },
            'DUE_TODAY': { color: '#f59e0b', textColor: '#000000', text: 'DUE TODAY' },
            'DUE_SOON': { color: '#fbbf24', textColor: '#000000', text: 'DUE SOON' },
            'UPCOMING': { color: '#a3a3a3', textColor: '#000000', text: 'UPCOMING' }
        };

        return bannerMap[level] || null;
    }


    /**
     * Calculate time in current stage with duration-based styling
     * Shows both business hours and total hours
     * @returns {Object} {display: string, cssClass: string, hours: number}
     */
    calculateTimeInStage(job) {
        // Try to get from cache
        const cachedTransition = this.stageTransitionCache?.get(job.TicketID);
        if (cachedTransition) {
            const businessHours = cachedTransition.business_hours || 0;
            const totalHours = cachedTransition.total_hours || 0;
            let display = '';
            let cssClass = '';

            // Format business hours display text
            let businessDisplay = '';
            if (businessHours < 1) {
                businessDisplay = `${Math.round(businessHours * 60)}m`;
            } else if (businessHours < 24) {
                businessDisplay = `${Math.round(businessHours * 10) / 10}h`;
            } else {
                businessDisplay = `${Math.round(businessHours / 24 * 10) / 10}d`;
            }

            // Format total hours display text
            let totalDisplay = '';
            if (totalHours < 24) {
                totalDisplay = `${Math.round(totalHours * 10) / 10}h`;
            } else {
                totalDisplay = `${Math.round(totalHours / 24 * 10) / 10}d`;
            }

            // Combined display: "2.5h work (3.2h total)"
            display = `${businessDisplay} work (${totalDisplay} total)`;

            // Add CSS class based on business hours duration (warning thresholds)
            // Jobs with > 30 business hours (3+ working days) get yellow
            // Jobs with > 70 business hours (7+ working days) get red
            if (businessHours > 70) {  // > 7 working days
                cssClass = 'very-long-duration';
            } else if (businessHours > 30) {  // > 3 working days
                cssClass = 'long-duration';
            }

            return { display, cssClass, hours: businessHours };
        }

        // Fallback: no data available
        return { display: 'In this stage', cssClass: '', hours: 0 };
    }

    /**
     * Get status badge class
     */
    getStatusClass(wipStatus) {
        if (!wipStatus) return 'status-active';
        const status = wipStatus.toLowerCase();
        if (status.includes('delayed')) return 'status-delayed';
        if (status.includes('risk')) return 'status-warning';
        return 'status-active';
    }

    /**
     * Get due date CSS class based on urgency level
     */
    getDueDateClass(urgencyLevel) {
        if (!urgencyLevel) return '';
        const level = urgencyLevel.toUpperCase();
        if (level === 'OVERDUE') return 'due-date-overdue';
        if (level === 'CRITICAL') return 'due-date-critical';
        if (level === 'HIGH') return 'due-date-high';
        if (level === 'MEDIUM') return 'due-date-medium';
        return 'due-date-low';
    }

    /**
     * Show job details modal
     */
    async showJobDetailsModal(jobId) {
        try {
            // Show loading
            this.showLoadingModal();

            // Fetch job details
            const response = await fetch(`${this.backendUrl}${this.apiEndpoint}/jobs/${jobId}`);

            if (!response.ok) {
                throw new Error('Failed to fetch job details');
            }

            const data = await response.json();
            const job = data.job;

            // Create modal with proper Synergy structure
            const modalHtml = `
                <div class="modal-overlay" id="job-details-modal">
                    <div class="kanban-job-modal" id="draggable-modal">
                        <!-- HEADER -->
                        <div class="kanban-modal-header" id="modal-header-drag">
                            <div class="kanban-modal-title">
                                <i class="fas fa-clipboard-list"></i>
                                <span>Job Details - Ticket #${job.TicketID}</span>
                            </div>
                            <button class="kanban-modal-close-btn" onclick="document.getElementById('job-details-modal').remove();">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        
                        <!-- BODY CONTENT -->
                        <div class="kanban-modal-body" id="modal-body-scroll">
                            <!-- JOB STATUS SECTION -->
                            <div class="kanban-content-section">
                                <div class="kanban-section-title">
                                    <i class="fas fa-badges"></i>
                                    <span>Job Status</span>
                                </div>
                                <div class="kanban-section-content">
                                    <div class="status-badges">
                                        <span class="badge badge-priority" style="background-color: ${job.PriorityColorHex};">
                                            ${job.PriorityLabel} Priority (Score: ${job.AIPriorityScore})
                                        </span>
                                        <span class="badge badge-tier" style="background-color: ${job.CustomerTierColorHex};">
                                            ${job.CustomerTier} Customer
                                        </span>
                                        <span class="badge badge-wip" style="background-color: ${job.WIPColorHex};">
                                            ${job.WIPStatus}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <!-- CLIENT INFORMATION SECTION -->
                            <div class="kanban-content-section">
                                <div class="kanban-section-title">
                                    <i class="fas fa-building"></i>
                                    <span>Client Information</span>
                                </div>
                                <div class="kanban-section-content">
                                    <div class="kanban-detail-grid">
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Client Name</span>
                                            <span class="kanban-detail-value">${this.escapeHtml(job.ClientName)}</span>
                                        </div>
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Order ID</span>
                                            <span class="kanban-detail-value">${job.OrderID}</span>
                                        </div>
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Order Date</span>
                                            <span class="kanban-detail-value">${this.formatDate(job.OrderDate)}</span>
                                        </div>
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Business Division</span>
                                            <span class="kanban-detail-value">${job.BusinessDivision || 'InHousePrint'}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- JOB SPECIFICATIONS SECTION -->
                            <div class="kanban-content-section">
                                <div class="kanban-section-title">
                                    <i class="fas fa-file-alt"></i>
                                    <span>Job Specifications</span>
                                </div>
                                <div class="kanban-section-content">
                                    <div class="kanban-detail-grid">
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Description</span>
                                            <span class="kanban-detail-value">${this.escapeHtml(job.ShortJobDesc || 'N/A')}</span>
                                        </div>
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Quantity</span>
                                            <span class="kanban-detail-value">${job.QTY || 0}</span>
                                        </div>
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Cost</span>
                                            <span class="kanban-detail-value">$${this.formatCurrency(job.Cost || 0)}</span>
                                        </div>
                                        ${job.Paper ? `
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Paper</span>
                                            <span class="kanban-detail-value">${job.Paper}</span>
                                        </div>` : ''}
                                        ${job.GSM ? `
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">GSM</span>
                                            <span class="kanban-detail-value">${job.GSM}</span>
                                        </div>` : ''}
                                        ${job.JobSize ? `
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Size</span>
                                            <span class="kanban-detail-value">${job.JobSize}</span>
                                        </div>` : ''}
                                        ${job.Pages ? `
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Pages</span>
                                            <span class="kanban-detail-value">${job.Pages}</span>
                                        </div>` : ''}
                                        ${job.Binding ? `
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Binding</span>
                                            <span class="kanban-detail-value">${job.Binding}</span>
                                        </div>` : ''}
                                    </div>
                                </div>
                            </div>
                            
                            ${job.Cello || job.Folding || job.Stitching ? `
                            <!-- FINISHING OPTIONS SECTION -->
                            <div class="kanban-content-section">
                                <div class="kanban-section-title">
                                    <i class="fas fa-magic"></i>
                                    <span>Finishing Options</span>
                                </div>
                                <div class="kanban-section-content">
                                    <div class="kanban-detail-grid">
                                        ${job.Cello ? `
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Cello</span>
                                            <span class="kanban-detail-value">${job.Cello}</span>
                                        </div>` : ''}
                                        ${job.Folding ? `
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Folding</span>
                                            <span class="kanban-detail-value">${job.Folding}</span>
                                        </div>` : ''}
                                        ${job.Stitching ? `
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Stitching</span>
                                            <span class="kanban-detail-value">${job.Stitching}</span>
                                        </div>` : ''}
                                    </div>
                                </div>
                            </div>` : ''}
                            
                            ${job.TicketNotes ? `
                            <!-- PRODUCTION NOTES SECTION -->
                            <div class="kanban-content-section">
                                <div class="kanban-section-title">
                                    <i class="fas fa-sticky-note"></i>
                                    <span>Production Notes</span>
                                </div>
                                <div class="kanban-section-content">
                                    <div class="kanban-notes-text">${this.escapeHtml(job.TicketNotes)}</div>
                                </div>
                            </div>` : ''}
                            
                            <!-- STATUS INFORMATION SECTION -->
                            <div class="kanban-content-section">
                                <div class="kanban-section-title">
                                    <i class="fas fa-info-circle"></i>
                                    <span>Status Information</span>
                                </div>
                                <div class="kanban-section-content">
                                    <div class="kanban-detail-grid">
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Current Stage</span>
                                            <span class="kanban-detail-value">${job.StageDescription}</span>
                                        </div>
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Due Date</span>
                                            <span class="kanban-detail-value ${this.getDueDateClass(job.UrgencyLevel)}">${this.formatDate(job.DateRequired)}</span>
                                        </div>
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Days in System</span>
                                            <span class="kanban-detail-value">${job.DaysInSystem || 0} days</span>
                                        </div>
                                        <div class="kanban-detail-item">
                                            <span class="kanban-detail-label">Urgency Level</span>
                                            <span class="kanban-detail-value">${job.UrgencyLevel}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            ${job.Shipping ? `
                            <!-- SHIPPING SECTION -->
                            <div class="kanban-content-section">
                                <div class="kanban-section-title">
                                    <i class="fas fa-shipping-fast"></i>
                                    <span>Shipping</span>
                                </div>
                                <div class="kanban-section-content">
                                    <div class="kanban-notes-text">${this.escapeHtml(job.Shipping)}</div>
                                </div>
                            </div>` : ''}
                            
                            <!-- PRODUCTION LOG SECTION -->
                            <div class="kanban-content-section" id="production-log-section-${job.TicketID}">
                                <div class="kanban-section-title">
                                    <i class="fas fa-history"></i>
                                    <span>Production Log</span>
                                    <button class="btn btn-sm btn-primary" style="margin-left: auto; padding: 4px 12px;" onclick="window.ModuleRegistry['inhouse-kanban'].showClientNotificationDialog(${job.TicketID})">
                                        <i class="fas fa-envelope"></i> Notify Client
                                    </button>
                                </div>
                                <div class="kanban-section-content" style="padding: 0;">
                                    <div id="production-log-entries-${job.TicketID}" style="max-height: 300px; overflow-y: auto; padding: 12px;">
                                        <div style="text-align: center; padding: 20px; color: #9ca3af;">
                                            <i class="fas fa-spinner fa-spin"></i> Loading production log...
                                        </div>
                                    </div>
                                    
                                    <!-- Add Entry Form -->
                                    <div style="border-top: 1px solid #30363d; padding: 12px; background: #0d1117;">
                                        <div style="display: flex; gap: 8px; margin-bottom: 8px;">
                                            <input type="text" id="log-initials-${job.TicketID}" placeholder="Initials" maxlength="3" style="width: 70px; padding: 6px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 13px;" />
                                            <select id="log-type-${job.TicketID}" style="flex: 1; padding: 6px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 13px;">
                                                <option value="note">Note</option>
                                                <option value="wastage">Wastage</option>
                                                <option value="delay">Delay</option>
                                                <option value="stock_change">Stock Change</option>
                                            </select>
                                        </div>
                                        <textarea id="log-note-${job.TicketID}" placeholder="Enter note, wastage details, or delay reason..." rows="2" style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; font-size: 13px; margin-bottom: 8px; resize: vertical;"></textarea>
                                        <button class="btn btn-primary btn-sm" onclick="window.ModuleRegistry['inhouse-kanban'].addProductionLogEntry(${job.TicketID})" style="width: 100%;">
                                            <i class="fas fa-plus"></i> Add Log Entry
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- FOOTER -->
                        <div class="kanban-modal-footer">
                            <button class="btn btn-secondary" onclick="document.getElementById('job-details-modal').remove();">
                                <i class="fas fa-times"></i> Close
                            </button>
                        </div>
                    </div>
                </div>
            `;

            // Remove loading modal
            const loadingModal = document.getElementById('loading-modal');
            if (loadingModal) loadingModal.remove();

            // Add modal to DOM
            document.body.insertAdjacentHTML('beforeend', modalHtml);

            // Set initial position (centered on screen, with cascade for multiple modals)
            const modal = document.getElementById('draggable-modal');
            if (modal) {
                // Count existing modals to cascade position
                const existingModals = document.querySelectorAll('.draggable-modal');
                const offset = (existingModals.length - 1) * 30;

                // Center on screen with cascade offset
                const modalWidth = 500;
                const modalHeight = 700;
                const screenWidth = window.innerWidth;
                const screenHeight = window.innerHeight;

                const left = Math.max(0, (screenWidth - modalWidth) / 2 + offset);
                const top = Math.max(0, (screenHeight - modalHeight) / 2 + offset);

                modal.style.left = `${left}px`;
                modal.style.top = `${top}px`;
            }

            // Initialize drag and resize functionality
            this.initializeModalDragResize();

            // Load production log entries
            this.loadProductionLogEntries(jobId);

        } catch (error) {
            console.error('Failed to show job details:', error);
            const loadingModal = document.getElementById('loading-modal');
            if (loadingModal) loadingModal.remove();
            this.showNotification('error', 'Failed to load job details');
        }
    }

    /**
     * Initialize modal drag and resize functionality
     */
    initializeModalDragResize() {
        const modal = document.getElementById('draggable-modal');
        const header = document.getElementById('modal-header-drag');

        if (!modal || !header) return;

        // Dragging
        let isDragging = false;
        let dragStartX, dragStartY, modalStartX, modalStartY;

        header.addEventListener('mousedown', (e) => {
            if (e.target.tagName === 'BUTTON' || e.target.closest('button')) return;

            isDragging = true;
            dragStartX = e.clientX;
            dragStartY = e.clientY;

            const rect = modal.getBoundingClientRect();
            modalStartX = rect.left;
            modalStartY = rect.top;

            modal.style.transition = 'none';
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            const deltaX = e.clientX - dragStartX;
            const deltaY = e.clientY - dragStartY;

            modal.style.left = (modalStartX + deltaX) + 'px';
            modal.style.top = (modalStartY + deltaY) + 'px';
            modal.style.transform = 'none';
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                modal.style.transition = '';
            }
        });

        // Resizing
        const resizeHandles = modal.querySelectorAll('.resize-handle');
        resizeHandles.forEach(handle => {
            handle.addEventListener('mousedown', (e) => {
                e.stopPropagation();
                e.preventDefault();

                const startX = e.clientX;
                const startY = e.clientY;
                const startWidth = modal.offsetWidth;
                const startHeight = modal.offsetHeight;
                const startLeft = modal.offsetLeft;
                const startTop = modal.offsetTop;

                const handleClass = handle.className;

                const onMouseMove = (e) => {
                    const deltaX = e.clientX - startX;
                    const deltaY = e.clientY - startY;

                    if (handleClass.includes('resize-handle-e')) {
                        modal.style.width = Math.max(400, startWidth + deltaX) + 'px';
                    }
                    if (handleClass.includes('resize-handle-w')) {
                        const newWidth = Math.max(400, startWidth - deltaX);
                        modal.style.width = newWidth + 'px';
                        modal.style.left = startLeft + (startWidth - newWidth) + 'px';
                    }
                    if (handleClass.includes('resize-handle-s')) {
                        modal.style.height = Math.max(300, startHeight + deltaY) + 'px';
                    }
                    if (handleClass.includes('resize-handle-n')) {
                        const newHeight = Math.max(300, startHeight - deltaY);
                        modal.style.height = newHeight + 'px';
                        modal.style.top = startTop + (startHeight - newHeight) + 'px';
                    }
                };

                const onMouseUp = () => {
                    document.removeEventListener('mousemove', onMouseMove);
                    document.removeEventListener('mouseup', onMouseUp);
                };

                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
            });
        });
    }

    /**
     * Show loading modal
     */
    showLoadingModal() {
        const modalHtml = `
            <div class="modal-overlay" id="loading-modal">
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin fa-3x"></i>
                    <p>Loading job details...</p>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    /**
     * Initialize Analytics tab
     */
    initializeAnalytics() {
        const container = this.getSubTabContainer('analytics');
        const primaryColor = this.manifest?.colors?.primary || '#00509E';

        container.innerHTML = `
            <div class="module-header" style="border-bottom-color: ${primaryColor};">
                <div class="module-header-left">
                    <h2 class="module-title">
                        <i class="fas fa-chart-line" style="color: ${primaryColor};"></i>
                        Workflow Analytics
                    </h2>
                    <p class="module-description">Performance metrics and bottleneck detection</p>
                </div>
            </div>
            
            <div class="analytics-container">
                <div class="dashboard-card">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="fas fa-chart-bar" style="color: ${primaryColor};"></i>
                            Coming Soon
                        </h3>
                    </div>
                    <div class="card-content">
                        <p class="text-secondary">Advanced analytics features will be available in the next version:</p>
                        <ul class="feature-list">
                            <li><i class="fas fa-check"></i> Stage efficiency analysis</li>
                            <li><i class="fas fa-check"></i> Bottleneck detection</li>
                            <li><i class="fas fa-check"></i> Customer performance trends</li>
                            <li><i class="fas fa-check"></i> Priority distribution charts</li>
                            <li><i class="fas fa-check"></i> WIP aging reports</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('inhouse-refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Timeframe selector
        const timeframeSelector = document.getElementById('timeframe-selector');
        if (timeframeSelector) {
            timeframeSelector.addEventListener('change', (e) => {
                this.filters.timeframe_months = parseInt(e.target.value);
                this.refreshData();
            });
        }

        // Priority filter
        const prioritySelector = document.getElementById('priority-selector');
        if (prioritySelector) {
            prioritySelector.addEventListener('change', (e) => {
                this.filters.priority_filter = e.target.value;
                this.refreshData();
            });
        }

        // Search input
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.filters.search_text = e.target.value.trim();
                    this.refreshData();
                }, 500);
            });
        }
    }

    /**
     * Start auto-refresh timer
     */
    startAutoRefresh() {
        // Clear existing timer
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }

        // Set up new timer (5 minutes)
        const refreshInterval = (this.manifest?.settings?.refresh_interval || 300) * 1000;
        this.refreshTimer = setInterval(() => {
            console.log('Auto-refreshing InHouse Print data...');
            this.refreshData();
        }, refreshInterval);
    }

    /**
     * Update last refresh time display
     */
    updateLastRefreshTime() {
        const timeElement = document.querySelector('#last-refresh-time .time-value');
        if (timeElement && this.lastRefresh) {
            timeElement.textContent = this.lastRefresh.toLocaleTimeString();
        }
    }

    /**
     * Format currency
     */
    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value || 0);
    }

    /**
     * Format date
     */
    formatDate(dateStr) {
        if (!dateStr) return 'N/A';
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-AU', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
        } catch {
            return 'Invalid Date';
        }
    }

    /**
     * Escape HTML
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Show notification
     */
    showNotification(type, message) {
        console.log(`[${type.toUpperCase()}] ${message}`);

        // You can integrate with a toast notification system here
        if (type === 'error') {
            alert(`Error: ${message}`);
        }
    }

    /**
     * Cleanup
     */
    cleanup() {
        // Clear auto-refresh timer
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }

        // Clear cache
        this.dataCache.clear();

        // CRITICAL: Remove injected CSS styles to prevent leaking to other modules
        const injectedStyle = document.getElementById('inhouse-kanban-critical-styles');
        if (injectedStyle) {
            injectedStyle.remove();
            console.log('✅ Removed injected CSS styles');
        }

        // Call parent cleanup
        super.cleanup();
    }

    // ========================================================================
    // PRODUCTION LOG METHODS
    // ========================================================================

    /**
     * Load production log entries for a job
     */
    async loadProductionLogEntries(ticketId) {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/production-log/${ticketId}`);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Failed to load production log');
            }

            this.renderProductionLogEntries(ticketId, data.entries || []);

        } catch (error) {
            console.error('Failed to load production log:', error);
            const container = document.getElementById(`production-log-entries-${ticketId}`);
            if (container) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: #ef4444;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p style="margin: 8px 0 0 0;">Failed to load production log</p>
                    </div>
                `;
            }
        }
    }

    /**
     * Render production log entries
     */
    renderProductionLogEntries(ticketId, entries) {
        const container = document.getElementById(`production-log-entries-${ticketId}`);
        if (!container) return;

        if (entries.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #9ca3af;">
                    <i class="fas fa-clipboard-list"></i>
                    <p style="margin: 8px 0 0 0;">No production log entries yet</p>
                </div>
            `;
            return;
        }

        // Sort entries by date/time (newest first)
        entries.sort((a, b) => {
            const dateA = new Date(a.log_date + ' ' + a.log_time);
            const dateB = new Date(b.log_date + ' ' + b.log_time);
            return dateB - dateA;
        });

        container.innerHTML = entries.map(entry => {
            const entryTypeIcons = {
                stage_change: 'fa-exchange-alt',
                note: 'fa-sticky-note',
                wastage: 'fa-trash-alt',
                delay: 'fa-clock',
                stock_change: 'fa-boxes',
                client_notification: 'fa-envelope'
            };

            const entryTypeColors = {
                stage_change: '#3b82f6',
                note: '#fbbf24',
                wastage: '#ef4444',
                delay: '#f97316',
                stock_change: '#8b5cf6',
                client_notification: '#10b981'
            };

            const icon = entryTypeIcons[entry.entry_type] || 'fa-info-circle';
            const color = entryTypeColors[entry.entry_type] || '#6b7280';
            const canDelete = entry.entry_type !== 'stage_change' || this.canUndoStageChange(entry);

            return `
                <div style="display: flex; gap: 12px; padding: 12px; border-bottom: 1px solid #30363d; align-items: start;">
                    <div style="flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%; background: ${color}20; display: flex; align-items: center; justify-content: center; color: ${color};">
                        <i class="fas ${icon}" style="font-size: 14px;"></i>
                    </div>
                    <div style="flex: 1; min-width: 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-size: 11px; color: #9ca3af;">${this.formatLogDate(entry.log_date)}</span>
                                <span style="font-size: 11px; color: #9ca3af;">${entry.log_time}</span>
                                <span style="font-size: 11px; font-weight: 600; color: ${color}; background: ${color}20; padding: 2px 6px; border-radius: 3px;">${entry.user_initials || 'AUTO'}</span>
                                <span style="font-size: 11px; color: #9ca3af; text-transform: uppercase;">${entry.entry_type.replace('_', ' ')}</span>
                            </div>
                            ${canDelete ? `
                            <button onclick="window.ModuleRegistry['inhouse-kanban'].deleteProductionLogEntry(${entry.log_id}, ${ticketId}); event.stopPropagation();" 
                                    style="background: none; border: none; color: #ef4444; cursor: pointer; padding: 4px 8px; font-size: 12px;"
                                    title="Delete entry">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                            ` : ''}
                        </div>
                        <div style="font-size: 13px; color: #f3f4f6; line-height: 1.5;">
                            ${this.formatLogContent(entry)}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Format log content based on entry type
     */
    formatLogContent(entry) {
        switch (entry.entry_type) {
            case 'stage_change':
                return `Moved from <strong>${entry.from_stage_name || 'Unknown'}</strong> to <strong>${entry.to_stage_name || 'Unknown'}</strong>`;
            case 'wastage':
                return `${entry.note_text || ''}<br><small style="color: #9ca3af;">Amount: ${entry.wastage_amount || 0} ${entry.wastage_unit || 'units'} - ${entry.wastage_reason || ''}</small>`;
            case 'delay':
                return `${entry.note_text || ''}<br><small style="color: #9ca3af;">Duration: ${entry.delay_hours || 0}h - Reason: ${entry.delay_reason || 'N/A'}</small>`;
            case 'client_notification':
                return `${entry.note_text || ''}<br><small style="color: #9ca3af;">${entry.notification_type || 'email'} to ${entry.notification_recipient || 'N/A'} - ${entry.notification_status || 'pending'}</small>`;
            case 'stock_change':
                return `${entry.note_text || ''}<br><small style="color: #9ca3af;">Item: ${entry.stock_item || 'N/A'} - Change: ${entry.stock_quantity_change || 0}</small>`;
            default:
                return entry.note_text || '';
        }
    }

    /**
     * Format log date
     */
    formatLogDate(dateStr) {
        try {
            const date = new Date(dateStr);
            const today = new Date();
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);

            if (date.toDateString() === today.toDateString()) {
                return 'Today';
            } else if (date.toDateString() === yesterday.toDateString()) {
                return 'Yesterday';
            } else {
                return date.toLocaleDateString('en-AU', { day: '2-digit', month: '2-digit' });
            }
        } catch {
            return dateStr;
        }
    }

    /**
     * Check if stage change can be undone (within 5 minutes and moved back to same stage)
     */
    canUndoStageChange(entry) {
        // For now, allow deletion of stage changes if they're recent (within 5 minutes)
        if (entry.entry_type !== 'stage_change') return false;

        const logTime = new Date(entry.log_date + ' ' + entry.log_time);
        const now = new Date();
        const diffMinutes = (now - logTime) / (1000 * 60);

        return diffMinutes <= 5;
    }

    /**
     * Add production log entry
     */
    async addProductionLogEntry(ticketId) {
        const initials = document.getElementById(`log-initials-${ticketId}`)?.value.trim();
        const type = document.getElementById(`log-type-${ticketId}`)?.value;
        const note = document.getElementById(`log-note-${ticketId}`)?.value.trim();

        if (!initials) {
            alert('Please enter your initials');
            return;
        }

        if (!note) {
            alert('Please enter a note');
            return;
        }

        try {
            const payload = {
                user_initials: initials.toUpperCase(),
                entry_type: type,
                note_text: note
            };

            // Add type-specific fields based on entry type
            if (type === 'wastage') {
                const wastageAmount = prompt('Wastage amount:');
                const wastageUnit = prompt('Unit (sheets/meters/etc):') || 'sheets';
                if (wastageAmount) {
                    payload.wastage_amount = parseFloat(wastageAmount);
                    payload.wastage_unit = wastageUnit;
                    payload.wastage_reason = note;
                }
            } else if (type === 'delay') {
                const delayHours = prompt('Delay duration (hours):');
                if (delayHours) {
                    payload.delay_hours = parseFloat(delayHours);
                    payload.delay_reason = note;
                }
            }

            const response = await fetch(`${this.API_BASE_URL}/api/production-log/${ticketId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Failed to add log entry');
            }

            // Clear form
            document.getElementById(`log-initials-${ticketId}`).value = '';
            document.getElementById(`log-note-${ticketId}`).value = '';

            // Reload entries
            this.loadProductionLogEntries(ticketId);

            this.showNotification('success', 'Log entry added successfully');

        } catch (error) {
            console.error('Failed to add log entry:', error);
            alert('Failed to add log entry: ' + error.message);
        }
    }

    /**
     * Delete production log entry
     */
    async deleteProductionLogEntry(logId, ticketId) {
        if (!confirm('Are you sure you want to delete this log entry?')) {
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/production-log/entry/${logId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Failed to delete log entry');
            }

            // Reload entries
            this.loadProductionLogEntries(ticketId);

            this.showNotification('success', 'Log entry deleted');

        } catch (error) {
            console.error('Failed to delete log entry:', error);
            alert('Failed to delete log entry: ' + error.message);
        }
    }

    // ========================================================================
    // DRAG AND DROP HANDLERS
    // ========================================================================

    /**
     * Handle drag start
     */
    handleDragStart(event, jobId, stageId) {
        event.stopPropagation();
        this.draggedJob = { jobId, stageId };
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData('text/html', event.target.innerHTML);
        event.target.style.opacity = '0.5';
    }

    /**
     * Handle drop
     */
    async handleDrop(event, toStageId, toStageName) {
        event.preventDefault();
        event.stopPropagation();

        if (!this.draggedJob) return;

        const { jobId, stageId: fromStageId } = this.draggedJob;

        // Don't log if dropped in same column
        if (fromStageId === toStageId) {
            this.draggedJob = null;
            return;
        }

        // Prompt for user initials
        const initials = prompt('Enter your initials for this stage change:');
        if (!initials) {
            this.draggedJob = null;
            return;
        }

        try {
            // Find stage names
            const fromStage = this.stages.find(s => s.StageID === fromStageId);
            const toStage = this.stages.find(s => s.StageID === toStageId);

            // Log stage change
            const response = await fetch(`${this.API_BASE_URL}/api/production-log/${jobId}/stage-change`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_initials: initials.toUpperCase(),
                    from_stage_id: fromStageId,
                    from_stage_name: fromStage?.StageDescription || 'Unknown',
                    to_stage_id: toStageId,
                    to_stage_name: toStage?.StageDescription || toStageName
                })
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Failed to log stage change');
            }

            this.showNotification('success', `Job moved to ${toStageName} and logged`);

            // Refresh board to show new position
            setTimeout(() => this.refreshData(), 500);

        } catch (error) {
            console.error('Failed to log stage change:', error);
            alert('Stage change logged, but there was an error: ' + error.message);
        }

        this.draggedJob = null;
    }

    // ========================================================================
    // CLIENT NOTIFICATION DIALOG
    // ========================================================================

    /**
     * Show client notification dialog
     */
    showClientNotificationDialog(ticketId) {
        // Find job to get client info
        const job = this.jobs.find(j => j.TicketID === ticketId);
        const clientName = job ? job.ClientName : 'Client';

        const dialogHtml = `
            <div class="modal-overlay" id="notification-dialog" style="z-index: 10000;">
                <div class="kanban-job-modal" style="width: 600px; max-width: 90%;">
                    <div class="kanban-modal-header">
                        <div class="kanban-modal-title">
                            <i class="fas fa-envelope"></i>
                            <span>Send Client Notification - Ticket #${ticketId}</span>
                        </div>
                        <button class="kanban-modal-close-btn" onclick="document.getElementById('notification-dialog').remove();">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <div class="kanban-modal-body" style="padding: 20px;">
                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-user"></i> Client Name
                            </label>
                            <input type="text" id="notif-client-name" value="${this.escapeHtml(clientName)}" 
                                   style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6;" readonly />
                        </div>

                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-bell"></i> Notification Type
                            </label>
                            <select id="notif-type" style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6;">
                                <option value="email">Email</option>
                                <option value="sms">SMS</option>
                                <option value="phone">Phone Call</option>
                                <option value="whatsapp">WhatsApp</option>
                                <option value="client_portal">Client Portal</option>
                            </select>
                        </div>

                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-envelope"></i> Email Address
                            </label>
                            <input type="email" id="notif-email" placeholder="client@example.com" 
                                   style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6;" />
                        </div>

                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-phone"></i> Phone Number
                            </label>
                            <input type="tel" id="notif-phone" placeholder="+61 4XX XXX XXX" 
                                   style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6;" />
                        </div>

                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-heading"></i> Subject
                            </label>
                            <input type="text" id="notif-subject" placeholder="Your print job update" 
                                   style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6;" />
                        </div>

                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-comment-alt"></i> Message
                            </label>
                            <textarea id="notif-message" rows="4" placeholder="Enter your message to the client..." 
                                      style="width: 100%; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6; resize: vertical;"></textarea>
                        </div>

                        <div style="margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #f3f4f6; margin-bottom: 6px;">
                                <i class="fas fa-user"></i> Your Initials
                            </label>
                            <input type="text" id="notif-initials" placeholder="JD" maxlength="3" 
                                   style="width: 100px; padding: 8px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; color: #f3f4f6;" />
                        </div>

                        <div style="padding: 12px; background: #1c2128; border: 1px solid #30363d; border-radius: 6px; margin-bottom: 16px;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                                <input type="checkbox" id="notif-auto-send" style="width: 18px; height: 18px;" />
                                <label for="notif-auto-send" style="font-size: 13px; font-weight: 600; color: #f3f4f6; cursor: pointer;">
                                    <i class="fas fa-paper-plane"></i> Auto-send notification
                                </label>
                            </div>
                            <p style="margin: 0; font-size: 12px; color: #9ca3af; padding-left: 26px;">
                                If unchecked, notification will be logged only (not sent automatically)
                            </p>
                        </div>
                    </div>

                    <div class="kanban-modal-footer" style="display: flex; gap: 8px; justify-content: flex-end;">
                        <button class="btn btn-secondary" onclick="document.getElementById('notification-dialog').remove();">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                        <button class="btn btn-primary" onclick="window.ModuleRegistry['inhouse-kanban'].sendClientNotification(${ticketId});">
                            <i class="fas fa-check"></i> Send & Log
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', dialogHtml);
    }

    /**
     * Send client notification
     */
    async sendClientNotification(ticketId) {
        const type = document.getElementById('notif-type')?.value;
        const email = document.getElementById('notif-email')?.value.trim();
        const phone = document.getElementById('notif-phone')?.value.trim();
        const subject = document.getElementById('notif-subject')?.value.trim();
        const message = document.getElementById('notif-message')?.value.trim();
        const initials = document.getElementById('notif-initials')?.value.trim();
        const autoSend = document.getElementById('notif-auto-send')?.checked;

        if (!initials) {
            alert('Please enter your initials');
            return;
        }

        if (!message) {
            alert('Please enter a message');
            return;
        }

        const recipient = type === 'email' ? email : phone;
        if (!recipient) {
            alert(`Please enter a ${type === 'email' ? 'email address' : 'phone number'}`);
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE_URL}/api/production-log/${ticketId}/notification`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_initials: initials.toUpperCase(),
                    notification_type: type,
                    notification_recipient: recipient,
                    notification_subject: subject || 'Print Job Update',
                    notification_message: message,
                    notification_status: autoSend ? 'sent' : 'pending',
                    auto_send: autoSend
                })
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Failed to log notification');
            }

            // Close dialog
            document.getElementById('notification-dialog')?.remove();

            // Reload production log if modal is open
            this.loadProductionLogEntries(ticketId);

            const action = autoSend ? 'sent and logged' : 'logged (not sent)';
            this.showNotification('success', `Client notification ${action}`);

        } catch (error) {
            console.error('Failed to send notification:', error);
            alert('Failed to send notification: ' + error.message);
        }
    }

    /**
     * Load muted cards from localStorage
     */
    loadMutedCards() {
        try {
            const stored = localStorage.getItem('kanban-muted-cards');
            if (stored) {
                const data = JSON.parse(stored);
                this.mutedCards = new Map(Object.entries(data));
                console.log(`Loaded ${this.mutedCards.size} muted cards from storage`);
            }
        } catch (error) {
            console.error('Failed to load muted cards:', error);
            this.mutedCards = new Map();
        }
    }

    /**
     * Save muted cards to localStorage
     */
    saveMutedCards() {
        try {
            const data = Object.fromEntries(this.mutedCards);
            localStorage.setItem('kanban-muted-cards', JSON.stringify(data));
            console.log(`Saved ${this.mutedCards.size} muted cards to storage`);
        } catch (error) {
            console.error('Failed to save muted cards:', error);
        }
    }

    /**
     * Get mute settings for a card
     * @param {number} ticketId - Ticket ID
     * @returns {Object} Mute settings object
     */
    getMuteSettings(ticketId) {
        return this.mutedCards.get(ticketId) || {
            muteDueDate: false,
            muteBackground: false,
            mutePriority: false,
            muteBorder: false,
            shiftToEnd: false
        };
    }

    /**
     * Set mute settings for a card
     * @param {number} ticketId - Ticket ID
     * @param {Object} settings - Mute settings object
     */
    setMuteSettings(ticketId, settings) {
        this.mutedCards.set(ticketId, settings);
        this.saveMutedCards();

        // Re-render to apply changes
        this.renderKanbanBoard();

        // Update count in expander
        this.updateMutedCardCount();
    }

    /**
     * Clear mute settings for a card
     * @param {number} ticketId - Ticket ID
     */
    clearMuteSettings(ticketId) {
        this.mutedCards.delete(ticketId);
        this.saveMutedCards();
        this.renderKanbanBoard();
        this.updateMutedCardCount();
    }

    /**
     * Clear all muted cards
     */
    clearAllMutedCards() {
        if (confirm(`Clear mute settings for ${this.mutedCards.size} cards?`)) {
            this.mutedCards.clear();
            this.saveMutedCards();
            this.renderKanbanBoard();
            this.updateMutedCardCount();
            this.showNotification('success', 'All card mutes cleared');
        }
    }

    /**
     * Update the muted card count display
     */
    updateMutedCardCount() {
        const countElement = document.querySelector('.muted-cards-count');
        if (countElement) {
            const count = this.mutedCards.size;
            countElement.textContent = count > 0 ? `(${count} muted)` : '';
            countElement.style.display = count > 0 ? 'inline' : 'none';
        }
    }

    /**
     * Check if a card should be muted
     * @param {number} ticketId - Ticket ID
     * @returns {boolean} True if card has any mute settings
     */
    isCardMuted(ticketId) {
        const settings = this.getMuteSettings(ticketId);
        return Object.values(settings).some(val => val === true);
    }

    /**
     * Show only muted cards by filtering
     */
    showMutedCardsOnly() {
        const mutedIds = Array.from(this.mutedCards.keys());
        if (mutedIds.length === 0) {
            alert('No muted cards found');
            return;
        }

        // Apply filter to show only muted cards
        const searchInput = document.getElementById('kanban-search-input');
        if (searchInput) {
            // Show message
            this.showNotification('info', `Filtering ${mutedIds.length} muted cards`);

            // Highlight muted cards by adding a temporary class
            document.querySelectorAll('.kanban-card').forEach(card => {
                const ticketId = parseInt(card.dataset.ticketId);
                if (this.isCardMuted(ticketId)) {
                    card.style.boxShadow = '0 0 10px 2px rgba(88, 166, 255, 0.5)';
                } else {
                    card.style.opacity = '0.3';
                }
            });

            // Remove highlights after 3 seconds
            setTimeout(() => {
                document.querySelectorAll('.kanban-card').forEach(card => {
                    card.style.boxShadow = '';
                    card.style.opacity = '';
                });
            }, 3000);
        }
    }

    /**
     * Export list of muted cards
     */
    exportMutedCards() {
        if (this.mutedCards.size === 0) {
            alert('No muted cards to export');
            return;
        }

        const mutedList = [];
        this.mutedCards.forEach((settings, ticketId) => {
            const job = this.jobsCache.get(ticketId);
            if (job) {
                mutedList.push({
                    ticketId: ticketId,
                    ticketNumber: job.TicketNumber,
                    clientName: job.ClientName,
                    description: job.Description,
                    muteSettings: settings
                });
            }
        });

        // Create CSV
        const headers = ['Ticket ID', 'Ticket Number', 'Client', 'Description', 'Mute Due Date', 'Mute Background', 'Mute Priority', 'Mute Border', 'Shift to End'];
        const rows = mutedList.map(item => [
            item.ticketId,
            item.ticketNumber,
            item.clientName,
            item.description,
            item.muteSettings.muteDueDate ? 'Yes' : 'No',
            item.muteSettings.muteBackground ? 'Yes' : 'No',
            item.muteSettings.mutePriority ? 'Yes' : 'No',
            item.muteSettings.muteBorder ? 'Yes' : 'No',
            item.muteSettings.shiftToEnd ? 'Yes' : 'No'
        ]);

        const csv = [headers.join(','), ...rows.map(r => r.map(cell => `"${cell}"`).join(','))].join('\n');

        // Download
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `muted-cards-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification('success', `Exported ${mutedList.length} muted cards`);
    }

    // ============================================================================
    // COLOR SETTINGS FUNCTIONS
    // ============================================================================

    /**
     * Initialize color settings from localStorage or defaults
     */
    loadColorSettings() {
        try {
            const stored = localStorage.getItem('kanban-color-settings');
            if (stored) {
                this.colorSettings = JSON.parse(stored);
                console.log('Loaded color settings from storage');
                this.applyColorSettingsToUI();
            } else {
                this.colorSettings = this.getDefaultColorSettings();
            }
        } catch (error) {
            console.error('Failed to load color settings:', error);
            this.colorSettings = this.getDefaultColorSettings();
        }
    }

    /**
     * Get default color settings
     */
    getDefaultColorSettings() {
        return {
            overdue: '#dc2626',
            dueToday: '#fbbf24',
            dueSoon: '#3b82f6',
            priorityHigh: '#dc2626',
            priorityMedium: '#fbbf24',
            priorityLow: '#10b981',
            stageDesign: '#8b5cf6',
            stageProduction: '#3b82f6',
            stageComplete: '#10b981'
        };
    }

    /**
     * Apply loaded color settings to UI inputs
     */
    applyColorSettingsToUI() {
        if (!this.colorSettings) return;

        Object.entries(this.colorSettings).forEach(([key, value]) => {
            const input = document.getElementById(`color-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`);
            const display = document.getElementById(`color-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}-value`);

            if (input) input.value = value;
            if (display) display.textContent = value;
        });
    }

    /**
     * Update a single color setting
     */
    updateColorSetting(key, value) {
        this.colorSettings = this.colorSettings || this.getDefaultColorSettings();
        this.colorSettings[key] = value;

        // Update hex display
        const display = document.getElementById(`color-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}-value`);
        if (display) display.textContent = value;

        console.log(`Updated ${key} to ${value}`);
    }

    /**
     * Apply a color scheme preset
     */
    applyColorScheme(scheme) {
        const schemes = {
            default: {
                overdue: '#dc2626',
                dueToday: '#fbbf24',
                dueSoon: '#3b82f6',
                priorityHigh: '#dc2626',
                priorityMedium: '#fbbf24',
                priorityLow: '#10b981',
                stageDesign: '#8b5cf6',
                stageProduction: '#3b82f6',
                stageComplete: '#10b981'
            },
            vibrant: {
                overdue: '#ff0000',
                dueToday: '#ffaa00',
                dueSoon: '#0088ff',
                priorityHigh: '#ff0066',
                priorityMedium: '#ff9900',
                priorityLow: '#00cc66',
                stageDesign: '#9933ff',
                stageProduction: '#0099ff',
                stageComplete: '#00ff88'
            },
            pastel: {
                overdue: '#ffb3ba',
                dueToday: '#ffffba',
                dueSoon: '#bae1ff',
                priorityHigh: '#ffccdd',
                priorityMedium: '#ffeaa7',
                priorityLow: '#b4f8c8',
                stageDesign: '#d4a5f9',
                stageProduction: '#a8daff',
                stageComplete: '#c7f9cc'
            },
            monochrome: {
                overdue: '#1f2937',
                dueToday: '#4b5563',
                dueSoon: '#6b7280',
                priorityHigh: '#1f2937',
                priorityMedium: '#4b5563',
                priorityLow: '#6b7280',
                stageDesign: '#374151',
                stageProduction: '#4b5563',
                stageComplete: '#6b7280'
            }
        };

        const selectedScheme = schemes[scheme];
        if (!selectedScheme) {
            console.error('Unknown color scheme:', scheme);
            return;
        }

        this.colorSettings = selectedScheme;
        this.applyColorSettingsToUI();
        this.showNotification('info', `Applied ${scheme} color scheme`);
    }

    /**
     * Test color changes (apply without saving)
     */
    testColorSettings() {
        this.renderKanbanBoard();
        this.showNotification('info', 'Testing color changes (not saved yet)');
    }

    /**
     * Save color settings to localStorage
     */
    saveColorSettings() {
        try {
            localStorage.setItem('kanban-color-settings', JSON.stringify(this.colorSettings));
            this.renderKanbanBoard();
            this.showNotification('success', 'Color settings saved successfully');
            console.log('Saved color settings:', this.colorSettings);
        } catch (error) {
            console.error('Failed to save color settings:', error);
            this.showNotification('error', 'Failed to save color settings');
        }
    }

    /**
     * Reset color settings to default
     */
    resetColorSettings() {
        if (confirm('Reset all color settings to default?')) {
            this.colorSettings = this.getDefaultColorSettings();
            this.applyColorSettingsToUI();
            localStorage.removeItem('kanban-color-settings');
            this.renderKanbanBoard();
            this.showNotification('success', 'Color settings reset to default');
        }
    }

    /**
     * Get color for a specific context (respects custom settings)
     */
    getColor(context, defaultColor) {
        if (!this.colorSettings) {
            this.loadColorSettings();
        }
        return this.colorSettings[context] || defaultColor;
    }

    // ============================================================================
    // COLOR TOGGLE FUNCTIONS (On/Off Switches)
    // ============================================================================

    /**
     * Load color toggle settings from localStorage
     */
    loadColorToggles() {
        try {
            const stored = localStorage.getItem('kanban-color-toggles');
            if (stored) {
                this.colorToggles = JSON.parse(stored);
                console.log('Loaded color toggles:', this.colorToggles);
            }
        } catch (error) {
            console.error('Failed to load color toggles:', error);
            this.colorToggles = {
                showBorderColors: true,
                showBackgroundColors: true,
                showBannerColors: true
            };
        }
    }

    /**
     * Save color toggle settings to localStorage
     */
    saveColorToggles() {
        try {
            localStorage.setItem('kanban-color-toggles', JSON.stringify(this.colorToggles));
            console.log('Saved color toggles:', this.colorToggles);
        } catch (error) {
            console.error('Failed to save color toggles:', error);
        }
    }

    /**
     * Toggle a color setting on/off
     */
    toggleColorSetting(setting) {
        // Toggle the value
        this.colorToggles[setting] = !this.colorToggles[setting];

        // Save to localStorage
        this.saveColorToggles();

        // Update button UI
        const buttonMap = {
            'showBorderColors': 'toggle-border-colors',
            'showBackgroundColors': 'toggle-background-colors',
            'showBannerColors': 'toggle-banner-colors'
        };

        const buttonId = buttonMap[setting];
        const button = document.getElementById(buttonId);

        if (button) {
            const isActive = this.colorToggles[setting];
            const checkIcon = button.querySelector('.fa-check');

            if (isActive) {
                button.classList.add('active');
                button.style.borderColor = '#58a6ff';
                button.style.color = '#58a6ff';
                if (checkIcon) checkIcon.style.color = '#22c55e';
            } else {
                button.classList.remove('active');
                button.style.borderColor = '#6b7280';
                button.style.color = '#6b7280';
                if (checkIcon) checkIcon.style.color = 'transparent';
            }
        }

        // Re-render board to apply changes
        this.renderKanbanBoard();

        // Show notification
        const settingNames = {
            'showBorderColors': 'Border colors (Priority)',
            'showBackgroundColors': 'Background colors (Due Date)',
            'showBannerColors': 'Banner colors (Urgency)'
        };

        const state = this.colorToggles[setting] ? 'enabled' : 'disabled';
        this.showNotification('info', `${settingNames[setting]} ${state}`);
    }

    /**
     * Update color toggle button states on page load
     */
    updateColorToggleButtons() {
        const buttonMap = {
            'showBorderColors': 'toggle-border-colors',
            'showBackgroundColors': 'toggle-background-colors',
            'showBannerColors': 'toggle-banner-colors'
        };

        Object.entries(buttonMap).forEach(([setting, buttonId]) => {
            const button = document.getElementById(buttonId);
            if (button) {
                const isActive = this.colorToggles[setting];
                const checkIcon = button.querySelector('.fa-check');

                if (isActive) {
                    button.classList.add('active');
                    button.style.borderColor = '#58a6ff';
                    button.style.color = '#58a6ff';
                    if (checkIcon) checkIcon.style.color = '#22c55e';
                } else {
                    button.classList.remove('active');
                    button.style.borderColor = '#6b7280';
                    button.style.color = '#6b7280';
                    if (checkIcon) checkIcon.style.color = 'transparent';
                }
            }
        });
    }

    // ============================================================================
    // ADVANCED COLOR CUSTOMIZATION (Interactive Tables)
    // ============================================================================

    /**
     * Render all advanced color customization tables
     */
    renderAdvancedColorTables() {
        this.renderPrioritySettingsTable();
        this.renderDueDateSettingsTable();
        this.renderBannerSettingsTable();
    }

    /**
     * Render Priority Settings Table
     */
    renderPrioritySettingsTable() {
        const tbody = document.getElementById('priority-settings-table');
        if (!tbody) return;

        // MATCH COLOR GUIDE EXACTLY
        const priorities = [
            { level: 'CRITICAL (800+)', defaultColor: '#dc2626', defaultWidth: '4px', range: '800+' },
            { level: 'HIGH (600-799)', defaultColor: '#f59e0b', defaultWidth: '4px', range: '600-799' },
            { level: 'MEDIUM (400-599)', defaultColor: '#fbbf24', defaultWidth: '3px', range: '400-599' },
            { level: 'NORMAL (200-399)', defaultColor: '#22c55e', defaultWidth: '2px', range: '200-399' },
            { level: 'LOW (0-199)', defaultColor: '#3b82f6', defaultWidth: '2px', range: '0-199' }
        ];

        tbody.innerHTML = priorities.map((p, idx) => `
            <tr style="border-bottom: 1px solid #30363d;">
                <td style="padding: 12px; color: #f0f6fc; font-weight: 500;">${p.level}</td>
                <td style="padding: 12px;">
                    <input type="color" value="${p.defaultColor}" 
                           data-priority-idx="${idx}"
                           class="priority-color-input"
                           style="width: 60px; height: 30px; border: 1px solid #58a6ff; border-radius: 4px; cursor: pointer;">
                </td>
                <td style="padding: 12px;">
                    <select data-priority-idx="${idx}" class="priority-width-select" style="padding: 6px 12px; background: #0d1117; border: 1px solid #58a6ff; border-radius: 4px; color: #f0f6fc;">
                        <option value="2px" ${p.defaultWidth === '2px' ? 'selected' : ''}>2px</option>
                        <option value="3px" ${p.defaultWidth === '3px' ? 'selected' : ''}>3px</option>
                        <option value="4px" ${p.defaultWidth === '4px' ? 'selected' : ''}>4px</option>
                        <option value="8px" ${p.defaultWidth === '8px' ? 'selected' : ''}>8px</option>
                    </select>
                </td>
                <td style="padding: 12px;">
                    <div class="priority-preview-${idx}" style="width: 60px; height: 30px; border-left: ${p.defaultWidth} solid ${p.defaultColor}; background: #161b22; border-radius: 3px;"></div>
                </td>
            </tr>
        `).join('');

        // Add event listeners for live preview updates (with slight delay to ensure DOM is ready)
        setTimeout(() => {
            if (typeof this.attachPriorityPreviewListeners === 'function') {
                this.attachPriorityPreviewListeners();
            }
        }, 100);
    }

    /**
     * Render Due Date Settings Table
     */
    renderDueDateSettingsTable() {
        const tbody = document.getElementById('duedate-settings-table');
        if (!tbody) return;

        // MATCH COLOR GUIDE EXACTLY
        const dueDateRanges = [
            { label: '8+ days overdue', borderColor: '#dc2626', borderType: 'solid', width: '4px', pulse: true, bgColor: 'rgba(220, 38, 38, 0.25)', displayName: 'Solid Red' },
            { label: '4-7 days overdue', borderColor: '#ef4444', borderType: 'solid', width: '3px', pulse: true, bgColor: 'rgba(239, 68, 68, 0.20)', displayName: 'Solid Red + PULSE' },
            { label: '1-3 days overdue', borderColor: '#fb7185', borderType: 'solid', width: '2px', pulse: true, bgColor: 'rgba(251, 113, 133, 0.15)', displayName: 'Dark Red + PULSE' },
            { label: 'Due TODAY', borderColor: '#f59e0b', borderType: 'solid', width: '2px', pulse: false, bgColor: 'rgba(245, 158, 11, 0.15)', displayName: 'Vibrant Orange' },
            { label: 'Due TOMORROW', borderColor: '#fbbf24', borderType: 'solid', width: '2px', pulse: false, bgColor: 'rgba(251, 191, 36, 0.12)', displayName: 'Bright Yellow' },
            { label: 'Due in 2-3 days', borderColor: '#3b82f6', borderType: 'solid', width: '2px', pulse: false, bgColor: 'rgba(59, 130, 246, 0.08)', displayName: 'Solid Blue' },
            { label: 'Due in 4-5 days', borderColor: '#60a5fa', borderType: 'dashed', width: '2px', pulse: false, bgColor: 'rgba(96, 165, 250, 0.05)', displayName: 'Dashed Blue' },
            { label: 'Due in 6-7 days', borderColor: '#22c55e', borderType: 'dashed', width: '2px', pulse: false, bgColor: 'rgba(34, 197, 94, 0.05)', displayName: 'Dashed Green' },
            { label: '8+ days future', borderColor: '#e5e7eb', borderType: 'solid', width: '1px', pulse: false, bgColor: 'transparent', displayName: 'Thin White' }
        ];

        tbody.innerHTML = dueDateRanges.map((range, idx) => `
            <tr style="border-bottom: 1px solid #30363d;">
                <td style="padding: 12px; color: #f0f6fc; font-size: 0.9em;">${range.label}</td>
                <td style="padding: 12px;">
                    <input type="color" value="${range.borderColor}" 
                           data-range-idx="${idx}"
                           class="duedate-border-color-input"
                           style="width: 50px; height: 26px; border: 1px solid #58a6ff; border-radius: 4px; cursor: pointer;">
                </td>
                <td style="padding: 12px;">
                    <select data-range-idx="${idx}" class="duedate-border-type-select" style="padding: 4px 8px; background: #0d1117; border: 1px solid #58a6ff; border-radius: 4px; color: #f0f6fc; font-size: 0.85em;">
                        <option value="solid" ${range.borderType === 'solid' ? 'selected' : ''}>Solid</option>
                        <option value="dashed" ${range.borderType === 'dashed' ? 'selected' : ''}>Dashed</option>
                        <option value="dotted" ${range.borderType === 'dotted' ? 'selected' : ''}>Dotted</option>
                    </select>
                </td>
                <td style="padding: 12px;">
                    <select data-range-idx="${idx}" class="duedate-width-select" style="padding: 4px 8px; background: #0d1117; border: 1px solid #58a6ff; border-radius: 4px; color: #f0f6fc; font-size: 0.85em;">
                        <option value="1px" ${range.width === '1px' ? 'selected' : ''}>1px</option>
                        <option value="2px" ${range.width === '2px' ? 'selected' : ''}>2px</option>
                        <option value="3px" ${range.width === '3px' ? 'selected' : ''}>3px</option>
                        <option value="4px" ${range.width === '4px' ? 'selected' : ''}>4px</option>
                    </select>
                </td>
                <td style="padding: 12px; text-align: center;">
                    <input type="checkbox" ${range.pulse ? 'checked' : ''} data-range-idx="${idx}"
                           class="duedate-pulse-checkbox"
                           style="width: 18px; height: 18px; cursor: pointer;">
                </td>
                <td style="padding: 12px;">
                    <input type="color" value="${range.bgColor === 'transparent' ? '#000000' : this.rgbaToHex(range.bgColor)}" 
                           data-range-idx="${idx}"
                           class="duedate-bg-color-input"
                           style="width: 50px; height: 26px; border: 1px solid #58a6ff; border-radius: 4px; cursor: pointer;">
                </td>
                <td style="padding: 12px;">
                    <div class="duedate-preview-${idx}" style="width: 70px; height: 26px; border: ${range.width} ${range.borderType} ${range.borderColor}; background: ${range.bgColor}; border-radius: 3px;"></div>
                </td>
            </tr>
        `).join('');

        // Add event listeners for live preview updates (with slight delay to ensure DOM is ready)
        setTimeout(() => {
            if (typeof this.attachDueDatePreviewListeners === 'function') {
                this.attachDueDatePreviewListeners();
            }
        }, 100);
    }

    /**
     * Render Banner Settings Table
     */
    renderBannerSettingsTable() {
        const tbody = document.getElementById('banner-settings-table');
        if (!tbody) return;

        const bannerStates = [
            { state: 'OVERDUE 7+', bgColor: '#fb7185', text: 'OVERDUE 7+' },
            { state: 'OVERDUE', bgColor: '#f87171', text: 'OVERDUE' },
            { state: 'DUE TODAY', bgColor: '#fb923c', text: 'DUE TODAY' },
            { state: 'TOMORROW', bgColor: '#fbbf24', text: 'TOMORROW' },
            { state: '2-3 DAYS', bgColor: '#fde047', text: '2-3 DAYS' },
            { state: '4-7 DAYS', bgColor: '#22c55e', text: '4-7 DAYS' },
            { state: '8+ DAYS', bgColor: '#60a5fa', text: '8+ DAYS' }
        ];

        tbody.innerHTML = bannerStates.map((banner, idx) => `
            <tr style="border-bottom: 1px solid #30363d;">
                <td style="padding: 12px; color: #f0f6fc; font-weight: 500;">${banner.state}</td>
                <td style="padding: 12px;">
                    <input type="color" value="${banner.bgColor}" 
                           data-banner-idx="${idx}"
                           class="banner-bg-color-input"
                           style="width: 60px; height: 30px; border: 1px solid #58a6ff; border-radius: 4px; cursor: pointer;">
                </td>
                <td style="padding: 12px;">
                    <input type="text" value="${banner.text}" 
                           data-banner-idx="${idx}"
                           class="banner-text-input"
                           style="padding: 6px 12px; background: #0d1117; border: 1px solid #58a6ff; border-radius: 4px; color: #f0f6fc; width: 100%;">
                </td>
                <td style="padding: 12px;">
                    <div class="banner-preview-${idx}" style="padding: 4px 8px; background: ${banner.bgColor}; color: white; font-size: 11px; font-weight: 600; text-align: center; border-radius: 3px;">
                        ${banner.text}
                    </div>
                </td>
            </tr>
        `).join('');

        // Add event listeners for live preview updates (with slight delay to ensure DOM is ready)
        setTimeout(() => {
            if (typeof this.attachBannerPreviewListeners === 'function') {
                this.attachBannerPreviewListeners();
            }
        }, 100);
    }

    /**
     * Attach live preview listeners for Priority Settings
     */
    attachPriorityPreviewListeners() {
        // Color inputs
        document.querySelectorAll('.priority-color-input').forEach(input => {
            input.addEventListener('input', (e) => {
                const idx = e.target.getAttribute('data-priority-idx');
                const color = e.target.value;
                const width = document.querySelector(`.priority-width-select[data-priority-idx="${idx}"]`).value;
                const preview = document.querySelector(`.priority-preview-${idx}`);
                if (preview) {
                    preview.style.borderLeft = `${width} solid ${color}`;
                }
            });
        });

        // Width selects
        document.querySelectorAll('.priority-width-select').forEach(select => {
            select.addEventListener('change', (e) => {
                const idx = e.target.getAttribute('data-priority-idx');
                const width = e.target.value;
                const color = document.querySelector(`.priority-color-input[data-priority-idx="${idx}"]`).value;
                const preview = document.querySelector(`.priority-preview-${idx}`);
                if (preview) {
                    preview.style.borderLeft = `${width} solid ${color}`;
                }
            });
        });
    }

    /**
     * Attach live preview listeners for Due Date Settings
     */
    attachDueDatePreviewListeners() {
        const updatePreview = (idx) => {
            const borderColor = document.querySelector(`.duedate-border-color-input[data-range-idx="${idx}"]`)?.value;
            const borderType = document.querySelector(`.duedate-border-type-select[data-range-idx="${idx}"]`)?.value;
            const width = document.querySelector(`.duedate-width-select[data-range-idx="${idx}"]`)?.value;
            const bgColorInput = document.querySelector(`.duedate-bg-color-input[data-range-idx="${idx}"]`)?.value;
            const preview = document.querySelector(`.duedate-preview-${idx}`);

            if (preview && borderColor && borderType && width) {
                preview.style.border = `${width} ${borderType} ${borderColor}`;
                preview.style.backgroundColor = bgColorInput || 'transparent';
            }
        };

        // Border color inputs
        document.querySelectorAll('.duedate-border-color-input').forEach(input => {
            input.addEventListener('input', (e) => {
                const idx = e.target.getAttribute('data-range-idx');
                updatePreview(idx);
            });
        });

        // Border type selects
        document.querySelectorAll('.duedate-border-type-select').forEach(select => {
            select.addEventListener('change', (e) => {
                const idx = e.target.getAttribute('data-range-idx');
                updatePreview(idx);
            });
        });

        // Width selects
        document.querySelectorAll('.duedate-width-select').forEach(select => {
            select.addEventListener('change', (e) => {
                const idx = e.target.getAttribute('data-range-idx');
                updatePreview(idx);
            });
        });

        // Background color inputs
        document.querySelectorAll('.duedate-bg-color-input').forEach(input => {
            input.addEventListener('input', (e) => {
                const idx = e.target.getAttribute('data-range-idx');
                updatePreview(idx);
            });
        });
    }

    /**
     * Attach live preview listeners for Banner Settings
     */
    attachBannerPreviewListeners() {
        // Background color inputs
        document.querySelectorAll('.banner-bg-color-input').forEach(input => {
            input.addEventListener('input', (e) => {
                const idx = e.target.getAttribute('data-banner-idx');
                const bgColor = e.target.value;
                const text = document.querySelector(`.banner-text-input[data-banner-idx="${idx}"]`)?.value;
                const preview = document.querySelector(`.banner-preview-${idx}`);
                if (preview) {
                    preview.style.backgroundColor = bgColor;
                    if (text) preview.textContent = text;
                }
            });
        });

        // Text inputs
        document.querySelectorAll('.banner-text-input').forEach(input => {
            input.addEventListener('input', (e) => {
                const idx = e.target.getAttribute('data-banner-idx');
                const text = e.target.value;
                const preview = document.querySelector(`.banner-preview-${idx}`);
                if (preview) {
                    preview.textContent = text;
                }
            });
        });
    }

    /**
     * Convert rgba to hex (helper function)
     */
    rgbaToHex(rgba) {
        if (!rgba || rgba === 'transparent') return '#000000';
        const parts = rgba.match(/[\d.]+/g);
        if (!parts || parts.length < 3) return '#000000';
        const r = parseInt(parts[0]);
        const g = parseInt(parts[1]);
        const b = parseInt(parts[2]);
        return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
    }

    /**
     * Test Advanced Color Settings (Apply to Color Guide + Render Board)
     */
    testAdvancedColorSettings() {
        // Collect settings from tables and temporarily apply them
        this.showNotification('info', 'Testing color changes (not saved)');

        // Force re-render of the board with current table settings
        this.renderKanbanBoard();

        console.log('Test mode: Color settings applied to preview');
    }

    /**
     * Save Advanced Color Settings (to database)
     */
    saveAdvancedColorSettings() {
        this.showNotification('info', 'Save to database - not yet implemented');
        console.log('Save advanced color settings called');
    }

    /**
     * Reset Advanced Color Settings (to defaults)
     */
    resetAdvancedColorSettings() {
        if (confirm('Reset all advanced color settings to defaults?')) {
            this.renderAdvancedColorTables();
            this.showNotification('success', 'Advanced color settings reset to defaults');
        }
    }
}

// OLD REGISTRATION REMOVED - Module now uses simplified pattern at end of file
/*
window.ModuleRegistry = window.ModuleRegistry || {};
window.ModuleRegistry['inhouse_print'] = {
    class: InhouseKanbanModule,
    instance: null,

    init: async function () {
        console.log('🔧 Initializing InHouse Kanban...');

        // Check if sidebar element exists
        const sidebar = document.getElementById('inhouse_print-sidebar');
        if (!sidebar) {
            console.error('❌ Kanban sidebar element not found!');
            return;
        }

        // Initialize sub-tabs
        const subTabs = sidebar.querySelectorAll('.module-sub-tab');
        const tabContents = sidebar.querySelectorAll('.module-sub-tab-content');

        subTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                subTabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));

                tab.classList.add('active');
                const tabId = tab.dataset.tab;
                const content = document.getElementById(tabId);
                if (content) {
                    content.classList.add('active');
                }
            });
        });

        // Create and initialize the Kanban board instance
        this.instance = new InhouseKanbanModule('inhouse_print');

        // Set up controls
        this.setupControls();

        // Load initial data
        await this.loadKanbanData();

        console.log('✅ InHouse Kanban ready');
    },

    setupControls: function () {
        // Timeframe filter
        const timeframeSelect = document.getElementById('kanban-timeframe');
        if (timeframeSelect) {
            timeframeSelect.addEventListener('change', () => {
                this.instance.filters.timeframe_months = parseInt(timeframeSelect.value);
                this.loadKanbanData();
            });
        }

        // Priority filter
        const prioritySelect = document.getElementById('kanban-priority');
        if (prioritySelect) {
            prioritySelect.addEventListener('change', () => {
                this.instance.filters.priority_filter = prioritySelect.value;
                this.loadKanbanData();
            });
        }

        // Search
        const searchInput = document.getElementById('kanban-search');
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                this.instance.filters.search_text = searchInput.value;
                this.filterKanbanBoard();
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('kanban-refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadKanbanData();
            });
        }

        // Analytics refresh button
        const analyticsBtn = document.getElementById('analytics-refresh-btn');
        if (analyticsBtn) {
            analyticsBtn.addEventListener('click', () => {
                this.loadAnalytics();
            });
        }
    },

    async loadKanbanData() {
        const loadingEl = document.getElementById('kanban-loading');
        const boardEl = document.getElementById('kanban-board-container');
        const emptyEl = document.getElementById('kanban-empty');

        if (loadingEl) loadingEl.style.display = 'block';
        if (boardEl) boardEl.style.display = 'none';
        if (emptyEl) emptyEl.style.display = 'none';

        try {
            // Call the backend API
            const response = await fetch(`/api/inhouse-kanban/jobs?timeframe=${this.instance.filters.timeframe_months}`);
            const data = await response.json();

            if (data.success && data.jobs) {
                this.instance.jobs = data.jobs;
                this.instance.stages = data.stages || [];
                this.instance.metrics = data.metrics || {};

                // Update metrics display
                this.updateMetrics();

                // Render Kanban board
                this.instance.renderKanbanBoard();

                if (loadingEl) loadingEl.style.display = 'none';
                if (boardEl) boardEl.style.display = 'block';
            } else {
                if (loadingEl) loadingEl.style.display = 'none';
                if (emptyEl) emptyEl.style.display = 'block';
            }
        } catch (error) {
            console.error('Failed to load Kanban data:', error);
            if (loadingEl) loadingEl.style.display = 'none';
            if (emptyEl) emptyEl.style.display = 'block';
        }
    },

    updateMetrics() {
        const metrics = this.instance.metrics;

        document.getElementById('metric-total-jobs').textContent = metrics.total_jobs || 0;
        document.getElementById('metric-in-progress').textContent = metrics.in_progress || 0;
        document.getElementById('metric-delayed').textContent = metrics.delayed || 0;
        document.getElementById('metric-completed').textContent = metrics.completed || 0;
    },

    filterKanbanBoard() {
        // Filter logic (simplified version)
        const searchText = this.instance.filters.search_text.toLowerCase();
        const cards = document.querySelectorAll('.kanban-card');

        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(searchText) ? 'block' : 'none';
        });
    },

    async loadAnalytics() {
        // Placeholder for analytics loading
        console.log('Loading analytics...');
    }
};
*/

// Module Registry Registration - NEW SIMPLIFIED PATTERN
window.ModuleRegistry = window.ModuleRegistry || {};
window.ModuleRegistry['inhouse-kanban'] = {
    init: async () => {
        console.log('🏭 Initializing InHouse Kanban Module...');
        try {
            const module = new InhouseKanbanModule('inhouse-kanban');
            await module.initialize();
            console.log('✅ InHouse Kanban Module initialized successfully');
            return module;
        } catch (error) {
            console.error('❌ Failed to initialize InHouse Kanban Module:', error);
            throw error;
        }
    }
};

console.log('📦 InHouse Kanban Module script loaded');



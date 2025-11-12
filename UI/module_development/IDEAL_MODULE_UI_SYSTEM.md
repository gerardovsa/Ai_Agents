# 🎨 IDEAL MODULE UI BUILDING SYSTEM
**Created:** November 11, 2025  
**Purpose:** Reusable component system with consistency + flexibility  
**Status:** Design Specification

---

## 🎯 PHILOSOPHY: "Build Once, Use Everywhere"

### **The Problem We're Solving:**

**Current State:**
- Each module reinvents the wheel (buttons, cards, tables)
- Inconsistent styling across modules
- No shared component library
- Copy-paste code between modules
- Hard to maintain visual consistency

**Ideal State:**
- **Component Library** - Pre-built, tested, styled components
- **Consistency** - All modules look professional and cohesive
- **Flexibility** - Easy to customize colors, layout, behavior
- **Speed** - Build new modules 5x faster
- **Maintainability** - Change once, update everywhere

---

## 🏗️ ARCHITECTURE: Three-Layer System

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 3: MODULE CODE                     │
│  (Your custom logic - quotes, stock, communication, etc.)   │
│                                                              │
│  import { Card, Button, Table } from 'ui-components';       │
│  const dashboard = Card.create({title: "Sales"});           │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Uses
                            │
┌─────────────────────────────────────────────────────────────┐
│               LAYER 2: COMPONENT LIBRARY                    │
│     (Pre-built components - cards, buttons, tables)         │
│                                                              │
│  • UIComponents.Card       • UIComponents.Button            │
│  • UIComponents.Table      • UIComponents.Form              │
│  • UIComponents.Modal      • UIComponents.Toast             │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Built on
                            │
┌─────────────────────────────────────────────────────────────┐
│              LAYER 1: DESIGN SYSTEM (CSS)                   │
│        (Design tokens, utilities, base styles)              │
│                                                              │
│  • CSS Variables (colors, spacing, fonts)                   │
│  • Utility Classes (.flex, .grid, .btn, .card)              │
│  • Base Styles (typography, borders, shadows)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 LAYER 1: DESIGN SYSTEM (Foundation)

### **File:** `UI/css/design-tokens.css`

**Purpose:** Single source of truth for all design decisions

```css
/**
 * DESIGN TOKENS - Never use hard-coded values in modules!
 * Version: 2.0.0
 */

:root {
    /* ================================================================
       COLORS - Professional, flexible, consistent
       ================================================================ */
    
    /* Primary Brand Colors */
    --color-primary: #3b82f6;           /* Blue - main actions */
    --color-primary-hover: #2563eb;     /* Darker on hover */
    --color-primary-light: rgba(59, 130, 246, 0.1);  /* Backgrounds */
    --color-primary-border: rgba(59, 130, 246, 0.3); /* Borders */
    
    /* Secondary/Accent */
    --color-secondary: #10b981;         /* Green - success actions */
    --color-secondary-hover: #059669;
    --color-secondary-light: rgba(16, 185, 129, 0.1);
    
    /* Semantic Colors */
    --color-success: #10b981;    /* Green */
    --color-warning: #f59e0b;    /* Amber */
    --color-error: #ef4444;      /* Red */
    --color-info: #3b82f6;       /* Blue */
    
    /* Neutrals - Dark theme */
    --color-bg-primary: #0a0a0a;        /* Main background */
    --color-bg-secondary: #161616;      /* Cards, panels */
    --color-bg-tertiary: #1e1e1e;       /* Hover states */
    --color-bg-elevated: #242424;       /* Modals, dropdowns */
    
    /* Text */
    --color-text-primary: #ffffff;      /* Headings, important text */
    --color-text-secondary: #b8bcc8;    /* Body text, labels */
    --color-text-tertiary: #6b7280;     /* Disabled, placeholder */
    --color-text-inverse: #0a0a0a;      /* Text on light backgrounds */
    
    /* Borders */
    --color-border-default: #30363d;    /* Standard borders */
    --color-border-hover: #444c56;      /* Hover state borders */
    --color-border-focus: #3b82f6;      /* Focus/active borders */
    
    /* ================================================================
       TYPOGRAPHY - Consistent text hierarchy
       ================================================================ */
    
    --font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-family-mono: 'Roboto Mono', 'Courier New', monospace;
    
    /* Font Sizes - Use these, never px values! */
    --text-xs: 0.75rem;      /* 12px - tiny labels */
    --text-sm: 0.875rem;     /* 14px - body text */
    --text-base: 1rem;       /* 16px - default */
    --text-lg: 1.125rem;     /* 18px - subtabs, large labels */
    --text-xl: 1.25rem;      /* 20px - card values */
    --text-2xl: 1.5rem;      /* 24px - section headings */
    --text-3xl: 1.875rem;    /* 30px - page headings */
    --text-4xl: 2.25rem;     /* 36px - hero text */
    
    /* Font Weights */
    --font-normal: 400;
    --font-medium: 500;
    --font-semibold: 600;
    --font-bold: 700;
    
    /* ================================================================
       SPACING - Consistent margins and padding
       ================================================================ */
    
    --space-1: 0.25rem;   /* 4px */
    --space-2: 0.5rem;    /* 8px */
    --space-3: 0.75rem;   /* 12px */
    --space-4: 1rem;      /* 16px */
    --space-5: 1.5rem;    /* 24px */
    --space-6: 2rem;      /* 32px */
    --space-8: 3rem;      /* 48px */
    --space-10: 4rem;     /* 64px */
    
    /* ================================================================
       BORDERS & RADIUS - Modern, subtle
       ================================================================ */
    
    --radius-sm: 4px;      /* Buttons, tags */
    --radius-md: 6px;      /* Cards, inputs */
    --radius-lg: 8px;      /* Modals, panels */
    --radius-xl: 12px;     /* Large cards */
    --radius-full: 9999px; /* Pills, avatars */
    
    --border-width: 1px;
    --border-width-thick: 2px;
    
    /* ================================================================
       SHADOWS - Subtle depth
       ================================================================ */
    
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.4);
    --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.5);
    
    /* ================================================================
       TRANSITIONS - Smooth, professional
       ================================================================ */
    
    --transition-fast: 150ms ease;
    --transition-base: 200ms ease;
    --transition-slow: 300ms ease;
    
    /* ================================================================
       Z-INDEX SCALE - Prevent layering issues
       ================================================================ */
    
    --z-base: 0;
    --z-dropdown: 1000;
    --z-sticky: 1100;
    --z-modal-backdrop: 1200;
    --z-modal: 1300;
    --z-popover: 1400;
    --z-toast: 1500;
    --z-tooltip: 1600;
}

/* ================================================================
   MODULE COLOR CUSTOMIZATION
   ================================================================ */

/* Each module can override primary color while keeping everything else consistent */
.module-quote-calculator {
    --color-primary: #f59e0b;        /* Orange */
    --color-primary-hover: #d97706;
    --color-primary-light: rgba(245, 158, 11, 0.1);
}

.module-communication-hub {
    --color-primary: #8b5cf6;        /* Purple */
    --color-primary-hover: #7c3aed;
    --color-primary-light: rgba(139, 92, 246, 0.1);
}

.module-stock-management {
    --color-primary: #10b981;        /* Green */
    --color-primary-hover: #059669;
    --color-primary-light: rgba(16, 185, 129, 0.1);
}

/* ================================================================
   UTILITY CLASSES - Use these in HTML
   ================================================================ */

/* Flexbox */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }
.items-center { align-items: center; }
.items-start { align-items: flex-start; }
.items-end { align-items: flex-end; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.justify-end { justify-content: flex-end; }
.gap-1 { gap: var(--space-1); }
.gap-2 { gap: var(--space-2); }
.gap-3 { gap: var(--space-3); }
.gap-4 { gap: var(--space-4); }
.gap-5 { gap: var(--space-5); }

/* Grid */
.grid { display: grid; }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

/* Spacing */
.m-0 { margin: 0; }
.m-auto { margin: auto; }
.mt-2 { margin-top: var(--space-2); }
.mt-4 { margin-top: var(--space-4); }
.mb-4 { margin-bottom: var(--space-4); }
.mb-6 { margin-bottom: var(--space-6); }
.p-4 { padding: var(--space-4); }
.px-4 { padding-left: var(--space-4); padding-right: var(--space-4); }
.py-2 { padding-top: var(--space-2); padding-bottom: var(--space-2); }

/* Text */
.text-xs { font-size: var(--text-xs); }
.text-sm { font-size: var(--text-sm); }
.text-base { font-size: var(--text-base); }
.text-lg { font-size: var(--text-lg); }
.text-xl { font-size: var(--text-xl); }
.text-2xl { font-size: var(--text-2xl); }
.text-center { text-align: center; }
.text-right { text-align: right; }
.font-medium { font-weight: var(--font-medium); }
.font-semibold { font-weight: var(--font-semibold); }
.font-bold { font-weight: var(--font-bold); }

/* Colors */
.text-primary { color: var(--color-text-primary); }
.text-secondary { color: var(--color-text-secondary); }
.text-success { color: var(--color-success); }
.text-error { color: var(--color-error); }
.text-warning { color: var(--color-warning); }

/* Borders */
.border { border: var(--border-width) solid var(--color-border-default); }
.border-t { border-top: var(--border-width) solid var(--color-border-default); }
.border-b { border-bottom: var(--border-width) solid var(--color-border-default); }
.rounded { border-radius: var(--radius-md); }
.rounded-lg { border-radius: var(--radius-lg); }
.rounded-full { border-radius: var(--radius-full); }

/* Width */
.w-full { width: 100%; }
.w-auto { width: auto; }
.h-full { height: 100%; }

/* Visibility */
.hidden { display: none; }
.visible { visibility: visible; }
.invisible { visibility: hidden; }

/* Cursor */
.cursor-pointer { cursor: pointer; }
.cursor-not-allowed { cursor: not-allowed; }

/* Overflow */
.overflow-hidden { overflow: hidden; }
.overflow-auto { overflow: auto; }
```

---

## 🧩 LAYER 2: COMPONENT LIBRARY

### **File:** `UI/js/ui-components.js`

**Purpose:** Reusable, tested, styled components - your building blocks

```javascript
/**
 * UI COMPONENTS LIBRARY
 * Version: 2.0.0
 * Created: November 11, 2025
 * 
 * Pre-built components with consistent styling and behavior.
 * All components use design tokens from design-tokens.css
 * 
 * USAGE:
 * import UIComponents from './ui-components.js';
 * const card = UIComponents.Card.create({title: "Dashboard"});
 */

const UIComponents = {

    // ================================================================
    // CARDS - Dashboard cards, metric cards, info cards
    // ================================================================
    
    Card: {
        /**
         * Create a metric/stat card
         * Perfect for dashboards showing KPIs
         * 
         * @example
         * UIComponents.Card.metric({
         *   label: "Total Sales",
         *   value: "$45,231",
         *   change: {value: "+12%", trend: "up"},
         *   icon: "fa-dollar-sign",
         *   color: "success"
         * })
         */
        metric(options) {
            const {
                label,           // "Total Sales"
                value,           // "$45,231"
                change = null,   // {value: "+12%", trend: "up"|"down"|"neutral"}
                icon = null,     // "fa-dollar-sign"
                color = null,    // "primary"|"success"|"warning"|"error"|"info"
                footer = null,   // "Last 30 days"
                onClick = null   // Click handler
            } = options;
            
            const card = document.createElement('div');
            card.className = 'ui-card ui-card-metric';
            if (color) card.classList.add(`ui-card-${color}`);
            if (onClick) {
                card.style.cursor = 'pointer';
                card.addEventListener('click', onClick);
            }
            
            // Icon
            if (icon) {
                const iconContainer = document.createElement('div');
                iconContainer.className = 'ui-card-icon';
                iconContainer.innerHTML = `<i class="${icon}"></i>`;
                card.appendChild(iconContainer);
            }
            
            // Content
            const content = document.createElement('div');
            content.className = 'ui-card-content';
            
            const labelEl = document.createElement('div');
            labelEl.className = 'ui-card-label text-sm text-secondary';
            labelEl.textContent = label;
            content.appendChild(labelEl);
            
            const valueEl = document.createElement('div');
            valueEl.className = 'ui-card-value text-2xl font-semibold';
            valueEl.textContent = value;
            content.appendChild(valueEl);
            
            // Change indicator
            if (change) {
                const changeEl = document.createElement('div');
                changeEl.className = `ui-card-change ${change.trend}`;
                const arrow = change.trend === 'up' ? '↑' : (change.trend === 'down' ? '↓' : '→');
                changeEl.innerHTML = `<span>${arrow}</span> <span>${change.value}</span>`;
                content.appendChild(changeEl);
            }
            
            // Footer
            if (footer) {
                const footerEl = document.createElement('div');
                footerEl.className = 'ui-card-footer text-xs text-tertiary';
                footerEl.textContent = footer;
                content.appendChild(footerEl);
            }
            
            card.appendChild(content);
            return card;
        },
        
        /**
         * Create a content card with header
         * Perfect for sections with title and actions
         * 
         * @example
         * UIComponents.Card.section({
         *   title: "Recent Orders",
         *   icon: "fa-shopping-cart",
         *   actions: [{label: "View All", onClick: () => {}}],
         *   content: tableElement
         * })
         */
        section(options) {
            const {
                title,
                icon = null,
                subtitle = null,
                actions = [],
                content = null,
                footer = null
            } = options;
            
            const card = document.createElement('div');
            card.className = 'ui-card ui-card-section';
            
            // Header
            const header = document.createElement('div');
            header.className = 'ui-card-header flex items-center justify-between';
            
            const titleContainer = document.createElement('div');
            titleContainer.className = 'flex items-center gap-3';
            
            if (icon) {
                const iconEl = document.createElement('i');
                iconEl.className = `${icon} text-xl`;
                titleContainer.appendChild(iconEl);
            }
            
            const titleGroup = document.createElement('div');
            const titleEl = document.createElement('h3');
            titleEl.className = 'text-lg font-medium';
            titleEl.textContent = title;
            titleGroup.appendChild(titleEl);
            
            if (subtitle) {
                const subtitleEl = document.createElement('p');
                subtitleEl.className = 'text-sm text-secondary';
                subtitleEl.textContent = subtitle;
                titleGroup.appendChild(subtitleEl);
            }
            
            titleContainer.appendChild(titleGroup);
            header.appendChild(titleContainer);
            
            // Actions
            if (actions.length > 0) {
                const actionsContainer = document.createElement('div');
                actionsContainer.className = 'flex gap-2';
                
                actions.forEach(action => {
                    const btn = UIComponents.Button.create({
                        label: action.label,
                        icon: action.icon,
                        variant: action.variant || 'ghost',
                        size: 'sm',
                        onClick: action.onClick
                    });
                    actionsContainer.appendChild(btn);
                });
                
                header.appendChild(actionsContainer);
            }
            
            card.appendChild(header);
            
            // Body
            if (content) {
                const body = document.createElement('div');
                body.className = 'ui-card-body';
                if (typeof content === 'string') {
                    body.innerHTML = content;
                } else {
                    body.appendChild(content);
                }
                card.appendChild(body);
            }
            
            // Footer
            if (footer) {
                const footerEl = document.createElement('div');
                footerEl.className = 'ui-card-footer';
                if (typeof footer === 'string') {
                    footerEl.innerHTML = footer;
                } else {
                    footerEl.appendChild(footer);
                }
                card.appendChild(footerEl);
            }
            
            return card;
        }
    },
    
    // ================================================================
    // BUTTONS - Primary, secondary, ghost, icon-only
    // ================================================================
    
    Button: {
        /**
         * Create a button
         * 
         * @example
         * UIComponents.Button.create({
         *   label: "Save Changes",
         *   icon: "fa-save",
         *   variant: "primary",
         *   onClick: () => {}
         * })
         */
        create(options) {
            const {
                label,
                icon = null,
                variant = 'primary',  // primary|secondary|success|danger|warning|ghost
                size = 'md',           // sm|md|lg
                disabled = false,
                loading = false,
                onClick = null,
                fullWidth = false
            } = options;
            
            const btn = document.createElement('button');
            btn.className = `ui-btn ui-btn-${variant} ui-btn-${size}`;
            if (fullWidth) btn.classList.add('ui-btn-full');
            if (disabled || loading) btn.disabled = true;
            
            if (loading) {
                const spinner = document.createElement('i');
                spinner.className = 'fa fa-spinner fa-spin';
                btn.appendChild(spinner);
            } else if (icon) {
                const iconEl = document.createElement('i');
                iconEl.className = icon;
                btn.appendChild(iconEl);
            }
            
            if (label) {
                const labelEl = document.createElement('span');
                labelEl.textContent = label;
                btn.appendChild(labelEl);
            }
            
            if (onClick) {
                btn.addEventListener('click', onClick);
            }
            
            return btn;
        },
        
        /**
         * Create button group
         * 
         * @example
         * UIComponents.Button.group([
         *   {label: "Day", active: true},
         *   {label: "Week"},
         *   {label: "Month"}
         * ])
         */
        group(buttons) {
            const group = document.createElement('div');
            group.className = 'ui-btn-group';
            
            buttons.forEach(btnOpts => {
                const btn = this.create(btnOpts);
                if (btnOpts.active) btn.classList.add('active');
                group.appendChild(btn);
            });
            
            return group;
        }
    },
    
    // ================================================================
    // TABS - Subtab navigation, pill tabs
    // ================================================================
    
    Tabs: {
        /**
         * Create tab navigation
         * 
         * @example
         * UIComponents.Tabs.create({
         *   tabs: [
         *     {id: "overview", label: "Overview", icon: "fa-home", active: true},
         *     {id: "details", label: "Details", icon: "fa-list"}
         *   ],
         *   onChange: (tabId) => {}
         * })
         */
        create(options) {
            const {
                tabs,
                activeTab = null,
                onChange = null,
                variant = 'underline'  // underline|pills
            } = options;
            
            const container = document.createElement('div');
            container.className = `ui-tabs ui-tabs-${variant}`;
            
            tabs.forEach(tab => {
                const btn = document.createElement('button');
                btn.className = 'ui-tab';
                btn.dataset.tabId = tab.id;
                
                if (tab.id === activeTab || tab.active) {
                    btn.classList.add('active');
                }
                
                if (tab.icon) {
                    const icon = document.createElement('i');
                    icon.className = tab.icon;
                    btn.appendChild(icon);
                }
                
                const label = document.createElement('span');
                label.textContent = tab.label;
                btn.appendChild(label);
                
                if (tab.badge) {
                    const badge = document.createElement('span');
                    badge.className = 'ui-badge';
                    badge.textContent = tab.badge;
                    btn.appendChild(badge);
                }
                
                btn.addEventListener('click', () => {
                    // Update active state
                    container.querySelectorAll('.ui-tab').forEach(t => t.classList.remove('active'));
                    btn.classList.add('active');
                    
                    // Call handler
                    if (onChange) onChange(tab.id);
                    if (tab.onClick) tab.onClick();
                });
                
                container.appendChild(btn);
            });
            
            return container;
        }
    },
    
    // ================================================================
    // FORMS - Inputs, selects, checkboxes, form groups
    // ================================================================
    
    Form: {
        /**
         * Create form input
         * 
         * @example
         * UIComponents.Form.input({
         *   label: "Email Address",
         *   type: "email",
         *   placeholder: "you@example.com",
         *   required: true
         * })
         */
        input(options) {
            const {
                label = null,
                type = 'text',
                placeholder = '',
                value = '',
                required = false,
                disabled = false,
                error = null,
                hint = null,
                icon = null
            } = options;
            
            const group = document.createElement('div');
            group.className = 'ui-form-group';
            
            // Label
            if (label) {
                const labelEl = document.createElement('label');
                labelEl.className = 'ui-form-label';
                labelEl.innerHTML = label + (required ? ' <span class="text-error">*</span>' : '');
                group.appendChild(labelEl);
            }
            
            // Input container
            const inputContainer = document.createElement('div');
            inputContainer.className = 'ui-form-input-container';
            
            // Icon
            if (icon) {
                const iconEl = document.createElement('i');
                iconEl.className = `${icon} ui-form-icon`;
                inputContainer.appendChild(iconEl);
            }
            
            // Input
            const input = document.createElement('input');
            input.type = type;
            input.className = 'ui-form-input';
            input.placeholder = placeholder;
            input.value = value;
            input.required = required;
            input.disabled = disabled;
            if (icon) input.classList.add('has-icon');
            if (error) input.classList.add('error');
            
            inputContainer.appendChild(input);
            group.appendChild(inputContainer);
            
            // Error message
            if (error) {
                const errorEl = document.createElement('div');
                errorEl.className = 'ui-form-error text-error text-sm';
                errorEl.textContent = error;
                group.appendChild(errorEl);
            }
            
            // Hint
            if (hint && !error) {
                const hintEl = document.createElement('div');
                hintEl.className = 'ui-form-hint text-tertiary text-sm';
                hintEl.textContent = hint;
                group.appendChild(hintEl);
            }
            
            return group;
        },
        
        /**
         * Create select dropdown
         */
        select(options) {
            const {
                label = null,
                options: selectOptions,
                value = '',
                required = false,
                disabled = false,
                onChange = null
            } = options;
            
            const group = document.createElement('div');
            group.className = 'ui-form-group';
            
            if (label) {
                const labelEl = document.createElement('label');
                labelEl.className = 'ui-form-label';
                labelEl.innerHTML = label + (required ? ' <span class="text-error">*</span>' : '');
                group.appendChild(labelEl);
            }
            
            const select = document.createElement('select');
            select.className = 'ui-form-select';
            select.required = required;
            select.disabled = disabled;
            
            selectOptions.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt.value;
                option.textContent = opt.label;
                if (opt.value === value) option.selected = true;
                select.appendChild(option);
            });
            
            if (onChange) {
                select.addEventListener('change', (e) => onChange(e.target.value));
            }
            
            group.appendChild(select);
            return group;
        }
    },
    
    // ================================================================
    // LAYOUT - Grids, stacks, dividers
    // ================================================================
    
    Layout: {
        /**
         * Create responsive grid for metrics/cards
         * 
         * @example
         * const grid = UIComponents.Layout.grid({columns: 4});
         * grid.appendChild(metricCard1);
         * grid.appendChild(metricCard2);
         */
        grid(options = {}) {
            const {
                columns = 4,      // Number of columns
                gap = 4,          // Gap size (1-10)
                className = ''
            } = options;
            
            const grid = document.createElement('div');
            grid.className = `ui-grid grid-cols-${columns} gap-${gap} ${className}`;
            return grid;
        },
        
        /**
         * Create vertical stack
         */
        stack(options = {}) {
            const {
                gap = 4,
                className = ''
            } = options;
            
            const stack = document.createElement('div');
            stack.className = `flex flex-col gap-${gap} ${className}`;
            return stack;
        },
        
        /**
         * Create horizontal divider
         */
        divider(options = {}) {
            const {
                label = null,
                className = ''
            } = options;
            
            if (!label) {
                const div = document.createElement('div');
                div.className = `ui-divider ${className}`;
                return div;
            }
            
            // Divider with label
            const container = document.createElement('div');
            container.className = `ui-divider-label ${className}`;
            container.innerHTML = `
                <div class="ui-divider-line"></div>
                <span class="ui-divider-text">${label}</span>
                <div class="ui-divider-line"></div>
            `;
            return container;
        }
    },
    
    // ================================================================
    // FEEDBACK - Toasts, modals, alerts
    // ================================================================
    
    Toast: {
        /**
         * Show toast notification
         * 
         * @example
         * UIComponents.Toast.success("Order saved successfully!");
         */
        show(message, type = 'info', duration = 3000) {
            const toast = document.createElement('div');
            toast.className = `ui-toast ui-toast-${type}`;
            
            const icon = {
                success: 'fa-check-circle',
                error: 'fa-times-circle',
                warning: 'fa-exclamation-triangle',
                info: 'fa-info-circle'
            }[type];
            
            toast.innerHTML = `
                <i class="${icon}"></i>
                <span>${message}</span>
                <button class="ui-toast-close"><i class="fa fa-times"></i></button>
            `;
            
            // Close button
            toast.querySelector('.ui-toast-close').addEventListener('click', () => {
                toast.remove();
            });
            
            // Auto-dismiss
            if (duration > 0) {
                setTimeout(() => toast.remove(), duration);
            }
            
            // Add to DOM
            let container = document.querySelector('.ui-toast-container');
            if (!container) {
                container = document.createElement('div');
                container.className = 'ui-toast-container';
                document.body.appendChild(container);
            }
            container.appendChild(toast);
            
            return toast;
        },
        
        success: (msg, duration) => UIComponents.Toast.show(msg, 'success', duration),
        error: (msg, duration) => UIComponents.Toast.show(msg, 'error', duration),
        warning: (msg, duration) => UIComponents.Toast.show(msg, 'warning', duration),
        info: (msg, duration) => UIComponents.Toast.show(msg, 'info', duration)
    },
    
    // ================================================================
    // TABLES - Wrapper for Tabulator with standard config
    // ================================================================
    
    Table: {
        /**
         * Create Tabulator table with standard styling
         * 
         * @example
         * UIComponents.Table.create({
         *   container: '#table-container',
         *   columns: [{title: "Name", field: "name"}],
         *   data: []
         * })
         */
        create(options) {
            const {
                container,
                columns,
                data = [],
                pagination = true,
                pageSize = 20,
                selectable = false,
                ...tabulatorOptions
            } = options;
            
            const config = {
                data: data,
                columns: columns,
                layout: 'fitColumns',
                responsiveLayout: 'collapse',
                pagination: pagination,
                paginationSize: pageSize,
                paginationSizeSelector: [10, 20, 50, 100],
                selectableRows: selectable ? true : false,
                ...tabulatorOptions
            };
            
            return new Tabulator(container, config);
        }
    }
};

// Export globally
window.UIComponents = UIComponents;

// Export as module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIComponents;
}
```

---

## 🎨 CSS FOR COMPONENTS

### **File:** `UI/css/ui-components.css`

```css
/**
 * UI COMPONENTS STYLING
 * Styles for all UIComponents library elements
 */

/* ================================================================
   CARDS
   ================================================================ */

.ui-card {
    background: var(--color-bg-secondary);
    border: var(--border-width) solid var(--color-border-default);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    transition: all var(--transition-base);
}

.ui-card:hover {
    border-color: var(--color-border-hover);
}

/* Metric Cards */
.ui-card-metric {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-4);
    position: relative;
    overflow: hidden;
    cursor: default;
}

/* Colored accent bar */
.ui-card-metric::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: var(--color-primary);
}

.ui-card-metric.ui-card-success::before {
    background: var(--color-success);
}

.ui-card-metric.ui-card-error::before {
    background: var(--color-error);
}

.ui-card-metric.ui-card-warning::before {
    background: var(--color-warning);
}

.ui-card-metric:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.ui-card-icon {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    background: var(--color-primary-light);
    color: var(--color-primary);
    flex-shrink: 0;
}

.ui-card-success .ui-card-icon {
    background: var(--color-secondary-light);
    color: var(--color-secondary);
}

.ui-card-content {
    flex: 1;
    min-width: 0;
}

.ui-card-label {
    margin-bottom: var(--space-1);
}

.ui-card-value {
    margin-bottom: var(--space-2);
    line-height: 1;
}

.ui-card-change {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
}

.ui-card-change.up {
    color: var(--color-success);
}

.ui-card-change.down {
    color: var(--color-error);
}

.ui-card-change.neutral {
    color: var(--color-text-secondary);
}

.ui-card-footer {
    margin-top: var(--space-2);
}

/* Section Cards */
.ui-card-section {
    padding: 0;
}

.ui-card-header {
    padding: var(--space-4);
    border-bottom: var(--border-width) solid var(--color-border-default);
}

.ui-card-body {
    padding: var(--space-4);
}

.ui-card-footer {
    padding: var(--space-4);
    border-top: var(--border-width) solid var(--color-border-default);
    background: var(--color-bg-tertiary);
}

/* ================================================================
   BUTTONS
   ================================================================ */

.ui-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    font-family: var(--font-family);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    border-radius: var(--radius-sm);
    border: var(--border-width) solid transparent;
    cursor: pointer;
    transition: all var(--transition-fast);
    white-space: nowrap;
}

.ui-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Button Variants */
.ui-btn-primary {
    background: var(--color-primary);
    color: white;
    border-color: var(--color-primary);
}

.ui-btn-primary:hover:not(:disabled) {
    background: var(--color-primary-hover);
    border-color: var(--color-primary-hover);
}

.ui-btn-secondary {
    background: var(--color-bg-tertiary);
    color: var(--color-text-primary);
    border-color: var(--color-border-default);
}

.ui-btn-secondary:hover:not(:disabled) {
    background: var(--color-bg-elevated);
    border-color: var(--color-border-hover);
}

.ui-btn-success {
    background: var(--color-success);
    color: white;
}

.ui-btn-danger {
    background: var(--color-error);
    color: white;
}

.ui-btn-ghost {
    background: transparent;
    color: var(--color-text-secondary);
    border-color: transparent;
}

.ui-btn-ghost:hover:not(:disabled) {
    background: var(--color-bg-tertiary);
    color: var(--color-text-primary);
}

/* Button Sizes */
.ui-btn-sm {
    padding: var(--space-1) var(--space-3);
    font-size: var(--text-xs);
}

.ui-btn-lg {
    padding: var(--space-3) var(--space-5);
    font-size: var(--text-base);
}

.ui-btn-full {
    width: 100%;
}

/* Button Group */
.ui-btn-group {
    display: inline-flex;
    border-radius: var(--radius-sm);
    overflow: hidden;
}

.ui-btn-group .ui-btn {
    border-radius: 0;
    border-right: none;
}

.ui-btn-group .ui-btn:first-child {
    border-radius: var(--radius-sm) 0 0 var(--radius-sm);
}

.ui-btn-group .ui-btn:last-child {
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    border-right: var(--border-width) solid;
}

.ui-btn-group .ui-btn.active {
    background: var(--color-primary);
    color: white;
    border-color: var(--color-primary);
}

/* ================================================================
   TABS
   ================================================================ */

.ui-tabs {
    display: flex;
    gap: var(--space-2);
    border-bottom: 2px solid var(--color-border-default);
    margin-bottom: var(--space-5);
}

.ui-tab {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-4);
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--color-text-secondary);
    font-size: var(--text-lg);
    font-weight: var(--font-medium);
    cursor: pointer;
    transition: all var(--transition-fast);
    margin-bottom: -2px;
}

.ui-tab:hover {
    color: var(--color-text-primary);
}

.ui-tab.active {
    color: var(--color-primary);
    border-bottom-color: var(--color-primary);
    font-weight: var(--font-semibold);
}

.ui-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 20px;
    height: 20px;
    padding: 0 var(--space-1);
    background: var(--color-primary);
    color: white;
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    border-radius: var(--radius-full);
}

/* ================================================================
   FORMS
   ================================================================ */

.ui-form-group {
    margin-bottom: var(--space-4);
}

.ui-form-label {
    display: block;
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    color: var(--color-text-primary);
    margin-bottom: var(--space-2);
}

.ui-form-input-container {
    position: relative;
}

.ui-form-icon {
    position: absolute;
    left: var(--space-3);
    top: 50%;
    transform: translateY(-50%);
    color: var(--color-text-tertiary);
}

.ui-form-input {
    width: 100%;
    padding: var(--space-3);
    font-family: var(--font-family);
    font-size: var(--text-sm);
    color: var(--color-text-primary);
    background: var(--color-bg-tertiary);
    border: var(--border-width) solid var(--color-border-default);
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
}

.ui-form-input.has-icon {
    padding-left: calc(var(--space-3) * 2 + 16px);
}

.ui-form-input:focus {
    outline: none;
    border-color: var(--color-border-focus);
    box-shadow: 0 0 0 3px var(--color-primary-light);
}

.ui-form-input.error {
    border-color: var(--color-error);
}

.ui-form-error {
    margin-top: var(--space-1);
}

.ui-form-hint {
    margin-top: var(--space-1);
}

.ui-form-select {
    width: 100%;
    padding: var(--space-3);
    font-family: var(--font-family);
    font-size: var(--text-sm);
    color: var(--color-text-primary);
    background: var(--color-bg-tertiary);
    border: var(--border-width) solid var(--color-border-default);
    border-radius: var(--radius-sm);
    cursor: pointer;
}

/* ================================================================
   LAYOUT
   ================================================================ */

.ui-grid {
    display: grid;
    gap: var(--space-4);
}

.ui-divider {
    height: var(--border-width);
    background: var(--color-border-default);
    margin: var(--space-5) 0;
}

.ui-divider-label {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin: var(--space-5) 0;
}

.ui-divider-line {
    flex: 1;
    height: var(--border-width);
    background: var(--color-border-default);
}

.ui-divider-text {
    color: var(--color-text-secondary);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
}

/* ================================================================
   TOAST NOTIFICATIONS
   ================================================================ */

.ui-toast-container {
    position: fixed;
    top: var(--space-5);
    right: var(--space-5);
    z-index: var(--z-toast);
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
}

.ui-toast {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    background: var(--color-bg-elevated);
    border: var(--border-width) solid var(--color-border-default);
    border-left-width: 4px;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    min-width: 300px;
    max-width: 400px;
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.ui-toast-success {
    border-left-color: var(--color-success);
    color: var(--color-success);
}

.ui-toast-error {
    border-left-color: var(--color-error);
    color: var(--color-error);
}

.ui-toast-warning {
    border-left-color: var(--color-warning);
    color: var(--color-warning);
}

.ui-toast-info {
    border-left-color: var(--color-info);
    color: var(--color-info);
}

.ui-toast span {
    flex: 1;
    color: var(--color-text-primary);
}

.ui-toast-close {
    background: none;
    border: none;
    color: var(--color-text-secondary);
    cursor: pointer;
    padding: 0;
    font-size: var(--text-sm);
}
```

---

## 🚀 LAYER 3: MODULE USAGE EXAMPLES

### **Example 1: Simple Dashboard Module**

```javascript
// modules/sales-dashboard/sales-dashboard.js

class SalesDashboardModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);
        this.salesData = null;
    }
    
    async initialize() {
        await super.initialize();
        
        // Fetch data
        this.salesData = await this.fetchSalesData();
        
        // Build UI using components
        this.buildDashboard();
    }
    
    buildDashboard() {
        const container = document.getElementById('tab-overview-content');
        
        // Metrics Grid
        const metricsGrid = UIComponents.Layout.grid({columns: 4, gap: 4});
        
        // Total Sales Card
        const totalSales = UIComponents.Card.metric({
            label: "Total Sales",
            value: `$${this.salesData.total.toLocaleString()}`,
            change: {value: "+12.5%", trend: "up"},
            icon: "fa fa-dollar-sign",
            color: "success",
            footer: "Last 30 days"
        });
        metricsGrid.appendChild(totalSales);
        
        // Orders Card
        const orders = UIComponents.Card.metric({
            label: "Orders",
            value: this.salesData.orderCount,
            change: {value: "+8%", trend: "up"},
            icon: "fa fa-shopping-cart",
            color: "primary",
            footer: "Last 30 days"
        });
        metricsGrid.appendChild(orders);
        
        // Avg Order Value
        const avgOrder = UIComponents.Card.metric({
            label: "Avg Order Value",
            value: `$${this.salesData.avgOrder}`,
            change: {value: "-2%", trend: "down"},
            icon: "fa fa-receipt",
            color: "warning",
            footer: "Last 30 days"
        });
        metricsGrid.appendChild(avgOrder);
        
        // Conversion Rate
        const conversion = UIComponents.Card.metric({
            label: "Conversion Rate",
            value: `${this.salesData.conversion}%`,
            change: {value: "+0.5%", trend: "up"},
            icon: "fa fa-chart-line",
            color: "info",
            footer: "Last 30 days"
        });
        metricsGrid.appendChild(conversion);
        
        container.appendChild(metricsGrid);
        
        // Recent Orders Table
        const ordersCard = UIComponents.Card.section({
            title: "Recent Orders",
            icon: "fa fa-list",
            actions: [
                {
                    label: "Export",
                    icon: "fa fa-download",
                    variant: "ghost",
                    onClick: () => this.exportOrders()
                },
                {
                    label: "Refresh",
                    icon: "fa fa-sync",
                    variant: "ghost",
                    onClick: () => this.refreshOrders()
                }
            ],
            content: '<div id="orders-table"></div>'
        });
        container.appendChild(ordersCard);
        
        // Initialize table
        this.ordersTable = UIComponents.Table.create({
            container: '#orders-table',
            columns: [
                {title: "Order #", field: "id", width: 100},
                {title: "Customer", field: "customer"},
                {title: "Total", field: "total", formatter: "money"},
                {title: "Status", field: "status"},
                {title: "Date", field: "date"}
            ],
            data: this.salesData.orders,
            pagination: true,
            pageSize: 10,
            selectable: true
        });
    }
    
    async fetchSalesData() {
        // API call or backend integration
        const response = await fetch('/api/sales/dashboard');
        return await response.json();
    }
    
    exportOrders() {
        UIComponents.Toast.info("Exporting orders...");
        // Export logic
    }
    
    refreshOrders() {
        UIComponents.Toast.info("Refreshing data...");
        // Refresh logic
    }
}

// Register module
window.SalesDashboardModule = SalesDashboardModule;
```

### **Example 2: Form-Heavy Module**

```javascript
// modules/customer-management/customer-management.js

class CustomerManagementModule extends BaseModule {
    buildNewCustomerForm() {
        const container = document.getElementById('tab-new-customer-content');
        
        // Form container
        const formCard = UIComponents.Card.section({
            title: "New Customer",
            icon: "fa fa-user-plus",
            content: ''
        });
        
        const form = document.createElement('form');
        form.className = 'customer-form';
        
        // Name input
        const nameInput = UIComponents.Form.input({
            label: "Full Name",
            type: "text",
            placeholder: "John Smith",
            required: true,
            icon: "fa fa-user"
        });
        form.appendChild(nameInput);
        
        // Email input
        const emailInput = UIComponents.Form.input({
            label: "Email Address",
            type: "email",
            placeholder: "john@example.com",
            required: true,
            icon: "fa fa-envelope",
            hint: "We'll never share your email"
        });
        form.appendChild(emailInput);
        
        // Phone input
        const phoneInput = UIComponents.Form.input({
            label: "Phone Number",
            type: "tel",
            placeholder: "(555) 123-4567",
            icon: "fa fa-phone"
        });
        form.appendChild(phoneInput);
        
        // Customer type
        const typeSelect = UIComponents.Form.select({
            label: "Customer Type",
            required: true,
            options: [
                {value: "", label: "Select type..."},
                {value: "retail", label: "Retail Customer"},
                {value: "wholesale", label: "Wholesale Customer"},
                {value: "vip", label: "VIP Customer"}
            ]
        });
        form.appendChild(typeSelect);
        
        // Divider
        form.appendChild(UIComponents.Layout.divider({label: "Address Information"}));
        
        // Address fields...
        const addressInput = UIComponents.Form.input({
            label: "Street Address",
            type: "text",
            placeholder: "123 Main St",
            icon: "fa fa-map-marker-alt"
        });
        form.appendChild(addressInput);
        
        // Action buttons
        const actions = document.createElement('div');
        actions.className = 'flex justify-end gap-3 mt-6';
        
        const cancelBtn = UIComponents.Button.create({
            label: "Cancel",
            variant: "ghost",
            onClick: () => this.cancelForm()
        });
        actions.appendChild(cancelBtn);
        
        const saveBtn = UIComponents.Button.create({
            label: "Save Customer",
            icon: "fa fa-save",
            variant: "primary",
            onClick: () => this.saveCustomer(form)
        });
        actions.appendChild(saveBtn);
        
        form.appendChild(actions);
        
        formCard.querySelector('.ui-card-body').appendChild(form);
        container.appendChild(formCard);
    }
    
    async saveCustomer(form) {
        // Validate and save
        UIComponents.Toast.success("Customer saved successfully!");
    }
}
```

---

## 🎨 CUSTOMIZATION PATTERNS

### **Pattern 1: Module-Specific Colors**

```javascript
// In your module's initialize()
async initialize() {
    await super.initialize();
    
    // Apply module-specific color theme
    const container = document.querySelector(`[data-module="${this.moduleId}"]`);
    container.style.setProperty('--color-primary', '#f59e0b');  // Orange
    container.style.setProperty('--color-primary-hover', '#d97706');
    
    this.buildUI();
}
```

### **Pattern 2: Custom Component Variants**

```javascript
// Extend existing components
const myCustomCard = UIComponents.Card.metric({
    label: "Custom Metric",
    value: "1,234",
    icon: "fa fa-star",
    color: "warning"  // Uses predefined colors
});

// OR create fully custom
const customCard = document.createElement('div');
customCard.className = 'ui-card my-custom-card';
customCard.innerHTML = `
    <div class="custom-header">My Custom Design</div>
    <div class="custom-content">Fully custom content</div>
`;
```

### **Pattern 3: Responsive Layouts**

```javascript
// Use grid that automatically adapts
const grid = UIComponents.Layout.grid({
    columns: 4,  // 4 cols on desktop
    gap: 4
});

// Add CSS in your module stylesheet
// .module-mymodule .ui-grid {
//     grid-template-columns: repeat(4, 1fr);  /* Desktop */
// }
// 
// @media (max-width: 1200px) {
//     .module-mymodule .ui-grid {
//         grid-template-columns: repeat(2, 1fr);  /* Tablet */
//     }
// }
//
// @media (max-width: 768px) {
//     .module-mymodule .ui-grid {
//         grid-template-columns: 1fr;  /* Mobile */
//     }
// }
```

---

## 📊 BEFORE & AFTER COMPARISON

### **BEFORE (Current System):**

```javascript
// Every module does this differently
buildDashboard() {
    const card = document.createElement('div');
    card.className = 'metric-card';  // Maybe different class names
    card.style.background = '#1a1a1a';  // Hard-coded values
    card.style.border = '1px solid #333';
    card.style.padding = '16px';
    card.innerHTML = `
        <div style="font-size: 14px; color: #999;">Total Sales</div>
        <div style="font-size: 24px; color: #fff;">$45,231</div>
    `;
    // Repeated 100 times across modules...
}
```

### **AFTER (Component System):**

```javascript
// Consistent, reusable, maintainable
buildDashboard() {
    const card = UIComponents.Card.metric({
        label: "Total Sales",
        value: "$45,231",
        change: {value: "+12%", trend: "up"},
        icon: "fa-dollar-sign",
        color: "success"
    });
    // Done! Professional, consistent, tested.
}
```

---

## ✅ BENEFITS SUMMARY

| Aspect | Before | After |
|--------|--------|-------|
| **Development Time** | 2-3 hours per module | 30-45 minutes per module |
| **Code Duplication** | High (copy-paste everywhere) | Zero (import components) |
| **Consistency** | Poor (each module different) | Perfect (same components) |
| **Maintenance** | Update each module manually | Update component library once |
| **Learning Curve** | Steep (learn each module) | Easy (learn components once) |
| **Customization** | Easy but inconsistent | Easy AND consistent |
| **Testing** | Test each module separately | Test components once |
| **Performance** | Varies by module | Optimized in components |
| **Accessibility** | Inconsistent | Built-in to components |
| **Responsiveness** | Manual per module | Built-in to components |

---

## 🚀 IMPLEMENTATION ROADMAP

### **Phase 1: Foundation (Week 1)**
- [x] Create `design-tokens.css` with all variables
- [x] Create utility classes
- [ ] Test on 1-2 existing modules

### **Phase 2: Core Components (Week 2)**
- [ ] Implement Card component (metric + section variants)
- [ ] Implement Button component (all variants)
- [ ] Implement Tabs component
- [ ] Test and refine

### **Phase 3: Form Components (Week 3)**
- [ ] Implement Input component
- [ ] Implement Select component
- [ ] Implement Checkbox/Radio components
- [ ] Form validation helpers

### **Phase 4: Advanced Components (Week 4)**
- [ ] Toast notifications
- [ ] Modal dialogs
- [ ] Table wrapper (Tabulator integration)
- [ ] Layout helpers

### **Phase 5: Migration (Week 5-6)**
- [ ] Migrate Quote Calculator module
- [ ] Migrate Stock Management module
- [ ] Migrate Communication Hub module
- [ ] Document patterns and lessons learned

### **Phase 6: Documentation (Week 7)**
- [ ] Create component showcase page
- [ ] Write usage examples
- [ ] Create video tutorials
- [ ] Developer onboarding guide

---

## 📚 NEXT STEPS

**To get started RIGHT NOW:**

1. **Copy design-tokens.css** to `UI/css/design-tokens.css`
2. **Copy ui-components.js** to `UI/js/ui-components.js`
3. **Copy ui-components.css** to `UI/css/ui-components.css`
4. **Add to your HTML:**
   ```html
   <link rel="stylesheet" href="css/design-tokens.css">
   <link rel="stylesheet" href="css/ui-components.css">
   <script src="js/ui-components.js"></script>
   ```
5. **Test in one module** - Start with Quote Calculator or Stock Management
6. **Build new module** using ONLY components - see how fast you can go!

**Questions to answer:**
- Which module should we migrate first as proof-of-concept?
- Do you want additional components (charts, timelines, kanban boards)?
- Should we create a visual component showcase/sandbox?

---

**Created:** November 11, 2025  
**Status:** Design Specification - Ready for Implementation  
**Next Action:** Choose first module for proof-of-concept migration

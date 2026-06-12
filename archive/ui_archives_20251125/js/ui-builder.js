/**
 * UI COMPONENT BUILDER - JavaScript Helper
 * Version: 1.0.0
 * Date: November 7, 2025
 * 
 * PURPOSE:
 * Dynamic creation of standardized UI components
 * Ensures consistency across all modules
 * 
 * DEPENDENCIES:
 * - ui-standards.css (standardized styles)
 * 
 * EXPORTS:
 * - UIBuilder class (window.UIBuilder singleton)
 * 
 * USAGE:
 * const card = UIBuilder.createMetricCard({...});
 * container.appendChild(card);
 */

class UIBuilder {
    /**
     * Create a standardized metric/stat card
     * 
     * @param {Object} options - Card configuration
     * @param {string} options.label - Card label (e.g., "Total Sales")
     * @param {string|number} options.value - Main value to display
     * @param {string} [options.icon] - FontAwesome icon class (e.g., "fa-chart-line")
     * @param {Object} [options.change] - Change indicator {value: "+12%", positive: true}
     * @param {string} [options.footer] - Footer text (e.g., "Last 30 days")
     * @param {string} [options.accentColor] - Accent color: "primary"|"success"|"error"|"warning"|"info"
     * @param {Function} [options.onClick] - Click handler
     * @returns {HTMLElement} Metric card element
     */
    static createMetricCard(options) {
        const {
            label,
            value,
            icon = null,
            change = null,
            footer = null,
            accentColor = null,
            onClick = null
        } = options;

        const card = document.createElement('div');
        card.className = 'metric-card';
        if (accentColor) {
            card.classList.add(`accent-${accentColor}`);
        }
        if (onClick) {
            card.style.cursor = 'pointer';
            card.addEventListener('click', onClick);
        }

        // Header
        const header = document.createElement('div');
        header.className = 'metric-card-header';

        if (icon) {
            const iconEl = document.createElement('i');
            iconEl.className = `${icon} metric-card-icon`;
            header.appendChild(iconEl);
        }

        const labelEl = document.createElement('div');
        labelEl.className = 'metric-card-label';
        labelEl.textContent = label;
        header.appendChild(labelEl);

        card.appendChild(header);

        // Value
        const valueEl = document.createElement('div');
        valueEl.className = 'metric-card-value';
        valueEl.textContent = value;
        card.appendChild(valueEl);

        // Change indicator
        if (change) {
            const changeEl = document.createElement('div');
            changeEl.className = 'metric-card-change';
            if (change.positive) changeEl.classList.add('positive');
            else if (change.positive === false) changeEl.classList.add('negative');
            else changeEl.classList.add('neutral');

            const arrow = change.positive ? '↑' : (change.positive === false ? '↓' : '→');
            changeEl.innerHTML = `<span>${arrow}</span><span>${change.value}</span>`;
            card.appendChild(changeEl);
        }

        // Footer
        if (footer) {
            const footerEl = document.createElement('div');
            footerEl.className = 'metric-card-footer';
            footerEl.textContent = footer;
            card.appendChild(footerEl);
        }

        return card;
    }

    /**
     * Create a standardized dashboard card with header
     * 
     * @param {Object} options - Card configuration
     * @param {string} options.title - Card title
     * @param {string} [options.icon] - FontAwesome icon class
     * @param {HTMLElement|string} [options.content] - Card body content
     * @param {Array<Object>} [options.actions] - Header actions [{label, icon, onClick}]
     * @param {HTMLElement|string} [options.footer] - Footer content
     * @returns {HTMLElement} Dashboard card element
     */
    static createDashboardCard(options) {
        const {
            title,
            icon = null,
            content = null,
            actions = [],
            footer = null
        } = options;

        const card = document.createElement('div');
        card.className = 'dashboard-card';

        // Header
        const header = document.createElement('div');
        header.className = 'dashboard-card-header';

        const titleContainer = document.createElement('div');
        titleContainer.className = 'dashboard-card-title';

        if (icon) {
            const iconEl = document.createElement('i');
            iconEl.className = `${icon} dashboard-card-icon`;
            titleContainer.appendChild(iconEl);
        }

        const titleText = document.createElement('span');
        titleText.textContent = title;
        titleContainer.appendChild(titleText);

        header.appendChild(titleContainer);

        // Actions
        if (actions.length > 0) {
            const actionsContainer = document.createElement('div');
            actionsContainer.className = 'dashboard-card-actions';

            actions.forEach(action => {
                const btn = document.createElement('button');
                btn.className = action.className || 'btn btn-sm btn-ghost';
                if (action.icon) {
                    const icon = document.createElement('i');
                    icon.className = action.icon;
                    btn.appendChild(icon);
                }
                if (action.label) {
                    const label = document.createElement('span');
                    label.textContent = action.label;
                    btn.appendChild(label);
                }
                if (action.onClick) {
                    btn.addEventListener('click', action.onClick);
                }
                actionsContainer.appendChild(btn);
            });

            header.appendChild(actionsContainer);
        }

        card.appendChild(header);

        // Body
        if (content) {
            const body = document.createElement('div');
            body.className = 'dashboard-card-body';
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
            footerEl.className = 'dashboard-card-footer';
            if (typeof footer === 'string') {
                footerEl.innerHTML = footer;
            } else {
                footerEl.appendChild(footer);
            }
            card.appendChild(footerEl);
        }

        return card;
    }

    /**
     * Create standardized subtab navigation
     * 
     * @param {Object} options - Subtab configuration
     * @param {Array<Object>} options.tabs - Tabs [{id, label, icon, onClick}]
     * @param {string} [options.activeTab] - ID of active tab
     * @returns {HTMLElement} Subtab container
     */
    static createSubtabs(options) {
        const { tabs, activeTab = null } = options;

        const container = document.createElement('div');
        container.className = 'subtab-container';

        tabs.forEach(tab => {
            const btn = document.createElement('button');
            btn.className = 'subtab-btn';
            btn.dataset.tabId = tab.id;

            if (tab.id === activeTab) {
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

            if (tab.onClick) {
                btn.addEventListener('click', (e) => {
                    // Remove active from all tabs
                    container.querySelectorAll('.subtab-btn').forEach(b => b.classList.remove('active'));
                    // Add active to clicked tab
                    btn.classList.add('active');
                    // Call handler
                    tab.onClick(e, tab.id);
                });
            }

            container.appendChild(btn);
        });

        return container;
    }

    /**
     * Create standardized section header
     * 
     * @param {Object} options - Header configuration
     * @param {string} options.title - Section title
     * @param {string} [options.subtitle] - Section subtitle/description
     * @param {Array<Object>} [options.badges] - Badges [{text, type: "primary"|"success"|"secondary"}]
     * @param {string} [options.icon] - FontAwesome icon class
     * @returns {HTMLElement} Section header element
     */
    static createSectionHeader(options) {
        const {
            title,
            subtitle = null,
            badges = [],
            icon = null
        } = options;

        const header = document.createElement('div');
        header.className = 'section-header';

        // Title
        const titleEl = document.createElement('h2');
        titleEl.className = 'section-title';

        if (icon) {
            const iconEl = document.createElement('i');
            iconEl.className = icon;
            titleEl.appendChild(iconEl);
        }

        const titleText = document.createElement('span');
        titleText.textContent = title;
        titleEl.appendChild(titleText);

        header.appendChild(titleEl);

        // Subtitle
        if (subtitle) {
            const subtitleEl = document.createElement('p');
            subtitleEl.className = 'section-subtitle';
            subtitleEl.textContent = subtitle;
            header.appendChild(subtitleEl);
        }

        // Badges
        if (badges.length > 0) {
            const meta = document.createElement('div');
            meta.className = 'section-meta';

            badges.forEach(badge => {
                const badgeEl = document.createElement('span');
                badgeEl.className = `section-badge badge-${badge.type || 'secondary'}`;
                badgeEl.textContent = badge.text;
                meta.appendChild(badgeEl);
            });

            header.appendChild(meta);
        }

        return header;
    }

    /**
     * Create standardized filter row
     * 
     * @param {Object} options - Filter configuration
     * @param {Array<Object>} options.filters - Filters [{id, label, icon, active, onClick}]
     * @returns {HTMLElement} Filter row element
     */
    static createFilterRow(options) {
        const { filters } = options;

        const row = document.createElement('div');
        row.className = 'filter-row';

        filters.forEach(filter => {
            const btn = document.createElement('button');
            btn.className = 'filter-btn';
            btn.dataset.filterId = filter.id;

            if (filter.active) {
                btn.classList.add('active');
            }

            if (filter.icon) {
                const icon = document.createElement('i');
                icon.className = filter.icon;
                btn.appendChild(icon);
            }

            const label = document.createElement('span');
            label.textContent = filter.label;
            btn.appendChild(label);

            if (filter.onClick) {
                btn.addEventListener('click', (e) => {
                    filter.onClick(e, filter.id, btn);
                });
            }

            row.appendChild(btn);
        });

        return row;
    }

    /**
     * Create standardized button
     * 
     * @param {Object} options - Button configuration
     * @param {string} options.label - Button text
     * @param {string} [options.type] - "primary"|"secondary"|"success"|"danger"|"warning"|"info"|"ghost"
     * @param {string} [options.size] - "sm"|"lg"
     * @param {string} [options.icon] - FontAwesome icon class
     * @param {Function} [options.onClick] - Click handler
     * @param {boolean} [options.disabled] - Disabled state
     * @returns {HTMLElement} Button element
     */
    static createButton(options) {
        const {
            label,
            type = 'primary',
            size = null,
            icon = null,
            onClick = null,
            disabled = false
        } = options;

        const btn = document.createElement('button');
        btn.className = `btn btn-${type}`;
        if (size) btn.classList.add(`btn-${size}`);
        if (disabled) btn.disabled = true;

        if (icon) {
            const iconEl = document.createElement('i');
            iconEl.className = icon;
            btn.appendChild(iconEl);
        }

        const labelEl = document.createElement('span');
        labelEl.textContent = label;
        btn.appendChild(labelEl);

        if (onClick) {
            btn.addEventListener('click', onClick);
        }

        return btn;
    }

    /**
     * Create standardized expandable section
     * 
     * @param {Object} options - Expander configuration
     * @param {string} options.title - Expander title
     * @param {HTMLElement|string} options.content - Content to show/hide
     * @param {boolean} [options.expanded] - Initial state
     * @param {string} [options.icon] - FontAwesome icon class
     * @returns {HTMLElement} Expander element
     */
    static createExpander(options) {
        const {
            title,
            content,
            expanded = false,
            icon = null
        } = options;

        const expander = document.createElement('div');
        expander.className = 'expander';
        if (expanded) expander.classList.add('expanded');

        // Header
        const header = document.createElement('div');
        header.className = 'expander-header';

        const titleContainer = document.createElement('div');
        titleContainer.className = 'expander-title';

        if (icon) {
            const iconEl = document.createElement('i');
            iconEl.className = icon;
            titleContainer.appendChild(iconEl);
        }

        const titleText = document.createElement('span');
        titleText.textContent = title;
        titleContainer.appendChild(titleText);

        header.appendChild(titleContainer);

        // Icon
        const expandIcon = document.createElement('i');
        expandIcon.className = 'fas fa-chevron-down expander-icon';
        header.appendChild(expandIcon);

        expander.appendChild(header);

        // Content
        const contentContainer = document.createElement('div');
        contentContainer.className = 'expander-content';
        if (typeof content === 'string') {
            contentContainer.innerHTML = content;
        } else {
            contentContainer.appendChild(content);
        }
        expander.appendChild(contentContainer);

        // Toggle handler
        header.addEventListener('click', () => {
            expander.classList.toggle('expanded');
        });

        return expander;
    }

    /**
     * Create standardized form group (label + input)
     * 
     * @param {Object} options - Form group configuration
     * @param {string} options.label - Input label
     * @param {string} options.type - "text"|"email"|"password"|"number"|"select"|"textarea"
     * @param {string} [options.id] - Input ID
     * @param {string} [options.placeholder] - Placeholder text
     * @param {*} [options.value] - Initial value
     * @param {boolean} [options.required] - Required field
     * @param {Array<Object>} [options.options] - Select options [{value, text}]
     * @returns {HTMLElement} Form group element
     */
    static createFormGroup(options) {
        const {
            label,
            type,
            id = `input-${Date.now()}`,
            placeholder = '',
            value = '',
            required = false,
            options = []
        } = options;

        const group = document.createElement('div');
        group.className = 'form-group';

        // Label
        const labelEl = document.createElement('label');
        labelEl.className = 'form-label';
        labelEl.htmlFor = id;
        labelEl.textContent = label;
        if (required) {
            const asterisk = document.createElement('span');
            asterisk.style.color = 'var(--error-color)';
            asterisk.textContent = ' *';
            labelEl.appendChild(asterisk);
        }
        group.appendChild(labelEl);

        // Input
        let input;
        if (type === 'textarea') {
            input = document.createElement('textarea');
            input.className = 'form-textarea';
        } else if (type === 'select') {
            input = document.createElement('select');
            input.className = 'form-select';
            options.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt.value;
                option.textContent = opt.text;
                input.appendChild(option);
            });
        } else {
            input = document.createElement('input');
            input.type = type;
            input.className = 'form-input';
        }

        input.id = id;
        input.placeholder = placeholder;
        if (value) input.value = value;
        if (required) input.required = true;

        group.appendChild(input);

        return group;
    }

    /**
     * Create metrics grid container
     * 
     * @param {Array<Object>} metrics - Array of metric card options
     * @returns {HTMLElement} Grid container with metric cards
     */
    static createMetricsGrid(metrics) {
        const grid = document.createElement('div');
        grid.className = 'metrics-grid';

        metrics.forEach(metric => {
            const card = this.createMetricCard(metric);
            grid.appendChild(card);
        });

        return grid;
    }

    /**
     * Create control row with buttons/filters
     * 
     * @param {Object} options - Control row configuration
     * @param {Array<HTMLElement>} options.items - Array of elements to add
     * @param {boolean} [options.spaceBetween] - Use space-between layout
     * @returns {HTMLElement} Control row element
     */
    static createControlRow(options) {
        const { items, spaceBetween = false } = options;

        const row = document.createElement('div');
        row.className = 'control-row';
        if (spaceBetween) row.classList.add('space-between');

        items.forEach(item => row.appendChild(item));

        return row;
    }
}

// Export to window for global access
if (typeof window !== 'undefined') {
    window.UIBuilder = UIBuilder;
}

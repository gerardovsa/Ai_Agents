# Settings Sidebar Module

**Version:** 2.0.0  
**Status:** Production Ready  
**Last Updated:** November 23, 2025

## Overview

Enhanced Settings Sidebar module providing comprehensive error recovery configuration, error tracking analytics, display preferences, and advanced system settings.

## Features

### 1. Error Recovery Configuration
- Master enable/disable toggle for auto-recovery system
- Granular controls for recovery types:
  - Tool Use Mismatch
  - Invalid Message Structure
  - Context Length Exceeded
  - Rate Limit Exceeded
  - Network Errors
- Configurable max retry attempts (1-5)
- Notification and logging preferences
- Real-time statistics dashboard

### 2. Error Tracking & Analytics (NEW)
- Detailed error type statistics with success rates
- Recovery timeline visualization
- Comprehensive error logs (last 100 entries)
- Effectiveness metrics by error type
- Overall system effectiveness dashboard

### 3. Display Preferences
- Show/hide thinking process
- Show/hide tool execution details
- Auto-scroll to bottom toggle

### 4. Advanced Settings
- Debug mode toggle
- API response caching
- Settings import/export
- Complete reset functionality

## Architecture

### Module Structure
```
settings-sidebar/
├── manifest.json          # Module configuration
├── settings-sidebar.js    # Main module class (extends BaseModule)
├── settings-sidebar.css   # Enhanced styles with error tracking UI
└── README.md             # This file
```

### Class Hierarchy
```
BaseModule (from module-base.js)
    ↓
SettingsSidebarModule (extends BaseModule)
    ├── settingsManager (internal utility)
    ├── errorLogManager (internal utility)
    └── Public API methods (backward compatible)
```

## Data Storage

### Settings (localStorage: 'aiAgentSettings')
```javascript
{
  autoRecovery: {
    enabled: true,
    toolMismatch: true,
    invalidStructure: true,
    contextLength: true,
    rateLimit: true,
    network: true,
    maxRetries: 3,
    showNotifications: true,
    detailedLogging: true
  },
  display: {
    showThinking: true,
    showToolDetails: true,
    autoScroll: true
  },
  advanced: {
    debugMode: false,
    cacheResponses: true
  },
  statistics: {
    totalRecoveries: 0,
    successfulRecoveries: 0,
    failedRecoveries: 0,
    lastRecovery: null,
    byErrorType: {
      tool_use_mismatch: { total: 0, successful: 0, failed: 0 },
      invalid_message_structure: { total: 0, successful: 0, failed: 0 },
      context_length_exceeded: { total: 0, successful: 0, failed: 0 },
      rate_limit_exceeded: { total: 0, successful: 0, failed: 0 },
      network_error: { total: 0, successful: 0, failed: 0 }
    }
  }
}
```

### Error Logs (localStorage: 'aiAgentErrorLogs')
```javascript
[
  {
    timestamp: "2025-11-23T10:30:00.000Z",
    errorType: "tool_use_mismatch",
    errorMessage: "tool_result without matching tool_use",
    recovered: true,
    attemptNumber: 2,
    threadId: "thread_abc123"
  },
  // ... up to 100 most recent logs
]
```

## Public API

### Module Instance
```javascript
window.settingsModule // Global module instance
```

### Methods

#### Error Recovery
```javascript
// Check if error recovery is enabled
window.settingsModule.isErrorRecoveryEnabled(errorType)
// Returns: boolean

// Get max retry attempts
window.settingsModule.getMaxRetryAttempts()
// Returns: number (1-5)

// Check if notifications should be shown
window.settingsModule.shouldShowRecoveryNotifications()
// Returns: boolean

// Check if detailed logging is enabled
window.settingsModule.isDetailedLoggingEnabled()
// Returns: boolean
```

#### Error Tracking
```javascript
// Record a recovery attempt
window.settingsModule.recordRecovery(errorType, success)
// errorType: string (e.g., 'tool_use_mismatch')
// success: boolean

// Log an error with details
window.settingsModule.logError(errorType, errorMessage, recovered, attemptNumber, threadId)
```

#### Tab Navigation
```javascript
// Switch to a specific tab
window.settingsModule.switchSubTab('recovery')   // Error recovery
window.settingsModule.switchSubTab('tracking')   // Error tracking
window.settingsModule.switchSubTab('display')    // Display preferences
window.settingsModule.switchSubTab('advanced')   // Advanced settings
```

## Backward Compatibility

### Deprecated Global Functions (v1.x - Temporary Support)
```javascript
// These still work but will be removed in v3.0
window.isErrorRecoveryEnabled(type)
window.getMaxRetryAttempts()
window.shouldShowRecoveryNotifications()
window.isDetailedLoggingEnabled()

// Migrate to:
window.settingsModule.isErrorRecoveryEnabled(type)
window.settingsModule.getMaxRetryAttempts()
// etc.
```

## Integration with Error Recovery System

### Example: Check Before Recovery
```javascript
// In error-recovery.js or agent-routes.py equivalent

if (window.settingsModule?.isErrorRecoveryEnabled('tool_use_mismatch')) {
    const maxRetries = window.settingsModule.getMaxRetryAttempts();
    
    // Attempt recovery
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            // Recovery logic here
            const result = await attemptRecovery();
            
            // Log success
            window.settingsModule.recordRecovery('tool_use_mismatch', true);
            window.settingsModule.logError(
                'tool_use_mismatch',
                'Recovered successfully',
                true,
                attempt,
                threadId
            );
            
            if (window.settingsModule.shouldShowRecoveryNotifications()) {
                showToast('Error recovered successfully', 'success');
            }
            
            break;
        } catch (error) {
            if (attempt === maxRetries) {
                // Log failure
                window.settingsModule.recordRecovery('tool_use_mismatch', false);
                window.settingsModule.logError(
                    'tool_use_mismatch',
                    error.message,
                    false,
                    attempt,
                    threadId
                );
            }
        }
    }
}
```

## UI Components

### Statistics Dashboard
- Total recoveries
- Successful recoveries
- Failed recoveries
- Success rate percentage
- Last recovery timestamp

### Error Type Statistics
- Visual bar charts showing success/failure ratio per error type
- Total attempts, successful, and failed counts
- Color-coded success rates (green: >80%, yellow: >50%, red: <50%)

### Recovery Timeline
- Chronological list of recent recovery attempts
- Status icons (check/x)
- Error type, message, timestamp
- Attempt number and thread ID

### Error Logs Table
- Searchable/filterable table of all logged errors
- Columns: Time, Type, Message, Status, Attempt, Thread
- Color-coded rows (green: recovered, red: failed)

### Effectiveness Metrics
- Overall effectiveness percentage
- Per-error-type effectiveness cards
- Visual status indicators (excellent/good/fair/poor)

## Styling

### Module Colors
```css
--module-settings-primary: #8b5cf6 (Purple)
--module-settings-secondary: #7c3aed
--module-settings-hover: #6d28d9
```

### Component Classes
- `.settings-section` - Main section container
- `.setting-item` - Individual setting row
- `.toggle-switch` - Custom toggle component
- `.stat-card` - Statistics card
- `.error-type-stat` - Error type statistics
- `.timeline-item` - Timeline entry
- `.error-logs-table` - Error logs table
- `.effectiveness-card` - Effectiveness metric card

## Testing

### Manual Test Checklist
- [ ] Module loads on page start
- [ ] All 4 tabs render correctly
- [ ] Settings persist to localStorage
- [ ] Toggle switches work
- [ ] Statistics update after recordRecovery()
- [ ] Error logs display correctly
- [ ] Timeline shows recent errors
- [ ] Effectiveness metrics calculate correctly
- [ ] Export/import settings works
- [ ] Reset functions work with confirmation

### Integration Test Checklist
- [ ] Error recovery system respects settings
- [ ] Recovery attempts update statistics
- [ ] Error logs populate automatically
- [ ] Notifications appear when enabled
- [ ] Debug mode affects console output
- [ ] Backward compatibility functions work

## Migration from v1.x

### Breaking Changes
1. Global functions deprecated (use `window.settingsModule` instead)
2. HTML no longer needs to be embedded (auto-loaded)
3. Path changed: `UI/modules/settings-sidebar` → `UI/external/modules/settings-sidebar`

### Migration Steps
1. Remove old script tag from `business-ai-platform-v2.html`
2. Remove old HTML template inclusion
3. Update function calls: `window.fnName()` → `window.settingsModule.fnName()`
4. Module auto-loads via `ModuleLoader`

## Future Enhancements

### Planned for v2.1
- [ ] Backend storage (Supabase PostgreSQL)
- [ ] Settings sync across devices
- [ ] Advanced filtering in error logs
- [ ] Export error logs as CSV
- [ ] Graphical charts for effectiveness over time
- [ ] User preferences per thread

### Planned for v3.0
- [ ] Remove backward compatibility wrappers
- [ ] Add settings versioning/migration system
- [ ] Role-based settings access
- [ ] Settings presets (default, debugging, production)

## Dependencies

- `UI/js/module-base.js` (BaseModule)
- `UI/js/module-manager.js` (ModuleManager)
- `UI/js/module-loader.js` (ModuleLoader)
- Font Awesome icons
- localStorage API

## Browser Compatibility

- Chrome: ✅ 90+
- Firefox: ✅ 88+
- Safari: ✅ 14+
- Edge: ✅ 90+

## License

Internal use only - InHouse Print AI Agent Platform

## Changelog

### v2.0.0 (2025-11-23)
- Complete refactor to proper module structure
- Extended BaseModule for consistency
- Added Error Tracking tab with analytics
- Added Recovery Timeline visualization
- Added Effectiveness Metrics dashboard
- Enhanced statistics by error type
- Added error log management (last 100 entries)
- Added settings import/export
- Improved UI with module colors
- Added backward compatibility wrappers
- Registered in module manifest

### v1.2.0 (2025-11-XX)
- Added v2 with dynamic HTML loading
- Added toast notifications
- Added tooltips for settings

### v1.0.0 (Initial)
- Basic error recovery settings
- Display preferences
- Advanced settings
- Statistics dashboard

## Support

For issues or feature requests, contact the AI Agent Platform team.

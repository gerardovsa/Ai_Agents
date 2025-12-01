# Universal Search Module

**Version:** 1.0.0  
**Framework:** Modern Framework V4 (ES6 Composition)  
**Type:** Internal Module  
**Category:** Search

## Overview

Universal Search provides a unified search interface across all connected platforms and data sources. Search documents, threads, messages, Synergy sessions, Gmail, Slack, and more from a single search box.

## Features

- **Multi-Platform Search**: Search across all connected platforms simultaneously
- **Real-Time Results**: Debounced search with instant feedback
- **Faceted Filters**: Filter by source, date, type, and relevance
- **Result Grouping**: Results organized by source with expandable sections
- **Semantic Search**: AI-powered semantic search capabilities
- **Search History**: Recently searched queries with quick access

## Architecture

**Pattern:** Modern Framework V4 (ES6 Composition)

### File Structure
```
universal-search/
├── manifest.json                 # Module configuration (V3.0)
├── universal-search.js          # Main module (ES6 export default)
├── universal-search.css         # Styles
├── universal-search.html        # Container template
├── universal-search.legacy.js   # Legacy version (archived)
└── README.md                    # This file
```

### Lifecycle Hooks

- **onLoad(utilities)**: Initialize module, load available sources, register in ModuleRegistry
- **onDashboardLoad(utilities)**: Render full search interface in main dashboard
- **onSidebarLoad(utilities)**: Render compact search in sidebar
- **onUnload()**: Cleanup event listeners and clear state

### Dependencies

- `dom` - DOM manipulation utilities
- `api` - API client for backend requests
- `storage` - LocalStorage wrapper
- `events` - Event bus for inter-module communication
- `log` - Logging utilities

## Usage

### Dashboard View

The module provides a full-featured search interface in the main dashboard:

1. Click "Universal Search" in sidebar
2. Type query in search box
3. Select sources to search (documents, threads, Gmail, etc.)
4. View results grouped by source
5. Click result to open in respective platform

### Sidebar View

Compact search interface in sidebar:

1. Double-click floating toggle to switch sides
2. Type query to search
3. View condensed results
4. Click to expand in main dashboard

## Configuration

### Manifest Settings

```json
{
  "loading": {
    "strategy": "lazy",
    "priority": 50,
    "framework": "v4"
  },
  "settings": {
    "defaultSearchType": "hybrid",
    "enableSemanticSearch": true,
    "maxResults": 50,
    "enableRealtime": true
  }
}
```

### Available Sources

- **documents**: Vector database documents
- **threads**: Conversation threads
- **messages**: Direct messages
- **synergy**: Synergy sessions and analytics
- **gmail**: Gmail emails (requires OAuth)
- **slack**: Slack messages (requires OAuth)

## API Endpoints

### Get Available Sources
```
GET /api/universal-search/sources
Response: { sources: [...] }
```

### Search
```
POST /api/universal-search/search
Body: {
  query: string,
  sources: string[],
  limit: number
}
Response: {
  results: [...],
  total: number,
  bySource: {...}
}
```

## State Management

```javascript
state: {
  query: '',              // Current search query
  results: [],            // Search results array
  loading: false,         // Loading indicator
  error: null,            // Error message
  selectedSources: Set,   // Active search sources
  availableSources: {},   // Platform availability
  searchTimeout: null,    // Debounce timer
  stats: {
    total: 0,             // Total result count
    bySource: {}          // Results per source
  }
}
```

## Development

### Testing Container ID

The module uses `getElementById('universal-search-container')` which exists in `universal-search.html`. The analyzer warning refers to the legacy file only.

### Debugging

Enable debug mode in browser console:
```javascript
window.ModuleRegistry['universal-search'].log.debug('Debug info');
```

### Hot Reload

After code changes:
1. Hard refresh: `CTRL+SHIFT+R`
2. Module auto-reloads via V4 loader
3. Check console for errors

## V4 Compliance

- ✅ **ES6 Export Default**: Proper ES6 module pattern
- ✅ **Composition Pattern**: No inheritance, uses utility injection
- ✅ **Lifecycle Hooks**: All 4 hooks implemented
- ✅ **Modern Framework**: Configured for `loading.framework = 'v4'`
- ✅ **ModuleRegistry**: Registered in `window.ModuleRegistry['universal-search']`
- ✅ **Container Management**: Proper container-scoped queries

**Compliance Score:** 100/100 (EXCELLENT)

## Performance

- **Initial Load**: < 100ms (lazy loading)
- **Search Latency**: < 500ms (debounced)
- **Average Response**: 2028ms (includes all sources)
- **Memory Footprint**: ~5MB (including cached results)

## Permissions Required

```json
[
  "documents:read",
  "threads:read",
  "messages:read",
  "synergy:read",
  "gmail:read",
  "slack:read"
]
```

## Troubleshooting

### No Results Returned

1. Check available sources: Ensure platforms are connected
2. Verify API endpoint: `/api/universal-search/search` should return 200
3. Check credentials: OAuth tokens may be expired
4. Browser console: Look for API errors

### Search Not Working

1. Clear browser cache: `CTRL+SHIFT+R`
2. Check Flask server: Ensure backend is running
3. Network tab: Verify API requests are being sent
4. Module loader: Confirm V4 loader initialized

### Container Not Found

**This error only occurs in legacy file** - production file uses proper container management.

## Migration Notes

**From Legacy to V4:**

The module was migrated from BaseModule inheritance to Modern Framework V4 composition pattern. The legacy file (`universal-search.legacy.js`) is kept for reference but not loaded by the module loader.

**Key Changes:**
- Removed class inheritance
- Changed to export default pattern
- Added lifecycle hooks
- Switched to utility composition
- Updated manifest for V4 framework

## Support

For issues or questions:
1. Check browser console for errors
2. Review Flask server logs
3. Verify module appears in `/api/modules/list`
4. Test with module analyzer: `python scripts/testing/module_analyzer.py UI/modules_internal/universal-search`

---

**Last Updated:** November 30, 2025  
**Status:** ✅ Production Ready  
**Framework:** Modern Framework V4

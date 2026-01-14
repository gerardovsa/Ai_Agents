# Synergy Sidebar Implementation Plan

## Overview
Creating a right-side collapsible sidebar that displays Synergy sessions as inline tiles (not floating windows). Users can view 2-3 sessions simultaneously in a scrollable tile view.

## Key Features
1. **Collapsible Sidebar** - Toggle open/close like thread menu
2. **Session List** - Categorized by status (Active, In Progress, Review, Done)
3. **Tile-Based Views** - Sessions expand as inline tiles within sidebar
4. **Multi-Tile Support** - View up to 3 sessions simultaneously
5. **Scrollable Container** - Scroll through multiple open tiles
6. **Edit Mode Per Tile** - Each tile has its own edit/view toggle
7. **Compact List** - Collapsed sessions shown as compact items with expand button

## HTML Structure
```
synergy-sidebar (right side, similar to ai-chat-panel left side)
├── synergy-sidebar-header (collapsible toggle button)
├── synergy-sidebar-content
│   ├── synergy-session-list (compact list view)
│   │   └── synergy-session-item × N (clickable to expand as tile)
│   └── synergy-tiles-container (expanded tiles)
│       └── synergy-tile × 1-3 (inline popup-style content)
│           ├── tile-header (title, status, collapse/edit buttons)
│           ├── tile-content (full synergy card content)
│           └── tile-footer (session info, actions)
```

## CSS Classes Needed
- `.synergy-sidebar` - Main container (position: fixed; right side)
- `.synergy-sidebar.collapsed` - Hidden state
- `.synergy-session-list` - Compact list of all sessions
- `.synergy-session-item` - Single session in list (title + status badge)
- `.synergy-tiles-container` - Container for expanded tiles (scrollable)
- `.synergy-tile` - Individual expanded session tile
- `.synergy-tile.edit-mode` - Tile in edit mode

## JavaScript Functions Needed
```javascript
// SynergySidebar object (similar to synergyBoard)
const SynergySidebar = {
    sessions: [],
    openTiles: [], // Track which sessions are open as tiles (max 3)
    
    async loadSessions() {},
    toggleSidebar() {},
    expandSessionAsTile(sessionId) {},
    closeTile(sessionId) {},
    toggleTileEdit(sessionId) {},
    saveTileEdits(sessionId) {},
    scrollToTile(sessionId) {}
};
```

## Implementation Steps
1. Add CSS for sidebar and tiles
2. Add HTML structure after ai-chat-panel
3. Implement SynergySidebar JavaScript object
4. Connect to existing synergyBoard session data
5. Add edit mode functionality for tiles
6. Test tile scrolling and multi-tile view

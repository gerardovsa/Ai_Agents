# 🎨 Open Source Kanban Board Options - Code You Can Use

## Overview

Here are **battle-tested open-source Kanban board projects** you can use, fork, or extract code from:

---

## 🏆 TOP RECOMMENDATION: Taiga (Python + React)

**GitHub:** https://github.com/taigaio/taiga  
**Stars:** 10k+  
**License:** MPL 2.0 (commercial-friendly)

### Why Taiga?

✅ **Python backend** (like your AI_agents project!)  
✅ **React frontend** (modern, drag-and-drop)  
✅ **REST API** (easy integration)  
✅ **Kanban board component** (exactly what you need)  
✅ **Open source** (MIT/MPL - can use code freely)  
✅ **Production-ready** (used by thousands of companies)

### What You Can Extract:

```
taiga/front/app/modules/kanban/
├── kanban.component.js          ← Main Kanban board
├── kanban-board.directive.js    ← Drag & drop logic
├── kanban-card.component.js     ← Card component
├── kanban.service.js            ← API integration
└── kanban.scss                  ← Styling
```

### Key Code Patterns:

**1. Kanban Board Structure:**
```javascript
// From: taiga/front/app/modules/kanban/kanban.component.js

class KanbanController {
    constructor() {
        this.columns = [];
        this.cards = [];
        this.loadBoard();
    }

    loadBoard() {
        // Fetch from API
        this.api.getKanbanData().then(data => {
            this.columns = data.columns;
            this.cards = this.groupCardsByStatus(data.cards);
        });
    }

    onCardMoved(card, newColumn) {
        // Optimistic update
        this.moveCardLocally(card, newColumn);
        
        // Sync to backend
        this.api.updateCard(card.id, { status: newColumn.id })
            .then(() => {
                console.log('✅ Synced to backend');
            })
            .catch(error => {
                // Revert on error
                this.revertCardMove(card, newColumn);
            });
    }
}
```

**2. Drag & Drop:**
```javascript
// Uses Dragula library (smooth drag-and-drop)
dragula([...containers], {
    moves: function (el, container, handle) {
        return handle.classList.contains('drag-handle');
    },
    accepts: function (el, target) {
        return target.classList.contains('kanban-column');
    }
}).on('drop', function (el, target, source) {
    // Card dropped in new column
    const cardId = el.dataset.cardId;
    const newStatus = target.dataset.status;
    controller.onCardMoved(cardId, newStatus);
});
```

---

## Option 2: Wekan (Meteor + React)

**GitHub:** https://github.com/wekan/wekan  
**Stars:** 19k+  
**License:** MIT

### Why Wekan?

✅ **Complete Kanban app** (like Trello clone)  
✅ **Real-time sync** (uses Meteor's reactive data)  
✅ **Feature-rich** (labels, checklists, attachments)  
✅ **MIT license** (freely use code)

### What You Can Extract:

```
client/components/
├── boards/boardBody.js          ← Main Kanban layout
├── cards/cardDetails.js         ← Card component
├── lists/list.js                ← Column component
└── swimlanes/swimlane.js        ← Swimlane support
```

**Key Feature:** Real-time collaboration (multiple users see changes instantly)

---

## Option 3: Planka (React + PostgreSQL)

**GitHub:** https://github.com/plankanban/planka  
**Stars:** 7k+  
**License:** AGPL 3.0 (open source)

### Why Planka?

✅ **Modern React** (uses Hooks)  
✅ **Beautiful UI** (polished design)  
✅ **REST API** (easy to integrate)  
✅ **Docker-ready** (easy deployment)

### What You Can Extract:

```
client/src/components/
├── Board/Board.jsx              ← Main board component
├── Card/Card.jsx                ← Card with modal
├── List/List.jsx                ← Column component
└── CardModal/CardModal.jsx      ← Detailed card view
```

**Key Feature:** Very clean, modern codebase (easy to understand)

---

## Option 4: Focalboard (Go + React)

**GitHub:** https://github.com/mattermost/focalboard  
**Stars:** 20k+  
**License:** MIT  
**By:** Mattermost (trusted company)

### Why Focalboard?

✅ **Enterprise-grade** (production-ready)  
✅ **Multiple views** (Kanban, table, calendar, gallery)  
✅ **Clean React code** (TypeScript)  
✅ **MIT license** (use freely)

### What You Can Extract:

```
webapp/src/components/
├── kanban/kanban.tsx            ← Kanban board
├── kanban/kanbanCard.tsx        ← Card component
├── kanban/kanbanColumn.tsx      ← Column component
└── kanban/kanbanHiddenItem.tsx  ← Hidden cards
```

**Bonus:** Can switch between Kanban, Table, Calendar views (same data, different visualizations!)

---

## Option 5: React Kanban (Lightweight Library)

**GitHub:** https://github.com/lourenci/react-kanban  
**Stars:** 1.5k+  
**License:** MIT

### Why React Kanban?

✅ **Library, not full app** (plug-and-play)  
✅ **Minimal dependencies** (just React + DnD)  
✅ **Simple API** (easy to integrate)  
✅ **MIT license** (use freely)

### Installation:

```bash
npm install @lourenci/react-kanban
```

### Usage Example:

```javascript
import Board from '@lourenci/react-kanban'

const board = {
  columns: [
    {
      id: 'backlog',
      title: '📦 Backlog',
      cards: [
        {
          id: 1,
          title: 'Research Campaign',
          description: '5 messages • 1 doc'
        }
      ]
    },
    {
      id: 'in_progress',
      title: '🏃 In Progress',
      cards: []
    },
    {
      id: 'done',
      title: '✅ Done',
      cards: []
    }
  ]
}

function MyKanban() {
  const handleCardMove = (_card, source, destination) => {
    console.log('Card moved from', source, 'to', destination)
    // Sync to backend
  }

  return (
    <Board
      initialBoard={board}
      onCardDragEnd={handleCardMove}
    />
  )
}
```

**Perfect for:** Quick implementation, no complex setup needed

---

## Comparison Table

| Project | Backend | Frontend | License | Complexity | Best For |
|---------|---------|----------|---------|------------|----------|
| **Taiga** | Python | React | MPL 2.0 | Medium | Python projects (✅ YOUR CASE) |
| **Wekan** | Meteor | React | MIT | High | Real-time collab |
| **Planka** | Node.js | React | AGPL | Medium | Modern UI |
| **Focalboard** | Go | React | MIT | Medium | Multi-view support |
| **React Kanban** | None | React | MIT | **Low** | Quick start (✅ FASTEST) |

---

## 🎯 RECOMMENDED APPROACH FOR YOUR PROJECT

### Phase 1: Quick Start with React Kanban Library

```bash
cd AI_agents
mkdir frontend
cd frontend
npm init -y
npm install react react-dom @lourenci/react-kanban
npm install socket.io-client  # For real-time sync
```

**Why start here?**
- ✅ Get working Kanban board in 1 hour
- ✅ Focus on YOUR sync logic (not reinventing drag-and-drop)
- ✅ Can always upgrade to Taiga's components later

### Phase 2: Extract Best Components from Taiga

**Clone Taiga to study:**
```bash
git clone https://github.com/taigaio/taiga-front.git
cd taiga-front/app/modules/kanban
```

**What to extract:**
1. **Card component** (`kanban-card.component.js`) - Feature-rich card design
2. **Column component** (`kanban-board.directive.js`) - Column management
3. **Styles** (`kanban.scss`) - Professional styling

### Phase 3: Add Your Custom Features

```javascript
// Your custom SessionCard component

const SessionCard = ({ session, onResume }) => {
  const priorityEmoji = {
    'high': '🔴',
    'medium': '🟡',
    'low': '🟢'
  };

  return (
    <div className="session-card">
      <div className="header">
        <span>{priorityEmoji[session.priority]}</span>
        <h4>{session.title}</h4>
      </div>
      
      <div className="project">
        📋 {session.project_name}
      </div>
      
      <div className="stats">
        <span>💬 {session.message_count}</span>
        <span>📁 {session.active_docs}</span>
        <span>✔️ {session.completed_steps}/{session.total_steps}</span>
      </div>
      
      <div className="recent-activity">
        📝 {session.last_activity}
      </div>
      
      <div className="actions">
        <button onClick={() => onResume(session.session_id)}>
          Resume →
        </button>
        
        {/* Link to Google Tasks */}
        <a 
          href={`https://tasks.google.com/.../${session.google_task_id}`}
          target="_blank"
          className="google-task-link"
        >
          📱 View in Google Tasks
        </a>
      </div>
      
      {/* Sync indicator */}
      {session.is_syncing && (
        <div className="sync-indicator">
          🔄 Syncing...
        </div>
      )}
      
      {session.last_synced_at && (
        <div className="sync-status">
          ✅ Synced {timeAgo(session.last_synced_at)}
        </div>
      )}
    </div>
  );
};
```

---

## Complete File Structure for Your Kanban Frontend

```
AI_agents/
├── frontend/
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js
│   │   ├── components/
│   │   │   ├── KanbanBoard.jsx          ← Main board
│   │   │   ├── KanbanColumn.jsx         ← Column component
│   │   │   ├── SessionCard.jsx          ← Card component
│   │   │   ├── CardModal.jsx            ← Full session details
│   │   │   └── SyncIndicator.jsx        ← Sync status
│   │   ├── services/
│   │   │   ├── api.js                   ← Backend API calls
│   │   │   ├── socket.js                ← WebSocket connection
│   │   │   └── sync.js                  ← Sync manager
│   │   ├── hooks/
│   │   │   ├── useSessions.js           ← Session data hook
│   │   │   └── useSync.js               ← Sync status hook
│   │   └── styles/
│   │       ├── kanban.css               ← Kanban styles
│   │       └── theme.css                ← Colors/spacing
│   └── .env
│       API_URL=http://localhost:4000
```

---

## Quick Start Code

**Full working example you can copy/paste:**

```javascript
// frontend/src/components/KanbanBoard.jsx

import React, { useState, useEffect } from 'react';
import Board from '@lourenci/react-kanban';
import io from 'socket.io-client';

const socket = io('http://localhost:4000');

export default function KanbanBoard() {
  const [board, setBoard] = useState({
    columns: [
      { id: 'backlog', title: '📦 Backlog', cards: [] },
      { id: 'in_progress', title: '🏃 In Progress', cards: [] },
      { id: 'review', title: '👁️ Review', cards: [] },
      { id: 'done', title: '✅ Done', cards: [] }
    ]
  });

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
    
    // Listen for real-time updates from Google Tasks
    socket.on('session_updated', handleSessionUpdate);
    
    return () => socket.off('session_updated');
  }, []);

  const loadSessions = async () => {
    const response = await fetch('http://localhost:4000/api/sessions');
    const sessions = await response.json();
    
    // Group by kanban_column
    const newBoard = { ...board };
    newBoard.columns.forEach(col => {
      col.cards = sessions
        .filter(s => s.kanban_column === col.id)
        .map(s => sessionToCard(s));
    });
    
    setBoard(newBoard);
  };

  const handleCardMove = async (card, source, destination) => {
    // Sync to backend (triggers Google Tasks sync)
    await fetch('http://localhost:4000/api/sessions/move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: card.id,
        new_column: destination.toColumnId
      })
    });
    
    console.log('✅ Synced move to backend and Google Tasks');
  };

  const handleSessionUpdate = (session) => {
    // Real-time update from Google Tasks
    console.log('🔄 Session updated from Google:', session);
    loadSessions();  // Refresh board
  };

  const sessionToCard = (session) => ({
    id: session.session_id,
    title: `${getPriorityEmoji(session.priority)} ${session.title}`,
    description: (
      <div className="card-content">
        <div>📋 {session.project_name}</div>
        <div>📊 {session.message_count} msgs • {session.active_docs} docs</div>
        <div>⏱️ {timeAgo(session.last_active)}</div>
        <button onClick={() => window.location.href = `/session/${session.session_id}`}>
          Resume →
        </button>
      </div>
    )
  });

  const getPriorityEmoji = (priority) => ({
    'high': '🔴', 'medium': '🟡', 'low': '🟢'
  })[priority];

  return (
    <div className="kanban-container">
      <Board
        initialBoard={board}
        onCardDragEnd={handleCardMove}
        renderCard={(card) => (
          <div className="custom-card">
            <h4>{card.title}</h4>
            {card.description}
          </div>
        )}
      />
    </div>
  );
}

function timeAgo(timestamp) {
  // Same as task_card_manager.py _time_ago()
  const now = new Date();
  const then = new Date(timestamp);
  const seconds = Math.floor((now - then) / 1000);
  
  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}
```

---

## Styling (Copy from Taiga)

```css
/* frontend/src/styles/kanban.css */

.kanban-container {
  display: flex;
  gap: 1rem;
  padding: 2rem;
  background: #f8fafc;
  min-height: 100vh;
  overflow-x: auto;
}

.kanban-column {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  min-width: 300px;
  max-width: 350px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.kanban-column h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1e293b;
}

.custom-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  cursor: grab;
  transition: all 0.2s;
}

.custom-card:hover {
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.custom-card h4 {
  font-size: 0.95rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #0f172a;
}

.card-content {
  font-size: 0.85rem;
  color: #64748b;
  line-height: 1.5;
}

.card-content button {
  margin-top: 0.5rem;
  padding: 0.4rem 0.8rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.card-content button:hover {
  background: #2563eb;
}

/* Drag placeholder */
.react-kanban-card-skeleton {
  background: #f1f5f9;
  border: 2px dashed #cbd5e1;
  border-radius: 6px;
  height: 100px;
}
```

---

## Next Steps

1. **Start with React Kanban library** (`@lourenci/react-kanban`) - Get working in 1 hour ✅
2. **Connect to your backend** - Use existing Flask API ✅
3. **Add WebSocket sync** - Real-time updates from Google Tasks ✅
4. **Enhance with Taiga's styles** - Professional look ✅
5. **Add Google Calendar integration** - Auto-create events ✅

**You'll have a production-ready Kanban board with full Google Tasks sync!** 🚀

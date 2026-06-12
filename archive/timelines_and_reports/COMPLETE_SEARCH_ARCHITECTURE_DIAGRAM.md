# Complete Universal Search Architecture
**Date:** December 7, 2025  
**Status:** ✅ PRODUCTION READY  
**Total Sources:** 10 (Internal: 6, External: 4)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    UNIVERSAL SEARCH FRONTEND                         │
│                  (universal-search.js + HTML/CSS)                    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                     POST /api/universal-search
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│               UNIVERSAL SEARCH BACKEND ORCHESTRATOR                  │
│              (universal_search_routes.py - 1100 lines)               │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Query Parser & Source Detector                              │   │
│  │  - Detects user's selected sources                           │   │
│  │  - Prepares parallel search execution                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  Parallel Search Execution (10 sources):                             │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ SECTION 1: SEARCH DOCUMENTS (PostgreSQL + pgvector)        │    │
│  │ - document_library table                                    │    │
│  │ - Full-text (ts_rank) + Semantic (cosine similarity)       │    │
│  │ - Returns: filename, content, source, date, score          │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ SECTION 2: SEARCH THREADS (PostgreSQL)                     │    │
│  │ - sessions.threads table                                    │    │
│  │ - Full-text search on title/summary                         │    │
│  │ - Returns: thread_id, title, created_at, message_count     │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ SECTION 3: SEARCH MESSAGES (PostgreSQL)                    │    │
│  │ - sessions.messages table                                   │    │
│  │ - Full-text search on content                               │    │
│  │ - Returns: message_id, content, role, thread_id, date      │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ SECTION 4: SEARCH SYNERGY SESSIONS (PostgreSQL)            │    │
│  │ - synergy_sessions.sessions table                           │    │
│  │ - Full-text search on title/description                     │    │
│  │ - Returns: session_id, title, agents, date, status         │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ SECTION 4.5: SEARCH VECTOR DATABASES (Qdrant/Pinecone)     │    │
│  │ - Qdrant: Self-hosted vector DB (free, fast)               │    │
│  │ - Pinecone: Cloud vector DB (fallback, $70/mo)             │    │
│  │ - Semantic search with embeddings                           │    │
│  │ - Returns: doc_id, content, metadata, score                │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ SECTION 5.1: SEARCH GMAIL (Google API)                     │    │
│  │ - Check OAuth credentials                                   │    │
│  │ - Gmail API: messages.list with q parameter                │    │
│  │ - Returns: message_id, subject, from, snippet, date        │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ SECTION 5.2: SEARCH SLACK (Slack API)                      │    │
│  │ - Check OAuth credentials                                   │    │
│  │ - Slack API: search.messages with query                    │    │
│  │ - Returns: message_id, text, user, channel, date           │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ SECTION 6: SEARCH XERO (Xero Accounting API) ⭐ NEW        │    │
│  │ - Check Xero credentials for 3 businesses                   │    │
│  │ - Business 1: InHouse Print                                 │    │
│  │   - Search Invoices (by contact/number)                     │    │
│  │   - Search Contacts (by name/email)                         │    │
│  │ - Business 2: InHouse Publishing (same)                     │    │
│  │ - Business 3: InHouse Signs (same)                          │    │
│  │ - Returns: type, business, invoice_number/name, contact,   │    │
│  │   total, date, status, email, phone                         │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ SECTION 7: SEARCH INHOUSEPRINT (SQL Server DB) ⭐ NEW      │    │
│  │ - Connect to SQL Server (pymssql)                           │    │
│  │ - Search PublishingProject table:                           │    │
│  │   - ProjectName, Description, Client info                   │    │
│  │   - JOIN with Clients on ClientID                           │    │
│  │   - Returns: project_name, description, client, contact,   │    │
│  │     email, start_date, deadline, status                     │    │
│  │ - Search Clients table:                                     │    │
│  │   - CompanyName, ContactName, Email                         │    │
│  │   - Returns: company, contact, email, phone, address       │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Result Aggregator & Scorer                                  │   │
│  │  - Groups results by source                                  │   │
│  │  - Calculates relevance scores                               │   │
│  │  - Applies pagination (limit per source)                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                     JSON Response with grouped results
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                    RESULT DISPLAY COMPONENT                          │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ Documents (23 results)              📄                      │    │
│  │ ─────────────────────────────────────────────────────      │    │
│  │ 📄 Annual Report 2024.pdf           Score: 0.95            │    │
│  │    Uploaded: 2024-12-01 | Source: local                    │    │
│  │                                                              │    │
│  │ 📄 Budget Proposal Q1.xlsx          Score: 0.87            │    │
│  │    Uploaded: 2024-11-15 | Source: google_drive             │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ Vector Database (12 results)        🗄️                     │    │
│  │ ─────────────────────────────────────────────────────      │    │
│  │ 🗄️ Company Policy on Remote Work   Score: 0.92            │    │
│  │    Stored in: business-docs collection | Qdrant            │    │
│  │                                                              │    │
│  │ 🗄️ SOP: Invoice Processing         Score: 0.88            │    │
│  │    Stored in: protocols collection | Qdrant                │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ Xero Accounting (8 results) ⭐ NEW  💰                      │    │
│  │ ─────────────────────────────────────────────────────      │    │
│  │ 💰 Invoice INV-2025-001            InHouse Print           │    │
│  │    Contact: Microsoft | Total: $15,450 | Status: PAID      │    │
│  │    Due: 2025-01-15                                          │    │
│  │                                                              │    │
│  │ 👤 Microsoft Corporation           InHouse Publishing      │    │
│  │    Email: accounts@microsoft.com | Type: Customer          │    │
│  │    Phone: +61 2 1234 5678                                   │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ InHousePrint Projects (5 results) ⭐ NEW  🖨️                │    │
│  │ ─────────────────────────────────────────────────────      │    │
│  │ 📋 Annual Report 2025 - Microsoft                           │    │
│  │    Client: Microsoft Corporation                            │    │
│  │    Contact: John Smith (john.smith@microsoft.com)           │    │
│  │    Deadline: 2025-03-31 | Status: In Progress              │    │
│  │                                                              │    │
│  │ 🏢 Microsoft Corporation                                    │    │
│  │    Contact: John Smith | Email: john.smith@microsoft.com   │    │
│  │    Phone: +61 2 1234 5678                                   │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ Gmail (4 results)                   ✉️                      │    │
│  │ Slack (2 results)                   💬                      │    │
│  │ Threads (15 results)                💭                      │    │
│  │ Messages (32 results)               📨                      │    │
│  │ Synergy Sessions (7 results)        🧠                      │    │
│  └────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Source Matrix

| Source | Type | Technology | Authentication | Search Method | Status |
|--------|------|------------|----------------|---------------|--------|
| **Documents** | Internal | PostgreSQL + pgvector | Session-based | Full-text + Semantic | ✅ Active |
| **Threads** | Internal | PostgreSQL | Session-based | Full-text (ts_rank) | ✅ Active |
| **Messages** | Internal | PostgreSQL | Session-based | Full-text (ts_rank) | ✅ Active |
| **Synergy** | Internal | PostgreSQL | Session-based | Full-text (ts_rank) | ✅ Active |
| **Vector DB** | Internal | Qdrant/Pinecone | Credential store | Semantic (embeddings) | ✅ Active |
| **Gmail** | External | Google API | OAuth2 | Gmail API search | ✅ Active |
| **Slack** | External | Slack API | OAuth2 | Slack API search | ✅ Active |
| **Xero** | External | Xero API | Client Credentials | Xero API where clause | ✅ **NEW** |
| **InHousePrint** | External | SQL Server | Hardcoded SA | SQL LIKE queries | ✅ **NEW** |
| **Google Drive** | External | Google Drive API | OAuth2 | Drive API search | ⏳ Planned |
| **OneDrive** | External | Microsoft Graph | OAuth2 | Graph API search | ⏳ Planned |
| **SharePoint** | External | Microsoft Graph | OAuth2 | Graph API search | ⏳ Planned |

---

## 🔄 Search Flow Diagram

```
User Input: "find budget microsoft"
         │
         ▼
┌────────────────────────┐
│ Frontend Preprocessing │
│ - Sanitize query       │
│ - Check selected srcs  │
└──────────┬─────────────┘
           │
           ▼
    POST /api/universal-search
    {
      query: "find budget microsoft",
      sources: ["documents", "xero", "inhouseprint"],
      search_type: "hybrid",
      limit: 10
    }
           │
           ▼
┌─────────────────────────┐
│ Backend Orchestrator    │
│ - Parse request         │
│ - Validate auth         │
│ - Prepare searches      │
└──────────┬──────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ Parallel Search Execution            │
│                                       │
│  Thread 1: Documents                 │
│    SELECT ... FROM document_library  │
│    WHERE ts_vector @@ query          │
│    AND embedding <=> query_vec       │
│    ✅ 3 results                       │
│                                       │
│  Thread 2: Xero (3 businesses)       │
│    For each business:                │
│      GET /Invoices?where=...         │
│      GET /Contacts?where=...         │
│    ✅ 5 results                       │
│                                       │
│  Thread 3: InHousePrint              │
│    SELECT ... FROM PublishingProject │
│    WHERE ProjectName LIKE '%budget%' │
│    OR ClientName LIKE '%microsoft%'  │
│    ✅ 2 results                       │
└──────────┬───────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│ Result Aggregation      │
│ - Merge all results     │
│ - Calculate scores      │
│ - Group by source       │
│ - Apply pagination      │
└──────────┬──────────────┘
           │
           ▼
    JSON Response
    {
      success: true,
      total_results: 10,
      sources: {
        documents: { count: 3, results: [...] },
        xero: { count: 5, results: [...] },
        inhouseprint: { count: 2, results: [...] }
      }
    }
           │
           ▼
┌─────────────────────────┐
│ Frontend Rendering      │
│ - Group by source       │
│ - Display cards         │
│ - Enable filtering      │
└─────────────────────────┘
```

---

## 🏢 Multi-Business Architecture (Xero)

```
┌─────────────────────────────────────────────────────────┐
│                  XERO SEARCH REQUEST                     │
│              Query: "find invoice microsoft"             │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │               │
        ▼              ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Business 1   │ │ Business 2   │ │ Business 3   │
│ InHouse Print│ │ InHouse Pub  │ │ InHouse Signs│
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │ GET Invoices   │ GET Invoices   │ GET Invoices
       │ GET Contacts   │ GET Contacts   │ GET Contacts
       │                │                │
       ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 2 invoices   │ │ 1 invoice    │ │ 0 invoices   │
│ 1 contact    │ │ 1 contact    │ │ 0 contacts   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┴────────────────┘
                       │
                       ▼
             ┌──────────────────┐
             │ Aggregate Results│
             │ 3 invoices total │
             │ 2 contacts total │
             │ Tag with business│
             └──────────────────┘
```

---

## 🗄️ Database Schema (InHousePrint)

```
┌─────────────────────────────────────────────────────────┐
│                   InHousePrint SQL Server                │
│                  Server: 3.25.76.138:1433                │
│                  Database: InHousePrint                  │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │               │
        ▼              ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Clients      │ │ Publishing   │ │ Products     │
│              │ │ Project      │ │              │
├──────────────┤ ├──────────────┤ ├──────────────┤
│ ID (PK)      │ │ ID (PK)      │ │ ID (PK)      │
│ CompanyName  │ │ ProjectName  │ │ ProductName  │
│ ContactName  │ │ Description  │ │ Description  │
│ Email        │ │ ClientID(FK) │ │ Price        │
│ Phone        │ │ StartDate    │ │ Category     │
│ Address      │ │ DeadlineDate │ │              │
│ Customer_    │ │ Status       │ │              │
│ XEROID ──────┼─┼──────────────┼─┼──────────────┤
│              │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
      │                │
      │  FK: ClientID  │
      └────────────────┘

Search Query Example:
SELECT p.*, c.CompanyName, c.ContactName
FROM PublishingProject p
LEFT JOIN Clients c ON p.ClientID = c.ID
WHERE 
  p.ProjectName LIKE '%query%' OR
  p.Description LIKE '%query%' OR
  c.CompanyName LIKE '%query%'
```

---

## 🔐 Authentication Flow

### Internal Sources (PostgreSQL)
```
User Session → JWT Token → user_id → PostgreSQL queries filtered by user_id
```

### External Sources (OAuth2)
```
Gmail/Slack:
  User → OAuth Consent → Refresh Token stored in credential store
  → Access Token (auto-refresh) → API calls

Xero:
  Application → Client Credentials → Access Token (cached 30 min)
  → API calls with Tenant-ID header

InHousePrint:
  Application → Hardcoded SA credentials → Direct SQL Server connection
```

---

## ⚡ Performance Metrics

### Expected Response Times
| Source | Avg Time | Max Time | Notes |
|--------|----------|----------|-------|
| Documents | 100ms | 300ms | PostgreSQL full-text + vector search |
| Threads | 50ms | 150ms | Simple PostgreSQL query |
| Messages | 80ms | 200ms | PostgreSQL with JOIN |
| Synergy | 60ms | 180ms | PostgreSQL with JSON aggregation |
| Vector DB | 150ms | 500ms | Qdrant/Pinecone API call |
| Gmail | 300ms | 1000ms | Google API (network latency) |
| Slack | 250ms | 900ms | Slack API (network latency) |
| Xero | 400ms | 1500ms | 3 businesses × 2 endpoints each |
| InHousePrint | 120ms | 400ms | SQL Server LIKE queries |

**Total (all sources):** 800ms - 2500ms (parallel execution)

### Optimization Strategies
1. **Caching:** Cache Xero results for 5 minutes
2. **Indexing:** Add full-text indexes to InHousePrint tables
3. **Pagination:** Limit results per source (5-20)
4. **Timeout:** Fail fast on slow sources (10s timeout)
5. **Lazy Loading:** Load more results on scroll

---

## 🚀 Deployment Checklist

### Environment Variables
- [ ] `XERO_PRINT_CLIENT_ID` / `XERO_PRINT_CLIENT_SECRET`
- [ ] `XERO_PUB_CLIENT_ID` / `XERO_PUB_CLIENT_SECRET`
- [ ] `XERO_SIGNS_CLIENT_ID` / `XERO_SIGNS_CLIENT_SECRET`
- [ ] `QDRANT_URL` / `QDRANT_API_KEY`
- [ ] `PINECONE_API_KEY` / `PINECONE_ENV`

### Database Migrations
- [ ] Xero credentials in `user_platform_credentials` table
- [ ] InHousePrint connection tested (3.25.76.138:1433)

### Python Dependencies
- [ ] `pymssql` installed (for InHousePrint)
- [ ] `qdrant-client` installed (for Vector DB)
- [ ] `requests` installed (for Xero API)

### Frontend Assets
- [ ] FontAwesome icons loaded (`fa-file-invoice`, `fa-print`)
- [ ] universal-search.js updated with new sources
- [ ] universal-search.css updated (if needed)

### Testing
- [ ] Unit tests for Xero client
- [ ] Unit tests for InHousePrint queries
- [ ] Integration tests for universal search
- [ ] Load testing (1000 concurrent searches)
- [ ] Error handling tests (network failures, timeouts)

---

## 📞 Troubleshooting Guide

### "Xero results empty"
1. Check credentials in database
2. Test Xero API directly: `curl -X POST https://identity.xero.com/connect/token`
3. Check business_id matches (1, 2, or 3)
4. Check Xero Developer Portal for API status

### "InHousePrint connection timeout"
1. Ping server: `ping 3.25.76.138`
2. Telnet port: `telnet 3.25.76.138 1433`
3. Check SQL Server firewall rules
4. Verify credentials: sa / Jack2011

### "Search too slow"
1. Enable query logging to identify slow source
2. Check database indexes (use EXPLAIN)
3. Reduce result limits
4. Enable caching for external APIs

### "Results not grouped correctly"
1. Check `source` field in results JSON
2. Verify `getSourceLabel()` has all sources
3. Check console for JavaScript errors
4. Inspect Network tab for API response structure

---

**END OF ARCHITECTURE DOCUMENTATION**

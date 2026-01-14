# 🧠 Vector Database Embedding Provider System - Complete Documentation

## Overview

The Vector Database module now supports **multiple embedding providers** with a dropdown selection interface, following the MustCare ValorAISynergySuite architecture pattern.

**Created:** November 29, 2025  
**Status:** ✅ Production Ready  
**Architecture Pattern:** MustCare ValorAISynergySuite provider factory pattern

---

## 📋 Table of Contents

1. [Supported Providers](#supported-providers)
2. [Architecture Overview](#architecture-overview)
3. [User Interface](#user-interface)
4. [Backend API](#backend-api)
5. [Credential Storage](#credential-storage)
6. [Usage Guide](#usage-guide)
7. [Adding New Providers](#adding-new-providers)

---

## Supported Providers

### 1. **Voyager AI (InHousePrint)**
- **Provider ID:** `voyager`
- **Platform:** `voyager`
- **API Key Format:** `pa-GOCp1HsNfuuvjXnHPumV5f6sD-YLQwQg5Fl3Fx2AlDm`
- **Models:**
  - `voyager` - Standard model (1536 dimensions)
  - `voyager-large` - Large model (1536 dimensions)
- **Use Case:** High-quality embeddings optimized for InHousePrint documents
- **Credential Key:** `VOYAGER_API_KEY`

### 2. **OpenAI**
- **Provider ID:** `openai`
- **Platform:** `openai_embeddings`
- **API Key Format:** `sk-proj-...`
- **Models:**
  - `text-embedding-ada-002` - Legacy model (1536 dimensions)
  - `text-embedding-3-small` - Small model (1536 dimensions)
  - `text-embedding-3-large` - Large model (3072 dimensions)
- **Use Case:** Industry-standard embeddings with broad compatibility
- **Credential Key:** `OPENAI_API_KEY`

---

## Architecture Overview

### Frontend Components

```
UI/modules/vector_database/
├── vector_database.html       - Provider dropdown + config forms
├── vector_database.js         - Controller with provider switching logic
└── vector_database.css        - Styling for provider configs
```

### Backend Components

```
AI_infrastructure/routes/
└── vector_db_routes.py        - API endpoints for config management
    ├── GET  /api/vector-db/embedding-config/get
    └── POST /api/vector-db/embedding-config/save
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  [Embedding Provider Dropdown: Voyager AI | OpenAI]             │
│                                                                   │
│  IF Voyager:                        IF OpenAI:                   │
│  ├─ API Key input                   ├─ API Key input            │
│  ├─ Model: voyager | voyager-large  └─ Model: ada-002 | 3-small│
│  └─ [Save] button                       └─ [Save] button        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    onEmbeddingProviderChange()
                              ↓
                Show/hide provider-specific forms
                              ↓
                    User fills in credentials
                              ↓
                     [Save] → saveEmbeddingConfig()
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API                                 │
│  POST /api/vector-db/embedding-config/save                      │
│  {                                                               │
│    user_id: 1,                                                   │
│    provider: "voyager",                                          │
│    platform: "voyager",                                          │
│    api_key: "pa-GOCp...",                                        │
│    model: "voyager",                                             │
│    metadata: { dimensions: 1536, ... }                           │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    UserAuthManager.store_platform_credential()
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   DATABASE STORAGE                               │
│  ai_infrastructure.oauth_tokens table:                           │
│  ├─ user_id: 1                                                   │
│  ├─ platform: "voyager"                                          │
│  ├─ access_token: "pa-GOCp..." (encrypted)                       │
│  └─ metadata: {                                                  │
│       "provider": "voyager",                                     │
│       "model": "voyager",                                        │
│       "dimensions": 1536,                                        │
│       "updated_at": "2025-11-29T..."                             │
│    }                                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## User Interface

### Credentials Tab Structure

```html
<!-- Pinecone Configuration (Vector DB) -->
[API Key input]
[Index Name input]
[Environment input]
[Namespace input]
[Save Credentials] [Test]

<!-- Embedding Model Configuration (NEW) -->
[Provider Dropdown: -- Select Provider --]
                   ├─ Voyager AI (InHousePrint)
                   └─ OpenAI

<!-- Conditional Provider Forms -->
IF Provider = "voyager":
  [Voyager API Key input]
  [Model: voyager | voyager-large]
  [Info: Voyager provides high-quality embeddings...]
  [Save Embedding Config]

IF Provider = "openai":
  [OpenAI API Key input]
  [Model: ada-002 | 3-small | 3-large]
  [Info: OpenAI embeddings provide industry-standard...]
  [Save Embedding Config]
```

### Visual Design

**Provider Dropdown:**
```
┌──────────────────────────────────────────┐
│ Embedding Provider *                     │
│ ┌──────────────────────────────────────┐ │
│ │ -- Select Provider --             ▼ │ │
│ └──────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

**Provider Configuration (Voyager Example):**
```
┌──────────────────────────────────────────┐
│ Voyager API Key *                        │
│ ┌──────────────────────────────────────┐ │
│ │ ●●●●●●●●●●●●●●●●●●●●               │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ Model                                    │
│ ┌──────────────────────────────────────┐ │
│ │ voyager (1536d)                   ▼ │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ ℹ️  Voyager provides high-quality    │ │
│ │    embeddings optimized for          │ │
│ │    InHousePrint documents.           │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │      💾 Save Embedding Config        │ │
│ └──────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

---

## Backend API

### GET `/api/vector-db/embedding-config/get`

**Purpose:** Retrieve saved embedding configuration for user

**Query Parameters:**
```javascript
{
  user_id: 1  // Required
}
```

**Response (Voyager):**
```json
{
  "success": true,
  "config": {
    "provider": "voyager",
    "model": "voyager",
    "dimensions": 1536,
    "api_key_masked": "****AlDm"
  }
}
```

**Response (No Config):**
```json
{
  "success": true,
  "config": null
}
```

### POST `/api/vector-db/embedding-config/save`

**Purpose:** Save embedding provider configuration

**Request Body:**
```javascript
{
  user_id: 1,                    // Required
  provider: "voyager",           // "voyager" or "openai"
  platform: "voyager",           // Storage platform name
  api_key: "pa-GOCp...",         // API key
  model: "voyager",              // Model name
  metadata: {                    // Optional
    provider: "voyager",
    model: "voyager",
    dimensions: 1536
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Voyager configuration saved successfully",
  "provider": "voyager",
  "model": "voyager"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "api_key required"
}
```

---

## Credential Storage

### Database Schema

**Table:** `ai_infrastructure.oauth_tokens`

**Voyager Entry:**
```sql
INSERT INTO ai_infrastructure.oauth_tokens (
  user_id,
  platform,
  access_token,
  metadata
) VALUES (
  1,
  'voyager',
  'pa-GOCp1HsNfuuvjXnHPumV5f6sD-YLQwQg5Fl3Fx2AlDm',
  '{
    "provider": "voyager",
    "model": "voyager",
    "dimensions": 1536,
    "description": "Voyager embedding model configuration",
    "updated_at": "2025-11-29T12:00:00"
  }'
);
```

**OpenAI Entry:**
```sql
INSERT INTO ai_infrastructure.oauth_tokens (
  user_id,
  platform,
  access_token,
  metadata
) VALUES (
  1,
  'openai_embeddings',
  'sk-proj-...',
  '{
    "provider": "openai",
    "model": "text-embedding-ada-002",
    "dimensions": 1536,
    "description": "OpenAI embeddings - backup option",
    "updated_at": "2025-11-29T12:00:00"
  }'
);
```

### Retrieval Pattern

**Priority Order:**
1. Try Voyager credentials first
2. Fallback to OpenAI if Voyager not found
3. Return `null` if neither found

```python
# Backend retrieval logic
voyager_creds = auth_manager.get_platform_credentials(user_id, 'voyager')
if voyager_creds and 'VOYAGER_API_KEY' in voyager_creds:
    return voyager_config

openai_creds = auth_manager.get_platform_credentials(user_id, 'openai_embeddings')
if openai_creds and 'OPENAI_API_KEY' in openai_creds:
    return openai_config

return None
```

---

## Usage Guide

### Initial Setup

**1. Open Vector Database Sidebar**
- Click Vector Database toggle button in left sidebar
- Navigate to **Credentials** tab

**2. Configure Pinecone (Vector DB)**
- Enter Pinecone API key
- Enter index name (e.g., `inhouseprint`)
- Enter environment (e.g., `us-east-1`)
- Click **Save Credentials**

**3. Configure Embedding Provider**
- Scroll to "Embedding Model Configuration"
- Select provider from dropdown:
  - **Voyager AI** for InHousePrint documents
  - **OpenAI** for general-purpose embeddings

**4. Enter Provider Credentials**

**For Voyager:**
```
API Key: pa-GOCp1HsNfuuvjXnHPumV5f6sD-YLQwQg5Fl3Fx2AlDm
Model: voyager (1536d)
```

**For OpenAI:**
```
API Key: sk-proj-...
Model: text-embedding-ada-002 (1536d)
```

**5. Save Configuration**
- Click **Save Embedding Config**
- Verify success message appears

### Changing Providers

**To Switch from Voyager to OpenAI:**

1. Open Vector Database sidebar → Credentials tab
2. Change provider dropdown to "OpenAI"
3. OpenAI form appears automatically
4. Enter OpenAI API key
5. Select model
6. Click **Save Embedding Config**
7. New configuration overwrites old one

### Using Saved Configuration

**Frontend Auto-Load:**
```javascript
// On sidebar init
await this.loadEmbeddingConfig();
// Automatically:
// - Sets provider dropdown
// - Shows correct form
// - Loads model selection
// - Masks API key
```

**Backend Tool Access:**
```python
# In vector DB tools
from AI_infrastructure.auth.user_auth import UserAuthManager

auth_manager = UserAuthManager()
voyager_creds = auth_manager.get_platform_credentials(user_id, 'voyager')

if voyager_creds:
    api_key = voyager_creds['VOYAGER_API_KEY']
    model = voyager_creds['metadata']['model']
    # Use for embedding generation
```

---

## Adding New Providers

### Step-by-Step Guide

**Example: Adding Cohere Embeddings**

#### 1. Update Frontend HTML

**File:** `UI/modules/vector_database/vector_database.html`

```html
<!-- Add to provider dropdown -->
<select id="embedding-provider" class="form-input">
    <option value="">-- Select Provider --</option>
    <option value="voyager">Voyager AI (InHousePrint)</option>
    <option value="openai">OpenAI</option>
    <option value="cohere">Cohere</option>  <!-- NEW -->
</select>

<!-- Add provider configuration form -->
<div id="cohere-config" class="embedding-provider-config" style="display: none;">
    <div class="form-group">
        <label class="form-label" for="cohere-api-key">
            Cohere API Key <span style="color: #f85149;">*</span>
        </label>
        <input 
            type="password" 
            id="cohere-api-key" 
            class="form-input" 
            placeholder="Enter Cohere API key"
        />
    </div>

    <div class="form-group">
        <label class="form-label" for="cohere-model">
            Model
        </label>
        <select id="cohere-model" class="form-input">
            <option value="embed-english-v3.0">embed-english-v3.0 (1024d)</option>
            <option value="embed-multilingual-v3.0">embed-multilingual-v3.0 (1024d)</option>
        </select>
    </div>

    <div class="form-hint">
        <i class="fas fa-info-circle"></i>
        Cohere provides multilingual embeddings with high accuracy.
    </div>
</div>
```

#### 2. Update Frontend JavaScript

**File:** `UI/modules/vector_database/vector_database.js`

```javascript
// Update onEmbeddingProviderChange()
onEmbeddingProviderChange() {
    const provider = document.getElementById('embedding-provider').value;
    
    // Hide all configs
    document.getElementById('voyager-config').style.display = 'none';
    document.getElementById('openai-config').style.display = 'none';
    document.getElementById('cohere-config').style.display = 'none';  // NEW

    // Show selected
    if (provider === 'voyager') {
        document.getElementById('voyager-config').style.display = 'block';
    } else if (provider === 'openai') {
        document.getElementById('openai-config').style.display = 'block';
    } else if (provider === 'cohere') {                                // NEW
        document.getElementById('cohere-config').style.display = 'block';
    }
}

// Update saveEmbeddingConfig()
async saveEmbeddingConfig() {
    const provider = document.getElementById('embedding-provider').value;
    let apiKey, model, platform;

    if (provider === 'cohere') {                                       // NEW
        apiKey = document.getElementById('cohere-api-key').value.trim();
        model = document.getElementById('cohere-model').value;
        platform = 'cohere_embeddings';

        if (!apiKey) {
            this.showEmbeddingMessage('Please enter Cohere API key', 'error');
            return;
        }
    }
    // ... rest of function
}

// Update getOpenAIDimensions() to support Cohere
getModelDimensions(provider, model) {                                  // NEW
    if (provider === 'cohere') {
        return 1024;  // All Cohere models use 1024d
    } else if (provider === 'openai') {
        // ... existing OpenAI logic
    } else if (provider === 'voyager') {
        return 1536;
    }
}
```

#### 3. Update Backend API

**File:** `AI_infrastructure/routes/vector_db_routes.py`

```python
@vector_db_bp.route('/api/vector-db/embedding-config/get', methods=['GET'])
def get_embedding_config():
    # Add Cohere credential check
    cohere_creds = auth_manager.get_platform_credentials(user_id, 'cohere_embeddings')
    if cohere_creds and 'COHERE_API_KEY' in cohere_creds:
        metadata = cohere_creds.get('metadata', {})
        return jsonify({
            'success': True,
            'config': {
                'provider': 'cohere',
                'model': metadata.get('model', 'embed-english-v3.0'),
                'dimensions': metadata.get('dimensions', 1024),
                'api_key_masked': '****' + cohere_creds['COHERE_API_KEY'][-8:]
            }
        })
    
    # ... existing Voyager/OpenAI checks

@vector_db_bp.route('/api/vector-db/embedding-config/save', methods=['POST'])
def save_embedding_config():
    # Add Cohere case
    if provider == 'cohere':
        credential_key = 'COHERE_API_KEY'
    elif provider == 'voyager':
        credential_key = 'VOYAGER_API_KEY'
    # ... rest of function
```

#### 4. Test New Provider

```javascript
// Browser Console Testing
window.vectorDbSidebar.onEmbeddingProviderChange();  // Should show Cohere form
// Fill in credentials
// Click Save
// Check console for success message
```

---

## Troubleshooting

### Issue: Provider form doesn't appear

**Symptom:** Selecting provider from dropdown does nothing

**Solutions:**
1. Check browser console for JavaScript errors
2. Verify `onEmbeddingProviderChange()` is called:
   ```javascript
   <select id="embedding-provider" onchange="window.vectorDbSidebar.onEmbeddingProviderChange()">
   ```
3. Verify provider config div exists with correct ID:
   ```html
   <div id="voyager-config" class="embedding-provider-config">
   ```

### Issue: Credentials not saving

**Symptom:** Click Save but no success message

**Solutions:**
1. Check browser DevTools → Network tab for API errors
2. Verify backend endpoint is running:
   ```powershell
   BISTART  # Restart Flask server
   ```
3. Check backend console for error logs
4. Verify request body contains all required fields:
   ```javascript
   { user_id, provider, platform, api_key, model }
   ```

### Issue: Saved config not loading

**Symptom:** Reopen sidebar, credentials not populated

**Solutions:**
1. Check `loadEmbeddingConfig()` is called in `init()`
2. Verify GET endpoint returns data:
   ```
   GET /api/vector-db/embedding-config/get?user_id=1
   ```
3. Check database for stored credentials:
   ```sql
   SELECT * FROM ai_infrastructure.oauth_tokens 
   WHERE user_id = 1 AND platform IN ('voyager', 'openai_embeddings');
   ```

---

## Best Practices

### Provider Selection
- ✅ Use **Voyager** for InHousePrint-specific documents
- ✅ Use **OpenAI** for general-purpose embeddings
- ✅ Switch providers based on document type/use case

### Security
- ✅ API keys stored encrypted in database
- ✅ Keys masked in GET responses (`****AtDykyhr`)
- ✅ Never log full API keys in console
- ✅ Use HTTPS for production deployments

### Performance
- ✅ Cache embedding configurations in memory
- ✅ Only regenerate embeddings when provider/model changes
- ✅ Use appropriate model dimensions (1536 vs 3072)

---

**Last Updated:** November 29, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Architecture:** MustCare ValorAISynergySuite provider pattern implemented

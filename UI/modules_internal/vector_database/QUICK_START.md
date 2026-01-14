# Vector Database Module - Quick Start Guide

**Version:** 2.0.0 Enhanced Edition  
**Date:** November 30, 2025  
**Framework:** ModuleLoaderV4  
**Status:** ✅ Phase 1 Complete

---

## 🚀 What's New

### **Enhanced Capabilities Added**

1. **🔍 Hybrid Search** - Keyword + semantic search with sparse vectors
2. **🌐 Cross-Namespace Queries** - Search multiple namespaces in parallel
3. **🔧 Metadata Filtering** - Query vectors without embeddings using advanced filters
4. **📁 Namespace Management** - List, describe, and delete namespaces

### **Modern Framework Migration**

- Composition pattern (no class inheritance)
- Lifecycle hooks: `onLoad`, `onSidebarLoad`, `onUnload`
- Explicit utility injection via `Object.assign(this, utilities)`
- Automatic event cleanup (no manual listener removal)

---

## 📁 File Structure

```
UI/modules_internal/vector_database/
├── 📄 manifest.json                     ✅ V3.0 spec with 14 endpoints
├── 📜 vector_database_modern.js         ✅ Core module (800 lines)
├── 📜 vector_database_enhanced.js       ⭐ NEW - Advanced features (850 lines)
├── 📜 vector_database_integration.js    ⭐ NEW - Bootstrap connector
├── 🎨 vector_database.css               Legacy base styles
├── 🎨 vector_database_enhanced.css      ⭐ NEW - Enhanced styles (400 lines)
├── 📄 vector_database.html              Legacy sidebar HTML
├── 📖 README.md                         Complete documentation (1,011 lines)
├── 📋 IMPLEMENTATION_SUMMARY.md         ⭐ NEW - Feature summary
├── 📋 PINECONE_ENHANCED_FEATURES.md     ⭐ NEW - Enhancement roadmap
└── 📋 QUICK_START.md                    ⭐ This file
```

---

## 🎯 Quick Setup (5 Minutes)

### **Step 1: Load Module with ModuleLoaderV4**

```javascript
// In browser console or initialization script
await window.ModuleLoaderV4.loadModule('vector_database', 'sidebar');
```

### **Step 2: Configure Credentials**

1. Open sidebar (should auto-load)
2. Click **"Credentials"** tab
3. Enter:
   - Pinecone API Key
   - Index Name (e.g., `my-vectors`)
   - Environment (e.g., `us-east-1`)
   - Namespace (optional, default: `default`)
4. Click **"Test Connection"** to verify

### **Step 3: Configure Embeddings**

1. Stay on **"Credentials"** tab
2. Select embedding provider:
   - **OpenAI** (recommended) - `text-embedding-ada-002` or `text-embedding-3-small`
   - **Voyager AI** - Alternative provider
3. Enter API key for chosen provider
4. Click **"Save Embedding Config"**

### **Step 4: Upload Documents**

1. Click **"Upload"** tab
2. Drag & drop files or click to browse
3. Supported formats: PDF, DOCX, TXT, MD
4. Toggle **"Enable Hybrid Search"** for keyword + semantic (⭐ NEW)
5. Click **"Process Files"**

### **Step 5: Explore Enhanced Features**

Click new tabs:
- **🔍 Hybrid Search** - Advanced search with sparse vectors
- **🌐 Cross-Namespace** - Multi-namespace queries
- **🔧 Metadata Filter** - Advanced filtering
- **📁 Namespaces** - Namespace management

---

## 🎨 UI Components

### **Base Tabs (Original)**

1. **Credentials** - Setup Pinecone + embedding config
2. **Upload** - Document upload with drag & drop
3. **Documents** - List indexed documents

### **Enhanced Tabs (New)** ⭐

4. **Hybrid Search** - Keyword + semantic search
5. **Cross-Namespace** - Multi-namespace queries
6. **Metadata Filter** - Advanced metadata filtering
7. **Namespaces** - Namespace management

---

## 🛠️ Backend Integration TODO

### **Required Flask Endpoints**

Add to `AI_infrastructure/routes/vector_db/vector_db_routes.py`:

```python
from flask import Blueprint, request, jsonify
from AI_infrastructure.auth.user_auth import UserAuthManager

auth_manager = UserAuthManager()
vector_db_bp = Blueprint('vector_db', __name__)

# NEW ENDPOINT 1: Cross-Namespace Query
@vector_db_bp.route('/query-namespaces', methods=['POST'])
@auth_manager.require_auth
def query_namespaces():
    user_id = request.user_id
    data = request.json
    
    # Call Pinecone query_namespaces()
    # Return aggregated results
    
    return jsonify({"matches": [], "usage": {}})

# NEW ENDPOINT 2: Fetch by Metadata
@vector_db_bp.route('/fetch-by-metadata', methods=['POST'])
@auth_manager.require_auth
def fetch_by_metadata():
    user_id = request.user_id
    data = request.json
    
    # Call Pinecone fetch_by_metadata()
    # Return filtered vectors
    
    return jsonify({"vectors": [], "pagination": {}})

# NEW ENDPOINT 3: List Namespaces
@vector_db_bp.route('/namespaces', methods=['GET'])
@auth_manager.require_auth
def list_namespaces():
    user_id = request.user_id
    
    # Call Pinecone namespace.list()
    # Return namespace array
    
    return jsonify({"namespaces": []})

# NEW ENDPOINT 4: Describe Namespace
@vector_db_bp.route('/namespaces/<namespace>', methods=['GET'])
@auth_manager.require_auth
def describe_namespace(namespace):
    user_id = request.user_id
    
    # Call Pinecone namespace.describe(namespace)
    # Return namespace details
    
    return jsonify({"name": "", "vector_count": 0, "dimension": 0})

# NEW ENDPOINT 5: Delete Namespace
@vector_db_bp.route('/namespaces/<namespace>', methods=['DELETE'])
@auth_manager.require_auth
def delete_namespace(namespace):
    user_id = request.user_id
    
    # Call Pinecone namespace.delete(namespace)
    # Return success status
    
    return jsonify({"success": True})
```

### **Required Tool Updates**

Add to `tools/implementations/pinecone/pinecone_tools.py`:

```python
def pinecone_query_namespaces(
    query_text: str,
    namespaces: List[str],
    metric: str = 'cosine',
    top_k: int = 10,
    **kwargs
) -> Dict[str, Any]:
    """Query multiple namespaces simultaneously"""
    user_id = kwargs.get('_user_id')
    client = _get_pinecone_client(user_id)
    
    embedding = _generate_embedding(query_text, user_id)
    
    results = client.query_namespaces(
        vector=embedding,
        namespaces=namespaces,
        metric=metric,
        top_k=top_k,
        include_metadata=True
    )
    
    return {
        "matches": [...],
        "usage": results.usage
    }

def pinecone_fetch_by_metadata(
    filter: Dict[str, Any],
    namespace: str = "default",
    limit: int = 100,
    **kwargs
) -> Dict[str, Any]:
    """Fetch vectors by metadata filter"""
    user_id = kwargs.get('_user_id')
    client = _get_pinecone_client(user_id)
    
    results = client.fetch_by_metadata(
        filter=filter,
        namespace=namespace,
        limit=limit
    )
    
    return {
        "vectors": [...],
        "pagination": {...}
    }
```

Update `tools/schemas/pinecone_tools.json`:

```json
{
  "tools": [
    {
      "name": "pinecone_query_namespaces",
      "description": "Query multiple namespaces in parallel",
      "platform": "pinecone",
      "parameters": {
        "type": "object",
        "properties": {
          "query_text": {"type": "string"},
          "namespaces": {"type": "array", "items": {"type": "string"}},
          "metric": {"type": "string", "enum": ["cosine", "euclidean", "dotproduct"]},
          "top_k": {"type": "integer", "default": 10}
        },
        "required": ["query_text", "namespaces"]
      }
    },
    {
      "name": "pinecone_fetch_by_metadata",
      "description": "Fetch vectors by metadata filter",
      "platform": "pinecone",
      "parameters": {
        "type": "object",
        "properties": {
          "filter": {"type": "object"},
          "namespace": {"type": "string", "default": "default"},
          "limit": {"type": "integer", "default": 100}
        },
        "required": ["filter"]
      }
    }
  ]
}
```

---

## 🧪 Testing

### **Frontend Tests**

```javascript
// Test 1: Module loads
await window.ModuleLoaderV4.loadModule('vector_database', 'sidebar');
console.assert(window.ModuleLoaderV4.modules.vector_database, 'Module loaded');

// Test 2: Utilities injected
const module = window.ModuleLoaderV4.modules.vector_database;
console.assert(module.dom, 'DOM utility exists');
console.assert(module.api, 'API utility exists');

// Test 3: Enhanced features available
console.assert(module.enhanced, 'Enhanced features loaded');
console.assert(typeof module.switchToEnhancedTab === 'function', 'Enhanced tab switching available');
```

### **Backend Tests**

```bash
# Test namespace listing
curl -X GET http://localhost:5001/api/vector-db/namespaces \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test cross-namespace query
curl -X POST http://localhost:5001/api/vector-db/query-namespaces \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query_text": "test", "namespaces": ["default", "test"], "metric": "cosine", "top_k": 10}'

# Test metadata filtering
curl -X POST http://localhost:5001/api/vector-db/fetch-by-metadata \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filter": {"category": {"$eq": "legal"}}, "namespace": "default", "limit": 100}'
```

---

## 🐛 Troubleshooting

### **Issue: Module won't load**

**Symptoms:** Console error "Module not found" or blank sidebar

**Solutions:**
1. Check file paths in `manifest.json`
2. Verify `ModuleLoaderV4` is initialized
3. Check browser console for errors
4. Ensure all files are in correct directory

### **Issue: Enhanced features not showing**

**Symptoms:** Only 3 tabs visible (Credentials, Upload, Documents)

**Solutions:**
1. Check if `vector_database_enhanced.js` imported
2. Verify `vector_database_integration.js` bootstrap ran
3. Check console for import errors
4. Ensure `vector_database_enhanced.css` loaded

### **Issue: API calls failing**

**Symptoms:** "Network error" or 404 responses

**Solutions:**
1. Verify Flask server running on port 5001
2. Check JWT token validity
3. Ensure endpoints registered in `flask_app.py`
4. Check CORS configuration

### **Issue: Hybrid search not working**

**Symptoms:** Results same as regular search

**Solutions:**
1. Verify `enable_hybrid` parameter sent to backend
2. Check if sparse vectors generated during upload
3. Ensure TF-IDF vectorizer installed: `pip install scikit-learn`
4. Verify Pinecone index supports sparse vectors

---

## 📖 Documentation

- **Complete Guide**: `README.md` (1,011 lines)
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Enhancement Roadmap**: `PINECONE_ENHANCED_FEATURES.md`
- **This Guide**: `QUICK_START.md`

---

## 🎓 Key Concepts

### **Hybrid Search**
Combines dense vectors (semantic) with sparse vectors (keywords). Best for domain-specific queries with technical terms.

### **Cross-Namespace Queries**
Query multiple isolated namespaces simultaneously. Useful for multi-tenant applications or cross-domain searches.

### **Metadata Filtering**
Query vectors by metadata alone without generating embeddings. Efficient for data export, compliance, auditing.

### **Namespace Management**
Organize vectors into isolated namespaces for better data organization and multi-tenant support.

---

## 🔗 Resources

- **Pinecone Docs**: https://docs.pinecone.io
- **Modern Framework**: `UI/MODERN_FRAMEWORK_GUIDE.md`
- **Utility Reference**: `UI/UTILITIES_REFERENCE.md`
- **Tool Registry**: `tools/registry_v3.py`

---

## ✅ Checklist

### **Setup Complete When:**

- [ ] Module loads in sidebar
- [ ] Credentials saved and tested
- [ ] Documents uploaded successfully
- [ ] All 7 tabs visible
- [ ] Enhanced CSS loaded (professional dark theme)
- [ ] No console errors

### **Backend Complete When:**

- [ ] 5 new endpoints implemented
- [ ] 2 new tools added to registry
- [ ] Sparse vector generation working
- [ ] Namespace operations functional
- [ ] All API tests passing

---

**Next Steps:** Complete backend integration following TODO sections above. All frontend UI is ready!

**Support:** Check `README.md` for detailed API reference and troubleshooting.

**Version:** 2.0.0 Enhanced Edition  
**Last Updated:** November 30, 2025

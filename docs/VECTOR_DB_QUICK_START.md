# ⚡ Vector Database Quick Start - 15 Minutes to Production

**Goal:** Get autonomous vector database search working in 15 minutes

---

## 📋 Prerequisites Checklist

- [ ] Pinecone account with API key
- [ ] OpenAI API key
- [ ] Python 3.9+
- [ ] AI_agents server running (BISTART)

---

## 🚀 5-Step Setup (15 Minutes)

### Step 1: Environment Variables (2 minutes)

Create/edit `.env` file in `c:\Users\gpoli\GIT\AI_agents\`:

```bash
# Vector Database
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=ai-agents-vectors
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for full document retrieval from cloud)
GOOGLE_DRIVE_CREDENTIALS_PATH=path/to/credentials.json
```

### Step 2: Install Dependencies (3 minutes)

```powershell
cd c:\Users\gpoli\GIT\AI_agents
pip install pinecone-client openai PyPDF2 python-docx
```

### Step 3: Create Pinecone Index (2 minutes)

Run this once to set up your vector database:

```powershell
python -c "
from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

# Create index
pc.create_index(
    name=os.getenv('PINECONE_INDEX_NAME', 'ai-agents-vectors'),
    dimension=1536,  # OpenAI ada-002
    metric='cosine',
    spec=ServerlessSpec(cloud='aws', region='us-east-1')
)

print('✅ Pinecone index created successfully!')
"
```

**Note:** If index already exists, you'll see an error - that's fine, skip to step 4.

### Step 4: Register API Routes (3 minutes)

Open `c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\flask_app.py` and add:

```python
# Near the top with other imports
from AI_infrastructure.routes.vector_db_routes import vector_db_bp

# After other blueprint registrations (around line 50-100)
app.register_blueprint(vector_db_bp)
```

### Step 5: Restart Server & Test (5 minutes)

```powershell
# Stop server if running
BISTOP  # or Ctrl+C in terminal

# Start server
cd c:\Users\gpoli\GIT\AI_agents
BISTART

# Wait 10 seconds for tools to load
Start-Sleep -Seconds 10

# Test tool availability
CHAT List vector database tools

# Test upload endpoint
curl http://localhost:5001/api/vector-db/stats
```

**Expected output:**
```json
{
  "success": true,
  "stats": {
    "total_namespaces": 0,
    "total_vectors": 0
  }
}
```

---

## 🧪 Quick Test (5 Minutes)

### Test 1: Upload a Document

1. Open sidebar at `http://localhost:5001`
2. Click "Vector Database" tab
3. Click "Upload Documents"
4. Select a PDF/DOCX file
5. Wait for "Upload complete" message

### Test 2: AI Search (via CHAT command)

```powershell
CHAT Search the vector database for documents about return policies
```

**What should happen:**
1. AI says: "I'll search the vector database..."
2. AI calls: `vector_db_search(query="return policies")`
3. AI responds with: "I found 3 documents about return policies..."

### Test 3: Full Document Retrieval

```powershell
CHAT Get the complete text of document doc_abc123
```

**What should happen:**
1. AI calls: `vector_db_get_full_document(document_id="doc_abc123")`
2. AI responds with: Full document text or summary

---

## ✅ Verification Checklist

After setup, verify these:

- [ ] **Environment variables set:** `echo $env:PINECONE_API_KEY`
- [ ] **Dependencies installed:** `pip show pinecone-client`
- [ ] **Pinecone index exists:** Check Pinecone dashboard
- [ ] **Tools loaded:** `CHAT List vector database tools` shows 4 tools
- [ ] **API routes registered:** `curl http://localhost:5001/api/vector-db/stats` returns JSON
- [ ] **Upload works:** Upload test file via UI
- [ ] **AI search works:** AI calls `vector_db_search` when asked
- [ ] **Full doc retrieval works:** AI can fetch complete documents

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pinecone'"

**Solution:**
```powershell
pip install pinecone-client
```

### Issue: "PINECONE_API_KEY not set"

**Solution:** Check `.env` file exists and has:
```bash
PINECONE_API_KEY=your_actual_key_here
```

### Issue: "Tools not showing up"

**Solution:**
1. Check `tools/schemas/vector_database_tools.json` exists
2. Restart server: `BISTOP; BISTART`
3. Wait 15 seconds for tools to load
4. Check logs: `docker logs ai-agents-flask` or terminal output

### Issue: "Pinecone index not found"

**Solution:** Create index manually:
```powershell
python -c "from pinecone import Pinecone, ServerlessSpec; pc = Pinecone(api_key='YOUR_KEY'); pc.create_index(name='ai-agents-vectors', dimension=1536, metric='cosine', spec=ServerlessSpec(cloud='aws', region='us-east-1'))"
```

### Issue: "Upload endpoint returns 404"

**Solution:** Verify blueprint registration in `flask_app.py`:
```python
from AI_infrastructure.routes.vector_db_routes import vector_db_bp
app.register_blueprint(vector_db_bp)
```

### Issue: "AI doesn't call vector_db_search"

**Possible causes:**
1. **Tools not loaded:** Check tool registry: `GET /api/tools/list`
2. **AI doesn't know to search:** Ask explicitly: "Search the vector database for X"
3. **Namespace mismatch:** Ensure documents uploaded to correct namespace

---

## 📊 What You Just Built

### Architecture Created:

```
User → AI Agent (Claude)
    ↓ (autonomous decision)
AI calls: vector_db_search(query="X")
    ↓
Pinecone Vector DB
    ↓ (3 snippets + metadata)
AI reads results
    ↓ (if snippets not enough)
AI calls: vector_db_get_full_document(document_id="Y")
    ↓
Google Drive / Local Storage
    ↓ (complete document)
AI crafts answer
```

### Tools Available:

1. **`vector_db_search`** - AI searches for relevant snippets
2. **`vector_db_get_full_document`** - AI fetches complete files
3. **`vector_db_list_namespaces`** - AI discovers collections
4. **`vector_db_get_document_metadata`** - AI gets file info

### Key Features:

- ✅ **AI autonomous control** (not automatic injection)
- ✅ **Metadata-rich responses** with cloud links
- ✅ **Full document retrieval** from Google Drive
- ✅ **Namespace isolation** (per user/workspace)
- ✅ **Semantic search** with similarity scoring
- ✅ **Smart chunking** with overlap

---

## 🎯 Next Steps

### Immediate (Today):

1. **Upload your documents:**
   - Customer policies
   - Product manuals
   - FAQ documents
   - Internal knowledge base

2. **Test AI search:**
   - Ask questions about uploaded content
   - Verify AI finds relevant info
   - Check cloud links work

3. **Configure namespaces:**
   - Create workspace-specific collections
   - Organize by project/team

### This Week:

1. **Google Drive Integration:**
   - Connect Google Drive account
   - Enable automatic upload to Drive
   - Test full document retrieval

2. **Optimize Chunking:**
   - Adjust chunk size (default: 800 chars)
   - Test overlap settings (default: 20 chars)
   - Monitor search quality

3. **User Training:**
   - Show team how to upload docs
   - Demonstrate AI search capabilities
   - Collect feedback

### This Month:

1. **Advanced Features:**
   - Implement hybrid search (keyword + vector)
   - Add document categorization
   - Create custom embedding models

2. **Enterprise Setup:**
   - Configure role-based access
   - Set up audit logging
   - Enable compliance mode (HIPAA/GDPR)

3. **Performance Tuning:**
   - Optimize chunk sizes per doc type
   - Implement caching layer
   - Monitor vector database costs

---

## 💡 Usage Examples

### Example 1: Customer Support

```
User: "What's our return policy for defective items?"

AI (autonomous):
1. Calls: vector_db_search(query="return policy defective items")
2. Gets: 3 snippets from return_policy.pdf
3. Responds: "According to our return policy, defective items..."
4. Provides cloud link: [View Full Policy](https://drive.google.com/...)
```

### Example 2: Product Information

```
User: "Do we have specs for Model XYZ-500?"

AI (autonomous):
1. Calls: vector_db_search(query="Model XYZ-500 specifications")
2. Gets: 2 snippets from product_specs.pdf
3. Decides: "Snippets don't show full specs table"
4. Calls: vector_db_get_full_document(document_id="doc_xyz500")
5. Gets: Complete spec sheet with tables
6. Responds: "Here are the full specs for Model XYZ-500: [detailed info]"
```

### Example 3: Internal Knowledge

```
User: "How do I configure the email server?"

AI (autonomous):
1. Calls: vector_db_list_namespaces() to see available collections
2. Searches: vector_db_search(query="email server configuration", namespace="it_docs")
3. Gets: 1 snippet from setup_guide.md
4. Responds with step-by-step instructions
5. Offers: "Would you like me to fetch the complete setup guide?"
```

---

## 📚 Additional Resources

- **Full Documentation:** `docs/AUTONOMOUS_VECTOR_DB_INTEGRATION.md`
- **MustCare Analysis:** `docs/MUSTCARE_VECTOR_DB_INTEGRATION_ANALYSIS.md`
- **Tool Schema:** `tools/schemas/vector_database_tools.json`
- **Implementation:** `tools/implementations/vector_database.py`
- **API Routes:** `AI_infrastructure/routes/vector_db_routes.py`

---

## 🤝 Getting Help

**If stuck:**

1. Check troubleshooting section above
2. Review logs: Terminal output or Docker logs
3. Test API directly: `curl http://localhost:5001/api/vector-db/stats`
4. Verify environment variables: `echo $env:PINECONE_API_KEY`
5. Check tool loading: `CHAT List vector database tools`

**Common mistakes:**

- ❌ Forgot to create Pinecone index
- ❌ Wrong API key in .env
- ❌ Didn't restart server after adding routes
- ❌ Tools not loaded (need to wait 10-15 seconds)
- ❌ Namespace mismatch (uploaded to "default", searching "custom")

---

**Status:** ✅ Quick Start Guide  
**Time:** 15 minutes  
**Difficulty:** Easy  
**Last Updated:** November 29, 2025

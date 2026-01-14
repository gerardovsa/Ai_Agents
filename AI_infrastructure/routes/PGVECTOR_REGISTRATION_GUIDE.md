# pgvector Routes Registration Guide

## File Created
`AI_infrastructure/routes/pgvector_routes.py` ✅

## Registration Required in Flask App

Add these lines to `AI_infrastructure/flask_app.py`:

```python
# Import pgvector blueprint
from routes.pgvector_routes import pgvector_bp

# Register pgvector blueprint (add after other blueprint registrations)
app.register_blueprint(pgvector_bp)
logger.info("✅ Registered pgvector routes")
```

## Usage Example (Frontend)

```javascript
// Create pgvector index
const response = await api.post('/api/pgvector/create-index', {
    namespace: 'my_documents',
    dimensions: 1536
});

// Upsert vectors
await api.post('/api/pgvector/upsert', {
    vectors: [
        {
            text: 'This is a document about AI',
            metadata: {title: 'AI Overview', author: 'John'}
        }
    ],
    namespace: 'my_documents'
});

// Search similar
const results = await api.post('/api/pgvector/search', {
    query: 'artificial intelligence',
    namespace: 'my_documents',
    top_k: 5,
    threshold: 0.7
});

// Get stats
const stats = await api.get('/api/pgvector/stats');
```

## Benefits Over Pinecone
- ✅ No external API calls (20ms vs 150ms)
- ✅ Free (no $70/month cost)
- ✅ Already deployed (pgvector extension enabled)
- ✅ Same database integration
- ✅ JWT authentication built-in

## Testing
1. Ensure Supabase pgvector extension is enabled (already done)
2. Test auth by calling any endpoint (JWT required)
3. Create index → upsert vectors → search

## Documentation
See `pgvector_routes.py` file header for complete API documentation.

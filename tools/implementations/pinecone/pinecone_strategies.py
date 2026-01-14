"""
Pinecone Vector Database Strategies & Education Tool

FILE: tools/implementations/pinecone/pinecone_strategies.py
PURPOSE: Expert AI assistance for understanding vector database concepts and configuration strategies

FUNCTION:
- pinecone_explain_strategies: Comprehensive explanations of vector DB concepts

LAST MODIFIED: 2025-11-30
"""

from typing import Dict, Any, Optional


def pinecone_explain_strategies(
    topic: str,
    context: Optional[str] = None,
    depth: str = 'intermediate',
    include_examples: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Provide comprehensive explanations of Pinecone vector database strategies.
    
    Args:
        topic: Concept to explain (embeddings_basics, similarity_metrics, hybrid_search, etc.)
        context: User's specific situation (optional)
        depth: Explanation level (beginner, intermediate, advanced)
        include_examples: Include code examples
        
    Returns:
        {
            "success": true,
            "topic": "hybrid_search",
            "explanation": "...",
            "use_cases": [...],
            "best_practices": [...],
            "examples": [...],
            "recommendations": [...]
        }
    """
    
    # Knowledge base with comprehensive explanations
    knowledge_base = {
        "embeddings_basics": {
            "title": "Vector Embeddings & Semantic Search Fundamentals",
            "explanation": """
**What are Vector Embeddings?**

Vector embeddings are numerical representations of text, images, or other data that capture semantic meaning. Instead of matching exact keywords, embeddings allow you to find content based on *meaning*.

**Example:**
- Query: "dog" 
- Traditional search: Only finds exact word "dog"
- Semantic search: Finds "puppy", "canine", "pet", "Golden Retriever" (similar meaning)

**How Embeddings Work:**

1. **Text Input**: "The quick brown fox jumps over the lazy dog"
2. **Embedding Model**: OpenAI text-embedding-ada-002 
3. **Vector Output**: [0.023, -0.145, 0.567, ..., 0.234] (1536 numbers)

Each number represents a feature of the text's meaning. Similar texts have similar vectors.

**Dimensions:**
- OpenAI ada-002: 1536 dimensions
- OpenAI text-embedding-3-small: 1536 dimensions  
- OpenAI text-embedding-3-large: 3072 dimensions
- Sentence Transformers: 384, 768 dimensions

Higher dimensions = more nuanced understanding but slower/costlier.
            """,
            "use_cases": [
                {
                    "scenario": "Customer Support Knowledge Base",
                    "description": "Customer asks 'How do I reset my password?' - System finds articles about password recovery, account access, login issues (even if exact phrase isn't present)",
                    "embedding_model": "text-embedding-ada-002 (1536 dims)",
                    "why": "Good balance of accuracy and cost for general text"
                },
                {
                    "scenario": "Legal Document Search",
                    "description": "Lawyer searches 'employment termination' - Finds contracts with 'dismissal', 'severance', 'end of employment' (semantic matches)",
                    "embedding_model": "text-embedding-3-large (3072 dims)",
                    "why": "Legal text requires high precision - more dimensions capture subtle differences"
                },
                {
                    "scenario": "E-commerce Product Search",
                    "description": "User searches 'laptop for programming' - Finds high-RAM developer laptops, workstations (understands intent)",
                    "embedding_model": "text-embedding-ada-002 (1536 dims)",
                    "why": "Product descriptions are shorter - 1536 dims sufficient"
                }
            ],
            "best_practices": [
                "Use consistent embedding model for indexing and querying (don't mix models)",
                "Store embedding model name in metadata for future reference",
                "Test different models with your specific content type",
                "Consider cost: ada-002 ($0.0001/1K tokens) vs 3-large ($0.00013/1K tokens)",
                "Batch embed documents for efficiency (up to 2048 texts at once)",
                "Pre-process text: remove HTML, normalize whitespace, handle special characters"
            ],
            "beginner_tip": "Think of embeddings like GPS coordinates for words - similar words are 'close together' in meaning-space.",
            "intermediate_tip": "Embedding quality depends on training data. OpenAI models excel at general text, but domain-specific models (legal, medical) may perform better for specialized content.",
            "advanced_tip": "Consider fine-tuning embeddings on your domain data, or use contrastive learning to improve relevance for your specific use case."
        },
        
        "similarity_metrics": {
            "title": "Similarity Metrics: Cosine vs Euclidean vs Dot Product",
            "explanation": """
**What are Similarity Metrics?**

Metrics measure "how similar" two vectors are. Pinecone supports three:

**1. COSINE SIMILARITY** (Most Common ✅)
- Measures *angle* between vectors (ignores magnitude)
- Range: -1 (opposite) to +1 (identical)
- **When to use**: Text embeddings, normalized vectors
- **Why**: Text length doesn't matter - "dog" and "The quick brown dog" can still match well

**Formula**: cos(θ) = (A · B) / (||A|| × ||B||)

**Example:**
```
Vector A: [0.5, 0.5, 0.7]  (short document)
Vector B: [5.0, 5.0, 7.0]  (long document with same content)
Cosine: 1.0 (perfect match - same direction/meaning)
Euclidean: 10.4 (very different - sees size difference)
```

**2. EUCLIDEAN DISTANCE**
- Measures *straight-line distance* between points
- Range: 0 (identical) to ∞ (very different)
- **When to use**: Normalized vectors, image embeddings, coordinate data
- **Why**: Magnitude matters - useful when vector length has meaning

**Formula**: √[(A₁-B₁)² + (A₂-B₂)² + ... + (Aₙ-Bₙ)²]

**3. DOT PRODUCT**
- Measures both angle AND magnitude
- Range: -∞ to +∞
- **When to use**: Pre-normalized vectors, recommendation systems
- **Why**: Faster than cosine, but vectors must be normalized first

**Formula**: A · B = A₁B₁ + A₂B₂ + ... + AₙBₙ
            """,
            "use_cases": [
                {
                    "metric": "cosine",
                    "scenario": "Document Search (Legal, Customer Support)",
                    "reason": "Document length varies widely. You want semantic meaning, not text length to affect results.",
                    "example": "Finding 'contract breach' should match both 2-page summaries and 50-page agreements equally"
                },
                {
                    "metric": "euclidean",
                    "scenario": "Image Similarity (Product Images)",
                    "reason": "Image embeddings are pre-normalized. Euclidean works well for finding visually similar products.",
                    "example": "Finding similar product photos where color/texture matters"
                },
                {
                    "metric": "dotproduct",
                    "scenario": "Recommendation Systems",
                    "reason": "User/item embeddings are normalized. Dot product is faster and equivalent to cosine.",
                    "example": "Recommending products based on user purchase history"
                }
            ],
            "decision_tree": {
                "question": "Are your vectors normalized (all have length = 1)?",
                "yes": {
                    "next": "Use **dot product** (fastest) or **euclidean** (standard)"
                },
                "no": {
                    "next": "Are you using text embeddings from OpenAI/similar?",
                    "yes": "Use **cosine** (handles varying text lengths)",
                    "no": "Do you care about vector magnitude?",
                    "magnitude_matters": "Use **euclidean**",
                    "magnitude_irrelevant": "Use **cosine**"
                }
            },
            "best_practices": [
                "For OpenAI embeddings: Always use COSINE (default and recommended)",
                "For image embeddings: Use EUCLIDEAN or DOT PRODUCT (images are pre-normalized)",
                "Never mix metrics: If you index with cosine, query with cosine",
                "Test all three with your data - sometimes results surprise you",
                "Cosine is safest default if unsure (works 90% of cases)"
            ]
        },
        
        "hybrid_search": {
            "title": "Hybrid Search: Dense + Sparse Vectors",
            "explanation": """
**What is Hybrid Search?**

Hybrid search combines TWO search methods:
1. **Dense vectors** (semantic/meaning) - "What does this MEAN?"
2. **Sparse vectors** (keywords/exact matches) - "What does this SAY?"

**Why Use Hybrid Search?**

**Problem with Dense-Only:**
- Query: "GPT-4 vs GPT-3.5"
- Dense might miss exact model names (treats as generic "AI comparison")
- Result: Misses documents with specific model mentions

**Problem with Sparse-Only:**
- Query: "machine learning"  
- Sparse only finds exact phrase "machine learning"
- Misses: "neural networks", "deep learning", "AI models" (synonyms)

**Hybrid Solution:**
- Dense: Understands "AI models" ≈ "machine learning" (meaning)
- Sparse: Ensures exact keyword "GPT-4" is present (precision)
- **Result**: Best of both worlds - semantic + exact matching

**How It Works:**

1. **Dense Vector** (OpenAI ada-002): [0.023, -0.145, ..., 0.234] (1536 numbers)
2. **Sparse Vector** (TF-IDF): {indices: [42, 156, 1024], values: [0.8, 0.6, 0.4]}
   - Only important words get non-zero values
   - Index = word position in vocabulary
   - Value = importance weight (TF-IDF score)

3. **Combined Score**: 
   - Dense score: 0.85 (semantic similarity)
   - Sparse score: 0.92 (keyword match)
   - Final: 0.85 × 0.7 + 0.92 × 0.3 = 0.87 (weighted combination)

**Sparse Vector Generation (TF-IDF):**

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# Example document
text = "Contract termination requires 30 days notice"

# Generate sparse vector
vectorizer = TfidfVectorizer(max_features=100)  # Top 100 words
sparse = vectorizer.fit_transform([text])

# Result: 
# indices: [12, 45, 67, 89]  (positions of: contract, termination, days, notice)
# values: [0.52, 0.61, 0.38, 0.44]  (importance scores)
```
            """,
            "use_cases": [
                {
                    "scenario": "Technical Documentation Search",
                    "problem": "Query 'React useState hook' should find exact function names",
                    "solution": "Dense finds 'state management' concepts, Sparse ensures 'useState' is present",
                    "improvement": "40% better accuracy than dense-only for code docs"
                },
                {
                    "scenario": "Legal Contract Search",
                    "problem": "Must find specific clause numbers and legal terms exactly",
                    "solution": "Dense finds similar contract types, Sparse matches exact 'Section 4.2' references",
                    "improvement": "Reduces false positives by 60% vs dense-only"
                },
                {
                    "scenario": "Medical Records (HIPAA Compliant)",
                    "problem": "Need semantic search but must match exact medication names",
                    "solution": "Dense finds symptom descriptions, Sparse ensures drug names match exactly",
                    "improvement": "Critical for avoiding dangerous medication mix-ups"
                },
                {
                    "scenario": "E-commerce Product Search",
                    "problem": "User searches 'iPhone 15 Pro Max 256GB' - needs exact specs",
                    "solution": "Dense understands 'smartphone', Sparse matches exact model/storage",
                    "improvement": "75% fewer irrelevant results (no iPhone 13 mixing with 15)"
                }
            ],
            "when_to_use": {
                "use_hybrid": [
                    "Technical documentation with specific function/API names",
                    "Legal documents with clause references",
                    "Medical/pharmaceutical content with drug names",
                    "Product catalogs with model numbers/SKUs",
                    "Scientific papers with formula/chemical names",
                    "Code repositories with exact function names"
                ],
                "use_dense_only": [
                    "General customer support (broad questions)",
                    "Blog content / news articles",
                    "Social media posts",
                    "Marketing content",
                    "General Q&A systems"
                ]
            },
            "implementation": {
                "upload": "Set sparse_vector parameter in upsert (automatic with enhanced upload tool)",
                "query": "Both dense + sparse vectors sent together in query (automatic with query_namespaces tool)",
                "tuning": "Adjust dense_weight (0.7) vs sparse_weight (0.3) based on your use case"
            },
            "best_practices": [
                "Start with 70% dense, 30% sparse weights - tune based on results",
                "Use 100 TF-IDF features for sparse (good balance)",
                "Remove stop words ('the', 'a', 'is') from sparse vectors",
                "Test hybrid vs dense-only on your data - measure precision/recall",
                "Hybrid adds ~15% cost (sparse vector storage) but often worth it",
                "Monitor query latency - hybrid is slightly slower (~10-20ms)"
            ]
        },
        
        "namespaces": {
            "title": "Namespaces: Multi-Tenancy & Data Isolation",
            "explanation": """
**What are Namespaces?**

Namespaces are **isolated containers** within a Pinecone index. Think of them as "folders" or "buckets" that keep vectors separated.

**Key Properties:**
- Vectors in different namespaces don't interfere with each other
- You can query one namespace, multiple namespaces, or all at once
- Perfect for multi-tenant applications (one namespace per customer)
- Free to create, delete, and manage

**Architecture:**

```
Pinecone Index: "my-documents"
├── Namespace: "user_42_legal"
│   ├── Vector 1: contract_2024.pdf chunk 1
│   ├── Vector 2: contract_2024.pdf chunk 2
│   └── Vector 3: agreement.docx chunk 1
├── Namespace: "user_42_finance"  
│   ├── Vector 4: invoice_jan.pdf chunk 1
│   └── Vector 5: receipt.pdf chunk 1
└── Namespace: "user_43_legal" (different user)
    └── Vector 6: user43_contract.pdf chunk 1
```

**Query Options:**

1. **Single Namespace**: `query(namespace="user_42_legal")` - Only legal docs for user 42
2. **Multi-Namespace**: `query_namespaces(["user_42_legal", "user_42_finance"])` - Cross-category search
3. **All Namespaces**: `query(namespace="")` - Search everything (not recommended for multi-tenant)

**Naming Strategies:**

**Pattern 1: User-Based (Recommended for SaaS)**
```
Format: user_{user_id}_{category}
Examples:
- user_42_legal
- user_42_finance  
- user_43_legal

Benefits:
✅ Perfect data isolation per user
✅ Easy to delete all user data (GDPR compliance)
✅ Can query across user's categories
✅ Scales to millions of users
```

**Pattern 2: Category-Based (Recommended for Single-Tenant)**
```
Format: {category}_{subcategory}
Examples:
- legal_contracts
- legal_policies
- finance_invoices
- hr_handbook

Benefits:
✅ Simple category organization
✅ Easy cross-category search
✅ Good for internal knowledge bases
```

**Pattern 3: Hybrid (Recommended for Enterprise)**
```
Format: {tenant}_{department}_{category}
Examples:
- acme_legal_contracts
- acme_finance_invoices
- techcorp_legal_contracts

Benefits:
✅ Multi-tenant SaaS with departments
✅ Enterprise-grade isolation
✅ Flexible querying (by tenant, department, or category)
```

**Pattern 4: Time-Based**
```
Format: {category}_{year}_{month}
Examples:
- documents_2024_11
- documents_2024_12
- documents_2025_01

Benefits:
✅ Easy to archive old data
✅ Fast queries on recent documents
✅ Optimize storage (delete old namespaces)
```
            """,
            "use_cases": [
                {
                    "scenario": "Multi-Tenant SaaS (Law Firm Software)",
                    "namespace_pattern": "firm_{firm_id}_{category}",
                    "example": "firm_123_contracts, firm_123_cases, firm_456_contracts",
                    "reasoning": "Each law firm's data completely isolated. Firm 123 can't see Firm 456's documents.",
                    "query_strategy": "Query only namespaces starting with firm_123_ for that customer"
                },
                {
                    "scenario": "Enterprise Knowledge Base",
                    "namespace_pattern": "{department}_{type}",
                    "example": "legal_policies, hr_handbook, engineering_docs",
                    "reasoning": "Departments can search their own docs or cross-department with permissions",
                    "query_strategy": "User in legal can query legal_* namespaces, admins query all"
                },
                {
                    "scenario": "E-commerce Product Catalog",
                    "namespace_pattern": "{category}_{brand}",
                    "example": "electronics_apple, electronics_samsung, clothing_nike",
                    "reasoning": "Category-first organization with brand subdivision for faceted search",
                    "query_strategy": "Filter by category, then narrow by brand if needed"
                },
                {
                    "scenario": "Healthcare (HIPAA Compliant)",
                    "namespace_pattern": "patient_{patient_id}_{record_type}",
                    "example": "patient_789_medical, patient_789_billing, patient_789_prescriptions",
                    "reasoning": "Complete patient data isolation for HIPAA compliance. Easy to export/delete per patient.",
                    "query_strategy": "Only query namespaces for authenticated patient"
                }
            ],
            "best_practices": [
                "Keep namespace names short (max 50 chars) - faster queries",
                "Use consistent naming convention across your app",
                "Don't create too many namespaces (thousands OK, millions slow)",
                "Empty namespaces have no cost - clean up periodically",
                "Use metadata filters WITHIN namespaces for fine-grained filtering",
                "Default namespace = '' (empty string) - use for global/public data",
                "Test cross-namespace queries - they're powerful but need tuning"
            ],
            "anti_patterns": [
                "❌ DON'T: One namespace per document (namespace_doc123) - Use metadata instead",
                "❌ DON'T: Mix user data in same namespace - Security risk",
                "❌ DON'T: Use special characters in names (%, #, @) - Stick to alphanumeric + underscore",
                "❌ DON'T: Create namespaces on-the-fly without validation - Validate user input first"
            ]
        },
        
        "metadata_filtering": {
            "title": "Metadata Filtering: Advanced Query Refinement",
            "explanation": """
**What is Metadata Filtering?**

Metadata filtering lets you add **structured filters** to semantic search. Instead of just "find similar documents", you can say "find similar documents WHERE year >= 2024 AND category = 'legal'".

**How It Works:**

Every vector in Pinecone can have metadata (key-value pairs):

```python
{
    "id": "vec_123",
    "values": [0.023, -0.145, ...],  # Dense vector
    "metadata": {
        "document": "contract.pdf",
        "category": "legal",
        "year": 2024,
        "author": "John Smith",
        "tags": ["important", "confidential"],
        "file_size": 245000,
        "uploaded_at": "2024-11-30T10:00:00Z"
    }
}
```

**Query with Filters:**

```python
query_result = index.query(
    vector=[0.1, 0.2, ...],
    top_k=10,
    filter={
        "category": {"$eq": "legal"},
        "year": {"$gte": 2024},
        "author": {"$in": ["John Smith", "Jane Doe"]}
    }
)
```

**How It's Different from Metadata-Only Search:**

1. **Semantic + Filter**: Finds *similar* documents that match filters
2. **Filter-Only**: Finds *any* documents that match filters (use fetch_by_metadata tool)

**Supported Operators:**

| Operator | Meaning | Example |
|----------|---------|---------|
| `$eq` | Equals | `{"category": {"$eq": "legal"}}` |
| `$ne` | Not equals | `{"status": {"$ne": "archived"}}` |
| `$gt` | Greater than | `{"year": {"$gt": 2023}}` |
| `$gte` | Greater than or equal | `{"price": {"$gte": 100}}` |
| `$lt` | Less than | `{"file_size": {"$lt": 1000000}}` |
| `$lte` | Less than or equal | `{"rating": {"$lte": 5}}` |
| `$in` | In array | `{"author": {"$in": ["John", "Jane"]}}` |
| `$nin` | Not in array | `{"tags": {"$nin": ["spam", "deleted"]}}` |

**Complex Filters (AND logic):**

```python
filter = {
    "category": {"$eq": "legal"},
    "year": {"$gte": 2024},
    "author": {"$in": ["John", "Jane"]},
    "tags": {"$nin": ["archived"]},
    "file_size": {"$lt": 5000000}
}
# Returns: Legal docs from 2024+, by John or Jane, not archived, under 5MB
```

**Nested Metadata (JSON):**

```python
metadata = {
    "document": "contract.pdf",
    "client": {
        "name": "ACME Corp",
        "id": 12345,
        "tier": "enterprise"
    }
}

# Query nested fields:
filter = {"client.tier": {"$eq": "enterprise"}}
```
            """,
            "use_cases": [
                {
                    "scenario": "Legal Document Compliance Search",
                    "query": "Find contracts from 2024 by specific attorneys for ACME client",
                    "filter": {
                        "category": {"$eq": "contracts"},
                        "year": {"$gte": 2024},
                        "author": {"$in": ["Attorney A", "Attorney B"]},
                        "client_name": {"$eq": "ACME Corp"},
                        "status": {"$ne": "draft"}
                    },
                    "benefit": "Narrow 10,000 contracts to 50 relevant ones before semantic search"
                },
                {
                    "scenario": "E-commerce Product Filter",
                    "query": "Find similar products under $500 in electronics, in stock",
                    "filter": {
                        "category": {"$eq": "electronics"},
                        "price": {"$lte": 500},
                        "in_stock": {"$eq": true},
                        "brand": {"$in": ["Sony", "Samsung", "LG"]}
                    },
                    "benefit": "Show only affordable, available alternatives to user's query"
                },
                {
                    "scenario": "Customer Support Ticket Search",
                    "query": "Find similar open tickets for premium customers",
                    "filter": {
                        "status": {"$eq": "open"},
                        "customer_tier": {"$eq": "premium"},
                        "created_at": {"$gte": "2024-11-01"},
                        "tags": {"$nin": ["spam", "resolved"]}
                    },
                    "benefit": "Support agents find relevant open issues for VIP customers only"
                },
                {
                    "scenario": "Healthcare Patient Records",
                    "query": "Find patients with similar symptoms, diabetic, age 40-60",
                    "filter": {
                        "diagnosis": {"$in": ["diabetes_type1", "diabetes_type2"]},
                        "age": {"$gte": 40, "$lte": 60},
                        "status": {"$eq": "active"},
                        "last_visit": {"$gte": "2024-01-01"}
                    },
                    "benefit": "HIPAA-compliant search within specific patient cohort"
                }
            ],
            "best_practices": [
                "Index only filterable fields - Don't waste metadata on non-searchable data",
                "Use consistent data types (string, int, float, bool, array)",
                "Keep metadata under 40KB per vector (Pinecone limit)",
                "Use $in operator for multi-value fields instead of OR queries",
                "Combine filters with namespaces for double isolation (namespace + metadata)",
                "Test filter performance - complex filters can slow queries",
                "Store filter-friendly values: Use 2024 (int) not 'Year 2024' (string)",
                "Use ISO dates for time-based filters: '2024-11-30T10:00:00Z'"
            ],
            "performance_tips": [
                "Filters with $eq are fastest (direct lookup)",
                "$in with small arrays (< 10 items) performs well",
                "Avoid $ne when possible (excludes require scanning)",
                "Range queries ($gt, $lt) are slower than $eq",
                "Combine namespace + filter = optimal performance",
                "Pre-filter with namespace, then metadata filter within namespace"
            ]
        },
        
        "chunk_optimization": {
            "title": "Chunk Size Optimization: Balancing Context vs Precision",
            "explanation": """
**What is Chunking?**

Large documents must be split into smaller "chunks" because:
1. Embedding models have token limits (8,191 tokens for ada-002)
2. Smaller chunks = more precise matching
3. You return chunks, not entire documents

**The Chunking Dilemma:**

**Too Small (100-200 chars):**
- ✅ Precise matching (exact sentences)
- ❌ Loses context (no surrounding information)
- ❌ Too many chunks (expensive, slow)
- Example: "30 days notice" (what requires notice? Lost context)

**Too Large (2000-5000 chars):**
- ✅ Preserves context (full sections)
- ❌ Diluted matching (too many topics per chunk)
- ❌ Returns too much text (user must re-read everything)
- Example: 5-page chunk with 20 topics mixed together

**Optimal Balance (500-1000 chars):**
- ✅ Good context (few paragraphs)
- ✅ Focused topic per chunk
- ✅ Reasonable number of chunks
- ✅ Manageable return text
- **Our default: 800 chars** (sweet spot for most content)

**Overlap Strategy:**

Chunks should overlap to avoid cutting sentences in half:

```
Chunk 1: [0........800] chars
Chunk 2:       [780.......1580] chars (20 char overlap)
Chunk 3:              [1560......2360] chars (20 char overlap)
```

**Why Overlap?**
- Prevents losing context at chunk boundaries
- Ensures important phrases aren't split between chunks
- Small overlap (20-50 chars) is enough

**Visual Example:**

```
Document: "The contract requires 30 days notice. Termination must be in writing. 
           Both parties must agree to terms."

Chunk 1 (800 chars): 
"The contract requires 30 days notice. Termination must be in writing."

Chunk 2 (800 chars, 20 overlap):
"must be in writing. Both parties must agree to terms."
           ^overlap^

Without overlap, "must be in writing" would be split awkwardly.
```

**Intelligent Chunking Strategies:**

**1. Sentence Boundary Chunking** (Best for general text)
```python
# Don't cut mid-sentence
def chunk_by_sentence(text, target_size=800):
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < target_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + ". "
    
    return chunks
```

**2. Paragraph Chunking** (Best for structured docs)
```python
# Keep paragraphs together
chunks = text.split('\\n\\n')
# Then merge small paragraphs to reach target size
```

**3. Semantic Chunking** (Advanced - best for technical docs)
```python
# Use NLP to detect topic shifts, chunk at natural boundaries
# Libraries: LangChain TextSplitter, NLTK
```
            """,
            "use_cases": [
                {
                    "content_type": "Legal Contracts",
                    "recommended_size": "1000-1500 chars",
                    "overlap": "50 chars",
                    "reasoning": "Legal clauses are dense and need full context. Longer chunks preserve clause structure.",
                    "example": "Entire 'Termination Clause' in one chunk, not split across chunks"
                },
                {
                    "content_type": "Customer Support FAQs",
                    "recommended_size": "300-500 chars",
                    "overlap": "20 chars",
                    "reasoning": "FAQs are short Q&A pairs. Keep each answer as one chunk.",
                    "example": "Q: How do I reset password? A: Go to settings... (complete answer in one chunk)"
                },
                {
                    "content_type": "Technical Documentation (API docs)",
                    "recommended_size": "500-800 chars",
                    "overlap": "30 chars",
                    "reasoning": "Code examples need context but not too much mixing. One function/endpoint per chunk.",
                    "example": "Entire 'GET /api/users' endpoint description in one chunk"
                },
                {
                    "content_type": "Blog Posts / News Articles",
                    "recommended_size": "800-1200 chars",
                    "overlap": "50 chars",
                    "reasoning": "Narrative flow matters. Keep 2-3 paragraphs together for story coherence.",
                    "example": "Introduction paragraph + first main point together"
                },
                {
                    "content_type": "Scientific Papers",
                    "recommended_size": "1200-1500 chars",
                    "overlap": "100 chars",
                    "reasoning": "Dense technical content requires significant context. Abstract/methods/results as separate chunks.",
                    "example": "Entire 'Methods' section in 1-2 chunks, not fragmented"
                },
                {
                    "content_type": "Chat Logs / Conversations",
                    "recommended_size": "500-700 chars",
                    "overlap": "50 chars",
                    "reasoning": "Conversational context matters. Keep 5-10 message exchanges together.",
                    "example": "Customer question + support response + follow-up in one chunk"
                }
            ],
            "testing_methodology": {
                "step1": "Start with 800 chars (default)",
                "step2": "Test with 10-20 representative documents",
                "step3": "Measure: Do results include full answer or cut off context?",
                "step4": "Adjust: Too precise (missing context)? Increase size. Too broad? Decrease.",
                "step5": "Monitor: Track top_k parameter - if users always need 10+ results, chunks too small"
            },
            "best_practices": [
                "Default to 800 chars with 20-50 char overlap (works 80% of cases)",
                "For highly structured content (contracts, code), use larger chunks (1000-1500)",
                "For short Q&A content, use smaller chunks (300-500)",
                "Test different sizes - quality improvement is often measurable",
                "Store chunk_size in metadata for debugging",
                "Consider smart chunking libraries (LangChain, LlamaIndex) for advanced cases",
                "Monitor chunk retrieval metrics - if users need many chunks per query, chunks too small"
            ],
            "anti_patterns": [
                "❌ DON'T: Use same chunk size for all content types",
                "❌ DON'T: Chunk at exact char count (might split mid-word)",
                "❌ DON'T: Skip overlap (loses boundary context)",
                "❌ DON'T: Make chunks too small (< 200 chars) - context loss",
                "❌ DON'T: Make chunks too large (> 2000 chars) - precision loss"
            ]
        },
        
        "user_permissions": {
            "title": "User Permissions: Multi-Tenant Data Isolation Strategies",
            "explanation": """
**The Challenge:**

Pinecone doesn't have built-in user permissions. YOU must implement access control to prevent User A from seeing User B's data.

**Three Permission Models:**

**1. NAMESPACE-BASED (Recommended for SaaS) ✅**

Each user gets their own namespaces:

```
user_42_documents   (User 42's private docs)
user_42_shared      (User 42's shared docs)
user_43_documents   (User 43's private docs)
global_knowledge    (Public docs - all users)
```

**Access Control:**
```python
# Backend enforces: user can only query their namespaces
allowed_namespaces = [
    f"user_{user_id}_documents",
    f"user_{user_id}_shared",
    "global_knowledge"  # Everyone can access
]

# Query restricted to allowed namespaces
result = index.query(
    vector=embedding,
    namespace=allowed_namespaces[0]  # or multi-namespace query
)
```

**Pros:**
- ✅ Complete data isolation (user data physically separated)
- ✅ Easy to delete all user data (GDPR compliance)
- ✅ Fast queries (only search user's namespaces)
- ✅ Simple to implement

**Cons:**
- ❌ Can't share individual documents easily (must copy to shared namespace)
- ❌ Namespace proliferation if many users

---

**2. METADATA-BASED (Recommended for Enterprise) ✅**

All vectors in one namespace, filter by user_id metadata:

```python
# Upload with owner metadata
vector = {
    "id": "doc123",
    "values": [...],
    "metadata": {
        "owner_user_id": 42,
        "visibility": "private",  # or "public", "team"
        "shared_with": [43, 44],  # Optional: specific user sharing
        "document": "contract.pdf"
    }
}

# Query with metadata filter
result = index.query(
    vector=embedding,
    namespace="documents",
    filter={
        "$or": [
            {"owner_user_id": {"$eq": user_id}},  # User's own docs
            {"visibility": {"$eq": "public"}},     # Public docs
            {"shared_with": {"$in": [user_id]}}   # Shared with user
        ]
    }
)
```

**Pros:**
- ✅ Flexible sharing (document-level permissions)
- ✅ Complex permission models (public, private, team, individual sharing)
- ✅ Fewer namespaces to manage

**Cons:**
- ❌ Metadata filtering adds query latency
- ❌ Must carefully validate filters (security risk if wrong)
- ❌ Can't prevent unauthorized queries at storage level

---

**3. HYBRID (Recommended for Complex Apps) 🚀**

Combine namespaces + metadata:

```
Namespaces:
- user_42_private       (User 42 only, no sharing)
- user_42_team          (User 42's team, metadata for fine-grained)
- company_public        (Everyone, metadata for categorization)

Metadata per vector:
{
    "owner_user_id": 42,
    "team_id": 5,
    "department": "legal",
    "visibility": "team",
    "access_level": "read_only"
}
```

**Query Strategy:**
```python
# Step 1: Determine allowed namespaces (coarse-grained)
if user.is_admin:
    namespaces = ["company_public", "user_*"]  # All namespaces
elif user.team_id == 5:
    namespaces = [f"user_{user.id}_*", f"team_{user.team_id}_*", "company_public"]
else:
    namespaces = [f"user_{user.id}_*", "company_public"]

# Step 2: Apply metadata filter (fine-grained)
filter = {
    "$or": [
        {"owner_user_id": {"$eq": user.id}},
        {"visibility": {"$eq": "public"}},
        {"access_level": {"$in": ["read", "read_write"]}}
    ]
}

# Query
result = query_namespaces(
    namespaces=namespaces,
    filter=filter
)
```

**Pros:**
- ✅ Best of both worlds (namespace isolation + flexible sharing)
- ✅ Performance (namespace reduces search space, metadata refines)
- ✅ Scalable (works for simple and complex permission models)

**Cons:**
- ❌ More complex to implement
- ❌ Requires careful namespace + metadata design
            """,
            "implementation_guide": {
                "step1": {
                    "title": "Choose Your Model",
                    "decision_tree": {
                        "simple_saas": "Use NAMESPACE-BASED (one namespace per user)",
                        "document_sharing": "Use METADATA-BASED (visibility + owner_user_id)",
                        "enterprise": "Use HYBRID (namespaces for teams, metadata for granular)"
                    }
                },
                "step2": {
                    "title": "Backend Validation (CRITICAL)",
                    "code": """
# NEVER trust client-side filtering!

@require_auth
def query_documents():
    user_id = request.user_id  # From JWT
    
    # ✅ CORRECT: Server enforces user's namespaces
    allowed_namespaces = get_user_namespaces(user_id)
    
    # ❌ WRONG: Client specifies namespaces (security hole!)
    # namespaces = request.json.get('namespaces')
    
    # Add user filter
    filter = request.json.get('filter', {})
    filter['owner_user_id'] = {'$eq': user_id}  # Force user isolation
    
    result = index.query(
        namespace=allowed_namespaces[0],
        filter=filter
    )
    return jsonify(result)
"""
                },
                "step3": {
                    "title": "Database Schema (Track Ownership)",
                    "tables": {
                        "vector_permissions": {
                            "columns": [
                                "vector_id (string)",
                                "owner_user_id (int)",
                                "visibility (enum: private, public, team)",
                                "shared_with_users (array)",
                                "shared_with_teams (array)",
                                "access_level (enum: read, write, admin)"
                            ],
                            "purpose": "Track who can access which vectors"
                        },
                        "namespace_permissions": {
                            "columns": [
                                "namespace (string)",
                                "owner_user_id (int)",
                                "team_id (int, optional)",
                                "visibility (enum: private, team, public)"
                            ],
                            "purpose": "Control namespace access"
                        }
                    }
                },
                "step4": {
                    "title": "Test Security (Penetration Testing)",
                    "tests": [
                        "Can User A query User B's private namespace? (Should fail)",
                        "Can User A modify filter to see User B's docs? (Should fail)",
                        "Can User A access global namespace? (Should succeed)",
                        "Can User A share document with User B? (Should succeed if owner)",
                        "Can Admin access all namespaces? (Should succeed with proper auth)"
                    ]
                }
            },
            "best_practices": [
                "ALWAYS validate namespace access on backend (never trust client)",
                "Use JWT tokens with user_id claim for authentication",
                "Log all queries with user_id for auditing (GDPR/HIPAA compliance)",
                "Implement 'shared_with' metadata for document-level sharing",
                "Use 'visibility' enum: private, team, public (clear semantics)",
                "Test permission logic thoroughly (penetration testing)",
                "Document your permission model clearly for developers",
                "Consider rate limiting per user to prevent abuse"
            ]
        },
        
        "performance_tuning": {
            "title": "Performance Tuning: Optimizing Query Speed & Costs",
            "explanation": """
**Pinecone Performance Factors:**

1. **Index Size**: More vectors = slower queries (but still fast)
2. **top_k Parameter**: More results = longer processing
3. **Metadata Filtering**: Complex filters add latency
4. **Hybrid Search**: Sparse vectors add ~10-20ms
5. **Multi-Namespace Queries**: Parallel but additive latency

**Latency Breakdown (Typical):**

```
Dense-only query (1M vectors, top_k=10):        30-50ms
+ Metadata filter ($eq):                        +5-10ms
+ Metadata filter (complex $in, $gt):           +10-30ms
+ Sparse vectors (hybrid):                      +10-20ms
+ Multi-namespace (3 namespaces):               +20-40ms
Total worst case:                               90-150ms
```

**Optimization Strategies:**

**1. Reduce top_k (Biggest Impact) 🚀**

```python
# ❌ SLOW: Requesting too many results
result = index.query(vector=emb, top_k=100)  # 100ms

# ✅ FAST: Request only what you need
result = index.query(vector=emb, top_k=10)   # 40ms

# Even better: Use pagination
page_1 = index.query(vector=emb, top_k=10, offset=0)
page_2 = index.query(vector=emb, top_k=10, offset=10)
```

**Rule of Thumb:**
- top_k=5: Fastest, good for precise matches
- top_k=10: Default, balanced speed/quality
- top_k=20: Slower, more diverse results
- top_k=50+: Slow, rarely needed

**2. Optimize Metadata Filters**

```python
# ❌ SLOW: Multiple $ne operators (exclusion scan)
filter = {
    "status": {"$ne": "archived"},
    "type": {"$ne": "draft"},
    "category": {"$ne": "spam"}
}

# ✅ FAST: Use $in with allowed values (inclusion)
filter = {
    "status": {"$in": ["active", "pending"]},
    "category": {"$in": ["legal", "finance"]}
}

# ❌ SLOW: Complex nested OR logic
filter = {
    "$or": [
        {"category": {"$eq": "A"}, "year": {"$gt": 2020}},
        {"category": {"$eq": "B"}, "year": {"$gt": 2021}}
    ]
}

# ✅ FAST: Simplify with $in
filter = {
    "category": {"$in": ["A", "B"]},
    "year": {"$gte": 2020}
}
```

**3. Namespace Pre-filtering**

```python
# ❌ SLOW: Query all namespaces with metadata filter
result = index.query(
    namespace="",  # All namespaces
    filter={"category": {"$eq": "legal"}}  # Filter after query
)

# ✅ FAST: Query specific namespace only
result = index.query(
    namespace="user_42_legal",  # Pre-filtered
    filter={}  # No additional filter needed
)

# Namespace reduces search space by 90%+ before semantic search
```

**4. Batch Queries**

```python
# ❌ SLOW: Sequential queries
for query in queries:
    result = index.query(vector=query)  # 50ms × 10 = 500ms

# ✅ FAST: Parallel batch queries
results = asyncio.gather(*[
    index.query(vector=q) for q in queries
])  # 50ms (parallelized)
```

**5. Reduce Dimensionality (Advanced)**

```python
# Smaller vectors = faster queries

# ❌ SLOWER: text-embedding-3-large (3072 dims)
model = "text-embedding-3-large"  # 60ms queries

# ✅ FASTER: text-embedding-ada-002 (1536 dims)
model = "text-embedding-ada-002"  # 40ms queries

# Trade-off: Slightly lower quality, 33% faster
```

**6. Index Tuning (Pod-Based Indexes)**

```python
# Pod type affects performance:

# p1 pods: Cheapest, good for small indexes (<100K vectors)
# p2 pods: Balanced, good for medium indexes (100K-1M vectors)
# s1 pods: Storage-optimized, cheapest per vector but slower queries

# Replicas: Add replicas for higher throughput
# 1 replica: 100 queries/sec
# 2 replicas: 200 queries/sec
# 4 replicas: 400 queries/sec
```
            """,
            "cost_optimization": {
                "strategies": [
                    {
                        "strategy": "Use Serverless Indexes for Variable Workloads",
                        "savings": "50-80% vs pod-based for bursty traffic",
                        "when": "Traffic varies greatly (nights/weekends low, weekdays high)"
                    },
                    {
                        "strategy": "Reduce Metadata Size",
                        "savings": "$5-10/month per 100K vectors",
                        "how": "Store only filterable fields in metadata, keep full document elsewhere"
                    },
                    {
                        "strategy": "Archive Old Namespaces",
                        "savings": "$20-50/month per 1M archived vectors",
                        "how": "Delete old namespaces (2023 data if only querying 2024+)"
                    },
                    {
                        "strategy": "Optimize Chunk Size",
                        "savings": "20-40% fewer vectors = 20-40% lower costs",
                        "how": "Use 1000 char chunks instead of 500 (if quality acceptable)"
                    }
                ],
                "pricing_example": {
                    "scenario": "100K vectors, 1536 dims, 10KB metadata",
                    "pod_based": "$70/month (p1.x1 pod)",
                    "serverless": "$10-30/month (depends on usage)",
                    "recommendation": "Serverless for most apps, pod if consistently high traffic"
                }
            },
            "monitoring": {
                "key_metrics": [
                    "Query latency (p50, p95, p99) - Target: <100ms p95",
                    "top_k distribution - Are users requesting too many results?",
                    "Filter complexity - How many operators per query?",
                    "Namespace hit rate - Are queries spread across namespaces?",
                    "Hybrid search usage - What % of queries use sparse vectors?",
                    "Error rate - Failed queries (timeout, quota exceeded)"
                ],
                "alerts": [
                    "p95 latency > 200ms (investigate slow queries)",
                    "Error rate > 1% (check quota, index health)",
                    "Avg top_k > 50 (users requesting too many results)",
                    "Storage growth > 10%/week (unexpected data growth)"
                ]
            }
        },
        
        "use_cases": {
            "title": "Common Use Cases & Implementation Patterns",
            "scenarios": [
                {
                    "use_case": "Customer Support Knowledge Base",
                    "description": "Search internal docs, FAQs, and past tickets to answer customer questions",
                    "config": {
                        "embedding_model": "text-embedding-ada-002",
                        "dimension": 1536,
                        "metric": "cosine",
                        "chunk_size": 500,
                        "chunk_overlap": 50,
                        "namespaces": ["faqs", "docs", "tickets_2024"],
                        "hybrid_search": False,
                        "metadata": ["category", "last_updated", "helpfulness_score", "tags"]
                    },
                    "query_pattern": "User asks question → Embed question → Query with metadata filter (category, recent docs) → Return top 5 answers",
                    "success_metrics": "80% questions answered without human intervention"
                },
                {
                    "use_case": "Legal Document Management (Law Firm)",
                    "description": "Search contracts, cases, policies with GDPR compliance",
                    "config": {
                        "embedding_model": "text-embedding-3-large",
                        "dimension": 3072,
                        "metric": "cosine",
                        "chunk_size": 1200,
                        "chunk_overlap": 100,
                        "namespaces": "firm_{firm_id}_{category}",
                        "hybrid_search": True,
                        "metadata": ["document_type", "client_id", "case_id", "year", "attorney", "confidential"]
                    },
                    "query_pattern": "Lawyer searches 'severance agreements 2024' → Hybrid search (semantic + keywords) → Filter by firm_id + year → Rank by relevance + recency",
                    "success_metrics": "90% relevant results in top 10, 0% data leakage between firms"
                },
                {
                    "use_case": "E-commerce Product Search",
                    "description": "Semantic product search with filters (price, brand, availability)",
                    "config": {
                        "embedding_model": "text-embedding-ada-002",
                        "dimension": 1536,
                        "metric": "cosine",
                        "chunk_size": 400,
                        "chunk_overlap": 0,
                        "namespaces": "{category}_{brand}",
                        "hybrid_search": True,
                        "metadata": ["price", "brand", "in_stock", "rating", "num_reviews", "color", "size"]
                    },
                    "query_pattern": "User: 'affordable laptop for programming' → Embed → Hybrid search → Filter: price<$1000, in_stock=true, category=laptops → Rerank by rating",
                    "success_metrics": "30% increase in click-through rate vs keyword search"
                },
                {
                    "use_case": "Healthcare Patient Records (HIPAA)",
                    "description": "Find similar patient cases, treatment plans, outcomes",
                    "config": {
                        "embedding_model": "text-embedding-ada-002",
                        "dimension": 1536,
                        "metric": "cosine",
                        "chunk_size": 800,
                        "chunk_overlap": 50,
                        "namespaces": "patient_{patient_id}_{record_type}",
                        "hybrid_search": True,
                        "metadata": ["patient_id", "diagnosis_code", "treatment", "outcome", "date", "provider_id"]
                    },
                    "query_pattern": "Doctor: 'Similar cases to patient 123 with diabetes complications' → Query patient_123_* namespaces → Filter by diagnosis → Return similar treatment plans",
                    "success_metrics": "HIPAA compliant (100% patient isolation), 70% faster diagnosis research"
                },
                {
                    "use_case": "Multi-Tenant SaaS (HR Software)",
                    "description": "Each company searches their own employee docs, policies, handbooks",
                    "config": {
                        "embedding_model": "text-embedding-ada-002",
                        "dimension": 1536,
                        "metric": "cosine",
                        "chunk_size": 700,
                        "chunk_overlap": 50,
                        "namespaces": "company_{company_id}_{department}",
                        "hybrid_search": False,
                        "metadata": ["company_id", "department", "document_type", "effective_date", "author"]
                    },
                    "query_pattern": "Employee: 'PTO policy' → Query company_42_hr namespace → Filter by company_id=42 (enforced) → Return policy docs",
                    "success_metrics": "100% data isolation, 0 cross-company data leaks, 60% reduced HR inquiries"
                }
            ]
        }
    }
    
    # Get explanation for requested topic
    topic_data = knowledge_base.get(topic, {})
    
    if not topic_data:
        return {
            "success": False,
            "error": f"Topic '{topic}' not found",
            "available_topics": list(knowledge_base.keys())
        }
    
    # Build response based on depth
    response = {
        "success": True,
        "topic": topic,
        "title": topic_data.get("title", ""),
        "explanation": topic_data.get("explanation", ""),
        "use_cases": topic_data.get("use_cases", []),
        "best_practices": topic_data.get("best_practices", [])
    }
    
    # Add context-specific recommendations if provided
    if context:
        response["context_analysis"] = f"Based on your situation: '{context}'"
        response["recommendations"] = _generate_recommendations(topic, context)
    
    # Add depth-appropriate content
    if depth == 'beginner' and 'beginner_tip' in topic_data:
        response["learning_tip"] = topic_data["beginner_tip"]
    elif depth == 'intermediate' and 'intermediate_tip' in topic_data:
        response["learning_tip"] = topic_data["intermediate_tip"]
    elif depth == 'advanced' and 'advanced_tip' in topic_data:
        response["learning_tip"] = topic_data["advanced_tip"]
    
    # Include examples if requested
    if include_examples and 'examples' in topic_data:
        response["examples"] = topic_data["examples"]
    
    # Add additional topic-specific data
    for key in ['decision_tree', 'implementation', 'when_to_use', 'anti_patterns', 
                'performance_tips', 'implementation_guide', 'cost_optimization', 
                'monitoring', 'scenarios']:
        if key in topic_data:
            response[key] = topic_data[key]
    
    return response


def _generate_recommendations(topic: str, context: str) -> list:
    """Generate context-specific recommendations"""
    recommendations = []
    
    context_lower = context.lower()
    
    # Pattern matching for recommendations
    if 'legal' in context_lower or 'law' in context_lower:
        recommendations.append("Use text-embedding-3-large (3072 dims) for legal - precision matters")
        recommendations.append("Implement hybrid search - exact clause references critical")
        recommendations.append("Larger chunks (1200-1500 chars) - legal clauses need full context")
        recommendations.append("Use firm_{firm_id}_{category} namespace pattern for multi-tenant isolation")
    
    if 'customer support' in context_lower or 'help' in context_lower:
        recommendations.append("Use text-embedding-ada-002 (1536 dims) - cost-effective for FAQs")
        recommendations.append("Smaller chunks (500 chars) - Q&A format works best")
        recommendations.append("Dense-only search acceptable - hybrid not critical for support")
        recommendations.append("Add 'helpfulness_score' metadata - surface best answers first")
    
    if 'healthcare' in context_lower or 'hipaa' in context_lower or 'patient' in context_lower:
        recommendations.append("Use patient_{patient_id}_* namespaces - HIPAA requires strict isolation")
        recommendations.append("Implement comprehensive audit logging - track all queries with user_id")
        recommendations.append("Hybrid search recommended - medical terms need exact matching")
        recommendations.append("Add diagnosis codes to metadata - enables cohort filtering")
    
    if 'ecommerce' in context_lower or 'product' in context_lower or 'shop' in context_lower:
        recommendations.append("Use hybrid search - users search by product codes/SKUs")
        recommendations.append("Add rich metadata: price, brand, stock, rating, reviews")
        recommendations.append("Namespace by category_brand - fast categorical browsing")
        recommendations.append("Smaller chunks (300-500) - product descriptions are concise")
    
    if '10000' in context or '10,000' in context or 'large' in context_lower:
        recommendations.append("Consider serverless index - cost-effective for 10K+ documents")
        recommendations.append("Use metadata filtering to reduce search space")
        recommendations.append("Monitor query performance - set alert if p95 > 100ms")
    
    return recommendations or ["Configure based on specific content type and user needs"]


print('[PINECONE STRATEGIES] Education tool loaded')

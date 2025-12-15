#!/usr/bin/env python3
"""Check if Pinecone deprecated functions are accessible"""
from tools.implementations import pinecone

print(f"Module has {len(dir(pinecone))} attributes")
print(f"__all__ has {len(pinecone.__all__)} items")
print()

deprecated = [
    'pinecone_explain_strategies',
    'pinecone_query_namespaces',
    'pinecone_fetch_by_metadata',
    'pinecone_search_summaries',
    'pinecone_get_vector_details',
    'pinecone_search_and_retrieve'
]

for func_name in deprecated:
    exists = hasattr(pinecone, func_name)
    in_all = func_name in pinecone.__all__
    callable_check = callable(getattr(pinecone, func_name, None))
    print(f"{func_name}:")
    print(f"  - exists: {exists}")
    print(f"  - in __all__: {in_all}")
    print(f"  - callable: {callable_check}")

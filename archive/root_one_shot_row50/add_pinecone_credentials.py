"""
Add Pinecone and Voyager (Embedding) credentials to AI_agents database

This script adds:
1. Pinecone API key for InHousePrint index
2. Voyager API key (for embeddings)
3. OpenAI credentials (also for embeddings)

Usage:
    python add_pinecone_credentials.py
"""

import sys
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from auth.user_auth import UserAuthManager
import json

def add_credentials():
    """Add Pinecone and Voyager credentials to database"""
    
    print("=" * 60)
    print("Adding Pinecone and Voyager Credentials to Database")
    print("=" * 60)
    
    # Initialize auth manager
    auth_manager = UserAuthManager()
    
    # User ID (usually 1 for master account)
    user_id = 1
    
    # ==================== PINECONE CREDENTIALS ====================
    print("\n1. Adding Pinecone credentials...")
    
    pinecone_api_key = "pcsk_4NZhAZ_8JpgceKPsfMsgRQGouKyfMWNZJ5SybzB72PCVVjVuK1HCkyc7uUd8RFAtDykyhr"
    pinecone_metadata = {
        "index_name": "inhouseprint",
        "environment": "us-east-1",  # Update if different
        "namespace": "",  # Default namespace
        "description": "InHousePrint vector database for document storage and semantic search"
    }
    
    result = auth_manager.store_platform_credential(
        user_id=user_id,
        platform='pinecone',
        credential_type='api_key',
        credential_key='PINECONE_API_KEY',
        credential_value=pinecone_api_key,
        metadata=pinecone_metadata
    )
    
    if result.get('success'):
        print(f"   ✅ Pinecone API key saved")
        print(f"   Index: {pinecone_metadata['index_name']}")
        print(f"   Environment: {pinecone_metadata['environment']}")
    else:
        print(f"   ❌ Failed: {result.get('error')}")
    
    # ==================== VOYAGER API KEY ====================
    print("\n2. Adding Voyager API key (embedding model)...")
    
    voyager_api_key = "pa-GOCp1HsNfuuvjXnHPumV5f6sD-YLQwQg5Fl3Fx2AlDm"
    voyager_metadata = {
        "provider": "InHousePrint",
        "model": "voyager",
        "dimensions": 1536,  # Standard embedding dimension
        "description": "Voyager embedding model API key for vector generation"
    }
    
    result = auth_manager.store_platform_credential(
        user_id=user_id,
        platform='voyager',
        credential_type='api_key',
        credential_key='VOYAGER_API_KEY',
        credential_value=voyager_api_key,
        metadata=voyager_metadata
    )
    
    if result.get('success'):
        print(f"   ✅ Voyager API key saved")
        print(f"   Provider: {voyager_metadata['provider']}")
        print(f"   Model: {voyager_metadata['model']}")
    else:
        print(f"   ❌ Failed: {result.get('error')}")
    
    # ==================== OPENAI EMBEDDINGS (BACKUP) ====================
    print("\n3. Adding OpenAI embeddings config (backup)...")
    
    # Get OpenAI key from environment or config
    import os
    from dotenv import load_dotenv
    
    env_master = Path(__file__).parent / '.env.master'
    if env_master.exists():
        load_dotenv(env_master)
    
    openai_api_key = os.getenv('OPENAI_API_KEY', '')
    
    if openai_api_key:
        openai_metadata = {
            "model": "text-embedding-ada-002",
            "dimensions": 1536,
            "description": "OpenAI embeddings - backup option for vector generation"
        }
        
        result = auth_manager.store_platform_credential(
            user_id=user_id,
            platform='openai_embeddings',
            credential_type='api_key',
            credential_key='OPENAI_API_KEY',
            credential_value=openai_api_key,
            metadata=openai_metadata
        )
        
        if result.get('success'):
            print(f"   ✅ OpenAI embeddings config saved")
            print(f"   Model: {openai_metadata['model']}")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
    else:
        print(f"   ⚠️  Skipped (no OPENAI_API_KEY in .env.master)")
    
    # ==================== SUMMARY ====================
    print("\n" + "=" * 60)
    print("CREDENTIALS SUMMARY")
    print("=" * 60)
    
    # Retrieve and display all vector DB credentials
    pinecone_creds = auth_manager.get_platform_credentials(user_id, 'pinecone')
    voyager_creds = auth_manager.get_platform_credentials(user_id, 'voyager')
    openai_creds = auth_manager.get_platform_credentials(user_id, 'openai_embeddings')
    
    print(f"\n✅ Pinecone: {len(pinecone_creds)} credentials stored")
    for key in pinecone_creds:
        print(f"   - {key}: {'*' * 20}{pinecone_creds[key][-8:]}")
    
    print(f"\n✅ Voyager: {len(voyager_creds)} credentials stored")
    for key in voyager_creds:
        print(f"   - {key}: {'*' * 20}{voyager_creds[key][-8:]}")
    
    if openai_creds:
        print(f"\n✅ OpenAI: {len(openai_creds)} credentials stored")
        for key in openai_creds:
            print(f"   - {key}: {'*' * 20}{openai_creds[key][-8:]}")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("""
1. Start the AI_agents server:
   cd C:\\Users\\gpoli\\GIT\\AI_agents
   BISTART

2. Open Vector Database UI:
   - Navigate to Vector Database module in browser
   - Credentials should auto-load from database
   - Test connection to verify

3. Upload test document:
   - Use Upload tab
   - Drag-drop a PDF/DOCX file
   - Verify processing completes

4. Test AI agent access:
   - Ask: "Search my documents for..."
   - AI will use pinecone_query_vectors tool
   - Verify results are returned

IMPORTANT: If you need to update credentials later, just run this script again.
It will update existing credentials without duplicating them.
""")

if __name__ == '__main__':
    try:
        add_credentials()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

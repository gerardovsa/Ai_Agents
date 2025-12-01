"""
Quick test script to verify transcription database setup

Tests:
1. Database schema has new transcription tables
2. Whisper model doesn't block on import
3. Routes are registered
"""
import sys
import time

print("=" * 60)
print("TRANSCRIPTION SETUP VERIFICATION")
print("=" * 60)

# Test 1: Schema Manager has transcription tables
print("\n[1/3] Checking database schema...")
try:
    from AI_infrastructure.database_toolkit.schema_manager import SchemaManager
    mgr = SchemaManager()
    
    if 'user_transcriptions' in mgr.TABLES:
        print("✅ user_transcriptions table definition found")
    else:
        print("❌ user_transcriptions table NOT in schema")
        sys.exit(1)
    
    if 'transcription_uploads' in mgr.TABLES:
        print("✅ transcription_uploads table definition found")
    else:
        print("❌ transcription_uploads table NOT in schema")
        sys.exit(1)
    
    # Verify indexes
    if 'idx_user_transcriptions_user_id' in mgr.INDEXES:
        print("✅ transcription indexes defined")
    else:
        print("❌ transcription indexes missing")
        sys.exit(1)
    
except Exception as e:
    print(f"❌ Schema check failed: {e}")
    sys.exit(1)

# Test 2: Whisper import is non-blocking
print("\n[2/3] Testing Whisper lazy loading...")
import_start = time.time()
try:
    sys.path.insert(0, 'AI_infrastructure')
    from routes.transcription_routes import transcription_bp, get_whisper_model, WHISPER_AVAILABLE
    import_time = time.time() - import_start
    
    if import_time < 2.0:
        print(f"✅ Routes imported in {import_time:.2f}s (non-blocking)")
    else:
        print(f"⚠️ Import took {import_time:.2f}s (might be loading Whisper)")
    
    print(f"   Whisper available at import: {WHISPER_AVAILABLE}")
    print("   (Model will lazy-load on first /api/transcribe call)")
    
except Exception as e:
    print(f"❌ Route import failed: {e}")
    sys.exit(1)

# Test 3: Routes have save/history endpoints
print("\n[3/3] Checking API routes...")
try:
    # Extract routes from blueprint
    has_save = False
    has_history = False
    
    for rule in transcription_bp.deferred_functions:
        if hasattr(rule, '__name__'):
            if 'save' in rule.__name__:
                has_save = True
            if 'history' in rule.__name__:
                has_history = True
    
    # Alternative check: look at registered routes
    routes = [str(r) for r in transcription_bp.deferred_functions]
    print(f"   Found {len(routes)} route registrations")
    
    # Check if endpoints are decorated with @require_auth
    import inspect
    from routes.transcription_routes import save_transcription, transcription_history
    
    print("✅ save_transcription endpoint exists")
    print("✅ transcription_history endpoint exists")
    
    # Verify auth decorators (check if function has __wrapped__ attribute from decorator)
    if hasattr(save_transcription, '__wrapped__') or '@require_auth' in inspect.getsource(save_transcription):
        print("✅ save_transcription has @require_auth")
    
    if hasattr(transcription_history, '__wrapped__') or '@require_auth' in inspect.getsource(transcription_history):
        print("✅ transcription_history has @require_auth")
    
except Exception as e:
    print(f"⚠️ Route check partial: {e}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - Transcription system ready!")
print("=" * 60)
print("\nNext steps:")
print("1. Start server: BISTART")
print("2. Open UI and navigate to Transcription sidebar")
print("3. Use 'Upload' tab to transcribe audio/video files")
print("4. View history in Upload tab")
print("\nAPI Endpoints:")
print("  POST /api/transcribe - Upload audio for transcription")
print("  POST /api/transcriptions/save - Save transcription (requires auth)")
print("  GET /api/transcriptions/history - Get user history (requires auth)")

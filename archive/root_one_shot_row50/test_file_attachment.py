"""
Smoke Test: File Attachment System
Tests file_encoding.py integration and content block generation
"""

import io
from werkzeug.datastructures import FileStorage
from AI_infrastructure.utils.file_encoding import (
    process_file_uploads,
    build_content_block,
    FileValidationError,
    guess_media_type,
    get_content_block_type
)

print("\n" + "="*80)
print("FILE ATTACHMENT SMOKE TEST")
print("="*80 + "\n")

# Test 1: Media type guessing
print("Test 1: Media Type Detection")
print("-" * 40)
tests = [
    ('image.jpg', 'image/jpeg'),
    ('photo.png', 'image/png'),
    ('doc.pdf', 'application/pdf'),
    ('pic.webp', 'image/webp'),
]
for filename, expected in tests:
    result = guess_media_type(filename)
    status = "✅" if result == expected else "❌"
    print(f"{status} {filename} → {result} (expected: {expected})")

# Test 2: Content block type
print("\nTest 2: Content Block Type")
print("-" * 40)
type_tests = [
    ('image/jpeg', 'image'),
    ('image/png', 'image'),
    ('application/pdf', 'document'),
]
for media_type, expected in type_tests:
    result = get_content_block_type(media_type)
    status = "✅" if result == expected else "❌"
    print(f"{status} {media_type} → {result}")

# Test 3: Build content block
print("\nTest 3: Build Content Block")
print("-" * 40)
try:
    test_data = b"This is test image data"
    block = build_content_block("test.jpg", test_data, "image/jpeg")
    
    print(f"✅ Block created successfully")
    print(f"   - Type: {block['type']}")
    print(f"   - Source type: {block['source']['type']}")
    print(f"   - Media type: {block['source']['media_type']}")
    print(f"   - Data length: {len(block['source']['data'])} chars (base64)")
    print(f"   - Has all required fields: {all(k in block for k in ['type', 'source'])}")
except Exception as e:
    print(f"❌ Failed: {e}")

# Test 4: Process file uploads (Flask-like)
print("\nTest 4: Process File Uploads")
print("-" * 40)
try:
    # Create mock files
    files = [
        FileStorage(
            stream=io.BytesIO(b"PNG image content"),
            filename="photo.png",
            content_type="image/png"
        ),
        FileStorage(
            stream=io.BytesIO(b"PDF document content"),
            filename="document.pdf",
            content_type="application/pdf"
        ),
    ]
    
    blocks = process_file_uploads(files)
    
    print(f"✅ Processed {len(blocks)} file(s)")
    for i, block in enumerate(blocks):
        print(f"\n   File {i+1}:")
        print(f"   - Type: {block['type']}")
        print(f"   - Media: {block['source']['media_type']}")
        print(f"   - Base64 data: {len(block['source']['data'])} chars")
        
except Exception as e:
    print(f"❌ Failed: {e}")

# Test 5: File size validation
print("\nTest 5: File Size Validation")
print("-" * 40)
try:
    # Try with oversized file (should fail)
    large_data = b"X" * (33 * 1024 * 1024)  # 33MB (over 32MB limit)
    block = build_content_block("huge.jpg", large_data, "image/jpeg")
    print("❌ Should have rejected oversized file!")
except FileValidationError as e:
    print(f"✅ Correctly rejected oversized file: {str(e)[:50]}...")

# Test 6: Check route integration
print("\nTest 6: Route Integration Check")
print("-" * 40)
try:
    from AI_infrastructure.routes.agent_routes_v4 import agent_bp
    print(f"✅ agent_routes_v4 imports successfully")
    print(f"✅ Blueprint name: {agent_bp.name}")
    
    # Check if process_file_uploads is imported in routes
    import AI_infrastructure.routes.agent_routes_v4 as routes_module
    if hasattr(routes_module, 'process_file_uploads'):
        print(f"✅ process_file_uploads available in routes")
    else:
        print(f"⚠️  process_file_uploads not directly imported (may use qualified import)")
        
except Exception as e:
    print(f"❌ Route integration issue: {e}")

# Test 7: Anthropic API format validation
print("\nTest 7: Anthropic API Format Validation")
print("-" * 40)
test_file = FileStorage(
    stream=io.BytesIO(b"Test image"),
    filename="test.jpg",
    content_type="image/jpeg"
)
blocks = process_file_uploads([test_file])
block = blocks[0]

# Check required fields for Anthropic Messages API
required_fields = {
    'top_level': ['type', 'source'],
    'source': ['type', 'media_type', 'data']
}

all_valid = True
for key in required_fields['top_level']:
    if key not in block:
        print(f"❌ Missing required field: {key}")
        all_valid = False

if 'source' in block:
    for key in required_fields['source']:
        if key not in block['source']:
            print(f"❌ Missing required source field: {key}")
            all_valid = False

if all_valid:
    print("✅ All required Anthropic API fields present")
    print("✅ Format matches official docs:")
    print("   {")
    print(f"     'type': '{block['type']}',")
    print("     'source': {")
    print(f"       'type': '{block['source']['type']}',")
    print(f"       'media_type': '{block['source']['media_type']}',")
    print(f"       'data': '<base64_string>'")
    print("     }")
    print("   }")

print("\n" + "="*80)
print("SMOKE TEST COMPLETE")
print("="*80 + "\n")

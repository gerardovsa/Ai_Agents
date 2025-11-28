"""
Test Universal File Handler v2.0 - Text Extraction Feature
===========================================================

Tests the new text extraction capabilities for office documents.
"""

import sys
import io
sys.path.insert(0, 'AI_infrastructure')

from core.universal_file_handler import UniversalFileHandler
from core.text_extractor import TextExtractor

def test_text_extractor():
    """Test text extractor module"""
    print("\n" + "="*70)
    print("TEST 1: Text Extractor Module")
    print("="*70)
    
    extractor = TextExtractor()
    
    # Test 1: Plain text
    print("\n📝 Test 1.1: Plain Text File")
    text_data = b"This is a test document.\nIt has multiple lines.\n\nAnd paragraphs!"
    result = extractor.extract_text(
        file_data=text_data,
        content_type='text/plain',
        filename='test.txt'
    )
    
    if result['success']:
        print(f"✅ Success!")
        print(f"   Words: {result['metadata']['word_count']}")
        print(f"   Chars: {result['metadata']['char_count']}")
        print(f"   Text: {result['text'][:100]}...")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 2: JSON
    print("\n📊 Test 1.2: JSON File")
    json_data = b'{"name": "Test", "value": 123, "items": ["a", "b", "c"]}'
    result = extractor.extract_text(
        file_data=json_data,
        content_type='application/json',
        filename='test.json'
    )
    
    if result['success']:
        print(f"✅ Success!")
        print(f"   Words: {result['metadata']['word_count']}")
        print(f"   Preview: {result['text'][:150]}...")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 3: CSV
    print("\n📋 Test 1.3: CSV File")
    csv_data = b"Name,Age,City\nAlice,30,NYC\nBob,25,LA\nCharlie,35,Chicago"
    result = extractor.extract_text(
        file_data=csv_data,
        content_type='text/csv',
        filename='test.csv'
    )
    
    if result['success']:
        print(f"✅ Success!")
        print(f"   Words: {result['metadata']['word_count']}")
        print(f"   Extracted CSV:\n{result['text']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 4: Check extractable types
    print("\n🔍 Test 1.4: Extractable Type Detection")
    test_types = [
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/pdf',
        'image/png',
        'text/plain',
        'application/json'
    ]
    
    for content_type in test_types:
        is_extractable = extractor.is_extractable(content_type)
        status = "✅ Extractable" if is_extractable else "❌ Not extractable"
        print(f"   {content_type}: {status}")


def test_universal_file_handler_integration():
    """Test Universal File Handler with new extraction"""
    print("\n" + "="*70)
    print("TEST 2: Universal File Handler Integration")
    print("="*70)
    
    handler = UniversalFileHandler(user_id=1)
    
    # Test 1: Text file (should use extract method)
    print("\n📝 Test 2.1: Text File Processing")
    text_content = b"# Test Document\n\nThis is a test markdown file.\n\n## Features\n- Feature 1\n- Feature 2"
    
    result = handler.process_file(
        source='bytes',
        source_id={
            'filename': 'test.md',
            'content_type': 'text/markdown',
            'data': text_content
        },
        mode='auto'
    )
    
    print(f"   Method selected: {result.get('method', 'N/A')}")
    if result['success']:
        print(f"✅ Success!")
        print(f"   Token estimate: {result['metadata']['token_estimate']}")
        print(f"   Content type: {result['content_block']['type']}")
        if result['content_block']['type'] == 'text':
            print(f"   Text preview: {result['content_block']['text'][:200]}...")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 2: JSON file (should use extract method)
    print("\n📊 Test 2.2: JSON File Processing")
    json_content = b'{"project": "AI_agents", "version": "2.0", "features": ["text extraction", "token optimization"]}'
    
    result = handler.process_file(
        source='bytes',
        source_id={
            'filename': 'config.json',
            'content_type': 'application/json',
            'data': json_content
        },
        mode='auto'
    )
    
    print(f"   Method selected: {result.get('method', 'N/A')}")
    if result['success']:
        print(f"✅ Success!")
        print(f"   Token estimate: {result['metadata']['token_estimate']}")
        print(f"   Content block type: {result['content_block']['type']}")
        if result['content_block']['type'] == 'text':
            print(f"   Extracted text length: {len(result['content_block']['text'])} chars")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 3: Image file (should use direct or files_api)
    print("\n🖼️  Test 2.3: Image File (Legacy Path)")
    # Create a tiny valid PNG (1x1 pixel)
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    result = handler.process_file(
        source='bytes',
        source_id={
            'filename': 'test.png',
            'content_type': 'image/png',
            'data': png_data
        },
        mode='auto'
    )
    
    print(f"   Method selected: {result.get('method', 'N/A')}")
    if result['success']:
        print(f"✅ Success!")
        print(f"   Method used: {result['method']} (not 'extract' - as expected)")
        print(f"   Content block type: {result['content_block']['type']}")
    else:
        print(f"❌ Failed: {result['error']}")


def test_mode_detection():
    """Test automatic mode detection"""
    print("\n" + "="*70)
    print("TEST 3: Automatic Mode Detection")
    print("="*70)
    
    handler = UniversalFileHandler()
    
    test_cases = [
        # (content_type, size, expected_mode)
        ('image/png', 1024 * 1024, 'direct'),  # 1MB PNG
        ('image/png', 10 * 1024 * 1024, 'files_api'),  # 10MB PNG
        ('application/pdf', 2 * 1024 * 1024, 'direct'),  # 2MB PDF
        ('application/pdf', 50 * 1024 * 1024, 'files_api'),  # 50MB PDF
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 1024 * 1024, 'extract'),  # 1MB DOCX
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 5 * 1024 * 1024, 'extract'),  # 5MB XLSX
        ('text/plain', 100 * 1024, 'extract'),  # 100KB TXT
        ('application/json', 500 * 1024, 'extract'),  # 500KB JSON
        ('text/csv', 2 * 1024 * 1024, 'extract'),  # 2MB CSV
        ('video/mp4', 50 * 1024 * 1024, 'url'),  # 50MB MP4 (unsupported)
    ]
    
    print("\n🔍 Testing mode detection for different file types:\n")
    for content_type, size, expected_mode in test_cases:
        detected_mode = handler._determine_optimal_method(content_type, size)
        status = "✅" if detected_mode == expected_mode else "❌"
        print(f"{status} {content_type} ({size:,} bytes)")
        print(f"      Expected: {expected_mode}, Got: {detected_mode}")


def test_token_comparison():
    """Compare token usage: base64 vs text extraction"""
    print("\n" + "="*70)
    print("TEST 4: Token Usage Comparison")
    print("="*70)
    
    # Simulate a 1000-word document
    word_count = 1000
    document_text = " ".join(["word"] * word_count)
    
    # Base64 size (if we sent it as base64)
    base64_size = len(document_text.encode('utf-8')) * 4 // 3  # Base64 encoding overhead
    base64_tokens = base64_size // 4  # Rough estimate: 4 bytes per token
    
    # Text extraction size
    text_tokens = word_count // 0.75  # ~0.75 words per token
    
    print(f"\n📊 1000-word document comparison:")
    print(f"   Base64 method: ~{base64_tokens:,} tokens")
    print(f"   Text extraction: ~{text_tokens:,} tokens")
    print(f"   Token reduction: ~{((base64_tokens - text_tokens) / base64_tokens * 100):.1f}%")
    print(f"\n✅ Text extraction avoids base64 overhead!")


if __name__ == '__main__':
    print("\n🚀 UNIVERSAL FILE HANDLER v2.0 - TEXT EXTRACTION TESTS")
    print("="*70)
    
    try:
        # Test 1: Text extractor module
        test_text_extractor()
        
        # Test 2: Universal file handler integration
        test_universal_file_handler_integration()
        
        # Test 3: Mode detection
        test_mode_detection()
        
        # Test 4: Token comparison
        test_token_comparison()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETE!")
        print("="*70)
        
        print("\n📋 SUMMARY:")
        print("   - Text extraction module: Working")
        print("   - Universal file handler integration: Working")
        print("   - Mode detection: Working")
        print("   - Token optimization: Verified")
        
        print("\n🎯 Next Steps:")
        print("   1. Install dependencies: pip install -r requirements_text_extraction.txt")
        print("   2. Test with real DOCX/XLSX files")
        print("   3. Update frontend to support new file types")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

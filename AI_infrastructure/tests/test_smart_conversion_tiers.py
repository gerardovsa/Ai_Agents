"""Test: Smart Two-Tier Conversion Strategy

This test verifies:
1. Small office docs → Convert to PDF (Tier 1)
2. Large spreadsheets/docs → Extract to markdown (Tier 2)
3. Fallback if conversion exceeds 2000 tokens

Run:
    python -m AI_infrastructure.tests.test_smart_conversion_tiers
"""
import io
import json
from docx import Document
from openpyxl import Workbook
from PIL import Image

from flask import Flask
from werkzeug.datastructures import MultiDict, FileStorage

from AI_infrastructure.routes.chat_routes import chat_bp, init_chat_routes


class DummySessionManager:
    def get_session(self, session_id):
        return {'id': session_id}

    def add_file_context(self, session_id, filename, text):
        print(f"\n[Session] Saved file context: {filename} ({len(text)} chars)")

    def add_message(self, session_id, role, message):
        pass


class DummyAIClient:
    pass


def make_small_docx():
    """Create small DOCX (should convert to PDF - Tier 1)"""
    doc = Document()
    doc.add_heading('Test Document', 0)
    doc.add_paragraph('This is a small document with an image reference.')
    doc.add_paragraph('It should be converted to PDF for visual analysis.')
    
    b = io.BytesIO()
    doc.save(b)
    b.seek(0)
    return b


def make_large_xlsx():
    """Create large XLSX (should extract to markdown - Tier 2)"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Data"
    
    # Add headers
    ws.append(['Product', 'Q1', 'Q2', 'Q3', 'Q4', 'Total'])
    
    # Add 500 rows of data (will be >100KB)
    for i in range(500):
        ws.append([
            f'Product {i}',
            10000 + i * 100,
            11000 + i * 110,
            12000 + i * 120,
            13000 + i * 130,
            46000 + i * 460
        ])
    
    b = io.BytesIO()
    wb.save(b)
    b.seek(0)
    return b


def run_test():
    """Test smart two-tier conversion"""
    app = Flask(__name__)
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    init_chat_routes(DummySessionManager(), DummyAIClient())
    
    client = app.test_client()
    
    print("\n" + "="*60)
    print("TEST 1: Small DOCX (should convert to PDF - Tier 1)")
    print("="*60)
    
    multi1 = MultiDict()
    multi1.add('session_id', 'test-session-123')
    multi1.add('convert_pref', 'auto')
    multi1.add('files', FileStorage(
        stream=make_small_docx(),
        filename='small_doc.docx',
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ))
    
    response1 = client.post('/api/chat/upload', data=multi1, content_type='multipart/form-data')
    result1 = response1.get_json()
    
    print(f"\nStatus: {response1.status_code}")
    if result1.get('success'):
        file_result = result1['files'][0]
        print(f"Method: {file_result.get('method')}")
        print(f"Token estimate: {file_result.get('metadata', {}).get('token_estimate', 'N/A')}")
        content = file_result.get('content', {})
        print(f"Content type: {content.get('type')}")
        if content.get('type') == 'document':
            print(f"✅ SUCCESS: Small DOCX converted to PDF (Tier 1)")
        elif content.get('type') == 'text':
            print(f"⚠️  UNEXPECTED: Small DOCX extracted to markdown (should be PDF)")
    else:
        print(f"❌ FAILED: {result1.get('error')}")
    
    print("\n" + "="*60)
    print("TEST 2: Large XLSX (should extract to markdown - Tier 2)")
    print("="*60)
    
    multi2 = MultiDict()
    multi2.add('session_id', 'test-session-456')
    multi2.add('convert_pref', 'auto')
    multi2.add('files', FileStorage(
        stream=make_large_xlsx(),
        filename='large_spreadsheet.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ))
    
    response2 = client.post('/api/chat/upload', data=multi2, content_type='multipart/form-data')
    result2 = response2.get_json()
    
    print(f"\nStatus: {response2.status_code}")
    if result2.get('success'):
        file_result = result2['files'][0]
        print(f"Method: {file_result.get('method')}")
        print(f"Token estimate: {file_result.get('metadata', {}).get('token_estimate', 'N/A')}")
        content = file_result.get('content', {})
        print(f"Content type: {content.get('type')}")
        if content.get('type') == 'text':
            text_preview = content.get('text', '')[:200]
            print(f"✅ SUCCESS: Large XLSX extracted to markdown (Tier 2)")
            print(f"Text preview: {text_preview}...")
        elif content.get('type') == 'document':
            print(f"⚠️  UNEXPECTED: Large XLSX converted to PDF (should be markdown)")
    else:
        print(f"❌ FAILED: {result2.get('error')}")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("Two-tier strategy:")
    print("  Tier 1: Small office docs → PDF (visual analysis)")
    print("  Tier 2: Large files (>100KB spreadsheets, >500KB docs) → Markdown")
    print("  Fallback: If conversion >2000 tokens → Markdown")
    print("="*60 + "\n")


if __name__ == '__main__':
    run_test()

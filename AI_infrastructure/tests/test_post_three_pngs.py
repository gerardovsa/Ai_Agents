"""Test: POST three PNGs to the chat upload endpoint using Flask test client

This script creates a minimal Flask app, registers the `chat_bp` blueprint
from `AI_infrastructure.routes.chat_routes`, and posts three in-memory PNG
files to `/api/chat/upload`. It prints the JSON response.

Run:
    python -m AI_infrastructure.tests.test_post_three_pngs
"""
import io
import json
from PIL import Image

from flask import Flask

from AI_infrastructure.routes.chat_routes import chat_bp, init_chat_routes


class DummySessionManager:
    def get_session(self, session_id):
        return {'id': session_id}

    def add_file_context(self, session_id, filename, text):
        print(f"[DummySessionManager] add_file_context: {session_id} {filename} ({len(text)} chars)")

    def add_message(self, session_id, role, message):
        pass


class DummyAIClient:
    pass


def make_png_bytes(color=(255, 0, 0), size=(200, 200)):
    img = Image.new('RGB', size, color)
    b = io.BytesIO()
    img.save(b, format='PNG')
    b.seek(0)
    return b


def run_test():
    app = Flask(__name__)
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    # Initialize routes' session manager and ai_client with dummies
    init_chat_routes(DummySessionManager(), DummyAIClient())

    client = app.test_client()

    # Build a MultiDict and use FileStorage for file uploads
    from werkzeug.datastructures import MultiDict, FileStorage

    multi = MultiDict()
    multi.add('session_id', 'test-session-123')
    multi.add('convert_pref', 'auto')

    multi.add('files', FileStorage(stream=make_png_bytes((255, 0, 0)), filename='img1.png', content_type='image/png'))
    multi.add('files', FileStorage(stream=make_png_bytes((0, 255, 0)), filename='img2.png', content_type='image/png'))
    multi.add('files', FileStorage(stream=make_png_bytes((0, 0, 255)), filename='img3.png', content_type='image/png'))

    response = client.post('/api/chat/upload', data=multi, content_type='multipart/form-data')

    try:
        print('Status code:', response.status_code)
        print(json.dumps(response.get_json(), indent=2))
    except Exception as e:
        print('Failed to decode response:', e)


if __name__ == '__main__':
    run_test()

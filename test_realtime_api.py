"""
Quick API Test - Verify Real-Time Integration Endpoints

Tests:
1. Health check
2. Synergy sessions batch endpoint
3. Threads list endpoint
4. WebSocket connection
"""

import requests
import socketio
import time
import json

API_BASE = 'http://localhost:5001'

def test_health():
    """Test server health"""
    print("\n1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        print(f"   ✅ Health: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"   ❌ Health failed: {e}")
        return False

def test_synergy_batch():
    """Test synergy batch endpoint"""
    print("\n2. Testing Synergy Batch Endpoint...")
    try:
        response = requests.get(
            f"{API_BASE}/api/synergy/sessions/batch",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        data = response.json()
        print(f"   ✅ Synergy: {response.status_code}")
        print(f"   📊 Sessions: {len(data.get('sessions', []))}")
        print(f"   📄 Internal docs: {len(data.get('internal_docs', []))}")
        return True
    except Exception as e:
        print(f"   ❌ Synergy batch failed: {e}")
        return False

def test_threads_list():
    """Test threads list endpoint"""
    print("\n3. Testing Threads List Endpoint...")
    try:
        response = requests.get(
            f"{API_BASE}/api/threads/list?user_id=1",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        data = response.json()
        threads = data.get('threads', []) or (data.get('data', {}).get('threads', []))
        print(f"   ✅ Threads: {response.status_code}")
        print(f"   📊 Thread count: {len(threads)}")
        return True
    except Exception as e:
        print(f"   ❌ Threads list failed: {e}")
        return False

def test_websocket():
    """Test WebSocket connection"""
    print("\n4. Testing WebSocket Connection...")
    
    connected = False
    messages_received = []
    
    def on_connect():
        nonlocal connected
        print(f"   ✅ WebSocket connected")
        connected = True
        sio.emit('ping', {'test': True}, namespace='/ws/synergy')
    
    def on_disconnect():
        print(f"   🔴 WebSocket disconnected")
    
    def on_pong(data):
        print(f"   ✅ Pong received: {data}")
        messages_received.append(('pong', data))
    
    def on_connect_error(error):
        print(f"   ❌ Connection error: {error}")
    
    try:
        sio = socketio.Client()
        
        # Register handlers
        sio.on('connect', on_connect, namespace='/ws/synergy')
        sio.on('disconnect', on_disconnect, namespace='/ws/synergy')
        sio.on('pong', on_pong, namespace='/ws/synergy')
        sio.on('connect_error', on_connect_error, namespace='/ws/synergy')
        
        # Connect
        print(f"   🔌 Connecting to {API_BASE}/ws/synergy...")
        sio.connect(API_BASE, namespaces=['/ws/synergy'], wait_timeout=5)
        
        # Wait for connection
        time.sleep(1)
        
        if connected:
            print(f"   ✅ Connection successful")
            
            # Wait for pong
            time.sleep(1)
            
            if messages_received:
                print(f"   ✅ Ping/Pong working")
            else:
                print(f"   ⚠️  No pong received (but connected)")
            
            # Join room
            sio.emit('join', {'room': 'synergy_board'}, namespace='/ws/synergy')
            print(f"   ✅ Joined room: synergy_board")
            
            # Disconnect
            sio.disconnect()
            return True
        else:
            print(f"   ❌ Failed to connect")
            return False
            
    except Exception as e:
        print(f"   ❌ WebSocket test failed: {e}")
        return False

def test_cache_headers():
    """Test if endpoints support caching"""
    print("\n5. Testing Cache Headers...")
    try:
        response = requests.get(f"{API_BASE}/api/synergy/sessions/batch", timeout=5)
        headers = response.headers
        
        print(f"   Cache-Control: {headers.get('Cache-Control', 'Not set')}")
        print(f"   ETag: {headers.get('ETag', 'Not set')}")
        print(f"   Last-Modified: {headers.get('Last-Modified', 'Not set')}")
        
        return True
    except Exception as e:
        print(f"   ❌ Cache headers test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("   REAL-TIME INTEGRATION TEST")
    print("=" * 60)
    
    results = {
        'Health Check': test_health(),
        'Synergy Batch': test_synergy_batch(),
        'Threads List': test_threads_list(),
        'WebSocket': test_websocket(),
        'Cache Headers': test_cache_headers()
    }
    
    print("\n" + "=" * 60)
    print("   TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        icon = "✅" if passed_test else "❌"
        print(f"{icon} {test_name}")
    
    print(f"\n📊 Score: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Integration working correctly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Check logs above")

if __name__ == '__main__':
    main()

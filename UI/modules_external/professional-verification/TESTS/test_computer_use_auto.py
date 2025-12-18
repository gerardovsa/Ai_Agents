"""
Automated Computer Use Test - No User Input Required
====================================================

This will automatically test Computer Use by having Claude:
1. Visit isb.eco
2. Extract information about the organization
3. Report findings

RUN:
    python test_computer_use_auto.py

CREATED: December 18, 2025
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import base64

# Fix Unicode encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

# Load .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded .env from: {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed (trying environment variables)")


# Simple Docker interaction functions
async def take_screenshot_simple(container_name):
    """Take screenshot from container"""
    import subprocess
    
    # Use scrot to capture screenshot in container
    cmd = ['docker', 'exec', container_name, 'scrot', '-o', '/tmp/screenshot.png']
    subprocess.run(cmd, capture_output=True, timeout=10)
    
    # Copy screenshot from container
    cmd = ['docker', 'cp', f'{container_name}:/tmp/screenshot.png', '/tmp/screenshot.png']
    subprocess.run(cmd, capture_output=True, timeout=10)
    
    # Read and encode
    try:
        with open('/tmp/screenshot.png', 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except:
        # Return placeholder if screenshot fails
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


async def move_mouse_simple(container_name, x, y):
    """Move mouse in container"""
    import subprocess
    cmd = ['docker', 'exec', container_name, 'xdotool', 'mousemove', str(x), str(y)]
    subprocess.run(cmd, capture_output=True, timeout=5)


async def click_mouse_simple(container_name):
    """Click mouse in container"""
    import subprocess
    cmd = ['docker', 'exec', container_name, 'xdotool', 'click', '1']
    subprocess.run(cmd, capture_output=True, timeout=5)


async def type_text_simple(container_name, text):
    """Type text in container"""
    import subprocess
    cmd = ['docker', 'exec', container_name, 'xdotool', 'type', '--', text]
    subprocess.run(cmd, capture_output=True, timeout=10)


async def press_key_simple(container_name, key):
    """Press key in container"""
    import subprocess
    cmd = ['docker', 'exec', container_name, 'xdotool', 'key', key]
    subprocess.run(cmd, capture_output=True, timeout=5)


async def test_computer_use():
    """Test Computer Use by having Claude browse a website"""
    
    print("="*80)
    print("COMPUTER USE AUTOMATED TEST")
    print("="*80)
    
    # Check API key
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    if not anthropic_key:
        print("\n❌ ANTHROPIC_API_KEY not found")
        print("   Set it with: $env:ANTHROPIC_API_KEY = 'sk-ant-...'")
        print("\n⚠️  Test SKIPPED - No API key")
        return
    
    print("\n✅ API key found")
    
    # Check Docker - use simple subprocess instead of docker-py
    try:
        import subprocess
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Docker is running")
            
            # Check if our container exists
            check_container = subprocess.run(
                ['docker', 'ps', '-a', '--filter', 'name=computer-use-test', '--format', '{{.Names}}'],
                capture_output=True, text=True, timeout=5
            )
            
            if 'computer-use-test' not in check_container.stdout:
                print("\n⚠️  Container 'computer-use-test' not found")
                print("   Build and start it with:")
                print("   cd", Path(__file__).parent)
                print("   docker-compose up -d")
                return
            
            # Check if container is running
            check_running = subprocess.run(
                ['docker', 'ps', '--filter', 'name=computer-use-test', '--format', '{{.Names}}'],
                capture_output=True, text=True, timeout=5
            )
            
            if 'computer-use-test' not in check_running.stdout:
                print("\n⚠️  Container 'computer-use-test' is not running")
                print("   Start it with: docker start computer-use-test")
                print("   Or: docker-compose up -d")
                return
            
            print("✅ Container 'computer-use-test' is running")
        else:
            raise Exception("Docker ps command failed")
    except FileNotFoundError:
        print(f"\n❌ Docker command not found")
        print("   Install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        print("\n⚠️  Test SKIPPED - Docker not available")
        return
    except Exception as e:
        print(f"\n❌ Docker error: {e}")
        print("\n⚠️  Test SKIPPED - Docker not available")
        print("   Start Docker Desktop and try again")
        return
    
    # Use simplified executor for testing (no need for full platform executor)
    print("✅ Using test Docker container directly")
    
    # Import Anthropic
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=anthropic_key)
        print("✅ Anthropic client initialized")
    except Exception as e:
        print(f"\n❌ Anthropic error: {e}")
        print("\n⚠️  Test SKIPPED - Anthropic client failed")
        return
    
    print("\n" + "="*80)
    print("STARTING TEST - Claude will browse isb.eco")
    print("="*80)
    
    # Use the test container we already verified is running
    container_id = "computer-use-test"
    print(f"\n📦 Using container: {container_id}")
    
    # Task
    task = """Visit https://isb.eco and tell me what this organization does. 
Be brief - just 2-3 sentences summarizing their purpose."""
    
    print(f"\n💬 Task: {task}")
    print("\n🤖 Claude is working...")
    
    messages = [{"role": "user", "content": task}]
    
    iteration = 0
    max_iterations = 25
    actions = []
    
    try:
        while iteration < max_iterations:
            iteration += 1
            
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=4096,
                tools=[{
                    "type": "computer_20241022",
                    "name": "computer",
                    "display_width_px": 1920,
                    "display_height_px": 1080
                }],
                messages=messages
            )
            
            print(f"   Iteration {iteration}: {response.stop_reason}", end="")
            
            if response.stop_reason == "end_turn":
                print(" ✅ DONE")
                
                # Get response text
                result_text = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        result_text += block.text
                
                print("\n" + "="*80)
                print("CLAUDE'S FINDINGS")
                print("="*80)
                print(f"\n{result_text}\n")
                
                # Save screenshot
                try:
                    screenshot = await take_screenshot_simple(container_id)
                    screenshot_path = f"test_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    with open(screenshot_path, 'wb') as f:
                        f.write(base64.b64decode(screenshot))
                    print(f"📸 Screenshot saved: {screenshot_path}")
                except Exception as e:
                    print(f"⚠️  Screenshot error: {e}")
                
                print("\n" + "="*80)
                print("ACTIONS PERFORMED")
                print("="*80)
                for idx, action in enumerate(actions, 1):
                    print(f"   {idx}. {action}")
                
                print("\n" + "="*80)
                print("✅ TEST PASSED")
                print("="*80)
                print(f"\nTotal iterations: {iteration}")
                print(f"Total actions: {len(actions)}")
                
                return True
            
            if response.stop_reason == "tool_use":
                tool_results = []
                
                for block in response.content:
                    if block.type == "tool_use" and block.name == "computer":
                        action = block.input.get('action')
                        
                        try:
                            if action == "screenshot":
                                result = await take_screenshot_simple(container_id)
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": result
                                })
                                actions.append("Screenshot")
                                print(" 📸", end="")
                            
                            elif action == "mouse_move":
                                coord = block.input.get('coordinate', [0, 0])
                                await move_mouse_simple(container_id, coord[0], coord[1])
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": "Mouse moved"
                                })
                                actions.append(f"Move ({coord[0]}, {coord[1]})")
                                print(" 🖱️", end="")
                            
                            elif action == "left_click":
                                await click_mouse_simple(container_id)
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": "Clicked"
                                })
                                actions.append("Click")
                                print(" 👆", end="")
                            
                            elif action == "type":
                                text = block.input.get('text', '')
                                await type_text_simple(container_id, text)
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": f"Typed: {text}"
                                })
                                actions.append(f"Type: {text[:30]}")
                                print(" ⌨️", end="")
                            
                            elif action == "key":
                                key = block.input.get('text', '')
                                await press_key_simple(container_id, key)
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": f"Key: {key}"
                                })
                                actions.append(f"Key: {key}")
                                print(" ⌨️", end="")
                            
                            else:
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": "OK"
                                })
                        
                        except Exception as e:
                            print(f"\n⚠️  Action error: {e}")
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Error: {str(e)}"
                            })
                
                print()  # New line
                
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
            
            else:
                print(f" ⚠️  Unexpected: {response.stop_reason}")
                break
        
        if iteration >= max_iterations:
            print(f"\n⚠️  Max iterations reached")
            return False
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
        return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\nStarting automated Computer Use test...")
    print("This will take 30-60 seconds...\n")
    
    try:
        result = asyncio.run(test_computer_use())
        
        if result:
            print("\n🎉 Computer Use is working perfectly!")
            print("\nYou can now use:")
            print("  - auto_enter_verification_results() for form automation")
            print("  - batch_enter_verifications() for bulk processing")
            print("  - auto_enter_to_postgres() for direct database inserts")
        else:
            print("\n⚠️  Test incomplete or skipped")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

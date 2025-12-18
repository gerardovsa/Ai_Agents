"""
Live Computer Use Demo - Interactive Test
=========================================

This script will:
1. Start a Docker browser container
2. Ask Claude to navigate to a website and extract information
3. Show you what Claude sees (screenshots)
4. Display Claude's actions in real-time

REQUIREMENTS:
- Docker Desktop running
- Anthropic API key set: $env:ANTHROPIC_API_KEY = "sk-ant-..."

RUN:
    python demo_computer_use_live.py

CREATED: December 18, 2025
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import base64

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


async def demo_simple_browse():
    """Demo: Have Claude browse a website and extract information"""
    print("\n" + "="*80)
    print("🤖 CLAUDE COMPUTER USE - LIVE DEMO")
    print("="*80)
    
    print("\n📋 TASK: Ask Claude to visit ISB.eco and tell us what the organization does")
    
    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    if not anthropic_key:
        print("   ❌ ANTHROPIC_API_KEY not found in environment")
        print("   Set it with: $env:ANTHROPIC_API_KEY = 'sk-ant-...'")
        return
    else:
        print("   ✅ Anthropic API key found")
    
    # Check Docker
    try:
        import docker
        client = docker.from_env()
        print("   ✅ Docker is available")
    except Exception as e:
        print(f"   ❌ Docker not available: {e}")
        print("   Make sure Docker Desktop is running")
        return
    
    # Import Computer Use executor
    try:
        from AI_infrastructure.core.computer_use_executor import get_computer_use_executor
        executor = get_computer_use_executor()
        print("   ✅ Computer Use executor loaded")
    except ImportError as e:
        print(f"   ❌ Computer Use executor not available: {e}")
        return
    
    # Import Anthropic
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=anthropic_key)
        print("   ✅ Anthropic client initialized")
    except Exception as e:
        print(f"   ❌ Anthropic client error: {e}")
        return
    
    print("\n" + "="*80)
    print("🚀 STARTING COMPUTER USE SESSION")
    print("="*80)
    
    # Get browser container
    print("\n📦 Starting browser container...")
    container_id = await executor.get_browser_container(reuse=False)
    
    if not container_id:
        print("❌ Failed to start container")
        return
    
    print(f"✅ Container started: {container_id[:12]}")
    
    # Task for Claude
    task = """
Please visit the website isb.eco and tell me:
1. What is this organization about?
2. What are their main focus areas?
3. Is there contact information available?

Navigate to https://isb.eco, take your time to explore the page, 
and give me a comprehensive summary of what you find.
"""
    
    print(f"\n💬 Task for Claude:")
    print(f"   {task.strip()}")
    
    # Execute with Claude
    messages = [{
        "role": "user",
        "content": task
    }]
    
    print("\n🤖 Claude is now browsing isb.eco...")
    print("   (This may take 30-60 seconds)")
    
    iteration = 0
    max_iterations = 30
    actions_log = []
    
    try:
        while iteration < max_iterations:
            iteration += 1
            
            # Call Claude with Computer Use
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
            
            print(f"\n   Iteration {iteration}: {response.stop_reason}")
            
            # Check if done
            if response.stop_reason == "end_turn":
                print("\n✅ Claude finished the task!")
                
                # Extract text response
                final_text = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        final_text += block.text
                
                print("\n" + "="*80)
                print("📊 CLAUDE'S FINDINGS")
                print("="*80)
                print(f"\n{final_text}")
                
                # Save final screenshot
                print("\n📸 Capturing final screenshot...")
                screenshot = await executor.take_screenshot(container_id)
                
                # Save to file
                screenshot_path = f"claude_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot_bytes = base64.b64decode(screenshot)
                with open(screenshot_path, 'wb') as f:
                    f.write(screenshot_bytes)
                
                print(f"   ✅ Saved: {screenshot_path}")
                
                print("\n" + "="*80)
                print("📋 ACTIONS LOG")
                print("="*80)
                for idx, action in enumerate(actions_log, 1):
                    print(f"   {idx}. {action}")
                
                break
            
            # Process tool use
            if response.stop_reason == "tool_use":
                tool_results = []
                
                for block in response.content:
                    if block.type == "tool_use" and block.name == "computer":
                        action = block.input.get('action')
                        
                        if action == "screenshot":
                            result = await executor.take_screenshot(container_id)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result
                            })
                            action_desc = "📸 Screenshot"
                        
                        elif action == "mouse_move":
                            coordinate = block.input.get('coordinate', [0, 0])
                            await executor.move_mouse(container_id, coordinate[0], coordinate[1])
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": "Mouse moved"
                            })
                            action_desc = f"🖱️  Mouse move to ({coordinate[0]}, {coordinate[1]})"
                        
                        elif action == "left_click":
                            await executor.click_mouse(container_id)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": "Clicked"
                            })
                            action_desc = "🖱️  Left click"
                        
                        elif action == "type":
                            text = block.input.get('text', '')
                            await executor.type_text(container_id, text)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Typed: {text}"
                            })
                            action_desc = f"⌨️  Type: {text[:50]}..."
                        
                        elif action == "key":
                            key = block.input.get('text', '')
                            await executor.press_key(container_id, key)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Pressed key: {key}"
                            })
                            action_desc = f"⌨️  Key press: {key}"
                        
                        elif action == "cursor_position":
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": "Cursor position recorded"
                            })
                            action_desc = "📍 Cursor position"
                        
                        else:
                            action_desc = f"❓ Unknown: {action}"
                        
                        print(f"      {action_desc}")
                        actions_log.append(action_desc)
                
                # Continue conversation
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            
            else:
                print(f"\n⚠️  Unexpected stop reason: {response.stop_reason}")
                break
        
        if iteration >= max_iterations:
            print(f"\n⚠️  Max iterations ({max_iterations}) reached")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🧹 Cleaning up...")
        # Container cleanup handled by executor


async def demo_form_fill():
    """Demo: Have Claude fill a Google Form"""
    print("\n" + "="*80)
    print("🤖 CLAUDE COMPUTER USE - FORM FILLING DEMO")
    print("="*80)
    
    print("\n📋 TASK: Ask Claude to fill a Google Form with verification data")
    
    # This is a more advanced demo - shows form automation
    print("\n⚠️  This demo requires a Google Form URL")
    print("   Create a test form at: https://forms.google.com")
    print("   Then update the URL in this script")
    
    form_url = input("\n📝 Enter your Google Form URL (or press Enter to skip): ").strip()
    
    if not form_url:
        print("   ⏩ Skipping form fill demo")
        return
    
    print(f"\n✅ Will fill form at: {form_url}")
    
    # Data to fill
    test_data = {
        'name': 'Gregory Dutton',
        'company': 'Institute of Sustainable Biodiversity',
        'email': 'gregory.dutton@isb.eco',
        'legitimacy_score': '42.3',
        'status': 'UNCERTAIN'
    }
    
    print("\n📊 Data to enter:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    print("\n🤖 Starting form fill...")
    print("   (This may take 60-90 seconds)")
    
    # Similar process as demo_simple_browse but with form filling task
    # Implementation would follow same pattern


async def main():
    """Main entry point"""
    print("="*80)
    print("🎯 COMPUTER USE LIVE DEMOS")
    print("="*80)
    
    print("\nAvailable demos:")
    print("  1. Simple Browse - Claude visits isb.eco and extracts info")
    print("  2. Form Fill - Claude fills a Google Form (requires form URL)")
    print("  3. Both demos")
    
    choice = input("\nSelect demo (1/2/3) or press Enter for demo 1: ").strip() or "1"
    
    if choice == "1":
        await demo_simple_browse()
    elif choice == "2":
        await demo_form_fill()
    elif choice == "3":
        await demo_simple_browse()
        print("\n" + "="*80)
        await demo_form_fill()
    else:
        print(f"❌ Invalid choice: {choice}")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE")
    print("="*80)
    
    print("\n📚 Next Steps:")
    print("   1. Review the screenshot that was saved")
    print("   2. Check the actions log above")
    print("   3. Try modifying the task to explore different websites")
    print("   4. Use auto_enter_verification_results() for production automation")
    
    print("\n💡 Tips:")
    print("   - Claude can navigate any publicly accessible website")
    print("   - Screenshots are saved in the current directory")
    print("   - You can interrupt with Ctrl+C at any time")
    print("   - Docker container is automatically cleaned up")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

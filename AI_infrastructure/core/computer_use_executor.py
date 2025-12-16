"""
Computer Use Executor - Global Service
======================================

PURPOSE:
Executes Anthropic Computer Use API commands in Docker containers.
This is a GLOBALLY ACCESSIBLE service that any module can use for browser automation.

USAGE:
    from AI_infrastructure.core.computer_use_executor import get_computer_use_executor
    
    executor = get_computer_use_executor()
    container_id = await executor.get_browser_container()
    screenshot = await executor.take_screenshot(container_id)
    await executor.move_mouse(container_id, 100, 200)
    await executor.click_mouse(container_id)
    await executor.type_text(container_id, "Hello World")

INTEGRATION WITH ANTHROPIC:
    response = anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        tools=[{
            "type": "computer_20241022",
            "name": "computer",
            "display_width_px": 1920,
            "display_height_px": 1080
        }],
        messages=messages
    )
    
    # When Claude requests computer use
    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use" and block.name == "computer":
                result = await executor.execute_computer_action(
                    container_id,
                    block.input
                )

CREATED: December 16, 2025
AUTHOR: AI Agent Platform
"""

import docker
import asyncio
import base64
import io
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class ComputerUseExecutor:
    """
    Singleton service for executing Anthropic Computer Use commands in Docker containers.
    
    This service provides a unified interface for browser automation across the entire platform.
    Any module needing browser automation (verification, testing, scraping, etc.) can use this.
    
    Features:
    - Screenshot capture from containerized displays
    - Mouse control (move, click, drag)
    - Keyboard input (type text, press keys)
    - Bash command execution
    - Integration with DockerContainerManager
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - only one executor instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize executor (only once due to singleton)"""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.docker_client = None
        self.active_containers = {}  # container_id -> container_info
        
        logger.info("[COMPUTER_USE_EXECUTOR] Initializing...")
        
        try:
            self.docker_client = docker.from_env()
            logger.info("[COMPUTER_USE_EXECUTOR] ✅ Docker client initialized")
        except docker.errors.DockerException as e:
            logger.warning(f"[COMPUTER_USE_EXECUTOR] ⚠️ Docker not available: {e}")
            logger.warning("[COMPUTER_USE_EXECUTOR] Computer Use features will not be available")
    
    async def get_browser_container(self, reuse: bool = True) -> Optional[str]:
        """
        Get or create a browser container for computer use.
        
        Args:
            reuse: If True, reuse existing container if available
            
        Returns:
            Container ID string, or None if Docker unavailable
        """
        if self.docker_client is None:
            logger.error("[COMPUTER_USE_EXECUTOR] Docker client not available")
            return None
        
        # Check for available container
        if reuse and self.active_containers:
            for container_id, info in self.active_containers.items():
                if info.get('in_use') == False:
                    info['in_use'] = True
                    logger.info(f"[COMPUTER_USE_EXECUTOR] Reusing container: {container_id[:12]}")
                    return container_id
        
        # Create new container
        try:
            logger.info("[COMPUTER_USE_EXECUTOR] Creating new browser container...")
            
            container = self.docker_client.containers.run(
                'professional-verification-browser:latest',  # Custom image (see Step 16)
                detach=True,
                environment={
                    'DISPLAY': ':1',
                    'WIDTH': '1920',
                    'HEIGHT': '1080'
                },
                mem_limit='2g',
                cpu_period=100000,
                cpu_quota=100000,  # 100% CPU limit
                network_mode='bridge',  # Allow network for browsing
                remove=False,
                command='bash -c "Xvfb :1 -screen 0 1920x1080x24 & x11vnc -display :1 -forever -shared & fluxbox & chromium-browser --no-sandbox --disable-dev-shm-usage & tail -f /dev/null"'
            )
            
            container_id = container.id
            
            # Wait for services to start
            logger.info(f"[COMPUTER_USE_EXECUTOR] Waiting for services in {container_id[:12]}...")
            await asyncio.sleep(5)
            
            # Store container info
            self.active_containers[container_id] = {
                'container': container,
                'created_at': time.time(),
                'in_use': True,
                'display': ':1'
            }
            
            logger.info(f"[COMPUTER_USE_EXECUTOR] ✅ Container ready: {container_id[:12]}")
            return container_id
            
        except docker.errors.ImageNotFound:
            logger.error("[COMPUTER_USE_EXECUTOR] ❌ Image 'professional-verification-browser:latest' not found")
            logger.error("[COMPUTER_USE_EXECUTOR] Please build the image first (see Step 16 - docker/computer-use/)")
            return None
        except Exception as e:
            logger.error(f"[COMPUTER_USE_EXECUTOR] ❌ Failed to create container: {e}")
            return None
    
    def release_container(self, container_id: str):
        """
        Release container back to pool (mark as not in use).
        
        Args:
            container_id: Container to release
        """
        if container_id in self.active_containers:
            self.active_containers[container_id]['in_use'] = False
            logger.info(f"[COMPUTER_USE_EXECUTOR] Released container: {container_id[:12]}")
    
    def destroy_container(self, container_id: str):
        """
        Destroy a container completely.
        
        Args:
            container_id: Container to destroy
        """
        if container_id in self.active_containers:
            try:
                container = self.active_containers[container_id]['container']
                container.stop()
                container.remove()
                del self.active_containers[container_id]
                logger.info(f"[COMPUTER_USE_EXECUTOR] Destroyed container: {container_id[:12]}")
            except Exception as e:
                logger.error(f"[COMPUTER_USE_EXECUTOR] Error destroying container: {e}")
    
    async def execute_computer_action(
        self,
        container_id: str,
        action_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a computer use action (from Anthropic API response).
        
        This is the main entry point when integrating with Claude's computer use tools.
        
        Args:
            container_id: Container to execute in
            action_input: Dict from Claude's tool_use block.input
                Example: {"action": "screenshot"}
                Example: {"action": "mouse_move", "coordinate": [100, 200]}
                Example: {"action": "type", "text": "Hello"}
        
        Returns:
            Dict with action result, formatted for Anthropic API
        """
        action = action_input.get("action")
        
        if action == "screenshot":
            return await self.take_screenshot(container_id)
        
        elif action == "mouse_move":
            coordinate = action_input.get("coordinate", [0, 0])
            return await self.move_mouse(container_id, coordinate[0], coordinate[1])
        
        elif action == "left_click":
            return await self.click_mouse(container_id, button="left")
        
        elif action == "right_click":
            return await self.click_mouse(container_id, button="right")
        
        elif action == "middle_click":
            return await self.click_mouse(container_id, button="middle")
        
        elif action == "double_click":
            return await self.double_click(container_id)
        
        elif action == "type":
            text = action_input.get("text", "")
            return await self.type_text(container_id, text)
        
        elif action == "key":
            key = action_input.get("text", "")
            return await self.press_key(container_id, key)
        
        elif action == "cursor_position":
            return await self.get_cursor_position(container_id)
        
        else:
            return {
                "error": f"Unknown action: {action}",
                "success": False
            }
    
    async def take_screenshot(self, container_id: str) -> Dict[str, Any]:
        """
        Capture screenshot from container's display.
        
        Args:
            container_id: Container to screenshot
            
        Returns:
            Dict with base64-encoded screenshot for Anthropic API
        """
        if container_id not in self.active_containers:
            return {"error": "Container not found", "success": False}
        
        try:
            container = self.active_containers[container_id]['container']
            display = self.active_containers[container_id]['display']
            
            # Use scrot to capture screenshot
            exit_code, output = container.exec_run(
                f"DISPLAY={display} scrot -o /tmp/screenshot.png",
                workdir="/tmp"
            )
            
            if exit_code != 0:
                logger.error(f"[COMPUTER_USE_EXECUTOR] Screenshot failed: {output.decode()}")
                return {"error": "Screenshot capture failed", "success": False}
            
            # Get the image file
            bits, stat = container.get_archive('/tmp/screenshot.png')
            
            # Extract file from tar archive
            import tarfile
            tar_stream = io.BytesIO()
            for chunk in bits:
                tar_stream.write(chunk)
            tar_stream.seek(0)
            
            tar = tarfile.open(fileobj=tar_stream)
            screenshot_file = tar.extractfile('screenshot.png')
            screenshot_data = screenshot_file.read()
            
            # Encode to base64
            screenshot_base64 = base64.b64encode(screenshot_data).decode('utf-8')
            
            logger.info(f"[COMPUTER_USE_EXECUTOR] ✅ Screenshot captured ({len(screenshot_base64)} chars)")
            
            # Return in Anthropic API format
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": screenshot_base64
                }
            }
            
        except Exception as e:
            logger.error(f"[COMPUTER_USE_EXECUTOR] Screenshot error: {e}")
            return {"error": str(e), "success": False}
    
    async def move_mouse(self, container_id: str, x: int, y: int) -> Dict[str, Any]:
        """
        Move mouse cursor in container.
        
        Args:
            container_id: Container to control
            x: X coordinate (0-1920)
            y: Y coordinate (0-1080)
            
        Returns:
            Success/error dict
        """
        if container_id not in self.active_containers:
            return {"error": "Container not found", "success": False}
        
        try:
            container = self.active_containers[container_id]['container']
            display = self.active_containers[container_id]['display']
            
            exit_code, output = container.exec_run(
                f"DISPLAY={display} xdotool mousemove {x} {y}"
            )
            
            if exit_code == 0:
                return {"success": True, "message": f"Mouse moved to ({x}, {y})"}
            else:
                return {"error": output.decode(), "success": False}
                
        except Exception as e:
            logger.error(f"[COMPUTER_USE_EXECUTOR] Mouse move error: {e}")
            return {"error": str(e), "success": False}
    
    async def click_mouse(self, container_id: str, button: str = "left") -> Dict[str, Any]:
        """
        Click mouse in container.
        
        Args:
            container_id: Container to control
            button: "left", "right", or "middle"
            
        Returns:
            Success/error dict
        """
        if container_id not in self.active_containers:
            return {"error": "Container not found", "success": False}
        
        button_map = {"left": 1, "middle": 2, "right": 3}
        button_num = button_map.get(button, 1)
        
        try:
            container = self.active_containers[container_id]['container']
            display = self.active_containers[container_id]['display']
            
            exit_code, output = container.exec_run(
                f"DISPLAY={display} xdotool click {button_num}"
            )
            
            if exit_code == 0:
                return {"success": True, "message": f"{button} click executed"}
            else:
                return {"error": output.decode(), "success": False}
                
        except Exception as e:
            logger.error(f"[COMPUTER_USE_EXECUTOR] Mouse click error: {e}")
            return {"error": str(e), "success": False}
    
    async def double_click(self, container_id: str) -> Dict[str, Any]:
        """Double-click mouse in container."""
        if container_id not in self.active_containers:
            return {"error": "Container not found", "success": False}
        
        try:
            container = self.active_containers[container_id]['container']
            display = self.active_containers[container_id]['display']
            
            exit_code, output = container.exec_run(
                f"DISPLAY={display} xdotool click --repeat 2 1"
            )
            
            if exit_code == 0:
                return {"success": True, "message": "Double-click executed"}
            else:
                return {"error": output.decode(), "success": False}
                
        except Exception as e:
            logger.error(f"[COMPUTER_USE_EXECUTOR] Double-click error: {e}")
            return {"error": str(e), "success": False}
    
    async def type_text(self, container_id: str, text: str) -> Dict[str, Any]:
        """
        Type text in container.
        
        Args:
            container_id: Container to control
            text: Text to type
            
        Returns:
            Success/error dict
        """
        if container_id not in self.active_containers:
            return {"error": "Container not found", "success": False}
        
        try:
            container = self.active_containers[container_id]['container']
            display = self.active_containers[container_id]['display']
            
            # Escape single quotes in text
            escaped_text = text.replace("'", "'\\''")
            
            exit_code, output = container.exec_run(
                f"DISPLAY={display} xdotool type '{escaped_text}'"
            )
            
            if exit_code == 0:
                return {"success": True, "message": f"Typed: {text[:50]}..."}
            else:
                return {"error": output.decode(), "success": False}
                
        except Exception as e:
            logger.error(f"[COMPUTER_USE_EXECUTOR] Type text error: {e}")
            return {"error": str(e), "success": False}
    
    async def press_key(self, container_id: str, key: str) -> Dict[str, Any]:
        """
        Press a special key in container.
        
        Args:
            container_id: Container to control
            key: Key name (e.g., "Return", "Tab", "Escape", "ctrl+c")
            
        Returns:
            Success/error dict
        """
        if container_id not in self.active_containers:
            return {"error": "Container not found", "success": False}
        
        try:
            container = self.active_containers[container_id]['container']
            display = self.active_containers[container_id]['display']
            
            exit_code, output = container.exec_run(
                f"DISPLAY={display} xdotool key {key}"
            )
            
            if exit_code == 0:
                return {"success": True, "message": f"Pressed: {key}"}
            else:
                return {"error": output.decode(), "success": False}
                
        except Exception as e:
            logger.error(f"[COMPUTER_USE_EXECUTOR] Press key error: {e}")
            return {"error": str(e), "success": False}
    
    async def get_cursor_position(self, container_id: str) -> Dict[str, Any]:
        """
        Get current mouse cursor position.
        
        Args:
            container_id: Container to query
            
        Returns:
            Dict with x, y coordinates
        """
        if container_id not in self.active_containers:
            return {"error": "Container not found", "success": False}
        
        try:
            container = self.active_containers[container_id]['container']
            display = self.active_containers[container_id]['display']
            
            exit_code, output = container.exec_run(
                f"DISPLAY={display} xdotool getmouselocation --shell"
            )
            
            if exit_code == 0:
                # Parse output: X=123\nY=456\nSCREEN=0\nWINDOW=...
                lines = output.decode().strip().split('\n')
                coords = {}
                for line in lines:
                    if '=' in line:
                        key, value = line.split('=')
                        coords[key] = value
                
                return {
                    "success": True,
                    "x": int(coords.get('X', 0)),
                    "y": int(coords.get('Y', 0))
                }
            else:
                return {"error": output.decode(), "success": False}
                
        except Exception as e:
            logger.error(f"[COMPUTER_USE_EXECUTOR] Get cursor position error: {e}")
            return {"error": str(e), "success": False}
    
    async def execute_bash(
        self,
        container_id: str,
        command: str,
        workdir: str = "/tmp"
    ) -> Dict[str, Any]:
        """
        Execute bash command in container.
        
        Args:
            container_id: Container to execute in
            command: Bash command to run
            workdir: Working directory
            
        Returns:
            Dict with exit_code and output
        """
        if container_id not in self.active_containers:
            return {"error": "Container not found", "success": False}
        
        try:
            container = self.active_containers[container_id]['container']
            
            exit_code, output = container.exec_run(
                f'bash -c "{command}"',
                workdir=workdir
            )
            
            return {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "output": output.decode('utf-8', errors='replace')
            }
            
        except Exception as e:
            logger.error(f"[COMPUTER_USE_EXECUTOR] Bash execution error: {e}")
            return {"error": str(e), "success": False}
    
    def cleanup_all_containers(self):
        """
        Cleanup all active containers.
        Call this on application shutdown.
        """
        logger.info("[COMPUTER_USE_EXECUTOR] Cleaning up all containers...")
        
        for container_id in list(self.active_containers.keys()):
            self.destroy_container(container_id)
        
        logger.info("[COMPUTER_USE_EXECUTOR] ✅ Cleanup complete")


# Singleton getter
def get_computer_use_executor() -> ComputerUseExecutor:
    """
    Get the global ComputerUseExecutor instance.
    
    Usage:
        from AI_infrastructure.core.computer_use_executor import get_computer_use_executor
        
        executor = get_computer_use_executor()
        container_id = await executor.get_browser_container()
    """
    return ComputerUseExecutor()

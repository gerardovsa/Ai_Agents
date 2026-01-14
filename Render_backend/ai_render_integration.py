"""
AI-Render Integration Module
Connects AI models (DeepSeek, Claude, GPT) to Render.com services

Usage:
    from ai_render_integration import AIRenderClient
    
    client = AIRenderClient()
    
    # Process data with AI through Render
    result = client.process_with_ai("Analyze this data...", model="deepseek")
    
    # Deploy AI service to Render
    client.deploy_ai_service()
    
    # Monitor AI service health
    status = client.check_ai_health()
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from Render_backend.render_api_client import RenderAPIClient
except ImportError:
    print("⚠️  Warning: render_api_client not found. Install or check path.")
    RenderAPIClient = None


class AIRenderClient:
    """Client for integrating AI models with Render.com services"""
    
    def __init__(self, render_api_key: Optional[str] = None):
        """
        Initialize AI-Render integration client
        
        Args:
            render_api_key: Render API key (defaults to env var)
        """
        # Render configuration
        self.render_api_key = render_api_key or os.getenv('RENDER_API_KEY')
        self.render_flask_url = os.getenv('RENDER_FLASK_URL', 'https://inhouseprint-flask.onrender.com')
        self.render_streamlit_url = os.getenv('RENDER_STREAMLIT_URL', 'https://inhouseprint-streamlit.onrender.com')
        
        # AI model configuration
        self.deepseek_keys = self._load_deepseek_keys()
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        # Default AI settings
        self.default_provider = os.getenv('DEFAULT_AI_PROVIDER', 'deepseek')
        self.ai_model = os.getenv('AI_MODEL', 'deepseek-chat')
        self.temperature = float(os.getenv('AI_TEMPERATURE', '0.1'))
        self.max_tokens = int(os.getenv('AI_MAX_TOKENS', '8000'))
        
        # Initialize Render client
        self.render_client = RenderAPIClient(self.render_api_key) if RenderAPIClient and self.render_api_key else None
        
        print(" AI-Render Integration Client initialized")
        print(f"   Render Flask URL: {self.render_flask_url}")
        print(f"   Default AI Provider: {self.default_provider}")
        print(f"   AI Model: {self.ai_model}")
    
    def _load_deepseek_keys(self) -> List[str]:
        """Load DeepSeek API keys from environment"""
        keys = []
        for i in range(1, 11):
            key = os.getenv(f'DEEPSEEK_API_KEY_{i}')
            if key:
                keys.append(key)
        return keys
    
    # ==================== AI Processing ====================
    
    def process_with_deepseek(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Process prompt with DeepSeek AI
        
        Args:
            prompt: Text prompt to process
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            AI response with content and metadata
        """
        if not self.deepseek_keys:
            return {"error": "No DeepSeek API keys configured"}
        
        api_key = self.deepseek_keys[0]  # Use first key (implement rotation later)
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": kwargs.get("model", "deepseek-chat"),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens)
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "content": result['choices'][0]['message']['content'],
                "model": result.get('model'),
                "usage": result.get('usage'),
                "provider": "deepseek"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "deepseek"
            }
    
    def process_with_claude(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Process prompt with Anthropic Claude
        
        Args:
            prompt: Text prompt to process
            **kwargs: Additional parameters
            
        Returns:
            AI response with content and metadata
        """
        if not self.anthropic_key:
            return {"error": "No Anthropic API key configured"}
        
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": kwargs.get("model", "claude-sonnet-4-5-20250929"),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "content": result['content'][0]['text'],
                "model": result.get('model'),
                "usage": result.get('usage'),
                "provider": "anthropic"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "anthropic"
            }
    
    def process_with_gpt(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Process prompt with OpenAI GPT
        
        Args:
            prompt: Text prompt to process
            **kwargs: Additional parameters
            
        Returns:
            AI response with content and metadata
        """
        if not self.openai_key:
            return {"error": "No OpenAI API key configured"}
        
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_key}"
        }
        
        payload = {
            "model": kwargs.get("model", "gpt-4"),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens)
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "content": result['choices'][0]['message']['content'],
                "model": result.get('model'),
                "usage": result.get('usage'),
                "provider": "openai"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "openai"
            }
    
    def process_with_ai(self, prompt: str, provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Process prompt with specified AI provider (auto-select if not specified)
        
        Args:
            prompt: Text prompt to process
            provider: AI provider ('deepseek', 'anthropic', 'openai', or None for default)
            **kwargs: Additional parameters
            
        Returns:
            AI response with content and metadata
        """
        provider = provider or self.default_provider
        
        print(f"🤖 Processing with {provider.upper()}...")
        
        if provider == 'deepseek':
            return self.process_with_deepseek(prompt, **kwargs)
        elif provider in ['anthropic', 'claude']:
            return self.process_with_claude(prompt, **kwargs)
        elif provider in ['openai', 'gpt']:
            return self.process_with_gpt(prompt, **kwargs)
        else:
            return {"error": f"Unknown provider: {provider}"}
    
    # ==================== Render Integration ====================
    
    def send_to_flask(self, endpoint: str, data: Dict[str, Any], method: str = "POST") -> Dict[str, Any]:
        """
        Send data to Flask service on Render
        
        Args:
            endpoint: API endpoint (e.g., '/api/process')
            data: Data to send
            method: HTTP method (GET, POST, etc.)
            
        Returns:
            Response from Flask service
        """
        url = f"{self.render_flask_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, params=data, timeout=30)
            else:
                response = requests.post(url, json=data, timeout=30)
            
            response.raise_for_status()
            
            return {
                "success": True,
                "data": response.json(),
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_with_ai_and_store(self, prompt: str, provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Process with AI and send results to Flask service
        
        Args:
            prompt: Text prompt to process
            provider: AI provider
            **kwargs: Additional parameters
            
        Returns:
            Combined result with AI response and storage confirmation
        """
        # Get AI response
        ai_result = self.process_with_ai(prompt, provider, **kwargs)
        
        if not ai_result.get('success'):
            return ai_result
        
        # Send to Flask (if endpoint exists)
        storage_result = self.send_to_flask('/api/ai-result', {
            'prompt': prompt,
            'response': ai_result['content'],
            'provider': ai_result['provider'],
            'model': ai_result.get('model'),
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            "ai_result": ai_result,
            "storage_result": storage_result
        }
    
    # ==================== Service Management ====================
    
    def check_render_services(self) -> Dict[str, Any]:
        """
        Check status of all Render services
        
        Returns:
            Status of Flask and Streamlit services
        """
        if not self.render_client:
            return {"error": "Render API client not initialized"}
        
        print("🔍 Checking Render services...")
        
        try:
            # Get Flask service
            flask_service = self.render_client.get_flask_service()
            flask_status = self.render_client.check_service_status(flask_service['id']) if flask_service else None
            
            # Get Streamlit service
            streamlit_service = self.render_client.get_streamlit_service()
            streamlit_status = self.render_client.check_service_status(streamlit_service['id']) if streamlit_service else None
            
            return {
                "success": True,
                "flask": {
                    "name": flask_service['name'] if flask_service else None,
                    "status": flask_status['status'] if flask_status else None,
                    "url": flask_status['url'] if flask_status else None,
                    "plan": flask_status['plan'] if flask_status else None
                },
                "streamlit": {
                    "name": streamlit_service['name'] if streamlit_service else None,
                    "status": streamlit_status['status'] if streamlit_status else None,
                    "url": streamlit_status['url'] if streamlit_status else None,
                    "plan": streamlit_status['plan'] if streamlit_status else None
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_full_integration(self) -> Dict[str, Any]:
        """
        Test full AI-Render integration pipeline
        
        Returns:
            Test results with all components
        """
        print("=" * 80)
        print("TESTING AI-RENDER INTEGRATION")
        print("=" * 80)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
        
        # Test 1: Render service status
        print("\n📊 Test 1: Render Service Status")
        service_status = self.check_render_services()
        results["tests"].append({
            "name": "Render Services",
            "result": service_status
        })
        
        if service_status.get('success'):
            print("    Flask:", service_status['flask']['status'])
            print("    Streamlit:", service_status['streamlit']['status'])
        
        # Test 2: DeepSeek AI
        print("\n🤖 Test 2: DeepSeek AI")
        deepseek_result = self.process_with_deepseek("Say 'Hello from DeepSeek AI!' in one sentence.", max_tokens=100)
        results["tests"].append({
            "name": "DeepSeek AI",
            "result": deepseek_result
        })
        
        if deepseek_result.get('success'):
            print(f"    Response: {deepseek_result['content'][:100]}...")
        else:
            print(f"    Error: {deepseek_result.get('error')}")
        
        # Test 3: Claude AI
        print("\n🤖 Test 3: Claude AI")
        claude_result = self.process_with_claude("Say 'Hello from Claude AI!' in one sentence.", max_tokens=100)
        results["tests"].append({
            "name": "Claude AI",
            "result": claude_result
        })
        
        if claude_result.get('success'):
            print(f"    Response: {claude_result['content'][:100]}...")
        else:
            print(f"    Error: {claude_result.get('error')}")
        
        # Test 4: Flask connectivity
        print("\n🌐 Test 4: Flask Service Connectivity")
        try:
            flask_response = requests.get(self.render_flask_url, timeout=10)
            flask_test = {
                "success": flask_response.status_code == 200,
                "status_code": flask_response.status_code,
                "response_time": flask_response.elapsed.total_seconds()
            }
            results["tests"].append({
                "name": "Flask Connectivity",
                "result": flask_test
            })
            print(f"    Status: {flask_response.status_code}")
            print(f"    Response time: {flask_response.elapsed.total_seconds():.2f}s")
        except Exception as e:
            results["tests"].append({
                "name": "Flask Connectivity",
                "result": {"success": False, "error": str(e)}
            })
            print(f"    Error: {e}")
        
        print("\n" + "=" * 80)
        print("INTEGRATION TEST COMPLETE")
        print("=" * 80)
        
        return results


# ==================== CLI Interface ====================

def main():
    """CLI interface for AI-Render integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-Render Integration Tool")
    parser.add_argument("--test", action="store_true", help="Run full integration test")
    parser.add_argument("--prompt", type=str, help="Process prompt with AI")
    parser.add_argument("--provider", type=str, choices=["deepseek", "claude", "openai"], help="AI provider")
    parser.add_argument("--check-services", action="store_true", help="Check Render service status")
    
    args = parser.parse_args()
    
    # Initialize client
    client = AIRenderClient()
    
    if args.test:
        # Run full integration test
        results = client.test_full_integration()
        
    elif args.check_services:
        # Check Render services
        status = client.check_render_services()
        print(json.dumps(status, indent=2))
        
    elif args.prompt:
        # Process prompt
        result = client.process_with_ai(args.prompt, provider=args.provider)
        print("\n" + "=" * 80)
        print("AI RESPONSE")
        print("=" * 80)
        if result.get('success'):
            print(f"\nProvider: {result['provider']}")
            print(f"Model: {result.get('model')}")
            print(f"\n{result['content']}")
            print(f"\nUsage: {result.get('usage')}")
        else:
            print(f"\n Error: {result.get('error')}")
        print("=" * 80)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

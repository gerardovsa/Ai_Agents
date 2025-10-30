"""
Unified AI Client - Multi-Provider Support
Supports: Anthropic Claude, DeepSeek, OpenAI GPT

This client wraps all AI providers with a unified interface
so routes can switch providers without code changes.
"""

from anthropic import Anthropic
import openai
import requests
import json
from typing import Dict, List, Optional, Callable, Any, Literal
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Quote_Calculator', 'AI_Quote_Agent', 'core'))

# TODO: Uncomment when tool_use_agent is available
# from tool_use_agent import ToolUseAgent

# Placeholder for ToolUseAgent - replace with actual implementation when available
class ToolUseAgent:
    """
    Placeholder for tool execution agent
    Replace this with actual tool_use_agent when the module is available
    """
    def __init__(self, config_path=None):
        self.config_path = config_path
        self.tools = []
    
    def execute_tool(self, tool_name, tool_input):
        """Placeholder tool execution"""
        return {"status": "Tool execution not implemented", "tool": tool_name}


class UnifiedAIClient:
    """
    Multi-provider AI client with unified interface
    
    Supported Providers:
    - Anthropic (Claude Sonnet, Haiku)
    - DeepSeek (deepseek-chat, deepseek-reasoner)
    - OpenAI (GPT-4o, GPT-4o-mini)
    
    Features:
    - Single interface for all providers
    - SSE streaming for all providers
    - System prompt routing by UI context
    - Server-side tool execution
    - Same SSE event format (NO UI CHANGES)
    """
    
    def __init__(self, config_path: str):
        """
        Initialize multi-provider AI client
        
        Args:
            config_path: Path to database-config.json
        """
        # Load config
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize all providers
        self._init_anthropic()
        self._init_deepseek()
        self._init_openai()
        
        # Initialize tool use agent (server-side tools)
        self.tool_agent = ToolUseAgent(config_path)
        
        print(f"[UnifiedAIClient] Initialized with providers:")
        print(f"  - Anthropic: {self.anthropic_model}")
        print(f"  - DeepSeek: {self.deepseek_model}")
        print(f"  - OpenAI: {self.openai_model}")
    
    def _init_anthropic(self):
        """Initialize Anthropic Claude client"""
        # Try environment variable first, then config file
        api_key = os.environ.get('ANTHROPIC_API_KEY') or self.config.get('AI', {}).get('AnthropicAPIKey', '')
        if api_key:
            self.anthropic_client = Anthropic(api_key=api_key)
        else:
            self.anthropic_client = None
            print("⚠️  Warning: No Anthropic API key found. Set ANTHROPIC_API_KEY environment variable.")
        self.anthropic_model = self.config.get('AI', {}).get('Model', 'claude-sonnet-4-20250514')
    
    def _init_deepseek(self):
        """Initialize DeepSeek client"""
        # Try environment variable first, then config file
        self.deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY') or self.config.get('AI', {}).get('DeepSeekAPIKey', '')
        self.deepseek_model = self.config.get('AI', {}).get('DeepSeekModel', 'deepseek-chat')
        self.deepseek_base_url = "https://api.deepseek.com/v1"
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        # Try environment variable first, then config file
        openai_key = os.environ.get('OPENAI_API_KEY') or self.config.get('AI', {}).get('OpenAIAPIKey', '')
        if openai_key:
            openai.api_key = openai_key
        self.openai_model = self.config.get('AI', {}).get('OpenAIModel', 'gpt-4o-mini')
    
    def get_system_prompt(self, ui_context: str, agent_id: Optional[str] = None) -> str:
        """
        Get system prompt for UI context
        
        Args:
            ui_context: 'stock_chat' | 'data_agent_chat' | 'single_viewer' | 'triple_agent'
            agent_id: For triple_agent: '1', '2', '3'
        
        Returns:
            System prompt string
        """
        if ui_context == 'stock_chat':
            return self._get_stock_chat_prompt()
        
        elif ui_context == 'data_agent_chat':
            return self._get_data_agent_prompt()
        
        elif ui_context == 'single_viewer':
            return self._get_single_viewer_prompt()
        
        elif ui_context == 'triple_agent':
            return self._get_triple_agent_prompt(agent_id)
        
        # Default fallback
        return "You are a helpful AI assistant with access to database and business tools."
    
    def process_streaming(
        self,
        session_id: str,
        session_data: Dict,
        prompt: str,
        files: Optional[List] = None,
        provider: Literal['anthropic', 'deepseek', 'openai'] = 'anthropic',
        sse_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """
        Process AI request with streaming (unified interface for all providers)
        
        Args:
            session_id: Session identifier
            session_data: Session data from UnifiedSessionManager
            prompt: User message
            files: Optional files (for Claude Vision)
            provider: AI provider to use
            sse_callback: Callback for SSE events (lambda event: queue.put(event))
        
        Returns:
            Updated conversation history
        """
        # Route to appropriate provider
        if provider == 'anthropic':
            return self._process_anthropic(session_id, session_data, prompt, files, sse_callback)
        
        elif provider == 'deepseek':
            return self._process_deepseek(session_id, session_data, prompt, sse_callback)
        
        elif provider == 'openai':
            return self._process_openai(session_id, session_data, prompt, sse_callback)
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _process_anthropic(
        self,
        session_id: str,
        session_data: Dict,
        prompt: str,
        files: Optional[List],
        sse_callback: Optional[Callable]
    ) -> List[Dict]:
        """Process with Anthropic Claude (streaming with tools)"""
        
        # Get system prompt
        system_prompt = self.get_system_prompt(
            session_data['ui_context'],
            session_data.get('agent_id')
        )
        
        # Build conversation
        conversation = session_data.get('conversation', [])
        
        # Build user message
        user_message = {'role': 'user', 'content': []}
        
        # Add files if present (Claude Vision)
        if files:
            for file_data in files:
                user_message['content'].append({
                    'type': 'image' if file_data['media_type'].startswith('image/') else 'document',
                    'source': {
                        'type': 'base64',
                        'media_type': file_data['media_type'],
                        'data': file_data['data']
                    }
                })
        
        # Add text
        user_message['content'].append({'type': 'text', 'text': prompt})
        
        # Add to conversation
        conversation.append(user_message)
        
        # Get tool definitions
        tools = self.tool_agent.get_tool_definitions()
        
        # Stream with Anthropic
        assistant_message = {'role': 'assistant', 'content': []}
        
        with self.anthropic_client.messages.stream(
            model=self.anthropic_model,
            max_tokens=12000,
            system=system_prompt,
            messages=conversation,
            tools=tools
        ) as stream:
            for event in stream:
                # Convert to SSE format
                sse_event = self._convert_anthropic_event_to_sse(event)
                
                if sse_event and sse_callback:
                    sse_callback(sse_event)
                
                # Build assistant message
                if event.type == 'content_block_start':
                    if event.content_block.type == 'text':
                        assistant_message['content'].append({'type': 'text', 'text': ''})
                    elif event.content_block.type == 'tool_use':
                        assistant_message['content'].append({
                            'type': 'tool_use',
                            'id': event.content_block.id,
                            'name': event.content_block.name,
                            'input': {}
                        })
                
                elif event.type == 'content_block_delta':
                    if event.delta.type == 'text_delta':
                        assistant_message['content'][-1]['text'] += event.delta.text
                    elif event.delta.type == 'input_json_delta':
                        # Accumulate tool input
                        pass
        
        # Handle tool use
        if any(block['type'] == 'tool_use' for block in assistant_message['content']):
            assistant_message = self._handle_tool_use(assistant_message, sse_callback)
        
        # Add to conversation
        conversation.append(assistant_message)
        
        return conversation
    
    def _process_deepseek(
        self,
        session_id: str,
        session_data: Dict,
        prompt: str,
        sse_callback: Optional[Callable]
    ) -> List[Dict]:
        """Process with DeepSeek (streaming)"""
        
        # Get system prompt
        system_prompt = self.get_system_prompt(
            session_data['ui_context'],
            session_data.get('agent_id')
        )
        
        # Build conversation
        conversation = session_data.get('conversation', [])
        
        # Convert to OpenAI format (DeepSeek uses OpenAI-compatible API)
        messages = [{'role': 'system', 'content': system_prompt}]
        
        for msg in conversation:
            # Convert Anthropic format to OpenAI format
            if msg['role'] == 'user':
                text_content = ''
                for block in msg['content']:
                    if block['type'] == 'text':
                        text_content += block['text']
                messages.append({'role': 'user', 'content': text_content})
            
            elif msg['role'] == 'assistant':
                text_content = ''
                for block in msg['content']:
                    if block['type'] == 'text':
                        text_content += block['text']
                messages.append({'role': 'assistant', 'content': text_content})
        
        # Add new user message
        messages.append({'role': 'user', 'content': prompt})
        
        # Call DeepSeek API (streaming)
        headers = {
            'Authorization': f'Bearer {self.deepseek_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.deepseek_model,
            'messages': messages,
            'stream': True,
            'max_tokens': 8000
        }
        
        response = requests.post(
            f'{self.deepseek_base_url}/chat/completions',
            headers=headers,
            json=payload,
            stream=True
        )
        
        assistant_text = ''
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    
                    try:
                        chunk = json.loads(data)
                        delta = chunk['choices'][0]['delta']
                        
                        if 'content' in delta:
                            text = delta['content']
                            assistant_text += text
                            
                            # Emit SSE event
                            if sse_callback:
                                sse_callback({
                                    'type': 'text_delta',
                                    'text': text,
                                    'index': 0
                                })
                    except:
                        pass
        
        # ✅ Add to conversation (Anthropic format for consistency)
        # DeepSeek doesn't support thinking blocks, but we preserve the format
        conversation.append({'role': 'user', 'content': [{'type': 'text', 'text': prompt}]})
        # NOTE: DeepSeek responses are text-only (no thinking/tool_use support)
        conversation.append({'role': 'assistant', 'content': [{'type': 'text', 'text': assistant_text}]})
        
        return conversation
    
    def _process_openai(
        self,
        session_id: str,
        session_data: Dict,
        prompt: str,
        sse_callback: Optional[Callable]
    ) -> List[Dict]:
        """Process with OpenAI GPT (streaming)"""
        
        # Get system prompt
        system_prompt = self.get_system_prompt(
            session_data['ui_context'],
            session_data.get('agent_id')
        )
        
        # Build conversation
        conversation = session_data.get('conversation', [])
        
        # Convert to OpenAI format
        messages = [{'role': 'system', 'content': system_prompt}]
        
        for msg in conversation:
            if msg['role'] == 'user':
                text_content = ''
                for block in msg['content']:
                    if block['type'] == 'text':
                        text_content += block['text']
                messages.append({'role': 'user', 'content': text_content})
            
            elif msg['role'] == 'assistant':
                text_content = ''
                for block in msg['content']:
                    if block['type'] == 'text':
                        text_content += block['text']
                messages.append({'role': 'assistant', 'content': text_content})
        
        # Add new user message
        messages.append({'role': 'user', 'content': prompt})
        
        # Call OpenAI API (streaming)
        response = openai.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            stream=True,
            max_tokens=8000
        )
        
        assistant_text = ''
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                assistant_text += text
                
                # Emit SSE event
                if sse_callback:
                    sse_callback({
                        'type': 'text_delta',
                        'text': text,
                        'index': 0
                    })
        
        # ✅ Add to conversation (Anthropic format for consistency)
        # OpenAI doesn't support thinking blocks, but we preserve the format
        conversation.append({'role': 'user', 'content': [{'type': 'text', 'text': prompt}]})
        # NOTE: OpenAI responses are text-only (no thinking/tool_use support)
        conversation.append({'role': 'assistant', 'content': [{'type': 'text', 'text': assistant_text}]})
        
        return conversation
    
    def _convert_anthropic_event_to_sse(self, event) -> Optional[Dict]:
        """Convert Anthropic event to SSE format (SAME AS BEFORE)"""
        
        if event.type == 'content_block_delta':
            if event.delta.type == 'text_delta':
                return {
                    'type': 'text_delta',
                    'text': event.delta.text,
                    'index': event.index
                }
        
        elif hasattr(event, 'delta') and hasattr(event.delta, 'type'):
            if event.delta.type == 'thinking_delta':
                return {
                    'type': 'thinking_delta',
                    'text': event.delta.text,
                    'index': event.index
                }
        
        return None
    
    def _handle_tool_use(self, assistant_message: Dict, sse_callback: Optional[Callable]) -> Dict:
        """Execute server-side tools"""
        
        for block in assistant_message['content']:
            if block['type'] == 'tool_use':
                # Emit tool use event
                if sse_callback:
                    sse_callback({
                        'type': 'tool_use',
                        'name': block['name'],
                        'input': block['input']
                    })
                
                # Execute tool
                result = self.tool_agent.execute_tool(block['name'], block['input'])
                
                # Emit tool result event
                if sse_callback:
                    sse_callback({
                        'type': 'tool_result',
                        'tool_use_id': block['id'],
                        'result': result
                    })
        
        return assistant_message
    
    # System prompts (same as unified_anthropic_client.py)
    def _get_stock_chat_prompt(self) -> str:
        """System prompt for Stock AI Chat"""
        return """You are a Stock Management AI Assistant with expertise in inventory, supplier relationships, and pricing.

Your role is to help manage stock inventory, analyze usage patterns, process invoices, and optimize purchasing decisions.

You have access to:
- Stock inventory database (unified_stocks, extracted_jobs)
- Quote calculator tools
- SQL query execution
- Invoice processing (document analysis with PDFs and images)

Communication style:
- Professional and data-driven
- Use tables for structured data
- Suggest actionable next steps
- Always compare to database when processing invoices"""
    
    def _get_data_agent_prompt(self) -> str:
        """System prompt for Data Agent Chat"""
        return """You are a Data Analysis AI Assistant with expertise in business intelligence and SQL.

Your role is to help analyze business data, generate insights, and answer complex queries about the printing business.

You have access to:
- Complete SQL Server database (production data)
- Business intelligence tools
- Advanced analytics capabilities

Communication style:
- Analytical and insight-driven
- Use visualizations when helpful
- Explain trends and patterns
- Provide actionable recommendations"""
    
    def _get_single_viewer_prompt(self) -> str:
        """System prompt for Single Viewer"""
        return """You are a general-purpose AI assistant for the printing business platform.

Your role is to help with various tasks and answer questions about the business.

Communication style:
- Clear and concise
- Helpful and proactive
- Suggest tools and features available"""
    
    def _get_triple_agent_prompt(self, agent_id: str) -> str:
        """System prompt for Triple Agent"""
        
        if agent_id == '1':
            return """You are Agent 1: The Stock & Inventory Specialist.

Your expertise:
- Stock management and inventory tracking
- Supplier relationships and pricing
- Invoice processing and cost analysis

Focus on stock-related queries and provide detailed inventory insights."""
        
        elif agent_id == '2':
            return """You are Agent 2: The Data & Analytics Specialist.

Your expertise:
- Business intelligence and reporting
- SQL queries and data analysis
- Trends, patterns, and forecasting

Focus on data-driven insights and analytical queries."""
        
        elif agent_id == '3':
            return """You are Agent 3: The Operations & Quote Specialist.

Your expertise:
- Quote calculations and pricing
- Production workflows and job management
- Customer orders and business operations

Focus on operational queries and quote assistance."""
        
        return "You are a helpful AI assistant."


# Create singleton instance (loaded from config when Flask app starts)
ai_client = None

def initialize_ai_client(config_path: str):
    """Initialize the global AI client instance"""
    global ai_client
    ai_client = UnifiedAIClient(config_path)
    return ai_client

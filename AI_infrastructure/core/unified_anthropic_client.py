"""
Unified Anthropic Client
Single reusable Anthropic client for ALL AI interactions

Replaces:
- Multiple anthropic.Anthropic() instantiations across endpoints
- Duplicate streaming logic
- Scattered system prompts
- Inconsistent SSE event formats

Features:
- Single Anthropic client instance (reusable)
- Unified streaming logic with SSE
- System prompt routing by UI context
- Tool execution integration
- Same SSE event format as existing system (NO UI CHANGES)
"""

from anthropic import Anthropic
import json
from typing import Dict, List, Optional, Callable, Any
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the new 281-tool registry system
try:
    from tools.registry import ToolRegistry
    TOOL_REGISTRY_AVAILABLE = True
    print("[OK] Tool Registry loaded - 281 tools available")
except ImportError as e:
    TOOL_REGISTRY_AVAILABLE = False
    print(f"[WARNING] Tool Registry not available: {e}")
    print("          Continuing without tool execution capability")


class UnifiedAnthropicClient:
    """
    Single Anthropic client instance for all UIs
    
    Architecture:
    - ONE client instance (not 10+)
    - System prompts per UI context
    - Server-side tool execution
    - SSE streaming (SAME format as existing system)
    - NO client-side tools (Plotly/Mermaid already render)
    """
    
    def __init__(self, config_path: str):
        """
        Initialize unified client
        
        Args:
            config_path: Path to database-config.json
        """
        # Load config
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize Anthropic client (SINGLE INSTANCE)
        self.client = Anthropic(api_key=self.config['AI']['AnthropicAPIKey'])
        self.model = self.config['AI']['Model']
        
        # Initialize tool registry (NEW: 281-tool system)
        if TOOL_REGISTRY_AVAILABLE:
            self.tool_registry = ToolRegistry()
            print(f"[UnifiedAnthropicClient] Tool Registry initialized - {len(self.tool_registry.tools)} tools loaded")
        else:
            self.tool_registry = None
            print("[UnifiedAnthropicClient] [WARNING] Running without tool execution capability")
        
        print(f"[UnifiedAnthropicClient] Initialized with model: {self.model}")
    
    def process_files_to_content_blocks(self, files: List) -> List[Dict]:
        """
        Process uploaded files into Anthropic content blocks
        
        Args:
            files: List of Flask FileStorage objects
        
        Returns:
            List of content blocks (text + images)
        """
        content_blocks = []
        
        # Add text prompt first
        text_prompt = "Please analyze the uploaded files:"
        content_blocks.append({"type": "text", "text": text_prompt})
        
        # Process each file
        for file in files:
            try:
                # Read file content
                file_content = file.read()
                file.seek(0)  # Reset file pointer
                
                # Check if image
                if file.content_type and file.content_type.startswith('image/'):
                    import base64
                    # Convert to base64
                    image_data = base64.b64encode(file_content).decode('utf-8')
                    
                    # Add image block
                    content_blocks.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": file.content_type,
                            "data": image_data
                        }
                    })
                else:
                    # Text file - decode and add as text
                    try:
                        text_content = file_content.decode('utf-8')
                        content_blocks.append({
                            "type": "text",
                            "text": f"File: {file.filename}\n\n{text_content}"
                        })
                    except UnicodeDecodeError:
                        content_blocks.append({
                            "type": "text",
                            "text": f"File: {file.filename} (binary file, cannot display)"
                        })
            except Exception as e:
                print(f"[UnifiedAnthropicClient] Error processing file {file.filename}: {e}")
                content_blocks.append({
                    "type": "text",
                    "text": f"Error processing file: {file.filename}"
                })
        
        return content_blocks
    
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
    
    def _get_stock_chat_prompt(self) -> str:
        """System prompt for Stock AI Chat"""
        return """You are a Stock Management AI Assistant with expertise in inventory, supplier relationships, and pricing.

Your role is to help manage stock inventory, analyze usage patterns, process invoices, and optimize purchasing decisions.

You have access to:
- Stock inventory database (unified_stocks, extracted_jobs)
- Quote calculator tools
- SQL query execution
- Invoice processing (document analysis with PDFs and images)

Key responsibilities:
1. Answer questions about stock levels, costs, suppliers
2. Analyze stock usage patterns and trends
3. Help process supplier invoices with AI extraction
4. Suggest reorder points and quantities
5. Compare supplier pricing
6. Identify cost-saving opportunities

Always:
- Provide specific numbers (stock IDs, quantities, costs)
- Show calculations transparently
- Suggest actionable next steps
- Ask for confirmation before major changes

Available tools include SQL queries, stock lookups, invoice processing, and quote calculations."""
    
    def _get_data_agent_prompt(self) -> str:
        """System prompt for Data Agent Chat"""
        return """You are a Data Analysis AI Assistant specializing in business intelligence for a printing company.

Your role is to analyze production data, client trends, job history, and business metrics.

You have access to:
- Production database (JobTickets, Orders, Clients)
- Quote calculator tools
- SQL query execution
- Business analytics functions

Key responsibilities:
1. Analyze business performance (revenue, jobs, clients)
2. Identify trends in client behavior and product demand
3. Generate insights from production data
4. Help with forecasting and planning
5. Create custom reports and visualizations

Always:
- Use data to support your insights
- Show SQL queries when relevant
- Provide actionable recommendations
- Visualize data when helpful (Plotly charts, tables)

Be analytical, data-driven, and business-focused."""
    
    def _get_single_viewer_prompt(self) -> str:
        """System prompt for Single Viewer"""
        return """You are a versatile AI assistant for a printing business management system.

You have access to:
- Complete production database
- Stock inventory system
- Quote calculator tools
- SQL query execution
- Business analytics

You can help with:
- Business questions and analysis
- Stock management queries
- Quote calculations
- Data exploration
- Report generation

Always be helpful, accurate, and provide specific actionable information."""
    
    def _get_triple_agent_prompt(self, agent_id: Optional[str]) -> str:
        """System prompts for Triple Agent (3 specialized agents)"""
        prompts = {
            '1': """You are Agent 1: SQL Query Specialist

Your expertise: Database queries, data extraction, and business intelligence.

Focus on:
- Writing efficient SQL queries
- Analyzing production data
- Client and job history
- Revenue and performance metrics
- Data exploration

Always show the SQL queries you use and explain the results clearly.""",

            '2': """You are Agent 2: Quote Calculator Expert

Your expertise: Pricing, cost calculations, and quote generation.

Focus on:
- Calculating accurate quotes
- Stock cost analysis
- Pricing strategy
- Profit margin optimization
- Product recommendations

Always show your calculations and explain pricing logic.""",

            '3': """You are Agent 3: Business Intelligence Analyst

Your expertise: Trends, forecasting, and strategic insights.

Focus on:
- Business trends and patterns
- Client behavior analysis
- Product performance
- Market insights
- Strategic recommendations

Always provide data-driven insights with actionable recommendations."""
        }
        
        return prompts.get(agent_id, prompts['1'])
    
    def get_tools(self, ui_context: str) -> List[Dict]:
        """
        Get tools for UI context
        Returns server tools only (NO client tools - Plotly/Mermaid already render)
        
        Args:
            ui_context: UI context
        
        Returns:
            List of tool definitions (Anthropic format)
        """
        if not self.tool_registry:
            return []
        
        # Get all tools from the registry
        all_tools = self.tool_registry.list_tools()
        
        # Convert to Anthropic tool format
        anthropic_tools = []
        for tool in all_tools:
            # Convert tool schema to Anthropic format
            anthropic_tool = {
                "name": tool.get("name"),
                "description": tool.get("description", ""),
                "input_schema": {
                    "type": "object",
                    "properties": tool.get("parameters", {}),
                    "required": [
                        param for param, spec in tool.get("parameters", {}).items()
                        if spec.get("required", False)
                    ]
                }
            }
            anthropic_tools.append(anthropic_tool)
        
        # Filter by UI context if needed (future enhancement)
        # For now, all UIs get all 281 tools
        return anthropic_tools
    
    async def process_streaming(
        self,
        session_id: str,
        session_data: Dict,
        prompt: str,
        files: Optional[List] = None,
        sse_callback: Optional[Callable] = None
    ):
        """
        Process AI request with streaming
        
        Args:
            session_id: Session ID
            session_data: Session data dict (from session_manager)
            prompt: User message
            files: Optional file uploads (Flask FileStorage objects)
            sse_callback: Function to emit SSE events - callback(event_dict)
        
        SSE Event Format (SAME as existing system):
            {'type': 'content_block_start', 'index': 0, 'block_type': 'text', 'message_id': '...'}
            {'type': 'content_block_delta', 'index': 0, 'delta_type': 'text_delta', 'text': '...'}
            {'type': 'content_block_delta', 'index': 1, 'delta_type': 'thinking_delta', 'thinking': '...'}
            {'type': 'tool_result', 'tool_name': '...', 'result': {...}, 'success': True}
            {'type': 'done', 'final_message': {...}}
        """
        # Get system prompt
        system_prompt = self.get_system_prompt(
            session_data['ui_context'],
            session_data.get('agent_id')
        )
        
        # Get tools
        tools = self.get_tools(session_data['ui_context'])
        
        # Get conversation history
        conversation = session_data.get('conversation', [])
        
        # Build user message
        user_message = {"role": "user", "content": prompt}
        
        # Process files if provided
        if files:
            content_blocks = self.process_files_to_content_blocks(files)
            user_message['content'] = content_blocks
        
        # Add to conversation
        conversation.append(user_message)
        
        # Stream with Anthropic API
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=8000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 10000
                },
                system=system_prompt,
                messages=conversation,
                tools=tools
            ) as stream:
                
                # Track content blocks
                block_index = 0
                current_blocks = []
                
                for event in stream:
                    # Convert to SSE event format (SAME as existing system)
                    sse_event = self._convert_event_to_sse(event, block_index)
                    
                    # Track block index
                    if hasattr(event, 'type'):
                        if event.type == 'content_block_start':
                            block_index = event.index
                        elif event.type == 'content_block_delta':
                            block_index = event.index
                    
                    # Emit via callback
                    if sse_callback and sse_event:
                        sse_callback(sse_event)
                
                # Get final message
                final_message = stream.get_final_message()
            
            # Handle tool use
            if final_message.stop_reason == 'tool_use':
                # Execute server tools and continue conversation
                await self._handle_tool_use(
                    final_message,
                    conversation,
                    session_id,
                    session_data,
                    sse_callback
                )
            else:
                # Add assistant response to conversation
                conversation.append({
                    "role": "assistant",
                    "content": final_message.content
                })
                
                # Emit completion
                if sse_callback:
                    sse_callback({
                        'type': 'done',
                        'final_message': {
                            'content': [self._content_block_to_dict(c) for c in final_message.content],
                            'stop_reason': final_message.stop_reason
                        }
                    })
            
            # Return updated conversation
            return conversation
        
        except Exception as e:
            print(f"[UnifiedAnthropicClient] Error during streaming: {e}")
            if sse_callback:
                sse_callback({
                    'type': 'error',
                    'message': str(e)
                })
            raise
    
    async def _handle_tool_use(
        self,
        final_message,
        conversation: List[Dict],
        session_id: str,
        session_data: Dict,
        sse_callback: Optional[Callable]
    ):
        """
        Handle tool execution and continue conversation
        
        Args:
            final_message: Anthropic final message with tool_use blocks
            conversation: Conversation history
            session_id: Session ID
            session_data: Session data
            sse_callback: SSE callback function
        """
        # Add assistant message with tool use
        conversation.append({
            "role": "assistant",
            "content": final_message.content
        })
        
        # Execute each tool
        tool_results = []
        for content in final_message.content:
            if content.type == 'tool_use':
                try:
                    # Execute tool using NEW ToolRegistry (281 tools)
                    if self.tool_registry:
                        result = self.tool_registry.execute_tool(
                            content.name,
                            **content.input
                        )
                    else:
                        result = {
                            'success': False,
                            'error': 'Tool registry not available'
                        }
                    
                    # Emit tool result event
                    if sse_callback:
                        sse_callback({
                            'type': 'tool_result',
                            'tool_name': content.name,
                            'result': result,
                            'success': result.get('success', True)
                        })
                    
                    # Add to results
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": json.dumps(result) if not isinstance(result, str) else result
                    })
                
                except Exception as e:
                    print(f"[UnifiedAnthropicClient] Tool execution error ({content.name}): {e}")
                    
                    # Emit error
                    if sse_callback:
                        sse_callback({
                            'type': 'tool_result',
                            'tool_name': content.name,
                            'result': {'error': str(e)},
                            'success': False
                        })
                    
                    # Add error result
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "is_error": True,
                        "content": str(e)
                    })
        
        # Add tool results to conversation
        conversation.append({
            "role": "user",
            "content": tool_results
        })
        
        # Continue conversation with tool results
        await self.process_streaming(
            session_id,
            session_data,
            "",  # Empty prompt (continuing from tool results)
            files=None,
            sse_callback=sse_callback
        )
    
    def _convert_event_to_sse(self, event, block_index: int) -> Optional[Dict]:
        """
        Convert Anthropic event to SSE format
        SAME format as existing system (NO UI CHANGES)
        
        Args:
            event: Anthropic stream event
            block_index: Current content block index
        
        Returns:
            SSE event dict or None
        """
        if not hasattr(event, 'type'):
            return None
        
        event_type = event.type
        
        # Content block start
        if event_type == 'content_block_start':
            block_type = event.content_block.type  # 'text', 'thinking', 'tool_use'
            
            sse_event = {
                'type': 'content_block_start',
                'index': event.index,
                'block_type': block_type
            }
            
            # Add tool name if tool_use
            if block_type == 'tool_use':
                sse_event['tool_name'] = event.content_block.name
            
            return sse_event
        
        # Content block delta
        elif event_type == 'content_block_delta':
            delta_type = event.delta.type  # 'text_delta', 'thinking_delta', 'input_json_delta'
            
            sse_event = {
                'type': 'content_block_delta',
                'index': event.index,
                'delta_type': delta_type
            }
            
            # Add delta content
            if delta_type == 'text_delta':
                sse_event['text'] = event.delta.text
            elif delta_type == 'thinking_delta':
                sse_event['thinking'] = event.delta.thinking
            elif delta_type == 'input_json_delta':
                sse_event['partial_json'] = event.delta.partial_json
            
            return sse_event
        
        # Content block stop
        elif event_type == 'content_block_stop':
            return {
                'type': 'content_block_stop',
                'index': event.index
            }
        
        # Message delta
        elif event_type == 'message_delta':
            return {
                'type': 'message_delta',
                'stop_reason': event.delta.stop_reason if hasattr(event.delta, 'stop_reason') else None
            }
        
        # Message stop
        elif event_type == 'message_stop':
            return {
                'type': 'message_stop'
            }
        
        return None
    
    def _content_block_to_dict(self, content_block) -> Dict:
        """Convert Anthropic content block to dict"""
        if content_block.type == 'text':
            return {
                'type': 'text',
                'text': content_block.text
            }
        elif content_block.type == 'thinking':
            return {
                'type': 'thinking',
                'thinking': content_block.thinking,
                'signature': getattr(content_block, 'signature', '')  # Required by Anthropic API
            }
        elif content_block.type == 'tool_use':
            return {
                'type': 'tool_use',
                'id': content_block.id,
                'name': content_block.name,
                'input': content_block.input
            }
        else:
            return {'type': content_block.type}


# Global singleton instance
# Initialize with config path (will be set by Flask app)
anthropic_client = None

def init_anthropic_client(config_path: str):
    """Initialize global anthropic_client instance"""
    global anthropic_client
    anthropic_client = UnifiedAnthropicClient(config_path)
    return anthropic_client

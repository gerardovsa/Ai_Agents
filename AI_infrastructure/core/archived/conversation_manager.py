"""
Conversation Manager - Orchestrate multi-turn conversations with Claude
Part of V4 Modular Architecture

Responsibilities:
- Orchestrate conversation flow
- Integrate all V4 modules
- Handle Claude API communication
- Manage tool execution workflow
- Process multi-turn conversations
"""

from typing import Dict, Any, List, Optional
import sys
from pathlib import Path
import os

# Add paths
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

tools_dir = ai_infra_dir.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

# Third-party
import anthropic

# V4 Infrastructure modules
from AI_infrastructure.utils.logger import get_logger
from AI_infrastructure.config.constants import (
    MAX_TURNS, MAX_TOKENS, CLAUDE_MODEL, TEMPERATURE,
    THINKING_BUDGET, ANTHROPIC_BETA_HEADERS
)

# Core modules
from AI_infrastructure.core.tool_executor import ToolExecutor
from AI_infrastructure.core.tool_processor import ToolCallProcessor
from AI_infrastructure.core.session_handler import SessionHandler
from AI_infrastructure.core.response_serializer import ResponseSerializer

# Builder modules
from AI_infrastructure.builders.user_profile_builder import UserProfileBuilder
from AI_infrastructure.builders.system_prompt_builder import SystemPromptBuilder
from AI_infrastructure.builders.tool_schema_converter import ToolSchemaConverter
from AI_infrastructure.builders.credential_fetcher import CredentialFetcher

# Tool registry
from tools.registry_v3 import RegistryV3

logger = get_logger(__name__)


class ConversationManager:
    """
    Orchestrates multi-turn conversations with Claude API.
    
    Integrates all V4 modules:
    - UserProfileBuilder: Get user context
    - SystemPromptBuilder: Build system prompt
    - ToolSchemaConverter: Format tools for Claude
    - CredentialFetcher: Get OAuth credentials
    - ToolExecutor: Execute tools with credentials
    - ToolCallProcessor: Process tool_use blocks
    - ResponseSerializer: Format responses
    - SessionHandler: Manage conversation state
    
    Usage:
        manager = ConversationManager(api_key="sk-ant-...")
        
        response = manager.start_conversation(
            user_id=1,
            message="Send an email to john@example.com"
        )
        
        print(response['response'])  # Claude's text response
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize conversation manager.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        logger.info("🎭 Initializing ConversationManager")
        
        # Get API key
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or parameters")
        
        # Initialize Anthropic client with beta headers
        if ANTHROPIC_BETA_HEADERS:
            # Pass beta headers to client initialization (for extended thinking)
            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                default_headers={"anthropic-beta": ",".join(ANTHROPIC_BETA_HEADERS)}
            )
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.debug("Anthropic client initialized")
        
        # Initialize tool registry
        self.registry = RegistryV3()
        logger.debug(f"Tool registry loaded: {len(self.registry.tools)} tools")
        
        # Initialize module instances
        self.tool_executor = ToolExecutor()
        self.tool_processor = ToolCallProcessor(self.tool_executor)
        self.session_handler = SessionHandler()
        self.response_serializer = ResponseSerializer()
        self.user_profile_builder = UserProfileBuilder()
        self.system_prompt_builder = SystemPromptBuilder()
        self.tool_schema_converter = ToolSchemaConverter()
        self.credential_fetcher = CredentialFetcher()
        
        logger.info(f"ConversationManager ready: {len(self.registry.tools)} tools available")

    def handle_chat(self, 
                   user_id: int, 
                   message: str,
                   session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point for handling chat requests.
        Alias for start_conversation() to match V4 guide naming.
        
        Args:
            user_id: User ID
            message: User's message
            session_id: Optional session ID (creates new if None)
            
        Returns:
            Response dict with clean text (no raw XML tool calls)
        """
        return self.start_conversation(user_id, message, session_id)

    def start_conversation(self, 
                          user_id: int, 
                          message: str,
                          session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new conversation or continue existing one.
        
        Args:
            user_id: User ID
            message: User's message
            session_id: Optional session ID (creates new if None)
            
        Returns:
            Response dict:
            {
                "session_id": str,
                "response": str,
                "thinking": str,
                "tool_calls": [],
                "turn_count": int,
                "stop_reason": str,
                "usage": {...}
            }
            
        Example:
            response = manager.start_conversation(
                user_id=1,
                message="What emails do I have from John?"
            )
            print(f"Session: {response['session_id']}")
            print(f"Response: {response['response']}")
        """
        logger.info(f"🎬 Starting conversation: user_id={user_id}, "
                   f"session_id={session_id or 'new'}")
        
        try:
            # 1. Load or create session
            if session_id:
                session = self.session_handler.load_session(
                    session_id, 
                    create_if_missing=True,
                    user_id=user_id
                )
            else:
                session = self.session_handler.create_session(user_id=user_id)
                session_id = session['session_id']
            
            logger.debug(f"📂 Session: {session_id[:8]}... "
                        f"({len(session['conversation'])} existing messages)")
            
            # 2. Build system prompt with user context
            system_prompt = self._build_system_prompt(user_id)
            logger.debug(f"📝 System prompt: {len(system_prompt)} chars")
            
            # 3. Get available tools for user
            tools = self._get_tools_for_user(user_id)
            logger.debug(f"🔧 Available tools: {len(tools)} tools")
            
            # 4. Start conversation loop
            result = self._conversation_loop(
                session_id=session_id,
                user_id=user_id,
                user_message=message,
                system_prompt=system_prompt,
                tools=tools
            )
            
            logger.info(f"Conversation complete: {result['turn_count']} turns, "
                       f"{result['usage']['total_tokens']} tokens")
            
            return result
            
        except Exception as e:
            logger.error(f" Conversation error: {e}")
            return self.response_serializer.serialize_error(e)

    def _build_system_prompt(self, user_id: int) -> str:
        """
        Build system prompt with user context.
        
        Args:
            user_id: User ID
            
        Returns:
            Complete system prompt string
        """
        logger.debug(f"🔨 Building system prompt for user_id={user_id}")
        
        # Get user context
        user_context = self.user_profile_builder.build_prompt_context(user_id)
        
        # Get available platforms
        capabilities = self.user_profile_builder.get_user_capabilities(user_id)
        platforms = capabilities['available_platforms']
        
        # Build complete prompt
        prompt = self.system_prompt_builder.build_prompt(
            user_context=user_context,
            available_platforms=platforms,
            include_tool_patterns=True,
            include_anti_xml=True
        )
        
        logger.debug(f"System prompt built: {len(prompt)} chars, "
                    f"{len(platforms)} platforms")
        
        return prompt

    def _get_tools_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get tools available to user based on OAuth connections.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Anthropic-formatted tool schemas
        """
        logger.debug(f"🔍 Getting tools for user_id={user_id}")
        
        # Get user's available platforms
        capabilities = self.user_profile_builder.get_user_capabilities(user_id)
        platforms = capabilities['available_platforms']
        
        # Get all tool schemas from registry
        all_tools = list(self.registry.tools.values())
        
        # Convert and filter by user's platforms
        user_tools = self.tool_schema_converter.convert_and_filter(
            all_tools,
            platforms=platforms
        )
        
        logger.info(f"Filtered tools: {len(user_tools)} available "
                   f"(from {len(all_tools)} total)")
        
        return user_tools

    def _conversation_loop(self,
                          session_id: str,
                          user_id: int,
                          user_message: str,
                          system_prompt: str,
                          tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main conversation loop with tool execution.
        
        Args:
            session_id: Session ID
            user_id: User ID
            user_message: User's message
            system_prompt: System prompt
            tools: Available tools
            
        Returns:
            Final response dict
        """
        logger.debug(f"🔄 Starting conversation loop (max {MAX_TURNS} turns)")
        
        # Get conversation history
        conversation = self.session_handler.get_conversation(session_id)
        
        # Add user message
        conversation.append({
            'role': 'user',
            'content': user_message
        })
        
        turn_count = 0
        last_response = None
        
        # Loop until done or max turns
        while turn_count < MAX_TURNS:
            turn_count += 1
            logger.info(f"🔄 Turn {turn_count}/{MAX_TURNS}")
            
            # Call Claude API
            response = self._call_claude_api(
                conversation=conversation,
                system_prompt=system_prompt,
                tools=tools
            )
            
            last_response = response
            
            # Add assistant response to conversation
            conversation.append({
                'role': 'assistant',
                'content': response['content']
            })
            
            # Process response (check for tool calls)
            processed = self._process_claude_response(response, user_id)
            
            # Check if should continue
            if not self._should_continue(response, turn_count):
                logger.debug(f"🛑 Stopping: stop_reason={response.get('stop_reason')}")
                break
            
            # If no tool calls, we're done
            if not processed['has_tool_calls']:
                logger.debug("🛑 Stopping: no tool calls")
                break
            
            # Add tool results to conversation
            if processed['result_blocks']:
                conversation.append({
                    'role': 'user',
                    'content': processed['result_blocks']
                })
                logger.debug(f"➕ Added {len(processed['result_blocks'])} tool results")
        
        # Save updated conversation
        self.session_handler.save_session(session_id, conversation)
        logger.debug(f"💾 Saved conversation: {len(conversation)} messages")
        
        # Build final response
        final_response = self._build_final_response(
            response=last_response,
            session_id=session_id,
            turn_count=turn_count
        )
        
        return final_response

    def _call_claude_api(self,
                        conversation: List[Dict[str, Any]],
                        system_prompt: str,
                        tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Call Claude API with conversation and tools.
        
        Args:
            conversation: Conversation history
            system_prompt: System prompt
            tools: Available tools
            
        Returns:
            Claude API response dict
        """
        logger.debug(f"📞 Calling Claude API: {len(conversation)} messages, "
                    f"{len(tools)} tools")
        
        try:
            # Build request
            request_params = {
                'model': CLAUDE_MODEL,
                'max_tokens': MAX_TOKENS,
                'temperature': TEMPERATURE,
                'system': [{'type': 'text', 'text': system_prompt}],
                'messages': conversation
            }
            
            # Add tools if available
            if tools:
                request_params['tools'] = tools
            
            # Add extended thinking (beta headers already in client initialization)
            if ANTHROPIC_BETA_HEADERS:
                request_params['thinking'] = {
                    'type': 'enabled',
                    'budget_tokens': THINKING_BUDGET
                }
            
            # Make API call
            response = self.client.messages.create(**request_params)
            
            # Convert to dict
            response_dict = {
                'id': response.id,
                'model': response.model,
                'role': response.role,
                'content': response.content,
                'stop_reason': response.stop_reason,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                }
            }
            
            logger.debug(f"API response: stop_reason={response.stop_reason}, "
                        f"{response_dict['usage']['total_tokens']} tokens")
            
            return response_dict
            
        except anthropic.APIError as e:
            logger.error(f" Claude API error: {e}")
            raise

    def _process_claude_response(self, 
                                response: Dict[str, Any],
                                user_id: int) -> Dict[str, Any]:
        """
        Process Claude response and execute tools if needed.
        
        Args:
            response: Claude API response
            user_id: User ID
            
        Returns:
            Processed response dict with tool results
        """
        logger.debug("🔍 Processing Claude response")
        
        # Get user credentials
        credentials = self.credential_fetcher.get_all_credentials(user_id)
        
        # Process response with tool processor
        processed = self.tool_processor.process_response(
            response=response,
            user_id=user_id,
            credentials=credentials
        )
        
        if processed['has_tool_calls']:
            logger.info(f"🔧 Executed {len(processed['tool_calls'])} tools")
        
        return processed

    def _should_continue(self, response: Dict[str, Any], turn_count: int) -> bool:
        """
        Check if conversation should continue.
        
        Args:
            response: Claude API response
            turn_count: Current turn count
            
        Returns:
            True to continue, False to stop
        """
        # Check turn limit
        if turn_count >= MAX_TURNS:
            logger.warning(f"⚠️ Max turns reached: {MAX_TURNS}")
            return False
        
        # Check stop reason
        stop_reason = response.get('stop_reason')
        
        if stop_reason == 'end_turn':
            logger.debug("🛑 Claude finished (end_turn)")
            return False
        
        if stop_reason == 'max_tokens':
            logger.warning("⚠️ Token limit reached")
            return False
        
        if stop_reason == 'tool_use':
            logger.debug("🔧 Continuing for tool execution")
            return True
        
        # Default: continue
        return True

    def _build_final_response(self,
                             response: Dict[str, Any],
                             session_id: str,
                             turn_count: int) -> Dict[str, Any]:
        """
        Build final response dict.
        
        Args:
            response: Last Claude response
            session_id: Session ID
            turn_count: Total turn count
            
        Returns:
            Final response dict
        """
        logger.debug("📦 Building final response")
        
        # Serialize response
        serialized = self.response_serializer.serialize_response(
            response,
            include_metadata=True
        )
        
        # Build final dict
        final = {
            'session_id': session_id,
            'response': serialized['text'],
            'thinking': serialized['thinking'],
            'tool_calls': serialized['tool_calls'],
            'turn_count': turn_count,
            'stop_reason': response.get('stop_reason'),
            'usage': response.get('usage', {})
        }
        
        logger.debug(f"Final response: {len(final['response'])} chars text, "
                    f"{len(final['thinking'])} chars thinking")
        
        return final


# Export
__all__ = ['ConversationManager']

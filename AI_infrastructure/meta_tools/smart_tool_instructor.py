"""
Smart Tool Instructor - Context-aware tool recommendations
Part of V4 Modular Architecture - Meta-Tools

Responsibilities:
- Analyze user requests
- Recommend appropriate tools
- Consider user's available platforms (OAuth status)
- Provide tool sequences with rationale
"""

from typing import Dict, Any, List, Optional
import sys
import logging
from pathlib import Path

# Add paths
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

tools_dir = ai_infra_dir.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from tools.registry_v3 import RegistryV3

logger = logging.getLogger(__name__)


class SmartToolInstructor:
    """
    Provides context-aware tool recommendations based on user intent.
    
    This is a meta-tool that helps AI choose the right tools for a task.
    
    Usage:
        instructor = SmartToolInstructor(registry, user_platforms)
        
        # Get recommendations for a request
        recommendations = instructor.recommend_tools(
            "Send an email to John about the invoice",
            user_platforms=['google_workspace']
        )
        print(recommendations)
    """

    def __init__(self, registry: RegistryV3 = None):
        """
        Initialize smart tool instructor.
        
        Args:
            registry: Optional RegistryV3 instance (creates new if None)
        """
        logger.info("SmartToolInstructor initialized")
        
        # Initialize registry
        self.registry = registry or RegistryV3()
        
        # Intent patterns
        self.intent_patterns = {
            'email': ['send', 'email', 'mail', 'message', 'write to', 'contact'],
            'search': ['find', 'search', 'look for', 'locate', 'get'],
            'document': ['create', 'document', 'doc', 'file', 'write'],
            'calendar': ['schedule', 'meeting', 'appointment', 'event', 'book'],
            'quote': ['quote', 'price', 'cost', 'calculate', 'estimate'],
            'file': ['upload', 'download', 'file', 'folder', 'share']
        }

    def recommend_tools(
        self, 
        user_request: str, 
        user_platforms: Optional[List[str]] = None
    ) -> str:
        """
        Recommend tools based on user request.
        
        Args:
            user_request: User's natural language request
            user_platforms: List of platforms user has connected (e.g., ['google_workspace'])
            
        Returns:
            Formatted recommendations with rationale
            
        Example:
            recommendations = instructor.recommend_tools(
                "Send an email to john@example.com about the invoice",
                user_platforms=['google_workspace']
            )
        """
        logger.debug(f"Analyzing request: {user_request}")
        
        # Detect intent
        intent = self._detect_intent(user_request)
        logger.info(f"Detected intent: {intent}")
        
        # Get relevant tools
        relevant_tools = self._get_tools_for_intent(intent, user_platforms)
        
        # Build recommendation
        recommendation = self._build_recommendation(
            user_request,
            intent,
            relevant_tools,
            user_platforms
        )
        
        logger.info(f"Generated recommendations for: {intent}")
        return recommendation

    def _detect_intent(self, user_request: str) -> str:
        """
        Detect user intent from request.
        
        Args:
            user_request: User's request text
            
        Returns:
            Intent category (email, search, document, calendar, quote, file, unknown)
        """
        request_lower = user_request.lower()
        
        # Check each intent pattern
        for intent, keywords in self.intent_patterns.items():
            if any(keyword in request_lower for keyword in keywords):
                return intent
        
        return 'unknown'

    def _get_tools_for_intent(
        self, 
        intent: str, 
        user_platforms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get relevant tools for an intent.
        
        Args:
            intent: Detected intent category
            user_platforms: User's available platforms
            
        Returns:
            List of relevant tool dictionaries
        """
        all_tools = []
        
        # ToolRegistry has flat dictionary: {tool_name: tool_schema, ...}
        # Each tool_schema has: name, description, platform, parameters, etc.
        if hasattr(self.registry, 'tools') and isinstance(self.registry.tools, dict):
            for tool_name, tool_schema in self.registry.tools.items():
                if isinstance(tool_schema, dict):
                    all_tools.append({
                        'name': tool_name,
                        'platform': tool_schema.get('platform', 'unknown'),
                        'module': 'unknown',
                        'schema': tool_schema
                    })
        
        # Filter by intent
        relevant = []
        intent_keywords = self.intent_patterns.get(intent, [])
        
        for tool in all_tools:
            tool_name = tool['name'].lower()
            description = tool['schema'].get('description', '').lower()
            
            # Check if tool matches intent
            if any(keyword in tool_name or keyword in description for keyword in intent_keywords):
                # Filter by user platforms if provided
                if user_platforms is None or tool['platform'] in user_platforms:
                    relevant.append(tool)
        
        return relevant

    def _build_recommendation(
        self,
        user_request: str,
        intent: str,
        relevant_tools: List[Dict[str, Any]],
        user_platforms: Optional[List[str]] = None
    ) -> str:
        """
        Build formatted recommendation.
        
        Args:
            user_request: Original user request
            intent: Detected intent
            relevant_tools: List of relevant tools
            user_platforms: User's available platforms
            
        Returns:
            Formatted recommendation text
        """
        if not relevant_tools:
            return self._build_no_tools_response(intent, user_platforms)
        
        # Group by platform
        by_platform = {}
        for tool in relevant_tools:
            platform = tool['platform']
            if platform not in by_platform:
                by_platform[platform] = []
            by_platform[platform].append(tool)
        
        # Build recommendation text
        lines = [
            f"=== TOOL RECOMMENDATIONS ===",
            f"",
            f"USER REQUEST: {user_request}",
            f"DETECTED INTENT: {intent.upper()}",
            f"",
            f"RECOMMENDED APPROACH:",
            f""
        ]
        
        # Add platform-specific recommendations
        for platform, tools in by_platform.items():
            lines.append(f"--- {platform.upper()} ---")
            lines.append("")
            
            for tool in tools[:5]:  # Limit to 5 tools per platform
                tool_name = tool['name']
                description = tool['schema'].get('description', 'No description')
                
                lines.append(f"Tool: {tool_name}")
                lines.append(f"Description: {description}")
                
                # Add parameter info
                params = tool['schema'].get('parameters', {}).get('properties', {})
                if params:
                    lines.append("Parameters:")
                    for param_name, param_info in list(params.items())[:3]:  # First 3 params
                        param_desc = param_info.get('description', 'No description')
                        lines.append(f"  - {param_name}: {param_desc}")
                
                lines.append("")
        
        # Add usage advice
        lines.extend([
            "USAGE ADVICE:",
            self._get_intent_advice(intent),
            "",
            "NEXT STEPS:",
            "1. Review recommended tools above",
            "2. Check required parameters",
            "3. Execute tool(s) with appropriate values",
            "4. Handle response and proceed with next steps"
        ])
        
        return "\n".join(lines)

    def _build_no_tools_response(
        self, 
        intent: str, 
        user_platforms: Optional[List[str]]
    ) -> str:
        """
        Build response when no tools found.
        
        Args:
            intent: Detected intent
            user_platforms: User's platforms
            
        Returns:
            Helpful message
        """
        lines = [
            "=== NO TOOLS FOUND ===",
            "",
            f"INTENT: {intent.upper()}",
            ""
        ]
        
        if user_platforms:
            lines.extend([
                f"AVAILABLE PLATFORMS: {', '.join(user_platforms)}",
                "",
                "POSSIBLE REASONS:",
                "1. Intent not supported by available platforms",
                "2. User needs to connect additional platforms",
                "3. Request requires custom implementation",
                ""
            ])
        else:
            lines.extend([
                "NO PLATFORMS CONNECTED",
                "",
                "NEXT STEPS:",
                "1. User needs to connect platforms (Google Workspace, Microsoft 365, etc.)",
                "2. Once connected, relevant tools will become available",
                ""
            ])
        
        return "\n".join(lines)

    def _get_intent_advice(self, intent: str) -> str:
        """
        Get specific advice for an intent.
        
        Args:
            intent: Intent category
            
        Returns:
            Advice text
        """
        advice_map = {
            'email': (
                "For email tasks: Verify recipient addresses, prepare clear subject/body, "
                "consider using search tools first to find relevant conversations."
            ),
            'search': (
                "For search tasks: Use specific keywords, apply filters (date, sender, etc.), "
                "limit results initially (10-20), read full content only when needed."
            ),
            'document': (
                "For document tasks: Check for existing documents first (avoid duplicates), "
                "choose appropriate folder location, consider sharing permissions."
            ),
            'calendar': (
                "For calendar tasks: Check availability first, include clear meeting details, "
                "set appropriate reminders, verify timezone if needed."
            ),
            'quote': (
                "For quote tasks: Get stock list first to show options, verify all measurements, "
                "check quantity tiers, include all specifications in parameters."
            ),
            'file': (
                "For file tasks: Organize in logical folders, use descriptive names, "
                "set appropriate permissions, verify upload success."
            ),
            'unknown': (
                "Intent unclear - try to understand user's goal better before proceeding. "
                "Ask clarifying questions if needed."
            )
        }
        
        return advice_map.get(intent, advice_map['unknown'])

    def get_tool_sequence(
        self, 
        workflow_type: str,
        user_platforms: Optional[List[str]] = None
    ) -> str:
        """
        Get recommended tool sequence for a workflow.
        
        Args:
            workflow_type: Type of workflow (email, document, calendar, etc.)
            user_platforms: User's available platforms
            
        Returns:
            Formatted tool sequence
            
        Example:
            sequence = instructor.get_tool_sequence(
                'email',
                user_platforms=['google_workspace']
            )
        """
        logger.debug(f"Getting tool sequence for: {workflow_type}")
        
        sequences = {
            'email': self._get_email_sequence(user_platforms),
            'document': self._get_document_sequence(user_platforms),
            'calendar': self._get_calendar_sequence(user_platforms),
            'quote': self._get_quote_sequence(),
            'search': self._get_search_sequence(user_platforms)
        }
        
        sequence = sequences.get(workflow_type.lower())
        
        if sequence:
            logger.info(f"Generated tool sequence for: {workflow_type}")
            return sequence
        else:
            logger.warning(f"No sequence available for: {workflow_type}")
            return f"No tool sequence available for workflow type: {workflow_type}"

    def _get_email_sequence(self, user_platforms: Optional[List[str]]) -> str:
        """Get email workflow sequence."""
        if user_platforms and 'google_workspace' in user_platforms:
            tool = 'send_gmail'
        elif user_platforms and 'microsoft' in user_platforms:
            tool = 'send_outlook_email'
        else:
            tool = 'send_gmail OR send_outlook_email'
        
        return f"""
EMAIL WORKFLOW SEQUENCE:

1. Optional: search_contacts (verify recipient)
2. Required: {tool} (send email)
3. Optional: get_gmail_message / get_outlook_message (verify sent)

RATIONALE:
- Verifying contacts prevents typos in email addresses
- Send tool is the main action
- Verification step confirms delivery
"""

    def _get_document_sequence(self, user_platforms: Optional[List[str]]) -> str:
        """Get document workflow sequence."""
        if user_platforms and 'google_workspace' in user_platforms:
            search_tool = 'search_drive'
            create_tool = 'create_google_doc'
            share_tool = 'share_drive_file'
        elif user_platforms and 'microsoft' in user_platforms:
            search_tool = 'list_onedrive_files'
            create_tool = 'create_word_document'
            share_tool = 'share_onedrive_file'
        else:
            search_tool = 'search_drive OR list_onedrive_files'
            create_tool = 'create_google_doc OR create_word_document'
            share_tool = 'share_drive_file OR share_onedrive_file'
        
        return f"""
DOCUMENT WORKFLOW SEQUENCE:

1. Optional: {search_tool} (check for duplicates)
2. Required: {create_tool} (create document)
3. Optional: {share_tool} (share with others)

RATIONALE:
- Checking for duplicates prevents clutter
- Create tool is the main action
- Sharing enables collaboration
"""

    def _get_calendar_sequence(self, user_platforms: Optional[List[str]]) -> str:
        """Get calendar workflow sequence."""
        if user_platforms and 'google_workspace' in user_platforms:
            list_tool = 'list_calendar_events'
            create_tool = 'create_calendar_event'
        elif user_platforms and 'microsoft' in user_platforms:
            list_tool = 'list_outlook_events'
            create_tool = 'create_outlook_event'
        else:
            list_tool = 'list_calendar_events OR list_outlook_events'
            create_tool = 'create_calendar_event OR create_outlook_event'
        
        return f"""
CALENDAR WORKFLOW SEQUENCE:

1. Optional: {list_tool} (check availability)
2. Required: {create_tool} (create event)

RATIONALE:
- Checking availability prevents double-booking
- Create event is the main action
- Invitations are sent automatically
"""

    def _get_quote_sequence(self) -> str:
        """Get quote workflow sequence."""
        return """
QUOTE WORKFLOW SEQUENCE:

1. Recommended: get_stock_list (show options)
2. Optional: get_calculator_requirements (check params)
3. Required: calculate_[product_type] (generate quote)
   - calculate_business_cards
   - calculate_flyers
   - calculate_perfect_bound_books
   - calculate_corflute_signs
   - calculate_booklets

RATIONALE:
- Stock list helps customer choose materials
- Requirements check ensures correct parameters
- Calculator produces accurate pricing
"""

    def _get_search_sequence(self, user_platforms: Optional[List[str]]) -> str:
        """Get search workflow sequence."""
        if user_platforms and 'google_workspace' in user_platforms:
            search_tool = 'search_gmail'
            read_tool = 'get_gmail_message'
        elif user_platforms and 'microsoft' in user_platforms:
            search_tool = 'search_outlook_messages'
            read_tool = 'get_outlook_message'
        else:
            search_tool = 'search_gmail OR search_outlook_messages'
            read_tool = 'get_gmail_message OR get_outlook_message'
        
        return f"""
SEARCH WORKFLOW SEQUENCE:

1. Required: {search_tool} (find messages)
2. Optional: {read_tool} (read specific messages)

RATIONALE:
- Search narrows down results
- Reading full messages only when needed
- Prevents information overload
"""


# Export
__all__ = ['SmartToolInstructor']

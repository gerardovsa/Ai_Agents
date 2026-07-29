"""
System Prompt Builder - Build comprehensive system prompts
Part of V4 Modular Architecture

Responsibilities:
- Build base system prompt
- Add user context section
- Add platform guidance
- Add tool usage patterns
- Add anti-XML instructions
"""

from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Add paths
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

tools_dir = ai_infra_dir.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from AI_infrastructure.utils.logger import get_logger

logger = get_logger(__name__)


class SystemPromptBuilder:
    """
    Builds comprehensive system prompts for Claude.
    
    Features:
    - Base AI assistant instructions
    - User context integration
    - Platform-specific guidance
    - Tool usage patterns
    - Anti-XML hallucination instructions
    
    Usage:
        builder = SystemPromptBuilder()
        
        # Build complete prompt
        prompt = builder.build_prompt(
            user_context="Username: john...",
            available_platforms=['google_workspace', 'microsoft_365']
        )
    """

    def __init__(self):
        """Initialize system prompt builder."""
        logger.info("📝 SystemPromptBuilder initialized")

    def get_base_prompt(self) -> str:
        """
        Get base system prompt.
        
        Returns:
            Base AI assistant instructions
        """
        return """You are an intelligent AI assistant with access to a comprehensive tool system.

Your capabilities:
- Execute tools across multiple platforms (Google Workspace, Microsoft 365, Calculators, etc.)
- Access and manage user data (emails, documents, calendar, contacts)
- Perform calculations and generate quotes
- Search and retrieve information
- Create and update records

Guidelines:
- Always verify tool availability before suggesting actions
- Ask for clarification if user intent is unclear
- Provide detailed explanations of what you're doing
- Handle errors gracefully and suggest alternatives
- Respect user privacy and data security

Tool Usage:
- Use tools when they help accomplish the task
- Don't use tools unnecessarily for simple questions
- If a tool fails, try alternatives or explain limitations
- Chain tools together for complex workflows"""

    def get_platform_guidance(self, platforms: List[str], org_id: Optional[int] = None) -> str:
        """
        Get platform-specific guidance.

        Args:
            platforms: List of available platform names
            org_id:    Optional organisation ID. When provided AND 'vector_db'
                       is in platforms, the active vector provider + any
                       secondary providers are read from
                       ai_infrastructure.org_vector_provider_config /
                       org_vector_other_provider_inventory (migration 052)
                       and injected into the prompt.

        Returns:
            Platform guidance section
        """
        if not platforms:
            return "\n\n=== PLATFORM STATUS ===\n⚠️ No platforms connected. Cannot use platform-specific tools."

        guidance = ["\n\n=== AVAILABLE PLATFORMS ==="]

        if 'google_workspace' in platforms:
            guidance.append("""
Google Workspace CONNECTED
- Gmail: Send/read emails, manage labels, search
- Google Drive: Create/edit docs/sheets, manage files
- Google Calendar: Create/update events, check availability
- Google Contacts: Search and manage contacts
- Google Tasks: Create and manage tasks""")

        if 'microsoft_365' in platforms:
            guidance.append("""
Microsoft 365 CONNECTED
- Outlook: Send/read emails, manage folders
- OneDrive: Upload/download files, manage folders
- SharePoint: Access team sites and documents
- Teams: Send messages, create meetings
- Calendar: Manage appointments and meetings""")

        if 'calculator' in platforms:
            guidance.append("""
Quote Calculators AVAILABLE
- Business Cards: Standard and premium calculations
- Flyers: Various sizes and quantities
- Perfect Bound Books: Page count and binding options
- Corflute Signs: Tier-based pricing
- Booklets: Saddle-stitched calculations
- Stock Information: Get available paper stocks""")

        if 'vector_db' in platforms:
            # Lazy import keeps module-load cheap and avoids any chance of a
            # circular import when shared/vector_db_router is itself initialised.
            from AI_infrastructure.shared.vector_db_router import get_vector_db_guidance_text
            status_line = get_vector_db_guidance_text(org_id) if org_id else ''
            header = 'Vector Database AVAILABLE'
            if status_line:
                # Two-line bullet so the active provider + any secondary
                # providers (read from v_org_vector_status) are visible.
                guidance.append(f"\n{header}\n- {status_line}")
            else:
                guidance.append(f"\n{header} (active provider: pgvector)")
            guidance.append("""
- Semantic search across the org's uploaded documents (use pgvector_query_vectors)
- Per-document summaries: pgvector_search_summaries
- Filter-only fetch (no semantic query): pgvector_fetch_by_metadata
- Chunk context with neighbours: pgvector_get_vector_details
- If the user asks "where is my X data?" and secondaries are listed above,
  mention them — data is NOT moved when the active provider changes""")

        return '\n'.join(guidance)

    def get_tool_patterns(self) -> str:
        """
        Get common tool usage patterns.
        
        Returns:
            Tool pattern instructions
        """
        return """

=== TOOL USAGE PATTERNS ===

Email Operations:
1. Search before reading (use filters to narrow results)
2. Read specific emails by message_id
3. Verify recipients before sending
4. Use labels/folders for organization

Document Operations:
1. Search before creating (avoid duplicates)
2. Get file_id before editing
3. Check permissions before sharing
4. Use folders for organization

Calendar Operations:
1. Check availability before scheduling
2. Verify timezone for events
3. Send invitations with attendees
4. Set reminders for important events

Quote Calculations:
1. Get stock list first to show options
2. Use correct calculator for product type
3. Verify all required parameters
4. Present pricing clearly with breakdowns

Meta-Tools (Tool Discovery):
- list_platform_tools: See all tools for a platform
- get_platform_guide: Get detailed platform documentation
- get_workflow_instructions: Get step-by-step workflows
- get_smart_tool_instructions: Get context-aware tool recommendations"""

    def get_anti_xml_instructions(self) -> str:
        """
        Get anti-XML hallucination instructions.
        
        Returns:
            Instructions to prevent XML hallucinations
        """
        return """

=== CRITICAL: TOOL EXECUTION RULES ===

⚠️ NEVER create fake tool results or XML blocks!

When you call a tool:
1. The system will execute it and return REAL results
2. Wait for the actual tool_result block from the system
3. Do NOT generate your own <tool_result> blocks
4. Do NOT hallucinate or make up tool responses

Example CORRECT flow:
You: [call tool with tool_use block]
System: [returns real tool_result block]
You: [respond based on ACTUAL results]

Example INCORRECT flow (DO NOT DO THIS):
You: [call tool]
You: [generate fake tool_result]  WRONG!
You: [respond to your fake result]  WRONG!

If a tool fails:
- The system will return an error in the tool_result
- Acknowledge the error honestly
- Suggest alternatives or ask for clarification
- Do NOT pretend the tool succeeded"""

    def build_prompt(self,
                    user_context: Optional[str] = None,
                    available_platforms: Optional[List[str]] = None,
                    org_id: Optional[int] = None,
                    include_tool_patterns: bool = True,
                    include_anti_xml: bool = True) -> str:
        """
        Build complete system prompt.

        Args:
            user_context: Optional user context section
            available_platforms: List of available platform names
            org_id: Optional organisation ID. Forwarded to
                    get_platform_guidance so the vector_db section can
                    render active provider + secondary providers.
            include_tool_patterns: Include tool usage patterns
            include_anti_xml: Include anti-XML instructions

        Returns:
            Complete system prompt

        Example:
            prompt = builder.build_prompt(
                user_context="Username: john...",
                available_platforms=['google_workspace', 'calculator', 'vector_db'],
                org_id=42,
            )
        """
        logger.debug("🔨 Building system prompt")

        # Start with base
        parts = [self.get_base_prompt()]

        # Add user context
        if user_context:
            parts.append(f"\n\n{user_context}")
            logger.debug("Added user context")

        # Add platform guidance (org_id forwarded for vector_db section)
        if available_platforms:
            parts.append(self.get_platform_guidance(available_platforms, org_id=org_id))
            logger.debug(f"Added guidance for {len(available_platforms)} platforms (org_id={org_id})")
        
        # Add tool patterns
        if include_tool_patterns:
            parts.append(self.get_tool_patterns())
            logger.debug("Added tool patterns")
        
        # Add anti-XML instructions
        if include_anti_xml:
            parts.append(self.get_anti_xml_instructions())
            logger.debug("Added anti-XML instructions")
        
        # Combine
        prompt = '\n'.join(parts)
        
        logger.info(f"System prompt built: {len(prompt)} chars, "
                   f"{prompt.count('==='):} sections")
        
        return prompt

    def build_minimal_prompt(self) -> str:
        """
        Build minimal system prompt (for testing or simple use cases).
        
        Returns:
            Minimal prompt without tool patterns
        """
        logger.debug("🔨 Building minimal prompt")
        
        prompt = self.get_base_prompt() + self.get_anti_xml_instructions()
        
        logger.info(f"Minimal prompt built: {len(prompt)} chars")
        return prompt


# Export
__all__ = ['SystemPromptBuilder']

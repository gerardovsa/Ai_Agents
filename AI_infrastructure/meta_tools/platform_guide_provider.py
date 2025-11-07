"""
Platform Guide Provider - Provide detailed platform documentation
Part of V4 Modular Architecture - Meta-Tools

Responsibilities:
- Provide comprehensive platform guides
- Include authentication requirements
- List common workflows
- Provide usage examples
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

logger = logging.getLogger(__name__)


class PlatformGuideProvider:
    """
    Provides detailed platform documentation and guides.
    
    This is a meta-tool that helps AI understand how to use platform tools.
    
    Usage:
        provider = PlatformGuideProvider()
        
        # Get Google Workspace guide
        guide = provider.get_platform_guide('google_workspace')
        print(guide)
    """

    def __init__(self):
        """Initialize platform guide provider."""
        logger.info("PlatformGuideProvider initialized")
        
        # Platform guides
        self.guides = {
            'google_workspace': self._get_google_guide(),
            'microsoft_365': self._get_microsoft_guide(),
            'calculator': self._get_calculator_guide()
        }

    def get_platform_guide(self, platform: str) -> str:
        """
        Get comprehensive guide for a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Formatted guide string
            
        Example:
            guide = provider.get_platform_guide('google_workspace')
            print(guide)
        """
        logger.debug(f"Getting guide for platform: {platform}")
        
        platform_lower = platform.lower()
        
        # Find matching guide
        for key in self.guides.keys():
            if platform_lower in key or key in platform_lower:
                logger.info(f"Found guide for {platform}")
                return self.guides[key]
        
        logger.warning(f"No guide found for {platform}")
        return f"No documentation available for platform: {platform}"

    def list_available_guides(self) -> list:
        """
        List all available platform guides.
        
        Returns:
            List of platform names with guides
        """
        logger.debug("Listing available guides")
        return list(self.guides.keys())

    def _get_google_guide(self) -> str:
        """Get Google Workspace platform guide."""
        return """
=== GOOGLE WORKSPACE PLATFORM GUIDE ===

AUTHENTICATION:
- Requires OAuth 2.0 authentication
- User must connect Google account via Account Linking
- Scopes: Gmail, Drive, Calendar, Contacts, Tasks
- Credentials automatically injected by system

AVAILABLE SERVICES:

1. GMAIL
   - Send emails: send_gmail
   - Read emails: get_gmail_message, list_gmail_messages
   - Search: search_gmail
   - Labels: list_gmail_labels, add_gmail_label
   - Attachments: get_gmail_attachment

2. GOOGLE DRIVE
   - Files: create_drive_file, get_drive_file, list_drive_files
   - Folders: create_drive_folder
   - Search: search_drive
   - Sharing: share_drive_file
   - Export: export_drive_file

3. GOOGLE DOCS
   - Create: create_google_doc
   - Edit: update_google_doc
   - Read: get_google_doc_content

4. GOOGLE SHEETS
   - Create: create_google_sheet
   - Read: get_sheet_values
   - Write: update_sheet_values
   - Append: append_sheet_values

5. GOOGLE CALENDAR
   - Events: create_calendar_event, list_calendar_events
   - Search: search_calendar_events
   - Update: update_calendar_event
   - Delete: delete_calendar_event

6. GOOGLE CONTACTS
   - Search: search_contacts
   - Create: create_contact
   - Update: update_contact

7. GOOGLE TASKS
   - Create: create_task
   - List: list_tasks
   - Complete: complete_task

COMMON WORKFLOWS:
- Email Management: search_gmail → get_gmail_message → send_gmail
- Document Creation: create_google_doc → update_google_doc → share_drive_file
- Calendar Scheduling: list_calendar_events → create_calendar_event
- Contact Management: search_contacts → create_contact

BEST PRACTICES:
- Always search before creating to avoid duplicates
- Use specific queries to narrow results
- Check permissions before sharing
- Use batch operations when possible
"""

    def _get_microsoft_guide(self) -> str:
        """Get Microsoft 365 platform guide."""
        return """
=== MICROSOFT 365 PLATFORM GUIDE ===

AUTHENTICATION:
- Requires Microsoft OAuth authentication
- User must connect Microsoft account via Account Linking
- Scopes: Mail, Calendar, Files, Contacts
- Credentials automatically injected by system

AVAILABLE SERVICES:

1. OUTLOOK MAIL
   - Send: send_outlook_email
   - Read: get_outlook_message, list_outlook_messages
   - Search: search_outlook_messages
   - Folders: list_outlook_folders

2. ONEDRIVE
   - Files: upload_to_onedrive, download_from_onedrive
   - List: list_onedrive_files
   - Folders: create_onedrive_folder
   - Share: share_onedrive_file

3. OUTLOOK CALENDAR
   - Events: create_outlook_event, list_outlook_events
   - Update: update_outlook_event
   - Delete: delete_outlook_event

4. SHAREPOINT
   - Sites: list_sharepoint_sites
   - Documents: get_sharepoint_document
   - Lists: get_sharepoint_list

5. TEAMS (if available)
   - Messages: send_teams_message
   - Channels: list_teams_channels

COMMON WORKFLOWS:
- Email Management: search_outlook_messages → get_outlook_message → send_outlook_email
- File Management: list_onedrive_files → upload_to_onedrive → share_onedrive_file
- Calendar Management: list_outlook_events → create_outlook_event

BEST PRACTICES:
- Use folder filters to narrow search results
- Check file permissions before operations
- Respect rate limits (120 requests/minute)
- Use delta queries for efficient syncing
"""

    def _get_calculator_guide(self) -> str:
        """Get Calculator tools guide."""
        return """
=== QUOTE CALCULATOR PLATFORM GUIDE ===

AUTHENTICATION:
- No authentication required
- Available to all users
- Uses InHouse Print database for accurate pricing

AVAILABLE CALCULATORS:

1. BUSINESS CARDS
   - calculate_business_cards
   - Parameters: quantity, stock_type, corners, lamination
   - Returns: Price with Shopify pricing match

2. FLYERS
   - calculate_flyers
   - Parameters: quantity, width, length, stock_id
   - Also handles business cards (90x55mm size)
   - Returns: Per-unit and total pricing

3. PERFECT BOUND BOOKS
   - calculate_perfect_bound_books
   - Parameters: quantity, page_count, cover_stock, content_stock
   - Returns: Binding cost + paper cost breakdown

4. CORFLUTE SIGNS
   - calculate_corflute_signs
   - Parameters: width, height, quantity, thickness
   - Tier-based pricing (1-10, 11-50, 51+)
   - Returns: Price per sign with tier discounts

5. BOOKLETS
   - calculate_booklets
   - Parameters: quantity, page_count, size, stock_id
   - Saddle-stitched binding
   - Returns: Total price with binding

6. STOCK INFORMATION
   - get_stock_list
   - Returns: Available paper stocks with specs
   - Use before other calculators to show options

7. CALCULATOR REQUIREMENTS
   - get_calculator_requirements
   - Parameters: calculator_name
   - Returns: Required parameters for any calculator

TYPICAL WORKFLOW:
1. get_stock_list → Show customer options
2. calculate_[product] → Generate quote
3. Present pricing clearly with breakdowns

BEST PRACTICES:
- Always get stock list first to show options
- Verify all required parameters
- Present pricing with per-unit and total costs
- Include turnaround time in quotes
- Mention GST inclusion/exclusion clearly
"""


# Export
__all__ = ['PlatformGuideProvider']

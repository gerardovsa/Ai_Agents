"""
Workflow Instructor - Provide step-by-step workflow instructions
Part of V4 Modular Architecture - Meta-Tools

Responsibilities:
- Provide step-by-step workflows for common tasks
- Include tool sequences
- Add parameter examples
- Provide success criteria
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


class WorkflowInstructor:
    """
    Provides step-by-step workflow instructions for common tasks.
    
    This is a meta-tool that helps AI execute multi-step workflows correctly.
    
    Usage:
        instructor = WorkflowInstructor()
        
        # Get email workflow
        workflow = instructor.get_workflow('send_email')
        print(workflow)
    """

    def __init__(self):
        """Initialize workflow instructor."""
        logger.info("WorkflowInstructor initialized")
        
        # Common workflows
        self.workflows = {
            'send_email': self._get_send_email_workflow(),
            'search_email': self._get_search_email_workflow(),
            'create_document': self._get_create_document_workflow(),
            'schedule_meeting': self._get_schedule_meeting_workflow(),
            'generate_quote': self._get_generate_quote_workflow(),
            'file_management': self._get_file_management_workflow()
        }

    def get_workflow(self, workflow_name: str) -> str:
        """
        Get workflow instructions by name.
        
        Args:
            workflow_name: Workflow identifier
            
        Returns:
            Formatted workflow instructions
            
        Example:
            workflow = instructor.get_workflow('send_email')
            print(workflow)
        """
        logger.debug(f"Getting workflow: {workflow_name}")
        
        workflow_lower = workflow_name.lower()
        
        # Find matching workflow
        for key in self.workflows.keys():
            if workflow_lower in key or key in workflow_lower:
                logger.info(f"Found workflow: {workflow_name}")
                return self.workflows[key]
        
        logger.warning(f"No workflow found: {workflow_name}")
        return f"No workflow available for: {workflow_name}"

    def list_available_workflows(self) -> List[str]:
        """
        List all available workflows.
        
        Returns:
            List of workflow names
        """
        logger.debug("Listing available workflows")
        return list(self.workflows.keys())

    def _get_send_email_workflow(self) -> str:
        """Get send email workflow."""
        return """
=== WORKFLOW: SEND EMAIL ===

OBJECTIVE: Send an email to one or more recipients

PREREQUISITES:
- User must have Google Workspace or Microsoft 365 connected
- Valid recipient email addresses
- Email content prepared

STEPS:

1. VERIFY RECIPIENTS (Optional but recommended)
   Tool: search_contacts
   Parameters: {"query": "recipient name"}
   Purpose: Verify email addresses are correct
   Success: Found contact with matching email

2. SEND EMAIL
   Tool: send_gmail (Google) OR send_outlook_email (Microsoft)
   
   Parameters (Gmail):
   {
     "to": ["recipient@example.com"],
     "subject": "Email subject",
     "body": "Email body text",
     "cc": ["cc@example.com"],  // Optional
     "bcc": ["bcc@example.com"],  // Optional
     "attachments": [...]  // Optional
   }
   
   Parameters (Outlook):
   {
     "to": ["recipient@example.com"],
     "subject": "Email subject",
     "body": "Email body text",
     "cc": ["cc@example.com"],  // Optional
     "importance": "normal"  // Optional: low, normal, high
   }
   
   Success: Returns message_id

3. CONFIRM DELIVERY (Optional)
   - Email sent successfully
   - No errors returned
   - Message ID received

ERROR HANDLING:
- Invalid email format: Verify recipient addresses
- Authentication error: Check OAuth connection
- Rate limit: Wait and retry

VARIATIONS:
- With attachments: Include attachment_ids or file data
- HTML email: Use html_body parameter instead of body
- Multiple recipients: Include array of email addresses
"""

    def _get_search_email_workflow(self) -> str:
        """Get search email workflow."""
        return """
=== WORKFLOW: SEARCH EMAILS ===

OBJECTIVE: Find specific emails based on criteria

PREREQUISITES:
- User must have email platform connected
- Search criteria defined (sender, subject, date, etc.)

STEPS:

1. SEARCH WITH FILTERS
   Tool: search_gmail OR search_outlook_messages
   
   Parameters (Gmail):
   {
     "query": "from:sender@example.com subject:invoice",
     "max_results": 10,
     "include_spam_trash": false
   }
   
   Common Gmail queries:
   - "from:john@example.com" - Emails from John
   - "subject:invoice" - Emails with "invoice" in subject
   - "after:2025/01/01" - Emails after date
   - "has:attachment" - Emails with attachments
   - "is:unread" - Unread emails only
   
   Parameters (Outlook):
   {
     "filter": "from/emailAddress/address eq 'sender@example.com'",
     "top": 10,
     "select": ["subject", "from", "receivedDateTime"]
   }
   
   Success: Returns list of message IDs

2. READ SPECIFIC EMAILS (If needed)
   Tool: get_gmail_message OR get_outlook_message
   
   Parameters:
   {
     "message_id": "msg_abc123"
   }
   
   Success: Returns full email content

3. PROCESS RESULTS
   - Present relevant emails to user
   - Extract needed information
   - Perform follow-up actions if requested

BEST PRACTICES:
- Start with specific queries to narrow results
- Use date filters for recent emails
- Limit results (10-20) for initial search
- Read full messages only when necessary

ERROR HANDLING:
- No results: Broaden search criteria
- Too many results: Add more filters
- Authentication error: Check OAuth connection
"""

    def _get_create_document_workflow(self) -> str:
        """Get create document workflow."""
        return """
=== WORKFLOW: CREATE DOCUMENT ===

OBJECTIVE: Create a new document (Google Docs or OneDrive)

PREREQUISITES:
- User must have document platform connected
- Document content prepared
- Folder location decided (optional)

STEPS:

1. SEARCH FOR EXISTING (Avoid duplicates)
   Tool: search_drive OR list_onedrive_files
   
   Parameters:
   {
     "query": "name contains 'Document Title'",
     "max_results": 5
   }
   
   Success: No duplicate found, or found existing to update

2. CREATE NEW DOCUMENT
   Tool: create_google_doc OR create_word_document
   
   Parameters (Google Docs):
   {
     "title": "Document Title",
     "content": "Initial document content",
     "folder_id": "parent_folder_id"  // Optional
   }
   
   Parameters (Word):
   {
     "name": "Document Title.docx",
     "content": "Initial content",
     "folder_path": "/Documents"  // Optional
   }
   
   Success: Returns document_id or file_id

3. ADD CONTENT (If needed)
   Tool: update_google_doc OR update_word_document
   
   Parameters:
   {
     "document_id": "doc_abc123",
     "content": "Additional content to append",
     "mode": "append"  // or "replace"
   }

4. SHARE DOCUMENT (Optional)
   Tool: share_drive_file OR share_onedrive_file
   
   Parameters:
   {
     "file_id": "doc_abc123",
     "email": "recipient@example.com",
     "role": "writer",  // or "reader"
     "send_notification": true
   }

SUCCESS CRITERIA:
- Document created with correct title
- Content added successfully
- Shared with intended recipients (if applicable)
- Document URL returned for access

ERROR HANDLING:
- Permission denied: Check folder permissions
- Duplicate name: Append timestamp or version number
- Content too large: Split into multiple documents
"""

    def _get_schedule_meeting_workflow(self) -> str:
        """Get schedule meeting workflow."""
        return """
=== WORKFLOW: SCHEDULE MEETING ===

OBJECTIVE: Create a calendar event/meeting

PREREQUISITES:
- User must have calendar platform connected
- Meeting details prepared (time, attendees, topic)
- Attendee availability checked (optional)

STEPS:

1. CHECK AVAILABILITY (Optional)
   Tool: list_calendar_events OR list_outlook_events
   
   Parameters:
   {
     "start_time": "2025-10-30T14:00:00Z",
     "end_time": "2025-10-30T15:00:00Z",
     "calendar_id": "primary"
   }
   
   Purpose: Verify time slot is free

2. CREATE MEETING
   Tool: create_calendar_event OR create_outlook_event
   
   Parameters:
   {
     "summary": "Meeting Title",
     "start_time": "2025-10-30T14:00:00Z",
     "end_time": "2025-10-30T15:00:00Z",
     "attendees": ["attendee1@example.com", "attendee2@example.com"],
     "description": "Meeting agenda and details",
     "location": "Conference Room A",
     "reminders": [15, 60]  // Minutes before
   }
   
   Success: Returns event_id and meeting link

3. SEND INVITATIONS
   - Automatically handled by calendar tool
   - Attendees receive email invitation
   - Can accept/decline/tentative

4. CONFIRM CREATION
   - Event added to calendar
   - Invitations sent
   - Meeting link generated (for online meetings)

BEST PRACTICES:
- Include clear meeting title and agenda
- Set appropriate reminders (15 min, 1 hour)
- Add location or video link
- Check timezone considerations
- Send follow-up email with additional details if needed

ERROR HANDLING:
- Time conflict: Choose different time
- Invalid attendee: Verify email addresses
- Timezone issues: Use UTC or specify timezone explicitly
"""

    def _get_generate_quote_workflow(self) -> str:
        """Get generate quote workflow."""
        return """
=== WORKFLOW: GENERATE QUOTE ===

OBJECTIVE: Calculate pricing for print products

PREREQUISITES:
- Product type identified (business cards, flyers, books, etc.)
- Quantity determined
- Stock/material preferences known

STEPS:

1. GET AVAILABLE STOCKS (Recommended)
   Tool: get_stock_list
   
   Parameters: {}
   
   Returns: List of available paper stocks with:
   - Stock ID
   - Name (e.g., "Satin 350gsm")
   - Dimensions
   - GSM (paper weight)
   - Cost per thousand
   
   Purpose: Show customer their options

2. CHECK CALCULATOR REQUIREMENTS (If unsure)
   Tool: get_calculator_requirements
   
   Parameters:
   {
     "calculator_name": "calculate_business_cards"
   }
   
   Returns: Required and optional parameters

3. CALCULATE QUOTE
   Choose appropriate calculator:
   
   A) BUSINESS CARDS:
      Tool: calculate_business_cards
      Parameters: {
        "quantity": 1000,
        "stock_type": "standard",  // or "premium"
        "corners": "square",  // or "rounded"
        "lamination": false
      }
   
   B) FLYERS:
      Tool: calculate_flyers
      Parameters: {
        "quantity": 500,
        "width": 210,  // mm
        "length": 297,  // mm (A4)
        "stock_id": 16  // From get_stock_list
      }
   
   C) PERFECT BOUND BOOKS:
      Tool: calculate_perfect_bound_books
      Parameters: {
        "quantity": 100,
        "page_count": 200,
        "cover_stock_id": 16,
        "content_stock_id": 94
      }
   
   D) CORFLUTE SIGNS:
      Tool: calculate_corflute_signs
      Parameters: {
        "width": 600,
        "height": 900,
        "quantity": 10,
        "thickness": 5  // 3mm or 5mm
      }
   
   Success: Returns detailed pricing breakdown

4. PRESENT QUOTE
   Include:
   - Product description
   - Quantity
   - Per-unit price
   - Total price
   - Stock details
   - Turnaround time
   - GST information

BEST PRACTICES:
- Always show stock options first
- Verify all measurements (mm for most products)
- Present pricing clearly with breakdowns
- Mention tier discounts if applicable
- Include turnaround time
- Clarify GST inclusion/exclusion

ERROR HANDLING:
- Invalid quantity: Check minimum order quantities
- Stock not found: Use get_stock_list to find valid options
- Calculation error: Verify all parameters are correct
"""

    def _get_file_management_workflow(self) -> str:
        """Get file management workflow."""
        return """
=== WORKFLOW: FILE MANAGEMENT ===

OBJECTIVE: Upload, organize, and share files

PREREQUISITES:
- User must have Drive or OneDrive connected
- File(s) to upload available
- Destination folder decided

STEPS:

1. LIST EXISTING FILES (Optional)
   Tool: list_drive_files OR list_onedrive_files
   
   Parameters:
   {
     "folder_id": "parent_folder_id",  // Optional
     "query": "name contains 'filename'",
     "max_results": 20
   }
   
   Purpose: Avoid duplicates, find existing files

2. CREATE FOLDER (If needed)
   Tool: create_drive_folder OR create_onedrive_folder
   
   Parameters:
   {
     "name": "Project Files",
     "parent_folder_id": "root"  // Optional
   }
   
   Returns: folder_id

3. UPLOAD FILE
   Tool: upload_to_drive OR upload_to_onedrive
   
   Parameters:
   {
     "file_name": "document.pdf",
     "file_data": "base64_encoded_content",
     "folder_id": "folder_abc123",  // Optional
     "mime_type": "application/pdf"
   }
   
   Success: Returns file_id

4. SHARE FILE (If needed)
   Tool: share_drive_file OR share_onedrive_file
   
   Parameters:
   {
     "file_id": "file_abc123",
     "email": "recipient@example.com",
     "role": "reader",  // or "writer"
     "notify": true
   }
   
   Returns: Share link

5. ORGANIZE FILES
   - Move to folders
   - Apply consistent naming
   - Set permissions appropriately

BEST PRACTICES:
- Use descriptive file names
- Organize in logical folder structure
- Set appropriate permissions (reader vs writer)
- Use share links for external sharing
- Clean up duplicate files

ERROR HANDLING:
- File too large: Check size limits (Google: 5TB, OneDrive: 250GB)
- Permission denied: Verify folder permissions
- Duplicate name: Append version number or date
- Upload failed: Check network connection, retry
"""


# Export
__all__ = ['WorkflowInstructor']

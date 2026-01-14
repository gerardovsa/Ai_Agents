"""
Google Workspace Integration Module
====================================

Centralized location for all Google Workspace API integrations.

This package provides tools for interacting with:
- Google Docs (document creation, formatting, tables)
- Google Sheets (spreadsheets, data, charts)
- Google Slides (presentations, pitch decks, training materials)
- Google Meet (video meetings, scheduling, recurring meetings)
- Google Drive (file management, folders, permissions)
- Google Forms (form creation, questions, responses)
- Google Calendar (event management, scheduling)
- Google Analytics (data tracking, reporting)
- Google Cloud Run (serverless deployments)
- Gmail (email management, sending, filtering)

All functions use service account authentication via google_auth_helper.
"""

# Import authentication helper first (required by all other modules)
from .google_auth_helper import (
    get_service_account_credentials,
    build_docs_service,
    build_drive_service,
    build_forms_service,
    build_calendar_service,
    build_analytics_service,
    build_gmail_service
)

# Import all Google Docs/Sheets/Charts functions
from .google_docs import (
    # Document operations
    google_docs_create_document,
    google_docs_smart_create_from_markdown,
    google_docs_smart_update,
    google_docs_get_document,
    google_docs_batch_update,
    google_docs_append_text,
    google_docs_replace_text,
    google_docs_delete_content,
    
    # Formatting operations
    google_docs_create_heading,
    google_docs_create_list,
    google_docs_insert_text,
    google_docs_insert_image,
    google_docs_insert_table,
    google_docs_insert_page_break,
    google_docs_format_text,
    google_docs_add_formatted_content,
    
    # Export operations
    google_docs_export_as_pdf,
    google_docs_add_page_numbers,
    google_docs_export_as_html,
    google_docs_export_as_markdown,
    google_docs_create_from_template,
    google_docs_get_suggestions,
    google_docs_create_named_range,
    
    # Sheets operations - imported from google_sheets module below
    # google_sheets_read_data,
    # google_sheets_create,
    # google_sheets_append_data,
    
    # Charts operations
    google_charts_create,
    google_docs_insert_chart,
    google_docs_create_professional_report_with_charts
)

# Import all Google Slides functions
from .google_slides import (
    # Core presentation operations
    google_slides_create_presentation,
    google_slides_get_presentation,
    
    # Slide operations
    google_slides_add_slide,
    google_slides_delete_slide,
    google_slides_duplicate_slide,
    
    # Content operations
    google_slides_insert_text,
    google_slides_insert_image,
    google_slides_insert_shape,
    google_slides_insert_table,
    google_slides_insert_chart_from_sheets,
    
    # Export operations
    google_slides_export_as_pdf,
    google_slides_export_as_pptx,
    
    # SMART BULK ACTIONS
    google_slides_create_pitch_deck,
    google_slides_create_training_presentation,
    google_slides_create_business_report
)

# Import all Google Meet functions
from .google_meet import (
    # Meeting creation
    google_meet_create_meeting,
    google_meet_create_instant_meeting,
    google_meet_schedule_recurring_meeting,
    
    # Meeting management
    google_meet_get_meeting_details,
    google_meet_update_meeting,
    google_meet_cancel_meeting,
    
    # Meeting listing
    google_meet_list_upcoming_meetings,
    
    # Spaces (persistent rooms)
    google_meet_create_space,
    google_meet_get_space,
    
    # SMART BULK ACTIONS
    google_meet_create_daily_standup,
    google_meet_schedule_interview_series,
    google_meet_create_team_meeting_with_agenda,
    google_meet_create_weekly_review,
    
    # Helper functions
    google_meet_get_join_info
)

# Import all Google Drive functions
from .google_drive import (
    google_drive_list_files,
    google_drive_get_file,
    google_drive_upload_file,
    google_drive_update_file,
    google_drive_delete_file,
    google_drive_create_folder,
    google_drive_move_file,
    google_drive_copy_file,
    google_drive_share_file,
    google_drive_list_permissions,
    google_drive_remove_permission,
    google_drive_search_files,
    google_drive_export_file,
    google_drive_get_storage_quota,
    google_drive_restore_file
)

# Import all Google Forms functions
from .google_forms import (
    google_forms_create_form,
    google_forms_get_form,
    google_forms_add_question,
    google_forms_get_responses
)

# Import all Google Calendar functions
from .google_calendar import (
    google_calendar_list_events,
    google_calendar_create_event,
    google_calendar_update_event,
    google_calendar_delete_event,
    google_calendar_list_calendars
)

# Import all Google Analytics functions
from .google_analytics import (
    google_analytics_list_accounts,
    google_analytics_list_properties,
    google_analytics_get_realtime_report,
    google_analytics_run_report,
    google_analytics_get_page_views,
    google_analytics_get_user_behavior,
    google_analytics_get_conversions,
    google_analytics_get_traffic_sources,
    google_analytics_get_demographics,
    google_analytics_get_device_data,
    google_analytics_get_top_pages,
    google_analytics_get_events
)

# Import Google Cloud Run functions
from .google_cloud_run import (
    google_cloud_run_list_services,
    google_cloud_run_deploy_service,
    google_cloud_run_delete_service,
    google_cloud_run_get_service
)

# Import Gmail functions
from .gmail import (
    gmail_send_email,
    gmail_create_draft,
    gmail_send_draft,
    gmail_list_messages,
    gmail_get_message,
    gmail_get_attachment,
    gmail_delete_message,
    gmail_modify_message,
    gmail_mark_as_read,
    gmail_mark_as_unread,
    gmail_archive_message,
    gmail_unarchive_message,
    gmail_list_labels,
    gmail_create_label,
    gmail_update_label,
    gmail_delete_label,
    gmail_create_filter,
    gmail_list_filters,
    gmail_delete_filter,
    gmail_get_profile,
    gmail_search_messages,
    # SMTP email sending functions
    gmail_send_email_smtp,
    gmail_send_email_smtp_html,
    gmail_list_available_accounts
)

# Import Google Sheets functions (from google_sheets.py - using Sheets API v4)
from .google_sheets import (
    google_sheets_create as gsheets_create,
    google_sheets_read_data as gsheets_read,
    google_sheets_append_data as gsheets_append,
    google_sheets_create as google_sheets_create,
    google_sheets_read_data as google_sheets_read_data,
    google_sheets_append_data as google_sheets_append_data,
    google_sheets_create_multiple,
    google_sheets_format_cells,
    google_sheets_delete
)

# Import Google Tasks functions
from .google_tasks import (
    build_tasks_service,
    google_tasks_list_task_lists,
    google_tasks_create_task_list,
    google_tasks_get_task_list,
    google_tasks_delete_task_list,
    google_tasks_list_tasks,
    google_tasks_create_task,
    google_tasks_update_task,
    google_tasks_complete_task,
    google_tasks_delete_task,
    # SMART bundled tools
    google_tasks_smart_create_project,
    google_tasks_smart_bulk_complete,
    google_tasks_smart_organize_by_priority
)

# Import AI Personal Task Management
from .ai_personal_tasks import (
    ai_create_task,
    ai_list_my_tasks,
    ai_update_task,
    ai_complete_task,
    ai_organize_tasks,
    ai_create_project_tasks,
    ai_check_pending_work
)

# Define __all__ for explicit exports
__all__ = [
    # Auth
    'get_service_account_credentials',
    'build_docs_service',
    'build_drive_service',
    'build_forms_service',
    'build_calendar_service',
    'build_analytics_service',
    'build_gmail_service',
    
    # Docs - Document operations
    'google_docs_create_document',
    'google_docs_smart_create_from_markdown',
    'google_docs_smart_update',
    'google_docs_get_document',
    'google_docs_batch_update',
    'google_docs_append_text',
    'google_docs_replace_text',
    'google_docs_delete_content',
    
    # Docs - Formatting operations
    'google_docs_create_heading',
    'google_docs_create_list',
    'google_docs_insert_text',
    'google_docs_insert_image',
    'google_docs_insert_table',
    'google_docs_insert_page_break',
    'google_docs_format_text',
    'google_docs_add_formatted_content',
    
    # Docs - Export operations
    'google_docs_export_as_pdf',
    'google_docs_add_page_numbers',
    'google_docs_export_as_html',
    'google_docs_export_as_markdown',
    'google_docs_create_from_template',
    'google_docs_get_suggestions',
    'google_docs_create_named_range',
    
    # Sheets
    'google_sheets_read_data',
    'google_sheets_create',
    'google_sheets_append_data',
    
    # Charts
    'google_charts_create',
    'google_docs_insert_chart',
    'google_docs_create_professional_report_with_charts',
    
    # Slides
    'google_slides_create_presentation',
    'google_slides_get_presentation',
    'google_slides_add_slide',
    'google_slides_delete_slide',
    'google_slides_duplicate_slide',
    'google_slides_insert_text',
    'google_slides_insert_image',
    'google_slides_insert_shape',
    'google_slides_insert_table',
    'google_slides_insert_chart_from_sheets',
    'google_slides_export_as_pdf',
    'google_slides_export_as_pptx',
    'google_slides_create_pitch_deck',
    'google_slides_create_training_presentation',
    'google_slides_create_business_report',
    
    # Meet
    'google_meet_create_meeting',
    'google_meet_create_instant_meeting',
    'google_meet_schedule_recurring_meeting',
    'google_meet_get_meeting_details',
    'google_meet_update_meeting',
    'google_meet_cancel_meeting',
    'google_meet_list_upcoming_meetings',
    'google_meet_create_space',
    'google_meet_get_space',
    'google_meet_create_daily_standup',
    'google_meet_schedule_interview_series',
    'google_meet_create_team_meeting_with_agenda',
    'google_meet_create_weekly_review',
    'google_meet_get_join_info',
    
    # Drive
    'google_drive_list_files',
    'google_drive_get_file',
    'google_drive_upload_file',
    'google_drive_update_file',
    'google_drive_delete_file',
    'google_drive_create_folder',
    'google_drive_move_file',
    'google_drive_copy_file',
    'google_drive_share_file',
    'google_drive_list_permissions',
    'google_drive_remove_permission',
    'google_drive_search_files',
    'google_drive_export_file',
    'google_drive_get_storage_quota',
    'google_drive_restore_file',
    
    # Forms
    'google_forms_create_form',
    'google_forms_get_form',
    'google_forms_add_question',
    'google_forms_get_responses',
    
    # Calendar
    'google_calendar_list_events',
    'google_calendar_create_event',
    'google_calendar_update_event',
    'google_calendar_delete_event',
    'google_calendar_list_calendars',
    
    # Analytics
    'google_analytics_list_accounts',
    'google_analytics_list_properties',
    'google_analytics_get_realtime_report',
    'google_analytics_run_report',
    'google_analytics_get_page_views',
    'google_analytics_get_user_behavior',
    'google_analytics_get_conversions',
    'google_analytics_get_traffic_sources',
    'google_analytics_get_demographics',
    'google_analytics_get_device_data',
    'google_analytics_get_top_pages',
    'google_analytics_get_events',
    
    # Cloud Run
    'google_cloud_run_list_services',
    'google_cloud_run_deploy_service',
    'google_cloud_run_delete_service',
    'google_cloud_run_get_service',
    
    # Gmail
    'gmail_send_email',
    'gmail_create_draft',
    'gmail_send_draft',
    'gmail_list_messages',
    'gmail_get_message',
    'gmail_get_attachment',
    'gmail_delete_message',
    'gmail_modify_message',
    'gmail_mark_as_read',
    'gmail_mark_as_unread',
    'gmail_archive_message',
    'gmail_unarchive_message',
    'gmail_list_labels',
    'gmail_create_label',
    'gmail_update_label',
    'gmail_delete_label',
    'gmail_create_filter',
    'gmail_list_filters',
    'gmail_delete_filter',
    'gmail_get_profile',
    'gmail_search_messages',
    'gmail_send_email_smtp',
    'gmail_send_email_smtp_html',
    'gmail_list_available_accounts',
    
    # GSheets
    'gsheets_read',
    'gsheets_write',
    'gsheets_append',
    'gsheets_create',
    
    # Google Tasks
    'build_tasks_service',
    'google_tasks_list_task_lists',
    'google_tasks_create_task_list',
    'google_tasks_get_task_list',
    'google_tasks_delete_task_list',
    'google_tasks_list_tasks',
    'google_tasks_create_task',
    'google_tasks_update_task',
    'google_tasks_complete_task',
    'google_tasks_delete_task',
    'google_tasks_smart_create_project',
    'google_tasks_smart_bulk_complete',
    'google_tasks_smart_organize_by_priority',
    
    # AI Personal Task Management
    'ai_create_task',
    'ai_list_my_tasks',
    'ai_update_task',
    'ai_complete_task',
    'ai_organize_tasks',
    'ai_create_project_tasks',
    'ai_check_pending_work'
]

__version__ = '1.0.0'
__author__ = 'Valor AI Team'

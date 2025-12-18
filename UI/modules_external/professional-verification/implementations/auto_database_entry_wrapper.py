"""
Auto Database Entry Wrapper - Registry V3 Integration
=====================================================

Registers automated database entry tools with the AI Agent platform.
Uses Computer Use API to fill forms and PostgreSQL for direct inserts.

TOOLS:
1. auto_enter_verification_results - Computer Use form automation
2. auto_enter_to_postgres - Direct PostgreSQL insertion
3. batch_enter_verifications - Bulk Computer Use automation

CREATED: December 18, 2025
"""

import logging
from tools.registry_v3 import tool_executor

logger = logging.getLogger(__name__)

# Import the async functions
from UI.modules_external.professional_verification.tools.implementations.auto_database_entry import (
    auto_enter_verification_results_sync,
    auto_enter_to_postgres_sync,
    batch_enter_verifications_sync
)


@tool_executor()
def auto_enter_verification_results(
    verification_data: dict,
    target_system: str,
    target_url: str,
    form_fields: dict
):
    """
    Automatically enter professional verification results into a web form using Computer Use.
    
    Claude will:
    1. Navigate to the target URL in a Docker browser
    2. Locate form fields by name/id/label
    3. Fill each field with corresponding data
    4. Submit the form
    5. Verify success and capture screenshots
    
    Perfect for automating:
    - CRM contact creation
    - Database record entry
    - Web form submissions
    - Any browser-based data entry
    
    Args:
        verification_data: Dict of data to enter (name, email, company, legitimacy_score, etc.)
        target_system: System type - 'crm', 'database', 'erp', or 'custom'
        target_url: URL of the form to fill
        form_fields: Mapping of form field names to data keys
                    Example: {'full_name': 'name', 'email_address': 'email'}
    
    Returns:
        {
            'success': bool,
            'records_created': int,
            'screenshot_before': str (base64),
            'screenshot_after': str (base64),
            'actions_taken': List[str],
            'execution_time': float,
            'ai_response': str,
            'error': str (if failed)
        }
    
    Example:
        result = auto_enter_verification_results(
            verification_data={
                'name': 'Gregory Dutton',
                'company': 'Institute of Sustainable Biodiversity',
                'email': 'gregory.dutton@isb.eco',
                'legitimacy_score': 42.3,
                'status': 'UNCERTAIN',
                'notes': 'Requires manual verification'
            },
            target_system='crm',
            target_url='https://your-crm.com/contacts/new',
            form_fields={
                'contact_name': 'name',
                'company_name': 'company',
                'email_address': 'email',
                'risk_rating': 'legitimacy_score',
                'verification_status': 'status',
                'additional_notes': 'notes'
            }
        )
    """
    return auto_enter_verification_results_sync(
        verification_data=verification_data,
        target_system=target_system,
        target_url=target_url,
        form_fields=form_fields
    )


@tool_executor()
def auto_enter_to_postgres(
    verification_data: dict,
    table_name: str,
    schema_name: str = 'public'
):
    """
    Directly insert verification results into PostgreSQL database.
    
    Fast and efficient - no Computer Use needed. Uses the platform's
    database connection to execute INSERT statements.
    
    Args:
        verification_data: Dict where keys are column names, values are data
        table_name: PostgreSQL table name
        schema_name: Schema name (default 'public')
    
    Returns:
        {
            'success': bool,
            'records_created': int,
            'insert_id': int,
            'table': str,
            'error': str (if failed)
        }
    
    Example:
        result = auto_enter_to_postgres(
            verification_data={
                'full_name': 'Gregory Dutton',
                'company_name': 'Institute of Sustainable Biodiversity',
                'email': 'gregory.dutton@isb.eco',
                'domain': 'isb.eco',
                'legitimacy_score': 42.3,
                'verification_status': 'UNCERTAIN',
                'domain_authority': 27,
                'web_archive_snapshots': 27,
                'requires_manual_review': True,
                'created_at': '2025-12-18T10:30:00Z'
            },
            table_name='verified_professionals',
            schema_name='verification'
        )
    """
    return auto_enter_to_postgres_sync(
        verification_data=verification_data,
        table_name=table_name,
        schema_name=schema_name
    )


@tool_executor()
def batch_enter_verifications(
    verification_list: list,
    target_system: str,
    target_url: str,
    form_fields: dict
):
    """
    Batch process multiple verification results using Computer Use automation.
    
    Iterates through each record, fills the form, submits, and verifies.
    Includes 2-second delays between entries to avoid rate limiting.
    
    Args:
        verification_list: List of verification data dicts
        target_system: System type - 'crm', 'database', 'erp', or 'custom'
        target_url: URL of the form to fill
        form_fields: Mapping of form field names to data keys
    
    Returns:
        {
            'success': bool,
            'total_records': int,
            'records_created': int,
            'records_failed': int,
            'results': List[Dict],
            'execution_time': float
        }
    
    Example:
        result = batch_enter_verifications(
            verification_list=[
                {
                    'name': 'Gregory Dutton',
                    'company': 'ISB',
                    'email': 'gregory.dutton@isb.eco',
                    'score': 42.3
                },
                {
                    'name': 'John Smith',
                    'company': 'ABC Corp',
                    'email': 'john@abc.com',
                    'score': 85.7
                }
            ],
            target_system='crm',
            target_url='https://your-crm.com/contacts/new',
            form_fields={
                'full_name': 'name',
                'company': 'company',
                'email': 'email',
                'legitimacy': 'score'
            }
        )
    """
    return batch_enter_verifications_sync(
        verification_list=verification_list,
        target_system=target_system,
        target_url=target_url,
        form_fields=form_fields
    )


logger.info("[AUTO_DB_ENTRY_WRAPPER] ✅ 3 automated database entry tools registered")

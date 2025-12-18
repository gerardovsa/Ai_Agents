"""
Automated Database Entry with Computer Use
==========================================

Uses Anthropic Computer Use API to automate:
1. Entering verified professional data into databases
2. Filling web forms with verification results
3. Updating CRM systems with legitimacy scores
4. Creating records in business systems

REQUIRES:
- Anthropic API key (for Computer Use)
- Docker container with browser
- Database/form URLs and credentials

USAGE:
    from auto_database_entry import auto_enter_verification_results
    
    result = await auto_enter_verification_results(
        verification_data={
            'name': 'Gregory Dutton',
            'company': 'Institute of Sustainable Biodiversity',
            'email': 'gregory.dutton@isb.eco',
            'domain': 'isb.eco',
            'legitimacy_score': 42.3,
            'status': 'UNCERTAIN'
        },
        target_system='crm',
        target_url='https://your-crm.com/add-contact',
        form_fields={
            'full_name': 'name',
            'company_name': 'company',
            'email_address': 'email',
            'risk_score': 'legitimacy_score',
            'verification_status': 'status'
        }
    )

CREATED: December 18, 2025
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

logger = logging.getLogger(__name__)


async def auto_enter_verification_results(
    verification_data: Dict[str, Any],
    target_system: str,
    target_url: str,
    form_fields: Dict[str, str],
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Automatically enter verification results into a database or web form using Computer Use.
    
    Args:
        verification_data: Dictionary of verified data to enter
        target_system: System type ('crm', 'database', 'erp', 'custom')
        target_url: URL of form/system to fill
        form_fields: Mapping of form field names to data keys
        _user_id: User ID (injected)
        _injected_credentials: API credentials (injected)
    
    Returns:
        {
            'success': bool,
            'records_created': int,
            'screenshot_before': str (base64),
            'screenshot_after': str (base64),
            'actions_taken': List[str],
            'execution_time': float,
            'error': str (if failed)
        }
    """
    logger.info(f"[AUTO_DB_ENTRY] Starting automated entry to {target_system} at {target_url}")
    
    start_time = datetime.now()
    actions_taken = []
    
    try:
        # Import Computer Use executor
        try:
            from AI_infrastructure.core.computer_use_executor import get_computer_use_executor
            executor = get_computer_use_executor()
        except ImportError as e:
            logger.error(f"[AUTO_DB_ENTRY] Computer Use not available: {e}")
            return {
                'success': False,
                'error': 'Computer Use executor not available. Install Docker and check AI_infrastructure.',
                'records_created': 0
            }
        
        # Get Anthropic API key
        anthropic_key = None
        if _injected_credentials:
            anthropic_key = _injected_credentials.get('anthropic_api_key')
        if not anthropic_key:
            anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        
        if not anthropic_key:
            return {
                'success': False,
                'error': 'Anthropic API key required for Computer Use',
                'records_created': 0
            }
        
        # Import Anthropic
        from anthropic import Anthropic
        client = Anthropic(api_key=anthropic_key)
        
        # Get browser container
        container_id = await executor.get_browser_container(reuse=True)
        if not container_id:
            return {
                'success': False,
                'error': 'Failed to start browser container',
                'records_created': 0
            }
        
        actions_taken.append(f"Started browser container: {container_id}")
        
        # Build the task instruction for Claude
        task_instruction = f"""
You are automating data entry into a {target_system} system.

TASK: Navigate to {target_url} and fill the form with the following data:

DATA TO ENTER:
{json.dumps(verification_data, indent=2)}

FORM FIELD MAPPINGS:
{json.dumps(form_fields, indent=2)}

STEPS:
1. Navigate to the URL
2. Wait for page to load completely
3. Locate each form field by name, id, or label
4. Fill each field with the corresponding data
5. Submit the form
6. Verify the record was created successfully
7. Take a screenshot of the confirmation

IMPORTANT:
- If login is required, report back that credentials are needed
- Verify each field was filled correctly before submitting
- Look for success confirmation messages
- Report any errors clearly
"""
        
        # Take initial screenshot
        screenshot_before = await executor.take_screenshot(container_id)
        actions_taken.append("Captured initial screenshot")
        
        # Execute Computer Use with Claude
        messages = [{
            "role": "user",
            "content": task_instruction
        }]
        
        max_iterations = 20
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call Claude with Computer Use tools
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=4096,
                tools=[{
                    "type": "computer_20241022",
                    "name": "computer",
                    "display_width_px": 1920,
                    "display_height_px": 1080
                }],
                messages=messages
            )
            
            actions_taken.append(f"Iteration {iteration}: {response.stop_reason}")
            
            # Check if Claude is done
            if response.stop_reason == "end_turn":
                # Task completed
                final_text = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        final_text += block.text
                
                # Take final screenshot
                screenshot_after = await executor.take_screenshot(container_id)
                actions_taken.append("Captured final screenshot")
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    'success': True,
                    'records_created': 1,
                    'screenshot_before': screenshot_before,
                    'screenshot_after': screenshot_after,
                    'actions_taken': actions_taken,
                    'execution_time': execution_time,
                    'ai_response': final_text
                }
            
            # Process tool use requests
            if response.stop_reason == "tool_use":
                tool_results = []
                
                for block in response.content:
                    if block.type == "tool_use" and block.name == "computer":
                        action = block.input.get('action')
                        
                        if action == "screenshot":
                            result = await executor.take_screenshot(container_id)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result
                            })
                        
                        elif action == "mouse_move":
                            coordinate = block.input.get('coordinate', [0, 0])
                            await executor.move_mouse(container_id, coordinate[0], coordinate[1])
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": "Mouse moved"
                            })
                        
                        elif action == "left_click":
                            await executor.click_mouse(container_id)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": "Clicked"
                            })
                        
                        elif action == "type":
                            text = block.input.get('text', '')
                            await executor.type_text(container_id, text)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Typed: {text}"
                            })
                        
                        elif action == "key":
                            key = block.input.get('text', '')
                            await executor.press_key(container_id, key)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Pressed key: {key}"
                            })
                        
                        elif action == "cursor_position":
                            # Return current cursor position (placeholder)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": "Cursor position recorded"
                            })
                        
                        actions_taken.append(f"Executed: {action}")
                
                # Add tool results to messages
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            
            else:
                # Unexpected stop reason
                break
        
        # If we hit max iterations
        screenshot_after = await executor.take_screenshot(container_id)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': False,
            'error': f'Max iterations ({max_iterations}) reached without completion',
            'records_created': 0,
            'screenshot_before': screenshot_before,
            'screenshot_after': screenshot_after,
            'actions_taken': actions_taken,
            'execution_time': execution_time
        }
    
    except Exception as e:
        logger.error(f"[AUTO_DB_ENTRY] Error: {e}", exc_info=True)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': False,
            'error': str(e),
            'records_created': 0,
            'actions_taken': actions_taken,
            'execution_time': execution_time
        }


async def auto_enter_to_postgres(
    verification_data: Dict[str, Any],
    table_name: str,
    schema_name: str = 'public',
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Directly insert verification results into PostgreSQL database.
    
    Args:
        verification_data: Dictionary of data to insert
        table_name: Target table name
        schema_name: Schema name (default 'public')
        _user_id: User ID (injected)
        _injected_credentials: Database credentials (injected)
    
    Returns:
        {
            'success': bool,
            'records_created': int,
            'insert_id': int,
            'error': str
        }
    """
    logger.info(f"[AUTO_POSTGRES] Inserting into {schema_name}.{table_name}")
    
    try:
        # Import database utilities
        from AI_infrastructure.shared.database_utils import execute_query
        
        # Build column names and values
        columns = list(verification_data.keys())
        values = list(verification_data.values())
        
        # Build INSERT query
        placeholders = ', '.join(['%s'] * len(columns))
        column_list = ', '.join(columns)
        
        query = f"""
        INSERT INTO {schema_name}.{table_name} ({column_list})
        VALUES ({placeholders})
        RETURNING id
        """
        
        # Execute query
        result = execute_query(query, tuple(values), fetch_mode='one')
        
        insert_id = result[0] if result else None
        
        logger.info(f"[AUTO_POSTGRES] ✅ Inserted record ID: {insert_id}")
        
        return {
            'success': True,
            'records_created': 1,
            'insert_id': insert_id,
            'table': f"{schema_name}.{table_name}"
        }
    
    except Exception as e:
        logger.error(f"[AUTO_POSTGRES] Error: {e}", exc_info=True)
        return {
            'success': False,
            'records_created': 0,
            'error': str(e)
        }


async def batch_enter_verifications(
    verification_list: List[Dict[str, Any]],
    target_system: str,
    target_url: str,
    form_fields: Dict[str, str],
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Batch process multiple verification results and enter them automatically.
    
    Args:
        verification_list: List of verification data dictionaries
        target_system: System type ('crm', 'database', 'erp', 'custom')
        target_url: URL of form/system to fill
        form_fields: Mapping of form field names to data keys
        _user_id: User ID (injected)
        _injected_credentials: API credentials (injected)
    
    Returns:
        {
            'success': bool,
            'total_records': int,
            'records_created': int,
            'records_failed': int,
            'results': List[Dict],
            'execution_time': float
        }
    """
    logger.info(f"[BATCH_ENTRY] Processing {len(verification_list)} records")
    
    start_time = datetime.now()
    results = []
    records_created = 0
    records_failed = 0
    
    for idx, verification_data in enumerate(verification_list):
        logger.info(f"[BATCH_ENTRY] Processing record {idx+1}/{len(verification_list)}")
        
        result = await auto_enter_verification_results(
            verification_data=verification_data,
            target_system=target_system,
            target_url=target_url,
            form_fields=form_fields,
            _user_id=_user_id,
            _injected_credentials=_injected_credentials
        )
        
        results.append(result)
        
        if result['success']:
            records_created += result.get('records_created', 0)
        else:
            records_failed += 1
        
        # Small delay between entries
        await asyncio.sleep(2)
    
    execution_time = (datetime.now() - start_time).total_seconds()
    
    return {
        'success': records_failed == 0,
        'total_records': len(verification_list),
        'records_created': records_created,
        'records_failed': records_failed,
        'results': results,
        'execution_time': execution_time
    }


# Synchronous wrapper for backwards compatibility
def auto_enter_verification_results_sync(*args, **kwargs):
    """Synchronous wrapper for async function"""
    return asyncio.run(auto_enter_verification_results(*args, **kwargs))

def auto_enter_to_postgres_sync(*args, **kwargs):
    """Synchronous wrapper for async function"""
    return asyncio.run(auto_enter_to_postgres(*args, **kwargs))

def batch_enter_verifications_sync(*args, **kwargs):
    """Synchronous wrapper for async function"""
    return asyncio.run(batch_enter_verifications(*args, **kwargs))

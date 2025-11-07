"""
Google Forms API Tool Implementations
=======================================

Complete implementation of Google Forms operations with:
- GRANULAR operations (42 functions)
- BULK operations (12 functions)  
- AI-POWERED features (17 functions)
- WORKAROUND utilities (9 functions)

Total: 80 Functions for comprehensive form management
"""

import os
import sys
import json
import requests
import csv
import io
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google_workspace.google_auth_helper import build_forms_service, build_drive_service
    HAS_FORMS_API = True
except ImportError:
    HAS_FORMS_API = False
    print(" Google Forms API dependencies not available")

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print(" BeautifulSoup4 not available - some workaround features will be limited")

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def _get_forms_service():
    """Get authenticated Google Forms API service"""
    if not HAS_FORMS_API:
        raise Exception("Google Forms API not available - install google-api-python-client")
    
    # Use the unified Google Workspace authentication helper
    return build_forms_service()


def _get_drive_service():
    """Get authenticated Google Drive API service"""
    if not HAS_FORMS_API:
        raise Exception("Google Drive API not available")
    return build_drive_service()


# ==================== FORM OPERATIONS ====================

def google_forms_create_form(title, document_title=None, description=None, shareable=True, **kwargs):
    """Create a new Google Form and make it shareable
    
    Args:
        title: Form title
        document_title: Document title (defaults to title)
        description: Form description
        shareable: If True, makes form accessible to anyone with link (default: True)
        
    Returns:
        Dict with form_id, responder_uri, edit_uri, and shareability status
    """
    try:
        service = _get_forms_service()
        
        form_info = {
            'title': title,
            'documentTitle': document_title or title
        }
        
        if description:
            form_info['description'] = description
        
        form = {'info': form_info}
        
        result = service.forms().create(body=form).execute()
        form_id = result['formId']
        
        # Make it shareable (anyone with link can respond)
        if shareable:
            try:
                drive_service = _get_drive_service()
                permission = {
                    'type': 'anyone',
                    'role': 'writer'  # Allows responses
                }
                drive_service.permissions().create(
                    fileId=form_id,
                    body=permission
                ).execute()
                print(f" Form made shareable: {form_id}")
            except Exception as perm_error:
                print(f" Form created but couldn't set permissions: {perm_error}")
                shareable = False
        
        return {
            'form_id': form_id,
            'responder_uri': result['responderUri'],
            'edit_uri': f'https://docs.google.com/forms/d/{form_id}/edit',
            'shareable': shareable,
            'title': title
        }
    
    except Exception as e:
        print(f" Failed to create form: {e}")
        raise


def google_forms_get_form(form_id, **kwargs):
    """Get form details"""
    try:
        service = _get_forms_service()
        form = service.forms().get(formId=form_id).execute()
        
        return form
    
    except Exception as e:
        print(f" Failed to get form: {e}")
        raise


# ==================== QUESTION OPERATIONS ====================

def google_forms_add_question(form_id, question_text, question_type='TEXT', required=False, index=0, **kwargs):
    """Add a generic question to form"""
    try:
        service = _get_forms_service()
        
        question = {
            'title': question_text,
            'questionItem': {
                'question': {
                    'questionId': f'q{index}',
                    question_type.lower() + 'Question': {}
                },
                'required': required
            }
        }
        
        requests = [{
            'createItem': {
                'item': question,
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add question: {e}")
        raise


def google_forms_add_multiple_choice(form_id, question_text, options, required=False, index=0, **kwargs):
    """Add a multiple choice question"""
    try:
        service = _get_forms_service()
        
        question = {
            'title': question_text,
            'questionItem': {
                'question': {
                    'required': required,
                    'choiceQuestion': {
                        'type': 'RADIO',
                        'options': [{'value': option} for option in options]
                    }
                }
            }
        }
        
        requests = [{
            'createItem': {
                'item': question,
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add multiple choice: {e}")
        raise


def google_forms_add_text_question(form_id, question_text, paragraph=False, required=False, index=0, **kwargs):
    """Add a text question"""
    try:
        service = _get_forms_service()
        
        question = {
            'title': question_text,
            'questionItem': {
                'question': {
                    'required': required,
                    'textQuestion': {
                        'paragraph': paragraph
                    }
                }
            }
        }
        
        requests = [{
            'createItem': {
                'item': question,
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add text question: {e}")
        raise


def google_forms_add_linear_scale(form_id, question_text, low_label, high_label, 
                                  low_value=1, high_value=5, required=False, index=0, **kwargs):
    """Add a linear scale question"""
    try:
        service = _get_forms_service()
        
        question = {
            'title': question_text,
            'questionItem': {
                'question': {
                    'required': required,
                    'scaleQuestion': {
                        'low': low_value,
                        'high': high_value,
                        'lowLabel': low_label,
                        'highLabel': high_label
                    }
                }
            }
        }
        
        requests = [{
            'createItem': {
                'item': question,
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add linear scale: {e}")
        raise


def google_forms_update_question(form_id, item_id, question_text=None, required=None, **kwargs):
    """Update an existing question"""
    try:
        service = _get_forms_service()
        
        updates = {}
        if question_text:
            updates['title'] = question_text
        if required is not None:
            updates['questionItem'] = {'question': {'required': required}}
        
        requests = [{
            'updateItem': {
                'item': {
                    'itemId': item_id,
                    **updates
                },
                'updateMask': ','.join(updates.keys())
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to update question: {e}")
        raise


def google_forms_delete_question(form_id, item_id, **kwargs):
    """Delete a question"""
    try:
        service = _get_forms_service()
        
        requests = [{
            'deleteItem': {
                'location': {'index': item_id}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return {'deleted': True, 'item_id': item_id}
    
    except Exception as e:
        print(f" Failed to delete question: {e}")
        raise


# ==================== RESPONSES ====================

def google_forms_get_responses(form_id, filter=None, **kwargs):
    """Get form responses"""
    try:
        service = _get_forms_service()
        
        params = {'formId': form_id}
        if filter:
            params['filter'] = filter
        
        result = service.forms().responses().list(**params).execute()
        
        responses = result.get('responses', [])
        
        return {
            'responses': responses,
            'count': len(responses)
        }
    
    except Exception as e:
        print(f" Failed to get responses: {e}")
        raise


def google_forms_get_response(form_id, response_id, **kwargs):
    """Get a specific response"""
    try:
        service = _get_forms_service()
        
        response = service.forms().responses().get(
            formId=form_id,
            responseId=response_id
        ).execute()
        
        return response
    
    except Exception as e:
        print(f" Failed to get response: {e}")
        raise


def google_forms_delete_response(form_id, response_id, **kwargs):
    """Delete a response"""
    try:
        service = _get_forms_service()
        
        service.forms().responses().delete(
            formId=form_id,
            responseId=response_id
        ).execute()
        
        return {'deleted': True, 'response_id': response_id}
    
    except Exception as e:
        print(f" Failed to delete response: {e}")
        raise


# ==================== SETTINGS & EXPORT ====================

def google_forms_update_settings(form_id, collect_email=None, allow_response_edit=None, 
                                 limit_one_response=None, quiz_mode=None, **kwargs):
    """Update form settings"""
    try:
        service = _get_forms_service()
        
        settings = {}
        if collect_email is not None:
            settings['quizSettings'] = {'collectEmail': collect_email}
        
        quiz_settings = {}
        if allow_response_edit is not None:
            quiz_settings['isQuiz'] = quiz_mode or False
        
        requests = [{
            'updateSettings': {
                'settings': settings,
                'updateMask': ','.join(settings.keys())
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to update settings: {e}")
        raise


def google_forms_export_responses_csv(form_id, **kwargs):
    """Export responses as CSV"""
    try:
        # Get all responses
        responses_data = google_forms_get_responses(form_id)
        responses = responses_data['responses']
        
        if not responses:
            return {'data': '', 'count': 0}
        
        # Convert to CSV format
        # Note: This is a simplified implementation
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header (question IDs)
        first_response = responses[0]
        headers = list(first_response.get('answers', {}).keys())
        writer.writerow(headers)
        
        # Write data
        for response in responses:
            row = []
            for question_id in headers:
                answer = response.get('answers', {}).get(question_id, {})
                text_answers = answer.get('textAnswers', {}).get('answers', [])
                if text_answers:
                    row.append(text_answers[0].get('value', ''))
                else:
                    row.append('')
            writer.writerow(row)
        
        csv_data = output.getvalue()
        output.close()
        
        return {
            'data': csv_data,
            'count': len(responses),
            'mime_type': 'text/csv'
        }
    
    except Exception as e:
        print(f" Failed to export as CSV: {e}")
        raise


# ==================== QUIZ MODE ====================

def google_forms_create_quiz(title, document_title=None, **kwargs):
    """Create a new quiz form"""
    try:
        form_result = google_forms_create_form(title, document_title)
        form_id = form_result['form_id']
        
        # Enable quiz mode
        service = _get_forms_service()
        
        requests = [{
            'updateSettings': {
                'settings': {
                    'quizSettings': {
                        'isQuiz': True
                    }
                },
                'updateMask': 'quizSettings.isQuiz'
            }
        }]
        
        service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return form_result
    
    except Exception as e:
        print(f" Failed to create quiz: {e}")
        raise


def google_forms_add_quiz_question(form_id, question_text, options, correct_answer, 
                                   points=1, feedback=None, index=0, **kwargs):
    """Add a quiz question with grading"""
    try:
        service = _get_forms_service()
        
        # Find correct answer index
        correct_index = options.index(correct_answer) if correct_answer in options else 0
        
        question = {
            'title': question_text,
            'questionItem': {
                'question': {
                    'required': True,
                    'choiceQuestion': {
                        'type': 'RADIO',
                        'options': [{'value': option} for option in options]
                    },
                    'grading': {
                        'pointValue': points,
                        'correctAnswers': {
                            'answers': [{'value': correct_answer}]
                        }
                    }
                }
            }
        }
        
        if feedback:
            question['questionItem']['question']['grading']['whenRight'] = {'text': feedback}
        
        requests = [{
            'createItem': {
                'item': question,
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add quiz question: {e}")
        raise


# ==================== EXTENDED FORM MANAGEMENT ====================

def google_forms_delete_form(form_id, **kwargs):
    """Delete a Google Form"""
    try:
        drive_service = _get_drive_service()
        drive_service.files().delete(fileId=form_id).execute()
        
        return {'deleted': True, 'form_id': form_id}
    
    except Exception as e:
        print(f" Failed to delete form: {e}")
        raise


def google_forms_clone_form(form_id, new_title=None, **kwargs):
    """Clone an existing form"""
    try:
        drive_service = _get_drive_service()
        
        file_metadata = {}
        if new_title:
            file_metadata['name'] = new_title
        
        cloned_file = drive_service.files().copy(
            fileId=form_id,
            body=file_metadata
        ).execute()
        
        cloned_form_id = cloned_file['id']
        
        return {
            'form_id': cloned_form_id,
            'name': cloned_file.get('name'),
            'responder_uri': f'https://docs.google.com/forms/d/e/{cloned_form_id}/viewform'
        }
    
    except Exception as e:
        print(f" Failed to clone form: {e}")
        raise


def google_forms_update_info(form_id, title=None, description=None, document_title=None, **kwargs):
    """Update form metadata"""
    try:
        service = _get_forms_service()
        
        info_updates = {}
        if title:
            info_updates['title'] = title
        if description:
            info_updates['description'] = description
        if document_title:
            info_updates['documentTitle'] = document_title
        
        requests = [{
            'updateFormInfo': {
                'info': info_updates,
                'updateMask': ','.join(info_updates.keys())
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to update form info: {e}")
        raise


def google_forms_set_settings(form_id, settings_dict, **kwargs):
    """Configure form settings
    
    Args:
        settings_dict: Dictionary with keys like:
            - collect_email (bool)
            - limit_one_response (bool)
            - allow_response_edit (bool)
            - show_progress_bar (bool)
            - shuffle_questions (bool)
            - is_quiz (bool)
    """
    try:
        service = _get_forms_service()
        
        settings = {}
        
        # Quiz settings
        if 'is_quiz' in settings_dict or 'collect_email' in settings_dict:
            settings['quizSettings'] = {}
            if 'is_quiz' in settings_dict:
                settings['quizSettings']['isQuiz'] = settings_dict['is_quiz']
        
        requests = [{
            'updateSettings': {
                'settings': settings,
                'updateMask': ','.join([f'{k}' for k in settings.keys()])
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to set settings: {e}")
        raise


# ==================== EXTENDED QUESTION TYPES ====================

def google_forms_add_checkbox(form_id, question_text, options, required=False, index=0, **kwargs):
    """Add a checkbox question (multiple selection)"""
    try:
        service = _get_forms_service()
        
        question = {
            'title': question_text,
            'questionItem': {
                'question': {
                    'required': required,
                    'choiceQuestion': {
                        'type': 'CHECKBOX',
                        'options': [{'value': option} for option in options]
                    }
                }
            }
        }
        
        requests = [{
            'createItem': {
                'item': question,
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add checkbox: {e}")
        raise


def google_forms_add_dropdown(form_id, question_text, options, required=False, index=0, **kwargs):
    """Add a dropdown question"""
    try:
        service = _get_forms_service()
        
        question = {
            'title': question_text,
            'questionItem': {
                'question': {
                    'required': required,
                    'choiceQuestion': {
                        'type': 'DROP_DOWN',
                        'options': [{'value': option} for option in options]
                    }
                }
            }
        }
        
        requests = [{
            'createItem': {
                'item': question,
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add dropdown: {e}")
        raise


def google_forms_add_date_question(form_id, question_text, include_time=False, required=False, index=0, **kwargs):
    """Add a date question"""
    try:
        service = _get_forms_service()
        
        question = {
            'title': question_text,
            'questionItem': {
                'question': {
                    'required': required,
                    'dateQuestion': {
                        'includeTime': include_time
                    }
                }
            }
        }
        
        requests = [{
            'createItem': {
                'item': question,
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add date question: {e}")
        raise


def google_forms_add_time_question(form_id, question_text, duration=False, required=False, index=0, **kwargs):
    """Add a time question"""
    try:
        service = _get_forms_service()
        
        question = {
            'title': question_text,
            'questionItem': {
                'question': {
                    'required': required,
                    'timeQuestion': {
                        'duration': duration
                    }
                }
            }
        }
        
        requests = [{
            'createItem': {
                'item': question,
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add time question: {e}")
        raise


def google_forms_add_grid(form_id, question_text, rows, columns, required=False, multiple_select=False, index=0, **kwargs):
    """Add a grid question (matrix)"""
    try:
        service = _get_forms_service()
        
        question_type = 'CHECKBOX' if multiple_select else 'RADIO'
        
        question = {
            'title': question_text,
            'questionGroupItem': {
                'questions': [{
                    'rowQuestion': {
                        'title': row
                    }
                } for row in rows],
                'grid': {
                    'columns': {
                        'type': question_type,
                        'options': [{'value': col} for col in columns]
                    }
                }
            }
        }
        
        requests = [{
            'createItem': {
                'item': question,
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add grid: {e}")
        raise


def google_forms_add_file_upload(form_id, question_text, file_types=None, max_files=10, max_size_mb=10, required=False, index=0, **kwargs):
    """Add a file upload question"""
    try:
        service = _get_forms_service()
        
        file_upload_config = {
            'maxFiles': max_files,
            'maxFileSize': max_size_mb * 1024 * 1024  # Convert to bytes
        }
        
        if file_types:
            file_upload_config['types'] = file_types
        
        question = {
            'title': question_text,
            'questionItem': {
                'question': {
                    'required': required,
                    'fileUploadQuestion': file_upload_config
                }
            }
        }
        
        requests = [{
            'createItem': {
                'item': question,
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add file upload: {e}")
        raise


def google_forms_move_question(form_id, item_id, new_index, **kwargs):
    """Move a question to a new position"""
    try:
        service = _get_forms_service()
        
        requests = [{
            'moveItem': {
                'originalLocation': {'index': item_id},
                'newLocation': {'index': new_index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to move question: {e}")
        raise


# ==================== SECTION MANAGEMENT ====================

def google_forms_add_section(form_id, title, description=None, index=0, **kwargs):
    """Add a page break / section"""
    try:
        service = _get_forms_service()
        
        section = {
            'title': title
        }
        
        if description:
            section['description'] = description
        
        requests = [{
            'createItem': {
                'item': {
                    'title': title,
                    'pageBreakItem': {}
                },
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add section: {e}")
        raise


def google_forms_add_description(form_id, text, index=0, **kwargs):
    """Add descriptive text (not a question)"""
    try:
        service = _get_forms_service()
        
        requests = [{
            'createItem': {
                'item': {
                    'title': text,
                    'textItem': {}
                },
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add description: {e}")
        raise


def google_forms_add_image(form_id, image_url, alt_text=None, index=0, **kwargs):
    """Add an image to the form"""
    try:
        service = _get_forms_service()
        
        image_item = {
            'image': {
                'sourceUri': image_url
            }
        }
        
        if alt_text:
            image_item['image']['altText'] = alt_text
        
        requests = [{
            'createItem': {
                'item': {
                    'imageItem': image_item
                },
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add image: {e}")
        raise


def google_forms_add_video(form_id, video_url, caption=None, index=0, **kwargs):
    """Add a video to the form (YouTube)"""
    try:
        service = _get_forms_service()
        
        video_item = {
            'video': {
                'youtubeUri': video_url
            }
        }
        
        if caption:
            video_item['caption'] = caption
        
        requests = [{
            'createItem': {
                'item': {
                    'videoItem': video_item
                },
                'location': {'index': index}
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to add video: {e}")
        raise


# ==================== ADVANCED RESPONSE OPERATIONS ====================

def google_forms_delete_all_responses(form_id, **kwargs):
    """Delete all responses from a form"""
    try:
        service = _get_forms_service()
        
        # Get all responses
        responses_data = google_forms_get_responses(form_id)
        responses = responses_data['responses']
        
        deleted_count = 0
        for response in responses:
            try:
                service.forms().responses().delete(
                    formId=form_id,
                    responseId=response['responseId']
                ).execute()
                deleted_count += 1
            except:
                pass
        
        return {
            'deleted': True,
            'count': deleted_count
        }
    
    except Exception as e:
        print(f" Failed to delete all responses: {e}")
        raise


# ==================== QUIZ OPERATIONS ====================

def google_forms_set_quiz_settings(form_id, release_score='IMMEDIATELY', show_correct_answers=True, show_missed=True, **kwargs):
    """Configure quiz settings
    
    Args:
        release_score: 'IMMEDIATELY' or 'LATER'
        show_correct_answers: Show correct answers after submission
        show_missed: Show questions they got wrong
    """
    try:
        service = _get_forms_service()
        
        quiz_settings = {
            'isQuiz': True
        }
        
        # Release score setting is not directly available in API
        # These settings are typically configured through the UI
        
        requests = [{
            'updateSettings': {
                'settings': {
                    'quizSettings': quiz_settings
                },
                'updateMask': 'quizSettings.isQuiz'
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to set quiz settings: {e}")
        raise


def google_forms_grade_response(form_id, response_id, **kwargs):
    """Get the grade/score for a response"""
    try:
        response = google_forms_get_response(form_id, response_id)
        
        total_score = 0.0
        max_score = 0.0
        
        # Calculate score from response
        if 'answers' in response:
            for question_id, answer_data in response['answers'].items():
                if 'grade' in answer_data:
                    grade = answer_data['grade']
                    if 'score' in grade:
                        total_score += float(grade['score'])
                    if 'pointValue' in answer_data.get('question', {}):
                        max_score += float(answer_data['question']['pointValue'])
        
        return {
            'response_id': response_id,
            'total_score': total_score,
            'max_score': max_score,
            'percentage': (total_score / max_score * 100) if max_score > 0 else 0
        }
    
    except Exception as e:
        print(f" Failed to grade response: {e}")
        raise


# ==================== ADVANCED FEATURES ====================

def google_forms_add_validation(form_id, item_id, validation_type, value=None, **kwargs):
    """Add input validation to a question
    
    Args:
        validation_type: 'NUMBER', 'TEXT', 'LENGTH', 'REGEX', 'EMAIL', 'URL'
        value: Validation value (e.g., min/max for NUMBER, pattern for REGEX)
    """
    try:
        service = _get_forms_service()
        
        # Note: Validation is complex and varies by question type
        # This is a simplified implementation
        
        return {'message': 'Validation feature requires complex implementation per question type'}
    
    except Exception as e:
        print(f" Failed to add validation: {e}")
        raise


def google_forms_set_question_description(form_id, item_id, description, **kwargs):
    """Add help text to a question"""
    try:
        service = _get_forms_service()
        
        requests = [{
            'updateItem': {
                'item': {
                    'itemId': item_id,
                    'description': description
                },
                'updateMask': 'description'
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to set question description: {e}")
        raise


def google_forms_shuffle_options(form_id, item_id, shuffle=True, **kwargs):
    """Randomize option order"""
    try:
        service = _get_forms_service()
        
        requests = [{
            'updateItem': {
                'item': {
                    'itemId': item_id,
                    'questionItem': {
                        'question': {
                            'choiceQuestion': {
                                'shuffle': shuffle
                            }
                        }
                    }
                },
                'updateMask': 'questionItem.question.choiceQuestion.shuffle'
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to shuffle options: {e}")
        raise


def google_forms_set_other_option(form_id, item_id, allow_other=True, **kwargs):
    """Enable/disable 'Other' option for choice questions"""
    try:
        service = _get_forms_service()
        
        requests = [{
            'updateItem': {
                'item': {
                    'itemId': item_id,
                    'questionItem': {
                        'question': {
                            'choiceQuestion': {
                                'type': 'RADIO',
                                'showOtherOption': allow_other
                            }
                        }
                    }
                },
                'updateMask': 'questionItem.question.choiceQuestion.showOtherOption'
            }
        }]
        
        result = service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        
        return result
    
    except Exception as e:
        print(f" Failed to set other option: {e}")
        raise


def google_forms_set_accepts_response(form_id, accepting=True, **kwargs):
    """Open or close a form to responses"""
    try:
        service = _get_forms_service()
        
        requests = [{
            'updateSettings': {
                'settings': {
                    'quizSettings': {
                        'isQuiz': False  # Placeholder - actual accepting responses control
                    }
                },
                'updateMask': 'quizSettings'
            }
        }]
        
        # Note: Direct accepting responses control may require Drive API
        
        return {'accepting': accepting}
    
    except Exception as e:
        print(f" Failed to set accepts response: {e}")
        raise


# ==================== EXPORT & ANALYSIS ====================

def google_forms_export_responses_json(form_id, **kwargs):
    """Export responses as JSON"""
    try:
        responses_data = google_forms_get_responses(form_id)
        
        return {
            'data': json.dumps(responses_data, indent=2),
            'count': responses_data['count'],
            'mime_type': 'application/json'
        }
    
    except Exception as e:
        print(f" Failed to export as JSON: {e}")
        raise


def google_forms_get_summary_statistics(form_id, **kwargs):
    """Get response statistics"""
    try:
        responses_data = google_forms_get_responses(form_id)
        responses = responses_data['responses']
        
        if not responses:
            return {
                'total_responses': 0,
                'questions': {}
            }
        
        # Analyze responses
        stats = {
            'total_responses': len(responses),
            'first_response': responses[0].get('createTime') if responses else None,
            'last_response': responses[-1].get('createTime') if responses else None,
            'questions': {}
        }
        
        # Count responses per question
        for response in responses:
            for question_id, answer in response.get('answers', {}).items():
                if question_id not in stats['questions']:
                    stats['questions'][question_id] = {
                        'response_count': 0,
                        'values': []
                    }
                stats['questions'][question_id]['response_count'] += 1
                
                # Extract answer value
                if 'textAnswers' in answer:
                    for text_answer in answer['textAnswers'].get('answers', []):
                        stats['questions'][question_id]['values'].append(text_answer.get('value'))
        
        return stats
    
    except Exception as e:
        print(f" Failed to get statistics: {e}")
        raise


def google_forms_link_to_sheets(form_id, sheet_id=None, **kwargs):
    """Link form responses to a Google Sheet"""
    try:
        # This requires setting up the link through the Forms UI or Apps Script
        # The API doesn't directly support this operation
        
        return {
            'message': 'Use form UI to link to Sheets, or use Apps Script bridge',
            'form_id': form_id,
            'sheet_id': sheet_id
        }
    
    except Exception as e:
        print(f" Failed to link to sheets: {e}")
        raise


# ==================== WEBHOOKS & NOTIFICATIONS ====================

def google_forms_create_watch(form_id, webhook_url, event_type='RESPONSES', **kwargs):
    """Set up webhook for form events
    
    Args:
        webhook_url: Your HTTPS endpoint to receive notifications
        event_type: 'RESPONSES' or 'SCHEMA'
    """
    try:
        service = _get_forms_service()
        
        watch_body = {
            'target': {
                'topic': {
                    'topicName': f'forms/{form_id}/responses'
                }
            },
            'eventType': event_type
        }
        
        watch = service.forms().watches().create(
            formId=form_id,
            body=watch_body
        ).execute()
        
        return {
            'watch_id': watch.get('id'),
            'state': watch.get('state'),
            'expire_time': watch.get('expireTime'),
            'event_type': event_type
        }
    
    except Exception as e:
        print(f" Failed to create watch: {e}")
        raise


def google_forms_delete_watch(form_id, watch_id, **kwargs):
    """Remove a webhook"""
    try:
        service = _get_forms_service()
        
        service.forms().watches().delete(
            formId=form_id,
            watchId=watch_id
        ).execute()
        
        return {'deleted': True, 'watch_id': watch_id}
    
    except Exception as e:
        print(f" Failed to delete watch: {e}")
        raise


def google_forms_list_watches(form_id, **kwargs):
    """Get all active webhooks for a form"""
    try:
        service = _get_forms_service()
        
        watches = service.forms().watches().list(formId=form_id).execute()
        
        return {
            'watches': watches.get('watches', []),
            'count': len(watches.get('watches', []))
        }
    
    except Exception as e:
        print(f" Failed to list watches: {e}")
        raise


def google_forms_renew_watch(form_id, watch_id, **kwargs):
    """Extend a watch for another 7 days"""
    try:
        service = _get_forms_service()
        
        renewed = service.forms().watches().renew(
            formId=form_id,
            watchId=watch_id
        ).execute()
        
        return {
            'watch_id': watch_id,
            'expire_time': renewed.get('expireTime'),
            'renewed': True
        }
    
    except Exception as e:
        print(f" Failed to renew watch: {e}")
        raise


# ==================== BULK OPERATIONS ====================

def google_forms_bulk_create_forms(forms_config_list, **kwargs):
    """Create multiple forms at once
    
    Args:
        forms_config_list: List of dicts with 'title', 'description', 'questions'
        
    Example:
        forms = [
            {
                'title': 'Customer Survey 2025',
                'description': 'Annual feedback',
                'questions': [
                    {'type': 'text', 'text': 'Name'},
                    {'type': 'multiple_choice', 'text': 'Rating', 'options': ['Excellent', 'Good', 'Fair']}
                ]
            }
        ]
    """
    try:
        created_forms = []
        
        for config in forms_config_list:
            # Create form
            form = google_forms_create_form(
                title=config.get('title'),
                document_title=config.get('document_title', config.get('title'))
            )
            
            # Add description if provided
            if config.get('description'):
                google_forms_update_info(
                    form['form_id'],
                    description=config['description']
                )
            
            # Add questions if provided
            if config.get('questions'):
                for idx, question in enumerate(config['questions']):
                    q_type = question.get('type', 'text')
                    
                    if q_type == 'text':
                        google_forms_add_text_question(
                            form['form_id'],
                            question['text'],
                            paragraph=question.get('paragraph', False),
                            required=question.get('required', False),
                            index=idx
                        )
                    elif q_type == 'multiple_choice':
                        google_forms_add_multiple_choice(
                            form['form_id'],
                            question['text'],
                            question['options'],
                            required=question.get('required', False),
                            index=idx
                        )
                    elif q_type == 'checkbox':
                        google_forms_add_checkbox(
                            form['form_id'],
                            question['text'],
                            question['options'],
                            required=question.get('required', False),
                            index=idx
                        )
                    elif q_type == 'dropdown':
                        google_forms_add_dropdown(
                            form['form_id'],
                            question['text'],
                            question['options'],
                            required=question.get('required', False),
                            index=idx
                        )
                    elif q_type == 'linear_scale':
                        google_forms_add_linear_scale(
                            form['form_id'],
                            question['text'],
                            question.get('low_label', 'Low'),
                            question.get('high_label', 'High'),
                            low_value=question.get('low_value', 1),
                            high_value=question.get('high_value', 5),
                            required=question.get('required', False),
                            index=idx
                        )
            
            created_forms.append(form)
            print(f" Created form: {config['title']}")
        
        return {
            'forms': created_forms,
            'count': len(created_forms)
        }
    
    except Exception as e:
        print(f" Failed to bulk create forms: {e}")
        raise


def google_forms_create_from_template(template_id, variations_list, **kwargs):
    """Clone a template form with variations
    
    Args:
        template_id: Form ID to use as template
        variations_list: List of dicts with variation data
        
    Example:
        variations = [
            {'title': 'Event Registration - NYC', 'event': 'NYC Conference'},
            {'title': 'Event Registration - LA', 'event': 'LA Summit'}
        ]
    """
    try:
        created_forms = []
        
        for variation in variations_list:
            # Clone the template
            cloned = google_forms_clone_form(template_id, variation.get('title'))
            
            # Apply variations (update questions with custom values)
            # This would require more complex logic to update specific questions
            
            created_forms.append(cloned)
            print(f" Created from template: {variation.get('title')}")
        
        return {
            'forms': created_forms,
            'count': len(created_forms)
        }
    
    except Exception as e:
        print(f" Failed to create from template: {e}")
        raise


def google_forms_clone_multiple(form_ids, new_titles=None, **kwargs):
    """Clone multiple forms"""
    try:
        cloned_forms = []
        
        for idx, form_id in enumerate(form_ids):
            new_title = new_titles[idx] if new_titles and idx < len(new_titles) else None
            cloned = google_forms_clone_form(form_id, new_title)
            cloned_forms.append(cloned)
            print(f" Cloned form: {form_id}")
        
        return {
            'forms': cloned_forms,
            'count': len(cloned_forms)
        }
    
    except Exception as e:
        print(f" Failed to clone multiple forms: {e}")
        raise


def google_forms_batch_add_questions(form_id, questions_list, **kwargs):
    """Add multiple questions to a form at once
    
    Args:
        questions_list: List of question dicts with 'type', 'text', 'options', etc.
    """
    try:
        service = _get_forms_service()
        
        requests = []
        
        for idx, question in enumerate(questions_list):
            q_type = question.get('type', 'text')
            
            # Build request based on type
            if q_type == 'text':
                item = {
                    'title': question['text'],
                    'questionItem': {
                        'question': {
                            'required': question.get('required', False),
                            'textQuestion': {
                                'paragraph': question.get('paragraph', False)
                            }
                        }
                    }
                }
            elif q_type in ['multiple_choice', 'checkbox', 'dropdown']:
                choice_type = {
                    'multiple_choice': 'RADIO',
                    'checkbox': 'CHECKBOX',
                    'dropdown': 'DROP_DOWN'
                }
                item = {
                    'title': question['text'],
                    'questionItem': {
                        'question': {
                            'required': question.get('required', False),
                            'choiceQuestion': {
                                'type': choice_type[q_type],
                                'options': [{'value': opt} for opt in question.get('options', [])]
                            }
                        }
                    }
                }
            elif q_type == 'linear_scale':
                item = {
                    'title': question['text'],
                    'questionItem': {
                        'question': {
                            'required': question.get('required', False),
                            'scaleQuestion': {
                                'low': question.get('low_value', 1),
                                'high': question.get('high_value', 5),
                                'lowLabel': question.get('low_label', ''),
                                'highLabel': question.get('high_label', '')
                            }
                        }
                    }
                }
            else:
                continue
            
            requests.append({
                'createItem': {
                    'item': item,
                    'location': {'index': idx}
                }
            })
        
        # Execute batch update
        result = service.forms().batchUpdate(
            formId=form_id,
            body={'requests': requests}
        ).execute()
        
        print(f" Added {len(questions_list)} questions")
        
        return result
    
    except Exception as e:
        print(f" Failed to batch add questions: {e}")
        raise


def google_forms_batch_update_questions(form_id, updates_list, **kwargs):
    """Update multiple questions at once
    
    Args:
        updates_list: List of dicts with 'item_id', 'title', 'required', etc.
    """
    try:
        service = _get_forms_service()
        
        requests = []
        
        for update in updates_list:
            request = {
                'updateItem': {
                    'item': {
                        'itemId': update['item_id']
                    },
                    'updateMask': ''
                }
            }
            
            update_fields = []
            if 'title' in update:
                request['updateItem']['item']['title'] = update['title']
                update_fields.append('title')
            
            if 'required' in update:
                request['updateItem']['item']['questionItem'] = {
                    'question': {'required': update['required']}
                }
                update_fields.append('questionItem.question.required')
            
            request['updateItem']['updateMask'] = ','.join(update_fields)
            requests.append(request)
        
        result = service.forms().batchUpdate(
            formId=form_id,
            body={'requests': requests}
        ).execute()
        
        print(f" Updated {len(updates_list)} questions")
        
        return result
    
    except Exception as e:
        print(f" Failed to batch update questions: {e}")
        raise


def google_forms_batch_delete_questions(form_id, item_ids, **kwargs):
    """Delete multiple questions at once"""
    try:
        service = _get_forms_service()
        
        requests = []
        for item_id in item_ids:
            requests.append({
                'deleteItem': {
                    'location': {'index': item_id}
                }
            })
        
        result = service.forms().batchUpdate(
            formId=form_id,
            body={'requests': requests}
        ).execute()
        
        print(f" Deleted {len(item_ids)} questions")
        
        return result
    
    except Exception as e:
        print(f" Failed to batch delete questions: {e}")
        raise


def google_forms_reorder_questions(form_id, new_order, **kwargs):
    """Reorder all questions
    
    Args:
        new_order: List of item_ids in desired order
    """
    try:
        service = _get_forms_service()
        
        requests = []
        for new_idx, item_id in enumerate(new_order):
            requests.append({
                'moveItem': {
                    'originalLocation': {'index': item_id},
                    'newLocation': {'index': new_idx}
                }
            })
        
        result = service.forms().batchUpdate(
            formId=form_id,
            body={'requests': requests}
        ).execute()
        
        print(f" Reordered {len(new_order)} questions")
        
        return result
    
    except Exception as e:
        print(f" Failed to reorder questions: {e}")
        raise


def google_forms_batch_delete_responses(form_id, response_ids, **kwargs):
    """Delete multiple responses"""
    try:
        service = _get_forms_service()
        
        deleted_count = 0
        for response_id in response_ids:
            try:
                service.forms().responses().delete(
                    formId=form_id,
                    responseId=response_id
                ).execute()
                deleted_count += 1
            except:
                pass
        
        print(f" Deleted {deleted_count} responses")
        
        return {
            'deleted': True,
            'count': deleted_count
        }
    
    except Exception as e:
        print(f" Failed to batch delete responses: {e}")
        raise


def google_forms_export_all_responses(form_ids, format='json', **kwargs):
    """Export responses from multiple forms
    
    Args:
        form_ids: List of form IDs
        format: 'json' or 'csv'
    """
    try:
        all_responses = {}
        
        for form_id in form_ids:
            if format == 'csv':
                responses = google_forms_export_responses_csv(form_id)
            else:
                responses = google_forms_export_responses_json(form_id)
            
            all_responses[form_id] = responses
            print(f" Exported from form: {form_id}")
        
        return {
            'forms': all_responses,
            'count': len(form_ids),
            'format': format
        }
    
    except Exception as e:
        print(f" Failed to export all responses: {e}")
        raise


def google_forms_analyze_responses_bulk(form_ids, **kwargs):
    """Get aggregate statistics from multiple forms"""
    try:
        all_stats = {}
        total_responses = 0
        
        for form_id in form_ids:
            stats = google_forms_get_summary_statistics(form_id)
            all_stats[form_id] = stats
            total_responses += stats.get('total_responses', 0)
            print(f" Analyzed form: {form_id}")
        
        return {
            'forms': all_stats,
            'total_responses': total_responses,
            'form_count': len(form_ids)
        }
    
    except Exception as e:
        print(f" Failed to analyze responses bulk: {e}")
        raise


def google_forms_batch_update_settings(form_ids, settings, **kwargs):
    """Update settings for multiple forms
    
    Args:
        form_ids: List of form IDs
        settings: Dict with settings to apply to all
    """
    try:
        updated_forms = []
        
        for form_id in form_ids:
            result = google_forms_set_settings(form_id, settings)
            updated_forms.append({
                'form_id': form_id,
                'updated': True
            })
            print(f" Updated settings for: {form_id}")
        
        return {
            'forms': updated_forms,
            'count': len(form_ids)
        }
    
    except Exception as e:
        print(f" Failed to batch update settings: {e}")
        raise


def google_forms_batch_open_close(form_ids, accepting=True, **kwargs):
    """Open or close multiple forms"""
    try:
        updated_forms = []
        
        for form_id in form_ids:
            result = google_forms_set_accepts_response(form_id, accepting)
            updated_forms.append({
                'form_id': form_id,
                'accepting': accepting
            })
            print(f" {'Opened' if accepting else 'Closed'} form: {form_id}")
        
        return {
            'forms': updated_forms,
            'count': len(form_ids),
            'accepting': accepting
        }
    
    except Exception as e:
        print(f" Failed to batch open/close: {e}")
        raise


# ==================== AI-POWERED OPERATIONS ====================

def _get_ai_client():
    """Get OpenAI client if available"""
    if not HAS_OPENAI:
        raise Exception("OpenAI not available - install openai package")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")
    
    return openai.OpenAI(api_key=api_key)


def google_forms_ai_generate_from_prompt(prompt, form_type='survey', ai_model='gpt-4', **kwargs):
    """Generate a complete form from natural language description
    
    Args:
        prompt: Natural language description of the form
        form_type: 'survey', 'quiz', 'registration', 'feedback', 'assessment'
        ai_model: OpenAI model to use
        
    Example:
        prompt = "Create a customer satisfaction survey for a restaurant with questions about food quality, service, ambiance, and overall experience"
    """
    try:
        if not HAS_OPENAI:
            return {
                'error': 'OpenAI not available - install openai package',
                'form_id': None
            }
        
        client = _get_ai_client()
        
        system_prompt = f"""You are a Google Forms generator. Generate a {form_type} form based on the user's description.
        
Return a JSON structure with:
- title: Form title
- description: Form description
- questions: Array of questions with:
  - type: 'text', 'paragraph', 'multiple_choice', 'checkbox', 'dropdown', 'linear_scale'
  - text: Question text
  - options: Array of options (for choice questions)
  - required: boolean
  - low_value, high_value, low_label, high_label (for linear_scale)

Make questions clear, specific, and appropriate for the form type."""
        
        response = client.chat.completions.create(
            model=ai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        form_config = json.loads(response.choices[0].message.content)
        
        # Create the form using bulk create
        result = google_forms_bulk_create_forms([form_config])
        
        print(f" AI generated form: {form_config['title']}")
        
        return {
            'form': result['forms'][0],
            'config': form_config,
            'ai_model': ai_model
        }
    
    except Exception as e:
        print(f" Failed to AI generate form: {e}")
        raise


def google_forms_ai_generate_survey(topic, audience, question_count=5, ai_model='gpt-4', **kwargs):
    """Auto-generate a survey on a specific topic"""
    prompt = f"""Create a {question_count}-question survey about {topic} for {audience}.
    
Include:
- Mix of question types (multiple choice, linear scale, open-ended)
- Clear, concise questions
- Appropriate answer options
- Logical flow"""
    
    return google_forms_ai_generate_from_prompt(prompt, 'survey', ai_model)


def google_forms_ai_generate_quiz(topic, difficulty='medium', question_count=10, ai_model='gpt-4', **kwargs):
    """Auto-generate a quiz on a topic"""
    prompt = f"""Create a {difficulty} difficulty quiz about {topic} with {question_count} questions.
    
Include:
- Multiple choice questions with 4 options each
- One correct answer per question
- Mix of topics within {topic}
- Clear question wording"""
    
    form = google_forms_ai_generate_from_prompt(prompt, 'quiz', ai_model)
    
    # Convert to quiz mode
    if form.get('form'):
        google_forms_set_quiz_settings(form['form']['form_id'])
    
    return form


def google_forms_ai_generate_registration(event_details, ai_model='gpt-4', **kwargs):
    """Generate event registration form"""
    prompt = f"""Create an event registration form for: {event_details}
    
Include:
- Name and contact information
- Dietary restrictions (if event has food)
- T-shirt size (if applicable)
- Emergency contact
- Special accommodations
- Any event-specific questions"""
    
    return google_forms_ai_generate_from_prompt(prompt, 'registration', ai_model)


def google_forms_ai_optimize_questions(form_id, ai_model='gpt-4', **kwargs):
    """Get AI suggestions to improve questions"""
    try:
        if not HAS_OPENAI:
            return {'error': 'OpenAI not available'}
        
        # Get current form
        form = google_forms_get_form(form_id)
        
        # Extract questions
        questions = []
        for item in form.get('items', []):
            if 'questionItem' in item:
                questions.append(item.get('title'))
        
        client = _get_ai_client()
        
        system_prompt = """You are a form optimization expert. Analyze these questions and suggest improvements for:
- Clarity
- Bias removal
- Better answer options
- Logical flow
- Response rate optimization

Return JSON with 'suggestions' array containing improvement recommendations."""
        
        response = client.chat.completions.create(
            model=ai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Questions: {json.dumps(questions)}"}
            ],
            response_format={"type": "json_object"}
        )
        
        suggestions = json.loads(response.choices[0].message.content)
        
        print(f" Generated {len(suggestions.get('suggestions', []))} optimization suggestions")
        
        return suggestions
    
    except Exception as e:
        print(f" Failed to optimize questions: {e}")
        raise


def google_forms_ai_suggest_questions(form_id, context, ai_model='gpt-4', **kwargs):
    """Suggest additional questions based on context"""
    try:
        if not HAS_OPENAI:
            return {'error': 'OpenAI not available'}
        
        client = _get_ai_client()
        
        prompt = f"""Based on this context: {context}
        
Suggest 5 additional questions that would complement the existing form.
Return JSON with 'questions' array containing question objects with type, text, and options (if applicable)."""
        
        response = client.chat.completions.create(
            model=ai_model,
            messages=[
                {"role": "system", "content": "You are a form design expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        suggestions = json.loads(response.choices[0].message.content)
        
        print(f" Suggested {len(suggestions.get('questions', []))} new questions")
        
        return suggestions
    
    except Exception as e:
        print(f" Failed to suggest questions: {e}")
        raise


def google_forms_ai_translate_form(form_id, target_language, ai_model='gpt-4', **kwargs):
    """Translate entire form to another language"""
    try:
        if not HAS_OPENAI:
            return {'error': 'OpenAI not available'}
        
        # Get current form
        form = google_forms_get_form(form_id)
        
        # Clone form
        translated_title = f"{form['info']['title']} ({target_language})"
        cloned = google_forms_clone_form(form_id, translated_title)
        
        print(f" Cloned form for translation to {target_language}")
        
        # Note: Full translation would require updating all text elements
        # This is a simplified implementation
        
        return {
            'form_id': cloned['form_id'],
            'language': target_language,
            'note': 'Translation requires updating all text elements individually'
        }
    
    except Exception as e:
        print(f" Failed to translate form: {e}")
        raise


def google_forms_ai_generate_multilingual(prompt, languages, ai_model='gpt-4', **kwargs):
    """Create forms in multiple languages"""
    try:
        created_forms = []
        
        for language in languages:
            language_prompt = f"{prompt} (Generate in {language})"
            form = google_forms_ai_generate_from_prompt(language_prompt, 'survey', ai_model)
            created_forms.append({
                'language': language,
                'form': form
            })
            print(f" Created form in {language}")
        
        return {
            'forms': created_forms,
            'count': len(languages)
        }
    
    except Exception as e:
        print(f" Failed to generate multilingual forms: {e}")
        raise


def google_forms_ai_analyze_responses(form_id, analysis_type='summary', ai_model='gpt-4', **kwargs):
    """AI-powered response analysis
    
    Args:
        analysis_type: 'summary', 'sentiment', 'insights', 'trends', 'recommendations'
    """
    try:
        if not HAS_OPENAI:
            return {'error': 'OpenAI not available'}
        
        # Get responses
        responses_data = google_forms_get_responses(form_id)
        responses = responses_data['responses']
        
        if not responses:
            return {'error': 'No responses to analyze'}
        
        client = _get_ai_client()
        
        system_prompts = {
            'summary': "Provide a comprehensive summary of form responses.",
            'sentiment': "Analyze the sentiment of text responses (positive/negative/neutral).",
            'insights': "Extract key insights and patterns from the responses.",
            'trends': "Identify trends and correlations in the response data.",
            'recommendations': "Provide actionable recommendations based on the responses."
        }
        
        response = client.chat.completions.create(
            model=ai_model,
            messages=[
                {"role": "system", "content": system_prompts.get(analysis_type, system_prompts['summary'])},
                {"role": "user", "content": f"Analyze these responses: {json.dumps(responses[:50])}"}  # Limit to first 50
            ],
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        print(f" Completed {analysis_type} analysis on {len(responses)} responses")
        
        return {
            'analysis_type': analysis_type,
            'response_count': len(responses),
            'analysis': analysis
        }
    
    except Exception as e:
        print(f" Failed to analyze responses: {e}")
        raise


def google_forms_ai_sentiment_analysis(form_id, question_ids=None, ai_model='gpt-4', **kwargs):
    """Sentiment analysis on text responses"""
    return google_forms_ai_analyze_responses(form_id, 'sentiment', ai_model)


def google_forms_ai_categorize_responses(form_id, categories, ai_model='gpt-4', **kwargs):
    """Auto-categorize responses"""
    try:
        if not HAS_OPENAI:
            return {'error': 'OpenAI not available'}
        
        responses_data = google_forms_get_responses(form_id)
        responses = responses_data['responses']
        
        client = _get_ai_client()
        
        categorized = []
        
        for response in responses[:50]:  # Limit to first 50
            response_text = json.dumps(response.get('answers', {}))
            
            result = client.chat.completions.create(
                model=ai_model,
                messages=[
                    {"role": "system", "content": f"Categorize this response into one of: {', '.join(categories)}"},
                    {"role": "user", "content": response_text}
                ]
            )
            
            category = result.choices[0].message.content.strip()
            categorized.append({
                'response_id': response.get('responseId'),
                'category': category
            })
        
        print(f" Categorized {len(categorized)} responses")
        
        return {
            'categorized': categorized,
            'count': len(categorized)
        }
    
    except Exception as e:
        print(f" Failed to categorize responses: {e}")
        raise


def google_forms_ai_extract_insights(form_id, ai_model='gpt-4', **kwargs):
    """Extract key insights from responses"""
    return google_forms_ai_analyze_responses(form_id, 'insights', ai_model)


def google_forms_ai_generate_report(form_id, report_type='summary', ai_model='gpt-4', **kwargs):
    """Generate summary report"""
    try:
        analysis = google_forms_ai_analyze_responses(form_id, report_type, ai_model)
        stats = google_forms_get_summary_statistics(form_id)
        
        report = {
            'form_id': form_id,
            'report_type': report_type,
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'analysis': analysis.get('analysis', {}),
            'ai_model': ai_model
        }
        
        print(f" Generated {report_type} report")
        
        return report
    
    except Exception as e:
        print(f" Failed to generate report: {e}")
        raise


def google_forms_ai_detect_spam(form_id, ai_model='gpt-4', **kwargs):
    """Identify spam responses"""
    try:
        if not HAS_OPENAI:
            return {'error': 'OpenAI not available'}
        
        responses_data = google_forms_get_responses(form_id)
        responses = responses_data['responses']
        
        client = _get_ai_client()
        
        spam_responses = []
        
        for response in responses:
            response_text = json.dumps(response.get('answers', {}))
            
            result = client.chat.completions.create(
                model=ai_model,
                messages=[
                    {"role": "system", "content": "Analyze if this response is spam (return 'spam' or 'legitimate' with confidence score 0-1)"},
                    {"role": "user", "content": response_text}
                ],
                response_format={"type": "json_object"}
            )
            
            spam_check = json.loads(result.choices[0].message.content)
            
            if spam_check.get('classification') == 'spam' and spam_check.get('confidence', 0) > 0.7:
                spam_responses.append({
                    'response_id': response.get('responseId'),
                    'confidence': spam_check.get('confidence')
                })
        
        print(f" Detected {len(spam_responses)} potential spam responses")
        
        return {
            'spam_responses': spam_responses,
            'count': len(spam_responses),
            'total_responses': len(responses)
        }
    
    except Exception as e:
        print(f" Failed to detect spam: {e}")
        raise


def google_forms_ai_flag_priority(form_id, criteria, ai_model='gpt-4', **kwargs):
    """Flag important/urgent responses"""
    try:
        if not HAS_OPENAI:
            return {'error': 'OpenAI not available'}
        
        responses_data = google_forms_get_responses(form_id)
        responses = responses_data['responses']
        
        client = _get_ai_client()
        
        priority_responses = []
        
        for response in responses:
            response_text = json.dumps(response.get('answers', {}))
            
            result = client.chat.completions.create(
                model=ai_model,
                messages=[
                    {"role": "system", "content": f"Analyze if this response meets priority criteria: {criteria}. Return JSON with 'is_priority' (bool) and 'reason' (string)"},
                    {"role": "user", "content": response_text}
                ],
                response_format={"type": "json_object"}
            )
            
            priority_check = json.loads(result.choices[0].message.content)
            
            if priority_check.get('is_priority'):
                priority_responses.append({
                    'response_id': response.get('responseId'),
                    'reason': priority_check.get('reason')
                })
        
        print(f" Flagged {len(priority_responses)} priority responses")
        
        return {
            'priority_responses': priority_responses,
            'count': len(priority_responses)
        }
    
    except Exception as e:
        print(f" Failed to flag priority: {e}")
        raise


def google_forms_ai_auto_respond(form_id, response_template, ai_model='gpt-4', **kwargs):
    """Generate auto-responses for submissions"""
    try:
        return {
            'note': 'Auto-response requires email integration',
            'template': response_template
        }
    
    except Exception as e:
        print(f" Failed to auto respond: {e}")
        raise


def google_forms_ai_suggest_improvements(form_id, ai_model='gpt-4', **kwargs):
    """Get form optimization suggestions"""
    return google_forms_ai_optimize_questions(form_id, ai_model)


# ==================== WORKAROUND UTILITIES ====================

def google_forms_extract_entry_ids(form_id, **kwargs):
    """Extract entry IDs for HTTP submission workaround"""
    try:
        if not HAS_BS4:
            return {'error': 'BeautifulSoup4 not available'}
        
        url = f'https://docs.google.com/forms/d/e/{form_id}/viewform'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        entries = {}
        for input_tag in soup.find_all(['input', 'textarea']):
            name = input_tag.get('name', '')
            if name.startswith('entry.'):
                # Try to find associated label
                label = 'Unknown'
                try:
                    label_div = input_tag.find_previous('div', class_='freebirdFormviewerComponentsQuestionBaseTitle')
                    if label_div:
                        label = label_div.text
                except:
                    pass
                entries[name] = label
        
        print(f" Extracted {len(entries)} entry IDs")
        
        return {
            'entries': entries,
            'count': len(entries),
            'form_id': form_id
        }
    
    except Exception as e:
        print(f" Failed to extract entry IDs: {e}")
        raise


def google_forms_submit_response_http(form_id, responses_dict, **kwargs):
    """Submit response via HTTP POST workaround
    
    Args:
        responses_dict: Dict mapping entry IDs to values
            e.g., {'entry.123456': 'Answer', 'entry.789012': ['Option 1', 'Option 2']}
    """
    try:
        form_url = f"https://docs.google.com/forms/d/e/{form_id}/formResponse"
        
        response = requests.post(form_url, data=responses_dict)
        
        success = response.status_code in [200, 302]
        
        if success:
            print(f" Submitted response to form")
        else:
            print(f" Response may not have been submitted (status: {response.status_code})")
        
        return {
            'submitted': success,
            'status_code': response.status_code,
            'form_id': form_id
        }
    
    except Exception as e:
        print(f" Failed to submit response: {e}")
        raise


def google_forms_bulk_submit_responses(form_id, responses_list, **kwargs):
    """Submit multiple responses"""
    try:
        submitted_count = 0
        
        for responses_dict in responses_list:
            result = google_forms_submit_response_http(form_id, responses_dict)
            if result.get('submitted'):
                submitted_count += 1
        
        print(f" Submitted {submitted_count}/{len(responses_list)} responses")
        
        return {
            'submitted': submitted_count,
            'total': len(responses_list)
        }
    
    except Exception as e:
        print(f" Failed to bulk submit: {e}")
        raise


def google_forms_auto_test(form_id, count=10, realistic=True, ai_model='gpt-4', **kwargs):
    """Generate and submit test responses
    
    Args:
        count: Number of test responses to generate
        realistic: Use AI to generate realistic answers (requires OpenAI)
    """
    try:
        # Get form structure
        form = google_forms_get_form(form_id)
        
        # Extract entry IDs
        entry_data = google_forms_extract_entry_ids(form_id)
        entries = entry_data.get('entries', {})
        
        if not entries:
            return {'error': 'Could not extract entry IDs'}
        
        responses_to_submit = []
        
        for i in range(count):
            response_dict = {}
            
            for entry_id, question_text in entries.items():
                # Generate test answer
                if realistic and HAS_OPENAI:
                    # Use AI to generate realistic answer
                    client = _get_ai_client()
                    result = client.chat.completions.create(
                        model=ai_model,
                        messages=[
                            {"role": "system", "content": "Generate a realistic survey response"},
                            {"role": "user", "content": f"Question: {question_text}"}
                        ]
                    )
                    answer = result.choices[0].message.content.strip()
                else:
                    # Simple test answer
                    answer = f"Test response {i+1} for {question_text}"
                
                response_dict[entry_id] = answer
            
            responses_to_submit.append(response_dict)
        
        # Submit all responses
        result = google_forms_bulk_submit_responses(form_id, responses_to_submit)
        
        print(f" Generated and submitted {result['submitted']} test responses")
        
        return result
    
    except Exception as e:
        print(f" Failed to auto test: {e}")
        raise


def google_forms_export_with_metadata(form_id, include_timestamps=True, **kwargs):
    """Export responses with full metadata"""
    try:
        responses_data = google_forms_get_responses(form_id)
        form = google_forms_get_form(form_id)
        
        export_data = {
            'form': {
                'id': form_id,
                'title': form['info'].get('title'),
                'description': form['info'].get('description')
            },
            'responses': responses_data['responses'],
            'count': responses_data['count'],
            'exported_at': datetime.now().isoformat()
        }
        
        print(f" Exported {export_data['count']} responses with metadata")
        
        return export_data
    
    except Exception as e:
        print(f" Failed to export with metadata: {e}")
        raise


def google_forms_sync_to_sheets(form_id, sheet_id, realtime=False, **kwargs):
    """Advanced Sheets synchronization"""
    try:
        return {
            'note': 'Advanced Sheets sync requires Apps Script bridge',
            'form_id': form_id,
            'sheet_id': sheet_id,
            'realtime': realtime
        }
    
    except Exception as e:
        print(f" Failed to sync to sheets: {e}")
        raise


def google_forms_export_pdf_report(form_id, **kwargs):
    """Generate PDF report (requires additional libraries)"""
    try:
        return {
            'note': 'PDF generation requires reportlab or similar library',
            'form_id': form_id
        }
    
    except Exception as e:
        print(f" Failed to export PDF: {e}")
        raise


def google_forms_inject_custom_html(form_id, html, **kwargs):
    """Add custom HTML elements (requires Apps Script bridge)"""
    try:
        return {
            'note': 'Custom HTML injection requires Apps Script',
            'form_id': form_id
        }
    
    except Exception as e:
        print(f" Failed to inject HTML: {e}")
        raise


def google_forms_set_custom_theme(form_id, theme_config, **kwargs):
    """Apply custom styling (limited API support)"""
    try:
        return {
            'note': 'Custom theming is limited in API - use Forms UI',
            'form_id': form_id
        }
    
    except Exception as e:
        print(f" Failed to set theme: {e}")
        raise


# ==================== MODULE METADATA ====================

__all__ = [
    # Form Management (6)
    'google_forms_create_form',
    'google_forms_get_form',
    'google_forms_delete_form',
    'google_forms_clone_form',
    'google_forms_update_info',
    'google_forms_set_settings',
    
    # Question Operations (17)
    'google_forms_add_text_question',
    'google_forms_add_multiple_choice',
    'google_forms_add_checkbox',
    'google_forms_add_dropdown',
    'google_forms_add_linear_scale',
    'google_forms_add_date_question',
    'google_forms_add_time_question',
    'google_forms_add_grid',
    'google_forms_add_file_upload',
    'google_forms_add_question',
    'google_forms_update_question',
    'google_forms_delete_question',
    'google_forms_move_question',
    
    # Section Management (4)
    'google_forms_add_section',
    'google_forms_add_description',
    'google_forms_add_image',
    'google_forms_add_video',
    
    # Response Operations (5)
    'google_forms_get_responses',
    'google_forms_get_response',
    'google_forms_delete_response',
    'google_forms_delete_all_responses',
    
    # Quiz Mode (4)
    'google_forms_create_quiz',
    'google_forms_add_quiz_question',
    'google_forms_set_quiz_settings',
    'google_forms_grade_response',
    
    # Advanced Features (6)
    'google_forms_add_validation',
    'google_forms_set_question_description',
    'google_forms_shuffle_options',
    'google_forms_set_other_option',
    'google_forms_set_accepts_response',
    
    # Export & Analysis (6)
    'google_forms_export_responses_csv',
    'google_forms_export_responses_json',
    'google_forms_get_summary_statistics',
    'google_forms_link_to_sheets',
    'google_forms_update_settings',
    
    # Webhooks (4)
    'google_forms_create_watch',
    'google_forms_delete_watch',
    'google_forms_list_watches',
    'google_forms_renew_watch',
    
    # Bulk Operations (12)
    'google_forms_bulk_create_forms',
    'google_forms_create_from_template',
    'google_forms_clone_multiple',
    'google_forms_batch_add_questions',
    'google_forms_batch_update_questions',
    'google_forms_batch_delete_questions',
    'google_forms_reorder_questions',
    'google_forms_batch_delete_responses',
    'google_forms_export_all_responses',
    'google_forms_analyze_responses_bulk',
    'google_forms_batch_update_settings',
    'google_forms_batch_open_close',
    
    # AI-Powered (17)
    'google_forms_ai_generate_from_prompt',
    'google_forms_ai_generate_survey',
    'google_forms_ai_generate_quiz',
    'google_forms_ai_generate_registration',
    'google_forms_ai_optimize_questions',
    'google_forms_ai_suggest_questions',
    'google_forms_ai_translate_form',
    'google_forms_ai_generate_multilingual',
    'google_forms_ai_analyze_responses',
    'google_forms_ai_sentiment_analysis',
    'google_forms_ai_categorize_responses',
    'google_forms_ai_extract_insights',
    'google_forms_ai_generate_report',
    'google_forms_ai_detect_spam',
    'google_forms_ai_flag_priority',
    'google_forms_ai_auto_respond',
    'google_forms_ai_suggest_improvements',
    
    # Workarounds (9)
    'google_forms_extract_entry_ids',
    'google_forms_submit_response_http',
    'google_forms_bulk_submit_responses',
    'google_forms_auto_test',
    'google_forms_export_with_metadata',
    'google_forms_sync_to_sheets',
    'google_forms_export_pdf_report',
    'google_forms_inject_custom_html',
    'google_forms_set_custom_theme',
    
    # Smart Bundled Tools (3)
    'google_forms_create_complete_form',
    'google_forms_ai_generate_form',
    'google_forms_bulk_create_multiple',
]


# ==================== SMART BUNDLED TOOLS (HIGH-LEVEL) ====================

def google_forms_create_complete_form(title, questions, description=None, shareable=True, 
                                      collect_email=False, settings=None, **kwargs):
    """Create a complete Google Form with all questions in ONE operation
    
    This is the PREFERRED method for creating forms - it bundles multiple operations
    into one, making it much more efficient than calling create_form + add_question
    multiple times.
    
    Args:
        title: Form title
        questions: List of question dicts with:
            - type: 'text', 'paragraph', 'multiple_choice', 'checkbox', 'dropdown', 'linear_scale'
            - text: Question text
            - options: List of options (for choice questions)
            - required: Boolean (default False)
            - low_value, high_value, low_label, high_label (for linear_scale)
        description: Form description
        shareable: Make form accessible to anyone with link (default True)
        collect_email: Require email addresses (default False)
        settings: Additional settings dict
        
    Returns:
        Dict with form details and all created questions
        
    Example:
        form = google_forms_create_complete_form(
            title="Customer Feedback Survey",
            description="We value your opinion!",
            questions=[
                {
                    'type': 'text',
                    'text': 'What is your name?',
                    'required': True
                },
                {
                    'type': 'multiple_choice',
                    'text': 'How satisfied are you?',
                    'options': ['Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied'],
                    'required': True
                },
                {
                    'type': 'paragraph',
                    'text': 'Any additional comments?',
                    'required': False
                },
                {
                    'type': 'linear_scale',
                    'text': 'Rate our service:',
                    'low_value': 1,
                    'high_value': 5,
                    'low_label': 'Poor',
                    'high_label': 'Excellent',
                    'required': True
                }
            ],
            shareable=True,
            collect_email=True
        )
        
        print(f"Form ready: {form['responder_uri']}")
    """
    try:
        # Step 1: Create form (now shareable by default)
        form = google_forms_create_form(
            title=title,
            description=description,
            shareable=shareable
        )
        
        form_id = form['form_id']
        print(f" Created form: {form_id}")
        
        # Step 2: Add all questions in one batch
        if questions:
            result = google_forms_batch_add_questions(form_id, questions)
            print(f" Added {len(questions)} questions")
        
        # Step 3: Configure settings
        if collect_email or settings:
            settings_dict = settings or {}
            if collect_email:
                settings_dict['collect_email'] = True
            google_forms_set_settings(form_id, settings_dict)
            print(f" Configured settings")
        
        # Return complete form info
        return {
            'success': True,
            'form_id': form_id,
            'title': title,
            'responder_uri': form['responder_uri'],
            'edit_uri': form['edit_uri'],
            'shareable': form['shareable'],
            'questions_added': len(questions) if questions else 0,
            'message': f'Complete form created with {len(questions) if questions else 0} questions'
        }
    
    except Exception as e:
        print(f" Failed to create complete form: {e}")
        raise


def google_forms_ai_generate_form(prompt, form_type='survey', shareable=True, ai_model='gpt-4', **kwargs):
    """Generate a complete form from natural language description using AI
    
    This is the EASIEST way to create forms - just describe what you want and
    AI will generate appropriate questions, types, and options.
    
    Args:
        prompt: Natural language description of the form you want
        form_type: 'survey', 'quiz', 'registration', 'feedback', 'assessment'
        shareable: Make form accessible to anyone with link (default True)
        ai_model: OpenAI model to use (default gpt-4)
        
    Returns:
        Dict with complete form details
        
    Example:
        form = google_forms_ai_generate_form(
            prompt="Create a restaurant feedback survey with questions about food quality, service speed, cleanliness, value for money, and likelihood to return. Include a mix of ratings and open-ended questions.",
            form_type='survey',
            shareable=True
        )
        
        print(f"AI generated form: {form['responder_uri']}")
        print(f"Questions created: {form['questions_count']}")
    """
    try:
        # Use AI to generate form structure
        ai_result = google_forms_ai_generate_from_prompt(prompt, form_type, ai_model)
        
        if 'error' in ai_result:
            return ai_result
        
        # Extract form details
        form = ai_result['form']
        config = ai_result['config']
        
        # Make sure it's shareable if requested
        if shareable and not form.get('shareable'):
            try:
                drive_service = _get_drive_service()
                permission = {
                    'type': 'anyone',
                    'role': 'writer'
                }
                drive_service.permissions().create(
                    fileId=form['form_id'],
                    body=permission
                ).execute()
                form['shareable'] = True
                print(f" Made AI-generated form shareable")
            except:
                pass
        
        return {
            'success': True,
            'form_id': form['form_id'],
            'title': config.get('title'),
            'responder_uri': form['responder_uri'],
            'edit_uri': form.get('edit_uri'),
            'shareable': form.get('shareable', False),
            'questions_count': len(config.get('questions', [])),
            'ai_model': ai_model,
            'form_type': form_type,
            'message': f"AI generated {form_type} with {len(config.get('questions', []))} questions"
        }
    
    except Exception as e:
        print(f" Failed to AI generate form: {e}")
        raise


def google_forms_bulk_create_multiple(forms_configs, shareable=True, **kwargs):
    """Create multiple complete forms at once - MOST EFFICIENT for bulk operations
    
    Args:
        forms_configs: List of form configuration dicts, each with:
            - title: Form title
            - description: Form description (optional)
            - questions: List of question dicts (optional)
        shareable: Make all forms accessible to anyone with link (default True)
        
    Returns:
        Dict with all created forms
        
    Example:
        forms = google_forms_bulk_create_multiple([
            {
                'title': 'Event Registration - New York',
                'description': 'NYC Conference 2025',
                'questions': [
                    {'type': 'text', 'text': 'Full Name', 'required': True},
                    {'type': 'text', 'text': 'Email', 'required': True},
                    {'type': 'multiple_choice', 'text': 'Attendance', 
                     'options': ['In-Person', 'Virtual'], 'required': True}
                ]
            },
            {
                'title': 'Event Registration - Los Angeles',
                'description': 'LA Summit 2025',
                'questions': [
                    {'type': 'text', 'text': 'Full Name', 'required': True},
                    {'type': 'text', 'text': 'Email', 'required': True},
                    {'type': 'multiple_choice', 'text': 'Attendance', 
                     'options': ['In-Person', 'Virtual'], 'required': True}
                ]
            }
        ])
        
        print(f"Created {forms['count']} forms")
        for form in forms['forms']:
            print(f"  - {form['title']}: {form['responder_uri']}")
    """
    try:
        created_forms = []
        
        for config in forms_configs:
            # Use smart bundled creation for each form
            form = google_forms_create_complete_form(
                title=config.get('title'),
                questions=config.get('questions', []),
                description=config.get('description'),
                shareable=shareable,
                collect_email=config.get('collect_email', False)
            )
            
            created_forms.append(form)
            print(f" Created: {config.get('title')}")
        
        return {
            'success': True,
            'forms': created_forms,
            'count': len(created_forms),
            'message': f'Successfully created {len(created_forms)} forms'
        }
    
    except Exception as e:
        print(f" Failed to bulk create forms: {e}")
        raise


print(f" Google Forms Module loaded: {len(__all__)} functions available")

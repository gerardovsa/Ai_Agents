"""
Google Slides API Integration
==============================

Complete Google Slides functionality with advanced features:
- Presentation creation and management
- Slide manipulation (add, delete, duplicate, reorder)
- Text formatting (fonts, colors, sizes, styles)
- Shapes and objects (rectangles, circles, lines, arrows)
- Images and videos
- Tables and charts from Sheets
- Themes and layouts
- Animations and transitions
- Speaker notes
- Collaboration and sharing
- Export to PDF/PPTX

SMART BULK ACTIONS:
- Create complete pitch decks from data
- Generate training presentations
- Build reports with auto-formatting
- Create branded templates
"""

from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from .google_auth_helper import get_service_account_credentials, build_drive_service
import json
import time

# Slides API scopes
SLIDES_SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive.file'
]

def _get_user_credentials_if_available(user_id, injected_credentials_flag):
    """Helper to get user OAuth credentials from database
    
    Args:
        user_id: User ID (from _user_id parameter)
        injected_credentials_flag: Flag indicating credentials should be injected
    
    Returns:
        dict: Credential dictionary or None
    """
    if user_id and injected_credentials_flag:
        try:
            from AI_infrastructure.auth.user_auth import UserAuthManager
            auth_manager = UserAuthManager()
            cred_dict = auth_manager.get_user_google_oauth_credentials(user_id)
            if cred_dict:
                print(f"🔑 Using database OAuth credentials for user {user_id}")
                return cred_dict
            else:
                print(f"⚠️ User {user_id} has no Google OAuth credentials in database")
        except Exception as e:
            print(f"⚠️ Could not load user credentials: {e}")
    return None


def _get_slides_service(user_id=None, injected_credentials=None):
    """Get authenticated Google Slides service
    
    Args:
        user_id: User ID for OAuth credentials from database
        injected_credentials: OAuth credentials dict (from database)
    
    Returns:
        Authenticated Slides service
    """
    # If user credentials provided, use those (database OAuth)
    if user_id and injected_credentials:
        credentials = Credentials(
            token=injected_credentials['access_token'],
            refresh_token=injected_credentials.get('refresh_token'),
            token_uri=injected_credentials['token_uri'],
            client_id=injected_credentials['client_id'],
            client_secret=injected_credentials['client_secret'],
            scopes=injected_credentials['scopes']
        )
        print(f"📊 Building Slides service with user {user_id}'s OAuth credentials")
        return build('slides', 'v1', credentials=credentials)
    else:
        # Fallback to service account (may have permission issues)
        credentials = get_service_account_credentials(SLIDES_SCOPES)
        return build('slides', 'v1', credentials=credentials)


# ==================== CORE PRESENTATION OPERATIONS ====================

def google_slides_create_presentation(title, template_id=None, _user_id=None, _injected_credentials=None, **kwargs):
    """
    Create a new Google Slides presentation
    
    Args:
        title (str): Presentation title
        template_id (str): Optional template presentation ID to copy
        _user_id: User ID for credential injection (from tool registry)
        _injected_credentials: OAuth credentials flag (from database)
        **kwargs: Additional parameters
        
    Returns:
        dict: {
            'presentation_id': str,
            'url': str,
            'title': str,
            'slide_count': int
        }
    """
    try:
        # Get user OAuth credentials if available
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        
        if cred_dict:
            slides_service = _get_slides_service(user_id=_user_id, injected_credentials=cred_dict)
            drive_service = build_drive_service(user_id=_user_id, injected_credentials=cred_dict)
        else:
            # Fall back to service account (may have permission issues)
            slides_service = _get_slides_service()
            drive_service = build_drive_service()
        
        if template_id:
            # Copy from template
            copied_file = drive_service.files().copy(
                fileId=template_id,
                body={'name': title}
            ).execute()
            presentation_id = copied_file['id']
            
            presentation = slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            print(f"📊 Created presentation from template: {title}")
        else:
            # Create blank presentation
            presentation = slides_service.presentations().create(
                body={'title': title}
            ).execute()
            presentation_id = presentation['presentationId']
            
            print(f"📊 Created blank presentation: {title}")
        
        # Make shareable and editable
        permission = {
            'type': 'anyone',
            'role': 'writer'
        }
        drive_service.permissions().create(
            fileId=presentation_id,
            body=permission
        ).execute()
        
        url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
        slide_count = len(presentation.get('slides', []))
        
        print(f" Presentation shareable and editable: {url}")
        
        return {
            'presentation_id': presentation_id,
            'url': url,
            'title': title,
            'slide_count': slide_count
        }
        
    except Exception as e:
        print(f" Failed to create presentation: {e}")
        raise


def google_slides_get_presentation(presentation_id, format='summary', **kwargs):
    """
    Get presentation content with format control to prevent token overflow
    
    FORMAT OPTIONS:
    - 'summary' (DEFAULT): Returns title, slide count, slide titles/layouts preview (~1K tokens)
    - 'text': Returns all slide text content and speaker notes (~80K tokens for 24 slides)
    - 'markdown': Returns slides as markdown with structure metadata (~90K tokens for 24 slides)
    - 'full': Complete JSON with all positioning/styling (LEGACY - NOT RECOMMENDED, ~280K tokens)
    
    Args:
        presentation_id: Presentation ID
        format: Output format ('summary', 'text', 'markdown', 'full')
        **kwargs: Credential injection (_user_id, _injected_credentials)
        
    Returns:
        dict: Content in requested format
    """
    try:
        slides_service = _get_slides_service()
        
        presentation = slides_service.presentations().get(
            presentationId=presentation_id
        ).execute()
        
        title = presentation.get('title', 'Untitled Presentation')
        slides = presentation.get('slides', [])
        slide_count = len(slides)
        
        # FORMAT: summary (DEFAULT - 1K tokens)
        if format == 'summary':
            slide_summaries = []
            for idx, slide in enumerate(slides, 1):
                slide_id = slide.get('objectId')
                page_elements = slide.get('pageElements', [])
                
                # Extract slide title
                slide_title = None
                for element in page_elements:
                    if 'shape' in element:
                        shape = element['shape']
                        if shape.get('shapeType') == 'TEXT_BOX':
                            text = shape.get('text', {})
                            text_elements = text.get('textElements', [])
                            for text_el in text_elements:
                                if 'textRun' in text_el:
                                    content = text_el['textRun'].get('content', '').strip()
                                    if content and len(content) > 5:
                                        slide_title = content[:100]
                                        break
                            if slide_title:
                                break
                
                # Get layout info
                layout_id = slide.get('slideProperties', {}).get('layoutObjectId', '')
                layout_name = 'Unknown'
                for layout in presentation.get('layouts', []):
                    if layout.get('objectId') == layout_id:
                        layout_name = layout.get('layoutProperties', {}).get('displayName', 'Unknown')
                        break
                
                # Check for speaker notes
                notes_page = slide.get('slideProperties', {}).get('notesPage', {})
                has_notes = len(notes_page.get('pageElements', [])) > 1
                
                slide_summaries.append({
                    'slide_number': idx,
                    'slide_id': slide_id,
                    'title': slide_title or f'(Slide {idx})',
                    'layout': layout_name,
                    'element_count': len(page_elements),
                    'has_notes': has_notes
                })
            
            return {
                'success': True,
                'presentation_id': presentation_id,
                'title': title,
                'slide_count': slide_count,
                'slides': slide_summaries,
                'format': 'summary',
                'note': 'Use format="text" for full content or google_slides_get_slide() for specific slides'
            }
        
        # FORMAT: text (80K tokens for 24 slides)
        elif format == 'text':
            text_content = []
            
            for idx, slide in enumerate(slides, 1):
                slide_text = [f"=== Slide {idx} ==="]
                page_elements = slide.get('pageElements', [])
                
                # Extract all text from slide
                for element in page_elements:
                    if 'shape' in element:
                        shape = element['shape']
                        if 'text' in shape:
                            text_elements = shape['text'].get('textElements', [])
                            for text_el in text_elements:
                                if 'textRun' in text_el:
                                    content = text_el['textRun'].get('content', '').strip()
                                    if content:
                                        slide_text.append(content)
                
                # Extract speaker notes
                notes_page = slide.get('slideProperties', {}).get('notesPage', {})
                notes_elements = notes_page.get('pageElements', [])
                for notes_el in notes_elements:
                    if 'shape' in notes_el:
                        shape = notes_el['shape']
                        if 'text' in shape:
                            text_elements = shape['text'].get('textElements', [])
                            for text_el in text_elements:
                                if 'textRun' in text_el:
                                    notes_content = text_el['textRun'].get('content', '').strip()
                                    if notes_content and len(notes_content) > 10:
                                        slide_text.append(f"\n[Speaker Notes]: {notes_content}")
                
                text_content.append('\n'.join(slide_text))
            
            full_text = '\n\n'.join(text_content)
            
            return {
                'success': True,
                'presentation_id': presentation_id,
                'title': title,
                'text': full_text,
                'slide_count': slide_count,
                'format': 'text'
            }
        
        # FORMAT: markdown (90K tokens for 24 slides)
        elif format == 'markdown':
            markdown_lines = [f"# {title}\n"]
            
            for idx, slide in enumerate(slides, 1):
                markdown_lines.append(f"---\n**Slide {idx}**\n---\n")
                
                page_elements = slide.get('pageElements', [])
                
                # Extract text with basic formatting
                for element in page_elements:
                    if 'shape' in element:
                        shape = element['shape']
                        if 'text' in shape:
                            text_elements = shape['text'].get('textElements', [])
                            for text_el in text_elements:
                                if 'textRun' in text_el:
                                    content = text_el['textRun'].get('content', '').strip()
                                    style = text_el['textRun'].get('style', {})
                                    
                                    if content:
                                        # Apply basic formatting
                                        if style.get('bold'):
                                            content = f"**{content}**"
                                        if style.get('italic'):
                                            content = f"*{content}*"
                                        
                                        # Check font size for heading detection
                                        font_size = style.get('fontSize', {}).get('magnitude', 11)
                                        if font_size >= 24:
                                            markdown_lines.append(f"## {content}")
                                        elif font_size >= 18:
                                            markdown_lines.append(f"### {content}")
                                        else:
                                            markdown_lines.append(content)
                
                # Add speaker notes as blockquote
                notes_page = slide.get('slideProperties', {}).get('notesPage', {})
                notes_elements = notes_page.get('pageElements', [])
                for notes_el in notes_elements:
                    if 'shape' in notes_el:
                        shape = notes_el['shape']
                        if 'text' in shape:
                            text_elements = shape['text'].get('textElements', [])
                            for text_el in text_elements:
                                if 'textRun' in text_el:
                                    notes_content = text_el['textRun'].get('content', '').strip()
                                    if notes_content and len(notes_content) > 10:
                                        markdown_lines.append(f"\n> **Speaker Notes:** {notes_content}\n")
                
                markdown_lines.append("")
            
            markdown_content = '\n'.join(markdown_lines)
            
            return {
                'success': True,
                'presentation_id': presentation_id,
                'title': title,
                'markdown': markdown_content,
                'slide_count': slide_count,
                'format': 'markdown',
                'note': 'Slides converted to markdown with basic formatting'
            }
        
        # FORMAT: full (LEGACY - 280K+ tokens)
        elif format == 'full':
            print(f"📖 Retrieved presentation: {title}")
            print(f"   Slides: {slide_count}")
            
            return {
                'success': True,
                'presentation': presentation,
                'format': 'full',
                'warning': 'Full format can return 280K+ tokens for large presentations. Use format="summary" instead.'
            }
        
        else:
            raise ValueError(f"Invalid format: '{format}'. Use 'summary', 'text', 'markdown', or 'full'")
        
    except Exception as e:
        print(f"❌ Failed to get presentation: {e}")
        raise


def google_slides_get_slide(presentation_id, slide_number, **kwargs):
    """
    Get content from a specific slide
    
    Args:
        presentation_id (str): Presentation ID
        slide_number (int): Slide number (1-indexed)
        **kwargs: Credential injection parameters
    
    Returns:
        dict: Slide content including text, notes, and elements
    """
    try:
        # Get credentials
        user_id = kwargs.get('_user_id')
        injected_creds = kwargs.get('_injected_credentials')
        credentials_dict = _get_user_credentials_if_available(user_id, injected_creds)
        
        if credentials_dict:
            credentials = Credentials(
                token=credentials_dict.get('access_token'),
                refresh_token=credentials_dict.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
            )
            service = build('slides', 'v1', credentials=credentials)
        else:
            credentials = get_service_account_credentials(SLIDES_SCOPES)
            service = build('slides', 'v1', credentials=credentials)
        
        # Get full presentation
        presentation = service.presentations().get(presentationId=presentation_id).execute()
        
        slides = presentation.get('slides', [])
        
        if slide_number < 1 or slide_number > len(slides):
            raise ValueError(f"Slide number {slide_number} out of range (1-{len(slides)})")
        
        # Get the specific slide (convert to 0-indexed)
        slide = slides[slide_number - 1]
        
        # Extract text content
        text_content = []
        for element in slide.get('pageElements', []):
            if 'shape' in element and 'text' in element['shape']:
                for text_element in element['shape']['text'].get('textElements', []):
                    if 'textRun' in text_element:
                        text_content.append(text_element['textRun']['content'])
        
        # Get speaker notes
        notes_page = slide.get('slideProperties', {}).get('notesPage', {})
        speaker_notes = ""
        for element in notes_page.get('pageElements', []):
            if 'shape' in element and 'text' in element['shape']:
                for text_element in element['shape']['text'].get('textElements', []):
                    if 'textRun' in text_element:
                        speaker_notes += text_element['textRun']['content']
        
        # Count elements
        elements = slide.get('pageElements', [])
        element_types = {
            'text_boxes': 0,
            'images': 0,
            'shapes': 0,
            'tables': 0,
            'charts': 0
        }
        
        for element in elements:
            if 'shape' in element:
                if 'text' in element['shape']:
                    element_types['text_boxes'] += 1
                else:
                    element_types['shapes'] += 1
            elif 'image' in element:
                element_types['images'] += 1
            elif 'table' in element:
                element_types['tables'] += 1
            elif 'sheetsChart' in element:
                element_types['charts'] += 1
        
        # Get images metadata
        images = []
        for element in elements:
            if 'image' in element:
                img = element['image']
                images.append({
                    'url': img.get('contentUrl', ''),
                    'description': element.get('description', '')
                })
        
        result = {
            'success': True,
            'presentation_id': presentation_id,
            'slide_number': slide_number,
            'object_id': slide.get('objectId', ''),
            'layout': slide.get('slideProperties', {}).get('layoutObjectId', ''),
            'text_content': text_content,
            'speaker_notes': speaker_notes.strip(),
            'elements': element_types,
            'images': images
        }
        
        print(f"📄 Retrieved slide {slide_number}")
        print(f"   Text elements: {len(text_content)}")
        print(f"   Has speaker notes: {len(speaker_notes) > 0}")
        
        return result
        
    except Exception as e:
        print(f"❌ Failed to get slide: {e}")
        raise


def google_slides_search_presentation(presentation_id, query, **kwargs):
    """
    Search for slides containing specific text
    
    Args:
        presentation_id (str): Presentation ID
        query (str): Search query
        **kwargs: Credential injection parameters
    
    Returns:
        dict: Matching slides with context
    """
    try:
        # Get credentials
        user_id = kwargs.get('_user_id')
        injected_creds = kwargs.get('_injected_credentials')
        credentials_dict = _get_user_credentials_if_available(user_id, injected_creds)
        
        if credentials_dict:
            credentials = Credentials(
                token=credentials_dict.get('access_token'),
                refresh_token=credentials_dict.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
            )
            service = build('slides', 'v1', credentials=credentials)
        else:
            credentials = get_service_account_credentials(SLIDES_SCOPES)
            service = build('slides', 'v1', credentials=credentials)
        
        # Get full presentation
        presentation = service.presentations().get(presentationId=presentation_id).execute()
        
        title = presentation.get('title', 'Untitled')
        slides = presentation.get('slides', [])
        
        # Search through slides
        matches = []
        query_lower = query.lower()
        
        for idx, slide in enumerate(slides):
            slide_number = idx + 1
            
            # Get slide title (usually first text element)
            slide_title = ""
            elements = slide.get('pageElements', [])
            if elements:
                first_element = elements[0]
                if 'shape' in first_element and 'text' in first_element['shape']:
                    for text_el in first_element['shape']['text'].get('textElements', []):
                        if 'textRun' in text_el:
                            slide_title = text_el['textRun']['content'].strip()
                            break
            
            # Collect all text from slide
            all_text = []
            for element in elements:
                if 'shape' in element and 'text' in element['shape']:
                    for text_element in element['shape']['text'].get('textElements', []):
                        if 'textRun' in text_element:
                            all_text.append(text_element['textRun']['content'])
            
            full_text = "".join(all_text)
            
            # Get speaker notes
            notes_page = slide.get('slideProperties', {}).get('notesPage', {})
            speaker_notes = ""
            for element in notes_page.get('pageElements', []):
                if 'shape' in element and 'text' in element['shape']:
                    for text_element in element['shape']['text'].get('textElements', []):
                        if 'textRun' in text_element:
                            speaker_notes += text_element['textRun']['content']
            
            # Check if query matches
            if query_lower in full_text.lower() or query_lower in speaker_notes.lower():
                # Find the specific matching text with context
                matched_text = full_text if query_lower in full_text.lower() else ""
                matched_notes = speaker_notes if query_lower in speaker_notes.lower() else ""
                
                matches.append({
                    'slide_number': slide_number,
                    'title': slide_title or f"Slide {slide_number}",
                    'matched_text': matched_text[:500] if matched_text else "",  # Limit length
                    'speaker_notes': matched_notes[:500] if matched_notes else ""  # Limit length
                })
        
        result = {
            'success': True,
            'presentation_id': presentation_id,
            'title': title,
            'query': query,
            'matches': matches,
            'match_count': len(matches),
            'total_slides': len(slides)
        }
        
        print(f"🔍 Searched presentation: {title}")
        print(f"   Query: '{query}'")
        print(f"   Matches: {len(matches)} slides")
        
        return result
        
    except Exception as e:
        print(f"❌ Failed to search presentation: {e}")
        raise


# ==================== SLIDE OPERATIONS ====================

def google_slides_add_slide(presentation_id, layout='BLANK', index=None, **kwargs):
    """
    Add a new slide to presentation
    
    Args:
        presentation_id (str): Presentation ID
        layout (str): Layout type - BLANK, TITLE, TITLE_AND_BODY, TITLE_AND_TWO_COLUMNS, 
                     TITLE_ONLY, SECTION_HEADER, SECTION_TITLE_AND_DESCRIPTION,
                     ONE_COLUMN_TEXT, MAIN_POINT, BIG_NUMBER
        index (int): Position to insert (None = end)
        **kwargs: Credential injection (_user_id, _injected_credentials)
        
    Returns:
        dict: {
            'slide_id': str,
            'page_index': int,
            'layout': str
        }
    """
    try:
        slides_service = _get_slides_service()
        
        # Get presentation to find layout ID
        presentation = slides_service.presentations().get(
            presentationId=presentation_id
        ).execute()
        
        # Find the layout master
        layouts = presentation.get('layouts', [])
        layout_id = None
        
        # Try to find matching layout
        for layout_obj in layouts:
            layout_props = layout_obj.get('layoutProperties', {})
            if layout.upper() in layout_props.get('displayName', '').upper():
                layout_id = layout_obj.get('objectId')
                break
        
        # Default to first layout if not found
        if not layout_id and layouts:
            layout_id = layouts[0].get('objectId')
        
        requests = [{
            'createSlide': {
                'slideLayoutReference': {
                    'layoutId': layout_id
                } if layout_id else {
                    'predefinedLayout': 'BLANK'
                },
                'insertionIndex': index
            }
        }]
        
        response = slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        slide_id = response['replies'][0]['createSlide']['objectId']
        
        print(f" Added slide with layout: {layout}")
        
        return {
            'slide_id': slide_id,
            'page_index': index,
            'layout': layout
        }
        
    except Exception as e:
        print(f" Failed to add slide: {e}")
        raise


def google_slides_delete_slide(presentation_id, slide_id, **kwargs):
    """Delete a slide"""
    try:
        slides_service = _get_slides_service()
        
        requests = [{
            'deleteObject': {
                'objectId': slide_id
            }
        }]
        
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        print(f" Deleted slide: {slide_id}")
        
        return {'deleted': True, 'slide_id': slide_id}
        
    except Exception as e:
        print(f" Failed to delete slide: {e}")
        raise


def google_slides_duplicate_slide(presentation_id, slide_id, **kwargs):
    """Duplicate a slide"""
    try:
        slides_service = _get_slides_service()
        
        requests = [{
            'duplicateObject': {
                'objectId': slide_id
            }
        }]
        
        response = slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        new_slide_id = response['replies'][0]['duplicateObject']['objectId']
        
        print(f" Duplicated slide: {slide_id} → {new_slide_id}")
        
        return {
            'original_slide_id': slide_id,
            'new_slide_id': new_slide_id
        }
        
    except Exception as e:
        print(f" Failed to duplicate slide: {e}")
        raise


# ==================== TEXT OPERATIONS ====================

def google_slides_insert_text(presentation_id, slide_id, text, 
                              x=50, y=50, width=600, height=100,
                              font_family='Arial', font_size=14, 
                              bold=False, italic=False, 
                              color_hex='#000000', alignment='LEFT',
                              _user_id=None, _injected_credentials=None, **kwargs):
    """
    Insert text box with formatting
    
    Args:
        presentation_id (str): Presentation ID
        slide_id (str): Slide ID
        text (str): Text content
        x, y (float): Position in points (72 points = 1 inch)
        width, height (float): Size in points
        font_family (str): Font name (Arial, Calibri, Times New Roman, etc.)
        font_size (int): Font size in points
        bold (bool): Bold text
        italic (bool): Italic text
        color_hex (str): Text color in hex (#RRGGBB)
        alignment (str): LEFT, CENTER, RIGHT, JUSTIFIED
        _user_id: User ID for credential injection
        _injected_credentials: OAuth credentials flag
        
    Returns:
        dict: Text box object ID and properties
    """
    try:
        # Get user OAuth credentials if available
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        
        if cred_dict:
            slides_service = _get_slides_service(user_id=_user_id, injected_credentials=cred_dict)
        else:
            slides_service = _get_slides_service()
        
        # Generate unique ID
        text_box_id = f"textBox_{int(time.time() * 1000)}"
        
        # Convert hex color to RGB
        color_hex = color_hex.lstrip('#')
        r = int(color_hex[0:2], 16) / 255.0
        g = int(color_hex[2:4], 16) / 255.0
        b = int(color_hex[4:6], 16) / 255.0
        
        # Convert points to EMU (1 point = 12700 EMU)
        x_emu = x * 12700
        y_emu = y * 12700
        width_emu = width * 12700
        height_emu = height * 12700
        
        requests = [
            # Create text box
            {
                'createShape': {
                    'objectId': text_box_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': width_emu, 'unit': 'EMU'},
                            'height': {'magnitude': height_emu, 'unit': 'EMU'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': x_emu,
                            'translateY': y_emu,
                            'unit': 'EMU'
                        }
                    }
                }
            },
            # Insert text
            {
                'insertText': {
                    'objectId': text_box_id,
                    'text': text
                }
            },
            # Format text
            {
                'updateTextStyle': {
                    'objectId': text_box_id,
                    'style': {
                        'fontFamily': font_family,
                        'fontSize': {'magnitude': font_size, 'unit': 'PT'},
                        'bold': bold,
                        'italic': italic,
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': {'red': r, 'green': g, 'blue': b}
                            }
                        }
                    },
                    'fields': 'fontFamily,fontSize,bold,italic,foregroundColor'
                }
            },
            # Set alignment
            {
                'updateParagraphStyle': {
                    'objectId': text_box_id,
                    'style': {
                        'alignment': alignment
                    },
                    'fields': 'alignment'
                }
            }
        ]
        
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        print(f" Inserted text: '{text[:50]}...'")
        
        return {
            'text_box_id': text_box_id,
            'text': text,
            'position': {'x': x, 'y': y},
            'size': {'width': width, 'height': height}
        }
        
    except Exception as e:
        print(f" Failed to insert text: {e}")
        raise


# ==================== IMAGE OPERATIONS ====================

def google_slides_insert_image(presentation_id, slide_id, image_url,
                               x=50, y=50, width=400, height=300,
                               _user_id=None, _injected_credentials=None, **kwargs):
    """
    Insert image from URL
    
    Args:
        presentation_id (str): Presentation ID
        slide_id (str): Slide ID
        image_url (str): Public image URL
        x, y (float): Position in points
        width, height (float): Size in points
        _user_id: User ID for credential injection
        _injected_credentials: OAuth credentials flag
        
    Returns:
        dict: Image object ID and properties
    """
    try:
        # Get user OAuth credentials if available
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        
        if cred_dict:
            slides_service = _get_slides_service(user_id=_user_id, injected_credentials=cred_dict)
        else:
            slides_service = _get_slides_service()
        
        image_id = f"image_{int(time.time() * 1000)}"
        
        x_emu = x * 12700
        y_emu = y * 12700
        width_emu = width * 12700
        height_emu = height * 12700
        
        requests = [{
            'createImage': {
                'objectId': image_id,
                'url': image_url,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': width_emu, 'unit': 'EMU'},
                        'height': {'magnitude': height_emu, 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': x_emu,
                        'translateY': y_emu,
                        'unit': 'EMU'
                    }
                }
            }
        }]
        
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        print(f" Inserted image from: {image_url}")
        
        return {
            'image_id': image_id,
            'url': image_url,
            'position': {'x': x, 'y': y},
            'size': {'width': width, 'height': height}
        }
        
    except Exception as e:
        print(f" Failed to insert image: {e}")
        raise


# ==================== SHAPE OPERATIONS ====================

def google_slides_insert_shape(presentation_id, slide_id, shape_type='RECTANGLE',
                               x=50, y=50, width=200, height=100,
                               fill_color='#4285F4', border_color='#000000',
                               border_width=1,
                               _user_id=None, _injected_credentials=None, **kwargs):
    """
    Insert shape
    
    Args:
        presentation_id (str): Presentation ID
        slide_id (str): Slide ID
        shape_type (str): RECTANGLE, ELLIPSE, ROUND_RECTANGLE, TRIANGLE, 
                         RIGHT_TRIANGLE, STAR, ARROW_NORTH, ARROW_EAST, etc.
        x, y (float): Position in points
        width, height (float): Size in points
        fill_color (str): Fill color hex
        border_color (str): Border color hex
        border_width (float): Border width in points
        _user_id: User ID for credential injection
        _injected_credentials: OAuth credentials flag
        
    Returns:
        dict: Shape object ID and properties
    """
    try:
        # Get user OAuth credentials if available
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        
        if cred_dict:
            slides_service = _get_slides_service(user_id=_user_id, injected_credentials=cred_dict)
        else:
            slides_service = _get_slides_service()
        
        shape_id = f"shape_{int(time.time() * 1000)}"
        
        # Convert colors
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return {
                'red': int(hex_color[0:2], 16) / 255.0,
                'green': int(hex_color[2:4], 16) / 255.0,
                'blue': int(hex_color[4:6], 16) / 255.0
            }
        
        requests = [
            {
                'createShape': {
                    'objectId': shape_id,
                    'shapeType': shape_type,
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': width * 12700, 'unit': 'EMU'},
                            'height': {'magnitude': height * 12700, 'unit': 'EMU'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': x * 12700,
                            'translateY': y * 12700,
                            'unit': 'EMU'
                        }
                    }
                }
            },
            {
                'updateShapeProperties': {
                    'objectId': shape_id,
                    'shapeProperties': {
                        'shapeBackgroundFill': {
                            'solidFill': {
                                'color': {
                                    'rgbColor': hex_to_rgb(fill_color)
                                }
                            }
                        },
                        'outline': {
                            'outlineFill': {
                                'solidFill': {
                                    'color': {
                                        'rgbColor': hex_to_rgb(border_color)
                                    }
                                }
                            },
                            'weight': {'magnitude': border_width, 'unit': 'PT'}
                        }
                    },
                    'fields': 'shapeBackgroundFill,outline'
                }
            }
        ]
        
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        print(f" Inserted shape: {shape_type}")
        
        return {
            'shape_id': shape_id,
            'shape_type': shape_type,
            'position': {'x': x, 'y': y},
            'size': {'width': width, 'height': height}
        }
        
    except Exception as e:
        print(f" Failed to insert shape: {e}")
        raise


# ==================== TABLE OPERATIONS ====================

def google_slides_insert_table(presentation_id, slide_id, rows, columns,
                               x=50, y=50, width=600, height=400,
                               data=None,
                               _user_id=None, _injected_credentials=None, **kwargs):
    """
    Insert table
    
    Args:
        presentation_id (str): Presentation ID
        slide_id (str): Slide ID
        rows (int): Number of rows
        columns (int): Number of columns
        x, y (float): Position in points
        width, height (float): Size in points
        data (list[list]): Optional 2D array of cell data
        _user_id: User ID for credential injection
        _injected_credentials: OAuth credentials flag
        
    Returns:
        dict: Table object ID and properties
    """
    try:
        # Get user OAuth credentials if available
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        
        if cred_dict:
            slides_service = _get_slides_service(user_id=_user_id, injected_credentials=cred_dict)
        else:
            slides_service = _get_slides_service()
        
        table_id = f"table_{int(time.time() * 1000)}"
        
        requests = [{
            'createTable': {
                'objectId': table_id,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': width * 12700, 'unit': 'EMU'},
                        'height': {'magnitude': height * 12700, 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': x * 12700,
                        'translateY': y * 12700,
                        'unit': 'EMU'
                    }
                },
                'rows': rows,
                'columns': columns
            }
        }]
        
        # Add data if provided
        if data:
            for row_idx, row_data in enumerate(data):
                for col_idx, cell_value in enumerate(row_data):
                    if row_idx < rows and col_idx < columns:
                        requests.append({
                            'insertText': {
                                'objectId': table_id,
                                'cellLocation': {
                                    'rowIndex': row_idx,
                                    'columnIndex': col_idx
                                },
                                'text': str(cell_value)
                            }
                        })
        
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        print(f" Inserted table: {rows}x{columns}")
        
        return {
            'table_id': table_id,
            'rows': rows,
            'columns': columns,
            'position': {'x': x, 'y': y},
            'size': {'width': width, 'height': height}
        }
        
    except Exception as e:
        print(f" Failed to insert table: {e}")
        raise


# ==================== CHART FROM SHEETS ====================

def google_slides_insert_chart_from_sheets(presentation_id, slide_id,
                                           spreadsheet_id, chart_id,
                                           x=50, y=50, width=500, height=300,
                                           _user_id=None, _injected_credentials=None, **kwargs):
    """
    Insert chart from Google Sheets
    
    Args:
        presentation_id (str): Presentation ID
        slide_id (str): Slide ID
        spreadsheet_id (str): Source spreadsheet ID
        chart_id (int): Chart ID from spreadsheet
        x, y (float): Position in points
        width, height (float): Size in points
        _user_id: User ID for credential injection
        _injected_credentials: OAuth credentials flag
        
    Returns:
        dict: Chart object ID and properties
    """
    try:
        # Get user OAuth credentials if available
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        
        if cred_dict:
            slides_service = _get_slides_service(user_id=_user_id, injected_credentials=cred_dict)
        else:
            slides_service = _get_slides_service()
        
        chart_obj_id = f"chart_{int(time.time() * 1000)}"
        
        requests = [{
            'createSheetsChart': {
                'objectId': chart_obj_id,
                'spreadsheetId': spreadsheet_id,
                'chartId': chart_id,
                'linkingMode': 'LINKED',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': width * 12700, 'unit': 'EMU'},
                        'height': {'magnitude': height * 12700, 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': x * 12700,
                        'translateY': y * 12700,
                        'unit': 'EMU'
                    }
                }
            }
        }]
        
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        print(f" Inserted chart from Sheets")
        
        return {
            'chart_id': chart_obj_id,
            'spreadsheet_id': spreadsheet_id,
            'source_chart_id': chart_id,
            'position': {'x': x, 'y': y},
            'size': {'width': width, 'height': height}
        }
        
    except Exception as e:
        print(f" Failed to insert chart: {e}")
        raise


# ==================== EXPORT OPERATIONS ====================

def google_slides_export_as_pdf(presentation_id, **kwargs):
    """Export presentation as PDF"""
    try:
        from googleapiclient.http import MediaIoBaseDownload
        import io
        
        drive_service = build_drive_service()
        
        request = drive_service.files().export_media(
            fileId=presentation_id,
            mimeType='application/pdf'
        )
        
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        print(f" Exported presentation as PDF")
        
        return {
            'data': file.getvalue(),
            'mime_type': 'application/pdf',
            'size': len(file.getvalue())
        }
        
    except Exception as e:
        print(f" Failed to export as PDF: {e}")
        raise


def google_slides_export_as_pptx(presentation_id, **kwargs):
    """Export presentation as PowerPoint"""
    try:
        from googleapiclient.http import MediaIoBaseDownload
        import io
        
        drive_service = build_drive_service()
        
        request = drive_service.files().export_media(
            fileId=presentation_id,
            mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        print(f" Exported presentation as PPTX")
        
        return {
            'data': file.getvalue(),
            'mime_type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'size': len(file.getvalue())
        }
        
    except Exception as e:
        print(f" Failed to export as PPTX: {e}")
        raise


# ==================== SMART BULK ACTIONS ====================

def google_slides_create_pitch_deck(title, company_name, sections_data,
                                   brand_color='#4285F4', logo_url=None, **kwargs):
    """
    🎯 SMART ACTION: Create complete pitch deck with professional formatting
    
    Args:
        title (str): Presentation title
        company_name (str): Company name for branding
        sections_data (dict): {
            'problem': str,
            'solution': str,
            'market_size': {'tam': str, 'sam': str, 'som': str},
            'product': str,
            'business_model': str,
            'traction': [{'metric': str, 'value': str}, ...],
            'team': [{'name': str, 'role': str, 'bio': str}, ...],
            'financials': {'revenue': str, 'growth': str, 'runway': str},
            'ask': str,
            'contact': {'email': str, 'phone': str, 'website': str}
        }
        brand_color (str): Primary brand color hex
        logo_url (str): Optional company logo URL
        
    Returns:
        dict: Complete presentation with all slides created
    """
    try:
        print(f"🎯 Creating pitch deck for: {company_name}")
        
        # Create presentation
        result = google_slides_create_presentation(title)
        pres_id = result['presentation_id']
        
        # Get first slide (title slide)
        presentation = google_slides_get_presentation(pres_id)
        title_slide_id = presentation['slides'][0]['objectId']
        
        # ===== SLIDE 1: TITLE SLIDE =====
        google_slides_insert_text(
            pres_id, title_slide_id, company_name,
            x=50, y=150, width=620, height=80,
            font_family='Montserrat', font_size=48, bold=True,
            color_hex=brand_color, alignment='CENTER'
        )
        google_slides_insert_text(
            pres_id, title_slide_id, title,
            x=50, y=250, width=620, height=40,
            font_family='Arial', font_size=24,
            color_hex='#666666', alignment='CENTER'
        )
        if logo_url:
            google_slides_insert_image(
                pres_id, title_slide_id, logo_url,
                x=310, y=50, width=100, height=100
            )
        
        # ===== SLIDE 2: PROBLEM =====
        problem_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = problem_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "The Problem",
            x=50, y=50, width=620, height=50,
            font_family='Montserrat', font_size=36, bold=True,
            color_hex=brand_color
        )
        google_slides_insert_text(
            pres_id, slide_id, sections_data.get('problem', ''),
            x=50, y=120, width=620, height=300,
            font_family='Arial', font_size=18,
            color_hex='#333333'
        )
        
        # ===== SLIDE 3: SOLUTION =====
        solution_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = solution_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Our Solution",
            x=50, y=50, width=620, height=50,
            font_family='Montserrat', font_size=36, bold=True,
            color_hex=brand_color
        )
        google_slides_insert_text(
            pres_id, slide_id, sections_data.get('solution', ''),
            x=50, y=120, width=620, height=300,
            font_family='Arial', font_size=18,
            color_hex='#333333'
        )
        
        # ===== SLIDE 4: MARKET SIZE =====
        market_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = market_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Market Opportunity",
            x=50, y=50, width=620, height=50,
            font_family='Montserrat', font_size=36, bold=True,
            color_hex=brand_color
        )
        
        market = sections_data.get('market_size', {})
        y_pos = 120
        for label, value in [('TAM (Total Addressable)', market.get('tam')),
                            ('SAM (Serviceable Available)', market.get('sam')),
                            ('SOM (Serviceable Obtainable)', market.get('som'))]:
            if value:
                google_slides_insert_shape(
                    pres_id, slide_id, 'RECTANGLE',
                    x=50, y=y_pos, width=200, height=60,
                    fill_color=brand_color, border_width=0
                )
                google_slides_insert_text(
                    pres_id, slide_id, f"{label}\n{value}",
                    x=270, y=y_pos, width=400, height=60,
                    font_family='Arial', font_size=16, bold=True,
                    color_hex='#333333'
                )
                y_pos += 80
        
        # ===== SLIDE 5: PRODUCT =====
        product_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = product_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Product",
            x=50, y=50, width=620, height=50,
            font_family='Montserrat', font_size=36, bold=True,
            color_hex=brand_color
        )
        google_slides_insert_text(
            pres_id, slide_id, sections_data.get('product', ''),
            x=50, y=120, width=620, height=300,
            font_family='Arial', font_size=18,
            color_hex='#333333'
        )
        
        # ===== SLIDE 6: BUSINESS MODEL =====
        business_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = business_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Business Model",
            x=50, y=50, width=620, height=50,
            font_family='Montserrat', font_size=36, bold=True,
            color_hex=brand_color
        )
        google_slides_insert_text(
            pres_id, slide_id, sections_data.get('business_model', ''),
            x=50, y=120, width=620, height=300,
            font_family='Arial', font_size=18,
            color_hex='#333333'
        )
        
        # ===== SLIDE 7: TRACTION =====
        traction_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = traction_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Traction & Metrics",
            x=50, y=50, width=620, height=50,
            font_family='Montserrat', font_size=36, bold=True,
            color_hex=brand_color
        )
        
        traction_data = sections_data.get('traction', [])
        if traction_data:
            cols = min(len(traction_data), 3)
            col_width = 200
            spacing = 10
            start_x = (720 - (cols * col_width + (cols - 1) * spacing)) / 2
            
            for idx, metric in enumerate(traction_data[:3]):
                x_pos = start_x + (idx * (col_width + spacing))
                google_slides_insert_shape(
                    pres_id, slide_id, 'ROUND_RECTANGLE',
                    x=x_pos, y=150, width=col_width, height=150,
                    fill_color=brand_color, border_width=0
                )
                google_slides_insert_text(
                    pres_id, slide_id, metric.get('value', ''),
                    x=x_pos, y=170, width=col_width, height=60,
                    font_family='Montserrat', font_size=32, bold=True,
                    color_hex='#FFFFFF', alignment='CENTER'
                )
                google_slides_insert_text(
                    pres_id, slide_id, metric.get('metric', ''),
                    x=x_pos, y=240, width=col_width, height=40,
                    font_family='Arial', font_size=14,
                    color_hex='#FFFFFF', alignment='CENTER'
                )
        
        # ===== SLIDE 8: TEAM =====
        team_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = team_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Team",
            x=50, y=50, width=620, height=50,
            font_family='Montserrat', font_size=36, bold=True,
            color_hex=brand_color
        )
        
        team_data = sections_data.get('team', [])
        y_pos = 120
        for member in team_data[:3]:
            google_slides_insert_text(
                pres_id, slide_id, f"{member.get('name', '')} - {member.get('role', '')}",
                x=50, y=y_pos, width=620, height=30,
                font_family='Arial', font_size=16, bold=True,
                color_hex='#333333'
            )
            google_slides_insert_text(
                pres_id, slide_id, member.get('bio', ''),
                x=50, y=y_pos + 35, width=620, height=60,
                font_family='Arial', font_size=14,
                color_hex='#666666'
            )
            y_pos += 110
        
        # ===== SLIDE 9: FINANCIALS =====
        financials_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = financials_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Financials",
            x=50, y=50, width=620, height=50,
            font_family='Montserrat', font_size=36, bold=True,
            color_hex=brand_color
        )
        
        financials = sections_data.get('financials', {})
        fin_text = f"""Revenue: {financials.get('revenue', 'N/A')}
Growth Rate: {financials.get('growth', 'N/A')}
Runway: {financials.get('runway', 'N/A')}"""
        
        google_slides_insert_text(
            pres_id, slide_id, fin_text,
            x=50, y=150, width=620, height=200,
            font_family='Arial', font_size=20,
            color_hex='#333333'
        )
        
        # ===== SLIDE 10: THE ASK =====
        ask_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = ask_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "The Ask",
            x=50, y=50, width=620, height=50,
            font_family='Montserrat', font_size=36, bold=True,
            color_hex=brand_color
        )
        google_slides_insert_text(
            pres_id, slide_id, sections_data.get('ask', ''),
            x=50, y=120, width=620, height=300,
            font_family='Arial', font_size=22, bold=True,
            color_hex='#333333', alignment='CENTER'
        )
        
        # ===== SLIDE 11: CONTACT =====
        contact_slide = google_slides_add_slide(pres_id, 'BLANK')
        slide_id = contact_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Let's Talk",
            x=50, y=150, width=620, height=60,
            font_family='Montserrat', font_size=42, bold=True,
            color_hex=brand_color, alignment='CENTER'
        )
        
        contact = sections_data.get('contact', {})
        contact_text = f"""{contact.get('email', '')}
{contact.get('phone', '')}
{contact.get('website', '')}"""
        
        google_slides_insert_text(
            pres_id, slide_id, contact_text,
            x=50, y=240, width=620, height=100,
            font_family='Arial', font_size=18,
            color_hex='#333333', alignment='CENTER'
        )
        
        print(f" Created pitch deck with 11 slides")
        
        return {
            'presentation_id': pres_id,
            'url': result['url'],
            'title': title,
            'slide_count': 11,
            'sections': list(sections_data.keys())
        }
        
    except Exception as e:
        print(f" Failed to create pitch deck: {e}")
        raise


def google_slides_create_training_presentation(title, course_name, modules_data,
                                               brand_color='#0F9D58', **kwargs):
    """
    🎯 SMART ACTION: Create training presentation with exercises
    
    Args:
        title (str): Presentation title
        course_name (str): Course name
        modules_data (list): [{
            'module_title': str,
            'objectives': [str, ...],
            'content': str,
            'examples': [str, ...],
            'exercise': str,
            'key_takeaways': [str, ...]
        }, ...]
        brand_color (str): Course theme color
        
    Returns:
        dict: Complete training presentation
    """
    try:
        print(f"🎯 Creating training presentation: {course_name}")
        
        result = google_slides_create_presentation(title)
        pres_id = result['presentation_id']
        
        # Get title slide
        presentation = google_slides_get_presentation(pres_id)
        title_slide_id = presentation['slides'][0]['objectId']
        
        # TITLE SLIDE
        google_slides_insert_text(
            pres_id, title_slide_id, course_name,
            x=50, y=200, width=620, height=80,
            font_family='Roboto', font_size=44, bold=True,
            color_hex=brand_color, alignment='CENTER'
        )
        google_slides_insert_text(
            pres_id, title_slide_id, title,
            x=50, y=300, width=620, height=40,
            font_family='Arial', font_size=20,
            color_hex='#666666', alignment='CENTER'
        )
        
        # AGENDA SLIDE
        agenda_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = agenda_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Agenda",
            x=50, y=50, width=620, height=50,
            font_family='Roboto', font_size=36, bold=True,
            color_hex=brand_color
        )
        
        agenda_text = "\n".join([f"{i+1}. {m.get('module_title', '')}" 
                                for i, m in enumerate(modules_data)])
        google_slides_insert_text(
            pres_id, slide_id, agenda_text,
            x=80, y=120, width=560, height=300,
            font_family='Arial', font_size=18,
            color_hex='#333333'
        )
        
        # CREATE MODULE SLIDES
        for idx, module in enumerate(modules_data):
            module_num = idx + 1
            
            # MODULE TITLE SLIDE
            module_title_slide = google_slides_add_slide(pres_id, 'SECTION_HEADER')
            slide_id = module_title_slide['slide_id']
            google_slides_insert_shape(
                pres_id, slide_id, 'RECTANGLE',
                x=0, y=0, width=720, height=540,
                fill_color=brand_color, border_width=0
            )
            google_slides_insert_text(
                pres_id, slide_id, f"Module {module_num}",
                x=50, y=180, width=620, height=50,
                font_family='Roboto', font_size=28,
                color_hex='#FFFFFF', alignment='CENTER'
            )
            google_slides_insert_text(
                pres_id, slide_id, module.get('module_title', ''),
                x=50, y=240, width=620, height=80,
                font_family='Roboto', font_size=42, bold=True,
                color_hex='#FFFFFF', alignment='CENTER'
            )
            
            # LEARNING OBJECTIVES
            objectives_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
            slide_id = objectives_slide['slide_id']
            google_slides_insert_text(
                pres_id, slide_id, "Learning Objectives",
                x=50, y=50, width=620, height=50,
                font_family='Roboto', font_size=32, bold=True,
                color_hex=brand_color
            )
            
            objectives = module.get('objectives', [])
            obj_text = "\n".join([f"• {obj}" for obj in objectives])
            google_slides_insert_text(
                pres_id, slide_id, obj_text,
                x=80, y=120, width=560, height=300,
                font_family='Arial', font_size=18,
                color_hex='#333333'
            )
            
            # CONTENT SLIDE
            content_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
            slide_id = content_slide['slide_id']
            google_slides_insert_text(
                pres_id, slide_id, module.get('module_title', ''),
                x=50, y=50, width=620, height=50,
                font_family='Roboto', font_size=32, bold=True,
                color_hex=brand_color
            )
            google_slides_insert_text(
                pres_id, slide_id, module.get('content', ''),
                x=50, y=120, width=620, height=300,
                font_family='Arial', font_size=16,
                color_hex='#333333'
            )
            
            # EXAMPLES SLIDE
            if module.get('examples'):
                examples_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
                slide_id = examples_slide['slide_id']
                google_slides_insert_text(
                    pres_id, slide_id, "Examples",
                    x=50, y=50, width=620, height=50,
                    font_family='Roboto', font_size=32, bold=True,
                    color_hex=brand_color
                )
                
                examples = module.get('examples', [])
                ex_text = "\n\n".join([f"Example {i+1}:\n{ex}" 
                                      for i, ex in enumerate(examples)])
                google_slides_insert_text(
                    pres_id, slide_id, ex_text,
                    x=80, y=120, width=560, height=300,
                    font_family='Arial', font_size=14,
                    color_hex='#333333'
                )
            
            # EXERCISE SLIDE
            if module.get('exercise'):
                exercise_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
                slide_id = exercise_slide['slide_id']
                google_slides_insert_shape(
                    pres_id, slide_id, 'RECTANGLE',
                    x=0, y=0, width=720, height=100,
                    fill_color='#FFF3CD', border_width=0
                )
                google_slides_insert_text(
                    pres_id, slide_id, "✏️ Exercise Time",
                    x=50, y=25, width=620, height=50,
                    font_family='Roboto', font_size=32, bold=True,
                    color_hex='#856404'
                )
                google_slides_insert_text(
                    pres_id, slide_id, module.get('exercise', ''),
                    x=50, y=120, width=620, height=300,
                    font_family='Arial', font_size=18,
                    color_hex='#333333'
                )
            
            # KEY TAKEAWAYS SLIDE
            takeaways_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
            slide_id = takeaways_slide['slide_id']
            google_slides_insert_text(
                pres_id, slide_id, "Key Takeaways",
                x=50, y=50, width=620, height=50,
                font_family='Roboto', font_size=32, bold=True,
                color_hex=brand_color
            )
            
            takeaways = module.get('key_takeaways', [])
            takeaway_text = "\n".join([f"✓ {ta}" for ta in takeaways])
            google_slides_insert_text(
                pres_id, slide_id, takeaway_text,
                x=80, y=120, width=560, height=300,
                font_family='Arial', font_size=18, bold=True,
                color_hex='#333333'
            )
        
        # SUMMARY SLIDE
        summary_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = summary_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Course Summary",
            x=50, y=50, width=620, height=50,
            font_family='Roboto', font_size=36, bold=True,
            color_hex=brand_color
        )
        google_slides_insert_text(
            pres_id, slide_id, f"You've completed {len(modules_data)} modules!",
            x=50, y=150, width=620, height=40,
            font_family='Arial', font_size=20,
            color_hex='#333333', alignment='CENTER'
        )
        google_slides_insert_text(
            pres_id, slide_id, "Thank you for your participation!",
            x=50, y=250, width=620, height=60,
            font_family='Arial', font_size=24, bold=True,
            color_hex=brand_color, alignment='CENTER'
        )
        
        total_slides = 3 + (len(modules_data) * 6)  # Title + Agenda + Summary + (6 slides per module)
        
        print(f" Created training presentation with {total_slides} slides")
        
        return {
            'presentation_id': pres_id,
            'url': result['url'],
            'title': title,
            'slide_count': total_slides,
            'module_count': len(modules_data)
        }
        
    except Exception as e:
        print(f" Failed to create training presentation: {e}")
        raise


def google_slides_create_business_report(title, report_date, sections_data,
                                         charts_data=None, brand_color='#EA4335', **kwargs):
    """
    🎯 SMART ACTION: Create business report with charts and data
    
    Args:
        title (str): Report title
        report_date (str): Report period (e.g., "Q4 2025")
        sections_data (dict): {
            'executive_summary': str,
            'key_metrics': [{'label': str, 'value': str, 'change': str}, ...],
            'performance': str,
            'challenges': str,
            'opportunities': str,
            'action_items': [str, ...],
            'next_steps': str
        }
        charts_data (list): Optional [{
            'spreadsheet_id': str,
            'chart_id': int,
            'title': str
        }, ...]
        brand_color (str): Brand color
        
    Returns:
        dict: Complete business report presentation
    """
    try:
        print(f"🎯 Creating business report: {title}")
        
        result = google_slides_create_presentation(title)
        pres_id = result['presentation_id']
        
        presentation = google_slides_get_presentation(pres_id)
        title_slide_id = presentation['slides'][0]['objectId']
        
        # TITLE SLIDE
        google_slides_insert_text(
            pres_id, title_slide_id, title,
            x=50, y=180, width=620, height=70,
            font_family='Roboto', font_size=40, bold=True,
            color_hex=brand_color, alignment='CENTER'
        )
        google_slides_insert_text(
            pres_id, title_slide_id, report_date,
            x=50, y=270, width=620, height=40,
            font_family='Arial', font_size=24,
            color_hex='#666666', alignment='CENTER'
        )
        
        # EXECUTIVE SUMMARY
        summary_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = summary_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Executive Summary",
            x=50, y=50, width=620, height=50,
            font_family='Roboto', font_size=36, bold=True,
            color_hex=brand_color
        )
        google_slides_insert_text(
            pres_id, slide_id, sections_data.get('executive_summary', ''),
            x=50, y=120, width=620, height=300,
            font_family='Arial', font_size=16,
            color_hex='#333333'
        )
        
        # KEY METRICS DASHBOARD
        metrics_slide = google_slides_add_slide(pres_id, 'BLANK')
        slide_id = metrics_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Key Metrics",
            x=50, y=30, width=620, height=50,
            font_family='Roboto', font_size=36, bold=True,
            color_hex=brand_color
        )
        
        metrics = sections_data.get('key_metrics', [])
        cols = min(len(metrics), 3)
        if cols > 0:
            card_width = 200
            spacing = 10
            start_x = (720 - (cols * card_width + (cols - 1) * spacing)) / 2
            
            for idx, metric in enumerate(metrics[:3]):
                x_pos = start_x + (idx * (card_width + spacing))
                
                # Card background
                google_slides_insert_shape(
                    pres_id, slide_id, 'ROUND_RECTANGLE',
                    x=x_pos, y=100, width=card_width, height=180,
                    fill_color='#F8F9FA', border_color='#E0E0E0', border_width=1
                )
                
                # Metric value
                google_slides_insert_text(
                    pres_id, slide_id, metric.get('value', ''),
                    x=x_pos, y=130, width=card_width, height=60,
                    font_family='Roboto', font_size=36, bold=True,
                    color_hex=brand_color, alignment='CENTER'
                )
                
                # Metric label
                google_slides_insert_text(
                    pres_id, slide_id, metric.get('label', ''),
                    x=x_pos, y=200, width=card_width, height=30,
                    font_family='Arial', font_size=14,
                    color_hex='#666666', alignment='CENTER'
                )
                
                # Change indicator
                change = metric.get('change', '')
                change_color = '#0F9D58' if '+' in change else '#EA4335'
                google_slides_insert_text(
                    pres_id, slide_id, change,
                    x=x_pos, y=235, width=card_width, height=25,
                    font_family='Arial', font_size=12, bold=True,
                    color_hex=change_color, alignment='CENTER'
                )
        
        # CHARTS (if provided)
        if charts_data:
            for chart_info in charts_data:
                chart_slide = google_slides_add_slide(pres_id, 'TITLE_ONLY')
                slide_id = chart_slide['slide_id']
                google_slides_insert_text(
                    pres_id, slide_id, chart_info.get('title', 'Chart'),
                    x=50, y=30, width=620, height=40,
                    font_family='Roboto', font_size=28, bold=True,
                    color_hex=brand_color
                )
                
                google_slides_insert_chart_from_sheets(
                    pres_id, slide_id,
                    chart_info['spreadsheet_id'],
                    chart_info['chart_id'],
                    x=110, y=90, width=500, height=380
                )
        
        # PERFORMANCE
        perf_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = perf_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Performance Analysis",
            x=50, y=50, width=620, height=50,
            font_family='Roboto', font_size=36, bold=True,
            color_hex=brand_color
        )
        google_slides_insert_text(
            pres_id, slide_id, sections_data.get('performance', ''),
            x=50, y=120, width=620, height=300,
            font_family='Arial', font_size=16,
            color_hex='#333333'
        )
        
        # CHALLENGES
        challenges_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = challenges_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Challenges",
            x=50, y=50, width=620, height=50,
            font_family='Roboto', font_size=36, bold=True,
            color_hex='#EA4335'
        )
        google_slides_insert_text(
            pres_id, slide_id, sections_data.get('challenges', ''),
            x=50, y=120, width=620, height=300,
            font_family='Arial', font_size=16,
            color_hex='#333333'
        )
        
        # OPPORTUNITIES
        opp_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = opp_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Opportunities",
            x=50, y=50, width=620, height=50,
            font_family='Roboto', font_size=36, bold=True,
            color_hex='#0F9D58'
        )
        google_slides_insert_text(
            pres_id, slide_id, sections_data.get('opportunities', ''),
            x=50, y=120, width=620, height=300,
            font_family='Arial', font_size=16,
            color_hex='#333333'
        )
        
        # ACTION ITEMS
        action_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = action_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Action Items",
            x=50, y=50, width=620, height=50,
            font_family='Roboto', font_size=36, bold=True,
            color_hex=brand_color
        )
        
        actions = sections_data.get('action_items', [])
        action_text = "\n".join([f"□ {action}" for action in actions])
        google_slides_insert_text(
            pres_id, slide_id, action_text,
            x=80, y=120, width=560, height=300,
            font_family='Arial', font_size=18,
            color_hex='#333333'
        )
        
        # NEXT STEPS
        next_slide = google_slides_add_slide(pres_id, 'TITLE_AND_BODY')
        slide_id = next_slide['slide_id']
        google_slides_insert_text(
            pres_id, slide_id, "Next Steps",
            x=50, y=50, width=620, height=50,
            font_family='Roboto', font_size=36, bold=True,
            color_hex=brand_color
        )
        google_slides_insert_text(
            pres_id, slide_id, sections_data.get('next_steps', ''),
            x=50, y=120, width=620, height=300,
            font_family='Arial', font_size=18,
            color_hex='#333333'
        )
        
        chart_count = len(charts_data) if charts_data else 0
        total_slides = 9 + chart_count
        
        print(f" Created business report with {total_slides} slides")
        
        return {
            'presentation_id': pres_id,
            'url': result['url'],
            'title': title,
            'slide_count': total_slides,
            'chart_count': chart_count
        }
        
    except Exception as e:
        print(f" Failed to create business report: {e}")
        raise


# ==================== SMART DOCS → SLIDES INTEGRATION ====================

def google_docs_to_slides_auto_generate(
    doc_id,
    presentation_title=None,
    slide_style='modern',
    auto_create_sections=True,
    include_bullet_lists=True,
    include_images=True,
    include_tables=True,
    max_text_per_slide=300,
    brand_color='#1a73e8',
    template_id=None,
    **kwargs
):
    """
    🎯 SMART ACTION: Auto-generate slides from Google Doc as content is added
    
    Intelligently converts long-form Google Doc content into short-form presentation slides:
    - Detects document structure (headings, sections, paragraphs)
    - Chunks content into digestible slide-sized pieces
    - Creates title slides from Heading 1
    - Creates content slides from Heading 2/3
    - Extracts bullet points and lists
    - Includes images and tables
    - Auto-formats for readability
    - Applies consistent styling
    
    Perfect for:
    - Converting reports to presentations
    - Creating slides while writing docs
    - Transforming meeting notes to slides
    - Building training decks from documentation
    - Generating pitch decks from business plans
    
    Args:
        doc_id (str): Google Doc ID to convert
        presentation_title (str): Title for presentation (uses doc title if None)
        slide_style (str): 'modern', 'minimal', 'corporate', 'creative'
        auto_create_sections (bool): Auto-detect sections from headings
        include_bullet_lists (bool): Extract bullet points to slides
        include_images (bool): Include images from doc
        include_tables (bool): Include tables from doc
        max_text_per_slide (int): Maximum characters per content slide
        brand_color (str): Primary brand color hex code
        template_id (str): Optional template presentation ID
        
    Returns:
        dict: {
            'presentation_id': str,
            'url': str,
            'title': str,
            'slide_count': int,
            'sections_created': int,
            'doc_id': str,
            'doc_url': str,
            'conversion_summary': {
                'headings': int,
                'paragraphs': int,
                'lists': int,
                'images': int,
                'tables': int
            }
        }
    """
    try:
        from .google_docs import google_docs_read
        
        print(f"🔧 Reading Google Doc content from {doc_id}...")
        
        # Read the Google Doc
        doc_data = google_docs_read(doc_id)
        doc_title = doc_data.get('title', 'Untitled Document')
        doc_content = doc_data.get('content', '')
        
        if not doc_content:
            raise ValueError("Document is empty - no content to convert")
        
        print(f"📄 Found document: '{doc_title}' ({len(doc_content)} characters)")
        
        # Parse document structure
        print("🔍 Analyzing document structure...")
        structure = _parse_doc_structure(
            doc_content,
            auto_create_sections=auto_create_sections,
            include_bullet_lists=include_bullet_lists,
            max_text_per_slide=max_text_per_slide
        )
        
        print(f"📊 Detected: {structure['heading_1_count']} main sections, "
              f"{structure['heading_2_count']} subsections, "
              f"{structure['paragraph_count']} paragraphs, "
              f"{structure['list_count']} lists")
        
        # Create presentation
        pres_title = presentation_title or f"{doc_title} - Presentation"
        print(f"🎨 Creating presentation: '{pres_title}'...")
        
        result = google_slides_create_presentation(
            title=pres_title,
            template_id=template_id
        )
        pres_id = result['presentation_id']
        
        # Get presentation to work with slides
        service = _get_slides_service()
        presentation = service.presentations().get(presentationId=pres_id).execute()
        slides = presentation.get('slides', [])
        
        # Delete default blank slide if exists
        if slides and len(slides) == 1:
            first_slide_id = slides[0]['objectId']
            google_slides_delete_slide(pres_id, first_slide_id)
        
        # Apply theme/style
        theme_colors = _get_theme_colors(slide_style, brand_color)
        
        # Create title slide
        print("🎯 Creating title slide...")
        title_slide = google_slides_add_slide(pres_id, layout='TITLE')
        google_slides_insert_text(
            pres_id, title_slide['slide_id'], doc_title,
            x=50, y=150, width=620, height=120,
            font_family='Roboto', font_size=48, bold=True,
            color_hex=theme_colors['primary']
        )
        
        slide_count = 1
        sections_created = 0
        
        # Process each section
        for section in structure['sections']:
            section_type = section['type']
            
            if section_type == 'heading_1':
                # Create section divider slide
                print(f"📑 Creating section slide: '{section['content'][:50]}...'")
                section_slide = google_slides_add_slide(pres_id, layout='SECTION_HEADER')
                google_slides_insert_text(
                    pres_id, section_slide['slide_id'], section['content'],
                    x=50, y=200, width=620, height=120,
                    font_family='Roboto', font_size=44, bold=True,
                    color_hex=theme_colors['primary'],
                    alignment='CENTER'
                )
                slide_count += 1
                sections_created += 1
                
            elif section_type == 'heading_2':
                # Create content slide with title
                print(f"📝 Creating content slide: '{section['content'][:50]}...'")
                content_slide = google_slides_add_slide(pres_id, layout='TITLE_AND_BODY')
                
                # Add heading as slide title
                google_slides_insert_text(
                    pres_id, content_slide['slide_id'], section['content'],
                    x=50, y=50, width=620, height=60,
                    font_family='Roboto', font_size=32, bold=True,
                    color_hex=theme_colors['primary']
                )
                
                # Add content if available
                if section.get('body'):
                    body_text = _format_slide_content(section['body'], max_text_per_slide)
                    google_slides_insert_text(
                        pres_id, content_slide['slide_id'], body_text,
                        x=50, y=130, width=620, height=320,
                        font_family='Arial', font_size=18,
                        color_hex=theme_colors['text']
                    )
                
                slide_count += 1
                
            elif section_type == 'bullet_list' and include_bullet_lists:
                # Create bullet point slide
                print(f"🔹 Creating bullet list slide...")
                list_slide = google_slides_add_slide(pres_id, layout='TITLE_AND_BODY')
                
                list_title = section.get('title', 'Key Points')
                google_slides_insert_text(
                    pres_id, list_slide['slide_id'], list_title,
                    x=50, y=50, width=620, height=60,
                    font_family='Roboto', font_size=32, bold=True,
                    color_hex=theme_colors['primary']
                )
                
                # Format bullet points
                bullets = section.get('items', [])
                bullet_text = '\n'.join([f"• {item}" for item in bullets[:8]])  # Max 8 bullets
                
                google_slides_insert_text(
                    pres_id, list_slide['slide_id'], bullet_text,
                    x=70, y=130, width=580, height=320,
                    font_family='Arial', font_size=20,
                    color_hex=theme_colors['text']
                )
                
                slide_count += 1
                
            elif section_type == 'paragraph':
                # Create text content slide
                if len(section['content']) > 100:  # Only create slide if substantial content
                    print(f"📄 Creating paragraph slide...")
                    para_slide = google_slides_add_slide(pres_id, layout='BLANK')
                    
                    content_text = _format_slide_content(section['content'], max_text_per_slide)
                    google_slides_insert_text(
                        pres_id, para_slide['slide_id'], content_text,
                        x=50, y=80, width=620, height=400,
                        font_family='Arial', font_size=20,
                        color_hex=theme_colors['text']
                    )
                    
                    slide_count += 1
        
        # Create summary/closing slide
        print("🎯 Creating closing slide...")
        closing_slide = google_slides_add_slide(pres_id, layout='TITLE')
        google_slides_insert_text(
            pres_id, closing_slide['slide_id'], "Thank You",
            x=50, y=200, width=620, height=100,
            font_family='Roboto', font_size=48, bold=True,
            color_hex=theme_colors['primary'],
            alignment='CENTER'
        )
        slide_count += 1
        
        # Make presentation editable
        drive = build_drive_service()
        drive.permissions().create(
            fileId=pres_id,
            body={'type': 'anyone', 'role': 'writer'},
            fields='id'
        ).execute()
        
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        pres_url = f"https://docs.google.com/presentation/d/{pres_id}/edit"
        
        print(f" Successfully created presentation with {slide_count} slides!")
        print(f"📄 Source Doc: {doc_url}")
        print(f"🎨 Presentation: {pres_url}")
        
        return {
            'presentation_id': pres_id,
            'url': pres_url,
            'title': pres_title,
            'slide_count': slide_count,
            'sections_created': sections_created,
            'doc_id': doc_id,
            'doc_url': doc_url,
            'conversion_summary': {
                'headings': structure['heading_1_count'] + structure['heading_2_count'],
                'paragraphs': structure['paragraph_count'],
                'lists': structure['list_count'],
                'images': 0,  # Could be enhanced to extract images
                'tables': 0   # Could be enhanced to extract tables
            }
        }
        
    except Exception as e:
        print(f" Failed to convert doc to slides: {e}")
        raise


def _parse_doc_structure(content, auto_create_sections=True, include_bullet_lists=True, max_text_per_slide=300):
    """
    Parse document structure to identify sections, headings, lists, etc.
    
    This is a simplified parser - could be enhanced with actual Google Docs API
    to detect proper heading styles, lists, images, tables, etc.
    """
    lines = content.split('\n')
    
    sections = []
    heading_1_count = 0
    heading_2_count = 0
    paragraph_count = 0
    list_count = 0
    
    current_section = None
    current_body = []
    current_list_items = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        # Detect headings (simple heuristic - all caps or short lines)
        is_heading_1 = (line.isupper() and len(line) < 80 and not line.startswith(('•', '-', '*', '1', '2', '3')))
        is_heading_2 = (len(line) < 80 and line.endswith(':') and not line.startswith(('•', '-', '*')))
        
        # Detect bullet points
        is_bullet = line.startswith(('•', '-', '*', '▪', '○')) or (len(line) > 2 and line[0].isdigit() and line[1] in ('.', ')'))
        
        if is_heading_1 and auto_create_sections:
            # Save previous section
            if current_section:
                if current_body:
                    current_section['body'] = '\n'.join(current_body)
                sections.append(current_section)
                current_body = []
            
            # Start new heading 1 section
            current_section = {
                'type': 'heading_1',
                'content': line
            }
            heading_1_count += 1
            in_list = False
            
        elif is_heading_2 and auto_create_sections:
            # Save previous section
            if current_section:
                if current_body:
                    current_section['body'] = '\n'.join(current_body)
                sections.append(current_section)
                current_body = []
            
            # Start new heading 2 section
            current_section = {
                'type': 'heading_2',
                'content': line.rstrip(':')
            }
            heading_2_count += 1
            in_list = False
            
        elif is_bullet and include_bullet_lists:
            # Extract bullet text
            bullet_text = line.lstrip('•-*▪○').strip()
            if bullet_text and bullet_text[0].isdigit():
                bullet_text = bullet_text[bullet_text.find(' ')+1:]  # Remove number prefix
            
            if not in_list:
                # Start new list
                in_list = True
                current_list_items = [bullet_text]
            else:
                current_list_items.append(bullet_text)
                
        else:
            # Regular paragraph
            if in_list and current_list_items:
                # Save completed list
                if current_section and current_section['type'] in ('heading_2', 'heading_1'):
                    # Attach list to current section
                    if not current_section.get('body'):
                        current_section['body'] = ''
                else:
                    # Create standalone list slide
                    sections.append({
                        'type': 'bullet_list',
                        'title': current_section['content'] if current_section else 'Key Points',
                        'items': current_list_items[:8]  # Max 8 items
                    })
                    list_count += 1
                
                current_list_items = []
                in_list = False
            
            # Add to current body
            if current_section:
                current_body.append(line)
            else:
                # Create paragraph section
                sections.append({
                    'type': 'paragraph',
                    'content': line
                })
                paragraph_count += 1
    
    # Save final section
    if current_section:
        if current_body:
            current_section['body'] = '\n'.join(current_body)
        sections.append(current_section)
    
    # Save final list if exists
    if in_list and current_list_items:
        sections.append({
            'type': 'bullet_list',
            'title': 'Key Points',
            'items': current_list_items[:8]
        })
        list_count += 1
    
    return {
        'sections': sections,
        'heading_1_count': heading_1_count,
        'heading_2_count': heading_2_count,
        'paragraph_count': paragraph_count,
        'list_count': list_count
    }


def _format_slide_content(text, max_length=300):
    """Format text content for slide - truncate and clean up"""
    if len(text) <= max_length:
        return text
    
    # Truncate at sentence boundary
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    last_question = truncated.rfind('?')
    last_exclaim = truncated.rfind('!')
    
    cut_point = max(last_period, last_question, last_exclaim)
    
    if cut_point > max_length * 0.7:  # At least 70% of desired length
        return text[:cut_point+1]
    else:
        return truncated + '...'


def _get_theme_colors(style, brand_color):
    """Get color theme based on style"""
    themes = {
        'modern': {
            'primary': brand_color,
            'secondary': '#4285f4',
            'text': '#202124',
            'background': '#ffffff'
        },
        'minimal': {
            'primary': '#000000',
            'secondary': '#666666',
            'text': '#333333',
            'background': '#ffffff'
        },
        'corporate': {
            'primary': '#003366',
            'secondary': '#0066cc',
            'text': '#333333',
            'background': '#f8f9fa'
        },
        'creative': {
            'primary': '#ff6b6b',
            'secondary': '#4ecdc4',
            'text': '#2d3436',
            'background': '#ffffff'
        }
    }
    
    return themes.get(style, themes['modern'])

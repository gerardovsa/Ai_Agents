"""
Image Verification Core Module
===============================

Provides reverse image search and AI-generated face detection capabilities
for professional verification using FREE services.

Features:
- Reverse image search via Google, TinEye, Yandex
- AI-generated face detection
- EXIF metadata extraction
- Profile picture analysis
- Social media image verification
"""

import logging
import os
import base64
import hashlib
from typing import Dict, Any, Optional, List
from urllib.parse import quote, urlencode
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reverse_image_search_urls(
    image_url: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Generate reverse image search URLs for multiple platforms (FREE).
    
    Args:
        image_url: Direct URL to the image to search
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Search URLs for Google, TinEye, Yandex
    """
    logger.info(f"[REVERSE_IMAGE] Generating search URLs for: {image_url}")
    
    try:
        # Google Images reverse search
        google_url = f"https://www.google.com/searchbyimage?image_url={quote(image_url)}"
        
        # TinEye reverse search
        tineye_url = f"https://tineye.com/search?url={quote(image_url)}"
        
        # Yandex Images reverse search
        yandex_url = f"https://yandex.com/images/search?rpt=imageview&url={quote(image_url)}"
        
        # Bing reverse search
        bing_url = f"https://www.bing.com/images/search?view=detailv2&iss=sbi&form=SBIIRP&sbisrc=UrlPaste&q=imgurl:{quote(image_url)}"
        
        return {
            'success': True,
            'image_url': image_url,
            'search_urls': {
                'google': google_url,
                'tineye': tineye_url,
                'yandex': yandex_url,
                'bing': bing_url
            },
            'instructions': [
                '1. Open each URL in your browser',
                '2. Check if image appears on multiple unrelated profiles',
                '3. Look for stock photo watermarks or credits',
                '4. Note any AI-generated image indicators',
                '5. Check earliest appearance date'
            ]
        }
        
    except Exception as e:
        logger.error(f"[REVERSE_IMAGE] Error: {e}")
        return {'success': False, 'error': str(e)}


def reverse_image_search_file(
    image_path: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Generate reverse image search URLs for a local image file (FREE).
    
    Args:
        image_path: Path to local image file
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Search URLs and upload instructions
    """
    logger.info(f"[REVERSE_IMAGE_FILE] Processing: {image_path}")
    
    try:
        if not os.path.exists(image_path):
            return {'success': False, 'error': f'Image file not found: {image_path}'}
        
        # Get file hash for identification
        with open(image_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        # Get file size
        file_size = os.path.getsize(image_path)
        
        return {
            'success': True,
            'image_path': image_path,
            'file_hash': file_hash,
            'file_size_bytes': file_size,
            'upload_urls': {
                'google': 'https://images.google.com',
                'tineye': 'https://tineye.com',
                'yandex': 'https://yandex.com/images'
            },
            'instructions': [
                '1. Go to https://images.google.com',
                '2. Click the camera icon in the search bar',
                '3. Upload your image file',
                '4. Repeat for TinEye and Yandex',
                '5. Compare results across all platforms'
            ],
            'automated_search_note': 'Direct file upload requires browser interaction - use URLs above'
        }
        
    except Exception as e:
        logger.error(f"[REVERSE_IMAGE_FILE] Error: {e}")
        return {'success': False, 'error': str(e)}


def detect_ai_generated_face(
    image_url: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Analyze image for AI-generated face indicators (FREE analysis).
    
    Args:
        image_url: URL to the profile image
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Analysis of AI generation likelihood
    """
    logger.info(f"[AI_FACE_DETECT] Analyzing: {image_url}")
    
    try:
        # Download image with timeout and retry
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(image_url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        # Basic checks (without ML - looking for patterns)
        indicators = {
            'file_size_suspicious': len(response.content) < 50000,  # AI images often small
            'content_type': response.headers.get('Content-Type', ''),
            'file_size_bytes': len(response.content)
        }
        
        # AI-generated face red flags (manual verification needed)
        red_flags = [
            'Perfectly symmetrical face',
            'Unrealistic skin texture (too smooth)',
            'Warped background near hair edges',
            'Misaligned eyes or ears',
            'Unnatural hair transitions',
            'Floating accessories',
            'Inconsistent lighting',
            'No visible pores or skin details',
            'Generic professional background',
            'Too-perfect teeth alignment'
        ]
        
        return {
            'success': True,
            'image_url': image_url,
            'file_size': indicators['file_size_bytes'],
            'content_type': indicators['content_type'],
            'ai_detection_method': 'manual_visual_inspection',
            'red_flags_to_check': red_flags,
            'automated_detection': 'Not available without ML model',
            'recommendations': [
                'Download image and zoom to 200%',
                'Check background warping near face edges',
                'Look for symmetry that seems too perfect',
                'Compare skin texture to known real photos',
                'Check if pupils reflect light naturally',
                'Look for consistent lighting across face'
            ],
            'advanced_tools': {
                'illuminarty': 'https://illuminarty.ai (AI image detector)',
                'hive_moderation': 'https://hivemoderation.com/ai-generated-content-detection',
                'optic': 'https://optic.xyz/deepfake-detector'
            }
        }
        
    except Exception as e:
        logger.error(f"[AI_FACE_DETECT] Error: {e}")
        return {'success': False, 'error': str(e)}


def extract_image_metadata(
    image_url: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Extract EXIF metadata from image (FREE).
    
    Args:
        image_url: URL to the image
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        EXIF metadata including camera, date, GPS
    """
    logger.info(f"[EXIF_EXTRACT] Extracting metadata from: {image_url}")
    
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        from io import BytesIO
        
        # Download image with better headers and timeout
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(image_url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        # Open with PIL
        image = Image.open(BytesIO(response.content))
        
        # Extract EXIF data
        exif_data = {}
        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                exif_data[tag] = str(value)
        
        # Key indicators
        has_camera_data = 'Make' in exif_data or 'Model' in exif_data
        has_date = 'DateTime' in exif_data or 'DateTimeOriginal' in exif_data
        has_gps = any('GPS' in key for key in exif_data.keys())
        
        # AI-generated images typically lack camera EXIF
        ai_likelihood = 'high' if not has_camera_data else 'low'
        
        return {
            'success': True,
            'image_url': image_url,
            'has_exif_data': bool(exif_data),
            'has_camera_info': has_camera_data,
            'has_datetime': has_date,
            'has_gps': has_gps,
            'ai_generation_likelihood': ai_likelihood,
            'exif_data': exif_data,
            'image_format': image.format,
            'image_size': image.size,
            'image_mode': image.mode,
            'red_flags': [] if has_camera_data else ['No camera metadata - possible AI generation or screenshot']
        }
        
    except ImportError:
        logger.warning("[EXIF_EXTRACT] PIL not available")
        return {
            'success': False,
            'error': 'PIL (Pillow) library required for EXIF extraction',
            'install_command': 'pip install Pillow'
        }
    except Exception as e:
        logger.error(f"[EXIF_EXTRACT] Error: {e}")
        return {'success': False, 'error': str(e)}


def verify_profile_image_consistency(
    linkedin_url: str,
    facebook_url: str,
    twitter_url: Optional[str] = None,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Check if profile images are consistent across social platforms (FREE).
    
    Args:
        linkedin_url: LinkedIn profile URL
        facebook_url: Facebook profile URL
        twitter_url: Twitter/X profile URL (optional)
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Consistency analysis and verification URLs
    """
    logger.info(f"[PROFILE_CONSISTENCY] Checking across platforms")
    
    try:
        platforms = {
            'linkedin': linkedin_url,
            'facebook': facebook_url
        }
        if twitter_url:
            platforms['twitter'] = twitter_url
        
        # Generate verification instructions
        instructions = []
        for platform, url in platforms.items():
            instructions.append({
                'platform': platform,
                'url': url,
                'steps': [
                    f'1. Visit {url}',
                    '2. Download profile picture',
                    '3. Save as {platform}_profile.jpg',
                    '4. Compare visually or use reverse image search'
                ]
            })
        
        return {
            'success': True,
            'platforms_checked': list(platforms.keys()),
            'verification_steps': instructions,
            'red_flags_to_check': [
                'Different faces across platforms',
                'Same stock photo on multiple platforms',
                'One platform has professional photo, others don\'t',
                'Inconsistent age/appearance across platforms',
                'One profile much older than others'
            ],
            'automated_note': 'Manual verification required - profile images often protected',
            'tools': {
                'image_comparison': 'Use reverse_image_search_file() for each downloaded image',
                'visual_comparison': 'Place images side-by-side and check for differences'
            }
        }
        
    except Exception as e:
        logger.error(f"[PROFILE_CONSISTENCY] Error: {e}")
        return {'success': False, 'error': str(e)}


def search_profile_image_online(
    person_name: str,
    company_name: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Generate search queries to find profile images online (FREE).
    
    Args:
        person_name: Full name of person
        company_name: Company/organization name
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Search URLs and strategies
    """
    logger.info(f"[PROFILE_SEARCH] Searching for {person_name} at {company_name}")
    
    try:
        # Generate search queries
        queries = [
            f'"{person_name}" {company_name}',
            f'"{person_name}" {company_name} profile',
            f'"{person_name}" {company_name} photo',
            f'"{person_name}" {company_name} headshot',
            f'"{person_name}" {company_name} linkedin',
            f'"{person_name}" CEO {company_name}',
            f'"{person_name}" founder {company_name}'
        ]
        
        # Generate Google Image search URLs
        search_urls = {}
        for i, query in enumerate(queries):
            search_urls[f'search_{i+1}'] = f"https://www.google.com/search?q={quote(query)}&tbm=isch"
        
        return {
            'success': True,
            'person_name': person_name,
            'company_name': company_name,
            'search_queries': queries,
            'image_search_urls': search_urls,
            'instructions': [
                '1. Open each search URL',
                '2. Look for profile pictures',
                '3. Right-click and "Search image with Google"',
                '4. Check where else the image appears',
                '5. Note any stock photo sources'
            ],
            'red_flags': [
                'Image appears on stock photo websites',
                'Same image used for multiple different people',
                'Image only appears on suspicious websites',
                'No images found at all',
                'Images don\'t match claimed identity'
            ]
        }
        
    except Exception as e:
        logger.error(f"[PROFILE_SEARCH] Error: {e}")
        return {'success': False, 'error': str(e)}


def check_facial_recognition_databases(
    image_url: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Generate URLs for facial recognition database searches (PAID services).
    
    Args:
        image_url: URL to profile image
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Links to facial recognition services
    """
    logger.info(f"[FACIAL_RECOGNITION] Checking databases for: {image_url}")
    
    try:
        services = {
            'pimeyes': {
                'url': 'https://pimeyes.com',
                'cost': 'Paid ($29.99-$89.99/month)',
                'features': [
                    'Searches across internet for matching faces',
                    'Social media profile detection',
                    'Website appearance tracking',
                    'Dark web monitoring'
                ],
                'instructions': [
                    '1. Go to pimeyes.com',
                    '2. Upload profile image',
                    '3. Review all matches',
                    '4. Check if face appears on multiple identities'
                ]
            },
            'facecheck_id': {
                'url': 'https://facecheck.id',
                'cost': 'Paid ($9.99/search or subscription)',
                'features': [
                    'Reverse face search',
                    'Social media matching',
                    'Dating profile detection',
                    'Criminal database check'
                ],
                'instructions': [
                    '1. Go to facecheck.id',
                    '2. Upload image',
                    '3. Purchase credits if needed',
                    '4. Review match results'
                ]
            },
            'social_catfish': {
                'url': 'https://socialcatfish.com',
                'cost': 'Paid ($5.73-$28.59/month)',
                'features': [
                    'Reverse image search',
                    'Social media profiles',
                    'Dating site profiles',
                    'Identity verification'
                ],
                'instructions': [
                    '1. Go to socialcatfish.com',
                    '2. Select reverse image search',
                    '3. Upload image',
                    '4. Review findings'
                ]
            }
        }
        
        return {
            'success': True,
            'image_url': image_url,
            'note': 'These services require payment for full results',
            'services': services,
            'free_alternative': 'Use reverse_image_search_urls() for free searches first',
            'recommendation': 'Only use paid services if free searches are inconclusive and stakes are high'
        }
        
    except Exception as e:
        logger.error(f"[FACIAL_RECOGNITION] Error: {e}")
        return {'success': False, 'error': str(e)}


def analyze_profile_image_quality(
    image_url: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Analyze profile image for quality and authenticity indicators (FREE).
    
    Args:
        image_url: URL to profile image
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Quality analysis and red flags
    """
    logger.info(f"[IMAGE_QUALITY] Analyzing: {image_url}")
    
    try:
        from PIL import Image
        from io import BytesIO
        
        # Download image with better headers
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(image_url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        # Open with PIL
        image = Image.open(BytesIO(response.content))
        width, height = image.size
        
        # Quality indicators
        is_square = abs(width - height) < 10
        is_high_res = width >= 400 and height >= 400
        is_low_res = width < 200 or height < 200
        aspect_ratio = width / height if height > 0 else 0
        
        # Detect potential issues
        red_flags = []
        if is_low_res:
            red_flags.append('Low resolution - may indicate screenshot or download')
        if not is_square and not (0.8 < aspect_ratio < 1.2):
            red_flags.append('Unusual aspect ratio for profile picture')
        if width > 2000 or height > 2000:
            red_flags.append('Unusually high resolution - may be professional headshot')
        
        quality_score = 0
        if is_high_res: quality_score += 30
        if is_square: quality_score += 20
        if image.format in ['JPEG', 'PNG']: quality_score += 20
        if len(response.content) > 100000: quality_score += 30
        
        return {
            'success': True,
            'image_url': image_url,
            'dimensions': {'width': width, 'height': height},
            'aspect_ratio': round(aspect_ratio, 2),
            'is_square': is_square,
            'resolution_category': 'high' if is_high_res else ('low' if is_low_res else 'medium'),
            'file_format': image.format,
            'file_size_bytes': len(response.content),
            'quality_score': quality_score,
            'red_flags': red_flags,
            'authenticity_indicators': {
                'professional_headshot': width >= 800 and is_square,
                'social_media_standard': 200 <= width <= 800 and is_square,
                'screenshot': is_low_res or aspect_ratio > 1.5,
                'ai_generated': is_square and is_high_res and len(response.content) < 50000
            }
        }
        
    except ImportError:
        return {
            'success': False,
            'error': 'PIL (Pillow) library required',
            'install_command': 'pip install Pillow'
        }
    except Exception as e:
        logger.error(f"[IMAGE_QUALITY] Error: {e}")
        return {'success': False, 'error': str(e)}

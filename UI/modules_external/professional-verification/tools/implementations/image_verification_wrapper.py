"""
Image Verification Wrapper
===========================

Maps Registry V3 tool calls to image verification implementations.
"""

from tools.registry_v3 import tool_executor


@tool_executor()
def reverse_image_search_urls(image_url: str):
    """Generate reverse image search URLs for Google, TinEye, Yandex, Bing."""
    from image_verification_core import reverse_image_search_urls as impl
    return impl(image_url)


@tool_executor()
def reverse_image_search_file(image_path: str):
    """Generate reverse image search instructions for local image file."""
    from image_verification_core import reverse_image_search_file as impl
    return impl(image_path)


@tool_executor()
def detect_ai_generated_face(image_url: str):
    """Analyze image for AI-generated face indicators."""
    from image_verification_core import detect_ai_generated_face as impl
    return impl(image_url)


@tool_executor()
def extract_image_metadata(image_url: str):
    """Extract EXIF metadata from image (camera, date, GPS)."""
    from image_verification_core import extract_image_metadata as impl
    return impl(image_url)


@tool_executor()
def verify_profile_image_consistency(linkedin_url: str, facebook_url: str, twitter_url: str = None):
    """Check if profile images are consistent across social platforms."""
    from image_verification_core import verify_profile_image_consistency as impl
    return impl(linkedin_url, facebook_url, twitter_url)


@tool_executor()
def search_profile_image_online(person_name: str, company_name: str):
    """Generate search queries to find profile images online."""
    from image_verification_core import search_profile_image_online as impl
    return impl(person_name, company_name)


@tool_executor()
def check_facial_recognition_databases(image_url: str):
    """Get info about paid facial recognition services (PimEyes, FaceCheck.ID)."""
    from image_verification_core import check_facial_recognition_databases as impl
    return impl(image_url)


@tool_executor()
def analyze_profile_image_quality(image_url: str):
    """Analyze profile image quality and authenticity indicators."""
    from image_verification_core import analyze_profile_image_quality as impl
    return impl(image_url)

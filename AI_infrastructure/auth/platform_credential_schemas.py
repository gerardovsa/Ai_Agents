"""
FILE: AI_infrastructure/auth/platform_credential_schemas.py
PURPOSE: Platform-specific credential schemas and validation for flexible credential storage

DEPENDENCIES:
- pydantic ^2.0.0 (schema validation)
- typing (type hints)

EXPORTS:
- PlatformCredentialSchema (base schema class)
- PLATFORM_SCHEMAS (registry of all platform schemas)
- validate_platform_credentials(platform, credentials) - Validate credentials against schema
- get_required_fields(platform) - Get required credential fields for platform
- get_optional_fields(platform) - Get optional credential/settings fields

USED BY:
- AI_infrastructure/auth/user_auth.py (credential storage/retrieval)
- AI_infrastructure/routes/account_linking_routes.py (OAuth credential storage)

NOTES:
- Each platform has a Pydantic schema defining required/optional fields
- Credentials stored in JSONB format in user_platform_credentials.credentials column
- Settings stored in JSONB format in user_platform_credentials.settings column
- Validation ensures correct structure before storage
- Easy to add new platforms by extending PLATFORM_SCHEMAS

LAST MODIFIED: 2025-11-25 - Initial implementation for flexible credential system
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


# ============================================================================
# BASE CREDENTIAL SCHEMA
# ============================================================================

class PlatformCredentialSchema(BaseModel):
    """Base schema for platform credentials"""
    class Config:
        extra = "allow"  # Allow additional fields not in schema
        json_schema_extra = {
            "description": "Platform-specific credential configuration"
        }


# ============================================================================
# VECTOR DATABASE CREDENTIALS
# ============================================================================

class PineconeCredentials(PlatformCredentialSchema):
    """Pinecone vector database credentials"""
    api_key: str = Field(..., description="Pinecone API key")
    environment: str = Field(default="us-east-1", description="Pinecone environment/region")
    index_name: str = Field(..., description="Pinecone index name")
    namespace: Optional[str] = Field(default=None, description="Namespace for data isolation")
    
    # Optional settings
    dimension: Optional[int] = Field(default=1536, description="Vector dimension (default: OpenAI embeddings)")
    metric: Optional[str] = Field(default="cosine", description="Distance metric: cosine, euclidean, dotproduct")
    pod_type: Optional[str] = Field(default="p1.x1", description="Pod type for performance")


class VoyagerCredentials(PlatformCredentialSchema):
    """Voyager vector database credentials"""
    api_key: str = Field(..., description="Voyager API key")
    collection_name: str = Field(..., description="Collection name")
    endpoint: Optional[str] = Field(default="https://api.voyager.ai", description="API endpoint URL")
    
    # Optional settings
    dimension: Optional[int] = Field(default=1536, description="Vector dimension")
    distance_metric: Optional[str] = Field(default="cosine", description="Distance metric")


class OpenAIEmbeddingsCredentials(PlatformCredentialSchema):
    """OpenAI embeddings credentials (for vector DB usage)"""
    api_key: str = Field(..., description="OpenAI API key")
    model: Optional[str] = Field(default="text-embedding-ada-002", description="Embedding model")
    organization_id: Optional[str] = Field(default=None, description="OpenAI organization ID")


# ============================================================================
# COMMUNICATION PLATFORMS
# ============================================================================

class TwilioCredentials(PlatformCredentialSchema):
    """Twilio phone/SMS credentials"""
    account_sid: str = Field(..., description="Twilio Account SID (ACxxxxxxxxxxxxx)")
    auth_token: str = Field(..., description="Twilio Auth Token")
    phone_number: str = Field(..., description="Twilio phone number (E.164 format: +15555551234)")
    
    # Optional settings
    messaging_service_sid: Optional[str] = Field(default=None, description="Messaging Service SID (for SMS)")
    emergency_phone: Optional[str] = Field(default=None, description="Emergency routing number")
    business_hours_start: Optional[int] = Field(default=8, description="Business hours start (24h format)")
    business_hours_end: Optional[int] = Field(default=18, description="Business hours end (24h format)")
    webhook_base_url: Optional[str] = Field(default=None, description="Base URL for webhooks")


class SendGridCredentials(PlatformCredentialSchema):
    """SendGrid email credentials"""
    api_key: str = Field(..., description="SendGrid API key (SG.xxxxxxxxxxxxx)")
    from_email: Optional[str] = Field(default=None, description="Default sender email")
    from_name: Optional[str] = Field(default=None, description="Default sender name")
    
    # Optional settings
    template_ids: Optional[Dict[str, str]] = Field(default=None, description="Template IDs by name")
    click_tracking: Optional[bool] = Field(default=True, description="Enable click tracking")
    open_tracking: Optional[bool] = Field(default=True, description="Enable open tracking")


# ============================================================================
# TRANSCRIPTION / AI SERVICES
# ============================================================================

class AssemblyAICredentials(PlatformCredentialSchema):
    """AssemblyAI speech-to-text credentials"""
    api_key: str = Field(..., description="AssemblyAI API key")
    
    # Optional settings
    language_code: Optional[str] = Field(default="en", description="Default language code")
    speaker_labels: Optional[bool] = Field(default=True, description="Enable speaker diarization")
    punctuate: Optional[bool] = Field(default=True, description="Enable auto-punctuation")
    format_text: Optional[bool] = Field(default=True, description="Enable text formatting")
    word_boost: Optional[List[str]] = Field(
        default=None,
        description="Medical/domain-specific vocabulary to boost (e.g., ['parvo', 'heartworm'])"
    )
    webhook_url: Optional[str] = Field(default=None, description="Webhook URL for async transcriptions")


class OpenAICredentials(PlatformCredentialSchema):
    """OpenAI GPT/embeddings credentials"""
    api_key: str = Field(..., description="OpenAI API key (sk-xxxxxxxxxxxxx)")
    organization_id: Optional[str] = Field(default=None, description="Organization ID")
    
    # Optional settings
    default_model: Optional[str] = Field(default="gpt-4", description="Default GPT model")
    embedding_model: Optional[str] = Field(default="text-embedding-ada-002", description="Default embedding model")
    temperature: Optional[float] = Field(default=0.7, description="Default temperature (0-2)")
    max_tokens: Optional[int] = Field(default=1500, description="Default max tokens")
    timeout: Optional[int] = Field(default=60, description="Request timeout (seconds)")


class AnthropicCredentials(PlatformCredentialSchema):
    """Anthropic Claude credentials"""
    api_key: str = Field(..., description="Anthropic API key (sk-ant-xxxxxxxxxxxxx)")
    
    # Optional settings
    default_model: Optional[str] = Field(default="claude-3-sonnet-20240229", description="Default Claude model")
    max_tokens: Optional[int] = Field(default=4096, description="Default max tokens")
    temperature: Optional[float] = Field(default=1.0, description="Default temperature (0-1)")


class DeepSeekCredentials(PlatformCredentialSchema):
    """DeepSeek AI credentials"""
    api_key: str = Field(..., description="DeepSeek API key")
    
    # Optional settings
    default_model: Optional[str] = Field(default="deepseek-chat", description="Default model")
    base_url: Optional[str] = Field(default="https://api.deepseek.com", description="API base URL")


# ============================================================================
# PAYMENT / E-COMMERCE
# ============================================================================

class StripeCredentials(PlatformCredentialSchema):
    """Stripe payment credentials"""
    secret_key: str = Field(..., description="Stripe secret key (sk_live_xxxxxxxxxxxxx)")
    publishable_key: str = Field(..., description="Stripe publishable key (pk_live_xxxxxxxxxxxxx)")
    webhook_secret: str = Field(..., description="Webhook signing secret (whsec_xxxxxxxxxxxxx)")
    
    # Optional settings
    test_mode: Optional[bool] = Field(default=False, description="Use test keys instead of live")
    api_version: Optional[str] = Field(default="2023-10-16", description="Stripe API version")
    connect_account_id: Optional[str] = Field(default=None, description="Connected account ID (for platforms)")


class WooCommerceCredentials(PlatformCredentialSchema):
    """WooCommerce REST API credentials"""
    consumer_key: str = Field(..., description="WooCommerce consumer key (ck_xxxxxxxxxxxxx)")
    consumer_secret: str = Field(..., description="WooCommerce consumer secret (cs_xxxxxxxxxxxxx)")
    store_url: str = Field(..., description="WooCommerce store URL (https://example.com)")
    
    # Optional settings
    wp_api: Optional[bool] = Field(default=True, description="Use WP REST API")
    version: Optional[str] = Field(default="wc/v3", description="API version")
    timeout: Optional[int] = Field(default=30, description="Request timeout (seconds)")


class ShopifyCredentials(PlatformCredentialSchema):
    """Shopify API credentials"""
    api_key: str = Field(..., description="Shopify API key")
    api_secret: str = Field(..., description="Shopify API secret")
    shop_domain: str = Field(..., description="Shop domain (myshop.myshopify.com)")
    access_token: Optional[str] = Field(default=None, description="Admin API access token")
    
    # Optional settings
    api_version: Optional[str] = Field(default="2024-01", description="API version")
    scopes: Optional[List[str]] = Field(default=None, description="OAuth scopes")


# ============================================================================
# GOOGLE WORKSPACE
# ============================================================================

class GoogleOAuthCredentials(PlatformCredentialSchema):
    """Google OAuth 2.0 credentials (Gmail, Drive, Calendar, etc.)"""
    access_token: str = Field(..., description="OAuth access token")
    refresh_token: str = Field(..., description="OAuth refresh token")
    token_uri: str = Field(default="https://oauth2.googleapis.com/token", description="Token refresh endpoint")
    client_id: Optional[str] = Field(default=None, description="OAuth client ID")
    client_secret: Optional[str] = Field(default=None, description="OAuth client secret")
    
    # Token metadata
    expires_at: Optional[datetime] = Field(default=None, description="Token expiration timestamp")
    scopes: Optional[List[str]] = Field(default=None, description="Granted OAuth scopes")
    
    # Account info
    email: Optional[str] = Field(default=None, description="Google account email")
    account_name: Optional[str] = Field(default=None, description="Account display name")
    is_primary_account: Optional[bool] = Field(default=False, description="Is this the primary Google account?")


# ============================================================================
# MICROSOFT 365
# ============================================================================

class MicrosoftOAuthCredentials(PlatformCredentialSchema):
    """Microsoft Graph API OAuth credentials (Outlook, OneDrive, Teams, etc.)"""
    access_token: str = Field(..., description="OAuth access token")
    refresh_token: Optional[str] = Field(default=None, description="OAuth refresh token")
    token_uri: str = Field(default="https://login.microsoftonline.com/common/oauth2/v2.0/token", description="Token refresh endpoint")
    
    # Token metadata
    expires_at: Optional[datetime] = Field(default=None, description="Token expiration timestamp")
    scopes: Optional[List[str]] = Field(default=None, description="Granted OAuth scopes")
    
    # Account info
    email: Optional[str] = Field(default=None, description="Microsoft account email")
    account_name: Optional[str] = Field(default=None, description="Account display name")
    tenant_id: Optional[str] = Field(default=None, description="Azure AD tenant ID")


# ============================================================================
# ACCOUNTING / BUSINESS
# ============================================================================

class XeroCredentials(PlatformCredentialSchema):
    """Xero accounting API credentials"""
    client_id: str = Field(..., description="Xero OAuth client ID")
    client_secret: str = Field(..., description="Xero OAuth client secret")
    tenant_id: str = Field(..., description="Xero tenant ID (organization)")
    access_token: Optional[str] = Field(default=None, description="OAuth access token")
    refresh_token: Optional[str] = Field(default=None, description="OAuth refresh token")
    
    # Optional settings
    expires_at: Optional[datetime] = Field(default=None, description="Token expiration")
    scopes: Optional[List[str]] = Field(default=None, description="OAuth scopes")


# ============================================================================
# KNOWLEDGE COMMERCE / E-LEARNING
# ============================================================================

class KajabiCredentials(PlatformCredentialSchema):
    """Kajabi Knowledge Commerce Platform API credentials"""
    api_key: str = Field(..., description="Kajabi API key (Bearer token)")
    
    # Optional settings
    site_id: Optional[str] = Field(default=None, description="Kajabi site ID")
    site_url: Optional[str] = Field(default=None, description="Custom domain URL")
    webhook_secret: Optional[str] = Field(default=None, description="Webhook signature secret")


# ============================================================================
# PLATFORM REGISTRY
# ============================================================================

PLATFORM_SCHEMAS: Dict[str, type[PlatformCredentialSchema]] = {
    # Vector Databases
    "pinecone": PineconeCredentials,
    "voyager": VoyagerCredentials,
    "openai_embeddings": OpenAIEmbeddingsCredentials,
    
    # Communication
    "twilio": TwilioCredentials,
    "sendgrid": SendGridCredentials,
    
    # Transcription / AI
    "assemblyai": AssemblyAICredentials,
    "openai": OpenAICredentials,
    "anthropic": AnthropicCredentials,
    "deepseek": DeepSeekCredentials,
    
    # Payment / E-commerce
    "stripe": StripeCredentials,
    "woocommerce": WooCommerceCredentials,
    "shopify": ShopifyCredentials,
    
    # Google Workspace
    "google": GoogleOAuthCredentials,
    "gmail": GoogleOAuthCredentials,
    "google_drive": GoogleOAuthCredentials,
    "google_calendar": GoogleOAuthCredentials,
    
    # Microsoft 365
    "microsoft": MicrosoftOAuthCredentials,
    "outlook": MicrosoftOAuthCredentials,
    "onedrive": MicrosoftOAuthCredentials,
    "teams": MicrosoftOAuthCredentials,
    
    # Accounting
    "xero": XeroCredentials,
    
    # Knowledge Commerce / E-Learning
    "kajabi": KajabiCredentials,
}


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_platform_credentials(platform: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate credentials against platform schema
    
    Args:
        platform: Platform name (e.g., 'pinecone', 'twilio')
        credentials: Credentials dictionary
    
    Returns:
        Validated credentials dictionary
    
    Raises:
        ValueError: If platform not found or validation fails
    """
    if platform not in PLATFORM_SCHEMAS:
        raise ValueError(f"Unknown platform: {platform}. Available platforms: {list(PLATFORM_SCHEMAS.keys())}")
    
    schema_class = PLATFORM_SCHEMAS[platform]
    
    try:
        validated = schema_class(**credentials)
        return validated.model_dump(exclude_none=True)
    except Exception as e:
        raise ValueError(f"Credential validation failed for {platform}: {str(e)}")


def get_required_fields(platform: str) -> List[str]:
    """
    Get required credential fields for platform
    
    Args:
        platform: Platform name
    
    Returns:
        List of required field names
    """
    if platform not in PLATFORM_SCHEMAS:
        return []
    
    schema_class = PLATFORM_SCHEMAS[platform]
    required = []
    
    for field_name, field_info in schema_class.model_fields.items():
        if field_info.is_required():
            required.append(field_name)
    
    return required


def get_optional_fields(platform: str) -> List[str]:
    """
    Get optional credential/settings fields for platform
    
    Args:
        platform: Platform name
    
    Returns:
        List of optional field names
    """
    if platform not in PLATFORM_SCHEMAS:
        return []
    
    schema_class = PLATFORM_SCHEMAS[platform]
    optional = []
    
    for field_name, field_info in schema_class.model_fields.items():
        if not field_info.is_required():
            optional.append(field_name)
    
    return optional


def get_platform_schema_info(platform: str) -> Dict[str, Any]:
    """
    Get comprehensive schema information for platform
    
    Args:
        platform: Platform name
    
    Returns:
        Dictionary with schema details
    """
    if platform not in PLATFORM_SCHEMAS:
        return {"error": f"Unknown platform: {platform}"}
    
    schema_class = PLATFORM_SCHEMAS[platform]
    
    fields_info = {}
    for field_name, field_info in schema_class.model_fields.items():
        fields_info[field_name] = {
            "type": str(field_info.annotation),
            "required": field_info.is_required(),
            "default": field_info.default if field_info.default is not None else None,
            "description": field_info.description
        }
    
    return {
        "platform": platform,
        "schema_class": schema_class.__name__,
        "description": schema_class.__doc__,
        "fields": fields_info,
        "required_fields": get_required_fields(platform),
        "optional_fields": get_optional_fields(platform)
    }


def list_all_platforms() -> List[Dict[str, Any]]:
    """
    List all available platforms with basic info
    
    Returns:
        List of platform dictionaries
    """
    platforms = []
    
    for platform_name, schema_class in PLATFORM_SCHEMAS.items():
        platforms.append({
            "name": platform_name,
            "schema_class": schema_class.__name__,
            "description": schema_class.__doc__,
            "required_fields": get_required_fields(platform_name),
            "optional_fields_count": len(get_optional_fields(platform_name))
        })
    
    return platforms

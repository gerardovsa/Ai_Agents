"""
Australia Post PAC API Client
==============================

Python client for Australia Post Postage Assessment Calculator (PAC) API.

API Documentation: https://developers.auspost.com.au/apis/pac
Register for API key: https://developers.auspost.com.au/apis/pacpcs-registration

Features:
- Domestic parcel postage calculation
- International parcel postage calculation
- Service options lookup
- Auto-detection of domestic vs international

FILE: UI/modules_external/auspost-shipping/backend/auspost_client.py
"""

import os
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AusPostClient:
    """Client for Australia Post PAC API."""
    
    # API endpoints
    PROD_BASE_URL = "https://digitalapi.auspost.com.au"
    TEST_BASE_URL = "https://test.npe.auspost.com.au"
    TEST_API_KEY = "28744ed5982391881611cca6cf5c240"  # Public test key from docs
    
    # Service codes
    DOMESTIC_SERVICES = {
        'AUS_PARCEL_REGULAR': 'Parcel Post (Standard)',
        'AUS_PARCEL_EXPRESS': 'Express Post',
        'AUS_PARCEL_REGULAR_SATCHEL_3KG': 'Parcel Post Medium Satchel',
        'AUS_PARCEL_EXPRESS_SATCHEL_3KG': 'Express Post Medium Satchel',
        'AUS_PARCEL_REGULAR_SATCHEL_500G': 'Parcel Post Small Satchel',
        'AUS_PARCEL_EXPRESS_SATCHEL_500G': 'Express Post Small Satchel'
    }
    
    def __init__(self, api_key: Optional[str] = None, use_test_env: bool = False):
        """
        Initialize Australia Post API client.
        
        Args:
            api_key: Australia Post API key. If None, reads from AUSPOST_API_KEY env var.
            use_test_env: If True, uses test environment with public test key.
        """
        if use_test_env:
            self.api_key = self.TEST_API_KEY
            self.base_url = self.TEST_BASE_URL
            self.is_test = True
        else:
            self.api_key = api_key or os.getenv('AUSPOST_API_KEY')
            self.base_url = self.PROD_BASE_URL
            self.is_test = False
        
        if not self.api_key:
            raise ValueError(
                "Australia Post API key required. Set AUSPOST_API_KEY environment variable "
                "or pass api_key parameter. Register at: "
                "https://developers.auspost.com.au/apis/pacpcs-registration"
            )
        
        self.session = requests.Session()
        self.session.headers.update({
            'AUTH-KEY': self.api_key,
            'User-Agent': 'InHousePrint-ShippingCalculator/1.0'
        })
    
    def get_domestic_services(
        self,
        from_postcode: str,
        to_postcode: str,
        length_cm: float,
        width_cm: float,
        height_cm: float,
        weight_kg: float
    ) -> Dict[str, Any]:
        """
        Get available domestic shipping services and prices.
        
        Args:
            from_postcode: Origin Australian postcode
            to_postcode: Destination Australian postcode
            length_cm: Package length in cm
            width_cm: Package width in cm
            height_cm: Package height in cm
            weight_kg: Package weight in kg
            
        Returns:
            Dict with 'services' array containing available options
        """
        url = f"{self.base_url}/postage/parcel/domestic/service.json"
        
        params = {
            'from_postcode': from_postcode,
            'to_postcode': to_postcode,
            'length': length_cm,
            'width': width_cm,
            'height': height_cm,
            'weight': weight_kg
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'message': 'Failed to retrieve domestic services'
            }
    
    def calculate_domestic_postage(
        self,
        from_postcode: str,
        to_postcode: str,
        length_cm: float,
        width_cm: float,
        height_cm: float,
        weight_kg: float,
        service_code: str = 'AUS_PARCEL_REGULAR'
    ) -> Dict[str, Any]:
        """
        Calculate domestic postage cost for specific service.
        
        Args:
            from_postcode: Origin Australian postcode
            to_postcode: Destination Australian postcode
            length_cm: Package length in cm
            width_cm: Package width in cm
            height_cm: Package height in cm
            weight_kg: Package weight in kg
            service_code: Service code (default: AUS_PARCEL_REGULAR)
            
        Returns:
            Dict with 'postage_result' containing cost and delivery time
        """
        url = f"{self.base_url}/postage/parcel/domestic/calculate.json"
        
        params = {
            'from_postcode': from_postcode,
            'to_postcode': to_postcode,
            'length': length_cm,
            'width': width_cm,
            'height': height_cm,
            'weight': weight_kg,
            'service_code': service_code
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'message': f'Failed to calculate postage for service {service_code}'
            }
    
    def get_international_services(
        self,
        country_code: str,
        weight_kg: float
    ) -> Dict[str, Any]:
        """
        Get available international shipping services and prices.
        
        Args:
            country_code: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB', 'NZ')
            weight_kg: Package weight in kg
            
        Returns:
            Dict with 'services' array containing available options
        """
        url = f"{self.base_url}/postage/parcel/international/service.json"
        
        params = {
            'country_code': country_code,
            'weight': weight_kg
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'message': 'Failed to retrieve international services'
            }
    
    def calculate_international_postage(
        self,
        country_code: str,
        weight_kg: float,
        service_code: str = 'INT_PARCEL_STD_OWN_PACKAGING'
    ) -> Dict[str, Any]:
        """
        Calculate international postage cost for specific service.
        
        Args:
            country_code: ISO 3166-1 alpha-2 country code
            weight_kg: Package weight in kg
            service_code: Service code (default: standard international parcel)
            
        Returns:
            Dict with 'postage_result' containing cost and delivery time
        """
        url = f"{self.base_url}/postage/parcel/international/calculate.json"
        
        params = {
            'country_code': country_code,
            'weight': weight_kg,
            'service_code': service_code
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'message': f'Failed to calculate international postage for service {service_code}'
            }
    
    def get_country_list(self) -> Dict[str, Any]:
        """
        Get list of supported countries for international shipping.
        
        Returns:
            Dict with 'countries' array
        """
        url = f"{self.base_url}/postage/country.json"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'message': 'Failed to retrieve country list'
            }
    
    @staticmethod
    def get_service_descriptions() -> Dict[str, str]:
        """Get human-readable descriptions of service codes."""
        return AusPostClient.DOMESTIC_SERVICES.copy()
    
    @staticmethod
    def country_name_to_code(country_name: str) -> Optional[str]:
        """
        Convert country name to ISO code (basic mapping).
        
        Args:
            country_name: Country name (e.g., 'United States', 'New Zealand')
            
        Returns:
            ISO country code or None if not found
        """
        # Common country mappings
        country_map = {
            'united states': 'US',
            'usa': 'US',
            'united kingdom': 'GB',
            'uk': 'GB',
            'new zealand': 'NZ',
            'canada': 'CA',
            'australia': 'AU',
            'japan': 'JP',
            'china': 'CN',
            'singapore': 'SG',
            'india': 'IN',
            'germany': 'DE',
            'france': 'FR',
            'italy': 'IT',
            'spain': 'ES',
            'netherlands': 'NL',
            'belgium': 'BE',
            'switzerland': 'CH',
            'austria': 'AT',
            'sweden': 'SE',
            'norway': 'NO',
            'denmark': 'DK',
            'finland': 'FI',
            'ireland': 'IE',
            'south korea': 'KR',
            'hong kong': 'HK',
            'taiwan': 'TW',
            'thailand': 'TH',
            'malaysia': 'MY',
            'indonesia': 'ID',
            'philippines': 'PH',
            'vietnam': 'VN',
            'brazil': 'BR',
            'mexico': 'MX',
            'argentina': 'AR',
            'chile': 'CL',
            'south africa': 'ZA',
            'israel': 'IL',
            'turkey': 'TR',
            'russia': 'RU',
            'poland': 'PL',
            'czech republic': 'CZ',
            'greece': 'GR',
            'portugal': 'PT',
            'romania': 'RO',
            'hungary': 'HU'
        }
        
        return country_map.get(country_name.lower().strip())

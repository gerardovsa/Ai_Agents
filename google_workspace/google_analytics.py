"""
Google Analytics API Tool Implementations
===========================================

Implements Google Analytics 4 (GA4) operations for tracking, reports, and metrics.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google_workspace.google_auth_helper import build_analytics_service, get_service_account_credentials
    HAS_ANALYTICS_API = True
except ImportError:
    HAS_ANALYTICS_API = False
    print("⚠️ Google Analytics API dependencies not available")


def _get_analytics_service():
    """Get authenticated Google Analytics Data API service (for reports)"""
    if not HAS_ANALYTICS_API:
        raise Exception("Google Analytics API not available - install google-api-python-client")
    
    # Use the unified Google Workspace authentication helper
    return build_analytics_service()


def _get_analytics_admin_service():
    """Get authenticated Google Analytics Admin API service (for accounts/properties)"""
    if not HAS_ANALYTICS_API:
        raise Exception("Google Analytics API not available - install google-api-python-client")
    
    scopes = ['https://www.googleapis.com/auth/analytics.readonly']
    credentials = get_service_account_credentials(scopes)
    return build('analyticsadmin', 'v1beta', credentials=credentials)


# ==================== ACCOUNT & PROPERTY ====================

def google_analytics_list_accounts(**kwargs):
    """List all Analytics accounts"""
    try:
        service = _get_analytics_admin_service()
        
        accounts = service.accountSummaries().list().execute()
        
        account_summaries = accounts.get('accountSummaries', [])
        
        return {
            'accounts': account_summaries,
            'count': len(account_summaries)
        }
    
    except Exception as e:
        print(f" Failed to list accounts: {e}")
        raise


def google_analytics_list_properties(account_id=None, **kwargs):
    """List Analytics properties"""
    try:
        service = _get_analytics_admin_service()
        
        if account_id:
            parent = f'accounts/{account_id}'
            properties = service.properties().list(filter=f'parent:{parent}').execute()
        else:
            properties = service.properties().list().execute()
        
        property_list = properties.get('properties', [])
        
        return {
            'properties': property_list,
            'count': len(property_list)
        }
    
    except Exception as e:
        print(f" Failed to list properties: {e}")
        raise


# ==================== REPORTS ====================

def google_analytics_get_realtime_report(property_id, metrics=None, dimensions=None, **kwargs):
    """Get realtime analytics report"""
    try:
        service = _get_analytics_service()
        
        # Default metrics if not provided
        if not metrics:
            metrics = [{'name': 'activeUsers'}]
        
        if not dimensions:
            dimensions = [{'name': 'country'}]
        
        request_body = {
            'metrics': metrics,
            'dimensions': dimensions
        }
        
        response = service.properties().runRealtimeReport(
            property=f'properties/{property_id}',
            body=request_body
        ).execute()
        
        return response
    
    except Exception as e:
        print(f" Failed to get realtime report: {e}")
        raise


def google_analytics_run_report(property_id, start_date, end_date, metrics, dimensions=None, 
                                dimension_filter=None, metric_filter=None, limit=10, **kwargs):
    """Run a custom analytics report"""
    try:
        service = _get_analytics_service()
        
        request_body = {
            'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
            'metrics': metrics,
            'limit': limit
        }
        
        if dimensions:
            request_body['dimensions'] = dimensions
        if dimension_filter:
            request_body['dimensionFilter'] = dimension_filter
        if metric_filter:
            request_body['metricFilter'] = metric_filter
        
        response = service.properties().runReport(
            property=f'properties/{property_id}',
            body=request_body
        ).execute()
        
        return response
    
    except Exception as e:
        print(f" Failed to run report: {e}")
        raise


# ==================== SPECIFIC METRICS ====================

def google_analytics_get_page_views(property_id, start_date='7daysAgo', end_date='today', **kwargs):
    """Get page views for date range"""
    metrics = [
        {'name': 'screenPageViews'},
        {'name': 'sessions'}
    ]
    dimensions = [
        {'name': 'pagePath'},
        {'name': 'pageTitle'}
    ]
    
    return google_analytics_run_report(
        property_id, start_date, end_date, metrics, dimensions, limit=100
    )


def google_analytics_get_user_behavior(property_id, start_date='7daysAgo', end_date='today', **kwargs):
    """Get user behavior metrics"""
    metrics = [
        {'name': 'activeUsers'},
        {'name': 'newUsers'},
        {'name': 'sessions'},
        {'name': 'averageSessionDuration'},
        {'name': 'bounceRate'}
    ]
    dimensions = [
        {'name': 'date'}
    ]
    
    return google_analytics_run_report(
        property_id, start_date, end_date, metrics, dimensions, limit=30
    )


def google_analytics_get_conversions(property_id, start_date='7daysAgo', end_date='today', **kwargs):
    """Get conversion metrics"""
    metrics = [
        {'name': 'conversions'},
        {'name': 'totalRevenue'},
        {'name': 'eventCount'}
    ]
    dimensions = [
        {'name': 'eventName'}
    ]
    
    return google_analytics_run_report(
        property_id, start_date, end_date, metrics, dimensions, limit=50
    )


def google_analytics_get_traffic_sources(property_id, start_date='7daysAgo', end_date='today', **kwargs):
    """Get traffic source breakdown"""
    metrics = [
        {'name': 'sessions'},
        {'name': 'activeUsers'}
    ]
    dimensions = [
        {'name': 'sessionSource'},
        {'name': 'sessionMedium'},
        {'name': 'sessionCampaignName'}
    ]
    
    return google_analytics_run_report(
        property_id, start_date, end_date, metrics, dimensions, limit=100
    )


def google_analytics_get_demographics(property_id, start_date='7daysAgo', end_date='today', **kwargs):
    """Get demographic data"""
    metrics = [
        {'name': 'activeUsers'}
    ]
    dimensions = [
        {'name': 'country'},
        {'name': 'city'},
        {'name': 'language'}
    ]
    
    return google_analytics_run_report(
        property_id, start_date, end_date, metrics, dimensions, limit=100
    )


def google_analytics_get_device_data(property_id, start_date='7daysAgo', end_date='today', **kwargs):
    """Get device and browser data"""
    metrics = [
        {'name': 'activeUsers'},
        {'name': 'sessions'}
    ]
    dimensions = [
        {'name': 'deviceCategory'},
        {'name': 'operatingSystem'},
        {'name': 'browser'}
    ]
    
    return google_analytics_run_report(
        property_id, start_date, end_date, metrics, dimensions, limit=50
    )


def google_analytics_get_top_pages(property_id, start_date='7daysAgo', end_date='today', limit=20, **kwargs):
    """Get top performing pages"""
    metrics = [
        {'name': 'screenPageViews'},
        {'name': 'averageSessionDuration'},
        {'name': 'bounceRate'}
    ]
    dimensions = [
        {'name': 'pagePath'},
        {'name': 'pageTitle'}
    ]
    
    return google_analytics_run_report(
        property_id, start_date, end_date, metrics, dimensions, limit=limit
    )


def google_analytics_get_events(property_id, start_date='7daysAgo', end_date='today', **kwargs):
    """Get custom event data"""
    metrics = [
        {'name': 'eventCount'},
        {'name': 'eventCountPerUser'}
    ]
    dimensions = [
        {'name': 'eventName'},
        {'name': 'date'}
    ]
    
    return google_analytics_run_report(
        property_id, start_date, end_date, metrics, dimensions, limit=100
    )

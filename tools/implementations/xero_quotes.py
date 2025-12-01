"""
Xero Quotes and BrandingThemes (Templates) Tools - Integration with Xero Accounting API

Functions:
- xero_create_quote: Create new sales quote with branding theme
- xero_list_quotes: List quotes with filtering and pagination (70,000+ quotes)
- xero_get_quote_by_id: Get specific quote details
- xero_update_quote: Update existing quote
- xero_get_branding_themes: List available branding themes/templates

CRITICAL: Requires XeroAPIClient from UI/external/modules/xero/xero_routes.py
CRITICAL: Credentials injected via credential_injector.py (xero_ prefix detection)
"""

import traceback
from typing import Dict, Any, List, Optional
from datetime import date, datetime


def _get_client(business_id: int):
    """
    Get XeroAPIClient instance for specified business
    
    Args:
        business_id: 1=InHouse Print, 2=Publishing, 3=Signs
    
    Returns:
        XeroAPIClient instance
    
    Raises:
        RuntimeError: If XeroAPIClient not available
    """
    try:
        from UI.external.modules.xero.xero_routes import XeroAPIClient
        return XeroAPIClient(business_id=business_id)
    except ImportError as e:
        raise RuntimeError(f"XeroAPIClient not available. Ensure xero_routes.py is accessible: {str(e)}")


def xero_create_quote(
    business_id: int,
    contact_id: str,
    line_items: List[Dict[str, Any]],
    branding_theme_id: Optional[str] = None,
    template_name: Optional[str] = None,
    date: Optional[str] = None,
    expiry_date: Optional[str] = None,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    terms: Optional[str] = None,
    reference: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new sales quote in Xero with optional branding theme (template)
    
    Args:
        business_id: Business ID (1=InHouse Print, 2=Publishing, 3=Signs)
        contact_id: Xero contact ID (customer receiving quote)
        line_items: Array of line items with description, quantity, unit_amount, account_code
        branding_theme_id: BrandingThemeID for template/logo/styling (optional, use if you have GUID)
        template_name: Template name to auto-lookup (optional, use instead of branding_theme_id)
        date: Quote issue date YYYY-MM-DD (optional, defaults to today)
        expiry_date: Quote expiry date YYYY-MM-DD (optional)
        title: Quote title text max 100 chars (optional)
        summary: Quote summary text max 3000 chars (optional)
        terms: Terms and conditions text max 4000 chars (optional)
        reference: Additional reference number max 4000 chars (optional)
        **kwargs: Credential injection (unused, for compatibility)
    
    Returns:
        Dict with success status, created quote details (QuoteID, QuoteNumber, Status, etc.)
    
    Raises:
        RuntimeError: If XeroAPIClient is not available
        Exception: If quote creation fails
    
    Examples:
        # Using template name (easier)
        xero_create_quote(
            business_id=1,
            contact_id="a3675fc4-f8dd-4f03-ba5b-f1870566bcd7",
            line_items=[
                {
                    "description": "Business Cards - 1000qty, 350GSM",
                    "quantity": 1,
                    "unit_amount": 150.00,
                    "account_code": "200"
                }
            ],
            template_name="Standard Invoice",
            title="Printing Quote",
            expiry_date="2025-12-31"
        )
        
        # Using branding_theme_id (if you have the GUID)
        xero_create_quote(
            business_id=1,
            contact_id="a3675fc4-f8dd-4f03-ba5b-f1870566bcd7",
            line_items=[...],
            branding_theme_id="d5b89e36-8a28-4c40-b8e4-2a0d3f5d7c93"
        )
    """
    try:
        client = _get_client(business_id)
        
        # If template_name provided, look up the BrandingThemeID
        resolved_branding_theme_id = branding_theme_id
        if template_name and not branding_theme_id:
            try:
                themes_response = client.make_request('GET', 'BrandingThemes')
                themes = themes_response.get('BrandingThemes', [])
                
                # Look for exact match (case-insensitive)
                for theme in themes:
                    if theme.get('Name', '').lower() == template_name.lower():
                        resolved_branding_theme_id = theme.get('BrandingThemeID')
                        break
                
                # If no exact match, try partial match
                if not resolved_branding_theme_id:
                    for theme in themes:
                        if template_name.lower() in theme.get('Name', '').lower():
                            resolved_branding_theme_id = theme.get('BrandingThemeID')
                            break
            except Exception as e:
                # If template lookup fails, continue without it
                print(f"Warning: Could not lookup template '{template_name}': {e}")
        
        # Build quote payload
        quote_data = {
            "Contact": {
                "ContactID": contact_id
            },
            "LineItems": []
        }
        
        # Add line items
        for item in line_items:
            line_item = {
                "Description": item.get("description", ""),
                "Quantity": item.get("quantity", 1),
                "UnitAmount": item.get("unit_amount", 0)
            }
            
            # Add account code if provided
            if "account_code" in item:
                line_item["AccountCode"] = item["account_code"]
            
            quote_data["LineItems"].append(line_item)
        
        # Add optional fields
        if resolved_branding_theme_id:
            quote_data["BrandingThemeID"] = resolved_branding_theme_id
        
        if date:
            quote_data["Date"] = date
        
        if expiry_date:
            quote_data["ExpiryDate"] = expiry_date
        
        if title:
            quote_data["Title"] = title[:100]  # Max 100 chars
        
        if summary:
            quote_data["Summary"] = summary[:3000]  # Max 3000 chars
        
        if terms:
            quote_data["Terms"] = terms[:4000]  # Max 4000 chars
        
        if reference:
            quote_data["Reference"] = reference[:4000]  # Max 4000 chars
        
        # Make API request to create quote
        response = client.make_request('PUT', 'Quotes', json={"Quotes": [quote_data]})
        
        if response and 'Quotes' in response and len(response['Quotes']) > 0:
            created_quote = response['Quotes'][0]
            return {
                "success": True,
                "business_id": business_id,
                "business_name": client.config['name'],
                "quote": {
                    "quote_id": created_quote.get("QuoteID"),
                    "quote_number": created_quote.get("QuoteNumber"),
                    "status": created_quote.get("Status"),
                    "contact": created_quote.get("Contact", {}),
                    "line_items": created_quote.get("LineItems", []),
                    "sub_total": created_quote.get("SubTotal"),
                    "total_tax": created_quote.get("TotalTax"),
                    "total": created_quote.get("Total"),
                    "date": created_quote.get("Date"),
                    "expiry_date": created_quote.get("ExpiryDate"),
                    "branding_theme_id": created_quote.get("BrandingThemeID"),
                    "title": created_quote.get("Title"),
                    "summary": created_quote.get("Summary"),
                    "terms": created_quote.get("Terms"),
                    "reference": created_quote.get("Reference"),
                    "updated_date_utc": created_quote.get("UpdatedDateUTC")
                }
            }
        else:
            return {
                "success": False,
                "error": "No quote returned from Xero API",
                "response": response
            }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_list_quotes(
    business_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    contact_id: Optional[str] = None,
    status: Optional[str] = None,
    quote_number: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
    **kwargs
) -> Dict[str, Any]:
    """
    List quotes from Xero with filtering and pagination
    
    CRITICAL: With 70,000+ quotes, ALWAYS use filters (date range, contact, status)
    
    Args:
        business_id: Business ID (1=InHouse Print, 2=Publishing, 3=Signs)
        date_from: Filter from date YYYY-MM-DD (strongly recommended)
        date_to: Filter to date YYYY-MM-DD (strongly recommended)
        contact_id: Filter by specific contact ID
        status: Filter by status (DRAFT, SENT, DECLINED, ACCEPTED, INVOICED, DELETED)
        quote_number: Filter by specific quote number (exact match)
        page: Page number (default 1)
        page_size: Records per page (default 100, max 100)
        **kwargs: Credential injection (unused, for compatibility)
    
    Returns:
        Dict with pagination metadata and quotes array
    
    Raises:
        RuntimeError: If XeroAPIClient is not available
        Exception: If quote retrieval fails
    
    Example:
        xero_list_quotes(
            business_id=1,
            date_from="2025-11-01",
            date_to="2025-12-01",
            status="DRAFT",
            page=1,
            page_size=50
        )
    """
    try:
        client = _get_client(business_id)
        
        # Build WHERE clause for filtering
        where_clauses = []
        
        if date_from:
            where_clauses.append(f'Date >= DateTime({date_from.replace("-", ", ")})')
        
        if date_to:
            where_clauses.append(f'Date <= DateTime({date_to.replace("-", ", ")})')
        
        if contact_id:
            where_clauses.append(f'Contact.ContactID == Guid("{contact_id}")')
        
        if status:
            where_clauses.append(f'Status == "{status}"')
        
        if quote_number:
            where_clauses.append(f'QuoteNumber == "{quote_number}"')
        
        where_clause = " AND ".join(where_clauses) if where_clauses else None
        
        # Build query parameters
        params = {}
        if where_clause:
            params['where'] = where_clause
        if page:
            params['page'] = page
        
        # Make API request
        endpoint = 'Quotes'
        response = client.make_request('GET', endpoint, params=params)
        
        quotes = response.get('Quotes', [])
        
        # Apply page_size limit (Xero doesn't have page_size param, so we slice)
        start_idx = 0
        end_idx = page_size
        paginated_quotes = quotes[start_idx:end_idx]
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": len(quotes),
                "returned_count": len(paginated_quotes),
                "total_pages": (len(quotes) + page_size - 1) // page_size
            },
            "filters": {
                "date_from": date_from,
                "date_to": date_to,
                "contact_id": contact_id,
                "status": status,
                "quote_number": quote_number,
                "where_clause": where_clause
            },
            "quotes": [{
                "quote_id": q.get("QuoteID"),
                "quote_number": q.get("QuoteNumber"),
                "status": q.get("Status"),
                "contact": q.get("Contact", {}),
                "date": q.get("Date"),
                "expiry_date": q.get("ExpiryDate"),
                "sub_total": q.get("SubTotal"),
                "total_tax": q.get("TotalTax"),
                "total": q.get("Total"),
                "title": q.get("Title"),
                "branding_theme_id": q.get("BrandingThemeID"),
                "updated_date_utc": q.get("UpdatedDateUTC")
            } for q in paginated_quotes]
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_quote_by_id(
    business_id: int,
    quote_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get specific quote by QuoteID
    
    Args:
        business_id: Business ID (1=InHouse Print, 2=Publishing, 3=Signs)
        quote_id: Xero QuoteID (GUID format)
        **kwargs: Credential injection (unused, for compatibility)
    
    Returns:
        Dict with complete quote details
    
    Raises:
        RuntimeError: If XeroAPIClient is not available
        Exception: If quote retrieval fails
    
    Example:
        xero_get_quote_by_id(
            business_id=1,
            quote_id="d5b89e36-8a28-4c40-b8e4-2a0d3f5d7c93"
        )
    """
    try:
        client = _get_client(business_id)
        
        # Make API request
        endpoint = f'Quotes/{quote_id}'
        response = client.make_request('GET', endpoint)
        
        if response and 'Quotes' in response and len(response['Quotes']) > 0:
            quote = response['Quotes'][0]
            return {
                "success": True,
                "business_id": business_id,
                "business_name": client.config['name'],
                "quote": {
                    "quote_id": quote.get("QuoteID"),
                    "quote_number": quote.get("QuoteNumber"),
                    "status": quote.get("Status"),
                    "contact": quote.get("Contact", {}),
                    "line_items": quote.get("LineItems", []),
                    "sub_total": quote.get("SubTotal"),
                    "total_tax": quote.get("TotalTax"),
                    "total": quote.get("Total"),
                    "date": quote.get("Date"),
                    "expiry_date": quote.get("ExpiryDate"),
                    "branding_theme_id": quote.get("BrandingThemeID"),
                    "title": quote.get("Title"),
                    "summary": quote.get("Summary"),
                    "terms": quote.get("Terms"),
                    "reference": quote.get("Reference"),
                    "updated_date_utc": quote.get("UpdatedDateUTC")
                }
            }
        else:
            return {
                "success": False,
                "error": f"Quote not found: {quote_id}",
                "response": response
            }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_update_quote(
    business_id: int,
    quote_id: str,
    contact_id: Optional[str] = None,
    line_items: Optional[List[Dict[str, Any]]] = None,
    status: Optional[str] = None,
    branding_theme_id: Optional[str] = None,
    date: Optional[str] = None,
    expiry_date: Optional[str] = None,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    terms: Optional[str] = None,
    reference: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update an existing quote in Xero
    
    Args:
        business_id: Business ID (1=InHouse Print, 2=Publishing, 3=Signs)
        quote_id: Xero QuoteID to update
        contact_id: Update contact ID (optional)
        line_items: Updated line items array (optional, replaces all if provided)
        status: Update status (DRAFT, SENT, DECLINED, ACCEPTED)
        branding_theme_id: Change branding theme (optional)
        date: Update quote date YYYY-MM-DD (optional)
        expiry_date: Update expiry date YYYY-MM-DD (optional)
        title: Update title text max 100 chars (optional)
        summary: Update summary text max 3000 chars (optional)
        terms: Update terms text max 4000 chars (optional)
        reference: Update reference number max 4000 chars (optional)
        **kwargs: Credential injection (unused, for compatibility)
    
    Returns:
        Dict with updated quote details
    
    Raises:
        RuntimeError: If XeroAPIClient is not available
        Exception: If quote update fails
    
    Example:
        xero_update_quote(
            business_id=1,
            quote_id="d5b89e36-8a28-4c40-b8e4-2a0d3f5d7c93",
            status="SENT"
        )
    """
    try:
        client = _get_client(business_id)
        
        # Build update payload (only include provided fields)
        update_data = {
            "QuoteID": quote_id
        }
        
        if contact_id:
            update_data["Contact"] = {"ContactID": contact_id}
        
        if line_items:
            update_data["LineItems"] = []
            for item in line_items:
                line_item = {
                    "Description": item.get("description", ""),
                    "Quantity": item.get("quantity", 1),
                    "UnitAmount": item.get("unit_amount", 0)
                }
                if "account_code" in item:
                    line_item["AccountCode"] = item["account_code"]
                update_data["LineItems"].append(line_item)
        
        if status:
            update_data["Status"] = status
        
        if branding_theme_id:
            update_data["BrandingThemeID"] = branding_theme_id
        
        if date:
            update_data["Date"] = date
        
        if expiry_date:
            update_data["ExpiryDate"] = expiry_date
        
        if title:
            update_data["Title"] = title[:100]
        
        if summary:
            update_data["Summary"] = summary[:3000]
        
        if terms:
            update_data["Terms"] = terms[:4000]
        
        if reference:
            update_data["Reference"] = reference[:4000]
        
        # Make API request to update quote
        response = client.make_request('POST', 'Quotes', json={"Quotes": [update_data]})
        
        if response and 'Quotes' in response and len(response['Quotes']) > 0:
            updated_quote = response['Quotes'][0]
            return {
                "success": True,
                "business_id": business_id,
                "business_name": client.config['name'],
                "quote": {
                    "quote_id": updated_quote.get("QuoteID"),
                    "quote_number": updated_quote.get("QuoteNumber"),
                    "status": updated_quote.get("Status"),
                    "contact": updated_quote.get("Contact", {}),
                    "line_items": updated_quote.get("LineItems", []),
                    "sub_total": updated_quote.get("SubTotal"),
                    "total_tax": updated_quote.get("TotalTax"),
                    "total": updated_quote.get("Total"),
                    "date": updated_quote.get("Date"),
                    "expiry_date": updated_quote.get("ExpiryDate"),
                    "branding_theme_id": updated_quote.get("BrandingThemeID"),
                    "title": updated_quote.get("Title"),
                    "summary": updated_quote.get("Summary"),
                    "terms": updated_quote.get("Terms"),
                    "reference": updated_quote.get("Reference"),
                    "updated_date_utc": updated_quote.get("UpdatedDateUTC")
                },
                "updated_fields": [k for k in update_data.keys() if k != "QuoteID"]
            }
        else:
            return {
                "success": False,
                "error": "No quote returned from Xero API",
                "response": response
            }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def xero_get_branding_themes(
    business_id: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Get all available branding themes (templates) from Xero
    
    Branding themes control logo, colors, and layout of quotes/invoices.
    Use this to find BrandingThemeID values for creating/updating quotes.
    
    Args:
        business_id: Business ID (1=InHouse Print, 2=Publishing, 3=Signs)
        **kwargs: Credential injection (unused, for compatibility)
    
    Returns:
        Dict with branding themes array (BrandingThemeID, Name, LogoUrl, SortOrder)
    
    Raises:
        RuntimeError: If XeroAPIClient is not available
        Exception: If branding theme retrieval fails
    
    Example:
        xero_get_branding_themes(business_id=1)
    """
    try:
        client = _get_client(business_id)
        
        # Make API request
        response = client.make_request('GET', 'BrandingThemes')
        
        themes = response.get('BrandingThemes', [])
        
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "branding_themes": [{
                "branding_theme_id": theme.get("BrandingThemeID"),
                "name": theme.get("Name"),
                "logo_url": theme.get("LogoUrl"),
                "type": theme.get("Type"),
                "sort_order": theme.get("SortOrder"),
                "created_date_utc": theme.get("CreatedDateUTC")
            } for theme in themes]
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

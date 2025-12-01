"""
Xero Quotes Smart Tools - AI-Optimized Quote Creation Workflow

This module provides intelligent, single-call quote creation that handles
the complete workflow automatically:
- Contact lookup by name/email/ID
- Template selection based on business type
- Line item parsing from natural language
- Smart defaults for dates and terms
- Automatic quote generation

Functions:
- xero_create_quote_smart: Complete quote workflow in one call
"""

import traceback
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta


def _get_client(business_id: int):
    """Get XeroAPIClient instance"""
    try:
        from UI.external.modules.xero.xero_routes import XeroAPIClient
        return XeroAPIClient(business_id=business_id)
    except ImportError as e:
        raise RuntimeError(f"XeroAPIClient not available: {str(e)}")


def _find_contact(client, customer: str) -> Optional[Dict[str, Any]]:
    """
    Smart contact lookup by name, email, or ID
    
    Args:
        client: XeroAPIClient instance
        customer: Name, email, or contact ID
    
    Returns:
        Contact dict with ContactID, Name, Email or None
    """
    try:
        # Check if it's a GUID (ContactID)
        if len(customer) == 36 and customer.count('-') == 4:
            # Direct ID lookup
            response = client.make_request('GET', f'Contacts/{customer}')
            if response and 'Contacts' in response and len(response['Contacts']) > 0:
                return response['Contacts'][0]
        
        # Search by name or email
        # Try exact name match first
        where_clause = f'Name == "{customer}"'
        response = client.make_request('GET', 'Contacts', params={'where': where_clause})
        
        if response and 'Contacts' in response and len(response['Contacts']) > 0:
            return response['Contacts'][0]
        
        # Try email match
        if '@' in customer:
            where_clause = f'EmailAddress == "{customer}"'
            response = client.make_request('GET', 'Contacts', params={'where': where_clause})
            
            if response and 'Contacts' in response and len(response['Contacts']) > 0:
                return response['Contacts'][0]
        
        # Try partial name match
        response = client.make_request('GET', 'Contacts')
        if response and 'Contacts' in response:
            customer_lower = customer.lower()
            for contact in response['Contacts']:
                contact_name = contact.get('Name', '').lower()
                if customer_lower in contact_name or contact_name in customer_lower:
                    return contact
        
        return None
    except Exception as e:
        print(f"Warning: Contact lookup failed: {e}")
        return None


def _parse_line_items(items: List[Union[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Smart line item parser - handles both strings and objects
    
    Args:
        items: List of strings or dicts
    
    Returns:
        List of standardized line item dicts
    """
    parsed_items = []
    
    for item in items:
        if isinstance(item, dict):
            # Already structured
            parsed_items.append({
                'description': item.get('description', ''),
                'quantity': item.get('quantity', 1),
                'unit_amount': item.get('price', item.get('unit_amount', 0)),
                'account_code': item.get('account_code')
            })
        elif isinstance(item, str):
            # Parse from string
            # Pattern: "Description qty $price" or "Description $price" or just "Description"
            description = item
            quantity = 1
            price = 0
            
            # Extract price: $150, $150.00, 150.00, 150
            price_match = re.search(r'\$?(\d+\.?\d*)', item)
            if price_match:
                price = float(price_match.group(1))
                # Remove price from description
                description = item[:price_match.start()].strip()
            
            # Extract quantity: 1000qty, 500 qty, x10, 10x
            qty_match = re.search(r'(\d+)\s*(qty|x|units?)', item, re.IGNORECASE)
            if qty_match:
                quantity = int(qty_match.group(1))
            
            # Clean up description
            description = re.sub(r'\s+', ' ', description).strip()
            
            parsed_items.append({
                'description': description,
                'quantity': quantity,
                'unit_amount': price,
                'account_code': None
            })
    
    return parsed_items


def _get_default_template(client, business_id: int) -> Optional[str]:
    """
    Get default template for business
    
    Args:
        client: XeroAPIClient instance
        business_id: Business ID
    
    Returns:
        BrandingThemeID or None
    """
    try:
        response = client.make_request('GET', 'BrandingThemes')
        themes = response.get('BrandingThemes', [])
        
        # Find default (SortOrder = 0)
        for theme in themes:
            if theme.get('SortOrder', 999) == 0:
                return theme.get('BrandingThemeID')
        
        # Fallback to first theme
        if themes:
            return themes[0].get('BrandingThemeID')
        
        return None
    except Exception as e:
        print(f"Warning: Could not get default template: {e}")
        return None


def _find_template(client, template_hint: str) -> Optional[str]:
    """
    Find template by name/hint
    
    Args:
        client: XeroAPIClient instance
        template_hint: Template name or hint
    
    Returns:
        BrandingThemeID or None
    """
    try:
        response = client.make_request('GET', 'BrandingThemes')
        themes = response.get('BrandingThemes', [])
        
        template_lower = template_hint.lower()
        
        # Exact match
        for theme in themes:
            if theme.get('Name', '').lower() == template_lower:
                return theme.get('BrandingThemeID')
        
        # Partial match
        for theme in themes:
            theme_name = theme.get('Name', '').lower()
            if template_lower in theme_name or theme_name in template_lower:
                return theme.get('BrandingThemeID')
        
        return None
    except Exception as e:
        print(f"Warning: Template lookup failed: {e}")
        return None


def _generate_title(items: List[Dict[str, Any]]) -> str:
    """
    Auto-generate quote title from items
    
    Args:
        items: Line items
    
    Returns:
        Generated title
    """
    if not items:
        return "Quote"
    
    # Use first item description
    first_item = items[0].get('description', 'Quote')
    
    if len(items) == 1:
        return f"Quote: {first_item[:50]}"
    else:
        return f"Quote: {first_item[:30]}... (+{len(items)-1} items)"


def _get_business_terms(business_id: int) -> str:
    """
    Get default terms for business
    
    Args:
        business_id: Business ID
    
    Returns:
        Default terms text
    """
    terms_map = {
        1: "Payment due within 7 days. All prices are in AUD and exclude GST. Rush orders available for additional fee.",
        2: "Payment due within 14 days. Publishing services include design and print. Revisions subject to additional charges.",
        3: "Payment due within 7 days. Installation not included unless specified. Weather delays may affect timeline."
    }
    return terms_map.get(business_id, "Payment due within 7 days.")


def xero_create_quote_smart(
    business_id: int,
    customer: str,
    items: List[Union[str, Dict[str, Any]]],
    template: Optional[str] = None,
    title: Optional[str] = None,
    valid_days: int = 30,
    notes: Optional[str] = None,
    terms: Optional[str] = None,
    reference: Optional[str] = None,
    auto_send: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    🤖 SMART TOOL - Create quote with intelligent workflow automation
    
    Handles the complete quote creation process:
    1. Finds customer by name/email/ID
    2. Parses line items from natural language or structured data
    3. Selects appropriate template automatically
    4. Sets smart defaults for dates and terms
    5. Creates quote and optionally sends it
    
    Args:
        business_id: Business ID (1=InHouse Print, 2=Publishing, 3=Signs)
        customer: Customer name, email, or contact ID (smart lookup)
        items: Line items - strings or dicts (e.g., ["Business Cards 1000qty $150"] or detailed objects)
        template: Template name/hint (optional, auto-selects if not provided)
        title: Quote title (optional, auto-generates from items)
        valid_days: Quote validity in days (optional, default 30)
        notes: Additional notes/summary (optional)
        terms: Terms and conditions (optional, uses business defaults)
        reference: Internal reference number (optional)
        auto_send: Mark as SENT after creation (optional, default False/DRAFT)
        **kwargs: Credential injection
    
    Returns:
        Dict with success status, quote details, contact info, and recommendations
    
    Examples:
        # Simple natural language quote
        xero_create_quote_smart(
            business_id=1,
            customer="ABC Company",
            items=["Business Cards 1000qty $150", "Flyers A5 500qty $95"]
        )
        
        # Detailed quote with options
        xero_create_quote_smart(
            business_id=1,
            customer="john@example.com",
            items=[
                {"description": "Business Cards - 1000qty, 350GSM", "quantity": 1, "price": 150},
                {"description": "Flyers A5 - 500qty", "quantity": 1, "price": 95}
            ],
            template="Professional",
            title="Printing Quote",
            valid_days=14,
            auto_send=True
        )
    """
    try:
        client = _get_client(business_id)
        workflow_log = []
        
        # Step 1: Find customer
        workflow_log.append("🔍 Looking up customer...")
        contact = _find_contact(client, customer)
        
        if not contact:
            return {
                "success": False,
                "error": f"Customer not found: '{customer}'",
                "suggestion": "Try searching with xero_get_contacts first, or provide exact ContactID",
                "workflow_log": workflow_log
            }
        
        contact_id = contact.get('ContactID')
        contact_name = contact.get('Name')
        workflow_log.append(f"✅ Found customer: {contact_name} ({contact_id})")
        
        # Step 2: Parse line items
        workflow_log.append(f"📝 Parsing {len(items)} line items...")
        parsed_items = _parse_line_items(items)
        
        total_estimate = sum(item['quantity'] * item['unit_amount'] for item in parsed_items)
        workflow_log.append(f"✅ Items parsed - Estimated total: ${total_estimate:.2f}")
        
        # Step 3: Select template
        workflow_log.append("🎨 Selecting template...")
        branding_theme_id = None
        
        if template:
            branding_theme_id = _find_template(client, template)
            if branding_theme_id:
                workflow_log.append(f"✅ Using template: {template}")
            else:
                workflow_log.append(f"⚠️ Template '{template}' not found, using default")
        
        if not branding_theme_id:
            branding_theme_id = _get_default_template(client, business_id)
            workflow_log.append("✅ Using default template")
        
        # Step 4: Generate title if not provided
        if not title:
            title = _generate_title(parsed_items)
            workflow_log.append(f"✅ Auto-generated title: {title}")
        
        # Step 5: Calculate dates
        today = datetime.now().strftime("%Y-%m-%d")
        expiry = (datetime.now() + timedelta(days=valid_days)).strftime("%Y-%m-%d")
        workflow_log.append(f"✅ Quote valid until: {expiry} ({valid_days} days)")
        
        # Step 6: Set terms
        if not terms:
            terms = _get_business_terms(business_id)
            workflow_log.append("✅ Using default terms")
        
        # Step 7: Create quote
        workflow_log.append("📤 Creating quote in Xero...")
        
        quote_data = {
            "Contact": {"ContactID": contact_id},
            "LineItems": [
                {
                    "Description": item['description'],
                    "Quantity": item['quantity'],
                    "UnitAmount": item['unit_amount'],
                    **({"AccountCode": item['account_code']} if item['account_code'] else {})
                }
                for item in parsed_items
            ],
            "Date": today,
            "ExpiryDate": expiry,
            "Title": title,
            "Terms": terms
        }
        
        if branding_theme_id:
            quote_data["BrandingThemeID"] = branding_theme_id
        
        if notes:
            quote_data["Summary"] = notes
        
        if reference:
            quote_data["Reference"] = reference
        
        # Create quote
        response = client.make_request('PUT', 'Quotes', json={"Quotes": [quote_data]})
        
        if not response or 'Quotes' not in response or len(response['Quotes']) == 0:
            return {
                "success": False,
                "error": "Quote creation failed - no response from Xero API",
                "workflow_log": workflow_log
            }
        
        created_quote = response['Quotes'][0]
        quote_id = created_quote.get('QuoteID')
        quote_number = created_quote.get('QuoteNumber')
        
        workflow_log.append(f"✅ Quote created: {quote_number}")
        
        # Step 8: Auto-send if requested
        if auto_send:
            workflow_log.append("📧 Marking quote as SENT...")
            update_response = client.make_request('POST', 'Quotes', json={
                "Quotes": [{
                    "QuoteID": quote_id,
                    "Status": "SENT"
                }]
            })
            
            if update_response and 'Quotes' in update_response:
                created_quote = update_response['Quotes'][0]
                workflow_log.append("✅ Quote marked as SENT")
        
        # Step 9: Build comprehensive response
        return {
            "success": True,
            "business_id": business_id,
            "business_name": client.config['name'],
            "workflow_log": workflow_log,
            "quote": {
                "quote_id": created_quote.get('QuoteID'),
                "quote_number": created_quote.get('QuoteNumber'),
                "status": created_quote.get('Status'),
                "total": created_quote.get('Total'),
                "sub_total": created_quote.get('SubTotal'),
                "total_tax": created_quote.get('TotalTax'),
                "date": created_quote.get('Date'),
                "expiry_date": created_quote.get('ExpiryDate'),
                "title": created_quote.get('Title')
            },
            "contact": {
                "contact_id": contact.get('ContactID'),
                "name": contact.get('Name'),
                "email": contact.get('EmailAddress')
            },
            "items": [
                {
                    "description": item.get('Description'),
                    "quantity": item.get('Quantity'),
                    "unit_amount": item.get('UnitAmount'),
                    "line_amount": item.get('LineAmount')
                }
                for item in created_quote.get('LineItems', [])
            ],
            "summary": {
                "total_items": len(parsed_items),
                "estimated_total": f"${created_quote.get('Total', 0):.2f}",
                "valid_until": expiry,
                "status": created_quote.get('Status'),
                "ready_to_send": created_quote.get('Status') == 'DRAFT'
            },
            "next_steps": [
                f"Quote {quote_number} created successfully",
                f"Status: {created_quote.get('Status')}",
                "Use xero_update_quote to mark as SENT when ready" if not auto_send else "Quote has been marked as SENT",
                "Share quote with customer via email or Xero portal"
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "workflow_log": workflow_log if 'workflow_log' in locals() else []
        }

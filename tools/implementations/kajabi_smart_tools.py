"""
Kajabi Smart Tools - Enhanced Analytics & Export Capabilities
=============================================================

Provides Gmail/Outlook-style smart tools for Kajabi:
- Bulk analytics and summaries (reduces token usage)
- Direct export to Google Sheets/Docs
- Multiple result formats (JSON, CSV, summary)
- Batch member operations

Pattern: Follows gmail_bulk_read_summarize and outlook_smart_email_summary patterns
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from tools.implementations.kajabi import KajabiTools, KajabiError
    HAS_KAJABI = True
except ImportError:
    HAS_KAJABI = False
    print("⚠️ Kajabi base tools not available")


class KajabiSmartTools:
    """Enhanced Kajabi tools with analytics and export capabilities"""
    
    def __init__(self):
        """Initialize smart tools"""
        if not HAS_KAJABI:
            raise Exception("Kajabi base tools required - import kajabi.py first")
        
        self.kajabi = KajabiTools()
    
    # ==================== SMART ANALYTICS ====================
    
    def kajabi_member_analytics(
        self,
        status_filter: Optional[str] = None,
        include_product_access: bool = True,
        output_format: str = 'summary',
        export_to_sheets: bool = False,
        sheet_title: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        📊 SMART ANALYTICS: Comprehensive member analytics with export
        
        Similar to gmail_bulk_read_summarize - analyzes all members and provides insights.
        
        Args:
            status_filter: Filter by 'active', 'inactive', 'trialing', or None for all
            include_product_access: Include product access details (more API calls)
            output_format: 'summary' (token-efficient), 'detailed' (full data), 'csv' (export format)
            export_to_sheets: Create Google Sheets with results
            sheet_title: Custom sheet title (default: "Kajabi Members - {date}")
        
        Returns:
            Dict with analytics + optional spreadsheet_url
            
        Output format 'summary':
            {
                'total_members': int,
                'by_status': {'active': int, 'inactive': int, ...},
                'top_products': [{'product_name': str, 'member_count': int}, ...],
                'recent_signups': int (last 30 days),
                'spreadsheet_url': str (if export_to_sheets=True)
            }
        
        Output format 'detailed':
            {
                'members': [full member data],
                'analytics': {...},
                'spreadsheet_url': str (optional)
            }
        
        Output format 'csv':
            {
                'csv_data': str (CSV formatted),
                'spreadsheet_url': str (optional)
            }
        
        Use Cases:
            - "Analyze all active members and export to sheets"
            - "Show member stats in summary format"
            - "Get member list as CSV"
        """
        try:
            print(f"📊 Analyzing Kajabi members (format: {output_format})...")
            
            # Fetch all members (paginated)
            all_members = []
            page = 1
            
            while True:
                result = self.kajabi.list_members(
                    page=page,
                    per_page=100,
                    status=status_filter,
                    **kwargs
                )
                
                members = result.get('members', result.get('data', []))
                if not members:
                    break
                
                all_members.extend(members)
                
                # Check pagination
                pagination = result.get('pagination', {})
                if page >= pagination.get('total_pages', 1):
                    break
                
                page += 1
                print(f"  Loaded page {page} ({len(all_members)} members so far)...")
            
            print(f"✅ Loaded {len(all_members)} members")
            
            # Build analytics
            analytics = {
                'total_members': len(all_members),
                'by_status': {},
                'top_products': {},
                'recent_signups': 0,
                'tags_summary': {}
            }
            
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            for member in all_members:
                # Status breakdown
                status = member.get('status', 'unknown')
                analytics['by_status'][status] = analytics['by_status'].get(status, 0) + 1
                
                # Recent signups
                created_at = member.get('created_at')
                if created_at:
                    try:
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if created_date >= thirty_days_ago:
                            analytics['recent_signups'] += 1
                    except:
                        pass
                
                # Product access
                if include_product_access:
                    products = member.get('products', [])
                    for product in products:
                        product_name = product.get('name', 'Unknown')
                        analytics['top_products'][product_name] = \
                            analytics['top_products'].get(product_name, 0) + 1
                
                # Tags
                tags = member.get('tags', [])
                for tag in tags:
                    analytics['tags_summary'][tag] = \
                        analytics['tags_summary'].get(tag, 0) + 1
            
            # Sort top products
            top_products_list = [
                {'product_name': name, 'member_count': count}
                for name, count in sorted(
                    analytics['top_products'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            ]
            
            analytics['top_products'] = top_products_list
            
            # Format output based on requested format
            if output_format == 'summary':
                result_data = analytics
                
            elif output_format == 'detailed':
                result_data = {
                    'analytics': analytics,
                    'members': all_members
                }
            
            elif output_format == 'csv':
                # Convert to CSV format
                csv_lines = ['Email,Name,Status,Created At,Products,Tags']
                
                for member in all_members:
                    email = member.get('email', '')
                    name = member.get('name', member.get('full_name', ''))
                    status = member.get('status', '')
                    created_at = member.get('created_at', '')
                    products = ';'.join([p.get('name', '') for p in member.get('products', [])])
                    tags = ';'.join(member.get('tags', []))
                    
                    csv_lines.append(f'"{email}","{name}","{status}","{created_at}","{products}","{tags}"')
                
                result_data = {
                    'csv_data': '\n'.join(csv_lines),
                    'row_count': len(all_members)
                }
            
            else:
                raise ValueError(f"Invalid output_format: {output_format}. Use 'summary', 'detailed', or 'csv'")
            
            # Export to Google Sheets if requested
            if export_to_sheets:
                try:
                    print("📊 Creating Google Sheets export...")
                    
                    # Import Google Sheets tools
                    from google_workspace import gsheets
                    
                    # Prepare data for spreadsheet
                    if output_format == 'csv':
                        # Use CSV data
                        rows = [line.split(',') for line in result_data['csv_data'].split('\n')]
                    else:
                        # Build from member data
                        headers = ['Email', 'Name', 'Status', 'Created At', 'Products', 'Tags']
                        rows = [headers]
                        
                        for member in all_members:
                            rows.append([
                                member.get('email', ''),
                                member.get('name', member.get('full_name', '')),
                                member.get('status', ''),
                                member.get('created_at', ''),
                                ', '.join([p.get('name', '') for p in member.get('products', [])]),
                                ', '.join(member.get('tags', []))
                            ])
                    
                    # Create spreadsheet
                    sheet_result = gsheets.gsheets_create_complete_spreadsheet(
                        title=sheet_title or f"Kajabi Members - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        data=rows,
                        bold_headers=True,
                        freeze_header_row=True,
                        **kwargs
                    )
                    
                    result_data['spreadsheet_id'] = sheet_result['spreadsheet_id']
                    result_data['spreadsheet_url'] = sheet_result['spreadsheet_url']
                    
                    print(f"✅ Spreadsheet created: {sheet_result['spreadsheet_url']}")
                    
                except Exception as e:
                    print(f"⚠️ Could not create spreadsheet: {e}")
                    result_data['spreadsheet_error'] = str(e)
            
            return result_data
            
        except Exception as e:
            print(f"❌ Member analytics failed: {e}")
            raise KajabiError(f"Analytics failed: {str(e)}")
    
    def kajabi_product_performance(
        self,
        include_member_count: bool = True,
        include_revenue_data: bool = False,
        output_format: str = 'summary',
        export_to_sheets: bool = False,
        **kwargs
    ) -> Dict:
        """
        📈 SMART ANALYTICS: Product performance analysis
        
        Analyzes all products with enrollment and engagement metrics.
        
        Args:
            include_member_count: Count members per product (more API calls)
            include_revenue_data: Include revenue metrics (if available)
            output_format: 'summary' (top products only), 'detailed' (all products), 'csv'
            export_to_sheets: Create Google Sheets with results
        
        Returns:
            Product performance metrics + optional spreadsheet_url
            
        Use Cases:
            - "Which products have the most students?"
            - "Show product performance summary"
            - "Export product data to sheets"
        """
        try:
            print(f"📈 Analyzing Kajabi products (format: {output_format})...")
            
            # Fetch all products
            all_products = []
            page = 1
            
            while True:
                result = self.kajabi.list_products(page=page, per_page=100, **kwargs)
                
                products = result.get('products', result.get('data', []))
                if not products:
                    break
                
                all_products.extend(products)
                
                pagination = result.get('pagination', {})
                if page >= pagination.get('total_pages', 1):
                    break
                
                page += 1
            
            print(f"✅ Loaded {len(all_products)} products")
            
            # Enrich with member count if requested
            if include_member_count:
                print("  Counting members per product...")
                
                # Get all members
                members_result = self.kajabi.list_members(per_page=100, **kwargs)
                all_members = members_result.get('members', members_result.get('data', []))
                
                # Count members per product
                product_member_counts = {}
                for member in all_members:
                    for product in member.get('products', []):
                        product_id = product.get('id')
                        if product_id:
                            product_member_counts[product_id] = \
                                product_member_counts.get(product_id, 0) + 1
                
                # Add counts to products
                for product in all_products:
                    product['member_count'] = product_member_counts.get(product.get('id'), 0)
            
            # Sort by member count (if available)
            if include_member_count:
                all_products.sort(key=lambda p: p.get('member_count', 0), reverse=True)
            
            # Format output
            if output_format == 'summary':
                result_data = {
                    'total_products': len(all_products),
                    'top_products': [
                        {
                            'name': p.get('name'),
                            'type': p.get('type'),
                            'member_count': p.get('member_count', 'N/A'),
                            'id': p.get('id')
                        }
                        for p in all_products[:10]
                    ]
                }
            
            elif output_format == 'detailed':
                result_data = {
                    'total_products': len(all_products),
                    'products': all_products
                }
            
            elif output_format == 'csv':
                csv_lines = ['Product Name,Type,Member Count,Product ID']
                
                for product in all_products:
                    csv_lines.append(
                        f'"{product.get("name", "")}","{product.get("type", "")}","{product.get("member_count", "N/A")}","{product.get("id", "")}"'
                    )
                
                result_data = {
                    'csv_data': '\n'.join(csv_lines),
                    'row_count': len(all_products)
                }
            
            else:
                raise ValueError(f"Invalid output_format: {output_format}")
            
            # Export to sheets if requested
            if export_to_sheets:
                try:
                    from google_workspace import gsheets
                    
                    # Prepare rows
                    if output_format == 'csv':
                        rows = [line.split(',') for line in result_data['csv_data'].split('\n')]
                    else:
                        headers = ['Product Name', 'Type', 'Member Count', 'Product ID']
                        rows = [headers]
                        
                        for product in all_products:
                            rows.append([
                                product.get('name', ''),
                                product.get('type', ''),
                                str(product.get('member_count', 'N/A')),
                                product.get('id', '')
                            ])
                    
                    sheet_result = gsheets.gsheets_create_complete_spreadsheet(
                        title=f"Kajabi Products - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        data=rows,
                        bold_headers=True,
                        freeze_header_row=True,
                        **kwargs
                    )
                    
                    result_data['spreadsheet_url'] = sheet_result['spreadsheet_url']
                    print(f"✅ Spreadsheet created: {sheet_result['spreadsheet_url']}")
                    
                except Exception as e:
                    result_data['spreadsheet_error'] = str(e)
            
            return result_data
            
        except Exception as e:
            print(f"❌ Product performance analysis failed: {e}")
            raise KajabiError(f"Analysis failed: {str(e)}")
    
    def kajabi_bulk_member_operations(
        self,
        operation: str,
        member_ids: List[str],
        **operation_params
    ) -> Dict:
        """
        🔧 BULK OPERATIONS: Perform actions on multiple members at once
        
        Supported operations:
        - 'grant_access': Grant product access to multiple members
        - 'revoke_access': Revoke product access from multiple members
        - 'add_tag': Add tag to multiple members
        - 'remove_tag': Remove tag from multiple members
        
        Args:
            operation: Operation type (see above)
            member_ids: List of member IDs
            **operation_params: Operation-specific parameters
                For 'grant_access'/'revoke_access': product_id (required)
                For 'add_tag'/'remove_tag': tag (required)
        
        Returns:
            {
                'operation': str,
                'total_members': int,
                'successful': int,
                'failed': int,
                'results': [{'member_id': str, 'success': bool, 'error': str?}, ...]
            }
        
        Use Cases:
            - "Grant course access to 50 members"
            - "Add 'VIP' tag to all premium members"
            - "Remove access from list of members"
        """
        try:
            print(f"🔧 Bulk operation '{operation}' on {len(member_ids)} members...")
            
            results = []
            successful = 0
            failed = 0
            
            for i, member_id in enumerate(member_ids):
                try:
                    if operation == 'grant_access':
                        product_id = operation_params.get('product_id')
                        if not product_id:
                            raise ValueError("product_id required for grant_access")
                        
                        self.kajabi.grant_product_access(
                            member_id=member_id,
                            product_id=product_id,
                            **operation_params
                        )
                        results.append({'member_id': member_id, 'success': True})
                        successful += 1
                    
                    elif operation == 'revoke_access':
                        product_id = operation_params.get('product_id')
                        if not product_id:
                            raise ValueError("product_id required for revoke_access")
                        
                        self.kajabi.revoke_product_access(
                            member_id=member_id,
                            product_id=product_id,
                            **operation_params
                        )
                        results.append({'member_id': member_id, 'success': True})
                        successful += 1
                    
                    elif operation == 'add_tag':
                        tag = operation_params.get('tag')
                        if not tag:
                            raise ValueError("tag required for add_tag")
                        
                        self.kajabi.add_member_tag(
                            member_id=member_id,
                            tag=tag,
                            **operation_params
                        )
                        results.append({'member_id': member_id, 'success': True})
                        successful += 1
                    
                    elif operation == 'remove_tag':
                        tag = operation_params.get('tag')
                        if not tag:
                            raise ValueError("tag required for remove_tag")
                        
                        self.kajabi.remove_member_tag(
                            member_id=member_id,
                            tag=tag,
                            **operation_params
                        )
                        results.append({'member_id': member_id, 'success': True})
                        successful += 1
                    
                    else:
                        raise ValueError(f"Invalid operation: {operation}")
                    
                    if (i + 1) % 10 == 0:
                        print(f"  Processed {i + 1}/{len(member_ids)} members...")
                
                except Exception as e:
                    results.append({
                        'member_id': member_id,
                        'success': False,
                        'error': str(e)
                    })
                    failed += 1
            
            print(f"✅ Bulk operation complete: {successful} successful, {failed} failed")
            
            return {
                'operation': operation,
                'total_members': len(member_ids),
                'successful': successful,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            print(f"❌ Bulk operation failed: {e}")
            raise KajabiError(f"Bulk operation failed: {str(e)}")
    
    def kajabi_export_to_doc(
        self,
        content_type: str,
        title: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        📄 EXPORT TO GOOGLE DOCS: Create formatted Google Doc with Kajabi data
        
        Exports Kajabi data to a Google Doc with proper formatting.
        
        Args:
            content_type: 'member_list', 'product_list', 'analytics_report'
            title: Document title (default: auto-generated)
        
        Returns:
            {
                'document_id': str,
                'document_url': str,
                'title': str
            }
        
        Use Cases:
            - "Create a doc with all members"
            - "Export product list to Google Docs"
            - "Generate analytics report in docs"
        """
        try:
            print(f"📄 Creating Google Doc with {content_type}...")
            
            # Import Google Docs tools
            from google_workspace import google_docs
            
            # Generate content based on type
            if content_type == 'member_list':
                analytics = self.kajabi_member_analytics(
                    output_format='detailed',
                    **kwargs
                )
                
                content_lines = [
                    f"# Kajabi Members Report",
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    f"",
                    f"## Summary",
                    f"- Total Members: {analytics['analytics']['total_members']}",
                    f"- Recent Signups (30 days): {analytics['analytics']['recent_signups']}",
                    f"",
                    f"## Members by Status",
                ]
                
                for status, count in analytics['analytics']['by_status'].items():
                    content_lines.append(f"- {status.title()}: {count}")
                
                content_lines.extend([
                    "",
                    "## Top Products",
                ])
                
                for product in analytics['analytics']['top_products']:
                    content_lines.append(f"- {product['product_name']}: {product['member_count']} members")
                
                content = '\n'.join(content_lines)
                doc_title = title or f"Kajabi Members - {datetime.now().strftime('%Y-%m-%d')}"
            
            elif content_type == 'product_list':
                products_data = self.kajabi_product_performance(
                    output_format='detailed',
                    include_member_count=True,
                    **kwargs
                )
                
                content_lines = [
                    f"# Kajabi Products Report",
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    f"",
                    f"Total Products: {products_data['total_products']}",
                    f"",
                    f"## Product List",
                    f""
                ]
                
                for product in products_data['products']:
                    content_lines.extend([
                        f"### {product.get('name', 'Unnamed')}",
                        f"- Type: {product.get('type', 'N/A')}",
                        f"- Members: {product.get('member_count', 'N/A')}",
                        f"- ID: {product.get('id', 'N/A')}",
                        ""
                    ])
                
                content = '\n'.join(content_lines)
                doc_title = title or f"Kajabi Products - {datetime.now().strftime('%Y-%m-%d')}"
            
            elif content_type == 'analytics_report':
                # Comprehensive analytics report
                member_analytics = self.kajabi_member_analytics(output_format='summary', **kwargs)
                product_data = self.kajabi_product_performance(output_format='summary', include_member_count=True, **kwargs)
                
                content_lines = [
                    f"# Kajabi Analytics Report",
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    f"",
                    f"## Member Analytics",
                    f"- Total Members: {member_analytics['total_members']}",
                    f"- Recent Signups: {member_analytics['recent_signups']}",
                    f"",
                    f"### Members by Status",
                ]
                
                for status, count in member_analytics['by_status'].items():
                    content_lines.append(f"- {status.title()}: {count}")
                
                content_lines.extend([
                    "",
                    "## Product Analytics",
                    f"- Total Products: {product_data['total_products']}",
                    "",
                    "### Top Products",
                ])
                
                for product in product_data['top_products']:
                    content_lines.append(f"- {product['name']}: {product['member_count']} members")
                
                content = '\n'.join(content_lines)
                doc_title = title or f"Kajabi Analytics - {datetime.now().strftime('%Y-%m-%d')}"
            
            else:
                raise ValueError(f"Invalid content_type: {content_type}")
            
            # Create Google Doc
            doc_result = google_docs.gdocs_create_from_markdown(
                title=doc_title,
                markdown_content=content,
                **kwargs
            )
            
            print(f"✅ Google Doc created: {doc_result['document_url']}")
            
            return {
                'document_id': doc_result['document_id'],
                'document_url': doc_result['document_url'],
                'title': doc_title
            }
            
        except Exception as e:
            print(f"❌ Export to doc failed: {e}")
            raise KajabiError(f"Export failed: {str(e)}")


# ========================================
# GLOBAL INSTANCE & MODULE-LEVEL EXPORTS
# ========================================

# Create global instance
kajabi_smart_tools = KajabiSmartTools() if HAS_KAJABI else None

# Export all functions at module level
def kajabi_member_analytics(**kwargs):
    """Smart analytics for Kajabi members with export options"""
    if not kajabi_smart_tools:
        raise Exception("Kajabi smart tools not available")
    return kajabi_smart_tools.kajabi_member_analytics(**kwargs)

def kajabi_product_performance(**kwargs):
    """Smart analytics for Kajabi products with export options"""
    if not kajabi_smart_tools:
        raise Exception("Kajabi smart tools not available")
    return kajabi_smart_tools.kajabi_product_performance(**kwargs)

def kajabi_bulk_member_operations(**kwargs):
    """Bulk operations on multiple members"""
    if not kajabi_smart_tools:
        raise Exception("Kajabi smart tools not available")
    return kajabi_smart_tools.kajabi_bulk_member_operations(**kwargs)

def kajabi_export_to_doc(**kwargs):
    """Export Kajabi data to Google Docs"""
    if not kajabi_smart_tools:
        raise Exception("Kajabi smart tools not available")
    return kajabi_smart_tools.kajabi_export_to_doc(**kwargs)

"""
Quote Request Email Processor

This module automatically processes incoming emails for quote requests,
extracts relevant information, and prepares them for quote generation.

Features:
- Monitor inbox for quote request emails
- Extract customer details, product requirements, quantities
- Parse attachments (specs, artwork, etc.)
- Create structured quote request data
- Store in database and OneDrive
- Send acknowledgment emails

Author: InHouse Print Development Team
Date: October 17, 2025
"""

import re
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Microsoft_365_Connection.microsoft365_client import Microsoft365Client
from tools.db_connector import InHousePrintDB

logger = logging.getLogger(__name__)


class QuoteRequestProcessor:
    """
    Process incoming emails for quote requests
    """
    
    # Keywords that indicate quote requests
    QUOTE_KEYWORDS = [
        'quote', 'quotation', 'price', 'estimate', 'pricing',
        'cost', 'how much', 'proposal', 'can you quote'
    ]
    
    # Product keywords
    PRODUCT_KEYWORDS = {
        'flyers': ['flyer', 'flyers', 'leaflet', 'leaflets'],
        'business_cards': ['business card', 'business cards', 'card', 'cards'],
        'brochures': ['brochure', 'brochures', 'booklet', 'booklets'],
        'posters': ['poster', 'posters', 'banner', 'banners'],
        'books': ['book', 'books', 'perfect bound', 'wire bound', 'spiral bound'],
        'corflute': ['corflute', 'corflute sign', 'signage', 'yard sign'],
        'stickers': ['sticker', 'stickers', 'label', 'labels', 'decal'],
        'vinyl': ['vinyl', 'vinyl banner', 'mesh banner']
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize quote request processor
        
        Args:
            config_path: Path to config file
        """
        self.m365 = Microsoft365Client(config_path)
        self.db = InHousePrintDB(config_path or "config/database-config.json")
    
    def monitor_for_quote_requests(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Monitor inbox for quote request emails
        
        Args:
            limit: Maximum number of emails to check
            
        Returns:
            List of quote request emails
        """
        logger.info("Checking inbox for quote requests...")
        
        # Search for quote-related emails
        quote_emails = self.m365.search_emails_for_quotes(
            keywords=self.QUOTE_KEYWORDS,
            top=limit
        )
        
        logger.info(f"Found {len(quote_emails)} potential quote request emails")
        
        # Filter unread emails only
        unread_quotes = [email for email in quote_emails if not email.get('isRead', True)]
        
        logger.info(f"{len(unread_quotes)} unread quote requests")
        
        return unread_quotes
    
    def extract_quote_info(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract quote request information from email
        
        Args:
            email: Email message dictionary
            
        Returns:
            Structured quote request data
        """
        subject = email.get('subject', '')
        body = email.get('body', {}).get('content', '')
        sender = email.get('from', {}).get('emailAddress', {})
        
        # Extract customer info
        customer_email = sender.get('address', '')
        customer_name = sender.get('name', customer_email.split('@')[0])
        
        # Detect product type
        product_type = self._detect_product_type(subject + ' ' + body)
        
        # Extract quantities
        quantities = self._extract_quantities(body)
        
        # Extract sizes
        sizes = self._extract_sizes(body)
        
        # Check for attachments
        attachments = email.get('hasAttachments', False)
        
        quote_data = {
            'message_id': email.get('id'),
            'received_date': email.get('receivedDateTime'),
            'customer_name': customer_name,
            'customer_email': customer_email,
            'subject': subject,
            'body_preview': email.get('bodyPreview', '')[:500],
            'product_type': product_type,
            'quantities': quantities,
            'sizes': sizes,
            'has_attachments': attachments,
            'status': 'pending',
            'extracted_at': datetime.now().isoformat()
        }
        
        logger.info(f"Extracted quote request: {product_type} - {quantities}")
        
        return quote_data
    
    def _detect_product_type(self, text: str) -> str:
        """
        Detect product type from email text
        
        Args:
            text: Email subject + body
            
        Returns:
            Product type (or 'unknown')
        """
        text_lower = text.lower()
        
        for product_type, keywords in self.PRODUCT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return product_type
        
        return 'unknown'
    
    def _extract_quantities(self, text: str) -> List[int]:
        """
        Extract quantity numbers from text
        
        Args:
            text: Email body
            
        Returns:
            List of quantities found
        """
        quantities = []
        
        # Pattern: number followed by quantity indicators
        patterns = [
            r'(\d{1,6})\s*(?:pcs|pieces|units|qty|quantity|x)',
            r'(?:quantity|qty)[:=\s]+(\d{1,6})',
            r'(\d{1,6})\s*(?:flyers|cards|posters|books|brochures)',
            r'need\s+(\d{1,6})',
            r'print\s+(\d{1,6})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    qty = int(match)
                    if 1 <= qty <= 1000000:  # Reasonable range
                        quantities.append(qty)
                except ValueError:
                    continue
        
        # Remove duplicates and sort
        quantities = sorted(list(set(quantities)))
        
        return quantities
    
    def _extract_sizes(self, text: str) -> List[str]:
        """
        Extract paper/product sizes from text
        
        Args:
            text: Email body
            
        Returns:
            List of sizes found (e.g., ['A4', 'DL', '210x297mm'])
        """
        sizes = []
        
        # Standard sizes
        standard_patterns = [
            r'\b(A[0-9]|DL|A6|A5|A4|A3|A2|A1|A0)\b',
            r'\b(\d{2,4}\s*x\s*\d{2,4})\s*mm\b',
            r'\b(\d{2,4}mm\s*x\s*\d{2,4}mm)\b'
        ]
        
        for pattern in standard_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            sizes.extend(matches)
        
        # Remove duplicates
        sizes = list(set(sizes))
        
        return sizes
    
    def process_quote_request(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete processing of quote request email
        
        Args:
            email: Email message dictionary
            
        Returns:
            Processing result with quote request ID
        """
        logger.info(f"Processing quote request: {email.get('subject')}")
        
        # Extract quote information
        quote_data = self.extract_quote_info(email)
        
        # Download attachments if any
        if quote_data['has_attachments']:
            attachments = self.m365.get_email_attachments(email['id'])
            quote_data['attachment_count'] = len(attachments)
            
            # Store attachments in OneDrive
            attachment_folder = f"InHouse/QuoteRequests/{datetime.now().strftime('%Y%m%d')}_{quote_data['customer_email'].split('@')[0]}"
            
            for idx, attachment in enumerate(attachments):
                if attachment.get('@odata.type') == '#microsoft.graph.fileAttachment':
                    file_name = attachment.get('name', f'attachment_{idx}')
                    
                    # Download and upload to OneDrive
                    try:
                        import base64
                        content = base64.b64decode(attachment.get('contentBytes', ''))
                        
                        result = self.m365.upload_file_content(
                            file_content=content,
                            destination_path=f"{attachment_folder}/{file_name}"
                        )
                        
                        logger.info(f"Stored attachment: {file_name}")
                    except Exception as e:
                        logger.error(f"Failed to store attachment: {e}")
        
        # Save to database
        quote_request_id = self._save_to_database(quote_data)
        quote_data['quote_request_id'] = quote_request_id
        
        # Mark email as read
        self.m365.mark_email_as_read(email['id'])
        
        # Move to Quote Requests folder (optional)
        # self.m365.move_email_to_folder(email['id'], 'Quote Requests')
        
        # Send acknowledgment email
        self._send_acknowledgment(quote_data)
        
        logger.info(f"Quote request processed: ID {quote_request_id}")
        
        return quote_data
    
    def _save_to_database(self, quote_data: Dict[str, Any]) -> int:
        """
        Save quote request to database
        
        Args:
            quote_data: Quote request data
            
        Returns:
            Quote request ID
        """
        try:
            sql = """
                INSERT INTO QuoteRequests 
                (CustomerName, CustomerEmail, Subject, ProductType, Quantities, Sizes, 
                 ReceivedDate, Status, HasAttachments, BodyPreview)
                VALUES 
                (@CustomerName, @CustomerEmail, @Subject, @ProductType, @Quantities, @Sizes,
                 @ReceivedDate, @Status, @HasAttachments, @BodyPreview);
                
                SELECT SCOPE_IDENTITY() AS QuoteRequestID;
            """
            
            params = {
                'CustomerName': quote_data['customer_name'],
                'CustomerEmail': quote_data['customer_email'],
                'Subject': quote_data['subject'],
                'ProductType': quote_data['product_type'],
                'Quantities': json.dumps(quote_data['quantities']),
                'Sizes': json.dumps(quote_data['sizes']),
                'ReceivedDate': quote_data['received_date'],
                'Status': 'pending',
                'HasAttachments': quote_data['has_attachments'],
                'BodyPreview': quote_data['body_preview']
            }
            
            result = self.db.execute_query(sql, params)
            quote_request_id = result[0]['QuoteRequestID'] if result else None
            
            logger.info(f"Saved quote request to database: ID {quote_request_id}")
            return quote_request_id
            
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
            return None
    
    def _send_acknowledgment(self, quote_data: Dict[str, Any]):
        """
        Send acknowledgment email to customer
        
        Args:
            quote_data: Quote request data
        """
        try:
            body = f"""
            <html>
            <body>
                <h2>Thank you for your quote request!</h2>
                <p>Dear {quote_data['customer_name']},</p>
                <p>We have received your quote request for <strong>{quote_data['product_type']}</strong> 
                   and our team is reviewing it.</p>
                
                <h3>Request Details:</h3>
                <ul>
                    <li><strong>Product:</strong> {quote_data['product_type']}</li>
                    <li><strong>Quantities:</strong> {', '.join(map(str, quote_data['quantities'])) if quote_data['quantities'] else 'To be confirmed'}</li>
                    <li><strong>Sizes:</strong> {', '.join(quote_data['sizes']) if quote_data['sizes'] else 'To be confirmed'}</li>
                    <li><strong>Reference:</strong> #{quote_data.get('quote_request_id', 'Pending')}</li>
                </ul>
                
                <p>We will respond to your request within <strong>24 hours</strong> with a detailed quote.</p>
                
                <p>If you have any questions, please don't hesitate to contact us.</p>
                
                <p>Best regards,<br>
                <strong>InHouse Print Team</strong><br>
                printing@inhouseprint.com.au</p>
            </body>
            </html>
            """
            
            self.m365.send_email(
                to_addresses=[quote_data['customer_email']],
                subject=f"Quote Request Received - Ref #{quote_data.get('quote_request_id')}",
                body=body,
                body_type='HTML'
            )
            
            logger.info(f"Acknowledgment email sent to {quote_data['customer_email']}")
            
        except Exception as e:
            logger.error(f"Failed to send acknowledgment email: {e}")
    
    def batch_process_inbox(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Batch process all quote request emails in inbox
        
        Args:
            limit: Maximum number of emails to process
            
        Returns:
            List of processed quote requests
        """
        logger.info("Starting batch processing of quote requests...")
        
        # Get quote request emails
        quote_emails = self.monitor_for_quote_requests(limit)
        
        processed_requests = []
        
        for email in quote_emails:
            try:
                result = self.process_quote_request(email)
                processed_requests.append(result)
            except Exception as e:
                logger.error(f"Failed to process email {email.get('id')}: {e}")
                continue
        
        logger.info(f"Batch processing complete: {len(processed_requests)} requests processed")
        
        return processed_requests


if __name__ == "__main__":
    """
    Example usage and testing
    """
    print("Quote Request Email Processor")
    print("=" * 60)
    
    processor = QuoteRequestProcessor()
    
    print("\nFeatures:")
    print("  ✓ Monitor inbox for quote request emails")
    print("  ✓ Extract customer details and product info")
    print("  ✓ Parse quantities, sizes, and requirements")
    print("  ✓ Download and store attachments in OneDrive")
    print("  ✓ Save to database for quote generation")
    print("  ✓ Send acknowledgment emails to customers")
    
    print("\n" + "=" * 60)
    print("Usage:")
    print("  processor = QuoteRequestProcessor()")
    print("  requests = processor.batch_process_inbox()")
    print("=" * 60)

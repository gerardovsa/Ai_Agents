"""
TOOL USE API IMPLEMENTATION - Official Anthropic API
=====================================================
from shared.database_utils import convert_sql_placeholders

This implements the OFFICIAL Anthropic Tool Use API with:
- Client tools (execute_sql, calculate_quote, get_calculator_requirements)
- Server tools (web_search with Brisbane location)
- Extended Thinking with Interleaved Thinking beta
- Comprehensive event capture and logging
- Citation display for web search results
"""

import sys
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from anthropic import Anthropic

# CRITICAL FIX: Override print() to strip Unicode emoji for Windows cp1252 console
import builtins
_original_print = builtins.print
def _safe_print(*args, **kwargs):
    """Windows-safe print that strips Unicode emoji before printing"""
    safe_args = []
    for arg in args:
        if isinstance(arg, str):
            # Strip Unicode characters that cp1252 can't handle
            safe_arg = arg.encode('ascii', errors='ignore').decode('ascii')
            safe_args.append(safe_arg)
        else:
            safe_args.append(arg)
    _original_print(*safe_args, **kwargs)
builtins.print = _safe_print

# Add Quote_Calculator directory (2 levels up) to path
quote_calculator_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, quote_calculator_path)

# Add tools directory to path  
tools_path = os.path.join(quote_calculator_path, '..', 'tools')
sys.path.insert(0, tools_path)

# Add core directory to path (for query_library)
core_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, core_path)

# Add shopify_calculators directory to path
shopify_calculators_path = os.path.join(quote_calculator_path, 'shopify_calculators')
sys.path.insert(0, shopify_calculators_path)

# Add stocks directory to path (for stock database tools)
stocks_path = os.path.join(quote_calculator_path, 'stocks')
sys.path.insert(0, stocks_path)

from db_connector import InHousePrintDB
from complete_calculator_implementation import ComprehensiveQuoteCalculator
from query_library import QueryLibrary
from stock_database_tools import StockDatabaseTools

# Import Shopify calculator classes (October 2025)
# Note: These match pricing from inhouseprint.com.au Shopify store
from WireBound_Shopify_Calculator import WireBoundShopifyCalculator
from SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator
from PerfectBound_Shopify_Calculator import PerfectBoundShopifyCalculator
from EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator
from FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator

# Import Shopify-specific calculators with unique pricing quirks
from PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator


class ToolUseAgent:
    """
    Official Tool Use API implementation with comprehensive event capture.
    """
    
    def __init__(self, config_path: str, log_callback: Optional[callable] = None):
        """
        Initialize agent with database, calculator, and AI client.
        
        Args:
            config_path: Path to database-config.json
            log_callback: Optional callback function for streaming logs to UI
                          Signature: log_callback(log_entry: dict) -> None
        """
        
        # Load config
        config_full_path = os.path.join(quote_calculator_path, '..', '..', config_path)
        with open(config_full_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize connections
        self.db = InHousePrintDB(config_full_path)
        self.calculator = ComprehensiveQuoteCalculator(self.db)
        self.query_library = QueryLibrary(self.db)  #  NEW: Query library
        self.stock_tools = StockDatabaseTools()  #  NEW: Stock database tools
        # Path to stocks folder (contains stock_data.db)
        self.stocks_path = stocks_path
        self.anthropic_client = Anthropic(api_key=self.config['AI']['AnthropicAPIKey'])
        self.model = self.config['AI']['Model']
        
        # Store callback for streaming logs
        self.log_callback = log_callback
        
        # Event capture
        self.captured_events = []
        self.citations = []
        
        # Setup exports - save to AI_Quotes folder
        self.exports_dir = os.path.join(os.path.dirname(__file__), '..', 'exports', 'AI_Quotes')
        os.makedirs(self.exports_dir, exist_ok=True)
        
        # Setup log file for complete terminal output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(self.exports_dir, f"ai_quote_session_{timestamp}.log")
        self.log_file = open(self.log_file_path, 'w', encoding='utf-8')
        
        print(f"[OK] Tool Use Agent initialized")
        print(f"   - Database: Connected")
        print(f"   - Calculator: Ready")
        print(f"   - AI: {self.model} with Extended Thinking + Interleaved Thinking")
        print(f"   - Event logs: {self.exports_dir}")
        print(f"   - Session log: {self.log_file_path}")
        
        # Log initialization
        self._log_to_file(f"{'='*100}")
        self._log_to_file(f"AI QUOTE AGENT SESSION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log_to_file(f"{'='*100}\n")
    
    def process_files_to_content_blocks(self, files) -> List[Dict[str, Any]]:
        """
        Convert Flask file uploads to Anthropic content blocks format.
        
        Supports:
        - PDFs: application/pdf → document type
        - Images: image/jpeg, image/png, image/gif, image/webp → image type
        
        Args:
            files: List of FileStorage objects from request.files.getlist('files')
        
        Returns:
            List of content blocks in Anthropic format:
            [
                {
                    "type": "document",  # or "image"
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",  # or "image/jpeg", etc.
                        "data": "base64_encoded_string"
                    }
                }
            ]
        """
        import base64
        
        content_blocks = []
        
        for file in files:
            # Read file bytes
            file_bytes = file.read()
            
            # Encode to base64
            base64_data = base64.b64encode(file_bytes).decode('utf-8')
            
            # Determine content type and media type
            filename = file.filename.lower()
            content_type = file.content_type or ""
            
            # Map to Anthropic content block type
            if content_type == "application/pdf" or filename.endswith('.pdf'):
                block_type = "document"
                media_type = "application/pdf"
            elif content_type.startswith("image/") or filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                block_type = "image"
                # Determine specific image type
                if "jpeg" in content_type or filename.endswith(('.jpg', '.jpeg')):
                    media_type = "image/jpeg"
                elif "png" in content_type or filename.endswith('.png'):
                    media_type = "image/png"
                elif "gif" in content_type or filename.endswith('.gif'):
                    media_type = "image/gif"
                elif "webp" in content_type or filename.endswith('.webp'):
                    media_type = "image/webp"
                else:
                    media_type = "image/jpeg"  # Default fallback
            else:
                # Unsupported file type - skip
                self._print_and_log(f"⚠️ Skipping unsupported file type: {filename} ({content_type})")
                continue
            
            # Create content block
            content_block = {
                "type": block_type,
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64_data
                }
            }
            
            content_blocks.append(content_block)
            self._print_and_log(f" Processed file: {filename} → {block_type} ({media_type})")
        
        return content_blocks
    
    def _log_to_file(self, message: str):
        """Write message to log file."""
        if hasattr(self, 'log_file') and self.log_file:
            self.log_file.write(message + '\n')
            self.log_file.flush()
    
    def _print_and_log(self, message: str):
        """Print to terminal AND log to file."""
        # Windows cp1252 console can't handle Unicode emoji - strip them for console output
        # But keep them in the log file (UTF-8)
        try:
            # Try printing with ASCII-safe version
            printable_message = message.encode('ascii', errors='ignore').decode('ascii')
            print(printable_message)
        except:
            # Fallback: just print without emoji
            print(message.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))
        
        # Log file uses UTF-8, can handle emoji
        self._log_to_file(message)
    
    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Define ALL tools (client + server) following official API spec.
        Reference: API_EVENT_STRUCTURES.md section 1
        """
        return [
            # CLIENT TOOL 1: Get calculator requirements
            {
                "name": "get_calculator_requirements",
                "description": "Get the required parameters for a specific product type from the quote calculator. This tells you what information you need to collect before calculating a quote.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "product_type": {
                            "type": "string",
                            "enum": ["business_cards", "economical_business_cards", "premium_business_cards_shopify", "flyers", "folded_flyers", "wire_bound_books", "spiral_bound_books", "perfect_bound_books", "booklets", "letterheads", "corflute_signs"],
                            "description": "The type of product to get requirements for. BUSINESS CARDS: business_cards = Premium cards (Shopify exact pricing), economical_business_cards = Budget cards (F1-F6 fields, artwork setup, 10% GST), premium_business_cards_shopify = SHOPIFY Premium cards (F1-F7 fields with celloglaze, dual profit structure, DOUBLE GST). FLYERS: flyers = Regular flat flyers (GOD calculator, database-driven, optional folding), folded_flyers = Folded brochures (Shopify hardcoded, F1-F8 fields, MANDATORY folding with setup cost, size-based profit margins). BOOK BINDING TYPES (Shopify calculators): wire_bound_books = Metal wire coil binding (F1-F14 fields, 14 binding tiers, 15% GST + $44 surcharge), spiral_bound_books = Plastic spiral coil binding (F1-F14 fields, 17 binding tiers, 15% GST + $44 surcharge), perfect_bound_books = Glued square spine binding (F1-F11 fields, quantity-based binding, 10% GST only). STATIONERY: letterheads = Letterheads/stationery printing (simplified flyer calculator). corflute_signs = Corflute signs with Shopify tier-based pricing."
                        }
                    },
                    "required": ["product_type"]
                }
            },
            
            # CLIENT TOOL 2: Execute SQL query
            {
                "name": "execute_sql",
                "description": """Execute SQL query against InHousePrint database (SQL Server FredDEV).

🔥 **VERIFIED DATABASE SCHEMA (Based on Live Database Exploration):**

**KEY TABLES - CORRECT STRUCTURE:**

**Orders:**
• OrderID, ClientName (NOT Customer.Name!), OrderDate, CustomerMYOB_ID
• NOTE: NO TotalPrice column! Use jt.Cost for job ticket pricing

**JobTickets:**
• TicketID, OrderID, ShortJobDesc, JobTypeID, PaperTypeID, GSM_ID, QTY, Cost
• TicketNotes (NOT "Note"!), Pages (often NULL!), BindTypeID (often NULL!)
• RingBind, PerfectBind, StitchYes, Books (Boolean flags)
• FrontCelloMatt, FrontCelloGloss, BackCelloMatt, BackCelloGloss, FoldDesc
• ColourStatus (NOT ColourStatusID!) - FK to ColourStatus.ColourID

**PaperSize - CRITICAL CORRECTION:**
• SizeID, [Desc] ONLY - NO Width/Height columns!
• Sample data: SizeID=3 → [Desc]="BC - 90x55", SizeID=4 → "A5", SizeID=9 → "A4"
• ⚠️ Dimensions must be parsed from ps.[Desc] or jt.TicketNotes!

**BindType - DIFFERENT from other lookup tables:**
• BindID (NOT BindTypeID!), BindTypeDesc (NOT [Desc]!)
• Sample data: BindID=7 → BindTypeDesc="Plastic Spiral", BindID=3 → "Perfect Bound"
• ⚠️ JOIN: LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID

**ColourStatus - NOT about print colors!**
• ColourID, ColourDesc, ColourValue, OrderPriority
• This is PRODUCTION URGENCY ("Before Lunch Today", "48 Hour", etc.)
• NOT color mode (B&W, CMYK) - that info is in TicketNotes!
• ⚠️ JOIN: LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID

**JobType, PaperType, GSM - Standard lookup tables:**
• JobType: JobTypeID, [Desc]
• PaperType: PaperTypeID, [Desc]
• GSM: GSM_ID, [DESC] (uppercase!)

** CORRECT QUERY TEMPLATE (Based on Live Database):**

SELECT TOP 20
    -- Identifiers
    jt.TicketID,
    jt.ShortJobDesc AS JobDescription,
    o.ClientName,
    o.OrderDate,
    
    -- Quantities and Costs
    jt.QTY AS Quantity,
    jt.Cost AS JobTicketCost,
    jt.Pages,  -- Often NULL! Parse from TicketNotes instead
    
    -- ⭐ PRIMARY SOURCE OF TRUTH
    jt.TicketNotes AS ProductionNotes,  --  NOT "Note"! Contains FULL specifications
    
    -- Paper Size (parse for dimensions!)
    ps.[Desc] AS PaperSize,  -- "A6", "A4", "BC - 90x55", "DL"
    
    -- Job Details
    jtype.[Desc] AS JobType,
    pt.[Desc] AS PaperType,
    gsm.[DESC] AS GSMValue,
    
    -- Binding (often NULL - check TicketNotes!)
    bt.BindTypeDesc AS BindType,  --  NOT bt.[Desc]!
    jt.RingBind,
    jt.PerfectBind,
    jt.StitchYes,
    jt.Books,
    
    -- Finishing
    jt.FrontCelloMatt,
    jt.FrontCelloGloss,
    jt.BackCelloMatt,
    jt.BackCelloGloss,
    jt.FoldDesc
    
FROM JobTickets jt
JOIN Orders o ON jt.OrderID = o.OrderID
JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID  --  Join on SizeID!
LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID  --  Join on BindID!
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID  --  Production urgency

WHERE o.ClientName LIKE '%[CustomerName]%'
  -- AND jt.ShortJobDesc LIKE '%keyword%'
  -- AND jt.QTY BETWEEN 900 AND 1100
ORDER BY o.OrderDate DESC

**🔥 CRITICAL CORRECTIONS:**
 ps.Width, ps.Height - These columns DON'T EXIST!
 ps.[Desc] - Use this: "BC - 90x55", "A4", "A5", "DL"
 Parse dimensions from jt.TicketNotes: "90mm x 55mm", "Trim size: A6"

 bt.[Desc] - BindType uses BindTypeDesc!
 bt.BindTypeDesc - Correct column name

 jt.ColourStatusID - Doesn't exist!
 jt.ColourStatus - FK to ColourStatus.ColourID

 jt.Note - Doesn't exist!
 jt.TicketNotes - Primary source of truth

**RESERVED KEYWORDS - ALWAYS USE SQUARE BRACKETS:**
• JobType.[Desc] NOT JobType.Desc
• PaperType.[Desc] NOT PaperType.Desc
• GSM.[DESC] NOT GSM.DESC (uppercase!)
• PaperSize.[Desc] NOT PaperSize.Desc
• [Order] NOT Order (table name is reserved keyword)
• ⚠️ BindType is DIFFERENT: Use bt.BindTypeDesc (no brackets needed)

**📋 REAL-WORLD EXAMPLES FROM DATABASE:**

**Example 1: Gerardo Poli - MiniVet Guide (1000 units, $9,444.07)**
```sql
TicketNotes: "Black Plastic Spiral Bound
Cover 300gsm Matt Art Card Gloss celloglazed
Clear plastic front and back"
PaperType: "White Bond"
GSM: "100"
BindTypeDesc: "Plastic Spiral"
QTY: 1000
Date: 2025-07-02
```

**Example 2: Gerardo Poli - Emergency VG (2000 units, $19,140.04)**
```sql
TicketNotes: "Trim size: A6 (scale file down from A4) 
Content stock: 100GSM uncoated B&W 
Page count: 430 
Cover stock: 300gsm Matt Art Card 
Cello: Gloss 
Clear plastic front and back"
PaperType: "Mixed"
GSM: "Mixed"
BindTypeDesc: "Plastic Spiral"
QTY: 2000
Date: 2024-03-27
```

**Example 3: Business Card - Matt Cello ($104.50 for 500)**
```sql
TicketNotes: "Business Cards - Double sided
90mm x 55mm
350gsm Satin
Full Colour
Matt Cello Both Sides
1 x artwork"
JobType: "Business Cards - Double Sided"
PaperType: "Satin"
GSM: "350"
FrontCelloMatt: TRUE
BackCelloMatt: TRUE
Date: 2025-10-03
```

**SEARCH STRATEGIES:**
• For product type: WHERE jt.ShortJobDesc LIKE '%keyword%'
• Extract keywords: business card, flyer, booklet, A4, DL, 6pp, 350gsm, etc.
• For client: WHERE o.ClientName LIKE '%ClientName%'  (use LIKE for partial match!)
• When structured columns NULL: Parse jt.TicketNotes field for specifications
• Always ORDER BY o.OrderDate DESC for most recent first
• Use TOP 20 or TOP 50 to limit results

**WORKFLOW:**
1. FIRST: Call get_calculator_requirements(product_type) for complete guidance
2. Query database with correct SQL structure (verified above)
3. Extract specifications from TicketNotes (primary source!)
4. Map to calculator parameters using guidance from step 1
5. Calculate quote with validated parameters""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL SELECT query. CRITICAL: Use [Order] with square brackets! Use Client.Name for company name. Use TOP N to limit results. Join [Order].ClientID to Client.ContactID."
                        }
                    },
                    "required": ["query"]
                }
            },
            
            # CLIENT TOOL 3: Calculate quote
            {
                "name": "calculate_quote",
                "description": "Calculate a quote using the comprehensive quote calculator. You must provide ALL required parameters for the product type. Returns detailed quote with cost breakdown.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "product_type": {
                            "type": "string",
                            "enum": ["business_cards", "economical_business_cards", "premium_business_cards_shopify", "flyers", "folded_flyers", "wire_bound_books", "spiral_bound_books", "perfect_bound_books", "booklets", "letterheads", "corflute_signs"],
                            "description": "The type of product to calculate. BUSINESS CARDS: business_cards = Premium cards (Shopify exact pricing), economical_business_cards = Budget cards (EconomicalBusinessCards_Shopify_Calculator), premium_business_cards_shopify = SHOPIFY Premium cards (PremiumBusinessCards_Shopify_Calculator with DOUBLE GST). FLYERS: flyers = Regular flat flyers (GOD calculator, database-driven, optional folding), folded_flyers = Folded brochures (Shopify hardcoded, F1-F8 fields, MANDATORY folding with setup cost, size-based profit margins). BOOK BINDING TYPES (Shopify calculators - October 2025): wire_bound_books = Metal wire coil binding (WireBound_Shopify_Calculator), spiral_bound_books = Plastic spiral coil binding (SpiralBound_Shopify_Calculator), perfect_bound_books = Glued square spine binding (PerfectBound_Shopify_Calculator). STATIONERY: letterheads = Letterheads/compliment slips (GOD Flyer algorithm). corflute_signs = Shopify tier-based pricing."
                        },
                        "parameters": {
                            "type": "object",
                            "description": """Product-specific parameters. 
                            
FLYERS: quantity (int), width (int mm), height (int mm), gsm (int), print_side1 (int: 0=none, 1=colour, 2=b&w), print_side2 (int: 0=none, 1=colour, 2=b&w), folding_required (bool), folding_passes (int, default 1), folding_extra_mins (int, default 0), cello_required (bool), cello_side1 (int: 0=none, 1=gloss, 2=matt, 3=soft touch), cello_side2 (int: 0=none, 1=gloss, 2=matt, 3=soft touch).

FOLDED FLYERS (folded_flyers): Shopify Calculator - F1-F8 Fields with MANDATORY folding. quantity (int, F1), print_sides (str, F2: 'Single side print'|'Double side print'), print_type (str, F3: 'Colour'|'Black & White'), finish_size (str, F4: 'A5 - 148mm x 210mm'|'A4 - 210mm x 297mm'|'A3 - 297mm x 420mm'|'6pp A4 - 630mm x 297mm'), paper_stock (str, F5: 'Satin 128GSM'|'Satin 150GSM'|'Satin 250GSM'|'Satin 300GSM'|'Satin 350GSM'|'Uncoated Bond 80GSM'|'Uncoated Bond 90GSM'|'Uncoated Bond 100GSM'), artworks (int, F6: 1-50, default 1, first free then $15 each), fold_type (str, F7: 'Single Fold'|'Double Fold'|'Triple Fold'), celloglaze (str, F8: 'None'|'1 Side Gloss'|'2 Side Gloss'|'1 Side Matt'|'2 Side Matt', only for Satin stocks). Uses FoldedFlyersShopifyCalculator with size-based profit margins (A5: 150%-21%, A4: 160%-21%, A3: 130%-30%, 6pp A4: 120%-33%, different tiers for qty <4000 vs >4000). MANDATORY folding costs: $22 setup + $23 per 1000 folds × fold multiplier (1-3). Celloglaze setup $17, per-sheet cost $0.19-$0.38, ONLY available for Satin stocks. Pricing: NO price increase default + 10% GST + NO surcharge. Cards per sheet calculation based on finish size.

BUSINESS CARDS (PREMIUM): quantity (int), stock_type (str: 'satin_300gsm'|'satin_350gsm'|'kingkong_420gsm'|'ecostar_350gsm'), sides (int: 1 or 2), celloglaze (str: 'none'|'1_side_matt'|'2_side_matt'|'1_side_gloss'|'2_side_gloss'|'1_side_silk'|'2_side_silk'), artworks (int, default 1). 

ECONOMICAL BUSINESS CARDS (economical_business_cards): Shopify Calculator - F1-F6 Fields. quantity (int, F1: 250|500|1000|2000|5000|10000), print_sides (str, F2: 'Single side print'|'Double side print'), print_type (str, F3: 'Colour'|'Black & White'), finish_size (str, F4: '90mm x 55mm' standard only), paper_stock (str, F5: 'Satin 300GSM' standard only), artworks (int, F6: 1-50, default 1, first free then $15 each additional). Uses EconomicalBusinessCardsShopifyCalculator with cards-per-sheet calculation (21 cards per sheet). Pricing: NO price increase default + 10% GST + NO surcharge. BizCost-based profit margins (13 tiers: 50%-90%). Artwork setup: first design free, $15 per additional design. No binding costs - just cutting to finished size.

PREMIUM BUSINESS CARDS SHOPIFY (premium_business_cards_shopify): ⚠️ SHOPIFY-SPECIFIC Calculator - F1-F7 Fields with DUAL PROFIT STRUCTURE. quantity (int, F1: 250|500|1000|2000|5000|10000), print_sides (str, F2: 'Single side print'|'Double side print'), print_type (str, F3: 'Colour'|'Black & White'), finish_size (str, F4: '90mm x 55mm'|'90mm x 45mm'), paper_stock (str, F5: 'Satin 350GSM'|'King Kong High Bulk'|'EcoStar 350GSM Uncoated'), artworks (int, F6: 1-50, default 1), celloglaze (str, F7: 'None'|'1 Side Gloss'|'2 Side Gloss'|'1 Side Matt'|'2 Side Matt'|'1 Side SILK FEEL Matt'|'2 Side SILK FEEL Matt'). Uses PremiumBusinessCardsShopifyCalculator. CRITICAL FEATURES: DUAL profit margins (120% without celloglaze, 30%-90% with celloglaze), celloglaze setup $17, per-sheet costs ($0.16-$0.64), DOUBLE GST APPLICATION (Total * 1.1 * 1.1 = 21% total tax - Shopify quirk). Premium stocks: Satin 350GSM ($180/1000), King Kong 420GSM ($300/1000), EcoStar 350GSM ($500/1000). Cards per sheet: 21 (90x55mm) or 30 (90x45mm). Artwork setup added AFTER margin calculation.

BOOKLETS: quantity (int), width (int mm), height (int mm), pages (int, total pages including cover), stock_type_id (int, internal pages stock type), internal_gsm (int, internal pages GSM), internal_print_mode (int: 1=B&W, 2=Color), hard_cover (bool, IMPORTANT: true=separate cover stock with cello option, false=self-cover using internal stock, default false), cover_stock_type_id (int, cover stock type - required if hard_cover=true), cover_gsm (int, cover GSM - required if hard_cover=true), cover_side1 (int: 0=none, 1=color, 2=b&w), cover_side2 (int: 0=none, 1=color, 2=b&w), cello_required (bool), cello_side1 (int: 0=none, 1=gloss, 2=matt), cello_side2 (int: 0=none, 1=gloss, 2=matt), is_scored (bool, default false), discount (decimal, default 0). NOTE: hard_cover parameter controls whether booklet uses SEPARATE cover stock (not binding method). For saddle stitch with separate cover (e.g., 300GSM Satin cover with cello on 100GSM internal pages), use hard_cover=true.

LETTERHEADS (letterheads): GOD Flyer Calculator - Simplified stationery printing. quantity (int), width (int mm, default 210 for A4), height (int mm, default 297 for A4), gsm (int, typically 100-120gsm Uncoated), print_side1 (int: 0=none, 1=colour, 2=b&w), print_side2 (int: 0=none, 1=colour, 2=b&w, typically 0 for letterheads), discount (decimal, default 0). Uses GOD Flyer algorithm without folding or celloglaze. Most common: 100GSM Uncoated, single-sided color, A4 size, 500-1000 quantity. Used for: letterheads, compliment slips, memo pads, basic stationery.

WIRE BOUND BOOKS (wire_bound_books): Shopify Calculator - F1-F14 Fields. quantity (int, F1), artworks (int, F2: number of different artwork designs, default 1, first free then $15 each), finish_size (str, F14: 'A5 Portrait'|'A5 Landscape'|'A4 Portrait'|'A4 Landscape'|'DL Portrait'|'DL Landscape'|'A6 Portrait'), outer_front_pvc (str, F3: 'None'|'Clear PVC'), printed_front_cover_stock (str, F4: 'Satin 300GSM'|'Satin 350GSM'|'Uncoated Bond 300GSM'), printed_front_cover_print (str, F5: 'Full Colour'|'Black & White'), printed_front_cover_cello (str, F6: 'None'|'Gloss Celloglaze'|'Matt Celloglaze'), outer_back_pvc (str, F7: 'None'|'Clear PVC'|'Black Leather Look'), printed_back_cover_stock (str, F8: 'Satin 300GSM'|'Satin 350GSM'|'Uncoated Bond 300GSM'), printed_back_cover_print (str, F9: 'Full Colour'|'Black & White'), printed_back_cover_cello (str, F10: 'None'|'Gloss Celloglaze'|'Matt Celloglaze'), internal_pages (int, F11: 20-500 pages, must be even), internal_stock (str, F12: 'Uncoated Bond 80GSM'|'Uncoated Bond 100GSM'|'Satin 128GSM'|'Satin 150GSM'), internal_print (str, F13: 'Black & White'|'Full Colour'). Uses WireBoundShopifyCalculator with 14 thickness-based binding tiers. Pricing: 5% price increase + 15% GST + $44 surcharge. Layered cover structure: PVC overlay + Printed cover + Celloglaze finish (separate for front/back).

SPIRAL BOUND BOOKS (spiral_bound_books): Shopify Calculator - F1-F14 Fields. SAME parameters as Wire Bound (quantity, artworks, finish_size, outer_front_pvc, printed_front_cover_stock, printed_front_cover_print, printed_front_cover_cello, outer_back_pvc, printed_back_cover_stock, printed_back_cover_print, printed_back_cover_cello, internal_pages, internal_stock, internal_print). KEY DIFFERENCE: Uses SpiralBoundShopifyCalculator with 17 thickness-based binding tiers (vs Wire's 14 tiers). Pricing: 5% price increase + 15% GST + $44 surcharge. Additional internal stock options: 'Uncoated Bond 140GSM', 'Satin 300GSM'. Layered cover structure same as Wire Bound.

PERFECT BOUND BOOKS (perfect_bound_books): Shopify Calculator - F1-F11 Fields. quantity (int, F1), printed_pages (int, F2: 40-800 pages, must be divisible by 4), proof_requirements (str, F3: 'Digital Emailed Proof' $0|'Physical Unbound Proof' $40), cover_stock (str, F4: 'Satin 300GSM'), cover_print_type (str, F5: '1 side colour (4pp)'|'2 side colour (4pp)'|'1 side Black & White (4pp)'|'2 side Black & White (4pp)'), celloglaze (str, F6: 'None'|'Gloss outside only'|'Matt outside only'), finish_size (str, F8: 'A5 Portrait'|'A4 Portrait'|'A4 Landscape'|'US Trade - 152mm x 229mm'|'B-Format - 198mm x 129mm'), content_print_type (str, F10: 'Full Colour'|'Black & White'), content_stock_type (str, F11: 'Satin 128GSM'|'Satin 150GSM'|'Uncoated Bond 80GSM'|'Uncoated Bond 90GSM'|'Uncoated Bond 100GSM'). Uses PerfectBoundShopifyCalculator with 8 quantity-based binding tiers. Pricing: NO price increase default + 10% GST + NO surcharge. Simple cover structure (not layered): Single printed cover + optional celloglaze finish.

CORFLUTE SIGNS (corflute_signs): size_preset (str: '450x600mm'|'600x900mm'|'900x1200mm'|'1200x2400mm'|'custom'), custom_width_mm (int, required if size_preset='custom'), custom_height_mm (int, required if size_preset='custom'), thickness (str: '3mm'|'5mm', default '5mm'), quantity (int), double_sided (bool, default False), eyelet_option (str: 'none'|'4_corners'|'2_top'|'2_center_lr'|'2_center_tb'|'6_top_bottom'|'6_left_right', default 'none'), cutting_type (str: 'standard'|'custom_shape', default 'standard'), artworks (int, default 1). Shopify tier-based pricing with 43 volume tiers, 5% discount, $135 minimum.

CRITICAL: Use SEPARATE calculators for each binding type - wire_bound_books uses WireBoundShopifyCalculator, spiral_bound_books uses SpiralBoundShopifyCalculator, perfect_bound_books uses PerfectBoundShopifyCalculator. Do NOT use old unified calculate_perfect_bound_book() method.

Get full parameter details from get_calculator_requirements first."""
                        }
                    },
                    "required": ["product_type", "parameters"]
                }
            },
            
            # CLIENT TOOL: Get available BI queries from library
            {
                "name": "get_available_queries",
                "description": """Get list of available pre-built business intelligence queries from the query library.

These are optimized, parameterized SQL queries for common business analysis tasks:
- Sales & Revenue Analysis
- Customer Analytics  
- Product Analysis
- Operational Metrics
- Financial Analysis
- Business Division Analysis
- Comparative Analysis

Use this tool to discover what pre-built queries are available before building custom SQL.""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Optional category filter (e.g., 'Sales & Revenue', 'Customer Analytics'). Omit to see all queries.",
                            "enum": ["Sales & Revenue", "Customer Analytics", "Product Analysis", 
                                   "Operational Metrics", "Financial Analysis", "Business Divisions", 
                                   "Comparative Analysis"]
                        }
                    }
                }
            },
            
            # CLIENT TOOL: Get specific query from library
            {
                "name": "get_query_from_library",
                "description": """Get a specific pre-built query from the query library and execute it.

This returns an optimized SQL query with your parameters applied, executes it, and returns the results.

Available queries include:
- sales_trend_by_month: Monthly sales trends with revenue and order counts
- revenue_by_product_type: Revenue breakdown by product category
- revenue_by_customer: Top customers by revenue
- customer_retention_cohort: Customer cohort retention analysis
- customer_lifetime_value: High-value customer identification
- product_performance_detail: Detailed product analytics
- paper_stock_usage: Paper stock usage patterns
- apg_workflow_status: APG production workflow status
- and many more...

Use get_available_queries first to see all options.""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query_name": {
                            "type": "string",
                            "description": "Name of the query from the library (e.g., 'sales_trend_by_month')"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Query parameters (e.g., {\"months\": 6, \"top_n\": 20}). Each query has different parameters - use get_available_queries to see required parameters for each query."
                        }
                    },
                    "required": ["query_name"]
                }
            },
            
            # CLIENT TOOL: Query stock levels
            {
                "name": "query_stock_levels",
                "description": """Query current stock levels from the inventory management system.

Returns stock levels with status indicators (critical, low, ok) for paper stocks including:
- Current stock levels, reorder points, critical levels
- Stock type, GSM, dimensions, colour
- Supplier information and location codes
- Cost per thousand and markup percentages

Supports filtering by:
- stock_type: Filter by stock description (e.g., "Satin", "Gloss", "Bond")
- gsm: Filter by paper weight (e.g., 300, 350, 128)
- status: Filter by stock status ("critical", "low", "ok")
- min_level/max_level: Filter by stock quantity range

Use this to check inventory before processing large orders or calculating quotes.""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": "Optional filters: stock_type (string), gsm (integer), status (string: 'critical'|'low'|'ok'), min_level (integer), max_level (integer)",
                            "properties": {
                                "stock_type": {
                                    "type": "string",
                                    "description": "Filter by stock type (e.g., 'Satin', 'Gloss', 'Bond')"
                                },
                                "gsm": {
                                    "type": "integer",
                                    "description": "Filter by GSM weight (e.g., 300, 350, 128)"
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["critical", "low", "ok"],
                                    "description": "Filter by stock status"
                                },
                                "min_level": {
                                    "type": "integer",
                                    "description": "Minimum stock level"
                                },
                                "max_level": {
                                    "type": "integer",
                                    "description": "Maximum stock level"
                                }
                            }
                        }
                    }
                }
            },
            
            # CLIENT TOOL: Get stock transactions
            {
                "name": "get_stock_transactions",
                "description": """Get stock transaction history from the inventory system.

Returns transaction records including:
- Transaction type (PURCHASE, CONSUMPTION, ADJUSTMENT, RETURN)
- Quantity changes (positive for additions, negative for consumption)
- Transaction dates and timestamps
- Reasons and reference numbers (job tickets, orders, POs)
- Stock type and GSM information

Use this to:
- Audit stock movements and consumption patterns
- Track production material usage
- Investigate stock discrepancies
- Review purchase history""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "stock_id": {
                            "type": "integer",
                            "description": "Optional: Filter transactions for specific stock ID"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of records to return (default: 50)",
                            "default": 50
                        }
                    }
                }
            },
            
            # CLIENT TOOL: Get reorder alerts
            {
                "name": "get_reorder_alerts",
                "description": """Get active stock reorder alerts from the inventory system.

Returns alerts for stocks that are:
- CRITICAL: At or below critical level (immediate action required)
- WARNING: At or below reorder point (should reorder soon)

Each alert includes:
- Stock type, GSM, current level
- Critical and reorder point thresholds
- Alert date and resolution status
- Supplier information for reordering

Use this to:
- Monitor stock shortages
- Plan purchase orders
- Prioritize stock replenishment
- Avoid production delays""",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            
            # CLIENT TOOL: Update stock level
            {
                "name": "update_stock_level",
                "description": """Update stock level in the inventory system and create transaction record.

⚠️ IMPORTANT: This modifies inventory data - use carefully!

Updates stock level and automatically:
- Creates transaction record with reason and reference
- Checks if reorder alerts need to be triggered
- Updates last modified timestamp
- Calculates quantity change from old to new level

Transaction types:
- ADJUSTMENT: Manual corrections or additions (positive change)
- CONSUMPTION: Material usage or waste (negative change)

Use this for:
- Manual stock adjustments after physical counts
- Recording stock consumption after production runs
- Correcting inventory discrepancies
- Adding new stock receipts

⚠️ NOTE: Updates temp database only (not production pricing database)""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "stock_id": {
                            "type": "integer",
                            "description": "Stock ID to update"
                        },
                        "new_level": {
                            "type": "integer",
                            "description": "New stock level (sheets/units)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update (e.g., 'Manual adjustment', 'Production consumption', 'Physical count correction')"
                        },
                        "reference": {
                            "type": "string",
                            "description": "Optional reference (e.g., job ticket number, order ID, PO number)"
                        }
                    },
                    "required": ["stock_id", "new_level", "reason"]
                }
            },
            
            # CLIENT TOOL: Get production pricing
            {
                "name": "get_production_pricing",
                "description": """Query production pricing data from SQL Server database.

Returns pricing information for digital printing stocks:
- Stock ID, type, and description
- Sheet dimensions (length x width in mm)
- GSM (paper weight)
- Cost per thousand sheets
- Markup percentage
- Calculated sell price per thousand

This is the REAL production pricing data (not demo/temp data).

⚠️ NOTE: This table has ONLY 7 columns (StockID, StockTypeID, Length, Width, GSM, CostPerThousand, Markup).
It does NOT have inventory management columns (CurrentStockLevel, ReorderPoint, etc.).
Use query_stock_levels for inventory data.

Use this for:
- Getting accurate production costs for quotes
- Comparing pricing across stock types
- Analyzing cost structures
- Validating calculator pricing""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": "Optional filters: gsm (integer), stock_type_id (integer)",
                            "properties": {
                                "gsm": {
                                    "type": "integer",
                                    "description": "Filter by GSM weight"
                                },
                                "stock_type_id": {
                                    "type": "integer",
                                    "description": "Filter by stock type ID"
                                }
                            }
                        }
                    }
                }
            },
            
            # CLIENT TOOL: Update stock record in unified_stocks table
            {
                "name": "update_stock_record",
                "description": """Update a stock record in the unified_stocks table of SQLite stock_data.db.

Use this to modify stock information such as:
- Pricing (cost_per_thousand, cost_per_sqm, markup)
- Supplier information (supplier_name, product_code, brand_name)
- Stock levels (current_stock_level, reorder_point, critical_level)

**IMPORTANT RULES:**
1. ALWAYS confirm with user before updating
2. Stock ID must exist (will validate)
3. Use proper data types (numbers for costs, dates as 'YYYY-MM-DD')

**Example:** stock_id=44, updates={"cost_per_thousand": 145.00}
""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "stock_id": {
                            "type": "string",
                            "description": "Stock ID to update (e.g., '44', 'T1', 'R5')"
                        },
                        "updates": {
                            "type": "object",
                            "description": "Dictionary of column names and new values"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update (audit trail)"
                        }
                    },
                    "required": ["stock_id", "updates", "reason"]
                }
            },
            
            # CLIENT TOOL: Update job record in extracted_jobs table
            {
                "name": "update_job_record",
                "description": """Update a job ticket record in the extracted_jobs table of SQLite stock_data.db.

Use this to modify job ticket information such as:
- Stock assignment (stock_id) - Assign correct stock after analysis
- Quantities (quantity, sheets_required)
- Job details (product_type, job_description, finishing_details)
- Client info (client_name, industry)
- Pricing (total_estimated_value, estimated_profit)

**IMPORTANT RULES:**
1. ALWAYS confirm with user before updating
2. Ticket ID must exist (will validate)
3. Use proper data types (numbers for quantities, dates as 'YYYY-MM-DD')

**Example:** ticket_id=71584, updates={"stock_id": "44", "sheets_required": 5000}
""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Job ticket ID to update (e.g., '71584')"
                        },
                        "updates": {
                            "type": "object",
                            "description": "Dictionary of column names and new values"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update (audit trail)"
                        }
                    },
                    "required": ["ticket_id", "updates", "reason"]
                }
            },
            
            # CLIENT TOOL: Query AI-extracted jobs from SQLite stock database
            {
                "name": "query_ai_extracted_jobs",
                "description": """Query AI-extracted job data from stock_data.db SQLite database (READ-ONLY).

The `extracted_jobs` table contains 219 jobs extracted by AI with rich business intelligence:

**Table Schema (31 columns):**
- **Identification**: ticket_id (unique), order_id, order_date
- **Client**: client_name, industry (14 industries), client_type, suburb
- **Stock**: stock_type (19 types: uncoated, satin, linen, corflute, etc.), stock_description, gsm, paper_finish, sheet_size, length_mm, width_mm
- **Quantities**: quantity_ordered, total_sheets_consumed (44,751 total), sheets_per_item
- **Job Details**: job_description, product_type (booklets, brochures, corflute, pads), finishing_notes
- **Pricing**: total_estimated_value, estimated_profit, profit_margin_percent, stock_cost_estimate
- **AI Metadata**: extraction_confidence (0.92-0.98), ai_model, extraction_timestamp
- **Raw Data**: json_data (full JSON blob)

**Current Data:**
- 219 jobs from tickets #72487-72799
- Date range: 2025-09-22 to 2025-10-10
- 44,751 sheets consumed across 19 stock types
- 14 industries tracked

**Top Stock Types by Usage:**
1. uncoated: 25,448 sheets (11 jobs)
2. satin: 17,491 sheets (59 jobs)
3. linen: 1,100 sheets (14 jobs)
4. corflute: 711 sheets (39 jobs)

**Example Queries:**
- SELECT stock_type, SUM(total_sheets_consumed) FROM extracted_jobs GROUP BY stock_type
- SELECT industry, COUNT(*), AVG(extraction_confidence) FROM extracted_jobs GROUP BY industry
- SELECT * FROM extracted_jobs WHERE gsm > 300 AND stock_type = 'satin'
- SELECT client_name, SUM(total_sheets_consumed) FROM extracted_jobs GROUP BY client_name ORDER BY SUM(total_sheets_consumed) DESC LIMIT 10

Use this for:
- Stock consumption analysis by type, GSM, client, industry
- Business intelligence reporting
- Client pattern analysis
- Geographic analysis by suburb
- Quality assurance (extraction_confidence)""",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sql_query": {
                            "type": "string",
                            "description": "SQL query to execute against extracted_jobs table in stock_data.db"
                        }
                    },
                    "required": ["sql_query"]
                }
            },
            
            # SERVER TOOL: Web search (Anthropic executes this)
            # Note: For job extraction with 20+ jobs, allow 1 search per unique business
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 25,  # Increased from 5 to allow 1 search per business (for ~20 job batch)
                "user_location": {
                    "type": "approximate",
                    "city": "Brisbane",
                    "region": "Queensland",
                    "country": "AU",
                    "timezone": "Australia/Brisbane"
                }
            }
        ]
    
    def _log_event(self, event_type: str, data: Any):
        """Capture and log all events for debugging."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        self.captured_events.append(event)
        
        # Send to callback if provided (for web UI streaming)
        if self.log_callback:
            try:
                self.log_callback(event)
            except Exception as e:
                # Don't let callback errors break the agent
                print(f"Warning: log_callback error: {e}")
        
        # Print to terminal AND log file with clear formatting
        self._print_and_log(f"\n{'='*80}")
        self._print_and_log(f"📡 EVENT: {event_type}")
        self._print_and_log(f"{'='*80}")
        self._print_and_log(json.dumps(data, indent=2, default=str))
        self._print_and_log(f"{'='*80}\n")
    
    def _execute_client_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute CLIENT tools (run on our system).
        Reference: API_EVENT_STRUCTURES.md section 4
        """
        self._print_and_log(f"\n{'='*80}")
        self._print_and_log(f"🔧 EXECUTING CLIENT TOOL: {tool_name}")
        self._print_and_log(f"{'='*80}")
        self._print_and_log(f"INPUT:")
        self._print_and_log(json.dumps(tool_input, indent=2))
        self._print_and_log("")
        
        try:
            if tool_name == "get_calculator_requirements":
                product_type = tool_input["product_type"]
                result = self.calculator.get_calculator_requirements(product_type)
                
                # CRITICAL FIX: Convert Decimal types to JSON-serializable formats
                # Calculator returns Decimal values for pricing that must be converted
                def convert_to_json_serializable(obj):
                    """Convert Decimal, datetime, and other types to JSON-serializable formats"""
                    if isinstance(obj, list):
                        return [convert_to_json_serializable(item) for item in obj]
                    elif isinstance(obj, dict):
                        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
                    elif isinstance(obj, (int, float, str, bool, type(None))):
                        return obj
                    else:
                        # Convert Decimal, datetime, etc. to string
                        return str(obj)
                
                json_safe_result = convert_to_json_serializable(result)
                
                self._print_and_log(f" RESULT:")
                self._print_and_log(json.dumps(json_safe_result, indent=2))
                
                result_data = {
                    "success": True,
                    "product_type": product_type,
                    "requirements": json_safe_result
                }
                
                # Emit client_tool_execution event
                self._log_event("client_tool_execution", {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "result": result_data,
                    "summary": f"Retrieved calculator requirements for {product_type}"
                })
                
                return result_data
            
            elif tool_name == "execute_sql":
                query = tool_input["query"]
                self._print_and_log(f"SQL QUERY:")
                self._print_and_log(query)
                self._print_and_log("")
                
                df = self.db.execute_query(query)
                records = df.to_dict('records')
                
                # CRITICAL FIX: Convert all values to JSON-serializable types
                # This handles Decimal, datetime, and other non-JSON types
                def convert_to_json_serializable(obj):
                    """Convert Decimal, datetime, and other types to JSON-serializable formats"""
                    if isinstance(obj, list):
                        return [convert_to_json_serializable(item) for item in obj]
                    elif isinstance(obj, dict):
                        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
                    elif isinstance(obj, (int, float, str, bool, type(None))):
                        return obj
                    else:
                        # Convert Decimal, datetime, etc. to string
                        return str(obj)
                
                json_safe_records = convert_to_json_serializable(records)
                
                self._print_and_log(f" RESULT: {len(json_safe_records)} rows")
                # Print ALL records without truncation
                self._print_and_log(json.dumps(json_safe_records, indent=2, default=str))
                
                result_data = {
                    "success": True,
                    "row_count": len(json_safe_records),
                    "data": json_safe_records
                }
                
                # Emit client_tool_execution event
                self._log_event("client_tool_execution", {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "result": result_data,
                    "summary": f"SQL query returned {len(json_safe_records)} rows"
                })
                
                return result_data
            
            elif tool_name == "calculate_quote":
                product_type = tool_input["product_type"]
                params = tool_input["parameters"]
                
                # FIX: Handle both JSON string and dict parameters (Issue #1 - Dec 8, 2025)
                # The registry may pass parameters as JSON string instead of dict object
                # This caused 100% failure rate with 'str' object has no attribute 'items' error
                if isinstance(params, str):
                    try:
                        params = json.loads(params)
                        self._print_and_log(f"✅ Deserialized parameters from JSON string")
                    except json.JSONDecodeError as e:
                        error_msg = f"Invalid JSON in parameters: {str(e)}"
                        self._print_and_log(f"❌ {error_msg}")
                        return {
                            "success": False,
                            "error": error_msg,
                            "hint": "Parameters must be valid JSON object/dict"
                        }
                
                # Validate it's now a dict
                if not isinstance(params, dict):
                    error_msg = f"Parameters must be dict or JSON string, got {type(params).__name__}"
                    self._print_and_log(f"❌ {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "hint": "Expected: {...} or '{...}'"
                    }
                
                self._print_and_log(f"PRODUCT: {product_type}")
                self._print_and_log(f"PARAMETERS:")
                self._print_and_log(json.dumps(params, indent=2))
                self._print_and_log("")
                
                # Define supported parameters for each product type
                # Updated Dec 8, 2025: Added Shopify calculator parameters for perfect_bound_books
                supported_params = {
                    "flyers": ["quantity", "width", "height", "gsm", "print_side1", "print_side2", 
                              "folding_required", "folding_passes", "folding_extra_mins",
                              "cello_required", "cello_side1", "cello_side2"],
                    "folded_flyers": ["quantity", "print_sides", "print_type", "finish_size", 
                                     "paper_stock", "artworks", "fold_type", "celloglaze"],
                    "perfect_bound_books": [
                                          # Shopify Calculator Parameters (PerfectBoundShopifyCalculator.calculate)
                                          "quantity", "printed_pages", "proof_requirements", "cover_stock",
                                          "cover_print_type", "celloglaze", "finish_size", "content_print_type",
                                          "content_stock_type",
                                          # Legacy/Documentation Parameters (for backwards compatibility)
                                          "pages", "width", "height", "cover_stock_gsm", 
                                          "inner_gsm", "colour_pages", "binding_type", "book_width", 
                                          "book_height", "stock_type_id", "internal_stock_gsm", 
                                          "internal_print_mode", "cover_stock_type_id", 
                                          "cover_print_mode", "cello_type", "is_scored", "colour_insert_type",
                                          "clear_pvc_front", "clear_pvc_back", "front_cello_type", "back_cello_type"],
                    "booklets": ["quantity", "width", "height", "pages", "stock_type_id", "internal_gsm", 
                                "internal_print_mode", "hard_cover", "cover_stock_type_id", "cover_gsm", 
                                "cover_side1", "cover_side2", "cello_required", "cello_side1", "cello_side2", 
                                "is_scored", "discount"],
                    "business_cards": ["quantity", "stock_type", "sides", "print_type", "finish_size", 
                                      "celloglaze", "artworks"],
                    "corflute_signs": ["size_preset", "custom_width_mm", "custom_height_mm", "thickness",
                                      "quantity", "double_sided", "eyelet_option", "cutting_type", "artworks"]
                }
                
                # ========================================================================
                # PARAMETER ALIASING - Handle common parameter name variations
                # Documentation vs Implementation Mapping (Dec 8, 2025 - Issue #2)
                # ========================================================================
                parameter_aliases = {
                    "cover_gsm": "cover_stock_gsm",  # Booklets use cover_gsm, Books use cover_stock_gsm
                    
                    # Perfect Bound Books - Documentation uses GOD calculator params but routes to Shopify
                    "book_width": None,               # Shopify uses finish_size instead
                    "book_height": None,              # Shopify uses finish_size instead
                    "pages": "printed_pages",         # Documentation says "pages", calculator needs "printed_pages"
                    "cello_type": "celloglaze",       # Documentation uses cello_type (0/1/2), calculator uses celloglaze string
                    "internal_gsm": "content_stock_type",  # GSM value maps to stock type string
                    "cover_gsm": "cover_stock",       # GSM value maps to stock type string
                    "internal_print_mode": "content_print_type",  # mode → type
                    "cover_print_mode": "cover_print_type",       # mode → type
                }
                
                # Apply aliases - if AI uses alias, map to correct parameter name
                for alias, correct_name in parameter_aliases.items():
                    if alias in params:
                        if correct_name is None:
                            # Parameter not used by target calculator - will be filtered out
                            self._print_and_log(f"🔄 PARAMETER ALIAS: '{alias}' not used by Shopify calculator (will filter)")
                        elif correct_name not in params:
                            self._print_and_log(f"🔄 PARAMETER ALIAS: Mapping '{alias}' → '{correct_name}'")
                            params[correct_name] = params.pop(alias)
                
                # ========================================================================
                # INTELLIGENT PARAMETER MAPPING (Dec 8, 2025 - Issue #2)
                # Convert book_width/book_height to finish_size for Shopify calculators
                # ========================================================================
                if product_type == "perfect_bound_books" and ("book_width" in params or "book_height" in params):
                    book_width = params.get("book_width", params.get("width", 148))
                    book_height = params.get("book_height", params.get("height", 210))
                    
                    # Map dimensions to Shopify finish_size options
                    if book_width == 148 and book_height == 210:
                        finish_size = "A5 Portrait"
                    elif book_width == 210 and book_height == 297:
                        finish_size = "A4 Portrait"
                    elif book_width == 297 and book_height == 210:
                        finish_size = "A4 Landscape"
                    elif book_width == 152 and book_height == 229:
                        finish_size = "US Trade (6x9 inches)"
                    else:
                        # Default to A5 for unknown dimensions
                        finish_size = "A5 Portrait"
                        self._print_and_log(f"⚠️ Unknown book dimensions {book_width}x{book_height}mm, defaulting to A5")
                    
                    params["finish_size"] = finish_size
                    self._print_and_log(f"🔄 MAPPED: book dimensions {book_width}x{book_height}mm → finish_size='{finish_size}'")
                    
                    # Remove dimension parameters (not used by Shopify calculator)
                    params.pop("book_width", None)
                    params.pop("book_height", None)
                    params.pop("width", None)
                    params.pop("height", None)
                
                # Filter out unsupported parameters
                if product_type in supported_params:
                    filtered_params = {
                        k: v for k, v in params.items() 
                        if k in supported_params[product_type]
                    }
                    
                    # Log if any parameters were filtered out
                    removed_params = set(params.keys()) - set(filtered_params.keys())
                    if removed_params:
                        self._print_and_log(f"⚠️ FILTERED OUT unsupported parameters: {', '.join(removed_params)}")
                    
                    params = filtered_params
                
                # Call appropriate calculator method
                if product_type == "flyers":
                    quote = self.calculator.calculate_flyers(**params)
                    
                elif product_type == "folded_flyers":
                    # FOLDED FLYERS: Shopify Calculator (October 14, 2025)
                    # Uses FoldedFlyersShopifyCalculator with F1-F8 fields
                    # MANDATORY folding with setup cost, size-based profit margins
                    self._print_and_log(f"🔗 ROUTING: Folded Flyers → FoldedFlyersShopifyCalculator")
                    
                    from FoldedFlyers_Shopify_Calculator import (
                        FoldedFlyersShopifyCalculator,
                        PrintSides, PrintType, FinishSize, PaperStock, FoldType, Celloglaze
                    )
                    from decimal import Decimal
                    
                    folded_calc = FoldedFlyersShopifyCalculator()
                    
                    # Map string parameters to Enums
                    print_sides_map = {
                        'single': PrintSides.SINGLE_SIDE,
                        'double': PrintSides.DOUBLE_SIDE,
                        'single side print': PrintSides.SINGLE_SIDE,
                        'double side print': PrintSides.DOUBLE_SIDE
                    }
                    
                    print_type_map = {
                        'colour': PrintType.COLOUR,
                        'color': PrintType.COLOUR,
                        'black & white': PrintType.BLACK_WHITE,
                        'black and white': PrintType.BLACK_WHITE,
                        'b&w': PrintType.BLACK_WHITE
                    }
                    
                    finish_size_map = {
                        'a5': FinishSize.A5,
                        'a4': FinishSize.A4,
                        'a3': FinishSize.A3,
                        '6pp a4': FinishSize.A4_6PP,
                        'a5 - 148mm x 210mm': FinishSize.A5,
                        'a4 - 210mm x 297mm': FinishSize.A4,
                        'a3 - 297mm x 420mm': FinishSize.A3,
                        '6pp a4 - 630mm x 297mm': FinishSize.A4_6PP
                    }
                    
                    paper_stock_map = {
                        'satin 128gsm': PaperStock.SATIN_128GSM,
                        'satin 150gsm': PaperStock.SATIN_150GSM,
                        'satin 250gsm': PaperStock.SATIN_250GSM,
                        'satin 300gsm': PaperStock.SATIN_300GSM,
                        'satin 350gsm': PaperStock.SATIN_350GSM,
                        'uncoated bond 80gsm': PaperStock.UNCOATED_80GSM,
                        'uncoated bond 90gsm': PaperStock.UNCOATED_90GSM,
                        'uncoated bond 100gsm': PaperStock.UNCOATED_100GSM
                    }
                    
                    fold_type_map = {
                        'single fold': FoldType.SINGLE_FOLD,
                        'double fold': FoldType.DOUBLE_FOLD,
                        'triple fold': FoldType.TRIPLE_FOLD,
                        'single': FoldType.SINGLE_FOLD,
                        'double': FoldType.DOUBLE_FOLD,
                        'triple': FoldType.TRIPLE_FOLD
                    }
                    
                    celloglaze_map = {
                        'none': Celloglaze.NONE,
                        '1 side gloss': Celloglaze.ONE_SIDE_GLOSS,
                        '2 side gloss': Celloglaze.TWO_SIDE_GLOSS,
                        '1 side matt': Celloglaze.ONE_SIDE_MATT,
                        '2 side matt': Celloglaze.TWO_SIDE_MATT
                    }
                    
                    # Extract and map parameters
                    quantity = params.get('quantity', 1000)
                    print_sides = print_sides_map.get(params.get('print_sides', 'double').lower(), PrintSides.DOUBLE_SIDE)
                    print_type = print_type_map.get(params.get('print_type', 'colour').lower(), PrintType.COLOUR)
                    finish_size = finish_size_map.get(params.get('finish_size', 'a4').lower(), FinishSize.A4)
                    paper_stock = paper_stock_map.get(params.get('paper_stock', 'satin 128gsm').lower(), PaperStock.SATIN_128GSM)
                    artworks = params.get('artworks', 1)
                    fold_type = fold_type_map.get(params.get('fold_type', 'single fold').lower(), FoldType.SINGLE_FOLD)
                    celloglaze = celloglaze_map.get(params.get('celloglaze', 'none').lower(), Celloglaze.NONE)
                    
                    result = folded_calc.calculate_quote(
                        quantity=quantity,
                        print_sides=print_sides,
                        print_type=print_type,
                        finish_size=finish_size,
                        paper_stock=paper_stock,
                        artworks=artworks,
                        fold_type=fold_type,
                        celloglaze=celloglaze
                    )
                    
                    # Convert to QuoteResult format for compatibility
                    from complete_calculator_implementation import QuoteResult
                    quote = QuoteResult(
                        product_type="folded_flyers",
                        quantity=result.quantity,
                        cost_to_business=result.biz_cost,
                        profit_margin=result.profit_margin_rate,
                        total_cost_ex_gst=result.subtotal,
                        total_cost_inc_gst=result.final_price,
                        breakdown={
                            'biz_cost': result.biz_cost,
                            'setup_total': result.setup_total,
                            'stock_cost': result.stock_cost,
                            'click_cost': result.click_cost,
                            'cutting_cost': result.cutting_cost,
                            'folding_cost': result.folding_cost,
                            'cello_cost': result.cello_cost,
                            'profit_margin_rate': result.profit_margin_rate,
                            'profit': result.profit,
                            'subtotal': result.subtotal,
                            'gst': result.gst,
                            'final_price': result.final_price
                        },
                        specifications=result.specifications
                    )
                    
                elif product_type == "wire_bound_books":
                    # WIRE BOUND: Shopify Calculator (October 2025)
                    # Uses WireBoundShopifyCalculator with F1-F14 fields
                    # 14 thickness-based binding tiers, 15% GST + $44 surcharge
                    self._print_and_log(f"🔗 ROUTING: Wire Bound Books → WireBoundShopifyCalculator")
                    wire_calc = WireBoundShopifyCalculator()
                    
                    # Extract configurable pricing variables if provided
                    price_increase = params.pop('price_increase_multiplier', None)
                    gst_rate = params.pop('gst_rate', None)
                    surcharge = params.pop('surcharge', None)
                    
                    # Override class variables if custom values provided
                    if price_increase is not None:
                        wire_calc.PRICE_INCREASE_MULTIPLIER = Decimal(str(price_increase))
                        self._print_and_log(f"   💰 Custom price increase: {price_increase}")
                    if gst_rate is not None:
                        wire_calc.GST_RATE = Decimal(str(gst_rate))
                        self._print_and_log(f"   💰 Custom GST rate: {gst_rate}")
                    if surcharge is not None:
                        wire_calc.SURCHARGE = Decimal(str(surcharge))
                        self._print_and_log(f"   💰 Custom surcharge: ${surcharge}")
                    
                    self._print_and_log(f"   📊 Using: {float(wire_calc.PRICE_INCREASE_MULTIPLIER-1)*100:.1f}% price increase, {float(wire_calc.GST_RATE-1)*100:.0f}% GST, ${float(wire_calc.SURCHARGE):.2f} surcharge")
                    
                    result = wire_calc.calculate(**params)
                    
                    # Convert to QuoteResult format for compatibility
                    from complete_calculator_implementation import QuoteResult
                    quote = QuoteResult(
                        product_type="wire_bound_books",
                        quantity=result.quantity,
                        cost_to_business=result.breakdown['biz_cost'],
                        profit_margin=result.breakdown.get('profit_margin_rate', 0),
                        total_cost_ex_gst=result.breakdown['subtotal_with_increase'],
                        total_cost_inc_gst=result.total_price,
                        breakdown=result.breakdown,
                        specifications=result.specifications
                    )
                    
                elif product_type == "spiral_bound_books":
                    # SPIRAL BOUND: Shopify Calculator (October 2025)
                    # Uses SpiralBoundShopifyCalculator with F1-F14 fields
                    # 17 thickness-based binding tiers, 15% GST + $44 surcharge
                    self._print_and_log(f"🔗 ROUTING: Spiral Bound Books → SpiralBoundShopifyCalculator")
                    spiral_calc = SpiralBoundShopifyCalculator()
                    result = spiral_calc.calculate(**params)
                    
                    # Convert to QuoteResult format for compatibility
                    from complete_calculator_implementation import QuoteResult
                    quote = QuoteResult(
                        product_type="spiral_bound_books",
                        quantity=result.quantity,
                        cost_to_business=result.breakdown['biz_cost'],
                        profit_margin=result.breakdown.get('profit_margin_rate', 0),
                        total_cost_ex_gst=result.breakdown['subtotal_with_increase'],
                        total_cost_inc_gst=result.total_price,
                        breakdown=result.breakdown,
                        specifications=result.specifications
                    )
                    
                elif product_type == "perfect_bound_books":
                    # PERFECT BOUND: Shopify Calculator (October 2025)
                    # Uses PerfectBoundShopifyCalculator with F1-F11 fields
                    # 8 quantity-based binding tiers, 10% GST, NO surcharge
                    self._print_and_log(f"🔗 ROUTING: Perfect Bound Books → PerfectBoundShopifyCalculator")
                    perfect_calc = PerfectBoundShopifyCalculator()
                    result = perfect_calc.calculate(**params)
                    
                    # Convert to QuoteResult format for compatibility
                    from complete_calculator_implementation import QuoteResult
                    quote = QuoteResult(
                        product_type="perfect_bound_books",
                        quantity=result.quantity,
                        cost_to_business=result.breakdown['biz_cost'],
                        profit_margin=result.breakdown.get('profit_margin_rate', 0),
                        total_cost_ex_gst=result.breakdown['subtotal_with_increase'],
                        total_cost_inc_gst=result.total_price,
                        breakdown=result.breakdown,
                        specifications=result.specifications
                    )
                    
                elif product_type == "booklets":
                    quote = self.calculator.calculate_booklets(**params)
                    
                elif product_type == "economical_business_cards":
                    # ECONOMICAL BUSINESS CARDS: Shopify Calculator (October 2025)
                    # Uses EconomicalBusinessCardsShopifyCalculator with F1-F6 fields
                    # Cards-per-sheet calculation, BizCost-based profit margins (13 tiers), 10% GST
                    self._print_and_log(f"🔗 ROUTING: Economical Business Cards → EconomicalBusinessCardsShopifyCalculator")
                    econ_cards_calc = EconomicalBusinessCardsShopifyCalculator()
                    result = econ_cards_calc.calculate(**params)
                    
                    # Convert to QuoteResult format for compatibility
                    from complete_calculator_implementation import QuoteResult
                    quote = QuoteResult(
                        product_type="economical_business_cards",
                        quantity=result.quantity,
                        cost_to_business=result.breakdown['biz_cost'],
                        profit_margin=result.breakdown.get('profit_margin_rate', 0),
                        total_cost_ex_gst=result.breakdown['subtotal_with_increase'],
                        total_cost_inc_gst=result.total_price,
                        breakdown=result.breakdown,
                        specifications=result.specifications
                    )
                    
                elif product_type == "premium_business_cards_shopify":
                    # PREMIUM BUSINESS CARDS SHOPIFY: Shopify-Specific Calculator (October 2025)
                    # Uses PremiumBusinessCardsShopifyCalculator with F1-F7 fields
                    # DUAL profit structure (120% without cello, 30%-90% with cello)
                    # DOUBLE GST application (Total * 1.1 * 1.1 = 21% tax - Shopify quirk)
                    self._print_and_log(f"🔗 ROUTING: Premium Business Cards Shopify → PremiumBusinessCardsShopifyCalculator")
                    self._print_and_log(f"⚠️  WARNING: This is SHOPIFY-specific calculator with DOUBLE GST application")
                    premium_shopify_calc = PremiumBusinessCardsShopifyCalculator()
                    result = premium_shopify_calc.calculate(**params)
                    
                    # Convert to QuoteResult format for compatibility
                    from complete_calculator_implementation import QuoteResult
                    quote = QuoteResult(
                        product_type="premium_business_cards_shopify",
                        quantity=result.quantity,
                        cost_to_business=result.breakdown['biz_cost'],
                        profit_margin=result.breakdown.get('profit_margin_rate', 0),
                        total_cost_ex_gst=result.breakdown['subtotal'],
                        total_cost_inc_gst=result.total_price,
                        breakdown=result.breakdown,
                        specifications=result.specifications
                    )
                    
                elif product_type == "business_cards":
                    self._print_and_log(f"🔗 ROUTING: Business Cards → calculate_business_cards()")
                    
                    # Use the unified business cards method from complete_calculator_implementation
                    quote = self.calculator.calculate_business_cards(
                        quantity=params.get('quantity', 500),
                        stock_type=params.get('stock_type', 'satin_350gsm'),
                        sides=params.get('sides', 2),
                        print_type=params.get('print_type', 'color'),
                        finish_size=params.get('finish_size', 'standard'),
                        celloglaze=params.get('celloglaze', 'none'),
                        artworks=params.get('artworks', 1)
                    )
                    
                elif product_type == "corflute_signs":
                    self._print_and_log(f"🔗 ROUTING: Corflute Signs → calculate_corflute_signs()")
                    
                    # Import Shopify corflute calculator enums (Website Pricing - Hardcoded)
                    import sys
                    import os
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
                    from shopify_calculators.corflute_calculator_shopify import (
                        CorflutePricingCalculatorShopify as CorflutePricingCalculatorWooCommerce,
                        CorfluteSizePreset,
                        CorfiuteThickness,
                        EyeletOption,
                        CuttingType
                    )
                    
                    # Map size_preset string to enum
                    size_preset_str = params.get('size_preset', '600x900mm')
                    size_map = {
                        '450x600mm': CorfluteSizePreset.SIZE_450x600,
                        '600x900mm': CorfluteSizePreset.SIZE_600x900,
                        '900x1200mm': CorfluteSizePreset.SIZE_900x1200,
                        '1200x2400mm': CorfluteSizePreset.SIZE_1200x2400,
                        'custom': CorfluteSizePreset.CUSTOM
                    }
                    size_preset = size_map.get(size_preset_str, CorfluteSizePreset.SIZE_600x900)
                    
                    # Map thickness string to enum
                    thickness_str = params.get('thickness', '5mm')
                    thickness = CorfiuteThickness.MM_5 if thickness_str == '5mm' else CorfiuteThickness.MM_3
                    
                    # Map eyelet_option string to enum
                    eyelet_str = params.get('eyelet_option', 'none')
                    eyelet_map = {
                        'none': EyeletOption.NONE,
                        '4_corners': EyeletOption.FOUR_CORNERS,
                        '2_top': EyeletOption.TWO_TOP,
                        '2_center_lr': EyeletOption.TWO_CENTER_LR,
                        '2_center_tb': EyeletOption.TWO_CENTER_TB,
                        '6_top_bottom': EyeletOption.SIX_TOP_BOTTOM,
                        '6_left_right': EyeletOption.SIX_LEFT_RIGHT
                    }
                    eyelet_option = eyelet_map.get(eyelet_str, EyeletOption.NONE)
                    
                    # Map cutting_type string to enum
                    cutting_str = params.get('cutting_type', 'standard')
                    cutting_type = CuttingType.STANDARD if cutting_str == 'standard' else CuttingType.CUSTOM_SHAPE
                    
                    # Create corflute calculator and calculate quote
                    corflute_calc = CorflutePricingCalculatorWooCommerce()
                    corflute_result = corflute_calc.calculate_quote(
                        size_preset=size_preset,
                        custom_width_mm=params.get('custom_width_mm', 0),
                        custom_height_mm=params.get('custom_height_mm', 0),
                        thickness=thickness,
                        quantity=params.get('quantity', 10),
                        double_sided=params.get('double_sided', False),
                        eyelet_option=eyelet_option,
                        cutting_type=cutting_type,
                        artworks=params.get('artworks', 1)
                    )
                    
                    # Convert corflute result to QuoteResult format
                    from dataclasses import dataclass
                    from decimal import Decimal
                    
                    @dataclass
                    class CorfluteCuoteResult:
                        """Corflute quote result in QuoteResult format"""
                        product_type: str
                        quantity: int
                        cost_to_business: Decimal
                        profit_margin: Decimal
                        total_cost_ex_gst: Decimal
                        total_cost_inc_gst: Decimal
                        breakdown: dict
                        specifications: dict
                    
                    # Corflute includes GST in pricing, so extract it
                    # Assume 10% GST: total = ex_gst * 1.1
                    total_inc_gst = Decimal(str(corflute_result['total']))
                    total_ex_gst = total_inc_gst / Decimal('1.1')
                    
                    quote = CorfluteCuoteResult(
                        product_type="corflute_signs",
                        quantity=corflute_result['quantity'],
                        cost_to_business=total_ex_gst,  # Cost before markup
                        profit_margin=Decimal('0'),  # WooCommerce pricing includes margin
                        total_cost_ex_gst=total_ex_gst,
                        total_cost_inc_gst=total_inc_gst,
                        breakdown={
                            'sqm_per_unit': corflute_result['sqm_per_unit'],
                            'total_sqm': corflute_result['total_sqm'],
                            'tier_price_per_sqm': corflute_result['tier_price_per_sqm'],
                            'base_cost': corflute_result['base_cost'],
                            'double_sided_cost': corflute_result['double_sided_cost'],
                            'custom_premium': corflute_result['custom_premium'],
                            'eyelet_cost': corflute_result['eyelet_cost'],
                            'artwork_cost': corflute_result['artwork_cost'],
                            'subtotal_before_discount': corflute_result['subtotal_before_discount'],
                            'discount_amount': corflute_result['discount_amount'],
                            'subtotal_after_discount': corflute_result['subtotal_after_discount'],
                            'minimum_applied': corflute_result['minimum_applied'],
                            'per_unit': corflute_result['per_unit']
                        },
                        specifications={
                            'width_mm': corflute_result['width_mm'],
                            'height_mm': corflute_result['height_mm'],
                            'thickness': corflute_result['thickness'],
                            'double_sided': corflute_result['double_sided'],
                            'eyelets': corflute_result['eyelets'],
                            'artworks': corflute_result['artworks'],
                            'is_custom_size': corflute_result['is_custom_size']
                        }
                    )
                    
                else:
                    raise ValueError(f"Product type '{product_type}' not implemented")
                
                # Build comprehensive result with Decimal conversion
                # CRITICAL: Convert nested Decimals in specifications and breakdown
                def convert_to_json_serializable(obj):
                    """Convert Decimal, datetime, and other types to JSON-serializable formats"""
                    if isinstance(obj, list):
                        return [convert_to_json_serializable(item) for item in obj]
                    elif isinstance(obj, dict):
                        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
                    elif isinstance(obj, (int, float, str, bool, type(None))):
                        return obj
                    else:
                        # Convert Decimal, datetime, etc. to string
                        return str(obj)
                
                result = {
                    "success": True,
                    "cost_ex_gst": float(quote.total_cost_ex_gst),
                    "cost_inc_gst": float(quote.total_cost_inc_gst),
                    "cost_to_business": float(quote.cost_to_business),
                    "profit_margin": float(quote.profit_margin),
                    "product_type": quote.product_type,
                    "quantity": quote.quantity,
                    "specifications": convert_to_json_serializable(quote.specifications if hasattr(quote, 'specifications') else {}),
                    "breakdown": convert_to_json_serializable(quote.breakdown if hasattr(quote, 'breakdown') else {})
                }
                
                self._print_and_log(f" QUOTE CALCULATED:")
                self._print_and_log(f"   Cost Ex GST: ${result['cost_ex_gst']:,.2f}")
                self._print_and_log(f"   Cost Inc GST: ${result['cost_inc_gst']:,.2f}")
                self._print_and_log(f"   Profit Margin: ${result['profit_margin']:,.2f}")
                
                # Print FULL result including all breakdown details
                self._print_and_log(f"\n📋 COMPLETE QUOTE RESULT (Full JSON):")
                self._print_and_log(json.dumps(result, indent=2, default=str))
                
                # Emit client_tool_execution event
                self._log_event("client_tool_execution", {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "result": result,
                    "summary": f"Quote calculated: ${result['cost_inc_gst']:,.2f} for {result['quantity']} {product_type}"
                })
                
                return result
            
            elif tool_name == "get_available_queries":
                # Get available queries from library
                category = tool_input.get("category")
                queries = self.query_library.get_available_queries(category)
                
                self._print_and_log(f" AVAILABLE QUERIES:")
                if category:
                    self._print_and_log(f"   Category: {category}")
                self._print_and_log(f"   Total queries: {len(queries)}")
                
                # Format results for AI
                result_data = {
                    "success": True,
                    "category": category,
                    "query_count": len(queries),
                    "queries": queries
                }
                
                # Print summary
                for query in queries:
                    self._print_and_log(f"\n📊 {query['name']}")
                    self._print_and_log(f"   Category: {query['category']}")
                    self._print_and_log(f"   Description: {query['description']}")
                    self._print_and_log(f"   Best for: {query['best_for']}")
                
                # Emit client_tool_execution event
                self._log_event("client_tool_execution", {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "result": result_data,
                    "summary": f"Retrieved {len(queries)} available queries" + (f" in category '{category}'" if category else "")
                })
                
                return result_data
            
            elif tool_name == "get_query_from_library":
                # Get and execute query from library
                query_name = tool_input["query_name"]
                parameters = tool_input.get("parameters", {})
                
                self._print_and_log(f"QUERY NAME: {query_name}")
                self._print_and_log(f"PARAMETERS:")
                self._print_and_log(json.dumps(parameters, indent=2))
                self._print_and_log("")
                
                # Build query with parameters
                query_result = self.query_library.build_query(query_name, **parameters)
                
                self._print_and_log(f" QUERY BUILT:")
                self._print_and_log(f"   Name: {query_name}")
                self._print_and_log(f"   Category: {query_result['metadata']['category']}")
                self._print_and_log(f"   Description: {query_result['metadata']['description']}")
                self._print_and_log(f"\nSQL:")
                self._print_and_log(query_result['sql'])
                self._print_and_log("")
                
                # Execute the query
                df = self.db.execute_query(query_result['sql'])
                records = df.to_dict('records')
                
                # Convert to JSON-serializable
                def convert_to_json_serializable(obj):
                    if isinstance(obj, list):
                        return [convert_to_json_serializable(item) for item in obj]
                    elif isinstance(obj, dict):
                        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
                    elif isinstance(obj, (int, float, str, bool, type(None))):
                        return obj
                    else:
                        return str(obj)
                
                json_safe_records = convert_to_json_serializable(records)
                
                self._print_and_log(f" QUERY RESULT: {len(json_safe_records)} rows")
                self._print_and_log(json.dumps(json_safe_records, indent=2, default=str))
                
                result_data = {
                    "success": True,
                    "query_name": query_name,
                    "parameters": query_result['parameters'],
                    "row_count": len(json_safe_records),
                    "data": json_safe_records,
                    "metadata": query_result['metadata'],
                    "sql": query_result['sql']  # Include SQL for transparency
                }
                
                # Emit client_tool_execution event
                self._log_event("client_tool_execution", {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "result": result_data,
                    "summary": f"Query '{query_name}' returned {len(json_safe_records)} rows"
                })
                
                return result_data
            
            elif tool_name == "query_stock_levels":
                # Query stock levels from temp database
                filters = tool_input.get("filters", {})
                
                self._print_and_log(f"FILTERS:")
                self._print_and_log(json.dumps(filters, indent=2))
                self._print_and_log("")
                
                result = self.stock_tools.query_stock_levels(filters)
                
                self._print_and_log(f" RESULT:")
                self._print_and_log(json.dumps(result, indent=2, default=str))
                
                # Emit client_tool_execution event
                self._log_event("client_tool_execution", {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "result": result,
                    "summary": result['message']
                })
                
                return result
            
            elif tool_name == "get_stock_transactions":
                # Get stock transaction history
                stock_id = tool_input.get("stock_id")
                limit = tool_input.get("limit", 50)
                
                self._print_and_log(f"STOCK ID: {stock_id}")
                self._print_and_log(f"LIMIT: {limit}")
                self._print_and_log("")
                
                result = self.stock_tools.get_stock_transactions(stock_id, limit)
                
                self._print_and_log(f" RESULT:")
                self._print_and_log(json.dumps(result, indent=2, default=str))
                
                # Emit client_tool_execution event
                self._log_event("client_tool_execution", {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "result": result,
                    "summary": result['message']
                })
                
                return result
            
            elif tool_name == "get_reorder_alerts":
                # Get active reorder alerts
                self._print_and_log("Getting reorder alerts...")
                self._print_and_log("")
                
                result = self.stock_tools.get_reorder_alerts()
                
                self._print_and_log(f" RESULT:")
                self._print_and_log(json.dumps(result, indent=2, default=str))
                
                # Emit client_tool_execution event
                self._log_event("client_tool_execution", {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "result": result,
                    "summary": result['message']
                })
                
                return result
            
            elif tool_name == "update_stock_level":
                # Update stock level (WRITE operation)
                stock_id = tool_input["stock_id"]
                new_level = tool_input["new_level"]
                reason = tool_input["reason"]
                reference = tool_input.get("reference")
                
                self._print_and_log(f"STOCK ID: {stock_id}")
                self._print_and_log(f"NEW LEVEL: {new_level}")
                self._print_and_log(f"REASON: {reason}")
                self._print_and_log(f"REFERENCE: {reference}")
                self._print_and_log("")
                
                result = self.stock_tools.update_stock_level(stock_id, new_level, reason, reference)
                
                self._print_and_log(f" RESULT:")
                self._print_and_log(json.dumps(result, indent=2, default=str))
                
                # Emit client_tool_execution event
                self._log_event("client_tool_execution", {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "result": result,
                    "summary": result['message']
                })
                
                return result
            
            elif tool_name == "get_production_pricing":
                # Query production pricing from SQL Server
                filters = tool_input.get("filters", {})
                
                self._print_and_log(f"FILTERS:")
                self._print_and_log(json.dumps(filters, indent=2))
                self._print_and_log("")
                
                result = self.stock_tools.get_production_pricing(filters)
                
                self._print_and_log(f" RESULT:")
                self._print_and_log(json.dumps(result, indent=2, default=str))
                
                # Emit client_tool_execution event
                self._log_event("client_tool_execution", {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "result": result,
                    "summary": result['message']
                })
                
                return result
            
            elif tool_name == "update_stock_record":
                # Update stock record in unified_stocks table
                import sqlite3
                
                stock_id = tool_input.get("stock_id", "")
                updates = tool_input.get("updates", {})
                reason = tool_input.get("reason", "No reason provided")
                
                if not stock_id or not updates:
                    return {
                        "success": False,
                        "error": "stock_id and updates are required"
                    }
                
                db_path = os.path.join(self.stocks_path, 'stock_data.db')
                
                self._print_and_log(f"\n✏️ UPDATING Stock Record: {stock_id}")
                self._print_and_log(f"📝 Updates: {json.dumps(updates, indent=2)}")
                self._print_and_log(f"📋 Reason: {reason}")
                self._print_and_log("")
                
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Verify stock exists
                    sql, params = convert_sql_placeholders("SELECT stock_id FROM unified_stocks WHERE stock_id = ?", (stock_id,))

                    cursor.execute(sql, params)
                    if not cursor.fetchone():
                        conn.close()
                        return {
                            "success": False,
                            "error": f"Stock ID '{stock_id}' not found in unified_stocks table"
                        }
                    
                    # Build UPDATE query
                    set_clauses = [f"{col} = ?" for col in updates.keys()]
                    values = list(updates.values()) + [stock_id]
                    
                    update_sql = f"UPDATE unified_stocks SET {', '.join(set_clauses)}, updated_at = datetime('now') WHERE stock_id = ?"
                    
                    self._print_and_log(f"🔧 SQL: {update_sql}")
                    self._print_and_log(f"📊 Values: {values}")
                    
                    cursor.execute(update_sql, values)
                    rows_affected = cursor.rowcount
                    conn.commit()
                    conn.close()
                    
                    self._print_and_log(f" Updated {rows_affected} record(s)")
                    
                    result = {
                        "success": True,
                        "message": f"Successfully updated stock {stock_id}",
                        "stock_id": stock_id,
                        "updates": updates,
                        "reason": reason,
                        "rows_affected": rows_affected
                    }
                    
                    self._log_event("client_tool_execution", {
                        "tool_name": tool_name,
                        "tool_input": tool_input,
                        "result": result,
                        "summary": result['message']
                    })
                    
                    return result
                    
                except sqlite3.Error as e:
                    if conn:
                        conn.rollback()
                        conn.close()
                    error_msg = f"SQLite error: {str(e)}"
                    self._print_and_log(f" {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "message": f"Update failed: {error_msg}"
                    }
                except Exception as e:
                    if conn:
                        conn.rollback()
                        conn.close()
                    error_msg = f"Unexpected error: {str(e)}"
                    self._print_and_log(f" {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "message": f"Update failed: {error_msg}"
                    }
            
            elif tool_name == "update_job_record":
                # Update job record in extracted_jobs table
                import sqlite3
                
                ticket_id = tool_input.get("ticket_id", "")
                updates = tool_input.get("updates", {})
                reason = tool_input.get("reason", "No reason provided")
                
                if not ticket_id or not updates:
                    return {
                        "success": False,
                        "error": "ticket_id and updates are required"
                    }
                
                db_path = os.path.join(self.stocks_path, 'stock_data.db')
                
                self._print_and_log(f"\n✏️ UPDATING Job Record: {ticket_id}")
                self._print_and_log(f"📝 Updates: {json.dumps(updates, indent=2)}")
                self._print_and_log(f"📋 Reason: {reason}")
                self._print_and_log("")
                
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Verify job ticket exists
                    sql, params = convert_sql_placeholders("SELECT ticket_id FROM extracted_jobs WHERE ticket_id = ?", (ticket_id,))

                    cursor.execute(sql, params)
                    if not cursor.fetchone():
                        conn.close()
                        return {
                            "success": False,
                            "error": f"Ticket ID '{ticket_id}' not found in extracted_jobs table"
                        }
                    
                    # Build UPDATE query
                    set_clauses = [f"{col} = ?" for col in updates.keys()]
                    values = list(updates.values()) + [ticket_id]
                    
                    update_sql = f"UPDATE extracted_jobs SET {', '.join(set_clauses)}, extraction_date = datetime('now') WHERE ticket_id = ?"
                    
                    self._print_and_log(f"🔧 SQL: {update_sql}")
                    self._print_and_log(f"📊 Values: {values}")
                    
                    cursor.execute(update_sql, values)
                    rows_affected = cursor.rowcount
                    conn.commit()
                    conn.close()
                    
                    self._print_and_log(f" Updated {rows_affected} record(s)")
                    
                    result = {
                        "success": True,
                        "message": f"Successfully updated job ticket {ticket_id}",
                        "ticket_id": ticket_id,
                        "updates": updates,
                        "reason": reason,
                        "rows_affected": rows_affected
                    }
                    
                    self._log_event("client_tool_execution", {
                        "tool_name": tool_name,
                        "tool_input": tool_input,
                        "result": result,
                        "summary": result['message']
                    })
                    
                    return result
                    
                except sqlite3.Error as e:
                    if conn:
                        conn.rollback()
                        conn.close()
                    error_msg = f"SQLite error: {str(e)}"
                    self._print_and_log(f" {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "message": f"Update failed: {error_msg}"
                    }
                except Exception as e:
                    if conn:
                        conn.rollback()
                        conn.close()
                    error_msg = f"Unexpected error: {str(e)}"
                    self._print_and_log(f" {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "message": f"Update failed: {error_msg}"
                    }
            
            elif tool_name == "query_ai_extracted_jobs":
                # Query AI-extracted jobs from SQLite stock_data.db
                import sqlite3
                import pandas as pd
                
                sql_query = tool_input.get("sql_query", "")
                
                if not sql_query:
                    return {
                        "success": False,
                        "error": "No SQL query provided"
                    }
                
                # Build path to stock_data.db
                db_path = os.path.join(self.stocks_path, 'stock_data.db')
                
                self._print_and_log(f"\n🔍 QUERYING SQLite Database: {db_path}")
                self._print_and_log(f"📊 SQL: {sql_query}")
                self._print_and_log("")
                
                try:
                    # Connect and execute
                    conn = sqlite3.connect(db_path)
                    df = pd.read_sql_query(sql_query, conn)
                    conn.close()
                    
                    # Convert to records
                    data = df.to_dict('records')
                    
                    self._print_and_log(f" Query successful: {len(data)} rows returned")
                    self._print_and_log(json.dumps({"rows": len(data), "sample": data[:3] if data else []}, indent=2, default=str))
                    
                    result = {
                        "success": True,
                        "message": f"Retrieved {len(data)} rows from extracted_jobs table",
                        "rows": len(data),
                        "columns": list(df.columns),
                        "data": data
                    }
                    
                    # Emit client_tool_execution event
                    self._log_event("client_tool_execution", {
                        "tool_name": tool_name,
                        "tool_input": tool_input,
                        "result": result,
                        "summary": result['message']
                    })
                    
                    return result
                    
                except sqlite3.Error as e:
                    error_msg = f"SQLite error: {str(e)}"
                    self._print_and_log(f" {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "message": f"Database query failed: {error_msg}"
                    }
                except Exception as e:
                    error_msg = f"Unexpected error: {str(e)}"
                    self._print_and_log(f" {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "message": f"Query execution failed: {error_msg}"
                    }
            
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        
        except Exception as e:
            error_msg = str(e)
            self._print_and_log(f" ERROR: {error_msg}")
            
            # Provide helpful guidance for common errors
            helpful_hint = ""
            if "unexpected keyword argument" in error_msg.lower():
                # Extract the problematic parameter name
                import re
                match = re.search(r"unexpected keyword argument '(\w+)'", error_msg)
                if match:
                    param_name = match.group(1)
                    helpful_hint = f"\n\n💡 HINT: The parameter '{param_name}' is not supported for this product type. Try calling the tool again WITHOUT this parameter. For cellophane finishing, use only 'cello_required': true/false without specifying finish type or sides."
            
            error_result = {
                "success": False,
                "error": error_msg + helpful_hint
            }
            
            # Emit client_tool_execution event for errors too
            self._log_event("client_tool_execution", {
                "tool_name": tool_name,
                "tool_input": tool_input,
                "result": error_result,
                "summary": f"Tool execution failed: {error_msg}"
            })
            
            return error_result
    
    def _handle_server_tool_use(self, block: Any):
        """
        Handle SERVER tool use (already executed by Anthropic).
        Just log it - we don't execute anything.
        Reference: API_EVENT_STRUCTURES.md section 3.5
        """
        self._log_event("server_tool_use", {
            "id": block.id,
            "name": block.name,
            "input": block.input
        })
        
        print(f"🌐 SERVER TOOL EXECUTED (by Anthropic): {block.name}")
        print(f"   Search query: {block.input.get('query', 'N/A')}")
    
    def _handle_web_search_result(self, block: Any):
        """
        Handle web search results (automatically provided by Anthropic).
        Store for citation display.
        Reference: API_EVENT_STRUCTURES.md section 3.6
        """
        self._log_event("web_search_tool_result", {
            "tool_use_id": block.tool_use_id,
            "result_count": len(block.content) if hasattr(block, 'content') else 0
        })
        
        print(f"📚 WEB SEARCH RESULTS:")
        if hasattr(block, 'content'):
            for i, result in enumerate(block.content, 1):
                if hasattr(result, 'title'):
                    print(f"   [{i}] {result.title}")
                    print(f"       {result.url}")
                    if hasattr(result, 'page_age') and result.page_age:
                        print(f"       Updated: {result.page_age}")
    
    def _display_citations(self, text_block: Any):
        """
        Display citations (LEGAL REQUIREMENT).
        Reference: API_EVENT_STRUCTURES.md section 3.7
        """
        if hasattr(text_block, 'citations') and text_block.citations:
            print(f"\n📖 CITATIONS:")
            for i, citation in enumerate(text_block.citations, 1):
                print(f"   [{i}] {citation.title}")
                print(f"       {citation.url}")
                if hasattr(citation, 'cited_text'):
                    cited_preview = citation.cited_text[:150] + "..." if len(citation.cited_text) > 150 else citation.cited_text
                    print(f"       \"{cited_preview}\"")
            self.citations.extend(text_block.citations)
    
    def process_request(self, customer_message: str = None, max_turns: int = 10, conversation_history: list = None, system_prompt: str = None, content_blocks: list | None = None, model_override: str | None = None) -> Dict[str, Any]:
        """
        Process customer request using official Tool Use API.
        
        Args:
            customer_message: The current user message
            max_turns: Maximum number of conversation turns
            conversation_history: List of previous messages [{"role": "user"|"assistant", "content": "..."}]
            system_prompt: Optional custom system prompt (overrides default quote agent prompt)
        """
        self._print_and_log(f"\n{'='*100}")
        self._print_and_log(f"🤖 TOOL USE API - PROCESSING REQUEST")
        self._print_and_log(f"{'='*100}\n")
        self._print_and_log(f"Customer: {customer_message}")
        self._print_and_log("")
        
        # Build conversation starting with history (if provided)
        if conversation_history:
            conversation = conversation_history.copy()
            self._print_and_log(f"📜 Resuming conversation with {len(conversation_history)} previous messages")
        else:
            conversation = []
        
        # Add current user message. If content_blocks provided, include them directly
        if content_blocks is not None:
            # content_blocks follows Anthropic content block structure (documents/images + text)
            conversation.append({
                "role": "user",
                "content": content_blocks
            })
        else:
            # Backward compatible: plain text message
            conversation.append({
                "role": "user",
                "content": customer_message or ""
            })
        
        # System prompt - use custom if provided, otherwise default quote agent prompt
        if system_prompt is None:
            system_prompt = """You are Viki, an AI quote assistant for InHouse Print in Brisbane, Australia.

**IMPORTANT: You have Extended Thinking enabled with interleaved thinking capability.**
- Use your thinking blocks BETWEEN actions to analyze, plan, and reason
- Think before executing tools to determine the best approach
- Use client name and past orders to personalise quotes and recommendations - always check for existing relationships
- Search both customers name and business name and product key terms in past orders - analyse the results as it could be a new staff member for a busineess that is a client, or a past customer at a new business - use SQL LIKE with wildcards for partial matches
- Think after receiving results to interpret and validate data
- DON'T wait to be prompted - use thinking naturally throughout the conversation
- Your thinking is internal - customers don't see it

You have access to:
1. get_calculator_requirements(product_type) - Find what parameters you need
2. execute_sql(query) - Query database for historical orders
3. calculate_quote(product_type, parameters) - Calculate a quote
4. web_search (automatic) - Search web for current pricing/standards

**SUPPORTED CALCULATORS:**
- "business_cards" - Business cards (WooCommerce calculator - EXACT pricing)
- "flyers" - Digital flyers/leaflets  
- "perfect_bound_books" - Books (40+ pages) - includes ALL binding types:
  * Perfect Bound: Glued square spine (default)
  * Wire Bound: Metal wire coil binding (WooCommerce pricing with 15% GST)
  * Spiral Bound: Plastic coil binding (WooCommerce pricing with 15% discount + 15% GST)
  * CRITICAL: Specify binding_type parameter to select binding method
- "booklets" - Saddle stitched booklets/magazines (4-60 pages)
- "corflute_signs" - Corflute signs (WooCommerce calculator - EXACT pricing)

**CRITICAL DATABASE STRUCTURE & EXPLORATION STRATEGY:**

**⚠️ VERIFIED DATABASE STRUCTURE (Based on Live Database Exploration):**

**The `jt.TicketNotes` Field is Your PRIMARY Source of Truth!**

When structured database columns (Pages, BindTypeID) are NULL or incomplete, 
the production team writes ALL specifications as free text in the `JobTickets.TicketNotes` field.

**🔥 CRITICAL CORRECTIONS - PaperSize Table Reality:**
```sql
--  WRONG: System used to say PaperSize has Width/Height columns
--  REALITY: PaperSize ONLY has SizeID and [Desc]
-- Table structure: SizeID | Desc
-- Sample data:      3     | "BC - 90x55"
--                   4     | "A5"
--                   9     | "A4"

--  DON'T DO THIS (PaperSize doesn't have Width/Height!):
SELECT ps.Width, ps.Height FROM PaperSize ps  -- THESE COLUMNS DON'T EXIST

--  DO THIS INSTEAD - Parse dimensions from TicketNotes or size description:
SELECT 
    ps.[Desc] AS PaperSize,      -- "A6", "A4", "BC - 90x55"
    jt.TicketNotes               -- "90mm x 55mm", "Trim size: A6"
FROM JobTickets jt
LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID  -- Join on SizeID!
```

**CORRECT Column Names - Verified Against Live Database:**
```sql
--  WRONG (These columns DON'T EXIST!)
jt.Note              -- Does NOT exist! Use jt.TicketNotes
jt.Width             -- Does NOT exist! Parse from TicketNotes
jt.Height            -- Does NOT exist! Parse from TicketNotes  
jt.InnerGSM_ID       -- Does NOT exist! Parse from TicketNotes
jt.ColourStatusID    -- Does NOT exist! Use jt.ColourStatus (no "ID" suffix)
ps.Width             -- Does NOT exist! PaperSize only has SizeID and [Desc]
ps.Height            -- Does NOT exist! PaperSize only has SizeID and [Desc]

--  CORRECT (Always use these!)
jt.TicketNotes       -- Production notes with ALL specifications
ps.[Desc]            -- Size description: "A4", "A5", "BC - 90x55", "DL"
jt.ColourStatus      -- Urgency status (Nullable Integer, no "ID" suffix)
jt.BindTypeID        -- FK to BindType.BindID (often NULL - check TicketNotes!)
jt.RingBind          -- Boolean for ring/wire binding
jt.PerfectBind       -- Boolean for perfect binding
jt.Books             -- Boolean indicating book product
jt.Pages             -- Often NULL! Parse from TicketNotes instead
```

**🔥 CRITICAL: BindType Table Structure (DIFFERENT from other lookup tables!):**
```sql
--  CORRECT BindType table structure:
-- Columns: BindID | BindTypeDesc (NOT [Desc]!)
-- Sample data:
--   1 | "None"
--   2 | "Cut Ring Wire"
--   3 | "Perfect Bound"
--   4 | "Saddle Stitch"
--   5 | "Pad Glue"
--   7 | "Plastic Spiral"  ← Used for MiniVet Guides!

--  CORRECT JOIN syntax:
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID  -- Join on BindID, not BindTypeID!

--  CORRECT column reference:
bt.BindTypeDesc AS BindType  -- NOT bt.[Desc]!
```

**🔥 CRITICAL: ColourStatus is NOT About Print Colors!**
```sql
--  WRONG ASSUMPTION: ColourStatus indicates print color mode (B&W, CMYK, etc.)
--  REALITY: ColourStatus is PRODUCTION URGENCY/PRIORITY!
-- Columns: ColourID | ColourDesc | ColourValue | OrderPriority
-- Sample data:
--   2 | "Before Lunch Today"     | #ff0000 | 1
--   3 | "Before COB Today"       | #ff6600 | 2
--   7 | "Timely Manner"          | #66b3ff | 6

--  CORRECT JOIN syntax:
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID  -- jt.ColourStatus is the FK!

-- For actual print color info, parse from:
-- - jt.TicketNotes: "Full Colour", "B&W", "CMYK", "Black print only"
-- - JobType.[Desc]: "Business Cards - Double Sided", "Flyers - Single Side"
```

**ALWAYS Include in Your SELECT Queries:**
```sql
jt.TicketNotes AS ProductionNotes,   --  PRIMARY source (NOT "Note")
ps.[Desc] AS PaperSize,              --  "A4", "A5", "BC - 90x55"
jt.Pages,                            -- Often NULL - parse from TicketNotes!
bt.BindTypeDesc AS BindType,        --  NOT bt.[Desc]!
cs.ColourDesc AS UrgencyStatus       --  Production priority, not print color
```

**Correct JOIN Structure:**
```sql
FROM JobTickets jt
JOIN Orders o ON jt.OrderID = o.OrderID
JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID        --  Join on SizeID
LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID          --  Join on BindID!
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID  --  jt.ColourStatus FK
```

**What's in the TicketNotes Field (Real Examples from Database):**

**Example 1: Gerardo Poli - MiniVet Guide (1000 units, $9,444.07)**
```
"Black Plastic Spiral Bound
Cover 300gsm Matt Art Card Gloss celloglazed
Clear plastic front and back"
```
**Extract:** Binding=Plastic Spiral, Cover=300GSM Matt Art + Gloss Cello, Interior=100GSM (from PaperType field)

**Example 2: Gerardo Poli - Emergency VG (2000 units, $19,140.04)**
```
"Trim size: A6 (scale file down from A4) 
Content stock: 100GSM uncoated B&W 
Page count: 430 
Cover stock: 300gsm Matt Art Card 
Cello: Gloss 
Clear plastic front and back"
```
**Extract:** Size=A6, Pages=430, Interior=100GSM B&W uncoated, Cover=300GSM + Gloss Cello

**Example 3: Business Card - Matt Cello Both Sides ($104.50 for 500)**
```
"Business Cards - Double sided
90mm x 55mm
350gsm Satin
Full Colour
Matt Cello Both Sides
1 x artwork"
```
**Extract:** Size=90x55mm, Stock=350GSM Satin, Sides=Double, Cello=Matt Both Sides

**Example 4: A4 Booklet - Saddle Stitch ($501.83 for 100)**
```
"Quantity: 100
Finish Size: A5 Portrait
Cover Option: Hard Cover
Cover Print Type: 2 side colour (4pp)
Cover Stock: Satin 250GSM
Celloglaze: None
Printed Pages: 40pp
Content Print Type: Colour
Content Stock Type: Uncoated Bond 100GSM"
```
**Extract:** Size=A5, Pages=40pp, Cover=250GSM Satin no cello, Interior=100GSM Color

**What to Extract from TicketNotes:**
- Exact page counts: "430 pages", "246 pages", "40pp"
- Product dimensions: "A6", "90mm x 55mm", "A5 Portrait", "A4"
- Paper specs: "100GSM uncoated B&W", "300GSM Matt Art Card", "350gsm Satin"
- Binding details: "Black plastic spiral bound", "Saddle Stitch", "Perfect bound"
- Finishing: "Gloss celloglazed", "Matt cello both sides", "Celloglaze: None"
- Print mode: "Full Colour", "B&W", "CMYK", "Black print only"
- Special features: "Clear plastic front and back covers"

**🔥 CRITICAL: Book Orientation (Width × Height)**
⚠️ **MOST BOOKS ARE PORTRAIT (taller than wide) - Do NOT swap dimensions!**

**Standard Portrait Orientations (MOST COMMON):**
- A6 Portrait: book_width=105mm, book_height=148mm (STANDARD for small books)
- A5 Portrait: book_width=148mm, book_height=210mm (STANDARD for medium books)  
- A4 Portrait: book_width=210mm, book_height=297mm (STANDARD for large books)
- DL Portrait: book_width=99mm, book_height=210mm (STANDARD for slim books)

**Landscape Orientations (RARE - only if explicitly stated):**
- A6 Landscape: book_width=148mm, book_height=105mm (RARE - must say "landscape")
- A5 Landscape: book_width=210mm, book_height=148mm (RARE - must say "landscape")
- A4 Landscape: book_width=297mm, book_height=210mm (RARE - must say "landscape")

**Extraction Rules:**
 "A6" or "Trim size: A6" → book_width=105, book_height=148 (Portrait is default)
 "A5" or "A5 Portrait" → book_width=148, book_height=210
 "A4" → book_width=210, book_height=297
 "A6 Landscape" → book_width=148, book_height=105 (Only if "landscape" mentioned)
 NEVER swap width/height unless customer explicitly says "landscape"

**Common Mistake to Avoid:**
 WRONG: "A6 book" → book_width=148, book_height=105 (this is landscape!)
 CORRECT: "A6 book" → book_width=105, book_height=148 (portrait is standard)

**Why This Matters:**
- Portrait books: Width < Height (taller than wide) - STANDARD
- Landscape books: Width > Height (wider than tall) - RARE
- Wrong orientation = wrong sheets calculation = wrong pricing (10-15% error)

**SQL TROUBLESHOOTING - When Queries Don't Work:**

If you get "Invalid column name" errors:
-  Use jt.TicketNotes NOT jt.Note
-  JOIN PaperSize table for Width/Height (not in JobTickets!)
-  Use jt.ColourStatus NOT jt.ColourStatusID
-  Always use [Desc] with square brackets for lookup tables

If structured columns return NULL:
-  Check the jt.TicketNotes field - parse the free text
-  Try broader LEFT JOINs instead of INNER JOINs
-  Search by jt.ShortJobDesc keywords instead of exact matches
-  Query recent orders (last 12 months) to see current data patterns

If you get zero results:
-  Remove filters one at a time to find what's blocking results
-  Try LIKE '%keyword%' instead of exact matches
-  Check if ClientName is spelled differently (search broader, e.g., '%Poli%' instead of '%Gerardo Poli%')
-  Query the schema to see what values actually exist in lookup tables

**Exploration Mindset - Don't Give Up!**
- If one approach fails, try a different angle
- Use client name and past orders to personalise quotes and recommendations - always check for existing relationships
- Search both customers name and business name and product key terms in past orders - analyse the results as it could be a new staff member for a busineess that is a client, or a past customer at a new business - use SQL LIKE with wildcards for partial matches
- Start broad (all customer orders), then narrow down
- Look at what data actually exists before assuming structure
- The Note field often has what structured columns lack
- You have multiple paths to get a quote - use what works!

**RESERVED KEYWORDS - ALWAYS USE SQUARE BRACKETS:**
• JobType.[Desc] NOT JobType.Desc
• PaperType.[Desc] NOT PaperType.Desc  
• GSM.[DESC] NOT GSM.DESC
• BindType.[Desc] NOT BindType.Desc
• ColourStatus.[Desc] NOT ColourStatus.Desc

**RESERVED KEYWORDS - ALWAYS USE SQUARE BRACKETS:**
• JobType.[Desc] NOT JobType.Desc
• PaperType.[Desc] NOT PaperType.Desc  
• GSM.[DESC] NOT GSM.DESC
• BindType.[Desc] NOT BindType.Desc
• ColourStatus.[Desc] NOT ColourStatus.Desc

**PRODUCT-TO-CALCULATOR MAPPING RULES (Based on 150+ orders analyzed):**

**BUSINESS CARDS:**
- Use "business_cards" calculator (NOT "flyers")
- Standard: 300GSM Satin, NO celloglaze
- Premium: 350GSM or 420GSM (King Kong), WITH or WITHOUT celloglaze
- Celloglaze options: None, 1-side or 2-side, Matt/Gloss/Silk
- Standard size: 90mm × 55mm
- Small size (premium only): 90mm × 45mm
- Always double-sided color printing
- 1 artwork included, $15 per additional artwork

**MAGAZINES / CATALOGS:**
- Pages ≤ 60 → Use "booklets" (saddle stitch)
- Pages > 40 AND square spine needed → Use "perfect_bound_books" (Books - any binding type)

**BOOKLETS / BROCHURES / NEWSLETTERS:**
- Pages ≤ 60 → Use "booklets" (saddle stitch)
- Pages > 40 AND square spine needed → Use "perfect_bound_books" (Books - any binding type)

**PROGRAMS / PROSPECTUSES:**
- Usually 8-20pp → Use "booklets" (saddle stitch)

**ANNUAL REPORTS:**
- Pages ≤ 60 AND saddle stitch OK → Use "booklets"
- Pages > 40 AND square spine needed → Use "perfect_bound_books" (Books - any binding type)

**BOOKS / NOVELS / THICK MANUALS:**
- Usually > 40pp → Use "perfect_bound_books" (Books - includes Perfect, Wire, and Spiral binding)

**USER MANUALS / GUIDES / VETERINARY GUIDES:**
- Pages ≤ 60 → Use "booklets" (saddle stitch)
- Pages > 60 → Use "perfect_bound_books" (Books - includes Perfect, Wire, and Spiral binding)
- Lay-flat needed (spiral/wire) → Use "perfect_bound_books" with binding_type parameter!
- Example: MVG Emergency (430pp spiral) → perfect_bound_books with binding_type="Spiral Bound"

**KEY BINDING RULES:**
- Saddle Stitch: 4-60 pages (must be divisible by 4)
- Perfect Bound: 40+ pages minimum, spine ≥3mm (glued square spine)
- Wire Bound: 40+ pages, metal wire coil (specify binding_type="Wire Bound")
- Spiral Bound: 40+ pages, plastic coil, 15% cheaper than Wire (specify binding_type="Spiral Bound")
- Transition zone (40-60 pages): Check stock weight & customer preference

**CRITICAL: BINDING TYPE PARAMETER FOR perfect_bound_books:**
When using perfect_bound_books calculator, ALWAYS specify the binding_type parameter:
- binding_type="Perfect Bound" → Traditional glued square spine (default if not specified)
- binding_type="Wire Bound" → Metal wire coil binding (WooCommerce pricing, 15% GST)
- binding_type="Spiral Bound" → Plastic coil binding (WooCommerce pricing with 15% discount + 15% GST)

**BINDING TYPE ROUTING (CRITICAL IMPLEMENTATION DETAILS):**

All binding types use the SAME calculator method: calculate_perfect_bound_book(binding_type=...)
- The method internally routes based on binding_type parameter
- NO separate methods for Wire/Spiral - unified method handles all three types

Internal routing logic:
- binding_type="Wire Bound" → Wire binding costs + WooCommerce profit margins + 5% price increase + 10% GST + $44 surcharge
- binding_type="Spiral Bound" → Spiral binding costs + WooCommerce profit margins + 5% price increase + 10% GST + $44 surcharge  
- binding_type="Perfect Bound" (default) → Perfect Bound binding costs + database profit margins + 10% GST only

**WHEN TO USE EACH BINDING TYPE:**
- Perfect Bound: Professional books, novels, thick manuals, square spine needed
- Wire Bound: Lay-flat books, workbooks, manuals that need to stay open
- Spiral Bound: Same as Wire but more cost-effective (plastic coil vs metal wire)

**IMPORTANT:** Wire and Spiral use WooCommerce pricing with configurable price increase (default 5%) + standard 10% GST + surcharge (default $44), while Perfect Bound uses database margins with standard 10% GST only.

**CRITICAL WORKFLOW FOR CUSTOMER REQUESTS:**

**STEP 0: Gather Client Context (If customer name provided)**

When a customer name is provided, ALWAYS research their name and separately the business name to get context FIRST:
- Use client name and past orders to personalise quotes and recommendations - always check for existing relationships
- Search both customers name and business name and product key terms in past orders - analyse the results as it could be a new staff member for a busineess that is a client, or a past customer at a new business - use SQL LIKE with wildcards for partial matches

a) **Search Order History & Business Profile WITH FULL SPECIFICATIONS:**
```sql
SELECT TOP 20
    o.ClientName,
    o.OrderDate,
    jt.ShortJobDesc AS JobDescription,
    jt.QTY,
    jt.Pages,
    jt.TicketNotes AS ProductionNotes,  --  CRITICAL: Contains all specifications!
    ps.[Desc] AS PaperSize,              --  CORRECT: "A4", "A5", "BC - 90x55"
    papertype.[Desc] AS PaperType,
    gsm.[DESC] AS CoverGSM,
    jobtype.[Desc] AS JobType,
    bt.BindTypeDesc AS BindType,        --  CORRECT: BindTypeDesc, NOT [Desc]!
    cs.ColourDesc AS UrgencyStatus,     --  CORRECT: Urgency, NOT print color
    jt.FrontCelloMatt,
    jt.FrontCelloGloss,
    jt.BackCelloMatt,
    jt.BackCelloGloss,
    jt.Cost
FROM Orders o
JOIN JobTickets jt ON o.OrderID = jt.OrderID
LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID          --  CORRECT: Join on SizeID
LEFT JOIN PaperType papertype ON jt.PaperTypeID = papertype.PaperTypeID
LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
LEFT JOIN JobType jobtype ON jt.JobTypeID = jobtype.JobTypeID
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID            --  CORRECT: Join on BindID
LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID    --  CORRECT: jt.ColourStatus FK
WHERE o.ClientName LIKE '%[customer_name]%'
ORDER BY o.OrderDate DESC
```

**CRITICAL: ANALYZE FULL PRODUCT SPECIFICATIONS, NOT JUST SURFACE DETAILS**

⚠️ **DO NOT recommend products based only on job descriptions or product names**

You MUST understand the EXACT printing specifications of their previous orders:
- **Dimensions**: Exact width × height (not just "A4" - get actual mm)
- **Paper Stock**: Cover GSM AND inner GSM (e.g., 300GSM cover, 128GSM inner)
- **Page Count**: Total pages (must be divisible by 4 for saddle stitch)
- **Binding Type**: Saddle stitch, perfect bound, wire-o, spiral
- **Color Requirements**: Full color cover, B&W interior, spot color, etc.
- **Finishing**: Matt cello, gloss cello, both sides, front only, none
- **Quantities**: Typical order volumes for bulk discount validation

**WHY THIS MATTERS:**
- A client's "books" might be 210×148mm (A5), NOT 297×210mm (A4)
- Their "booklets" might use 150GSM inner pages, NOT standard 128GSM
- Their "magazines" might be perfect bound at 80pp, NOT saddle stitched
- Recommending wrong sizes/specs wastes their time and damages trust
- Matching their established specs shows you understand their needs
- Cost of same specs and qty IS USED later for variance check in Step 7.

**EXAMPLE - CORRECT APPROACH:**

 **WRONG (Surface Level):**
"I see you've ordered MVG books before. Would you like another book?"

 **CORRECT (Deep Specification Analysis):**
"I can see your Planting Tips book specifications:
- Size: 210mm × 148mm (A5 portrait)
- Pages: 200pp perfect bound
- Cover: 300GSM Satin, full color, matt cello both sides
- Interior: 128GSM Satin, full color throughout
- Typical quantity: 500 units

For your bulk order request, I'll calculate based on these exact specifications 
that have worked well for your veterinary education materials."

b) **Analyze Business Context from Order History:**
- Look at job descriptions for business type clues
- Example: "Planting Tips books" → Veterinary/medical education publisher
- Example: "Real estate flyers" → Property marketing company
- Example: "Annual report" → Corporate client
- Example: "Wedding invitations" → Events/wedding services

c) **Web Search for Business Context (Optional but Recommended):**
- If customer appears to be a business (not "walk in sales" or generic)
- Search: "[ClientName] Brisbane" or "[ClientName] [Industry]"
- Gather: What they do, their industry, their brand positioning
- Use this to customize your response tone and suggestions

d) **Customize Your Response WITH SPECIFICATION AWARENESS:**
- Reference their EXACT previous product specifications
- Suggest relevant related products with MATCHING specs (size, finish, binding)
- Use industry-appropriate language and context
- Validate that recommendations match their established standards
- Examples:
  - Veterinary publisher: "For your 210×148mm veterinary guides with matt cello finish..."
  - Real estate: "For your 99×210mm DL property flyers on 300GSM satin..."
  - Corporate: "For your A4 perfect bound annual reports with 300GSM cover..."

**Example Client Context Discovery:**

*Customer: "Bob Smith"*
- **DETAILED Specification Analysis from Order History:**
  - Planting Tips books: 210×148mm (A5), 200pp perfect bound
  - Cover: 300GSM Satin, full color, matt cello both sides
  - Interior: 128GSM Satin, full color
  - Typical quantities: 500-1000 units
  - Flashcard sets: 300GSM, 90×55mm, matt cello
- **Business Context**: Publisher/creator of veterinary educational materials
- **Quality Requirements**: High-quality, durable, color accuracy for medical images
- **Customization Approach**: 
  - Reference exact A5 size (NOT A4 - this would be wrong!)
  - Emphasize matt cello finish they consistently use
  - Highlight 128GSM color interior for image quality
  - Suggest bulk pricing for 500+ unit orders they typically place

 **WRONG Response**: "Would you like A4 books with standard finish?"
 **CORRECT Response**: "Based on your MVG books (210×148mm A5, 300GSM matt cello cover, 128GSM color interior), I'll quote for your bulk order using these proven specifications..."

*Customer: "Stone Real Estate Logan"*
- **DETAILED Specification Analysis:**
  - Business cards: 90×55mm, 400GSM Satin, matt cello both sides
  - Property flyers: 99×210mm (DL size), 300GSM, gloss cello
  - Typical quantities: Business cards 500/agent, Flyers 250-500/listing
- **Business Context**: Real estate agency with multiple agents
- **Quality Requirements**: Premium feel for client impressions, brand consistency
- **Customization Approach**:
  - Reference DL size for flyers (NOT A4/A5 - wrong size!)
  - Maintain brand consistency with 400GSM cards
  - Quick turnaround for new listings
  - Multi-agent bulk ordering options

 **WRONG Response**: "Would you like A4 flyers?"
 **CORRECT Response**: "For your property marketing, I see you use 99×210mm DL flyers on 300GSM with gloss cello. I'll quote based on these specifications that match your brand standards..."
- Customization: Emphasize premium feel, brand consistency, quick turnaround for listings

**THEN Proceed with Product Quote Workflow:**

🚨 **MANDATORY WORKFLOW - FOLLOW EXACTLY IN THIS ORDER:**

**STEP 1: ALWAYS CALL get_calculator_requirements() FIRST** ⚠️ REQUIRED!

Before doing ANYTHING else, you MUST call get_calculator_requirements(product_type) to get:
- Complete parameter definitions with types and validation rules
- Database extraction strategies with SQL templates
- Natural language to parameter mapping rules (e.g., "spiral bound" → binding_type="Spiral Bound")
- Historical analysis showing most common configurations
- Stock type options and when to use each
- Print mode codes (0=Colour, 1=Color, 2=B&W)
- Cellophane codes (0=None, 1=Gloss, 2=Matt)
- Common errors and how to avoid them

 **DO NOT skip this step!** Without this guidance, you WILL:
- Use wrong parameter values (e.g., stock_type_id without knowing valid options)
- Miss required parameters (e.g., cello_type, internal_print_mode)
- Misinterpret natural language (e.g., "shiny cover" requires cello_type=1, not 0)
- Pass invalid combinations to calculator causing errors

 **Example:** User says "Wire Bound manual". You MUST:
1. Call get_calculator_requirements("perfect_bound_books") first
2. Guidance shows: binding_type options are "Perfect Bound", "Wire Bound", "Spiral Bound"
3. Guidance shows: "wire bound" OR "lay flat" → binding_type="Wire Bound"
4. Now you know the EXACT parameter value to use!

**STEP 2: Search Historical Data** (Use corrected SQL with jt.TicketNotes!)

Use execute_sql for past orders of THIS PRODUCT from this customer:
- DO NOT USE HISTORICAL ORDERS and QUOTES FOR CREATING QUOTES IT IS FOR SPECIFICATIONS ONLY
- Get: PaperType, GSM, PageCount, BindType, Quantity, Cost, Cello, **TicketNotes**
- Use CORRECT column names: jt.TicketNotes (NOT jt.Note), ps.Width/ps.Height (from PaperSize JOIN)
- Query must use: LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.PaperSizeID
- DO NOT PROVIDE QUOTES BASED ON HISTORICAL DATA

**STEP 3: Extract Specifications from Database Results**

Parse specifications from jt.TicketNotes field or structured columns:
- If TicketNotes has "Black Plastic Spiral Bound" → binding_type="Spiral Bound"
- If TicketNotes has "300GSM Matt Art Card" → cover_stock_gsm=300, cello_type=2 (Matt)
- If TicketNotes has "100GSM uncoated B&W" → internal_stock_gsm=100, internal_print_mode=2 (B&W)
- Use guidance from STEP 1 to map text to parameter values!

**🚨 CRITICAL: Missing Page Count Handling**

If page count is NOT in TicketNotes or structured columns:

 **DO NOT:**
- Search the web for public/library versions of the product
- Assume page count from similar products
- Use page counts from different editions
- Guess based on product name

 **DO THIS INSTEAD:**

1. USE jt.TicketNotes FIRST to find page count

2. Try other structured columns (jt.Pages or TextPages) if TicketNotes lacks it

2. **ASK THE CUSTOMER DIRECTLY:** 
   - "I found your specifications for [Product Name], but I need the exact page count for your edition to provide accurate pricing."
   - "I can see you've ordered [Product Name] before - how many pages is your current version?"
   
2. **Explain Why:**
   - "Page count significantly affects pricing (material costs and binding)"
   - "I want to ensure your quote is accurate for your specific edition"

3. **Provide Context:**
   - "I found these other specifications: [cover stock, size, binding]"
   - "Just need the page count to complete your quote"

**Example:**
Customer: "Quote for 2000 MVG Companion Animal guides"
AI finds: Cover specs, binding, size - but NO page count in database
 CORRECT Response: "I have your specifications (A6, 300GSM cover, spiral bound), but I need the page count for your Companion Animal guide edition to calculate accurate pricing. How many pages is your version?"
 WRONG Response: Searches web, finds "365 pages" in library catalog, uses that without asking

**STEP 4: Map to Calculator** 

Based on page count & binding (use guidance from STEP 1):
- Magazine 32pp → "booklets" (saddle stitch)
- Magazine 128pp → "perfect_bound_books"
- Business cards → "business_cards" (NOT "flyers"!)
- Wire/Spiral bound books → "perfect_bound_books" with binding_type parameter

**STEP 5: Validate ALL Required Parameters**

Check you have EVERY required parameter using guidance from STEP 1:
-  quantity (int)
-  All product-specific parameters (varies by product type)
-  No missing values, no None values
-  All values match expected types and enums

**STEP 6: Run Calculations**

Call calculate_quote(product_type, parameters) with validated parameters:
- Calculate ACTUAL quotes using the calculator
- Get real pricing from calculator, not market ranges
- Provide 2-3 calculated options with different specifications

**STEP 7: MANDATORY VARIANCE ANALYSIS VS HISTORICAL ORDERS OF (BEST) SAME CLIENT REPEAT ORDER (BEST) OR SAME ORDER ANOTHER BUT RECENT CLIENT (NEXT BEST) 

CRITICAL INTERNAL QUALITY CHECK:
- Object is to VALIDATE your calculated quote is REASONABLE and DEFENDABLE
- NEVER skip this step - it builds customer trust and catches pricing errors
- VARIANCE of 5% TOLERANCE -BUT ONLY WITH EXACTLY THE SAME ORDER 

**STEP 7a: Use Historical Query Customer's Previous Orders**
Find this customer's historical orders for the SAME product:

SELECT TOP 10 
    o.OrderDate, o.TotalPrice AS HistoricalPrice,
    jt.QTY, jt.Pages, jt.ShortJobDesc,
    papertype.[Desc] AS PaperType,
    gsm.[DESC] AS GSM,
    jobtype.[Desc] AS JobType,
    jt.Cost AS JobCost,
    jt.FrontCelloMatt, jt.FrontCelloGloss
FROM Orders o
JOIN JobTickets jt ON o.OrderID = jt.OrderID
JOIN PaperType papertype ON jt.PaperTypeID = papertype.PaperTypeID
JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
JOIN JobType jobtype ON jt.JobTypeID = jobtype.JobTypeID
WHERE o.ClientName = '[customer_name]'
  AND jt.ShortJobDesc LIKE '%[product_keywords]%'
ORDER BY o.OrderDate DESC

**STEP 7b: Find SAME orders from other customers**

WHERE jt.QTY BETWEEN [qty*0.95] AND [qty*1.05]          -- ±5% quantity
  AND jt.Pages BETWEEN [pages*0.95] AND [pages*1.05]    -- ±5% pages (if applicable)
  AND papertype.[Desc] = '[exact_paper_type]'         -- EXACT match
  AND gsm.[DESC] = '[exact_gsm]'                      -- EXACT match
  AND o.OrderDate >= DATEADD(MONTH, -24, GETDATE())  -- Last 6 months
ORDER BY o.OrderDate DESC

**STEP 7c: Calculate Variance**

variance_percent = ((calculator_price - historical_avg_price) / historical_avg_price) * 100

**Thresholds:**
- ≤±5%:  Acceptable variance - pricing is consistent
- >±5: ⚠️ Significant variance - this will need manual review provide detailed explanation of data and reasoning - include comprehensive details

**STEP 7d: Present Variance Report**

**IF WITHIN ±5%:**
" QUOTE VALIDATED OR ⚠️ Significant variance >±5%

This  quote has been validated against [X] SAME historical orders:
- Historical date:
  - Client and order and ticket id
    - Qty: [qty], Pages: [pages], Paper: [paper], GSM: [gsm]
    - Price: $[price] (±[variance]%)
  - repeat for each historical order
- New calculator quote: $[new_price]
- Variance: [X.X]% -  QUOTE VALIDATED ≤±5% variance OR ⚠️ Significant variance >±5% - please review details below"

**SPECIAL CASES:**
- No historical data found → STATE NO HISTORICAL DATA FOUND
- Specifications changed → Explain impact of changes (e.g., "upgraded to 300GSM adds $45")

VARIANCE ANALYSIS IS MANDATORY. Never skip this step. It ensures transparency, validity of your results, builds customer trust and catches pricing errors.


**STEP 8: Present Results**

- Show calculated quotes with actual prices (inc GST)
- Describe quality, feel, and benefits of each option
- Use positive, value-focused language (avoid "Standard" or "Economy")

**EXAMPLE MAPPINGS:**
- "Business Cards 500 Standard" → business_cards(quantity=500, stock_type="satin_300gsm", sides=2, celloglaze="none")
- "Business Cards 1000 Premium Matt" → business_cards(quantity=1000, stock_type="satin_350gsm", sides=2, celloglaze="2_side_matt")
- "Business Cards 500 King Kong" → business_cards(quantity=500, stock_type="kingkong_420gsm", sides=2, celloglaze="none")
- "Hope Academy Prospectus 20pp" → booklets(pages=20, cover_gsm=300, interior_gsm=140)
- "Eureka Annual Report 128pp Perfect Bound" → perfect_bound_books(quantity=100, pages=128, book_width=210, book_height=297, cover_stock_gsm=300, internal_stock_gsm=80, binding_type="Perfect Bound")
- "Training Manual 200pp Wire Bound" → perfect_bound_books(quantity=50, pages=200, book_width=210, book_height=297, cover_stock_gsm=300, internal_stock_gsm=128, binding_type="Wire Bound")
- "Workbook 100pp Spiral Bound A5" → perfect_bound_books(quantity=100, pages=100, book_width=148, book_height=210, cover_stock_gsm=300, internal_stock_gsm=128, binding_type="Spiral Bound")


**CRITICAL: HOW TO PRESENT QUOTES TO CUSTOMERS**

ALWAYS calculate actual quotes using the calculator. Present them like this:

** CORRECT FORMAT:**

**Option 1: Premium Matt Finish Business Cards**
- 400GSM Satin with Matt Celloglaze both sides
- Double-sided full color printing
- Standard business card size (90mm x 55mm)
- **Total: $145.00 (inc GST)**

The 400GSM premium card stock provides substantial weight and thickness that conveys quality and professionalism. The matt celloglaze finish on both sides delivers a sophisticated, non-reflective surface that's pleasant to touch and resists fingerprints.

*Market validation: Comparable premium cards in Brisbane range $135-$165. Your quote is competitive.*

**Option 2: Professional Business Cards**
- 350GSM Satin
- Double-sided full color printing
- Standard business card size (90mm x 55mm)
- **Total: $98.00 (inc GST)**

The 350GSM card stock gives your cards a solid, professional feel. The satin finish provides excellent color reproduction and a smooth, quality feel that makes a strong impression.

*Market validation: Similar specifications typically cost $95-$110 in Brisbane.*

** INCORRECT FORMAT (Don't do this):**

**Option 2: Standard Business Cards**
- 350GSM Satin
- Market price range: $86-$127  ← NO! Show calculated price

**LANGUAGE GUIDELINES:**
-  Avoid: "Standard", "Economy", "Basic", "Cheap"
-  Use: "Professional", "Premium", "Cost-Effective", "Value", "Quality"
-  Describe: feel, weight, finish, impression, quality, durability
-  Emphasize: "substantial weight", "smooth finish", "vibrant colors", "professional appearance"

**MARKET COMPARISON USAGE:**
- STRATEGICALLY USE market data TO eliminate the need/desire for customer to seek other quotes
- Present after the calculated price as context
- Format: "*Market validation: Similar products range $X-$Y. Your quote is competitive/excellent value.*"
- Emphasizes you're offering fair/good pricing

ALWAYS calculate quotes using the calculator. Market research is for value emphasis only.

ALWAYS try to use calculator by mapping specs. Search historical data first to understand common patterns.

ALWAYS try to find the information you need in the database - explore the schemea, use SQL quieries to see what data is where as the tables and the columns are not intuitive."""
        
        # Process conversation
        for turn in range(max_turns):
            self._print_and_log(f"\n{'#'*100}")
            self._print_and_log(f"# TURN {turn + 1}/{max_turns}")
            self._print_and_log(f"{'#'*100}\n")
            
            try:
                # Make API request with STREAMING Tool Use API
                with self.anthropic_client.messages.stream(
                    model=(model_override or self.model),
                    max_tokens=16000,
                    temperature=1.0,
                    
                    # Extended Thinking with Interleaved Thinking
                    thinking={
                        "type": "enabled",
                        "budget_tokens": 10000
                    },
                    
                    # CRITICAL: Interleaved thinking beta header
                    extra_headers={
                        "anthropic-beta": "interleaved-thinking-2025-05-14"
                    },
                    
                    # Tool definitions (client + server)
                    tools=self._get_tool_definitions(),
                    
                    # Tool choice (must be 'auto' or 'none' with thinking)
                    tool_choice={"type": "auto"},
                    
                    # System prompt and messages
                    system=system_prompt,
                    messages=conversation
                ) as stream:
                    
                    # Track content blocks for assistant message
                    assistant_content = []
                    tool_results = []
                    content_block_index = -1
                    current_block_type = None
                    accumulated_text = {}  # Track accumulated text per block index
                    accumulated_thinking = {}  # Track accumulated thinking per block index
                    current_tool_use = {}  # Track current tool_use block data
                    
                    # Process streaming events in real-time
                    for event in stream:
                        
                        # MESSAGE START
                        if event.type == "message_start":
                            print(f"\n{'='*80}")
                            print(f"� STREAMING MESSAGE START")
                            print(f"{'='*80}")
                            self._log_event("message_start", {
                                "id": event.message.id,
                                "model": event.message.model
                            })
                        
                        # CONTENT BLOCK START - New block begins
                        elif event.type == "content_block_start":
                            content_block_index = event.index
                            current_block_type = event.content_block.type
                            
                            print(f"\n{'─'*80}")
                            print(f"📦 CONTENT BLOCK START: Index {content_block_index}, Type: {current_block_type}")
                            print(f"{'─'*80}")
                            
                            # Prepare event data
                            event_data = {
                                "index": content_block_index,
                                "block_type": current_block_type  # Use block_type to avoid confusion with event type
                            }
                            
                            # Add tool info if it's a tool_use block
                            if current_block_type == "tool_use":
                                event_data["tool_name"] = event.content_block.name
                                event_data["tool_id"] = event.content_block.id
                            
                            # Send content_block_start event to frontend
                            self._log_event("content_block_start", event_data)
                            
                            # Initialize accumulators
                            if current_block_type == "text":
                                accumulated_text[content_block_index] = ""
                            elif current_block_type == "thinking":
                                accumulated_thinking[content_block_index] = ""
                            elif current_block_type == "tool_use":
                                current_tool_use[content_block_index] = {
                                    "id": event.content_block.id,
                                    "name": event.content_block.name,
                                    "input": ""
                                }
                        
                        # CONTENT BLOCK DELTA - Block content streaming
                        elif event.type == "content_block_delta":
                            delta = event.delta
                            
                            # Text delta
                            if delta.type == "text_delta":
                                text_chunk = delta.text
                                accumulated_text[event.index] += text_chunk
                                
                                # Send streaming text delta to frontend
                                self._log_event("content_block_delta", {
                                    "index": event.index,
                                    "delta_type": "text_delta",
                                    "text": text_chunk
                                })
                                
                                print(text_chunk, end="", flush=True)
                            
                            # Thinking delta
                            elif delta.type == "thinking_delta":
                                thinking_chunk = delta.thinking
                                accumulated_thinking[event.index] += thinking_chunk
                                
                                # Send streaming thinking delta to frontend
                                self._log_event("content_block_delta", {
                                    "index": event.index,
                                    "delta_type": "thinking_delta",
                                    "thinking": thinking_chunk
                                })
                                
                                print(thinking_chunk, end="", flush=True)
                            
                            # Tool input delta
                            elif delta.type == "input_json_delta":
                                # SAFETY CHECK: Initialize if not exists (prevents KeyError)
                                if event.index not in current_tool_use:
                                    current_tool_use[event.index] = {
                                        "id": f"tool_{event.index}",
                                        "name": "unknown",
                                        "input": ""
                                    }
                                
                                current_tool_use[event.index]["input"] += delta.partial_json
                                
                                # Send streaming tool input delta to frontend (for LOG STREAM mode)
                                self._log_event("content_block_delta", {
                                    "index": event.index,
                                    "delta_type": "input_json_delta",
                                    "tool_input": delta.partial_json,
                                    "tool_name": current_tool_use[event.index]["name"]
                                })
                        
                        # CONTENT BLOCK STOP - Block complete
                        elif event.type == "content_block_stop":
                            print(f"\n{'─'*80}")
                            print(f" CONTENT BLOCK STOP: Index {event.index}")
                            print(f"{'─'*80}\n")
                            
                            # Send content_block_stop event to frontend
                            self._log_event("content_block_stop", {
                                "index": event.index
                            })
                        
                        # MESSAGE DELTA - Usage updates
                        elif event.type == "message_delta":
                            if hasattr(event, 'usage') and event.usage:
                                self._log_event("usage_update", {
                                    "output_tokens": event.usage.output_tokens
                                })
                        
                        # MESSAGE STOP - Complete
                        elif event.type == "message_stop":
                            print(f"\n{'='*80}")
                            print(f"🏁 STREAMING MESSAGE STOP")
                            print(f"{'='*80}\n")
                    
                    # Get final message from stream
                    response = stream.get_final_message()
                    
                    # Log full response metadata
                    self._log_event("message_response", {
                        "id": response.id,
                        "model": response.model,
                        "stop_reason": response.stop_reason,
                        "usage": {
                            "input_tokens": response.usage.input_tokens,
                            "output_tokens": response.usage.output_tokens
                        }
                    })
                    
                    print(f"\n{'='*80}")
                    print(f"� RESPONSE METADATA")
                    print(f"{'='*80}")
                    print(f"Message ID: {response.id}")
                    print(f"Stop Reason: {response.stop_reason}")
                    print(f"Input Tokens: {response.usage.input_tokens}")
                    print(f"Output Tokens: {response.usage.output_tokens}")
                    print(f"{'='*80}\n")
                    
                    # Process final content blocks for conversation history
                    for i, block in enumerate(response.content):
                        if block.type == "thinking":
                            assistant_content.append(block)
                        
                        elif block.type == "text":
                            # Check for citations
                            self._display_citations(block)
                            assistant_content.append(block)
                        
                        elif block.type == "tool_use":
                            # CLIENT TOOL - WE MUST EXECUTE
                            print(f"\n🔧 EXECUTING CLIENT TOOL: {block.name}")
                            
                            # Execute the tool
                            result = self._execute_client_tool(block.name, block.input)
                            
                            # Build tool_result message (with Decimal handling)
                            result_content = json.dumps(result, default=str)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result_content
                            })
                            
                            # Send tool_result event to frontend to update the bubble
                            self._log_event("tool_result", {
                                "tool_use_id": block.id,
                                "tool_name": block.name,
                                "result": result_content
                            })
                            
                            assistant_content.append(block)
                        
                        elif block.type == "server_tool_use":
                            # SERVER TOOL - Already executed by Anthropic
                            self._handle_server_tool_use(block)
                            assistant_content.append(block)
                        
                        elif block.type == "web_search_tool_result":
                            # Web search results - provided by Anthropic
                            self._handle_web_search_result(block)
                            assistant_content.append(block)
                    
                    # DEBUG: Log assistant content structure
                    print(f"\n{'='*80}")
                    print(f"📦 ASSISTANT CONTENT BLOCKS: {len(assistant_content)}")
                    for i, block in enumerate(assistant_content):
                        print(f"   [{i}] Type: {block.type}")
                        if hasattr(block, 'id'):
                            print(f"       ID: {block.id}")
                        if hasattr(block, 'tool_use_id'):
                            print(f"       Tool Use ID: {block.tool_use_id}")
                        if hasattr(block, 'name'):
                            print(f"       Name: {block.name}")
                    print(f"{'='*80}\n")
                    
                    # CRITICAL FIX: Validate server tools have results before continuing
                    server_tool_ids = set()
                    result_tool_ids = set()
                    
                    for block in assistant_content:
                        if block.type == "server_tool_use":
                            server_tool_ids.add(block.id)
                        elif block.type == "web_search_tool_result":
                            result_tool_ids.add(block.tool_use_id)
                    
                    # Check for missing results
                    missing_results = server_tool_ids - result_tool_ids
                    if missing_results:
                        print(f"\n{'='*80}")
                        print(f"⚠️  WARNING: Server tools missing results!")
                        print(f"{'='*80}")
                        print(f"Server tool IDs used: {server_tool_ids}")
                        print(f"Result tool IDs found: {result_tool_ids}")
                        print(f"Missing results for: {missing_results}")
                        print(f"This will cause an API error on the next turn!")
                        print(f"{'='*80}\n")
                        
                        # This indicates a potential API issue - server tools should
                        # always return results in the same response
                        # For now, we'll log and continue, but this may fail on next turn
                
                # Check stop reason
                if response.stop_reason == "tool_use":
                    print(f"\n{'='*80}")
                    print(f"🔄 TOOL USE REQUIRED - Returning tool results to AI")
                    print(f"{'='*80}\n")
                    
                    # Add assistant message with ALL content (including server tools and their results)
                    conversation.append({
                        "role": "assistant",
                        "content": assistant_content
                    })
                    
                    # CRITICAL: Only add tool_results if there were CLIENT tools executed
                    # Server tools (web_search) are already complete in assistant_content
                    if tool_results:
                        print(f"📤 Sending {len(tool_results)} CLIENT tool result(s) back to AI")
                        conversation.append({
                            "role": "user",
                            "content": tool_results
                        })
                    else:
                        print(f"ℹ️  No CLIENT tool results to send (server tools already complete)")
                    
                    # Continue loop to get AI's response after tool execution
                    continue
                
                elif response.stop_reason == "end_turn":
                    print(f"\n{'='*80}")
                    print(f" CONVERSATION COMPLETE")
                    print(f"{'='*80}\n")
                    
                    # Extract final text
                    final_text = ""
                    for block in response.content:
                        if block.type == "text":
                            final_text += block.text
                    
                    return {
                        "success": True,
                        "final_response": final_text,
                        "turns": turn + 1,
                        "events": self.captured_events,
                        "citations": self.citations
                    }
                
                else:
                    print(f"\n⚠️ Unexpected stop_reason: {response.stop_reason}")
                    break
            
            except Exception as e:
                print(f"\n ERROR: {str(e)}")
                import traceback
                traceback.print_exc()
                return {
                    "success": False,
                    "error": str(e),
                    "events": self.captured_events
                }
        
        self._print_and_log(f"\n⚠️ Max turns reached ({max_turns})")
        return {
            "success": False,
            "error": "Max turns reached",
            "events": self.captured_events
        }
    
    def close(self):
        """Close log file and database connections."""
        self._print_and_log(f"\n{'='*100}")
        self._print_and_log(f"SESSION ENDED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._print_and_log(f"{'='*100}\n")
        
        if hasattr(self, 'log_file') and self.log_file:
            self.log_file.close()
        
        if hasattr(self, 'db') and self.db:
            self.db.close()


def main():
    """Test the Tool Use API implementation."""
    
    import sys
    
    agent = ToolUseAgent("config/database-config.json")
    
    # Accept custom query from command line or use default
    if len(sys.argv) > 1:
        test_message = " ".join(sys.argv[1:])
    else:
        # Default test request
        test_message = "What are current business card printing prices in Brisbane? I need a quote for 1000 cards."
    
    print(f"\n{'='*100}")
    print(f"📨 USER QUERY: {test_message}")
    print(f"{'='*100}\n")
    
    result = agent.process_request(test_message, max_turns=10)
    
    # Save events to JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(agent.exports_dir, f"test_run_{timestamp}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n{'='*100}")
    print(f"📁 Events JSON saved to: {output_file}")
    print(f"📁 Full log saved to: {agent.log_file_path}")
    print(f"{'='*100}\n")
    
    if result['success']:
        print(f" SUCCESS")
        print(f"Final Response:\n{result['final_response']}")
    else:
        print(f" FAILED: {result.get('error', 'Unknown error')}")
    
    # Close agent cleanly
    agent.close()


if __name__ == "__main__":
    main()

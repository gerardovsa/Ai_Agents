"""
Google Sheets Markdown Formatter v3.1
Converts markdown syntax to Google Sheets API formatting

BASIC FORMATTING:
- **bold text** → Bold formatting
- *italic* → Italic formatting
- ~~strikethrough~~ → Strikethrough
- __underline__ → Underline
- # Headers → Bold + larger font + gray background

NUMBER FORMATTING:
- [$]1000 → $1,000.00 (currency)
- [%]75 → 75% (percentage)
- [DATE]2025-12-16 → Dec 16, 2025
- [#]1234.5 → 1,234.50 (number with commas)

FORMULAS (v3.1):
- [FORMULA]=SUM(A1:A10) → Direct Excel formula
- [SUM:A1:A10] → Shorthand for =SUM(A1:A10)
- [AVG:B2:B50] → Shorthand for =AVERAGE(B2:B50)
- [COUNT:C1:C100] → Shorthand for =COUNT(C1:C100)
- [MIN:D1:D10] / [MAX:E1:E10] → Min/Max formulas

COLORS:
- [RED]text[/RED] or [R]text → Red text
- {LG}text → Light green background

ADVANCED:
- [SIZE:12]text → Custom font size
- [WRAP]text or [NOWRAP]text → Text wrapping
- [MERGE:3]text → Merge 3 cells
- [DROPDOWN:Red,Green,Blue]Red → Dropdown validation
- [IF>100:RED]125 → Conditional formatting

ALIGNMENT:
- (L)text → Left align
- (C)text → Center align
- (R)text → Right align
"""

import re
from typing import List, Dict, Any, Tuple
from datetime import datetime


class MarkdownToSheetsFormatter:
    """Convert markdown formatting to Google Sheets API format requests - v3.0 Enhanced"""
    
    # Color mapping for [COLOR] tags (text colors)
    # Supports both verbose ([RED]) and shortened ([R]) codes
    COLORS = {
        'RED': {'red': 0.9, 'green': 0.2, 'blue': 0.2},
        'R': {'red': 0.9, 'green': 0.2, 'blue': 0.2},  # v2.0 shortened
        'GREEN': {'red': 0.2, 'green': 0.8, 'blue': 0.2},
        'G': {'red': 0.2, 'green': 0.8, 'blue': 0.2},  # v2.0 shortened
        'BLUE': {'red': 0.2, 'green': 0.5, 'blue': 0.9},
        'B': {'red': 0.2, 'green': 0.5, 'blue': 0.9},  # v2.0 shortened
        'YELLOW': {'red': 0.8, 'green': 0.6, 'blue': 0.0},  # Darker yellow for visibility
        'ORANGE': {'red': 0.9, 'green': 0.5, 'blue': 0.1},  # Darker orange for visibility
        'PURPLE': {'red': 0.7, 'green': 0.3, 'blue': 0.9},
        'P': {'red': 0.7, 'green': 0.3, 'blue': 0.9},  # v2.0 shortened
        'GRAY': {'red': 0.5, 'green': 0.5, 'blue': 0.5},
        'GR': {'red': 0.5, 'green': 0.5, 'blue': 0.5},  # v2.0 shortened
        'BLACK': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
        'BK': {'red': 0.0, 'green': 0.0, 'blue': 0.0},  # v2.0 shortened
    }
    
    # Background color mapping for [BG:COLOR] tags
    # Supports both verbose ([BG:LIGHTRED]) and shortened ({LR}) codes
    BG_COLORS = {
        'LIGHTGRAY': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
        'GRAY': {'red': 0.85, 'green': 0.85, 'blue': 0.85},
        'LIGHTRED': {'red': 0.95, 'green': 0.8, 'blue': 0.8},
        'LR': {'red': 0.95, 'green': 0.8, 'blue': 0.8},  # v2.0 shortened
        'LIGHTGREEN': {'red': 0.85, 'green': 0.95, 'blue': 0.85},
        'LG': {'red': 0.85, 'green': 0.95, 'blue': 0.85},  # v2.0 shortened
        'LIGHTBLUE': {'red': 0.85, 'green': 0.9, 'blue': 0.95},
        'LB': {'red': 0.85, 'green': 0.9, 'blue': 0.95},  # v2.0 shortened
        'LIGHTYELLOW': {'red': 0.98, 'green': 0.95, 'blue': 0.8},
        'LIGHTORANGE': {'red': 0.98, 'green': 0.9, 'blue': 0.8},
        'LIGHTPURPLE': {'red': 0.95, 'green': 0.85, 'blue': 0.95},
        'LP': {'red': 0.95, 'green': 0.85, 'blue': 0.95},  # v2.0 shortened
        'LIGHTGRAY': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
        'LGR': {'red': 0.9, 'green': 0.9, 'blue': 0.9},  # v2.0 shortened (duplicate for clarity)
        'WHITE': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
    }
    
    # Header styles
    HEADER_SIZES = {
        1: 18,  # # Header
        2: 16,  # ## Header
        3: 14,  # ### Header
    }
    
    # Number format patterns (v3.0)
    NUMBER_FORMATS = {
        'CURRENCY': '"$"#,##0.00',           # [$]1000 → $1,000.00
        'PERCENTAGE': '0.00%',                # [%]75 → 75.00%
        'NUMBER': '#,##0.00',                 # [#]1234.5 → 1,234.50
        'INTEGER': '#,##0',                   # [INT]1234 → 1,234
        'DATE': 'mmm dd, yyyy',               # [DATE]2025-12-16 → Dec 16, 2025
        'DATETIME': 'mmm dd, yyyy hh:mm',     # [DATETIME] → Dec 16, 2025 14:30
        'TIME': 'hh:mm:ss',                   # [TIME]14:30:00 → 14:30:00
    }
    
    def __init__(self):
        self.formatting_rules = []
        self.merge_requests = []  # Track cell merges (v3.0)
        self.validation_requests = []  # Track data validation (v3.0)
        self.conditional_formats = []  # Track conditional formatting (v3.0)
        
    def parse_cell_markdown(self, text: str, row_idx: int = 0, col_idx: int = 0) -> Tuple[str, Dict[str, Any]]:
        """
        Parse markdown in a single cell and return clean text + formatting
        
        Args:
            text: Cell text with markdown (e.g., "**Bold** and *italic*")
            row_idx: Row index for merge/conditional tracking
            col_idx: Column index for merge/conditional tracking
            
        Returns:
            (clean_text, format_dict): Clean text and Google Sheets format dict
        
        v3.0 Enhanced Features:
        - ~~strikethrough~~ → Strikethrough
        - __underline__ → Underline
        - [$]1000 → $1,000.00 (currency format)
        - [%]75 → 75% (percentage format)
        - [DATE]2025-12-16 → Formatted date
        - [SIZE:14]text → Custom font size
        - [WRAP]text → Wrap text
        - [NOWRAP]text → No wrap
        - [MERGE:3]text → Merge 3 cells
        - [DROPDOWN:opt1,opt2]value → Dropdown validation
        - [IF>100:RED]125 → Conditional formatting (red if >100)
        """
        if not isinstance(text, str):
            return str(text), {}
        
        clean_text = text
        text_format = {}
        number_format = None
        wrap_strategy = None
        merge_count = None
        dropdown_options = None
        conditional_rule = None
        
        # v3.0: Check for MERGE [MERGE:3]text
        merge_match = re.match(r'^\[MERGE:(\d+)\](.*)$', clean_text)
        if merge_match:
            merge_count = int(merge_match.group(1))
            clean_text = merge_match.group(2)
            # Store merge request for later processing
            self.merge_requests.append({
                'row': row_idx,
                'col': col_idx,
                'count': merge_count
            })
        
        # v2.0: Check for alignment (L), (R), (C) - process EARLY before other syntax
        align_match = re.match(r'^\(([LRC])\)', clean_text)
        if align_match:
            align_code = align_match.group(1)
            clean_text = clean_text[3:]  # Remove (L), (R), or (C)
            if align_code == 'L':
                text_format['horizontalAlignment'] = 'LEFT'
            elif align_code == 'R':
                text_format['horizontalAlignment'] = 'RIGHT'
            elif align_code == 'C':
                text_format['horizontalAlignment'] = 'CENTER'
        
        # v3.0: Check for DROPDOWN [DROPDOWN:Red,Green,Blue]Red
        dropdown_match = re.match(r'^\[DROPDOWN:(.*?)\](.*)$', clean_text)
        if dropdown_match:
            dropdown_options = [opt.strip() for opt in dropdown_match.group(1).split(',')]
            clean_text = dropdown_match.group(2)
            # Store validation request
            self.validation_requests.append({
                'row': row_idx,
                'col': col_idx,
                'options': dropdown_options
            })
        
        # v3.0: Check for CONDITIONAL FORMATTING [IF>100:RED]125
        conditional_match = re.match(r'^\[IF([<>=!]+)([\d.]+):([A-Z]+)\](.*)$', clean_text)
        if conditional_match:
            operator = conditional_match.group(1)
            threshold = conditional_match.group(2)
            color_code = conditional_match.group(3)
            clean_text = conditional_match.group(4)
            # Store conditional format request
            if color_code in self.COLORS or color_code in self.BG_COLORS:
                self.conditional_formats.append({
                    'row': row_idx,
                    'col': col_idx,
                    'operator': operator,
                    'threshold': threshold,
                    'color': color_code
                })
        
        # v3.0: Check for NUMBER FORMATTING
        # [$]1000 → Currency
        if clean_text.startswith('[$]'):
            clean_text = clean_text[3:]
            number_format = self.NUMBER_FORMATS['CURRENCY']
        # [%]75 → Percentage (convert to decimal)
        elif clean_text.startswith('[%]'):
            clean_text = clean_text[3:]
            number_format = self.NUMBER_FORMATS['PERCENTAGE']
            # Convert percentage to decimal for Sheets
            try:
                if clean_text.replace('.', '', 1).replace('-', '', 1).isdigit():
                    clean_text = str(float(clean_text) / 100)
            except:
                pass
        # [#]1234.5 → Number with commas
        elif clean_text.startswith('[#]'):
            clean_text = clean_text[3:]
            number_format = self.NUMBER_FORMATS['NUMBER']
        # [INT]1234 → Integer with commas
        elif clean_text.startswith('[INT]'):
            clean_text = clean_text[5:]
            number_format = self.NUMBER_FORMATS['INTEGER']
        # [DATE]2025-12-16 → Date
        elif clean_text.startswith('[DATE]'):
            clean_text = clean_text[6:]
            number_format = self.NUMBER_FORMATS['DATE']
        # [DATETIME]...
        elif clean_text.startswith('[DATETIME]'):
            clean_text = clean_text[10:]
            number_format = self.NUMBER_FORMATS['DATETIME']
        # [TIME]14:30:00
        elif clean_text.startswith('[TIME]'):
            clean_text = clean_text[6:]
            number_format = self.NUMBER_FORMATS['TIME']
        
        # v3.0: Check for WRAPPING [WRAP] or [NOWRAP]
        if clean_text.startswith('[WRAP]'):
            clean_text = clean_text[6:]
            wrap_strategy = 'WRAP'
        elif clean_text.startswith('[NOWRAP]'):
            clean_text = clean_text[8:]
            wrap_strategy = 'OVERFLOW_CELL'
        
        # v3.1: Check for FORMULAS [FORMULA]=SUM(A1:A10) or [SUM:A1:A10]
        # Process AFTER number format prefixes are removed
        # Direct formula: [FORMULA]=SUM(A1:A10)
        formula_match = re.match(r'^\[FORMULA\](.*)$', clean_text)
        if formula_match:
            formula_text = formula_match.group(1)
            # Ensure formula starts with =
            if not formula_text.startswith('='):
                formula_text = f'={formula_text}'
            clean_text = formula_text
        # Shorthand formulas: [SUM:A1:A10], [AVG:B2:B50], [COUNT:C1:C100]
        elif clean_text.startswith('[SUM:'):
            shorthand_match = re.match(r'^\[SUM:(.*?)\](.*)$', clean_text)
            if shorthand_match:
                range_ref = shorthand_match.group(1)
                remaining = shorthand_match.group(2)
                clean_text = f'=SUM({range_ref}){remaining}'
        elif clean_text.startswith('[AVG:') or clean_text.startswith('[AVERAGE:'):
            shorthand_match = re.match(r'^\[(?:AVG|AVERAGE):(.*?)\](.*)$', clean_text)
            if shorthand_match:
                range_ref = shorthand_match.group(1)
                remaining = shorthand_match.group(2)
                clean_text = f'=AVERAGE({range_ref}){remaining}'
        elif clean_text.startswith('[COUNT:'):
            shorthand_match = re.match(r'^\[COUNT:(.*?)\](.*)$', clean_text)
            if shorthand_match:
                range_ref = shorthand_match.group(1)
                remaining = shorthand_match.group(2)
                clean_text = f'=COUNT({range_ref}){remaining}'
        elif clean_text.startswith('[MIN:'):
            shorthand_match = re.match(r'^\[MIN:(.*?)\](.*)$', clean_text)
            if shorthand_match:
                range_ref = shorthand_match.group(1)
                remaining = shorthand_match.group(2)
                clean_text = f'=MIN({range_ref}){remaining}'
        elif clean_text.startswith('[MAX:'):
            shorthand_match = re.match(r'^\[MAX:(.*?)\](.*)$', clean_text)
            if shorthand_match:
                range_ref = shorthand_match.group(1)
                remaining = shorthand_match.group(2)
                clean_text = f'=MAX({range_ref}){remaining}'
        
        # v3.0: Check for FONT SIZE [SIZE:14]text
        size_match = re.match(r'^\[SIZE:(\d+)\](.*)$', clean_text)
        if size_match:
            font_size = int(size_match.group(1))
            clean_text = size_match.group(2)
            text_format['fontSize'] = font_size
        
        # v2.0: Check for shortened text color [R]text (no closing tag)
        shortened_color_match = re.match(r'^\[([RGBPGRBK]+)\](.*)$', clean_text)
        if shortened_color_match:
            color_code = shortened_color_match.group(1)
            if color_code in self.COLORS:  # Validate it's a known code
                clean_text = shortened_color_match.group(2)
                text_format['foregroundColor'] = self.COLORS[color_code]
        
        # v2.0: Check for shortened background color {LR}text (no closing tag)
        shortened_bg_match = re.match(r'^\{([A-Z]+)\}(.*)$', clean_text)
        if shortened_bg_match:
            bg_code = shortened_bg_match.group(1)
            if bg_code in self.BG_COLORS:  # Validate it's a known code
                clean_text = shortened_bg_match.group(2)
                text_format['backgroundColor'] = self.BG_COLORS[bg_code]
        
        # v3.0: Check for strikethrough (~~text~~)
        if '~~' in clean_text:
            clean_text = re.sub(r'~~(.*?)~~', r'\1', clean_text)
            text_format['strikethrough'] = True
        
        # v3.0: Check for underline (__text__)
        if '__' in clean_text:
            clean_text = re.sub(r'__(.*?)__', r'\1', clean_text)
            text_format['underline'] = True
        
        # Check for bold (**text**)
        if '**' in clean_text:
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_text)
            text_format['bold'] = True
        
        # Check for italic (*text*)
        if '*' in clean_text and '**' not in text:
            clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)
            text_format['italic'] = True
        
        # Check for color tags [RED]text[/RED]
        for color_name, color_rgb in self.COLORS.items():
            pattern = f'\\[{color_name}\\](.*?)\\[/{color_name}\\]'
            if re.search(pattern, clean_text, re.IGNORECASE):
                clean_text = re.sub(pattern, r'\1', clean_text, flags=re.IGNORECASE)
                text_format['foregroundColor'] = color_rgb
                break
        
        # Check for background color tags [BG:LIGHTBLUE]text[/BG]
        bg_pattern = r'\[BG:([A-Z]+)\](.*?)\[/BG\]'
        bg_match = re.search(bg_pattern, clean_text, re.IGNORECASE)
        if bg_match:
            bg_color_name = bg_match.group(1).upper()
            if bg_color_name in self.BG_COLORS:
                clean_text = re.sub(bg_pattern, r'\2', clean_text, flags=re.IGNORECASE)
                text_format['backgroundColor'] = self.BG_COLORS[bg_color_name]
        
        # Check for header (# text)
        header_match = re.match(r'^(#{1,3})\s+(.+)$', clean_text)
        if header_match:
            level = len(header_match.group(1))
            clean_text = header_match.group(2)
            text_format['bold'] = True
            if 'fontSize' not in text_format:  # Don't override [SIZE:] if present
                text_format['fontSize'] = self.HEADER_SIZES.get(level, 14)
        
        # Add number format if detected
        if number_format:
            text_format['numberFormat'] = {'type': 'NUMBER', 'pattern': number_format}
        
        # Add wrap strategy if detected
        if wrap_strategy:
            text_format['wrapStrategy'] = wrap_strategy
            
        return clean_text, text_format
    
    def parse_data_with_markdown(self, data: List[List[Any]]) -> Tuple[List[List[Any]], List[Dict]]:
        """
        Parse entire data array and extract formatting
        
        Args:
            data: 2D array with markdown syntax
            
        Returns:
            (clean_data, format_requests): Clean data + API format requests
        """
        clean_data = []
        format_requests = []
        
        # Reset v3.0 tracking lists
        self.merge_requests = []
        self.validation_requests = []
        self.conditional_formats = []
        
        for row_idx, row in enumerate(data):
            clean_row = []
            
            for col_idx, cell in enumerate(row):
                clean_text, text_format = self.parse_cell_markdown(cell, row_idx, col_idx)
                clean_row.append(clean_text)
                
                # Create format request if formatting detected
                if text_format:
                    request = self._create_cell_format_request(
                        row_idx, col_idx, text_format
                    )
                    format_requests.append(request)
            
            clean_data.append(clean_row)
        
        # Add v3.0 special requests (merge, validation, conditional)
        format_requests.extend(self._create_merge_requests())
        format_requests.extend(self._create_validation_requests())
        format_requests.extend(self._create_conditional_format_requests())
        
        return clean_data, format_requests
    
    def _create_cell_format_request(self, row_idx: int, col_idx: int, 
                                    text_format: Dict) -> Dict:
        """Create Google Sheets API format request for a cell (v3.0 enhanced)"""
        
        cell_format = {}
        fields = []
        
        # Alignment
        if 'horizontalAlignment' in text_format:
            cell_format['horizontalAlignment'] = text_format['horizontalAlignment']
            fields.append('horizontalAlignment')
        
        # Wrap strategy (v3.0)
        if 'wrapStrategy' in text_format:
            cell_format['wrapStrategy'] = text_format['wrapStrategy']
            fields.append('wrapStrategy')
        
        # Number format (v3.0)
        if 'numberFormat' in text_format:
            cell_format['numberFormat'] = text_format['numberFormat']
            fields.append('numberFormat')
        
        # Text formatting (bold, italic, fontSize, strikethrough, underline)
        if any(k in text_format for k in ['bold', 'italic', 'fontSize', 'strikethrough', 'underline', 'foregroundColor']):
            cell_format['textFormat'] = {}
            if 'bold' in text_format:
                cell_format['textFormat']['bold'] = text_format['bold']
            if 'italic' in text_format:
                cell_format['textFormat']['italic'] = text_format['italic']
            if 'strikethrough' in text_format:  # v3.0
                cell_format['textFormat']['strikethrough'] = text_format['strikethrough']
            if 'underline' in text_format:  # v3.0
                cell_format['textFormat']['underline'] = text_format['underline']
            if 'fontSize' in text_format:
                cell_format['textFormat']['fontSize'] = text_format['fontSize']
            # Text color
            if 'foregroundColor' in text_format:
                cell_format['textFormat']['foregroundColor'] = text_format['foregroundColor']
            fields.append('textFormat')
        
        # Background color
        if 'backgroundColor' in text_format:
            cell_format['backgroundColor'] = text_format['backgroundColor']
            fields.append('backgroundColor')
        elif text_format.get('fontSize', 0) >= 14 and 'backgroundColor' not in text_format:
            # Auto gray background for headers if no explicit background
            cell_format['backgroundColor'] = {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            fields.append('backgroundColor')
        
        return {
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': row_idx,
                    'endRowIndex': row_idx + 1,
                    'startColumnIndex': col_idx,
                    'endColumnIndex': col_idx + 1
                },
                'cell': {
                    'userEnteredFormat': cell_format
                },
                'fields': f"userEnteredFormat({','.join(fields)})" if fields else 'userEnteredFormat'
            }
        }
    
    def _create_merge_requests(self) -> List[Dict]:
        """Create cell merge requests from [MERGE:3] tags (v3.0)"""
        requests = []
        for merge in self.merge_requests:
            requests.append({
                'mergeCells': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': merge['row'],
                        'endRowIndex': merge['row'] + 1,
                        'startColumnIndex': merge['col'],
                        'endColumnIndex': merge['col'] + merge['count']
                    },
                    'mergeType': 'MERGE_ALL'
                }
            })
        return requests
    
    def _create_validation_requests(self) -> List[Dict]:
        """Create data validation requests from [DROPDOWN:...] tags (v3.0)"""
        requests = []
        for validation in self.validation_requests:
            # Create dropdown with options
            requests.append({
                'setDataValidation': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': validation['row'],
                        'endRowIndex': validation['row'] + 1,
                        'startColumnIndex': validation['col'],
                        'endColumnIndex': validation['col'] + 1
                    },
                    'rule': {
                        'condition': {
                            'type': 'ONE_OF_LIST',
                            'values': [{'userEnteredValue': opt} for opt in validation['options']]
                        },
                        'showCustomUi': True,
                        'strict': False  # Allow other values
                    }
                }
            })
        return requests
    
    def _create_conditional_format_requests(self) -> List[Dict]:
        """Create conditional formatting from [IF>100:RED] tags (v3.0)"""
        requests = []
        for cond in self.conditional_formats:
            # Determine operator type
            operator_map = {
                '>': 'NUMBER_GREATER',
                '>=': 'NUMBER_GREATER_THAN_EQ',
                '<': 'NUMBER_LESS',
                '<=': 'NUMBER_LESS_THAN_EQ',
                '=': 'NUMBER_EQ',
                '==': 'NUMBER_EQ',
                '!=': 'NUMBER_NOT_EQ'
            }
            
            operator_type = operator_map.get(cond['operator'], 'NUMBER_GREATER')
            
            # Determine color (foreground or background)
            color_dict = {}
            if cond['color'] in self.COLORS:
                color_dict = {'foregroundColor': self.COLORS[cond['color']]}
            elif cond['color'] in self.BG_COLORS:
                color_dict = {'backgroundColor': self.BG_COLORS[cond['color']]}
            
            if color_dict:
                requests.append({
                    'addConditionalFormatRule': {
                        'rule': {
                            'ranges': [{
                                'sheetId': 0,
                                'startRowIndex': cond['row'],
                                'endRowIndex': cond['row'] + 1,
                                'startColumnIndex': cond['col'],
                                'endColumnIndex': cond['col'] + 1
                            }],
                            'booleanRule': {
                                'condition': {
                                    'type': operator_type,
                                    'values': [{'userEnteredValue': cond['threshold']}]
                                },
                                'format': color_dict
                            }
                        },
                        'index': 0
                    }
                })
        return requests
    
    def parse_markdown_table(self, markdown_text: str) -> Tuple[List[List[str]], Dict]:
        """
        Parse markdown table format into data + formatting
        
        Example:
            | **Name** | *Age* | City |
            |----------|-------|------|
            | John     | 30    | NYC  |
            
        Returns:
            (data, formatting_info)
        """
        lines = markdown_text.strip().split('\n')
        data = []
        
        for line in lines:
            # Skip separator lines (|---|---|)
            if re.match(r'^\s*\|[\s\-|]+\|\s*$', line):
                continue
            
            # Parse table row
            if '|' in line:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                data.append(cells)
        
        return data, {'has_header': True}
    
    def add_border_formatting(self, num_rows: int, num_cols: int) -> List[Dict]:
        """Add borders around all cells"""
        
        border_style = {
            'style': 'SOLID',
            'width': 1,
            'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
        }
        
        return [{
            'updateBorders': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': num_rows,
                    'startColumnIndex': 0,
                    'endColumnIndex': num_cols
                },
                'top': border_style,
                'bottom': border_style,
                'left': border_style,
                'right': border_style,
                'innerHorizontal': border_style,
                'innerVertical': border_style
            }
        }]
    
    def add_column_auto_resize(self, num_cols: int, data: List[List[Any]] = None) -> List[Dict]:
        """Auto-resize columns based on content (v3.0)
        
        Args:
            num_cols: Number of columns to resize
            data: Optional data array to calculate optimal widths
            
        Returns:
            List of autoResizeDimensions requests
        """
        requests = []
        
        if data:
            # Calculate optimal width for each column based on content
            for col_idx in range(num_cols):
                max_length = 0
                for row in data:
                    if col_idx < len(row):
                        cell_value = str(row[col_idx])
                        max_length = max(max_length, len(cell_value))
                
                # Estimate pixel width (rough: 8 pixels per character + 20px padding)
                estimated_width = max(100, min(500, max_length * 8 + 20))
                
                requests.append({
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': 0,
                            'dimension': 'COLUMNS',
                            'startIndex': col_idx,
                            'endIndex': col_idx + 1
                        },
                        'properties': {
                            'pixelSize': estimated_width
                        },
                        'fields': 'pixelSize'
                    }
                })
        else:
            # Use Google's auto-resize (faster but less control)
            requests.append({
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': 0,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': num_cols
                    }
                }
            })
        
        return requests


# Convenience function for integration
def format_data_with_markdown(data: List[List[Any]], 
                              headers: List[str] = None,
                              auto_borders: bool = True,
                              auto_resize_columns: bool = False) -> Tuple[List[List[Any]], List[str], List[Dict]]:
    """
    Main function to convert markdown data to clean data + formatting requests (v3.0)
    
    Args:
        data: 2D array with markdown syntax
        headers: Optional header row with markdown
        auto_borders: If True, add borders to all cells (default: True)
        auto_resize_columns: If True, auto-resize columns based on content (v3.0)
        
    Returns:
        (clean_data, clean_headers, format_requests): Ready for Google Sheets API
        - clean_data: Data rows with markdown syntax removed
        - clean_headers: Header row with markdown syntax removed (or None)
        - format_requests: Formatting rules to apply via batchUpdate()
        
    v3.0 Enhanced Features:
        - ~~strikethrough~~ → Strikethrough
        - __underline__ → Underline
        - [$]1000 → $1,000.00 (currency)
        - [%]75 → 75% (percentage)
        - [DATE]2025-12-16 → Formatted date
        - [SIZE:14]text → Custom font size
        - [WRAP]text → Wrap text
        - [MERGE:3]text → Merge 3 cells
        - [DROPDOWN:opt1,opt2]value → Dropdown
        - [IF>100:RED]125 → Conditional formatting
        - auto_resize_columns for better column widths
        
    Example:
        data = [
            ["**Product**", "[$]1000", "[%]75"],
            ["[MERGE:2]Quarterly Report", "", "[IF>100:RED]125"]
        ]
        headers = ["# Name", "**Price**", "**Growth**"]
        
        clean_data, clean_headers, formats = format_data_with_markdown(
            data, headers, auto_resize_columns=True
        )
    """
    formatter = MarkdownToSheetsFormatter()
    format_requests = []
    
    # Process headers if provided
    clean_headers = None
    if headers:
        clean_headers = []
        header_formats = []
        
        # Parse each header cell individually for markdown
        for col_idx, header in enumerate(headers):
            clean_text, text_format = formatter.parse_cell_markdown(header, row_idx=0, col_idx=col_idx)
            clean_headers.append(clean_text)
            
            # Create format request for each header cell with markdown
            if text_format:
                request = formatter._create_cell_format_request(
                    row_idx=0, col_idx=col_idx, text_format=text_format
                )
                header_formats.append(request)
        
        # Add individual header cell formats (respects markdown)
        format_requests.extend(header_formats)
    
    # Process data
    clean_data, data_formats = formatter.parse_data_with_markdown(data)
    
    # Offset data formats by 1 row if headers exist
    if headers:
        for request in data_formats:
            if 'repeatCell' in request:
                request['repeatCell']['range']['startRowIndex'] += 1
                request['repeatCell']['range']['endRowIndex'] += 1
            elif 'mergeCells' in request:
                request['mergeCells']['range']['startRowIndex'] += 1
                request['mergeCells']['range']['endRowIndex'] += 1
            elif 'setDataValidation' in request:
                request['setDataValidation']['range']['startRowIndex'] += 1
                request['setDataValidation']['range']['endRowIndex'] += 1
            elif 'addConditionalFormatRule' in request:
                for rng in request['addConditionalFormatRule']['rule'].get('ranges', []):
                    rng['startRowIndex'] += 1
                    rng['endRowIndex'] += 1
    
    format_requests.extend(data_formats)
    
    # Add borders if requested
    if auto_borders:
        num_rows = len(data) + (1 if headers else 0)
        num_cols = max(len(row) for row in data) if data else 0
        if headers:
            num_cols = max(num_cols, len(headers))
        if num_cols > 0:
            border_requests = formatter.add_border_formatting(num_rows, num_cols)
            format_requests.extend(border_requests)
    
    # Add column auto-resize if requested (v3.0)
    if auto_resize_columns:
        num_cols = max(len(row) for row in data) if data else 0
        if headers:
            num_cols = max(num_cols, len(headers))
        if num_cols > 0:
            # Include headers in width calculation
            all_data = [headers] + data if headers else data
            resize_requests = formatter.add_column_auto_resize(num_cols, all_data)
            format_requests.extend(resize_requests)
    
    # Return clean_data, clean_headers (without markdown), and format_requests
    return clean_data, clean_headers, format_requests


if __name__ == '__main__':
    # Test the formatter v3.0
    print("=" * 60)
    print("Testing Markdown Formatter v3.0 - Enhanced Edition")
    print("=" * 60)
    
    formatter = MarkdownToSheetsFormatter()
    
    # Test 1: Basic formatting
    print("\n[TEST 1] Basic Formatting")
    text, fmt = formatter.parse_cell_markdown("**Bold** and *italic*", 0, 0)
    print(f"  Input:  '**Bold** and *italic*'")
    print(f"  Output: '{text}'")
    print(f"  Format: {list(fmt.keys())}")
    
    # Test 2: v3.0 Strikethrough and underline
    print("\n[TEST 2] Strikethrough & Underline (v3.0)")
    text, fmt = formatter.parse_cell_markdown("~~deleted~~ and __important__", 0, 0)
    print(f"  Input:  '~~deleted~~ and __important__'")
    print(f"  Output: '{text}'")
    print(f"  Format: {list(fmt.keys())}")
    
    # Test 3: Number formatting
    print("\n[TEST 3] Number Formatting (v3.0)")
    tests = [
        ("[$]1000", "Currency"),
        ("[%]75", "Percentage"),
        ("[#]1234.5", "Number with commas"),
        ("[DATE]2025-12-16", "Date formatting")
    ]
    for test_input, description in tests:
        text, fmt = formatter.parse_cell_markdown(test_input, 0, 0)
        pattern = fmt.get('numberFormat', {}).get('pattern', 'None')
        print(f"  {description:20} | '{test_input:15}' → '{text}' (pattern: {pattern})")
    
    # Test 4: Custom font size
    print("\n[TEST 4] Custom Font Size (v3.0)")
    text, fmt = formatter.parse_cell_markdown("[SIZE:20]Big Title", 0, 0)
    print(f"  Input:  '[SIZE:20]Big Title'")
    print(f"  Output: '{text}' (fontSize: {fmt.get('fontSize', 'default')})")
    
    # Test 5: Text wrapping
    print("\n[TEST 5] Text Wrapping (v3.0)")
    text, fmt = formatter.parse_cell_markdown("[WRAP]This is a long text that should wrap", 0, 0)
    print(f"  Wrap strategy: {fmt.get('wrapStrategy', 'default')}")
    
    # Test 6: Cell merging
    print("\n[TEST 6] Cell Merging (v3.0)")
    text, fmt = formatter.parse_cell_markdown("[MERGE:3]Merged Title", 0, 0)
    print(f"  Input:  '[MERGE:3]Merged Title'")
    print(f"  Output: '{text}'")
    print(f"  Merge requests: {len(formatter.merge_requests)}")
    
    # Test 7: Dropdown validation
    print("\n[TEST 7] Dropdown Validation (v3.0)")
    text, fmt = formatter.parse_cell_markdown("[DROPDOWN:Red,Green,Blue]Red", 0, 0)
    print(f"  Input:  '[DROPDOWN:Red,Green,Blue]Red'")
    print(f"  Output: '{text}'")
    print(f"  Validation requests: {len(formatter.validation_requests)}")
    
    # Test 8: Conditional formatting
    print("\n[TEST 8] Conditional Formatting (v3.0)")
    text, fmt = formatter.parse_cell_markdown("[IF>100:RED]125", 0, 0)
    print(f"  Input:  '[IF>100:RED]125'")
    print(f"  Output: '{text}'")
    print(f"  Conditional formats: {len(formatter.conditional_formats)}")
    
    # Test 9: Full data array with v3.0 features
    print("\n[TEST 9] Full Data Conversion with v3.0 Features")
    data = [
        ["**Product**", "[$]1500", "[%]15", "[IF>10:GREEN]12"],
        ["[MERGE:2]Quarterly Summary", "", "[$]5000", "Complete"]
    ]
    headers = ["# Item", "**Price**", "**Tax**", "**Status**"]
    
    clean_data, clean_headers, formats = format_data_with_markdown(
        data, headers, auto_resize_columns=True
    )
    
    print(f"  Original data rows: {len(data)}")
    print(f"  Clean data rows:    {len(clean_data)}")
    print(f"  Format requests:    {len(formats)}")
    print(f"  Request types:      ", end="")
    request_types = set()
    for req in formats:
        request_types.update(req.keys())
    print(", ".join(request_types))
    
    # Test 10: Complex combined formatting
    print("\n[TEST 10] Complex Combined Formatting")
    complex_text = "(R)[SIZE:16]**__[RED]URGENT__**[/RED]"
    text, fmt = formatter.parse_cell_markdown(complex_text, 0, 0)
    print(f"  Input:  '{complex_text}'")
    print(f"  Output: '{text}'")
    print(f"  Attributes applied: {', '.join(fmt.keys())}")
    
    print("\n" + "=" * 60)
    print("✓ All v3.0 tests completed!")
    print("=" * 60)

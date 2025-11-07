"""
Google Sheets Markdown Formatter
Converts markdown syntax to Google Sheets API formatting

Supports:
- **bold text** → Bold formatting
- *italic text* → Italic formatting  
- # Headers → Bold + larger font + gray background
- Tables → Formatted cells with borders
- Color hints: [RED]text[/RED] → Red text
"""

import re
from typing import List, Dict, Any, Tuple


class MarkdownToSheetsFormatter:
    """Convert markdown formatting to Google Sheets API format requests"""
    
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
    
    def __init__(self):
        self.formatting_rules = []
        
    def parse_cell_markdown(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse markdown in a single cell and return clean text + formatting
        
        Args:
            text: Cell text with markdown (e.g., "**Bold** and *italic*")
            
        Returns:
            (clean_text, format_dict): Clean text and Google Sheets format dict
        
        Supports v2.0 syntax:
        - (L)text → Left align
        - (R)text → Right align
        - (C)text → Center align
        - [R]text → Red text (shortened from [RED]text[/RED])
        - {LG}text → Light green background (shortened from [BG:LIGHTGREEN]text[/BG])
        """
        if not isinstance(text, str):
            return str(text), {}
        
        clean_text = text
        text_format = {}
        
        # v2.0: Check for alignment (L), (R), (C) - must be at start
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
        
        # Check for bold (**text**)
        if '**' in text:
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_text)
            text_format['bold'] = True
        
        # Check for italic (*text*)
        if '*' in text and '**' not in text:
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
            text_format['fontSize'] = self.HEADER_SIZES.get(level, 14)
            
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
        
        for row_idx, row in enumerate(data):
            clean_row = []
            
            for col_idx, cell in enumerate(row):
                clean_text, text_format = self.parse_cell_markdown(cell)
                clean_row.append(clean_text)
                
                # Create format request if formatting detected
                if text_format:
                    request = self._create_cell_format_request(
                        row_idx, col_idx, text_format
                    )
                    format_requests.append(request)
            
            clean_data.append(clean_row)
        
        return clean_data, format_requests
    
    def _create_cell_format_request(self, row_idx: int, col_idx: int, 
                                    text_format: Dict) -> Dict:
        """Create Google Sheets API format request for a cell"""
        
        cell_format = {}
        
        # Alignment (v2.0)
        if 'horizontalAlignment' in text_format:
            cell_format['horizontalAlignment'] = text_format['horizontalAlignment']
        
        # Text formatting
        if 'bold' in text_format or 'italic' in text_format or 'fontSize' in text_format:
            cell_format['textFormat'] = {}
            if 'bold' in text_format:
                cell_format['textFormat']['bold'] = text_format['bold']
            if 'italic' in text_format:
                cell_format['textFormat']['italic'] = text_format['italic']
            if 'fontSize' in text_format:
                cell_format['textFormat']['fontSize'] = text_format['fontSize']
        
        # Text color
        if 'foregroundColor' in text_format:
            if 'textFormat' not in cell_format:
                cell_format['textFormat'] = {}
            cell_format['textFormat']['foregroundColor'] = text_format['foregroundColor']
        
        # Background color (explicit or for headers)
        if 'backgroundColor' in text_format:
            cell_format['backgroundColor'] = text_format['backgroundColor']
        elif text_format.get('fontSize', 0) >= 14:
            # Auto gray background for large headers (# ## ###) if no explicit background
            cell_format['backgroundColor'] = {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        
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
                'fields': 'userEnteredFormat(textFormat,backgroundColor)'
            }
        }
    
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


# Convenience function for integration
def format_data_with_markdown(data: List[List[Any]], 
                              headers: List[str] = None,
                              auto_borders: bool = True) -> Tuple[List[List[Any]], List[str], List[Dict]]:
    """
    Main function to convert markdown data to clean data + formatting requests
    
    Args:
        data: 2D array with markdown syntax
        headers: Optional header row with markdown
        auto_borders: If True, add borders to all cells (default: True)
        
    Returns:
        (clean_data, clean_headers, format_requests): Ready for Google Sheets API
        - clean_data: Data rows with markdown syntax removed
        - clean_headers: Header row with markdown syntax removed (or None)
        - format_requests: Formatting rules to apply via batchUpdate()
        
    Example:
        data = [
            ["**John**", "*30*", "NYC"],
            ["[RED]Jane[/RED]", "25", "LA"]
        ]
        headers = ["# Name", "**Age**", "City"]
        
        clean_data, formats = format_data_with_markdown(data, headers)
        # Use clean_data for values.update()
        # Use formats for batchUpdate()
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
            clean_text, text_format = formatter.parse_cell_markdown(header)
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
            request['repeatCell']['range']['startRowIndex'] += 1
            request['repeatCell']['range']['endRowIndex'] += 1
    
    format_requests.extend(data_formats)
    
    # Add borders if requested
    if auto_borders:
        num_rows = len(data) + (1 if headers else 0)
        num_cols = max(len(row) for row in data) if data else 0
        if num_cols > 0:
            border_requests = formatter.add_border_formatting(num_rows, num_cols)
            format_requests.extend(border_requests)
    
    # Return clean_data, clean_headers (without markdown), and format_requests
    return clean_data, clean_headers, format_requests


if __name__ == '__main__':
    # Test the formatter
    print("Testing Markdown Formatter...")
    
    # Test 1: Simple markdown
    formatter = MarkdownToSheetsFormatter()
    text, fmt = formatter.parse_cell_markdown("**Bold** and *italic*")
    print(f"Test 1: '{text}' -> {fmt}")
    
    # Test 2: Headers
    text, fmt = formatter.parse_cell_markdown("# Patient Records")
    print(f"Test 2: '{text}' -> {fmt}")
    
    # Test 3: Color tags
    text, fmt = formatter.parse_cell_markdown("[RED]CRITICAL[/RED]")
    print(f"Test 3: '{text}' -> {fmt}")
    
    # Test 4: Full data array
    data = [
        ["**John Doe**", "*30*", "NYC"],
        ["Jane Smith", "[GREEN]Active[/GREEN]", "LA"]
    ]
    headers = ["# Name", "**Age**", "**Status**"]
    
    clean_data, formats = format_data_with_markdown(data, headers)
    print(f"\nTest 4: Data conversion")
    print(f"Clean data: {clean_data}")
    print(f"Format requests: {len(formats)} requests generated")

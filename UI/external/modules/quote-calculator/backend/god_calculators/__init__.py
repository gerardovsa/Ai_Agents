"""
GOD Calculators - Database-Driven Production Calculators
========================================================

These calculators use LIVE data from the InHousePrint SQL Server database:
- Real-time stock prices from Quote_DigitalStocks
- Current click costs from Quote_DigitalClicks  
- Live settings from Quote_GenericSetting
- Dynamic profit margins from Quote_ProfitMargins

Used by the VB.NET production system for actual customer orders.

Modular Architecture:
-  FlyerCalculatorGOD: Flyers/leaflets with folding and cello (NEW - EXTRACTED)
-  CorfluteSigsCalculator: Corflute signs with database pricing (EXISTING)
- ⚠️ BusinessCardCalculator: Business cards (OLD - hardcoded, needs rewrite)
- ⏳ LetterheadCalculatorGOD: Coming soon
- ⏳ BookletCalculatorGOD: Coming soon
- ⏳ PerfectBoundBookCalculatorGOD: Coming soon

Usage:
    from god_calculators import FlyerCalculatorGOD
    from inhouse_modules.db_connector import InHousePrintDB
    
    db = InHousePrintDB("config/database-config.json")
    calc = FlyerCalculatorGOD(db)
    result = calc.calculate(1000, 210, 297, 300, print_side1=1)
    print(f"Total: ${result.total_cost_inc_gst:.2f}")
"""

# Import calculators
from .GOD_flyer_calculator import FlyerCalculatorGOD, calculate_flyer_quote
from .GOD_letterhead_calculator import LetterheadCalculatorGOD, calculate_letterhead_quote
from .GOD_perfect_bound_books_calculator import PerfectBoundBooksCalculator, calculate_perfect_bound_book_quote

try:
    from .corflute_calculator import CorflutePricingCalculator, CorfluteSigsCalculator
except ImportError:
    CorflutePricingCalculator = None
    CorfluteSigsCalculator = None


# Calculator Registry (for discovery and tool integration)
CALCULATOR_REGISTRY = {
    'flyers': {
        'class': FlyerCalculatorGOD,
        'tool_function': calculate_flyer_quote,
        'status': 'active',
        'database_driven': True,
        'extracted': True,
        'vb_source': 'FlyerQuote.vb'
    },
    'letterheads': {
        'class': LetterheadCalculatorGOD,
        'tool_function': calculate_letterhead_quote,
        'status': 'active',
        'database_driven': True,
        'extracted': True,
        'vb_source': 'LetterheadQuote.vb'
    },
    'perfect_bound_books': {
        'class': PerfectBoundBooksCalculator,
        'tool_function': calculate_perfect_bound_book_quote,
        'status': 'active',
        'database_driven': True,
        'extracted': True,
        'vb_source': 'PerfectBBQuote.vb'
    },
    'corflute': {
        'class': CorfluteSigsCalculator or CorflutePricingCalculator,
        'status': 'active',
        'database_driven': True,
        'extracted': True,
        'vb_source': 'RidgedQuote.vb'
    }
}


def get_available_calculators():
    """Get list of available calculators"""
    return [
        {'name': name, **info}
        for name, info in CALCULATOR_REGISTRY.items()
        if info['class'] is not None
    ]


__all__ = [
    'FlyerCalculatorGOD',
    'calculate_flyer_quote',
    'LetterheadCalculatorGOD',
    'calculate_letterhead_quote',
    'PerfectBoundBooksCalculator',
    'calculate_perfect_bound_book_quote',
    'CorflutePricingCalculator',
    'CorfluteSigsCalculator',
    'CALCULATOR_REGISTRY',
    'get_available_calculators',
]

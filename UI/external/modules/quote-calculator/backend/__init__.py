"""
Calculator Module Backend
Standalone quote calculators (no SQL Server dependency)
"""

from .calculator_wrapper import QuoteCalculatorWrapper

__all__ = ['QuoteCalculatorWrapper']
__version__ = '2.0.0'
__author__ = 'InHouse Print'

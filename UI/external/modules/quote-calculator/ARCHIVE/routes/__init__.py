"""
Quote Calculator Routes Package

This package contains Flask routes for the quote calculator module.
Routes are auto-discovered by module_blueprint_loader.

FILE: UI/external/modules/quote-calculator/routes/__init__.py
PURPOSE: Package initialization for quote calculator routes
LAST MODIFIED: 2025-11-04 - Initial creation
"""

from .calculator_routes import quote_calculator_bp

__all__ = ['quote_calculator_bp']

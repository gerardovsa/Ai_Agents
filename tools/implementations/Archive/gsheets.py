"""
REDIRECT - GSheets Functions (Sheets API v4)
============================================

*** GOOGLE SHEETS FUNCTIONS NOW USE GOOGLE SHEETS API V4 ***
*** Functions are in google_workspace.google_docs module ***

This file maintains backward compatibility for existing code.
The old gspread-based implementation has been archived.

New location: google_workspace/google_docs.py
Functions: google_sheets_create, google_sheets_read_data, google_sheets_append_data
"""

from google_workspace.google_docs import (
    google_sheets_create as gsheets_create,
    google_sheets_read_data as gsheets_read,
    google_sheets_append_data as gsheets_append
)

# Note: gsheets_write is not implemented in Sheets API v4 yet
# Use gsheets_append instead for adding data

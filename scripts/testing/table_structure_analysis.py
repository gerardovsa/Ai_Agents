"""
Google Docs Table Structure Analysis

When you insert a table with insertTable, Google Docs creates this structure:

EMPTY DOCUMENT:
- Index 1: Start (body starts at 1)

AFTER INSERTING 2x2 TABLE:
The table creates this structure:
- Table start marker: 1 char
- Row 1:
  - Cell 1,1: 2 chars (start + end markers)
  - Cell 1,2: 2 chars
  - Row end: 1 char
- Row 2:
  - Cell 2,1: 2 chars
  - Cell 2,2: 2 chars
  - Row end: 1 char
- Table end marker: 1 char

FORMULA ATTEMPT 1: 2 + (rows * cols * 2) + rows
For 2x2: 2 + (2 * 2 * 2) + 2 = 2 + 8 + 2 = 12

ACTUAL SIZE: Varies based on Google's internal structure!

THE PROBLEM:
Google Docs doesn't document the exact structure, and it can vary based on:
- Document state
- API version
- Whether content exists
- Cell merging
- Borders/styling

SOLUTION OPTIONS:
1. Insert table, then QUERY the document to get actual structure  BEST
2. Use conservative estimate and skip content after tables  Current
3. Don't support tables  Too limiting
"""
print(__doc__)

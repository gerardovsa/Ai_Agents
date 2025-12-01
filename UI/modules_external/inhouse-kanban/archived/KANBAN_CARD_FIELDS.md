# InHouse Kanban Card Fields - Complete Reference

## Database Source
**Database**: InHousePrint (SQL Server at 3.25.76.138:1433)
**Primary Tables**: JobTickets, Orders, JobStage

---

## COLLAPSED CARD STATE (renderJobCard)

### Currently Displayed Fields:
1. **TicketID** - Job ticket number (e.g., #12345)
2. **ShortJobDesc** - Job description/title
3. **ClientName** - Client company name
4. **Cost** - Job value in dollars
5. **DaysInSystem** - Days since order date
6. **WIPStatus** - Work in progress status (ACTIVE, DELAYED, AT RISK)
7. **AIPriorityScore** - AI-calculated priority (0-999)
8. **PriorityColorHex** - Priority indicator color

### Visual Elements:
- Priority icon (top-right corner)
- Status badge (ACTIVE/DELAYED/AT RISK)
- Client name with building icon
- Cost with dollar icon
- Days in system counter

---

## EXPANDED CARD STATE (showJobDetailsModal)

### Section 1: Status Badges (Top Row)
1. **PriorityLabel** - Text label (Critical/High/Normal/Low)
2. **AIPriorityScore** - Numeric score (0-999)
3. **CustomerTier** - Customer tier (Gold/Silver/Bronze)
4. **WIPStatus** - Current WIP status

### Section 2: Client Information
1. **ClientName** - Customer name
2. **OrderID** - Order reference number
3. **OrderDate** - Date order was placed
4. **BusinessDivision** - Division (InHousePrint/Graphiti/Wide Format)

### Section 3: Job Specifications
1. **ShortJobDesc** - Job description
2. **QTY** - Quantity to produce
3. **Cost** - Total job cost
4. **Paper** - Paper type (from PaperType table)
5. **GSM** - Paper weight (from GSM table)
6. **JobSize** - Paper size (from PaperSize table)
7. **Pages** - Number of pages
8. **Binding** - Binding type (from BindType table)

### Section 4: Finishing Options (Conditional)
1. **Cello** - Cellophane finish (Matt/Gloss/Both)
2. **Folding** - Folding description
3. **Stitching** - Stitching yes/no

### Section 5: Production Notes (Conditional)
1. **TicketNotes** - Internal production notes

### Section 6: Status Information
1. **StageDescription** - Current production stage
2. **DateRequired** - Due date
3. **DaysInSystem** - Days in workflow
4. **UrgencyLevel** - Urgency classification

### Section 7: Shipping (Conditional)
1. **Shipping** - Shipping instructions

---

## API RESPONSE FIELDS (from /api/inhouse-kanban/jobs/:id)

### Core Job Fields:
```python
{
    'TicketID': int,
    'OrderID': int,
    'StageID': int,
    'StageDescription': str,
    'ClientName': str,
    'OrderDate': datetime,
    'ShortJobDesc': str,
    'DateRequired': datetime,
    'QTY': int,
    'Cost': decimal
}
```

### Paper/Material Fields:
```python
{
    'PaperType': str,          # e.g., "Satin", "Matt", "Gloss"
    'GSM': str,                # e.g., "350GSM", "250GSM"
    'PaperSize': str,          # e.g., "A4", "DL", "A5"
    'JobType': str,            # e.g., "Business Cards", "Flyers"
    'BindType': str            # e.g., "Saddle Stitch", "Perfect Bound"
}
```

### Finishing Options:
```python
{
    'FrontCelloMatt': int,     # 0 or 1
    'FrontCelloGloss': int,    # 0 or 1
    'BackCelloMatt': int,      # 0 or 1
    'BackCelloGloss': int,     # 0 or 1
    'FoldDesc': str,           # Folding description
    'StitchYes': int,          # 0 or 1
    'RingBind': int,           # 0 or 1
    'PerfectBind': int,        # 0 or 1
    'Books': int               # Number of books
}
```

### Additional Fields:
```python
{
    'Pages': int,
    'ProductionNotes': str,
    'ClientOrderNum': str,
    'ShippingDesc': str,
    'InvoicingBusinessID': int,
    'InvoicingBusiness': str,
    'Priority': str,           # "Overdue", "Urgent", "Normal", "Low Priority"
    'DaysUntilDue': int,
    'DaysInSystem': int,
    'UrgencyLevel': str,       # "OVERDUE", "CRITICAL", "HIGH", "MEDIUM", "LOW"
    'CustomerOrderCount': int,
    'CustomerLifetimeValue': decimal
}
```

### Calculated Fields (added by backend):
```python
{
    'AIPriorityScore': int,        # 0-999
    'PriorityLabel': str,          # "Critical", "High", "Normal", "Low"
    'PriorityColorHex': str,       # "#ef4444", "#f97316", etc.
    'CustomerTier': str,           # "Gold", "Silver", "Bronze"
    'CustomerTierColorHex': str,   # Tier color
    'WIPStatus': str,              # "ACTIVE", "DELAYED", "AT RISK"
    'WIPColorHex': str             # Status color
}
```

---

## MISSING FIELDS IN CURRENT IMPLEMENTATION

### Not Currently Displayed (but available):
1. **ClientOrderNum** - Customer's PO number
2. **InvoicingBusiness** - Invoicing entity
3. **CustomerOrderCount** - Total orders from this customer
4. **CustomerLifetimeValue** - Total value from customer
5. **JobType** - Job type description
6. **Books** - Number of books (for book jobs)
7. **RingBind** - Ring binding flag
8. **PerfectBind** - Perfect binding flag

### Field Mapping Issues:
- API returns `PaperType`, `GSM`, `PaperSize` as separate fields
- Frontend expects combined `Paper` field (needs concatenation)
- API returns `FoldDesc` but frontend expects `Folding`
- API returns `ProductionNotes` but frontend expects `TicketNotes`
- API returns `ShippingDesc` but frontend expects `Shipping`

---

## FIELD MAPPING FIX NEEDED

### Backend Returns → Frontend Expects:
```
PaperType + GSM + PaperSize → Paper
FoldDesc → Folding
StitchYes → Stitching
ProductionNotes → TicketNotes
ShippingDesc → Shipping
PaperSize → JobSize
BindType → Binding
```

### Cello Field Combination:
```python
# Frontend expects single "Cello" field
# Backend returns: FrontCelloMatt, FrontCelloGloss, BackCelloMatt, BackCelloGloss

Cello = 
  if FrontCelloMatt and BackCelloMatt: "Both Sides Matt"
  elif FrontCelloGloss and BackCelloGloss: "Both Sides Gloss"
  elif FrontCelloMatt: "Front Matt"
  elif FrontCelloGloss: "Front Gloss"
  elif BackCelloMatt: "Back Matt"
  elif BackCelloGloss: "Back Gloss"
  else: None
```

---

## RECOMMENDED FIXES

### 1. Update Backend Response (inhouse_kanban_routes.py)
Add field mapping in `get_job_details()` endpoint:
```python
# Combine paper fields
job['Paper'] = f"{job.get('PaperType', '')} {job.get('GSM', '')}".strip()
job['JobSize'] = job.get('PaperSize', '')
job['Binding'] = job.get('BindType', '')

# Map field names
job['Folding'] = job.get('FoldDesc', '')
job['TicketNotes'] = job.get('ProductionNotes', '')
job['Shipping'] = job.get('ShippingDesc', '')

# Combine cello options
cello_parts = []
if job.get('FrontCelloMatt'): cello_parts.append('Front Matt')
if job.get('FrontCelloGloss'): cello_parts.append('Front Gloss')
if job.get('BackCelloMatt'): cello_parts.append('Back Matt')
if job.get('BackCelloGloss'): cello_parts.append('Back Gloss')
job['Cello'] = ', '.join(cello_parts) if cello_parts else None

# Stitching
job['Stitching'] = 'Yes' if job.get('StitchYes') else 'No'
```

### 2. Add Missing Fields to Modal
Add these sections to expanded card:
- Customer lifetime value
- Customer order count
- Job type
- Invoicing business
- Client PO number

---

## PRIORITY SCORING ALGORITHM

### Formula (mirrors kanban_board_system.py):
```python
base_score = 500

# Days until due (-50 to +300 points)
if overdue: +300
elif due_today_tomorrow: +250
elif due_within_3_days: +200
elif due_within_7_days: +150
else: -(days - 7) * 5 (max -50)

# Job value (0 to +400 points)
if cost > $5000: +400
elif cost > $2000: +300
elif cost > $1000: +200
elif cost > $500: +100

# Customer tier (0 to +200 points)
Gold: +200
Silver: +100
Bronze: +50

# Stage urgency (0 to +99 points)
Critical stages: +99
High priority stages: +75
Normal stages: +50

# Total: 0-999
```

---

## STATUS: CURRENT ISSUES

### ❌ ERROR: "Failed to load job details"
**Root Cause**: Field name mismatches between API response and frontend expectations

**Fix Required**: Backend field mapping (see section above)

### ✅ WORKING: Collapsed cards display correctly
All base fields render properly in card grid view

### ⚠️ PARTIAL: Expanded modal needs field mapping
Modal template references fields that don't exist in API response

---

**Last Updated**: November 3, 2025
**Database**: InHousePrint @ 3.25.76.138:1433
**API Endpoint**: `/api/inhouse-kanban/jobs/:id`

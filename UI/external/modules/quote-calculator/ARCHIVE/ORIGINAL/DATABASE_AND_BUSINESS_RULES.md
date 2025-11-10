# DATABASE SCHEMA AND BUSINESS RULES REFERENCE

## Table Structures and Relationships

### 1. Quote_GenericSetting
**Purpose**: System-wide configuration values for all quote calculations

```sql
CREATE TABLE Quote_GenericSetting (
    SettingID           INT IDENTITY(1,1) PRIMARY KEY,
    SettingDesc         VARCHAR(100) NOT NULL,
    SettingValue        VARCHAR(50) NOT NULL,
    IsActive            BIT DEFAULT 1,
    LastModified        DATETIME DEFAULT GETDATE()
);
```

**Key Configuration Values**:
```sql
-- Core Settings
MaterialWastePercentage     = 5.0       -- 5% material waste factor
DigitalImpositionSetup      = 25.00     -- Digital setup cost
BinderyLaborPerHour         = 45.00     -- Labor rate per hour
GST                         = 10.0      -- GST percentage
FlyerBleedMeasurement       = 3         -- Bleed in mm

-- Cutting & Finishing
GuilloSetup                 = 15.00     -- Guillotine setup cost
CuttingBlockSheets          = 100       -- Sheets per cutting block
CostPerBlock                = 2.50      -- Cost per cutting block

-- Folding
FoldingSetupCost           = 20.00      -- Folding setup
FoldingCostPer1000         = 18.00      -- Cost per 1000 folds

-- Cello Lamination
CelloSetupCost             = 15.00      -- Cello setup
CelloGlossShortPerM        = 2.20       -- Gloss cello short roll per meter
CelloGlossWidePerM         = 1.95       -- Gloss cello wide roll per meter
CellMattShortPerM          = 2.50       -- Matt cello short roll per meter
CelloMattWidePerM          = 2.25       -- Matt cello wide roll per meter
CelloCostPerHour           = 45.00      -- Cello machine hourly rate
SpeedMPerMin               = 8          -- Cello machine speed meters/min

-- Booklet Machine
BookletSetup               = 25.00      -- Booklet machine setup
BookletSheetsPerHour       = 400        -- Booklet machine capacity
BookletCostPerBook         = 0.12       -- Running cost per booklet

-- Perfect Bound Books
PBBGuiloSetup             = 20.00       -- PBB guillotine setup
PBBCuttingBlocks          = 200         -- PBB cutting block size
PBBGuiloCostPerBlock      = 3.50        -- PBB cost per cutting block
PBBBinderSetup            = 35.00       -- Binder setup cost
PBBTrimmerSetup           = 25.00       -- Three-way trimmer setup
PBBThreeWayCostPerBook    = 0.25        -- Trimming cost per book
PBBProofCost              = 15.00       -- Proof cost
PBBCostPerBox             = 5.00        -- Packaging cost
CostPerColourInsertBlock  = 8.50        -- Color insert handling

-- Ridged Boards
RidgedWaste               = 8.0         -- 8% waste for ridged boards
HPR2000InkCost           = 0.085        -- HP R2000 ink cost per sqm
HP560InkCost             = 0.095        -- HP 560 ink cost per sqm
WFAdditionalArtworkCost  = 25.00        -- Extra artwork cost
WFRidgedDblSideMaterialMargin = 15.0    -- 15% extra for double-sided
```

### 2. Quote_DigitalClicks
**Purpose**: Digital printing click charges per A4 equivalent

```sql
CREATE TABLE Quote_DigitalClicks (
    DigitalClickID      INT IDENTITY(1,1) PRIMARY KEY,
    ClickDesc           VARCHAR(50) NOT NULL,
    ClickPricePerA4     DECIMAL(10,6) NOT NULL,
    IsActive            BIT DEFAULT 1,
    LastModified        DATETIME DEFAULT GETDATE()
);
```

**Standard Click Rates**:
```sql
INSERT INTO Quote_DigitalClicks VALUES
(1, 'Colour', 0.023000, 1),
(2, 'Black & White', 0.003500, 1),
(3, 'B&W on Colour Machine', 0.007000, 1);
```

### 3. Quote_DigitalStocks
**Purpose**: Paper stock inventory with pricing and specifications

```sql
CREATE TABLE Quote_DigitalStocks (
    StockID             INT IDENTITY(1,1) PRIMARY KEY,
    StockTypeID         INT NOT NULL,
    Width               INT NOT NULL,           -- Sheet width in mm
    Length              INT NOT NULL,           -- Sheet height in mm  
    GSM                 INT NOT NULL,           -- Paper weight
    CostPerThousand     DECIMAL(10,2) NOT NULL, -- Cost per 1000 sheets
    Markup              DECIMAL(5,2) NOT NULL,  -- Markup percentage
    StockDescription    VARCHAR(100),
    IsActive            BIT DEFAULT 1,
    LastModified        DATETIME DEFAULT GETDATE()
);
```

**Common Stock Sizes**:
```sql
-- SRA3 Stocks (320 x 450mm)
Width=320, Length=450, GSM=80,  CostPerThousand=45.00, Markup=25.0
Width=320, Length=450, GSM=100, CostPerThousand=52.00, Markup=25.0
Width=320, Length=450, GSM=120, CostPerThousand=58.00, Markup=25.0
Width=320, Length=450, GSM=150, CostPerThousand=68.00, Markup=25.0
Width=320, Length=450, GSM=200, CostPerThousand=85.00, Markup=25.0
Width=320, Length=450, GSM=250, CostPerThousand=105.00, Markup=25.0
Width=320, Length=450, GSM=300, CostPerThousand=125.00, Markup=25.0

-- A3+ Stocks (330 x 483mm)
Width=330, Length=483, GSM=80,  CostPerThousand=48.00, Markup=25.0
Width=330, Length=483, GSM=100, CostPerThousand=55.00, Markup=25.0
Width=330, Length=483, GSM=150, CostPerThousand=72.00, Markup=25.0

-- Banner Stocks (Various x 700mm+)
Width=320, Length=700, GSM=120, CostPerThousand=95.00, Markup=25.0
Width=330, Length=750, GSM=150, CostPerThousand=125.00, Markup=25.0
```

### 4. Quote_ProfitMargins
**Purpose**: Tiered profit margin structure by product type and job value

```sql
CREATE TABLE Quote_ProfitMargins (
    MarginID            INT IDENTITY(1,1) PRIMARY KEY,
    ProductTypeID       INT NOT NULL,
    StartPrice          DECIMAL(10,2) NOT NULL,
    EndPrice            DECIMAL(10,2) NOT NULL,
    Margin              DECIMAL(5,1) NOT NULL,  -- Percentage
    IsActive            BIT DEFAULT 1,
    LastModified        DATETIME DEFAULT GETDATE()
);
```

**Product Type IDs**:
- **1**: Flyers (Under 4000 qty, no folding)
- **2**: Booklets (SRA3 size)
- **3**: Booklets (Banner size)
- **4**: Perfect Bound Books
- **5**: Flyers (Over 4000 qty, no folding)
- **6**: Flyers (Under 4000 qty, with folding)
- **7**: Flyers (Over 4000 qty, with folding)
- **8**: Letterheads

**Typical Margin Structure (Product Type 1 - Flyers)**:
```sql
INSERT INTO Quote_ProfitMargins (ProductTypeID, StartPrice, EndPrice, Margin) VALUES
(1, 0.00, 10.00, 200.0),      -- 200% margin on jobs under $10
(1, 10.01, 25.00, 150.0),     -- 150% margin on jobs $10-25
(1, 25.01, 50.00, 120.0),     -- 120% margin on jobs $25-50
(1, 50.01, 100.00, 100.0),    -- 100% margin on jobs $50-100
(1, 100.01, 200.00, 80.0),    -- 80% margin on jobs $100-200
(1, 200.01, 500.00, 65.0),    -- 65% margin on jobs $200-500
(1, 500.01, 1000.00, 50.0),   -- 50% margin on jobs $500-1000
(1, 1000.01, 9999.00, 40.0);  -- 40% margin on jobs over $1000
```

### 5. Quote_PBBPerBookBindCost
**Purpose**: Perfect bound book binding costs by quantity

```sql
CREATE TABLE Quote_PBBPerBookBindCost (
    BindCostID          INT IDENTITY(1,1) PRIMARY KEY,
    StartQty            INT NOT NULL,
    EndQTY              INT NOT NULL,
    CostPerBook         DECIMAL(5,3) NOT NULL,
    IsActive            BIT DEFAULT 1,
    LastModified        DATETIME DEFAULT GETDATE()
);
```

**Sample Binding Costs**:
```sql
INSERT INTO Quote_PBBPerBookBindCost (StartQty, EndQTY, CostPerBook) VALUES
(1, 25, 3.500),        -- $3.50 per book for 1-25 books
(26, 50, 2.750),       -- $2.75 per book for 26-50 books
(51, 100, 2.250),      -- $2.25 per book for 51-100 books
(101, 250, 1.850),     -- $1.85 per book for 101-250 books
(251, 500, 1.450),     -- $1.45 per book for 251-500 books
(501, 1000, 1.150),    -- $1.15 per book for 501-1000 books
(1001, 9999, 0.950);   -- $0.95 per book for 1000+ books
```

### 6. Quote_PBBExtraBookScale
**Purpose**: Extra book allowances for perfect bound books

```sql
CREATE TABLE Quote_PBBExtraBookScale (
    ExtraBookID         INT IDENTITY(1,1) PRIMARY KEY,
    StartQty            INT NOT NULL,
    EndQty              INT NOT NULL,
    BookAmount          INT NOT NULL,          -- Extra books to produce
    IsActive            BIT DEFAULT 1,
    LastModified        DATETIME DEFAULT GETDATE()
);
```

**Extra Book Allowances**:
```sql
INSERT INTO Quote_PBBExtraBookScale (StartQty, EndQty, BookAmount) VALUES
(1, 25, 6),            -- 6 extra books for orders 1-25
(26, 50, 5),           -- 5 extra books for orders 26-50
(51, 100, 4),          -- 4 extra books for orders 51-100
(101, 250, 4),         -- 4 extra books for orders 101-250
(251, 500, 3),         -- 3 extra books for orders 251-500
(501, 9999, 2);        -- 2 extra books for orders 500+
```

### 7. Quote_RidgedStocks
**Purpose**: Ridged board material specifications and costs

```sql
CREATE TABLE Quote_RidgedStocks (
    StockID             INT IDENTITY(1,1) PRIMARY KEY,
    StockTypeID         INT NOT NULL,
    CostPerSq           DECIMAL(6,3) NOT NULL,  -- Cost per square meter
    Thickness           INT NOT NULL,           -- Material thickness in microns
    StockDescription    VARCHAR(100),
    IsActive            BIT DEFAULT 1,
    LastModified        DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (StockTypeID) REFERENCES Quote_RidgedStockType(StockTypeID)
);
```

**Sample Ridged Stocks**:
```sql
INSERT INTO Quote_RidgedStocks (StockTypeID, CostPerSq, Thickness, StockDescription) VALUES
(1, 8.500, 400, '400mic Corrugated Board'),
(1, 12.750, 600, '600mic Corrugated Board'),
(2, 15.250, 800, '800mic Foam Core'),
(2, 18.500, 1000, '1000mic Foam Core'),
(3, 22.500, 3000, '3mm Aluminium Composite'),
(3, 28.750, 4000, '4mm Aluminium Composite');
```

### 8. Quote_RidgedStockType
**Purpose**: Ridged board categories and print machine assignments

```sql
CREATE TABLE Quote_RidgedStockType (
    StockTypeID         INT IDENTITY(1,1) PRIMARY KEY,
    StockTypeName       VARCHAR(50) NOT NULL,
    PrintMachine        INT NOT NULL,          -- 1=HP R2000, 2=HP 560
    MaxWidth            INT,                   -- Maximum printable width
    MaxHeight           INT,                   -- Maximum printable height
    IsActive            BIT DEFAULT 1,
    LastModified        DATETIME DEFAULT GETDATE()
);
```

**Stock Types**:
```sql
INSERT INTO Quote_RidgedStockType (StockTypeName, PrintMachine, MaxWidth, MaxHeight) VALUES
('Corrugated Board', 1, 1300, 2000),      -- HP R2000
('Foam Core', 1, 1300, 2000),             -- HP R2000
('Aluminium Composite', 2, 560, 1000),    -- HP 560
('Vinyl Sticker', 2, 560, 1000),          -- HP 560
('Magnetic Sheet', 2, 560, 1000);         -- HP 560
```

### 9. Quote_RidgedProfitMargin
**Purpose**: Profit margins specific to ridged board products

```sql
CREATE TABLE Quote_RidgedProfitMargin (
    MarginID            INT IDENTITY(1,1) PRIMARY KEY,
    ProductTypeID       INT NOT NULL,          -- Links to stock type or category
    StartPrice          DECIMAL(10,2) NOT NULL,
    EndPrice            DECIMAL(10,2) NOT NULL,
    Margin              DECIMAL(5,1) NOT NULL,
    IsActive            BIT DEFAULT 1,
    LastModified        DATETIME DEFAULT GETDATE()
);
```

**Ridged Board Margins**:
```sql
INSERT INTO Quote_RidgedProfitMargin (ProductTypeID, StartPrice, EndPrice, Margin) VALUES
(1, 0.00, 50.00, 120.0),      -- 120% margin for corrugated under $50
(1, 50.01, 100.00, 100.0),    -- 100% margin for corrugated $50-100
(1, 100.01, 200.00, 80.0),    -- 80% margin for corrugated $100-200
(1, 200.01, 9999.00, 60.0),   -- 60% margin for corrugated over $200
(2, 0.00, 100.00, 100.0),     -- 100% margin for foam core under $100
(2, 100.01, 9999.00, 70.0),   -- 70% margin for foam core over $100
(3, 0.00, 9999.00, 50.0);     -- 50% margin for aluminium composite
```

## Business Rules and Relationships

### Stock Selection Logic
1. **Size Compatibility**: Stock must accommodate item size + bleed
2. **GSM Matching**: Must match specified paper weight exactly
3. **Cost Optimization**: Select cheapest cost per unit after imposition
4. **Efficiency Consideration**: Prefer stocks with better sheet utilization

### Imposition Calculation
```python
# Calculate how many items fit per sheet
ups_normal = int(stock_width // (item_width + bleed)) * int(stock_height // (item_height + bleed))
ups_rotated = int(stock_width // (item_height + bleed)) * int(stock_height // (item_width + bleed))
best_ups = max(ups_normal, ups_rotated)
```

### A4 Equivalent Calculation
```python
# Determine A4 multiplier based on stock size
if stock_height > 483:  # Banner size
    a4_multiplier = 3
else:  # SRA3 size  
    a4_multiplier = 2

# Calculate click cost
click_cost = sheets * (click_rate * a4_multiplier)
```

### Waste Calculation
- **Standard Products**: 5% material waste
- **Ridged Boards**: 8% material waste
- **Applied to sheet count**: `sheets_with_waste = sheets_needed * (1 + waste_percentage/100)`

### Cello Roll Selection
```python
# Determine roll type based on stock dimensions
if stock_height < 455:
    use_wide_roll = True    # Wide cello roll rates
else:
    use_short_roll = True   # Short cello roll rates
```

### Profit Margin Application Order
1. Calculate total cost to business
2. Look up margin percentage based on product type and cost range
3. Apply margin: `cost_with_margin = cost_to_business * (1 + margin_percentage/100)`
4. Apply discount: `discounted_cost = cost_with_margin * (1 - discount_percentage/100)`
5. Add GST: `final_cost = discounted_cost * (1 + gst_rate/100)`

### Perfect Bound Book Special Rules
- **Cover Calculation**: Uses open size (width × 2) for imposition
- **Text Block**: 4 pages per sheet (front/back of folded sheet)
- **Extra Books**: Additional books produced based on quantity scale
- **Binding Cost**: Decreases per unit as quantity increases
- **Three-Way Trimming**: Applied to all perfect bound books

### Booklet Page Calculations
```python
# Self-cover booklets
if pages % 4 == 0:
    # All pages can be printed 2-sided
    sheets_needed = (quantity * pages) / 4
elif pages % 2 == 0:
    # Single-sided cover, 2-sided internals
    cover_sheets = quantity
    internal_sheets = (quantity * (pages - 2)) / 4
else:
    # Invalid page count
    raise Exception("Invalid page count for booklet")
```

### Ridged Board Double-Sided Rules
- **Material Increase**: 15% extra material for double-sided printing
- **Ink Cost**: Doubled for both sides
- **Machine Assignment**: Determined by stock type and size requirements

### Size Limitations
- **Maximum Width**: 330mm (SRA3 press width)
- **Maximum Height**: 483mm (SRA3 press height)
- **Banner Exceptions**: Up to 700mm height on banner press
- **Ridged Boards**: Machine-specific size limits

### Quantity Breaks
- **Minimum Order**: 1 unit for all products
- **Maximum Order**: 100,000 units (varies by product)
- **Margin Breaks**: Multiple tiers based on job value
- **Setup Cost Amortization**: Fixed setup costs spread over quantity

---

**Document Status**: Complete database schema and business rules  
**Coverage**: All 9 primary tables with relationships and constraints  
**Implementation Ready**: Full SQL DDL and business logic documented  
**Last Updated**: August 25, 2025

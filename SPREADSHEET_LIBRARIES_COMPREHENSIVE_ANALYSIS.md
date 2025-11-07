# Spreadsheet Libraries Comprehensive Analysis

**Date:** November 8, 2025  
**Purpose:** Analyze Python libraries for Excel/Google Sheets creation, formulas, statistics, and data analysis

---

## EXECUTIVE SUMMARY

Python offers POWERFUL libraries for spreadsheet automation, far beyond simple cell manipulation. This analysis covers:

1. **Spreadsheet Creation/Manipulation:** openpyxl, XlsxWriter, xlwings, gspread, pygsheets
2. **Formula Support:** formulas, xlcalculator, xlwings (UDFs)
3. **Data Analysis:** pandas, numpy, scipy, statsmodels, scikit-learn
4. **Statistics/Mathematics:** scipy.stats, statsmodels, pingouin, pyod

---

## 1. SPREADSHEET CREATION LIBRARIES

### A) Excel-Focused Libraries

#### **openpyxl** (PRIMARY for Excel)
- **Best For:** Creating/editing .xlsx files with full formatting and formula support
- **Capabilities:**
  - Read/write .xlsx, .xlsm files
  - Full formatting control (fonts, colors, borders, number formats)
  - **Formulas:** Can insert formulas (preserves them, doesn't calculate)
  - Charts (30+ chart types: bar, line, scatter, pie, etc.)
  - Images, conditional formatting
  - Cell merging, data validation
  - Named ranges, tables
  - Worksheet protection
- **Limitations:** 
  - Does NOT calculate formulas (just stores them)
  - For calculation, need external tools (LibreOffice or xlcalculator)
- **Example:**
```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference

wb = Workbook()
ws = wb.active

# Add data
ws['A1'] = 'Product'
ws['B1'] = 'Sales'
ws['A2'] = 'Widgets'
ws['B2'] = 1000

# Add formula
ws['B3'] = '=SUM(B2)'

# Add chart
chart = BarChart()
chart.add_data(Reference(ws, min_col=2, min_row=1, max_row=3))
ws.add_chart(chart, 'D1')

wb.save('sales.xlsx')
```

#### **XlsxWriter** (Excel Write-Only)
- **Best For:** Creating Excel files from scratch (cannot read/edit existing)
- **Capabilities:**
  - Write-only (fast performance for large files)
  - **Formulas:** Full formula support (all Excel functions)
  - Charts, images, sparklines
  - Conditional formatting
  - Rich text formatting
  - Memory optimization mode
- **Performance:** 4x faster than openpyxl for large files
- **Example:**
```python
import xlsxwriter

workbook = xlsxwriter.Workbook('report.xlsx')
worksheet = workbook.add_worksheet()

# Add formulas
worksheet.write('A1', 'Product')
worksheet.write('B1', 'Sales')
worksheet.write('A2', 'Widgets')
worksheet.write('B2', 1000)
worksheet.write_formula('B3', '=SUM(B2)')
worksheet.write_formula('C2', '=B2*1.2')  # 20% markup

# Add chart
chart = workbook.add_chart({'type': 'column'})
chart.add_series({'values': '=Sheet1!$B$2:$B$2'})
worksheet.insert_chart('D2', chart)

workbook.close()
```

#### **xlwings** (Excel Integration Platform)
- **Best For:** Python-Excel bidirectional communication, UDFs, automation
- **Unique Features:**
  - **User Defined Functions (UDFs)** - Write Excel functions in Python (Windows only)
  - **Macros** - Replace VBA with Python
  - **Scripting** - Automate Excel from Python
  - Works with Excel on Windows and Mac
  - Real-time interaction with running Excel instance
  - Full integration with numpy and pandas
- **UDF Example:**
```python
import xlwings as xw
import pandas as pd
import numpy as np

@xw.func
def matrix_mult(x: np.array, y: np.array):
    """Matrix multiplication in Excel"""
    return x @ y

@xw.func
def analyze_data(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze DataFrame and return statistics"""
    return df.describe()

@xw.func
def price_with_tax(price, tax_rate=0.2):
    """Calculate price including tax"""
    return price * (1 + tax_rate)
```

---

### B) Google Sheets Libraries

#### **gspread** (Most Popular)
- **Best For:** Google Sheets API interactions
- **Capabilities:**
  - Create, read, update Google Sheets
  - Cell formatting, borders
  - **Formulas:** Full Google Sheets formula support
  - Batch updates (efficient)
  - Share permissions
  - Works with service accounts
- **Example:**
```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Create spreadsheet
sheet = client.create('Sales Report')
worksheet = sheet.get_worksheet(0)

# Add formulas
worksheet.update_acell('A1', 'Product')
worksheet.update_acell('B1', 'Sales')
worksheet.update_acell('A2', 'Widgets')
worksheet.update_acell('B2', 1000)
worksheet.update_acell('B3', '=SUM(B2)')
```

#### **pygsheets** (Google Sheets API v4)
- **Best For:** Advanced Google Sheets features
- **Capabilities:**
  - All gspread features PLUS:
  - Data validation
  - Conditional formatting
  - Protected ranges
  - Charts
  - Named ranges
  - More Pythonic API
- **Example:**
```python
import pygsheets

gc = pygsheets.authorize(service_file='credentials.json')

# Create and populate
sh = gc.create('Sales Dashboard')
wks = sh[0]

wks.update_values('A1', [['Product', 'Sales']])
wks.update_values('A2', [['Widgets', 1000]])

# Add formula
wks.update_value('B3', '=SUM(B2)')

# Add chart
chart = wks.add_chart(('D1', 'G10'), [(2, 3)], chart_type='COLUMN')
```

---

## 2. FORMULA CALCULATION LIBRARIES

### **formulas** - Excel Formula Interpreter
- **Purpose:** Parse and execute Excel formulas in Python
- **Capabilities:**
  - Interprets ~400 Excel functions
  - Builds dependency graph
  - Evaluates formulas in correct order
  - Supports cell ranges, named ranges
  - Works with complex nested formulas
- **Use Case:** Calculate values from Excel files without Excel
- **Example:**
```python
import formulas

# Load Excel file and build calculation model
fpath = 'data.xlsx'
xl_model = formulas.ExcelModel().loads(fpath).finish()

# Calculate all formulas
xl_model.calculate()

# Get specific cell value
result = xl_model['Sheet1!A1'].value

# Or compile specific formula
func = formulas.Parser().ast('=SUM(A1:A10, B1:B10)')[1].compile()
result = func(A1=10, A2=20, ..., B10=50)
```

### **xlcalculator** - Excel Formula Execution
- **Purpose:** Convert Excel formulas to Python and evaluate
- **Capabilities:**
  - Loads Excel workbooks
  - Extracts formula dependencies
  - Evaluates formulas
  - Supports ~200 Excel functions
  - Works with pandas DataFrames
- **Example:**
```python
from xlcalculator import ModelCompiler, Model, Evaluator

# Load workbook
compiler = ModelCompiler()
model = compiler.read_and_parse_archive('example.xlsx')

# Evaluate formula
evaluator = Evaluator(model)
result = evaluator.evaluate('Sheet1!A1')

# Or compile and run
model = Model()
model.set_cell_value('Sheet1!A1', 10)
model.set_cell_value('Sheet1!A2', 20)
model.set_cell_formula('Sheet1!A3', '=A1+A2')
result = model.evaluate('Sheet1!A3')  # Returns 30
```

---

## 3. DATA ANALYSIS LIBRARIES (The Core Power)

### **pandas** - Data Manipulation Powerhouse
- **The #1 tool for spreadsheet-like data**
- **Capabilities:**
  - DataFrames (spreadsheet-like structures)
  - 100+ statistical functions
  - Group by, pivot tables
  - Time series analysis
  - Data cleaning, merging, joining
  - Excel I/O (read/write .xlsx)
  - **Formula equivalent:** All Excel formulas can be replicated
- **Excel Integration:**
```python
import pandas as pd

# Read Excel
df = pd.read_excel('sales.xlsx', sheet_name='Data')

# Data analysis (replaces Excel formulas)
df['Total'] = df['Quantity'] * df['Price']  # Instead of =B2*C2
df['Running Total'] = df['Total'].cumsum()  # Instead of =SUM($D$2:D2)
df['Percent'] = df['Total'] / df['Total'].sum()  # Percentage of total

# Group by (pivot table)
summary = df.groupby('Product').agg({
    'Quantity': 'sum',
    'Total': 'mean'
})

# Statistical analysis
stats = df.describe()  # Count, mean, std, min, 25%, 50%, 75%, max

# Write back to Excel with formulas
with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Data')
    summary.to_excel(writer, sheet_name='Summary')
```

### **numpy** - Numerical Computing
- **Purpose:** Array operations, linear algebra, mathematical functions
- **Capabilities:**
  - Multi-dimensional arrays
  - 1000+ mathematical functions
  - Linear algebra (matrix operations)
  - Fourier transforms
  - Random number generation
  - Statistical functions
- **Excel Integration:**
```python
import numpy as np
import pandas as pd

# Array operations (faster than Excel)
data = np.array([[1, 2], [3, 4], [5, 6]])

# Matrix multiplication (=MMULT in Excel)
matrix1 = np.array([[1, 2], [3, 4]])
matrix2 = np.array([[5, 6], [7, 8]])
result = matrix1 @ matrix2  # or np.matmul(matrix1, matrix2)

# Statistical functions
mean = np.mean(data, axis=0)
std = np.std(data, axis=0)
correlation = np.corrcoef(data.T)

# Use with pandas
df = pd.DataFrame(data, columns=['A', 'B'])
df['C'] = np.sqrt(df['A']**2 + df['B']**2)  # Pythagorean theorem
```

---

## 4. STATISTICS & MATHEMATICS LIBRARIES

### **statsmodels** - Statistical Modeling
- **Purpose:** Econometrics and statistical analysis
- **Capabilities:**
  - Regression models (linear, logistic, generalized)
  - Time series analysis (ARIMA, VAR, state space)
  - Hypothesis testing (t-tests, F-tests, chi-square)
  - ANOVA
  - Statistical graphics
- **Excel Equivalent:** Data Analysis Toolpak on steroids
- **Example:**
```python
import statsmodels.api as sm
import pandas as pd

# Linear regression (like Excel's LINEST)
df = pd.read_excel('sales_data.xlsx')
X = df[['Advertising', 'Price']]
y = df['Sales']
X = sm.add_constant(X)  # Add intercept

model = sm.OLS(y, X).fit()
print(model.summary())  # R-squared, p-values, coefficients

# Predictions
predictions = model.predict(X)

# Time series analysis
from statsmodels.tsa.arima.model import ARIMA
ts_data = df['Sales']
model = ARIMA(ts_data, order=(1,1,1))
results = model.fit()
forecast = results.forecast(steps=10)
```

### **scipy** - Scientific Computing
- **Purpose:** Advanced mathematical functions and algorithms
- **Capabilities:**
  - **scipy.stats:** 100+ statistical distributions
  - **scipy.optimize:** Optimization algorithms (Solver equivalent)
  - **scipy.integrate:** Numerical integration
  - **scipy.interpolate:** Data interpolation
  - **scipy.linalg:** Linear algebra
- **Example:**
```python
from scipy import stats, optimize
import numpy as np

# Statistical tests
data1 = [1, 2, 3, 4, 5]
data2 = [2, 3, 4, 5, 6]

# T-test (like Excel's TTEST)
t_stat, p_value = stats.ttest_ind(data1, data2)

# Correlation (like Excel's CORREL)
correlation, p_value = stats.pearsonr(data1, data2)

# Curve fitting / regression
def func(x, a, b):
    return a * x + b

xdata = np.array([1, 2, 3, 4, 5])
ydata = np.array([2, 4, 6, 8, 10])

params, covariance = optimize.curve_fit(func, xdata, ydata)

# Optimization (Solver equivalent)
def objective(x):
    return x[0]**2 + x[1]**2

result = optimize.minimize(objective, x0=[5, 5])
```

### **scikit-learn** - Machine Learning
- **Purpose:** Predictive modeling and data mining
- **Capabilities:**
  - Regression (linear, polynomial, ridge, lasso)
  - Classification (decision trees, random forest, SVM)
  - Clustering (k-means, hierarchical)
  - Dimensionality reduction (PCA)
  - Model evaluation metrics
- **Example:**
```python
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import pandas as pd

# Regression
df = pd.read_excel('sales.xlsx')
X = df[['Advertising']]
y = df['Sales']

model = LinearRegression()
model.fit(X, y)
predictions = model.predict(X)

# Clustering
data = df[['Age', 'Income']]
kmeans = KMeans(n_clusters=3)
df['Cluster'] = kmeans.fit_predict(data)
```

### **pingouin** - Statistical Tests
- **Purpose:** Statistical analysis focused on usability
- **Capabilities:**
  - ANOVA, ANCOVA
  - Post-hoc tests
  - Non-parametric tests
  - Correlation matrices
  - Effect sizes
  - More user-friendly than statsmodels
- **Example:**
```python
import pingouin as pg
import pandas as pd

df = pd.read_excel('experiment_data.xlsx')

# ANOVA
aov = pg.anova(data=df, dv='Score', between='Group')

# Correlation matrix
corr_matrix = pg.pairwise_corr(df, columns=['A', 'B', 'C'])

# T-test
ttest = pg.ttest(df['Group1'], df['Group2'])
```

---

## 5. RECOMMENDED ARCHITECTURE FOR AI AGENTS

### Option 1: Excel-Based Workflow

```python
"""
Excel Tool Stack for AI Agents
"""
import openpyxl
from openpyxl.chart import BarChart, LineChart, PieChart
from openpyxl.styles import Font, Fill, Border, Alignment
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm

def create_excel_report_with_analysis(data_source: str, output_file: str):
    """
    Create comprehensive Excel report with data, analysis, charts
    """
    # 1. Load and analyze data with pandas
    df = pd.read_csv(data_source)
    
    # Statistical analysis
    summary_stats = df.describe()
    correlation = df.corr()
    
    # 2. Create Excel workbook
    wb = openpyxl.Workbook()
    
    # Sheet 1: Raw Data
    ws_data = wb.active
    ws_data.title = "Data"
    for r_idx, row in enumerate(df.values, start=1):
        for c_idx, value in enumerate(row, start=1):
            ws_data.cell(r_idx, c_idx, value)
    
    # Sheet 2: Summary Statistics
    ws_stats = wb.create_sheet("Statistics")
    # Write summary_stats DataFrame to sheet
    for r_idx, row in enumerate(summary_stats.values, start=2):
        for c_idx, value in enumerate(row, start=2):
            ws_stats.cell(r_idx, c_idx, value)
    
    # Add formulas
    ws_stats['B10'] = '=AVERAGE(Data!B:B)'
    ws_stats['B11'] = '=STDEV(Data!B:B)'
    
    # Sheet 3: Charts
    ws_charts = wb.create_sheet("Charts")
    
    chart = BarChart()
    chart.title = "Sales by Product"
    chart.add_data(Reference(ws_data, min_col=2, min_row=1, max_row=10))
    ws_charts.add_chart(chart, 'A1')
    
    # Save
    wb.save(output_file)
    
    return {
        'file': output_file,
        'sheets': 3,
        'rows': len(df),
        'summary': summary_stats.to_dict()
    }
```

### Option 2: Google Sheets-Based Workflow

```python
"""
Google Sheets Tool Stack for AI Agents
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np

def create_google_sheets_dashboard(df: pd.DataFrame, spreadsheet_name: str):
    """
    Create Google Sheets with data, formulas, and charts
    """
    # Authenticate
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)
    
    # Create spreadsheet
    sh = client.create(spreadsheet_name)
    
    # Sheet 1: Data
    wks_data = sh.get_worksheet(0)
    wks_data.update([df.columns.values.tolist()] + df.values.tolist())
    
    # Sheet 2: Analysis
    wks_analysis = sh.add_worksheet(title="Analysis", rows=100, cols=20)
    
    # Add formulas
    wks_analysis.update('A1', 'Metric')
    wks_analysis.update('B1', 'Value')
    wks_analysis.update('A2', 'Average')
    wks_analysis.update('B2', '=AVERAGE(Data!B:B)')
    wks_analysis.update('A3', 'Total')
    wks_analysis.update('B3', '=SUM(Data!B:B)')
    wks_analysis.update('A4', 'Count')
    wks_analysis.update('B4', '=COUNT(Data!B:B)')
    
    # Share
    sh.share('user@example.com', perm_type='user', role='writer')
    
    return {
        'url': sh.url,
        'sheets': 2,
        'rows': len(df)
    }
```

---

## 6. TOOL RECOMMENDATIONS BY USE CASE

### Use Case 1: Business Reports
**Tools:** openpyxl + pandas + matplotlib
- Load data with pandas
- Analyze with pandas/numpy
- Create charts with matplotlib
- Export to Excel with openpyxl
- Add formulas for dynamic updates

### Use Case 2: Financial Analysis
**Tools:** pandas + statsmodels + openpyxl
- Time series analysis with statsmodels
- Regression models
- Forecasting
- Export to Excel with formulas

### Use Case 3: Data Dashboards
**Tools:** pandas + pygsheets + plotly
- Real-time data updates
- Google Sheets for collaboration
- Interactive charts
- Automated refresh

### Use Case 4: Statistical Reports
**Tools:** pandas + scipy + pingouin + openpyxl
- Statistical tests
- Correlation analysis
- ANOVA
- Export to formatted Excel

### Use Case 5: Excel Automation
**Tools:** xlwings + pandas + numpy
- Python UDFs in Excel
- Replace VBA macros
- Real-time calculations
- Works on existing Excel files

---

## 7. INTEGRATION WITH CURRENT AI AGENT PLATFORM

### Recommended New Tools:

#### A) Excel Tools (4 new tools)

1. **excel_create_with_analysis**
   - Create Excel with data, formulas, charts
   - Uses: openpyxl + pandas + matplotlib
   - Input: DataFrame, chart types, formula specs
   - Output: .xlsx file with multiple sheets

2. **excel_add_formulas**
   - Add Excel formulas to existing workbook
   - Uses: openpyxl + formulas library
   - Input: Workbook path, formula definitions
   - Output: Updated workbook

3. **excel_calculate_formulas**
   - Calculate formulas without Excel
   - Uses: xlcalculator or formulas library
   - Input: .xlsx file
   - Output: Calculated values

4. **excel_create_udf**
   - Create Python UDF for Excel (Windows only)
   - Uses: xlwings
   - Input: Function definition
   - Output: UDF code and installation instructions

#### B) Google Sheets Tools (3 new tools)

5. **google_sheets_create_with_formulas**
   - Create Google Sheets with formulas
   - Uses: gspread + pandas
   - Input: DataFrame, formula specs
   - Output: Google Sheets URL

6. **google_sheets_add_chart**
   - Add charts to Google Sheets
   - Uses: pygsheets
   - Input: Sheet ID, data range, chart type
   - Output: Updated sheet with chart

7. **google_sheets_apply_formatting**
   - Apply conditional formatting and styles
   - Uses: pygsheets
   - Input: Sheet ID, formatting rules
   - Output: Formatted sheet

#### C) Data Analysis Tools (5 new tools)

8. **analyze_data_statistics**
   - Run statistical analysis on data
   - Uses: pandas + scipy + statsmodels
   - Input: Data source, analysis type
   - Output: Statistical results

9. **create_regression_model**
   - Build regression model
   - Uses: statsmodels or scikit-learn
   - Input: X variables, y variable
   - Output: Model results, predictions

10. **calculate_correlations**
    - Correlation matrix and tests
    - Uses: pandas + scipy.stats
    - Input: DataFrame
    - Output: Correlation matrix, p-values

11. **run_hypothesis_test**
    - Statistical hypothesis testing
    - Uses: scipy.stats + pingouin
    - Input: Test type, data
    - Output: Test results

12. **create_pivot_analysis**
    - Create pivot table analysis
    - Uses: pandas
    - Input: DataFrame, pivot specs
    - Output: Pivot table results

---

## 8. IMPLEMENTATION PRIORITY

### High Priority (Implement First):
1. **excel_create_with_analysis** - Most versatile, combines everything
2. **google_sheets_create_with_formulas** - Essential for cloud collaboration
3. **analyze_data_statistics** - Core analytical capability
4. **calculate_correlations** - Frequently requested

### Medium Priority:
5. **excel_add_formulas** - Extends existing Excel tools
6. **create_regression_model** - Advanced analytics
7. **google_sheets_add_chart** - Visualization

### Low Priority:
8. **excel_calculate_formulas** - Niche use case
9. **excel_create_udf** - Windows-only, advanced users
10. **run_hypothesis_test** - Specialized statistical needs

---

## 9. CODE EXAMPLES FOR TOOL IMPLEMENTATION

### Example: excel_create_with_analysis

```python
def excel_create_with_analysis(
    data: pd.DataFrame,
    output_file: str,
    charts: List[Dict] = None,
    formulas: List[Dict] = None,
    statistics: bool = True
) -> Dict[str, Any]:
    """
    Create Excel workbook with data, analysis, charts, and formulas
    
    Args:
        data: pandas DataFrame with source data
        output_file: Path to output .xlsx file
        charts: List of chart specifications
        formulas: List of formula definitions
        statistics: Include statistics sheet
    
    Returns:
        Dict with file path, sheet names, and summary
    """
    wb = openpyxl.Workbook()
    
    # Sheet 1: Raw Data
    ws_data = wb.active
    ws_data.title = "Data"
    
    # Write headers
    for c_idx, col_name in enumerate(data.columns, start=1):
        ws_data.cell(1, c_idx, col_name)
    
    # Write data
    for r_idx, row in enumerate(data.values, start=2):
        for c_idx, value in enumerate(row, start=1):
            ws_data.cell(r_idx, c_idx, value)
    
    # Sheet 2: Statistics (if requested)
    if statistics:
        ws_stats = wb.create_sheet("Statistics")
        summary = data.describe()
        
        # Write summary statistics
        ws_stats['A1'] = 'Statistic'
        for c_idx, col in enumerate(summary.columns, start=2):
            ws_stats.cell(1, c_idx, col)
        
        for r_idx, (stat_name, row) in enumerate(summary.iterrows(), start=2):
            ws_stats.cell(r_idx, 1, stat_name)
            for c_idx, value in enumerate(row, start=2):
                ws_stats.cell(r_idx, c_idx, value)
        
        # Add formulas
        last_row = len(data) + 1
        ws_stats['A10'] = 'Average (Formula)'
        ws_stats['B10'] = f'=AVERAGE(Data!B2:B{last_row})'
        ws_stats['A11'] = 'StdDev (Formula)'
        ws_stats['B11'] = f'=STDEV(Data!B2:B{last_row})'
    
    # Sheet 3: Charts
    if charts:
        ws_charts = wb.create_sheet("Charts")
        
        for chart_spec in charts:
            if chart_spec['type'] == 'bar':
                chart = BarChart()
            elif chart_spec['type'] == 'line':
                chart = LineChart()
            elif chart_spec['type'] == 'pie':
                chart = PieChart()
            
            chart.title = chart_spec.get('title', 'Chart')
            
            # Add data
            data_range = Reference(
                ws_data,
                min_col=chart_spec['data_col'],
                min_row=1,
                max_row=len(data) + 1
            )
            chart.add_data(data_range, titles_from_data=True)
            
            # Place chart
            ws_charts.add_chart(chart, chart_spec.get('position', 'A1'))
    
    # Add custom formulas
    if formulas:
        for formula_spec in formulas:
            sheet = wb[formula_spec['sheet']]
            sheet[formula_spec['cell']] = formula_spec['formula']
    
    # Save
    wb.save(output_file)
    
    return {
        'file': output_file,
        'sheets': len(wb.sheetnames),
        'rows': len(data),
        'columns': len(data.columns),
        'charts': len(charts) if charts else 0,
        'formulas': len(formulas) if formulas else 0
    }
```

### Example: analyze_data_statistics

```python
def analyze_data_statistics(
    data: pd.DataFrame,
    analysis_type: str = 'summary'
) -> Dict[str, Any]:
    """
    Perform statistical analysis on data
    
    Args:
        data: pandas DataFrame
        analysis_type: 'summary', 'correlation', 'regression', 'hypothesis'
    
    Returns:
        Dict with analysis results
    """
    results = {}
    
    if analysis_type == 'summary':
        results['summary'] = data.describe().to_dict()
        results['missing'] = data.isnull().sum().to_dict()
        results['dtypes'] = data.dtypes.astype(str).to_dict()
    
    elif analysis_type == 'correlation':
        numeric_data = data.select_dtypes(include=[np.number])
        results['correlation_matrix'] = numeric_data.corr().to_dict()
        
        # P-values for each correlation
        from scipy.stats import pearsonr
        p_values = pd.DataFrame(
            np.zeros((len(numeric_data.columns), len(numeric_data.columns))),
            columns=numeric_data.columns,
            index=numeric_data.columns
        )
        
        for col1 in numeric_data.columns:
            for col2 in numeric_data.columns:
                if col1 != col2:
                    _, p_val = pearsonr(numeric_data[col1], numeric_data[col2])
                    p_values.loc[col1, col2] = p_val
        
        results['p_values'] = p_values.to_dict()
    
    elif analysis_type == 'regression':
        # Simple linear regression (first two numeric columns)
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            X = data[numeric_cols[0]]
            y = data[numeric_cols[1]]
            
            model = sm.OLS(y, sm.add_constant(X)).fit()
            
            results['r_squared'] = model.rsquared
            results['coefficients'] = {
                'intercept': model.params[0],
                'slope': model.params[1]
            }
            results['p_values'] = {
                'intercept': model.pvalues[0],
                'slope': model.pvalues[1]
            }
    
    return results
```

---

## 10. DEPENDENCIES TO ADD

```python
# requirements.txt additions

# Spreadsheet libraries
openpyxl==3.1.2
XlsxWriter==3.1.9
xlwings==0.30.13  # Windows only for UDFs
gspread==5.12.0
pygsheets==2.0.6

# Formula libraries
formulas==1.2.5
xlcalculator==0.5.0

# Data analysis
pandas==2.1.4
numpy==1.26.2
scipy==1.11.4
statsmodels==0.14.1
scikit-learn==1.3.2

# Statistics
pingouin==0.5.4
ydata-profiling==4.6.1  # Exploratory data analysis

# Visualization (for charts)
matplotlib==3.8.2
seaborn==0.13.0
plotly==5.18.0

# OAuth for Google Sheets
oauth2client==4.1.3
```

---

## 11. CONCLUSION

Python's spreadsheet ecosystem is VASTLY superior to Excel/Google Sheets for:

 **Data Analysis:** pandas + numpy = Excel on steroids
 **Statistics:** scipy + statsmodels = Professional statistical software
 **Automation:** openpyxl + xlwings = Full Excel control
 **Formulas:** formulas library = Excel formula engine in Python
 **Cloud Collaboration:** gspread + pygsheets = Google Sheets API mastery

**Recommendation:** Implement all 12 new tools in priority order. This will give AI agents professional-grade spreadsheet and data analysis capabilities comparable to Excel + SPSS + Tableau combined.

---

**Status:** Ready for implementation  
**Next Steps:** Create tool schemas and implementations  
**Last Updated:** November 8, 2025

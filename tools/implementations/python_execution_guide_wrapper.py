"""
Python Execution Guide Wrapper
Returns comprehensive documentation for python_exec tools
"""
from tools.registry_v3 import tool_executor
import logging

logger = logging.getLogger(__name__)


@tool_executor()
def python_exec_get_guide():
    """
    Returns comprehensive guide for Python execution system.
    
    Provides complete documentation for all 3 python_exec tools including:
    - Tool comparison and selection guide
    - Security model and sandbox restrictions
    - Available libraries and their capabilities
    - 20+ code patterns and examples
    - Common use cases and workflows
    - Error handling and troubleshooting
    - Best practices for code generation
    
    Returns:
        dict: Complete guide object with all documentation
    """
    
    guide = {
        "success": True,
        "guide_version": "1.0",
        "last_updated": "2026-01-02",
        
        "overview": {
            "title": "Python Execution System - Complete Guide",
            "description": "Sandboxed Python code execution with data analysis, visualization, and computation capabilities",
            "total_tools": 3,
            "security_model": "RestrictedPython with 30-second timeout",
            "key_capabilities": [
                "Data analysis with pandas/numpy",
                "Visualization with matplotlib/seaborn",
                "Statistical computations",
                "Data transformation and cleaning",
                "Custom calculations and business logic"
            ]
        },
        
        "tool_comparison": {
            "decision_tree": """
┌─────────────────────────────────────────────────────┐
│         Which Python Exec Tool Should I Use?        │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
              Do you have data to analyze?
                    │           │
                   YES          NO
                    │           │
                    ▼           ▼
      Where is the data?    Just need to
         │          │        run code?
       FILE      MEMORY          │
         │          │            │
         ▼          ▼            ▼
python_exec_     python_exec_   python_exec()
analysis()      with_dataframe()
                    
│ Load CSV      │ Pass dict/   │ General
│ Auto-inject   │  DataFrame   │  purpose
│ as 'df'       │ as 'df'      │ execution
""",
            "tools": [
                {
                    "name": "python_exec",
                    "best_for": "General code execution, calculations, custom logic",
                    "data_source": "Code generates data OR uses globals_dict",
                    "when_to_use": [
                        "Custom calculations without external data",
                        "Code that generates its own data",
                        "Mathematical/statistical computations",
                        "Text processing or JSON manipulation",
                        "When you need full control over imports and setup"
                    ],
                    "example": "python_exec(code='result = 5 * 10\\nprint(f\"Result: {result}\")')"
                },
                {
                    "name": "python_exec_with_dataframe",
                    "best_for": "Analyzing data already in memory",
                    "data_source": "Dict or DataFrame passed as parameter",
                    "when_to_use": [
                        "Data already loaded from database/API",
                        "Analyzing results from another tool",
                        "Quick data transformations",
                        "When data is small enough to pass directly"
                    ],
                    "example": "python_exec_with_dataframe(code='print(df.describe())', dataframe={'col': [1,2,3]})"
                },
                {
                    "name": "python_exec_analysis",
                    "best_for": "Analyzing CSV files",
                    "data_source": "CSV file path",
                    "when_to_use": [
                        "User provides CSV file",
                        "Large datasets in files",
                        "Workspace has data files",
                        "One-liner analysis workflows"
                    ],
                    "example": "python_exec_analysis(code='print(df.head())', data_file='sales.csv')"
                }
            ]
        },
        
        "security_model": {
            "sandbox": "RestrictedPython",
            "timeout": "30 seconds (hard limit)",
            "allowed_operations": {
                "data_analysis": "✅ pandas DataFrame operations, numpy calculations",
                "visualization": "✅ matplotlib plots, seaborn charts",
                "math": "✅ Mathematical functions, statistics",
                "text": "✅ String manipulation, regex, JSON/CSV parsing",
                "datetime": "✅ Date/time operations and calculations"
            },
            "blocked_operations": {
                "file_system": "❌ open(), read(), write() - No file access outside workspace",
                "network": "❌ requests, urllib, socket - No HTTP calls or network access",
                "subprocess": "❌ subprocess, os.system - No system command execution",
                "dangerous": "❌ eval(), exec() on user input - No code injection",
                "imports": "❌ Only whitelisted modules allowed"
            },
            "allowed_imports": [
                "pandas (as pd)",
                "numpy (as np)",
                "matplotlib (as plt, matplotlib.pyplot)",
                "seaborn (as sns)",
                "datetime",
                "time",
                "math",
                "json",
                "re",
                "collections",
                "itertools",
                "functools",
                "operator",
                "copy",
                "typing"
            ],
            "blocked_imports": [
                "requests - Use API tools instead",
                "urllib - Use web_fetch tools instead",
                "subprocess - Cannot execute system commands",
                "os - Limited access (no file operations)",
                "sys - Limited access",
                "socket - No network programming",
                "pickle - Security risk",
                "Any module not in whitelist"
            ]
        },
        
        "code_patterns": {
            "data_analysis": [
                {
                    "name": "Basic Statistics",
                    "code": """import pandas as pd
import numpy as np

# Summary statistics
print(df.describe())

# Mean and median
mean_value = df['column'].mean()
median_value = df['column'].median()

print(f"Mean: {mean_value:.2f}")
print(f"Median: {median_value:.2f}")"""
                },
                {
                    "name": "Group By Analysis",
                    "code": """# Group and aggregate
summary = df.groupby('category').agg({
    'sales': ['sum', 'mean', 'count'],
    'profit': 'sum'
})

print(summary)"""
                },
                {
                    "name": "Filtering and Selection",
                    "code": """# Filter data
high_sales = df[df['sales'] > 1000]
recent = df[df['date'] > '2025-01-01']

# Multiple conditions
filtered = df[(df['sales'] > 500) & (df['region'] == 'North')]

print(f"Found {len(filtered)} matching rows")"""
                },
                {
                    "name": "Data Transformation",
                    "code": """# Create new columns
df['total'] = df['price'] * df['quantity']
df['profit_margin'] = (df['profit'] / df['revenue']) * 100

# Apply functions
df['category'] = df['product'].apply(lambda x: x.split('-')[0])

print(df.head())"""
                }
            ],
            "visualization": [
                {
                    "name": "Line Chart",
                    "code": """import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(df['date'], df['sales'], marker='o')
plt.title('Sales Over Time')
plt.xlabel('Date')
plt.ylabel('Sales ($)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('sales_chart.png')

print("Chart saved to sales_chart.png")"""
                },
                {
                    "name": "Bar Chart",
                    "code": """import matplotlib.pyplot as plt

summary = df.groupby('category')['sales'].sum().sort_values(ascending=False)

plt.figure(figsize=(10, 6))
summary.plot(kind='bar')
plt.title('Sales by Category')
plt.xlabel('Category')
plt.ylabel('Total Sales ($)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('category_chart.png')

print("Chart created successfully")"""
                },
                {
                    "name": "Histogram",
                    "code": """import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.hist(df['price'], bins=20, edgecolor='black')
plt.title('Price Distribution')
plt.xlabel('Price ($)')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig('price_distribution.png')

print("Distribution chart saved")"""
                }
            ],
            "calculations": [
                {
                    "name": "Statistical Analysis",
                    "code": """import numpy as np
from scipy import stats

# Correlation
correlation = np.corrcoef(df['x'], df['y'])[0, 1]

# Standard deviation
std_dev = df['values'].std()

# Percentiles
p25 = df['values'].quantile(0.25)
p75 = df['values'].quantile(0.75)

print(f"Correlation: {correlation:.3f}")
print(f"Std Dev: {std_dev:.2f}")
print(f"25th percentile: {p25:.2f}")
print(f"75th percentile: {p75:.2f}")"""
                },
                {
                    "name": "Business Calculations",
                    "code": """# Revenue calculation
df['revenue'] = df['price'] * df['quantity']

# Profit margin
df['profit_margin'] = ((df['revenue'] - df['cost']) / df['revenue']) * 100

# Cumulative sum
df['cumulative_sales'] = df['sales'].cumsum()

# Total summary
total_revenue = df['revenue'].sum()
avg_margin = df['profit_margin'].mean()

print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Average Margin: {avg_margin:.1f}%")"""
                },
                {
                    "name": "Date Calculations",
                    "code": """import pandas as pd
from datetime import datetime, timedelta

# Convert to datetime
df['date'] = pd.to_datetime(df['date'])

# Calculate age
df['days_old'] = (datetime.now() - df['date']).dt.days

# Filter by date range
last_30_days = df[df['date'] >= datetime.now() - timedelta(days=30)]

print(f"Records in last 30 days: {len(last_30_days)}")"""
                }
            ]
        },
        
        "common_use_cases": {
            "data_analysis": {
                "description": "Analyze datasets with pandas",
                "scenarios": [
                    "Calculate summary statistics (mean, median, std)",
                    "Group data and aggregate (sum, count, average)",
                    "Filter and select specific records",
                    "Find outliers and anomalies",
                    "Calculate correlations between variables"
                ],
                "example_request": "Analyze this sales data and show me the top 10 products by revenue",
                "tool_to_use": "python_exec_with_dataframe"
            },
            "visualization": {
                "description": "Create charts and plots",
                "scenarios": [
                    "Line charts for trends over time",
                    "Bar charts for category comparisons",
                    "Histograms for distribution analysis",
                    "Scatter plots for correlations",
                    "Pie charts for proportions"
                ],
                "example_request": "Create a chart showing sales trends over the last 6 months",
                "tool_to_use": "python_exec or python_exec_with_dataframe"
            },
            "calculations": {
                "description": "Custom business logic",
                "scenarios": [
                    "Calculate pricing with complex formulas",
                    "Apply business rules and discounts",
                    "Compute financial metrics (ROI, margins)",
                    "Statistical analysis and hypothesis testing",
                    "Mathematical modeling"
                ],
                "example_request": "Calculate the profit margin for each product category",
                "tool_to_use": "python_exec or python_exec_with_dataframe"
            },
            "transformation": {
                "description": "Clean and transform data",
                "scenarios": [
                    "Format dates and timestamps",
                    "Clean text fields (trim, uppercase)",
                    "Merge and join datasets",
                    "Reshape data (pivot, unpivot)",
                    "Handle missing values"
                ],
                "example_request": "Clean this customer data and standardize the phone numbers",
                "tool_to_use": "python_exec_with_dataframe"
            }
        },
        
        "error_handling": {
            "common_errors": [
                {
                    "error": "ImportError: Import of 'requests' is not allowed",
                    "cause": "Trying to import blocked module",
                    "solution": "Use allowed libraries only. For HTTP, use web_fetch or API tools instead"
                },
                {
                    "error": "NameError: name 'open' is not defined",
                    "cause": "Trying to access file system",
                    "solution": "Use workspace_dir parameter or universal_file_tools for file operations"
                },
                {
                    "error": "PythonExecutionTimeout: Execution exceeded 30 seconds",
                    "cause": "Code takes too long (infinite loop or large dataset)",
                    "solution": "Optimize code, reduce data size, or break into smaller chunks"
                },
                {
                    "error": "KeyError: 'column_name'",
                    "cause": "Column doesn't exist in DataFrame",
                    "solution": "Check df.columns first or use df.get('column', default_value)"
                },
                {
                    "error": "SyntaxError: invalid syntax",
                    "cause": "Python syntax error in code",
                    "solution": "Review code for typos, missing colons, or incorrect indentation"
                }
            ],
            "debugging_tips": [
                "Always print df.columns to see available columns",
                "Use df.head() to preview data before operations",
                "Print intermediate results to debug calculations",
                "Use try/except for robust error handling",
                "Test with small data before scaling up"
            ]
        },
        
        "best_practices": {
            "code_generation": [
                "✅ Always import libraries at the start",
                "✅ Include print statements for user feedback",
                "✅ Add comments explaining complex logic",
                "✅ Use descriptive variable names",
                "✅ Format numbers with appropriate precision (:.2f)",
                "✅ Handle edge cases (empty data, null values)",
                "✅ Keep code under 30 seconds execution time",
                "✅ Test with sample data first"
            ],
            "data_operations": [
                "✅ Check df.shape before operations",
                "✅ Use df.describe() to understand data",
                "✅ Filter data before expensive operations",
                "✅ Use vectorized operations (not loops)",
                "✅ Handle missing values explicitly",
                "✅ Use appropriate data types",
                "✅ Avoid loading entire large files into memory"
            ],
            "visualization": [
                "✅ Set figure size appropriately (10, 6)",
                "✅ Add titles and axis labels",
                "✅ Rotate x-axis labels if needed",
                "✅ Use tight_layout() before saving",
                "✅ Save to descriptive filenames",
                "✅ Print confirmation message",
                "✅ Close figures to free memory"
            ]
        },
        
        "integration_patterns": {
            "with_database_queries": {
                "description": "Analyze data from database queries",
                "workflow": [
                    "1. Execute SQL query with inhouse_execute_sql or similar",
                    "2. Pass results to python_exec_with_dataframe",
                    "3. Analyze with pandas",
                    "4. Return insights to user"
                ],
                "example": "Query InHouse orders → Analyze with python_exec_with_dataframe → Generate report"
            },
            "with_google_sheets": {
                "description": "Analyze Google Sheets data",
                "workflow": [
                    "1. Read sheet with google_sheets_read",
                    "2. Pass to python_exec_with_dataframe",
                    "3. Perform analysis",
                    "4. Write results back with google_sheets_write"
                ],
                "example": "Read sales sheet → Analyze trends → Write summary back to sheet"
            },
            "with_file_uploads": {
                "description": "Analyze uploaded CSV files",
                "workflow": [
                    "1. User uploads CSV",
                    "2. Use python_exec_analysis with file path",
                    "3. Perform analysis",
                    "4. Return results and/or charts"
                ],
                "example": "User uploads customer_data.csv → python_exec_analysis → Show insights"
            }
        },
        
        "quick_reference": {
            "tool_selection": {
                "Have CSV file?": "→ python_exec_analysis()",
                "Have dict/DataFrame?": "→ python_exec_with_dataframe()",
                "Just need code?": "→ python_exec()"
            },
            "common_imports": {
                "Data analysis": "import pandas as pd\\nimport numpy as np",
                "Visualization": "import matplotlib.pyplot as plt\\nimport seaborn as sns",
                "Dates": "from datetime import datetime, timedelta",
                "JSON": "import json",
                "Regex": "import re"
            },
            "pandas_cheatsheet": {
                "Read": "df.head(), df.tail(), df.describe()",
                "Filter": "df[df['col'] > 10]",
                "Group": "df.groupby('col').agg({'col2': 'sum'})",
                "Sort": "df.sort_values('col', ascending=False)",
                "New column": "df['new'] = df['a'] + df['b']"
            }
        },
        
        "next_steps": {
            "after_reading_guide": [
                "1. Choose the right tool based on your data source",
                "2. Review relevant code patterns for your use case",
                "3. Generate Python code following best practices",
                "4. Execute with appropriate python_exec tool",
                "5. Handle any errors using error_handling guide"
            ]
        },
        
        "related_documentation": {
            "files": [
                "tools/implementations/python_execution_tools.py - Implementation code",
                "test_python_exec_implementation.py - Comprehensive test suite",
                "PYTHON_EXEC_IMPLEMENTATION_COMPLETE.md - Technical documentation"
            ],
            "related_tools": [
                "universal_file_tools - File upload and processing",
                "google_sheets_* - Google Sheets integration",
                "inhouse_execute_sql - Database queries",
                "data_analysis_* - Specialized analysis tools"
            ]
        }
    }
    
    return guide

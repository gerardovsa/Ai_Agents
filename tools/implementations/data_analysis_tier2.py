"""
Data Analysis Tools - Tier 2 (Template-Based with RestrictedPython)

SECURITY: Limited code execution with RestrictedPython sandbox
PERFORMANCE: 100ms-2s execution time
MEMORY: 200-500 MB per operation

Tier 2 Tools:
1. data_execute_calculation - Custom calculations using safe templates
2. data_create_regression_model - Statistical and ML regression models

Dependencies: pandas, numpy, scipy, statsmodels, scikit-learn, RestrictedPython
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from typing import Dict, Any, List, Optional, Union
import json

try:
    from RestrictedPython import compile_restricted, safe_globals
    RESTRICTED_PYTHON_AVAILABLE = True
except ImportError:
    RESTRICTED_PYTHON_AVAILABLE = False
    print("Warning: RestrictedPython not installed. Tier 2 tools will use predefined templates only.")


class DataCalculationError(Exception):
    """Custom exception for data calculation errors"""
    pass


def data_execute_calculation(
    data_source: Union[str, dict],
    calculation_template: str,
    parameters: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Execute custom calculations using safe templates
    
    Args:
        data_source: CSV file path, JSON string, or dict
        calculation_template: Template name for calculation type
            - 'calculate_column': Add new column with formula
            - 'apply_formula': Apply mathematical formula to column
            - 'conditional': If-then-else conditional logic
            - 'lookup': VLOOKUP-style merge with another dataset
            - 'percentage': Calculate percentages
            - 'ranking': Rank, percentile, or quartile
            - 'custom': Execute custom pandas code (requires RestrictedPython)
        parameters: Template-specific parameters
            - calculate_column: {'new_column': 'Total', 'formula': 'Quantity * Price'}
            - apply_formula: {'column': 'Sales', 'operation': 'sqrt', 'new_column': 'Sales_Sqrt'}
            - conditional: {'new_column': 'Category', 'condition': 'Sales > 1000', 
                           'if_true': 'High', 'if_false': 'Low'}
            - lookup: {'lookup_data': {...}, 'on': 'ProductID', 'columns': ['ProductName', 'Category']}
            - percentage: {'column': 'Sales', 'total_column': 'TotalSales', 'new_column': 'SalesPct'}
            - ranking: {'column': 'Sales', 'method': 'dense', 'new_column': 'SalesRank'}
    
    Returns:
        Dict with calculated data and metadata
    
    Execution Time: 100-400ms
    Security: RestrictedPython sandbox for custom templates
    
    Examples:
        # Calculate total column
        data_execute_calculation('sales.csv', 'calculate_column',
                                {'new_column': 'Total', 'formula': 'Quantity * Price'})
        
        # Apply logarithm to sales
        data_execute_calculation('data.csv', 'apply_formula',
                                {'column': 'Sales', 'operation': 'log', 'new_column': 'LogSales'})
        
        # Conditional categorization
        data_execute_calculation('data.csv', 'conditional',
                                {'new_column': 'Category', 
                                 'condition': 'Revenue > 10000',
                                 'if_true': 'Premium', 
                                 'if_false': 'Standard'})
    """
    # Load data
    df = _load_data(data_source)
    
    # Route to appropriate template
    if calculation_template == 'calculate_column':
        result_df = _calculate_column(df, parameters)
    elif calculation_template == 'apply_formula':
        result_df = _apply_formula(df, parameters)
    elif calculation_template == 'conditional':
        result_df = _apply_conditional(df, parameters)
    elif calculation_template == 'lookup':
        result_df = _apply_lookup(df, parameters)
    elif calculation_template == 'percentage':
        result_df = _calculate_percentage(df, parameters)
    elif calculation_template == 'ranking':
        result_df = _calculate_ranking(df, parameters)
    elif calculation_template == 'custom':
        if not RESTRICTED_PYTHON_AVAILABLE:
            raise DataCalculationError("Custom template requires RestrictedPython (not installed)")
        result_df = _execute_custom_code(df, parameters)
    else:
        raise DataCalculationError(
            f"Unknown calculation_template: {calculation_template}. "
            f"Supported: calculate_column, apply_formula, conditional, lookup, percentage, ranking, custom"
        )
    
    return {
        'success': True,
        'template': calculation_template,
        'result': result_df.to_dict(orient='records'),
        'metadata': {
            'rows': len(result_df),
            'columns': list(result_df.columns)
        }
    }


def data_create_regression_model(
    data_source: Union[str, dict],
    model_type: str,
    target_variable: str,
    predictor_variables: List[str],
    options: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Build regression and predictive models
    
    Args:
        data_source: CSV file path, JSON string, or dict
        model_type: Type of regression model
            - 'linear': Linear regression (OLS)
            - 'logistic': Logistic regression (classification)
            - 'polynomial': Polynomial regression
            - 'ridge': Ridge regression (L2 regularization)
            - 'lasso': Lasso regression (L1 regularization)
            - 'random_forest': Random forest regression
            - 'time_series': ARIMA time series model
        target_variable: Column name for dependent variable (y)
        predictor_variables: List of column names for independent variables (X)
        options: Model-specific options
            - polynomial: {'degree': 2}
            - ridge: {'alpha': 1.0}
            - lasso: {'alpha': 1.0}
            - random_forest: {'n_estimators': 100, 'max_depth': 10}
            - time_series: {'order': (1,1,1)}
            - all: {'test_size': 0.2, 'return_predictions': True}
    
    Returns:
        Dict with model results, coefficients, metrics, and predictions
    
    Execution Time: 200ms-2s
    
    Examples:
        # Simple linear regression
        data_create_regression_model('sales.csv', 'linear',
                                     target_variable='Sales',
                                     predictor_variables=['Advertising', 'Price'])
        
        # Ridge regression with cross-validation
        data_create_regression_model('data.csv', 'ridge',
                                     target_variable='Revenue',
                                     predictor_variables=['Feature1', 'Feature2', 'Feature3'],
                                     options={'alpha': 0.5})
        
        # Random forest with predictions
        data_create_regression_model('train.csv', 'random_forest',
                                     target_variable='Target',
                                     predictor_variables=['X1', 'X2', 'X3'],
                                     options={'n_estimators': 100, 'return_predictions': True})
    """
    # Load data
    df = _load_data(data_source)
    
    # Default options
    if options is None:
        options = {}
    
    # Validate columns exist
    if target_variable not in df.columns:
        raise DataCalculationError(f"Target variable '{target_variable}' not found in data")
    
    for var in predictor_variables:
        if var not in df.columns:
            raise DataCalculationError(f"Predictor variable '{var}' not found in data")
    
    # Route to appropriate model
    if model_type == 'linear':
        result = _build_linear_regression(df, target_variable, predictor_variables, options)
    elif model_type == 'logistic':
        result = _build_logistic_regression(df, target_variable, predictor_variables, options)
    elif model_type == 'polynomial':
        result = _build_polynomial_regression(df, target_variable, predictor_variables, options)
    elif model_type == 'ridge':
        result = _build_ridge_regression(df, target_variable, predictor_variables, options)
    elif model_type == 'lasso':
        result = _build_lasso_regression(df, target_variable, predictor_variables, options)
    elif model_type == 'random_forest':
        result = _build_random_forest(df, target_variable, predictor_variables, options)
    elif model_type == 'time_series':
        result = _build_time_series_model(df, target_variable, options)
    else:
        raise DataCalculationError(
            f"Unknown model_type: {model_type}. "
            f"Supported: linear, logistic, polynomial, ridge, lasso, random_forest, time_series"
        )
    
    return {
        'success': True,
        'model_type': model_type,
        'result': result,
        'metadata': {
            'target_variable': target_variable,
            'predictor_variables': predictor_variables,
            'observations': len(df)
        }
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _load_data(data_source: Union[str, dict]) -> pd.DataFrame:
    """Load data from various sources"""
    if isinstance(data_source, str):
        if data_source.endswith('.csv'):
            return pd.read_csv(data_source)
        else:
            try:
                data = json.loads(data_source)
                return pd.DataFrame(data)
            except:
                raise DataCalculationError(f"Could not load data from: {data_source}")
    elif isinstance(data_source, dict):
        return pd.DataFrame(data_source)
    elif isinstance(data_source, pd.DataFrame):
        return data_source
    else:
        raise DataCalculationError(f"Unsupported data_source type: {type(data_source)}")


# ============================================================================
# CALCULATION TEMPLATE FUNCTIONS
# ============================================================================

def _calculate_column(df: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    """Calculate new column using formula"""
    new_column = parameters.get('new_column')
    formula = parameters.get('formula')
    
    if not new_column or not formula:
        raise DataCalculationError("calculate_column requires 'new_column' and 'formula' parameters")
    
    # Safe evaluation using pandas eval
    try:
        df[new_column] = df.eval(formula)
    except Exception as e:
        raise DataCalculationError(f"Formula evaluation failed: {str(e)}")
    
    return df


def _apply_formula(df: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    """Apply mathematical formula to column"""
    column = parameters.get('column')
    operation = parameters.get('operation')
    new_column = parameters.get('new_column', f'{column}_{operation}')
    
    if not column or not operation:
        raise DataCalculationError("apply_formula requires 'column' and 'operation' parameters")
    
    # Safe operations mapping
    SAFE_OPERATIONS = {
        'sqrt': np.sqrt,
        'log': np.log,
        'log10': np.log10,
        'exp': np.exp,
        'abs': np.abs,
        'square': lambda x: x**2,
        'cube': lambda x: x**3,
        'reciprocal': lambda x: 1/x
    }
    
    if operation not in SAFE_OPERATIONS:
        raise DataCalculationError(
            f"Unknown operation: {operation}. "
            f"Supported: {', '.join(SAFE_OPERATIONS.keys())}"
        )
    
    df[new_column] = SAFE_OPERATIONS[operation](df[column])
    
    return df


def _apply_conditional(df: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    """Apply conditional logic"""
    new_column = parameters.get('new_column')
    condition = parameters.get('condition')
    if_true = parameters.get('if_true')
    if_false = parameters.get('if_false')
    
    if not all([new_column, condition, if_true is not None, if_false is not None]):
        raise DataCalculationError("conditional requires new_column, condition, if_true, if_false")
    
    # Safe evaluation
    try:
        mask = df.eval(condition)
        df[new_column] = np.where(mask, if_true, if_false)
    except Exception as e:
        raise DataCalculationError(f"Condition evaluation failed: {str(e)}")
    
    return df


def _apply_lookup(df: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    """Perform VLOOKUP-style merge"""
    lookup_data = parameters.get('lookup_data')
    on = parameters.get('on')
    columns = parameters.get('columns')
    
    if not all([lookup_data, on]):
        raise DataCalculationError("lookup requires lookup_data and on parameters")
    
    # Convert lookup_data to DataFrame
    if isinstance(lookup_data, str):
        lookup_df = pd.read_csv(lookup_data)
    elif isinstance(lookup_data, dict):
        lookup_df = pd.DataFrame(lookup_data)
    else:
        lookup_df = lookup_data
    
    # Select columns if specified
    if columns:
        merge_columns = [on] + [c for c in columns if c != on]
        lookup_df = lookup_df[merge_columns]
    
    # Merge
    result = pd.merge(df, lookup_df, on=on, how='left')
    
    return result


def _calculate_percentage(df: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    """Calculate percentages"""
    column = parameters.get('column')
    new_column = parameters.get('new_column', f'{column}_pct')
    total_column = parameters.get('total_column')
    
    if not column:
        raise DataCalculationError("percentage requires 'column' parameter")
    
    if total_column:
        # Percentage of another column
        df[new_column] = (df[column] / df[total_column]) * 100
    else:
        # Percentage of total
        df[new_column] = (df[column] / df[column].sum()) * 100
    
    return df


def _calculate_ranking(df: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    """Calculate rankings"""
    column = parameters.get('column')
    method = parameters.get('method', 'dense')
    new_column = parameters.get('new_column', f'{column}_rank')
    ascending = parameters.get('ascending', False)
    
    if not column:
        raise DataCalculationError("ranking requires 'column' parameter")
    
    df[new_column] = df[column].rank(method=method, ascending=ascending)
    
    return df


def _execute_custom_code(df: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    """Execute custom pandas code with RestrictedPython"""
    code = parameters.get('code')
    
    if not code:
        raise DataCalculationError("custom template requires 'code' parameter")
    
    # Compile restricted code
    byte_code = compile_restricted(code, '<custom_calculation>', 'exec')
    
    # Safe execution environment
    safe_locals = {
        'df': df.copy(),
        'pd': pd,
        'np': np,
        'result': None
    }
    
    restricted_globals = {
        '__builtins__': {
            'True': True,
            'False': False,
            'None': None,
            'len': len,
            'range': range,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs
        }
    }
    
    try:
        exec(byte_code, restricted_globals, safe_locals)
        result_df = safe_locals.get('result', safe_locals['df'])
    except Exception as e:
        raise DataCalculationError(f"Custom code execution failed: {str(e)}")
    
    return result_df


# ============================================================================
# REGRESSION MODEL FUNCTIONS
# ============================================================================

def _build_linear_regression(df: pd.DataFrame, target: str, predictors: List[str], options: dict) -> dict:
    """Build linear regression model"""
    X = df[predictors]
    y = df[target]
    
    # Add constant for intercept
    X_with_const = sm.add_constant(X)
    
    # Fit model
    model = sm.OLS(y, X_with_const).fit()
    
    result = {
        'model': 'linear_regression',
        'r_squared': float(model.rsquared),
        'adj_r_squared': float(model.rsquared_adj),
        'f_statistic': float(model.fvalue),
        'f_pvalue': float(model.f_pvalue),
        'coefficients': {
            'intercept': float(model.params[0]),
            **{var: float(model.params[var]) for var in predictors}
        },
        'p_values': {
            'intercept': float(model.pvalues[0]),
            **{var: float(model.pvalues[var]) for var in predictors}
        },
        'std_errors': {
            'intercept': float(model.bse[0]),
            **{var: float(model.bse[var]) for var in predictors}
        }
    }
    
    if options.get('return_predictions', False):
        result['predictions'] = model.predict(X_with_const).tolist()
        result['residuals'] = model.resid.tolist()
    
    return result


def _build_logistic_regression(df: pd.DataFrame, target: str, predictors: List[str], options: dict) -> dict:
    """Build logistic regression model"""
    X = df[predictors]
    y = df[target]
    
    # Fit model
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    
    result = {
        'model': 'logistic_regression',
        'coefficients': {
            'intercept': float(model.intercept_[0]),
            **{var: float(coef) for var, coef in zip(predictors, model.coef_[0])}
        },
        'classes': model.classes_.tolist()
    }
    
    if options.get('return_predictions', False):
        result['predictions'] = model.predict(X).tolist()
        result['probabilities'] = model.predict_proba(X).tolist()
    
    return result


def _build_polynomial_regression(df: pd.DataFrame, target: str, predictors: List[str], options: dict) -> dict:
    """Build polynomial regression model"""
    degree = options.get('degree', 2)
    
    X = df[predictors]
    y = df[target]
    
    # Create polynomial features
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)
    
    # Fit model
    model = LinearRegression()
    model.fit(X_poly, y)
    
    # Calculate R-squared
    r_squared = model.score(X_poly, y)
    
    result = {
        'model': 'polynomial_regression',
        'degree': degree,
        'r_squared': float(r_squared),
        'coefficients': {
            'intercept': float(model.intercept_),
            'features': model.coef_.tolist()
        }
    }
    
    if options.get('return_predictions', False):
        result['predictions'] = model.predict(X_poly).tolist()
    
    return result


def _build_ridge_regression(df: pd.DataFrame, target: str, predictors: List[str], options: dict) -> dict:
    """Build ridge regression model"""
    alpha = options.get('alpha', 1.0)
    
    X = df[predictors]
    y = df[target]
    
    # Fit model
    model = Ridge(alpha=alpha)
    model.fit(X, y)
    
    result = {
        'model': 'ridge_regression',
        'alpha': alpha,
        'r_squared': float(model.score(X, y)),
        'coefficients': {
            'intercept': float(model.intercept_),
            **{var: float(coef) for var, coef in zip(predictors, model.coef_)}
        }
    }
    
    if options.get('return_predictions', False):
        result['predictions'] = model.predict(X).tolist()
    
    return result


def _build_lasso_regression(df: pd.DataFrame, target: str, predictors: List[str], options: dict) -> dict:
    """Build lasso regression model"""
    alpha = options.get('alpha', 1.0)
    
    X = df[predictors]
    y = df[target]
    
    # Fit model
    model = Lasso(alpha=alpha)
    model.fit(X, y)
    
    result = {
        'model': 'lasso_regression',
        'alpha': alpha,
        'r_squared': float(model.score(X, y)),
        'coefficients': {
            'intercept': float(model.intercept_),
            **{var: float(coef) for var, coef in zip(predictors, model.coef_)}
        },
        'selected_features': [var for var, coef in zip(predictors, model.coef_) if coef != 0]
    }
    
    if options.get('return_predictions', False):
        result['predictions'] = model.predict(X).tolist()
    
    return result


def _build_random_forest(df: pd.DataFrame, target: str, predictors: List[str], options: dict) -> dict:
    """Build random forest regression model"""
    n_estimators = options.get('n_estimators', 100)
    max_depth = options.get('max_depth', None)
    
    X = df[predictors]
    y = df[target]
    
    # Fit model
    model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    model.fit(X, y)
    
    result = {
        'model': 'random_forest_regression',
        'n_estimators': n_estimators,
        'max_depth': max_depth,
        'r_squared': float(model.score(X, y)),
        'feature_importances': {
            var: float(importance) for var, importance in zip(predictors, model.feature_importances_)
        }
    }
    
    if options.get('return_predictions', False):
        result['predictions'] = model.predict(X).tolist()
    
    return result


def _build_time_series_model(df: pd.DataFrame, target: str, options: dict) -> dict:
    """Build ARIMA time series model"""
    try:
        from statsmodels.tsa.arima.model import ARIMA
    except ImportError:
        raise DataCalculationError("Time series modeling requires statsmodels>=0.12.0")
    
    order = options.get('order', (1, 1, 1))
    forecast_steps = options.get('forecast_steps', 10)
    
    y = df[target]
    
    # Fit model
    model = ARIMA(y, order=order)
    fitted_model = model.fit()
    
    # Forecast
    forecast = fitted_model.forecast(steps=forecast_steps)
    
    result = {
        'model': 'arima',
        'order': order,
        'aic': float(fitted_model.aic),
        'bic': float(fitted_model.bic),
        'forecast': forecast.tolist()
    }
    
    if options.get('return_predictions', False):
        result['fitted_values'] = fitted_model.fittedvalues.tolist()
    
    return result

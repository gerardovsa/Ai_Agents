"""
Data Analysis Tools - Tier 1 (Predefined Safe Operations)

SECURITY: No arbitrary code execution - all operations are predefined
PERFORMANCE: 50-500ms execution time
MEMORY: 100-300 MB per operation

Tier 1 Tools:
1. data_analyze_statistics - Comprehensive statistical analysis
2. data_run_hypothesis_test - Statistical hypothesis testing
3. data_create_aggregation - Data aggregation and transformation

Dependencies: pandas, numpy, scipy, statsmodels, pingouin
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from typing import Dict, Any, List, Optional, Union
import json


class DataAnalysisError(Exception):
    """Custom exception for data analysis errors"""
    pass


def data_analyze_statistics(
    data_source: Union[str, dict],
    analysis_type: str,
    columns: Optional[List[str]] = None,
    options: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Comprehensive statistical analysis with multiple analysis types
    
    Args:
        data_source: CSV file path, JSON string, or dict
        analysis_type: Type of analysis to perform
            - 'summary': Descriptive statistics (mean, median, std, min, max, quartiles)
            - 'correlation': Correlation matrix (Pearson, Spearman, Kendall)
            - 'distribution': Distribution analysis (skewness, kurtosis, normality tests)
            - 'outliers': Outlier detection (Z-score, IQR method)
            - 'missing': Missing value analysis
            - 'variance': Variance analysis
        columns: Optional list of columns to analyze (None = all numeric columns)
        options: Optional parameters for specific analysis types
            - correlation: {'method': 'pearson|spearman|kendall', 'include_pvalues': True}
            - outliers: {'method': 'zscore|iqr', 'threshold': 3.0}
            - distribution: {'test_normality': True}
    
    Returns:
        Dict with analysis results and metadata
    
    Execution Time: 50-200ms
    
    Examples:
        # Summary statistics
        data_analyze_statistics('sales.csv', 'summary')
        
        # Correlation with p-values
        data_analyze_statistics('data.csv', 'correlation', 
                               options={'method': 'pearson', 'include_pvalues': True})
        
        # Outlier detection using IQR
        data_analyze_statistics('data.csv', 'outliers',
                               options={'method': 'iqr'})
    """
    # Load data
    df = _load_data(data_source)
    
    # Select columns
    if columns:
        df = df[columns]
    
    # Default options
    if options is None:
        options = {}
    
    # Route to appropriate analysis
    if analysis_type == 'summary':
        result = _analyze_summary(df, options)
    elif analysis_type == 'correlation':
        result = _analyze_correlation(df, options)
    elif analysis_type == 'distribution':
        result = _analyze_distribution(df, options)
    elif analysis_type == 'outliers':
        result = _detect_outliers(df, options)
    elif analysis_type == 'missing':
        result = _analyze_missing(df, options)
    elif analysis_type == 'variance':
        result = _analyze_variance(df, options)
    else:
        raise DataAnalysisError(
            f"Unknown analysis_type: {analysis_type}. "
            f"Supported: summary, correlation, distribution, outliers, missing, variance"
        )
    
    return {
        'success': True,
        'analysis_type': analysis_type,
        'result': result,
        'metadata': {
            'rows': len(df),
            'columns': list(df.columns),
            'numeric_columns': list(df.select_dtypes(include=[np.number]).columns)
        }
    }


def data_run_hypothesis_test(
    data_source: Union[str, dict],
    test_type: str,
    groups: Optional[List[str]] = None,
    variables: Optional[List[str]] = None,
    options: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Statistical hypothesis testing with multiple test types
    
    Args:
        data_source: CSV file path, JSON string, or dict
        test_type: Type of hypothesis test
            - 't_test': Independent or paired t-test
            - 'anova': One-way or two-way ANOVA
            - 'chi_square': Chi-square test of independence
            - 'mann_whitney': Mann-Whitney U test (non-parametric t-test)
            - 'kruskal': Kruskal-Wallis H test (non-parametric ANOVA)
            - 'wilcoxon': Wilcoxon signed-rank test (paired non-parametric)
            - 'f_test': F-test for equality of variances
        groups: Column names for grouping variables
        variables: Column names for dependent variables
        options: Test-specific options
            - t_test: {'paired': False, 'equal_var': True, 'alternative': 'two-sided'}
            - anova: {'type': 'one-way', 'post_hoc': 'tukey'}
            - chi_square: {'correction': True}
    
    Returns:
        Dict with test results (statistic, p-value, interpretation)
    
    Execution Time: 50-300ms
    
    Examples:
        # Independent t-test comparing two groups
        data_run_hypothesis_test('data.csv', 't_test',
                                groups=['Group'],
                                variables=['Score'])
        
        # One-way ANOVA with post-hoc
        data_run_hypothesis_test('data.csv', 'anova',
                                groups=['Treatment'],
                                variables=['Response'],
                                options={'post_hoc': 'tukey'})
    """
    # Load data
    df = _load_data(data_source)
    
    # Default options
    if options is None:
        options = {}
    
    # Route to appropriate test
    if test_type == 't_test':
        result = _run_t_test(df, groups, variables, options)
    elif test_type == 'anova':
        result = _run_anova(df, groups, variables, options)
    elif test_type == 'chi_square':
        result = _run_chi_square(df, groups, variables, options)
    elif test_type == 'mann_whitney':
        result = _run_mann_whitney(df, groups, variables, options)
    elif test_type == 'kruskal':
        result = _run_kruskal(df, groups, variables, options)
    elif test_type == 'wilcoxon':
        result = _run_wilcoxon(df, groups, variables, options)
    elif test_type == 'f_test':
        result = _run_f_test(df, groups, variables, options)
    else:
        raise DataAnalysisError(
            f"Unknown test_type: {test_type}. "
            f"Supported: t_test, anova, chi_square, mann_whitney, kruskal, wilcoxon, f_test"
        )
    
    return {
        'success': True,
        'test_type': test_type,
        'result': result,
        'metadata': {
            'rows': len(df),
            'groups': groups,
            'variables': variables
        }
    }


def data_create_aggregation(
    data_source: Union[str, dict],
    aggregation_type: str,
    group_by: Optional[List[str]] = None,
    aggregations: Optional[Dict[str, Union[str, List[str]]]] = None,
    options: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Data aggregation and transformation
    
    Args:
        data_source: CSV file path, JSON string, or dict
        aggregation_type: Type of aggregation
            - 'pivot': Pivot table with multi-level aggregations
            - 'groupby': Group by with custom aggregations
            - 'rolling': Moving averages, rolling sums, etc.
            - 'cumulative': Cumulative sums, products, etc.
            - 'resample': Time series resampling
            - 'crosstab': Cross-tabulation analysis
        group_by: Columns to group by
        aggregations: Dict mapping columns to aggregation functions
            - {'Sales': 'sum', 'Quantity': ['mean', 'max']}
        options: Aggregation-specific options
            - rolling: {'window': 7, 'min_periods': 1}
            - resample: {'freq': 'D', 'method': 'sum'}
            - pivot: {'values': 'Sales', 'index': 'Product', 'columns': 'Region'}
    
    Returns:
        Dict with aggregated data
    
    Execution Time: 50-500ms
    
    Examples:
        # Group by with multiple aggregations
        data_create_aggregation('sales.csv', 'groupby',
                               group_by=['Product', 'Region'],
                               aggregations={'Sales': 'sum', 'Quantity': 'mean'})
        
        # 7-day rolling average
        data_create_aggregation('timeseries.csv', 'rolling',
                               aggregations={'Sales': 'mean'},
                               options={'window': 7})
        
        # Pivot table
        data_create_aggregation('data.csv', 'pivot',
                               options={'values': 'Sales', 
                                       'index': 'Product',
                                       'columns': 'Region',
                                       'aggfunc': 'sum'})
    """
    # Load data
    df = _load_data(data_source)
    
    # Default options
    if options is None:
        options = {}
    
    # Route to appropriate aggregation
    if aggregation_type == 'pivot':
        result = _create_pivot(df, group_by, aggregations, options)
    elif aggregation_type == 'groupby':
        result = _create_groupby(df, group_by, aggregations, options)
    elif aggregation_type == 'rolling':
        result = _create_rolling(df, aggregations, options)
    elif aggregation_type == 'cumulative':
        result = _create_cumulative(df, aggregations, options)
    elif aggregation_type == 'resample':
        result = _create_resample(df, aggregations, options)
    elif aggregation_type == 'crosstab':
        result = _create_crosstab(df, group_by, options)
    else:
        raise DataAnalysisError(
            f"Unknown aggregation_type: {aggregation_type}. "
            f"Supported: pivot, groupby, rolling, cumulative, resample, crosstab"
        )
    
    return {
        'success': True,
        'aggregation_type': aggregation_type,
        'result': result,
        'metadata': {
            'original_rows': len(df),
            'result_rows': len(result) if isinstance(result, (pd.DataFrame, list)) else None
        }
    }


# ============================================================================
# HELPER FUNCTIONS - Data Loading
# ============================================================================

def _load_data(data_source: Union[str, dict]) -> pd.DataFrame:
    """Load data from various sources"""
    if isinstance(data_source, str):
        if data_source.endswith('.csv'):
            return pd.read_csv(data_source)
        else:
            # Try as JSON string
            try:
                data = json.loads(data_source)
                return pd.DataFrame(data)
            except:
                raise DataAnalysisError(f"Could not load data from: {data_source}")
    elif isinstance(data_source, dict):
        return pd.DataFrame(data_source)
    elif isinstance(data_source, pd.DataFrame):
        return data_source
    else:
        raise DataAnalysisError(f"Unsupported data_source type: {type(data_source)}")


# ============================================================================
# ANALYSIS FUNCTIONS - Summary Statistics
# ============================================================================

def _analyze_summary(df: pd.DataFrame, options: dict) -> dict:
    """Calculate summary statistics"""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        raise DataAnalysisError("No numeric columns found for summary statistics")
    
    summary = numeric_df.describe()
    
    return {
        'statistics': summary.to_dict(),
        'column_count': len(numeric_df.columns),
        'row_count': len(df)
    }


def _analyze_correlation(df: pd.DataFrame, options: dict) -> dict:
    """Calculate correlation matrix"""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        raise DataAnalysisError("No numeric columns found for correlation")
    
    method = options.get('method', 'pearson')
    include_pvalues = options.get('include_pvalues', False)
    
    corr_matrix = numeric_df.corr(method=method)
    
    result = {
        'correlation_matrix': corr_matrix.to_dict(),
        'method': method
    }
    
    if include_pvalues:
        # Calculate p-values
        pvalues = pd.DataFrame(np.zeros_like(corr_matrix), 
                              columns=corr_matrix.columns,
                              index=corr_matrix.index)
        
        for col1 in numeric_df.columns:
            for col2 in numeric_df.columns:
                if col1 != col2:
                    if method == 'pearson':
                        _, p = stats.pearsonr(numeric_df[col1], numeric_df[col2])
                    elif method == 'spearman':
                        _, p = stats.spearmanr(numeric_df[col1], numeric_df[col2])
                    else:
                        _, p = stats.kendalltau(numeric_df[col1], numeric_df[col2])
                    pvalues.loc[col1, col2] = p
        
        result['p_values'] = pvalues.to_dict()
    
    return result


def _analyze_distribution(df: pd.DataFrame, options: dict) -> dict:
    """Analyze distribution of numeric columns"""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        raise DataAnalysisError("No numeric columns found for distribution analysis")
    
    result = {}
    
    for col in numeric_df.columns:
        col_stats = {
            'skewness': float(numeric_df[col].skew()),
            'kurtosis': float(numeric_df[col].kurtosis())
        }
        
        if options.get('test_normality', False):
            # Shapiro-Wilk test for normality
            stat, p_value = stats.shapiro(numeric_df[col].dropna())
            col_stats['normality_test'] = {
                'statistic': float(stat),
                'p_value': float(p_value),
                'is_normal': p_value > 0.05
            }
        
        result[col] = col_stats
    
    return result


def _detect_outliers(df: pd.DataFrame, options: dict) -> dict:
    """Detect outliers using Z-score or IQR method"""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        raise DataAnalysisError("No numeric columns found for outlier detection")
    
    method = options.get('method', 'zscore')
    threshold = options.get('threshold', 3.0)
    
    result = {}
    
    for col in numeric_df.columns:
        if method == 'zscore':
            z_scores = np.abs(stats.zscore(numeric_df[col].dropna()))
            outliers = (z_scores > threshold).sum()
        else:  # IQR method
            Q1 = numeric_df[col].quantile(0.25)
            Q3 = numeric_df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = ((numeric_df[col] < lower_bound) | (numeric_df[col] > upper_bound)).sum()
        
        result[col] = {
            'outlier_count': int(outliers),
            'outlier_percentage': float(outliers / len(numeric_df) * 100),
            'method': method
        }
    
    return result


def _analyze_missing(df: pd.DataFrame, options: dict) -> dict:
    """Analyze missing values"""
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df) * 100)
    
    result = {
        'missing_counts': missing_count.to_dict(),
        'missing_percentages': missing_pct.to_dict(),
        'total_missing': int(df.isnull().sum().sum()),
        'columns_with_missing': list(missing_count[missing_count > 0].index)
    }
    
    return result


def _analyze_variance(df: pd.DataFrame, options: dict) -> dict:
    """Calculate variance statistics"""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        raise DataAnalysisError("No numeric columns found for variance analysis")
    
    result = {}
    
    for col in numeric_df.columns:
        result[col] = {
            'variance': float(numeric_df[col].var()),
            'std_dev': float(numeric_df[col].std()),
            'coefficient_of_variation': float(numeric_df[col].std() / numeric_df[col].mean() if numeric_df[col].mean() != 0 else 0)
        }
    
    return result


# ============================================================================
# HYPOTHESIS TESTING FUNCTIONS
# ============================================================================

def _run_t_test(df: pd.DataFrame, groups: List[str], variables: List[str], options: dict) -> dict:
    """Perform t-test"""
    if not groups or not variables:
        raise DataAnalysisError("t_test requires groups and variables")
    
    group_col = groups[0]
    var_col = variables[0]
    
    unique_groups = df[group_col].unique()
    
    if len(unique_groups) != 2:
        raise DataAnalysisError(f"t_test requires exactly 2 groups, found {len(unique_groups)}")
    
    group1_data = df[df[group_col] == unique_groups[0]][var_col]
    group2_data = df[df[group_col] == unique_groups[1]][var_col]
    
    equal_var = options.get('equal_var', True)
    alternative = options.get('alternative', 'two-sided')
    
    statistic, p_value = stats.ttest_ind(group1_data, group2_data, equal_var=equal_var, alternative=alternative)
    
    return {
        'test': 't_test',
        'statistic': float(statistic),
        'p_value': float(p_value),
        'significant': p_value < 0.05,
        'groups': list(unique_groups),
        'group_means': {
            str(unique_groups[0]): float(group1_data.mean()),
            str(unique_groups[1]): float(group2_data.mean())
        }
    }


def _run_anova(df: pd.DataFrame, groups: List[str], variables: List[str], options: dict) -> dict:
    """Perform ANOVA"""
    if not groups or not variables:
        raise DataAnalysisError("anova requires groups and variables")
    
    group_col = groups[0]
    var_col = variables[0]
    
    group_data = [df[df[group_col] == group][var_col].values for group in df[group_col].unique()]
    
    statistic, p_value = stats.f_oneway(*group_data)
    
    result = {
        'test': 'anova',
        'f_statistic': float(statistic),
        'p_value': float(p_value),
        'significant': p_value < 0.05,
        'groups': list(df[group_col].unique())
    }
    
    return result


def _run_chi_square(df: pd.DataFrame, groups: List[str], variables: List[str], options: dict) -> dict:
    """Perform chi-square test"""
    if not groups or len(groups) < 2:
        raise DataAnalysisError("chi_square requires at least 2 categorical variables")
    
    contingency_table = pd.crosstab(df[groups[0]], df[groups[1]])
    
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    
    return {
        'test': 'chi_square',
        'chi2_statistic': float(chi2),
        'p_value': float(p_value),
        'degrees_of_freedom': int(dof),
        'significant': p_value < 0.05
    }


def _run_mann_whitney(df: pd.DataFrame, groups: List[str], variables: List[str], options: dict) -> dict:
    """Perform Mann-Whitney U test"""
    if not groups or not variables:
        raise DataAnalysisError("mann_whitney requires groups and variables")
    
    group_col = groups[0]
    var_col = variables[0]
    
    unique_groups = df[group_col].unique()
    
    if len(unique_groups) != 2:
        raise DataAnalysisError(f"mann_whitney requires exactly 2 groups, found {len(unique_groups)}")
    
    group1_data = df[df[group_col] == unique_groups[0]][var_col]
    group2_data = df[df[group_col] == unique_groups[1]][var_col]
    
    statistic, p_value = stats.mannwhitneyu(group1_data, group2_data)
    
    return {
        'test': 'mann_whitney',
        'u_statistic': float(statistic),
        'p_value': float(p_value),
        'significant': p_value < 0.05
    }


def _run_kruskal(df: pd.DataFrame, groups: List[str], variables: List[str], options: dict) -> dict:
    """Perform Kruskal-Wallis H test"""
    if not groups or not variables:
        raise DataAnalysisError("kruskal requires groups and variables")
    
    group_col = groups[0]
    var_col = variables[0]
    
    group_data = [df[df[group_col] == group][var_col].values for group in df[group_col].unique()]
    
    statistic, p_value = stats.kruskal(*group_data)
    
    return {
        'test': 'kruskal',
        'h_statistic': float(statistic),
        'p_value': float(p_value),
        'significant': p_value < 0.05
    }


def _run_wilcoxon(df: pd.DataFrame, groups: List[str], variables: List[str], options: dict) -> dict:
    """Perform Wilcoxon signed-rank test"""
    if not variables or len(variables) < 2:
        raise DataAnalysisError("wilcoxon requires 2 paired variables")
    
    var1 = df[variables[0]]
    var2 = df[variables[1]]
    
    statistic, p_value = stats.wilcoxon(var1, var2)
    
    return {
        'test': 'wilcoxon',
        'statistic': float(statistic),
        'p_value': float(p_value),
        'significant': p_value < 0.05
    }


def _run_f_test(df: pd.DataFrame, groups: List[str], variables: List[str], options: dict) -> dict:
    """Perform F-test for equality of variances"""
    if not groups or not variables:
        raise DataAnalysisError("f_test requires groups and variables")
    
    group_col = groups[0]
    var_col = variables[0]
    
    unique_groups = df[group_col].unique()
    
    if len(unique_groups) != 2:
        raise DataAnalysisError(f"f_test requires exactly 2 groups, found {len(unique_groups)}")
    
    group1_data = df[df[group_col] == unique_groups[0]][var_col]
    group2_data = df[df[group_col] == unique_groups[1]][var_col]
    
    var1 = group1_data.var()
    var2 = group2_data.var()
    
    f_statistic = var1 / var2 if var1 > var2 else var2 / var1
    df1 = len(group1_data) - 1
    df2 = len(group2_data) - 1
    
    p_value = 1 - stats.f.cdf(f_statistic, df1, df2)
    
    return {
        'test': 'f_test',
        'f_statistic': float(f_statistic),
        'p_value': float(p_value * 2),  # Two-tailed
        'significant': (p_value * 2) < 0.05,
        'variances': {
            str(unique_groups[0]): float(var1),
            str(unique_groups[1]): float(var2)
        }
    }


# ============================================================================
# AGGREGATION FUNCTIONS
# ============================================================================

def _create_pivot(df: pd.DataFrame, group_by: List[str], aggregations: dict, options: dict) -> dict:
    """Create pivot table"""
    values = options.get('values')
    index = options.get('index')
    columns = options.get('columns')
    aggfunc = options.get('aggfunc', 'sum')
    
    if not all([values, index, columns]):
        raise DataAnalysisError("pivot requires values, index, and columns in options")
    
    pivot = pd.pivot_table(df, values=values, index=index, columns=columns, aggfunc=aggfunc)
    
    return pivot.to_dict()


def _create_groupby(df: pd.DataFrame, group_by: List[str], aggregations: dict, options: dict) -> dict:
    """Create group by aggregation"""
    if not group_by:
        raise DataAnalysisError("groupby requires group_by columns")
    
    if not aggregations:
        aggregations = {col: 'sum' for col in df.select_dtypes(include=[np.number]).columns}
    
    grouped = df.groupby(group_by).agg(aggregations)
    
    return grouped.reset_index().to_dict(orient='records')


def _create_rolling(df: pd.DataFrame, aggregations: dict, options: dict) -> dict:
    """Create rolling window aggregation"""
    window = options.get('window', 7)
    min_periods = options.get('min_periods', 1)
    
    if not aggregations:
        raise DataAnalysisError("rolling requires aggregations")
    
    result_df = df.copy()
    
    for col, agg_func in aggregations.items():
        result_df[f'{col}_rolling_{agg_func}'] = df[col].rolling(window=window, min_periods=min_periods).agg(agg_func)
    
    return result_df.to_dict(orient='records')


def _create_cumulative(df: pd.DataFrame, aggregations: dict, options: dict) -> dict:
    """Create cumulative aggregation"""
    if not aggregations:
        raise DataAnalysisError("cumulative requires aggregations")
    
    result_df = df.copy()
    
    for col, agg_func in aggregations.items():
        if agg_func == 'sum':
            result_df[f'{col}_cumsum'] = df[col].cumsum()
        elif agg_func == 'product':
            result_df[f'{col}_cumprod'] = df[col].cumprod()
        elif agg_func == 'max':
            result_df[f'{col}_cummax'] = df[col].cummax()
        elif agg_func == 'min':
            result_df[f'{col}_cummin'] = df[col].cummin()
    
    return result_df.to_dict(orient='records')


def _create_resample(df: pd.DataFrame, aggregations: dict, options: dict) -> dict:
    """Create time series resampling"""
    freq = options.get('freq', 'D')
    
    if 'date' not in df.columns and 'Date' not in df.columns:
        raise DataAnalysisError("resample requires a 'date' or 'Date' column")
    
    date_col = 'date' if 'date' in df.columns else 'Date'
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    
    if not aggregations:
        aggregations = {col: 'sum' for col in df.select_dtypes(include=[np.number]).columns}
    
    resampled = df.resample(freq).agg(aggregations)
    
    return resampled.reset_index().to_dict(orient='records')


def _create_crosstab(df: pd.DataFrame, group_by: List[str], options: dict) -> dict:
    """Create cross-tabulation"""
    if not group_by or len(group_by) < 2:
        raise DataAnalysisError("crosstab requires at least 2 columns in group_by")
    
    crosstab = pd.crosstab(df[group_by[0]], df[group_by[1]], normalize=options.get('normalize', False))
    
    return crosstab.to_dict()

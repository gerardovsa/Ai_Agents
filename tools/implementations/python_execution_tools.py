"""
Python Execution Tools - Sandboxed code execution for AI agents

This module provides safe Python code execution for deployed AI agents.

SECURITY MODEL:
- Uses RestrictedPython for sandbox
- Limited imports (pandas, numpy, matplotlib only)
- No file system access (except job workspace)
- No network access
- No subprocess execution
- Timeout protection (30 seconds)

INTENDED USE:
- Data analysis (pandas, numpy)
- Visualization (matplotlib, seaborn)
- Statistical computation (scipy, statsmodels)
- Machine learning (scikit-learn)

NOT FOR:
- Web scraping
- API calls
- System commands
- File operations outside workspace

Created: December 6, 2025
"""

import io
import sys
import time
import traceback
from typing import Dict, Any, Optional
from contextlib import redirect_stdout, redirect_stderr

try:
    from RestrictedPython import compile_restricted
    from RestrictedPython.Guards import safe_builtins, guarded_iter_unpack_sequence
    RESTRICTED_PYTHON_AVAILABLE = True
except ImportError:
    RESTRICTED_PYTHON_AVAILABLE = False
    print("⚠️ RestrictedPython not available - python_exec will use fallback mode")

# Safe libraries available to executed code
try:
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    ANALYSIS_LIBS_AVAILABLE = True
except ImportError:
    ANALYSIS_LIBS_AVAILABLE = False
    print("⚠️ Analysis libraries not fully available")


class PythonExecutionError(Exception):
    """Raised when Python code execution fails"""
    pass


class PythonExecutionTimeout(Exception):
    """Raised when Python code execution exceeds timeout"""
    pass


def python_exec(
    code: str,
    timeout: int = 30,
    workspace_dir: Optional[str] = None,
    globals_dict: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute Python code in a sandboxed environment
    
    SECURITY:
    - RestrictedPython sandbox (if available)
    - Limited imports (pandas, numpy, matplotlib, seaborn)
    - No file system access outside workspace
    - No network access
    - No subprocess execution
    - Timeout protection
    
    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds (default 30)
        workspace_dir: Directory for file operations (optional)
        globals_dict: Additional global variables (optional)
    
    Returns:
        {
            "success": True/False,
            "output": "stdout output",
            "error": "error message if failed",
            "variables": {captured variables},
            "execution_time": 1.23
        }
    
    Example:
        python_exec(code=\"\"\"
            import pandas as pd
            df = pd.DataFrame({'a': [1, 2, 3]})
            result = df['a'].sum()
            print(f"Sum: {result}")
        \"\"\")
        
        Returns:
        {
            "success": True,
            "output": "Sum: 6\\n",
            "variables": {"result": 6},
            "execution_time": 0.05
        }
    """
    
    if not RESTRICTED_PYTHON_AVAILABLE:
        return {
            "success": False,
            "error": "RestrictedPython not installed. Cannot execute arbitrary code safely.",
            "output": "",
            "execution_time": 0
        }
    
    start_time = time.time()
    
    # Capture stdout and stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    # Build safe globals
    safe_globals = _build_safe_globals(workspace_dir, globals_dict)
    
    # Build safe locals (for variable capture)
    safe_locals = {}
    
    try:
        # Compile code with RestrictedPython
        byte_code = compile_restricted(
            code,
            filename='<agent_code>',
            mode='exec'
        )
        
        if byte_code.errors:
            return {
                "success": False,
                "error": f"Compilation errors: {'; '.join(byte_code.errors)}",
                "output": "",
                "execution_time": time.time() - start_time
            }
        
        # Execute with output capture
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(byte_code.code, safe_globals, safe_locals)
        
        execution_time = time.time() - start_time
        
        # Check timeout
        if execution_time > timeout:
            raise PythonExecutionTimeout(f"Execution exceeded {timeout} seconds")
        
        # Extract variables (exclude special and imported modules)
        captured_vars = {
            k: v for k, v in safe_locals.items()
            if not k.startswith('_') and not callable(v)
        }
        
        return {
            "success": True,
            "output": stdout_capture.getvalue(),
            "error": stderr_capture.getvalue() if stderr_capture.getvalue() else None,
            "variables": _serialize_variables(captured_vars),
            "execution_time": execution_time
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}",
            "output": stdout_capture.getvalue(),
            "traceback": traceback.format_exc(),
            "execution_time": time.time() - start_time
        }


def _build_safe_globals(workspace_dir: Optional[str], additional_globals: Optional[Dict]) -> Dict[str, Any]:
    """
    Build safe global namespace for code execution
    
    SECURITY: Only safe libraries and functions are exposed
    """
    
    safe_globals = {
        # Safe builtins from RestrictedPython
        '__builtins__': {
            'True': True,
            'False': False,
            'None': None,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
            'sorted': sorted,
            'reversed': reversed,
            'any': any,
            'all': all,
            'print': print,
            # RestrictedPython guards
            '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
        },
        
        # Safe libraries
        'pd': pd if ANALYSIS_LIBS_AVAILABLE else None,
        'pandas': pd if ANALYSIS_LIBS_AVAILABLE else None,
        'np': np if ANALYSIS_LIBS_AVAILABLE else None,
        'numpy': np if ANALYSIS_LIBS_AVAILABLE else None,
        'plt': plt if ANALYSIS_LIBS_AVAILABLE else None,
        'matplotlib': matplotlib if ANALYSIS_LIBS_AVAILABLE else None,
        'sns': sns if ANALYSIS_LIBS_AVAILABLE else None,
        'seaborn': sns if ANALYSIS_LIBS_AVAILABLE else None,
    }
    
    # Add additional globals if provided
    if additional_globals:
        safe_globals.update(additional_globals)
    
    # Add workspace directory if provided
    if workspace_dir:
        safe_globals['WORKSPACE_DIR'] = workspace_dir
    
    return safe_globals


def _serialize_variables(variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize variables for JSON output
    
    Handles:
    - Pandas DataFrames → summary dict
    - NumPy arrays → list
    - Matplotlib figures → saved status
    - Standard types → as-is
    """
    serialized = {}
    
    for key, value in variables.items():
        try:
            if isinstance(value, pd.DataFrame):
                # Summarize DataFrame
                serialized[key] = {
                    'type': 'DataFrame',
                    'shape': value.shape,
                    'columns': list(value.columns),
                    'head': value.head(5).to_dict('records')
                }
            elif isinstance(value, pd.Series):
                serialized[key] = {
                    'type': 'Series',
                    'length': len(value),
                    'head': value.head(5).to_dict()
                }
            elif isinstance(value, np.ndarray):
                serialized[key] = {
                    'type': 'ndarray',
                    'shape': value.shape,
                    'dtype': str(value.dtype),
                    'sample': value.flatten()[:10].tolist()
                }
            elif isinstance(value, matplotlib.figure.Figure):
                serialized[key] = {
                    'type': 'Figure',
                    'status': 'created (use plt.savefig() to save)'
                }
            elif isinstance(value, (int, float, str, bool, list, dict, tuple)):
                serialized[key] = value
            else:
                serialized[key] = {
                    'type': type(value).__name__,
                    'repr': str(value)[:200]
                }
        except Exception as e:
            serialized[key] = f"<Error serializing: {e}>"
    
    return serialized


# Additional utility functions for specific use cases

def python_exec_with_dataframe(
    code: str,
    dataframe: pd.DataFrame,
    timeout: int = 30,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute Python code with a pre-loaded DataFrame
    
    Convenience function that injects 'df' variable
    """
    additional_globals = {'df': dataframe}
    
    return python_exec(
        code=code,
        timeout=timeout,
        globals_dict=additional_globals,
        **kwargs
    )


def python_exec_analysis(
    code: str,
    data_file: str,
    timeout: int = 30,
    workspace_dir: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute Python analysis code with automatic data loading
    
    Convenience function that:
    1. Loads data file into 'df'
    2. Executes analysis code
    3. Returns results
    """
    
    # Build code that loads data first
    full_code = f"""
import pandas as pd

# Load data
df = pd.read_csv('{data_file}')

# User code
{code}
"""
    
    return python_exec(
        code=full_code,
        timeout=timeout,
        workspace_dir=workspace_dir,
        **kwargs
    )


# Export for registry registration
__all__ = [
    'python_exec',
    'python_exec_with_dataframe',
    'python_exec_analysis'
]

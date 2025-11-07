"""
Data Analysis Tools - Tier 3 (Docker Sandbox for Advanced Analysis)

SECURITY: Complete isolation via Docker container
PERFORMANCE: 5-60 seconds execution time (container overhead)
MEMORY: 1-1.5 GB per container

Tier 3 Tools:
1. data_execute_advanced_analysis - Execute arbitrary Python code in Docker sandbox

Dependencies: docker, pandas, numpy, scipy, statsmodels, scikit-learn
"""

import docker
import tempfile
import os
import json
import uuid
from typing import Dict, Any, Optional, Union
import pandas as pd
from pathlib import Path
import time


class AdvancedAnalysisError(Exception):
    """Custom exception for advanced analysis errors"""
    pass


# Container pool for performance optimization
_container_pool = []
_max_pool_size = 4
_docker_client = None


def _initialize_docker():
    """Initialize Docker client and container pool"""
    global _docker_client, _container_pool
    
    if _docker_client is not None:
        return
    
    try:
        _docker_client = docker.from_env()
        print("Docker client initialized successfully")
        
        # Pre-warm container pool (optional - improves performance)
        # Uncomment to enable:
        # _prewarm_containers()
        
    except docker.errors.DockerException as e:
        print(f"Warning: Docker not available: {e}")
        print("Tier 3 tools (data_execute_advanced_analysis) will not be available")
        _docker_client = None


def _prewarm_containers():
    """Pre-create containers for faster execution (optional)"""
    global _container_pool
    
    print("Pre-warming Docker containers...")
    
    for i in range(_max_pool_size):
        try:
            container = _docker_client.containers.run(
                'python:3.11-slim',
                command='sleep infinity',
                detach=True,
                mem_limit='1g',
                cpu_period=100000,
                cpu_quota=50000,  # 50% CPU limit
                network_mode='none',  # No network access
                remove=False,
                name=f'data_analysis_worker_{i}_{uuid.uuid4().hex[:8]}'
            )
            
            # Install Python packages
            print(f"Installing packages in container {i}...")
            exec_result = container.exec_run(
                'pip install --no-cache-dir pandas numpy scipy statsmodels scikit-learn'
            )
            
            if exec_result.exit_code == 0:
                _container_pool.append(container)
                print(f"Container {i} ready")
            else:
                print(f"Container {i} package installation failed")
                container.stop()
                container.remove()
                
        except Exception as e:
            print(f"Could not create container {i}: {e}")
    
    print(f"Container pool initialized with {len(_container_pool)} containers")


def _get_container():
    """Get container from pool or create new one"""
    global _container_pool
    
    if _container_pool:
        return _container_pool.pop(), True  # (container, from_pool)
    else:
        # Create temporary container
        container = _docker_client.containers.run(
            'python:3.11-slim',
            command='sleep infinity',
            detach=True,
            mem_limit='1g',
            cpu_period=100000,
            cpu_quota=50000,
            network_mode='none',
            remove=False
        )
        
        # Install packages
        container.exec_run(
            'pip install --no-cache-dir pandas numpy scipy statsmodels scikit-learn'
        )
        
        return container, False


def _return_container(container, from_pool: bool):
    """Return container to pool or destroy it"""
    global _container_pool
    
    if from_pool and len(_container_pool) < _max_pool_size:
        # Clean up container
        try:
            container.exec_run('rm -rf /tmp/*')
            _container_pool.append(container)
        except:
            container.stop()
            container.remove()
    else:
        # Destroy container
        try:
            container.stop()
            container.remove()
        except:
            pass


def data_execute_advanced_analysis(
    data_source: Union[str, dict],
    analysis_code: str,
    timeout: int = 60,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute arbitrary Python code in secure Docker sandbox
    
    EXECUTION TIME: 5-60 seconds (includes container initialization)
    
    This tool provides MAXIMUM flexibility for advanced data analysis by executing
    custom Python code in a completely isolated Docker container. Use when predefined
    tools (Tier 1 and Tier 2) cannot fulfill the analysis requirements.
    
    IMPORTANT: AI must inform user before execution:
    "Running advanced analysis in secure sandbox environment. This will take 
    approximately 20-30 seconds for container initialization and execution..."
    
    Args:
        data_source: CSV file path, JSON string, or dict
        analysis_code: Python code to execute
            - Must use 'df' variable for input DataFrame
            - Must set 'result' variable with output
            - Available libraries: pandas, numpy, scipy, statsmodels, scikit-learn
        timeout: Maximum execution time in seconds
            - Default: 60 seconds
            - Maximum: 300 seconds (5 minutes)
            - Adjust based on data size and complexity
    
    Security Features:
        - Complete filesystem isolation
        - No network access
        - Memory limited to 1 GB
        - CPU limited to 50%
        - Automatic timeout enforcement
        - Automatic cleanup
    
    Returns:
        Dict with analysis results and execution metadata
    
    Examples:
        # Custom statistical analysis
        data_execute_advanced_analysis(
            data_source='sales.csv',
            analysis_code='''
# Calculate custom metrics
df['Profit'] = df['Revenue'] - df['Cost']
df['ROI'] = (df['Profit'] / df['Cost']) * 100

# Advanced grouping
summary = df.groupby('Product').agg({
    'Profit': ['sum', 'mean', 'std'],
    'ROI': 'mean'
})

result = summary.to_dict()
            ''',
            timeout=60
        )
        
        # Machine learning pipeline
        data_execute_advanced_analysis(
            data_source='training_data.csv',
            analysis_code='''
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Prepare data
X = df[['Feature1', 'Feature2', 'Feature3']]
y = df['Target']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

result = {
    'accuracy': accuracy,
    'feature_importances': dict(zip(X.columns, model.feature_importances_))
}
            ''',
            timeout=120
        )
        
        # Time series forecasting
        data_execute_advanced_analysis(
            data_source='timeseries.csv',
            analysis_code='''
from statsmodels.tsa.arima.model import ARIMA

# Prepare time series
ts = df['Sales']

# Fit ARIMA model
model = ARIMA(ts, order=(1,1,1))
fitted = model.fit()

# Forecast next 10 periods
forecast = fitted.forecast(steps=10)

result = {
    'forecast': forecast.tolist(),
    'aic': fitted.aic,
    'bic': fitted.bic
}
            '''
        )
    """
    # Initialize Docker if not already done
    if _docker_client is None:
        _initialize_docker()
    
    if _docker_client is None:
        raise AdvancedAnalysisError(
            "Docker not available. Tier 3 analysis requires Docker installation. "
            "Please install Docker or use Tier 1/2 tools for predefined analyses."
        )
    
    # Validate timeout
    if timeout > 300:
        timeout = 300  # Max 5 minutes
    elif timeout < 5:
        timeout = 5  # Min 5 seconds
    
    # Create unique analysis ID
    analysis_id = str(uuid.uuid4())
    
    # Start timing
    start_time = time.time()
    
    # Get container
    try:
        container, from_pool = _get_container()
    except Exception as e:
        raise AdvancedAnalysisError(f"Failed to create Docker container: {str(e)}")
    
    container_init_time = time.time() - start_time
    
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Prepare data file
            data_file = tmpdir_path / f'{analysis_id}_data.csv'
            
            if isinstance(data_source, str):
                if data_source.endswith('.csv') and os.path.exists(data_source):
                    import shutil
                    shutil.copy(data_source, data_file)
                else:
                    # Try as JSON
                    try:
                        data = json.loads(data_source)
                        pd.DataFrame(data).to_csv(data_file, index=False)
                    except:
                        raise AdvancedAnalysisError(f"Could not load data from: {data_source}")
            elif isinstance(data_source, dict):
                pd.DataFrame(data_source).to_csv(data_file, index=False)
            elif isinstance(data_source, pd.DataFrame):
                data_source.to_csv(data_file, index=False)
            else:
                raise AdvancedAnalysisError(f"Unsupported data_source type: {type(data_source)}")
            
            # Create analysis script
            script_file = tmpdir_path / f'{analysis_id}_analysis.py'
            script_content = f"""
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
import json
import sys

try:
    # Load data
    df = pd.read_csv('/data/{analysis_id}_data.csv')
    
    # User analysis code
{chr(10).join('    ' + line for line in analysis_code.split(chr(10)))}
    
    # Validate result exists
    if 'result' not in locals():
        raise ValueError("Analysis code must set 'result' variable")
    
    # Determine result type and save
    if isinstance(result, pd.DataFrame):
        result.to_csv('/data/{analysis_id}_result.csv', index=False)
        metadata = {{'type': 'dataframe', 'shape': list(result.shape), 'columns': list(result.columns)}}
    elif isinstance(result, (dict, list)):
        with open('/data/{analysis_id}_result.json', 'w') as f:
            json.dump(result, f, default=str)
        metadata = {{'type': 'json'}}
    else:
        # Convert to string
        with open('/data/{analysis_id}_result.txt', 'w') as f:
            f.write(str(result))
        metadata = {{'type': 'scalar', 'value': str(result)}}
    
    # Save metadata
    with open('/data/{analysis_id}_metadata.json', 'w') as f:
        json.dump(metadata, f)
    
    print("Analysis completed successfully")
    sys.exit(0)

except Exception as e:
    # Save error
    with open('/data/{analysis_id}_error.txt', 'w') as f:
        f.write(str(e))
    print(f"Analysis failed: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
            
            script_file.write_text(script_content)
            
            # Copy files to container
            _copy_to_container(container, tmpdir, '/data')
            
            copy_time = time.time() - start_time - container_init_time
            
            # Execute analysis
            exec_start = time.time()
            
            exec_result = container.exec_run(
                f'timeout {timeout} python /data/{analysis_id}_analysis.py',
                demux=True
            )
            
            execution_time = time.time() - exec_start
            
            stdout, stderr = exec_result.output
            
            # Copy results back
            _copy_from_container(container, '/data', tmpdir)
            
            # Check for errors
            error_file = tmpdir_path / f'{analysis_id}_error.txt'
            if error_file.exists():
                error_msg = error_file.read_text()
                raise AdvancedAnalysisError(f"Analysis execution failed: {error_msg}")
            
            if exec_result.exit_code != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                raise AdvancedAnalysisError(f"Container execution failed: {error_msg}")
            
            # Read results
            metadata_file = tmpdir_path / f'{analysis_id}_metadata.json'
            
            if not metadata_file.exists():
                raise AdvancedAnalysisError("No results produced by analysis")
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Load result based on type
            if metadata['type'] == 'dataframe':
                result_file = tmpdir_path / f'{analysis_id}_result.csv'
                result_data = pd.read_csv(result_file).to_dict(orient='records')
            elif metadata['type'] == 'json':
                result_file = tmpdir_path / f'{analysis_id}_result.json'
                with open(result_file, 'r') as f:
                    result_data = json.load(f)
            else:  # scalar
                result_data = metadata.get('value')
            
            total_time = time.time() - start_time
            
            # Return container to pool
            _return_container(container, from_pool)
            
            return {
                'success': True,
                'result': result_data,
                'metadata': metadata,
                'execution_info': {
                    'analysis_id': analysis_id,
                    'container_init_time': f'{container_init_time:.2f}s',
                    'data_copy_time': f'{copy_time:.2f}s',
                    'execution_time': f'{execution_time:.2f}s',
                    'total_time': f'{total_time:.2f}s',
                    'from_pool': from_pool
                }
            }
    
    except AdvancedAnalysisError:
        _return_container(container, from_pool)
        raise
    
    except Exception as e:
        _return_container(container, from_pool)
        raise AdvancedAnalysisError(f"Unexpected error: {str(e)}")


def _copy_to_container(container, src_dir, dest_dir):
    """Copy directory to container"""
    import tarfile
    from io import BytesIO
    
    tar_stream = BytesIO()
    with tarfile.open(fileobj=tar_stream, mode='w') as tar:
        for item in Path(src_dir).iterdir():
            tar.add(item, arcname=item.name)
    
    tar_stream.seek(0)
    container.put_archive(dest_dir, tar_stream)


def _copy_from_container(container, src_dir, dest_dir):
    """Copy files from container"""
    import tarfile
    from io import BytesIO
    
    try:
        tar_stream, _ = container.get_archive(src_dir)
        
        tar_bytes = BytesIO(b''.join(tar_stream))
        
        with tarfile.open(fileobj=tar_bytes) as tar:
            # Extract only our analysis files
            members = [m for m in tar.getmembers() if not m.name.endswith('/')]
            tar.extractall(dest_dir, members=members)
    except Exception as e:
        print(f"Warning: Could not copy results from container: {e}")


# Initialize Docker on module import (optional - can be done lazily)
# _initialize_docker()

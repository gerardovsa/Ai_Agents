"""
CloudConvert Tool Implementations
==================================

This module provides tool implementations for CloudConvert file conversion.
"""

import os
import cloudconvert

try:
    from config import get_api_key_enhanced
    api_key = get_api_key_enhanced('CLOUDCONVERT_API_KEY')
except ImportError:
    api_key = os.getenv('CLOUDCONVERT_API_KEY')

# Initialize CloudConvert client
cloudconvert.configure(api_key=api_key)


def cloudconvert_convert(input_file: str, input_format: str, output_format: str, output_file: str = None):
    """
    Convert a file from one format to another.
    
    Args:
        input_file: Path to input file or URL
        input_format: Input format (e.g., 'docx')
        output_format: Output format (e.g., 'pdf')
        output_file: Optional output file path
    
    Returns:
        Conversion result with download URL
    """
    print(f"🔧 Converting {input_format} to {output_format}")
    
    try:
        job = cloudconvert.Job.create(payload={
            "tasks": {
                "import-file": {
                    "operation": "import/upload" if os.path.exists(input_file) else "import/url",
                    "url": input_file if not os.path.exists(input_file) else None
                },
                "convert-file": {
                    "operation": "convert",
                    "input": "import-file",
                    "input_format": input_format,
                    "output_format": output_format
                },
                "export-file": {
                    "operation": "export/url",
                    "input": "convert-file"
                }
            }
        })
        
        # Upload file if local
        if os.path.exists(input_file):
            upload_task = job.tasks.filter(operation='import/upload')[0]
            cloudconvert.Task.upload(file_name=input_file, task=upload_task)
        
        # Wait for completion
        job = cloudconvert.Job.wait(id=job['id'])
        
        # Get download URL
        export_task = job.tasks.filter(operation='export/url')[0]
        download_url = export_task.result.files[0]['url']
        
        # Download if output_file specified
        if output_file:
            cloudconvert.download(filename=output_file, url=download_url)
            return {'success': True, 'output_file': output_file, 'download_url': download_url}
        
        return {'success': True, 'download_url': download_url, 'job_id': job['id']}
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        raise


def cloudconvert_optimize(input_file: str, file_type: str, quality: int = 85, output_file: str = None):
    """
    Optimize an image or video file.
    
    Args:
        input_file: Path to input file
        file_type: 'image' or 'video'
        quality: Quality level 1-100
        output_file: Optional output path
    
    Returns:
        Optimization result with size reduction
    """
    print(f"🔧 Optimizing {file_type}: {input_file}")
    
    try:
        if file_type == 'image':
            # For images, convert with quality setting
            return cloudconvert_convert(
                input_file=input_file,
                input_format=os.path.splitext(input_file)[1][1:],
                output_format='jpg',
                output_file=output_file
            )
        elif file_type == 'video':
            # For videos, use optimize operation
            job = cloudconvert.Job.create(payload={
                "tasks": {
                    "import-file": {
                        "operation": "import/upload",
                        "file": input_file
                    },
                    "optimize-file": {
                        "operation": "optimize",
                        "input": "import-file"
                    },
                    "export-file": {
                        "operation": "export/url",
                        "input": "optimize-file"
                    }
                }
            })
            
            job = cloudconvert.Job.wait(id=job['id'])
            export_task = job.tasks.filter(operation='export/url')[0]
            download_url = export_task.result.files[0]['url']
            
            if output_file:
                cloudconvert.download(filename=output_file, url=download_url)
            
            return {'success': True, 'download_url': download_url}
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        raise


def cloudconvert_merge(input_files: list, output_format: str, output_file: str = None):
    """
    Merge multiple files into one.
    
    Args:
        input_files: List of file paths
        output_format: Output format (e.g., 'pdf')
        output_file: Optional output path
    
    Returns:
        Merge result with download URL
    """
    print(f"🔧 Merging {len(input_files)} files into {output_format}")
    
    try:
        # Create merge job
        tasks = {}
        
        # Import tasks
        for i, file_path in enumerate(input_files):
            tasks[f"import-{i}"] = {
                "operation": "import/upload",
                "file": file_path
            }
        
        # Merge task
        tasks["merge"] = {
            "operation": "merge",
            "input": [f"import-{i}" for i in range(len(input_files))],
            "output_format": output_format
        }
        
        # Export task
        tasks["export"] = {
            "operation": "export/url",
            "input": "merge"
        }
        
        job = cloudconvert.Job.create(payload={"tasks": tasks})
        job = cloudconvert.Job.wait(id=job['id'])
        
        export_task = job.tasks.filter(operation='export/url')[0]
        download_url = export_task.result.files[0]['url']
        
        if output_file:
            cloudconvert.download(filename=output_file, url=download_url)
        
        return {'success': True, 'download_url': download_url, 'output_file': output_file}
        
    except Exception as e:
        print(f"❌ Merge failed: {e}")
        raise


def cloudconvert_status(job_id: str):
    """
    Check status of a CloudConvert job.
    
    Args:
        job_id: Job ID to check
    
    Returns:
        Job status and progress
    """
    print(f"🔧 Checking job status: {job_id}")
    
    try:
        job = cloudconvert.Job.find(id=job_id)
        
        return {
            'job_id': job['id'],
            'status': job['status'],
            'created_at': job['created_at'],
            'finished_at': job.get('finished_at'),
            'tasks': len(job['tasks'])
        }
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        raise


if __name__ == "__main__":
    print("CloudConvert tools loaded")

"""
Render Cloud Platform Tools - Service deployment and monitoring

Functions:
- render_deploy_service: Deploy services with specific commits/images
- render_get_service_logs: Retrieve and filter service logs
- render_restart_service: Restart service instances
- render_list_services: List all workspace services
- render_get_service_metrics: Get CPU, memory, request metrics
- render_scale_service: Scale instances or change instance type
- render_get_deploys: List deployment history
- render_postgres_backup: Trigger database backups

Requirements:
- Render CLI installed (https://github.com/render-oss/cli)
- Authenticated via: render login OR RENDER_API_KEY env var
"""

import subprocess
import json
from typing import Dict, Any, List, Optional


class RenderError(Exception):
    """Custom exception for Render operations"""
    pass


def _run_render_cli(command: List[str]) -> Dict[str, Any]:
    """
    Execute Render CLI command and return parsed JSON output
    
    Args:
        command: List of command arguments (e.g., ['services', '--output', 'json'])
    
    Returns:
        Parsed JSON response from CLI
    
    Raises:
        RenderError: If command fails or returns invalid JSON
    """
    full_command = ['render'] + command + ['--output', 'json', '--confirm']
    
    try:
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse JSON output
        if result.stdout.strip():
            return json.loads(result.stdout)
        else:
            return {"success": True, "message": "Command completed successfully"}
            
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Command failed"
        raise RenderError(f"Render CLI error: {error_msg}")
    except json.JSONDecodeError as e:
        raise RenderError(f"Failed to parse Render CLI output: {str(e)}")


def render_deploy_service(
    service_id: str,
    commit_sha: Optional[str] = None,
    image_url: Optional[str] = None,
    wait: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Deploy a Render service
    
    Args:
        service_id: Render service ID (e.g., srv-abc123)
        commit_sha: Git commit SHA for Git-backed services (optional)
        image_url: Docker image URL for image-backed services (optional)
        wait: Wait for deploy to complete (default: True)
        **kwargs: Reserved for credential injection (not needed for CLI)
    
    Returns:
        Dict with deploy details (id, status, created_at, finished_at, duration)
    
    Raises:
        RenderError: If deployment fails
    
    Examples:
        # Deploy with latest commit
        render_deploy_service("srv-abc123")
        
        # Deploy specific commit
        render_deploy_service("srv-abc123", commit_sha="6377387")
        
        # Deploy specific Docker image
        render_deploy_service("srv-abc123", image_url="ghcr.io/user/repo:v1.2.3")
    """
    command = ['deploys', 'create', service_id]
    
    if commit_sha:
        command.extend(['--commit', commit_sha])
    
    if image_url:
        command.extend(['--image', image_url])
    
    if wait:
        command.append('--wait')
    
    try:
        result = _run_render_cli(command)
        return {
            "success": True,
            "service_id": service_id,
            "deploy_id": result.get('id', 'unknown'),
            "status": result.get('status', 'unknown'),
            "created_at": result.get('createdAt'),
            "finished_at": result.get('finishedAt'),
            "commit": result.get('commit', {}).get('id'),
            "message": f"Deploy {'completed' if wait else 'triggered'} successfully"
        }
    except RenderError as e:
        return {
            "success": False,
            "service_id": service_id,
            "error": str(e),
            "message": "Deploy failed"
        }


def render_get_service_logs(
    service_id: str,
    tail: int = 100,
    filter: Optional[str] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Get recent logs from a Render service
    
    Args:
        service_id: Render service ID
        tail: Number of log lines to return (default: 100, max: 10000)
        filter: Filter logs by text pattern (case-insensitive)
        **kwargs: Reserved for credential injection
    
    Returns:
        List of log entries with timestamp, level, message
    
    Raises:
        RenderError: If log retrieval fails
    """
    command = ['logs', service_id, '--tail', str(tail)]
    
    try:
        result = _run_render_cli(command)
        
        # Parse log output (CLI returns array of log lines)
        logs = result if isinstance(result, list) else []
        
        # Apply filter if provided
        if filter:
            filter_lower = filter.lower()
            logs = [log for log in logs if filter_lower in log.get('message', '').lower()]
        
        return logs
        
    except RenderError as e:
        raise RenderError(f"Failed to get logs for {service_id}: {str(e)}")


def render_restart_service(
    service_id: str,
    wait: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Restart a Render service instance
    
    Args:
        service_id: Render service ID
        wait: Wait for restart to complete (default: True)
        **kwargs: Reserved for credential injection
    
    Returns:
        Dict with restart status and timestamp
    
    Raises:
        RenderError: If restart fails
    
    Note:
        Render CLI doesn't have direct restart command.
        Triggers a new deploy which restarts the service.
    """
    return render_deploy_service(service_id, wait=wait)


def render_list_services(
    service_type: Optional[str] = None,
    status: Optional[str] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    List all Render services in workspace
    
    Args:
        service_type: Filter by type (web_service, background_worker, cron_job, etc.)
        status: Filter by status (live, suspended, failed)
        **kwargs: Reserved for credential injection
    
    Returns:
        List of services with id, name, type, status, url, last_deploy
    
    Raises:
        RenderError: If listing fails
    """
    command = ['services']
    
    try:
        result = _run_render_cli(command)
        
        # Result is array of services
        services = result if isinstance(result, list) else []
        
        # Apply filters
        if service_type:
            services = [s for s in services if s.get('type') == service_type]
        
        if status:
            services = [s for s in services if s.get('status') == status]
        
        return [{
            "service_id": s.get('id'),
            "name": s.get('name'),
            "type": s.get('type'),
            "status": s.get('status'),
            "url": s.get('serviceDetails', {}).get('url'),
            "created_at": s.get('createdAt'),
            "updated_at": s.get('updatedAt')
        } for s in services]
        
    except RenderError as e:
        raise RenderError(f"Failed to list services: {str(e)}")


def render_get_service_metrics(
    service_id: str,
    time_range: str = "1h",
    **kwargs
) -> Dict[str, Any]:
    """
    Get current metrics for a Render service
    
    Args:
        service_id: Render service ID
        time_range: Time range for metrics (1h, 6h, 24h, 7d)
        **kwargs: Reserved for credential injection
    
    Returns:
        Dict with CPU usage, memory usage, request count, latency
    
    Note:
        Render CLI doesn't expose metrics directly.
        This is a placeholder for future API integration.
        For now, returns service details only.
    
    Raises:
        RenderError: If metrics retrieval fails
    """
    # For now, get basic service info
    # TODO: Integrate with Render API for actual metrics
    command = ['services']
    
    try:
        result = _run_render_cli(command)
        services = result if isinstance(result, list) else []
        
        # Find matching service
        service = next((s for s in services if s.get('id') == service_id), None)
        
        if not service:
            raise RenderError(f"Service {service_id} not found")
        
        return {
            "service_id": service_id,
            "name": service.get('name'),
            "status": service.get('status'),
            "type": service.get('type'),
            "time_range": time_range,
            "note": "Full metrics require Render API integration (CLI limited). Set up metrics streaming to Grafana for detailed metrics."
        }
        
    except RenderError as e:
        raise RenderError(f"Failed to get metrics for {service_id}: {str(e)}")


def render_scale_service(
    service_id: str,
    num_instances: Optional[int] = None,
    instance_type: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Scale a Render service (change instance count or type)
    
    Args:
        service_id: Render service ID
        num_instances: Number of instances (1-10)
        instance_type: Instance type (starter, standard, pro, etc.)
        **kwargs: Reserved for credential injection
    
    Returns:
        Dict with updated service configuration
    
    Note:
        Render CLI doesn't support scaling directly.
        Requires Render API integration.
    
    Raises:
        RenderError: If scaling fails
    """
    raise RenderError(
        "Scaling requires Render API integration (not available via CLI). "
        "Use Render Dashboard or implement API client."
    )


def render_get_deploys(
    service_id: str,
    limit: int = 10,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    List recent deploys for a service
    
    Args:
        service_id: Render service ID
        limit: Number of deploys to return (default: 10, max: 100)
        **kwargs: Reserved for credential injection
    
    Returns:
        List of deploys with id, status, created_at, finished_at, duration, commit
    
    Raises:
        RenderError: If listing deploys fails
    """
    command = ['deploys', 'list', service_id]
    
    try:
        result = _run_render_cli(command)
        
        # Result is array of deploys
        deploys = result if isinstance(result, list) else []
        
        # Limit results
        deploys = deploys[:limit]
        
        return [{
            "deploy_id": d.get('id'),
            "status": d.get('status'),
            "created_at": d.get('createdAt'),
            "finished_at": d.get('finishedAt'),
            "commit": d.get('commit', {}).get('id'),
            "commit_message": d.get('commit', {}).get('message')
        } for d in deploys]
        
    except RenderError as e:
        raise RenderError(f"Failed to list deploys for {service_id}: {str(e)}")


def render_postgres_backup(
    database_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Trigger a manual backup of Render Postgres database
    
    Args:
        database_id: Render Postgres database ID (e.g., dpg-abc123)
        **kwargs: Reserved for credential injection
    
    Returns:
        Dict with backup details (id, timestamp, status)
    
    Note:
        Render CLI supports psql sessions but not backup triggers.
        Requires Render API integration for backup operations.
    
    Raises:
        RenderError: If backup fails
    """
    raise RenderError(
        "Database backups require Render API integration (not available via CLI). "
        "Use Render Dashboard or implement API client. "
        "Automatic daily backups are enabled for Standard tier and above."
    )


# Helper function for checking CLI availability
def _check_render_cli() -> bool:
    """Check if Render CLI is installed and authenticated"""
    try:
        result = subprocess.run(
            ['render', 'login'],
            capture_output=True,
            text=True
        )
        # If login returns 0, CLI is authenticated
        return result.returncode == 0
    except FileNotFoundError:
        return False

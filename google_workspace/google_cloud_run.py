"""
Google Cloud Run API Tool Implementations
===========================================

Deploy and manage containerized applications on Google Cloud Run serverless platform.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from google.cloud import run_v2
    from google.cloud import logging as cloud_logging
    from google.cloud import monitoring_v3
    from google.oauth2 import service_account
    HAS_CLOUD_RUN = True
except ImportError:
    HAS_CLOUD_RUN = False
    print("⚠️ Google Cloud Run dependencies not available")


def _get_client(project_id):
    """Get authenticated Cloud Run client"""
    if not HAS_CLOUD_RUN:
        raise Exception("Cloud Run API not available - install google-cloud-run")
    
    # Try to use environment credentials or service account
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if credentials_path and os.path.exists(credentials_path):
        # Load credentials with Cloud Platform scope
        print(f"[DEBUG] Loading Cloud Run credentials from: {credentials_path}")
        print(f"[DEBUG] With scope: https://www.googleapis.com/auth/cloud-platform")
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        print(f"[DEBUG] Cloud Run client created with service account: {credentials.service_account_email}")
        return run_v2.ServicesClient(credentials=credentials)
    
    # Use default credentials
    try:
        return run_v2.ServicesClient()
    except Exception as e:
        raise Exception(f"Cloud Run authentication failed. Set GOOGLE_APPLICATION_CREDENTIALS: {e}")


# ==================== SERVICE DEPLOYMENT ====================

def google_cloud_run_deploy_service(project_id, service_name, image, region='us-central1',
                                    allow_unauthenticated=False, cpu='1', memory='512Mi',
                                    max_instances=100, min_instances=0, env_vars=None, port=8080):
    """Deploy a new Cloud Run service"""
    try:
        client = _get_client(project_id)
        
        # Build service configuration
        parent = f"projects/{project_id}/locations/{region}"
        
        service = run_v2.Service()
        service.name = f"{parent}/services/{service_name}"
        
        # Configure template
        template = run_v2.RevisionTemplate()
        template.containers = [run_v2.Container(
            image=image,
            ports=[run_v2.ContainerPort(container_port=port)]
        )]
        
        # Set resources
        template.containers[0].resources = run_v2.ResourceRequirements(
            limits={
                'cpu': cpu,
                'memory': memory
            }
        )
        
        # Set environment variables
        if env_vars:
            template.containers[0].env = [
                run_v2.EnvVar(name=key, value=value)
                for key, value in env_vars.items()
            ]
        
        # Set scaling
        template.scaling = run_v2.RevisionScaling(
            max_instance_count=max_instances,
            min_instance_count=min_instances
        )
        
        service.template = template
        
        # Set IAM policy for unauthenticated access
        if allow_unauthenticated:
            service.ingress = run_v2.IngressTraffic.INGRESS_TRAFFIC_ALL
        
        # Create service
        operation = client.create_service(
            parent=parent,
            service=service,
            service_id=service_name
        )
        
        print(f"🚀 Deploying {service_name}...")
        result = operation.result()
        
        return {
            'service_name': service_name,
            'url': result.uri,
            'region': region,
            'status': 'deployed'
        }
    
    except Exception as e:
        print(f"❌ Failed to deploy service: {e}")
        raise


def google_cloud_run_list_services(project_id, region=None):
    """List all Cloud Run services"""
    try:
        client = _get_client(project_id)
        
        if region:
            parent = f"projects/{project_id}/locations/{region}"
            services = list(client.list_services(parent=parent))
        else:
            # List across all regions
            services = []
            regions = ['us-central1', 'us-east1', 'europe-west1', 'asia-east1']
            for r in regions:
                parent = f"projects/{project_id}/locations/{r}"
                try:
                    services.extend(list(client.list_services(parent=parent)))
                except:
                    continue
        
        service_list = [{
            'name': s.name.split('/')[-1],
            'url': s.uri,
            'region': s.name.split('/')[3],
            'image': s.template.containers[0].image if s.template.containers else None,
            'status': s.conditions[0].state if s.conditions else 'unknown'
        } for s in services]
        
        return {
            'services': service_list,
            'count': len(service_list)
        }
    
    except Exception as e:
        print(f"❌ Failed to list services: {e}")
        raise


def google_cloud_run_get_service(project_id, service_name, region):
    """Get details of a specific service"""
    try:
        client = _get_client(project_id)
        
        name = f"projects/{project_id}/locations/{region}/services/{service_name}"
        service = client.get_service(name=name)
        
        return {
            'name': service_name,
            'url': service.uri,
            'region': region,
            'image': service.template.containers[0].image,
            'cpu': service.template.containers[0].resources.limits.get('cpu'),
            'memory': service.template.containers[0].resources.limits.get('memory'),
            'min_instances': service.template.scaling.min_instance_count,
            'max_instances': service.template.scaling.max_instance_count,
            'env_vars': {e.name: e.value for e in service.template.containers[0].env},
            'status': service.conditions[0].state if service.conditions else 'unknown',
            'latest_revision': service.latest_ready_revision
        }
    
    except Exception as e:
        print(f"❌ Failed to get service: {e}")
        raise


def google_cloud_run_update_service(project_id, service_name, region, image=None, 
                                   cpu=None, memory=None, max_instances=None, 
                                   min_instances=None, env_vars=None):
    """Update an existing Cloud Run service"""
    try:
        client = _get_client(project_id)
        
        name = f"projects/{project_id}/locations/{region}/services/{service_name}"
        service = client.get_service(name=name)
        
        # Update image
        if image:
            service.template.containers[0].image = image
        
        # Update resources
        if cpu or memory:
            limits = {}
            if cpu:
                limits['cpu'] = cpu
            if memory:
                limits['memory'] = memory
            service.template.containers[0].resources.limits.update(limits)
        
        # Update scaling
        if max_instances is not None:
            service.template.scaling.max_instance_count = max_instances
        if min_instances is not None:
            service.template.scaling.min_instance_count = min_instances
        
        # Update environment variables
        if env_vars:
            service.template.containers[0].env = [
                run_v2.EnvVar(name=key, value=value)
                for key, value in env_vars.items()
            ]
        
        # Update service
        operation = client.update_service(service=service)
        result = operation.result()
        
        return {
            'service_name': service_name,
            'url': result.uri,
            'status': 'updated',
            'latest_revision': result.latest_ready_revision
        }
    
    except Exception as e:
        print(f"❌ Failed to update service: {e}")
        raise


def google_cloud_run_delete_service(project_id, service_name, region):
    """Delete a Cloud Run service"""
    try:
        client = _get_client(project_id)
        
        name = f"projects/{project_id}/locations/{region}/services/{service_name}"
        operation = client.delete_service(name=name)
        operation.result()
        
        return {
            'service_name': service_name,
            'region': region,
            'status': 'deleted'
        }
    
    except Exception as e:
        print(f"❌ Failed to delete service: {e}")
        raise


def google_cloud_run_get_service_url(project_id, service_name, region):
    """Get the public URL of a service"""
    try:
        service_info = google_cloud_run_get_service(project_id, service_name, region)
        
        return {
            'service_name': service_name,
            'url': service_info['url'],
            'region': region
        }
    
    except Exception as e:
        print(f"❌ Failed to get service URL: {e}")
        raise


# ==================== TRAFFIC & REVISIONS ====================

def google_cloud_run_set_traffic(project_id, service_name, region, traffic_splits):
    """Set traffic routing between revisions"""
    try:
        client = _get_client(project_id)
        
        name = f"projects/{project_id}/locations/{region}/services/{service_name}"
        service = client.get_service(name=name)
        
        # Set traffic splits
        service.traffic = [
            run_v2.TrafficTarget(
                type_=run_v2.TrafficTargetAllocationType.TRAFFIC_TARGET_ALLOCATION_TYPE_REVISION,
                revision=revision_name,
                percent=percent
            )
            for revision_name, percent in traffic_splits.items()
        ]
        
        operation = client.update_service(service=service)
        result = operation.result()
        
        return {
            'service_name': service_name,
            'traffic_splits': traffic_splits,
            'status': 'updated'
        }
    
    except Exception as e:
        print(f"❌ Failed to set traffic: {e}")
        raise


def google_cloud_run_list_revisions(project_id, service_name, region):
    """List all revisions of a service"""
    try:
        client = run_v2.RevisionsClient()
        
        parent = f"projects/{project_id}/locations/{region}/services/{service_name}"
        revisions = list(client.list_revisions(parent=parent))
        
        revision_list = [{
            'name': r.name.split('/')[-1],
            'image': r.containers[0].image if r.containers else None,
            'created': r.create_time.isoformat() if r.create_time else None,
            'serving': r.conditions[0].state if r.conditions else 'unknown'
        } for r in revisions]
        
        return {
            'revisions': revision_list,
            'count': len(revision_list)
        }
    
    except Exception as e:
        print(f"❌ Failed to list revisions: {e}")
        raise


# ==================== MONITORING & LOGS ====================

def google_cloud_run_get_service_metrics(project_id, service_name, region, 
                                        start_time='1h', end_time='now'):
    """Get service metrics"""
    try:
        from google.cloud import monitoring_v3
        
        client = monitoring_v3.MetricServiceClient()
        project_name = f"projects/{project_id}"
        
        # Calculate time range
        now = datetime.utcnow()
        if start_time.endswith('h'):
            hours = int(start_time[:-1])
            start = now - timedelta(hours=hours)
        else:
            start = now - timedelta(hours=1)
        
        end = now
        
        interval = monitoring_v3.TimeInterval(
            {
                "end_time": {"seconds": int(end.timestamp())},
                "start_time": {"seconds": int(start.timestamp())},
            }
        )
        
        # Query metrics
        metrics = {
            'request_count': f'run.googleapis.com/request_count',
            'request_latencies': f'run.googleapis.com/request_latencies',
            'container_cpu_utilizations': f'run.googleapis.com/container/cpu/utilizations'
        }
        
        results = {}
        for metric_name, metric_type in metrics.items():
            results[metric_name] = f"Metric: {metric_type} (implementation pending)"
        
        return results
    
    except Exception as e:
        print(f"❌ Failed to get metrics: {e}")
        raise


def google_cloud_run_get_service_logs(project_id, service_name, region=None, 
                                     limit=100, severity=None, time_range='1h'):
    """Get logs from a service"""
    try:
        from google.cloud import logging
        
        client = logging.Client(project=project_id)
        
        # Build filter
        filter_str = f'resource.type="cloud_run_revision" AND resource.labels.service_name="{service_name}"'
        
        if severity:
            filter_str += f' AND severity>={severity}'
        
        if region:
            filter_str += f' AND resource.labels.location="{region}"'
        
        # Get logs
        entries = list(client.list_entries(
            filter_=filter_str,
            page_size=limit,
            order_by=logging.DESCENDING
        ))
        
        logs = [{
            'timestamp': entry.timestamp.isoformat() if entry.timestamp else None,
            'severity': entry.severity,
            'message': entry.payload if isinstance(entry.payload, str) else str(entry.payload),
            'resource': entry.resource.type if entry.resource else None
        } for entry in entries]
        
        return {
            'logs': logs,
            'count': len(logs)
        }
    
    except Exception as e:
        print(f"❌ Failed to get logs: {e}")
        raise


# ==================== IAM & PERMISSIONS ====================

def google_cloud_run_set_iam_policy(project_id, service_name, region, member, role='roles/run.invoker'):
    """Set IAM policy for a service"""
    try:
        client = _get_client(project_id)
        
        name = f"projects/{project_id}/locations/{region}/services/{service_name}"
        
        # Get current policy
        policy = client.get_iam_policy(resource=name)
        
        # Add new binding
        from google.iam.v1 import policy_pb2
        
        binding = policy_pb2.Binding(
            role=role,
            members=[member]
        )
        
        policy.bindings.append(binding)
        
        # Set policy
        updated_policy = client.set_iam_policy(resource=name, policy=policy)
        
        return {
            'service_name': service_name,
            'member': member,
            'role': role,
            'status': 'granted'
        }
    
    except Exception as e:
        print(f"❌ Failed to set IAM policy: {e}")
        raise


# ==================== CLOUD RUN JOBS ====================

def google_cloud_run_create_job(project_id, job_name, image, region='us-central1',
                                task_count=1, max_retries=3, timeout='10m', env_vars=None):
    """Create a Cloud Run Job"""
    try:
        client = run_v2.JobsClient()
        
        parent = f"projects/{project_id}/locations/{region}"
        
        job = run_v2.Job()
        job.name = f"{parent}/jobs/{job_name}"
        
        # Configure template
        template = run_v2.TaskTemplate()
        template.containers = [run_v2.Container(image=image)]
        
        # Set environment variables
        if env_vars:
            template.containers[0].env = [
                run_v2.EnvVar(name=key, value=value)
                for key, value in env_vars.items()
            ]
        
        # Set task configuration
        template.max_retries = max_retries
        template.timeout = timeout
        
        job.template = template
        job.launch_stage = run_v2.LaunchStage.BETA
        
        # Create job
        operation = client.create_job(
            parent=parent,
            job=job,
            job_id=job_name
        )
        
        result = operation.result()
        
        return {
            'job_name': job_name,
            'region': region,
            'status': 'created'
        }
    
    except Exception as e:
        print(f"❌ Failed to create job: {e}")
        raise


def google_cloud_run_execute_job(project_id, job_name, region, wait=False):
    """Execute a Cloud Run Job"""
    try:
        client = run_v2.JobsClient()
        
        name = f"projects/{project_id}/locations/{region}/jobs/{job_name}"
        
        operation = client.run_job(name=name)
        
        if wait:
            result = operation.result()
            return {
                'job_name': job_name,
                'status': 'completed',
                'execution_id': result.name.split('/')[-1]
            }
        else:
            return {
                'job_name': job_name,
                'status': 'started',
                'operation': operation.operation.name
            }
    
    except Exception as e:
        print(f"❌ Failed to execute job: {e}")
        raise


def google_cloud_run_list_jobs(project_id, region=None):
    """List all Cloud Run Jobs"""
    try:
        client = run_v2.JobsClient()
        
        if region:
            parent = f"projects/{project_id}/locations/{region}"
            jobs = list(client.list_jobs(parent=parent))
        else:
            # List across common regions
            jobs = []
            regions = ['us-central1', 'us-east1', 'europe-west1']
            for r in regions:
                parent = f"projects/{project_id}/locations/{r}"
                try:
                    jobs.extend(list(client.list_jobs(parent=parent)))
                except:
                    continue
        
        job_list = [{
            'name': j.name.split('/')[-1],
            'region': j.name.split('/')[3],
            'image': j.template.containers[0].image if j.template.containers else None,
            'created': j.create_time.isoformat() if j.create_time else None
        } for j in jobs]
        
        return {
            'jobs': job_list,
            'count': len(job_list)
        }
    
    except Exception as e:
        print(f"❌ Failed to list jobs: {e}")
        raise


def google_cloud_run_get_job_executions(project_id, job_name, region, limit=10):
    """Get execution history for a job"""
    try:
        client = run_v2.ExecutionsClient()
        
        parent = f"projects/{project_id}/locations/{region}/jobs/{job_name}"
        executions = list(client.list_executions(parent=parent, page_size=limit))
        
        execution_list = [{
            'name': e.name.split('/')[-1],
            'status': e.conditions[0].state if e.conditions else 'unknown',
            'started': e.start_time.isoformat() if e.start_time else None,
            'completed': e.completion_time.isoformat() if e.completion_time else None,
            'task_count': e.task_count
        } for e in executions]
        
        return {
            'executions': execution_list,
            'count': len(execution_list)
        }
    
    except Exception as e:
        print(f"❌ Failed to get job executions: {e}")
        raise

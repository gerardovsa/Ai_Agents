"""
Track Render Deployment with Real-time Error Detection

FILE: scripts/deployment/track_render_deployment.py
PURPOSE: Monitor Render deployments in real-time with automatic error detection

DEPENDENCIES:
- requests (HTTP client for Render API)
- Standard library: time, sys, datetime, json

USAGE:
    python track_render_deployment.py [service_id] [--interval SECONDS]
    
    Default service_id: srv-d4b2723uibrs73ff02t0
    Default interval: 15 seconds

FEATURES:
- Real-time deployment status monitoring
- Automatic error pattern detection
- Success marker identification
- Colored console output
- Log analysis and reporting

LAST MODIFIED: 2025-11-16 - Initial creation for v6 deployment
"""

import requests
import time
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional

class RenderDeploymentTracker:
    """
    Track Render deployments with real-time monitoring and error detection
    """
    
    def __init__(self, service_id: str = "srv-d4b2723uibrs73ff02t0"):
        """
        Initialize deployment tracker
        
        Args:
            service_id: Render service ID to monitor
        """
        self.service_id = service_id
        self.api_key = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
        self.base_url = "https://api.render.com/v1"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Error patterns to detect
        self.error_patterns = [
            "no such column",
            "relation does not exist",
            "connection refused",
            "AUTOINCREMENT",
            "sqlite3.connect",
            "ModuleNotFoundError",
            "ImportError",
            "SyntaxError",
            "NameError",
            "KeyError",
            "AttributeError",
            "TypeError",
            "ValueError",
            "RuntimeError",
            "permission denied",
            "authentication failed",
            "timeout",
            "cannot connect",
            "failed to",
            "error:",
            "exception:",
            "traceback",
        ]
        
        # Success patterns to identify
        self.success_patterns = [
            "Connected to Supabase PostgreSQL",
            "Serving on http://0.0.0.0:10000",
            "Loaded 594 tools",
            "Loaded 576 tools",
            "Flask app registered",
            "All tools loaded successfully",
            "Database connection established",
            "OAuth routes registered",
            "Health check endpoint active",
            "Application startup complete",
        ]
        
        # Warning patterns
        self.warning_patterns = [
            "warning:",
            "deprecated",
            "fallback",
            "retrying",
            "skipping",
        ]
    
    def get_latest_deploy(self) -> Optional[Dict]:
        """
        Get latest deployment status from Render API
        
        Returns:
            Dict with deployment info or None if request fails
        """
        try:
            url = f"{self.base_url}/services/{self.service_id}/deploys"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            deploys = response.json()
            
            if deploys and len(deploys) > 0:
                return deploys[0]  # Most recent deploy
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None
    
    def get_logs(self, deploy_id: str) -> str:
        """
        Get deployment logs from Render API
        
        Args:
            deploy_id: Deployment ID to fetch logs for
            
        Returns:
            Log text as string
        """
        try:
            url = f"{self.base_url}/services/{self.service_id}/deploys/{deploy_id}/logs"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"Log Fetch Error: {e}")
            return ""
    
    def analyze_logs(self, logs: str) -> Dict:
        """
        Analyze logs for errors, warnings, and success markers
        
        Args:
            logs: Log text to analyze
            
        Returns:
            Dict with errors, warnings, success_markers, and metadata
        """
        errors = []
        warnings = []
        success_markers = []
        
        log_lines = logs.split('\n')
        
        for line in log_lines:
            line_lower = line.lower()
            
            # Check for errors
            for pattern in self.error_patterns:
                if pattern.lower() in line_lower:
                    if line not in errors:  # Avoid duplicates
                        errors.append(line.strip())
                    break  # Only count once per line
            
            # Check for warnings
            for pattern in self.warning_patterns:
                if pattern.lower() in line_lower:
                    if line not in warnings:
                        warnings.append(line.strip())
                    break
            
            # Check for success markers
            for pattern in self.success_patterns:
                if pattern in line:
                    if line not in success_markers:
                        success_markers.append(line.strip())
                    break
        
        return {
            'errors': errors,
            'warnings': warnings,
            'success_markers': success_markers,
            'total_lines': len(log_lines),
            'non_empty_lines': len([l for l in log_lines if l.strip()])
        }
    
    def print_analysis(self, analysis: Dict, show_all: bool = False):
        """
        Print log analysis results
        
        Args:
            analysis: Analysis dict from analyze_logs()
            show_all: If True, show all entries; if False, show last 10
        """
        # Print success markers
        if analysis['success_markers']:
            print("\n=== SUCCESS MARKERS ===")
            markers = analysis['success_markers'] if show_all else analysis['success_markers'][-10:]
            for marker in markers:
                print(f"  {marker}")
        
        # Print warnings
        if analysis['warnings']:
            print("\n=== WARNINGS ===")
            warns = analysis['warnings'] if show_all else analysis['warnings'][-10:]
            for warning in warns:
                print(f"  {warning}")
        
        # Print errors
        if analysis['errors']:
            print("\n=== ERRORS DETECTED ===")
            errs = analysis['errors'] if show_all else analysis['errors'][-15:]
            for error in errs:
                print(f"  {error}")
        
        # Print summary
        print(f"\n=== SUMMARY ===")
        print(f"  Total log lines: {analysis['total_lines']}")
        print(f"  Non-empty lines: {analysis['non_empty_lines']}")
        print(f"  Success markers: {len(analysis['success_markers'])}")
        print(f"  Warnings: {len(analysis['warnings'])}")
        print(f"  Errors: {len(analysis['errors'])}")
    
    def track(self, interval: int = 15, max_iterations: int = 100):
        """
        Track deployment with real-time updates
        
        Args:
            interval: Seconds between status checks
            max_iterations: Max number of checks before stopping
        """
        print("=" * 70)
        print("RENDER DEPLOYMENT TRACKER")
        print("=" * 70)
        print(f"\nService ID: {self.service_id}")
        print(f"Check interval: {interval} seconds")
        print(f"Max iterations: {max_iterations}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nPress Ctrl+C to stop monitoring\n")
        print("=" * 70)
        
        last_status = None
        last_deploy_id = None
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
                deploy = self.get_latest_deploy()
                
                if not deploy:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] No deployment found")
                    time.sleep(interval)
                    continue
                
                status = deploy.get('status')
                deploy_id = deploy.get('id')
                created_at = deploy.get('createdAt', 'Unknown')
                updated_at = deploy.get('updatedAt', 'Unknown')
                
                # New deployment or status changed
                if deploy_id != last_deploy_id or status != last_status:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"\n{'=' * 70}")
                    print(f"[{timestamp}] DEPLOYMENT STATUS: {status.upper()}")
                    print(f"Deploy ID: {deploy_id}")
                    print(f"Created: {created_at}")
                    print(f"Updated: {updated_at}")
                    print(f"{'=' * 70}")
                    
                    # Get and analyze logs
                    print("\nFetching logs...")
                    logs = self.get_logs(deploy_id)
                    
                    if logs:
                        analysis = self.analyze_logs(logs)
                        self.print_analysis(analysis, show_all=False)
                    else:
                        print("  (No logs available yet)")
                    
                    last_status = status
                    last_deploy_id = deploy_id
                
                # Deployment completed
                if status in ['live', 'failed']:
                    print(f"\n{'=' * 70}")
                    print(f"DEPLOYMENT {status.upper()}")
                    print(f"{'=' * 70}")
                    
                    if status == 'live':
                        print("\nDEPLOYMENT SUCCESSFUL")
                        print("\nNext steps:")
                        print("1. Test health endpoint:")
                        print("   https://ai-agents-backend-singapore.onrender.com/health")
                        print("\n2. Verify Supabase connection:")
                        print("   Check logs for 'Connected to Supabase PostgreSQL'")
                        print("\n3. Test OAuth flows:")
                        print("   - Google OAuth: /api/google-oauth/authorize")
                        print("   - Microsoft OAuth: /api/microsoft-oauth/authorize")
                        print("\n4. Test tool execution:")
                        print("   POST /api/agent/chat")
                        print("   {\"message\": \"List available platforms\", \"user_id\": 1}")
                        
                    else:
                        print("\nDEPLOYMENT FAILED")
                        print("\nReview errors above and check full logs:")
                        print(f"https://dashboard.render.com/web/{self.service_id}")
                        print("\nCommon fixes:")
                        print("- Check environment variables in Render dashboard")
                        print("- Verify Supabase connection string")
                        print("- Review database migration status")
                        print("- Check for Python dependency issues")
                    
                    print(f"\n{'=' * 70}")
                    break
                
                # Show progress indicator
                dots = "." * (iteration % 4)
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] Monitoring{dots:<4}", end='', flush=True)
                
                # Continue monitoring
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n\nMonitoring stopped by user")
                print(f"Last status: {last_status}")
                print(f"Iterations completed: {iteration}")
                break
                
            except Exception as e:
                print(f"\nUnexpected error: {e}")
                print("Continuing monitoring...")
                time.sleep(interval)
        
        if iteration >= max_iterations:
            print(f"\n\nReached maximum iterations ({max_iterations})")
            print(f"Last status: {last_status}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Track Render deployment status in real-time'
    )
    parser.add_argument(
        'service_id',
        nargs='?',
        default='srv-d4b2723uibrs73ff02t0',
        help='Render service ID (default: srv-d4b2723uibrs73ff02t0)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=15,
        help='Seconds between status checks (default: 15)'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=100,
        help='Maximum number of checks (default: 100)'
    )
    
    args = parser.parse_args()
    
    tracker = RenderDeploymentTracker(service_id=args.service_id)
    tracker.track(interval=args.interval, max_iterations=args.max_iterations)


if __name__ == "__main__":
    main()

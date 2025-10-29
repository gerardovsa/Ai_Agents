"""
Microsoft To Do and Planner Tools
Provides task management, planning, and collaboration via Microsoft Graph API
"""

import os
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

class MicrosoftTodoTools:
    """Microsoft To Do and Planner task management tools"""
    
    def __init__(self):
        # Credentials are injected dynamically per-user via credential_injector
        # No need to check environment variables at init time
        self.graph_api_base = 'https://graph.microsoft.com/v1.0'
    
    def _get_headers(self, **kwargs) -> Dict[str, str]:
        """Get authorization headers for Microsoft Graph API"""
        # Get access token from credential injector
        if '_user_id' in kwargs:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'AI_infrastructure'))
            from auth.credential_injector import get_microsoft_access_token
            access_token = get_microsoft_access_token(**kwargs)
        else:
            raise Exception("No user credentials provided. User must be authenticated.")
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, **kwargs) -> Dict:
        """Make HTTP request to Microsoft Graph API"""
        url = f"{self.graph_api_base}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self._get_headers(**kwargs), params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self._get_headers(**kwargs), json=data, params=params)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self._get_headers(**kwargs), json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self._get_headers(**kwargs))
            else:
                return {'success': False, 'error': f'Unsupported HTTP method: {method}'}
            
            response.raise_for_status()
            
            if response.status_code == 204:
                return {'success': True}
            
            return {'success': True, 'data': response.json()}
            
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = e.response.json()
                error_msg = error_data.get('error', {}).get('message', str(e))
            except:
                pass
            return {'success': False, 'error': error_msg, 'status_code': e.response.status_code}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== TO DO TASKS ====================
    
    def todo_list_tasks(self, user_id: str, list_id: str = None, show_completed: bool = False, **kwargs) -> Dict:
        """List tasks from To Do"""
        
        if list_id:
            endpoint = f'/me/todo/lists/{list_id}/tasks'
        else:
            # Get default list
            lists_result = self._make_request('GET', '/me/todo/lists', **kwargs)
            if not lists_result['success']:
                return lists_result
            
            lists = lists_result['data'].get('value', [])
            if not lists:
                return {'success': False, 'error': 'No To Do lists found'}
            
            list_id = lists[0]['id']
            endpoint = f'/me/todo/lists/{list_id}/tasks'
        
        params = {}
        if not show_completed:
            params['$filter'] = 'status ne \'completed\''
        
        result = self._make_request('GET', endpoint, params=params, **kwargs)
        
        if result['success']:
            tasks = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(tasks),
                'list_id': list_id,
                'tasks': [{
                    'id': t.get('id'),
                    'title': t.get('title'),
                    'status': t.get('status'),
                    'importance': t.get('importance'),
                    'due_date': t.get('dueDateTime', {}).get('dateTime') if t.get('dueDateTime') else None,
                    'created': t.get('createdDateTime')
                } for t in tasks]
            }
        return result
    
    def todo_create_task(self, user_id: str, title: str, list_id: str = None,
                        due_date: str = None, importance: str = 'normal',
                        body: str = None, reminder: str = None, **kwargs) -> Dict:
        """Create a new To Do task"""
        
        if not list_id:
            # Get default list
            lists_result = self._make_request('GET', '/me/todo/lists', **kwargs)
            if not lists_result['success']:
                return lists_result
            lists = lists_result['data'].get('value', [])
            if not lists:
                return {'success': False, 'error': 'No To Do lists found'}
            list_id = lists[0]['id']
        
        task_data = {
            'title': title,
            'importance': importance
        }
        
        if due_date:
            task_data['dueDateTime'] = {
                'dateTime': due_date,
                'timeZone': 'UTC'
            }
        
        if body:
            task_data['body'] = {
                'content': body,
                'contentType': 'text'
            }
        
        if reminder:
            task_data['reminderDateTime'] = {
                'dateTime': reminder,
                'timeZone': 'UTC'
            }
        
        result = self._make_request('POST', f'/me/todo/lists/{list_id}/tasks', task_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Task "{title}" created successfully',
                'task': result['data']
            }
        return result
    
    def todo_update_task(self, user_id: str, list_id: str, task_id: str, updates: Dict, **kwargs) -> Dict:
        """Update an existing To Do task"""
        result = self._make_request('PATCH', f'/me/todo/lists/{list_id}/tasks/{task_id}', updates, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Task updated successfully',
                'task': result.get('data', {})
            }
        return result
    
    def todo_complete_task(self, user_id: str, list_id: str, task_id: str, **kwargs) -> Dict:
        """Mark a To Do task as complete"""
        update_data = {'status': 'completed'}
        result = self.todo_update_task(user_id, list_id, task_id, update_data)
        
        if result['success']:
            result['message'] = 'Task marked as complete'
        return result
    
    def todo_delete_task(self, user_id: str, list_id: str, task_id: str, **kwargs) -> Dict:
        """Delete a To Do task"""
        result = self._make_request('DELETE', f'/me/todo/lists/{list_id}/tasks/{task_id}', **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Task deleted successfully'
            }
        return result
    
    def todo_create_list(self, user_id: str, list_name: str, **kwargs) -> Dict:
        """Create a new To Do list"""
        list_data = {'displayName': list_name}
        result = self._make_request('POST', '/me/todo/lists', list_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'List "{list_name}" created successfully',
                'list': result['data']
            }
        return result
    
    def todo_list_lists(self, user_id: str, **kwargs) -> Dict:
        """List all To Do lists"""
        result = self._make_request('GET', '/me/todo/lists', **kwargs)
        
        if result['success']:
            lists = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(lists),
                'lists': [{
                    'id': l.get('id'),
                    'name': l.get('displayName'),
                    'is_owner': l.get('isOwner'),
                    'is_shared': l.get('isShared')
                } for l in lists]
            }
        return result
    
    # ==================== PLANNER ====================
    
    def planner_list_plans(self, user_id: str, group_id: str = None, **kwargs) -> Dict:
        """List Planner plans"""
        
        if group_id:
            endpoint = f'/groups/{group_id}/planner/plans'
        else:
            endpoint = '/me/planner/plans'
        
        result = self._make_request('GET', endpoint, **kwargs)
        
        if result['success']:
            plans = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(plans),
                'plans': [{
                    'id': p.get('id'),
                    'title': p.get('title'),
                    'owner': p.get('owner'),
                    'created': p.get('createdDateTime')
                } for p in plans]
            }
        return result
    
    def planner_create_plan(self, user_id: str, title: str, group_id: str, **kwargs) -> Dict:
        """Create a new Planner plan"""
        
        plan_data = {
            'owner': group_id,
            'title': title
        }
        
        result = self._make_request('POST', '/planner/plans', plan_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Plan "{title}" created successfully',
                'plan': result['data']
            }
        return result
    
    def planner_list_buckets(self, user_id: str, plan_id: str, **kwargs) -> Dict:
        """List buckets in a Planner plan"""
        result = self._make_request('GET', f'/planner/plans/{plan_id}/buckets', **kwargs)
        
        if result['success']:
            buckets = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(buckets),
                'buckets': [{
                    'id': b.get('id'),
                    'name': b.get('name'),
                    'order_hint': b.get('orderHint')
                } for b in buckets]
            }
        return result
    
    def planner_create_bucket(self, user_id: str, plan_id: str, name: str, **kwargs) -> Dict:
        """Create a new bucket in a Planner plan"""
        
        bucket_data = {
            'name': name,
            'planId': plan_id,
            'orderHint': ' !'
        }
        
        result = self._make_request('POST', '/planner/buckets', bucket_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Bucket "{name}" created successfully',
                'bucket': result['data']
            }
        return result
    
    def planner_list_tasks(self, user_id: str, plan_id: str = None, bucket_id: str = None, **kwargs) -> Dict:
        """List tasks in a Planner plan or bucket"""
        
        if bucket_id:
            endpoint = f'/planner/buckets/{bucket_id}/tasks'
        elif plan_id:
            endpoint = f'/planner/plans/{plan_id}/tasks'
        else:
            endpoint = '/me/planner/tasks'
        
        result = self._make_request('GET', endpoint, **kwargs)
        
        if result['success']:
            tasks = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(tasks),
                'tasks': [{
                    'id': t.get('id'),
                    'title': t.get('title'),
                    'bucket_id': t.get('bucketId'),
                    'percent_complete': t.get('percentComplete'),
                    'priority': t.get('priority'),
                    'due_date': t.get('dueDateTime'),
                    'assignments': list(t.get('assignments', {}).keys())
                } for t in tasks]
            }
        return result
    
    def planner_create_task(self, user_id: str, plan_id: str, bucket_id: str,
                           title: str, due_date: str = None, priority: int = 5,
                           assignments: List[str] = None, **kwargs) -> Dict:
        """Create a new Planner task"""
        
        task_data = {
            'planId': plan_id,
            'bucketId': bucket_id,
            'title': title,
            'priority': priority
        }
        
        if due_date:
            task_data['dueDateTime'] = due_date
        
        if assignments:
            task_data['assignments'] = {
                user_id: {'@odata.type': '#microsoft.graph.plannerAssignment', 'orderHint': ' !'}
                for user_id in assignments
            }
        
        result = self._make_request('POST', '/planner/tasks', task_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Task "{title}" created successfully',
                'task': result['data']
            }
        return result
    
    def planner_update_task(self, user_id: str, task_id: str, updates: Dict, etag: str, **kwargs) -> Dict:
        """Update a Planner task"""
        
        # Planner requires If-Match header with etag
        headers = self._get_headers(**kwargs)
        headers['If-Match'] = etag
        
        try:
            response = requests.patch(
                f'{self.graph_api_base}/planner/tasks/{task_id}',
                headers=headers,
                json=updates
            )
            response.raise_for_status()
            
            return {
                'success': True,
                'message': 'Task updated successfully',
                'task': response.json()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def planner_assign_task(self, user_id: str, task_id: str, assignee_id: str, etag: str, **kwargs) -> Dict:
        """Assign a Planner task to a user"""
        
        updates = {
            'assignments': {
                assignee_id: {
                    '@odata.type': '#microsoft.graph.plannerAssignment',
                    'orderHint': ' !'
                }
            }
        }
        
        return self.planner_update_task(user_id, task_id, updates, etag)
    
    def planner_add_checklist(self, user_id: str, task_id: str, checklist_items: List[str], etag: str, **kwargs) -> Dict:
        """Add checklist items to a Planner task"""
        
        # Get task details first
        details_result = self._make_request('GET', f'/planner/tasks/{task_id}/details', **kwargs)
        
        if not details_result['success']:
            return details_result
        
        # Build checklist
        checklist = {}
        for item in checklist_items:
            item_id = str(int(time.time() * 1000))  # Simple unique ID
            checklist[item_id] = {
                '@odata.type': '#microsoft.graph.plannerChecklistItem',
                'title': item,
                'isChecked': False
            }
        
        # Update task details
        headers = self._get_headers(**kwargs)
        headers['If-Match'] = etag
        
        try:
            response = requests.patch(
                f'{self.graph_api_base}/planner/tasks/{task_id}/details',
                headers=headers,
                json={'checklist': checklist}
            )
            response.raise_for_status()
            
            return {
                'success': True,
                'message': f'Added {len(checklist_items)} checklist items',
                'checklist': checklist
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== SMART TOOLS ====================
    
    def todo_smart_daily_digest(self, user_id: str, **kwargs) -> Dict:
        """Generate daily task digest with priorities and deadlines"""
        
        # Get all To Do lists
        lists_result = self.todo_list_lists(user_id)
        if not lists_result['success']:
            return lists_result
        
        digest = {
            'success': True,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'overdue': [],
            'due_today': [],
            'due_this_week': [],
            'high_priority': [],
            'total_tasks': 0
        }
        
        today = datetime.now().date()
        week_end = today + timedelta(days=7)
        
        # Process each list
        for todo_list in lists_result['lists']:
            tasks_result = self.todo_list_tasks(user_id, todo_list['id'], show_completed=False)
            
            if tasks_result['success']:
                for task in tasks_result['tasks']:
                    digest['total_tasks'] += 1
                    
                    # Check due date
                    if task['due_date']:
                        due_date = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00')).date()
                        
                        if due_date < today:
                            digest['overdue'].append(task)
                        elif due_date == today:
                            digest['due_today'].append(task)
                        elif due_date <= week_end:
                            digest['due_this_week'].append(task)
                    
                    # Check priority
                    if task['importance'] == 'high':
                        digest['high_priority'].append(task)
        
        digest['summary'] = {
            'overdue_count': len(digest['overdue']),
            'due_today_count': len(digest['due_today']),
            'due_this_week_count': len(digest['due_this_week']),
            'high_priority_count': len(digest['high_priority'])
        }
        
        return digest
    
    def planner_smart_sprint_setup(self, user_id: str, group_id: str, sprint_name: str,
                                   duration_weeks: int = 2, buckets: List[str] = None, **kwargs) -> Dict:
        """Create complete sprint board with buckets and tasks"""
        
        # Default sprint buckets
        if not buckets:
            buckets = ['Backlog', 'To Do', 'In Progress', 'Review', 'Done']
        
        # Create plan
        plan_result = self.planner_create_plan(user_id, sprint_name, group_id)
        
        if not plan_result['success']:
            return plan_result
        
        plan_id = plan_result['plan']['id']
        
        results = {
            'success': True,
            'plan_id': plan_id,
            'plan_name': sprint_name,
            'buckets_created': [],
            'duration_weeks': duration_weeks,
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(weeks=duration_weeks)).strftime('%Y-%m-%d')
        }
        
        # Create buckets
        for bucket_name in buckets:
            bucket_result = self.planner_create_bucket(user_id, plan_id, bucket_name)
            
            if bucket_result['success']:
                results['buckets_created'].append({
                    'name': bucket_name,
                    'id': bucket_result['bucket']['id']
                })
            else:
                results['success'] = False
                results['error'] = f"Failed to create bucket: {bucket_name}"
                break
        
        results['message'] = f"Sprint '{sprint_name}' created with {len(results['buckets_created'])} buckets"
        
        return results
    
    def planner_smart_team_workload(self, user_id: str, plan_id: str, **kwargs) -> Dict:
        """Analyze team workload and balance suggestions"""
        
        # Get all tasks
        tasks_result = self.planner_list_tasks(user_id, plan_id=plan_id)
        
        if not tasks_result['success']:
            return tasks_result
        
        # Analyze workload by assignee
        workload = {}
        unassigned = []
        
        for task in tasks_result['tasks']:
            if task['assignments']:
                for assignee in task['assignments']:
                    if assignee not in workload:
                        workload[assignee] = {
                            'total_tasks': 0,
                            'completed': 0,
                            'in_progress': 0,
                            'high_priority': 0
                        }
                    
                    workload[assignee]['total_tasks'] += 1
                    
                    if task['percent_complete'] == 100:
                        workload[assignee]['completed'] += 1
                    elif task['percent_complete'] > 0:
                        workload[assignee]['in_progress'] += 1
                    
                    if task['priority'] <= 3:  # Priority 1-3 is high
                        workload[assignee]['high_priority'] += 1
            else:
                unassigned.append(task)
        
        # Calculate balance
        if workload:
            avg_tasks = sum(w['total_tasks'] for w in workload.values()) / len(workload)
            
            overloaded = [uid for uid, w in workload.items() if w['total_tasks'] > avg_tasks * 1.5]
            underutilized = [uid for uid, w in workload.items() if w['total_tasks'] < avg_tasks * 0.5]
        else:
            avg_tasks = 0
            overloaded = []
            underutilized = []
        
        return {
            'success': True,
            'total_tasks': tasks_result['count'],
            'workload_by_user': workload,
            'unassigned_tasks': len(unassigned),
            'analysis': {
                'average_tasks_per_user': round(avg_tasks, 2),
                'overloaded_users': overloaded,
                'underutilized_users': underutilized
            },
            'recommendations': self._generate_workload_recommendations(workload, overloaded, underutilized, unassigned)
        }
    
    def _generate_workload_recommendations(self, workload: Dict, overloaded: List, 
                                          underutilized: List, unassigned: List) -> List[str]:
        """Generate workload balancing recommendations"""
        recommendations = []
        
        if overloaded:
            recommendations.append(f"Redistribute tasks from {len(overloaded)} overloaded users")
        
        if underutilized and unassigned:
            recommendations.append(f"Assign some of {len(unassigned)} unassigned tasks to underutilized users")
        
        if not workload:
            recommendations.append("No tasks assigned yet - start assigning tasks to team members")
        
        return recommendations
    
    def todo_smart_recurring_tasks(self, user_id: str, task_template: Dict, 
                                  recurrence_pattern: str, count: int, **kwargs) -> Dict:
        """Create recurring tasks with custom patterns"""
        
        # Parse recurrence pattern (daily, weekly, monthly)
        title_template = task_template['title']
        list_id = task_template.get('list_id')
        
        results = {
            'success': True,
            'created': [],
            'failed': []
        }
        
        start_date = datetime.now()
        
        for i in range(count):
            # Calculate due date based on pattern
            if recurrence_pattern == 'daily':
                due_date = start_date + timedelta(days=i)
            elif recurrence_pattern == 'weekly':
                due_date = start_date + timedelta(weeks=i)
            elif recurrence_pattern == 'monthly':
                due_date = start_date + timedelta(days=30 * i)
            else:
                return {'success': False, 'error': f'Invalid recurrence pattern: {recurrence_pattern}'}
            
            # Create task with date in title
            task_title = f"{title_template} - {due_date.strftime('%Y-%m-%d')}"
            
            create_result = self.todo_create_task(
                user_id,
                task_title,
                list_id=list_id,
                due_date=due_date.isoformat(),
                importance=task_template.get('importance', 'normal'),
                body=task_template.get('body')
            )
            
            if create_result['success']:
                results['created'].append(task_title)
            else:
                results['failed'].append({'task': task_title, 'error': create_result.get('error')})
        
        results['message'] = f"Created {len(results['created'])} recurring tasks"
        
        return results
    
    # ==================== ADVANCED TOOLS ====================
    
    def planner_get_plan_progress(self, user_id: str, plan_id: str, **kwargs) -> Dict:
        """Get progress statistics for a Planner plan"""
        
        tasks_result = self.planner_list_tasks(user_id, plan_id=plan_id)
        
        if not tasks_result['success']:
            return tasks_result
        
        total = len(tasks_result['tasks'])
        completed = sum(1 for t in tasks_result['tasks'] if t['percent_complete'] == 100)
        in_progress = sum(1 for t in tasks_result['tasks'] if 0 < t['percent_complete'] < 100)
        not_started = sum(1 for t in tasks_result['tasks'] if t['percent_complete'] == 0)
        
        return {
            'success': True,
            'plan_id': plan_id,
            'total_tasks': total,
            'completed': completed,
            'in_progress': in_progress,
            'not_started': not_started,
            'completion_percentage': round((completed / total * 100), 2) if total > 0 else 0
        }
    
    def todo_export_tasks(self, user_id: str, format: str = 'json', **kwargs) -> Dict:
        """Export all To Do tasks"""
        
        # Get all lists
        lists_result = self.todo_list_lists(user_id)
        
        if not lists_result['success']:
            return lists_result
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'format': format,
            'lists': []
        }
        
        # Export each list
        for todo_list in lists_result['lists']:
            tasks_result = self.todo_list_tasks(user_id, todo_list['id'], show_completed=True)
            
            if tasks_result['success']:
                export_data['lists'].append({
                    'list_name': todo_list['name'],
                    'task_count': tasks_result['count'],
                    'tasks': tasks_result['tasks']
                })
        
        return {
            'success': True,
            'export_data': export_data
        }


# Create global instance
microsoft_todo_tools = MicrosoftTodoTools()

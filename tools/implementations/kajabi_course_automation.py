"""
Kajabi Course Automation Tools
Workarounds for course creation using webhooks, templates, and automation patterns

Note: Kajabi API v1 does not support direct course creation via API.
These tools provide alternative automation workflows.
"""
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime


class KajabiCourseAutomationError(Exception):
    """Custom exception for Kajabi course automation errors"""
    pass


class KajabiCourseAutomation:
    """Kajabi Course Automation - Workarounds for course creation"""
    
    def __init__(self):
        """Initialize Kajabi course automation"""
        self.base_url = "https://api.kajabi.com"
    
    def _get_headers(self, **kwargs) -> Dict[str, str]:
        """Get headers for API requests with credential injection"""
        api_key = kwargs.get('kajabi_api_key') or kwargs.get('api_key')
        
        if not api_key:
            raise KajabiCourseAutomationError("Kajabi API key not provided")
        
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling"""
        headers = self._get_headers(**kwargs)
        url = f"{self.base_url}{endpoint}"
        
        try:
            params = kwargs.get('params', {})
            data = kwargs.get('json')
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            
            if response.status_code == 204:
                return {'success': True, 'message': 'Operation completed successfully'}
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Kajabi API error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data.get('message', str(error_data))}"
            except:
                error_msg += f" - {e.response.text}"
            raise KajabiCourseAutomationError(error_msg)
        
        except requests.exceptions.RequestException as e:
            raise KajabiCourseAutomationError(f"Request failed: {str(e)}")
    
    # ==================== COURSE BLUEPRINT GENERATOR ====================
    
    def generate_course_blueprint(
        self,
        course_title: str,
        course_description: str,
        num_modules: int = 5,
        lessons_per_module: int = 3,
        include_assessments: bool = True,
        course_type: str = "online_course",
        pricing_model: str = "one_time",
        **kwargs
    ) -> Dict[str, Any]:
        """
        📋 COURSE BLUEPRINT: Generate detailed course structure blueprint
        
        Creates a comprehensive JSON blueprint that can be:
        1. Used as a manual creation guide in Kajabi UI
        2. Imported into course creation tools
        3. Shared with team members
        4. Saved as templates
        
        Args:
            course_title: Course name
            course_description: Course overview
            num_modules: Number of course modules (default: 5)
            lessons_per_module: Lessons per module (default: 3)
            include_assessments: Add quizzes/assessments (default: True)
            course_type: Type - 'online_course', 'coaching', 'membership'
            pricing_model: 'one_time', 'subscription', 'payment_plan'
        
        Returns:
            Detailed course blueprint with structure, content outline, settings
        """
        blueprint = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "blueprint_version": "1.0",
                "api_note": "⚠️ Kajabi API does not support direct course creation. Use this blueprint to create course manually in Kajabi."
            },
            "course": {
                "title": course_title,
                "description": course_description,
                "type": course_type,
                "status": "draft",
                "pricing": {
                    "model": pricing_model,
                    "suggested_price": 997 if pricing_model == "one_time" else 97,
                    "currency": "USD"
                }
            },
            "structure": {
                "total_modules": num_modules,
                "total_lessons": num_modules * lessons_per_module,
                "total_assessments": num_modules if include_assessments else 0
            },
            "modules": []
        }
        
        # Generate module structure
        for module_num in range(1, num_modules + 1):
            module = {
                "module_number": module_num,
                "title": f"Module {module_num}: {self._generate_module_title(course_title, module_num)}",
                "description": f"This module covers key concepts for {course_title}",
                "lessons": []
            }
            
            # Generate lessons for this module
            for lesson_num in range(1, lessons_per_module + 1):
                lesson = {
                    "lesson_number": lesson_num,
                    "title": f"Lesson {lesson_num}: {self._generate_lesson_title(module_num, lesson_num)}",
                    "content_type": self._suggest_content_type(lesson_num),
                    "duration_minutes": 15,
                    "resources": []
                }
                module["lessons"].append(lesson)
            
            # Add assessment if enabled
            if include_assessments:
                module["assessment"] = {
                    "type": "quiz",
                    "title": f"Module {module_num} Assessment",
                    "passing_score": 80,
                    "question_count": 5
                }
            
            blueprint["modules"].append(module)
        
        # Add implementation instructions
        blueprint["implementation_instructions"] = {
            "step_1": "Log into Kajabi dashboard",
            "step_2": f"Create new {course_type} product",
            "step_3": f"Add {num_modules} modules using this blueprint",
            "step_4": f"Create {num_modules * lessons_per_module} lessons following structure",
            "step_5": "Configure pricing and access settings",
            "step_6": "Publish course when content is complete",
            "webhook_automation": "Use kajabi_setup_course_webhook to automate member enrollment"
        }
        
        # Add checklist
        blueprint["creation_checklist"] = [
            {"task": "Create product in Kajabi", "completed": False},
            {"task": "Add course modules", "completed": False},
            {"task": "Upload lesson content", "completed": False},
            {"task": "Create assessments", "completed": False},
            {"task": "Set pricing", "completed": False},
            {"task": "Configure sales page", "completed": False},
            {"task": "Setup email sequences", "completed": False},
            {"task": "Test enrollment flow", "completed": False},
            {"task": "Publish course", "completed": False}
        ]
        
        return {
            "success": True,
            "blueprint": blueprint,
            "export_options": {
                "save_to_file": "Save this JSON to use as template",
                "share_with_team": "Share blueprint with course creators",
                "import_instructions": "Follow implementation_instructions to create in Kajabi"
            }
        }
    
    def _generate_module_title(self, course_title: str, module_num: int) -> str:
        """Generate smart module title"""
        titles = [
            "Foundation & Getting Started",
            "Core Concepts & Strategies",
            "Advanced Techniques",
            "Implementation & Practice",
            "Mastery & Next Steps"
        ]
        if module_num <= len(titles):
            return titles[module_num - 1]
        return f"Section {module_num}"
    
    def _generate_lesson_title(self, module_num: int, lesson_num: int) -> str:
        """Generate lesson title placeholder"""
        return f"Key Concept {lesson_num}"
    
    def _suggest_content_type(self, lesson_num: int) -> str:
        """Suggest content type for lesson"""
        types = ["video", "video", "text", "video", "downloadable"]
        return types[(lesson_num - 1) % len(types)]
    
    # ==================== WEBHOOK AUTOMATION ====================
    
    def setup_course_webhook(
        self,
        webhook_url: str,
        events: Optional[List[str]] = None,
        course_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        🔗 WEBHOOK AUTOMATION: Setup webhook for course enrollment automation
        
        Creates webhook to automate course-related actions:
        - Auto-enroll members when they purchase
        - Send welcome emails with course access
        - Trigger integrations (Zapier, Make.com, etc.)
        
        Args:
            webhook_url: Your webhook endpoint URL
            events: List of events to listen for (default: purchase events)
            course_id: Specific course to monitor (optional)
        
        Returns:
            Webhook configuration with automation instructions
        """
        if not events:
            events = [
                "offer.purchased",
                "member.created",
                "assessment.completed",
                "course.completed"
            ]
        
        # Create webhook via Kajabi API
        webhook_data = {
            "url": webhook_url,
            "events": events,
            "active": True
        }
        
        try:
            result = self._make_request('POST', '/v1/webhooks', json=webhook_data, **kwargs)
            
            return {
                "success": True,
                "webhook_id": result.get('data', {}).get('id'),
                "webhook_url": webhook_url,
                "monitored_events": events,
                "automation_examples": {
                    "offer_purchased": "Auto-grant course access when purchase completes",
                    "member_created": "Send custom welcome email with course instructions",
                    "assessment_completed": "Award certificates or trigger next module unlock",
                    "course_completed": "Send completion certificate and upsell next course"
                },
                "integration_options": [
                    "Zapier - Connect to 5000+ apps",
                    "Make.com - Advanced workflow automation",
                    "n8n - Self-hosted automation",
                    "Custom webhook handler - Build your own"
                ],
                "next_steps": [
                    "Test webhook with Kajabi test events",
                    "Build webhook handler to process events",
                    "Setup automation workflows in integration platform",
                    "Monitor webhook logs for debugging"
                ]
            }
        except Exception as e:
            raise KajabiCourseAutomationError(f"Failed to create webhook: {str(e)}")
    
    # ==================== BULK COURSE ACCESS MANAGEMENT ====================
    
    def bulk_enroll_from_csv(
        self,
        course_id: str,
        csv_data: str,
        offer_id: Optional[str] = None,
        dry_run: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        📊 BULK ENROLLMENT: Enroll multiple members from CSV
        
        Automates mass enrollment for course launches or migrations.
        CSV format: email,name,custom_field1,custom_field2
        
        Args:
            course_id: Target course ID
            csv_data: CSV string with member data
            offer_id: Specific offer to use (optional)
            dry_run: Preview only, don't execute (default: True)
        
        Returns:
            Enrollment summary with success/failure counts
        """
        # Parse CSV
        lines = csv_data.strip().split('\n')
        headers = lines[0].split(',')
        members = [dict(zip(headers, line.split(','))) for line in lines[1:]]
        
        if dry_run:
            return {
                "success": True,
                "mode": "DRY RUN - Preview Only",
                "total_members": len(members),
                "course_id": course_id,
                "offer_id": offer_id,
                "sample_members": members[:5],
                "preview": {
                    "would_enroll": len(members),
                    "estimated_time": f"{len(members) * 2} seconds",
                    "api_calls": len(members)
                },
                "next_step": "Set dry_run=False to execute enrollment"
            }
        
        # Execute enrollment
        results = {
            "enrolled": [],
            "failed": [],
            "skipped": []
        }
        
        for member in members:
            email = member.get('email')
            
            # Check if member exists
            try:
                search_result = self._make_request(
                    'GET',
                    '/v1/members/search',
                    params={'query': email},
                    **kwargs
                )
                
                members_data = search_result.get('data', [])
                if not members_data:
                    results["failed"].append({
                        "email": email,
                        "reason": "Member not found - create member first"
                    })
                    continue
                
                member_id = members_data[0]['id']
                
                # Grant course access
                grant_result = self._make_request(
                    'POST',
                    '/v1/member_access',
                    json={
                        'member_id': member_id,
                        'product_id': course_id,
                        'offer_id': offer_id
                    },
                    **kwargs
                )
                
                results["enrolled"].append({
                    "email": email,
                    "member_id": member_id,
                    "status": "success"
                })
                
            except Exception as e:
                results["failed"].append({
                    "email": email,
                    "reason": str(e)
                })
        
        return {
            "success": True,
            "summary": {
                "total_processed": len(members),
                "enrolled": len(results["enrolled"]),
                "failed": len(results["failed"]),
                "skipped": len(results["skipped"])
            },
            "details": results
        }
    
    # ==================== COURSE TEMPLATE LIBRARY ====================
    
    def get_course_templates(
        self,
        category: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        📚 TEMPLATE LIBRARY: Get pre-built course templates
        
        Returns course blueprints for common course types that can be
        customized and used to create courses in Kajabi.
        
        Args:
            category: Filter by category (optional)
                - 'online_course'
                - 'membership'
                - 'coaching'
                - 'mini_course'
        
        Returns:
            List of course templates with structure and content ideas
        """
        templates = {
            "online_course": {
                "name": "Complete Online Course Template",
                "description": "Full-featured course with 6 modules, assessments, and resources",
                "modules": 6,
                "lessons_per_module": 4,
                "duration_weeks": 8,
                "includes": ["Video lessons", "Downloadable resources", "Quizzes", "Community access"],
                "pricing": {"model": "one_time", "suggested": 997}
            },
            "membership": {
                "name": "Monthly Membership Template",
                "description": "Recurring membership with weekly content releases",
                "modules": 12,
                "lessons_per_module": 4,
                "duration_weeks": 52,
                "includes": ["Weekly videos", "Monthly workshops", "Community", "Resource library"],
                "pricing": {"model": "subscription", "suggested": 97}
            },
            "coaching": {
                "name": "Group Coaching Program",
                "description": "12-week coaching program with live calls and accountability",
                "modules": 12,
                "lessons_per_module": 2,
                "duration_weeks": 12,
                "includes": ["Weekly group calls", "Worksheets", "Private community", "Email support"],
                "pricing": {"model": "payment_plan", "suggested": 2997}
            },
            "mini_course": {
                "name": "Quick Win Mini Course",
                "description": "Fast-paced course for immediate results",
                "modules": 3,
                "lessons_per_module": 3,
                "duration_weeks": 2,
                "includes": ["Short videos", "Action guides", "Email sequence"],
                "pricing": {"model": "one_time", "suggested": 97}
            }
        }
        
        if category:
            if category in templates:
                return {
                    "success": True,
                    "template": templates[category],
                    "usage": "Use this template with generate_course_blueprint to create detailed structure"
                }
            else:
                return {
                    "success": False,
                    "error": f"Template category '{category}' not found",
                    "available_categories": list(templates.keys())
                }
        
        return {
            "success": True,
            "templates": templates,
            "usage": "Choose a template and use generate_course_blueprint with these parameters"
        }


# ============================================================================
# TOOL FUNCTIONS (Exported for registry)
# ============================================================================

def kajabi_generate_course_blueprint(**kwargs):
    """Generate detailed course blueprint"""
    automation = KajabiCourseAutomation()
    return automation.generate_course_blueprint(**kwargs)


def kajabi_setup_course_webhook(**kwargs):
    """Setup webhook for course automation"""
    automation = KajabiCourseAutomation()
    return automation.setup_course_webhook(**kwargs)


def kajabi_bulk_enroll_from_csv(**kwargs):
    """Bulk enroll members from CSV"""
    automation = KajabiCourseAutomation()
    return automation.bulk_enroll_from_csv(**kwargs)


def kajabi_get_course_templates(**kwargs):
    """Get pre-built course templates"""
    automation = KajabiCourseAutomation()
    return automation.get_course_templates(**kwargs)

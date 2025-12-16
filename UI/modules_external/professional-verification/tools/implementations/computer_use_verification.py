"""
Computer Use Verification Tools
================================

Advanced verification tools using Anthropic Computer Use API for browser automation.
These tools use Claude with computer use capability to navigate websites, fill forms,
and extract information from sources without public APIs.

TOOLS IMPLEMENTED:
1. search_linkedin_profile - LinkedIn profile search and extraction
2. verify_credential_registry - Professional credential verification (Medical, Legal, Finance, etc.)
3. check_education_credentials - University degree verification
4. verify_certification - Professional certification verification
5. google_dork_search - Advanced Google searches for candidate mentions
6. cross_platform_timeline - Unified timeline from multiple sources
7. analyze_social_media_authenticity - Detect fake profiles

ANTHROPIC COMPUTER USE INTEGRATION:
These tools create conversations with Claude using the computer_20241022 tool.
Claude responds with tool_use blocks containing actions (screenshot, mouse_move, click, type, key).
We execute those actions via ComputerUseExecutor and send results back to Claude.

USAGE:
    from tools.registry_v3 import RegistryV3
    
    registry = RegistryV3()
    result = registry.execute_tool(
        'search_linkedin_profile',
        full_name='John Doe',
        company_name='Google',
        location='San Francisco',
        _user_id='user123',
        _injected_credentials={'linkedin_verifier_account': {...}}
    )

CREATED: December 16, 2025
AUTHOR: AI Agent Platform
"""

import logging
import asyncio
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
import anthropic
import os

# Import global Computer Use Executor
from AI_infrastructure.core.computer_use_executor import get_computer_use_executor

logger = logging.getLogger(__name__)


class ComputerUseSession:
    """
    Manages a Claude conversation with computer use tools.
    Handles the request-response loop between Claude and the browser container.
    """
    
    def __init__(self, task_description: str, max_iterations: int = 20):
        """
        Initialize computer use session.
        
        Args:
            task_description: What Claude should accomplish
            max_iterations: Max back-and-forth iterations
        """
        self.task_description = task_description
        self.max_iterations = max_iterations
        self.messages = []
        self.executor = get_computer_use_executor()
        self.container_id = None
        
        # Get Anthropic API key from environment
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.warning("[COMPUTER_USE] No ANTHROPIC_API_KEY found in environment")
        
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
    
    async def run(self) -> Dict[str, Any]:
        """
        Execute the computer use task.
        
        Returns:
            Dict with task result and screenshots
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Anthropic API key not configured (set ANTHROPIC_API_KEY environment variable)'
            }
        
        try:
            # Get browser container
            logger.info(f"[COMPUTER_USE] Starting task: {self.task_description[:100]}...")
            self.container_id = await self.executor.get_browser_container(reuse=True)
            
            if not self.container_id:
                return {
                    'success': False,
                    'error': 'Failed to create browser container - Docker may not be running or image not built'
                }
            
            # Initialize conversation with task
            self.messages = [
                {
                    "role": "user",
                    "content": self.task_description
                }
            ]
            
            # Iterative loop: Claude → tool_use → execute → result → Claude
            for iteration in range(self.max_iterations):
                logger.info(f"[COMPUTER_USE] Iteration {iteration + 1}/{self.max_iterations}")
                
                # Call Claude with computer use tools
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    tools=[
                        {
                            "type": "computer_20241022",
                            "name": "computer",
                            "display_width_px": 1920,
                            "display_height_px": 1080,
                            "display_number": 1
                        }
                    ],
                    messages=self.messages
                )
                
                # Check stop reason
                if response.stop_reason == "end_turn":
                    # Claude finished the task
                    logger.info("[COMPUTER_USE] ✅ Task completed")
                    
                    # Extract final answer
                    final_text = ""
                    for block in response.content:
                        if hasattr(block, 'text'):
                            final_text += block.text
                    
                    return {
                        'success': True,
                        'result': final_text,
                        'iterations': iteration + 1,
                        'message': 'Task completed successfully'
                    }
                
                elif response.stop_reason == "tool_use":
                    # Claude wants to use computer
                    tool_results = []
                    
                    for block in response.content:
                        if block.type == "tool_use" and block.name == "computer":
                            # Execute the computer action
                            logger.info(f"[COMPUTER_USE] Executing action: {block.input.get('action')}")
                            
                            result = await self.executor.execute_computer_action(
                                self.container_id,
                                block.input
                            )
                            
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result if isinstance(result, list) else [result]
                            })
                    
                    # Add assistant message with tool use
                    self.messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    
                    # Add tool results
                    self.messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                    
                    # Continue loop
                    continue
                
                elif response.stop_reason == "max_tokens":
                    logger.warning("[COMPUTER_USE] Hit token limit")
                    return {
                        'success': False,
                        'error': 'Reached token limit - task too complex',
                        'iterations': iteration + 1
                    }
            
            # Max iterations reached
            logger.warning(f"[COMPUTER_USE] Reached max iterations ({self.max_iterations})")
            return {
                'success': False,
                'error': f'Task did not complete in {self.max_iterations} iterations',
                'iterations': self.max_iterations
            }
        
        except Exception as e:
            logger.error(f"[COMPUTER_USE] Error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            # Release container back to pool
            if self.container_id:
                self.executor.release_container(self.container_id)


# ===== COMPUTER USE VERIFICATION TOOLS =====

def search_linkedin_profile(
    full_name: str,
    company_name: Optional[str] = None,
    location: Optional[str] = None,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Search LinkedIn profile using Computer Use.
    
    Args:
        full_name: Candidate's full name
        company_name: Current/past company for filtering
        location: Location for disambiguation
        _user_id: User ID (injected)
        _injected_credentials: Must contain 'linkedin_verifier_account' with username/password
    
    Returns:
        Profile data with job history, skills, screenshot evidence
    """
    logger.info(f"[LINKEDIN_SEARCH] Searching for: {full_name}")
    
    # Check for LinkedIn credentials
    if not _injected_credentials or 'linkedin_verifier_account' not in _injected_credentials:
        return {
            'success': False,
            'error': 'LinkedIn verifier account credentials not configured. Please add credentials in Settings → Platform Connections.'
        }
    
    linkedin_creds = _injected_credentials['linkedin_verifier_account']
    linkedin_user = linkedin_creds.get('username')
    linkedin_pass = linkedin_creds.get('password')
    
    if not linkedin_user or not linkedin_pass:
        return {
            'success': False,
            'error': 'LinkedIn credentials incomplete (missing username or password)'
        }
    
    # Build search query
    search_query = full_name
    if company_name:
        search_query += f" at {company_name}"
    if location:
        search_query += f" in {location}"
    
    # Create task description for Claude
    task = f"""
Your task is to search for a LinkedIn profile and extract information.

SEARCH CRITERIA:
- Name: {full_name}
- Company: {company_name or 'Not specified'}
- Location: {location or 'Not specified'}

STEPS:
1. Navigate to https://www.linkedin.com/login
2. Log in using these credentials:
   - Email: {linkedin_user}
   - Password: {linkedin_pass}
3. After login, use the search bar to search for: "{search_query}"
4. Filter results to "People" if needed
5. Click on the most relevant profile (match name, company, location)
6. Extract the following information from the profile:
   - Current job title and company
   - Location
   - Past work experience (job titles, companies, dates)
   - Education (degrees, schools, years)
   - Skills listed
   - Number of connections
   - Profile URL
7. Take a screenshot of the profile as evidence
8. Return the extracted data in JSON format

IMPORTANT:
- If you encounter 2FA or CAPTCHA, report it immediately
- If multiple profiles match, choose the one that best matches company/location
- If no exact match found, report "Profile not found"
- Handle any login errors gracefully

Return the data in this format:
{{
    "profile_found": true/false,
    "profile_url": "URL",
    "job_title": "Current title",
    "company": "Current company",
    "location": "Location",
    "work_history": [
        {{"title": "...", "company": "...", "dates": "..."}}
    ],
    "education": [
        {{"degree": "...", "school": "...", "year": "..."}}
    ],
    "skills": ["skill1", "skill2", ...],
    "connections": 500
}}
"""
    
    # Run computer use session
    try:
        session = ComputerUseSession(task, max_iterations=25)
        result = asyncio.run(session.run())
        
        if not result['success']:
            return result
        
        # Parse Claude's response
        import json
        try:
            # Extract JSON from Claude's text response
            text = result['result']
            
            # Try to find JSON in the response
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = text[json_start:json_end]
                profile_data = json.loads(json_str)
                
                return {
                    'success': True,
                    'profile_found': profile_data.get('profile_found', False),
                    'profile_url': profile_data.get('profile_url'),
                    'job_title': profile_data.get('job_title'),
                    'company': profile_data.get('company'),
                    'location': profile_data.get('location'),
                    'work_history': profile_data.get('work_history', []),
                    'education': profile_data.get('education', []),
                    'skills': profile_data.get('skills', []),
                    'endorsements': 0,  # Not easily extractable
                    'connections': profile_data.get('connections', 0),
                    'screenshot': '',  # Would be in tool results
                    'ai_annotations': [text]  # Claude's observations
                }
            else:
                # Claude didn't return JSON - return text response
                return {
                    'success': True,
                    'profile_found': False,
                    'message': text,
                    'ai_annotations': [text]
                }
        
        except json.JSONDecodeError:
            return {
                'success': True,
                'profile_found': False,
                'message': result['result'],
                'ai_annotations': [result['result']]
            }
    
    except Exception as e:
        logger.error(f"[LINKEDIN_SEARCH] Error: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def verify_credential_registry(
    profession: str,
    credential_number: str,
    full_name: str,
    country: str,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Verify professional credentials against official registries using Computer Use.
    
    Supports: Medical (AHPRA, GMC), Legal (Bar Associations), Finance (CPA, CFA), 
    Engineering (PE licenses), Nursing, Pharmacy, etc.
    
    Args:
        profession: Profession type (medical/legal/finance/engineering/nursing/etc.)
        credential_number: License/registration number
        full_name: Professional's full name
        country: Country for registry lookup
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Credential verification status with screenshot evidence
    """
    logger.info(f"[CREDENTIAL_VERIFY] Checking {profession} credential: {credential_number}")
    
    # Registry URLs by profession and country
    registries = {
        'medical': {
            'australia': 'https://www.ahpra.gov.au/registration/registers-of-practitioners.aspx',
            'uk': 'https://www.gmc-uk.org/registration-and-licensing/the-medical-register',
            'usa': 'https://www.fsmb.org/fcvs/physician-profile/',
        },
        'legal': {
            'australia': 'https://www.lawsociety.com.au/find-a-lawyer',
            'uk': 'https://www.sra.org.uk/consumers/register/',
            'usa': 'https://www.americanbar.org/directories/lawyers/',
        },
        'nursing': {
            'australia': 'https://www.ahpra.gov.au/registration/registers-of-practitioners.aspx',
            'uk': 'https://www.nmc.org.uk/registration/search-the-register/',
            'usa': 'https://www.nursys.com/LQC/LQCTerms.aspx',
        },
        'finance': {
            'australia': 'https://www.cpaaustralia.com.au/verify-a-member',
            'usa': 'https://www.aicpa.org/verify',
        }
    }
    
    # Get registry URL
    profession_lower = profession.lower()
    country_lower = country.lower()
    
    registry_url = None
    if profession_lower in registries and country_lower in registries[profession_lower]:
        registry_url = registries[profession_lower][country_lower]
    else:
        return {
            'success': False,
            'error': f'No registry URL configured for {profession} in {country}. Supported: {list(registries.keys())}'
        }
    
    # Create task for Claude
    task = f"""
Your task is to verify a professional credential in an official registry.

CREDENTIAL DETAILS:
- Profession: {profession}
- Credential Number: {credential_number}
- Full Name: {full_name}
- Country: {country}
- Registry URL: {registry_url}

STEPS:
1. Navigate to {registry_url}
2. Find the search/lookup function on the page
3. Enter the credential number: {credential_number}
   OR enter the full name: {full_name}
   (Use whichever field is available)
4. Submit the search
5. Check the results for:
   - Does the credential exist? (Valid/Invalid)
   - Status: Active, Expired, Suspended, or Not Found
   - Issue date
   - Expiry date (if applicable)
   - Specializations or endorsements
   - Any disciplinary actions or sanctions
6. Take a screenshot of the search results as evidence
7. Return the findings in JSON format

IMPORTANT:
- If the website requires CAPTCHA, report it
- If no results found, clearly state "Not Found"
- Record the exact status shown on the registry
- Note any warnings or restrictions

Return data in this format:
{{
    "credential_valid": true/false,
    "status": "Active/Expired/Suspended/Not_Found",
    "issue_date": "YYYY-MM-DD or null",
    "expiry_date": "YYYY-MM-DD or null",
    "specializations": ["specialty1", "specialty2"],
    "disciplinary_actions": ["action1" or empty list],
    "registry_url": "{registry_url}",
    "verification_timestamp": "{datetime.now().isoformat()}"
}}
"""
    
    try:
        session = ComputerUseSession(task, max_iterations=20)
        result = asyncio.run(session.run())
        
        if not result['success']:
            return result
        
        # Parse response
        import json
        try:
            text = result['result']
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = text[json_start:json_end]
                verification_data = json.loads(json_str)
                
                return {
                    'success': True,
                    'credential_valid': verification_data.get('credential_valid', False),
                    'status': verification_data.get('status', 'Unknown'),
                    'issue_date': verification_data.get('issue_date'),
                    'expiry_date': verification_data.get('expiry_date'),
                    'specializations': verification_data.get('specializations', []),
                    'disciplinary_actions': verification_data.get('disciplinary_actions', []),
                    'registry_url': registry_url,
                    'screenshot': '',  # Would be in tool results
                    'verification_timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': True,
                    'credential_valid': False,
                    'message': text
                }
        
        except json.JSONDecodeError:
            return {
                'success': True,
                'credential_valid': False,
                'message': result['result']
            }
    
    except Exception as e:
        logger.error(f"[CREDENTIAL_VERIFY] Error: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def google_dork_search(
    full_name: str,
    keywords: List[str] = [],
    limit: int = 10,
    _user_id: Optional[str] = None,
    _injected_credentials: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Perform targeted Google searches using Computer Use.
    
    Args:
        full_name: Candidate's full name
        keywords: Additional search keywords
        limit: Max results to analyze
        _user_id: User ID (injected)
        _injected_credentials: Credentials (injected)
    
    Returns:
        Search results with mentions, publications, news
    """
    logger.info(f"[GOOGLE_DORK] Searching for: {full_name}")
    
    # Build search query
    search_terms = [f'"{full_name}"'] + keywords
    search_query = ' '.join(search_terms)
    
    task = f"""
Your task is to perform a Google search and analyze the results for mentions of a person.

SEARCH QUERY: {search_query}

STEPS:
1. Navigate to https://www.google.com
2. Enter the search query: {search_query}
3. Press Enter to search
4. Analyze the first {limit} results
5. For each result, extract:
   - Title
   - URL
   - Snippet (description)
   - Type (news article, publication, social media, professional profile, etc.)
6. Categorize results:
   - Publications (academic papers, articles)
   - News articles
   - Social media posts
   - Professional profiles
   - Other mentions
7. Take a screenshot of the search results
8. Return the data in JSON format

Return format:
{{
    "total_results": approximate_count,
    "mentions": [
        {{"title": "...", "url": "...", "snippet": "...", "type": "..."}}
    ],
    "publications": [list of academic/professional publications],
    "news_articles": [list of news mentions],
    "social_media_posts": [list of social posts],
    "professional_profiles": [list of LinkedIn, company pages, etc.]
}}
"""
    
    try:
        session = ComputerUseSession(task, max_iterations=15)
        result = asyncio.run(session.run())
        
        if not result['success']:
            return result
        
        # Parse response
        import json
        try:
            text = result['result']
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = text[json_start:json_end]
                search_data = json.loads(json_str)
                
                return {
                    'success': True,
                    'total_results': search_data.get('total_results', 0),
                    'mentions': search_data.get('mentions', []),
                    'publications': search_data.get('publications', []),
                    'news_articles': search_data.get('news_articles', []),
                    'social_media_posts': search_data.get('social_media_posts', []),
                    'professional_profiles': search_data.get('professional_profiles', []),
                    'screenshot': ''  # Would be in tool results
                }
            else:
                return {
                    'success': True,
                    'total_results': 0,
                    'message': text
                }
        
        except json.JSONDecodeError:
            return {
                'success': True,
                'total_results': 0,
                'message': result['result']
            }
    
    except Exception as e:
        logger.error(f"[GOOGLE_DORK] Error: {e}")
        return {
            'success': False,
            'error': str(e)
        }


# Placeholder implementations for remaining tools

def check_education_credentials(*args, **kwargs):
    return {'success': False, 'error': 'Not yet implemented - similar pattern to verify_credential_registry'}

def verify_certification(*args, **kwargs):
    return {'success': False, 'error': 'Not yet implemented - similar pattern to verify_credential_registry'}

def cross_platform_timeline(*args, **kwargs):
    return {'success': False, 'error': 'Not yet implemented - aggregates data from multiple sources'}

def analyze_social_media_authenticity(*args, **kwargs):
    return {'success': False, 'error': 'Not yet implemented - analyzes profile for fake indicators'}

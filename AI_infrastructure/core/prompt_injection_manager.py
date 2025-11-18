"""
Prompt Injection Manager - Dynamic prompt library system

Allows users to inject custom prompts from a library into the system prompt.
Supports:
- Quick action prompts (lightning strike button)
- Prompt library selection (dropdown/modal)
- Custom user prompts
- Per-user prompt preferences

Usage:
    manager = PromptInjectionManager()
    
    # Get quick action prompt
    prompt = manager.get_quick_action('expert_coder')
    
    # Inject into system prompt
    final_prompt = manager.inject_prompts(
        base_prompt=system_prompt,
        quick_actions=['expert_coder', 'detailed_analysis'],
        library_prompts=['sql_expert'],
        custom_prompt="Focus on performance optimization"
    )
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from AI_infrastructure.shared.database_utils import get_database_connection


class PromptInjectionManager:
    """Manages dynamic prompt injection from library and user preferences"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the Prompt Injection Manager
        
        Args:
            db_path: Path to ai_infrastructure.db (auto-detected if not provided)
        """
        if db_path is None:
            from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
            db_path = get_ai_infrastructure_db_path()
        
        self.db_path = str(db_path)
        self._ensure_tables()
        
        # Load built-in prompt library
        self.quick_actions = self._load_quick_actions()
        self.prompt_library = self._load_prompt_library()
    
    def _ensure_tables(self):
        """Create prompt-related tables if they don't exist"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Table for prompt library (replaces user_custom_prompts)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                workspace_id INTEGER,
                name VARCHAR(200) NOT NULL,
                category VARCHAR(50) NOT NULL,
                type VARCHAR(20) NOT NULL DEFAULT 'quick_action',
                description TEXT,
                prompt_text TEXT NOT NULL,
                tags TEXT,
                visibility VARCHAR(20) NOT NULL DEFAULT 'private',
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for prompt_library performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_library_user_id 
            ON prompt_library(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_library_workspace_id 
            ON prompt_library(workspace_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_library_category 
            ON prompt_library(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_library_visibility 
            ON prompt_library(visibility)
        """)
        
        # Table for user's prompt preferences (saved combinations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_prompt_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                preference_name TEXT NOT NULL,
                quick_actions TEXT,
                library_prompts TEXT,
                custom_prompt TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_quick_actions(self) -> Dict[str, Dict[str, str]]:
        """
        Load built-in quick action prompts (lightning strike buttons)
        
        These are short, focused prompt modifiers that change AI behavior
        """
        return {
            # CODING & DEVELOPMENT
            'expert_coder': {
                'name': 'Expert Coder',
                'icon': '⚡',
                'category': 'development',
                'prompt': """CODING EXPERT MODE ACTIVATED:
- Write production-ready code with error handling
- Include comprehensive docstrings and type hints
- Follow best practices and design patterns
- Optimize for readability and maintainability
- Add inline comments for complex logic"""
            },
            
            'code_reviewer': {
                'name': 'Code Reviewer',
                'icon': '🔍',
                'category': 'development',
                'prompt': """CODE REVIEW MODE ACTIVATED:
- Analyze code for bugs, security issues, and performance problems
- Check for code smells and anti-patterns
- Suggest refactoring opportunities
- Verify error handling and edge cases
- Provide specific line-by-line feedback"""
            },
            
            'debugger': {
                'name': 'Debugger',
                'icon': '🐛',
                'category': 'development',
                'prompt': """DEBUG MODE ACTIVATED:
- Systematically analyze the issue step-by-step
- Check error messages, stack traces, and logs
- Verify data flow and state at each step
- Test edge cases and boundary conditions
- Provide detailed debugging steps"""
            },
            
            # ANALYSIS & THINKING
            'detailed_analysis': {
                'name': 'Detailed Analysis',
                'icon': '📊',
                'category': 'analysis',
                'prompt': """DETAILED ANALYSIS MODE ACTIVATED:
- Provide comprehensive, in-depth analysis
- Break down complex topics into components
- Use data and evidence to support conclusions
- Consider multiple perspectives and scenarios
- Include visualizations or tables where helpful"""
            },
            
            'step_by_step': {
                'name': 'Step by Step',
                'icon': '📝',
                'category': 'analysis',
                'prompt': """STEP-BY-STEP MODE ACTIVATED:
- Break down the task into clear, numbered steps
- Explain the reasoning for each step
- Show intermediate results
- Verify each step before proceeding
- Provide a summary at the end"""
            },
            
            'critical_thinking': {
                'name': 'Critical Thinking',
                'icon': '🧠',
                'category': 'analysis',
                'prompt': """CRITICAL THINKING MODE ACTIVATED:
- Question assumptions and challenge conventional wisdom
- Identify logical fallacies and weak arguments
- Consider alternative explanations
- Evaluate evidence quality and sources
- Acknowledge uncertainties and limitations"""
            },
            
            # DATA & SQL
            'sql_expert': {
                'name': 'SQL Expert',
                'icon': '🗄️',
                'category': 'data',
                'prompt': """SQL EXPERT MODE ACTIVATED:
- Write optimized, performant SQL queries
- Use proper indexing strategies
- Include query execution plans (EXPLAIN)
- Handle edge cases (NULL values, duplicates)
- Add comments explaining complex joins"""
            },
            
            'data_analyst': {
                'name': 'Data Analyst',
                'icon': '📈',
                'category': 'data',
                'prompt': """DATA ANALYSIS MODE ACTIVATED:
- Explore data patterns and trends
- Calculate relevant metrics and KPIs
- Identify anomalies and outliers
- Provide statistical insights
- Create visualizations to illustrate findings"""
            },
            
            # COMMUNICATION STYLES
            'concise': {
                'name': 'Concise',
                'icon': '⚡',
                'category': 'style',
                'prompt': """CONCISE MODE ACTIVATED:
- Provide brief, to-the-point responses
- Focus on essential information only
- Use bullet points for clarity
- Avoid unnecessary explanations
- Get straight to the answer"""
            },
            
            'eli5': {
                'name': 'ELI5 (Explain Like I\'m 5)',
                'icon': '🎈',
                'category': 'style',
                'prompt': """ELI5 MODE ACTIVATED:
- Explain concepts in simple, everyday language
- Use analogies and real-world examples
- Avoid technical jargon
- Break complex ideas into basic components
- Make it easy to understand"""
            },
            
            'professional': {
                'name': 'Professional',
                'icon': '💼',
                'category': 'style',
                'prompt': """PROFESSIONAL MODE ACTIVATED:
- Use formal business language
- Structure responses clearly with headings
- Focus on actionable recommendations
- Include relevant metrics and data
- Maintain a polished, executive tone"""
            },
            
            # BUSINESS & OPERATIONS
            'quote_assistant': {
                'name': 'Quote Assistant',
                'icon': '💰',
                'category': 'business',
                'prompt': """QUOTE ASSISTANT MODE ACTIVATED:
- Calculate accurate quotes with all cost factors
- Explain pricing breakdown clearly
- Consider turnaround time and urgency
- Check stock availability
- Provide alternative options if needed"""
            },
            
            'efficiency_optimizer': {
                'name': 'Efficiency Optimizer',
                'icon': '⚙️',
                'category': 'business',
                'prompt': """EFFICIENCY OPTIMIZATION MODE ACTIVATED:
- Identify bottlenecks and inefficiencies
- Suggest process improvements
- Calculate time and cost savings
- Prioritize high-impact changes
- Provide implementation steps"""
            },
            
            # CREATIVE & CONTENT
            'creative_writer': {
                'name': 'Creative Writer',
                'icon': '✍️',
                'category': 'creative',
                'prompt': """CREATIVE WRITING MODE ACTIVATED:
- Use engaging, vivid language
- Tell stories with clear narratives
- Include descriptive details
- Maintain consistent tone and style
- Make content memorable and impactful"""
            },
            
            'email_composer': {
                'name': 'Email Composer',
                'icon': '📧',
                'category': 'creative',
                'prompt': """EMAIL COMPOSITION MODE ACTIVATED:
- Write clear, professional emails
- Use appropriate greeting and closing
- Structure with clear subject and body
- Be concise but complete
- Include clear call-to-action if needed"""
            }
        }
    
    def _load_prompt_library(self) -> Dict[str, Dict[str, str]]:
        """
        Load extended prompt library (for dropdown/modal selection)
        
        These are longer, more specialized prompt enhancements
        """
        return {
            'system_architect': {
                'name': 'System Architect',
                'category': 'development',
                'prompt': """You are now operating as a System Architect.

Focus on:
- High-level system design and architecture patterns
- Scalability, reliability, and performance
- Technology stack selection and trade-offs
- Integration points and API design
- Security architecture and best practices
- Database schema design and data flow
- Deployment and infrastructure considerations

Provide architecture diagrams (in text/ASCII) where helpful."""
            },
            
            'security_analyst': {
                'name': 'Security Analyst',
                'category': 'development',
                'prompt': """You are now operating as a Security Analyst.

Focus on:
- Vulnerability assessment and threat modeling
- Authentication and authorization mechanisms
- Data encryption and protection strategies
- Input validation and sanitization
- Security best practices (OWASP Top 10)
- Compliance requirements (GDPR, PCI-DSS, etc.)
- Incident response and logging

Always consider: "How could this be exploited?" """
            },
            
            'business_intelligence': {
                'name': 'Business Intelligence Analyst',
                'category': 'data',
                'prompt': """You are now operating as a Business Intelligence Analyst.

Focus on:
- KPI definition and tracking
- Dashboard design and data visualization
- Trend analysis and forecasting
- Comparative analysis (YoY, MoM, etc.)
- Customer segmentation and cohort analysis
- Revenue optimization and cost reduction
- Actionable business insights

Always tie findings to business outcomes and ROI."""
            },
            
            'technical_writer': {
                'name': 'Technical Writer',
                'category': 'creative',
                'prompt': """You are now operating as a Technical Writer.

Focus on:
- Clear, structured documentation
- User guides and tutorials
- API documentation with examples
- Troubleshooting guides
- Installation and setup instructions
- Code comments and inline documentation
- Changelog and release notes

Write for both technical and non-technical audiences as needed."""
            },
            
            'performance_engineer': {
                'name': 'Performance Engineer',
                'category': 'development',
                'prompt': """You are now operating as a Performance Engineer.

Focus on:
- Performance profiling and bottleneck identification
- Query optimization and indexing strategies
- Caching strategies and implementation
- Load testing and capacity planning
- Memory management and garbage collection
- Network optimization and CDN usage
- Database query optimization

Provide specific metrics and benchmarks."""
            },
            
            'ux_consultant': {
                'name': 'UX Consultant',
                'category': 'creative',
                'prompt': """You are now operating as a UX (User Experience) Consultant.

Focus on:
- User journey mapping and flow analysis
- Information architecture and navigation
- Accessibility compliance (WCAG)
- Mobile-first and responsive design
- User feedback and testing insights
- Design system consistency
- Conversion optimization

Consider usability, accessibility, and user satisfaction."""
            }
        }
    
    def get_quick_action(self, action_key: str) -> Optional[str]:
        """Get a quick action prompt by key"""
        action = self.quick_actions.get(action_key)
        return action['prompt'] if action else None
    
    def get_library_prompt(self, prompt_key: str) -> Optional[str]:
        """Get a library prompt by key"""
        prompt = self.prompt_library.get(prompt_key)
        return prompt['prompt'] if prompt else None
    
    def get_user_custom_prompt(self, user_id: int, prompt_name: str) -> Optional[str]:
        """Get a user's custom prompt by name"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT prompt_text FROM prompt_library
            WHERE user_id = %s AND name = %s
            ORDER BY updated_at DESC LIMIT 1
        """, (user_id, prompt_name))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def inject_prompts(
        self,
        base_prompt: str,
        quick_actions: Optional[List[str]] = None,
        library_prompts: Optional[List[str]] = None,
        custom_prompt: Optional[str] = None,
        user_id: Optional[int] = None,
        user_custom_prompts: Optional[List[str]] = None
    ) -> str:
        """
        Inject prompts into the base system prompt
        
        Args:
            base_prompt: Base system prompt
            quick_actions: List of quick action keys to inject
            library_prompts: List of library prompt keys to inject
            custom_prompt: Free-form custom prompt text
            user_id: User ID for fetching user custom prompts
            user_custom_prompts: List of user custom prompt names
        
        Returns:
            Enhanced system prompt with injections
        """
        injections = []
        
        # Add quick actions
        if quick_actions:
            quick_action_text = "\n\n".join([
                self.get_quick_action(action) 
                for action in quick_actions 
                if self.get_quick_action(action)
            ])
            if quick_action_text:
                injections.append(f"\n\n{'='*80}\nQUICK ACTION MODIFIERS:\n{'='*80}\n{quick_action_text}")
        
        # Add library prompts
        if library_prompts:
            library_text = "\n\n".join([
                self.get_library_prompt(prompt_key)
                for prompt_key in library_prompts
                if self.get_library_prompt(prompt_key)
            ])
            if library_text:
                injections.append(f"\n\n{'='*80}\nSPECIALIZATION PROMPTS:\n{'='*80}\n{library_text}")
        
        # Add user custom prompts
        if user_id and user_custom_prompts:
            user_prompts_text = "\n\n".join([
                self.get_user_custom_prompt(user_id, prompt_name)
                for prompt_name in user_custom_prompts
                if self.get_user_custom_prompt(user_id, prompt_name)
            ])
            if user_prompts_text:
                injections.append(f"\n\n{'='*80}\nUSER CUSTOM PROMPTS:\n{'='*80}\n{user_prompts_text}")
        
        # Add free-form custom prompt
        if custom_prompt and custom_prompt.strip():
            injections.append(f"\n\n{'='*80}\nCUSTOM INSTRUCTIONS:\n{'='*80}\n{custom_prompt.strip()}")
        
        # Combine all injections
        if injections:
            return base_prompt + "".join(injections)
        else:
            return base_prompt
    
    def save_user_custom_prompt(
        self,
        user_id: int,
        name: str,
        prompt_text: str,
        category: Optional[str] = None,
        is_quick_action: bool = False
    ) -> int:
        """Save a user's custom prompt"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Convert is_quick_action to type field
        prompt_type = 'quick_action' if is_quick_action else 'full_prompt'
        
        cursor.execute("""
            INSERT INTO prompt_library (user_id, name, prompt_text, category, type, visibility)
            VALUES (%s, %s, %s, %s, %s, 'private')
        """, (user_id, name, prompt_text, category or 'custom', prompt_type))
        
        prompt_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return prompt_id
    
    def save_prompt_preference(
        self,
        user_id: int,
        preference_name: str,
        quick_actions: Optional[List[str]] = None,
        library_prompts: Optional[List[str]] = None,
        custom_prompt: Optional[str] = None
    ) -> int:
        """Save a user's prompt preference combination"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_prompt_preferences 
            (user_id, preference_name, quick_actions, library_prompts, custom_prompt)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            preference_name,
            json.dumps(quick_actions) if quick_actions else None,
            json.dumps(library_prompts) if library_prompts else None,
            custom_prompt
        ))
        
        pref_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return pref_id
    
    def get_prompt_preference(self, user_id: int, preference_name: str) -> Optional[Dict[str, Any]]:
        """Get a user's saved prompt preference"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT quick_actions, library_prompts, custom_prompt
            FROM user_prompt_preferences
            WHERE user_id = %s AND preference_name = %s
            ORDER BY created_at DESC LIMIT 1
        """, (user_id, preference_name))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'quick_actions': json.loads(row[0]) if row[0] else [],
                'library_prompts': json.loads(row[1]) if row[1] else [],
                'custom_prompt': row[2]
            }
        return None
    
    def list_quick_actions(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all quick actions, optionally filtered by category"""
        actions = []
        for key, action in self.quick_actions.items():
            if category is None or action['category'] == category:
                actions.append({
                    'key': key,
                    'name': action['name'],
                    'icon': action['icon'],
                    'category': action['category']
                })
        return actions
    
    def list_library_prompts(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all library prompts, optionally filtered by category"""
        prompts = []
        for key, prompt in self.prompt_library.items():
            if category is None or prompt['category'] == category:
                prompts.append({
                    'key': key,
                    'name': prompt['name'],
                    'category': prompt['category']
                })
        return prompts
    
    def list_user_custom_prompts(self, user_id: int) -> List[Dict[str, Any]]:
        """List all custom prompts for a user"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, category, type, created_at
            FROM prompt_library
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        prompts = []
        for row in cursor.fetchall():
            prompts.append({
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'is_quick_action': row[3] == 'quick_action',
                'type': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        return prompts


# Singleton instance
_prompt_manager = None

def get_prompt_manager() -> PromptInjectionManager:
    """Get the singleton PromptInjectionManager instance"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptInjectionManager()
    return _prompt_manager

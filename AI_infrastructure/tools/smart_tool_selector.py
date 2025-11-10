"""
Smart Tool Selector
===================

Strategically selects relevant tools based on user query using:
1. Category detection (Platform-based filtering)
2. Keyword matching
3. Priority ranking
4. Related tool expansion

Reduces tool set from 564 → 15-20 relevant tools
"""

import re
from typing import List, Dict, Set, Tuple

class SmartToolSelector:
    """
    Intelligent tool selection system that reduces cognitive load on AI
    by pre-filtering tools based on query analysis
    """
    
    def __init__(self, tool_registry):
        self.registry = tool_registry
        self.categories = self._load_categories()
        
    def _load_categories(self) -> Dict:
        """
        Define tool categories with keywords for fast matching
        """
        return {
            # Communication
            "email": {
                "priority": 1,
                "keywords": ["email", "send", "compose", "draft", "gmail", "message", "mail", "inbox"],
                "platforms": ["gmail"],
                "smart_tools": ["gmail_smart_compose_and_send", "gmail_smart_bulk_send_personalized"]
            },
            "messaging": {
                "priority": 1,
                "keywords": ["slack", "message", "chat", "channel", "dm", "notification"],
                "platforms": ["slack", "twilio"],
                "smart_tools": ["slack_smart_send_rich_message"]
            },
            
            # Google Workspace
            "documents": {
                "priority": 1,
                "keywords": ["document", "doc", "google docs", "write", "proposal", "report", "text"],
                "platforms": ["google_docs"],
                "smart_tools": ["google_docs_smart_create_from_markdown"]
            },
            "spreadsheets": {
                "priority": 1,
                "keywords": ["spreadsheet", "sheet", "excel", "data", "table", "csv", "google sheets"],
                "platforms": ["google_sheets"],
                "smart_tools": ["google_sheets_smart_create_with_data"]
            },
            "presentations": {
                "priority": 2,
                "keywords": ["slide", "presentation", "deck", "google slides"],
                "platforms": ["google_slides"],
                "smart_tools": []
            },
            "forms": {
                "priority": 2,
                "keywords": ["form", "survey", "questionnaire", "response", "google forms"],
                "platforms": ["google_forms"],
                "smart_tools": ["google_forms_smart_create"]
            },
            "drive": {
                "priority": 2,
                "keywords": ["drive", "file", "folder", "upload", "download", "storage", "share"],
                "platforms": ["google_drive"],
                "smart_tools": []
            },
            "calendar": {
                "priority": 1,
                "keywords": ["calendar", "event", "meeting", "schedule", "appointment"],
                "platforms": ["google_calendar"],
                "smart_tools": []
            },
            
            # E-commerce & Payments
            "ecommerce": {
                "priority": 1,
                "keywords": ["product", "inventory", "order", "woocommerce", "store", "shop", "customer"],
                "platforms": ["woocommerce"],
                "smart_tools": ["woocommerce_smart_create_product", "woocommerce_smart_bulk_import"]
            },
            "payments": {
                "priority": 1,
                "keywords": ["payment", "stripe", "paypal", "charge", "refund", "invoice", "subscription"],
                "platforms": ["stripe", "paypal"],
                "smart_tools": []
            },
            
            # Calculators
            "calculators": {
                "priority": 1,
                "keywords": ["quote", "calculate", "price", "cost", "business cards", "flyers", "printing"],
                "platforms": [],
                "smart_tools": [],
                "tools": [
                    "calculate_business_cards",
                    "calculate_flyers", 
                    "calculate_perfect_bound_books",
                    "calculate_corflute_signs",
                    "calculate_booklets",
                    "get_stock_list",
                    "get_calculator_requirements"
                ]
            },
            
            # Cloud & Infrastructure
            "cloud": {
                "priority": 2,
                "keywords": ["cloud", "deploy", "server", "container", "cloud run", "hosting"],
                "platforms": ["google_cloud_run", "cloudflare"],
                "smart_tools": []
            },
            "database": {
                "priority": 2,
                "keywords": ["database", "supabase", "sql", "query", "table", "row"],
                "platforms": ["supabase"],
                "smart_tools": []
            },
            
            # Social & Media
            "social": {
                "priority": 2,
                "keywords": ["instagram", "social", "post", "story", "follower"],
                "platforms": ["instagram"],
                "smart_tools": []
            },
            "media": {
                "priority": 2,
                "keywords": ["convert", "transcribe", "audio", "video", "file format"],
                "platforms": ["cloudconvert", "assemblyai"],
                "smart_tools": []
            },
            
            # Developer Tools
            "dev_tools": {
                "priority": 2,
                "keywords": ["github", "repository", "code", "commit", "ngrok", "tunnel"],
                "platforms": ["github", "ngrok"],
                "smart_tools": []
            },
            
            # Task Management (AI's personal tasks)
            "task_management": {
                "priority": 1,
                "keywords": ["remember", "task", "todo", "remind", "pending", "follow up", "track"],
                "platforms": [],
                "smart_tools": [],
                "tools": [
                    "ai_check_pending_work",
                    "ai_create_task",
                    "ai_list_my_tasks",
                    "ai_update_task",
                    "ai_complete_task",
                    "ai_create_project_tasks",
                    "ai_organize_tasks"
                ]
            },
            
            # Meta-tools (Always include these)
            "meta": {
                "priority": 0,  # Always include
                "keywords": ["help", "guide", "how to", "instructions", "documentation"],
                "platforms": [],
                "smart_tools": [],
                "tools": [
                    "get_platform_guide",
                    "get_workflow_instructions",
                    "get_smart_tool_instructions",
                    "list_platform_tools"
                ]
            }
        }
    
    def select_tools(self, user_query: str, max_tools: int = 20) -> Tuple[List[Dict], str]:
        """
        Select most relevant tools for user query
        
        Returns:
            (tool_definitions, strategy_guide)
        """
        query_lower = user_query.lower()
        
        # Step 1: Detect categories from query
        matched_categories = self._detect_categories(query_lower)
        
        # Step 2: Collect candidate tools from matched categories
        candidate_tools = set()
        smart_tools_to_highlight = []
        platforms_detected = []
        
        # Always include meta-tools
        candidate_tools.update(self.categories["meta"]["tools"])
        
        for category in matched_categories:
            cat_config = self.categories[category]
            
            # Add platform-specific tools
            for platform in cat_config["platforms"]:
                # Get all tools from this platform
                platform_tools = [
                    name for name, tool in self.registry.tools.items()
                    if tool.get("platform") == platform or name.startswith(f"{platform}_")
                ]
                candidate_tools.update(platform_tools)
                platforms_detected.append(platform)
            
            # Add specific tools (for calculators, task management)
            if "tools" in cat_config:
                candidate_tools.update(cat_config["tools"])
            
            # Track SMART tools for guidance
            if cat_config["smart_tools"]:
                smart_tools_to_highlight.extend(cat_config["smart_tools"])
        
        # Step 3: Score and rank tools by keyword relevance
        scored_tools = self._score_tools(query_lower, candidate_tools)
        
        # Step 4: Limit to max_tools
        top_tools = scored_tools[:max_tools]
        
        # Step 5: Get tool definitions
        tool_definitions = [
            self.registry.tools[tool_name]
            for tool_name in top_tools
            if tool_name in self.registry.tools
        ]
        
        # Step 6: Generate strategy guide
        strategy_guide = self._generate_strategy_guide(
            matched_categories,
            platforms_detected,
            smart_tools_to_highlight,
            len(tool_definitions)
        )
        
        return tool_definitions, strategy_guide
    
    def _detect_categories(self, query: str) -> List[str]:
        """
        Detect relevant categories from query keywords
        """
        matches = []
        
        for category, config in self.categories.items():
            priority = config["priority"]
            
            # Check if any keyword matches
            for keyword in config["keywords"]:
                if keyword in query:
                    matches.append((category, priority))
                    break  # Found match, move to next category
        
        # Sort by priority (0 = highest, always include)
        matches.sort(key=lambda x: x[1])
        
        # Return top 3 categories (plus any priority 0)
        result = [cat for cat, pri in matches if pri == 0]  # Always include priority 0
        result.extend([cat for cat, pri in matches if pri > 0][:3])  # Top 3 others
        
        return result
    
    def _score_tools(self, query: str, tool_names: Set[str]) -> List[str]:
        """
        Score tools by keyword overlap with query
        """
        query_words = set(query.split())
        scored = []
        
        for tool_name in tool_names:
            if tool_name not in self.registry.tools:
                continue
                
            tool = self.registry.tools[tool_name]
            
            # Get tool description and name
            description = tool.get("description", "").lower()
            name_parts = tool_name.lower().replace("_", " ")
            
            # Calculate overlap score
            desc_words = set(description.split())
            name_words = set(name_parts.split())
            
            # Score based on keyword overlap
            desc_overlap = len(query_words & desc_words)
            name_overlap = len(query_words & name_words) * 2  # Name matches worth more
            
            total_score = desc_overlap + name_overlap
            
            # Boost SMART tools
            if "smart" in tool_name:
                total_score += 5
            
            # Boost meta-tools slightly
            if tool_name.startswith("get_") or tool_name.startswith("list_"):
                total_score += 2
            
            scored.append((tool_name, total_score))
        
        # Sort by score (descending)
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [tool for tool, _ in scored]
    
    def _generate_strategy_guide(
        self,
        categories: List[str],
        platforms: List[str],
        smart_tools: List[str],
        tool_count: int
    ) -> str:
        """
        Generate strategic guidance for the AI based on detected categories
        """
        guide = f"\n🎯 **TOOL SELECTION STRATEGY** ({tool_count} tools loaded)\n\n"
        
        # Categories detected
        if categories:
            guide += f"**Detected Categories:** {', '.join(categories)}\n"
        
        # Platforms available
        if platforms:
            guide += f"**Platforms Available:** {', '.join(platforms)}\n"
        
        # Recommend SMART tools
        if smart_tools:
            guide += f"\n**⚡ RECOMMENDED SMART TOOLS:**\n"
            for smart_tool in smart_tools[:3]:  # Top 3
                guide += f"  - `{smart_tool}` (Use this for complex operations in one call)\n"
        
        # Task complexity guidance
        guide += f"\n**📋 TASK APPROACH:**\n"
        if "calculators" in categories:
            guide += "  - This appears to be a quote/pricing calculation\n"
            guide += "  - Use calculate_* tools with proper parameters\n"
            guide += "  - Use get_calculator_requirements() if unsure of parameters\n"
        elif "task_management" in categories:
            guide += "  - User wants you to remember or track something\n"
            guide += "  - Create a task with ai_create_task() immediately\n"
            guide += "  - Include detailed notes for future reference\n"
        elif "ecommerce" in categories or "payments" in categories:
            guide += "  - E-commerce/payment operation detected\n"
            guide += "  - Consider using SMART tools for bulk operations\n"
            guide += "  - WooCommerce + Stripe often work together\n"
        elif len(categories) > 2:
            guide += "  - Complex multi-platform task detected\n"
            guide += "  - Consider creating a project task plan with ai_create_project_tasks()\n"
            guide += "  - Use SMART tools to minimize API calls\n"
        else:
            guide += "  - Straightforward task, use appropriate tools directly\n"
            guide += "  - Prefer SMART tools when creating new resources\n"
        
        return guide

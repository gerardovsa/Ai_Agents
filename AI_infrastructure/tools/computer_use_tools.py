"""
Generic Computer Use Tools - Platform-Wide
===========================================

UNIVERSAL browser automation tools using Anthropic Computer Use API.
These tools can accomplish ANY task requiring web interaction:
- Competitor research (analyze quote calculators, pricing pages)
- Web scraping (extract data from any website)
- Form filling (submit applications, create accounts)
- Testing (UI/UX testing, cross-browser checks)
- OSINT (search social media, forums, databases)
- E-commerce (price comparisons, product research)

DESIGN PHILOSOPHY:
Generic, task-agnostic tools that accept natural language instructions.
Claude figures out HOW to accomplish the task - you just describe WHAT to do.

USAGE EXAMPLES:

    # Research competitor printing calculator
    result = registry.execute_tool(
        'computer_use_browse_and_extract',
        task='Navigate to vistaprint.com quote calculator, configure 1000 business cards 
              with 4-color both sides, extract final price and delivery time',
        _user_id='user123'
    )
    
    # Scrape product data
    result = registry.execute_tool(
        'computer_use_browse_and_extract',
        task='Go to amazon.com, search for "industrial label printer", extract top 5 
              product names, prices, and ratings',
        _user_id='user123'
    )
    
    # Fill online form
    result = registry.execute_tool(
        'computer_use_fill_form',
        url='https://example.com/contact',
        form_data={'name': 'John Doe', 'email': 'john@example.com', 'message': 'Hello'},
        submit=True,
        _user_id='user123'
    )

PLATFORM INTEGRATION:
These tools are available to ALL modules through Tool Registry V3.
No module-specific dependencies - pure platform infrastructure.

CREATED: December 16, 2025
AUTHOR: AI Agent Platform
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import anthropic
import os

# Import global Computer Use Executor
from AI_infrastructure.core.computer_use_executor import get_computer_use_executor

logger = logging.getLogger(__name__)


class GenericComputerUseSession:
    """
    Generic Computer Use session for ANY task.
    Manages Claude conversation loop for browser automation.
    """
    
    def __init__(
        self,
        task_description: str,
        max_iterations: int = 30,
        return_format: str = 'auto'
    ):
        """
        Initialize session.
        
        Args:
            task_description: Natural language task (WHAT to accomplish)
            max_iterations: Max Claude iterations (default 30 for complex tasks)
            return_format: 'json', 'text', or 'auto' (Claude decides)
        """
        self.task_description = task_description
        self.max_iterations = max_iterations
        self.return_format = return_format
        self.messages = []
        self.executor = get_computer_use_executor()
        self.container_id = None
        self.screenshots = []  # Store all screenshots for evidence
        
        # Get Anthropic API key
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.warning("[COMPUTER_USE] No ANTHROPIC_API_KEY in environment")
        
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
    
    async def run(self) -> Dict[str, Any]:
        """
        Execute the task.
        
        Returns:
            {
                'success': bool,
                'result': str or dict (extracted data),
                'screenshots': [base64 images],
                'iterations': int,
                'message': str
            }
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Anthropic API key not configured (set ANTHROPIC_API_KEY environment variable)',
                'help': 'Get API key from https://console.anthropic.com/'
            }
        
        try:
            # Get browser container
            logger.info(f"[COMPUTER_USE] Starting task: {self.task_description[:100]}...")
            self.container_id = await self.executor.get_browser_container(reuse=True)
            
            if not self.container_id:
                return {
                    'success': False,
                    'error': 'Failed to create browser container',
                    'help': 'Ensure Docker is running and professional-verification-browser image is built'
                }
            
            # Build system prompt based on return format
            system_prompt = self._build_system_prompt()
            
            # Initialize conversation
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
                    system=system_prompt,
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
                
                # Add assistant response to conversation
                assistant_message = {
                    "role": "assistant",
                    "content": response.content
                }
                self.messages.append(assistant_message)
                
                # Check stop reason
                if response.stop_reason == "end_turn":
                    # Claude finished - extract final answer
                    logger.info("[COMPUTER_USE] ✅ Task completed")
                    
                    final_text = ""
                    for block in response.content:
                        if hasattr(block, 'text'):
                            final_text += block.text
                    
                    # Try to parse as JSON if return_format is json
                    result_data = final_text
                    if self.return_format == 'json':
                        try:
                            result_data = json.loads(final_text)
                        except json.JSONDecodeError:
                            # Extract JSON from markdown code blocks if present
                            if '```json' in final_text:
                                json_start = final_text.index('```json') + 7
                                json_end = final_text.index('```', json_start)
                                result_data = json.loads(final_text[json_start:json_end].strip())
                            else:
                                logger.warning("[COMPUTER_USE] Could not parse JSON from response")
                    
                    return {
                        'success': True,
                        'result': result_data,
                        'screenshots': self.screenshots,
                        'iterations': iteration + 1,
                        'message': 'Task completed successfully'
                    }
                
                elif response.stop_reason == "tool_use":
                    # Claude wants to use computer - execute actions
                    tool_results = []
                    
                    for block in response.content:
                        if block.type == "tool_use" and block.name == "computer":
                            # Execute the computer action
                            action_result = await self.executor.execute_computer_action(
                                self.container_id,
                                block.input
                            )
                            
                            # Store screenshots for evidence
                            if block.input.get('action') == 'screenshot' and action_result.get('success'):
                                self.screenshots.append({
                                    'iteration': iteration + 1,
                                    'image': action_result.get('image'),
                                    'timestamp': datetime.now().isoformat()
                                })
                            
                            # Add tool result to conversation
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(action_result)
                            })
                    
                    # Add tool results as user message
                    if tool_results:
                        self.messages.append({
                            "role": "user",
                            "content": tool_results
                        })
                
                elif response.stop_reason == "max_tokens":
                    # Response too long - continue conversation
                    logger.warning("[COMPUTER_USE] Max tokens reached, continuing...")
                    continue
                
                else:
                    # Unknown stop reason
                    logger.warning(f"[COMPUTER_USE] Unexpected stop reason: {response.stop_reason}")
                    break
            
            # Max iterations reached without completion
            logger.warning(f"[COMPUTER_USE] Max iterations ({self.max_iterations}) reached")
            
            # Extract partial result
            final_text = ""
            for msg in self.messages:
                if msg['role'] == 'assistant':
                    for block in msg['content']:
                        if hasattr(block, 'text'):
                            final_text += block.text
            
            return {
                'success': False,
                'result': final_text,
                'screenshots': self.screenshots,
                'iterations': self.max_iterations,
                'message': f'Task incomplete after {self.max_iterations} iterations',
                'error': 'Max iterations reached - task may be too complex or website unresponsive'
            }
            
        except Exception as e:
            logger.error(f"[COMPUTER_USE] Task error: {e}")
            return {
                'success': False,
                'error': str(e),
                'screenshots': self.screenshots
            }
        
        finally:
            # Release container back to pool (don't destroy - reuse for next task)
            if self.container_id:
                self.executor.release_container(self.container_id)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt based on return format."""
        
        base_prompt = """You are a browser automation assistant. Use the computer tool to accomplish the user's task.

AVAILABLE ACTIONS:
- screenshot: Capture current screen
- mouse_move: Move cursor to coordinates
- left_click: Click at current position
- left_click_drag: Click and drag to coordinates
- right_click: Right click at current position
- middle_click: Middle click at current position
- double_click: Double click at current position
- type: Type text (supports special keys like Return, Tab, Escape)
- key: Press special keys (ctrl+c, ctrl+v, etc.)
- cursor_position: Get current cursor location

WORKFLOW:
1. Take screenshot to see current state
2. Plan your actions based on what you see
3. Execute actions (navigate, click, type, etc.)
4. Take screenshot to verify action worked
5. Repeat until task is complete
"""
        
        if self.return_format == 'json':
            base_prompt += """
RETURN FORMAT:
When task is complete, return a JSON object with the extracted data.
Wrap JSON in ```json code blocks for clarity.
Example: ```json
{
  "product_name": "Business Cards",
  "price": "$29.99",
  "delivery_time": "3-5 business days"
}
```
"""
        elif self.return_format == 'text':
            base_prompt += """
RETURN FORMAT:
When task is complete, return a clear text summary of findings.
Use bullet points or paragraphs as appropriate.
"""
        else:  # auto
            base_prompt += """
RETURN FORMAT:
Return data in the most appropriate format for the task.
Use JSON for structured data (prices, lists, tables).
Use text for summaries or descriptions.
"""
        
        return base_prompt


# ========================================
# PLATFORM TOOLS (Available to ALL modules)
# ========================================

def computer_use_browse_and_extract(
    task: str,
    return_format: str = 'auto',
    max_iterations: int = 30,
    _user_id: str = None,
    _injected_credentials: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Universal browser automation tool - accomplishes ANY web-based task.
    
    Use this for:
    - Competitor research (quote calculators, pricing, features)
    - Web scraping (extract data from any site)
    - Product research (compare prices, reviews, specs)
    - OSINT (search social media, forums, databases)
    - Testing (UI/UX, cross-browser compatibility)
    
    Args:
        task: Natural language description of WHAT to accomplish
              Examples:
              - "Navigate to vistaprint.com quote calculator, configure 1000 
                 business cards 4-color both sides, extract final price"
              - "Go to printful.com, search for t-shirt printing, extract 
                 pricing tiers for 100-500-1000 units"
              - "Research competitor.com customer reviews, extract common 
                 complaints and praise points"
        
        return_format: 'json' (structured data), 'text' (summary), 'auto' (Claude decides)
        max_iterations: Max browser interactions (default 30)
        _user_id: Platform user ID (auto-injected)
        _injected_credentials: Platform credentials (auto-injected)
    
    Returns:
        {
            'success': bool,
            'result': str or dict (extracted data),
            'screenshots': [base64 images] (evidence),
            'iterations': int,
            'message': str
        }
    
    Examples:
        >>> # Competitor quote calculator
        >>> result = computer_use_browse_and_extract(
        ...     task='Go to vistaprint.com business cards, configure 1000 qty, 
        ...           extract price and delivery time',
        ...     return_format='json'
        ... )
        >>> print(result['result'])
        {'price': '$29.99', 'delivery': '3-5 days', 'shipping': '$7.99'}
        
        >>> # Product research
        >>> result = computer_use_browse_and_extract(
        ...     task='Search amazon.com for "thermal label printer", extract 
        ...           top 3 products with prices and ratings',
        ...     return_format='json'
        ... )
    """
    session = GenericComputerUseSession(
        task_description=task,
        max_iterations=max_iterations,
        return_format=return_format
    )
    
    return asyncio.run(session.run())


def computer_use_fill_form(
    url: str,
    form_data: Dict[str, str],
    submit: bool = True,
    wait_for_result: bool = True,
    _user_id: str = None,
    _injected_credentials: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Fill and submit web forms automatically.
    
    Use this for:
    - Contact forms (inquiries, quotes)
    - Account creation (register on competitor sites)
    - Application submissions
    - Survey responses
    
    Args:
        url: Website URL with form
        form_data: Field name -> value mapping
                   Example: {'name': 'John Doe', 'email': 'john@example.com', 
                            'message': 'Request quote for 1000 business cards'}
        submit: Click submit button after filling (default True)
        wait_for_result: Wait for confirmation page (default True)
        _user_id: Platform user ID (auto-injected)
        _injected_credentials: Platform credentials (auto-injected)
    
    Returns:
        {
            'success': bool,
            'result': str (confirmation message or page content),
            'screenshots': [before, after],
            'message': str
        }
    
    Example:
        >>> # Request quote from competitor
        >>> result = computer_use_fill_form(
        ...     url='https://competitor.com/quote',
        ...     form_data={
        ...         'quantity': '1000',
        ...         'product': 'Business Cards',
        ...         'size': '3.5x2',
        ...         'color': 'Full Color Both Sides',
        ...         'email': 'research@mycompany.com'
        ...     }
        ... )
    """
    # Build task description
    task = f"""Navigate to {url} and fill out the form with the following data:
{json.dumps(form_data, indent=2)}
"""
    
    if submit:
        task += "\nAfter filling all fields, click the submit button."
    
    if wait_for_result:
        task += "\nWait for the confirmation page to load and extract the result message."
    
    task += "\n\nReturn the confirmation message or result page content as text."
    
    session = GenericComputerUseSession(
        task_description=task,
        max_iterations=20,
        return_format='text'
    )
    
    return asyncio.run(session.run())


def computer_use_compare_competitors(
    competitors: List[str],
    comparison_task: str,
    return_format: str = 'json',
    _user_id: str = None,
    _injected_credentials: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Compare multiple competitor websites automatically.
    
    Use this for:
    - Pricing comparison (quote calculators)
    - Feature comparison (product offerings)
    - UX comparison (checkout flows)
    - Performance comparison (load times, responsiveness)
    
    Args:
        competitors: List of competitor URLs
                     Example: ['vistaprint.com', 'moo.com', 'printful.com']
        comparison_task: What to compare
                         Example: "Extract pricing for 1000 business cards with 
                                  4-color printing both sides"
        return_format: 'json' (structured data), 'text' (summary)
        _user_id: Platform user ID (auto-injected)
        _injected_credentials: Platform credentials (auto-injected)
    
    Returns:
        {
            'success': bool,
            'result': dict with competitor data,
            'screenshots': [images from each site],
            'comparison': summary
        }
    
    Example:
        >>> # Compare printing prices
        >>> result = computer_use_compare_competitors(
        ...     competitors=['vistaprint.com', 'moo.com', 'printful.com'],
        ...     comparison_task='Extract pricing for 1000 business cards, 
        ...                     4-color both sides, standard delivery'
        ... )
        >>> print(result['result'])
        {
          'vistaprint.com': {'price': '$29.99', 'delivery': '3-5 days'},
          'moo.com': {'price': '$39.99', 'delivery': '2-4 days'},
          'printful.com': {'price': '$34.99', 'delivery': '4-7 days'}
        }
    """
    # Build comprehensive task
    task = f"""Compare the following competitor websites:
{json.dumps(competitors, indent=2)}

For each competitor, {comparison_task}

Return a JSON object with competitor URLs as keys and extracted data as values.
Example format:
```json
{{
  "competitor1.com": {{"price": "$X", "delivery": "Y days"}},
  "competitor2.com": {{"price": "$X", "delivery": "Y days"}}
}}
```
"""
    
    session = GenericComputerUseSession(
        task_description=task,
        max_iterations=50,  # More iterations for multiple sites
        return_format=return_format
    )
    
    result = asyncio.run(session.run())
    
    # Add comparison summary if successful
    if result.get('success') and isinstance(result.get('result'), dict):
        # Simple comparison logic (can be enhanced)
        result['comparison'] = f"Compared {len(competitors)} competitors successfully"
    
    return result


# ========================================
# TOOL REGISTRATION METADATA
# ========================================

COMPUTER_USE_TOOLS_METADATA = {
    "computer_use_browse_and_extract": {
        "name": "computer_use_browse_and_extract",
        "description": "Universal browser automation - navigate websites, interact with pages, extract data. Use for competitor research, web scraping, quote calculators, product research, OSINT.",
        "category": "automation",
        "tags": ["browser", "scraping", "research", "automation", "web"],
        "required_params": ["task"],
        "optional_params": ["return_format", "max_iterations"],
        "examples": [
            {
                "task": "Navigate to vistaprint.com quote calculator, configure 1000 business cards 4-color both sides, extract final price and delivery time",
                "return_format": "json"
            },
            {
                "task": "Go to printful.com, search for t-shirt printing, extract pricing tiers for quantities 100, 500, 1000",
                "return_format": "json"
            }
        ]
    },
    "computer_use_fill_form": {
        "name": "computer_use_fill_form",
        "description": "Automatically fill and submit web forms. Use for contact forms, quote requests, account creation, surveys.",
        "category": "automation",
        "tags": ["forms", "automation", "web"],
        "required_params": ["url", "form_data"],
        "optional_params": ["submit", "wait_for_result"],
        "examples": [
            {
                "url": "https://competitor.com/quote",
                "form_data": {
                    "quantity": "1000",
                    "product": "Business Cards",
                    "email": "research@company.com"
                },
                "submit": True
            }
        ]
    },
    "computer_use_compare_competitors": {
        "name": "computer_use_compare_competitors",
        "description": "Compare multiple competitor websites automatically. Extract and compare pricing, features, UX, performance across competitors.",
        "category": "analysis",
        "tags": ["competitors", "comparison", "research", "pricing"],
        "required_params": ["competitors", "comparison_task"],
        "optional_params": ["return_format"],
        "examples": [
            {
                "competitors": ["vistaprint.com", "moo.com", "printful.com"],
                "comparison_task": "Extract pricing for 1000 business cards, 4-color both sides, standard delivery",
                "return_format": "json"
            }
        ]
    }
}


if __name__ == "__main__":
    # Test the tools
    print("[COMPUTER_USE_TOOLS] Generic Computer Use Tools initialized")
    print(f"[COMPUTER_USE_TOOLS] Available tools: {list(COMPUTER_USE_TOOLS_METADATA.keys())}")

"""
Agent Deployment Tools - Dynamic worker spawning with tool access

This module provides the orchestrator AI with the ability to:
1. Deploy specialized AI workers on-demand
2. Generate dynamic prompts and cognitive processes
3. Give workers filtered access to tool registry
4. Handle data preparation (markdown conversion)
5. Monitor and collect worker outputs

INTEGRATION STATUS:
- ✅ Non-conflicting with existing system
- ✅ Uses existing combined_agent_worker.py
- ✅ Uses existing registry_v3 tool execution
- ✅ Uses existing OAuth credential injection
- ✅ Additive only - no modifications to core files

Created: December 6, 2025
"""

import json
import tempfile
import fnmatch
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
from queue import Queue
import threading

# Import your existing systems
def get_registry():
    """Import registry lazily to avoid circular imports"""
    from tools.registry_v3 import get_registry
    return get_registry()

def get_google_workspace_tools():
    """Import Google Workspace tools lazily"""
    from google_workspace import (
        google_sheets_read_data,
        google_docs_export_as_markdown,
        google_docs_smart_create_from_markdown,
        google_drive_upload_file
    )
    return {
        'sheets_read': google_sheets_read_data,
        'docs_export': google_docs_export_as_markdown,
        'docs_create': google_docs_smart_create_from_markdown,
        'drive_upload': google_drive_upload_file
    }

def get_agent_worker():
    """Import agent worker lazily"""
    from AI_infrastructure.core.combined_agent_worker import run_simple_agent_worker
    return run_simple_agent_worker


class AgentDeploymentManager:
    """
    Manages dynamic agent deployment and execution
    
    This manager:
    - Creates isolated job workspaces
    - Prepares data files (converts to markdown)
    - Generates dynamic system prompts
    - Filters tool access
    - Spawns worker AIs using existing infrastructure
    - Collects and uploads results
    """
    
    def __init__(self):
        self.registry = get_registry()
        self.active_agents = {}  # Track running agents
        self.job_workspace_root = Path(tempfile.gettempdir()) / "valor_ai_agents"
        self.job_workspace_root.mkdir(exist_ok=True)
        
        print(f"[AGENT DEPLOY] Initialized - Workspace: {self.job_workspace_root}")
        
    def deploy_agent(
        self,
        agent_type: str,
        task_description: str,
        files: Optional[List[Dict[str, str]]] = None,
        output_requirements: Optional[Dict[str, Any]] = None,
        tool_filter: Optional[List[str]] = None,
        execution_mode: str = "hybrid",
        user_id: int = 1,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Deploy a dynamic AI agent to handle a specialized task
        
        Args:
            agent_type: Type hint for prompt generation
                Options: "data_analysis", "report_generation", "automation",
                        "research", "content_creation", "custom"
            
            task_description: Natural language description of the task
                Example: "Analyze veterinary consultation data, find revisit 
                         patterns by species and month, create visualization"
            
            files: List of file references to prepare as context
                Format: [
                    {"type": "google_sheet", "url": "...", "export_as": "markdown"},
                    {"type": "google_doc", "url": "...", "export_as": "markdown"},
                    {"type": "local_file", "path": "/tmp/data.csv"}
                ]
            
            output_requirements: Expected outputs from the agent
                Format: {
                    "report": {"format": "markdown", "filename": "report.md"},
                    "metrics": {"format": "json", "filename": "metrics.json"},
                    "charts": {"format": "png", "directory": "charts/"}
                }
            
            tool_filter: List of tool patterns to allow
                Examples: ["google_*", "python_exec", "matplotlib_*"]
                If None, agent gets access to ALL tools
            
            execution_mode:
                - "hybrid": AI decides when to use tools vs direct action
                - "guided": System provides tool suggestions
                - "autonomous": AI has full tool access
            
            user_id: User ID for credential injection
            session_id: Session ID for tracking
        
        Returns:
            {
                "agent_id": "agent_abc123",
                "status": "running" | "complete" | "error",
                "job_workspace": "/tmp/valor_ai_agents/job_abc123",
                "outputs": {...},  # When complete
                "summary": "...",   # When complete
                "error": "..."      # If error
            }
        """
        
        print(f"[AGENT DEPLOY] ========================================")
        print(f"[AGENT DEPLOY] Deploying {agent_type} agent")
        print(f"[AGENT DEPLOY] Task: {task_description[:100]}...")
        print(f"[AGENT DEPLOY] ========================================")
        
        # Step 1: Create job workspace
        job_id = f"job_{int(time.time())}_{agent_type}"
        job_workspace = self.job_workspace_root / job_id
        job_workspace.mkdir(exist_ok=True)
        
        print(f"[AGENT DEPLOY] ✅ Created workspace: {job_workspace}")
        
        # Step 2: Prepare data files (convert to markdown)
        prepared_files = self._prepare_data_files(
            files=files,
            job_workspace=job_workspace,
            user_id=user_id
        )
        
        print(f"[AGENT DEPLOY] ✅ Prepared {len(prepared_files)} file(s)")
        
        # Step 3: Generate dynamic system prompt
        system_prompt = self._generate_agent_prompt(
            agent_type=agent_type,
            task_description=task_description,
            prepared_files=prepared_files,
            output_requirements=output_requirements,
            execution_mode=execution_mode
        )
        
        print(f"[AGENT DEPLOY] ✅ Generated system prompt ({len(system_prompt)} chars)")
        
        # Step 4: Filter tools (if requested)
        available_tools = self._filter_tools(tool_filter)
        
        print(f"[AGENT DEPLOY] ✅ Filtered to {len(available_tools)} tool(s)")
        
        # Step 5: Create agent configuration
        agent_config = {
            "agent_id": job_id,
            "agent_type": agent_type,
            "task_description": task_description,
            "job_workspace": str(job_workspace),
            "prepared_files": prepared_files,
            "output_requirements": output_requirements,
            "system_prompt": system_prompt,
            "available_tools": [t.get('name') for t in available_tools],
            "execution_mode": execution_mode,
            "created_at": time.time(),
            "user_id": user_id,
            "session_id": session_id
        }
        
        # Save config to workspace
        with open(job_workspace / "agent_config.json", "w") as f:
            json.dump(agent_config, f, indent=2)
        
        print(f"[AGENT DEPLOY] ✅ Saved agent config")
        
        # Step 6: Spawn the agent worker
        print(f"[AGENT DEPLOY] 🚀 Spawning worker: {job_id}")
        
        try:
            # Use your existing agent worker system
            queue = Queue()
            lock = threading.Lock()
            
            # Build initial prompt for the worker
            initial_prompt = self._build_initial_prompt(
                task_description=task_description,
                prepared_files=prepared_files,
                output_requirements=output_requirements
            )
            
            # Execute the worker
            # NOTE: This is SYNCHRONOUS for now
            # For async, you'd spawn a background thread
            run_simple_agent_worker = get_agent_worker()
            
            result = run_simple_agent_worker(
                agent_id=job_id,
                prompt=initial_prompt,
                lock=lock,
                session_id=session_id or job_id,
                queue=queue,
                conversation_history=[],
                user_id=user_id,
                thread_id=None  # Worker doesn't need thread persistence
            )
            
            print(f"[AGENT DEPLOY] ✅ Worker completed")
            
            # Step 7: Collect outputs
            outputs = self._collect_outputs(
                job_workspace=job_workspace,
                output_requirements=output_requirements
            )
            
            print(f"[AGENT DEPLOY] ✅ Collected {len(outputs)} output(s)")
            
            # Step 8: Upload results to Google (if needed)
            uploaded_results = self._upload_results(
                outputs=outputs,
                user_id=user_id
            )
            
            print(f"[AGENT DEPLOY] ✅ Uploaded {len(uploaded_results)} result(s)")
            print(f"[AGENT DEPLOY] ========================================")
            print(f"[AGENT DEPLOY] ✅ DEPLOYMENT COMPLETE")
            print(f"[AGENT DEPLOY] ========================================")
            
            return {
                "agent_id": job_id,
                "status": "complete",
                "job_workspace": str(job_workspace),
                "outputs": outputs,
                "uploaded_results": uploaded_results,
                "summary": self._extract_summary(result),
                "execution_time": time.time() - agent_config["created_at"]
            }
            
        except Exception as e:
            print(f"[AGENT DEPLOY] ❌ Error: {e}")
            return {
                "agent_id": job_id,
                "status": "error",
                "error": str(e),
                "job_workspace": str(job_workspace)
            }
    
    def _prepare_data_files(
        self,
        files: Optional[List[Dict]],
        job_workspace: Path,
        user_id: int
    ) -> List[Dict[str, str]]:
        """
        Prepare data files - KEY: Convert to markdown, not JSON
        
        This is CRITICAL for token efficiency:
        - Google Sheet as JSON: 50,000+ tokens
        - Google Sheet as Markdown: 5,000 tokens
        
        Returns list of prepared files with paths and metadata
        """
        if not files:
            return []
        
        prepared = []
        gw_tools = get_google_workspace_tools()
        
        for idx, file_spec in enumerate(files, 1):
            file_type = file_spec.get("type")
            export_format = file_spec.get("export_as", "markdown")
            
            print(f"[AGENT DEPLOY]   Preparing file {idx}/{len(files)}: {file_type}")
            
            try:
                if file_type == "google_sheet":
                    # Extract Sheet ID from URL
                    sheet_id = self._extract_id_from_url(file_spec["url"])
                    
                    # Read as markdown table (token-efficient)
                    if export_format == "markdown":
                        data = gw_tools['sheets_read'](
                            spreadsheet_id=sheet_id,
                            range_name=file_spec.get("range", "A:Z"),
                            _user_id=user_id,
                            _injected_credentials=True
                        )
                        
                        # Save to workspace
                        filename = f"sheet_{sheet_id[:8]}.md"
                        filepath = job_workspace / filename
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(str(data))
                        
                        prepared.append({
                            "type": "google_sheet",
                            "original_url": file_spec["url"],
                            "local_path": str(filepath),
                            "filename": filename,
                            "format": "markdown",
                            "size_bytes": filepath.stat().st_size
                        })
                        
                        print(f"[AGENT DEPLOY]     ✅ Saved as {filename} ({filepath.stat().st_size:,} bytes)")
                
                elif file_type == "google_doc":
                    # Extract Doc ID
                    doc_id = self._extract_id_from_url(file_spec["url"])
                    
                    # Export as markdown
                    markdown_content = gw_tools['docs_export'](
                        document_id=doc_id,
                        _user_id=user_id,
                        _injected_credentials=True
                    )
                    
                    # Save to workspace
                    filename = f"doc_{doc_id[:8]}.md"
                    filepath = job_workspace / filename
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(str(markdown_content))
                    
                    prepared.append({
                        "type": "google_doc",
                        "original_url": file_spec["url"],
                        "local_path": str(filepath),
                        "filename": filename,
                        "format": "markdown",
                        "size_bytes": filepath.stat().st_size
                    })
                    
                    print(f"[AGENT DEPLOY]     ✅ Saved as {filename} ({filepath.stat().st_size:,} bytes)")
                
                elif file_type == "local_file":
                    # Copy local file to workspace
                    import shutil
                    source_path = Path(file_spec["path"])
                    dest_path = job_workspace / source_path.name
                    shutil.copy(source_path, dest_path)
                    
                    prepared.append({
                        "type": "local_file",
                        "local_path": str(dest_path),
                        "filename": source_path.name,
                        "format": source_path.suffix[1:],  # Extension without dot
                        "size_bytes": dest_path.stat().st_size
                    })
                    
                    print(f"[AGENT DEPLOY]     ✅ Copied {source_path.name} ({dest_path.stat().st_size:,} bytes)")
            
            except Exception as e:
                print(f"[AGENT DEPLOY]     ❌ Failed: {e}")
                prepared.append({
                    "type": file_type,
                    "error": str(e),
                    "original_spec": file_spec
                })
        
        return prepared
    
    def _generate_agent_prompt(
        self,
        agent_type: str,
        task_description: str,
        prepared_files: List[Dict],
        output_requirements: Optional[Dict],
        execution_mode: str
    ) -> str:
        """
        Generate dynamic system prompt for the deployed agent
        
        This is where the MAGIC happens - the orchestrator AI
        can customize the worker's behavior dynamically
        """
        
        # Base prompts by agent type
        agent_type_prompts = {
            "data_analysis": """You are a data analysis specialist AI.

Your expertise:
- Statistical analysis and pattern recognition
- Data cleaning and transformation
- Visualization creation
- Report generation with insights

Your tools:
- python_exec: Execute Python code for analysis
- read_file: Read data files from your workspace
- write_file: Save results, reports, charts
- pandas, numpy, matplotlib, seaborn libraries available
""",
            
            "report_generation": """You are a report generation specialist AI.

Your expertise:
- Structured document creation
- Data summarization
- Visual presentation
- Professional formatting

Your tools:
- read_file: Read source data
- write_file: Create markdown reports
- google_docs_create: Upload to Google Docs
""",
            
            "automation": """You are an automation specialist AI.

Your expertise:
- Workflow automation
- Multi-step process orchestration
- Tool chaining
- Error handling and recovery

Your tools:
- Full access to Google Workspace tools
- Microsoft 365 tools
- Database tools
- File manipulation tools
""",
            
            "custom": """You are a general-purpose AI agent.

You have been deployed to handle a specific task.
Use the tools available to you to accomplish the goal.
"""
        }
        
        base_prompt = agent_type_prompts.get(agent_type, agent_type_prompts["custom"])
        
        # Add task description
        task_section = f"""
## Your Task

{task_description}

## Files Available to You

You have access to the following prepared data files in your workspace:
"""
        
        for file_info in prepared_files:
            if "error" not in file_info:
                task_section += f"""
- **{file_info['filename']}** ({file_info['format']})
  - Type: {file_info['type']}
  - Size: {file_info['size_bytes']:,} bytes
  - Path: {file_info['filename']} (in current directory)
"""
            else:
                task_section += f"""
- ⚠️ Error preparing file: {file_info.get('error', 'Unknown error')}
"""
        
        # Add output requirements
        output_section = ""
        if output_requirements:
            output_section = f"""
## Output Requirements

You MUST produce the following outputs:

"""
            for output_name, output_spec in output_requirements.items():
                output_section += f"""
### {output_name}
- Format: {output_spec.get('format', 'text')}
- Filename: {output_spec.get('filename', output_name)}
- Description: {output_spec.get('description', 'Required output')}
"""
        
        # Add execution mode guidance
        mode_section = f"""
## Execution Mode: {execution_mode}
"""
        
        if execution_mode == "hybrid":
            mode_section += """
You should balance between:
- Using tools when they provide efficiency or capabilities you lack
- Direct action when you can accomplish the task yourself
- Writing Python code for complex data processing
- Using Google Workspace tools for final outputs
"""
        elif execution_mode == "guided":
            mode_section += """
I will suggest tools for each step.
Use them as recommended, but you have autonomy to choose alternatives if better.
"""
        elif execution_mode == "autonomous":
            mode_section += """
You have full autonomy to:
- Choose which tools to use
- Decide your approach
- Iterate on errors
- Produce outputs in any way you see fit
"""
        
        # Add working directory info
        workspace_section = """
## Your Workspace

You are working in an isolated job directory.
All file operations are relative to this directory.

Example:
- To read a file: read_file(path="sheet_abc123.md")
- To write output: write_file(path="report.md", content="...")
- To create chart: python_exec(code="plt.savefig('chart.png')")
"""
        
        # Combine all sections
        full_prompt = f"""{base_prompt}

{task_section}

{output_section}

{mode_section}

{workspace_section}

## Important Notes

1. **File Paths:** Use relative paths (just filenames) - you're already in the job directory
2. **Token Efficiency:** Data files are in markdown format to save tokens
3. **Iteration:** You can iterate multiple times to refine outputs
4. **Error Recovery:** If a tool fails, try an alternative approach
5. **Completion:** When done, your outputs will be automatically collected

Begin working on your task now.
"""
        
        return full_prompt
    
    def _filter_tools(self, tool_filter: Optional[List[str]]) -> List[Dict]:
        """
        Filter available tools based on patterns
        
        If tool_filter is None, return ALL tools.
        Otherwise, filter to matching patterns.
        
        Patterns:
        - "google_*" - All Google tools
        - "python_exec" - Specific tool
        - "microsoft_word_*" - All Word tools
        """
        if tool_filter is None:
            # Return ALL tools from registry
            all_tools = self.registry.get_tools()
            return list(all_tools.values()) if isinstance(all_tools, dict) else all_tools
        
        all_tools = self.registry.get_tools()
        tool_list = list(all_tools.values()) if isinstance(all_tools, dict) else all_tools
        
        filtered = []
        
        for tool in tool_list:
            tool_name = tool.get("name", "")
            for pattern in tool_filter:
                if fnmatch.fnmatch(tool_name, pattern):
                    filtered.append(tool)
                    break
        
        return filtered
    
    def _build_initial_prompt(
        self,
        task_description: str,
        prepared_files: List[Dict],
        output_requirements: Optional[Dict]
    ) -> str:
        """Build the initial user prompt for the worker"""
        
        prompt = f"Task: {task_description}\n\n"
        
        if prepared_files:
            prompt += "Files available:\n"
            for file_info in prepared_files:
                if "error" not in file_info:
                    prompt += f"- {file_info['filename']}\n"
        
        if output_requirements:
            prompt += "\nRequired outputs:\n"
            for output_name in output_requirements.keys():
                prompt += f"- {output_name}\n"
        
        prompt += "\nBegin your work."
        
        return prompt
    
    def _collect_outputs(
        self,
        job_workspace: Path,
        output_requirements: Optional[Dict]
    ) -> Dict[str, Any]:
        """Collect outputs from the job workspace"""
        
        outputs = {}
        
        if output_requirements:
            for output_name, output_spec in output_requirements.items():
                filename = output_spec.get("filename", output_name)
                filepath = job_workspace / filename
                
                if filepath.exists():
                    if output_spec.get("format") == "json":
                        with open(filepath) as f:
                            outputs[output_name] = json.load(f)
                    else:
                        with open(filepath, "rb") as f:
                            outputs[output_name] = f.read()
                else:
                    outputs[output_name] = {"error": "File not created by agent"}
        else:
            # Collect all files in workspace
            for file in job_workspace.iterdir():
                if file.is_file() and file.name != "agent_config.json":
                    with open(file, "rb") as f:
                        outputs[file.name] = f.read()
        
        return outputs
    
    def _upload_results(
        self,
        outputs: Dict[str, Any],
        user_id: int
    ) -> Dict[str, str]:
        """Upload results to Google Docs/Drive"""
        
        uploaded = {}
        gw_tools = get_google_workspace_tools()
        
        for output_name, output_data in outputs.items():
            try:
                if output_name.endswith(".md"):
                    # Upload markdown as Google Doc
                    doc = gw_tools['docs_create'](
                        title=output_name.replace(".md", ""),
                        markdown_content=output_data.decode("utf-8") if isinstance(output_data, bytes) else output_data,
                        _user_id=user_id,
                        _injected_credentials=True
                    )
                    uploaded[output_name] = doc.get("documentUrl", "") if isinstance(doc, dict) else str(doc)
                    print(f"[AGENT DEPLOY]     ✅ Uploaded {output_name} to Google Docs")
                
                elif output_name.endswith((".png", ".jpg", ".pdf")):
                    # Upload to Drive
                    file_result = gw_tools['drive_upload'](
                        file_name=output_name,
                        file_data=output_data,
                        _user_id=user_id,
                        _injected_credentials=True
                    )
                    uploaded[output_name] = file_result.get("webViewLink", "") if isinstance(file_result, dict) else str(file_result)
                    print(f"[AGENT DEPLOY]     ✅ Uploaded {output_name} to Google Drive")
            
            except Exception as e:
                print(f"[AGENT DEPLOY]     ❌ Failed to upload {output_name}: {e}")
                uploaded[output_name] = f"Error: {e}"
        
        return uploaded
    
    def _extract_id_from_url(self, url: str) -> str:
        """Extract Google file ID from URL"""
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if match:
            return match.group(1)
        return url  # Assume it's already an ID
    
    def _extract_summary(self, worker_result: Any) -> str:
        """Extract summary from worker execution result"""
        # This would extract key insights from the worker's output
        return "Task completed successfully"


# ============================================================
# TOOL FUNCTION (What gets registered in registry_v3)
# ============================================================

def deploy_agent(
    agent_type: str,
    task_description: str,
    files: Optional[List[Dict[str, str]]] = None,
    output_requirements: Optional[Dict[str, Any]] = None,
    tool_filter: Optional[List[str]] = None,
    execution_mode: str = "hybrid",
    _user_id: int = 1,
    _session_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Deploy a dynamic AI agent to handle specialized tasks
    
    This tool allows the orchestrator AI to:
    1. Spawn specialized worker AIs on-demand
    2. Generate dynamic prompts and cognitive processes
    3. Provide filtered tool access
    4. Handle data preparation (markdown conversion)
    5. Collect and upload results
    
    Args:
        agent_type: "data_analysis", "report_generation", "automation", "custom"
        task_description: Natural language task description
        files: List of file references (Google Docs/Sheets, local files)
        output_requirements: Expected outputs with format specifications
        tool_filter: Tool patterns to allow (e.g., ["google_*", "python_exec"])
        execution_mode: "hybrid", "guided", or "autonomous"
    
    Returns:
        {
            "agent_id": "job_...",
            "status": "complete" | "error",
            "outputs": {...},
            "uploaded_results": {"report.md": "https://docs.google.com/..."},
            "summary": "...",
            "execution_time": 12.5
        }
    
    Example:
        deploy_agent(
            agent_type="data_analysis",
            task_description="Analyze veterinary consultation data...",
            files=[
                {"type": "google_sheet", "url": "https://...", "export_as": "markdown"}
            ],
            output_requirements={
                "report": {"format": "markdown", "filename": "report.md"},
                "metrics": {"format": "json", "filename": "metrics.json"}
            },
            tool_filter=["google_*", "python_exec", "read_file", "write_file"]
        )
    """
    manager = AgentDeploymentManager()
    
    return manager.deploy_agent(
        agent_type=agent_type,
        task_description=task_description,
        files=files,
        output_requirements=output_requirements,
        tool_filter=tool_filter,
        execution_mode=execution_mode,
        user_id=_user_id,
        session_id=_session_id,
        **kwargs
    )


# Export for registry registration
__all__ = ['deploy_agent', 'AgentDeploymentManager']

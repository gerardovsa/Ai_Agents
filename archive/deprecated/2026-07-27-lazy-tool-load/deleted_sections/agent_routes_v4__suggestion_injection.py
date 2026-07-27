"""
ORIGINAL LOCATION: AI_infrastructure/routes/agent_routes_v4.py, lines 2185-2190
NAME: if intelligent_tool_suggestions: system_prompt += ...
DATE REMOVED: 2026-07-27
PURPOSE: Inject the pre-searched tool suggestions into the system prompt right before the system_prompt_continued block.

RESTORE: Paste back into agent_routes_v4.py at the original location. Requires intelligent_tool_suggestions to be defined (snippet agent_routes_v4__intelligent_tool_suggestions.py).

CONTEXT — WHY REMOVED:
Lazy-load refactor: the AI no longer receives proactive semantic tool
suggestions at startup. It sees only the 8 meta-tools and discovers
the remaining 829 tools on demand via search_tools / get_tool_schema /
execute_tool. The background prewarm that loaded MiniLM embeddings was
the silent OOM/SIGTERM trigger on Render (the prewarm held the gevent
worker for 1-3s on first chat while gunicorn's 120s timeout ticked).

This bundle is the rollback recipe. See archive/deprecated/2026-07-27-
lazy-tool-load/ROLLBACK.md for the exact git + cp commands.
"""

# --- ORIGINAL CODE BEGINS -----------------------------------------------

    # ============================================
    # 🎯 INJECT INTELLIGENT TOOL SUGGESTIONS
    # ============================================
    if intelligent_tool_suggestions:
        print(f"[STREAM] 📋 Injecting intelligent tool suggestions into system prompt")
        system_prompt += intelligent_tool_suggestions

# --- ORIGINAL CODE ENDS -------------------------------------------------

"""
ORIGINAL LOCATION: AI_infrastructure/routes/agent_routes_v4.py, lines 1318-1445
NAME: intelligent_tool_suggestions block
DATE REMOVED: 2026-07-27
PURPOSE: The full proactive semantic tool pre-search: runs semantic_search.search(last_message, top_k=15), filters by auth platform (microsoft vs google), limits to top 8, formats into a INTELLIGENT TOOL SUGGESTIONS block injected into the system prompt at line 2188.

RESTORE: Paste back into agent_routes_v4.py between line 1317 and 1446. Re-add the injection at line 2188 (snippet in agent_routes_v4__suggestion_injection.py).

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

    intelligent_tool_suggestions = ""
    try:
        # Get cached semantic search instance (embeddings computed once at startup)
        semantic_search = get_semantic_search(registry)
        
        if semantic_search and semantic_search.available:
            # Pre-search tools using the user's actual message
            print(f"[STREAM] 🔍 PRE-SEARCHING tools for: '{last_message[:100]}...'")
            suggested_tools = semantic_search.search(last_message, top_k=15)  # Get more, then filter
        
            # ============================================
            # 🔒 PLATFORM FILTERING (Based on Auth)
            # ============================================
            if suggested_tools and auth_platform in ['microsoft', 'google']:
                original_count = len(suggested_tools)
                
                # Define platform exclusions
                google_platforms = ['gmail', 'google_workspace', 'google_docs', 'google_sheets', 
                                  'google_drive', 'google_calendar', 'google_tasks', 'google_forms',
                                  'google_slides', 'google_meet', 'google_analytics', 'google_cloud_run']
                
                microsoft_platforms = ['microsoft_outlook', 'microsoft_excel', 'microsoft_word',
                                     'microsoft_onedrive', 'microsoft_teams', 'microsoft_calendar',
                                     'microsoft_todo', 'microsoft_onenote', 'microsoft_sharepoint',
                                     'microsoft_forms', 'outlook', 'excel', 'word', 'onedrive']
                
                # Filter based on auth platform
                if auth_platform == 'microsoft':
                    # User authenticated with Microsoft → exclude Google tools
                    suggested_tools = [
                        tool for tool in suggested_tools 
                        if tool.get('platform', '').lower() not in google_platforms
                    ]
                    print(f"[STREAM] 🔒 MICROSOFT user: Filtered out {original_count - len(suggested_tools)} Google tools")
                
                elif auth_platform == 'google':
                    # User authenticated with Google → exclude Microsoft tools
                    suggested_tools = [
                        tool for tool in suggested_tools 
                        if tool.get('platform', '').lower() not in microsoft_platforms
                    ]
                    print(f"[STREAM] 🔒 GOOGLE user: Filtered out {original_count - len(suggested_tools)} Microsoft tools")
                
                # Keep only top 8 after filtering
                suggested_tools = suggested_tools[:8]
            
            if suggested_tools:
                print(f"[STREAM] ✨ Found {len(suggested_tools)} semantically relevant tools (after platform filtering)")
                
                # Build intelligent suggestions block with IMPROVED FORMATTING
                intelligent_tool_suggestions = "\n\n" + "="*80 + "\n"
                intelligent_tool_suggestions += "🎯 INTELLIGENT TOOL SUGGESTIONS (Pre-searched for this query)\n"
                intelligent_tool_suggestions += "="*80 + "\n\n"
                intelligent_tool_suggestions += "Based on semantic analysis of the user's message, these tools are most relevant:\n\n"
                
                for idx, tool_result in enumerate(suggested_tools, 1):
                    tool_name = tool_result['tool_name']
                    short_desc = tool_result.get('short_description', 'No description')
                    similarity = tool_result.get('similarity', 0.0)
                    platform = tool_result.get('platform', 'unknown')
                    
                    # Add emoji based on similarity score
                    if similarity >= 0.7:
                        relevance = "🔥"
                    elif similarity >= 0.5:
                        relevance = "✅"
                    else:
                        relevance = "💡"
                    
                    # Determine required guides based on tool name and platform
                    required_guides = []
                    if 'calculate_' in tool_name or platform == 'quote_calculator':
                        required_guides.append('inhouse_get_domain_guide()')
                        required_guides.append('inhouse_calculator_guide()')
                    elif 'inhouse_execute_sql' in tool_name or 'inhouse_query' in tool_name:
                        required_guides.append('inhouse_get_domain_guide()')
                        if 'execute_sql' in tool_name:
                            required_guides.append('inhouse_database_guide()')
                        else:
                            required_guides.append('inhouse_query_guide()')
                    elif 'synergy_' in tool_name and 'guide' not in tool_name:
                        required_guides.append('synergy_guide(\"overview\")')
                    elif any(viz in tool_name for viz in ['chart', 'graph', 'plot', 'visual']):
                        required_guides.append('visualization_guide(type)')
                    
                    # NEW FORMAT: tool name, platform, emoji on one line
                    intelligent_tool_suggestions += f"{idx}. {tool_name} [{platform}] {relevance}\n"
                    intelligent_tool_suggestions += f"   {short_desc}\n"
                    intelligent_tool_suggestions += f"   Similarity: {similarity:.1%}\n"
                    if required_guides:
                        intelligent_tool_suggestions += f"   ⚠️  MUST call first: {' → '.join(required_guides)}\n"
                    intelligent_tool_suggestions += "\n"
                
                intelligent_tool_suggestions += "**How to Use These Suggestions:**\n"
                intelligent_tool_suggestions += "- These tools were pre-selected by semantic analysis (NOT guaranteed perfect matches)\n"
                intelligent_tool_suggestions += "- ⚠️  CRITICAL: Always call GUIDE tools FIRST before using suggested tools:\n"
                intelligent_tool_suggestions += "  • InHouse operations: inhouse_get_domain_guide() → domain-specific guide\n"
                intelligent_tool_suggestions += "  • Visualizations: visualization_guide(type) before creating charts\n"
                intelligent_tool_suggestions += "  • Complex workflows: synergy_guide(\"overview\") for 3+ tool operations\n"
                intelligent_tool_suggestions += "- Similarity scores are suggestions, not certainty:\n"
                intelligent_tool_suggestions += "  • 🔥 ≥70% = High confidence (still verify with get_tool_schema)\n"
                intelligent_tool_suggestions += "  • ✅ ≥50% = Medium confidence (validate carefully)\n"
                intelligent_tool_suggestions += "  • 💡 <50% = Low confidence (consider manual search_tools())\n"
                intelligent_tool_suggestions += "- You can use get_tool_schema → execute_tool IF no guide tools required\n"
                intelligent_tool_suggestions += "- You still have autonomy: if these don't fit, use search_tools() manually\n"
                intelligent_tool_suggestions += "- This saves discovery time, but NOT context-gathering time (guides still mandatory)\n"
                intelligent_tool_suggestions += "\n" + "="*80 + "\n"
                
                # LOG ALL SELECTED TOOLS (Not just top 3)
                print(f"[STREAM] 🎯 INTELLIGENT TOOL SELECTION (Top {len(suggested_tools)}):")
                for idx, tool_result in enumerate(suggested_tools, 1):
                    tool_name = tool_result['tool_name']
                    similarity = tool_result.get('similarity', 0.0)
                    platform = tool_result.get('platform', 'unknown')
                    print(f"[STREAM]   {idx}. {tool_name} [{platform}] - {similarity:.1%} match")
            else:
                print(f"[STREAM] ℹ️  No semantic matches found (threshold 0.3+)")
        else:
            print(f"[STREAM] ⚠️  Semantic search not available")
    
    except Exception as e:
        # ✅ NO TEMPORAL COUPLING (July 24, 2026): The prewarm gate is
        # gone. The chat endpoint never 503s because of an optimisation
        # layer (tool embeddings) being unavailable. If anything in the
        # suggestion-block pipeline raises, we log it and continue with
        # `intelligent_tool_suggestions = ""`. The AI still receives the
        # full tool schema and can pick tools directly.
        print(f"[STREAM] ⚠️  Semantic pre-search failed (continuing without suggestions): {e}")

# --- ORIGINAL CODE ENDS -------------------------------------------------

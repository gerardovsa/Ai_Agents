"""
FILE: AI_infrastructure/config/deployment_config.py
PURPOSE: Deployment-specific configuration for module loading

ARCHITECTURE:
- Environment detection (local, Render, production)
- Module filtering based on deployment target
- Centralized configuration for module availability

USAGE:
    from AI_infrastructure.config.deployment_config import is_module_enabled
    
    if is_module_enabled('parametric-cad'):
        # Load module
    else:
        # Skip module (disabled for this environment)

CREATED: December 16, 2025
"""
import os
import logging

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENVIRONMENT DETECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Detect deployment environment
IS_RENDER = os.environ.get('RENDER') == 'true'
IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'
IS_LOCAL = not (IS_RENDER or IS_PRODUCTION)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODULE FILTERING CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Modules to DISABLE on Render deployment
# Strategy: Only keep inhouse-kanban visible on Render, disable all other external modules
# NOTE (July 23, 2026): Removed 'veterinary_alerts', 'vsa-veterinary-alerts', and 'xero'
#   from this list per active development work. The user is iterating on these modules
#   so they must stay enabled. Re-add here only with explicit instruction.
RENDER_DISABLED_MODULES = [
    # External modules (all disabled except inhouse-kanban)
    'database-visualizer',
    'design-engineering',
    'github',
    # 'inhouse-kanban',    # ← KEEP THIS ENABLED (the only external module visible on Render)
    'inhouse-print',
    'parametric-cad',
    'quote-calculator',
    'render-management',
    'salesforce',
    'shopify',
    'stock-management',
    'voip-demo',
    # 'veterinary_alerts',        # OFF disabled list — module under active development
    # 'vsa-veterinary-alerts',    # OFF disabled list — module under active development
    # 'xero',                     # OFF disabled list — normal xero tools stay enabled
]

# Modules to DISABLE in ALL production environments
# (development/debugging tools only)
PRODUCTION_DISABLED_MODULES = [
    'debug-module',        # Development debugging tools
]

# Modules that are ALWAYS enabled (core system modules)
# These will never be disabled regardless of environment
ALWAYS_ENABLED_MODULES = [
    # Core internal modules (already hardcoded in HTML)
    'agents',
    'automation',
    'automation-workflows',
    'communication-hub',
    'internal-docs',
    'messages',
    'notifications',
    'prompt-library',
    'settings-sidebar',
    'synergy',
    'thread-cards',
    'thread-manager',
    'transcription',
    'universal-search',
    'vector_database',
    'workflow',
    
    # Critical external modules (ONLY inhouse-kanban on Render)
    'inhouse-kanban',    # ← ONLY external module visible on Render deployment
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PUBLIC API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_environment_name():
    """Get current environment name"""
    if IS_RENDER:
        return 'render'
    elif IS_PRODUCTION:
        return 'production'
    elif IS_LOCAL:
        return 'local'
    else:
        return 'unknown'


def get_disabled_modules():
    """
    Get list of modules to disable based on current environment
    
    Returns:
        List[str]: List of module IDs to disable
    """
    disabled = []
    
    if IS_RENDER:
        disabled.extend(RENDER_DISABLED_MODULES)
        logger.info(f"🌐 Render deployment detected - disabling {len(RENDER_DISABLED_MODULES)} modules: {', '.join(RENDER_DISABLED_MODULES)}")
    
    if IS_PRODUCTION or IS_RENDER:
        disabled.extend(PRODUCTION_DISABLED_MODULES)
        logger.info(f"🏭 Production environment - disabling {len(PRODUCTION_DISABLED_MODULES)} debug modules: {', '.join(PRODUCTION_DISABLED_MODULES)}")
    
    if IS_LOCAL:
        logger.info("💻 Local development - all modules enabled")
    
    # Remove duplicates
    return list(set(disabled))


def is_module_enabled(module_id):
    """
    Check if module should be enabled in current environment
    
    Args:
        module_id (str): Module identifier (e.g., 'parametric-cad')
    
    Returns:
        bool: True if module should be loaded, False if disabled
    """
    # Always enable core modules
    if module_id in ALWAYS_ENABLED_MODULES:
        return True
    
    # Check if module is in disabled list
    disabled = get_disabled_modules()
    enabled = module_id not in disabled
    
    if not enabled:
        logger.debug(f"⏸️  Module '{module_id}' disabled in {get_environment_name()} environment")
    
    return enabled


def get_module_filter_stats():
    """
    Get statistics about module filtering
    
    Returns:
        dict: Statistics about enabled/disabled modules
    """
    disabled = get_disabled_modules()
    
    return {
        'environment': get_environment_name(),
        'is_local': IS_LOCAL,
        'is_production': IS_PRODUCTION,
        'is_render': IS_RENDER,
        'disabled_count': len(disabled),
        'disabled_modules': disabled,
        'always_enabled_count': len(ALWAYS_ENABLED_MODULES),
        'always_enabled_modules': ALWAYS_ENABLED_MODULES
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INITIALIZATION LOG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Log environment detection on import
env_name = get_environment_name()
logger.info(f"🎯 Deployment environment detected: {env_name.upper()}")

if IS_RENDER:
    logger.info(f"🌐 Render deployment mode: {len(RENDER_DISABLED_MODULES)} modules will be disabled")
elif IS_PRODUCTION:
    logger.info(f"🏭 Production mode: {len(PRODUCTION_DISABLED_MODULES)} debug modules will be disabled")
elif IS_LOCAL:
    logger.info("💻 Local development mode: All modules enabled")

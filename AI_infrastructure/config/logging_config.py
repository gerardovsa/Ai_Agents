"""
Logging Configuration for V4 Agent System
Import this module to apply logging settings.
"""

from AI_infrastructure.utils.logger import get_logger, log_system_startup
from AI_infrastructure.config.constants import LOG_LEVELS, ENVIRONMENT

# Get root logger
root_logger = get_logger('v4_agent')

# Log system startup on import
log_system_startup(root_logger, "V4 Agent System", "v4.0.0")

# Export for convenience
__all__ = ['root_logger']

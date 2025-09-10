"""GV-NFO-Maker 日志工具。"""

import logging
import logging.config
from typing import Optional

from ..config.settings import LOGGING_CONFIG


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
    """Setup logging configuration.
    
    Args:
        verbose: Enable verbose logging
        log_file: Custom log file path
    """
    config = LOGGING_CONFIG.copy()
    
    # Adjust log levels based on verbose flag
    if verbose:
        config['handlers']['console']['level'] = 'DEBUG'
        config['loggers']['gv_nfo_maker']['level'] = 'DEBUG'
    
    # Use custom log file if provided
    if log_file:
        config['handlers']['file']['filename'] = log_file
    
    # Apply logging configuration
    logging.config.dictConfig(config)
    
    # Get logger and log startup message
    logger = logging.getLogger('gv_nfo_maker')
    logger.info("GV-NFO-Maker logging initialized")
    
    if verbose:
        logger.debug("Verbose logging enabled")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f'gv_nfo_maker.{name}')


class LoggerMixin:
    """Mixin class to add logging capabilities."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)
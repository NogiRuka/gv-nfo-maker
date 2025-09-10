"""GV-NFO-Maker 配置模块。"""

from .config_manager import ConfigManager
from .settings import DEFAULT_CONFIG, SITE_CONFIGS

__all__ = [
    'ConfigManager',
    'DEFAULT_CONFIG',
    'SITE_CONFIGS'
]
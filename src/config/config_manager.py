"""Configuration Manager for NFO Generator."""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from .settings import DEFAULT_CONFIG, SITE_CONFIGS, VALIDATION_RULES
from ..core.exceptions import ConfigurationError


class ConfigManager:
    """Manages configuration for NFO Generator."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or "config.json"
        self.config = DEFAULT_CONFIG.copy()
        self.site_configs = SITE_CONFIGS.copy()
        self.validation_rules = VALIDATION_RULES.copy()
        
        # Load configuration from file if exists
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                
                # Merge with default config
                self.config.update(file_config.get('general', {}))
                
                # Update site configs
                if 'sites' in file_config:
                    for site, site_config in file_config['sites'].items():
                        if site in self.site_configs:
                            self.site_configs[site].update(site_config)
                        else:
                            self.site_configs[site] = site_config
                
                print(f"✅ 配置文件已加载: {self.config_file}")
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  配置文件加载失败: {e}，使用默认配置")
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            config_data = {
                'general': self.config,
                'sites': self.site_configs
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 配置已保存到: {self.config_file}")
            
        except IOError as e:
            raise ConfigurationError(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def get_site_config(self, site: str) -> Dict[str, Any]:
        """Get site-specific configuration.
        
        Args:
            site: Site identifier
            
        Returns:
            Site configuration dictionary
            
        Raises:
            ConfigurationError: If site not found
        """
        if site not in self.site_configs:
            raise ConfigurationError(f"未找到网站配置: {site}")
        
        return self.site_configs[site]
    
    def set_site_config(self, site: str, config: Dict[str, Any]) -> None:
        """Set site-specific configuration.
        
        Args:
            site: Site identifier
            config: Site configuration dictionary
        """
        if site in self.site_configs:
            self.site_configs[site].update(config)
        else:
            self.site_configs[site] = config
    
    def get_supported_sites(self) -> list:
        """Get list of supported sites.
        
        Returns:
            List of supported site identifiers
        """
        return list(self.site_configs.keys())
    
    def validate_config(self) -> bool:
        """Validate current configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Validate general config
        required_keys = ['user_agent', 'timeout', 'output_format']
        for key in required_keys:
            if key not in self.config:
                raise ConfigurationError(f"缺少必需的配置项: {key}")
        
        # Validate timeout
        if not isinstance(self.config['timeout'], (int, float)) or self.config['timeout'] <= 0:
            raise ConfigurationError("timeout必须是正数")
        
        # Validate retry attempts
        if 'retry_attempts' in self.config:
            if not isinstance(self.config['retry_attempts'], int) or self.config['retry_attempts'] < 0:
                raise ConfigurationError("retry_attempts必须是非负整数")
        
        # Validate site configs
        for site, site_config in self.site_configs.items():
            required_site_keys = ['name', 'domain']
            for key in required_site_keys:
                if key not in site_config:
                    raise ConfigurationError(f"网站 {site} 缺少必需的配置项: {key}")
        
        return True
    
    def create_default_config_file(self) -> None:
        """Create default configuration file."""
        if not os.path.exists(self.config_file):
            self.save_config()
            print(f"✅ 已创建默认配置文件: {self.config_file}")
        else:
            print(f"⚠️  配置文件已存在: {self.config_file}")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.config = DEFAULT_CONFIG.copy()
        self.site_configs = SITE_CONFIGS.copy()
        print("✅ 配置已重置为默认值")
    
    def get_generator_config(self, site: str) -> Dict[str, Any]:
        """Get combined configuration for a specific generator.
        
        Args:
            site: Site identifier
            
        Returns:
            Combined configuration dictionary
        """
        site_config = self.get_site_config(site)
        
        # Combine general and site-specific config
        generator_config = self.config.copy()
        generator_config.update(site_config)
        
        return generator_config
    
    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
        """
        if 'general' in config_dict:
            self.config.update(config_dict['general'])
        
        if 'sites' in config_dict:
            for site, site_config in config_dict['sites'].items():
                self.set_site_config(site, site_config)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
            'general': self.config,
            'sites': self.site_configs
        }
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"ConfigManager(config_file={self.config_file}, sites={list(self.site_configs.keys())})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ConfigManager(config={self.config}, sites={self.site_configs})"
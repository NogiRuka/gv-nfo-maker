"""Generator Factory for NFO Generator."""

from typing import Optional, Dict, Type
from urllib.parse import urlparse

from ..core.base_generator import BaseNfoGenerator
from ..core.exceptions import ConfigurationError
from ..config.config_manager import ConfigManager
from ..generators.ck_download_generator import CkDownloadNfoGenerator
from ..generators.trance_generator import TranceMusicNfoGenerator


class GeneratorFactory:
    """Factory class for creating NFO generators."""
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize the factory.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self._generators: Dict[str, Type[BaseNfoGenerator]] = {
            "ck-download": CkDownloadNfoGenerator,
            "trance-music": TranceMusicNfoGenerator
        }
    
    def register_generator(self, site: str, generator_class: Type[BaseNfoGenerator]) -> None:
        """Register a new generator class.
        
        Args:
            site: Site identifier
            generator_class: Generator class
        """
        self._generators[site] = generator_class
        print(f"✅ 已注册生成器: {site} -> {generator_class.__name__}")
    
    def create_generator(self, site: str) -> BaseNfoGenerator:
        """Create a generator for the specified site.
        
        Args:
            site: Site identifier
            
        Returns:
            Generator instance
            
        Raises:
            ConfigurationError: If site is not supported
        """
        if site not in self._generators:
            supported_sites = list(self._generators.keys())
            raise ConfigurationError(
                f"不支持的网站: {site}. 支持的网站: {', '.join(supported_sites)}"
            )
        
        generator_class = self._generators[site]
        config = self.config_manager.get_generator_config(site)
        
        return generator_class(config)
    
    def create_generator_from_url(self, url: str) -> Optional[BaseNfoGenerator]:
        """Create a generator based on URL analysis.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Generator instance if URL is recognized, None otherwise
        """
        # Parse URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()
        
        # Check each registered generator
        for site, generator_class in self._generators.items():
            try:
                # Create temporary instance to check URL
                temp_config = self.config_manager.get_generator_config(site)
                temp_generator = generator_class(temp_config)
                
                if temp_generator.validate_url(url):
                    print(f"🎯 检测到网站类型: {temp_generator.site_name}")
                    return temp_generator
                    
            except Exception as e:
                print(f"⚠️  检查生成器 {site} 时出错: {e}")
                continue
        
        # Fallback: try to match by domain keywords
        domain_mappings = {
            "ck-download": ["ck-download", "ckdownload"],
            "trance-music": ["trance", "music", "electronic", "dance"]
        }
        
        for site, keywords in domain_mappings.items():
            if any(keyword in domain or keyword in path for keyword in keywords):
                try:
                    return self.create_generator(site)
                except ConfigurationError:
                    continue
        
        return None
    
    def get_supported_sites(self) -> list:
        """Get list of supported sites.
        
        Returns:
            List of supported site identifiers
        """
        return list(self._generators.keys())
    
    def get_generator_info(self, site: str) -> Dict[str, str]:
        """Get information about a generator.
        
        Args:
            site: Site identifier
            
        Returns:
            Dictionary with generator information
            
        Raises:
            ConfigurationError: If site is not supported
        """
        if site not in self._generators:
            raise ConfigurationError(f"不支持的网站: {site}")
        
        generator_class = self._generators[site]
        site_config = self.config_manager.get_site_config(site)
        
        # Create temporary instance to get site info
        temp_config = self.config_manager.get_generator_config(site)
        temp_generator = generator_class(temp_config)
        
        return {
            "site": site,
            "name": temp_generator.site_name,
            "domain": temp_generator.site_domain,
            "class": generator_class.__name__,
            "description": generator_class.__doc__ or "No description available"
        }
    
    def list_generators(self) -> None:
        """Print information about all registered generators."""
        print("📋 已注册的生成器:")
        print("=" * 50)
        
        for site in self._generators:
            try:
                info = self.get_generator_info(site)
                print(f"\n🔹 {info['name']} ({info['site']})")
                print(f"   类名: {info['class']}")
                print(f"   域名: {info['domain']}")
                print(f"   描述: {info['description']}")
            except Exception as e:
                print(f"\n❌ {site}: 获取信息失败 - {e}")
    
    def validate_all_generators(self) -> bool:
        """Validate all registered generators.
        
        Returns:
            True if all generators are valid
        """
        all_valid = True
        
        print("🔍 验证所有生成器...")
        
        for site in self._generators:
            try:
                generator = self.create_generator(site)
                print(f"✅ {generator.site_name}: 验证通过")
            except Exception as e:
                print(f"❌ {site}: 验证失败 - {e}")
                all_valid = False
        
        return all_valid
    
    def __str__(self) -> str:
        """String representation of the factory."""
        sites = list(self._generators.keys())
        return f"GeneratorFactory(sites={sites})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"GeneratorFactory(generators={self._generators})"
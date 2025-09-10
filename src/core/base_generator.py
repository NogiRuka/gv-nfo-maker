"""Base NFO Generator abstract class."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom

from .movie_data import MovieData, Actor, Rating
from .exceptions import ScrapingError, ValidationError, NetworkError
from .nfo_template import TemplateManager


class BaseNfoGenerator(ABC):
    """Abstract base class for NFO generators."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.config.get(
                "user_agent", 
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        })
        self.movie_data = MovieData()
        self.timeout = self.config.get("timeout", 10)
        self.run_mode = self.config.get("run_mode", "interactive")
        self.template_manager = TemplateManager()
        self.nfo_template = self.config.get("nfo_template", "standard")
    
    @property
    @abstractmethod
    def site_name(self) -> str:
        """Return the name of the supported site."""
        pass
    
    @property
    @abstractmethod
    def site_domain(self) -> str:
        """Return the domain of the supported site."""
        pass
    
    @abstractmethod
    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from URL.
        
        Args:
            url: The movie URL
            
        Returns:
            Product ID if found, None otherwise
        """
        pass
    
    @abstractmethod
    def scrape_movie_info(self, url: str) -> bool:
        """Scrape movie information from URL.
        
        Args:
            url: The movie URL
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ScrapingError: If scraping fails
            NetworkError: If network request fails
        """
        pass
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL belongs to supported site.
        
        Args:
            url: The URL to validate
            
        Returns:
            True if URL is valid for this generator
        """
        return self.site_domain in url
    
    def make_request(self, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling.
        
        Args:
            url: The URL to request
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            NetworkError: If request fails
        """
        try:
            kwargs.setdefault('timeout', self.timeout)
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise NetworkError(f"Network request failed: {e}")
    
    def manual_input_correction(self) -> bool:
        """Allow manual correction of movie data.
        
        Returns:
            True if correction completed successfully
        """
        print("\n" + "=" * 50)
        print("📝 请检查并修正以下信息")
        print("=" * 50)
        
        # Title correction
        print(f"当前标题: {self.movie_data.title}")
        new_title = input("请输入修正后的标题(直接回车保持当前): ").strip()
        if new_title:
            self.movie_data.title = new_title
            self.movie_data.original_title = new_title
            self.movie_data.sort_title = self.movie_data.generate_sort_title()
        
        # Year correction
        print(f"\n当前年份: {self.movie_data.year}")
        new_year = input("请输入修正后的年份: ").strip()
        if new_year:
            self.movie_data.year = new_year
        
        # Plot correction
        print(f"\n当前剧情简介:\n{self.movie_data.plot}")
        new_plot = input("请输入修正后的剧情简介(直接回车保持当前):\n").strip()
        if new_plot:
            self.movie_data.plot = new_plot
        
        # Director correction
        print(f"\n当前导演: {self.movie_data.director}")
        new_director = input("请输入修正后的导演: ").strip()
        if new_director:
            self.movie_data.director = new_director
            self.movie_data.credits = new_director
        
        # Runtime correction
        print(f"\n当前片长: {self.movie_data.runtime}分钟")
        new_runtime = input("请输入修正后的片长: ").strip()
        if new_runtime:
            self.movie_data.runtime = new_runtime
        
        # Premiered correction
        print(f"\n当前上映日期: {self.movie_data.premiered or '未设置'}")
        new_premiered = input("请输入上映日期(YYYY-MM-DD): ").strip()
        if new_premiered:
            self.movie_data.premiered = new_premiered
            self.movie_data.release_date = new_premiered
        
        # Thumb correction
        print(f"\n当前海报URL: {self.movie_data.thumb or '未设置'}")
        new_thumb = input("请输入海报图片URL: ").strip()
        if new_thumb:
            self.movie_data.thumb = new_thumb
        
        # Fanart correction
        print(f"\n当前背景图URL: {self.movie_data.fanart or '未设置'}")
        new_fanart = input("请输入背景图URL: ").strip()
        if new_fanart:
            self.movie_data.fanart = new_fanart
        
        # Actors correction
        print(f"\n当前演员信息:")
        for i, actor in enumerate(self.movie_data.actors):
            print(f"  {i+1}. {actor.name} 饰演 {actor.role}")
        
        modify_actors = input("\n是否修改演员信息? (y/n): ").lower()
        if modify_actors == "y":
            self.movie_data.actors = []
            print("请输入演员信息(输入'done'结束):")
            while True:
                name = input("演员姓名: ").strip()
                if name.lower() == "done":
                    break
                role = input("扮演角色: ").strip()
                self.movie_data.add_actor(name, role)
                print("---")
        
        # Genres correction
        print(f"\n当前影片风格: {', '.join(self.movie_data.genres)}")
        modify_genres = input("是否修改风格信息? (y/n): ").lower()
        if modify_genres == "y":
            self.movie_data.genres = []
            print("请输入影片风格(输入'done'结束):")
            while True:
                genre = input("风格: ").strip()
                if genre.lower() == "done":
                    break
                self.movie_data.genres.append(genre)
        
        return True
    
    def create_nfo_file(self, filename: Optional[str] = None) -> str:
        """Create NFO file from movie data using template system.
        
        Args:
            filename: Output filename, defaults to movie title
            
        Returns:
            Created filename
            
        Raises:
            ValidationError: If movie data is invalid
        """
        # Get appropriate template
        template = self.template_manager.get_template(self.nfo_template)
        
        # Generate XML content using template
        xml_content = template.create_nfo_xml(self.movie_data, self.site_name)
        
        # Save to file
        if not filename:
            filename = f"{self.movie_data.title}.nfo"
        
        with open(filename, "wb") as f:
            f.write(xml_content)
        
        print(f"\n✅ NFO文件已生成: {filename}")
        print(f"📋 使用模板: {self.nfo_template}")
        return filename
    
    def run(self, url: str) -> Optional[str]:
        """Main execution method.
        
        Args:
            url: The movie URL
            
        Returns:
            Generated NFO filename if successful, None otherwise
        """
        print(f"🎬 {self.site_name} NFO 文件生成器")
        print(f"📋 运行模式: {self._get_mode_description()}")
        print("=" * 40)
        
        if not self.validate_url(url):
            print(f"❌ URL不属于{self.site_name}网站")
            return None
        
        try:
            success = self.scrape_movie_info(url)
            if not success:
                if self.run_mode == "auto":
                    print("❌ 自动模式下爬取失败，无法继续")
                    return None
                else:
                    print("⚠️  自动爬取失败，请手动输入信息")
                    # Initialize with basic data
                    self.movie_data = MovieData(
                        product_id=self.extract_product_id(url) or "unknown",
                        year=str(2023),
                        runtime="120",
                        studio=self.site_name
                    )
            
            # Handle different run modes
            if self.run_mode == "auto":
                print("🤖 自动模式：跳过人工修正")
            elif self.run_mode == "manual":
                print("✋ 手动模式：需要人工修正所有信息")
                self.manual_input_correction()
            else:  # interactive mode
                if self._should_manual_correct():
                    self.manual_input_correction()
                else:
                    print("⚡ 自动生成模式：跳过人工修正")
            
            nfo_file = self.create_nfo_file()
            
            if nfo_file:
                print(f"\n🎉 完成！请将 '{nfo_file}' 与视频文件放在同一目录下")
                print("💡 提示: 确保NFO文件与视频文件主文件名相同")
            
            return nfo_file
            
        except Exception as e:
            print(f"❌ 生成过程中出现错误: {e}")
            return None
    
    def _get_mode_description(self) -> str:
        """Get description of current run mode."""
        mode_descriptions = {
            "auto": "自动模式 (无人工干预)",
            "manual": "手动模式 (需要人工修正)",
            "interactive": "交互模式 (可选择是否修正)"
        }
        return mode_descriptions.get(self.run_mode, "未知模式")
    
    def _should_manual_correct(self) -> bool:
        """Ask user if they want to manually correct data in interactive mode."""
        if not self.config.get("manual_input", True):
            return False
        
        while True:
            choice = input("\n是否需要手动修正信息? (y/n/auto): ").lower().strip()
            if choice in ['y', 'yes', '是']:
                return True
            elif choice in ['n', 'no', '否']:
                return False
            elif choice in ['auto', '自动']:
                # Switch to auto mode for this session
                self.run_mode = "auto"
                return False
            else:
                print("请输入 y(是)/n(否)/auto(自动)")
    
    def get_template_for_site(self) -> str:
        """Get appropriate template for the site.
        
        Returns:
            Template name
        """
        # Override in subclasses to return appropriate template
        return "standard"
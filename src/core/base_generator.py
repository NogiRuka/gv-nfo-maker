"""Base NFO Generator abstract class."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom

from .movie_data import MovieData, Actor, Rating
from .exceptions import ScrapingError, ValidationError, NetworkError


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
        """Create NFO file from movie data.
        
        Args:
            filename: Output filename, defaults to movie title
            
        Returns:
            Created filename
            
        Raises:
            ValidationError: If movie data is invalid
        """
        if not self.movie_data.validate():
            raise ValidationError("Movie data validation failed")
        
        # Create XML structure
        movie = ET.Element("movie")
        
        # Basic information
        ET.SubElement(movie, "title").text = self.movie_data.title
        ET.SubElement(movie, "originaltitle").text = self.movie_data.original_title
        ET.SubElement(movie, "sorttitle").text = self.movie_data.sort_title
        
        # Ratings
        if self.movie_data.ratings:
            ratings = ET.SubElement(movie, "ratings")
            for rating in self.movie_data.ratings:
                rating_elem = ET.SubElement(
                    ratings, "rating", 
                    name=rating.name, 
                    max=str(rating.max_rating),
                    default=str(rating.is_default).lower()
                )
                ET.SubElement(rating_elem, "value").text = str(rating.value)
                ET.SubElement(rating_elem, "votes").text = str(rating.votes)
        else:
            # Default rating
            ratings = ET.SubElement(movie, "ratings")
            rating = ET.SubElement(
                ratings, "rating", name="default", max="10", default="true"
            )
            ET.SubElement(rating, "value").text = "7.5"
            ET.SubElement(rating, "votes").text = "1000"
        
        ET.SubElement(movie, "userrating").text = str(self.movie_data.user_rating)
        ET.SubElement(movie, "top250").text = str(self.movie_data.top250)
        ET.SubElement(movie, "year").text = self.movie_data.year
        ET.SubElement(movie, "plot").text = self.movie_data.plot
        ET.SubElement(movie, "outline").text = self.movie_data.outline
        ET.SubElement(movie, "tagline").text = self.movie_data.tagline
        ET.SubElement(movie, "runtime").text = self.movie_data.runtime
        
        # Images
        if self.movie_data.thumb:
            ET.SubElement(movie, "thumb", aspect="poster").text = self.movie_data.thumb
        
        if self.movie_data.fanart:
            fanart = ET.SubElement(movie, "fanart")
            ET.SubElement(fanart, "thumb").text = self.movie_data.fanart
        
        # Certification and dates
        ET.SubElement(movie, "mpaa").text = self.movie_data.mpaa
        ET.SubElement(movie, "premiered").text = self.movie_data.premiered
        ET.SubElement(movie, "releasedate").text = self.movie_data.release_date
        ET.SubElement(movie, "certification").text = self.movie_data.certification
        
        # IDs
        if self.movie_data.product_id:
            ET.SubElement(movie, "id").text = f"{self.site_name.lower()}-{self.movie_data.product_id}"
        
        for id_type, id_value in self.movie_data.unique_ids.items():
            is_default = id_type == self.site_name.lower()
            ET.SubElement(
                movie, "uniqueid", 
                type=id_type, 
                default=str(is_default).lower()
            ).text = id_value
        
        # Genres and tags
        for genre in self.movie_data.genres:
            ET.SubElement(movie, "genre").text = genre
        
        for tag in self.movie_data.tags:
            ET.SubElement(movie, "tag").text = tag
        
        # Studio and trailer
        ET.SubElement(movie, "studio").text = self.movie_data.studio
        ET.SubElement(movie, "trailer").text = self.movie_data.trailer
        
        # Actors
        for actor in self.movie_data.actors:
            actor_elem = ET.SubElement(movie, "actor")
            ET.SubElement(actor_elem, "name").text = actor.name
            ET.SubElement(actor_elem, "role").text = actor.role
            ET.SubElement(actor_elem, "order").text = str(actor.order)
            ET.SubElement(actor_elem, "thumb").text = actor.thumb
        
        # Director and credits
        ET.SubElement(movie, "director").text = self.movie_data.director
        ET.SubElement(movie, "credits").text = self.movie_data.credits
        
        # Set and country
        ET.SubElement(movie, "set").text = self.movie_data.set_name
        ET.SubElement(movie, "country").text = self.movie_data.country
        
        # Generate pretty XML
        rough_string = ET.tostring(movie, "utf-8")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")
        
        # Save to file
        if not filename:
            filename = f"{self.movie_data.title}.nfo"
        
        with open(filename, "wb") as f:
            f.write(pretty_xml)
        
        print(f"\n✅ NFO文件已生成: {filename}")
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
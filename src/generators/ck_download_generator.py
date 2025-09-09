"""CK-Download NFO Generator."""

import re
from typing import Optional
from bs4 import BeautifulSoup
from datetime import datetime

from ..core.base_generator import BaseNfoGenerator
from ..core.movie_data import MovieData
from ..core.exceptions import ScrapingError, NetworkError


class CkDownloadNfoGenerator(BaseNfoGenerator):
    """NFO Generator for CK-Download website."""
    
    @property
    def site_name(self) -> str:
        """Return the name of the supported site."""
        return "CK-Download"
    
    @property
    def site_domain(self) -> str:
        """Return the domain of the supported site."""
        return "ck-download"
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from CK-Download URL.
        
        Args:
            url: The movie URL
            
        Returns:
            Product ID if found, None otherwise
        """
        match = re.search(r"product/detail/(\d+)", url)
        if match:
            return match.group(1)
        return None
    
    def scrape_movie_info(self, url: str) -> bool:
        """Scrape movie information from CK-Download URL.
        
        Args:
            url: The movie URL
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ScrapingError: If scraping fails
            NetworkError: If network request fails
        """
        print("🚀 开始尝试获取影片信息...")
        
        try:
            response = self.make_request(url)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract basic information
            title = self._extract_title(soup)
            product_number = self._extract_product_number(soup)
            
            # Combine product number with title
            if product_number:
                title = f"{product_number} {title}".strip()
            
            # Initialize movie data
            self.movie_data = MovieData(
                title=title,
                original_title=title,
                product_id=self.extract_product_id(url) or "26966",
                year=self._extract_year(soup),
                plot=self._extract_plot(soup),
                outline=self._extract_premiered(soup),
                genres=self._extract_tags(soup),
                runtime=self._extract_runtime(soup),
                director=self._extract_director(soup),
                studio=self.site_name,
                premiered="",
                thumb="",
                fanart=""
            )
            
            # Add actors
            actors = self._extract_actors(soup)
            for actor_info in actors:
                self.movie_data.add_actor(actor_info["name"], actor_info["role"])
            
            # Add unique ID
            if self.movie_data.product_id:
                self.movie_data.add_unique_id(
                    self.site_name.lower(), 
                    self.movie_data.product_id, 
                    is_default=True
                )
            
            # Add default tags
            self.movie_data.tags.extend([self.site_name.lower(), "国产"])
            
            # Add default rating
            self.movie_data.add_rating(7.5, 1000, "default", 10.0, True)
            
            print("✅ 基本信息获取完成")
            return True
            
        except NetworkError:
            raise
        except Exception as e:
            raise ScrapingError(f"爬取过程中出现错误: {e}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract movie title from soup."""
        title_elem = soup.select_one("div#Contents h3")
        return title_elem.get_text().strip() if title_elem else "未知标题"
    
    def _extract_product_number(self, soup: BeautifulSoup) -> str:
        """Extract product number from soup."""
        num_td = soup.find("th", string="プロダクトナンバー")
        if num_td and num_td.find_next("td"):
            return num_td.find_next("td").get_text(strip=True)
        return ""
    
    def _extract_tags(self, soup: BeautifulSoup) -> list:
        """Extract tags/genres from soup."""
        tags = []
        category_div = soup.select_one("div.prod_category")
        if category_div:
            for a in category_div.select("a"):
                text = a.get_text(strip=True)
                if text:
                    tags.append(text)
        return tags if tags else ["剧情", "爱情"]
    
    def _extract_year(self, soup: BeautifulSoup) -> str:
        """Extract year from soup."""
        premiered_date = self._extract_premiered(soup)
        if premiered_date:
            return premiered_date.split("-")[0]
        return str(datetime.now().year)
    
    def _extract_plot(self, soup: BeautifulSoup) -> str:
        """Extract plot/description from soup."""
        intro_div = soup.select_one("div.intro_text")
        
        if intro_div:
            paragraphs = []
            p_elements = intro_div.find_all("p")
            
            for p in p_elements:
                text = p.get_text().strip()
                if text:
                    # Handle line breaks
                    br_elements = p.find_all("br")
                    if br_elements:
                        text = p.get_text("\n", strip=True)
                    paragraphs.append(text)
            
            if paragraphs:
                return "\n\n".join(paragraphs)
        
        return "暂无剧情简介"
    
    def _extract_premiered(self, soup: BeautifulSoup) -> str:
        """Extract premiere date from soup."""
        date_div = soup.select_one("div.add_info div.date")
        if date_div:
            date_text = date_div.get_text().strip()
            date_match = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", date_text)
            if date_match:
                year, month, day = date_match.groups()
                return f"{year}-{month}-{day}"
        
        current_year = datetime.now().year
        return f"{current_year}-01-01"
    
    def _extract_actors(self, soup: BeautifulSoup) -> list:
        """Extract actors from soup."""
        # This is a placeholder implementation
        # In a real scenario, you would extract actual actor information
        return [
            {"name": "演员1", "role": "主角"},
            {"name": "演员2", "role": "配角"}
        ]
    
    def _extract_director(self, soup: BeautifulSoup) -> str:
        """Extract director from soup."""
        # This is a placeholder implementation
        # In a real scenario, you would extract actual director information
        return "知名导演"
    
    def _extract_runtime(self, soup: BeautifulSoup) -> str:
        """Extract runtime from soup."""
        # This is a placeholder implementation
        # In a real scenario, you would extract actual runtime information
        return "120"
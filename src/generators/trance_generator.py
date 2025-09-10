"""Trance Video NFO Generator."""

import re
from typing import Optional
from bs4 import BeautifulSoup
from datetime import datetime

from ..core.base_generator import BaseNfoGenerator
from ..core.movie_data import MovieData
from ..core.exceptions import ScrapingError, NetworkError


class TranceMusicNfoGenerator(BaseNfoGenerator):
    """NFO Generator for Trance Video websites."""
    
    @property
    def site_name(self) -> str:
        """Return the name of the supported site."""
        return "Trance-Video"
    
    @property
    def site_domain(self) -> str:
        """Return the domain of the supported site."""
        return "trance-video.com"
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from Trance Video URL.
        
        Args:
            url: The video URL
            
        Returns:
            Product ID if found, None otherwise
        """
        # Support trance-video.com URL pattern
        patterns = [
            r"/product/detail/(\d+)",
            r"/(\d+)/?$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def scrape_movie_info(self, url: str) -> bool:
        """Scrape video information from Trance Video URL.
        
        Args:
            url: The video URL
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ScrapingError: If scraping fails
            NetworkError: If network request fails
        """
        print("🚀 开始尝试获取视频信息...")
        
        try:
            response = self.make_request(url)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract basic information
            title = self._extract_title(soup)
            work_id = self._extract_work_id(soup)
            
            # Combine work ID with title
            if work_id:
                title = f"[{work_id}] {title}".strip()
            
            # Initialize movie data
            self.movie_data = MovieData(
            title=title,
            original_title=title,
            product_id=self.extract_product_id(url) or "unknown",
            year=self._extract_year(soup),
            plot=self._extract_description(soup),
            outline=self._extract_release_date(soup),
            genres=self._extract_genres(soup),
            runtime=self._extract_duration(soup),
            director=self._extract_maker(soup),
            studio=self._extract_label(soup) or self.site_name,
            premiered=self._extract_release_date(soup),
            thumb=self._extract_artwork(soup),
            fanart=self._extract_background(soup),
            maker=self._extract_maker(soup),
            label=self._extract_label(soup) or self.site_name,
            series_name=self._extract_series(soup)
        )
            
            # Add performers as actors
            performers = self._extract_performers(soup)
            for i, performer_name in enumerate(performers):
                self.movie_data.add_actor(performer_name, "出演者")
            
            # Add unique ID
            if self.movie_data.product_id:
                self.movie_data.add_unique_id(
                    self.site_name.lower(), 
                    self.movie_data.product_id, 
                    is_default=True
                )
            
            # Add video-specific tags
            self.movie_data.tags.extend([
                self.site_name.lower(), 
                "成人视频",
                "日本"
            ])
            
            # Add default rating
            self.movie_data.add_rating(7.5, 100, "default", 10.0, True)
            
            # Set video-specific properties
        self.movie_data.mpaa = "XXX"
        self.movie_data.certification = "R18+"
        self.movie_data.country = "日本"
        
        # Use adult template for this site
        self.nfo_template = "adult"
            
            print("✅ 视频信息获取完成")
            return True
            
        except NetworkError:
            raise
        except Exception as e:
            raise ScrapingError(f"爬取过程中出现错误: {e}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract video title from soup."""
        # Try multiple selectors for trance-video.com
        selectors = [
            "h1",
            ".title",
            "title"
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                # Clean up title (remove site name, etc.)
                title = re.sub(r'\s*-\s*.*?(trance|video|market).*$', '', title, flags=re.IGNORECASE)
                if title:
                    return title
        
        return "未知视频标题"
    
    def _extract_work_id(self, soup: BeautifulSoup) -> str:
        """Extract work ID from soup."""
        # Look for work ID in the page
        work_id_selectors = [
            ".work-id",
            "[class*='work']",
            "[class*='id']"
        ]
        
        for selector in work_id_selectors:
            id_elem = soup.select_one(selector)
            if id_elem:
                return id_elem.get_text().strip()
        
        # Try to extract from text content
        text_content = soup.get_text()
        id_match = re.search(r'([A-Z]{2}-\d{2}-\d{4}-\d{2})', text_content)
        if id_match:
            return id_match.group(1)
        
        return ""
    
    def _extract_performers(self, soup: BeautifulSoup) -> list:
        """Extract performers from soup."""
        performers = []
        
        # Look for performer information
        performer_selectors = [
            ".performer",
            ".actor",
            ".cast",
            "[class*='performer']",
            "[class*='actor']"
        ]
        
        for selector in performer_selectors:
            performer_elems = soup.select(selector)
            for elem in performer_elems:
                performer_name = elem.get_text().strip()
                if performer_name and performer_name not in performers:
                    performers.append(performer_name)
        
        return performers if performers else ["未知出演者"]
    
    def _extract_genres(self, soup: BeautifulSoup) -> list:
        """Extract video genres from soup."""
        genres = []
        
        # Look for category tags
        genre_selectors = [
            ".category",
            ".genre",
            ".tag",
            "[class*='category']",
            "[class*='genre']"
        ]
        
        for selector in genre_selectors:
            genre_elems = soup.select(selector)
            for elem in genre_elems:
                genre = elem.get_text().strip()
                if genre and genre not in genres:
                    genres.append(genre)
        
        # Default genres if none found
        if not genres:
            genres = ["成人", "日本"]
        
        return genres
    
    def _extract_year(self, soup: BeautifulSoup) -> str:
        """Extract release year from soup."""
        release_date = self._extract_release_date(soup)
        if release_date:
            return release_date.split("-")[0]
        return str(datetime.now().year)
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract video description from soup."""
        desc_selectors = [
            ".description",
            ".summary",
            ".content",
            "[class*='desc']",
            "p"
        ]
        
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                desc_text = desc_elem.get_text().strip()
                if len(desc_text) > 20:  # Ensure it's substantial content
                    return desc_text
        
        return "精彩的成人视频作品。"
    
    def _extract_release_date(self, soup: BeautifulSoup) -> str:
        """Extract release date from soup."""
        date_selectors = [
            ".release-date",
            ".date",
            ".published",
            "[class*='date']",
            "time"
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text().strip()
                # Try to parse various date formats
                date_patterns = [
                    r"(\d{4})-(\d{2})-(\d{2})",
                    r"(\d{4})\.(\d{2})\.(\d{2})",
                    r"(\d{2})/(\d{2})/(\d{4})",
                    r"(\d{4})"
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, date_text)
                    if match:
                        if len(match.groups()) == 3:
                            if pattern.endswith(r"(\d{4})"):
                                # MM/DD/YYYY format
                                month, day, year = match.groups()
                                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            else:
                                # YYYY-MM-DD or YYYY.MM.DD format
                                year, month, day = match.groups()
                                return f"{year}-{month}-{day}"
                        else:
                            # Year only
                            year = match.group(1)
                            return f"{year}-01-01"
        
        current_year = datetime.now().year
        return f"{current_year}-01-01"
    
    def _extract_duration(self, soup: BeautifulSoup) -> str:
        """Extract video duration from soup."""
        duration_selectors = [
            ".duration",
            ".runtime",
            ".time",
            "[class*='duration']",
            "[class*='time']"
        ]
        
        for selector in duration_selectors:
            duration_elem = soup.select_one(selector)
            if duration_elem:
                duration_text = duration_elem.get_text().strip()
                # Convert HH:MM:SS or MM:SS to total minutes
                time_match = re.search(r"(?:(\d+):)?(\d+):(\d+)", duration_text)
                if time_match:
                    hours, minutes, seconds = time_match.groups()
                    hours = int(hours) if hours else 0
                    minutes = int(minutes)
                    seconds = int(seconds)
                    total_minutes = hours * 60 + minutes + (seconds / 60)
                    return str(int(total_minutes))
        
        return "30"  # Default 30 minutes for videos
    
    def _extract_maker(self, soup: BeautifulSoup) -> str:
        """Extract maker/director from soup."""
        maker_selectors = [
            ".maker",
            ".director",
            ".producer",
            "[class*='maker']",
            "[class*='director']"
        ]
        
        for selector in maker_selectors:
            maker_elem = soup.select_one(selector)
            if maker_elem:
                return maker_elem.get_text().strip()
        
        return "未知制作商"
    
    def _extract_label(self, soup: BeautifulSoup) -> str:
        """Extract label/studio from soup."""
        label_selectors = [
            ".label",
            ".studio",
            ".publisher",
            "[class*='label']",
            "[class*='studio']"
        ]
        
        for selector in label_selectors:
            label_elem = soup.select_one(selector)
            if label_elem:
                return label_elem.get_text().strip()
        
        return ""
    
    def _extract_artwork(self, soup: BeautifulSoup) -> str:
        """Extract poster/cover image from soup."""
        img_selectors = [
            ".poster img",
            ".cover img",
            ".thumbnail img",
            ".preview img",
            "img[class*='cover']",
            "img[class*='poster']",
            "img[class*='thumb']"
        ]
        
        for selector in img_selectors:
            img_elem = soup.select_one(selector)
            if img_elem:
                src = img_elem.get('src') or img_elem.get('data-src')
                if src:
                    return src if src.startswith('http') else f"https:{src}"
        
        return ""
    
    def _extract_background(self, soup: BeautifulSoup) -> str:
        """Extract background image from soup."""
        # For videos, background is often the same as artwork
        return self._extract_artwork(soup)
    
    def _extract_series(self, soup: BeautifulSoup) -> str:
        """Extract series name from soup."""
        series_selectors = [
            ".series",
            ".collection",
            "[class*='series']",
            "[class*='collection']"
        ]
        
        for selector in series_selectors:
            series_elem = soup.select_one(selector)
            if series_elem:
                return series_elem.get_text().strip()
        
        return ""
    
    def get_template_for_site(self) -> str:
        """Get appropriate template for trance video site."""
        return "adult"
"""Trance Music NFO Generator."""

import re
from typing import Optional
from bs4 import BeautifulSoup
from datetime import datetime

from ..core.base_generator import BaseNfoGenerator
from ..core.movie_data import MovieData
from ..core.exceptions import ScrapingError, NetworkError


class TranceMusicNfoGenerator(BaseNfoGenerator):
    """NFO Generator for Trance Music websites."""
    
    @property
    def site_name(self) -> str:
        """Return the name of the supported site."""
        return "Trance-Music"
    
    @property
    def site_domain(self) -> str:
        """Return the domain of the supported site."""
        return "trance"
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from Trance Music URL.
        
        Args:
            url: The music/video URL
            
        Returns:
            Product ID if found, None otherwise
        """
        # Support multiple URL patterns for trance music sites
        patterns = [
            r"/track/(\d+)",
            r"/music/(\d+)",
            r"/video/(\d+)",
            r"/release/(\d+)",
            r"id=(\d+)",
            r"/(\d+)/?$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def scrape_movie_info(self, url: str) -> bool:
        """Scrape music/video information from Trance Music URL.
        
        Args:
            url: The music/video URL
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ScrapingError: If scraping fails
            NetworkError: If network request fails
        """
        print("🚀 开始尝试获取音乐/视频信息...")
        
        try:
            response = self.make_request(url)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract basic information
            title = self._extract_title(soup)
            artist = self._extract_artist(soup)
            
            # Combine artist with title for music content
            if artist:
                title = f"{artist} - {title}".strip()
            
            # Initialize movie data (adapted for music content)
            self.movie_data = MovieData(
                title=title,
                original_title=title,
                product_id=self.extract_product_id(url) or "unknown",
                year=self._extract_year(soup),
                plot=self._extract_description(soup),
                outline=self._extract_release_date(soup),
                genres=self._extract_genres(soup),
                runtime=self._extract_duration(soup),
                director=self._extract_producer(soup),
                studio=self._extract_label(soup) or self.site_name,
                premiered="",
                thumb=self._extract_artwork(soup),
                fanart=self._extract_background(soup)
            )
            
            # Add artists as actors
            artists = self._extract_all_artists(soup)
            for i, artist_name in enumerate(artists):
                role = "主唱" if i == 0 else "合作艺人"
                self.movie_data.add_actor(artist_name, role)
            
            # Add unique ID
            if self.movie_data.product_id:
                self.movie_data.add_unique_id(
                    self.site_name.lower(), 
                    self.movie_data.product_id, 
                    is_default=True
                )
            
            # Add music-specific tags
            self.movie_data.tags.extend([
                self.site_name.lower(), 
                "电子音乐", 
                "trance",
                "音乐视频"
            ])
            
            # Add default rating
            self.movie_data.add_rating(8.0, 500, "default", 10.0, True)
            
            # Set music-specific properties
            self.movie_data.mpaa = "G"  # Music is generally all-ages
            self.movie_data.certification = "G"
            self.movie_data.country = "国际"
            
            print("✅ 音乐信息获取完成")
            return True
            
        except NetworkError:
            raise
        except Exception as e:
            raise ScrapingError(f"爬取过程中出现错误: {e}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract track/video title from soup."""
        # Try multiple selectors for different trance music sites
        selectors = [
            "h1.track-title",
            "h1.song-title",
            ".title h1",
            "h1",
            ".track-name",
            ".song-name",
            "title"
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                # Clean up title (remove site name, etc.)
                title = re.sub(r'\s*-\s*.*?(trance|music|radio).*$', '', title, flags=re.IGNORECASE)
                if title:
                    return title
        
        return "未知音乐标题"
    
    def _extract_artist(self, soup: BeautifulSoup) -> str:
        """Extract main artist from soup."""
        selectors = [
            ".artist-name",
            ".track-artist",
            ".by-artist",
            "[class*='artist']",
            ".performer"
        ]
        
        for selector in selectors:
            artist_elem = soup.select_one(selector)
            if artist_elem:
                return artist_elem.get_text().strip()
        
        return ""
    
    def _extract_all_artists(self, soup: BeautifulSoup) -> list:
        """Extract all artists from soup."""
        artists = []
        main_artist = self._extract_artist(soup)
        if main_artist:
            artists.append(main_artist)
        
        # Look for featured artists
        feat_selectors = [
            ".featured-artists",
            ".collaborators",
            "[class*='feat']"
        ]
        
        for selector in feat_selectors:
            feat_elems = soup.select(selector)
            for elem in feat_elems:
                artist_name = elem.get_text().strip()
                if artist_name and artist_name not in artists:
                    artists.append(artist_name)
        
        return artists if artists else ["未知艺人"]
    
    def _extract_genres(self, soup: BeautifulSoup) -> list:
        """Extract music genres from soup."""
        genres = []
        
        # Look for genre tags
        genre_selectors = [
            ".genre",
            ".tag",
            ".style",
            "[class*='genre']",
            ".categories a"
        ]
        
        for selector in genre_selectors:
            genre_elems = soup.select(selector)
            for elem in genre_elems:
                genre = elem.get_text().strip()
                if genre and genre not in genres:
                    genres.append(genre)
        
        # Default trance genres if none found
        if not genres:
            genres = ["Trance", "Electronic", "Dance"]
        
        return genres
    
    def _extract_year(self, soup: BeautifulSoup) -> str:
        """Extract release year from soup."""
        release_date = self._extract_release_date(soup)
        if release_date:
            return release_date.split("-")[0]
        return str(datetime.now().year)
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract track/video description from soup."""
        desc_selectors = [
            ".description",
            ".track-info",
            ".about",
            ".summary",
            "[class*='desc']"
        ]
        
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                return desc_elem.get_text().strip()
        
        return "精彩的电子音乐作品，带您进入trance的音乐世界。"
    
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
        """Extract track duration from soup."""
        duration_selectors = [
            ".duration",
            ".length",
            ".time",
            "[class*='duration']",
            "[class*='time']"
        ]
        
        for selector in duration_selectors:
            duration_elem = soup.select_one(selector)
            if duration_elem:
                duration_text = duration_elem.get_text().strip()
                # Convert MM:SS to total minutes
                time_match = re.search(r"(\d+):(\d+)", duration_text)
                if time_match:
                    minutes, seconds = map(int, time_match.groups())
                    total_minutes = minutes + (seconds / 60)
                    return str(int(total_minutes))
        
        return "4"  # Default 4 minutes for music tracks
    
    def _extract_producer(self, soup: BeautifulSoup) -> str:
        """Extract producer/remixer from soup."""
        producer_selectors = [
            ".producer",
            ".remixer",
            ".credits .producer",
            "[class*='producer']"
        ]
        
        for selector in producer_selectors:
            producer_elem = soup.select_one(selector)
            if producer_elem:
                return producer_elem.get_text().strip()
        
        # Fallback to main artist
        return self._extract_artist(soup) or "未知制作人"
    
    def _extract_label(self, soup: BeautifulSoup) -> str:
        """Extract record label from soup."""
        label_selectors = [
            ".label",
            ".record-label",
            ".publisher",
            "[class*='label']"
        ]
        
        for selector in label_selectors:
            label_elem = soup.select_one(selector)
            if label_elem:
                return label_elem.get_text().strip()
        
        return ""
    
    def _extract_artwork(self, soup: BeautifulSoup) -> str:
        """Extract artwork/cover image from soup."""
        img_selectors = [
            ".artwork img",
            ".cover img",
            ".album-art img",
            ".track-image img",
            "img[class*='cover']",
            "img[class*='artwork']"
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
        # For music, background is often the same as artwork
        return self._extract_artwork(soup)
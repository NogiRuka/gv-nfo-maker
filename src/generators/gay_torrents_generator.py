"""Gay Torrents NFO生成器。

专门用于Gay Torrents网站的NFO文件生成。
"""

import re
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from datetime import datetime

from ..core.base_generator import BaseNfoGenerator
from ..core.movie_data import MovieData
from ..core.exceptions import ScrapingError, NetworkError


class GayTorrentsNfoGenerator(BaseNfoGenerator):
    """Gay Torrents网站的NFO生成器。
    
    支持从Gay Torrents网站爬取电影信息并生成标准NFO文件。
    """
    
    @property
    def site_name(self) -> str:
        """返回支持的网站名称。"""
        return "Gay-Torrents"
    
    @property
    def site_domain(self) -> str:
        """返回支持的网站域名。"""
        return "gay-torrents.net"
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """从Gay Torrents URL中提取torrent ID。
        
        Args:
            url: 电影URL
            
        Returns:
            找到则返回torrent ID，否则返回None
            
        支持的URL格式：
        - https://www.gay-torrents.net/torrentdetails.php?torrentid=xxxxx
        """
        match = re.search(r"torrentid=([a-f0-9]+)", url)
        if match:
            return match.group(1)
        return None
    
    def scrape_movie_info(self, url: str) -> bool:
        """从Gay Torrents URL爬取电影信息。
        
        Args:
            url: 电影URL
            
        Returns:
            成功返回True，失败返回False
            
        Raises:
            ScrapingError: 爬取失败时抛出
            NetworkError: 网络请求失败时抛出
        """
        print("🚀 开始尝试获取Gay Torrents影片信息...")
        
        try:
            # 由于网站需要登录，我们需要处理登录状态
            response = self.make_request(url)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 检查是否需要登录
            if "You are not logged in" in response.text or "log in" in response.text.lower():
                print("⚠️ 检测到需要登录访问，将使用默认信息生成NFO")
                return self._generate_default_info(url)
            
            # Extract basic information
            title = self._extract_title(soup)
            
            # 初始化电影数据
            self.movie_data = MovieData(
                title=title,
                original_title=title,
                product_id=self.extract_product_id(url) or "unknown",
                year=self._extract_year(soup),
                plot=self._extract_plot(soup),
                outline="",  # 概要默认空
                genres=self._extract_genres(soup),
                runtime=self._extract_runtime(soup),
                studio=self.site_name,
                release_date=self._extract_premiered(soup),
                poster=self._extract_poster(soup),  # 封面图片URL
                imdb_id=f"GT-{self.extract_product_id(url) or 'unknown'}"
            )
            
            # 添加演员信息
            actors = self._extract_actors(soup)
            for actor_info in actors:
                self.movie_data.add_actor(actor_info["name"], "Actor")
            
            # 添加标签
            self.movie_data.tags.extend([self.movie_data.imdb_id, "Gay", "Adult", "Gay-Torrents"])
            
            print("✅ 影片信息获取成功")
            return True
            
        except Exception as e:
            print(f"❌ 爬取失败: {e}")
            # 如果爬取失败，生成默认信息
            return self._generate_default_info(url)
    
    def _generate_default_info(self, url: str) -> bool:
        """生成默认的电影信息（当无法访问网站时）。
        
        Args:
            url: 电影URL
            
        Returns:
            True
        """
        torrent_id = self.extract_product_id(url) or "unknown"
        
        self.movie_data = MovieData(
            title=f"Gay Torrents Movie {torrent_id}",
            original_title=f"Gay Torrents Movie {torrent_id}",
            product_id=torrent_id,
            year=str(datetime.now().year),
            plot="这是一部来自Gay Torrents的成人影片。由于网站访问限制，无法获取详细信息。",
            outline="Gay Torrents成人影片",
            genres=["Adult", "Gay"],
            runtime="120",  # 默认120分钟
            studio=self.site_name,
            release_date=datetime.now().strftime("%Y-%m-%d"),
            poster="",  # 无封面
            imdb_id=f"GT-{torrent_id}"
        )
        
        # 添加默认标签
        self.movie_data.tags.extend([self.movie_data.imdb_id, "Gay", "Adult", "Gay-Torrents"])
        
        print("✅ 已生成默认影片信息")
        return True
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取影片标题。"""
        # 尝试多种选择器
        selectors = [
            "h1",
            ".torrent-title",
            "title",
            ".main-title"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and "Gay Torrents" not in title:
                    return title
        
        return "Unknown Gay Torrents Movie"
    
    def _extract_year(self, soup: BeautifulSoup) -> str:
        """提取发行年份。"""
        # 尝试从标题或描述中提取年份
        text = soup.get_text()
        year_match = re.search(r"\b(19|20)\d{2}\b", text)
        if year_match:
            return year_match.group()
        return str(datetime.now().year)
    
    def _extract_plot(self, soup: BeautifulSoup) -> str:
        """提取剧情简介。"""
        # 尝试多种选择器
        selectors = [
            ".description",
            ".plot",
            ".summary",
            ".torrent-description"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                plot = element.get_text(strip=True)
                if plot and len(plot) > 20:
                    return plot
        
        return "这是一部来自Gay Torrents的成人影片。"
    
    def _extract_genres(self, soup: BeautifulSoup) -> List[str]:
        """提取影片类型。"""
        genres = ["Adult", "Gay"]
        
        # 尝试从页面中提取更多类型信息
        text = soup.get_text().lower()
        
        # 常见的Gay成人影片类型
        genre_keywords = {
            "bareback": "Bareback",
            "twink": "Twink", 
            "bear": "Bear",
            "muscle": "Muscle",
            "daddy": "Daddy",
            "amateur": "Amateur",
            "oral": "Oral",
            "anal": "Anal",
            "group": "Group",
            "solo": "Solo"
        }
        
        for keyword, genre in genre_keywords.items():
            if keyword in text:
                genres.append(genre)
        
        return list(set(genres))  # 去重
    
    def _extract_runtime(self, soup: BeautifulSoup) -> str:
        """提取影片时长。"""
        # 尝试从页面中提取时长信息
        text = soup.get_text()
        
        # 匹配时长格式：XX分钟、XX min、XX:XX等
        runtime_patterns = [
            r"(\d+)\s*分钟",
            r"(\d+)\s*min",
            r"(\d+):(\d+)",
            r"Duration:\s*(\d+)"
        ]
        
        for pattern in runtime_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if ":" in pattern:
                    # 处理 HH:MM 格式
                    hours, minutes = match.groups()
                    return str(int(hours) * 60 + int(minutes))
                else:
                    return match.group(1)
        
        return "120"  # 默认120分钟
    
    def _extract_premiered(self, soup: BeautifulSoup) -> str:
        """提取首映日期。"""
        # 尝试从页面中提取日期信息
        text = soup.get_text()
        
        # 匹配日期格式
        date_patterns = [
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{2}/\d{2}/\d{4})",
            r"(\d{2}-\d{2}-\d{4})"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                try:
                    # 尝试解析日期
                    if "/" in date_str:
                        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
                    elif "-" in date_str and len(date_str.split("-")[0]) == 4:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    else:
                        date_obj = datetime.strptime(date_str, "%m-%d-%Y")
                    return date_obj.strftime("%Y-%m-%d")
                except:
                    continue
        
        return datetime.now().strftime("%Y-%m-%d")
    
    def _extract_poster(self, soup: BeautifulSoup) -> str:
        """提取封面图片URL。"""
        # 尝试多种选择器
        selectors = [
            "img.poster",
            ".torrent-image img",
            ".preview img",
            "img[src*='preview']",
            "img[src*='thumb']"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get("src"):
                src = element.get("src")
                if src.startswith("http"):
                    return src
                elif src.startswith("/"):
                    return f"https://{self.site_domain}{src}"
        
        return ""
    
    def _extract_actors(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """提取演员信息。"""
        actors = []
        
        # 尝试从页面中提取演员信息
        text = soup.get_text()
        
        # 查找可能的演员名称模式
        actor_patterns = [
            r"Starring:\s*([^,\n]+)",
            r"Actor:\s*([^,\n]+)",
            r"Performer:\s*([^,\n]+)"
        ]
        
        for pattern in actor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                actor_name = match.strip()
                if actor_name and len(actor_name) < 50:  # 合理的名字长度
                    actors.append({"name": actor_name})
        
        # 如果没有找到演员，添加默认信息
        if not actors:
            actors.append({"name": "Unknown Performer"})
        
        return actors
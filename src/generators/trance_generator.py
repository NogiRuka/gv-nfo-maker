"""Trance Video NFO生成器。

专门用于Trance Video网站的成人视频NFO文件生成。
"""

import re
from typing import Optional
from bs4 import BeautifulSoup
from datetime import datetime

from ..core.base_generator import BaseNfoGenerator
from ..core.movie_data import MovieData
from ..core.exceptions import ScrapingError, NetworkError


class TranceMusicNfoGenerator(BaseNfoGenerator):
    """Trance Video网站的NFO生成器。
    
    支持从Trance Video网站爬取成人视频信息并生成标准NFO文件。
    使用成人内容专用模板。
    """
    
    @property
    def site_name(self) -> str:
        """返回支持的网站名称。"""
        return "Trance-Video"
    
    @property
    def site_domain(self) -> str:
        """返回支持的网站域名。"""
        return "trance-video.com"
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """从Trance Video URL中提取产品ID。
        
        Args:
            url: 视频URL
            
        Returns:
            找到则返回产品ID，否则返回None
            
        支持的URL格式：
        - https://www.trance-video.com/product/detail/39661
        - https://www.trance-video.com/39661
        """
        # 支持trance-video.com URL模式
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
        """从Trance Video URL爬取视频信息。
        
        Args:
            url: 视频URL
            
        Returns:
            成功返回True，失败返回False
            
        Raises:
            ScrapingError: 爬取失败时抛出
            NetworkError: 网络请求失败时抛出
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
            
            # 初始化电影数据
            self.movie_data = MovieData(
                title=title,
                original_title=title,
                product_id=self.extract_product_id(url) or "unknown",
                year=self._extract_year(soup),
                plot=self._extract_description(soup),
                outline="",  # 概要默认空
                genres=self._extract_genres(soup),
                runtime=self._extract_duration(soup),
                studio=self._extract_label(soup) or self.site_name,
                release_date=self._extract_release_date(soup),
                poster=self._extract_artwork(soup),  # 封面图片URL
                maker=self._extract_maker(soup),
                label=self._extract_label(soup) or self.site_name,
                series_name=self._extract_series(soup),
                imdb_id=f"GV-{self.extract_product_id(url) or 'unknown'}"
            )
            
            # 添加演员信息
            performers = self._extract_performers(soup)
            for performer_name in performers:
                self.movie_data.add_actor(performer_name, "Actor")
            
            # 添加标签（第一个为imdbid）
            self.movie_data.tags.extend([
                self.movie_data.imdb_id,
                "成人视频",
                "日本",
                "GV"
            ])
            
            # 设置成人视频特有属性
            self.movie_data.mpaa = "XXX"
            self.movie_data.custom_rating = "XXX"
            
            # 使用成人模板
            self.nfo_template = "adult"
            
            print("✅ 视频信息获取完成")
            return True
            
        except NetworkError:
            raise
        except Exception as e:
            raise ScrapingError(f"爬取过程中出现错误: {e}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """从页面提取视频标题。
        
        可设置的值：
        - 成人视频标题
        - 支持日文、中文、英文标题
        - 自动清理网站名称等无关信息
        """
        # 尝试多个选择器用于trance-video.com
        selectors = [
            "h1",
            ".title",
            "title"
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                # 清理标题（移除网站名称等）
                title = re.sub(r'\s*-\s*.*?(trance|video|market).*$', '', title, flags=re.IGNORECASE)
                if title:
                    return title
        
        return "未知视频标题"
    
    def _extract_work_id(self, soup: BeautifulSoup) -> str:
        """从页面提取作品ID。
        
        可设置的值：
        - GV-RML4001 格式的作品ID
        - 其他自定义格式的作品编号
        """
        # 在页面中查找作品ID
        work_id_selectors = [
            ".work-id",
            "[class*='work']",
            "[class*='id']"
        ]
        
        for selector in work_id_selectors:
            id_elem = soup.select_one(selector)
            if id_elem:
                return id_elem.get_text().strip()
        
        # 尝试从文本内容中提取
        text_content = soup.get_text()
        id_match = re.search(r'([A-Z]{2}-\d{2}-\d{4}-\d{2})', text_content)
        if id_match:
            return id_match.group(1)
        
        return ""
    
    def _extract_performers(self, soup: BeautifulSoup) -> list:
        """从页面提取出演者信息。
        
        演员姓名可设置的值：
        - 日文姓名（如：藤原道人、田口晃汰）
        - 中文姓名
        - 英文姓名
        - 艺名或昵称
        - 成人视频演员名
        """
        performers = []
        
        # 查找出演者信息
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
        """从页面提取视频类型。
        
        可设置的值：
        - GV (默认，必须包含)
        - ゲイAV (同性恋成人视频)
        - リーマンもの (上班族题材)
        - 筋肉系 (肌肉系)
        - ストーリー系 (剧情系)
        - 成人、日本等地区标签
        """
        genres = []
        
        # 查找分类标签
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
        
        # 如果没有找到类型，使用默认值
        if not genres:
            genres = ["GV", "成人", "日本"]
        
        return genres
    
    def _extract_year(self, soup: BeautifulSoup) -> str:
        """从页面提取发布年份。
        
        从发布日期自动解析，格式：YYYY
        """
        release_date = self._extract_release_date(soup)
        if release_date:
            return release_date.split("-")[0]
        return str(datetime.now().year)
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """从页面提取视频描述。
        
        可设置的内容：
        - 详细的剧情描述
        - 成人视频内容描述
        - 支持多行文本和换行
        - 支持日文、中文、英文等多语言
        - CDATA格式输出
        """
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
                if len(desc_text) > 20:  # 确保内容充实
                    return desc_text
        
        return "精彩的成人视频作品。"
    
    def _extract_release_date(self, soup: BeautifulSoup) -> str:
        """从页面提取发布日期。
        
        格式：YYYY-MM-DD
        用于releasedate和premiered字段
        """
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
                # 尝试解析各种日期格式
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
                                # MM/DD/YYYY 格式
                                month, day, year = match.groups()
                                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            else:
                                # YYYY-MM-DD 或 YYYY.MM.DD 格式
                                year, month, day = match.groups()
                                return f"{year}-{month}-{day}"
                        else:
                            # 仅年份
                            year = match.group(1)
                            return f"{year}-01-01"
        
        current_year = datetime.now().year
        return f"{current_year}-01-01"
    
    def _extract_duration(self, soup: BeautifulSoup) -> str:
        """从页面提取视频时长。
        
        格式：分钟数（如：37）
        支持HH:MM:SS或MM:SS格式自动转换
        """
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
                # 将HH:MM:SS或MM:SS转换为总分钟数
                time_match = re.search(r"(?:(\d+):)?(\d+):(\d+)", duration_text)
                if time_match:
                    hours, minutes, seconds = time_match.groups()
                    hours = int(hours) if hours else 0
                    minutes = int(minutes)
                    seconds = int(seconds)
                    total_minutes = hours * 60 + minutes + (seconds / 60)
                    return str(int(total_minutes))
        
        return "30"  # 视频默认30分钟
    
    def _extract_maker(self, soup: BeautifulSoup) -> str:
        """从页面提取制作商信息。
        
        可设置的值：
        - G@MES（如RML4001样本中的制作商）
        - 其他成人视频制作商名称
        """
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
        """从页面提取厂牌/制片厂信息。
        
        可设置的值：
        - 制片厂名称
        - 发行商名称
        - 默认空（如果未找到）
        """
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
        """从页面提取封面图片。
        
        用于poster字段，仅用于生成封面，不在NFO中输出。
        
        可设置的值：
        - 完整的图片URL
        - 相对路径（会自动转换为绝对路径）
        """
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
    
    def _extract_series(self, soup: BeautifulSoup) -> str:
        """从页面提取系列名称。
        
        可设置的值：
        - 系列名称（如：リーマンずラブ4）
        - 作品集合名称
        - 默认空（如果未找到）
        """
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
        """获取适合trance video网站的模板。
        
        返回成人内容专用模板。
        """
        return "adult"
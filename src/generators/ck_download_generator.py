"""CK-Download NFO生成器。

专门用于CK-Download网站的NFO文件生成。
"""

import re
from typing import Optional
from bs4 import BeautifulSoup
from datetime import datetime

from ..core.base_generator import BaseNfoGenerator
from ..core.movie_data import MovieData
from ..core.exceptions import ScrapingError, NetworkError


class CkDownloadNfoGenerator(BaseNfoGenerator):
    """CK-Download网站的NFO生成器。
    
    支持从CK-Download网站爬取电影信息并生成标准NFO文件。
    """
    
    @property
    def site_name(self) -> str:
        """返回支持的网站名称。"""
        return "CK-Download"
    
    @property
    def site_domain(self) -> str:
        """返回支持的网站域名。"""
        return "ck-download"
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """从CK-Download URL中提取产品ID。
        
        Args:
            url: 电影URL
            
        Returns:
            找到则返回产品ID，否则返回None
            
        支持的URL格式：
        - https://ck-download.com/product/detail/12345
        """
        match = re.search(r"product/detail/(\d+)", url)
        if match:
            return match.group(1)
        return None
    
    def scrape_movie_info(self, url: str) -> bool:
        """从CK-Download URL爬取电影信息。
        
        Args:
            url: 电影URL
            
        Returns:
            成功返回True，失败返回False
            
        Raises:
            ScrapingError: 爬取失败时抛出
            NetworkError: 网络请求失败时抛出
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
            
            # 初始化电影数据
            self.movie_data = MovieData(
                title=title,
                original_title=title,
                product_id=self.extract_product_id(url) or "26966",
                year=self._extract_year(soup),
                plot=self._extract_plot(soup),
                outline="",  # 概要默认空
                genres=self._extract_tags(soup),
                runtime=self._extract_runtime(soup),
                studio=self.site_name,
                release_date=self._extract_premiered(soup),
                poster=self._extract_poster(soup),  # 封面图片URL
                imdb_id=f"CK-{self.extract_product_id(url) or '26966'}"
            )
            
            # 添加演员信息
            actors = self._extract_actors(soup)
            for actor_info in actors:
                self.movie_data.add_actor(actor_info["name"], "Actor")
            
            # 添加标签（第一个为imdbid）
            self.movie_data.tags.extend([self.movie_data.imdb_id, "国产", "CK-Download"])
            
            # 使用标准模板
            self.nfo_template = "standard"
            
            print("✅ 基本信息获取完成")
            return True
            
        except NetworkError:
            raise
        except Exception as e:
            raise ScrapingError(f"爬取过程中出现错误: {e}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """从页面提取电影标题。
        
        可设置的值：任意电影标题文本
        """
        title_elem = soup.select_one("div#Contents h3")
        return title_elem.get_text().strip() if title_elem else "未知标题"
    
    def _extract_product_number(self, soup: BeautifulSoup) -> str:
        """从页面提取产品编号。
        
        可设置的值：如CK-001、CK-002等格式
        """
        num_td = soup.find("th", string="プロダクトナンバー")
        if num_td and num_td.find_next("td"):
            return num_td.find_next("td").get_text(strip=True)
        return ""
    
    def _extract_tags(self, soup: BeautifulSoup) -> list:
        """从页面提取标签/类型。
        
        可设置的值：
        - 剧情、爱情、动作、喜剧等类型标签
        - 国产、日本、韩国等地区标签
        - 其他自定义标签
        """
        tags = []
        category_div = soup.select_one("div.prod_category")
        if category_div:
            for a in category_div.select("a"):
                text = a.get_text(strip=True)
                if text:
                    tags.append(text)
        return tags if tags else ["剧情", "爱情"]
    
    def _extract_year(self, soup: BeautifulSoup) -> str:
        """从页面提取年份。
        
        从发布日期自动解析，格式：YYYY
        """
        premiered_date = self._extract_premiered(soup)
        if premiered_date:
            return premiered_date.split("-")[0]
        return str(datetime.now().year)
    
    def _extract_plot(self, soup: BeautifulSoup) -> str:
        """从页面提取剧情简介。
        
        可设置的内容：
        - 详细的剧情描述
        - 支持多行文本和换行
        - 支持中文、日文、英文等多语言
        - CDATA格式输出
        """
        intro_div = soup.select_one("div.intro_text")
        
        if intro_div:
            paragraphs = []
            p_elements = intro_div.find_all("p")
            
            for p in p_elements:
                text = p.get_text().strip()
                if text:
                    # 处理换行符
                    br_elements = p.find_all("br")
                    if br_elements:
                        text = p.get_text("\n", strip=True)
                    paragraphs.append(text)
            
            if paragraphs:
                return "\n\n".join(paragraphs)
        
        return "暂无剧情简介"
    
    def _extract_premiered(self, soup: BeautifulSoup) -> str:
        """从页面提取首映日期。
        
        格式：YYYY-MM-DD
        用于releasedate和premiered字段
        """
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
        """从页面提取演员信息。
        
        演员姓名可设置的值：
        - 中文姓名
        - 日文姓名
        - 英文姓名
        - 艺名或昵称
        """
        # 这是一个占位符实现
        # 在实际场景中，您需要提取真实的演员信息
        return [
            {"name": "演员1"},
            {"name": "演员2"}
        ]
    
    def _extract_runtime(self, soup: BeautifulSoup) -> str:
        """从页面提取时长。
        
        格式：分钟数（如：120）
        """
        # 这是一个占位符实现
        # 在实际场景中，您需要提取真实的时长信息
        return "120"
    
    def _extract_poster(self, soup: BeautifulSoup) -> str:
        """从页面提取封面图片URL。
        
        仅用于生成封面，不在NFO中输出。
        
        可设置的值：
        - 完整的图片URL
        - 相对路径（会自动转换为绝对路径）
        """
        # 查找封面图片
        img_selectors = [
            ".poster img",
            ".cover img",
            ".thumbnail img",
            "img[class*='cover']",
            "img[class*='poster']"
        ]
        
        for selector in img_selectors:
            img_elem = soup.select_one(selector)
            if img_elem:
                src = img_elem.get('src') or img_elem.get('data-src')
                if src:
                    return src if src.startswith('http') else f"https:{src}"
        
        return ""
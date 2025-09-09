import black

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import json
import time
from datetime import datetime


class CkDownloadNfoGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        self.movie_data = {}

    def extract_info_from_url(self, url):
        match = re.search(r"product/detail/(\d+)", url)
        if match:
            return match.group(1)
        return None

    def scrape_movie_info(self, url):
        print("🚀 开始尝试获取影片信息...")
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = "utf-8"
            if response.status_code != 200:
                print(f"❌ 访问失败，状态码: {response.status_code}")
                return False
            soup = BeautifulSoup(response.text, "html.parser")
            title_elem = soup.select_one("div#Contents h3")
            title = title_elem.get_text().strip() if title_elem else "未知标题"
            
            product_number = self.extract_product_number(soup)
            title = f"{product_number} {title}".strip()
            
            self.movie_data = {
                "title": title,
                "originaltitle": title,
                "sorttitle": self.generate_sort_title(title),
                "product_id": self.extract_info_from_url(url) or "26966",
                "year": self.extract_year_from_page(soup),
                "plot": self.extract_plot(soup),
                "outline": self.extract_premiered(soup),
                "genres": self.extract_tags(soup),
                "actors": self.extract_actors(soup),
                "director": self.extract_director(soup),
                "runtime": self.extract_runtime(soup),
                "premiered": "",
                "thumb": "",
                "fanart": "",
            }
            print("✅ 基本信息获取完成")
            return True
        except Exception as e:
            print(f"❌ 爬取过程中出现错误: {e}")
            return False

    def extract_product_number(self, soup):
        num_td = soup.find("th", string="プロダクトナンバー")
        if num_td and num_td.find_next("td"):
            return num_td.find_next("td").get_text(strip=True)
        return ""

    def extract_tags(self, soup):
        tags = []
        category_div = soup.select_one("div.prod_category")
        if category_div:
            for a in category_div.select("a"):
                text = a.get_text(strip=True)
                if text:
                    tags.append(text)
        return tags

    def generate_sort_title(self, title):
        if not title:
            return "Unknown"
        return "".join([word[0].upper() for word in title.split() if word])

    def extract_year_from_page(self, soup):
        premiered_date = self.extract_premiered(soup)
        if premiered_date:
            return premiered_date.split("-")[0]
        return str(datetime.now().year)

    def extract_plot(self, soup):
        intro_div = soup.select_one("div.intro_text")

        if intro_div:
            # 提取所有段落文本
            paragraphs = []
        p_elements = intro_div.find_all("p")

        for p in p_elements:
            text = p.get_text().strip()
            if text:
                # 处理换行符，将<br>转换为换行
                br_elements = p.find_all("br")
                if br_elements:
                    # 使用BeautifulSoup的get_text方法处理换行
                    text = p.get_text("\n", strip=True)
                paragraphs.append(text)

        if paragraphs:
            # 合并所有段落，用两个换行符分隔
            return "\n\n".join(paragraphs)

        # 备用选择器
        return "暂无剧情简介"

    def extract_premiered(self, soup):
        date_div = soup.select_one("div.add_info div.date")
        if date_div:
            date_text = date_div.get_text().strip()
            date_match = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", date_text)
            if date_match:
                year, month, day = date_match.groups()
                return f"{year}-{month}-{day}"
        current_year = datetime.now().year
        return f"{current_year}-01-01"

    def extract_genres(self, soup):
        return ["剧情", "爱情"]

    def extract_actors(self, soup):
        return [{"name": "演员1", "role": "主角"}, {"name": "演员2", "role": "配角"}]

    def extract_director(self, soup):
        return "知名导演"

    def extract_runtime(self, soup):
        return "120"

    def manual_input_correction(self):
        print("\n" + "=" * 50)
        print("📝 请检查并修正以下信息")
        print("=" * 50)
        current_data = self.movie_data.copy()
        print(f"当前标题: {current_data['title']}")
        new_title = input("请输入修正后的标题(直接回车保持当前): ").strip()
        if new_title:
            current_data["title"] = new_title
        print(f"\n当前年份: {current_data['year']}")
        new_year = input("请输入修正后的年份: ").strip()
        if new_year:
            current_data["year"] = new_year
        print(f"\n当前剧情简介:\n{current_data['plot']}")
        new_plot = input("请输入修正后的剧情简介(直接回车保持当前):\n").strip()
        if new_plot:
            current_data["plot"] = new_plot
        print(f"\n当前导演: {current_data['director']}")
        new_director = input("请输入修正后的导演: ").strip()
        if new_director:
            current_data["director"] = new_director
        print(f"\n当前片长: {current_data['runtime']}分钟")
        new_runtime = input("请输入修正后的片长: ").strip()
        if new_runtime:
            current_data["runtime"] = new_runtime
        print(f"\n当前上映日期: {current_data['premiered'] or '未设置'}")
        new_premiered = input("请输入上映日期(YYYY-MM-DD): ").strip()
        if new_premiered:
            current_data["premiered"] = new_premiered
        print(f"\n当前海报URL: {current_data['thumb'] or '未设置'}")
        new_thumb = input("请输入海报图片URL: ").strip()
        if new_thumb:
            current_data["thumb"] = new_thumb
        print(f"\n当前背景图URL: {current_data['fanart'] or '未设置'}")
        new_fanart = input("请输入背景图URL: ").strip()
        if new_fanart:
            current_data["fanart"] = new_fanart
        print(f"\n当前演员信息:")
        for i, actor in enumerate(current_data["actors"]):
            print(f"  {i+1}. {actor['name']} 饰演 {actor['role']}")
        modify_actors = input("\n是否修改演员信息? (y/n): ").lower()
        if modify_actors == "y":
            current_data["actors"] = []
            print("请输入演员信息(输入'done'结束):")
            while True:
                name = input("演员姓名: ").strip()
                if name.lower() == "done":
                    break
                role = input("扮演角色: ").strip()
                current_data["actors"].append({"name": name, "role": role})
                print("---")
        print(f"\n当前影片风格: {', '.join(current_data['genres'])}")
        modify_genres = input("是否修改风格信息? (y/n): ").lower()
        if modify_genres == "y":
            current_data["genres"] = []
            print("请输入影片风格(输入'done'结束):")
            while True:
                genre = input("风格: ").strip()
                if genre.lower() == "done":
                    break
                current_data["genres"].append(genre)
        self.movie_data = current_data
        return True

    def create_nfo_file(self):
        if not self.movie_data:
            print("❌ 没有可用的影片数据")
            return False
        movie = ET.Element("movie")
        ET.SubElement(movie, "title").text = self.movie_data["title"]
        ET.SubElement(movie, "originaltitle").text = self.movie_data["originaltitle"]
        ET.SubElement(movie, "sorttitle").text = self.movie_data["sorttitle"]
        ratings = ET.SubElement(movie, "ratings")
        rating = ET.SubElement(
            ratings, "rating", name="default", max="10", default="true"
        )
        ET.SubElement(rating, "value").text = "7.5"
        ET.SubElement(rating, "votes").text = "1000"
        ET.SubElement(movie, "userrating").text = "0"
        ET.SubElement(movie, "top250").text = "0"
        ET.SubElement(movie, "year").text = self.movie_data["year"]
        ET.SubElement(movie, "plot").text = self.movie_data["plot"]
        ET.SubElement(movie, "outline").text = self.movie_data["outline"]
        ET.SubElement(movie, "tagline").text = ""
        ET.SubElement(movie, "runtime").text = self.movie_data["runtime"]
        if self.movie_data["thumb"]:
            ET.SubElement(movie, "thumb", aspect="poster").text = self.movie_data[
                "thumb"
            ]
        if self.movie_data["fanart"]:
            fanart = ET.SubElement(movie, "fanart")
            ET.SubElement(fanart, "thumb").text = self.movie_data["fanart"]
        ET.SubElement(movie, "mpaa").text = "TV-MA"
        ET.SubElement(movie, "premiered").text = self.movie_data.get(
            "premiered", "2023-01-01"
        )
        ET.SubElement(movie, "releasedate").text = self.movie_data.get(
            "premiered", "2023-01-01"
        )
        ET.SubElement(movie, "certification").text = "CN-18"
        product_id = self.movie_data.get("product_id", "26966")
        ET.SubElement(movie, "id").text = f"ck-download-{product_id}"
        ET.SubElement(movie, "uniqueid", type="ck-download", default="true").text = (
            product_id
        )
        for genre in self.movie_data["genres"]:
            ET.SubElement(movie, "tag").text = genre
        ET.SubElement(movie, "studio").text = "CK-Download"
        ET.SubElement(movie, "trailer").text = ""
        for i, actor in enumerate(self.movie_data["actors"]):
            actor_elem = ET.SubElement(movie, "actor")
            ET.SubElement(actor_elem, "name").text = actor["name"]
            ET.SubElement(actor_elem, "role").text = actor["role"]
            ET.SubElement(actor_elem, "order").text = str(i)
            ET.SubElement(actor_elem, "thumb").text = ""
        ET.SubElement(movie, "director").text = self.movie_data["director"]
        ET.SubElement(movie, "credits").text = self.movie_data["director"]
        ET.SubElement(movie, "set").text = ""
        ET.SubElement(movie, "country").text = "中国"
        ET.SubElement(movie, "tag").text = "ck-download"
        ET.SubElement(movie, "tag").text = "国产"
        rough_string = ET.tostring(movie, "utf-8")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")
        filename = f"{self.movie_data['title']}.nfo"
        with open(filename, "wb") as f:
            f.write(pretty_xml)
        print(f"\n✅ NFO文件已生成: {filename}")
        return filename

    def run(self):
        print("🎬 CK-Download NFO 文件生成器")
        print("=" * 40)
        url = input("请输入影片URL: ").strip()
        if not url:
            print("❌ 请输入有效的URL")
            return
        success = self.scrape_movie_info(url)
        if not success:
            print("⚠️  自动爬取失败，请手动输入信息")
            self.movie_data = {
                "title": "",
                "originaltitle": "",
                "sorttitle": "",
                "product_id": self.extract_info_from_url(url) or "26966",
                "year": "2023",
                "plot": "",
                "outline": "",
                "genres": [],
                "actors": [],
                "director": "",
                "runtime": "120",
                "premiered": "",
                "thumb": "",
                "fanart": "",
            }
        self.manual_input_correction()
        nfo_file = self.create_nfo_file()
        if nfo_file:
            print(f"\n🎉 完成！请将 '{nfo_file}' 与视频文件放在同一目录下")
        print("💡 提示: 确保NFO文件与视频文件主文件名相同")


if __name__ == "__main__":
    generator = CkDownloadNfoGenerator()
    generator.run()

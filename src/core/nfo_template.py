"""NFO模板管理器，用于标准化NFO文件生成。

基于RML4001.nfo格式标准，支持多种NFO模板类型。
"""

from typing import Dict, Any, Optional, List
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

from .movie_data import MovieData, Actor, Rating
from .exceptions import ValidationError
from .rating_validator import CustomRatingValidator


class NFOTemplate:
    """基于RML4001格式的标准NFO模板。
    
    支持的字段完全基于RML4001.nfo样本文件，确保兼容性。
    """
    
    # 标准NFO字段映射 - 基于RML4001.nfo格式
    STANDARD_FIELDS = {
        # 基本信息字段
        'title': 'title',                    # 标题 - 可设置任意文本
        'originaltitle': 'original_title',   # 原始标题 - 通常与title相同
        'sorttitle': 'sort_title',           # 排序标题 - 格式：imdbid + 空格 + title
        'year': 'year',                      # 年份 - 从releasedate自动解析，格式：YYYY
        'plot': 'plot',                      # 剧情简介 - 详细描述，支持CDATA格式
        'outline': 'outline',                # 概要 - 简短描述，默认空
        'tagline': 'tagline',                # 标语 - 宣传语，默认空
        'runtime': 'runtime',                # 时长 - 分钟数，如：37
        
        # 日期字段
        'premiered': 'premiered',            # 首映日期 - 与releasedate相同，格式：YYYY-MM-DD
        'releasedate': 'release_date',       # 发布日期 - 格式：YYYY-MM-DD
        'dateadded': 'date_added',           # 添加日期 - 文件生成时间，格式：YYYY-MM-DD HH:MM:SS
        
        # 评级和分类字段
        'mpaa': 'mpaa',                      # MPAA评级 - 如：XXX, PG-13, R等
        'rating': 'rating',                  # 评分 - 数字评分，默认空
        'criticrating': 'critic_rating',     # 影评人评分 - 数字评分，默认空
        'customrating': 'custom_rating',     # 自定义评级 - 严格验证，默认XXX
        
        # 制作信息字段
        'studio': 'studio',                  # 制片厂 - 如：G@MES，默认空
        
        # ID字段
        'imdbid': 'imdb_id',                # IMDB ID - 如：GV-RML4001
        'tmdbid': 'tmdb_id',                # TMDB ID - 与imdbid相同
        'tvdbid': 'tvdb_id',                # TVDB ID - 与imdbid相同
        
        # 元数据字段
        'lockdata': 'lock_data',            # 锁定数据 - 固定为false
        'lockedfields': 'locked_fields'     # 锁定字段 - 固定值
    }
    
    # 必填字段验证
    REQUIRED_FIELDS = ['title']  # 只有title是必填的
    
    # 字段默认值 - 基于用户要求和RML4001格式
    DEFAULT_VALUES = {
        # 基本字段默认值
        'outline': '',              # 概要 - 默认空
        'tagline': '',              # 标语 - 默认空  
        'customrating': 'XXX',      # 自定义评级 - 默认XXX
        'rating': '',               # 评分 - 默认空
        'criticrating': '',         # 影评人评分 - 默认空
        'studio': '',               # 制片厂 - 默认空
        'runtime': '0',             # 时长 - 默认0分钟
        
        # 固定值字段
        'lockdata': False,          # 锁定数据 - 固定false
        'lockedfields': 'Name|OriginalTitle|SortName|CommunityRating|CriticRating|Tagline|Overview|OfficialRating|Genres|Cast|Studios|Tags',  # 锁定字段列表 - 固定值
        
        # MPAA评级默认值
        'mpaa': 'XXX'               # MPAA评级 - 成人内容默认XXX
    }
    
    def __init__(self, template_name: str = "standard"):
        """初始化NFO模板。
        
        Args:
            template_name: 模板名称 (standard, adult, music等)
        """
        self.template_name = template_name
        self.custom_fields = {}
        self.field_order = self._get_field_order()
    
    def _get_field_order(self) -> List[str]:
        """获取基于RML4001样本的标准字段顺序。
        
        字段顺序严格按照RML4001.nfo文件排列，确保兼容性。
        """
        return [
            'plot',          # 剧情简介 - CDATA格式
            'outline',       # 概要 - CDATA格式，默认空
            'customrating',  # 自定义评级 - 验证值，默认XXX
            'lockdata',      # 锁定数据 - 固定false
            'lockedfields',  # 锁定字段 - 固定值
            'dateadded',     # 添加日期 - 生成时间
            'title',         # 标题 - 主要标题
            'originaltitle', # 原始标题 - 与title相同
            'actor',         # 演员信息 - name和type字段
            'rating',        # 评分 - 数字，默认空
            'year',          # 年份 - 从releasedate解析
            'sorttitle',     # 排序标题 - imdbid + 空格 + title
            'mpaa',          # MPAA评级 - 如XXX
            'imdbid',        # IMDB ID - 主要ID
            'tvdbid',        # TVDB ID - 与imdbid相同
            'tmdbid',        # TMDB ID - 与imdbid相同
            'premiered',     # 首映日期 - 与releasedate相同
            'releasedate',   # 发布日期 - YYYY-MM-DD格式
            'criticrating',  # 影评人评分 - 数字，默认空
            'runtime',       # 时长 - 分钟数
            'tagline',       # 标语 - 默认空
            'genre',         # 类型 - 多个值，默认包含GV
            'studio',        # 制片厂 - 默认空
            'tag',           # 标签 - 多个值，首个为imdbid
            'uniqueid',      # 唯一ID - imdb/tmdb/tvdb类型
            'id',            # 主ID - 与imdbid相同
            'fileinfo'       # 文件信息 - 媒体流详情
        ]
    
    def add_custom_field(self, field_name: str, data_attribute: str, default_value: Any = None):
        """添加自定义字段映射。
        
        Args:
            field_name: NFO字段名称
            data_attribute: MovieData属性名称
            default_value: 属性为空时的默认值
        """
        self.custom_fields[field_name] = {
            'attribute': data_attribute,
            'default': default_value
        }
    
    def validate_data(self, movie_data: MovieData) -> bool:
        """验证电影数据是否符合模板要求。
        
        Args:
            movie_data: 要验证的电影数据
            
        Returns:
            验证通过返回True
            
        Raises:
            ValidationError: 验证失败时抛出异常
        """
        for field in self.REQUIRED_FIELDS:
            if field in self.STANDARD_FIELDS:
                attr_name = self.STANDARD_FIELDS[field]
                value = getattr(movie_data, attr_name, None)
                if not value:
                    raise ValidationError(f"必填字段 '{field}' 缺失或为空")
        
        return True
    
    def create_nfo_xml(self, movie_data: MovieData, site_name: str = "") -> str:
        """从电影数据创建NFO XML内容。
        
        Args:
            movie_data: 电影数据对象
            site_name: 网站名称，用于ID生成
            
        Returns:
            格式化的XML字符串
        """
        self.validate_data(movie_data)
        
        # 创建根元素
        movie = ET.Element("movie")
        
        # 按标准顺序添加字段
        for field_name in self.field_order:
            self._add_field_to_xml(movie, field_name, movie_data, site_name)
        
        # 添加自定义字段
        for field_name, config in self.custom_fields.items():
            self._add_custom_field_to_xml(movie, field_name, config, movie_data)
        
        # 生成格式化XML
        rough_string = ET.tostring(movie, "utf-8")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")
        
        return pretty_xml
    
    def _add_field_to_xml(self, parent: ET.Element, field_name: str, movie_data: MovieData, site_name: str):
        """向XML元素添加字段。
        
        根据字段类型调用相应的处理方法。
        """
        if field_name == 'plot':
            # 剧情简介 - 使用CDATA格式
            self._add_cdata_field(parent, 'plot', movie_data.plot)
        elif field_name == 'outline':
            # 概要 - 使用CDATA格式，默认空
            self._add_cdata_field(parent, 'outline', movie_data.outline)
        elif field_name == 'genre':
            # 类型标签 - 多个值，默认包含GV
            self._add_genres(parent, movie_data)
        elif field_name == 'tag':
            # 标签 - 多个值，首个为imdbid
            self._add_tags(parent, movie_data)
        elif field_name == 'actor':
            # 演员信息 - name和type字段
            self._add_actors(parent, movie_data)
        elif field_name == 'uniqueid':
            # 唯一ID - imdb/tmdb/tvdb类型
            self._add_unique_ids(parent, movie_data)
        elif field_name == 'id':
            # 主ID - 与imdbid相同
            self._add_main_id(parent, movie_data, site_name)
        elif field_name == 'dateadded':
            # 添加日期 - 文件生成时间
            self._add_date_added(parent)
        elif field_name == 'fileinfo':
            # 文件信息 - 媒体流详情
            self._add_fileinfo(parent, movie_data)
        elif field_name in self.STANDARD_FIELDS:
            # 标准字段 - 简单文本字段
            self._add_simple_field(parent, field_name, movie_data)
    
    def _add_simple_field(self, parent: ET.Element, field_name: str, movie_data: MovieData):
        """添加简单文本字段，应用用户定义的规则。
        
        处理字段间的关联关系和默认值设置。
        """
        attr_name = self.STANDARD_FIELDS[field_name]
        value = getattr(movie_data, attr_name, None)
        
        # 应用用户定义的字段规则
        if field_name == 'originaltitle':
            # 原始标题 - 与title值相同
            value = movie_data.title
        elif field_name == 'sorttitle':
            # 排序标题 - 格式：imdbid + 空格 + title
            if movie_data.imdb_id and movie_data.title:
                value = f"{movie_data.imdb_id} {movie_data.title}"
            else:
                value = movie_data.title or ''
        elif field_name == 'year':
            # 年份 - 从releasedate自动解析，格式：YYYY
            if movie_data.release_date:
                try:
                    value = movie_data.release_date.split('-')[0]
                except:
                    value = movie_data.year or ''
            else:
                value = movie_data.year or ''
        elif field_name == 'premiered':
            # 首映日期 - 与releasedate值相同
            value = movie_data.release_date or ''
        elif field_name == 'tvdbid':
            # TVDB ID - 与imdbid值相同
            value = movie_data.imdb_id or ''
        elif field_name == 'tmdbid':
            # TMDB ID - 与imdbid值相同
            value = movie_data.imdb_id or ''
        elif field_name == 'customrating':
            # 自定义评级 - 严格验证，仅允许特定值
            value = CustomRatingValidator.sanitize_rating(value)
        
        # 如果值仍为空，使用默认值
        if value is None or value == "":
            value = self.DEFAULT_VALUES.get(field_name, "")
        
        # 只有在有值或是必填字段时才添加
        if value or field_name in self.REQUIRED_FIELDS:
            ET.SubElement(parent, field_name).text = str(value)
    
    def _add_ratings(self, parent: ET.Element, movie_data: MovieData):
        """Add ratings section."""
        if movie_data.ratings:
            ratings = ET.SubElement(parent, "ratings")
            for rating in movie_data.ratings:
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
            ratings = ET.SubElement(parent, "ratings")
            rating = ET.SubElement(
                ratings, "rating", name="default", max="10", default="true"
            )
            ET.SubElement(rating, "value").text = "7.5"
            ET.SubElement(rating, "votes").text = "1000"
    
    def _add_genres(self, parent: ET.Element, movie_data: MovieData):
        """添加类型标签元素。
        
        可设置的值：
        - GV (默认，必须包含)
        - AV (成人视频)
        - ゲイAV (同性恋成人视频)
        - リーマンもの (上班族题材)
        - 筋肉系 (肌肉系)
        - ストーリー系 (剧情系)
        - 其他自定义类型
        """
        # 类型默认包含GV
        genres = movie_data.genres if movie_data.genres else ['GV']
        
        # 确保GV在列表中
        if 'GV' not in genres:
            genres.insert(0, 'GV')
        
        for genre in genres:
            if genre:
                ET.SubElement(parent, "genre").text = genre
    
    def _add_tags(self, parent: ET.Element, movie_data: MovieData):
        """添加标签元素。
        
        标签设置规则：
        - 第一个标签固定为imdbid（如果有值）
        - 支持多个标签，自动去重
        
        可设置的标签值示例：
        - GV-RML4001 (作品ID)
        - FullHD高画质 (画质标签)
        - カラミ (情节标签)
        - ガッチリ筋肉質 (体型标签)
        - マッチョ (肌肉标签)
        - 体育会系 (类型标签)
        - ノンケ (性向标签)
        - リーマン (职业标签)
        - 巨根 (特征标签)
        - ストーリー (剧情标签)
        """
        tags = []
        
        # 第一个标签固定为imdbid（有值的情况）
        if movie_data.imdb_id:
            tags.append(movie_data.imdb_id)
        
        # 添加其他标签
        if movie_data.tags:
            for tag in movie_data.tags:
                if tag and tag != movie_data.imdb_id:  # 避免重复
                    tags.append(tag)
        
        # 生成标签元素
        for tag in tags:
            if tag:
                ET.SubElement(parent, "tag").text = tag
    
    def _add_actors(self, parent: ET.Element, movie_data: MovieData):
        """添加演员信息元素。
        
        演员字段设置：
        - name: 演员姓名（如：藤原道人、田口晃汰）
        - type: 固定为"Actor"
        
        演员姓名可设置的值：
        - 日文姓名（如：藤原道人、田口晃汰）
        - 中文姓名
        - 英文姓名
        - 艺名或昵称
        """
        for actor in movie_data.actors:
            actor_elem = ET.SubElement(parent, "actor")
            ET.SubElement(actor_elem, "name").text = actor.name
            # 演员类型固定为Actor
            ET.SubElement(actor_elem, "type").text = "Actor"
    
    def _add_unique_ids(self, parent: ET.Element, movie_data: MovieData):
        """添加唯一ID元素。
        
        ID设置规则：
        - 根据imdbid生成，如果imdbid无值则不生成
        - imdb、tmdb、tvdb三个ID值相同
        
        ID格式示例：
        - GV-RML4001 (GV系列)
        - AV-XXX001 (AV系列)
        - 自定义格式ID
        """
        # 根据imdbid生成，如果imdbid无值则不生成
        if movie_data.imdb_id:
            # imdb、tmdb、tvdb字段值相同，都使用imdbid
            id_types = ['imdb', 'tmdb', 'tvdb']
            for id_type in id_types:
                ET.SubElement(
                    parent, "uniqueid",
                    type=id_type
                ).text = movie_data.imdb_id
    
    def _add_main_id(self, parent: ET.Element, movie_data: MovieData, site_name: str):
        """添加主ID元素。
        
        ID设置规则：
        - 使用imdbid作为主ID
        - 如果imdbid无值则不生成此字段
        
        ID格式要求：
        - 格式：前缀-编号 (如：GV-RML4001)
        - 前缀可以是：GV、AV等
        - 编号部分：字母数字组合
        """
        # 主ID根据imdbid生成，如果imdbid无值则不生成
        if movie_data.imdb_id:
            ET.SubElement(parent, "id").text = movie_data.imdb_id
    
    # 注意：thumb和fanart字段在RML4001.nfo中不存在，已移除
    
    def _add_date_added(self, parent: ET.Element):
        """添加文件添加日期元素。
        
        日期格式：YYYY-MM-DD HH:MM:SS
        使用文件生成时的当前时间。
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ET.SubElement(parent, "dateadded").text = current_time
    
    def _add_cdata_field(self, parent: ET.Element, field_name: str, content: str):
        """添加CDATA格式的字段。
        
        用于plot和outline字段，支持多行文本和特殊字符。
        
        可设置的内容：
        - 详细的剧情描述（plot）
        - 简短的概要描述（outline）
        - 支持日文、中文、英文等多语言
        - 支持换行和特殊字符
        """
        if content:
            elem = ET.SubElement(parent, field_name)
            elem.text = content
            # 注意：Python的ET不直接支持CDATA，但内容会被正确转义
    
    def _add_fileinfo(self, parent: ET.Element, movie_data: MovieData):
        """添加文件信息部分。
        
        包含媒体流详细信息，通常由媒体扫描器填充。
        
        视频流可设置的值：
        - codec: h264, h265, mpeg4等
        - width: 1280, 1920, 720等（像素宽度）
        - height: 720, 1080, 480等（像素高度）
        - aspect: 16:9, 4:3等（宽高比）
        - bitrate: 比特率（如：3491075）
        - framerate: 帧率（如：29.97）
        
        音频流可设置的值：
        - codec: aac, mp3, ac3等
        - channels: 2, 5.1, 7.1等（声道数）
        - bitrate: 比特率（如：127933）
        - samplingrate: 采样率（如：44100）
        """
        # 通常由媒体扫描器填充，这里提供基本结构
        fileinfo = ET.SubElement(parent, "fileinfo")
        streamdetails = ET.SubElement(fileinfo, "streamdetails")
        
        # 视频流信息
        video = ET.SubElement(streamdetails, "video")
        ET.SubElement(video, "codec").text = "h264"
        ET.SubElement(video, "width").text = "1280"
        ET.SubElement(video, "height").text = "720"
        ET.SubElement(video, "aspect").text = "16:9"
        # 注意：runtime字段在fileinfo中不生成（按用户要求）
        
        # 音频流信息
        audio = ET.SubElement(streamdetails, "audio")
        ET.SubElement(audio, "codec").text = "aac"
        ET.SubElement(audio, "channels").text = "2"
    
    def _add_custom_field_to_xml(self, parent: ET.Element, field_name: str, config: Dict, movie_data: MovieData):
        """添加自定义字段到XML。
        
        用于扩展字段，如series、maker、label等。
        """
        attr_name = config['attribute']
        default_value = config.get('default', '')
        
        value = getattr(movie_data, attr_name, default_value)
        if value:
            ET.SubElement(parent, field_name).text = str(value)


class AdultNFOTemplate(NFOTemplate):
    """成人内容专用NFO模板。
    
    基于用户详细要求和RML4001格式，专门用于成人视频内容。
    """
    
    def __init__(self):
        super().__init__("adult")
        
        # 基于用户要求的成人内容默认值
        self.DEFAULT_VALUES.update({
            'mpaa': 'XXX',              # MPAA评级 - 成人内容固定XXX
            'customrating': 'XXX',      # 自定义评级 - 默认XXX
            'rating': '',               # 评分 - 默认空
            'criticrating': '',         # 影评人评分 - 默认空
            'lockdata': False,          # 锁定数据 - 固定false
            'lockedfields': 'Name|OriginalTitle|SortName|CommunityRating|CriticRating|Tagline|Overview|OfficialRating|Genres|Cast|Studios|Tags',  # 锁定字段 - 固定值
            'outline': '',              # 概要 - 默认空
            'tagline': '',              # 标语 - 默认空
            'studio': ''                # 制片厂 - 默认空
        })
        
        # 添加成人内容特有的自定义字段
        self.add_custom_field('series', 'series_name', '')    # 系列名称
        self.add_custom_field('maker', 'maker', '')           # 制作商
        self.add_custom_field('label', 'label', '')           # 厂牌


class MusicNFOTemplate(NFOTemplate):
    """音乐内容专用NFO模板。
    
    适用于音乐视频、演唱会等音乐相关内容。
    """
    
    def __init__(self):
        super().__init__("music")
        
        # 音乐内容的默认值设置
        self.DEFAULT_VALUES.update({
            'mpaa': 'G',                # MPAA评级 - 音乐内容默认G级
            'customrating': 'G',        # 自定义评级 - 默认G级
            'runtime': '4'              # 时长 - 音乐默认4分钟
        })
        
        # 添加音乐内容特有的自定义字段
        self.add_custom_field('artist', 'artist', '')         # 艺人
        self.add_custom_field('album', 'album', '')           # 专辑
        self.add_custom_field('track', 'track_number', '')    # 曲目编号


class TemplateManager:
    """NFO模板管理器。
    
    管理不同类型的NFO模板，支持模板注册和获取。
    """
    
    def __init__(self):
        """初始化模板管理器，注册默认模板。"""
        self.templates = {
            'standard': NFOTemplate('standard'),    # 标准模板
            'adult': AdultNFOTemplate(),           # 成人内容模板
            'music': MusicNFOTemplate()            # 音乐内容模板
        }
    
    def get_template(self, template_name: str) -> NFOTemplate:
        """根据名称获取模板。
        
        Args:
            template_name: 模板名称 (standard/adult/music)
            
        Returns:
            NFO模板实例
            
        Raises:
            ValueError: 模板不存在时抛出异常
        """
        if template_name not in self.templates:
            available = list(self.templates.keys())
            raise ValueError(f"模板 '{template_name}' 不存在。可用模板: {available}")
        
        return self.templates[template_name]
    
    def register_template(self, name: str, template: NFOTemplate):
        """注册新模板。
        
        Args:
            name: 模板名称
            template: 模板实例
        """
        self.templates[name] = template
    
    def list_templates(self) -> List[str]:
        """列出所有可用的模板名称。
        
        Returns:
            模板名称列表
        """
        return list(self.templates.keys())
"""NFO Template Manager for standardized NFO file generation."""

from typing import Dict, Any, Optional, List
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

from .movie_data import MovieData, Actor, Rating
from .exceptions import ValidationError
from .rating_validator import CustomRatingValidator


class NFOTemplate:
    """Standard NFO template based on Kodi/Plex format."""
    
    # Standard NFO field mapping
    STANDARD_FIELDS = {
        # Basic Information
        'title': 'title',
        'originaltitle': 'original_title', 
        'sorttitle': 'sort_title',
        'year': 'year',
        'plot': 'plot',
        'outline': 'outline',
        'tagline': 'tagline',
        'runtime': 'runtime',
        
        # Dates
        'premiered': 'premiered',
        'releasedate': 'release_date',
        'dateadded': 'date_added',
        
        # Ratings and Classification
        'mpaa': 'mpaa',
        'certification': 'certification',
        'rating': 'rating',
        'criticrating': 'critic_rating',
        'customrating': 'custom_rating',
        'userrating': 'user_rating',
        'top250': 'top250',
        
        # Production
        'studio': 'studio',
        'director': 'director',
        'credits': 'credits',
        'country': 'country',
        'set': 'set_name',
        'trailer': 'trailer',
        
        # Media
        'thumb': 'thumb',
        'fanart': 'fanart',
        
        # IDs
        'imdbid': 'imdb_id',
        'tmdbid': 'tmdb_id',
        'tvdbid': 'tvdb_id',
        
        # Metadata
        'lockdata': 'lock_data',
        'lockedfields': 'locked_fields'
    }
    
    # Required fields for validation
    REQUIRED_FIELDS = ['title', 'year']
    
    # Optional fields with defaults based on user requirements
    DEFAULT_VALUES = {
        'mpaa': 'Not Rated',
        'certification': 'Not Rated',
        'user_rating': 0,
        'top250': 0,
        'runtime': '0',
        'country': '未知',
        'outline': '',  # 默认空
        'tagline': '',  # 默认空
        'customrating': 'XXX',  # 默认XXX
        'lockdata': False,  # 固定false
        'lockedfields': 'Name|OriginalTitle|SortName|CommunityRating|CriticRating|Tagline|Overview|OfficialRating|Genres|Cast|Studios|Tags',  # 固定值
        'rating': '',  # 默认空白
        'criticrating': '',  # 默认空
        'trailer': '',
        'set_name': '',
        'studio': ''  # 默认空
    }
    
    def __init__(self, template_name: str = "standard"):
        """Initialize NFO template.
        
        Args:
            template_name: Template name (standard, adult, music, etc.)
        """
        self.template_name = template_name
        self.custom_fields = {}
        self.field_order = self._get_field_order()
    
    def _get_field_order(self) -> List[str]:
        """Get the standard field order for NFO generation based on RML4001 sample."""
        return [
            'plot',
            'outline',
            'customrating',
            'lockdata',
            'lockedfields',
            'dateadded',
            'title',
            'originaltitle',
            'actor',
            'rating',
            'year',
            'sorttitle',
            'mpaa',
            'imdbid',
            'tvdbid',
            'tmdbid',
            'premiered',
            'releasedate',
            'criticrating',
            'runtime',
            'tagline',
            'genre',
            'studio',
            'tag',
            'uniqueid',
            'id',
            'fileinfo'
        ]
    
    def add_custom_field(self, field_name: str, data_attribute: str, default_value: Any = None):
        """Add custom field mapping.
        
        Args:
            field_name: NFO field name
            data_attribute: MovieData attribute name
            default_value: Default value if attribute is empty
        """
        self.custom_fields[field_name] = {
            'attribute': data_attribute,
            'default': default_value
        }
    
    def validate_data(self, movie_data: MovieData) -> bool:
        """Validate movie data against template requirements.
        
        Args:
            movie_data: Movie data to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        for field in self.REQUIRED_FIELDS:
            if field in self.STANDARD_FIELDS:
                attr_name = self.STANDARD_FIELDS[field]
                value = getattr(movie_data, attr_name, None)
                if not value:
                    raise ValidationError(f"Required field '{field}' is missing or empty")
        
        return True
    
    def create_nfo_xml(self, movie_data: MovieData, site_name: str = "") -> str:
        """Create NFO XML content from movie data.
        
        Args:
            movie_data: Movie data
            site_name: Site name for ID generation
            
        Returns:
            Pretty formatted XML string
        """
        self.validate_data(movie_data)
        
        # Create root element
        movie = ET.Element("movie")
        
        # Add fields in standard order
        for field_name in self.field_order:
            self._add_field_to_xml(movie, field_name, movie_data, site_name)
        
        # Add custom fields
        for field_name, config in self.custom_fields.items():
            self._add_custom_field_to_xml(movie, field_name, config, movie_data)
        
        # Generate pretty XML
        rough_string = ET.tostring(movie, "utf-8")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")
        
        return pretty_xml
    
    def _add_field_to_xml(self, parent: ET.Element, field_name: str, movie_data: MovieData, site_name: str):
        """Add a field to XML element."""
        if field_name == 'plot':
            self._add_cdata_field(parent, 'plot', movie_data.plot)
        elif field_name == 'outline':
            self._add_cdata_field(parent, 'outline', movie_data.outline)
        elif field_name == 'ratings':
            self._add_ratings(parent, movie_data)
        elif field_name == 'genre':
            self._add_genres(parent, movie_data)
        elif field_name == 'tag':
            self._add_tags(parent, movie_data)
        elif field_name == 'actor':
            self._add_actors(parent, movie_data)
        elif field_name == 'uniqueid':
            self._add_unique_ids(parent, movie_data)
        elif field_name == 'id':
            self._add_main_id(parent, movie_data, site_name)
        elif field_name == 'thumb':
            self._add_thumb(parent, movie_data)
        elif field_name == 'fanart':
            self._add_fanart(parent, movie_data)
        elif field_name == 'dateadded':
            self._add_date_added(parent)
        elif field_name == 'fileinfo':
            self._add_fileinfo(parent, movie_data)
        elif field_name in self.STANDARD_FIELDS:
            self._add_simple_field(parent, field_name, movie_data)
    
    def _add_simple_field(self, parent: ET.Element, field_name: str, movie_data: MovieData):
        """Add simple text field with user-defined rules."""
        attr_name = self.STANDARD_FIELDS[field_name]
        value = getattr(movie_data, attr_name, None)
        
        # Apply user-defined field rules
        if field_name == 'originaltitle':
            # originaltitle值与title相同
            value = movie_data.title
        elif field_name == 'sorttitle':
            # sorttitle为imdbid空格title
            if movie_data.imdb_id and movie_data.title:
                value = f"{movie_data.imdb_id} {movie_data.title}"
            else:
                value = movie_data.title or ''
        elif field_name == 'year':
            # year从releasedate解析，如果没有则使用原值
            if movie_data.release_date:
                try:
                    value = movie_data.release_date.split('-')[0]
                except:
                    value = movie_data.year or ''
            else:
                value = movie_data.year or ''
        elif field_name == 'premiered':
            # premiered值与releasedate相同
            value = movie_data.release_date or ''
        elif field_name == 'tvdbid':
            # tvdbid值与imdbid相同
            value = movie_data.imdb_id or ''
        elif field_name == 'tmdbid':
            # tmdbid值与imdbid相同
            value = movie_data.imdb_id or ''
        elif field_name == 'customrating':
            # customrating需要验证有效值
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
        """Add genre elements with default GV."""
        # genre默认给一个GV
        genres = movie_data.genres if movie_data.genres else ['GV']
        
        # 确保GV在列表中
        if 'GV' not in genres:
            genres.insert(0, 'GV')
        
        for genre in genres:
            if genre:
                ET.SubElement(parent, "genre").text = genre
    
    def _add_tags(self, parent: ET.Element, movie_data: MovieData):
        """Add tag elements with imdbid as first tag."""
        tags = []
        
        # tag固定第一个为imdbid（有值的情况）
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
        """Add actor elements with fixed type."""
        for actor in movie_data.actors:
            actor_elem = ET.SubElement(parent, "actor")
            ET.SubElement(actor_elem, "name").text = actor.name
            # actor的type固定Actor
            ET.SubElement(actor_elem, "type").text = "Actor"
    
    def _add_unique_ids(self, parent: ET.Element, movie_data: MovieData):
        """Add unique ID elements based on imdbid."""
        # 根据imdbid来，如果imdbid无值则nfo里不生成
        if movie_data.imdb_id:
            # imdb, tmdb, tvdb字段相同，根据imdbid来
            id_types = ['imdb', 'tmdb', 'tvdb']
            for id_type in id_types:
                ET.SubElement(
                    parent, "uniqueid",
                    type=id_type
                ).text = movie_data.imdb_id
    
    def _add_main_id(self, parent: ET.Element, movie_data: MovieData, site_name: str):
        """Add main ID element based on imdbid."""
        # id根据imdbid来，如果imdbid无值则nfo里不生成
        if movie_data.imdb_id:
            ET.SubElement(parent, "id").text = movie_data.imdb_id
    
    def _add_thumb(self, parent: ET.Element, movie_data: MovieData):
        """Add thumb element."""
        if movie_data.thumb:
            ET.SubElement(parent, "thumb", aspect="poster").text = movie_data.thumb
    
    def _add_fanart(self, parent: ET.Element, movie_data: MovieData):
        """Add fanart element."""
        if movie_data.fanart:
            fanart = ET.SubElement(parent, "fanart")
            ET.SubElement(fanart, "thumb").text = movie_data.fanart
    
    def _add_date_added(self, parent: ET.Element):
        """Add dateadded element with current timestamp."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ET.SubElement(parent, "dateadded").text = current_time
    
    def _add_cdata_field(self, parent: ET.Element, field_name: str, content: str):
        """Add field with CDATA content."""
        if content:
            elem = ET.SubElement(parent, field_name)
            elem.text = content
            # Note: Python's ET doesn't directly support CDATA, but content will be properly escaped
    
    def _add_fileinfo(self, parent: ET.Element, movie_data: MovieData):
        """Add fileinfo section (placeholder for media file information)."""
        # This would typically be filled by media scanner
        # For now, we'll add a basic structure
        fileinfo = ET.SubElement(parent, "fileinfo")
        streamdetails = ET.SubElement(fileinfo, "streamdetails")
        
        # Video stream placeholder
        video = ET.SubElement(streamdetails, "video")
        ET.SubElement(video, "codec").text = "h264"
        ET.SubElement(video, "width").text = "1280"
        ET.SubElement(video, "height").text = "720"
        ET.SubElement(video, "aspect").text = "16:9"
        # runtime fileinfo里的 nfo里不生成 - 按用户要求移除
        
        # Audio stream placeholder
        audio = ET.SubElement(streamdetails, "audio")
        ET.SubElement(audio, "codec").text = "aac"
        ET.SubElement(audio, "channels").text = "2"
    
    def _add_custom_field_to_xml(self, parent: ET.Element, field_name: str, config: Dict, movie_data: MovieData):
        """Add custom field to XML."""
        attr_name = config['attribute']
        default_value = config.get('default', '')
        
        value = getattr(movie_data, attr_name, default_value)
        if value:
            ET.SubElement(parent, field_name).text = str(value)


class AdultNFOTemplate(NFOTemplate):
    """Specialized template for adult content based on user requirements."""
    
    def __init__(self):
        super().__init__("adult")
        
        # Override defaults for adult content based on user requirements
        self.DEFAULT_VALUES.update({
            'mpaa': 'XXX',
            'customrating': 'XXX',  # 默认XXX
            'certification': 'R18+',
            'country': '日本',
            'rating': '',  # 默认空白
            'criticrating': '',  # 默认空
            'lockdata': False,  # 固定false
            'lockedfields': 'Name|OriginalTitle|SortName|CommunityRating|CriticRating|Tagline|Overview|OfficialRating|Genres|Cast|Studios|Tags',  # 固定值
            'outline': '',  # 默认空
            'tagline': '',  # 默认空
            'studio': ''  # 默认空
        })
        
        # Add adult-specific custom fields
        self.add_custom_field('series', 'series_name', '')
        self.add_custom_field('maker', 'maker', '')
        self.add_custom_field('label', 'label', '')


class MusicNFOTemplate(NFOTemplate):
    """Specialized template for music content."""
    
    def __init__(self):
        super().__init__("music")
        
        # Override defaults for music content
        self.DEFAULT_VALUES.update({
            'mpaa': 'G',
            'certification': 'G',
            'country': '国际',
            'runtime': '4'  # Default 4 minutes for music
        })
        
        # Add music-specific custom fields
        self.add_custom_field('artist', 'artist', '')
        self.add_custom_field('album', 'album', '')
        self.add_custom_field('track', 'track_number', '')


class TemplateManager:
    """Manages different NFO templates."""
    
    def __init__(self):
        self.templates = {
            'standard': NFOTemplate('standard'),
            'adult': AdultNFOTemplate(),
            'music': MusicNFOTemplate()
        }
    
    def get_template(self, template_name: str) -> NFOTemplate:
        """Get template by name.
        
        Args:
            template_name: Template name
            
        Returns:
            NFO template instance
            
        Raises:
            ValueError: If template not found
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found. Available: {list(self.templates.keys())}")
        
        return self.templates[template_name]
    
    def register_template(self, name: str, template: NFOTemplate):
        """Register a new template.
        
        Args:
            name: Template name
            template: Template instance
        """
        self.templates[name] = template
    
    def list_templates(self) -> List[str]:
        """List available template names."""
        return list(self.templates.keys())
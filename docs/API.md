# GV-NFO-Maker API 文档

## 核心模块 (Core)

### BaseNfoGenerator

基础NFO生成器抽象类，所有具体生成器都应继承此类。

#### 抽象方法

```python
@abstractmethod
def site_name(self) -> str:
    """返回支持的网站名称"""
    pass

@abstractmethod
def site_domain(self) -> str:
    """返回支持的网站域名"""
    pass

@abstractmethod
def extract_product_id(self, url: str) -> Optional[str]:
    """从URL中提取产品ID"""
    pass

@abstractmethod
def scrape_movie_info(self, url: str) -> bool:
    """爬取电影信息"""
    pass
```

#### 公共方法

```python
def validate_url(self, url: str) -> bool:
    """验证URL是否属于支持的网站"""

def make_request(self, url: str, **kwargs) -> requests.Response:
    """发起HTTP请求"""

def manual_input_correction(self) -> bool:
    """手动输入修正"""

def create_nfo_file(self, filename: Optional[str] = None) -> str:
    """创建NFO文件"""

def run(self, url: str) -> Optional[str]:
    """主执行方法"""
```

### MovieData

电影数据模型类，用于存储和管理电影信息。

#### 主要属性

```python
@dataclass
class MovieData:
    title: str = ""                    # 标题
    original_title: str = ""           # 原始标题
    sort_title: str = ""               # 排序标题
    product_id: str = ""               # 产品ID
    year: str = ""                     # 年份
    plot: str = ""                     # 剧情简介
    outline: str = ""                  # 概要
    runtime: str = "0"                 # 片长
    premiered: str = ""                # 首映日期
    director: str = ""                 # 导演
    studio: str = ""                   # 制片厂
    genres: List[str] = field(default_factory=list)  # 类型
    actors: List[Actor] = field(default_factory=list) # 演员
    ratings: List[Rating] = field(default_factory=list) # 评分
```

#### 主要方法

```python
def add_actor(self, name: str, role: str = "", thumb: str = "") -> None:
    """添加演员"""

def add_rating(self, value: float, votes: int = 0, name: str = "default") -> None:
    """添加评分"""

def add_unique_id(self, id_type: str, id_value: str, is_default: bool = False) -> None:
    """添加唯一ID"""

def validate(self) -> bool:
    """验证数据"""

def to_dict(self) -> Dict:
    """转换为字典"""
```

### 异常类

```python
class NFOGeneratorError(Exception):
    """NFO生成器基础异常"""

class ScrapingError(NFOGeneratorError):
    """爬取失败异常"""

class ValidationError(NFOGeneratorError):
    """数据验证失败异常"""

class ConfigurationError(NFOGeneratorError):
    """配置错误异常"""

class NetworkError(NFOGeneratorError):
    """网络操作失败异常"""
```

## 生成器模块 (Generators)

### CkDownloadNfoGenerator

CK-Download网站的NFO生成器。

```python
class CkDownloadNfoGenerator(BaseNfoGenerator):
    @property
    def site_name(self) -> str:
        return "CK-Download"
    
    @property
    def site_domain(self) -> str:
        return "ck-download"
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """提取产品ID，支持格式: product/detail/{id}"""
    
    def scrape_movie_info(self, url: str) -> bool:
        """爬取CK-Download网站的电影信息"""
```

### TranceMusicNfoGenerator

Trance音乐网站的NFO生成器。

```python
class TranceMusicNfoGenerator(BaseNfoGenerator):
    @property
    def site_name(self) -> str:
        return "Trance-Music"
    
    @property
    def site_domain(self) -> str:
        return "trance"
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """提取产品ID，支持多种URL格式"""
    
    def scrape_movie_info(self, url: str) -> bool:
        """爬取Trance音乐网站的信息"""
```

## 配置模块 (Config)

### ConfigManager

配置管理器，负责加载、保存和管理配置。

```python
class ConfigManager:
    def __init__(self, config_file: Optional[str] = None):
        """初始化配置管理器"""
    
    def load_config(self) -> None:
        """从文件加载配置"""
    
    def save_config(self) -> None:
        """保存配置到文件"""
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
    
    def get_site_config(self, site: str) -> Dict[str, Any]:
        """获取网站特定配置"""
    
    def validate_config(self) -> bool:
        """验证配置"""
```

## 工具模块 (Utils)

### GeneratorFactory

生成器工厂类，负责创建和管理生成器实例。

```python
class GeneratorFactory:
    def __init__(self, config_manager: ConfigManager):
        """初始化工厂"""
    
    def register_generator(self, site: str, generator_class: Type[BaseNfoGenerator]) -> None:
        """注册新的生成器类"""
    
    def create_generator(self, site: str) -> BaseNfoGenerator:
        """创建指定网站的生成器"""
    
    def create_generator_from_url(self, url: str) -> Optional[BaseNfoGenerator]:
        """根据URL自动创建生成器"""
    
    def get_supported_sites(self) -> list:
        """获取支持的网站列表"""
```

### URLValidator

URL验证工具类。

```python
class URLValidator:
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """检查URL是否有效"""
    
    @staticmethod
    def is_http_url(url: str) -> bool:
        """检查URL是否使用HTTP/HTTPS协议"""
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """从URL中提取域名"""
    
    @staticmethod
    def validate_url(url: str) -> None:
        """验证URL并在无效时抛出异常"""
```

### DataValidator

数据验证工具类。

```python
class DataValidator:
    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        """初始化验证器"""
    
    def validate_field(self, field_name: str, value: Any) -> None:
        """验证单个字段"""
    
    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """验证多个字段"""
    
    @staticmethod
    def validate_year(year: str) -> None:
        """验证年份格式"""
    
    @staticmethod
    def validate_runtime(runtime: str) -> None:
        """验证片长格式"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名"""
```

## 使用示例

### 基本使用

```python
from src.config.config_manager import ConfigManager
from src.utils.generator_factory import GeneratorFactory

# 初始化配置管理器
config_manager = ConfigManager()

# 创建生成器工厂
factory = GeneratorFactory(config_manager)

# 创建生成器
generator = factory.create_generator("ck-download")

# 生成NFO文件
nfo_file = generator.run("https://ck-download.com/product/detail/12345")
```

### 自动识别网站

```python
# 根据URL自动创建生成器
generator = factory.create_generator_from_url(url)
if generator:
    nfo_file = generator.run(url)
else:
    print("不支持的网站")
```

### 自定义配置

```python
# 加载自定义配置
config_manager = ConfigManager("my_config.json")

# 修改配置
config_manager.set("timeout", 30)
config_manager.save_config()
```

### 添加新的生成器

```python
class MyWebsiteGenerator(BaseNfoGenerator):
    @property
    def site_name(self) -> str:
        return "My Website"
    
    @property
    def site_domain(self) -> str:
        return "mywebsite.com"
    
    def extract_product_id(self, url: str) -> Optional[str]:
        # 实现逻辑
        pass
    
    def scrape_movie_info(self, url: str) -> bool:
        # 实现逻辑
        pass

# 注册生成器
factory.register_generator("my-website", MyWebsiteGenerator)
```

## 错误处理

```python
try:
    generator = factory.create_generator("unknown-site")
except ConfigurationError as e:
    print(f"配置错误: {e}")

try:
    success = generator.scrape_movie_info(url)
except ScrapingError as e:
    print(f"爬取失败: {e}")
except NetworkError as e:
    print(f"网络错误: {e}")
```

## 日志记录

```python
from src.utils.logger import setup_logging, get_logger

# 设置日志
setup_logging(verbose=True)

# 获取日志器
logger = get_logger("my_module")
logger.info("开始处理")
logger.error("处理失败")
```
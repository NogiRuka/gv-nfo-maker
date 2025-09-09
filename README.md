# NFO Generator

一个支持多网站的模块化NFO文件生成器，专为媒体库管理而设计。

## 🌟 特性

- **多网站支持**: 支持CK-Download、Trance视频网站等多个平台
- **模块化架构**: 易于扩展和维护的模块化设计
- **智能识别**: 自动识别URL对应的网站类型
- **配置管理**: 灵活的配置系统，支持自定义设置
- **多种运行模式**: 支持自动、手动、交互三种运行模式
- **交互式界面**: 支持命令行和交互式两种使用模式
- **数据验证**: 完整的数据验证和错误处理机制
- **日志记录**: 详细的日志记录功能

## 📦 安装

### 环境要求

- Python 3.7+
- pip

### 依赖安装

```bash
pip install -r requirements.txt
```

### 依赖包

- `requests`: HTTP请求库
- `beautifulsoup4`: HTML解析库
- `lxml`: XML处理库

## 🚀 快速开始

### 命令行模式

```bash
# 自动识别网站类型
python -m src.main https://ck-download.com/product/detail/12345

# 指定网站类型
python -m src.main --site trance-video https://www.trance-video.com/product/detail/39661

# 指定输出文件名
python -m src.main -o "我的电影.nfo" https://example.com/movie

# 跳过手动输入步骤
python -m src.main --no-manual https://example.com/movie

# 设置运行模式
python -m src.main --mode auto https://example.com/movie
python -m src.main --mode manual https://example.com/movie

# 详细输出
python -m src.main -v https://example.com/movie
```

### 交互式模式

```bash
# 启动交互式模式
python -m src.main
```

### 配置管理

```bash
# 创建默认配置文件
python -m src.main --create-config

# 使用自定义配置文件
python -m src.main --config my_config.json https://example.com/movie
```

## 📁 项目结构

```
gv-nfo-maker/
├── src/
│   ├── __init__.py
│   ├── main.py                 # 主程序入口
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── base_generator.py   # 基础生成器抽象类
│   │   ├── movie_data.py       # 电影数据模型
│   │   └── exceptions.py       # 自定义异常
│   ├── generators/             # 生成器模块
│   │   ├── __init__.py
│   │   ├── ck_download_generator.py  # CK-Download生成器
│   │   └── trance_generator.py       # Trance音乐生成器
│   ├── config/                 # 配置模块
│   │   ├── __init__.py
│   │   ├── config_manager.py   # 配置管理器
│   │   └── settings.py         # 配置设置
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       ├── generator_factory.py # 生成器工厂
│       ├── logger.py           # 日志工具
│       └── validators.py       # 验证器
├── nfo_generator.py            # 原始文件（已重构）
├── requirements.txt            # 依赖列表
├── config.json                 # 配置文件
├── README.md                   # 项目文档
└── .gitignore                  # Git忽略文件
```

## 🎮 运行模式

NFO Generator 支持三种运行模式，满足不同的使用需求：

### 1. 自动模式 (auto)
- **特点**: 完全自动化，无人工干预
- **适用**: 批量处理、脚本自动化
- **行为**: 自动爬取信息并直接生成NFO文件，如果爬取失败则终止

```bash
python -m src.main --mode auto https://example.com/movie
```

### 2. 手动模式 (manual)
- **特点**: 强制人工修正所有信息
- **适用**: 需要精确控制输出内容
- **行为**: 爬取信息后必须进行人工修正确认

```bash
python -m src.main --mode manual https://example.com/movie
```

### 3. 交互模式 (interactive) - 默认
- **特点**: 灵活选择是否进行人工修正
- **适用**: 日常使用，平衡自动化和控制性
- **行为**: 爬取信息后询问是否需要人工修正

```bash
python -m src.main --mode interactive https://example.com/movie
# 或直接使用（默认模式）
python -m src.main https://example.com/movie
```

## 🔧 配置

### 配置文件格式

配置文件使用JSON格式，包含通用配置和网站特定配置：

```json
{
  "general": {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "timeout": 10,
    "retry_attempts": 3,
    "output_format": "nfo",
    "auto_correction": true,
    "manual_input": true
  },
  "sites": {
    "ck-download": {
      "name": "CK-Download",
      "domain": "ck-download",
      "default_studio": "CK-Download",
      "default_tags": ["ck-download", "国产"]
    },
    "trance-music": {
      "name": "Trance-Music",
      "domain": "trance",
      "default_studio": "Trance-Music",
      "default_tags": ["trance-music", "电子音乐"]
    }
  }
}
```

### 主要配置项

- `user_agent`: HTTP请求的User-Agent
- `timeout`: 请求超时时间（秒）
- `retry_attempts`: 重试次数
- `run_mode`: 运行模式 (auto/manual/interactive)
- `manual_input`: 是否启用手动输入修正
- `auto_correction`: 是否启用自动修正

## 🎯 支持的网站

### CK-Download

- **网站**: ck-download.com
- **支持内容**: 电影、电视剧
- **URL格式**: `https://ck-download.com/product/detail/{id}`

### Trance Video

- **网站**: trance-video.com
- **支持内容**: 成人视频
- **URL格式**: `https://www.trance-video.com/product/detail/{id}`

## 🔌 扩展开发

### 添加新的网站支持

1. **创建生成器类**:

```python
from src.core.base_generator import BaseNfoGenerator

class MyWebsiteGenerator(BaseNfoGenerator):
    @property
    def site_name(self) -> str:
        return "My Website"
    
    @property
    def site_domain(self) -> str:
        return "mywebsite.com"
    
    def extract_product_id(self, url: str) -> Optional[str]:
        # 实现产品ID提取逻辑
        pass
    
    def scrape_movie_info(self, url: str) -> bool:
        # 实现信息爬取逻辑
        pass
```

2. **注册生成器**:

```python
from src.utils.generator_factory import GeneratorFactory

factory = GeneratorFactory(config_manager)
factory.register_generator("my-website", MyWebsiteGenerator)
```

3. **添加配置**:

在配置文件中添加网站特定配置。

### 自定义数据处理

继承`MovieData`类来添加自定义字段：

```python
from src.core.movie_data import MovieData

class CustomMovieData(MovieData):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom_field = kwargs.get('custom_field', '')
```

## 🐛 故障排除

### 常见问题

1. **网络连接问题**
   - 检查网络连接
   - 确认目标网站可访问
   - 调整超时设置

2. **解析失败**
   - 网站结构可能已更改
   - 检查选择器配置
   - 启用详细日志查看错误信息

3. **配置错误**
   - 验证配置文件格式
   - 检查必需配置项
   - 使用`--create-config`重新创建配置

### 调试模式

```bash
# 启用详细日志
python -m src.main -v https://example.com/movie

# 查看日志文件
tail -f nfo_generator.log
```

## 📝 更新日志

### v1.0.0 (2024-01-XX)

- ✨ 初始版本发布
- 🏗️ 模块化架构重构
- 🔌 支持CK-Download和Trance视频网站
- ⚙️ 配置管理系统
- 🔍 智能URL识别
- 📊 数据验证和错误处理
- 📋 交互式和命令行模式

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发环境设置

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 代码规范

- 遵循PEP 8代码风格
- 添加适当的文档字符串
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 👥 作者

- **NFO Generator Team** - 初始开发

## 🙏 致谢

- BeautifulSoup4 - HTML解析
- Requests - HTTP库
- 所有贡献者和用户

---

**注意**: 请遵守目标网站的robots.txt和使用条款，合理使用爬虫功能。
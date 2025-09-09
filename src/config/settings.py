"""Configuration settings for NFO Generator."""

from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "timeout": 10,
    "retry_attempts": 3,
    "retry_delay": 1,
    "output_format": "nfo",
    "encoding": "utf-8",
    "pretty_xml": True,
    "xml_indent": "  ",
    "default_rating": 7.5,
    "default_votes": 1000,
    "default_runtime": "120",
    "default_mpaa": "TV-MA",
    "default_certification": "CN-18",
    "default_country": "中国",
    "auto_correction": True,
    "manual_input": True,
    "backup_files": True,
    "log_level": "INFO",
    "log_file": "nfo_generator.log"
}

# Site-specific configurations
SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "ck-download": {
        "name": "CK-Download",
        "domain": "ck-download",
        "base_url": "https://ck-download.com",
        "selectors": {
            "title": "div#Contents h3",
            "product_number": "th:contains('プロダクトナンバー') + td",
            "category": "div.prod_category a",
            "intro": "div.intro_text",
            "date": "div.add_info div.date"
        },
        "patterns": {
            "product_id": r"product/detail/(\d+)",
            "date": r"(\d{4})\.(\d{2})\.(\d{2})"
        },
        "default_studio": "CK-Download",
        "default_tags": ["ck-download", "国产"],
        "default_genres": ["剧情", "爱情"]
    },
    "trance-video": {
        "name": "Trance-Video",
        "domain": "trance-video.com",
        "base_url": "https://www.trance-video.com",
        "selectors": {
            "title": ["h1", ".title", "title"],
            "work_id": [".work-id", "[class*='work']", "[class*='id']"],
            "genre": [".category", ".genre", ".tag", "[class*='category']"],
            "description": [".description", ".summary", ".content", "p"],
            "date": [".release-date", ".date", ".published", "time"],
            "duration": [".duration", ".runtime", ".time"],
            "artwork": [".poster img", ".cover img", ".thumbnail img", ".preview img"]
        },
        "patterns": {
            "product_id": [r"/product/detail/(\d+)", r"/(\d+)/?$"],
            "work_id": r"([A-Z]{2}-\d{2}-\d{4}-\d{2})",
            "date": [r"(\d{4})-(\d{2})-(\d{2})", r"(\d{4})\.(\d{2})\.(\d{2})", r"(\d{2})/(\d{2})/(\d{4})"],
            "duration": r"(?:(\d+):)?(\d+):(\d+)"
        },
        "default_studio": "Trance-Video",
        "default_tags": ["trance-video", "成人视频", "日本"],
        "default_genres": ["成人", "日本"],
        "default_mpaa": "XXX",
        "default_certification": "R18+",
        "default_country": "日本",
        "default_runtime": "30"
    }
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "nfo_generator.log",
            "formatter": "detailed"
        }
    },
    "loggers": {
        "nfo_generator": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

# Validation rules
VALIDATION_RULES = {
    "title": {
        "required": True,
        "min_length": 1,
        "max_length": 200
    },
    "year": {
        "required": True,
        "pattern": r"^\d{4}$",
        "min_value": 1900,
        "max_value": 2030
    },
    "runtime": {
        "required": False,
        "pattern": r"^\d+$",
        "min_value": 1,
        "max_value": 1000
    },
    "rating": {
        "required": False,
        "min_value": 0.0,
        "max_value": 10.0
    },
    "url": {
        "required": True,
        "pattern": r"^https?://.*"
    }
}
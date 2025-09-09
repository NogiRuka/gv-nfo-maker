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
    "trance-music": {
        "name": "Trance-Music",
        "domain": "trance",
        "base_url": "https://trance-music.com",
        "selectors": {
            "title": ["h1.track-title", "h1.song-title", ".title h1", "h1"],
            "artist": [".artist-name", ".track-artist", ".by-artist"],
            "genre": [".genre", ".tag", ".style", ".categories a"],
            "description": [".description", ".track-info", ".about"],
            "date": [".release-date", ".date", ".published", "time"],
            "duration": [".duration", ".length", ".time"],
            "artwork": [".artwork img", ".cover img", ".album-art img"]
        },
        "patterns": {
            "product_id": [r"/track/(\d+)", r"/music/(\d+)", r"/video/(\d+)", r"id=(\d+)"],
            "date": [r"(\d{4})-(\d{2})-(\d{2})", r"(\d{4})\.(\d{2})\.(\d{2})", r"(\d{2})/(\d{2})/(\d{4})"],
            "duration": r"(\d+):(\d+)"
        },
        "default_studio": "Trance-Music",
        "default_tags": ["trance-music", "电子音乐", "trance", "音乐视频"],
        "default_genres": ["Trance", "Electronic", "Dance"],
        "default_mpaa": "G",
        "default_certification": "G",
        "default_country": "国际",
        "default_runtime": "4"
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
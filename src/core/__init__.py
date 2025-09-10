"""Core module for NFO Generator."""

from .base_generator import BaseNfoGenerator
from .movie_data import MovieData
from .exceptions import NFOGeneratorError, ScrapingError, ValidationError
from .nfo_template import NFOTemplate, AdultNFOTemplate, MusicNFOTemplate, TemplateManager
from .rating_validator import CustomRatingValidator

__all__ = [
    'BaseNfoGenerator',
    'MovieData',
    'NFOGeneratorError',
    'ScrapingError',
    'ValidationError',
    'NFOTemplate',
    'AdultNFOTemplate',
    'MusicNFOTemplate',
    'TemplateManager',
    'CustomRatingValidator'
]
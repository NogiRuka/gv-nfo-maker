"""NFO Generators module."""

from .ck_download_generator import CkDownloadNfoGenerator
from .trance_generator import TranceMusicNfoGenerator

__all__ = [
    'CkDownloadNfoGenerator',
    'TranceMusicNfoGenerator'
]
"""NFO Generators module."""

from .ck_download_generator import CkDownloadNfoGenerator
from .trance_generator import TranceMusicNfoGenerator  # Actually handles trance-video.com

__all__ = [
    'CkDownloadNfoGenerator',
    'TranceMusicNfoGenerator'
]
"""Movie data model for NFO Generator."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Actor:
    """Actor information."""
    name: str
    role: str = ""
    thumb: str = ""
    order: int = 0


@dataclass
class Rating:
    """Rating information."""
    value: float = 0.0
    votes: int = 0
    max_rating: float = 10.0
    name: str = "default"
    is_default: bool = True


@dataclass
class MovieData:
    """Movie data container."""
    title: str = ""
    original_title: str = ""
    sort_title: str = ""
    product_id: str = ""
    year: str = ""
    plot: str = ""
    outline: str = ""
    tagline: str = ""
    runtime: str = "0"
    premiered: str = ""
    release_date: str = ""
    mpaa: str = "TV-MA"
    certification: str = "CN-18"
    studio: str = ""
    country: str = "中国"
    director: str = ""
    credits: str = ""
    trailer: str = ""
    thumb: str = ""
    fanart: str = ""
    genres: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    actors: List[Actor] = field(default_factory=list)
    ratings: List[Rating] = field(default_factory=list)
    user_rating: float = 0.0
    top250: int = 0
    set_name: str = ""
    unique_ids: Dict[str, str] = field(default_factory=dict)
    date_added: str = ""
    series_name: str = ""
    maker: str = ""
    label: str = ""
    artist: str = ""
    album: str = ""
    track_number: str = ""
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.original_title:
            self.original_title = self.title
        if not self.sort_title:
            self.sort_title = self.generate_sort_title()
        if not self.year and self.premiered:
            self.year = self.premiered.split("-")[0]
        if not self.release_date:
            self.release_date = self.premiered
        if not self.credits:
            self.credits = self.director
    
    def generate_sort_title(self) -> str:
        """Generate sort title from main title."""
        if not self.title:
            return "Unknown"
        return "".join([word[0].upper() for word in self.title.split() if word])
    
    def add_actor(self, name: str, role: str = "", thumb: str = "") -> None:
        """Add an actor to the movie."""
        order = len(self.actors)
        actor = Actor(name=name, role=role, thumb=thumb, order=order)
        self.actors.append(actor)
    
    def add_rating(self, value: float, votes: int = 0, name: str = "default", 
                   max_rating: float = 10.0, is_default: bool = False) -> None:
        """Add a rating to the movie."""
        rating = Rating(
            value=value, 
            votes=votes, 
            name=name, 
            max_rating=max_rating, 
            is_default=is_default
        )
        self.ratings.append(rating)
    
    def add_unique_id(self, id_type: str, id_value: str, is_default: bool = False) -> None:
        """Add a unique ID for the movie."""
        self.unique_ids[id_type] = id_value
    
    def validate(self) -> bool:
        """Validate movie data."""
        if not self.title:
            return False
        if not self.year or not self.year.isdigit():
            return False
        return True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'original_title': self.original_title,
            'sort_title': self.sort_title,
            'product_id': self.product_id,
            'year': self.year,
            'plot': self.plot,
            'outline': self.outline,
            'tagline': self.tagline,
            'runtime': self.runtime,
            'premiered': self.premiered,
            'release_date': self.release_date,
            'mpaa': self.mpaa,
            'certification': self.certification,
            'studio': self.studio,
            'country': self.country,
            'director': self.director,
            'credits': self.credits,
            'trailer': self.trailer,
            'thumb': self.thumb,
            'fanart': self.fanart,
            'genres': self.genres,
            'tags': self.tags,
            'actors': [{'name': a.name, 'role': a.role, 'thumb': a.thumb, 'order': a.order} for a in self.actors],
            'ratings': [{'value': r.value, 'votes': r.votes, 'max_rating': r.max_rating, 'name': r.name, 'is_default': r.is_default} for r in self.ratings],
            'user_rating': self.user_rating,
            'top250': self.top250,
            'set_name': self.set_name,
            'unique_ids': self.unique_ids
        }
"""Custom rating validator for NFO Generator."""

from typing import List, Optional
from .exceptions import ValidationError


class CustomRatingValidator:
    """Validator for custom rating values."""
    
    # Valid custom rating values based on user requirements
    VALID_RATINGS = [
        "",  # Empty value allowed
        "TV-Y",
        "APPROVED",
        "G",
        "E",
        "EC",
        "TV-G",
        "TV-Y7",
        "TV-Y7-FV",
        "PG",
        "TV-PG",
        "PG-13",
        "T",
        "TV-14",
        "R",
        "M",
        "TV-MA",
        "NC-17",
        "AO",
        "RP",
        "UR",
        "NR",
        "X",
        "XXX"
    ]
    
    @classmethod
    def validate_rating(cls, rating: str) -> bool:
        """Validate if the rating is in the allowed list.
        
        Args:
            rating: Rating value to validate
            
        Returns:
            True if valid, False otherwise
        """
        return rating in cls.VALID_RATINGS
    
    @classmethod
    def validate_rating_strict(cls, rating: str) -> None:
        """Validate rating and raise exception if invalid.
        
        Args:
            rating: Rating value to validate
            
        Raises:
            ValidationError: If rating is not valid
        """
        if not cls.validate_rating(rating):
            valid_ratings_str = ", ".join([f"'{r}'" if r else "'(空)'" for r in cls.VALID_RATINGS])
            raise ValidationError(
                f"Invalid custom rating '{rating}'. Valid values are: {valid_ratings_str}"
            )
    
    @classmethod
    def get_valid_ratings(cls) -> List[str]:
        """Get list of valid rating values.
        
        Returns:
            List of valid rating strings
        """
        return cls.VALID_RATINGS.copy()
    
    @classmethod
    def get_default_rating(cls) -> str:
        """Get default rating value.
        
        Returns:
            Default rating (XXX)
        """
        return "XXX"
    
    @classmethod
    def sanitize_rating(cls, rating: Optional[str]) -> str:
        """Sanitize and return valid rating or default.
        
        Args:
            rating: Input rating value
            
        Returns:
            Valid rating or default if invalid
        """
        if rating is None:
            return cls.get_default_rating()
        
        rating = str(rating).strip()
        
        if cls.validate_rating(rating):
            return rating
        else:
            return cls.get_default_rating()
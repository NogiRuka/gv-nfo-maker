"""Custom exceptions for NFO Generator."""


class NFOGeneratorError(Exception):
    """Base exception for NFO Generator."""
    pass


class ScrapingError(NFOGeneratorError):
    """Exception raised when scraping fails."""
    pass


class ValidationError(NFOGeneratorError):
    """Exception raised when data validation fails."""
    pass


class ConfigurationError(NFOGeneratorError):
    """Exception raised when configuration is invalid."""
    pass


class NetworkError(NFOGeneratorError):
    """Exception raised when network operations fail."""
    pass
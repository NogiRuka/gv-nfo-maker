"""Validation utilities for NFO Generator."""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from ..core.exceptions import ValidationError
from ..config.settings import VALIDATION_RULES


class URLValidator:
    """URL validation utilities."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def is_http_url(url: str) -> bool:
        """Check if URL uses HTTP/HTTPS protocol.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL uses HTTP/HTTPS
        """
        try:
            result = urlparse(url)
            return result.scheme.lower() in ['http', 'https']
        except Exception:
            return False
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """Extract domain from URL.
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain name or None if invalid
        """
        try:
            result = urlparse(url)
            return result.netloc.lower()
        except Exception:
            return None
    
    @staticmethod
    def validate_url(url: str) -> None:
        """Validate URL and raise exception if invalid.
        
        Args:
            url: URL to validate
            
        Raises:
            ValidationError: If URL is invalid
        """
        if not url:
            raise ValidationError("URL不能为空")
        
        if not URLValidator.is_valid_url(url):
            raise ValidationError(f"无效的URL格式: {url}")
        
        if not URLValidator.is_http_url(url):
            raise ValidationError(f"URL必须使用HTTP或HTTPS协议: {url}")


class DataValidator:
    """Data validation utilities."""
    
    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        """Initialize validator with rules.
        
        Args:
            rules: Validation rules dictionary
        """
        self.rules = rules or VALIDATION_RULES
    
    def validate_field(self, field_name: str, value: Any) -> None:
        """Validate a single field.
        
        Args:
            field_name: Name of the field
            value: Value to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if field_name not in self.rules:
            return  # No rules for this field
        
        field_rules = self.rules[field_name]
        
        # Check required
        if field_rules.get('required', False) and not value:
            raise ValidationError(f"{field_name}是必填字段")
        
        # Skip further validation if value is empty and not required
        if not value and not field_rules.get('required', False):
            return
        
        # Check string length
        if isinstance(value, str):
            min_length = field_rules.get('min_length')
            max_length = field_rules.get('max_length')
            
            if min_length is not None and len(value) < min_length:
                raise ValidationError(f"{field_name}长度不能少于{min_length}个字符")
            
            if max_length is not None and len(value) > max_length:
                raise ValidationError(f"{field_name}长度不能超过{max_length}个字符")
        
        # Check pattern
        pattern = field_rules.get('pattern')
        if pattern and isinstance(value, str):
            if not re.match(pattern, value):
                raise ValidationError(f"{field_name}格式不正确")
        
        # Check numeric range
        if isinstance(value, (int, float)):
            min_value = field_rules.get('min_value')
            max_value = field_rules.get('max_value')
            
            if min_value is not None and value < min_value:
                raise ValidationError(f"{field_name}不能小于{min_value}")
            
            if max_value is not None and value > max_value:
                raise ValidationError(f"{field_name}不能大于{max_value}")
    
    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate multiple fields.
        
        Args:
            data: Dictionary of field names and values
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        for field_name, value in data.items():
            try:
                self.validate_field(field_name, value)
            except ValidationError as e:
                errors.append(str(e))
        
        return errors
    
    def validate_data_strict(self, data: Dict[str, Any]) -> None:
        """Validate multiple fields and raise on first error.
        
        Args:
            data: Dictionary of field names and values
            
        Raises:
            ValidationError: If any validation fails
        """
        for field_name, value in data.items():
            self.validate_field(field_name, value)
    
    @staticmethod
    def validate_year(year: str) -> None:
        """Validate year format.
        
        Args:
            year: Year string to validate
            
        Raises:
            ValidationError: If year is invalid
        """
        if not year:
            raise ValidationError("年份不能为空")
        
        if not re.match(r'^\d{4}$', year):
            raise ValidationError("年份必须是4位数字")
        
        year_int = int(year)
        if year_int < 1900 or year_int > 2030:
            raise ValidationError("年份必须在1900-2030之间")
    
    @staticmethod
    def validate_runtime(runtime: str) -> None:
        """Validate runtime format.
        
        Args:
            runtime: Runtime string to validate
            
        Raises:
            ValidationError: If runtime is invalid
        """
        if not runtime:
            return  # Runtime is optional
        
        if not re.match(r'^\d+$', runtime):
            raise ValidationError("片长必须是数字")
        
        runtime_int = int(runtime)
        if runtime_int < 1 or runtime_int > 1000:
            raise ValidationError("片长必须在1-1000分钟之间")
    
    @staticmethod
    def validate_rating(rating: float) -> None:
        """Validate rating value.
        
        Args:
            rating: Rating value to validate
            
        Raises:
            ValidationError: If rating is invalid
        """
        if rating < 0.0 or rating > 10.0:
            raise ValidationError("评分必须在0.0-10.0之间")
    
    @staticmethod
    def validate_date(date_str: str) -> None:
        """Validate date format (YYYY-MM-DD).
        
        Args:
            date_str: Date string to validate
            
        Raises:
            ValidationError: If date is invalid
        """
        if not date_str:
            return  # Date is optional
        
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            raise ValidationError("日期格式必须是YYYY-MM-DD")
        
        try:
            from datetime import datetime
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValidationError("无效的日期")
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename by removing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters for Windows/Unix filesystems
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')
        
        # Ensure filename is not empty
        if not sanitized:
            sanitized = 'untitled'
        
        return sanitized
    
    @staticmethod
    def validate_filename(filename: str) -> None:
        """Validate filename.
        
        Args:
            filename: Filename to validate
            
        Raises:
            ValidationError: If filename is invalid
        """
        if not filename:
            raise ValidationError("文件名不能为空")
        
        # Check for invalid characters
        invalid_chars = r'[<>:"/\\|?*]'
        if re.search(invalid_chars, filename):
            raise ValidationError("文件名包含无效字符")
        
        # Check length
        if len(filename) > 255:
            raise ValidationError("文件名过长")
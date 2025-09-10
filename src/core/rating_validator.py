"""NFO生成器的自定义评级验证器。

基于用户要求，严格验证customrating字段的有效值。
"""

from typing import List, Optional
from .exceptions import ValidationError


class CustomRatingValidator:
    """自定义评级值验证器。
    
    验证customrating字段，确保只能设置为允许的特定值。
    """
    
    # 基于用户要求的有效自定义评级值
    VALID_RATINGS = [
        "",          # 空值 - 允许
        "TV-Y",      # 儿童节目
        "APPROVED",  # 已批准
        "G",         # 普通观众
        "E",         # 所有人
        "EC",        # 幼儿
        "TV-G",      # 电视普通级
        "TV-Y7",     # 7岁以上儿童
        "TV-Y7-FV",  # 7岁以上儿童（幻想暴力）
        "PG",        # 家长指导
        "TV-PG",     # 电视家长指导
        "PG-13",     # 13岁以下需家长陪同
        "T",         # 青少年
        "TV-14",     # 14岁以上
        "R",         # 限制级
        "M",         # 成熟
        "TV-MA",     # 电视成人级
        "NC-17",     # 17岁以下禁止
        "AO",        # 仅限成人
        "RP",        # 评级待定
        "UR",        # 未评级
        "NR",        # 无评级
        "X",         # X级
        "XXX"        # XXX级（成人内容默认）
    ]
    
    @classmethod
    def validate_rating(cls, rating: str) -> bool:
        """验证评级是否在允许的列表中。
        
        Args:
            rating: 要验证的评级值
            
        Returns:
            有效返回True，无效返回False
        """
        return rating in cls.VALID_RATINGS
    
    @classmethod
    def validate_rating_strict(cls, rating: str) -> None:
        """严格验证评级，无效时抛出异常。
        
        Args:
            rating: 要验证的评级值
            
        Raises:
            ValidationError: 评级无效时抛出异常
        """
        if not cls.validate_rating(rating):
            valid_ratings_str = ", ".join([f"'{r}'" if r else "'(空)'" for r in cls.VALID_RATINGS])
            raise ValidationError(
                f"无效的自定义评级 '{rating}'。有效值为: {valid_ratings_str}"
            )
    
    @classmethod
    def get_valid_ratings(cls) -> List[str]:
        """获取有效评级值列表。
        
        Returns:
            有效评级字符串列表
        """
        return cls.VALID_RATINGS.copy()
    
    @classmethod
    def get_default_rating(cls) -> str:
        """获取默认评级值。
        
        Returns:
            默认评级（XXX）
        """
        return "XXX"
    
    @classmethod
    def sanitize_rating(cls, rating: Optional[str]) -> str:
        """清理并返回有效评级或默认值。
        
        Args:
            rating: 输入的评级值
            
        Returns:
            有效评级或默认值（如果输入无效）
        """
        if rating is None:
            return cls.get_default_rating()
        
        rating = str(rating).strip()
        
        if cls.validate_rating(rating):
            return rating
        else:
            return cls.get_default_rating()
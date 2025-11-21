"""
输入验证模块
提供统一的输入验证功能，确保数据安全性和有效性
"""

import re
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import logging

from .exceptions import ValidationError

logger = logging.getLogger(__name__)


class InputValidator:
    """输入验证器"""
    
    def __init__(self):
        """初始化验证器"""
        self.validators: Dict[str, Callable] = {
            'required': self._validate_required,
            'string': self._validate_string,
            'integer': self._validate_integer,
            'float': self._validate_float,
            'email': self._validate_email,
            'url': self._validate_url,
            'uuid': self._validate_uuid,
            'enum': self._validate_enum,
            'min_length': self._validate_min_length,
            'max_length': self._validate_max_length,
            'min_value': self._validate_min_value,
            'max_value': self._validate_max_value,
            'pattern': self._validate_pattern,
            'custom': self._validate_custom
        }
    
    def validate(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据schema验证数据
        
        Args:
            data: 要验证的数据字典
            schema: 验证规则schema
        
        Returns:
            验证后的数据字典
        
        Raises:
            ValidationError: 验证失败时抛出
        """
        validated_data = {}
        errors = []
        
        for field_name, field_schema in schema.items():
            value = data.get(field_name)
            
            # 检查必填字段
            if field_schema.get('required', False) and value is None:
                errors.append(f"字段 '{field_name}' 是必填的")
                continue
            
            # 如果字段为空且不是必填，跳过验证
            if value is None:
                validated_data[field_name] = None
                continue
            
            # 执行验证规则
            try:
                validated_value = self._validate_field(
                    field_name, value, field_schema
                )
                validated_data[field_name] = validated_value
            except ValidationError as e:
                errors.append(str(e))
        
        if errors:
            raise ValidationError(f"验证失败: {'; '.join(errors)}")
        
        return validated_data
    
    def _validate_field(self, field_name: str, value: Any, schema: Dict[str, Any]) -> Any:
        """验证单个字段"""
        validated_value = value
        
        # 按顺序执行验证规则
        for rule_name, rule_value in schema.items():
            if rule_name == 'required' or rule_name == 'default':
                continue
            
            if rule_name in self.validators:
                validated_value = self.validators[rule_name](
                    field_name, validated_value, rule_value, schema
                )
            elif rule_name == 'type':
                type_validator = self.validators.get(rule_value)
                if type_validator:
                    validated_value = type_validator(
                        field_name, validated_value, None, schema
                    )
        
        return validated_value
    
    def _validate_required(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> Any:
        """验证必填字段"""
        if value is None or value == '':
            raise ValidationError(f"字段 '{field_name}' 是必填的")
        return value
    
    def _validate_string(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> str:
        """验证字符串类型"""
        if not isinstance(value, str):
            raise ValidationError(f"字段 '{field_name}' 必须是字符串类型")
        return str(value)
    
    def _validate_integer(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> int:
        """验证整数类型"""
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"字段 '{field_name}' 必须是整数类型")
    
    def _validate_float(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> float:
        """验证浮点数类型"""
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"字段 '{field_name}' 必须是浮点数类型")
    
    def _validate_email(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> str:
        """验证邮箱格式"""
        if not isinstance(value, str):
            raise ValidationError(f"字段 '{field_name}' 必须是字符串类型")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValidationError(f"字段 '{field_name}' 必须是有效的邮箱地址")
        
        return value
    
    def _validate_url(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> str:
        """验证URL格式"""
        if not isinstance(value, str):
            raise ValidationError(f"字段 '{field_name}' 必须是字符串类型")
        
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, value):
            raise ValidationError(f"字段 '{field_name}' 必须是有效的URL")
        
        return value
    
    def _validate_uuid(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> str:
        """验证UUID格式"""
        if not isinstance(value, str):
            raise ValidationError(f"字段 '{field_name}' 必须是字符串类型")
        
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, value, re.IGNORECASE):
            raise ValidationError(f"字段 '{field_name}' 必须是有效的UUID格式")
        
        return value
    
    def _validate_enum(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> Any:
        """验证枚举值"""
        if rule_value is None or not isinstance(rule_value, list):
            raise ValueError(f"枚举验证规则必须提供选项列表")
        
        if value not in rule_value:
            raise ValidationError(
                f"字段 '{field_name}' 必须是以下值之一: {', '.join(map(str, rule_value))}"
            )
        
        return value
    
    def _validate_min_length(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> Any:
        """验证最小长度"""
        if isinstance(value, str) and len(value) < rule_value:
            raise ValidationError(f"字段 '{field_name}' 长度不能少于 {rule_value} 个字符")
        elif isinstance(value, (list, dict)) and len(value) < rule_value:
            raise ValidationError(f"字段 '{field_name}' 元素数量不能少于 {rule_value} 个")
        return value
    
    def _validate_max_length(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> Any:
        """验证最大长度"""
        if isinstance(value, str) and len(value) > rule_value:
            raise ValidationError(f"字段 '{field_name}' 长度不能超过 {rule_value} 个字符")
        elif isinstance(value, (list, dict)) and len(value) > rule_value:
            raise ValidationError(f"字段 '{field_name}' 元素数量不能超过 {rule_value} 个")
        return value
    
    def _validate_min_value(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> Any:
        """验证最小值"""
        try:
            num_value = float(value)
            if num_value < rule_value:
                raise ValidationError(f"字段 '{field_name}' 值不能小于 {rule_value}")
        except (ValueError, TypeError):
            pass  # 非数字类型跳过
        return value
    
    def _validate_max_value(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> Any:
        """验证最大值"""
        try:
            num_value = float(value)
            if num_value > rule_value:
                raise ValidationError(f"字段 '{field_name}' 值不能大于 {rule_value}")
        except (ValueError, TypeError):
            pass  # 非数字类型跳过
        return value
    
    def _validate_pattern(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> str:
        """验证正则表达式模式"""
        if not isinstance(value, str):
            raise ValidationError(f"字段 '{field_name}' 必须是字符串类型")
        
        if not re.match(rule_value, value):
            raise ValidationError(f"字段 '{field_name}' 格式不正确")
        
        return value
    
    def _validate_custom(self, field_name: str, value: Any, rule_value: Any, schema: Dict) -> Any:
        """自定义验证函数"""
        if not callable(rule_value):
            raise ValueError(f"自定义验证规则必须是可调用对象")
        
        result = rule_value(value)
        if result is False:
            raise ValidationError(f"字段 '{field_name}' 验证失败")
        elif isinstance(result, str):
            raise ValidationError(f"字段 '{field_name}': {result}")
        
        return value


# 常用验证schema
PROJECT_SCHEMA = {
    'name': {
        'type': 'string',
        'required': True,
        'min_length': 1,
        'max_length': 200
    },
    'description': {
        'type': 'string',
        'required': False,
        'max_length': 1000
    },
    'config': {
        'type': 'dict',
        'required': False
    }
}

WORKFLOW_SCHEMA = {
    'project_id': {
        'type': 'string',
        'required': True,
        'pattern': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    },
    'workflow_type': {
        'type': 'string',
        'required': True,
        'enum': ['seven_step', 'creative', 'custom']
    }
}

CARD_SCHEMA = {
    'project_id': {
        'type': 'string',
        'required': True
    },
    'type': {
        'type': 'string',
        'required': True,
        'enum': ['character', 'scene', 'outline', 'chapter', 'worldview', 'other']
    },
    'data': {
        'type': 'dict',
        'required': True
    }
}


def get_validator() -> InputValidator:
    """获取验证器实例（单例模式）"""
    if not hasattr(get_validator, '_instance'):
        get_validator._instance = InputValidator()
    return get_validator._instance



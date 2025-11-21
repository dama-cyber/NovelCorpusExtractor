"""
配置验证模块
验证配置文件的有效性和完整性
"""

import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from core.exceptions import ConfigurationError, ValidationError

logger = logging.getLogger(__name__)


class ConfigValidator:
    """配置验证器"""
    
    REQUIRED_SECTIONS = ["api", "storage"]
    REQUIRED_API_FIELDS = ["base_url", "api_key"]
    REQUIRED_STORAGE_FIELDS = ["base_path"]
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化配置验证器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> bool:
        """
        验证配置
        
        Returns:
            bool: 验证是否通过
        """
        self.errors.clear()
        self.warnings.clear()
        
        # 验证必需部分
        self._validate_sections()
        
        # 验证API配置
        if "api" in self.config:
            self._validate_api_config()
        
        # 验证存储配置
        if "storage" in self.config:
            self._validate_storage_config()
        
        # 验证日志配置
        if "logging" in self.config:
            self._validate_logging_config()
        
        # 验证工作流配置
        if "workflows" in self.config:
            self._validate_workflow_config()
        
        return len(self.errors) == 0
    
    def _validate_sections(self):
        """验证必需部分"""
        for section in self.REQUIRED_SECTIONS:
            if section not in self.config:
                self.errors.append(f"缺少必需的配置部分: {section}")
    
    def _validate_api_config(self):
        """验证API配置"""
        api_config = self.config.get("api", {})
        
        # 检查必需字段
        for field in self.REQUIRED_API_FIELDS:
            if field not in api_config:
                self.errors.append(f"API配置缺少必需字段: {field}")
        
        # 验证base_url格式
        base_url = api_config.get("base_url", "")
        if base_url and not (base_url.startswith("http://") or base_url.startswith("https://")):
            self.warnings.append("API base_url 应该以 http:// 或 https:// 开头")
        
        # 验证timeout
        timeout = api_config.get("timeout", 30)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            self.errors.append("API timeout 必须是正数")
    
    def _validate_storage_config(self):
        """验证存储配置"""
        storage_config = self.config.get("storage", {})
        
        # 检查必需字段
        for field in self.REQUIRED_STORAGE_FIELDS:
            if field not in storage_config:
                self.errors.append(f"存储配置缺少必需字段: {field}")
        
        # 验证路径
        base_path = storage_config.get("base_path", "")
        if base_path:
            path = Path(base_path)
            if not path.exists():
                self.warnings.append(f"存储路径不存在: {base_path}")
            elif not path.is_dir():
                self.errors.append(f"存储路径不是目录: {base_path}")
    
    def _validate_logging_config(self):
        """验证日志配置"""
        logging_config = self.config.get("logging", {})
        
        # 验证日志级别
        level = logging_config.get("level", "INFO")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level.upper() not in valid_levels:
            self.warnings.append(f"无效的日志级别: {level}，将使用默认值")
    
    def _validate_workflow_config(self):
        """验证工作流配置"""
        workflow_config = self.config.get("workflows", {})
        
        # 验证工作流类型
        if isinstance(workflow_config, dict):
            for workflow_name, workflow_data in workflow_config.items():
                if not isinstance(workflow_data, dict):
                    self.warnings.append(f"工作流 '{workflow_name}' 配置格式不正确")
    
    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        """获取警告列表"""
        return self.warnings.copy()
    
    def raise_if_invalid(self):
        """
        如果配置无效则抛出异常
        
        Raises:
            ConfigurationError: 配置无效时抛出
        """
        if not self.validate():
            error_msg = "配置验证失败:\n" + "\n".join(self.errors)
            raise ConfigurationError(error_msg)


def validate_config(config: Dict[str, Any], raise_on_error: bool = True) -> bool:
    """
    验证配置的便捷函数
    
    Args:
        config: 配置字典
        raise_on_error: 是否在错误时抛出异常
    
    Returns:
        bool: 验证是否通过
    
    Raises:
        ConfigurationError: 如果 raise_on_error=True 且配置无效
    """
    validator = ConfigValidator(config)
    
    if raise_on_error:
        validator.raise_if_invalid()
    
    if not validator.validate():
        errors = validator.get_errors()
        warnings = validator.get_warnings()
        
        if errors:
            logger.error("配置验证失败:")
            for error in errors:
                logger.error(f"  - {error}")
        
        if warnings:
            logger.warning("配置验证警告:")
            for warning in warnings:
                logger.warning(f"  - {warning}")
        
        return False
    
    return True


def validate_and_fix_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证并修复配置（添加默认值）
    
    Args:
        config: 配置字典
    
    Returns:
        Dict[str, Any]: 修复后的配置
    """
    # 创建配置副本
    fixed_config = config.copy()
    
    # 添加默认API配置
    if "api" not in fixed_config:
        fixed_config["api"] = {}
    
    api_config = fixed_config["api"]
    api_config.setdefault("timeout", 30)
    api_config.setdefault("max_retries", 3)
    
    # 添加默认存储配置
    if "storage" not in fixed_config:
        fixed_config["storage"] = {}
    
    storage_config = fixed_config["storage"]
    storage_config.setdefault("projects_dir", "projects")
    storage_config.setdefault("cards_dir", "cards")
    storage_config.setdefault("workflows_dir", "workflows")
    
    # 添加默认日志配置
    if "logging" not in fixed_config:
        fixed_config["logging"] = {}
    
    logging_config = fixed_config["logging"]
    logging_config.setdefault("level", "INFO")
    logging_config.setdefault("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    return fixed_config



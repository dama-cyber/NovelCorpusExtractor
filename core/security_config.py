"""
安全配置模块
管理安全相关的配置和设置
"""

import os
import hashlib
import secrets
from typing import Dict, Optional, List
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)


class SecurityConfig:
    """安全配置管理器"""
    
    def __init__(self, config_file: str = "security_config.json"):
        """
        初始化安全配置
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self.config: Dict = self._load_config()
        self._ensure_secret_key()
    
    def _load_config(self) -> Dict:
        """加载安全配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载安全配置失败: {e}，使用默认配置")
        
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """默认安全配置"""
        return {
            "secret_key": None,
            "allowed_origins": ["http://localhost:3000", "http://localhost:8000"],
            "max_request_size": 10 * 1024 * 1024,  # 10MB
            "rate_limit_enabled": True,
            "cors_enabled": True,
            "api_key_required": False,
            "session_timeout": 3600,  # 1小时
            "password_min_length": 8,
            "require_https": False,
            "allowed_file_extensions": [".txt", ".md", ".json", ".yaml", ".yml"],
            "max_file_size": 50 * 1024 * 1024,  # 50MB
        }
    
    def _ensure_secret_key(self):
        """确保存在密钥"""
        if not self.config.get("secret_key"):
            # 生成新的密钥
            secret_key = secrets.token_urlsafe(32)
            self.config["secret_key"] = secret_key
            self.save_config()
            logger.info("已生成新的安全密钥")
    
    def save_config(self):
        """保存配置到文件"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存安全配置失败: {e}")
    
    def get_secret_key(self) -> str:
        """获取密钥"""
        return self.config.get("secret_key", "")
    
    def get_allowed_origins(self) -> List[str]:
        """获取允许的源"""
        return self.config.get("allowed_origins", [])
    
    def add_allowed_origin(self, origin: str):
        """添加允许的源"""
        origins = self.get_allowed_origins()
        if origin not in origins:
            origins.append(origin)
            self.config["allowed_origins"] = origins
            self.save_config()
    
    def remove_allowed_origin(self, origin: str):
        """移除允许的源"""
        origins = self.get_allowed_origins()
        if origin in origins:
            origins.remove(origin)
            self.config["allowed_origins"] = origins
            self.save_config()
    
    def is_rate_limit_enabled(self) -> bool:
        """是否启用限流"""
        return self.config.get("rate_limit_enabled", True)
    
    def is_cors_enabled(self) -> bool:
        """是否启用CORS"""
        return self.config.get("cors_enabled", True)
    
    def is_api_key_required(self) -> bool:
        """是否需要API密钥"""
        return self.config.get("api_key_required", False)
    
    def get_max_request_size(self) -> int:
        """获取最大请求大小（字节）"""
        return self.config.get("max_request_size", 10 * 1024 * 1024)
    
    def get_session_timeout(self) -> int:
        """获取会话超时时间（秒）"""
        return self.config.get("session_timeout", 3600)
    
    def get_allowed_file_extensions(self) -> List[str]:
        """获取允许的文件扩展名"""
        return self.config.get("allowed_file_extensions", [])
    
    def is_file_extension_allowed(self, filename: str) -> bool:
        """检查文件扩展名是否允许"""
        ext = Path(filename).suffix.lower()
        allowed = self.get_allowed_file_extensions()
        return ext in allowed or not allowed  # 如果列表为空，允许所有扩展名
    
    def get_max_file_size(self) -> int:
        """获取最大文件大小（字节）"""
        return self.config.get("max_file_size", 50 * 1024 * 1024)
    
    def validate_file(self, filename: str, file_size: int) -> bool:
        """
        验证文件
        
        Args:
            filename: 文件名
            file_size: 文件大小（字节）
        
        Returns:
            是否通过验证
        """
        # 检查扩展名
        if not self.is_file_extension_allowed(filename):
            return False
        
        # 检查文件大小
        if file_size > self.get_max_file_size():
            return False
        
        return True
    
    def hash_password(self, password: str) -> str:
        """
        哈希密码
        
        Args:
            password: 原始密码
        
        Returns:
            哈希后的密码
        """
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{hash_obj.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        验证密码
        
        Args:
            password: 原始密码
            hashed: 哈希后的密码
        
        Returns:
            是否匹配
        """
        try:
            salt, hash_hex = hashed.split(':')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_hex
        except Exception:
            return False
    
    def generate_api_key(self) -> str:
        """生成API密钥"""
        return secrets.token_urlsafe(32)
    
    def generate_session_token(self) -> str:
        """生成会话令牌"""
        return secrets.token_urlsafe(32)


# 全局安全配置实例
_security_config: Optional[SecurityConfig] = None


def get_security_config() -> SecurityConfig:
    """获取安全配置实例（单例模式）"""
    global _security_config
    if _security_config is None:
        _security_config = SecurityConfig()
    return _security_config



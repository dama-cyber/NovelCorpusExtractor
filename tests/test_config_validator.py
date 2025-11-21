"""
配置验证器测试
"""

import unittest
import tempfile
from pathlib import Path
from core.config_validator import (
    ConfigValidator, validate_config, validate_and_fix_config
)
from core.exceptions import ConfigurationError


class TestConfigValidator(unittest.TestCase):
    """配置验证器测试"""
    
    def test_valid_config(self):
        """测试有效配置"""
        config = {
            "api": {
                "base_url": "https://api.example.com",
                "api_key": "test_key",
                "timeout": 30
            },
            "storage": {
                "base_path": "/tmp/test"
            }
        }
        
        validator = ConfigValidator(config)
        self.assertTrue(validator.validate())
        self.assertEqual(len(validator.get_errors()), 0)
    
    def test_missing_section(self):
        """测试缺少必需部分"""
        config = {
            "api": {
                "base_url": "https://api.example.com",
                "api_key": "test_key"
            }
        }
        
        validator = ConfigValidator(config)
        self.assertFalse(validator.validate())
        self.assertGreater(len(validator.get_errors()), 0)
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        config = {
            "api": {
                "base_url": "https://api.example.com"
            },
            "storage": {
                "base_path": "/tmp/test"
            }
        }
        
        validator = ConfigValidator(config)
        self.assertFalse(validator.validate())
        self.assertIn("api_key", str(validator.get_errors()))
    
    def test_invalid_timeout(self):
        """测试无效的timeout"""
        config = {
            "api": {
                "base_url": "https://api.example.com",
                "api_key": "test_key",
                "timeout": -1
            },
            "storage": {
                "base_path": "/tmp/test"
            }
        }
        
        validator = ConfigValidator(config)
        self.assertFalse(validator.validate())
        self.assertGreater(len(validator.get_errors()), 0)
    
    def test_validate_and_fix(self):
        """测试验证并修复配置"""
        config = {
            "api": {
                "base_url": "https://api.example.com",
                "api_key": "test_key"
            }
        }
        
        fixed = validate_and_fix_config(config)
        
        # 应该添加默认值
        self.assertIn("timeout", fixed["api"])
        self.assertIn("storage", fixed)
        self.assertIn("logging", fixed)
    
    def test_raise_on_error(self):
        """测试错误时抛出异常"""
        config = {
            "api": {
                "base_url": "https://api.example.com"
            }
        }
        
        with self.assertRaises(ConfigurationError):
            validate_config(config, raise_on_error=True)


if __name__ == '__main__':
    unittest.main()



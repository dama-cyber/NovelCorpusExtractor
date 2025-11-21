"""
异常类测试
"""

import unittest
from core.exceptions import (
    NovelExtractorError,
    ConfigurationError,
    APIError,
    ValidationError,
    FileProcessingError,
    WorkflowError
)


class TestExceptions(unittest.TestCase):
    """异常类测试"""
    
    def test_novel_extractor_error(self):
        """测试基础异常类"""
        error = NovelExtractorError("测试错误")
        self.assertEqual(str(error), "测试错误")
        self.assertIsInstance(error, Exception)
    
    def test_configuration_error(self):
        """测试配置错误"""
        error = ConfigurationError("配置错误")
        self.assertIsInstance(error, NovelExtractorError)
    
    def test_api_error(self):
        """测试API错误"""
        error = APIError("API错误", provider="openai", status_code=500)
        self.assertIsInstance(error, NovelExtractorError)
        self.assertEqual(error.provider, "openai")
        self.assertEqual(error.status_code, 500)
    
    def test_validation_error(self):
        """测试验证错误"""
        error = ValidationError("验证失败")
        self.assertIsInstance(error, NovelExtractorError)
    
    def test_file_processing_error(self):
        """测试文件处理错误"""
        error = FileProcessingError("文件处理失败")
        self.assertIsInstance(error, NovelExtractorError)
    
    def test_workflow_error(self):
        """测试工作流错误"""
        error = WorkflowError("工作流失败")
        self.assertIsInstance(error, NovelExtractorError)


if __name__ == '__main__':
    unittest.main()



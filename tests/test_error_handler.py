"""
错误处理测试
"""

import unittest
from fastapi import HTTPException
from core.error_handler import (
    error_handler, sync_error_handler, get_status_code,
    validate_request_data, safe_execute
)
from core.exceptions import (
    ValidationError, ConfigurationError, APIError,
    FileProcessingError, WorkflowError
)


class TestErrorHandler(unittest.TestCase):
    """错误处理测试"""
    
    def test_get_status_code(self):
        """测试获取状态码"""
        self.assertEqual(get_status_code(ValidationError("test")), 400)
        self.assertEqual(get_status_code(ConfigurationError("test")), 500)
        self.assertEqual(get_status_code(FileProcessingError("test")), 400)
        self.assertEqual(get_status_code(WorkflowError("test")), 500)
        
        # 测试APIError的状态码
        api_error = APIError("test", status_code=403)
        self.assertEqual(get_status_code(api_error), 403)
    
    def test_validate_request_data(self):
        """测试请求数据验证"""
        # 正常情况
        data = {"name": "test", "age": 20}
        validate_request_data(data, ["name", "age"])
        
        # 缺少必需字段
        with self.assertRaises(ValidationError):
            validate_request_data(data, ["name", "age", "email"])
        
        # 类型错误
        with self.assertRaises(ValidationError):
            validate_request_data(
                data,
                ["name", "age"],
                field_types={"age": str}
            )
    
    def test_safe_execute(self):
        """测试安全执行"""
        def success_func():
            return "success"
        
        def fail_func():
            raise ValueError("error")
        
        # 成功执行
        result = safe_execute(success_func)
        self.assertEqual(result, "success")
        
        # 失败执行
        result = safe_execute(fail_func, default_return="default")
        self.assertEqual(result, "default")
    
    async def test_error_handler_decorator(self):
        """测试错误处理装饰器"""
        @error_handler
        async def test_func():
            raise ValidationError("test error")
        
        # 应该转换为HTTPException
        with self.assertRaises(HTTPException) as context:
            await test_func()
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("test error", context.exception.detail)


if __name__ == '__main__':
    unittest.main()



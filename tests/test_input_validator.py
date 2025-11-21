"""
输入验证器测试
"""

import unittest
from core.input_validator import InputValidator, ValidationError, PROJECT_SCHEMA, WORKFLOW_SCHEMA, CARD_SCHEMA


class TestInputValidator(unittest.TestCase):
    """输入验证器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.validator = InputValidator()
    
    def test_required_field(self):
        """测试必填字段验证"""
        schema = {
            'name': {'type': 'string', 'required': True}
        }
        
        # 缺少必填字段应该失败
        with self.assertRaises(ValidationError):
            self.validator.validate({}, schema)
        
        # 提供必填字段应该成功
        result = self.validator.validate({'name': 'test'}, schema)
        self.assertEqual(result['name'], 'test')
    
    def test_string_validation(self):
        """测试字符串验证"""
        schema = {
            'name': {'type': 'string', 'min_length': 3, 'max_length': 10}
        }
        
        # 长度不足应该失败
        with self.assertRaises(ValidationError):
            self.validator.validate({'name': 'ab'}, schema)
        
        # 长度过长应该失败
        with self.assertRaises(ValidationError):
            self.validator.validate({'name': 'a' * 11}, schema)
        
        # 有效字符串应该成功
        result = self.validator.validate({'name': 'test'}, schema)
        self.assertEqual(result['name'], 'test')
    
    def test_integer_validation(self):
        """测试整数验证"""
        schema = {
            'age': {'type': 'integer', 'min_value': 0, 'max_value': 150}
        }
        
        # 无效整数应该失败
        with self.assertRaises(ValidationError):
            self.validator.validate({'age': 'not_a_number'}, schema)
        
        # 超出范围应该失败
        with self.assertRaises(ValidationError):
            self.validator.validate({'age': 200}, schema)
        
        # 有效整数应该成功
        result = self.validator.validate({'age': 25}, schema)
        self.assertEqual(result['age'], 25)
    
    def test_email_validation(self):
        """测试邮箱验证"""
        schema = {
            'email': {'type': 'email'}
        }
        
        # 无效邮箱应该失败
        with self.assertRaises(ValidationError):
            self.validator.validate({'email': 'invalid_email'}, schema)
        
        # 有效邮箱应该成功
        result = self.validator.validate({'email': 'test@example.com'}, schema)
        self.assertEqual(result['email'], 'test@example.com')
    
    def test_enum_validation(self):
        """测试枚举验证"""
        schema = {
            'status': {'type': 'string', 'enum': ['active', 'inactive', 'pending']}
        }
        
        # 无效枚举值应该失败
        with self.assertRaises(ValidationError):
            self.validator.validate({'status': 'invalid'}, schema)
        
        # 有效枚举值应该成功
        result = self.validator.validate({'status': 'active'}, schema)
        self.assertEqual(result['status'], 'active')
    
    def test_project_schema(self):
        """测试项目schema"""
        # 有效项目数据
        data = {
            'name': 'Test Project',
            'description': 'Test Description'
        }
        result = self.validator.validate(data, PROJECT_SCHEMA)
        self.assertEqual(result['name'], 'Test Project')
        
        # 缺少必填字段应该失败
        with self.assertRaises(ValidationError):
            self.validator.validate({'description': 'Test'}, PROJECT_SCHEMA)
    
    def test_workflow_schema(self):
        """测试工作流schema"""
        # 有效工作流数据
        data = {
            'project_id': '12345678-1234-1234-1234-123456789012',
            'workflow_type': 'seven_step'
        }
        result = self.validator.validate(data, WORKFLOW_SCHEMA)
        self.assertEqual(result['workflow_type'], 'seven_step')
        
        # 无效UUID应该失败
        with self.assertRaises(ValidationError):
            self.validator.validate({
                'project_id': 'invalid-uuid',
                'workflow_type': 'seven_step'
            }, WORKFLOW_SCHEMA)


if __name__ == '__main__':
    unittest.main()



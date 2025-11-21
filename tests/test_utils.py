"""
工具函数测试
"""

import unittest
from core.utils import (
    generate_id, ensure_dir, safe_read_json, safe_write_json,
    safe_read_yaml, safe_write_yaml, get_timestamp, merge_dicts,
    deep_merge_dicts, validate_uuid, sanitize_filename, chunk_list,
    flatten_dict, safe_get, format_file_size, truncate_string
)
import tempfile
import shutil
from pathlib import Path


class TestUtils(unittest.TestCase):
    """工具函数测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def test_generate_id(self):
        """测试生成ID"""
        id1 = generate_id()
        id2 = generate_id()
        self.assertNotEqual(id1, id2)
        self.assertEqual(len(id1), 36)  # UUID格式
    
    def test_ensure_dir(self):
        """测试确保目录存在"""
        dir_path = Path(self.temp_dir) / "test" / "subdir"
        result = ensure_dir(dir_path)
        self.assertTrue(result.exists())
        self.assertTrue(result.is_dir())
    
    def test_safe_read_write_json(self):
        """测试安全JSON读写"""
        file_path = Path(self.temp_dir) / "test.json"
        data = {"key": "value"}
        
        # 写入
        self.assertTrue(safe_write_json(file_path, data))
        
        # 读取
        result = safe_read_json(file_path)
        self.assertEqual(result, data)
        
        # 读取不存在的文件
        result = safe_read_json(Path(self.temp_dir) / "nonexistent.json", default={})
        self.assertEqual(result, {})
    
    def test_safe_read_write_yaml(self):
        """测试安全YAML读写"""
        file_path = Path(self.temp_dir) / "test.yaml"
        data = {"key": "value"}
        
        # 写入
        self.assertTrue(safe_write_yaml(file_path, data))
        
        # 读取
        result = safe_read_yaml(file_path)
        self.assertEqual(result, data)
    
    def test_get_timestamp(self):
        """测试获取时间戳"""
        timestamp = get_timestamp()
        self.assertIsInstance(timestamp, str)
        self.assertIn("T", timestamp)  # ISO格式包含T
    
    def test_merge_dicts(self):
        """测试合并字典"""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        result = merge_dicts(dict1, dict2)
        self.assertEqual(result, {"a": 1, "b": 2, "c": 3, "d": 4})
    
    def test_deep_merge_dicts(self):
        """测试深度合并字典"""
        base = {"a": {"b": 1, "c": 2}}
        update = {"a": {"b": 3}, "d": 4}
        result = deep_merge_dicts(base, update)
        self.assertEqual(result, {"a": {"b": 3, "c": 2}, "d": 4})
    
    def test_validate_uuid(self):
        """测试UUID验证"""
        valid_uuid = "12345678-1234-1234-1234-123456789012"
        invalid_uuid = "invalid-uuid"
        
        self.assertTrue(validate_uuid(valid_uuid))
        self.assertFalse(validate_uuid(invalid_uuid))
    
    def test_sanitize_filename(self):
        """测试文件名清理"""
        filename = "test<>file.txt"
        sanitized = sanitize_filename(filename)
        self.assertNotIn("<", sanitized)
        self.assertNotIn(">", sanitized)
    
    def test_chunk_list(self):
        """测试列表分块"""
        lst = [1, 2, 3, 4, 5, 6, 7]
        chunks = chunk_list(lst, 3)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], [1, 2, 3])
    
    def test_flatten_dict(self):
        """测试展平字典"""
        nested = {"a": {"b": {"c": 1}}}
        flattened = flatten_dict(nested)
        self.assertEqual(flattened, {"a.b.c": 1})
    
    def test_safe_get(self):
        """测试安全获取嵌套值"""
        data = {"a": {"b": {"c": 1}}}
        self.assertEqual(safe_get(data, "a", "b", "c"), 1)
        self.assertEqual(safe_get(data, "a", "b", "d", default=0), 0)
    
    def test_format_file_size(self):
        """测试格式化文件大小"""
        self.assertEqual(format_file_size(1024), "1.00 KB")
        self.assertEqual(format_file_size(1024 * 1024), "1.00 MB")
    
    def test_truncate_string(self):
        """测试截断字符串"""
        s = "这是一个很长的字符串"
        truncated = truncate_string(s, 5)
        self.assertLessEqual(len(truncated), 5)
        self.assertTrue(truncated.endswith("..."))


if __name__ == '__main__':
    unittest.main()



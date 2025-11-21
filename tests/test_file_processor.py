"""
文件处理器测试
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from core.file_processor import FileProcessor, get_file_processor


class TestFileProcessor(unittest.TestCase):
    """文件处理器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = FileProcessor()
    
    def tearDown(self):
        """清理测试环境"""
        self.processor.close()
        shutil.rmtree(self.temp_dir)
    
    def test_read_write_json(self):
        """测试JSON读写"""
        file_path = Path(self.temp_dir) / "test.json"
        data = {"key": "value", "number": 123}
        
        # 写入
        self.processor.write_json(file_path, data)
        self.assertTrue(file_path.exists())
        
        # 读取
        result = self.processor.read_json(file_path)
        self.assertEqual(result, data)
    
    def test_read_write_yaml(self):
        """测试YAML读写"""
        file_path = Path(self.temp_dir) / "test.yaml"
        data = {"key": "value", "number": 123}
        
        # 写入
        self.processor.write_yaml(file_path, data)
        self.assertTrue(file_path.exists())
        
        # 读取
        result = self.processor.read_yaml(file_path)
        self.assertEqual(result, data)
    
    def test_cache(self):
        """测试缓存功能"""
        file_path = Path(self.temp_dir) / "test.json"
        data = {"key": "value"}
        
        # 写入并读取
        self.processor.write_json(file_path, data)
        result1 = self.processor.read_json(file_path, use_cache=True)
        
        # 再次读取应该使用缓存
        result2 = self.processor.read_json(file_path, use_cache=True)
        self.assertEqual(result1, result2)
    
    def test_clear_cache(self):
        """测试清除缓存"""
        file_path = Path(self.temp_dir) / "test.json"
        data = {"key": "value"}
        
        self.processor.write_json(file_path, data)
        self.processor.read_json(file_path, use_cache=True)
        
        # 清除缓存
        self.processor.clear_cache(file_path)
        
        # 缓存应该已清除
        self.assertNotIn(str(file_path.absolute()), self.processor._cache)


if __name__ == '__main__':
    unittest.main()



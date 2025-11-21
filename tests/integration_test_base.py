"""
集成测试基类
提供集成测试的基础设施和工具
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
from typing import Optional

from main import NovelCorpusExtractor
from core.project_manager import ProjectManager
from core.card_manager import CardManager


class IntegrationTestBase(unittest.TestCase):
    """集成测试基类"""
    
    @classmethod
    def setUpClass(cls):
        """类级别设置"""
        cls.test_dir = tempfile.mkdtemp(prefix="novel_test_")
        cls.config_path = Path(cls.test_dir) / "test_config.yaml"
        cls._create_test_config()
    
    @classmethod
    def tearDownClass(cls):
        """类级别清理"""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    @classmethod
    def _create_test_config(cls):
        """创建测试配置"""
        config_content = """
api:
  base_url: "http://test-api.example.com"
  api_key: "test_key"
  timeout: 30

storage:
  base_path: "{base_path}"
  projects_dir: "projects"
  cards_dir: "cards"
  workflows_dir: "workflows"

logging:
  level: "DEBUG"
  file: "test.log"
""".format(base_path=cls.test_dir)
        
        with open(cls.config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
    
    def setUp(self):
        """测试前设置"""
        self.extractor: Optional[NovelCorpusExtractor] = None
        self.project_manager: Optional[ProjectManager] = None
        self.card_manager: Optional[CardManager] = None
    
    def tearDown(self):
        """测试后清理"""
        if self.extractor:
            # 清理资源
            pass
    
    def create_extractor(self) -> NovelCorpusExtractor:
        """创建提取器实例"""
        if self.extractor is None:
            self.extractor = NovelCorpusExtractor(str(self.config_path))
        return self.extractor
    
    def create_project_manager(self) -> ProjectManager:
        """创建项目管理器实例"""
        if self.project_manager is None:
            extractor = self.create_extractor()
            self.project_manager = ProjectManager(extractor.config)
        return self.project_manager
    
    def create_card_manager(self) -> CardManager:
        """创建卡片管理器实例"""
        if self.card_manager is None:
            extractor = self.create_extractor()
            self.card_manager = CardManager(extractor.config)
        return self.card_manager
    
    def get_test_project_path(self, project_name: str) -> Path:
        """获取测试项目路径"""
        return Path(self.test_dir) / "projects" / project_name
    
    def get_test_card_path(self, card_name: str) -> Path:
        """获取测试卡片路径"""
        return Path(self.test_dir) / "cards" / card_name
    
    def assert_project_exists(self, project_name: str):
        """断言项目存在"""
        project_path = self.get_test_project_path(project_name)
        self.assertTrue(project_path.exists(), f"项目 {project_name} 不存在")
    
    def assert_card_exists(self, card_name: str):
        """断言卡片存在"""
        card_path = self.get_test_card_path(card_name)
        self.assertTrue(card_path.exists(), f"卡片 {card_name} 不存在")


if __name__ == '__main__':
    unittest.main()



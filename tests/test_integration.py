"""
集成测试
测试各个模块之间的集成
"""

import unittest
from tests.integration_test_base import IntegrationTestBase
from tests.mock_data_generator import MockDataGenerator


class TestProjectCardIntegration(IntegrationTestBase):
    """项目和卡片集成测试"""
    
    def test_create_project_and_card(self):
        """测试创建项目和卡片"""
        project_manager = self.create_project_manager()
        card_manager = self.create_card_manager()
        generator = MockDataGenerator()
        
        # 创建项目
        project_data = generator.generate_project_data()
        project = project_manager.create_project(
            project_data["name"],
            project_data["description"]
        )
        self.assertIsNotNone(project)
        self.assert_project_exists(project_data["name"])
        
        # 创建卡片
        card_data = generator.generate_card_data()
        card = card_manager.create_card(
            card_data["title"],
            card_data["content"],
            card_data["type"]
        )
        self.assertIsNotNone(card)
    
    def test_workflow_with_project(self):
        """测试工作流与项目集成"""
        extractor = self.create_extractor()
        project_manager = self.create_project_manager()
        generator = MockDataGenerator()
        
        # 创建项目
        project_data = generator.generate_project_data()
        project = project_manager.create_project(
            project_data["name"],
            project_data["description"]
        )
        
        # 创建工作流
        workflow_data = generator.generate_workflow_data()
        # 这里可以测试工作流与项目的关联


class TestCacheAndPerformanceIntegration(IntegrationTestBase):
    """缓存和性能监控集成测试"""
    
    def test_cache_with_extractor(self):
        """测试提取器与缓存集成"""
        from core.cache_manager import get_cache_manager
        
        extractor = self.create_extractor()
        cache_manager = get_cache_manager()
        
        # 测试缓存功能
        cache_key = "test_extractor_config"
        cache_manager.set(cache_key, extractor.config, ttl=60)
        
        cached_config = cache_manager.get(cache_key)
        self.assertIsNotNone(cached_config)
    
    def test_performance_monitoring(self):
        """测试性能监控集成"""
        from core.performance_monitor import get_performance_monitor
        
        monitor = get_performance_monitor()
        
        # 记录操作
        with monitor.measure("test_operation"):
            # 模拟操作
            pass
        
        # 获取指标
        metrics = monitor.get_metrics()
        self.assertIn("test_operation", metrics)


if __name__ == '__main__':
    unittest.main()



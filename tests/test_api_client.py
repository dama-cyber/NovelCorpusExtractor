"""
API客户端测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from client import NovelCorpusClient, AsyncNovelCorpusClient
from client.models import Project, Card, Workflow, HealthStatus
from core.exceptions import APIError, ValidationError


class TestNovelCorpusClient(unittest.TestCase):
    """同步客户端测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = NovelCorpusClient(
            base_url="http://localhost:8000",
            timeout=10
        )
    
    def tearDown(self):
        """清理测试环境"""
        self.client.close()
    
    @patch('client.api_client.requests.Session.request')
    def test_health_check(self, mock_request):
        """测试健康检查"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00",
            "components": {}
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        health = self.client.health_check()
        
        self.assertIsInstance(health, HealthStatus)
        self.assertEqual(health.status, "healthy")
        mock_request.assert_called_once()
    
    @patch('client.api_client.requests.Session.request')
    def test_create_project(self, mock_request):
        """测试创建项目"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "project_123",
            "name": "测试项目",
            "description": "测试描述"
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        project = self.client.create_project(
            name="测试项目",
            description="测试描述"
        )
        
        self.assertIsInstance(project, Project)
        self.assertEqual(project.id, "project_123")
        self.assertEqual(project.name, "测试项目")
    
    @patch('client.api_client.requests.Session.request')
    def test_list_projects(self, mock_request):
        """测试列出项目"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "project_1", "name": "项目1"},
            {"id": "project_2", "name": "项目2"}
        ]
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        projects = self.client.list_projects()
        
        self.assertEqual(len(projects), 2)
        self.assertIsInstance(projects[0], Project)
    
    @patch('client.api_client.requests.Session.request')
    def test_process_novel_with_file(self, mock_request):
        """测试处理小说文件"""
        # 创建临时文件
        test_file = Path("test_novel.txt")
        test_file.write_text("测试小说内容", encoding="utf-8")
        
        try:
            mock_response = Mock()
            mock_response.json.return_value = {
                "chunkResults": [],
                "workflow": None
            }
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response
            
            result = self.client.process_novel(
                file_path=str(test_file),
                novel_type="测试"
            )
            
            self.assertIsNotNone(result)
            mock_request.assert_called_once()
        finally:
            if test_file.exists():
                test_file.unlink()
    
    @patch('client.api_client.requests.Session.request')
    def test_process_novel_with_text(self, mock_request):
        """测试处理文本"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "chunkResults": [],
            "workflow": None
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = self.client.process_novel(
            sample_text="测试文本内容",
            novel_type="测试"
        )
        
        self.assertIsNotNone(result)
    
    def test_process_novel_no_input(self):
        """测试无输入时抛出异常"""
        with self.assertRaises(ValidationError):
            self.client.process_novel()
    
    @patch('client.api_client.requests.Session.request')
    def test_api_error_handling(self, mock_request):
        """测试API错误处理"""
        mock_request.side_effect = Exception("连接失败")
        
        with self.assertRaises(APIError):
            self.client.health_check()


class TestAsyncNovelCorpusClient(unittest.IsolatedAsyncioTestCase):
    """异步客户端测试"""
    
    async def asyncSetUp(self):
        """设置测试环境"""
        self.client = AsyncNovelCorpusClient(
            base_url="http://localhost:8000"
        )
    
    async def asyncTearDown(self):
        """清理测试环境"""
        await self.client.close()
    
    @patch('client.api_client.aiohttp.ClientSession.request')
    async def test_health_check_async(self, mock_request):
        """测试异步健康检查"""
        mock_response = MagicMock()
        mock_response.json = Mock(return_value={
            "status": "healthy",
            "components": {}
        })
        mock_response.raise_for_status = Mock()
        mock_response.__aenter__ = Mock(return_value=mock_response)
        mock_response.__aexit__ = Mock(return_value=None)
        mock_request.return_value = mock_response
        
        health = await self.client.health_check()
        
        self.assertIsInstance(health, HealthStatus)
        self.assertEqual(health.status, "healthy")


if __name__ == '__main__':
    unittest.main()



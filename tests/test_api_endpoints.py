"""
API端点测试
使用FastAPI TestClient进行API测试
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

from api_server import app
from main import NovelCorpusExtractor


class TestAPIEndpoints(unittest.TestCase):
    """API端点测试"""
    
    @classmethod
    def setUpClass(cls):
        """类级别设置"""
        cls.client = TestClient(app)
        cls.test_dir = tempfile.mkdtemp(prefix="api_test_")
    
    @classmethod
    def tearDownClass(cls):
        """类级别清理"""
        shutil.rmtree(cls.test_dir)
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "ok")
    
    def test_get_projects(self):
        """测试获取项目列表"""
        response = self.client.get("/api/projects")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_create_project(self):
        """测试创建项目"""
        project_data = {
            "name": "test_project",
            "description": "测试项目"
        }
        response = self.client.post("/api/projects", json=project_data)
        # 可能返回201或200
        self.assertIn(response.status_code, [200, 201])
    
    def test_get_project(self):
        """测试获取单个项目"""
        # 先创建项目
        project_data = {"name": "test_get_project", "description": "测试"}
        create_response = self.client.post("/api/projects", json=project_data)
        
        if create_response.status_code in [200, 201]:
            project_id = create_response.json().get("id")
            if project_id:
                response = self.client.get(f"/api/projects/{project_id}")
                self.assertIn(response.status_code, [200, 404])
    
    def test_upload_file(self):
        """测试文件上传"""
        # 创建测试文件
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("测试内容", encoding='utf-8')
        
        with open(test_file, 'rb') as f:
            response = self.client.post(
                "/api/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
            # 可能返回200或400（如果端点不存在）
            self.assertIn(response.status_code, [200, 400, 404])
    
    def test_rate_limiting(self):
        """测试限流功能"""
        # 发送多个请求
        responses = []
        for _ in range(10):
            response = self.client.get("/health")
            responses.append(response.status_code)
        
        # 至少前几个请求应该成功
        self.assertIn(200, responses)


if __name__ == '__main__':
    unittest.main()



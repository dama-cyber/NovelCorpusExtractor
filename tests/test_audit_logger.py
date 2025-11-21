"""
审计日志测试
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from core.audit_logger import AuditLogger, AuditEventType, get_audit_logger


class TestAuditLogger(unittest.TestCase):
    """审计日志测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = AuditLogger(log_dir=self.temp_dir)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def test_log_user_action(self):
        """测试记录用户操作"""
        self.audit_logger.log_user_action(
            "create_project",
            user_id="user1",
            resource_type="project",
            resource_id="project1"
        )
        
        # 验证日志文件存在
        log_file = Path(self.temp_dir) / "audit.log"
        self.assertTrue(log_file.exists())
    
    def test_log_api_call(self):
        """测试记录API调用"""
        self.audit_logger.log_api_call(
            "/api/projects",
            "POST",
            user_id="user1",
            success=True
        )
        
        log_file = Path(self.temp_dir) / "audit.log"
        self.assertTrue(log_file.exists())
    
    def test_log_workflow_action(self):
        """测试记录工作流操作"""
        self.audit_logger.log_workflow_action(
            "start_workflow",
            workflow_id="workflow1",
            project_id="project1",
            user_id="user1"
        )
        
        log_file = Path(self.temp_dir) / "audit.log"
        self.assertTrue(log_file.exists())
    
    def test_query_logs(self):
        """测试查询日志"""
        # 记录一些日志
        self.audit_logger.log_user_action("action1", "user1")
        self.audit_logger.log_user_action("action2", "user2")
        
        # 查询所有日志
        logs = self.audit_logger.query_logs(limit=10)
        self.assertGreaterEqual(len(logs), 2)
        
        # 按用户ID查询
        logs = self.audit_logger.query_logs(user_id="user1", limit=10)
        self.assertGreaterEqual(len(logs), 1)
        self.assertEqual(logs[0].get('user_id'), 'user1')
    
    def test_get_audit_logger_singleton(self):
        """测试单例模式"""
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()
        self.assertIs(logger1, logger2)


if __name__ == '__main__':
    unittest.main()



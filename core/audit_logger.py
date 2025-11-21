"""
审计日志模块
记录系统操作和重要事件，用于审计和追踪
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import threading

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """审计事件类型"""
    USER_ACTION = "user_action"
    API_CALL = "api_call"
    WORKFLOW_ACTION = "workflow_action"
    PROJECT_ACTION = "project_action"
    CARD_ACTION = "card_action"
    CONFIG_CHANGE = "config_change"
    SECURITY_EVENT = "security_event"
    ERROR = "error"
    SYSTEM_EVENT = "system_event"


class AuditLogger:
    """审计日志记录器"""
    
    def __init__(
        self,
        log_dir: str = "logs/audit",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 10
    ):
        """
        初始化审计日志记录器
        
        Args:
            log_dir: 日志目录
            max_file_size: 单个日志文件最大大小（字节）
            backup_count: 保留的备份文件数量
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self._lock = threading.Lock()
        
        # 设置审计日志处理器
        self._setup_handler()
    
    def _setup_handler(self):
        """设置日志处理器"""
        from logging.handlers import RotatingFileHandler
        
        log_file = self.log_dir / "audit.log"
        handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        # 设置格式
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # 创建审计日志记录器
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        self.audit_logger.addHandler(handler)
        self.audit_logger.propagate = False
    
    def log(
        self,
        event_type: AuditEventType,
        action: str,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        记录审计事件
        
        Args:
            event_type: 事件类型
            action: 操作名称
            user_id: 用户ID
            resource_type: 资源类型
            resource_id: 资源ID
            details: 详细信息
            success: 是否成功
            error_message: 错误消息
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type.value,
            'action': action,
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'success': success,
            'error_message': error_message,
            'details': details or {}
        }
        
        log_message = json.dumps(event, ensure_ascii=False)
        
        with self._lock:
            if success:
                self.audit_logger.info(log_message)
            else:
                self.audit_logger.warning(log_message)
    
    def log_user_action(
        self,
        action: str,
        user_id: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """记录用户操作"""
        self.log(
            AuditEventType.USER_ACTION,
            action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
    
    def log_api_call(
        self,
        endpoint: str,
        method: str,
        user_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """记录API调用"""
        self.log(
            AuditEventType.API_CALL,
            f"{method} {endpoint}",
            user_id=user_id,
            resource_type="api",
            resource_id=endpoint,
            details=details,
            success=success,
            error_message=error_message
        )
    
    def log_workflow_action(
        self,
        action: str,
        workflow_id: str,
        project_id: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """记录工作流操作"""
        self.log(
            AuditEventType.WORKFLOW_ACTION,
            action,
            user_id=user_id,
            resource_type="workflow",
            resource_id=workflow_id,
            details={
                'project_id': project_id,
                **(details or {})
            }
        )
    
    def log_project_action(
        self,
        action: str,
        project_id: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """记录项目操作"""
        self.log(
            AuditEventType.PROJECT_ACTION,
            action,
            user_id=user_id,
            resource_type="project",
            resource_id=project_id,
            details=details
        )
    
    def log_card_action(
        self,
        action: str,
        card_id: str,
        project_id: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """记录卡片操作"""
        self.log(
            AuditEventType.CARD_ACTION,
            action,
            user_id=user_id,
            resource_type="card",
            resource_id=card_id,
            details={
                'project_id': project_id,
                **(details or {})
            }
        )
    
    def log_security_event(
        self,
        event: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "medium"
    ):
        """记录安全事件"""
        self.log(
            AuditEventType.SECURITY_EVENT,
            event,
            user_id=user_id,
            details={
                'severity': severity,
                **(details or {})
            }
        )
    
    def query_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        查询审计日志
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            event_type: 事件类型
            user_id: 用户ID
            resource_type: 资源类型
            resource_id: 资源ID
            limit: 返回结果数量限制
        
        Returns:
            日志记录列表
        """
        log_file = self.log_dir / "audit.log"
        if not log_file.exists():
            return []
        
        results = []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        
                        # 过滤条件
                        if start_time and datetime.fromisoformat(event['timestamp']) < start_time:
                            continue
                        if end_time and datetime.fromisoformat(event['timestamp']) > end_time:
                            continue
                        if event_type and event['event_type'] != event_type.value:
                            continue
                        if user_id and event.get('user_id') != user_id:
                            continue
                        if resource_type and event.get('resource_type') != resource_type:
                            continue
                        if resource_id and event.get('resource_id') != resource_id:
                            continue
                        
                        results.append(event)
                        
                        if len(results) >= limit:
                            break
                    except (json.JSONDecodeError, KeyError):
                        continue
        except Exception as e:
            logger.error(f"查询审计日志失败: {e}")
        
        return results


# 全局审计日志记录器实例
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """获取审计日志记录器实例（单例模式）"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger



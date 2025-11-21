"""
斜杠命令系统
提供快速访问常用功能的命令接口
"""

from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import re
import logging

from .workflows import WorkflowFactory

logger = logging.getLogger(__name__)


class SlashCommand:
    """斜杠命令"""
    
    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable,
        aliases: List[str] = None,
        parameters: List[Dict] = None
    ):
        self.name = name
        self.description = description
        self.handler = handler
        self.aliases = aliases or []
        self.parameters = parameters or []
    
    def matches(self, command_text: str) -> bool:
        """检查命令是否匹配"""
        command_text = command_text.strip().lower()
        if command_text.startswith(f"/{self.name}"):
            return True
        for alias in self.aliases:
            if command_text.startswith(f"/{alias}"):
                return True
        return False
    
    async def execute(self, command_text: str, context: Dict) -> Any:
        """执行命令"""
        # 解析参数
        args = self._parse_args(command_text)
        return await self.handler(args, context)
    
    def _parse_args(self, command_text: str) -> Dict:
        """解析命令参数"""
        # 简单的参数解析实现
        parts = command_text.split()
        args = {}
        for i, param in enumerate(self.parameters):
            if i + 1 < len(parts):
                args[param['name']] = parts[i + 1]
        return args


class SlashCommandProcessor:
    """斜杠命令处理器"""
    
    def __init__(self, workflow_manager=None, card_manager=None, project_manager=None, llm_client=None):
        self.workflow_manager = workflow_manager
        self.card_manager = card_manager
        self.project_manager = project_manager
        self.llm_client = llm_client
        self.commands: Dict[str, SlashCommand] = {}
        self._register_default_commands()
    
    def _register_default_commands(self):
        """注册默认命令"""
        # /constitution
        self.register_command(SlashCommand(
            name="constitution",
            description="建立或编辑创作原则",
            handler=self._handle_constitution,
            aliases=["const", "原则"]
        ))
        
        # /specify
        self.register_command(SlashCommand(
            name="specify",
            description="定义故事需求规范",
            handler=self._handle_specify,
            aliases=["spec", "规范", "需求"]
        ))
        
        # /clarify
        self.register_command(SlashCommand(
            name="clarify",
            description="澄清歧义，生成关键问题",
            handler=self._handle_clarify,
            aliases=["clar", "澄清", "问题"]
        ))
        
        # /plan
        self.register_command(SlashCommand(
            name="plan",
            description="生成创作计划",
            handler=self._handle_plan,
            aliases=["计划", "规划"]
        ))
        
        # /tasks
        self.register_command(SlashCommand(
            name="tasks",
            description="管理任务列表",
            handler=self._handle_tasks,
            aliases=["task", "任务"]
        ))
        
        # /write
        self.register_command(SlashCommand(
            name="write",
            description="开始写作",
            handler=self._handle_write,
            aliases=["写作", "写"]
        ))
        
        # /analyze
        self.register_command(SlashCommand(
            name="analyze",
            description="验证质量和一致性",
            handler=self._handle_analyze,
            aliases=["analysis", "验证", "分析"]
        ))
    
    def register_command(self, command: SlashCommand):
        """注册命令"""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command
    
    async def process(self, command_text: str, context: Dict) -> Dict:
        """处理命令"""
        command_text = command_text.strip()
        
        if not command_text.startswith("/"):
            return {"error": "命令必须以 / 开头"}
        
        # 查找匹配的命令
        for command in self.commands.values():
            if command.matches(command_text):
                try:
                    result = await command.execute(command_text, context)
                    return {
                        "success": True,
                        "command": command.name,
                        "result": result
                    }
                except Exception as e:
                    logger.error(f"执行命令失败: {e}", exc_info=True)
                    return {
                        "success": False,
                        "error": str(e)
                    }
        
        return {"error": f"未知命令: {command_text.split()[0]}"}
    
    async def _handle_constitution(self, args: Dict, context: Dict) -> Dict:
        """处理 /constitution 命令"""
        project_id = context.get('project_id')
        if not project_id:
            return {"error": "需要项目ID"}
        
        # 如果提供了工作流，跳转到 constitution 阶段
        workflow_id = context.get('workflow_id')
        if workflow_id:
            try:
                from core.workflow_storage import get_workflow_storage
                storage = get_workflow_storage()
                workflow = storage.get_workflow(workflow_id)
                if workflow:
                    return {
                        "message": "跳转到创作原则阶段",
                        "workflow_id": workflow_id,
                        "project_id": project_id,
                        "stage": "constitution",
                        "workflow_status": workflow.get("status", "unknown")
                    }
            except Exception as e:
                logger.warning(f"获取工作流失败 {workflow_id}: {e}")
        
        return {
            "message": "创建创作原则",
            "project_id": project_id,
            "stage": "constitution"
        }
    
    async def _handle_specify(self, args: Dict, context: Dict) -> Dict:
        """处理 /specify 命令"""
        project_id = context.get('project_id')
        if not project_id:
            return {"error": "需要项目ID"}
        
        return {
            "message": "定义故事需求",
            "project_id": project_id,
            "stage": "specify"
        }
    
    async def _handle_clarify(self, args: Dict, context: Dict) -> Dict:
        """处理 /clarify 命令"""
        project_id = context.get('project_id')
        if not project_id:
            return {"error": "需要项目ID"}
        
        return {
            "message": "生成澄清问题",
            "project_id": project_id,
            "stage": "clarify"
        }
    
    async def _handle_plan(self, args: Dict, context: Dict) -> Dict:
        """处理 /plan 命令"""
        project_id = context.get('project_id')
        if not project_id:
            return {"error": "需要项目ID"}
        
        return {
            "message": "生成创作计划",
            "project_id": project_id,
            "stage": "plan"
        }
    
    async def _handle_tasks(self, args: Dict, context: Dict) -> Dict:
        """处理 /tasks 命令"""
        project_id = context.get('project_id')
        if not project_id:
            return {"error": "需要项目ID"}
        
        return {
            "message": "管理任务列表",
            "project_id": project_id,
            "stage": "tasks"
        }
    
    async def _handle_write(self, args: Dict, context: Dict) -> Dict:
        """处理 /write 命令"""
        project_id = context.get('project_id')
        if not project_id:
            return {"error": "需要项目ID"}
        
        return {
            "message": "开始写作",
            "project_id": project_id,
            "stage": "write"
        }
    
    async def _handle_analyze(self, args: Dict, context: Dict) -> Dict:
        """处理 /analyze 命令"""
        project_id = context.get('project_id')
        if not project_id:
            return {"error": "需要项目ID"}
        
        return {
            "message": "验证质量",
            "project_id": project_id,
            "stage": "analyze"
        }
    
    def list_commands(self) -> List[Dict]:
        """列出所有可用命令"""
        unique_commands = {}
        for name, command in self.commands.items():
            if command.name not in unique_commands:
                unique_commands[command.name] = command
        
        return [
            {
                "name": cmd.name,
                "description": cmd.description,
                "aliases": cmd.aliases
            }
            for cmd in unique_commands.values()
        ]
    
    def autocomplete(self, prefix: str) -> List[str]:
        """命令自动补全"""
        prefix = prefix.lower().lstrip('/')
        matches = []
        
        for name, command in self.commands.items():
            if name.startswith(prefix) or any(alias.startswith(prefix) for alias in command.aliases):
                matches.append(f"/{command.name}")
        
        return sorted(set(matches))


"""
API文档生成器
自动生成OpenAPI/Swagger文档
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import yaml
import logging

logger = logging.getLogger(__name__)


class APIDocGenerator:
    """API文档生成器"""
    
    def __init__(self):
        """初始化文档生成器"""
        self.openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Novel Corpus Extractor API",
                "version": "1.0.0",
                "description": "小说语料提取系统API文档",
                "contact": {
                    "name": "API Support"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:8000",
                    "description": "本地开发服务器"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {}
            },
            "tags": []
        }
    
    def add_endpoint(
        self,
        path: str,
        method: str,
        summary: str,
        description: str = "",
        tags: List[str] = None,
        parameters: List[Dict] = None,
        request_body: Dict = None,
        responses: Dict = None,
        security: List[Dict] = None
    ):
        """
        添加API端点文档
        
        Args:
            path: API路径
            method: HTTP方法（get, post, put, delete等）
            summary: 简短描述
            description: 详细描述
            tags: 标签列表
            parameters: 参数列表
            request_body: 请求体定义
            responses: 响应定义
            security: 安全要求
        """
        method = method.lower()
        
        if path not in self.openapi_spec["paths"]:
            self.openapi_spec["paths"][path] = {}
        
        endpoint_spec = {
            "summary": summary,
            "description": description,
            "operationId": f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}",
            "tags": tags or [],
            "responses": responses or {
                "200": {
                    "description": "成功响应",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object"
                            }
                        }
                    }
                },
                "400": {
                    "description": "请求错误"
                },
                "500": {
                    "description": "服务器错误"
                }
            }
        }
        
        if parameters:
            endpoint_spec["parameters"] = parameters
        
        if request_body:
            endpoint_spec["requestBody"] = request_body
        
        if security:
            endpoint_spec["security"] = security
        
        self.openapi_spec["paths"][path][method] = endpoint_spec
    
    def add_schema(self, name: str, schema: Dict[str, Any]):
        """
        添加数据模型定义
        
        Args:
            name: 模型名称
            schema: 模型定义
        """
        self.openapi_spec["components"]["schemas"][name] = schema
    
    def add_tag(self, name: str, description: str = ""):
        """
        添加标签
        
        Args:
            name: 标签名称
            description: 标签描述
        """
        tag = {"name": name}
        if description:
            tag["description"] = description
        
        # 检查是否已存在
        existing_tags = [t["name"] for t in self.openapi_spec["tags"]]
        if name not in existing_tags:
            self.openapi_spec["tags"].append(tag)
    
    def generate_openapi_json(self, output_path: Optional[str] = None) -> str:
        """
        生成OpenAPI JSON文档
        
        Args:
            output_path: 输出文件路径（可选）
        
        Returns:
            JSON字符串
        """
        json_str = json.dumps(self.openapi_spec, ensure_ascii=False, indent=2)
        
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_str)
            logger.info(f"OpenAPI JSON文档已保存到: {output_path}")
        
        return json_str
    
    def generate_openapi_yaml(self, output_path: Optional[str] = None) -> str:
        """
        生成OpenAPI YAML文档
        
        Args:
            output_path: 输出文件路径（可选）
        
        Returns:
            YAML字符串
        """
        yaml_str = yaml.dump(self.openapi_spec, allow_unicode=True, default_flow_style=False)
        
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(yaml_str)
            logger.info(f"OpenAPI YAML文档已保存到: {output_path}")
        
        return yaml_str
    
    def get_spec(self) -> Dict[str, Any]:
        """获取OpenAPI规范字典"""
        return self.openapi_spec.copy()


def generate_api_docs() -> Dict[str, Any]:
    """
    生成完整的API文档
    
    Returns:
        OpenAPI规范字典
    """
    generator = APIDocGenerator()
    
    # 添加标签
    generator.add_tag("Projects", "项目管理")
    generator.add_tag("Workflows", "工作流管理")
    generator.add_tag("Cards", "卡片管理")
    generator.add_tag("Commands", "斜杠命令")
    generator.add_tag("Health", "健康检查")
    
    # 添加数据模型
    generator.add_schema("Project", {
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "config": {"type": "object"},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"}
        }
    })
    
    generator.add_schema("Workflow", {
        "type": "object",
        "properties": {
            "workflow_id": {"type": "string", "format": "uuid"},
            "project_id": {"type": "string", "format": "uuid"},
            "status": {"type": "string", "enum": ["not_started", "in_progress", "paused", "completed", "cancelled"]},
            "current_stage": {"type": "string"},
            "stages": {"type": "array", "items": {"type": "object"}}
        }
    })
    
    generator.add_schema("Card", {
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "project_id": {"type": "string", "format": "uuid"},
            "type": {"type": "string"},
            "data": {"type": "object"},
            "parent_id": {"type": "string", "format": "uuid", "nullable": True},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"}
        }
    })
    
    # 添加API端点
    # 健康检查
    generator.add_endpoint(
        "/health",
        "get",
        "健康检查",
        "检查API服务器状态",
        tags=["Health"]
    )
    
    # 项目管理
    generator.add_endpoint(
        "/api/projects",
        "get",
        "列出所有项目",
        "获取所有项目的列表",
        tags=["Projects"],
        responses={
            "200": {
                "description": "项目列表",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Project"}
                        }
                    }
                }
            }
        }
    )
    
    generator.add_endpoint(
        "/api/projects",
        "post",
        "创建项目",
        "创建新项目",
        tags=["Projects"],
        request_body={
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "template_id": {"type": "string"}
                        }
                    }
                }
            }
        },
        responses={
            "200": {
                "description": "创建的项目",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Project"}
                    }
                }
            }
        }
    )
    
    generator.add_endpoint(
        "/api/projects/{project_id}",
        "get",
        "获取项目",
        "根据ID获取项目详情",
        tags=["Projects"],
        parameters=[
            {
                "name": "project_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"}
            }
        ],
        responses={
            "200": {
                "description": "项目详情",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Project"}
                    }
                }
            }
        }
    )
    
    # 工作流管理
    generator.add_endpoint(
        "/api/workflows",
        "post",
        "创建工作流",
        "创建新的工作流实例",
        tags=["Workflows"],
        request_body={
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["project_id", "workflow_type"],
                        "properties": {
                            "project_id": {"type": "string", "format": "uuid"},
                            "workflow_type": {"type": "string", "enum": ["seven_step", "creative"]}
                        }
                    }
                }
            }
        },
        responses={
            "200": {
                "description": "创建的工作流",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Workflow"}
                    }
                }
            }
        }
    )
    
    generator.add_endpoint(
        "/api/workflows/{workflow_id}",
        "get",
        "获取工作流",
        "根据ID获取工作流详情",
        tags=["Workflows"],
        parameters=[
            {
                "name": "workflow_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"}
            }
        ],
        responses={
            "200": {
                "description": "工作流详情",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Workflow"}
                    }
                }
            }
        }
    )
    
    # 卡片管理
    generator.add_endpoint(
        "/api/projects/{project_id}/cards",
        "get",
        "列出项目卡片",
        "获取项目的所有卡片",
        tags=["Cards"],
        parameters=[
            {
                "name": "project_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"}
            }
        ],
        responses={
            "200": {
                "description": "卡片列表",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Card"}
                        }
                    }
                }
            }
        }
    )
    
    generator.add_endpoint(
        "/api/projects/{project_id}/cards",
        "post",
        "创建卡片",
        "在项目中创建新卡片",
        tags=["Cards"],
        parameters=[
            {
                "name": "project_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"}
            }
        ],
        request_body={
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["type", "data"],
                        "properties": {
                            "type": {"type": "string"},
                            "data": {"type": "object"},
                            "parent_id": {"type": "string", "format": "uuid"}
                        }
                    }
                }
            }
        },
        responses={
            "200": {
                "description": "创建的卡片",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Card"}
                    }
                }
            }
        }
    )
    
    # 斜杠命令
    generator.add_endpoint(
        "/api/commands",
        "post",
        "执行斜杠命令",
        "执行斜杠命令并返回结果",
        tags=["Commands"],
        request_body={
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["command"],
                        "properties": {
                            "command": {"type": "string"},
                            "context": {"type": "object"}
                        }
                    }
                }
            }
        },
        responses={
            "200": {
                "description": "命令执行结果",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "result": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }
    )
    
    return generator.get_spec()


def save_api_docs(output_dir: str = "docs"):
    """
    保存API文档到文件
    
    Args:
        output_dir: 输出目录
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    spec = generate_api_docs()
    generator = APIDocGenerator()
    generator.openapi_spec = spec
    
    # 保存JSON格式
    generator.generate_openapi_json(str(output_path / "openapi.json"))
    
    # 保存YAML格式
    generator.generate_openapi_yaml(str(output_path / "openapi.yaml"))
    
    logger.info(f"API文档已保存到: {output_dir}")



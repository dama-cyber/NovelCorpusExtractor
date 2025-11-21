"""
FastAPI Web服务器
提供RESTful API接口，供前端调用小说语料提取功能
"""

import asyncio
import json
import logging
import os
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from main import NovelCorpusExtractor
from core.card_manager import CardManager
from core.project_manager import ProjectManager
from core.workflows import WorkflowFactory
from core.agent_skills import AgentSkillsManager
from core.slash_commands import SlashCommandProcessor
from core.rate_limiter import get_rate_limiter
from core.workflow_storage import get_workflow_storage
from core.performance_monitor import get_performance_monitor
from core.data_exporter import DataExporter, create_exporter
from core.exceptions import (
    NovelExtractorError,
    ConfigurationError,
    APIError,
    ValidationError,
    FileProcessingError,
    WorkflowError
)
from core.error_handler import error_handler, global_exception_handler

# 配置日志
def setup_api_logging():
    """设置API服务器日志"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('api_server.log', encoding='utf-8')
        ]
    )

setup_api_logging()
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="NovelCorpusExtractor API",
    description="小说语料提取系统API服务",
    version="1.0.0"
)

# 注册全局异常处理器
app.add_exception_handler(Exception, global_exception_handler)

# 配置CORS
# 从环境变量读取允许的来源，默认允许所有（开发环境）
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局提取器实例
extractor: Optional[NovelCorpusExtractor] = None


def get_extractor() -> NovelCorpusExtractor:
    """获取或创建提取器实例"""
    global extractor
    if extractor is None:
        config_path = os.getenv("CONFIG_PATH", "config.yaml")
        extractor = NovelCorpusExtractor(config_path)
    return extractor


class ProcessResponse(BaseModel):
    """处理响应模型"""
    chunkResults: List[Dict]
    workflowStages: Optional[Dict[str, Dict]] = None
    workflow: Optional[Dict] = None
    outline: Optional[str] = None
    memories: Optional[List[Dict]] = None
    creative: Optional[Dict] = None
    emittedAt: Optional[str] = None


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "NovelCorpusExtractor API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """
    健康检查接口
    返回系统健康状态和详细信息
    """
    from core.cache_manager import get_cache_manager
    from core.rate_limiter import get_rate_limiter
    from core.workflow_storage import get_workflow_storage
    import datetime
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "components": {}
    }
    
    try:
        monitor = get_performance_monitor()
        with monitor.timer("health_check"):
            # 检查提取器
            try:
                extractor = get_extractor()
                health_status["components"]["extractor"] = {
                    "status": "ok",
                    "initialized": extractor is not None
                }
            except Exception as e:
                health_status["components"]["extractor"] = {
                    "status": "error",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            # 检查缓存管理器
            try:
                cache_manager = get_cache_manager()
                cache_stats = cache_manager.get_stats()
                health_status["components"]["cache"] = {
                    "status": "ok",
                    "stats": cache_stats
                }
            except Exception as e:
                health_status["components"]["cache"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            # 检查限流器
            try:
                rate_limiter = get_rate_limiter()
                health_status["components"]["rate_limiter"] = {
                    "status": "ok",
                    "enabled": rate_limiter is not None
                }
            except Exception as e:
                health_status["components"]["rate_limiter"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            # 检查工作流存储
            try:
                workflow_storage = get_workflow_storage()
                health_status["components"]["workflow_storage"] = {
                    "status": "ok"
                }
            except Exception as e:
                health_status["components"]["workflow_storage"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            # 性能摘要
            summary = monitor.get_summary()
            health_status["performance"] = summary
            
            # 如果任何关键组件失败，标记为不健康
            critical_components = ["extractor"]
            for component in critical_components:
                if health_status["components"].get(component, {}).get("status") != "ok":
                    health_status["status"] = "unhealthy"
                    break
            
    except Exception as e:
        logger.error(f"健康检查失败: {e}", exc_info=True)
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    # 根据状态返回相应的HTTP状态码
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


# 文件大小限制（默认 50MB）
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", 10 * 1024 * 1024))  # 10MB 文本

# 限流配置
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))  # 每分钟最大请求数
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # 时间窗口（秒）

# 初始化限流器
rate_limiter = get_rate_limiter() if RATE_LIMIT_ENABLED else None


def check_rate_limit(request, endpoint: str):
    """检查限流（中间件函数）"""
    if not rate_limiter:
        return None
    
    # 获取客户端标识（IP地址或用户ID）
    client_ip = request.client.host if hasattr(request, 'client') else "unknown"
    is_allowed, remaining = rate_limiter.check_rate_limit(
        endpoint=endpoint,
        key=client_ip,
        max_requests=RATE_LIMIT_REQUESTS,
        time_window=RATE_LIMIT_WINDOW
    )
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail=f"请求过于频繁，请稍后再试。剩余请求数: {remaining}",
            headers={"X-RateLimit-Remaining": str(remaining)}
        )
    
    return remaining


@app.post("/api/process")
async def process_novel(
    request: Request,
    file: Optional[UploadFile] = File(None),
    novel_type: str = Form("通用"),
    topology_mode: str = Form("auto"),
    api_pool_mode: str = Form("auto"),
    sample_text: Optional[str] = Form(None),
    workflow_targets: str = Form("[]"),
    run_creative_flow: str = Form("false")
):
    """
    处理小说文件或文本
    
    参数:
    - file: 上传的小说文件（可选，最大 50MB）
    - novel_type: 小说类型
    - topology_mode: 拓扑模式 (auto/linear/triangular/swarm)
    - api_pool_mode: API池模式 (auto/single/triple/swarm)
    - sample_text: 示例文本（可选，当没有文件时使用，最大 10MB）
    - workflow_targets: 工作流目标列表（JSON字符串）
    - run_creative_flow: 是否运行创作流程（字符串 "true"/"false"）
    """
    # 检查限流
    try:
        check_rate_limit(request, "/api/process")
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"限流检查失败: {e}")
    
    temp_dir = None
    input_file_path = None
    
    try:
        # 解析工作流目标
        try:
            targets = json.loads(workflow_targets) if workflow_targets else []
        except json.JSONDecodeError:
            targets = []
            logger.warning(f"无法解析工作流目标: {workflow_targets}")
        
        run_creative = run_creative_flow.lower() == "true"
        
        # 获取提取器实例
        extractor = get_extractor()
        
        # 更新拓扑模式（如果指定）
        if topology_mode != "auto":
            from core.topology_manager import TopologyMode
            try:
                mode = TopologyMode(topology_mode)
                extractor.topology_manager.mode = mode
                logger.info(f"设置拓扑模式为: {topology_mode}")
            except ValueError:
                logger.warning(f"无效的拓扑模式: {topology_mode}，使用默认模式")
        
        # 准备输入文件
        if file and file.filename:
            # 检查文件大小
            if file.size and file.size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"文件大小超过限制 ({MAX_FILE_SIZE / 1024 / 1024:.1f}MB)"
                )
            
            # 保存上传的文件到临时目录
            temp_dir = tempfile.mkdtemp(prefix="novel_extractor_")
            input_file_path = os.path.join(temp_dir, file.filename)
            
            # 读取文件内容（限制大小）
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"文件大小超过限制 ({MAX_FILE_SIZE / 1024 / 1024:.1f}MB)"
                )
            
            with open(input_file_path, "wb") as f:
                f.write(content)
            
            logger.info(f"已保存上传文件: {input_file_path} ({len(content)} 字节)")
        
        elif sample_text:
            # 检查文本长度
            if len(sample_text) > MAX_TEXT_LENGTH:
                raise HTTPException(
                    status_code=413,
                    detail=f"文本长度超过限制 ({MAX_TEXT_LENGTH / 1024 / 1024:.1f}MB)"
                )
            
            # 使用示例文本创建临时文件
            temp_dir = tempfile.mkdtemp(prefix="novel_extractor_")
            input_file_path = os.path.join(temp_dir, "sample_text.txt")
            
            with open(input_file_path, "w", encoding="utf-8") as f:
                f.write(sample_text)
            
            logger.info(f"已创建临时文件: {input_file_path} ({len(sample_text)} 字符)")
        
        else:
            raise HTTPException(
                status_code=400,
                detail="必须提供文件或示例文本"
            )
        
        # 验证文件存在且可读
        if not os.path.exists(input_file_path):
            raise HTTPException(
                status_code=500,
                detail="临时文件创建失败"
            )
        
        # 生成工作流ID
        workflow_id = str(uuid.uuid4())
        logger.info(f"创建工作流: {workflow_id}")
        
        # 保存工作流初始状态
        try:
            storage = get_workflow_storage()
            storage.save_workflow(workflow_id, {
                "id": workflow_id,
                "project_id": None,  # process端点不关联特定项目
                "status": "in_progress",
                "type": "novel_processing",
                "novel_type": novel_type,
                "topology_mode": topology_mode,
                "api_pool_mode": api_pool_mode,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "stages": [],
                "current_stage": None
            })
        except Exception as e:
            logger.warning(f"保存工作流状态失败: {e}")
        
        # 处理小说
        logger.info(f"开始处理小说，类型: {novel_type}, 拓扑模式: {topology_mode}, 工作流ID: {workflow_id}")
        
        results = await extractor.process_novel(input_file_path, novel_type)
        
        # 格式化响应数据
        chunk_results = []
        for result in results.get("chunk_results", []):
            chunk_results.append({
                "chunkId": result.get("chunk_id", ""),
                "title": result.get("title"),
                "summary": result.get("summary", ""),
                "tokens": result.get("tokens"),
                "themes": result.get("themes", []),
                "hookScore": result.get("hook_score")
            })
        
        # 提取大纲
        outline = results.get("outline", "")
        if isinstance(outline, dict):
            outline = json.dumps(outline, ensure_ascii=False, indent=2)
        
        # 提取工作流信息
        workflow_summary = results.get("workflow", {})
        workflow_stages = {}
        
        # 提取记忆体信息
        memories = []
        memory_dir = extractor.memory_manager.output_dir
        if memory_dir.exists():
            # 读取世界观记忆体
            worldview_file = memory_dir / "worldview_memory.yaml"
            if worldview_file.exists():
                memories.append({
                    "id": "worldview",
                    "title": "世界观记忆体",
                    "entries": [str(worldview_file)]
                })
            
            # 读取人物记忆体
            character_file = memory_dir / "character_memory.yaml"
            if character_file.exists():
                memories.append({
                    "id": "character",
                    "title": "人物记忆体",
                    "entries": [str(character_file)]
                })
        
        # 构建创作输出（从工作流结果中提取）
        creative_outputs = {}
        if workflow_summary:
            creation_flow = workflow_summary.get("creationFlow", {})
            optimization_flow = workflow_summary.get("optimizationFlow", {})
            detection_flow = workflow_summary.get("detectionFlow", {})
            
            # 提取各种创作工具的输出
            if creation_flow:
                creative_outputs.update(creation_flow)
            if optimization_flow:
                creative_outputs.update(optimization_flow)
            if detection_flow:
                creative_outputs.update(detection_flow)
        
        # 更新工作流状态为完成
        try:
            storage = get_workflow_storage()
            workflow_data = storage.get_workflow(workflow_id)
            if workflow_data:
                workflow_data["status"] = "completed"
                workflow_data["updated_at"] = datetime.now().isoformat()
                workflow_data["chunk_count"] = len(chunk_results)
                storage.save_workflow(workflow_id, workflow_data)
        except Exception as e:
            logger.warning(f"更新工作流状态失败: {e}")
        
        response_data = {
            "workflowId": workflow_id,  # 添加工作流ID
            "chunkResults": chunk_results,
            "workflowStages": workflow_stages,
            "workflow": workflow_summary,
            "outline": outline,
            "memories": memories,
            "creative": creative_outputs if creative_outputs else None,
            "emittedAt": datetime.now().isoformat(),  # 添加时间戳
            "outputDir": str(extractor.memory_manager.output_dir)  # 添加输出目录
        }
        
        logger.info(f"处理完成，共 {len(chunk_results)} 个文本块，工作流ID: {workflow_id}")
        
        return JSONResponse(content=response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        # 更新工作流状态为失败（如果工作流ID已创建）
        if 'workflow_id' in locals():
            try:
                storage = get_workflow_storage()
                workflow_data = storage.get_workflow(workflow_id)
                if workflow_data:
                    workflow_data["status"] = "failed"
                    workflow_data["error"] = str(e)
                    workflow_data["updated_at"] = datetime.now().isoformat()
                    storage.save_workflow(workflow_id, workflow_data)
            except Exception as storage_error:
                logger.warning(f"更新工作流失败状态失败: {storage_error}")
        raise HTTPException(
            status_code=500,
            detail=f"处理失败: {str(e)}"
        )
    finally:
        # 确保清理临时文件和目录
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"已清理临时目录: {temp_dir}")
            except Exception as e:
                logger.warning(f"清理临时目录失败: {e}")


@app.get("/api/config")
async def get_config():
    """获取当前配置信息"""
    try:
        import yaml
        config_path = os.getenv("CONFIG_PATH", "config.yaml")
        
        # 读取配置文件
        config_data = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
        
        # 获取模型配置（隐藏敏感信息）
        model_config = config_data.get("model", {})
        api_pool_config = config_data.get("api_pool", {})
        
        # 检查 API 密钥是否配置（不返回实际密钥）
        api_key_configured = bool(
            model_config.get("api_key") or 
            os.getenv("OPENAI_API_KEY") or 
            os.getenv("GEMINI_API_KEY") or
            os.getenv("DEEPSEEK_API_KEY")
        )
        
        # 检查 API 池配置
        api_pool_enabled = api_pool_config.get("enabled", False)
        api_pool_apis = api_pool_config.get("apis", [])
        enabled_apis = [api for api in api_pool_apis if api.get("enabled", False)]
        
        try:
            extractor = get_extractor()
            llm_client = get_llm_client()
            
            # 检查 API 配置状态
            api_status = "configured" if api_key_configured else "not_configured"
            if hasattr(llm_client, 'api_pool'):
                api_status = f"api_pool_mode_{len(llm_client.api_pool.apis)}_apis"
            elif hasattr(llm_client, 'model'):
                api_status = f"single_api_mode_{llm_client.model}"
        except:
            api_status = "not_configured"
        
        return {
            "topology_mode": config_data.get("topology", {}).get("mode", "auto"),
            "output_dir": config_data.get("output_dir", "output"),
            "corpus_dir": config_data.get("corpus_dir", "corpus_samples"),
            "api_mode": "api_only",  # 明确标识只使用 API
            "api_status": api_status,
            "model": {
                "provider": model_config.get("model", ""),
                "model_name": model_config.get("model_name", ""),
                "api_key_configured": api_key_configured,
                "base_url": model_config.get("base_url", "")
            },
            "api_pool": {
                "enabled": api_pool_enabled,
                "total_apis": len(api_pool_apis),
                "enabled_apis": len(enabled_apis),
                "providers": [api.get("provider") for api in enabled_apis]
            }
        }
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config")
async def update_config(config: Dict):
    """更新配置信息（仅更新非敏感配置）"""
    try:
        import yaml
        config_path = os.getenv("CONFIG_PATH", "config.yaml")
        
        # 读取现有配置
        config_data = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
        
        # 更新配置（不允许更新 API 密钥等敏感信息）
        if "topology" in config:
            if "topology" not in config_data:
                config_data["topology"] = {}
            config_data["topology"]["mode"] = config["topology"].get("mode")
        
        if "output_dir" in config:
            config_data["output_dir"] = config["output_dir"]
        
        if "corpus_dir" in config:
            config_data["corpus_dir"] = config["corpus_dir"]
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)
        
        # 重新加载提取器
        global extractor
        extractor = None
        
        return {"status": "success", "message": "配置已更新"}
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 初始化管理器（单例模式）
_card_manager = None
_project_manager = None
_skills_manager = None
_command_processor = None

def get_card_manager() -> CardManager:
    """获取卡片管理器实例"""
    global _card_manager
    if _card_manager is None:
        _card_manager = CardManager()
    return _card_manager

def get_project_manager() -> ProjectManager:
    """获取项目管理器实例"""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager

def get_skills_manager() -> AgentSkillsManager:
    """获取技能管理器实例"""
    global _skills_manager
    if _skills_manager is None:
        _skills_manager = AgentSkillsManager()
    return _skills_manager

def get_llm_client():
    """获取 LLM 客户端实例（从 extractor 获取）"""
    extractor = get_extractor()
    if extractor and hasattr(extractor, 'llm_client'):
        return extractor.llm_client
    raise HTTPException(
        status_code=500,
        detail="LLM 客户端未初始化，请检查配置文件中的 API 设置"
    )

def get_command_processor() -> SlashCommandProcessor:
    """获取命令处理器实例"""
    global _command_processor
    if _command_processor is None:
        llm_client = get_llm_client()
        _command_processor = SlashCommandProcessor(
            card_manager=get_card_manager(),
            project_manager=get_project_manager(),
            llm_client=llm_client
        )
    return _command_processor


# ==================== 新增 API 端点 ====================

@app.post("/api/projects")
async def create_project(name: str, description: str = ""):
    """创建新项目"""
    try:
        project_manager = get_project_manager()
        project = project_manager.create_project(name, description)
        return project
    except Exception as e:
        logger.error(f"创建项目失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects")
async def list_projects():
    """列出所有项目"""
    try:
        project_manager = get_project_manager()
        projects = project_manager.list_projects()
        return {"projects": projects}
    except Exception as e:
        logger.error(f"列出项目失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """获取项目详情"""
    try:
        project_manager = get_project_manager()
        project = project_manager.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cards")
async def create_card(project_id: str, card_type: str, data: Dict, parent_id: Optional[str] = None):
    """创建卡片"""
    try:
        card_manager = get_card_manager()
        card = card_manager.create_card(project_id, card_type, data, parent_id)
        return card
    except Exception as e:
        logger.error(f"创建卡片失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cards/{card_id}")
async def get_card(card_id: str):
    """获取卡片"""
    try:
        card_manager = get_card_manager()
        card = card_manager.get_card(card_id)
        if not card:
            raise HTTPException(status_code=404, detail="卡片不存在")
        return card
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取卡片失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows/list")
async def list_workflows():
    """列出所有可用工作流"""
    try:
        workflows = WorkflowFactory.list_workflows()
        return {"workflows": workflows}
    except Exception as e:
        logger.error(f"列出工作流失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/start")
async def start_workflow(workflow_type: str, project_id: str, initial_data: Optional[Dict] = None):
    """启动工作流"""
    try:
        card_manager = get_card_manager()
        llm_client = get_llm_client()
        
        workflow = WorkflowFactory.create_workflow(
            workflow_type=workflow_type,
            project_id=project_id,
            card_manager=card_manager,
            llm_client=llm_client
        )
        
        result = await workflow.start(initial_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动工作流失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"启动工作流失败: {str(e)}")

@app.get("/api/skills")
async def list_skills(level: Optional[str] = None, tags: Optional[List[str]] = None):
    """列出所有技能"""
    try:
        skills_manager = get_skills_manager()
        from core.agent_skills import SkillLevel
        
        skill_level = None
        if level:
            skill_level = SkillLevel(level)
        
        skills = skills_manager.list_skills(level=skill_level, tags=tags)
        return {"skills": [s.to_dict() for s in skills]}
    except Exception as e:
        logger.error(f"列出技能失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/commands/execute")
async def execute_command(command: str, project_id: str):
    """执行斜杠命令"""
    try:
        command_processor = get_command_processor()
        context = {"project_id": project_id}
        result = await command_processor.process(command, context)
        return result
    except Exception as e:
        logger.error(f"执行命令失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/commands/list")
async def list_commands():
    """列出所有可用命令"""
    try:
        command_processor = get_command_processor()
        commands = command_processor.list_commands()
        return {"commands": commands}
    except Exception as e:
        logger.error(f"列出命令失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    try:
        extractor = get_extractor()
        llm_client = get_llm_client()
        
        # 检查 LLM 客户端是否可用
        llm_status = "available" if llm_client else "unavailable"
        
        return {
            "status": "healthy",
            "llm_client": llm_status,
            "extractor": "available" if extractor else "unavailable",
            "api_mode": "api_only"  # 明确标识只使用 API
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/api/workflows/{workflow_id}/progress")
async def get_workflow_progress(workflow_id: str):
    """获取工作流进度"""
    try:
        storage = get_workflow_storage()
        workflow = storage.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="工作流不存在")
        return {
            "workflow_id": workflow_id,
            "status": workflow.get("status", "unknown"),
            "progress": workflow.get("progress", {}),
            "current_stage": workflow.get("current_stage"),
            "updated_at": workflow.get("updated_at")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取工作流进度失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflows/{workflow_id}/details")
async def get_workflow_details(workflow_id: str):
    """获取工作流详细信息"""
    try:
        storage = get_workflow_storage()
        workflow = storage.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="工作流不存在")
        
        # 返回完整的工作流信息
        return {
            "workflow_id": workflow_id,
            "status": workflow.get("status", "unknown"),
            "progress": workflow.get("progress", {}),
            "current_stage": workflow.get("current_stage"),
            "stages": workflow.get("stages", {}),
            "created_at": workflow.get("created_at"),
            "updated_at": workflow.get("updated_at"),
            "chunk_count": workflow.get("chunk_count"),
            "error": workflow.get("error"),
            "workflow_summary": workflow.get("workflow"),
            "output_dir": workflow.get("output_dir")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取工作流详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflows/{workflow_id}/stream")
async def stream_workflow_progress(workflow_id: str):
    """通过SSE流式推送工作流进度更新"""
    async def event_generator():
        """生成SSE事件"""
        storage = get_workflow_storage()
        last_updated = None
        max_attempts = 3600  # 最多轮询1小时（假设每1秒一次）
        attempts = 0
        
        try:
            while attempts < max_attempts:
                # 检查工作流是否存在
                workflow = storage.get_workflow(workflow_id)
                if not workflow:
                    # 工作流不存在，发送错误并结束
                    yield f"data: {json.dumps({'error': '工作流不存在'})}\n\n"
                    break
                
                # 获取当前状态
                status = workflow.get("status", "unknown")
                current_updated = workflow.get("updated_at")
                
                # 如果状态有更新，发送事件
                if current_updated != last_updated:
                    progress_data = {
                        "workflow_id": workflow_id,
                        "status": status,
                        "progress": workflow.get("progress", {}),
                        "current_stage": workflow.get("current_stage"),
                        "updated_at": current_updated
                    }
                    yield f"data: {json.dumps(progress_data)}\n\n"
                    last_updated = current_updated
                    
                    # 如果工作流已完成或失败，结束流
                    if status in ["completed", "failed"]:
                        yield f"event: close\ndata: {json.dumps({'status': status})}\n\n"
                        break
                
                # 等待1秒后再次检查
                await asyncio.sleep(1)
                attempts += 1
                
                # 发送心跳（每10秒一次）
                if attempts % 10 == 0:
                    yield f": heartbeat\n\n"
            
            # 如果达到最大尝试次数，发送超时消息
            if attempts >= max_attempts:
                yield f"data: {json.dumps({'error': '轮询超时'})}\n\n"
                
        except asyncio.CancelledError:
            logger.info(f"SSE连接已取消: {workflow_id}")
            raise
        except Exception as e:
            logger.error(f"SSE流错误 {workflow_id}: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
        }
    )


# 批量处理相关端点
batch_processor = None

def get_batch_processor():
    """获取或创建批量处理器"""
    global batch_processor
    if batch_processor is None:
        from core.batch_processor import BatchProcessor
        extractor = get_extractor()
        batch_processor = BatchProcessor(extractor)
    return batch_processor


@app.post("/api/batch/create")
async def create_batch(
    file_paths: List[str],
    novel_type: str = "通用",
    topology_mode: str = "auto",
    api_pool_mode: str = "auto",
    workflow_targets: Optional[List[str]] = None,
    run_creative_flow: bool = False
):
    """创建批量处理任务"""
    try:
        processor = get_batch_processor()
        batch_result = processor.create_batch(
            file_paths=file_paths,
            novel_type=novel_type,
            topology_mode=topology_mode,
            api_pool_mode=api_pool_mode,
            workflow_targets=workflow_targets,
            run_creative_flow=run_creative_flow
        )
        return {
            "batch_id": batch_result.batch_id,
            "total_jobs": batch_result.total_jobs,
            "status": batch_result.status
        }
    except Exception as e:
        logger.error(f"创建批量任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/{batch_id}/start")
async def start_batch(batch_id: str):
    """启动批量处理"""
    try:
        processor = get_batch_processor()
        batch_result = processor.get_batch(batch_id)
        if not batch_result:
            raise HTTPException(status_code=404, detail="批量任务不存在")
        
        # 在后台启动处理
        asyncio.create_task(processor.process_batch(batch_id))
        
        return {
            "batch_id": batch_id,
            "status": "started",
            "message": "批量处理已启动"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动批量处理失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/{batch_id}")
async def get_batch_status(batch_id: str):
    """获取批量任务状态"""
    try:
        processor = get_batch_processor()
        batch_result = processor.get_batch(batch_id)
        if not batch_result:
            raise HTTPException(status_code=404, detail="批量任务不存在")
        
        return {
            "batch_id": batch_result.batch_id,
            "total_jobs": batch_result.total_jobs,
            "completed_jobs": batch_result.completed_jobs,
            "failed_jobs": batch_result.failed_jobs,
            "progress_percentage": batch_result.progress_percentage,
            "success_rate": batch_result.success_rate,
            "status": batch_result.status,
            "created_at": batch_result.created_at,
            "completed_at": batch_result.completed_at,
            "jobs": [
                {
                    "job_id": job.job_id,
                    "file_path": job.file_path,
                    "status": job.status,
                    "error": job.error
                }
                for job in batch_result.jobs
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取批量任务状态失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch")
async def list_batches():
    """列出所有批量任务"""
    try:
        processor = get_batch_processor()
        batches = processor.list_batches()
        return {
            "batches": [
                {
                    "batch_id": batch.batch_id,
                    "total_jobs": batch.total_jobs,
                    "completed_jobs": batch.completed_jobs,
                    "failed_jobs": batch.failed_jobs,
                    "progress_percentage": batch.progress_percentage,
                    "status": batch.status,
                    "created_at": batch.created_at
                }
                for batch in batches
            ]
        }
    except Exception as e:
        logger.error(f"列出批量任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/{batch_id}/cancel")
async def cancel_batch(batch_id: str):
    """取消批量任务"""
    try:
        processor = get_batch_processor()
        success = processor.cancel_batch(batch_id)
        if not success:
            raise HTTPException(status_code=404, detail="批量任务不存在或无法取消")
        return {
            "batch_id": batch_id,
            "status": "cancelled"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消批量任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 数据导出端点 ====================

@app.post("/api/export")
async def export_data(
    output_dir: str = Form(...),
    format: str = Form("all"),
    export_dir: Optional[str] = Form(None)
):
    """
    导出处理结果
    
    参数:
    - output_dir: 包含处理结果的输出目录
    - format: 导出格式 (json, csv, excel, markdown, html, all)
    - export_dir: 导出文件保存目录（可选）
    """
    try:
        output_path = Path(output_dir)
        if not output_path.exists():
            raise HTTPException(status_code=404, detail=f"输出目录不存在: {output_dir}")
        
        # 创建临时提取器以访问memory_manager
        extractor = get_extractor()
        extractor.memory_manager.output_dir = output_path
        
        # 确定导出目录
        if export_dir:
            export_path = Path(export_dir)
        else:
            export_path = output_path / "exports"
        
        export_path.mkdir(parents=True, exist_ok=True)
        
        # 创建导出器
        exporter = create_exporter(export_path)
        
        # 加载已有数据
        chunk_results = []
        outline = None
        workflow_summary = None
        
        # 尝试从结果文件加载（如果有）
        result_files = list(output_path.glob("*_result.json"))
        if result_files:
            # 从最新的结果文件加载
            latest_file = max(result_files, key=lambda p: p.stat().st_mtime)
            with open(latest_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
                chunk_results = result_data.get('chunkResults', result_data.get('chunk_results', []))
                outline = result_data.get('outline')
                workflow_summary = result_data.get('workflow')
        
        # 生成基础文件名
        base_filename = f"export_{output_path.name}"
        
        # 根据格式导出
        exported_files = {}
        
        if format.lower() == "all":
            exported_files = exporter.export_from_memory_manager(
                extractor.memory_manager,
                chunk_results=chunk_results if chunk_results else None,
                outline=outline,
                workflow_summary=workflow_summary,
                base_filename=base_filename
            )
        elif format.lower() == "json":
            data = {}
            if chunk_results:
                data['chunkResults'] = chunk_results
            if outline:
                data['outline'] = outline
            if workflow_summary:
                data['workflow'] = workflow_summary
            exported_files['json'] = exporter.export_json(data, base_filename)
        elif format.lower() == "csv":
            if chunk_results:
                exported_files['csv'] = exporter.export_csv(chunk_results, base_filename)
            else:
                raise HTTPException(status_code=400, detail="没有文本块结果可导出为CSV")
        elif format.lower() == "excel":
            if chunk_results:
                excel_data = {'文本块结果': chunk_results}
                exported_files['excel'] = exporter.export_excel(excel_data, base_filename)
            else:
                raise HTTPException(status_code=400, detail="没有数据可导出为Excel")
        elif format.lower() == "markdown":
            data = {}
            if chunk_results:
                data['chunkResults'] = chunk_results
            if outline:
                data['outline'] = outline
            if workflow_summary:
                data['workflow'] = workflow_summary
            exported_files['markdown'] = exporter.export_markdown(data, base_filename)
        elif format.lower() == "html":
            data = {}
            if chunk_results:
                data['chunkResults'] = chunk_results
            if outline:
                data['outline'] = outline
            if workflow_summary:
                data['workflow'] = workflow_summary
            exported_files['html'] = exporter.export_html(data, base_filename)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的导出格式: {format}")
        
        return {
            "status": "success",
            "export_dir": str(export_path),
            "exported_files": {fmt: str(path) for fmt, path in exported_files.items()}
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@app.get("/api/export/formats")
async def list_export_formats():
    """列出所有支持的导出格式"""
    return {
        "formats": [
            {
                "name": "json",
                "description": "JSON格式，包含完整数据",
                "supports": ["all"]
            },
            {
                "name": "csv",
                "description": "CSV格式，适合表格数据",
                "supports": ["chunk_results"]
            },
            {
                "name": "excel",
                "description": "Excel格式，多工作表",
                "supports": ["chunk_results", "memories"]
            },
            {
                "name": "markdown",
                "description": "Markdown格式，可读性好",
                "supports": ["all"]
            },
            {
                "name": "html",
                "description": "HTML格式，可在浏览器中查看",
                "supports": ["all"]
            },
            {
                "name": "all",
                "description": "导出所有格式",
                "supports": ["all"]
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"启动API服务器: http://{host}:{port}")
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )


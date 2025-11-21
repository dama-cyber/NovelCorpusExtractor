"""
批量处理模块
支持批量处理多个文件
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import json

from core.exceptions import FileProcessingError, ValidationError
from core.utils import ensure_dir

logger = logging.getLogger(__name__)


@dataclass
class BatchJob:
    """批量任务"""
    job_id: str
    file_path: str
    novel_type: str = "通用"
    topology_mode: str = "auto"
    api_pool_mode: str = "auto"
    workflow_targets: List[str] = field(default_factory=list)
    run_creative_flow: bool = False
    status: str = "pending"  # pending, processing, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


@dataclass
class BatchResult:
    """批量处理结果"""
    batch_id: str
    total_jobs: int
    completed_jobs: int = 0
    failed_jobs: int = 0
    jobs: List[BatchJob] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    status: str = "running"  # running, completed, failed, cancelled
    
    @property
    def progress_percentage(self) -> float:
        """计算进度百分比"""
        if self.total_jobs == 0:
            return 0.0
        return (self.completed_jobs + self.failed_jobs) / self.total_jobs * 100
    
    @property
    def success_rate(self) -> float:
        """计算成功率"""
        if self.completed_jobs == 0:
            return 0.0
        return self.completed_jobs / (self.completed_jobs + self.failed_jobs) * 100


class BatchProcessor:
    """批量处理器"""
    
    def __init__(
        self,
        extractor,
        max_concurrent: int = 3,
        output_dir: Optional[Path] = None
    ):
        """
        初始化批量处理器
        
        Args:
            extractor: 小说提取器实例
            max_concurrent: 最大并发数
            output_dir: 输出目录
        """
        self.extractor = extractor
        self.max_concurrent = max_concurrent
        self.output_dir = output_dir or Path("batch_outputs")
        ensure_dir(self.output_dir)
        
        self.active_batches: Dict[str, BatchResult] = {}
    
    def create_batch(
        self,
        file_paths: List[Union[str, Path]],
        novel_type: str = "通用",
        topology_mode: str = "auto",
        api_pool_mode: str = "auto",
        workflow_targets: Optional[List[str]] = None,
        run_creative_flow: bool = False
    ) -> BatchResult:
        """
        创建批量任务
        
        Args:
            file_paths: 文件路径列表
            novel_type: 小说类型
            topology_mode: 拓扑模式
            api_pool_mode: API池模式
            workflow_targets: 工作流目标列表
            run_creative_flow: 是否运行创作流程
        
        Returns:
            BatchResult: 批量任务结果
        """
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        jobs = []
        for file_path in file_paths:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.warning(f"文件不存在，跳过: {file_path}")
                continue
            
            job = BatchJob(
                job_id=f"{batch_id}_job_{len(jobs)}",
                file_path=str(file_path),
                novel_type=novel_type,
                topology_mode=topology_mode,
                api_pool_mode=api_pool_mode,
                workflow_targets=workflow_targets or [],
                run_creative_flow=run_creative_flow
            )
            jobs.append(job)
        
        if not jobs:
            raise ValidationError("没有有效的文件可以处理")
        
        batch_result = BatchResult(
            batch_id=batch_id,
            total_jobs=len(jobs),
            jobs=jobs
        )
        
        self.active_batches[batch_id] = batch_result
        logger.info(f"创建批量任务: {batch_id}, 共 {len(jobs)} 个文件")
        
        return batch_result
    
    async def process_batch(
        self,
        batch_id: str,
        progress_callback: Optional[Callable[[BatchResult], None]] = None
    ) -> BatchResult:
        """
        处理批量任务
        
        Args:
            batch_id: 批量任务ID
            progress_callback: 进度回调函数
        
        Returns:
            BatchResult: 处理结果
        """
        if batch_id not in self.active_batches:
            raise ValidationError(f"批量任务不存在: {batch_id}")
        
        batch_result = self.active_batches[batch_id]
        batch_result.status = "running"
        
        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_job(job: BatchJob):
            """处理单个任务"""
            async with semaphore:
                try:
                    job.status = "processing"
                    logger.info(f"开始处理任务: {job.job_id}, 文件: {job.file_path}")
                    
                    # 调用提取器处理文件
                    result = await self.extractor.process_novel(
                        job.file_path,
                        job.novel_type
                    )
                    
                    job.result = result
                    job.status = "completed"
                    job.completed_at = datetime.now().isoformat()
                    batch_result.completed_jobs += 1
                    
                    # 保存结果
                    await self._save_job_result(job)
                    
                    logger.info(f"任务完成: {job.job_id}")
                    
                except Exception as e:
                    job.status = "failed"
                    job.error = str(e)
                    job.completed_at = datetime.now().isoformat()
                    batch_result.failed_jobs += 1
                    
                    logger.error(f"任务失败: {job.job_id}, 错误: {e}", exc_info=True)
                
                finally:
                    # 调用进度回调
                    if progress_callback:
                        try:
                            progress_callback(batch_result)
                        except Exception as e:
                            logger.warning(f"进度回调失败: {e}")
        
        # 并发处理所有任务
        tasks = [process_job(job) for job in batch_result.jobs]
        await asyncio.gather(*tasks)
        
        # 更新批量任务状态
        if batch_result.failed_jobs == 0:
            batch_result.status = "completed"
        elif batch_result.completed_jobs == 0:
            batch_result.status = "failed"
        else:
            batch_result.status = "completed"  # 部分成功也算完成
        
        batch_result.completed_at = datetime.now().isoformat()
        
        # 保存批量结果
        await self._save_batch_result(batch_result)
        
        logger.info(
            f"批量任务完成: {batch_id}, "
            f"成功: {batch_result.completed_jobs}, "
            f"失败: {batch_result.failed_jobs}"
        )
        
        return batch_result
    
    async def _save_job_result(self, job: BatchJob):
        """保存任务结果"""
        if not job.result:
            return
        
        output_file = self.output_dir / f"{job.job_id}_result.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "job_id": job.job_id,
                "file_path": job.file_path,
                "status": job.status,
                "result": job.result,
                "error": job.error,
                "completed_at": job.completed_at
            }, f, ensure_ascii=False, indent=2)
    
    async def _save_batch_result(self, batch_result: BatchResult):
        """保存批量结果"""
        output_file = self.output_dir / f"{batch_result.batch_id}_summary.json"
        
        summary = {
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
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    
    def get_batch(self, batch_id: str) -> Optional[BatchResult]:
        """获取批量任务"""
        return self.active_batches.get(batch_id)
    
    def list_batches(self) -> List[BatchResult]:
        """列出所有批量任务"""
        return list(self.active_batches.values())
    
    def cancel_batch(self, batch_id: str) -> bool:
        """
        取消批量任务
        
        Args:
            batch_id: 批量任务ID
        
        Returns:
            bool: 是否成功取消
        """
        if batch_id not in self.active_batches:
            return False
        
        batch_result = self.active_batches[batch_id]
        if batch_result.status == "running":
            batch_result.status = "cancelled"
            logger.info(f"取消批量任务: {batch_id}")
            return True
        
        return False


def create_batch_processor(extractor, **kwargs) -> BatchProcessor:
    """
    创建批量处理器的便捷函数
    
    Args:
        extractor: 小说提取器实例
        **kwargs: 其他参数
    
    Returns:
        BatchProcessor: 批量处理器实例
    """
    return BatchProcessor(extractor, **kwargs)



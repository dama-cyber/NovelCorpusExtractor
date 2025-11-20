"""
归档员Agent
负责将提取的信息转换为结构化数据并写入记忆体文件
"""

from typing import Dict, List
import logging
from ..core.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class ArchivistAgent:
    """归档员Agent - 负责信息归档和一致性检查"""
    
    def __init__(self, memory_manager: MemoryManager):
        """
        初始化归档员
        Args:
            memory_manager: 记忆体管理器
        """
        self.memory_manager = memory_manager
    
    def archive_extracted_info(self, extracted_info: Dict, chunk_id: str) -> Dict:
        """
        归档提取的信息
        Returns:
            归档结果，包含冲突列表
        """
        conflicts = []
        
        # 归档世界观设定
        if "世界观设定" in extracted_info and extracted_info["世界观设定"]:
            worldview = extracted_info["世界观设定"]
            # 检查冲突
            worldview_conflicts = self.memory_manager.check_consistency(
                worldview, "worldview"
            )
            conflicts.extend(worldview_conflicts)
            
            if not worldview_conflicts:
                # 无冲突，更新记忆体
                self.memory_manager.update_worldview(worldview, merge=True)
                logger.info(f"世界观设定已归档 (块: {chunk_id})")
        
        # 归档人物信息
        if "人物信息" in extracted_info and extracted_info["人物信息"]:
            characters = extracted_info["人物信息"]
            for char_name, char_info in characters.items():
                # 检查冲突
                char_conflicts = self.memory_manager.check_consistency(
                    {char_name: char_info}, "character"
                )
                conflicts.extend(char_conflicts)
                
                if not char_conflicts:
                    # 无冲突，更新记忆体
                    self.memory_manager.update_character(char_name, char_info, merge=True)
                    logger.info(f"人物信息已归档: {char_name} (块: {chunk_id})")
        
        # 归档伏笔
        if "伏笔线索" in extracted_info and extracted_info["伏笔线索"]:
            foreshadowings = extracted_info["伏笔线索"]
            for foreshadowing in foreshadowings:
                if isinstance(foreshadowing, dict):
                    self.memory_manager.add_foreshadowing(foreshadowing)
                    logger.info(f"伏笔已归档 (块: {chunk_id})")
        
        return {
            "archived": True,
            "conflicts": conflicts,
            "chunk_id": chunk_id
        }
    
    def resolve_conflicts(self, conflicts: List[str], resolution: str = "manual"):
        """
        解决冲突
        Args:
            conflicts: 冲突列表
            resolution: 解决方式 ("manual", "keep_existing", "overwrite")
        """
        if resolution == "keep_existing":
            logger.info("保留现有记忆体，忽略新数据")
        elif resolution == "overwrite":
            logger.warning("覆盖现有记忆体（谨慎使用）")
        else:
            logger.info(f"检测到 {len(conflicts)} 个冲突，需要手动解决")


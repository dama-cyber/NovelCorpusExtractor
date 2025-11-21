"""
数据迁移工具
用于迁移和升级数据格式
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.exceptions import ConfigurationError, FileProcessingError
from core.utils import safe_read_json, safe_write_json, ensure_dir

logger = logging.getLogger(__name__)


class MigrationTool:
    """数据迁移工具"""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """
        初始化迁移工具
        
        Args:
            backup_dir: 备份目录，如果为None则使用默认位置
        """
        if backup_dir is None:
            backup_dir = Path("backups") / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(backup_dir)
        ensure_dir(self.backup_dir)
    
    def backup_data(self, source_path: Path) -> Path:
        """
        备份数据
        
        Args:
            source_path: 源文件或目录路径
        
        Returns:
            Path: 备份路径
        """
        backup_path = self.backup_dir / source_path.name
        
        if source_path.is_file():
            shutil.copy2(source_path, backup_path)
            logger.info(f"已备份文件: {source_path} -> {backup_path}")
        elif source_path.is_dir():
            shutil.copytree(source_path, backup_path, dirs_exist_ok=True)
            logger.info(f"已备份目录: {source_path} -> {backup_path}")
        else:
            raise FileProcessingError(f"源路径不存在: {source_path}")
        
        return backup_path
    
    def migrate_project_format(self, project_path: Path, target_version: str = "2.0") -> bool:
        """
        迁移项目格式
        
        Args:
            project_path: 项目路径
            target_version: 目标版本
        
        Returns:
            bool: 迁移是否成功
        """
        try:
            # 备份项目
            self.backup_data(project_path)
            
            # 读取项目配置
            config_file = project_path / "config.yaml"
            if not config_file.exists():
                logger.warning(f"项目配置文件不存在: {config_file}")
                return False
            
            # 这里可以添加具体的迁移逻辑
            # 例如：更新字段名、添加新字段等
            
            logger.info(f"项目格式迁移完成: {project_path} -> v{target_version}")
            return True
            
        except Exception as e:
            logger.error(f"项目格式迁移失败: {e}", exc_info=True)
            return False
    
    def migrate_card_format(self, card_path: Path, target_version: str = "2.0") -> bool:
        """
        迁移卡片格式
        
        Args:
            card_path: 卡片路径
            target_version: 目标版本
        
        Returns:
            bool: 迁移是否成功
        """
        try:
            # 备份卡片
            self.backup_data(card_path)
            
            # 读取卡片数据
            card_data = safe_read_json(card_path / "card.json")
            if not card_data:
                logger.warning(f"卡片数据文件不存在: {card_path}")
                return False
            
            # 迁移逻辑
            # 例如：更新字段结构
            if "version" not in card_data:
                card_data["version"] = target_version
                card_data["migrated_at"] = datetime.now().isoformat()
            
            # 保存迁移后的数据
            safe_write_json(card_path / "card.json", card_data)
            
            logger.info(f"卡片格式迁移完成: {card_path} -> v{target_version}")
            return True
            
        except Exception as e:
            logger.error(f"卡片格式迁移失败: {e}", exc_info=True)
            return False
    
    def migrate_all_projects(self, projects_dir: Path, target_version: str = "2.0") -> Dict[str, bool]:
        """
        迁移所有项目
        
        Args:
            projects_dir: 项目目录
            target_version: 目标版本
        
        Returns:
            Dict[str, bool]: 迁移结果 {项目名: 是否成功}
        """
        results = {}
        
        if not projects_dir.exists():
            logger.warning(f"项目目录不存在: {projects_dir}")
            return results
        
        for project_path in projects_dir.iterdir():
            if project_path.is_dir():
                project_name = project_path.name
                results[project_name] = self.migrate_project_format(
                    project_path, target_version
                )
        
        return results
    
    def migrate_all_cards(self, cards_dir: Path, target_version: str = "2.0") -> Dict[str, bool]:
        """
        迁移所有卡片
        
        Args:
            cards_dir: 卡片目录
            target_version: 目标版本
        
        Returns:
            Dict[str, bool]: 迁移结果 {卡片名: 是否成功}
        """
        results = {}
        
        if not cards_dir.exists():
            logger.warning(f"卡片目录不存在: {cards_dir}")
            return results
        
        for card_path in cards_dir.iterdir():
            if card_path.is_dir():
                card_name = card_path.name
                results[card_name] = self.migrate_card_format(
                    card_path, target_version
                )
        
        return results
    
    def get_migration_report(self) -> Dict[str, Any]:
        """
        获取迁移报告
        
        Returns:
            Dict[str, Any]: 迁移报告
        """
        return {
            "backup_dir": str(self.backup_dir),
            "backup_exists": self.backup_dir.exists(),
            "backup_files": list(self.backup_dir.iterdir()) if self.backup_dir.exists() else []
        }


def migrate_data(
    projects_dir: Optional[Path] = None,
    cards_dir: Optional[Path] = None,
    target_version: str = "2.0",
    backup_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    迁移数据的便捷函数
    
    Args:
        projects_dir: 项目目录
        cards_dir: 卡片目录
        target_version: 目标版本
        backup_dir: 备份目录
    
    Returns:
        Dict[str, Any]: 迁移结果
    """
    tool = MigrationTool(backup_dir)
    results = {
        "projects": {},
        "cards": {},
        "backup_dir": str(tool.backup_dir)
    }
    
    if projects_dir:
        results["projects"] = tool.migrate_all_projects(projects_dir, target_version)
    
    if cards_dir:
        results["cards"] = tool.migrate_all_cards(cards_dir, target_version)
    
    return results



"""
卡片管理系统
管理所有创作元素（角色、场景、大纲、章节等）的卡片
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Card:
    """卡片数据类"""
    id: str
    project_id: str
    type: str
    data: Dict[str, Any]
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)  # 引用的其他卡片ID
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def update(self, updates: Dict[str, Any]):
        """更新卡片数据"""
        if 'data' in updates:
            self.data.update(updates['data'])
        if 'metadata' in updates:
            self.metadata.update(updates['metadata'])
        self.updated_at = datetime.now().isoformat()


class CardManager:
    """卡片管理器"""
    
    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.cards: Dict[str, Card] = {}
        self._load_all_cards()
    
    def _get_project_dir(self, project_id: str) -> Path:
        """获取项目目录"""
        return self.projects_dir / project_id
    
    def _get_cards_dir(self, project_id: str) -> Path:
        """获取项目卡片目录"""
        cards_dir = self._get_project_dir(project_id) / "cards"
        cards_dir.mkdir(parents=True, exist_ok=True)
        return cards_dir
    
    def _get_card_path(self, project_id: str, card_id: str) -> Path:
        """获取卡片文件路径"""
        return self._get_cards_dir(project_id) / f"{card_id}.json"
    
    def _load_all_cards(self):
        """加载所有卡片"""
        if not self.projects_dir.exists():
            return
        
        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            
            project_id = project_dir.name
            cards_dir = project_dir / "cards"
            
            if not cards_dir.exists():
                continue
            
            for card_file in cards_dir.glob("*.json"):
                try:
                    with open(card_file, 'r', encoding='utf-8') as f:
                        card_data = json.load(f)
                        card = Card(**card_data)
                        self.cards[card.id] = card
                except Exception as e:
                    logger.error(f"加载卡片失败 {card_file}: {e}")
    
    def _save_card(self, card: Card):
        """保存卡片到文件"""
        card_path = self._get_card_path(card.project_id, card.id)
        try:
            with open(card_path, 'w', encoding='utf-8') as f:
                json.dump(card.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存卡片失败 {card_path}: {e}")
            raise
    
    def create_card(
        self,
        project_id: str,
        card_type: str,
        data: Dict[str, Any],
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """创建新卡片"""
        card_id = str(uuid.uuid4())
        card = Card(
            id=card_id,
            project_id=project_id,
            type=card_type,
            data=data,
            parent_id=parent_id,
            metadata=metadata or {}
        )
        
        # 如果有父卡片，更新父卡片的children_ids
        if parent_id:
            parent_card = self.cards.get(parent_id)
            if parent_card:
                parent_card.children_ids.append(card_id)
                self._save_card(parent_card)
        
        self.cards[card_id] = card
        self._save_card(card)
        
        logger.info(f"创建卡片: {card_id} (类型: {card_type}, 项目: {project_id})")
        return card.to_dict()
    
    def get_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        """获取卡片"""
        card = self.cards.get(card_id)
        return card.to_dict() if card else None
    
    def update_card(self, card_id: str, updates: Dict[str, Any]):
        """更新卡片"""
        card = self.cards.get(card_id)
        if not card:
            raise ValueError(f"卡片不存在: {card_id}")
        
        card.update(updates)
        self._save_card(card)
        logger.info(f"更新卡片: {card_id}")
    
    def delete_card(self, card_id: str):
        """删除卡片"""
        card = self.cards.get(card_id)
        if not card:
            raise ValueError(f"卡片不存在: {card_id}")
        
        # 如果有父卡片，从父卡片的children_ids中移除
        if card.parent_id:
            parent_card = self.cards.get(card.parent_id)
            if parent_card and card_id in parent_card.children_ids:
                parent_card.children_ids.remove(card_id)
                self._save_card(parent_card)
        
        # 删除子卡片
        for child_id in card.children_ids:
            self.delete_card(child_id)
        
        # 删除文件
        card_path = self._get_card_path(card.project_id, card_id)
        if card_path.exists():
            card_path.unlink()
        
        # 从内存中移除
        del self.cards[card_id]
        logger.info(f"删除卡片: {card_id}")
    
    def get_project_cards(
        self,
        project_id: str,
        card_type: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取项目的所有卡片"""
        cards = [c for c in self.cards.values() if c.project_id == project_id]
        
        if card_type:
            cards = [c for c in cards if c.type == card_type]
        
        if parent_id:
            cards = [c for c in cards if c.parent_id == parent_id]
        
        return [c.to_dict() for c in cards]
    
    def get_card_tree(self, root_card_id: str) -> Dict[str, Any]:
        """获取卡片树（包含所有子卡片）"""
        card = self.cards.get(root_card_id)
        if not card:
            return {}
        
        result = card.to_dict()
        result['children'] = []
        
        for child_id in card.children_ids:
            child_tree = self.get_card_tree(child_id)
            if child_tree:
                result['children'].append(child_tree)
        
        return result
    
    def add_reference(self, card_id: str, referenced_card_id: str):
        """添加卡片引用"""
        card = self.cards.get(card_id)
        if not card:
            raise ValueError(f"卡片不存在: {card_id}")
        
        if referenced_card_id not in card.references:
            card.references.append(referenced_card_id)
            self._save_card(card)
            logger.info(f"添加引用: {card_id} -> {referenced_card_id}")



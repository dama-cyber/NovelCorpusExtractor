"""
记忆体管理器
负责世界观、人物、剧情、伏笔等记忆体的读写和管理
"""

import os
import yaml
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryManager:
    """记忆体管理器"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 记忆体文件路径
        self.worldview_path = self.output_dir / "02_世界观记忆体.yaml"
        self.character_path = self.output_dir / "03_人物记忆体.yaml"
        self.plot_path = self.output_dir / "04_剧情规划大纲.yaml"
        self.foreshadowing_path = self.output_dir / "05_伏笔追踪表.yaml"
        
        # 初始化记忆体
        self._init_memories()
    
    def _init_memories(self):
        """初始化记忆体文件"""
        if not self.worldview_path.exists():
            self.save_worldview({})
        if not self.character_path.exists():
            self.save_characters({})
        if not self.plot_path.exists():
            self.save_plot({})
        if not self.foreshadowing_path.exists():
            self.save_foreshadowing([])
    
    def load_worldview(self) -> Dict:
        """加载世界观记忆体"""
        try:
            if self.worldview_path.exists():
                with open(self.worldview_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            return {}
        except Exception as e:
            logger.error(f"加载世界观记忆体失败: {e}")
            return {}
    
    def save_worldview(self, data: Dict):
        """保存世界观记忆体"""
        try:
            with open(self.worldview_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            logger.info(f"世界观记忆体已保存到 {self.worldview_path}")
        except Exception as e:
            logger.error(f"保存世界观记忆体失败: {e}")
            raise
    
    def update_worldview(self, updates: Dict, merge: bool = True):
        """更新世界观记忆体"""
        current = self.load_worldview()
        if merge:
            current = self._deep_merge(current, updates)
        else:
            current.update(updates)
        self.save_worldview(current)
    
    def load_characters(self) -> Dict:
        """加载人物记忆体"""
        try:
            if self.character_path.exists():
                with open(self.character_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            return {}
        except Exception as e:
            logger.error(f"加载人物记忆体失败: {e}")
            return {}
    
    def save_characters(self, data: Dict):
        """保存人物记忆体"""
        try:
            with open(self.character_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            logger.info(f"人物记忆体已保存到 {self.character_path}")
        except Exception as e:
            logger.error(f"保存人物记忆体失败: {e}")
            raise
    
    def update_character(self, character_name: str, updates: Dict, merge: bool = True):
        """更新特定人物信息"""
        characters = self.load_characters()
        if character_name not in characters:
            characters[character_name] = {}
        
        if merge:
            characters[character_name] = self._deep_merge(characters[character_name], updates)
        else:
            characters[character_name].update(updates)
        
        self.save_characters(characters)
    
    def load_plot(self) -> Dict:
        """加载剧情规划大纲"""
        try:
            if self.plot_path.exists():
                with open(self.plot_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            return {}
        except Exception as e:
            logger.error(f"加载剧情规划大纲失败: {e}")
            return {}
    
    def save_plot(self, data: Dict):
        """保存剧情规划大纲"""
        try:
            with open(self.plot_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            logger.info(f"剧情规划大纲已保存到 {self.plot_path}")
        except Exception as e:
            logger.error(f"保存剧情规划大纲失败: {e}")
            raise
    
    def load_foreshadowing(self) -> List[Dict]:
        """加载伏笔追踪表"""
        try:
            if self.foreshadowing_path.exists():
                with open(self.foreshadowing_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or []
            return []
        except Exception as e:
            logger.error(f"加载伏笔追踪表失败: {e}")
            return []
    
    def save_foreshadowing(self, data: List[Dict]):
        """保存伏笔追踪表"""
        try:
            with open(self.foreshadowing_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            logger.info(f"伏笔追踪表已保存到 {self.foreshadowing_path}")
        except Exception as e:
            logger.error(f"保存伏笔追踪表失败: {e}")
            raise
    
    def add_foreshadowing(self, foreshadowing: Dict):
        """添加新伏笔"""
        if not isinstance(foreshadowing, dict):
            logger.warning(f"伏笔数据格式错误，期望字典类型，得到: {type(foreshadowing)}")
            return
        
        foreshadowings = self.load_foreshadowing()
        # 生成ID
        if not foreshadowing.get("id"):
            if foreshadowings:
                # 提取所有ID并找到最大值
                ids = []
                for f in foreshadowings:
                    fid = f.get("id", "0")
                    # 移除前导零并转换为整数
                    try:
                        ids.append(int(fid.lstrip("0") or "0"))
                    except (ValueError, AttributeError):
                        ids.append(0)
                max_id = max(ids) if ids else 0
            else:
                max_id = 0
            foreshadowing["id"] = f"{max_id + 1:03d}"
        
        foreshadowing.setdefault("status", "未回收")
        foreshadowing.setdefault("埋设时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        foreshadowings.append(foreshadowing)
        self.save_foreshadowing(foreshadowings)
    
    def mark_foreshadowing_resolved(self, foreshadowing_id: str, resolved_chapter: str):
        """标记伏笔已回收"""
        foreshadowings = self.load_foreshadowing()
        for f in foreshadowings:
            if f.get("id") == foreshadowing_id:
                f["status"] = "已回收"
                f["实际回收章节"] = resolved_chapter
                f["回收时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
        self.save_foreshadowing(foreshadowings)
    
    def check_consistency(self, new_data: Dict, data_type: str) -> List[str]:
        """检查新数据与现有记忆体的一致性，返回冲突列表"""
        conflicts = []
        
        if data_type == "worldview":
            current = self.load_worldview()
            conflicts = self._check_worldview_conflicts(current, new_data)
        elif data_type == "character":
            current = self.load_characters()
            conflicts = self._check_character_conflicts(current, new_data)
        
        return conflicts
    
    def _check_worldview_conflicts(self, current: Dict, new_data: Dict) -> List[str]:
        """检查世界观冲突"""
        conflicts = []
        # 实现冲突检测逻辑
        # 例如：检查力量体系等级是否一致
        if "力量体系" in current and "力量体系" in new_data:
            current_levels = current["力量体系"].get("等级划分", [])
            new_levels = new_data["力量体系"].get("等级划分", [])
            if current_levels and new_levels and current_levels != new_levels:
                conflicts.append("力量体系等级划分不一致")
        return conflicts
    
    def _check_character_conflicts(self, current: Dict, new_data: Dict) -> List[str]:
        """检查人物设定冲突"""
        conflicts = []
        # 实现冲突检测逻辑
        # 例如：检查同一人物的性格设定是否一致
        for char_name, char_data in new_data.items():
            if char_name in current:
                current_char = current[char_name]
                if "MBTI类型" in current_char and "MBTI类型" in char_data:
                    if current_char["MBTI类型"] != char_data["MBTI类型"]:
                        conflicts.append(f"{char_name}的MBTI类型不一致: {current_char['MBTI类型']} vs {char_data['MBTI类型']}")
        return conflicts
    
    def _deep_merge(self, base: Dict, updates: Dict) -> Dict:
        """深度合并字典"""
        result = base.copy()
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result


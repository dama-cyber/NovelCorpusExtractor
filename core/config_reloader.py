"""
配置热重载模块
支持在不重启服务的情况下重新加载配置
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Optional, Callable, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class ConfigReloader:
    """配置热重载器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置重载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config: Dict = {}
        self.callbacks: List[Callable[[Dict], None]] = []
        self.observer: Optional[Observer] = None
        self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"配置已加载: {self.config_path}")
            else:
                logger.warning(f"配置文件不存在: {self.config_path}")
                self.config = {}
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            self.config = {}
        return self.config
    
    def register_callback(self, callback: Callable[[Dict], None]):
        """
        注册配置变更回调
        
        Args:
            callback: 配置变更时调用的回调函数
        """
        self.callbacks.append(callback)
    
    def _notify_callbacks(self, new_config: Dict):
        """通知所有回调函数配置已变更"""
        for callback in self.callbacks:
            try:
                callback(new_config)
            except Exception as e:
                logger.error(f"配置变更回调执行失败: {e}")
    
    def start_watching(self):
        """开始监控配置文件变更"""
        if self.observer:
            return
        
        class ConfigFileHandler(FileSystemEventHandler):
            def __init__(self, reloader):
                self.reloader = reloader
            
            def on_modified(self, event):
                if event.src_path == str(self.reloader.config_path):
                    logger.info("检测到配置文件变更，重新加载...")
                    new_config = self.reloader._load_config()
                    self.reloader._notify_callbacks(new_config)
        
        try:
            self.observer = Observer()
            self.observer.schedule(
                ConfigFileHandler(self),
                str(self.config_path.parent),
                recursive=False
            )
            self.observer.start()
            logger.info(f"开始监控配置文件: {self.config_path}")
        except Exception as e:
            logger.error(f"启动配置监控失败: {e}")
    
    def stop_watching(self):
        """停止监控配置文件变更"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("已停止监控配置文件")
    
    def get_config(self) -> Dict:
        """获取当前配置"""
        return self.config.copy()
    
    def reload(self) -> Dict:
        """
        手动重新加载配置
        
        Returns:
            新的配置字典
        """
        new_config = self._load_config()
        self._notify_callbacks(new_config)
        return new_config


# 全局配置重载器实例
_global_reloader: Optional[ConfigReloader] = None


def get_config_reloader(config_path: str = "config.yaml") -> ConfigReloader:
    """获取配置重载器实例（单例模式）"""
    global _global_reloader
    if _global_reloader is None:
        _global_reloader = ConfigReloader(config_path)
    return _global_reloader



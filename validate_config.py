"""
配置文件验证工具
用于检查 config.yaml 的完整性和有效性
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import yaml
except ImportError:
    print("错误: 需要安装 PyYAML")
    print("运行: pip install PyYAML")
    sys.exit(1)


def validate_config(config_path: str = "config.yaml") -> Tuple[bool, List[str]]:
    """
    验证配置文件
    
    返回:
        (是否有效, 错误/警告列表)
    """
    errors = []
    warnings = []
    
    # 检查文件是否存在
    if not Path(config_path).exists():
        return False, [f"配置文件不存在: {config_path}"]
    
    # 读取配置
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        return False, [f"配置文件格式错误: {e}"]
    except Exception as e:
        return False, [f"读取配置文件失败: {e}"]
    
    # 验证模型配置
    model_config = config.get("model", {})
    api_pool_config = config.get("api_pool", {})
    
    if api_pool_config.get("enabled", False):
        # 多API池模式
        apis = api_pool_config.get("apis", [])
        if not apis:
            errors.append("API池模式已启用，但未配置任何API")
        else:
            enabled_apis = []
            for i, api in enumerate(apis):
                if api.get("enabled", True):
                    enabled_apis.append(api)
                    # 检查必要的字段
                    if not api.get("provider"):
                        errors.append(f"API配置 #{i+1} 缺少 provider 字段")
                    if not api.get("api_key"):
                        provider = api.get("provider", "").upper()
                        env_key = f"{provider}_API_KEY"
                        if not os.getenv(env_key):
                            warnings.append(f"API配置 #{i+1} ({api.get('name', 'unknown')}) 缺少 api_key，且环境变量 {env_key} 也未设置")
            if not enabled_apis:
                warnings.append("API池模式已启用，但未找到启用的API配置")
    else:
        # 单API模式
        if not model_config.get("model"):
            warnings.append("未指定模型类型，将使用默认配置")
        if not model_config.get("api_key"):
            model_type = model_config.get("model", "openai").upper()
            env_key = f"{model_type}_API_KEY"
            if not os.getenv(env_key):
                warnings.append(f"未找到API密钥（配置文件中或环境变量 {env_key}）")
    
    # 验证拓扑配置
    topology_config = config.get("topology", {})
    topology_mode = topology_config.get("mode", "auto")
    valid_modes = ["auto", "linear", "triangular", "swarm"]
    if topology_mode not in valid_modes:
        errors.append(f"无效的拓扑模式: {topology_mode}，有效值: {', '.join(valid_modes)}")
    
    # 验证处理配置
    chunk_size = config.get("chunk_size", 1024)
    if chunk_size <= 0:
        errors.append(f"chunk_size ({chunk_size}) 必须大于 0")
    
    chunk_overlap = config.get("chunk_overlap", 100)
    if chunk_overlap < 0:
        errors.append(f"chunk_overlap ({chunk_overlap}) 不能为负数")
    
    if chunk_overlap >= chunk_size:
        warnings.append(f"chunk_overlap ({chunk_overlap}) 大于等于 chunk_size ({chunk_size})，建议调整")
    
    # 验证目录配置
    output_dir = config.get("output_dir", "output")
    if not output_dir:
        errors.append("output_dir 不能为空")
    
    corpus_dir = config.get("corpus_dir", "corpus_samples")
    if not corpus_dir:
        warnings.append("corpus_dir 未配置，将使用默认值")
    
    # 验证日志配置
    log_config = config.get("logging", {})
    log_level = log_config.get("level", "INFO")
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level.upper() not in valid_levels:
        warnings.append(f"无效的日志级别: {log_level}，有效值: {', '.join(valid_levels)}")
    
    all_issues = errors + warnings
    return len(errors) == 0, all_issues


def main():
    """主函数"""
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    print(f"验证配置文件: {config_path}")
    print("=" * 50)
    
    is_valid, issues = validate_config(config_path)
    
    if not issues:
        print("✓ 配置文件验证通过，未发现问题")
        return 0
    
    # 分类显示问题
    errors = [i for i in issues if i.startswith("错误") or "必须" in i or "不能" in i]
    warnings = [i for i in issues if i not in errors]
    
    if errors:
        print("\n❌ 错误:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("\n⚠️  警告:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if errors:
        print("\n配置文件存在错误，请修复后重试")
        return 1
    else:
        print("\n配置文件验证完成（有警告但可以使用）")
        return 0


if __name__ == "__main__":
    sys.exit(main())



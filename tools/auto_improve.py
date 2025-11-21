"""
自动化代码改进工具
批量检查和修复常见代码质量问题
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class CodeImprover:
    """代码改进器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.issues: List[Dict] = []
    
    def find_issues(self) -> List[Dict]:
        """查找代码问题"""
        issues = []
        
        # 查找Python文件
        for py_file in self.root_dir.rglob("*.py"):
            if "node_modules" in str(py_file) or ".git" in str(py_file):
                continue
            
            file_issues = self._check_file(py_file)
            issues.extend(file_issues)
        
        return issues
    
    def _check_file(self, file_path: Path) -> List[Dict]:
        """检查单个文件"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 检查空行
            for i, line in enumerate(lines, 1):
                # 检查行尾空格
                if line.rstrip() != line and line.strip():
                    issues.append({
                        "file": str(file_path),
                        "line": i,
                        "type": "trailing_whitespace",
                        "message": "行尾有空格"
                    })
            
            # 检查导入顺序
            imports = self._extract_imports(content)
            if imports:
                issues.extend(self._check_import_order(file_path, imports))
            
            # 检查TODO注释
            for i, line in enumerate(lines, 1):
                if "TODO" in line or "FIXME" in line:
                    issues.append({
                        "file": str(file_path),
                        "line": i,
                        "type": "todo",
                        "message": f"发现TODO/FIXME: {line.strip()}"
                    })
            
        except Exception as e:
            logger.warning(f"检查文件失败 {file_path}: {e}")
        
        return issues
    
    def _extract_imports(self, content: str) -> List[Tuple[int, str]]:
        """提取导入语句"""
        imports = []
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip().startswith(('import ', 'from ')):
                imports.append((i, line))
        return imports
    
    def _check_import_order(self, file_path: Path, imports: List[Tuple[int, str]]) -> List[Dict]:
        """检查导入顺序"""
        issues = []
        # 标准库应该在前面
        stdlib_imports = []
        third_party_imports = []
        local_imports = []
        
        for line_num, line in imports:
            if line.startswith('from .') or line.startswith('import .'):
                local_imports.append((line_num, line))
            elif any(stdlib in line for stdlib in ['import os', 'import sys', 'import json', 'import logging']):
                stdlib_imports.append((line_num, line))
            else:
                third_party_imports.append((line_num, line))
        
        # 检查顺序是否正确
        all_imports = stdlib_imports + third_party_imports + local_imports
        if len(all_imports) > 1:
            # 简单检查：如果本地导入在标准库之前，报告问题
            if local_imports and stdlib_imports:
                if local_imports[0][0] < stdlib_imports[-1][0]:
                    issues.append({
                        "file": str(file_path),
                        "line": local_imports[0][0],
                        "type": "import_order",
                        "message": "导入顺序可能不正确，标准库应该在本地导入之前"
                    })
        
        return issues
    
    def generate_report(self, issues: List[Dict]) -> str:
        """生成问题报告"""
        if not issues:
            return "未发现代码质量问题"
        
        report = f"发现 {len(issues)} 个潜在问题：\n\n"
        
        by_type = {}
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue)
        
        for issue_type, type_issues in by_type.items():
            report += f"\n{issue_type} ({len(type_issues)} 个):\n"
            for issue in type_issues[:10]:  # 只显示前10个
                report += f"  {issue['file']}:{issue['line']} - {issue['message']}\n"
            if len(type_issues) > 10:
                report += f"  ... 还有 {len(type_issues) - 10} 个类似问题\n"
        
        return report


def main():
    """主函数"""
    improver = CodeImprover(".")
    issues = improver.find_issues()
    report = improver.generate_report(issues)
    print(report)
    
    # 保存报告
    with open("code_quality_report.txt", 'w', encoding='utf-8') as f:
        f.write(report)


if __name__ == "__main__":
    main()



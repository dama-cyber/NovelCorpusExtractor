#!/bin/bash
# Linux/Mac Shell脚本 - 使用示例

echo "========================================"
echo "小说语料提取系统 - 使用示例"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python，请先安装Python 3.8+"
    exit 1
fi

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "[警告] 未找到config.yaml配置文件"
    echo "请先创建配置文件或设置环境变量"
    echo ""
fi

# 示例1: 基本使用
echo "示例1: 基本使用"
echo "python3 main.py --input novel.txt --type 玄幻"
echo ""

# 示例2: 自定义输出目录
echo "示例2: 自定义输出目录"
echo "python3 main.py --input novel.txt --type 玄幻 --output my_output"
echo ""

# 示例3: 使用环境变量
echo "示例3: 使用环境变量"
echo "export OPENAI_API_KEY='your-api-key-here'"
echo "python3 main.py --input novel.txt --type 玄幻"
echo ""

echo "========================================"
echo "请将上述命令中的参数替换为实际值"
echo "详细说明请查看 USAGE_GUIDE.md"
echo "========================================"


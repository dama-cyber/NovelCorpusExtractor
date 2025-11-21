#!/bin/bash
# Linux/Mac启动脚本 - API服务器

echo "启动NovelCorpusExtractor API服务器..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查依赖是否安装
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 设置环境变量（可选）
export CONFIG_PATH=${CONFIG_PATH:-config.yaml}
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}

# 启动服务器
echo "启动API服务器在 http://localhost:${PORT}"
python3 api_server.py



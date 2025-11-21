@echo off
REM Windows启动脚本 - API服务器
echo 启动NovelCorpusExtractor API服务器...

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)

REM 设置环境变量（可选）
set CONFIG_PATH=config.yaml
set PORT=8000
set HOST=0.0.0.0

REM 启动服务器
echo 启动API服务器在 http://localhost:8000
python api_server.py

pause



@echo off
REM Windows批处理脚本 - 使用示例
chcp 65001 >nul
echo ========================================
echo 小说语料提取系统 - 使用示例
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查配置文件
if not exist config.yaml (
    echo [警告] 未找到config.yaml配置文件
    echo 请先创建配置文件或设置环境变量
    echo.
)

REM 示例1: 基本使用
echo 示例1: 基本使用
echo python main.py --input novel.txt --type 玄幻
echo.

REM 示例2: 自定义输出目录
echo 示例2: 自定义输出目录
echo python main.py --input novel.txt --type 玄幻 --output my_output
echo.

REM 示例3: 使用环境变量
echo 示例3: 使用环境变量（在运行前设置）
echo set OPENAI_API_KEY=your-api-key-here
echo python main.py --input novel.txt --type 玄幻
echo.

echo ========================================
echo 请将上述命令中的参数替换为实际值
echo 详细说明请查看 USAGE_GUIDE.md
echo ========================================
pause


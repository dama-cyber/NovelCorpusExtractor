"""测试服务器启动"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("检查依赖...")
try:
    import fastapi
    print("✓ FastAPI 已安装")
except ImportError as e:
    print(f"✗ FastAPI 未安装: {e}")
    sys.exit(1)

try:
    import uvicorn
    print("✓ Uvicorn 已安装")
except ImportError as e:
    print(f"✗ Uvicorn 未安装: {e}")
    sys.exit(1)

try:
    from main import NovelCorpusExtractor
    print("✓ main 模块导入成功")
except ImportError as e:
    print(f"✗ main 模块导入失败: {e}")
    sys.exit(1)

print("\n所有依赖检查通过！")
print("正在启动服务器...\n")

# 导入并启动服务器
from api_server import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )



# 小说语料提取系统 - 依赖安装脚本
# PowerShell 版本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  小说语料提取系统 - 依赖安装" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 查找 Python
$pythonPaths = @(
    "python",
    "python3",
    "py",
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "C:\Program Files\Python313\python.exe",
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe",
    "C:\Program Files\Python310\python.exe"
)

$pythonCmd = $null
foreach ($path in $pythonPaths) {
    try {
        $result = & $path --version 2>&1
        if ($LASTEXITCODE -eq 0 -or $result -match "Python") {
            $pythonCmd = $path
            Write-Host "✓ 找到 Python: $path" -ForegroundColor Green
            Write-Host "  版本: $result" -ForegroundColor Gray
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "❌ 未找到 Python！" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先安装 Python 3.8 或更高版本：" -ForegroundColor Yellow
    Write-Host "1. 访问 https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "2. 下载并安装 Python 3.8+" -ForegroundColor Yellow
    Write-Host "3. 安装时勾选 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "正在安装依赖包..." -ForegroundColor Yellow
Write-Host ""

# 获取脚本所在目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$requirementsFile = Join-Path $scriptDir "requirements.txt"

if (-not (Test-Path $requirementsFile)) {
    Write-Host "❌ 未找到 requirements.txt 文件！" -ForegroundColor Red
    Write-Host "   路径: $requirementsFile" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

# 升级 pip
Write-Host "升级 pip..." -ForegroundColor Cyan
& $pythonCmd -m pip install --upgrade pip --quiet

# 安装依赖
Write-Host "安装项目依赖..." -ForegroundColor Cyan
& $pythonCmd -m pip install -r $requirementsFile

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ 依赖安装完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "现在可以启动服务器了：" -ForegroundColor Yellow
    Write-Host "  方法1: 运行 start_api.bat" -ForegroundColor White
    Write-Host "  方法2: 运行 python api_server.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ 依赖安装失败！" -ForegroundColor Red
    Write-Host "请检查错误信息并重试。" -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "Press Enter to exit"


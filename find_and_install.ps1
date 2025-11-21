# 查找 Python 并安装依赖

Write-Host "正在查找 Python..." -ForegroundColor Cyan

# 尝试多种方式查找 Python
$pythonPaths = @(
    "python",
    "python3",
    "py",
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python38\python.exe",
    "C:\Program Files\Python313\python.exe",
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe",
    "C:\Program Files\Python310\python.exe",
    "C:\Program Files\Python39\python.exe",
    "C:\Program Files\Python38\python.exe",
    "C:\Python313\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe"
)

$pythonCmd = $null
foreach ($path in $pythonPaths) {
    try {
        if (Test-Path $path) {
            $result = & $path --version 2>&1
            if ($LASTEXITCODE -eq 0 -or $result -match "Python") {
                $pythonCmd = $path
                Write-Host "✓ 找到 Python: $path" -ForegroundColor Green
                Write-Host "  版本信息: $result" -ForegroundColor Gray
                break
            }
        }
    } catch {
        continue
    }
}

# 如果还没找到，尝试搜索整个系统
if (-not $pythonCmd) {
    Write-Host "在常见位置未找到 Python，正在搜索..." -ForegroundColor Yellow
    $searchPaths = @(
        "$env:LOCALAPPDATA\Programs",
        "C:\Program Files",
        "C:\Python*"
    )
    
    foreach ($searchPath in $searchPaths) {
        $found = Get-ChildItem -Path $searchPath -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            try {
                $result = & $found.FullName --version 2>&1
                if ($LASTEXITCODE -eq 0 -or $result -match "Python") {
                    $pythonCmd = $found.FullName
                    Write-Host "✓ 找到 Python: $($found.FullName)" -ForegroundColor Green
                    Write-Host "  版本信息: $result" -ForegroundColor Gray
                    break
                }
            } catch {
                continue
            }
        }
    }
}

if (-not $pythonCmd) {
    Write-Host ""
    Write-Host "❌ 未找到 Python！" -ForegroundColor Red
    Write-Host ""
    Write-Host "请确保 Python 已正确安装，然后：" -ForegroundColor Yellow
    Write-Host "1. 重启 PowerShell 窗口" -ForegroundColor Yellow
    Write-Host "2. 或者手动运行: python -m pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按 Enter 键退出"
    exit 1
}

Write-Host ""
Write-Host "正在升级 pip..." -ForegroundColor Cyan
& $pythonCmd -m pip install --upgrade pip --quiet

Write-Host "正在安装项目依赖..." -ForegroundColor Cyan
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$requirementsFile = Join-Path $scriptDir "requirements.txt"

if (-not (Test-Path $requirementsFile)) {
    Write-Host "❌ 未找到 requirements.txt 文件！" -ForegroundColor Red
    Read-Host "按 Enter 键退出"
    exit 1
}

& $pythonCmd -m pip install -r $requirementsFile

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ 依赖安装完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ 依赖安装失败！" -ForegroundColor Red
    Write-Host "请检查错误信息并重试。" -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "按 Enter 键退出"



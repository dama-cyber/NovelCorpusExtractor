@echo off
chcp 65001 >nul
echo ========================================
echo   小说语料提取系统 - 依赖安装
echo ========================================
echo.

REM 尝试查找 Python
set PYTHON_CMD=
where python >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON_CMD=python
    python --version
    goto :found
)

where py >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON_CMD=py
    py --version
    goto :found
)

REM 尝试常见安装路径
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
    "%PYTHON_CMD%" --version
    goto :found
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    "%PYTHON_CMD%" --version
    goto :found
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
    "%PYTHON_CMD%" --version
    goto :found
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
    "%PYTHON_CMD%" --version
    goto :found
)

echo 未找到 Python！
echo.
echo 请确保 Python 已正确安装，然后：
echo 1. 重启命令提示符窗口
echo 2. 或者手动运行: python -m pip install -r requirements.txt
echo.
pause
exit /b 1

:found
echo.
echo 正在升级 pip...
"%PYTHON_CMD%" -m pip install --upgrade pip --quiet

echo 正在安装项目依赖...
"%PYTHON_CMD%" -m pip install -r requirements.txt

if %ERRORLEVEL% == 0 (
    echo.
    echo ========================================
    echo   ✓ 依赖安装完成！
    echo ========================================
    echo.
) else (
    echo.
    echo 依赖安装失败！
    echo 请检查错误信息并重试。
    echo.
)

pause



@echo off
chcp 65001 >nul
echo ========================================
echo   Python Dependency Installer
echo ========================================
echo.

echo Checking for Python...
python --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo [OK] Python found
    python --version
    echo.
    echo Upgrading pip...
    python -m pip install --upgrade pip --quiet
    echo.
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% == 0 (
        echo.
        echo ========================================
        echo   Installation completed successfully!
        echo ========================================
    ) else (
        echo.
        echo [ERROR] Installation failed!
        echo Please check the error messages above.
    )
    echo.
    pause
    exit /b 0
)

echo [ERROR] Python not found!
echo.
echo Please install Python first:
echo 1. Visit: https://www.python.org/downloads/
echo 2. Download and install Python
echo 3. Make sure to check "Add Python to PATH" during installation
echo 4. Restart this terminal and run this script again
echo.
echo For detailed instructions, see: 安装指南.md
echo.
pause
exit /b 1



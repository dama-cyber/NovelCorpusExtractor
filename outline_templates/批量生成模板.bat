@echo off
chcp 65001 >nul
echo 正在生成所有类型的大纲模板...
cd /d "%~dp0"
python 生成所有类型模板.py
pause





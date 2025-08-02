@echo off
echo 正在构建智能文件分类器可执行文件...
python build_executable.py
if %ERRORLEVEL% EQU 0 (
    echo 构建成功！可执行文件位于 release\ 目录中
    pause
) else (
    echo 构建失败！
    pause
    exit /b 1
) 
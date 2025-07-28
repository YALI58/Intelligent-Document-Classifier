@echo off
echo 正在构建智能文件分类器可执行文件...
python build_executable.py
if %ERRORLEVEL% NEQ 0 (
    echo 构建失败！
    pause
    exit /b 1
)
echo 构建完成！可执行文件位于release目录。
pause 
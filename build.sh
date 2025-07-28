#!/bin/bash

echo "正在构建智能文件分类器可执行文件..."
python3 build_executable.py

if [ $? -ne 0 ]; then
    echo "构建失败！"
    read -p "按回车键继续..."
    exit 1
fi

echo "构建完成！可执行文件位于release目录。"
read -p "按回车键继续..." 
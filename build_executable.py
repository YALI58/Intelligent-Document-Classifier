#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess
import platform

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 确保PyInstaller已安装
    try:
        import PyInstaller
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 检查图标文件
    icon_path = os.path.join("resources", "icon.ico")
    if not os.path.exists(icon_path):
        print(f"警告：未找到图标文件 {icon_path}")
        icon_path = None
    else:
        print(f"使用自定义图标：{icon_path}")
    
    # 创建发布目录
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    if not os.path.exists("build"):
        os.makedirs("build")
    
    # 构建命令参数
    args = [
        "pyinstaller",
        "--name=intelligent_file_classifier",
        "--onefile",
        "--windowed",
        "--clean",
        "--add-data=README.md:.",
        "--add-data=hierarchical_classification_guide.md:.",
        "--add-data=intelligent_recommendations_guide.md:.",
        "main.py"
    ]
    
    # 添加图标
    if icon_path:
        args.append(f"--icon={icon_path}")
    
    print(f"执行命令: {' '.join(args)}")
    subprocess.check_call(args)
    
    # 创建发布包
    release_dir = "release"
    if not os.path.exists(release_dir):
        os.makedirs(release_dir)
    
    # 复制可执行文件到发布目录
    exe_name = "intelligent_file_classifier.exe" if platform.system().lower() == "windows" else "intelligent_file_classifier"
    exe_path = os.path.join("dist", exe_name)
    
    if os.path.exists(exe_path):
        shutil.copy(exe_path, release_dir)
        print(f"可执行文件已构建并复制到 {release_dir} 目录")
    else:
        print(f"错误：未找到构建的可执行文件 {exe_path}")
        return False
    
    return True

if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
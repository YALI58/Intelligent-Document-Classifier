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
    
    # 创建发布目录
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    if not os.path.exists("build"):
        os.makedirs("build")
    
    # 确定系统类型
    system = platform.system().lower()
    
    # 构建命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=智能文件分类器",
        "--onefile",
        "--windowed",
        "--clean",
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",
        "--add-data=README.md{}README.md".format(os.pathsep),
        "--add-data=使用指南.md{}使用指南.md".format(os.pathsep),
        "main.py"
    ]
    
    # 过滤掉空字符串
    cmd = [item for item in cmd if item]
    
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    # 创建发布包
    release_dir = "release"
    if not os.path.exists(release_dir):
        os.makedirs(release_dir)
    
    # 复制可执行文件到发布目录
    exe_name = "智能文件分类器.exe" if system == "windows" else "智能文件分类器"
    exe_path = os.path.join("dist", exe_name)
    
    if os.path.exists(exe_path):
        shutil.copy(exe_path, release_dir)
        
        # 创建安装说明
        with open(os.path.join(release_dir, "安装说明.txt"), "w", encoding="utf-8") as f:
            f.write("智能文件分类器 v1.1\n")
            f.write("===================\n\n")
            f.write("安装说明：\n")
            f.write("1. 解压本压缩包到任意位置\n")
            f.write("2. 双击运行「智能文件分类器」可执行文件\n")
            f.write("3. 首次运行时可能需要允许系统权限\n\n")
            f.write("使用说明请参考程序内的「帮助」菜单或随附的使用指南文档。\n")
        
        print(f"可执行文件已构建并复制到 {release_dir} 目录")
        print(f"请将 {release_dir} 目录打包为ZIP文件以便分发")
    else:
        print(f"错误：未找到构建的可执行文件 {exe_path}")
        return False
    
    return True

if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1) 
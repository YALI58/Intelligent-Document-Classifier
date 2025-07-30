#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标志文件功能演示脚本
展示如何使用标志文件来保护特定文件夹不被分类
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
import threading
from pathlib import Path

def create_real_demo():
    """创建真实的演示环境"""
    print("🎯 创建真实使用演示环境...")
    
    # 创建演示目录
    demo_root = Path("真实使用演示")
    if demo_root.exists():
        shutil.rmtree(demo_root)
    
    demo_root.mkdir()
    
    # 创建源文件夹
    source_dir = demo_root / "待分类文件"
    source_dir.mkdir()
    
    # 创建目标文件夹
    target_dir = demo_root / "分类结果"
    target_dir.mkdir()
    
    print(f"📁 源文件夹: {source_dir}")
    print(f"📁 目标文件夹: {target_dir}")
    
    # 创建各种类型的文件和文件夹
    files_structure = {
        # 普通文件 - 应该被分类
        "家庭照片.jpg": "图片内容",
        "工作文档.pdf": "PDF内容", 
        "音乐文件.mp3": "音乐内容",
        "压缩包.zip": "压缩文件内容",
        
        # 普通文件夹 - 内容应该被分类
        "下载的图片/风景1.jpg": "风景图片",
        "下载的图片/风景2.png": "风景图片",
        "临时文档/报告.docx": "报告内容",
        "临时文档/表格.xlsx": "表格内容",
        
        # 重要项目文件夹 - 应该被保护
        "重要的Python项目/main.py": "print('这是重要的项目代码')",
        "重要的Python项目/config.json": '{"project": "important", "version": "1.0"}',
        "重要的Python项目/requirements.txt": "requests>=2.25.0\nnumpy>=1.20.0",
        "重要的Python项目/src/utils.py": "def important_function(): pass",
        "重要的Python项目/tests/test_main.py": "import unittest",
        "重要的Python项目/docs/README.md": "# 重要项目\n这是一个重要的项目",
        
        # 软件安装目录 - 应该被保护
        "我的软件/MyApp.exe": "模拟的可执行文件",
        "我的软件/config.ini": "[Settings]\nversion=2.1\nlanguage=zh-CN",
        "我的软件/library.dll": "模拟的动态链接库",
        "我的软件/plugins/扩展1.dll": "插件文件",
        "我的软件/plugins/扩展2.dll": "插件文件",
        "我的软件/data/userdata.db": "用户数据库",
        "我的软件/data/cache.tmp": "缓存文件",
        
        # 游戏目录 - 应该被保护
        "我的游戏/game.exe": "游戏可执行文件",
        "我的游戏/assets/textures/texture1.png": "游戏纹理",
        "我的游戏/assets/sounds/bgm.ogg": "背景音乐",
        "我的游戏/saves/save1.dat": "游戏存档",
        "我的游戏/saves/save2.dat": "游戏存档",
        "我的游戏/mods/mod1.zip": "游戏模组",
    }
    
    # 创建文件结构
    for file_path, content in files_structure.items():
        full_path = source_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        print(f"📄 创建: {file_path}")
    
    print(f"\n✅ 演示环境创建完成！")
    print(f"📊 总共创建了 {len(files_structure)} 个文件")
    
    return source_dir, target_dir

def demonstrate_step_by_step():
    """分步演示标志文件功能"""
    print("\n" + "="*60)
    print("分步演示标志文件功能")
    print("="*60)
    
    # 第一步：创建演示环境
    print("\n📋 第1步：创建演示环境")
    source_dir, target_dir = create_real_demo()
    
    # 第二步：导入分类器
    print("\n📋 第2步：初始化文件分类器")
    try:
        from file_classifier_enhanced import EnhancedFileClassifier
        classifier = EnhancedFileClassifier()
        print("✅ 成功导入增强版文件分类器")
    except ImportError:
        print("❌ 无法导入增强版分类器，请检查文件是否存在")
        return
    
    # 第三步：首次扫描（无保护）
    print("\n📋 第3步：首次扫描所有文件")
    classifier.respect_flag_file = True
    all_files = classifier._get_files_from_source(source_dir)
    print(f"🔍 扫描结果：找到 {len(all_files)} 个文件")
    
    # 按目录分组显示
    from collections import defaultdict
    files_by_dir = defaultdict(list)
    for file in all_files:
        parent = file.parent.relative_to(source_dir)
        files_by_dir[str(parent)].append(file.name)
    
    for dir_name, files in sorted(files_by_dir.items()):
        print(f"  📁 {dir_name}/")
        for file in sorted(files):
            print(f"    📄 {file}")
    
    # 第四步：添加标志文件
    print("\n📋 第4步：为重要目录添加标志文件")
    protected_dirs = [
        source_dir / "重要的Python项目",
        source_dir / "我的软件", 
        source_dir / "我的游戏"
    ]
    
    for protected_dir in protected_dirs:
        flag_file = protected_dir / ".noclassify"
        flag_content = f"""这是标志文件
目录: {protected_dir.name}
保护原因: 保持文件结构完整性
创建时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        flag_file.write_text(flag_content, encoding='utf-8')
        print(f"  🛡️  {protected_dir.name}/.noclassify")
    
    # 第五步：重新扫描（有保护）
    print("\n📋 第5步：重新扫描（考虑标志文件）")
    protected_files = classifier._get_files_from_source(source_dir)
    print(f"🔍 扫描结果：找到 {len(protected_files)} 个文件")
    
    print(f"\n📊 对比结果：")
    print(f"  • 无保护时：{len(all_files)} 个文件")
    print(f"  • 有保护时：{len(protected_files)} 个文件")
    print(f"  • 受保护的文件：{len(all_files) - len(protected_files)} 个")
    
    print(f"\n🛡️  受保护的目录：")
    for protected_dir in protected_dirs:
        print(f"  📁 {protected_dir.name}/ - 已跳过")
    
    print(f"\n📄 剩余可分类的文件：")
    files_by_dir = defaultdict(list)
    for file in protected_files:
        parent = file.parent.relative_to(source_dir)
        files_by_dir[str(parent)].append(file.name)
    
    for dir_name, files in sorted(files_by_dir.items()):
        if dir_name != ".":
            print(f"  📁 {dir_name}/")
        for file in sorted(files):
            if dir_name == ".":
                print(f"  📄 {file}")
            else:
                print(f"    📄 {file}")
    
    # 第六步：模拟分类预览
    print("\n📋 第6步：模拟文件分类预览")
    print("如果现在执行分类，文件将被移动到以下位置：")
    
    # 模拟分类逻辑
    classification_preview = {
        "images": [],
        "documents": [], 
        "audio": [],
        "archives": [],
        "others": []
    }
    
    for file in protected_files:
        ext = file.suffix.lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif']:
            classification_preview["images"].append(file.name)
        elif ext in ['.pdf', '.docx', '.xlsx']:
            classification_preview["documents"].append(file.name)
        elif ext in ['.mp3', '.wav', '.ogg']:
            classification_preview["audio"].append(file.name)
        elif ext in ['.zip', '.rar']:
            classification_preview["archives"].append(file.name)
        else:
            classification_preview["others"].append(file.name)
    
    for category, files in classification_preview.items():
        if files:
            print(f"  📁 {category}/")
            for file in sorted(files):
                print(f"    📄 {file}")
    
    # 第七步：清理演示
    print("\n📋 第7步：清理演示环境")
    demo_root = source_dir.parent
    try:
        shutil.rmtree(demo_root)
        print(f"🧹 演示目录已清理: {demo_root}")
    except Exception as e:
        print(f"❌ 清理失败: {e}")
    
    print("\n✅ 演示完成！")
    print("\n💡 关键要点：")
    print("1. 标志文件 (.noclassify) 可以保护整个目录树")
    print("2. 被保护的目录及其子目录完全跳过分类")
    print("3. 普通文件和未保护的目录正常分类")
    print("4. 可以灵活地选择哪些目录需要保护")

def show_settings_demo():
    """展示设置界面中的标志文件配置"""
    print("\n" + "="*60)
    print("设置界面演示")
    print("="*60)
    
    print("\n在实际使用中，您可以通过以下方式配置标志文件：")
    print("\n1. 打开智能文件分类器")
    print("2. 点击菜单栏的 '设置' 按钮")
    print("3. 在设置对话框中选择 '高级设置' 标签页")
    print("4. 找到 '标志文件设置' 部分")
    print("5. 配置以下选项：")
    print("   ✅ 启用标志文件功能")
    print("   📝 标志文件名称: .noclassify")
    print("6. 点击 '保存' 按钮")
    
    print("\n📋 配置说明：")
    print("• 启用/禁用：控制是否检查标志文件")
    print("• 文件名称：自定义标志文件的名称")
    print("• 实时生效：设置保存后立即生效")

def main():
    """主演示函数"""
    print("🎯 智能文件分类器 - 标志文件功能实际使用演示")
    print("这个演示将展示如何在真实场景中使用标志文件功能")
    
    # 分步演示
    demonstrate_step_by_step()
    
    # 设置演示
    show_settings_demo()
    
    print("\n🎉 演示结束！现在您可以在实际项目中使用标志文件功能了。")

if __name__ == "__main__":
    main()
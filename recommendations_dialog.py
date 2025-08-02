#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能推荐对话框
提供分类建议、清理建议和整理提醒的用户界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from intelligent_recommendations import IntelligentRecommendationEngine

class RecommendationsDialog:
    """智能推荐对话框"""
    
    def __init__(self, parent, initial_directory: str = ""):
        self.parent = parent
        self.recommendation_engine = IntelligentRecommendationEngine()
        self.current_directory = initial_directory
        self.current_report = None
        
        # 导入分类器，用于一键执行
        try:
            from file_classifier_enhanced import EnhancedFileClassifier
            self.classifier = EnhancedFileClassifier()
        except ImportError:
            from file_classifier import FileClassifier
            self.classifier = FileClassifier()
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("智能推荐助手")
        self.dialog.geometry("900x700")
        self.dialog.resizable(True, True)
        
        # 设置窗口图标和属性
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # 如果提供了初始目录，立即分析
        if initial_directory and os.path.exists(initial_directory):
            self.analyze_directory()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 目录选择框架
        self.setup_directory_frame(main_frame)
        
        # 分析按钮框架
        self.setup_analysis_frame(main_frame)
        
        # 结果展示框架
        self.setup_results_frame(main_frame)
        
        # 底部按钮框架
        self.setup_button_frame(main_frame)
    
    def setup_directory_frame(self, parent):
        """设置目录选择框架"""
        dir_frame = ttk.LabelFrame(parent, text="📁 分析目录", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 目录路径输入
        path_frame = ttk.Frame(dir_frame)
        path_frame.pack(fill=tk.X)
        
        ttk.Label(path_frame, text="目录路径:").pack(side=tk.LEFT)
        
        self.directory_var = tk.StringVar(value=self.current_directory)
        self.directory_entry = ttk.Entry(path_frame, textvariable=self.directory_var)
        self.directory_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        ttk.Button(path_frame, text="浏览", command=self.browse_directory).pack(side=tk.RIGHT)
    
    def setup_analysis_frame(self, parent):
        """设置分析按钮框架"""
        analysis_frame = ttk.Frame(parent)
        analysis_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.analyze_btn = ttk.Button(
            analysis_frame, 
            text="🔍 开始智能分析", 
            command=self.analyze_directory,
            style="Accent.TButton"
        )
        self.analyze_btn.pack(side=tk.LEFT)
        
        self.progress_var = tk.StringVar(value="就绪")
        self.progress_label = ttk.Label(analysis_frame, textvariable=self.progress_var)
        self.progress_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # 进度条
        self.progress_bar = ttk.Progressbar(analysis_frame, mode='indeterminate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
    
    def setup_results_frame(self, parent):
        """设置结果展示框架"""
        # 创建笔记本控件用于分页显示
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 汇总页面
        self.setup_summary_tab()
        
        # 清理建议页面
        self.setup_cleanup_tab()
        
        # 整理提醒页面
        self.setup_reminders_tab()
        
        # 分类建议页面
        self.setup_classification_tab()
    
    def setup_summary_tab(self):
        """设置汇总页面"""
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="📊 分析汇总")
        
        # 滚动区域
        canvas = tk.Canvas(summary_frame)
        scrollbar = ttk.Scrollbar(summary_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.summary_content = scrollable_frame
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_cleanup_tab(self):
        """设置清理建议页面"""
        cleanup_frame = ttk.Frame(self.notebook)
        self.notebook.add(cleanup_frame, text="🧹 清理建议")
        
        # 子标签页
        cleanup_notebook = ttk.Notebook(cleanup_frame)
        cleanup_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 重复文件
        self.duplicates_tree = self.create_tree_tab(
            cleanup_notebook, "🔄 重复文件", 
            ["文件路径", "大小", "原始文件", "操作"]
        )
        
        # 临时文件
        self.temp_files_tree = self.create_tree_tab(
            cleanup_notebook, "🗑️ 临时文件",
            ["文件路径", "大小", "类型", "操作"]
        )
        
        # 大文件
        self.large_files_tree = self.create_tree_tab(
            cleanup_notebook, "📦 大文件",
            ["文件路径", "大小(MB)", "建议", "操作"]
        )
        
        # 旧文件
        self.old_files_tree = self.create_tree_tab(
            cleanup_notebook, "📅 旧文件",
            ["文件路径", "天数", "大小", "操作"]
        )
    
    def setup_reminders_tab(self):
        """设置整理提醒页面"""
        reminders_frame = ttk.Frame(self.notebook)
        self.notebook.add(reminders_frame, text="⚠️ 整理提醒")
        
        # 创建树形视图
        columns = ("优先级", "类型", "描述", "建议")
        self.reminders_tree = ttk.Treeview(reminders_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            self.reminders_tree.heading(col, text=col)
            self.reminders_tree.column(col, width=150)
        
        # 滚动条
        reminders_scrollbar = ttk.Scrollbar(reminders_frame, orient="vertical", command=self.reminders_tree.yview)
        self.reminders_tree.configure(yscrollcommand=reminders_scrollbar.set)
        
        self.reminders_tree.pack(side="left", fill="both", expand=True)
        reminders_scrollbar.pack(side="right", fill="y")
        
        # 绑定双击事件
        self.reminders_tree.bind("<Double-1>", self.on_reminder_double_click)
    
    def setup_classification_tab(self):
        """设置分类建议页面"""
        classification_frame = ttk.Frame(self.notebook)
        self.notebook.add(classification_frame, text="🎯 分类建议")
        
        # 文件选择框架
        file_frame = ttk.LabelFrame(classification_frame, text="选择文件获取分类建议", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        file_input_frame = ttk.Frame(file_frame)
        file_input_frame.pack(fill=tk.X)
        
        self.selected_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_input_frame, textvariable=self.selected_file_var)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(file_input_frame, text="选择文件", command=self.select_file_for_classification).pack(side=tk.RIGHT)
        
        # 建议列表
        suggestions_frame = ttk.LabelFrame(classification_frame, text="分类建议", padding="10")
        suggestions_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("位置", "置信度", "原因", "类型")
        self.suggestions_tree = ttk.Treeview(suggestions_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.suggestions_tree.heading(col, text=col)
            self.suggestions_tree.column(col, width=120)
        
        suggestions_scrollbar = ttk.Scrollbar(suggestions_frame, orient="vertical", command=self.suggestions_tree.yview)
        self.suggestions_tree.configure(yscrollcommand=suggestions_scrollbar.set)
        
        self.suggestions_tree.pack(side="left", fill="both", expand=True)
        suggestions_scrollbar.pack(side="right", fill="y")
    
    def create_tree_tab(self, parent, tab_name: str, columns: List[str]):
        """创建树形视图标签页"""
        frame = ttk.Frame(parent)
        parent.add(frame, text=tab_name)
        
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定右键菜单
        tree.bind("<Button-3>", lambda e: self.show_context_menu(e, tree))
        
        return tree
    
    def setup_button_frame(self, parent):
        """设置底部按钮框架"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        # 左侧按钮
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        ttk.Button(left_buttons, text="导出报告", command=self.export_report).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_buttons, text="刷新分析", command=self.analyze_directory).pack(side=tk.LEFT, padx=(0, 5))
        
        # 中间按钮 - 一键执行
        center_buttons = ttk.Frame(button_frame)
        center_buttons.pack(side=tk.LEFT, padx=(20, 0))
        
        self.execute_btn = ttk.Button(
            center_buttons, 
            text="🚀 一键执行推荐", 
            command=self.execute_recommendations,
            style="Accent.TButton"
        )
        self.execute_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 初始状态禁用，等有分析结果后启用
        self.execute_btn.configure(state="disabled")
        
        # 右侧按钮
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, text="关闭", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def browse_directory(self):
        """浏览选择目录"""
        directory = filedialog.askdirectory(
            title="选择要分析的目录",
            initialdir=self.current_directory
        )
        if directory:
            self.directory_var.set(directory)
            self.current_directory = directory
    
    def analyze_directory(self):
        """分析目录"""
        directory = self.directory_var.get().strip()
        if not directory or not os.path.exists(directory):
            messagebox.showerror("错误", "请选择有效的目录路径")
            return
        
        self.current_directory = directory
        
        # 在后台线程中执行分析
        self.analyze_btn.configure(state="disabled")
        self.progress_var.set("正在分析...")
        self.progress_bar.start()
        
        thread = threading.Thread(target=self._analyze_directory_thread)
        thread.daemon = True
        thread.start()
    
    def _analyze_directory_thread(self):
        """后台分析线程"""
        try:
            # 生成推荐报告
            self.current_report = self.recommendation_engine.generate_recommendations_report(self.current_directory)
            
            # 在主线程中更新界面
            self.dialog.after(0, self._update_results)
            
        except Exception as e:
            self.dialog.after(0, lambda: self._analysis_error(str(e)))
    
    def _update_results(self):
        """更新分析结果界面"""
        if not self.current_report:
            return
        
        # 更新汇总页面
        self.update_summary_tab()
        
        # 更新清理建议
        self.update_cleanup_tabs()
        
        # 更新整理提醒
        self.update_reminders_tab()
        
        # 停止进度条
        self.progress_bar.stop()
        self.progress_var.set("分析完成")
        self.analyze_btn.configure(state="normal")
        self.execute_btn.configure(state="normal") # 启用一键执行按钮
        
        messagebox.showinfo("完成", "智能分析已完成！请查看各个页面的建议。")
    
    def _analysis_error(self, error_msg: str):
        """处理分析错误"""
        self.progress_bar.stop()
        self.progress_var.set("分析失败")
        self.analyze_btn.configure(state="normal")
        self.execute_btn.configure(state="disabled") # 禁用一键执行按钮
        messagebox.showerror("分析失败", f"分析过程中出现错误：{error_msg}")
    
    def update_summary_tab(self):
        """更新汇总页面"""
        # 清除现有内容
        for widget in self.summary_content.winfo_children():
            widget.destroy()
        
        if not self.current_report:
            return
        
        summary = self.current_report.get('summary', {})
        
        # 总体统计
        stats_frame = ttk.LabelFrame(self.summary_content, text="📈 总体统计", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        stats_text = f"""
📁 分析目录: {self.current_report.get('directory', 'N/A')}
🕐 分析时间: {datetime.fromisoformat(self.current_report.get('timestamp', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M:%S')}

🔄 重复文件: {summary.get('total_duplicates', 0)} 个
🗑️ 临时文件: {summary.get('total_temp_files', 0)} 个
📦 大文件: {summary.get('total_large_files', 0)} 个
📅 旧文件: {summary.get('total_old_files', 0)} 个
📝 空文件: {summary.get('total_empty_files', 0)} 个
⚠️ 整理提醒: {summary.get('reminder_count', 0)} 个

💾 潜在节省空间: {summary.get('potential_space_savings_mb', 0)} MB
        """.strip()
        
        ttk.Label(stats_frame, text=stats_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # 推荐操作
        recommendations = self.current_report.get('recommendations', [])
        if recommendations:
            rec_frame = ttk.LabelFrame(self.summary_content, text="🎯 推荐操作", padding="10")
            rec_frame.pack(fill=tk.X)
            
            for i, rec in enumerate(recommendations[:5], 1):
                priority_color = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec.get('priority', 'low'), '⚪')
                rec_text = f"{i}. {priority_color} {rec.get('description', 'N/A')} - {rec.get('impact', 'N/A')}"
                ttk.Label(rec_frame, text=rec_text, justify=tk.LEFT).pack(anchor=tk.W, pady=2)
    
    def update_cleanup_tabs(self):
        """更新清理建议标签页"""
        if not self.current_report:
            return
        
        cleanup = self.current_report.get('cleanup_suggestions', {})
        
        # 更新重复文件
        self.update_tree_data(self.duplicates_tree, cleanup.get('duplicates', []), 
                             lambda item: [
                                 os.path.basename(item['path']),
                                 f"{item['size'] / 1024:.1f} KB",
                                 os.path.basename(item.get('original', 'N/A')),
                                 "删除"
                             ])
        
        # 更新临时文件
        self.update_tree_data(self.temp_files_tree, cleanup.get('temp_files', []),
                             lambda item: [
                                 os.path.basename(item['path']),
                                 f"{item['size'] / 1024:.1f} KB",
                                 item.get('reason', 'N/A'),
                                 "删除"
                             ])
        
        # 更新大文件
        self.update_tree_data(self.large_files_tree, cleanup.get('large_files', []),
                             lambda item: [
                                 os.path.basename(item['path']),
                                 f"{item.get('size_mb', 0):.1f}",
                                 item.get('reason', 'N/A'),
                                 "归档"
                             ])
        
        # 更新旧文件
        self.update_tree_data(self.old_files_tree, cleanup.get('old_files', []),
                             lambda item: [
                                 os.path.basename(item['path']),
                                 str(item.get('days_old', 0)),
                                 f"{item['size'] / 1024:.1f} KB",
                                 "归档"
                             ])
    
    def update_reminders_tab(self):
        """更新整理提醒页面"""
        # 清除现有数据
        for item in self.reminders_tree.get_children():
            self.reminders_tree.delete(item)
        
        if not self.current_report:
            return
        
        reminders = self.current_report.get('organization_reminders', [])
        
        for reminder in reminders:
            priority = reminder.get('priority', 'low')
            priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '⚪')
            
            self.reminders_tree.insert('', 'end', values=[
                f"{priority_icon} {priority.upper()}",
                reminder.get('type', 'N/A'),
                reminder.get('message', 'N/A'),
                reminder.get('suggestion', 'N/A')
            ])
    
    def update_tree_data(self, tree, data, value_func):
        """更新树形视图数据"""
        # 清除现有数据
        for item in tree.get_children():
            tree.delete(item)
        
        # 添加新数据
        for item in data:
            values = value_func(item)
            tree.insert('', 'end', values=values)
    
    def select_file_for_classification(self):
        """选择文件进行分类建议"""
        file_path = filedialog.askopenfilename(
            title="选择文件",
            initialdir=self.current_directory
        )
        
        if file_path:
            self.selected_file_var.set(file_path)
            self.get_classification_suggestions(file_path)
    
    def get_classification_suggestions(self, file_path: str):
        """获取文件分类建议"""
        # 模拟可能的位置列表
        possible_locations = [
            "Documents/工作文档",
            "Documents/个人文档",
            "Pictures/照片",
            "Downloads/下载",
            "Archive/归档",
            "Projects/项目",
            "Media/媒体文件"
        ]
        
        suggestions = self.recommendation_engine.get_classification_suggestions(
            file_path, possible_locations
        )
        
        # 清除现有建议
        for item in self.suggestions_tree.get_children():
            self.suggestions_tree.delete(item)
        
        # 添加新建议
        for suggestion in suggestions:
            confidence_percent = f"{suggestion['confidence'] * 100:.0f}%"
            self.suggestions_tree.insert('', 'end', values=[
                suggestion['location'],
                confidence_percent,
                suggestion['reason'],
                suggestion['type']
            ])
    
    def show_context_menu(self, event, tree):
        """显示右键菜单"""
        item = tree.selection()[0] if tree.selection() else None
        if not item:
            return
        
        context_menu = tk.Menu(self.dialog, tearoff=0)
        context_menu.add_command(label="查看详情", command=lambda: self.show_item_details(tree, item))
        context_menu.add_command(label="执行操作", command=lambda: self.execute_action(tree, item))
        context_menu.add_separator()
        context_menu.add_command(label="忽略此项", command=lambda: tree.delete(item))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def show_item_details(self, tree, item):
        """显示项目详情"""
        values = tree.item(item)['values']
        details = f"详细信息:\n" + "\n".join([f"{col}: {val}" for col, val in zip(tree['columns'], values)])
        messagebox.showinfo("详情", details)
    
    def execute_action(self, tree, item):
        """执行操作"""
        # 这里可以实现具体的操作逻辑
        messagebox.showinfo("操作", "操作功能待实现")
    
    def on_reminder_double_click(self, event):
        """处理提醒双击事件"""
        item = self.reminders_tree.selection()[0] if self.reminders_tree.selection() else None
        if item:
            self.show_item_details(self.reminders_tree, item)
    
    def execute_recommendations(self):
        """一键执行智能推荐"""
        if not self.current_report:
            messagebox.showwarning("警告", "请先进行智能分析")
            return
        
        # 确认对话框
        confirm_msg = "即将执行以下操作：\n\n"
        operations_count = 0
        
        # 获取清理建议数据
        cleanup_suggestions = self.current_report.get('cleanup_suggestions', {})
        
        # 统计要执行的操作
        duplicates = cleanup_suggestions.get('duplicates', [])
        if duplicates:
            confirm_msg += f"• 删除 {len(duplicates)} 个重复文件\n"
            operations_count += len(duplicates)
        
        temp_files = cleanup_suggestions.get('temp_files', [])
        if temp_files:
            confirm_msg += f"• 清理 {len(temp_files)} 个临时文件\n"
            operations_count += len(temp_files)
        
        empty_files = cleanup_suggestions.get('empty_files', [])
        if empty_files:
            confirm_msg += f"• 删除 {len(empty_files)} 个空文件\n"
            operations_count += len(empty_files)
        
        # 智能分类
        if self.current_directory:
            confirm_msg += f"• 对目录 {self.current_directory} 进行智能分类整理\n"
            operations_count += 1
        
        if operations_count == 0:
            messagebox.showinfo("提示", "没有可执行的推荐操作")
            return
        
        confirm_msg += f"\n总共 {operations_count} 个操作，是否继续？\n\n"
        confirm_msg += "⚠️ 建议在执行前备份重要文件"
        
        if not messagebox.askyesno("确认执行", confirm_msg):
            return
        
        # 在后台线程中执行操作
        self.execute_btn.configure(state="disabled")
        self.progress_var.set("正在执行推荐操作...")
        self.progress_bar.start()
        
        thread = threading.Thread(target=self._execute_recommendations_thread)
        thread.daemon = True
        thread.start()
    
    def _execute_recommendations_thread(self):
        """在后台线程中执行推荐操作"""
        try:
            results = {
                'duplicates_removed': 0,
                'temp_files_cleaned': 0,
                'empty_files_removed': 0,
                'files_classified': 0,
                'errors': []
            }
            
            # 获取清理建议数据
            cleanup_suggestions = self.current_report.get('cleanup_suggestions', {})
            
            # 1. 清理重复文件
            duplicates = cleanup_suggestions.get('duplicates', [])
            if duplicates:
                results['duplicates_removed'] = self._remove_duplicate_files(duplicates)
            
            # 2. 清理临时文件
            temp_files = cleanup_suggestions.get('temp_files', [])
            if temp_files:
                results['temp_files_cleaned'] = self._clean_temp_files(temp_files)
            
            # 3. 清理空文件
            empty_files = cleanup_suggestions.get('empty_files', [])
            if empty_files:
                results['empty_files_removed'] = self._clean_empty_files(empty_files)
            
            # 4. 执行智能分类
            if self.current_directory:
                results['files_classified'] = self._execute_smart_classification()
            
            # 更新UI
            self.dialog.after(0, lambda: self._on_execution_complete(results))
            
        except Exception as e:
            error_msg = str(e)
            self.dialog.after(0, lambda: self._on_execution_error(error_msg))
    
    def _remove_duplicate_files(self, duplicates: List[Dict]) -> int:
        """移除重复文件"""
        removed_count = 0
        
        for duplicate_file in duplicates:
            try:
                file_path = duplicate_file['path']
                import send2trash
                send2trash.send2trash(file_path)
                removed_count += 1
                print(f"删除重复文件: {file_path}")
            except Exception as e:
                print(f"删除重复文件失败 {file_path}: {e}")
        
        return removed_count
    
    def _clean_temp_files(self, temp_files: List[Dict]) -> int:
        """清理临时文件"""
        cleaned_count = 0
        for temp_file in temp_files:
            try:
                import send2trash
                send2trash.send2trash(temp_file['path'])
                cleaned_count += 1
            except Exception as e:
                print(f"清理临时文件失败 {temp_file['path']}: {e}")
        
        return cleaned_count
    
    def _clean_empty_files(self, empty_files: List[Dict]) -> int:
        """清理空文件"""
        removed_count = 0
        for empty_file in empty_files:
            try:
                import os
                os.remove(empty_file['path'])
                removed_count += 1
            except Exception as e:
                print(f"清理空文件失败 {empty_file['path']}: {e}")
        
        return removed_count
    
    def _execute_smart_classification(self):
        """执行智能分类"""
        try:
            # 创建目标文件夹
            target_path = os.path.join(self.current_directory, "智能整理结果")
            
            # 使用分类器进行智能分类
            if hasattr(self.classifier, 'classify_files_with_associations'):
                # 使用增强版分类器
                results = self.classifier.classify_files_with_associations(
                    self.current_directory, 
                    target_path, 
                    ['by_type', 'by_date'],  # 按类型和日期分类
                    'move',  # 移动文件
                    preserve_associations=True
                )
            else:
                # 使用基础分类器
                results = self.classifier.classify_files(
                    self.current_directory, 
                    target_path, 
                    ['by_type', 'by_date'], 
                    'move'
                )
            
            return len([r for r in results if r.get('success', False)])
            
        except Exception as e:
            print(f"智能分类失败: {e}")
            return 0
    
    def _on_execution_complete(self, results):
        """执行完成的回调"""
        self.progress_bar.stop()
        self.progress_var.set("执行完成")
        self.execute_btn.configure(state="normal")
        
        # 显示结果
        result_msg = "一键执行完成！\n\n"
        result_msg += f"• 删除重复文件: {results['duplicates_removed']} 个\n"
        result_msg += f"• 清理临时文件: {results['temp_files_cleaned']} 个\n"
        result_msg += f"• 清理空文件: {results['empty_files_removed']} 个\n"
        result_msg += f"• 分类整理文件: {results['files_classified']} 个\n"
        
        if results['errors']:
            result_msg += f"\n⚠️ 遇到 {len(results['errors'])} 个错误"
        
        messagebox.showinfo("执行完成", result_msg)
        
        # 刷新分析结果
        self.analyze_directory()
    
    def _on_execution_error(self, error_msg):
        """执行错误的回调"""
        self.progress_bar.stop()
        self.progress_var.set("执行失败")
        self.execute_btn.configure(state="normal")
        
        messagebox.showerror("执行失败", f"执行推荐操作时出现错误：\n{error_msg}")
    
    def export_report(self):
        """导出分析报告"""
        if not self.current_report:
            messagebox.showwarning("警告", "没有可导出的报告")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="导出报告",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_report, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"报告已导出到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {e}")

def show_recommendations_dialog(parent, directory: str = ""):
    """显示智能推荐对话框"""
    dialog = RecommendationsDialog(parent, directory)
    return dialog 
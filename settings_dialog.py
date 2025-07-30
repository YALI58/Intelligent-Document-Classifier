#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置对话框模块
提供高级配置选项和自定义规则管理
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Any

class SettingsDialog:
    """设置对话框类"""
    
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.dialog = None
        self.custom_rules = []
        self.file_type_mapping = {}
        
        self.create_dialog()
        
    def create_dialog(self):
        """创建对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("高级设置")
        self.dialog.geometry("800x700")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 创建笔记本控件
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建各个标签页
        self.create_file_type_tab(notebook)
        self.create_custom_rules_tab(notebook)
        self.create_advanced_tab(notebook)
        self.create_exclude_tab(notebook)
        self.create_association_tab(notebook)
        
        # 按钮框架
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="保存", 
                  command=self.save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="重置", 
                  command=self.reset_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="导入配置", 
                  command=self.import_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="导出配置", 
                  command=self.export_config).pack(side=tk.LEFT, padx=5)
        
        # 加载当前设置
        self.load_settings()
        
        # 居中显示
        self.center_dialog()
        
    def create_file_type_tab(self, notebook):
        """创建文件类型映射标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="文件类型")
        
        # 说明标签
        info_label = ttk.Label(frame, text="配置不同文件扩展名对应的分类文件夹")
        info_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # 创建滚动框架
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.type_frame = ttk.Frame(canvas)
        
        self.type_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.type_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # 存储文件类型映射控件
        self.type_entries = {}
        
    def populate_file_type_mapping(self):
        """填充文件类型映射"""
        # 清空现有控件
        for widget in self.type_frame.winfo_children():
            widget.destroy()
            
        self.type_entries.clear()
        
        row = 0
        for type_name, extensions in self.file_type_mapping.items():
            # 类型名标签
            ttk.Label(self.type_frame, text=f"{type_name}:").grid(
                row=row, column=0, sticky=tk.W, padx=5, pady=2
            )
            
            # 扩展名输入框
            extensions_str = ', '.join(extensions)
            entry = ttk.Entry(self.type_frame, width=60)
            entry.insert(0, extensions_str)
            entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
            
            self.type_entries[type_name] = entry
            self.type_frame.columnconfigure(1, weight=1)
            
            row += 1
            
    def create_custom_rules_tab(self, notebook):
        """创建自定义规则标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="自定义规则")
        
        # 说明标签
        info_label = ttk.Label(frame, 
            text="创建基于文件名模式的自定义分类规则\n"
                 "支持通配符: * (任意字符) ? (单个字符)")
        info_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # 规则列表框架
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 规则列表
        columns = ("启用", "名称", "模式", "目标文件夹", "描述")
        self.rules_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        column_widths = {"启用": 50, "名称": 100, "模式": 120, "目标文件夹": 150, "描述": 200}
        for col in columns:
            self.rules_tree.heading(col, text=col)
            self.rules_tree.column(col, width=column_widths.get(col, 100))
            
        # 滚动条
        rules_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=rules_scrollbar.set)
        
        self.rules_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rules_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="添加规则", 
                  command=self.add_custom_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="编辑规则", 
                  command=self.edit_custom_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除规则", 
                  command=self.delete_custom_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="切换启用", 
                  command=self.toggle_rule_enabled).pack(side=tk.LEFT, padx=5)
                  
    def create_advanced_tab(self, notebook):
        """创建高级设置标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="高级设置")
        
        # 标志文件设置
        flag_frame = ttk.LabelFrame(frame, text="标志文件设置", padding="10")
        flag_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 启用标志文件
        self.respect_flag_file = tk.BooleanVar(value=True)
        ttk.Checkbutton(flag_frame, text="启用标志文件功能", 
                       variable=self.respect_flag_file).pack(anchor=tk.W)
        
        # 标志文件名称
        flag_name_frame = ttk.Frame(flag_frame)
        flag_name_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(flag_name_frame, text="标志文件名称:").pack(side=tk.LEFT)
        self.flag_file_name = tk.StringVar(value=".noclassify")
        flag_entry = ttk.Entry(flag_name_frame, textvariable=self.flag_file_name)
        flag_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # 说明文本
        info_text = """当文件夹中存在标志文件时，该文件夹及其子文件夹将被跳过不进行分类。
这对于保持某些特定文件夹的结构很有用，比如软件安装目录、项目文件夹等。
您可以通过在文件夹中创建一个名为".noclassify"（或自定义名称）的空文件来标记该文件夹。"""
        info_label = ttk.Label(flag_frame, text=info_text, wraplength=600, 
                             justify=tk.LEFT, foreground="gray")
        info_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 重复文件处理
        duplicate_frame = ttk.LabelFrame(frame, text="重复文件处理", padding=10)
        duplicate_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.duplicate_var = tk.StringVar()
        ttk.Radiobutton(duplicate_frame, text="重命名（推荐）", variable=self.duplicate_var, 
                       value="rename").pack(anchor=tk.W)
        ttk.Radiobutton(duplicate_frame, text="跳过", variable=self.duplicate_var, 
                       value="skip").pack(anchor=tk.W)
        ttk.Radiobutton(duplicate_frame, text="覆盖（危险）", variable=self.duplicate_var, 
                       value="overwrite").pack(anchor=tk.W)
        
        # 监控设置
        monitor_frame = ttk.LabelFrame(frame, text="监控设置", padding=10)
        monitor_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.monitor_subfolders_var = tk.BooleanVar()
        ttk.Checkbutton(monitor_frame, text="监控子文件夹", 
                       variable=self.monitor_subfolders_var).pack(anchor=tk.W)
        
        self.auto_start_monitoring_var = tk.BooleanVar()
        ttk.Checkbutton(monitor_frame, text="启动时自动开始监控", 
                       variable=self.auto_start_monitoring_var).pack(anchor=tk.W)
        
        # 监控延迟设置
        delay_frame = ttk.Frame(monitor_frame)
        delay_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(delay_frame, text="监控延迟 (秒):").pack(side=tk.LEFT)
        self.monitor_delay_var = tk.DoubleVar()
        delay_spin = ttk.Spinbox(delay_frame, from_=0.1, to=10.0, increment=0.1, 
                                textvariable=self.monitor_delay_var, width=10)
        delay_spin.pack(side=tk.LEFT, padx=5)
        
        # 性能设置
        performance_frame = ttk.LabelFrame(frame, text="性能设置", padding=10)
        performance_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.parallel_processing_var = tk.BooleanVar()
        ttk.Checkbutton(performance_frame, text="启用并行处理", 
                       variable=self.parallel_processing_var).pack(anchor=tk.W)
        
        workers_frame = ttk.Frame(performance_frame)
        workers_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(workers_frame, text="最大工作线程数:").pack(side=tk.LEFT)
        self.max_workers_var = tk.IntVar()
        workers_spin = ttk.Spinbox(workers_frame, from_=1, to=16, 
                                  textvariable=self.max_workers_var, width=10)
        workers_spin.pack(side=tk.LEFT, padx=5)
        
        # 其他设置
        other_frame = ttk.LabelFrame(frame, text="其他设置", padding=10)
        other_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.auto_create_folders_var = tk.BooleanVar()
        ttk.Checkbutton(other_frame, text="自动创建目标文件夹", 
                       variable=self.auto_create_folders_var).pack(anchor=tk.W)
        
        self.preserve_timestamps_var = tk.BooleanVar()
        ttk.Checkbutton(other_frame, text="保留文件时间戳", 
                       variable=self.preserve_timestamps_var).pack(anchor=tk.W)
        
        self.use_recycle_bin_var = tk.BooleanVar()
        ttk.Checkbutton(other_frame, text="删除文件时使用回收站", 
                       variable=self.use_recycle_bin_var).pack(anchor=tk.W)
        
    def create_exclude_tab(self, notebook):
        """创建排除设置标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="排除设置")
        
        # 说明标签
        info_label = ttk.Label(frame, text="设置要排除的文件模式和大小限制")
        info_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # 排除模式
        exclude_frame = ttk.LabelFrame(frame, text="排除模式", padding=10)
        exclude_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 排除模式列表
        list_frame = ttk.Frame(exclude_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.exclude_listbox = tk.Listbox(list_frame, height=8)
        exclude_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                         command=self.exclude_listbox.yview)
        self.exclude_listbox.configure(yscrollcommand=exclude_scrollbar.set)
        
        self.exclude_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        exclude_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 排除模式操作按钮
        exclude_btn_frame = ttk.Frame(exclude_frame)
        exclude_btn_frame.pack(fill=tk.X, pady=5)
        
        self.exclude_entry = ttk.Entry(exclude_btn_frame, width=30)
        self.exclude_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(exclude_btn_frame, text="添加", 
                  command=self.add_exclude_pattern).pack(side=tk.LEFT, padx=2)
        ttk.Button(exclude_btn_frame, text="删除", 
                  command=self.remove_exclude_pattern).pack(side=tk.LEFT, padx=2)
        
        # 文件大小限制
        size_frame = ttk.LabelFrame(frame, text="文件大小限制", padding=10)
        size_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 最小文件大小
        min_size_frame = ttk.Frame(size_frame)
        min_size_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(min_size_frame, text="最小文件大小 (字节):").pack(side=tk.LEFT)
        self.min_file_size_var = tk.IntVar()
        ttk.Entry(min_size_frame, textvariable=self.min_file_size_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # 最大文件大小
        max_size_frame = ttk.Frame(size_frame)
        max_size_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(max_size_frame, text="最大文件大小 (字节):").pack(side=tk.LEFT)
        self.max_file_size_var = tk.IntVar()
        ttk.Entry(max_size_frame, textvariable=self.max_file_size_var, width=15).pack(side=tk.LEFT, padx=5)
        
    def load_settings(self):
        """加载当前设置"""
        config = self.config_manager.load_config()
        
        # 加载标志文件设置
        flag_file_config = config.get('flag_file', {
            'enabled': True,
            'name': '.noclassify'
        })
        self.respect_flag_file.set(flag_file_config.get('enabled', True))
        self.flag_file_name.set(flag_file_config.get('name', '.noclassify'))
        
        # 加载文件类型映射
        self.file_type_mapping = config.get('file_type_mapping', {})
        self.populate_file_type_mapping()
        
        # 加载自定义规则
        self.custom_rules = config.get('custom_rules', [])
        self.populate_custom_rules()
        
        # 加载高级设置
        self.duplicate_var.set(config.get('handle_duplicates', 'rename'))
        self.monitor_subfolders_var.set(config.get('monitor_subfolders', True))
        self.auto_start_monitoring_var.set(config.get('auto_start_monitoring', False))
        self.monitor_delay_var.set(config.get('monitor_delay', 1.0))
        self.parallel_processing_var.set(config.get('parallel_processing', True))
        self.max_workers_var.set(config.get('max_workers', 4))
        self.auto_create_folders_var.set(config.get('auto_create_folders', True))
        self.preserve_timestamps_var.set(config.get('preserve_timestamps', True))
        self.use_recycle_bin_var.set(config.get('use_recycle_bin', True))
        
        # 加载排除设置
        exclude_patterns = config.get('exclude_patterns', [])
        self.exclude_listbox.delete(0, tk.END)
        for pattern in exclude_patterns:
            self.exclude_listbox.insert(tk.END, pattern)
            
        self.min_file_size_var.set(config.get('min_file_size', 0))
        self.max_file_size_var.set(config.get('max_file_size', 1024*1024*1024))
        
    def populate_custom_rules(self):
        """填充自定义规则"""
        # 清空现有项目
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
            
        # 添加规则
        for rule in self.custom_rules:
            enabled = "✓" if rule.get('enabled', True) else "✗"
            self.rules_tree.insert('', 'end', values=(
                enabled,
                rule.get('name', ''),
                rule.get('pattern', ''),
                rule.get('target_folder', ''),
                rule.get('description', '')
            ))
            
    def add_custom_rule(self):
        """添加自定义规则"""
        dialog = CustomRuleDialog(self.dialog)
        if dialog.result:
            self.custom_rules.append(dialog.result)
            self.populate_custom_rules()
            
    def edit_custom_rule(self):
        """编辑自定义规则"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的规则")
            return
            
        item = selection[0]
        index = self.rules_tree.index(item)
        
        current_rule = self.custom_rules[index]
        dialog = CustomRuleDialog(self.dialog, current_rule)
        
        if dialog.result:
            self.custom_rules[index] = dialog.result
            self.populate_custom_rules()
            
    def delete_custom_rule(self):
        """删除自定义规则"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的规则")
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的规则吗？"):
            item = selection[0]
            index = self.rules_tree.index(item)
            del self.custom_rules[index]
            self.populate_custom_rules()
            
    def toggle_rule_enabled(self):
        """切换规则启用状态"""
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要切换的规则")
            return
            
        item = selection[0]
        index = self.rules_tree.index(item)
        
        rule = self.custom_rules[index]
        rule['enabled'] = not rule.get('enabled', True)
        self.populate_custom_rules()
        
    def add_exclude_pattern(self):
        """添加排除模式"""
        pattern = self.exclude_entry.get().strip()
        if pattern:
            self.exclude_listbox.insert(tk.END, pattern)
            self.exclude_entry.delete(0, tk.END)
            
    def remove_exclude_pattern(self):
        """删除排除模式"""
        selection = self.exclude_listbox.curselection()
        if selection:
            self.exclude_listbox.delete(selection[0])
            
    def save_settings(self):
        """保存设置"""
        try:
            config = self.config_manager.load_config()
            
            # 保存标志文件设置
            config['flag_file'] = {
                'enabled': self.respect_flag_file.get(),
                'name': self.flag_file_name.get()
            }
            
            # 保存文件类型映射
            new_mapping = {}
            for type_name, entry in self.type_entries.items():
                extensions_str = entry.get().strip()
                if extensions_str:
                    extensions = [ext.strip() for ext in extensions_str.split(',')]
                    # 确保扩展名以点开头
                    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions if ext]
                    new_mapping[type_name] = extensions
                else:
                    new_mapping[type_name] = []
                    
            config['file_type_mapping'] = new_mapping
            
            # 保存自定义规则
            config['custom_rules'] = self.custom_rules
            
            # 保存高级设置
            config['handle_duplicates'] = self.duplicate_var.get()
            config['monitor_subfolders'] = self.monitor_subfolders_var.get()
            config['auto_start_monitoring'] = self.auto_start_monitoring_var.get()
            config['monitor_delay'] = self.monitor_delay_var.get()
            config['parallel_processing'] = self.parallel_processing_var.get()
            config['max_workers'] = self.max_workers_var.get()
            config['auto_create_folders'] = self.auto_create_folders_var.get()
            config['preserve_timestamps'] = self.preserve_timestamps_var.get()
            config['use_recycle_bin'] = self.use_recycle_bin_var.get()
            
            # 保存排除设置
            exclude_patterns = [self.exclude_listbox.get(i) for i in range(self.exclude_listbox.size())]
            config['exclude_patterns'] = exclude_patterns
            config['min_file_size'] = self.min_file_size_var.get()
            config['max_file_size'] = self.max_file_size_var.get()
            
            # 保存配置
            if self.config_manager.save_config(config):
                messagebox.showinfo("成功", "设置已保存")
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "保存设置失败")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")
            
    def reset_settings(self):
        """重置设置"""
        if messagebox.askyesno("确认", "确定要重置所有设置到默认值吗？"):
            if self.config_manager.reset_to_default():
                self.load_settings()
                messagebox.showinfo("成功", "设置已重置")
            else:
                messagebox.showerror("错误", "重置设置失败")
                
    def export_config(self):
        """导出配置"""
        filename = filedialog.asksaveasfilename(
            title="导出配置文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filename:
            if self.config_manager.export_config(filename):
                messagebox.showinfo("成功", f"配置已导出到: {filename}")
            else:
                messagebox.showerror("错误", "导出配置失败")
                
    def import_config(self):
        """导入配置"""
        filename = filedialog.askopenfilename(
            title="导入配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filename:
            if messagebox.askyesno("确认", "导入配置将覆盖当前设置，确定要继续吗？"):
                if self.config_manager.import_config(filename):
                    self.load_settings()
                    messagebox.showinfo("成功", "配置已导入")
                else:
                    messagebox.showerror("错误", "导入配置失败")
            
    def center_dialog(self):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

class CustomRuleDialog:
    """自定义规则编辑对话框"""
    
    def __init__(self, parent, rule=None):
        self.parent = parent
        self.result = None
        self.dialog = None
        
        self.create_dialog(rule)
        
    def create_dialog(self, rule):
        """创建规则编辑对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("自定义规则")
        self.dialog.geometry("500x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 规则名称
        ttk.Label(main_frame, text="规则名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=rule.get('name', '') if rule else '')
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 模式输入
        ttk.Label(main_frame, text="文件名模式:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pattern_var = tk.StringVar(value=rule.get('pattern', '') if rule else '')
        pattern_entry = ttk.Entry(main_frame, textvariable=self.pattern_var, width=40)
        pattern_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 目标文件夹
        ttk.Label(main_frame, text="目标文件夹:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.folder_var = tk.StringVar(value=rule.get('target_folder', '') if rule else '')
        folder_entry = ttk.Entry(main_frame, textvariable=self.folder_var, width=40)
        folder_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 描述
        ttk.Label(main_frame, text="描述:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.desc_var = tk.StringVar(value=rule.get('description', '') if rule else '')
        desc_entry = ttk.Entry(main_frame, textvariable=self.desc_var, width=40)
        desc_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 启用状态
        self.enabled_var = tk.BooleanVar(value=rule.get('enabled', True) if rule else True)
        ttk.Checkbutton(main_frame, text="启用此规则", 
                       variable=self.enabled_var).grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        main_frame.columnconfigure(1, weight=1)
        
        # 示例说明
        example_frame = ttk.LabelFrame(main_frame, text="模式示例", padding=10)
        example_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        examples = [
            "*.jpg - 所有jpg文件",
            "报告* - 以'报告'开头的文件",
            "*_backup.* - 以'_backup'结尾的文件",
            "???.txt - 三个字符的txt文件",
            "*重要* - 文件名包含'重要'的文件"
        ]
        
        for example in examples:
            ttk.Label(example_frame, text=example).pack(anchor=tk.W)
            
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", 
                  command=self.save_rule).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
                  
        # 居中显示
        self.center_dialog()
        
    def save_rule(self):
        """保存规则"""
        name = self.name_var.get().strip()
        pattern = self.pattern_var.get().strip()
        folder = self.folder_var.get().strip()
        
        if not name:
            messagebox.showwarning("警告", "请输入规则名称")
            return
            
        if not pattern:
            messagebox.showwarning("警告", "请输入文件名模式")
            return
            
        if not folder:
            messagebox.showwarning("警告", "请输入目标文件夹")
            return
            
        self.result = {
            'name': name,
            'pattern': pattern,
            'target_folder': folder,
            'description': self.desc_var.get().strip(),
            'enabled': self.enabled_var.get()
        }
        
        self.dialog.destroy()
        
    def center_dialog(self):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_association_tab(self, notebook):
        """创建文件关联配置标签页"""
        association_frame = ttk.Frame(notebook)
        notebook.add(association_frame, text="文件关联")
        
        # 主框架
        main_frame = ttk.Frame(association_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 说明文本
        info_text = """
文件关联功能可以保持相关文件在同一文件夹中，避免破坏文件间的依赖关系。

支持的关联类型：
• 程序文件：可执行文件与其依赖库保持一起
• 项目文件夹：包含源码、配置文件的项目目录  
• 网页文件：HTML文件与相关的CSS、JS、图片文件
• 媒体集合：视频文件与字幕、海报等相关文件
• 同名文件：相同名称但不同扩展名的文件
        """
        
        info_label = ttk.Label(main_frame, text=info_text.strip(), justify=tk.LEFT, 
                              font=("微软雅黑", 9))
        info_label.pack(anchor=tk.W, pady=(0, 15))
        
        # 关联规则配置
        rules_frame = ttk.LabelFrame(main_frame, text="关联规则配置", padding="10")
        rules_frame.pack(fill=tk.BOTH, expand=True)
        
        # 程序文件关联
        program_frame = ttk.LabelFrame(rules_frame, text="程序文件关联", padding="8")
        program_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.enable_program_association = tk.BooleanVar(value=True)
        program_check = ttk.Checkbutton(
            program_frame, 
            text="启用程序文件关联检测", 
            variable=self.enable_program_association
        )
        program_check.pack(anchor=tk.W)
        
        program_desc = ttk.Label(
            program_frame,
            text="主文件类型: .exe, .app, .jar | 相关文件: .dll, .so, .ini, .cfg",
            foreground="gray",
            font=("微软雅黑", 8)
        )
        program_desc.pack(anchor=tk.W, pady=(2, 0))
        
        # 项目文件关联
        project_frame = ttk.LabelFrame(rules_frame, text="项目文件关联", padding="8")
        project_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.enable_project_association = tk.BooleanVar(value=True)
        project_check = ttk.Checkbutton(
            project_frame, 
            text="启用项目文件夹检测", 
            variable=self.enable_project_association
        )
        project_check.pack(anchor=tk.W)
        
        project_desc = ttk.Label(
            project_frame,
            text="检测标志: package.json, requirements.txt, .gitignore 等项目指示文件",
            foreground="gray",
            font=("微软雅黑", 8)
        )
        project_desc.pack(anchor=tk.W, pady=(2, 0))
        
        # 网页文件关联
        web_frame = ttk.LabelFrame(rules_frame, text="网页文件关联", padding="8")
        web_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.enable_web_association = tk.BooleanVar(value=True)
        web_check = ttk.Checkbutton(
            web_frame, 
            text="启用网页文件关联检测", 
            variable=self.enable_web_association
        )
        web_check.pack(anchor=tk.W)
        
        web_desc = ttk.Label(
            web_frame,
            text="HTML文件与同名或相关的CSS、JS、图片等资源文件保持一起",
            foreground="gray",
            font=("微软雅黑", 8)
        )
        web_desc.pack(anchor=tk.W, pady=(2, 0))
        
        # 媒体文件关联
        media_frame = ttk.LabelFrame(rules_frame, text="媒体文件关联", padding="8")
        media_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.enable_media_association = tk.BooleanVar(value=True)
        media_check = ttk.Checkbutton(
            media_frame, 
            text="启用媒体文件关联检测", 
            variable=self.enable_media_association
        )
        media_check.pack(anchor=tk.W)
        
        media_desc = ttk.Label(
            media_frame,
            text="视频文件与同名字幕文件(.srt, .ass)、海报图片等保持一起",
            foreground="gray",
            font=("微软雅黑", 8)
        )
        media_desc.pack(anchor=tk.W, pady=(2, 0))
        
        # 同名文件关联
        samename_frame = ttk.LabelFrame(rules_frame, text="同名文件关联", padding="8")
        samename_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.enable_samename_association = tk.BooleanVar(value=True)
        samename_check = ttk.Checkbutton(
            samename_frame, 
            text="启用同名文件关联检测", 
            variable=self.enable_samename_association
        )
        samename_check.pack(anchor=tk.W)
        
        samename_desc = ttk.Label(
            samename_frame,
            text="相同文件名但不同扩展名的文件将保持在同一文件夹中",
            foreground="gray",
            font=("微软雅黑", 8)
        )
        samename_desc.pack(anchor=tk.W, pady=(2, 0))
        
        # 测试和重置按钮
        test_frame = ttk.Frame(rules_frame)
        test_frame.pack(fill=tk.X, pady=(15, 0))
        
        test_btn = ttk.Button(
            test_frame, 
            text="测试关联检测", 
            command=self.test_association_detection
        )
        test_btn.pack(side=tk.LEFT)
        
        reset_btn = ttk.Button(
            test_frame, 
            text="重置为默认", 
            command=self.reset_association_settings
        )
        reset_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 关联强度设置
        strength_frame = ttk.LabelFrame(rules_frame, text="关联强度设置", padding="8")
        strength_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(strength_frame, text="项目文件密度阈值:").pack(anchor=tk.W)
        self.project_threshold = tk.DoubleVar(value=0.5)
        threshold_scale = ttk.Scale(
            strength_frame, 
            from_=0.1, 
            to=0.9, 
            variable=self.project_threshold,
            orient=tk.HORIZONTAL
        )
        threshold_scale.pack(fill=tk.X, pady=(2, 0))
        
        threshold_desc = ttk.Label(
            strength_frame,
            text="值越高，要求项目文件夹中代码/配置文件比例越高才被识别为项目",
            foreground="gray",
            font=("微软雅黑", 8)
        )
        threshold_desc.pack(anchor=tk.W, pady=(2, 0))
    
    def test_association_detection(self):
        """测试关联检测功能"""
        test_folder = filedialog.askdirectory(
            title="选择测试文件夹",
            parent=self.dialog
        )
        if not test_folder:
            return
        
        try:
            from file_classifier_enhanced import EnhancedFileClassifier
            enhanced_classifier = EnhancedFileClassifier()
            
            associations = enhanced_classifier.preview_associations(test_folder)
            
            # 显示结果
            result_text = (
                f"检测完成！\n\n"
                f"总文件数: {associations['total_files']}\n"
                f"关联组数: {associations['total_groups']}\n\n"
                f"详细信息:\n"
            )
            
            for group_name, group_info in associations['groups'].items():
                if group_name == 'individual_files':
                    result_text += f"• 独立文件: {group_info['file_count']} 个\n"
                else:
                    group_type = ""
                    if group_name.startswith('project_'):
                        group_type = "项目文件夹"
                    elif group_name.startswith('program_'):
                        group_type = "程序文件组"
                    elif group_name.startswith('web_'):
                        group_type = "网页文件组"
                    elif group_name.startswith('media_'):
                        group_type = "媒体文件组"
                    elif group_name.startswith('samename_'):
                        group_type = "同名文件组"
                    
                    result_text += f"• {group_type}: {group_info['file_count']} 个文件\n"
            
            messagebox.showinfo("检测结果", result_text, parent=self.dialog)
            
        except ImportError:
            messagebox.showerror(
                "功能不可用", 
                "增强版文件分类器模块不可用，请检查文件是否存在。",
                parent=self.dialog
            )
        except Exception as e:
            messagebox.showerror("错误", f"检测失败: {str(e)}", parent=self.dialog)
    
    def reset_association_settings(self):
        """重置关联设置为默认值"""
        self.enable_program_association.set(True)
        self.enable_project_association.set(True)
        self.enable_web_association.set(True)
        self.enable_media_association.set(True)
        self.enable_samename_association.set(True)
        self.project_threshold.set(0.5)
        messagebox.showinfo("提示", "已重置为默认设置", parent=self.dialog) 
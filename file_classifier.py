#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件分类器核心模块
提供文件自动分类、预览、撤销等核心功能
"""

import os
import shutil
import json
import fnmatch
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import send2trash

class FileClassifier:
    """文件分类器核心类"""
    
    def __init__(self):
        self.operation_history = []
        self.max_history = 50  # 最多保存50次操作记录
        self.history_file = Path.home() / '.file_classifier_history.json'
        
        # 默认文件类型映射
        self.default_type_mapping = {
            # 图片文件
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', 
                      '.svg', '.webp', '.ico', '.raw', '.heic', '.heif'],
            # 文档文件
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages',
                         '.md', '.tex', '.epub', '.mobi'],
            # 表格文件
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods', '.numbers', '.tsv'],
            # 演示文件
            'presentations': ['.ppt', '.pptx', '.odp', '.key'],
            # 音频文件
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
                     '.opus', '.ape', '.ac3', '.dts'],
            # 视频文件
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
                      '.m4v', '.3gp', '.ogv', '.ts', '.vob'],
            # 压缩文件
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
                        '.cab', '.ace', '.arj', '.lzh'],
            # 代码文件
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h',
                    '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.ts', '.jsx',
                    '.vue', '.sql', '.sh', '.bat', '.ps1', '.xml', '.json', '.yaml'],
            # 可执行文件
            'executables': ['.exe', '.msi', '.deb', '.rpm', '.dmg', '.app', '.pkg',
                           '.run', '.bin', '.jar'],
            # 字体文件
            'fonts': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
            # 其他
            'others': []
        }
        
        # 加载操作历史
        self.load_operation_history()
        
    def classify_files(self, source_path: str, target_path: str, 
                      rules: List[str], operation: str = 'move',
                      custom_rules: List[Dict] = None,
                      type_mapping: Dict[str, List[str]] = None) -> List[Dict]:
        """
        批量分类文件
        
        Args:
            source_path: 源文件夹路径
            target_path: 目标文件夹路径
            rules: 启用的分类规则列表
            operation: 操作类型 ('move', 'copy', 'link')
            custom_rules: 自定义规则列表
            type_mapping: 文件类型映射字典
            
        Returns:
            操作结果列表
        """
        results = []
        current_operation = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'source_path': source_path,
            'target_path': target_path,
            'rules': rules,
            'files': []
        }
        
        try:
            source_path = Path(source_path)
            target_path = Path(target_path)
            
            # 确保目标文件夹存在
            target_path.mkdir(parents=True, exist_ok=True)
            
            # 获取所有文件
            files = self._get_files_from_source(source_path)
            
            # 使用提供的映射或默认映射
            current_type_mapping = type_mapping or self.default_type_mapping
            
            for file_path in files:
                try:
                    # 确定目标位置
                    target_subdir = self._determine_target_folder(
                        file_path, rules, custom_rules, current_type_mapping
                    )
                    final_target_dir = target_path / target_subdir
                    final_target_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 处理文件名冲突
                    target_file_path = self._resolve_filename_conflict(
                        final_target_dir / file_path.name
                    )
                    
                    # 执行操作
                    success, status = self._execute_file_operation(
                        file_path, target_file_path, operation
                    )
                    
                    # 记录操作
                    file_record = {
                        'filename': file_path.name,
                        'source': str(file_path),
                        'target': str(target_file_path) if success else '',
                        'operation': operation,
                        'status': status,
                        'success': success,
                        'size': file_path.stat().st_size if file_path.exists() else 0,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    results.append(file_record)
                    if success:
                        current_operation['files'].append(file_record)
                    
                except Exception as e:
                    error_record = {
                        'filename': file_path.name if hasattr(file_path, 'name') else '未知',
                        'source': str(file_path) if file_path else '',
                        'target': '',
                        'operation': operation,
                        'status': f'错误: {str(e)}',
                        'success': False,
                        'size': 0,
                        'timestamp': datetime.now().isoformat()
                    }
                    results.append(error_record)
                    
            # 保存操作记录
            if current_operation['files']:
                self._save_operation_history(current_operation)
                
        except Exception as e:
            raise Exception(f"分类过程中发生错误: {str(e)}")
            
        return results
        
    def preview_classification(self, source_path: str, target_path: str, 
                             rules: List[str], custom_rules: List[Dict] = None,
                             type_mapping: Dict[str, List[str]] = None) -> List[Dict]:
        """
        预览分类结果，不实际移动文件
        
        Args:
            source_path: 源文件夹路径
            target_path: 目标文件夹路径
            rules: 启用的分类规则列表
            custom_rules: 自定义规则列表
            type_mapping: 文件类型映射字典
            
        Returns:
            预览结果列表
        """
        results = []
        
        try:
            source_path = Path(source_path)
            target_path = Path(target_path)
            
            # 获取所有文件
            files = self._get_files_from_source(source_path)
            
            # 使用提供的映射或默认映射
            current_type_mapping = type_mapping or self.default_type_mapping
            
            for file_path in files:
                try:
                    # 确定目标位置
                    target_subdir = self._determine_target_folder(
                        file_path, rules, custom_rules, current_type_mapping
                    )
                    final_target_dir = target_path / target_subdir
                    target_file_path = final_target_dir / file_path.name
                    
                    # 检查是否会有冲突
                    conflict_info = ""
                    if target_file_path.exists():
                        conflict_info = " (存在冲突)"
                    
                    # 创建预览记录
                    preview_record = {
                        'filename': file_path.name,
                        'source': str(file_path),
                        'target': str(target_file_path),
                        'operation': '预览',
                        'status': f'待处理{conflict_info}',
                        'success': True,
                        'size': file_path.stat().st_size,
                        'file_type': self._get_file_type(file_path, current_type_mapping),
                        'target_folder': target_subdir
                    }
                    
                    results.append(preview_record)
                    
                except Exception as e:
                    error_record = {
                        'filename': file_path.name if hasattr(file_path, 'name') else '未知',
                        'source': str(file_path) if file_path else '',
                        'target': '',
                        'operation': '预览',
                        'status': f'预览错误: {str(e)}',
                        'success': False,
                        'size': 0
                    }
                    results.append(error_record)
                    
        except Exception as e:
            raise Exception(f"预览过程中发生错误: {str(e)}")
            
        return results
        
    def classify_single_file(self, file_path: str, target_path: str, 
                           rules: List[str], operation: str = 'move',
                           custom_rules: List[Dict] = None,
                           type_mapping: Dict[str, List[str]] = None) -> Dict:
        """
        分类单个文件（用于监控模式）
        
        Args:
            file_path: 文件路径
            target_path: 目标基础路径
            rules: 启用的分类规则列表
            operation: 操作类型
            custom_rules: 自定义规则列表
            type_mapping: 文件类型映射字典
            
        Returns:
            操作结果字典
        """
        try:
            file_path = Path(file_path)
            target_path = Path(target_path)
            
            if not file_path.exists() or not file_path.is_file():
                return {
                    'filename': file_path.name,
                    'source': str(file_path),
                    'target': '',
                    'operation': operation,
                    'status': '文件不存在或不是文件',
                    'success': False
                }
            
            # 使用提供的映射或默认映射
            current_type_mapping = type_mapping or self.default_type_mapping
            
            # 确定目标位置
            target_subdir = self._determine_target_folder(
                file_path, rules, custom_rules, current_type_mapping
            )
            final_target_dir = target_path / target_subdir
            final_target_dir.mkdir(parents=True, exist_ok=True)
            
            # 处理文件名冲突
            target_file_path = self._resolve_filename_conflict(
                final_target_dir / file_path.name
            )
            
            # 执行操作
            success, status = self._execute_file_operation(
                file_path, target_file_path, operation
            )
            
            # 创建操作记录
            file_record = {
                'filename': file_path.name,
                'source': str(file_path),
                'target': str(target_file_path) if success else '',
                'operation': operation,
                'status': status,
                'success': success,
                'size': file_path.stat().st_size if file_path.exists() else 0,
                'timestamp': datetime.now().isoformat()
            }
            
            # 保存单个文件操作记录
            if success:
                single_operation = {
                    'timestamp': datetime.now().isoformat(),
                    'operation': operation,
                    'source_path': str(file_path.parent),
                    'target_path': str(target_path),
                    'rules': rules,
                    'files': [file_record]
                }
                self._save_operation_history(single_operation)
            
            return file_record
            
        except Exception as e:
            return {
                'filename': file_path.name if 'file_path' in locals() and hasattr(file_path, 'name') else '未知',
                'source': str(file_path) if 'file_path' in locals() else '',
                'target': '',
                'operation': operation,
                'status': f'错误: {str(e)}',
                'success': False
            }
            
    def _get_files_from_source(self, source_path: Path) -> List[Path]:
        """从源路径获取所有文件"""
        files = []
        try:
            if source_path.is_file():
                files.append(source_path)
            elif source_path.is_dir():
                files = [f for f in source_path.rglob('*') if f.is_file()]
        except PermissionError:
            pass  # 跳过无权限访问的文件
        return files
        
    def _determine_target_folder(self, file_path: Path, rules: List[str],
                               custom_rules: List[Dict] = None,
                               type_mapping: Dict[str, List[str]] = None) -> str:
        """
        根据规则确定目标文件夹
        
        Args:
            file_path: 文件路径
            rules: 启用的规则列表
            custom_rules: 自定义规则列表
            type_mapping: 文件类型映射
            
        Returns:
            目标子文件夹路径
        """
        target_parts = []
        current_type_mapping = type_mapping or self.default_type_mapping
        
        # 首先检查自定义规则（优先级最高）
        if 'by_custom' in rules and custom_rules:
            custom_folder = self._apply_custom_rules(file_path, custom_rules)
            if custom_folder:
                return custom_folder
        
        # 按文件类型分类
        if 'by_type' in rules:
            file_type = self._get_file_type(file_path, current_type_mapping)
            target_parts.append(file_type)
            
        # 按修改日期分类
        if 'by_date' in rules:
            date_folder = self._get_date_folder(file_path)
            target_parts.append(date_folder)
            
        # 按文件大小分类
        if 'by_size' in rules:
            size_folder = self._get_size_folder(file_path)
            target_parts.append(size_folder)
            
        # 如果没有任何规则匹配，使用默认文件夹
        if not target_parts:
            target_parts.append('未分类')
            
        return os.path.join(*target_parts)
        
    def _get_file_type(self, file_path: Path, type_mapping: Dict[str, List[str]]) -> str:
        """根据文件扩展名获取文件类型"""
        extension = file_path.suffix.lower()
        
        for type_name, extensions in type_mapping.items():
            if extension in extensions:
                return type_name
                
        return 'others'
        
    def _get_date_folder(self, file_path: Path) -> str:
        """根据文件修改时间获取日期文件夹"""
        try:
            mtime = os.path.getmtime(file_path)
            date = datetime.fromtimestamp(mtime)
            return date.strftime('%Y-%m')
        except:
            return '未知日期'
            
    def _get_size_folder(self, file_path: Path) -> str:
        """根据文件大小获取大小文件夹"""
        try:
            size = file_path.stat().st_size
            
            if size < 1024 * 1024:  # < 1MB
                return '小文件(<1MB)'
            elif size < 10 * 1024 * 1024:  # < 10MB
                return '中文件(1-10MB)'
            elif size < 100 * 1024 * 1024:  # < 100MB
                return '大文件(10-100MB)'
            else:
                return '超大文件(>100MB)'
        except:
            return '未知大小'
            
    def _apply_custom_rules(self, file_path: Path, custom_rules: List[Dict]) -> Optional[str]:
        """应用自定义规则"""
        filename = file_path.name.lower()
        
        for rule in custom_rules:
            pattern = rule.get('pattern', '').lower()
            target_folder = rule.get('target_folder', '')
            
            if pattern and target_folder:
                # 支持通配符匹配
                if fnmatch.fnmatch(filename, pattern):
                    return target_folder
                    
        return None
        
    def _resolve_filename_conflict(self, target_path: Path) -> Path:
        """解决文件名冲突"""
        if not target_path.exists():
            return target_path
            
        # 生成新的文件名
        counter = 1
        stem = target_path.stem
        suffix = target_path.suffix
        parent = target_path.parent
        
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
            if counter > 1000:  # 防止无限循环
                break
                
        # 如果还是冲突，使用时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return parent / f"{stem}_{timestamp}{suffix}"
        
    def _execute_file_operation(self, source_path: Path, target_path: Path, 
                              operation: str) -> tuple[bool, str]:
        """
        执行文件操作
        
        Returns:
            (success: bool, status_message: str)
        """
        try:
            if operation == 'move':
                shutil.move(str(source_path), str(target_path))
                return True, '移动成功'
            elif operation == 'copy':
                shutil.copy2(str(source_path), str(target_path))
                return True, '复制成功'
            elif operation == 'link':
                # 创建硬链接
                os.link(str(source_path), str(target_path))
                return True, '链接成功'
            else:
                return False, f'未知操作类型: {operation}'
                
        except PermissionError:
            return False, '权限不足'
        except FileExistsError:
            return False, '目标文件已存在'
        except OSError as e:
            return False, f'系统错误: {str(e)}'
        except Exception as e:
            return False, f'操作失败: {str(e)}'
            
    def _save_operation_history(self, operation: Dict):
        """保存操作历史"""
        self.operation_history.append(operation)
        
        # 限制历史记录数量
        if len(self.operation_history) > self.max_history:
            self.operation_history = self.operation_history[-self.max_history:]
            
        # 保存到文件
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.operation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
            
    def load_operation_history(self):
        """加载操作历史"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.operation_history = json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            self.operation_history = []
            
    def undo_last_operation(self) -> tuple[bool, str]:
        """
        撤销上次操作
        
        Returns:
            (success: bool, message: str)
        """
        if not self.operation_history:
            return False, "没有可撤销的操作"
            
        last_operation = self.operation_history[-1]
        
        try:
            undone_files = 0
            failed_files = 0
            
            # 撤销文件操作（逆序进行）
            for file_record in reversed(last_operation['files']):
                if not file_record.get('success', False):
                    continue
                    
                try:
                    source_path = Path(file_record['source'])
                    target_path = Path(file_record['target'])
                    
                    if last_operation['operation'] == 'move':
                        # 移动操作的撤销：将文件移回原位置
                        if target_path.exists():
                            # 确保源目录存在
                            source_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(target_path), str(source_path))
                            undone_files += 1
                    elif last_operation['operation'] == 'copy':
                        # 复制操作的撤销：删除目标文件
                        if target_path.exists():
                            send2trash.send2trash(str(target_path))
                            undone_files += 1
                    elif last_operation['operation'] == 'link':
                        # 链接操作的撤销：删除链接文件
                        if target_path.exists():
                            target_path.unlink()
                            undone_files += 1
                            
                except Exception as e:
                    print(f"撤销文件 {file_record['filename']} 失败: {e}")
                    failed_files += 1
                    
            # 移除历史记录
            self.operation_history.pop()
            
            # 更新历史文件
            try:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump(self.operation_history, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"更新历史文件失败: {e}")
            
            if failed_files == 0:
                return True, f"成功撤销 {undone_files} 个文件的操作"
            else:
                return True, f"撤销完成，成功 {undone_files} 个，失败 {failed_files} 个"
            
        except Exception as e:
            return False, f"撤销操作失败: {str(e)}"
            
    def get_operation_history(self) -> List[Dict]:
        """获取操作历史"""
        return self.operation_history.copy()
        
    def clear_history(self):
        """清空操作历史"""
        self.operation_history.clear()
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
        except Exception as e:
            print(f"清空历史文件失败: {e}")
            
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_operations = len(self.operation_history)
        total_files = sum(len(op['files']) for op in self.operation_history)
        
        operation_types = {}
        for op in self.operation_history:
            op_type = op['operation']
            operation_types[op_type] = operation_types.get(op_type, 0) + len(op['files'])
            
        return {
            'total_operations': total_operations,
            'total_files': total_files,
            'operation_types': operation_types,
            'last_operation': self.operation_history[-1]['timestamp'] if self.operation_history else None
        } 
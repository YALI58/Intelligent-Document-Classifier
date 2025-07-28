import json
import re
import os
from datetime import datetime
from typing import Dict, Optional
import markdown
from markdown.extensions.fenced_code import FencedCodeExtension

class MarkdownToBlogConverter:
    def __init__(self):
        self.md_parser = markdown.Markdown(
            extensions=[
                'extra',
                FencedCodeExtension(),
                'tables',
                'toc',
                'nl2br',
                'sane_lists'
            ],
            output_format='html5'
        )
        
        self.default_metadata = {
            'category': '技术',
            'author': '未知作者'
        }

    def extract_tag_from_filename(self, filename: str) -> str:
        """从文件名提取标签（取文件名第一部分）"""
        # 移除扩展名和常见前缀/后缀
        name = os.path.splitext(filename)[0]
        name = re.sub(r'^\d+-', '', name)  # 移除开头的数字和破折号
        name = re.sub(r'[-_]', ' ', name)  # 将下划线和中划线转为空格
        
        # 提取第一个有意义的单词作为标签
        words = name.split()
        if words:
            # 移除常见停用词
            stop_words = {'how', 'to', 'a', 'an', 'the', 'guide', 'tutorial'}
            for word in words:
                if word.lower() not in stop_words and len(word) > 2:
                    return word.capitalize()
        
        return '未分类'

    def parse_markdown(self, md_content: str, filename: str) -> Dict:
        """解析Markdown内容"""
        metadata, cleaned_content = self.extract_metadata(md_content)
        
        # 使用文件名作为标题（不带扩展名）
        title = os.path.splitext(filename)[0].replace('-', ' ').replace('_', ' ')
        
        # 从文件名提取标签
        tag = self.extract_tag_from_filename(filename)
        
        # 生成HTML内容
        html_content = self.md_parser.reset().convert(cleaned_content)
        
        # 自动生成摘要
        text_content = re.sub(r'<[^>]+>', '', html_content)
        summary = metadata.get('summary') or (text_content[:200] + '...' if len(text_content) > 200 else text_content)
        
        return {
            "id": int(datetime.now().timestamp() % 100000),
            "title": title,
            "date": metadata.get('date') or datetime.now().strftime("%Y-%m-%d"),
            "summary": summary,
            "content": html_content,
            "category": metadata.get('category', self.default_metadata['category']),
            "tag": tag,  # 从文件名提取的单个标签
            "author": metadata.get('author', self.default_metadata['author']),
            "word_count": len(text_content.split()),
            "reading_time": max(1, len(text_content.split()) // 200)
        }
    def process_file(self, input_path: str, output_path: Optional[str] = None) -> Optional[Dict]:
        """处理单个Markdown文件"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            filename = os.path.basename(input_path)
            post = self.parse_markdown(md_content, filename)
            
            if not output_path:
                output_path = f"{os.path.splitext(input_path)[0]}.json"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(post, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 转换成功: {input_path} -> {output_path}")
            return post
        
        except Exception as e:
            print(f"❌ 处理文件 {input_path} 时出错: {str(e)}")
            return None

    def batch_process(self, input_dir: str, output_dir: Optional[str] = None):
        """批量处理目录中的Markdown文件"""
        if not output_dir:
            output_dir = input_dir
        
        os.makedirs(output_dir, exist_ok=True)
        all_posts = []
        
        for filename in os.listdir(input_dir):
            if filename.endswith('.md'):
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
                post = self.process_file(input_path, output_path)
                if post:
                    all_posts.append(post)
        
        # 生成索引文件
        if all_posts:
            index_path = os.path.join(output_dir, '_index.json')
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "generated_at": datetime.now().isoformat(),
                    "post_count": len(all_posts),
                    "posts": sorted(all_posts, key=lambda x: x['date'], reverse=True)
                }, f, ensure_ascii=False, indent=2)
            print(f"\n📁 生成索引文件: {index_path}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Markdown转JSON博客工具',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input', help='Markdown文件路径或目录路径')
    parser.add_argument('-o', '--output', help='输出路径(文件或目录)')
    
    args = parser.parse_args()
    
    converter = MarkdownToBlogConverter()
    
    if os.path.isdir(args.input):
        print(f"📂 批量处理目录: {args.input}")
        converter.batch_process(args.input, args.output)
    elif os.path.isfile(args.input):
        print(f"📄 处理单个文件: {args.input}")
        converter.process_file(args.input, args.output)
    else:
        print(f"❌ 错误: 路径 {args.input} 不存在")
        exit(1)
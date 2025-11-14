#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL请求工具 - 读取txt文件中的URL并获取标题和状态码

使用方法:
    python main.py urls.txt
    或
    main.exe urls.txt

参数:
    urls.txt - 包含URL列表的文本文件，每行一个URL
"""

import sys
import os
import re
import argparse
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import time

class URLProcessor:
    def __init__(self, timeout=10, retries=3, delay=1):
        """初始化URL处理器"""
        self.timeout = timeout
        self.delay = delay
        
        # 创建带重试机制的session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def normalize_url(self, url_line):
        """标准化URL，处理只有域名的情况"""
        url_line = url_line.strip()
        if not url_line:
            return None
            
        # 如果URL没有协议头，添加https://
        if not url_line.startswith(('http://', 'https://')):
            # 检查是否包含域名格式
            if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', url_line):
                url_line = 'https://' + url_line
            else:
                return None
        
        return url_line
    
    def extract_title(self, html_content):
        """从HTML内容中提取标题"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
            return "无标题"
        except Exception as e:
            return f"标题提取失败: {str(e)}"
    
    def process_url(self, url):
        """处理单个URL，返回状态码和标题"""
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True, verify=False)
            status_code = response.status_code
            
            # 检查内容类型，只处理HTML内容
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                title = self.extract_title(response.content)
            else:
                title = f"非HTML内容: {content_type}"
            
            return {
                'url': url,
                'status_code': status_code,
                'title': title,
                'success': True
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'url': url,
                'status_code': '请求失败',
                'title': f"错误: {str(e)}",
                'success': False
            }
        except Exception as e:
            return {
                'url': url,
                'status_code': '处理失败',
                'title': f"错误: {str(e)}",
                'success': False
            }
    
    def process_file(self, file_path, output_file=None):
        """处理整个文件中的URL"""
        if not os.path.exists(file_path):
            print(f"错误: 文件 '{file_path}' 不存在")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = f.readlines()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    urls = f.readlines()
            except Exception as e:
                print(f"错误: 无法读取文件 '{file_path}': {str(e)}")
                return False
        
        valid_urls = []
        for i, url_line in enumerate(urls, 1):
            normalized_url = self.normalize_url(url_line)
            if normalized_url:
                valid_urls.append((i, normalized_url))
            else:
                print(f"警告: 第{i}行URL格式无效: {url_line.strip()}")
        
        if not valid_urls:
            print("错误: 文件中没有有效的URL")
            return False
        
        print(f"找到 {len(valid_urls)} 个有效URL，开始处理...")
        print("-" * 80)
        
        results = []
        
        # 准备输出文件
        output_fh = None
        if output_file:
            try:
                output_fh = open(output_file, 'w', encoding='utf-8')
                output_fh.write("URL,状态码,标题\n")
            except Exception as e:
                print(f"警告: 无法创建输出文件 '{output_file}': {str(e)}")
        
        for line_num, url in valid_urls:
            print(f"处理第{line_num}行: {url}")
            
            result = self.process_url(url)
            results.append(result)
            
            # 输出结果
            status_display = result['status_code'] if result['success'] else result['status_code']
            title_display = result['title'][:100] + "..." if len(result['title']) > 100 else result['title']
            
            print(f"  状态码: {status_display}")
            print(f"  标题: {title_display}")
            print("-" * 80)
            
            # 写入输出文件
            if output_fh:
                # CSV格式转义
                title_csv = result['title'].replace('"', '""')
                output_fh.write(f'"{url}","{status_display}","{title_csv}"\n')
            
            # 延迟处理，避免请求过快
            if self.delay > 0:
                time.sleep(self.delay)
        
        if output_fh:
            output_fh.close()
            print(f"\n结果已保存到: {output_file}")
        
        # 统计信息
        successful = sum(1 for r in results if r['success'])
        print(f"\n处理完成! 成功: {successful}/{len(results)}")
        
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='URL请求工具 - 读取txt文件中的URL并获取标题和状态码')
    parser.add_argument('file', help='包含URL列表的文本文件路径')
    parser.add_argument('-o', '--output', help='输出结果到CSV文件')
    parser.add_argument('-t', '--timeout', type=int, default=10, help='请求超时时间(秒)，默认10秒')
    parser.add_argument('-r', '--retries', type=int, default=3, help='重试次数，默认3次')
    parser.add_argument('-d', '--delay', type=float, default=1, help='请求间隔延迟(秒)，默认1秒')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.file):
        print(f"错误: 文件 '{args.file}' 不存在")
        sys.exit(1)
    
    # 创建处理器并处理文件
    processor = URLProcessor(
        timeout=args.timeout,
        retries=args.retries,
        delay=args.delay
    )
    
    success = processor.process_file(args.file, args.output)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
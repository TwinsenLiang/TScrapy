#!/usr/bin/env python3
"""
TScrapy - 通用网站爬虫工具
支持命令行参数配置 URL、深度、输出目录等
"""
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, urlparse
import hashlib
import time
import random
import json
import argparse
from datetime import datetime
from typing import List, Set, Tuple, Optional


class WebScraper:
    """通用网站爬虫"""

    def __init__(
        self,
        start_url: str,
        output_dir: str = 'scraped_content',
        depth_limit: int = 3,
        delay_range: Tuple[float, float] = (2.0, 4.0),
        same_domain_only: bool = True,
        exclude_patterns: Optional[List[str]] = None
    ):
        """
        初始化爬虫

        Args:
            start_url: 起始 URL
            output_dir: 输出目录
            depth_limit: 最大爬取深度
            delay_range: 请求延迟范围（秒）
            same_domain_only: 是否只爬取同域名链接
            exclude_patterns: 排除的 URL 模式列表
        """
        self.start_url = start_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.depth_limit = depth_limit
        self.delay_range = delay_range
        self.same_domain_only = same_domain_only
        self.exclude_patterns = exclude_patterns or ['.pdf', '.zip', '.tar', '.gz', '.exe', '#']

        # 解析起始域名
        self.start_domain = urlparse(start_url).netloc

        # 初始化会话，强制 HTTP/1.1
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=3)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

        # 统计信息
        self.stats = {
            'total_pages': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': datetime.now(),
        }

        # 爬取队列
        self.urls_to_scrape: List[Tuple[str, int]] = [(self.start_url, 0)]  # (url, depth)
        self.scraped_urls: Set[str] = set()

    def fetch_page(self, url: str) -> Optional[requests.Response]:
        """获取页面内容"""
        try:
            # 随机延迟，避免频繁请求
            time.sleep(random.uniform(*self.delay_range))

            # 发送请求 (connect_timeout=10, read_timeout=90)
            response = self.session.get(url, timeout=(10, 90))
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"✗ 请求失败 {url}: {e}")
            return None
        except Exception as e:
            print(f"✗ 未知错误 {url}: {e}")
            return None

    def save_page(self, url: str, response: requests.Response) -> Optional[BeautifulSoup]:
        """保存页面内容"""
        try:
            soup = BeautifulSoup(response.content, 'html.parser')

            # 提取标题
            title = soup.title.string if soup.title else 'Untitled'
            title = self.sanitize_filename(title)

            # 生成唯一文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"{title}_{url_hash}"

            # 保存 HTML
            html_path = self.output_dir / f"{filename}.html"
            html_path.write_text(response.text, encoding='utf-8')

            # 保存纯文本
            text_content = soup.get_text(separator='\n', strip=True)
            text_content = '\n'.join(line.strip() for line in text_content.split('\n') if line.strip())

            txt_path = self.output_dir / f"{filename}.txt"
            txt_path.write_text(text_content, encoding='utf-8')

            # 保存元数据
            metadata = {
                'url': url,
                'title': soup.title.string if soup.title else None,
                'scraped_at': datetime.now().isoformat(),
            }
            json_path = self.output_dir / f"{filename}.json"
            json_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')

            print(f"✓ 已保存: {filename}")

            return soup

        except Exception as e:
            print(f"✗ 保存失败 {url}: {e}")
            return None

    def extract_links(self, url: str, soup: BeautifulSoup) -> List[str]:
        """提取页面链接"""
        links = []
        for link in soup.find_all('a', href=True):
            try:
                full_url = urljoin(url, link['href'])
                parsed = urlparse(full_url)

                # 移除 fragment
                full_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    full_url += f"?{parsed.query}"

                # 检查域名限制
                if self.same_domain_only and parsed.netloc != self.start_domain:
                    continue

                # 检查排除模式
                if any(pattern in full_url for pattern in self.exclude_patterns):
                    continue

                # 只爬取 HTTP(S) 链接
                if parsed.scheme not in ['http', 'https']:
                    continue

                links.append(full_url)
            except Exception as e:
                print(f"  ⚠ 链接解析失败: {link.get('href', '')} - {e}")
                continue

        return links

    def crawl(self):
        """开始爬取"""
        print("=" * 70)
        print("TScrapy - 通用网站爬虫")
        print("=" * 70)
        print(f"起始 URL: {self.start_url}")
        print(f"输出目录: {self.output_dir.absolute()}")
        print(f"最大深度: {self.depth_limit}")
        print(f"同域限制: {'是' if self.same_domain_only else '否'}")
        print(f"延迟范围: {self.delay_range[0]}-{self.delay_range[1]} 秒")
        print("=" * 70)

        while self.urls_to_scrape:
            current_url, depth = self.urls_to_scrape.pop(0)

            # 检查是否已爬取
            if current_url in self.scraped_urls:
                self.stats['skipped'] += 1
                continue

            # 检查深度限制
            if depth > self.depth_limit:
                self.stats['skipped'] += 1
                continue

            print(f"\n[深度 {depth}/{self.depth_limit}] 正在爬取: {current_url}")

            # 获取页面
            response = self.fetch_page(current_url)
            if not response:
                self.stats['failed'] += 1
                self.scraped_urls.add(current_url)
                continue

            # 保存页面
            soup = self.save_page(current_url, response)
            if soup:
                self.stats['success'] += 1

                # 提取链接（仅在未达到深度限制时）
                if depth < self.depth_limit:
                    new_links = self.extract_links(current_url, soup)
                    for link in new_links:
                        if link not in self.scraped_urls and link not in [url for url, _ in self.urls_to_scrape]:
                            self.urls_to_scrape.append((link, depth + 1))
                            print(f"  → 发现新链接 (深度 {depth + 1}): {link}")
            else:
                self.stats['failed'] += 1

            self.scraped_urls.add(current_url)
            self.stats['total_pages'] += 1

        # 打印统计信息
        self.print_stats()

    def print_stats(self):
        """打印统计信息"""
        end_time = datetime.now()
        duration = (end_time - self.stats['start_time']).total_seconds()

        print("\n" + "=" * 70)
        print("爬取完成！")
        print("=" * 70)
        print(f"总页面数: {self.stats['total_pages']}")
        print(f"成功: {self.stats['success']}")
        print(f"失败: {self.stats['failed']}")
        print(f"跳过: {self.stats['skipped']}")
        print(f"耗时: {duration:.2f} 秒")
        print(f"平均速度: {self.stats['success'] / duration:.2f} 页/秒" if duration > 0 else "")
        print(f"输出目录: {self.output_dir.absolute()}")
        print("=" * 70)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名，移除非法字符"""
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '')
        filename = ''.join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-', '(', ')'))
        filename = filename.strip().replace(' ', '_')
        return filename[:100] if filename else 'untitled'


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='TScrapy - 通用网站爬虫工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 爬取网站，深度为 2 层
  python scraper.py https://example.com -d 2

  # 指定输出目录
  python scraper.py https://example.com -o ./output

  # 允许跨域爬取
  python scraper.py https://example.com --allow-external

  # 自定义延迟和排除模式
  python scraper.py https://example.com --delay 1 3 --exclude .pdf .zip /login
        """
    )

    parser.add_argument(
        'url',
        help='起始 URL（必须包含 http:// 或 https://）'
    )

    parser.add_argument(
        '-d', '--depth',
        type=int,
        default=3,
        help='最大爬取深度（默认: 3）'
    )

    parser.add_argument(
        '-o', '--output',
        default='scraped_content',
        help='输出目录（默认: scraped_content）'
    )

    parser.add_argument(
        '--delay',
        nargs=2,
        type=float,
        default=[2.0, 4.0],
        metavar=('MIN', 'MAX'),
        help='请求延迟范围（秒），格式: 最小值 最大值（默认: 2.0 4.0）'
    )

    parser.add_argument(
        '--allow-external',
        action='store_true',
        help='允许爬取外部链接（默认只爬取同域名链接）'
    )

    parser.add_argument(
        '--exclude',
        nargs='+',
        default=['.pdf', '.zip', '.tar', '.gz', '.exe', '#'],
        help='排除的 URL 模式列表（默认: .pdf .zip .tar .gz .exe #）'
    )

    args = parser.parse_args()

    # 验证 URL 格式
    if not args.url.startswith(('http://', 'https://')):
        parser.error('URL 必须以 http:// 或 https:// 开头')

    # 创建爬虫实例
    scraper = WebScraper(
        start_url=args.url,
        output_dir=args.output,
        depth_limit=args.depth,
        delay_range=tuple(args.delay),
        same_domain_only=not args.allow_external,
        exclude_patterns=args.exclude
    )

    # 开始爬取
    try:
        scraper.crawl()
    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断爬取")
        scraper.print_stats()
    except Exception as e:
        print(f"\n\n✗ 爬取过程出错: {e}")
        scraper.print_stats()


if __name__ == "__main__":
    main()

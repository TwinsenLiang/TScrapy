#!/usr/bin/env python3
"""
TScrapy - 通用网站爬虫工具 (Selenium 版)
支持命令行参数配置 URL、深度、输出目录等，可处理 JavaScript 渲染的页面
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, urlparse
import hashlib
import time
import json
import argparse
from datetime import datetime
from typing import List, Set, Tuple, Optional
import random


class WebScraper:
    """通用网站爬虫 (基于 Selenium)"""

    def __init__(
        self,
        start_url: str,
        output_dir: str = 'scraped_content',
        depth_limit: int = 3,
        delay_range: Tuple[float, float] = (2.0, 4.0),
        same_domain_only: bool = True,
        exclude_patterns: Optional[List[str]] = None,
        headless: bool = True,
        page_load_timeout: int = 30,
        implicit_wait: int = 10
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
            headless: 是否使用无头模式
            page_load_timeout: 页面加载超时时间（秒）
            implicit_wait: 隐式等待时间（秒）
        """
        self.start_url = start_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.depth_limit = depth_limit
        self.delay_range = delay_range
        self.same_domain_only = same_domain_only
        self.exclude_patterns = exclude_patterns or ['.pdf', '.zip', '.tar', '.gz', '.exe', '#']
        self.headless = headless
        self.page_load_timeout = page_load_timeout
        self.implicit_wait = implicit_wait

        # 解析起始域名
        self.start_domain = urlparse(start_url).netloc

        # 初始化 WebDriver
        self.driver = None
        self._setup_driver()

        # 统计信息
        self.stats = {
            'total_pages': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': datetime.now(),
        }

        # 爬取队列（depth 从 1 开始，1 表示起始页面本身）
        self.urls_to_scrape: List[Tuple[str, int]] = [(self.start_url, 1)]  # (url, depth)
        self.scraped_urls: Set[str] = set()

    def _setup_driver(self):
        """初始化 Selenium WebDriver"""
        try:
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument('--headless=new')

            # 通用选项
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # User Agent
            chrome_options.add_argument(
                'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # 使用 webdriver-manager 自动管理驱动
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # 设置超时
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.implicitly_wait(self.implicit_wait)

            print("✓ WebDriver 初始化成功")

        except Exception as e:
            print(f"✗ WebDriver 初始化失败: {e}")
            raise

    def fetch_page(self, url: str) -> Optional[str]:
        """获取页面内容"""
        try:
            # 随机延迟，避免频繁请求
            time.sleep(random.uniform(*self.delay_range))

            print(f"  → 正在请求...")

            # 导航到页面
            self.driver.get(url)

            # 等待页面加载（可以根据需要调整）
            time.sleep(1)

            # 获取渲染后的 HTML
            html_content = self.driver.page_source
            print(f"  → 获取内容大小: {len(html_content)} 字节")

            return html_content

        except TimeoutException:
            print(f"✗ 页面加载超时: {url}")
            return None
        except WebDriverException as e:
            print(f"✗ WebDriver 错误 {url}: {e}")
            return None
        except Exception as e:
            print(f"✗ 请求失败 {url}: {e}")
            return None

    def save_page(self, url: str, html_content: str) -> Optional[BeautifulSoup]:
        """保存页面内容"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # 提取标题
            title = soup.title.string if soup.title else 'Untitled'
            title = self.sanitize_filename(title)

            # 生成唯一文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"{title}_{url_hash}"

            # 保存 HTML
            html_path = self.output_dir / f"{filename}.html"
            html_path.write_text(html_content, encoding='utf-8')

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
        print("TScrapy - 通用网站爬虫 (Selenium 版)")
        print("=" * 70)
        print(f"起始 URL: {self.start_url}")
        print(f"输出目录: {self.output_dir.absolute()}")
        print(f"最大深度: {self.depth_limit}")
        print(f"同域限制: {'是' if self.same_domain_only else '否'}")
        print(f"延迟范围: {self.delay_range[0]}-{self.delay_range[1]} 秒")
        print(f"无头模式: {'是' if self.headless else '否'}")
        print("=" * 70)

        try:
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
                html_content = self.fetch_page(current_url)
                if not html_content:
                    self.stats['failed'] += 1
                    self.scraped_urls.add(current_url)
                    continue

                # 保存页面
                soup = self.save_page(current_url, html_content)
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

        finally:
            # 关闭浏览器
            if self.driver:
                self.driver.quit()
                print("\n✓ WebDriver 已关闭")

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
        description='TScrapy - 通用网站爬虫工具 (Selenium 版)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 爬取网站，深度为 2 层
  python scraper.py https://example.com -d 2

  # 指定输出目录
  python scraper.py https://example.com -o ./output

  # 允许跨域爬取
  python scraper.py https://example.com --allow-external

  # 使用可视模式（调试用）
  python scraper.py https://example.com --no-headless

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

    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='使用可视模式运行浏览器（默认无头模式）'
    )

    parser.add_argument(
        '--page-load-timeout',
        type=int,
        default=30,
        help='页面加载超时时间（秒，默认: 30）'
    )

    parser.add_argument(
        '--implicit-wait',
        type=int,
        default=10,
        help='隐式等待时间（秒，默认: 10）'
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
        exclude_patterns=args.exclude,
        headless=not args.no_headless,
        page_load_timeout=args.page_load_timeout,
        implicit_wait=args.implicit_wait
    )

    # 开始爬取
    try:
        scraper.crawl()
    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断爬取")
        if scraper.driver:
            scraper.driver.quit()
        scraper.print_stats()
    except Exception as e:
        print(f"\n\n✗ 爬取过程出错: {e}")
        import traceback
        traceback.print_exc()
        if scraper.driver:
            scraper.driver.quit()
        scraper.print_stats()


if __name__ == "__main__":
    main()

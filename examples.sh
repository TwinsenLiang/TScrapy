#!/bin/bash
# TScrapy 使用示例脚本
# 这个脚本展示了 TScrapy 的各种使用方式

echo "========================================"
echo "TScrapy 使用示例"
echo "========================================"
echo ""

# 确保虚拟环境已激活
PYTHON="./venv/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "错误: 虚拟环境不存在，请先运行:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo "提示: 以下命令仅供参考，不会实际执行"
echo "您可以复制命令并手动运行"
echo ""

# 示例 1: 基础爬取
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "示例 1: 基础爬取（深度 2 层）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PYTHON scraper.py https://example.com -d 2"
echo ""

# 示例 2: 自定义输出目录
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "示例 2: 自定义输出目录"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PYTHON scraper.py https://example.com -o ./my_output"
echo ""

# 示例 3: 快速爬取（短延迟）
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "示例 3: 快速爬取（延迟 1-2 秒）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PYTHON scraper.py https://example.com --delay 1 2"
echo ""

# 示例 4: 允许外部链接
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "示例 4: 允许爬取外部链接"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PYTHON scraper.py https://example.com --allow-external -d 1"
echo ""

# 示例 5: 排除特定模式
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "示例 5: 排除登录和管理页面"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PYTHON scraper.py https://example.com --exclude /login /admin /api .pdf .zip"
echo ""

# 示例 6: 爬取博客
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "示例 6: 爬取博客文章（实际案例）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PYTHON scraper.py https://blog.example.com -d 3 -o ./blog_backup --delay 3 5"
echo ""

# 示例 7: 爬取文档网站
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "示例 7: 爬取文档网站（大深度）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PYTHON scraper.py https://docs.example.com -d 5 -o ./docs --delay 2 3"
echo ""

# 示例 8: 单页爬取（深度 0）
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "示例 8: 仅爬取单页（不跟随链接）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PYTHON scraper.py https://example.com -d 0"
echo ""

# 示例 9: 查看帮助
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "示例 9: 查看完整帮助信息"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$PYTHON scraper.py --help"
echo ""

echo "========================================"
echo "提示: 要实际运行示例，请复制上述命令"
echo "========================================"

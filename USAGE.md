# TScrapy 使用说明（AI 专用）

## 最简使用

```bash
# 只爬一个页面
python scraper.py https://example.com -d 1

# 爬页面和它的所有链接（最常用）
python scraper.py https://example.com -d 2

# 指定输出目录
python scraper.py https://example.com -d 2 -o ./output
```

## 深度说明

- **depth 1** = 只爬起始页面
- **depth 2** = 起始页面 + 页面上的链接
- **depth 3** = 前两层 + 第二层的链接

## 输出

每个页面生成 3 个文件：
- `标题_哈希.html` - 完整 HTML
- `标题_哈希.txt` - 纯文本内容
- `标题_哈希.json` - 元数据（URL、标题、时间）

## 常见场景

```bash
# 1. 爬取文档网站
python scraper.py https://docs.example.com -d 2 -o ./docs

# 2. 爬取博客文章
python scraper.py https://blog.example.com -d 2 -o ./blog

# 3. 快速测试（只爬首页）
python scraper.py https://example.com -d 1
```

## 仅此而已

就这么简单，不需要其他参数。更多高级选项请看 README.md。

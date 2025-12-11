# TScrapy - 通用网站爬虫脚手架 (Selenium 版)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个强大、灵活的通用网站爬虫工具，基于 Selenium + BeautifulSoup4 构建。**支持爬取 JavaScript 渲染的动态页面**。

---

## ⚡ 快速开始（给 AI 的极简指南）

```bash
# 1. 安装依赖（首次使用）
pip install -r requirements.txt

# 2. 基础用法 - 只爬一个页面
python scraper.py <URL> -d 1

# 3. 爬取页面及其所有链接（推荐）
python scraper.py <URL> -d 2

# 4. 深度爬取（3层）
python scraper.py <URL> -d 3
```

**核心参数**：
- `-d 1`: 只爬首页
- `-d 2`: 爬首页 + 首页的链接（常用）
- `-d 3`: 爬首页 + 第一层链接 + 第二层链接
- `-o 目录`: 指定输出目录（可选）

**输出**：每个页面生成 `.html`、`.txt`、`.json` 三个文件

> 💡 **给 AI 用户**：如果你是 AI，直接看 [USAGE.md](USAGE.md) 获取最简单的使用说明

---

## ✨ 特性

- 🚀 **简单易用** - 命令行一键启动，无需编写代码
- ⚡ **JavaScript 支持** - 使用 Selenium 可爬取动态渲染的页面（React、Vue、Angular 等）
- 🎯 **灵活配置** - 支持自定义爬取深度、输出目录、延迟时间等
- 🔒 **安全可控** - 内置请求延迟、失败重试、域名限制等机制
- 📦 **多格式输出** - 自动保存 HTML、纯文本、JSON 元数据
- 🎨 **友好提示** - 实时显示爬取进度和统计信息
- 🛡️ **错误处理** - 完善的异常处理和错误日志
- 🎭 **可视调试** - 支持无头模式和可视模式，方便调试

## 📋 系统要求

- Python 3.8 或更高版本
- pip 包管理器

## 🔧 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd TScrapy
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt

# webdriver-manager 会自动下载并管理 ChromeDriver，无需手动安装
```

## 🚀 快速开始

### 基础用法

```bash
# 爬取网站，使用默认设置（深度 3 层）
python scraper.py https://example.com
```

### 深度说明

**重要**: 深度从 1 开始计数：
- `depth 1`: 起始页面本身
- `depth 2`: 起始页面上的所有链接
- `depth 3`: 第二层页面上的所有链接
- 以此类推...

```bash
# 只爬取起始页面本身，不爬取任何链接
python scraper.py https://example.com -d 1

# 爬取起始页面 + 起始页面的所有链接（两层）
python scraper.py https://example.com -d 2
```

### 常用参数

```bash
# 指定爬取深度（爬取首页及其链接）
python scraper.py https://example.com -d 2

# 自定义输出目录
python scraper.py https://example.com -o ./my_output

# 调整请求延迟（避免被封）
python scraper.py https://example.com --delay 3 5

# 允许爬取外部链接
python scraper.py https://example.com --allow-external

# 排除特定文件类型
python scraper.py https://example.com --exclude .pdf .zip /login /admin

# 使用可视模式运行（方便调试）
python scraper.py https://example.com --no-headless

# 自定义超时时间
python scraper.py https://example.com --page-load-timeout 60
```

## 📖 详细说明

### 命令行参数

| 参数 | 简写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `url` | - | string | - | 起始 URL（必须包含 http:// 或 https://） |
| `--depth` | `-d` | int | 3 | 最大爬取深度 |
| `--output` | `-o` | string | `scraped_content` | 输出目录路径 |
| `--delay` | - | float float | 2.0 4.0 | 请求延迟范围（秒） |
| `--allow-external` | - | flag | False | 允许爬取外部链接 |
| `--exclude` | - | list | `.pdf .zip ...` | 排除的 URL 模式 |
| `--no-headless` | - | flag | False | 使用可视模式运行浏览器 |
| `--page-load-timeout` | - | int | 30 | 页面加载超时时间（秒） |
| `--implicit-wait` | - | int | 10 | 隐式等待时间（秒） |

### 输出格式

每个爬取的页面会生成三个文件：

1. **HTML 文件** (`页面标题_哈希值.html`) - 完整的 HTML 源码
2. **文本文件** (`页面标题_哈希值.txt`) - 提取的纯文本内容
3. **元数据文件** (`页面标题_哈希值.json`) - 包含 URL、标题、爬取时间等信息

### 使用示例

#### 示例 1: 只爬取单个页面

```bash
# 只爬取首页本身，不跟随任何链接
python scraper.py https://blog.example.com -d 1 -o ./single_page
```

#### 示例 2: 爬取博客首页及所有文章列表

```bash
# 爬取首页和首页上的所有文章链接（两层）
python scraper.py https://blog.example.com -d 2 -o ./blog_backup
```

#### 示例 3: 深度爬取文档网站

```bash
# 爬取文档首页 + 一级目录 + 二级目录（三层）
python scraper.py https://docs.example.com -d 3 --delay 1 2
```

#### 示例 4: 爬取并包含外部链接

```bash
# 只爬取首页及其直接链接，包括外部链接
python scraper.py https://example.com --allow-external -d 2
```

#### 示例 5: 排除登录和管理页面

```bash
python scraper.py https://example.com --exclude /login /admin /api .pdf
```

## ⚙️ 高级配置

### 修改请求头

编辑 `scraper.py` 中的 `session.headers` 部分：

```python
self.session.headers.update({
    'User-Agent': '你的自定义 User-Agent',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    # 添加其他请求头...
})
```

### 自定义排除规则

在命令行或代码中修改 `exclude_patterns`：

```python
exclude_patterns = [
    '.pdf', '.zip',     # 文件类型
    '/login', '/admin', # 路径模式
    '#',                # Fragment
    '/api/',            # API 端点
]
```

## 🔐 安全性说明

### 已实现的安全措施

1. ✅ **请求延迟** - 默认 2-4 秒随机延迟，避免过于频繁的请求
2. ✅ **域名限制** - 默认只爬取同域名链接，防止无限扩散
3. ✅ **文件类型过滤** - 自动排除二进制文件和危险文件类型
4. ✅ **超时控制** - 连接超时 10 秒，读取超时 90 秒
5. ✅ **失败重试** - 自动重试失败的请求（最多 3 次）
6. ✅ **异常处理** - 完善的错误捕获和日志记录
7. ✅ **文件名清理** - 防止路径遍历攻击
8. ✅ **HTTPS 优先** - 支持安全连接

### 使用建议

- ⚠️ **遵守 robots.txt** - 请检查目标网站的 robots.txt 文件
- ⚠️ **合理延迟** - 建议至少设置 1-2 秒延迟，避免对服务器造成压力
- ⚠️ **法律合规** - 确保爬取行为符合目标网站的服务条款和当地法律
- ⚠️ **私人使用** - 本工具仅供学习和个人使用，请勿用于商业目的

## 🛠️ 故障排查

### 问题 1: 连接超时

```
✗ 请求失败: timeout
```

**解决方案**: 增加延迟时间或检查网络连接

```bash
python scraper.py <url> --delay 5 10
```

### 问题 2: 403 Forbidden

```
✗ 请求失败: 403 Client Error
```

**解决方案**: 网站可能检测到爬虫，尝试修改 User-Agent 或增加延迟

### 问题 3: 无内容爬取

**可能原因**:
- 网站使用 JavaScript 动态加载内容，尝试增加 `--implicit-wait` 等待时间
- 域名限制过滤了所有链接

**解决方案**:
- 使用 `--allow-external` 参数允许爬取外部链接
- 增加 `--implicit-wait 20` 等待时间
- 使用 `--no-headless` 可视模式查看页面加载情况

## 📊 性能说明

### 速度基准

- 使用 Selenium WebDriver 同步爬取
- 平均速度: 0.2-0.4 页/秒（取决于延迟设置和页面复杂度）
- 适合爬取规模: 10-1000 个页面
- 支持 JavaScript 渲染的动态页面
- webdriver-manager 自动管理浏览器驱动

### 性能优化建议

- 减少延迟时间（需注意被封风险）
- 降低爬取深度
- 使用更快的网络连接
- 调整超时时间参数

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m '添加某个很棒的特性'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue: [GitHub Issues](https://github.com/yourusername/TScrapy/issues)
- Email: your.email@example.com

## ⚖️ 免责声明

本工具仅供学习和研究使用。使用者需自行承担使用本工具的所有责任，包括但不限于：

- 遵守目标网站的服务条款
- 遵守当地法律法规
- 不进行恶意爬取和攻击行为
- 不侵犯他人知识产权

作者不对使用本工具造成的任何后果负责。

---

⭐ 如果这个项目对你有帮助，请给一个 Star 支持一下！

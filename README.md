# 智慧之塔 · 我的书海

Notion 图书数据库 → 交互式 HTML 仪表盘，通过 GitHub Actions 每日自动同步并部署到 GitHub Pages。

## 功能

- 📊 数据看板：藏书统计、月度趋势、类型分布、阅读活跃热力图
- 📚 书架画廊：真实封面 + 可视化进度条
- 📖 书籍详情页：独立页面展示元信息 + 读书笔记
- 🔥 阅读热力图：基于真实每日阅读打卡数据（页数映射颜色深度）
- 📈 阅读统计：状态分布、类型阅读量、已读页数 Top 10
- 👤 作者排行、📅 入藏时间线
- 🔍 全文搜索（匹配全部结果，下拉列表选择）

## 数据来源

| Notion 数据库 | 说明 |
|---------------|------|
| 图书总览 | 书籍属性、封面、笔记内容 |
| 读书记录 | 每日阅读打卡（日期、页数、媒介） |

## 本地开发

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 填入你的 Notion token 和数据库 ID
vim .env

# 3. 运行数据拉取（按顺序）
python fetch_notion_api.py       # 拉图书数据 + 下载封面
python fetch_content.py          # 拉书籍笔记内容
python fetch_reading_records.py  # 拉阅读打卡记录
python gen_html_v2.py            # 生成 HTML

# 4. 本地预览
cd dist && python3 -m http.server 8080
# 浏览器打开 http://localhost:8080
```

## GitHub Actions 自动部署

### 1. 推送到 GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<你的用户名>/booknotes.git
git push -u origin main
```

### 2. 配置 Secrets

在 GitHub 仓库 Settings → Secrets and variables → Actions → New repository secret：

| Secret 名称 | 值 |
|-------------|-----|
| `NOTION_TOKEN` | 你的 Notion API token |
| `NOTION_BOOKS_DB_ID` | 图书总览数据库 ID |
| `NOTION_RECORDS_DB_ID` | 读书记录数据库 ID |

### 3. 启用 GitHub Pages

Settings → Pages → Source: **GitHub Actions**

### 4. 手动触发首次部署

Actions → Sync & Deploy → Run workflow

部署完成后，访问 `https://<你的用户名>.github.io/booknotes/` 即可看到你的书海仪表盘。

## 自动同步计划

- **每天北京时间 9:00** 自动运行
- 也支持随时手动触发（Actions → Run workflow）
- 每次运行约 2-3 分钟（拉取 122 本书 + 354 条记录 + 121 张封面）

## 文件结构

```
booknotes/
├── .github/workflows/sync.yml  # GitHub Actions 工作流
├── .env.example                # 环境变量模板
├── .env                        # 本地环境变量（gitignored）
├── .gitignore
├── config.py                   # 共享配置（路径、env vars、.env 加载）
├── fetch_notion_api.py         # 拉取图书数据 + 下载封面
├── fetch_content.py            # 拉取书籍笔记内容
├── fetch_reading_records.py    # 拉取阅读打卡记录
├── gen_html_v2.py              # 生成 HTML 仪表盘
├── gen_books.py                # 旧版数据处理（已弃用）
├── gen_html.py                 # 旧版 HTML 生成器（已弃用）
└── dist/                       # 输出目录（gitignored）
    ├── index.html
    ├── covers/
    ├── books_data_full.json
    └── reading_records.json
```

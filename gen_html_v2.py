import json
from config import DATA_FILE, HTML_FILE, DIST_DIR

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

books = data["books"]
stats = data["stats"]
books_js = json.dumps(books, ensure_ascii=False)
stats_js = json.dumps(stats, ensure_ascii=False)

# Build reading date -> pages map from reading records
reading_records = data.get("readingRecords", [])
date_pages = {}
date_records = {}
max_pages_day = 0
for r in reading_records:
    d = r.get("date", "")
    p = r.get("pagesRead", 0) or 0
    if d:
        date_pages[d] = date_pages.get(d, 0) + p
        date_records[d] = date_records.get(d, 0) + 1
        if date_pages[d] > max_pages_day:
            max_pages_day = date_pages[d]

reading_stats = {
    "totalRecords": stats.get("readingRecords", 0),
    "totalPagesRead": stats.get("totalPagesReadFromRecords", 0),
    "uniqueReadingDays": stats.get("uniqueReadingDays", 0),
    "maxPagesDay": max_pages_day,
    "mediumCounts": stats.get("mediumCounts", {}),
}
date_pages_js = json.dumps(date_pages, ensure_ascii=False)
reading_stats_js = json.dumps(reading_stats, ensure_ascii=False)

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#1a1b2e">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="书海">
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icon.svg">
<link rel="icon" type="image/svg+xml" href="icon.svg">
<title>智慧之塔 · 我的书海 · Notion 实时数据</title>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
:root{--bg-primary:#1a1b2e;--bg-secondary:#232544;--bg-tertiary:#2d3055;--bg-card:#232544;--bg-hover:#2d3055;--text-primary:#e8e9f3;--text-secondary:#a0a3c0;--text-tertiary:#6b6e8a;--border:rgba(255,255,255,0.08);--border-hover:rgba(255,255,255,0.15);--accent-purple:#7F77DD;--accent-teal:#1D9E75;--accent-coral:#D85A30;--accent-amber:#EF9F27;--accent-pink:#D4537E;--accent-blue:#378ADD;--accent-green:#639922;--radius-sm:6px;--radius-md:10px;--radius-lg:16px}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",system-ui,sans-serif;background:var(--bg-primary);color:var(--text-primary);min-height:100vh;overflow-x:hidden}
::-webkit-scrollbar{width:8px;height:8px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--bg-tertiary);border-radius:4px}
.app{display:flex;min-height:100vh}

/* ===== Sidebar ===== */
.sidebar{width:220px;background:var(--bg-secondary);border-right:1px solid var(--border);padding:20px 0;position:fixed;height:100vh;overflow-y:auto;z-index:100;transition:transform 0.3s}
.sidebar.hidden{transform:translateX(-100%)}
.sidebar-header{padding:0 24px 24px;border-bottom:1px solid var(--border)}
.logo{display:flex;align-items:center;gap:10px;font-size:18px;font-weight:700}
.logo i{color:var(--accent-purple);font-size:24px}
.logo-sub{font-size:11px;color:var(--text-tertiary);margin-top:2px}
.nav{padding:16px 12px}
.nav-item{display:flex;align-items:center;gap:12px;padding:10px 16px;border-radius:var(--radius-md);cursor:pointer;color:var(--text-secondary);font-size:14px;transition:all 0.2s;margin-bottom:4px;user-select:none}
.nav-item:hover{background:var(--bg-hover);color:var(--text-primary)}
.nav-item.active{background:linear-gradient(135deg,var(--accent-purple),#534AB7);color:#fff;box-shadow:0 4px 12px rgba(127,119,221,0.3)}
.nav-item i{width:20px;text-align:center;font-size:15px}
.nav-badge{margin-left:auto;background:var(--bg-tertiary);color:var(--text-secondary);font-size:11px;padding:2px 8px;border-radius:10px}
.nav-item.active .nav-badge{background:rgba(255,255,255,0.2);color:#fff}
.nav-section-title{font-size:11px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:1px;padding:16px 20px 8px}

/* ===== Sidebar Toggle ===== */
.sidebar-toggle{position:fixed;top:16px;left:236px;z-index:200;width:40px;height:40px;border-radius:var(--radius-md);background:var(--bg-secondary);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--text-primary);transition:left 0.3s,background 0.2s,border-color 0.2s;box-shadow:0 2px 8px rgba(0,0,0,0.3)}
.sidebar-toggle:hover{background:var(--bg-tertiary);border-color:var(--border-hover)}
.sidebar-toggle.collapsed{left:16px}

/* ===== Main ===== */
.main{flex:1;margin-left:220px;padding:24px 32px;min-height:100vh;transition:margin-left 0.3s,padding-left 0.3s}
.main.expanded{margin-left:0;padding-left:72px}
.topbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;flex-wrap:wrap;gap:16px}
.page-title{font-size:24px;font-weight:700}
.page-subtitle{font-size:13px;color:var(--text-secondary);margin-top:4px}
.search-box{display:flex;align-items:center;gap:8px;background:var(--bg-secondary);border:1px solid var(--border);border-radius:var(--radius-md);padding:8px 16px;width:300px}
.search-box input{background:none;border:none;color:var(--text-primary);outline:none;font-size:13px;flex:1}
.search-box i{color:var(--text-tertiary)}
.search-wrapper{position:relative}
.search-dropdown{position:absolute;top:calc(100% + 8px);left:0;right:0;background:var(--bg-secondary);border:1px solid var(--border-hover);border-radius:var(--radius-md);max-height:420px;overflow-y:auto;z-index:500;display:none;box-shadow:0 8px 24px rgba(0,0,0,0.4)}
.search-dropdown.active{display:block;animation:fadeIn 0.2s}
.search-result-item{display:flex;align-items:center;gap:10px;padding:10px 14px;cursor:pointer;transition:background 0.15s;border-bottom:1px solid var(--border)}
.search-result-item:last-child{border-bottom:none}
.search-result-item:hover{background:var(--bg-hover)}
.search-result-cover{width:28px;height:40px;border-radius:4px;object-fit:cover;flex-shrink:0;background:var(--bg-tertiary)}
.search-result-info{flex:1;min-width:0}
.search-result-title{font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.search-result-sub{font-size:11px;color:var(--text-tertiary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.search-no-result{padding:20px;text-align:center;color:var(--text-tertiary);font-size:13px}
.search-count{padding:6px 14px;font-size:11px;color:var(--text-tertiary);border-bottom:1px solid var(--border);background:var(--bg-primary)}
.view{display:none;animation:fadeIn 0.3s}.view.active{display:block}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* ===== Stats Cards ===== */
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:24px}
.stat-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);padding:20px;position:relative;overflow:hidden;transition:transform 0.2s,border-color 0.2s}
.stat-card:hover{transform:translateY(-2px);border-color:var(--border-hover)}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--accent)}
.stat-icon{width:44px;height:44px;border-radius:var(--radius-md);display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:12px}
.stat-value{font-size:28px;font-weight:700}
.stat-label{font-size:13px;color:var(--text-secondary);margin-top:4px}
.stat-trend{font-size:12px;margin-top:8px;color:var(--text-tertiary)}

/* ===== Panels & Charts ===== */
.dashboard-grid{display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:16px}
.dashboard-grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.panel{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);padding:20px}
.panel-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.panel-title{font-size:15px;font-weight:600;display:flex;align-items:center;gap:8px}
.panel-title i{color:var(--accent-purple)}
.chart-container{position:relative;height:240px}

/* ===== Gallery (Bookshelf Cards) ===== */
.gallery-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:20px;padding:8px 0 32px}
.gallery-item{cursor:pointer;display:flex;flex-direction:column;gap:10px;transition:transform 0.25s ease}
.gallery-item:hover{transform:translateY(-6px)}
.gallery-cover{position:relative;aspect-ratio:3/4.2;border-radius:var(--radius-md);overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,0.35);transition:box-shadow 0.25s ease;background:var(--bg-tertiary)}
.gallery-item:hover .gallery-cover{box-shadow:0 12px 28px rgba(0,0,0,0.5)}
.gallery-cover img{width:100%;height:100%;object-fit:cover;display:block}
.gallery-cover-fallback{width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:16px 12px;text-align:center;position:relative}
.gallery-cover-fallback::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:rgba(0,0,0,0.25)}
.gallery-cover-title{font-size:15px;font-weight:700;color:rgba(255,255,255,0.97);line-height:1.35;text-shadow:0 1px 3px rgba(0,0,0,0.4);margin-bottom:8px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.gallery-cover-author{font-size:11px;color:rgba(255,255,255,0.7);text-shadow:0 1px 2px rgba(0,0,0,0.4)}
.gallery-meta{padding:0 2px}
.gallery-title{font-size:13px;font-weight:600;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.4}
.gallery-progress-track{height:4px;background:var(--bg-tertiary);border-radius:2px;overflow:hidden;margin-top:6px}
.gallery-progress-bar-fill{height:100%;border-radius:2px;transition:width 0.6s}

/* ===== Bookshelf Controls ===== */
.bookshelf-controls{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;align-items:center}
.filter-chip{padding:6px 14px;border-radius:20px;background:var(--bg-secondary);border:1px solid var(--border);color:var(--text-secondary);font-size:12px;cursor:pointer;transition:all 0.2s;user-select:none}
.filter-chip:hover{border-color:var(--border-hover);color:var(--text-primary)}
.filter-chip.active{background:var(--accent-purple);color:#fff;border-color:var(--accent-purple)}
.sort-select{background:var(--bg-secondary);border:1px solid var(--border);color:var(--text-primary);border-radius:20px;padding:6px 14px;font-size:12px;outline:none;cursor:pointer}

/* ===== Heatmap ===== */
.heatmap-wrapper{overflow-x:auto;padding:8px 0}
.heatmap{display:grid;grid-template-columns:repeat(53,1fr);gap:3px;min-width:700px}
.heatmap-cell{aspect-ratio:1;border-radius:2px;background:var(--bg-tertiary);transition:transform 0.15s;cursor:pointer}
.heatmap-cell:hover{transform:scale(1.4);z-index:5;position:relative}
.heatmap-legend{display:flex;align-items:center;gap:4px;font-size:11px;color:var(--text-tertiary);margin-top:12px;justify-content:flex-end}
.heatmap-legend-cell{width:12px;height:12px;border-radius:2px}

/* ===== Authors ===== */
.author-row{display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid var(--border)}
.author-bar{flex:1;height:8px;background:var(--bg-tertiary);border-radius:4px;overflow:hidden}
.author-bar-fill{height:100%;border-radius:4px}

/* ===== Timeline ===== */
.timeline{position:relative;padding-left:24px}
.timeline::before{content:'';position:absolute;left:8px;top:0;bottom:0;width:2px;background:var(--border)}
.timeline-item{position:relative;margin-bottom:20px}
.timeline-item::before{content:'';position:absolute;left:-20px;top:4px;width:12px;height:12px;border-radius:50%;background:var(--accent-purple);border:2px solid var(--bg-primary)}
.timeline-date{font-size:12px;color:var(--text-tertiary);margin-bottom:4px}
.timeline-content{font-size:14px}
.timeline-content strong{color:var(--accent-purple)}

/* ===== Progress Bar (shared) ===== */
.progress-bar{height:8px;background:var(--bg-tertiary);border-radius:4px;overflow:hidden;margin-top:8px}
.progress-fill{height:100%;background:linear-gradient(90deg,var(--accent-purple),var(--accent-teal));border-radius:4px;transition:width 0.6s}

/* ===== Book Detail Page ===== */
.book-detail-nav{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px}
.back-btn{background:var(--bg-secondary);border:1px solid var(--border);color:var(--text-primary);padding:8px 18px;border-radius:var(--radius-md);cursor:pointer;font-size:13px;transition:all 0.2s;display:flex;align-items:center;gap:8px}
.back-btn:hover{background:var(--bg-tertiary);border-color:var(--border-hover)}
.notion-source{color:var(--text-secondary);font-size:12px;text-decoration:none;display:flex;align-items:center;gap:6px;transition:color 0.2s}
.notion-source:hover{color:var(--accent-purple)}
.book-detail-hero{display:flex;gap:36px;margin-bottom:32px;align-items:flex-start}
.book-detail-cover{width:180px;height:252px;border-radius:var(--radius-md);overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,0.4);flex-shrink:0;background:var(--bg-tertiary)}
.book-detail-cover img{width:100%;height:100%;object-fit:cover;display:block}
.book-detail-cover-fallback{width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:18px;font-weight:700;color:#fff;text-align:center;padding:20px;line-height:1.4}
.book-detail-info{flex:1;min-width:0}
.book-detail-info h1{font-size:28px;margin-bottom:8px;line-height:1.3}
.book-detail-author{color:var(--text-secondary);font-size:15px;margin-bottom:16px;display:flex;align-items:center;gap:6px}
.book-detail-tags{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
.book-detail-tags .tag{background:var(--bg-secondary);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:12px;color:var(--text-secondary);display:flex;align-items:center;gap:4px}
.book-detail-tags .tag i{font-size:10px;opacity:0.7}
.book-detail-progress{margin-bottom:16px}
.progress-label{display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px}
.progress-pct{color:var(--accent-purple);font-weight:600}
.progress-bar-lg{height:10px;background:var(--bg-tertiary);border-radius:5px;overflow:hidden}
.progress-fill-lg{height:100%;background:linear-gradient(90deg,var(--accent-purple),var(--accent-teal));border-radius:5px;transition:width 0.6s}
.book-detail-stats{display:flex;gap:20px;font-size:12px;color:var(--text-tertiary);flex-wrap:wrap}
.book-detail-stats span{display:flex;align-items:center;gap:5px}
.book-detail-notes{border-top:1px solid var(--border);padding-top:28px}
.book-detail-notes h2{font-size:18px;margin-bottom:20px;display:flex;align-items:center;gap:8px}
.book-detail-notes h2 i{color:var(--accent-purple)}
.note-section{margin-bottom:24px}
.note-section-title{font-size:15px;font-weight:700;color:var(--accent-purple);margin-bottom:12px;padding-left:12px;border-left:3px solid var(--accent-purple)}
.note-item{font-size:13px;line-height:1.8;color:var(--text-secondary);margin-bottom:10px;padding-left:4px}
.note-quote{font-size:13px;line-height:1.8;color:var(--text-primary);margin-bottom:12px;padding:12px 16px;background:var(--bg-primary);border-radius:var(--radius-sm);border-left:3px solid var(--accent-amber);position:relative}
.note-quote i{color:var(--accent-amber);font-size:11px;margin-right:6px;opacity:0.6}
.note-empty{text-align:center;padding:40px 20px;color:var(--text-tertiary);font-size:14px}
.note-empty i{font-size:36px;display:block;margin-bottom:12px;opacity:0.3}

/* ===== Misc ===== */
.empty-state{text-align:center;padding:48px 20px;color:var(--text-tertiary)}
.empty-state i{font-size:48px;margin-bottom:16px;opacity:0.3}
.notion-badge{position:fixed;bottom:16px;right:16px;background:var(--bg-secondary);border:1px solid var(--border);border-radius:20px;padding:6px 14px;font-size:11px;color:var(--text-tertiary);display:flex;align-items:center;gap:6px;z-index:50}
.notion-badge i{color:#fff}

/* ===== View Selector Dropdown ===== */
.view-selector-wrap{position:relative}
.view-selector{display:inline-flex;align-items:center;gap:8px;cursor:pointer;font-size:24px;font-weight:700;transition:color 0.2s;user-select:none}
.view-selector:hover{color:var(--accent-purple)}
.view-selector-caret{font-size:14px;color:var(--text-tertiary);transition:transform 0.3s}
.view-selector-wrap.menu-open .view-selector-caret{transform:rotate(180deg)}
.view-menu{position:absolute;top:calc(100% + 12px);left:0;background:var(--bg-secondary);border:1px solid var(--border-hover);border-radius:var(--radius-md);min-width:200px;z-index:500;display:none;box-shadow:0 8px 24px rgba(0,0,0,0.4);overflow:hidden;padding:4px 0}
.view-menu.active{display:block;animation:fadeIn 0.2s}
.view-menu-section{font-size:11px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:1px;padding:10px 16px 4px}
.view-menu-item{padding:8px 16px;cursor:pointer;font-size:14px;color:var(--text-secondary);transition:all 0.15s}
.view-menu-item:hover{background:var(--bg-hover);color:var(--text-primary)}
.view-menu-item.current{color:var(--accent-purple);font-weight:600}

/* ===== Collapsible Panels ===== */
.panel-header{cursor:pointer;position:relative;padding-right:24px;user-select:none}
.panel-header::after{content:'\\25BE';position:absolute;right:0;top:50%;transform:translateY(-50%);color:var(--text-tertiary);font-size:14px;transition:transform 0.3s}
.panel.collapsed .panel-header::after{transform:translateY(-50%) rotate(-90deg)}
.panel.collapsed > *:not(.panel-header){display:none}
.panel.collapsed .panel-header{margin-bottom:0}

/* ===== Responsive ===== */
.bottom-nav{display:none}

@media (max-width:900px){
  .sidebar{transform:translateX(-100%)}
  .sidebar.hidden{transform:translateX(-100%)}
  .main{margin-left:0;padding:14px 14px 80px}
  .main.expanded{padding-left:14px;padding-right:14px}
  .sidebar-toggle{display:none}
  .dashboard-grid,.dashboard-grid-2{grid-template-columns:1fr}
  .book-detail-hero{flex-direction:column;gap:20px;align-items:center;text-align:center}
  .book-detail-cover{width:140px;height:196px}
  .book-detail-info{width:100%}
  .book-detail-tags{justify-content:center}
  .book-detail-stats{justify-content:center}
  .search-box{width:100%}
  .topbar{flex-direction:column;align-items:stretch;gap:10px;margin-bottom:16px}
  .view-selector{font-size:20px}
  .bottom-nav{display:flex;position:fixed;bottom:0;left:0;right:0;background:var(--bg-secondary);border-top:1px solid var(--border);z-index:200;padding:6px 0 calc(6px + env(safe-area-inset-bottom,0px));justify-content:space-around}
  .bottom-nav-item{display:flex;flex-direction:column;align-items:center;gap:3px;padding:6px 10px;cursor:pointer;color:var(--text-tertiary);font-size:10px;transition:color 0.2s;min-width:50px}
  .bottom-nav-item.active{color:var(--accent-purple)}
  .bottom-nav-item i{font-size:18px}
}
@media (max-width:640px){
  .main{padding:12px 12px 80px}
  .main.expanded{padding-left:12px;padding-right:12px}
  .stats-grid{grid-template-columns:repeat(2,1fr);gap:10px}
  .stat-card{padding:14px}
  .stat-value{font-size:20px}
  .stat-icon{width:34px;height:34px;font-size:15px}
  .stat-label{font-size:11px}
  .stat-trend{font-size:10px}
  .gallery-grid{grid-template-columns:repeat(2,1fr);gap:12px}
  .gallery-cover-title{font-size:13px}
  .gallery-cover-author{font-size:10px}
  .gallery-title{font-size:12px}
  .gallery-progress-track{height:3px}
  .panel{padding:14px}
  .panel-title{font-size:13px}
  .chart-container{height:200px}
  .page-title{font-size:18px}
  .page-subtitle{font-size:11px}
  .view-selector{font-size:17px}
  .book-detail-info h1{font-size:20px}
  .book-detail-cover{width:110px;height:154px}
  .note-item{font-size:12px;line-height:1.7}
  .note-quote{font-size:12px;padding:10px 12px}
  .note-section-title{font-size:13px}
  .filter-chip{padding:5px 10px;font-size:11px}
  .search-box{padding:6px 12px}
  .search-box input{font-size:12px}
  .heatmap{min-width:600px}
  .author-row{gap:8px}
  .author-row>div:first-child{width:80px;font-size:12px}
  .back-btn{padding:6px 14px;font-size:12px}
  .timeline{padding-left:20px}
  .notion-badge{display:none}
}
@media (max-width:380px){
  .stats-grid{grid-template-columns:1fr}
  .gallery-grid{grid-template-columns:repeat(2,1fr)}
}
</style>
</head>
<body>
<div class="sidebar-toggle" id="sidebarToggle" onclick="toggleSidebar()"><i class="fas fa-bars" id="toggleIcon"></i></div>
<div class="app">
<aside class="sidebar" id="sidebar">
<div class="sidebar-header"><div class="logo"><i class="fas fa-book-open-reader"></i><div><div>智慧之塔</div><div class="logo-sub">Notion API 实时数据</div></div></div></div>
<nav class="nav">
<div class="nav-section-title">总览</div>
<div class="nav-item active" data-view="dashboard"><i class="fas fa-gauge-high"></i> 数据看板</div>
<div class="nav-item" data-view="bookshelf"><i class="fas fa-bookmark"></i> 书架<span class="nav-badge" id="bookCountBadge">0</span></div>
<div class="nav-section-title">分析</div>
<div class="nav-item" data-view="stats"><i class="fas fa-chart-line"></i> 阅读统计</div>
<div class="nav-item" data-view="authors"><i class="fas fa-user-pen"></i> 作者排行</div>
<div class="nav-item" data-view="timeline"><i class="fas fa-clock-rotate-left"></i> 入藏时间线</div>
<div class="nav-section-title">管理</div>
<div class="nav-item" data-view="reading"><i class="fas fa-book-open"></i> 在读书籍<span class="nav-badge" id="readingBadge">0</span></div>
<div class="nav-item" data-view="finished"><i class="fas fa-check-double"></i> 已读书籍<span class="nav-badge" id="finishedBadge">0</span></div>
<div class="nav-item" data-view="unread"><i class="fas fa-book-bookmark"></i> 待读书籍<span class="nav-badge" id="unreadBadge">0</span></div>
</nav>
</aside>
<main class="main" id="mainContent">
<div class="topbar">
<div class="view-selector-wrap" id="viewSelectorWrap"><div class="view-selector" onclick="toggleViewMenu(event)"><span id="pageTitle">数据看板</span><i class="fas fa-chevron-down view-selector-caret"></i></div><div class="page-subtitle" id="pageSubtitle">你的书海全景</div><div class="view-menu" id="viewMenu"><div class="view-menu-section">总览</div><div class="view-menu-item" onclick="switchViewFromMenu('dashboard')">数据看板</div><div class="view-menu-item" onclick="switchViewFromMenu('bookshelf')">书架</div><div class="view-menu-section">分析</div><div class="view-menu-item" onclick="switchViewFromMenu('stats')">阅读统计</div><div class="view-menu-item" onclick="switchViewFromMenu('authors')">作者排行</div><div class="view-menu-item" onclick="switchViewFromMenu('timeline')">入藏时间线</div><div class="view-menu-section">管理</div><div class="view-menu-item" onclick="switchViewFromMenu('reading')">在读书籍</div><div class="view-menu-item" onclick="switchViewFromMenu('finished')">已读书籍</div><div class="view-menu-item" onclick="switchViewFromMenu('unread')">待读书籍</div></div></div>
<div class="search-wrapper"><div class="search-box"><i class="fas fa-search"></i><input type="text" placeholder="搜索书名或作者..." id="globalSearch"></div><div class="search-dropdown" id="searchDropdown"></div></div>
</div>

<div class="view active" id="view-dashboard">
<div class="stats-grid" id="statsGrid"></div>
<div class="dashboard-grid">
<div class="panel"><div class="panel-header"><div class="panel-title"><i class="fas fa-chart-area"></i> 月度入藏趋势</div></div><div class="chart-container"><canvas id="trendChart" role="img" aria-label="月度入藏趋势">趋势图</canvas></div></div>
<div class="panel"><div class="panel-header"><div class="panel-title"><i class="fas fa-chart-pie"></i> 类型分布</div></div><div class="chart-container"><canvas id="categoryChart" role="img" aria-label="类型分布饼图">分类饼图</canvas></div></div>
</div>
<div class="dashboard-grid-2">
<div class="panel"><div class="panel-header"><div class="panel-title"><i class="fas fa-fire"></i> 阅读活跃热力图</div></div><div class="heatmap-wrapper"><div class="heatmap" id="heatmap"></div></div><div class="heatmap-legend"><span>少</span><div class="heatmap-legend-cell" style="background:#2d3055"></div><div class="heatmap-legend-cell" style="background:#3F3489"></div><div class="heatmap-legend-cell" style="background:#534AB7"></div><div class="heatmap-legend-cell" style="background:#7F77DD"></div><div class="heatmap-legend-cell" style="background:#AFA9EC"></div><span>多</span></div></div>
<div class="panel"><div class="panel-header"><div class="panel-title"><i class="fas fa-list-check"></i> 最近入藏</div></div><div id="recentBooks"></div></div>
</div>
</div>

<div class="view" id="view-bookshelf">
<div class="bookshelf-controls"><span style="font-size:12px;color:var(--text-tertiary);margin-right:4px;">分类:</span><span id="shelfFilters"></span><select class="sort-select" id="sortSelect"><option value="time">按入藏时间</option><option value="progress">按阅读进度</option><option value="pages">按页数</option><option value="rating">按评分</option><option value="title">按书名</option></select></div>
<div id="bookshelf"></div>
</div>

<div class="view" id="view-stats">
<div class="dashboard-grid">
<div class="panel"><div class="panel-header"><div class="panel-title"><i class="fas fa-chart-pie"></i> 阅读状态分布</div></div><div class="chart-container"><canvas id="statusChart" role="img" aria-label="阅读状态分布">状态图</canvas></div></div>
<div class="panel"><div class="panel-header"><div class="panel-title"><i class="fas fa-chart-column"></i> 类型阅读量</div></div><div class="chart-container"><canvas id="catReadChart" role="img" aria-label="类型阅读量">类型图</canvas></div></div>
</div>
<div class="panel"><div class="panel-header"><div class="panel-title"><i class="fas fa-chart-simple"></i> 已读页数 Top 10</div></div><div class="chart-container" style="height:320px;"><canvas id="pagesChart" role="img" aria-label="已读页数排行">页数图</canvas></div></div>
</div>

<div class="view" id="view-authors"><div class="panel"><div class="panel-header"><div class="panel-title"><i class="fas fa-user-pen"></i> 作者藏书排行</div></div><div id="authorList"></div></div></div>
<div class="view" id="view-timeline"><div class="panel"><div class="panel-header"><div class="panel-title"><i class="fas fa-clock-rotate-left"></i> 入藏时间线</div></div><div class="timeline" id="timeline"></div></div></div>
<div class="view" id="view-reading"><div id="readingContainer"></div></div>
<div class="view" id="view-finished"><div id="finishedContainer"></div></div>
<div class="view" id="view-unread"><div id="unreadContainer"></div></div>
<div class="view" id="view-bookdetail"><div id="bookDetailContent"></div></div>
</main>
</div>
<nav class="bottom-nav" id="bottomNav">
<div class="bottom-nav-item active" data-view="dashboard"><i class="fas fa-gauge-high"></i><span>看板</span></div>
<div class="bottom-nav-item" data-view="bookshelf"><i class="fas fa-bookmark"></i><span>书架</span></div>
<div class="bottom-nav-item" data-view="stats"><i class="fas fa-chart-line"></i><span>统计</span></div>
<div class="bottom-nav-item" data-view="reading"><i class="fas fa-book-open"></i><span>在读</span></div>
<div class="bottom-nav-item" onclick="focusSearch()"><i class="fas fa-search"></i><span>搜索</span></div>
</nav>
<div class="notion-badge"><i class="fas fa-database"></i> Notion API · 图书总览 · 实时数据</div>
<script>
const BOOKS=''' + books_js + ''';
const STATS=''' + stats_js + ''';
const READING_DATE_PAGES=''' + date_pages_js + ''';
const READING_STATS=''' + reading_stats_js + ''';
let currentView='dashboard',previousView='dashboard',activeShelfCat='all',sortMode='time',charts={};

/* ===== Sidebar Toggle ===== */
function toggleSidebar(){
  document.getElementById('sidebar').classList.toggle('hidden');
  document.getElementById('mainContent').classList.toggle('expanded');
  document.getElementById('sidebarToggle').classList.toggle('collapsed');
}
function hideSidebar(){
  document.getElementById('sidebar').classList.add('hidden');
  document.getElementById('mainContent').classList.add('expanded');
  document.getElementById('sidebarToggle').classList.add('collapsed');
}
if(window.innerWidth<900){hideSidebar();}

/* ===== View Selector Menu ===== */
function toggleViewMenu(e){
  if(e)e.stopPropagation();
  var wrap=document.getElementById('viewSelectorWrap');
  var menu=document.getElementById('viewMenu');
  wrap.classList.toggle('menu-open');
  menu.classList.toggle('active');
  var currentTitle=document.getElementById('pageTitle').textContent;
  menu.querySelectorAll('.view-menu-item').forEach(function(item){
    item.classList.toggle('current',item.textContent===currentTitle);
  });
}
function closeViewMenu(){
  document.getElementById('viewSelectorWrap').classList.remove('menu-open');
  document.getElementById('viewMenu').classList.remove('active');
}
function switchViewFromMenu(view){
  closeViewMenu();
  switchView(view);
}
document.addEventListener('click',function(e){
  if(!e.target.closest('.view-selector-wrap'))closeViewMenu();
});

/* ===== Panel Collapse (event delegation) ===== */
document.addEventListener('click',function(e){
  var header=e.target.closest('.panel-header');
  if(!header)return;
  var panel=header.parentElement;
  panel.classList.toggle('collapsed');
  if(!panel.classList.contains('collapsed')){
    setTimeout(function(){Object.keys(charts).forEach(function(k){if(charts[k])charts[k].resize();});},100);
  }
});

document.querySelectorAll('.nav-item').forEach(item=>item.addEventListener('click',()=>switchView(item.dataset.view)));
document.querySelectorAll('.bottom-nav-item[data-view]').forEach(function(item){item.addEventListener('click',function(){switchView(item.dataset.view);});});
function focusSearch(){document.getElementById('globalSearch').focus();}

function switchView(view){
  closeViewMenu();
  previousView=currentView;
  currentView=view;
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  var navEl=document.querySelector('.nav-item[data-view="'+view+'"]');
  if(navEl)navEl.classList.add('active');
  document.querySelectorAll('.bottom-nav-item').forEach(function(n){n.classList.remove('active');});
  var bnEl=document.querySelector('.bottom-nav-item[data-view="'+view+'"]');
  if(bnEl)bnEl.classList.add('active');
  document.querySelectorAll('.view').forEach(v=>v.classList.remove('active'));
  var viewEl=document.getElementById('view-'+view);
  if(viewEl)viewEl.classList.add('active');
  var titles={dashboard:['数据看板',''+STATS.total+'本藏书 · '+STATS.finished+'本已读 · '+(READING_STATS.uniqueReadingDays||0)+'天阅读'],bookshelf:['书架','画廊式呈现，真实封面'],stats:['阅读统计','数据会说话'],authors:['作者排行','谁陪你走过最多书页'],timeline:['入藏时间线','每本书来到你身边的时刻'],reading:['在读书籍','正在翻阅的'+STATS.reading+'本'],finished:['已读书籍','已经读完的'+STATS.finished+'本'],unread:['待读书籍','等待开启的'+STATS.unread+'本'],bookdetail:['书籍详情','']};
  var t=titles[view]||['',''];
  document.getElementById('pageTitle').textContent=t[0];
  document.getElementById('pageSubtitle').textContent=t[1];
  if(view==='bookshelf')renderBookshelf();
  if(view==='stats')renderStats();
  if(view==='authors')renderAuthors();
  if(view==='timeline')renderTimeline();
  if(view==='reading')renderGalleryList('readingContainer',function(b){return b.status==='在读';});
  if(view==='finished')renderGalleryList('finishedContainer',function(b){return b.status==='已读';});
  if(view==='unread')renderGalleryList('unreadContainer',function(b){return b.status==='未读';});
  hideSidebar();
  window.scrollTo(0,0);
}

/* ===== Cover HTML helper ===== */
function coverHtml(b){
  if(b.coverLocal){
    return '<div class="gallery-cover"><img src="'+b.coverLocal+'" alt="'+b.title+'" loading="lazy"></div>';
  }else{
    return '<div class="gallery-cover" style="background:linear-gradient(135deg,'+b.color+' 0%,'+b.color+'cc 60%,'+b.color+'99 100%);"><div class="gallery-cover-fallback"><div class="gallery-cover-title">'+b.title+'</div><div class="gallery-cover-author">'+b.author+'</div></div></div>';
  }
}

/* ===== Dashboard ===== */
function renderDashboard(){
  var cards=[
    {icon:'fa-book',color:'#7F77DD',bg:'rgba(127,119,221,0.15)',value:STATS.total,label:'藏书总数',trend:STATS.finished+'本已读 · '+STATS.reading+'本在读'},
    {icon:'fa-check-double',color:'#1D9E75',bg:'rgba(29,158,117,0.15)',value:STATS.finished,label:'已读完',trend:'完成率 '+Math.round(STATS.finished/STATS.total*100)+'%'},
    {icon:'fa-book-open',color:'#EF9F27',bg:'rgba(239,159,39,0.15)',value:STATS.reading,label:'阅读中',trend:'正在翻阅的书海'},
    {icon:'fa-book-bookmark',color:'#378ADD',bg:'rgba(55,138,221,0.15)',value:STATS.unread,label:'待读',trend:'等待开启的旅程'},
    {icon:'fa-file-lines',color:'#D4537E',bg:'rgba(212,83,126,0.15)',value:STATS.totalPages.toLocaleString(),label:'总页数',trend:'已读 '+STATS.readPages.toLocaleString()+' 页 ('+Math.round(STATS.readPages/STATS.totalPages*100)+'%)'},
    {icon:'fa-image',color:'#639922',bg:'rgba(99,153,34,0.15)',value:STATS.booksWithCover,label:'封面已同步',trend:'真实封面图片'},
    {icon:'fa-feather-pointed',color:'#D4537E',bg:'rgba(212,83,126,0.15)',value:STATS.booksWithContent||0,label:'读书笔记',trend:'已整理笔记的书籍'},
    {icon:'fa-calendar-day',color:'#378ADD',bg:'rgba(55,138,221,0.15)',value:READING_STATS.uniqueReadingDays||0,label:'阅读天数',trend:'累计 '+READING_STATS.totalRecords+' 条打卡'},
    {icon:'fa-book-reader',color:'#1D9E75',bg:'rgba(29,158,117,0.15)',value:(READING_STATS.totalPagesRead||0).toLocaleString(),label:'累计阅读页数',trend:'来自读书记录数据库'},
    {icon:'fa-bolt',color:'#EF9F27',bg:'rgba(239,159,39,0.15)',value:READING_STATS.maxPagesDay||0,label:'单日最多',trend:'页 · 燃烧的一天'},
  ];
  document.getElementById('statsGrid').innerHTML=cards.map(function(c){return '<div class="stat-card" style="--accent:'+c.color+'"><div class="stat-icon" style="background:'+c.bg+';color:'+c.color+'"><i class="fas '+c.icon+'"></i></div><div class="stat-value">'+c.value+'</div><div class="stat-label">'+c.label+'</div><div class="stat-trend">'+c.trend+'</div></div>';}).join('');
  document.getElementById('bookCountBadge').textContent=STATS.total;
  document.getElementById('readingBadge').textContent=STATS.reading;
  document.getElementById('finishedBadge').textContent=STATS.finished;
  document.getElementById('unreadBadge').textContent=STATS.unread;
  renderTrendChart();renderCategoryChart();renderHeatmap();renderRecentBooks();
}

function renderTrendChart(){
  var months={};
  BOOKS.forEach(function(b){var m=b.createdTime.slice(0,7);if(m)months[m]=(months[m]||0)+1;});
  var keys=Object.keys(months).sort();
  var ctx=document.getElementById('trendChart');
  if(charts.trend)charts.trend.destroy();
  charts.trend=new Chart(ctx,{type:'bar',data:{labels:keys,datasets:[{data:keys.map(function(k){return months[k];}),backgroundColor:'#7F77DD',borderRadius:6}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{color:'rgba(255,255,255,0.05)'},ticks:{color:'#a0a3c0',maxRotation:45}},y:{grid:{color:'rgba(255,255,255,0.05)'},ticks:{color:'#a0a3c0'}}}}});
}

function renderCategoryChart(){
  var ctx=document.getElementById('categoryChart');
  if(charts.category)charts.category.destroy();
  var cats=Object.keys(STATS.categories);
  var colors=cats.map(function(c){var m={"小说":"#7F77DD","科幻":"#378ADD","历史":"#BA7517","社科":"#1D9E75","军事":"#D85A30","写作":"#639922","经济":"#EF9F27","讽刺":"#D4537E","未分类":"#5F5E5A"};return m[c]||'#5F5E5A';});
  charts.category=new Chart(ctx,{type:'doughnut',data:{labels:cats,datasets:[{data:cats.map(function(c){return STATS.categories[c];}),backgroundColor:colors,borderWidth:0,spacing:4}]},options:{responsive:true,maintainAspectRatio:false,cutout:'60%',plugins:{legend:{position:'right',labels:{color:'#a0a3c0',font:{size:11},padding:10,usePointStyle:true,pointStyle:'circle'}}}}});
}

function renderHeatmap(){
  var container=document.getElementById('heatmap');
  var colors=['#2d3055','#3F3489','#534AB7','#7F77DD','#AFA9EC'];
  var html='';
  for(var i=0;i<365;i++){
    var d=new Date();d.setDate(d.getDate()-(364-i));
    var dStr=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
    var pages=READING_DATE_PAGES[dStr]||0;
    var level=0;
    if(pages>=200)level=4;else if(pages>=80)level=3;else if(pages>=30)level=2;else if(pages>0)level=1;
    var tip=(d.getMonth()+1)+'月'+d.getDate()+'日'+(pages?' · 阅读'+pages+'页':'');
    html+='<div class="heatmap-cell" style="background:'+colors[level]+'" title="'+tip+'"></div>';
  }
  container.innerHTML=html;
}

function renderRecentBooks(){
  var recent=BOOKS.slice(0,8);
  document.getElementById('recentBooks').innerHTML=recent.map(function(b){
    var cover=b.coverLocal?'<img src="'+b.coverLocal+'" style="width:32px;height:44px;border-radius:4px;object-fit:cover;flex-shrink:0;">':'<div style="width:32px;height:44px;border-radius:4px;background:'+b.color+';flex-shrink:0;"></div>';
    return '<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--border);cursor:pointer;" onclick="openBookDetail('+b.id+')">'+cover+'<div style="flex:1;min-width:0;"><div style="font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'+b.title+'</div><div style="font-size:11px;color:var(--text-tertiary);">'+b.author+' · '+b.category+'</div></div><div style="text-align:right;"><div style="font-size:12px;color:var(--accent-purple);font-weight:600;">'+b.progress+'%</div><div style="font-size:10px;color:var(--text-tertiary);">'+b.readPages+'/'+(b.pages||'?')+'页</div></div></div>';
  }).join('');
}

/* ===== Bookshelf ===== */
function renderBookshelf(){
  var cats=['all'].concat(Object.keys(STATS.categories));
  document.getElementById('shelfFilters').innerHTML=cats.map(function(c){return '<span class="filter-chip '+(c===activeShelfCat?'active':'')+'" onclick="filterShelf(\\''+c+'\\')">'+(c==='all'?'全部('+STATS.total+')':c+'('+STATS.categories[c]+')')+'</span>';}).join('');
  document.getElementById('sortSelect').onchange=function(e){sortMode=e.target.value;renderBookshelf();};
  var filtered=activeShelfCat==='all'?BOOKS.slice():BOOKS.filter(function(b){return b.category===activeShelfCat;});
  if(sortMode==='progress')filtered.sort(function(a,b){return b.progress-a.progress;});
  else if(sortMode==='pages')filtered.sort(function(a,b){return (b.pages||0)-(a.pages||0);});
  else if(sortMode==='rating')filtered.sort(function(a,b){return (b.rating||0)-(a.rating||0);});
  else if(sortMode==='title')filtered.sort(function(a,b){return a.title.localeCompare(b.title,'zh');});
  document.getElementById('bookshelf').innerHTML='<div class="gallery-grid">'+filtered.map(function(b){
    return '<div class="gallery-item" onclick="openBookDetail('+b.id+')">'+coverHtml(b)+'<div class="gallery-meta"><div class="gallery-title">'+b.title+'</div><div class="gallery-progress-track"><div class="gallery-progress-bar-fill" style="width:'+b.progress+'%;background:'+b.color+'"></div></div></div></div>';
  }).join('')+'</div>';
}

function filterShelf(cat){activeShelfCat=cat;renderBookshelf();}

/* ===== Gallery List (reading/finished/unread) ===== */
function renderGalleryList(containerId,filterFn){
  var list=BOOKS.filter(filterFn).sort(function(a,b){return b.progress-a.progress;});
  var el=document.getElementById(containerId);
  if(list.length===0){el.innerHTML='<div class="empty-state"><i class="fas fa-inbox"></i><div>暂无书籍</div></div>';return;}
  el.innerHTML='<div class="gallery-grid">'+list.map(function(b){
    return '<div class="gallery-item" onclick="openBookDetail('+b.id+')">'+coverHtml(b)+'<div class="gallery-meta"><div class="gallery-title">'+b.title+'</div><div class="gallery-progress-track"><div class="gallery-progress-bar-fill" style="width:'+b.progress+'%;background:'+b.color+'"></div></div></div></div>';
  }).join('')+'</div>';
}

/* ===== Book Detail Page ===== */
function openBookDetail(id){
  var b=BOOKS.find(function(x){return x.id===id;});
  if(!b)return;
  previousView=currentView;

  var cover=b.coverLocal?'<img src="'+b.coverLocal+'" alt="'+b.title+'">':'<div class="book-detail-cover-fallback" style="background:linear-gradient(135deg,'+b.color+','+b.color+'cc);">'+b.title+'</div>';

  var tags='<div class="book-detail-tags">';
  tags+='<span class="tag"><i class="fas fa-tag"></i> '+b.category+'</span>';
  if(b.pages)tags+='<span class="tag"><i class="fas fa-file-lines"></i> '+b.pages+'页</span>';
  tags+='<span class="tag"><i class="fas fa-box"></i> '+b.source+'</span>';
  if(b.rating)tags+='<span class="tag"><i class="fas fa-star" style="color:#EF9F27"></i> '+b.rating+'</span>';
  if(b.publisher)tags+='<span class="tag"><i class="fas fa-building"></i> '+b.publisher+'</span>';
  tags+='<span class="tag"><i class="fas fa-calendar"></i> '+b.createdTime+'</span>';
  tags+='</div>';

  var statsHtml='<div class="book-detail-stats">';
  statsHtml+='<span><i class="fas fa-bookmark"></i> 已读 '+b.readPages+' / '+(b.pages||'?')+' 页</span>';
  if(b.startDate)statsHtml+='<span><i class="fas fa-play"></i> 开始: '+b.startDate+'</span>';
  if(b.finishDate)statsHtml+='<span><i class="fas fa-flag-checkered"></i> 完读: '+b.finishDate+'</span>';
  statsHtml+='<span><i class="fas fa-calendar-check"></i> '+b.recordCount+' 条打卡</span>';
  statsHtml+='</div>';

  var notesHtml='';
  if(b.content&&b.content.hasContent){
    notesHtml='<div class="book-detail-notes"><h2><i class="fas fa-feather-pointed"></i> 读书笔记</h2>';
    if(b.content.sections&&b.content.sections.length){
      b.content.sections.forEach(function(s){
        notesHtml+='<div class="note-section"><div class="note-section-title">'+s.title+'</div>';
        s.items.forEach(function(item){notesHtml+='<div class="note-item">'+item+'</div>';});
        s.quotes.forEach(function(q){notesHtml+='<div class="note-quote"><i class="fas fa-quote-left"></i> '+q+'</div>';});
        notesHtml+='</div>';
      });
    }
    if(b.content.quotes&&b.content.quotes.length){
      b.content.quotes.forEach(function(q){notesHtml+='<div class="note-quote"><i class="fas fa-quote-left"></i> '+q+'</div>';});
    }
    if(b.content.notes&&b.content.notes.length){
      b.content.notes.forEach(function(n){notesHtml+='<div class="note-item">'+n+'</div>';});
    }
    notesHtml+='</div>';
  }else{
    notesHtml='<div class="book-detail-notes"><h2><i class="fas fa-feather-pointed"></i> 读书笔记</h2><div class="note-empty"><i class="fas fa-book-open"></i>这本书还没有笔记</div></div>';
  }

  var navHtml='<div class="book-detail-nav"><button class="back-btn" onclick="goBack()"><i class="fas fa-arrow-left"></i> 返回</button>';
  if(b.url)navHtml+='<a href="'+b.url+'" target="_blank" class="notion-source"><i class="fas fa-external-link-alt"></i> Notion原页</a>';
  navHtml+='</div>';

  var heroHtml='<div class="book-detail-hero"><div class="book-detail-cover">'+cover+'</div><div class="book-detail-info"><h1>'+b.title+'</h1><div class="book-detail-author"><i class="fas fa-user-pen"></i> '+b.author+'</div>'+tags+'<div class="book-detail-progress"><div class="progress-label"><span>阅读进度</span><span class="progress-pct">'+b.progress+'% · '+b.status+'</span></div><div class="progress-bar-lg"><div class="progress-fill-lg" style="width:'+b.progress+'%"></div></div></div>'+statsHtml+'</div></div>';

  document.getElementById('bookDetailContent').innerHTML=navHtml+heroHtml+notesHtml;

  currentView='bookdetail';
  document.querySelectorAll('.nav-item').forEach(function(n){n.classList.remove('active');});
  document.querySelectorAll('.view').forEach(function(v){v.classList.remove('active');});
  document.getElementById('view-bookdetail').classList.add('active');
  document.getElementById('pageTitle').textContent='书籍详情';
  document.getElementById('pageSubtitle').textContent=b.title;
  hideSidebar();
  window.scrollTo(0,0);
}

function goBack(){
  switchView(previousView);
}

/* ===== Stats View ===== */
function renderStats(){
  var ctx=document.getElementById('statusChart');
  if(charts.status)charts.status.destroy();
  charts.status=new Chart(ctx,{type:'doughnut',data:{labels:['已读','在读','未读'],datasets:[{data:[STATS.finished,STATS.reading,STATS.unread],backgroundColor:['#1D9E75','#EF9F27','#378ADD'],borderWidth:0,spacing:4}]},options:{responsive:true,maintainAspectRatio:false,cutout:'60%',plugins:{legend:{position:'bottom',labels:{color:'#a0a3c0',padding:12,usePointStyle:true,pointStyle:'circle'}}}}});
  var ctx2=document.getElementById('catReadChart');
  if(charts.catRead)charts.catRead.destroy();
  var cats=Object.keys(STATS.categories);
  var readData=cats.map(function(c){return BOOKS.filter(function(b){return b.category===c&&(b.status==='已读'||b.status==='在读');}).length;});
  charts.catRead=new Chart(ctx2,{type:'bar',data:{labels:cats,datasets:[{data:readData,backgroundColor:'#7F77DD',borderRadius:6}]},options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{grid:{color:'rgba(255,255,255,0.05)'},ticks:{color:'#a0a3c0'}},y:{grid:{display:false},ticks:{color:'#a0a3c0'}}}}});
  var ctx3=document.getElementById('pagesChart');
  if(charts.pages)charts.pages.destroy();
  var sorted=BOOKS.filter(function(b){return b.readPages;}).sort(function(a,b){return b.readPages-a.readPages;}).slice(0,10);
  charts.pages=new Chart(ctx3,{type:'bar',data:{labels:sorted.map(function(b){return b.title;}),datasets:[{data:sorted.map(function(b){return b.readPages;}),backgroundColor:sorted.map(function(b){return b.color;}),borderRadius:6}]},options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{grid:{color:'rgba(255,255,255,0.05)'},ticks:{color:'#a0a3c0'}},y:{grid:{display:false},ticks:{color:'#a0a3c0'}}}}});
}

/* ===== Authors View ===== */
function renderAuthors(){
  var authors=STATS.topAuthors;
  var max=authors[0][1];
  var colors=['#7F77DD','#378ADD','#1D9E75','#D85A30','#EF9F27','#D4537E','#639922','#534AB7','#0F6E56','#185FA5'];
  document.getElementById('authorList').innerHTML=authors.map(function(a,i){
    var pct=Math.round(a[1]/max*100);
    var booksByAuthor=BOOKS.filter(function(b){return b.author===a[0];});
    var finished=booksByAuthor.filter(function(b){return b.status==='已读';}).length;
    return '<div class="author-row"><div style="width:140px;font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'+a[0]+'</div><div class="author-bar"><div class="author-bar-fill" style="width:'+pct+'%;background:'+colors[i%10]+';"></div></div><div style="font-size:12px;color:var(--text-secondary);width:80px;text-align:right;">'+a[1]+' 本</div><div style="font-size:11px;color:var(--text-tertiary);width:60px;">已读'+finished+'</div></div>';
  }).join('');
}

/* ===== Timeline View ===== */
function renderTimeline(){
  var sorted=BOOKS.slice().sort(function(a,b){return b.createdTime.localeCompare(a.createdTime);}).slice(0,50);
  document.getElementById('timeline').innerHTML=sorted.map(function(b){return '<div class="timeline-item"><div class="timeline-date">'+b.createdTime+'</div><div class="timeline-content"><strong>《'+b.title+'》</strong> · '+b.author+' · '+b.category+' · '+b.status+'</div></div>';}).join('');
}

/* ===== Search ===== */
document.getElementById('globalSearch').addEventListener('input',function(e){
  var q=e.target.value.trim().toLowerCase();
  var dropdown=document.getElementById('searchDropdown');
  if(!q){dropdown.classList.remove('active');dropdown.innerHTML='';return;}
  var matches=BOOKS.filter(function(b){return b.title.toLowerCase().indexOf(q)!==-1||b.author.toLowerCase().indexOf(q)!==-1;});
  if(matches.length===0){
    dropdown.innerHTML='<div class="search-no-result"><i class="fas fa-search" style="font-size:24px;opacity:0.3;display:block;margin-bottom:8px;"></i>未找到匹配的书籍</div>';
    dropdown.classList.add('active');
    return;
  }
  var shown=matches.slice(0,30);
  var html='<div class="search-count">找到 '+matches.length+' 本'+(matches.length>30?'，显示前 30 本':'')+'</div>';
  html+=shown.map(function(b){
    var cover=b.coverLocal?'<img class="search-result-cover" src="'+b.coverLocal+'" loading="lazy">':'<div class="search-result-cover" style="background:'+b.color+';"></div>';
    var subText=b.author+' · '+b.category;
    if(b.progress>0)subText+=' · '+b.progress+'%';
    return '<div class="search-result-item" onclick="searchSelectBook('+b.id+')">'+cover+'<div class="search-result-info"><div class="search-result-title">'+b.title+'</div><div class="search-result-sub">'+subText+'</div></div></div>';
  }).join('');
  dropdown.innerHTML=html;
  dropdown.classList.add('active');
});

function searchSelectBook(id){
  closeSearchDropdown();
  openBookDetail(id);
}

function closeSearchDropdown(){
  document.getElementById('searchDropdown').classList.remove('active');
  document.getElementById('globalSearch').value='';
}

document.addEventListener('click',function(e){
  if(!e.target.closest('.search-wrapper')){
    document.getElementById('searchDropdown').classList.remove('active');
  }
});

renderDashboard();
if('serviceWorker' in navigator){navigator.serviceWorker.register('sw.js').catch(function(){});}
</script>
</body>
</html>'''

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Generated {HTML_FILE} ({len(html)} chars)")
print(f"Books: {len(books)}, Covers: {stats['booksWithCover']}")

# ===== PWA: manifest.json, sw.js, icon.svg =====
import json as _json, os as _os

manifest = {
    "name": "智慧之塔 · 我的书海",
    "short_name": "书海",
    "description": "Notion 图书数据驱动的书海仪表盘",
    "start_url": "./",
    "display": "standalone",
    "background_color": "#1a1b2e",
    "theme_color": "#7F77DD",
    "icons": [
        {"src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}
    ],
}
with open(_os.path.join(DIST_DIR, "manifest.json"), "w", encoding="utf-8") as f:
    _json.dump(manifest, f, ensure_ascii=False, indent=2)

sw_js = r'''const CACHE="booknotes-v1";
self.addEventListener("install",e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(["./","./index.html","./manifest.json","./icon.svg"])));self.skipWaiting();});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  e.respondWith(
    caches.match(e.request).then(cached=>{
      const fetchPromise=fetch(e.request).then(resp=>{
        if(resp.ok&&e.request.url.startsWith(self.location.origin)){
          const clone=resp.clone();
          caches.open(CACHE).then(c=>c.put(e.request,clone));
        }
        return resp;
      }).catch(()=>cached);
      return cached||fetchPromise;
    })
  );
});'''
with open(_os.path.join(DIST_DIR, "sw.js"), "w", encoding="utf-8") as f:
    f.write(sw_js)

icon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#7F77DD"/><stop offset="100%" stop-color="#534AB7"/></linearGradient></defs>
<rect width="512" height="512" rx="112" fill="url(#g)"/>
<path d="M160 140 Q160 120 180 120 L256 120 L256 392 L180 392 Q160 392 160 372 Z" fill="#fff" opacity="0.95"/>
<path d="M352 140 Q352 120 332 120 L256 120 L256 392 L332 392 Q352 392 352 372 Z" fill="#fff" opacity="0.75"/>
<line x1="256" y1="120" x2="256" y2="392" stroke="#534AB7" stroke-width="4"/>
</svg>'''
with open(_os.path.join(DIST_DIR, "icon.svg"), "w", encoding="utf-8") as f:
    f.write(icon_svg)

print("Generated PWA files: manifest.json, sw.js, icon.svg")

import json, urllib.request, os, time, hashlib, re
from config import TOKEN, BOOKS_DB_ID as DB_ID, HEADERS, COVERS_DIR, DATA_FILE

def query_database(db_id):
    all_results = []
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{db_id}/query",
            data=json.dumps(body).encode(), headers=HEADERS, method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        all_results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
        time.sleep(0.4)
    return all_results

def get_prop(props, name):
    p = props.get(name)
    if not p: return None
    t = p.get("type")
    if t == "title":
        arr = p.get("title", [])
        return arr[0]["plain_text"] if arr else ""
    elif t == "rich_text":
        arr = p.get("rich_text", [])
        return arr[0]["plain_text"] if arr else ""
    elif t == "select":
        s = p.get("select")
        return s["name"] if s else None
    elif t == "number":
        return p.get("number")
    elif t == "formula":
        f = p.get("formula", {})
        if f.get("string"): return f["string"]
        if f.get("number") is not None: return f["number"]
        if f.get("date"): return f["date"].get("start")
        return None
    elif t == "rollup":
        r = p.get("rollup", {})
        if r.get("number") is not None: return r["number"]
        arr = r.get("array", [])
        if arr:
            first = arr[0]
            if first.get("number") is not None: return first["number"]
            if first.get("date"): return first["date"].get("start")
        return None
    elif t == "files":
        files = p.get("files", [])
        if files:
            f0 = files[0]
            if f0.get("type") == "file": return f0["file"]["url"]
            elif f0.get("type") == "external": return f0["external"]["url"]
        return None
    elif t == "relation":
        return [r["id"] for r in p.get("relation", [])]
    elif t == "created_time":
        return p.get("created_time")
    return None

def download_cover(url, book_id, title):
    safe_name = re.sub(r'[^\w\u4e00-\u9fff]', '_', title)[:30]
    ext = ".jpg"
    if ".png" in url: ext = ".png"
    fname = f"{book_id:03d}_{safe_name}{ext}"
    fpath = os.path.join(COVERS_DIR, fname)
    if os.path.exists(fpath) and os.path.getsize(fpath) > 1000:
        return f"covers/{fname}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        if len(data) < 100:
            return None
        with open(fpath, "wb") as f:
            f.write(data)
        return f"covers/{fname}"
    except Exception as e:
        print(f"    Cover download failed for {title}: {e}")
        return None

print("Fetching books from Notion API...")
book_pages = query_database(DB_ID)
print(f"Got {len(book_pages)} books\n")

CAT_COLORS = {"小说":"#7F77DD","科幻":"#378ADD","历史":"#BA7517","社科":"#1D9E75","军事":"#D85A30","写作":"#639922","经济":"#EF9F27","讽刺":"#D4537E"}

def hash_color(s):
    palette = ["#7F77DD","#378ADD","#1D9E75","#D85A30","#EF9F27","#D4537E","#639922","#534AB7","#0F6E56","#185FA5"]
    h = int(hashlib.md5((s or "x").encode()).hexdigest(), 16)
    return palette[h % len(palette)]

books = []
for i, page in enumerate(book_pages):
    props = page.get("properties", {})
    title = get_prop(props, "书籍名称") or ""
    author = get_prop(props, "作者") or "佚名"
    author = re.sub(r'【.*?】', '', author).strip()
    cat = get_prop(props, "类型") or "未分类"
    pages = get_prop(props, "总页数") or 0
    rating = get_prop(props, "豆评") or 0
    source = get_prop(props, "书源") or "未知"
    publisher = get_prop(props, "出版社") or ""
    cover_url = get_prop(props, "封面")
    progress_val = get_prop(props, "阅读进度")
    status = get_prop(props, "阅读状态")
    read_pages = get_prop(props, "已读页数") or 0
    start_date = get_prop(props, "开始日期")
    finish_date = get_prop(props, "完读日期")
    created = get_prop(props, "创建时间") or ""
    record_ids = get_prop(props, "每日读书记录") or []

    # FIX: progress is 0-1 decimal from formula
    progress = 0
    if progress_val is not None:
        if isinstance(progress_val, str):
            progress_val = progress_val.replace("%","").strip()
            try: progress = float(progress_val)
            except: progress = 0
        else:
            progress = float(progress_val)
        if progress <= 1.0:
            progress = round(progress * 100)
        else:
            progress = int(progress)

    if not status:
        if progress >= 100: status = "已读"
        elif progress > 0: status = "在读"
        else: status = "未读"
    status = str(status).strip()

    color = CAT_COLORS.get(cat, hash_color(title))
    clean_title = re.sub(r'^\d+\s*《', '《', title)
    clean_title = re.sub(r'^\d+\s*', '', clean_title).strip()

    books.append({
        "id": i+1, "pageId": page.get("id"), "url": page.get("url"),
        "title": clean_title, "rawTitle": title,
        "author": author, "category": cat, "source": source,
        "publisher": publisher, "pages": pages, "rating": rating,
        "coverUrl": cover_url, "color": color,
        "progress": progress, "status": status,
        "readPages": read_pages, "startDate": start_date or "",
        "finishDate": finish_date or "", "recordCount": len(record_ids),
        "createdTime": (created[:10] if created else ""),
    })

books.sort(key=lambda x: x["createdTime"], reverse=True)
for i, b in enumerate(books):
    b["id"] = i + 1

# Download covers
print("Downloading covers...")
downloaded = 0
for b in books:
    if b["coverUrl"]:
        local = download_cover(b["coverUrl"], b["id"], b["title"])
        if local:
            b["coverLocal"] = local
            downloaded += 1
        else:
            b["coverLocal"] = None
    else:
        b["coverLocal"] = None
    if (b["id"]) % 20 == 0:
        print(f"  {b['id']}/{len(books)} done, {downloaded} covers downloaded")
    time.sleep(0.1)
print(f"Covers downloaded: {downloaded}/{len(books)}\n")

# Stats
total = len(books)
finished = len([b for b in books if b["status"]=="已读"])
reading = len([b for b in books if b["status"]=="在读"])
unread = len([b for b in books if b["status"]=="未读"])
total_pages = sum(b["pages"] for b in books)
read_pages = sum(b["readPages"] for b in books)
books_with_cover = downloaded

cats = {}
for b in books:
    cats[b["category"]] = cats.get(b["category"], 0) + 1

authors = {}
for b in books:
    authors[b["author"]] = authors.get(b["author"], 0) + 1
top_authors = sorted(authors.items(), key=lambda x:-x[1])[:10]

print(f"Stats:")
print(f"  Total: {total}, Finished: {finished}, Reading: {reading}, Unread: {unread}")
print(f"  Pages: {total_pages} total, {read_pages} read")
print(f"  Covers: {books_with_cover}/{total}")
print(f"  Categories: {cats}")
print(f"  Top authors: {top_authors[:5]}")

print(f"\nSample books:")
for b in books[:8]:
    print(f"  {b['title']}: {b['progress']}% ({b['status']}), pages {b['readPages']}/{b['pages']}, cover={'Y' if b['coverLocal'] else 'N'}")

output = {
    "books": books,
    "stats": {
        "total": total, "finished": finished, "reading": reading, "unread": unread,
        "totalPages": total_pages, "readPages": read_pages,
        "booksWithCover": books_with_cover,
        "categories": cats, "topAuthors": top_authors,
    }
}
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("\nSaved to books_data_full.json")

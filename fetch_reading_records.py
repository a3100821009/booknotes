import json, urllib.request, time
from config import TOKEN, RECORDS_DB_ID as DB_ID, HEADERS, DATA_FILE as BOOKS_DATA_FILE, RECORDS_FILE

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
        print(f"  Fetched {len(all_results)} records so far...")
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
        time.sleep(0.4)
    return all_results

def get_prop(props, name):
    p = props.get(name)
    if not p:
        return None
    t = p.get("type")
    if t == "title":
        arr = p.get("title", [])
        return arr[0]["plain_text"] if arr else ""
    elif t == "number":
        return p.get("number")
    elif t == "select":
        s = p.get("select")
        return s["name"] if s else None
    elif t == "date":
        d = p.get("date")
        return d.get("start") if d else None
    elif t == "formula":
        f = p.get("formula", {})
        if f.get("string"): return f["string"]
        if f.get("date"): return f["date"].get("start")
        return None
    elif t == "relation":
        return [r["id"] for r in p.get("relation", [])]
    elif t == "created_time":
        return p.get("created_time")
    return None

print("Fetching reading records from Notion...")
records = query_database(DB_ID)
print(f"Got {len(records)} reading records\n")

# Load existing books data to map page IDs to book IDs
with open(BOOKS_DATA_FILE, "r", encoding="utf-8") as f:
    books_data = json.load(f)

page_id_to_book = {}
for b in books_data["books"]:
    if b.get("pageId"):
        page_id_to_book[b["pageId"]] = b

parsed = []
for rec in records:
    props = rec.get("properties", {})
    note = get_prop(props, "备注") or ""
    read_date = get_prop(props, "读书日期") or ""
    pages_read = get_prop(props, "所读页数") or 0
    medium = get_prop(props, "读书媒介") or ""
    book_ids = get_prop(props, "图书总览") or []
    chart_date = get_prop(props, "图表日期") or ""
    created = rec.get("created_time", "")[:10]

    # Match to book
    matched_book = None
    for bid in book_ids:
        if bid in page_id_to_book:
            matched_book = page_id_to_book[bid]
            break

    parsed.append({
        "id": rec.get("id"),
        "date": read_date[:10] if read_date else created,
        "pagesRead": pages_read,
        "medium": medium,
        "note": note,
        "bookTitle": matched_book["title"] if matched_book else "",
        "bookId": matched_book["id"] if matched_book else None,
        "bookPageId": book_ids[0] if book_ids else None,
        "chartDate": chart_date[:10] if chart_date else "",
        "createdTime": created,
    })

# Sort by date
parsed.sort(key=lambda x: x["date"], reverse=True)

# Stats
total_records = len(parsed)
total_pages_read = sum(r["pagesRead"] for r in parsed if r["pagesRead"])
date_counts = {}
for r in parsed:
    d = r["date"]
    if d:
        date_counts[d] = date_counts.get(d, 0) + 1

medium_counts = {}
for r in parsed:
    if r["medium"]:
        medium_counts[r["medium"]] = medium_counts.get(r["medium"], 0) + 1

# Date range
dates_with_read = [r["date"] for r in parsed if r["date"]]
date_range = ""
if dates_with_read:
    dates_sorted = sorted(dates_with_read)
    date_range = f"{dates_sorted[0]} ~ {dates_sorted[-1]}"

print(f"=== Reading Records Stats ===")
print(f"Total records: {total_records}")
print(f"Total pages read: {total_pages_read}")
print(f"Unique reading days: {len(date_counts)}")
print(f"Date range: {date_range}")
print(f"Medium: {medium_counts}")
print(f"Max pages in a day: {max((r['pagesRead'] for r in parsed if r['pagesRead']), default=0)}")
print(f"\nRecent 10 records:")
for r in parsed[:10]:
    print(f"  {r['date']} | {r['bookTitle'][:20]:20s} | {r['pagesRead']:>4}页 | {r['medium']}")

# Save reading records
output = {
    "records": parsed,
    "stats": {
        "totalRecords": total_records,
        "totalPagesRead": total_pages_read,
        "uniqueReadingDays": len(date_counts),
        "dateRange": date_range,
        "mediumCounts": medium_counts,
        "dateCounts": date_counts,
    }
}

with open(RECORDS_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\nSaved to reading_records.json")

# Also update books_data_full.json with reading activity data
books_data["readingRecords"] = parsed
books_data["stats"]["readingRecords"] = total_records
books_data["stats"]["totalPagesReadFromRecords"] = total_pages_read
books_data["stats"]["uniqueReadingDays"] = len(date_counts)
books_data["stats"]["readingDateCounts"] = date_counts

with open(BOOKS_DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(books_data, f, ensure_ascii=False, indent=2)
print(f"Updated books_data_full.json with reading records data")

import json, urllib.request, time, re
from config import TOKEN, HEADERS, DATA_FILE

def get_blocks(page_id):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    req = urllib.request.Request(url, headers=HEADERS, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        return data.get("results", [])
    except Exception as e:
        print(f"    Error fetching blocks for {page_id}: {e}")
        return []

def extract_text(rich_text_array):
    if not rich_text_array:
        return ""
    return "".join(rt.get("plain_text", "") for rt in rich_text_array)

def parse_blocks(blocks):
    sections = []
    current_section = None
    quotes = []
    notes = []

    for block in blocks:
        btype = block.get("type", "")
        content = block.get(btype, {})

        if btype in ("heading_1", "heading_2", "heading_3"):
            text = extract_text(content.get("rich_text", []))
            if text.strip():
                if current_section and (current_section["items"] or current_section["quotes"]):
                    sections.append(current_section)
                current_section = {"title": text.strip(), "items": [], "quotes": []}

        elif btype == "paragraph":
            text = extract_text(content.get("rich_text", []))
            if text.strip():
                if current_section:
                    current_section["items"].append(text.strip())
                else:
                    notes.append(text.strip())

        elif btype == "bulleted_list_item":
            text = extract_text(content.get("rich_text", []))
            if text.strip():
                if current_section:
                    current_section["items"].append("• " + text.strip())
                else:
                    notes.append("• " + text.strip())

        elif btype == "numbered_list_item":
            text = extract_text(content.get("rich_text", []))
            if text.strip():
                if current_section:
                    current_section["items"].append(text.strip())
                else:
                    notes.append(text.strip())

        elif btype == "quote":
            text = extract_text(content.get("rich_text", []))
            if text.strip():
                if current_section:
                    current_section["quotes"].append(text.strip())
                else:
                    quotes.append(text.strip())

        elif btype == "callout":
            text = extract_text(content.get("rich_text", []))
            if text.strip():
                if current_section:
                    current_section["items"].append(text.strip())
                else:
                    notes.append(text.strip())

        elif btype == "toggle":
            text = extract_text(content.get("rich_text", []))
            if text.strip():
                if current_section:
                    current_section["items"].append(text.strip())
                else:
                    notes.append(text.strip())

        elif btype == "divider":
            pass

    if current_section and (current_section["items"] or current_section["quotes"]):
        sections.append(current_section)

    return {
        "sections": sections,
        "quotes": quotes,
        "notes": notes,
        "hasContent": bool(sections or quotes or notes),
    }

print("Loading existing data...")
with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

books = data["books"]
print(f"Total books: {len(books)}")

print("\nFetching page content for each book...")
books_with_content = 0
for i, book in enumerate(books):
    page_id = book.get("pageId")
    if not page_id:
        continue

    blocks = get_blocks(page_id)
    content = parse_blocks(blocks)
    book["content"] = content

    if content["hasContent"]:
        books_with_content += 1
        section_names = [s["title"] for s in content["sections"]]
        total_items = sum(len(s["items"]) for s in content["sections"]) + len(content["quotes"]) + len(content["notes"])
        if total_items > 0:
            print(f"  [{i+1}/{len(books)}] {book['title']}: {total_items} items, sections: {section_names}")

    if (i + 1) % 20 == 0:
        print(f"  --- {i+1}/{len(books)} processed, {books_with_content} with content ---")
    time.sleep(0.35)

print(f"\nBooks with content: {books_with_content}/{len(books)}")

data["stats"]["booksWithContent"] = books_with_content

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated books_data_full.json")

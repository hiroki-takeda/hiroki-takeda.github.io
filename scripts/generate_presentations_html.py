from pathlib import Path
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from datetime import datetime

# --- ファイルパスの設定 ---
bib_file = Path("bib/presentations.bib")
template_file = Path("templates/template.html")
output_file = Path("presentations.html")

# --- 月の数値 → 月名への変換辞書 ---
month_map = {
    "1": "January", "01": "January",
    "2": "February", "02": "February",
    "3": "March", "03": "March",
    "4": "April", "04": "April",
    "5": "May", "05": "May",
    "6": "June", "06": "June",
    "7": "July", "07": "July",
    "8": "August", "08": "August",
    "9": "September", "09": "September",
    "10": "October",
    "11": "November",
    "12": "December"
}

# --- 発表日でソートするためのキー ---
def get_sort_key(entry):
    year = entry.get("year", "1900")
    month = entry.get("month", "01").zfill(2)
    try:
        return datetime.strptime(f"{year}-{month}", "%Y-%m")
    except:
        return datetime.min

# --- 著者整形 ---
def format_authors(authors_raw):
    authors = [a.strip() for a in authors_raw.replace("\n", " ").split(" and ")]
    formatted = []
    for a in authors:
        if "Takeda, Hiroki" in a:
            formatted.append("<u>Hiroki Takeda</u>")
        else:
            if "," in a:
                parts = [p.strip() for p in a.split(",")]
                if len(parts) == 2:
                    a = f"{parts[1]} {parts[0]}"
            formatted.append(a)
    return ", ".join(formatted)

# --- BibTeX 読み込み ---
with open(bib_file, encoding="utf-8") as bf:
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    bib_db = bibtexparser.load(bf, parser=parser)

# --- カテゴリ分類 ---
categories = {
    "invited": [],
    "int_oral": [],
    "int_poster": [],
    "dom_oral": [],
    "dom_poster": []
}

for entry in bib_db.entries:
    keywords = entry.get("keywords", "")
    for kw in keywords.split(","):
        kw = kw.strip()
        if kw in categories:
            categories[kw].append(entry)

for kw in categories:
    categories[kw].sort(key=get_sort_key, reverse=True)

# --- エントリをHTML化 ---
def format_entry_html(entry):
    authors = format_authors(entry.get("author", ""))
    title = entry.get("title", "").strip("{}")
    booktitle = entry.get("booktitle", "")
    address = entry.get("address", "")
    year = entry.get("year", "")
    month_raw = entry.get("month", "")
    month_str = month_map.get(month_raw.strip(), month_raw)
    date_str = f"{month_str} {year}" if month_str else year
    return f"<li>{authors},<br><i>{title}</i>,<br>{booktitle}, {address}, {date_str}.</li>"

# --- セクション構築 ---
def generate_section_html(title, entries):
    if not entries:
        return ""
    html = f"<h2>{title}</h2>\n<ul>\n"
    for entry in entries:
        html += format_entry_html(entry) + "\n"
    html += "</ul>\n"
    return html

# --- International Conference セクション構築（Oral/Poster） ---
def generate_international_section_html():
    oral_html = generate_section_html("Oral", categories["int_oral"])
    poster_html = generate_section_html("Poster", categories["int_poster"])
    return f"<h2>International Conference</h2>\n{oral_html}\n{poster_html}"

# --- 本文HTML構築 ---
body_html = ""
body_html += generate_section_html("Invited Talks", categories["invited"])
body_html += generate_international_section_html()
body_html += generate_section_html("Domestic Conference - Oral", categories["dom_oral"])
body_html += generate_section_html("Domestic Conference - Poster", categories["dom_poster"])

# --- テンプレートに埋め込み ---
with open(template_file, encoding="utf-8") as tf:
    template = tf.read()

# タイトル1回のみ表示するよう $title$ プレースホルダーだけ使用
html = template.replace("$title$", "Presentations").replace("$body$", body_html)

# --- 出力 ---
with open(output_file, "w", encoding="utf-8") as out:
    out.write(html)

print("✅ presentations.html を生成しました。")
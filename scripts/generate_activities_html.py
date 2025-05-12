from pathlib import Path
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from datetime import datetime

# --- ファイルパスの設定 ---
bib_file = Path("bib/activities_jap.bib")
template_file = Path("templates/template.html")
output_file = Path("activities.html")

# --- 月のマッピング（日本語） ---
month_map = {
    "1": "1月", "01": "1月", "jan": "1月", "january": "1月",
    "2": "2月", "02": "2月", "feb": "2月", "february": "2月",
    "3": "3月", "03": "3月", "mar": "3月", "march": "3月",
    "4": "4月", "04": "4月", "apr": "4月", "april": "4月",
    "5": "5月", "05": "5月", "may": "5月",
    "6": "6月", "06": "6月", "jun": "6月", "june": "6月",
    "7": "7月", "07": "7月", "jul": "7月", "july": "7月",
    "8": "8月", "08": "8月", "aug": "8月", "august": "8月",
    "9": "9月", "09": "9月", "sep": "9月", "september": "9月",
    "10": "10月", "oct": "10月", "october": "10月",
    "11": "11月", "nov": "11月", "november": "11月",
    "12": "12月", "dec": "12月", "december": "12月"
}

# --- BibTeX読み込み ---
with open(bib_file, encoding="utf-8") as bf:
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    bib_database = bibtexparser.load(bf, parser=parser)

# --- カテゴリ分け ---
categorized = {
    "lecture": [],
    "appearance": [],
    "writing": [],
    "interview": [],
    "others": [],
    "notes": []
}

for entry in bib_database.entries:
    keywords = entry.get("keywords", "")
    for kw in keywords.split(","):
        kw = kw.strip()
        if kw in categorized:
            categorized[kw].append(entry)

# --- ソート関数 ---
def get_sort_key(entry):
    year = entry.get("year", "1900")
    month = entry.get("month", "01").lower()
    month_num = month_map.get(month, "1月").replace("月", "")
    try:
        return datetime.strptime(f"{year}-{month_num}", "%Y-%m")
    except:
        return datetime.min

for kw in categorized:
    categorized[kw].sort(key=get_sort_key, reverse=True)

# --- 日付整形 ---
def format_date(entry):
    month = entry.get("month", "").lower()
    year = entry.get("year", "")
    m = month_map.get(month, "")
    return f"{year}年{m}" if m else f"{year}年"

# --- エントリ整形 ---
def format_entry_html(entry):
    title = f"<i>{entry.get('title', '').strip()}</i>"
    org = entry.get("organization", "").strip()
    how = entry.get("howpublished", "").strip()
    date = format_date(entry)
    return f"<li>{title},<br>{org}, {how}, {date}.</li>"

# --- セクション生成 ---
def generate_section_html(title, entries):
    if not entries:
        return ""
    html = f"<h2>{title}</h2>\n<ul>\n"

    for entry in entries:
        html += format_entry_html(entry) + "\n"
    html += "</ul>\n"
    return html

# --- HTML構築 ---
body_html = "<h1 id=\"activities\">Activities</h1>\n"
body_html += """ <p>ご依頼・お問い合わせは<a href="index.html#contact">Contact</a>よりご連絡ください。</p> """
body_html += generate_section_html("講演", categorized["lecture"])
body_html += generate_section_html("出演", categorized["appearance"])
body_html += generate_section_html("記事", categorized["writing"])
body_html += generate_section_html("取材", categorized["interview"])
body_html += generate_section_html("その他", categorized["others"])
body_html += generate_section_html("Notes", categorized["notes"])

# --- テンプレート読み込みと結合 ---
with open(template_file, encoding="utf-8") as tf:
    template = tf.read()

html = template.replace("$title$", "Activities").replace("$body$", body_html)

# --- HTML出力 ---
with open(output_file, "w", encoding="utf-8") as out:
    out.write(html)

print("✅ activities.html を生成しました。")

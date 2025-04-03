from pathlib import Path
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
import re
from datetime import datetime

# --- ファイルパスの設定 ---
bib_papers = Path("bib/papers.bib")
bib_books = Path("bib/books_jap.bib")
collab_file = Path("bib/collaboration.bib")
template_file = Path("templates/template.html")
output_file = Path("publications.html")

# --- ジャーナル名の正式名称マッピング ---
journal_name_map = {
    "Phys. Rev. D": "Physical Review D",
    "Class. Quant. Grav.": "Classical and Quantum Gravity",
    "Astrophys. J.": "The Astrophysical Journal",
    "Rev. Sci. Instrum.": "Review of Scientific Instruments",
    "PTEP": "Progress of Theoretical and Experimental Physics",
    "Astropart. Phys.": "Astroparticle Physics",
    "Phys. Rev. Lett.": "Physical Review Letters",
    "Gen. Rel. Grav.": "General Relativity and Gravitation",
    "Astron. Astrophys.": "Astronomy & Astrophysics",
    "Phys. Rev. X": "Physical Review X",
    "Living Rev. Rel.": "Living Reviews in Relativity",
    "Nature Astron.": "Nature Astronomy",
    "Astrophys. J. Lett.": "The Astrophysical Journal Letters",
    "Astrophys. J. Suppl.": "The Astrophysical Journal Supplement Series",
    "Mon. Not. Roy. Astron. Soc.": "Monthly Notices of the Royal Astronomical Society"
}

def get_sort_key(entry):
    eprint = entry.get("eprint", "")
    if len(eprint) >= 4 and eprint[:4].isdigit():
        # arXiv:YYMM形式の最初の4桁を使う
        year = "20" + eprint[:2]
        month = eprint[2:4]
    else:
        year = entry.get("year", "1900")  # fallback
        month = entry.get("month", "01")  # fallback

    try:
        return datetime.strptime(f"{year}-{month}", "%Y-%m")
    except:
        return datetime.min  # ソート不能なデータは最古に

def load_bib(path):
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    return bibtexparser.load(open(path, encoding="utf-8"), parser=parser)

papers_db = load_bib(bib_papers)
books_db  = load_bib(bib_books)
collab_db = load_bib(collab_file)

for entry in collab_db.entries:
    entry["keywords"] = "collaboration"

# --- 業績をカテゴリ別に分類 ---
entries = papers_db.entries + books_db.entries + collab_db.entries
categorized = {"book": [], "short": [], "collaboration": []}
for entry in entries:
    keywords = entry.get("keywords", "")
    for kw in keywords.split(","):
      kw = kw.strip()
      if kw in categorized:
        categorized[kw].append(entry)

    # ★ 各カテゴリ内で新しい順にソート（年の降順）
    for kw in categorized:
      categorized[kw].sort(key=get_sort_key, reverse=True)

# --- 著者表記を整形 ---
def format_authors(authors_raw):
    authors = [a.strip() for a in authors_raw.replace("\n", " ").split(" and ")]
    formatted = []
    for a in authors:
        if "Takeda, Hiroki" in a:
            formatted.append("<u>Hiroki Takeda</u>")
        else:
            # "Last, First" → "First Last"
            if "," in a:
                parts = [p.strip() for p in a.split(",")]
                if len(parts) == 2:
                    a = f"{parts[1]} {parts[0]}"
            formatted.append(a)
    return ", ".join(formatted)

# --- エントリのフォーマット ---
def format_entry_html(entry):
    # --- 著者名の処理 ---
    if entry.get("keywords", "").strip() == "collaboration":
        collab = entry.get("collaboration", "Collaboration")
        authors = f"{collab} Collaboration (including <u>Hiroki Takeda</u>)"
    else:
        authors = format_authors(entry.get("author", ""))

    # --- その他の共通項目 ---
    title = entry.get("title", "").strip("{}")
    year = entry.get("year", "")
    doi = entry.get("doi", "")
    doi_link = f'<a href="https://doi.org/{doi}">[{doi}]</a>' if doi else ""
    arxiv = entry.get("eprint", "")
    arxiv_link = f'<a href="https://arxiv.org/abs/{arxiv}">[arXiv:{arxiv}]</a>' if arxiv else ""

    # --- Book ---
    if entry.get("ENTRYTYPE") == "book":
        publisher = entry.get("publisher", "")
        date = entry.get("date", "")
        pages = entry.get("pages", "")
        url = entry.get("url", "")
        link = f'<br><a href="{url}">[Link]</a>' if url else ""
        return f"<li>{authors},<br><i>{title}</i>,<br>{publisher}, {date}, {pages} pages.{link}</li>"

    # --- Published article ---
    if "journal" in entry:
        journal = journal_name_map.get(entry.get("journal", ""), entry.get("journal", ""))
        volume = entry.get("volume", "")
        pages = entry.get("pages", "")
        return f"<li>{authors},<br><i>{title}</i>,<br>{journal}, {volume}, {pages} ({year}).<br>{arxiv_link} {doi_link}</li>"

    # --- arXiv only ---
    return f"<li>{authors},<br><i>{title}</i>,<br>arXiv:{arxiv}.<br>{arxiv_link}</li>"

# --- セクション生成 ---
def generate_section_html(title, entries):
    if not entries:
        return ""
    html = f"<h2>{title}</h2>\n<ul>\n"
    for entry in entries:
        html += format_entry_html(entry) + "\n"
    html += "</ul>\n"
    return html

# --- HTMLボディ構築 ---
body_html = "<h1 id=\"publications\">Publications</h1>\n"
body_html += generate_section_html("Books", categorized["book"])
body_html += generate_section_html("Papers", categorized["short"])
body_html += """
<h1 id="publications">Publications</h1>
See also:
  <a href="https://arxiv.org/search/?query=%22Hiroki+Takeda%22&searchtype=author&abstracts=show&order=-announced_date_first&size=50">arXiv</a>, 
  <a href="https://scholar.google.com/citations?user=Cq6rALgAAAAJ&hl=ja&oi=ao">Google Scholar</a>,
  <a href="https://inspirehep.net/authors/1684306">INSPIRE</a>.
"""
body_html += generate_section_html("Collaboration Papers", categorized["collaboration"])

# --- テンプレート読み込みと結合 ---
with open(template_file, encoding="utf-8") as tf:
    template = tf.read()

html = template.replace("$title$", "Publications").replace("$body$", body_html)

# --- 出力ファイル書き込み ---
with open(output_file, "w", encoding="utf-8") as out:
    out.write(html)

"✅ HTMLファイルが生成されました（author整形とDOI表示も改善済）"

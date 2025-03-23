# scripts/generate_cv_japanese.py
from pathlib import Path
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from datetime import datetime
import subprocess

# ---------- 設定 ----------
template_path = Path("templates/cv_template_eng.tex")
output_path = Path("cv/cv_english/cv.tex")

bib_books = Path("bib/books_eng.bib")
bib_papers = Path("bib/papers.bib")
bib_collab = Path("bib/collaboration.bib")
bib_presentations = Path("bib/presentations.bib")
bib_activities = Path("bib/activities_eng.bib")

# ---------- 月名の日本語変換 ----------
month_map = {
    "1": "January", "01": "January", "jan": "January",
    "2": "February", "02": "February", "feb": "February",
    "3": "March", "03": "March", "mar": "March",
    "4": "April", "04": "April", "apr": "April",
    "5": "May", "05": "May",
    "6": "June", "06": "June", "jun": "June",
    "7": "July", "07": "July", "jul": "July",
    "8": "August", "08": "August", "aug": "August",
    "9": "September", "09": "September", "sep": "September",
    "10": "October", "oct": "October",
    "11": "November", "nov": "November",
    "12": "December", "dec": "December"
}

# ---------- ソート ----------
def get_sort_key(entry):
    eprint = entry.get("eprint", "")
    if len(eprint) >= 4 and eprint[:4].isdigit():
        year = "20" + eprint[:2]
        month = eprint[2:4]
    else:
        year = entry.get("year", "1900")
        month = entry.get("month", "01").lower()
        month = month_map.get(month, "01").replace("月", "")
    try:
        return datetime.strptime(f"{year}-{month}", "%Y-%m")
    except:
        return datetime.min

def format_authors_latex(raw):
    authors = [a.strip() for a in raw.replace("\n", " ").split(" and ")]
    result = []
    for a in authors:
        if "Takeda, Hiroki" in a:
            result.append(r"\uline{Hiroki Takeda}")
        else:
            if "," in a:
                parts = [p.strip() for p in a.split(",")]
                if len(parts) == 2:
                    a = f"{parts[1]} {parts[0]}"
            result.append(a)
    return ", ".join(result)

def load_bib(path):
    with open(path, encoding="utf-8") as f:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        return bibtexparser.load(f, parser=parser)

def generate_section(title, entries, formatter):
    if not entries:
        return ""
    tex = f"\\subsection*{{{title}}}\n\\begin{{enumerate}}\n"
    for entry in entries:
        tex += formatter(entry) + "\n"
    tex += "\\end{enumerate}\n"
    return tex

def format_publication(entry):
    title = entry.get("title", "").strip("{}")
    year = entry.get("year", "")
    doi = entry.get("doi", "")
    arxiv = entry.get("eprint", "")
    url = entry.get("url", "")
    volume = entry.get("volume", "")
    pages = entry.get("pages", "")
    journal = entry.get("journal", "")
    publisher = entry.get("publisher", "")
    date = entry.get("date", "")
    author = format_authors_latex(entry.get("author", ""))
    entry_type = entry.get("ENTRYTYPE", "")

    if entry.get("keywords", "").strip() == "collaboration":
        collab = entry.get("collaboration", "Collaboration")
        author = f"{collab} Collaboration (including \\uline{{Hiroki Takeda}})"

    if entry_type == "book":
        return f"\\item {author}, “{title}”, {publisher}, {date}, {pages} pages."

    elif journal:
        parts = f"{journal}, {volume}, {pages} ({year})" if volume else f"{journal} ({year})"
        links = []
        if arxiv:
            links.append(f"arXiv:{arxiv}")
        if doi:
            links.append(f"DOI: {doi}")
        return f"\\item {author}, “{title}”, {parts}. {'; '.join(links)}"

    elif arxiv:
        return f"\\item {author}, “{title}”, arXiv:{arxiv}."

    else:
        return f"\\item {author}, “{title}”, {year}."

def format_presentation(entry):
    author = format_authors_latex(entry.get("author", ""))
    title = entry.get("title", "").strip("{}")
    book = entry.get("booktitle", "")
    address = entry.get("address", "")
    year = entry.get("year", "")
    month = month_map.get(entry.get("month", "").lower(), "")
    date = f"{month} {year}" if month else f"{year}"
    return f"\\item {author}, “{title}”, {book}, {address}, {date}."

def format_activity(entry):
    title = entry.get("title", "").strip("{}")
    org = entry.get("organization", "")
    how = entry.get("howpublished", "")
    year = entry.get("year", "")
    month = month_map.get(entry.get("month", "").lower(), "")
    date = f"{month} {year}" if month else f"{year}"
    return f"\\item “{title}”, {org}, {how}, {date}."

def insert_between(text, begin_marker, end_marker, content):
    start = text.find(begin_marker)
    end = text.find(end_marker)
    if start == -1 or end == -1:
        raise ValueError("マーカーが見つかりません")
    return text[:start + len(begin_marker)] + "\n" + content + "\n" + text[end:]

# ---------- 読み込み ----------
books_db = load_bib(bib_books)
papers_db = load_bib(bib_papers)
collab_db = load_bib(bib_collab)
for e in collab_db.entries:
    e["keywords"] = "collaboration"

categorized = {
    "book": books_db.entries,
    "short": papers_db.entries,
    "collaboration": collab_db.entries
}
for k in categorized:
    categorized[k].sort(key=get_sort_key, reverse=True)

latex_publications = ""
latex_publications += generate_section("Books", categorized["book"], format_publication)
latex_publications += generate_section("Journal Articles", categorized["short"], format_publication)
latex_publications += generate_section("Collaboration Papers", categorized["collaboration"], format_publication)

# ---------- 発表 ----------
pres_db = load_bib(bib_presentations)
presentation_categories = {
    "invited": "Invited Talks",
    "int_oral": "International Conferences (Oral)",
    "int_poster": "International Conferences (Poster)",
    "dom_oral": "Domestic Conferences (Oral)",
    "dom_poster": "Domestic Conferences (Poster)"
}
latex_presentations = ""
for key, title in presentation_categories.items():
    entries = [e for e in pres_db.entries if key in e.get("keywords", "")]
    entries.sort(key=get_sort_key, reverse=True)
    latex_presentations += generate_section(title, entries, format_presentation)

# ---------- 活動 ----------
act_db = load_bib(bib_activities)
activity_categories = {
    "lecture": "Lectures",
    "appearance": "Media Appearances",
    "writing": "Writing",
    "interview": "Interviews",
    "others": "Others",
    "notes": "Notes"
}
latex_activities = ""
for key, title in activity_categories.items():
    entries = [e for e in act_db.entries if key in e.get("keywords", "")]
    entries.sort(key=get_sort_key, reverse=True)
    latex_activities += generate_section(title, entries, format_activity)

# ---------- 指標の集計 ----------
def count_entries(entries, keyword=None):
    if keyword:
        return sum(1 for e in entries if keyword in e.get("keywords", ""))
    return len(entries)

# 論文
count_books = len(categorized["book"])
count_short = len(categorized["short"])
count_collab = len(categorized["collaboration"])
total_pubs = count_books + count_short + count_collab

# 発表
pres_counts = {
    "invited": count_entries(pres_db.entries, "invited"),
    "int_oral": count_entries(pres_db.entries, "int_oral"),
    "int_poster": count_entries(pres_db.entries, "int_poster"),
    "dom_oral": count_entries(pres_db.entries, "dom_oral"),
    "dom_poster": count_entries(pres_db.entries, "dom_poster")
}
total_pres = sum(pres_counts.values())

# アウトリーチ
outreach_counts = {
    "lecture": count_entries(act_db.entries, "lecture"),
    "appearance": count_entries(act_db.entries, "appearance"),
    "writing": count_entries(act_db.entries, "writing"),
    "interview": count_entries(act_db.entries, "interview"),
    "others": count_entries(act_db.entries, "others")
}
total_outreach = sum(outreach_counts.values())

# ---------- 指標セクションを生成 ----------
latex_metrics = f"""
\\noindent
\\textbf{{Publications:}} {count_books} book(s), {count_short} first-author paper(s), {count_collab} collaboration paper(s), total {total_pubs}.\\\\

\\noindent 
\\textbf{{Presentations:}} Invited talks {pres_counts["invited"]}. International: oral {pres_counts["int_oral"]}, poster {pres_counts["int_poster"]}.\\\\
\\hspace{{0.8cm}}Total: {total_pres}. \\\\

\\noindent 
\\textbf{{Outreach:}} Lectures {outreach_counts["lecture"]}. Media appearances {outreach_counts["appearance"]}. Writing {outreach_counts["writing"]}. Interviews {outreach_counts["interview"]}. Others {outreach_counts["others"]}.\\\\
\\hspace{{2.75cm}}Total: {total_outreach}. \\\\
"""

# ---------- テンプレート反映 ----------
with open(template_path, encoding="utf-8") as tf:
    template = tf.read()

filled = template
filled = insert_between(filled, "%BEGIN_PUBLICATIONS%", "%END_PUBLICATIONS%", latex_publications)
filled = insert_between(filled, "%BEGIN_PRESENTATIONS%", "%END_PRESENTATIONS%", latex_presentations)
filled = insert_between(filled, "%BEGIN_ACTIVITIES%", "%END_ACTIVITIES%", latex_activities)
filled = filled.replace(r'\textquoteright', "'")

# `\section*{指標}` のマーカーと置換
filled = insert_between(filled, "%BEGIN_METRICS%", "%END_METRICS%", latex_metrics)

output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(filled)

print("✅ 完全なLaTeXファイルが生成されました:", output_path)

def compile_latex(tex_path):
    try:
        subprocess.run(
            [
                "latexmk",
                "-gg",  # ←強制再ビルド
                "-pdfdvi",
                "-e", "$latex = 'uplatex -interaction=nonstopmode'",
                "-e", "$dvipdf = 'dvipdfmx %O -o %D %S'",
                "-f",
                str(tex_path.name)
            ],
            cwd=tex_path.parent,
            check=True
        )
        pdf_path = tex_path.with_suffix(".pdf")
        if pdf_path.exists():
            print("✅ PDF生成完了:", pdf_path)
        else:
            print("❌ PDFが生成されませんでした。")
    except subprocess.CalledProcessError:
        print("⚠️ LaTeXコンパイルに警告または軽微なエラーがありますが、PDFは生成された可能性があります。")
        pdf_path = tex_path.with_suffix(".pdf")
        if pdf_path.exists():
            print("✅ PDF生成済み:", pdf_path)
        else:
            print("❌ PDFも生成されていません。")

# 実行
compile_latex(output_path)

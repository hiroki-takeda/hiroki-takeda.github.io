# scripts/generate_cv_japanese.py
from pathlib import Path
import re
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from datetime import datetime
import subprocess

# ---------- 設定 ----------
template_path = Path("templates/cv_template_jap.tex")
output_path = Path("cv/cv_japanese/cv.tex")

bib_books = Path("bib/books_jap.bib")
bib_papers = Path("bib/papers.bib")
bib_collab = Path("bib/collaboration.bib")
bib_presentations = Path("bib/presentations.bib")
bib_activities = Path("bib/activities_jap.bib")

# ---------- 月名 ----------
month_map = {
    "1": "1月", "01": "1月", "jan": "1月",
    "2": "2月", "02": "2月", "feb": "2月",
    "3": "3月", "03": "3月", "mar": "3月",
    "4": "4月", "04": "4月", "apr": "4月",
    "5": "5月", "05": "5月", "may": "5月",
    "6": "6月", "06": "6月", "jun": "6月",
    "7": "7月", "07": "7月", "jul": "7月",
    "8": "8月", "08": "8月", "aug": "8月",
    "9": "9月", "09": "9月", "sep": "9月",
    "10": "10月", "oct": "10月",
    "11": "11月", "nov": "11月",
    "12": "12月", "dec": "12月"
}

# ---------- ソート ----------
def get_sort_key(entry):
    eprint = entry.get("eprint", "")
    if len(eprint) >= 4 and eprint[:4].isdigit():
        year = "20" + eprint[:2]
        month = eprint[2:4]
    else:
        year = entry.get("year", "1900")
        month_raw = entry.get("month", "01").lower()
        month = month_map.get(month_raw, "1月").replace("月", "")
        if len(month) == 1:
            month = "0" + month
    try:
        return datetime.strptime(f"{year}-{month}", "%Y-%m")
    except Exception:
        return datetime.min

# ---------- LaTeX文字列整形 ----------
def sanitize_latex_text(text: str) -> str:
    if not text:
        return ""

    s = text.strip()

    # 改行・空白の正規化
    s = s.replace("\r\n", " ").replace("\n", " ")
    s = s.replace("\u00A0", " ")
    s = s.replace("\u2009", " ")
    s = s.replace("\u202F", " ")
    s = re.sub(r"[ \t]+", " ", s)

    # Bib/LaTeX由来の一部表記整理
    s = s.replace(r"\textquoteright{}", "'")
    s = s.replace(r"\textquoteright", "'")

    # Unicode dash を LaTeX 寄りに揃える
    s = s.replace("–", "--")
    s = s.replace("—", "---")

    # 太陽質量表記の正規化
    # M$_{⊙}$, M $_{⊙}$, M$_⊙$, M $_⊙$ -> $M_{\odot}$
    s = re.sub(r"M\s*\$_\{?⊙\}?\$", r"$M_{\\odot}$", s)

    # tabular / alignment 内で壊れる & を escape
    s = re.sub(r"(?<!\\)&", r"\\&", s)

    return s

def format_authors_latex(raw):
    raw = sanitize_latex_text(raw)
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
    title = sanitize_latex_text(entry.get("title", "").strip("{}"))
    year = sanitize_latex_text(entry.get("year", ""))
    doi = sanitize_latex_text(entry.get("doi", ""))
    arxiv = sanitize_latex_text(entry.get("eprint", ""))
    volume = sanitize_latex_text(entry.get("volume", ""))
    pages = sanitize_latex_text(entry.get("pages", ""))
    journal = sanitize_latex_text(entry.get("journal", ""))
    publisher = sanitize_latex_text(entry.get("publisher", ""))
    date = sanitize_latex_text(entry.get("date", ""))
    author = format_authors_latex(entry.get("author", ""))
    entry_type = entry.get("ENTRYTYPE", "")

    if entry.get("keywords", "").strip() == "collaboration":
        collab = sanitize_latex_text(entry.get("collaboration", "Collaboration"))
        author = f"{collab} Collaboration (including \\uline{{Hiroki Takeda}})"

    if entry_type == "book":
        return f"\\item {author}, “{title}”, {publisher}, {date}, {pages}頁."

    if journal:
        parts = f"{journal}, {volume}, {pages} ({year})" if volume else f"{journal} ({year})"
        links = []
        if arxiv:
            links.append(f"arXiv:{arxiv}")
        if doi:
            links.append(f"DOI: {doi}")
        tail = f" {'; '.join(links)}" if links else ""
        return f"\\item {author}, “{title}”, {parts}.{tail}"

    if arxiv:
        return f"\\item {author}, “{title}”, arXiv:{arxiv}."

    return f"\\item {author}, “{title}”, {year}."

def format_presentation(entry):
    author = format_authors_latex(entry.get("author", ""))
    title = sanitize_latex_text(entry.get("title", "").strip("{}"))
    book = sanitize_latex_text(entry.get("booktitle", ""))
    address = sanitize_latex_text(entry.get("address", ""))
    year = sanitize_latex_text(entry.get("year", ""))
    month = month_map.get(entry.get("month", "").lower(), "")
    date = f"{year}年{month}" if month else f"{year}年"
    return f"\\item {author}, “{title}”, {book}, {address}, {date}."

def format_activity(entry):
    title = sanitize_latex_text(entry.get("title", "").strip("{}"))
    org = sanitize_latex_text(entry.get("organization", ""))
    how = sanitize_latex_text(entry.get("howpublished", ""))
    year = sanitize_latex_text(entry.get("year", ""))
    month = month_map.get(entry.get("month", "").lower(), "")
    date = f"{year}年{month}" if month else f"{year}年"
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
latex_publications += generate_section("著書", categorized["book"], format_publication)
latex_publications += generate_section("論文", categorized["short"], format_publication)
latex_publications += generate_section("コラボレーション論文", categorized["collaboration"], format_publication)

# ---------- 発表 ----------
pres_db = load_bib(bib_presentations)
presentation_categories = {
    "invited": "招待講演",
    "int_oral": "国際会議・口頭発表",
    "int_poster": "国際会議・ポスター発表",
    "dom_oral": "国内会議・口頭発表",
    "dom_poster": "国内会議・ポスター発表"
}
latex_presentations = ""
for key, title in presentation_categories.items():
    entries = [e for e in pres_db.entries if key in e.get("keywords", "")]
    entries.sort(key=get_sort_key, reverse=True)
    latex_presentations += generate_section(title, entries, format_presentation)

# ---------- 活動 ----------
act_db = load_bib(bib_activities)
activity_categories = {
    "lecture": "講演",
    "appearance": "出演",
    "writing": "執筆",
    "interview": "取材",
    "others": "その他",
    "notes": "ノート"
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
\\textbf{{出版物:}} 著書{count_books}, 主著論文{count_short}報, 共著論文{count_collab}報, 合計{total_pubs}報.\\\\

\\noindent
\\textbf{{講演:}} 招待セミナー{pres_counts["invited"]}. 国際会議: 口頭発表{pres_counts["int_oral"]}, ポスター発表{pres_counts["int_poster"]}. 国内会議: 口頭発表{pres_counts["dom_oral"]}, ポスター発表{pres_counts["dom_poster"]}.\\\\
\\hspace{{0.8cm}}合計{total_pres}. \\\\

\\noindent
\\textbf{{アウトリーチ活動:}} 講演{outreach_counts["lecture"]}. メディア出演{outreach_counts["appearance"]}. 執筆{outreach_counts["writing"]}. 取材{outreach_counts["interview"]}. その他{outreach_counts["others"]}.\\\\
\\hspace{{2.75cm}}合計{total_outreach}. \\\\
"""

# ---------- テンプレート反映 ----------
with open(template_path, encoding="utf-8") as tf:
    template = tf.read()

filled = template
filled = insert_between(filled, "%BEGIN_PUBLICATIONS%", "%END_PUBLICATIONS%", latex_publications)
filled = insert_between(filled, "%BEGIN_PRESENTATIONS%", "%END_PRESENTATIONS%", latex_presentations)
filled = insert_between(filled, "%BEGIN_ACTIVITIES%", "%END_ACTIVITIES%", latex_activities)
filled = insert_between(filled, "%BEGIN_METRICS%", "%END_METRICS%", latex_metrics)

filled = filled.replace(r"\textquoteright{}", "'")
filled = filled.replace(r"\textquoteright", "'")

output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(filled)

print("✅ 完全なLaTeXファイルが生成されました:", output_path)

def compile_latex(tex_path: Path):
    try:
        subprocess.run(
            [
                "latexmk",
                "-gg",
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
        print("❌ LaTeXコンパイル中にエラーが発生しました。PDFが生成されていても内容が不完全な可能性があります。")
        pdf_path = tex_path.with_suffix(".pdf")
        if pdf_path.exists():
            print("⚠️ PDF生成済み:", pdf_path)
        else:
            print("❌ PDFも生成されていません。")

# 実行
compile_latex(output_path)
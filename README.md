- ディレクトリ構成

├── bib/
│   ├── books_jap.bib          # 著書（日本語）
│   ├── books_eng.bib          # 著書（英語）
│   ├── papers.bib             # 論文（short）
│   ├── collaboration.bib      # 論文（コラボ）
│   ├── presentations.bib      # 発表
│   ├── activities_jap.bib     # 活動（日本語）
│   └── activities_eng.bib     # 活動（英語）
├── scripts/
│   ├── update_all.py          # すべての生成スクリプトをまとめて実行
│   ├── generate_*.py          # 各種生成スクリプト
├── update_all.sh              # update_all.py を実行し git push まで行う
├── cv/
│   └── cv_japanese/, cv_english/  # LaTeX から生成されたCV
├── *.html                     # 公開用 HTML ファイル群



- 更新の基本的な流れ
1. `bib/` フォルダの BibTeXファイルを編集して論文・講演・活動情報を更新
    - 論文: `papers.bib`(keywords = {short}を追加), `books_jap.bib` / `books_eng.bib`, `collaboration.bib`
    - 発表: `presentations.bib`
    - 活動: `activities_jap.bib` / `activities_eng.bib`

2. BibTeX では管理していない「静的な情報（自己紹介や所属など）」を変更する場合は、以下を直接編集
    - index.html などの HTML ファイル
    - templates/cv_template_jap.tex（日本語CV）/ templates/cv_template_eng.tex（英語CV）

3. 以下のコマンドで自動更新＋Git Push を行う：
    chmod +x update_all.sh
    ./update_all.sh

    * このスクリプトは次の手順を自動で実行します：
        scripts/update_all.py を使って以下の5つのPythonスクリプトを順に実行
            generate_publications_html.py
            generate_presentations_html.py
            generate_activities_html.py
            generate_cv_japanese.py
            generate_cv_english.py
    
        その後、自動的に git add . && git commit && git push も実行

    * 個別更新
        python scripts/generate_cv_japanese.py        # 日本語CV（cv/cv_japanese/cv.pdf）を更新
        python scripts/generate_cv_english.py         # 英語CV（cv/cv_english/cv.pdf）を更新
        python scripts/generate_publications_html.py  # publications.html を更新
        python scripts/generate_presentations_html.py # presentations.html を更新
        python scripts/generate_activities_html.py    # activities.html を更新

    
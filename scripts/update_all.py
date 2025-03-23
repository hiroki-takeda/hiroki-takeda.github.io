import subprocess
from pathlib import Path

scripts = [
    "generate_publications_html.py",
    "generate_presentations_html.py",
    "generate_activities_html.py",
    "generate_cv_japanese.py",
    "generate_cv_english.py",
]

base_dir = Path(__file__).parent  # scripts/ ディレクトリを基準に

for script in scripts:
    script_path = base_dir / script
    print(f"▶ Running {script}")
    subprocess.run(["python", str(script_path)], check=True)

print("✅ All files have been updated.")

#!/bin/bash

set -e  # エラー時に即終了
echo "▶ Step 1: Running Python generation scripts..."
python3 scripts/update_all.py

echo "▶ Step 2: Adding all changes to git..."
git add .

echo "▶ Step 3: Committing changes..."
git commit -m "Auto update"

echo "▶ Step 4: Pushing to GitHub..."
git push origin master

echo "✅ All updates complete and pushed to GitHub."

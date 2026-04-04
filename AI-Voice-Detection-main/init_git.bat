@echo off
cd /d d:\AI-Voice-Detection-main\AI-Voice-Detection-main

echo [1/7] Initializing git repository...
git init

echo [2/7] Adding remote origin...
git remote add origin https://github.com/Muditsrivastav21/VoxSentinel.git 2>nul
if errorlevel 1 (
    echo Remote already exists, updating...
    git remote set-url origin https://github.com/Muditsrivastav21/VoxSentinel.git
)

echo [3/7] Adding all files (excluding .env via .gitignore)...
git add .

echo [4/7] Committing changes...
git commit -m "VoxSentinel v1.0 - Call Center Compliance API

Features:
- Multi-language STT (Hindi/Hinglish, Tamil/Tanglish, English)
- AI-powered SOP validation (5 stages)
- Payment preference categorization
- Rejection reason analysis
- Sentiment analysis
- Keyword extraction
- Celery async processing support
- Supabase database integration
- Rate limiting and API authentication

Tech: FastAPI, Groq (Whisper + Llama), Supabase

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

echo [5/7] Renaming branch to main...
git branch -M main

echo [6/7] Pushing to remote repository...
git push -u origin main --force

echo [7/7] Done! Repository initialized and pushed to GitHub.
echo.
echo Git status:
git status
echo.
echo Repository URL: https://github.com/Muditsrivastav21/VoxSentinel

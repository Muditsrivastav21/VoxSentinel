@echo off
echo Cleaning up repository structure...

cd /d d:\AI-Voice-Detection-main

if not exist docs mkdir docs

echo Moving documentation files to docs/...
move "API_TEST_GUIDE.md" "docs\" 2>nul
move "DASHBOARD_FIX.md" "docs\" 2>nul
move "DEPLOYMENT_CHECKLIST.txt" "docs\" 2>nul
move "DEPLOYMENT_FIX.md" "docs\" 2>nul
move "GROQ_MIGRATION.md" "docs\" 2>nul
move "LATEST_FIXES.md" "docs\" 2>nul
move "QUICK_TEST_GUIDE.md" "docs\" 2>nul
move "RENDER_DEPLOYMENT_GUIDE.md" "docs\" 2>nul
move "VoxSentinel_API_Collection.postman.json" "docs\" 2>nul
move "render-both.yaml" "docs\" 2>nul
move "test_api.html" "docs\" 2>nul
move "test_sample_audio.py" "docs\" 2>nul

echo.
echo Done! Repository structure cleaned.
echo.
echo Root directory now contains:
dir /b

echo.
echo Press any key to continue...
pause >nul

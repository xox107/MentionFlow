@echo off
title MentionFlow Launcher
echo 🚀 Starting MentionFlow Intelligence System...

:: 1. Activate Python Venv and install requirements just in case
call .\venv\Scripts\activate
pip install requests fpdf2 --quiet

:: 2. Start the Backend in a separate minimized window
start /min cmd /c "node server.js"

:: 3. Wait 2 seconds for server to warm up
timeout /t 2 >nul

:: 4. Open the Dashboard in the default browser
start "" "index.html"

echo ✅ System is LIVE!
echo 📡 Backend: http://localhost:5000
echo 🖥️  Dashboard: index.html
pause
@echo off
REM Start Flask Server for Jira Dashboard
echo Starting Jira Dashboard Server...
echo.
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py
pause

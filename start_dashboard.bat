@echo off
echo ========================================
echo  Jira Dashboard Startup Script
echo ========================================
echo.

echo [1/3] Updating data from CSV...
python update_data.py

if %errorlevel% neq 0 (
    echo Error: Failed to update data!
    pause
    exit /b 1
)

echo.
echo [2/3] Opening dashboard in browser...
start http://localhost:8000/dashboard.html

echo.
echo [3/3] Starting HTTP server on port 8000...
echo.
echo Dashboard is now running at: http://localhost:8000/dashboard.html
echo Press Ctrl+C to stop the server
echo.

python -m http.server 8000

@echo off
echo Starting Contact Management System...
echo.

echo Starting API Server on port 3001...
start cmd /k "python api_server.py"

timeout /t 3 /nobreak > nul

echo Starting Web Server on port 3000...
start cmd /k "python serve.py"

timeout /t 2 /nobreak > nul

echo.
echo ===================================
echo   Contact Management System Ready
echo ===================================
echo.
echo Web Interface: http://localhost:3000/list.html
echo API Server:    http://localhost:3001/api/health
echo.
echo Press any key to open the contact list page...
pause > nul

start http://localhost:3000/list.html

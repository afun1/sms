@echo off
echo Starting Contact Management System...
echo.

echo Starting API Server (Port 3001)...
start "Contacts API" python api_server.py

echo Waiting for API server to start...
timeout /t 3 /nobreak > nul

echo Starting Web Server (Port 3002)...
start "Web Server" python serve.py

echo.
echo Both servers are starting...
echo.
echo Web Interface: http://localhost:3002/list.html
echo API Server: http://localhost:3001/api/health
echo.
echo Press any key to stop all servers...
pause > nul

echo Stopping servers...
taskkill /f /im python.exe > nul 2>&1
echo Servers stopped.

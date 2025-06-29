@echo off
echo Starting Sparky Messaging Development Server...
echo ================================================
echo.
echo Available commands:
echo   npm run dev    - Start development server
echo   npm run setup  - Install Python dependencies  
echo   npm run test   - Run API tests
echo.
echo Server will auto-reload on code changes...
echo Press Ctrl+C to stop the server
echo.

python sms_api_server.py

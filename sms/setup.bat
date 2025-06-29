@echo off
echo SMS Sender Application Setup
echo ==============================
echo.

echo 1. Installing Python packages...
pip install -r requirements.txt

echo.
echo 2. Creating .env file from template...
if not exist .env (
    copy .env.example .env
    echo Please edit .env file with your Twilio credentials
) else (
    echo .env file already exists
)

echo.
echo 3. Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your Twilio credentials
echo 2. Prepare your CSV file with phone_number column
echo 3. Run: python sms_sender.py
echo.
pause

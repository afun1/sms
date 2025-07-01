# Quick Start Guide - Contact Management System

## System Status: ✅ READY TO USE

The CSV upload system is fully functional! Here's how to start it:

## Option 1: Use Batch File (Recommended for Windows)

```cmd
.\start_servers.bat
```

## Option 2: Manual Start (Two Terminals)

**Terminal 1** - API Server:
```cmd
python api_server.py
```

**Terminal 2** - Web Server:  
```cmd
python serve.py
```

## Access the System

Once both servers are running:

🌐 **Main Interface**: http://localhost:3002/list.html
🔧 **API Health**: http://localhost:3001/api/health

## How to Import CSV

1. Open http://localhost:3002/list.html
2. Click the **"Import"** button (purple button on the right)
3. Select your CSV file (try `sample_test_contacts.csv`)
4. Review the preview showing first 5 rows
5. Click **"Import Data"** to upload to database
6. Contacts will appear in the table automatically!

## Troubleshooting

**If you see "Unable to load contacts from API server":**
- Make sure both servers are running
- Check that API server shows "✅ Database initialized" 
- Verify API health at http://localhost:3001/api/health

**If import button doesn't work:**
- Check browser console (F12) for errors
- Ensure API server is responding
- Try refreshing the page

**Port conflicts:**
- API Server: Port 3001
- Web Server: Port 3002 (changed from 3000 to avoid conflicts)

## Test Data

Use the included `sample_test_contacts.csv` file to test the import:
- 10 sample contacts
- Proper CSV format with headers
- Various data types (names, emails, phones, addresses)

## Features Working

✅ CSV file upload and parsing  
✅ Data preview before import  
✅ Database storage (SQLite)  
✅ Dynamic table display  
✅ Search and pagination  
✅ Column management  
✅ Error handling  

**Everything is ready to use! 🎉**

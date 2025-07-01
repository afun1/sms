# Contact Management System - CSV Upload

A complete contact management system with CSV import functionality, built with Python backend and HTML/JavaScript frontend.

## Features

- **CSV Import**: Upload and import contacts from CSV files
- **Contact Table**: View contacts with sticky columns and pagination
- **Search & Filter**: Search contacts by name, email, or phone
- **Multi-level Sorting**: Sort by multiple columns with priority
- **Column Management**: Show/hide table columns as needed
- **Bulk Actions**: Send SMS, email, or RVM to selected contacts
- **Responsive UI**: Modern, mobile-friendly interface

## Quick Start (PowerShell)

1. **Start the system**:
   ```powershell
   .\start_servers.ps1
   ```

2. **Test the system**:
   ```powershell
   .\test_system.ps1
   ```

3. **Open the interface**:
   - Visit: http://localhost:3000/list.html
   - API: http://localhost:3001/api/health

## Manual Setup

If you prefer to start servers individually:

```powershell
# Terminal 1 - API Server
python api_server.py

# Terminal 2 - Web Server  
python serve.py
```

## CSV Import

1. Click the **"Import"** button in the contact list
2. Select a CSV file (see `sample_contacts.csv` for format)
3. Preview the data and column mapping
4. Click **"Import Data"** to upload to database

### Supported CSV Columns

- Basic Info: First Name, Last Name, Email, Phone
- Address: Address, City, State, Zip, Country
- Sponsor: Sponsor, Sponsor First, Sponsor Last
- Phone Types: Cell, Landline, Voip, Carrier
- Metadata: User ID, Status, Rating, IP, Date, Timezone

## API Endpoints

- `GET /api/health` - Server health check
- `GET /api/contacts` - List contacts (with pagination/search)
- `POST /api/contacts/import` - Import contacts from CSV

### Example API Usage

```powershell
# Check API health
Invoke-RestMethod -Uri "http://localhost:3001/api/health"

# Get contacts
Invoke-RestMethod -Uri "http://localhost:3001/api/contacts?page=1&per_page=20"

# Search contacts
Invoke-RestMethod -Uri "http://localhost:3001/api/contacts?search=john"
```

## Database

The system uses SQLite database (`contacts.db`) with the following features:
- Automatic table creation
- Data validation and constraints
- Indexes for performance
- Boolean field handling

## File Structure

```
contacts/
├── list.html              # Main contact interface
├── api_server.py          # Backend API server (port 3001)
├── serve.py               # Frontend web server (port 3000)
├── start_servers.ps1      # PowerShell startup script
├── test_system.ps1        # PowerShell test script
├── sample_contacts.csv    # Example CSV file
├── contacts.db            # SQLite database (auto-created)
└── README_UPLOAD.md       # This file
```

## Requirements

- Python 3.6+
- No additional packages required (uses built-in modules)
- Modern web browser
- PowerShell (Windows) or compatible shell

## Troubleshooting

**API Server not starting?**
- Check if port 3001 is available
- Verify Python is in your PATH
- Check for firewall blocking localhost connections

**CSV import fails?**
- Ensure CSV has headers in first row
- Check for special characters or encoding issues
- Verify API server is running

**Table not loading contacts?**
- Check browser console for errors
- Verify API server response at http://localhost:3001/api/contacts
- Ensure both servers are running

## Development

The system is designed for easy extension:
- Add new CSV column mappings in `mapCsvHeaderToDbColumn()`
- Extend database schema in `api_server.py`
- Add new UI features in `list.html`
- Create additional API endpoints as needed

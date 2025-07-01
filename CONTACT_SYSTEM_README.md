# Contact Management System - CSV Upload

A comprehensive contact management system with CSV import functionality, advanced table features, and robust backend API.

## Features

### Frontend (list.html)
- **Sticky Columns**: First 4 columns (SMS, Call, Email, Select) stay fixed while scrolling
- **Bulk Actions**: Send SMS, Email, RVM to selected contacts
- **Multi-level Sorting**: Sort by up to 8 different columns
- **Column Selection**: Show/hide columns as needed  
- **CSV Import**: Upload and preview CSV files before import
- **Search & Pagination**: Find contacts quickly with search and pagination
- **Responsive Design**: Clean, professional interface

### Backend (api_server.py)
- **CSV Import API**: Process and validate CSV data
- **Contact Management**: CRUD operations for contacts
- **Search & Filtering**: Server-side search capabilities
- **Data Validation**: Ensure data integrity
- **SQLite Database**: Local database storage

## Quick Start

1. **Start the System**:
   ```bash
   start_system.bat
   ```
   This will start both the API server (port 3001) and web server (port 3000).

2. **Open Contact List**: 
   Navigate to http://localhost:3000/list.html

3. **Import Contacts**:
   - Click the "Import" button
   - Select a CSV file (sample: `sample_test_contacts.csv`)
   - Preview the data and click "Import Data"

## CSV Import Format

Your CSV file should have a header row with any of these column names:

### Basic Contact Info
- `First Name`, `Last Name`
- `E-mail`, `Email`
- `Phone`
- `Address`, `City`, `State`, `Zip`

### Advanced Fields
- `Sponsor`, `Sponsor First`, `Sponsor Last`
- `User ID`, `Status`, `Rating`
- `Valid` (email validation: true/false)
- `Cell`, `Landline`, `Voip` (phone type: true/false)
- `Carrier`, `Country`, `Timezone`
- `IP`, `Date`

### Example CSV Format
```csv
First Name,Last Name,E-mail,Phone,City,State,Status
John,Doe,john.doe@email.com,555-0101,New York,NY,Active
Jane,Smith,jane.smith@email.com,555-0102,Los Angeles,CA,Active
```

## Using the Interface

### Import CSV
1. Click "Import" button
2. Select your CSV file
3. Review the preview (first 5 rows)
4. Click "Import Data" to save to database

### Search Contacts
- Type in the search box and press Enter or click "Search"
- Searches across name, email, phone, and sponsor fields
- Click "Reset" to clear search

### Bulk Actions
1. Select contacts using checkboxes
2. Choose action: Send SMS, Send Email, Send RVM, or Campaign
3. System will open the appropriate editor with selected contacts

### Table Features
- **Sort**: Click "Sort" for multi-level sorting options
- **Columns**: Click "Select Columns" to show/hide fields
- **Pagination**: Use the page numbers or "Rows per page" dropdown

## Architecture

```
Frontend (Port 3000)          Backend (Port 3001)
┌─────────────────┐          ┌─────────────────┐
│   list.html     │────────→ │  api_server.py  │
│                 │          │                 │
│ • CSV Upload    │          │ • Import API    │
│ • Table Display │◄────────│ • Contact CRUD  │
│ • Search/Filter │          │ • Data Validation│
│ • Pagination    │          │                 │
└─────────────────┘          └─────────────────┘
                                      │
                                      ▼
                               ┌─────────────────┐
                               │  contacts.db    │
                               │   (SQLite)      │
                               └─────────────────┘
```

## Database Schema

The `contacts` table includes:
- **Basic**: id, first_name, last_name, email, phone
- **Address**: address, city, state, zip, country
- **Meta**: status, rating, created_at, updated_at
- **Phone Types**: cell, landline, voip, carrier
- **Sponsor**: sponsor, sponsor_first, sponsor_last
- **Technical**: ip_address, timezone, user_id

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/contacts` - List contacts (with search & pagination)
- `POST /api/contacts/import` - Import CSV data
- `POST /api/contacts` - Create single contact

## Troubleshooting

### API Connection Issues
- Ensure both servers are running (start_system.bat)
- Check that ports 3000 and 3001 are available
- Verify API health: http://localhost:3001/api/health

### CSV Import Problems
- Ensure CSV has headers in the first row
- Check file encoding (UTF-8 recommended)  
- Verify column names match expected format
- Check browser console for detailed error messages

### Performance
- Large CSV files (>1000 rows) may take a few seconds to import
- Use pagination for large datasets
- Search is indexed on common fields for speed

## Development

### File Structure
```
c:\texts\
├── list.html              # Main contact list interface
├── api_server.py          # Backend API server
├── serve.py               # Static file web server
├── start_system.bat       # System startup script
├── sample_test_contacts.csv # Example CSV file
├── contacts.db            # SQLite database (auto-created)
└── create_contacts_table.sql # Database schema reference
```

### Extending the System
- Add new CSV column mappings in `mapCsvHeaderToDbColumn()`
- Modify database schema in `api_server.py` `_init_database()`
- Add new UI features in `list.html`
- Create additional API endpoints as needed

## Security Notes
- This is a local development system
- CORS is enabled for localhost development
- No authentication implemented
- Use HTTPS and proper auth for production use

---

**Ready to use!** Run `start_system.bat` and go to http://localhost:3000/list.html

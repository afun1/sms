# PowerShell script to test the Contact Management System
Write-Host "Testing Contact Management System..." -ForegroundColor Green
Write-Host ""

# Test API Server
Write-Host "Testing API Server..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:3001/api/health" -Method Get
    Write-Host "✓ API Server is healthy" -ForegroundColor Green
    Write-Host "  Status: $($healthResponse.status)" -ForegroundColor Cyan
    Write-Host "  Service: $($healthResponse.service)" -ForegroundColor Cyan
} catch {
    Write-Host "✗ API Server is not responding" -ForegroundColor Red
    Write-Host "  Make sure the API server is running on port 3001" -ForegroundColor Yellow
    exit 1
}

# Test Web Server
Write-Host ""
Write-Host "Testing Web Server..." -ForegroundColor Yellow
try {
    $webResponse = Invoke-WebRequest -Uri "http://localhost:3002/list.html" -UseBasicParsing -TimeoutSec 5
    if ($webResponse.StatusCode -eq 200) {
        Write-Host "✓ Web Server is responding" -ForegroundColor Green
        Write-Host "  Status Code: $($webResponse.StatusCode)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "✗ Web Server is not responding" -ForegroundColor Red
    Write-Host "  Make sure the web server is running on port 3002" -ForegroundColor Yellow
    exit 1
}

# Test Contacts API
Write-Host ""
Write-Host "Testing Contacts API..." -ForegroundColor Yellow
try {
    $contactsResponse = Invoke-RestMethod -Uri "http://localhost:3001/api/contacts" -Method Get
    Write-Host "✓ Contacts API is working" -ForegroundColor Green
    if ($contactsResponse.contacts) {
        Write-Host "  Current contacts: $($contactsResponse.contacts.Count)" -ForegroundColor Cyan
        if ($contactsResponse.pagination) {
            Write-Host "  Total in database: $($contactsResponse.pagination.total)" -ForegroundColor Cyan
        }
    }
} catch {
    Write-Host "✗ Contacts API error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 System test complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:3002/list.html in your browser" -ForegroundColor Cyan
Write-Host "2. Click the 'Import' button to upload a CSV file" -ForegroundColor Cyan
Write-Host "3. Use sample_contacts.csv for testing" -ForegroundColor Cyan
Write-Host ""

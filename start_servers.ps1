# PowerShell script to start Contact Management System
Write-Host "Starting Contact Management System..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python or add it to your PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start API Server
Write-Host "Starting API Server (Port 3001)..." -ForegroundColor Yellow
$apiProcess = Start-Process -FilePath "python" -ArgumentList "api_server.py" -PassThru -WindowStyle Normal

# Wait for API server to start
Write-Host "Waiting for API server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Test API server
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001/api/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ API Server is running" -ForegroundColor Green
} catch {
    Write-Host "⚠ API Server may not be fully ready yet" -ForegroundColor Yellow
}

# Start Web Server
Write-Host "Starting Web Server (Port 3002)..." -ForegroundColor Yellow
$webProcess = Start-Process -FilePath "python" -ArgumentList "serve.py" -PassThru -WindowStyle Normal

Write-Host ""
Write-Host "🚀 Contact Management System is running!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Main Interface: http://localhost:3002/list.html" -ForegroundColor Cyan
Write-Host "🔧 API Health Check: http://localhost:3001/api/health" -ForegroundColor Cyan
Write-Host "📤 Upload CSV files using the Import button" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C or close this window to stop all servers" -ForegroundColor Yellow
Write-Host ""

# Keep script running and monitor processes
try {
    while ($true) {
        Start-Sleep -Seconds 10
        
        # Check if processes are still running
        if (-not (Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host "API Server process has stopped" -ForegroundColor Red
            break
        }
        
        if (-not (Get-Process -Id $webProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host "Web Server process has stopped" -ForegroundColor Red
            break
        }
    }
} catch {
    Write-Host ""
    Write-Host "Stopping servers..." -ForegroundColor Yellow
}

# Clean up processes
Write-Host "Stopping servers..." -ForegroundColor Red
try {
    if ($apiProcess -and -not $apiProcess.HasExited) { $apiProcess.Kill() }
    if ($webProcess -and -not $webProcess.HasExited) { $webProcess.Kill() }
} catch {
    # Force kill any remaining python processes
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
}

Write-Host "All servers stopped." -ForegroundColor Green

# IQOO Z6 Pro Mobile App Viewing Setup
# Run this in PowerShell to get your device connection URL

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Mobile App - IQOO Z6 Pro Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Get local IP address
Write-Host "Step 1: Finding your computer's IP address..." -ForegroundColor Yellow
$IP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notmatch '^127\.' -and $_.IPAddress -ne '169.254.1.1'} | Select-Object -ExpandProperty IPAddress)[0]

if ($IP) {
    Write-Host "Found IP address: $IP" -ForegroundColor Green
} else {
    Write-Host "Could not detect IP address" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please manually check your IP:" -ForegroundColor Yellow
    Write-Host "  1. Run: ipconfig" -ForegroundColor White
    Write-Host "  2. Look for IPv4 Address" -ForegroundColor White
    Write-Host ""
    exit
}

Write-Host ""

# Check if app is running
Write-Host "Step 2: Checking if mobile app is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "Mobile app is running on localhost:5173" -ForegroundColor Green
} catch {
    Write-Host "Mobile app is NOT running on localhost:5173" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To start the mobile app, run:" -ForegroundColor Yellow
    Write-Host "  cd apps/mobile" -ForegroundColor White
    Write-Host "  npm run dev" -ForegroundColor White
    Write-Host ""
    exit
}

Write-Host ""

# Display connection info
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "DEVICE CONNECTION URL" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "On your IQOO Z6 Pro:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Connect to the SAME WiFi as your PC" -ForegroundColor White
Write-Host ""
Write-Host "2. Open Chrome or any browser" -ForegroundColor White
Write-Host ""
Write-Host "3. Go to this URL:" -ForegroundColor White
Write-Host ""
Write-Host "   http://$($IP):5173" -ForegroundColor Magenta
Write-Host ""
Write-Host "4. Press Enter - the app will load!" -ForegroundColor White
Write-Host ""

# Copy to clipboard
Write-Host "URL copied to clipboard" -ForegroundColor Green
$URL = "http://$($IP):5173"
$URL | Set-Clipboard

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "TROUBLESHOOTING" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "App not loading?" -ForegroundColor Yellow
Write-Host ""
Write-Host "  - Check WiFi: Same network for both devices" -ForegroundColor White
Write-Host "  - Check Firewall: Allow Node.js through firewall" -ForegroundColor White
Write-Host "  - Check IP: Run ipconfig to verify" -ForegroundColor White
Write-Host "  - Restart: Stop and restart npm run dev" -ForegroundColor White
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "HOT RELOAD" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Code changes automatically refresh in browser" -ForegroundColor Green
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan

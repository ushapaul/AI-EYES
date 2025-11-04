Set-Location 'C:\Users\Lenovo\Desktop\AI eyes\backend'
Write-Host '=== MULTI-CAMERA: starting ===' -ForegroundColor Cyan

# Wait for backend to finish setup
Write-Host 'Waiting 10 seconds for backend setup...' -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Find venv (should exist from backend tab)
$pythonExe = $null
$venvPaths = @('.venv\Scripts\python.exe', 'venv\Scripts\python.exe', 'venv_fresh_py310\Scripts\python.exe')
foreach ($vPath in $venvPaths) {
    if (Test-Path $vPath) {
        $pythonExe = (Resolve-Path $vPath).Path
        break
    }
}

if (-not $pythonExe) {
    Write-Warning 'No venv found. Please ensure backend API tab completed setup.'
    Read-Host 'Press Enter to exit'
    exit 1
}

Write-Host "Using: $pythonExe" -ForegroundColor Green
Write-Host 'Starting multi-camera surveillance...' -ForegroundColor Green
& $pythonExe multi_camera_surveillance.py

Write-Host ''
Write-Warning 'Surveillance stopped. Press Enter to close.'
Read-Host

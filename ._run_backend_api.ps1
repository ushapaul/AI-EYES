Set-Location 'C:\Users\Lenovo\Desktop\AI eyes\backend'
Write-Host '=== BACKEND API: starting ===' -ForegroundColor Cyan

# Find existing venv
$pythonExe = $null
$venvPaths = @('.venv\Scripts\python.exe', 'venv\Scripts\python.exe', 'venv_fresh_py310\Scripts\python.exe')
foreach ($vPath in $venvPaths) {
    if (Test-Path $vPath) {
        $pythonExe = (Resolve-Path $vPath).Path
        break
    }
}

# Create venv if not found
if (-not $pythonExe) {
    Write-Host 'Creating new venv...' -ForegroundColor Yellow
    try {
        py -3.10 -m venv .venv
    } catch {
        python -m venv .venv
    }
    $pythonExe = (Resolve-Path '.venv\Scripts\python.exe').Path
}

if (-not (Test-Path $pythonExe)) {
    Write-Warning 'Failed to create venv. Please install Python and try again.'
    Read-Host 'Press Enter to exit'
    exit 1
}

Write-Host "Using: $pythonExe" -ForegroundColor Green

# Install packages
Write-Host 'Installing packages...' -ForegroundColor Yellow
& $pythonExe -m pip install --quiet --upgrade pip setuptools wheel
& $pythonExe -m pip install --quiet -r requirements.txt
& $pythonExe -m pip install --quiet -r requirements_surveillance.txt
& $pythonExe -m pip install --quiet pymongo sendgrid PyJWT

Write-Host 'Starting backend API...' -ForegroundColor Green
& $pythonExe app_simple.py

Write-Host ''
Write-Warning 'Backend stopped. Press Enter to close.'
Read-Host
